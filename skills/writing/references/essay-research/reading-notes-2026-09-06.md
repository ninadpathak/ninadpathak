# Fresh reading: understanding, order, and the reader

## Scope and method

Fetched the links on [Essays](https://paulgraham.com/articles.html) again on 2026-09-06. The current index yielded 231 distinct local HTML pages and two external ANSI Common Lisp chapter texts. The HTML pages, stripped text, index, fetch script, and hashes are under `/tmp/pg-codex/`; `fresh-corpus-manifest.json` preserves the inventory here. Fetching was sequential with a 0.65-second pause before each HTML request and retry backoff. The two chapter texts were fetched separately with a pause. No request concurrency.

Read entries 1–60 completely, newest to oldest, from *How Universities Should Prepare Founders* through *Life is Short*, including notes and acknowledgments. Long essays were read in consecutive word chunks; truncated tool output was reread in smaller portions. The ledger below records each essay, rather than treating a search result or opening as a whole reading. Additional pages were fetched for archive coverage and quotation verification, not claimed as closely read.

The earlier 232-essay measurements remain historical data. The current index count is not forced to match them. HTML layout, page revisions, date stripping, notes, and sentence splitting can change totals. New mechanism positions below use their own declared method; they do not silently replace the archived thesis positions.

## What the earlier rules missed

### Understanding is visible in dependencies

In [The Brand Age](https://paulgraham.com/brandage.html), the currency change matters because it changes the foreign buyer's price. The accuracy figures matter later because a luxury watch must still keep tolerable time. Different numbers answer different questions at different stages. “Add an exact number” loses the reason for either one. The essay also qualifies the proposed mechanism: branding does not make quality irrelevant.

[The Airbnbs](https://paulgraham.com/airbnbs.html) gives rent and food costs to explain the survival threshold, then searches to explain the choice of New York, then visits and photographs to explain the work, then weekly receipts to establish growth. A scene and an exact number are useful because they carry evidence into the next inference. They are not signs to sprinkle into a paragraph.

[Billionaires Build](https://paulgraham.com/ace.html) explains why YC can use founders as domain experts only after establishing the interview's time constraint and the need to judge an uncertain market. The detail about answering questions rather than delivering a pitch follows from how that judgment gets made. This is the kind of operational specificity missing from the rejected Claude drafts.

### Conversational first principles start nearby

[How to Convert Between Wealth and Income Tax](https://paulgraham.com/winc.html) uses an assumed return and a small worked balance. It does not begin with the invention of money or a lesson on taxation. The denominator is stated; the arithmetic then shows what it does. The assumptions remain visible. The claim is a model, not a universal contemporary conversion rate.

[Modeling a Wealth Tax](https://paulgraham.com/wtax.html) starts with a founder's holding period and explains the fraction retained each year before applying the exponent. That is different from leading with an “area under the curve” and asserting that caching changes a coefficient. The reader has to know what each repeat does before a formula becomes useful.

[Donate Unrestricted](https://paulgraham.com/donate.html) derives the problem from who knows where the money is needed. It then admits umbrella organizations and informed donors. A description of donor motives follows the mechanism, rather than substituting for it. This supports testing the contractor argument against referrals before announcing that reputation is absent.

### The reader's knowledge changes the route

[The Shape of the Essay Field](https://paulgraham.com/field.html) explicitly makes the reader's reason for not knowing part of the writer's problem. Its conclusions about audience are PG's argument, not instructions to write every article for beginners. The Claude reader has daily practice; a basic model-memory explanation starts too far away.

[Putting Ideas into Words](https://paulgraham.com/words.html) distinguishes what the author has in mind from what a stranger can reconstruct on the page. The problem is missing connections, not just missing facts. [How to Write Usefully](https://paulgraham.com/useful.html) also distinguishes novelty from surprise: articulating something tacit can be valuable. A requirement for a dramatic second-order revelation would create another performance ritual.

[How to Think for Yourself](https://paulgraham.com/think.html) can assume the reader knows publication and prices, then explain why correctness alone is insufficient in certain work. [The Lesson to Unlearn](https://paulgraham.com/lesson.html) acknowledges experienced students' knowledge and examines what their familiar behavior implies. A clause of recognition avoids retelling their education to them.

### Backstory and explanation are not separate compartments

[Having Kids](https://paulgraham.com/kids.html) needs the writer's former view, its evidence, and how his sample was biased. The surprise is a corrected inference from experience. [Coronavirus and Credibility](https://paulgraham.com/cred.html) moves quickly from observed predictions to the conditions under which predictions are falsified. Both explain early, at different speeds.

Draft 11 starts with a familiar operation, identifies its relevant contents, follows their accumulation, and brings in caching to motivate measurement. Draft 9 retreats to a beginner's definition. Draft 10 puts an abstraction before the event it abstracts. The difference is explanatory order, not sentence length. The rewrite preserves the first route, without copying draft 11's unverified quantities or invented measurement claim into a new article.

### PG's corpus is not Ninad's permission slip

The fresh essays contain recaps, rhetorical Q&A, broad generalizations, analogies, and long openings. *Life is Short* recaps. *The Reddits* and *What I Worked On* need extended histories. *Haters* deliberately repeats a paragraph shape with its signs reversed. The old “at most once per essay” claim is not a dependable corpus finding. The rewrite removes such devices as prescriptions because they failed Ninad's task. It does not misreport their absence in PG.

The narrator admits uncertain causes and incomplete knowledge, including ordinary personal limitations. Expertise is established by the quality of the account and the evidence, not a rule against admitting ignorance. The skill therefore forbids fabricated expertise and vague hedging while preserving explicit limits on a claim.

## Measured onset of explanation

This purposive 12-essay sample spans short arguments, technical/economic explanations, and longer personal/historical openings. It is not a random sample, and no population median or opening deadline is inferred from it.

Count: whitespace-delimited words before the selected explanatory step, excluding the prepended title and initial month/year. Paragraphs: nonempty blocks separated by blank lines in the extracted body. Locators and coding reasons are in `mechanism-positions.tsv`. Coding identifies the first subject-relevant explanatory step, not necessarily a complete causal theory. Author-standing explanations are excluded. This judgment is explicit because “mechanism begins” is not an objective regex feature.

| Essay | Words before explanation | Extracted paragraph | What begins there |
|---|---:|---:|---|
| How Universities Should Prepare Founders | 79 | 3 | Product demands determine useful preparation. |
| How to Convert Between Wealth and Income Tax | 74 | 4 | Return on capital links the two bases. |
| The Brand Age | 36 | 2 | Competitive pressure, before currency and quartz. |
| The Shape of the Essay Field | 31 | 2 | Causes of reader ignorance. |
| Good Writing | 110 | 3 | An inference from joint optimization; the positive causal account is later. |
| Putting Ideas into Words | 29 | 1 | Word choice exposes imprecision. |
| How People Get Rich Now | 101 | 3 | New fortunes alter the composition of the list. |
| Donate Unrestricted | 66 | 2 | Allocation differs from what the nonprofit would choose. |
| Modeling a Wealth Tax | 80 | 3 | The holding retained after one year's tax. |
| Coronavirus and Credibility | 69 | 2 | Prediction environments permit evasion. |
| Having Kids | 195 | 6 | Changed judgment attributed first to parenthood's effects. |
| The Risk of Discovery | 0 | 1 | Biographical selection distorts perceived risk. |

The sample is enough to disprove a universal “no mechanism in the first three paragraphs” rule. It does not prescribe putting a mechanism in paragraph two. The full explanation in *Good Writing* and the later selection-bias account in *Having Kids* also show why thesis position, explanatory onset, and completed explanation must not be conflated.

## Whole-essay ledger

Each row records the route of the whole argument and a lesson relevant to this rewrite. These are reading judgments, not measurements of author intent or endorsements of every factual claim.

| # | Essay | Explanatory route and lesson |
|---:|---|---|
| 1 | [How Universities Should Prepare Founders](https://paulgraham.com/prepare.html) | YC's vantage → builder competence → educational environment and projects. The curriculum conclusion follows from what founders must actually do. Standing is relevant, not decorative biography. |
| 2 | [How to Earn a Billion Dollars](https://paulgraham.com/earn.html) | Political claim → startup creation → founder outcomes and constraints. The scale calculations establish possibility; do not copy the polemical foil as a mandatory hook. |
| 3 | [How to Convert Between Wealth and Income Tax](https://paulgraham.com/winc.html) | Conversion claim → stated return assumption → worked balances → implications and qualifications. Numbers are model inputs, not timeless constants. |
| 4 | [The Brand Age](https://paulgraham.com/brandage.html) | Japanese competition, currency, quartz → luxury repositioning → persistence of quality requirements. A long history earns the generalization through separate mechanisms. |
| 5 | [The Shape of the Essay Field](https://paulgraham.com/field.html) | Reasons readers do not know → audience implications → surprise and reach. Reader calibration precedes the audience conclusion. |
| 6 | [Good Writing](https://paulgraham.com/goodwriting.html) | Distinction → personal evidence of joint improvement → layout constraints → relation between sound and thought. A pleasing sentence is investigated, not accepted as evidence of truth by itself. |
| 7 | [What to Do](https://paulgraham.com/do.html) | Candidate answers are refined by their deficiencies, with later practical implications. Revision is doing intellectual work here; imposing a wrong-answer-first template elsewhere would be theatrical. |
| 8 | [The Origins of Wokeness](https://paulgraham.com/woke.html) | Historical comparison → institutional spread → responses under pluralism. Separate the proposed explanatory category from agreement with its contested claims. The author's polemical register is not mandatory. |
| 9 | [Writes and Write-Nots](https://paulgraham.com/writes.html) | New means of avoiding writing → loss of enforced practice → division in thinking ability. Technological change is connected to a behavior it removes, without an API tutorial. |
| 10 | [When To Do What You Love](https://paulgraham.com/when.html) | Timing choice → risk and obligations → paths with different tradeoffs. Conditions drive the advice; the slogan alone would omit them. |
| 11 | [Founder Mode](https://paulgraham.com/foundermode.html) | Chesky's talk → repeated mismatch with received management advice → hypotheses about founder involvement. The admitted lack of a complete theory matters. A catchy name is not proof. |
| 12 | [The Right Kind of Stubborn](https://paulgraham.com/persistence.html) | Persistence versus obstinacy → question of retrospective labeling → observed responses to criticism → behavior-based distinction. The counterexample tests the distinction instead of supplying a straw opponent. |
| 13 | [The Reddits](https://paulgraham.com/reddits.html) | Founders' history and changing circumstances support an assessment of them. It needs narrative duration; an 80-word anecdote ceiling would damage it. |
| 14 | [How to Start Google](https://paulgraham.com/google.html) | Young audience → technical ability and own projects → future cofounders and ideas. Basics are appropriate to this audience, not to every technical audience. |
| 15 | [The Best Essay](https://paulgraham.com/best.html) | What valuable essays could do → exploration, selection, and constraints of the medium. Claims grow out of the work of finding ideas rather than a catalogue of sentence shapes. |
| 16 | [Superlinear Returns](https://paulgraham.com/superlinear.html) | Familiar proportional model → mechanisms producing nonlinear returns → domain cases → practical implications. The many cases separate mechanisms; reproducing only the bold opening would lose the explanation. |
| 17 | [How to Do Great Work](https://paulgraham.com/greatwork.html) | Choose work → build knowledge → notice gaps → pursue curiosity → methods, obstacles, and conditions. Length tracks interacting problems; the archived median is not a maximum. |
| 18 | [How to Get New Ideas](https://paulgraham.com/getideas.html) | Observing anomalies → question what was taken for granted. The anomaly has to come from knowledge, not a manufactured contradiction. |
| 19 | [The Need to Read](https://paulgraham.com/read.html) | Reading's relation to thought → limits of substitute media. It assumes an educated reader and makes the relation itself the subject. |
| 20 | [What You (Want to)* Want](https://paulgraham.com/want.html) | Successive preferences reveal a problem with a simple account of wanting. Revisions expose a real conceptual difficulty; they are not merely hooks. |
| 21 | [Alien Truth](https://paulgraham.com/alien.html) | Writing conventions → what would remain true without humans. The hypothetical probes dependence on audience and convention. |
| 22 | [What I've Learned from Users](https://paulgraham.com/users.html) | Occasion for reflection → repeated founder problems → implications for helping users. Advice has a defined observed population. |
| 23 | [Heresy](https://paulgraham.com/heresy.html) | Historical reading → changed interpretation → contemporary social costs of speech. The surprise concerns a comparison across time, not ignorance of the basic source. |
| 24 | [Putting Ideas into Words](https://paulgraham.com/words.html) | Articulation exposes defects → neutral reader reconstruction → changes to thought. The reader cannot fill gaps with what remains in the author's head. |
| 25 | [Is There Such a Thing as Good Taste?](https://paulgraham.com/goodtaste.html) | Inherited view → practice and improvement → argument about judgment. The personal premise is evidence he actually has, not a license to invent the author's father. |
| 26 | [Beyond Smart](https://paulgraham.com/smart.html) | Familiar account of Einstein → importance of generating ideas → implications for evaluating ability. The relevant distinction is operational, not simply a more impressive adjective. |
| 27 | [Weird Languages](https://paulgraham.com/weird.html) | Unusual languages → different mental resources → learning consequences. It assumes programming knowledge and explains why unfamiliar choices matter. |
| 28 | [How to Work Hard](https://paulgraham.com/hwh.html) | Personal calibration → kinds and amounts of work → honest attention to productive limits. The practical account is more than exhortation to exert effort. |
| 29 | [A Project of One's Own](https://paulgraham.com/own.html) | Son's project → self-directed work → implications for learning and motivation. The ordinary event matters for the inference; the narrator is not astonished that children write. |
| 30 | [Fierce Nerds](https://paulgraham.com/fn.html) | Apparent social diffidence → selection of setting → behavior in work. It explains why an observer sees the misleading sample. |
| 31 | [Crazy New Ideas](https://paulgraham.com/newideas.html) | Initial implausibility → how to respond to a proposed idea. An unconventional appearance alone does not establish that an idea is good. |
| 32 | [An NFT That Saves Lives](https://paulgraham.com/nft.html) | Specific fundraising offer and beneficiary. This is an announcement with a practical purpose; it cannot establish a universal essay structure. |
| 33 | [The Real Reason to End the Death Penalty](https://paulgraham.com/real.html) | Irreversible punishment and fallible decisions → objection to the institution. Treat as analysis of argumentative structure, not current legal guidance. |
| 34 | [How People Get Rich Now](https://paulgraham.com/richnow.html) | Dated list comparison → sources of changed composition → historical company formation. A denominator can change a proportion without the assumed change to its numerator. |
| 35 | [Write Simply](https://paulgraham.com/simply.html) | Own practice → demands on the reader → economy of language. Ordinary wording lets complex content remain visible; simplicity is not an instruction to explain elementary facts. |
| 36 | [Donate Unrestricted](https://paulgraham.com/donate.html) | Allocation knowledge → exceptions → donor behavior → decision. Exceptions improve the conclusion instead of merely softening the tone. |
| 37 | [What I Worked On](https://paulgraham.com/worked.html) | Actual sequence of projects, constraints, and changes of direction. Tool and career choices are intelligible within their circumstances. It refutes a generic ban on long backstory. |
| 38 | [Earnestness](https://paulgraham.com/earnest.html) | Meaning of a founder assessment → motives, strength, vulnerability → domains where it matters. The article supplies boundaries instead of extending one trait to all success. |
| 39 | [Billionaires Build](https://paulgraham.com/ace.html) | YC judgment → user knowledge → evidence under uncertainty → interview behavior → motivation. Domain knowledge appears as answers to specific questions, including what can go wrong. |
| 40 | [The Airbnbs](https://paulgraham.com/airbnbs.html) | Early evidence of earnestness → survival → geographic focus → receipts. Exact costs and dates answer distinct practical questions. |
| 41 | [How to Think for Yourself](https://paulgraham.com/think.html) | Work requiring independent correctness → social environment → components and ways to cultivate them. The component breakdown follows the need for it. |
| 42 | [Early Work](https://paulgraham.com/early.html) | Fear of poor initial work → social and personal judgment → techniques → revised evaluation. It distinguishes necessary standards from their mistimed application. |
| 43 | [Modeling a Wealth Tax](https://paulgraham.com/wtax.html) | Annual retention → lifetime multiplication → threshold variant → compounding. The procedure makes the claim inspectable before naming it. |
| 44 | [The Four Quadrants of Conformism](https://paulgraham.com/conformism.html) | Proposed axes → recognizable behaviors → institutions and free inquiry. The taxonomy is the substantive model being defended, not a generic formatting technique. |
| 45 | [Orthodox Privilege](https://paulgraham.com/orth.html) | Differing perceived safety of speech → dependence on one's beliefs → limits of persuasion. It explains a viewpoint rather than merely calling its holders bad. |
| 46 | [Coronavirus and Credibility](https://paulgraham.com/cred.html) | Observed confidence → accountability of predictions → unusually clear falsification. Relevant to the contractor topic's question of when a failure reaches later decisions. |
| 47 | [How to Write Usefully](https://paulgraham.com/useful.html) | Correctness plus specificity, importance, novelty → revision practices → qualification → reader conflict. Precision must not outrun evidence; qualification is part of thinking. |
| 48 | [Being a Noob](https://paulgraham.com/noob.html) | Personal discomfort → local versus wider knowledge → possible evolutionary explanation. Ordinary ignorance is admitted; causal speculation is marked as such. |
| 49 | [Haters](https://paulgraham.com/fh.html) | Mirrored fan/critic behavior → distinction from dispute → practical response. Deliberate paragraph repetition is present in the corpus, but unsuitable as a reusable instruction here. |
| 50 | [The Two Kinds of Moderate](https://paulgraham.com/mod.html) | Different routes to the same average → distributions of positions → pressures on independent thinkers. Simple numbers make a distinction inspectable. |
| 51 | [Fashionable Problems](https://paulgraham.com/fp.html) | Observed concentration of effort → unexamined space → interest as protection. The short essay does not need an anecdote or fabricated epiphany. |
| 52 | [Having Kids](https://paulgraham.com/kids.html) | Former fear → new experience → biased observations → real costs and benefits. Personal evidence is examined, not made representative by confidence alone. |
| 53 | [The Lesson to Unlearn](https://paulgraham.com/lesson.html) | Grades → hackable proxies → founder behavior → work chosen by its tests. The surprising connection comes after a familiar mechanism is understood. |
| 54 | [Novelty and Heresy](https://paulgraham.com/nov.html) | Non-obvious ideas beneath assumptions → resistance → effects on exploration. Causal sequence carries the short piece. |
| 55 | [The Bus Ticket Theory of Genius](https://paulgraham.com/genius.html) | Disinterested obsession → historical cases → uncertainty and unsuccessful bets → cultivation. The uncertainty is real and survives the memorable label. |
| 56 | [General and Surprising](https://paulgraham.com/sun.html) | Two sources of value → small novelty on a general idea → persistence in exploration. It permits modest discoveries; constant dramatic revelation is unnecessary. |
| 57 | [Charisma / Power](https://paulgraham.com/pow.html) | Exposure from power plus lack of charisma → public dislike. An extremely short explanatory sketch; no forced three-paragraph introduction. |
| 58 | [The Risk of Discovery](https://paulgraham.com/disc.html) | Biographical selection → hindsight → Newton's bets. Mechanism begins in the first sentence; the historical case makes it concrete. |
| 59 | [How to Make Pittsburgh a Startup Hub](https://paulgraham.com/pgh.html) | Youth migration → housing and urban character → university, tolerance, capital. The demographic number acquires meaning from the number of people and the city's circumstances. |
| 60 | [Life is Short](https://paulgraham.com/vb.html) | Finite repeated experiences → use of time → forced/chosen waste → loss and attention. Counts convert an abstraction into lived opportunities; its recap is a real counterexample to the old corpus claim. |
