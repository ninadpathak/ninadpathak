# Ninad's corrections while building this skill, 2026-09-05 to 06

Each entry: the draft the skill produced, and what Ninad said was wrong. This is the ground truth for what the skill still fails at. A rewrite of the skill must make every one of these failures impossible.

## Topic used for all drafts: "Claude Code Context Window: What Fills It, What It Costs"
Earlier topic: "9 Agentic Search Tools Ranked by Index Points per Dollar"

### Draft 1 (search tools)
> Everyone ranks search tools by how well they answer a question. That's the wrong metric for an agent... I noticed this the way you notice most things about infrastructure, which is by getting a bill. I'd built a small research agent...
Ninad: "not once did he assume 'everyone' or use such ai slop sentences." Also (root's own finding): invented anecdote, tease ("the ranking surprised me"), coined term, set-piece punchline.

### Draft 2 (search tools)
Four paragraphs with bracketed placeholders, narrative about a bill.
Ninad: "still way too long winded for what paul graham does."

### Draft 3 (context window)
> Open a fresh Claude Code session and type one sentence. Before you've said anything else, [N]k of the 200k-token window is already gone. You didn't put it there... That's the thing about a context window: most of what fills it is not conversation. It's plumbing... Why does that matter? Not because the window runs out... So the question isn't how big the window is. It's what's in it, who put it there, and how many times you're going to buy it.
Ninad: "the skill is still outputting AI slop." Patterns: "That's the thing", colon reveal, "not X. It's Y" three times, self-answered rhetorical question, rule-of-three kicker, plan announcement.
Root's diagnosis: the skill listed "X is not Y. It's Z." and "Why would X? Not because Y." as PG moves, and the model used them three times in four paragraphs. PG uses each once per essay at most.

### Draft 4
> Open a fresh Claude Code session and type one sentence. Before it is sent, [N]k of the 200k-token window is taken by...
Ninad: "'Open a claude code session' is redundant if you think about it. The person reading the topic already knows about context windows enough to search about it." And: "[N]k is vague, don't give this and instead just say a part of the overall context (because context windows keep changing)."

### Draft 5
> Most of a Claude Code context window is filled by things you never typed...
Ninad: "it starts with 'Most' and paul graham doesn't usually throw generalizations like these."

### Draft 6
> Before your first message reaches the model, Claude Code has already sent it the system prompt... When it fills, compaction swaps the transcript for a summary. That is the smaller cost...
Ninad: "the intro doesn't introduce, you're just summarizing the full topic in 3 paragraphs. The idea of an intro is to share the backstory, the narrative, the 'why' and 'what' rather than 'full detail'."

### Draft 7
> In [month] I was [N] messages into a Claude Code session when it warned me the context was nearly full. I scrolled back and read everything I had typed. It came to about a page. Something else had filled the window...
Ninad: "you made the writing shit. This makes the author feel like a dumbass who has never used a tool in their life and is surprised by the most basic thing that an AI is designed to do."

### Draft 8
> Claude Code ships a tool called ToolSearch whose only job is to hide most of the other tools from the model... What they cost is turns. A token in the window is read again on every turn until compaction removes it, so its price is its size times how long it stays...
Ninad: "write from first principles"

### Draft 9
> A language model remembers nothing between calls. Everything it knows about your session is what gets sent with the current request... Two things follow...
Ninad: "this is extremely weird, not first principles, this feels dumbed down"

### Draft 10
> The cost of a Claude Code session is the area under one curve: window size against turns... Two things fall out of that shape... Caching changes the coefficient, not the shape... How much you type is not on the list.
Ninad: "still trying too hard rather than explaining like you understand it"

### Draft 11 (no complaint yet; closest so far)
> Every turn, Claude Code sends the model the whole conversation so far. Not just your messages: the system prompt, your CLAUDE.md files, the schema for every tool it might call, and the output of every tool it has already called. That's the context window, and you're billed for all of it on every turn.
>
> Once you look at what's in there, your own messages are a rounding error. The system prompt and tool schemas are there before you type anything. If you've got a couple of MCP servers connected, that's a hundred tool definitions sitting in the window for the whole session. Then the work starts, and the model reads files, greps, runs tests, and each of those results lands in the window too. A single test failure with a stack trace is bigger than everything you'll type all day.
>
> Caching is what makes this affordable. As long as you keep the conversation going, the model has most of the window cached and the reread is cheap. Walk away for five minutes and the cache is gone, so the next turn pays full price for everything again. Compaction eventually summarises the transcript to make room, but by then you've paid for it many times over.
>
> So the bill is mostly about three things: what gets loaded at the start, how much tool output piles up, and how often you leave gaps. I wanted to know how much each of those actually costs, so I measured one session.

## What the pattern of corrections says
- Every "clever" move (framing device, curve metaphor, derived-from-axioms structure, second-order hook) read as trying too hard. The draft that landed talks plainly, like someone who understands the thing explaining it to a peer, in the order they'd say it out loud.
- The narrator must be an expert peer. Never surprised by the tool's basic behaviour. Never explaining what the reader already knows.
- The intro is backstory and the why/what, not the body compressed.
- No quantity generalizations ("most", "everyone") as claims. No placeholder numbers for facts that change; proportions or mechanisms instead. Brackets only for the author's own measurements.
- PG's real habits ("X is not Y. It's Z.", reframed question, "Why? Not because...") become slop when a model follows them as rules. Cap at once per piece or remove from the rule list entirely.
- Ninad also wants the skill to capture how PG thinks through a topic and how the intro connects the reader via lived experience or a story hook, not only surface style.

## Interview transcript the skill started from
A 2026 YC interview. Observed there: answers the literal question first; rejects bad premises; one homely image per idea (model train falling off the table; finish line that has width, "a smear"); real named examples only (Reddit, Sid from GitLab, Sam Altman); admits ignorance readily ("I've never really been clear what a lean startup is"); "right?" as listener check; dry humor inside the argument; strips romance off facts ("that was just an accident"); ends on a new point not a recap.
