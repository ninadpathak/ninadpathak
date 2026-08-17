#!/usr/bin/env python3
"""Token-match contamination sweep over the seven-cluster keyword universe.

Context. Two agents independently found the same defect class within an hour:
`audit documentation software` is the ISA 230 accounting sense, and
`developer community` returns community development block grants. Ahrefs `terms`
mode matches token presence, not meaning, and the first cleaning pass (_clean.py)
removed obvious veins while leaving whole industries behind — including at the
head of a cluster.

Method, in the order the evidence was weighted:

1. **Parent topic.** The cheapest and strongest tell. A keyword whose Ahrefs
   parent topic belongs to another industry is contaminated however well it
   matched the seed string. `community management` has parent topic `hoa`.
   `audit documentation software` has parent `auditing software for accountants`.
2. **Live SERP**, where the parent topic is missing, ambiguous, or itself
   misleading. Every SERP call is recorded in DECISIONS below with its date.
3. **Keep on doubt.** Where neither instrument settled it, the keyword is kept
   and listed as CONTESTED rather than removed. An over-stripped universe is as
   wrong as an inflated one, just less visibly.

Two SERP checks reversed a removal that parent topic alone would have made:
`developer portal` (parent `discord developer portal`) is a genuine docs-ops
concept, and `reddit seo` (parent `latest seo`) is genuine Reddit-marketing
practice. Both are kept. That is why the SERP step is not optional.

Run: python3 _contamination_sweep.py
Emits: DERIVED-contamination-sweep.json
"""

import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
UNIVERSE = HERE / "DERIVED-full-universe.json"
OUT = HERE / "DERIVED-contamination-sweep.json"

# ---------------------------------------------------------------------------
# Verification record. Every SERP read was done on 2026-08-17 via WebSearch,
# which is free; no paid call was made for this sweep.
# ---------------------------------------------------------------------------
DECISIONS = {
    "community management": {
        "verdict": "REMOVE",
        "evidence": "SERP 2026-08-17: Community Management Services Inc, CMS Orlando "
                    "'HOA & Condo Association Management Experts', Community Management "
                    "Advisors, CMC 'HOA Property Management', CMA Community Association, "
                    "Professional Community Management. A definition result states "
                    "'community management (also called property management)'. "
                    "Entirely HOA/property. This is cluster 6's head term.",
    },
    "community management services": {
        "verdict": "REMOVE",
        "evidence": "SERP 2026-08-17: The Management Trust 'HOA Services', Yelp Property "
                    "Management, CMA Community Association Management, CMC 'HOA Property "
                    "Management', Associa, condomanagement.com. Entirely HOA/property.",
    },
    "community management software": {
        "verdict": "KEEP",
        "evidence": "SERP 2026-08-17: majority on-niche — Glue Up, Sprinklr, Bevy, G2's "
                    "'Online Community Management' category, BuddyBoss. PayHOA and "
                    "association-management results are a minority. Kept, partially "
                    "contaminated.",
    },
    "online community engagement": {
        "verdict": "REMOVE",
        "evidence": "SERP 2026-08-17: Granicus (government software), Simply Stakeholders, "
                    "Local Housing Solutions (housing policy), an NCBI COVID paper. This is "
                    "the civic/public-consultation sense, a separate industry. Higher Logic "
                    "is the only on-niche result.",
    },
    "reddit seo": {
        "verdict": "KEEP",
        "evidence": "SERP 2026-08-17: Search Engine Land, Siege Media, SEO Sherpa, Sprout "
                    "Social, Semrush — all about optimising brand presence on Reddit for "
                    "search. Genuinely on-niche despite parent topic 'latest seo'. "
                    "A removal that parent topic alone would have made wrongly.",
    },
    "developer portal": {
        "verdict": "KEEP",
        "evidence": "SERP 2026-08-17: OpsLevel, Zuplo, Pronovix, Port.io, Azure API "
                    "Management, getDX — developer portals as a docs and platform "
                    "engineering concept. Parent topic 'discord developer portal' is "
                    "misleading. A second removal that parent topic alone would have "
                    "made wrongly.",
    },
    "audit documentation example": {
        "verdict": "REMOVE",
        "evidence": "SERP 2026-08-17: PCAOB AS 1215, wallstreetmojo, wikiaccounting, "
                    "accountinguide, Vaia accounting. 'work papers or working papers', "
                    "depreciation, inventory counts. ISA 230 assurance sense.",
    },
    "chatgpt seo": {
        "verdict": "KEEP",
        "evidence": "SERP 2026-08-17: mixed but majority the right sense — SEO Sherpa "
                    "'Optimize Your Content for AI Search', Semrush 'How to Show Up in "
                    "ChatGPT Responses', directom 'How To Optimize For ChatGPT'. The "
                    "head terms are citation-optimisation. Only the explicit prompt "
                    "sub-family is the inverted job.",
    },
    "how to host a virtual event": {
        "verdict": "REMOVE",
        "evidence": "SERP 2026-08-17: Zoom Webinars, Lucidspark, Whova, ON24, wiz-team, "
                    "Wharton IT. 'speaker fees, attendee gifts, video and audio equipment', "
                    "'attendee acquisition and marketing'. Corporate webinar/events "
                    "industry, not community or technical events.",
    },
}

