import re
import shutil

def upgrade_mt5():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    bak_path = path + ".v300.bak"
    shutil.copyfile(bak_path, path)

    with open(path, "r", encoding="utf-8") as f:
        c = f.read()

    # 1. Update version property
    c = c.replace('#property version   "3.00"', '#property version   "3.10"')
    c = c.replace('Vikar EA 4-Pillar Pro - Apex Grandmaster Edition v3.00', 'Vikar EA 4-Pillar Pro - Apex Grandmaster Edition v3.10 (Adaptive AI Learning)')

    # 2. Add input parameters for directional & hourly learning
    old_inputs = 'input double        InpPatternPenaltyScore     = 15.0;         // Penalti Pengetatan Skor untuk Pola Lemah'
    new_inputs = '''input double        InpPatternPenaltyScore     = 15.0;         // Penalti Pengetatan Skor untuk Pola Lemah
input bool          InpUseDirectionalLearning      = true;         // Proteksi Anti-Loss Berulang Searah (Directional Bias Learning)
input double        InpDirectionalPenaltyScore     = 10.0;         // Penalti Skor Tambahan untuk Arah yang Baru Saja Gagal
input int           InpDirectionalPenaltyBars      = 12;           // Durasi Penalti Arah Gagal (Bars Lilin)
input bool          InpUseHourlyLearning           = true;         // Hindari Jam Rawan Loss Berulang Hari Ini (Hourly Learning)'''
    c = c.replace(old_inputs, new_inputs)

    # 3. Update LossAutopsyReport struct & TOTAL_TRACKED_PATTERNS
    old_struct = '''struct LossAutopsyReport
{
   bool                 isActive;
   ulong                failedTicket;
   datetime             timeLoss;
   ENUM_CANDLE_PATTERN  failedPattern;
   string               failedPatternName;
   string               lossReason;
   double               scorePenalty;
   datetime             quarantineUntilBar;
   int                  tradesWithExtraBuffer;
};
LossAutopsyReport g_autopsy;
//+------------------------------------------------------------------+
//| STRUKTUR & MEMORI DINAMIS: PATTERN PERFORMANCE MATRIX (v2.50)   |
//+------------------------------------------------------------------+
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
   ulong                failedTicket;
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
//+------------------------------------------------------------------+
//| STRUKTUR & MEMORI DINAMIS: PATTERN PERFORMANCE MATRIX (v3.10)   |
//+------------------------------------------------------------------+
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

    # 4. Extract CalculateChoppinessIndexMQL5 from the original code
    chop_match = re.search(r'//\+------------------------------------------------------------------\+\s*//\|\s*FUNGSI MATEMATIS: CHOPPINESS INDEX \(CI\) MQL5.*?double CalculateChoppinessIndexMQL5\(int period\)\s*\{.*?\n\}', c, re.DOTALL)
    if not chop_match:
        print("[ERROR] Could not find CalculateChoppinessIndexMQL5!")
        return False
    choppiness_code = chop_match.group(0)

    # 5. Remove entire old block between OnDeinit and CloseAllOpenOrders
    old_block_match = re.search(r'//\+------------------------------------------------------------------\+\s*//\|\s*MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS.*?(?=//\+------------------------------------------------------------------\+\s*//\|\s*EMERGENCY CLOSE ALL OPEN POSITIONS)', c, re.DOTALL)
    if not old_block_match:
        print("[ERROR] Could not match old block between OnDeinit and CloseAllOpenOrders!")
        return False
    c = c[:old_block_match.start()] + c[old_block_match.end():]

    # 6. Define complete upgraded AI Learning Engine block to place ABOVE OnInit()
    ai_learning_block = choppiness_code + r'''

