@echo off
REM MOEX AI Hedge Fund — Desktop Launcher
REM Запускает сбор данных и мульти-агентный анализ MOEX

cd /d "%~dp0"
echo ═══════════════════════════════════════════════
echo   MOEX AI Hedge Fund
echo   Tickers: SBER, GAZP, LKOH, SBERP, VTBR
echo ═══════════════════════════════════════════════
echo.

echo [1/2] Collecting MOEX data...
python scripts/collect_moex_data.py --output data/market.json
echo.

echo [2/2] Running analysts + CIO...
bash scripts/run_hedge_fund.sh --data data/market.json

echo.
echo Done. Press any key to close...
pause > nul
