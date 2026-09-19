import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add enum ENUM_MARKET_REGIME
regime_enum_code = """
enum ENUM_MARKET_REGIME
{
   REGIME_STRONG_TREND,     // Tren Sangat Kuat (CI < 38.2) - Momentum Breakout Ideal
   REGIME_NORMAL,           // Tren Normal / Sehat (38.2 <= CI <= 61.8) - 4-Pillar Sniper Standard
   REGIME_CHOPPY_SIDEWAYS   // Sideways Sempit / Kompresi (CI > 61.8) - Bahaya Fakeout Tinggi!
};
"""
if "enum ENUM_MARKET_REGIME" not in content:
    content = content.replace("enum ENUM_LOT_TYPE", regime_enum_code.strip() + "\n\nenum ENUM_LOT_TYPE")

# 2. Add Section 8.5 and 8.6 Inputs
inputs_85_86 = """
input group "=== 8.5 DYNAMIC PATTERN PERFORMANCE MATRIX (AI LEARNING v2.50) ==="
input bool          InpUsePatternMatrix        = true;         // Aktifkan Memori Rapor & Bobot Kinerja Pola
input int           InpMinTradesForPatternEval = 3;            // Minimal Transaksi Sebelum Evaluasi Pola
input double        InpPatternBlacklistWinrate = 40.0;         // Ambang Batas Blacklist Pola (Winrate < 40%)
input double        InpPatternBoostWinrate     = 70.0;         // Ambang Batas Boost Pola (Winrate > 70%)
input double        InpPatternBoostScore       = 10.0;         // Bonus Skor Konfluensi untuk Pola Akurat
input double        InpPatternPenaltyScore     = 15.0;         // Penalti Pengetatan Skor untuk Pola Lemah

input group "=== 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ==="
input bool          InpUseRegimeFilter         = true;         // Aktifkan Sensor Cuaca Pasar (Trending vs Choppy)
input int           InpChoppinessPeriod        = 14;           // Periode Perhitungan Choppiness Index (CI)
input double        InpChoppyThreshold         = 61.8;         // Ambang Batas Pasar Choppy / Sideways (CI > 61.8)
input double        InpTrendingThreshold       = 38.2;         // Ambang Batas Pasar Tren Kuat (CI < 38.2)
input bool          InpBlockBreakoutInChoppy   = true;         // Blokir Momentum Breakout Saat Pasar Choppy
"""
if "InpUsePatternMatrix" not in content:
    content = content.replace(
        'input bool          InpAutopsyNotifyPush           = true;         // Kirim Laporan Otopsi Pasca-Loss ke Smartphone',
        'input bool          InpAutopsyNotifyPush           = true;         // Kirim Laporan Otopsi Pasca-Loss ke Smartphone\n' + inputs_85_86.strip()
    )

# 3. Add PatternRecord struct, array, and market regime globals
pattern_matrix_struct = """
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
PatternRecord g_patternMatrix[TOTAL_TRACKED_PATTERNS];

ENUM_MARKET_REGIME g_currentRegime     = REGIME_NORMAL;
double             g_currentChoppiness = 50.0;
string             g_bestPatternStr    = "BELUM ADA DATA";
"""
if "struct PatternRecord" not in content:
    content = content.replace("LossAutopsyReport g_autopsy;", "LossAutopsyReport g_autopsy;\n" + pattern_matrix_struct.strip())

