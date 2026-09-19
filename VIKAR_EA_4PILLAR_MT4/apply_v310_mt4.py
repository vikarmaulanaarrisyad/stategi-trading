import sys

filepath = 'VIKAR_EA_4PILLAR_MT4/VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4'
with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"Read {len(content)} characters.")

# 1. Version & Description
old_header = '#property version   "3.00"\n#property strict\n#property description "Robot Trading MT4 Institusional 4 Pilar Terpadu (v3.0 Apex Grandmaster Edition)"'
new_header = '#property version   "3.10"\n#property strict\n#property description "Robot Trading MT4 Institusional 4 Pilar Terpadu (v3.10 Adaptive AI Learning Edition)"'
assert old_header in content, "Failed to find old_header"
content = content.replace(old_header, new_header, 1)

# 2. Inputs
old_inputs = '''extern int           InpAdaptiveBufferTrades    = 3;                // Jumlah Transaksi dengan Buffer Ekstra Pasca-SL
extern bool          InpAutopsyNotifyPush       = true;             // Kirim Laporan Otopsi Pasca-Loss ke Smartphone'''

new_inputs = '''extern int           InpAdaptiveBufferTrades    = 3;                // Jumlah Transaksi dengan Buffer Ekstra Pasca-SL
extern bool          InpAutopsyNotifyPush       = true;             // Kirim Laporan Otopsi Pasca-Loss ke Smartphone
extern bool          InpUseDirectionalLearning  = true;             // Proteksi Arah: Penalti Jika Arah Sama Gagal Baru Saja
extern double        InpDirectionalPenaltyScore = 15.0;             // Penalti Skor Jika Mencoba Arah Gagal Berulang
extern int           InpDirectionalPenaltyBars  = 12;               // Durasi Penalti Arah Gagal (Bars Lilin)
extern bool          InpUseHourlyLearning       = true;             // Pelajari & Hindari Jam Tertentu yang Rawan Loss Berulang'''
assert old_inputs in content, "Failed to find old_inputs"
content = content.replace(old_inputs, new_inputs, 1)

# 3. struct LossAutopsyReport
old_struct = '''struct LossAutopsyReport
{
   bool                 isActive;
   int                  failedTicket;
   datetime             timeLoss;
   ENUM_CANDLE_PATTERN  failedPattern;
   string               failedPatternName;
   string               lossReason;
   double               scorePenalty;
   datetime             quarantineUntilBar;
   int                  tradesWithExtraBuffer;
};'''

new_struct = '''struct LossAutopsyReport
{
   bool                 isActive;
   int                  failedTicket;
   datetime             timeLoss;
   ENUM_CANDLE_PATTERN  failedPattern;
   string               failedPatternName;
   string               lossReason;
   double               scorePenalty;
   datetime             quarantineUntilBar;
   int                  tradesWithExtraBuffer;
   int                  failedDirection;        // Arah posisi gagal: +1 BUY, -1 SELL, 0 None
   datetime             directionPenaltyUntil;  // Waktu berakhirnya penalti arah gagal
   int                  toxicHour;              // Jam server rawan loss berulang (-1 jika aman)
};'''
assert old_struct in content, "Failed to find old_struct"
content = content.replace(old_struct, new_struct, 1)

# 4. #define TOTAL_TRACKED_PATTERNS 12
assert '#define TOTAL_TRACKED_PATTERNS 12' in content, "Failed to find TOTAL_TRACKED_PATTERNS 12"
content = content.replace('#define TOTAL_TRACKED_PATTERNS 12', '#define TOTAL_TRACKED_PATTERNS 13', 1)