//+------------------------------------------------------------------+
//| SISTEM PEMBELAJARAN & OTOPSI ADAPTIF PASCA-LOSS (v3.10 MQL5)     |
//+------------------------------------------------------------------+
void SaveTradeEntrySnapshotMQL5(ulong orderTicket, ulong dealTicket, int patternId, int direction, double currentScore, double currentAtr)
{
   MqlDateTime mdt;
   TimeCurrent(mdt);

   GlobalVariableSet("VIKAR_PAT_"  + IntegerToString((long)orderTicket), (double)patternId);
   GlobalVariableSet("VIKAR_DIR_"  + IntegerToString((long)orderTicket), (double)direction);
   GlobalVariableSet("VIKAR_HOUR_" + IntegerToString((long)orderTicket), (double)mdt.hour);
   GlobalVariableSet("VIKAR_ATR_"  + IntegerToString((long)orderTicket), currentAtr);
   GlobalVariableSet("VIKAR_SCO_"  + IntegerToString((long)orderTicket), currentScore);

   if (dealTicket > 0 && dealTicket != orderTicket)
   {
      GlobalVariableSet("VIKAR_PAT_"  + IntegerToString((long)dealTicket), (double)patternId);
      GlobalVariableSet("VIKAR_DIR_"  + IntegerToString((long)dealTicket), (double)direction);
      GlobalVariableSet("VIKAR_HOUR_" + IntegerToString((long)dealTicket), (double)mdt.hour);
      GlobalVariableSet("VIKAR_ATR_"  + IntegerToString((long)dealTicket), currentAtr);
      GlobalVariableSet("VIKAR_SCO_"  + IntegerToString((long)dealTicket), currentScore);
   }
}

void SaveAutopsyStateMQL5()
{
   string pfx = "VIKAR_MT5_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
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

void LoadAutopsyStateMQL5()
{
   string pfx = "VIKAR_MT5_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
   if (GlobalVariableCheck(pfx + "ACTIVE") && GlobalVariableGet(pfx + "ACTIVE") > 0.5)
   {
      g_autopsy.isActive              = true;
      g_autopsy.failedTicket          = (ulong)GlobalVariableGet(pfx + "TICKET");
      g_autopsy.failedPattern         = (ENUM_CANDLE_PATTERN)(int)GlobalVariableGet(pfx + "PAT");
      g_autopsy.scorePenalty          = GlobalVariableGet(pfx + "PENALTY");
      g_autopsy.quarantineUntilBar    = (datetime)GlobalVariableGet(pfx + "QUARANTINE");
      g_autopsy.tradesWithExtraBuffer = (int)GlobalVariableGet(pfx + "BUFFER");
      g_autopsy.failedDirection       = (int)GlobalVariableGet(pfx + "DIR");
      g_autopsy.directionPenaltyUntil = (datetime)GlobalVariableGet(pfx + "DIRUNTIL");
      g_autopsy.toxicHour             = (int)GlobalVariableGet(pfx + "TOXICHOUR");
      g_autopsy.lossReason            = "PEMULIHAN STATUS PASCA-RESTART (PERSISTENT)";
      Print("[SELF-HEALING RESTORED MT5] Status otopsi berhasil dipulihkan dari memori persisten.");
   }
   else
   {
      g_autopsy.isActive              = false;
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
      g_autopsy.toxicHour             = -1;
   }
}

void InitPatternMatrixMQL5()
{
   string patNames[TOTAL_TRACKED_PATTERNS] = {
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
   };

   int blacklistedCount = 0;
   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      g_patternMatrix[i].patternId = i;
      g_patternMatrix[i].name      = patNames[i];

      string gvWKey = "VIKAR_MT5_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);
      string gvLKey = "VIKAR_MT5_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);

      int wins   = GlobalVariableCheck(gvWKey) ? (int)GlobalVariableGet(gvWKey) : 0;
      int losses = GlobalVariableCheck(gvLKey) ? (int)GlobalVariableGet(gvLKey) : 0;
      int total  = wins + losses;
      double wr  = (total > 0) ? ((double)wins * 100.0 / (double)total) : 0.0;

      g_patternMatrix[i].wins          = wins;
      g_patternMatrix[i].losses        = losses;
      g_patternMatrix[i].total         = total;
      g_patternMatrix[i].winRate       = wr;
      g_patternMatrix[i].isBlacklisted = false;
      g_patternMatrix[i].scoreModifier = 0.0;

      if (InpUsePatternMatrix && total >= InpMinTradesForPatternEval)
      {
         if (wr < InpPatternBlacklistWinrate)
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            blacklistedCount++;
         }
         else if (wr >= InpPatternBoostWinrate)
         {
            g_patternMatrix[i].isBlacklisted = false;
            g_patternMatrix[i].scoreModifier = InpPatternBoostScore;
         }
      }

      if (total >= 2 && wr > highestWR)
      {
         highestWR = wr;
         bestName  = patNames[i] + " (" + DoubleToString(wr, 0) + "%)";
      }
   }

   g_bestPatternStr = bestName;
   Print("[AI PATTERN MATRIX MT5] Diinisialisasi. Pola Aktif: ", TOTAL_TRACKED_PATTERNS, " | Ter-blacklist: ", blacklistedCount, " | Terbaik: ", g_bestPatternStr);
}