# 4. Add Choppiness Index calculation function and Pattern Matrix functions
matrix_functions = """
//+------------------------------------------------------------------+
//| FUNGSI MATEMATIS: CHOPPINESS INDEX (CI) MQL5 DENGAN LOG10       |
//+------------------------------------------------------------------+
double CalculateChoppinessIndexMQL5(int period)
{
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if (CopyRates(_Symbol, _Period, 0, period + 2, rates) < period + 2)
      return 50.0;

   double sumTR = 0.0;
   double highMax = rates[1].high;
   double lowMin  = rates[1].low;

   for (int i = 1; i <= period; i++)
   {
      double h = rates[i].high;
      double l = rates[i].low;
      double prevClose = rates[i + 1].close;

      double tr1 = h - l;
      double tr2 = MathAbs(h - prevClose);
      double tr3 = MathAbs(l - prevClose);
      double trueRange = MathMax(tr1, MathMax(tr2, tr3));

      sumTR += trueRange;
      if (h > highMax) highMax = h;
      if (l < lowMin)  lowMin  = l;
   }

   double range = highMax - lowMin;
   if (range <= 0.00001 || sumTR <= 0.00001) return 50.0;

   double log10Period = MathLog(period) / MathLog(10.0);
   double log10Val    = MathLog(sumTR / range) / MathLog(10.0);

   double ci = 100.0 * (log10Val / log10Period);
   if (ci < 0.0) ci = 0.0;
   if (ci > 100.0) ci = 100.0;

   return ci;
}

//+------------------------------------------------------------------+
//| INISIALISASI & PEMULIHAN MEMORI PATTERN PERFORMANCE MATRIX MQL5  |
//+------------------------------------------------------------------+
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
      "Momentum BOS Breakout"
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

//+------------------------------------------------------------------+
//| PEMBARUAN REKOR SETIAP KALI DEAL TERTUTUP MQL5                   |
//+------------------------------------------------------------------+
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

   // Cari pola dengan performa terbaik
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
"""
if "CalculateChoppinessIndexMQL5" not in content:
    content = content.replace("void ResetSelfHealingStateMQL5(string triggerReason)", matrix_functions.strip() + "\n\nvoid ResetSelfHealingStateMQL5(string triggerReason)")

# 5. Call InitPatternMatrixMQL5() in OnInit()
if "InitPatternMatrixMQL5();" not in content:
    content = content.replace(
        'Print("Start Time: ", TimeToString(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Modal: $", DoubleToString(g_eaInitialBalance, 2));',
        'Print("Start Time: ", TimeToString(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Modal: $", DoubleToString(g_eaInitialBalance, 2));\n   InitPatternMatrixMQL5();'
    )

# 6. Hook deal evaluation in CheckCircuitBreakers() for MT5
old_deal_hook = """      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
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
      }"""

new_deal_hook = """      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
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
      }"""

if "VIKAR_MT5_PMR_PROC_" not in content:
    content = content.replace(old_deal_hook, new_deal_hook)

# 7. Hook BUY logic in CheckTradeSignal()
old_buy_mt5 = """         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, rates, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
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
         }

         // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = rates[1].close - rates[1].open;
            bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (rates[1].close > currentEma8 && currentEma8 > currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close > lastSwingHigh.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || tickVolume[1] >= (long)(1.3 * (double)tickVolume[2])));

            if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
               isMomentumBreakout = true;
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk);"""

new_buy_mt5 = """         // 1. Evaluasi Cuaca Pasar (Market Regime Classifier CI v2.50)
         g_currentChoppiness = CalculateChoppinessIndexMQL5(InpChoppinessPeriod);
         if (g_currentChoppiness > InpChoppyThreshold)
            g_currentRegime = REGIME_CHOPPY_SIDEWAYS;
         else if (g_currentChoppiness < InpTrendingThreshold)
            g_currentRegime = REGIME_STRONG_TREND;
         else
            g_currentRegime = REGIME_NORMAL;

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, rates, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreBUY += 10.0; // Filter ekstra saat pasar sideways sempit

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
         }

         // 3. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways (Fakeout 85%)
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody = rates[1].close - rates[1].open;
               bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (rates[1].close > currentEma8 && currentEma8 > currentEma21);
               bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close > lastSwingHigh.price || g_smcAnalysis.hasBOS);
               bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || tickVolume[1] >= (long)(1.3 * (double)tickVolume[2])));

               if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
                  isMomentumBreakout = true;
            }
         }

         // 4. Evaluasi Pattern Performance Matrix MT5 (AI Pattern Learning v2.50)
         int activePatIdBUY = isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern;
         if (InpUsePatternMatrix)
         {
            if (g_patternMatrix[activePatIdBUY].isBlacklisted)
            {
               g_lastSignalType = "AI MATRIX: POLA " + g_patternMatrix[activePatIdBUY].name + " DI-BLACKLIST (WR: " + DoubleToString(g_patternMatrix[activePatIdBUY].winRate, 1) + "%)";
               return;
            }
            effectiveMinScoreBUY -= g_patternMatrix[activePatIdBUY].scoreModifier;
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk);"""

if "CalculateChoppinessIndexMQL5(InpChoppinessPeriod)" not in content:
    content = content.replace(old_buy_mt5, new_buy_mt5)

