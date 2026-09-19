import os
import re

file_path = "VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add inputs in Section 8
inp_needle = 'extern string       sec83                  = "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ===";\nextern bool          InpUseFridayGuard          = true;             // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend\nextern int           InpFridayCloseHour         = 21;               // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)'

inp_replace = '''extern string       sec83                  = "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ===";
extern bool          InpUseFridayGuard          = true;             // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
extern int           InpFridayCloseHour         = 21;               // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)

//--- 8.4 MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE) ---
extern string       sec84                  = "=== 8.4 MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING) ===";
extern bool          InpUseSelfHealing          = true;             // Aktifkan Mesin Otopsi & Koreksi Diri Pasca-Loss
extern double        InpPenaltyConfluencePts    = 10.0;             // Penalti Ambang Skor Minimal Pasca-SL (+10 Poin)
extern int           InpQuarantinePatternBars   = 15;               // Durasi Karantina Pola Lilin Gagal (Bars)
extern double        InpAdaptiveSLBufferBoost   = 0.3;              // Tambahan Buffer ATR Pasca-Loss (x ATR)
extern int           InpAdaptiveBufferTrades    = 3;                // Jumlah Transaksi dengan Buffer Ekstra Pasca-SL
extern bool          InpAutopsyNotifyPush       = true;             // Kirim Laporan Otopsi Pasca-Loss ke Smartphone'''

if inp_needle in code:
    code = code.replace(inp_needle, inp_replace)
    print("1. Inputs added successfully!")
else:
    print("ERROR: inp_needle not found!")

# 2. Add struct and global state
state_needle = 'bool                 g_dailyLossLimitHit    = false;'
state_replace = '''bool                 g_dailyLossLimitHit    = false;

// Struktur & State Mesin Otopsi & Koreksi Diri Pasca-Loss (v2.40)
struct LossAutopsyReport
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
LossAutopsyReport g_autopsy;'''

if state_needle in code:
    code = code.replace(state_needle, state_replace)
    print("2. State struct added successfully!")
else:
    print("ERROR: state_needle not found!")

# 3. Add PerformLossAutopsy and ResetSelfHealingState functions
func_needle = '//+------------------------------------------------------------------+\n//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|'
func_replace = '''//+------------------------------------------------------------------+
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
      string notif = "OTOPSI PASCA-SL #" + IntegerToString(ticket) + " (" + DoubleToString(lossAmount, 2) + ")\n" +
                     "Diagnosa: " + reason + "\n" +
                     "Koreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      SendPushAlert(notif);
   }
}

void ResetSelfHealingState(string triggerReason)
{
   if (!g_autopsy.isActive) return;
   g_autopsy.isActive              = false;
   g_autopsy.scorePenalty          = 0.0;
   g_autopsy.tradesWithExtraBuffer = 0;
   g_autopsy.quarantineUntilBar    = 0;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   Print("[SELF-HEALING NORMALIZED MT4] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}

//+------------------------------------------------------------------+
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|'''

if func_needle in code:
    code = code.replace(func_needle, func_replace)
    print("3. Functions added successfully!")
else:
    print("ERROR: func_needle not found!")

# 4. Hook into CheckCircuitBreakers
cb_needle = '''   struct HistoryTradeInfo
   {
      datetime closeTime;
      double   profit;
   };

   HistoryTradeInfo todayTrades[];
   int countToday = 0;
   int histTotal = OrdersHistoryTotal();

   for (int i = 0; i < histTotal; i++)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
      if (OrderCloseTime() < todayStart) continue;

      ArrayResize(todayTrades, countToday + 1);
      todayTrades[countToday].closeTime = OrderCloseTime();
      todayTrades[countToday].profit    = OrderProfit() + OrderSwap() + OrderCommission();
      countToday++;
   }'''

cb_replace = '''   struct HistoryTradeInfo
   {
      int      ticket;
      datetime closeTime;
      double   profit;
   };

   HistoryTradeInfo todayTrades[];
   int countToday = 0;
   int histTotal = OrdersHistoryTotal();

   for (int i = 0; i < histTotal; i++)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
      if (OrderCloseTime() < todayStart) continue;

      ArrayResize(todayTrades, countToday + 1);
      todayTrades[countToday].ticket    = OrderTicket();
      todayTrades[countToday].closeTime = OrderCloseTime();
      todayTrades[countToday].profit    = OrderProfit() + OrderSwap() + OrderCommission();
      countToday++;
   }'''

