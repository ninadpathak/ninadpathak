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
