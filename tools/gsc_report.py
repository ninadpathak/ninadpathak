#!/usr/bin/env python3
"""Search Console movement, decay, and striking-distance report, per cluster.

The operating loop in CHARTER.md section 5 asks the same three questions every cycle,
and until now the only instrument that answered them was an ad-hoc script in a session
temp directory, which meant the analysis died with the session. This is the durable
version. It sits alongside tools/daily_cycle.py and shares its conventions.

    WHAT MOVED    position and click deltas, trailing 28 days against the prior 28,
                  by page and by query. Anything moving more than three places is flagged.
    WHAT DECAYED  pages losing impressions or position. The campaign has no other way
                  to see this, and a decaying page needs a refresh, not a new article.
    WHAT IS CLOSE queries in positions 4-30 with real impressions, after the machine
                  keyword-salad fan-out is separated out. See FAN-OUT below - this is
                  the part that decides whether the report is useful or misleading.

Plus a per-cluster rollup, so a cluster earning nothing is visible instead of averaged
into the site total.

Two conventions inherited from tools/daily_cycle.py, both load-bearing:

  * Search Console lags about three days. Every window ends GSC_LAG_DAYS back, because
    asking for yesterday returns zeros and reads as a collapse.
  * The query dimension does NOT sum to the sitewide total - Search Console withholds
    low-volume queries. Every figure derived from the query dimension is therefore a
    floor, and is labelled as one wherever it prints. Never present one as a total.

FAN-OUT, and why it gets this much code
---------------------------------------
This site's query data is dominated by machine-generated permutation fan-out. In the
28 days to 2026-08-14, 26 of the 46 queries sitting in positions 4-30 were reorderings
of one token core - `anthropic contextual retrieval` decorated with bm25, embeddings,
reranking, official, blog, 2024 - carrying 145 impressions and zero clicks between
them. Ranked naively by impressions they bury the three or four genuinely human queries
in reach, and a campaign that chases them optimises for a phantom.

The heuristic is deliberately structural rather than a keyword blocklist:

  1. BLOB     more than MAX_QUERY_WORDS words, or containing an object-replacement or
              control character. These are pasted passages, not queries.
  2. FAMILY   single-link clustering of content-token sets at Jaccard >= JACCARD_THRESHOLD.
              A group of MIN_FAMILY_SIZE or more is treated as one fan-out family and
              collapsed to a single reported line, never silently dropped.
  3. ABSORB   two looser passes pull in decorated stragglers that carry enough novel
              tokens to fall under the primary threshold: a query joins a family if it
              reaches JACCARD_ABSORB against any member, or if it contains one of the
              family's signature phrases - a contiguous SIGNATURE_NGRAM-token run shared
              by at least SIGNATURE_SHARE of the members, which is what a generator
              holding a stem looks like. Neither pass will absorb a query that adds
              fewer than CORE_EXTRA_TOKENS tokens to that stem, because the bare stem is
              a real head term and must survive.

Its limits, stated plainly because they matter:

  * A genuine topic with many close human variants will cluster too. Nothing is deleted -
    families are reported with their combined impressions - but a real cluster can be
    collapsed into one line, so read the family list, not just the human list.
  * The signature-phrase pass assumes a generator holds a contiguous stem. Fan-out that
    permutes every token with no stable run will not be absorbed by it, and fan-out
    built from wholly novel vocabulary each time will not cluster at all.
  * Token-set clustering is order-blind by design, which is what catches permutations,
    and it therefore cannot tell a reordering from a distinct question built of the same
    words.
  * The stopword ratio is computed and printed for surviving long queries as a weak
    corroborating signal. It is NOT used to exclude anything, because it misfires on
    terse human queries ("long context windows" scores zero).
  * Brand and near-brand queries are filtered with the same regex daily_cycle.py uses.
    A query for an unrelated person's name is not brand and will show up; that is honest
    rather than tidy.

    tools/gsc_report.py                  # report, and append to planning/gsc-report.md
    tools/gsc_report.py --dry-run        # print, write nothing
    tools/gsc_report.py --json out.json  # machine-readable alongside the markdown

Needs GOOGLE_APPLICATION_CREDENTIALS or the workspace service-account file, plus
google-api-python-client, google-auth, and python-frontmatter.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import pathlib
import re
import sys
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "sc-domain:ninadpathak.com"
CRED_DEFAULT = pathlib.Path(
    "/Users/ninad/Development/.google-service-account/google-workspace-service-account.json"
)
LOG = ROOT / "planning" / "gsc-report.md"
POSTS = ROOT / "content" / "posts"

# Search Console lags roughly three days; see module docstring.
GSC_LAG_DAYS = 3
WINDOW_DAYS = 28

# Movement worth a human looking at it.
POSITION_FLAG = 3.0
# Below this a delta is sampling noise, not a signal.
MIN_PRIOR_IMPRESSIONS = 5
MIN_CLOSE_IMPRESSIONS = 3
CLOSE_RANGE = (4.0, 30.0)

# Fan-out detection. See module docstring for what each one does and why.
MAX_QUERY_WORDS = 15
JACCARD_THRESHOLD = 0.6
# Looser threshold used only to absorb stragglers into an already-formed family.
JACCARD_ABSORB = 0.4
MIN_FAMILY_SIZE = 3
MIN_FAMILY_TOKENS = 4
CORE_EXTRA_TOKENS = 2
# A contiguous run this long, shared by most of a family, is a held generator stem.
SIGNATURE_NGRAM = 3
SIGNATURE_SHARE = 0.5

# Same brand test as daily_cycle.py, so the two tools agree on what brand means.
BRAND = re.compile(r"ninad|pathak", re.IGNORECASE)

# The cluster map in campaign-90d.md section 3. Post cluster comes from the `category`
# frontmatter field, which is what tools/audit_clusters.py treats as authoritative.
CLUSTERS: list[tuple[int, str, str]] = [
    (1, "technical-documentation", "Technical documentation & docs ops"),
    (2, "developer-experience", "Developer experience & DevRel"),
    (3, "ai-engineering", "AI agents, memory, RAG, inference"),
    (4, "ai-search-optimization", "AI Overviews & AI-search citation"),
    (5, "reddit-marketing", "Reddit marketing"),
    (6, "community-building", "Forums & community building"),
    (7, "technical-events", "Technical & community events"),
]
CLUSTER_BY_SLUG = {slug: num for num, slug, _ in CLUSTERS}
CLUSTER_LABEL = {num: label for num, _, label in CLUSTERS}
# campaign-90d.md section 3 assigns the shipped tools to the cluster-4 owner page.
TOOL_PATHS = {"/linter/": "ai-search-optimization",
              "/llms-txt-generator/": "ai-search-optimization"}

# build.py routes posts to /articles/<slug>/, but Search Console still reports most of
# this site's traffic under the pre-migration /blog/<slug>/ path - 51 of 54 /blog/ pages
# in the 28 days to 2026-08-14 carry a slug that still belongs to a published post, and
# /blog/ held 1,259 of 1,767 impressions against /articles/'s 86. Treating the two as
# one page identity is the only way the cluster rollup describes reality; keeping them
# apart would file the site's actual traffic under "no cluster".
POST_PATH_PREFIXES = ("/articles/", "/blog/")
CANONICAL_POST_PREFIX = "/articles/"

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this", "these",
    "those", "is", "are", "was", "were", "be", "been", "being", "do", "does", "did",
    "doing", "done", "have", "has", "had", "how", "what", "why", "when", "where",
    "which", "who", "whom", "whose", "can", "could", "should", "would", "will", "shall",
    "may", "might", "must", "i", "you", "he", "she", "it", "we", "they", "me", "my",
    "your", "his", "her", "its", "our", "their", "in", "on", "at", "by", "for", "with",
    "from", "to", "of", "as", "about", "into", "over", "under", "vs", "versus",
    "between", "without", "within", "during", "after", "before", "not", "no", "there",
    "here", "get", "got", "make", "makes", "keep", "use", "using", "best", "practices",
}

TOKEN = re.compile(r"[a-z0-9][a-z0-9\-\.]*")


# --------------------------------------------------------------------- pure helpers

def tokens(query: str) -> list[str]:
    return TOKEN.findall(query.lower())


def content_token_list(query: str) -> list[str]:
    """Topic-bearing tokens in the order written, for phrase signatures."""
    return [t for t in tokens(query) if t not in STOPWORDS]


def content_tokens(query: str) -> set[str]:
    """Tokens carrying topic meaning. Order is discarded, which is the point."""
    return set(content_token_list(query))


def ngrams(query: str, n: int = SIGNATURE_NGRAM) -> set[tuple[str, ...]]:
    """Contiguous content-token n-grams, for detecting a held stem."""
    t = content_token_list(query)
    return {tuple(t[i:i + n]) for i in range(len(t) - n + 1)}


def stopword_ratio(query: str) -> float:
    t = tokens(query)
    return sum(1 for x in t if x in STOPWORDS) / len(t) if t else 0.0


def is_blob(query: str) -> bool:
    """A pasted passage rather than a query."""
    if len(query.split()) > MAX_QUERY_WORDS:
        return True
    return any(ord(c) < 32 or c == "￼" for c in query)


def jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def find_families(queries: list[str]) -> list[list[str]]:
    """Single-link clusters of permutation variants, largest first.

    Two passes, per the module docstring: Jaccard clustering, then core containment to
    absorb decorated stragglers that fell under the threshold.
    """
    sets = {q: content_tokens(q) for q in queries}
    eligible = sorted(q for q in queries if len(sets[q]) >= MIN_FAMILY_TOKENS)

    parent = {q: q for q in eligible}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i, a in enumerate(eligible):
        for b in eligible[i + 1:]:
            if jaccard(sets[a], sets[b]) >= JACCARD_THRESHOLD:
                union(a, b)

    grouped: dict[str, list[str]] = collections.defaultdict(list)
    for q in eligible:
        grouped[find(q)].append(q)
    families = [sorted(v) for v in grouped.values() if len(v) >= MIN_FAMILY_SIZE]

    # Straggler absorption. A decorated variant can fall under the primary threshold
    # simply by carrying novel tokens, so two looser passes pull it in. Both refuse to
    # absorb a query that adds nothing to the stem, because that one is the head term.
    claimed = {q for fam in families for q in fam}
    for fam in families:
        signatures = signature_phrases(fam)
        for q in queries:
            if q in claimed or q in fam:
                continue
            qt = sets[q]
            near = any(jaccard(qt, sets[m]) >= JACCARD_ABSORB for m in fam if m in sets)
            stem = ngrams(q) & signatures
            if not (near or stem):
                continue
            floor = max(sig_len for sig_len in (len(s) for s in stem)) if stem else 0
            if len(qt) < floor + CORE_EXTRA_TOKENS:
                continue
            fam.append(q)
            claimed.add(q)
    for fam in families:
        fam.sort()

    return sorted(families, key=lambda f: -len(f))


def signature_phrases(family: list[str]) -> set[tuple[str, ...]]:
    """Contiguous n-grams shared by most of a family — the generator's held stem."""
    if not family:
        return set()
    counts: collections.Counter = collections.Counter()
    for q in family:
        counts.update(ngrams(q))
    need = max(2, int(len(family) * SIGNATURE_SHARE))
    return {gram for gram, n in counts.items() if n >= need}


