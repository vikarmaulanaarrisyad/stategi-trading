# apply_pro_pullback_scalper.py
import sys
import shutil

mq4_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
bak_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4.v420.bak"

shutil.copyfile(mq4_path, bak_path)
print(f"Backup created at: {bak_path}")

with open(mq4_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

replacements = [
    # 1. ENUM_TREND_ALIGNMENT
    (
        '''enum ENUM_HTF_BIAS
{
   HTF_BIAS_NEUTRAL,
   HTF_BIAS_BULLISH,
   HTF_BIAS_BEARISH
};''',
        '''enum ENUM_HTF_BIAS
{
   HTF_BIAS_NEUTRAL,
   HTF_BIAS_BULLISH,
   HTF_BIAS_BEARISH
};

enum ENUM_TREND_ALIGNMENT
{
   TREND_ALIGN_M5_BASELINE,        // 1. M5 EMA 125 Baseline Saja (Standar)
   TREND_ALIGN_TRIPLE_EMA_STACK,   // 2. Triple EMA Stack (8 > 21 > 125 untuk BUY, 8 < 21 < 125 untuk SELL)
   TREND_ALIGN_DUAL_M15_M5,        // 3. Dual Timeframe M15 + M5 Alignment (Rekomendasi Institusional Pro)
   TREND_ALIGN_MACRO_H1_M5         // 4. Macro H1 + M5 Alignment (Swing Trend)
};'''
    ),
    # 2. Section 3.4 Input Parameters
    (
        '''extern double        InpSniperSLBufferPips    = 2.0;                // Buffer SL Di Balik Jarum Sweep (Pips)
extern bool          InpSniperEnterAt50FVG    = true;               // Entry Presisi di 50% FVG (false = Ujung FVG)


//--- 4. PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS) ---''',
        '''extern double        InpSniperSLBufferPips    = 2.0;                // Buffer SL Di Balik Jarum Sweep (Pips)
extern bool          InpSniperEnterAt50FVG    = true;               // Entry Presisi di 50% FVG (false = Ujung FVG)

//--- 3.4 MESIN PRO TREND PULLBACK SCALPER (v4.20 INSTITUSIONAL) ---
extern string             sec34                       = "=== 3.4 PRO TREND PULLBACK SCALPER (v4.20) ===";
extern bool               InpEnableProPullbackScalper = true;                  // Aktifkan Mesin Pro Pullback Scalper Institusional
extern ENUM_TREND_ALIGNMENT InpTrendAlignment         = TREND_ALIGN_DUAL_M15_M5;// Hierarki Trend Dominan (M15+M5 Rekomendasi Pro)
extern bool               InpStrictTrendOnly          = true;                  // Kunci Arah: Wajib 100% Mengikuti Trend (Anti-Melawan Trend)
extern bool               InpBlockCounterTrendCHoCH   = true;                  // Blokir CHoCH Kontra-Trend (Alihkan ke Mode Siaga Pullback)
extern int                InpMinPullbackConfluences   = 2;                     // Minimal Konfluensi (Ribbon, Fibo GP, FVG, POI, Sweep)
extern bool               InpRequireVSAExhaustion     = true;                  // Wajib Konfirmasi Volume Kering (No-Supply / No-Demand)
extern bool               InpFastScalpTP1AtSwing      = true;                  // TP1 Otomatis di Pucuk Swing Terdekat (Amankan Profit Kilat)


//--- 4. PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS) ---'''
    ),
    # 3. Global Struct & Variables for Pro Pullback
    (
        '''SMCSniperTracker      g_sniperBUY;
SMCSniperTracker      g_sniperSELL;''',
        '''SMCSniperTracker      g_sniperBUY;
SMCSniperTracker      g_sniperSELL;

struct ProPullbackResult
{
   bool   isValid;
   int    confluenceCount;
   string confluencesStr;
   double suggestedSL;
   double suggestedTP;
   double pullbackScore;
   bool   isVSAOk;
};

ProPullbackResult    g_proPullbackBUY;
ProPullbackResult    g_proPullbackSELL;
ENUM_HTF_BIAS        g_dominantTrendBias = HTF_BIAS_NEUTRAL;
string               g_dominantTrendStr  = "NEUTRAL (STANDBY)";'''
    ),
    # 4. Implement GetDominantTrendBias() & EvaluateProPullbackSetup()
    (
        '''//+------------------------------------------------------------------+
//| ANALISIS BIAS MAKRO HIGHER TIMEFRAME (H1 MACRO)                  |
//+------------------------------------------------------------------+
ENUM_HTF_BIAS AnalyzeHTFMacroTrend()
{
   if (!InpUseHTFFilter) return HTF_BIAS_NEUTRAL;

   double htfEma125 = iMA(Symbol(), InpHTFTimeframe, InpHTFTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double htfEma8   = iMA(Symbol(), InpHTFTimeframe, InpFastEMA,     0, MODE_EMA, PRICE_CLOSE, 1);
   double htfEma21  = iMA(Symbol(), InpHTFTimeframe, InpMediumEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double htfClose  = iClose(Symbol(), InpHTFTimeframe, 1);

   bool bull = (htfClose > htfEma125);
   bool bear = (htfClose < htfEma125);

   if (InpHTFRequireRibbon)
   {
      bull = bull && (htfEma8 > htfEma21);
      bear = bear && (htfEma8 < htfEma21);
   }

   if (bull)
   {
      g_htfMacroStr = "BULLISH (H1 di atas 125 & Ribbon)";
      return HTF_BIAS_BULLISH;
   }
   else if (bear)
   {
      g_htfMacroStr = "BEARISH (H1 di bawah 125 & Ribbon)";
      return HTF_BIAS_BEARISH;
   }

   g_htfMacroStr = "NEUTRAL / CONFLICT";
   return HTF_BIAS_NEUTRAL;
}''',
        '''//+------------------------------------------------------------------+
//| ANALISIS BIAS MAKRO HIGHER TIMEFRAME (H1 MACRO)                  |
//+------------------------------------------------------------------+
ENUM_HTF_BIAS AnalyzeHTFMacroTrend()
{
   if (!InpUseHTFFilter) return HTF_BIAS_NEUTRAL;

   double htfEma125 = iMA(Symbol(), InpHTFTimeframe, InpHTFTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double htfEma8   = iMA(Symbol(), InpHTFTimeframe, InpFastEMA,     0, MODE_EMA, PRICE_CLOSE, 1);
   double htfEma21  = iMA(Symbol(), InpHTFTimeframe, InpMediumEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double htfClose  = iClose(Symbol(), InpHTFTimeframe, 1);

   bool bull = (htfClose > htfEma125);
   bool bear = (htfClose < htfEma125);

   if (InpHTFRequireRibbon)
   {
      bull = bull && (htfEma8 > htfEma21);
      bear = bear && (htfEma8 < htfEma21);
   }

   if (bull)
   {
      g_htfMacroStr = "BULLISH (H1 di atas 125 & Ribbon)";
      return HTF_BIAS_BULLISH;
   }
   else if (bear)
   {
      g_htfMacroStr = "BEARISH (H1 di bawah 125 & Ribbon)";
      return HTF_BIAS_BEARISH;
   }

   g_htfMacroStr = "NEUTRAL / CONFLICT";
   return HTF_BIAS_NEUTRAL;
}

//+------------------------------------------------------------------+
//| HIERARKI TREN DOMINAN INSTITUSIONAL: ANTI-MELAWAN TREND (v4.20)  |
//+------------------------------------------------------------------+
ENUM_HTF_BIAS GetDominantTrendBias()
{
   // 1. Data EMA M5 Chart Aktif
   double m5Ema8   = iMA(Symbol(), 0, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double m5Ema21  = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double m5Ema125 = iMA(Symbol(), 0, InpTrendEMA,  0, MODE_EMA, PRICE_CLOSE, 1);
   double m5Close  = Close[1];

   bool m5BullBase = (m5Close > m5Ema125);
   bool m5BearBase = (m5Close < m5Ema125);

   // Mode 1: M5 EMA 125 Baseline Saja
   if (InpTrendAlignment == TREND_ALIGN_M5_BASELINE)
   {
      if (m5BullBase) { g_dominantTrendStr = "BULLISH (M5 > EMA 125)"; return HTF_BIAS_BULLISH; }
      if (m5BearBase) { g_dominantTrendStr = "BEARISH (M5 < EMA 125)"; return HTF_BIAS_BEARISH; }
      g_dominantTrendStr = "NEUTRAL (M5)";
      return HTF_BIAS_NEUTRAL;
   }

   // Mode 2: Triple EMA Stack M5 (8 > 21 > 125)
   if (InpTrendAlignment == TREND_ALIGN_TRIPLE_EMA_STACK)
   {
      if (m5Ema8 > m5Ema21 && m5Ema21 > m5Ema125 && m5Close > m5Ema21)
      {
         g_dominantTrendStr = "STRONG BULLISH (Stack 8>21>125)";
         return HTF_BIAS_BULLISH;
      }
      if (m5Ema8 < m5Ema21 && m5Ema21 < m5Ema125 && m5Close < m5Ema21)
      {
         g_dominantTrendStr = "STRONG BEARISH (Stack 8<21<125)";
         return HTF_BIAS_BEARISH;
      }
      g_dominantTrendStr = "NEUTRAL (EMA Transisi)";
      return HTF_BIAS_NEUTRAL;
   }

   // Mode 3: Dual Timeframe M15 + M5 Alignment (Rekomendasi Pro Institusional)
   if (InpTrendAlignment == TREND_ALIGN_DUAL_M15_M5)
   {
      double m15Ema8   = iMA(Symbol(), PERIOD_M15, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
      double m15Ema21  = iMA(Symbol(), PERIOD_M15, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      double m15Ema125 = iMA(Symbol(), PERIOD_M15, InpTrendEMA,  0, MODE_EMA, PRICE_CLOSE, 1);
      double m15Close  = iClose(Symbol(), PERIOD_M15, 1);

      bool m15Bull = (m15Close > m15Ema125 && m15Ema8 > m15Ema21);
      bool m15Bear = (m15Close < m15Ema125 && m15Ema8 < m15Ema21);

      bool m5Bull  = (m5Close > m5Ema125 && (m5Ema8 > m5Ema21 || m5Close > m5Ema21));
      bool m5Bear  = (m5Close < m5Ema125 && (m5Ema8 < m5Ema21 || m5Close < m5Ema21));

      if (m15Bull && m5Bull)
      {
         g_dominantTrendStr = "STRONG BULLISH (M15+M5 Aligned)";
         return HTF_BIAS_BULLISH;
      }
      if (m15Bear && m5Bear)
      {
         g_dominantTrendStr = "STRONG BEARISH (M15+M5 Aligned)";
         return HTF_BIAS_BEARISH;
      }
      g_dominantTrendStr = "NEUTRAL (M15 vs M5 Pullback Phase)";
      return HTF_BIAS_NEUTRAL;
   }

   // Mode 4: Macro H1 + M5 Alignment
   if (InpTrendAlignment == TREND_ALIGN_MACRO_H1_M5)
   {
      double h1Ema8   = iMA(Symbol(), PERIOD_H1, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
      double h1Ema21  = iMA(Symbol(), PERIOD_H1, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      double h1Ema125 = iMA(Symbol(), PERIOD_H1, InpTrendEMA,  0, MODE_EMA, PRICE_CLOSE, 1);
      double h1Close  = iClose(Symbol(), PERIOD_H1, 1);

      bool h1Bull = (h1Close > h1Ema125 && h1Ema8 > h1Ema21);
      bool h1Bear = (h1Close < h1Ema125 && h1Ema8 < h1Ema21);

      if (h1Bull && m5BullBase)
      {
         g_dominantTrendStr = "STRONG BULLISH (H1+M5 Aligned)";
         return HTF_BIAS_BULLISH;
      }
      if (h1Bear && m5BearBase)
      {
         g_dominantTrendStr = "STRONG BEARISH (H1+M5 Aligned)";
         return HTF_BIAS_BEARISH;
      }
      g_dominantTrendStr = "NEUTRAL (H1 vs M5 Transisi)";
      return HTF_BIAS_NEUTRAL;
   }

   return HTF_BIAS_NEUTRAL;
}

//+------------------------------------------------------------------+
//| MESIN EVALUASI PRO TREND PULLBACK SCALPER (v4.20)                |
//+------------------------------------------------------------------+
ProPullbackResult EvaluateProPullbackSetup(bool isBuy, double currentAtr)
{
   ProPullbackResult res;
   res.isValid = false;
   res.confluenceCount = 0;
   res.confluencesStr = "";
   res.suggestedSL = 0.0;
   res.suggestedTP = 0.0;
   res.pullbackScore = 0.0;
   res.isVSAOk = false;

   if (!InpEnableProPullbackScalper) return res;

   double ema8_1  = iMA(Symbol(), 0, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double ema21_1 = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double ribbonLow  = MathMin(ema8_1, ema21_1);
   double ribbonHigh = MathMax(ema8_1, ema21_1);

   // Confluence 1: Menguji Ribbon EMA 8/21
   bool inRibbon = false;
   if (isBuy)
      inRibbon = (Low[1] <= ribbonHigh && High[1] >= ribbonLow && Close[1] >= ribbonLow);
   else
      inRibbon = (High[1] >= ribbonLow && Low[1] <= ribbonHigh && Close[1] <= ribbonHigh);

   if (inRibbon)
   {
      res.confluenceCount++;
      res.confluencesStr += "Ribbon ";
   }

   // Confluence 2: Golden Pocket Fibo 50% - 78.6%
   if (currentFibo.isValid)
   {
      bool inGP = false;
      if (isBuy)
         inGP = (Low[1] <= currentFibo.level500 && High[1] >= currentFibo.level786);
      else
         inGP = (High[1] >= currentFibo.level500 && Low[1] <= currentFibo.level786);

      if (inGP)
      {
         res.confluenceCount++;
         res.confluencesStr += "FiboGP ";
      }
   }

   // Confluence 3: Fair Value Gap (FVG Imbalance)
   if (g_activeFVG.isValid)
   {
      bool inFVG = false;
      if (isBuy && g_activeFVG.isBullish)
         inFVG = (Low[1] <= g_activeFVG.top && High[1] >= g_activeFVG.bottom);
      else if (!isBuy && !g_activeFVG.isBullish)
         inFVG = (High[1] >= g_activeFVG.bottom && Low[1] <= g_activeFVG.top);

      if (inFVG)
      {
         res.confluenceCount++;
         res.confluencesStr += "FVG ";
      }
   }

   // Confluence 4: Institutional POI (Demand / Supply Zone)
   if (InpUsePOIStalker && g_m15Stalker.isValid)
   {
      if (isBuy && g_m15Stalker.isInDemandPOI)
      {
         res.confluenceCount++;
         res.confluencesStr += "POI-Demand ";
      }
      else if (!isBuy && g_m15Stalker.isInSupplyPOI)
      {
         res.confluenceCount++;
         res.confluencesStr += "POI-Supply ";
      }
   }

   // Confluence 5: Liquidity Sweep (Turtle Soup Inducement)
   if (isBuy && g_smcAnalysis.hasSweep && Low[1] <= lastSwingLow.price && Close[1] > lastSwingLow.price)
   {
      res.confluenceCount++;
      res.confluencesStr += "Sweep-SSL ";
   }
   else if (!isBuy && g_smcAnalysis.hasSweep && High[1] >= lastSwingHigh.price && Close[1] < lastSwingHigh.price)
   {
      res.confluenceCount++;
      res.confluencesStr += "Sweep-BSL ";
   }

   // Evaluasi VSA Volume Exhaustion (No-Supply / No-Demand)
   long volNow = iVolume(Symbol(), 0, 1);
   long volImpulse = 0;
   for (int vi = 2; vi <= 6; vi++)
   {
      long v = iVolume(Symbol(), 0, vi);
      if (v > volImpulse) volImpulse = v;
   }
   res.isVSAOk = (!InpRequireVSAExhaustion || (volImpulse > 0 && volNow <= (long)(volImpulse * 0.90)));
   if (res.isVSAOk && InpRequireVSAExhaustion)
   {
      res.confluenceCount++;
      res.confluencesStr += "VSA-Exhaustion ";
   }

   // Evaluasi Rejection Candle Trigger:
   // Untuk BUY: candle ditutup di atas EMA 8 dan memiliki ekor bawah atau badan bullish
   // Untuk SELL: candle ditutup di bawah EMA 8 dan memiliki ekor atas atau badan bearish
   bool triggerOk = false;
   if (isBuy)
      triggerOk = (Close[1] > ema8_1 && (Close[1] > Open[1] || (High[1] - Low[1] > 0 && (MathMin(Open[1], Close[1]) - Low[1]) / (High[1] - Low[1]) >= 0.30)));
   else
      triggerOk = (Close[1] < ema8_1 && (Close[1] < Open[1] || (High[1] - Low[1] > 0 && (High[1] - MathMax(Open[1], Close[1])) / (High[1] - Low[1]) >= 0.30)));

   if (res.confluenceCount >= InpMinPullbackConfluences && triggerOk && res.isVSAOk)
   {
      res.isValid = true;
      res.pullbackScore = CalculatePullbackScore(isBuy, currentAtr);

      // Hitung Target Scalping Cerdas (TP di Swing Terdekat)
      if (isBuy)
      {
         if (InpFastScalpTP1AtSwing && lastSwingHigh.price > Ask + (5 * Point))
            res.suggestedTP = lastSwingHigh.price;
         else
            res.suggestedTP = Ask + (InpRiskRewardRatio * (Ask - (Low[1] - (InpSLBufferAtrMult * currentAtr))));

         res.suggestedSL = Low[1] - (InpSLBufferAtrMult * currentAtr);
      }
      else
      {
         if (InpFastScalpTP1AtSwing && lastSwingLow.price < Bid - (5 * Point) && lastSwingLow.price > 0)
            res.suggestedTP = lastSwingLow.price;
         else
            res.suggestedTP = Bid - (InpRiskRewardRatio * (((High[1] + (InpSLBufferAtrMult * currentAtr)) - Bid)));

         res.suggestedSL = High[1] + (InpSLBufferAtrMult * currentAtr);
      }
   }

   return res;
}'''
    ),
    # 5. OnTick Trend Check and BUY evaluation
    (
        '''   // Filter HTF Makro H1
   ENUM_HTF_BIAS htfBias = AnalyzeHTFMacroTrend();
   bool buyHTFOk  = (!InpUseHTFFilter || htfBias == HTF_BIAS_BULLISH);
   bool sellHTFOk = (!InpUseHTFFilter || htfBias == HTF_BIAS_BEARISH);

   //+---------------------------------------------------------------+
   //| EVALUASI SETUP BUY                                            |
   //+---------------------------------------------------------------+
   bool buyTrendEMA125 = (Close[1] > currentEma125);
   bool buyDoubleAlign = true;
   if (InpUseDailyPivots && InpRequireDoubleAlign)
      buyDoubleAlign = (Close[1] > currentPivot.P);

   if (buyTrendEMA125 && buyDoubleAlign)
   {
      if (!buyHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {''',
        '''   // Evaluasi Tren Dominan Institusional (v4.20 Anti-Melawan Trend)
   g_dominantTrendBias = GetDominantTrendBias();
   ENUM_HTF_BIAS htfBias = AnalyzeHTFMacroTrend();
   bool buyHTFOk  = (!InpUseHTFFilter || htfBias == HTF_BIAS_BULLISH);
   bool sellHTFOk = (!InpUseHTFFilter || htfBias == HTF_BIAS_BEARISH);

   // Evaluasi Keselarasan Tren untuk BUY
   bool isTrendBullish = (g_dominantTrendBias == HTF_BIAS_BULLISH);
   bool isTrendBearish = (g_dominantTrendBias == HTF_BIAS_BEARISH);

   //+---------------------------------------------------------------+
   //| EVALUASI SETUP BUY                                            |
   //+---------------------------------------------------------------+
   bool buyTrendEMA125 = (Close[1] > currentEma125);
   if (InpStrictTrendOnly && isTrendBearish)
   {
      // Tren Makro Bearish: Dilarang keras BUY!
      buyTrendEMA125 = false;
   }
   bool buyDoubleAlign = true;
   if (InpUseDailyPivots && InpRequireDoubleAlign)
      buyDoubleAlign = (Close[1] > currentPivot.P);

   if (buyTrendEMA125 && buyDoubleAlign)
   {
      if (!buyHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {'''
    ),
    # 6. BUY Pro Pullback Scalper integration before canExecuteBuy
    (
        '''         // 2.6 Sequential SMC Sniper Engine (Sweep -> CHoCH -> FVG Retest)
         bool isSMCSniperBUY = false;
         if (InpUseSequentialSMCSniper && g_sniperBUY.stage == SNIPER_STAGE_READY_TO_FIRE)
         {
            isSMCSniperBUY = true;
         }''',
        '''         // 2.6 Sequential SMC Sniper Engine (Sweep -> CHoCH -> FVG Retest)
         bool isSMCSniperBUY = false;
         if (InpUseSequentialSMCSniper && g_sniperBUY.stage == SNIPER_STAGE_READY_TO_FIRE)
         {
            isSMCSniperBUY = true;
         }

         // 2.7 Pro Trend Pullback Scalper Engine (v4.20 Institusional)
         g_proPullbackBUY = EvaluateProPullbackSetup(true, currentAtr);
         bool isProPullbackBUY = (InpEnableProPullbackScalper && g_proPullbackBUY.isValid && (isTrendBullish || !InpStrictTrendOnly));'''
    ),
    # 7. BUY canExecuteBuy condition
    (
        '''         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk) ||
                              (isBullishSweepTrap && isHeadroomOk) ||
                              (isSMCSniperBUY && isHeadroomOk);''',
        '''         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isProPullbackBUY && isHeadroomOk) ||
                              (isMomentumBreakout && isHeadroomOk) ||
                              (isBullishSweepTrap && isHeadroomOk) ||
                              (isSMCSniperBUY && isHeadroomOk);'''
    ),
    # 8. BUY trade comment and TP
    (
        '''            string tradeCmt = InpTradeComment + (isSMCSniperBUY ? "-SNIPER-BUY" : (isBullishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")))));''',
        '''            if (isProPullbackBUY && g_proPullbackBUY.suggestedTP > Ask)
               tpPrice = g_proPullbackBUY.suggestedTP;

            string tradeCmt = InpTradeComment + (isProPullbackBUY ? "-PRO-PB" : (isSMCSniperBUY ? "-SNIPER-BUY" : (isBullishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))))));'''
    ),
    # 9. BUY patStr for notification
    (
        '''               string patStr = isSMCSniperBUY ? "Sequential SMC Sniper (Sweep->CHoCH->FVG)" : (isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName);''',
        '''               string patStr = isProPullbackBUY ? ("Pro Pullback Scalper (" + g_proPullbackBUY.confluencesStr + ")") : (isSMCSniperBUY ? "Sequential SMC Sniper (Sweep->CHoCH->FVG)" : (isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName));'''
    ),
    # 10. SELL setup strict trend check
    (
        '''   //+---------------------------------------------------------------+
   //| EVALUASI SETUP SELL                                           |
   //+---------------------------------------------------------------+
   bool sellTrendEMA125 = (Close[1] < currentEma125);
   bool sellDoubleAlign = true;
   if (InpUseDailyPivots && InpRequireDoubleAlign)
      sellDoubleAlign = (Close[1] < currentPivot.P);

   if (sellTrendEMA125 && sellDoubleAlign)
   {
      if (!sellHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {''',
        '''   //+---------------------------------------------------------------+
   //| EVALUASI SETUP SELL                                           |
   //+---------------------------------------------------------------+
   bool sellTrendEMA125 = (Close[1] < currentEma125);
   if (InpStrictTrendOnly && isTrendBullish)
   {
      // Tren Makro Bullish: Dilarang keras SELL!
      sellTrendEMA125 = false;
   }
   bool sellDoubleAlign = true;
   if (InpUseDailyPivots && InpRequireDoubleAlign)
      sellDoubleAlign = (Close[1] < currentPivot.P);

   if (sellTrendEMA125 && sellDoubleAlign)
   {
      if (!sellHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {'''
    ),
    # 11. SELL Pro Pullback Scalper integration before canExecuteSell
    (
        '''         // 2.6 Sequential SMC Sniper Engine (Sweep -> CHoCH -> FVG Retest)
         bool isSMCSniperSELL = false;
         if (InpUseSequentialSMCSniper && g_sniperSELL.stage == SNIPER_STAGE_READY_TO_FIRE)
         {
            isSMCSniperSELL = true;
         }''',
        '''         // 2.6 Sequential SMC Sniper Engine (Sweep -> CHoCH -> FVG Retest)
         bool isSMCSniperSELL = false;
         if (InpUseSequentialSMCSniper && g_sniperSELL.stage == SNIPER_STAGE_READY_TO_FIRE)
         {
            isSMCSniperSELL = true;
         }

         // 2.7 Pro Trend Pullback Scalper Engine (v4.20 Institusional)
         g_proPullbackSELL = EvaluateProPullbackSetup(false, currentAtr);
         bool isProPullbackSELL = (InpEnableProPullbackScalper && g_proPullbackSELL.isValid && (isTrendBearish || !InpStrictTrendOnly));'''
    ),
    # 12. SELL canExecuteSell condition
    (
        '''         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                               (isMomentumBreakout && isHeadroomOk) ||
                               (isBearishSweepTrap && isHeadroomOk) ||
                               (isSMCSniperSELL && isHeadroomOk);''',
        '''         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                               (isProPullbackSELL && isHeadroomOk) ||
                               (isMomentumBreakout && isHeadroomOk) ||
                               (isBearishSweepTrap && isHeadroomOk) ||
                               (isSMCSniperSELL && isHeadroomOk);'''
    ),
    # 13. SELL trade comment and TP
    (
        '''            string tradeCmt = InpTradeComment + (isSMCSniperSELL ? "-SNIPER-SELL" : (isBearishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")))));''',
        '''            if (isProPullbackSELL && g_proPullbackSELL.suggestedTP < Bid && g_proPullbackSELL.suggestedTP > 0)
               tpPrice = g_proPullbackSELL.suggestedTP;

            string tradeCmt = InpTradeComment + (isProPullbackSELL ? "-PRO-PB" : (isSMCSniperSELL ? "-SNIPER-SELL" : (isBearishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))))));'''
    ),
    # 14. SELL patStr for notification
    (
        '''               string patStr = isSMCSniperSELL ? "Sequential SMC Sniper (Sweep->CHoCH->FVG)" : (isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName);''',
        '''               string patStr = isProPullbackSELL ? ("Pro Pullback Scalper (" + g_proPullbackSELL.confluencesStr + ")") : (isSMCSniperSELL ? "Sequential SMC Sniper (Sweep->CHoCH->FVG)" : (isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName));'''
    ),
    # 15. Dashboard HUD: Trend Dominan line
    (
        '''   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   string htfText = InpUseHTFFilter ? g_htfMacroStr : "FILTER OFF";
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", panelX + 12, currY + 14, "[Macro H1]    : " + htfText, htfClr, 7, "Segoe UI Bold");''',
        '''   color trendClr = (g_dominantTrendBias == HTF_BIAS_BULLISH) ? C'74,222,128' : ((g_dominantTrendBias == HTF_BIAS_BEARISH) ? C'248,113,113' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", panelX + 12, currY + 14, "[Trend Dominan]: " + g_dominantTrendStr, trendClr, 7, "Segoe UI Bold");'''
    )
]

applied_count = 0
for idx, (target, repl) in enumerate(replacements):
    target_crlf = target.replace('\r\n', '\n').replace('\n', '\r\n')
    target_lf = target.replace('\r\n', '\n')
    
    if target in content:
        content = content.replace(target, repl, 1)
        applied_count += 1
        print(f"[{idx+1}/{len(replacements)}] Replaced exact match (original newlines)")
    elif target_crlf in content:
        content = content.replace(target_crlf, repl.replace('\r\n', '\n').replace('\n', '\r\n'), 1)
        applied_count += 1
        print(f"[{idx+1}/{len(replacements)}] Replaced CRLF match")
    elif target_lf in content:
        content = content.replace(target_lf, repl.replace('\r\n', '\n'), 1)
        applied_count += 1
        print(f"[{idx+1}/{len(replacements)}] Replaced LF match")
    else:
        print(f"ERROR: [{idx+1}/{len(replacements)}] Target NOT found!")
        print("First 80 chars of target:", repr(target[:80]))
        sys.exit(1)

with open(mq4_path, 'w', encoding='utf-8', errors='ignore') as f:
    f.write(content)

print(f"\nSUCCESS: All {applied_count}/{len(replacements)} modifications applied successfully to {mq4_path}!")
