# Voice repair plan: revived articles

Date: 2026-08-17

## Audit rules

This review covers every first-person claim and every quantitative claim in the ten requested articles. A record may cover adjacent sentences or a table when they make one evidentiary claim. Counts at the end use one record as one claim unit.

- **KEEP** means the line is an attributed fact, transparent arithmetic, a clearly marked example, a verifiable reference to Ninad's published work, or editorial judgment he has earned as an engineer turned technical writer.
- **REWRITE** means the idea is useful but the existing attribution, precision, or framing is not defensible. The quoted replacement is the complete replacement for the cited line or range.
- **CUT** means no replacement. The claim either invents experience, rests on evidence that tests its own premise, or adds first person without adding information.

Artifact labels distinguish a real benchmark artifact from decorative output. A chart with hard-coded values is not an artifact. A script that generates the fixture and then verifies the property used to generate it is not independent evidence.

## Source ledger for replacement lines

- Anthropic, [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)
- Anthropic, [Claude Code memory](https://code.claude.com/docs/en/memory)
- OpenAI, [Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI, [text-embedding-3-large model page](https://developers.openai.com/api/docs/models/text-embedding-3-large)
- Stripe, [Stripe's payments APIs: the first 10 years](https://stripe.com/blog/payment-api-design)
- Stripe, [2025 annual letter](https://stripe.com/en-no/annual-updates/2025)
- H2O paper, [Heavy-Hitter Oracle for Efficient Generative Inference](https://arxiv.org/abs/2306.14048)
- StreamingLLM paper, [Efficient Streaming Language Models with Attention Sinks](https://arxiv.org/abs/2309.17453)
- vLLM, [PagedAttention implementation](https://github.com/vllm-project/vllm)

## 1. `how-anthropics-contextual-retrieval-changes-rag-architecture.md`

**Artifact status:** No local benchmark artifact, but the measurements are attributed to Anthropic's official post and appendix. They are research claims, not presented as Ninad's measurements.

- **REWRITE | L4-6**: “I walk through the mechanism, the benchmark, and the part of the RAG pipeline it changes.” First person adds nothing. Replacement: “The mechanism changes what gets indexed before the RAG pipeline runs a query.”
- **KEEP | L16**: “revenue grew by 3%” is Anthropic's example; “top-20 retrieval failure by 49%” is linked to Anthropic's result.
- **KEEP | L18, L24-26**: “What I like...” and “the part I keep coming back to... I think...” are analysis of a sourced result, not a claimed implementation.
- **REWRITE | L30**: “I still see people treat the chunk as if it were a clean unit of knowledge.” The observation is unnecessary. Replacement: “A common indexing mistake is to treat the chunk as a clean unit of knowledge.”
- **KEEP | L36, L42**: “tell me why it exists” is ordinary reader perspective; “I wrote about” points to a real internal article.
- **KEEP | L50-55**: The six numbered items enumerate a pipeline. They are not measurements.
- **KEEP | L64**: “50 to 100 tokens” is explicitly attributed to Anthropic.
- **KEEP | L72**: “the ones I trust” is earned technical judgment.
- **REWRITE | L76**: “A reranker, when I add one, starts from a stronger candidate pool.” It implies an implementation. Replacement: “A reranker then starts from a stronger candidate pool.”
- **KEEP | L92-94**: “I do not read this...” and “My reranking piece” are interpretation and a verifiable authorship claim.
- **KEEP | L104-112**: The 5.7%, 3.7%, 2.9%, 1.9%, 35%, 49%, and 67% results are all attributed to Anthropic.
- **KEEP | L108, L114, L118**: “I read,” “I trust,” and “I believe” explain how Ninad weighs the sourced evidence.
- **KEEP | L122-126**: `1 - recall@20`, `@10`, `@5`, top 20, top 150, and top 20 are attributed to Anthropic's appendix.
- **KEEP | L130-132**: “I would still run my own evals” is a recommendation, and the 49% figure remains explicitly tied to another corpus.
- **KEEP | L143, L147, L153-160**: These are editorial priorities and questions, not claims that Ninad ran a system.
- **REWRITE | L145**: “Almost every RAG conversation I sit in...” is a sweeping personal observation. Replacement: “RAG discussions often concentrate on the live request path because query-time mistakes are visible in a trace.”
- **REWRITE | L164**: The 100-page, 400-chunk scenario is arbitrary precision. Replacement: “Without prompt caching, contextualizing every chunk resends the same source document for each chunk.”
- **KEEP | L171-173**: The token-cost judgment is earned; “more than 2x” and “up to 90%” are attributed to Anthropic.
- **REWRITE | L175**: “unless I add reranking” implies a build. Replacement: “Query-time retrieval barely changes unless reranking is added.”
- **KEEP | L181, L185, L187-189**: These are recommendations and explicitly illustrative examples. `max_retries = 3` is example code, not a measured setting.
- **KEEP | L205, L209-218**: The reaction, agreement, 200,000-token threshold, and decision criteria are sourced analysis or earned judgment.
- **REWRITE | L220**: “after I have attached every field I have” implies a specific implementation. Replacement: “Contextual Retrieval earns its keep when the raw chunk still reads as anonymous after available metadata has been attached.”
- **REWRITE | L224**: “what I store” and “how I sort” add false ownership. Replacement: “Contextual Retrieval changes what gets stored, and reranking changes how retrieved candidates are sorted.”
- **REWRITE | L226-228**: “ones I have watched happen,” top 100, top 20, and “when I split it” turn a general failure pattern into unsupported eyewitness evidence. Replacement: “One failure mode retrieves the right chunk but ranks it below the candidates passed to the model. Another never retrieves the right chunk because chunking removed too much identity from it.”
- **KEEP | L232-260, L264**: “I would,” “my signal,” “my rollout,” and “I expect” are clearly recommendations and judgment. The numbered rollout is a sequence, not measurement.

## 2. `kv-cache-eviction-accuracy.md`

**Artifact status:** `static/js/kv_cache_benchmark.py` exists, but it is a NumPy simulation, not a Llama, GPU, Triton, LongBench, VRAM, or thermal benchmark. It marks high-weight tokens as heavy hitters, chooses the “needle” from that same high-weight set, and lets H2O retain top-weight tokens. Perfect H2O recall therefore follows from the fixture. It tests nothing the setup did not already assume. All hardware, model, latency, capacity, and LongBench numbers are bare.

- **REWRITE | L4-6**: “I benchmarked... reaching 90% pruning with zero recall loss” claims a real benchmark that did not occur. Replacement: “A research-led comparison of KV-cache eviction strategies, including their accuracy risks and implementation trade-offs.”
- **REWRITE | L15**: “Measuring Accuracy vs. KV Cache Eviction” promises measurements the artifact cannot provide. Replacement title: “Context Engineering as Heap Management: Accuracy Risks in KV Cache Eviction”.
- **CUT | L30**: “I wanted a number for this, so I benchmarked...” claims a real benchmark that did not occur.
- **REWRITE | L20-22**: “128k... Llama 3 70B... 20GB” and “1M... 160GB” are bare and configuration-dependent. Replacement: “KV-cache memory grows with sequence length, layer count, KV-head count, head dimension, batch size, and precision. Calculate it from the deployed model's actual configuration before setting a context limit.”
- **REWRITE | L26-28**: “a tiny fraction” and “near-infinite sequences on consumer hardware” overstate the cited work. Replacement: “H2O and StreamingLLM show that retaining high-importance tokens and attention sinks can reduce KV-cache pressure, with quality depending on the model and task.”
- **CUT | L39-41**: The 100% recall, 80% pruning, 16GB M2 Air, “massive context,” and “swap death” claims are not backed by the script.
- **REWRITE | L47**: The exact 70B, 80-head, 128-dimension configuration is unsourced and the precision term is wrong for FP16. Replacement: “For a decoder-only transformer, KV-cache size is determined by layers, KV heads, head dimension, bytes per value, sequence length, and batch size.”
- **CUT | L49, L53, L55**: The 160KB per token, 100,000 tokens, 16GB, 100x disk penalty, and five-times-A100 capacity claims are bare personal measurements.
- **REWRITE | L61, L63**: “I evaluated” and “my implementation” falsely own the comparison. Replacement: “The comparison covers sliding-window, importance-based, and random eviction. H2O uses accumulated attention as a utility signal and protects high-scoring tokens when the budget fills.”
- **KEEP | L65**: The 20% cache result is attributed to the H2O paper.
- **CUT | L71-73**: “my baseline,” “I expected,” and “the data backed that up” refer to a circular simulation and support the absolute claim that semantic importance is the only useful metric.
- **REWRITE | L84-86**: The M2 and “benchmark” framing inflate the artifact. Replacement: “The included NumPy script simulates a 4,096-token sequence. It does not run a language model or measure hardware, and its needle is selected from the same high-weight tokens that H2O is designed to retain.”
- **CUT | L90-94, L98, L107-109**: The full pruning table, 100% at 90%, 5%, four initial tokens, perfect recall, 90% VRAM, and reproduction claim all come from the self-confirming simulation.
- **CUT | L117-119**: No artifact backs 80 measured layers, the 40% and 10% layer split, or the extra 15% memory reduction.
- **REWRITE | L123, L134**: The 3D visual is a conceptual illustration, not observed attention evidence. Replacement: “Attention-sink research shows that retaining initial tokens can stabilize streaming generation. The visualization is illustrative and does not report measurements from this article.”
- **REWRITE | L136**: “I've watched a team...” is falsifiable eyewitness evidence. Replacement: “A bad eviction policy can resemble a prompting or sampling failure when it drops tokens the model still needs.”
- **REWRITE | L148**: The 50% threshold is arbitrary. Replacement: “Compaction should run only after fragmentation is high enough to justify the copy cost.”
- **CUT | L158, L168, L178, L188**: The custom Triton kernel, 20% slowdown, 10x context, distributed tests, 5%/95% precision split, 80% eviction, 92% memory fall, 1% LongBench result, and model-specific 90%/70% thresholds have no code, logs, or data.
- **KEEP | L190**: “I profile its attention map first” is a defensible recommendation, provided it is read as process advice rather than a completed benchmark.
- **REWRITE | L210**: The 400%/1,000-token ablation is not sourced in the sentence. Replacement: “The StreamingLLM paper shows that removing attention sinks destabilizes generation as the stream grows.”
- **CUT | L222, L228-230**: The 80% sorting reduction and every M2 thermal, clock, latency, swap, million-token, and 12GB result are bare.
- **REWRITE | L234**: “Every megabyte I saved...” falsely claims the run. Replacement: “Cache memory saved can instead be used for model weights or concurrency.”
- **CUT | L255-257**: The 80%, 5x, A100 user counts, 4,096-token heap, one-million-token session, and iPad claim are derived from unsupported premises.
- **REWRITE | L269**: “how I've turned dense inference infrastructure...” claims work not demonstrated here. Replacement: “My work page shows how I explain dense infrastructure topics for developer-tool companies.”
- **CUT | L277**: The four-token personal test and claim about up to 32 tokens for GPT-4 are unsupported and speculate about a closed architecture.

## 3. `how-memory-works-in-claude-code.md`

**Artifact status:** No artifact. More importantly, the article's SQLite database, `--memory` flag, `.claude/memory.md`, and precedence model conflict with Anthropic's current documentation. Claude Code currently documents `CLAUDE.md` files plus auto memory stored under `~/.claude/projects/<project>/memory/`, with `MEMORY.md` as the entry point.

- **CUT | L19, L23**: “I spent the last few weeks auditing...” and “turned me from someone...” are invented experience and add no evidence.
- **REWRITE | L17-21**: The opening's “three distinct places” includes a nonexistent SQLite layer. Replacement: “Claude Code carries instructions across sessions through `CLAUDE.md` files and auto memory. Conversation context itself remains session-bound.”
- **REWRITE | L27**: “Sonnet 4... 200K tokens” is version-specific and stale. Replacement: “Each session starts with a fresh context window whose size depends on the selected model.”
- **REWRITE | L29-31**: “Opus 4... smaller but deeper” is vague and “unless you specifically enable persistent memory” does not describe the current product. Replacement: “Conversation context disappears when the session ends. Project instructions and auto memory persist because Claude Code stores them on disk.”
- **REWRITE | L33**: “I have tested this directly.” Replacement: “A fresh session does not retain the previous conversation unless the relevant information was saved in `CLAUDE.md` or auto memory.”
- **KEEP | L65**: The new-hire rule is earned editorial judgment.
- **REWRITE | L92**: The witnessed team story is unsupported. Replacement: “A project `CLAUDE.md` can tell Claude Code to use an async database client and avoid blocking calls, so that constraint is present in each session.”
- **REWRITE | L89**: “takes ~3 minutes” is unneeded precision inside an example file. Replacement inside the example: “Onboarding: run `make setup`.”
- **CUT | L94**: “The mistakes stopped that same afternoon” is an unsupported result from the invented team story.
- **CUT | L116**: The claimed verification of `memory.db` and `--memory` contradicts current Anthropic documentation.
- **CUT | L112-154**: The database heading, commands, schema, output tuples, and week-later retrieval story describe a SQLite feature Anthropic does not document. This range must be removed as one factual unit, not softened.
- **REWRITE | L157-163**: The four-level precedence and SQLite layer are false. Replacement: “Claude Code loads `CLAUDE.md` files from managed, user, project, and local scopes. Anthropic documents the current scopes and load behavior in its [memory guide](https://code.claude.com/docs/en/memory).”
- **REWRITE | L166**: The auto-memory path and behavior are wrong. Replacement: “Claude Code stores auto memory under `~/.claude/projects/<project>/memory/`. `MEMORY.md` is the entry point, and topic files hold additional notes.”
- **CUT | L168**: The observed 800-line, dated monorepo memory file is invented and conflicts with the documented startup load limit.
- **REWRITE | L169-189**: The purportedly “real” memory file contains dates and counts without provenance. Replacement for its lead-in: “An illustrative memory file might look like this:” The example may remain only after that label and after its path is updated to the documented auto-memory location.
- **CUT | L214, L216**: The SQLite write behavior and comparison to other agent systems rest on a nonexistent Claude Code layer.
- **REWRITE | L224**: The weekly personal practice is unsupported and names the wrong interface. Replacement: “Use `/memory` to inspect loaded memory and remove instructions that no longer match the codebase.”
- **CUT | L252**: The 50K-token versus 10-line refactoring test has no artifact.
- **KEEP | L254**: “we use PostgreSQL, FastAPI, and Redis” is clearly sample project guidance, not a claim about Ninad's stack.
- **REWRITE | L255**: “500 lines of project history spanning three years” is arbitrary. Replacement: “A concise file with current instructions gives the agent less irrelevant context to sort through than a long project history.”
- **CUT | L262**: “I have tested extensively” adds false evidence to an internal link.
- **REWRITE | L265-268**: The article invents a 90-day database rule and claims a monthly habit. Replacement: “Anthropic says Claude Code loads the first 200 lines or 25KB of `MEMORY.md` at startup. Review `CLAUDE.md` and auto memory regularly so stale instructions do not survive refactors.”
- **CUT | L272-304**: The 30-day shell check and SQLite monthly-query workflow operate on the wrong path and nonexistent database.
- **KEEP | L290**: The conflicting SQLAlchemy/asyncpg example is explicitly framed as an example.
- **KEEP | L326**: “a decision framework I use” is earned judgment.
- **CUT | L338-340**: The SQLite recommendation and claimed production comparison are factually inapplicable to Claude Code and unsupported.
- **CUT | L308-322**: The fixed four-step load order and the claim that an RS256 memory is written to SQLite are not in Anthropic's current memory model.
- **KEEP | L361**: “advice I give” is an earned technical-writing judgment.
- **REWRITE | L373**: The 100K-line threshold is arbitrary and the auto-memory path is wrong. Replacement: “For a large codebase, keep `CLAUDE.md` concise and use imports or scoped files to document module boundaries and ownership.”
- **CUT | L381-388, L413-417**: The FAQ claims about database conflict resolution, reset commands, and an unencrypted `~/.claude/memory.db` describe a store Anthropic does not document.
- **KEEP | L393**: “my post” links to a real internal article.

## 4. `embedding-models-compared.md`

**Artifact status:** No scripts, dataset, raw results, or linked benchmark repo. Product dimensions can be kept only when linked to provider documentation. All claimed production tests, latency results, recall results, and team outcomes are bare.

- **KEEP | L20**: “We call these lists of numbers embeddings” is inclusive explanatory voice, not personal evidence.
- **CUT | L28**: “I benchmarked these models on production workloads... serving real users” is the damaging claim the article cannot support.
- **REWRITE | L82**: “teams I've worked with” is unnecessary. Replacement: “High cosine scores become misleading when a team treats them as universal rather than calibrating them on its own corpus.”
- **REWRITE | L87**: The 0.82/0.79 comparison is an unlabeled hypothetical. Replacement: “For example, two nearby similarity scores may correspond to different relevance judgments. Calibrate the cutoff with labeled queries instead of copying a universal score.”
- **REWRITE | L105**: The 500-word limit is arbitrary. Replacement: “Split long documents where topic or section boundaries change rather than forcing one vector to represent several ideas.”
- **KEEP | L43**: The 1,536 dimensions for `text-embedding-3-small` are a provider specification. Add the OpenAI embeddings guide as the source in the sentence.
- **REWRITE | L51**: “trillions of tokens” is an unsourced training-data quantity. Replacement: “The model learns those features from patterns in its training data.”
- **KEEP | L65-73**: L2, unit length, zero, one, and negative one are mathematical definitions, not experimental measurements.
- **KEEP | L118**: The 3,072-to-1,536 size ratio is transparent arithmetic when the provider dimensions are sourced.
- **REWRITE | L120**: “Watching models... taught me a lot” claims experience without information. Replacement: “Higher-dimensional output also increases similarity-computation and storage cost.”
- **KEEP | L126-128**: “we” and “us” describe common use of projection tools; 2D is intrinsic to the illustration.
- **REWRITE | L149-151**: The 1,536-to-128 claim and “most semantic meaning” need evaluation. Replacement: “OpenAI's embeddings API accepts a `dimensions` parameter for shortening `text-embedding-3` outputs. Measure retrieval quality at each candidate size on your own corpus.”
- **CUT | L155, L159**: The claimed 75% dimension cut, less-than-5% accuracy loss, four-to-one storage result, and 10%/90% signal split are bare personal results.
- **KEEP | L171, L183-185**: 3D and 1,536D are used for conceptual contrast; the 0.7 statement is explicitly hypothetical and followed by a calibration warning.
- **REWRITE | L179**: “I mentioned earlier” adds nothing. Replacement: “This crowding can make semantically distinct vectors land on similarly high cosine scores.”
- **REWRITE | L201**: “I've found Cohere's models hard to beat” presents an unsupported evaluation. Replacement: “For high-cost retrieval errors, compare providers on a labeled slice of the actual contracts or filings rather than relying on a general leaderboard.”
- **KEEP | L213-215**: 32-bit floats, 1,536 dimensions, 6KB, one million vectors, and 6GB are transparent arithmetic, excluding index overhead.
- **REWRITE | L217**: The 32-to-8-bit and 75% storage arithmetic is valid, but “almost no loss” is bare. Replacement: “Scalar quantization reduces each component from 32 bits to 8 bits, cutting raw vector storage by 75%. Measure recall loss on the target corpus.”
- **KEEP | L223**: One bit versus 32 bits and the 32x raw-storage ratio are transparent arithmetic.
- **KEEP | L219**: The 256 levels follow directly from eight-bit quantization. The “industry standard” claim still needs a source or removal during factual editing.
- **REWRITE | L229**: The 10x oversampling rule is arbitrary. Replacement: “A binary index can retrieve a wider candidate set, which a second pass reranks with full-precision vectors.”
- **REWRITE | L266, L270**: The 150-to-300ms and sub-50ms claims are bare. Replacement: “Provider and self-hosted latency varies with region, batching, model, and hardware. Measure end-to-end query latency in the deployment environment.”
- **REWRITE | L286**: The 8,192, 32K, and 128K limits are volatile and unsourced. Replacement: “Input limits vary by model and provider. Check the current model documentation before setting a chunking policy.”
- **CUT | L290**: “My tests show a significant decay” has no artifact.
- **REWRITE | L292**: The 32K-to-1,536 and 200-person analogy uses unearned precision. Replacement: “Packing several topics into one vector dilutes the signal for any single passage.”
- **REWRITE | L321-324**: “over 100 languages” needs a provider source, and “I've used this... five languages” invents a project. Replacement: “Cohere documents multilingual support for its multilingual embedding models. Validate the languages in the target corpus because coverage is not the same as equal retrieval quality.”
- **REWRITE | L345**: “512 vectors per document” is a model-specific example without a source. Replacement: “Late-interaction models store multiple token-level vectors per document, which improves matching granularity at a substantial storage cost.”
- **REWRITE | L362**: Sub-50ms is bare. Replacement: “Open-source models are attractive when the team already operates suitable inference hardware and can measure latency itself.”
- **KEEP | L368**: The 32x statement follows the one-bit versus 32-bit arithmetic, but should say “raw vector storage” rather than total index cost.
- **CUT | L374**: “Having helped several teams...” is unverified social proof. The recommendation in the second half can stand without it.
- **REWRITE | L378**: “a baseline in twelve months” is a bare forecast. Replacement: “The field changes quickly, so build for re-embedding and provider replacement.”

## 5. `shared-vs-isolated-memory-multi-agent.md`

**Artifact status:** No implementation or trace. The architecture discussion can stand as judgment, but the two claimed team stories and production observations cannot.

- **REWRITE | L16-18**: The last-year, three-agent, document-processing story and “my first choice” are unsupported. Replacement: “Consider a three-stage document pipeline: one agent extracts fields, one validates them, and one writes the summary. Shared memory looks efficient until concurrent writes make the result hard to audit.”
- **KEEP | L24**: “how I think through it now” is a decision framework, not claimed evidence.
- **KEEP | L53**: “the reason I reach for isolated memory” is earned architectural judgment.
- **REWRITE | L55**: “I can replay... on the first try” overpromises a result. Replacement: “Explicit handoffs make the pipeline easier to replay because each stage has a bounded input artifact.”
- **REWRITE | L61**: “a Python service my team owns” invents ownership. Replacement: “If the extractor and validator are separate services with independent release cadences, isolated handoffs reduce coupling.”
- **REWRITE | L65**: “I see most” and “My summary agent” invent observation and implementation. Replacement: “One isolated-memory failure is a contradictory pipeline: the summary agent receives a verdict calculated from fields the extractor later corrected during a retry.”
- **REWRITE | L73**: “A research agent team I built” is unsupported. Replacement: “A parallel research workflow is a useful counterexample: several agents can explore different questions while writing confirmed findings to a shared read layer.”
- **REWRITE | L87**: Replacement heading: “## The practical trade-offs”.
- **KEEP | L89**: “the first thing I check” is judgment.
- **REWRITE | L91**: The 50-to-200ms and doubling claims are bare. Replacement: “Every shared-memory access adds a round trip whose cost depends on the store, network, and serialization path. Measure it against the duration of the agent stage before choosing shared state.”
- **REWRITE | L95, L101**: The 40,000-token example and “tens of thousands... across dozens of steps” are arbitrary. Replacement: “Shared memory can fill an agent's context with other agents' observations, while reproducible debugging may require a memory snapshot at each step. Measure both context growth and snapshot cost in the actual workflow.”
- **KEEP | L97**: “I wrote about” points to a real article.
- **REWRITE | L103-105**: “I keep using” and “works most often for me” claim repeated implementations. Replacement heading: “## A useful hybrid pattern”. Replacement paragraph: “Start with isolated working memory and add a shared read-only store for facts that agents have explicitly confirmed.”
- **KEEP | L113**: “I cover” points to a real article.
- **REWRITE | L115**: “common ones I see in production systems” is unsupported. Replacement: “Cross-contamination is a predictable risk when agents can overwrite shared state without provenance or version checks.”
- **KEEP | L117**: “decision framework I use” is earned judgment.
- **REWRITE | L126**: “pipelines I build,” “I hit,” and “systems I have shipped” claim projects. Replacement: “For most pipelines, start with isolated memory and add a shared read layer only when incoherent outputs appear in traces. Full shared read-write memory must earn its additional debugging cost.”

## 6. `how-stripes-technical-blog-became-a-competitive-moat.md`

**Artifact status:** This is editorial analysis, not a benchmark. Its two business measurements have first-party Stripe sources.

- **KEEP | L4, L66, L70**: “I think,” “stands out to me,” and “When a vendor tells me...” are earned editorial judgments. Stripe's article is the source for “almost two years.”
- **REWRITE | L89**: “2am incident” is decorative specificity. Replacement: “A team pinning an API version can see what changed between releases instead of discovering it during an incident.”
- **KEEP | L91, L99-101**: These are analysis plus a verifiable reference to Ninad's changelog article.
- **KEEP | L110**: $1.9 trillion, 2025, and 1.6% are attributed to Stripe's 2025 annual letter.
- **KEEP | L118-124**: The first-person phrases are explicitly examples of what developers say, not Ninad's experience.
- **REWRITE | L130**: “11pm” is decorative specificity. Replacement: “Picture an engineer whose webhook fired twice and double-charged a customer, searching for the exact symptom during an incident.”
- **KEEP | L134**: “I covered” links to a real article.
- **REWRITE | L152**: “I see everywhere” is a sweeping observation. Replacement: “Stripe also avoids a common technical-marketing trap: a ‘best practices’ post that is only an SEO wrapper for product mentions.”
- **KEEP | L170-184**: “I call it,” “I would steal,” “work I do,” and “My work page” are editorial conclusions and verifiable professional positioning. The five-item list is an enumeration, not a measurement.

## 7. `fine-tuning-vs-rag-for-agent-memory.md`

**Artifact status:** No benchmark, dataset, fine-tuning run, billing record, or production trace. All personal incidents and latency/cost figures are bare.

- **CUT | L16-17**: “Three times in the past year I walked into this decision...” is invented consulting experience and exists to force first person.
- **CUT | L65**: “I have benchmarked... 40-120ms” has no artifact.
- **REWRITE | L67**: “three tool calls that each take a second or two” is an unsupported universal comparison. Replacement: “Compare retrieval overhead with the tool-call and inference traces from the target workflow.”
- **KEEP | L75**: “I wrote” links to a real internal article.
- **REWRITE | L85-89**: “the case that convinced me,” “We had an agent,” and the implied 200-example fix invent a team event. Replacement: “For example, an agent may call a charge endpoint before creating the customer record. That is a behavior problem, so training examples of the correct sequence may help where retrieving another document would not.”
- **CUT | L97**: The team whose documentation fine-tune destroyed arithmetic is unsupported and sensational.
- **REWRITE | L90-92**: The $100-to-$500 run and $20 monthly update are bare and volatile. Replacement: “Fine-tuning cost varies by provider, model, and dataset, and changing facts force another training run. A retrieval index can be updated without retraining the model.”
- **REWRITE | L123**: “Every system I have seen hold up under real traffic” is an absolute production claim. Replacement: “A practical default is RAG for changing knowledge, with fine-tuning reserved for narrow behavior calibration.”
- **REWRITE | L131**: “failure mode I run into most” invents repeated observation. Replacement: “Adding more documents to RAG will not reliably correct behavior learned in model weights.”
- **KEEP | L141**: “how I think through it” is judgment.
- **REWRITE | L157**: The 60ms threshold is bare. Replacement: “If retrieval latency breaks the service-level objective, test a different retrieval path or architecture rather than assuming a universal overhead.”
- **REWRITE | L159**: “hundreds of milliseconds” is an unsourced generalization. Replacement: “Compare retrieval time with the actual tool-call and inference traces from the target workflow.”
- **KEEP | L165**: “I covered” points to a real internal article.

## 8. `local-wasm-vector-benchmarks.md`

**Artifact status:** No benchmark script, generated dataset, raw timings, package lock, browser version, or repository is linked or present. The HTML visuals contain hard-coded values and do not reproduce them. Every reported benchmark result is bare.

- **REWRITE | L4-5**: “I benchmarked... on a MacBook Air M2” claims a missing benchmark. Replacement: “A comparison of PGlite and SQLite-vec for browser-based vector search, including indexing, memory, and deployment trade-offs.”
- **REWRITE | L14**: The “100ms” title promises an unproduced result. Replacement title: “Vector Search in the Browser: PGlite vs. SQLite-vec”.
- **CUT | L17**: “Benchmarking... I watched...” claims a benchmark with no artifact.
- **CUT | L17-21**: Sub-100ms, 100,000 vectors, 16GB M2, 3.2MB, 800KB, 3,072 dimensions, 384 dimensions, and under 5ms are all bare in this article.
- **REWRITE | L30**: The 100K cutoff is unsupported. Replacement: “Choose PGlite when Postgres compatibility and indexed search matter. Choose SQLite-vec when a smaller SQLite-based runtime and flat or quantized search fit the dataset.”
- **REWRITE | L40**: “Teams I talk to,” 200ms, and 500ms are unsupported. Replacement: “Local retrieval can remove a network round trip from an interactive search path.”
- **CUT | L55-62**: The claimed M2 setup, 100,000-vector synthetic dataset, model dimensions, and p99 method have no files or runnable procedure.
- **REWRITE | L59**: “I measured four primary metrics” is false ownership. Replacement: “A reproducible comparison should report bundle size, index-build time, query latency distributions, memory use, and recall.”
- **CUT | L87, L100**: Sub-15ms, 100% core use, 45 seconds, and the personal run are bare.
- **CUT | L91**: “several minutes” is another bare index-build timing.
- **KEEP | L117**: One bit versus 32 bits and the 32x raw-vector ratio are transparent arithmetic.
- **KEEP | L132**: Three expected results, two returned results, and a near-miss fourth form a clearly marked example, not a benchmark.
- **CUT | L120-126**: The p99 chart and 4ms-versus-12ms result are hard-coded presentation, not evidence.
- **CUT | L141-143**: The 99.8%, 92%, 10x speed, and “plenty” quality conclusion have no data.
- **REWRITE | L158**: The eight-times dimension ratio is arithmetic, but the 100ms crossover is bare. Replacement: “A flat scan does proportionally more arithmetic as vector dimension grows. Benchmark the crossover against the target browser, vector count, and recall requirement.”
- **KEEP | L147-149**: The 384 and 3,072 dimensions are model specifications relevant to this comparison, provided the article links the official model cards.
- **REWRITE | L164**: The universal 4GB browser limit is not reliable across browsers and runtimes. Replacement: “Browser and WebAssembly memory limits constrain how large an in-memory vector index can grow, and those limits vary by runtime.”
- **CUT | L173-175**: The 180MB and 45MB heap measurements are bare.
- **REWRITE | L179, L188**: “a few hundred thousand queries” and “millions of users” are unsupported scale claims. Replacement: “Moving retrieval to the client can reduce per-query backend compute, but it shifts compute and memory cost to the user's device.”
- **REWRITE | L205, L209**: “a few thousand bundled pages,” the 2026 framing, and M2 reference add unsupported scale and device specificity. Replacement: “A local documentation assistant with a bounded corpus can fit SQLite-vec's simpler deployment model.”
- **REWRITE | L219**: The sub-5ms and 15ms two-stage outcome is bare. Replacement: “A two-stage design can show approximate candidates first and rerank them with a higher-precision index before settling the result set.”
- **CUT | L221, L231**: The 20% thermal figure and the 50K/100K crossover are bare.
- **REWRITE | L229**: The three-to-five versus 20-chunk rule is arbitrary. Replacement: “Choose top-K from retrieval and answer-quality evals for the local model rather than copying a cloud pipeline's setting.”
- **CUT | L241-242**: “I have bridged the gap” is self-congratulation, while the 100K and one-million-vector limits are unsupported.

## 9. `voice-ai-latency-gemini-benchmark.md`

**Artifact status:** No agent code, audio corpus, timestamp logs, raw results, environment lock, dataset, or repository exists. The charts are hard-coded HTML. Every benchmark number is bare. This article is the worst offender because its title, answer, causal argument, recommendations, FAQ, and hidden editorial notes all depend on an unproduced 200-turn benchmark.

- **REWRITE | L4-5**: “I built a sub-second latency voice assistant and profiled every millisecond” is unsupported. Replacement: “A systems-level guide to tracing latency across endpointing, transcription, model inference, speech synthesis, and transport.”
- **REWRITE | L16-17**: The “800ms Barrier” and named Gemini version promise an unsupported benchmark. Replacement title: “How to Trace Latency in a Real-Time Voice Agent”.
- **CUT | L22-26**: “My latency audit,” 420-to-1,800ms, the 800ms perception threshold, and the claimed surprise about VAD are unsupported personal evidence.
- **REWRITE | L35**: The 40% result is bare, but the system point is sound. Replacement: “The model's first-token latency is only one part of voice responsiveness. Endpointing, transcription, synthesis, buffering, and network handoffs also contribute.”
- **CUT | L37-39**: Every 320ms, 120ms, 180ms, 150ms, 770ms, 80ms, 16GB, eight-minute, 60ms, 750ms, and 800ms result is bare.
- **REWRITE | L57**: The 30-to-50ms handoff cost is bare. Replacement: “A voice pipeline can still feel slow when each handoff adds buffering or network delay.”
- **CUT | L66, L68**: The 180/320/150/650ms floor and “overhead I profiled” have no artifact.
- **CUT | L70-84**: The entire setup claim, including M2, 16GB, 500Mbps, 12ms ping, 200 turns, Python agent, protocols, and 200/500ms frame tests, is unsupported.
- **REWRITE | L97**: The $4,200 pause is decorative specificity. Replacement: “A caller may pause mid-sentence to check a figure, which makes endpointing a trade-off between interruption and delay.”
- **CUT | L99, L103-110**: The Silero version, 32ms frames, under 2ms inference, all 200/500/800ms patience results, 18/6/1% false-end rates, and production verdict are bare.
- **REWRITE | L123**: “200ms frames” is an unsupported selected configuration. Replacement: “Smaller audio frames create more frequent handoffs, while utterance-level sends wait longer before transcription begins.”
- **CUT | L129-135**: The STT table, five round trips, 12ms ping, and 400MB memory result are bare.
- **CUT | L143-152**: The claimed 200ms marketing figure, personal benchmark, all clean/5-turn/50-turn p50 and p95 values, 15K tokens, and linear-degradation conclusion lack an official source or artifact.
- **CUT | L161-165**: The 50-turn, 15K-token, 30%, first-four-token, ten-turn, and 520-to-380ms pruning result inherits the circular KV-cache evidence and adds no voice artifact.
- **CUT | L171, L179-186**: The personal TTS comparison, 120/140/180/200/60/80-token/190ms results, and causal explanation are bare.
- **CUT | L192-218**: The complete 800ms budget table, 1,415ms total, all percentage shares, and every claimed saving and failure rate are unsupported.
- **CUT | L237-244**: The 500-turn speculative-TTS test, 3/12/28% backtrack rates, 80ms saving, and 50ms glitch are bare.
- **REWRITE | L259**: The 200-to-500ms stall and 12ms network values are bare. Replacement: “TCP retransmission can turn packet loss into head-of-line blocking, while real-time media transports are designed to tolerate some loss without waiting for every packet.”
- **CUT | L265-269**: The 200-turn, 2% loss, all p50/p95 figures, and 80/730ms savings have no packet-loss harness or logs.
- **REWRITE | L279-281**: The 1,400ms and 200-to-300ms figures are bare. Replacement: “Long silence after a caller stops speaking feels unlike ordinary turn-taking and can prompt the caller to speak again.”
- **CUT | L287-292**: The filler test, 40% interruption lift, and 50ms synthesis cost are bare.
- **CUT | L295-321**: The entire thermal section, including M2 Air/Pro, eight and 60 minutes, 40 turns, temperatures, clocks, frame times, and A2A timings, has no telemetry.
- **CUT | L329-351**: The context quarantine results and trade-off matrix repeat unsupported numbers, including 320/520/380/140/300/80/50/520/1,415/895/700ms, 5K/10-turn/15K-token settings, 18/3% errors, and the $50 story.
- **REWRITE | L365-367**: The -40dB threshold and 200ms buffer stall are bare. Replacement: “Use a noise gate only after measuring its effect on speech loss, and log TTS buffer underruns separately from model latency.”
- **REWRITE | L376, L378**: The 10% and 10K thresholds are unsupported. Replacement: “Tune endpointing against a labeled interruption set, then limit prompt history according to measured first-token latency and recall.”
- **REWRITE | L385-387**: The 800ms framing and 200-to-400ms model range are unsupported. Replacement: “Voice responsiveness is a systems problem, not only a model-speed problem. Compare models inside the full audio pipeline rather than treating first-token latency as the answer.”
- **REWRITE | L393**: The under-300ms reaction claim is bare. Replacement: “Full-duplex systems also need a measured interruption target because the agent must stop output promptly when the caller speaks.”
- **KEEP | L395**: “I covered” points to an internal article, but that target should not be treated as evidence until its own repair is applied.
- **REWRITE | L399**: “how I've turned complex inference infrastructure...” claims work not supported by this article. Replacement: “My work page shows how I explain complex infrastructure for developer-tool companies.”
- **CUT | L403-423**: Every FAQ benchmark answer repeats bare values: 500ms/36%, Gemini 320ms versus GPT-4o Mini 380ms, 2% loss and 890/1,650/920ms, 1,400ms silence, 200ms filler, and 50ms TTS cost.
- **CUT | L435-436**: The hidden notes claim Ninad decomposed seven measured stages and ran a 200-turn controlled benchmark. They are unsupported and must not remain even inside a comment.

## 10. `memory-for-voice-ai-agents.md`

**Artifact status:** No code, trace, dataset, database fixture, or latency log. It imports many bare figures from the unsupported voice-latency article and presents a fictional implementation as Ninad's production system.

- **CUT | L22**: “Six months of building real-time voice agents...” is invented experience.
- **CUT | L26**: “I will walk through” is empty first-person signposting.
- **REWRITE | L37**: The 500ms, 200ms, and two-second comparison is bare. Replacement: “A text chatbot can hide retrieval and prompt-loading delay behind a visible wait. In a voice conversation, the same delay becomes silence.”
- **CUT | L41-43**: “My benchmark,” 420ms, and 750ms inherit an unsupported benchmark.
- **REWRITE | L63**: “what I mean” adds no evidence, while 10-to-30 seconds is configuration-dependent. Replacement: “Working memory here means mutable state held by the transcription and language-model stages before a turn is committed.”
- **REWRITE | L69**: Three or four candidate transcripts is arbitrary. Replacement: “A partial transcript can change several times before endpointing commits the final user turn.”
- **REWRITE | L79-89**: The VAD frame sizes, sample rates, five environments, 12% result, 3ms timing, and M2 attribution are unsupported. Replacement: “VAD systems expose frame and threshold settings that trade detection speed against false endpoints. Compare WebRTC VAD and neural alternatives on labeled audio from the deployment environment.”
- **REWRITE | L111-113**: “My implementation” invents ownership. Replacement: “One interruption pattern keeps the partial generation in a buffer, marks it invalid, and passes that state into the next model turn so the response can acknowledge the correction.”
- **CUT | L115-117**: The 4GB, 30-second, under-1KB, Gemini version, and 50ms measurements are bare.
- **REWRITE | L127**: The ElevenLabs 50ms claim lacks a current vendor source. Replacement: “Use the TTS provider's documented stop or flush mechanism, then measure how quickly queued audio actually stops in the client.”
- **REWRITE | L129**: “took me the longest” and “My current architecture” invent a build. Replacement: “A useful design separates current-turn state, conversation history, and retrieved cross-session context.”
- **REWRITE | L135-139**: Three sentences, 30 minutes, 8KB, and ten turns are arbitrary. Replacement: “Completed turns can be summarized into a bounded history while extracted entities are kept separately. Set both limits from recall tests, not a universal conversation length.”
- **REWRITE | L149**: “pipeline I use” invents implementation. Replacement: “A streaming pipeline can use these boundaries:”
- **REWRITE | L165**: Tokens 3 through 50 and the permanently three-deep pipeline are invented precision. Replacement: “Transcription, generation, and synthesis can overlap, so state must be committed at explicit boundaries while other stages continue.”
- **REWRITE | L177**: “handles this for me” invents implementation. Replacement: “A checkpoint-and-rollback pattern can preserve the pre-turn conversation buffer until the response completes.”
- **CUT | L179**: The 10KB and 2ms checkpoint result is bare.
- **REWRITE | L183-199**: Every 300/800/200/400/100/150ms latency target, ten-million-vector timing, and resulting architectural prohibition is bare. Replacement: “Set the memory budget from measured end-to-end latency for the target interaction. Co-locate frequently read state when network and retrieval time consume too much of that budget, and keep external retrieval off the critical path when traces show it is the bottleneck.”
- **CUT | L207**: The 128K, ten-tokens-per-word, 12,000-word, 30-minute calculation is unsupported and mathematically suspect.
- **REWRITE | L211**: “My approach” invents a system, while three sentences and 50 turns are arbitrary. Replacement: “One option is tiered summarization: keep recent turn summaries in a bounded buffer, then merge older summaries while preserving separately extracted entities.”
- **CUT | L219**: The 30-to-50ms Gemini summarization result is bare.
- **REWRITE | L233**: “My current implementation” invents a store. Replacement: “A simple cross-session design can store timestamped facts under a user identifier and retrieve relevant facts when a new session starts.”
- **CUT | L235**: Seven days, 20-to-40ms, SQLite, and 50,000 records are bare personal measurements.
- **REWRITE | L239**: “My current habit” implies operation of the fictional system. Replacement: “When missing a remembered fact is more costly than retrieving an irrelevant one, tune the system toward recall and measure the resulting noise.”
- **REWRITE | L245-247**: One-to-three seconds and 800ms are bare. Replacement: “Text retrieval often tolerates a visible wait that becomes awkward silence in voice, so retrieval should be overlapped or moved off the live turn when traces require it.”
- **REWRITE | L279-283**: The 30/10/20ms windows and detection ranges are unsupported. Replacement: “Shorter VAD frames can reduce detection delay but increase processing and false endpoints. Choose the window with labeled audio from the deployment environment.”
- **CUT | L301-303**: SQLite at 50,000 records and 20-to-40ms, Redis under 5ms, and the 100ms budget are bare.
- **CUT | L315**: The 40-to-200ms vector-search result and categorical “Standard RAG does not work” conclusion are unsupported.
- **REWRITE | L323**: The N-offset pipeline and 150ms result invent instrumentation. Replacement: “Streaming generation and synthesis can overlap, allowing audio playback to begin before the full model response is complete.”
- **KEEP | L325**: “my benchmark post” and the contextual-retrieval link are verifiable authorship references, but the benchmark target cannot be used as evidence until repaired.

## Totals and priority

The audit contains **235 claim units**:

- **KEEP: 54**
- **REWRITE: 115**
- **CUT: 66**

The worst offender is **`voice-ai-latency-gemini-benchmark.md`**. Its central 200-turn experiment has no reproducible artifact, and at least 17 claim units, covering dozens of individual measurements, must be cut. The article cannot continue to present itself as a benchmark until the code, audio fixture, raw timestamps, environment, and analysis are published or the benchmark framing is removed.

The next highest-risk articles are `kv-cache-eviction-accuracy.md`, whose available script confirms its own fixture rather than a model or hardware result, and `memory-for-voice-ai-agents.md`, which turns the unsupported voice benchmark into a fictional first-person production architecture.

## Extension audit: artifact verdict first

The first question for each extension article is whether a repository artifact or an article-linked public artifact produces the numbers the article states.

| Article | Artifact verdict | What exists | Required action |
|---|---|---|---|
| `beam-memory-benchmark` | **NO** | The repo contains only a hard-coded HTML visual. The article links no paper, dataset, code, or result files. A search for the expanded benchmark name found only this article; the real RULER benchmark does not validate the invented BEAM results. | Remove BEAM as a benchmark, delete its fabricated tables and model scores, and retitle the page around the documented lost-in-the-middle problem. |
| `local-wasm-vector-benchmarks` | **NO** | Hard-coded HTML visuals only. No script, generated vectors, dependency lock, browser version, raw timings, or result files. | Already stripped in the first application pass and retitled as a reasoned PGlite versus SQLite-vec comparison. |
| `agentic-cli-benchmarks` | **NO** | No task fixture, starting repository, prompts, CLI transcripts, patches, test logs, environment lock, or result files. No public artifact is linked. | Remove the head-to-head benchmark framing, personal test claims, score tables, and hardware results. Retitle as a workflow comparison. |
| `lambda-calculus-ai-reasoning-benchmark` | **NO** | The article contains examples but no versioned problem set, runner, prompts, model outputs, grader, or result files. LamBench exists publicly, but the article does not link it and it does not reproduce the article's claimed personal results. | Remove personal benchmark claims and numerical model results. Retitle as a reasoning exercise and keep the transparent lambda-reduction examples. |
| `rag-evaluation-metrics-what-actually-matters` | **NO** | The article contains illustrative functions, but no dataset or runnable repository produces article-specific results. | Keep the evaluation-guide framing, which does not promise a benchmark. Remove invented project history and label code as implementation sketches rather than evidence. |
| `state-of-ai-agent-memory-2026` | **NO** | No corpus, ColBERT configuration, queries, labels, output, or logs back the claimed 50,000-point and 23% comparison. The article links no public artifact for it. | Cut the personal benchmark and invented production history. Keep only sourced or clearly framed architectural analysis. |
| `state-of-open-source-memory-2026` | **NO for article-specific claims** | The article links papers and projects, but its LongMemEval arXiv URL is wrong and no linked artifact produces its bare 65% token reduction or product conclusions. The official LongMemEval repository does provide a dataset and evaluator once linked correctly. | Remove article-specific performance claims, correct the LongMemEval source, and rename the benchmark section as an explanation of how multi-session memory is evaluated. |
| `embedding-models-compared` | **NO** | No dataset, scripts, model outputs, or raw results. Provider documentation supports model dimensions only. | The first application pass already removed personal benchmark claims and bare recall and latency results. The title remains a guide, not a benchmark promise. |

### Public artifacts used to distinguish real benchmarks from invented ones

- [NVIDIA RULER](https://github.com/NVIDIA/RULER) publishes code and task configuration for long-context evaluation.
- [LongMemEval](https://github.com/xiaowu0162/LongMemEval) publishes the dataset, evaluator, environment instructions, and history-generation code.
- [Hindsight](https://github.com/vectorize-io/hindsight) publishes implementation code and links its reported LongMemEval work.
- [LamBench](https://victortaelin.github.io/lambench/) is a public lambda-calculus benchmark, but it is not the artifact behind the lambda-calculus article's claimed tests.

### Framing changes approved by the artifact test

- `beam-memory-benchmark`: benchmark promise removed; page becomes a sourced explanation of lost-in-the-middle behavior.
- `agentic-cli-benchmarks`: benchmark promise removed; page becomes a workflow comparison.
- `lambda-calculus-ai-reasoning-benchmark`: benchmark promise removed; page becomes a guide to using lambda calculus as a reasoning exercise.
- `local-wasm-vector-benchmarks`: benchmark promise already removed in the first pass.
- `rag-evaluation-metrics-what-actually-matters`, `state-of-ai-agent-memory-2026`, `state-of-open-source-memory-2026`, and `embedding-models-compared`: their titles do not promise article-run benchmarks. Unsupported personal measurements still require removal, while attributable public benchmark discussion may remain.

## Documentation-cluster extension: self-confirming artifacts

The test for this extension is whether an artifact confronts the article with evidence it did not supply itself. A checker that looks for the headings, fields, or answer encoded in its own fixture does not meet that test.

### 1. `api-documentation-best-practices-reference-guides-and-working-requests.md`

**Artifact verdict:** Does not survive. `check_api_docs_package.py` checks a hand-authored JSON object for the same fields the article declares necessary, so its `PASS` line adds no independent evidence.

- **REWRITE | original L21:** “I built a small package checker” turns an editorial premise into a personal test claim. Replacement: “An API portal can list every endpoint and still leave a developer unable to send a request. The missing work is usually distributed across a quickstart, reference, and error guidance, which makes an incomplete path look finished in a navigation tree.”
- **CUT | original L64-80:** Remove the heading, fixture description, command, exact `PASS` string, screenshot, and caption. The run verifies only the fixture the article authored.

### 2. `api-documentation-examples-what-the-best-developer-portals-get-right.md`

**Artifact verdict:** Does not survive. `check_developer_portal_path.py` checks a local fixture for the exact editorial fields the comparison already assumes.

- **REWRITE | original L23:** Remove the invented need for a checker. Replacement: “A polished API portal can still make a developer guess which credential to create, which request proves access, and where an error belongs. A portal earns its example status when a reader can follow one inspectable path from access to recovery.”
- **CUT | original L60-76:** Remove the complete checker section, including the command, result, screenshot, and caption.

### 3. `api-documentation-template-the-pages-every-api-needs.md`

**Artifact verdict:** The downloadable outline survives as a useful template. Its checker does not, because it searches that same outline for a hard-coded list of headings.

- **KEEP | original L22:** “I built this API documentation page outline” is verifiable authorship of a real downloadable artifact, and the artifact is useful without claiming that it proves itself correct.
- **CUT | original L70-86:** Remove the outline-validation section, exact `PASS` string, screenshot, and caption.

### 4. `api-documentation-tools-hands-on-comparison-small-teams.md`

**Artifact verdict:** Does not survive. The selector maps a fixture's `source_of_truth` value directly to a hard-coded product label; it neither exercises the tools nor compares their workflows.

- **REWRITE | original L18:** The title promises hands-on evidence the page does not contain. Replacement: “API Documentation Tools: A Workflow Comparison for Small Teams.”
- **REWRITE | original L22:** Remove the selector as evidence. Replacement: “Small teams don't need a portal with every switch turned on. The first choice that changes the outcome is where the API contract lives and how a change gets reviewed.”
- **CUT | original L59-83:** Remove the selector fixture, download commands, result, screenshot, and caption.

### 5. `documentation-style-guide-template-for-developer-teams.md`

**Artifact verdict:** The style-guide template survives as a usable editorial scaffold. Its validator does not survive as evidence because it checks the template for its own hard-coded headings and markers.

- **KEEP | original L21:** “I built the attached template” is verifiable authorship of the downloadable file.
- **REWRITE | original L29:** The checker adds no information. Replacement: “The first useful use is one guide that changes often. Fill its bracketed fields with product facts, then let the next release show which parts of the template need more detail.”
- **CUT | original L71-73:** Remove the fresh Python 3.13.5 claim and the validator result. The version is irrelevant to the reader task, and the result is self-confirming.
- **REWRITE | original L91:** Replacement: “Download the template and fill it against a frequently edited guide before asking the rest of the team to adopt it.”

### 6. `how-to-document-multiple-product-versions.md`

**Artifact verdict:** Does not survive. The route audit correctly implements its declared policy, but the supplied pass and fail inventories were authored to trigger those same branches and do not test a real documentation site.

- **REWRITE | original L21:** Replacement: “A version switcher can make incompatible instructions look like interchangeable pages. A current page, a supported older page, and a retired page need different URL behavior before a canonical tag or redirect can be correct.”
- **CUT | original L62-78:** Remove the fixture audit section, command, expected `PASS` line, screenshot, and caption.
- **CUT | reported 30-site measurement:** “Measured across 30 developer docs sites on 2026-08-14, 11 had no version selector at all” has no source list, capture, dataset, or method in the repository. The sentence is absent from the deployed article revision but remained in the live AI Overviews checker sample, so it was removed there rather than preserved as a hedge.

### 7. `seo-for-technical-documentation.md`

**Artifact verdict:** The Cloudflare audit survives. `static/tools/docs-seo-audit.py` exists, targets a live external page, emits inspectable checks, and reproduced 12 passes with zero warnings and zero errors on 17 August 2026. The broken local fixture does not survive because it contains the failures the same run is supposed to discover.

- **REWRITE | original L21:** Replacement: “I built the audit for this guide around Cloudflare's live Workers CLI guide. Its source and rendered page show which checks a reader can rerun and which still need browser or Search Console evidence.”
- **REWRITE | original L93:** The example command uses a placeholder URL, not the Cloudflare target. Replacement: “Start with the final URL and headers:”
- **KEEP | original L191-201:** The repository contains the linked standard-library auditor, its documented checks match the code, and the published command is rerunnable.
- **REWRITE | original L205:** Attribute the result to a dated rerun rather than an unverifiable personal event. Replacement: “A rerun against Cloudflare's Workers CLI getting-started guide on 17 August 2026 returned 12 passes, zero warnings, and zero errors.”
- **CUT | original L217-223:** Remove the deliberately broken local fixture, its result, screenshot, and caption.
- **KEEP | original L225-229:** The limitations accurately state what the script cannot establish and stop the source-level checks from being presented as a ranking or task-success score.

### 8. `what-is-technical-documentation-and-what-should-it-include.md`

**Artifact verdict:** Does not survive. The manifest and validator share the same required fields, so seven passing entries prove only that the authored fixture contains seven authored records.

- **CUT | original L72-92:** Remove the entire manifest-validation section, including the first-person run, exact count, command, screenshot, and claim that it exposes missing ownership.

### 9. `the-case-for-shorter-technical-documentation.md`

**Artifact verdict:** No evidence artifact exists. The cognitive-load visual is an illustration, not a measurement, and the article must not turn bare percentages or an editorial preference into observed results.

- **KEEP | original L18:** “why I keep arguing for it” is an earned editorial opinion.
- **REWRITE | original L55:** The claim that action-oriented design reduces onboarding time by up to 30 percent is bare. Replacement: “I follow four minimalist principles in my work.”
- **KEEP | original L64:** “I am after essentialism” is a judgment about the author's editing standard.
- **REWRITE | original L70:** The five-percent edge-case claim is bare. Replacement: “The happy path stays clear of edge cases that belong in reference or troubleshooting.”
- **REWRITE | original L72-80:** Three levels may remain an editorial structure, but the XAI and UX claims do not support a universal limit. Replacement: “I separate the primary task from supporting context and deep reference.” Follow with: “The layers are useful only when each one gives the reader a clear route back to the task. Hiding detail without providing that route merely moves the confusion into navigation.”
- **KEEP | original L102-116:** The webhook-page behavior and three-sentence opening are clearly framed as personal reading and editing preferences, not measured outcomes.
- **REWRITE | original L124-126:** The article does not measure search or retrieval performance. Replacement: “Clear, shorter docs also make exact answers easier to find within a page. A bloated page can bury the sentence a reader needs under unrelated preamble.” Follow with: “Infrastructure topics attract vague abstractions, so I organized [Agent harnesses](/articles/agent-harnesses/) as focused sections rather than one sprawling essay.”
- **KEEP | original L134-143:** The case for longer migration guides, specifications, architecture references, and runbooks is editorial judgment tied to the decisions those formats must preserve.
- **KEEP | original L147-152:** The four editing questions are a stated review practice and make no result claim.
- **KEEP | original L160:** The changelog link supports a stated editorial position, not a measurement.
- **KEEP | original L164-168:** Preferring modular pages is an opinion earned from the author's work.
- **REWRITE | original L174:** The 600-word and 3,000-word examples add arbitrary precision. Replacement: “There is no universal word count. A quickstart may be brief, while a deep migration guide needs enough space to cover every consequential decision.”
- **KEEP | original L188:** Wanting fewer mixed-purpose pages is an editorial preference.

### 10. `from-engineer-to-technical-writer-what-i-kept-and-what-i-left-behind.md`

**Artifact verdict:** No artifact backs the Structured Outputs test or its claimed failure boundary. The career history and editorial judgments remain valid first-person material, but the fabricated test event and fabricated anecdotes do not.

- **KEEP | original L14-20:** The career transition and its central distinction are the author's lived professional history.
- **KEEP | original L24-30:** Verifying a draft command and agreeing with GitLab's review standard describe an earned working principle.
- **CUT | original L32-34:** Remove the claim that Ninad tested a four-level schema with an optional enum and observed a guarantee degrade to best effort. No input, request, output, model version, or repository artifact exists.
- **KEEP | original L42-53:** The information-architecture questions and use of Diataxis are editorial practices, not performance claims.
- **KEEP | original L63-67:** Spelling out prerequisites and avoiding repeated definitions are earned writing judgments.
- **REWRITE | original L71-75:** “almost none” and “someone who already watched the thing crash” invent a survey and event. Replacement: “A debugger's mindset persists in my writing for that reason. My post on [Agent harnesses](/articles/agent-harnesses/) focuses on control flow and observability because prompting advice often skips retry loops and recovery.” Follow with: “Documentation gets stronger when it explains how a failure becomes visible and what ends it.”
- **KEEP | original L79-81:** The danger of local prose optimization is an earned editorial judgment.
- **CUT | original L92:** Remove the sharp three-page rate-limit aside. It is a specific event with no support and contributes nothing beyond the surrounding point.
- **KEEP | original L102-109:** Git, linting, CI, and review gates are real tools and practices in the repository workflow.
- **KEEP | original L111-113:** The Write the Docs survey figures are attributed to the linked survey.
- **KEEP | original L119-125:** Maintenance cost and internal linking describe current site practice that the repository can verify.
- **KEEP | original L131-146:** The difficulty of technical writing and the listed skills are professional judgments, while the career-path statement is linked to Google's material.
- **REWRITE | original L152:** The precise reader drop-off and repeated ticket are unsupported. Replacement: “Feedback loops got more legible, for one. A confusing page fails in visible ways: readers leave before finishing the task, and support sees the same missing step again.”
- **REWRITE | original L158:** “first user of every feature” is an absolute personal claim. Replacement: “A technical writer never gets that pass. The job requires approaching onboarding as a first-time user and naming the context the product assumes.”
- **REWRITE | original L160:** The claim about thousands of developers is an unsupported scale. Replacement: “The reach of my work changed too. A feature helps users who find it, while one well-built page can shape how developers understand the product before signup.”
- **KEEP | original L162:** Choosing durable documentation assets is a stated professional preference.
- **REWRITE | original L174:** The absolute claim that Ninad refuses to publish anything untested conflicts with unsupported material found on the site. Replacement: “Empirical verification. Run every command, flag, and claimed output before publication so copied examples do not fail on behavior the product has already changed.”
- **REWRITE | original L178-180:** The 90/10 split is invented precision. Replacement: “I had to stop compressing my explanations too early. I used to write for the person who already understood most of the system.” Follow with: “I had to learn to write for the reader missing the context that makes it work.”
- **KEEP | original L184-190:** Reading code, testing APIs, researching, editing, and designing information systems are ordinary descriptions of the role.

### Documentation-extension totals

The extension contains **55 classified claim units**:

- **KEEP: 23**
- **REWRITE: 21**
- **CUT: 11**

Only three artifacts survive the test: the API documentation page outline as a template, the documentation style guide as a template, and the external Cloudflare Workers audit as reproducible evidence. None of the other checkers or fixtures tests a proposition that its own input did not already assume.
