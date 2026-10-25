#!/usr/bin/env python3
"""collect_moex_data.py — Сбор данных с MOEX для AI Hedge Fund.

Собирает: портфель, свечи, новости, RSS, индексы.
Сохраняет в JSON для передачи opencode-агентам.

Usage:
  python collect_moex_data.py --tickers SBER,GAZP,LKOH,SBERP,VTBR
  python collect_moex_data.py --output data/moex_data.json
  python collect_moex_data.py --hours 72  # RSS за 72ч
"""

import argparse, datetime, json, os, subprocess, sys

# Дочерние python-процессы должны писать в stdout UTF-8 независимо от
# локали Windows (иначе кириллица превращается в mojibake при чтении пайпа).
CHILD_ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def find_skill_dir():
    """Ищет skill moex-iss во ВСЕХ профилях hermes (имя профиля не хардкодится)."""
    home = os.path.expanduser("~")
    roots = [
        os.path.join(home, "AppData", "Local", "hermes", "profiles"),
        os.path.join(home, ".hermes", "profiles"),
        os.path.join(home, ".hermes"),
    ]
    for root in roots:
        if not os.path.isdir(root):
            continue
        # прямой путь root/skills/moex-iss (без профиля)
        direct = os.path.join(root, "skills", "moex-iss")
        if os.path.isfile(os.path.join(direct, "scripts", "moex_iss.py")):
            return os.path.normpath(direct)
        # перебираем профили в алфавитном порядке
        try:
            for name in sorted(os.listdir(root)):
                cand = os.path.join(root, name, "skills", "moex-iss")
                if os.path.isfile(os.path.join(cand, "scripts", "moex_iss.py")):
                    return os.path.normpath(cand)
        except OSError:
            continue
    return None

SKILL_DIR = find_skill_dir()
MOEX_SCRIPT = os.path.join(SKILL_DIR, "scripts", "moex_iss.py") if SKILL_DIR else None
RSS_SCRIPT = os.path.join(SKILL_DIR, "scripts", "market_news.py") if SKILL_DIR else None

DEFAULT_TICKERS = "SBER,GAZP,LKOH,SBERP,VTBR"
CANDLE_DAYS = 14


def run(cmd, timeout=30):
    """Запуск python-скрипта moex-iss, возврат stdout (или текст ошибки)."""
    if not cmd or cmd[0] is None:
        return "ERROR: moex-iss skill not found (см. SKILL.md, раздел Установка)"
    try:
        r = subprocess.run([sys.executable] + cmd, capture_output=True, timeout=timeout,
                           encoding="utf-8", errors="replace", env=CHILD_ENV)
        if r.returncode != 0:
            err = (r.stderr or "").strip()[:300]
            return f"ERROR: rc={r.returncode} {err}" if err else f"ERROR: rc={r.returncode}"
        return r.stdout
    except subprocess.TimeoutExpired:
        return f"ERROR: timeout after {timeout}s"
    except Exception as e:
        return f"ERROR: {e}"


def main():
    # Кириллица/emoji в выводе не должны падать при редиректе на Windows (cp1251)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="MOEX Data Collector for AI Hedge Fund")
    ap.add_argument("--tickers", default=DEFAULT_TICKERS,
                    help="Comma-separated tickers (default: %s)" % DEFAULT_TICKERS)
    ap.add_argument("--candle-days", type=int, default=CANDLE_DAYS,
                    help="Days of OHLCV history per ticker")
    ap.add_argument("--rss-hours", type=int, default=48,
                    help="RSS lookback hours")
    ap.add_argument("--output", default=None,
                    help="Output JSON path (default: stdout)")
    args = ap.parse_args()

    if not SKILL_DIR:
        print("ERROR: skill moex-iss не найден. Установите его в "
              "%LOCALAPPDATA%\\hermes\\profiles\\<name>\\skills\\moex-iss "
              "или ~/.hermes/skills/moex-iss", file=sys.stderr)
        sys.exit(2)

    tickers = [t.strip().upper() for t in args.tickers.split(",")]

    data = {
        "meta": {
            "collected_at": datetime.datetime.now().isoformat(),
            "tickers": tickers,
            "source": "MOEX ISS + RSS feeds",
        },
        "portfolio": None,
        "candles": {},
        "moex_news": None,
        "rss_news": {},
        "indices": None,
    }

    # 1. Портфель (все тикеры разом)
    print("[1/6] Portfolio...", file=sys.stderr)
    out = run([MOEX_SCRIPT, "portfolio", args.tickers])
    data["portfolio"] = out.strip()

    # 2. Свечи по каждому тикеру (за candle_days, ежедневные)
    # ВАЖНО: --output ДО подкоманды (argparse quirk)
    for t in tickers:
        print(f"[2/6] Candles {t} ({args.candle_days}d)...", file=sys.stderr)
        out = run([MOEX_SCRIPT, "--output", "json",
                   "candles", t,
                   "--interval", "24", "--days", str(args.candle_days)], timeout=30)
        try:
            data["candles"][t] = json.loads(out) if out.strip() else []
        except json.JSONDecodeError:
            data["candles"][t] = out.strip()

    # 3. Новости MOEX
    print("[3/6] MOEX News...", file=sys.stderr)
    out = run([MOEX_SCRIPT, "news", "--days", "2", "--limit", "20"])
    data["moex_news"] = out.strip()

    # 4. RSS по каждому тикеру отдельно
    # market_news.py принимает ОДИН тикер позиционно (без --tickers/--json).
    # Формат вывода — text. Сохраняем как dict {ticker: text}.
    print(f"[4/6] RSS feeds ({args.rss_hours}h)...", file=sys.stderr)
    for t in tickers:
        print(f"  RSS {t}...", file=sys.stderr)
        out = run([RSS_SCRIPT, t, "--hours", str(args.rss_hours)], timeout=45)
        data["rss_news"][t] = out.strip()

    # 5. Индексы
    print("[5/6] Indices...", file=sys.stderr)
    out = run([MOEX_SCRIPT, "indices"])
    data["indices"] = out.strip()

    # 6. Итоговые тикеры
    print(f"[6/6] Done. {len(tickers)} tickers collected.", file=sys.stderr)

    output = json.dumps(data, ensure_ascii=False, indent=2)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Data saved: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
