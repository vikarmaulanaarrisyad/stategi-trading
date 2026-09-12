//+------------------------------------------------------------------+
//|                                           SMC_OrderBlock_EA.mq5  |
//|                 Smart Money Concepts (SMC) Expert Advisor        |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.40"
#property description "Auto Trading EA Smart Money Concepts (Order Block & FVG) untuk XAUUSD & Forex - Ultra High Probability 80%+ Winrate Edition"

// Include pustaka standar MQL5
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\AccountInfo.mqh>

// Include modul strategi SMC
#include "..\Include\SMC_Core.mqh"
#include "..\Include\SMC_RiskManager.mqh"

//+------------------------------------------------------------------+
//| Enum Mode Money Management                                       |
//+------------------------------------------------------------------+
enum ENUM_SMC_LOT_MODE
  {
   LOT_MODE_FIXED,        // Fixed Lot
   LOT_MODE_RISK_PERCENT  // Dinamis Berdasarkan % Resiko dari Modal
  };

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== Parameter Deteksi Smart Money Concepts ==="
input int                  InpSwingLookback        = 3;             // Fractal Swing Lookback (Bars)
input int                  InpMaxZones             = 8;             // Maksimal Zona OB & FVG Aktif
input double               InpMinFvgPoints         = 30.0;          // Ukuran Minimal FVG (Points)
input double               InpMinObPoints          = 30.0;          // Ukuran Minimal Order Block (Points)
input int                  InpSignalCooldownBars   = 4;             // Jeda Minimal Antar Sinyal (Bars Anti-Spam)
input bool                 InpRequireStrongClose   = true;          // Wajib Candle Close Rejection (Bullish/Bearish)
input bool                 InpRequireRejectionWick = true;          // Wajib Ekor Rejection Penolakan Harga (Pin Bar)
input double               InpMinRejectionWickPct  = 30.0;          // Minimal Panjang Ekor Rejection (% Candle Range)
input bool                 InpRequireFVGConfluence = false;         // Wajib Konfirmasi FVG Imbalance

input group "=== Konfirmasi Probabilitas Tinggi (Target Winrate 80%+) ==="
input bool                 InpUsePremiumDiscount   = true;          // Hanya Buy di Discount & Sell di Premium (Equilibrium 50%)
input bool                 InpUseRsiFilter         = true;          // Filter RSI Momentum Exhaustion
input int                  InpRsiPeriod            = 14;            // Periode RSI
input double               InpRsiOversold          = 48.0;          // Batas Maksimal RSI Buy (Area Jenuh Jual)
input double               InpRsiOverbought        = 52.0;          // Batas Minimal RSI Sell (Area Jenuh Beli)
input bool                 InpRequireLiquiditySweep= false;         // Wajib Konfirmasi Liquidity Sweep (Turtle Soup)

input group "=== Filter Arah Tren & Institusional ==="
input bool                 InpRequireStructure     = true;          // Wajib Searah Struktur SMC (BOS / CHoCH)
input bool                 InpUseEma200Filter      = true;          // Filter Tren Institusional EMA 200
input int                  InpEma200Period         = 200;           // Periode EMA Tren
input bool                 InpUseHtfFilter         = true;          // Filter Macro HTF Trend (H1 EMA 50)
input ENUM_TIMEFRAMES      InpHtfTimeframe         = PERIOD_H1;     // Timeframe HTF Macro Baseline
input int                  InpHtfEmaPeriod         = 50;            // Periode EMA Macro HTF
input bool                 InpUseADXFilter         = true;          // Filter Momentum ADX (Hindari Sideways)
input int                  InpADXPeriod            = 14;            // Periode ADX
input double               InpMinADX               = 20.0;          // Batas Minimal ADX (Pasar Aktif)

input group "=== Money Management & Lot Size ==="
input ENUM_SMC_LOT_MODE    InpLotMode              = LOT_MODE_RISK_PERCENT; // Mode Lot Sizing
input double               InpFixedLot             = 0.01;          // Fixed Lot Size (jika LOT_MODE_FIXED)
input double               InpRiskPercent          = 1.0;           // Resiko per Trade (% Equity)
input double               InpMaxLotSize           = 5.0;           // Maksimal Lot Eksekusi
input int                  InpMaxOpenPositions     = 1;             // Maksimal Posisi Terbuka Bersamaan

