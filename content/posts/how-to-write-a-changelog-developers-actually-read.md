---
date: 2026-03-30
description: Most changelogs exist to satisfy a checkbox. Here's what makes developers
  actually read them, and how to structure entries so breaking changes land before
  they cause incidents.
status: published
tags:
- technical-writing
- developer-experience
- devtools
title: How to Write a Changelog That Developers Actually Read
---

A changelog nobody reads is infrastructure cost with no return. You pay someone to write it, you maintain the format, and developers still get surprised by breaking changes because they skimmed the entry or never opened the file. I once shipped a patch upgrade for a logging library and broke production because a "minor" config rename sat as the eighth bullet under Changed, unlabeled. Getting developers to read changelogs requires two things: a format that makes the critical information findable in seconds, and enough signal-to-noise ratio that they trust the document is worth their attention.

**Short answer:** Structure every entry around the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format: group by Added, Changed, Deprecated, Removed, Fixed, Security. Put breaking changes at the top of any version section with an explicit label. Keep the file in CHANGELOG.md, update it per release, and never combine multiple releases into a wall of bullet points without version headers.

## Why developers don't read changelogs (and why that's usually the changelog's fault)

Developers skip changelogs because the format punishes them. A 400-line wall of bullet points with no version grouping, no breaking-change callouts, and no date stamps forces a linear scan through irrelevant details to find the one thing that might affect their integration. Having scanned a few of these and found nothing useful, most developers conclude the effort isn't worth it and start treating the changelog as a post-incident reference only, opened after something already broke.

The format also fails when it conflates what changed with why it matters. "Updated authentication handler" tells me nothing. "Authentication handler now rejects tokens with `exp` claims in the past (previously these were accepted with a 10-second grace window)" tells me everything I need to decide whether to read further.

Separating technical details from the lead entry is what [Stripe's changelog approach](https://docs.stripe.com/changelog) does well. Developers who need the quick summary get it immediately. Those who need migration specifics click through. That separation comes from understanding that changelog readers arrive in one of two modes: skimming for impact, or deep-reading for a migration path. A single flat entry serves neither, the way a restaurant menu that prints the full recipe under each dish helps nobody actually order.

## The keepachangelog.com spec and why it became the standard

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) established the format that most serious developer tools have converged on: entries grouped by version (newest first), dates in ISO 8601 format (YYYY-MM-DD), and change types categorized as Added, Changed, Deprecated, Removed, Fixed, or Security.

The six categories matter because they map to developer intent:
- **Added** and **Changed** are features worth knowing about before upgrading
- **Deprecated** tells you what to stop using before it disappears
- **Removed** is the first thing to scan before any upgrade
- **Fixed** is relevant if you hit the bug, skip otherwise
- **Security** gets read immediately by anyone running the library in production

With this structure, developers learn to scan a version section in under 10 seconds. They look for Removed and Security first, then Deprecated, then Changed for anything in their integration surface. My own eye goes Security, Removed, Deprecated, in that order, before I read a single word of the feature additions. That pattern only works if the format is consistent across every release, because the moment one release buries Security under Added, the reader stops trusting the column order and reverts to reading everything.

<div class="visual-wrapper">
  <div class="visual-title">Anatomy of a Changelog Entry</div>
  <div class="visual-container">
    <iframe src="/static/visuals/changelog-anatomy.html" title="A scannable changelog entry annotated with version, ISO date, grouped changes, a breaking-change label, and a migration link, versus an unscannable one" loading="lazy"></iframe>
  </div>
</div>

An `Unreleased` section at the top, for changes merged to the main branch that haven't shipped yet, rounds out the spec. Many teams skip this. Keeping an Unreleased section means contributors document changes as they land, which kills the Friday-afternoon scramble of reconstructing a release from a week of commit messages and cuts the risk of a change shipping with no entry at all.

## Breaking changes need a higher signal level than a category

As a category heading for a breaking change in a heavily-used API, "Removed" carries almost no signal on its own. A developer scanning a version section will still miss it when it sits as the fifth item in a list and the entry text opens with the mechanic instead of the impact.

[Mintlify's analysis of developer brand changelogs](https://www.mintlify.com/blog/five-changelog-principles-from-best-developer-brands) recommends prefixing breaking changes with a visible label, something like `[BREAKING]` or bolded text, and positioning them at the top of the Removed or Changed section. Stripe's SDK changelogs use warning symbols and direct developers to review migration paths before upgrading.

Front-loading the consequence is what the entries themselves should do. A line reading "Removed the `legacy_token` parameter" makes me hunt for what it costs me. A line reading "Removed `legacy_token` parameter from authentication calls, replace with `api_key` before upgrading or requests will return 401" tells me in one read whether I can ignore this release or have to stop and migrate.

A practical template for breaking change entries:

```
### Removed
- **[BREAKING]** Removed `legacy_token` parameter from `/v2/auth`.
  Replace with `api_key` parameter. All requests using `legacy_token`
  will return HTTP 401 after upgrading. See migration guide: [link]
```

For a breaking change, the migration link is not optional. A developer who needs to migrate and finds no path forward will open a support ticket or file a GitHub issue, and answering ten of those one by one in a thread costs your team far more time than writing the migration guide once.

## Yanked releases belong in the changelog

A yanked release is a version pulled after shipping because of a critical bug or security issue, the kind of thing where a corrupt build or a leaked credential makes leaving it on the registry worse than removing it. Many changelogs omit yanked versions entirely, so a developer who already installed the yanked version and searches the changelog for context finds nothing and has to reverse-engineer why their pinned dependency vanished.

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) handles this with a `[YANKED]` label on the version entry plus a note explaining why. A developer who installed `2.3.1` and sees `2.3.1 - 2026-02-14 [YANKED]` with "Critical memory leak in connection pool, replaced by 2.3.2" gets the context they need immediately.

