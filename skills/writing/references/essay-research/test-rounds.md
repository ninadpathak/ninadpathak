# Revision trials — 2026-09-06

These are sequential self-tests, not independent model evaluations or Ninad's acceptance. I reread the complete rewritten SKILL.md before each round, using it as the only style instruction for generation. The conversation's prior context cannot be erased without a separate model run; the user prohibited subagents. Topic facts came from the supplied samples and checked primary documentation. No Claude Code cost experiment was performed.

Audience: senior engineers who use Claude Code daily; Indian homeowners and the Interio founder for the second topic. Only the supplied payment of about ₹20 lakh is treated as personal history. The samples' restaurant comparison, repeated customer failures, diversion of advances, and claimed certification effects are not established facts.

## Round 1

Skill snapshot: `/tmp/pg-codex/SKILL.round1.md`.

### Claude Code Context Window: What Fills It, What It Costs

Every request Claude Code sends includes the context it has retained from the session. Your messages sit alongside the system prompt, project instructions, loaded tool definitions, and results from the work Claude has done. A request to fix a test can add the file it reads, the test output, and the patch discussion to the conversation.

Those results remain available on later requests until Claude Code removes or compacts them. On API billing, retaining them also means paying to read them again. Prompt caching reduces the cost of the unchanged portion, so the same amount of context can cost different amounts depending on whether it is cached.

That gives a session two histories. One is the work being done in the repository. The other is the material carried forward to support that work. Understanding the second explains why a short exchange can use so much context, and why the amount of space occupied does not by itself tell you the price.

### Why Interior Contractors in India Get Away With It

I paid an interior contractor about ₹20 lakh for work on my home. A homeowner making a payment like that needs to know more than whether the contractor has completed an attractive apartment. They need to know whether the work was delivered on the terms agreed.

A photograph cannot show that. It leaves out the original scope, the payment schedule, and the work that had to be redone. References can supply some of this history, but only when the prospective customer reaches someone who knows it.

This is the problem behind InterioHQ's proposed certification. A record of previous jobs would let a new customer examine what happened before paying. If failures became visible at the next sale, doing a bad job would have a cost beyond the dispute with the current customer.

### Diagnosis and skill repair

Claude paragraph 3 invents “two histories” to package an already clear account. This repeats draft 10's performance in milder language. It also repeats paragraphs 1–2 and ends without a specific inquiry (draft 6). Interio rushes from the information gap to certification and the claimed remedy, compressing the future body into the introduction (draft 6). Neither failure needs a sentence-length fix.

Added to the skill: reject a paragraph that merely renames the preceding explanation; make the unresolved task concrete; establish why a proposed remedy is needed before introducing it. These are checks on paragraph function, not additional banned phrases. Draft 11 already passes: its final paragraph specifies measurement rather than supplying a new name or selling a remedy.

## Round 2

Skill snapshot: `/tmp/pg-codex/SKILL.round2.md`. Complete skill reread before drafting.

### Claude Code Context Window: What Fills It, What It Costs

Claude Code includes the retained conversation in each request to the model. That conversation includes the files it has read and the output of its tools, alongside your messages and its replies. The system prompt, project instructions, and loaded tool definitions take up space too.

During a debugging session, each attempt can add another test result. The earlier results remain in context until they are removed or compacted, even when the latest failure is the one Claude needs to investigate. On API billing you pay for that retained input again, with a discount for the part served from cache.

To find the cost of a session, we need to separate the initial load from the accumulating transcript, identify the cached portion, and determine when compaction changes what is retained. Then we can decide which material to remove without losing the information needed for the task.

### Why Interior Contractors in India Get Away With It

I paid an interior contractor about ₹20 lakh for work on my home. Before paying that much, a homeowner needs evidence that the contractor will finish the work agreed. A portfolio establishes that they can produce a good-looking room. It does not establish how the job went for the person who paid for it.

