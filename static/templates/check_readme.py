#!/usr/bin/env python3
"""Check a README written from readme-template.md, and run the commands it promises.

Usage:
  python3 check_readme.py README.md                  # structure only
  python3 check_readme.py --filled README.md         # also fail on unfilled {{placeholders}}
  python3 check_readme.py --filled --run README.md   # also run the Install, Usage and Tests commands

--run copies the README's folder to a temporary directory and runs every bash, sh or
shell code block under Install, Usage and Tests there, in order, in one bash session.
A block fails when a command in it exits non-zero, or when the text block that follows
it holds a line the command did not print. An HTML comment that holds only
"check_readme: skip" on the line above a block keeps that block from running.

Other options: --timeout SECONDS (default 300, for the whole run), --keep (leave the
temporary copy in place), --env NAME (pass one environment variable through; repeatable).

--run is not a sandbox. The commands run as your user, with network access, so use it
on a README you trust. Exit status is 0 when the README passes and 1 when it fails.
"""
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile

PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
SKIP_MARK = re.compile(r"<!--\s*check_readme:\s*skip\s*-->")
SKIP_LINE = "@@check-readme-skip@@"
FENCE_OPEN = re.compile(r"^( {0,3})(`{3,}|~{3,})[ \t]*([^`\s]*)")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
COMMAND_LANGS = {"bash", "sh", "shell"}
OUTPUT_LANGS = {"", "text", "txt", "output", "plaintext", "json"}
MAX_OPENING_WORDS = 40
SECTIONS = (
    ("Install", re.compile(r"\b(install|installation|installing|setup|getting started)\b", re.I)),
    ("Usage", re.compile(r"\b(usage|examples?|quick ?start)\b", re.I)),
    ("Tests", re.compile(r"\b(tests?|testing)\b", re.I)),
    ("Help", re.compile(r"\b(help|support|contributing|contribute|feedback|questions)\b", re.I)),
    ("License", re.compile(r"\blicen[sc]e\b", re.I)),
)
RUN_SECTIONS = ("Install", "Usage", "Tests")
NOT_PROSE = ("[![", "![", "<", "#", ">", "|", "- ", "* ", "+ ", "```", "~~~")
COPY_SKIP = (".git", ".hg", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
             ".mypy_cache", ".tox", "dist", "build", "target", "*.egg-info", ".DS_Store")


class Block:
    def __init__(self, lang, line, skip):
        self.lang, self.line, self.skip, self.lines = lang.lower(), line, skip, []
        self.expected = None

    @property
    def body(self):
        return "\n".join(self.lines)

    @property
    def first(self):
        for line in self.lines:
            if line.strip() and not line.strip().startswith("#"):
                return line.strip()
        return ""


def parse(text):
    """Split a README into the lines above the first ## heading and its ## sections.

    Headings are read outside code fences only, so a shell comment such as
    "## build" inside a block does not start a section.
    """
    text = SKIP_MARK.sub(SKIP_LINE, text)
    text = re.sub(r"<!--.*?-->", lambda comment: "\n" * comment.group(0).count("\n"), text, flags=re.S)
    top = {"title": "", "prose": [], "blocks": []}
    sections, current, block, skip_next, unclosed = [], top, None, False, None
    for number, line in enumerate(text.splitlines(), 1):
        if block is not None:
            closing = re.match(r"^ {0,3}(`{3,}|~{3,})[ \t]*$", line)
            if closing and closing.group(1)[0] == block.fence[0] and len(closing.group(1)) >= len(block.fence):
                current["blocks"].append(block)
                block = None
            else:
                block.lines.append(line[len(block.indent):] if line.startswith(block.indent) else line)
            continue
        opening = FENCE_OPEN.match(line)
        if opening:
            block = Block(opening.group(3), number, skip_next)
            block.indent, block.fence = opening.group(1), opening.group(2)
            skip_next, unclosed = False, number
            continue
        if line.strip() == SKIP_LINE:
            skip_next = True
            continue
        heading = HEADING.match(line)
        if heading and len(heading.group(1)) == 2:
            current = {"title": heading.group(2), "prose": [], "blocks": []}
            sections.append(current)
            continue
        current["prose"].append(line)
    return top, sections, (unclosed if block is not None else None)


def pair_output(blocks):
    """Attach each output block to the command block right before it."""
    commands, last = [], None
    for block in blocks:
        if block.lang in COMMAND_LANGS:
            commands.append(block)
            last = block
        elif block.lang in OUTPUT_LANGS and last is not None and last.expected is None:
            last.expected = block
            last = None
        else:
            last = None
    return commands


