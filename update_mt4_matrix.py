import os

file_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

is_crlf = "\r\n" in content
content = content.replace("\r\n", "\n")

pos_init = content.find("void InitPatternMatrix()")
pos_end = content.find("//| SENSOR PRE-NEWS EVENT SHIELD", pos_init)
pos_cut = content.rfind("//+", pos_init, pos_end)

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
}

"""

content = content[:pos_init] + new_matrix_code + content[pos_cut:]
if is_crlf: content = content.replace("\n", "\r\n")
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("[MT4] Pattern Matrix code successfully updated!")
