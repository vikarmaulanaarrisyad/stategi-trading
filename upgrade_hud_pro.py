import os
import shutil

def apply_pro_hud():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Update g_panelW default width
    code = code.replace("int            g_panelW           = 355;", "int            g_panelW           = 390;")

    # 2. Define the new professional UpdateDashboard()
    new_hud_code = """//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (MODERN GLASSMORPHIC PRO GUI)     |
//+------------------------------------------------------------------+
void UpdateDashboard()
{
   if (!InpShowDashboard)
   {
      DestroyDashboardGUI();
      return;
   }

   Comment(""); // Bersihkan teks Comment biasa agar chart bersih

   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
   double spread  = PriceToPips(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));

   int openCount = 0;
   double openFloating = GetOpenFloatingPnL(openCount);

   // Hitung Statistik Sejak Start, Harian, dan Mingguan
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
   int panelW = 390;
   g_panelW = panelW;
   int cardW  = panelW - 16;
   int cardX  = panelX + 8;

   int totalH = InpShowPnLStats ? 560 : 482;
   g_panelH = totalH;

   // 1. Container Utama (Dark Slate Obsidian Card)
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, totalH, C'11,15,25', C'30,41,59');

   // 2. Header Banner (Deep Navy Gradient Accent)
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 46, C'15,23,42', C'2,132,199');
   CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + 44, panelW, 2, C'14,165,233', C'14,165,233');

   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 7, "◈ VIKAR 4-PILLAR PRO  v3.30", clrWhite, 10, "Segoe UI Bold");

   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot " + DoubleToString(currentLotSize, 2)) : ("Lot " + DoubleToString(currentLotSize, 2));
   string entryModeTag = (InpEntryMode == ENTRY_MARKET_INSTANT) ? "MARKET" : ((InpEntryMode == ENTRY_PENDING_LIMIT) ? "LIMIT (" + DoubleToString(InpLimitPullbackPips, 0) + "p)" : "STOP (" + DoubleToString(InpStopBufferPips, 0) + "p)");
   string headerSubStr = _Symbol + " • " + EnumToString(_Period) + " • " + entryModeTag + " • " + lotDisplay + " • ID: " + IntegerToString(InpMagicNumber);
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 26, headerSubStr, C'186,230,253', 7, "Segoe UI");

   // Tombol Geser Interaktif (Mini Badge)
   CreateOrUpdateRect("VIKAR_HUD_DRAG_BOX", panelX + panelW - 74, panelY + 11, 62, 22, C'11,15,25', C'14,165,233');
   CreateOrUpdateText("VIKAR_HUD_HDR_DRAG", panelX + panelW - 68, panelY + 14, "⠿ GESER", C'56,189,248', 7, "Segoe UI Bold");

   // 3. Card 1: Ringkasan Saldo & Ekuitas
   int currY = panelY + 54;
   CreateOrUpdateRect("VIKAR_HUD_ACC_BG", cardX, currY, cardW, 66, C'15,23,42', C'30,41,59');

   CreateOrUpdateText("VIKAR_HUD_ACC_LINE1", cardX + 10, currY + 7, "SALDO: $" + DoubleToString(balance, 2) + "  |  EKUITAS: $" + DoubleToString(equity, 2), clrWhite, 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_ACC_LINE2", cardX + 10, currY + 25, "FLOATING: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Posisi)  |  SPREAD: " + DoubleToString(spread, 1) + " pips", floatClr, 8, "Segoe UI Bold");

   string startStr = "Start: $" + DoubleToString(g_eaInitialBalance, 2) + " (" + TimeToString(g_eaStartTime, TIME_MINUTES) + ")  |  Pertumbuhan: " + (totalGrowthPct >= 0 ? "+" : "") + DoubleToString(totalGrowthPct, 1) + "%";
   CreateOrUpdateText("VIKAR_HUD_ACC_LINE3", cardX + 10, currY + 44, startStr, C'148,163,184', 7, "Segoe UI");
   currY += 72;

   // 4. Card 2: Rekap Profit & Loss Real-Time (Opsional Sesuai Input)
   if (InpShowPnLStats)
   {
      CreateOrUpdateRect("VIKAR_HUD_PNL_BG", cardX, currY, cardW, 74, C'17,24,39', C'51,65,85');
      CreateOrUpdateText("VIKAR_HUD_PNL_TITLE", cardX + 10, currY + 6, "📊 REKAP PERFORMA TRANSAKSI:", C'251,191,36', 8, "Segoe UI Bold");

      double dailyWinratePct = (statsDaily.totalTrades > 0) ? ((double)statsDaily.winTrades / statsDaily.totalTrades * 100.0) : 0.0;
      string dailyWRStr = (statsDaily.totalTrades > 0) ? (" (" + IntegerToString(statsDaily.winTrades) + "W/" + IntegerToString(statsDaily.lossTrades) + "L - " + DoubleToString(dailyWinratePct, 0) + "%)") : "";
      CreateOrUpdateText("VIKAR_HUD_PNL_DAY", cardX + 10, currY + 23, "• Hari Ini    : " + FormatPnL(statsDaily.netProfit) + dailyWRStr + " (+$" + DoubleToString(statsDaily.grossProfit, 1) + " / -$" + DoubleToString(statsDaily.grossLoss, 1) + ")", C'226,232,240', 7, "Segoe UI");

      CreateOrUpdateText("VIKAR_HUD_PNL_WEEK", cardX + 10, currY + 39, "• Minggu Ini  : " + FormatPnL(statsWeekly.netProfit) + " (+$" + DoubleToString(statsWeekly.grossProfit, 1) + " | -$" + DoubleToString(statsWeekly.grossLoss, 1) + ")", C'226,232,240', 7, "Segoe UI");

      color pnlTotalClr = (statsTotal.netProfit > 0) ? C'74,222,128' : (statsTotal.netProfit < 0 ? C'248,113,113' : clrWhite);
      double totalWinratePct = (statsTotal.totalTrades > 0) ? ((double)statsTotal.winTrades / statsTotal.totalTrades * 100.0) : 0.0;
      string winrateStr = (statsTotal.totalTrades > 0) ? (" | WR: " + DoubleToString(totalWinratePct, 1) + "%") : "";
      CreateOrUpdateText("VIKAR_HUD_PNL_TOTAL", cardX + 10, currY + 55, "• Sejak Start : " + FormatPnL(statsTotal.netProfit) + " (" + (totalGrowthPct >= 0 ? "+" : "") + DoubleToString(totalGrowthPct, 1) + "%) | " + IntegerToString(statsTotal.winTrades) + "W/" + IntegerToString(statsTotal.lossTrades) + "L" + winrateStr, pnlTotalClr, 7, "Segoe UI Bold");
      currY += 80;
   }

   // 5. Card 3: Analisis 4-Pilar & Multi-Confluence Institusional
   CreateOrUpdateRect("VIKAR_HUD_PILAR_BG", cardX, currY, cardW, 142, C'15,23,42', C'30,41,59');

   string scoreStr = (g_lastScoreResult.totalScore > 0) ? (DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")") : "Ready (Standby)";
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 65.0) ? C'251,191,36' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_PILAR_HDR", cardX + 10, currY + 6, "🏛️ ANALISIS 4-PILAR INSTITUSIONAL", C'56,189,248', 8, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_SCORE", cardX + cardW - 115, currY + 6, "Skor: " + scoreStr, scoreClr, 7, "Segoe UI Bold");

   string smcStr = (g_smcAnalysis.structureName != "") ? g_smcAnalysis.structureName : "Market Equilibrium (Scan)";
   if (g_smcAnalysis.hasSweep) smcStr += " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr += " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_PILAR1", cardX + 10, currY + 24, "SMC Struktur  : " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   if (currentFibo.isValid) rangeStr += " | GP: " + DoubleToString(currentFibo.level618, 2);
   CreateOrUpdateText("VIKAR_HUD_PILAR2", cardX + 10, currY + 40, "Dealing Range : " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   string emaTrendStr = "BULLISH (Di Atas 125)";
   if (CopyBuffer(h_ema125, 0, 0, 2, ema125Val) >= 2)
   {
      double closePrice = iClose(_Symbol, _Period, 1);
      emaTrendStr = (closePrice > ema125Val[1]) ? "BULLISH (Di Atas 125)" : "BEARISH (Di Bawah 125)";
   }
   CreateOrUpdateText("VIKAR_HUD_PILAR4", cardX + 10, currY + 56, "Triple EMA    : " + emaTrendStr + " | Ribbon 8/21", C'232,121,249', 7, "Segoe UI");

   string obStr = "OB: Scanning Zona...";
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
      obStr = "Bull OB " + DoubleToString(g_bullishOB.bottom, 1) + "-" + DoubleToString(g_bullishOB.top, 1) + " (Disp " + DoubleToString(g_bullishOB.displacementAtr, 1) + "x)";
   else if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
      obStr = "Bear OB " + DoubleToString(g_bearishOB.bottom, 1) + "-" + DoubleToString(g_bearishOB.top, 1) + " (Disp " + DoubleToString(g_bearishOB.displacementAtr, 1) + "x)";
   else if (g_activeFVG.isValid)
      obStr = "FVG " + DoubleToString(g_activeFVG.bottom, 1) + "-" + DoubleToString(g_activeFVG.top, 1);
   CreateOrUpdateText("VIKAR_HUD_OB_FVG", cardX + 10, currY + 72, "Order Block   : " + obStr, C'244,114,182', 7, "Segoe UI");

   CreateOrUpdateText("VIKAR_HUD_PILAR5", cardX + 10, currY + 88, "S/R Daily     : P: " + DoubleToString(currentPivot.P, 2) + " [R1: " + DoubleToString(currentPivot.R1, 2) + " | S1: " + DoubleToString(currentPivot.S1, 2) + "]", C'148,163,184', 7, "Segoe UI");

   string candleStr = (g_candleAnalysis.patternName != "") ? g_candleAnalysis.patternName : "Formasi Lilin Normal (Scanning)";
   if (g_candleAnalysis.score > 0) candleStr += " [Skor " + DoubleToString(g_candleAnalysis.score, 0) + "/100]";
   color candleClr = g_candleAnalysis.isHighQuality ? C'251,191,36' : C'203,213,225';
   CreateOrUpdateText("VIKAR_HUD_PILAR3", cardX + 10, currY + 104, "Pola Lilin    : " + candleStr, candleClr, 7, "Segoe UI");

   string patStr = g_chartPattern.isValid ? (g_chartPattern.patternName + " [" + DoubleToString(g_chartPattern.score, 0) + "p]") : "Scanning Geometri Pattern...";
   color patClr = g_chartPattern.isValid ? (g_chartPattern.isBullish ? C'74,222,128' : C'248,113,113') : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_CHART_PAT", cardX + 10, currY + 120, "Pola Chart    : " + patStr, patClr, 7, "Segoe UI Bold");
   currY += 148;

   // 6. Card 4: Sensor Risiko, AI Guardian & Market Regime
   CreateOrUpdateRect("VIKAR_HUD_RISK_BG", cardX, currY, cardW, 118, C'15,23,42', C'30,41,59');
   CreateOrUpdateText("VIKAR_HUD_RISK_HDR", cardX + 10, currY + 6, "🛡️ SENSOR PASAR & PROTEKSI MODAL", C'52,211,153', 8, "Segoe UI Bold");

   string regimeStr = "NORMAL (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
   color regimeClr  = C'74,222,128';
   if (g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
   {
      regimeStr = "CHOPPY / FAKEOUT RISK (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
      regimeClr = C'248,113,113';
   }
   else if (g_currentRegime == REGIME_STRONG_TREND)
   {
      regimeStr = "STRONG TREND (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
      regimeClr = C'56,189,248';
   }
   CreateOrUpdateText("VIKAR_HUD_REGIME", cardX + 10, currY + 23, "Cuaca Pasar   : " + regimeStr, regimeClr, 7, "Segoe UI Bold");

   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   string htfText = InpUseHTFFilter ? g_htfMacroStr : "FILTER OFF";
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", cardX + 10, currY + 39, "Macro " + EnumToString(InpHTFTimeframe) + " Trend: " + htfText, htfClr, 7, "Segoe UI Bold");

   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Institutional Volume") : "VSA: OFF";
   color vsaClr = (StringFind(vsaDisplay, "CLIMAX") >= 0) ? C'74,222,128' : ((StringFind(vsaDisplay, "NO-SUPPLY") >= 0) ? C'56,189,248' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_VSA", cardX + 10, currY + 55, "VSA Footprint : " + vsaDisplay, vsaClr, 7, "Segoe UI");

   string pfStr = InpUseEquityGuardian ? ("DD: " + DoubleToString(g_currentDailyDDPct, 1) + "% / Max " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%") : "OFF";
   color pfClr = (g_currentDailyDDPct >= InpMaxDailyEquityDDPct * 0.75) ? C'248,113,113' : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_PROPFIRM", cardX + 10, currY + 71, "Prop Firm Guard: " + pfStr + " | Trap Hunter: AKTIF", pfClr, 7, "Segoe UI");

   string cbDisplay = "Normal (0/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss)";
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
   CreateOrUpdateText("VIKAR_HUD_CB", cardX + 10, currY + 87, "Circuit Guard : " + cbDisplay + " | AI Brain: STANDBY", cbClr, 7, "Segoe UI");

   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", cardX + 10, currY + 103, "News & Shield : " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI");
   currY += 124;

   // 7. Card 5: Status Eksekusi Langsung & Konfigurasi Aktif
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", cardX, currY, cardW, 56, C'11,15,25', C'14,165,233');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", cardX + 10, currY + 6, "⚡ STATUS EKSEKUSI PASAR:", C'56,189,248', 7, "Segoe UI Bold");

   string statusDisplay = (g_lastSignalType != "") ? g_lastSignalType : "MENUNGGU SETUP GRADE A (SCANNING)";
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING SETUP";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", cardX + 10, currY + 22, statusDisplay, clrWhite, 7, "Segoe UI Bold");

   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = (InpUsePointsTrailing || InpUseCandleTrailing || InpUseTrailingEMA21) ? "Trail: ON" : "Trail: OFF";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", cardX + 10, currY + 39, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + " | Lot: " + DoubleToString(currentLotSize, 2), C'148,163,184', 7, "Segoe UI");
}
"""

    start_idx = code.find("void UpdateDashboard()")
    end_idx = code.find("void OnChartEvent(")
    if start_idx == -1 or end_idx == -1:
        print("[-] Could not find UpdateDashboard boundaries!")
        return False

    code = code[:start_idx] + new_hud_code + "\n" + code[end_idx:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] Successfully replaced UpdateDashboard with Professional Modular GUI!")
    return True

if __name__ == '__main__':
    apply_pro_hud()
