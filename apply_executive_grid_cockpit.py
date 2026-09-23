import os

def apply_executive_grid():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Update g_panelW and g_panelH defaults
    code = code.replace("int            g_panelW           = 480;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelW           = 430;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelW           = 390;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelW           = 355;", "int            g_panelW           = 460;")
    code = code.replace("int            g_panelH           = 420;", "int            g_panelH           = 350;")
    code = code.replace("int            g_panelH           = 620;", "int            g_panelH           = 350;")

    # 2. Complete Executive 2-Column Grid Cockpit HUD
    executive_grid_code = """//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD: EXECUTIVE 2-COLUMN COCKPIT v3.30          |
//| Ultra-Modern Fintech Dark Theme (460px x 350px Solid Canvas)     |
//+------------------------------------------------------------------+
void UpdateDashboard()
{
   if (!InpShowDashboard)
   {
      DestroyDashboardGUI();
      return;
   }

   Comment(""); // Bersihkan teks comment biasa

   // Bersihkan objek lama sekali saat inisialisasi / pergantian versi
   static bool s_firstDashboardInit = true;
   if (s_firstDashboardInit)
   {
      DestroyDashboardGUI();
      s_firstDashboardInit = false;
   }

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

   int panelX = g_panelX;
   int panelY = g_panelY;
   int panelW = 460;
   g_panelW = panelW;

   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));
   string entryModeTag = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MARKET" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "BUY/SELL STOP" : "BUY/SELL LIMIT");
   string btnModeText  = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MODE: MKT" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "MODE: STOP" : "MODE: LIMIT");

   // ===================================================================
   // JIKA DALAM MODE MINIMIZED (HANYA BILAH RAMPING 44px)
   // ===================================================================
   if (g_hudMinimized)
   {
      int minH = 46;
      g_panelH = minH;
      CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, minH, C'13,18,30', C'30,41,59');
      CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + minH - 2, panelW, 2, C'14,165,233', C'14,165,233');

      CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 8, "◈ VIKAR PRO v3.30", clrWhite, 9, "Segoe UI Bold");
      color floatClrMin = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
      string minStatus = "Float: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + "P) | Eq: $" + DoubleToString(equity, 2) + " | " + btnModeText;
      CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 26, minStatus, floatClrMin, 7, "Segoe UI Bold");

      CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 78, panelY + 10, 68, 26, "👁️ EXPAND", C'15,23,42', C'52,211,153', 7);
      ChartRedraw(0);
      return;
   }

   // ===================================================================
   // MODE EXPANDED (EXECUTIVE 2-COLUMN COCKPIT)
   // ===================================================================

   // 1. MASTER CANVAS BACKGROUND (SOLID SLATE-OBSIDIAN - ANTI-TEMBUS CANDLE)
   int totalH = 348;
   g_panelH = totalH;
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, totalH, C'13,18,30', C'30,41,59');

   // 2. HEADER BANNER (Y: 0 s/d 44)
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 44, C'18,24,38', C'2,132,199');
   CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + 42, panelW, 2, C'14,165,233', C'14,165,233');

   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 6, "◈ VIKAR 4-PILLAR PRO  v3.30", clrWhite, 10, "Segoe UI Bold");

   string pauseStatus = g_eaManualPause ? "[PAUSED]" : "[ACTIVE]";
   string headerSubStr = _Symbol + " • " + EnumToString(_Period) + " • " + lotDisplay + " • " + pauseStatus + " • ID: " + IntegerToString(InpMagicNumber);
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 24, headerSubStr, C'148,163,184', 7, "Segoe UI");

   // Tombol Mode & Mini
   CreateOrUpdateBtn("VIKAR_HUD_BTN_MODE", panelX + panelW - 170, panelY + 9, 92, 25, btnModeText, C'15,23,42', C'56,189,248', 7);
   CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 74, panelY + 9, 64, 25, "👁️ MINI", C'15,23,42', C'52,211,153', 7);

   int currY = panelY + 48;

   // 3. BARIS KPI: RINGKASAN AKUN & PERFORMA (Y: 48 s/d 124, Tinggi 76px)
   CreateOrUpdateRect("VIKAR_HUD_ACC_BG", panelX + 8, currY, panelW - 16, 76, C'20,28,45', C'39,51,73');
   CreateOrUpdateText("VIKAR_HUD_SEC1_TITLE", panelX + 16, currY + 6, "💼 RINGKASAN AKUN & PERFORMA", C'251,191,36', 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   string floatSummary = "Floating: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Pos)";
   CreateOrUpdateText("VIKAR_HUD_SEC1_FLOAT", panelX + panelW - 175, currY + 6, floatSummary, floatClr, 7, "Segoe UI Bold");

   int col1X = panelX + 16;
   int col2X = panelX + 235;

   // Baris 1: Saldo & Ekuitas
   CreateOrUpdateText("VIKAR_HUD_ACC_L1", col1X, currY + 25, "Saldo    : $" + DoubleToString(balance, 2), clrWhite, 7, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_ACC_R1", col2X, currY + 25, "Ekuitas  : $" + DoubleToString(equity, 2), clrWhite, 7, "Segoe UI Bold");

   // Baris 2: Hari Ini & Minggu Ini
   double dailyWinratePct = (statsDaily.totalTrades > 0) ? ((double)statsDaily.winTrades / statsDaily.totalTrades * 100.0) : 0.0;
   string dailyWRStr = (statsDaily.totalTrades > 0) ? (" (" + DoubleToString(dailyWinratePct, 0) + "% WR)") : "";
   CreateOrUpdateText("VIKAR_HUD_ACC_L2", col1X, currY + 42, "Hari Ini : " + FormatPnL(statsDaily.netProfit) + dailyWRStr, (statsDaily.netProfit >= 0 ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_ACC_R2", col2X, currY + 42, "Minggu Ini: " + FormatPnL(statsWeekly.netProfit), (statsWeekly.netProfit >= 0 ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   // Baris 3: Daily Drawdown & Spread
   double ddLimit = InpMaxDailyEquityDDPct;
   double bufferSisa = MathMax(0.0, ddLimit - g_currentDailyDDPct);
   color ddClr = (g_currentDailyDDPct >= ddLimit * 0.75) ? C'248,113,113' : ((g_currentDailyDDPct > 0.0) ? C'251,191,36' : C'74,222,128');
   CreateOrUpdateText("VIKAR_HUD_ACC_L3", col1X, currY + 59, "Daily DD : " + DoubleToString(g_currentDailyDDPct, 2) + "% / " + DoubleToString(ddLimit, 1) + "% (" + DoubleToString(bufferSisa, 1) + "% Sisa)", ddClr, 7, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_ACC_R3", col2X, currY + 59, "Spread   : " + DoubleToString(spread, 1) + " pip | " + lotDisplay, C'148,163,184', 7, "Segoe UI");

   currY += 80;

   // 4. GRID 2-KOLOM: 4-PILAR SMC (KIRI) vs SENSOR PASAR & RADAR (KANAN)
   // Lebar masing-masing kolom: 218px, tinggi: 138px
   int colCardW = 218;
   int leftCardX = panelX + 8;
   int rightCardX = panelX + 234;

   // --- KARTU KIRI: 4-PILAR SMC & KONFLUENSI ---
   CreateOrUpdateRect("VIKAR_HUD_SMC_BG", leftCardX, currY, colCardW, 138, C'18,25,40', C'30,41,59');
   CreateOrUpdateRect("VIKAR_HUD_SMC_HDR_BG", leftCardX, currY, colCardW, 22, C'24,33,52', C'40,53,78');
   CreateOrUpdateText("VIKAR_HUD_SMC_HDR", leftCardX + 8, currY + 4, "🏛️ 4-PILAR SMC", C'56,189,248', 7, "Segoe UI Bold");

   string scoreStr = (g_lastScoreResult.totalScore > 0) ? (DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")") : "Ready";
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 65.0) ? C'251,191,36' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_SMC_SCORE", leftCardX + colCardW - 88, currY + 4, "Skor: " + scoreStr, scoreClr, 7, "Segoe UI Bold");

   // Baris 1: SMC Structure Trend
   string smcStr = (g_smcAnalysis.structureName != "") ? g_smcAnalysis.structureName : "Equilibrium";
   if (g_smcAnalysis.hasSweep) smcStr += " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr += " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_SMC_L1", leftCardX + 8, currY + 25, "SMC Trend  : " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   // Baris 2: Dealing Range (Diskon / Premium)
   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   CreateOrUpdateText("VIKAR_HUD_SMC_L2", leftCardX + 8, currY + 43, "Zona Harga : " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   // Baris 3: Triple EMA Baseline
   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   string emaTrendStr = "Bullish (Ribbon)";
   if (CopyBuffer(h_ema125, 0, 0, 2, ema125Val) >= 2)
   {
      double closePrice = iClose(_Symbol, _Period, 1);
      emaTrendStr = (closePrice > ema125Val[1]) ? "Bullish (> EMA125)" : "Bearish (< EMA125)";
   }
   CreateOrUpdateText("VIKAR_HUD_SMC_L3", leftCardX + 8, currY + 61, "Triple EMA : " + emaTrendStr, C'232,121,249', 7, "Segoe UI");

   // Baris 4: Order Block & FVG
   string obStr = "OB: Scanning...";
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
      obStr = "Bull OB " + DoubleToString(g_bullishOB.bottom, 1) + "-" + DoubleToString(g_bullishOB.top, 1);
   else if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
      obStr = "Bear OB " + DoubleToString(g_bearishOB.bottom, 1) + "-" + DoubleToString(g_bearishOB.top, 1);
   CreateOrUpdateText("VIKAR_HUD_SMC_L4", leftCardX + 8, currY + 79, "Order Block: " + obStr, C'244,114,182', 7, "Segoe UI");

   // Baris 5: Fibo Golden Pocket
   string fiboStr = currentFibo.isValid ? ("GP 61.8% @" + DoubleToString(currentFibo.level618, 1)) : "GP: Scanning...";
   CreateOrUpdateText("VIKAR_HUD_SMC_L5", leftCardX + 8, currY + 97, "Fibo Pocket: " + fiboStr, C'52,211,153', 7, "Segoe UI");

   // Baris 6: Pola Lilin & Chart Pattern
   string candleStr = (g_candleAnalysis.patternName != "") ? g_candleAnalysis.patternName : "Lilin Normal";
   if (g_candleAnalysis.score > 0) candleStr += " [" + DoubleToString(g_candleAnalysis.score, 0) + "p]";
   CreateOrUpdateText("VIKAR_HUD_SMC_L6", leftCardX + 8, currY + 115, "Pola Lilin : " + candleStr, C'251,191,36', 7, "Segoe UI");


   // --- KARTU KANAN: SENSOR PASAR & RADAR RISIKO ---
   CreateOrUpdateRect("VIKAR_HUD_RADAR_BG", rightCardX, currY, colCardW, 138, C'18,25,40', C'30,41,59');
   CreateOrUpdateRect("VIKAR_HUD_RADAR_HDR_BG", rightCardX, currY, colCardW, 22, C'24,33,52', C'40,53,78');
   CreateOrUpdateText("VIKAR_HUD_RADAR_HDR", rightCardX + 8, currY + 4, "🛡️ SENSOR PASAR", C'52,211,153', 7, "Segoe UI Bold");

   string regimeStr = (g_currentRegime == REGIME_CHOPPY_SIDEWAYS) ? "CHOPPY" : "TREND SEHAT";
   color regimeClr  = (g_currentRegime == REGIME_CHOPPY_SIDEWAYS) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_RADAR_BADGE", rightCardX + colCardW - 74, currY + 4, "CI: " + DoubleToString(g_currentChoppiness, 0), regimeClr, 7, "Segoe UI Bold");

   // Baris 1: Kondisi Cuaca Pasar
   CreateOrUpdateText("VIKAR_HUD_RADAR_L1", rightCardX + 8, currY + 25, "Kondisi    : " + regimeStr + " (Regime)", regimeClr, 7, "Segoe UI Bold");

   // Baris 2: Macro Trend H1
   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_RADAR_L2", rightCardX + 8, currY + 43, "Macro H1   : " + g_htfMacroStr, htfClr, 7, "Segoe UI Bold");

   // Baris 3: VSA Volume Flow
   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Volume") : "VSA: OFF";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L3", rightCardX + 8, currY + 61, "VSA Volume : " + vsaDisplay, C'203,213,225', 7, "Segoe UI");

   // Baris 4: ADX Trend Kinetic Strength
   string adxStatus = (g_currentADXVal >= 25.0) ? " (Kuat)" : " (Lemah)";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L4", rightCardX + 8, currY + 79, "ADX Power  : " + DoubleToString(g_currentADXVal, 1) + adxStatus, C'251,191,36', 7, "Segoe UI");

   // Baris 5: Circuit Guard Max Consecutive Loss
   string cbDisplay = "0/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss (Aman)";
   if (g_cooldownUntilTime > TimeCurrent()) cbDisplay = "COOLDOWN AKTIF";
   else if (g_consecutiveLossCount > 0) cbDisplay = IntegerToString(g_consecutiveLossCount) + " Loss";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L5", rightCardX + 8, currY + 97, "Circuit G. : " + cbDisplay, C'74,222,128', 7, "Segoe UI");

   // Baris 6: Disiplin Harian (Max Order)
   string discText = IntegerToString(g_todayTradesCount) + (InpUseMaxDailyTrades ? ("/" + IntegerToString(InpMaxDailyTrades)) : "") + " Order Hari Ini";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L6", rightCardX + 8, currY + 115, "Disiplin   : " + discText, C'148,163,184', 7, "Segoe UI");

   currY += 142;

   // 5. BARIS STATUS EKSEKUSI & ACTION (Y: 270 s/d 338, Tinggi 68px)
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", panelX + 8, currY, panelW - 16, 68, C'11,15,25', C'14,165,233');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", panelX + 16, currY + 6, "⚡ RADAR EKSEKUSI & STATUS SINYAL TERAKHIR:", C'56,189,248', 7, "Segoe UI Bold");

   // Tombol Emergency Close All
   CreateOrUpdateBtn("VIKAR_HUD_BTN_CLOSEALL", panelX + panelW - 104, currY + 6, 92, 24, "🚨 CLOSE ALL", C'153,27,27', clrWhite, 7);

   string statusDisplay = (g_lastSignalType != "") ? g_lastSignalType : "MENUNGGU SETUP GRADE A (SCANNING)";
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING ULANG";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 16, currY + 24, "● " + statusDisplay, clrWhite, 8, "Segoe UI Bold");

   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = (InpUsePointsTrailing || InpUseCandleTrailing || InpUseTrailingEMA21) ? "Trail: ON" : "Trail: OFF";
   string pendingInfo = (pendingCount > 0) ? (" | Pending: " + IntegerToString(pendingCount)) : "";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 16, currY + 44, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + pendingInfo, C'148,163,184', 7, "Segoe UI");

   int finalH = (currY + 74) - panelY;
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

    code = code[:start_idx] + executive_grid_code + "\n" + code[end_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] Successfully replaced UpdateDashboard with Executive 2-Column Grid Cockpit!")
    return True

if __name__ == '__main__':
    apply_executive_grid()
