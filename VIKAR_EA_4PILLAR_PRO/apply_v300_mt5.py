import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

crlf = "\r\n" in content
normalized = content.replace("\r\n", "\n")

# 1. Version and description
normalized = normalized.replace('#property version   "2.70"', '#property version   "3.00"')
normalized = normalized.replace('v2.70 Apex Edition', 'v3.00 Apex Grandmaster Edition')
old_desc = '#property description "6. Smart Sideways & Anti-Fakeout Suite (ADX, EMA Slope, VSA, ATR Floor v2.70)"'
new_desc = '#property description "6. Smart Sideways & Anti-Fakeout Suite (ADX, EMA Slope, VSA, ATR Floor v2.70)"\n#property description "7. Prop Firm Guardian & Trap Hunter (v3.0)"'
if old_desc in normalized and "Prop Firm Guardian" not in normalized:
    normalized = normalized.replace(old_desc, new_desc, 1)

# 2. Section 2.6 Header
old_sec2_marker = '// --- Multi-Stage Structural Trailing Stop (SMC Swing High/Low Runner) ---'
new_sec2_marker = 'input group "=== 2.6 DYNAMIC STRUCTURAL SWING TRAILING (v3.00) ==="'
if old_sec2_marker in normalized:
    normalized = normalized.replace(old_sec2_marker, new_sec2_marker, 1)

# 3. Section 8.13 - 8.15 Inputs
inputs_v300 = """
input group "=== 8.13 PROP FIRM EQUITY GUARDIAN & KILL-SWITCH (v3.00) ==="
input bool          InpUseEquityGuardian       = true;             // Aktifkan Pengaman Batas Drawdown Harian Ketat
input double        InpMaxDailyEquityDDPct     = 4.0;              // Batas Maksimal Penurunan Equity Harian (%)
input bool          InpLockTradingOnDDBreach   = true;             // Kunci Trading Otomatis Hingga Besok Jika Batas Tersentuh

input group "=== 8.14 ASYMMETRIC CONFIDENCE RISK ALLOCATOR (v3.00) ==="
input bool          InpUseAsymmetricLot        = true;             // Skalakan Lot Berdasarkan Kualitas Konfluensi (Kelly)
input double        InpGradeABoostMultiplier   = 1.30;             // Pengali Lot untuk Setup Grade A+ (Skor >= 85)
input double        InpGradeBPenaltyMultiplier = 0.70;             // Pengali Lot untuk Setup Standar (Skor 60-75)

input group "=== 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ==="
input bool          InpUseTrapHunter           = true;             // Eksekusi Reversal saat Bandar Menyapu Stop Loss Retail
input double        InpMinSweepPips            = 4.0;              // Minimal Jarak Penembusan Palsu (Pips)
input double        InpMaxSweepPips            = 30.0;             // Maksimal Jarak Penembusan Palsu (Pips)
input double        InpMinRejectionWickPct     = 40.0;             // Minimal Panjang Ekor Penolakan Lilin (%)
"""

old_atr_floor = 'input double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)'
if old_atr_floor in normalized and "InpUseEquityGuardian" not in normalized:
    normalized = normalized.replace(old_atr_floor, old_atr_floor + "\n" + inputs_v300.strip(), 1)

# 4. Globals for v3.00
globals_v300 = """
double g_midnightBalance      = 0.0;
bool   g_equityLockActive     = false;
double g_currentDailyDDPct    = 0.0;
string g_trapHunterStatusStr  = "STANDBY";
"""
if "g_midnightBalance" not in normalized:
    old_glob = 'int    h_adx14             = INVALID_HANDLE;'
    normalized = normalized.replace(old_glob, old_glob + "\n" + globals_v300.strip(), 1)

