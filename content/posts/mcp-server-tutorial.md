---
category: ai-engineering
date: 2026-10-22
description: 'Build an MCP server in Python, test it without a model, and see how numbering a tool''s output changed whether Claude cited the right line in a test run.'
slug: mcp-server-tutorial
status: published
takeaways:
- The MCP Python SDK turns type-hinted functions into tools, and a stdio server must keep its stdout for protocol messages.
- Resolve every path a tool receives before checking it against the folder it may read, because relative segments and symlinks both arrive as plain strings.
- Return what the model has to cite, because Claude cited the right line in every run once the tool numbered its lines.
title: 'MCP Server Tutorial: Build a Docs Search Server in Python'
work_note: '[Ninad Pathak](/portfolio/) wrote Firecrawl''s technical guides to its MCP server in Cursor and in ChatGPT. The server here is smaller on purpose, because it exists to test which tool decisions change what a model does with the output.'
---

A tool's return value is part of its interface to the model, and its format decides what the model can do with the result. Tested with Claude Code 2.1.308 on Haiku 5.5, a `read_doc` tool that returned plain text led to the right line citation in one run of four, and the same tool returning numbered lines led to it in four of four.

The docs-search server below makes that change, plus two decisions about refusals: it resolves every path before checking it against the one folder it may read, and it refuses with an error the model can read. Every command ran from a clean directory on 2026-10-22, with MCP Python SDK 2.3.0 and MCP Inspector 2.12.0, and the `server.py` and `test_server.py` shown here are the files that ran.

## How to set up an MCP server project in Python

Create a bare uv project on Python 3.10 or later and add the [Model Context Protocol](/articles/model-context-protocol/) SDK. I've pinned the SDK to 2.3.0, because version 2 renamed the server class to `MCPServer`, and code written against the 1.x `FastMCP` import won't run on it:

```bash
uv init --bare docs-search --python 3.12
cd docs-search
uv add "mcp[cli]==2.3.0"
```

With uv 0.12.7, a plain `uv init docs-search` creates a packaged `src/` layout. `--bare` writes only `pyproject.toml`, which is all a single-file server needs.

Add a small docs folder to search, and a Markdown file outside it that the server must never read. The sentinel ends in `.md` on purpose, so only the folder check can refuse it:

```bash
mkdir -p docs/guides
printf '# Quickstart\n\nInstall the CLI with `npm install -g acme-cli`.\nThen run `acme login` to store an API key.\n\n## Rate limits\n\nThe API allows 100 requests per minute per key.\n' > docs/guides/quickstart.md
printf '# Errors\n\nA 429 response means you hit the rate limit. Wait and retry.\n' > docs/guides/errors.md
printf '# Private\n\nSECRET=do-not-read\n' > private.md
```

## How to write the server's tools

Each tool is a type-hinted Python function under `@mcp.tool()`, and this server has two read-only ones, `search_docs` and `read_doc`. Save this as `server.py`:

```python
"""An MCP server that searches and reads the Markdown files in one docs folder."""
import logging
import os
from pathlib import Path

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

DOCS_DIR = Path(os.environ.get("DOCS_DIR", "docs")).resolve()
logger = logging.getLogger(__name__)
mcp = MCPServer("docs-search")
READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)


def inside_docs(path: Path) -> bool:
    """True only for a real .md file whose resolved location is inside DOCS_DIR."""
    resolved = path.resolve()
    return resolved.is_relative_to(DOCS_DIR) and resolved.suffix == ".md" and resolved.is_file()


@mcp.tool(annotations=READ_ONLY)
def search_docs(query: str, limit: int = 5) -> list[dict]:
    """Find lines in the docs that contain the query, ignoring case.

    Returns up to `limit` matches (no more than 50), each with the file path relative
    to the docs folder, the line number and the line text.
    """
    needle = query.lower()
    limit = max(1, min(limit, 50))
    matches = []
    for path in sorted(DOCS_DIR.rglob("*.md")):
        if not inside_docs(path):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for number, line in enumerate(lines, start=1):
            if needle in line.lower():
                matches.append({"path": path.relative_to(DOCS_DIR).as_posix(), "line": number, "text": line.strip()})
                if len(matches) == limit:
                    return matches
    logger.info("search_docs %r returned %d matches", query, len(matches))
    return matches


@mcp.tool(annotations=READ_ONLY)
def read_doc(path: str) -> str:
    """Return one Markdown file with each line numbered, given its path relative to the docs folder."""
    target = DOCS_DIR / path
    if not inside_docs(target):
        raise ToolError(f"{path} is not a Markdown file inside the docs folder")
    lines = target.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"{number}: {line}" for number, line in enumerate(lines, start=1))


if __name__ == "__main__":
    mcp.run(transport="stdio")
```

