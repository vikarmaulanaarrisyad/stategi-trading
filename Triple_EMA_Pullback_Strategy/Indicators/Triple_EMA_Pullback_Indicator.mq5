//+------------------------------------------------------------------+
//|                               Triple_EMA_Pullback_Indicator.mq5  |
//|                        Triple EMA Pullback Strategy Indicator    |
//|                                  Copyright 2026, XAUUSD Trader   |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.00"
#property description "Strategi 3 EMA (8, 21, 125) dengan 18 Pola Price Action Rejection, Filter False Signal & HUD Dashboard"
#property indicator_chart_window

#property indicator_buffers 7
#property indicator_plots   6

// Plot EMA 8
#property indicator_label1  "EMA 8"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrAqua
#property indicator_style1  STYLE_SOLID
#property indicator_width1  2

// Plot EMA 21
#property indicator_label2  "EMA 21"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrMagenta
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

// Plot EMA 125
#property indicator_label3  "EMA 125"
#property indicator_type3   DRAW_LINE
#property indicator_color3  clrWhite
#property indicator_style3  STYLE_SOLID
#property indicator_width3  3

// Plot Sinyal Buy
#property indicator_label4  "Signal BUY"
#property indicator_type4   DRAW_ARROW
#property indicator_color4  clrAqua
#property indicator_width4  3

// Plot Sinyal Sell
#property indicator_label5  "Signal SELL"
#property indicator_type5   DRAW_ARROW
#property indicator_color5  clrMagenta
#property indicator_width5  3

// Plot 6: Area Pullback Cloud (Value Zone EMA 8 vs 21)
#property indicator_label6  "Pullback Bullish Cloud;Pullback Bearish Cloud"
#property indicator_type6   DRAW_FILLING
#property indicator_color6  C'18,48,70', C'65,22,55'

// Include file pendukung
#include "..\Include\CandlePatterns.mqh"
#include "..\Include\MarketStructure.mqh"

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== Parameter Moving Average ==="
input int                  InpEMA8_Period          = 8;             // Periode EMA Cepat
input int                  InpEMA21_Period         = 21;            // Periode EMA Menengah (Support/Resistance)
input int                  InpEMA125_Period        = 125;           // Periode EMA Tren Utama (Baseline)
input ENUM_APPLIED_PRICE   InpEMA_Price            = PRICE_CLOSE;   // Applied Price

input group "=== Kustomisasi Warna & Ketebalan Garis EMA ==="
input color                InpColorEMA8            = clrAqua;       // Warna EMA 8 (Cyan Electric)
input int                  InpWidthEMA8            = 2;             // Ketebalan Garis EMA 8
input color                InpColorEMA21           = clrMagenta;    // Warna EMA 21 (Fuchsia / Magenta)
input int                  InpWidthEMA21           = 2;             // Ketebalan Garis EMA 21
input color                InpColorEMA125          = clrWhite;      // Warna EMA 125 (Putih Bersih Baseline)
input int                  InpWidthEMA125          = 3;             // Ketebalan Garis EMA 125 (Tebal)

input group "=== Filter False Signal & Anti-Spam ==="
input int                  InpSignalCooldownBars   = 5;             // Jeda Minimal Antar Sinyal (Bars Anti-Spam)
input bool                 InpRequireStrongClose   = true;          // Wajib Close Kuat Menembus EMA 8
input bool                 InpRequireEmaSlope      = true;          // Wajib Slope EMA 8 Searah Tren
input bool                 InpUseStructureFilter   = true;          // Wajib Struktur HH/HL (Buy) atau LH/LL (Sell)
input bool                 InpUseChopFilter        = true;          // Filter EMA 8 & 21 Sering Bolak-balik (Chop)
input int                  InpChopBars             = 15;            // Lookback Cek Chop EMA
input int                  InpMaxEmaCrosses        = 2;             // Maksimal Cross EMA dalam Lookback
input bool                 InpUseWhipsawFilter     = true;          // Filter Whipsaw EMA 125
input int                  InpWhipsawBars          = 20;            // Lookback Cek Whipsaw EMA 125
input int                  InpMaxWhipsawCrosses    = 2;             // Maksimal Tembus EMA 125 dalam Lookback
input bool                 InpUseOverextendFilter  = true;          // Filter Candle Terlalu Jauh dari EMA
input double               InpMaxAtrMultiplier     = 2.0;           // Toleransi Jarak Jauh (x ATR 14)
input int                  InpAtrPeriod            = 14;            // Periode ATR

