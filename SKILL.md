---
name: moex-ai-hedge-fund
description: >-
  MOEX AI Hedge Fund — multi-agent ensemble для анализа MOEX (SBER, GAZP, LKOH, SBERP, VTBR)
  через 5 бесплатных OpenCode Zen моделей с разными инвестиционными философиями.
version: 1.0.1
author: L-MORIA
tags: [moex, ai-hedge-fund, multi-agent, ensemble, trading, finance]
platforms: [windows]
prerequisites:
  commands: [python, hermes]
  skills: [moex-iss]
  pip_packages: []
metadata:
  hermes:
    related_skills: [moex-iss, hermes-multi-agent-orchestrator, llm-ensemble, kronos-signal]
---

# MOEX AI Hedge Fund

> Адаптация AI Hedge Fund (ClawHub) под MOEX + ваши 5 бесплатных моделей OpenCode Zen.

## Концепция

Каждая из 5 OpenCode Zen моделей назначается в роль «инвест-аналитика» со своей философией. Собираются реальные данные с MOEX → каждый аналитик выдаёт свой анализ + сигнал → Арбитр (Nemotron 3 Ultra) синтезирует итоговый сигнал.

```
📡 Сбор данных MOEX (портфель, свечи, новости, RSS, индексы)
        │
        ├── 🧮 Big Pickle Med      — Фундаментальный аналитик
        ├── 🔬 Deepseek V4 Flash   — Новостной аналитик
        ├── 📈 Mimo V2.5           — Технический аналитик
        ├── ⚙️ Deepseek V4 Flash   — Квант-аналитик
        │
        └── 👑 Nemotron 3 Ultra    — CIO / Арбитр
                    │
                    ▼
         BUY/SELL/HOLD + обоснование + уверенность
```

## Аналитики и их модели

**Дефолтный маппинг (оригинал, требует opencode CLI):**

| Роль | Модель | Вес | Философия |
|------|--------|------|-----------|
| 🧮 **Фундаментальный** | `opencode/big-pickle` | 70B | Value investing (Баффет + РФ) |
| 🔬 **Новостной (RSS)** | `opencode/deepseek-v4-flash-free` | 284B | Сантимент, event-driven (Сорос) |
| 📈 **Технический** | `opencode/mimo-v2.5-free` | 7B | Тренды, паттерны (Принг) |
| ⚙️ **Квант** | `opencode/deepseek-v4-flash-free` | 284B | Статистика, скрининг (Саймонс) |
| 👑 **CIO / Арбитр** | `opencode/nemotron-3-ultra-free` | 550B | Синтез, риск (Далио) |

> **Note:** Quant изначально был `north-mini-code-free` (~1-3B), но оказался слишком слаб для аналитики (146 байт мусора вместо разбора данных). Заменён на Deepseek V4 Flash (284B). Diversity между News и Quant обеспечивается разными промптами, а не архитектурой модели.

**Для Windows (через hermes CLI):** используй `--default-model` и `--analyst-model` чтобы мапить на свои провайдеры. Например:

```bash
python scripts/run_hedge_fund.py --tickers SBERP \
    --default-model ollama-cloud/llama-3.3-70b-instruct
```

> **⚠️ Прямой HTTP к opencode.ai/zen не работает** — бесплатные модели доступны только через `opencode` CLI, не через прямые запросы. Python-версия использует `hermes chat -m MODEL` для вызова моделей.

## Установка

```bash
pip install requests  # если нужен run_hedge_fund.sh (opencode CLI)
```

**Зависимости:** Python 3.8+, `moex-iss` skill установлен.

## Использование

### Вариант 1: Python оркестратор через hermes CLI (рекомендуется для Windows)

```bash
# Полный прогон (сбор → 4 аналитика → Арбитр) с текущей моделью hermes
python scripts/run_hedge_fund.py --tickers SBERP

# Или через .bat
hedge_fund.bat

# Pipeline (последовательно) вместо council (параллельно)
python scripts/run_hedge_fund.py --mode pipeline --tickers SBERP

# Использовать ранее сохранённые данные
python scripts/run_hedge_fund.py --no-collect

# Конкретный файл данных
python scripts/run_hedge_fund.py --data data/moex_data.json

# Только конкретные аналитики
python scripts/run_hedge_fund.py --analysts technical,fundamental

# Разные модели для разных ролей (если у тебя openrouter/ollama)
python scripts/run_hedge_fund.py \
    --default-model openrouter/deepseek/deepseek-chat-v3 \
    --analyst-model technical=openrouter/qwen/qwen-2.5-coder-32b-instruct \
    --analyst-model fundamental=openrouter/anthropic/claude-3.5-sonnet
```

