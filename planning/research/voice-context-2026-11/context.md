# Voice context, November 2026

Working notes for the voice rewrite of ninadpathak.com. `sources.json` holds every external item with its URL, author, date, exact quotes and the posts it connects to. `verify_quotes.py` refetches each page and checks each quote.

## Why the old posts read like a B2B blog

Diagnosis from 16 posts read on 2026-11-16 (semantic-caching, agent-error-handling, documentation-velocity, writing-for-ai-products, technical-writing-for-engineers, rag-vs-memory, technical-docs, time-to-first-token, ai-agent-failures, multi-agent-vs-single-agent, shorter-documentation, writing-changelogs, llm-inference-optimization, code-documentation, internal-vs-external-docs queries, claude-code-subagents pilot).

| Habit | Example from the corpus | Fix |
|---|---|---|
| The opener is a claim about the field that anyone could have written | "Technical documentation often suffers from information obesity." | Open on a dated thing a named person said or shipped, then the reaction to it |
| Experience is asserted and never shown | "Two years of running AI agents in production taught me", "I watched this play out at my last job", "one team I helped" | Cut every claim the repo cannot back. First person carries opinions only |
| Nobody else exists | No names, no dates, no thread, no one to disagree with | Quote people, link them, say where they are right and wrong |
| Every section has the same weight | Six H2s of about 250 words, each a principle with one analogy | Spend the words where the argument is. Compress settled material into a table |
| The reflexive analogy | "Think of it as a bus", "like watertight compartments", "like a tree" | Use the real case from a source. Keep an analogy only when no real case exists |
| Secondary statistics accepted whole | "Industry data puts 30-40% of LLM requests as semantically similar", "750%" | Go to the primary source, give the denominator, or drop the number |
| Stale advice presented as timeless | "Enable continuous batching", which engines have shipped as a default for years | Date the advice against what the tools do this quarter |
| Titles that promise a secret | "What Actually Works", "Nobody Talks About", "What Nobody Tells You" | Leave titles alone where they rank. Put the literal query first on a retitle |
| The recap ending | "Documentation is a tool, and a tool works best when it is lean" | End on the last concrete point or the open question |
| Sentence fragments left by the two-sentence paragraph rule | "Fail fast." as its own paragraph | Write paragraphs as one or two full sentences from the start |

## What each topic has been arguing about

### Agent memory and RAG
- Kevin Liao (Oct 3) says memory plugins are RAG over transcripts and agents need a maintained documentation workspace. The top comments answer that documents go stale too.
- Anthropic (Nov 6) measured what models choose to write down. Fewer, better notes beat an archive, and notes need checking against transcripts ("dreaming").
- Mads Thines (Nov 7) counts nine memory formats and asks for a shared one, on the OpenTelemetry model.
- Position taken on the site: the storage was never the difference. Memory is the write, supersede and expire decisions. Liao's Operator has all of them (rewrite on change, a session catalog, a write rule), so the post titled against memory specifies one. Liao rejects background "dreamer" agents and Anthropic relies on one; a note that was wrong when written is the case only the later pass catches.

### LLM inference
- The Modelplane field guide (Nov 10) treats continuous batching, paged KV cache and prefix caching as engine defaults: "Check it, don't build it."
- Ubicloud (Oct 20) showed tool-call schema accuracy of 92% on vLLM 0.28 and 100% with constrained decoding. Output quality depends on the engine and its flags.
- NVIDIA (Nov 13) published a table where throughput falls from 607.8 to 385.0 tok/s between concurrency 16 and 32.
- Position: the 2024 checklist is now the default config. The work is measuring where a deployment stops being useful and checking the engine has not changed the model's output.

### Code comments and coding agents
- Tom Adamczewski (Sep 24) measured models ignoring a "no comments" rule on 100 SWE-bench tasks.
- ryandrake (Sep 8) on comments that say what the code does not do. kqr (Sep 9) built a detector for machine-written comments.
- Nathan Broadbent (Nov 13) keeps 42 nested AGENTS.md files beside the code they describe.
- Position: the placement test in the post now has a fourth reader. Narrating comments are noise. Rationale belongs beside the code, where the agent editing the code will read it.

### Documentation length
- The i-have-adhd skill (Sep 8, 542 points) exists to stop agents burying the answer.
- Simon Willison (Nov 9) hides agent-written PR descriptions behind a details tag and writes the first paragraph himself.
- Rishabh Mishra (Nov 10): "It is too big for no reason."
- Position: text now costs nothing to produce, so length stopped signalling effort. Selection is the writer's job that is left.

### Docs read by agents
- Fern's State of Docs (Nov 10): agents are over half of requests on Fern-hosted docs, read the API reference and changelog, and ask for Markdown. Their method section says 68% of "agent" requests are classified by route and that the named-agent share is 32.8%.
- Position (new essay): a request is not a reader. The report's page-type finding is the useful part.

## Rules for using this file

- Use a source only after `verify_quotes.py <id>` passes in the session that writes the piece.
- Give the date of the thing next to its first mention.
- `unused_leads` in `sources.json` are unfetched. Fetch and quote-check before use.
- The two scripts check wording only. Before quoting, read the whole source, including what follows the quoted line: the first review of batch 1 found four fair-context failures that both scripts passed (a post said to skip a fix it contains, a comment quoted before its own reversal, an experiment asked to prove what it never varied, a limits paragraph quoted in part).
- Voice findings from that review, to hold in every batch: no shared second-paragraph concede-then-pivot, a pseudonymous commenter only where the argument turns on the comment, one date per source, no pronoun inferred from a name, plain opinion in place of "I'd", and essays without takeaways, checklists or all-question headings.

## Batch 2 (2026-11-17)

Pieces: internal-vs-external-docs, contextual-retrieval, stripe-technical-blog, documentation-types and the essay coding-models-new-code-vs-change went forward as batch 2a. The independent review held hybrid-search, llm-structured-outputs and ai-memory-management for batch 2b, where every carried-over vendor claim and code block is confirmed today or cut.

### Skipped, with reasons

| Post | Impressions (90 days) | Why it was skipped |
|---|---|---|
| best-llms-for-coding | 294 | Its figure draws the old model picks (Claude Opus, Gemini Pro, DeepSeek, GPT Codex, Cursor) and its narrated video recommends March models. An honest rewrite contradicts both assets, and no redraw or video work is in scope. The sources for a rewrite are fetched and recorded (SlopCodeBench, Real-SWE 1.1, Parsimony, Dan Luu), and the new essay covers the argument. Needs Ninad's call on the figure and video. |
| browser-vector-search | 435 | state.md holds changes to this page until Google recrawls the October 22 version. |
| quickstart-guide, release-notes-template | 307, 114 | Written on October 22 under the newer rules, tested, and ranking at positions 7 and 6. The risk to ranking outweighs a voice pass. |

### Where social posts come from

- Bluesky: `public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor=<handle>` and `getPosts?uris=at://<did>/app.bsky.feed.post/<rkey>` fetch without a login. Search (`searchPosts`) returns 403, so start from known practitioners' feeds.
- Mastodon: `https://<instance>/api/v1/timelines/tag/<tag>` and `/api/v1/statuses/<id>` fetch without a login. Tag timelines are thin for retrieval topics and better for documentation.
- X: no public page fetched cleanly in either batch, so no X post is quoted anywhere.

### Carried-over material that was not re-verified

- hybrid-search: the Elastic, Azure, Weaviate and WANDS benchmark figures.
- ai-memory-management: every code block and the eviction, KV cache and compression sections.
- llm-structured-outputs: OpenAI and Gemini API details and the 10-30% latency overhead.
- One carried-over quotation was wrong and is fixed: hybrid-search quoted BEIR as calling BM25 a "strong generalizable baseline", and the abstract's words are "Our results show BM25 is a robust baseline".

### Batch 2b (2026-11-17)

hybrid-search, llm-structured-outputs and ai-memory-management were rewritten to the reviewer's standard: every vendor, benchmark and API claim confirmed on its linked page that day and dated when older than a year, or cut, and every code block run with its output printed. The second review found three places where that still fell short (one OpenAI latency note read from a single tab, one unsupported comparison, one undated 2024 paper), and all three are corrected. The list of carried-over material below is therefore closed for these three posts.

- ai-memory-management film, mismatches with the text after the rewrite (the film is not changed in this batch):
  - Narration L4 (fourth of five lines in `video.yaml`): "So I'd score each entry by its relevance to the task and by whether the user asked to remember it." The text says a frontier model should decide what to write and limits hand-written rules to smaller or older models. The second half of the line, keeping what the user asked to remember, still matches the pinned-entry example.
  - On-screen caption in the L4 scenes: "THE SCORE ALSO WEIGHS ACCESS FREQUENCY ACROSS SESSIONS", with score bars. The text has no access-frequency scoring.
  - End card: "AI Memory Management for LLMs: What Actually Works". The title is now "...: What Works".
  - Narration L5: "add eviction on day one". The text puts eviction fifth of six build steps, before the first long session. Compatible in outcome.
  - Fixed in text: the `video.yaml` description no longer mentions scoring, so the page's VideoObject markup agrees with the article.
  - L1 to L3 agree with the text.
- ai-memory-management title lost the word "Actually" (Search Console shows no query containing it for the URL over 16 months).
- verify_quotes.py reads PDFs through pdftotext, used for the 2009 RRF paper.

### Videos checked against their text

- contextual-retrieval: no mismatch. My first note here said the film presents code as the best use case, and that was wrong: the reviewer's contact sheet and the narration show a 10-Q filing, the 49% figure and the metadata check, all of which the article still says.

## Batch 3 (2026-11-17, owner voice-rewrite-2)

Pieces: best-llms-for-coding, vector-embeddings, rag-reranking, documentation-headings, technical-docs, writing-release-notes, and the essay nobody-understands-the-code. They were picked as the highest-impression posts not yet rewritten, counting each post's redirected old slugs with it. The reviewer's 90-day pull by current URL alone gives best-llms 300, vector-embeddings 77, technical-docs 71, documentation-headings 50, writing-release-notes 47 and rag-reranking 9.

