#!/usr/bin/env python3
"""Clean the raw cluster pulls into a single deduped addressable universe.

Ahrefs `terms` mode matches on token presence, not meaning, so several clusters
came back carrying large off-niche industries that happen to share vocabulary:
HOA/property "community management", "online community college", the TV show
Community, corporate party planning, and navigational university hackathons.
Counting those would inflate the addressable universe.

Rules are explicit and auditable. Each cluster has BLOCK patterns (drop on match)
and, where the vocabulary is genuinely ambiguous, REQUIRE patterns (keep only on
match). Drop counts are reported so the cleaning is inspectable.

Output: DERIVED-full-universe.json + a printed summary.
"""
import json
import os
import re

CACHE = os.path.dirname(os.path.abspath(__file__))

# Cluster 1 is the banked documentation pull, already cleaned by the prior pass.
CLUSTERS = {
    1: ("Technical documentation & docs ops", ["DERIVED-clean-universe.json"]),
    2: ("Developer experience & DevRel", ["B1-devex-devrel.json"]),
    3: ("AI agents, memory, RAG, inference", ["B2-ai-agents-memory.json", "B3-rag-inference.json"]),
    4: ("AI Overviews & AI-search citation", ["B4-ai-overviews-geo.json"]),
    5: ("Reddit marketing", ["B5-reddit-marketing.json"]),
    6: ("Forums & community building", ["B6-community-forums.json"]),
    7: ("Technical & community events", ["B7-events.json"]),
}

BLOCK = {
    # Cluster 1 arrives pre-banked but is NOT clean: the prior pass left a large
    # body of nursing / medical charting keywords ("picc line documentation
    # example") and one junk 3,000-vol term. Those are a different profession.
    1: [r"\btest\.com\b",
        r"head to toe", r"unwitnessed fall", r"\biv site\b", r"physical exam",
        r"physical assessment", r"respiratory documentation", r"\bmar documentation\b",
        r"picc line", r"\bwound\b", r"skin tear", r"urinary catheter", r"\bcatheter\b",
        r"neurological", r"soap note", r"soap documentation", r"restraint",
        r"review of systems", r"musculoskeletal", r"perrla", r"blood draw",
        r"\bnursing\b", r"\bnurse\b", r"\bpatient\b", r"clinical documentation",
        r"medication", r"vital signs", r"\bcharting\b", r"meat documentation",
        r"wound dressing", r"assessment documentation"],
    2: [r"\bjobs?\b", r"salary", r"resume"],
    3: [r"\bnews\b", r"\bstock\b", r"\bprice\b", r"paper 2020", r"lewis et al",
        r"\bjobs?\b", r"salary", r"\bcourse\b", r"certification",
        # design assets and scraped junk, not subject-matter queries
        r"\bicon\b", r"\blogo\b", r"gpt4 can train",
        r"intercom fin ai agent features",
        # vendor procurement Ninad does not sell (same rule applied to cluster 7 AV)
        r"ai agent development (company|services|agency|companies)",
        r"ai agent (company|companies|agency|vendors?)"],
    4: [r"\bjobs?\b", r"salary"],
    5: [r"report a subreddit", r"\bnsfw\b", r"porn", r"\bgone wild\b", r"drama",
        r"\bbanned\b", r"delete", r"\bkarma bot\b", r"how to report",
        r"\bjobs?\b", r"salary", r"onlyfans", r"hentai", r"\bincel\b",
        r"\bpiracy\b", r"benadryl", r"\bblock a subreddit\b"],
    6: [  # HOA / property management industry
        r"\bhoa\b", r"association management", r"property management",
        r"resident portal", r"community management (inc|corporation|llc|corp)\b",
        r"community management (companies|near me|jobs|login)",
        r"(asset|investment|case|care|health) management",
        # education
        r"community college", r"colleges", r"classroom", r"student", r"teacher",
        r"elementary", r"adjunct", r"\bdegree", r"\bcampus\b", r"physics",
        r"calculus", r"online class", r"online course", r"\bcourses\b",
        # court-ordered community service
        r"community service", r"court",
        # banking
        r"credit union", r"\bbank\b", r"banking",
        # the TV show, and other homographs
        r"watch community", r"community goods", r"boat building",
        r"metal community building", r"community center building",
        r"community use building", r"path of building", r"\bmadden\b",
        r"tolarian", r"quickbooks", r"\bapc network\b", r"community health",
        r"\bnursing\b", r"\brn community\b", r"community action",
        r"community first", r"community bank", r"lawrence ks", r"williamsburg",
        r"\bjobs?\b", r"salary", r"community boat",
        # market-research online communities (MROC) are a separate B2B industry
        r"market research online community", r"online panel community",
        r"online community research", r"online research community",
    ],
    7: [  # consumer / corporate party planning, not technical-community events
        r"chocolate", r"cooking", r"magician", r"christmas", r"mother's day",
        r"fundraising", r"alumni", r"\bswag\b", r"\bbags\b", r"\bgifts\b",
        r"virtual event games", r"team event", r"\bkids\b", r"families",
        r"nonprofit", r"\bhiring\b", r"credit", r"tasting",
        # navigational university / vendor hackathons
        r"\b(mit|stanford|nyu|harvard|columbia|berkeley|cmu|purdue|ucla|princeton)\b",
        r"georgia tech", r"smart india", r"\buidai\b", r"\bmlh\b", r"\bsas\b",
        r"\broblox\b", r"\byahoo\b", r"\bsolana\b", r"open ai hackathon",
        r"\b(google|microsoft|aws|anthropic) hackathon\b",
        r"hackathon (nyc|san francisco|sf|boston|atlanta|bay area|2024|2023)",
        r"worldwide developer conference", r"web developer conference \d",
        r"hackathon (team names|winners|prizes|judge)",
        r"furniture and things", r"mercer island", r"community event center",
        r"\bjobs?\b", r"salary", r"\bflyer\b",
        # AV/production vendor procurement — a corporate-events industry Ninad
        # cannot serve or monetise, even though he could rank for it
        r"virtual event (production|producer|agency|consultant|rfp)",
        r"virtual event (compan|service|provider|solution)",
    ],
}