# 5. PerformLossAutopsy + Snapshot & Persistent State Helpers
old_autopsy = '''//+------------------------------------------------------------------+
//| MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE v2.40)|
//+------------------------------------------------------------------+
void PerformLossAutopsy(int ticket, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil data pola candlestick dari memori Global Variable
   string patGvKey = "VIKAR_PAT_" + IntegerToString(ticket);
   ENUM_CANDLE_PATTERN pat = PATTERN_NONE;
   if (GlobalVariableCheck(patGvKey))
   {
      pat = (ENUM_CANDLE_PATTERN)(int)GlobalVariableGet(patGvKey);
      GlobalVariableDel(patGvKey);
   }
   g_autopsy.failedPattern = pat;

   string patName = "Pola Setup Standard";
   if (pat == PATTERN_HAMMER_PINBAR) patName = "Pin Bar / Hammer";
   else if (pat == PATTERN_ENGULFING) patName = "Engulfing";
   else if (pat == PATTERN_TWEEZER) patName = "Tweezer Rejection";
   else if (pat == PATTERN_MORNING_EVENING) patName = "Morning/Evening Star";
   else if (pat == PATTERN_FVG_MITIGATION) patName = "FVG Mitigation Rebound";
   else if (pat == PATTERN_THREE_SOLDIERS_CROWS) patName = "Three Soldiers/Crows";
   else if (pat == PATTERN_HARAMI_INSIDE_BAR) patName = "Harami Inside Bar";
   else if (pat == PATTERN_PIERCING_DARKCLOUD) patName = "Piercing/Dark Cloud";
   else if (pat == PATTERN_DOJI_REJECTION) patName = "Doji Rejection";
   else if (pat == PATTERN_INVERTED_HAMMER_STAR) patName = "Inverted Hammer/Star";
   g_autopsy.failedPatternName = patName;

   if (pat != PATTERN_NONE)
      g_autopsy.quarantineUntilBar = Time[0] + (InpQuarantinePatternBars * Period() * 60);
   else
      g_autopsy.quarantineUntilBar = 0;

   // 2. Diagnosa Anatomi Penyebab Loss
   double currentAtr = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   double lastBarRange = High[1] - Low[1];
   double currentEma125 = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);

   string reason = "PENGUJIAN LEVEL GAGAL (LOW CONFLUENCE)";
   if (lastBarRange >= (2.2 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPIKE)";
   else if (g_smcAnalysis.hasCHoCH || (Close[1] < currentEma125 && Open[1] > currentEma125) || (Close[1] > currentEma125 && Open[1] < currentEma125))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU WICK)";

   g_autopsy.lossReason = reason;

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT4] Posisi #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
   Print("DIAGNOSA PENYEBAB : ", g_autopsy.lossReason);
   Print("KOREKSI 1 (SKOR)  : Ambang Konfluensi dinaikkan +", DoubleToString(g_autopsy.scorePenalty, 0), " Poin (Hanya Setup Grade A+)");
   if (pat != PATTERN_NONE)
      Print("KOREKSI 2 (POLA)  : Pola ", patName, " dikarantina selama ", InpQuarantinePatternBars, " Bar lilin.");
   Print("KOREKSI 3 (BUFFER): Stop Loss diperlebar +", DoubleToString(InpAdaptiveSLBufferBoost, 2), "x ATR untuk ", InpAdaptiveBufferTrades, " trade berikutnya.");
   Print("==================================================================");

   if (InpAutopsyNotifyPush)
   {
      string notif = "OTOPSI PASCA-SL #" + IntegerToString(ticket) + " (" + DoubleToString(lossAmount, 2) + ")\\n" +
                     "Diagnosa: " + reason + "\\n" +
                     "Koreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      SendPushAlert(notif);
   }
}'''

