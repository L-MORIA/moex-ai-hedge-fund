# Windows bat→bash path pitfall

## The problem

When a Windows `.bat` file passes a path argument to a bash script:

```bat
bash scripts/run.sh --data data\market.json
```

Bash in git-bash interprets backslashes as escape sequences inside double-quoted strings:
- `\m` → `m` (backslash is discarded)
- `\f` → form-feed character
- `\r` → carriage return

So `data\market.json` becomes `dataarket.json` — file not found.

## The fix (two layers)

### Layer 1: .bat file — use forward slashes

```bat
python scripts/collect_moex_data.py --output data/market.json
bash scripts/run_hedge_fund.sh --data data/market.json
```

Python on Windows accepts forward slashes natively. Bash always expects forward slashes.

### Layer 2: bash script — normalize defensively

In the bash script that parses `--data`, normalize any backslashes that might sneak through:

```bash
--data) DATA_FILE="$(echo "$2" | tr '\\' '/')"; shift 2 ;;
```

This catches cases where:
- A `.bat` passed backslashes anyway
- The user typed the path manually with backslashes
- PowerShell or another tool generated the path

## Why not sed

```bash
# OK — but tr is simpler
DATA_FILE="$(echo "$2" | sed 's/\\/\//g')"

# Cleaner
DATA_FILE="$(echo "$2" | tr '\\' '/')"
```

`tr` is cleaner for simple character replacement. No escaping ambiguity.

## Verification

```bash
echo 'data\market.json' | tr '\\' '/'
# Output: data/market.json
```
