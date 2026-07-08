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
  commands: [python, opencode]
  skills: [moex-iss]
  pip_packages: [requests]
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

| Роль | Модель | Вес | Философия |
|------|--------|------|-----------|
| 🧮 **Фундаментальный** | `opencode/big-pickle` | 70B | Value investing (Баффет + РФ) |
| 🔬 **Новостной (RSS)** | `opencode/deepseek-v4-flash-free` | 284B | Сантимент, event-driven (Сорос) |
| 📈 **Технический** | `opencode/mimo-v2.5-free` | 7B | Тренды, паттерны (Принг) |
| ⚙️ **Квант** | `opencode/deepseek-v4-flash-free` | 284B | Статистика, скрининг (Саймонс) |
| 👑 **CIO / Арбитр** | `opencode/nemotron-3-ultra-free` | 550B | Синтез, риск (Далио) |

> **Note:** Quant изначально был `north-mini-code-free` (~1-3B), но оказался слишком слаб для аналитики (146 байт мусора вместо разбора данных). Заменён на Deepseek V4 Flash (284B). Diversity между News и Quant обеспечивается разными промптами, а не архитектурой модели.

## Установка

```bash
hermes skills install moex-ai-hedge-fund
```

## Использование

```bash
# Полный прогон (сбор → 5 моделей → сигнал)
cd ~/.hermes/skills/moex-ai-hedge-fund
bash scripts/run_hedge_fund.sh

# Сбор данных без opencode
python scripts/collect_moex_data.py

# Использовать ранее сохранённые данные (без повторного сбора)
bash scripts/run_hedge_fund.sh --no-collect

# Свои тикеры
bash scripts/run_hedge_fund.sh --tickers SBER,GAZP
```

## Структура файлов

```
moex-ai-hedge-fund/
├── SKILL.md
├── scripts/
│   ├── collect_moex_data.py
│   └── run_hedge_fund.sh
├── personas/
│   ├── fundamental_analyst.txt
│   ├── news_analyst.txt
│   ├── technical_analyst.txt
│   ├── quant_analyst.txt
│   └── arbiter.txt
├── references/
│   └── windows-bat-bash-paths.md
└── data/
    └── moex_data_*.json
```

## Скрипты

### collect_moex_data.py

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
8. **`timeout` не использовать в .bat→bash контексте** — при запуске bash из `.bat` `timeout` резолвится в Windows `TIMEOUT` (другой синтаксис), а не в GNU `/usr/bin/timeout`. В скрипте `timeout` отсутствует — если opencode завис, закройте окно. См. `references/gnu-timeout-vs-windows.md`.