input group "=== Filter Multi-Timeframe (HTF Trend Alignment) ==="
input bool                 InpUseMTFFilter         = true;          // Aktifkan Filter Multi-Timeframe (HTF)
input ENUM_TIMEFRAMES      InpHTFTimeframe         = PERIOD_H1;     // Timeframe Tren Utama (Default: H1)
input int                  InpHTF_EMA_Period       = 50;            // Periode EMA HTF (Macro Baseline)

input group "=== Tampilan Visual & Dashboard HUD ==="
input bool                 InpShowPullbackCloud    = true;             // Tampilkan Area Ribbon / Cloud EMA 8-21
input bool                 InpShowDashboard        = true;             // Tampilkan HUD Dashboard di Chart
input ENUM_BASE_CORNER     InpDashboardCorner      = CORNER_LEFT_LOWER;// Letak Sudut Dashboard (Default: Bawah Kiri)
input int                  InpDashboardX           = 20;               // Posisi X Dashboard (Pixel)
input int                  InpDashboardY           = 25;               // Posisi Y Dashboard (Pixel dari Bawah)

input group "=== Notifikasi & Alert ==="
input bool                 InpPopupAlert           = true;          // Alert Pop-up di MT5
input bool                 InpPushNotification     = true;          // Push Notification ke HP (MT5 Mobile)
input bool                 InpEmailNotification    = false;         // Kirim Notifikasi Email
input bool                 InpSoundAlert           = true;          // Bunyi Suara Alarm
input string               InpSoundFile            = "alert.wav";   // File Suara Alarm

//+------------------------------------------------------------------+
//| Buffer Indikator                                                 |
//+------------------------------------------------------------------+
double BufferEMA8[];
double BufferEMA21[];
double BufferEMA125[];
double BufferBuySignal[];
double BufferSellSignal[];
double BufferCloud1[];
double BufferCloud2[];

// Handle Indikator MQL5
int    handle_ema8;
int    handle_ema21;
int    handle_ema125;
int    handle_atr;
int    handle_htf_ema;

// Objek Detektor
CCandlePatternDetector patternDetector;
CMarketStructure       structureAnalyzer;

// Status Terakhir untuk Dashboard & Sinyal
datetime               lastAlertBarTime    = 0;
datetime               lastBuySignalTime   = 0;
datetime               lastSellSignalTime  = 0;
string                 lastDetectedPattern = "None";
string                 lastFilterStatus    = "Normal";
ENUM_MARKET_STRUCTURE  currentStructure   = STRUCTURE_UNKNOWN;
string                 currentTrendStatus  = "Neutral";
ENUM_TIMEFRAMES        effectiveHTF        = PERIOD_H1;
string                 currentHtfStatus    = "Neutral";
color                  currentHtfColor     = C'180,185,195';

