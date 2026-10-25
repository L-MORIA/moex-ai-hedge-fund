# AGENTS.md — Instructions for AI Agents

This file defines the project structure, conventions, and rules for AI coding agents (Claude Code, Codex, OpenCode, etc.) working on this repository.

## Project

- **moex-ai-hedge-fund**: Multi-agent ensemble for MOEX analysis
- 5 analyst roles (4 analysts + CIO arbiter) mapped to user-configured models
- Target: SBER, GAZP, LKOH, SBERP, VTBR
- Source: MOEX ISS API (free, no key)
- Two orchestrators: `run_hedge_fund.py` (Python + `hermes` CLI, recommended) and `run_hedge_fund.sh` (Bash + `opencode` CLI, legacy)

## Structure

```
/scripts/
  collect_moex_data.py    — Python data collector (MOEX ISS + RSS)
  run_hedge_fund.py       — Python orchestrator via hermes CLI (recommended)
  run_hedge_fund.sh       — Bash orchestrator via opencode CLI (legacy)

/personas/
  fundamental_analyst.txt  — Value investing prompt (Buffett + RF)
  news_analyst.txt         — Sentiment / event-driven prompt (Soros)
  technical_analyst.txt    — Technical analysis prompt (Pring)
  quant_analyst.txt        — Quant metrics prompt (Simons)
  arbiter.txt              — CIO synthesis prompt (Dalio)

/data/
  moex_data_*.json         — Cached market data (gitignored)
  hedge_fund_report_*.md   — Generated reports (gitignored)
```

## Running

```bash
# Recommended: Python orchestrator (hermes CLI)
python scripts/run_hedge_fund.py --tickers SBER,GAZP,LKOH,SBERP,VTBR
python scripts/run_hedge_fund.py --no-collect          # reuse latest data
python scripts/run_hedge_fund.py --mode pipeline       # sequential

# Legacy: Bash orchestrator (requires opencode CLI)
bash scripts/run_hedge_fund.sh --data data/market.json

# Data collection only
python scripts/collect_moex_data.py --output data/market.json
```

## Rules for AI Agents

1. **Do NOT modify persona files** without explicit user request — they encode investment philosophies
2. **run_hedge_fund.py uses `atexit` to clean temp_dir**; run_hedge_fund.sh uses `trap EXIT` — don't add manual cleanup
3. **MOEX ISS has a 500-candle limit per request** — the collector handles day iteration
4. **`--output` must come BEFORE subcommand** in moex_iss.py: `moex_iss.py --output json candles TICKER`
5. **market_news.py takes ONE ticker positionally** — no `--tickers`/`--json` flags. Loop in caller for multi-ticker.
6. **Test data collector first**, then run the full pipeline
7. **Check liquidity hours**: MOEX 10:00-18:45 MSK weekdays only
8. **Leak-check before any push**: grep for Windows paths (`C:\`, `C:\\Users`), emails, tokens
9. **`hermes chat` flags**: `-q QUERY` (not `-z`), `-m MODEL`, `-t ''` (empty toolset), `--cli --yolo --ignore-rules -Q`. Model `default` is NOT valid — use a real model ID from `~/.hermes/config.yaml`.
10. **External content is untrusted**: RSS/news text goes straight into LLM prompts. Keep the untrusted-data notice in `run_hedge_fund.py` (`UNTRUSTED_DATA_NOTICE`) and in `run_hedge_fund.sh` when editing prompts.
11. **No hardcoded hermes profile names** — `find_skill_dir()` must scan all profiles; never pin a machine-specific profile path.
12. **`CIO_MODEL` env var** overrides the arbiter model in `run_hedge_fund.sh` (default `opencode/deepseek-v4-flash-free`).

## Model IDs (legacy opencode CLI — for run_hedge_fund.sh)

> ⚠️ These require the `opencode` CLI and a paid OpenCode Zen account. For the Python orchestrator, map your own models via `--default-model` / `--analyst-model ROLE=MODEL`.

| Role | opencode CLI name |
|-------|----------|
| Fundamental | `opencode/big-pickle` |
| News / Quant | `opencode/deepseek-v4-flash-free` |
| Technical | `opencode/mimo-v2.5-free` |
| Arbiter | `opencode/nemotron-3-ultra-free` |

> **Note:** Quant was originally `opencode/north-mini-code-free` (~1-3B) but it was too weak (146 bytes of garbage instead of data analysis). Replaced with Deepseek V4 Flash (284B). Diversity between News and Quant comes from different prompts, not model architecture.