### What each piece is built on

| Piece | Spark | What was run |
|---|---|---|
| best-llms-for-coding | Real-SWE 1.1 (October), Kimi K3.1 Pro and Ripple-65B launches, Nathan Lambert on benchmarks (Oct 28), Evan X. Merz (Nov 7) | `cost_per_pass.py`: cost per resolved task from the Real-SWE table |
| vector-embeddings | Hacker News thread on The Last Museum (Oct 22), Apple's retrieval post (Nov 5) | `embed_demo.py` (bge-small on six texts, float and sign-bit search) and `shell_demo.py` (random directions in 3, 384 and 1,536 dimensions) |
| rag-reranking | The page's own March claims, tested | `rerank_demo.py`: one bi-encoder and two cross-encoders on four queries with marked answers, plus timings on 14-word passages |
| documentation-headings | Stripe's webhook guide outline, a promotional Mastodon post by Dedox (Nov 1) used as an example of vendor advice | `curl ... \| grep '^## '` on the Stripe page |
| technical-docs | Matt Cockayne, "Answer first, then everything else" (Nov 11) | His awk one-liner on five vendor pages and two of this site's, results in a table |
| writing-release-notes | OpenSSH 10.6p2 (Nov 5), Ghostty 1.4.0 (Oct 27), GitLab critical patch (Oct 21) | `first_warning.py`: words before each note first names affected users |
| nobody-understands-the-code (essay) | Hacker News threads of Nov 9 and 10, the Claude Code team's review post (Oct 15), Naur 1985 | Nothing; quotes only |

Every script was run in scratch on 2026-11-17 and its printed output pasted into the post. The embedding and reranking runs used fastembed 0.7.4 with onnxruntime 1.19.2 on an Apple M2 CPU.

### Findings that contradicted the old pages

- rag-reranking said a bi-encoder cannot tell error code E-4048 from E-4049 and a cross-encoder can. In the run the bi-encoder ranked E-4048 first, the small cross-encoder scored the neighbours within 0.35 of it, and only bge-reranker-base separated them. Neither reranker fixed the two queries the bi-encoder got wrong.
- vector-embeddings said a 0.7 cosine score in 1,536 dimensions "might be noise". Random directions at that size topped out at 0.126 in two million pairs. The real floor is the model's own: unrelated texts scored 0.37 to 0.57 on bge-small.
- best-llms-for-coding named Claude 4.6 Opus at 80.9% on SWE-bench Verified, "Engram Memory" in DeepSeek V4 and other details with no source. None of its picks appears in Real-SWE 1.1.
- hybrid-search said dense retrieval "has nothing to hold on to for an error code like `ORA-00942`". In the bge-small run the exact code scored 0.75 and ranked first, with a different ORA code at 0.70. The reviewer embedded 100 documents differing only in the code and the right one ranked first 100 times of 100, by a median margin of 0.017. The supported claim, now on the page, is that a dense model ranks the exact code first by a margin too thin to threshold on, and a keyword index matches it outright.

### Skipped, with reasons

| Post | Impressions (90 days) | Why |
|---|---|---|
| engineer-to-writer | 73 | The title and body are a personal career story the repo does not back. Needs Ninad's facts. |
| browser-vector-search, quickstart-guide, release-notes-template | 435, 307, 114 | Unchanged from batch 2: held or newer-rules pages. |

### Videos and figures checked against the new text

- best-llms-for-coding film: narration L2 to L5 recommend SWE-bench Verified, Claude 4.6 Opus, Gemini 3.1 Pro and a small model for autocomplete. The text now uses Real-SWE 1.1 and makes no per-task pick, so the `video:` field was removed from the post after review and the page ships without the film, its transcript and its VideoObject markup. The `video.yaml` description no longer names a benchmark or a pick. Its figure still draws the March pairings; the caption and alt say so.
- documentation-headings film: no mismatch.
- rag-reranking figures: the keyword-exactness drawing shows the textbook case; its caption now reports what the run found. After review the pipeline and cross-encoder captions no longer say the reranker fixes the order or that its score is accurate, the latency figure reads 0.2 to 1.8 s, and the models-providers alt names bge-reranker-base.

### Films to re-render when video work restarts

- ai-memory-management (batch 2b): narration L4, an on-screen caption and the end card title.
- best-llms-for-coding (batch 3): narration L2 to L5 name March models and SWE-bench Verified. The embed is off until it is redone.
- claude-code-memory (batch 6): the narration says CLAUDE.md is "read only at startup, so a mid-session edit waits for the next session". Anthropic's docs say the root file is re-read after `/compact` and subdirectory files load on demand, and the page now says so. The closing line recommends `/memory` for seeing what is loaded, where the docs give `/context all`. The embed is off until it is redone.
- speculative-decoding (batch 5): the narration claims ownership of a model ("my 70B", "So I use speculative decoding"), says a verification pass "costs about the same as making one token", and gives two to three times faster as a general result. The page gives 2X-3X for the paper's T5-XXL run only. The embed came off once hub-build's commit 3b177090 stopped the video and lastmod tests depending on this post; before that, removing the `video` field failed two tests in `tests/test_article_video.py`.
- ai-agent-failures (batch 5): the first twelve seconds argue that agents fail because "the patterns for running them are still being invented" and call it "a distributed systems problem", the thesis the page dropped for Real-SWE's measured causes. The specifics after that still match the page. The embed is off until it is redone.
- ai-agent-taxonomy (batch 5): L1 and L2 say cost and blast radius rise by roughly an order of magnitude per type, which no source backs and the page no longer says. The embed is off until it is redone.

### Notes for the next batch

- The claims audit in CI counts any dollar figure outside a code fence as a candidate, and a changed post may not raise its count. Put the unit in a table header.
- `node render.mjs <one file>` deletes the sibling narrow variant. Run the full render after editing any figure source.
- A new post takes the newest slot in the latest-posts list, which is what had been giving runbook-template its only inbound link. technical-docs now links to it from its body.
- Mastodon tag timelines for `technicalwriting` produced two usable posts this batch. X still returns nothing fetchable.
- Openers used so far in this batch: own earlier page, a search result, a test stated purpose first, a vendor page's outline, a named person's count, a release note, a thread about a post. Do not reuse "On <date> someone".

### Batch 3 review (2026-11-17)

The independent review passed the batch with fixes. What changed after it:

- rag-reranking no longer tells the reader to cut on a score threshold. The four queries show the reranker's scores separating cleanly around the right passage on two and around a wrong passage on the other two, so the page now says a threshold needs checking against marked answers first.
- best-llms-for-coding prints the ten highest Real-SWE rows plus GLM-5.3 and says so, includes Particle-1 in the cost script, and gives model sizes in the local-hardware answer.
- technical-docs opens on the definition again, and its counting script became a table with Cockayne's one-liner. documentation-headings uses a one-line command for the outline. The two pages no longer share example pages.
- vector-embeddings corrects "shares no keyword" (both texts contain "charged") and the description's count of texts.
- writing-release-notes lost its section-closing morals, and its FAQ heading is now "FAQ" so the build emits FAQPage markup.
- fastembed resolves `BAAI/bge-small-en-v1.5` to a quantized ONNX build, which both pages now state.

## Batch 4 (2026-11-17, owner voice-rewrite-2)

Pieces: writing-changelogs, short-term-agent-memory, memory-versioning, voice-agent-memory, lambda-calculus-ai, writing-for-ai-products, and the essay written-by-a-human. The branch sits on origin/main, which already holds batch 3.

### What each piece is built on

| Piece | Spark | What was run |
|---|---|---|
| writing-changelogs | The Claude Code changelog for the 30 days to November 16, Keep a Changelog 1.1.0, Fern's report | `changelog_stats.py`: 20 releases, 1,807 entries, 11 that open with Deprecated or Removed, and a table of entries per label (1,149 under "N bug fixes") |
| short-term-agent-memory | Anthropic's compaction documentation, two November changelog fixes, an Ask HN thread of November 7 | `window_demo.py`: a 400-token window over 40 messages, with and without a pinned rule (tiktoken 0.14.0) |
| memory-versioning | Stroq (Show HN, November 5), Fowler 2005, EU AI Act Article 12, LangGraph persistence docs | `memory_ledger.py`: append-only SQLite ledger with validity derived from the next row, as-of query, hash chain, and five probes: untouched, edited in place, edited with hashes redone, the same checked against an anchor, newest row deleted |
| voice-agent-memory | OpenAI's SIP calling guide (Hacker News, November 6), and the interruption and truncation rules in OpenAI's Realtime guide, LiveKit Agents and Pipecat | `heard_demo.py`: a labelled simulation of truncating a reply to what was played |
| lambda-calculus-ai | DeepMind's AlphaProof Code post (November 10) | `reduce.py`: normal-order reducer with capture-avoiding substitution on six expressions, one of which needs a fresh name that the term already uses |
| writing-for-ai-products | Hacker News thread on perceived model drift (November 8), OpenAI and Anthropic guidance on snapshots and retirements | Nothing; quotes only, plus labelled arithmetic on eval size |
| written-by-a-human (essay) | Hacker News thread of November 13, Ghostty 1.4.0 release notes, Merz | Nothing; quotes only |

### What was removed as unbacked

- short-term-agent-memory: "Every production AI agent I have shipped", context limits for GPT-4o, Claude 3.5 Sonnet and Gemini 1.5 Pro, and two untested code blocks. Its H2 lines were written `##Heading` with no space. They rendered as headings, but `extract_faqs` in `build.py` needs `## FAQ` with the space, so the live page emitted no FAQPage markup.
- memory-versioning: "Building a diagnostic agent for a compliance workflow taught me this", "We needed an append-only audit trail", retention figures of 30 to 90 days and 7 years, the claim that LangGraph checkpoints cannot hold long-term knowledge (its docs describe stores for that).
- voice-agent-memory: untested pipeline code and unsourced VAD and RTP advice. It had the same `##Heading` fault on 13 headings and so no FAQPage markup.
- lambda-calculus-ai: unsourced comparisons with MMLU, HumanEval and ARC-AGI. The page states that no model was run.
- writing-for-ai-products: "I once watched a docs example ... pasted into three internal services", and "Mem0" in the services sentence.

