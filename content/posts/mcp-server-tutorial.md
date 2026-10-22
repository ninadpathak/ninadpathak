---
category: ai-engineering
date: 2026-10-22
description: Build an MCP server in Python that searches a docs folder, test it without a model, inspect it, and connect it to Claude Code, with every step run on 2026-10-22.
slug: mcp-server-tutorial
status: published
takeaways:
- The MCP Python SDK turns type-hinted functions into tools, and a stdio server must keep its stdout for protocol messages.
- Resolve every path a tool receives before checking it against the folder it may read, because relative segments and symlinks both arrive as plain strings.
- Return what the model has to cite, because Claude cited the right line in every run once the tool numbered its lines.
title: 'MCP Server Tutorial: Build and Test a Docs Search Server in Python'
work_note: 'Technical writer [Ninad Pathak](/portfolio/) writes technical documentation for developer tools, including setup guides for MCP servers and the AI clients that call them.'
---

An MCP server is a small program that hands an AI client a list of tools it can call. The one built here gives Claude Code, or any MCP client, read-only search over a folder of Markdown docs.

Every command below ran from a clean directory on 2026-10-22, with MCP Python SDK 2.3.0 and MCP Inspector 2.12.0, and Claude Code 2.1.308 as the client. Numbering the lines a tool returns was the smallest change, and it decided whether Claude cited the right line.

## Set up the project

The [Model Context Protocol](/articles/model-context-protocol/) has its own SDKs, and the Python one installs with uv. The SDK needs Python 3.10 or later:

```bash
uv init --bare docs-search --python 3.12
cd docs-search
uv add "mcp[cli]==2.3.0"
```

With uv 0.12.7, a plain `uv init docs-search` creates a packaged `src/` layout. `--bare` writes only `pyproject.toml`, which is all a single-file server needs.

Add a small docs folder to search, and a file outside it that the server must never read:

```bash
mkdir -p docs/guides
printf '# Quickstart\n\nInstall the CLI with `npm install -g acme-cli`.\nThen run `acme login` to store an API key.\n\n## Rate limits\n\nThe API allows 100 requests per minute per key.\n' > docs/guides/quickstart.md
printf '# Errors\n\nA 429 response means you hit the rate limit. Wait and retry.\n' > docs/guides/errors.md
echo "SECRET=do-not-read" > .env.secret
```

## Write the server with two read-only tools

Save this as `server.py`:

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

    Returns up to `limit` matches (at most 50), each with the file path relative
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

The server never calls `print()`. The [stdio transport spec](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio) says a server "MUST NOT write anything to its `stdout` that is not a valid MCP message," and Python's `logging` writes to stderr, which the spec leaves free for logs.

A refused path raises `ToolError` on purpose. SDK 2.3.0 sends a `ToolError` message to the client as an error result, and it turns any other exception into a generic "Error executing tool" with a crash traceback in the server log.

## Keep tool arguments inside the docs folder

A tool's arguments come from the model, so treat each one as untrusted input. `inside_docs()` calls `resolve()` before comparing, which collapses `..` segments and follows symlinks, then checks that the real location sits under `DOCS_DIR`.

Checking the raw string would miss both. `guides/../../.env.secret` contains no suspicious prefix, and a symlink named `leak.md` inside `docs/` looks like any other Markdown file until it's resolved.

## Test the server without a model

The SDK's `Client` can connect to the server object in memory, or launch it as a stdio subprocess the way a host does. Save this as `test_server.py`:

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

    for escape in ["../.env.secret", "/etc/passwd", "guides/../../.env.secret", "leak.md"]:
        result = await client.call_tool("read_doc", {"path": escape})
        assert result.is_error, (escape, result)
        assert "do-not-read" not in str(result), (escape, result)
        assert "not a Markdown file inside the docs folder" in result.content[0].text, result

    leaked = await client.call_tool("search_docs", {"query": "do-not-read"})
    assert leaked.structured_content["result"] == [], leaked


async def main() -> None:
    leak = DOCS_DIR / "leak.md"
    leak.unlink(missing_ok=True)
    leak.symlink_to(Path("..") / ".env.secret")
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

The test catches the bugs it is there for. With the `is_relative_to` check removed, `../.env.secret` came back with the secret in it, and with `os.path.abspath` in place of `resolve()`, the `leak.md` symlink did.

## Inspect the server with the MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) has a CLI mode that calls one method and prints the JSON result:

```bash
npx -y @modelcontextprotocol/inspector@2.12.0 --cli --method tools/list uv run server.py
npx -y @modelcontextprotocol/inspector@2.12.0 --cli --method tools/call --tool-name search_docs --tool-arg 'query=rate limit' -- uv run server.py
```

The first command lists both tools with `"readOnlyHint": true`, and the second returns both rate-limit matches as `structuredContent`. When a call fails, the CLI exits with status 5, so a script can catch a refused path.

Put `--` before the server command whenever `--tool-arg` comes last, because the flag takes every value that follows it. Without `--`, the Inspector read `uv` as a malformed argument.

The Inspector also parses `--tool-arg query=429` as a number, and the server's schema rejects it with "Input should be a valid string." Wrap the value in JSON quotes, as in `--tool-arg 'query="429"'`, and it arrives as a string.

## Connect the server to Claude Code

Register the server for this project with [`claude mcp add`](https://code.claude.com/docs/en/mcp). The server name goes before `-e`, because `-e` reads every value after it until `--`:

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

If Claude answers without calling `mcp__docs-search__search_docs`, run `/mcp` in the session to check that the server is connected.

## Number the lines a tool returns

The first version of `read_doc` returned plain text, and Claude on Haiku 5.5 read the right file and found the right limit. It then cited the wrong line, because it had to count lines itself.

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
