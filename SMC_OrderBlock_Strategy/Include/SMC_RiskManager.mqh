//+------------------------------------------------------------------+
//|                                             SMC_RiskManager.mqh  |
//|               SMC Risk Management & Execution Safeguards         |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, XAUUSD Senior Trader"
#property link      ""
#property version   "1.00"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\AccountInfo.mqh>

//+------------------------------------------------------------------+
//| Class Pengelola Resiko SMC                                       |
//+------------------------------------------------------------------+
class CSMCRiskManager
  {
private:
   int               m_dailyLossCount;
   double            m_dailyLossAmount;
   int               m_lastCalculatedDay;

public:
                     CSMCRiskManager();
                    ~CSMCRiskManager();

   double            CalculateLotSize(double equity, double riskPercent, double slDistancePoints,
                                      string symbol, double fixedLot = 0.01, bool useFixedLot = false,
                                      double maxLotSize = 5.0);

   void              UpdateDailyStats(ulong magic, string symbol);
   bool              IsDailyLossLimitReached(ulong magic, string symbol, double equity,
                                             bool useDailyLimit, int maxLosses, double maxLossPercent);

   bool              IsFridayTradingRestricted(bool useFridayClose, int closeHour, int closeMinute,
                                               bool blockNewTrades, int stopTradeHour);

   void              CheckFridayAutoClose(CTrade &tradeObj, CPositionInfo &posInfo, ulong magic, string symbol,
                                          bool useFridayClose, int closeHour, int closeMinute);
  };

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CSMCRiskManager::CSMCRiskManager()
  {
   m_dailyLossCount    = 0;
   m_dailyLossAmount   = 0.0;
   m_lastCalculatedDay = -1;
  }

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CSMCRiskManager::~CSMCRiskManager()
  {
  }

//+------------------------------------------------------------------+
//| Hitung Lot Size Dinamis Berdasarkan % Resiko Modal               |
//+------------------------------------------------------------------+
double CSMCRiskManager::CalculateLotSize(double equity, double riskPercent, double slDistancePoints,
                                         string symbol, double fixedLot = 0.01, bool useFixedLot = false,
                                         double maxLotSize = 5.0)
  {
   if(useFixedLot) return fixedLot;

   double riskMoney = equity * (riskPercent / 100.0);

   double tickSize  = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(symbol, SYMBOL_TRADE_TICK_VALUE);
   double pointVal  = (tickSize > 0.0) ? (tickValue / tickSize) * SymbolInfoDouble(symbol, SYMBOL_POINT) : 1.0;

   if(slDistancePoints <= 0 || pointVal <= 0) return SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);

   double calculatedLot = riskMoney / (slDistancePoints * pointVal);

   double stepLot = SymbolInfoDouble(symbol, SYMBOL_VOLUME_STEP);
   double minLot  = SymbolInfoDouble(symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = MathMin(SymbolInfoDouble(symbol, SYMBOL_VOLUME_MAX), maxLotSize);

   int lotDigits = 2;
   if(stepLot <= 0.001) lotDigits = 3;
   else if(stepLot >= 0.1) lotDigits = 1;

   calculatedLot = MathFloor(calculatedLot / stepLot) * stepLot;
   calculatedLot = MathMax(minLot, MathMin(maxLot, calculatedLot));
   calculatedLot = NormalizeDouble(calculatedLot, lotDigits);

   return calculatedLot;
  }

