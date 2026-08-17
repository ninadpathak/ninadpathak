/*
 * Fetches a site's robots.txt so the AI crawler access checker can read a live
 * domain. The file is returned to the browser and evaluated there by the same
 * engine the paste path uses, so there is one rule implementation.
 *
 * Privacy: this endpoint exists only for the "check a domain" path and receives a
 * domain and nothing else. A pasted robots.txt is evaluated entirely in the
 * browser and is never sent here.
 *
 * Security posture matches functions/api/fetch-llms-txt.js: absolute
 * private-address guard on every hop, manual redirect handling, fetch timeout,
 * body-size ceiling. A cross-host redirect is followed and reported rather than
 * refused, because apex-to-www is routine.
 *
 * One protocol detail that matters here: robots.txt applies per origin, so a
 * redirect to a different host means the rules belong to that host, not the one
 * the user typed. The response flags that so the UI can say so.
 */

const MAX_BODY_BYTES = 500_000;
const FETCH_TIMEOUT_MS = 8_000;
const USER_AGENT = "NinadPathak-ai-crawler-checker/1.0 (+https://ninadpathak.com/ai-crawler-checker/)";

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
    throw new Error("Enter a valid domain.");
  }
  if (!["http:", "https:"].includes(url.protocol)) throw new Error("The domain must use http:// or https://.");
  const host = url.hostname.toLowerCase().replace(/\.$/, "");
  if (!host || host === "localhost" || host.endsWith(".localhost") || host.endsWith(".local") ||
      host.endsWith(".internal") || host.includes(":") || isPrivateIpv4(host)) {
    throw new Error("Private and local network addresses cannot be checked.");
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
  for (let redirect = 0; redirect < 4; redirect += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    let response;
    try {
      response = await fetch(url, {
        redirect: "manual",
        signal: controller.signal,
        headers: { "user-agent": USER_AGENT, accept: "text/plain, */*;q=0.5" },
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
  if (declared > MAX_BODY_BYTES) throw new Error("That robots.txt is too large to read safely.");
  const text = await response.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) {
    throw new Error("That robots.txt is too large to read safely.");
  }
  return text;
}

/* A 200 carrying an HTML document is the common real failure: the host serves a
 * styled 404 or its SPA shell instead of the file. Crawlers treat that as an
 * unparseable file, which is not the same as an absent one. */
function looksLikeHtml(text) {
  const head = text.slice(0, 2000).toLowerCase();
  return /<!doctype html|<html[\s>]|<head[\s>]|<body[\s>]/.test(head);
}

export async function onRequestPost(context) {
  let payload;
  try {
    payload = await context.request.json();
  } catch {
    return json({ error: "Send a domain as JSON." }, 400);
  }

  try {
    const input = String(payload.url || "").trim();
    if (!input) return json({ error: "Enter a domain." }, 400);

    const initial = validatePublicUrl(/^https?:\/\//i.test(input) ? input : `https://${input}`);
    const target = new URL("/robots.txt", initial).toString();

    const { response, url, chain, leftOriginalSite } = await safeFetch(target, initial.hostname);
    const contentType = (response.headers.get("content-type") || "").toLowerCase();

    /* A 404 is a real and meaningful answer: no robots.txt means nothing is
     * disallowed, so every crawler is permitted. That is not an error state. */
    if (response.status === 404 || response.status === 410) {
      return json({
        found: false,
        absent: true,
        requestedUrl: target,
        finalUrl: url.toString(),
        status: response.status,
        content: "",
        message: `No robots.txt at ${url.toString()} (HTTP ${response.status}). An absent file disallows nothing, so every crawler is permitted.`,
      });
    }

    if (!response.ok) {
      return json({
        found: false,
        absent: false,
        requestedUrl: target,
        finalUrl: url.toString(),
        status: response.status,
        error: `robots.txt returned HTTP ${response.status}. A server error is not the same as an absent file, and crawler behaviour on a 5xx varies.`,
      });
    }

    const text = await readText(response);

    return json({
      found: true,
      absent: false,
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
      ? "That domain took too long to respond."
      : error.message;
    return json({ error: message || "That robots.txt could not be fetched." }, 422);
  }
}
