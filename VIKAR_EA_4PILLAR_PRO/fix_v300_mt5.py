import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

crlf = "\r\n" in content
normalized = content.replace("\r\n", "\n")

# 1. Fix property description (ensure concise and <= 4 lines)
old_props = """#property description "6. Smart Sideways & Anti-Fakeout Suite (ADX, EMA Slope, VSA, ATR Floor v2.70)"
#property description "7. Prop Firm Guardian & Trap Hunter (v3.0)\""""

new_props = """#property description "6. Smart Sideways Suite (ADX, EMA Slope, VSA v2.70)"
#property description "7. Prop Firm Guardian & Trap Hunter (v3.00)\""""

if old_props in normalized:
    normalized = normalized.replace(old_props, new_props)

# 2. Fix CalculateRiskLot (remove riskMultiplier which is MT4 specific)
old_calc_chunk = """      // Adaptive Risk Multiplier pasca-loss (Self-Healing Engine v2.40)
      if (InpUseSelfHealing && g_autopsy.isActive && g_autopsy.riskMultiplier < 0.99)
      {
         riskAmount *= g_autopsy.riskMultiplier;
      }"""

if old_calc_chunk in normalized:
    normalized = normalized.replace(old_calc_chunk, "")
    print("Fixed CalculateRiskLot riskMultiplier reference")

# 3. Add void CloseAllOpenOrders() before CheckCircuitBreakers()
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

cb_header = "//+------------------------------------------------------------------+\n//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|"
if "void CloseAllOpenOrders()" not in normalized and cb_header in normalized:
    normalized = normalized.replace(cb_header, close_all_fn + "\n" + cb_header, 1)
    print("Inserted void CloseAllOpenOrders() before CheckCircuitBreakers()")

# 4. Fix CheckCircuitBreakers condition and Prop Firm Guardian block
old_cb_check = "   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit)"
new_cb_check = "   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit && !InpUseEquityGuardian)"
if old_cb_check in normalized:
    normalized = normalized.replace(old_cb_check, new_cb_check, 1)

# Fix the broken multiline string in CheckCircuitBreakers
broken_block = """            g_circuitBreakerActive = true;
            g_equityLockActive     = true;
            g_circuitBreakerReason = "PROP FIRM GUARDIAN: Daily DD " + DoubleToString(g_currentDailyDDPct, 2) + "% >= " + DoubleToString(InpMaxDailyEquityDDPct, 2) + "%";
            g_lastSignalType       = "PROP FIRM GUARDIAN: DD " + DoubleToString(g_currentDailyDDPct, 1) + "% HIT! TRADING DIKUNCI";
            Print("[PROP FIRM GUARDIAN MQL5] EMERGENCY KILL-SWITCH! Equity DD: ", DoubleToString(g_currentDailyDDPct, 2), "%. Menutup seluruh order aktif & mengunci trading!");
            CloseAllOpenOrders();
            if (InpSendPushNotifications)
            {
               SendPushAlert("EMERGENCY KILL-SWITCH!
Prop Firm Equity Guardian terpicu (DD: " + DoubleToString(g_currentDailyDDPct, 1) + "%). Seluruh order ditutup dan trading dikunci hingga esok hari.");
            }"""

fixed_block = """            g_equityLockActive     = true;
            g_lastSignalType       = "PROP FIRM GUARDIAN: DD " + DoubleToString(g_currentDailyDDPct, 1) + "% HIT! TRADING DIKUNCI";
            Print("[PROP FIRM GUARDIAN MQL5] EMERGENCY KILL-SWITCH! Equity DD: ", DoubleToString(g_currentDailyDDPct, 2), "%. Menutup seluruh order aktif & mengunci trading!");
            CloseAllOpenOrders();
            if (InpSendPushNotifications)
            {
               SendPushAlert("EMERGENCY KILL-SWITCH! Prop Firm Equity Guardian terpicu (DD: " + DoubleToString(g_currentDailyDDPct, 1) + "%). Seluruh order ditutup dan trading dikunci.");
            }"""

if broken_block in normalized:
    normalized = normalized.replace(broken_block, fixed_block)
    print("Fixed broken PushAlert string and undeclared circuit breaker variables")

if crlf:
    final_content = normalized.replace("\n", "\r\n")
else:
    final_content = normalized

with open(target_file, "w", encoding="utf-8") as f:
    f.write(final_content)

print("fix_v300_mt5.py executed successfully!")
