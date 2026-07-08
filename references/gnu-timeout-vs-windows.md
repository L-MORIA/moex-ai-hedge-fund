# GNU timeout vs Windows TIMEOUT in .bat → bash context

## The problem

When a Windows `.bat` file invokes `bash script.sh`, and that bash script calls
`timeout 300 opencode run ...`, the `timeout` command resolves to
**`C:\Windows\System32\timout.exe`** (Windows TIMEOUT) — NOT `/usr/bin/timeout` (GNU coreutils).

```
Windows TIMEOUT syntax:  TIMEOUT /T <seconds> [/NOBREAK]
GNU timeout syntax:      timeout <seconds> <command> [args]
```

Result: `timeout 300 opencode run ...` → `ОШИБКА: Синтаксическая ошибка. Параметр
по умолчанию нельзя использовать более '1' раз(а).`

## Root cause

In interactive git-bash, `which timeout` → `/usr/bin/timeout` (GNU coreutils, from
MSYS2 MINGW package). But when bash is invoked from `cmd.exe` via a `.bat` file,
the PATH may include `C:\Windows\System32\` before `/usr/bin/`, so `timeout.exe`
(Windows) shadows `/usr/bin/timeout`.

## Solution

**Don't use `timeout` in bash scripts that run from .bat files.**

Workarounds that DON'T work reliably:
- Full path `/usr/bin/timeout` — MSYS2 path translation may still fail
- `command timeout` — still resolves via PATH
- `TIMEOUT=$(which timeout)` — same PATH issue

Best approach: remove `timeout` entirely. If the subprocess (opencode, etc.) may
hang, rely on the user pressing Ctrl+C, or implement timeout via shell logic
(e.g. `$SECONDS` + `kill`).

## Test

```bash
# In interactive git-bash — works
timeout 1 echo ok

# From a .bat file — may resolve to Windows TIMEOUT
# Call from .bat:
#   bash -c "timeout 1 echo ok"
# This breaks.
```