// Prefix Nama Objek Chart
#define PREFIX_DASH "TEP_DASH_"

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
   // Inisialisasi Buffer Mapping
   SetIndexBuffer(0, BufferEMA8, INDICATOR_DATA);
   SetIndexBuffer(1, BufferEMA21, INDICATOR_DATA);
   SetIndexBuffer(2, BufferEMA125, INDICATOR_DATA);
   SetIndexBuffer(3, BufferBuySignal, INDICATOR_DATA);
   SetIndexBuffer(4, BufferSellSignal, INDICATOR_DATA);
   SetIndexBuffer(5, BufferCloud1, INDICATOR_DATA);
   SetIndexBuffer(6, BufferCloud2, INDICATOR_DATA);

   // Atur Kode Panah Wingdings
   PlotIndexSetInteger(3, PLOT_ARROW, 233); // Panah Naik (Buy)
   PlotIndexSetInteger(4, PLOT_ARROW, 234); // Panah Turun (Sell)

   PlotIndexSetDouble(3, PLOT_EMPTY_VALUE, 0.0);
   PlotIndexSetDouble(4, PLOT_EMPTY_VALUE, 0.0);
   PlotIndexSetDouble(5, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(6, PLOT_EMPTY_VALUE, EMPTY_VALUE);

   // Terapkan Warna & Ketebalan Garis Dinamis
   PlotIndexSetInteger(0, PLOT_LINE_COLOR, InpColorEMA8);
   PlotIndexSetInteger(0, PLOT_LINE_WIDTH, InpWidthEMA8);
   PlotIndexSetInteger(1, PLOT_LINE_COLOR, InpColorEMA21);
   PlotIndexSetInteger(1, PLOT_LINE_WIDTH, InpWidthEMA21);
   PlotIndexSetInteger(2, PLOT_LINE_COLOR, InpColorEMA125);
   PlotIndexSetInteger(2, PLOT_LINE_WIDTH, InpWidthEMA125);

   // Inisialisasi Handle MA dan ATR
   handle_ema8   = iMA(_Symbol, _Period, InpEMA8_Period, 0, MODE_EMA, InpEMA_Price);
   handle_ema21  = iMA(_Symbol, _Period, InpEMA21_Period, 0, MODE_EMA, InpEMA_Price);
   handle_ema125 = iMA(_Symbol, _Period, InpEMA125_Period, 0, MODE_EMA, InpEMA_Price);
   handle_atr    = iATR(_Symbol, _Period, InpAtrPeriod);

   // Tentukan Timeframe HTF yang adaptif jika chart dibuka di TF tinggi
   effectiveHTF = InpHTFTimeframe;
   if(effectiveHTF <= _Period)
     {
      if(_Period == PERIOD_M1) effectiveHTF = PERIOD_M15;
      else if(_Period == PERIOD_M5) effectiveHTF = PERIOD_H1;
      else if(_Period == PERIOD_M15) effectiveHTF = PERIOD_H1;
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

   if(handle_ema8 == INVALID_HANDLE || handle_ema21 == INVALID_HANDLE ||
      handle_ema125 == INVALID_HANDLE || handle_atr == INVALID_HANDLE)
     {
      Print("[Error] Gagal membuat handle indikator internal MQL5");
      return(INIT_FAILED);
     }

   // Konfigurasi modul struktur pasar
   structureAnalyzer.Configure(50, InpChopBars, InpMaxEmaCrosses, InpWhipsawBars, InpMaxWhipsawCrosses, InpMaxAtrMultiplier);

   // Nama Indikator
   IndicatorSetString(INDICATOR_SHORTNAME, "Triple EMA Pullback System (" + 
                      IntegerToString(InpEMA8_Period) + "," + 
                      IntegerToString(InpEMA21_Period) + "," + 
                      IntegerToString(InpEMA125_Period) + ")");
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   // Hapus handle indikator
   IndicatorRelease(handle_ema8);
   IndicatorRelease(handle_ema21);
   IndicatorRelease(handle_ema125);
   IndicatorRelease(handle_atr);
   if(handle_htf_ema != INVALID_HANDLE)
     {
      IndicatorRelease(handle_htf_ema);
      handle_htf_ema = INVALID_HANDLE;
     }

   // Bersihkan objek dashboard di chart
   ObjectsDeleteAll(0, PREFIX_DASH);
  }

//+------------------------------------------------------------------+
//| Format Singkat Timeframe (misal M5, H1, bukan PERIOD_M5)         |
//+------------------------------------------------------------------+
string GetTfShortName(ENUM_TIMEFRAMES tf)
  {
   switch(tf)
     {
      case PERIOD_M1:  return "M1";
      case PERIOD_M2:  return "M2";
      case PERIOD_M3:  return "M3";
      case PERIOD_M4:  return "M4";
      case PERIOD_M5:  return "M5";
      case PERIOD_M6:  return "M6";
      case PERIOD_M10: return "M10";
      case PERIOD_M12: return "M12";
      case PERIOD_M15: return "M15";
      case PERIOD_M20: return "M20";
      case PERIOD_M30: return "M30";
      case PERIOD_H1:  return "H1";
      case PERIOD_H2:  return "H2";
      case PERIOD_H3:  return "H3";
      case PERIOD_H4:  return "H4";
      case PERIOD_H6:  return "H6";
      case PERIOD_H8:  return "H8";
      case PERIOD_H12: return "H12";
      case PERIOD_D1:  return "D1";
      case PERIOD_W1:  return "W1";
      case PERIOD_MN1: return "MN";
      default:         return EnumToString(tf);
     }
  }

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
   if(rates_total < InpEMA125_Period + 35) return(0);

   // Salin buffer indikator dari handle ke buffer lokal
   int calculated_ema8   = CopyBuffer(handle_ema8, 0, 0, rates_total, BufferEMA8);
   int calculated_ema21  = CopyBuffer(handle_ema21, 0, 0, rates_total, BufferEMA21);
   int calculated_ema125 = CopyBuffer(handle_ema125, 0, 0, rates_total, BufferEMA125);

   if(calculated_ema8 <= 0 || calculated_ema21 <= 0 || calculated_ema125 <= 0)
     {
      return(0);
     }

   // Copy rates untuk kalkulasi pola candlestick & price action
   int copyCount = MathMin(rates_total, 1000);
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copiedRates = CopyRates(_Symbol, _Period, 0, copyCount, rates);
   if(copiedRates < 40) return(0);

   // Copy ATR
   double atrValues[];
   ArraySetAsSeries(atrValues, true);
   CopyBuffer(handle_atr, 0, 0, copyCount, atrValues);
   double currentAtr = (ArraySize(atrValues) > 1) ? atrValues[1] : 1.0 * _Point;

   // Salin array EMA terbalik (series) untuk memudahkan kalkulasi shift
   double ema8Series[];
   double ema21Series[];
   double ema125Series[];
   ArraySetAsSeries(ema8Series, true);
   ArraySetAsSeries(ema21Series, true);
   ArraySetAsSeries(ema125Series, true);
   CopyBuffer(handle_ema8, 0, 0, copyCount, ema8Series);
   CopyBuffer(handle_ema21, 0, 0, copyCount, ema21Series);
   CopyBuffer(handle_ema125, 0, 0, copyCount, ema125Series);

   // Mulai dari candle mana yang perlu dikalkulasi
   int start = (prev_calculated > 0) ? prev_calculated - 1 : InpEMA125_Period + 10;

   // Update buffer panah dan pullback cloud ribbon
   for(int i = start; i < rates_total; i++)
     {
      if(prev_calculated > 0)
        {
         BufferBuySignal[i]  = 0.0;
         BufferSellSignal[i] = 0.0;
        }
      if(InpShowPullbackCloud)
        {
         BufferCloud1[i] = BufferEMA8[i];
         BufferCloud2[i] = BufferEMA21[i];
        }
      else
        {
         BufferCloud1[i] = EMPTY_VALUE;
         BufferCloud2[i] = EMPTY_VALUE;
        }
     }

   // Kalkulasi sinyal panah pada bar historis agar terlihat saat scroll chart
   if(prev_calculated == 0)
     {
      for(int i = 0; i < rates_total; i++)
        {
         BufferBuySignal[i]  = 0.0;
         BufferSellSignal[i] = 0.0;
        }

      int maxHist = MathMin(copiedRates - 60, 800);
      int lastBuyBar  = 999999;
      int lastSellBar = 999999;

      for(int s = maxHist; s >= 2; s--)
        {
         int target_idx = rates_total - 1 - s;
         if(target_idx < 0 || target_idx >= rates_total) continue;

         double e8_s   = ema8Series[s];
         double e21_s  = ema21Series[s];
         double e125_s = ema125Series[s];
         double atr_s  = (s < ArraySize(atrValues)) ? atrValues[s] : currentAtr;

         // Cek Sinyal Buy Historis
         ENUM_CANDLE_PATTERN bPat = patternDetector.DetectBullishPattern(rates, s, e8_s, e21_s, e125_s);
         if(bPat != PATTERN_NONE && rates[s].close > e125_s && e8_s > e21_s && rates[s].low > e125_s)
           {
            bool strongClose = (!InpRequireStrongClose || (rates[s].close > e8_s && rates[s].close > rates[s].open));
            bool emaSlopeOk  = (!InpRequireEmaSlope || (e8_s > ema8Series[s + 1]));
            bool cooldownOk  = (lastBuyBar - s >= InpSignalCooldownBars);

            if(strongClose && emaSlopeOk && cooldownOk)
              {
               if(structureAnalyzer.ValidateBuyFilters(rates, copiedRates, ema8Series, ema21Series, ema125Series, atr_s, InpUseStructureFilter, s) == FILTER_PASS)
                 {
                  BufferBuySignal[target_idx] = rates[s].low - (atr_s * 0.4);
                  lastBuyBar = s;
                 }
              }
           }

         // Cek Sinyal Sell Historis
         ENUM_CANDLE_PATTERN sPat = patternDetector.DetectBearishPattern(rates, s, e8_s, e21_s, e125_s);
         if(sPat != PATTERN_NONE && rates[s].close < e125_s && e8_s < e21_s && rates[s].high < e125_s)
           {
            bool strongClose = (!InpRequireStrongClose || (rates[s].close < e8_s && rates[s].close < rates[s].open));
            bool emaSlopeOk  = (!InpRequireEmaSlope || (e8_s < ema8Series[s + 1]));
            bool cooldownOk  = (lastSellBar - s >= InpSignalCooldownBars);

            if(strongClose && emaSlopeOk && cooldownOk)
              {
               if(structureAnalyzer.ValidateSellFilters(rates, copiedRates, ema8Series, ema21Series, ema125Series, atr_s, InpUseStructureFilter, s) == FILTER_PASS)
                 {
                  BufferSellSignal[target_idx] = rates[s].high + (atr_s * 0.4);
                  lastSellBar = s;
                 }
              }
           }
        }
     }

   // Analisis Status untuk Bar 1 (Closed Candle yang baru selesai)
   // rates[1] adalah bar tertutup, rates[0] adalah bar berjalan
   double e8_1   = ema8Series[1];
   double e21_1  = ema21Series[1];
   double e125_1 = ema125Series[1];

   // Tentukan status tren utama
   if(rates[1].close > e125_1 && e8_1 > e21_1)
      currentTrendStatus = "BULLISH (Uptrend)";
   else if(rates[1].close < e125_1 && e8_1 < e21_1)
      currentTrendStatus = "BEARISH (Downtrend)";
   else
      currentTrendStatus = "SIDEWAYS / TRANSITION";

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

      if(cEma < 2 || cRates < 2)
        {
         cRates = CopyRates(_Symbol, effectiveHTF, 0, 20, htfRatesBuf);
         cEma   = CopyBuffer(handle_htf_ema, 0, 0, 20, htfEmaBuf);
        }

      if(cEma >= 2 && cRates >= 2)
        {
         // Membaca HTF bar 1 (closed bar) untuk validasi non-repainting
         if(htfRatesBuf[1].close > htfEmaBuf[1])
           {
            htfBullish = true;
            htfBearish = false;
            currentHtfStatus = StringFormat("BULLISH (Above EMA %d)", InpHTF_EMA_Period);
            currentHtfColor  = clrLime;
           }
         else if(htfRatesBuf[1].close < htfEmaBuf[1])
           {
            htfBullish = false;
            htfBearish = true;
            currentHtfStatus = StringFormat("BEARISH (Below EMA %d)", InpHTF_EMA_Period);
            currentHtfColor  = clrTomato;
           }
        }
      else
        {
         currentHtfStatus = StringFormat("Syncing %s Data...", GetTfShortName(effectiveHTF));
         currentHtfColor  = clrGold;
        }
     }
   else
     {
      currentHtfStatus = "Disabled (Single TF)";
      currentHtfColor  = C'140,150,165';
     }

   // Analisis Struktur Pasar pada bar 1
   currentStructure = structureAnalyzer.AnalyzeStructure(rates, copiedRates, 1);

   // Deteksi Pola Candlestick Bullish pada bar 1
   ENUM_CANDLE_PATTERN bullPattern = patternDetector.DetectBullishPattern(rates, 1, e8_1, e21_1, e125_1);
   // Deteksi Pola Candlestick Bearish pada bar 1
   ENUM_CANDLE_PATTERN bearPattern = patternDetector.DetectBearishPattern(rates, 1, e8_1, e21_1, e125_1);

   // Index bar 1 dalam buffer non-series
   int bar1_idx = rates_total - 2;

   bool strongCloseBuy  = (!InpRequireStrongClose || (rates[1].close > e8_1 && rates[1].close > rates[1].open));
   bool strongCloseSell = (!InpRequireStrongClose || (rates[1].close < e8_1 && rates[1].close < rates[1].open));
   bool slopeBuyOk      = (!InpRequireEmaSlope || (e8_1 > ema8Series[2]));
   bool slopeSellOk     = (!InpRequireEmaSlope || (e8_1 < ema8Series[2]));
   bool cooldownBuyOk   = (lastBuySignalTime == 0 || (rates[1].time - lastBuySignalTime >= PeriodSeconds() * InpSignalCooldownBars));
   bool cooldownSellOk  = (lastSellSignalTime == 0 || (rates[1].time - lastSellSignalTime >= PeriodSeconds() * InpSignalCooldownBars));

   // VALIDASI SETUP BUY
   if(bullPattern != PATTERN_NONE)
     {
      lastDetectedPattern = GetPatternName(bullPattern);

      // Syarat 1: Harga > EMA 125 dan EMA 8 > EMA 21
      bool trendValid = (rates[1].close > e125_1 && e8_1 > e21_1 && rates[1].low > e125_1);

      if(!trendValid)
        {
         lastFilterStatus = "FILTERED: Trend/EMA Misalignment";
        }
      else if(InpUseMTFFilter && !htfBullish)
        {
         lastFilterStatus = StringFormat("FILTERED: HTF (%s) Bearish", GetTfShortName(effectiveHTF));
        }
      else if(!strongCloseBuy)
        {
         lastFilterStatus = "FILTERED: Weak Close (Must close above EMA 8)";
        }
      else if(!slopeBuyOk)
        {
         lastFilterStatus = "FILTERED: EMA 8 Slope Down";
        }
      else if(!cooldownBuyOk)
        {
         lastFilterStatus = "FILTERED: Signal Cooldown Active";
        }
      else
        {
         // Validasi Filter False Signal & Struktur
         ENUM_FILTER_RESULT filterRes = structureAnalyzer.ValidateBuyFilters(
            rates, copiedRates, ema8Series, ema21Series, ema125Series, currentAtr, InpUseStructureFilter, 1
         );

         if(filterRes == FILTER_PASS)
           {
            lastFilterStatus = "VALID SIGNAL PASS";
            BufferBuySignal[bar1_idx] = rates[1].low - (currentAtr * 0.4);

             // Kirim notifikasi jika bar baru belum pernah di-alert (hanya saat live market)
             if(rates[1].time != lastAlertBarTime)
               {
                lastAlertBarTime  = rates[1].time;
                lastBuySignalTime = rates[1].time;
                if(prev_calculated > 0)
                  {
                   SendSignalNotification("BUY", lastDetectedPattern, rates[1].close);
                  }
               }
           }
         else
           {
            lastFilterStatus = "FILTERED: " + FilterResultToString(filterRes);
           }
        }
     }
   // VALIDASI SETUP SELL
   else if(bearPattern != PATTERN_NONE)
     {
      lastDetectedPattern = GetPatternName(bearPattern);

      // Syarat 1: Harga < EMA 125 dan EMA 8 < EMA 21
      bool trendValid = (rates[1].close < e125_1 && e8_1 < e21_1 && rates[1].high < e125_1);

      if(!trendValid)
        {
         lastFilterStatus = "FILTERED: Trend/EMA Misalignment";
        }
      else if(InpUseMTFFilter && !htfBearish)
        {
         lastFilterStatus = StringFormat("FILTERED: HTF (%s) Bullish", EnumToString(effectiveHTF));
        }
      else if(!strongCloseSell)
        {
         lastFilterStatus = "FILTERED: Weak Close (Must close below EMA 8)";
        }
      else if(!slopeSellOk)
        {
         lastFilterStatus = "FILTERED: EMA 8 Slope Up";
        }
      else if(!cooldownSellOk)
        {
         lastFilterStatus = "FILTERED: Signal Cooldown Active";
        }
      else
        {
         // Validasi Filter False Signal & Struktur
         ENUM_FILTER_RESULT filterRes = structureAnalyzer.ValidateSellFilters(
            rates, copiedRates, ema8Series, ema21Series, ema125Series, currentAtr, InpUseStructureFilter, 1
         );

         if(filterRes == FILTER_PASS)
           {
            lastFilterStatus = "VALID SIGNAL PASS";
            BufferSellSignal[bar1_idx] = rates[1].high + (currentAtr * 0.4);

             // Kirim notifikasi jika bar baru belum pernah di-alert (hanya saat live market)
             if(rates[1].time != lastAlertBarTime)
               {
                lastAlertBarTime   = rates[1].time;
                lastSellSignalTime = rates[1].time;
                if(prev_calculated > 0)
                  {
                   SendSignalNotification("SELL", lastDetectedPattern, rates[1].close);
                  }
               }
           }
         else
           {
            lastFilterStatus = "FILTERED: " + FilterResultToString(filterRes);
           }
        }
     }
   else
     {
      // Tidak ada pola baru pada bar saat ini
      if(lastFilterStatus == "VALID SIGNAL PASS")
        {
         lastFilterStatus = "Monitoring Next Pullback";
        }
     }

   // Update HUD Dashboard jika diaktifkan
   if(InpShowDashboard)
     {
      DrawDashboard(rates, ema8Series, ema21Series, ema125Series);
     }

   return(rates_total);
  }