The contractor chooses which jobs to show. A homeowner who had a bad experience has no equivalent access to the next prospective customer. They can warn friends or leave a review, but the warning only affects the next sale if that customer sees it and finds it credible.

InterioHQ's proposed certification has to address that gap. It needs a way to connect what happened on a job with the next customer's hiring decision. That requires more than collecting photographs of completed rooms.

### Diagnosis and skill repair

Claude paragraph 3 is an outline disguised as prose (draft 3's plan announcement and draft 6's compressed article). “We need to separate … identify … determine” lists future actions without developing the reader's practical difficulty. The final introductory paragraph rule was too easy to satisfy with a methodology list.

Interio states a one-sided market structure as fact: “has no equivalent access.” Referrals, reviews, and direct contact can give previous customers access. “A portfolio establishes” is also too strong: selection and authenticity are exactly what remain to be checked. These repeat drafts 1 and 5's unsupported scope, despite avoiding their opening words. Certification still arrives as a premature answer.

Skill repair: require a practical unresolved issue rather than a sequence of future sections; test claims with existing alternatives such as referrals; reject a title's premise when the evidence does not establish it. Narrow the mechanism without making the author timid. Draft 11's concrete measurement objective is permitted; its confident tone remains permitted. Unsupported quantities in that draft remain an accuracy concern, separately from its accepted explanatory manner.

## Round 3

Skill snapshot: `/tmp/pg-codex/SKILL.round3.md`. Complete skill reread before drafting.

### Claude Code Context Window: What Fills It, What It Costs

Each time Claude Code calls the model, it sends the conversation it has retained so far, along with the system prompt, project instructions, and loaded tool definitions. The files Claude reads and the tool results it receives become part of that conversation. Your next message arrives with the work that led up to it.

During debugging, that includes attempts you've already moved past. Claude reads a file, changes it, runs a test, and gets another failure. While those earlier results remain in context, they take up space on subsequent requests too. A short instruction to try again can carry a long history of failed attempts.

With API billing, you also pay for that history on subsequent requests. Caching makes the unchanged portion cheaper to read, but it still occupies context. That matters when deciding what to trim: the material taking up the most space isn't necessarily the material costing the most to process. Before discarding useful project instructions or clearing a debugging session, you need to know which retained material is responsible for the cost.

### Why Interior Contractors in India Get Away With It

I paid an interior contractor about ₹20 lakh for work on my home. At that price, the history of their previous jobs matters. Photographs show the finished rooms. They don't tell you what the customer was promised, how much more they had to pay, or what was left unfinished outside the frame.

A previous customer can tell you those things. That is why a referral from someone whose home you've seen is useful. But the warning from a failed job has to reach you too. A contractor can show you a completed kitchen without putting you in touch with the customer still waiting for theirs.

For a bad job to cost a contractor future work, a later customer has to learn about it before hiring them. If the next customer sees only the successful jobs, the failure need not affect the next sale. The problem to investigate is how a homeowner gets a reliable account of the jobs a contractor would rather not show.

### Round 3 judgment

No remaining complaint identified in this self-review. This is not a claim that Ninad will accept the prose or that a fresh model will reproduce it. No change to the substantive rules after this generation. The final Claude introduction deliberately scopes price to API billing; the contractor introduction states a conditional sales mechanism, not a prevalence claim or an accusation about the author’s contractor. Neither claims a new empirical discovery. Actual evidence about cost shares and contractor records belongs in the body.

## Complaint-by-complaint checks across rounds

P = passed this self-review; F = failure described above. C = Claude; I = Interio. Multiple complaints within an entry are separated so a surface pass cannot conceal a reasoning failure.

