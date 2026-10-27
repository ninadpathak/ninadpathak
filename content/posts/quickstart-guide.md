---
category: technical-documentation
date: 2026-10-22
description: A quick start guide template for developer products, with a filled example against the GitHub REST API and a checklist to run before you publish.
slug: quickstart-guide
status: published
takeaways:
- A quick start guide gets one reader to one working result by the shortest supported path.
- Put tool versions and access first, then show the exact output the reader should see.
- Run every command in a fresh directory before publishing, and compare the output with the page.
title: 'Quick Start Guide Template: Write a Quickstart Developers Can Run'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer products, starting with the quickstart that takes a new reader to a first working request.'
video: quickstart-guide
---

GitHub's [REST API quickstart](https://docs.github.com/en/rest/quickstart) offers paths for GitHub CLI, `curl` and JavaScript, and its CLI path starts by installing the CLI and signing in. I've kept the example on this page to one public request that needs no account, with the requirements listed before the first command.

I put requirements before the first command and the expected output beside the command that produces it. A reader can then tell within one step whether they are on track, and you can check the page the same way before it ships.

## What a quick start guide is

A quick start guide takes one reader from nothing to one working result by the shortest supported path. For a developer product that result is a first successful request, build or deploy, and each section of the template serves that one result:

1. **A title that names the result**, like "Get a repository's details from the GitHub REST API".
2. **Before you start:** each tool with its minimum version and the command that checks it, plus any account or key and where to get it.
3. **Steps:** one outcome per step, each with the command in a code block.
4. **See it work:** the exact output that proves success.
5. **If it fails:** the errors a reader is likely to hit next, each with its cause and fix.
6. **Next steps:** the task after first success and the reference for what they used.

## Copy the template

Both files are plain Markdown:

- [Quick start guide template (Markdown)](/static/templates/quickstart-template.md)
- [Filled example for the GitHub REST API](/static/examples/github-rest-quickstart.md)

The template keeps each command in its own code block and puts the expected result in a separate block right after it. A reader can copy a command without copying its output, and you can compare the two when you test the page.

## A filled example: the GitHub REST API

The example needs no account, because GitHub allows unauthenticated requests at [60 requests per hour per IP address](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api). Its first step requests one repository and saves the response:

```bash
curl -sS --fail-with-body \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/kubernetes/kubernetes \
  -o repo.json
```

The second step pulls out the fields the reader came for, and the page shows the output they should get:

```bash
jq -r '.full_name, .default_branch, .license.spdx_id' repo.json
```

```text
kubernetes/kubernetes
master
Apache-2.0
```

The `--fail-with-body` flag makes curl exit with an error on the failed request, and it needs [curl 7.76.0 or later](https://curl.se/docs/manpage.html#--fail-with-body), which the example's "Before you start" list names. Without it, curl exits 0 on a 404 and saves the error body, and jq then prints `null` for each field without failing.

The example's "If it fails" table covers three errors, starting with the one a typo produces:

| What you see | Why | Fix |
|---|---|---|
| `curl: (22) The requested URL returned error: 404` | The owner or repository name is misspelled, or the repository is private | Check the URL path, and use a token for private repositories |
| A `403` or `429` status, with `x-ratelimit-remaining: 0` | The 60 unauthenticated requests for this hour are used up | Wait until the time in `x-ratelimit-reset`, or send a token |
| `jq: command not found` | jq is not installed | Install jq, or read the fields from `repo.json` |

The first row came from running the page with the repository name misspelled. The second comes from [GitHub's rate-limit documentation](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), which lists the `x-ratelimit-*` headers and the two status codes.

## Time-to-first-success checklist

Run these checks on a finished quickstart, in a new directory and a fresh terminal. Each one names what to fix when it fails:

1. **Every command works in order from an empty directory.** If one fails, find out why first: a missing file or login needs a new step, while a wrong URL or flag needs the command fixed.
2. **Each tool in "Before you start" has a version check.** If one is missing, a reader on an old version fails in Step 1 with nothing pointing at the cause.
3. **"See it work" matches a fresh run.** If your output differs, replace the block with the output you got.
4. **"If it fails" covers the error from a misspelled input.** Misspell the resource name, run the page, and add a row for the error you get if it is missing.
5. **No step needs a value the page never explains.** If a step needs a token or an ID, "Before you start" has to say where the reader gets it.

## Quickstart, tutorial or onboarding doc

A quickstart ends at one working result. A [technical tutorial](/articles/writing-technical-tutorials/) teaches a concept through a longer build, and [developer onboarding docs](/articles/developer-onboarding-docs/) get a new team member to a merged change in your own codebase.

## FAQ

### What should a quick start guide include?

It needs a title naming the result, a "Before you start" list with version checks, steps with one outcome each, and the exact expected output. Add an "If it fails" table for the likely errors and a short list of next steps.

### How long should a quickstart take?

Time a reader who hasn't seen the page before, on a clean machine, from opening the page to seeing the expected output. Put a number in the title only after that run.

### What is the difference between a quickstart and a tutorial?

A quickstart gets one reader to one working result by the shortest path and stops. A tutorial teaches a concept, so it can take longer and explain each choice along the way.
