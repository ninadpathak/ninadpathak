import pathlib
import subprocess
import unittest

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]
QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"


class WorkflowShellSyntaxTests(unittest.TestCase):
    def test_every_quality_workflow_run_block_is_valid_bash(self):
        workflow = yaml.safe_load(QUALITY_WORKFLOW.read_text(encoding="utf-8"))
        checked = 0
        for job_name, job in workflow["jobs"].items():
            for step in job.get("steps", []):
                script = step.get("run")
                if not script:
                    continue
                checked += 1
                result = subprocess.run(
                    ["bash", "-n"],
                    input=script,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    f"invalid shell in {job_name!r} step {step.get('name')!r}:\n"
                    f"{result.stderr}",
                )
        self.assertGreater(checked, 0, "quality workflow has no shell run blocks")


if __name__ == "__main__":
    unittest.main()
