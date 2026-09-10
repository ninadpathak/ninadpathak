# Briefs for a technical-writing practice

Dated 10 September 2026. These are candidate briefs under [the strategy](technical-writing-strategy-2026-09.md), with capacity for four substantial refreshes and up to two new experiment pages during the first quarter.

The hypotheses below are untested unless a source is explicitly named. A future writer must save the environment and raw results before drafting a result headline, and Ninad must confirm a personal recollection before it is written in his voice.

## Repairing the tutorial that cannot be copied

**Working title:** Can a reader run this tutorial without its author?

**Placement and intent:** Refresh `/articles/how-to-write-a-technical-tutorial-that-actually-teaches/`. Serve the practical tutorial-design task; the exact query `how to write a technical tutorial` returned volume 0 and KD 0, so the case for this repair is reader trust and an existing page, not traffic size.

**Hypothesis:** A guide can contain individually plausible snippets while withholding a dependency that prevents completion. The current `@example/webhooks` import provides a specific audit target, not evidence of a failed customer integration.

**Evidence and experiment:** Read the entire example sequence, identify declared prerequisites, and attempt it in a disposable environment. Save the unresolved import, implement a clearly labeled local fixture, and run the documented steps from an empty directory using pinned dependencies.

**Artifact:** A small fixture repository plus the exact before/after documentation diff. Capture expected output and a deliberate invalid-signature case; a successful import alone does not validate webhook security.

**Argument:** Start with the missing dependency, explain what the tutorial expected its reader to supply, then show how a completeness check catches it. Separate illustrative code from executable instructions before either appears.

**HN interest:** A writing guide that fails its own copy-paste test is inspectable and relevant to engineers. The discussion should concern the missing contract, without claiming Ninad previously made or discovered the error.

**Links and gate:** Link to the review checklist and onboarding guide. Hold the article if a clean run cannot reproduce the stated path, or if the fixture is still presented as a real vendor package.

## Filling the template before recommending it

**Working title:** A documentation template tested against a failed request

**Placement and intent:** Refresh `/articles/technical-documentation-template/`. Target `technical documentation template`, US volume 390 and KD 25; Semrush also returned the existing URL at position 65 for `code documentation template`.

**Hypothesis:** A template's headings can look complete while providing no place for an ambiguous operation result. A filled example can expose that omission before another team copies the structure.

**Evidence and experiment:** Build an explicitly hypothetical export service with a documented request contract. Fill the current template, then ask a reviewer to choose an action after a timeout using only the resulting pages.

**Artifact:** Filled Markdown pages and a recovery decision table, with the implementation fixture beside them. Record the reviewer's actual uncertainty; do not invent a completion-time improvement.

**Argument:** Present the filled template near the top, then examine the section that decides whether to retry. Keep the API-specific starter linked as a separate reader task.

**HN interest:** The template is useful even if the experiment finds that the existing structure already covers the failure. A null result can reveal which part of the template earned the reader's decision.

**Links and gate:** Link to technical-writing examples and the API template. Stop expansion if the fixture's contract is unsettled; document the unresolved promise before publishing instructions.

## Showing what changed between writing examples

**Working title:** Technical writing examples with the decisions left visible

**Placement and intent:** Refresh `/articles/technical-writing-examples/`. Target `technical writing examples`, volume 880 and KD 26, without creating a competing examples URL.

**Hypothesis:** Annotated original artifacts teach judgment that a list of admired documentation brands cannot supply. The returned SERP includes broad examples pages and a Reddit discussion, indicating that readers are comparing tangible examples.

**Evidence and experiment:** Use the same hypothetical service to produce a quickstart and a reference page. Give each a distinct task, change one consequential assumption, and show how that change alters the writing.

**Artifact:** Before/after pages with margin notes that point to the evidence behind the edit. Use a public documentation example only to establish an observable pattern, with a direct source and access date.

**Argument:** Open on an actual instruction from the fixture. Show the reader's decision before explaining the choice of document type.

**HN interest:** A comparison where a shorter sentence creates a worse instruction gives readers something precise to dispute. Do not predetermine that result; keep the version that the task supports.

**Links and gate:** Link to document types and the general template. Remove any example whose annotation merely praises clarity without showing its consequence.