//+------------------------------------------------------------------+
//| Fungsi Mengirim Notifikasi Lengkap (Pop-up, Push, Sound, Email)  |
//+------------------------------------------------------------------+
void SendSignalNotification(string signalType, string pattern, double price)
  {
   string msg = StringFormat("[TRIPLE EMA %s] %s %s @ %s | Pattern: %s | Structure: %s",
                             signalType, _Symbol, EnumToString(_Period),
                             DoubleToString(price, _Digits), pattern,
                             GetMarketStructureName(currentStructure));

   Print(msg);

   if(InpPopupAlert)
     {
      Alert(msg);
     }

   if(InpPushNotification)
     {
      SendNotification(msg);
     }

   if(InpEmailNotification)
     {
      SendMail("MT5 Signal: " + signalType + " " + _Symbol, msg);
     }

   if(InpSoundAlert && InpSoundFile != "")
     {
      PlaySound(InpSoundFile);
     }
  }

//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| Helper Menggambar Objek Teks Dashboard                           |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, color clr, int fontSize = 9, bool isBold = false, ENUM_BASE_CORNER corner = CORNER_LEFT_LOWER)
  {
   string objName = PREFIX_DASH + name;
   if(ObjectFind(0, objName) < 0)
     {
      ObjectCreate(0, objName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, objName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, objName, OBJPROP_HIDDEN, true);
     }
   ObjectSetInteger(0, objName, OBJPROP_BACK, false);
   ObjectSetInteger(0, objName, OBJPROP_CORNER, corner);
   ObjectSetInteger(0, objName, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, objName, OBJPROP_YDISTANCE, y);
   ObjectSetString(0, objName, OBJPROP_TEXT, text);
   ObjectSetInteger(0, objName, OBJPROP_COLOR, clr);
   ObjectSetString(0, objName, OBJPROP_FONT, isBold ? "Segoe UI Bold" : "Segoe UI");
   ObjectSetInteger(0, objName, OBJPROP_FONTSIZE, fontSize);
  }

