# Worked example

The same material twice, so the difference is visible.

## Dry version (what to avoid)

Prompt caching reduces costs. Keep system prompts static. Do not change tool definitions mid-conversation. Cache misses increase token costs. Compaction should occur while the cache is warm.

Each sentence is correct. None of them tells the reader why it follows from the previous one, so the reader has to rebuild the logic alone and will probably skim.

## Spoken-narrative version (what to write)

Every time you send a message to an agent, you are resending the whole conversation, plus one new line at the bottom. That sounds wasteful, and it would be, except that model providers give a steep discount on tokens they have already seen. So the game becomes keeping the top of the prompt identical from one call to the next, because the moment anything up there changes, the discount disappears and you pay full price for everything below it.

That is why the system prompt and the tool definitions should sit still. Add a tool halfway through a turn, or reorder two sections for an experiment, and you have just busted the cache: Anthropic's docs list a changed tool definition as invalidating tools, system and messages, which is the whole prompt. A cache miss at scale is a bug, and an expensive one.

Providers keep the cache warm for a window, from five minutes by default on Anthropic up to an hour on its longer option. Summarize a long conversation while the cache is still warm and the summary is cheap to produce, so you start the next session from a short, cheap context. Wait until the cache goes cold and you pay full price for the exact same summary.

Why it works, point by point:

- The opening sets up a concrete mechanism (resending the conversation) before any rule appears, so the rules feel inevitable.
- "So the game becomes" is the one budgeted pivot, the turn from the mechanism to the rule. "That is why" turns the next rule into a consequence of the one before.
- The second rule arrives as a plain claim about the cache window. The example spends one setup sentence in about 250 words, which is the budget, and no more.
- Each rule gets one sourced fact (the tool-definition invalidation, the five-minute default) in place of an invented scenario, so the reader can check it.
- No sentence starts with a banned word, no em dashes appear, and no sentence leans on "not X but Y".
