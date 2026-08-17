/*
 * Fetches a site's llms.txt so the validator can check a live domain.
 *
 * Privacy: this endpoint exists only for the "check a domain" path. It receives
 * a domain and nothing else. Pasted file contents are validated entirely in the
 * browser and are never sent here or anywhere else.
 *
 * Security posture is copied from discover-site.js deliberately: the same
 * public-URL validation, manual redirect handling with host pinning, fetch
 * timeout, and body-size ceiling. Do not relax these independently.
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

function validatePublicUrl(value, expectedHost) {
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
  if (expectedHost && host !== expectedHost) throw new Error("The website redirected to a different domain.");
  url.hash = "";
  return url;
}

async function safeFetch(input, expectedHost) {
  let url = validatePublicUrl(input, expectedHost);
  const chain = [];
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
      url = validatePublicUrl(new URL(response.headers.get("location"), url).toString(), expectedHost);
      continue;
    }
    return { response, url, chain };
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

    const { response, url, chain } = await safeFetch(target, initial.hostname);
    const contentType = (response.headers.get("content-type") || "").toLowerCase();

    if (!response.ok) {
      return json({
        found: false,
        requestedUrl: target,
        finalUrl: url.toString(),
        status: response.status,
        contentType,
        redirected: chain.length > 0,
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