# Where vocabulary is ambiguous, require an on-niche anchor as well.
REQUIRE = {
    # "<topic> subreddit" (nfl, anime, politics...) is consumer navigation, not
    # Reddit marketing. Ahrefs' traffic_potential made these look enormous
    # because the #1 ranking page is reddit.com itself.
    5: [r"reddit (ads?|advertis|marketing|seo|growth|promot|strateg|agency|business|"
        r"traffic|engagement|karma|analytics|campaign)",
        r"(marketing|advertis|promot|seo|growth) on reddit",
        r"ads? on reddit", r"ads reddit", r"seo reddit", r"affiliate marketing reddit",
        r"how to (make|create|start|grow|moderate|run|manage) an? subreddit",
        r"(create|creating) (a )?subreddit", r"^subreddit$", r"^reddit subreddit$",
        r"what is (a )?subreddit", r"subreddit (meaning|list|finder|search|stats|viewer|discovery)",
        r"how to search within a subreddit", r"similar subreddit",
        r"reddit for (business|marketing|b2b)", r"progressive growth reddit",
        r"reddit progressive growth"],
    6: [r"online community", r"community building", r"build\w* (an? )?(online |discord )?community",
        r"community platform", r"community engagement", r"community manager",
        r"community management (software|tools?|platform|strategy|best practices|services?|app|system|agency|social media)",
        r"social media community", r"forum software", r"discord community",
        r"grow\w* (an? )?(online )?community", r"community strategy",
        r"what is (an? )?(online )?community", r"^community management$",
        r"creating an online community", r"online (writing|learning|gaming|health|fitness|trading|artistic|marketing) community",
        r"circle online community"],
}

# "<FirmName> community management" is the HOA/property industry, not audience work.
# Only these modifiers make the phrase on-niche.
OK_MOD = {"online", "social", "social media", "media", "digital", "brand", "discord",
          "telegram", "crypto", "cryptocurrency", "best", "best online", "what is",
          "what is a", "professional", "b2b", "developer", "product"}
PREFIXED = re.compile(r"^(.*?)\s+community\s+(management|building)$", re.I)


def prefix_guard(keyword):
    """Drop '<proper noun> community management/building' — HOA firms, place names."""
    m = PREFIXED.match(keyword.strip())
    if not m:
        return True
    return m.group(1).strip().lower() in OK_MOD

TOOL_JOB = re.compile(
    r"\b(checker|check|validator|validate|generator|generate|calculator|calculate|"
    r"analyzer|analyse|analyzer|converter|convert|linter|lint|scanner|audit|"
    r"tester|template|tools?)\b", re.I)
