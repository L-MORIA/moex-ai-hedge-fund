# Windows cmd.exe pitfalls for bash scripts

## Problem 1: `timeout` resolves to Windows TIMEOUT (not GNU)

When bash is invoked from a `.bat` file, `timeout N` calls `C:\Windows\System32\timout.exe`
(syntax: `TIMEOUT /T N /NOBREAK`), not GNU `/usr/bin/timeout` (syntax: `timeout N`).

**Symptoms:**
```
ОШИБКА: Синтаксическая ошибка. Параметр по умолчанию нельзя использовать более '1' раз(а).
Введите "TIMEOUT /?" для получения справки по использованию.
```

**Root cause:** MSYS2/git-bash's PATH ordering. When bash spawns a child process
from a `.bat`-launched session, `C:\Windows\System32` appears before `/usr/bin/`
in PATH.

**Three fixes (pick one):**

| Fix | How | Best for |
|-----|-----|----------|
| Remove `timeout` entirely | Just call `opencode run` directly | Interactive / user-windowed scripts (user can Ctrl+C) |
| Use full GNU path | `/usr/bin/timeout 300 opencode run ...` | Cron / automated scripts |
| Call from PowerShell | `powershell -Command "bash script.sh"` | When you need precise timeout control |

**Verification (inside bash):**
```bash
which timeout        # /usr/bin/timeout or /c/Windows/System32/timeout.exe
timeout --version    # GNU coreutils or "TIMEOUT /?" error
```

## Problem 2: Unicode box-drawing chars render as garbage

Characters like `═` (U+2550), `▸` (U+25B8) display as `тХР` in cmd.exe
because the terminal uses CP-866 (Russian OEM) not UTF-8.

**Symptoms:**
```
тХРтХРтХРтХРтХРтХРтХР   ← meant to be ════════
```

**Root cause:** cmd.exe on Russian Windows defaults to CP-866. `chcp` shows
active codepage. `═` is byte 0xE2 0x95 0x90 in UTF-8, interpreted as three
CP-866 chars: `т` (0xE2), `Х` (0x95), `Р` (0x90).

**Fixes:**

| Approach | How | Result |
|----------|-----|--------|
| Use ASCII only | Replace `═══` with `====`, `▸` with `>>` | Works everywhere, ugly but readable |
| Switch codepage | Add `chcp 65001 >nul` at top of `.bat` | May break other chars; not all fonts render box-drawing |
| Avoid cmd.exe | Run from PowerShell, git-bash, or Hermes TUI instead | Full Unicode support |

**Recommended:** ASCII-only headers in `.bat` files. Save Unicode formatting
for README.md / terminal output where UTF-8 is guaranteed.

## Problem 3: Visible progress matters

When a `.bat` double-click opens cmd.exe, the user sees NOTHING until
the script produces stdout. If the first step takes 30s+ to download/build
a model, the user assumes the program is broken.

**Fix:** `2>&1` (not `2>/dev/null`) for sequential steps so model build logs
are visible. Only suppress stderr for parallel sections where outputs
would interleave.

```bash
# Sequential (CIO): SHOW progress
cat persona data | opencode run --model "model" 2>&1

# Parallel (analysts): SUPPRESS interleaving
( cat persona data | opencode run --model "model" > out.txt 2>/dev/null ) &
```

## Summary: .bat file checklist

```bat
@echo off
chcp 65001 >nul          REM optional: UTF-8 (if terminal supports it)
cd /d "%~dp0"            REM cd to script dir

REM Use ONLY ASCII headers (no ═▸►→)
echo ====================
echo  Step description
echo ====================

REM Forward slashes for bash paths
bash script.sh --data data/file.json

REM No timeout inside bash (Windows conflict)
REM Let it run, user can Ctrl+C
pause > nul
```
