import os
import shutil

def apply_cockpit():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Update g_panelW to 430
    code = code.replace("int            g_panelW           = 390;", "int            g_panelW           = 430;")

    # 2. Add global state variables if not already present
    global_anchor = "int            g_dragOffsetY      = 0;"
    global_insert = """int            g_dragOffsetY      = 0;
bool           g_hudMinimized     = false;
ENUM_ENTRY_EXECUTION_MODE g_activeEntryMode = ENTRY_PENDING_STOP;
bool           g_eaManualPause    = false;"""
    if global_anchor in code and "g_hudMinimized" not in code:
        code = code.replace(global_anchor, global_insert)
        print("[+] Added g_hudMinimized, g_activeEntryMode, g_eaManualPause")

    # 3. Add CreateOrUpdateBtn & MakeProgressBar helpers right after CreateOrUpdateText
    helper_anchor = """void DestroyDashboardGUI()"""
    btn_helper = """//+------------------------------------------------------------------+
//| PEMBUATAN ELEMEN TOMBOL INTERAKTIF (OBJ_BUTTON)                 |
//+------------------------------------------------------------------+
void CreateOrUpdateBtn(string name, int x, int y, int width, int height, string text, color bgColor, color textColor, int fontSize = 8, string font = "Segoe UI Bold")
{
   if (ObjectFind(0, name) < 0)
   {
      ObjectCreate(0, name, OBJ_BUTTON, 0, 0, 0);
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetString(0, name, OBJPROP_FONT, font);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
      ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
      ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor);
      ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, C'51,65,85');
      ObjectSetInteger(0, name, OBJPROP_STATE, false);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   }
   else
   {
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
      ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor);
      ObjectSetInteger(0, name, OBJPROP_STATE, false);
   }
}

//+------------------------------------------------------------------+
//| METER VISUAL ASCII/UNICODE PROGRESS BAR                         |
//+------------------------------------------------------------------+
string MakeProgressBar(double value, double maxVal, int barLen = 8)
{
   if (maxVal <= 0.0) return "[░░░░░░░░]";
   double ratio = MathMin(MathMax(value / maxVal, 0.0), 1.0);
   int filled = (int)MathRound(ratio * barLen);
   string bar = "[";
   for (int i = 0; i < barLen; i++)
   {
      if (i < filled) bar += "█";
      else bar += "░";
   }
   bar += "]";
   return bar;
}

"""
    if "void CreateOrUpdateBtn" not in code:
        code = code.replace(helper_anchor, btn_helper + helper_anchor)
        print("[+] Added CreateOrUpdateBtn & MakeProgressBar")

    # 4. Replace InpEntryMode checks with g_activeEntryMode in execution
    code = code.replace("if (InpEntryMode == ENTRY_MARKET_INSTANT)", "if (g_activeEntryMode == ENTRY_MARKET_INSTANT)")
    code = code.replace("else if (InpEntryMode == ENTRY_PENDING_LIMIT)", "else if (g_activeEntryMode == ENTRY_PENDING_LIMIT)")
    code = code.replace("else if (InpEntryMode == ENTRY_PENDING_STOP)", "else if (g_activeEntryMode == ENTRY_PENDING_STOP)")

    # 5. In OnInit, initialize g_activeEntryMode = InpEntryMode;
    init_anchor = "g_activeEntryMode = InpEntryMode;"
    if init_anchor not in code:
        code = code.replace("EventSetTimer(1);", "g_activeEntryMode = InpEntryMode;\n   EventSetTimer(1);")
        print("[+] Initialized g_activeEntryMode in OnInit()")

    # 6. In OnTick, add pause check
    tick_anchor = "AutoCalibrateTradingParameters();"
    pause_check = """AutoCalibrateTradingParameters();
   if (g_eaManualPause)
   {
      g_lastSignalType = "PAUSED (TRADING DIHENTIKAN MANUAL VIA BUTTON)";
      return;
   }"""
    if tick_anchor in code and "g_eaManualPause" not in code[code.find(tick_anchor):code.find(tick_anchor)+120]:
        code = code.replace(tick_anchor, pause_check, 1)
        print("[+] Added g_eaManualPause check in OnTick()")

    # 7. Update OnChartEvent to handle button clicks
    chart_event_old = """   if (id == CHARTEVENT_MOUSE_MOVE)"""
    btn_click_code = """   if (id == CHARTEVENT_OBJECT_CLICK)
   {
      if (sparam == "VIKAR_HUD_BTN_VIEW")
      {
         g_hudMinimized = !g_hudMinimized;
         DestroyDashboardGUI();
         UpdateDashboard();
         ChartRedraw(0);
         return;
      }
      else if (sparam == "VIKAR_HUD_BTN_MODE")
      {
         if (g_activeEntryMode == ENTRY_MARKET_INSTANT)
            g_activeEntryMode = ENTRY_PENDING_STOP;
         else if (g_activeEntryMode == ENTRY_PENDING_STOP)
            g_activeEntryMode = ENTRY_PENDING_LIMIT;
         else
            g_activeEntryMode = ENTRY_MARKET_INSTANT;

         UpdateDashboard();
         ChartRedraw(0);
         return;
      }
      else if (sparam == "VIKAR_HUD_BTN_PAUSE")
      {
         g_eaManualPause = !g_eaManualPause;
         UpdateDashboard();
         ChartRedraw(0);
         return;
      }
      else if (sparam == "VIKAR_HUD_BTN_CLOSEALL")
      {
         CloseAllOpenOrders();
         UpdateDashboard();
         ChartRedraw(0);
         return;
      }
   }

   if (id == CHARTEVENT_MOUSE_MOVE)"""

    if chart_event_old in code and "CHARTEVENT_OBJECT_CLICK" not in code:
        code = code.replace(chart_event_old, btn_click_code, 1)
        print("[+] Added button click handling in OnChartEvent()")

    # 8. Define the Institutional Cyber-Cockpit UpdateDashboard()
    new_hud_body = """//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (PRO CYBER-COCKPIT GUI v3.30)     |
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
   int panelW = 430;
   g_panelW = panelW;
   int cardW  = panelW - 16;
   int cardX  = panelX + 8;

   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));
   string entryModeTag = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MARKET" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "BUY/SELL STOP" : "BUY/SELL LIMIT");
   string btnModeText  = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MODE: MKT" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "MODE: STOP" : "MODE: LIMIT");

   // ===================================================================
   // JIKA DALAM MODE MINIMIZED (HANYA BILAH RINGKAS ATAS)
   // ===================================================================
   if (g_hudMinimized)
   {
      int minH = 48;
      g_panelH = minH;
      CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, minH, C'11,15,25', C'30,41,59');
      CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + minH - 2, panelW, 2, C'14,165,233', C'14,165,233');

      CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 8, "◈ VIKAR PRO v3.30", clrWhite, 9, "Segoe UI Bold");
      color floatClrMin = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
      string minStatus = "Float: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + "P) | Eq: $" + DoubleToString(equity, 2);
      CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 26, minStatus, floatClrMin, 7, "Segoe UI Bold");

      CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 74, panelY + 11, 64, 26, "👁️ EXPAND", C'15,23,42', C'52,211,153', 7);
      ChartRedraw(0);
      return;
   }

   // ===================================================================
   // MODE EXPANDED (FULL INSTITUTIONAL COCKPIT)
   // ===================================================================

   // 1. Header Banner
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 48, C'15,23,42', C'2,132,199');
   CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + 46, panelW, 2, C'14,165,233', C'14,165,233');

   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 7, "◈ VIKAR 4-PILLAR PRO  v3.30", clrWhite, 10, "Segoe UI Bold");

   string pauseStatus = g_eaManualPause ? "[PAUSED]" : "[ACTIVE]";
   string headerSubStr = _Symbol + " • " + EnumToString(_Period) + " • " + lotDisplay + " • " + pauseStatus + " • ID: " + IntegerToString(InpMagicNumber);
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 26, headerSubStr, C'186,230,253', 7, "Segoe UI");

   // Header Interactive Buttons
   CreateOrUpdateBtn("VIKAR_HUD_BTN_MODE", panelX + panelW - 170, panelY + 11, 88, 26, btnModeText, C'11,15,25', C'56,189,248', 7);
   CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 76, panelY + 11, 68, 26, "👁️ MINI", C'11,15,25', C'52,211,153', 7);

   // 2. Card 1: Saldo, Ekuitas & Prop Firm Guardian
   int currY = panelY + 56;
   CreateOrUpdateRect("VIKAR_HUD_ACC_BG", cardX, currY, cardW, 86, C'15,23,42', C'30,41,59');

   CreateOrUpdateText("VIKAR_HUD_ACC_LINE1", cardX + 10, currY + 7, "SALDO: $" + DoubleToString(balance, 2) + "  |  EKUITAS: $" + DoubleToString(equity, 2) + "  |  FREE: $" + DoubleToString(AccountInfoDouble(ACCOUNT_MARGIN_FREE), 2), clrWhite, 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   string floatLotsStr = "FLOATING PnL : " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Posisi / " + DoubleToString(totalLots, 2) + " Lot)  |  SPREAD: " + DoubleToString(spread, 1) + " pips";
   CreateOrUpdateText("VIKAR_HUD_ACC_LINE2", cardX + 10, currY + 25, floatLotsStr, floatClr, 8, "Segoe UI Bold");

   string startStr = "Start Modal: $" + DoubleToString(g_eaInitialBalance, 2) + " (" + TimeToString(g_eaStartTime, TIME_MINUTES) + ")  |  Pertumbuhan: " + (totalGrowthPct >= 0 ? "+" : "") + DoubleToString(totalGrowthPct, 1) + "%";
   CreateOrUpdateText("VIKAR_HUD_ACC_LINE3", cardX + 10, currY + 44, startStr, C'148,163,184', 7, "Segoe UI");

   // Prop Firm Drawdown Meter Bar
   double ddLimit = InpMaxDailyEquityDDPct;
   string ddBar = MakeProgressBar(g_currentDailyDDPct, ddLimit, 8);
   color ddClr = (g_currentDailyDDPct >= ddLimit * 0.75) ? C'248,113,113' : ((g_currentDailyDDPct > 0.0) ? C'251,191,36' : C'74,222,128');
   double bufferSisa = MathMax(0.0, ddLimit - g_currentDailyDDPct);
   string ddStr = "Daily DD: " + DoubleToString(g_currentDailyDDPct, 2) + "% / Max " + DoubleToString(ddLimit, 1) + "%  " + ddBar + "  Buffer Sisa: " + DoubleToString(bufferSisa, 2) + "% (" + (bufferSisa > 1.0 ? "AMAN" : "WASPADA") + ")";
   CreateOrUpdateText("VIKAR_HUD_ACC_LINE4", cardX + 10, currY + 63, ddStr, ddClr, 7, "Segoe UI Bold");
   currY += 92;

   // 3. Card 2: Rekap Profit & Loss Real-Time (Opsional)
   if (InpShowPnLStats)
   {
      CreateOrUpdateRect("VIKAR_HUD_PNL_BG", cardX, currY, cardW, 76, C'17,24,39', C'51,65,85');
      CreateOrUpdateText("VIKAR_HUD_PNL_TITLE", cardX + 10, currY + 6, "📊 REKAP PROFIT REAL-TIME & WINRATE:", C'251,191,36', 8, "Segoe UI Bold");

      double dailyWinratePct = (statsDaily.totalTrades > 0) ? ((double)statsDaily.winTrades / statsDaily.totalTrades * 100.0) : 0.0;
      string dailyWRStr = (statsDaily.totalTrades > 0) ? (" (WR: " + DoubleToString(dailyWinratePct, 0) + "% - " + IntegerToString(statsDaily.winTrades) + "W/" + IntegerToString(statsDaily.lossTrades) + "L)") : "";
      CreateOrUpdateText("VIKAR_HUD_PNL_DAY", cardX + 10, currY + 23, "• Hari Ini    : Net " + FormatPnL(statsDaily.netProfit) + dailyWRStr + "  [+$" + DoubleToString(statsDaily.grossProfit, 1) + " / -$" + DoubleToString(statsDaily.grossLoss, 1) + "]", C'226,232,240', 7, "Segoe UI");

      CreateOrUpdateText("VIKAR_HUD_PNL_WEEK", cardX + 10, currY + 40, "• Minggu Ini  : Net " + FormatPnL(statsWeekly.netProfit) + "  (Profit: +$" + DoubleToString(statsWeekly.grossProfit, 1) + " | Loss: -$" + DoubleToString(statsWeekly.grossLoss, 1) + ")", C'226,232,240', 7, "Segoe UI");

      color pnlTotalClr = (statsTotal.netProfit > 0) ? C'74,222,128' : (statsTotal.netProfit < 0 ? C'248,113,113' : clrWhite);
      double totalWinratePct = (statsTotal.totalTrades > 0) ? ((double)statsTotal.winTrades / statsTotal.totalTrades * 100.0) : 0.0;
      string winrateStr = (statsTotal.totalTrades > 0) ? (" | WR: " + DoubleToString(totalWinratePct, 1) + "%") : "";
      CreateOrUpdateText("VIKAR_HUD_PNL_TOTAL", cardX + 10, currY + 57, "• Sejak Start : Net " + FormatPnL(statsTotal.netProfit) + " (" + (totalGrowthPct >= 0 ? "+" : "") + DoubleToString(totalGrowthPct, 1) + "%) | " + IntegerToString(statsTotal.winTrades) + "W / " + IntegerToString(statsTotal.lossTrades) + "L" + winrateStr, pnlTotalClr, 7, "Segoe UI Bold");
      currY += 82;
   }

   // 4. Card 3: Status 4-Pilar & Skor Konfluensi
   CreateOrUpdateRect("VIKAR_HUD_PILAR_BG", cardX, currY, cardW, 148, C'15,23,42', C'30,41,59');

   string scoreStr = (g_lastScoreResult.totalScore > 0) ? (DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")") : "Ready (Standby)";
   string scoreGauge = MakeProgressBar(g_lastScoreResult.totalScore, 100.0, 6);
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 65.0) ? C'251,191,36' : C'203,213,225');

   CreateOrUpdateText("VIKAR_HUD_PILAR_HDR", cardX + 10, currY + 6, "🏛️ STATUS ENGINE 4-PILAR SMC & KONFLUENSI", C'56,189,248', 8, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_SCORE", cardX + cardW - 145, currY + 6, "Skor: " + scoreGauge + " " + scoreStr, scoreClr, 7, "Segoe UI Bold");

   string smcStr = (g_smcAnalysis.structureName != "") ? g_smcAnalysis.structureName : "Market Equilibrium (Scan)";
   if (g_smcAnalysis.hasSweep) smcStr += " [LIQUIDITY SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr += " [BOS CONFIRMED]";
   CreateOrUpdateText("VIKAR_HUD_PILAR1", cardX + 10, currY + 24, "• SMC Struktur : " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   if (currentFibo.isValid) rangeStr += " | Fibo GP 61.8%: " + DoubleToString(currentFibo.level618, 2);
   CreateOrUpdateText("VIKAR_HUD_PILAR2", cardX + 10, currY + 41, "• Dealing Range: " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   string emaTrendStr = "BULLISH (Di Atas EMA 125 Baseline)";
   if (CopyBuffer(h_ema125, 0, 0, 2, ema125Val) >= 2)
   {
      double closePrice = iClose(_Symbol, _Period, 1);
      emaTrendStr = (closePrice > ema125Val[1]) ? "BULLISH (Di Atas EMA 125)" : "BEARISH (Di Bawah EMA 125)";
   }
   CreateOrUpdateText("VIKAR_HUD_PILAR4", cardX + 10, currY + 58, "• Triple EMA   : " + emaTrendStr + " | Ribbon 8/21: AKTIF", C'232,121,249', 7, "Segoe UI");

   string obStr = "Scanning Zona Mitigasi...";
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
      obStr = "Bull OB " + DoubleToString(g_bullishOB.bottom, 1) + " - " + DoubleToString(g_bullishOB.top, 1) + " (Disp " + DoubleToString(g_bullishOB.displacementAtr, 1) + "x ATR)";
   else if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
      obStr = "Bear OB " + DoubleToString(g_bearishOB.bottom, 1) + " - " + DoubleToString(g_bearishOB.top, 1) + " (Disp " + DoubleToString(g_bearishOB.displacementAtr, 1) + "x ATR)";
   else if (g_activeFVG.isValid)
      obStr = "FVG Imbalance " + DoubleToString(g_activeFVG.bottom, 1) + " - " + DoubleToString(g_activeFVG.top, 1);
   CreateOrUpdateText("VIKAR_HUD_OB_FVG", cardX + 10, currY + 75, "• Order Block  : " + obStr, C'244,114,182', 7, "Segoe UI");

   CreateOrUpdateText("VIKAR_HUD_PILAR5", cardX + 10, currY + 92, "• Daily Pivots : P: " + DoubleToString(currentPivot.P, 2) + " [R1: " + DoubleToString(currentPivot.R1, 2) + " | S1: " + DoubleToString(currentPivot.S1, 2) + "]", C'148,163,184', 7, "Segoe UI");

   string candleStr = (g_candleAnalysis.patternName != "") ? g_candleAnalysis.patternName : "Formasi Lilin Normal (Scanning)";
   if (g_candleAnalysis.score > 0) candleStr += " [Skor " + DoubleToString(g_candleAnalysis.score, 0) + "/100]";
   color candleClr = g_candleAnalysis.isHighQuality ? C'251,191,36' : C'203,213,225';
   CreateOrUpdateText("VIKAR_HUD_PILAR3", cardX + 10, currY + 109, "• Candlestick  : " + candleStr, candleClr, 7, "Segoe UI");

   string patStr = g_chartPattern.isValid ? (g_chartPattern.patternName + " [" + DoubleToString(g_chartPattern.score, 0) + "p]") : "Scanning Geometri Chart Pattern...";
   color patClr = g_chartPattern.isValid ? (g_chartPattern.isBullish ? C'74,222,128' : C'248,113,113') : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_CHART_PAT", cardX + 10, currY + 126, "• Chart Pattern: " + patStr, patClr, 7, "Segoe UI Bold");
   currY += 154;

   // 5. Card 4: Sensor Pasar, AI Regime & Intelejensi Risiko
   CreateOrUpdateRect("VIKAR_HUD_RISK_BG", cardX, currY, cardW, 118, C'15,23,42', C'30,41,59');
   CreateOrUpdateText("VIKAR_HUD_RISK_HDR", cardX + 10, currY + 6, "🛡️ RADAR SENSOR PASAR & INTELEJENSI RISIKO", C'52,211,153', 8, "Segoe UI Bold");

   string regimeStr = "NORMAL / TRENDING SEHAT (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
   color regimeClr  = C'74,222,128';
   if (g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
   {
      regimeStr = "CHOPPY / FAKEOUT RISK (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
      regimeClr = C'248,113,113';
   }
   else if (g_currentRegime == REGIME_STRONG_TREND)
   {
      regimeStr = "STRONG MOMENTUM TREND (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
      regimeClr = C'56,189,248';
   }
   CreateOrUpdateText("VIKAR_HUD_REGIME", cardX + 10, currY + 23, "• Cuaca Pasar  : " + regimeStr, regimeClr, 7, "Segoe UI Bold");

   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   string htfText = InpUseHTFFilter ? g_htfMacroStr : "FILTER MACRO OFF";
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", cardX + 10, currY + 40, "• Macro Trend  : H1 Macro " + htfText, htfClr, 7, "Segoe UI Bold");

   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Institutional Volume") : "VSA: OFF";
   color vsaClr = (StringFind(vsaDisplay, "CLIMAX") >= 0) ? C'74,222,128' : ((StringFind(vsaDisplay, "NO-SUPPLY") >= 0) ? C'56,189,248' : C'203,213,225');
   string adxStr = InpUseADXFilter ? ("ADX Power: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   CreateOrUpdateText("VIKAR_HUD_VSA", cardX + 10, currY + 57, "• Volume & ADX : " + vsaDisplay + " | " + adxStr, vsaClr, 7, "Segoe UI");

   string cbDisplay = "0/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss (Aman)";
   color cbClr = C'74,222,128';
   if (g_cooldownUntilTime > TimeCurrent())
   {
      int remMins = (int)((g_cooldownUntilTime - TimeCurrent()) / 60);
      cbDisplay = "COOLDOWN (" + IntegerToString(remMins) + " Mnt Sisa)";
      cbClr = C'248,113,113';
   }
   else if (g_dailyLossLimitHit)
   {
      cbDisplay = "DAILY LOCK REACHED";
      cbClr = C'248,113,113';
   }
   else if (g_consecutiveLossCount > 0)
   {
      cbDisplay = IntegerToString(g_consecutiveLossCount) + "/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss";
      cbClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_CB", cardX + 10, currY + 74, "• Circuit Guard: " + cbDisplay + " | AI Brain Self-Heal: STANDBY", cbClr, 7, "Segoe UI");

   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", cardX + 10, currY + 91, "• News & Shield: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI");

   string discStatus = "AKTIF";
   color discClr = C'74,222,128';
   if (g_dailyProfitLocked) { discStatus = "LOCKED (PROFIT HARIAN TERCAPAI)"; discClr = C'251,191,36'; }
   else if (IsInRolloverWindowMQL5()) { discStatus = "ROLLOVER FREEZE (MALAM)"; discClr = C'248,113,113'; }
   string discStr = "Order Hari Ini: " + IntegerToString(g_todayTradesCount) + (InpUseMaxDailyTrades ? ("/" + IntegerToString(InpMaxDailyTrades)) : "") + " | Disiplin: " + discStatus;
   CreateOrUpdateText("VIKAR_HUD_PRODISCIPLINE", cardX + 10, currY + 107, "• Target Disiplin: " + discStr, discClr, 7, "Segoe UI");
   currY += 124;

   // 6. Card 5: Radar Eksekusi & Status Sinyal Terakhir
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", cardX, currY, cardW, 68, C'11,15,25', C'14,165,233');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", cardX + 10, currY + 6, "⚡ RADAR EKSEKUSI & STATUS SINYAL TERAKHIR:", C'56,189,248', 7, "Segoe UI Bold");

   // Emergency Close All Button on Right
   CreateOrUpdateBtn("VIKAR_HUD_BTN_CLOSEALL", cardX + cardW - 100, currY + 8, 92, 28, "🚨 CLOSE ALL", C'153,27,27', clrWhite, 7);

   string statusDisplay = (g_lastSignalType != "") ? g_lastSignalType : "MENUNGGU SETUP GRADE A (SCANNING PASAR)";
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING ULANG";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", cardX + 10, currY + 23, "● " + statusDisplay, clrWhite, 8, "Segoe UI Bold");

   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = (InpUsePointsTrailing || InpUseCandleTrailing || InpUseTrailingEMA21) ? "Trail: ON" : "Trail: OFF";
   string pendingInfo = (pendingCount > 0) ? (" | Pending: " + IntegerToString(pendingCount) + " Aktif") : "";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", cardX + 10, currY + 44, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + pendingInfo, C'148,163,184', 7, "Segoe UI");

   int finalH = (currY + 76) - panelY;
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

    code = code[:start_idx] + new_hud_body + "\n" + code[end_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] Institutional Cyber-Cockpit Dashboard successfully integrated!")
    return True

if __name__ == '__main__':
    apply_cockpit()
