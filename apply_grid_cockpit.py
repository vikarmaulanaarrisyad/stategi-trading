import os

def apply_grid_cockpit():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Update g_panelW and g_panelH defaults
    code = code.replace("int            g_panelW           = 480;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelW           = 430;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelW           = 390;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelW           = 355;", "int            g_panelW           = 460;")

    # 2. Build the 2-Column Grid Executive Cockpit UpdateDashboard()
    grid_hud_code = """//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (2-COLUMN EXECUTIVE COCKPIT v3.30)|
//+------------------------------------------------------------------+
void UpdateDashboard()
{
   if (!InpShowDashboard)
   {
      DestroyDashboardGUI();
      return;
   }

   Comment(""); // Bersihkan teks comment biasa

   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
   double ask     = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid     = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread  = PriceToPips(ask - bid);

   int openCount = 0;
   double openFloating = GetOpenFloatingPnL(openCount);

   // Hitung total lot terbuka
   double totalLots = 0.0;
   for (int p = PositionsTotal() - 1; p >= 0; p--)
   {
      if (posInfo.SelectByIndex(p) && posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
         totalLots += posInfo.Volume();
   }

   // Hitung pending orders aktif
   int pendingCount = 0;
   for (int o = OrdersTotal() - 1; o >= 0; o--)
   {
      ulong ot = OrderGetTicket(o);
      if (ot > 0 && orderInfo.Select(ot) && orderInfo.Symbol() == _Symbol && orderInfo.Magic() == InpMagicNumber)
         pendingCount++;
   }

   // Statistik Sejak Start, Harian, Mingguan
   datetime startOfDay  = iTime(_Symbol, PERIOD_D1, 0);
   if (startOfDay == 0) startOfDay = TimeCurrent() - 86400;

   datetime startOfWeek = iTime(_Symbol, PERIOD_W1, 0);
   if (startOfWeek == 0) startOfWeek = TimeCurrent() - (7 * 86400);

   TradeStats statsTotal = CalculateHistoryStats(g_eaStartTime);
   TradeStats statsDaily = CalculateHistoryStats(startOfDay);
   TradeStats statsWeekly= CalculateHistoryStats(startOfWeek);

   double totalGrowthPct = (g_eaInitialBalance > 0.0001) ? ((balance - g_eaInitialBalance) / g_eaInitialBalance * 100.0) : 0.0;

   int panelX = g_panelX;
   int panelY = g_panelY;
   int panelW = 460;
   g_panelW = panelW;

   int col1X = panelX + 16;
   int col2X = panelX + 235;

   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));
   string entryModeTag = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MARKET" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "BUY/SELL STOP" : "BUY/SELL LIMIT");
   string btnModeText  = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MODE: MKT" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "MODE: STOP" : "MODE: LIMIT");

   // ===================================================================
   // JIKA DALAM MODE MINIMIZED (HANYA 1 BARIS RAMPING)
   // ===================================================================
   if (g_hudMinimized)
   {
      int minH = 46;
      g_panelH = minH;
      CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, minH, C'13,18,30', C'30,41,59');
      CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + minH - 2, panelW, 2, C'14,165,233', C'14,165,233');

      CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 7, "◈ VIKAR PRO v3.30", clrWhite, 9, "Segoe UI Bold");
      color floatClrMin = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
      string minStatus = "Float: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + "P) | Eq: $" + DoubleToString(equity, 2);
      CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 25, minStatus, floatClrMin, 7, "Segoe UI Bold");

      CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 80, panelY + 10, 70, 26, "👁️ EXPAND", C'15,23,42', C'52,211,153', 7);
      ChartRedraw(0);
      return;
   }

   // ===================================================================
   // MODE EXPANDED (2-COLUMN CYBER COCKPIT)
   // ===================================================================

   // 1. MASTER BACKGROUND (SOLID SLATE OBSIDIAN - ANTI-TEMBUS CANDLE)
   // Tinggi awal diestimasi 390px, akan disesuaikan di akhir
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, 395, C'13,18,30', C'30,41,59');

   // 2. HEADER BANNER
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 46, C'15,23,42', C'2,132,199');
   CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + 44, panelW, 2, C'14,165,233', C'14,165,233');

   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 7, "◈ VIKAR 4-PILLAR PRO  v3.30", clrWhite, 10, "Segoe UI Bold");

   string pauseStatus = g_eaManualPause ? "[PAUSED]" : "[ACTIVE]";
   string headerSubStr = _Symbol + " • " + EnumToString(_Period) + " • " + lotDisplay + " • " + pauseStatus + " • ID: " + IntegerToString(InpMagicNumber);
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 25, headerSubStr, C'186,230,253', 7, "Segoe UI");

   // Header Interactive Buttons
   CreateOrUpdateBtn("VIKAR_HUD_BTN_MODE", panelX + panelW - 175, panelY + 10, 92, 26, btnModeText, C'11,15,25', C'56,189,248', 7);
   CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 78, panelY + 10, 68, 26, "👁️ MINI", C'11,15,25', C'52,211,153', 7);

   int currY = panelY + 52;

   // 3. SEKSI 1: RINGKASAN AKUN & PERFORMA
   CreateOrUpdateRect("VIKAR_HUD_SEC1_BG", panelX + 8, currY, panelW - 16, 22, C'20,28,45', C'51,65,85');
   CreateOrUpdateText("VIKAR_HUD_SEC1_TITLE", panelX + 16, currY + 4, "💼 RINGKASAN AKUN & PERFORMA", C'251,191,36', 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   string floatSummary = "Floating: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Pos)";
   CreateOrUpdateText("VIKAR_HUD_SEC1_FLOAT", panelX + panelW - 165, currY + 4, floatSummary, floatClr, 7, "Segoe UI Bold");

   // Baris 1: Saldo & Ekuitas
   CreateOrUpdateText("VIKAR_HUD_ACC_L1", col1X, currY + 26, "Saldo    : $" + DoubleToString(balance, 2), clrWhite, 7, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_ACC_R1", col2X, currY + 26, "Ekuitas  : $" + DoubleToString(equity, 2), clrWhite, 7, "Segoe UI Bold");

   // Baris 2: Hari Ini & Minggu Ini
   double dailyWinratePct = (statsDaily.totalTrades > 0) ? ((double)statsDaily.winTrades / statsDaily.totalTrades * 100.0) : 0.0;
   string dailyWRStr = (statsDaily.totalTrades > 0) ? (" (" + DoubleToString(dailyWinratePct, 0) + "% WR)") : "";
   CreateOrUpdateText("VIKAR_HUD_ACC_L2", col1X, currY + 44, "Hari Ini : " + FormatPnL(statsDaily.netProfit) + dailyWRStr, (statsDaily.netProfit >= 0 ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_ACC_R2", col2X, currY + 44, "Minggu Ini: " + FormatPnL(statsWeekly.netProfit), (statsWeekly.netProfit >= 0 ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   // Baris 3: Prop Firm DD & Spread
   double ddLimit = InpMaxDailyEquityDDPct;
   double bufferSisa = MathMax(0.0, ddLimit - g_currentDailyDDPct);
   color ddClr = (g_currentDailyDDPct >= ddLimit * 0.75) ? C'248,113,113' : ((g_currentDailyDDPct > 0.0) ? C'251,191,36' : C'74,222,128');
   CreateOrUpdateText("VIKAR_HUD_ACC_L3", col1X, currY + 62, "Daily DD : " + DoubleToString(g_currentDailyDDPct, 2) + "% / " + DoubleToString(ddLimit, 1) + "% (" + DoubleToString(bufferSisa, 1) + "% Sisa)", ddClr, 7, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_ACC_R3", col2X, currY + 62, "Spread   : " + DoubleToString(spread, 1) + " pips | " + lotDisplay, C'148,163,184', 7, "Segoe UI");

   currY += 84;

   // 4. SEKSI 2: ANALISIS 4-PILAR SMC & KONFLUENSI
   CreateOrUpdateRect("VIKAR_HUD_SEC2_BG", panelX + 8, currY, panelW - 16, 22, C'20,28,45', C'51,65,85');
   CreateOrUpdateText("VIKAR_HUD_SEC2_TITLE", panelX + 16, currY + 4, "🏛️ ANALISIS 4-PILAR SMC & KONFLUENSI", C'56,189,248', 8, "Segoe UI Bold");

   string scoreStr = (g_lastScoreResult.totalScore > 0) ? (DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")") : "Ready";
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 65.0) ? C'251,191,36' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_SEC2_SCORE", panelX + panelW - 140, currY + 4, "Skor: " + scoreStr, scoreClr, 7, "Segoe UI Bold");

   // Baris 1: SMC Struktur & Dealing Range
   string smcStr = (g_smcAnalysis.structureName != "") ? g_smcAnalysis.structureName : "Market Equilibrium";
   if (g_smcAnalysis.hasSweep) smcStr += " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr += " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_P1_L", col1X, currY + 26, "SMC Trend : " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   CreateOrUpdateText("VIKAR_HUD_P1_R", col2X, currY + 26, "Dealing Range: " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   // Baris 2: Triple EMA & Fibo Golden Pocket
   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   string emaTrendStr = "BULLISH (Ribbon 8/21)";
   if (CopyBuffer(h_ema125, 0, 0, 2, ema125Val) >= 2)
   {
      double closePrice = iClose(_Symbol, _Period, 1);
      emaTrendStr = (closePrice > ema125Val[1]) ? "BULLISH (Di Atas 125)" : "BEARISH (Di Bawah 125)";
   }
   CreateOrUpdateText("VIKAR_HUD_P2_L", col1X, currY + 44, "Triple EMA: " + emaTrendStr, C'232,121,249', 7, "Segoe UI");

   string fiboStr = currentFibo.isValid ? ("GP 61.8% @ " + DoubleToString(currentFibo.level618, 1)) : "GP: Scanning...";
   CreateOrUpdateText("VIKAR_HUD_P2_R", col2X, currY + 44, "Fibo Pocket  : " + fiboStr, C'52,211,153', 7, "Segoe UI");

   // Baris 3: Order Block & Pivot Level
   string obStr = "OB: Scanning Zona...";
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
      obStr = "Bull OB " + DoubleToString(g_bullishOB.bottom, 1) + "-" + DoubleToString(g_bullishOB.top, 1);
   else if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
      obStr = "Bear OB " + DoubleToString(g_bearishOB.bottom, 1) + "-" + DoubleToString(g_bearishOB.top, 1);
   CreateOrUpdateText("VIKAR_HUD_P3_L", col1X, currY + 62, "Order Block: " + obStr, C'244,114,182', 7, "Segoe UI");

   CreateOrUpdateText("VIKAR_HUD_P3_R", col2X, currY + 62, "Daily Pivot  : P " + DoubleToString(currentPivot.P, 1) + " (R1 " + DoubleToString(currentPivot.R1, 1) + ")", C'148,163,184', 7, "Segoe UI");

   // Baris 4: Pola Lilin & Pola Chart
   string candleStr = (g_candleAnalysis.patternName != "") ? g_candleAnalysis.patternName : "Lilin Normal";
   if (g_candleAnalysis.score > 0) candleStr += " [" + DoubleToString(g_candleAnalysis.score, 0) + "p]";
   CreateOrUpdateText("VIKAR_HUD_P4_L", col1X, currY + 80, "Pola Lilin : " + candleStr, C'251,191,36', 7, "Segoe UI");

   string patStr = g_chartPattern.isValid ? (g_chartPattern.patternName + " [" + DoubleToString(g_chartPattern.score, 0) + "p]") : "Geometri Normal";
   CreateOrUpdateText("VIKAR_HUD_P4_R", col2X, currY + 80, "Pola Chart   : " + patStr, (g_chartPattern.isValid ? C'74,222,128' : C'148,163,184'), 7, "Segoe UI");

   currY += 102;

   // 5. SEKSI 3: SENSOR PASAR & INTELEJENSI RISIKO
   CreateOrUpdateRect("VIKAR_HUD_SEC3_BG", panelX + 8, currY, panelW - 16, 22, C'20,28,45', C'51,65,85');
   CreateOrUpdateText("VIKAR_HUD_SEC3_TITLE", panelX + 16, currY + 4, "🛡️ SENSOR PASAR & INTELEJENSI RISIKO", C'52,211,153', 8, "Segoe UI Bold");

   // Baris 1: Cuaca Pasar & Macro Trend
   string regimeStr = (g_currentRegime == REGIME_CHOPPY_SIDEWAYS) ? "CHOPPY / FAKEOUT" : "TREND SEHAT";
   color regimeClr  = (g_currentRegime == REGIME_CHOPPY_SIDEWAYS) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_R1_L", col1X, currY + 26, "Cuaca Pasar: " + regimeStr + " (CI " + DoubleToString(g_currentChoppiness, 0) + ")", regimeClr, 7, "Segoe UI Bold");

   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_R1_R", col2X, currY + 26, "Macro Trend  : H1 " + g_htfMacroStr, htfClr, 7, "Segoe UI Bold");

   // Baris 2: VSA Volume & Circuit Guard
   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Volume") : "VSA: OFF";
   CreateOrUpdateText("VIKAR_HUD_R2_L", col1X, currY + 44, "VSA Volume : " + vsaDisplay, C'203,213,225', 7, "Segoe UI");

   string cbDisplay = "0/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss (Aman)";
   if (g_cooldownUntilTime > TimeCurrent()) cbDisplay = "COOLDOWN AKTIF";
   else if (g_consecutiveLossCount > 0) cbDisplay = IntegerToString(g_consecutiveLossCount) + " Loss";
   CreateOrUpdateText("VIKAR_HUD_R2_R", col2X, currY + 44, "Circuit Guard: " + cbDisplay, C'74,222,128', 7, "Segoe UI");

   currY += 66;

   // 6. SEKSI 4: RADAR EKSEKUSI & STATUS SINYAL
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", panelX + 8, currY, panelW - 16, 64, C'11,15,25', C'14,165,233');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", panelX + 16, currY + 6, "⚡ RADAR EKSEKUSI & STATUS SINYAL TERAKHIR:", C'56,189,248', 7, "Segoe UI Bold");

   // Emergency Close All Button on Right
   CreateOrUpdateBtn("VIKAR_HUD_BTN_CLOSEALL", panelX + panelW - 104, currY + 6, 92, 24, "🚨 CLOSE ALL", C'153,27,27', clrWhite, 7);

   string statusDisplay = (g_lastSignalType != "") ? g_lastSignalType : "MENUNGGU SETUP GRADE A (SCANNING)";
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING ULANG";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 16, currY + 23, "● " + statusDisplay, clrWhite, 8, "Segoe UI Bold");

   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = (InpUsePointsTrailing || InpUseCandleTrailing || InpUseTrailingEMA21) ? "Trail: ON" : "Trail: OFF";
   string pendingInfo = (pendingCount > 0) ? (" | Pending: " + IntegerToString(pendingCount)) : "";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 16, currY + 42, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + pendingInfo, C'148,163,184', 7, "Segoe UI");

   int finalH = (currY + 72) - panelY;
   g_panelH = finalH;
   ObjectSetInteger(0, "VIKAR_HUD_BG", OBJPROP_YSIZE, finalH);

   ChartRedraw(0);
}
"""

    start_idx = code.find("void UpdateDashboard()")
    end_idx = code.find("void OnChartEvent(")
    if start_idx == -1 or end_idx == -1:
        print("[-] Could not find UpdateDashboard boundaries!")
        return False

    code = code[:start_idx] + grid_hud_code + "\n" + code[end_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] Successfully transformed Dashboard into 2-Column Grid Executive Cockpit!")
    return True

if __name__ == '__main__':
    apply_grid_cockpit()