def family_core(family: list[str]) -> set[str]:
    return set.intersection(*[content_tokens(q) for q in family]) if family else set()


def load_slug_clusters(posts_dir: pathlib.Path = POSTS) -> dict[str, str]:
    """slug -> category, from post frontmatter. Same source as audit_clusters.py."""
    try:
        import frontmatter
    except ImportError:
        return {}
    if not posts_dir.exists():
        return {}
    mapping: dict[str, str] = {}
    for path in sorted(posts_dir.glob("*.md")):
        data = frontmatter.load(path)
        if data.get("status") != "published":
            continue
        slug = data.get("slug") or path.stem
        category = data.get("category")
        if category:
            mapping[str(slug)] = str(category)
    return mapping


def post_slug(url: str) -> str | None:
    """Slug for a post URL under either the canonical or the legacy path prefix."""
    path = urlsplit(url).path
    if not path.endswith("/"):
        path += "/"
    for prefix in POST_PATH_PREFIXES:
        match = re.fullmatch(re.escape(prefix) + r"([^/]+)/", path)
        if match:
            return match.group(1)
    return None


def page_cluster(url: str, slug_clusters: dict[str, str]) -> str | None:
    """Cluster category slug for a page URL, or None if it belongs to no cluster."""
    path = urlsplit(url).path
    if not path.endswith("/"):
        path += "/"
    if path in TOOL_PATHS:
        return TOOL_PATHS[path]
    slug = post_slug(url)
    if slug is None:
        return None
    if slug in slug_clusters:
        return slug_clusters[slug]
    # A cluster owner page is /articles/<category>/ and has no post of its own.
    if slug in CLUSTER_BY_SLUG:
        return slug
    return None


