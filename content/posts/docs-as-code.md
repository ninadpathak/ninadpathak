---
category: technical-documentation
primary_query: docs as code
siblings:
- documentation-review
- code-documentation
- docs-seo
date: 2026-11-23
description: "Docs as code on a small MkDocs repository: the strict build and the link check pass on a stale page, and a script that runs the page's commands fails."
slug: docs-as-code
status: published
takeaways:
- Docs as code keeps documentation as plain-text files in Git, where each change gets a pull request and a CI run before it publishes.
- All four pipeline checks, the strict MkDocs build among them, passed on a usage page whose command had started printing its rows in a different order.
- A 119-line script that runs each command in a page's console blocks failed on that page and passed once two lines of it were fixed.
title: "Docs as Code: A Working Example and What a Green Build Misses"
work_note: "If your docs live in a repository, I can write in it and send each quickstart or reference page as a pull request your engineers review. I'm Ninad Pathak, a freelance technical writer, and I run every command on a page before I send it. [Ask me about your docs](/services/developer-documentation/)."
---

Docs as code means you keep documentation as plain-text files in Git and change it the way you change code. Each docs change goes through a pull request, and a CI job checks the pages before another job publishes them.

The test of what those checks prove ran on November 23, 2026, in a small docs-as-code repository built for it. The order its command-line tool prints rows in was changed and the docs were left alone, and every check in the pipeline, the strict MkDocs build included, passed on the stale page.

A 119-line script that runs the commands printed on the page did fail, and it named the wrong row. I'll walk you through the workflow's parts and then that repository, a small working setup for [technical documentation](/articles/technical-documentation/).

## What is docs as code?