## Documenting the retry a reader will actually write

**Working title:** Where an API retry example needs to create its key

**Placement and intent:** Refresh `/articles/api-documentation-best-practices-reference-guides-and-working-requests/`. Target `api documentation best practices`, volume 260 and KD 32; the reader wants to document behavior, not browse another API glossary.

**Hypothesis:** A page can define idempotency correctly while its example creates a fresh identity on each retry. The existing reader-assumptions essay identifies this possible error, but does not report a completed experiment.

**Evidence and experiment:** Create a local service fixture with explicit retention behavior. Run a dropped-response case using a new key per attempt and a stable key per operation, recording stored operations and responses.

**Artifact:** A small client/server pair with tests and a trace explaining what survived the simulated failure. Verify current vendor claims against primary documentation before citing a vendor as an example.

**Argument:** Start with the placement of key creation in the client. Explain the service guarantee only as far as needed to justify that placement and its limits.

**HN interest:** The code can pass a syntax check and still teach the wrong retry policy. A trace connects a writing choice to the resulting program behavior.

**Links and gate:** Link to the assumptions essay and API examples. Do not generalize the local fixture to an external provider's contract, and do not claim exactly-once side effects from key storage alone.

## Finding the docs change that a green build missed

**Working title:** My docs build passed after I broke the instructions

**Placement and intent:** Conditional new `/articles/docs-as-code-tested-example/`. Target `docs as code`, volume 320 and KD 30; use first person in the title only if Ninad runs or explicitly adopts and verifies the reported experiment.

**Hypothesis:** A static docs build can pass while a behavioral change invalidates the example. The distinct reader job is adding a meaningful failing check to a change workflow, beyond a definition of docs as code.

**Evidence and experiment:** Pin a small CLI fixture, document a command, then change its output or required argument. Run the site build and the example test separately, preserving both results.

**Artifact:** A commit pair showing the behavioral change and the check that catches it. Supply a docs-only failure case too, so the article distinguishes stale instructions from a software regression.

**Argument:** Show the passing build beside the failing instruction, then explain the claim each check is entitled to make. The counterexample is a change that does not affect the reader and should not trigger a rewrite.

**HN interest:** Engineers can reproduce the false confidence and suggest stronger checks. The useful question is which contracts deserve executable documentation, including the maintenance cost.

**Links and gate:** Link to code documentation and the review checklist. Recheck existing queue rows and current canonicals before creating the URL; if an owner already serves this job, refresh it instead.

## Tracing a change to the page that owes an update

**Working title:** Documentation maintenance starts with the changed behavior

**Placement and intent:** Conditional new `/articles/documentation-maintenance-tested-workflow/`. Target `documentation maintenance`, volume 90 and KD 3; include documentation debt as a section rather than a competing page.

**Hypothesis:** A change-to-page record can catch an outdated instruction that a calendar reminder misses. It can also create unnecessary review work if ownership rules are too broad.

**Evidence and experiment:** Use a declared sample of fixture commits with independently labeled affected pages. Run a simple ownership mapping, record missed pages and false alerts, and inspect the cases manually.

**Artifact:** The commit sample, labeling rules, ownership table, and results. A synthetic sample establishes how the method behaves on that sample; it does not establish an industry failure rate.

**Argument:** Begin with one changed behavior and the page it makes wrong. Show the smallest ownership rule that catches it, then the false alert that forces a narrower rule.

**HN interest:** The failure tradeoff makes this a maintenance problem engineers can reason about. An honest false alert is more informative than a dashboard screenshot alone.

**Links and gate:** Link to versioning and information organization. Hold separate workflow and ownership articles until a distinct reader task and enough evidence justify another URL.

## Measuring what a shorter page makes the reader recover

**Working title:** What disappeared when the documentation got shorter?

**Placement and intent:** Refresh `/articles/the-case-for-shorter-technical-documentation/`. Search demand for this exact question is unmeasured; this is an editorial test of the site's philosophy and an existing argument.

**Hypothesis:** Removing a prerequisite can reduce reading time while increasing the work needed to finish. The hypothesis concerns the removed dependency, not a universal preference for longer pages.

**Evidence and experiment:** Prepare two clearly labeled versions of one guide and record which information differs. With consenting readers, vary order or use separate readers to reduce learning effects; record task success and the information they seek elsewhere.

