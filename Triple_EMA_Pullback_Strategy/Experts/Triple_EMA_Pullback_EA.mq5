//+------------------------------------------------------------------+
//|                                     Triple_EMA_Pullback_EA.mq5   |
//|                        Triple EMA Pullback Expert Advisor        |
//|                                  Copyright 2026, XAUUSD Trader   |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.00"
#property description "Auto Trading EA Triple EMA Pullback (8, 21, 125) untuk XAUUSD & Forex dengan Risk Management Pro"

// Include pustaka standar MQL5 untuk eksekusi order
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\AccountInfo.mqh>

// Include modul strategi
#include "..\Include\CandlePatterns.mqh"
#include "..\Include\MarketStructure.mqh"

//+------------------------------------------------------------------+
//| Enum Mode Stop Loss                                              |
//+------------------------------------------------------------------+
enum ENUM_SL_MODE
  {
   SL_SWING_CANDLE,  // Swing Low / High Candle Setup + Buffer
   SL_ATR_BASED,     // Berbasis Kelipatan ATR
   SL_FIXED_POINTS   // Fixed Points / Pips
  };

//+------------------------------------------------------------------+
//| Enum Mode Money Management                                       |
//+------------------------------------------------------------------+
enum ENUM_LOT_MODE
  {
   LOT_FIXED,        // Fixed Lot
   LOT_RISK_PERCENT  // Dinamis Berdasarkan % Risk dari Equity
  };

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== Pengaturan Indikator Moving Average ==="
input int                  InpEMA8_Period          = 8;             // Periode EMA 8 (Fast)
input int                  InpEMA21_Period         = 21;            // Periode EMA 21 (Pullback Dynamic S/R)
input int                  InpEMA125_Period        = 125;           // Periode EMA 125 (Major Baseline Trend)

input group "=== Filter False Signal & Anti-Spam ==="
input int                  InpSignalCooldownBars   = 5;             // Jeda Minimal Antar Sinyal (Bars Anti-Spam)
input bool                 InpRequireStrongClose   = true;          // Wajib Close Kuat Menembus EMA 8
input bool                 InpRequireEmaSlope      = true;          // Wajib Slope EMA 8 Searah Tren
input bool                 InpUseStructureFilter   = true;          // Wajib Struktur HH-HL (Buy) atau LH-LL (Sell)
input bool                 InpUseChopFilter        = true;          // Filter EMA 8 & 21 Sering Bolak-balik (Chop)
input int                  InpChopBars             = 15;            // Lookback Cek Chop EMA
input int                  InpMaxEmaCrosses        = 2;             // Maksimal Cross EMA dalam Lookback
input bool                 InpUseWhipsawFilter     = true;          // Filter Whipsaw EMA 125
input int                  InpWhipsawBars          = 20;            // Lookback Cek Whipsaw EMA 125
input int                  InpMaxWhipsawCrosses    = 2;             // Maksimal Tembus EMA 125
input bool                 InpUseOverextendFilter  = true;          // Filter Candle Terlalu Jauh dari EMA
input double               InpMaxAtrMultiplier     = 2.0;           // Toleransi Jarak Jauh (x ATR 14)
input int                  InpAtrPeriod            = 14;            // Periode ATR

input group "=== Filter Multi-Timeframe (HTF Trend Alignment) ==="
input bool                 InpUseMTFFilter         = true;          // Aktifkan Filter Multi-Timeframe (HTF)
input ENUM_TIMEFRAMES      InpHTFTimeframe         = PERIOD_H1;     // Timeframe Tren Utama (Default: H1)
input int                  InpHTF_EMA_Period       = 50;            // Periode EMA HTF (Macro Baseline)

input group "=== Money Management & Lot Size ==="
input ENUM_LOT_MODE        InpLotMode              = LOT_RISK_PERCENT; // Mode Kalkulasi Lot
input double               InpFixedLot             = 0.01;          // Fixed Lot Size (jika LOT_FIXED)
input double               InpRiskPercent          = 1.0;           // Resiko per Trade (% Equity)
input double               InpMaxLotSize           = 5.0;           // Maksimal Lot Eksekusi
input int                  InpMaxOpenPositions     = 1;             // Maksimal Posisi Terbuka Bersamaan

