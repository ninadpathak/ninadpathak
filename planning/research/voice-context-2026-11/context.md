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