| Complaint / source | Round 1 C / I | Round 2 C / I | Round 3 C / I | Final evidence |
|---|---|---|---|---|
| Unsupported consensus or prevalence (1, 5) | P / P | P / F | P / P | Operations and conditional information flow; no population claims. |
| Invented personal experience (1, 7) | P / P | P / P | P / P | No Claude anecdote; only supplied ₹20 lakh payment. |
| Teased result, coined label, set-piece punchline (1) | F / P | P / P | P / P | “two histories” removed; no promised surprise. |
| Long-winded backstory, placeholders (2) | F / P | P / P | P / P | Three paragraphs each; payment is one sentence; no invented scene. |
| “That's the thing” and colon reveal (3) | P / P | P / P | P / P | Final colon introduces the practical distinction already motivated, not a reveal. |
| Repeated not-X-it's-Y, rhetorical Q&A (3) | P / P | P / P | P / P | No such frames or self-answered questions. |
| Decorative rule-of-three kicker (3) | P / P | P / P | P / P | Lists identify actual contents or missing job evidence, not three punchlines. |
| Plan announcement (3) | P / P | F / P | P / P | Final paragraphs state the decision/information problem without a section itinerary. |
| Redundant app-opening instruction (4) | P / P | P / P | P / P | No setup lesson. |
| Placeholder/changing context-size numbers (4) | P / P | P / P | P / P | No fixed capacity, TTL, token count, or price. Payment is supplied history. |
| Introduction compressed from whole article (6) | F / F | F / F | P / P | No remedies, compaction procedure, rate list, or certification pitch. |
| Narrator surprised by ordinary behavior (7) | P / P | P / P | P / P | Basic behavior is treated as the premise throughout. |
| Implementation-first; formula replacing cause (8) | P / P | P / P | P / P | Requests and job records precede deductions. No ToolSearch opener or cost formula. |
| Basic textbook explanation / dumbed down (9) | P / P | P / P | P / P | Reader already codes or hires; no definitions of models or contractors. |
| Cleverness instead of understanding (10) | F / P | F / P | P / P | The repeated cost and information gap are stated through actual actions. |
| Preserve accepted order and peer register (11) | F / F | F / F | P / P | Shared fact → work → consequential distinction → inquiry; no stolen experiment. |

Additional rule checks: no fabricated unnamed disagreement; no invented exact numbers; no recurrence of a decorative analogy; no recap ending; no claim that the narrator never admits ignorance; no compulsory novelty in the first sentence. The final contractor scenario is generic and conditional, not a report that the author's contractor left a kitchen unfinished.

## Technical fact checking