### Review fixes (2026-11-17)

The independent review found 1 blocker, 17 should-fix items and 18 notes. What changed in response:

- memory-versioning: the hash chain is evidence only while its newest hash is held where an editor of the database cannot write. The script drops the stored `valid_to` column, derives validity from the next row, and prints five probes including a rehashed edit and a deleted tail.
- voice-agent-memory: the page reports a three-way difference. OpenAI's Realtime API keeps the played audio and "doesn't provide a truncated transcript.", while LiveKit and Pipecat keep the heard text.
- lambda-calculus-ai: the reducer's fresh-name bug is fixed, and the parser rejects an unclosed parenthesis.
- writing-changelogs: the label regex counts "N bug fixes" and "N improvements", and the body below the first section was rewritten around real entries from the same changelog. The invented pull-request example is gone.
- writing-for-ai-products: both screenshots are out of the page. The image files stay in `static/images/visuals/` and nothing else uses them.
- written-by-a-human: the about-page sentence is quoted exactly, and the claim about the site is cut.
- `verify_quotes.py` fails on an unknown source id and on zero quotes checked. `check_post_quotes.py` fails when no post is given.

### Proposed skips for root to confirm

Pages written on 2026-10-22 or 2026-10-28 under the newer rules, with their own tests and receipts: mcp-server-tutorial, design-doc-template, api-documentation, claude-md, claude-code-subagents, llms-txt, ai-crawlers, aeo-for-developer-docs, runbook-template. They sit in the same class as quickstart-guide and release-notes-template, which are already on the skip list. A voice pass on them would mean re-running each page's test.

### Notes for the next batch

- Algolia's Hacker News API escapes curly apostrophes as `’`; `verify_quotes.py` now decodes those, and requests and decompresses gzip.
- A description regex that ran from `description:` to `status:` deleted the `slug:` line on one post, caught by rule_checker. Replace only up to the next key.
- Openers in this batch: a count from a changelog, a definition, an auditor's question, a call cut off mid-sentence, a single expression, a thread, a release note. Six of seven first drafts opened on a dated artifact, and three were changed.
- The Atlantic returned 403 and theregister.com 404, so neither is quoted.

## Batch 5 (2026-11-17, owner voice-rewrite-2)

Pieces: llm-token-budgets, time-to-first-token, speculative-decoding, agent-error-handling, ai-agent-failures, ai-agent-taxonomy, and the essay red-build-nobody-reads. Root put these six posts first because each claimed experience the repo does not back.

Openings follow Ninad's direction of 2026-11-17: start from something developers already know, state the parallel, say where it breaks.

### What each piece is built on

| Piece | Opens from | Current source | What was run |
|---|---|---|---|
| llm-token-budgets | The AWS billing alarm, which fires after the money is spent | Amazon's ticket-agent figures (Strands blog, November 9), Anthropic's pricing page, Simon Willison on hard caps (October 3) | `token_budget.py`: cost per ticket and a 20-turn chat with and without caching |
| time-to-first-token | Time to First Byte on the web | Artificial Analysis's methodology page, NVIDIA's GLM-5.3 serving post, Modelplane's inference guide | Nothing; quotes only |
| speculative-decoding | Speculative execution in processors | The 2022 paper (arXiv 2211.17192), NVIDIA's GLM-5.3 serving post, Modelplane's inference guide | `spec_tokens.py`: expected tokens per step from the paper's formula |
| agent-error-handling | The fallacies of distributed computing (1994) | Stripe's idempotency reference, Anthropic's tool-use docs, the MCP tools specification | `retry_demo.py`: three retry policies against a payment call that times out after charging |
| ai-agent-failures | The SRE postmortem | Real-SWE's breakdown of failed runs, Michael Lynch on coding agents | `compound.py`: success rate of a chain of steps |
| ai-agent-taxonomy | SAE driving levels and a product named Full Self-Driving at Level 2 | United Airlines' ban on booking agents (CBS News, November 11), Anthropic's workflow and agent split, Simon Willison's definition | Nothing; quotes only |
| red-build-nobody-reads (essay) | A dated post, since ai-agent-failures already opens on the SRE book | Rachel Laycock (October 29) and its Hacker News thread, the SRE pager rule, the Claude Code team's review post | Nothing; quotes only |

### What was removed as unbacked

- llm-token-budgets: "burning $200 on GPT-4 over a single weekend", a RAG pipeline climbing to $1,000 a month, and a price table for models whose prices were not checked.
- time-to-first-token: "Every interactive AI app I have shipped" and "I have watched the same chat UI".
- speculative-decoding: unsourced acceptance claims about boilerplate and JSON.
- agent-error-handling: "Two years of running AI agents in production" and "Nearly every agent implementation I have seen".
- ai-agent-failures: "Across two years of debugging production AI agents", "I have watched this happen for real", and "in my experience".
- ai-agent-taxonomy: "Having spent the last year building agents for production", "talking to teams", and the claim that cost and blast radius climb an order of magnitude per type.

### Decisions the hub plan asked for

- agent-error-handling and ai-agent-failures answer different questions after the rewrite. The first is what the harness should do after one tool call fails; the second is why runs fail, from a measured breakdown. My recommendation is to keep both and skip the 301.
- ai-agent-taxonomy states its boundary with agent-design-space in its closing section: types by how much the agent decides alone, against how to wire a chosen type.

### Notes for the next batch

- `sources.json` is edited in nearly every commit, so a rebase conflicts on each one. Keep source additions out of piece commits and land them in the record commit.
- Batch 4's review lessons were only partly applied before review. Reading output by line position and vague link anchors were gone, and the batch 5 review still found four sentences opening "The same X", eight "[X] covers Y" hand-offs and one closing disclaimer repeated on three pages. All were fixed after that review.
- Two pieces in one batch must not open on the same book. The essay first opened on the SRE book, which ai-agent-failures already uses.

### Batch 5 review fixes (2026-11-17)

The independent review found 2 blockers, 16 should-fix items and 12 notes. What changed in response:

- agent-error-handling: the page said neither protocol tells a client whether a call can be repeated. MCP's schema defines `idempotentHint` and warns clients not to act on annotations from untrusted servers, and Anthropic's tool-use page tells authors to write instructive error messages. The page now cites all three and argues from them: the protocol carries a hint, the hint is untrusted, so the harness owns the retry decision. The title lost "What Nobody Tells You". The script's classifier now treats an unrecognised error as ambiguous, with a fourth run that shows it.
- time-to-first-token: rebuilt around web.dev's own demotion of TTFB and two pieces of arithmetic on borrowed numbers (the spread across effort settings, and TTFT as a share of total latency in NVIDIA's table). Modelplane quotes went from seven to two, and the guide is dated as its page dates itself, October 2026. The title's second half changed because the page argued against it.
- llm-token-budgets: the script prints the saving with the cache lapsing at three rates, down to a 20% loss, and the page states AWS's interest in the post it quotes.
- speculative-decoding: the opening gives the condition under which speculation pays, quoted from the entry it cites, in place of a contrast that the Spectre reference contradicted.
- ai-agent-failures: the page says its counts come from a benchmark, prints the top-ranked model's different breakdown, and moves the figure to the section it illustrates.
- ai-agent-taxonomy: the two definitions no longer "fall in the same place", since Anthropic's cuts across the ladder; the five types are named in the second paragraph.
- red-build-nobody-reads: corrected to what Laycock reports (who took part, "80% done", "frequently red"), which changelog list held which entry, and that Willison's remedy is the collapsed block.
- Openings: the review found one device in one shape across six pieces. The known thing now sits first, second or runs through the piece, no opening has a sentence announcing where a parallel breaks, and the three undated references carry dates.
- Hub model: the branch was rebased onto the hub commit. All seven pieces link their hub in the first 200 words and declare siblings and bridges; the essay sits in the coding agents hub with a line in its pillar file.

## Hub retrofit (2026-11-17, owner voice-rewrite-2)

A links-only batch on the 38 posts the worklist marks "done or newer", which is the 29 rewrites plus the pages on the skip list. No argument, quote or script changed.

- Every one of the 38 links its hub in the first 200 words, in a sentence written for that page.
- Banned anchors replaced: "a separate essay" (three posts), "October article", two anchors ending in "piece", two full-title anchors, and "release notes" pointing at two URLs.
- Siblings declared and same-hub links added where a post had fewer than two: shorter-documentation, writing-changelogs, writing-for-ai-products, rag-vs-memory, memory-versioning, claude-md, coding-models-new-code-vs-change, nobody-understands-the-code, llm-structured-outputs.
- writing-for-ai-products lost its link to agent-harnesses so its bridges no longer outnumber its same-hub links.
- Inbound links added from six posts outside the 38 or from batch 5 pieces: devtools-documentation, documentation-template, speculative-decoding, ai-agent-taxonomy, ai-agent-failures, agent-error-handling.
- One stale reference fixed: release-notes-template pointed at a worked example that batch 4 removed from writing-changelogs.

`audit_clusters --strict` reports 0 errors and no warning on any of the 38 or on the batch 5 pieces. The 111 warnings left are on posts the voice rewrite has not reached.

### Retrofit review fixes (2026-11-17)

The review found 2 blockers, 8 should-fix items and 6 notes. Two added sentences were false about their target (the MCP tutorial builds a two-tool server; the hub has no page for every documentation type) and are corrected. Ten hub sentences sat between a paragraph and the one that refers back to it and moved to the end of the introduction. Seven that described the site's navigation now make a claim about the subject. Two links to lambda-calculus-ai claimed it tests a habit it does not; one is gone and the other says only that a script grades the answers, so that post has one inbound link from its hub and keeps the warning. Bridge reasons on eleven links now describe the link.

