---
category: technical-documentation
primary_query: how to write a changelog
siblings:
- writing-release-notes
- release-notes-template
bridges:
- slug: agents-reading-docs
  reason: A docs page now has agent readers.
date: 2026-03-30
description: How to write a changelog developers can search. Put breaking changes, removals and deprecations first, with counts from a month of one real changelog.
slug: writing-changelogs
status: published
work_note: "This post is about keeping a changelog readable when more pull requests ship than any person can read. If you'd rather someone else handle the changelog while you work on the product, that's what I do. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Here's how we'd work together](/services/)."
takeaways:
- Put breaking changes, removals and deprecations above routine entries.
- Write each entry so it makes sense when a search or a tool lifts it out of the file.
- State the condition under which a user notices the change, then the action.
- Keep an Unreleased section and add entries with the pull request.
title: "How to Write a Changelog"
updated: 2026-11-17
---

Claude Code published 20 releases between October 18 and November 16, and its [changelog](https://code.claude.com/docs/en/changelog) lists 1,807 entries for them, about sixty a day. An entry among them tells people who use fast mode on Opus 4.8 that their requests will start returning errors after November 30.

A changelog that developers read has to make that entry findable by someone who will never read the other 1,806. Writing a changelog means recording each change so that a person can assess an upgrade from it, and at this release rate the person gets there by searching the file or by asking a tool that read it for them.

A changelog is the page of [technical documentation](/articles/technical-documentation/) that only grows.

## How much changelog can one person read?

Far less than a fast-moving project now publishes. The thirty days to November 16 break down like this, with every entry counted under the label it sits beneath.

```text
window: 2026-10-18 to 2026-11-16
releases: 20
entries: 1807  (90.3 per release, 60.2 per day)
entries that open with Deprecated or Removed: 11
label             releases  entries
N bug fixes             16     1149
Changed                 16      293
N improvements          15      223
Added                   16      133
(no label)               0        5
Improved                 1        4
```

The largest group is the one a reader is invited to skip, a collapsed list with a counted label such as "233 bug fixes". The five entries with no label come from four small releases, and for two of those the whole release reads "Bug fixes and reliability improvements".

`python3 changelog_stats.py` produced the table, and its window is fixed so the counts hold as the page grows.

```python
"""Count releases, entries and section labels in the Claude Code changelog over a 30-day window."""
import datetime
import re
import urllib.request

url = "https://code.claude.com/docs/en/changelog.md"
request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
text = urllib.request.urlopen(request, timeout=60).read().decode("utf-8")

end = datetime.date(2026, 11, 16)
start = end - datetime.timedelta(days=29)
release = re.compile(r"^\*\*(\d+\.\d+\.\d+)\*\*\s+(\w+ \d+, \d{4})\s*$", re.M)
matches = list(release.finditer(text))

releases = entries = flagged = 0
headings = {}  # label -> [releases that use it, entries under it]
for i, match in enumerate(matches):
    day = datetime.datetime.strptime(match.group(2), "%B %d, %Y").date()
    if not start <= day <= end:
        continue
    body = text[match.end(): matches[i + 1].start() if i + 1 < len(matches) else len(text)]
    releases += 1
    current = "(no label)"
    for line in body.splitlines():
        label = re.match(r"^\*\*([^*]+)\*\*$", line.strip())
        if label:
            current = re.sub(r"^\d+ ", "N ", label.group(1))
            headings.setdefault(current, [0, 0])[0] += 1
        if line.lstrip().startswith("* "):
            entries += 1
            headings.setdefault(current, [0, 0])[1] += 1
            if re.match(r"\* (\\\[[^]]+\] )?(Deprecated|Removed) ", line.lstrip()):
                flagged += 1

print(f"window: {start} to {end}")
print(f"releases: {releases}")
print(f"entries: {entries}  ({entries / releases:.1f} per release, {entries / 30:.1f} per day)")
print(f"entries that open with Deprecated or Removed: {flagged}")
print("label             releases  entries")
for name, (used, count) in sorted(headings.items(), key=lambda kv: -kv[1][1]):
    print(f"{name:<17} {used:>8}  {count:>7}")
```

The project knows nobody reads all of it. The page describes itself as generated from the CHANGELOG.md file in the project's GitHub repository, and says "Longer releases are grouped by type of change, with long lists of improvements and bug fixes collapsed."

Its Added and Changed labels match two of the six in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), though the page names no format, so the resemblance is my observation. Keep a Changelog 1.1.0, which its own changelog dates to February 15, 2019, opens its principles with "Changelogs are for humans, not machines."

I think that is still right about who makes the upgrade decision and seven years out of date about who reads first. Fern's [State of Docs report](https://buildwithfern.com/post/state-of-docs) from November 10 says of the changelog that "Agents read it twice as much as people to understand what's changed on your platform."

That figure comes from the docs sites Fern hosts, and [my essay on agents reading docs](/articles/agents-reading-docs/) looks at how it was counted. An entry a tool lifts out of the file arrives without its heading or its neighbours, so it has to make sense alone, and the fast mode entry does.