new_autopsy = '''//+------------------------------------------------------------------+
//| HELPER & FUNGSI PERSISTENSI AUTOPSY MT4 (v3.10 AI LEARNING)     |
//+------------------------------------------------------------------+
void SaveTradeEntrySnapshotMT4(int ticket, int direction, int patternId, double currentScore, double currentAtr)
{
   GlobalVariableSet("VIKAR_PAT_"  + IntegerToString(ticket), (double)patternId);
   GlobalVariableSet("VIKAR_DIR_"  + IntegerToString(ticket), (double)direction);
   GlobalVariableSet("VIKAR_HOUR_" + IntegerToString(ticket), (double)Hour());
   GlobalVariableSet("VIKAR_ATR_"  + IntegerToString(ticket), currentAtr);
   GlobalVariableSet("VIKAR_SCO_"  + IntegerToString(ticket), currentScore);
}

void SaveAutopsyStateMT4()
{
   string pfx = "VIKAR_MT4_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
   GlobalVariableSet(pfx + "ACTIVE", g_autopsy.isActive ? 1.0 : 0.0);
   GlobalVariableSet(pfx + "TICKET", (double)g_autopsy.failedTicket);
   GlobalVariableSet(pfx + "PAT", (double)g_autopsy.failedPattern);
   GlobalVariableSet(pfx + "PENALTY", g_autopsy.scorePenalty);
   GlobalVariableSet(pfx + "QUARANTINE", (double)g_autopsy.quarantineUntilBar);
   GlobalVariableSet(pfx + "BUFFER", (double)g_autopsy.tradesWithExtraBuffer);
   GlobalVariableSet(pfx + "DIR", (double)g_autopsy.failedDirection);
   GlobalVariableSet(pfx + "DIRUNTIL", (double)g_autopsy.directionPenaltyUntil);
   GlobalVariableSet(pfx + "TOXICHOUR", (double)g_autopsy.toxicHour);
}

void LoadAutopsyStateMT4()
{
   string pfx = "VIKAR_MT4_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
   if (GlobalVariableCheck(pfx + "ACTIVE") && GlobalVariableGet(pfx + "ACTIVE") > 0.5)
   {
      g_autopsy.isActive              = true;
      g_autopsy.failedTicket          = (int)GlobalVariableGet(pfx + "TICKET");
      g_autopsy.failedPattern         = (ENUM_CANDLE_PATTERN)(int)GlobalVariableGet(pfx + "PAT");
      g_autopsy.scorePenalty          = GlobalVariableGet(pfx + "PENALTY");
      g_autopsy.quarantineUntilBar    = (datetime)GlobalVariableGet(pfx + "QUARANTINE");
      g_autopsy.tradesWithExtraBuffer = (int)GlobalVariableGet(pfx + "BUFFER");
      g_autopsy.failedDirection       = (int)GlobalVariableGet(pfx + "DIR");
      g_autopsy.directionPenaltyUntil = (datetime)GlobalVariableGet(pfx + "DIRUNTIL");
      g_autopsy.toxicHour             = (int)GlobalVariableGet(pfx + "TOXICHOUR");
      g_autopsy.lossReason            = "PEMULIHAN STATUS PASCA-RESTART (PERSISTENT)";
      Print("[SELF-HEALING RESTORED MT4] Status otopsi berhasil dipulihkan dari memori persisten.");
   }
   else
   {
      g_autopsy.isActive              = false;
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
      g_autopsy.toxicHour             = -1;
   }
}

//+------------------------------------------------------------------+
//| MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE v3.10)|
//+------------------------------------------------------------------+
void PerformLossAutopsy(int ticket, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil data pola candlestick dari memori Global Variable (TIDAK DIHAPUS DISINI AGAR BISA DIBACA MATRIX)
   string patGvKey = "VIKAR_PAT_" + IntegerToString(ticket);
   ENUM_CANDLE_PATTERN pat = PATTERN_NONE;
   int rawPatId = 0;
   if (GlobalVariableCheck(patGvKey))
   {
      rawPatId = (int)GlobalVariableGet(patGvKey);
      pat = (ENUM_CANDLE_PATTERN)rawPatId;
   }
   g_autopsy.failedPattern = pat;

   string patName = "Pola Setup Standard";
   if (rawPatId == 12) patName = "Liquidity Sweep Trap Hunter";
   else if (rawPatId == 11) patName = "Momentum BOS Breakout";
   else if (pat == PATTERN_HAMMER_PINBAR) patName = "Pin Bar / Hammer";
   else if (pat == PATTERN_ENGULFING) patName = "Engulfing";
   else if (pat == PATTERN_TWEEZER) patName = "Tweezer Rejection";
   else if (pat == PATTERN_MORNING_EVENING) patName = "Morning/Evening Star";
   else if (pat == PATTERN_FVG_MITIGATION) patName = "FVG Mitigation Rebound";
   else if (pat == PATTERN_THREE_SOLDIERS_CROWS) patName = "Three Soldiers/Crows";
   else if (pat == PATTERN_HARAMI_INSIDE_BAR) patName = "Harami Inside Bar";
   else if (pat == PATTERN_PIERCING_DARKCLOUD) patName = "Piercing/Dark Cloud";
   else if (pat == PATTERN_DOJI_REJECTION) patName = "Doji Rejection";
   else if (pat == PATTERN_INVERTED_HAMMER_STAR) patName = "Inverted Hammer/Star";
   g_autopsy.failedPatternName = patName;

   datetime currentBarTime = Time[0];
   if (pat != PATTERN_NONE || rawPatId >= 11)
      g_autopsy.quarantineUntilBar = currentBarTime + (InpQuarantinePatternBars * Period() * 60);
   else
      g_autopsy.quarantineUntilBar = 0;

   // Ambil Direction (BUY = +1, SELL = -1)
   int tradeDir = 0;
   string dirGvKey = "VIKAR_DIR_" + IntegerToString(ticket);
   if (GlobalVariableCheck(dirGvKey)) tradeDir = (int)GlobalVariableGet(dirGvKey);

   if (InpUseDirectionalLearning && tradeDir != 0)
   {
      g_autopsy.failedDirection       = tradeDir;
      g_autopsy.directionPenaltyUntil = currentBarTime + (InpDirectionalPenaltyBars * Period() * 60);
   }
   else
   {
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
   }

   // Ambil Jam Transaksi (0..23) dan Lacak Jam Rawan Loss Berulang
   int tradeHour = -1;
   string hrGvKey = "VIKAR_HOUR_" + IntegerToString(ticket);
   if (GlobalVariableCheck(hrGvKey)) tradeHour = (int)GlobalVariableGet(hrGvKey);

   if (InpUseHourlyLearning && tradeHour >= 0 && tradeHour <= 23)
   {
      string hLossKey = "VIKAR_MT4_HLOSS_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(tradeHour);
      int currentHLoss = GlobalVariableCheck(hLossKey) ? (int)GlobalVariableGet(hLossKey) : 0;
      currentHLoss++;
      GlobalVariableSet(hLossKey, (double)currentHLoss);

      if (currentHLoss >= 2)
      {
         g_autopsy.toxicHour = tradeHour;
         Print("[HOURLY LEARNING MT4] Jam ", tradeHour, ":00 server terdeteksi rawan loss berulang (", currentHLoss, "x loss). Proteksi jam aktif!");
      }
      else
         g_autopsy.toxicHour = -1;
   }
   else
      g_autopsy.toxicHour = -1;

   // 2. Diagnosa Anatomi Mendalam Penyebab Loss (7 Skenario Institusional)
   double currentAtr = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   double lastBarRange = High[1] - Low[1];
   double currentEma125 = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);

   double htfEma125 = iMA(Symbol(), InpHTFTimeframe, InpHTFTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double htfClose  = iClose(Symbol(), InpHTFTimeframe, 1);
   bool isHtfBull   = (htfClose > htfEma125);
   bool isHtfBear   = (htfClose < htfEma125);

   string reason = "PENGUJIAN LEVEL GAGAL (SUPPORT/RESISTEN DITEMBUS)";
   if (lastBarRange >= (2.0 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPREAD SPIKE)";
   else if (g_currentChoppiness > 61.8)
      reason = "JEBAKAN SIDEWAYS NOISE (PASAR CHOPPY KOMPRESI)";
   else if (g_smcAnalysis.hasCHoCH || (Close[1] < currentEma125 && Open[1] > currentEma125) || (Close[1] > currentEma125 && Open[1] < currentEma125))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU EKOR)";
   else if (tradeDir == 1 && isHtfBear)
      reason = "DIRECTIONAL ERROR (BUY MELAWAN TREN MAKRO HTF)";
   else if (tradeDir == -1 && isHtfBull)
      reason = "DIRECTIONAL ERROR (SELL MELAWAN TREN MAKRO HTF)";
   else if (g_autopsy.toxicHour >= 0)
      reason = "JAM RAWAN VOLATILITAS (TOXIC HOUR REVERSAL)";

   g_autopsy.lossReason = reason;
   SaveAutopsyStateMT4();

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT4] Posisi #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
   Print("DIAGNOSA PENYEBAB : ", g_autopsy.lossReason);
   Print("KOREKSI 1 (SKOR)  : Ambang Konfluensi dinaikkan +", DoubleToString(g_autopsy.scorePenalty, 0), " Poin (Hanya Setup Grade A+)");
   if (pat != PATTERN_NONE || rawPatId >= 11)
      Print("KOREKSI 2 (POLA)  : Pola ", patName, " dikarantina selama ", InpQuarantinePatternBars, " Bar lilin.");
   if (tradeDir != 0 && InpUseDirectionalLearning)
      Print("KOREKSI 3 (ARAH)  : Penalti arah ", (tradeDir == 1 ? "BUY" : "SELL"), " +", DoubleToString(InpDirectionalPenaltyScore, 0), " Poin selama ", InpDirectionalPenaltyBars, " Bar lilin.");
   Print("KOREKSI 4 (BUFFER): Stop Loss diperlebar +", DoubleToString(InpAdaptiveSLBufferBoost, 2), "x ATR untuk ", InpAdaptiveBufferTrades, " trade berikutnya.");
   Print("==================================================================");

   if (InpAutopsyNotifyPush)
   {
      string notif = "OTOPSI PASCA-SL MT4 #" + IntegerToString(ticket) + " (" + DoubleToString(lossAmount, 2) + ")\\n" +
                     "Diagnosa: " + reason + "\\n" +
                     "Koreksi: Ambang Skor +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE || rawPatId >= 11)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      if (tradeDir != 0 && InpUseDirectionalLearning)
         notif += " Penalti arah " + (tradeDir == 1 ? "BUY" : "SELL") + " aktif.";
      SendPushAlert(notif);
   }
}'''
assert old_autopsy in content, "Failed to find old_autopsy"
content = content.replace(old_autopsy, new_autopsy, 1)

