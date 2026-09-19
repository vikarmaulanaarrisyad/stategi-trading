# -*- coding: utf-8 -*-
"""
Script untuk menerapkan v2.2 Apex Institutional ke VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5:
1. Volume Spread Analysis (VSA Footprint Engine)
2. Multi-Stage Structural Trailing Stop (SMC Swing HL/LH Runner)
3. Daily Equity Guard & Consecutive Loss Circuit Breaker (SL+ = Win!)
"""

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Version & Description Header
old_header = """#property version   "2.10"
#property description "Robot Trading MT5 Institusional 4 Pilar Terpadu (v2.1 Master Intelligence)"
#property description "1. SMC Core: BOS, CHoCH, Liquidity Sweep, Discount/Premium Matrix"
#property description "2. Order Block Engine (Displacement ATR) & Multi-Bar FVG Tracker"
#property description "3. Chart Pattern Engine (W/M, Quasimodo QM, Head & Shoulders, Flags)"
#property description "4. Advanced Candlestick Intelligence (Soldiers, Harami, Piercing, Doji)"
#property description "5. Confluence Score (0-100), Shock Guard News & On-Chart Visualizer\""""

new_header = """#property version   "2.20"
#property description "Robot Trading MT5 Institusional 4 Pilar Terpadu (v2.2 Apex Institutional)"
#property description "1. SMC Core: BOS, CHoCH, Liquidity Sweep, Discount/Premium Matrix"
#property description "2. Order Block Engine (Displacement ATR) & Multi-Bar FVG Tracker"
#property description "3. Chart Pattern Engine (W/M, Quasimodo QM, Head & Shoulders, Flags)"
#property description "4. Advanced Candlestick Intelligence & Volume Spread Analysis (VSA Footprint)"
#property description "5. Multi-Stage Structural Trailing Stop & Daily Circuit Breaker Guard\""""

assert old_header in content, "Header match failed!"
content = content.replace(old_header, new_header, 1)

# 2. Structural Trailing Inputs
old_partial = """// --- Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner) ---
input bool          InpUsePartialClose    = true;                  // Aktifkan Partial Take Profit (Amankan 50% di TP1)
input double        InpPartialClosePercent= 50.0;                  // Persentase Lot Ditutup di TP1 (Default: 50%)
input ENUM_BE_MODE  InpPartialTriggerMode = BE_MODE_PIPS;          // Model Pemicu TP1 (Pips / Risk-Reward)
input double        InpPartialTriggerPips = 18.0;                 // Jarak Profit Pemicu TP1 (Pips, Mode Pips)
input double        InpPartialRRTrigger   = 1.5;                   // Pemicu TP1 Saat Mencapai R:R (1.5 = 1:1.5, Mode RR)
input bool          InpPartialMoveSLPlus  = true;                  // Otomatis Geser Sisa Lot ke SL+ Setelah TP1 Ambil Untung"""

new_partial = """// --- Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner) ---
input bool          InpUsePartialClose    = true;                  // Aktifkan Partial Take Profit (Amankan 50% di TP1)
input double        InpPartialClosePercent= 50.0;                  // Persentase Lot Ditutup di TP1 (Default: 50%)
input ENUM_BE_MODE  InpPartialTriggerMode = BE_MODE_PIPS;          // Model Pemicu TP1 (Pips / Risk-Reward)
input double        InpPartialTriggerPips = 18.0;                 // Jarak Profit Pemicu TP1 (Pips, Mode Pips)
input double        InpPartialRRTrigger   = 1.5;                   // Pemicu TP1 Saat Mencapai R:R (1.5 = 1:1.5, Mode RR)
input bool          InpPartialMoveSLPlus  = true;                  // Otomatis Geser Sisa Lot ke SL+ Setelah TP1 Ambil Untung

// --- Multi-Stage Structural Trailing Stop (SMC Swing High/Low Runner) ---
input bool          InpUseStructuralTrailing       = true;         // Trailing Stop Struktur Ayunan SMC (HL/LH) untuk Runner
input double        InpStructuralTrailingAtrBuffer = 0.5;          // Buffer Jarak dari Swing HL/LH (x ATR)"""

