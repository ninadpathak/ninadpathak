# Can this site build named reference infrastructure?

**Date:** 2026-08-17 · **Agent:** `seo-currency` · **Paid: 5 Semrush backlink calls, logged**

**Verdict: no, and it is a lottery ticket. Every coordination-problem slot in this niche is
already owned, and the slots that are open are open because they are not coordination
problems. Do not spend twenty rows on it.**

**But the counter-case comes with a replacement that is measured, not aspirational: one
original experiment by an independent author with zero domain authority earned 85 referring
domains.** That is the play. Working below.

---

## 1. What the four worked examples actually did

I read all four specs and measured their footprint rather than reasoning about them.

### The mechanism is embedded attribution, not admiration

This is the finding that reframes the question. Reference infrastructure does not earn links
because people admire it. **It earns links because the convention's own template contains a
link, and adopting the convention means pasting the template.**

`keepachangelog.com`'s example changelog contains the line:

> "The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)"

People copy that example into their own `CHANGELOG.md`. GitHub code search, 2026-08-17:

| String | Public files containing it |
|---|---:|
| `semver.org` | **956,416** |
| `keepachangelog` | **749,568** |
| `keepachangelog.com` | **706,560** |
| — of which `CHANGELOG.md` files | **587,776** |
| `conventionalcommits.org` | **285,696** |
| `llmstxt.org` | **16,128** |

**587,776 changelogs carry that pasted line.** That is where 2,220–7,185 referring domains
come from. It is a mechanism, and it is designable.

`semver.org` states it outright rather than relying on the template:

> "Link to this website from your README so others know the rules and can benefit from them."

It is also CC BY 3.0, which *requires* attribution. Two independent link engines in one spec.

### But four other things had to be true, and one cannot be manufactured

| | semver | keepachangelog | conventional commits | llms.txt |
|---|---|---|---|---|
| **Coordination problem** | dependency hell | shared changelog format | machine-readable history | agent-readable site map |
| **Link mechanism** | explicit instruction + CC BY | template line | badge + tooling | cited by every explainer |
| **Own domain** | semver.org | keepachangelog.com | conventionalcommits.org | llmstxt.org |
| **Tooling adoption** | npm | changelog generators | commitlint, semantic-release | Mintlify, GitBook auto-generate |
| **Author platform** | **Tom Preston-Werner, GitHub co-founder** | Olivier Lacan, known Rails dev | Angular team, then consortium | **Jeremy Howard, fast.ai founder** |

Ninad can build the first four. **The fifth is the one that cannot be manufactured**, and two
of the four exemplars had it in an extreme form.

### And a coordination problem is the load-bearing requirement

A convention accretes citations only when **the value comes from everyone doing it the same
way**. A changelog format is worth adopting because a reader recognises it. A versioning
scheme is worth adopting because a dependency resolver depends on it.

A checklist is not that. Everyone can have their own checklist and lose nothing. **That
distinction decides every candidate below.**

---

## 2. The candidate slots, and who owns them

| Candidate | Coordination problem? | Incumbent | Verdict |
|---|:---:|---|---|
| Documentation taxonomy | yes | **Diátaxis** — 2,240 referring domains | Closed |
| Changelog format | yes | **keepachangelog** — 587,776 files | Closed |
| Versioning scheme | yes | **semver** — 956,416 files | Closed |
| Commit convention | yes | **conventional commits** — 285,696 files | Closed |
| Machine-readable site summary | yes | **llms.txt** — 16,128 files | Closed |
| **Agent instruction file** | yes | **AGENTS.md — 2,723,840 public files**, stewarded by the **Agentic AI Foundation under the Linux Foundation**, backed by OpenAI Codex, Amp, Google Jules, Cursor and Factory | **Closed, hardest of all** |
| Crawler access declaration | yes | robots.txt, plus Cloudflare's Content Signals | Closed |
| Docs review checklist | **no** | none — top GitHub repo has 13 stars | Open, and worthless |
| Documentation maturity model | **no** | none — top repo has 13 stars | Open, and worthless |
| AI-citation readiness spec | partly | would need engine adoption; Google states no special markup is used | Unwinnable |

**Every slot with a genuine coordination problem is taken. The two that are open are open
because nobody needs them to be shared.** An empty slot in a market with coordination value
would not stay empty; its emptiness is the evidence against it.

The `AGENTS.md` row is the one to sit with. It is the newest convention in exactly our
territory, it reached 2.7 million files, and it was claimed by a Linux Foundation body backed
by OpenAI and Google. **That is the competition for any emerging slot in this niche now.** A
DR-26 personal site does not win that race; the slot gets claimed by whoever has distribution,
and the entities with distribution are watching.

---

## 3. The honest counter-case: yes, it is a lottery ticket

Ninad asked whether this is mostly luck and timing. **Substantially, yes**, and here is the
case as fairly as I can put it.

**Survivorship bias is the dominant feature of the evidence.** I studied four specs that
worked. I cannot easily count the specs that did not, and there are certainly hundreds. Every
one of them also had a name, a version number, a domain and a rationale. The four I can name
are the four that won, which tells me what winning looks like and almost nothing about the
odds.

**Timing did heavy lifting in each case.** semver landed as npm was exploding. keepachangelog
landed in 2014 into an empty slot. llms.txt landed in September 2024 at the exact peak of
AI-crawler anxiety. None of those windows were engineered by their authors.

**Adoption was decided by parties the author did not control.** semver became inevitable when
npm adopted it. llms.txt became inevitable when Mintlify and GitBook started generating it.
Neither author could make that happen.