**Архитектура:** Python-скрипт вызывает `hermes chat -q PROMPT -m MODEL -t '' --cli --yolo --ignore-rules -Q` для каждой роли. Промпт = persona + MOEX data. Council mode запускает 4 роли параллельно через ThreadPoolExecutor. Арбитр — отдельная роль (`--analyst-model arbiter=MODEL`), не наследуется от fundamental.

### Вариант 2: Bash с opencode CLI (оригинал, требует opencode)

```bash
bash scripts/run_hedge_fund.sh
```

## Структура файлов

```
moex-ai-hedge-fund/
├── SKILL.md
├── hedge_fund.bat                   # Windows launcher (.bat)
├── hedge_fund_pipeline.bat          # Pipeline mode launcher
├── scripts/
│   ├── collect_moex_data.py         # Сбор данных (только данные)
│   ├── run_hedge_fund.py            # Python оркестратор (БЕЗ opencode CLI)
│   └── run_hedge_fund.sh            # Bash вариант (требует opencode CLI)
├── personas/
│   ├── fundamental_analyst.txt
│   ├── news_analyst.txt
│   ├── technical_analyst.txt
│   ├── quant_analyst.txt
│   └── arbiter.txt
├── references/
│   └── windows-bat-bash-paths.md
└── data/
    ├── moex_data_*.json             # Собранные данные
    └── hedge_fund_report_*.md       # Итоговые отчёты
```

## Скрипты

### `collect_moex_data.py`

Собирает портфель, OHLCV-свечи (14d), новости MOEX, RSS-ленты, индексы.

```bash
python scripts/collect_moex_data.py --tickers SBER,GAZP,LKOH,SBERP,VTBR
python scripts/collect_moex_data.py --candle-days 7 --rss-hours 24
python scripts/collect_moex_data.py --output data/mydata.json
```

### run_hedge_fund.sh

Оркестратор: сбор данных → 4 аналитика (параллельно) → CIO.

```bash
# Совет директоров — режим по умолчанию
bash scripts/run_hedge_fund.sh

# Pipeline — последовательный анализ
bash scripts/run_hedge_fund.sh --mode pipeline
```

**Альтернативный запуск (без opencode CLI):**

```bash
# Через Python оркестратор (hermes CLI — любой провайдер)
python scripts/run_hedge_fund.py
python scripts/run_hedge_fund.py --mode pipeline --tickers SBERP
```

Архитектура Council:
```
        ┌─────────────────────────┐
        │  collect_moex_data.py   │
        └────────┬────────────────┘
                 │ data.json
    ┌────────────┼──────────────────────┐
    ▼            ▼          ▼           ▼
 Big Pickle   Deepseek   Mimo V2.5   Deepseek
 (fundamental) (news)   (technical)  (quant)
     70B        284B       7B         284B
    │            │          │           │
    └────────────┼──────────┼───────────┘
                 ▼
          Nemotron 3 Ultra (550B)
          └─ fallback: Deepseek V4 Flash
                 │
                 ▼
          BUY/SELL/HOLD
```

## Persona-файлы (промпты для моделей)

Каждый промпт задаёт: роль, философию, формат ответа (`TICKER | SIGNAL | CONFIDENCE% | RATIONALE`), правила валидации.

**fundamental_analyst.txt** — мультипликаторы, дивиденды, макро РФ
**news_analyst.txt** — сантимент, триггеры, event-driven
**technical_analyst.txt** — тренды, поддержка/сопротивление, RSI, объёмы
**quant_analyst.txt** — волатильность, корреляция, риск-метрики
**arbiter.txt** — CIO: синтез, взвешенное голосование, аллокация

## Правила CIO (арбитра)

1. **BUY** = минимум 3 из 4 аналитиков BUY, уверенность > 60%
2. **SELL** = минимум 3 из 4 аналитиков SELL, уверенность > 60%
3. **HOLD** = все остальные случаи (в т.ч. 2-2)
4. Максимум 30% в одну бумагу
5. Уверенность CIO = средняя уверенность с поправкой на риск

