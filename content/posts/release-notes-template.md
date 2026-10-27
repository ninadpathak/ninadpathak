---
category: technical-documentation
date: 2026-10-22
description: A release notes template in Markdown that puts the upgrade decision first, with a filled SDK example and a checker that fails a note missing its rollback line.
slug: release-notes-template
status: published
takeaways:
- Put compatibility, affected users, required action and rollback in a summary block at the top.
- Give each breaking change a migration step, a verification check and a calendar deadline.
- Run the checker with --filled before publishing, so a missing field fails the build.
title: 'Release Notes Template: Copyable Markdown With a Pre-Publish Check'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation that starts from the behavior a release changed and the check that proves a migration worked.'
video: release-notes-template
---

After its download links, the [Kubernetes v1.31.0 changelog](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.31.md#v1310) puts a section called "Urgent Upgrade Notes", subtitled "(No, really, you MUST read this before you upgrade)", ahead of the changes by kind. The Go 1.23 release notes restate the Go 1 compatibility promise in their introduction, so a reader learns in one sentence whether their programs should still build.

Both projects order the page around the upgrade decision. My template follows the same order, and it ships with a filled example and a small checker that fails a release note missing its rollback line.

## What a release notes template contains

A release notes template is a fixed outline for one release that puts the upgrade decision before the details. It has seven sections, in this order:

1. **Release summary:** version, date, compatibility, affected users, required action and rollback.
2. **Breaking changes:** one entry per change, each with a migration step, a verification check and a deadline.
3. **Security and support:** advisories, runtime requirements and end-of-support dates.
4. **Fixes:** the corrected behavior and who it affected.
5. **New capabilities:** what is available and how to try it.
6. **Known issues:** symptom, workaround, tracking link and planned fix.
7. **Resources:** migration guide, reference changes and support.

The order follows the structure in [writing release notes developers trust](/articles/writing-release-notes/), which explains why each section sits where it does.

## Copy the template and the checker

The checker needs only Python 3:

- [Release notes template (Markdown)](/static/templates/release-notes-template.md)
- [Checker script](/static/templates/check_release_notes.py)
- [Filled example for an SDK 4.0.0 release](/static/examples/release-notes-sdk-4.0.0.md)

The summary block is the part a reader sees first, so it is plain `Field: value` lines:

```markdown
Version: {{for example, 4.0.0}}
Date: {{YYYY-MM-DD}}
Compatibility: {{Backward compatible | Breaking changes to ...}}
Affected: {{who must act, and who can ignore this release}}
Action: {{the one thing an affected reader must do}}
Rollback: {{when rolling back is safe, and when it stops being safe}}
```

Each field stays, even when the answer is "None". A reader scanning for the rollback line then finds it in the same place on each release, and the checker fails a field that is missing or left empty.

Each breaking change gets its own entry with four fields:

```markdown
### {{Name the changed behavior}}

What changed: {{old behavior, new behavior}}
Migration: {{the step, in dependency order with the other steps}}
Verify: {{an observable check that the migration worked}}
Deadline: {{YYYY-MM-DD, or "None"}}
```

I made Verify required so readers can test the migration, and the checker rejects a vague deadline such as "end of September" because a reader cannot put it on a calendar.

## Fill it in for a breaking SDK release

The filled example uses the hypothetical SDK 4.0.0 release from the [changelog guide](/articles/writing-changelogs/), which moves list endpoints from page numbers to cursors and drops Node.js 18. Its summary reads:

```markdown
Version: 4.0.0
Date: 2026-07-30
Compatibility: Breaking changes to pagination and Node.js support
Affected: JavaScript SDK users and REST integrations that send `page`. Python SDK users can ignore this release.
Action: Upgrade to Node.js 20, then migrate list calls from `page` to cursors
Rollback: Safe until the application stores its first v4 cursor; after that, contact support before downgrading
```

The Affected line names who can ignore the release as well as who must act. That lets an unaffected reader stop after one line.

The pagination change then fills the four fields with things a developer can run:

```markdown
### List endpoints use cursors instead of page numbers

What changed: `list()` no longer accepts `page`. It returns `nextCursor`, which you pass back as `cursor`.
Migration: Replace `page: n` with the `cursor` returned by the previous call, starting from no cursor.
Verify: A full pagination run returns every record exactly once, and the last page returns `nextCursor: null`.
Deadline: 2026-09-30
```

## Check a release note before it ships

Run the checker on the finished note. It checks the summary block and each `###` entry, and `--filled` also fails on any `{{placeholder}}` left in the text:

```bash
python3 check_release_notes.py --filled release-notes-sdk-4.0.0.md
```

```text
release-notes-sdk-4.0.0.md: PASS
  summary fields: 6/6
  breaking changes checked: 2
  unfilled placeholders: 0
```

Now copy the example to `broken.md`, delete its `Rollback:` line and change the first deadline to "end of September", then check the copy:

```text
broken.md: FAIL (2 problem(s))
  - summary is missing 'Rollback:'
  - breaking change 'List endpoints use cursors instead of page numbers' has a Deadline without a calendar date: 'end of September'
```

The failing run exits with status 1, so fix each listed line and rerun until it prints PASS. Without `--filled` the checker accepts placeholders, which is why the blank template passes its own structure check and reports its 27 open placeholders.

## How Kubernetes, Go and Node.js order their release notes

| Project and release | What comes first | Where breaking changes live |
|---|---|---|
| [Kubernetes v1.31.0](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.31.md) | Download links, then "Urgent Upgrade Notes" | The urgent notes, then "Changes by Kind" (Deprecation, API Change, Feature and more) |
| [Go 1.23](https://go.dev/doc/go1.23) | An introduction restating the Go 1 compatibility promise | Sections by area: language, tools, runtime, standard library, ports |
| [Node.js 22.0.0](https://nodejs.org/en/blog/release/v22.0.0) | A highlights paragraph | A "Semver-Major Commits" list |

I'd copy the Kubernetes order, because its must-read section comes before the full list of changes. I'd use the Go and Node.js layouts when readers need to find a particular subsystem or change type.

## Release notes template or changelog template

A changelog keeps every version in one running file, and the [changelog guide](/articles/writing-changelogs/) covers that format. Use this template when one release needs its own page: a major version, or any release with a breaking change.

## FAQ

### What should a release notes template include?

It needs seven sections: a release summary, breaking changes, security and support, fixes, new capabilities, known issues and resources. The summary carries the upgrade decision, including who must act and when rollback stops being safe.

### Should a patch release use the full template?

Keep the summary block and delete the sections that would be empty. A patch with one fix still needs Compatibility and Rollback, because those are the lines a reader checks before upgrading.

### How is a release notes template different from a changelog template?

A changelog template formats a running history of versions, with a short entry for each. A release notes template covers one release in depth, with the migration steps, verification and rollback for that version.

### Can the checker run in CI?

Yes, it exits with status 1 on any problem. A CI step such as `python3 check_release_notes.py --filled docs/releases/4.0.0.md` blocks a merge until the note passes.
