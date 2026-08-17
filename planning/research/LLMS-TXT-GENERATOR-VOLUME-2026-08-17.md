# `llms.txt generator` volume: 300 or 2,400?

**Date:** 2026-08-17 · **Agent:** `seo-currency` · **Paid calls: 0** (the Semrush figure was
already bought on the earlier pass)

**Answer: neither number can be confirmed, the range is 300–2,400/mo, and I would plan
against the low end. But the number does not change any decision currently on the board, and
that is the more useful finding.**

---

## 1. What each instrument said, and what happened when I tried to arbitrate

| Instrument | Result |
|---|---|
| Ahrefs | **300/mo.** Cannot re-pull; token dead. |
| Semrush `phrase_these` | **2,400/mo**, KD 41, CPC $3.53, competition 0.29, 129 results. |
| **Google Trends** | **Unavailable.** The public endpoint returns **HTTP 429**. This was the one free instrument that could have given a quantitative relative answer, and it is closed. |
| **Search Console** | **Blind here, and not in the way it first appears.** See §2. |
| Live SERP | Read 2026-08-17. Evidence both ways. See §3. |
| Google autocomplete | Ordinal evidence, and the most useful thing I got. See §4. |

---

## 2. One correction to the brief, because it matters

The brief suggested that `/llms-txt-generator/` having zero impressions in its entire recorded
history is "itself evidence about whether 2,400/mo of intent exists and reaches anyone."

**It is not, and I would rather say so than let it be used that way.** A Search Console
impression requires appearing in a result set at all. The page has never appeared for these
queries at any depth, so its zero measures **our absence, not the market's size**. A keyword
with 100,000 searches a month would also show zero impressions for a page Google never
surfaces.

I checked the stronger version of the question too: **across Search Console's entire available
history, 2025-04-22 to 2026-08-14, this domain has received impressions for zero `llms.txt`
queries.** All 21 "llm"-matching queries are LLM-inference topics — `llm inference
optimization`, `speculative decoding llm`, `tool calling llm` — at positions 55–89. So Search
Console has no first-party signal on llms.txt demand of any kind, in either direction.

What the zero *does* prove is worth keeping: **whatever the true volume is, we currently
capture none of it.**

---

## 3. The live SERP argues both ways

**For the higher figure:** eight purpose-built tools on page one, including **Writesonic** (a
funded AI-writing SaaS) and **Firecrawl** (a funded developer tool), plus AIOSEO publishing a
"7 Best LLMs.txt Generators" listicle. Companies do not build and market eight competing free
tools against 300 searches a month. The related-search block also shows platform-specific
fragmentation — `wordpress`, `drupal`, `magento 2`, `shopify`, `wordlift` — which is the shape
of a large, splintered query family rather than a single small one.

**For the lower figure:** the SERP carried **no ads at all**. By comparison
`ai overviews checker`, which both tools price at only 390–700/mo, *did* carry a sponsored
result. A 2,400/mo commercial-intent query with a $3.53 CPC that attracts no advertiser is
odd.

**Neither argument is a measurement.** Both are inference from SERP shape, and I am labelling
them as such rather than dressing either up as a finding.

One more note on the Semrush figure specifically: it returned **exactly 2,400** for both
`llms.txt generator` and `robots.txt checker`. Its other figures in the same batch vary
plausibly (3,600, 1,600, 880, 720, 390, 260), so this is probably coincidence rather than a
bucket ceiling — but two identical round numbers is a reason to treat the precision, not
necessarily the magnitude, with suspicion.

---

## 4. Autocomplete, which is the best free evidence available

Google's autocomplete is ordered by real query popularity. Read 2026-08-17:

| Seed | Ordering |
|---|---|
| `llms.txt` | 1. llms.txt · **2. llms.txt generator** · 3. llms.txt file generator · 4. llms.txt what is it · 5. llms.txt checker · 6. llms.txt file · 7. llms.txt validator |
| `llms txt` | 1. llms txt · **2. llms txt generator** · 3. llms txt checker · 4. llms txt validator |

**`generator` is the top modifier in the family, ahead of `checker`, `validator`, `file` and
even `what is it`.** Both datasets agree on that *ordering*; they disagree only on magnitude.

This is the piece that leans me toward the higher figure being closer. The family head
`llms.txt` is 3,100/mo on Ahrefs' own numbers. Ahrefs then puts the family's **dominant
modifier** at 300 — under 10% of the head — while placing `what is llms.txt` at 1,800. A
modifier that outranks "what is it" in autocomplete but scores six times lower in volume is
internally inconsistent.

**But autocomplete is ordinal.** It tells me `generator` is the biggest modifier. It cannot
tell me whether that is 400 or 2,400, and I am not going to convert an ordering into a number.

---

## 5. Verdict, and which instrument I would trust

**Range: 300–2,400/mo. Plan against 300–500.**

**Which instrument I would trust: none of the third-party ones, and I would not spend more to
try.** Both vendors model this from clickstream panels, and `llms.txt` is a term barely two
years old — exactly the condition under which panel-based estimation is least reliable. Ahrefs
had no keyword difficulty and no parent topic for the entire llms.txt family, which is a
sparse-data signal on its side; Semrush returned a suspiciously round repeat on its side.

**The instrument I would trust is first-party Search Console, once we actually rank.** That is
not evasion: it is the only instrument that reports what this domain receives rather than what
a panel infers, and it becomes available the moment the page surfaces at any depth. Everything
else here is an estimate of a market we currently take 0% of.

Plan low, because the asymmetry favours it: if the true figure is 2,400 and we planned for
300, we under-invested in a page that already exists and cost nothing more. If it is 300 and
we planned for 2,400, we spent a calendar row on a phantom.

### Why this does not change any decision on the board

- **Tool building has stopped at five.** No row is being spent to build a generator; it has
  existed for months.
- **The generator's SERP is 8/10 purpose-built tools** and we appear nowhere on it. At 300 or
  at 2,400, our present capture is zero and the competitive picture is identical.
- **The only decision the number could touch** is whether to write supporting content for the
  generator. The answer is the same either way, and for a different reason: Google surfaces
  *"Does LLMs.txt actually work?"* as a People-also-ask question on the adjacent
  `llms.txt validator` SERP. **That is measured demand for a specific article**, it needs no
  volume estimate to justify, and it is a better use of a row than either figure would imply.

So: range stated, low end recommended, and the honest note that resolving it further would be
spending cycles on a number that changes nothing.