# 6. InitPatternMatrix patNames
old_patnames = '''   string patNames[TOTAL_TRACKED_PATTERNS] = {
      "Setup Standar / PA",
      "Pin Bar / Hammer",
      "Engulfing Absorption",
      "Tweezer Rejection",
      "Morning / Evening Star",
      "FVG Rebound",
      "Three Soldiers / Crows",
      "Harami Inside Bar",
      "Piercing / Dark Cloud",
      "Dragonfly / Gravestone",
      "Inverted Hammer / Star",
      "Momentum BOS Breakout"
   };'''

new_patnames = '''   string patNames[TOTAL_TRACKED_PATTERNS] = {
      "Setup Standar / PA",
      "Pin Bar / Hammer",
      "Engulfing Absorption",
      "Tweezer Rejection",
      "Morning / Evening Star",
      "FVG Rebound",
      "Three Soldiers / Crows",
      "Harami Inside Bar",
      "Piercing / Dark Cloud",
      "Dragonfly / Gravestone",
      "Inverted Hammer / Star",
      "Momentum BOS Breakout",
      "Liquidity Sweep Trap Hunter"
   };'''
assert old_patnames in content, "Failed to find old_patnames"
content = content.replace(old_patnames, new_patnames, 1)

# 7. ResetSelfHealingState
old_reset = '''void ResetSelfHealingState(string triggerReason)
{
   if (!g_autopsy.isActive) return;
   g_autopsy.isActive              = false;
   g_autopsy.scorePenalty          = 0.0;
   g_autopsy.tradesWithExtraBuffer = 0;
   g_autopsy.quarantineUntilBar    = 0;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   Print("[SELF-HEALING NORMALIZED MT4] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}'''