Checked 2026-09-06 against [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) and [How Claude Code uses prompt caching](https://code.claude.com/docs/en/prompt-caching), especially context layers, prefix reuse, loaded/deferred tools, and cache lifetime. These support retained content being sent again and cached input receiving a different rate. No fixed default window or universal five-minute expiry is used. Tool definitions are described as loaded, not all available MCP schemas. “Cost” in the final draft is API input cost; it does not assert that subscription customers receive a bill for every turn or that input is the entire bill.

The statement that the largest context item need not be the most expensive to process is a deduction from different cached/uncached rates. It is not a reported session measurement. The final intro stops before cache invalidation, output charges, compaction behavior, and cost attribution; those require the body.

## 2026-09-06 — pg-skill-codex2: depth and voice trials

### Method and factual brief

Three rounds for each requested topic, with the full SKILL.md freshly read immediately before drafting each round. SKILL.md is the sole style reference during generation; the topic, audience, and factual brief below remain inputs. Reviews then compare the result with all eleven feedback-log entries. These are sequential self-tests in this session, not independent or blind model evaluations. The no-subagent instruction rules out independent agent trials. Changes to the skill and complete drafts are retained, including failed drafts. No session measurement, author anecdote, or user acceptance is invented.

The contractor brief: Ninad explicitly confirms losing about ₹20 lakh to an interior contractor. The supplied samples locate the work at his home. The date, city, work delivered, contract, payment sequence, complaints, referrals, and contractor's later jobs are unknown. Earlier sample claims about ten abandoned jobs, silent homeowners, nonexistent market memory, and certification effectiveness are unsupported. No law, industry fraud rate, or claim about a named contractor is needed in an introduction. Brackets are permitted only for needed unknown personal specifics; omitting an unnecessary detail is preferable.

Claude facts checked on 2026-09-06 against primary documentation before the style trials:

- [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works#the-context-window): context includes tool results and instructions; older outputs may be cleared and history compacted; early details can be lost. Deferred tools and skills make the earlier draft's claim that all schemas are always loaded unreliable.
- [Prompt caching](https://code.claude.com/docs/en/prompt-caching): reuse depends on a matching prefix and an unexpired cache. Lifetimes and defaults depend on request type, billing, and configuration. No universal five-minute claim is warranted. The subsequent trials avoid numerical rates or lifetimes.
- [Manage costs](https://code.claude.com/docs/en/costs#track-your-costs): session dollar estimates and actual billing differ; included subscription usage is not a per-request invoice. A price claim must identify the billing context. The trials use API cost where a cash comparison is necessary.

The intros do not assert measured rankings or savings. Observations about a failed attempt preventing repeated work are conditional reasoning, not benchmark findings. Factual citations may accompany a paragraph; they are not a style source or a substitute for the narrator's voice.

### Claude round 1 — SKILL.v1, full fresh read

#### Draft

Clearing a Claude Code session halfway through a bug can mean having to explain why an apparently sensible fix won't work. The old session already had that explanation. I'd want to keep it, even if the investigation that produced it left a lot of text behind.

That makes context cleanup a question of value as well as size. A failed attempt may still be useful evidence. A successful search may have returned pages that no longer matter. The amount of space each occupies doesn't tell you how much of the investigation you'd have to repeat without it.

Cost adds another consideration. Cached input is cheaper to read again, so a large context needn't be expensive in proportion to its size. But it still takes up space. Before deciding what to remove, I'd want to understand how the cost of preserving the work compares with the cost of reconstructing it. That means looking at what the session contains and what happens to it as the work continues.

#### Review against every feedback entry

| Entry | Finding |
|---|---|
| 1 | No consensus, fabricated past event, coined term, or promised surprise. The conditional debugging case has honest standing. |
| 2 | Three paragraphs, but “question of value as well as size” and “Cost adds another consideration” delay concrete explanation. Brevity alone does not clear this complaint. |
| 3 | No reversal/Q&A/colon routine; last sentence drifts into a plan announcement. Needs repair. |
| 4 | No app-opening instruction, capacity placeholder, or volatile number. |
| 5 | No unsupported share or population claim. |
| 6 | The opening sets a problem, but paragraph two partly answers the sorting question, and paragraph three supplies a cache lesson. The title's investigation is drifting toward a cleanup guide. Needs repair. |
| 7 | The narrator already knows why prior investigation matters; no novice discovery. |
| 8 | No ToolSearch-first account or size-times-duration formula. “Cached input is cheaper” should explicitly concern API input cost if retained. |
| 9 | No memory lesson. The cache paragraph is still too close to reciting another familiar foundation without a specific observation. |
| 10 | **Fail.** “Cost of preserving the work” versus “cost of reconstructing it” sounds analytical but leaves the actual acts vague. “That makes context cleanup a question of value” is an essayist labelling the point, not a colleague explaining it. |
| 11 | The first paragraph has a speaking voice, but later paragraphs lack the directness of “the reread is cheap.” The closer is less concrete than the anchor's actual investigation. No false measurement claimed. |

Verdict: fail. The attempt improves reader level but loses voice as it becomes abstract. It also narrows the article prematurely to context cleanup. A useful hook must not silently change the requested topic.

Skill repair for v2: keep the concrete objects and acts through the explanation instead of summarizing them as value, preservation, or reconstruction. Check that the hook leads into the requested question, not a neighboring article. An intro needs a stake in that question, not an abstract label for it.

### Claude round 2 — SKILL.v2, full fresh read

#### Draft

A one-line fix can leave a long Claude Code session behind it. The useful part may be the failed attempts that explain why the fix is so small. I wouldn't want to lose those halfway through debugging. I also wouldn't assume that everything in the session deserves to stay just because getting this far took effort.

The bill makes that judgment harder. If you're paying through the API, changing models can make the next request reprocess the conversation without using the previous model's cache. The text hasn't changed, but reading it has become more expensive. A large session that stays cached presents a different problem: it can be cheap to continue even while you're running short of room. [Claude Code's caching documentation](https://code.claude.com/docs/en/prompt-caching#switching-models).

I'd want to trace both the space and the spending before deciding what to cut. That means identifying what was loaded at the start, following the results added during the work, and checking when the cache stopped covering them. With that account, we could distinguish context that is useful, context that is harmless, and context that is costing more than it contributes.

#### Review against every feedback entry

| Entry | Finding |
|---|---|
| 1 | No invented history, consensus, or reported measurement. Last sentence invents a tidy classification without evidence for assigning its labels. |
| 2 | First paragraph now connects through recognizable work. Third spends words naming the intended analysis twice. |
| 3 | **Fail.** “That means” introduces a three-part plan, followed by a second three-part taxonomy. No literal banned reversal is needed for the same performed structure to recur. |
| 4 | No setup tutorial, window limit, or numerical placeholder. |
| 5 | No quantitative claim about shares. “Can be cheap” remains too loose without a comparison; the supported assertion is that a cached read has a lower rate. |
| 6 | **Fail.** Paragraph three starts dispensing the body as an outline and suggested classification. The cache contrast in paragraph two is enough explanation to establish an inquiry; the third over-organizes it. |
| 7 | The narrator weighs failed attempts rather than discovering context for the first time. |
| 8 | A verified model-switch example supplies a relevant complication, rather than a ToolSearch definition or invented cost equation. |
| 9 | No basic memory explanation. Paragraph two assumes the reader knows a cache and uses the model-switch consequence to motivate accounting. |
| 10 | “Presents a different problem,” “trace both the space and the spending,” and the closing taxonomy sound prepared. The first paragraph's voice is stronger. |
| 11 | “The text hasn't changed” and the concrete model switch approach the anchor's directness. “Context that is harmless” claims a judgment the intro has not earned. |

Verdict: fail. The expert observation is usable, but the ending still performs a structure. The rule against outlines needs to cover parallel classifications and plans even when phrased as a narrator's intention.

Skill repair for v3: don't fill the final introductory paragraph by naming dimensions, categories, or steps; let it say why the unresolved comparison matters to a decision. Remove “cheap” as a freestanding cost conclusion when the evidence establishes only a lower rate. Keep this a general judgment rule, without prescribing a particular last sentence.

### Claude round 3 — SKILL.v3, full fresh read

#### Final intro: Claude Code Context Window: What Fills It, What It Costs

A one-line fix can leave a long Claude Code session behind it. Some of that history explains why the fix is so small. I'd hesitate to clear it while the bug was still open: a failed approach can be worth keeping if it stops Claude from trying the same thing again.

But looking at the length of the session only gets you so far. Switch models midway through it and the new model can't use the old model's prompt cache. If you're paying through the API, you can pay to process the same history again without having added anything substantial to it. The decision to switch may be sensible. Its cost still belongs in the account. [Claude Code's caching documentation](https://code.claude.com/docs/en/prompt-caching#switching-models).

I'd like to be able to look at a session and explain where the money went. A long transcript gives me somewhere to start, but it doesn't tell me what to change. Before cutting down a tool result or stripping instructions out of CLAUDE.md, I want to know how much that would actually save.

#### Review against every feedback entry

| Entry | Finding |
|---|---|
| 1 | No population premise or invented event. “I'd hesitate” and “I'd like” state a present judgment; no actual debugging session, bill, or measurement is claimed. No coined framework, tease, or punchline. |
| 2 | Three paragraphs. The first establishes why retaining investigation has value; the second complicates the cost account; the third makes that account matter to a decision. The within-round final read removed a sentence that repeated the reason for retaining history. |
| 3 | No staged reversal, rhetorical Q&A, revelation, trio, or announced section plan. The colon after “open” gives an immediate reason for hesitation rather than staging a discovery. This is a literal causal use, not the banned colon-reveal device. |
| 4 | No instruction to open the app or discover its window. No capacity, rate, or placeholder number. “One-line fix” describes a possible case, not a fabricated measurement. |
| 5 | “Some of that history” identifies evidence in the hypothetical debugging case, not a measured share or an assertion about typical users. No most/everyone claim. |
| 6 | Backstory is a recognizable debugging predicament; why is the value and expense of retaining work; what is explaining a session's cost before changing it. Component accounting, measurements, pricing details, and remedies remain for the body. |
| 7 | The author already understands the value of failed attempts. No astonishment about tool results or retained history. |
| 8 | One checked model-switch consequence makes a cost account based on transcript size insufficient. No tool definition first and no duration formula. The claim is scoped to API payment. |
| 9 | No lesson on LLM memory, requests, context, or what a cache is. Model-specific cache reuse is a concrete reason the accounting problem deserves attention. |
| 10 | “Trying the same thing again” and “where the money went” keep ordinary acts in the explanation. “Its cost still belongs in the account” is slightly more written than those phrases but states the relevant inclusion, not a slogan or new abstraction. |
| 11 | Borrows the anchor's directness and progression into a real inquiry. Does not copy its generic opener, all-tools assumption, fixed TTL, unsupported token shares, universal billing, or imaginary measurement. The quieter first-person judgments supply voice without imitating “rounding error.” |

Verdict: meets the trial's requirements on this self-review. No claim of Ninad's acceptance. The candidate idea is that useful investigative history and paid input cannot be judged from transcript length alone. The failed-approach case supplies its practical stake; the checked cache consequence earns the need for a better account. This introduction motivates an analysis; it does not prove a measured saving or demonstrate full-essay depth.

### Contractor round 1 — SKILL.v3, full fresh read

#### Draft

I lost about ₹20 lakh to an interior contractor working on my home. A loss like that ought to make it harder for the person responsible to get the next job. I want to understand why a contractor can so easily start again with another homeowner.

When you're choosing someone, you can look at the rooms they've finished. The photos may be genuine and the rooms may be beautiful. But they leave out what the owner was promised, what it took to get the work finished, and how much the agreement changed along the way. The contractor gets to show the result without the argument that preceded it.

A bad job should make its way into the next customer's decision. Referrals and reviews are supposed to help that happen. Yet a contractor choosing which projects to show can keep the unhappy customer out of the picture. I'd want to know how much of a previous job a new homeowner can actually check before paying an advance.

#### Review against every feedback entry

| Entry | Finding |
|---|---|
| 1 | Supplied loss is legitimate standing. **Fail:** “so easily start again” imports an unobserved outcome from the title. No evidence of later bookings was supplied. |
| 2 | Three compact paragraphs with no invented chronological scene. First paragraph's second sentence states a reasonable expectation, but the following claim outruns it. |
| 3 | No staged Q&A or reversal sequence. The photo paragraph naturally has several missing facts, but its final “argument that preceded it” invents an argument. |
| 4 | No irrelevant setup, changing facts, or placeholder numbers. Only the confirmed loss is quantified. |
| 5 | **Fail:** the ease claim is a prevalence implication without a quantity word. “Can keep the unhappy customer out of the picture” ignores routes a contractor doesn't control. |
| 6 | Does not sell certification or summarize laws and remedies. The inquiry is relevant, but a selected portfolio is already treated as sufficient explanation of evasion. |
| 7 | No naïve surprise that a portfolio omits things. Personal harm is used to ask about another buyer's information, not to invent the author's original belief. |
| 8 | Starts from a loss and a hiring decision, not a proposed trust mark. The mechanism lacks the limits imposed by independent references and reviews. |
| 9 | No elementary lecture defining reputation. |
| 10 | “So easily” and “keep ... out of the picture” make the account glib. A picture metaphor obscures the exact claim about what the next buyer can discover. |
| 11 | Directness in “The photos may be genuine and the rooms may be beautiful” is useful, but the anchor's tone cannot justify a leap from one person's loss to another person's continued success. |

Verdict: fail. Conditional phrasing is insufficient when the claim quietly includes ease, intentional concealment, or an observed sequence. The portfolio is one source of evidence; it cannot stand for everything a prospective client can learn.

Skill repair for v4: distinguish an observed bad outcome, an opportunity for repetition, and evidence that repetition occurred. Test independent information channels before claiming that one party controls what another can know. Adjectives such as “easy” can assert unsupported frequency or friction just as “most” can.

### Contractor round 2 — SKILL.v4, full fresh read

#### Draft

I lost about ₹20 lakh to an interior contractor working on my home. If another homeowner were considering hiring him, I'd want them to be able to find out what happened before paying. My experience ought to be useful to someone who hasn't committed their money yet.

A portfolio can contain genuine photographs and still leave a prospective client badly informed. A room may look good even if getting it finished cost the owner far more than agreed. The photograph gives you no way to tell whether that happened. You need to hear from the person who paid for the room.

A referral can supply that part of the story. So can a review with enough detail to check. The question is how reliably that information reaches someone choosing a contractor in India, especially when the contractor supplies the references. I'd want to understand where that process fails before claiming to have a way to fix it.

#### Review against every feedback entry

| Entry | Finding |
|---|---|
| 1 | No invented later client; the first paragraph is explicitly conditional. The confirmed loss is the sole autobiographical event. No consensus, teaser, or fake project. |
| 2 | Three paragraphs; first paragraph's third sentence mostly repeats the second. It should earn more space or go. |
| 3 | No reversal routine, Q&A, or outline. No count-driven trio. |
| 4 | No irrelevant setup or invented figure. Unknown personal specifics are omitted rather than bracketed into a scene. |
| 5 | No prevalence asserted. “How reliably” asks for evidence rather than supplying a made-up answer. |
| 6 | Establishes the hiring-information question and leaves causes, evidence, and remedies for the body. Last sentence about “claiming to have a way to fix it” brings the writing process into the intro. |
| 7 | Narrator has a concrete stake, without a novice's revelation or invented former beliefs. |
| 8 | Mechanism begins with what evidence a buyer can inspect. No certification scheme or legal account is introduced as the answer. |
| 9 | Portfolio and referral are used, not defined. |
| 10 | **Fail on voice and precision:** “The question is how reliably that information reaches someone” retreats from the person paying into an analytic label. “You need to hear from the person” also turns one valuable source into a necessity; records might establish parts of the same history. |
| 11 | “Genuine photographs” and the cost of finishing the room make a concrete distinction. The last paragraph is cooler and more editorial than the anchor's direct speech. Its closing announces responsible intentions instead of showing what needs explaining. |

Verdict: fail. It fixes the invented market history, but overcorrects into detached commentary. The intro can ask an honest question without ending on a statement about how the author plans to reason. The evidence-source prescription also needs a boundary.

Skill repair for v5: keep uncertainty attached to the actual missing fact rather than narrating your responsible writing process. Don't finish by saying you need to understand a problem before fixing it; say what about the problem still resists explanation. Distinguish one useful way to establish a fact from the only way to establish it.

### Contractor round 3 — SKILL.v5, full fresh read

#### Final intro: Why Interior Contractors in India Get Away With It

I lost about ₹20 lakh to an interior contractor working on my home. What I learned from that job could be useful to someone who still has their money.

A contractor can show you a beautiful room and be telling the truth about having built it. The owner might still have paid far more than agreed, or had to bring someone else in to finish the work. You wouldn't learn either of those things from the photograph. A genuine example of someone's work can leave you with a badly mistaken idea of what hiring them will be like.

A candid referral can fill in that history. So can a review with details you can check. But if the next buyer sees only the projects the contractor chooses to show, a failed job may never enter the decision. I want to understand what keeps a warning from reaching someone choosing a contractor in India before they pay an advance.

#### Review against every feedback entry

| Entry | Finding |
|---|---|
| 1 | The loss and home are supplied. Usefulness to another homeowner is conditional; no later booking, dispute, contract, or outcome is reported as fact. No population premise, invented business, tease, coined term, or clever closing. |
| 2 | Three paragraphs. The second sentence gives the experience a use before another buyer pays. The within-round final read removed an intervening sentence that made the same point twice. No ornamental scene or bracketed narrative. |
| 3 | No revelation frame, rhetorical Q&A, repeated reversals, trio kicker, or article outline. The turn from photos to a fuller history comes from what a photograph can establish. |
| 4 | No setup tutorial or volatile number. The only amount is the confirmed approximate loss. No unknown specifics are necessary to this account, so no brackets are used. |
| 5 | No most/everyone claim or invented rate. “Might” presents possible histories, not what happened on Ninad's job. The next buyer's limited information is an explicit condition. |
| 6 | Backstory is the loss; why is the value of that experience to someone who has not paid; what is whether and how a warning reaches the hiring decision. No certification pitch, legal diagnosis, or complete list of causes. |
| 7 | No discovery that contractors can fail or photos can be selective. The narrator examines the gap between genuine evidence of work and evidence of what hiring the person involved. |
| 8 | Starts with an actual consequence and proceeds to evidence available before hiring. The mechanism is limited to a failed job's possible absence from a later sale; it does not claim to explain every meaning of “get away with it.” |
| 9 | No lecture defining trust, reputation, or contracting. The reader is presumed able to judge a reference and an agreement. |
| 10 | “Someone who still has their money,” “bring someone else in,” and “what hiring them will be like” sound like a person weighing what happened. No equation, grand analogy, invented term, or process disclaimer. The final sentence names the missing event, a warning reaching the buyer. |
| 11 | Concrete acts and a speaker's stake supply the anchor's useful directness. No borrowed measurements or exaggerated certainty. The inquiry is open without promising a discovery already made. |

Verdict: meets the trial's requirements on this self-review. No claim of user acceptance. The candidate idea is that accurate evidence of a finished room can be poor evidence of the experience of hiring its contractor. The two possible histories earn that distinction. Referrals and reviews limit the explanation: continued evasion requires a failure to connect useful evidence with the next decision. The intro asks where that failure occurs; the body would need actual cases to answer it for India. The claim is not that India is uniquely prone to this mechanism.

### Check after the last skill repair

Rechecked Claude round 3 against v5's additions: its current judgment is attached to the concrete unknown saving; it does not end with a generic promise to investigate responsibly. The source attribution supports the specific model-switch claim and does not purport to be the only way to establish cost. Contractor round 3 keeps potential recurrence separate from reported recurrence. No further rule change was needed.

These six trials assess openings and their connection to a possible body. They do not establish one-shot reliability on unseen topics, sustained depth over a full essay, or external acceptance. The four failed drafts are retained because they show that a readable rule can still be misapplied.

Final line edit within the third rounds: removed “Getting the answer took work, and I'd want to keep the parts that could save doing that work twice” from Claude's first paragraph; removed “If another homeowner were considering hiring him, I'd want them to know what happened before paying” from the contractor's first paragraph. Both repeated an adjacent sentence. The remaining clauses preserve the conditional standing and the reason to care. No new rule was necessary: the existing final-read and long-windedness checks called for the cuts. The final intros above include these edits.