> Deprecated fast mode for Opus 4.8 as of October 30, 2026; it will be removed on November 30, 2026. After removal, fast mode requests on Opus 4.8 return an error and do not fall back to standard Opus 4.8. Migrate to Opus 5.5 to keep the speedup

It names the feature, gives both dates and states the failure a user will see. It sits in a list headed "Changed", though, and only eleven entries in the month open with the word Deprecated or Removed, none of them under a heading of their own.

## Start with the upgrade decision

Put the version and date first, then every change that needs action, then the rest. Keep a Changelog states the minimum as "If you do nothing else, list deprecations, removals, and any breaking changes in your changelog."

A person reading a release wants to know whether upgrading will break anything they run, and what to do if it will. The entries below, all from the same month, show how much of that one line can carry.

| Entry, quoted in full | Release | What a reader can decide |
| --- | --- | --- |
| "Bug fixes and reliability improvements" | 2.1.308, October 22 | Nothing, since it names no behaviour |
| "Changed some `cp` and `mv` commands to ask first" | 2.1.326, November 16 | That a script may now stop for a prompt, without knowing which commands |
| "Changed nested skill loading: `.claude/skills` folders in `--plugin-dir` plugins no longer load from a session started above them; start Claude Code in the plugin folder instead" | 2.1.325, November 13 | Whether their setup is the one affected, and the fix |

The third entry follows a pattern worth copying. It gives the thing that changed and the condition under which a user would notice, and it ends with the action.

The second may be vague on purpose, since a permission rule spelled out in full can tell an attacker what to avoid. Even then a link to the rule's documentation would let the affected reader find out.

Implementation detail belongs in an entry only when it helps someone diagnose or adapt. A refactor that users can't observe needs no entry at all.

## Which headings should a release use?

Use Keep a Changelog's six types of change, and put the ones that demand action first. The format lists releases newest first with the date beside each version, and it defines the types in a few words each.

| Type | Keep a Changelog's definition |
| --- | --- |
| Added | "for new features." |
| Changed | "for changes in existing functionality." |
| Deprecated | "for soon-to-be removed features." |
| Removed | "for now removed features." |
| Fixed | "for any bug fixes." |
| Security | "in case of vulnerabilities." |

<div class="visual-wrapper">
  <div class="visual-title">The Keep a Changelog structure</div>
  <div class="visual-container">
    <img src="/static/images/visuals/keep-a-changelog.png" alt="Keep a Changelog website showing its guidance for human-readable and chronologically organized changelogs" loading="lazy">
  </div>
</div>
<p class="visual-caption">Versions, dates and change types make the file predictable for someone assessing a release.</p>

The format has no heading for a change that breaks an integration without removing anything, and "Changed" will hold it beside harmless adjustments. My addition is a Breaking heading at the top of the release, followed by Removed and Deprecated, with the routine types below.

That ordering is where I part from the Claude Code page, which files deprecations and removals under "Changed". The entry below, from version 2.1.300 on October 14, is written well enough to stand under a Removed heading as it is.

> Removed the `--sandbox` and `--no-sandbox` flags from `claude remote-control`, which had no effect; passing either now exits with an error. Set `sandbox.enabled` in settings to sandbox sessions

A script that passed either flag started failing on that release, so the entry describes a breaking change. A reader scanning 88 entries would find it faster under its own heading.

Leave out a heading that has nothing under it. The types are a fixed vocabulary, and a release uses the ones it needs.

### Keep an Unreleased section

Keep a Changelog recommends it in one line: "Keep an Unreleased section at the top to track upcoming changes." Contributors add an entry there with the change, and at release time the section moves under a version and a date.

### Mark yanked releases

A release that was withdrawn keeps its entry. Keep a Changelog says of such versions "Often these versions don't even appear in change logs.", argues that they should, and marks them in the heading.

```markdown
## [0.0.5] - 2014-12-13 [YANKED]
```

Anyone who installed the version can then find out why it was pulled and which release replaces it.

## Should the version number agree with the entry?

