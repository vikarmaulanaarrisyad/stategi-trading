@echo off
title Menjalankan Visual Strategy Tester MT5 - VIKAR EA v3.00
echo =====================================================================
echo  MEMBUKA VISUAL STRATEGY TESTER METATRADER 5 (DIDIMAX)
echo  Robot: VIKAR EA 4-Pillar Pro (v3.00 Apex Grandmaster Edition)
echo  Preset: XAUUSD_BACKTEST_1YEAR_OPTIMAL.set (M5)
echo =====================================================================
echo.
set MT5_EXE="C:\Program Files\DIDIMAX MetaTrader 5\terminal64.exe"
set INI_FILE="e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\backtest_visual.ini"

if not exist %MT5_EXE% (
    echo [ERROR] MetaTrader 5 Didimax tidak ditemukan di %MT5_EXE%!
    pause
    exit /b
)

echo Meluncurkan Strategy Tester dalam mode Visual...
%MT5_EXE% /config:%INI_FILE%

echo.
echo Strategy Tester telah dibuka. Silakan nikmati simulasi playback candle!
pause
