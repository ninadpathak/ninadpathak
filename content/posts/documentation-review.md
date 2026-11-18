---
category: technical-documentation
primary_query: documentation review checklist
siblings:
- writing-technical-tutorials
- documentation-headings
- writing-changelogs
date: 2026-07-30
description: A documentation review checklist in four passes. Check the product's behavior
  first, then the reader's route, the rendered page and the release state, and edit the
  prose last.
slug: documentation-review
status: published
work_note: "I run the product before I write a page, which is the review this post describes, done ahead of time. So your reviewers get commands that already worked. I'm Ninad Pathak, a freelance technical writer, and [we can work together](/services/)."
takeaways:
- Check that the product does what the page says before you edit a sentence.
- Run the page's success path and its error path from the starting state it documents.
- Review the rendered page at desktop and phone widths, not the Markdown.
- Have each reviewer approve only the facts they can check.
title: A Documentation Review Checklist That Starts With the Product
updated: 2026-09-11
video: documentation-review
---

Poul-Henning Kamp gave programmers the word bikeshedding in [a 1999 email](https://phk.freebsd.dk/sagas/bikeshed/) to the FreeBSD project, borrowing [Parkinson's story](https://en.wikipedia.org/wiki/Law_of_triviality) of a committee that waves through a nuclear plant and argues about the staff bicycle shed. A docs pull request with twelve comments about commas and none about whether the command works is the same committee.

A documentation review checklist should run its checks in order of the harm a miss does, so a command that fails comes before a comma. I'd review in four passes: the product's behavior first, then the reader's route through the page, then the rendered page, then the release state, with the prose edited after all four.

Wording still matters to me. But a well-edited sentence makes a false instruction look trustworthy, so in a review of [technical documentation](/articles/technical-documentation/) the facts get checked before the sentences get polished.

## What should a documentation review check first?

A documentation review should check first that the product does what the page says. A technical page makes claims, such as which role can create an API key and what an invalid key returns, so list those claims before you touch the sentences that carry them.

Each claim that could break the reader's task needs a source outside the draft. Checking a draft against itself only tells you the draft is consistent.

A 500-word Docker explainer shows what an unchecked claim costs. Its paragraphs were careful, and [its heading about root](/articles/docker-is-weird-explainer/) was seven years out of date.

### Build a claim ledger

Put the claims in a table where every row has to point at a source. The API, role and response in this example are invented and don't describe a real product:

| Page claim | Verification source | Reviewer | Result |
| --- | --- | --- | --- |
| Workspace owners can create API keys | Released permission model | Product owner | Pending |
| The API accepts `Authorization: Bearer` | Current API schema plus request | Engineer | Pending |
| Invalid keys return `401 invalid_api_key` | Reproduced response | Engineer | Pending |
| The key is displayed once | Released UI | Product owner | Pending |

Reject a row when its source is the draft itself, somebody's memory of a demo, or another page that repeats the same unsupported sentence.

If you ask an AI model about the product before you ask an engineer, treat its answers as questions to put to the engineer. A plausible explanation from a model is not a verification source.

### Run what the page documents

Start in the environment the page promises its reader. Follow the released UI path, or run the API calls, CLI commands and code samples with the inputs the page gives.

Record enough for a second reviewer to repeat your check:

```text
Product version: [released version or commit]
Account role: [role used]
Runtime: [name and version]
Starting state: [required resource or clean project]
Command: [exact command copied from the render]
Expected signal: [status, output, or screen state]
Observed signal: [actual result]
```

If your run needed a credential, a global package or a feature flag that the page doesn't mention, add it to the page's prerequisites and run the page again.

### Trigger the error the page claims to fix

Cause the error on purpose. Then confirm that the message, the status code, the diagnostic step and the fix all match what the page says.

Record each recovery in four fields:

| Field | Required evidence |
| --- | --- |
| Symptom | Exact error or visible behavior |
| Diagnostic | Command or observation that separates likely causes |
| Recovery | The smallest documented fix, such as revoking one key |
| Proof | Signal that the recovery worked |

Replace "Try again" with a command that tells the reader what went wrong. Keep "Restart the service" only if the page says what the restart clears and how the reader can tell it worked.

## How do you decide whether a page should exist?

Decide by asking whether the page answers one question that no other page answers. A draft can be correct and still be the wrong page, because it repeats an existing answer or tries to serve two different readers.

### Write the page's purpose in one sentence

Before the review starts, write one sentence:

```text
This page helps [reader with starting state] decide or do [specific outcome].
```

If one reviewer fills in "create a key" and another fills in "understand authentication", the draft is doing two jobs. Split it into two pages or pick one job before anyone edits it.

The [technical tutorial guide](/articles/writing-technical-tutorials/) shows how a tutorial differs from a task page. The difference matters in review because a reviewer runs a tutorial from start to finish and checks a reference page one field at a time.

### Search for the answer that already exists

Search existing titles, body text and error strings before you give the draft its own URL. The command below is an illustration, so replace its search terms and the `content/` path with your project's:

```bash
rg -n -i 'create.*api key|invalid_api_key|authorization: bearer' content/
```

If two pages answer the same question, merge the useful parts into one and redirect the other. Publishing a second answer because the first file is awkward to edit leaves readers with two versions to choose between.

### Find the starting state the author forgot to mention

Mark everything the author already had when they wrote the page: an account role, a runtime, an installed package, a region, sample data, a credential.

Move each prerequisite above the first step that needs it. A reader shouldn't learn that they need an access request from the error message of the command that required the access.

## How do you review the page as a reader would?

Follow the page in order and check that each section gives you what you need to choose the next action. Then scan it out of order, the way someone returns to a page after a command has failed.

### Read the headings without the paragraphs

Extract the outline. The file path below is an illustration and not a page in this repository:

```bash
rg '^#{2,3} ' content/posts/example.md
```

[Google's heading guidance](https://developers.google.com/style/headings) asks for descriptive headings organized in a hierarchy, with no skipped levels. An outline that reads Overview, Setup, Configuration, Usage tells the reader nothing about the task, so I'd rewrite any heading that could be moved to another article without anyone noticing.

[Task-based documentation headings](/articles/documentation-headings/) goes through that rewrite one heading type at a time.

### Ask for proof after each step that matters

Each stage of a procedure needs a result the reader can see before they go on to the next stage. The API-key action, the role and the button label below are invented:

```text
Action: Create a test API key.
Proof: The key list shows the new key name and test scope.
Failure: If the Create key control is absent, confirm the workspace-owner role.
```

A screenshot of the final screen doesn't prove the middle steps worked. If step three can fail without an error message, step three needs its own check.

### Separate advice from criteria a reviewer can apply

"Keep paragraphs short" is advice. "Split a paragraph that holds both a setup step and its exception" is a criterion, because a reviewer can look at a paragraph and say whether it meets it.

Use a list for items of the same kind and a table to compare the same fields across rows, and keep the reasoning in prose. A page built only from cards and checklists can look organized and never explain why one choice is better than another.

## Why review the rendered page and not the Markdown?

Review the rendered page because it is what the reader gets, and it can break in ways the Markdown doesn't show. A rendered table can be clipped at phone width, and a fixed header can cover the heading a link jumps to.

### Build the page the way production builds it

Use the same build that production uses. For this site the build, the SEO audit and a local server are these commands:

```bash
python3 build.py
python3 seo_audit.py
python3 -m http.server 8765 --directory output
```

The build has to come from the branch under review, and it should stop on a missing page or canonical. If the preview is serving an older build directory, your screenshots show the old page.

GitLab's [documentation review apps](https://docs.gitlab.com/development/documentation/review_apps/) do this per merge request: team members can deploy a preview that shows how a docs change will look on the docs site before it merges. GitLab's [documentation workflow](https://docs.gitlab.com/development/documentation/workflow/) is built for a much larger docs set than a small static site has, and the part worth copying is reviewing the preview that belongs to the change.

### Check a desktop width and a phone width

Look at the title, the navigation, the tables, the code blocks, the images and the links at both widths. Copy a command from the rendered page and run it, because a renderer can drop or change a character.

Fix anything that is clipped, overlapped or unreachable. A line that wraps is fine unless the wrap changes what the line means, as it does when a long command breaks in the middle of a flag.

### Check the HTML structure

[W3C's page-structure tutorial](https://www.w3.org/WAI/tutorials/page-structure/) covers page regions, labels for those regions, headings and content structure. Check them in the page's HTML: one descriptive H1, heading levels in order, labeled navigation, table headers and image alternatives.

Test keyboard access in the browser, because the HTML doesn't show where the focus goes when a reader presses Tab.

A script can report a missing `alt` attribute, and it can't tell whether the alt text carries the image's information. My [documentation accessibility checklist](/articles/docs-accessibility/) has a checker for the structural part and the manual tests for the rest.

### Open every link from the rendered page

Check internal links, fragment links, external sources, canonicals and redirects on the rendered page. The `output/articles/example/` path below is an illustration, so use the page your change generated:

```bash
python3 seo_audit.py
rg -n 'href="[^"]+#' output/articles/example/index.html
```

Fix a fragment that doesn't match a heading, a redirect that hides a stale internal link, and a canonical that points at a different page. A link that returns `200` can still land the reader on the wrong answer.

## How do you match the page to the release?

Tie the page to the product version and the audience that will receive it. A page can be correct in a preview environment and wrong in production, for example when the feature hasn't shipped or the permission differs by plan.

### Record availability and timing

Add the release facts the page depends on:

| Release question | Evidence |
| --- | --- |
| Which version contains the behavior? | Release or commit record |
| Is a flag required? | Current feature status |
| Which roles, plans, or regions can use it? | Released availability source |
| Does an older supported version differ? | Versioned reference or compatibility test |
| When should the page become indexable? | Release plan |

Don't describe preview behavior as current behavior. For a breaking change, the page's compatibility statement has to agree with the [changelog](/articles/writing-changelogs/) and the [release notes](/articles/writing-release-notes/).

### Name what triggers the next review

"Review annually" lets eleven months of product changes go by. Tie the next review to the events that can make the page wrong: a renamed control, a dependency release, a permission change or a changed response schema.

Name an owner who will see that event in their normal work. If another team controls the fact, put that team's name there and not "the docs team".

## Who should approve a documentation change?

Each reviewer should approve the facts they can check, and nothing else. A single "LGTM" can't stand in for an engineer, an editor, an accessibility reviewer and a release owner, although on a small team the same person may answer more than one row:

| Reviewer | Evidence owned |
| --- | --- |
| Engineer or subject-matter expert | Product behavior, code, versions, risk, and recovery |
| Technical writer or editor | Reader fit, structure, terminology, and links |
| Accessibility reviewer or trained contributor | Semantics, keyboard behavior, visuals, and alternatives |
| Product or release owner | Scope, availability, timing, and migration state |
| Maintainer | Build, metadata, navigation, redirects, and deployment readiness |

Each reviewer should say what evidence they looked at. An engineer's approval of the commands says nothing about the alt text.

Terminology is in the writer's row because one term can mean different things across vendors, as [the phrase agent harness](/articles/what-agent-harness-means/) does.

## What do the first two passes look like on one page?

The example below runs the product pass and the reader's-route pass on an authentication guide for Orbit, an API I invented for this page. Orbit isn't a client project or a real service.

The draft under review says:

> Generate an API key in Settings, add it to your request, and run the example. The API returns your account.

Those two sentences are grammatical and leave out nearly everything a reader needs. They don't give the role, the navigation path, the header format, the expected response, the errors or the cleanup.

### Pass one: check the product contract

Suppose Orbit's behavior is defined like this:

```text
Role: workspace owner
Path: Developer settings > API keys
Header: Authorization: Bearer $ORBIT_API_KEY
Success: 200 with mode set to test
Invalid key: 401 invalid_api_key
Missing scope: 403 insufficient_scope
Cleanup: revoke the test key
```

### Pass one, continued: run the reader's request

The command below targets the made-up host `api.orbit.example` with a placeholder key. It isn't a live endpoint:

```bash
export ORBIT_API_KEY="replace-with-a-fictional-test-key"

curl --fail-with-body \
  --request GET \
  --url "https://api.orbit.example/v1/account" \
  --header "Authorization: Bearer $ORBIT_API_KEY"
```

The response the fixture defines is:

```json
{
  "id": "acct_example",
  "name": "Docs sandbox",
  "mode": "test"
}
```

The pass condition is `"mode": "test"`. A response without that field doesn't show that the request reached the test environment.

### Pass two: rewrite the headings as the reader's steps

Replace the headings Setup, Usage, Errors and Security with headings that name what the reader does:

- Create a test API key
- Send an authenticated request
- Fix an invalid or under-scoped key
- Store the key outside source control
- Revoke the test key

Put the cleanup step before any link that sends the reader to another page, and keep each error's fix next to the request that produces the error.

## What can you automate in a documentation review?

You can automate the checks whose answer doesn't depend on judgment:

- Markdown and frontmatter syntax
- Internal link and fragment resolution
- Duplicate slugs and heading IDs
- Missing image alternatives
- Heading-level jumps
- Build success
- Canonical, sitemap, and robots rules
- Redirect loops and chains

External link checks need retries and a short list of allowed exceptions, because a site can refuse an automated client and still load for readers. The link checker for this site hit that with a Harvard accessibility page, which returned 403 to a script.

A check should report the file, the rule and the command that reproduces the failure locally. It shouldn't call a page "high quality" because it counted the headings.

Whether the product matches the page, and whether the page helps its reader, still take a person to approve.

Writing a product's docs so they pass a review like this one is work I take on, described under [developer documentation](/services/developer-documentation/).

## Documentation review checklist

- Block publication when a behavior, permission or recovery claim has no source a reviewer can inspect.
- Run the commands from the documented starting state and record the success output and the error output.
- Give the page one question to answer, and name it in the title and the URL.
- Review the rendered page from the branch under review at desktop and phone widths.
- Match availability and version limits to the release.
- Have each reviewer approve only the evidence they can inspect.

## FAQ

**Should documentation block a product release?**

It should block the release when a missing or false instruction stops a reader from adopting, operating or recovering the product safely. A wording improvement can follow in a later change, as long as the published steps are true and usable.

**Can automated checks replace documentation review?**

No. Automation can verify structure, links and the build, and it can't confirm that the released product matches a claim on the page.

**Who should review documentation?**

An engineer checks behavior and code, a writer or editor checks reader fit and terminology, and a release owner checks availability and timing. On a small team one person can take more than one of those roles, with each check recorded separately.

**What is a claim ledger?**

A claim ledger is a table that lists each factual claim on a page next to the source that verifies it and the reviewer who checked it. A row whose only source is the draft itself fails.