assert old_partial in content, "Partial inputs match failed!"
content = content.replace(old_partial, new_partial, 1)

# 3. Circuit Breaker & VSA Inputs
idx_g8 = content.find('input group "=== 8. FILTER PROTEKSI & WAKTU SESI PASAR ==="')
assert idx_g8 != -1, "Group 8 find failed!"
idx_g9 = content.find('input group "=== 9. ON-CHART SMC VISUALIZER', idx_g8)
assert idx_g9 != -1, "Group 9 find failed!"

g8_snippet = content[idx_g8:idx_g9]

new_g8_snippet = g8_snippet.strip() + "\n\n" + """input group "=== 8.1 PROTEKSI AKUN & CIRCUIT BREAKER ==="
input bool          InpUseConsecutiveLossGuard = true;          // Jeda Anti-Overtrading Pasca-Loss Berturut-turut
input int           InpMaxConsecutiveLosses    = 2;             // Batas Loss Berturut-turut Hari Ini (Default: 2)
input int           InpCooldownHours           = 4;             // Durasi Istirahat Robot Pasca-Loss (Jam)
input bool          InpUseDailyLossLimit       = true;          // Batasi Maksimal Kerugian Harian (% Modal)
input double        InpMaxDailyLossPercent     = 2.5;           // Batas Maksimal Kerugian Harian (% Saldo Awal Hari Ini)

input group "=== 8.2 VOLUME SPREAD ANALYSIS (VSA INSTITUSIONAL) ==="
input bool          InpUseVSA                  = true;          // Aktifkan Analisis Volume Footprint Institusional
input int           InpVSALookbackBars         = 20;            // Periode Rata-rata Volume Lilin Acuan (Bars)
input double        InpVSAClimaxRatio          = 1.75;          // Batas Lonjakan Volume Climax / Absorption (x Rata-rata)
input double        InpVSANoSupplyRatio        = 0.85;          // Batas Volume Kering / No-Supply Pullback (x Rata-rata)

"""

content = content[:idx_g8] + new_g8_snippet + content[idx_g9:]

# 4. ConfluenceScoreResult struct additions
old_score_res = """   double candlePts;        // Max 10
   double chartPatternPts;  // Max 15 (Bonus Pola Grafik)
   string details;
};"""

new_score_res = """   double candlePts;        // Max 10
   double chartPatternPts;  // Max 15 (Bonus Pola Grafik)
   double vsaPts;           // Max 10 (Bonus VSA Volume Climax / No-Supply)
   string vsaStatus;        // "CLIMAX ABSORPTION (+10)", "NO-SUPPLY PULLBACK (+5)", "NORMAL"
   string details;
};"""

assert old_score_res in content, "Score result struct match failed!"
content = content.replace(old_score_res, new_score_res, 1)

# 5. Global variables additions
old_globals = """bool                 g_shockGuardActive  = false;
datetime             g_lastShockTime     = 0;
int                  g_shockCooldownLeft = 0;

string         g_lastSignalType = "MENUNGGU SETUP";"""

new_globals = """bool                 g_shockGuardActive  = false;
datetime             g_lastShockTime     = 0;
int                  g_shockCooldownLeft = 0;

// Variabel Status Circuit Breaker & VSA Institusional (v2.2)
int                  g_consecutiveLossCount = 0;
datetime             g_lastLossTime         = 0;
datetime             g_cooldownUntilTime    = 0;
double               g_todayClosedProfit    = 0.0;
bool                 g_dailyLossLimitHit    = false;

string         g_lastSignalType = "MENUNGGU SETUP";"""

assert old_globals in content, "Global variables match failed!"
content = content.replace(old_globals, new_globals, 1)

# 6. CalculateConfluenceScore additions
old_score_init = """   r.candlePts = 0.0;
   r.chartPatternPts = 0.0;"""

