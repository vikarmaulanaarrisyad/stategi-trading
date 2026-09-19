import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Shorten description line 18
content = content.replace(
    '#property description "7. Prop Firm Equity Guardian, Structural Trailing & Trap Hunter (v3.00)"',
    '#property description "7. Prop Firm Guardian & Trap Hunter (v3.0)"'
)

# 2. Fix CalculateRiskLot definition
old_calc = """double CalculateRiskLot(double slDistancePrice)
{
   double brokerMinLot  = MarketInfo(Symbol(), MODE_MINLOT);
   double brokerMaxLot  = MarketInfo(Symbol(), MODE_MAXLOT);
   double brokerStepLot = MarketInfo(Symbol(), MODE_LOTSTEP);

   // Safeguard jika broker mengembalikan 0
   if (brokerMinLot <= 0.0) brokerMinLot = 0.01;
   if (brokerMaxLot <= 0.0) brokerMaxLot = 100.0;
   if (brokerStepLot <= 0.0) brokerStepLot = 0.01;

   double finalLot = brokerMinLot;

   if (InpLotType == LOT_TYPE_BROKER_MIN)
   {
      finalLot = brokerMinLot;
   }
   else if (InpLotType == LOT_TYPE_FIXED)
   {
      finalLot = InpFixedLot;
   }
   else if (InpLotType == LOT_TYPE_RISK_PERCENT)
   {
      double balance = AccountBalance();
      double riskMoney = balance * (InpRiskPercent / 100.0);
      double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
      double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);

      if (tickSize > 0 && tickValue > 0 && slDistancePrice > 0)
      {
         double ticksAtRisk = slDistancePrice / tickSize;
         double calculatedLot = riskMoney / (ticksAtRisk * tickValue);
         finalLot = calculatedLot;
      }
      else
      {
         finalLot = brokerMinLot;
      }
   }

   // Bulatkan ke lot step broker
   finalLot = MathFloor((finalLot + 0.0000001) / brokerStepLot) * brokerStepLot;
   finalLot = MathMax(brokerMinLot, MathMin(brokerMaxLot, finalLot));
   return NormalizeDouble(finalLot, 2);
}"""

new_calc = """double CalculateRiskLot(double slDistancePrice, double score = 70.0)
{
   double brokerMinLot  = MarketInfo(Symbol(), MODE_MINLOT);
   double brokerMaxLot  = MarketInfo(Symbol(), MODE_MAXLOT);
   double brokerStepLot = MarketInfo(Symbol(), MODE_LOTSTEP);

   // Safeguard jika broker mengembalikan 0
   if (brokerMinLot <= 0.0) brokerMinLot = 0.01;
   if (brokerMaxLot <= 0.0) brokerMaxLot = 100.0;
   if (brokerStepLot <= 0.0) brokerStepLot = 0.01;

   double finalLot = brokerMinLot;

   if (InpLotType == LOT_TYPE_BROKER_MIN)
   {
      finalLot = brokerMinLot;
   }
   else if (InpLotType == LOT_TYPE_FIXED)
   {
      finalLot = InpFixedLot;
   }
   else if (InpLotType == LOT_TYPE_RISK_PERCENT)
   {
      double balance = AccountBalance();
      double riskMoney = balance * (InpRiskPercent / 100.0);

      // Adaptive Risk Multiplier pasca-loss (Self-Healing Engine v2.40)
      if (InpUseSelfHealing && g_autopsy.isActive && g_autopsy.riskMultiplier < 0.99)
      {
         riskMoney *= g_autopsy.riskMultiplier;
      }

      double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
      double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);

      if (tickSize > 0 && tickValue > 0 && slDistancePrice > 0)
      {
         double ticksAtRisk = slDistancePrice / tickSize;
         double calculatedLot = riskMoney / (ticksAtRisk * tickValue);
         finalLot = calculatedLot;
      }
      else
      {
         finalLot = brokerMinLot;
      }
   }

   // 8.14 Asymmetric Confidence Risk Allocator (Kelly Scaling v3.00)
   if (InpUseAsymmetricLot)
   {
      if (score >= 85.0)
         finalLot *= InpGradeABoostMultiplier;
      else if (score < 75.0)
         finalLot *= InpGradeBPenaltyMultiplier;
   }

   // Bulatkan ke lot step broker
   finalLot = MathFloor((finalLot + 0.0000001) / brokerStepLot) * brokerStepLot;
   finalLot = MathMax(brokerMinLot, MathMin(brokerMaxLot, finalLot));
   return NormalizeDouble(finalLot, 2);
}"""

if old_calc in content:
    content = content.replace(old_calc, new_calc)

# 3. Add isBullishSweepTrap before Momentum Breakout in BUY logic
old_buy_marker = '         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)\n         bool isMomentumBreakout = false;'

new_buy_trap = """         // 2.5 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
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

if old_buy_marker in content and "isBullishSweepTrap" not in content:
    content = content.replace(old_buy_marker, new_buy_trap)

# 4. Add isBearishSweepTrap before Momentum Breakout in SELL logic
old_sell_marker = '      // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)\n      bool isMomentumBreakout = false;'

new_sell_trap = """      // 2.5 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
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

      // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
      bool isMomentumBreakout = false;"""

if old_sell_marker in content and "isBearishSweepTrap" not in content:
    content = content.replace(old_sell_marker, new_sell_trap)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("fix_v300_mt4.py executed successfully!")
