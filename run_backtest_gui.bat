@echo off
title VIKAR EA 4-PILLAR - MT4 Backtest Studio GUI
cd /d "e:\Python\STRATEGY"

echo =======================================================================
echo   VIKAR EA 4-PILLAR PRO (v3.10) - METATRADER 4 BACKTEST STUDIO GUI
echo   Mengambil Data Historis Langsung dari MetaTrader 4 (.hst / .csv)
echo   TP 100 Poin, Trailing Stop Lilin, Auto-BE, dan AI Autopsy
echo =======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di sistem PATH!
    echo Silakan install Python 3.10+ dan pastikan dicentang 'Add Python to PATH'.
    pause
    exit /b
)

echo Menjalankan Desktop Studio GUI...
python vikar_backtest_gui.py

if %errorlevel% neq 0 (
    echo.
    echo [INFO] Terjadi kendala saat menjalankan GUI.
    pause
)