//+------------------------------------------------------------------+
//| Helper Menggambar Background Panel Dashboard                     |
//+------------------------------------------------------------------+
void CreatePanel(string name, int x, int y, int width, int height, color bgClr, color borderClr, ENUM_BASE_CORNER corner = CORNER_LEFT_LOWER)
  {
   string objName = PREFIX_DASH + name;
   if(ObjectFind(0, objName) < 0)
     {
      ObjectCreate(0, objName, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, objName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, objName, OBJPROP_HIDDEN, true);
     }
   ObjectSetInteger(0, objName, OBJPROP_BACK, false);
   ObjectSetInteger(0, objName, OBJPROP_CORNER, corner);
   ObjectSetInteger(0, objName, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, objName, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, objName, OBJPROP_XSIZE, width);
   ObjectSetInteger(0, objName, OBJPROP_YSIZE, height);
   ObjectSetInteger(0, objName, OBJPROP_BGCOLOR, bgClr);
   ObjectSetInteger(0, objName, OBJPROP_BORDER_COLOR, borderClr);
   ObjectSetInteger(0, objName, OBJPROP_COLOR, borderClr);
   ObjectSetInteger(0, objName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
  }

//+------------------------------------------------------------------+
//| Menggambar HUD Dashboard Elegan & Rapi pada Chart (Posisi Bawah) |
//+------------------------------------------------------------------+
void DrawDashboard(const MqlRates &rates[], const double &ema8Series[], const double &ema21Series[], const double &ema125Series[])
  {
   int x = InpDashboardX;
   int y = InpDashboardY;
   int width = 430;  // Lebar proporsional agar tidak ada teks yang terpotong
   int height = 230;
   ENUM_BASE_CORNER corner = InpDashboardCorner;

   bool isLower = (corner == CORNER_LEFT_LOWER || corner == CORNER_RIGHT_LOWER);

   int y_bg     = y;
   int y_header = isLower ? (y + height - 28) : y;
   int y_title  = isLower ? (y + height - 21) : (y + 6);
   int y_sub    = isLower ? (y + height - 20) : (y + 7);
   int y_row1   = isLower ? (y + height - 48) : (y + 34);
   int stepY    = isLower ? -21 : 21;
   int y_div    = isLower ? (y + 26) : (y + 196);
   int y_foot   = isLower ? (y + 8)  : (y + 202);

   // 1. Background Panel Elegan (Dark Glassmorphism Shield)
   CreatePanel("BG", x, y_bg, width, height, C'20,26,38', C'52,66,92', corner);
   CreatePanel("HEADER", x, y_header, width, 28, C'30,38,54', C'65,82,112', corner);

   // 2. Header: Judul & Simbol/Timeframe/Spread
   long liveSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   CreateLabel("TITLE", x + 14, y_title, "TRIPLE EMA PULLBACK", clrGold, 9, true, corner);
   string symTfText = StringFormat("[%s | %s | Spr:%d]", _Symbol, GetTfShortName(_Period), liveSpread);
   CreateLabel("SUBTITLE", x + 215, y_sub, symTfText, (liveSpread <= 45) ? clrDeepSkyBlue : clrTomato, 8, false, corner);

   // Data Realtime Bar 0 & Konfirmasi
   double curPrice = rates[0].close;
   double e8_0     = ema8Series[0];
   double e21_0    = ema21Series[0];
   double e125_0   = ema125Series[0];

   // 3. Konten Baris Dashboard (X Label = x+14, X Nilai = x+150 agar tidak tumpang tindih)
   int lineY = y_row1;
   int x_val = x + 150;

   // Baris 1: Trend Baseline (EMA 125)
   color trendColor = (curPrice > e125_0) ? clrLimeGreen : clrTomato;
   string trendVal  = (curPrice > e125_0) ? "BULLISH (Above 125)" : "BEARISH (Below 125)";
   CreateLabel("L_TREND", x + 14, lineY, "Trend (EMA 125):", C'180,185,195', 9, false, corner);
   CreateLabel("V_TREND", x_val, lineY, trendVal, trendColor, 9, true, corner);

   // Baris 2: HTF Macro Trend (H1 / Higher TF)
   lineY += stepY;
   string htfLabel = StringFormat("HTF Trend (%s):", GetTfShortName(effectiveHTF));
   CreateLabel("L_HTF", x + 14, lineY, htfLabel, C'180,185,195', 9, false, corner);
   CreateLabel("V_HTF", x_val, lineY, currentHtfStatus, currentHtfColor, 8, true, corner);

   // Baris 3: EMA Alignment (EMA 8 vs 21)
   lineY += stepY;
   color alignColor = (e8_0 > e21_0) ? InpColorEMA8 : InpColorEMA21;
   string alignText = (e8_0 > e21_0) ? "EMA 8 > 21 (Bullish)" : "EMA 8 < 21 (Bearish)";
   CreateLabel("L_ALIGN", x + 14, lineY, "EMA 8/21 Align:", C'180,185,195', 9, false, corner);
   CreateLabel("V_ALIGN", x_val, lineY, alignText, alignColor, 9, true, corner);

   // Baris 4: Struktur Pasar (HH-HL / LH-LL)
   lineY += stepY;
   color structColor = C'190,195,205';
   string structText = "Sideways / Range";
   if(currentStructure == STRUCTURE_BULLISH_HH_HL) { structColor = clrLime; structText = "HH - HL (Uptrend)"; }
   else if(currentStructure == STRUCTURE_BEARISH_LH_LL) { structColor = clrSalmon; structText = "LH - LL (Downtrend)"; }
   CreateLabel("L_STRUCT", x + 14, lineY, "Market Structure:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STRUCT", x_val, lineY, structText, structColor, 9, true, corner);

   // Baris 5: Real-time Live Candle (Bar 0 Sedang Bergerak)
   lineY += stepY;
   bool inPullbackZone = (rates[0].low <= MathMax(e8_0, e21_0) && rates[0].high >= MathMin(e8_0, e21_0));
   string bar0Status = "Floating Movement";
   color  bar0Color  = C'170,180,195';

   if(inPullbackZone)
     {
      if(curPrice > e125_0 && e8_0 > e21_0)
        {
         bar0Status = "PULLBACK ACTIVE (In Buy Zone)";
         bar0Color  = clrAqua;
        }
      else if(curPrice < e125_0 && e8_0 < e21_0)
        {
         bar0Status = "PULLBACK ACTIVE (In Sell Zone)";
         bar0Color  = clrMagenta;
        }
      else
        {
         bar0Status = "TESTING EMA 8-21 CLOUD";
         bar0Color  = clrGold;
        }
     }
   else
     {
      if(curPrice > e125_0 && e8_0 > e21_0)
        {
         bar0Status = "Riding Trend (Above EMA 8)";
         bar0Color  = clrLimeGreen;
        }
      else if(curPrice < e125_0 && e8_0 < e21_0)
        {
         bar0Status = "Riding Trend (Below EMA 8)";
         bar0Color  = clrTomato;
        }
     }
   CreateLabel("L_BAR0", x + 14, lineY, "Live Bar 0:", C'180,185,195', 9, false, corner);
   CreateLabel("V_BAR0", x_val, lineY, bar0Status, bar0Color, 8, true, corner);

   // Baris 6: Pola Candlestick Terdeteksi pada Bar 1
   lineY += stepY;
   CreateLabel("L_PATTERN", x + 14, lineY, "Pattern (Bar 1):", C'180,185,195', 9, false, corner);
   CreateLabel("V_PATTERN", x_val, lineY, lastDetectedPattern, clrYellow, 8, true, corner);

   // Baris 7: Status Filter Sinyal
   lineY += stepY;
   color filterColor = (StringFind(lastFilterStatus, "FILTERED") >= 0) ? clrOrangeRed :
                       ((lastFilterStatus == "VALID SIGNAL PASS") ? clrLime : clrWhiteSmoke);
   CreateLabel("L_FILTER", x + 14, lineY, "Filter Status:", C'180,185,195', 9, false, corner);
   CreateLabel("V_FILTER", x_val, lineY, lastFilterStatus, filterColor, 8, true, corner);

   // 4. Garis Pembatas Halus & Footer Info (Sesi Pasar Aktif)
   CreatePanel("DIVIDER", x + 12, y_div, width - 24, 1, C'42,54,75', C'42,54,75', corner);

   MqlDateTime dt;
   TimeCurrent(dt);
   string sessionName = "Asian Session";
   if(dt.hour >= 8 && dt.hour < 13) sessionName = "London Session (Active)";
   else if(dt.hour >= 13 && dt.hour < 17) sessionName = "London-NY Overlap (Peak)";
   else if(dt.hour >= 17 && dt.hour < 22) sessionName = "New York Session (Active)";
   else sessionName = "Asian / Rollover (Quiet)";

   string footerText = StringFormat("● Sesi: %s", sessionName);
   CreateLabel("FOOTER", x + 14, y_foot, footerText, C'145,160,185', 8, false, corner);
  }
//+------------------------------------------------------------------+
