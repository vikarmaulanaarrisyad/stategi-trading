import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update version property and description
content = content.replace('#property version   "2.70"', '#property version   "3.00"')
content = content.replace('v2.70 Apex Edition', 'v3.00 Apex Grandmaster Edition')
content = content.replace(
    '#property description "6. Smart Sideways & Anti-Fakeout Suite (ADX, EMA Slope, VSA, ATR Floor v2.70)"',
    '#property description "6. Smart Sideways & Anti-Fakeout Suite (ADX, EMA Slope, VSA, ATR Floor v2.70)"\n#property description "7. Prop Firm Equity Guardian, Structural Trailing & Trap Hunter (v3.00)"'
)

# 2. Add Section 8.13 - 8.15 Inputs
inputs_v300 = """
//--- 8.13 PROP FIRM EQUITY GUARDIAN & KILL-SWITCH (v3.00) ---
extern string       sec813                 = "=== 8.13 PROP FIRM EQUITY GUARDIAN (v3.00) ===";
extern bool          InpUseEquityGuardian       = true;             // Aktifkan Pengaman Batas Drawdown Harian Ketat
extern double        InpMaxDailyEquityDDPct     = 4.0;              // Batas Maksimal Penurunan Equity Harian (%)
extern bool          InpLockTradingOnDDBreach   = true;             // Kunci Trading Otomatis Hingga Besok Jika Batas Tersentuh

//--- 8.14 ASYMMETRIC CONFIDENCE RISK ALLOCATOR (v3.00) ---
extern string       sec814                 = "=== 8.14 ASYMMETRIC RISK ALLOCATOR (v3.00) ===";
extern bool          InpUseAsymmetricLot        = true;             // Skalakan Lot Berdasarkan Kualitas Konfluensi (Kelly)
extern double        InpGradeABoostMultiplier   = 1.30;             // Pengali Lot untuk Setup Grade A+ (Skor >= 85)
extern double        InpGradeBPenaltyMultiplier = 0.70;             // Pengali Lot untuk Setup Standar (Skor 60-75)

//--- 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ---
extern string       sec815                 = "=== 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ===";
extern bool          InpUseTrapHunter           = true;             // Eksekusi Reversal saat Bandar Menyapu Stop Loss Retail
extern double        InpMinSweepPips            = 4.0;              // Minimal Jarak Penembusan Palsu (Pips)
extern double        InpMaxSweepPips            = 30.0;             // Maksimal Jarak Penembusan Palsu (Pips)
extern double        InpMinRejectionWickPct     = 40.0;             // Minimal Panjang Ekor Penolakan Lilin (%)
"""

if "InpUseEquityGuardian" not in content:
    content = content.replace(
        'extern double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)',
        'extern double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)\n' + inputs_v300.strip()
    )

# 3. Add Globals for v3.00
globals_v300 = """
double g_midnightBalance      = 0.0;
bool   g_equityLockActive     = false;
double g_currentDailyDDPct    = 0.0;
string g_trapHunterStatusStr  = "STANDBY";
"""
if "g_midnightBalance" not in content:
    content = content.replace(
        'string g_sidewaysStatusStr = "NORMAL (TREN SEHAT)";',
        'string g_sidewaysStatusStr = "NORMAL (TREN SEHAT)";\n' + globals_v300.strip()
    )

