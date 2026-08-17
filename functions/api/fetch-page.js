/*
 * Fetches a public page's HTML so the AI Overviews checker can grade a live URL.
 *
 * The HTML is returned to the browser and graded there by the same engine the
 * paste path uses, so there is one rule implementation and the analysis never
 * happens server-side.
 *
 * Privacy: this endpoint exists only for the "check a URL" path and receives a
 * URL and nothing else. Pasted content is graded entirely in the browser and is
 * never sent here.
 *
 * Security posture matches functions/api/fetch-llms-txt.js: absolute
 * private-address guard on every hop, manual redirect handling, fetch timeout,
 * body-size ceiling. A cross-host redirect is followed and reported rather than
 * refused, because apex-to-www is routine and refusing it fails real pages.
 */

const MAX_BODY_BYTES = 2_000_000;
const FETCH_TIMEOUT_MS = 10_000;
const USER_AGENT = "NinadPathak-ai-overviews-checker/1.0 (+https://ninadpathak.com/ai-overviews-checker/)";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
    },
  });
}

function isPrivateIpv4(hostname) {
  const parts = hostname.split(".").map(Number);
  if (parts.length !== 4 || parts.some((part) => !Number.isInteger(part) || part < 0 || part > 255)) return false;
  return parts[0] === 10 || parts[0] === 127 || parts[0] === 0 ||
    (parts[0] === 169 && parts[1] === 254) ||
    (parts[0] === 172 && parts[1] >= 16 && parts[1] <= 31) ||
    (parts[0] === 192 && parts[1] === 168);
}

function validatePublicUrl(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error("Enter a valid page URL.");
  }
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("The URL must use http:// or https://.");
  const host = url.hostname.toLowerCase().replace(/\.$/, "");
  if (!host || host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local") ||
      host.endsWith(".internal") || host.includes(":") || isPrivateIpv4(host)) {
    throw new Error("Private and local network addresses cannot be fetched.");
  }
  url.hash = "";
  return url;
}

function isSameSite(a, b) {
  if (!a || !b) return false;
  if (a === b) return true;
  return a.endsWith("." + b) || b.endsWith("." + a);
}

async function safeFetch(input, expectedHost) {
  let url = validatePublicUrl(input);
  const chain = [];
  let leftOriginalSite = false;
  for (let redirect = 0; redirect < 5; redirect += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    let response;
    try {
      response = await fetch(url, {
        redirect: "manual",
        signal: controller.signal,
        headers: { "user-agent": USER_AGENT, accept: "text/html, application/xhtml+xml, text/plain;q=0.8" },
      });
    } finally {
      clearTimeout(timer);
    }
    if (response.status >= 300 && response.status < 400 && response.headers.get("location")) {
      chain.push({ from: url.toString(), status: response.status });
      const next = validatePublicUrl(new URL(response.headers.get("location"), url).toString());
      if (expectedHost && !isSameSite(next.hostname.toLowerCase(), expectedHost)) leftOriginalSite = true;
      url = next;
      continue;
    }
    return { response, url, chain, leftOriginalSite };
  }
  throw new Error("Too many redirects.");
}

async function readText(response) {
  const declared = Number(response.headers.get("content-length") || 0);
  if (declared > MAX_BODY_BYTES) throw new Error("That page is too large to fetch safely.");
  const text = await response.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) {
    throw new Error("That page is too large to fetch safely.");
  }
  return text;
}

export async function onRequestPost(context) {
  let payload;
  try {
    payload = await context.request.json();
  } catch {
    return json({ error: "Send a page URL as JSON." }, 400);
  }

  try {
    const input = String(payload.url || "").trim();
    if (!input) return json({ error: "Enter a page URL." }, 400);

    const initial = validatePublicUrl(/^https?:\/\//i.test(input) ? input : `https://${input}`);
    const { response, url, chain, leftOriginalSite } = await safeFetch(initial.toString(), initial.hostname);
    const contentType = (response.headers.get("content-type") || "").toLowerCase();

    if (!response.ok) {
      return json({
        found: false,
        finalUrl: url.toString(),
        status: response.status,
        error: `That URL returned HTTP ${response.status}.`,
      });
    }

    if (contentType && !/text\/html|application\/xhtml/.test(contentType)) {
      return json({
        found: false,
        finalUrl: url.toString(),
        status: response.status,
        contentType,
        error: `That URL returned ${contentType.split(";")[0]} rather than HTML.`,
      });
    }

    const html = await readText(response);

    /* The X-Robots-Tag header carries the same snippet directives as the meta
     * tag, and a page can be excluded by the header alone with nothing visible
     * in its markup. Passing it through lets the client check both. */
    return json({
      found: true,
      finalUrl: url.toString(),
      status: response.status,
      contentType,
      redirected: chain.length > 0,
      leftOriginalSite: Boolean(leftOriginalSite),
      xRobotsTag: response.headers.get("x-robots-tag") || "",
      bytes: new TextEncoder().encode(html).length,
      content: html,
    });
  } catch (error) {
    const message = error && error.name === "AbortError"
      ? "That page took too long to respond."
      : error.message;
    return json({ error: message || "That page could not be fetched." }, 422);
  }
}