new_reset = '''void ResetSelfHealingState(string triggerReason)
{
   if (!g_autopsy.isActive) return;
   g_autopsy.isActive              = false;
   g_autopsy.scorePenalty          = 0.0;
   g_autopsy.tradesWithExtraBuffer = 0;
   g_autopsy.quarantineUntilBar    = 0;
   g_autopsy.failedDirection       = 0;
   g_autopsy.directionPenaltyUntil = 0;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   SaveAutopsyStateMT4();
   Print("[SELF-HEALING NORMALIZED MT4] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}'''
assert old_reset in content, "Failed to find old_reset"
content = content.replace(old_reset, new_reset, 1)

# 8. CheckCircuitBreakers PMR Loop
old_cb_loop = '''      // Pembaruan Statistik Pattern Performance Matrix (v2.50)
      string procKey = "VIKAR_PMR_PROC_" + IntegerToString(todayTrades[k].ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patGvKey = "VIKAR_PAT_" + IntegerToString(todayTrades[k].ticket);
         int patId = GlobalVariableCheck(patGvKey) ? (int)GlobalVariableGet(patGvKey) : 0;
         if (profit > 0.01)
            UpdatePatternRecord(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecord(patId, false);
         GlobalVariableSet(procKey, 1.0);
      }'''

new_cb_loop = '''      // Pembaruan Statistik Pattern Performance Matrix MT4 (v3.10)
      string procKey = "VIKAR_PMR_PROC_" + IntegerToString(todayTrades[k].ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patGvKey = "VIKAR_PAT_" + IntegerToString(todayTrades[k].ticket);
         int patId = GlobalVariableCheck(patGvKey) ? (int)GlobalVariableGet(patGvKey) : 0;
         if (profit > 0.01)
            UpdatePatternRecord(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecord(patId, false);
         GlobalVariableSet(procKey, 1.0);

         // Bersihkan snapshot tiket setelah statistik diperbarui
         if (GlobalVariableCheck(patGvKey)) GlobalVariableDel(patGvKey);
         GlobalVariableDel("VIKAR_DIR_" + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_ATR_" + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_SCO_" + IntegerToString(todayTrades[k].ticket));
      }'''