new_score_init = """   r.candlePts = 0.0;
   r.chartPatternPts = 0.0;
   r.vsaPts = 0.0;
   r.vsaStatus = "NORMAL";"""

assert old_score_init in content, "Score init match failed!"
content = content.replace(old_score_init, new_score_init, 1)

old_score_calc = """   r.totalScore = r.structurePts + r.displacementPts + r.obMitigationPts + r.fvgPts + r.sweepPts + r.fiboGPPts + r.emaRibbonPts + r.candlePts + r.chartPatternPts;"""

new_score_calc = """   // 10. Volume Spread Analysis (VSA Footprint Absorption & No-Supply Test)
   if (InpUseVSA)
   {
      long sumVol = 0;
      int countVol = 0;
      int vLookback = MathMin(InpVSALookbackBars, ArraySize(rates) - 2);
      for (int v = 2; v < 2 + vLookback; v++)
      {
         sumVol += rates[v].tick_volume;
         countVol++;
      }
      double avgVol = (countVol > 0) ? ((double)sumVol / (double)countVol) : (double)rates[1].tick_volume;
      double volRatio = (avgVol > 0) ? ((double)rates[1].tick_volume / avgVol) : 1.0;

      if (isBuy)
      {
         bool atKeyZone = (ob.isValid && ob.isBullish && low1 <= ob.top && high1 >= ob.bottom) ||
                          (fibo.isValid && low1 <= fibo.level500 && high1 >= fibo.level786) ||
                          (low1 <= MathMax(ema8, ema21) && high1 >= MathMin(ema8, ema21));

         if (atKeyZone && volRatio >= InpVSAClimaxRatio)
         {
            r.vsaPts = 10.0;
            r.vsaStatus = "CLIMAX ABSORPTION (" + DoubleToString(volRatio, 1) + "x)";
         }
         else if (volRatio <= InpVSANoSupplyRatio)
         {
            r.vsaPts = 5.0;
            r.vsaStatus = "NO-SUPPLY PULLBACK (" + DoubleToString(volRatio, 1) + "x)";
         }
      }
      else // SELL
      {
         bool atKeyZone = (ob.isValid && !ob.isBullish && high1 >= ob.bottom && low1 <= ob.top) ||
                          (fibo.isValid && high1 >= fibo.level500 && low1 <= fibo.level786) ||
                          (high1 >= MathMin(ema8, ema21) && low1 <= MathMax(ema8, ema21));

         if (atKeyZone && volRatio >= InpVSAClimaxRatio)
         {
            r.vsaPts = 10.0;
            r.vsaStatus = "CLIMAX ABSORPTION (" + DoubleToString(volRatio, 1) + "x)";
         }
         else if (volRatio <= InpVSANoSupplyRatio)
         {
            r.vsaPts = 5.0;
            r.vsaStatus = "NO-SUPPLY PULLBACK (" + DoubleToString(volRatio, 1) + "x)";
         }
      }
   }

   r.totalScore = r.structurePts + r.displacementPts + r.obMitigationPts + r.fvgPts + r.sweepPts + r.fiboGPPts + r.emaRibbonPts + r.candlePts + r.chartPatternPts + r.vsaPts;"""

assert old_score_calc in content, "Score calc match failed!"
content = content.replace(old_score_calc, new_score_calc, 1)

