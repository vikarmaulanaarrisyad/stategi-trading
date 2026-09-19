//+------------------------------------------------------------------+
//|                                     Triple_EMA_Pullback_EA.mq5   |
//|                        Triple EMA Pullback Expert Advisor        |
//|                                  Copyright 2026, XAUUSD Trader   |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "2.00"
#property description "Auto Trading EA Triple EMA Pullback (8, 21, 125) untuk XAUUSD & Forex dengan Risk Management Pro, False Signal Telemetry, & Mode Backtest Bebas"

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
//| Enum Mode Sesi Pasar XAUUSD                                      |
//+------------------------------------------------------------------+
enum ENUM_XAU_SESSION_MODE
  {
   XAU_SESSION_ALL,       // Semua Sesi Aktif (24 Jam)
   XAU_SESSION_LONDON_NY, // Sesi London & New York Saja (Volatilitas Terbaik)
   XAU_SESSION_LONDON,    // Sesi London Saja (08:00 - 16:00 Broker)
   XAU_SESSION_NY         // Sesi New York Saja (13:00 - 22:00 Broker)
  };

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== Mode Backtest & Unconstrained Trading ==="
input bool                 InpAllowUnlimitedTrades         = false;         // Mode Backtest: Buka Posisi Tanpa Batas Maksimal
input bool                 InpIgnoreCooldownInTester       = false;         // Mode Backtest: Abaikan Cooldown Bar Sinyal
input bool                 InpDisableCircuitBreakerInTester = false;        // Mode Backtest: Nonaktifkan Circuit Breaker Harian

input group "=== Analisis & Audit False Signal ==="
input double               InpFalseSignalMFEThreshold      = 0.5;           // Ambang Batas MFE (R) untuk False Signal
input bool                 InpEnableChartHUD               = false;         // Tampilkan Teks Comment HUD di Chart (Default OFF agar Chart Bersih)

input group "=== Filter Fundamental & News Shock (XAUUSD) ==="
input bool                 InpUseFundamentalShockFilter    = true;          // Filter Volatilitas Ekstrem / News Shock
input double               InpFundamentalShockAtrMult      = 2.5;           // Batas Lonjakan Candle Shock (> x ATR)
input int                  InpFundamentalShockCooldown     = 4;             // Cooldown Pasca Shock Candle (Bars)
input bool                 InpUseNewsWindowFilter          = false;         // Blackout Jam Berita Ekonomi AS (NFP/CPI/FOMC)
input ENUM_XAU_SESSION_MODE InpXauSessionFilter            = XAU_SESSION_LONDON_NY; // Filter Sesi Pasar XAUUSD (London & NY)

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

input group "=== Sistem 3 Layar / Triple Screen (H1 -> M15 -> M5) ==="
input bool                 InpUseTripleScreen      = true;          // Aktifkan Sistem 3 Layar (H1 Macro -> M15 Structure -> M5 Trigger)
input ENUM_TIMEFRAMES      InpScreen1_TF           = PERIOD_H1;     // Layar 1: Timeframe Tren Besar Institusi (Macro Bias H1)
input int                  InpScreen1_EMA          = 50;            // Layar 1: Periode EMA Tren Besar Macro
input ENUM_TIMEFRAMES      InpScreen2_TF           = PERIOD_M15;    // Layar 2: Timeframe Struktur Pasar & Ayunan M15
input int                  InpScreen2_EMA          = 50;            // Layar 2: Periode EMA Level Kunci M15
input bool                 InpScreen2_RequireStruct = true;         // Layar 2: Wajib Konfirmasi Struktur Ayunan (Tolak Counter-Trend M15)
input bool                 InpScreen2_RequireKeyLevel = true;       // Layar 2: Wajib Konfirmasi Level Kunci EMA M15
input bool                 InpUseMTFFilter         = true;          // Filter HTF Tambahan (Legacy MTF Compatibility)
input ENUM_TIMEFRAMES      InpHTFTimeframe         = PERIOD_H1;     // Timeframe Tren Utama HTF
input int                  InpHTF_EMA_Period       = 50;            // Periode EMA HTF

input group "=== Money Management & Lot Size ==="
input ENUM_LOT_MODE        InpLotMode              = LOT_RISK_PERCENT; // Mode Kalkulasi Lot (Default: RISK_PERCENT)
input double               InpFixedLot             = 0.10;          // Fixed Lot Size (jika LOT_FIXED)
input double               InpRiskPercent          = 1.0;           // Resiko per Trade (% Equity - Terkendali Stabil)
input double               InpMaxLotSize           = 5.0;           // Maksimal Lot Eksekusi
input int                  InpMaxOpenPositions     = 1;             // Maksimal Posisi Terbuka Bersamaan

input group "=== Stop Loss & Take Profit ==="
input ENUM_SL_MODE         InpSLMode               = SL_SWING_CANDLE; // Mode Stop Loss
input double               InpSL_AtrMultiplier     = 1.5;           // Multiplier ATR untuk SL (jika SL_ATR_BASED)
input int                  InpSL_FixedPoints       = 300;           // SL Points (jika SL_FIXED_POINTS)
input int                  InpSL_BufferPoints      = 50;            // Buffer Tambahan SL Candle (Points)
input double               InpRiskRewardRatio      = 2.0;           // Target Risk:Reward (misal 1:2.0)
input int                  InpMinSLPoints          = 300;           // Batas Minimal SL Points (Proteksi Gold $3.00)
input int                  InpMaxSLPoints          = 650;           // Batas Maksimal SL Points (Tolak jika > $6.50 Gold)
input double               InpXauMinSlAtrMult      = 1.0;           // Minimal SL Floor Berbasis ATR (Gold Adaptive)

input group "=== Proteksi Profit: Partial Close, Break-Even & Trailing ==="
input bool                 InpUsePartialClose      = true;          // Aktifkan Ambil Sebagian Untung (Scale-Out)
input double               InpPartialCloseRR       = 1.0;           // Trigger Partial Close saat Profit mencapai 1:X R:R
input double               InpPartialClosePercent  = 50.0;          // Persentase Lot Ditutup (misal 50%)
input bool                 InpUseBreakEven         = true;          // Aktifkan Auto Break-Even (BEP)
input double               InpBE_TriggerRR         = 1.0;           // Pindahkan SL ke BEP saat Profit mencapai 1:X R:R
input int                  InpBE_LockProfitPoints  = 30;            // Profit Terkunci di atas Entry (Points)
input bool                 InpUseTrailingStop      = false;         // Aktifkan Trailing Stop (False agar leluasa capai TP 1:2)
input double               InpTrailingStartRR      = 1.8;           // Trailing Stop Baru Aktif Setelah Profit Mencapai 1:X R:R
input bool                 InpTrailingByEMA21      = false;         // Trailing Mengikuti Garis EMA 21
input double               InpTrailingAtrMult      = 1.5;           // Trailing Jarak ATR (jika bukan EMA 21)

input group "=== Filter Rintangan Support & Resistance (S/R Obstacle) ==="
input bool                 InpUseSnrObstacleFilter = true;          // Tolak Entry jika Terhalang Major S/R
input int                  InpSnrLookbackBars      = 50;            // Lookback Bar Pencarian Major S/R
input double               InpMinClearanceRR       = 1.0;           // Ruang Bebas Minimal ke Rintangan (x Jarak SL)

input group "=== Strategi Tambahan: Momentum Breakout ==="
input bool                 InpEnableBreakout       = true;          // Aktifkan Strategi Momentum Breakout
input int                  InpBreakoutLookbackBars = 15;            // Lookback Bar Konsolidasi / Range Breakout
input double               InpBreakoutMinBodyRatio = 0.50;          // Minimal Rasio Body Candle Penembus (50%)
input bool                 InpBreakoutRequireVolume= true;          // Wajib Konfirmasi Lonjakan Volume
input double               InpBreakoutVolMult      = 1.1;           // Pengali Volume Minimal (1.1x Rata-rata)

input group "=== Strategi Tambahan: Smart Money Concepts (SMC) ==="
input bool                 InpEnableSMC            = true;          // Aktifkan Strategi SMC (Liquidity Sweep & Value Zone)
input int                  InpSmcDealingRangeBars  = 35;            // Lookback Bar Dealing Range (High/Low)
input int                  InpSmcSweepLookback     = 10;            // Toleransi Bar Terjadinya Sweep (1-10 Bar Terakhir)
input bool                 InpSmcRequireDiscountPrem = true;        // Wajib di Zona Discount (Buy) / Premium (Sell)
input bool                 InpSmcRequireSweep      = false;         // Wajib Ada Liquidity Sweep (SSL/BSL Grab)
input int                  InpSmcPivotLookback     = 5;             // Lookback Pivot Ayunan Likuiditas BSL/SSL

input group "=== Filter Volume Transaksi Lilin (Smart Money Volume) ==="
input bool                 InpUseVolumeFilter      = true;          // Wajib Volume Lilin Setup Valid (Diatas Rata-rata)
input int                  InpVolumeLookback       = 20;            // Lookback Rata-rata Volume (SMA 20)
input double               InpVolumeMultiplier     = 1.0;           // Minimal Volume Setup (x Rata-rata Volume)

input group "=== Filter Kekuatan Tren (ADX Momentum) ==="
input bool                 InpUseADXFilter         = true;          // Wajib Tren Kuat (ADX Filter)
input int                  InpADX_Period           = 14;            // Periode ADX
input double               InpMinADXLevel          = 20.0;          // Minimal ADX Level (Di bawah 20 = Sideways Flat)

input group "=== Filter Tambahan: Fibonacci Golden Pocket (OTE) ==="
input bool                 InpUseFiboFilter        = true;          // Wajib Pullback Masuk Zona Emas Fibo (0.50 - 0.786)
input int                  InpFiboLookback         = 30;            // Lookback Rentang Swing Impulsif Fibonacci
input double               InpFiboMinRetrace       = 0.50;          // Minimal Retracement (50% Equilibrium)
input double               InpFiboMaxRetrace       = 0.786;         // Maksimal Retracement (78.6% Deep OTE)

input group "=== Filter Tambahan: RSI Momentum & Divergence ==="
input bool                 InpUseRSIFilter         = true;          // Filter Momentum Sehat RSI
input int                  InpRSI_Period           = 14;            // Periode RSI
input double               InpRSI_BuyMin           = 45.0;          // Minimal RSI untuk Buy (Momentum Naik)
input double               InpRSI_BuyMax           = 70.0;          // Maksimal RSI untuk Buy (Anti-Pucuk Overbought)
input double               InpRSI_SellMin          = 30.0;          // Minimal RSI untuk Sell (Anti-Lembah Oversold)
input double               InpRSI_SellMax          = 55.0;          // Maksimal RSI untuk Sell (Momentum Turun)
input bool                 InpUseRsiDivergence     = false;         // Konfirmasi Khusus RSI Hidden Divergence

input group "=== Filter Tambahan: Fair Value Gap (FVG / Imbalance) ==="
input bool                 InpUseFVGFilter         = false;         // Konfirmasi Mitigasi Area FVG
input int                  InpFVG_Lookback         = 10;            // Lookback Cek FVG (Candles)

