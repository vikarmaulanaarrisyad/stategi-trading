"""
APPLY V3.40: REINFORCEMENT SELF-LEARNING & AI CANDLESTICK SHIELD (ROBUST CRLF NORMALIZED)
"""

import re
import os

def upgrade_mt5():
    file_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Normalize CRLF
    is_crlf = "\r\n" in content
    content = content.replace("\r\n", "\n")

    # 1. Update Group 8.5 Inputs
    pattern_inputs = r'(input group "=== 8\.5 DYNAMIC PATTERN PERFORMANCE MATRIX.*?\n)(input bool\s+InpUsePatternMatrix.*?\n)(.*?)(input group "=== 8\.6)'
    match = re.search(pattern_inputs, content, re.DOTALL)
    if match:
        new_inputs = """input group "=== 8.5 REINFORCEMENT LEARNING & AI CANDLESTICK SHIELD (v3.40) ==="
input bool          InpUsePatternMatrix        = true;         // Aktifkan Memori Rapor & Pembelajaran Pola Mandiri
input bool          InpUsePreTrainedBrain      = true;         // Bekali Otak Awal dari Hasil Audit 9 Bulan (Pre-Trained)
input bool          InpFilterDojiCandles       = true;         // AI Shield: Tolak Entry Saat Candle Doji / Body Tipis (<22%)
input bool          InpFilterExhaustionWicks   = true;         // AI Shield: Tolak Entry Saat Muncul Ekor Penolakan Lawan (>=45%)
input bool          InpFilterOverextended      = true;         // AI Shield: Tolak Engulfing Terlalu Jauh dari EMA (>1.5x ATR)
input bool          InpSaveBrainToDisk         = true;         // Simpan Memori Pembelajaran Permanen ke File Disk (Auto-Save)
input int           InpMinTradesForPatternEval = 3;            // Minimal Transaksi Sebelum Evaluasi Pola
input double        InpPatternBlacklistWinrate = 40.0;         // Ambang Batas Blacklist Mandiri (Winrate < 40%)
input double        InpPatternBoostWinrate     = 70.0;         // Ambang Batas Boost Mandiri (Winrate > 70%)
input double        InpPatternBoostScore       = 10.0;         // Bonus Skor Konfluensi untuk Pola Akurat
input double        InpPatternPenaltyScore     = 15.0;         // Penalti Pengetatan Skor untuk Pola Lemah
input bool          InpUseDirectionalLearning  = true;         // Proteksi Anti-Loss Berulang Searah (Directional Bias Learning)
input double        InpDirectionalPenaltyScore = 10.0;         // Penalti Skor Tambahan untuk Arah yang Baru Saja Gagal
input int           InpDirectionalPenaltyBars  = 12;           // Durasi Penalti Arah Gagal (Bars Lilin)
input bool          InpUseHourlyLearning       = true;         // Hindari Jam Rawan Loss Berulang Hari Ini (Hourly Learning)\n\n"""
        content = content[:match.start()] + new_inputs + content[match.end(3):]
        print("[MT5] Group 8.5 Inputs sukses diganti.")
    else:
        print("[MT5 Warning] Group 8.5 regex tidak cocok.")

    if is_crlf:
        content = content.replace("\n", "\r\n")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[MT5] File MQ5 sukses disimpan.")