# 5. CalculateRiskLot upgrade
old_calc_lot = """double CalculateRiskLot(double slDistancePrice)
{
   double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if (brokerMinLot <= 0) brokerMinLot = 0.10;

   // Mode 1: Otomatis Menyesuaikan Minimal Lot Broker (Aman, Konservatif & Anti-Lot Besar)
   if (InpLotType == LOT_TYPE_BROKER_MIN)
      return NormalizeLots(brokerMinLot);

   // Mode 2: Fixed Lot (Ukuran Statis)
   if (InpLotType == LOT_TYPE_FIXED)
      return NormalizeLots(InpFixedLot);

   // Mode 3: Dynamic Risk Percent (% Saldo Modal)
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   if (balance <= 0) return NormalizeLots(brokerMinLot);

   double riskAmount = balance * (InpRiskPercent / 100.0);
   double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

   if (tickValue <= 0 || tickSize <= 0 || slDistancePrice <= 0)
      return NormalizeLots(brokerMinLot);

   double lossPerLot = (slDistancePrice / tickSize) * tickValue;
   if (lossPerLot <= 0) return NormalizeLots(brokerMinLot);

   double calcLot = riskAmount / lossPerLot;
   return NormalizeLots(calcLot);
}"""

new_calc_lot = """double CalculateRiskLot(double slDistancePrice, double score = 70.0)
{
   double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if (brokerMinLot <= 0) brokerMinLot = 0.10;

   double finalLot = brokerMinLot;

   // Mode 1: Otomatis Menyesuaikan Minimal Lot Broker (Aman, Konservatif & Anti-Lot Besar)
   if (InpLotType == LOT_TYPE_BROKER_MIN)
   {
      finalLot = brokerMinLot;
   }
   // Mode 2: Fixed Lot (Ukuran Statis)
   else if (InpLotType == LOT_TYPE_FIXED)
   {
      finalLot = InpFixedLot;
   }
   // Mode 3: Dynamic Risk Percent (% Saldo Modal)
   else if (InpLotType == LOT_TYPE_RISK_PERCENT)
   {
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      if (balance <= 0) return NormalizeLots(brokerMinLot);

      double riskAmount = balance * (InpRiskPercent / 100.0);

      // Adaptive Risk Multiplier pasca-loss (Self-Healing Engine v2.40)
      if (InpUseSelfHealing && g_autopsy.isActive && g_autopsy.riskMultiplier < 0.99)
      {
         riskAmount *= g_autopsy.riskMultiplier;
      }

      double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

      if (tickValue <= 0 || tickSize <= 0 || slDistancePrice <= 0)
         return NormalizeLots(brokerMinLot);

      double lossPerLot = (slDistancePrice / tickSize) * tickValue;
      if (lossPerLot <= 0) return NormalizeLots(brokerMinLot);

      finalLot = riskAmount / lossPerLot;
   }

   // 8.14 Asymmetric Confidence Risk Allocator (Kelly Scaling v3.00)
   if (InpUseAsymmetricLot)
   {
      if (score >= 85.0)
         finalLot *= InpGradeABoostMultiplier;
      else if (score < 75.0)
         finalLot *= InpGradeBPenaltyMultiplier;
   }

   return NormalizeLots(finalLot);
}"""

if old_calc_lot in normalized:
    normalized = normalized.replace(old_calc_lot, new_calc_lot, 1)

# 6. CloseAllOpenOrders helper & CheckCircuitBreakers updates
close_all_fn = """//+------------------------------------------------------------------+
//| EMERGENCY CLOSE ALL OPEN POSITIONS (PROP FIRM GUARDIAN v3.00)    |
//+------------------------------------------------------------------+
void CloseAllOpenOrders()
{
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (!posInfo.SelectByIndex(i)) continue;
      if (posInfo.Symbol() != _Symbol) continue;
      if (posInfo.Magic() != InpMagicNumber) continue;

      ulong ticket = posInfo.Ticket();
      if (trade.PositionClose(ticket, InpDeviation))
      {
         Print("[PROP FIRM GUARDIAN MQL5] Emergency Close posisi #", ticket, " berhasil dieksekusi.");
      }
      else
      {
         Print("[PROP FIRM GUARDIAN MQL5] Gagal emergency close posisi #", ticket, ". Error: ", trade.ResultRetcode());
      }
   }
}
"""

