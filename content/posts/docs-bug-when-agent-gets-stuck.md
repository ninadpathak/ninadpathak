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
date: 2026-11-23
description: "Jon Udell treats a how-to that Claude couldn't find as a docs bug and tests the fix with a search. That kind of test still passed on a page I made wrong. XMLUI's own repository has the test I'd add, for 199 of its 219 how-to pages."
slug: docs-bug-when-agent-gets-stuck
status: published
title: "Jon Udell files a docs bug when an agent gets stuck"
work_note: "A docs page can come back first in a search and still carry a command that fails. I'm Ninad Pathak, a freelance technical writer, and I run every command on a page before your engineers see it. [Talk to me about your developer documentation](/services/developer-documentation/)."
---

On August 26, Jon Udell [wrote in InfoWorld](https://www.infoworld.com/article/4211198/when-an-ai-agent-goes-off-the-rails-file-a-bug-to-fix-the-documentation-then-test-the-fix.html) about a coding session in which Claude had to turn a select widget into a radio group in Bram, Udell's desktop app built with the XMLUI framework. Claude searched XMLUI's how-to pages through the framework's MCP server and found nothing on radio groups, so it worked the conversion out from the RadioGroup reference page.

Udell treated the missing how-to as a bug in the docs and had an agent write the page. The article calls that page "a testable fix", and the test was to have Claude repeat its failed search against the new docs and see the page come back first.

I think filing it as a bug is right, and I think the search test is half of what I'd want before calling a bug in [technical documentation](/articles/technical-documentation/) fixed. So the same kind of test runs below on a small docs folder of my own, and after it comes a look in XMLUI's repository for a test that runs the new how-to's example.

## The failed search is the reproduction

Udell's bug has a reproduction because XMLUI's MCP server logs each query an agent makes and the results the agent saw. Udell asked Claude to find its failed searches in that log, and Claude came back with two queries from 21:12, the first of which had returned how-tos about forms.

I'd copy that step before anything else in the article. You can't rerun a complaint that the docs don't cover radio groups, and you can rerun a logged query against the next version of the docs.

The failed searches had topped out at a relevance score of about 0.7, and with the new page in place the repeated search returned it first at 4.2. Udell can make that comparison because the MCP server can pin the version of the docs it searches, so the old docs and the new docs get the same query.

Udell co-maintains XMLUI and builds Bram, so the article is a maintainer's account of the maintainer's own project. It gives enough detail that I could check parts of that account.

## The search test passed on a page I made wrong

A search test keeps passing when the page it finds gives the wrong command, and I checked that with the docs search server from my [MCP server tutorial](/articles/mcp-server-tutorial/). I reused the tutorial's `server.py` unchanged on November 23, with MCP Python SDK 2.3.0 and uv 0.13.8 on Python 3.13.18.

The server's `search_docs` tool returns the lines that contain the query, which makes it much cruder than XMLUI's scored search. My test folder held two how-to pages that I wrote about uv, one on adding a dependency and one on running a script.

The task with no page was creating a project that has only a `pyproject.toml`. I fixed the query before I wrote the page and ran it through the MCP Inspector:

```bash
npx -y @modelcontextprotocol/inspector@2.12.0 --cli --method tools/call \
  --tool-name search_docs --tool-arg 'query=only a pyproject.toml' -- uv run server.py
```

That command ran once against each of these states of the docs folder:

| State of the how-to page | `result` the search returned |
|---|---|
| Missing | `[]` |
| Added, telling the reader to run `uv init --bare demo` | `howto/create-a-bare-project.md`, line 1 |
| Edited to say `uv init demo` | `howto/create-a-bare-project.md`, line 1 |

The first row is the missing page showing up as a failed search, which the server logged as `search_docs 'only a pyproject.toml' returned 0 matches`. The second row is the fix passing its test.

<!-- evidence-three: the script output further down lists the six entries uv init demo created and the three besides src and README.md and pyproject.toml are .git and .gitignore and .python-version --> But the third row passes as well, and the page is now wrong. With uv 0.13.8, `uv init demo` creates a `src` folder, a `README.md` and three more entries beside `pyproject.toml`.

My test also had a weakness that Udell's doesn't. I chose the query and then wrote a heading that contains it, so I could have made any page pass, and Udell's queries came from a log of what Claude had searched for.

## XMLUI already runs how-to examples in tests

XMLUI's repository already has tests that run a how-to's example in the framework, and Udell's article doesn't mention them. At [commit 57bc5f2](https://github.com/xmlui-org/xmlui/tree/57bc5f271cb8d7de0f87ecd92fbb6d7ded2ffdf5/xmlui/tests-e2e/how-to-examples) from November 19, the folder `xmlui/tests-e2e/how-to-examples` holds 199 Playwright spec files, and each one pulls a named example out of a how-to's Markdown and drives it in a browser.

Udell writes that agents are told to prefer how-to examples "that provide verified working patterns". For 199 of the 219 how-to pages a spec does the verifying, and the [RadioGroup how-to](https://github.com/xmlui-org/xmlui/blob/57bc5f271cb8d7de0f87ecd92fbb6d7ded2ffdf5/website/content/docs/pages/howto/present-choices-with-a-radiogroup.md) from the article is one of the 20 pages that no test reads.

<!-- evidence-three: pull request 3732 shows opened and merged times on August 11 that are three minutes apart --> [Pull request 3732](https://github.com/xmlui-org/xmlui/pull/3732), which added the page, was opened from Udell's account on August 11 and merged three minutes later with no review on record. Its description is signed by Udell's Claude and says the example is grounded in the RadioGroup component's reference examples.

So Claude wrote the how-to from the same reference page it had worked the conversion out from in the session. An agent in that position can write a confident page that's wrong, and a search score of 4.2 can't tell you whether it did.

The example ran on November 23 in a standalone XMLUI 0.14.28 app driven by Playwright 1.65.1 in headless Chromium. The app rendered its radio buttons in one row with Pro selected, as the page says it will.

Clicking Free changed the text below the buttons to `Selected plan: free`, and the Reset to Pro button moved the selection back. Udell's example works, and the evidence for that is a run of the example, which is a step the article doesn't describe.

## The how-to's address returns 404 to a plain fetch

On November 23, curl got HTTP status 404 from the how-to's address, `https://www.xmlui.org/docs/howto/present-choices-with-a-radiogroup`. The body was a JavaScript shell with 22 words of text, and none of them came from the how-to.

A browser builds the page from that shell, so a person sees the how-to. An agent that fetches the address without running JavaScript gets the 404.

The nine other how-to addresses I tried each returned 404 as well, while the RadioGroup reference page returned 200 with its text in the HTML. Udell's search test can't show that, because the MCP server searches a local cache of the docs, as [a February 20 post on XMLUI's blog](https://www.xmlui.org/blog/improving-the-xmlui-mcp-server) describes.

So the search test shows the page is findable by an agent that has XMLUI's MCP server installed.

## What I'd add before closing a docs bug

I'd close a docs bug like Udell's only when two checks pass. The logged query has to return the new page, and a test has to run the page's example against the product.

For XMLUI the second check is one more spec file in `how-to-examples`. For my uv page it's this script, which runs the page's command in an empty temporary folder, the clean start that my [tutorial guide](/articles/writing-technical-tutorials/) asks for:

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

On the edited page the script printed this line and exited with status 1, and it exited with 0 once I put `--bare` back:

```text
uv init demo created ['.git', '.gitignore', '.python-version', 'README.md', 'pyproject.toml', 'src']
```

My [documentation review checklist](/articles/documentation-review/) puts that check first, before anyone edits a sentence. It also refuses a model's explanation as the source for a claim about the product, which is the rule a how-to written by an agent needs.

Neither check shows that an agent given the original task now uses the page. I didn't rerun the select-to-radio conversion in a fresh session, and the article doesn't say that Udell did.

To find missing pages across many apps, Udell proposes mining the MCP logs and the code of real apps for searches that find no working pattern. Both find a page that's missing, and neither finds a wrong page, because a wrong how-to that ranks first is recorded in the MCP log as a hit.

A wrong page would show up only in Udell's third source, the session logs, as an agent that found the how-to and still struggled. Of those logs Udell writes, "I haven't yet gotten agents to reliably surface episodes of struggle."

My [essay on on-call agents](/articles/agents-on-call-runbooks/) asks an agent for the same kind of record, after a runbook test in which the final check passed and the agent had cancelled the wrong queries. Until session logs can be searched for that kind of failure, a test that runs the page's example is the check that catches a wrong how-to before an agent copies it.

For the RadioGroup page that test is one spec file with the checks made by hand in the November 23 run. It would give XMLUI 200 tested how-tos out of 219.