def path_split(page_rows: list[dict]) -> dict:
    """Impressions on the canonical post path against the legacy one.

    Surfaced because a migration that left the old path ranking is invisible in a
    cluster rollup once both are mapped to the same cluster.
    """
    canonical = legacy = other = 0.0
    for row in page_rows:
        path = urlsplit(row["keys"][0]).path
        if path.startswith(CANONICAL_POST_PREFIX):
            canonical += row["impressions"]
        elif any(path.startswith(p) for p in POST_PATH_PREFIXES):
            legacy += row["impressions"]
        else:
            other += row["impressions"]
    return {"canonical": int(canonical), "legacy": int(legacy), "other": int(other)}


def windows(today: dt.date, window_days: int = WINDOW_DAYS,
            lag_days: int = GSC_LAG_DAYS) -> tuple[dt.date, dt.date, dt.date, dt.date]:
    """Current and prior comparison windows, both ending `lag_days` back."""
    end = today - dt.timedelta(days=lag_days)
    start = end - dt.timedelta(days=window_days - 1)
    prior_end = start - dt.timedelta(days=1)
    prior_start = prior_end - dt.timedelta(days=window_days - 1)
    return start, end, prior_start, prior_end


def index_rows(rows: list[dict]) -> dict[str, dict]:
    """GSC rows keyed by their single dimension value."""
    return {r["keys"][0]: r for r in rows}


