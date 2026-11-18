---
category: technical-documentation
primary_query: release notes
siblings:
- release-notes-template
- writing-changelogs
date: 2026-04-03
description: Write release notes that let developers assess upgrade risk, understand
  product impact, and migrate without surprises.
slug: writing-release-notes
status: published
work_note: "Release notes shouldn't make a developer read hundreds of words before learning whether the upgrade will break them. If you'd rather someone else write yours while you ship the release, I do that. I'm Ninad Pathak, a freelance technical writer. [Let's work together](/services/)."
takeaways:
- Put compatibility, affected users, and required action on the first screen.
- Separate product impact from launch language and implementation detail.
- Use visuals only when they clarify changed behavior or a migration.
- Automate the release inventory, then edit it for risk and consequence.
title: Writing Release Notes That Developers Trust
updated: 2026-11-17
---

OpenSSH 10.6p2, released on November 5, contains what [its own release notes](https://www.openssh.org/releasenotes.html) call "a critical security workaround", and a reader is 427 words into those notes before learning it. GitLab's [critical patch release](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-5-1-released/) of October 21 says who has to upgrade within 32 words.

Writing release notes that developers trust comes down to how many words a reader passes before learning whether they're affected. Someone opening the notes is deciding whether to upgrade and what it will cost, so the page has to answer that decision before it describes the release.

Release notes are [technical documentation](/articles/technical-documentation/) read with an upgrade waiting.

## How soon do real release notes say who is affected?

The notes I looked at ranged from 32 words to 427, counted from the release line to the first sentence that names affected users.

```python
"""Count the words a reader passes before a release note says who must act."""
import html
import re
import urllib.request

notes = [
    ("GitLab 19.5.1 (Oct 21)", "https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-5-1-released/",
     "On October 21, 2026, we released", "we strongly recommend that all self-managed"),
    ("Ghostty 1.4.0 (Oct 27)", "https://ghostty.org/docs/install/release-notes/1-4-0",
     "Release notes for Ghostty 1.4.0", "Paste protection didn't treat"),
    ("OpenSSH 10.6p2 (Nov 5)", "https://www.openssh.org/releasenotes.html",
     "Portable OpenSSH 10.6p2 was released", "This release contains a critical security workaround"),
]

for name, url, start, warning in notes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    page = urllib.request.urlopen(request, timeout=60).read().decode("utf-8", "replace")
    page = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", page)
    text = html.unescape(re.sub(r"<[^>]+>", " ", page)).replace("’", "'")
    begin = text.index(start)
    words = len(text[begin:text.index(warning, begin)].split())
    print(f"{name:<24} {words:>4} words before the first sentence about who is affected")
```

Saved as `first_warning.py`, it reports the distance for each note.

```text
GitLab 19.5.1 (Oct 21)     32 words before the first sentence about who is affected
Ghostty 1.4.0 (Oct 27)    144 words before the first sentence about who is affected
OpenSSH 10.6p2 (Nov 5)    427 words before the first sentence about who is affected
```

GitLab's opening is the model. Its second sentence says "we strongly recommend that all self-managed GitLab installations be upgraded to one of these versions immediately", and the third tells everyone else to stand down: "GitLab.com is already running the patched version."

[Ghostty 1.4.0](https://ghostty.org/docs/install/release-notes/1-4-0), released on October 27, spends its first 144 words on a summary and thanks, then lists security advisories ahead of any feature. Each advisory states what an attack needs, in sentences such as "This requires user interaction (copy-paste) to trigger." and "This affects Ghostty 1.3.0 and 1.3.1."

The OpenSSH sentence is precise once you reach it, naming "Linux systems that use the musl libc and PAM disabled". It sits below a donations paragraph and a deprecation notice, in the order the project's notes always use.

That order matters more as releases speed up. Since the 10.5 release in August the notes have opened with a paragraph on security reports found with AI tools, which says the team will be "making more frequent releases to get bugfixes into users' hands", and a project that ships more often asks its users to make the upgrade decision more often.

## Release notes and changelogs do different jobs

A changelog is the running list of every version, kept in a file such as `CHANGELOG.md`. Release notes cover one version and explain what it changes for users and what an upgrade takes.

Both can be written from the same merged pull requests.

| Changelog | Release notes |
|---|---|
| Covers many versions | Focuses on one release |
| Uses concise categorized entries | Adds context, examples, and migration guidance |
| Optimized for lookup | Optimized for an upgrade decision |
| Usually maintained as a continuous file | Published as a versioned page or release |

[GitHub's releases documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases) ties a release to a Git tag, its notes and its downloadable assets. A developer needs that tagged version to install or pin, and the notes explain what the version changes.

### Keep launch copy out of the risk summary

A launch post can explain why the team built the feature. Release notes say first what the product now does differently, and for whom.

"Our fastest release yet" tells an operator nothing they can act on. "Batch exports now finish up to 30 minutes after creation and send a webhook when the file is ready" describes behavior a developer can design around.

> If a sentence cannot help someone decide, migrate, verify, or troubleshoot, it does not belong above the technical changes.

## Put upgrade risk on the first screen

The opening should read like a status panel. A reader shouldn't have to inspect every feature section to discover a runtime requirement or a removed option.

### Name five things immediately

Lead with:

1. **Version and release date**
2. **Compatibility statement**
3. **Affected products, APIs, SDKs, or environments**
4. **Required action and deadline**
5. **Links to migration and rollback instructions**

A compact summary can look like this:

```text
Version:        4.0.0, 30 July 2026
Compatibility:  Breaking changes in authentication and pagination
Affected:       REST API and JavaScript SDK users
Action:         Migrate before 30 September 2026
Rollback:       v3 remains supported until the migration deadline
```

With that block first, nobody has to discover the risk halfway down the page, and the migration details follow it.

### Say who is not affected

Tell the readers who can ignore the release that they can. If a change affects only self-hosted deployments, say that cloud customers don't need to act, as GitLab's patch release does in its opening lines.

Saying who is unaffected matters more when a product has several SDKs, API versions or deployment models. Without it, every customer reads a broad warning as their own emergency.

## Write what changed for the user

A pull request title describes the work from the team's side, such as "Refactored token validation". Release notes have to say what that work changes for the person using the product.

### Turn internal changes into decisions

| Internal language | Release-note language |
|---|---|
| Refactored token validation | Expired tokens now return `401` immediately; clients that relied on the previous grace period must refresh sooner. |
| Added queue backpressure | Requests above the queue limit now return `429` with a `Retry-After` header. |
| Upgraded database driver | No application change is required, but self-hosted deployments now require PostgreSQL 15 or later. |
| Fixed CSV bug | CSV exports now preserve leading zeroes in string columns such as postal codes. |

The release-note wording lets a developer recognize their system and choose an action. Concrete terms such as the error code and the field name also let a search find the entry later.

### Separate breaking changes from new capability

Put migration work before the feature tour. Breaking changes, deprecations, security fixes and dropped environments get their own section.

Within that section, use the same order for every item:

- Previous behavior
- New behavior
- Affected users
- Required change
- Verification step
- Rollback or support path

The same order in every item lets a reader scan long notes.

### Be precise about security

Say which versions are affected and what users should do, and link the advisory.

The Ghostty notes above do it in one line per advisory, and GitLab's add a warning a version number can't carry: "upgrading GitLab is not sufficient: you must also upgrade Ruby" for installations that bring their own runtime. A phrase such as "security improvements" tells a reader neither how urgent the upgrade is nor which versions it covers.

Have whoever owns the advisory approve the wording, and leave out detail that would help someone build the exploit.

Cloudflare's report on a cache leak in Workers AI shows that wording done with care, and I've noted [what I'd copy from it](/articles/cloudflare-kv-cache-incident-report/).

## Show the changed behavior

A visual belongs in the notes when it shows the change faster than a sentence can. A two-line diff of an API response does that, and a screenshot of the whole dashboard doesn't.

### Use before-and-after examples

For an API change, I'd use a request or response diff cropped to the fields that changed:

```diff
- { "next_page": 3 }
+ { "next_cursor": "eyJpZCI6IjEwMDAifQ==" }
```

For an interface change, crop the screenshot to the control that moved or changed. The caption should say what the reader now does differently, say "Export moved from the toolbar to the row menu".

### Skip visuals for routine inventory

A dependency update needs no screenshot. An image there adds page weight and one more asset to keep current.

So the test for a visual is whether it helps someone migrate or check the new behavior.

## Let the version and prose make the same promise

[Semantic Versioning](https://semver.org/) uses `MAJOR.MINOR.PATCH` to signal compatibility. A major release contains incompatible API changes, a minor release adds backward-compatible functionality, and a patch release contains backward-compatible fixes.

The notes have to agree with the number. A patch release that drops a runtime, say Node.js 18 in a 3.4.2, makes a reader distrust both the number and the notes.

<div class="visual-wrapper">
  <div class="visual-title">Semantic Versioning at a glance</div>
  <div class="visual-container">
    <img src="/static/images/visuals/semver.png" alt="Semantic Versioning website showing the major, minor, and patch version number format" loading="lazy">
  </div>
</div>
<p class="visual-caption">The version number is the first compatibility signal. The notes have to state what the number can't, such as a patch release that also needs a newer Ruby.</p>

GitLab's patch release from the top of this page is that case. Its version number says patch, and its notes add that an installation bringing its own runtime must also upgrade Ruby.

### Explain support windows with dates

Give the version that deprecates the behavior, the version that removes it and a calendar date, in a form such as "Deprecated in 3.8, removed in 4.0 on 30 September 2026". "Deprecated soon" gives a team nothing to put in a plan.

If the schedule changes, update the page for the release that announced it, and link later notes back to that page.

### Include rollback limits

If a database migration or a new file format prevents a clean downgrade, say so before the upgrade steps. A rollback instruction that no longer works does more harm than a missing one, because the reader trusts it until the moment it fails.

State what can be reversed, which data needs a backup first, and the date support for the previous version ends.

## Automate collection, keep judgment human

Release tooling can already collect pull requests, contributors, labels and links. GitHub's [automatically generated release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes) can also sort them into categories and exclude some, through a `.github/release.yml` file.

The generated list saves collection time, and it is still a draft. It can't merge five pull requests into the one change a user sees, or spot the migration work behind a title like "Upgraded database driver".

Ghostty's maintainers went the other way and say so in the notes: "They take a combined 16+ hours to write". Those hours are the cost of the judgment, and a generated inventory doesn't remove it.

Those notes also say that human maintainers wrote them by hand, and my essay on [what a written-by-a-human label proves](/articles/written-by-a-human/) starts from that line.

### Build the notes during development

Ask the author of a user-visible change to record:

- The previous and new behavior
- The affected user or environment
- Compatibility and migration impact
- Documentation that must change
- A verification or test result
- Screenshots or examples when behavior is visual

Capture those answers in the pull request or an Unreleased entry while the author still remembers them. The person editing the release then starts from the answers and doesn't have to chase each engineer.

### Give one editor the full page

Individual engineers can verify their sections, but one person should edit the complete release for hierarchy, duplicate entries, tone, and missing links. Without that pass, the notes read like several teams pasted their sprint summaries together.

Edit from highest risk to lowest risk: breaking changes, security and support changes, fixes, new capability, and minor improvements.

## What order should release notes follow?

Release notes should start with what the reader has to decide, which is whether to upgrade now, and end with the reference detail. The labels can change, and the order below should stay the same from one release to the next.

1. **Release summary:** version, date, compatibility, scope, and action.
2. **Breaking changes:** migration, verification, deadline, and rollback.
3. **Security and support:** advisories, runtime requirements, and end-of-support dates.
4. **Fixes:** corrected behavior and affected users.
5. **New capabilities:** what is available and how to try it.
6. **Known issues:** symptoms, workarounds, and tracking links.
7. **Resources:** migration guide, reference changes, assets, and support.

The [release notes template](/articles/release-notes-template/) turns this order into a copyable Markdown file with a checker that fails a note missing its rollback line.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/writing-release-notes/release-layers.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/writing-release-notes/release-layers.narrow.svg" width="288" height="992"><img class="np-has-narrow" src="/static/images/diagrams/writing-release-notes/release-layers.svg" width="720" height="696" alt="A release note reads in three layers. The summary comes first with version, date, compatibility, and the action required. Impact comes second: breaking changes, security and support notes, fixes, new capabilities, and known issues with their workarounds. Resources such as the migration guide and reference changes come last, for readers who need the implementation detail." loading="lazy" decoding="async"></picture></a>
  <figcaption>A reader who only needs to know whether to upgrade can stop after the summary. Breaking changes and fixes come next, and the migration guide and reference links come last.</figcaption>
</figure>

### Final trust check

- Can a developer identify upgrade risk from the first screen?
- Are affected and unaffected users both clear?
- Does every breaking change include an action and verification step?
- Do the version number and compatibility claim agree?
- Does every deadline include a calendar date?
- Are screenshots current and necessary?
- Do migration, advisory, rollback, and reference links work?
- Can someone find the same release again by version?

## Worked example: write the notes for a breaking SDK release

Take a hypothetical `4.0.0` release of an SDK, with a [changelog](/articles/writing-changelogs/) kept alongside it. The changelog records five changes in a line or two each: pagination, the Node.js runtime, webhook retries, validation and login.

The release notes turn those entries into an upgrade plan: what to do first, how to check it worked and how far a rollback is safe.

### Open with the decision

The first screen could read:

```text
SDK 4.0.0, 30 July 2026

Upgrade effort: Medium
Compatibility: Breaking changes to pagination and Node.js support
Affected: JavaScript SDK users and REST integrations using `page`
Deadline: Version 3 security support ends 30 September 2026
Action: Upgrade to Node.js 20 and migrate list endpoints to cursors
Rollback: Safe until the first v4 cursor is stored; see rollback limits
```

"Medium" means something only because the fields under it say what the effort is: a Node.js upgrade and a pagination migration.

### Explain the migration in dependency order

The runtime has to be right before the package installs, and the package has to install before the code changes. So the migration steps go in that order:

1. Confirm that development, CI, and production run Node.js 20 or later.
2. Upgrade the SDK in a branch and run the existing integration tests.
3. Replace numeric `page` parameters with the returned `next_cursor`.
4. Make webhook handlers idempotent before enabling the new retry behavior.
5. Deploy to a test environment and compare pagination results.
6. Roll out gradually while monitoring `400` and `401` responses.

### Show the change where prose is weak

The pagination section gets a before-and-after of the one call that changes:

```diff
- const orders = await client.orders.list({ page: 3, limit: 50 });
+ const orders = await client.orders.list({ cursor, limit: 50 });
+ cursor = orders.nextCursor;
```

Then state what the diff can't show:

- Cursors follow creation-time order.
- A cursor is valid for 24 hours.
- Changing filters invalidates the previous cursor.
- The SDK returns `nextCursor: null` on the final page.

### State the rollback boundary

Suppose version 4 cursors cannot be passed to version 3. The notes should then say that rolling back the SDK is safe only until the application stores or exposes a v4 cursor.

A rollback block for that case might say:

> Keep version 3 deployed in the previous production slot. If error rates rise before v4 cursors are stored, shift traffic back. After that point, disable pagination writes and contact support before downgrading.

Writing that boundary down before release can prompt the engineers to make version 3 accept v4 cursors, when there is still time to do it.

### Separate known issues from migration work

If the release has a known issue with cursors on empty filtered results, give it a visible section:

```text
Known issue: A filtered list with zero results can return an empty string
for `nextCursor`; the expected value is `null`.

Workaround: Treat both values as the end of the list.
Tracking: SDK-917
Fixed in: Planned for 4.0.1
```

Include a searchable symptom, a workaround, a tracking reference and the version expected to fix it.

### Finish with verification

End the notes with checks the reader can run after upgrading:

- CI and production report Node.js 20 or later.
- The application no longer sends a numeric `page` parameter.
- A full pagination test returns every record exactly once.
- Duplicate webhook delivery does not create duplicate work.
- Monitoring shows no unexplained increase in `400`, `401`, or `429` responses.

Writing each release's notes for a team is work I take on, described under [release notes and changelogs](/services/changelogs-and-release-notes/).

## FAQ

**Who writes release notes?**

Release notes should be written by someone who knows what the release changes for its users, with engineers checking the sections they own. Ghostty's 1.4.0 notes were written by its maintainers, who put the cost at more than 16 hours.

**How long should release notes be?**

Release notes should be as long as the upgrade decision needs. A small patch may need five exact bullets, and a major version may need a summary with a separate migration guide.

**Should release notes include every pull request?**

No. Include the pull requests that change what a user sees, what the product is compatible with, its security or the environments it supports.

**Where should release notes be published?**

Publish them at a stable URL with the version in it, so developers can search for a release and link to it. A shorter copy can go in GitHub Releases or a package registry, with one page kept as the canonical one.

**What makes release notes trustworthy?**

Release notes earn trust by answering the same four questions in every release: who is affected, what they have to do, by when, and what is still broken. Developers trust notes when past releases helped them upgrade without surprises.

**Can AI write release notes from commit history?**

AI can group the commits and write a first draft, but commits seldom say who a change affects or what an upgrade takes. Someone who knows the release has to check the compatibility line, the affected users, the security wording and each required action.
