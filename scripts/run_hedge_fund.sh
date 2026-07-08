#!/usr/bin/env bash
# run_hedge_fund.sh — MOEX AI Hedge Fund оркестратор
#
# 1. Собирает данные с MOEX
# 2. Запускает 4 аналитиков (OpenCode Zen) ПАРАЛЛЕЛЬНО
# 3. Арбитр (Nemotron 3 Ultra) синтезирует итоговый сигнал
# 4. Выводит результат
#
# Usage:
#   bash scripts/run_hedge_fund.sh                    # council mode (default)
#   bash scripts/run_hedge_fund.sh --mode pipeline     # pipeline mode
#   bash scripts/run_hedge_fund.sh --tickers SBER,GAZP # свои тикеры
#   bash scripts/run_hedge_fund.sh --no-collect        # использовать сохранённые данные
#   bash scripts/run_hedge_fund.sh --data data.json    # конкретный файл данных

set -eo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PERSONAS_DIR="$SKILL_DIR/personas"
SCRIPTS_DIR="$SKILL_DIR/scripts"
DATA_DIR="$SKILL_DIR/data"

# Дефолты
MODE="${MODE:-council}"
TICKERS="${TICKERS:-SBER,GAZP,LKOH,SBERP,VTBR}"
NO_COLLECT=false
DATA_FILE=""

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode) MODE="$2"; shift 2 ;;
        --tickers) TICKERS="$2"; shift 2 ;;
        --no-collect) NO_COLLECT=true; shift ;;
        --data) DATA_FILE="$(echo "$2" | tr '\\' '/')"; shift 2 ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
done

echo ""
echo "======================================================"
echo "  MOEX AI Hedge Fund — $MODE mode"
echo "  Tickers: $TICKERS"
echo "======================================================"
echo ""

# ── Step 1: Collect data ─────────────────────────────────────────────────
if [ "$NO_COLLECT" = false ] && [ -z "$DATA_FILE" ]; then
    echo ">> [1/3] Collecting MOEX data..."
    mkdir -p "$DATA_DIR"
    TIMESTAMP=$(date +"%Y-%m-%d_%H%M")
    DATA_FILE="$DATA_DIR/moex_data_${TIMESTAMP}.json"
    python "$SCRIPTS_DIR/collect_moex_data.py" \
        --tickers "$TICKERS" \
        --candle-days 14 \
        --rss-hours 48 \
        --output "$DATA_FILE"
    echo ""
elif [ -n "$DATA_FILE" ]; then
    echo ">> [1/3] Using existing data: $DATA_FILE"
else
    echo ">> [1/3] Skipping data collection (--no-collect)"
    DATA_FILE=$(ls -t "$DATA_DIR"/moex_data_*.json 2>/dev/null | head -1)
    if [ -z "$DATA_FILE" ]; then
        echo "ERROR: No existing data found. Run without --no-collect first."
        exit 1
    fi
    echo "   Using: $DATA_FILE"
fi

# ── Step 2: Run analysts ────────────────────────────────────────────────
echo ""
echo ">> [2/3] Launching 4 analysts ($MODE mode)..."
echo ""

ANALYSTS_DIR=$(mktemp -d)
trap "rm -rf '$ANALYSTS_DIR'" EXIT

ANALYSTS=(
    "fundamental:opencode/big-pickle:Fundamental (Big Pickle)"
    "news:opencode/deepseek-v4-flash-free:News (Deepseek)"
    "technical:opencode/mimo-v2.5-free:Technical (Mimo)"
    "quant:opencode/deepseek-v4-flash-free:Quant (Deepseek)"
)

# Run a single analyst, optionally with prior context
run_analyst() {
    local role="$1" model="$2" label="$3"
    local PERSONA_FILE="$PERSONAS_DIR/${role}_analyst.txt"
    if [ ! -f "$PERSONA_FILE" ]; then
        echo "  SKIP: Missing persona $PERSONA_FILE"
        return
    fi
    echo "  >> $role ($model)..."
    local outfile="$ANALYSTS_DIR/${role}.txt"
    local errfile="$ANALYSTS_DIR/${role}.err"
    (cat "$PERSONA_FILE"; echo ""; echo "=== MOEX DATA ==="; cat "$DATA_FILE") \
        | opencode run --model "$model" \
        > "$outfile" 2>"$errfile"
    local ec=$?
    if [ ! -s "$outfile" ]; then
        echo "  WARN: $role produced no output ($(head -c 200 "$errfile" 2>/dev/null))" >&2
    fi
    echo "  DONE: $role" >&2
    rm -f "$errfile"
    return $ec
}

if [ "$MODE" = "pipeline" ]; then
    # Pipeline: sequential (each gets same data, CIO sees accumulated reports)
    for entry in "${ANALYSTS[@]}"; do
        IFS=":" read -r role model label <<< "$entry"
        run_analyst "$role" "$model" "$label"
        # Stagger to avoid hammering API
        sleep 1
    done
else
    # Council: parallel (default)
    PID_LIST=""
    for entry in "${ANALYSTS[@]}"; do
        IFS=":" read -r role model label <<< "$entry"
        run_analyst "$role" "$model" "$label" &
        sleep 2
        PID_LIST="$PID_LIST $!"
    done
    echo ""
    echo "  Waiting for all analysts..."
    wait $PID_LIST || true
fi
echo "  All analysts completed."
echo ""

# ── Step 3: Arbiter (CIO) ───────────────────────────────────────────────
echo ">> [3/3] CIO synthesis..."
echo ""

ARBITER_INPUT="$ANALYSTS_DIR/all_analyses.txt"
{
    echo "# MOEX AI Hedge Fund -- Analyst Reports"
    echo "Date: $(date)"
    echo "Tickers: $TICKERS"
    echo ""

    for entry in "${ANALYSTS[@]}"; do
        IFS=":" read -r role model label <<< "$entry"
        REPORT="$ANALYSTS_DIR/${role}.txt"
        if [ -f "$REPORT" ]; then
            echo "--- $label ---"
            cat "$REPORT"
            echo ""
        fi
    done
} > "$ARBITER_INPUT"

PERSONA_ARBITER="$PERSONAS_DIR/arbiter.txt"
if [ -f "$PERSONA_ARBITER" ]; then
    echo "  Running CIO (Deepseek V4 Flash) ..."
    echo "  (reliable model - Nemotron 3 Ultra often fails on free tier)"
    echo ""
    {
        cat "$PERSONA_ARBITER"
        echo ""
        echo "=== ANALYST REPORTS ==="
        cat "$ARBITER_INPUT"
    } | opencode run --model "opencode/deepseek-v4-flash-free" 2>&1
    echo ""
    echo "  Tip: export CIO_MODEL=opencode/nemotron-3-ultra-free to try 550B"
else
    echo "SKIP: Missing arbiter persona"
    echo "--- Analyst Reports ---"
    cat "$ARBITER_INPUT"
fi

echo ""
echo "======================================================"
echo "  Data: $DATA_FILE"
echo "======================================================"
