/*
 * Fetches a site's llms.txt so the validator can check a live domain.
 *
 * Privacy: this endpoint exists only for the "check a domain" path. It receives
 * a domain and nothing else. Pasted file contents are validated entirely in the
 * browser and are never sent here or anywhere else.
 *
 * Security posture is copied from discover-site.js deliberately: the same
 * public-URL validation, manual redirect handling, fetch timeout, and body-size
 * ceiling. Do not relax these independently. The one intentional divergence is
 * the redirect host policy, explained above validatePublicUrl.
 */

const MAX_BODY_BYTES = 1_000_000;
const FETCH_TIMEOUT_MS = 8_000;
const USER_AGENT = "NinadPathak-llms-txt-validator/1.0 (+https://ninadpathak.com/llms-txt-validator/)";

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

/*
 * The private/local guard is absolute and applies to every hop. Host identity is
 * handled separately, because pinning the host outright breaks the most common
 * real case: apex-to-www. Verified 2026-08-17, mintlify.com/llms.txt returns 307
 * to www.mintlify.com/llms.txt, and docs.anthropic.com/llms.txt returns 301 to
 * platform.claude.com/llms.txt. Rejecting either would fail the tool on files
 * that plainly exist, so a cross-host redirect is followed and reported rather
 * than refused. Following a redirect between public hosts is not the SSRF risk;
 * reaching a private address is, and that stays blocked.
 */
function validatePublicUrl(value) {
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error("Enter a valid website URL.");
  }
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("The website must use http:// or https://.");
  const host = url.hostname.toLowerCase().replace(/\.$/, "");
  if (!host || host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local") ||
      host.endsWith(".internal") || host.includes(":") || isPrivateIpv4(host)) {
    throw new Error("Private and local network addresses cannot be scanned.");
  }
  url.hash = "";
  return url;
}

/* True when two hosts are the same site: identical, or one is a subdomain of the
 * other. Deliberately conservative and PSL-free, so it treats a move to a
 * different registrable domain as off-site and lets the caller say so. */
function isSameSite(a, b) {
  if (!a || !b) return false;
  if (a === b) return true;
  return a.endsWith("." + b) || b.endsWith("." + a);
}

async function safeFetch(input, expectedHost) {
  let url = validatePublicUrl(input);
  const chain = [];
  let leftOriginalSite = false;
  for (let redirect = 0; redirect < 4; redirect += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    let response;
    try {
      response = await fetch(url, {
        redirect: "manual",
        signal: controller.signal,
        headers: { "user-agent": USER_AGENT, accept: "text/plain, text/markdown, */*;q=0.5" },
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
  if (declared > MAX_BODY_BYTES) throw new Error("The file is too large to validate safely.");
  const text = await response.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) {
    throw new Error("The file is too large to validate safely.");
  }
  return text;
}

/*
 * A 200 response carrying an HTML document is the most common real failure: the
 * host serves its SPA shell or a styled 404 page instead of the file. Callers
 * need to distinguish that from a genuine llms.txt.
 */
function looksLikeHtml(text) {
  const head = text.slice(0, 2000).toLowerCase();
  return /<!doctype html|<html[\s>]|<head[\s>]|<body[\s>]|<script[\s>]/.test(head);
}

export async function onRequestPost(context) {
  let payload;
  try {
    payload = await context.request.json();
  } catch {
    return json({ error: "Send a website URL as JSON." }, 400);
  }

  try {
    const input = String(payload.url || "").trim();
    if (!input) return json({ error: "Enter a website URL." }, 400);

    const initial = validatePublicUrl(/^https?:\/\//i.test(input) ? input : `https://${input}`);

    // The spec allows llms.txt at the root or at any subpath. Honour an explicit
    // path ending in llms.txt; otherwise look at the origin root.
    const target = /\/llms\.txt$/i.test(initial.pathname)
      ? initial.toString()
      : new URL("/llms.txt", initial).toString();

    const { response, url, chain, leftOriginalSite } = await safeFetch(target, initial.hostname);
    const contentType = (response.headers.get("content-type") || "").toLowerCase();

    if (!response.ok) {
      return json({
        found: false,
        requestedUrl: target,
        finalUrl: url.toString(),
        status: response.status,
        contentType,
        redirected: chain.length > 0,
        leftOriginalSite: Boolean(leftOriginalSite),
        error: `No llms.txt at that URL. It returned HTTP ${response.status}.`,
      });
    }

    const text = await readText(response);

    return json({
      found: true,
      requestedUrl: target,
      finalUrl: url.toString(),
      status: response.status,
      contentType,
      redirected: chain.length > 0,
      leftOriginalSite: Boolean(leftOriginalSite),
      bytes: new TextEncoder().encode(text).length,
      servedAsHtml: looksLikeHtml(text),
      content: text,
    });
  } catch (error) {
    const message = error && error.name === "AbortError"
      ? "The website took too long to respond."
      : error.message;
    return json({ error: message || "The file could not be fetched." }, 422);
  }
}