# 4. Update CalculateRiskLot with score parameter and Asymmetric multiplier
old_calc_risk = """double CalculateRiskLot(double slDistancePrice)
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
      finalLot = InpFixedLotSize;
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

      double tickVal = MarketInfo(Symbol(), MODE_TICKVALUE);
      double tickSize = MarketInfo(Symbol(), MODE_TICKSIZE);
      if (tickSize <= 0.0) tickSize = Point;
      if (tickVal <= 0.0)  tickVal = 1.0;

      double slPoints = slDistancePrice / tickSize;
      if (slPoints > 0 && tickVal > 0)
      {
         finalLot = riskMoney / (slPoints * tickVal);
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

new_calc_risk = """double CalculateRiskLot(double slDistancePrice, double score = 70.0)
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
      finalLot = InpFixedLotSize;
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

      double tickVal = MarketInfo(Symbol(), MODE_TICKVALUE);
      double tickSize = MarketInfo(Symbol(), MODE_TICKSIZE);
      if (tickSize <= 0.0) tickSize = Point;
      if (tickVal <= 0.0)  tickVal = 1.0;

      double slPoints = slDistancePrice / tickSize;
      if (slPoints > 0 && tickVal > 0)
      {
         finalLot = riskMoney / (slPoints * tickVal);
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

if "Asymmetric Confidence Risk Allocator" not in content:
    content = content.replace(old_calc_risk, new_calc_risk)

# 5. Hook Prop Firm Equity Guardian into CheckCircuitBreakers()
guardian_code = """   // 0. Prop Firm Equity Guardian (v3.00)
   if (InpUseEquityGuardian)
   {
      static datetime lastDayReset = 0;
      datetime currentDayStart = iTime(Symbol(), PERIOD_D1, 0);
      if (lastDayReset != currentDayStart)
      {
         g_midnightBalance  = AccountBalance();
         g_equityLockActive = false;
         lastDayReset       = currentDayStart;
      }

      if (g_equityLockActive)
      {
         g_lastSignalType = "PROP FIRM GUARDIAN: TRADING DIKUNCI HARI INI (BATAS DD TERSENTUH)";
         return false;
      }

      if (g_midnightBalance > 0.0)
      {
         double currentDDAmount = g_midnightBalance - AccountEquity();
         double currentDDPct    = (currentDDAmount / g_midnightBalance) * 100.0;
         g_currentDailyDDPct    = currentDDPct;

         if (currentDDPct >= InpMaxDailyEquityDDPct)
         {
            Print("[PROP FIRM EQUITY GUARDIAN MT4] EMERGENCY KILL-SWITCH! Penurunan equity harian mencapai ", DoubleToString(currentDDPct, 2), "% >= ", DoubleToString(InpMaxDailyEquityDDPct, 2), "%. Menutup seluruh posisi & mengunci trading!");
            
            int totalOrders = OrdersTotal();
            for (int p = totalOrders - 1; p >= 0; p--)
            {
               if (OrderSelect(p, SELECT_BY_POS, MODE_TRADES))
               {
                  if (OrderSymbol() == Symbol() && OrderMagicNumber() == InpMagicNumber)
                  {
                     bool cls = OrderClose(OrderTicket(), OrderLots(), (OrderType() == OP_BUY ? Bid : Ask), InpDeviation, clrRed);
                     if (!cls) Print("[ERROR] Gagal emergency close order #", OrderTicket());
                  }
               }
            }

            g_equityLockActive = true;
            g_lastSignalType   = "PROP FIRM GUARDIAN: TRADING DIKUNCI (DD " + DoubleToString(currentDDPct, 1) + "% >= " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%)";
            
            if (InpSendPushNotifications)
               SendPushAlert("PROP FIRM EQUITY GUARDIAN MEMICU HARD KILL-SWITCH!\\nDrawdown Harian: " + DoubleToString(currentDDPct, 1) + "% mencapai batas maksimal. Akun dikunci hingga besok.");
            
            return false;
         }
      }
   }
"""

if "Prop Firm Equity Guardian (v3.00)" not in content:
    content = content.replace(
        "bool CheckCircuitBreakers()\n{",
        "bool CheckCircuitBreakers()\n{\n" + guardian_code
    )

# 6. Enhance Structural Trailing in ManageActiveTrades()
old_struct_trailing = """      // 4. Multi-Stage Structural Trailing Stop untuk RUNNER (Pasca-TP1)
      if (InpUseStructuralTrailing && isRunnerLot)
      {
         if (type == OP_BUY)
         {
            if (lastSwingLow.price > 0 && lastSwingLow.price > open)
            {
               double structSL = NormalizeDouble(lastSwingLow.price - (InpStructuralTrailingAtrBuffer * currentAtr), Digits);
               if (structSL > sl && (current - structSL) >= minStopDist)
               {
                  Print("[STRUCTURAL TRAILING BUY] Geser SL #", ticket, " ke bawah Swing Low: ", structSL);
                  OrderModify(ticket, open, structSL, tp, 0, clrGold);
               }
            }
         }
         else if (type == OP_SELL)
         {
            if (lastSwingHigh.price > 0 && lastSwingHigh.price < open)
            {
               double structSL = NormalizeDouble(lastSwingHigh.price + (InpStructuralTrailingAtrBuffer * currentAtr), Digits);
               if ((structSL < sl || sl == 0) && (structSL - current) >= minStopDist)
               {
                  Print("[STRUCTURAL TRAILING SELL] Geser SL #", ticket, " ke atas Swing High: ", structSL);
                  OrderModify(ticket, open, structSL, tp, 0, clrGold);
               }
            }
         }
      }"""

new_struct_trailing = """      // 4. Multi-Stage Structural Trailing Stop (v3.00: Aktif untuk Runner Maupun Posisi Profit > BE)
      if (InpUseStructuralTrailing && (isRunnerLot || pipsProfit >= InpBreakevenLockPips))
      {
         if (type == OP_BUY)
         {
            if (lastSwingLow.price > 0 && lastSwingLow.price > open)
            {
               double structSL = NormalizeDouble(lastSwingLow.price - (InpStructuralTrailingAtrBuffer * currentAtr), Digits);
               if (structSL > sl && (current - structSL) >= minStopDist)
               {
                  Print("[STRUCTURAL TRAILING BUY v3.0] Geser SL #", ticket, " ke bawah Swing Low HL: ", structSL);
                  bool modRes = OrderModify(ticket, open, structSL, tp, 0, clrGold);
                  if (!modRes) Print("[ERROR] Gagal modif structural trailing BUY: ", GetLastError());
               }
            }
         }
         else if (type == OP_SELL)
         {
            if (lastSwingHigh.price > 0 && lastSwingHigh.price < open)
            {
               double structSL = NormalizeDouble(lastSwingHigh.price + (InpStructuralTrailingAtrBuffer * currentAtr), Digits);
               if ((structSL < sl || sl == 0) && (structSL - current) >= minStopDist)
               {
                  Print("[STRUCTURAL TRAILING SELL v3.0] Geser SL #", ticket, " ke atas Swing High LH: ", structSL);
                  bool modRes = OrderModify(ticket, open, structSL, tp, 0, clrGold);
                  if (!modRes) Print("[ERROR] Gagal modif structural trailing SELL: ", GetLastError());
               }
            }
         }
      }"""

if "Structural Trailing Stop (v3.00" not in content:
    content = content.replace(old_struct_trailing, new_struct_trailing)

# 7. Hook Trap Hunter & Score-based CalculateRiskLot into CheckTradeSignal()
content = content.replace(
    'double lots = CalculateRiskLot(Ask - slPrice);',
    'double lots = CalculateRiskLot(Ask - slPrice, scoreRes.totalScore);'
)
content = content.replace(
    'double lots = CalculateRiskLot(slPrice - Bid);',
    'double lots = CalculateRiskLot(slPrice - Bid, scoreRes.totalScore);'
)

# Trap Hunter detection logic right before buy/sell evaluation
trap_hunter_code = """
   // 0.6 Sensor Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
   bool isBullishSweepTrap = false;
   bool isBearishSweepTrap = false;
   if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
   {
      double candleRange = High[1] - Low[1];
      if (candleRange > 0)
      {
         // Bullish Sweep: Sweep Low lalu tutup di atas level dengan ekor bawah panjang
         if (lastSwingLow.price > 0 && Low[1] < lastSwingLow.price && Close[1] > lastSwingLow.price)
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
         // Bearish Sweep: Sweep High lalu tutup di bawah level dengan ekor atas panjang
         if (lastSwingHigh.price > 0 && High[1] > lastSwingHigh.price && Close[1] < lastSwingHigh.price)
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
   }
"""

if "Turtle Soup Reversal Engine v3.00" not in content:
    content = content.replace(
        '// Sinyal Selesai Dipindai',
        trap_hunter_code.strip() + '\n\n   // Sinyal Selesai Dipindai'
    )

# Hook Trap Hunter into BUY and SELL canExecute conditions
old_buy_exec = 'bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||\n                              (isMomentumBreakout && isHeadroomOk);'
new_buy_exec = 'bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||\n                              (isMomentumBreakout && isHeadroomOk) ||\n                              (isBullishSweepTrap && isHeadroomOk);'
if old_buy_exec in content:
    content = content.replace(old_buy_exec, new_buy_exec)

old_sell_exec = 'bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||\n                            (isMomentumBreakout && isHeadroomOk);'
new_sell_exec = 'bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||\n                            (isMomentumBreakout && isHeadroomOk) ||\n                            (isBearishSweepTrap && isHeadroomOk);'
if old_sell_exec in content:
    content = content.replace(old_sell_exec, new_sell_exec)

# 8. Update HUD height & row in MT4
content = content.replace(
    'int panelH = InpShowPnLStats ? 610 : 530;',
    'int panelH = InpShowPnLStats ? 630 : 550;'
)

old_hud_v300 = """   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope Filter: AKTIF", C'148,163,184', 7, "Segoe UI");
   currY += 198;"""

new_hud_v300 = """   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope: AKTIF", C'148,163,184', 7, "Segoe UI");

   // Baris Prop Firm Guardian & Trap Hunter (v3.00)
   string pfStr = InpUseEquityGuardian ? ("DD: " + DoubleToString(g_currentDailyDDPct, 1) + "% / Max " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%") : "OFF";
   color pfClr = (g_currentDailyDDPct >= InpMaxDailyEquityDDPct * 0.75) ? C'248,113,113' : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_PROPFIRM", panelX + 12, currY + 190, "[Prop Firm Guard]: " + pfStr + " | Trap Hunter: AKTIF", pfClr, 7, "Segoe UI Bold");
   currY += 212;"""

if "VIKAR_HUD_PROPFIRM" not in content:
    content = content.replace(old_hud_v300, new_hud_v300)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("apply_v300_mt4.py finished successfully!")
