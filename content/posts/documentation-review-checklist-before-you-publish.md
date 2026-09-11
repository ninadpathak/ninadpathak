---
category: technical-documentation
date: 2026-07-30
description: 'Review documentation in four passes: product truth, reader route, rendered behavior, and release state, before polishing prose.'
slug: documentation-review-checklist-before-you-publish
status: published
work_note: "[Ninad Pathak](/contact/) reviews technical documentation against the product version it describes, checking the instructions and missing steps before editing the wording that carries them."
tags:
- technical-writing
- documentation-workflow
- docs-as-code
takeaways:
- Verify product behavior before editing sentences.
- Run the reader's success and failure paths from the documented starting state.
- Inspect the exact rendered output at desktop and mobile widths.
- Split approval by evidence instead of asking one reviewer to bless the page.
title: Documentation Review Should Start With the Product, Not the Prose
updated: 2026-09-11
---

Picture a documentation pull request where the comments are breeding around commas, heading length, and screenshot placement. The command remains untested in the rendered page.

So does the permission in the released product.

Then a beautifully edited page ships with a broken path.

Documentation review should begin with product truth, move through the reader's route, inspect the rendered artifact, and end at release state. Prose comes after the behavior survives.

My objection to the usual copyedit-first review is not that wording is unimportant. Perfect wording can make a false instruction look trustworthy enough to hurt someone.

## Put the product on trial first

A technical page makes claims about names, defaults, permissions, versions, side effects, errors, and recovery. Extract those claims before touching the sentences that carry them.

The reviewer needs a source outside the draft for each claim that can break the task. Otherwise the review is one sentence asking another sentence whether it is true.

### Build a claim ledger

Use a table that forces each material claim to point somewhere. The following API, role, response, and interface claims are fictional examples, not facts about a public product:

| Page claim | Verification source | Reviewer | Result |
| --- | --- | --- | --- |
| Workspace owners can create API keys | Released permission model | Product owner | Pending |
| The API accepts `Authorization: Bearer` | Current API schema plus request | Engineer | Pending |
| Invalid keys return `401 invalid_api_key` | Reproduced response | Engineer | Pending |
| The key is displayed once | Released UI | Product owner | Pending |

Reject a ledger row when its source is the draft itself, a remembered demo, or another page copying the same unsupported sentence.

When using AI before asking an expert, proposed explanations belong in the question pile, not the verified column. Plausible wording has no special claim on truth.

### Run the documented behavior

Start in the environment the page promises. Follow the released UI path or run the API, CLI, and code samples with the documented inputs.

Record enough state for a second reviewer to reproduce the check:

```text
Product version: [released version or commit]
Account role: [role used]
Runtime: [name and version]
Starting state: [required resource or clean project]
Command: [exact command copied from the render]
Expected signal: [status, output, or screen state]
Observed signal: [actual result]
```

Move an unstated credential, global package, private feature flag, or unreachable product state into the prerequisites before rerunning the page.

### Attack the failure path

Trigger the error the page claims to solve. Confirm the message, status or exit code, diagnostic, and recovery step.

Use a four-part recovery record:

| Field | Required evidence |
| --- | --- |
| Symptom | Exact error or visible behavior |
| Diagnostic | Command or observation that separates likely causes |
| Recovery | Smallest supported action that restores progress |
| Proof | Signal that the recovery worked |

Replace "Try again" with a diagnostic. Keep "Restart the service" only when the page names the state the restart clears and the signal that proves recovery.

## Make the page earn its URL

A technically correct draft can still be the wrong page. It may duplicate an existing answer, combine incompatible readers, or switch between tutorial and reference until neither job survives.

The URL earns more authority only after the page owns one necessary question.

### Name one reader decision

Write one sentence before review begins:

```text
This page helps [reader with starting state] decide or do [specific outcome].
```

If one reviewer writes "create a key" and another writes "understand authentication," the page has two jobs fighting inside it. Split the jobs or choose one before editing the draft.

The [technical tutorial guide](/articles/how-to-write-a-technical-tutorial-that-actually-teaches/) shows how a learning path differs from a task page. The distinction matters because a tutorial can teach through a controlled build while reference must state behavior without dragging the reader through a lesson.

### Search for the answer that already exists

Search titles, body copy, error strings, and product terms before granting the draft a new canonical URL.

The command below is an illustrative repository search. Replace its terms and `content/` path with the project under review:

```bash
rg -n -i 'create.*api key|invalid_api_key|authorization: bearer' content/
```

