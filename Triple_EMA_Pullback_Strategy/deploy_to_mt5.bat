@echo off
chcp 65001 >nul
title Deploy and Compile Triple EMA Pullback ke DIDIMAX MetaTrader 5

echo =======================================================================
echo    OTOMASI DEPLOY ^& KOMPILASI STRATEGI TRIPLE EMA PULLBACK (MT5)
echo =======================================================================
echo.

set "MT5_DIR=C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5"
set "EDITOR=C:\Program Files\DIDIMAX MetaTrader 5\MetaEditor64.exe"
set "BASE_DIR=%~dp0"

if not exist "%MT5_DIR%" (
    echo [ERROR] Folder Data Terminal MT5 tidak ditemukan di:
    echo "%MT5_DIR%"
    echo Silakan periksa kembali direktori data MetaTrader 5 Anda.
    exit /b 1
)

if not exist "%EDITOR%" (
    echo [ERROR] MetaEditor64.exe tidak ditemukan di:
    echo "%EDITOR%"
    exit /b 1
)

echo [1/5] Menyalin Include files (*.mqh)...
xcopy /Y /Q "%BASE_DIR%Include\*.mqh" "%MT5_DIR%\Include\" >nul
echo   - Selesai.

echo [2/5] Menyalin Experts (*.mq5)...
xcopy /Y /Q "%BASE_DIR%Experts\*.mq5" "%MT5_DIR%\Experts\" >nul
echo   - Selesai.

echo [3/5] Menyalin Indicators (*.mq5)...
xcopy /Y /Q "%BASE_DIR%Indicators\*.mq5" "%MT5_DIR%\Indicators\" >nul
echo   - Selesai.

echo [4/5] Menyalin Presets (*.set) ^& Template (*.tpl)...
if not exist "%MT5_DIR%\Profiles\Tester" mkdir "%MT5_DIR%\Profiles\Tester"
if not exist "%MT5_DIR%\Profiles\Templates" mkdir "%MT5_DIR%\Profiles\Templates"
xcopy /Y /Q "%BASE_DIR%*.set" "%MT5_DIR%\Profiles\Tester\" >nul
xcopy /Y /Q "%BASE_DIR%*.tpl" "%MT5_DIR%\Profiles\Templates\" >nul
echo   - Selesai.

echo [5/5] Mengompilasi source code via MetaEditor64...
echo   a. Mengompilasi Indikator...
start /wait "" "%EDITOR%" /compile:"%MT5_DIR%\Indicators\Triple_EMA_Pullback_Indicator.mq5" /log:"%BASE_DIR%compile_term_ind.log"
ping 127.0.0.1 -n 2 >nul

echo   b. Mengompilasi Expert Advisor...
start /wait "" "%EDITOR%" /compile:"%MT5_DIR%\Experts\Triple_EMA_Pullback_EA.mq5" /log:"%BASE_DIR%compile_term_ea.log"
ping 127.0.0.1 -n 2 >nul

echo.
echo [Sinkronisasi Binary EX5 Kembali ke Project Workspace]...
if exist "%MT5_DIR%\Indicators\Triple_EMA_Pullback_Indicator.ex5" (
    copy /Y "%MT5_DIR%\Indicators\Triple_EMA_Pullback_Indicator.ex5" "%BASE_DIR%Indicators\" >nul
)
if exist "%MT5_DIR%\Experts\Triple_EMA_Pullback_EA.ex5" (
    copy /Y "%MT5_DIR%\Experts\Triple_EMA_Pullback_EA.ex5" "%BASE_DIR%Experts\" >nul
)

echo =======================================================================
echo [STATUS HASIL DEPLOY ^& KOMPILASI]
echo =======================================================================
echo Log Indikator : %BASE_DIR%compile_term_ind.log
echo Log EA        : %BASE_DIR%compile_term_ea.log
echo.
echo Semua file EA, Indikator, Include, Preset .set, dan Template .tpl
echo telah BERHASIL disinkronkan ke DIDIMAX MetaTrader 5!
echo.
echo Silakan buka MT5 ^> Navigator ^> Refresh, atau jalankan Strategy Tester!
echo =======================================================================