def deltas(current: dict[str, dict], prior: dict[str, dict],
           min_prior_impressions: int = MIN_PRIOR_IMPRESSIONS) -> list[dict]:
    """Movement for every key present in either window.

    Position is better when lower, so `position_delta` is prior minus current: positive
    means it improved. Keys too small in the prior window to compare are marked `new`
    rather than being given a fake delta.
    """
    out = []
    for key in sorted(set(current) | set(prior)):
        cur, pre = current.get(key), prior.get(key)
        row = {
            "key": key,
            "clicks": int(cur["clicks"]) if cur else 0,
            "prior_clicks": int(pre["clicks"]) if pre else 0,
            "impressions": int(cur["impressions"]) if cur else 0,
            "prior_impressions": int(pre["impressions"]) if pre else 0,
            "position": round(cur["position"], 1) if cur else None,
            "prior_position": round(pre["position"], 1) if pre else None,
        }
        row["clicks_delta"] = row["clicks"] - row["prior_clicks"]
        row["impressions_delta"] = row["impressions"] - row["prior_impressions"]
        if cur and pre and pre["impressions"] >= min_prior_impressions:
            row["position_delta"] = round(pre["position"] - cur["position"], 1)
            row["comparable"] = True
        else:
            row["position_delta"] = None
            row["comparable"] = False
        row["status"] = ("new" if cur and not pre else
                         "gone" if pre and not cur else "present")
        out.append(row)
    return out


def flagged_moves(rows: list[dict], threshold: float = POSITION_FLAG) -> list[dict]:
    """Comparable rows whose position moved more than `threshold` places."""
    moved = [r for r in rows
             if r["comparable"] and abs(r["position_delta"]) > threshold]
    return sorted(moved, key=lambda r: -abs(r["position_delta"]))


def decaying(rows: list[dict], min_prior_impressions: int = MIN_PRIOR_IMPRESSIONS) -> list[dict]:
    """Pages losing impressions or losing position, worst first.

    Requires a prior window big enough to mean something, so a page going from two
    impressions to one is not reported as decay.
    """
    out = []
    for r in rows:
        if r["prior_impressions"] < min_prior_impressions:
            continue
        lost_impressions = r["impressions_delta"] < 0
        lost_position = r["comparable"] and r["position_delta"] < 0
        if lost_impressions or lost_position:
            out.append(r)
    return sorted(out, key=lambda r: (r["impressions_delta"],
                                      r["position_delta"] or 0))