void UpdatePatternRecordMQL5(int patternId, bool isWin)
{
   if (patternId < 0 || patternId >= TOTAL_TRACKED_PATTERNS) return;

   string gvWKey = "VIKAR_MT5_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);
   string gvLKey = "VIKAR_MT5_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);

   if (isWin)
   {
      g_patternMatrix[patternId].wins++;
      GlobalVariableSet(gvWKey, (double)g_patternMatrix[patternId].wins);
   }
   else
   {
      g_patternMatrix[patternId].losses++;
      GlobalVariableSet(gvLKey, (double)g_patternMatrix[patternId].losses);
   }

   g_patternMatrix[patternId].total = g_patternMatrix[patternId].wins + g_patternMatrix[patternId].losses;
   if (g_patternMatrix[patternId].total > 0)
      g_patternMatrix[patternId].winRate = (double)g_patternMatrix[patternId].wins * 100.0 / (double)g_patternMatrix[patternId].total;

   if (InpUsePatternMatrix && g_patternMatrix[patternId].total >= InpMinTradesForPatternEval)
   {
      if (g_patternMatrix[patternId].winRate < InpPatternBlacklistWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = true;
         g_patternMatrix[patternId].scoreModifier = -InpPatternPenaltyScore;
         Print("[AI MATRIX WARNING MT5] Pola '", g_patternMatrix[patternId].name, "' di-BLACKLIST sementara (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% < ", InpPatternBlacklistWinrate, "%).");
      }
      else if (g_patternMatrix[patternId].winRate >= InpPatternBoostWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = InpPatternBoostScore;
         Print("[AI MATRIX BOOST MT5] Pola '", g_patternMatrix[patternId].name, "' mendapatkan BOOST +", InpPatternBoostScore, " Poin (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% >= ", InpPatternBoostWinrate, "%).");
      }
      else
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = 0.0;
      }
   }

   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";
   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      if (g_patternMatrix[i].total >= 2 && g_patternMatrix[i].winRate > highestWR)
      {
         highestWR = g_patternMatrix[i].winRate;
         bestName  = g_patternMatrix[i].name + " (" + DoubleToString(g_patternMatrix[i].winRate, 0) + "%)";
      }
   }
   g_bestPatternStr = bestName;
}