CALC_JOB = re.compile(r"\b(calculator|calculate|roi|metrics|kpis?|statistics|budget|pricing|cost)\b", re.I)


def load(fn):
    return json.load(open(os.path.join(CACHE, fn)))


def clean(cid, rows):
    blocks = [re.compile(p, re.I) for p in BLOCK.get(cid, [])]
    reqs = [re.compile(p, re.I) for p in REQUIRE.get(cid, [])]
    kept, dropped = [], []
    for r in rows:
        k = r["keyword"]
        if any(b.search(k) for b in blocks):
            dropped.append(r); continue
        if reqs and not any(q.search(k) for q in reqs):
            dropped.append(r); continue
        if cid == 6 and not prefix_guard(k):
            dropped.append(r); continue
        kept.append(r)
    return kept, dropped


def main():
    universe, seen = [], {}
    print(f"{'#':>2} {'cluster':38} {'raw':>5} {'kept':>5} {'dropped':>7} {'gross_vol':>9} {'clean_vol':>9}")
    per_cluster = {}
    for cid, (name, files) in CLUSTERS.items():
        raw = []
        for f in files:
            raw.extend(load(f))
        # dedupe within cluster
        byk = {}
        for r in raw:
            if r["keyword"] not in byk or (r.get("volume") or 0) > (byk[r["keyword"]].get("volume") or 0):
                byk[r["keyword"]] = r
        raw = list(byk.values())
        kept, dropped = clean(cid, raw)
        gross = sum(r.get("volume") or 0 for r in raw)
        cl = sum(r.get("volume") or 0 for r in kept)
        print(f"{cid:>2} {name:38} {len(raw):>5} {len(kept):>5} {len(dropped):>7} {gross:>9} {cl:>9}")
        per_cluster[cid] = {"name": name, "raw": len(raw), "kept": kept, "dropped": dropped,
                            "gross_vol": gross}

    # Cross-cluster dedupe: first cluster to claim a keyword owns it
    # (charter rule: every piece belongs to exactly one cluster).
    print("\ncross-cluster dedupe:")
    for cid in sorted(per_cluster):
        c = per_cluster[cid]
        uniq = []
        for r in c["kept"]:
            k = r["keyword"].lower().strip()
            if k in seen:
                continue
            seen[k] = cid
            rr = dict(r); rr["cluster"] = cid
            uniq.append(rr); universe.append(rr)
        stolen = len(c["kept"]) - len(uniq)
        c["final"] = uniq
        if stolen:
            print(f"  cluster {cid}: {stolen} keyword(s) already claimed by an earlier cluster")

    json.dump(universe, open(os.path.join(CACHE, "DERIVED-full-universe.json"), "w"), indent=1)

    print(f"\n{'#':>2} {'cluster':38} {'kws':>5} {'volume':>8} {'kd<=20':>7} {'kd20_vol':>9} {'aio':>5} {'tool':>5}")
    tot = {"k": 0, "v": 0, "k20": 0, "v20": 0, "aio": 0, "tool": 0}
    for cid in sorted(per_cluster):
        f = per_cluster[cid]["final"]
        v = sum(r.get("volume") or 0 for r in f)
        k20 = [r for r in f if r.get("difficulty") is not None and r["difficulty"] <= 20]
        v20 = sum(r.get("volume") or 0 for r in k20)
        aio = sum(1 for r in f if "ai_overview" in (r.get("serp_features") or []))
        tool = sum(1 for r in f if TOOL_JOB.search(r["keyword"]))
        print(f"{cid:>2} {per_cluster[cid]['name']:38} {len(f):>5} {v:>8} {len(k20):>7} {v20:>9} {aio:>5} {tool:>5}")
        tot["k"] += len(f); tot["v"] += v; tot["k20"] += len(k20); tot["v20"] += v20
        tot["aio"] += aio; tot["tool"] += tool
    print(f"{'':>2} {'TOTAL':38} {tot['k']:>5} {tot['v']:>8} {tot['k20']:>7} {tot['v20']:>9} {tot['aio']:>5} {tot['tool']:>5}")

    json.dump({str(k): {"name": v["name"], "raw": v["raw"], "gross_vol": v["gross_vol"],
                        "dropped": [d["keyword"] for d in v["dropped"]]}
               for k, v in per_cluster.items()},
              open(os.path.join(CACHE, "DERIVED-cleaning-audit.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