# ---------------------------------------------------------------------------
# Removal rules. Each is (cluster, name, reason, keyword-regex, parent-regex).
# A row is removed if either regex matches, unless it is in KEEP_EXPLICIT.
# ---------------------------------------------------------------------------
KEEP_EXPLICIT = {
    # SERP-verified on-niche despite a misleading parent topic.
    "developer portal", "reddit seo", "reddit seo guide", "reddit seo tips",
    "reddit seo strategy", "community management software",
    "best community management software", "online community management software",
    "best online community management software", "community management platforms",
    "community management platform", "community management tools",
    "community management tool", "community management system",
    "online community management platform", "community management strategy",
    "online community management", "online community management services",
    "best online community management", "community management app",
    # Genuine AI/ML terms whose parent topics look off-domain.
    "linkedin mcp server", "tavily mcp server", "context7 mcp server",
    "ai customer support agent", "vector database companies",
    # A real DevRel community, not a token match.
    "developer marketing alliance",
    # Community event planning is the job a DevRel actually does; the commercial
    # rule's "event planning" token caught it wrongly.
    "community event planning",
    # Process documentation is genuinely adjacent to Ninad's work.
    "sop documentation template", "sop documentation software",
}

RULES = [
    # ---------------- cluster 1: documentation ----------------
    (1, "accounting-audit",
     "ISA 230 / PCAOB assurance workpapers, not developer documentation. "
     "Parent topic 'auditing software for accountants' names the industry outright; "
     "SERP confirmed.",
     r"^audit documentation", r"audit(ing)? (documentation|software for accountants)"),
    (1, "medical-records",
     "Clinical and hospital records management, a regulated separate industry.",
     r"\b(hospital|medical|clinical|patient|nursing|nurse|charting|wound|picc|perrla)\b",
     r"\b(medical|hospital|clinical|patient|nursing)\b"),
    (1, "lending-finance",
     "Loan origination document management.",
     r"\bloan documentation\b", r"\bloan document\b"),
    (1, "hr-disciplinary",
     "HR performance and disciplinary paperwork, not product documentation.",
     r"\bemployee (conversation|behavior|behaviour) documentation\b|^employee documentation template$",
     r"^employee (conversation )?documentation template$"),

    # ---------------- cluster 2: DevEx / DevRel ----------------
    (2, "real-estate-developer",
     "Property and construction 'developer'. Pure token match on developer/development.",
     r"\b(real estate|home) develope?r\b|how to become a real estate developer",
     r"\b(real estate|home builder) (develop|marketing)"),
    (2, "adobe-experience-manager",
     "Adobe Experience Manager product training and certification. Token match on "
     "'experience' plus 'developer'.",
     r"\badobe experience manager\b|\baem developer\b", r"\b(adobe experience manager|adobe aem|aem developer)\b"),
    (2, "salesforce-marketing-cloud-cert",
     "Salesforce Marketing Cloud Developer certification, including exam dumps. "
     "Token match on 'marketing' plus 'developer'.",
     r"\bmarketing[- ]cloud[- ]developer\b|\bsalesforce marketing cloud developer\b",
     r"\b(salesforce )?marketing[- ]cloud[- ]developer\b"),
    (2, "web-marketing-developer-roles",
     "Hiring and role queries for web or email developers at marketing agencies, "
     "not developer marketing as a discipline.",
     r"^(email marketing developer|digital marketing web developer|digital marketing developer|"
     r"marketing web developer|marketing developer|web developer and marketing)$",
     r"\b(email developer jobs|digital marketing web developer|marketing web developer)\b"),
    (2, "no-experience-jobseeker",
     "Job-seeker queries matching on the token 'experience'.",
     r"\bno experience\b", r"\b(no experience|cover letter)\b"),
    (2, "vendor-navigational",
     "Navigational or partner-programme pages for unrelated products.",
     r"^(apple worldwide developer relations certification authority|"
     r"pinterest marketing developer partners|user experience developer)$",
     r"^(apple worldwide developer relations certification authority|pinterest marketing|ux developer)$"),

    # ---------------- cluster 3: AI agents / RAG ----------------
    (3, "insurance-agent",
     "Insurance sales agents. Token match on 'agent'.",
     r"\b(insurance) agent\b", r"\binsurance agent\b"),

    # ---------------- cluster 4: AI Overviews / AI search ----------------
    (4, "chatgpt-as-seo-copywriter",
     "Prompt templates for using ChatGPT to do traditional SEO copywriting. The "
     "inverse job: this cluster is about being cited BY assistants, not using one "
     "to write meta descriptions.",
     r"\bprompts?\b|\bseo plugin\b", r"\bprompts?\b|\bseo core ai plugin\b"),
    (4, "non-english",
     "Spanish-language query in a US English universe.",
     r"\bpara seo\b", None),
    (4, "ai-overview-suppression",
     "Consumers wanting to switch AI Overviews off. Opposite intent, and a browser "
     "extension market.",
     r"\bhide (google )?ai overviews?\b", r"\bhide (google )?ai overviews?\b"),

    # ---------------- cluster 5: Reddit marketing ----------------
    (5, "junk-token",
     "A Reddit username or subreddit string, not a topic.",
     r"progressive growth", r"progressivegrowth"),
    (5, "consumer-subreddit-discovery",
     "Consumer Reddit browsing: finding, viewing, listing and defining subreddits. "
     "Reddit's own properties own these and they carry no marketing intent.",
     r"^(subreddit|reddit subreddit|what is a? ?subreddit|subreddit meaning|subreddit list|"
     r"subreddit finder|subreddit search|subreddit viewer|subreddit search engine|"
     r"similar subreddit|similar subreddit finder|reddit subreddit list|"
     r"how to search within a subreddit|reddit subreddit search)$",
     r"^(subreddit|subreddit list|subreddit meaning|what is a subreddit|reddit viewer|"
     r"reddit subreddits|list of subreddits|similar subreddits|reddit subreddits search)$"),
    (5, "ad-blocking",
     "People blocking Reddit ads. Opposite intent to advertising on Reddit.",
     r"\bblock (reddit )?ads?\b|\bblock ads (on )?reddit\b", r"\b(how to block|adblock)\b"),
    (5, "reddit-as-source-for-other-topics",
     "'reddit' is the source being consulted, not the subject. Parent topics point "
     "at other ad platforms and generic SEO.",
     r"^(seo reddit|squarespace seo reddit|youtube ads reddit|facebook ads reddit|twitch ads reddit|"
     r"affiliate marketing reddit)$",
     r"^(latest seo|is squarespace good for seo|reddit youtube ads|facebook ads news|twitch ads|"
     r"reddit affiliate marketing)$"),
    (5, "reddit-product-navigation",
     "Navigation to Reddit's own ad product: login, logo, account, help. A third "
     "party cannot rank and they convert to nothing.",
     r"^reddit ads (login|logo|account|help|help center)$", None),

    # ---------------- cluster 6: forums / community ----------------
    (6, "hoa-property-management",
     "HOA, condo association and residential property management. Parent topics "
     "'hoa', 'hoa management software', 'cms hoa', 'townsq' name the industry; SERP "
     "confirmed on the head term.",
     r"^(community management|community management services|community management service|"
     r"residential community management software)$",
     r"^(hoa|hoa management software|cms hoa)$"),
    (6, "corporate-team-building",
     "Corporate team-building and icebreakers, a distinct market from audience "
     "and community building.",
     r"\bcommunity building (activities|games|questions)\b", r"\bteam building\b"),
    (6, "discord-navigational",
     "Discord's own policy and login pages, and Discord job queries.",
     r"^(discord community guidelines|discord community server|discord community servers|"
     r"discord community manager)$",
     r"^(discord rules|discord login|discord jobs)$"),
    (6, "civic-community-engagement",
     "Public consultation and civic engagement, a separate government-software "
     "industry. Parent topic 'publicinput' names a civic-tech vendor; SERP confirmed.",
     r"^(online community engagement|online community engagement activities|"
     r"online community engagement strategy|online community engagement ideas|"
     r"benefits of online community engagement|online community engagement tools|"
     r"online community engagement platform)$",
     r"^(publicinput|platforms for community engagement|online community engagement activities|"
     r"benefits of online community engagement)$"),
    (6, "off-niche-vertical-communities",
     "Consumers looking for a community to join in an unrelated vertical, rather "
     "than practitioners building one.",
     r"^online (artistic|learning|gaming|writing|health|fitness|trading|marketing) community$|"
     r"^(aarp online community|small business online community)$",
     r"^(aarp virtual community center|virtual learning community|gaming community|"
     r"shut up and write|online health community|online fitness community|trading|"
     r"small business communities|digital marketing community)$"),
    (6, "classroom-and-dictionary",
     "Classroom teaching practice and a dictionary lookup.",
     r"^(community building synonym|community building examples)$",
     r"^(community building synonym|building community in the classroom)$"),
    (6, "community-manager-jobs",
     "Job-seeker queries.",
     r"^online community manager$", r"\bjobs\b"),

    # ---------------- cluster 7: events (bounded — seo-90day owns row level) ----
    (7, "commercial-event-industry",
     "Corporate and webinar events industry: platforms, software, ROI, attendee "
     "acquisition, registration, ticketing, sponsorship, trade shows, run-of-show. "
     "SERP on the head term returns Zoom, ON24 and Whova. seo-90day owns the "
     "row-level pass; this rule exists to size the correction, not to settle it.",
     r"\b(event (platform|platforms|software|management|marketing|roi|planner|planning|production|"
     r"trends|checklist|agenda|budget|branding|promotion|statistics|strategy|technology|"
     r"engagement|feedback|survey|landing page)|attendee|registration|ticketing|sponsorship|"
     r"trade ?show|expo|gala|fundrais|wedding|catering|venue|corporate (event|party)|"
     r"holiday party|team ?building|run of show|webinar (platform|software)|"
     r"how to (plan|host) a virtual event|best time to host a virtual event|"
     r"virtual (event ideas|networking event|product launch event)|zoom virtual event|"
     r"what is a? ?virtual event|types of virtual event|hybrid virtual and in person event)\b",
     None),
]