Rule for later batches: the hub link goes where the paragraph flow allows it, and never between a paragraph and the one that refers back to it.

## Standing rule: no "sell" about his own work (2026-11-17)

Ninad, through root: "'I sell' noo lol pls no sells. I help with... or something like this is better." First-person copy about his services never uses sell, sells or selling. Write "I run AI-ready documentation audits", "I help teams with", "I write technical content for a living" and the like. Sentences about other companies selling things are unaffected.

## Batch 6 (2026-11-17, owner voice-rewrite-2)

Pieces: hyperagents-memory, coding-agent-memory, claude-code-memory, memory-compression, memory-serialization, multi-agent-vs-single-agent, and the essay agent-memory-evidence. The branch sits on origin/main after the hub retrofit.

### What each piece is built on

| Piece | Opens from | Current source | What was run |
|---|---|---|---|
| hyperagents-memory | A dated paper, since the finding is the surprise | Meta's Hyperagents paper, arXiv 2603.19461, revised November 1 | `hyper_memory.py`: the MemoryTool printed in the paper's appendix, with a labelled loader |
| coding-agent-memory | The HTTP cookie (1994) | Vendor docs for Claude Code, Codex, Gemini CLI and Cursor; agents.md; Atuin Threads (October 27, Hacker News November 11) | Nothing; quotes only |
| claude-code-memory | Memento | Anthropic's memory documentation and a changelog fix of October 26 | Nothing; quotes only |
| memory-compression | `.gitignore` | Anthropic, "The components of agent memory" (November 6) | Nothing; quotes only |
| memory-serialization | Zork's save feature, via BYTE in 1981 | The same Anthropic post; Mads Thines on a shared memory format (November 7) | `state_roundtrip.py`: a versioned state record, migrated and checked for stale facts |
| multi-agent-vs-single-agent | Fowler's Monolith First (2015) | Anthropic and Cognition, both June 2025 and dated on the page; a guide discussed on Hacker News on November 5 | Nothing; quotes only |
| agent-memory-evidence (essay) | Wikipedia's citation needed tag | Thines's post and its Hacker News thread; the Anthropic post | Nothing; quotes only |

### What was removed as unbacked

- hyperagents-memory: the whole page. It described a three-layer architecture with parameters such as `max_turns` that the paper and repository do not contain, plus "I watched one of my early agents". The figure drew the same invention and is redrawn.
- coding-agent-memory: a Django migration anecdote, a SQLite database at `~/.claude/memory.db` and a `--memory` flag. Anthropic's docs describe neither; auto memory lives in a per-project directory of Markdown files.
- claude-code-memory: invented example memory files and the statement that CLAUDE.md is never re-read during a session. The docs say subdirectory files load on demand and the root file is re-read after compaction.
- memory-compression: "Around week three", a memory payload at 40% of the window, a 30-day half-life "I used", and a support agent "I watched".
- memory-serialization: the morning-after restart story and "the production systems I have worked on".
- multi-agent-vs-single-agent: "The first time I split a single agent into two", an event-bus incident and "One failure burned me badly".

### Decisions the hub plan asked for

