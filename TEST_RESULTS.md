# Test Results

## Test 1: Data Collection — 2026-07-08

**Command:** `python collect_moex_data.py --tickers SBER,GAZP,LKOH,SBERP,VTBR --candle-days 14 --rss-hours 48`

| Metric | Result |
|--------|--------|
| File size | 28,732 bytes |
| Tickers | SBER, GAZP, LKOH, SBERP, VTBR |
| Candles total | 75 (~15 per ticker × 14 days) |
| Portfolio | ✅ 5 live prices from MOEX ISS |
| MOEX News | ~50 entries (2 days) |
| RSS Feeds | 4 sources accessible (0 ticker-specific matches) |
| Indices | IMOEX, RTSI, MOEXBC, MOEXOG, MOEXFN, MOEXMM... |
| Duration | ~30 seconds |
| Errors | 0 |

## Test 2: Full Pipeline (Council Mode) — 2026-07-08

**Command:** `bash scripts/run_hedge_fund.sh --data data/live_test.json`

**Models tested:**

| Model | Role | Status |
|-------|------|--------|
| `opencode/big-pickle` (70B) | 🧮 Fundamental | ✅ Completed |
| `opencode/deepseek-v4-flash-free` (284B) | 🔬 News | ✅ Completed |
| `opencode/mimo-v2.5-free` (7B) | 📈 Technical | ✅ Completed |
| `opencode/north-mini-code-free` (~1-3B) | ⚙️ Quant | ✅ Completed |
| `opencode/nemotron-3-ultra-free` (550B) | 👑 CIO | ✅ Completed (no timeout) |

**Duration:** ~3 minutes (4 parallel + 1 sequential)

### CIO Signal

```
┌─────────────────────────────────────────────────┐
│ TICKER │ PRICE   │ SIGNAL │ CONFIDENCE │ RISK   │
├─────────────────────────────────────────────────┤
│ SBER   │ 295.8   │ HOLD   │ 59%        │ 3/5   │
│ GAZP   │ 93.5    │ SELL   │ 65%        │ 4/5   │
│ LKOH   │ 4472    │ BUY    │ 65%        │ 3/5   │
│ SBERP  │ 296.4   │ HOLD   │ 48%        │ 3/5   │
│ VTBR   │ 64.4    │ HOLD   │ 56%        │ 5/5   │
└─────────────────────────────────────────────────┘
```

### Consensus Matrix

| Ticker | 🧮 Fundamental | 🔬 News | 📈 Technical | ⚙️ Quant | CIO |
|--------|:-------------:|:------:|:-----------:|:-------:|:--:|
| SBER   | HOLD | SELL | HOLD | ✅ BUY | **HOLD** 59% |
| GAZP   | ❌ SELL | ❌ SELL | ❌ SELL | ❌ SELL | **SELL** 65% ✅ |
| LKOH   | ✅ BUY | ✅ BUY | ✅ BUY | ✅ BUY | **BUY** 65% ✅ |
| SBERP  | HOLD | SELL | HOLD | HOLD | **HOLD** 48% |
| VTBR   | SELL | HOLD | HOLD | SELL | **HOLD** 56% |

### Consensus Achieved
- **LKOH BUY** — 4/4 analysts agree ✅
- **GAZP SELL** — 4/4 analysts agree ✅
- **SBER, SBERP, VTBR** — split votes → HOLD

### Risks Identified
1. 50% concentration in Sberbank (SBER+SBERP) — sector risk below 290 support
2. VTBR capitulation volume (577M) — risk of renewed selling
3. GAZP at 0% weight — opportunity cost if reversal

## Test 3: Data Collector Argument Order — 2026-07-08

**Issue:** `--output` must be placed BEFORE the subcommand in moex_iss.py (`moex_iss.py --output json candles TICKER`, not `moex_iss.py candles TICKER --output json`).

**Fix applied:** Updated `collect_moex_data.py` to use correct argument order.
**Verification:** Candles returned correctly (75 entries).

## Test Environment

- **OS:** Windows 10 (git-bash)
- **Python:** 3.11.9
- **Hermes:** TUI session
- **opencode:** 1.17.4
- **OpenCode Zen:** Free tier (all 5 models available)
- **MOEX ISS:** Public API (no auth)
- **CPU:** i5-3337U, 8GB DDR3
