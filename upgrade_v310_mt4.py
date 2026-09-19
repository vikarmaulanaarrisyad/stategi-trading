import re
import shutil

def upgrade_mt4():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
    bak_path = path + ".v300.bak"
    shutil.copyfile(path, bak_path)

    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Update version property
    c = c.replace('#property version   "3.00"', '#property version   "3.10"')
    c = c.replace('Robot Trading MT4 Institusional 4 Pilar Terpadu (v3.0 Apex Grandmaster Edition)', 'Robot Trading MT4 Institusional 4 Pilar Terpadu (v3.10 Adaptive AI Learning Edition)')

    # 2. Add input parameters for directional & hourly learning
    old_inputs = 'extern double        InpPatternPenaltyScore     = 15.0;             // Penalti Pengetatan Skor untuk Pola Lemah'
    new_inputs = '''extern double        InpPatternPenaltyScore     = 15.0;             // Penalti Pengetatan Skor untuk Pola Lemah
extern bool          InpUseDirectionalLearning  = true;             // Proteksi Anti-Loss Berulang Searah (Directional Bias Learning)
extern double        InpDirectionalPenaltyScore = 10.0;             // Penalti Skor Tambahan untuk Arah yang Baru Saja Gagal
extern int           InpDirectionalPenaltyBars  = 12;               // Durasi Penalti Arah Gagal (Bars Lilin)
extern bool          InpUseHourlyLearning       = true;             // Hindari Jam Rawan Loss Berulang Hari Ini (Hourly Learning)'''
    c = c.replace(old_inputs, new_inputs)

    # 3. Update LossAutopsyReport struct & TOTAL_TRACKED_PATTERNS
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
};
LossAutopsyReport g_autopsy;

struct PatternRecord
{
   int    patternId;
   string name;
   int    wins;
   int    losses;
   int    total;
   double winRate;
   bool   isBlacklisted;
   double scoreModifier;
};

