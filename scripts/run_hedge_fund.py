#!/usr/bin/env python3
"""run_hedge_fund.py — MOEX AI Hedge Fund оркестратор (Python)

Использует hermes CLI для вызова моделей (а не внешний opencode CLI).
Поддерживает --analyst-model ROLE=PROVIDER/MODEL для маппинга на твои модели.

Usage:
    python scripts/run_hedge_fund.py --tickers SBERP
    python scripts/run_hedge_fund.py --no-collect
    python scripts/run_hedge_fund.py --analyst-model technical=openrouter/deepseek/deepseek-chat-v3
"""
import argparse
import atexit
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# ── Сбор данных ─────────────────────────────────────────────────────────
def find_skill_dir():
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "AppData", "Local", "hermes", "profiles", "old-laptop", "skills", "moex-iss"),
        os.path.join(home, ".hermes", "profiles", "old-laptop", "skills", "moex-iss"),
        os.path.expanduser("~/.hermes/skills/moex-iss"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return os.path.normpath(c)
    return os.path.normpath(candidates[0])


SKILL_DIR = find_skill_dir()
MOEX_SCRIPT = os.path.join(SKILL_DIR, "scripts", "moex_iss.py")
MARKET_NEWS_SCRIPT = os.path.join(SKILL_DIR, "scripts", "market_news.py")

DEFAULT_TICKERS = "SBER,GAZP,LKOH,SBERP,VTBR"

# Дефолтные модели — провайдер hermes должен понимать эти ID.
# "default" означает: брать модель из ~/.hermes/config.yaml (model.model).
# Пользователь может переопределить через --default-model или --analyst-model ROLE=MODEL.
DEFAULT_ANALYSTS = [
    ("fundamental", "default"),
    ("news",        "default"),
    ("technical",   "default"),
    ("quant",       "default"),
]
DEFAULT_ARBITER = "default"  # отдельная роль — не должна зависеть от fundamental


def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout
    except Exception as e:
        return f"ERROR: {e}"


def collect_data(tickers, candle_days, rss_hours, output_path):
    print(f"[1/3] Collecting MOEX data for {tickers}...", file=sys.stderr)
    data = {
        "meta": {
            "collected_at": datetime.datetime.now().isoformat(),
            "tickers": [t.strip().upper() for t in tickers.split(",")],
            "source": "MOEX ISS + RSS feeds",
        },
        "portfolio": None, "candles": {}, "moex_news": None, "rss_news": {}, "indices": None,
    }
    ticker_list = [t.strip().upper() for t in tickers.split(",")]

    data["portfolio"] = run(["python", MOEX_SCRIPT, "portfolio", tickers]).strip()

    for t in ticker_list:
        out = run(["python", MOEX_SCRIPT, "--output", "json",
                   "candles", t, "--interval", "24", "--days", str(candle_days)], timeout=30)
        try:
            data["candles"][t] = json.loads(out) if out.strip() else []
        except json.JSONDecodeError:
            data["candles"][t] = out.strip()

    data["moex_news"] = run(["python", MOEX_SCRIPT, "news", "--days", "2", "--limit", "20"]).strip()

    # market_news.py принимает ОДИН тикер позиционно (не --tickers), без --json.
    # Собираем новости по каждому тикеру отдельно → dict {ticker: text}.
    for t in ticker_list:
        out = run(["python", MARKET_NEWS_SCRIPT, t, "--hours", str(rss_hours)], timeout=60)
        data["rss_news"][t] = out.strip()

    data["indices"] = run(["python", MOEX_SCRIPT, "indices"]).strip()

    output = json.dumps(data, ensure_ascii=False, indent=2)
    if output_path:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"  Data saved: {output_path}", file=sys.stderr)
    return data, output_path