Docs as code, also written documentation as code, is a way of working in which a team writes and ships its documentation with the tools it already uses for source code. The [Write the Docs guide](https://www.writethedocs.org/guide/docs-as-code/), credited to Eric Holscher and the Write the Docs community, calls it "a philosophy that you should be writing documentation with the same tools as code" and lists five of them:

- Issue trackers
- Version control (Git)
- Plain-text markup (Markdown, reStructuredText, Asciidoc)
- Code reviews
- Automated tests

I read that guide on November 23, 2026, and its list ends at the words "Automated Tests" without naming one.

## The parts of a docs-as-code workflow

A docs-as-code workflow has five parts, from the Git repository the pages live in to the job that publishes them. The last column is what this page's example uses:

| Part | What it means | In the example |
|---|---|---|
| Version control | The pages live in Git, so each change has an author and a diff | `docs/` sits beside the tool's code |
| Plain-text format | A diff can show a page line by line | Two Markdown pages |
| Review | A docs change is a pull request that someone approves | None opened, because the repository has no remote host |
| Automated checks | A CI job runs commands that fail on a broken page | The five commands below |
| Automated publish | A merge to the main branch rebuilds and deploys the site | `mkdocs gh-deploy` |

I put the docs beside the code, following the rule in my guide to [code documentation](/articles/code-documentation/) that each fact sits next to the code whose change would make it wrong.

## A docs-as-code example repository

The example repository holds `statuscount`, a 44-line Python tool I wrote for this page, and a two-page MkDocs site that documents it. The tool counts the HTTP status codes in a web server's access log, and a 12-request sample log ships with it so every documented command has a known answer.

- [The whole repository as a zip](/static/examples/docs-as-code.zip), 19 files
- [The README](/static/examples/docs-as-code/README.md), with the setup and every check
- [The usage page](/static/examples/docs-as-code/docs/usage.md) and [the example check](/static/examples/docs-as-code/scripts/check_examples.py)

The usage page puts each command and its output in one fenced block tagged `console`, the way a terminal shows them. Its first example looked like this in the first commit:

```text
$ python3 statuscount.py examples/access.log
200  6
301  1
404  3
500  2
```

The sentence under that block said the rows come "lowest code first".

## The automated checks and the tools that run them

The pipeline starts with four automated checks, each one command that exits non-zero when it fails:

| Check | Tool | A pass tells you |
|---|---|---|
| `python -m unittest discover -s tests` | Python 3.12.3 | The tool's functions return what its 5 tests expect |
| `mkdocs build --strict` | MkDocs 1.6.1 | Each page renders, and each link between pages points at a page and a heading that exist |
| `lychee --root-dir "$PWD/site" site` | lychee 0.24.2 | Each link in the built HTML resolves, links to other websites included |
| `vale docs` | Vale 3.28.1 | No page breaks my one house rule or Vale's built-in rules |

The MkDocs [command-line reference](https://www.mkdocs.org/user-guide/cli/) says `--strict` will "abort the build on any warnings", and I turned on the four `validation` settings its [configuration page](https://www.mkdocs.org/user-guide/configuration/#validation) recommends for "maximal strictness".

All four passed on the first commit:

```text
$ python -m unittest discover -s tests
.....
----------------------------------------------------------------------
Ran 5 tests in 0.001s

OK
$ mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /tmp/np-work/docs-as-code/statuscount/site
INFO    -  Documentation built in 0.12 seconds
$ lychee --root-dir "$PWD/site" site
🔍 54 Total (in 305ms) 🔗 25 Unique ✅ 54 OK 🚫 0 Errors

$ vale docs
✔ 0 errors, 0 warnings and 0 suggestions in 2 files.
```

[Mintlify's guide](https://www.mintlify.com/library/what-is-docs-as-code), updated November 5, 2026, says a basic CI setup "confirms that the documentation site still builds and that internal links point to real pages". It leaves "incorrect examples" to technical reviewers.

[GitBook's guide](https://www.gitbook.com/blog/what-is-docs-as-code) from September 17, 2023 is the third guide I read for this search, and none of them describes an automated check that runs a page's command.

## What a passing docs build misses

A passing docs build misses a page whose command no longer prints what the page says. To get one, I changed `statuscount` to print the row with the highest count first, and I updated the unit test for the order in the same commit:

```diff
-    return sorted(counts.items())
+    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
```

I left `docs/` alone, so the usage page still showed `301  1` as its second row while the command now printed that row last. And all four checks passed again with exit status 0.

## A check that runs the examples on the page

The check that caught the stale page is `scripts/check_examples.py`, which finds each `console` block in the docs folder and runs every line that starts with `$ ` in bash. Whatever the command prints has to equal the lines under it on the page, and on the stale usage page it didn't, so the script exited with status 1:

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

The fix changed two lines of `docs/usage.md`, the `301  1` row and the sentence that read "lowest code first". The check had reported the row and nothing about the sentence, which I caught by rereading the page around the failing block.

With both lines fixed, the same command passed:

```text
$ python scripts/check_examples.py docs
docs/index.md: 0 run, 0 skipped
docs/usage.md: 3 run, 1 skipped (line 45)
PASS: examples that print what the page shows: 3 of 3
```

## Which changes each check catches

The strict build caught bad links between pages, and lychee caught those plus a mistyped external URL. Only the example check caught a page that disagreed with the tool, as the five changes I made one at a time show:

| The change | Strict build | lychee | Example check |
|---|---|---|---|
| The start page links to a page and a heading that don't exist | Fail | Fail | Pass |
| The Apache URL on the start page is mistyped | Pass | Fail | Pass |
| The output order changes, docs untouched | Pass | Pass | Fail |
| A count is mistyped in the usage page's output, code untouched | Pass | Pass | Fail |
| The counting loop is rewritten with `collections.Counter`, same output | Pass | Pass | Pass |

Vale and the unit tests passed on all five, and for the two bad links lychee read a site built without `--strict`, since the strict build had aborted. The mistyped count is a docs-only mistake, a `3` typed as `2` on the page with nothing wrong in the tool.

The `collections.Counter` rewrite is the case where a green run is correct. It changed how `statuscount.py` counts and nothing a reader can see, so no page owed an update and no check asked for one.

Now compare that with a rule based on file paths, such as "a change to `statuscount.py` must also touch `docs/`". Write the Docs counts it as a benefit of docs as code that you can "block merging of new features" that come without documentation, and a path rule automates that.

The path rule stops the rewrite as well as the order change, because neither patch touches `docs/`. I'd gate merges on the example check, which failed on the one code change a reader would notice.

## A GitHub Actions workflow for the same checks

The workflow at `.github/workflows/docs.yml` runs the five commands on every pull request and on every push to `main`. These are the last five steps of its `check` job, which first checks out the code and installs the tools:

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

Each of those commands ran on my own machine, on Ubuntu 24.04, and I did not run the workflow on GitHub. The YAML has only been checked for syntax, and both actionlint 1.7.12 and PyYAML 6.0.4 accepted it.

A second job, `publish`, runs `mkdocs gh-deploy --force` once `check` has passed on a push to `main`. That command ran against a bare Git repository on my disk, where it pushed the built site to a new `gh-pages` branch, and I haven't watched GitHub Pages serve it.

## How to start with docs as code

Start with one page and the strict build, then add a check when a mistake gets past the ones you have. I'd go in this order:

1. Put the pages in the code's repository as Markdown, where `mkdocs new .` writes a starter `mkdocs.yml` and `docs/index.md`.
2. Run `mkdocs build --strict` locally with the four `validation` settings from the example's `mkdocs.yml`.
3. Run the build and a link check in CI on every pull request.
4. Write your pages' commands as `console` blocks and add the example check to that job.
5. Publish from the main branch only after the checks pass.

## What docs as code doesn't give you

Docs as code doesn't tell you whether an instruction is still true. A green build says the pages render and the links resolve, and the example check extends that only to the commands you wrote as `console` blocks.

Executable examples also have costs, and each one showed up in this repository:

| Cost | Where it showed up |
|---|---|
| The check compares output rows and reads no sentences | The usage page says a missing file makes the tool exit "with status 2", and nothing compares that number |
| Each change to the tool's output needs a docs edit | The check kept failing until I changed two lines of `docs/usage.md` |
| Some commands can't run in CI | The example that reads `/var/log/nginx/access.log` has a skip marker, and each run prints `1 skipped (line 45)` |
| The commands run as your user, with no sandbox | CI will execute a docs page, so it needs the same review as code |

A person still has to run the instructions no script can, such as a click path through a dashboard. My [documentation review checklist](/articles/documentation-review/) puts that run ahead of any edit to the prose.

The [README template](/articles/readme-template/) I published the same day applies the idea to one file, with a checker that runs the commands a README shows. And a green pipeline says nothing about whether a search engine can read the page, which is what the audit script in my [SEO checklist for documentation sites](/articles/docs-seo/) looks at.

## FAQ

These answers use the example repository from this page.

### What tools do you need for docs as code?

You need Git and a static site generator for the plain-text pages, plus a CI service to run the checks. The example here uses MkDocs with lychee and Vale, and a GitHub Actions workflow that I validated and did not run.

### Does a passing docs build mean the docs are correct?

No. A strict MkDocs build passed here on a page whose command printed its rows in a different order, and only a check that ran the command failed.

### Do the docs have to live in the same repository as the code?

No, and GitBook's guide says you can keep them "in a dedicated repo, or store it alongside your code". Keeping them together lets one commit change the code and its page, and it lets CI run the documented commands against that commit's code.
