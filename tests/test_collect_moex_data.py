"""Unit tests for scripts/collect_moex_data.py (stdlib unittest)."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(os.path.dirname(TESTS_DIR), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

import collect_moex_data as cmd_mod  # noqa: E402


class TestFindSkillDir(unittest.TestCase):
    def test_finds_skill_in_profile(self):
        with tempfile.TemporaryDirectory() as home:
            skill = os.path.join(home, ".hermes", "profiles", "p1",
                                 "skills", "moex-iss", "scripts", "moex_iss.py")
            os.makedirs(os.path.dirname(skill), exist_ok=True)
            with open(skill, "w", encoding="utf-8") as f:
                f.write("# fake")
            with mock.patch("os.path.expanduser", return_value=home):
                self.assertIsNotNone(cmd_mod.find_skill_dir())

    def test_no_skill_returns_none(self):
        with tempfile.TemporaryDirectory() as home:
            with mock.patch("os.path.expanduser", return_value=home):
                self.assertIsNone(cmd_mod.find_skill_dir())


class TestMainNormalizesTickers(unittest.TestCase):
    def test_portfolio_gets_normalized_tickers(self):
        # Regression: the raw --tickers value used to go straight into the
        # `portfolio` subcommand even with spaces/lowercase/empty items.
        captured = []

        def fake_run(cmd, timeout=30):
            captured.append(cmd)
            return "[]" if "candles" in cmd else "text"

        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "out.json")
            argv = ["prog", "--tickers", "SBER, gazp ,", "--output", out_path]
            with mock.patch.object(sys, "argv", argv), \
                 mock.patch.object(cmd_mod, "run", side_effect=fake_run), \
                 mock.patch.object(cmd_mod, "SKILL_DIR", "fake"), \
                 mock.patch.object(cmd_mod, "MOEX_SCRIPT", "fake_moex.py"), \
                 mock.patch.object(cmd_mod, "RSS_SCRIPT", "fake_rss.py"):
                with contextlib.redirect_stderr(io.StringIO()):
                    cmd_mod.main()
            portfolio_cmd = next(c for c in captured if "portfolio" in c)
            self.assertEqual(portfolio_cmd[2], "SBER,GAZP")
            with open(out_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.assertEqual(saved["meta"]["tickers"], ["SBER", "GAZP"])
            self.assertEqual(sorted(saved["candles"].keys()), ["GAZP", "SBER"])
            self.assertEqual(sorted(saved["rss_news"].keys()), ["GAZP", "SBER"])


if __name__ == "__main__":
    unittest.main()
