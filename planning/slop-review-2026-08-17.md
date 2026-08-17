# Slop review: five pieces published through 2026-08-17

## Result

**PASS: 0. REJECT: 5.**

Every piece fails the evidence test and the cross-article structure test. The artifacts do not introduce independent information. Each script checks fields or headings chosen by the same run, against a fixture or outline written to contain them.

The review uses Charter sections 2c, 2d, and 2e. The Humanizer checklist was used to detect clusters of AI patterns, not to reject isolated words or clean technical prose.

## Generator defects

The findings below refer to these generator defects:

- **G1: Unconditional artifact.** The instruction to “build, run, or audit a real evidence artifact” on every run creates a toy checker even when the subject needs research or judgment instead.
- **G2: Mandatory first person.** The instruction requiring first person on every run turns pipeline activity into claims made in Ninad's voice.
- **G3: Mandatory evidence ceremony.** Required commands, exact output, and terminal captures force exact PASS strings and pixel-specified screenshot markup into the article whether they help the reader or not.
- **G4: Fixed cold-run structure.** Each run receives the same detailed sequence and no rolling structure log. The result converges on problem → “I built” → framework table → objection → fixture test → PASS screenshot → two-link conclusion.
- **G5: Objection slot.** The instruction to state a “competent objection” has become a stock paragraph rather than a response to a decision that genuinely needs one.
- **G6: Link quota without retrofit.** The internal-link requirement is being implemented as outbound links near the ending. The generator does not update an existing published page to provide the required inbound link.

## Cross-article finding

**Blocking: structural sameness across all five. Generator cause: G4, reinforced by G1, G2, and G3.**

All five use the same evidence sequence:

1. Open with a generic failure mode.
2. Claim “I built” a checker, selector, outline, or audit.
3. Present a table that defines the desired answer.
4. Run a script against an authored fixture that already contains that answer.
5. Print PASS and show a terminal screenshot with the same `2560 / 1664` inline dimensions.
6. Add a final section containing internal links and an imperative summary.

Four of five also contain “The strongest objection” or “The competent objection.” That is a prompt slot showing through the prose, not four independently discovered objections.

## api-documentation-template-the-pages-every-api-needs.md

**Verdict: REJECT.**

- **Line 15, falsifiable first person and preamble:** “I built this API documentation page outline to start somewhere more useful.” The reader came for the template, but the first paragraph spends authority on an authored artifact before providing it. The file's existence does not establish that Ninad designed or used it in real client work. **Generator cause: G1 + G2.**
- **Line 17, corporate abstraction:** “The template has seven page jobs, not seven arbitrary menu labels.” “Page jobs” is internal content-strategy jargon, and the seven-part contrast repeats the artifact's chosen structure as if the checker discovered it. **Generator cause: G1 plus the prompt's demand for a proprietary-sounding framework.**
- **Lines 65–71, zero-information evidence:** “I ran the included checker against the downloadable outline” and “The command returned `PASS: homepage, quickstart, authentication, reference, recovery, events, and changes are owned`.” The checker contains the seven required headings verbatim and passes the outline that the same run wrote with those headings. It tests no external API, real docs set, or reader behavior. **Generator cause: G1 + G2 + G3.**
- **Lines 67–76, uncalled-for specificity:** The exact Python command, exact PASS sentence, `2560 / 1664` aspect ratio, terminal background value, and pixel screenshot add no information to the reader's task of choosing documentation pages. **Generator cause: G3.**
- **Lines 63–83, repeated skeleton:** A validation heading, first-person run receipt, command, PASS output, screenshot, caption, then a final link section matches every other piece in this batch. **Generator cause: G4.**
- **Line 83, linking gate incomplete:** Both outbound article URLs were present in the fresh sitemap and are relevant, but no other published article links to this article. The required inbound retrofit is missing. **Generator cause: G6.**

## api-documentation-tools-hands-on-comparison-small-teams.md

**Verdict: REJECT.**

