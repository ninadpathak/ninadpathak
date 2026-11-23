# Technical video script

Turn a topic into a researched script that helps a viewer understand a problem and act on the answer. Use the teaching approach distilled from the user's supplied developer-relations transcript: establish relevance, organize the question, explain through examples, distinguish concepts that get confused, and follow through to a practical result.

Before drafting, read [the speaking and thought-structure reference](video-speaking.md). It preserves the transcript's nuances and includes an original calibration passage. Learn the explanatory mechanics; write original phrasing rather than reproducing the speaker's verbal identity.

## Start from the topic

A topic alone is sufficient. Honor supplied audience, duration, stance, format, and source constraints. Otherwise assume a technically curious viewer who knows general software concepts but is new to this topic, and a single-presenter explainer of roughly 8–10 minutes. State these assumptions briefly in the delivery; do not turn intake into a questionnaire. Ask only when an ambiguous topic or missing context would materially change the answer.

Decide what question the viewer is trying to answer and what they should understand or be able to do afterward. Narrow an expansive topic around that question and state the chosen scope. Use an actual starting situation before abstract categories. A focused how-to can begin with the failed operation; it does not need a long industry introduction.

## Research the answer

Research the actual topic before writing. Use current official documentation, specifications, original papers, release notes, or maintained source repositories as appropriate. Open the relevant pages; search snippets alone are insufficient. Use credible practitioner accounts for experience and disagreement, distinguish those from technical evidence, and trace technical claims back to primary sources.

Build a compact working claim ledger: claim, source URL, relevant version/date, and confidence or unresolved limitation. Cover the definition and mechanism, the running example, decision boundaries, and likely objections. Verify unstable facts such as APIs, pricing, limits, availability, and compatibility at drafting time. Resolve contradictory sources by checking scope and version; if unresolved, explain the uncertainty or leave out the disputed claim. Stop expanding research when the chosen question is supported; a script is not an inventory of the field.

For a demonstration, use a minimal reproducible example and check its relevant behavior when tools and authorization permit. Record what was actually run. Otherwise label the demo as untested in production notes and do not invent outputs. Research access does not authorize deployments, purchases, account changes, or publishing.

If browsing is unavailable or the user forbids it, work from supplied material and clearly label research and verification limits. Do not claim a fresh fact check. Avoid unsupported time-sensitive advice; identify the specific facts needing verification.

## Build the spoken explanation

Write a provisional one-sentence answer, then arrange the questions that make that answer understandable. The order should follow the viewer's reasoning rather than the order in which sources discuss the topic.

- Establish why the topic arises in the viewer's work. Give a short direct definition when it helps orientation; postpone taxonomy until its purpose is clear.
- Offer a compact roadmap only when the length or complexity needs it. Keep the promised categories consistent with what follows. Choose the number of sections from the topic, not from the reference video's counts.
- Carry one concrete example across the explanation. Develop a point through a claim, plain explanation, example, and consequence where useful; vary the shape so it sounds like teaching rather than a repeated template.
- Answer the plausible objection at the moment it arises. Specify when a claim holds and distinguish neighboring concepts before a viewer makes a costly inference.
- Spend additional time on consequential failure modes or neglected work. Weight sections by the viewer's risk of misunderstanding, not equal word counts.
- Use a brief recap at a genuine conceptual boundary to support the next step. End by resolving the opening question and offering a concrete next action or decision check. Add a subscription or promotional call to action only if requested.

Write connected spoken explanations. Let a customer situation develop through several sentences, including why it happens and what it changes, before moving on. Vary sentence and paragraph lengths; short emphasis lines need surrounding explanation. Use contractions and conversational connectors where the thought continues. Introduce a technical term after the example gives it meaning. Keep personality through direct judgments and concrete consequences. Avoid a succession of tiny paragraphs, rhetorical question volleys, repeated “I’d” recommendations, or identical lesson-and-transition endings for each section. Adding filler words does not fix that rhythm. Do not fabricate personal experience, benchmark results, company stories, or quotes. Frame invented situations explicitly as examples.

The plain-language and evidence rules in [core.md](../core.md) still apply. This requested spoken format calls for useful signposts and selective recaps. Do not force article headings, a runnable artifact in each conceptual section, or article introduction lengths onto a video.

## Deliver and check

Deliver a title, a short audience/scope note, and the complete script. Mark non-spoken section labels or sparse visual/demo cues clearly. Use normal prose for spoken lines; keep citations, URLs, research notes, and code listings outside those lines unless the presenter actually needs to say them. Put exact demo commands in a separate production block linked by cue.

After the script, include:

- An estimated duration based on the spoken word count, using approximately 130–150 words per minute unless the user provides their pace. Exclude headings, cues, code, and sources from the count. Account separately for demo or pause time; state that runtime is an estimate.
- A concise source map linking substantive claims or sections to the supporting pages, with version/date context where it affects the answer. Separate sourced facts from recommendations or inferences.
- Production or verification notes only where needed, including untested demos or a material unresolved claim.

Before delivery, perform a speakability pass over whole sections: mentally read them aloud and listen for repeated sentence shapes or paragraph endings. Compare the delivery with the source analysis, not just its outline. The viewer should hear a person developing an explanation, with space for examples, rather than a succession of polished advice cards. Then check the roadmap against the finished sections, examples against the evidence, and the ending against the opening question. A polished script must both explain the mechanism and equip the viewer to use the answer; an engaging list of benefits does not meet the task.
