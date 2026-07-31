const MAX_PAGES = 100;
const MAX_SITEMAPS = 12;
const MAX_METADATA_BATCH = 20;
const MAX_BODY_BYTES = 1_500_000;
const FETCH_TIMEOUT_MS = 8_000;
const USER_AGENT = "NinadPathak-llms-txt-generator/1.0 (+https://ninadpathak.com/llms-txt-generator/)";

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
  if (!['http:', 'https:'].includes(url.protocol)) throw new Error("The website must use http:// or https://.");
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
  for (let redirect = 0; redirect < 4; redirect += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    let response;
    try {
      response = await fetch(url, {
        redirect: "manual",
        signal: controller.signal,
        headers: { "user-agent": USER_AGENT, accept: "text/html, application/xml, text/xml, text/plain;q=0.8" },
      });
    } finally {
      clearTimeout(timer);
    }
    if (response.status >= 300 && response.status < 400 && response.headers.get("location")) {
      url = validatePublicUrl(new URL(response.headers.get("location"), url).toString(), expectedHost);
      continue;
    }
    return { response, url };
  }
  throw new Error("Too many redirects.");
}

async function readText(response) {
  const length = Number(response.headers.get("content-length") || 0);
  if (length > MAX_BODY_BYTES) throw new Error("A response was too large to scan safely.");
  const text = await response.text();
  if (new TextEncoder().encode(text).length > MAX_BODY_BYTES) throw new Error("A response was too large to scan safely.");
  return text;
}

