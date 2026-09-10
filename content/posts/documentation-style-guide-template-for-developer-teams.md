---
category: technical-documentation
date: 2026-08-07
description: Download a documentation style guide template that records product terms, code evidence, UI sources, owners, and review triggers.
slug: documentation-style-guide-template
status: published
tags:
- documentation
- technical-writing
- developer-experience
takeaways:
- A useful style guide records product decisions instead of collecting tone preferences.
- Code and UI rules need evidence a reviewer can inspect.
- Each product rule needs an owner and a change that triggers review.
title: A Documentation Style Guide Should Record Decisions, Not Taste
updated: 2026-09-11
---

A fictional feature rename can leave **Create environment** in the UI, workspace in the API, and the old project name in the guides. The names illustrate the failure and do not describe a client or public product.

A writer can follow the voice rules perfectly and still send the reader hunting through an interface that no longer exists.

I dislike style guides that spend six pages on tone before they name the product. The dangerous disagreements are not warm versus formal.

They are which term is real, which command was tested, which UI label shipped, and who has to change the page when the product moves.

The downloadable template records those decisions.

## Download the decision record

<p><a class="btn btn-primary" href="/static/templates/developer-documentation-style-guide-template.md">Download the documentation style guide template</a></p>

Put the file beside the product source or in the repository that owns the docs. Start with one guide that changes with the product.

If the template cannot settle a real review comment on that page, cut the rule or make its evidence sharper before rolling it across the site.

Use the file on one page first. A reviewer should be able to answer these questions without asking who remembers the decision:

- Which name should appear in the UI, API, and prose?
- Which environment produced the command and output?
- Which released screen proves the navigation path?
- Which product change forces this rule back into review?

If the answer is "check the style guide" and the style guide points nowhere else, the file has become a polite dead end.

## Make terminology answer to the product

