# MOEX AI Hedge Fund — Architecture

## Pipeline Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ MOEX ISS API │  │ MOEX News    │  │ RSS Feeds        │  │
│  │ (quotes,     │  │ (биржевые    │  │ (SmartLab,       │  │
│  │  candles,    │  │  уведомления)│  │  ПРАЙМ, Интерфакс)│  │
│  │  indices)    │  │              │  │                  │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│         └─────────────────┼────────────────────┘            │
│                           ▼                                 │
│               ┌──────────────────────┐                      │
│               │  collect_moex_data.py │  (28KB ~ 75 свечей) │
│               └──────────┬───────────┘                      │
│                          │ data/moex_data.json              │
└──────────────────────────┼──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ANALYST LAYER (COUNCIL)                   │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │    PARALLEL (4 hermes chat processes, via     │          │
│  │    ThreadPoolExecutor in run_hedge_fund.py)   │          │
│  │                                              │          │
│  │  ┌────────────────┐  ┌────────────────┐     │          │
│  │  │ 🧮 Fundamental │  │ 🔬 News        │     │          │
│  │  │ big-pickle    │  │ Deepseek V4    │     │          │
│  │  │ 70B + persona  │  │ 284B + persona │     │          │
│  │  └────────┬───────┘  └────────┬───────┘     │          │
│  │           │                   │              │          │
│  │  ┌────────┴───────┐  ┌────────┴───────┐     │          │
│  │  │ 📈 Technical   │  │ ⚙️ Quant       │     │          │
│  │  │ Mimo V2.5      │  │ Deepseek V4    │     │          │
│  │  │ 7B + persona   │  │ 284B + persona │     │          │
│  │  └────────┬───────┘  └────────┬───────┘     │          │
│  └───────────┼──────────────────┼──────────────┘          │
│              │                  │                          │
└──────────────┼──────────────────┼──────────────────────────┘
               │                  │
               ▼                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    ARBITER LAYER (CIO)                       │
│                                                             │
│  ┌──────────────────────────────────────────────┐          │
│  │        👑 Nemotron 3 Ultra (550B)             │          │
│  │        Fallback: Deepseek V4 Flash (284B)    │          │
│  │                                              │          │
│  │  Rules: 3/4 consensus → BUY/SELL             │          │
│  │         2-2 split       → HOLD               │          │
│  │         Max 30% per position                 │          │
│  └─────────────────────┬────────────────────────┘          │
│                        │                                     │
└────────────────────────┼──────────────────────────────────────┘
                         ▼
┌───────────────────────────────────────────────────────────────┐
│                     OUTPUT LAYER                               │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  CIO SIGNAL: Table + Verdict + Allocation + Risk       │   │
│  │                                                        │   │
│  │  TICKER │ PRICE │ SIGNAL │ CONFIDENCE │ RISK           │   │
│  │  SBER   │ 295.8 │ HOLD   │ 59%        │ 3/5            │   │
│  │  GAZP   │ 93.5  │ SELL   │ 65%        │ 4/5            │   │
│  │  LKOH   │ 4472  │ BUY    │ 65%        │ 3/5            │   │
│  │  SBERP  │ 296.4 │ HOLD   │ 48%        │ 3/5            │   │
│  │  VTBR   │ 64.4  │ HOLD   │ 56%        │ 5/5            │   │
│  └────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

> **Note:** Default OpenCode Zen models are shown above. In `run_hedge_fund.py` each role maps to whatever model you configure via `--default-model` / `--analyst-model ROLE=MODEL` (or the model in `~/.hermes/config.yaml`). The Quant role originally used North Mini Code (~1-3B) but it was replaced with Deepseek V4 Flash (284B) — the small model produced garbage output.

## Data Flow

```
Step 1: COLLECT
   python collect_moex_data.py --tickers SBER,GAZP,LKOH,SBERP,VTBR
   │
   ├── Portfolio   → live prices (MOEX ISS)
   ├── Candles     → 14d OHLCV per ticker (~75 candles)
   ├── MOEX News   → ~50 биржевых уведомлений
   ├── RSS Feeds   → per-ticker (SmartLab, Finam, 1prime, Interfax, ...)
   └── Indices     → IMOEX, RTSI, MOEXBC

Step 2: ANALYZE (parallel via ThreadPoolExecutor)
   for each analyst (fundamental, news, technical, quant):
       prompt = persona_{role}.txt + moex_data.json
       hermes chat -q "$prompt" -m {model} -t '' --cli --yolo --ignore-rules -Q

Step 3: SYNTHESIZE
   prompt = arbiter.txt + all_analyses.txt + moex_data.json
   hermes chat -q "$prompt" -m {arbiter_model} -t '' --cli --yolo --ignore-rules -Q

Step 4: OUTPUT
   CIO Signal → stdout + data/hedge_fund_report_*.md
```

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Council mode** (parallel) | Analysts are independent — no sequential dependency |
| **`-q` prompt flag** for hermes chat | Single-query, non-interactive; avoids TTY and stdin ambiguity |
| **`-t ''` empty toolset** | Models answer as text only — no tool calls that could derail analysis |
| **`--ignore-rules`** | Don't inject AGENTS.md/memory into analyst prompts — clean persona-only context |
| **Nemotron as arbiter** | 550B = best for synthesis, but fallback to Deepseek |
| **Persona files** | Separates prompt engineering from orchestration logic |
| **`tempfile.mkdtemp` + `atexit`** | Auto-cleanup of analyst output dirs on exit |
| **ThreadPoolExecutor** | Native Python parallelism for the 4 analyst `hermes chat` calls |

## Error Handling

```
Analyst failure → continue others → mark as abstain in arbiter
RSS unavailable → skip ticker's RSS, note in arbiter context
MOEX ISS down → data collector timeout → abort pipeline
hermes chat 401 → check ~/.hermes/config.yaml model + provider billing
```