assert old_cb_loop in content, "Failed to find old_cb_loop"
content = content.replace(old_cb_loop, new_cb_loop, 1)

# 9. OnInit: LoadAutopsyStateMT4()
old_oninit = '''   InitPatternMatrix();

   lastBarTime = Time[0]; // Safeguard: tunggu lilin penuh pertama pasca pasang EA'''
new_oninit = '''   InitPatternMatrix();
   LoadAutopsyStateMT4();

   lastBarTime = Time[0]; // Safeguard: tunggu lilin penuh pertama pasca pasang EA'''
assert old_oninit in content, "Failed to find old_oninit"
content = content.replace(old_oninit, new_oninit, 1)

# 10. BUY Evaluation: Directional & Hourly Penalty + activePatIdBUY (12 for Sweep Trap) + SaveTradeEntrySnapshotMT4
old_buy_eval = '''         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreBUY += 10.0; // Filter ekstra saat pasar sideways sempit'''

new_buy_eval = '''         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreBUY += 10.0; // Filter ekstra saat pasar sideways sempit

         // Adaptive Directional Penalty: Cegah balas dendam BUY jika baru saja loss BUY
         if (InpUseDirectionalLearning && g_autopsy.failedDirection == 1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
            effectiveMinScoreBUY += InpDirectionalPenaltyScore;

         // Hourly Toxic Learning: Hindari jam rawan loss berulang
         if (InpUseHourlyLearning && g_autopsy.toxicHour == Hour())
            effectiveMinScoreBUY += 10.0;'''
