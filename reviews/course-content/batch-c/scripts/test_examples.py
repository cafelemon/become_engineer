from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[4]
EXAMPLES = ROOT / "reviews/course-content/batch-c/examples"


def run(command: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.pop("DEEPSEEK_API_KEY", None)
    return subprocess.run(command, cwd=cwd, env=env, check=check, text=True, capture_output=True)


class BatchCExamplesTest(unittest.TestCase):
    def test_web_api(self) -> None:
        result = run([sys.executable, "-m", "unittest", "-v", "test_app.py"], EXAMPLES / "web-api")
        self.assertIn("OK", result.stderr)

    def test_ai_experiment(self) -> None:
        result = run([sys.executable, "-m", "unittest", "-v", "test_experiment.py"], EXAMPLES / "ai-experiment")
        self.assertIn("OK", result.stderr)

    def test_llm_offline(self) -> None:
        result = run([sys.executable, "-m", "unittest", "-v", "test_structured_output.py"], EXAMPLES / "llm-structured-output")
        self.assertIn("OK", result.stderr)
        valid = run([sys.executable, "structured_output.py", "--case", "valid"], EXAMPLES / "llm-structured-output")
        self.assertIn('"weekly_hours": 8', valid.stdout)
        invalid = run([sys.executable, "structured_output.py", "--case", "empty"], EXAMPLES / "llm-structured-output", check=False)
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("拒绝", invalid.stdout)

    def test_agent_offline(self) -> None:
        result = run([sys.executable, "-m", "unittest", "-v", "test_agent_tool.py"], EXAMPLES / "agent-read-only-tool")
        self.assertIn("OK", result.stderr)
        trace = run([sys.executable, "agent_tool.py", "--course-id", "python-basics-01"], EXAMPLES / "agent-read-only-tool")
        self.assertIn("call_offline_001", trace.stdout)
        self.assertIn("已开放", trace.stdout)

    def test_deepseek_adapter_requires_local_key(self) -> None:
        code = (
            "from shared.deepseek_client import request_json, DeepSeekConfigurationError; "
            "\ntry: request_json('json','json')\nexcept DeepSeekConfigurationError: print('offline-safe')"
        )
        result = run([sys.executable, "-c", code], EXAMPLES)
        self.assertEqual(result.stdout, "offline-safe\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
