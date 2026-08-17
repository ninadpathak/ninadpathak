#!/usr/bin/env python3
"""Quantify machine query fan-out sitewide, and report a human-only monthly baseline.

Built because every impression figure this campaign has reported is contaminated by
traffic with no person behind it, and until now the contamination rate was only known
inside positions 4-30, where it was 28 of 46 queries. This measures it across the full
history and produces the series the campaign should have been tracking from day one.

Uses the same classifier as tools/gsc_report.py - `partition_queries` - so the two
tools can never disagree about what counts as a person.

    tools/gsc_human_baseline.py                  # report, write planning/gsc-human-baseline.md
    tools/gsc_human_baseline.py --dry-run        # print, write nothing
    tools/gsc_human_baseline.py --json out.json

WHAT THIS CAN AND CANNOT SAY - read before quoting a percentage
---------------------------------------------------------------
Search Console withholds low-volume queries, so the query dimension does not sum to the
sitewide total. That is not a rounding gap here; it is most of the data. Consequently:

  * A machine share can only be measured WITHIN the named-query subset. That is the
    honest denominator and every percentage below uses it.
  * The sitewide machine share is therefore a RANGE, not a number. Its lower bound
    assumes every withheld impression is human; its upper bound assumes every withheld
    impression is machine. Both bounds are reported. Neither is a point estimate, and
    quoting the midpoint as one would be inventing data.
  * The human-only series is likewise a floor on human traffic, for the same reason:
    withheld queries are excluded from it entirely and some of them are certainly human.

The fan-out model is built once over the union of every query seen across the whole span
rather than per month, because family detection needs MIN_FAMILY_SIZE variants to see a
family at all. A month containing only two members of a known fan-out would otherwise
score them as human.

Its limits are those of the separator itself, documented in gsc_report.py: token-set
clustering is order-blind by design, a genuine topic with many close human variants
would cluster too, and fan-out built from wholly novel vocabulary each time would not
cluster at all. The stopword ratio is reported as a weak corroborating signal and
excludes nothing.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402
import report_log as rl  # noqa: E402

ROOT = gr.ROOT
LOG = ROOT / "planning" / "gsc-human-baseline.md"
# Search Console keeps roughly 16 months. Start before the site's first recorded day so
# nothing is clipped, and let the API return what it has.
HISTORY_START = dt.date(2025, 1, 1)


def month_windows(start: dt.date, end: dt.date) -> list[tuple[str, dt.date, dt.date]]:
    """Calendar months covering start..end, clipped to that span at both ends."""
    out = []
    cursor = dt.date(start.year, start.month, 1)
    while cursor <= end:
        last = dt.date(cursor.year, cursor.month,
                       calendar.monthrange(cursor.year, cursor.month)[1])
        out.append((cursor.strftime("%Y-%m"), max(cursor, start), min(last, end)))
        cursor = last + dt.timedelta(days=1)
    return out


def collect(svc, months: list[tuple[str, dt.date, dt.date]]) -> dict:
    """Sitewide totals and query rows for each month."""
    data = {}
    for label, start, end in months:
        s, e = start.isoformat(), end.isoformat()
        site = gr.fetch(svc, s, e, "")
        queries = gr.fetch(svc, s, e, "query")
        if not site and not queries:
            continue
        totals = ({"clicks": int(site[0]["clicks"]),
                   "impressions": int(site[0]["impressions"]),
                   "position": round(site[0]["position"], 1)} if site else
                  {"clicks": 0, "impressions": 0, "position": None})
        data[label] = {"start": s, "end": e, "site": totals, "queries": queries}
    return data


def build(data: dict) -> dict:
    """Classify every month against one fan-out model built over the whole span."""
    everything = [r for m in data.values() for r in m["queries"]]
    model = gr.partition_queries(everything)
    machine_queries = {r["keys"][0] for r in model["machine"]}
    families = gr.describe_families(model["families"], gr.index_rows(model["machine"]))

    months = []
    for label in sorted(data):
        m = data[label]
        parts = gr.partition_queries(m["queries"], machine_queries=machine_queries)
        named = gr.summarise(m["queries"])
        row = {
            "month": label, "start": m["start"], "end": m["end"],
            "site": m["site"], "named": named,
            "human": gr.summarise(parts["human"]),
            "machine": gr.summarise(parts["machine"]),
            "brand": gr.summarise(parts["brand"]),
            "blob": gr.summarise(parts["blob"]),
        }
        row["withheld_impressions"] = max(0, m["site"]["impressions"] - named["impressions"])
        row["withheld_clicks"] = max(0, m["site"]["clicks"] - named["clicks"])
        months.append(row)

    def total(key):
        return {
            "clicks": sum(m[key]["clicks"] for m in months),
            "impressions": sum(m[key]["impressions"] for m in months),
            "queries": sum(m[key]["queries"] for m in months),
        }

    site_impr = sum(m["site"]["impressions"] for m in months)
    site_clicks = sum(m["site"]["clicks"] for m in months)
    named_t, machine_t = total("named"), total("machine")
    human_t, brand_t, blob_t = total("human"), total("brand"), total("blob")
    withheld_impr = max(0, site_impr - named_t["impressions"])
    withheld_clicks = max(0, site_clicks - named_t["clicks"])

    def pct(a, b):
        return round(100 * a / b, 1) if b else None

    return {
        "generated": dt.date.today().isoformat(),
        "span": {"start": months[0]["start"], "end": months[-1]["end"]} if months else {},
        "months": months,
        "families": families,
        "totals": {
            "site": {"clicks": site_clicks, "impressions": site_impr},
            "named": named_t, "human": human_t, "machine": machine_t,
            "brand": brand_t, "blob": blob_t,
            "withheld": {"impressions": withheld_impr, "clicks": withheld_clicks},
        },
        "shares": {
            # Honest denominator: the named-query subset.
            "named_coverage_impressions": pct(named_t["impressions"], site_impr),
            "named_coverage_clicks": pct(named_t["clicks"], site_clicks),
            "machine_of_named_impressions": pct(machine_t["impressions"], named_t["impressions"]),
            "machine_of_named_clicks": pct(machine_t["clicks"], named_t["clicks"]),
            "human_of_named_impressions": pct(human_t["impressions"], named_t["impressions"]),
            # Sitewide is a range, never a point estimate.
            "machine_of_site_lower": pct(machine_t["impressions"], site_impr),
            "machine_of_site_upper": pct(machine_t["impressions"] + withheld_impr, site_impr),
        },
    }


def render(d: dict) -> str:
    s, t, sh = d["span"], d["totals"], d["shares"]
    L: list[str] = []
    L.append(f"\n## {d['generated']} — machine fan-out share and human-only baseline\n")
    L.append(f"Span {s.get('start')} to {s.get('end')}. Classifier shared with "
             f"`tools/gsc_report.py`; fan-out model built once over every query in the "
             f"span, because family detection needs {gr.MIN_FAMILY_SIZE} variants to see "
             f"a family at all.\n")

    L.append("### The denominator problem, first\n")
    L.append(f"Sitewide: **{t['site']['clicks']} clicks / {t['site']['impressions']} "
             f"impressions**. Named queries account for {t['named']['clicks']} clicks and "
             f"{t['named']['impressions']} impressions — "
             f"**{sh['named_coverage_impressions']}% of sitewide impressions**. Search "
             f"Console withholds the rest, so:\n")
    L.append(f"- Every share below is measured **within the named-query subset**, which is "
             f"the only denominator that exists.")
    L.append(f"- The sitewide machine share is a **range**: "
             f"**{sh['machine_of_site_lower']}% to {sh['machine_of_site_upper']}%** of all "
             f"impressions. Lower bound assumes every withheld impression is human, upper "
             f"assumes every one is machine. There is no point estimate and the midpoint "
             f"is not one.\n")

    L.append("### Composition of named queries, whole span\n")
    L.append("| Bucket | Queries | Clicks | Impressions | Share of named impressions |")
    L.append("|---|---:|---:|---:|---:|")
    for key, label in (("human", "Human"), ("machine", "Machine fan-out"),
                       ("brand", "Brand"), ("blob", "Pasted blob")):
        b = t[key]
        share = (round(100 * b["impressions"] / t["named"]["impressions"], 1)
                 if t["named"]["impressions"] else 0)
        L.append(f"| {label} | {b['queries']} | {b['clicks']} | {b['impressions']} | {share}% |")
    L.append(f"| **Named total** | {t['named']['queries']} | {t['named']['clicks']} | "
             f"{t['named']['impressions']} | 100% |")
    L.append(f"| *Withheld by Search Console* | — | {t['withheld']['clicks']} | "
             f"{t['withheld']['impressions']} | *unclassifiable* |")

    L.append("\n### Human-only monthly baseline\n")
    L.append("Human clicks, impressions and impression-weighted position, with fan-out, "
             "brand and blobs removed. A **floor** on human traffic: withheld queries are "
             "excluded entirely and some of them are certainly human.\n")
    L.append("| Month | Site impr | Named impr | Human impr | Human clicks | Human pos | "
             "Machine impr | Machine % of named |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for m in d["months"]:
        named_impr = m["named"]["impressions"]
        mshare = round(100 * m["machine"]["impressions"] / named_impr, 1) if named_impr else 0
        pos = m["human"]["position"] if m["human"]["position"] is not None else "—"
        L.append(f"| {m['month']} | {m['site']['impressions']} | {named_impr} | "
                 f"{m['human']['impressions']} | {m['human']['clicks']} | {pos} | "
                 f"{m['machine']['impressions']} | {mshare}% |")

    L.append("\n### Fan-out families found\n")
    L.append("Collapsed, not dropped. A genuine topic with many close human variants "
             "would cluster here too, so read this list rather than trusting the split "
             "blindly.\n")
    if d["families"]:
        L.append("| Variants | Shared core | Impressions | Clicks | Avg pos | Example |")
        L.append("|---:|---|---:|---:|---:|---|")
        for f in d["families"]:
            L.append(f"| {f['variants']} | `{' '.join(f['core'])}` | {f['impressions']} | "
                     f"{f['clicks']} | {f['position']} | {f['example'][:48]} |")
    else:
        L.append("None.")

    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", metavar="PATH")
    ap.add_argument("--credential")
    args = ap.parse_args()

    svc = gr.search_console(args.credential)
    if svc is None:
        print("Search Console UNAVAILABLE (missing credential or google-api-python-client)")
        return 2

    end = dt.date.today() - dt.timedelta(days=gr.GSC_LAG_DAYS)
    data = collect(svc, month_windows(HISTORY_START, end))
    if not data:
        print("no Search Console data in range")
        return 1

    result = build(data)
    report = render(result)
    print(report)

    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(result, indent=1), encoding="utf-8")
    if args.dry_run:
        return 0

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# Human-only Search Console baseline\n\n"
            "Maintained by `tools/gsc_human_baseline.py`, one authoritative section per "
            "date. Separates machine query fan-out\n"
            "from people and reports the human-only series monthly. Read the denominator\n"
            "note in each run: shares are measured within the named-query subset, the\n"
            "sitewide machine share is a range rather than a number, and the human series\n"
            "is a floor because Search Console withholds low-volume queries.\n",
            encoding="utf-8")
    LOG.write_text(
        rl.upsert_dated_report(LOG.read_text(encoding="utf-8"), report,
                               data["generated"]),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