if "void CloseAllOpenOrders()" not in normalized:
    cb_target = "//+------------------------------------------------------------------+\n//| CHECK CIRCUIT BREAKERS (PENGAMAN BERLAPIS & LOSS COOLDOWN)      |\n//+------------------------------------------------------------------+"
    normalized = normalized.replace(cb_target, close_all_fn + "\n" + cb_target, 1)

# Midnight balance & Guardian check in CheckCircuitBreakers
old_cb_end = """      if (todayClosedPnL <= maxAllowedLoss)
      {
         g_dailyLossLimitHit = true;
         g_lastSignalType = "DAILY LOSS LIMIT (-" + DoubleToString(InpMaxDailyLossPercent, 1) + "%): TRADING DIKUNCI HARI INI";
         return false; // Blok entry baru hingga hari berganti!
      }
      else
      {
         g_dailyLossLimitHit = false;
      }
   }

   return true;
}"""

new_cb_end = """      if (todayClosedPnL <= maxAllowedLoss)
      {
         g_dailyLossLimitHit = true;
         g_lastSignalType = "DAILY LOSS LIMIT (-" + DoubleToString(InpMaxDailyLossPercent, 1) + "%): TRADING DIKUNCI HARI INI";
         return false; // Blok entry baru hingga hari berganti!
      }
      else
      {
         g_dailyLossLimitHit = false;
      }
   }

   // 3. Update Midnight Balance saat hari server berganti
   static int lastDayOfYear = -1;
   MqlDateTime dtCur;
   TimeToStruct(TimeCurrent(), dtCur);
   if (dtCur.day_of_year != lastDayOfYear)
   {
      lastDayOfYear = dtCur.day_of_year;
      g_midnightBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      g_equityLockActive = false;
      Print("[PROP FIRM GUARDIAN MQL5] Pergantian hari server terdeteksi. Midnight Balance direset ke: $", DoubleToString(g_midnightBalance, 2));
   }

   // 4. Prop Firm Equity Guardian & Hard Drawdown Kill-Switch (v3.00)
   if (InpUseEquityGuardian && g_midnightBalance > 0.0)
   {
      double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      if (currentEquity < g_midnightBalance)
      {
         g_currentDailyDDPct = ((g_midnightBalance - currentEquity) / g_midnightBalance) * 100.0;
         if (g_currentDailyDDPct >= InpMaxDailyEquityDDPct)
         {
            g_circuitBreakerActive = true;
            g_equityLockActive     = true;
            g_circuitBreakerReason = "PROP FIRM GUARDIAN: Daily DD " + DoubleToString(g_currentDailyDDPct, 2) + "% >= " + DoubleToString(InpMaxDailyEquityDDPct, 2) + "%";
            g_lastSignalType       = "PROP FIRM GUARDIAN: DD " + DoubleToString(g_currentDailyDDPct, 1) + "% HIT! TRADING DIKUNCI";
            Print("[PROP FIRM GUARDIAN MQL5] EMERGENCY KILL-SWITCH! Equity DD: ", DoubleToString(g_currentDailyDDPct, 2), "%. Menutup seluruh order aktif & mengunci trading!");
            CloseAllOpenOrders();
            if (InpSendPushNotifications)
            {
               SendPushAlert("EMERGENCY KILL-SWITCH!\nProp Firm Equity Guardian terpicu (DD: " + DoubleToString(g_currentDailyDDPct, 1) + "%). Seluruh order ditutup dan trading dikunci hingga esok hari.");
            }
            return false;
         }
      }
      else
      {
         g_currentDailyDDPct = 0.0;
      }

      if (InpLockTradingOnDDBreach && g_equityLockActive)
      {
         g_lastSignalType = "PROP FIRM GUARDIAN: TRADING DIKUNCI HINGGA 00:00 SERVER";
         return false;
      }
   }

   return true;
}"""

if old_cb_end in normalized:
    normalized = normalized.replace(old_cb_end, new_cb_end, 1)

