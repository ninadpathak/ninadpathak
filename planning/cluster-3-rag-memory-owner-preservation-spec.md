# RAG-versus-memory owner preservation gate

Updated: 2026-08-18

`rag-vs-memory` remains the owner. It has 74 complete page-dimension impressions, one click, and an
average position of 17.2. Search Console withholds all of its named queries, so that click cannot be
reconstructed from query rows and must not be treated as absent.

`asymmetric-retrieval-agent-memory` has 12 impressions at position 18.3 and owns one visible query:
`hybrid retrieval for agent memory` at position 72.0 on one impression. The pages share no exact
named query, and merge-page query coverage is only 18.0%. The visible source job and the unknown
withheld demand must survive at the target before any redirect.

## Target integrity correction

The current owner contains unsupported customer/team anecdotes, fabricated performance gains,
unverified latency and pricing figures, changing model/vendor limits, an untested example client,
and an invented evaluation practice. Those passages are not evidence and may not be carried
forward. The source is the stronger page for retrieval mechanics, but it cannot replace the owner
because the owner has the click and greater observed demand.

## Target-only prose handoff

The writer may edit only `content/posts/rag-vs-memory.md` and must commit that one-file change
independently. It must:

1. Keep the owner's decision boundary: RAG selects external source evidence for the current
   request; memory governs state that must survive, change, expire, or return across requests.
   Neither is synonymous with a vector store or a conversation buffer.
2. Explain the hybrid request loop: read relevant durable state, retrieve source evidence, build a
   bounded context, answer from that evidence, and make any memory write a separate controlled
   decision.
3. Preserve the source's asymmetric-retrieval mechanism. Agent-generated queries arise from partial
   task state and can use different language from stored records or human-written questions.
4. Preserve the visible `hybrid retrieval for agent memory` job explicitly. Explain that dense
   retrieval handles semantic similarity, lexical retrieval protects identifiers and exact terms,
   and metadata filters enforce identity, service, event type, time, and access boundaries.
5. Distinguish HyDE from self-querying retrieval: HyDE moves a query toward document language;
   self-querying separates semantic text from typed constraints. A hypothetical passage is never
   evidence for the final answer.
6. Make evaluation match production query formation: test the queries the agent actually produces,
   the task state available when each query is formed, expected source records, retrieval results,
   and answer use. Human-authored questions may supplement but not substitute for that set.
7. Use the existing primary Anthropic contextual-retrieval reference and the site's hybrid-search,
   HyDE, self-querying, context-window, and memory-management pages only where the sentence earns
   each link.
8. Remove every unsupported first-person event and local result, including the claimed support-bot
   incident, teams losing weeks, benchmark gains, synthetic-conversation practice, and absolute
   production conclusions. Remove unattributed prices, latency, vendor limits, model defaults,
   fixed chunk counts, and cost projections. Do not invent replacements.
9. Remove the unverified OpenAI example implementation unless a committed test fixture and an
   authorised zero-spend verification surface exist. Explanatory pseudocode must not masquerade as
   a tested working client.
10. Keep the title/slug and the target's RAG-versus-memory reader outcome. Use present-tense
    engineering judgments only when they are inspectable from the described architecture.

The writer must not edit the source, redirects, inbound links, navigation, publication status, the
queue, briefs, or campaign records. A target-only prose commit is not merge authorization.

## Director execution gate

Only after the target-only commit passes review and renders live may the Director assemble one
atomic execution that:

- marks `asymmetric-retrieval-agent-memory` merged without deleting it;
- repoints every active inbound body, pillar, and navigation reference to `rag-vs-memory`;
- adds direct `/articles/` and legacy `/blog/` permanent redirects;
- preserves the owner's title, canonical, and historical click-bearing URL;
- passes `tools/gsc_merge_guard.py --dry-run`, claim/rule/heading checks, build, strict cluster,
  stylesheet, structure and inert-CSS gates, the full suite, exact-head CI, deploy checks, both live
  redirects, sitemap exclusion, and a human rendered-owner review.

Stop instead of redirecting if the target loses the RAG-versus-memory boundary, asymmetric query
formation, the hybrid retrieval mechanism, typed constraints, or agent-query evaluation.
