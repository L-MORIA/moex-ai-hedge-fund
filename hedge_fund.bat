@echo off
REM hedge_fund.bat — обёртка для Windows
REM Использует Python вместо bash (нет зависимости от opencode CLI)

setlocal

set SCRIPT_DIR=%~dp0
set PY_SCRIPT=%SCRIPT_DIR%run_hedge_fund.py

echo.
echo ======================================================
echo   MOEX AI Hedge Fund (Python launcher)
echo ======================================================
echo.

if "%~1"=="" (
    python "%PY_SCRIPT%"
) else (
    python "%PY_SCRIPT%" %*
)

endlocal
