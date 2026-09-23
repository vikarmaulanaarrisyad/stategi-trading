import os
import shutil

def update_ea_code():
    mq5_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(mq5_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Update InpEntryMode default to ENTRY_PENDING_STOP
    code = code.replace(
        "input ENUM_ENTRY_EXECUTION_MODE InpEntryMode          = ENTRY_MARKET_INSTANT; // Model Eksekusi Sinyal (Market / Limit / Stop)",
        "input ENUM_ENTRY_EXECUTION_MODE InpEntryMode          = ENTRY_PENDING_STOP;   // Model Eksekusi Sinyal (Market / Limit / Stop)"
    )

    # 2. Update RiskRewardRatio default to 2.0
    code = code.replace(
        "input double        InpRiskRewardRatio    = 1.5;                   // Rasio Risk to Reward (Default: 1 : 1.5 s/d 1 : 2.0)",
        "input double        InpRiskRewardRatio    = 2.0;                   // Rasio Risk to Reward (Default: 1 : 1.5 s/d 1 : 2.0)"
    )

    # 3. Update Breakeven Trigger Pips to 12.0 and Lock to 4.0
    code = code.replace(
        "input double        InpBreakevenTriggerPips= 5.0;                  // Jarak Profit Memicu BE / SL+ (5.0 Pips = 50 Point)",
        "input double        InpBreakevenTriggerPips= 12.0;                 // Jarak Profit Memicu BE / SL+ (12.0 Pips = 120 Point)"
    )
    code = code.replace(
        "input double        InpBreakevenLockPips  = 2.0;                   // Pips Keuntungan Terkunci Saat SL+ (2.0 Pips = 20 Point)",
        "input double        InpBreakevenLockPips  = 4.0;                   // Pips Keuntungan Terkunci Saat SL+ (4.0 Pips = 40 Point)"
    )
    code = code.replace(
        "input double        InpTrailingBufferPips = 3.0;                   // Jarak Buffer Trailing dari EMA 21 (Pips)",
        "input double        InpTrailingBufferPips = 5.0;                   // Jarak Buffer Trailing dari EMA 21 (Pips)"
    )

    # 4. Update Partial Close Trigger Pips to 15.0 and RR to 1.5
    code = code.replace(
        "input double        InpPartialTriggerPips = 6.0;                   // Jarak Profit Pemicu TP1 (6.0 Pips = 60 Point)",
        "input double        InpPartialTriggerPips = 15.0;                  // Jarak Profit Pemicu TP1 (15.0 Pips = 150 Point)"
    )
    code = code.replace(
        "input double        InpPartialRRTrigger   = 1.2;                   // Pemicu TP1 Saat Mencapai R:R (1.2 = 1:1.2, Mode RR)",
        "input double        InpPartialRRTrigger   = 1.5;                   // Pemicu TP1 Saat Mencapai R:R (1.5 = 1:1.5, Mode RR)"
    )

    # 5. Update MaxSpreadPips to 6.0
    code = code.replace(
        "input double        InpMaxSpreadPips      = 10.0;                  // Batas Maksimal Spread Diizinkan (Pips - Aman Malam Hari)",
        "input double        InpMaxSpreadPips      = 6.0;                   // Batas Maksimal Spread Diizinkan (Pips - Aman Rollover)"
    )

    # 6. Fix ManagePendingOrders() and add CancelAllPendingOrders()
    old_manage = """//+------------------------------------------------------------------+
//| MANAJEMEN & PEMBATALAN PENDING ORDER KEDALUWARSA / BERLAWANAN    |
//+------------------------------------------------------------------+
void ManagePendingOrders()
{
   if (g_activeEntryMode == ENTRY_MARKET_INSTANT)
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
}"""

    new_manage = """//+------------------------------------------------------------------+
//| MANAJEMEN & PEMBATALAN PENDING ORDER KEDALUWARSA / BERLAWANAN    |
//+------------------------------------------------------------------+
void ManagePendingOrders()
{
   if (OrdersTotal() == 0) return;

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

    if old_manage in code:
        code = code.replace(old_manage, new_manage)
        print("[+] Replaced ManagePendingOrders with robust version!")
    else:
        print("[!] Warning: exact old_manage string not found, checking...")

    # Replace CancelOppositePendingOrders with CancelAllPendingOrders prior to entry
    code = code.replace(
        "            if (InpCancelPendingOnOpposite)\n               CancelOppositePendingOrders(ORDER_TYPE_BUY);",
        "            CancelAllPendingOrders();"
    )
    code = code.replace(
        "         if (InpCancelPendingOnOpposite)\n            CancelOppositePendingOrders(ORDER_TYPE_SELL);",
        "         CancelAllPendingOrders();"
    )

    with open(mq5_path, "w", encoding="utf-8") as f:
        f.write(code)
    print("[+] MQ5 source code updated successfully!")

def update_presets():
    dirs = [
        r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO",
        r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Profiles\Tester"
    ]
    preset_files = [
        "XAUUSD_BACKTEST_1YEAR_OPTIMAL.set",
        "XAUUSD_HIGH_WINRATE_SNIPER.set",
        "XAUUSD_M5_Scalping_Confluence.set",
        "XAUUSD_M15_DayTrading_GradeA.set",
        "XAUUSD_FAST_AUTO_TRADE.set"
    ]

    extra_params = """
;--- 1.1 MODE EKSEKUSI TRANSAKSI v3.30 ---
InpEntryMode=2
InpLimitPullbackPips=5.0
InpStopBufferPips=2.0
InpPendingExpiryBars=4
InpCancelPendingOnOpposite=1
InpMaxSpreadPips=6.0
"""

    for d in dirs:
        if not os.path.exists(d): continue
        for p in preset_files:
            target = os.path.join(d, p)
            if os.path.exists(target):
                with open(target, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                if "InpEntryMode" not in content:
                    content = content + "\n" + extra_params
                    with open(target, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"[+] Appended v3.30 parameters to {target}")

if __name__ == '__main__':
    update_ea_code()
    update_presets()
