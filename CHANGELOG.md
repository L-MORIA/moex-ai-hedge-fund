# Changelog

## [1.0.0] — 2026-07-08

### Added
- Initial release: MOEX AI Hedge Fund
- `collect_moex_data.py` — data collector (MOEX ISS portfolio, candles, news, RSS, indices)
- `run_hedge_fund.sh` — bash orchestrator with 3 modes (council, pipeline, hybrid)
- 5 persona files for OpenCode Zen models:
  - `fundamental_analyst.txt` (Big Pickle Med — value investing)
  - `news_analyst.txt` (Deepseek V4 Flash — sentiment analysis)
  - `technical_analyst.txt` (Mimo V2.5 — technical analysis)
  - `quant_analyst.txt` (North Mini Code — quant metrics)
  - `arbiter.txt` (Nemotron 3 Ultra — CIO synthesis)
- Desktop shortcut for Windows (`MOEX AI Hedge Fund.lnk`)
- Documentation: README, ARCHITECTURE, AGENTS, CHANGELOG, TEST_RESULTS
- Verified end-to-end: 5 models, 5 tickers, 14 days of data