if cb_needle in code:
    code = code.replace(cb_needle, cb_replace)
    print("4. HistoryTradeInfo updated with ticket successfully!")
else:
    print("ERROR: cb_needle not found!")

# 5. Hook PerformLossAutopsy into chronological loop in CheckCircuitBreakers
loop_needle = '''      if (profit < -0.01) // True Loss (Kerugian riil modal)
      {
         consecutiveLosses++;
         lastLossTime = todayTrades[k].closeTime;
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER! TIDAK PERNAH MEMICU COOLDOWN!
      }'''

loop_replace = '''      if (profit < -0.01) // True Loss (Kerugian riil modal)
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
      }'''

if loop_needle in code:
    code = code.replace(loop_needle, loop_replace)
    print("5. PerformLossAutopsy hooked into CheckCircuitBreakers!")
else:
    print("ERROR: loop_needle not found!")

# 6. Hook into CheckTradeSignal (confluence score and pattern quarantine)
sig_needle = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;'''

sig_replace = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }'''

if sig_needle in code:
    code = code.replace(sig_needle, sig_replace)
    print("6. Confluence and quarantine hooked for BUY!")
else:
    print("ERROR: sig_needle not found!")

# Also for SELL
sig_sell_needle = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;'''

sig_sell_replace = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }'''

if sig_sell_needle in code:
    code = code.replace(sig_sell_needle, sig_sell_replace)
    print("7. Confluence and quarantine hooked for SELL!")
else:
    print("ERROR: sig_sell_needle not found!")

# Hook canExecuteBuy and canExecuteSell score checks
buy_exec_needle = 'bool canExecuteBuy  = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||'
buy_exec_replace = 'bool canExecuteBuy  = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||'

if buy_exec_needle in code:
    code = code.replace(buy_exec_needle, buy_exec_replace)
    print("8. canExecuteBuy updated with effectiveMinScoreBUY!")
else:
    print("ERROR: buy_exec_needle not found!")

sell_exec_needle = 'bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||'
sell_exec_replace = 'bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||'

if sell_exec_needle in code:
    code = code.replace(sell_exec_needle, sell_exec_replace)
    print("9. canExecuteSell updated with effectiveMinScoreSELL!")
else:
    print("ERROR: sell_exec_needle not found!")

# Adaptive SL buffer and store pattern GV on OrderSend
buy_send_needle = '''            int ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrBlue);

            if (ticket > 0)'''

buy_send_replace = '''            // Adaptive SL Buffer Expansion pasca-loss
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               slPrice = NormalizeDouble(slPrice - (InpAdaptiveSLBufferBoost * currentAtr), Digits);

            int ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrBlue);

            if (ticket > 0)
            {
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)g_candleAnalysis.pattern);'''

if buy_send_needle in code:
    code = code.replace(buy_send_needle, buy_send_replace, 1)
    print("10. Adaptive SL buffer and GV pattern stored for BUY!")
else:
    print("ERROR: buy_send_needle not found!")

sell_send_needle = '''            int ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrRed);

            if (ticket > 0)'''

sell_send_replace = '''            // Adaptive SL Buffer Expansion pasca-loss
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               slPrice = NormalizeDouble(slPrice + (InpAdaptiveSLBufferBoost * currentAtr), Digits);

            int ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrRed);

            if (ticket > 0)
            {
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString(ticket), (double)g_candleAnalysis.pattern);'''

if sell_send_needle in code:
    code = code.replace(sell_send_needle, sell_send_replace, 1)
    print("11. Adaptive SL buffer and GV pattern stored for SELL!")
else:
    print("ERROR: sell_send_needle not found!")

# 12. Dashboard HUD status
hud_needle = 'CreateOrUpdateText("VIKAR_HUD_CB", panelX + 12, currY + 112, "[Circuit Guard]: " + cbDisplay, cbClr, 7, "Segoe UI Bold");\n   currY += 130;'
hud_replace = '''CreateOrUpdateText("VIKAR_HUD_CB", panelX + 12, currY + 112, "[Circuit Guard]: " + cbDisplay, cbClr, 7, "Segoe UI Bold");

   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Skor | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");
   currY += 144;'''

if hud_needle in code:
    code = code.replace(hud_needle, hud_replace)
    print("12. Dashboard HUD updated with Self-Healing display!")
else:
    print("ERROR: hud_needle not found!")

# Adjust panel height slightly
code = code.replace('int            g_panelH           = 475;', 'int            g_panelH           = 490;')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Saved updated file!")
