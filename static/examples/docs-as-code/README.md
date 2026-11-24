# statuscount: a docs-as-code example

`statuscount` counts the HTTP status codes in a web server's access log. This repository is a small docs-as-code setup around it: the docs are Markdown in `docs/`, MkDocs builds them, and five checks run on every change.

It goes with the article at <https://ninadpathak.com/articles/docs-as-code/>, which shows the strict build passing on a page that no longer matches the tool.

## Requires

Python 3.9 or later, bash, and for two of the checks the `lychee` and `vale` binaries on your `PATH`. The versions this was run with on November 23, 2026: Python 3.12.3, MkDocs 1.6.1, lychee 0.24.2 and Vale 3.28.1.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run the checks

Run these from the repository root. `.github/workflows/docs.yml` runs the same five commands.

```bash
python -m unittest discover -s tests
mkdocs build --strict
lychee --root-dir "$PWD/site" site
vale docs
python scripts/check_examples.py docs
```

| Check | What a pass tells you |
| --- | --- |
| `python -m unittest discover -s tests` | The functions in `statuscount.py` return what the tests expect |
| `mkdocs build --strict` | Every page renders, and every link between pages points at a page and a heading that exist |
| `lychee --root-dir "$PWD/site" site` | Every link in the built HTML resolves, including links to other websites |
| `vale docs` | No page uses a word the rule in `styles/House/` bans, and the built-in spelling rule found nothing |
| `python scripts/check_examples.py docs` | Every command in a `console` block still prints the output written under it |

## Write an example the check can run

Put the command and its output in one fenced block tagged `console`, with `$ ` in front of the command:

````markdown
```console
$ python3 statuscount.py --min-status 400 examples/access.log
404  3
500  2
```
````

Put `<!-- check_examples: skip -->` on the line above a block that cannot run in CI. The check prints the line number of every block it skipped.

## See the example check fail

The folder `changes/` holds three patches, all already applied to the files here:

| Patch | What it changed | Files |
| --- | --- | --- |
| `1-sort-by-count.patch` | The output order, from lowest status code first to highest count first | `statuscount.py`, `tests/test_statuscount.py` |
| `2-usage-page-fix.patch` | The usage page, to show the new order | `docs/usage.md` |
| `3-counter-refactor.patch` | How the counting is written, with the same output | `statuscount.py` |

Take the docs fix back out, and the page is stale again:

```bash
patch -R -p1 -i changes/2-usage-page-fix.patch
mkdocs build --strict
python scripts/check_examples.py docs
```

The build passes and the example check fails. Put the fix back with `patch -p1 -i changes/2-usage-page-fix.patch`.

## License

MIT. See [LICENSE](LICENSE).
