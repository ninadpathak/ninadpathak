---
category: technical-documentation
primary_query: none
siblings:
- documentation-review
- writing-technical-tutorials
- agents-on-call-runbooks
bridges:
- slug: mcp-server-tutorial
  reason: The search test in this essay runs on the docs search server that tutorial builds.
- slug: vercel-agent-study-by-harness
  reason: The study tests what a fetch client can read from a public page.
date: 2026-11-23
description: "A search test found my new how-to even after I replaced its working command with a wrong one. Jon Udell’s XMLUI example shows what else to test."
slug: docs-bug-when-agent-gets-stuck
status: published
title: "The search found my how-to. The command was wrong."
work_note: "I'm Ninad Pathak, a freelance technical writer, and I can help you write docs that both developers and coding agents can follow. [Talk to me](/services/developer-documentation/)."
---

I took `--bare` out of a how-to for creating a Python project with only a `pyproject.toml`. The docs search still returned the page first.

The command now created five extra files and directories.

I was trying Jon Udell's idea of filing a docs bug when a coding agent gets stuck. I'd keep his test for whether the agent can find the fixed page.

I'd run the example on the page before closing the bug.

## Start with the query the agent actually ran

A failed search gives the team a specific [technical documentation](/articles/technical-documentation/) bug to reproduce.

Udell wanted Claude to replace a select widget with a set of radio buttons in Bram, his XMLUI desktop app. Claude got there using the component's reference page after the docs search failed to find a worked example.

[Udell’s account in InfoWorld](https://www.infoworld.com/article/4211198/when-an-ai-agent-goes-off-the-rails-file-a-bug-to-fix-the-documentation-then-test-the-fix.html)

The search server had logged what Claude typed and which pages came back. Udell replayed the query against the old docs and against the version with the new how-to.

The old results topped out around 0.7. The new page came back first at 4.2.

I'd attach that query to the bug report. Whoever fixes it can make the same request and see whether the right page comes back.

## A search can find the wrong instructions

For my test I used the server from my [MCP server tutorial](/articles/mcp-server-tutorial/). It returns lines that contain the query.

With MCP Python SDK 2.3.0 and uv 0.13.8, the same request ran against a folder before the how-to was added, after it was added, and after I changed its command.

```bash
npx -y @modelcontextprotocol/inspector@2.12.0 --cli --method tools/call \
  --tool-name search_docs --tool-arg 'query=only a pyproject.toml' -- uv run server.py
```

| State of the how-to page | `result` the search returned |
|---|---|
| Missing | `[]` |
| Added, telling the reader to run `uv init --bare demo` | `howto/create-a-bare-project.md`, line 1 |
| Edited to say `uv init demo` | `howto/create-a-bare-project.md`, line 1 |

I chose the phrase myself and put it in the heading, so the search test was deliberately simple. It still illustrates what the check measures.

The search can tell me the page is in the results. The last two rows give it no way to tell which page works.

## Run the example on the page

Start from the same clean state a reader gets, then follow the how-to as written. That's the first check in my [technical tutorial guide](/articles/writing-technical-tutorials/).

XMLUI already has a place to do this. At [commit 57bc5f2](https://github.com/xmlui-org/xmlui/tree/57bc5f271cb8d7de0f87ecd92fbb6d7ded2ffdf5/xmlui/tests-e2e/how-to-examples), Playwright tests pulled examples out of 199 of the 219 how-to pages and exercised them in a browser.

The new [RadioGroup how-to](https://github.com/xmlui-org/xmlui/blob/57bc5f271cb8d7de0f87ecd92fbb6d7ded2ffdf5/website/content/docs/pages/howto/present-choices-with-a-radiogroup.md) had no such test.

In a standalone XMLUI 0.14.28 app, the example displayed the choices with Pro selected. Clicking Free changed the text to `Selected plan: free`.

The reset button moved the selection back. I'd add those assertions to Playwright so the next change to RadioGroup has to pass them too.

For the uv page, the equivalent test runs the command in a temporary directory and checks what it created. Run this against a page you control, since it executes the first Bash block it finds.

```python
import re
import subprocess
import sys
import tempfile
from pathlib import Path

page = Path(sys.argv[1]).read_text(encoding="utf-8")
command = re.search(r"```bash\n(.+?)\n```", page, re.S).group(1)
with tempfile.TemporaryDirectory() as parent:
    subprocess.run(command, shell=True, cwd=parent, check=True, capture_output=True)
    created = sorted(path.name for path in (Path(parent) / "demo").iterdir())
print(f"{command} created {created}")
sys.exit(0 if created == ["pyproject.toml"] else 1)
```

With `--bare` missing, the script exited with status 1 and printed the extra entries. Adding the flag back made it pass.

```text
uv init demo created ['.git', '.gitignore', '.python-version', 'README.md', 'pyproject.toml', 'src']
```

## Check how the reader gets to the page

On November 23, a browser showed the RadioGroup how-to, but curl got a 404 and a JavaScript shell with none of the instructions in it. The same happened for nine other how-to URLs.

The RadioGroup reference returned 200 with its text in the HTML.

Udell’s search worked because the server uses a local copy of the docs. If an agent starts from the public URL, it needs to be able to retrieve the example there too.

[XMLUI’s explanation of its MCP server](https://www.xmlui.org/blog/improving-the-xmlui-mcp-server) · [Vercel’s agent fetch study](/articles/vercel-agent-study-by-harness/)

If the bug report says the agent couldn't finish the task, I'd go one step further and repeat the original task in a fresh session. The search replay tells me it could find the page.

Running the example tells me it works. A fresh session lets me watch whether the agent actually uses it.

I'd put the replay and the example result in the [docs review](/articles/documentation-review/). If the original task was an on-call fix, I'd check that the agent can use the procedure and verify recovery on a test system.

[Runbooks for agents on call](/articles/agents-on-call-runbooks/)