//+------------------------------------------------------------------+
//| Perbarui Statistik Kerugian Harian Dari Deal History Broker      |
//+------------------------------------------------------------------+
void CSMCRiskManager::UpdateDailyStats(ulong magic, string symbol)
  {
   MqlDateTime dt;
   TimeCurrent(dt);

   if(dt.day != m_lastCalculatedDay)
     {
      m_dailyLossCount    = 0;
      m_dailyLossAmount   = 0.0;
      m_lastCalculatedDay = dt.day;
     }

   datetime dayStart = StringToTime(StringFormat("%04d.%02d.%02d 00:00", dt.year, dt.mon, dt.day));
   if(!HistorySelect(dayStart, TimeCurrent())) return;

   m_dailyLossCount  = 0;
   m_dailyLossAmount = 0.0;
   int totalDeals    = HistoryDealsTotal();

   for(int i = 0; i < totalDeals; i++)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket > 0)
        {
         if(HistoryDealGetString(ticket, DEAL_SYMBOL) == symbol &&
            HistoryDealGetInteger(ticket, DEAL_MAGIC) == magic &&
            HistoryDealGetInteger(ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
           {
            double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) + 
                            HistoryDealGetDouble(ticket, DEAL_SWAP) + 
                            HistoryDealGetDouble(ticket, DEAL_COMMISSION);
            if(profit < -0.01)
              {
               m_dailyLossCount++;
               m_dailyLossAmount += MathAbs(profit);
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Cek Apakah Batas Kerugian Harian (Daily Circuit Breaker) Tercapai|
//+------------------------------------------------------------------+
bool CSMCRiskManager::IsDailyLossLimitReached(ulong magic, string symbol, double equity,
                                              bool useDailyLimit, int maxLosses, double maxLossPercent)
  {
   if(!useDailyLimit) return false;

   UpdateDailyStats(magic, symbol);

   if(m_dailyLossCount >= maxLosses)
     {
      Print(StringFormat("[SMC Circuit Breaker] Batas kalah harian (%d trade) tercapai. Trading ditutup hingga besok.",
                         m_dailyLossCount));
      return true;
     }

   double maxAllowedLoss = equity * (maxLossPercent / 100.0);
   if(m_dailyLossAmount >= maxAllowedLoss && maxAllowedLoss > 0.0)
     {
      Print(StringFormat("[SMC Circuit Breaker] Batas nominal loss harian ($%.2f / $%.2f) tercapai. Trading ditutup hingga besok.",
                         m_dailyLossAmount, maxAllowedLoss));
      return true;
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Trading Jumat Dibatasi (Proteksi Gap Akhir Pekan)     |
//+------------------------------------------------------------------+
bool CSMCRiskManager::IsFridayTradingRestricted(bool useFridayClose, int closeHour, int closeMinute,
                                                bool blockNewTrades, int stopTradeHour)
  {
   if(!useFridayClose) return false;

   MqlDateTime dt;
   TimeCurrent(dt);

   if(dt.day_of_week == 5) // Hari Jumat
     {
      if(dt.hour > closeHour || (dt.hour == closeHour && dt.min >= closeMinute))
         return true;

      if(blockNewTrades && dt.hour >= stopTradeHour)
         return true;
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Tutup Semua Posisi Terbuka di Hari Jumat Malam                   |
//+------------------------------------------------------------------+
void CSMCRiskManager::CheckFridayAutoClose(CTrade &tradeObj, CPositionInfo &posInfo, ulong magic, string symbol,
                                           bool useFridayClose, int closeHour, int closeMinute)
  {
   if(!useFridayClose) return;

   MqlDateTime dt;
   TimeCurrent(dt);

   if(dt.day_of_week == 5)
     {
      if(dt.hour > closeHour || (dt.hour == closeHour && dt.min >= closeMinute))
        {
         for(int i = PositionsTotal() - 1; i >= 0; i--)
           {
            if(!posInfo.SelectByIndex(i)) continue;
            if(posInfo.Symbol() != symbol || posInfo.Magic() != magic) continue;

            ulong ticket = posInfo.Ticket();
            if(tradeObj.PositionClose(ticket))
              {
               Print(StringFormat("[SMC Friday Auto-Close] Posisi #%I64u ditutup sebelum penutupan pasar akhir pekan.", ticket));
              }
            else
              {
               Print(StringFormat("[SMC Friday Auto-Close Error] Gagal menutup posisi #%I64u: %s", ticket, tradeObj.ResultRetcodeDescription()));
              }
           }
        }
     }
  }