function decodeEntities(value) {
  const entities = { amp: "&", quot: '"', apos: "'", lt: "<", gt: ">", nbsp: " " };
  return value.replace(/&(#x?[0-9a-f]+|[a-z]+);/gi, (match, key) => {
    const lower = key.toLowerCase();
    if (lower[0] === "#") {
      const hex = lower[1] === "x";
      const code = parseInt(lower.slice(hex ? 2 : 1), hex ? 16 : 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : match;
    }
    return entities[lower] || match;
  });
}

function cleanText(value = "") {
  return decodeEntities(value.replace(/<[^>]*>/g, " ")).replace(/\s+/g, " ").trim();
}

function metaContent(html, key, attribute = "name") {
  const tags = html.match(/<meta\b[^>]*>/gi) || [];
  for (const tag of tags) {
    const attrs = {};
    tag.replace(/([\w:-]+)\s*=\s*(["'])(.*?)\2/gi, (_, name, _quote, value) => { attrs[name.toLowerCase()] = value; });
    if ((attrs[attribute] || "").toLowerCase() === key.toLowerCase()) return cleanText(attrs.content || "");
  }
  return "";
}

function pageMetadata(html, requestedUrl) {
  const titleMatch = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  const h1Match = html.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/i);
  const langMatch = html.match(/<html\b[^>]*\blang\s*=\s*["']([^"']+)/i);
  const canonicalMatch = html.match(/<link\b[^>]*\brel\s*=\s*["'][^"']*canonical[^"']*["'][^>]*>/i);
  const hrefMatch = canonicalMatch && canonicalMatch[0].match(/\bhref\s*=\s*["']([^"']+)/i);
  let canonical = requestedUrl;
  try { if (hrefMatch) canonical = new URL(hrefMatch[1], requestedUrl).toString(); } catch { /* retain requested URL */ }
  return {
    title: cleanText(titleMatch ? titleMatch[1] : (h1Match ? h1Match[1] : new URL(requestedUrl).pathname)),
    description: metaContent(html, "description") || metaContent(html, "og:description", "property"),
    canonical,
    language: langMatch ? cleanText(langMatch[1]) : "",
    siteName: metaContent(html, "og:site_name", "property"),
  };
}

function xmlLocations(xml) {
  const values = [];
  const pattern = /<loc\b[^>]*>([\s\S]*?)<\/loc>/gi;
  let match;
  while ((match = pattern.exec(xml))) values.push(cleanText(match[1]));
  return values;
}

function sitemapUrlsFromRobots(text, base) {
  return text.split(/\r?\n/).map((line) => line.match(/^\s*sitemap\s*:\s*(.+?)\s*$/i)).filter(Boolean)
    .map((match) => new URL(match[1], base).toString());
}

function internalLinksFromHtml(html, baseUrl, host) {
  const links = [];
  const seen = new Set();
  const pattern = /<a\b[^>]*\bhref\s*=\s*(["'])(.*?)\1/gi;
  let match;
  while ((match = pattern.exec(html)) && links.length < MAX_PAGES) {
    try {
      const url = validatePublicUrl(new URL(decodeEntities(match[2]), baseUrl).toString(), host);
      url.hash = "";
      if (url.search || /\.(?:jpg|jpeg|png|gif|webp|svg|pdf|zip|xml)$/i.test(url.pathname)) continue;
      const normalized = url.toString();
      if (!seen.has(normalized)) {
        seen.add(normalized);
        links.push(normalized);
      }
    } catch { /* ignore non-HTTP and off-site links */ }
  }
  return links;
}

async function discoverFromSitemaps(baseUrl, host) {
  const queue = [];
  try {
    const { response } = await safeFetch(new URL("/robots.txt", baseUrl).toString(), host);
    if (response.ok) queue.push(...sitemapUrlsFromRobots(await readText(response), baseUrl));
  } catch { /* sitemap.xml remains the fallback */ }
  queue.push(new URL("/sitemap.xml", baseUrl).toString());

  const seenSitemaps = new Set();
  const pages = new Set();
  while (queue.length && seenSitemaps.size < MAX_SITEMAPS && pages.size < MAX_PAGES) {
    const candidate = queue.shift();
    let sitemapUrl;
    try {
      sitemapUrl = validatePublicUrl(candidate, host).toString();
    } catch { continue; }
    if (seenSitemaps.has(sitemapUrl)) continue;
    seenSitemaps.add(sitemapUrl);
    try {
      const { response, url } = await safeFetch(sitemapUrl, host);
      if (!response.ok) continue;
      const xml = await readText(response);
      const locations = xmlLocations(xml);
      if (/<sitemapindex\b/i.test(xml)) queue.push(...locations);
      else {
        for (const location of locations) {
          try {
            const page = validatePublicUrl(new URL(location, url).toString(), host);
            if (!/\.(?:xml|jpg|jpeg|png|gif|webp|svg|pdf|zip)$/i.test(page.pathname)) pages.add(page.toString());
          } catch { /* ignore off-site or invalid sitemap entries */ }
          if (pages.size >= MAX_PAGES) break;
        }
      }
    } catch { /* try the next sitemap */ }
  }
  return { urls: [...pages], sitemapCount: seenSitemaps.size };
}

async function mapWithConcurrency(items, concurrency, callback) {
  const results = new Array(items.length);
  let next = 0;
  async function worker() {
    while (next < items.length) {
      const index = next++;
      results[index] = await callback(items[index]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, worker));
  return results;
}

async function fetchPageMetadata(urls, host) {
  const records = await mapWithConcurrency(urls, 6, async (pageUrl) => {
    try {
      const { response, url } = await safeFetch(pageUrl, host);
      if (!response.ok || !(response.headers.get("content-type") || "").toLowerCase().includes("text/html")) return null;
      const metadata = pageMetadata(await readText(response), url.toString());
      if (new URL(metadata.canonical).hostname !== host) return null;
      return { title: metadata.title || url.pathname, url: metadata.canonical, description: metadata.description };
    } catch { return null; }
  });
  const unique = [];
  const seen = new Set();
  for (const page of records) {
    if (!page || seen.has(page.url)) continue;
    seen.add(page.url);
    unique.push(page);
  }
  return unique;
}

export async function onRequestPost(context) {
  let payload;
  try { payload = await context.request.json(); } catch { return json({ error: "Send a website URL as JSON." }, 400); }
  try {
    const input = String(payload.url || "").trim();
    const initial = validatePublicUrl(/^https?:\/\//i.test(input) ? input : `https://${input}`);
    if (Array.isArray(payload.pages)) {
      const requested = payload.pages.slice(0, MAX_METADATA_BATCH).map((pageUrl) =>
        validatePublicUrl(new URL(String(pageUrl), initial).toString(), initial.hostname).toString()
      );
      return json({ pages: await fetchPageMetadata(requested, initial.hostname) });
    }
    const { response: homeResponse, url: homeUrl } = await safeFetch(initial.toString());
    if (!homeResponse.ok) return json({ error: `The homepage returned HTTP ${homeResponse.status}.` }, 422);
    const homeHtml = await readText(homeResponse);
    const home = pageMetadata(homeHtml, homeUrl.toString());
    const discovery = await discoverFromSitemaps(homeUrl, homeUrl.hostname);
    const urls = discovery.urls.length ? discovery.urls : internalLinksFromHtml(homeHtml, homeUrl, homeUrl.hostname);
    if (!urls.includes(homeUrl.toString())) urls.unshift(homeUrl.toString());
    if (urls.length > MAX_PAGES) urls.length = MAX_PAGES;

    return json({
      site: {
        name: home.siteName || home.title.replace(/\s*[|–—-]\s*[^|–—-]+$/, "") || homeUrl.hostname,
        url: `${homeUrl.protocol}//${homeUrl.host}`,
        description: home.description,
        language: home.language,
      },
      urls,
      sitemapFound: discovery.urls.length > 0,
      sitemapCount: discovery.sitemapCount,
      truncated: discovery.urls.length >= MAX_PAGES,
      limit: MAX_PAGES,
    });
  } catch (error) {
    const message = error && error.name === "AbortError" ? "The website took too long to respond." : error.message;
    return json({ error: message || "The website could not be scanned." }, 422);
  }
}