## Cron-режим

```bash
cronjob action=create schedule='0 10 * * 1-5' name='MOEX AI Hedge Fund' \
  skills='[moex-ai-hedge-fund,moex-iss]' \
  prompt='Запусти MOEX AI Hedge Fund — собери данные по SBER,GAZP,LKOH,SBERP,VTBR, прогони через 5 OpenCode Zen моделей и покажи итоговый сигнал.'
```

## Pitfalls

1. **Windows bat→bash path backslashes** — при запуске `hedge_fund.bat` → `bash run_hedge_fund.sh`, бэкслеши в путях (`data\market.json`) ломают bash. В `.bat` используем `/`, в скрипте `tr '\\' '/'` для защиты. См. `references/windows-bat-bash-paths.md`
2. **MOEX открыт 10:00-18:45 MSK** — запускать не раньше 10:15.
3. **Выходные** — MOEX закрыт. Не запускать в Сб-Вс.
4. **RSS не всегда доступен** — SmartLab, ПРАЙМ, Интерфакс могут быть недоступны. Скрипт обрабатывает ошибки.
5. **Nemotron 3 Ultra может виснуть** на большом контексте — в скрипте fallback на Deepseek V4 Flash.
6. **North Mini Code слаб для аналитики** — заменён на Deepseek в quant-роли. Не использовать для задач, требующих рассуждений.
7. **`--output` ДО подкоманды** — `moex_iss.py --output json candles TICKER`, не `candles TICKER --output json`.
8. **`timeout` не использовать в .bat→bash контексте** — при запуске bash из `.bat` `timeout` резолвится в Windows `TIMEOUT` (другой синтаксис), а не в GNU `/usr/bin/timeout`. В `run_hedge_fund.sh` `timeout` отсутствует — если opencode завис, закройте окно.
9. **`opencode` CLI не установлен** — оригинальный `run_hedge_fund.sh` использует `opencode run --model ...`, который требует установленного opencode CLI. **Решение:** использовать `run_hedge_fund.py` — Python оркестратор, который вызывает модели через `hermes chat -m MODEL`. Доступны все твои провайдеры (ollama-cloud, openrouter и т.д.).
10. **Путь к moex-iss skill зависит от профиля Hermes** — на Windows реальный путь: `%LOCALAPPDATA%\hermes\profiles\<name>\skills\moex-iss` (например `C:\Users\User\AppData\Local\hermes\profiles\old-laptop\skills\moex-iss`). Скрипт автоматически ищет в обеих локациях (LOCALAPPDATA и `.hermes`).
11. **market_news.py — один тикер за раз** — принимает позиционный аргумент (без `--tickers`/`--json`). `collect_moex_data.py` и `run_hedge_fund.py` вызывают его в цикле по каждому тикеру.
12. **hermes chat в фоне** — Python оркестратор запускает 4 `hermes chat` параллельно. Убедись, что твои провайдеры не имеют строгих rate limits. Если есть — используй `--mode pipeline`.
13. **`hermes chat` интерактивен** — для автоматизации используются `--cli --yolo -Q` флаги. Не используйте несуществующие флаги (`-z`).
14. **Прямой HTTP к opencode.ai/zen НЕ работает** — бесплатные модели opencode (`opencode/big-pickle`, `opencode/mimo-v2.5-free`, `opencode/deepseek-v4-flash-free`) возвращают `401 ModelError: not supported` при прямых HTTP-запросах. Доступны ТОЛЬКО через `opencode` CLI. **Решение:** используй свои модели через `hermes chat`.
15. **`hermes chat -m default` не работает** — строка `default` не является валидным model ID. Нужно указать реальный ID из `~/.hermes/config.yaml` (model.model). Если в конфиге стоит `gpt-5.4-pro` с `provider: opencode-zen`, убедитесь что аккаунт оплачен (иначе `HTTP 401: No payment method`). Используйте `--default-model ollama-cloud/llama-3.3-70b-instruct` или другой настроенный провайдер.
16. **Арбитр — отдельная роль** — `--analyst-model fundamental=X` НЕ меняет модель арбитра. Для арбитра: `--analyst-model arbiter=Y`.