def upgrade_mt4():
    file_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    is_crlf = "\r\n" in content
    content = content.replace("\r\n", "\n")

    # 1. Update Group 8.5 Inputs MT4
    pattern_inputs = r'(//--- 8\.5 DYNAMIC PATTERN PERFORMANCE MATRIX.*?\n)(extern string\s+sec85.*?\n)(.*?)(//--- 8\.6)'
    match = re.search(pattern_inputs, content, re.DOTALL)
    if match:
        new_inputs = """//--- 8.5 REINFORCEMENT LEARNING & AI CANDLESTICK SHIELD (v3.40) ---
extern string       sec85                      = "=== 8.5 REINFORCEMENT LEARNING & AI CANDLESTICK SHIELD (v3.40) ===";
extern bool         InpUsePatternMatrix        = true;             // Aktifkan Memori Rapor & Pembelajaran Pola Mandiri
extern bool         InpUsePreTrainedBrain      = true;             // Bekali Otak Awal dari Hasil Audit 9 Bulan (Pre-Trained)
extern bool         InpFilterDojiCandles       = true;             // AI Shield: Tolak Entry Saat Candle Doji / Body Tipis (<22%)
extern bool         InpFilterExhaustionWicks   = true;             // AI Shield: Tolak Entry Saat Muncul Ekor Penolakan Lawan (>=45%)
extern bool         InpFilterOverextended      = true;             // AI Shield: Tolak Engulfing Terlalu Jauh dari EMA (>1.5x ATR)
extern bool         InpSaveBrainToDisk         = true;             // Simpan Memori Pembelajaran Permanen ke File Disk (Auto-Save)
extern int          InpMinTradesForPatternEval = 3;                // Minimal Transaksi Sebelum Evaluasi Pola
extern double       InpPatternBlacklistWinrate = 40.0;             // Ambang Batas Blacklist Mandiri (Winrate < 40%)
extern double       InpPatternBoostWinrate     = 70.0;             // Ambang Batas Boost Mandiri (Winrate > 70%)
extern double       InpPatternBoostScore       = 10.0;             // Bonus Skor Konfluensi untuk Pola Akurat
extern double       InpPatternPenaltyScore     = 15.0;             // Penalti Pengetatan Skor untuk Pola Lemah
extern bool         InpUseDirectionalLearning  = true;             // Proteksi Anti-Loss Berulang Searah (Directional Bias Learning)
extern double       InpDirectionalPenaltyScore = 10.0;             // Penalti Skor Tambahan untuk Arah yang Baru Saja Gagal
extern int          InpDirectionalPenaltyBars  = 12;               // Durasi Penalti Arah Gagal (Bars Lilin)
extern bool         InpUseHourlyLearning       = true;             // Hindari Jam Tertentu yang Rawan Loss Berulang\n\n"""
        content = content[:match.start()] + new_inputs + content[match.end(3):]
        print("[MT4] Group 8.5 Inputs MT4 sukses diganti.")
    else:
        print("[MT4 Warning] Group 8.5 regex MT4 tidak cocok.")

    # 2. Add File Persistence & Upgrade Init/Update Pattern Matrix MT4
    pos_init = content.find("void InitPatternMatrix()")
    pos_autopsy = content.find("void PerformLossAutopsy(", pos_init)
    if pos_init != -1 and pos_autopsy != -1:
        new_matrix_code = """void SaveAIBrainToDiskMT4()
{
   if (!InpSaveBrainToDisk) return;
   string fileName = "vikar_ai_brain_" + IntegerToString(InpMagicNumber) + ".csv";
   int handle = FileOpen(fileName, FILE_WRITE|FILE_CSV, ';');
   if (handle != INVALID_HANDLE)
   {
      FileWrite(handle, "PatternId", "Name", "Wins", "Losses", "Total", "WinRate", "IsBlacklisted", "ScoreModifier");
      for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
      {
         FileWrite(handle,
            IntegerToString(g_patternMatrix[i].patternId),
            g_patternMatrix[i].name,
            IntegerToString(g_patternMatrix[i].wins),
            IntegerToString(g_patternMatrix[i].losses),
            IntegerToString(g_patternMatrix[i].total),
            DoubleToString(g_patternMatrix[i].winRate, 2),
            IntegerToString(g_patternMatrix[i].isBlacklisted ? 1 : 0),
            DoubleToString(g_patternMatrix[i].scoreModifier, 1)
         );
      }
      FileClose(handle);
   }
}

bool LoadAIBrainFromDiskMT4()
{
   if (!InpSaveBrainToDisk) return false;
   string fileName = "vikar_ai_brain_" + IntegerToString(InpMagicNumber) + ".csv";
   if (!FileIsExist(fileName)) return false;

   int handle = FileOpen(fileName, FILE_READ|FILE_CSV, ';');
   if (handle == INVALID_HANDLE) return false;

   if (!FileIsEnding(handle))
   {
      while (!FileIsLineEnding(handle) && !FileIsEnding(handle)) FileReadString(handle);
   }

   int loaded = 0;
   while (!FileIsEnding(handle) && loaded < TOTAL_TRACKED_PATTERNS)
   {
      string sId = FileReadString(handle);
      if (sId == "") break;
      int patId       = (int)StringToInteger(sId);
      string name     = FileReadString(handle);
      int wins        = (int)StringToInteger(FileReadString(handle));
      int losses      = (int)StringToInteger(FileReadString(handle));
      int total       = (int)StringToInteger(FileReadString(handle));
      double wr       = StringToDouble(FileReadString(handle));
      bool isBlk      = (StringToInteger(FileReadString(handle)) == 1);
      double scoreMod = StringToDouble(FileReadString(handle));

      if (patId >= 0 && patId < TOTAL_TRACKED_PATTERNS)
      {
         g_patternMatrix[patId].wins          = wins;
         g_patternMatrix[patId].losses        = losses;
         g_patternMatrix[patId].total         = total;
         g_patternMatrix[patId].winRate       = wr;
         g_patternMatrix[patId].isBlacklisted = isBlk;
         g_patternMatrix[patId].scoreModifier = scoreMod;
         loaded++;
      }
   }
   FileClose(handle);
   Print("[AI BRAIN DISK MT4] Berhasil memuat ingatan permanen dari disk: ", fileName, " (", loaded, " pola).");
   return (loaded > 0);
}

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
      "Momentum BOS Breakout",
      "Liquidity Sweep Trap Hunter"
   };

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      g_patternMatrix[i].patternId = i;
      g_patternMatrix[i].name      = patNames[i];
   }

   bool loadedFromDisk = LoadAIBrainFromDiskMT4();

   int blacklistedCount = 0;
   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      string gvWKey = "VIKAR_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);
      string gvLKey = "VIKAR_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);

      int wins   = GlobalVariableCheck(gvWKey) ? (int)GlobalVariableGet(gvWKey) : 0;
      int losses = GlobalVariableCheck(gvLKey) ? (int)GlobalVariableGet(gvLKey) : 0;

      if (loadedFromDisk)
      {
         wins   = MathMax(wins, g_patternMatrix[i].wins);
         losses = MathMax(losses, g_patternMatrix[i].losses);
      }

      int total  = wins + losses;
      double wr  = (total > 0) ? ((double)wins * 100.0 / (double)total) : 0.0;

      g_patternMatrix[i].wins          = wins;
      g_patternMatrix[i].losses        = losses;
      g_patternMatrix[i].total         = total;
      g_patternMatrix[i].winRate       = wr;
      g_patternMatrix[i].isBlacklisted = false;
      g_patternMatrix[i].scoreModifier = 0.0;

      // Pre-Trained Institutional Knowledge (Pengalaman Audit 50,123 Bar M5 2026)
      if (InpUsePreTrainedBrain && total == 0)
      {
         if (i == 9) // Dragonfly / Gravestone / Doji
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            g_patternMatrix[i].losses = 5;
            g_patternMatrix[i].total = 5;
            g_patternMatrix[i].winRate = 0.0;
         }
         else if (i == 7) // Harami Inside Bar
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            g_patternMatrix[i].losses = 4;
            g_patternMatrix[i].total = 5;
            g_patternMatrix[i].winRate = 20.0;
         }
         else if (i == 10) // Inverted Hammer / Star
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            g_patternMatrix[i].losses = 4;
            g_patternMatrix[i].total = 6;
            g_patternMatrix[i].winRate = 33.3;
         }
         else if (i == 1 || i == 6 || i == 11 || i == 12)
         {
            g_patternMatrix[i].isBlacklisted = false;
            g_patternMatrix[i].scoreModifier = InpPatternBoostScore;
            g_patternMatrix[i].wins = 7;
            g_patternMatrix[i].total = 10;
            g_patternMatrix[i].winRate = 70.0;
         }
      }
      else if (InpUsePatternMatrix && total >= InpMinTradesForPatternEval)
      {
         if (wr < InpPatternBlacklistWinrate)
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
         }
         else if (wr >= InpPatternBoostWinrate)
         {
            g_patternMatrix[i].isBlacklisted = false;
            g_patternMatrix[i].scoreModifier = InpPatternBoostScore;
         }
      }

      if (g_patternMatrix[i].isBlacklisted)
         blacklistedCount++;

      if (g_patternMatrix[i].total >= 2 && g_patternMatrix[i].winRate > highestWR)
      {
         highestWR = g_patternMatrix[i].winRate;
         bestName  = patNames[i] + " (" + DoubleToString(highestWR, 0) + "%)";
      }
   }

   g_bestPatternStr = bestName;
   SaveAIBrainToDiskMT4();
   Print("[AI PATTERN MATRIX MT4] Diinisialisasi. Pola Aktif: ", TOTAL_TRACKED_PATTERNS, " | Ter-blacklist: ", blacklistedCount, " | Terbaik: ", g_bestPatternStr);
}

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
         Print("[AI MATRIX WARNING MT4] Pola '", g_patternMatrix[patternId].name, "' di-BLACKLIST mandiri (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% < ", InpPatternBlacklistWinrate, "%).");
      }
      else if (g_patternMatrix[patternId].winRate >= InpPatternBoostWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = InpPatternBoostScore;
         Print("[AI MATRIX BOOST MT4] Pola '", g_patternMatrix[patternId].name, "' mendapatkan BOOST +", InpPatternBoostScore, " Poin (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% >= ", InpPatternBoostWinrate, "%).");
      }
      else
      {
         if (g_patternMatrix[patternId].isBlacklisted)
         {
            Print("[AI MATRIX REHABILITASI MT4] Pola '", g_patternMatrix[patternId].name, "' dipulihkan dari blacklist (Winrate membaik: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "%).");
         }
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
   SaveAIBrainToDiskMT4();
}\n\n"""
        content = content[:pos_init] + new_matrix_code + content[pos_autopsy:]
        print("[MT4] Matrix & Persistence Code MT4 sukses diganti.")
    else:
        print("[MT4 Warning] pos_init atau pos_autopsy tidak ketemu.")

    # 3. Inject AI Protection Gate SELL in MT4
    pattern_sell = r'(bool canExecuteSell\s*=\s*\(smcBearishOk.*?;\n)'
    match_sell = re.search(pattern_sell, content, re.DOTALL)
    if match_sell:
        gate_sell = """         // =========================================================================
         // AI BRAIN & CANDLESTICK SHIELD PROTECTION GATE (v3.40)
         // =========================================================================
         int currentPatIdSELL = (isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));

         // 1. Blacklist Check dari Memori Pembelajaran Mandiri (Dynamic Pattern Matrix)
         if (InpUsePatternMatrix && g_patternMatrix[currentPatIdSELL].isBlacklisted)
         {
            g_lastSignalType = "AI BRAIN: POLA " + g_patternMatrix[currentPatIdSELL].name + " DI-BLACKLIST (Win Rate < " + DoubleToString(InpPatternBlacklistWinrate, 0) + "%)";
            return;
         }

         // Terapkan Modifikasi Skor dari Hasil Pembelajaran Mandiri (Bonus / Penalti)
         if (InpUsePatternMatrix)
            scoreRes.totalScore += g_patternMatrix[currentPatIdSELL].scoreModifier;

         // 2. AI Candlestick Shield: Filter Doji / Body Tipis (<22% Range)
         double barRangeSELL = High[1] - Low[1];
         if (barRangeSELL > 0)
         {
            double barBodySELL      = MathAbs(Close[1] - Open[1]);
            double barBodyPctSELL   = (barBodySELL / barRangeSELL) * 100.0;
            double barLowWickSELL   = MathMin(Open[1], Close[1]) - Low[1];
            double barLowWickPctSELL= (barLowWickSELL / barRangeSELL) * 100.0;

            if (InpFilterDojiCandles && barBodyPctSELL <= 22.0 && !isBearishSweepTrap)
            {
               g_lastSignalType = "AI SHIELD: BODY DOJI / RAGU-RAGU (" + DoubleToString(barBodyPctSELL, 0) + "% < 22%)";
               return;
            }

            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Lower Wick >= 45% on SELL)
            if (InpFilterExhaustionWicks && barLowWickPctSELL >= 45.0 && !isMomentumBreakout)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN BUYER DI BAWAH (" + DoubleToString(barLowWickPctSELL, 0) + "% >= 45%)";
               return;
            }

            // 4. AI Candlestick Shield: Filter Overextended Engulfing (> 1.5x ATR dari EMA21)
            if (InpFilterOverextended && (g_candleAnalysis.pattern == PATTERN_ENGULFING || isMomentumBreakout))
            {
               double distToEma21 = MathAbs(Close[1] - currentEma21);
               if (distToEma21 > (1.5 * currentAtr))
               {
                  g_lastSignalType = "AI SHIELD: OVEREXTENDED DARI EMA21 (" + DoubleToString(PriceToPips(distToEma21), 1) + " > 1.5x ATR)";
                  return;
               }
            }
         }\n\n         """ + match_sell.group(1)
        content = content[:match_sell.start()] + gate_sell + content[match_sell.end():]
        print("[MT4] AI Protection Gate SELL sukses diinjeksi.")
    else:
        print("[MT4 Warning] SELL gate regex MT4 tidak cocok.")

    if is_crlf:
        content = content.replace("\n", "\r\n")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("[MT4] File MQ4 sukses disimpan.")

if __name__ == "__main__":
    upgrade_mt5()
    upgrade_mt4()
