---
category: technical-documentation
primary_query: readme template
siblings:
- quickstart-guide
- code-documentation
- documentation-template
date: 2026-11-23
description: "A README template in Markdown with a filled example for a small Python CLI and a checker script that runs the install, usage and test commands it shows."
slug: readme-template
status: published
takeaways:
- Open a README with one sentence on what the project does, above every badge, which 5 of the 20 popular READMEs I went through on November 23, 2026 do.
- Put the output under the usage command, because 2 of those 20 READMEs show any and it is the line a script can compare.
- Run check_readme.py with --filled and --run before a release, so a renamed flag or a missing install step fails on your machine first.
title: "README Template With a Checker That Runs the Commands in It"
work_note: "A README covers the install and one command, and a quickstart covers the first real task after that. I'm Ninad Pathak, a freelance technical writer, and I write quickstarts after running the product from a clean machine. [Talk to me about yours](/services/developer-documentation/)."
---

The README template on this page is a Markdown file with one opening sentence and five sections, and every command in it sits in a code block that a script can run. It comes with a filled example for a small Python command-line tool and a checker that runs those commands in a fresh copy of the project.

To decide what belongs in the template, I went through the READMEs of 20 of GitHub's highest-starred repositories on November 23, 2026. An install command appears in 17 of them, and two show what a usage command prints.

So the template puts the output right under the usage command, and the checker fails the README when the command stops printing it. A README is the page of [technical documentation](/articles/technical-documentation/) that a code host shows on a repository's front page.

## What is a README template?

A README template is a fixed outline for the README file at the top of a repository, so each project you publish answers the same questions in the same order. GitHub's page [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes), which I read on November 23, 2026, calls a README "often the first item a visitor will see when visiting your repository."

My template has six parts:

1. **Opening sentence:** what the project does, in 40 words or fewer, above every badge and logo.
2. **Install:** a `Requires:` line with the runtime and its minimum version, then the install commands.
3. **Usage:** the smallest command that shows the project working, and the output it prints.
4. **Tests:** the command that runs the tests, and the line that means they passed.
5. **Help and contributing:** where to report a problem and how to propose a change.
6. **License:** the license name and a link to the license file.

## What GitHub says a README should contain

GitHub's documentation says a README typically covers five things, and my template has a place for each:

| GitHub says a README typically covers | Where it goes in my template |
|---|---|
| "What the project does" | The opening sentence |
| "Why the project is useful" | The Usage example and its output |
| "How users can get started with the project" | Install, then Usage |
| "Where users can get help with your project" | Help and contributing |
| "Who maintains and contributes to the project" | Help and contributing, with no separate list of maintainers |

The three pages I read for this search give you different things:

| Page | What it gives | What it leaves out |
|---|---|---|
| [Make a README](https://www.makeareadme.com/), by Danny Guo | An editable sample with four sections | A tests section |
| [Best-README-Template](https://github.com/othneildrew/Best-README-Template) | `BLANK_README.md`, which opens with six badges and a logo above the project description | A tests section |
| [Awesome README](https://github.com/matiassingers/awesome-readme), by Matias Singers | A list of 101 example READMEs, each with a note on what it does well | A template |

Make a README's advice for Usage is "Use examples liberally, and show the expected output if you can," and its own sample shows return values as comments such as `# returns 'geese'`. A script can't run a comment, so my template gives the output a block of its own, and none of those pages comes with a checker.

## What 20 popular READMEs include

An install or build command is in 17 of the 20 READMEs I went through, and the output of a usage example is in two. I made each call by reading the file's opening lines, headings and code blocks, and the [CSV of the census](/static/examples/readme-census-2026-11-23.csv) holds the line of text I judged for every repository.

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

The repositories came from GitHub's search API, sorted by stars, with the first four that hold software taken in each of five languages. I skipped ten that hold reading material such as lists of links, and the CSV names the languages and all 30 repositories, 20 read and 10 skipped.

Those 20 are a sample, and each has more than 120,000 stars, so the counts describe very popular projects. The two that show output are yt-dlp's, which prints a filename under three of its output-template commands, and React's, which says its sample component will render "Hello Taylor."

## Copy the README template, the example and the checker

All of the files are plain text, and the checker needs Python 3.9 or later and bash:

- [README template (Markdown)](/static/templates/readme-template.md)
- [Checker script](/static/templates/check_readme.py)
- [Filled example: the README of mdoutline](/static/examples/readme-example/README.md), or [the whole project as a zip](/static/examples/readme-example.zip)

Badges and screenshots go under the opening sentence, and commands go in `bash` blocks with no `$` prompt, so a reader can paste them and the checker can run them.

## A filled README example for a Python CLI

The filled example is the README of mdoutline, a 61-line Python tool I wrote for this page that prints the heading outline of a Markdown file. Its Install section opens with a `Requires:` line that names Python 3.9 or later and the `venv` module, and then creates a virtual environment before it calls pip:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

I kept the first two lines because the system Python on my Ubuntu 24.04 machine has no pip, and a bare `pip install .` fails there. The Usage section runs the tool on a sample file that ships in the repository, with the output in a `text` block right after the command:

```bash
mdoutline --max-level 2 examples/guide.md
```

```text
   1  Export service guide
   5    Before you start
  14    Send a request
  24    Troubleshooting
```

The README's commands passed on November 23, 2026 with Python 3.12.3 and pip 24.0 on Ubuntu 24.04. They passed again with Python 3.9.25, the floor its `Requires:` line states.

## Check a README by running its commands

Run the checker with `--filled` and `--run`, and it prints PASS or the list of problems:

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

With `--run`, the script copies the README's folder to a temporary directory, leaving out `.git` and folders of installed or built files such as `node_modules`. It runs the shell blocks under Install first, then Usage and then Tests, in one bash session with `set -e`, so an activated environment carries over and the first failing command stops the run.

The session gets an empty home directory and takes two variables from your shell, `LANG` and a `PATH` with the active virtual environment removed. Without `--run` the script only reads the file, and these are all of its checks:

| Part | The checker fails when |
|---|---|
| Whole file | A code block is opened and never closed |
| Whole file | A link points at a file that isn't in the README's folder (web links, `#anchor` links, images and paths that start with `/` are skipped) |
| Whole file | With `--filled`, a `{{placeholder}}` is left |
| Opening | The first line isn't a `# Title`, or the title line holds a badge or an image |
| Opening | No text sits between the title and the first `##` heading, or that text starts with a badge, an image, HTML, a heading, a quote, a table or a list item |
| Opening | The paragraph under the title runs past 40 words or holds more than one sentence |
| Sections | No `##` heading names Install, Usage, Tests, Help or License (a word such as "Installation", "Example" or "Contributing" also matches) |
| Install, Usage, Tests | The section has no command in a `bash`, `sh` or `shell` block, or a command line starts with a `$` prompt |
| Install | No line starts with `Requires:`, or that line has no version number |
| Usage | No command block is followed by a filled output block (`text`, `txt`, `output`, `plaintext`, `json` or untagged) |
| Help, License | The section has no text, or Help has no link, URL or email address |
| `--run` | The file still has placeholders, or `bash` isn't installed (the commands run only when every check above passes) |
| `--run` | A command exits non-zero, a block ends the shell, or the whole run takes longer than `--timeout` (300 seconds unless you set it) |
| `--run` | A line in an output block is missing from what its command block printed, read in order (spaces at the ends of a line are ignored, and a `...` line stands for output that varies) |

`--run` is not a sandbox. The commands run as your user with network access, so I'd use it on a README I wrote and put anyone else's in a container.

## What the checker prints when a README goes stale

A failed run names the command that exited and prints the last lines it wrote. To see one, I copied the project and renamed the tool's `--max-level` flag to `--depth` in `mdoutline.py`, leaving the README as it was:

```text
README.md: FAIL (1 problem(s))
  - Usage: `mdoutline --max-level 2 examples/guide.md` exited with status 2
      usage: mdoutline [-h] [--depth N] [--version] file
      mdoutline: error: unrecognized arguments: --max-level examples/guide.md
  command blocks run: 1 of 3 (Install 1, Usage 0, Tests 0)
  output blocks matched: 0
```

That run exited with status 1, so a CI job can stop a release on it. The project's four unit tests still passed after the rename, because none of them passes the flag.

I broke two more copies, each with one edit:

| The edit | What the checker printed |
|---|---|
| The install block cut down to `pip install .` | ``Install: `pip install .` exited with status 127``, then `pip: command not found` |
| Two lines added near the top of `examples/guide.md`, with the README untouched | ``Usage: `mdoutline --max-level 2 examples/guide.md` did not print the expected line '5    Before you start'`` |

With a virtual environment active in my own shell, the first row's `pip install .` worked by hand. It failed in the checker because the session drops that environment and the system Python has no pip.

## When the template or the checker doesn't fit

The checker needs a workaround in four situations, and the template stops fitting when a first run needs an account or the product needs reference pages.

| Situation | What to do |
|---|---|
| The usage example is Python or JavaScript code, which the checker doesn't run | Save it as a file such as `examples/hello.py`, and run that file from a `bash` block |
| A block mustn't run, such as the install commands for another platform | Put an HTML comment holding only `check_readme: skip` on the line above it |
| A command needs a secret from your shell, such as an API key | Pass the variable's name with `--env NAME` |
| A tool you installed globally is still on `PATH` | Run the checker in a CI job on a fresh image |

GitHub's page says a README "should only contain information necessary for developers to get started using and contributing to your project." The [quick start guide template](/articles/quickstart-guide/) has a place for the account step, and the [technical documentation template](/articles/documentation-template/) is a docs site with a reference page.

A README inside a subdirectory holds the pitfalls for the code in that directory, and my guide to [code documentation](/articles/code-documentation/) covers which facts go there.

## FAQ

The answers below use "the checker" for `check_readme.py`.

### What should a README include?

A README should open with one sentence on what the project does, then give the install commands and one usage example with its output. Below that go the test command and the license, plus a link for questions.

### Is there a standard README format?

No, and GitHub's docs only describe what READMEs typically include. Make a README says it's "up to the developers what information should be included."

### How do you test a README?

Run every command it shows in a fresh copy of the repository, in order, and compare what the usage command prints with the output on the page. The checker does that with `--run` and exits with status 1 on a failed command or a missing line.
