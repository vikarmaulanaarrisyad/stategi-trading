import os
import re

file_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(file_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add inputs in Section 8
inp_needle = '''input group "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ==="
input bool          InpUseFridayGuard              = true;         // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
input int           InpFridayCloseHour             = 21;           // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)'''

inp_replace = '''input group "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ==="
input bool          InpUseFridayGuard              = true;         // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
input int           InpFridayCloseHour             = 21;           // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)

input group "=== 8.4 MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE) ==="
input bool          InpUseSelfHealing              = true;         // Aktifkan Mesin Otopsi & Koreksi Diri Pasca-Loss
input double        InpPenaltyConfluencePts        = 10.0;         // Penalti Ambang Skor Minimal Pasca-SL (+10 Poin)
input int           InpQuarantinePatternBars       = 15;           // Durasi Karantina Pola Lilin Gagal (Bars)
input double        InpAdaptiveSLBufferBoost       = 0.3;          // Tambahan Buffer ATR Pasca-Loss (x ATR)
input int           InpAdaptiveBufferTrades        = 3;            // Jumlah Transaksi dengan Buffer Ekstra Pasca-SL
input bool          InpAutopsyNotifyPush           = true;         // Kirim Laporan Otopsi Pasca-Loss ke Smartphone'''

if inp_needle in code:
    code = code.replace(inp_needle, inp_replace)
    print("1. MT5 inputs added successfully!")
else:
    print("ERROR: inp_needle not found in MT5!")

# 2. Add state struct in global variables
state_needle = 'bool                 g_dailyLossLimitHit    = false;'
state_replace = '''bool                 g_dailyLossLimitHit    = false;

// Struktur & State Mesin Otopsi & Koreksi Diri Pasca-Loss (v2.40 Apex)
struct LossAutopsyReport
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
LossAutopsyReport g_autopsy;'''

if state_needle in code:
    code = code.replace(state_needle, state_replace)
    print("2. MT5 state struct added successfully!")
else:
    print("ERROR: state_needle not found in MT5!")

# 3. Add PerformLossAutopsyMQL5 and ResetSelfHealingStateMQL5
func_needle = '//+------------------------------------------------------------------+\n//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|'
func_replace = '''//+------------------------------------------------------------------+
//| MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE v2.40)|
//+------------------------------------------------------------------+
void PerformLossAutopsyMQL5(ulong ticket, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil data pola candlestick dari memori Global Variable
   string patGvKey = "VIKAR_PAT_" + IntegerToString((long)ticket);
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

   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if (pat != PATTERN_NONE)
      g_autopsy.quarantineUntilBar = currentBarTime + (InpQuarantinePatternBars * PeriodSeconds(_Period));
   else
      g_autopsy.quarantineUntilBar = 0;

   // 2. Diagnosa Anatomi Penyebab Loss
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   CopyRates(_Symbol, _Period, 0, 5, rates);

   double atrVal[];
   ArraySetAsSeries(atrVal, true);
   CopyBuffer(atrHandle, 0, 0, 3, atrVal);
   double currentAtr = (ArraySize(atrVal) > 1) ? atrVal[1] : PipToPrice(20.0);

   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   CopyBuffer(ema125Handle, 0, 0, 3, ema125Val);
   double currentEma125 = (ArraySize(ema125Val) > 1) ? ema125Val[1] : 0.0;

   double lastBarRange = (ArraySize(rates) > 1) ? (rates[1].high - rates[1].low) : 0.0;

   string reason = "PENGUJIAN LEVEL GAGAL (LOW CONFLUENCE)";
   if (lastBarRange >= (2.2 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPIKE)";
   else if (g_smcAnalysis.hasCHoCH || (ArraySize(rates) > 1 && currentEma125 > 0 && ((rates[1].close < currentEma125 && rates[1].open > currentEma125) || (rates[1].close > currentEma125 && rates[1].open < currentEma125))))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU WICK)";

   g_autopsy.lossReason = reason;

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT5] Posisi Deal #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
   Print("DIAGNOSA PENYEBAB : ", g_autopsy.lossReason);
   Print("KOREKSI 1 (SKOR)  : Ambang Konfluensi dinaikkan +", DoubleToString(g_autopsy.scorePenalty, 0), " Poin (Hanya Setup Grade A+)");
   if (pat != PATTERN_NONE)
      Print("KOREKSI 2 (POLA)  : Pola ", patName, " dikarantina selama ", InpQuarantinePatternBars, " Bar lilin.");
   Print("KOREKSI 3 (BUFFER): Stop Loss diperlebar +", DoubleToString(InpAdaptiveSLBufferBoost, 2), "x ATR untuk ", InpAdaptiveBufferTrades, " trade berikutnya.");
   Print("==================================================================");

   if (InpAutopsyNotifyPush)
   {
      string notif = "OTOPSI PASCA-SL #" + IntegerToString((long)ticket) + " (" + DoubleToString(lossAmount, 2) + ")\n" +
                     "Diagnosa: " + reason + "\n" +
                     "Koreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
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
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   Print("[SELF-HEALING NORMALIZED MT5] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}

//+------------------------------------------------------------------+
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|'''

if func_needle in code:
    code = code.replace(func_needle, func_replace)
    print("3. MT5 functions added successfully!")
else:
    print("ERROR: func_needle not found in MT5!")

# 4. Hook PerformLossAutopsy into CheckCircuitBreakers
deal_loop_needle = '''      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
      {
         consecutiveLosses++;
         lastLossTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER KERUGIAN! TIDAK PERNAH MEMICU COOLDOWN!
      }'''

deal_loop_replace = '''      // Evaluasi Loss vs Win:
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
      }'''

if deal_loop_needle in code:
    code = code.replace(deal_loop_needle, deal_loop_replace)
    print("4. MT5 CheckCircuitBreakers hooked with Self-Healing!")
else:
    print("ERROR: deal_loop_needle not found in MT5!")

# 5. Hook into CheckTradeSignal BUY
buy_sig_needle = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, rates, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         if (!scoreRes.isPassed)
         {
            g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
         }'''

buy_sig_replace = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, rates, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
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
         }'''

if buy_sig_needle in code:
    code = code.replace(buy_sig_needle, buy_sig_replace)
    print("5. MT5 BUY score and quarantine hooked!")
else:
    print("ERROR: buy_sig_needle not found in MT5!")

# 6. canExecuteBuy replacement
buy_can_needle = 'bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||'
buy_can_replace = 'bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||'

if buy_can_needle in code:
    code = code.replace(buy_can_needle, buy_can_replace)
    print("6. canExecuteBuy updated with effectiveMinScoreBUY!")
else:
    print("ERROR: buy_can_needle not found in MT5!")

# 7. Hook into CheckTradeSignal SELL
sell_sig_needle = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, rates, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         if (!scoreRes.isPassed)
         {
            g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
         }'''

sell_sig_replace = '''         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, rates, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
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
         }'''

if sell_sig_needle in code:
    code = code.replace(sell_sig_needle, sell_sig_replace)
    print("7. MT5 SELL score and quarantine hooked!")
else:
    print("ERROR: sell_sig_needle not found in MT5!")

# 8. canExecuteSell replacement
sell_can_needle = 'bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||'
sell_can_replace = 'bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||'

if sell_can_needle in code:
    code = code.replace(sell_can_needle, sell_can_replace)
    print("8. canExecuteSell updated with effectiveMinScoreSELL!")
else:
    print("ERROR: sell_can_needle not found in MT5!")

# 9. Adaptive SL buffer and store GV pattern in trade.Buy
buy_trade_needle = '''            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
            {
               lastOrderBarTime = iTime(_Symbol, _Period, 0);'''

buy_trade_replace = '''            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            // Adaptive SL Buffer Expansion pasca-loss
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               slPrice = NormalizeDouble(slPrice - (InpAdaptiveSLBufferBoost * currentAtr), _Digits);

            if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
            {
               ulong buyTicket = trade.ResultOrder();
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)buyTicket), (double)g_candleAnalysis.pattern);

               lastOrderBarTime = iTime(_Symbol, _Period, 0);'''

if buy_trade_needle in code:
    code = code.replace(buy_trade_needle, buy_trade_replace, 1)
    print("9. MT5 trade.Buy adaptive SL buffer and pattern stored!")
else:
    print("ERROR: buy_trade_needle not found in MT5!")

# 10. Adaptive SL buffer and store GV pattern in trade.Sell
sell_trade_needle = '''            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
            {
               lastOrderBarTime = iTime(_Symbol, _Period, 0);'''

sell_trade_replace = '''            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            // Adaptive SL Buffer Expansion pasca-loss
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               slPrice = NormalizeDouble(slPrice + (InpAdaptiveSLBufferBoost * currentAtr), _Digits);

            if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
            {
               ulong sellTicket = trade.ResultOrder();
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)sellTicket), (double)g_candleAnalysis.pattern);

               lastOrderBarTime = iTime(_Symbol, _Period, 0);'''

if sell_trade_needle in code:
    code = code.replace(sell_trade_needle, sell_trade_replace, 1)
    print("10. MT5 trade.Sell adaptive SL buffer and pattern stored!")
else:
    print("ERROR: sell_trade_needle not found in MT5!")

# 11. Dashboard HUD status in MT5
hud_needle = 'CreateOrUpdateText("VIKAR_HUD_CB", panelX + 12, currY + 112, "[Circuit Guard]: " + cbDisplay, cbClr, 7, "Segoe UI Bold");\n   currY += 130;'
hud_replace = '''CreateOrUpdateText("VIKAR_HUD_CB", panelX + 12, currY + 112, "[Circuit Guard]: " + cbDisplay, cbClr, 7, "Segoe UI Bold");

   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Pts | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");
   currY += 144;'''

if hud_needle in code:
    code = code.replace(hud_needle, hud_replace)
    print("11. MT5 Dashboard HUD updated with Self-Healing display!")
else:
    print("ERROR: hud_needle not found in MT5!")

# Adjust panel height slightly
code = code.replace('int            g_panelH           = 475;', 'int            g_panelH           = 490;')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Saved updated MT5 file successfully!")
