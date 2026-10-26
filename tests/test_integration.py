"""Integration and safety tests: bash orchestrator, CLI error handling, leak scan.

Run:
    python -m unittest discover -s tests -v
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(TESTS_DIR)
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
RUN_PY = os.path.join(SCRIPTS_DIR, "run_hedge_fund.py")
RUN_SH = os.path.join(SCRIPTS_DIR, "run_hedge_fund.sh")

BASH = shutil.which("bash")
for _candidate in (r"C:\Program Files\Git\bin\bash.exe",
                   r"C:\Program Files\Git\usr\bin\bash.exe"):
    if BASH:
        break
    if os.path.isfile(_candidate):
        BASH = _candidate


@unittest.skipIf(BASH is None, "bash not available")
class TestBashOrchestrator(unittest.TestCase):
    def test_no_collect_without_data_prints_friendly_error(self):
        # Regression: with `set -eo pipefail`, a failed glob in
        # `DATA_FILE=$(ls ... | head -1)` killed the script silently (exit 2)
        # and the "ERROR: No existing data found" branch was unreachable.
        tmp = tempfile.mkdtemp(prefix="hf_sh_test_")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        shutil.copy(RUN_SH, os.path.join(tmp, "run_hedge_fund.sh"))
        os.makedirs(os.path.join(tmp, "data"))  # empty data dir
        r = subprocess.run([BASH, os.path.join(tmp, "run_hedge_fund.sh"), "--no-collect"],
                           capture_output=True, text=True, timeout=60,
                           cwd=tmp, errors="replace")
        combined = (r.stdout or "") + (r.stderr or "")
        self.assertEqual(r.returncode, 1,
                         f"expected friendly exit 1, got {r.returncode}; output: {combined!r}")
        self.assertIn("ERROR: No existing data found", combined)

    def test_shell_syntax(self):
        r = subprocess.run([BASH, "-n", RUN_SH], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class TestPythonCliErrors(unittest.TestCase):
    """run_hedge_fund.py must fail with readable messages, not tracebacks."""

    def _run(self, *extra):
        return subprocess.run([sys.executable, RUN_PY, *extra],
                              capture_output=True, text=True, timeout=120,
                              cwd=REPO_ROOT, errors="replace")

    def test_analysts_all_typos_exits_with_message(self):
        # Regression (fixed in 1.0.2, guarded here): unknown --analysts roles
        # used to produce an empty list and crash ThreadPoolExecutor.
        with tempfile.TemporaryDirectory() as tmp:
            data = os.path.join(tmp, "d.json")
            with open(data, "w", encoding="utf-8") as f:
                json.dump({"meta": {"tickers": ["SBER"]}}, f)
            r = self._run("--data", data, "--analysts", "typo1,typo2")
            combined = (r.stdout or "") + (r.stderr or "")
            self.assertEqual(r.returncode, 1)
            self.assertIn("no valid analysts selected", combined)
            self.assertNotIn("Traceback", combined)

    def test_invalid_data_json_exits_with_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.json")
            with open(bad, "w", encoding="utf-8") as f:
                f.write("{not json")
            r = self._run("--data", bad, "--analysts", "news")
            combined = (r.stdout or "") + (r.stderr or "")
            self.assertEqual(r.returncode, 1)
            self.assertIn("not valid JSON", combined)
            self.assertNotIn("Traceback", combined)


class TestLauncherFiles(unittest.TestCase):
    def test_bat_files_ascii_only(self):
        # cmd.exe on RU Windows mangles non-ASCII in .bat (em-dashes broke it before)
        for name in ("hedge_fund.bat", "hedge_fund_pipeline.bat"):
            with open(os.path.join(REPO_ROOT, name), "rb") as f:
                raw = f.read()
            non_ascii = [b for b in raw if b > 0x7F]
            self.assertEqual(non_ascii, [], f"{name} contains non-ASCII bytes")

    def test_no_personal_profile_hardcoded(self):
        for name in ("run_hedge_fund.py", "collect_moex_data.py"):
            with open(os.path.join(SCRIPTS_DIR, name), "r", encoding="utf-8") as f:
                self.assertNotIn("old-laptop", f.read(), name)


class TestNoSecretsInRepo(unittest.TestCase):
    """Leak scan over all tracked files: secrets, tokens, personal paths, emails."""

    SECRET_PATTERNS = [
        re.compile(rb"(?i)api[_-]?key\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
        re.compile(rb"(?i)(secret|password|token)\s*[=:]\s*['\"]?[A-Za-z0-9_\-./+]{16,}"),
        re.compile(rb"sk-[A-Za-z0-9_\-]{20,}"),          # OpenAI-style keys
        re.compile(rb"gh[pousr]_[A-Za-z0-9]{20,}"),       # GitHub tokens
        re.compile(rb"AKIA[0-9A-Z]{16}"),                 # AWS access keys
        re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # emails
        re.compile(rb"C:\\+Users\\+[A-Za-z0-9_.\-]+"),    # personal Windows paths
    ]
    def _tracked_files(self):
        out = subprocess.run(["git", "ls-files"], cwd=REPO_ROOT,
                             capture_output=True, text=True)
        return [f for f in out.stdout.splitlines() if f]

    def test_no_leaks(self):
        offenders = []
        for rel in self._tracked_files():
            path = os.path.join(REPO_ROOT, rel)
            if not os.path.isfile(path):
                continue
            with open(path, "rb") as f:
                raw = f.read()
            for i, line in enumerate(raw.splitlines(), 1):
                for pat in self.SECRET_PATTERNS:
                    m = pat.search(line)
                    if m:
                        offenders.append(f"{rel}:{i}: {m.group(0)[:60]!r}")
        self.assertEqual(offenders, [], "Possible leaks found:\n" + "\n".join(offenders))


if __name__ == "__main__":
    unittest.main()