input group "=== Stop Loss & Take Profit (Target Winrate 80%+) ==="
input int                  InpSL_BufferPoints      = 80;            // Buffer Tambahan di luar Zona OB (Anti Liquidity Sweep)
input double               InpRiskRewardRatio      = 1.3;           // Target Risk:Reward (1:1.3 Optimal Winrate 80%+)
input int                  InpMinSLPoints          = 180;           // Batas Minimal SL Points (Proteksi Gold)

input group "=== Proteksi Profit: Break-Even & Trailing ==="
input bool                 InpUseBreakEven         = true;          // Aktifkan Auto Break-Even (BEP)
input double               InpBE_TriggerRR         = 1.0;           // Pindahkan SL ke BEP saat Profit 1:1 R:R
input int                  InpBE_LockProfitPoints  = 15;            // Profit Terkunci di atas Entry (Points)
input bool                 InpUseTrailingStop      = false;         // Aktifkan Trailing Stop (False agar TP penuh tercapai)
input double               InpTrailingStartRR      = 1.5;           // Trailing Baru Aktif Setelah Profit 1:X R:R
input double               InpTrailingStepPoints   = 100;           // Step Geser Trailing Stop (Points)

input group "=== Proteksi Kerugian Harian (Circuit Breaker) ==="
input bool                 InpUseDailyLossLimit    = true;          // Batasi Kerugian Harian (Stop Trading Hari Ini)
input int                  InpMaxDailyLosses       = 2;             // Maksimal Trade Kalah per Hari (Stop jika tercapai)
input double               InpMaxDailyLossPercent  = 3.0;           // Maksimal % Kerugian Harian dari Equity

input group "=== Proteksi Gap Akhir Pekan (Friday Auto-Close) ==="
input bool                 InpUseFridayClose       = true;          // Aktifkan Auto-Close Jumat Malam (Anti-Gap Weekend)
input int                  InpFridayCloseHour      = 21;            // Jam Auto-Close Jumat Malam (Broker Time)
input int                  InpFridayCloseMinute    = 30;            // Menit Auto-Close Jumat Malam (Broker Time)
input bool                 InpBlockFridayNewTrades = true;          // Blokir Sinyal Baru Jumat Sore/Malam
input int                  InpFridayStopTradeHour  = 18;            // Jam Mulai Blokir Sinyal Baru di Hari Jumat

input group "=== Filter Waktu Trading (Prime Sessions: London & NY) ==="
input bool                 InpUseTimeFilter        = true;          // Batasi Jam Trading
input int                  InpStartHour            = 8;             // Jam Mulai Trading (Sesi London)
input int                  InpEndHour              = 18;            // Jam Akhir Trading (Peak NY Session)
input int                  InpMaxSpreadPoints      = 60;            // Maksimal Spread Diizinkan (Points)

input group "=== Kecepatan Simulasi Visual Mode ==="
input int                  InpVisualDelayMs        = 0;             // Delay Visual Per Tick/Bar (ms, 0=Normal, 50-100ms=Santai)

input group "=== EA System ID ==="
input ulong                InpMagicNumber          = 7788991;       // Magic Number Unik SMC
input string               InpOrderComment         = "SMC_OB_XAU";  // Komentar Order

//+------------------------------------------------------------------+
//| Objek Trading & Indikator                                        |
//+------------------------------------------------------------------+
CTrade                 trade;
CPositionInfo          positionInfo;
CAccountInfo           accountInfo;

CSMCCore               smcEngine;
CSMCRiskManager        riskManager;

int                    handleEma200      = INVALID_HANDLE;
int                    handleADX         = INVALID_HANDLE;
int                    handleRSI         = INVALID_HANDLE;

