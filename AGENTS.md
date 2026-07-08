# AGENTS.md — Instructions for AI Agents

This file defines the project structure, conventions, and rules for AI coding agents (Claude Code, Codex, OpenCode, etc.) working on this repository.

## Project

- **moex-ai-hedge-fund**: Multi-agent ensemble for MOEX analysis
- 5 OpenCode Zen free models as specialized analysts
- Target: SBER, GAZP, LKOH, SBERP, VTBR
- Source: MOEX ISS API (free, no key)

## Structure

```
/scripts/
  collect_moex_data.py    — Python data collector (MOEX ISS + RSS)
  run_hedge_fund.sh       — Bash orchestrator (parallel analysts + CIO)

/personas/
  fundamental_analyst.txt  — Big Pickle Med prompt (value investing)
  news_analyst.txt         — Deepseek V4 Flash prompt (sentiment)
  technical_analyst.txt    — Mimo V2.5 prompt (technical analysis)
  quant_analyst.txt        — North Mini Code prompt (quant metrics)
  arbiter.txt              — Nemotron 3 Ultra prompt (CIO synthesis)

/data/
  moex_data_*.json         — Cached market data (gitignored)
```

## Running

```bash
# Full pipeline
python scripts/collect_moex_data.py --output data/market.json
bash scripts/run_hedge_fund.sh --data data/market.json

# Reuse cached data
bash scripts/run_hedge_fund.sh --no-collect
```

## Rules for AI Agents

1. **Do NOT modify persona files** without explicit user request — they encode investment philosophies
2. **Run.sh trap cleans temp files** — don't add manual cleanup
3. **MOEX ISS has a 500-candle limit per request** — the collector handles day iteration
4. **`--output` must come BEFORE subcommand** in moex_iss.py: `moex_iss.py --output json candles TICKER`
5. **Test data collector first**, then run the full pipeline
6. **Check liquidity hours**: MOEX 10:00-18:45 MSK weekdays only
7. **Leak-check before any push**: grep for Windows paths (`C:\`, `C:\\Users`), emails, tokens

## Model IDs

| Model | CLI name |
|-------|----------|
| Big Pickle Med | `opencode/big-pickle` |
| Deepseek V4 Flash | `opencode/deepseek-v4-flash-free` |
| Mimo V2.5 | `opencode/mimo-v2.5-free` |
| North Mini Code | `opencode/north-mini-code-free` |
| Nemotron 3 Ultra | `opencode/nemotron-3-ultra-free` |
