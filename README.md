# MOEX AI Hedge Fund

> Multi-agent ensemble for MOEX analysis (SBER, GAZP, LKOH, SBERP, VTBR). Four analyst roles + a CIO arbiter, mapped to your own LLM providers via the `hermes` CLI.

---

## 🇬🇧 English

### Overview

MOEX AI Hedge Fund is a **multi-agent ensemble** that adapts the AI Hedge Fund concept for the Moscow Exchange. Four analyst roles plus a CIO arbiter, each with a distinct investment philosophy. The Python orchestrator (`run_hedge_fund.py`) calls models through the `hermes` CLI, so you can use any provider you have configured (OpenRouter, Ollama, OpenCode Zen, etc.).

| Role | Default opencode Zen model | Philosophy |
|------|-------|------------|
| 🧮 **Fundamental Analyst** | `opencode/big-pickle` (70B) | Value investing (Buffett) |
| 🔬 **News Analyst** | `opencode/deepseek-v4-flash-free` (284B) | Sentiment/event-driven (Soros) |
| 📈 **Technical Analyst** | `opencode/mimo-v2.5-free` (7B) | Trends/patterns (Pring) |
| ⚙️ **Quant Analyst** | `opencode/deepseek-v4-flash-free` (284B) | Statistics/screening (Simons) |
| 👑 **CIO / Arbiter** | `opencode/nemotron-3-ultra-free` (550B) | Synthesis/risk (Dalio) |

> **Note:** The Quant role originally used `opencode/north-mini-code-free` (~1-3B) but it was too weak for analysis and was replaced with Deepseek V4 Flash. News vs Quant diversity comes from different prompts. To use your own models, see `--default-model` / `--analyst-model ROLE=MODEL` in `run_hedge_fund.py`.

### Quick Start

```bash
# Clone
git clone https://github.com/L-MORIA/moex-ai-hedge-fund.git
cd moex-ai-hedge-fund

# Recommended: Python orchestrator (uses hermes CLI — any provider)
python scripts/run_hedge_fund.py --tickers SBER,GAZP,LKOH,SBERP,VTBR

# Legacy: Bash orchestrator (requires opencode CLI + OpenCode Zen account)
bash scripts/run_hedge_fund.sh
```

### Requirements

- **moex-iss** skill (for MOEX ISS data collection)
- **hermes** CLI (for the Python orchestrator) — configure your model in `~/.hermes/config.yaml`
- Python 3.8+

---

## 🇷🇺 Русский

### Обзор

MOEX AI Hedge Fund — это **мульти-агентный ансамбль**, адаптация концепции AI Hedge Fund под Московскую Биржу. Четыре роли аналитиков плюс CIO-арбитр, каждая со своей инвестиционной философией. Python-оркестратор (`run_hedge_fund.py`) вызывает модели через `hermes` CLI — можно использовать любой настроенный провайдер (OpenRouter, Ollama, OpenCode Zen и т.д.).

| Роль | Модель OpenCode Zen по умолчанию | Философия |
|------|--------|-----------|
| 🧮 **Фундаментальный аналитик** | `opencode/big-pickle` (70B) | Стоимостное инвестирование (Баффет) |
| 🔬 **Новостной аналитик** | `opencode/deepseek-v4-flash-free` (284B) | Сантимент/event-driven (Сорос) |
| 📈 **Технический аналитик** | `opencode/mimo-v2.5-free` (7B) | Тренды/паттерны (Принг) |
| ⚙️ **Квант-аналитик** | `opencode/deepseek-v4-flash-free` (284B) | Статистика/скрининг (Саймонс) |
| 👑 **CIO / Арбитр** | `opencode/nemotron-3-ultra-free` (550B) | Синтез/риск-менеджмент (Далио) |

> **Примечание:** Роль Quant изначально использовала `opencode/north-mini-code-free` (~1-3B), но модель оказалась слишком слабой для анализа и заменена на Deepseek V4 Flash. Diversity между News и Quant обеспечивается разными промптами. Чтобы использовать свои модели — см. `--default-model` / `--analyst-model ROLE=MODEL` в `run_hedge_fund.py`.

### Быстрый старт

```bash
# Клонирование
git clone https://github.com/L-MORIA/moex-ai-hedge-fund.git
cd moex-ai-hedge-fund

# Рекомендуется: Python-оркестратор (через hermes CLI — любой провайдер)
python scripts/run_hedge_fund.py --tickers SBER,GAZP,LKOH,SBERP,VTBR

# Legacy: Bash-оркестратор (требует opencode CLI и аккаунт OpenCode Zen)
bash scripts/run_hedge_fund.sh
```

### Требования

- Скил **moex-iss** (для сбора данных MOEX ISS)
- **hermes** CLI (для Python-оркестратора) — настройте модель в `~/.hermes/config.yaml`
- Python 3.8+

### Пример сигнала (08.07.2026)

```
TICKER │ PRICE   │ SIGNAL │ CONFIDENCE
SBER   │ 295.8   │ HOLD   │ 59%
GAZP   │ 93.5    │ SELL   │ 65%
LKOH   │ 4472    │ BUY    │ 65%    ← consensus (4/4)
SBERP  │ 296.4   │ HOLD   │ 48%
VTBR   │ 64.4    │ HOLD   │ 56%
```