CONTESTED = {
    # Kept, but a reasonable reviewer could remove these. Listed so the decision
    # is visible rather than buried.
    "crypto community building": "A different vertical, but the job is the same growth work.",
    "circle online community": "Branded platform query; a practitioner researches Circle.",
    "best forum software": "On-niche, though 'forum software' skews to legacy vendors.",
    "best ai agent projects from 2025 hackathons": "Parent topic 'hackathon agency' is event "
        "services, but the keyword is genuinely about AI agent projects. Possible cluster-7 "
        "misassignment rather than contamination.",
    "how to make a subreddit": "Creating a subreddit is a real Reddit-marketing action; the "
        "consumer-discovery rule deliberately does not catch the create/start family.",
    "subreddit stats": "Analyst and marketer tooling rather than consumer browsing.",
}


def matches(rule, row):
    _, _, _, kw_pat, pt_pat = rule
    kw = row["keyword"]
    pt = row.get("parent_topic") or ""
    if kw in KEEP_EXPLICIT:
        return False
    if kw_pat and re.search(kw_pat, kw, re.I):
        return True
    if pt_pat and pt and re.search(pt_pat, pt, re.I):
        return True
    return False


def main():
    rows = json.loads(UNIVERSE.read_text())
    removed = {}
    reasons = defaultdict(lambda: {"keywords": [], "volume": 0, "reason": ""})

    for row in rows:
        for rule in RULES:
            cluster, name, reason, _, _ = rule
            if row["cluster"] != cluster:
                continue
            if matches(rule, row):
                key = f"{cluster}:{name}"
                reasons[key]["reason"] = reason
                reasons[key]["keywords"].append(
                    {"keyword": row["keyword"], "volume": row["volume"] or 0,
                     "parent_topic": row.get("parent_topic")}
                )
                reasons[key]["volume"] += row["volume"] or 0
                removed[row["keyword"]] = key
                break

    per_cluster = {}
    for c in sorted({r["cluster"] for r in rows}):
        crows = [r for r in rows if r["cluster"] == c]
        kept = [r for r in crows if r["keyword"] not in removed]
        drop = [r for r in crows if r["keyword"] in removed]
        per_cluster[c] = {
            "before_keywords": len(crows),
            "before_volume": sum(r["volume"] or 0 for r in crows),
            "removed_keywords": len(drop),
            "removed_volume": sum(r["volume"] or 0 for r in drop),
            "after_keywords": len(kept),
            "after_volume": sum(r["volume"] or 0 for r in kept),
            "kd20_after_keywords": len([r for r in kept if (r["difficulty"] or 99) <= 20]),
            "kd20_after_volume": sum(r["volume"] or 0 for r in kept
                                     if (r["difficulty"] or 99) <= 20),
        }

    out = {
        "generated": "2026-08-17",
        "method": "parent topic first, live SERP where ambiguous, keep on doubt",
        "paid_calls": 0,
        "serp_decisions": DECISIONS,
        "contested_kept": CONTESTED,
        "removals_by_reason": {k: v for k, v in sorted(reasons.items())},
        "per_cluster": per_cluster,
        "totals": {
            "before_keywords": len(rows),
            "before_volume": sum(r["volume"] or 0 for r in rows),
            "removed_keywords": len(removed),
            "removed_volume": sum(v["volume"] for v in reasons.values()),
            "after_keywords": len(rows) - len(removed),
            "after_volume": sum(r["volume"] or 0 for r in rows if r["keyword"] not in removed),
        },
    }
    OUT.write_text(json.dumps(out, indent=2))

    t = out["totals"]
    print(f"{'cluster':>8} {'before':>18} {'removed':>18} {'after':>18}  {'cut':>5}")
    for c, s in per_cluster.items():
        pct = (s["removed_volume"] / s["before_volume"] * 100) if s["before_volume"] else 0
        print(f"{c:>8} {s['before_keywords']:>4} {s['before_volume']:>11,} "
              f"{s['removed_keywords']:>4} {s['removed_volume']:>11,} "
              f"{s['after_keywords']:>4} {s['after_volume']:>11,}  {pct:>4.0f}%")
    pct = t["removed_volume"] / t["before_volume"] * 100
    print(f"{'TOTAL':>8} {t['before_keywords']:>4} {t['before_volume']:>11,} "
          f"{t['removed_keywords']:>4} {t['removed_volume']:>11,} "
          f"{t['after_keywords']:>4} {t['after_volume']:>11,}  {pct:>4.0f}%")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
