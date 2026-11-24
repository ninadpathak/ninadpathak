# mdoutline

mdoutline prints the heading outline of a Markdown file, with the line number of each heading.

<!-- Written from https://ninadpathak.com/static/templates/readme-template.md
     Checked with: python3 check_readme.py --filled --run README.md -->

## Install

Requires: Python 3.9 or later, with the `venv` module

Run these from the project folder:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

## Usage

```bash
mdoutline --max-level 2 examples/guide.md
```

```text
   1  Export service guide
   5    Before you start
  14    Send a request
  24    Troubleshooting
```

Each line is a heading's line number and its text, indented two spaces per level. A `#` line inside a fenced code block is skipped, so the shell comment on line 10 of `examples/guide.md` is not in the outline. Run `mdoutline --help` for the options.

## Tests

```bash
python -m unittest discover -s tests
```

```text
OK
```

## Help and contributing

Report a problem by [opening an issue](https://github.com/ninadpathak/ninadpathak/issues) with the command you ran and everything it printed.

To propose a change, add a test for it in `tests/test_mdoutline.py` and open a pull request against `static/examples/readme-example/` in the same repository.

## License

MIT. See [LICENSE](LICENSE).