input group "=== Stop Loss & Take Profit ==="
input ENUM_SL_MODE         InpSLMode               = SL_SWING_CANDLE; // Mode Stop Loss
input double               InpSL_AtrMultiplier     = 1.5;           // Multiplier ATR untuk SL (jika SL_ATR_BASED)
input int                  InpSL_FixedPoints       = 300;           // SL Points (jika SL_FIXED_POINTS)
input int                  InpSL_BufferPoints      = 50;            // Buffer Tambahan SL Candle (Points)
input double               InpRiskRewardRatio      = 2.0;           // Target Risk:Reward (misal 1:2.0)
input int                  InpMinSLPoints          = 150;           // Batas Minimal SL Points (Proteksi Gold)

input group "=== Proteksi Profit: Break-Even & Trailing ==="
input bool                 InpUseBreakEven         = true;          // Aktifkan Auto Break-Even (BEP)
input double               InpBE_TriggerRR         = 1.2;           // Pindahkan SL ke BEP saat Profit mencapai 1:X R:R
input int                  InpBE_LockProfitPoints  = 20;            // Profit Terkunci di atas Entry (Points)
input bool                 InpUseTrailingStop      = true;          // Aktifkan Trailing Stop
input double               InpTrailingStartRR      = 1.4;           // Trailing Stop Baru Aktif Setelah Profit Mencapai 1:X R:R
input bool                 InpTrailingByEMA21      = true;          // Trailing Mengikuti Garis EMA 21
input double               InpTrailingAtrMult      = 1.5;           // Trailing Jarak ATR (jika bukan EMA 21)

input group "=== Filter Kekuatan Tren (ADX Momentum) ==="
input bool                 InpUseADXFilter         = true;          // Wajib Tren Kuat (ADX Filter)
input int                  InpADX_Period           = 14;            // Periode ADX
input double               InpMinADXLevel          = 20.0;          // Minimal ADX Level (Di bawah 20 = Sideways Flat)

input group "=== Proteksi Kerugian Harian (Circuit Breaker) ==="
input bool                 InpUseDailyLossLimit    = true;          // Batasi Kerugian Harian (Stop Trading Hari Ini)
input int                  InpMaxDailyLosses       = 2;             // Maksimal Trade Kalah per Hari (Stop jika tercapai)
input double               InpMaxDailyLossPercent  = 3.0;           // Maksimal % Kerugian Harian dari Equity

input group "=== Filter Waktu & Jam Trading (Broker Time) ==="
input bool                 InpUseTimeFilter        = true;          // Batasi Jam Trading
input int                  InpStartHour            = 8;             // Jam Mulai Trading (Sesi London)
input int                  InpEndHour              = 21;            // Jam Akhir Trading (Sesi New York)
input int                  InpMaxSpreadPoints      = 40;            // Maksimal Spread Diizinkan (Points)

input group "=== Proteksi Gap Akhir Pekan (Friday Auto-Close) ==="
input bool                 InpUseFridayClose       = true;          // Aktifkan Auto-Close Jumat Malam (Anti-Gap Weekend)
input int                  InpFridayCloseHour      = 21;            // Jam Auto-Close Jumat Malam (Broker Time)
input int                  InpFridayCloseMinute    = 30;            // Menit Auto-Close Jumat Malam (Broker Time)
input bool                 InpBlockFridayNewTrades = true;          // Blokir Sinyal Baru Jumat Sore/Malam
input int                  InpFridayStopTradeHour  = 18;            // Jam Mulai Blokir Sinyal Baru di Hari Jumat

input group "=== Kecepatan Simulasi Visual Mode ==="
input int                  InpVisualDelayMs        = 0;             // Delay Visual Per Tick/Bar (ms, 0=Normal, 50-200ms=Santai)

input group "=== EA System ID ==="
input ulong                InpMagicNumber          = 8821125;       // Magic Number Unik
input string               InpOrderComment         = "TripleEMA_XAU"; // Komentar Order

//+------------------------------------------------------------------+
//| Objek Trading & Indikator                                        |
//+------------------------------------------------------------------+
CTrade                 trade;
CPositionInfo          positionInfo;
CAccountInfo           accountInfo;

CCandlePatternDetector patternDetector;
CMarketStructure       structureAnalyzer;

int                    handle_ema8;
int                    handle_ema21;
int                    handle_ema125;
int                    handle_atr;
int                    handle_htf_ema;
int                    handle_adx;