void PerformLossAutopsyMQL5(ulong ticket, ulong posId, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil snapshot data transaksi dari memori Global Variable
   string patGvKeyPos = "VIKAR_PAT_" + IntegerToString((long)posId);
   string patGvKeyTkt = "VIKAR_PAT_" + IntegerToString((long)ticket);
   ENUM_CANDLE_PATTERN pat = PATTERN_NONE;
   int rawPatId = 0;
   if (GlobalVariableCheck(patGvKeyPos))
   {
      rawPatId = (int)GlobalVariableGet(patGvKeyPos);
      pat = (ENUM_CANDLE_PATTERN)rawPatId;
   }
   else if (GlobalVariableCheck(patGvKeyTkt))
   {
      rawPatId = (int)GlobalVariableGet(patGvKeyTkt);
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

   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if (pat != PATTERN_NONE || rawPatId >= 11)
      g_autopsy.quarantineUntilBar = currentBarTime + (InpQuarantinePatternBars * PeriodSeconds(_Period));
   else
      g_autopsy.quarantineUntilBar = 0;

   // Ambil Direction (BUY = +1, SELL = -1)
   int tradeDir = 0;
   string dirKeyPos = "VIKAR_DIR_" + IntegerToString((long)posId);
   string dirKeyTkt = "VIKAR_DIR_" + IntegerToString((long)ticket);
   if (GlobalVariableCheck(dirKeyPos)) tradeDir = (int)GlobalVariableGet(dirKeyPos);
   else if (GlobalVariableCheck(dirKeyTkt)) tradeDir = (int)GlobalVariableGet(dirKeyTkt);

   if (InpUseDirectionalLearning && tradeDir != 0)
   {
      g_autopsy.failedDirection       = tradeDir;
      g_autopsy.directionPenaltyUntil = currentBarTime + (InpDirectionalPenaltyBars * PeriodSeconds(_Period));
   }
   else
   {
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
   }

   // Ambil Jam Transaksi (0..23) dan Lacak Jam Rawan Loss Berulang
   int tradeHour = -1;
   string hrKeyPos = "VIKAR_HOUR_" + IntegerToString((long)posId);
   string hrKeyTkt = "VIKAR_HOUR_" + IntegerToString((long)ticket);
   if (GlobalVariableCheck(hrKeyPos)) tradeHour = (int)GlobalVariableGet(hrKeyPos);
   else if (GlobalVariableCheck(hrKeyTkt)) tradeHour = (int)GlobalVariableGet(hrKeyTkt);

   if (InpUseHourlyLearning && tradeHour >= 0 && tradeHour <= 23)
   {
      string hLossKey = "VIKAR_MT5_HLOSS_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(tradeHour);
      int currentHLoss = GlobalVariableCheck(hLossKey) ? (int)GlobalVariableGet(hLossKey) : 0;
      currentHLoss++;
      GlobalVariableSet(hLossKey, (double)currentHLoss);

      if (currentHLoss >= 2)
      {
         g_autopsy.toxicHour = tradeHour;
         Print("[HOURLY LEARNING MT5] Jam ", tradeHour, ":00 server terdeteksi rawan loss berulang (", currentHLoss, "x loss). Proteksi jam aktif!");
      }
      else
         g_autopsy.toxicHour = -1;
   }
   else
      g_autopsy.toxicHour = -1;

   // 2. Diagnosa Anatomi Mendalam Penyebab Loss (7 Skenario Institusional)
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   CopyRates(_Symbol, _Period, 0, 5, rates);

   double atrVal[];
   ArraySetAsSeries(atrVal, true);
   CopyBuffer(h_atr14, 0, 0, 3, atrVal);
   double currentAtr = (ArraySize(atrVal) > 1) ? atrVal[1] : PipToPrice(20.0);

   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   CopyBuffer(h_ema125, 0, 0, 3, ema125Val);
   double currentEma125 = (ArraySize(ema125Val) > 1) ? ema125Val[1] : 0.0;

   double lastBarRange = (ArraySize(rates) > 1) ? (rates[1].high - rates[1].low) : 0.0;
   ENUM_HTF_BIAS currentHTFBias = AnalyzeHTFMacroTrend();

   string reason = "PENGUJIAN LEVEL GAGAL (SUPPORT/RESISTEN DITEMBUS)";
   if (lastBarRange >= (2.0 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPREAD SPIKE)";
   else if (g_currentChoppiness > 61.8)
      reason = "JEBAKAN SIDEWAYS NOISE (PASAR CHOPPY KOMPRESI)";
   else if (g_smcAnalysis.hasCHoCH || (ArraySize(rates) > 1 && currentEma125 > 0 && ((rates[1].close < currentEma125 && rates[1].open > currentEma125) || (rates[1].close > currentEma125 && rates[1].open < currentEma125))))
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
   SaveAutopsyStateMQL5();

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT5] Posisi Deal #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
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
      string notif = "OTOPSI PASCA-SL #" + IntegerToString((long)ticket) + " (" + DoubleToString(lossAmount, 2) + ")\nDiagnosa: " + reason + "\nKoreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE || rawPatId >= 11)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      if (tradeDir != 0 && InpUseDirectionalLearning)
         notif += " Penalti arah " + (tradeDir == 1 ? "BUY" : "SELL") + " aktif.";
      SendPushAlert(notif);
   }
}

