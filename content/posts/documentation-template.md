---
category: technical-documentation
primary_query: technical documentation template
siblings:
- documentation-types
- quickstart-guide
- api-documentation
date: 2026-08-01
description: A technical documentation template you can download, with a blank MkDocs
  starter and a filled example for a small export service. What each page has to show,
  with the commands that test it.
slug: documentation-template
status: published
work_note: "This post is a starting structure for product docs, for the team looking at an empty docs folder with a launch coming. If you'd rather have someone fill that structure with pages that were run against the product, that's what I do. I'm Ninad Pathak, a freelance technical writer for AI and developer-tool companies. [Work with me on them](/services/)."
takeaways:
- Give each page in the template one reader job and the evidence that job needs.
- Start with one tested reader task, then add reference and troubleshooting pages as
  the product needs them.
- Run the link validator and a strict build before you publish the site.
title: A Technical Documentation Template With a Filled Example
updated: 2026-09-10
---

A page of [lorem ipsum](https://en.wikipedia.org/wiki/Lorem_ipsum) looks finished from across the room. A technical documentation template has the same problem: it gives you a getting-started page, a reference section and a troubleshooting page in seconds, and every one of them is still empty.

So the technical documentation template on this page comes in two parts. You get a blank starter to copy, and a filled example for a small export service, so you can see what each heading looks like once a real command and a real response are under it.

I think a template is only useful if it makes the writer show how the product behaves. Each page in this one has a job, and I've listed the evidence that job needs, as part of my pages on [technical documentation](/articles/technical-documentation/).

## What is in the technical documentation template?

The template has five pages, and you can download it blank or read it filled in:

- [Download the blank technical documentation template](/static/templates/technical-documentation-template.zip).
- [Download the filled writing lab and runnable fixture](/static/examples/writing-lab.zip).
- [Read the filled documentation index](/static/examples/writing-lab/docs/index.md).

The blank starter is a MkDocs site with a script that validates its links. The writing lab is a separate set of Markdown pages about a local export service, and it comes with that service so you can run every command in the docs.

| Page job | Filled example | Evidence the page must supply |
| --- | --- | --- |
| Choose where to begin | `docs/index.md` | Links from the reader's task to the owning page |
| Reach first success | `docs/getting-started.md` | Startup commands and an observable response |
| Perform a bounded task | `docs/send-a-request.md` | A complete request with its recovery branch |
| Look up a contract | `docs/reference.md` | Input rules and response meanings |
| Recover from a symptom | `docs/troubleshooting.md` | A diagnostic check and a justified next action |

If a page in your copy has no reader job yet, delete it until a task needs it. An empty "Concepts" section tells readers that an explanation exists when nobody has written one.

When you later need a tutorial or an explanation page, the [documentation types guide](/articles/documentation-types/) covers where each one goes.

## How do you fill in the getting-started page?

Fill the getting-started page with commands you have run and the response the reader should see. The filled example tells the reader to extract the archive and run these three commands from the `writing-lab` folder:

```bash
node --version
node check.mjs
node service.mjs
```

The check prints `PASS` on its last line. The third command starts the export service, which prints a loopback URL and keeps running.

Open a second terminal, set `LAB_URL` to the URL the service printed, then send the two requests:

```bash
export LAB_URL=http://127.0.0.1:49152
curl --fail-with-body "$LAB_URL/health"
curl -i "$LAB_URL/exports" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: report-a' \
  --data '{"format":"csv"}'
```

On a freshly started service the export request returns HTTP 202 with `{"id":"exp_1","format":"csv","status":"accepted"}`. The page then has to say what "accepted" means, which for this fixture is that a record now exists in the service's memory.

If the health request fails, compare your `LAB_URL` with the URL in the first terminal before going further. Leave the service running, because the troubleshooting section below uses it.

For a quickstart page on its own, the [quick start guide template](/articles/quickstart-guide/) adds a version check for each tool and a table of the errors a first run produces.

## What belongs on the reference page?

The reference page holds the exact rules that the getting-started page skipped. The quickstart can use `csv` for its first request, and the reference page has to say that `json` is also allowed and that `xml` is refused.

| Reference field | Filled value | Check |
| --- | --- | --- |
| Format | `csv` or `json`, required | `xml` returns HTTP 400 |
| Request key | Required; 1 to 64 ASCII letters, digits, or hyphens | Missing key returns HTTP 400 |
| Body size | Limit: 4096 bytes | A valid padded 4096-byte request is accepted; 4097 bytes return HTTP 413 |
| Retention | The lifetime of this server instance | A new instance starts with no stored records |
| Output | An accepted record identifier | The fixture contains no file-generation worker |

Run `node check.mjs` to test every row of that table against the service. If an assertion fails, the row it tests is wrong and needs fixing before the page ships.

The [API documentation guide](/articles/api-documentation/) writes out the full reference entry for this endpoint, with each response and a script that checks them against the service. When your reference is generated from source code, [code documentation](/articles/code-documentation/) covers what stays in comments and what moves into a guide.

For a command-line tool, the same table works with one row per option: the allowed values, and the error the tool prints for a value outside them.

## How do you write the troubleshooting page?

Write the troubleshooting page as a table that tells the reader what to do for each state they might be in. The blank starter includes the page, and you supply the states and actions from your own product.

The filled example makes one failure happen on purpose. The service stores the request below and then closes the connection without sending a response:

```bash
curl -i "$LAB_URL/exports" \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: report-loss' \
  -H 'X-Fixture-Drop-Response: yes' \
  --data '{"format":"csv"}'
```

Use an idempotency key you haven't sent before. Curl prints `Empty reply from server` and exits with code 52.

If you get HTTP 200, the service already holds a record for that key, so pick a new key to see the failure.

| Observed state | Next action | Reason |
| --- | --- | --- |
| Response lost; same instance still running | Repeat with the saved key and format, omitting the fixture failure header | The retained record can be returned with HTTP 200 |
| HTTP 409 | Compare the new format with the original request | The key identifies a different retained payload |
| Process restarted after response loss | Stop the recovery experiment | The fixture cannot recover the previous record |

"Retry failed requests" is an instruction that reads well in a review and causes duplicates in production. The [filled request guide](/static/examples/writing-lab/docs/send-a-request.md) has the exact retry command, and the [troubleshooting page](/static/examples/writing-lab/docs/troubleshooting.md) says when to stop retrying.

A run of the lost-response request and the retry on November 18, 2026, with Node.js 24.22.3, matched the table. The retry with the same key and format returned HTTP 200, and the retry with the format changed to `json` returned HTTP 409.

The [recorded fixture checks](/static/examples/writing-lab/validation.txt) are from September 10, 2026 on Node.js 24.18.0. I haven't tested these pages with outside readers.

> Reader check: pick an action for each row of the table using only the filled pages, then find the sentence that supports it. If you need information from outside the pages to choose, write down what was missing.

When you're done, press Ctrl-C in the service's terminal. Stopping the service erases its stored records.

## How do you check the template before publishing?

Check the site's structure and the product's behavior separately, because a site can build cleanly while its commands are wrong. For structure, run the starter's validator and a strict MkDocs build from a fresh Python environment:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/validate_docs.py
mkdocs build --strict
```

On my run, with MkDocs 1.6.1, the validator printed a `PASS` line for each of its checks across five pages, and the strict build finished without a warning. If the install or the validator fails for you, fix that before publishing the generated site.

Those five commands never send a request to your product. The behavior test in the filled example is `node check.mjs`, and it doesn't test the starter's publishing setup.

| Change | Page to review | Evidence to repeat |
| --- | --- | --- |
| Startup command changes | Getting started | Clean-directory startup and health request |
| Input limit changes | Reference | Accepted boundary and rejected adjacent value |
| Storage lifetime changes | Reference and troubleshooting | Recovery before and after restart |
| A link target moves | Index and referring pages | Link validation and rendered navigation |

When one of those changes reaches users, release notes built on the [release notes template](/articles/release-notes-template/) tell them what to do about it. The [documentation review checklist](/articles/documentation-review/) adds the reader-facing checks.

I'd also give each filled page a named owner, and keep the product change that triggers its review next to that name.

## FAQ

**What should a technical documentation template include?**

A technical documentation template should include an index, a getting-started page, a task page, a reference page and a troubleshooting page. Each page needs one reader job and a note of the evidence that job requires.

**Is the template free to use?**

Yes. Both downloads on this page are free, and the filled example has no npm dependencies.

**Which tool does the template use?**

The blank starter is a MkDocs site, pinned to MkDocs 1.6.1 in its `requirements.txt`. The pages are plain Markdown, so you can move them to another static site generator.

**Can I use the template for an internal tool?**

Yes. The page jobs are the same for an internal tool, and the reference table works for a command-line option as well as for an API field.
