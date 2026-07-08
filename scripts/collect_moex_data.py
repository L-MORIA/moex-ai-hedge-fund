#!/usr/bin/env python3
"""collect_moex_data.py — Сбор данных с MOEX для AI Hedge Fund.

Собирает: портфель, свечи, новости, RSS, индексы.
Сохраняет в JSON для передачи opencode-агентам.

Usage:
  python collect_moex_data.py --tickers SBER,GAZP,LKOH,SBERP,VTBR
  python collect_moex_data.py --output data/moex_data.json
  python collect_moex_data.py --hours 72  # RSS за 72ч
"""

import argparse, datetime, json, os, sys, subprocess, tempfile, textwrap

# Путь к moex-iss скриптам (установленный skill)
SKILL_DIR = os.path.expanduser("~/.hermes/skills/moex-iss")
MOEX_SCRIPT = os.path.join(SKILL_DIR, "scripts", "moex_iss.py")
RSS_SCRIPT = os.path.join(SKILL_DIR, "scripts", "rss_market_news.py")

DEFAULT_TICKERS = "SBER,GAZP,LKOH,SBERP,VTBR"
CANDLE_DAYS = 14


def run(cmd, timeout=30):
    """Запуск команды, возврат stdout."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"


def main():
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

    tickers = [t.strip().upper() for t in args.tickers.split(",")]
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

    data = {
        "meta": {
            "collected_at": datetime.datetime.now().isoformat(),
            "tickers": tickers,
            "source": "MOEX ISS + RSS feeds",
        },
        "portfolio": None,
        "candles": {},
        "moex_news": None,
        "rss_news": None,
        "indices": None,
    }

    # 1. Портфель (все тикеры разом)
    print("[1/6] Portfolio...", file=sys.stderr)
    out = run(["python", MOEX_SCRIPT, "portfolio", args.tickers])
    data["portfolio"] = out.strip()

    # 2. Свечи по каждому тикеру (за candle_days, ежедневные)
    # ВАЖНО: --output ДО подкоманды (argparse quirk)
    for t in tickers:
        print(f"[2/6] Candles {t} ({args.candle_days}d)...", file=sys.stderr)
        out = run(["python", MOEX_SCRIPT, "--output", "json",
                    "candles", t,
                    "--interval", "24", "--days", str(args.candle_days)], timeout=30)
        try:
            data["candles"][t] = json.loads(out) if out.strip() else []
        except json.JSONDecodeError:
            data["candles"][t] = out.strip()

    # 3. Новости MOEX
    print("[3/6] MOEX News...", file=sys.stderr)
    out = run(["python", MOEX_SCRIPT, "news", "--days", "2", "--limit", "20"])
    data["moex_news"] = out.strip()

    # 4. RSS по тикерам
    print(f"[4/6] RSS feeds ({args.rss_hours}h)...", file=sys.stderr)
    out = run(["python", RSS_SCRIPT, "--hours", str(args.rss_hours),
               "--tickers", args.tickers, "--json"], timeout=45)
    try:
        data["rss_news"] = json.loads(out) if out.strip() else []
    except json.JSONDecodeError:
        data["rss_news"] = out.strip()

    # 5. Индексы
    print("[5/6] Indices...", file=sys.stderr)
    out = run(["python", MOEX_SCRIPT, "indices"])
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