`MCPServer` builds each tool's input schema from the type hints and its description from the docstring, so the docstring is the text the model reads when it decides which tool to call. The [SDK's tools guide](https://py.sdk.modelcontextprotocol.io/servers/tools/) calls the `read_only_hint` annotation a hint, "not security," so the code still has to enforce what the tool may touch.

That docstring does the job a tool registry does inside an [agent harness](/articles/agent-harnesses/), with a protocol in between.

The server never calls `print()`. The [stdio transport spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) says a server "MUST NOT write anything to its `stdout` that is not a valid MCP message," and Python's `logging` writes to stderr, which the spec leaves free for logs.

A refused path raises `ToolError` on purpose. SDK 2.3.0 sends a `ToolError` message to the client as an error result, and it turns any other exception into a generic "Error executing tool" with a crash traceback in the server log.

## How to keep tool arguments inside one folder

Resolve the path first, then check that the resolved location sits under the folder, because a tool's arguments come from the model and arrive as untrusted strings. `inside_docs()` calls `resolve()` before comparing, which collapses `..` segments and follows symlinks, then checks that the real location sits under `DOCS_DIR`.

Checking the raw string would miss both. `guides/../../private.md` contains no suspicious prefix, and a symlink named `leak.md` inside `docs/` looks like any other Markdown file until it's resolved.

## How to test an MCP server without a model

Connect the SDK's `Client` to the server object in memory, then launch the server as a stdio subprocess the way a host does, and run the same checks against both. Save this as `test_server.py`:

```python
"""Checks the docs-search server in memory and over stdio. Run: uv run python test_server.py"""
import asyncio
import os
from pathlib import Path

from mcp import Client, StdioServerParameters

from server import DOCS_DIR, mcp


async def check(client: Client) -> None:
    tools = (await client.list_tools()).tools
    assert sorted(tool.name for tool in tools) == ["read_doc", "search_docs"], tools
    assert all(tool.annotations.read_only_hint for tool in tools), tools

    found = await client.call_tool("search_docs", {"query": "rate limit"})
    assert not found.is_error, found
    paths = [match["path"] for match in found.structured_content["result"]]
    assert paths == ["guides/errors.md", "guides/quickstart.md"], paths

    page = await client.call_tool("read_doc", {"path": "guides/errors.md"})
    assert not page.is_error and "3: A 429 response" in page.content[0].text, page

    for escape in ["../private.md", "/etc/passwd", "guides/../../private.md", "leak.md"]:
        result = await client.call_tool("read_doc", {"path": escape})
        assert result.is_error, (escape, result)
        assert "do-not-read" not in str(result), (escape, result)
        assert "not a Markdown file inside the docs folder" in result.content[0].text, result

    leaked = await client.call_tool("search_docs", {"query": "do-not-read"})
    assert leaked.structured_content["result"] == [], leaked


async def main() -> None:
    leak = DOCS_DIR / "leak.md"
    leak.unlink(missing_ok=True)
    leak.symlink_to(Path("..") / "private.md")
    try:
        async with Client(mcp) as client:
            await check(client)
        print("in-memory: ok")
        stdio = StdioServerParameters(command="uv", args=["run", "server.py"], env={**os.environ, "DOCS_DIR": str(DOCS_DIR)})
        async with Client(stdio) as client:
            await check(client)
            print(f"stdio: ok (protocol {client.protocol_version})")
    finally:
        leak.unlink(missing_ok=True)


asyncio.run(main())
```

Run it, and expect both lines at the end of the output:

```bash
uv run python test_server.py
# in-memory: ok
# stdio: ok (protocol 2026-07-28)
```

If an assertion fails, the traceback names the escape path or the search that broke. The server also logs each refused path at INFO level on stderr, so those lines are expected in the output.

The test catches the bugs it is there for. With the `is_relative_to` check removed, `read_doc` returned `../private.md` with the secret in it, and with `os.path.abspath` in place of `resolve()`, the `leak.md` symlink did.

A sentinel without the `.md` suffix would hide the first bug, because the suffix check refuses it before the folder check matters.

## How to inspect an MCP server from the command line

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) in CLI mode, which calls one method and prints the JSON result:

```bash
npx -y @modelcontextprotocol/inspector@2.12.0 --cli --method tools/list uv run server.py
npx -y @modelcontextprotocol/inspector@2.12.0 --cli --method tools/call --tool-name search_docs --tool-arg 'query=rate limit' -- uv run server.py
```

The first command lists both tools with `"readOnlyHint": true`, and the second returns both rate-limit matches as `structuredContent`. When a call fails, the CLI exits with status 5, so a script can catch a refused path.

Put `--` before the server command whenever `--tool-arg` comes last, because the flag takes every value that follows it. Without `--`, the Inspector read `uv` as a malformed argument.

The Inspector also parses `--tool-arg query=429` as a number, and the server's schema rejects it with "Input should be a valid string." Wrap the value in JSON quotes, as in `--tool-arg 'query="429"'`, and it arrives as a string.

## How to connect an MCP server to Claude Code

Register it for the project with [`claude mcp add`](https://code.claude.com/docs/en/mcp), putting the server name before `-e`, because `-e` reads every value after it until `--`:

```bash
claude mcp add --scope project docs-search -e DOCS_DIR="$PWD/docs" -- uv --directory "$PWD" run server.py
claude mcp get docs-search
```

The command writes the server to `.mcp.json` in the project, and `claude mcp get` reports `⏸ Pending approval`. Run `claude` in the folder and approve the server, because Claude Code doesn't start a project-scoped server until you do.

Then ask a question the docs answer:

```text
Use the docs-search MCP tools to find the API's rate limit in these docs. Answer in one sentence and name the file and line you used.
```

Each headless `claude -p` run made the same calls, in this order:

1. `ToolSearch`, which loaded both tools
2. `search_docs` with the query `rate limit`
3. `read_doc` on `guides/quickstart.md`

If Claude answers without calling `mcp__docs-search__search_docs`, run `/mcp` in the session to check that the server is connected. A [Claude Code subagent](/articles/claude-code-subagents/) gets these MCP tools only if its `tools` list allows them, so a read-only subagent can be given `search_docs` and `read_doc` and nothing that writes.

## Why should a tool number the lines it returns?

Because the model cites what it can copy, and it miscounts what it has to count. The first version of `read_doc` returned plain text, and Claude on Haiku 5.5 read the right file and found the right limit, then cited the wrong line in every run but one.

Here are the lines it cited for the same question, with the same two tool calls in every run. The sentence it quoted sits on line 8 of `quickstart.md`:

| `read_doc` returns | Runs | Lines cited |
|---|---|---|
| Plain text | 4 | 9, 7, 8, 9 |
| Numbered lines, as in the server above | 4 | 8, 8, 8, 8 |

That's a small sample, and I'd read it as a design rule more than a benchmark. When a model has to cite something, such as a line or an ID, the tool should return it ready to copy.

## FAQ

### What is an MCP server?

An MCP server is a program that exposes tools, resources or prompts to an AI client over the Model Context Protocol. The client lists what the server offers, and the model calls a tool by name with arguments that match the tool's schema.

### Which transport should an MCP server use?

Use stdio for a server that runs on the same machine as the client, as this tutorial does. The MCP spec also defines Streamable HTTP, for a server that runs as a shared service that clients reach over the network.

### Can an MCP server print to stdout?

Not over stdio, because stdout carries the protocol messages and the spec forbids anything else there. Write logs with Python's `logging` module, which goes to stderr.

### How do you test an MCP server?

Connect the SDK's `Client` to the server object in memory for fast checks, then over stdio to test the real process. The MCP Inspector's CLI mode calls single methods from the shell, which suits a quick check or a CI script.