# 7. CheckCircuitBreakers function before OnTick
circuit_func = """//+------------------------------------------------------------------+
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|
//+------------------------------------------------------------------+
bool CheckCircuitBreakers()
{
   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit)
      return true;

   MqlDateTime dt;
   TimeCurrent(dt);
   dt.hour = 0;
   dt.min  = 0;
   dt.sec  = 0;
   datetime todayStart = StructToTime(dt);

   if (!HistorySelect(todayStart, TimeCurrent()))
      return true;

   int consecutiveLosses = 0;
   datetime lastLossTime = 0;
   double todayClosedPnL = 0.0;
   int totalDeals = HistoryDealsTotal();

   for (int i = 0; i < totalDeals; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if (ticket == 0) continue;

      long entryType = HistoryDealGetInteger(ticket, DEAL_ENTRY);
      if (entryType != DEAL_ENTRY_OUT && entryType != DEAL_ENTRY_INOUT) continue;

      long dealMagic = HistoryDealGetInteger(ticket, DEAL_MAGIC);
      if (dealMagic != InpMagicNumber) continue;

      double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) +
                      HistoryDealGetDouble(ticket, DEAL_SWAP) +
                      HistoryDealGetDouble(ticket, DEAL_COMMISSION);

      todayClosedPnL += profit;

      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
      {
         consecutiveLosses++;
         lastLossTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER KERUGIAN! TIDAK PERNAH MEMICU COOLDOWN!
      }
   }

   g_consecutiveLossCount = consecutiveLosses;
   g_lastLossTime         = lastLossTime;
   g_todayClosedProfit    = todayClosedPnL;

   // 1. Consecutive Loss Cooldown (Jeda 4 Jam Anti-Overtrading Pasca 2x True Loss)
   if (InpUseConsecutiveLossGuard && consecutiveLosses >= InpMaxConsecutiveLosses)
   {
      datetime cooldownEnd = lastLossTime + (InpCooldownHours * 3600);
      if (TimeCurrent() < cooldownEnd)
      {
         g_cooldownUntilTime = cooldownEnd;
         int remainingMins = (int)((cooldownEnd - TimeCurrent()) / 60);
         g_lastSignalType = "CIRCUIT BREAKER: 2x LOSS COOLDOWN (Sisa " + IntegerToString(remainingMins) + " Mnt)";
         return false; // Blok entry baru selama cooldown!
      }
      else
      {
         g_cooldownUntilTime = 0;
      }
   }
   else
   {
      g_cooldownUntilTime = 0;
   }

   // 2. Daily Loss Limit Safeguard (Kunci Hari Jika Akumulasi Rugi > 2.5% Modal)
   if (InpUseDailyLossLimit)
   {
      double currentBal = AccountInfoDouble(ACCOUNT_BALANCE);
      double maxAllowedLoss = -(currentBal * (InpMaxDailyLossPercent / 100.0));
      if (todayClosedPnL <= maxAllowedLoss)
      {
         g_dailyLossLimitHit = true;
         g_lastSignalType = "DAILY LOSS LIMIT (-" + DoubleToString(InpMaxDailyLossPercent, 1) + "%): TRADING DIKUNCI HARI INI";
         return false; // Blok entry baru hingga hari berganti!
      }
      else
      {
         g_dailyLossLimitHit = false;
      }
   }

   return true;
}

"""

old_ontick_start = """//+------------------------------------------------------------------+
//| ON TICK (EKSEKUSI UTAMA PERGERAKAN HARGA)                        |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Kelola Posisi Aktif (Trailing EMA 21 & Auto-Breakeven Kunci Modal)
   ManageActiveTrades();"""

new_ontick_start = circuit_func + """//+------------------------------------------------------------------+
//| ON TICK (EKSEKUSI UTAMA PERGERAKAN HARGA)                        |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Kelola Posisi Aktif (Trailing EMA 21, Structural Runner & Auto-BE Kunci Modal)
   ManageActiveTrades();"""

assert old_ontick_start in content, "OnTick start match failed!"
content = content.replace(old_ontick_start, new_ontick_start, 1)

old_newbar = """   // 3. Hanya Cari Sinyal Saat Lilin Baru Selesai (Non-Repaint Bar Close Rule)
   if (!IsNewBar())
      return;"""

new_newbar = """   // 3. Hanya Cari Sinyal Saat Lilin Baru Selesai (Non-Repaint Bar Close Rule)
   if (!IsNewBar())
      return;

   // 3.1 Periksa Proteksi Akun & Circuit Breaker (Consecutive Loss Cooldown & Daily Limit)
   if (!CheckCircuitBreakers())
      return;"""