ENUM_TIMEFRAMES        effectiveHTF      = PERIOD_H1;
datetime               lastTradeBarTime  = 0;
datetime               lastBuyTradeTime  = 0;
datetime               lastSellTradeTime = 0;

int                    dailyLossCount    = 0;
double                 dailyLossAmount   = 0.0;
int                    lastCalculatedDay = -1;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   // Inisialisasi Trade object
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetDeviationInPoints(20);

   // Inisialisasi Handle Indikator
   handle_ema8   = iMA(_Symbol, _Period, InpEMA8_Period, 0, MODE_EMA, PRICE_CLOSE);
   handle_ema21  = iMA(_Symbol, _Period, InpEMA21_Period, 0, MODE_EMA, PRICE_CLOSE);
   handle_ema125 = iMA(_Symbol, _Period, InpEMA125_Period, 0, MODE_EMA, PRICE_CLOSE);
   handle_atr    = iATR(_Symbol, _Period, InpAtrPeriod);
   handle_adx    = iADX(_Symbol, _Period, InpADX_Period);

   if(handle_ema8 == INVALID_HANDLE || handle_ema21 == INVALID_HANDLE ||
      handle_ema125 == INVALID_HANDLE || handle_atr == INVALID_HANDLE ||
      handle_adx == INVALID_HANDLE)
     {
      Print("[EA Error] Gagal memuat handle indikator MQL5!");
      return(INIT_FAILED);
     }

   // Konfigurasi Higher Timeframe (HTF) otomatis jika TF chart sama atau lebih tinggi dari target HTF
   effectiveHTF = InpHTFTimeframe;
   if(_Period >= effectiveHTF)
     {
      if(_Period == PERIOD_M1) effectiveHTF = PERIOD_M15;
      else if(_Period <= PERIOD_M15) effectiveHTF = PERIOD_H1;
      else if(_Period == PERIOD_M30) effectiveHTF = PERIOD_H4;
      else if(_Period == PERIOD_H1) effectiveHTF = PERIOD_H4;
      else if(_Period == PERIOD_H4) effectiveHTF = PERIOD_D1;
      else effectiveHTF = PERIOD_W1;
     }

   if(InpUseMTFFilter)
     {
      handle_htf_ema = iMA(_Symbol, effectiveHTF, InpHTF_EMA_Period, 0, MODE_EMA, PRICE_CLOSE);
     }
   else
     {
      handle_htf_ema = INVALID_HANDLE;
     }

   // Konfigurasi struktur pasar & filter
   structureAnalyzer.Configure(50, InpChopBars, InpMaxEmaCrosses, InpWhipsawBars, InpMaxWhipsawCrosses, InpMaxAtrMultiplier);

   Print(StringFormat("[EA Started] Triple EMA Pullback System aktif pada %s %s (HTF: %s) | Magic: %d",
                      _Symbol, EnumToString(_Period), EnumToString(effectiveHTF), InpMagicNumber));

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   IndicatorRelease(handle_ema8);
   IndicatorRelease(handle_ema21);
   IndicatorRelease(handle_ema125);
   IndicatorRelease(handle_atr);
   if(handle_adx != INVALID_HANDLE)
     {
      IndicatorRelease(handle_adx);
      handle_adx = INVALID_HANDLE;
     }
   if(handle_htf_ema != INVALID_HANDLE)
     {
      IndicatorRelease(handle_htf_ema);
      handle_htf_ema = INVALID_HANDLE;
     }
   Print("[EA Stopped] Triple EMA Pullback EA dimatikan. Reason: ", reason);
  }