input group "=== Sistem Skor Probabilitas & Konfluensi (Confluence Scoring) ==="
input bool                 InpUseConfluenceScoring = true;          // Aktifkan Sistem Skor Konfluensi (Anti Lagging Entry)
input int                  InpMinConfluenceScore   = 60;            // Minimal Skor untuk Entri (60=Grade A, 80=Grade A+, 40=Grade B)
input bool                 InpUseDynamicGradeSizing= false;         // Sizing Lot Dinamis Berbasis Grade (A+=100%, A=75%, B=50%)
input int                  InpScoreWeightFibo      = 20;            // Bobot Skor: Fibonacci Golden Zone (50%-78.6%)
input int                  InpScoreWeightRSI       = 20;            // Bobot Skor: RSI Momentum Sehat (45-70 Buy / 30-55 Sell)
input int                  InpScoreWeightFVG       = 20;            // Bobot Skor: Mitigasi Fair Value Gap (FVG)
input int                  InpScoreWeightADX       = 20;            // Bobot Skor: ADX Trend Strength (>= 20)
input int                  InpScoreWeightStructure = 20;            // Bobot Skor: Struktur Ayunan HH-HL / LH-LL

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
int                    handle_screen1_ema;
int                    handle_screen2_ema;
int                    handle_adx;
int                    handle_rsi;

ENUM_TIMEFRAMES        effectiveHTF      = PERIOD_H1;
datetime               lastTradeBarTime  = 0;
datetime               lastBuyTradeTime  = 0;
datetime               lastSellTradeTime = 0;

int                    dailyLossCount    = 0;
double                 dailyLossAmount   = 0.0;
int                    lastCalculatedDay = -1;

//+------------------------------------------------------------------+
//| Struktur Pelacakan Trade & MFE untuk Audit False Signal          |
//+------------------------------------------------------------------+
struct STrackedTrade
  {
   ulong              ticket;          // Order / Position Ticket
   long               positionId;      // Position Identifier
   ENUM_POSITION_TYPE posType;         // Buy atau Sell
   double             openPrice;       // Harga Masuk
   double             initialSL;       // Stop Loss Awal
   double             initialTP;       // Take Profit Awal
   double             slDistance;      // Jarak SL (Points/Price)
   double             maxMfePrice;     // Harga Tertinggi (Buy) / Terendah (Sell) yang Pernah Dicapai
   double             maxMfeR;         // Maximum Favorable Excursion dalam R-Multiple
   string             patternName;     // Pola Candlestick Pemantik
   string             sessionName;     // Sesi Pasar saat Eksekusi
   datetime           openTime;        // Waktu Order Dibuka
   datetime           closeTime;       // Waktu Posisi Ditutup
   double             closeProfit;     // Laba / Rugi Bersih saat Tutup
   bool               isClosed;        // Status Ditutup
   bool               isFalseSignal;   // Flag False Signal (MFE < InpFalseSignalMFEThreshold)
   bool               isPartialClosed; // Flag sudah dieksekusi partial close
   double             originalLot;     // Ukuran lot awal sebelum partial close
  };

STrackedTrade          trackedTrades[];
int                    g_totalClosedTrades = 0;
int                    g_winCount          = 0;
int                    g_bepCount          = 0;
int                    g_partialCloseCount = 0;
int                    g_normalLossCount   = 0;
int                    g_falseSignalCount  = 0;

int                    g_falsePerPatternPinbar    = 0;
int                    g_falsePerPatternEngulfing = 0;
int                    g_falsePerPatternInside    = 0;
int                    g_falsePerPatternOther     = 0;

int                    g_falsePerSessionLondon = 0;
int                    g_falsePerSessionNY     = 0;
int                    g_falsePerSessionAsia   = 0;

//+------------------------------------------------------------------+
//| Deklarasi Fungsi Forward                                         |
//+------------------------------------------------------------------+
void PrintAuditReport();
void SyncClosedTradesFromHistory();

//+------------------------------------------------------------------+
//| Dapatkan Nama Sesi Pasar Berdasarkan Jam Broker                  |
//+------------------------------------------------------------------+
string GetMarketSessionName(int hour)
  {
   if(hour >= 8 && hour < 16)
      return "London";
   else if(hour >= 13 && hour < 22)
      return "New York";
   else
      return "Asian / Sydney";
  }

//+------------------------------------------------------------------+
//| Registrasi Trade Baru ke Sistem Pelacakan Telemetri              |
//+------------------------------------------------------------------+
void RegisterTrackedTrade(ulong ticket, long posId, ENUM_POSITION_TYPE posType, double openPrice,
                          double initialSL, double initialTP, string patternName, string sessionName)
  {
   int total = ArraySize(trackedTrades);
   for(int i = 0; i < total; i++)
     {
      if((ticket > 0 && trackedTrades[i].ticket == ticket) || 
         (posId > 0 && trackedTrades[i].positionId == posId))
        {
         if(trackedTrades[i].positionId == 0 && posId > 0) trackedTrades[i].positionId = posId;
         if(trackedTrades[i].ticket == 0 && ticket > 0) trackedTrades[i].ticket = ticket;
         return;
        }
     }

   double slDist = MathAbs(openPrice - initialSL);
   if(slDist <= 0.0) slDist = InpMinSLPoints * _Point;

   ArrayResize(trackedTrades, total + 1);
   trackedTrades[total].ticket        = ticket;
   trackedTrades[total].positionId    = posId;
   trackedTrades[total].posType       = posType;
   trackedTrades[total].openPrice     = openPrice;
   trackedTrades[total].initialSL     = initialSL;
   trackedTrades[total].initialTP     = initialTP;
   trackedTrades[total].slDistance    = slDist;
   trackedTrades[total].maxMfePrice   = openPrice;
   trackedTrades[total].maxMfeR       = 0.0;
   trackedTrades[total].patternName   = patternName;
   trackedTrades[total].sessionName   = sessionName;
   trackedTrades[total].openTime      = TimeCurrent();
   trackedTrades[total].closeTime       = 0;
   trackedTrades[total].closeProfit     = 0.0;
   trackedTrades[total].isClosed        = false;
   trackedTrades[total].isFalseSignal   = false;
   trackedTrades[total].isPartialClosed = false;
   trackedTrades[total].originalLot     = 0.0;
  }

//+------------------------------------------------------------------+
//| Perbarui MFE (Maximum Favorable Excursion) untuk Posisi Terbuka  |
//+------------------------------------------------------------------+
void UpdateTrackedTradeMFE(ulong ticket, long posId, double currentPrice)
  {
   int total = ArraySize(trackedTrades);
   for(int i = 0; i < total; i++)
     {
      if(!trackedTrades[i].isClosed && 
         ((ticket > 0 && trackedTrades[i].ticket == ticket) || 
          (posId > 0 && trackedTrades[i].positionId == posId)))
        {
         if(trackedTrades[i].posType == POSITION_TYPE_BUY)
           {
            if(currentPrice > trackedTrades[i].maxMfePrice)
               trackedTrades[i].maxMfePrice = currentPrice;

            double mfeDist = trackedTrades[i].maxMfePrice - trackedTrades[i].openPrice;
            if(trackedTrades[i].slDistance > 0.0)
              {
               double r = mfeDist / trackedTrades[i].slDistance;
               if(r > trackedTrades[i].maxMfeR) trackedTrades[i].maxMfeR = r;
              }
           }
         else if(trackedTrades[i].posType == POSITION_TYPE_SELL)
           {
            if(trackedTrades[i].maxMfePrice == 0.0 || currentPrice < trackedTrades[i].maxMfePrice)
               trackedTrades[i].maxMfePrice = currentPrice;

            double mfeDist = trackedTrades[i].openPrice - trackedTrades[i].maxMfePrice;
            if(trackedTrades[i].slDistance > 0.0)
              {
               double r = mfeDist / trackedTrades[i].slDistance;
               if(r > trackedTrades[i].maxMfeR) trackedTrades[i].maxMfeR = r;
              }
           }
         break;
        }
     }
  }

//+------------------------------------------------------------------+
//| Evaluasi Trade yang Telah Ditutup untuk Audit False Signal       |
//+------------------------------------------------------------------+
void EvaluateClosedTrade(long posId, double profit, datetime closeTime)
  {
   if(posId <= 0) return;
   int total = ArraySize(trackedTrades);
   int foundIdx = -1;

   for(int i = 0; i < total; i++)
     {
      if(trackedTrades[i].positionId == posId || (trackedTrades[i].ticket > 0 && trackedTrades[i].ticket == (ulong)posId))
        {
         foundIdx = i;
         break;
        }
     }

   if(foundIdx != -1)
     {
      if(trackedTrades[foundIdx].isClosed) return; // Sudah tercatat

      trackedTrades[foundIdx].isClosed    = true;
      trackedTrades[foundIdx].closeProfit = profit;
      trackedTrades[foundIdx].closeTime   = closeTime;

      // Evaluasi Kategori Hasil
      if(profit > 0.5)
        {
         g_winCount++;
        }
      else if(profit >= -0.5 && profit <= 0.5)
        {
         g_bepCount++;
        }
      else
        {
         // Trade berakhir rugi (SL)
         if(trackedTrades[foundIdx].maxMfeR < InpFalseSignalMFEThreshold)
           {
            trackedTrades[foundIdx].isFalseSignal = true;
            g_falseSignalCount++;

            // Breakdown pola
            string pat = trackedTrades[foundIdx].patternName;
            if(StringFind(pat, "Hammer") >= 0 || StringFind(pat, "Pin") >= 0 || StringFind(pat, "Star") >= 0)
               g_falsePerPatternPinbar++;
            else if(StringFind(pat, "Engulfing") >= 0)
               g_falsePerPatternEngulfing++;
            else if(StringFind(pat, "Inside") >= 0)
               g_falsePerPatternInside++;
            else
               g_falsePerPatternOther++;

            // Breakdown sesi
            string sess = trackedTrades[foundIdx].sessionName;
            if(StringFind(sess, "London") >= 0)
               g_falsePerSessionLondon++;
            else if(StringFind(sess, "New York") >= 0)
               g_falsePerSessionNY++;
            else
               g_falsePerSessionAsia++;
           }
         else
           {
            trackedTrades[foundIdx].isFalseSignal = false;
            g_normalLossCount++;
           }
        }
      g_totalClosedTrades++;
     }
   else
     {
      // Posisi tidak ditemukan di array trackedTrades (misal dari sesi sebelumnya)
      ArrayResize(trackedTrades, total + 1);
      trackedTrades[total].ticket        = (ulong)posId;
      trackedTrades[total].positionId    = posId;
      trackedTrades[total].posType       = POSITION_TYPE_BUY;
      trackedTrades[total].openPrice     = 0.0;
      trackedTrades[total].initialSL     = 0.0;
      trackedTrades[total].initialTP     = 0.0;
      trackedTrades[total].slDistance    = InpMinSLPoints * _Point;
      trackedTrades[total].maxMfePrice   = 0.0;
      trackedTrades[total].maxMfeR       = 0.0;
      trackedTrades[total].patternName   = "Unknown";
      trackedTrades[total].sessionName   = "Unknown";
      trackedTrades[total].openTime      = closeTime;
      trackedTrades[total].closeTime     = closeTime;
      trackedTrades[total].closeProfit   = profit;
      trackedTrades[total].isClosed      = true;

      if(profit > 0.5) g_winCount++;
      else if(profit >= -0.5 && profit <= 0.5) g_bepCount++;
      else
        {
         g_normalLossCount++;
         trackedTrades[total].isFalseSignal = false;
        }
      g_totalClosedTrades++;
     }
  }