- **Line 2, unsupported framing:** “A Hands-On Comparison” promises direct use of the tools. The article cites product documentation and runs a home-grown selector; it does not show Swagger UI, Redoc CE, Bump.sh, or Mintlify being installed, configured, or used on the same API. **Generator cause: the research/comparison brief allowed a toy artifact to substitute for hands-on product testing, amplified by G1.**
- **Lines 15–21, padding before the answer:** “I built a small tool selector” and two paragraphs of “workflow boundary” language delay the useful comparison table until line 23. **Generator cause: G1 + G2 + fixed evidence-led opening in G4.**
- **Line 17, corporate register:** “Pick the tool that keeps those states close enough to inspect” is not how an engineer describes contract, guide, and release drift. It hides the concrete review problem behind “states” and “inspect.” **Generator cause: the prompt asks for authoritative synthesis before it has earned a concrete finding.**
- **Line 32, corporate register:** “API-definition release review versus maintaining a wider developer learning path” turns a simple distinction into planning language no working engineer needs. **Generator cause: the comparison template rewards abstract category labels over observed product behavior.**
- **Line 44, prompt-shaped objection:** “The strongest objection is that…” appears in the same position and register as objection paragraphs elsewhere in the batch. **Generator cause: G5.**
- **Lines 54–68, zero-information evidence:** The fixture says `source_of_truth` is `openapi-and-repository`; the script hard-codes that value to `Swagger UI or Redocly`. The returned answer is the lookup table the run wrote, not a comparison result. **Generator cause: G1 + G2 + G3.**
- **Lines 58–73, uncalled-for specificity:** Three setup commands, a renamed fixture, an exact selector invocation, and the same pixel-specified terminal screenshot do not help a team evaluate the four products. **Generator cause: G3.**
- **Lines 52–84, repeated skeleton:** Test heading, “I ran,” fixture result, limitations, screenshot, two links, and a short punchline repeat the batch template. Lines 82–84 also manufacture a two-sentence closer by splitting one thought. **Generator cause: G4 and Humanizer pattern 31, manufactured staccato.**
- **Line 80, linking gate incomplete:** Both outbound article URLs resolve and fit the topic, but no other published article links to this tools comparison. **Generator cause: G6.**

## api-documentation-examples-what-the-best-developer-portals-get-right.md

**Verdict: REJECT.**

- **Line 2, evidence does not support the title:** “What the Best Developer Portals Get Right” implies a comparative evaluation. The body briefly cites four portals but never defines “best,” applies one scoring method to them, or reports a complete observed path for any one portal. **Generator cause: the search-title instruction overpromises while G1 supplies a substitute artifact instead of comparative evidence.**
- **Lines 15–17, repeated opening and corporate register:** “I built a small portal-path checker to keep the comparison honest” is falsifiable provenance, and “earns its example status” sounds like a scoring framework that the article never actually applies to the named portals. **Generator cause: G1 + G2 + G4.**
- **Lines 23 and 38–50, shallow named examples:** Notion, GitHub, Stripe, and Cloudflare are each used to support one favorable sentence. The article does not trace the promised credential-to-request-to-recovery path through any of them. Naming several portals creates the appearance of comparison without doing the comparison. **Generator cause: the research prompt rewards source coverage and named examples instead of one complete observed example.**
- **Line 42, prompt-shaped objection:** “The competent objection is that…” is the same generator slot seen across the batch. **Generator cause: G5.**
- **Lines 54–60, zero-information evidence:** The checker asks whether a JSON object contains the fields `credentials`, `request`, `expected_response`, and related keys. The authored fixture contains those keys. It tests a fictional portal path, not any portal named in the article. **Generator cause: G1 + G2 + G3.**
- **Lines 56–65, uncalled-for specificity:** The exact command, exact PASS string, and `2560 / 1664` terminal screenshot carry no evidence about Notion, GitHub, Stripe, or Cloudflare. **Generator cause: G3.**
- **Lines 52–76, repeated skeleton:** Test heading, run claim, PASS, screenshot, caption, two links, and imperative conclusion mirror the other pieces. **Generator cause: G4.**
- **Line 74, internal links:** Both outbound URLs resolve in the fresh sitemap and are relevant. Existing published articles link back to this article, so the bidirectional link gate passes.

## api-documentation-best-practices-reference-guides-and-working-requests.md

**Verdict: REJECT.**