# 7. Structural Trailing for all profitable trades & runners in ManageActiveTrades
old_trail_struct = """      // 3. Multi-Stage Structural Trailing Stop untuk RUNNER (Pasca-TP1 50% Ditutup)
      string gvRunnerKey = "VIKAR_PARTIAL_" + IntegerToString(ticket);
      bool isRunnerLot = GlobalVariableCheck(gvRunnerKey);

      if (InpUseStructuralTrailing && isRunnerLot)"""

new_trail_struct = """      // 3. Multi-Stage Structural Trailing Stop untuk RUNNER & Posisi Cuan (v3.00)
      string gvRunnerKey = "VIKAR_PARTIAL_" + IntegerToString(ticket);
      bool isRunnerLot = GlobalVariableCheck(gvRunnerKey);
      bool isProfitable = (posType == POSITION_TYPE_BUY) ? (current - open >= PipToPrice(InpBreakevenLockPips)) : (open - current >= PipToPrice(InpBreakevenLockPips));

      if (InpUseStructuralTrailing && (isRunnerLot || isProfitable))"""

if old_trail_struct in normalized:
    normalized = normalized.replace(old_trail_struct, new_trail_struct, 1)

# 8. Liquidity Sweep Trap Hunter in BUY logic
old_buy_expansion = """         // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
         bool isMomentumBreakout = false;"""

new_buy_trap_and_expansion = """         // F.2 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
         bool isBullishSweepTrap = false;
         if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
         {
            double candleRange = rates[1].high - rates[1].low;
            if (candleRange > 0 && lastSwingLow.price > 0 && rates[1].low < lastSwingLow.price && rates[1].close > lastSwingLow.price)
            {
               double sweepDistPips = PriceToPips(lastSwingLow.price - rates[1].low);
               double lowerWick     = MathMin(rates[1].open, rates[1].close) - rates[1].low;
               double lowerWickPct  = (lowerWick / candleRange) * 100.0;
               if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && lowerWickPct >= InpMinRejectionWickPct)
               {
                  isBullishSweepTrap = true;
                  g_trapHunterStatusStr = "BULLISH SWEEP TRAP (SSL REVERSAL)";
                  Print("[TRAP HUNTER MQL5] Bullish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(lowerWickPct, 0), "%.");
               }
            }
         }

         // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
         bool isMomentumBreakout = false;"""

if old_buy_expansion in normalized and "bool isBullishSweepTrap = false;" not in normalized:
    normalized = normalized.replace(old_buy_expansion, new_buy_trap_and_expansion, 1)

# canExecuteBuy update
old_can_buy = """         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk);"""

new_can_buy = """         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk) ||
                              (isBullishSweepTrap && isHeadroomOk);"""

if old_can_buy in normalized:
    normalized = normalized.replace(old_can_buy, new_can_buy, 1)

# BUY lots and tradeCmt and pattern record
old_buy_lot_exec = "double lots = CalculateRiskLot(ask - slPrice);"
new_buy_lot_exec = "double lots = CalculateRiskLot(ask - slPrice, scoreRes.totalScore);"
if old_buy_lot_exec in normalized:
    normalized = normalized.replace(old_buy_lot_exec, new_buy_lot_exec, 1)

old_buy_cmt = 'string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));'
new_buy_cmt = 'string tradeCmt = InpTradeComment + (isBullishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))));'
if old_buy_cmt in normalized:
    normalized = normalized.replace(old_buy_cmt, new_buy_cmt, 1)

old_buy_pat = 'GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)buyTicket), (double)g_candleAnalysis.pattern);'
new_buy_pat = 'GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)buyTicket), (double)(isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)));'
if old_buy_pat in normalized:
    normalized = normalized.replace(old_buy_pat, new_buy_pat, 1)

# 9. Liquidity Sweep Trap Hunter in SELL logic
old_sell_expansion = """      // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Terjun)
      bool isMomentumBreakout = false;"""

