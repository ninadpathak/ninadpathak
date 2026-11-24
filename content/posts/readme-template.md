---
category: technical-documentation
primary_query: readme template
siblings:
- quickstart-guide
- code-documentation
- documentation-template
date: 2026-11-23
description: "A Markdown README template with a real command and expected output, plus a checker that runs the example in a fresh copy of the repo."
slug: readme-template
status: published
takeaways:
- "Start with one sentence that tells readers what the project does."
- "Show the output right under the first usage command so someone can tell when it worked."
- "Run the README checker in a fresh project copy. It caught the renamed flag that the unit tests never used."
title: "README Template With a Checker That Runs the Commands in It"
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write your README, your quickstart and the docs behind them. [Talk to me](/services/developer-documentation/)."
---

The first command under Usage told people to run `mdoutline --max-level 2`. I renamed the flag to `--depth`, and the unit tests stayed green while the command in the README stopped working.

That's why this README template gives the first command its own line of expected output. The reader can see whether it worked, and a checker can run the same command after the next change.

## Copy the README template

The README is the part of [technical documentation](/articles/technical-documentation/) someone can read before they decide to install anything.

The template, example, and checker are plain text. The checker needs Python 3.9 or later and Bash.

- [README template (Markdown)](/static/templates/readme-template.md)
- [Checker script](/static/templates/check_readme.py)
- [Filled example: the README of mdoutline](/static/examples/readme-example/README.md), or [the whole project as a zip](/static/examples/readme-example.zip)

Start with one sentence that says what the project does. Put the runtime requirements and install command under Install.

Under Usage, put the shortest command that does something real and the output someone should see. Use Tests for the command contributors need and Help for where to ask.

Add a license link so people know what they can do with it. [GitHub’s guide to repository READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)

## What I wanted to see on the first run

In a sample of 20 highly starred software repos, 17 showed an install or build command. Only two showed the output of a usage example.

I picked four repos in each of five languages by stars and skipped repos that were reading lists. That's a sample of popular repos, so I wouldn't turn it into a rule about every README.

[The census and the lines behind each count](/static/examples/readme-census-2026-11-23.csv)

| Part of the README | READMEs that have it, of 20 |
|---|---|
| First line of text says what the project is or does | 14 |
| That line sits above every badge and image | 5 |
| An install or build command | 17 |
| A usage example in a code block | 11 |
| The output of a usage example, shown as text | 2 |
| A command that runs the tests | 4 |
| The license named in text | 16 |
| A contributing section, or a link to a contributing guide | 17 |

My example, `mdoutline`, prints the headings in a Markdown file. I kept the virtual environment setup because a bare `pip install .` failed on the system Python on my Ubuntu 24.04 machine.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

The sample file ships with the project, so you can paste this command without creating any inputs. The output goes directly underneath it.

```bash
mdoutline --max-level 2 examples/guide.md
```

```text
   1  Export service guide
   5    Before you start
  14    Send a request
  24    Troubleshooting
```

## Run the README in a fresh checkout

The checker copies the project to a temporary directory and runs the commands under Install, Usage, and Tests in one Bash session. An environment you activate in Install carries through.

An environment you already had active before the check is left out.

```bash
python3 check_readme.py --filled --run readme-example/README.md
```

```text
README.md: PASS
  sections found: Install, Usage, Tests, Help and contributing, License
  command blocks run: 3 of 3 (Install 1, Usage 1, Tests 1)
  output blocks matched: 2
  unfilled placeholders: 0
```

Without `--run`, the checker reads the Markdown and checks its structure. With `--run`, it gives you the failed command or the output that differed.

Use it on a README whose commands you trust.

## See a failure before a reader does

I renamed `--max-level` to `--depth` in a copy of the tool. The unit tests didn't use that flag, so they passed.

The README checker used it because a reader would.

```text
README.md: FAIL (1 problem(s))
  - Usage: `mdoutline --max-level 2 examples/guide.md` exited with status 2
      usage: mdoutline [-h] [--depth N] [--version] file
      mdoutline: error: unrecognized arguments: --max-level examples/guide.md
  command blocks run: 1 of 3 (Install 1, Usage 0, Tests 0)
  output blocks matched: 0
```

A copied command should have everything it needs. If it needs an account, a credential, or a sequence of setup screens, I'd send the reader to a [quickstart](/articles/quickstart-guide/) and keep the README's first example small.

For commands spread across a full docs site, I'd put the same kind of output check in [the docs build](/articles/docs-as-code/).

I’d give detailed reference material a [docs site of its own](/articles/documentation-template/) and leave code-specific advice close to the code it explains. [Where code documentation belongs](/articles/code-documentation/)
