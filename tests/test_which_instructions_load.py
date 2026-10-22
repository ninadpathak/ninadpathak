"""static/examples/which-instructions-load.sh is published for readers to run.

Stub `claude` and `codex` executables stand in for the real agents, so these tests
need neither tool nor a login. They pin the review findings: the script must not
delete or enter directories it did not create, must clean up after itself, must
refuse to run under a parent directory that holds an instruction file, and must
report TOOLS when an agent had or used tools instead of trusting its answer.
"""

import os
import shutil
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "static/examples/which-instructions-load.sh"

FAKE_CLAUDE = r"""#!/usr/bin/env bash
# Emulates Claude Code's documented default: CLAUDE.md wins, AGENTS.md only without it,
# and an @AGENTS.md import pulls AGENTS.md in.
words=()
if [ -f CLAUDE.md ]; then
  grep -q '^@AGENTS.md' CLAUDE.md && words+=("AGENTS-4417")
  words+=("CLAUDE-2093")
elif [ -f AGENTS.md ]; then
  words+=("AGENTS-4417")
fi
answer=$(IFS=,; echo "${words[*]:-NONE}" | sed 's/,/, /g')
tools='[]'; [ -n "${FAKE_CLAUDE_TOOLS:-}" ] && tools='["Read"]'
echo "{\"type\":\"system\",\"subtype\":\"init\",\"tools\":$tools,\"mcp_servers\":[]}"
echo "{\"type\":\"assistant\",\"message\":{\"content\":[{\"type\":\"text\",\"text\":\"$answer\"}]}}"
echo "{\"type\":\"result\",\"subtype\":\"success\",\"result\":\"$answer\"}"
"""

FAKE_CODEX = r"""#!/usr/bin/env bash
answer=NONE; [ -f AGENTS.md ] && answer=AGENTS-4417
if [ -n "${FAKE_CODEX_COMMAND:-}" ]; then
  echo '{"type":"item.completed","item":{"type":"command_execution","command":"cat CLAUDE.md"}}'
fi
echo "{\"type\":\"item.completed\",\"item\":{\"type\":\"agent_message\",\"text\":\"$answer\"}}"
"""


class WhichInstructionsLoadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for name, body in (("claude", FAKE_CLAUDE), ("codex", FAKE_CODEX)):
            path = self.bin / name
            path.write_text(body)
            path.chmod(path.stat().st_mode | stat.S_IEXEC)
        self.scratch = self.tmp / "scratch"
        self.scratch.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_script(self, *args, cwd=None, **env):
        full_env = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}",
                    "TMPDIR": str(self.scratch), **env}
        return subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd or self.tmp,
                              env=full_env, capture_output=True, text=True, timeout=60)

    def test_caller_directory_is_never_deleted(self):
        # Review finding 6: the old script ran `rm -rf "$WORK/1-agents-only"` on a caller path.
        caller = self.tmp / "my-project"
        (caller / "1-agents-only").mkdir(parents=True)
        (caller / "1-agents-only" / "keep.txt").write_text("user data")
        result = self.run_script(str(caller))
        self.assertEqual(result.returncode, 2)
        self.assertTrue((caller / "1-agents-only" / "keep.txt").exists())
        self.run_script(cwd=caller)
        self.assertTrue((caller / "1-agents-only" / "keep.txt").exists())

    def test_reports_documented_defaults_and_cleans_up(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = {line.split()[0]: line for line in result.stdout.splitlines()[1:5]}
        self.assertIn("AGENTS-4417", rows["1-agents-only"])
        self.assertRegex(rows["2-claude-only"], r"CLAUDE-2093\s+NONE")
        self.assertRegex(rows["3-both"], r"CLAUDE-2093\s+AGENTS-4417")
        self.assertIn("AGENTS-4417, CLAUDE-2093", rows["4-claude-imports"])
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_aborts_under_a_parent_instruction_file(self):
        # Review finding 7: a parent CLAUDE.md would contaminate what the agent reports.
        (self.scratch / "CLAUDE.md").write_text("Codeword: PARENT-0001\n")
        nested = self.scratch / "nested"
        nested.mkdir()
        result = self.run_script(TMPDIR=str(nested))
        self.assertEqual(result.returncode, 3)
        self.assertIn("exists above the test directory", result.stderr)

    def test_tool_access_or_use_is_reported_instead_of_the_answer(self):
        # Review finding 7: an agent that can read files could find a codeword itself.
        result = self.run_script(FAKE_CLAUDE_TOOLS="1", FAKE_CODEX_COMMAND="1")
        self.assertEqual(result.returncode, 0, result.stderr)
        for line in result.stdout.splitlines()[1:5]:
            self.assertRegex(line, r"\S+\s+TOOLS\s+TOOLS$")


if __name__ == "__main__":
    unittest.main()