//+------------------------------------------------------------------+
//| Sinkronisasi Seluruh Deal Ditutup dari History                   |
//+------------------------------------------------------------------+
void SyncClosedTradesFromHistory()
  {
   if(!HistorySelect(0, TimeCurrent())) return;
   int totalDeals = HistoryDealsTotal();
   for(int i = 0; i < totalDeals; i++)
     {
      ulong dealTicket = HistoryDealGetTicket(i);
      if(dealTicket > 0)
        {
         if(HistoryDealGetString(dealTicket, DEAL_SYMBOL) == _Symbol &&
            HistoryDealGetInteger(dealTicket, DEAL_MAGIC) == InpMagicNumber &&
            HistoryDealGetInteger(dealTicket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
           {
            long posId = HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);
            double profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT) + 
                            HistoryDealGetDouble(dealTicket, DEAL_SWAP) + 
                            HistoryDealGetDouble(dealTicket, DEAL_COMMISSION);
            datetime dealTime = (datetime)HistoryDealGetInteger(dealTicket, DEAL_TIME);
            EvaluateClosedTrade(posId, profit, dealTime);
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Deteksi Lonjakan Volatilitas / Lilin Berita Ekstrem (News Shock) |
//+------------------------------------------------------------------+
bool IsFundamentalShockActive(const MqlRates &rates[], double currentAtr)
  {
   if(!InpUseFundamentalShockFilter) return false;
   if(currentAtr <= 0.0) return false;

   int lookback = MathMin(InpFundamentalShockCooldown, ArraySize(rates) - 1);
   for(int i = 1; i <= lookback; i++)
     {
      double candleRange = rates[i].high - rates[i].low;
      if(candleRange >= (InpFundamentalShockAtrMult * currentAtr))
        {
         return true;
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Jam Berita Berdampak Tinggi AS (High-Impact News Window)     |
//+------------------------------------------------------------------+
bool IsNewsWindowActive()
  {
   if(!InpUseNewsWindowFilter) return false;
   MqlDateTime dt;
   TimeCurrent(dt);
   // Jam rilis berita AS: 13, 14, 19, 20 waktu server
   if(dt.hour == 13 || dt.hour == 14 || dt.hour == 19 || dt.hour == 20)
      return true;
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Sesi Pasar Diizinkan Berdasarkan Filter               |
//+------------------------------------------------------------------+
bool IsSessionFilterAllowed()
  {
   if(InpXauSessionFilter == XAU_SESSION_ALL) return true;

   MqlDateTime dt;
   TimeCurrent(dt);
   int h = dt.hour;

   if(InpXauSessionFilter == XAU_SESSION_LONDON_NY)
     {
      return (h >= 8 && h < 22);
     }
   else if(InpXauSessionFilter == XAU_SESSION_LONDON)
     {
      return (h >= 8 && h < 16);
     }
   else if(InpXauSessionFilter == XAU_SESSION_NY)
     {
      return (h >= 13 && h < 22);
     }
   return true;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Pullback Berada di Fibonacci Golden Zone untuk BUY    |
//+------------------------------------------------------------------+
bool IsFiboGoldenZoneBuy(const MqlRates &rates[], int totalRates, int shift = 1)
  {
   if(!InpUseFiboFilter) return true;
   int start = shift + 1;
   int end = MathMin(shift + InpFiboLookback, totalRates - 1);
   if(end <= start) return true;

   double swingHigh = rates[start].high;
   double swingLow  = rates[start].low;

   for(int i = start + 1; i <= end; i++)
     {
      if(rates[i].high > swingHigh) swingHigh = rates[i].high;
      if(rates[i].low < swingLow)   swingLow  = rates[i].low;
     }

   double range = swingHigh - swingLow;
   if(range <= 0.0) return true;

   double fibo50 = swingHigh - (InpFiboMinRetrace * range);
   double fiboDeep = swingHigh - (InpFiboMaxRetrace * range);

   return (rates[shift].low <= fibo50 && rates[shift].high >= fiboDeep);
  }

//+------------------------------------------------------------------+
//| Cek Apakah Pullback Berada di Fibonacci Golden Zone untuk SELL   |
//+------------------------------------------------------------------+
bool IsFiboGoldenZoneSell(const MqlRates &rates[], int totalRates, int shift = 1)
  {
   if(!InpUseFiboFilter) return true;
   int start = shift + 1;
   int end = MathMin(shift + InpFiboLookback, totalRates - 1);
   if(end <= start) return true;

   double swingHigh = rates[start].high;
   double swingLow  = rates[start].low;

   for(int i = start + 1; i <= end; i++)
     {
      if(rates[i].high > swingHigh) swingHigh = rates[i].high;
      if(rates[i].low < swingLow)   swingLow  = rates[i].low;
     }

   double range = swingHigh - swingLow;
   if(range <= 0.0) return true;

   double fibo50 = swingLow + (InpFiboMinRetrace * range);
   double fiboDeep = swingLow + (InpFiboMaxRetrace * range);

   return (rates[shift].high >= fibo50 && rates[shift].low <= fiboDeep);
  }

//+------------------------------------------------------------------+
//| Cek Apakah Momentum RSI Aman & Sehat untuk BUY                  |
//+------------------------------------------------------------------+
bool IsRsiValidBuy(double rsiVal)
  {
   if(!InpUseRSIFilter) return true;
   return (rsiVal >= InpRSI_BuyMin && rsiVal <= InpRSI_BuyMax);
  }

//+------------------------------------------------------------------+
//| Cek Apakah Momentum RSI Aman & Sehat untuk SELL                 |
//+------------------------------------------------------------------+
bool IsRsiValidSell(double rsiVal)
  {
   if(!InpUseRSIFilter) return true;
   return (rsiVal >= InpRSI_SellMin && rsiVal <= InpRSI_SellMax);
  }

//+------------------------------------------------------------------+
//| Deteksi RSI Hidden Divergence (Trend Continuation Signal)        |
//+------------------------------------------------------------------+
bool CheckRsiHiddenDivergence(const MqlRates &rates[], const double &rsi[], bool isBuy, int shift = 1)
  {
   if(!InpUseRsiDivergence) return true;
   if(ArraySize(rsi) < 15 || ArraySize(rates) < 15) return true;

   for(int i = shift + 2; i < shift + 14; i++)
     {
      if(isBuy)
        {
         if(rates[i].low < rates[i-1].low && rates[i].low < rates[i+1].low)
           {
            if(rates[shift].low > rates[i].low && rsi[shift] < rsi[i])
               return true;
           }
        }
      else
        {
         if(rates[i].high > rates[i-1].high && rates[i].high > rates[i+1].high)
           {
            if(rates[shift].high < rates[i].high && rsi[shift] > rsi[i])
               return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Keberadaan Fair Value Gap (FVG) Aktif yang Termitigasi      |
//+------------------------------------------------------------------+
bool HasActiveFVG(const MqlRates &rates[], int totalRates, bool isBuy, int shift = 1)
  {
   if(!InpUseFVGFilter) return true;
   int end = MathMin(shift + InpFVG_Lookback, totalRates - 2);

   for(int i = shift + 1; i < end; i++)
     {
      if(isBuy)
        {
         if(rates[i].low > rates[i+2].high)
           {
            double gapTop = rates[i].low;
            double gapBottom = rates[i+2].high;
            if(rates[shift].low <= gapTop && rates[shift].low >= gapBottom)
               return true;
           }
        }
      else
        {
         if(rates[i].high < rates[i+2].low)
           {
            double gapBottom = rates[i].high;
            double gapTop = rates[i+2].low;
            if(rates[shift].high >= gapBottom && rates[shift].high <= gapTop)
               return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Periksa Apakah Ada Level S/R Mayor yang Menghalangi Target       |
//+------------------------------------------------------------------+
bool IsObstacleBlocking(bool isBuy, double entryPrice, double slDistance,
                        const MqlRates &rates[], int totalRates, string &outReason)
  {
   if(!InpUseSnrObstacleFilter) return false;
   if(totalRates < 15) return false;

   int count = MathMin(InpSnrLookbackBars, totalRates - 2);
   double requiredClearance = slDistance * InpMinClearanceRR;

   if(isBuy)
     {
      double nearestRes = DBL_MAX;
      for(int i = 2; i < count; i++)
        {
         // Deteksi Swing High Mayor (Fraktal)
         if(rates[i].high >= rates[i-1].high && rates[i].high >= rates[i+1].high)
           {
            if(rates[i].high > (entryPrice + (10 * _Point)) && rates[i].high < nearestRes)
              {
               nearestRes = rates[i].high;
              }
           }
        }

      if(nearestRes != DBL_MAX)
        {
         double distToRes = nearestRes - entryPrice;
         if(distToRes < requiredClearance)
           {
            outReason = StringFormat("Terhalang Major Resistance di %.2f (Jarak %.0f pts < Minimal %.0f pts)",
                                     nearestRes, distToRes / _Point, requiredClearance / _Point);
            return true;
           }
        }
     }
   else // SELL
     {
      double nearestSup = 0.0;
      for(int i = 2; i < count; i++)
        {
         // Deteksi Swing Low Mayor (Fraktal)
         if(rates[i].low <= rates[i-1].low && rates[i].low <= rates[i+1].low)
           {
            if(rates[i].low < (entryPrice - (10 * _Point)) && rates[i].low > nearestSup)
              {
               nearestSup = rates[i].low;
              }
           }
        }

      if(nearestSup > 0.0)
        {
         double distToSup = entryPrice - nearestSup;
         if(distToSup < requiredClearance)
           {
            outReason = StringFormat("Terhalang Major Support di %.2f (Jarak %.0f pts < Minimal %.0f pts)",
                                     nearestSup, distToSup / _Point, requiredClearance / _Point);
            return true;
           }
        }
     }

   return false;
  }

//+------------------------------------------------------------------+
//| Deteksi Bullish Momentum Breakout (Penembusan Range Lookback)    |
//+------------------------------------------------------------------+
bool DetectBullishBreakout(const MqlRates &rates[], int totalRates, int shift, int lookback, double minBodyRatio, double &outBreakoutLevel)
  {
   if(!InpEnableBreakout) return false;
   if(shift < 1 || totalRates < shift + lookback + 2) return false;

   double c0 = rates[shift].close;
   double o0 = rates[shift].open;
   double h0 = rates[shift].high;
   double l0 = rates[shift].low;
   double range0 = h0 - l0;
   if(range0 <= 0.0 || c0 <= o0) return false; // Wajib bullish candle

   double body0 = c0 - o0;
   if((body0 / range0) < minBodyRatio) return false; // Wajib solid body tebal

   // Cari Highest High dari [shift + 1] hingga [shift + lookback]
   double highestHigh = rates[shift + 1].high;
   for(int i = shift + 2; i <= shift + lookback; i++)
     {
      if(rates[i].high > highestHigh) highestHigh = rates[i].high;
     }

   outBreakoutLevel = highestHigh;
   return (c0 > highestHigh);
  }

//+------------------------------------------------------------------+
//| Deteksi Bearish Momentum Breakout (Penembusan Range Lookback)    |
//+------------------------------------------------------------------+
bool DetectBearishBreakout(const MqlRates &rates[], int totalRates, int shift, int lookback, double minBodyRatio, double &outBreakoutLevel)
  {
   if(!InpEnableBreakout) return false;
   if(shift < 1 || totalRates < shift + lookback + 2) return false;

   double c0 = rates[shift].close;
   double o0 = rates[shift].open;
   double h0 = rates[shift].high;
   double l0 = rates[shift].low;
   double range0 = h0 - l0;
   if(range0 <= 0.0 || c0 >= o0) return false; // Wajib bearish candle

   double body0 = o0 - c0;
   if((body0 / range0) < minBodyRatio) return false; // Wajib solid body tebal

   // Cari Lowest Low dari [shift + 1] hingga [shift + lookback]
   double lowestLow = rates[shift + 1].low;
   for(int i = shift + 2; i <= shift + lookback; i++)
     {
      if(rates[i].low < lowestLow) lowestLow = rates[i].low;
     }

   outBreakoutLevel = lowestLow;
   return (c0 < lowestLow);
  }

//+------------------------------------------------------------------+
//| Hitung Skor Konfluensi Khusus Setup Momentum Breakout            |
//+------------------------------------------------------------------+
int CalculateBreakoutConfluenceScore(bool isBuy, double curRsi, double adxVal, double volRatio, string &outDetails, string &outGrade)
  {
   int score = 40; // Base score valid breakout
   outDetails = "RangeBreak+";

   if(isBuy && curRsi >= 45.0 && curRsi <= 75.0)
     {
      score += 20;
      outDetails += "RSI+";
     }
   else if(!isBuy && curRsi >= 25.0 && curRsi <= 55.0)
     {
      score += 20;
      outDetails += "RSI+";
     }

   if(adxVal >= InpMinADXLevel)
     {
      score += 20;
      outDetails += "ADX+";
     }

   if(volRatio >= InpBreakoutVolMult)
     {
      score += 20;
      outDetails += "Vol+";
     }

   if(StringLen(outDetails) > 0 && StringSubstr(outDetails, StringLen(outDetails) - 1, 1) == "+")
      outDetails = StringSubstr(outDetails, 0, StringLen(outDetails) - 1);

   if(score >= 80)      outGrade = "A+";
   else if(score >= 60) outGrade = "A";
   else                 outGrade = "B";

   return score;
  }

//+------------------------------------------------------------------+
//| Hitung SMC Dealing Range & Posisi Valuasi (Discount / Premium)   |
//+------------------------------------------------------------------+
bool CalculateDealingRange(const MqlRates &rates[], int totalRates, int shift, int lookback,
                           double &outHigh, double &outLow, double &outEq, double &outPct)
  {
   if(shift < 1 || totalRates < shift + lookback + 1) return false;
   double h = rates[shift + 1].high;
   double l = rates[shift + 1].low;
   for(int i = shift + 2; i <= shift + lookback; i++)
     {
      if(rates[i].high > h) h = rates[i].high;
      if(rates[i].low < l)  l = rates[i].low;
     }
   double range = h - l;
   if(range <= 0.0) return false;
   outHigh = h;
   outLow  = l;
   outEq   = l + (range * 0.5);
   outPct  = (rates[shift].close - l) / range * 100.0;
   return true;
  }

//+------------------------------------------------------------------+
//| Deteksi Liquidity Sweep (SSL Sweep untuk Buy, BSL untuk Sell)    |
//+------------------------------------------------------------------+
bool DetectLiquiditySweep(const MqlRates &rates[], int totalRates, int shift, bool checkSsl,
                         int sweepLookback, int pivotLookback, double &outSweptLevel, int &outAgeBars)
  {
   outSweptLevel = 0.0;
   outAgeBars = 999;
   if(shift < 1 || totalRates < shift + sweepLookback + pivotLookback + 5) return false;

   int searchEnd = shift;
   int searchStart = shift + sweepLookback;

   for(int bar = searchEnd; bar <= searchStart; bar++)
     {
      double bHigh = rates[bar].high;
      double bLow  = rates[bar].low;
      double bClose= rates[bar].close;

      // Cari pivot likuiditas sebelum bar ini
      int pStart = bar + 1;
      int pEnd   = MathMin(totalRates - pivotLookback - 1, bar + 30);

      for(int p = pStart + pivotLookback; p <= pEnd; p++)
        {
         if(checkSsl) // SSL Sweep (Menyapu Sell-Side Liquidity)
           {
            bool isSwingLow = true;
            double pLow = rates[p].low;
            for(int k = 1; k <= pivotLookback; k++)
              {
               if((p - k) >= 0 && rates[p - k].low < pLow) { isSwingLow = false; break; }
               if((p + k) < totalRates && rates[p + k].low < pLow) { isSwingLow = false; break; }
              }
            if(isSwingLow)
              {
               // Low bar menusuk ke bawah pLow, namun close ditutup kembali di atas pLow
               if(bLow < pLow && bClose >= pLow)
                 {
                  outSweptLevel = pLow;
                  outAgeBars = bar - shift;
                  return true;
                 }
              }
           }
         else // BSL Sweep (Menyapu Buy-Side Liquidity)
           {
            bool isSwingHigh = true;
            double pHigh = rates[p].high;
            for(int k = 1; k <= pivotLookback; k++)
              {
               if((p - k) >= 0 && rates[p - k].high > pHigh) { isSwingHigh = false; break; }
               if((p + k) < totalRates && rates[p + k].high > pHigh) { isSwingHigh = false; break; }
              }
            if(isSwingHigh)
              {
               // High bar menusuk ke atas pHigh, namun close ditutup kembali di bawah pHigh
               if(bHigh > pHigh && bClose <= pHigh)
                 {
                  outSweptLevel = pHigh;
                  outAgeBars = bar - shift;
                  return true;
                 }
              }
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Deteksi Setup SMC Bullish Institutional                          |
//+------------------------------------------------------------------+
bool DetectSmcBullishSetup(const MqlRates &rates[], int totalRates, int shift,
                           double &outSweptLevel, string &outSmcInfo)
  {
   if(!InpEnableSMC) return false;
   if(shift < 1 || totalRates < shift + InpSmcDealingRangeBars + 10) return false;

   // 1. Hitung Dealing Range & Cek Zona Discount (< 50%)
   double rHigh = 0, rLow = 0, rEq = 0, rPct = 0;
   if(!CalculateDealingRange(rates, totalRates, shift, InpSmcDealingRangeBars, rHigh, rLow, rEq, rPct))
      return false;

   bool isDiscount = (rPct < 50.0);
   if(InpSmcRequireDiscountPrem && !isDiscount) return false;

   // 2. Deteksi SSL Liquidity Sweep
   double sweptLvl = 0.0;
   int ageBars = 0;
   bool hasSslSweep = DetectLiquiditySweep(rates, totalRates, shift, true, InpSmcSweepLookback, InpSmcPivotLookback, sweptLvl, ageBars);

   if(InpSmcRequireSweep && !hasSslSweep) return false;

   // 3. Cek Mitigasi FVG Bullish
   bool isFvgMitigated = HasActiveFVG(rates, totalRates, true, shift);

   // Wajib ada konfluensi institusional: SSL Sweep ATAU FVG Mitigation ATAU Deep Discount (< 40%)
   if(!hasSslSweep && !isFvgMitigated && rPct >= 40.0)
      return false;

   // 4. Candle konfirmasi wajib penolakan bullish (Close > Open)
   double c0 = rates[shift].close;
   double o0 = rates[shift].open;
   double l0 = rates[shift].low;
   double h0 = rates[shift].high;
   double range0 = h0 - l0;
   if(range0 <= 0.0 || c0 <= o0) return false;

   // Out info
   outSweptLevel = hasSslSweep ? sweptLvl : MathMin(rates[shift].low, rates[shift + 1].low);
   outSmcInfo = StringFormat("SMC Disc(%.0f%%)%s%s", rPct, hasSslSweep ? "+SSLSweep" : "", isFvgMitigated ? "+FVG" : "");
   return true;
  }

//+------------------------------------------------------------------+
//| Deteksi Setup SMC Bearish Institutional                          |
//+------------------------------------------------------------------+
bool DetectSmcBearishSetup(const MqlRates &rates[], int totalRates, int shift,
                           double &outSweptLevel, string &outSmcInfo)
  {
   if(!InpEnableSMC) return false;
   if(shift < 1 || totalRates < shift + InpSmcDealingRangeBars + 10) return false;

   // 1. Hitung Dealing Range & Cek Zona Premium (> 50%)
   double rHigh = 0, rLow = 0, rEq = 0, rPct = 0;
   if(!CalculateDealingRange(rates, totalRates, shift, InpSmcDealingRangeBars, rHigh, rLow, rEq, rPct))
      return false;

   bool isPremium = (rPct > 50.0);
   if(InpSmcRequireDiscountPrem && !isPremium) return false;

   // 2. Deteksi BSL Liquidity Sweep
   double sweptLvl = 0.0;
   int ageBars = 0;
   bool hasBslSweep = DetectLiquiditySweep(rates, totalRates, shift, false, InpSmcSweepLookback, InpSmcPivotLookback, sweptLvl, ageBars);

   if(InpSmcRequireSweep && !hasBslSweep) return false;

   // 3. Cek Mitigasi FVG Bearish
   bool isFvgMitigated = HasActiveFVG(rates, totalRates, false, shift);

   // Wajib ada konfluensi institusional: BSL Sweep ATAU FVG Mitigation ATAU Deep Premium (> 60%)
   if(!hasBslSweep && !isFvgMitigated && rPct <= 60.0)
      return false;

   // 4. Candle konfirmasi wajib penolakan bearish (Close < Open)
   double c0 = rates[shift].close;
   double o0 = rates[shift].open;
   double l0 = rates[shift].low;
   double h0 = rates[shift].high;
   double range0 = h0 - l0;
   if(range0 <= 0.0 || c0 >= o0) return false;

   // Out info
   outSweptLevel = hasBslSweep ? sweptLvl : MathMax(rates[shift].high, rates[shift + 1].high);
   outSmcInfo = StringFormat("SMC Prem(%.0f%%)%s%s", rPct, hasBslSweep ? "+BSLSweep" : "", isFvgMitigated ? "+FVG" : "");
   return true;
  }

//+------------------------------------------------------------------+
//| Hitung Skor Konfluensi Khusus Setup SMC Institutional            |
//+------------------------------------------------------------------+
int CalculateSmcConfluenceScore(bool isBuy, double curRsi, double adxVal, double volRatio,
                                string smcInfo, string &outDetails, string &outGrade)
  {
   int score = 40; // Base score valid SMC setup
   outDetails = smcInfo + "+";

   if(isBuy && curRsi >= 40.0 && curRsi <= 70.0)
     {
      score += 20;
      outDetails += "RSI+";
     }
   else if(!isBuy && curRsi >= 30.0 && curRsi <= 60.0)
     {
      score += 20;
      outDetails += "RSI+";
     }

   if(adxVal >= InpMinADXLevel)
     {
      score += 20;
      outDetails += "ADX+";
     }

   if(volRatio >= 1.0)
     {
      score += 20;
      outDetails += "Vol+";
     }

   if(StringLen(outDetails) > 0 && StringSubstr(outDetails, StringLen(outDetails) - 1, 1) == "+")
      outDetails = StringSubstr(outDetails, 0, StringLen(outDetails) - 1);

   if(score >= 80)      outGrade = "A+";
   else if(score >= 60) outGrade = "A";
   else                 outGrade = "B";

   return score;
  }

//+------------------------------------------------------------------+
//| Tampilkan Dashboard Telemetri Real-Time di Chart                 |
//+------------------------------------------------------------------+
void UpdateChartHUD(double currentAtr, double currentRsi, bool isShock, bool isNewsWin)
  {
   bool isTester = (bool)MQLInfoInteger(MQL_TESTER);
   if(!InpEnableChartHUD && !isTester)
     {
      Comment("");
      return;
     }

   MqlDateTime dt;
   TimeCurrent(dt);
   string sessionName = GetMarketSessionName(dt.hour);

   double winRate   = (g_totalClosedTrades > 0) ? (g_winCount * 100.0 / g_totalClosedTrades) : 0.0;
   double falseRate = (g_totalClosedTrades > 0) ? (g_falseSignalCount * 100.0 / g_totalClosedTrades) : 0.0;
   double validRate = 100.0 - falseRate;

   string hud = "";
   hud += "=========================================================\n";
   hud += "   TRIPLE EMA PULLBACK EXPERT ADVISOR - XAUUSD (PRO)     \n";
   hud += "=========================================================\n";
   hud += StringFormat("  Mode Eksekusi     : %s\n", InpAllowUnlimitedTrades ? "UNCONSTRAINED (BEBAS MULTI-TRADE)" : "STANDARD (SINGLE / LIMITED)");
   hud += StringFormat("  Sesi Pasar        : %s (Filter: %s)\n", sessionName, EnumToString(InpXauSessionFilter));
   hud += StringFormat("  RSI 14 Momentum   : %.1f (Filter: %s) | Fibo OTE: %s\n", currentRsi, InpUseRSIFilter ? "ON" : "OFF", InpUseFiboFilter ? "ON (50-78.6%)" : "OFF");
   hud += StringFormat("  Filter Volatilitas: %s | News Window: %s\n", isShock ? "NEWS SHOCK (BLOCKED)" : "NORMAL", isNewsWin ? "BLACKOUT" : "OK");
   hud += StringFormat("  Posisi Terbuka    : %d / %s\n", CountOpenPositions(), InpAllowUnlimitedTrades ? "Unlimited" : IntegerToString(InpMaxOpenPositions));
   hud += "---------------------------------------------------------\n";
   hud += "  [TELEMETRI AUDIT FALSE SIGNAL & KINERJA]\n";
   hud += StringFormat("  Total Trade Selesai : %d\n", g_totalClosedTrades);
   hud += StringFormat("  Win Rate            : %.1f%% (%d Wins | %d BEP | %d Loss)\n", winRate, g_winCount, g_bepCount, g_normalLossCount + g_falseSignalCount);
   hud += StringFormat("  False Signals       : %d (%.1f%%) [MFE < %.1fR]\n", g_falseSignalCount, falseRate, InpFalseSignalMFEThreshold);
   hud += StringFormat("  Valid Momentum (MFE): %d (%.1f%%)\n", g_totalClosedTrades - g_falseSignalCount, validRate);
   hud += "=========================================================";

   Comment(hud);
  }

//+------------------------------------------------------------------+
//| Cetak Laporan Audit Komprehensif ke Log & Tester Journal         |
//+------------------------------------------------------------------+
void PrintAuditReport()
  {
   SyncClosedTradesFromHistory();

   double winRate   = (g_totalClosedTrades > 0) ? (g_winCount * 100.0 / g_totalClosedTrades) : 0.0;
   double bepRate   = (g_totalClosedTrades > 0) ? (g_bepCount * 100.0 / g_totalClosedTrades) : 0.0;
   double lossRate  = (g_totalClosedTrades > 0) ? ((g_normalLossCount + g_falseSignalCount) * 100.0 / g_totalClosedTrades) : 0.0;
   double falseRate = (g_totalClosedTrades > 0) ? (g_falseSignalCount * 100.0 / g_totalClosedTrades) : 0.0;
   double normRate  = (g_totalClosedTrades > 0) ? (g_normalLossCount * 100.0 / g_totalClosedTrades) : 0.0;

   Print("=======================================================================");
   Print("       AUDIT KINERJA STRATEGI & ANALISIS FALSE SIGNAL (MT5 EA)         ");
   Print("=======================================================================");
   Print(StringFormat("Simbol: %s | Timeframe: %s | Magic: %d", _Symbol, EnumToString(_Period), InpMagicNumber));
   Print(StringFormat("Mode Backtest Bebas : %s | Cooldown Ignored: %s", InpAllowUnlimitedTrades ? "YES" : "NO", InpIgnoreCooldownInTester ? "YES" : "NO"));
   Print(StringFormat("Total Trade Selesai : %d", g_totalClosedTrades));
   Print(StringFormat(" - Profit / Wins     : %d (%.2f%%)", g_winCount, winRate));
   Print(StringFormat(" - Break-Even (BEP)  : %d (%.2f%%)", g_bepCount, bepRate));
   Print(StringFormat(" - Partial Closures  : %d trade diamankan 50%%", g_partialCloseCount));
   Print(StringFormat(" - Total Loss        : %d (%.2f%%)", g_normalLossCount + g_falseSignalCount, lossRate));
   Print("-----------------------------------------------------------------------");
   Print(StringFormat(" * FALSE SIGNALS (Trap/Fakeout MFE < %.1fR) : %d (%.2f%%)", InpFalseSignalMFEThreshold, g_falseSignalCount, falseRate));
   Print(StringFormat(" * Normal Losses (Failed Continuation)      : %d (%.2f%%)", g_normalLossCount, normRate));
   Print(StringFormat(" * Signal Follow-Through Rate (MFE >= %.1fR): %d (%.2f%%)", InpFalseSignalMFEThreshold, g_totalClosedTrades - g_falseSignalCount, 100.0 - falseRate));
   Print("-----------------------------------------------------------------------");
   Print("Breakdown False Signal per Pola Candlestick:");
   Print(StringFormat(" - Pinbar / Hammer / Shooting Star : %d", g_falsePerPatternPinbar));
   Print(StringFormat(" - Engulfing (Bullish / Bearish)   : %d", g_falsePerPatternEngulfing));
   Print(StringFormat(" - Inside Bar Breakout             : %d", g_falsePerPatternInside));
   Print(StringFormat(" - Pola Candlestick Lainnya        : %d", g_falsePerPatternOther));
   Print("-----------------------------------------------------------------------");
   Print("Breakdown False Signal per Sesi Pasar:");
   Print(StringFormat(" - Sesi London                     : %d", g_falsePerSessionLondon));
   Print(StringFormat(" - Sesi New York                   : %d", g_falsePerSessionNY));
   Print(StringFormat(" - Sesi Asian / Sydney             : %d", g_falsePerSessionAsia));
   Print("=======================================================================");
  }

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   Comment(""); // Bersihkan teks comment chart agar tampilan bersih
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
   handle_rsi    = iRSI(_Symbol, _Period, InpRSI_Period, PRICE_CLOSE);

   if(handle_ema8 == INVALID_HANDLE || handle_ema21 == INVALID_HANDLE ||
      handle_ema125 == INVALID_HANDLE || handle_atr == INVALID_HANDLE ||
      handle_adx == INVALID_HANDLE || handle_rsi == INVALID_HANDLE)
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

   // Inisialisasi Handle Sistem 3 Layar (Triple Screen)
   if(InpUseTripleScreen)
     {
      handle_screen1_ema = iMA(_Symbol, InpScreen1_TF, InpScreen1_EMA, 0, MODE_EMA, PRICE_CLOSE);
      handle_screen2_ema = iMA(_Symbol, InpScreen2_TF, InpScreen2_EMA, 0, MODE_EMA, PRICE_CLOSE);
      if(handle_screen1_ema == INVALID_HANDLE || handle_screen2_ema == INVALID_HANDLE)
        {
         Print("[EA Warning] Gagal menginisialisasi handle Triple Screen (H1/M15).");
        }
     }
   else
     {
      handle_screen1_ema = INVALID_HANDLE;
      handle_screen2_ema = INVALID_HANDLE;
     }

   // Konfigurasi struktur pasar & filter
   structureAnalyzer.Configure(50, InpChopBars, InpMaxEmaCrosses, InpWhipsawBars, InpMaxWhipsawCrosses, InpMaxAtrMultiplier);

   // Sinkronisasi riwayat transaksi awal
   SyncClosedTradesFromHistory();

   Print(StringFormat("[EA Started] Triple EMA Pullback System v2.0 aktif pada %s %s (HTF: %s) | Magic: %d",
                      _Symbol, EnumToString(_Period), EnumToString(effectiveHTF), InpMagicNumber));

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // Cetak audit False Signal komprehensif ke log
   PrintAuditReport();
   Comment(""); // Bersihkan HUD

   IndicatorRelease(handle_ema8);
   IndicatorRelease(handle_ema21);
   IndicatorRelease(handle_ema125);
   IndicatorRelease(handle_atr);
   if(handle_adx != INVALID_HANDLE)
     {
      IndicatorRelease(handle_adx);
      handle_adx = INVALID_HANDLE;
     }
   if(handle_rsi != INVALID_HANDLE)
     {
      IndicatorRelease(handle_rsi);
      handle_rsi = INVALID_HANDLE;
     }
   if(handle_htf_ema != INVALID_HANDLE)
     {
      IndicatorRelease(handle_htf_ema);
      handle_htf_ema = INVALID_HANDLE;
     }
   if(handle_screen1_ema != INVALID_HANDLE)
     {
      IndicatorRelease(handle_screen1_ema);
      handle_screen1_ema = INVALID_HANDLE;
     }
   if(handle_screen2_ema != INVALID_HANDLE)
     {
      IndicatorRelease(handle_screen2_ema);
      handle_screen2_ema = INVALID_HANDLE;
     }
   Print("[EA Stopped] Triple EMA Pullback EA dimatikan. Reason: ", reason);
  }

//+------------------------------------------------------------------+
//| Trade transaction handler                                        |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
     {
      ulong dealTicket = trans.deal;
      if(HistoryDealSelect(dealTicket))
        {
         if(HistoryDealGetString(dealTicket, DEAL_SYMBOL) == _Symbol &&
            HistoryDealGetInteger(dealTicket, DEAL_MAGIC) == InpMagicNumber &&
            HistoryDealGetInteger(dealTicket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
           {
            long posId = HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);
            double profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT) + 
                            HistoryDealGetDouble(dealTicket, DEAL_SWAP) + 
                            HistoryDealGetDouble(dealTicket, DEAL_COMMISSION);
            datetime dealTime = (datetime)HistoryDealGetInteger(dealTicket, DEAL_TIME);
            EvaluateClosedTrade(posId, profit, dealTime);
           }
        }
     }
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

   // Bypass di tester jika diminta
   bool isTester = (bool)MQLInfoInteger(MQL_TESTER);
   if(InpDisableCircuitBreakerInTester && (isTester || InpAllowUnlimitedTrades))
      return false;

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
//| Evaluasi Layar 1: Arah Tren Besar Institusi (Macro Bias H1)      |
//+------------------------------------------------------------------+
bool EvaluateScreen1MacroBias(bool isBuy, string &outReason)
  {
   if(!InpUseTripleScreen || handle_screen1_ema == INVALID_HANDLE) return true;

   MqlRates h1Rates[];
   double h1Ema[];
   ArraySetAsSeries(h1Rates, true);
   ArraySetAsSeries(h1Ema, true);

   int cRates = CopyRates(_Symbol, InpScreen1_TF, 0, 5, h1Rates);
   int cEma   = CopyBuffer(handle_screen1_ema, 0, 0, 5, h1Ema);

   if(cRates < 2 || cEma < 2)
     {
      outReason = StringFormat("Syncing %s Data...", EnumToString(InpScreen1_TF));
      return false;
     }

   if(isBuy)
     {
      if(h1Rates[1].close < h1Ema[1])
        {
         outReason = StringFormat("Layar 1 (%s) Macro Bearish (Close %.2f < EMA%d %.2f)",
                                  EnumToString(InpScreen1_TF), h1Rates[1].close, InpScreen1_EMA, h1Ema[1]);
         return false;
        }
     }
   else
     {
      if(h1Rates[1].close > h1Ema[1])
        {
         outReason = StringFormat("Layar 1 (%s) Macro Bullish (Close %.2f > EMA%d %.2f)",
                                  EnumToString(InpScreen1_TF), h1Rates[1].close, InpScreen1_EMA, h1Ema[1]);
         return false;
        }
     }

   return true;
  }

//+------------------------------------------------------------------+
//| Evaluasi Layar 2: Konfirmasi Struktur Ayunan & Level Kunci M15   |
//+------------------------------------------------------------------+
bool EvaluateScreen2MarketStructure(bool isBuy, string &outReason)
  {
   if(!InpUseTripleScreen) return true;

   MqlRates m15Rates[];
   ArraySetAsSeries(m15Rates, true);
   int cRates = CopyRates(_Symbol, InpScreen2_TF, 0, 55, m15Rates);
   if(cRates < 30)
     {
      outReason = StringFormat("Syncing %s Data...", EnumToString(InpScreen2_TF));
      return false;
     }

   // 1. Cek Struktur Ayunan M15 (HH-HL vs LH-LL)
   if(InpScreen2_RequireStruct)
     {
      ENUM_MARKET_STRUCTURE m15_struct = structureAnalyzer.AnalyzeStructure(m15Rates, cRates, 1);
      if(isBuy && m15_struct == STRUCTURE_BEARISH_LH_LL)
        {
         outReason = StringFormat("Layar 2 (%s) Struktur Bearish (LH-LL). Dilarang BUY melawan ayunan M15.", EnumToString(InpScreen2_TF));
         return false;
        }
      if(!isBuy && m15_struct == STRUCTURE_BULLISH_HH_HL)
        {
         outReason = StringFormat("Layar 2 (%s) Struktur Bullish (HH-HL). Dilarang SELL melawan ayunan M15.", EnumToString(InpScreen2_TF));
         return false;
        }
     }

   // 2. Cek Level Kunci EMA M15
   if(InpScreen2_RequireKeyLevel && handle_screen2_ema != INVALID_HANDLE)
     {
      double m15Ema[];
      ArraySetAsSeries(m15Ema, true);
      int cEma = CopyBuffer(handle_screen2_ema, 0, 0, 5, m15Ema);
      if(cEma >= 2)
        {
         if(isBuy && m15Rates[1].close < m15Ema[1])
           {
            outReason = StringFormat("Layar 2 (%s) di bawah Level Kunci EMA %d (%.2f < %.2f)",
                                     EnumToString(InpScreen2_TF), InpScreen2_EMA, m15Rates[1].close, m15Ema[1]);
            return false;
           }
         if(!isBuy && m15Rates[1].close > m15Ema[1])
           {
            outReason = StringFormat("Layar 2 (%s) di atas Level Kunci EMA %d (%.2f > %.2f)",
                                     EnumToString(InpScreen2_TF), InpScreen2_EMA, m15Rates[1].close, m15Ema[1]);
            return false;
           }
        }
     }

   return true;
  }

//+------------------------------------------------------------------+
//| Hitung Skor Konfluensi & Grade Kualitas Setup BUY                |
//+------------------------------------------------------------------+
int CalculateBuyConfluenceScore(const MqlRates &rates[], int totalRates, const double &rsiBuf[],
                                const double &adxBuf[], double currentRsi,
                                const double &e8Series[], const double &e21Series[], const double &e125Series[],
                                double currentAtr, string &outDetails, string &outGrade)
  {
   int score = 0;
   outDetails = "";

   // 1. Fibonacci Golden Zone (50% - 78.6%)
   bool isFibo = IsFiboGoldenZoneBuy(rates, totalRates, 1);
   if(isFibo)
     {
      score += InpScoreWeightFibo;
      outDetails += "Fibo+";
     }

   // 2. RSI Momentum Sehat (45 - 70) & Hidden Divergence
   bool isRsi = IsRsiValidBuy(currentRsi);
   bool isRsiDiv = (InpUseRsiDivergence) ? CheckRsiHiddenDivergence(rates, rsiBuf, true, 1) : false;
   if(isRsi || isRsiDiv)
     {
      score += InpScoreWeightRSI;
      outDetails += (isRsiDiv ? "RSI_Div+" : "RSI+");
     }

   // 3. Fair Value Gap (FVG Mitigation)
   bool isFvg = HasActiveFVG(rates, totalRates, true, 1);
   if(isFvg)
     {
      score += InpScoreWeightFVG;
      outDetails += "FVG+";
     }

   // 4. ADX Trend Strength (>= 20)
   bool isAdx = (ArraySize(adxBuf) >= 2 && adxBuf[1] >= InpMinADXLevel);
   if(isAdx)
     {
      score += InpScoreWeightADX;
      outDetails += "ADX+";
     }

   // 5. Market Structure & False Signal Filter (HH-HL)
   ENUM_FILTER_RESULT structRes = structureAnalyzer.ValidateBuyFilters(
      rates, totalRates, e8Series, e21Series, e125Series, currentAtr, InpUseStructureFilter, 1
   );
   if(structRes == FILTER_PASS)
     {
      score += InpScoreWeightStructure;
      outDetails += "Struct+";
     }

   if(StringLen(outDetails) > 0 && StringSubstr(outDetails, StringLen(outDetails) - 1, 1) == "+")
      outDetails = StringSubstr(outDetails, 0, StringLen(outDetails) - 1);

   // Tentukan Grade Setup
   if(score >= 80)      outGrade = "A+";
   else if(score >= 60) outGrade = "A";
   else if(score >= 40) outGrade = "B";
   else                 outGrade = "C";

   return score;
  }

//+------------------------------------------------------------------+
//| Hitung Skor Konfluensi & Grade Kualitas Setup SELL               |
//+------------------------------------------------------------------+
int CalculateSellConfluenceScore(const MqlRates &rates[], int totalRates, const double &rsiBuf[],
                                 const double &adxBuf[], double currentRsi,
                                 const double &e8Series[], const double &e21Series[], const double &e125Series[],
                                 double currentAtr, string &outDetails, string &outGrade)
  {
   int score = 0;
   outDetails = "";

   // 1. Fibonacci Golden Zone (50% - 78.6%)
   bool isFibo = IsFiboGoldenZoneSell(rates, totalRates, 1);
   if(isFibo)
     {
      score += InpScoreWeightFibo;
      outDetails += "Fibo+";
     }

   // 2. RSI Momentum Sehat (30 - 55) & Hidden Divergence
   bool isRsi = IsRsiValidSell(currentRsi);
   bool isRsiDiv = (InpUseRsiDivergence) ? CheckRsiHiddenDivergence(rates, rsiBuf, false, 1) : false;
   if(isRsi || isRsiDiv)
     {
      score += InpScoreWeightRSI;
      outDetails += (isRsiDiv ? "RSI_Div+" : "RSI+");
     }

   // 3. Fair Value Gap (FVG Mitigation)
   bool isFvg = HasActiveFVG(rates, totalRates, false, 1);
   if(isFvg)
     {
      score += InpScoreWeightFVG;
      outDetails += "FVG+";
     }

   // 4. ADX Trend Strength (>= 20)
   bool isAdx = (ArraySize(adxBuf) >= 2 && adxBuf[1] >= InpMinADXLevel);
   if(isAdx)
     {
      score += InpScoreWeightADX;
      outDetails += "ADX+";
     }

   // 5. Market Structure & False Signal Filter (LH-LL)
   ENUM_FILTER_RESULT structRes = structureAnalyzer.ValidateSellFilters(
      rates, totalRates, e8Series, e21Series, e125Series, currentAtr, InpUseStructureFilter, 1
   );
   if(structRes == FILTER_PASS)
     {
      score += InpScoreWeightStructure;
      outDetails += "Struct+";
     }

   if(StringLen(outDetails) > 0 && StringSubstr(outDetails, StringLen(outDetails) - 1, 1) == "+")
      outDetails = StringSubstr(outDetails, 0, StringLen(outDetails) - 1);

   // Tentukan Grade Setup
   if(score >= 80)      outGrade = "A+";
   else if(score >= 60) outGrade = "A";
   else if(score >= 40) outGrade = "B";
   else                 outGrade = "C";

   return score;
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
//| Kelola Break-Even, Trailing Stop, dan MFE Posisi Terbuka         |
//+------------------------------------------------------------------+
void ManageOpenTrades(double currentEma21, double currentAtr)
  {
   MqlDateTime dt;
   TimeCurrent(dt);
   string currentSession = GetMarketSessionName(dt.hour);

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(!positionInfo.SelectByIndex(i)) continue;
      if(positionInfo.Symbol() != _Symbol || positionInfo.Magic() != InpMagicNumber) continue;

      ulong ticket        = positionInfo.Ticket();
      long posId          = positionInfo.Identifier();
      double openPrice    = positionInfo.PriceOpen();
      double currentSL    = positionInfo.StopLoss();
      double currentTP    = positionInfo.TakeProfit();
      double currentPrice = positionInfo.PriceCurrent();
      ENUM_POSITION_TYPE posType = positionInfo.PositionType();

      // Registrasi otomatis jika posisi belum tercatat di tracker
      RegisterTrackedTrade(ticket, posId, posType, openPrice, currentSL, currentTP, positionInfo.Comment(), currentSession);

      // Perbarui MFE (Maximum Favorable Excursion) untuk audit False Signal
      UpdateTrackedTradeMFE(ticket, posId, currentPrice);

      // Jarak awal SL dalam points
      double initialSLDistance = MathAbs(openPrice - currentSL);
      if(initialSLDistance <= 0.0) initialSLDistance = InpMinSLPoints * _Point;

      // Jarak minimum stop level broker (proteksi error 10016)
      long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
      double minDist  = MathMax(stopsLevel * _Point, 15 * _Point);

      // Hitung profit distance saat ini dan rasio R:R
      double profitDistance = 0.0;
      if(posType == POSITION_TYPE_BUY) profitDistance = currentPrice - openPrice;
      else if(posType == POSITION_TYPE_SELL) profitDistance = openPrice - currentPrice;
      double currentR = (initialSLDistance > 0.0) ? profitDistance / initialSLDistance : 0.0;

      // 1. PARTIAL TAKE PROFIT (SCALE-OUT 50% DI 1:1 R:R)
      int trackIdx = -1;
      for(int t = 0; t < ArraySize(trackedTrades); t++)
        {
         if(!trackedTrades[t].isClosed && 
            ((ticket > 0 && trackedTrades[t].ticket == ticket) || 
             (posId > 0 && trackedTrades[t].positionId == posId)))
           {
            trackIdx = t;
            break;
           }
        }

      if(InpUsePartialClose && trackIdx >= 0 && !trackedTrades[trackIdx].isPartialClosed && currentR >= InpPartialCloseRR)
        {
         double currentVol = positionInfo.Volume();
         double minLot     = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
         double stepLot    = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
         double closeLot   = MathFloor((currentVol * (InpPartialClosePercent / 100.0)) / stepLot) * stepLot;
         closeLot          = NormalizeDouble(closeLot, 2);

         if(closeLot >= minLot && (currentVol - closeLot) >= minLot)
           {
            if(trade.PositionClosePartial(ticket, closeLot))
              {
               trackedTrades[trackIdx].isPartialClosed = true;
               g_partialCloseCount++;
               Print(StringFormat("[PARTIAL CLOSE 50%% SUKSES] Posisi #%I64u tutup %.2f lot @ %.2f (Sisa %.2f lot). Profit tunai diamankan!",
                                  ticket, closeLot, currentPrice, currentVol - closeLot));
              }
            else
              {
               Print(StringFormat("[PARTIAL CLOSE ERROR] Gagal menutup sebagian posisi #%I64u: %s", ticket, trade.ResultRetcodeDescription()));
              }
           }
         else
           {
            trackedTrades[trackIdx].isPartialClosed = true;
           }
        }

      // 2. AUTO BREAK-EVEN (Aktif saat mencapai InpBE_TriggerRR atau sesaat setelah Partial Close)
      bool triggerBEP = (InpUseBreakEven && (currentR >= InpBE_TriggerRR || (trackIdx >= 0 && trackedTrades[trackIdx].isPartialClosed)));
      if(triggerBEP)
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

   // Salin EMA & indikator series
   double ema8[], ema21[], ema125[], atr[], rsi[];
   ArraySetAsSeries(ema8, true);
   ArraySetAsSeries(ema21, true);
   ArraySetAsSeries(ema125, true);
   ArraySetAsSeries(atr, true);
   ArraySetAsSeries(rsi, true);

   CopyBuffer(handle_ema8, 0, 0, 30, ema8);
   CopyBuffer(handle_ema21, 0, 0, 30, ema21);
   CopyBuffer(handle_ema125, 0, 0, 30, ema125);
   CopyBuffer(handle_atr, 0, 0, 5, atr);
   CopyBuffer(handle_rsi, 0, 0, 30, rsi);

   double currentAtr = (ArraySize(atr) > 1) ? atr[1] : 1.0 * _Point;
   double currentRsi = (ArraySize(rsi) > 1) ? rsi[1] : 50.0;

   // Evaluasi lonjakan volatilitas (Fundamental News Shock) & News Window
   bool isFundamentalShock = IsFundamentalShockActive(rates, currentAtr);
   bool isNewsWindow        = IsNewsWindowActive();

   // Update Chart HUD Telemetri secara live
   UpdateChartHUD(currentAtr, currentRsi, isFundamentalShock, isNewsWindow);

   // Delay visual mode jika diatur agar pergerakan playback chart santai
   if(MQLInfoInteger(MQL_VISUAL_MODE) && InpVisualDelayMs > 0)
     {
      Sleep(InpVisualDelayMs);
     }

   // Kelola posisi aktif (Break-Even, Trailing Stop, dan MFE) pada setiap tick
   ManageOpenTrades(ema21[0], currentAtr);

   // Proteksi Gap Akhir Pekan: Tutup posisi otomatis jika sudah masuk Jumat malam
   CheckFridayAutoClose();

   // Cek apakah ada candle baru (Sinyal dieksekusi sekali saat candle baru buka)
   datetime currentBarTime = rates[0].time;
   if(currentBarTime == lastTradeBarTime)
     {
      return; // Sudah diperiksa pada candle ini
     }

   // Cek batas maksimum posisi (diabaikan jika Mode Backtest Bebas aktif)
   if(!InpAllowUnlimitedTrades && CountOpenPositions() >= InpMaxOpenPositions)
     {
      static datetime lastMaxPosLog = 0;
      if(rates[0].time != lastMaxPosLog)
        {
         Print(StringFormat("[INFO POSISI] Batas maksimum posisi tercapai (%d/%d). Sinyal baru dilewati hingga posisi aktif selesai.",
                            CountOpenPositions(), InpMaxOpenPositions));
         lastMaxPosLog = rates[0].time;
        }
      return;
     }

   // Cek filter waktu
   if(!IsTradingTimeAllowed())
     {
      return;
     }

   // Cek filter sesi pasar XAUUSD
   if(!IsSessionFilterAllowed())
     {
      return;
     }

   // Cek filter berita fundamental (Shock & Blackout Window)
   if(isNewsWindow)
     {
      Print("[FILTER BERITA] Jendela waktu rilis berita ekonomi AS aktif. Menghindari false signal.");
      return;
     }

   if(isFundamentalShock)
     {
      Print("[FILTER BERITA] Lonjakan shock candle (> 2.5x ATR) terdeteksi dalam 4 bar terakhir. Menunggu pasar stabil.");
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

   // Deteksi Pola Price Action Candlestick (Pullback Rejection)
   ENUM_CANDLE_PATTERN bullPattern = patternDetector.DetectBullishPattern(rates, 1, e8_1, e21_1, e125_1);
   ENUM_CANDLE_PATTERN bearPattern = patternDetector.DetectBearishPattern(rates, 1, e8_1, e21_1, e125_1);

   // Deteksi Strategi Tambahan: Momentum Breakout (Penembusan Range Lookback)
   double bullBreakLevel = 0.0;
   double bearBreakLevel = 0.0;
   bool isBullBreakout = DetectBullishBreakout(rates, copied, 1, InpBreakoutLookbackBars, InpBreakoutMinBodyRatio, bullBreakLevel);
   bool isBearBreakout = DetectBearishBreakout(rates, copied, 1, InpBreakoutLookbackBars, InpBreakoutMinBodyRatio, bearBreakLevel);

   // Volume candle konfirmasi bar 1
   long vol_bar1 = (rates[1].real_volume > 0) ? rates[1].real_volume : rates[1].tick_volume;
   double sumVol = 0;
   int volLookback = MathMin(InpVolumeLookback, copied - 2);
   for(int v = 2; v < 2 + volLookback; v++)
     {
      long vVal = (rates[v].real_volume > 0) ? rates[v].real_volume : rates[v].tick_volume;
      sumVol += (double)vVal;
     }
   double avgVol = (volLookback > 0) ? (sumVol / volLookback) : 1.0;
   double volRatio = (avgVol > 0) ? ((double)vol_bar1 / avgVol) : 1.0;
   bool volumeOk = (!InpUseVolumeFilter || (vol_bar1 >= (avgVol * InpVolumeMultiplier)));

   // Filter volume khusus breakout
   bool breakoutVolOk = (!InpBreakoutRequireVolume || (vol_bar1 >= (avgVol * InpBreakoutVolMult)));
   if(!breakoutVolOk)
     {
      isBullBreakout = false;
      isBearBreakout = false;
     }

   // Deteksi Strategi Tambahan: SMC Institutional (Liquidity Sweep & Value Zone)
   double smcBullLevel = 0.0, smcBearLevel = 0.0;
   string smcBullInfo = "", smcBearInfo = "";
   bool isSmcBull = (bullPattern == PATTERN_NONE && !isBullBreakout) && DetectSmcBullishSetup(rates, copied, 1, smcBullLevel, smcBullInfo);
   bool isSmcBear = (bearPattern == PATTERN_NONE && !isBearBreakout) && DetectSmcBearishSetup(rates, copied, 1, smcBearLevel, smcBearInfo);

   bool hasBuySignal  = (bullPattern != PATTERN_NONE) || isBullBreakout || isSmcBull;
   bool hasSellSignal = (bearPattern != PATTERN_NONE) || isBearBreakout || isSmcBear;
   bool isBuyBreakoutTrigger  = (bullPattern == PATTERN_NONE && isBullBreakout);
   bool isSellBreakoutTrigger = (bearPattern == PATTERN_NONE && isBearBreakout);
   bool isBuySmcTrigger       = (bullPattern == PATTERN_NONE && !isBullBreakout && isSmcBull);
   bool isSellSmcTrigger      = (bearPattern == PATTERN_NONE && !isBearBreakout && isSmcBear);

   // Syarat Tambahan: Strong Close & EMA Slope
   bool strongCloseBuy  = (!InpRequireStrongClose || (rates[1].close > e8_1 && rates[1].close > rates[1].open));
   bool strongCloseSell = (!InpRequireStrongClose || (rates[1].close < e8_1 && rates[1].close < rates[1].open));
   bool slopeBuyOk      = (!InpRequireEmaSlope || (e8_1 > ema8[2]));
   bool slopeSellOk     = (!InpRequireEmaSlope || (e8_1 < ema8[2]));

   // Cooldown bar sinyal
   bool bypassCooldown = InpIgnoreCooldownInTester && ((bool)MQLInfoInteger(MQL_TESTER) || InpAllowUnlimitedTrades);
   bool cooldownBuyOk   = bypassCooldown || (lastBuyTradeTime == 0 || (rates[1].time - lastBuyTradeTime >= PeriodSeconds() * InpSignalCooldownBars));
   bool cooldownSellOk  = bypassCooldown || (lastSellTradeTime == 0 || (rates[1].time - lastSellTradeTime >= PeriodSeconds() * InpSignalCooldownBars));

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
   // EKSEKUSI SINYAL BUY (PULLBACK & BREAKOUT)
   // ==========================================
   if(hasBuySignal)
     {
      // 1. Syarat Tren: Harga di atas EMA 125 dan EMA 8 di atas EMA 21
      bool trendBullish = (isBuyBreakoutTrigger || isBuySmcTrigger) ? 
         (rates[1].close > e125_1 && e8_1 > e21_1 && rates[1].close > e8_1) :
         (rates[1].close > e125_1 && e8_1 > e21_1 && rates[1].low > e125_1);

      string s1Reason = "", s2Reason = "";
      if(!trendBullish)
        {
         Print("[BUY FILTERED] Trend/EMA Misalignment");
        }
      else if(InpUseTripleScreen && !EvaluateScreen1MacroBias(true, s1Reason))
        {
         Print("[BUY FILTERED] ", s1Reason);
        }
      else if(InpUseTripleScreen && !isBuyBreakoutTrigger && !isBuySmcTrigger && !EvaluateScreen2MarketStructure(true, s2Reason))
        {
         Print("[BUY FILTERED] ", s2Reason);
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
      else if(!volumeOk)
        {
         Print(StringFormat("[BUY FILTERED] Low Volume (%d < %.0f Avg)", vol_bar1, avgVol * InpVolumeMultiplier));
        }
      else
        {
         // 2. Evaluasi Sistem Skor Konfluensi & Grade Kualitas
         string confDetails = "", confGrade = "A";
         int confScore = 100;

         if(isBuyBreakoutTrigger)
           {
            confScore = CalculateBreakoutConfluenceScore(true, currentRsi, (cAdx >= 2) ? adxBuf[1] : 20.0, volRatio, confDetails, confGrade);
           }
         else if(isBuySmcTrigger)
           {
            confScore = CalculateSmcConfluenceScore(true, currentRsi, (cAdx >= 2) ? adxBuf[1] : 20.0, volRatio, smcBullInfo, confDetails, confGrade);
           }
         else if(InpUseConfluenceScoring)
           {
            confScore = CalculateBuyConfluenceScore(rates, copied, rsi, adxBuf, currentRsi, ema8, ema21, ema125, currentAtr, confDetails, confGrade);
            if(confScore < InpMinConfluenceScore)
              {
               Print(StringFormat("[BUY FILTERED] Skor Konfluensi Rendah (%d/100, Grade %s < Min %d). Filter: [%s]",
                                  confScore, confGrade, InpMinConfluenceScore, confDetails));
               return;
              }
           }
         else
           {
            // Mode Tradisional: Semua filter tambahan wajib lulus
            if(!adxTrendOk) { Print("[BUY FILTERED] ADX Tren Lemah"); return; }
            if(!IsFiboGoldenZoneBuy(rates, copied, 1)) { Print("[BUY FILTERED] Retracement di luar Fibo Golden Zone"); return; }
            if(!IsRsiValidBuy(currentRsi)) { Print("[BUY FILTERED] RSI Momentum tidak ideal"); return; }
            if(InpUseRsiDivergence && !CheckRsiHiddenDivergence(rates, rsi, true, 1)) { Print("[BUY FILTERED] Tidak ada RSI Divergence"); return; }
            if(InpUseFVGFilter && !HasActiveFVG(rates, copied, true, 1)) { Print("[BUY FILTERED] Tidak ada mitigasi FVG"); return; }
            ENUM_FILTER_RESULT res = structureAnalyzer.ValidateBuyFilters(rates, copied, ema8, ema21, ema125, currentAtr, InpUseStructureFilter, 1);
            if(res != FILTER_PASS) { Print("[BUY FILTERED] ", FilterResultToString(res)); return; }
           }

         // Hitung Stop Loss Dinamis XAUUSD Berbasis ATR & Buffer
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double slPrice = 0.0;
         double minSlDist = MathMax(InpMinSLPoints * _Point, InpXauMinSlAtrMult * currentAtr);
         double slBuffer  = MathMax(InpSL_BufferPoints * _Point, 0.25 * currentAtr);

         if(isBuyBreakoutTrigger)
           {
            // Untuk breakout: SL diletakkan di bawah low candle penembus atau candle sebelumnya
            double lowestLow = MathMin(rates[1].low, rates[2].low);
            slPrice = lowestLow - slBuffer;
           }
         else if(isBuySmcTrigger)
           {
            // Untuk SMC: SL diletakkan di bawah level sweep likuiditas / low candle
            double lowestLow = MathMin(smcBullLevel, rates[1].low);
            slPrice = lowestLow - slBuffer;
           }
         else if(InpSLMode == SL_SWING_CANDLE)
           {
            double lowestLow = MathMin(rates[1].low, MathMin(rates[2].low, rates[3].low));
            slPrice = lowestLow - slBuffer;
           }
         else if(InpSLMode == SL_ATR_BASED)
           {
            slPrice = ask - (InpSL_AtrMultiplier * currentAtr);
           }
         else
           {
            slPrice = ask - (InpSL_FixedPoints * _Point);
           }

         // Pastikan jarak SL memenuhi standar minimal dinamis
         double slDist = ask - slPrice;
         if(slDist < minSlDist)
           {
            slPrice = ask - minSlDist;
            slDist = minSlDist;
           }
         double slDistPoints = slDist / _Point;

         // Filter Batas Maksimal SL (Tolak jika terlalu lebar / overextended)
         if(InpMaxSLPoints > 0 && slDistPoints > InpMaxSLPoints)
           {
            Print(StringFormat("[BUY FILTERED] Stop Loss Terlalu Lebar (%.0f > %d pts). Setup Overextended.", slDistPoints, InpMaxSLPoints));
            return;
           }

         // Filter Rintangan Support/Resistance Mayor (Obstacle Blocking)
         string snrReasonBuy = "";
         if(!isBuyBreakoutTrigger && !isBuySmcTrigger && IsObstacleBlocking(true, ask, slDist, rates, copied, snrReasonBuy))
           {
            Print("[BUY FILTERED] ", snrReasonBuy);
            return;
           }

         // Hitung Take Profit berbasis Risk:Reward
         double tpPrice = ask + (slDist * InpRiskRewardRatio);

         // Hitung Lot Sizing
         double lot = CalculateLotSize(slDistPoints);
         if(InpUseConfluenceScoring && InpUseDynamicGradeSizing)
           {
            if(confGrade == "A")       lot = NormalizeDouble(lot * 0.75, 2);
            else if(confGrade == "B")  lot = NormalizeDouble(lot * 0.50, 2);
            lot = MathMax(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), lot);
           }

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         string patternStr = (bullPattern != PATTERN_NONE) ? GetPatternName(bullPattern) : 
                             (isBuyBreakoutTrigger ? StringFormat("Breakout_H%d", InpBreakoutLookbackBars) : "SMC_Institutional");
         MqlDateTime barDt;
         TimeToStruct(rates[1].time, barDt);
         string sessionStr = GetMarketSessionName(barDt.hour);
         string orderPrefix = isBuyBreakoutTrigger ? "TripleEMA_XAU_Breakout" : 
                              (isBuySmcTrigger ? "TripleEMA_XAU_SMC" : InpOrderComment);
         string comment = StringFormat("%s_%s_%s", orderPrefix, confGrade, patternStr);

         if(trade.Buy(lot, _Symbol, ask, slPrice, tpPrice, comment))
           {
            lastBuyTradeTime = rates[1].time;
            ulong newTicket = trade.ResultOrder();
            if(newTicket == 0) newTicket = trade.ResultDeal();
            RegisterTrackedTrade(newTicket, 0, POSITION_TYPE_BUY, ask, slPrice, tpPrice, patternStr, sessionStr);
            Print(StringFormat("[ORDER BUY SUKSES (%s) | Grade %s (Skor %d) | %s] Lot: %.2f | Ask: %f | SL: %f | TP: %f | Sesi: %s",
                               isBuyBreakoutTrigger ? "MOMENTUM BREAKOUT" : (isBuySmcTrigger ? "SMC INSTITUTIONAL" : "PULLBACK"),
                               confGrade, confScore, confDetails, lot, ask, slPrice, tpPrice, sessionStr));
           }
         else
           {
            Print("[ORDER BUY GAGAL] Error: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
           }
        }
     }

   // ==========================================
   // EKSEKUSI SINYAL SELL (PULLBACK & BREAKOUT)
   // ==========================================
   else if(hasSellSignal)
     {
      // 1. Syarat Tren: Harga di bawah EMA 125 dan EMA 8 di bawah EMA 21
      bool trendBearish = (isSellBreakoutTrigger || isSellSmcTrigger) ?
         (rates[1].close < e125_1 && e8_1 < e21_1 && rates[1].close < e8_1) :
         (rates[1].close < e125_1 && e8_1 < e21_1 && rates[1].high < e125_1);

      string s1Reason = "", s2Reason = "";
      if(!trendBearish)
        {
         Print("[SELL FILTERED] Trend/EMA Misalignment");
        }
      else if(InpUseTripleScreen && !EvaluateScreen1MacroBias(false, s1Reason))
        {
         Print("[SELL FILTERED] ", s1Reason);
        }
      else if(InpUseTripleScreen && !isSellBreakoutTrigger && !isSellSmcTrigger && !EvaluateScreen2MarketStructure(false, s2Reason))
        {
         Print("[SELL FILTERED] ", s2Reason);
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
      else if(!volumeOk)
        {
         Print(StringFormat("[SELL FILTERED] Low Volume (%d < %.0f Avg)", vol_bar1, avgVol * InpVolumeMultiplier));
        }
      else
        {
         // 2. Evaluasi Sistem Skor Konfluensi & Grade Kualitas
         string confDetails = "", confGrade = "A";
         int confScore = 100;

         if(isSellBreakoutTrigger)
           {
            confScore = CalculateBreakoutConfluenceScore(false, currentRsi, (cAdx >= 2) ? adxBuf[1] : 20.0, volRatio, confDetails, confGrade);
           }
         else if(isSellSmcTrigger)
           {
            confScore = CalculateSmcConfluenceScore(false, currentRsi, (cAdx >= 2) ? adxBuf[1] : 20.0, volRatio, smcBearInfo, confDetails, confGrade);
           }
         else if(InpUseConfluenceScoring)
           {
            confScore = CalculateSellConfluenceScore(rates, copied, rsi, adxBuf, currentRsi, ema8, ema21, ema125, currentAtr, confDetails, confGrade);
            if(confScore < InpMinConfluenceScore)
              {
               Print(StringFormat("[SELL FILTERED] Skor Konfluensi Rendah (%d/100, Grade %s < Min %d). Filter: [%s]",
                                  confScore, confGrade, InpMinConfluenceScore, confDetails));
               return;
              }
           }
         else
           {
            // Mode Tradisional: Semua filter tambahan wajib lulus
            if(!adxTrendOk) { Print("[SELL FILTERED] ADX Tren Lemah"); return; }
            if(!IsFiboGoldenZoneSell(rates, copied, 1)) { Print("[SELL FILTERED] Retracement di luar Fibo Golden Zone"); return; }
            if(!IsRsiValidSell(currentRsi)) { Print("[SELL FILTERED] RSI Momentum tidak ideal"); return; }
            if(InpUseRsiDivergence && !CheckRsiHiddenDivergence(rates, rsi, false, 1)) { Print("[SELL FILTERED] Tidak ada RSI Divergence"); return; }
            if(InpUseFVGFilter && !HasActiveFVG(rates, copied, false, 1)) { Print("[SELL FILTERED] Tidak ada mitigasi FVG"); return; }
            ENUM_FILTER_RESULT res = structureAnalyzer.ValidateSellFilters(rates, copied, ema8, ema21, ema125, currentAtr, InpUseStructureFilter, 1);
            if(res != FILTER_PASS) { Print("[SELL FILTERED] ", FilterResultToString(res)); return; }
           }

         // Hitung Stop Loss Dinamis XAUUSD Berbasis ATR & Buffer
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double slPrice = 0.0;
         double minSlDist = MathMax(InpMinSLPoints * _Point, InpXauMinSlAtrMult * currentAtr);
         double slBuffer  = MathMax(InpSL_BufferPoints * _Point, 0.25 * currentAtr);

         if(isSellBreakoutTrigger)
           {
            // Untuk breakout: SL diletakkan di atas high candle penembus atau candle sebelumnya
            double highestHigh = MathMax(rates[1].high, rates[2].high);
            slPrice = highestHigh + slBuffer;
           }
         else if(isSellSmcTrigger)
           {
            // Untuk SMC: SL diletakkan di atas level sweep likuiditas / high candle
            double highestHigh = MathMax(smcBearLevel, rates[1].high);
            slPrice = highestHigh + slBuffer;
           }
         else if(InpSLMode == SL_SWING_CANDLE)
           {
            double highestHigh = MathMax(rates[1].high, MathMax(rates[2].high, rates[3].high));
            slPrice = highestHigh + slBuffer;
           }
         else if(InpSLMode == SL_ATR_BASED)
           {
            slPrice = bid + (InpSL_AtrMultiplier * currentAtr);
           }
         else
           {
            slPrice = bid + (InpSL_FixedPoints * _Point);
           }

         // Pastikan jarak SL memenuhi standar minimal dinamis
         double slDist = slPrice - bid;
         if(slDist < minSlDist)
           {
            slPrice = bid + minSlDist;
            slDist = minSlDist;
           }
         double slDistPoints = slDist / _Point;

         // Filter Batas Maksimal SL (Tolak jika terlalu lebar / overextended)
         if(InpMaxSLPoints > 0 && slDistPoints > InpMaxSLPoints)
           {
            Print(StringFormat("[SELL FILTERED] Stop Loss Terlalu Lebar (%.0f > %d pts). Setup Overextended.", slDistPoints, InpMaxSLPoints));
            return;
           }

         // Filter Rintangan Support/Resistance Mayor (Obstacle Blocking)
         string snrReasonSell = "";
         if(!isSellBreakoutTrigger && !isSellSmcTrigger && IsObstacleBlocking(false, bid, slDist, rates, copied, snrReasonSell))
           {
            Print("[SELL FILTERED] ", snrReasonSell);
            return;
           }

         // Hitung Take Profit berbasis Risk:Reward
         double tpPrice = bid - (slDist * InpRiskRewardRatio);

         // Hitung Lot Sizing
         double lot = CalculateLotSize(slDistPoints);
         if(InpUseConfluenceScoring && InpUseDynamicGradeSizing)
           {
            if(confGrade == "A")       lot = NormalizeDouble(lot * 0.75, 2);
            else if(confGrade == "B")  lot = NormalizeDouble(lot * 0.50, 2);
            lot = MathMax(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), lot);
           }

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         string patternStr = (bearPattern != PATTERN_NONE) ? GetPatternName(bearPattern) : 
                              (isSellBreakoutTrigger ? StringFormat("Breakout_L%d", InpBreakoutLookbackBars) : "SMC_Institutional");
         MqlDateTime barDt;
         TimeToStruct(rates[1].time, barDt);
         string sessionStr = GetMarketSessionName(barDt.hour);
         string orderPrefix = isSellBreakoutTrigger ? "TripleEMA_XAU_Breakout" : 
                              (isSellSmcTrigger ? "TripleEMA_XAU_SMC" : InpOrderComment);
         string comment = StringFormat("%s_%s_%s", orderPrefix, confGrade, patternStr);

         if(trade.Sell(lot, _Symbol, bid, slPrice, tpPrice, comment))
           {
            lastSellTradeTime = rates[1].time;
            ulong newTicket = trade.ResultOrder();
            if(newTicket == 0) newTicket = trade.ResultDeal();
            RegisterTrackedTrade(newTicket, 0, POSITION_TYPE_SELL, bid, slPrice, tpPrice, patternStr, sessionStr);
            Print(StringFormat("[ORDER SELL SUKSES (%s) | Grade %s (Skor %d) | %s] Lot: %.2f | Bid: %f | SL: %f | TP: %f | Sesi: %s",
                               isSellBreakoutTrigger ? "MOMENTUM BREAKOUT" : (isSellSmcTrigger ? "SMC INSTITUTIONAL" : "PULLBACK"),
                               confGrade, confScore, confDetails, lot, bid, slPrice, tpPrice, sessionStr));
           }
         else
           {
            Print("[ORDER SELL GAGAL] Error: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
           }
        }
     }

   // Tandai bar saat ini telah selesai dievaluasi agar tidak berulang setiap tick
   lastTradeBarTime = currentBarTime;
  }
//+------------------------------------------------------------------+