If two pages satisfy the same intent, consolidate the useful material and prepare a direct redirect.

Do not publish a second answer because the first file is annoying to edit.

### Expose hidden starting state

Reviewers should mark each noun the author already possessed: account role, runtime, package, region, sample data, credential, feature state, and existing resource.

Move a prerequisite before the first step that needs it. Do not make the reader discover an access request after the command that requires access.

## Review the route as a sequence of decisions

Once the behavior is true and the page deserves its URL, follow it as a reader. The question is not whether the prose sounds smooth.

Each section must give the reader enough state to choose the next action.

Read the route in order, then scan it out of order as someone returning with a failed command would.

### Read the headings without the paragraphs

Extract the outline. The path below is an illustrative Markdown file, not a live page in this repository:

```bash
rg '^#{2,3} ' content/posts/example.md
```

[Google's heading guidance](https://developers.google.com/style/headings) recommends a logical hierarchy, descriptive headings, and content between a parent heading and its subsections. The outline should expose the route rather than repeat labels such as Overview, Setup, Configuration, Usage, and Conclusion.

Rewrite headings that could move to another article without changing meaning. The outline should expose both progression and recovery.

### Demand proof after a consequential step

Each procedure stage needs an observable success condition before the reader spends more state on the next one. The next API-key action, role, and interface label are fictional:

```text
Action: Create a test API key.
Proof: The key list shows the new key name and test scope.
Failure: If the Create key control is absent, confirm the workspace-owner role.
```

A final screenshot does not prove the middle steps. If step three can silently fail, step three needs its own check.

### Separate advice from decision criteria

"Keep paragraphs short" is advice. "Split the paragraph when setup, consequence, and exception compete inside it" gives a reviewer something to inspect.

Lists should enumerate, and tables should compare repeated fields. Prose should carry judgment.

A page made entirely of cards and checklists can look organized while refusing to explain why one choice beats another.

## Inspect the page the reader receives

Markdown is source code for a page. It is not the page.

The rendered output can clip a table, swallow a character from copied code, hide a heading under a fixed header, or let a banner cover the only button that matters.

### Build the exact artifact

Use the same build path production uses:

```bash
python3 build.py
python3 seo_audit.py
python3 -m http.server 8765 --directory output
```

Build from the intended tree and stop on a missing page or canonical. Stop the server after review.

If the preview uses an older build directory, the screenshots prove nothing about the change.

GitLab's [documentation review apps](https://docs.gitlab.com/development/documentation/review_apps/) build and deploy a documentation preview from a merge request. GitLab's broader [documentation workflow](https://docs.gitlab.com/development/documentation/workflow/) also splits technical, writing, and maintainer review.

The product-specific process is larger than a small static site needs, but the principle is sound: review the artifact attached to the change.

### Check desktop and narrow widths

Inspect the title, local navigation, tables, code blocks, images, related links, and calls to action at both widths. Copy a command from the rendered page and run a syntax-safe check when the command is destructive or credentialed.

Fix clipping, overlap, unreadable code, hidden focus, or a control that moves outside the viewport. "It wraps" is not a defect by itself.

The question is whether the wrap destroys hierarchy or meaning.

### Check semantics instead of trusting a score

[W3C's page-structure tutorial](https://www.w3.org/WAI/tutorials/page-structure/) covers page regions, labels, headings, and content structure. Inspect the actual semantics: one descriptive H1, ordered heading levels, labeled navigation regions, keyboard access, visible focus, table headers, and meaningful image alternatives.

Automation can flag a missing `alt` attribute. It cannot decide whether the alt text carries the image's information or merely repeats the caption.

### Open links in context

Check internal paths, fragments, external sources, canonicals, and redirects from the rendered page.

The `output/articles/example/` path below is illustrative. Use the page generated by the current change:

```bash
python3 seo_audit.py
rg -n 'href="[^"]+#' output/articles/example/index.html
```

Repair a fragment that misses its heading, a redirect that hides a stale internal link, or a canonical that points at a competing page. A `200` response alone does not prove the reader reached the intended answer.

## Match the page to the release

Documentation can be accurate in a preview and wrong in production because the feature has not shipped, the permission differs by plan, or an older supported version behaves differently.

The release pass binds the reviewed behavior to the version and audience that will receive the page.

### Record availability and timing

Add the release facts the page depends on:

| Release question | Evidence |
| --- | --- |
| Which version contains the behavior? | Release or commit record |
| Is a flag required? | Current feature status |
| Which roles, plans, or regions can use it? | Released availability source |
| Does an older supported version differ? | Versioned reference or compatibility test |
| When should the page become indexable? | Release plan |

Do not present preview behavior as the current answer. For a breaking change, make the compatibility statement agree with the [changelog](/articles/how-to-write-a-changelog-developers-actually-read/) and [release notes](/articles/writing-release-notes-that-developers-trust/).

### Name the next review trigger

"Review annually" lets eleven months of product changes walk past the page. Tie review to the events that can falsify it: a renamed control, dependency release, permission change, response-schema change, or supported-version change.

Name an owner who can recognize the trigger in their normal workflow. Replace "the docs team" when another team controls the fact.

## Split approval by evidence

One reviewer should not impersonate an engineer, editor, accessibility specialist, and release owner in a single approval. A small team may combine people, but it should not combine the questions into one vague "LGTM."

| Reviewer | Evidence owned |
| --- | --- |
| Engineer or subject-matter expert | Product behavior, code, versions, risk, and recovery |
| Technical writer or editor | Reader fit, structure, terminology, and links |
| Accessibility reviewer or trained contributor | Semantics, keyboard behavior, visuals, and alternatives |
| Product or release owner | Scope, availability, timing, and migration state |
| Maintainer | Build, metadata, navigation, redirects, and deployment readiness |

Each reviewer should point to the evidence they checked. Do not treat one approval as proof of facts outside that reviewer's access.

## Run the passes on a fictional authentication guide

Orbit is a fictional API used to expose the review method. It is not client work, a product test, or evidence about a live service.

The draft says:

> Generate an API key in Settings, add it to your request, and run the example. The API returns your account.

The sentence is grammatical and nearly useless. It hides the role, navigation path, header format, environment, expected response, error behavior, and cleanup.

### Verify the fictional product contract

Assume the fixture defines this behavior:

```text
Role: workspace owner
Path: Developer settings > API keys
Header: Authorization: Bearer $ORBIT_API_KEY
Success: 200 with mode set to test
Invalid key: 401 invalid_api_key
Missing scope: 403 insufficient_scope
Cleanup: revoke the test key
```

Because these values belong to the fictional fixture, the article makes no claim that a public product behaves this way.

### Run the reader request

The following command targets the fictional `api.orbit.example` host with a placeholder test key. It is not a live endpoint or credential:

```bash
export ORBIT_API_KEY="replace-with-a-fictional-test-key"

curl --fail-with-body \
  --request GET \
  --url "https://api.orbit.example/v1/account" \
  --header "Authorization: Bearer $ORBIT_API_KEY"
```

The fictional response expected by this fixture is:

```json
{
  "id": "acct_example",
  "name": "Docs sandbox",
  "mode": "test"
}
```

The fictional pass condition is `mode: test`. A JSON object without that field does not prove the request reached the intended environment.

### Turn the outline into a route

Replace Setup, Usage, Errors, and Security with headings that expose decisions:

- Create a test API key
- Send an authenticated request
- Fix an invalid or under-scoped key
- Store the key outside source control
- Revoke the test key

Move cleanup before the page sends the reader elsewhere, and keep error recovery beside the request that produces the error.

## Automate mechanics without pretending to automate judgment

Machines are good at answers that should not depend on taste:

- Markdown and frontmatter syntax
- Internal link and fragment resolution
- Duplicate slugs and heading IDs
- Missing image alternatives
- Heading-level jumps
- Build success
- Canonical, sitemap, and robots rules
- Redirect loops and chains

External link checks need retries and bounded exceptions because a site can reject an automated client while remaining available to readers.

A mechanical gate should report the file, rule, and local reproduction command. It should not declare a page "high quality" because it counted headings or found an aggressive adjective.

Product truth and reader judgment remain human approval.

## Documentation review checklist

- Block publication when a behavior, permission, or recovery claim lacks an inspectable source.
- Run commands from the documented starting state and record both success and failure signals.
- Give one reader decision the title, route, and canonical URL.
- Inspect the exact intended tree at desktop and mobile widths.
- Match availability and version boundaries to the release.
- Split approval by the evidence each reviewer can inspect.

## Documentation review FAQ

**Should documentation block a product release?**

It should block when a missing or false instruction prevents safe adoption, operation, migration, or recovery. A tracked wording improvement can follow when the published route remains truthful and usable.

**Can automated checks replace review?**

No. Automation can verify deterministic structure and build behavior.

It cannot prove that the released product matches the claim or that the page changes the reader's next decision.