new_sell_trap_and_expansion = """      // F.2 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
      bool isBearishSweepTrap = false;
      if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
      {
         double candleRange = rates[1].high - rates[1].low;
         if (candleRange > 0 && lastSwingHigh.price > 0 && rates[1].high > lastSwingHigh.price && rates[1].close < lastSwingHigh.price)
         {
            double sweepDistPips = PriceToPips(rates[1].high - lastSwingHigh.price);
            double upperWick     = rates[1].high - MathMax(rates[1].open, rates[1].close);
            double upperWickPct  = (upperWick / candleRange) * 100.0;
            if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && upperWickPct >= InpMinRejectionWickPct)
            {
               isBearishSweepTrap = true;
               g_trapHunterStatusStr = "BEARISH SWEEP TRAP (BSL REVERSAL)";
               Print("[TRAP HUNTER MQL5] Bearish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(upperWickPct, 0), "%.");
            }
         }
      }

      // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Terjun)
      bool isMomentumBreakout = false;"""

if old_sell_expansion in normalized and "bool isBearishSweepTrap = false;" not in normalized:
    normalized = normalized.replace(old_sell_expansion, new_sell_trap_and_expansion, 1)

# canExecuteSell update
old_can_sell = """      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                            (isMomentumBreakout && isHeadroomOk);"""

new_can_sell = """      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                            (isMomentumBreakout && isHeadroomOk) ||
                            (isBearishSweepTrap && isHeadroomOk);"""

if old_can_sell in normalized:
    normalized = normalized.replace(old_can_sell, new_can_sell, 1)

# SELL lots and tradeCmt and pattern record
old_sell_lot_exec = "double lots = CalculateRiskLot(slPrice - bid);"
new_sell_lot_exec = "double lots = CalculateRiskLot(slPrice - bid, scoreRes.totalScore);"
if old_sell_lot_exec in normalized:
    normalized = normalized.replace(old_sell_lot_exec, new_sell_lot_exec, 1)

# Update SELL trade comment
sell_lines = normalized.splitlines()
for i, line in enumerate(sell_lines):
    if i > 3350 and 'string tradeCmt = InpTradeComment +' in line:
        sell_lines[i] = '         string tradeCmt = InpTradeComment + (isBearishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))));'
        break
normalized = "\n".join(sell_lines)

old_sell_pat = 'GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)sellTicket), (double)g_candleAnalysis.pattern);'
new_sell_pat = 'GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)sellTicket), (double)(isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)));'
if old_sell_pat in normalized:
    normalized = normalized.replace(old_sell_pat, new_sell_pat, 1)

# 10. HUD Dashboard: Prop Firm Guard Row & height
old_hud_sideways = """   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope Filter: AKTIF", C'148,163,184', 7, "Segoe UI");
   currY += 198;"""

new_hud_sideways = """   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope: AKTIF", C'148,163,184', 7, "Segoe UI");

   // Baris Prop Firm Guardian & Trap Hunter (v3.00)
   string pfStr = InpUseEquityGuardian ? ("DD: " + DoubleToString(g_currentDailyDDPct, 1) + "% / Max " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%") : "OFF";
   color pfClr = (g_currentDailyDDPct >= InpMaxDailyEquityDDPct * 0.75) ? C'248,113,113' : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_PROPFIRM", panelX + 12, currY + 190, "[Prop Firm Guard]: " + pfStr + " | Trap Hunter: AKTIF", pfClr, 7, "Segoe UI Bold");
   currY += 212;"""

if old_hud_sideways in normalized:
    normalized = normalized.replace(old_hud_sideways, new_hud_sideways, 1)

# Panel height adjustment
old_panel_h = "int panelH = InpShowPnLStats ? 610 : 530;"
new_panel_h = "int panelH = InpShowPnLStats ? 630 : 550;"
if old_panel_h in normalized:
    normalized = normalized.replace(old_panel_h, new_panel_h, 1)

if crlf:
    final_output = normalized.replace("\n", "\r\n")
else:
    final_output = normalized

with open(target_file, "w", encoding="utf-8") as f:
    f.write(final_output)

print("apply_v300_mt5.py completed successfully!")
