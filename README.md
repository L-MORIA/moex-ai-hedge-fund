# MOEX AI Hedge Fund

> Multi-agent ensemble for MOEX analysis (SBER, GAZP, LKOH, SBERP, VTBR) using 5 free OpenCode Zen models as specialized investment analysts.

---

## 🇬🇧 English

### Overview

MOEX AI Hedge Fund is a **multi-agent ensemble** that adapts the AI Hedge Fund concept for the Moscow Exchange. Five free OpenCode Zen models act as specialized investment analysts, each with a distinct philosophy:

| Role | Model | Weight | Philosophy |
|------|-------|--------|------------|
| 🧮 **Fundamental Analyst** | `opencode/big-pickle` | 70B | Value investing (Buffett) |
| 🔬 **News Analyst** | `opencode/deepseek-v4-flash-free` | 284B | Sentiment/event-driven (Soros) |
| 📈 **Technical Analyst** | `opencode/mimo-v2.5-free` | 7B | Trends/patterns (Pring) |
| ⚙️ **Quant Analyst** | `opencode/north-mini-code-free` | ~1-3B | Statistics/screening (Simons) |
| 👑 **CIO / Arbiter** | `opencode/nemotron-3-ultra-free` | 550B | Synthesis/risk (Dalio) |

### Quick Start

```bash
# Clone
git clone https://github.com/L-MORIA/moex-ai-hedge-fund.git
cd moex-ai-hedge-fund

# Full run (data → 4 analysts → CIO)
python scripts/collect_moex_data.py --output data/market.json
bash scripts/run_hedge_fund.sh --data data/market.json

# Or just use the shortcut (Windows)
# Double-click 'MOEX AI Hedge Fund.lnk' on Desktop
```

### Requirements

- **moex-iss** skill (for MOEX ISS data collection)
- **opencode** CLI (for running OpenCode Zen models)
- Python 3.8+ with `requests`

---

## 🇷🇺 Русский

### Обзор

MOEX AI Hedge Fund — это **мульти-агентный ансамбль**, адаптация концепции AI Hedge Fund под Московскую Биржу. Пять бесплатных моделей OpenCode Zen выступают в роли специализированных инвест-аналитиков:

| Роль | Модель | Вес | Философия |
|------|--------|------|-----------|
| 🧮 **Фундаментальный аналитик** | `opencode/big-pickle` | 70B | Стоимостное инвестирование (Баффет) |
| 🔬 **Новостной аналитик** | `opencode/deepseek-v4-flash-free` | 284B | Сантимент/event-driven (Сорос) |
| 📈 **Технический аналитик** | `opencode/mimo-v2.5-free` | 7B | Тренды/паттерны (Принг) |
| ⚙️ **Квант-аналитик** | `opencode/north-mini-code-free` | ~1-3B | Статистика/скрининг (Саймонс) |
| 👑 **CIO / Арбитр** | `opencode/nemotron-3-ultra-free` | 550B | Синтез/риск-менеджмент (Далио) |

### Быстрый старт

```bash
# Клонирование
git clone https://github.com/L-MORIA/moex-ai-hedge-fund.git
cd moex-ai-hedge-fund

# Полный прогон (данные → 4 аналитика → CIO)
python scripts/collect_moex_data.py --output data/market.json
bash scripts/run_hedge_fund.sh --data data/market.json

# Или ярлык на рабочем столе (Windows)
# Двойной клик по 'MOEX AI Hedge Fund.lnk'
```

### Требования

- Скил **moex-iss** (для сбора данных MOEX ISS)
- **opencode** CLI (для запуска моделей OpenCode Zen)
- Python 3.8+ с `requests`

### Пример сигнала (08.07.2026)

```
TICKER │ PRICE   │ SIGNAL │ CONFIDENCE
SBER   │ 295.8   │ HOLD   │ 59%
GAZP   │ 93.5    │ SELL   │ 65%
LKOH   │ 4472    │ BUY    │ 65%    ← consensus (4/4)
SBERP  │ 296.4   │ HOLD   │ 48%
VTBR   │ 64.4    │ HOLD   │ 56%
```