[Google's word list](https://developers.google.com/style/word-list) records preferred wording and usage decisions for Google's documentation. A product team needs a narrower local layer for names that exist in its permissions, API, migration flow, and interface.

Record the approved term, the definition that separates it from nearby terms, the product source, and the owner.

The next table is illustrative. Its feature names and evidence sources do not describe a live product.

| Product state | Style-guide decision | Evidence | Failure branch |
| --- | --- | --- | --- |
| A role controls access | Use the released role name | Permission schema or UI | Stop review if prose invents a friendlier name |
| A feature was renamed | Keep the old name only where readers still see it | Migration guide or compatibility field | Remove the alias if no released surface contains it |
| UI and API names differ | Name both and state the boundary | Released UI plus API schema | Escalate to the product owner if the boundary is unclear |

The default style-guide move is to decree one preferred word. That works for prose synonyms but lies when two released surfaces genuinely use different names.

Expose the mismatch rather than edit one side out of reality.

The following fictional deployment row shows the fields. Replace its terms, schema path, owner, and trigger with verified product facts:

```text
Concept: deployment environment
Approved UI term: Environment
API object: workspace
Avoid in prose: project
Definition: An isolated target that owns variables and deployments.
Evidence: settings screen + /v1/workspaces schema
Owner: Deployments team
Review trigger: UI label or API schema change
```

Verify the row against the released UI and schema. If "Environment" exists only in marketing copy, or the definition hides the API term a developer must send, reject the row.

When released surfaces use different names, record which surface owns each one and link the terms until the product resolves the mismatch.

## Give each page shape a completion signal

A tone rule cannot tell a tutorial when to stop. A page contract can.

| Page job | Required shape | Completion signal |
| --- | --- | --- |
| Tutorial | Starting state, ordered build, tested result | A working command, response, or screen state |
| How-to guide | Known starting state, bounded change | The changed behavior is visible |
| Reference | Exact name, type, default, and constraint | The reader can resolve the named question |
| Troubleshooting | Symptom, diagnostic, cause, and recovery | The failure is resolved or safely escalated |

The [Diataxis framework](https://diataxis.fr/start-here/) distinguishes tutorials, how-to guides, reference, and explanation by the reader's mode and need. My addition is the completion signal.

Without it, a page can match the right category and still wander until the author gets tired.

Use the [technical documentation template](/articles/technical-documentation-template/) to turn those jobs into pages. Use the [documentation organization guide](/articles/how-to-organize-a-documentation-site/) when two pages claim the same question.

### Reject a page rule that cannot be checked

"Be concise" gives a reviewer taste disguised as a standard. "Put prerequisites before the first command that needs them" gives the reviewer a page state to inspect.

Two reviewers should reach the same answer from the page. If approval depends on who argues harder in the comments, the rule needs observable criteria.

### Split pages when completion signals compete

A tutorial and a reference page can share a subject while ending at different proof. Keep the learning build in the tutorial and the stable field contract in reference.

Give each page one completion signal and link to the other at the decision boundary. If both pages repeat the same setup steps, choose one owner for that procedure.

## Put evidence beside code rules

A rule saying "use fenced code blocks" governs presentation. It says nothing about whether the command works.

Readers need the runtime, package version, starting state, command, expected result, and failure boundary. The command shell below is a placeholder, not a tested project command:

```bash
# Run from: [working directory]
# Requires: [access, environment variables, or local service]
[copyable command]
```

[Google's command-line syntax guidance](https://developers.google.com/style/code-syntax) recommends introducing commands by their task and separating options when they represent different procedures. The local product rule must go further: record the environment that produced the example and the signal that proves it worked.

### Review a command as a claim

The following command record is illustrative. `npm run verify:checkout`, its output, runtime, and credential state are placeholders to replace with a tested command:

| Field | Value |
| --- | --- |
| Runtime | Node.js 24 from `.node-version` |
| Working directory | Repository root |
| Starting state | Test credentials exported |
| Command | `npm run verify:checkout` |
| Expected result | Exit `0` and `checkout fixture: PASS` |
| Failure boundary | Does not test production credentials |

Run the real command in a clean environment. If it needs a global package or an unstated secret, repair the instructions instead of adding another adjective to the rule.

### Reject hidden starting state

Run the command outside the author's working environment. A clean container or temporary project can expose dependencies that a warm machine quietly supplies.

If success depends on a cached credential, unlisted file, or globally installed package, add that starting state or remove the example.

## Tie UI language to a released screen

UI instructions rot with the interface. The prose can remain crisp while the control moves behind a permission or changes its label.

[Google's UI guidance](https://developers.google.com/style/ui-elements) shows how to name menu paths and visible controls. The style guide still needs a product-specific source because Google's convention cannot tell you whether **Create environment** became **New environment** in your release.

| UI claim | Verification source | Review trigger |
| --- | --- | --- |
| Visible label | Released screen or accepted UI source | Label change |
| Navigation path | Current role and screen sequence | Information-architecture or permission change |
| Availability | Release record or feature status | Plan, region, or rollout change |

Have the named role follow the path in the released interface. A screenshot from a design file cannot support a claim about shipped behavior.

## Give rules owners and expiry conditions

A style guide becomes bureaucracy when it keeps preferences that prevent no reader error and answer to no product change. More rules make that document heavier, not safer.

GitLab's maintained [documentation style guide](https://docs.gitlab.com/development/documentation/styleguide/) and the [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/welcome/) are broad editorial references. They cannot own your product terms, commands, or release states.

Your local file should record only the decisions those external guides cannot make for you.

Keep a product rule when it prevents one of these failures:

- The reader chooses the wrong role or resource.
- A copied command depends on a hidden starting state.
- A UI path points to an unreleased or renamed control.
- Two pages give competing answers to the same task.
- A product change has no documentation review trigger.

For each surviving rule, name an owner and an event that reopens it. Replace "docs" and "review later" with the team that controls the fact and the product change that can falsify it.

## Documentation style guide checklist

- Product terms point to a released UI, schema, or compatibility source.
- Page forms have observable completion signals.
- Commands name their environment and failure boundary.
- Product rules name fact owners and review triggers.

Run the [documentation review checklist](/articles/documentation-review-checklist-before-you-publish/) after the decisions are filled. The style guide defines the claims a page should make, while review proves whether this page makes them truthfully.
