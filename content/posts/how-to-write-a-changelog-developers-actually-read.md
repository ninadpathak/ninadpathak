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

A changelog nobody reads is infrastructure cost with no return. You pay someone to write it, you maintain the format, and developers still get surprised by breaking changes because they skimmed the entry or never opened the file. Getting developers to read changelogs requires two things: a format that makes the critical information findable in seconds, and enough signal-to-noise ratio that they trust the document is worth their attention.

**Short answer:** Structure every entry around the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format: group by Added, Changed, Deprecated, Removed, Fixed, Security. Put breaking changes at the top of any version section with an explicit label. Keep the file in CHANGELOG.md, update it per release, and never combine multiple releases into a wall of bullet points without version headers.

## Why developers don't read changelogs (and why that's usually the changelog's fault)

Developers skip changelogs because the format punishes them. A 400-line wall of bullet points with no version grouping, no breaking-change callouts, and no date stamps forces a linear scan through irrelevant details to find the one thing that might affect their integration. Most developers learn that the effort isn't worth it and start using changelogs as a post-incident reference only.

The format also fails when it conflates what changed with why it matters. "Updated authentication handler" tells me nothing. "Authentication handler now rejects tokens with `exp` claims in the past — previously these were accepted with a 10-second grace window" tells me everything I need to decide whether to read further.

[Stripe's changelog approach](https://docs.stripe.com/changelog) separates technical details from the lead entry. Developers who need the quick summary get it immediately; those who need migration specifics click through. That separation is a design decision that comes from understanding that changelog readers are in two modes: skimming for impact, or deep-reading for migration path.

## The keepachangelog.com spec and why it became the standard

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) established the format that most serious developer tools have converged on: entries grouped by version (newest first), dates in ISO 8601 format (YYYY-MM-DD), and change types categorized as Added, Changed, Deprecated, Removed, Fixed, or Security.

The six categories matter because they map to developer intent:
- **Added** and **Changed** are features worth knowing about before upgrading
- **Deprecated** tells you what to stop using before it disappears
- **Removed** is the first thing to scan before any upgrade
- **Fixed** is relevant if you hit the bug; skip otherwise
- **Security** gets read immediately by anyone running the library in production

Developers learn to scan a version section in under 10 seconds using this structure. They look for Removed and Security first, then Deprecated, then Changed for anything in their integration surface. That pattern only works if the format is consistent across every release.

The spec also includes an `Unreleased` section at the top for changes in the main branch that haven't shipped yet. Many teams skip this. Keeping an Unreleased section means contributors can document changes as they land, which eliminates the scramble to write the changelog right before a release and reduces the risk of undocumented changes.

## Breaking changes need a higher signal level than a category

"Removed" as a category heading is not enough signal for a breaking change in a heavily-used API. A developer scanning a version section will still miss it if it's the fifth item in a list and the entry text doesn't lead with the impact.

[Mintlify's analysis of developer brand changelogs](https://www.mintlify.com/blog/five-changelog-principles-from-best-developer-brands) recommends prefixing breaking changes with a visible label, something like `[BREAKING]` or bolded text, and positioning them at the top of the Removed or Changed section. Stripe's SDK changelogs use warning symbols and direct developers to review migration paths before upgrading.

The entries themselves should front-load the consequence. Not: "Removed the `legacy_token` parameter." Instead: "Removed `legacy_token` parameter from authentication calls — replace with `api_key` before upgrading or requests will return 401."

A practical template for breaking change entries:

```
### Removed
- **[BREAKING]** Removed `legacy_token` parameter from `/v2/auth`.
  Replace with `api_key` parameter. All requests using `legacy_token`
  will return HTTP 401 after upgrading. See migration guide: [link]
```

The migration link is not optional for breaking changes. A developer who needs to migrate and has no path forward will open a support ticket or file a GitHub issue. Both are more expensive than writing the migration guide.

## Yanked releases belong in the changelog

A yanked release is a version pulled after shipping because of a critical bug or security issue. Many changelogs omit yanked versions, which means developers who installed the yanked version and search the changelog for context find nothing.

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) handles this with a `[YANKED]` label on the version entry plus a note explaining why. A developer who installed `2.3.1` and sees `2.3.1 - 2026-02-14 [YANKED]` with "Critical memory leak in connection pool, replaced by 2.3.2" gets the context they need immediately.

Omitting yanked versions from changelogs treats the changelog as marketing material rather than a technical record. The changelog should be the complete truth about version history, including the versions you'd rather forget.

## How Linear, Vercel, and Stripe handle release communication differently

These three developer tools have different changelog philosophies, and each one reflects a different assumption about their audience.

**Linear** uses an embedded product-focused approach. Their [weekly changelog](https://linear.app/changelog) combines short descriptions with native embedded videos. The format works because Linear's audience is a mix of developers and product managers, and the visual format reduces the reading burden. Linear stores minor bug fixes and API updates in collapsible sections to avoid diluting the signal from major feature releases.

**Vercel** links aggressively to associated packages and documentation, and uses screenshots of the affected UI. Vercel's changelog assumes developers want to see the change, not just read about it. The density is higher than Linear's because the audience is more technical.

**Stripe** takes a more formal, API-documentation-style approach. Each changelog entry for API changes links to the specific endpoint in the reference docs. Breaking changes get migration guides. The format is less visually engaging but maximizes precision, which matches Stripe's audience: developers who need to make careful upgrade decisions because payment integrations have real financial consequences if they break.

The lesson across all three: match the format to your audience's upgrade stakes. Low-stakes tooling can afford a visual, narrative format. High-stakes infrastructure needs precision and migration paths.

## Semantic versioning as a communication contract

[Semantic versioning](https://semver.org/) (MAJOR.MINOR.PATCH) is a promise: patch releases are safe to take automatically, minor releases add functionality without breaking existing integrations, and major releases may require migration.

That contract only works if you honor it in the changelog. A major version bump with no entry explaining what broke is a signal to developers that your versioning isn't trustworthy. A minor version bump that introduces a behavioral change without documentation is a breaking change without warning.

[Zuplo's semantic versioning guide](https://zuplo.com/learning-center/semantic-api-versioning) recommends a minimum notice period of 3-6 months between a deprecation entry in the changelog and removal. Publishing the deprecation entry in a minor release, then removing in the next major, gives developers time to adapt. Most production integrations don't get touched between minor releases; the deprecation window needs to be long enough to catch development cycles.

## My take on why most changelogs fail

Most changelog failures come from treating the document as a record of what was done rather than communication to someone who needs to make a decision. The writer of the entry knows the context: why the change was made, what it replaces, what the migration path is. The reader of the entry has none of that context and needs to decide whether this release is safe to take.

That mental model shift changes the writing entirely. "Updated dependency X" is a record. "Updated X from 3.1 to 3.2 to address CVE-2026-0231 (CVSS 7.4); no API changes required" is communication.

The other consistent failure: no one owns the changelog. Developers merge PRs, releases ship, and no one maintains the changelog entry until it's time to cut a release. At that point, reconstructing a week's worth of merged changes from commit messages is painful enough that entries become abbreviated. The fix is requiring a changelog entry on every PR that touches the public surface area — not as a process burden, but as part of how the team communicates externally.

The non-obvious insight: a good changelog is a forcing function for good API design. When you have to explain what changed and why to a developer who doesn't have your context, you notice quickly when a change is hard to explain clearly. Changes that are hard to document are often changes that should have been designed differently.

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