# 8. Hook SELL logic in CheckTradeSignal()
old_sell_mt5 = """      ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, rates, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
      g_lastScoreResult = scoreRes;

      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
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
      }

      // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
      bool isMomentumBreakout = false;
      if (InpAllowMomentumBreakout)
      {
         double candleBody = rates[1].open - rates[1].close;
         bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
         bool isRibbonExpanding = (rates[1].close < currentEma8 && currentEma8 < currentEma21);
         bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close < lastSwingLow.price || g_smcAnalysis.hasBOS);
         bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || tickVolume[1] >= (long)(1.3 * (double)tickVolume[2])));

         if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
            isMomentumBreakout = true;
      }

      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                            (isMomentumBreakout && isHeadroomOk);"""

new_sell_mt5 = """      // 1. Evaluasi Cuaca Pasar (Market Regime Classifier CI v2.50)
      g_currentChoppiness = CalculateChoppinessIndexMQL5(InpChoppinessPeriod);
      if (g_currentChoppiness > InpChoppyThreshold)
         g_currentRegime = REGIME_CHOPPY_SIDEWAYS;
      else if (g_currentChoppiness < InpTrendingThreshold)
         g_currentRegime = REGIME_STRONG_TREND;
      else
         g_currentRegime = REGIME_NORMAL;

      ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, rates, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
      g_lastScoreResult = scoreRes;

      // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
      if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
         effectiveMinScoreSELL += 10.0; // Filter ekstra saat pasar sideways sempit

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
      }

      // 3. Deteksi Momentum Breakout / Expansion
      bool isMomentumBreakout = false;
      if (InpAllowMomentumBreakout)
      {
         // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways
         if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
         {
            double candleBody = rates[1].open - rates[1].close;
            bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (rates[1].close < currentEma8 && currentEma8 < currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close < lastSwingLow.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || tickVolume[1] >= (long)(1.3 * (double)tickVolume[2])));

            if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
               isMomentumBreakout = true;
         }
      }

      // 4. Evaluasi Pattern Performance Matrix MT5 (AI Pattern Learning v2.50)
      int activePatIdSELL = isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern;
      if (InpUsePatternMatrix)
      {
         if (g_patternMatrix[activePatIdSELL].isBlacklisted)
         {
            g_lastSignalType = "AI MATRIX: POLA " + g_patternMatrix[activePatIdSELL].name + " DI-BLACKLIST (WR: " + DoubleToString(g_patternMatrix[activePatIdSELL].winRate, 1) + "%)";
            return;
         }
         effectiveMinScoreSELL -= g_patternMatrix[activePatIdSELL].scoreModifier;
      }

      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                            (isMomentumBreakout && isHeadroomOk);"""

if "int activePatIdSELL = isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern;" not in content:
    content = content.replace(old_sell_mt5, new_sell_mt5)

# 9. Correct ticket pattern recording in trade.Buy and trade.Sell
content = content.replace(
    'GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)trade.ResultOrder()), (double)g_candleAnalysis.pattern);',
    'GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)trade.ResultOrder()), (double)(isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));'
)

# 10. Update Dashboard HUD height and add Regime & Pattern Matrix rows in MT5
content = content.replace(
    'int panelH = InpShowPnLStats ? 515 : 435;',
    'int panelH = InpShowPnLStats ? 555 : 475;'
)

old_hud_mt5 = """   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");
   currY += 144;"""

new_hud_mt5 = """   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");

   // Baris Cuaca Pasar (Market Regime Choppiness)
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
   CreateOrUpdateText("VIKAR_HUD_REGIME", panelX + 12, currY + 138, "[Cuaca Pasar]: " + regimeStr, regimeClr, 7, "Segoe UI Bold");

   // Baris Rapor Pola Teruji (AI Pattern Matrix)
   string pmStr = InpUsePatternMatrix ? ("Terbaik: " + g_bestPatternStr) : "NONAKTIF";
   CreateOrUpdateText("VIKAR_HUD_PATMAT", panelX + 12, currY + 151, "[Rapor Pola]: " + pmStr, C'203,213,225', 7, "Segoe UI");
   currY += 170;"""

if "VIKAR_HUD_REGIME" not in content:
    content = content.replace(old_hud_mt5, new_hud_mt5)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Step 1 & 2 for MT5 done!")