Yes, wherever the project makes a versioning promise. [Semantic Versioning](https://semver.org/) defines each part of `MAJOR.MINOR.PATCH` by compatibility, and its summary gives the first as "MAJOR version when you make incompatible API changes".

Under that promise a removed flag in a patch release contradicts the number before anyone reads the notes. Keep a Changelog's principles include "Mention whether you follow Semantic Versioning.", and the reason is that a reader treats the number as a claim.

Claude Code's changelog page never mentions Semantic Versioning, and all 20 releases in the month carry a 2.1 number, including the one that deprecated fast mode. The number in such a project tells a reader nothing about compatibility, so the entry text has to carry all of it.

### Treat deprecation as a sequence

A deprecation entry should name the feature and its replacement, give the removal date, and link to the migration steps. The fast mode entry has all of that except the link.

Semantic Versioning asks for the same order in its FAQ: "Before you completely remove the functionality in a new major release there should be at least one minor release that contains the deprecation". Keep a Changelog describes the reader's side of it, an upgrade to the version that lists deprecations followed by an upgrade to "the version where the deprecations become removals."

When the removal ships, its entry should link back to the deprecation. A reader who missed the first notice can then see when it was given.

### State compatibility in plain words

Say whether existing setups keep working, and name the exception in the same entry. A Claude Code entry from November 12 does this in its second half.

> Removed the `subagentStatusLine` setting: subagent rows always use the default look, and settings files that still hold the key load as before

The clause after the comma answers the question an upgrading reader has, which is whether an old settings file will now fail.

<figure class="np-figure">
  <a class="np-figure-zoom" href="/static/images/diagrams/writing-changelogs/entry-anatomy.svg"><picture><source media="(max-width: 712px)" srcset="/static/images/diagrams/writing-changelogs/entry-anatomy.narrow.svg" width="288" height="720"><img class="np-has-narrow" src="/static/images/diagrams/writing-changelogs/entry-anatomy.svg" width="720" height="256" alt="A useful changelog entry exposes four layers in order: the version and date, the category it is grouped under with breaking changes first, the impact on the affected user, and the migration path or link that finishes the job. A reader can stop at the first layer that answers their question." loading="lazy" decoding="async"></picture></a>
  <figcaption>A strong entry exposes version, date, category, impact, and migration path in layers. A reader can stop after the first useful answer or continue into the details.</figcaption>
</figure>

## How does a changelog stay current?

Write each entry with the change that causes it, in the same pull request. The reviewer can then check the code and the entry's claim about it together.

Leave out commits with no visible effect. Keep a Changelog's case against pasting the log is "Using commit log diffs as changelogs is a bad idea: they're full of noise."

### Let automation collect and a person decide

GitHub's [automatically generated release notes](https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes) "include a list of merged pull requests, a list of contributors to the release, and a link to a full changelog." A `.github/release.yml` file can sort pull requests into categories by label and exclude others.

That output is a list of titles. Someone still has to decide which of them a user must act on, merge the ones that describe one change, and move the risky ones to the top.

### Give the file an owner

Name the person who checks the file before each release, and put that check in the release checklist. I'd have the engineer who made a change confirm the technical claim in its entry, since the entry is a statement about their code.

## Changelog checklist

- The version and date are correct, and releases appear newest first.
- Breaking changes, removals and deprecations sit above routine entries.
- Each entry describes behaviour a user can observe.
- Deprecated and removed features name a replacement.
- Links to migration and reference pages resolve.
- The version number matches the compatibility claim, where the project makes one.
- The Unreleased section is ready for the next change.

A last check is to read only the headings and the first words of each bullet. If the upgrade risk isn't visible from those, reorder the release.

## Worked example: regroup one real release

Version 2.1.323 of Claude Code, released on November 12, lists four entries under "Changed" that ask something of the reader. They are quoted exactly below, and the headings and their order are the only things I changed.

```markdown
## [2.1.323] - 2026-11-12

### Breaking

- Changed organization settings and policy requests to no longer use a proxy
  set only by `ALL_PROXY`; set `HTTPS_PROXY` if your network needs a proxy
  for them

### Removed

- Removed the `subagentStatusLine` setting: subagent rows always use the
  default look, and settings files that still hold the key load as before
- Changed `MCP_SDK_GENERATION=v1` to run the v2 MCP client in a
  compatibility mode (earlier handshake, relaxed OAuth sign-in checks),
  because the v1 MCP client is removed

### Deprecated

- Deprecated a plugin's `agent` setting: it still applies, and now warns at
  startup, in `claude plugin list` and in `claude plugin validate`
```

The original release has 294 entries, and these four were spread through a "Changed" list beside message limits and permission prompts. Regrouped, a reader behind a corporate proxy sees the line that affects them in the first screen.

The exercise also shows what a heading can't fix. The deprecation entry gives no removal date and no replacement, and a heading that says Deprecated makes that absence more obvious.

A changelog keeps the full sequence of changes, and [release notes explain one release](/articles/writing-release-notes/) in enough depth for a developer to act on it. The [release notes template](/articles/release-notes-template/) has the outline for that page.

## FAQ

**What is the difference between a changelog and release notes?**

A changelog is the chronological record of changes across every version. Release notes explain one release in more depth, with context and migration guidance.

**Should every commit appear in a changelog?**

No. Include changes that affect behaviour a user can see, compatibility, security or supported environments.

**Where should a changelog live?**

Keep a `CHANGELOG.md` file in the repository when developers consume the project from source or a package registry. A copy on the documentation site should be generated from that file, which is how the Claude Code page describes itself.

**How detailed should a changelog entry be?**

Detailed enough to show who is affected, what changed and whether action is required. Link to a migration guide when the change needs several steps.

**Can generated release notes replace a changelog?**

They collect the merged pull requests. Deciding which of those a user has to act on is still an editing job.
