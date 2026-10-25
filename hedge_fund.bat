@echo off
REM hedge_fund.bat - Windows launcher (Python orchestrator, no opencode dependency)

setlocal

set "SCRIPT_DIR=%~dp0"
set "PY_SCRIPT=%SCRIPT_DIR%run_hedge_fund.py"

echo.
echo ======================================================
echo   MOEX AI Hedge Fund (Python launcher)
echo ======================================================
echo.

python "%PY_SCRIPT%" %*

endlocal
