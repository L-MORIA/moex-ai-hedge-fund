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
│  │         PARALLEL (4 opencode processes)       │          │
│  │                                              │          │
│  │  ┌────────────────┐  ┌────────────────┐     │          │
│  │  │ 🧮 Fundamental │  │ 🔬 News        │     │          │
│  │  │ Big Pickle Med │  │ Deepseek V4    │     │          │
│  │  │ 70B + persona  │  │ 284B + persona │     │          │
│  │  └────────┬───────┘  └────────┬───────┘     │          │
│  │           │                   │              │          │
│  │  ┌────────┴───────┐  ┌────────┴───────┐     │          │
│  │  │ 📈 Technical   │  │ ⚙️ Quant       │     │          │
│  │  │ Mimo V2.5      │  │ North Mini Code│     │          │
│  │  │ 7B + persona   │  │ ~1-3B + persona│     │          │
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

## Data Flow

```
Step 1: COLLECT
   python collect_moex_data.py --tickers SBER,GAZP,LKOH,SBERP,VTBR
   │
   ├── Portfolio   → live prices (MOEX ISS)
   ├── Candles     → 14d OHLCV per ticker (~75 candles)
   ├── MOEX News   → ~50 биржевых уведомлений
   ├── RSS Feeds   → SmartLab, ПРАЙМ, Интерфакс, Investing.com
   └── Indices     → IMOEX, RTSI, MOEXBC

Step 2: ANALYZE (parallel)
   for each analyst (fundamental, news, technical, quant):
       cat persona_{role}.txt data.json | opencode run --model {model}
   
Step 3: SYNTHESIZE
   cat arbiter.txt all_analyses.txt | opencode run --model opencode/nemotron-3-ultra-free

Step 4: OUTPUT
   CIO Signal → stdout
```

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| **Council mode** (parallel) | Analysts are independent — no sequential dependency |
| **stdin pipe** for data | Avoids file I/O races in parallel processes |
| **Nemotron as arbiter** | 550B = best for synthesis, but fallback to Deepseek |
| **Persona files** | Separates prompt engineering from orchestration logic |
| **mktemp for analyst outputs** | Cleanup via `trap EXIT` — no temp file leaks |
| **& + wait parallelism** | Native bash, no external orchestration needed |

## Error Handling

```
Analyst failure → continue others → mark as abstain in arbiter
Nemotron timeout → auto-fallback to Deepseek V4 Flash
RSS unavailable → skip, note in arbiter context
MOEX ISS down → data collector timeout → abort pipeline
```
