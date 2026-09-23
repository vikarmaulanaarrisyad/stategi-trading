import os
import re

def remove_pending_from_ea():
    mq5_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(mq5_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Remove enum ENUM_ENTRY_EXECUTION_MODE
    enum_pattern = r"enum ENUM_ENTRY_EXECUTION_MODE\s*\{[^}]*\};"
    code = re.sub(enum_pattern, "", code)

    # 2. Remove group 1.1 input parameters
    input_pattern = r'input group "=== 1\.1 MODE EKSEKUSI TRANSAKSI \(MARKET / LIMIT / STOP\) ==="[\s\S]*?(?=input group "=== 2\.)'
    code = re.sub(input_pattern, "", code)

    # 3. Remove g_activeEntryMode global variable
    code = re.sub(r"ENUM_ENTRY_EXECUTION_MODE\s+g_activeEntryMode\s*=[^;]+;", "", code)

    # 4. Remove g_activeEntryMode assignment in OnInit
    code = code.replace("   g_activeEntryMode = InpEntryMode;\n", "")

    # 5. Remove ManagePendingOrders() call in OnTick
    code = code.replace("   ManagePendingOrders();\n", "")

    # 6. Remove pending orders loop in openCount check
    order_count_pattern = r"   for \(int i = OrdersTotal\(\) - 1; i >= 0; i--\)[\s\S]*?   \}"
    # Let's inspect exact block around line 3498:
    old_order_count_block = """   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong oTicket = OrderGetTicket(i);
      if (oTicket > 0 && orderInfo.Select(oTicket))
      {
         if (orderInfo.Symbol() == _Symbol && orderInfo.Magic() == InpMagicNumber)
            openCount++;
      }
   }"""
    if old_order_count_block in code:
        code = code.replace(old_order_count_block, "")
        print("[+] Removed pending order counting loop in OnTick!")
    else:
        print("[!] Warning: exact old_order_count_block not found!")

    # 7. Clean BUY entry execution back to direct market
    # Find block between slPrice adjustment and if (orderSuccess)
    buy_entry_old = """            CancelAllPendingOrders();

            bool orderSuccess = false;
            ulong buyTicket = 0;
            ulong buyDeal = 0;
            double executedPrice = ask;
            string execModeTag = "MARKET";

            if (g_activeEntryMode == ENTRY_MARKET_INSTANT)
            {
               orderSuccess = trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt);
               if (orderSuccess)
               {
                  buyTicket = trade.ResultOrder();
                  buyDeal = trade.ResultDeal();
                  executedPrice = ask;
                  execModeTag = "MARKET";
               }
            }
            else if (g_activeEntryMode == ENTRY_PENDING_LIMIT)
            {
               double limitPrice = NormalizeDouble(ask - PipToPrice(InpLimitPullbackPips), _Digits);
               if ((ask - limitPrice) < minStopDist)
                  limitPrice = NormalizeDouble(ask - minStopDist, _Digits);

               double pendingSL = NormalizeDouble(slPrice, _Digits);
               if ((limitPrice - pendingSL) < minStopDist)
                  pendingSL = NormalizeDouble(limitPrice - minStopDist, _Digits);

               double pendingTP = NormalizeDouble(limitPrice + (InpRiskRewardRatio * (limitPrice - pendingSL)), _Digits);
               if ((pendingTP - limitPrice) < minStopDist)
                  pendingTP = NormalizeDouble(limitPrice + minStopDist, _Digits);

               datetime expTime = (InpPendingExpiryBars > 0) ? (TimeCurrent() + (InpPendingExpiryBars * PeriodSeconds(_Period))) : 0;
               orderSuccess = trade.BuyLimit(lots, limitPrice, _Symbol, pendingSL, pendingTP, (expTime > 0 ? ORDER_TIME_SPECIFIED : ORDER_TIME_GTC), expTime, tradeCmt + "-LMT");
               if (orderSuccess)
               {
                  buyTicket = trade.ResultOrder();
                  executedPrice = limitPrice;
                  slPrice = pendingSL;
                  tpPrice = pendingTP;
                  execModeTag = "BUY LIMIT";
               }
            }
            else if (g_activeEntryMode == ENTRY_PENDING_STOP)
            {
               double stopPrice = NormalizeDouble(rates[1].high + PipToPrice(InpStopBufferPips), _Digits);
               if ((stopPrice - ask) < minStopDist)
                  stopPrice = NormalizeDouble(ask + minStopDist, _Digits);

               double pendingSL = NormalizeDouble(slPrice, _Digits);
               if ((stopPrice - pendingSL) < minStopDist)
                  pendingSL = NormalizeDouble(stopPrice - minStopDist, _Digits);

               double pendingTP = NormalizeDouble(stopPrice + (InpRiskRewardRatio * (stopPrice - pendingSL)), _Digits);
               if ((pendingTP - stopPrice) < minStopDist)
                  pendingTP = NormalizeDouble(stopPrice + minStopDist, _Digits);

               datetime expTime = (InpPendingExpiryBars > 0) ? (TimeCurrent() + (InpPendingExpiryBars * PeriodSeconds(_Period))) : 0;
               orderSuccess = trade.BuyStop(lots, stopPrice, _Symbol, pendingSL, pendingTP, (expTime > 0 ? ORDER_TIME_SPECIFIED : ORDER_TIME_GTC), expTime, tradeCmt + "-STP");
               if (orderSuccess)
               {
                  buyTicket = trade.ResultOrder();
                  executedPrice = stopPrice;
                  slPrice = pendingSL;
                  tpPrice = pendingTP;
                  execModeTag = "BUY STOP";
               }
            }"""

    buy_entry_new = """            bool orderSuccess = trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt);
            ulong buyTicket = 0;
            ulong buyDeal = 0;
            double executedPrice = ask;
            string execModeTag = "MARKET";

            if (orderSuccess)
            {
               buyTicket = trade.ResultOrder();
               buyDeal   = trade.ResultDeal();
               executedPrice = ask;
               execModeTag   = "MARKET";
            }"""

    if buy_entry_old in code:
        code = code.replace(buy_entry_old, buy_entry_new)
        print("[+] Simplified BUY entry to direct market execution!")
    else:
        print("[!] Warning: exact buy_entry_old not found!")

    # 8. Clean SELL entry execution back to direct market
    sell_entry_old = """         CancelAllPendingOrders();

         bool orderSuccess = false;
         ulong sellTicket = 0;
         ulong sellDeal = 0;
         double executedPrice = bid;
         string execModeTag = "MARKET";

         if (g_activeEntryMode == ENTRY_MARKET_INSTANT)
         {
            orderSuccess = trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt);
            if (orderSuccess)
            {
               sellTicket = trade.ResultOrder();
               sellDeal = trade.ResultDeal();
               executedPrice = bid;
               execModeTag = "MARKET";
            }
         }
         else if (g_activeEntryMode == ENTRY_PENDING_LIMIT)
         {
            double limitPrice = NormalizeDouble(bid + PipToPrice(InpLimitPullbackPips), _Digits);
            if ((limitPrice - bid) < minStopDist)
               limitPrice = NormalizeDouble(bid + minStopDist, _Digits);

            double pendingSL = NormalizeDouble(slPrice, _Digits);
            if ((pendingSL - limitPrice) < minStopDist)
               pendingSL = NormalizeDouble(limitPrice + minStopDist, _Digits);

            double pendingTP = NormalizeDouble(limitPrice - (InpRiskRewardRatio * (pendingSL - limitPrice)), _Digits);
            if ((limitPrice - pendingTP) < minStopDist)
               pendingTP = NormalizeDouble(limitPrice - minStopDist, _Digits);

            datetime expTime = (InpPendingExpiryBars > 0) ? (TimeCurrent() + (InpPendingExpiryBars * PeriodSeconds(_Period))) : 0;
            orderSuccess = trade.SellLimit(lots, limitPrice, _Symbol, pendingSL, pendingTP, (expTime > 0 ? ORDER_TIME_SPECIFIED : ORDER_TIME_GTC), expTime, tradeCmt + "-LMT");
            if (orderSuccess)
            {
               sellTicket = trade.ResultOrder();
               executedPrice = limitPrice;
               slPrice = pendingSL;
               tpPrice = pendingTP;
               execModeTag = "SELL LIMIT";
            }
         }
         else if (g_activeEntryMode == ENTRY_PENDING_STOP)
         {
            double stopPrice = NormalizeDouble(rates[1].low - PipToPrice(InpStopBufferPips), _Digits);
            if ((bid - stopPrice) < minStopDist)
               stopPrice = NormalizeDouble(bid - minStopDist, _Digits);

            double pendingSL = NormalizeDouble(slPrice, _Digits);
            if ((pendingSL - stopPrice) < minStopDist)
               pendingSL = NormalizeDouble(stopPrice + minStopDist, _Digits);

            double pendingTP = NormalizeDouble(stopPrice - (InpRiskRewardRatio * (pendingSL - stopPrice)), _Digits);
            if ((stopPrice - pendingTP) < minStopDist)
               pendingTP = NormalizeDouble(stopPrice - minStopDist, _Digits);

            datetime expTime = (InpPendingExpiryBars > 0) ? (TimeCurrent() + (InpPendingExpiryBars * PeriodSeconds(_Period))) : 0;
            orderSuccess = trade.SellStop(lots, stopPrice, _Symbol, pendingSL, pendingTP, (expTime > 0 ? ORDER_TIME_SPECIFIED : ORDER_TIME_GTC), expTime, tradeCmt + "-STP");
            if (orderSuccess)
            {
               sellTicket = trade.ResultOrder();
               executedPrice = stopPrice;
               slPrice = pendingSL;
               tpPrice = pendingTP;
               execModeTag = "SELL STOP";
            }
         }"""

    sell_entry_new = """         bool orderSuccess = trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt);
         ulong sellTicket = 0;
         ulong sellDeal = 0;
         double executedPrice = bid;
         string execModeTag = "MARKET";

         if (orderSuccess)
         {
            sellTicket = trade.ResultOrder();
            sellDeal   = trade.ResultDeal();
            executedPrice = bid;
            execModeTag   = "MARKET";
         }"""

    if sell_entry_old in code:
        code = code.replace(sell_entry_old, sell_entry_new)
        print("[+] Simplified SELL entry to direct market execution!")
    else:
        print("[!] Warning: exact sell_entry_old not found!")

    # 9. Remove ManagePendingOrders, CancelAllPendingOrders, CancelOppositePendingOrders functions
    funcs_old = """//+------------------------------------------------------------------+
//| PENGELOLA SIKLUS HIDUP PENDING ORDER (v3.30)                     |
//+------------------------------------------------------------------+
void ManagePendingOrders()
{
   if (OrdersTotal() == 0)
      return;

   datetime currentTime = TimeCurrent();
   int expirySeconds = InpPendingExpiryBars * PeriodSeconds(_Period);

   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong orderTicket = OrderGetTicket(i);
      if (orderTicket == 0) continue;
      if (!orderInfo.Select(orderTicket)) continue;
      if (orderInfo.Symbol() != _Symbol || orderInfo.Magic() != InpMagicNumber) continue;

      datetime setupTime = (datetime)orderInfo.TimeSetup();
      if (InpPendingExpiryBars > 0 && (currentTime - setupTime) >= expirySeconds)
      {
         Print("[PENDING ORDER EXPIRED] Menghapus order pending #", orderTicket, 
               " karena melewati batas waktu ", InpPendingExpiryBars, " lilin tanpa terjemput.");
         trade.OrderDelete(orderTicket);
      }
   }
}

void CancelAllPendingOrders()
{
   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong orderTicket = OrderGetTicket(i);
      if (orderTicket == 0) continue;
      if (!orderInfo.Select(orderTicket)) continue;
      if (orderInfo.Symbol() != _Symbol || orderInfo.Magic() != InpMagicNumber) continue;

      Print("[CANCEL PENDING ORDER] Menghapus pending order lama #", orderTicket, " untuk digantikan dengan setup terkini.");
      trade.OrderDelete(orderTicket);
   }
}

void CancelOppositePendingOrders(ENUM_ORDER_TYPE targetDir)
{
   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong orderTicket = OrderGetTicket(i);
      if (orderTicket == 0) continue;
      if (!orderInfo.Select(orderTicket)) continue;
      if (orderInfo.Symbol() != _Symbol || orderInfo.Magic() != InpMagicNumber) continue;

      ENUM_ORDER_TYPE oType = orderInfo.OrderType();
      if ((targetDir == ORDER_TYPE_BUY && (oType == ORDER_TYPE_SELL_LIMIT || oType == ORDER_TYPE_SELL_STOP)) ||
          (targetDir == ORDER_TYPE_SELL && (oType == ORDER_TYPE_BUY_LIMIT || oType == ORDER_TYPE_BUY_STOP)))
      {
         Print("[CANCEL OPPOSITE PENDING] Menghapus pending order berlawanan #", orderTicket, " karena sinyal baru telah terbentuk.");
         trade.OrderDelete(orderTicket);
      }
   }
}"""

    if funcs_old in code:
        code = code.replace(funcs_old, "")
        print("[+] Removed ManagePendingOrders & CancelPendingOrders functions!")
    else:
        print("[!] Warning: exact funcs_old not found!")

    # 10. Clean UpdateDashboard()
    # Remove pendingCount loop
    pending_loop_old = """   // Hitung pending orders aktif
   int pendingCount = 0;
   for (int o = OrdersTotal() - 1; o >= 0; o--)
   {
      ulong ot = OrderGetTicket(o);
      if (ot > 0 && orderInfo.Select(ot) && orderInfo.Symbol() == _Symbol && orderInfo.Magic() == InpMagicNumber)
         pendingCount++;
   }"""
    if pending_loop_old in code:
        code = code.replace(pending_loop_old, "")
        print("[+] Removed pendingCount loop in UpdateDashboard!")

    # Remove entryModeTag and btnModeText
    mode_tags_old = """   string entryModeTag = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MARKET" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "BUY/SELL STOP" : "BUY/SELL LIMIT");
   string btnModeText  = (g_activeEntryMode == ENTRY_MARKET_INSTANT) ? "MODE: MKT" : ((g_activeEntryMode == ENTRY_PENDING_STOP) ? "MODE: STOP" : "MODE: LIMIT");"""
    if mode_tags_old in code:
        code = code.replace(mode_tags_old, "")
        print("[+] Removed entryModeTag and btnModeText!")

    # In Minimized HUD:
    code = code.replace(' + " | " + btnModeText;', ';')

    # Remove VIKAR_HUD_BTN_MODE from header
    hud_btn_mode_old = """   // Tombol Mode & Mini
   CreateOrUpdateBtn("VIKAR_HUD_BTN_MODE", panelX + panelW - 170, panelY + 9, 92, 25, btnModeText, C'15,23,42', C'56,189,248', 7);
   CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 74, panelY + 9, 64, 25, "👁️ MINI", C'15,23,42', C'52,211,153', 7);"""

    hud_btn_mode_new = """   // Tombol Mini / Expand
   CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 74, panelY + 9, 64, 25, "👁️ MINI", C'15,23,42', C'52,211,153', 7);"""

    if hud_btn_mode_old in code:
        code = code.replace(hud_btn_mode_old, hud_btn_mode_new)
        print("[+] Removed VIKAR_HUD_BTN_MODE from header!")

    # In Section 4 (Execution bar):
    code = code.replace(
        """   string pendingInfo = (pendingCount > 0) ? (" | Pending: " + IntegerToString(pendingCount)) : "";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 16, currY + 44, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + pendingInfo, C'148,163,184', 7, "Segoe UI");""",
        """   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 16, currY + 44, "Mode: INSTANT MARKET | " + beStr + " | " + cutStr + " | " + trailStr, C'148,163,184', 7, "Segoe UI");"""
    )

    # 11. In OnChartEvent, remove VIKAR_HUD_BTN_MODE click handler
    btn_mode_event_old = """      else if (sparam == "VIKAR_HUD_BTN_MODE")
      {
         if (g_activeEntryMode == ENTRY_MARKET_INSTANT)
            g_activeEntryMode = ENTRY_PENDING_STOP;
         else if (g_activeEntryMode == ENTRY_PENDING_STOP)
            g_activeEntryMode = ENTRY_PENDING_LIMIT;
         else
            g_activeEntryMode = ENTRY_MARKET_INSTANT;

         UpdateDashboard();
         ChartRedraw(0);
         return;
      }"""

    if btn_mode_event_old in code:
        code = code.replace(btn_mode_event_old, "")
        print("[+] Removed VIKAR_HUD_BTN_MODE click handler in OnChartEvent!")

    with open(mq5_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("[+] Successfully purged pending orders from MQ5 source code!")

def clean_presets():
    dirs = [
        r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO",
        r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Profiles\Tester"
    ]
    params_to_remove = [
        "InpEntryMode",
        "InpLimitPullbackPips",
        "InpStopBufferPips",
        "InpPendingExpiryBars",
        "InpCancelPendingOnOpposite"
    ]

    for d in dirs:
        if not os.path.exists(d): continue
        for fname in os.listdir(d):
            if fname.endswith(".set"):
                fpath = os.path.join(d, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    skip = False
                    for p in params_to_remove:
                        if line.strip().startswith(p + "=") or "MODE EKSEKUSI TRANSAKSI" in line:
                            skip = True
                            break
                    if not skip:
                        new_lines.append(line)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                print(f"[+] Cleaned preset: {fname} in {d}")

if __name__ == '__main__':
    remove_pending_from_ea()
    clean_presets()
