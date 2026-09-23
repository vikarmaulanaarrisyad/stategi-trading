# apply_ea_repairs.py
import sys
import shutil

mq4_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
bak_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4.v410.bak"

shutil.copyfile(mq4_path, bak_path)
print(f"Backup created at: {bak_path}")

with open(mq4_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

replacements = [
    # 1. Inputs: InpSLBufferAtrMult & InpMinSLPips
    (
        '''extern double        InpSLBufferAtrMult    = 1.0;                   // Buffer Pengaman SL (x Nilai ATR 14) [v3.71: 1.2→1.0 lebih tight]
extern double        InpMinSLPips          = 15.0;                  // Batas Minimum Jarak SL (Pips) [v3.71: 20→15]''',
        '''extern double        InpSLBufferAtrMult    = 1.2;                   // Buffer Pengaman SL (x Nilai ATR 14) [v4.20: 1.2x ATR aman]
extern double        InpMinSLPips          = 20.0;                  // Batas Minimum Jarak SL (Pips) [v4.20: 20 pips aman]'''
    ),
    # 2. Input: InpAllowMomentumBreakout = false
    (
        '''//--- 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ---
extern string       sec32                  = "=== 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ===";
extern bool          InpAllowMomentumBreakout = true;               // Aktifkan Eksekusi Momentum Breakout (Anti-Ketinggalan Reli)''',
        '''//--- 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ---
extern string       sec32                  = "=== 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ===";
extern bool          InpAllowMomentumBreakout = false;              // Aktifkan Eksekusi Momentum Breakout (Default false: Anti Beli di Pucuk)'''
    ),
    # 3. Input: InpM1UseTightSL = false
    (
        '''extern bool          InpM1UseTightSL        = true;   // Gunakan Stop Loss Presisi di Balik Swing M1''',
        '''extern bool          InpM1UseTightSL        = false;  // Gunakan Stop Loss Presisi di Balik Swing M1 (Default false: Anti Wick-Hunt)'''
    ),
    # 4. Sequential Sniper buffer hardening
    (
        '''   double slBuffer = PipToPrice(InpSniperSLBufferPips);
   if (slBuffer <= 0.0) slBuffer = 2.0 * Point * 10.0;''',
        '''   double slBuffer = PipToPrice(InpSniperSLBufferPips);
   bool isGoldSniper = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
   if (isGoldSniper)
   {
      double goldMinBuf = MathMax(slBuffer, 0.4 * currentAtr);
      if (goldMinBuf < 1.0) goldMinBuf = 1.0; // Minimal $1.00 buffer di balik jarum sweep Gold
      slBuffer = goldMinBuf;
   }
   if (slBuffer <= 0.0) slBuffer = 2.0 * Point * 10.0;'''
    ),
    # 5. BUY rejection candle
    (
        '''         // Candlestick Rejection
         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
            isRejection = (Close[1] >= Open[1]);''',
        '''         // Candlestick Rejection
         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
         {
            double cRangeBUY  = High[1] - Low[1];
            double upWickBUY  = High[1] - MathMax(Open[1], Close[1]);
            double lowWickBUY = MathMin(Open[1], Close[1]) - Low[1];
            // Lilin hijau sehat atau penolakan bawah kuat (bukan doji/upper wick dominan)
            isRejection = (Close[1] > Open[1] && upWickBUY < 0.45 * cRangeBUY) || (cRangeBUY > 0 && (lowWickBUY / cRangeBUY) >= 0.35);
         }'''
    ),
    # 6. BUY Momentum Breakout Detection
    (
        '''         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
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
         }''',
        '''         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways (Fakeout 85%)
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody   = Close[1] - Open[1];
               double candleRange  = High[1] - Low[1];
               double upperWick    = High[1] - MathMax(Open[1], Close[1]);
               double distToEma21  = MathAbs(Close[1] - currentEma21);

               bool isBigBullBody     = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (Close[1] > currentEma8 && currentEma8 > currentEma21);
               bool isBOSBreakout     = (!InpBreakoutRequireBOS || Close[1] > lastSwingHigh.price || g_smcAnalysis.hasBOS);
               bool isVSASupported    = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));
               bool isNotExhausted    = (candleRange > 0 && (upperWick / candleRange) <= 0.35); // Anti Bull Trap ekor atas
               bool isNotOverextended = (distToEma21 <= (1.2 * currentAtr)); // Anti overstretch jauh dari Ribbon

               if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported && isNotExhausted && isNotOverextended)
                  isMomentumBreakout = true;
            }
         }'''
    ),
    # 7. BUY Exhaustion Wick filter (remove !isMomentumBreakout)
    (
        '''            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Upper Wick >= 45% on BUY)
            if (InpFilterExhaustionWicks && barUpWickPctBUY >= 45.0 && !isMomentumBreakout && !isSMCSniperBUY)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN SELLER DI ATAS (" + DoubleToString(barUpWickPctBUY, 0) + "% >= 45%)";
               return;
            }''',
        '''            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Upper Wick >= 40% on BUY)
            if (InpFilterExhaustionWicks && barUpWickPctBUY >= 40.0 && !isSMCSniperBUY)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN SELLER DI ATAS (" + DoubleToString(barUpWickPctBUY, 0) + "% >= 40%)";
               return;
            }'''
    ),
    # 8. BUY SL calculation: safe floor and M1 guard
    (
        '''            // 3. Jika di luar POI, terapkan Stop Loss Presisi M1 jika valid & lebih ketat
            else if (!isSMCSniperBUY && InpUseMTFM1Engine && InpM1UseTightSL && g_m1Sniper.isValid && g_m1Sniper.bestSLPrice > 0.0 && g_m1Sniper.bestSLPrice < Ask)
            {
               double m1SLDist = Ask - g_m1Sniper.bestSLPrice;
               if (PriceToPips(m1SLDist) >= InpM1MinSLPips && m1SLDist < slDist)
               {
                  slPrice = g_m1Sniper.bestSLPrice;
                  slDist  = Ask - slPrice;
               }
            }

            // 4. Batasi Jarak SL sesuai Batas Minimal & Maksimal
            if (PriceToPips(slDist) < InpMinSLPips) slPrice = Ask - PipToPrice(InpMinSLPips);
            if (PriceToPips(slDist) > InpMaxSLPips) slPrice = Ask - PipToPrice(InpMaxSLPips);
            slDist = Ask - slPrice;''',
        '''            bool isGoldBUY = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
            double safeMinSLBUY = PipToPrice(InpMinSLPips);
            double atrFloorBUY  = (isGoldBUY ? 1.0 : 0.8) * currentAtr;
            if (safeMinSLBUY < atrFloorBUY) safeMinSLBUY = atrFloorBUY;
            if (isGoldBUY && safeMinSLBUY < 5.0) safeMinSLBUY = 5.0; // Minimal $5.00 lantai pengaman XAUUSD

            // 3. Jika di luar POI, terapkan Stop Loss Presisi M1 jika valid, lebih ketat & tetap di atas batas aman
            else if (!isSMCSniperBUY && InpUseMTFM1Engine && InpM1UseTightSL && g_m1Sniper.isValid && g_m1Sniper.bestSLPrice > 0.0 && g_m1Sniper.bestSLPrice < Ask)
            {
               double m1SLDist = Ask - g_m1Sniper.bestSLPrice;
               if (PriceToPips(m1SLDist) >= InpM1MinSLPips && m1SLDist >= safeMinSLBUY && m1SLDist < slDist)
               {
                  slPrice = g_m1Sniper.bestSLPrice;
                  slDist  = Ask - slPrice;
               }
            }

            // 4. Batasi Jarak SL sesuai Batas Minimal Aman & Maksimal
            if (slDist < safeMinSLBUY)
            {
               slPrice = Ask - safeMinSLBUY;
               slDist  = safeMinSLBUY;
            }
            if (PriceToPips(slDist) > InpMaxSLPips)
            {
               slPrice = Ask - PipToPrice(InpMaxSLPips);
               slDist  = Ask - slPrice;
            }'''
    ),
    # 9. SELL rejection candle
    (
        '''         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (!g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
            isRejection = (Close[1] <= Open[1]);''',
        '''         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (!g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
         {
            double cRangeSELL  = High[1] - Low[1];
            double upWickSELL   = High[1] - MathMax(Open[1], Close[1]);
            double lowWickSELL  = MathMin(Open[1], Close[1]) - Low[1];
            // Lilin merah sehat atau penolakan atas kuat (bukan doji/lower wick dominan)
            isRejection = (Close[1] < Open[1] && lowWickSELL < 0.45 * cRangeSELL) || (cRangeSELL > 0 && (upWickSELL / cRangeSELL) >= 0.35);
         }'''
    ),
    # 10. SELL Momentum Breakout Detection
    (
        '''         // 3. Momentum Breakout Detection
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
         }''',
        '''         // 3. Momentum Breakout Detection
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody   = Open[1] - Close[1];
               double candleRange  = High[1] - Low[1];
               double lowerWick    = MathMin(Open[1], Close[1]) - Low[1];
               double distToEma21  = MathAbs(Close[1] - currentEma21);

               bool isBigBearBody     = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (Close[1] < currentEma8 && currentEma8 < currentEma21);
               bool isBOSBreakout     = (!InpBreakoutRequireBOS || Close[1] < lastSwingLow.price || g_smcAnalysis.hasBOS);
               bool isVSASupported    = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));
               bool isNotExhausted    = (candleRange > 0 && (lowerWick / candleRange) <= 0.35); // Anti Bear Trap ekor bawah
               bool isNotOverextended = (distToEma21 <= (1.2 * currentAtr)); // Anti overstretch jauh dari Ribbon

               if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported && isNotExhausted && isNotOverextended)
                  isMomentumBreakout = true;
            }
         }'''
    ),
    # 11. SELL Exhaustion Wick filter (remove !isMomentumBreakout)
    (
        '''            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Lower Wick >= 45% on SELL)
            if (InpFilterExhaustionWicks && barLowWickPctSELL >= 45.0 && !isMomentumBreakout && !isSMCSniperSELL)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN BUYER DI BAWAH (" + DoubleToString(barLowWickPctSELL, 0) + "% >= 45%)";
               return;
            }''',
        '''            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Lower Wick >= 40% on SELL)
            if (InpFilterExhaustionWicks && barLowWickPctSELL >= 40.0 && !isSMCSniperSELL)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN BUYER DI BAWAH (" + DoubleToString(barLowWickPctSELL, 0) + "% >= 40%)";
               return;
            }'''
    ),
    # 12. SELL SL calculation: safe floor and M1 guard
    (
        '''            // 3. Jika di luar POI, terapkan Stop Loss Presisi M1 jika valid & lebih ketat
            else if (!isSMCSniperSELL && InpUseMTFM1Engine && InpM1UseTightSL && g_m1Sniper.isValid && g_m1Sniper.bestSLPrice > 0.0 && g_m1Sniper.bestSLPrice > Bid)
            {
               double m1SLDist = g_m1Sniper.bestSLPrice - Bid;
               if (PriceToPips(m1SLDist) >= InpM1MinSLPips && m1SLDist < slDist)
               {
                  slPrice = g_m1Sniper.bestSLPrice;
                  slDist  = slPrice - Bid;
               }
            }

            // 4. Batasi Jarak SL sesuai Batas Minimal & Maksimal
            if (PriceToPips(slDist) < InpMinSLPips) slPrice = Bid + PipToPrice(InpMinSLPips);
            if (PriceToPips(slDist) > InpMaxSLPips) slPrice = Bid + PipToPrice(InpMaxSLPips);
            slDist = slPrice - Bid;''',
        '''            bool isGoldSELL = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
            double safeMinSLSELL = PipToPrice(InpMinSLPips);
            double atrFloorSELL  = (isGoldSELL ? 1.0 : 0.8) * currentAtr;
            if (safeMinSLSELL < atrFloorSELL) safeMinSLSELL = atrFloorSELL;
            if (isGoldSELL && safeMinSLSELL < 5.0) safeMinSLSELL = 5.0; // Minimal $5.00 lantai pengaman XAUUSD

            // 3. Jika di luar POI, terapkan Stop Loss Presisi M1 jika valid, lebih ketat & tetap di atas batas aman
            else if (!isSMCSniperSELL && InpUseMTFM1Engine && InpM1UseTightSL && g_m1Sniper.isValid && g_m1Sniper.bestSLPrice > 0.0 && g_m1Sniper.bestSLPrice > Bid)
            {
               double m1SLDist = g_m1Sniper.bestSLPrice - Bid;
               if (PriceToPips(m1SLDist) >= InpM1MinSLPips && m1SLDist >= safeMinSLSELL && m1SLDist < slDist)
               {
                  slPrice = g_m1Sniper.bestSLPrice;
                  slDist  = slPrice - Bid;
               }
            }

            // 4. Batasi Jarak SL sesuai Batas Minimal Aman & Maksimal
            if (slDist < safeMinSLSELL)
            {
               slPrice = Bid + safeMinSLSELL;
               slDist  = safeMinSLSELL;
            }
            if (PriceToPips(slDist) > InpMaxSLPips)
            {
               slPrice = Bid + PipToPrice(InpMaxSLPips);
               slDist  = slPrice - Bid;
            }'''
    )
]

applied_count = 0
for idx, (target, repl) in enumerate(replacements):
    target_crlf = target.replace('\r\n', '\n').replace('\n', '\r\n')
    target_lf = target.replace('\r\n', '\n')
    
    if target in content:
        content = content.replace(target, repl, 1)
        applied_count += 1
        print(f"[{idx+1}/12] Replaced exact match (original newlines)")
    elif target_crlf in content:
        content = content.replace(target_crlf, repl.replace('\r\n', '\n').replace('\n', '\r\n'), 1)
        applied_count += 1
        print(f"[{idx+1}/12] Replaced CRLF match")
    elif target_lf in content:
        content = content.replace(target_lf, repl.replace('\r\n', '\n'), 1)
        applied_count += 1
        print(f"[{idx+1}/12] Replaced LF match")
    else:
        print(f"ERROR: [{idx+1}/12] Target NOT found!")
        print("First 80 chars of target:", repr(target[:80]))
        sys.exit(1)

with open(mq4_path, 'w', encoding='utf-8', errors='ignore') as f:
    f.write(content)

print(f"\nSUCCESS: All {applied_count}/12 repairs applied successfully to {mq4_path}!")