void ResetSelfHealingStateMQL5(string triggerReason)
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
   SaveAutopsyStateMQL5();
   Print("[SELF-HEALING NORMALIZED MT5] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}
'''

    # Insert above OnInit()
    init_anchor = '//+------------------------------------------------------------------+\n//| ON INIT                                                          |\n//+------------------------------------------------------------------+'
    if init_anchor not in c:
        print("[ERROR] OnInit anchor not found!")
        return False

    c = c.replace(init_anchor, ai_learning_block + '\n' + init_anchor)

    # 7. Update OnInit() to call InitPatternMatrixMQL5() & LoadAutopsyStateMQL5()
    old_init_end = '''   // Aktifkan penerimaan event mouse untuk fitur Drag & Drop Dashboard
   ChartSetInteger(0, CHART_EVENT_MOUSE_MOVE, true);
   Comment("");

   Print("=== VIKAR EA 4-PILLAR PRO INITIALIZED SUCCESSFULLY ===");'''

    new_init_end = '''   // Aktifkan penerimaan event mouse untuk fitur Drag & Drop Dashboard
   ChartSetInteger(0, CHART_EVENT_MOUSE_MOVE, true);
   Comment("");

   // Inisialisasi AI Pattern Matrix & Pulihkan Memori Pembelajaran Pasca-Restart
   InitPatternMatrixMQL5();
   LoadAutopsyStateMQL5();

   Print("=== VIKAR EA 4-PILLAR PRO INITIALIZED SUCCESSFULLY ===");'''
    c = c.replace(old_init_end, new_init_end)

    # 8. Update CheckCircuitBreakers() ticket mapping & safe cleanup
    old_cb_loop = '''      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
      {
         consecutiveLosses++;
         lastLossTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
         if (InpUseSelfHealing && g_autopsy.failedTicket != ticket)
            PerformLossAutopsyMQL5(ticket, lastLossTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER KERUGIAN! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingStateMQL5("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }

      // Pembaruan Statistik Pattern Performance Matrix MT5 (v2.50)
      string procKey = "VIKAR_MT5_PMR_PROC_" + IntegerToString((long)ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patGvKey = "VIKAR_PAT_" + IntegerToString((long)ticket);
         int patId = GlobalVariableCheck(patGvKey) ? (int)GlobalVariableGet(patGvKey) : 0;
         if (profit > 0.01)
            UpdatePatternRecordMQL5(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecordMQL5(patId, false);
         GlobalVariableSet(procKey, 1.0);
      }'''

    new_cb_loop = '''      ulong posId = (ulong)HistoryDealGetInteger(ticket, DEAL_POSITION_ID);
      if (posId == 0) posId = (ulong)HistoryDealGetInteger(ticket, DEAL_ORDER);

      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
      {
         consecutiveLosses++;
         lastLossTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
         if (InpUseSelfHealing && g_autopsy.failedTicket != ticket)
            PerformLossAutopsyMQL5(ticket, posId, lastLossTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER KERUGIAN! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingStateMQL5("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }

      // Pembaruan Statistik Pattern Performance Matrix MT5 (v3.10)
      string procKey = "VIKAR_MT5_PMR_PROC_" + IntegerToString((long)ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patKeyPos = "VIKAR_PAT_" + IntegerToString((long)posId);
         string patKeyTkt = "VIKAR_PAT_" + IntegerToString((long)ticket);
         int patId = 0;
         if (GlobalVariableCheck(patKeyPos)) patId = (int)GlobalVariableGet(patKeyPos);
         else if (GlobalVariableCheck(patKeyTkt)) patId = (int)GlobalVariableGet(patKeyTkt);

         if (profit > 0.01)
            UpdatePatternRecordMQL5(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecordMQL5(patId, false);
         GlobalVariableSet(procKey, 1.0);

         // Bersihkan memori tiket setelah selesai diproses
         if (GlobalVariableCheck(patKeyPos)) GlobalVariableDel(patKeyPos);
         if (GlobalVariableCheck(patKeyTkt)) GlobalVariableDel(patKeyTkt);
         GlobalVariableDel("VIKAR_DIR_" + IntegerToString((long)posId));
         GlobalVariableDel("VIKAR_DIR_" + IntegerToString((long)ticket));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString((long)posId));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString((long)ticket));
      }'''
    c = c.replace(old_cb_loop, new_cb_loop)

    # 9. Update BUY entry evaluation for Directional & Hourly Learning
    old_buy_score = '''         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
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

    new_buy_score = '''         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis, Penalti Arah & Jam Rawan
         double dirPenaltyBUY = 0.0;
         if (InpUseDirectionalLearning && g_autopsy.isActive && g_autopsy.failedDirection == 1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
         {
            dirPenaltyBUY = InpDirectionalPenaltyScore;
         }

         double hourPenaltyBUY = 0.0;
         MqlDateTime mdtNowBuy;
         TimeCurrent(mdtNowBuy);
         if (InpUseHourlyLearning && g_autopsy.isActive && g_autopsy.toxicHour == mdtNowBuy.hour)
         {
            hourPenaltyBUY = 10.0;
         }

         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltyBUY + hourPenaltyBUY;

         if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         if (scoreRes.totalScore < effectiveMinScoreBUY)
         {
            if (dirPenaltyBUY > 0.0)
               g_lastSignalType = "KOREKSI DIRI: PENALTI BUY (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else if (hourPenaltyBUY > 0.0)
               g_lastSignalType = "KOREKSI DIRI: JAM RAWAN H:" + IntegerToString(mdtNowBuy.hour) + " (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else if (InpUseSelfHealing && g_autopsy.isActive)
               g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else
               g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
         }'''
    c = c.replace(old_buy_score, new_buy_score)

    # 10. Update BUY trade execution snapshot call
    old_buy_exec = '''             if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
             {
                ulong buyTicket = trade.ResultOrder();
                if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                   g_autopsy.tradesWithExtraBuffer--;
                GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)buyTicket), (double)(isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)));'''

    new_buy_exec = '''             if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
             {
                ulong buyTicket = trade.ResultOrder();
                ulong buyDeal   = trade.ResultDeal();
                if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                   g_autopsy.tradesWithExtraBuffer--;
                int execPatId = isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);
                SaveTradeEntrySnapshotMQL5(buyTicket, buyDeal, execPatId, 1, scoreRes.totalScore, currentAtr);'''
    c = c.replace(old_buy_exec, new_buy_exec)

    # 11. Update SELL entry evaluation for Directional & Hourly Learning
    old_sell_score = '''      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
      if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
          g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
      {
         int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
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

    new_sell_score = '''      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis, Penalti Arah & Jam Rawan
      double dirPenaltySELL = 0.0;
      if (InpUseDirectionalLearning && g_autopsy.isActive && g_autopsy.failedDirection == -1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
      {
         dirPenaltySELL = InpDirectionalPenaltyScore;
      }

      double hourPenaltySELL = 0.0;
      MqlDateTime mdtNowSell;
      TimeCurrent(mdtNowSell);
      if (InpUseHourlyLearning && g_autopsy.isActive && g_autopsy.toxicHour == mdtNowSell.hour)
      {
         hourPenaltySELL = 10.0;
      }

      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltySELL + hourPenaltySELL;

      if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
          g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
      {
         int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
         g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
         return;
      }

      if (scoreRes.totalScore < effectiveMinScoreSELL)
      {
         if (dirPenaltySELL > 0.0)
            g_lastSignalType = "KOREKSI DIRI: PENALTI SELL (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else if (hourPenaltySELL > 0.0)
            g_lastSignalType = "KOREKSI DIRI: JAM RAWAN H:" + IntegerToString(mdtNowSell.hour) + " (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else if (InpUseSelfHealing && g_autopsy.isActive)
            g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else
            g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
      }'''
    c = c.replace(old_sell_score, new_sell_score)

    # 12. Update SELL trade execution snapshot call
    old_sell_exec = '''          if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
          {
             ulong sellTicket = trade.ResultOrder();
             if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                g_autopsy.tradesWithExtraBuffer--;
             GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)sellTicket), (double)(isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)));'''

    new_sell_exec = '''          if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
          {
             ulong sellTicket = trade.ResultOrder();
             ulong sellDeal   = trade.ResultDeal();
             if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                g_autopsy.tradesWithExtraBuffer--;
             int execPatId = isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);
             SaveTradeEntrySnapshotMQL5(sellTicket, sellDeal, execPatId, -1, scoreRes.totalScore, currentAtr);'''
    c = c.replace(old_sell_exec, new_sell_exec)

    # 13. Update Dashboard HUD display for AI Brain / Self-Healing
    old_hud_heal = '''   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Pts | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");'''

    new_hud_heal = '''   string healDisplay = "STANDBY (NORMAL)";
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
    c = c.replace(old_hud_heal, new_hud_heal)

    with open(path, "w", encoding="utf-8") as f:
        f.write(c)

    print("[SUCCESS] MT5 EA completely upgraded to v3.10!")
    return True

if __name__ == "__main__":
    upgrade_mt5()