**Author platform was doing visible work in two of four.** A spec published by a GitHub
co-founder starts with distribution a personal site cannot buy.

**Honest probability that a DR-26 personal site becomes the cited reference for anything in
this niche within twelve months: low single digits.** I will not dress that up with a number
I cannot support, but I would not plan against better than roughly 1 in 20, and the twenty
rows it would cost are the same twenty rows that could go somewhere measured.

**The one thing that is not luck** is the mechanism. If a convention *is* adopted, embedded
attribution converts adoption into referring domains reliably. That part is craft. It is just
downstream of the part that is luck.

---

## 4. What to do instead, with a measured number attached

The point of the reframe was to grow referring domains from zero. Reference infrastructure is
one route to that and it is closed. **There is a second route and it is measurable.**

### The control case: an independent author, no domain authority, one experiment

Mark Williams-Cook published the **cats.txt** experiment — inventing a fake standard about
office cats to show that every "proof" that llms.txt works could be reproduced by a joke. It
was published on a Substack subdomain.

Semrush backlinks, 2026-08-17:

| Target | Backlinks | **Referring domains** | Authority score |
|---|---:|---:|---:|
| cats.txt experiment (single Substack post) | 842 | **85** | **0** |
| markwilliamscook.com (his whole personal domain) | 1,160 | 285 | 11 |
| Ahrefs 137k-domain llms.txt study (single post, DR-91 host) | 1,567 | **439** | 51 |
| keepachangelog.com (whole domain, 12 years) | 137,172 | 7,185 | 40 |

**One post, on a subdomain with an authority score of zero, earned 85 referring domains.**
That is the cleanest available control for whether a low-authority independent author can earn
links with original work. The answer is yes, and it did not require a coordination problem, a
consortium, or a famous name.

It got picked up by Search Engine Journal, Search Engine Land, multiple agency blogs and
YouTube — because it produced **a result nobody else had**, not because of who published it.

### Why this is the right play here specifically

- **It needs no slot.** Nobody owns "measuring things."
- **It is in our exact territory**, and the receipts for the first one are already gathered:
  Google's own statement that Search ignores llms.txt, the 137,210-domain study, the cats.txt
  falsification, Chrome Lighthouse's silence. `FORMAT-BACKLOG.md` item 6 already scoped it.
- **Google is surfacing the demand**: *"Does LLMs.txt actually work?"* appears as a
  People-also-ask question on the `llms.txt validator` SERP we already target.
- **The tools become the instrument rather than the product.** The AI crawler checker can
  measure 500 documentation sites' robots.txt in an afternoon and produce a number nobody has
  published. That is what the tools are *for* under the reframe — they generate original data,
  which earns the links, which moves position. That is a coherent chain, and each link in it
  is evidenced.

### Two caveats I will not leave out

**The comparison is not clean.** The Ahrefs study sat on a DR-91 domain, so 439 is an upper
bound that domain authority helped produce. And Williams-Cook is a known figure in SEO with an
existing audience — his 85 domains are not what a cold start earns. **A first attempt from
this domain should be planned at well under 85**, and possibly at single digits.

**One study is not a strategy either.** cats.txt worked because it was a genuine falsification
with a memorable hook. A competent-but-ordinary "we surveyed 30 sites" post earns far less. The
variance here is high too — it is just cheaper per ticket, in our niche, and with the first
set of receipts already in hand.

---

## 5. Recommendation

1. **Do not build reference infrastructure.** The slots are taken, the open ones are open for a
   reason, and the odds do not justify twenty rows.
2. **Do not spend a row proving me wrong on that** — the AGENTS.md row is the argument.
   Emerging slots in this niche are now claimed by Linux Foundation bodies within months.
3. **Spend the rows on original measurement**, starting with the llms.txt evidence piece whose
   receipts are already gathered and whose demand Google is visibly surfacing.
4. **Use the five tools as instruments, not products.** They exist, they are tested, and they
   can generate data nobody else has. That is the link engine available to this domain.
5. **Record a number to test this against.** The cats.txt control is 85 referring domains. If
   the first original-measurement piece earns fewer than ten within ninety days, that is
   evidence the second route is closed too, and the honest answer then is that authority is not
   movable at this scale inside this campaign, which is worth knowing before month three.

**One thing that follows from the funnel diagnosis and is worth saying plainly.** If 79% of
impressions sit at position 31+ and only 5.9% ever reach the top ten, then a handful of
referring domains will not fix it either. Eighty-five referring domains is a meaningful
improvement on zero and it is not authority parity with Semrush or SE Ranking. The realistic
ceiling for this campaign is winning specific long-tail queries where the competition is also
small — the two operational queries at 10.6 and 10.2 — not moving the domain into a weight
class it cannot reach in ninety days.

---

## 6. Paid call log

| Report | Target | Result |
|---|---|---|
| `backlinks_overview` | `ahrefs.com/blog/llmstxt-study/` (url) | ERROR 50, nothing found |
| `backlinks_overview` | `https://ahrefs.com/blog/llmstxt-study/` (url) | 1,567 links / 439 domains |
| `backlinks_overview` | `keepachangelog.com` (root) | 137,172 / 7,185 |
| `backlinks_overview` | cats.txt Substack post (url) | 842 / 85 |
| `backlinks_overview` | `markwilliamscook.com` (root) | 1,160 / 285 |

Five calls. Everything else — the four spec pages, GitHub code search counts, SERP reads —
was free. Note that Semrush reports 7,185 referring domains for keepachangelog where Ahrefs
reported 2,220; the tools disagree by 3×, as established in the SERP verification, so treat
the magnitude and not the figure.