//+------------------------------------------------------------------+
//| Perbarui Statistik Kerugian Harian (Circuit Breaker)             |
//+------------------------------------------------------------------+
void UpdateDailyStats()
  {
   MqlDateTime dt;
   TimeCurrent(dt);

   // Reset jika hari berganti
   if(dt.day != lastCalculatedDay)
     {
      dailyLossCount    = 0;
      dailyLossAmount   = 0.0;
      lastCalculatedDay = dt.day;
     }

   datetime dayStart = StringToTime(StringFormat("%04d.%02d.%02d 00:00", dt.year, dt.mon, dt.day));
   if(!HistorySelect(dayStart, TimeCurrent())) return;

   dailyLossCount  = 0;
   dailyLossAmount = 0.0;
   int totalDeals  = HistoryDealsTotal();

   for(int i = 0; i < totalDeals; i++)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket > 0)
        {
         if(HistoryDealGetString(ticket, DEAL_SYMBOL) == _Symbol &&
            HistoryDealGetInteger(ticket, DEAL_MAGIC) == InpMagicNumber &&
            HistoryDealGetInteger(ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
           {
            double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) + 
                            HistoryDealGetDouble(ticket, DEAL_SWAP) + 
                            HistoryDealGetDouble(ticket, DEAL_COMMISSION);
            if(profit < -0.01)
              {
               dailyLossCount++;
               dailyLossAmount += MathAbs(profit);
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Cek Apakah Batas Kerugian Harian Telah Tercapai                  |
//+------------------------------------------------------------------+
bool IsDailyLossLimitReached()
  {
   if(!InpUseDailyLossLimit) return false;

   UpdateDailyStats();

   if(dailyLossCount >= InpMaxDailyLosses)
     {
      Print(StringFormat("[Daily Circuit Breaker] Batas kalah harian (%d trade) tercapai. Trading dijeda hingga besok.",
                         dailyLossCount));
      return true;
     }

   double maxAllowedLoss = accountInfo.Equity() * (InpMaxDailyLossPercent / 100.0);
   if(dailyLossAmount >= maxAllowedLoss && maxAllowedLoss > 0.0)
     {
      Print(StringFormat("[Daily Circuit Breaker] Batas nominal loss harian ($%.2f / $%.2f) tercapai. Trading dijeda hingga besok.",
                         dailyLossAmount, maxAllowedLoss));
      return true;
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Jam Sekarang Diizinkan Trading                        |
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
//| Cek Apakah Trading Jumat Dibatasi (Proteksi Gap Akhir Pekan)     |
//+------------------------------------------------------------------+
bool IsFridayTradingRestricted()
  {
   if(!InpUseFridayClose) return false;

   MqlDateTime dt;
   TimeCurrent(dt);

   if(dt.day_of_week == 5) // 5 = Hari Jumat
     {
      // Jika sudah melewati jam auto-close
      if(dt.hour > InpFridayCloseHour || (dt.hour == InpFridayCloseHour && dt.min >= InpFridayCloseMinute))
         return true;

      // Jika disetel untuk blokir entri baru setelah jam tertentu di hari Jumat
      if(InpBlockFridayNewTrades && dt.hour >= InpFridayStopTradeHour)
         return true;
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Tutup Semua Posisi Terbuka di Hari Jumat Malam (Anti-Gap Weekend)|
//+------------------------------------------------------------------+
void CheckFridayAutoClose()
  {
   if(!InpUseFridayClose) return;

   MqlDateTime dt;
   TimeCurrent(dt);

   if(dt.day_of_week == 5) // 5 = Hari Jumat
     {
      if(dt.hour > InpFridayCloseHour || (dt.hour == InpFridayCloseHour && dt.min >= InpFridayCloseMinute))
        {
         for(int i = PositionsTotal() - 1; i >= 0; i--)
           {
            if(!positionInfo.SelectByIndex(i)) continue;
            if(positionInfo.Symbol() != _Symbol || positionInfo.Magic() != InpMagicNumber) continue;

            ulong ticket = positionInfo.Ticket();
            if(trade.PositionClose(ticket))
              {
               Print(StringFormat("[Friday Auto-Close] Posisi #%I64u berhasil ditutup sebelum penutupan pasar akhir pekan.", ticket));
              }
            else
              {
               Print(StringFormat("[Friday Auto-Close Error] Gagal menutup posisi #%I64u: %s", ticket, trade.ResultRetcodeDescription()));
              }
           }
        }
     }
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
//| Hitung Ukuran Lot Berdasarkan Money Management                   |
//+------------------------------------------------------------------+
double CalculateLotSize(double slDistancePoints)
  {
   if(InpLotMode == LOT_FIXED)
     {
      return InpFixedLot;
     }

   double equity = accountInfo.Equity();
   double riskMoney = equity * (InpRiskPercent / 100.0);

   // Nilai tick per point
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double pointVal  = (tickSize > 0.0) ? (tickValue / tickSize) * _Point : 1.0;

   if(slDistancePoints <= 0 || pointVal <= 0) return SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);

   double calculatedLot = riskMoney / (slDistancePoints * pointVal);

   // Sesuaikan dengan batas lot broker
   double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = MathMin(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX), InpMaxLotSize);

   int lotDigits = 2;
   if(stepLot <= 0.001) lotDigits = 3;
   else if(stepLot >= 0.1) lotDigits = 1;

   calculatedLot = MathFloor(calculatedLot / stepLot) * stepLot;
   calculatedLot = MathMax(minLot, MathMin(maxLot, calculatedLot));
   calculatedLot = NormalizeDouble(calculatedLot, lotDigits);

   return calculatedLot;
  }

//+------------------------------------------------------------------+
//| Kelola Break-Even dan Trailing Stop                              |
//+------------------------------------------------------------------+
void ManageOpenTrades(double currentEma21, double currentAtr)
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

      // Jarak awal SL dalam points
      double initialSLDistance = MathAbs(openPrice - currentSL);
      if(initialSLDistance <= 0.0) initialSLDistance = 200 * _Point;

      // Jarak minimum stop level broker (proteksi error 10016)
      long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
      double minDist  = MathMax(stopsLevel * _Point, 15 * _Point);

      // Hitung profit distance saat ini dan rasio R:R
      double profitDistance = 0.0;
      if(posType == POSITION_TYPE_BUY) profitDistance = currentPrice - openPrice;
      else if(posType == POSITION_TYPE_SELL) profitDistance = openPrice - currentPrice;
      double currentR = (initialSLDistance > 0.0) ? profitDistance / initialSLDistance : 0.0;

      // 1. AUTO BREAK-EVEN (Aktif saat mencapai InpBE_TriggerRR, default 1.2R)
      if(InpUseBreakEven && currentR >= InpBE_TriggerRR)
        {
         if(posType == POSITION_TYPE_BUY && currentSL < openPrice)
           {
            double newSL = NormalizeDouble(openPrice + (InpBE_LockProfitPoints * _Point), _Digits);
            if((currentPrice - newSL) >= minDist)
              {
               trade.PositionModify(ticket, newSL, currentTP);
               Print("[Auto BEP] Buy Order #", ticket, " SL dipindahkan ke Break-Even: ", newSL);
               continue;
              }
           }
         else if(posType == POSITION_TYPE_SELL && (currentSL > openPrice || currentSL == 0.0))
           {
            double newSL = NormalizeDouble(openPrice - (InpBE_LockProfitPoints * _Point), _Digits);
            if((newSL - currentPrice) >= minDist)
              {
               trade.PositionModify(ticket, newSL, currentTP);
               Print("[Auto BEP] Sell Order #", ticket, " SL dipindahkan ke Break-Even: ", newSL);
               continue;
              }
           }
        }

      // 2. TRAILING STOP (Baru aktif setelah profit mencapai InpTrailingStartRR, default 1.4R)
      if(InpUseTrailingStop && currentR >= InpTrailingStartRR)
        {
         if(posType == POSITION_TYPE_BUY)
           {
            double targetTrailSL = 0.0;
            if(InpTrailingByEMA21)
              {
               targetTrailSL = currentEma21 - (20 * _Point);
              }
            else
              {
               targetTrailSL = currentPrice - (InpTrailingAtrMult * currentAtr);
              }

            // Validasi Trailing hanya boleh naik mengunci profit dan mematuhi minDist broker
            if(targetTrailSL > openPrice && targetTrailSL > currentSL + (15 * _Point) && (currentPrice - targetTrailSL) >= minDist)
              {
               trade.PositionModify(ticket, NormalizeDouble(targetTrailSL, _Digits), currentTP);
               Print("[Trailing Stop] Buy Order #", ticket, " trailing SL diperbarui: ", targetTrailSL);
              }
           }
         else if(posType == POSITION_TYPE_SELL)
           {
            double targetTrailSL = 0.0;
            if(InpTrailingByEMA21)
              {
               targetTrailSL = currentEma21 + (20 * _Point);
              }
            else
              {
               targetTrailSL = currentPrice + (InpTrailingAtrMult * currentAtr);
              }

            // Validasi Trailing hanya boleh turun mengunci profit dan mematuhi minDist broker
            if(targetTrailSL < openPrice && (currentSL == 0.0 || targetTrailSL < currentSL - (15 * _Point)) && (targetTrailSL - currentPrice) >= minDist)
              {
               trade.PositionModify(ticket, NormalizeDouble(targetTrailSL, _Digits), currentTP);
               Print("[Trailing Stop] Sell Order #", ticket, " trailing SL diperbarui: ", targetTrailSL);
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
   // Copy data rates candle
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, 60, rates);
   if(copied < 35) return;

   // Salin EMA series
   double ema8[], ema21[], ema125[], atr[];
   ArraySetAsSeries(ema8, true);
   ArraySetAsSeries(ema21, true);
   ArraySetAsSeries(ema125, true);
   ArraySetAsSeries(atr, true);

   CopyBuffer(handle_ema8, 0, 0, 30, ema8);
   CopyBuffer(handle_ema21, 0, 0, 30, ema21);
   CopyBuffer(handle_ema125, 0, 0, 30, ema125);
   CopyBuffer(handle_atr, 0, 0, 5, atr);

   double currentAtr = (ArraySize(atr) > 1) ? atr[1] : 1.0 * _Point;

   // Delay visual mode jika diatur agar pergerakan playback chart santai
   if(MQLInfoInteger(MQL_VISUAL_MODE) && InpVisualDelayMs > 0)
     {
      Sleep(InpVisualDelayMs);
     }

   // Kelola posisi aktif (Break-Even & Trailing Stop) pada setiap tick
   ManageOpenTrades(ema21[0], currentAtr);

   // Proteksi Gap Akhir Pekan: Tutup posisi otomatis jika sudah masuk Jumat malam
   CheckFridayAutoClose();

   // Cek apakah ada candle baru (Sinyal dieksekusi sekali saat candle baru buka)
   datetime currentBarTime = rates[0].time;
   if(currentBarTime == lastTradeBarTime)
     {
      return; // Sudah diperiksa pada candle ini
     }

   // Cek batas maksimum posisi
   if(CountOpenPositions() >= InpMaxOpenPositions)
     {
      return;
     }

   // Cek filter waktu
   if(!IsTradingTimeAllowed())
     {
      return;
     }

   // Cek proteksi akhir pekan (Friday Auto-Close & Block New Trades)
   if(IsFridayTradingRestricted())
     {
      return;
     }

   // Cek batas kerugian harian (Daily Circuit Breaker)
   if(IsDailyLossLimitReached())
     {
      return;
     }

   // Cek batasan spread maksimum
   long currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(currentSpread > InpMaxSpreadPoints)
     {
      Print(StringFormat("[Filter Spread] Spread saat ini (%d pts) melebihi batas toleransi (%d pts)",
                         currentSpread, InpMaxSpreadPoints));
      return;
     }

   // Candle [1] adalah candle konfirmasi yang baru saja tertutup sempurna
   double e8_1   = ema8[1];
   double e21_1  = ema21[1];
   double e125_1 = ema125[1];

   // Deteksi Pola Price Action Candlestick
   ENUM_CANDLE_PATTERN bullPattern = patternDetector.DetectBullishPattern(rates, 1, e8_1, e21_1, e125_1);
   ENUM_CANDLE_PATTERN bearPattern = patternDetector.DetectBearishPattern(rates, 1, e8_1, e21_1, e125_1);

   // Syarat Tambahan: Strong Close & EMA Slope
   bool strongCloseBuy  = (!InpRequireStrongClose || (rates[1].close > e8_1 && rates[1].close > rates[1].open));
   bool strongCloseSell = (!InpRequireStrongClose || (rates[1].close < e8_1 && rates[1].close < rates[1].open));
   bool slopeBuyOk      = (!InpRequireEmaSlope || (e8_1 > ema8[2]));
   bool slopeSellOk     = (!InpRequireEmaSlope || (e8_1 < ema8[2]));
   bool cooldownBuyOk   = (lastBuyTradeTime == 0 || (rates[1].time - lastBuyTradeTime >= PeriodSeconds() * InpSignalCooldownBars));
   bool cooldownSellOk  = (lastSellTradeTime == 0 || (rates[1].time - lastSellTradeTime >= PeriodSeconds() * InpSignalCooldownBars));

   // Evaluasi Filter ADX (Kekuatan Tren)
   double adxBuf[];
   ArraySetAsSeries(adxBuf, true);
   int cAdx = CopyBuffer(handle_adx, 0, 0, 3, adxBuf);
   bool adxTrendOk = (!InpUseADXFilter || (cAdx >= 2 && adxBuf[1] >= InpMinADXLevel));

   // Evaluasi Tren Multi-Timeframe (HTF)
   bool htfBullish = true;
   bool htfBearish = true;

   if(InpUseMTFFilter && handle_htf_ema != INVALID_HANDLE)
     {
      double htfEmaBuf[];
      ArraySetAsSeries(htfEmaBuf, true);
      MqlRates htfRatesBuf[];
      ArraySetAsSeries(htfRatesBuf, true);

      int cEma   = CopyBuffer(handle_htf_ema, 0, 0, 5, htfEmaBuf);
      int cRates = CopyRates(_Symbol, effectiveHTF, 0, 5, htfRatesBuf);

      if(cEma >= 2 && cRates >= 2)
        {
         if(htfRatesBuf[1].close > htfEmaBuf[1])
           {
            htfBullish = true;
            htfBearish = false;
           }
         else if(htfRatesBuf[1].close < htfEmaBuf[1])
           {
            htfBullish = false;
            htfBearish = true;
           }
        }
      else
        {
         Print("[MTF Info] Menunggu sinkronisasi data HTF...");
         return;
        }
     }

   // ==========================================
   // EKSEKUSI SINYAL BUY
   // ==========================================
   if(bullPattern != PATTERN_NONE)
     {
      // 1. Syarat Tren: Harga di atas EMA 125 dan EMA 8 di atas EMA 21
      bool trendBullish = (rates[1].close > e125_1 && e8_1 > e21_1 && rates[1].low > e125_1);

      if(!trendBullish)
        {
         Print("[BUY FILTERED] Trend/EMA Misalignment");
        }
      else if(InpUseMTFFilter && !htfBullish)
        {
         Print(StringFormat("[BUY FILTERED] HTF (%s) Bearish (Macro Filter Active)", EnumToString(effectiveHTF)));
        }
      else if(!strongCloseBuy)
        {
         Print("[BUY FILTERED] Weak Close (Candle harus close bullish di atas EMA 8)");
        }
      else if(!slopeBuyOk)
        {
         Print("[BUY FILTERED] Slope EMA 8 Menukik Turun");
        }
      else if(!adxTrendOk)
        {
         Print(StringFormat("[BUY FILTERED] ADX Tren Lemah (< %.1f, Sideways)", InpMinADXLevel));
        }
      else if(!cooldownBuyOk)
        {
         Print("[BUY FILTERED] Signal Cooldown Active");
        }
      else
        {
         // 2. Filter False Signal & Struktur (Wajib HH-HL)
         ENUM_FILTER_RESULT res = structureAnalyzer.ValidateBuyFilters(
            rates, copied, ema8, ema21, ema125, currentAtr, InpUseStructureFilter, 1
         );

         if(res == FILTER_PASS)
           {
            // Hitung Stop Loss
            double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
            double slPrice = 0.0;

             if(InpSLMode == SL_SWING_CANDLE)
               {
                double lowestLow = MathMin(rates[1].low, MathMin(rates[2].low, rates[3].low));
                slPrice = lowestLow - (InpSL_BufferPoints * _Point);
               }
            else if(InpSLMode == SL_ATR_BASED)
              {
               slPrice = ask - (InpSL_AtrMultiplier * currentAtr);
              }
            else
              {
               slPrice = ask - (InpSL_FixedPoints * _Point);
              }

            // Pastikan jarak SL memenuhi standar minimal
            double slDistPoints = (ask - slPrice) / _Point;
            if(slDistPoints < InpMinSLPoints)
              {
               slPrice = ask - (InpMinSLPoints * _Point);
               slDistPoints = InpMinSLPoints;
              }

            // Hitung Take Profit berbasis Risk:Reward
            double tpPrice = ask + ((ask - slPrice) * InpRiskRewardRatio);

            // Hitung Lot Sizing
            double lot = CalculateLotSize(slDistPoints);

            slPrice = NormalizeDouble(slPrice, _Digits);
            tpPrice = NormalizeDouble(tpPrice, _Digits);

            string patternStr = GetPatternName(bullPattern);
            string comment = StringFormat("%s_%s", InpOrderComment, patternStr);

            if(trade.Buy(lot, _Symbol, ask, slPrice, tpPrice, comment))
              {
               lastBuyTradeTime = rates[1].time;
               Print(StringFormat("[ORDER BUY SUKSES] Lot: %.2f | Ask: %f | SL: %f | TP: %f | Pattern: %s",
                                  lot, ask, slPrice, tpPrice, patternStr));
              }
            else
              {
               Print("[ORDER BUY GAGAL] Error: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
              }
           }
         else
           {
            Print("[BUY FILTERED] ", FilterResultToString(res));
           }
        }
     }

   // ==========================================
   // EKSEKUSI SINYAL SELL
   // ==========================================
   else if(bearPattern != PATTERN_NONE)
     {
      // 1. Syarat Tren: Harga di bawah EMA 125 dan EMA 8 di bawah EMA 21
      bool trendBearish = (rates[1].close < e125_1 && e8_1 < e21_1 && rates[1].high < e125_1);

      if(!trendBearish)
        {
         Print("[SELL FILTERED] Trend/EMA Misalignment");
        }
      else if(InpUseMTFFilter && !htfBearish)
        {
         Print(StringFormat("[SELL FILTERED] HTF (%s) Bullish (Macro Filter Active)", EnumToString(effectiveHTF)));
        }
      else if(!strongCloseSell)
        {
         Print("[SELL FILTERED] Weak Close (Candle harus close bearish di bawah EMA 8)");
        }
      else if(!slopeSellOk)
        {
         Print("[SELL FILTERED] Slope EMA 8 Mengarah Naik");
        }
      else if(!adxTrendOk)
        {
         Print(StringFormat("[SELL FILTERED] ADX Tren Lemah (< %.1f, Sideways)", InpMinADXLevel));
        }
      else if(!cooldownSellOk)
        {
         Print("[SELL FILTERED] Signal Cooldown Active");
        }
      else
        {
         // 2. Filter False Signal & Struktur (Wajib LH-LL)
         ENUM_FILTER_RESULT res = structureAnalyzer.ValidateSellFilters(
            rates, copied, ema8, ema21, ema125, currentAtr, InpUseStructureFilter, 1
         );

         if(res == FILTER_PASS)
           {
            // Hitung Stop Loss
            double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
            double slPrice = 0.0;

             if(InpSLMode == SL_SWING_CANDLE)
               {
                double highestHigh = MathMax(rates[1].high, MathMax(rates[2].high, rates[3].high));
                slPrice = highestHigh + (InpSL_BufferPoints * _Point);
               }
            else if(InpSLMode == SL_ATR_BASED)
              {
               slPrice = bid + (InpSL_AtrMultiplier * currentAtr);
              }
            else
              {
               slPrice = bid + (InpSL_FixedPoints * _Point);
              }

            // Pastikan jarak SL memenuhi standar minimal
            double slDistPoints = (slPrice - bid) / _Point;
            if(slDistPoints < InpMinSLPoints)
              {
               slPrice = bid + (InpMinSLPoints * _Point);
               slDistPoints = InpMinSLPoints;
              }

            // Hitung Take Profit berbasis Risk:Reward
            double tpPrice = bid - ((slPrice - bid) * InpRiskRewardRatio);

            // Hitung Lot Sizing
            double lot = CalculateLotSize(slDistPoints);

            slPrice = NormalizeDouble(slPrice, _Digits);
            tpPrice = NormalizeDouble(tpPrice, _Digits);

            string patternStr = GetPatternName(bearPattern);
            string comment = StringFormat("%s_%s", InpOrderComment, patternStr);

            if(trade.Sell(lot, _Symbol, bid, slPrice, tpPrice, comment))
              {
               lastSellTradeTime = rates[1].time;
               Print(StringFormat("[ORDER SELL SUKSES] Lot: %.2f | Bid: %f | SL: %f | TP: %f | Pattern: %s",
                                  lot, bid, slPrice, tpPrice, patternStr));
              }
            else
              {
               Print("[ORDER SELL GAGAL] Error: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
              }
           }
         else
           {
            Print("[SELL FILTERED] ", FilterResultToString(res));
           }
        }
     }

   // Tandai bar saat ini telah selesai dievaluasi agar tidak berulang setiap tick
   lastTradeBarTime = currentBarTime;
  }
//+------------------------------------------------------------------+
