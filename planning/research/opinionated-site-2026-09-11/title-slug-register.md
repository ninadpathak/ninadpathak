# Title and slug register

No slug changes ship in Phase A. A short URL is useful, but breaking an indexed path to make it prettier is vanity unless the current path causes a real problem.

| Current slug | Recommended public title | Slug decision | Reason |
| --- | --- | --- | --- |
| `writing-ai-first-content` | Before You Ask an Expert | Fixed | User explicitly fixed this canonical. |
| `agent-harnesses` | The Agent Harness Is the Product | Keep | The slug is already short; the current title sounds like category copy. |
| `2026-04-23-agent-loop-anatomy` | Your Agent Is a Loop With Expensive Taste | Consider later | The date prefix weakens recall, but a redirect needs traffic and link evidence first. |
| `2026-04-26-agent-vs-ai-assistant` | You Probably Need an Assistant, Not an Agent | Consider later | The recommendation is sharper than a neutral comparison. |
| `2026-04-27-multi-agent-vs-single-agent-tradeoffs` | Every Extra Agent Is Another Failure Boundary | Consider later | The existing slug is long but descriptive; change only with redirect evidence. |
| `embedding-models-compared` | Embeddings Are Coordinates, Not Understanding | Keep | The slug owns a comparison intent; change the title without moving the URL. |
| `engineering-velocity-documentation` | Bad Docs Make Good Engineers Relearn the System | Keep | The current title sounds like a report and carries a quantitative claim that needs source review. |
| `technical-writing-for-engineers` | Documentation Is Part of the Build | Keep | The current slug is useful and short; the article needs evidence repair before a title change. |
| `the-case-for-shorter-technical-documentation` | Your Docs Are Long Because Nobody Decided | Keep | The existing slug still says what the argument covers. |
| `why-devtools-startups-lose-deals-over-bad-docs` | Your Docs Are in the Sales Call | Keep | The current slug has clear search language; the stronger title can change independently. |
| `what-is-technical-documentation-and-what-should-it-include` | Technical Documentation Starts Where the Product Gets Confusing | Keep | A long slug is not enough reason to move a useful canonical. |

Before any future slug change: record current traffic and inbound links, add both slash variants to `_redirects`, build the exact intended tree, and verify the destination canonical.
