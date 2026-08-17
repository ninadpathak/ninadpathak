#!/usr/bin/env python3
"""Diagnose a traffic collapse from Search Console alone: step or slope, and what broke.

Written to answer one question — when did the autumn 2025 collapse start and why — and
kept because the method is reusable. Point it at any window and it decomposes the drop
the four ways that distinguish the causes:

    STEP OR SLOPE   week-level series plus the largest week-over-week fall. A step on a
                    single date points at an event; a slope points at decay.
    PAGE            did everything fall together, or a specific set while others held?
                    A sitewide drop and a page-set drop have different causes.
    QUERY           did queries lose volume, or did the site lose position on queries
                    that kept it? Demand collapse and ranking loss need opposite fixes.
    DEVICE/COUNTRY  a break in one and not the other is usually technical.

It also flags URL paths that belong to no version of the site, which is what actually
settled the 2025 question: 398 `/products/<numeric-id>` pages appeared on the domain in
September 2025 ranking for Japanese counterfeit-goods queries.

    tools/gsc_collapse_forensics.py                          # the 2025 window
    tools/gsc_collapse_forensics.py --start 2026-01-01 --end 2026-06-30
    tools/gsc_collapse_forensics.py --dry-run

WHAT THIS CANNOT DO, stated because the temptation is to over-read it
---------------------------------------------------------------------
Search Console's Search Analytics API reports impressions, clicks and position. It does
NOT expose manual actions, security issues, or algorithm updates. So:

  * A demotion and a deindexing look similar here. Both reduce impressions.
  * Co-timing is not causation. Two things starting in the same week is strong evidence
    and still not proof, and the wording in the report reflects that.
  * The Manual Actions and Security Issues reports in the Search Console UI are the only
    thing that settles whether a penalty was applied. This tool says so rather than
    guessing.

Needs GOOGLE_APPLICATION_CREDENTIALS or the workspace service-account file.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import pathlib
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402

LOG = gr.ROOT / "planning" / "gsc-collapse-forensics.md"

# Path segments this site has legitimately used across all of its incarnations. Anything
# else receiving impressions did not come from Ninad. `/category/` is on the list because
# the pre-2026 site genuinely had category pages - it was a false positive in the first
# pass of this analysis and cost about a dozen impressions of accuracy before being caught.
KNOWN_SECTIONS = {
    "(root)", "articles", "blog", "glossary", "about", "contact", "work", "portfolio",
    "projects", "static", "terms", "topics", "linter", "llms-txt-generator", "guides",
    "essays", "marketing-research", "customers", "process", "category", "ai-engineering",
    "ai-agent-architecture", "ai-agent-memory", "ai-workflows", "technical-writing",
    "rag", "ai-crawler-checker", "ai-overviews-checker", "llms-txt-validator",
    "developer-experience", "technical-documentation", "reddit-marketing",
    "community-building", "technical-events", "ai-search-optimization",
    "distribution",
    # Pre-2026 site sections, all confirmed legitimate by inspection. Each of these was
    # a false positive in an earlier pass of this analysis: `/category/`, `/tags/`,
    # `/productivity/` and `/project/` are the old blog's own taxonomy and content.
    "tags", "productivity", "project",
}


def section(url: str) -> str:
    parts = [p for p in urlsplit(url).path.split("/") if p]
    return parts[0] if parts else "(root)"


def is_post_slug(url: str) -> bool:
    """A single hyphenated path segment, which is how the old site served root-level posts.

    `/todoist-vs-any-do/` and `/wordpress-6-7-rollins/` are real posts. The injected spam
    used either a bare word (`/hg/`, `/pw/`, `/jukyuban/`) or a numeric child
    (`/products/12201711`), so requiring a hyphen separates them without an explicit list.
    """
    parts = [p for p in urlsplit(url).path.split("/") if p]
    return len(parts) == 1 and "-" in parts[0] and not parts[0].isdigit()


def is_foreign(url: str) -> bool:
    """A path belonging to no version of this site.

    Deliberately an allowlist rather than a blocklist of known spam: the point is to catch
    the *next* injection, whose paths nobody can predict. The cost is that a genuinely new
    legitimate section reads as foreign until it is added here, which is a one-line fix and
    a far cheaper failure than missing an injection for ten months.
    """
    if is_post_slug(url):
        return False
    return section(url) not in KNOWN_SECTIONS


def weekly(svc, start: dt.date, end: dt.date) -> list[dict]:
    """Week buckets with the legitimate and foreign split, and the page counts."""
    out = []
    cursor = start
    while cursor <= end:
        stop = min(cursor + dt.timedelta(days=6), end)
        rows = gr.fetch(svc, cursor.isoformat(), stop.isoformat(), "page")
        legit = [r for r in rows if not is_foreign(r["keys"][0])]
        foreign = [r for r in rows if is_foreign(r["keys"][0])]
        out.append({
            "week": cursor.isoformat(), "end": stop.isoformat(),
            "legit_impressions": int(sum(r["impressions"] for r in legit)),
            "legit_pages": len(legit),
            "foreign_impressions": int(sum(r["impressions"] for r in foreign)),
            "foreign_pages": len(foreign),
            "foreign_examples": sorted(
                (urlsplit(r["keys"][0]).path for r in
                 sorted(foreign, key=lambda r: -r["impressions"])[:3])),
        })
        cursor = stop + dt.timedelta(days=1)
    return out


def largest_step(series: list[dict], key: str = "legit_impressions") -> dict:
    """Largest week-over-week fall, by absolute loss and by proportion.

    Both are reported because they answer different questions and can disagree sharply.
    On the 2025 data the proportional winner was 56 -> 8 impressions, an 86% fall that
    matters to nobody, while the absolute winner was 777 -> 253, which is the event. Rank
    by absolute loss when looking for where traffic went; use the proportional figure to
    judge whether a fall was a step or a wobble.
    """
    steps = []
    for a, b in zip(series, series[1:]):
        loss = a[key] - b[key]
        steps.append({"from_week": a["week"], "to_week": b["week"],
                      "before": a[key], "after": b[key], "loss": loss,
                      "drop_share": round(loss / a[key], 3) if a[key] else None})
    falls = [s for s in steps if s["loss"] > 0]
    by_absolute = max(falls, key=lambda s: s["loss"], default=None)
    material = [s for s in falls if s["before"] >= 20]
    by_share = max(material, key=lambda s: s["drop_share"], default=None)
    return {"by_absolute_loss": by_absolute, "by_proportion": by_share}


def decompose(svc, before: tuple[str, str], after: tuple[str, str]) -> dict:
    """Page, query, device and country comparison across the break."""
    def idx(dim, window):
        return {r["keys"][0]: r for r in gr.fetch(svc, *window, dim)}

    pb, pa = idx("page", before), idx("page", after)
    qb, qa = idx("query", before), idx("query", after)

    held_pages = [k for k in pb if k in pa]
    lost_pages = [k for k in pb if k not in pa]
    both_q = [k for k in qb if k in qa]
    gone_q = [k for k in qb if k not in qa]

    def band(p):
        return ("1-10" if p <= 10 else "11-20" if p <= 20 else "21-30" if p <= 30
                else "31-50" if p <= 50 else "51+")

    gone_bands = collections.Counter()
    for k in gone_q:
        gone_bands[band(qb[k]["position"])] += qb[k]["impressions"]

    moved = []
    for k in both_q:
        moved.append({"query": k, "impressions_before": int(qb[k]["impressions"]),
                      "impressions_after": int(qa[k]["impressions"]),
                      "position_before": round(qb[k]["position"], 1),
                      "position_after": round(qa[k]["position"], 1)})

    out = {
        "pages": {
            "before": len(pb), "after": len(pa),
            "held": len(held_pages), "vanished": len(lost_pages),
            "impressions_on_vanished": int(sum(pb[k]["impressions"] for k in lost_pages)),
            "impressions_on_held_before": int(sum(pb[k]["impressions"] for k in held_pages)),
            "biggest_losses": [
                {"path": urlsplit(k).path,
                 "before": int(pb[k]["impressions"]),
                 "position_before": round(pb[k]["position"], 1),
                 "after": int(pa[k]["impressions"]) if k in pa else 0,
                 "gone": k not in pa}
                for k in sorted(pb, key=lambda k: -pb[k]["impressions"])[:12]],
        },
        "queries": {
            "before": len(qb), "after": len(qa), "in_both": len(both_q),
            "impressions_on_vanished": int(sum(qb[k]["impressions"] for k in gone_q)),
            "impressions_on_survivors_before": int(sum(qb[k]["impressions"] for k in both_q)),
            "vanished_by_position_band": {b: int(gone_bands[b]) for b in
                                          ("1-10", "11-20", "21-30", "31-50", "51+")},
            "survivors": sorted(moved, key=lambda m: -m["impressions_before"])[:12],
        },
    }
    for dim in ("device", "country"):
        out[dim] = {}
        for label, window in (("before", before), ("after", after)):
            rows = sorted(gr.fetch(svc, *window, dim), key=lambda r: -r["impressions"])
            out[dim][label] = [{"key": r["keys"][0], "impressions": int(r["impressions"]),
                                "position": round(r["position"], 1)} for r in rows[:6]]
    return out


def render(d: dict) -> str:
    L = [f"\n## {d['generated']} — collapse forensics, {d['scan']['start']} to "
         f"{d['scan']['end']}\n"]
    absolute = d["step"]["by_absolute_loss"]
    share = d["step"]["by_proportion"]
    if absolute:
        L.append(f"**Largest weekly fall by volume:** week of {absolute['from_week']} to "
                 f"{absolute['to_week']}, legitimate impressions {absolute['before']} -> "
                 f"{absolute['after']}, a loss of {absolute['loss']} "
                 f"({100*absolute['drop_share']:.0f}%). This is the event.\n")
    if share and absolute and share["from_week"] != absolute["from_week"]:
        L.append(f"The steepest *proportional* fall was a different week — "
                 f"{share['from_week']} to {share['to_week']}, {share['before']} -> "
                 f"{share['after']} ({100*share['drop_share']:.0f}%) — which is the tail "
                 f"of the same decline and not a second event. Ranking by proportion "
                 f"alone would have pointed at the wrong week.\n")
    L.append("### Weekly series, legitimate against foreign URLs\n")
    L.append("| Week | Legit impr | Legit pages | Foreign impr | Foreign pages |")
    L.append("|---|---:|---:|---:|---:|")
    for w in d["weekly"]:
        L.append(f"| {w['week']} | {w['legit_impressions']} | {w['legit_pages']} | "
                 f"{w['foreign_impressions']} | {w['foreign_pages']} |")

    p, q = d["decomposition"]["pages"], d["decomposition"]["queries"]
    L.append(f"\n### Pages\n")
    L.append(f"{p['before']} pages before, {p['after']} after. {p['held']} survived, "
             f"{p['vanished']} vanished, carrying {p['impressions_on_vanished']} "
             f"impressions.\n")
    L.append("| Page | Before | Pos | After |")
    L.append("|---|---:|---:|---:|")
    for r in p["biggest_losses"]:
        L.append(f"| {r['path'][:52]} | {r['before']} | {r['position_before']} | "
                 f"{'GONE' if r['gone'] else r['after']} |")

    L.append(f"\n### Queries\n")
    L.append(f"{q['before']} before, {q['after']} after, **{q['in_both']} in both**. "
             f"{q['impressions_on_vanished']} impressions sat on queries that stopped "
             f"appearing entirely.\n")
    L.append("Position band of the vanished impressions, before the fall:\n")
    L.append("| Band | Impressions |")
    L.append("|---|---:|")
    for b, v in q["vanished_by_position_band"].items():
        L.append(f"| {b} | {v} |")
    if q["survivors"]:
        L.append("\n| Surviving query | Impr before | after | Pos before | after |")
        L.append("|---|---:|---:|---:|---:|")
        for m in q["survivors"]:
            L.append(f"| {m['query'][:44]} | {m['impressions_before']} | "
                     f"{m['impressions_after']} | {m['position_before']} | "
                     f"{m['position_after']} |")

    for dim in ("device", "country"):
        L.append(f"\n### {dim.title()}\n")
        for label in ("before", "after"):
            parts = ", ".join(f"{r['key']}={r['impressions']}@{r['position']:.0f}"
                              for r in d["decomposition"][dim][label])
            L.append(f"- **{label}**: {parts}")

    L.append("\n### What this cannot settle\n")
    L.append("Search Analytics reports impressions, clicks and position only. It cannot "
             "see manual actions, security issues, or algorithm updates, so a demotion "
             "and a deindexing look alike here and co-timing is not causation. The "
             "Manual Actions and Security Issues reports in the Search Console UI are "
             "the only thing that settles whether a penalty was applied.")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default="2025-08-04")
    ap.add_argument("--end", default="2025-12-28")
    ap.add_argument("--before", nargs=2, metavar=("FROM", "TO"),
                    default=["2025-08-09", "2025-09-05"])
    ap.add_argument("--after", nargs=2, metavar=("FROM", "TO"),
                    default=["2025-10-13", "2025-11-09"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--credential")
    args = ap.parse_args()

    svc = gr.search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client)")
        return 2

    series = weekly(svc, dt.date.fromisoformat(args.start), dt.date.fromisoformat(args.end))
    data = {
        "generated": dt.date.today().isoformat(),
        "scan": {"start": args.start, "end": args.end},
        "windows": {"before": args.before, "after": args.after},
        "weekly": series,
        "step": largest_step(series),
        "decomposition": decompose(svc, tuple(args.before), tuple(args.after)),
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
            "# Collapse forensics\n\n"
            "Appended by `tools/gsc_collapse_forensics.py`. Decomposes a traffic drop into\n"
            "step-or-slope, page, query, device and country, and flags URL paths belonging\n"
            "to no version of the site. Search Analytics cannot see manual actions,\n"
            "security issues, or algorithm updates, so causes are named as inferences.\n",
            encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
