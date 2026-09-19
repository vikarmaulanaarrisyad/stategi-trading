import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Make sure line endings are standardized or matched
# BUY section insertion
buy_target = """         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;"""

buy_replacement = """         // 2.5 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
         bool isBullishSweepTrap = false;
         if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
         {
            double candleRange = High[1] - Low[1];
            if (candleRange > 0 && lastSwingLow.price > 0 && Low[1] < lastSwingLow.price && Close[1] > lastSwingLow.price)
            {
               double sweepDistPips = PriceToPips(lastSwingLow.price - Low[1]);
               double lowerWick     = MathMin(Open[1], Close[1]) - Low[1];
               double lowerWickPct  = (lowerWick / candleRange) * 100.0;
               if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && lowerWickPct >= InpMinRejectionWickPct)
               {
                  isBullishSweepTrap = true;
                  g_trapHunterStatusStr = "BULLISH SWEEP TRAP (SSL REVERSAL)";
                  Print("[TRAP HUNTER MT4] Bullish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(lowerWickPct, 0), "%.");
               }
            }
         }

         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;"""

# SELL section insertion
sell_target = """         // 3. Momentum Breakout Detection
         bool isMomentumBreakout = false;"""

sell_replacement = """         // 2.5 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
         bool isBearishSweepTrap = false;
         if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
         {
            double candleRange = High[1] - Low[1];
            if (candleRange > 0 && lastSwingHigh.price > 0 && High[1] > lastSwingHigh.price && Close[1] < lastSwingHigh.price)
            {
               double sweepDistPips = PriceToPips(High[1] - lastSwingHigh.price);
               double upperWick     = High[1] - MathMax(Open[1], Close[1]);
               double upperWickPct  = (upperWick / candleRange) * 100.0;
               if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && upperWickPct >= InpMinRejectionWickPct)
               {
                  isBearishSweepTrap = true;
                  g_trapHunterStatusStr = "BEARISH SWEEP TRAP (BSL REVERSAL)";
                  Print("[TRAP HUNTER MT4] Bearish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(upperWickPct, 0), "%.");
               }
            }
         }

         // 3. Momentum Breakout Detection
         bool isMomentumBreakout = false;"""

# Convert CRLF to LF for matching, then we can save cleanly
crlf = "\r\n" in content
normalized = content.replace("\r\n", "\n")

if "bool isBullishSweepTrap = false;" not in normalized:
    if buy_target in normalized:
        normalized = normalized.replace(buy_target, buy_replacement, 1)
        print("Inserted isBullishSweepTrap successfully!")
    else:
        print("ERROR: buy_target not found!")

if "bool isBearishSweepTrap = false;" not in normalized:
    if sell_target in normalized:
        normalized = normalized.replace(sell_target, sell_replacement, 1)
        print("Inserted isBearishSweepTrap successfully!")
    else:
        print("ERROR: sell_target not found!")

# SELL execution condition
old_can_sell = """         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                               (isMomentumBreakout && isHeadroomOk);"""

new_can_sell = """         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                               (isMomentumBreakout && isHeadroomOk) ||
                               (isBearishSweepTrap && isHeadroomOk);"""

if old_can_sell in normalized:
    normalized = normalized.replace(old_can_sell, new_can_sell, 1)
    print("Updated canExecuteSell with isBearishSweepTrap!")

# Update trade comments for Trap Hunter
old_buy_cmt = 'string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));'
new_buy_cmt = 'string tradeCmt = InpTradeComment + (isBullishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))));'
if old_buy_cmt in normalized:
    normalized = normalized.replace(old_buy_cmt, new_buy_cmt, 1)
    print("Updated BUY trade comment for Trap Hunter!")

old_sell_cmt = 'string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));'
new_sell_cmt = 'string tradeCmt = InpTradeComment + (isBearishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))));'
if old_sell_cmt in normalized:
    normalized = normalized.replace(old_sell_cmt, new_sell_cmt, 1)
    print("Updated SELL trade comment for Trap Hunter!")

if crlf:
    final_content = normalized.replace("\n", "\r\n")
else:
    final_content = normalized

with open(target_file, "w", encoding="utf-8") as f:
    f.write(final_content)

print("MT4 code update complete.")