Leaving yanked versions out turns the changelog into marketing material rather than a technical record, and engineers detect that shift immediately because of [the developer trust hierarchy that ranks practitioner writing over marketing](/blog/developer-trust-hierarchy/). A changelog should be the complete history of every version, including the ones you'd rather forget shipped.

## How Linear, Vercel, and Stripe handle release communication differently

These three developer tools have different changelog philosophies, and each one reflects a different assumption about their audience, the same care that goes into [writing release notes that developers trust](/blog/writing-release-notes-that-developers-trust/).

**Linear** uses an embedded product-focused approach. Their [weekly changelog](https://linear.app/changelog) combines short descriptions with native embedded videos. The format works because Linear's audience is a mix of developers and product managers, and the visual format reduces the reading burden. Linear stores minor bug fixes and API updates in collapsible sections to avoid diluting the signal from major feature releases.

**Vercel** links aggressively to associated packages and documentation, and uses screenshots of the affected UI. Vercel's changelog assumes developers want to see the change, not just read about it. The density is higher than Linear's because the audience is more technical.

**Stripe** takes a more formal, API-documentation-style approach. Each changelog entry for API changes links to the specific endpoint in the reference docs. Breaking changes get migration guides. The format is less visually engaging but maximizes precision, which matches Stripe's audience: developers who need to make careful upgrade decisions because payment integrations have real financial consequences if they break.

Across all three, the lesson holds: match the format to your audience's upgrade stakes. Low-stakes tooling, where a bad upgrade means a quick rollback, can afford a visual narrative format. High-stakes infrastructure, where a bad upgrade can drop payments or take down auth, needs precision and migration paths.

## Semantic versioning as a communication contract

[Semantic versioning](https://semver.org/) (MAJOR.MINOR.PATCH) is a promise: patch releases are safe to take automatically, minor releases add functionality without breaking existing integrations, and major releases may require migration.

Honoring that contract in the changelog is what makes it real. A major version bump with no entry explaining what broke tells developers your version numbers are decoration, and from then on they read every release as if it might break, which defeats the point of semver. Worse is the minor bump that quietly changes a default timeout or an error code without documentation, because that is a breaking change wearing the costume of a safe upgrade.

A minimum notice period of 3-6 months between a deprecation entry and the actual removal is what [Zuplo's semantic versioning guide](https://zuplo.com/learning-center/semantic-api-versioning) recommends. Publishing the deprecation entry in a minor release, then removing in the next major, gives developers time to adapt. Plenty of production integrations sit untouched for a quarter or more between minor upgrades, so the deprecation window has to be long enough that a team on a slow upgrade cadence still sees the warning before the thing disappears under them.

## My take on why most changelogs fail

Treating the document as a record of what was done, rather than a message to someone who has to make a decision, is where most changelog failures begin. Whoever writes the entry holds all the context: why the change was made, what it replaces, where the migration path leads. Whoever reads it holds none of that and has to decide whether this release is safe to pull into a running system.

Once you hold that distinction in your head, the writing changes entirely. "Updated dependency X" is a record. "Updated X from 3.1 to 3.2 to address CVE-2026-0231 (CVSS 7.4), no API changes required" is communication, because it answers the only two questions the reader has: do I need this, and will it break me.

Ownership is the other failure I see again and again. Developers merge PRs, releases ship, and nobody touches the changelog until it's time to cut a release, at which point someone is squinting at a week of commit messages trying to remember what a squashed merge actually changed. Requiring a changelog entry on every PR that touches the public surface area fixes this, and I frame it to teams not as a process tax but as the same discipline as writing a commit message: part of how the change gets communicated outward.

A good changelog also doubles as a forcing function for good API design, which is the part teams rarely expect. Having to explain a change in plain language to a developer who lacks your context, you notice fast when a change is hard to describe clearly. A rename that takes three sentences to justify, or a parameter whose new behavior you can't state without a caveat, is usually a design that should have been reconsidered before it ever reached the changelog.

## FAQ

**Should the changelog live in the repo or on a web page?**
Both, ideally. CHANGELOG.md in the repo satisfies developers who want it under version control alongside the code. A web page (or published GitHub releases) makes it discoverable without cloning. The canonical source should be the repo file. The web version is a rendering of it.

**How detailed should a non-breaking change entry be?**
One sentence that answers "what changed and what does it let me do that I couldn't before?" For a new feature: include the parameter name, the default value, and the simplest use case. For a fix: what was the incorrect behavior and what is the correct behavior now? Skip the internal implementation details.

**What's the right release frequency for changelogs?**
Match your release cadence. Never accumulate multiple releases without entries. If you ship five patch releases and document them all at once, the developer who upgraded on patch 3 has no way to know what changed between 3 and 5. One entry per release, even if the entry is a single line.

**How do you handle changelogs for libraries with many active versions?**
Maintain separate changelog sections per major version, or separate files. A developer on v2 should be able to read v2's history without wading through v3 changes that don't apply to them. Stripe handles this by filtering their changelog by API version.

**Should changelogs include internal changes or only public surface area?**
Only public surface area. Internal refactors, test updates, and CI changes are noise for someone deciding whether to upgrade. The changelog audience is integrators, not contributors. Keep internal changes in commit history and PR descriptions.