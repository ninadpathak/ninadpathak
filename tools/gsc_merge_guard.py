#!/usr/bin/env python3
"""First-party Search Console guard for planned page merges.

The cluster-3 consolidation audit proposes twenty merges and one retirement. Those
redirects are irreversible in practice, but the audit's overlap evidence is editorial:
no reproducible instrument checks whether source and target have shared search demand,
whether the source owns demand the target has never shown, or whether Search Console
withholds the queries needed to answer.

This tool does that check without pretending GSC can decide content equivalence:

    tools/gsc_merge_guard.py --dry-run
    tools/gsc_merge_guard.py --json /tmp/merge-guard.json

It reports five merge verdicts:

    shared-named-demand     source and target have ranked for the same named human query
    review-source-demand   source has named human queries not observed on the target
    withheld-source-demand source has impressions but GSC names no human query
    no-human-source-demand source's named rows are only brand, machine fan-out or spam
    no-source-demand-observed
                              no source impressions in the full available history

Retirements use separate `retire-no-demand-observed` / `hold-retirement` verdicts. Exact query
overlap is a lower bound, not semantic equivalence. A missing overlap never becomes
proof of distinct intent because Search Console withholds low-volume queries.

All query-derived counts are FLOORS. Page-dimension impressions and clicks are complete.
Positions are point-in-time, impression-weighted page averages and always print with
their impression denominator; they are not trends and remain sensitive to query mix.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_collapse_forensics as fx  # noqa: E402
import gsc_report as gr  # noqa: E402
import report_log as rl  # noqa: E402

AUDIT = gr.ROOT / "planning" / "cluster-3-consolidation-audit.md"
LOG = gr.ROOT / "planning" / "merge-guard.md"
HISTORY_START = "2025-04-04"
WINDOW_DAYS = 90

MEASURED = "measured"
NO_HUMAN = "no-human-queries"
WITHHELD = "withheld"
NEVER = "never-impressed"

ROW_RE = re.compile(
    r"^\| `(?P<source>[^`]+)` \| [^|]+ \| [^|]+ \| "
    r"`(?P<target>[^`]+)` \| (?P<carry>.+) \|$"
)
def parse_dispositions(text: str) -> list[dict]:
    """Parse only the merge table, not later keep tables or prose examples."""
    marker = "### Merge, 21 pages"
    end_marker = "### Keep but repoint"
    if marker not in text or end_marker not in text:
        return []
    section = text.split(marker, 1)[1].split(end_marker, 1)[0]
    out = []
    for line in section.splitlines():
        match = ROW_RE.match(line)
        if not match:
            continue
        carry = match.group("carry")
        out.append({
            "source": match.group("source"),
            "target": match.group("target"),
            "disposition": "retire" if "RETIRE" in carry.upper() else "merge",
            "carry": carry,
        })
    return out


def load_post_statuses(posts_dir: pathlib.Path = gr.POSTS) -> dict[str, str]:
    """Load every source status so completed batches do not break later pre-merge runs."""
    try:
        import frontmatter
    except ImportError:
        return {}
    statuses = {}
    for path in sorted(posts_dir.glob("*.md")):
        data = frontmatter.load(path)
        slug = str(data.get("slug") or path.stem)
        statuses[slug] = str(data.get("status") or "unknown")
    return statuses


def urls_for(slug: str) -> list[str]:
    return [f"https://ninadpathak.com{prefix}{slug}/"
            for prefix in gr.POST_PATH_PREFIXES]


def combine_queries(rows: list[dict]) -> list[dict]:
    """Combine the same query across canonical and legacy page paths."""
    grouped: dict[str, dict] = {}
    for row in rows:
        query = row["keys"][0]
        bucket = grouped.setdefault(
            query, {"query": query, "impressions": 0.0, "clicks": 0.0,
                    "weighted": 0.0})
        bucket["impressions"] += row["impressions"]
        bucket["clicks"] += row["clicks"]
        bucket["weighted"] += row["position"] * row["impressions"]
    out = []
    for bucket in grouped.values():
        impressions = bucket["impressions"]
        out.append({
            "query": bucket["query"],
            "impressions": int(impressions),
            "clicks": int(bucket["clicks"]),
            "position": (round(bucket["weighted"] / impressions, 1)
                         if impressions else None),
        })
    return sorted(out, key=lambda row: (-row["impressions"], row["query"]))


def fetch_page_queries(svc, start: str, end: str, row_limit: int = 25000) -> list[dict]:
    """Fetch every page+query row; a capped first page must not masquerade as complete."""
    rows = []
    start_row = 0
    while True:
        body = {"startDate": start, "endDate": end,
                "dimensions": ["page", "query"], "rowLimit": row_limit,
                "startRow": start_row}
        batch = svc.searchanalytics().query(siteUrl=gr.SITE, body=body).execute().get(
            "rows", [])
        rows.extend(batch)
        if len(batch) < row_limit:
            return rows
        start_row += row_limit


def collect_period(svc, start: str, end: str) -> dict:
    """Collect complete page totals plus privacy-limited named human query rows."""
    page_rows = gr.fetch(svc, start, end, "page")
    by_page = {row["keys"][0]: row for row in page_rows}

    pq_rows = fetch_page_queries(svc, start, end)

    query_rows = [{"keys": [row["keys"][1]], "page": row["keys"][0],
                   "clicks": row["clicks"], "impressions": row["impressions"],
                   "position": row["position"]} for row in pq_rows]
    parts = gr.partition_queries(query_rows)
    human = [row for row in parts["human"] if not fx.is_foreign(row["page"])]

    human_by_page: dict[str, list[dict]] = collections.defaultdict(list)
    for row in human:
        human_by_page[row["page"]].append(row)

    named_by_page: dict[str, list[dict]] = collections.defaultdict(list)
    for row in pq_rows:
        named_by_page[row["keys"][0]].append(row)

    return {
        "start": start,
        "end": end,
        "page_rows": page_rows,
        "by_page": by_page,
        "human_by_page": dict(human_by_page),
        "named_by_page": dict(named_by_page),
        "pq_rows": pq_rows,
        "excluded": {
            "brand": len(parts["brand"]),
            "blob": len(parts["blob"]),
            "machine": len(parts["machine"]),
            "spam": sum(1 for row in parts["human"] if fx.is_foreign(row["page"])),
        },
    }


def page_stats(slug: str, period: dict) -> dict:
    """Four-state page evidence, preserving withheld versus never impressed."""
    urls = urls_for(slug)
    page_rows = [period["by_page"][url] for url in urls if url in period["by_page"]]
    impressions = sum(row["impressions"] for row in page_rows)
    clicks = sum(row["clicks"] for row in page_rows)
    weighted = sum(row["position"] * row["impressions"] for row in page_rows)
    position = weighted / impressions if impressions else None

    human_rows = [row for url in urls for row in period["human_by_page"].get(url, [])]
    queries = combine_queries(human_rows)
    named_rows = [row for url in urls for row in period["named_by_page"].get(url, [])]

    if queries:
        state = MEASURED
    elif impressions <= 0:
        state = NEVER
    elif named_rows:
        state = NO_HUMAN
    else:
        state = WITHHELD

    return {
        "slug": slug,
        "state": state,
        "impressions": int(impressions),
        "clicks": int(clicks),
        "position": round(position, 1) if position is not None else None,
        "named_query_rows": len(named_rows),
        "human_queries": queries,
        "human_query_count": len(queries),
        "human_impressions": sum(row["impressions"] for row in queries),
    }


def exact_overlap(source: dict, target: dict) -> list[str]:
    source_queries = {row["query"] for row in source["human_queries"]}
    target_queries = {row["query"] for row in target["human_queries"]}
    return sorted(source_queries & target_queries)


def verdict(disposition: str, source: dict, target: dict) -> str:
    """Conservative verdict: missing query rows never prove missing demand."""
    if disposition == "retire":
        return ("retire-no-demand-observed" if source["impressions"] == 0
                else "hold-retirement")
    if exact_overlap(source, target):
        return "shared-named-demand"
    if source["human_queries"]:
        return "review-source-demand"
    if source["state"] == WITHHELD:
        return "withheld-source-demand"
    if source["state"] == NO_HUMAN:
        return "no-human-source-demand"
    return "no-source-demand-observed"


def coverage(period: dict, slugs: set[str] | None = None) -> dict:
    if slugs is None:
        page_rows = period["page_rows"]
        pq_rows = period["pq_rows"]
    else:
        urls = {url for slug in slugs for url in urls_for(slug)}
        page_rows = [row for row in period["page_rows"] if row["keys"][0] in urls]
        pq_rows = [row for row in period["pq_rows"] if row["keys"][0] in urls]
    page_impressions = int(sum(row["impressions"] for row in page_rows))
    pq_impressions = int(sum(row["impressions"] for row in pq_rows))
    return {
        "page_impressions": page_impressions,
        "pq_impressions": pq_impressions,
        "pct": (round(100 * pq_impressions / page_impressions, 1)
                if page_impressions else None),
    }


def position_cell(stats: dict) -> str:
    if stats["position"] is None or stats["impressions"] < 1:
        return "—"
    return f"{stats['position']:.1f} ({stats['impressions']} impr)"


def analyse(dispositions: list[dict], current: dict, history: dict) -> dict:
    pairs = []
    for item in dispositions:
        current_source = page_stats(item["source"], current)
        current_target = page_stats(item["target"], current)
        history_source = page_stats(item["source"], history)
        history_target = page_stats(item["target"], history)
        overlap = exact_overlap(history_source, history_target)
        unshared = [row for row in history_source["human_queries"]
                    if row["query"] not in overlap]
        pairs.append({
            **item,
            "current_source": current_source,
            "current_target": current_target,
            "history_source": history_source,
            "history_target": history_target,
            "exact_overlap": overlap,
            "unshared_source_queries": unshared,
            "verdict": verdict(item["disposition"], history_source, history_target),
        })

    slugs = {item[key] for item in dispositions for key in ("source", "target")}
    return {
        "pairs": pairs,
        "current_coverage": {
            "sitewide": coverage(current),
            "merge_pages": coverage(current, slugs),
        },
        "history_coverage": {
            "sitewide": coverage(history),
            "merge_pages": coverage(history, slugs),
        },
    }


def render(data: dict) -> str:
    lines = [f"\n## {data['generated']} — pre-merge Search Console guard\n"]
    lines.append(
        f"Current window {data['current_window'][0]} to {data['current_window'][1]} "
        f"({data['window_days']}d); history {data['history_window'][0]} to "
        f"{data['history_window'][1]}. Both end {gr.GSC_LAG_DAYS} days back.\n")
    lines.append(
        "**Named queries, human impressions and overlap counts are FLOORS.** Exact shared "
        "queries are positive evidence of overlap; no observed overlap is not evidence of "
        "distinct intent because Search Console withholds low-volume queries. Page impressions "
        "and clicks are complete.\n")

    for label, cov in (("Current sitewide", data["current_coverage"]["sitewide"]),
                       ("Current merge pages", data["current_coverage"]["merge_pages"]),
                       ("Historical sitewide", data["history_coverage"]["sitewide"]),
                       ("Historical merge pages", data["history_coverage"]["merge_pages"])):
        pct = "—" if cov["pct"] is None else f"{cov['pct']}%"
        lines.append(f"- {label} query coverage: {cov['pq_impressions']} of "
                     f"{cov['page_impressions']} page-dimension impressions ({pct}).")

    counts = collections.Counter(pair["verdict"] for pair in data["pairs"])
    lines.append("\n" + ", ".join(f"**{count}** `{name}`"
                                  for name, count in sorted(counts.items())) + ".\n")
    lines.append("| Source → target | Disposition | Execution | Current source | 90d position | "
                 "Historical human queries | Exact shared | Verdict |")
    lines.append("|---|---|---|---|---|---:|---:|---|")
    for pair in data["pairs"]:
        src = pair["current_source"]
        hist = pair["history_source"]
        lines.append(
            f"| `{pair['source']}` → `{pair['target']}` | {pair['disposition']} | "
            f"`{pair['execution_state']}` | "
            f"`{src['state']}`; {src['impressions']} impr | {position_cell(src)} | "
            f"{hist['human_query_count']} | {len(pair['exact_overlap'])} | "
            f"`{pair['verdict']}` |")

    review = [pair for pair in data["pairs"]
              if pair["verdict"] in {"review-source-demand", "shared-named-demand",
                                      "hold-retirement"}]
    lines.append("\n### Named source demand requiring preservation review\n")
    if not review:
        lines.append("None visible. This is not proof that no source demand exists.")
    for pair in review:
        lines.append(f"\n**`{pair['source']}` → `{pair['target']}` — "
                     f"`{pair['verdict']}`**\n")
        if pair["exact_overlap"]:
            lines.append("Exact shared named queries: "
                         + ", ".join(f"`{q}`" for q in pair["exact_overlap"][:10]) + ".")
        queries = pair["unshared_source_queries"][:10]
        if queries:
            lines.append("\n| Source query not observed on target | Impr | Position |")
            lines.append("|---|---:|---:|")
            for row in queries:
                lines.append(f"| {row['query'][:70]} | {row['impressions']} | "
                             f"{row['position'] if row['position'] is not None else '—'} |")

    lines.append("\n### What this guard can and cannot decide\n")
    lines.append("- `shared-named-demand` supports overlap but does not prove two pages should merge.")
    lines.append("- `review-source-demand` means the source owns visible demand not observed on the "
                 "target; the carried prose must answer it before redirecting.")
    lines.append("- `withheld-source-demand` means a position exists but the query is private. It is "
                 "an unknown, never a zero.")
    lines.append("- Exact strings undercount semantic overlap, and page averages move when query mix "
                 "moves. This report does not infer either one.")
    lines.append("- Content equivalence, redirect correctness and carried ideas remain separate gates.")
    return "\n".join(lines) + "\n"


def upsert_dated_report(existing: str, report: str, generated: str) -> str:
    """Keep one authoritative run per date; retries are not independent observations."""
    return rl.upsert_dated_report(existing, report, generated)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--audit", default=str(AUDIT))
    parser.add_argument("--window", type=int, default=WINDOW_DAYS)
    parser.add_argument("--history-start", default=HISTORY_START)
    parser.add_argument("--credential")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", metavar="PATH")
    args = parser.parse_args()

    audit_path = pathlib.Path(args.audit)
    if not audit_path.exists():
        print(f"REFUSING: consolidation audit not found: {audit_path}")
        return 2
    dispositions = parse_dispositions(audit_path.read_text(encoding="utf-8"))
    sources = [item["source"] for item in dispositions]
    if not dispositions or len(sources) != len(set(sources)):
        print("REFUSING: merge dispositions are missing or contain duplicate sources.")
        return 2

    statuses = load_post_statuses()
    unknown = sorted({item[key] for item in dispositions for key in ("source", "target")
                      if item[key] not in statuses})
    if unknown:
        print(f"REFUSING: audit contains unknown slugs: {unknown}")
        return 2
    unpublished_targets = sorted({item["target"] for item in dispositions
                                  if statuses[item["target"]] != "published"})
    if unpublished_targets:
        print(f"REFUSING: merge targets are not published: {unpublished_targets}")
        return 2
    dispositions = [
        {**item, "execution_state": ("pending" if statuses[item["source"]] == "published"
                                     else f"already-{statuses[item['source']]}")}
        for item in dispositions
    ]

    svc = gr.search_console(args.credential)
    if svc is None:
        print("REFUSING: Search Console unavailable. Missing data must not become zero demand.")
        return 2

    end = dt.date.today() - dt.timedelta(days=gr.GSC_LAG_DAYS)
    current_start = end - dt.timedelta(days=args.window - 1)
    current = collect_period(svc, current_start.isoformat(), end.isoformat())
    history = collect_period(svc, args.history_start, end.isoformat())
    result = analyse(dispositions, current, history)
    result.update({
        "generated": dt.date.today().isoformat(),
        "window_days": args.window,
        "current_window": [current_start.isoformat(), end.isoformat()],
        "history_window": [args.history_start, end.isoformat()],
        "excluded": {"current": current["excluded"], "history": history["excluded"]},
    })

    report = render(result)
    print(report)
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(result, indent=1), encoding="utf-8")
    if args.dry_run:
        return 0

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Pre-merge Search Console guard\n\n"
            "Maintained by `tools/gsc_merge_guard.py`, one authoritative section per date. "
            "It tests whether planned merge sources and\n"
            "targets share named first-party search demand, while preserving withheld demand as\n"
            "unknown. It does not decide content equivalence.\n",
            encoding="utf-8")
    LOG.write_text(
        upsert_dated_report(LOG.read_text(encoding="utf-8"), report,
                            result["generated"]),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