assert old_buy_eval in content, "Failed to find old_buy_eval"
content = content.replace(old_buy_eval, new_buy_eval, 1)

old_buy_pat = 'int activePatIdBUY = isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern;'
new_buy_pat = 'int activePatIdBUY = isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);'
assert old_buy_pat in content, "Failed to find old_buy_pat"
content = content.replace(old_buy_pat, new_buy_pat, 1)

old_buy_order = '''            int ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrBlue);

            if (ticket > 0)
            {
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)(isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));'''

new_buy_order = '''            int ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrBlue);

            if (ticket > 0)
            {
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMT4(ticket, 1, activePatIdBUY, scoreRes.totalScore, currentAtr);'''
assert old_buy_order in content, "Failed to find old_buy_order"
content = content.replace(old_buy_order, new_buy_order, 1)

# 11. SELL Evaluation: Directional & Hourly Penalty + activePatIdSELL (12 for Sweep Trap) + SaveTradeEntrySnapshotMT4
old_sell_eval = '''         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreSELL += 10.0; // Filter ekstra saat pasar sideways sempit'''

new_sell_eval = '''         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreSELL += 10.0; // Filter ekstra saat pasar sideways sempit

         // Adaptive Directional Penalty: Cegah balas dendam SELL jika baru saja loss SELL
         if (InpUseDirectionalLearning && g_autopsy.failedDirection == -1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
            effectiveMinScoreSELL += InpDirectionalPenaltyScore;

         // Hourly Toxic Learning: Hindari jam rawan loss berulang
         if (InpUseHourlyLearning && g_autopsy.toxicHour == Hour())
            effectiveMinScoreSELL += 10.0;'''
assert old_sell_eval in content, "Failed to find old_sell_eval"
content = content.replace(old_sell_eval, new_sell_eval, 1)

old_sell_pat = 'int activePatIdSELL = isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern;'
new_sell_pat = 'int activePatIdSELL = isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);'
assert old_sell_pat in content, "Failed to find old_sell_pat"
content = content.replace(old_sell_pat, new_sell_pat, 1)

old_sell_order = '''            int ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrRed);

            if (ticket > 0)
            {
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)(isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));'''

new_sell_order = '''            int ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrRed);

            if (ticket > 0)
            {
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMT4(ticket, -1, activePatIdSELL, scoreRes.totalScore, currentAtr);'''
assert old_sell_order in content, "Failed to find old_sell_order"
content = content.replace(old_sell_order, new_sell_order, 1)

# 12. UpdateDashboard HUD
old_hud = '''   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Skor | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");'''

new_hud = '''   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      string extraGuard = "";
      if (InpUseDirectionalLearning && g_autopsy.failedDirection != 0 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
         extraGuard += (g_autopsy.failedDirection == 1 ? " | Blok BUY" : " | Blok SELL");
      if (InpUseHourlyLearning && g_autopsy.toxicHour >= 0)
         extraGuard += (" | Toxic H:" + IntegerToString(g_autopsy.toxicHour));
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Skor" + extraGuard + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[AI Brain / Heal]: " + healDisplay, healClr, 7, "Segoe UI Bold");'''
assert old_hud in content, "Failed to find old_hud"
content = content.replace(old_hud, new_hud, 1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully updated {filepath}! New length: {len(content)} characters.")