- coding-agent-memory and claude-code-memory stay as two pages. The first now answers a cross-tool question, which Search Console recorded once at position 2 for the query "why does my coding agent forget everything as soon as i start a new session" (one impression in 90 days; the URL's average position is 30.5); the second is the Claude Code reference.

### Films to check

- claude-code-memory: the narration says CLAUDE.md is "read only at startup, so a mid-session edit waits for the next session." The page no longer says this, and the docs say the root file is re-read after `/compact`.

### Notes for the next batch

- `sources.json` and the audit register were kept out of the piece commits in this batch and land in the record commit, so a rebase of the stack no longer conflicts on every commit.
- Openers used: a film, a dated paper, a protocol, a dotfile, a game, an essay, a wiki tag. The Anthropic memory post feeds three pieces and the essay, each from a different section of it.

### Batch 6 passes before review (2026-11-17)

Applied before the first review, from the batch 5 and retrofit findings:

- Openings: no sentence announces where a parallel breaks. After the review, claude-code-memory, coding-agent-memory and multi-agent-vs-single-agent give the answer first and the known thing second, hyperagents-memory gives its finding and then the Gödel machine, and memory-compression and memory-serialization keep the known thing first and close the introduction on a preview.
- Hub model: each piece links its hub at the end of its introduction, above the first H2, and declares the siblings and bridges its body links. Stale bridge entries left by the old bodies are removed, and every reason describes its link.
- The essay is in the agent-memory hub with `primary_query: none` and a line in `content/pillars/agent-memory.yaml`. memory-versioning links it from the end of its hash-chain section, and memory-serialization links it too.
- A wrong claim caught in self-check: coding-agent-memory said Codex was the only tool with a documented size cap. Claude Code's memory page sets one of 40,000 characters per file, in a 200K session, on instruction files that load on demand. Both pages now say so.

### Batch 6 review fixes (2026-11-17)

The independent review found 3 blockers, 15 should-fix items and 12 notes. What changed in response:

- coding-agent-memory said only Claude Code's docs describe agent-written notes. That was true of the one page per tool it cited and false of the tools: Codex has opt-in memories generated from earlier chats, and Gemini CLI has a memory tool plus an experimental Auto Memory feature that asks for approval. The page is rebuilt on all four tools' memory documentation, with a column for who writes notes and what the default is.
- claude-code-memory lost its film embed, and five statements were corrected against Anthropic's page: the resume exception, `/context all` for what loaded, the `modified` date as the check on stale auto memory, the 4 MiB limit on files loaded at launch, and the scope of the "plain markdown" quote.
- multi-agent-vs-single-agent argued a conclusion Walden Yan had published himself on April 22, 2026. The page now cites that follow-up, credits him with the rule that only one agent should write, and adds a second vendor's confirmation and two cautions of its own.
- memory-compression answers both meanings of its query, with a section on in-session compaction, and replaces a table that rag-vs-memory already prints with the contract-facts case from the same post.
- memory-serialization no longer repeats a quote and gloss from rag-vs-memory, and its sentence about coding tools matches what the linked page now says.
- hyperagents-memory opens its second paragraph on the Gödel machine, says the repository holds no memory code, and notes that the agent's own key naming avoided the overwrite the page demonstrates.
- The essay credits Thines with the three places he raises provenance, stops short of claiming the Anthropic post isolates the effect, and opens on xkcd 285.

### Rules added by this review

- A comparison across vendors checks each vendor's documentation index before saying a product lacks something. One page per vendor is not enough.
- No opening may reuse a known thing that a hub page or another post already opens on. Check the ledger below before writing.
- No table, quote or gloss is repeated from another page on the site. Link to the page that has it, or make a different point.
- A page answers what its primary query asks, near the top, in the sense a searcher means.

### Ledger of opening devices

Hub pages (owned by the pillar files): technical-documentation, the Unix Programmer's Manual of 1971; ai-search-optimization, robots.txt and Martijn Koster, 1994; developer-experience, a 2008 Stack Overflow founding post; ai-agents, Unix pipes, 1973; agent-memory, the HTTP cookie, 1994; rag, Okapi BM25 at TREC-3, 1994; coding-agents, the editor war; ai-engineering, the 64K intro and fr-08.

Posts, by batch. Batch 5: AWS billing alarm (llm-token-budgets); web TTFB and Core Web Vitals (time-to-first-token); CPU speculative execution and Spectre (speculative-decoding); fallacies of distributed computing (agent-error-handling); the SRE postmortem (ai-agent-failures); SAE driving levels (ai-agent-taxonomy); the SRE pager rule, placed second (red-build-nobody-reads).

Batch 6: Memento (claude-code-memory); `.env` files and dotenv (coding-agent-memory); the Gödel machine (hyperagents-memory); `.gitignore` (memory-compression); Zork's save feature (memory-serialization); Fowler's Monolith First (multi-agent-vs-single-agent); xkcd 285 and the citation needed tag (agent-memory-evidence).

Reserved by the hub plan for new spokes, so not available to rewrites: Netscape badges, RSS, the Joel Test, `man`, the keywords meta tag, featured snippets, the Netcraft survey, the PageRank toolbar, "Docs or it didn't happen", Readme Driven Development, Chesterton's fence, RFC 1, the GitLab outage of 2017, PC LOAD LETTER, The IT Crowd, Python 2 to 3, gofmt, Procida's 2017 talk, No Silver Bullet, Swagger, Jekyll, Ballmer's chant, the Slashdot effect, High Scalability, the `ls` man page, FizzBuzz, Getting Real, Write Like You Talk, Eternal September, Kawasaki at Apple, the Bitcoin paper, Ethernet, the Confused Deputy, SQL injection and xkcd 327, left-pad, the Language Server Protocol, the password anti-pattern, Dapper, the Heisenbug, chroot, Selenium, sudo and xkcd 149, Brooks's law, CGI, JavaScript in 2016, pre-commit hooks, dotfiles, Royce's 1970 paper, git worktree, Linus's law, Stack Overflow copying, Vim against Emacs, tabs against spaces, kernel patch series, TCP packets, grep, "X is dead", "Just use Postgres", PageRank, `.bash_history`, benchmarketing, Karlton's two hard things, memcached, bit rot, MP3.

## Standing direction: spoken prose (2026-11-17)

Ninad, through root: "writing needs to have a bit of spoken fillers to feel like it was written as we speak rather than like rigid prose." It applies from the batch 6 fixes onward.

- Write the body in the spoken form of the writing skill (`references/spoken.md`, `spoken-connectors.md`, `spoken-example.md`), which is that skill's stated exception to the core's ban on orienting sentences.
- Use sentence-opening connectors matched to the relationship (So, Now, And, But, Which means, Here's why), an occasional question that the next sentence answers, contractions, a short aside in the author's voice, and "you" for the reader.
- Keep a light hand. No run of the same opener, no connector that misstates the relationship, and never the banned softeners.
- The first sentence under each H2 still answers the heading in plain words. Sentences that only point at a table or announce a quote are still cut.
- Facts, sources, code, ranking and hub rules are unchanged, the query is still answered in the first two paragraphs, and the build still caps a paragraph at two sentences.
- After batch 6 ships, the 36 pieces already live get a light pass for connectors and rhythm only, as its own batch.

## Titles: what real ones do (research of 2026-11-17)

Ninad's direction, verbatim: "the titles for the recent articles you wrote are pure AI slop ... Read titles in the noema magazine or paul graham or simon willison or the hundreds of trending essays on hackernews daily. You'll find a pattern which is basically an experience that someone is sharing with passion."

The 100 titles below were fetched on 2026-11-17 from the Hacker News API, simonwillison.net, paulgraham.com and noemamag.com.

| Source | Date | Title | URL |
|---|---|---|---|
| Hacker News front page, 2026-11-17 | 2026-11-15 | Japan's Hometown Tax (2018) | https://www.kalzumeus.com/2018/10/19/japanese-hometown-tax/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | BugMeNot has closed | https://www.bugmenot.com/ |
| Hacker News front page, 2026-11-17 | 2026-11-17 | Why 3dfx 1 cards had such a washed out color output? | https://twitter.com/id_aa_carmack/status/2122478083319992513 |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Chemistry is Actually Geometry | https://chillphysicsenjoyer.substack.com/p/chemistry-is-actually-geometry |
| Hacker News front page, 2026-11-17 | 2026-11-16 | The Fossils That Haunted Lovecraft | https://paleonerdish.wordpress.com/2026/10/30/halloween-special-xiv-the-fossils-that-haunted-lovecraft/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | What is w2rt6byl5nf1opmc-a.com? | https://jack.cab/blog/siterate |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Grazing sheep in fields with solar arrays | https://news.cornell.edu/stories/2026/10/sheep-grazing-solar-fields-offers-farmers-economic-ecological-gains |
| Hacker News front page, 2026-11-17 | 2026-11-15 | Why did modems have speakers? (2019) | https://retrocomputing.stackexchange.com/questions/11765 |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Windows 11 is collecting data on which coding agents and developer tools you use | https://xusheng.dev/posts/windows-coding-agent-telemetry/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Test/verification technique effectiveness with Astra | https://danluu.com/astra-testing/ |
| Hacker News front page, 2026-11-17 | 2026-11-14 | Formal Verification Is Not Verifiable | https://alperenkeles.com/posts/formal-verification-is-not-verifiable/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Stop Filming in Log? | https://digitalfilms.wordpress.com/2026/11/15/stop-filming-in-log/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Do Repeat Yourself | https://arcentry.com/blog/do-repeat-yourself/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Squircles | https://linebender.org/wiki/curves/squircle/ |
| Hacker News front page, 2026-11-17 | 2026-11-17 | Mem Is Shutting Down | https://get.mem.ai/blog/mem-is-shutting-down |
| Hacker News front page, 2026-11-17 | 2026-11-16 | My Quest to push native Three.js quality match AAA Game Engines | https://ben3d.ca/blog/building-the-aaa-lighting-pipeline-in-threejs |
| Hacker News front page, 2026-11-17 | 2026-11-17 | Running coding agents without handing them my credentials | https://blog.antonio.cx/running-agents-with-lend |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Rust changed me as a developer | https://blog.startifact.com/posts/how-rust-changed-me/ |
| Hacker News front page, 2026-11-17 | 2026-11-16 | Interpreting claims that a theorem is correct because it was checked in Lean | https://xenaproject.wordpress.com/2026/11/12/and-the-proof-is-checked-in-lean/ |
| Hacker News, top of the week | 2026-11-12 | Jensen Huang resigns | https://apnews.com/article/nvidia-megaspeed-china-singapore-huang-5403f152a601cf82ce939f1d24fffa0f |
| Hacker News, top of the week | 2026-11-14 | SpaceX catches the Starship to end Flight 15 | https://www.spacex.com/launches/starship-flight-15 |
| Hacker News, top of the week | 2026-11-13 | FAA issues national ground stop – lifted 4.5 hours later | https://www.nbcnews.com/news/us-news/faa-orders-nationwide-ground-stop-departing-flights-reasons-safety-rcna609247 |
| Hacker News, top of the week | 2026-11-16 | Carnegie Mellon is putting computer science courses on YouTube for free | https://www.cs.cmu.edu/learn/ |
| Hacker News, top of the week | 2026-11-11 | Tim Peters has died | https://discuss.python.org/t/in-memoriam-tim-peters-1952-2026/110028 |
| Hacker News, top of the week | 2026-11-15 | All AI-generated code should be Open Source | https://jakub.jankiewicz.org/blog/ai-code-open-source/ |
| Hacker News, top of the week | 2026-11-11 | Nvidia is preparing to oust Jensen Huang | https://www.wsj.com/business/nvidia-is-preparing-to-oust-nvidia-ceo-jensen-huang-30f421ad |
| Hacker News, top of the week | 2026-11-10 | Smart home devices should work without the internet | https://docodethatmatters.com/home-automation-overnight-success/ |
| Hacker News, top of the week | 2026-11-12 | Service degradation on Microsoft 365 | https://status.cloud.microsoft/ |
| Hacker News, top of the week | 2026-11-14 | Nvidia allegedly engineered scarcity by funding AI startups to buy its GPUs | https://www.techpowerup.com/354814/nvidia-allegedly-engineered-scarcity-by-funding-ai-startups-to-buy-its-gpus |
| Hacker News, top of the week | 2026-11-11 | My AI agents found an unmapped Maya site? | https://pietromiotti.com/latest/maya-site |
| Hacker News, top of the week | 2026-11-12 | Anthropic IPO | https://ipo.anthropic.com/us/ |
| Hacker News, top of the week | 2026-11-14 | Lovable apps expose passport details and more than 200K private messages | https://www.crissyfield.de/research/lovable-en/ |
| Hacker News, top of the week | 2026-11-11 | AWS emulator | https://github.com/aws/aws-emulator |
| Hacker News, top of the week | 2026-11-13 | LibreOffice actually works 365 days a year | https://twitter.com/LibreOffice/status/2121205272479998268 |
| Hacker News, top of the week | 2026-11-10 | .name Grandfathered | https://neil.fraser.name/news/2026/11/10/ |
| Hacker News, top of the week | 2026-11-12 | Rust 1.100 | https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/ |
| Hacker News, top of the week | 2026-11-16 | Many of Amazon’s Black Friday and Cyber Monday “deals” offered no savings | http://groundworkcollaborative.org/news/amazons-decoy-deals-groundwork-investigation-reveals-nearly-1-in-3-black-friday-and-cyber-monday-deals-advertised-by-amazon-offered-no-savings-to-shoppers-nearly-1-in-10-w/ |
| Hacker News, top of the week | 2026-11-16 | How to make almost anything | https://pub.cba.mit.edu/863.26/site/ |
| Hacker News, top of the week | 2026-11-16 | Qwen4-Max | https://qwen.ai/blog?id=qwen4-max |
| Hacker News, top of the week | 2026-11-13 | Nvidia employees petition to bring back Jensen Huang | https://www.wired.com/story/nvidia-employees-petition-for-jensen-huangs-return/ |
| Hacker News, top of the week | 2026-11-12 | Reverse engineering my Coway air purifier to ditch the cloud | https://scottjg.com/posts/2026-11-11-reverse-engineering-my-coway-air-purifier-to-ditch-the-cloud/ |
| Hacker News, top of the week | 2026-11-16 | Technical issue at JPMorgan Chase triggers online banking delays for US banks | https://apnews.com/article/bank-outage-chase-wells-fargo-truist-50fee2693c22f597fa6ca51a97ef2cda |
| Hacker News, top of the week | 2026-11-12 | Show HN: My $300 embroidery machine needed a subscription, so I built my own app | https://github.com/simpsoka/zigzag |
| Hacker News, top of the week | 2026-11-11 | United Airlines bans AI agents from booking flights on behalf of travelers | https://www.cbsnews.com/news/united-airlines-bans-ai-agents-booking-flights/ |
| Hacker News, top of the week | 2026-11-10 | AlphaProof Code | https://deepmind.google/blog/introducing-alphaproof-code/ |
| Hacker News, top of the week | 2026-11-10 | Why get an expensive Pi when I have an old phone? | https://so.long.thanks.fish/why-pi-when-i-have-an-old-phone/ |
| Hacker News, top of the week | 2026-11-15 | Microsoft 365 outage leads to chlorine gas poisoning of 15 hotel guests | https://www1.wdr.de/nrw/rheinland/rhein-erft-kreis/technischer-defekt-chlor-phantasialand-100.html |
| Simon Willison | 2026-11-09 | Locating the source of a mysterious beep with Claude | https://simonwillison.net/2026/Nov/9/mysterious-beeps/ |
| Simon Willison | 2026-11-09 | Hide your slop PR descriptions behind <details><summary> | https://simonwillison.net/2026/Nov/9/details-summary/ |
| Simon Willison | 2026-11-03 | Qwen 3.8 27B on my laptop can interpret model weights, too | https://simonwillison.net/2026/Nov/3/qwen-can-interpret-model-weights/ |
| Simon Willison | 2026-11-02 | The U.S. Census Bureau and “Super Intelligence” | https://simonwillison.net/2026/Nov/2/census-bureau-super-intelligence/ |
| Simon Willison | 2026-10-28 | The October inflection point for vibe game development | https://simonwillison.net/2026/Oct/28/vibe-game-development/ |
| Simon Willison | 2026-10-20 | Battle Drones - a vibe coded RTS with audio-based multiplayer | https://simonwillison.net/2026/Oct/20/battledrones/ |
| Simon Willison | 2026-10-12 | Hello Python 3.15, goodbye 3.10, and now I can use 3.11 | https://simonwillison.net/2026/Oct/12/python-3-15/ |
| Simon Willison | 2026-10-09 | A new feature for my blog, built using my voice | https://simonwillison.net/2026/Oct/9/built-using-my-voice/ |
| Simon Willison | 2026-10-07 | Claude Haiku 5.5 | https://simonwillison.net/2026/Oct/7/claude-haiku-5-5/ |
| Simon Willison | 2026-10-03 | We're going to need default hard budget caps on pretty much everything | https://simonwillison.net/2026/Oct/3/default-hard-budget-caps/ |
| Simon Willison | 2026-09-29 | OpenAI DevDay 2026 live blog | https://simonwillison.net/2026/Sep/29/openai-devday-2026-live-blog/ |
| Simon Willison | 2026-09-22 | Claude Opus 5.5, GPT-6 Sol, GPT-6 Luna, and a new price war | https://simonwillison.net/2026/Sep/22/opus-and-sol-and-luna/ |
| Simon Willison | 2026-09-21 | Jev introduces a new shape of LLM - System One, aka Decision Models | https://simonwillison.net/2026/Sep/21/jev/ |
| Simon Willison | 2026-09-12 | Generating running routes with GPT-6 Astra and ChatGPT Work | https://simonwillison.net/2026/Sep/12/astra-running-routes/ |
| Simon Willison | 2026-Sep-01 | Claude Fable 5.1 made me a really nice animated pelican | https://simonwillison.net/2026/Sep/1/claude-fable-5-1/ |
| Simon Willison | 2026-Sep-02 | Claude’s new system prompt really doesn’t want to reproduce song lyrics | https://simonwillison.net/2026/Sep/2/claudes-new-system-prompt/ |
| Simon Willison | 2026-Sep-04 | OpenAI’s rogue agents were caught communicating via public wikis | https://simonwillison.net/2026/Sep/4/rogue-agent-wikis/ |
| Simon Willison | 2026-Sep-04 | The Pelican comparison grid for Astra is pretty interesting | https://simonwillison.net/2026/Sep/4/astra-pelicans/ |
| Simon Willison | 2026-Aug-04 | New release of LLM adds support for reasoning traces, OpenAI Responses, server-side tools, and smarter logging | https://simonwillison.net/2026/Aug/4/new-release-of-llm/ |
| Simon Willison | 2026-Aug-05 | One-shotting a Raccoon Heist game using Claude Fable 5 | https://simonwillison.net/2026/Aug/5/raccoon-heist/ |
| Simon Willison | 2026-Aug-07 | Now we have a timeline of the OpenAI accidental attack against Hugging Face | https://simonwillison.net/2026/Aug/7/openai-timeline/ |
| Simon Willison | 2026-Jul-05 | sqlite-utils 4.0rc2, mostly written by Claude Fable (for about $149.25) | https://simonwillison.net/2026/Jul/5/sqlite-utils-fable/ |
| Simon Willison | 2026-Jul-07 | sqlite-utils 4.0, now with database schema migrations | https://simonwillison.net/2026/Jul/7/sqlite-utils-4/ |
| Paul Graham | May 2025 | Good Writing | https://paulgraham.com/goodwriting.html |
| Paul Graham | October 2024 | Writes and Write-Nots | https://paulgraham.com/writes.html |
| Paul Graham | September 2024 | Founder Mode | https://paulgraham.com/foundermode.html |
| Paul Graham | March 2024 | The Best Essay | https://paulgraham.com/best.html |
| Paul Graham | October 2023 | Superlinear Returns | https://paulgraham.com/superlinear.html |
| Paul Graham | July 2023 | How to Do Great Work | https://paulgraham.com/greatwork.html |
| Paul Graham | January 2023 | How to Get New Ideas | https://paulgraham.com/getideas.html |
| Paul Graham | November 2022 | The Need to Read | https://paulgraham.com/read.html |
| Paul Graham | September 2022 | What I've Learned from Users | https://paulgraham.com/users.html |
| Paul Graham | February 2022 | Putting Ideas into Words | https://paulgraham.com/words.html |
| Paul Graham | June 2021 | How to Work Hard | https://paulgraham.com/hwh.html |
| Paul Graham | June 2021 | A Project of One's Own | https://paulgraham.com/own.html |
| Paul Graham | March 2021 | Write Simply | https://paulgraham.com/simply.html |
| Paul Graham | February 2021 | What I Worked On | https://paulgraham.com/worked.html |
| Noema | 2026-11-12 | A Generation Revolts | https://www.noemamag.com/a-generation-revolts |
| Noema | 2026-11-13 | Serbia’s Experiment: Combining Democracy & Meritocracy | https://www.noemamag.com/serbias-experiment-combining-democracy-meritocracy |
| Noema | 2026-09-29 | Noema’s AI Reading List | https://www.noemamag.com/noemas-ai-reading-list |
| Noema | 2026-11-10 | When AIs Become Unruly Swarms | https://www.noemamag.com/when-ais-become-unruly-swarms |
| Noema | 2026-11-05 | How Aristotle Anticipated The AI Era | https://www.noemamag.com/building-the-new-equilibrium-economy |
| Noema | 2026-11-03 | In Praise Of Japan’s Failure To Keep Up | https://www.noemamag.com/in-praise-of-japans-failure-to-keep-up |
| Noema | 2026-08-06 | Why Is Everyone In Tech So Sad? | https://www.noemamag.com/why-is-everyone-in-tech-so-sad |
| Noema | 2025-09-02 | The Last Days Of Social Media | https://www.noemamag.com/the-last-days-of-social-media |
| Noema | 2024-11-12 | The Making Of A New American Epidemic | https://www.noemamag.com/the-making-of-a-new-american-epidemic |
| Noema | 2026-06-18 | The Mars Delusion | https://www.noemamag.com/the-mars-delusion |
| Noema | 2026-07-14 | Why We Demand Perfect Machines Yet Tolerate Human Carnage | https://www.noemamag.com/why-we-demand-perfect-machines-yet-tolerate-human-carnage |
| Noema | 2025-02-12 | A Radical New Proposal For How Mind Emerges From Matter | https://www.noemamag.com/a-radical-new-proposal-for-how-mind-emerges-from-matter |
| Noema | 2026-01-14 | The Mythology Of Conscious AI | https://www.noemamag.com/the-mythology-of-conscious-ai |
| Noema | 2026-05-12 | We May Be Entering A Second Axial Age | https://www.noemamag.com/we-may-be-entering-a-second-axial-age |
| Noema | 2025-08-12 | How We Became Captives Of Social Media | https://www.noemamag.com/how-we-became-captives-of-social-media |
| Noema | 2026-04-09 | How To Future-Proof Your Career In The Age Of AI | https://www.noemamag.com/why-a-liberal-arts-education-will-soon-be-more-valuable-than-ever |

### What these titles do

- They name one thing. A release, a product, a bug, a question or an act: "Jiff 1.0: A datetime library for Rust", "BugMeNot has closed", "Squircles", "What I Worked On".
- Personal posts say what the writer did, in the first person and usually the present participle or simple past: "Reverse engineering my Coway air purifier to ditch the cloud", "Running coding agents without handing them my credentials", "Locating the source of a mysterious beep with Claude", "Rust changed me as a developer".
- A question title is the writer's real question: "Why get an expensive Pi when I have an old phone?", "What is w2rt6byl5nf1opmc-a.com?", "Why Is Everyone In Tech So Sad?".
- An opinion is stated once, flat, as a claim someone could disagree with: "Smart home devices should work without the internet", "All AI-generated code should be Open Source", "We're going to need default hard budget caps on pretty much everything".
- Paul Graham's are two to five words and name the subject or the task: "Write Simply", "Founder Mode", "How to Do Great Work", "The Need to Read".
- Noema's are a noun phrase or a question with one idea in it: "The Mars Delusion", "The Last Days Of Social Media", "In Praise Of Japan's Failure To Keep Up".
- Length runs from one word to about twelve. A colon appears only to attach a product name to its description ("Jolt – Clojure that speaks C").

### What they never do

- Two sentences in one title.
- A paired contrast ("X proves little. Y proves more", "X got better. Y is still").
- A metaphor offered as the thesis ("A is a B").
- A colon followed by a clever second half.
- An aphorism, or a title that states the conclusion as a rule for everyone.

### Rule for every title from now on

A title is what a person would put on their own post about something they did, read, found or changed their mind about. It may be first person only for what the piece did. No two-sentence titles, no paired contrast, no metaphor as thesis, no colon followed by a kicker, no aphorism. An explainer keeps its search query and stays plain. Slugs do not change.

## Pitch notes: Fly.io's patterns (research of 2026-11-17)

Ninad's direction, verbatim, on the work note: "such a bullshit paragraph. It won't even grab people from the web. Read Fly.io's blog you'll see how they add a simple pitch paragraph at the top of every article." And on shape: "not the same shape always, pick the patterns from fly.io's blogs and use that."

Lead paragraphs read from fly.io/blog on 2026-11-17 and from saved copies in `ninadpathak-research/flyio-blog-2026-10-23/`:

- `/blog/sprites-mcp/`: "Sprites are disposable cloud computers. They appear instantly, always include durable filesystems, and cost practically nothing when idle. They’re the best and safest place on the Internet to run agents and we want you to create dozens of them ."
- `/blog/kurt-scott-money-sprites/`: "We’re Fly.io, a public cloud platform that is both our favorite way to put an app on the Internet and our favorite way to safely let a frontier agent coding harness cook. This is a post about our company, the future, and Sprites, which are computers for agents that you can check out right now."
- `/blog/litestream-writable-vfs/`: "I’m Ben Johnson, and I work on Litestream at Fly.io. Litestream is the missing backup/restore system for SQLite. It’s free, open-source software that should run anywhere, and you can read more about it here ."
- `/blog/fly-io-has-gpus-now/`: "We’re Fly.io, we’re a new public cloud that lets you put your compute where it matters: near your users. Today we’re announcing that you can do this with GPUs too, allowing you to do AI workloads on the edge. Want to find out more? Keep reading. AI is pretty fly AI is apparently a bit of a thing (ma"
- `/blog/scaling-llm-ollama/`: "We’re Fly.io. We have powerful servers worldwide to run your code close to your users. Including GPUs so you can self host your own AI. Open-source self-hosted AI tools have advanced a lot in the past 6 months. They allow you to create new methods of expression (with QR code generation and Stable Di"
- `/blog/the-risks-of-building-apps-on-chatgpt/`: "We’re Fly.io. We put your code into lightweight microVMs on our own hardware around the world . Check us out —your app can be deployed in minutes. The topic of “AI” gets a lot of attention and press. Coverage ranges from apocalyptic warnings to Utopian predictions. The truth, as always, is likely so"
- `/blog/sentry-partnership/`: "We’re Fly.io. We put your code into lightweight microVMs on our own hardware around the world , close to your users. We partnered with Sentry to bring error and performance monitoring to your apps. Deploy your first app, and automatically get a year’s worth of credits to Sentry’s Team Plan credits."
- `/blog/flydotio-heart-js/`: "Fly.io is a great place to run fullstack applications. For most programming languages, there is a defacto default fullstack framework. For Ruby, there is Rails. For Elixir, there is Phoenix. For PHP there is Laravel. For Python, there is Django. If you don’t know where to look, Node.js appears to be"
- `/blog/shipping-logs/`: "Fly.io runs apps (globally) in just few commands. That means a lot of log output! Centralizing logs is important. Fire up an app and follow along as we see just how easy it can be. Nearly all of our apps are puking output. Sometimes, it’s intentional. Often this output is in the form of structured l"
- `/blog/launching-redis-by-upstash/`: "We’re Fly.io. We put your code into lightweight microVMs on our own hardware around the world , close to your users. Redis by Upstash is managed Redis living right next door to your Fly.io apps. Check us out —your app and database can be running close to your users within minutes. We love databases"
- `/blog/love-letter-react/`: "We’re Fly.io. React, Phoenix, Rails, whatever you use: we put your code into lightweight microVMs on our own hardware in 26 cities and counting. Check us out —your app can be running close to your users within minutes. It’s hard to overstate the impact React has had since its release in 2013. For me"
- `/blog/introducing-litefs/`: "Fly.io runs apps close to users by taking containers and upgrading them to full-fledged virtual machines running on our own hardware around the world. We’re also building an open-source distributed file system for SQLite called LiteFS which is pretty cool too. Give us a whirl and get up and running"
- `/blog/sqlite-virtual-machine/`: "Fly.io runs apps close to users around the world, by taking containers and upgrading them to full-fledged virtual machines running on our own hardware around the world. Sometimes those containers run SQLite and we make that easy too. Give us a whirl and get up and running quickly. SQL is a weird con"
- `/blog/the-serverless-server/`: "I’m Will Jordan, and I work on SRE at Fly.io. We transmogrify Docker containers into lightweight micro-VMs and run them on our own hardware in racks around the world, so your apps can run close to your users. Check it out —your app can be up and running in minutes. This is a post about how services"
- `/blog/logbook-2022-06-01/`: "We’re Fly.io. We take container images and run them on our hardware around the world. It’s pretty neat, and you should check it out ; with an already-working Docker container, you can be up and running on Fly in well under 10 minutes. Here’s our latest changelog. Looking back over the week, our foru"
- `/blog/fly-machines/`: "Fly.io turns Docker images into running VMs on physical servers all over the world. We built an API for booting VMs very quickly . Here’s what you need to know. Fly Machines are VMs with a fast REST API that can boot instances in about 300ms. Our proxy can boot Fly Machines for you, and you can shut"
- `/blog/a-foolish-consistency/`: "Fly.io runs applications by transmogrifying Docker containers into Firecracker micro-VMs running on our hardware around the world, connected with WireGuard to a global Anycast network. Yours could be one of them! Check us out : from a working container, your app can be running worldwide in minutes."
- `/blog/our-user-mode-wireguard-year/`: "We’re Fly.io . We run container images on our hardware around the world, linked to our Anycast network with a WireGuard mesh. It’s pretty neat, and you should check it out . You can be up and running on Fly.io in single-digit minutes. That’s the last thing we’re going to say about how great Fly.io i"
- `/blog/self-service-account-deactivation/`: "Fly.io runs apps close to users, by transmuting Docker containers into micro-VMs that run on our own hardware around the world. This is a post about deactivating accounts on Fly.io, but if you’re new, you might like to try us out first; you can be up and running in just a couple of minutes . We’ve j"
- `/blog/how-safari-ruined-my-tuesday/`: "Fly.io runs apps close to users, by transmuting Docker containers into micro-VMs that run on our own hardware around the world. This is a post about a bug in Safari, but if you just want to ship a Phoenix app, the easiest way to learn more is to try it out ; you can be up and running in just a coupl"
- saved copy `old-carving-the-scheduler-out-of-our-orchestrator`: "We’re Fly.io, a global sandwich-rating company with a hosting problem. Even if you don’t have a sandwich to rate, you might benefit from the hosting platform we built. Check it out: with a working Docker image, you can be up and running on Fly.io in just minutes."
- saved copy `old-api-tokens-a-tedious-survey`: "We’re Fly.io. This post isn’t about Fly.io, but you have to hear about us anyways, because my blog, my rules. Our users ship us Docker containers and we transmute them into Firecracker microvms, which we host on our own hardware around the world. With a working Dockerfile, getting up and running will take you less than 10 minutes."
- saved copy `design-and-implementation`: "We’re Fly.io, and this is the place in the post where we’d normally tell you that our job is to take your containers and run them on our own hardware all around the world. But last week, we launched Sprites, and they don’t work that way at all."
- saved copy `old-docker-without-docker`: "We’re Fly.io. We take container images and run them on our hardware around the world. It’s pretty neat, and you should check it out; with an already-working Docker container, you can be up and running on Fly in well under 10 minutes."
- saved copy `litestream-vfs`: "I’m Ben Johnson, and I work on Litestream at Fly.io. Litestream is the missing backup/restore system for SQLite. It’s free, open-source software that should run anywhere, and you can read more about it here."

Patterns, with the posts that show each:

1. Company first, plain, then an invitation: `the-risks-of-building-apps-on-chatgpt`, `love-letter-react`, `old-docker-without-docker`.
2. Company first with a joke: `old-carving-the-scheduler-out-of-our-orchestrator` ("a global sandwich-rating company with a hosting problem"), `old-api-tokens-a-tedious-survey` ("my blog, my rules").
3. Author first: `litestream-vfs` ("I'm Ben Johnson, and I work on Litestream at Fly.io"), `the-serverless-server` ("I'm Will Jordan, and I work on SRE at Fly.io").
4. What the product does, mechanism first: `a-foolish-consistency` ("Yours could be one of them!"), `fly-machines`, `introducing-litefs`.
5. A pitch that leans into the post's subject: `how-safari-ruined-my-tuesday` ("This is a post about a bug in Safari, but if you just want to ship a Phoenix app"), `self-service-account-deactivation`, `launching-redis-by-upstash`.
6. The self-aware aside: `our-user-mode-wireguard-year` ("That's the last thing we're going to say about how great Fly.io is in this post"), `design-and-implementation` ("this is the place in the post where we'd normally tell you").
7. The one-line version: `shipping-logs` ("Fly.io runs apps (globally) in just few commands."), `flydotio-heart-js` ("Fly.io is a great place to run fullstack applications.").
8. Tied to an announcement: `fly-io-has-gpus-now`, `sentry-partnership`.

Rules for Ninad's notes: true to the about page, the services pages and his confirmations; plain spoken register; two or three sentences; one link to a /services/ page or /contact/; never "I sell", never "my portfolio has the work", no credential-dropping, no forced tie to the article. A real conflict of interest is disclosed once in the body where it bears on the argument.

## Standing rule: show the reference, don't explain it (2026-11-17)

Ninad, on an opening that described an xkcd comic and then said why the joke works: "If you have to explain why the joke works, you have failed the joke and people will already leave."

- When a piece opens on a joke, comic, meme, screenshot or any cultural reference, show the thing itself and go straight to the point in the next sentence.
- Never describe an image in prose when the image can be shown.
- Never write a sentence that explains the reference or why the reader knows it ("the joke works because", "everyone knows", "developers already know").
- If a reference needs explaining to this readership, choose another.
- For an analogy, state the known thing, then the new thing, and leave out the sentence that says they are alike.


## Work notes rewritten as pitch notes (2026-11-17, branch voice-notes)

Ninad approved three patterns and corrected a fourth, and told us "not the same shape always". Every post's `work_note` follows these rules after the independent review.

- Confirmed by Ninad as work he takes: handling a company's changelog ("If you'd rather someone else handle the changelogs while you work on the product, that's what I do" is his own sentence) and writing release notes. Both may be offered in a note.
- Notes written for one post, 33 of them: all of technical-documentation, developer-experience and ai-search-optimization, plus `mcp-server-tutorial`. The 29 that lean on the post's subject use five shapes, and no shape or sentence frame is on more than a third of them: the post, the offer, then the name (Ninad's own example, 6 posts); the reader's situation as a question (5); the problem as a plain statement (9); name first (5); the method first with what the client gets (4).
- Plain and author-first notes, 51 posts in the five AI topics: ten wordings, each linking `/services/freelance-technical-writer-for-ai-companies/`. They are assigned so no post shares a wording, or a wording that opens the same way, with the next post on its topic page or with a related card at the foot of the article.
- Every note says "freelance" and carries a hiring phrase ("hire", "work with me", "get in touch", "tell me", "ask me", "talk to me"), which may sit in the link label.
- The offer is work the repo backs: developer documentation, tutorials, technical articles, AI-ready documentation audits, changelogs, release notes. For AI companies say "tutorials and technical articles", which the AI-companies page shows, and not "documentation". On posts about design docs, runbooks, accessibility and technical SEO the note offers the nearest backed work.
- Where the repo backs a concrete promise, state it: "I build the example and run it before I draft, so your engineers review working code", and "you can rerun every finding with the four tools I built and published". No number, turnaround or client count is invented.
- `tests/test_article_work_notes.py` fails closed on: a missing note; a link outside `/services/`, `/services/<slug>/` and `/contact/`; no "freelance"; no hiring phrase; any form of sell, sold, seller or sale; a digit or a count of years; a capitalised name outside a short allowed list; a first-person verb offering accessibility, SEO, design docs or runbooks; the name outside one "I'm Ninad Pathak"; a job title followed by a third-person verb. Neighbours come from the pillar files, notes in the three per-post topics must be unique, and no note may sit on more than seven posts.
- A note says what its post is about today. When a later batch rebuilds a page, reread its note against the new page.

## Visible wording: topic, not hub (2026-11-17)

The reader sees "topic". The lead, fact, argument and bridge text of every `content/pillars/*.yaml` now says "this topic" and "the [query] topic". Field names (`hub:`), audit output and JSON-LD ids keep "hub". New prose for readers never says "hub".


## Standing rule: an essay is his opinion of what he read (2026-11-17)

Ninad, on a stretch of `nobody-understands-the-code`: "okay while the direction is right, it feels like quote after quote after quote. Essays need to be my opinion of the posts that I read from across the web. If I read something I am not going to keep quoting the person or the author. I am going to write what I feel what I think etc and use the quotes to support my arguments or contrast their arguments or state what was mentioned for clarity sake."

- His view leads every section of an essay, in first person and plainly: what he thinks of what he read, what he makes of it, where he disagrees and why.
- A quote appears only to support that view, to set up something he argues against, or to pin down exact wording when the wording is the point. Everything else is paraphrased accurately in his own words, with a link.
- Never two quotes in a row, never a paragraph that is only a quote plus attribution, and never a source narrated sentence by sentence ("It says", "then asks", "The reply opens", "The post brings").
- Working limit: one short quote per section, and a reader can delete every quote and still follow the argument.
- Opinions and judgments need no source. Facts about the world keep their link. An experience he has not had still cannot be claimed, so the opinion comes from reading and reasoning and says so ("I think", "I don't buy", "what struck me").
- Accuracy now comes from faithful paraphrase and a link. `sources.json` still records the exact passage behind each paraphrase so a reviewer can check it.
- Explainers from batch 7 on take a lighter version: the page's own explanation and judgment carry it, quotes are occasional, and no section is one source quoted back.

### His own positions, to build three essays on

State these as his view. Do not soften them or stretch them into claims he did not make.

- `nobody-understands-the-code`, first statement: "yes people need to know what the codebase does at the very least. if it's just code written by someone with zero understanding of what's happening underneath it, there's no way someone can pinpoint what function or file actually caused an issue because the context doesn't exist in the developer's head."
- `nobody-understands-the-code`, his correction of how that was summarised: "debugging isn't a problem but knowing what the code does so we can actually work more effectively on the code is helpful. If we extrapolate the future, then we probably don't need humans to remember what code does but it's always going to be beneficial to know what happened and how things were shipped." Read together: knowing what the code does lets people work on it more effectively, and having no context has a cost; he expects people probably won't need to hold the code in their heads, so he does not flatly oppose Anthropic's position; the essay's centre is that a record of what happened and how things were shipped stays valuable either way. It is not a debugging piece, and the title still fits.
- `written-by-a-human`: "Written by human only makes me want to read it as a human but considering agents read changelogs more than humans do at this point, i think written by humans is going to be a fading aspect of the world unless someone really cares. It will be good for people that want developers to come back to them to read stories." The label is an invitation to a human reader; it is fading because changelog readers are increasingly agents; it keeps its value for teams that want developers to return for the writing. A statement that agents read changelogs more than people needs its source or is marked as his impression.
- `agents-reading-docs` and the llms.txt article: "llms.txt is good to have but there's no evidence that llms actually fetch that." Present Fern's data beside it, and if the data contradicts the sentence as worded, tell root the exact conflict.


## Essays rewritten as opinion (2026-11-17, branch voice-essays)

The six live essays were rewritten to the rule above: his view leads each section, sources are paraphrased with a link, and each section keeps at most one short quote. Quoted phrases of three words or more, before and after: agents-reading-docs 16 to 3; coding-models-new-code-vs-change 9 to 4; nobody-understands-the-code 17 to 5; written-by-a-human 10 to 2; red-build-nobody-reads 16 to 4; agent-memory-evidence 13 to 3. The passages behind the paraphrases are in `sources.json`, including the ones the essay review found missing and this branch added (Fern's conditional advice and named llms.txt count, the Ahrefs study, and passages from Merz, Anthropic, Thines, Willison and Luu).

Positions taken, for Ninad to confirm where they are not his own words:

- `coding-models-new-code-vs-change`: models are good at new code and poor at changing code without breaking it; a ranking by solve rate answers only the first; paying for more effort did not buy the second in the one run published; so a "best coding model" claim is a claim about new code until a benchmark prints regression passes.
- `red-build-nobody-reads`: a red build spends a team's attention, which Google's pager rule budgets at a few times a day; Laycock is right that production evidence takes time, and the build light need not wait for it; ration what reaches a person.
- `agent-memory-evidence`: a shared memory format matters less than whether each note says how the agent knew; the source field should be required, and a note without one should be read as a guess.
- `written-by-a-human`: beyond his three points, the essay keeps one section marked as a further thought, that a last-tested date and a checkable line prove more to a technical reader than the label does. That view is reasoned, not his words, and the essay ends on his own closing point.
- `nobody-understands-the-code`: beyond his two statements, the essay adds the split between what code does and why, taken from Naur, and the sentence that a team copying Anthropic's explainers without the people who remember the decisions should expect what Merz describes. Both are reasoned from the sources.
- `agents-reading-docs`: his sentence is "llms.txt is good to have but there's no evidence that llms actually fetch that." Fern's report counts 448,667 fetches of llms.txt in September on the docs it hosts, with Claude Code the largest named source, so the sentence as worded is contradicted for coding agents on one vendor's API docs. The same report says ChatGPT, Gemini and Perplexity fetch only HTML, and Ahrefs found 97% of files unrequested across 137,210 domains. The essay says "good to have, and the evidence that models fetch it is still thin" in both places it states the view, and prints 32,812 named Claude Code requests beside the 448,667 total, with the rest counted as agent requests by route.

## Batch 7 (2026-11-17, owner voice-rewrite-2)

Written under every rule above, including the lighter quote rule for explainers: the page's own explanation carries each section and a quote stays only where the wording is the point.

| Post | What it now rests on | Run or checked |
| --- | --- | --- |
| llm-context-windows | Lost in the Middle (2023), Chroma's context rot report (2025), Anthropic's context window docs | quotes re-fetched |
| agent-vs-ai-assistant | Vals AI's refund experiment (October 15), a post on Claude Duet (October 29) | quotes re-fetched; table paraphrases the report |
| agent-design-space, retitled "AI Agent Design Patterns" | Anthropic's Building effective agents (2024), Fadurudeen's multi-agent guide | figure redrawn as three groups; grid labelled as the author's |
| technical-writing-for-engineers, retitled "Technical Writing for Engineers" (the only recorded query on the URL has no "80/20") | Simplified Technical English, Karpathy's 80% tip of October 2 through the STE80 Humanizer README, Google's technical writing course including its Paragraphs unit | `sentence_rules.py` run, output on the page; renamed so it is not taken for the STE80 project's own `ste_check.py` |
| documentation-velocity, retitled "Documentation ROI and Engineering Velocity" | DORA's 2022 documentation table, DORA's metrics guide, Stripe's 2018 Developer Coefficient, Anthropic's code review post | every figure re-fetched; unverified 2.4x, 2.5x and 25% cut |
| devtools-documentation, retitled "How Developers Judge Devtools Documentation Before They Buy" | State of Docs 2026 purchase section (GitBook), three vendor quickstarts fetched November 17 | `quickstart_probe.py` run, output on the page |
| agents-on-call-runbooks (new essay, technical-documentation) | SigNoz's post of February 28 and its Hacker News thread of October 30, this site's runbook test | opinion-led, one quote |

Opening devices added to the ledger: conventional memory and the 640K line (llm-context-windows); the Office Assistant, placed second (agent-vs-ai-assistant); the Gang of Four's Design Patterns (agent-design-space); Simplified Technical English (technical-writing-for-engineers); the bus factor (documentation-velocity); "Nobody got fired for buying an IBM" (devtools-documentation); Bainbridge's Ironies of Automation, credited to the post that uses it (agents-on-call-runbooks).

Films that no longer match their page. After the batch review all three were unembedded (the `video` field removed and each `video.yaml` given a plain description) and stay on the re-render list: agent-vs-ai-assistant (the narration opens on a ticket-routing anecdote the page no longer has), agent-design-space (the narration describes five patterns the page no longer lists), devtools-documentation (the first line states that startups lose deals over docs, and the page now says no source counts one).

The three April screenshots of vendor quickstarts are no longer embedded on devtools-documentation. The files stay in `static/images/visuals/`.

Position taken in the new essay, for Ninad to confirm: the deskilling risk is real and sharpest for juniors, the post's evidence is borrowed from medicine and aviation, and the cheap remedy it leaves out is making the agent write a short account of each incident it closes for a person to read.

Rules the batch 7 review added:

- When a page stops making a claim, check the film, the pillar line, the money page and every inbound anchor for the same claim before reporting.
- A known thing in an opening is stated in his own words with the link on the noun. A Wikipedia citation with a quoted fragment is one shape among several and no batch may use it on more than two pieces.
- The vendor-interest disclosure stays, and it does not open on "Now," more than once in a batch.
- A script printed on a page asserts a known string on each page it fetches and exits non-zero without it.
- A source's limits paragraph is reported whole when the page leans on the numbers it limits.

