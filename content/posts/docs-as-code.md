---
category: technical-documentation
primary_query: docs as code
siblings:
- documentation-review
- code-documentation
- docs-seo
date: 2026-11-23
description: "A green docs build missed a stale command example. Use this sample Git repository to build, review, and test documentation alongside the code."
slug: docs-as-code
status: published
takeaways:
- "Keep the docs in Git and review their changes alongside the software."
- "The example site built successfully with old command output still on the page."
- "A separate check ran the command as written and pointed out the row that had moved."
title: "Docs as Code: A Working Example and What a Green Build Misses"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write your docs as pull requests in your own repository. [Ask me about your docs](/services/developer-documentation/)."
---

I changed the order a command printed its rows, updated the unit test, and left the docs alone. The docs build went green with the old output still on the page.

That's what I wanted this small docs-as-code repo to show. Keeping the docs beside the code gets both into the same review.

To catch a change like mine, you also need CI to run the command the reader will copy.

## What docs as code looks like in a repository

A docs-as-code project keeps its [technical documentation](/articles/technical-documentation/) in the same workflow as the software it describes.

Write the pages in Markdown and put them next to the code they describe. Open a pull request when either changes.

CI builds the pages and runs checks before you publish. [Write the Docs guide](https://www.writethedocs.org/guide/docs-as-code/)

| Part | What it means | In the example |
|---|---|---|
| Version control | The pages live in Git, so each change has an author and a diff | `docs/` sits beside the tool's code |
| Plain-text format | A diff can show a page line by line | Two Markdown pages |
| Review | A docs change is a pull request that someone approves | None opened, because the repository has no remote host |
| Automated checks | A CI job runs commands that fail on a broken page | The five commands below |
| Automated publish | A merge to the main branch rebuilds and deploys the site | `mkdocs gh-deploy` |

The example tool, `statuscount`, counts HTTP status codes from an access log. It ships with a sample log, so someone following the docs can compare what they see with the page.

- [The whole repository as a zip](/static/examples/docs-as-code.zip), 19 files
- [The README](/static/examples/docs-as-code/README.md), with the setup and every check
- [The usage page](/static/examples/docs-as-code/docs/usage.md) and [the example check](/static/examples/docs-as-code/scripts/check_examples.py)

The usage page puts the command and its output together in a `console` block.

```text
$ python3 statuscount.py examples/access.log
200  6
301  1
404  3
500  2
```

## Why the build stayed green

I changed the sort from status code to request count and updated the unit test to expect the new order.

```diff
-    return sorted(counts.items())
+    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
```

In the docs, `301  1` was still the second result. The command now printed it last.

The build could render the page, the links still resolved, and the unit tests agreed with the code. Each check passed because each had a different job.

| Check | Tool | A pass tells you |
|---|---|---|
| `python -m unittest discover -s tests` | Python 3.12.3 | The tool's functions return what its 5 tests expect |
| `mkdocs build --strict` | MkDocs 1.6.1 | Each page renders, and each link between pages points at a page and a heading that exist |
| `lychee --root-dir "$PWD/site" site` | lychee 0.24.2 | Each link in the built HTML resolves, links to other websites included |
| `vale docs` | Vale 3.28.1 | No page breaks my one house rule or Vale's built-in rules |

## Make CI run the example from the page

I’d put the example beside the code whose next change might break it. [Where code documentation belongs](/articles/code-documentation/)

The example checker scans Markdown for `console` blocks. It runs the lines prefixed with `$ ` in Bash and compares stdout with the lines underneath.

Use it on docs and commands you trust.

```text
$ python scripts/check_examples.py docs
docs/index.md: 0 run, 0 skipped
docs/usage.md:10: the command does not print what the page shows
  $ python3 statuscount.py examples/access.log
  --- the page
  +++ the command
  @@ -1,4 +1,4 @@
   200  6
  -301  1
   404  3
   500  2
  +301  1
docs/usage.md: 3 run, 1 skipped (line 45)
FAIL: examples that differ from the page: 1 of 3
```

The checker pointed out the misplaced row. The sentence below it still said “lowest code first,” so I changed that too.

With both edits the checker passed.

```text
$ python scripts/check_examples.py docs
docs/index.md: 0 run, 0 skipped
docs/usage.md: 3 run, 1 skipped (line 45)
PASS: examples that print what the page shows: 3 of 3
```

I tried other changes against the same checks to see which ones earned their place.

| The change | Strict build | lychee | Example check |
|---|---|---|---|
| The start page links to a page and a heading that don't exist | Fail | Fail | Pass |
| The Apache URL on the start page is mistyped | Pass | Fail | Pass |
| The output order changes, docs untouched | Pass | Pass | Fail |
| A count is mistyped in the usage page's output, code untouched | Pass | Pass | Fail |
| The counting loop is rewritten with `collections.Counter`, same output | Pass | Pass | Pass |

For the broken links, lychee read a site built without `--strict` because the strict build had stopped. When the tool changed how it counted internally, the checks stayed green and the docs were still right.

## Put the checks on the pull request

The sample GitHub Actions workflow runs the tests, build, and docs checks. Its publish job waits for the checks and runs on pushes to `main`.

```yaml
      - name: Unit tests
        run: python -m unittest discover -s tests
      - name: Strict build
        run: mkdocs build --strict
      - name: Link check
        run: lychee --root-dir "$PWD/site" site
      - name: Prose lint
        run: vale docs
      - name: Example check
        run: python scripts/check_examples.py docs
```

The commands ran locally on Ubuntu 24.04, and the workflow passed actionlint. The GitHub-hosted workflow itself was outside the test.

I'd start with one page. Put its first command and expected output together, then run the example check before merging a change to either.

For steps you can't automate, like a click path through a dashboard, give a reviewer a clean starting point and ask them to follow the page as written. [README template with a command checker](/articles/readme-template/)

Before release, I’d still have a person follow the instructions and check that the published pages can be found. [Documentation review checklist](/articles/documentation-review/) · [Checking how docs are indexed](/articles/docs-seo/)