assert old_newbar in content, "New bar match failed!"
content = content.replace(old_newbar, new_newbar, 1)

# 8. ManageActiveTrades Structural Trailing Stop
old_manage_start = """   double ema21Val[];
   ArraySetAsSeries(ema21Val, true);
   bool ema21Ok = false;
   if (InpUseTrailingEMA21)
   {
      if (CopyBuffer(h_ema21, 0, 0, 2, ema21Val) >= 2)
         ema21Ok = true;
   }"""

new_manage_start = """   double ema21Val[];
   ArraySetAsSeries(ema21Val, true);
   bool ema21Ok = false;
   if (InpUseTrailingEMA21)
   {
      if (CopyBuffer(h_ema21, 0, 0, 2, ema21Val) >= 2)
         ema21Ok = true;
   }

   double atrVal[];
   ArraySetAsSeries(atrVal, true);
   double currentAtr = PipToPrice(20.0);
   if (CopyBuffer(h_atr14, 0, 0, 2, atrVal) >= 2 && atrVal[1] > 0)
      currentAtr = atrVal[1];"""

assert old_manage_start in content, "ManageActiveTrades start match failed!"
content = content.replace(old_manage_start, new_manage_start, 1)

old_manage_loop_end = """      // 2. Logika Trailing Stop Mengikuti Ribbon EMA 21 Magenta
      if (InpUseTrailingEMA21 && ema21Ok)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            double trailSL = NormalizeDouble(ema21Val[1] - PipToPrice(InpTrailingBufferPips), _Digits);
            if (trailSL > open && (trailSL - sl) >= (10 * _Point) && (current - trailSL) >= minStopDist)
            {
               if (trade.PositionModify(ticket, trailSL, tp))
               {
                  Print("[TRAILING EMA 21] Posisi BUY #", ticket, " SL digeser ke: ", trailSL);
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            double trailSL = NormalizeDouble(ema21Val[1] + PipToPrice(InpTrailingBufferPips), _Digits);
            if (trailSL < open && (sl == 0 || (sl - trailSL) >= (10 * _Point)) && (trailSL - current) >= minStopDist)
            {
               if (trade.PositionModify(ticket, trailSL, tp))
               {
                  Print("[TRAILING EMA 21] Posisi SELL #", ticket, " SL digeser ke: ", trailSL);
               }
            }
         }
      }
   }
}"""

new_manage_loop_end = """      // 2. Logika Trailing Stop Mengikuti Ribbon EMA 21 Magenta
      if (InpUseTrailingEMA21 && ema21Ok)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            double trailSL = NormalizeDouble(ema21Val[1] - PipToPrice(InpTrailingBufferPips), _Digits);
            if (trailSL > open && (trailSL - sl) >= (10 * _Point) && (current - trailSL) >= minStopDist)
            {
               if (trade.PositionModify(ticket, trailSL, tp))
               {
                  Print("[TRAILING EMA 21] Posisi BUY #", ticket, " SL digeser ke: ", trailSL);
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            double trailSL = NormalizeDouble(ema21Val[1] + PipToPrice(InpTrailingBufferPips), _Digits);
            if (trailSL < open && (sl == 0 || (sl - trailSL) >= (10 * _Point)) && (trailSL - current) >= minStopDist)
            {
               if (trade.PositionModify(ticket, trailSL, tp))
               {
                  Print("[TRAILING EMA 21] Posisi SELL #", ticket, " SL digeser ke: ", trailSL);
               }
            }
         }
      }

      // 3. Multi-Stage Structural Trailing Stop untuk RUNNER (Pasca-TP1 50% Ditutup)
      string gvRunnerKey = "VIKAR_PARTIAL_" + IntegerToString(ticket);
      bool isRunnerLot = GlobalVariableCheck(gvRunnerKey);

      if (InpUseStructuralTrailing && isRunnerLot)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            if (lastSwingLow.price > 0 && lastSwingLow.price > open)
            {
               double structSL = NormalizeDouble(lastSwingLow.price - (InpStructuralTrailingAtrBuffer * currentAtr), _Digits);
               if (structSL > sl && (structSL - sl) >= (10 * _Point) && (current - structSL) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, structSL, tp))
                  {
                     Print("[SMC STRUCTURAL RUNNER] Posisi BUY #", ticket, " SL dipindah di bawah Higher Low (HL) terbaru: ", structSL);
                  }
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            if (lastSwingHigh.price > 0 && lastSwingHigh.price < open)
            {
               double structSL = NormalizeDouble(lastSwingHigh.price + (InpStructuralTrailingAtrBuffer * currentAtr), _Digits);
               if ((sl == 0 || structSL < sl) && (sl - structSL) >= (10 * _Point) && (structSL - current) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, structSL, tp))
                  {
                     Print("[SMC STRUCTURAL RUNNER] Posisi SELL #", ticket, " SL dipindah di atas Lower High (LH) terbaru: ", structSL);
                  }
               }
            }
         }
      }
   }
}"""