def classify_close(rows: list[dict],
                   close_range: tuple[float, float] = CLOSE_RANGE,
                   min_impressions: int = MIN_CLOSE_IMPRESSIONS) -> dict:
    """Split striking-distance queries into human, fan-out families, blobs, and brand.

    Returns every bucket. Nothing is discarded silently - the caller reports the
    families and the counts alongside the human list.
    """
    lo, hi = close_range
    in_range = [r for r in rows if lo <= r["position"] <= hi]

    brand = [r for r in in_range if BRAND.search(r["keys"][0])]
    rest = [r for r in in_range if not BRAND.search(r["keys"][0])]

    blobs = [r for r in rest if is_blob(r["keys"][0])]
    rest = [r for r in rest if not is_blob(r["keys"][0])]

    by_query = index_rows(rest)
    families = find_families(list(by_query))

    family_rows = []
    claimed: set[str] = set()
    for fam in families:
        members = [by_query[q] for q in fam if q in by_query]
        if not members:
            continue
        claimed.update(q for q in fam if q in by_query)
        impressions = sum(m["impressions"] for m in members)
        clicks = sum(m["clicks"] for m in members)
        weighted = (sum(m["position"] * m["impressions"] for m in members) / impressions
                    if impressions else 0.0)
        family_rows.append({
            "variants": len(members),
            "core": sorted(family_core(fam)),
            "impressions": int(impressions),
            "clicks": int(clicks),
            "position": round(weighted, 1),
            "example": max(members, key=lambda m: m["impressions"])["keys"][0],
        })
    family_rows.sort(key=lambda f: -f["impressions"])

    human = [r for r in rest if r["keys"][0] not in claimed]
    thin = [r for r in human if r["impressions"] < min_impressions]
    human = [r for r in human if r["impressions"] >= min_impressions]
    human.sort(key=lambda r: -r["impressions"])

    return {
        "in_range": len(in_range),
        "in_range_impressions": int(sum(r["impressions"] for r in in_range)),
        "human": [{"query": r["keys"][0], "impressions": int(r["impressions"]),
                   "clicks": int(r["clicks"]), "position": round(r["position"], 1),
                   "stopword_ratio": round(stopword_ratio(r["keys"][0]), 2)}
                  for r in human],
        "families": family_rows,
        "excluded": {
            "brand": len(brand), "blob": len(blobs),
            "fan_out": len(claimed), "below_impression_floor": len(thin),
        },
        "excluded_impressions": {
            "brand": int(sum(r["impressions"] for r in brand)),
            "blob": int(sum(r["impressions"] for r in blobs)),
            "fan_out": int(sum(f["impressions"] for f in family_rows)),
            "below_impression_floor": int(sum(r["impressions"] for r in thin)),
        },
    }


def cluster_rollup(page_rows: list[dict], slug_clusters: dict[str, str]) -> list[dict]:
    """Impressions, clicks and impression-weighted position for each of the seven clusters."""
    buckets: dict[str | None, dict] = {}
    for row in page_rows:
        category = page_cluster(row["keys"][0], slug_clusters)
        b = buckets.setdefault(category, {"clicks": 0.0, "impressions": 0.0,
                                          "weighted": 0.0, "pages": 0})
        b["clicks"] += row["clicks"]
        b["impressions"] += row["impressions"]
        b["weighted"] += row["position"] * row["impressions"]
        b["pages"] += 1

    out = []
    for num, slug, label in CLUSTERS:
        b = buckets.get(slug, {"clicks": 0.0, "impressions": 0.0, "weighted": 0.0, "pages": 0})
        out.append({
            "cluster": num, "slug": slug, "label": label, "pages": b["pages"],
            "clicks": int(b["clicks"]), "impressions": int(b["impressions"]),
            "position": round(b["weighted"] / b["impressions"], 1) if b["impressions"] else None,
        })
    b = buckets.get(None)
    if b:
        out.append({
            "cluster": None, "slug": "(no cluster)", "label": "Pages in no cluster",
            "pages": b["pages"], "clicks": int(b["clicks"]),
            "impressions": int(b["impressions"]),
            "position": round(b["weighted"] / b["impressions"], 1) if b["impressions"] else None,
        })
    return out


# --------------------------------------------------------------------------- fetch