def check_opening(top, errors):
    lines = [line for line in top["prose"] if line.strip()]
    if not lines or not lines[0].startswith("# "):
        errors.append("the file does not start with a '# Title' line")
        return
    if re.search(r"!\[|<img", lines[0]):
        errors.append("the title line holds a badge or an image; move it below the opening sentence")
    start = top["prose"].index(lines[0]) + 1
    paragraph = []
    for line in top["prose"][start:]:
        if line.strip():
            paragraph.append(line.strip())
        elif paragraph:
            break
    if not paragraph:
        errors.append("no sentence under the title says what the project does")
        return
    if paragraph[0].startswith(NOT_PROSE) or re.match(r"\d+\. ", paragraph[0]):
        errors.append(f"the first line under the title is not a sentence: {paragraph[0][:60]!r}")
        return
    opening = " ".join(paragraph)
    if PLACEHOLDER.search(opening):
        return
    plain = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", opening)
    words = len(plain.split())
    if words > MAX_OPENING_WORDS:
        errors.append(f"the opening paragraph is {words} words; say what the project does in {MAX_OPENING_WORDS} or fewer")
    sentences = [part for part in re.split(r"(?<=[.!?])[\"')]?\s+(?=[A-Z\[`\"'])", plain) if part.strip()]
    if len(sentences) > 1:
        errors.append(f"the opening paragraph has {len(sentences)} sentences; say what the project does in one")


def check(text, filled, folder=None):
    """Return (errors, found sections by name, placeholder count)."""
    errors = []
    top, sections, unclosed = parse(text)
    if unclosed:
        errors.append(f"the code block opened on line {unclosed} is never closed")
    check_opening(top, errors)

    found = {}
    for section in sections:
        for name, pattern in SECTIONS:
            if pattern.search(section["title"]) and name not in found:
                found[name] = section
                break
    for name, _ in SECTIONS:
        if name not in found:
            wanted = "Help and contributing" if name == "Help" else name
            errors.append(f"missing a '## {wanted}' section")

    for name in RUN_SECTIONS:
        if name not in found:
            continue
        section = found[name]
        section["commands"] = pair_output(section["blocks"])
        if not any(block.body.strip() for block in section["commands"]):
            errors.append(f"'{section['title']}' has no command in a bash, sh or shell code block")
        for block in section["commands"]:
            prompt = next((line for line in block.lines if re.match(r"^\s*\$ ", line)), None)
            if prompt:
                errors.append(f"'{section['title']}' line {block.line}: a command starts with a '$' prompt, which breaks when pasted: {prompt.strip()!r}")
    if "Install" in found:
        requires = next((line for line in found["Install"]["prose"] if line.startswith("Requires:")), None)
        value = (requires or "").split(":", 1)[-1].strip()
        if requires is None:
            errors.append(f"'{found['Install']['title']}' has no 'Requires:' line naming the runtime and its version")
        elif not PLACEHOLDER.search(value) and not re.search(r"\d", value):
            errors.append(f"'Requires:' names no version number: {value!r}")
    if "Usage" in found:
        shown = [block for block in found["Usage"].get("commands", []) if block.expected and block.expected.body.strip()]
        if found["Usage"].get("commands") and not shown:
            errors.append(f"'{found['Usage']['title']}' shows no expected output in a text block after its command")
    for name in ("Help", "License"):
        if name in found and not "".join(found[name]["prose"]).strip():
            errors.append(f"'{found[name]['title']}' is empty")
    if "Help" in found:
        body = "\n".join(found["Help"]["prose"])
        if body.strip() and not PLACEHOLDER.search(body) and not re.search(r"\]\([^)]+\)|https?://|[\w.+-]+@[\w-]+\.[\w.]+", body):
            errors.append(f"'{found['Help']['title']}' has no link, URL or email address to send a question to")

    if folder is not None:
        prose = "\n".join("\n".join(part["prose"]) for part in [top] + sections)
        for inside in LINK.findall(prose):
            target = inside.split()[0] if inside.split() else ""
            if PLACEHOLDER.search(inside) or re.match(r"[a-z][a-z0-9+.-]*:|#|/", target, flags=re.I):
                continue
            path = target.split("#", 1)[0].split("?", 1)[0]
            if path and not (folder / path).exists():
                errors.append(f"the link to '{target}' points at a file that is not in the README's folder")

    placeholders = PLACEHOLDER.findall(text)
    if filled and placeholders:
        errors.append(f"{len(placeholders)} unfilled placeholder(s), first: {placeholders[0]}")
    return errors, found, len(placeholders)


def clean_env(home, passthrough):
    """Build the environment for the run: PATH without the active virtualenv, and an empty HOME."""
    venv = os.environ.get("VIRTUAL_ENV")
    path = [part for part in os.environ.get("PATH", os.defpath).split(os.pathsep)
            if part and not (venv and Path(part).resolve().is_relative_to(Path(venv).resolve()))]
    env = {"PATH": os.pathsep.join(path), "HOME": str(home), "LANG": os.environ.get("LANG", "C.UTF-8"), "TERM": "dumb"}
    for name in passthrough:
        if name in os.environ:
            env[name] = os.environ[name]
    return env


def missing_line(expected, actual):
    """Return the first expected line that the output lacks, reading both in order."""
    got = [line.strip() for line in ANSI.sub("", actual).splitlines()]
    position = 0
    for line in (line.strip() for line in expected.splitlines()):
        if not line or line == "...":
            continue
        try:
            position = got.index(line, position) + 1
        except ValueError:
            return line
    return None