#define TOTAL_TRACKED_PATTERNS 12
PatternRecord g_patternMatrix[TOTAL_TRACKED_PATTERNS];'''

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
   int                  failedDirection;        // +1 for BUY, -1 for SELL
   datetime             directionPenaltyUntil;  // Waktu berakhir penalti arah
   int                  toxicHour;              // Jam rawan loss (-1 jika normal)
};
LossAutopsyReport g_autopsy;

struct PatternRecord
{
   int    patternId;
   string name;
   int    wins;
   int    losses;
   int    total;
   double winRate;
   bool   isBlacklisted;
   double scoreModifier;
};

#define TOTAL_TRACKED_PATTERNS 13
PatternRecord g_patternMatrix[TOTAL_TRACKED_PATTERNS];'''
    c = c.replace(old_struct, new_struct)

    # 4. Add Helper Functions before PerformLossAutopsy
    helper_code = '''//+------------------------------------------------------------------+
//| SIMPAN SNAPSHOT TRANSAKSI UNTUK EVALUASI ADAPTIF PASCA-TRADE MT4 |
//+------------------------------------------------------------------+
void SaveTradeEntrySnapshotMT4(int ticket, int patternId, int direction, double currentScore, double currentAtr)
{
   GlobalVariableSet("VIKAR_PAT_"  + IntegerToString(ticket), (double)patternId);
   GlobalVariableSet("VIKAR_DIR_"  + IntegerToString(ticket), (double)direction);
   GlobalVariableSet("VIKAR_HOUR_" + IntegerToString(ticket), (double)Hour());
   GlobalVariableSet("VIKAR_ATR_"  + IntegerToString(ticket), currentAtr);
   GlobalVariableSet("VIKAR_SCO_"  + IntegerToString(ticket), currentScore);
}

//+------------------------------------------------------------------+
//| PERSISTENSI STATUS OTOPSI & KOREKSI DIRI LINTAS RESTART MT4      |
//+------------------------------------------------------------------+
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
'''
    c = c.replace('void PerformLossAutopsy(int ticket', helper_code + '\nvoid PerformLossAutopsy(int ticket')

    # 5. Update PerformLossAutopsy in MT4
    old_autopsy = re.search(r'void PerformLossAutopsy\(int ticket, datetime closeTime, double lossAmount\)\s*\{.*?\n\}', c, re.DOTALL)
    if not old_autopsy:
        print("[ERROR] PerformLossAutopsy not found in MT4!")
        return False

    new_autopsy = r'''void PerformLossAutopsy(int ticket, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil snapshot data transaksi dari memori Global Variable
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
   string dirKey = "VIKAR_DIR_" + IntegerToString(ticket);
   if (GlobalVariableCheck(dirKey)) tradeDir = (int)GlobalVariableGet(dirKey);

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
   string hrKey = "VIKAR_HOUR_" + IntegerToString(ticket);
   if (GlobalVariableCheck(hrKey)) tradeHour = (int)GlobalVariableGet(hrKey);

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
   ENUM_HTF_BIAS currentHTFBias = AnalyzeHTFMacroTrend();

   string reason = "PENGUJIAN LEVEL GAGAL (SUPPORT/RESISTEN DITEMBUS)";
   if (lastBarRange >= (2.0 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPREAD SPIKE)";
   else if (g_currentChoppiness > 61.8)
      reason = "JEBAKAN SIDEWAYS NOISE (PASAR CHOPPY KOMPRESI)";
   else if (g_smcAnalysis.hasCHoCH || (Close[1] < currentEma125 && Open[1] > currentEma125) || (Close[1] > currentEma125 && Open[1] < currentEma125))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU EKOR)";
   else if (tradeDir == 1 && currentHTFBias == HTF_BIAS_BEARISH)
      reason = "DIRECTIONAL ERROR (BUY MELAWAN TREN MAKRO H1)";
   else if (tradeDir == -1 && currentHTFBias == HTF_BIAS_BULLISH)
      reason = "DIRECTIONAL ERROR (SELL MELAWAN TREN MAKRO H1)";
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
      string notif = "OTOPSI PASCA-SL #" + IntegerToString(ticket) + " (" + DoubleToString(lossAmount, 2) + ")\nDiagnosa: " + reason + "\nKoreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE || rawPatId >= 11)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      if (tradeDir != 0 && InpUseDirectionalLearning)
         notif += " Penalti arah " + (tradeDir == 1 ? "BUY" : "SELL") + " aktif.";
      SendPushAlert(notif);
   }
}'''
    c = c[:old_autopsy.start()] + new_autopsy + c[old_autopsy.end():]

    # 6. Update InitPatternMatrix in MT4
    old_names_mt4 = '''   string patNames[TOTAL_TRACKED_PATTERNS] = {
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

    new_names_mt4 = '''   string patNames[TOTAL_TRACKED_PATTERNS] = {
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
    c = c.replace(old_names_mt4, new_names_mt4)

    # 7. Update ResetSelfHealingState in MT4
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
   g_autopsy.toxicHour             = -1;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   SaveAutopsyStateMT4();
   Print("[SELF-HEALING NORMALIZED MT4] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}'''
    c = c.replace(old_reset, new_reset)

    # 8. Update CheckCircuitBreakers in MT4 for safe memory cleanup
    old_cb_mt4 = '''      // Pembaruan Statistik Pattern Performance Matrix (v2.50)
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

    new_cb_mt4 = '''      // Pembaruan Statistik Pattern Performance Matrix (v3.10)
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

         // Bersihkan memori tiket setelah selesai diproses
         if (GlobalVariableCheck(patGvKey)) GlobalVariableDel(patGvKey);
         GlobalVariableDel("VIKAR_DIR_"  + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString(todayTrades[k].ticket));
      }'''
    c = c.replace(old_cb_mt4, new_cb_mt4)

    # 9. Update BUY entry score evaluation in MT4
    old_buy_score_mt4 = '''         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         if (scoreRes.totalScore < effectiveMinScoreBUY)
         {
            if (InpUseSelfHealing && g_autopsy.isActive)
               g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else
               g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
         }'''

    new_buy_score_mt4 = '''         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis, Penalti Arah & Jam Rawan
         double dirPenaltyBUY = 0.0;
         if (InpUseDirectionalLearning && g_autopsy.isActive && g_autopsy.failedDirection == 1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
         {
            dirPenaltyBUY = InpDirectionalPenaltyScore;
         }

         double hourPenaltyBUY = 0.0;
         if (InpUseHourlyLearning && g_autopsy.isActive && g_autopsy.toxicHour == Hour())
         {
            hourPenaltyBUY = 10.0;
         }

         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltyBUY + hourPenaltyBUY;

         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         if (scoreRes.totalScore < effectiveMinScoreBUY)
         {
            if (dirPenaltyBUY > 0.0)
               g_lastSignalType = "KOREKSI DIRI: PENALTI BUY (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else if (hourPenaltyBUY > 0.0)
               g_lastSignalType = "KOREKSI DIRI: JAM RAWAN H:" + IntegerToString(Hour()) + " (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else if (InpUseSelfHealing && g_autopsy.isActive)
               g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else
               g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
         }'''
    c = c.replace(old_buy_score_mt4, new_buy_score_mt4)

    # 10. Update BUY execution snapshot in MT4
    old_buy_exec_mt4 = '''             if (ticket > 0)
             {
                if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                   g_autopsy.tradesWithExtraBuffer--;
                GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)(isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));'''

    new_buy_exec_mt4 = '''             if (ticket > 0)
             {
                if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                   g_autopsy.tradesWithExtraBuffer--;
                int execPatId = isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);
                SaveTradeEntrySnapshotMT4(ticket, execPatId, 1, scoreRes.totalScore, currentAtr);'''
    c = c.replace(old_buy_exec_mt4, new_buy_exec_mt4)

    # 11. Update SELL entry score evaluation in MT4
    old_sell_score_mt4 = '''      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
      if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
          g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
      {
         int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
         g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
         return;
      }

      if (scoreRes.totalScore < effectiveMinScoreSELL)
      {
         if (InpUseSelfHealing && g_autopsy.isActive)
            g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else
            g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
      }'''

    new_sell_score_mt4 = '''      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis, Penalti Arah & Jam Rawan
      double dirPenaltySELL = 0.0;
      if (InpUseDirectionalLearning && g_autopsy.isActive && g_autopsy.failedDirection == -1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
      {
         dirPenaltySELL = InpDirectionalPenaltyScore;
      }

      double hourPenaltySELL = 0.0;
      if (InpUseHourlyLearning && g_autopsy.isActive && g_autopsy.toxicHour == Hour())
      {
         hourPenaltySELL = 10.0;
      }

      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltySELL + hourPenaltySELL;

      if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
          g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
      {
         int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
         g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
         return;
      }

      if (scoreRes.totalScore < effectiveMinScoreSELL)
      {
         if (dirPenaltySELL > 0.0)
            g_lastSignalType = "KOREKSI DIRI: PENALTI SELL (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else if (hourPenaltySELL > 0.0)
            g_lastSignalType = "KOREKSI DIRI: JAM RAWAN H:" + IntegerToString(Hour()) + " (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else if (InpUseSelfHealing && g_autopsy.isActive)
            g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else
            g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
      }'''
    c = c.replace(old_sell_score_mt4, new_sell_score_mt4)

    # 12. Update SELL execution snapshot in MT4
    old_sell_exec_mt4 = '''             if (ticket > 0)
             {
                if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                   g_autopsy.tradesWithExtraBuffer--;
                GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)(isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));'''

    new_sell_exec_mt4 = '''             if (ticket > 0)
             {
                if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                   g_autopsy.tradesWithExtraBuffer--;
                int execPatId = isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);
                SaveTradeEntrySnapshotMT4(ticket, execPatId, -1, scoreRes.totalScore, currentAtr);'''
    c = c.replace(old_sell_exec_mt4, new_sell_exec_mt4)

    # 13. Update OnInit in MT4 to restore autopsy state
    old_init_mt4 = '''   InitPatternMatrix();

   lastBarTime = Time[0];'''

    new_init_mt4 = '''   InitPatternMatrix();
   LoadAutopsyStateMT4();

   lastBarTime = Time[0];'''
    c = c.replace(old_init_mt4, new_init_mt4)

    # 14. Update Dashboard HUD in MT4
    old_hud_mt4 = '''   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Pts | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");'''

    new_hud_mt4 = '''   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      string extraInfo = "";
      if (g_autopsy.failedDirection == 1 && TimeCurrent() < g_autopsy.directionPenaltyUntil) extraInfo += " [BUY PENALTY]";
      else if (g_autopsy.failedDirection == -1 && TimeCurrent() < g_autopsy.directionPenaltyUntil) extraInfo += " [SELL PENALTY]";
      if (g_autopsy.toxicHour >= 0) extraInfo += " [TOXIC H:" + IntegerToString(g_autopsy.toxicHour) + "]";
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Pts" + extraInfo + " | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[AI Brain / Heal]: " + healDisplay, healClr, 7, "Segoe UI Bold");'''
    c = c.replace(old_hud_mt4, new_hud_mt4)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

    print("[SUCCESS] MT4 EA completely upgraded to v3.10!")
    return True

if __name__ == "__main__":
    upgrade_mt4()
