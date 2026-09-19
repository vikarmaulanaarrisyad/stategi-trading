import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add InitPatternMatrix() call inside OnInit()
if "InitPatternMatrix();" not in content:
    content = content.replace(
        'Print("Start Time: ", TimeToStr(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Modal: $", DoubleToString(g_eaInitialBalance, 2));',
        'Print("Start Time: ", TimeToStr(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Modal: $", DoubleToString(g_eaInitialBalance, 2));\n   InitPatternMatrix();'
    )

# 2. Hook closed trades in CheckCircuitBreakers to update PatternRecord
old_trade_eval = """      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil modal)
      {
         consecutiveLosses++;
         lastLossTime = todayTrades[k].closeTime;
         if (InpUseSelfHealing && g_autopsy.failedTicket != todayTrades[k].ticket)
            PerformLossAutopsy(todayTrades[k].ticket, todayTrades[k].closeTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingState("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }"""

new_trade_eval = """      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil modal)
      {
         consecutiveLosses++;
         lastLossTime = todayTrades[k].closeTime;
         if (InpUseSelfHealing && g_autopsy.failedTicket != todayTrades[k].ticket)
            PerformLossAutopsy(todayTrades[k].ticket, todayTrades[k].closeTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingState("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }

      // Pembaruan Statistik Pattern Performance Matrix (v2.50)
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
      }"""

if "VIKAR_PMR_PROC_" not in content:
    content = content.replace(old_trade_eval, new_trade_eval)

# 3. Hook Choppiness Index and Pattern Matrix into CheckTradeSignal() for BUY
old_buy_eval = """         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         // Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = Close[1] - Open[1];
            bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (Close[1] > currentEma8 && currentEma8 > currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || Close[1] > lastSwingHigh.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));

            if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
               isMomentumBreakout = true;
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk);"""

new_buy_eval = """         // 1. Evaluasi Cuaca Pasar (Market Regime Classifier CI v2.50)
         g_currentChoppiness = CalculateChoppinessIndex(InpChoppinessPeriod);
         if (g_currentChoppiness > InpChoppyThreshold)
            g_currentRegime = REGIME_CHOPPY_SIDEWAYS;
         else if (g_currentChoppiness < InpTrendingThreshold)
            g_currentRegime = REGIME_STRONG_TREND;
         else
            g_currentRegime = REGIME_NORMAL;

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreBUY += 10.0; // Filter ekstra saat pasar sideways sempit

         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways (Fakeout 85%)
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody = Close[1] - Open[1];
               bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (Close[1] > currentEma8 && currentEma8 > currentEma21);
               bool isBOSBreakout = (!InpBreakoutRequireBOS || Close[1] > lastSwingHigh.price || g_smcAnalysis.hasBOS);
               bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));

               if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
                  isMomentumBreakout = true;
            }
         }

         // 4. Evaluasi Pattern Performance Matrix (AI Pattern Learning v2.50)
         int activePatIdBUY = isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern;
         if (InpUsePatternMatrix)
         {
            if (g_patternMatrix[activePatIdBUY].isBlacklisted)
            {
               g_lastSignalType = "AI MATRIX: POLA " + g_patternMatrix[activePatIdBUY].name + " DI-BLACKLIST (WR: " + DoubleToString(g_patternMatrix[activePatIdBUY].winRate, 1) + "%)";
               return;
            }
            effectiveMinScoreBUY -= g_patternMatrix[activePatIdBUY].scoreModifier; // Kurangi ambang batas jika pola berkinerja tinggi (Boost)
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk);"""

if "CalculateChoppinessIndex(InpChoppinessPeriod)" not in content:
    content = content.replace(old_buy_eval, new_buy_eval)

# 4. Hook Choppiness Index and Pattern Matrix into CheckTradeSignal() for SELL
old_sell_eval = """         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         // Momentum Breakout Detection
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = Open[1] - Close[1];
            bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (Close[1] < currentEma8 && currentEma8 < currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || Close[1] < lastSwingLow.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));

            if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
               isMomentumBreakout = true;
         }

         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                               (isMomentumBreakout && isHeadroomOk);"""

new_sell_eval = """         // 1. Evaluasi Cuaca Pasar (Market Regime Classifier CI v2.50)
         g_currentChoppiness = CalculateChoppinessIndex(InpChoppinessPeriod);
         if (g_currentChoppiness > InpChoppyThreshold)
            g_currentRegime = REGIME_CHOPPY_SIDEWAYS;
         else if (g_currentChoppiness < InpTrendingThreshold)
            g_currentRegime = REGIME_STRONG_TREND;
         else
            g_currentRegime = REGIME_NORMAL;

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreSELL += 10.0; // Filter ekstra saat pasar sideways sempit

         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         // 3. Momentum Breakout Detection
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody = Open[1] - Close[1];
               bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (Close[1] < currentEma8 && currentEma8 < currentEma21);
               bool isBOSBreakout = (!InpBreakoutRequireBOS || Close[1] < lastSwingLow.price || g_smcAnalysis.hasBOS);
               bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));

               if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
                  isMomentumBreakout = true;
            }
         }

         // 4. Evaluasi Pattern Performance Matrix (AI Pattern Learning v2.50)
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

if "int activePatIdSELL = isMomentumBreakout ? 11 :" not in content:
    content = content.replace(old_sell_eval, new_sell_eval)

# 5. Record ticket pattern correctly when BUY / SELL executed
content = content.replace(
    'GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)g_candleAnalysis.pattern);',
    'GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)(isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));'
)

# 6. Update Dashboard HUD height and add Regime and Pattern Matrix rows
content = content.replace(
    'int panelH = InpShowPnLStats ? 515 : 435;',
    'int panelH = InpShowPnLStats ? 555 : 475;'
)

old_hud_tail = """   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");
   currY += 144;"""

new_hud_tail = """   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");

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
    content = content.replace(old_hud_tail, new_hud_tail)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("Step 2 done: logic integration in MT4 complete.")
