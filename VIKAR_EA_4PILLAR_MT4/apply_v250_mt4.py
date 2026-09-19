import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
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
    content = content.replace("enum ENUM_HTF_BIAS", regime_enum_code.strip() + "\n\nenum ENUM_HTF_BIAS")

# 2. Add Section 8.5 and 8.6 Inputs
inputs_85_86 = """
//--- 8.5 DYNAMIC PATTERN PERFORMANCE MATRIX (AI LEARNING v2.50) ---
extern string       sec85                  = "=== 8.5 DYNAMIC PATTERN PERFORMANCE MATRIX (AI LEARNING v2.50) ===";
extern bool          InpUsePatternMatrix        = true;             // Aktifkan Memori Rapor & Bobot Kinerja Pola
extern int           InpMinTradesForPatternEval = 3;                // Minimal Transaksi Sebelum Evaluasi Pola
extern double        InpPatternBlacklistWinrate = 40.0;             // Ambang Batas Blacklist Pola (Winrate < 40%)
extern double        InpPatternBoostWinrate     = 70.0;             // Ambang Batas Boost Pola (Winrate > 70%)
extern double        InpPatternBoostScore       = 10.0;             // Bonus Skor Konfluensi untuk Pola Akurat
extern double        InpPatternPenaltyScore     = 15.0;             // Penalti Pengetatan Skor untuk Pola Lemah

//--- 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ---
extern string       sec86                  = "=== 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ===";
extern bool          InpUseRegimeFilter         = true;             // Aktifkan Sensor Cuaca Pasar (Trending vs Choppy)
extern int           InpChoppinessPeriod        = 14;               // Periode Perhitungan Choppiness Index (CI)
extern double        InpChoppyThreshold         = 61.8;             // Ambang Batas Pasar Choppy / Sideways (CI > 61.8)
extern double        InpTrendingThreshold       = 38.2;             // Ambang Batas Pasar Tren Kuat (CI < 38.2)
extern bool          InpBlockBreakoutInChoppy   = true;             // Blokir Momentum Breakout Saat Pasar Choppy
"""
if "InpUsePatternMatrix" not in content:
    content = content.replace(
        'extern bool          InpAutopsyNotifyPush       = true;             // Kirim Laporan Otopsi Pasca-Loss ke Smartphone',
        'extern bool          InpAutopsyNotifyPush       = true;             // Kirim Laporan Otopsi Pasca-Loss ke Smartphone\n' + inputs_85_86.strip()
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
//| FUNGSI MATEMATIS: CHOPPINESS INDEX (CI) DENGAN BASE 10 LOGARITHM|
//+------------------------------------------------------------------+
double CalculateChoppinessIndex(int period)
{
   if (Bars < period + 2) return 50.0;

   double sumTR = 0.0;
   double highMax = High[1];
   double lowMin  = Low[1];

   for (int i = 1; i <= period; i++)
   {
      double h = High[i];
      double l = Low[i];
      double prevClose = Close[i + 1];

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
//| INISIALISASI & PEMULIHAN MEMORI PATTERN PERFORMANCE MATRIX       |
//+------------------------------------------------------------------+
void InitPatternMatrix()
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

      string gvWKey = "VIKAR_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);
      string gvLKey = "VIKAR_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);

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
   Print("[AI PATTERN MATRIX MT4] Diinisialisasi. Pola Aktif: ", TOTAL_TRACKED_PATTERNS, " | Ter-blacklist: ", blacklistedCount, " | Terbaik: ", g_bestPatternStr);
}

//+------------------------------------------------------------------+
//| PEMBARUAN REKOR SETIAP KALI ORDER TERTUTUP (PERSISTEN DI GLOBAL)|
//+------------------------------------------------------------------+
void UpdatePatternRecord(int patternId, bool isWin)
{
   if (patternId < 0 || patternId >= TOTAL_TRACKED_PATTERNS) return;

   string gvWKey = "VIKAR_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);
   string gvLKey = "VIKAR_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);

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
         Print("[AI MATRIX WARNING] Pola '", g_patternMatrix[patternId].name, "' di-BLACKLIST sementara (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% < ", InpPatternBlacklistWinrate, "%).");
      }
      else if (g_patternMatrix[patternId].winRate >= InpPatternBoostWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = InpPatternBoostScore;
         Print("[AI MATRIX BOOST] Pola '", g_patternMatrix[patternId].name, "' mendapatkan BOOST +", InpPatternBoostScore, " Poin (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% >= ", InpPatternBoostWinrate, "%).");
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
if "CalculateChoppinessIndex" not in content:
    content = content.replace("void ResetSelfHealingState(string triggerReason)", matrix_functions.strip() + "\n\nvoid ResetSelfHealingState(string triggerReason)")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Step 1 done: inputs, structs, and math functions added.")
