@echo off
REM MOEX AI Hedge Fund Pipeline - Desktop Launcher
REM Sequential mode: analysts run one after another (no context passing),
REM then the CIO synthesizes the final signal. Uses the Python orchestrator.

cd /d "%~dp0"
echo =====================================================
echo   MOEX AI Hedge Fund - Pipeline
echo   Tickers: SBER, GAZP, LKOH, SBERP, VTBR
echo =====================================================
echo.

python scripts/run_hedge_fund.py --mode pipeline %*

echo.
echo Done. Press any key to close...
pause > nul
