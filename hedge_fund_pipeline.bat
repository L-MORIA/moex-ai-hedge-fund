@echo off
REM MOEX AI Hedge Fund Pipeline - Desktop Launcher
REM Последовательный режим: аналитики идут друг за другом с передачей контекста

cd /d "%~dp0"
echo =====================================================
echo   MOEX AI Hedge Fund - Pipeline
echo   Tickers: SBER, GAZP, LKOH, SBERP, VTBR
echo =====================================================
echo.

echo [1/2] Collecting MOEX data...
python scripts/collect_moex_data.py --output data/market.json
echo.

echo [2/2] Running analysts + CIO (pipeline mode)...
bash scripts/run_hedge_fund.sh --mode pipeline --data data/market.json

echo.
echo Done. Press any key to close...
pause > nul
