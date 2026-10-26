"""Unit tests for scripts/run_hedge_fund.py (stdlib unittest, no external deps).

Run:
    python -m unittest discover -s tests -v
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(os.path.dirname(TESTS_DIR), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import run_hedge_fund as rh  # noqa: E402


class TestParseModelArgs(unittest.TestCase):
    def test_basic_mapping_and_defaults(self):
        result = rh.parse_model_args(
            ["technical=openrouter/deepseek/deepseek-chat-v3", "arbiter=ollama/qwen3"],
            "default",
        )
        self.assertEqual(result["technical"], "openrouter/deepseek/deepseek-chat-v3")
        self.assertEqual(result["arbiter"], "ollama/qwen3")
        # Roles without explicit mapping fall back to the default model
        self.assertEqual(result["fundamental"], "default")
        self.assertEqual(result["news"], "default")
        self.assertEqual(result["quant"], "default")
        self.assertEqual(set(result), {"fundamental", "news", "technical", "quant", "arbiter"})

    def test_arbiter_is_independent_role(self):
        # Arbiter must not inherit a model set for another role (regression:
        # it used to be tied to the fundamental analyst's model)
        result = rh.parse_model_args(["fundamental=modelA"], "default")
        self.assertEqual(result["fundamental"], "modelA")
        self.assertEqual(result["arbiter"], "default")

    def test_unknown_role_warns_and_is_ignored(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = rh.parse_model_args(["hacker=modelX"], "default")
        self.assertNotIn("hacker", result)
        self.assertIn("unknown role", err.getvalue())

    def test_missing_equals_warns(self):
        # --analyst-model without '=' is a CLI mistake: must warn, not stay silent
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rh.parse_model_args(["technical"], "default")
        self.assertIn("expected role=model", err.getvalue())

    def test_spaces_around_roles_and_models(self):
        result = rh.parse_model_args([" technical = modelA "], "default")
        self.assertEqual(result["technical"], "modelA")


class TestFindSkillDir(unittest.TestCase):
    def _make_skill(self, base):
        skill = os.path.join(base, "skills", "moex-iss", "scripts", "moex_iss.py")
        os.makedirs(os.path.dirname(skill), exist_ok=True)
        with open(skill, "w", encoding="utf-8") as f:
            f.write("# fake")
        return skill

    def test_finds_skill_in_any_profile(self):
        with tempfile.TemporaryDirectory() as home:
            self._make_skill(os.path.join(home, "AppData", "Local", "hermes",
                                          "profiles", "some-profile"))
            with mock.patch("os.path.expanduser", return_value=home):
                self.assertIsNotNone(rh.find_skill_dir())

    def test_finds_direct_skill(self):
        with tempfile.TemporaryDirectory() as home:
            self._make_skill(os.path.join(home, ".hermes"))
            with mock.patch("os.path.expanduser", return_value=home):
                found = rh.find_skill_dir()
            self.assertIsNotNone(found)
            self.assertIn("moex-iss", found)

    def test_no_skill_returns_none(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch("os.path.expanduser", return_value=home):
                self.assertIsNone(rh.find_skill_dir())

    def test_no_hardcoded_profile_name(self):
        # The author's personal profile name must not be hardcoded (info leak)
        src = os.path.join(SCRIPTS_DIR, "run_hedge_fund.py")
        with open(src, "r", encoding="utf-8") as f:
            self.assertNotIn("old-laptop", f.read())


class TestCallHermesModel(unittest.TestCase):
    def test_hermes_cli_flags(self):
        with mock.patch("subprocess.run") as mrun:
            mrun.return_value = subprocess.CompletedProcess([], 0, stdout="OK", stderr="")
            out = rh.call_hermes_model("mymodel", "prompt")
        self.assertEqual(out, "OK")
        cmd = mrun.call_args[0][0]
        self.assertEqual(cmd, ["hermes", "chat", "-q", "prompt", "-m", "mymodel",
                               "-t", "", "--cli", "--yolo", "--ignore-rules", "-Q"])

    def test_hermes_nonzero_rc(self):
        with mock.patch("subprocess.run") as mrun:
            mrun.return_value = subprocess.CompletedProcess([], 3, stdout="", stderr="boom")
            out = rh.call_hermes_model("m", "p")
        self.assertIn("[HERMES FAILED rc=3", out)
        self.assertIn("boom", out)

    def test_hermes_empty_response(self):
        with mock.patch("subprocess.run") as mrun:
            mrun.return_value = subprocess.CompletedProcess([], 0, stdout="  \n", stderr="")
            out = rh.call_hermes_model("m", "p")
        self.assertEqual(out, "[HERMES EMPTY RESPONSE]")

    def test_hermes_timeout(self):
        with mock.patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="hermes", timeout=1)):
            out = rh.call_hermes_model("m", "p", timeout=1)
        self.assertIn("[HERMES TIMEOUT", out)

    def test_hermes_not_in_path(self):
        with mock.patch("subprocess.run", side_effect=FileNotFoundError("hermes")):
            out = rh.call_hermes_model("m", "p")
        self.assertIn("not found in PATH", out)

    def test_prompt_too_long_rejected_before_spawn(self):
        # Windows CreateProcess caps the command line at ~32K chars; a huge
        # prompt must fail with a readable message, not a WinError 206 crash.
        huge = "x" * (rh.MAX_CMDLINE_CHARS + 1000)
        with mock.patch("subprocess.run") as mrun:
            out = rh.call_hermes_model("m", huge)
        mrun.assert_not_called()
        self.assertIn("prompt too long", out)


class TestRunHelper(unittest.TestCase):
    def test_skill_not_found(self):
        self.assertIn("moex-iss skill not found", rh.run(None))
        self.assertIn("moex-iss skill not found", rh.run([None, "cmd"]))

    def test_timeout(self):
        with mock.patch("subprocess.run",
                        side_effect=subprocess.TimeoutExpired(cmd="py", timeout=5)):
            self.assertIn("ERROR: timeout", rh.run(["script.py", "x"], timeout=5))

    def test_nonzero_rc_reports_stderr(self):
        with mock.patch("subprocess.run") as mrun:
            mrun.return_value = subprocess.CompletedProcess([], 2, stdout="", stderr="oops")
            out = rh.run(["script.py"])
        self.assertEqual(out, "ERROR: rc=2 oops")


class TestCollectData(unittest.TestCase):
    def _patched_collect(self, tickers, output_path=None):
        captured = []

        def fake_run(cmd, timeout=30):
            captured.append(cmd)
            if "candles" in cmd:
                return '[{"open":1}]'
            return "text output"

        with mock.patch.object(rh, "run", side_effect=fake_run), \
             mock.patch.object(rh, "MOEX_SCRIPT", "fake_moex.py"), \
             mock.patch.object(rh, "MARKET_NEWS_SCRIPT", "fake_news.py"), \
             mock.patch.object(rh, "SKILL_DIR", "fake_skill_dir"):
            data, path = rh.collect_data(tickers, 14, 48, output_path)
        return data, path, captured

    def test_portfolio_gets_normalized_tickers(self):
        # Regression: raw "--tickers" value (spaces, lowercase, empty items)
        # used to be passed to the `portfolio` subcommand as-is, while
        # candles/RSS used the normalized list.
        data, _, captured = self._patched_collect("SBER, gazp ,LKOH,")
        portfolio_cmd = next(c for c in captured if "portfolio" in c)
        self.assertEqual(portfolio_cmd[2], "SBER,GAZP,LKOH")
        self.assertEqual(data["meta"]["tickers"], ["SBER", "GAZP", "LKOH"])

    def test_candles_parsed_as_json(self):
        data, _, _ = self._patched_collect("SBER")
        self.assertEqual(data["candles"]["SBER"], [{"open": 1}])

    def test_error_output_kept_as_string(self):
        def fake_run(cmd, timeout=30):
            return "ERROR: rc=1 boom"
        with mock.patch.object(rh, "run", side_effect=fake_run), \
             mock.patch.object(rh, "MOEX_SCRIPT", "s.py"), \
             mock.patch.object(rh, "MARKET_NEWS_SCRIPT", "n.py"), \
             mock.patch.object(rh, "SKILL_DIR", "d"):
            data, _ = rh.collect_data("SBER", 14, 48, None)
        self.assertEqual(data["candles"]["SBER"], "ERROR: rc=1 boom")

    def test_writes_output_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sub", "moex_data_test.json")
            self._patched_collect("SBER,GAZP", output_path=path)
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved["meta"]["tickers"], ["SBER", "GAZP"])


if __name__ == "__main__":
    unittest.main()