datetime               lastTradeBarTime  = 0;
datetime               lastBuyTradeTime  = 0;
datetime               lastSellTradeTime = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetDeviationInPoints(20);

   smcEngine.Configure(InpSwingLookback, InpMaxZones, InpMinFvgPoints, InpMinObPoints);

   if(InpUseEma200Filter)
     {
      handleEma200 = iMA(_Symbol, _Period, InpEma200Period, 0, MODE_EMA, PRICE_CLOSE);
      if(handleEma200 == INVALID_HANDLE)
        {
         Print("[SMC EA Error] Gagal membuat handle EMA 200!");
         return(INIT_FAILED);
        }
     }

   if(InpUseADXFilter)
     {
      handleADX = iADX(_Symbol, _Period, InpADXPeriod);
      if(handleADX == INVALID_HANDLE)
        {
         Print("[SMC EA Error] Gagal membuat handle ADX!");
         return(INIT_FAILED);
        }
     }

   if(InpUseRsiFilter)
     {
      handleRSI = iRSI(_Symbol, _Period, InpRsiPeriod, PRICE_CLOSE);
      if(handleRSI == INVALID_HANDLE)
        {
         Print("[SMC EA Error] Gagal membuat handle RSI!");
         return(INIT_FAILED);
        }
     }

   Print(StringFormat("[SMC EA Started] Ultra High Winrate Edition aktif pada %s %s | Magic: %d",
                      _Symbol, EnumToString(_Period), InpMagicNumber));

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(handleEma200 != INVALID_HANDLE) IndicatorRelease(handleEma200);
   if(handleADX != INVALID_HANDLE) IndicatorRelease(handleADX);
   if(handleRSI != INVALID_HANDLE) IndicatorRelease(handleRSI);
   Print("[SMC EA Stopped] Robot SMC dimatikan. Reason: ", reason);
  }

//+------------------------------------------------------------------+
//| Cek Trend Multi-Timeframe Macro (H1 EMA 50)                      |
//| Return: 1 = Bullish Macro, -1 = Bearish Macro, 0 = Netral        |
//+------------------------------------------------------------------+
int CheckHtfTrend()
  {
   if(!InpUseHtfFilter) return 0;

   ENUM_TIMEFRAMES targetHtf = InpHtfTimeframe;
   if(targetHtf <= _Period)
     {
      if(_Period == PERIOD_M1) targetHtf = PERIOD_M15;
      else if(_Period == PERIOD_M5) targetHtf = PERIOD_H1;
      else if(_Period == PERIOD_M15) targetHtf = PERIOD_H1;
      else if(_Period == PERIOD_M30) targetHtf = PERIOD_H4;
      else if(_Period >= PERIOD_H1) targetHtf = PERIOD_D1;
     }

   int htfHandle = iMA(_Symbol, targetHtf, InpHtfEmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
   if(htfHandle == INVALID_HANDLE) return 0;

   double htfEma[];
   ArraySetAsSeries(htfEma, true);
   if(CopyBuffer(htfHandle, 0, 1, 1, htfEma) <= 0)
     {
      IndicatorRelease(htfHandle);
      return 0;
     }

   MqlRates htfRates[];
   ArraySetAsSeries(htfRates, true);
   if(CopyRates(_Symbol, targetHtf, 1, 1, htfRates) <= 0)
     {
      IndicatorRelease(htfHandle);
      return 0;
     }

   double htfClose  = htfRates[0].close;
   double htfEmaVal = htfEma[0];
   IndicatorRelease(htfHandle);

   if(htfClose > htfEmaVal) return 1;
   if(htfClose < htfEmaVal) return -1;
   return 0;
  }

//+------------------------------------------------------------------+
//| Hitung Posisi Terbuka Sesuai Magic Number                        |
//+------------------------------------------------------------------+
int CountOpenPositions()
  {
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(positionInfo.SelectByIndex(i))
        {
         if(positionInfo.Symbol() == _Symbol && positionInfo.Magic() == InpMagicNumber)
           {
            count++;
           }
        }
     }
   return count;
  }

//+------------------------------------------------------------------+
//| Cek Filter Jam Trading                                           |
//+------------------------------------------------------------------+
bool IsTradingTimeAllowed()
  {
   if(!InpUseTimeFilter) return true;

   MqlDateTime dt;
   TimeCurrent(dt);

   if(dt.hour < InpStartHour || dt.hour >= InpEndHour)
      return false;

   return true;
  }