assert old_manage_loop_end in content, "ManageActiveTrades loop end match failed!"
content = content.replace(old_manage_loop_end, new_manage_loop_end, 1)

# 9. Update Dashboard HUD (Add VSA Footprint & Circuit Guard lines, expand height)
old_dash_h = "int panelH = InpShowPnLStats ? 465 : 385;"
new_dash_h = "int panelH = InpShowPnLStats ? 515 : 435;"
assert old_dash_h in content, "Dashboard height match failed!"
content = content.replace(old_dash_h, new_dash_h, 1)

old_dash_pivots = """   CreateOrUpdateText("VIKAR_HUD_PILAR4", panelX + 12, currY + 70, "[Triple EMA]  : " + emaTrendStr + " | Ribbon 8/21", C'232,121,249', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_PILAR5", panelX + 12, currY + 84, "[S/R Pivot]   : P: " + DoubleToString(currentPivot.P, 2) + " [R1: " + DoubleToString(currentPivot.R1, 2) + " | S1: " + DoubleToString(currentPivot.S1, 2) + "]", C'148,163,184', 7, "Segoe UI");
   currY += 102;"""

new_dash_pivots = """   CreateOrUpdateText("VIKAR_HUD_PILAR4", panelX + 12, currY + 70, "[Triple EMA]  : " + emaTrendStr + " | Ribbon 8/21", C'232,121,249', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_PILAR5", panelX + 12, currY + 84, "[S/R Pivot]   : P: " + DoubleToString(currentPivot.P, 2) + " [R1: " + DoubleToString(currentPivot.R1, 2) + " | S1: " + DoubleToString(currentPivot.S1, 2) + "]", C'148,163,184', 7, "Segoe UI");

   // Baris VSA Footprint
   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Volume") : "VSA: OFF";
   color vsaClr = (StringFind(vsaDisplay, "CLIMAX") >= 0) ? C'74,222,128' : ((StringFind(vsaDisplay, "NO-SUPPLY") >= 0) ? C'56,189,248' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_VSA", panelX + 12, currY + 98, "[VSA Footprint]: " + vsaDisplay, vsaClr, 7, "Segoe UI Bold");

   // Baris Circuit Guard & Consecutive Loss Counter
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
      cbDisplay = IntegerToString(g_consecutiveLossCount) + "/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss Berturut-turut";
      cbClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_CB", panelX + 12, currY + 112, "[Circuit Guard]: " + cbDisplay, cbClr, 7, "Segoe UI Bold");
   currY += 130;"""

assert old_dash_pivots in content, "Dashboard pivots match failed!"
content = content.replace(old_dash_pivots, new_dash_pivots, 1)

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5', 'w', encoding='utf-8') as f:
    f.write(content)

print("v2.2 Apex Institutional modifications successfully applied to VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5!")