# ── Вызов hermes CLI для получения ответа от модели ───────────────────
def call_hermes_model(model, prompt, timeout=300):
    """Неинтерактивный вызов: hermes chat -q PROMPT -m MODEL -t '' --cli --yolo.

    Флаги:
      -q PROMPT      — промпт как single-query (НЕ stdin, НЕ -z — такого флага нет)
      -m MODEL       — модель из config.yaml или переданная явно
      -t ''          — пустой toolset: модель не вызывает инструменты, только текст
      --cli          — неинтерактивный режим (без TUI)
      --yolo         — без подтверждений
      --ignore-rules — не инжектить AGENTS.md/SOUL.md/memory (чистый промпт)
      -Q             — тихий вывод: только финальный ответ
    """
    cmd = [
        "hermes", "chat",
        "-q", prompt,
        "-m", model,
        "-t", "",
        "--cli", "--yolo", "--ignore-rules", "-Q",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()[:300]
            return f"[HERMES FAILED rc={r.returncode}: {err}]"
        out = r.stdout.strip()
        return out if out else "[HERMES EMPTY RESPONSE]"
    except subprocess.TimeoutExpired:
        return f"[HERMES TIMEOUT after {timeout}s]"
    except FileNotFoundError:
        return "[HERMES ERROR: 'hermes' CLI not found in PATH]"
    except Exception as e:
        return f"[HERMES ERROR: {e}]"


# ── Запуск аналитика ───────────────────────────────────────────────────
def run_analyst(role, model, data_text, output_dir):
    persona_file = os.path.join(os.path.dirname(__file__), "..", "personas", f"{role}_analyst.txt")
    if not os.path.isfile(persona_file):
        return f"[SKIP: Missing persona {persona_file}]"

    with open(persona_file, "r", encoding="utf-8") as f:
        persona_text = f.read()

    full_prompt = f"{persona_text}\n\n=== MOEX DATA ===\n{data_text}"
    print(f"  >> {role} ({model})...", file=sys.stderr)

    response = call_hermes_model(model, full_prompt, timeout=300)
    out_path = os.path.join(output_dir, f"{role}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(response)
    return response


def run_arbiter(model, analyses_text, data_text):
    arbiter_file = os.path.join(os.path.dirname(__file__), "..", "personas", "arbiter.txt")
    if not os.path.isfile(arbiter_file):
        return "[SKIP: Missing arbiter persona]"
    with open(arbiter_file, "r", encoding="utf-8") as f:
        arbiter_prompt = f.read()
    print(f"  >> Arbiter ({model})...", file=sys.stderr)
    full_prompt = f"{arbiter_prompt}\n\n=== ANALYST REPORTS ===\n{analyses_text}\n\n=== MOEX DATA ===\n{data_text}"
    return call_hermes_model(model, full_prompt, timeout=300)


def parse_model_args(model_args, default_model):
    """Парсинг --analyst-model role1=model1 role2=model2 → dict.

    Возвращает маппинг для всех аналитиков + арбитра.
    Арбитр — отдельная роль: не наследует модель от fundamental.
    """
    mapping = {}
    for item in model_args:
        if "=" in item:
            role, m = item.split("=", 1)
            mapping[role.strip()] = m.strip()
    # Заполняем дефолтами: аналитики + arbiter
    result = {role: mapping.get(role, default_model) for role, _ in DEFAULT_ANALYSTS}
    result["arbiter"] = mapping.get("arbiter", default_model)
    return result


def main():
    ap = argparse.ArgumentParser(description="MOEX AI Hedge Fund (Python, через hermes CLI)")
    ap.add_argument("--mode", default="council", choices=["council", "pipeline"])
    ap.add_argument("--tickers", default=DEFAULT_TICKERS)
    ap.add_argument("--candle-days", type=int, default=14)
    ap.add_argument("--rss-hours", type=int, default=48)
    ap.add_argument("--no-collect", action="store_true")
    ap.add_argument("--data", default=None)
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--analysts", default=None,
                    help="Только указанные аналитики (fundamental,news,technical,quant)")
    ap.add_argument("--default-model", default="default",
                    help="Дефолтная модель для всех ролей (default = текущая модель hermes)")
    ap.add_argument("--analyst-model", action="append", default=[],
                    help="Маппинг role=model, например technical=openrouter/deepseek/deepseek-chat-v3")
    args = ap.parse_args()

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = args.output_dir or os.path.join(skill_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    print("=" * 60)
    print(f"  MOEX AI Hedge Fund — {args.mode} mode")
    print(f"  Tickers: {args.tickers}")
    print(f"  Default model: {args.default_model}")
    print("=" * 60)
    print()

    # Парсинг маппинга моделей
    model_map = parse_model_args(args.analyst_model, args.default_model)
    arbiter_model = model_map["arbiter"]  # отдельная роль, не наследуется от fundamental
    for role, m in model_map.items():
        print(f"  {role}: {m}", file=sys.stderr)

    # ── Step 1: Сбор данных ───────────────────────────────────────────
    data_file = args.data
    if not args.no_collect and not data_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        data_file = os.path.join(data_dir, f"moex_data_{timestamp}.json")
        _, data_file = collect_data(args.tickers, args.candle_days, args.rss_hours, data_file)
    elif not data_file:
        files = sorted([os.path.join(data_dir, f) for f in os.listdir(data_dir)
                        if f.startswith("moex_data_") and f.endswith(".json")])
        if not files:
            print("ERROR: No data files found.", file=sys.stderr)
            sys.exit(1)
        data_file = files[-1]
        print(f"  Using latest: {data_file}", file=sys.stderr)

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    data_text = json.dumps(data, ensure_ascii=False, indent=2)

    # ── Step 2: Аналитики ─────────────────────────────────────────────
    analysts = DEFAULT_ANALYSTS
    if args.analysts:
        wanted = set(args.analysts.split(","))
        analysts = [a for a in DEFAULT_ANALYSTS if a[0] in wanted]

    temp_dir = tempfile.mkdtemp(prefix="hedge_fund_")
    atexit.register(shutil.rmtree, temp_dir, ignore_errors=True)
    print(f"\n[2/3] Running {len(analysts)} analysts ({args.mode})...", file=sys.stderr)

    if args.mode == "pipeline":
        results = []
        for role, _ in analysts:
            model = model_map[role]
            r = run_analyst(role, model, data_text, temp_dir)
            results.append((role, model, r))
            print(f"  DONE: {role}", file=sys.stderr)
    else:
        results = []
        with ThreadPoolExecutor(max_workers=len(analysts)) as ex:
            futures = {}
            for role, _ in analysts:
                model = model_map[role]
                fut = ex.submit(run_analyst, role, model, data_text, temp_dir)
                futures[fut] = (role, model)
            for fut in as_completed(futures):
                role, model = futures[fut]
                try:
                    r = fut.result()
                except Exception as e:
                    r = f"[ERROR: {e}]"
                results.append((role, model, r))
                print(f"  DONE: {role}", file=sys.stderr)

    analyses_text = "\n\n".join(f"--- {role} ({model}) ---\n{text}"
                                 for role, model, text in results)

    # ── Step 3: Арбитр ────────────────────────────────────────────────
    print(f"\n[3/3] Running CIO (Arbiter)...", file=sys.stderr)
    arbiter_response = run_arbiter(arbiter_model, analyses_text, data_text)

    # ── Вывод ─────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("  ОТЧЁТЫ АНАЛИТИКОВ")
    print("=" * 60)
    for role, model, text in results:
        print(f"\n--- {role} ({model}) ---")
        print(text)
        print()

    print("=" * 60)
    print("  👑 CIO / АРБИТР (итоговый сигнал)")
    print("=" * 60)
    print(arbiter_response)
    print()
    print("=" * 60)
    print(f"  Data: {data_file}")
    print("=" * 60)

    # Сохранить отчёт
    report_path = os.path.join(data_dir, f"hedge_fund_report_{datetime.datetime.now():%Y-%m-%d_%H%M}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# MOEX AI Hedge Fund Report\n\n")
        f.write(f"**Date:** {datetime.datetime.now():%Y-%m-%d %H:%M}\n")
        f.write(f"**Tickers:** {args.tickers}\n")
        f.write(f"**Mode:** {args.mode}\n\n")
        for role, model, text in results:
            f.write(f"## {role.title()} ({model})\n\n{text}\n\n")
        f.write(f"## 👑 CIO Synthesis\n\n{arbiter_response}\n\n")
        f.write(f"---\n\n*Data: {data_file}*\n")
    print(f"\nReport saved: {report_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