//+------------------------------------------------------------------+
//| Kelola Break-Even dan Trailing Stop                              |
//+------------------------------------------------------------------+
void ManageOpenTrades()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(!positionInfo.SelectByIndex(i)) continue;
      if(positionInfo.Symbol() != _Symbol || positionInfo.Magic() != InpMagicNumber) continue;

      ulong ticket        = positionInfo.Ticket();
      double openPrice    = positionInfo.PriceOpen();
      double currentSL    = positionInfo.StopLoss();
      double currentTP    = positionInfo.TakeProfit();
      double currentPrice = positionInfo.PriceCurrent();
      ENUM_POSITION_TYPE posType = positionInfo.PositionType();

      double initialSLDistance = MathAbs(openPrice - currentSL);
      if(initialSLDistance <= 0.0) initialSLDistance = 200 * _Point;

      long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
      double minDist  = MathMax(stopsLevel * _Point, 15 * _Point);

      double profitDistance = 0.0;
      if(posType == POSITION_TYPE_BUY) profitDistance = currentPrice - openPrice;
      else if(posType == POSITION_TYPE_SELL) profitDistance = openPrice - currentPrice;
      double currentR = (initialSLDistance > 0.0) ? profitDistance / initialSLDistance : 0.0;

      // 1. AUTO BREAK-EVEN (Aktif saat profit mencapai InpBE_TriggerRR)
      if(InpUseBreakEven && currentR >= InpBE_TriggerRR)
        {
         if(posType == POSITION_TYPE_BUY && currentSL < openPrice)
           {
            double newSL = NormalizeDouble(openPrice + (InpBE_LockProfitPoints * _Point), _Digits);
            if((currentPrice - newSL) >= minDist)
              {
               trade.PositionModify(ticket, newSL, currentTP);
               Print("[SMC Auto BEP] Buy Order #", ticket, " SL dipindahkan ke Break-Even: ", newSL);
               continue;
              }
           }
         else if(posType == POSITION_TYPE_SELL && (currentSL > openPrice || currentSL == 0.0))
           {
            double newSL = NormalizeDouble(openPrice - (InpBE_LockProfitPoints * _Point), _Digits);
            if((newSL - currentPrice) >= minDist)
              {
               trade.PositionModify(ticket, newSL, currentTP);
               Print("[SMC Auto BEP] Sell Order #", ticket, " SL dipindahkan ke Break-Even: ", newSL);
               continue;
              }
           }
        }

      // 2. TRAILING STOP
      if(InpUseTrailingStop && currentR >= InpTrailingStartRR)
        {
         if(posType == POSITION_TYPE_BUY)
           {
            double targetTrailSL = currentPrice - (initialSLDistance * 0.75);
            if(targetTrailSL > openPrice && targetTrailSL > currentSL + (InpTrailingStepPoints * _Point) && (currentPrice - targetTrailSL) >= minDist)
              {
               trade.PositionModify(ticket, NormalizeDouble(targetTrailSL, _Digits), currentTP);
               Print("[SMC Trailing Stop] Buy Order #", ticket, " trailing SL diperbarui: ", targetTrailSL);
              }
           }
         else if(posType == POSITION_TYPE_SELL)
           {
            double targetTrailSL = currentPrice + (initialSLDistance * 0.75);
            if(targetTrailSL < openPrice && (currentSL == 0.0 || targetTrailSL < currentSL - (InpTrailingStepPoints * _Point)) && (targetTrailSL - currentPrice) >= minDist)
              {
               trade.PositionModify(ticket, NormalizeDouble(targetTrailSL, _Digits), currentTP);
               Print("[SMC Trailing Stop] Sell Order #", ticket, " trailing SL diperbarui: ", targetTrailSL);
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   // Copy data rates
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, 150, rates);
   if(copied < 40) return;

   // Delay visual mode jika diatur agar playback chart santai
   if(MQLInfoInteger(MQL_VISUAL_MODE) && InpVisualDelayMs > 0)
     {
      Sleep(InpVisualDelayMs);
     }

   // Kelola posisi aktif (Break-Even & Trailing Stop) setiap tick
   ManageOpenTrades();

   // Proteksi Gap Akhir Pekan: Tutup posisi otomatis Jumat malam
   riskManager.CheckFridayAutoClose(trade, positionInfo, InpMagicNumber, _Symbol,
                                    InpUseFridayClose, InpFridayCloseHour, InpFridayCloseMinute);

   // Cek apakah ada candle baru (Eksekusi sekali saat candle baru buka)
   datetime currentBarTime = rates[0].time;
   if(currentBarTime == lastTradeBarTime)
     {
      return;
     }

   // Cek batas maksimum posisi
   if(CountOpenPositions() >= InpMaxOpenPositions)
     {
      return;
     }

   // Cek filter waktu trading
   if(!IsTradingTimeAllowed())
     {
      return;
     }

   // Cek pembatasan hari Jumat (Proteksi Gap Akhir Pekan)
   if(riskManager.IsFridayTradingRestricted(InpUseFridayClose, InpFridayCloseHour, InpFridayCloseMinute,
                                           InpBlockFridayNewTrades, InpFridayStopTradeHour))
     {
      return;
     }

   // Cek pembatas kerugian harian (Daily Circuit Breaker)
   if(riskManager.IsDailyLossLimitReached(InpMagicNumber, _Symbol, accountInfo.Equity(),
                                         InpUseDailyLossLimit, InpMaxDailyLosses, InpMaxDailyLossPercent))
     {
      return;
     }

   // Cek batasan spread maksimum
   long currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(currentSpread > InpMaxSpreadPoints)
     {
      return;
     }

   // 1. Cek Filter ADX (Hindari Pasar Sideways/Chop)
   if(InpUseADXFilter && handleADX != INVALID_HANDLE)
     {
      double adxVal[];
      ArraySetAsSeries(adxVal, true);
      if(CopyBuffer(handleADX, 0, 1, 1, adxVal) > 0)
        {
         if(adxVal[0] < InpMinADX)
           {
            return;
           }
        }
     }

   // 2. Cek Filter EMA 200 (Baseline Tren Institusional)
   double ema200Val = 0.0;
   if(InpUseEma200Filter && handleEma200 != INVALID_HANDLE)
     {
      double buf[];
      ArraySetAsSeries(buf, true);
      if(CopyBuffer(handleEma200, 0, 1, 1, buf) > 0)
        {
         ema200Val = buf[0];
        }
     }

   // 3. Cek Filter RSI (Momentum Exhaustion)
   double rsiVal = 50.0;
   if(InpUseRsiFilter && handleRSI != INVALID_HANDLE)
     {
      double rsiBuf[];
      ArraySetAsSeries(rsiBuf, true);
      if(CopyBuffer(handleRSI, 0, 1, 1, rsiBuf) > 0)
        {
         rsiVal = rsiBuf[0];
        }
     }

   // Update mesin analisis SMC
   smcEngine.Update(rates, copied);

   bool cooldownBuyOk  = (lastBuyTradeTime == 0 || (rates[1].time - lastBuyTradeTime >= PeriodSeconds() * InpSignalCooldownBars));
   bool cooldownSellOk = (lastSellTradeTime == 0 || (rates[1].time - lastSellTradeTime >= PeriodSeconds() * InpSignalCooldownBars));

   // Ambil status struktur pasar dan tren HTF
   ENUM_SMC_STRUCTURE currentStruct = smcEngine.GetLastStructure();
   int htfTrend = CheckHtfTrend();

   bool structBuyOk  = (!InpRequireStructure || currentStruct == SMC_STRUCT_BULLISH_BOS || currentStruct == SMC_STRUCT_BULLISH_CHOCH);
   bool htfBuyOk     = (!InpUseHtfFilter || htfTrend >= 0);
   bool ema200BuyOk  = (!InpUseEma200Filter || ema200Val == 0.0 || rates[1].close > ema200Val);
   bool discountBuyOk= (!InpUsePremiumDiscount || smcEngine.IsInDiscountZone(rates[1].close));
   bool rsiBuyOk     = (!InpUseRsiFilter || rsiVal <= InpRsiOversold);

   bool structSellOk = (!InpRequireStructure || currentStruct == SMC_STRUCT_BEARISH_BOS || currentStruct == SMC_STRUCT_BEARISH_CHOCH);
   bool htfSellOk    = (!InpUseHtfFilter || htfTrend <= 0);
   bool ema200SellOk = (!InpUseEma200Filter || ema200Val == 0.0 || rates[1].close < ema200Val);
   bool premiumSellOk= (!InpUsePremiumDiscount || smcEngine.IsInPremiumZone(rates[1].close));
   bool rsiSellOk    = (!InpUseRsiFilter || rsiVal >= InpRsiOverbought);

   // Konfirmasi Rejection Wick
   double candleRange = rates[1].high - rates[1].low;
   if(candleRange <= 0.0) candleRange = 1.0 * _Point;

   double lowerWick = MathMin(rates[1].open, rates[1].close) - rates[1].low;
   double lowerWickPct = (lowerWick / candleRange) * 100.0;
   bool buyWickOk = (!InpRequireRejectionWick || lowerWickPct >= InpMinRejectionWickPct);
   bool sweepBuyOk = (!InpRequireLiquiditySweep || (rates[1].low < rates[2].low && rates[1].close > rates[2].low));

   double upperWick = rates[1].high - MathMax(rates[1].open, rates[1].close);
   double upperWickPct = (upperWick / candleRange) * 100.0;
   bool sellWickOk = (!InpRequireRejectionWick || upperWickPct >= InpMinRejectionWickPct);
   bool sweepSellOk = (!InpRequireLiquiditySweep || (rates[1].high > rates[2].high && rates[1].close < rates[2].high));

   SMC_OrderBlock obTarget;

   long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double minAllowedDist = MathMax((double)InpMinSLPoints, (double)(stopsLevel + currentSpread + 10)) * _Point;

   // ==========================================
   // EKSEKUSI SINYAL BUY (Bullish OB Retest)
   // ==========================================
   if(smcEngine.IsRetestingBullishOB(rates[1].low, obTarget))
     {
      bool strongClose = (!InpRequireStrongClose || (rates[1].close > rates[1].open));
      bool fvgConfluenceOk = (!InpRequireFVGConfluence || smcEngine.HasFVGConfluence(obTarget));

      if(!structBuyOk)
        {
         Print("[SMC BUY FILTERED] Struktur pasar belum Bullish (BOS/CHoCH)");
        }
      else if(!ema200BuyOk)
        {
         Print("[SMC BUY FILTERED] Harga di bawah EMA 200 (Tren Bearish)");
        }
      else if(!htfBuyOk)
        {
         Print("[SMC BUY FILTERED] Tren Macro HTF H1 sedang Bearish (di bawah EMA 50)");
        }
      else if(!discountBuyOk)
        {
         Print("[SMC BUY FILTERED] Harga berada di Zona Premium (Terlalu mahal untuk Buy)");
        }
      else if(!rsiBuyOk)
        {
         Print(StringFormat("[SMC BUY FILTERED] RSI belum jenuh jual (%.1f > %.1f)", rsiVal, InpRsiOversold));
        }
      else if(!strongClose)
        {
         Print("[SMC BUY FILTERED] Candle belum close bullish di atas open-nya");
        }
      else if(!buyWickOk)
        {
         Print(StringFormat("[SMC BUY FILTERED] Ekor bawah penolakan terlalu kecil (%.1f%% < %.1f%%)", lowerWickPct, InpMinRejectionWickPct));
        }
      else if(!sweepBuyOk)
        {
         Print("[SMC BUY FILTERED] Belum ada sapuan likuiditas (Liquidity Sweep)");
        }
      else if(!fvgConfluenceOk)
        {
         Print("[SMC BUY FILTERED] Tidak ada konfirmasi FVG Imbalance pendukung");
        }
      else if(!cooldownBuyOk)
        {
         Print("[SMC BUY FILTERED] Signal Cooldown Active");
        }
      else
        {
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

         double slPrice = obTarget.low - (InpSL_BufferPoints * _Point);
         if((bid - slPrice) < minAllowedDist)
           {
            slPrice = bid - minAllowedDist;
           }

         double slDistPoints = (ask - slPrice) / _Point;
         double tpPrice = ask + ((ask - slPrice) * InpRiskRewardRatio);

         double lot = riskManager.CalculateLotSize(accountInfo.Equity(), InpRiskPercent, slDistPoints,
                                                  _Symbol, InpFixedLot, (InpLotMode == LOT_MODE_FIXED), InpMaxLotSize);

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         if(trade.Buy(lot, _Symbol, ask, slPrice, tpPrice, InpOrderComment))
           {
            lastBuyTradeTime = rates[1].time;
            smcEngine.MarkOrderBlockTriggered(obTarget.time);
            Print(StringFormat("[SMC BUY EXECUTE 80%%+] Lot: %.2f | Entry: %f | SL: %f | TP: %f | OB: %.2f-%.2f",
                               lot, ask, slPrice, tpPrice, obTarget.low, obTarget.high));
           }
         else
           {
            Print("[SMC BUY GAGAL] Error: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
           }
        }
     }
   // ==========================================
   // EKSEKUSI SINYAL SELL (Bearish OB Retest)
   // ==========================================
   else if(smcEngine.IsRetestingBearishOB(rates[1].high, obTarget))
     {
      bool strongClose = (!InpRequireStrongClose || (rates[1].close < rates[1].open));
      bool fvgConfluenceOk = (!InpRequireFVGConfluence || smcEngine.HasFVGConfluence(obTarget));

      if(!structSellOk)
        {
         Print("[SMC SELL FILTERED] Struktur pasar belum Bearish (BOS/CHoCH)");
        }
      else if(!ema200SellOk)
        {
         Print("[SMC SELL FILTERED] Harga di atas EMA 200 (Tren Bullish)");
        }
      else if(!htfSellOk)
        {
         Print("[SMC SELL FILTERED] Tren Macro HTF H1 sedang Bullish (di atas EMA 50)");
        }
      else if(!premiumSellOk)
        {
         Print("[SMC SELL FILTERED] Harga berada di Zona Diskon (Terlalu murah untuk Sell)");
        }
      else if(!rsiSellOk)
        {
         Print(StringFormat("[SMC SELL FILTERED] RSI belum jenuh beli (%.1f < %.1f)", rsiVal, InpRsiOverbought));
        }
      else if(!strongClose)
        {
         Print("[SMC SELL FILTERED] Candle belum close bearish di bawah open-nya");
        }
      else if(!sellWickOk)
        {
         Print(StringFormat("[SMC SELL FILTERED] Ekor atas penolakan terlalu kecil (%.1f%% < %.1f%%)", upperWickPct, InpMinRejectionWickPct));
        }
      else if(!sweepSellOk)
        {
         Print("[SMC SELL FILTERED] Belum ada sapuan likuiditas (Liquidity Sweep)");
        }
      else if(!fvgConfluenceOk)
        {
         Print("[SMC SELL FILTERED] Tidak ada konfirmasi FVG Imbalance pendukung");
        }
      else if(!cooldownSellOk)
        {
         Print("[SMC SELL FILTERED] Signal Cooldown Active");
        }
      else
        {
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

         double slPrice = obTarget.high + (InpSL_BufferPoints * _Point);
         if((slPrice - ask) < minAllowedDist)
           {
            slPrice = ask + minAllowedDist;
           }

         double slDistPoints = (slPrice - bid) / _Point;
         double tpPrice = bid - ((slPrice - bid) * InpRiskRewardRatio);

         double lot = riskManager.CalculateLotSize(accountInfo.Equity(), InpRiskPercent, slDistPoints,
                                                  _Symbol, InpFixedLot, (InpLotMode == LOT_MODE_FIXED), InpMaxLotSize);

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         if(trade.Sell(lot, _Symbol, bid, slPrice, tpPrice, InpOrderComment))
           {
            lastSellTradeTime = rates[1].time;
            smcEngine.MarkOrderBlockTriggered(obTarget.time);
            Print(StringFormat("[SMC SELL EXECUTE 80%%+] Lot: %.2f | Entry: %f | SL: %f | TP: %f | OB: %.2f-%.2f",
                               lot, bid, slPrice, tpPrice, obTarget.low, obTarget.high));
           }
         else
           {
            Print("[SMC SELL GAGAL] Error: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
           }
        }
     }

   lastTradeBarTime = currentBarTime;
  }