def tail(text, count=6):
    lines = [line.rstrip() for line in ANSI.sub("", text).splitlines() if line.strip()]
    return [f"      {line[:160]}" for line in lines[-count:]]


def run(readme, found, timeout, keep, passthrough):
    """Run the command blocks in a temporary copy. Return (errors, notes)."""
    if shutil.which("bash") is None:
        return ["--run needs bash on PATH"], []
    work = Path(tempfile.mkdtemp(prefix="check-readme-"))
    project, home, scratch = work / "project", work / "home", work / "blocks"
    shutil.copytree(readme.resolve().parent, project, ignore=shutil.ignore_patterns(*COPY_SKIP), symlinks=True)
    home.mkdir()
    scratch.mkdir()

    queue = []
    for name in RUN_SECTIONS:
        for block in found[name]["commands"]:
            if not block.skip and block.body.strip():
                queue.append((name, block))
    driver = ['cd "$1"', "trap 'printf \"%s\\n%s\\n\" \"$?\" \"$BASH_COMMAND\" > \"$2/failed\"' ERR", "set -eE"]
    for index, (_, block) in enumerate(queue, 1):
        (scratch / f"{index}.sh").write_text(block.body + "\n", encoding="utf-8")
        driver.append(f'printf "%s\\n" {index} > "$2/current"; . "$2/{index}.sh" > "$2/{index}.out" 2>&1')
    driver.append('printf "done\\n" > "$2/current"')
    (scratch / "driver.sh").write_text("\n".join(driver) + "\n", encoding="utf-8")

    errors, timed_out = [], False
    process = subprocess.Popen(["bash", str(scratch / "driver.sh"), str(project), str(scratch)],
                               env=clean_env(home, passthrough), stdin=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        process.wait()

    current = (scratch / "current").read_text().strip() if (scratch / "current").exists() else "1"
    finished = len(queue) if current == "done" else int(current) - 1
    matched = 0
    for index, (name, block) in enumerate(queue[:finished], 1):
        output = (scratch / f"{index}.out").read_text(encoding="utf-8", errors="replace")
        if block.expected and block.expected.body.strip():
            lost = missing_line(block.expected.body, output)
            if lost is None:
                matched += 1
            else:
                errors.append(f"{name}: `{block.first}` did not print the expected line {lost!r}\n    it printed:\n"
                              + "\n".join(tail(output, 8) or ["      (nothing)"]))
    if current != "done":
        name, block = queue[finished]
        out_file = scratch / f"{finished + 1}.out"
        output = out_file.read_text(encoding="utf-8", errors="replace") if out_file.exists() else ""
        if timed_out:
            errors.append(f"{name}: the block starting `{block.first}` was still running after {timeout} seconds")
        elif (scratch / "failed").exists():
            status, _, command = (scratch / "failed").read_text(encoding="utf-8", errors="replace").partition("\n")
            errors.append(f"{name}: `{command.strip()}` exited with status {status}\n" + "\n".join(tail(output)))
        else:
            errors.append(f"{name}: the block starting `{block.first}` ended the shell with status {process.returncode}\n"
                          + "\n".join(tail(output)))
    counts = ", ".join(f"{name} {sum(1 for n, _ in queue[:finished] if n == name)}" for name in RUN_SECTIONS)
    notes = [f"command blocks run: {finished} of {len(queue)} ({counts})", f"output blocks matched: {matched}"]
    if keep:
        notes.append(f"copy kept at: {work}")
    else:
        shutil.rmtree(work, ignore_errors=True)
    return errors, notes


def main(argv):
    filled, do_run, keep = "--filled" in argv, "--run" in argv, "--keep" in argv
    timeout, passthrough, paths = 300, [], []
    args = iter(argv)
    for arg in args:
        if arg == "--timeout":
            timeout = int(next(args))
        elif arg == "--env":
            passthrough.append(next(args))
        elif not arg.startswith("--"):
            paths.append(arg)
    path = Path(paths[0]) if paths else Path(__file__).with_name("readme-template.md")
    text = path.read_text(encoding="utf-8")
    errors, found, placeholders = check(text, filled, path.resolve().parent)
    notes = []
    if do_run and not errors and placeholders:
        errors.append("--run needs a filled README; this file still has {{placeholders}}")
    elif do_run and not errors:
        errors, notes = run(path, found, timeout, keep, passthrough)
    elif do_run:
        notes.append("commands not run: fix the problems above first")
    if errors:
        print(f"{path.name}: FAIL ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        for note in notes:
            print(f"  {note}")
        return 1
    print(f"{path.name}: PASS")
    print(f"  sections found: {', '.join(found[name]['title'] for name, _ in SECTIONS)}")
    for note in notes or ["commands not run: pass --run to run them"]:
        print(f"  {note}")
    print(f"  unfilled placeholders: {placeholders}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