- **Lines 15–17, falsifiable first person and abstract preamble:** “I built a small package checker for this article” is pipeline provenance presented as Ninad's experience. “That path is the unit to design and test” is corporate architecture language where the concrete answer could start immediately with the quickstart, reference, and recovery split. **Generator cause: G1 + G2 + G4.**
- **Line 36, unearned generalization:** “A list endpoint is often a useful first move” assumes list operations are harmless and available. The following invented endpoint makes that generalization look tested when it is only an example. **Generator cause: the prompt requires a runnable-looking technical example even though the article has no real API under test.**
- **Lines 38–44, uncalled-for specificity:** The exact `api.example.com/v1/projects` command and invented `projects` and `limit` fields add a fake implementation surface to an editorial principle. No real API behavior supports them, and the reader does not need those names to understand that a quickstart needs a complete request and expected result. **Generator cause: mandatory command/example evidence under G3.**
- **Line 54, prompt-shaped objection:** “The strongest objection is that…” repeats the objection slot used by the tools article. **Generator cause: G5.**
- **Lines 60–66, zero-information evidence:** The checker requires named fields under `quickstart`, `reference`, and `errors`, then reports a complete path when an authored fixture contains them. No fixture is shipped in `static/`, making the reported run less reproducible as well as circular. **Generator cause: G1 + G2 + G3.**
- **Lines 62–71, uncalled-for specificity:** The exact command, exact PASS output, and standard `2560 / 1664` screenshot block do not test a live request or improve the best-practices argument. **Generator cause: G3.**
- **Lines 58–84, repeated skeleton:** Test heading, first-person receipt, PASS, screenshot, linking section, and final imperative are the batch template again. **Generator cause: G4.**
- **Lines 80–82, internal links:** All three outbound URLs resolve and fit the reader's next decisions. Existing published articles link back to this piece, so the bidirectional link gate passes.

## how-to-document-multiple-product-versions.md

**Verdict: REJECT.**

- **Line 15, falsifiable first person before the answer:** “I built a version-route audit download” is pipeline activity attributed to Ninad and delays the useful policy until line 17. **Generator cause: G1 + G2 + G4.**
- **Line 40, list-shaped corporate instruction:** “State the version, support state, relevant release date, and the route to migration guidance” compresses four policy fields into a sentence because the generator is filling a completeness checklist. **Generator cause: the framework prompt rewards exhaustive field enumeration instead of one example followed by the governing rule.**
- **Lines 58–64, zero-information evidence:** The script defines the accepted canonical and redirect policy. The same run wrote a failing fixture that violates those rules and a passing fixture that follows them. Repairing the fixture proves only that the fixture was changed to match the script. **Generator cause: G1 + G2 + G3.**
- **Lines 60–69, uncalled-for specificity:** The exact filename, expected PASS line, route count in the alt text, and `2560 / 1664` screenshot dimensions do not help a reader decide how to treat a real retired version. **Generator cause: G3.**
- **Line 72, fake-evidence register:** “The receipt confirms” overstates a self-authored fixture check as evidence. **Generator cause: G1 plus the prompt's requirement to present an evidence receipt.**
- **Line 78, unearned version label:** “`v2 supported documentation`” is an invented label that does not need a version number to make the point. **Generator cause: required specificity leaking into a general example.**
- **Line 86, prompt-shaped objection:** “The competent objection is that…” repeats the same generator slot. **Generator cause: G5.**
- **Lines 56–88, repeated skeleton:** Test heading, first-person fixture run, PASS result, terminal image, link section, objection, and final imperative follow the same sequence as the API pieces. **Generator cause: G4.**
- **Lines 78–80, internal links:** Both outbound URLs resolve and fit the topic. The API best-practices article links back to this page, so the bidirectional link gate passes.

## Recurrence ranking

1. **Unconditional artifact plus mandatory first person: 5/5 pieces.** Every article manufactures a checker or selector and attributes building or running it to Ninad.
2. **Fixed cold-run structure with evidence ceremony: 5/5 pieces.** Every article contains the same fixture-test section and terminal screenshot; four use the same objection formula.
3. **Uncalled-for exact commands, PASS output, and pixel screenshot details: 5/5 pieces.** The specificity appears in every artifact section and never adds independent evidence.

The generator should be changed before another article runs. Making artifacts conditional, making first person depend on the queue's Experience value, deleting the required terminal-receipt sequence, and adding a rolling structure log would remove the three most common causes.