def search_console(cred: str | None = None):
    """Authenticated Search Console client, or None if unavailable."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        return None
    path = cred or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or str(CRED_DEFAULT)
    if not pathlib.Path(path).exists():
        return None
    creds = service_account.Credentials.from_service_account_file(
        path, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


def fetch(svc, start: str, end: str, dimension: str) -> list[dict]:
    body = {"startDate": start, "endDate": end, "rowLimit": 25000}
    if dimension:
        body["dimensions"] = [dimension]
    return svc.searchanalytics().query(siteUrl=SITE, body=body).execute().get("rows", [])


# -------------------------------------------------------------------------- render

def render(data: dict) -> str:
    w = data["windows"]
    L: list[str] = []
    L.append(f"\n## {data['generated']}\n")
    L.append(f"Current window {w['start']} to {w['end']} ({data['window_days']}d), "
             f"against {w['prior_start']} to {w['prior_end']}. "
             f"Windows end {GSC_LAG_DAYS} days back because Search Console lags.\n")

    t, tp = data["totals"], data["prior_totals"]
    L.append(f"**Sitewide** {t['clicks']} clicks / {t['impressions']} impressions, "
             f"avg pos {t['position']:.1f} "
             f"(prior {tp['clicks']} / {tp['impressions']}, pos {tp['position']:.1f}).\n")
    L.append(f"Query dimension sees {data['query_floor']['impressions']} impressions across "
             f"{data['query_floor']['queries']} named queries — a **floor**, not a total: "
             f"Search Console withholds low-volume queries.\n")

    L.append("\n### Cluster rollup\n")
    L.append("| # | Cluster | Pages | Clicks | Impressions | Avg pos |")
    L.append("|---:|---|---:|---:|---:|---:|")
    for c in data["clusters"]:
        num = c["cluster"] if c["cluster"] is not None else "—"
        pos = f"{c['position']:.1f}" if c["position"] is not None else "—"
        L.append(f"| {num} | {c['label']} | {c['pages']} | {c['clicks']} | "
                 f"{c['impressions']} | {pos} |")
    silent = [c for c in data["clusters"]
              if c["cluster"] is not None and c["impressions"] == 0]
    if silent:
        L.append(f"\n**Earning nothing:** " + ", ".join(
            f"cluster {c['cluster']} ({c['label']})" for c in silent) + ".")

    p = data["path_split"]
    total_post = p["canonical"] + p["legacy"]
    if p["legacy"]:
        share = 100 * p["legacy"] / total_post if total_post else 0
        L.append(f"\n**Post-path split:** {p['canonical']} impressions on the canonical "
                 f"`{CANONICAL_POST_PREFIX}` path against {p['legacy']} on the legacy "
                 f"`/blog/` path ({share:.0f}% legacy), plus {p['other']} elsewhere. Both "
                 f"prefixes map to the same cluster here, since the slug identifies the "
                 f"post; a high legacy share means the migration is still unresolved.")

    L.append("\n### What moved\n")
    for label, key in (("Pages", "page_moves"), ("Queries", "query_moves")):
        rows = data[key]
        L.append(f"\n**{label}** — {len(rows)} moved more than "
                 f"{POSITION_FLAG:g} places.\n")
        if not rows:
            L.append("None.")
            continue
        L.append("| " + ("Page" if key == "page_moves" else "Query") +
                 " | Pos | Prior | Δpos | Clicks Δ | Impr Δ |")
        L.append("|---|---:|---:|---:|---:|---:|")
        for r in rows[:20]:
            arrow = "up" if r["position_delta"] > 0 else "down"
            L.append(f"| {r['key'][:70]} | {r['position']} | {r['prior_position']} | "
                     f"**{r['position_delta']:+.1f}** {arrow} | {r['clicks_delta']:+d} | "
                     f"{r['impressions_delta']:+d} |")

    L.append("\n### What decayed\n")
    dec = data["decayed"]
    L.append(f"{len(dec)} page(s) lost impressions or position, prior window at least "
             f"{MIN_PRIOR_IMPRESSIONS} impressions. A decaying page wants a refresh, "
             f"not a new article.\n")
    if dec:
        L.append("| Page | Impr | Prior | Δ | Pos | Δpos |")
        L.append("|---|---:|---:|---:|---:|---:|")
        for r in dec[:20]:
            dp = f"{r['position_delta']:+.1f}" if r["position_delta"] is not None else "—"
            L.append(f"| {r['key'][:70]} | {r['impressions']} | {r['prior_impressions']} | "
                     f"{r['impressions_delta']:+d} | {r['position'] or '—'} | {dp} |")
    else:
        L.append("None.")

    c = data["close"]
    L.append("\n### What is close\n")
    ex, exi = c["excluded"], c["excluded_impressions"]
    L.append(f"{c['in_range']} queries sit in positions {CLOSE_RANGE[0]:g}–{CLOSE_RANGE[1]:g} "
             f"carrying {c['in_range_impressions']} impressions. Separated out: "
             f"{ex['fan_out']} machine fan-out variants ({exi['fan_out']} impressions), "
             f"{ex['brand']} brand ({exi['brand']}), {ex['blob']} pasted blob "
             f"({exi['blob']}), {ex['below_impression_floor']} below the "
             f"{MIN_CLOSE_IMPRESSIONS}-impression floor ({exi['below_impression_floor']}).\n")

    L.append(f"\n**Human queries in reach — {len(c['human'])}.**\n")
    if c["human"]:
        L.append("| Query | Impr | Clicks | Pos | Stopword ratio |")
        L.append("|---|---:|---:|---:|---:|")
        for r in c["human"]:
            L.append(f"| {r['query'][:70]} | {r['impressions']} | {r['clicks']} | "
                     f"{r['position']} | {r['stopword_ratio']} |")
        L.append("\nStopword ratio is printed as a weak corroborating signal only. "
                 "It excludes nothing — terse human queries score zero.")
    else:
        L.append("None above the impression floor.")

    L.append(f"\n**Machine fan-out families — {len(c['families'])}.** "
             "Collapsed, not dropped. A real topic with many close human variants would "
             "cluster here too, so read this list rather than trusting the split blindly.\n")
    if c["families"]:
        L.append("| Variants | Shared core | Impr | Clicks | Avg pos | Example |")
        L.append("|---:|---|---:|---:|---:|---|")
        for f in c["families"]:
            L.append(f"| {f['variants']} | `{' '.join(f['core'])}` | {f['impressions']} | "
                     f"{f['clicks']} | {f['position']} | {f['example'][:52]} |")
    else:
        L.append("None.")

    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print, write nothing")
    ap.add_argument("--json", metavar="PATH", help="also write machine-readable JSON")
    ap.add_argument("--window", type=int, default=WINDOW_DAYS, help="window length in days")
    ap.add_argument("--credential", help="service-account JSON path")
    args = ap.parse_args()

    svc = search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client)")
        return 2

    start, end, prior_start, prior_end = windows(dt.date.today(), args.window)
    cur = (start.isoformat(), end.isoformat())
    pre = (prior_start.isoformat(), prior_end.isoformat())

    def totals(rows):
        if not rows:
            return {"clicks": 0, "impressions": 0, "position": 0.0}
        r = rows[0]
        return {"clicks": int(r["clicks"]), "impressions": int(r["impressions"]),
                "position": r["position"]}

    site_cur = totals(fetch(svc, *cur, ""))
    site_pre = totals(fetch(svc, *pre, ""))
    pages_cur = fetch(svc, *cur, "page")
    pages_pre = fetch(svc, *pre, "page")
    queries_cur = fetch(svc, *cur, "query")
    queries_pre = fetch(svc, *pre, "query")

    slug_clusters = load_slug_clusters()
    page_rows = deltas(index_rows(pages_cur), index_rows(pages_pre))
    query_rows = deltas(index_rows(queries_cur), index_rows(queries_pre))

    data = {
        "generated": dt.date.today().isoformat(),
        "window_days": args.window,
        "windows": {"start": cur[0], "end": cur[1],
                    "prior_start": pre[0], "prior_end": pre[1]},
        "totals": site_cur,
        "prior_totals": site_pre,
        "query_floor": {
            "queries": len(queries_cur),
            "impressions": int(sum(r["impressions"] for r in queries_cur)),
            "clicks": int(sum(r["clicks"] for r in queries_cur)),
            "note": "query dimension is a floor; Search Console withholds low-volume queries",
        },
        "clusters": cluster_rollup(pages_cur, slug_clusters),
        "path_split": path_split(pages_cur),
        "page_moves": flagged_moves(page_rows),
        "query_moves": flagged_moves(query_rows),
        "decayed": decaying(page_rows),
        "close": classify_close(queries_cur),
    }

    report = render(data)
    print(report)

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(data, indent=1), encoding="utf-8")

    if args.dry_run:
        return 0

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Search Console report\n\n"
            "Appended by `tools/gsc_report.py`. Movement, decay, and striking distance,\n"
            "per cluster. Search Console lags about three days, so every window ends three\n"
            "days before its date, and every query-dimension figure is a floor rather than\n"
            "a total because low-volume queries are withheld.\n\n"
            "The machine keyword-salad fan-out is separated from human queries by the\n"
            "heuristic documented in the tool's docstring. Families are collapsed and\n"
            "reported, never silently dropped.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