**Artifact:** Both guides and an anonymized task log. If recruitment is unavailable, publish a single reproducible walkthrough as a case analysis and omit user-performance claims.

**Argument:** Begin with the removed instruction and follow the reader's next step. Include a passage whose removal has no cost, so the argument does not become a defense of verbosity.

**HN interest:** A concrete counterexample can challenge word-count rules without contrarian theater. A small sample supports a local finding, with no population estimate.

**Links and gate:** Link to the assumptions essay and template. Do not infer faster completion from word count or manufacture timing data.

## Keeping a release note attached to a user's action

**Working title:** A release note that tells me whether to change my code

**Placement and intent:** Refresh `/articles/writing-release-notes-that-developers-trust/`. Target the task behind `release notes template`, volume 720 and KD 24, while checking the live SERP before any title change.

**Hypothesis:** A change description can be accurate without telling an existing user whether migration is required. A task-based review can expose that missing action.

**Evidence and experiment:** Use a fixture change with an explicit compatibility boundary. Write the note from the actual diff, ask a reviewer which client is affected, and retain the sentence that supports their choice.

**Artifact:** Before/after API behavior and the release note, with a runnable migration example. Explain why the chronological changelog remains a separate navigation task.

**Argument:** Show a client that continues to work and one that fails. Describe the note's required precision around those cases rather than prescribing a universal format.

**HN interest:** The difference between an accurate change log and actionable migration guidance is visible in the code. Readers can challenge the boundary without needing access to a customer incident.

**Links and gate:** Link to the changelog guide and API practices. If the compatibility boundary is not confirmed, record the open question instead of drafting reassuring copy.

## Asking AI to find the promise the test never made

**Working title:** This assertion passed. The paragraph still overclaimed.

**Placement and intent:** Refresh `/articles/writing-with-ai-before-you-know-what-you-think/` only when new evidence adds to its current argument. Target `ai technical writing`, volume 40 and KD 24, alongside `technical writing with ai`, volume 20 and KD 0.

**Hypothesis:** An AI reviewer may confuse the scope of a passing assertion with the scope of the article's claim. The current SQLite example is a useful starting case, not an evaluation result about models.

**Evidence and experiment:** Define a fixed set of claim/test pairs and human labels before collecting responses. Save model versions, complete prompts, sampling settings, and outputs; disclose run count and inspect disagreements.

**Artifact:** A compact evaluation table and raw responses with no sensitive inputs. Paid model calls require a separately authorized budget; an unfunded run remains a protocol, not a result.

**Argument:** Start with the narrow assertion and the extra guarantee in the paragraph. Explain the review instruction through the failures it catches and the failures it misses.

**HN interest:** Engineers can add adversarial examples or dispute the labels. A result where a model does well is still publishable and should change the recommendation.

**Links and gate:** Link to the assumptions essay and a tested tutorial. Do not make an AI-detector claim or conceal material AI involvement if asked about how the work was produced.

## Publishing the correction to the measurement

**Working title:** The documentation audit measured the extractor first

**Placement and intent:** Conditional research note, with canonical placement chosen after reviewing the existing census owner. Target the documentation-testing reader; `documentation testing` returned volume 20 and KD 0.

**Hypothesis:** A syntax census can mistake fragments or deliberate errors for broken examples. The existing code-sample census protocol already names these classification risks and records a documentation-root resolution rule that failed its coverage requirement.

**Evidence and experiment:** Read the frozen protocol and pilot records without changing them. Reproduce the recorded resolver result, audit sampled exclusions, and distinguish extraction errors from source errors before expanding the study.

**Artifact:** A correction note that links the original method to its replacement and shows how counts change. Preserve the preregistration and report deviations, including cases that remain unresolved.

**Argument:** Open with the specific measurement that changed and its cause. Attribute the work to the recorded study owner and artifacts; Ninad's first-person account requires his confirmation.

**HN interest:** Research about the limits of a documentation-quality metric gives readers a method to inspect. Publishing the correction can be valuable before a full census is ready.

**Links and gate:** Link to the review checklist and code documentation. Do not headline a percentage of broken documentation until human classification supports that exact estimand; do not treat syntax validity as successful execution.
