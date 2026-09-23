import os
import shutil

def upgrade_mt5():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    backup_path = path + ".v330.bak"
    shutil.copyfile(path, backup_path)
    print(f"[+] Backup created at: {backup_path}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Version update
    code = code.replace('#property version   "3.20"', '#property version   "3.30"')
    code = code.replace(
        '#property description "Vikar EA 4-Pillar Pro - Apex Grandmaster Edition v3.20 (Autonomous Neuro-Calibration & Self-Tuning)"',
        '#property description "Vikar EA 4-Pillar Pro - Apex Grandmaster Edition v3.30 (Multi-Execution Matrix: Market, Limit, Stop)"'
    )

    # 2. Enum declaration
    enum_decl = """enum ENUM_ENTRY_EXECUTION_MODE
{
   ENTRY_MARKET_INSTANT,   // Langsung Entry (Instant Market Order di Open Lilin)
   ENTRY_PENDING_LIMIT,    // BUY Limit / SELL Limit (Pullback / Retracement Discount)
   ENTRY_PENDING_STOP      // BUY Stop / SELL Stop (Breakout Konfirmasi High/Low Lilin)
};
"""
    anchor_enum = '//+------------------------------------------------------------------+\n//| INPUT PARAMETERS USER'
    if anchor_enum in code:
        code = code.replace(anchor_enum, enum_decl + "\n" + anchor_enum)
    else:
        print("[-] anchor_enum not found!")
        return False

    # 3. Input parameters for Entry Mode
    input_decl = """input group "=== 1.1 MODE EKSEKUSI TRANSAKSI (MARKET / LIMIT / STOP) ==="
input ENUM_ENTRY_EXECUTION_MODE InpEntryMode          = ENTRY_MARKET_INSTANT; // Model Eksekusi Sinyal (Market / Limit / Stop)
input double                    InpLimitPullbackPips  = 5.0;                  // Jarak Pullback Limit Order (Pips dari Open/Market)
input double                    InpStopBufferPips     = 2.0;                  // Buffer Breakout Stop Order (Pips di Luar Ujung Lilin)
input int                       InpPendingExpiryBars  = 4;                    // Batas Lilin Kedaluwarsa Pending Order (0 = Batal Mati)
input bool                      InpCancelPendingOnOpposite = true;            // Batalkan Pending Order Jika Terbentuk Sinyal Berlawanan
"""
    anchor_input = 'input group "=== 2. TARGET STOP LOSS, TAKE PROFIT & EXIT STRATEGY ==="'
    if anchor_input in code:
        code = code.replace(anchor_input, input_decl + "\n" + anchor_input)
    else:
        print("[-] anchor_input not found!")
        return False

    # 4. Global object: COrderInfo orderInfo;
    anchor_obj = "CPositionInfo  posInfo;"
    if anchor_obj in code:
        code = code.replace(anchor_obj, anchor_obj + "\nCOrderInfo     orderInfo;")
    else:
        print("[-] anchor_obj not found!")
        return False

    # 5. Helper functions: ManagePendingOrders & CancelOppositePendingOrders
    helper_code = """//+------------------------------------------------------------------+
//| PENGELOLA SIKLUS HIDUP PENDING ORDER (v3.30)                     |
//+------------------------------------------------------------------+
void ManagePendingOrders()
{
   if (InpEntryMode == ENTRY_MARKET_INSTANT)
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
}
"""
    anchor_helper = "void ManageActiveTrades()"
    if anchor_helper in code:
        code = code.replace(anchor_helper, helper_code + "\n" + anchor_helper)
    else:
        print("[-] anchor_helper not found!")
        return False

    # 6. Call ManagePendingOrders in OnTick
    anchor_ontick = "ManageActiveTrades();"
    if anchor_ontick in code:
        code = code.replace(anchor_ontick, "ManageActiveTrades();\n   ManagePendingOrders();", 1)
    else:
        print("[-] anchor_ontick not found!")
        return False

    # 7. Check InpMaxOpenPositions for both positions and pending orders
    old_pos_count = """   // 8. Periksa Batas Maksimal Posisi Aktif untuk Entry Baru
   int openCount = 0;
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (posInfo.SelectByIndex(i))
      {
         if (posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
            openCount++;
      }
   }
   if (openCount >= InpMaxOpenPositions)
      return;"""

    new_pos_count = """   // 8. Periksa Batas Maksimal Posisi Aktif untuk Entry Baru (Posisi Aktif + Pending Orders)
   int openCount = 0;
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (posInfo.SelectByIndex(i))
      {
         if (posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
            openCount++;
      }
   }
   for (int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong oTicket = OrderGetTicket(i);
      if (oTicket > 0 && orderInfo.Select(oTicket))
      {
         if (orderInfo.Symbol() == _Symbol && orderInfo.Magic() == InpMagicNumber)
            openCount++;
      }
   }
   if (openCount >= InpMaxOpenPositions)
      return;"""

    if old_pos_count in code:
        code = code.replace(old_pos_count, new_pos_count)
    else:
        print("[-] old_pos_count not found!")
        return False

    # 8. BUY Execution replacement
    old_buy_exec = """            if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
            {
               ulong buyTicket = trade.ResultOrder();
               ulong buyDeal = trade.ResultDeal();
               GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString((long)buyTicket), MathMax(ask - slPrice, 10 * _Point));
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMQL5(buyTicket, buyDeal, (isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)), 1, scoreRes.totalScore, currentAtr);

               lastOrderBarTime = iTime(_Symbol, _Period, 0);
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = "BUY EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
               Print("[BUY EXECUTION] Lot: ", lots, " | Price: ", ask, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert("BUY " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(ask, _Digits) +
                                "\\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                                "\\nPola: " + patStr);
               }
               UpdateDashboard();
               return;
            }
            else
            {
               Print("[BUY REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
               g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
            }"""

    new_buy_exec = """            if (InpCancelPendingOnOpposite)
               CancelOppositePendingOrders(ORDER_TYPE_BUY);

            bool orderSuccess = false;
            ulong buyTicket = 0;
            ulong buyDeal = 0;
            double executedPrice = ask;
            string execModeTag = "MARKET";

            if (InpEntryMode == ENTRY_MARKET_INSTANT)
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
            else if (InpEntryMode == ENTRY_PENDING_LIMIT)
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
            else if (InpEntryMode == ENTRY_PENDING_STOP)
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
            }

            if (orderSuccess)
            {
               GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString((long)buyTicket), MathMax(executedPrice - slPrice, 10 * _Point));
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMQL5(buyTicket, buyDeal, (isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)), 1, scoreRes.totalScore, currentAtr);

               lastOrderBarTime = iTime(_Symbol, _Period, 0);
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = execModeTag + " PLACED: " + patStr + " @ " + DoubleToString(executedPrice, _Digits);
               Print("[", execModeTag, " EXECUTION] Lot: ", lots, " | Price: ", executedPrice, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert(execModeTag + " " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(executedPrice, _Digits) +
                                "\\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                                "\\nPola: " + patStr);
               }
               UpdateDashboard();
               return;
            }
            else
            {
               Print("[BUY REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
               g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
            }"""

    if old_buy_exec in code:
        code = code.replace(old_buy_exec, new_buy_exec)
    else:
        print("[-] old_buy_exec not found!")
        return False

    # 9. SELL Execution replacement
    old_sell_exec = """         if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
         {
            ulong sellTicket = trade.ResultOrder();
            ulong sellDeal = trade.ResultDeal();
            GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString((long)sellTicket), MathMax(slPrice - bid, 10 * _Point));
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               g_autopsy.tradesWithExtraBuffer--;
            SaveTradeEntrySnapshotMQL5(sellTicket, sellDeal, (isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)), -1, scoreRes.totalScore, currentAtr);

            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
            g_lastSignalType = "SELL EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
            Print("[SELL EXECUTION] Lot: ", lots, " | Price: ", bid, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
            if (InpNotifyOnEntry)
            {
               SendPushAlert("SELL " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(bid, _Digits) +
                             "\\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                             "\\nPola: " + patStr);
            }
            UpdateDashboard();
            return;
         }
         else
         {
            Print("[SELL REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
            g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
         }"""

    new_sell_exec = """         if (InpCancelPendingOnOpposite)
            CancelOppositePendingOrders(ORDER_TYPE_SELL);

         bool orderSuccess = false;
         ulong sellTicket = 0;
         ulong sellDeal = 0;
         double executedPrice = bid;
         string execModeTag = "MARKET";

         if (InpEntryMode == ENTRY_MARKET_INSTANT)
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
         else if (InpEntryMode == ENTRY_PENDING_LIMIT)
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
         else if (InpEntryMode == ENTRY_PENDING_STOP)
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
         }

         if (orderSuccess)
         {
            GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString((long)sellTicket), MathMax(slPrice - executedPrice, 10 * _Point));
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               g_autopsy.tradesWithExtraBuffer--;
            SaveTradeEntrySnapshotMQL5(sellTicket, sellDeal, (isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)), -1, scoreRes.totalScore, currentAtr);

            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
            g_lastSignalType = execModeTag + " PLACED: " + patStr + " @ " + DoubleToString(executedPrice, _Digits);
            Print("[", execModeTag, " EXECUTION] Lot: ", lots, " | Price: ", executedPrice, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
            if (InpNotifyOnEntry)
            {
               SendPushAlert(execModeTag + " " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(executedPrice, _Digits) +
                             "\\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                             "\\nPola: " + patStr);
            }
            UpdateDashboard();
            return;
         }
         else
         {
            Print("[SELL REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
            g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
         }"""

    if old_sell_exec in code:
        code = code.replace(old_sell_exec, new_sell_exec)
    else:
        print("[-] old_sell_exec not found!")
        return False

    # 10. Dashboard update for Entry Mode
    old_hud_sub = """CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 12, panelY + 19, _Symbol + " [" + EnumToString(_Period) + "] | " + lotDisplay + " | ID: " + IntegerToString(InpMagicNumber), C'224,242,254', 7, "Segoe UI");"""
    new_hud_sub = """string entryModeTag = (InpEntryMode == ENTRY_MARKET_INSTANT) ? "MARKET" : ((InpEntryMode == ENTRY_PENDING_LIMIT) ? "LIMIT (" + DoubleToString(InpLimitPullbackPips, 0) + "p)" : "STOP (" + DoubleToString(InpStopBufferPips, 0) + "p)");
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 12, panelY + 19, _Symbol + " [" + EnumToString(_Period) + "] | " + lotDisplay + " | " + entryModeTag + " | ID: " + IntegerToString(InpMagicNumber), C'224,242,254', 7, "Segoe UI");"""

    if old_hud_sub in code:
        code = code.replace(old_hud_sub, new_hud_sub)
    else:
        print("[-] old_hud_sub not found!")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] Successfully upgraded VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5 to v3.30!")
    return True

if __name__ == '__main__':
    upgrade_mt5()
