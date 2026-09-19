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

input group "=== Sistem 3 Layar / Triple Screen (H1 -> M15 -> M5) ==="
input bool                 InpUseTripleScreen      = true;          // Aktifkan Sistem 3 Layar (H1 Macro -> M15 Structure -> M5 Trigger)
input ENUM_TIMEFRAMES      InpScreen1_TF           = PERIOD_H1;     // Layar 1: Timeframe Tren Besar Institusi (Macro Bias H1)
input int                  InpScreen1_EMA          = 50;            // Layar 1: Periode EMA Tren Besar Macro
input ENUM_TIMEFRAMES      InpScreen2_TF           = PERIOD_M15;    // Layar 2: Timeframe Struktur Pasar & Ayunan M15
input int                  InpScreen2_EMA          = 50;            // Layar 2: Periode EMA Level Kunci M15
input bool                 InpScreen2_RequireStruct = true;         // Layar 2: Wajib Konfirmasi Struktur Ayunan (Tolak Counter-Trend M15)
input bool                 InpScreen2_RequireKeyLevel = true;       // Layar 2: Wajib Konfirmasi Level Kunci EMA M15
input bool                 InpUseMTFFilter         = true;          // Filter HTF Tambahan (Legacy MTF Compatibility)
input ENUM_TIMEFRAMES      InpHTFTimeframe         = PERIOD_H1;     // Timeframe Tren Utama (Default: H1)
input int                  InpHTF_EMA_Period       = 50;            // Periode EMA HTF (Macro Baseline)

input group "=== Filter Volume Transaksi Lilin (Smart Money Volume) ==="
input bool                 InpUseVolumeFilter      = true;          // Wajib Volume Lilin Setup Valid (Diatas Rata-rata)
input int                  InpVolumeLookback       = 20;            // Lookback Rata-rata Volume (SMA 20)
input double               InpVolumeMultiplier     = 1.0;           // Minimal Volume Setup (x Rata-rata Volume)

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

input group "=== Sistem Skor Probabilitas & Konfluensi (Confluence Scoring) ==="
input bool                 InpUseConfluenceScoring = true;          // Aktifkan Sistem Skor Konfluensi (Anti Lagging Entry)
input int                  InpMinConfluenceScore   = 60;            // Minimal Skor untuk Alert (60=Grade A, 80=Grade A+, 40=Grade B)
input int                  InpScoreWeightFibo      = 20;            // Bobot Skor: Fibonacci Golden Zone (50%-78.6%)
input int                  InpScoreWeightRSI       = 20;            // Bobot Skor: RSI Momentum Sehat (45-70 Buy / 30-55 Sell)
input int                  InpScoreWeightFVG       = 20;            // Bobot Skor: Mitigasi Fair Value Gap (FVG)
input int                  InpScoreWeightADX       = 20;            // Bobot Skor: ADX Trend Strength (>= 20)
input int                  InpScoreWeightStructure = 20;            // Bobot Skor: Struktur Ayunan HH-HL / LH-LL

//+------------------------------------------------------------------+
//| Enum Mode Tampilan Dashboard                                     |
//+------------------------------------------------------------------+
enum ENUM_DASHBOARD_MODE
  {
   DASH_MODE_MINI_PRO = 0,  // Mini HUD Glassmorphic (Ramping 78px - Rekomendasi)
   DASH_MODE_FULL     = 1,  // Detail Penuh (11 Baris Telemetri Lengkap)
   DASH_MODE_OFF      = 2   // Nonaktif (100% Layar Bersih Bebas Objek)
  };

input group "=== Tampilan Garis Resistance & Support (S/R) ==="
input bool                 InpShowSnrLines         = true;          // Tampilkan Garis Resistance & Support di Chart
input int                  InpSnrLookbackBars      = 50;            // Lookback Bar Pencarian S/R (Default: 50)
input color                InpColorResistance      = C'235,87,87';  // Warna Garis Resistance (Soft Crimson)
input color                InpColorSupport         = C'39,174,96';  // Warna Garis Support (Soft Emerald)
input ENUM_LINE_STYLE      InpSnrLineStyle         = STYLE_DOT;     // Gaya Garis S/R (Titik Halus Elegan)
input int                  InpSnrLineWidth         = 1;             // Ketebalan Garis S/R

input group "=== Tampilan Garis Entry Sinyal ==="
input bool                 InpShowEntryLine        = true;          // Tampilkan Garis Level Entry
input color                InpColorEntryBuy        = C'41,121,255'; // Warna Garis Entry BUY (Electric Blue)
input color                InpColorEntrySell       = C'255,61,120'; // Warna Garis Entry SELL (Neon Rose)
input ENUM_LINE_STYLE      InpEntryLineStyle       = STYLE_DASHDOT; // Gaya Garis Entry
input int                  InpEntryLineWidth       = 1;             // Ketebalan Garis Entry

input group "=== Countdown Timer Penutupan Candle ==="
input bool                 InpShowCandleCountdown  = true;          // Tampilkan Hitung Mundur Waktu Candle
input color                InpColorCountdown       = C'255,215,0';  // Warna Teks Countdown (Gold)
input int                  InpCountdownFontSize    = 9;             // Ukuran Font Countdown
input ENUM_BASE_CORNER     InpCountdownCorner      = CORNER_RIGHT_UPPER; // Posisi Sudut Countdown di Chart
input int                  InpCountdownX           = 25;            // Jarak X dari Tepi (Pixel)
input int                  InpCountdownY           = 25;            // Jarak Y dari Tepi (Pixel)

input group "=== Tampilan Visual & Dashboard HUD ==="
input ENUM_DASHBOARD_MODE  InpDashboardMode        = DASH_MODE_MINI_PRO; // Mode Dashboard HUD (Mini PRO / Full / Off)
input bool                 InpShowPullbackCloud    = true;             // Tampilkan Area Ribbon / Cloud EMA 8-21
input ENUM_BASE_CORNER     InpDashboardCorner      = CORNER_LEFT_LOWER;// Letak Sudut Dashboard (Default: Bawah Kiri)
input int                  InpDashboardX           = 20;               // Posisi X Dashboard (Pixel)
input int                  InpDashboardY           = 25;               // Posisi Y Dashboard (Pixel dari Bawah)

input group "=== Kebersihan & Tema Visual Profesional ==="
input bool                 InpApplyProTheme        = true;             // Terapkan Tema Dark Obsidian TradingView Otomatis
input bool                 InpCleanStrayHlines     = true;             // Bersihkan Garis Liar/Sisa Lama yang Menumpuk

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
int    handle_screen1_ema;
int    handle_screen2_ema;
int    handle_rsi;
int    handle_adx;

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
string                 currentScreen1Status = "Neutral";
color                  currentScreen1Color  = C'180,185,195';
string                 currentScreen2Status = "Neutral";
color                  currentScreen2Color  = C'180,185,195';
string                 currentSetupGrade   = "-";
int                    currentSetupScore   = 0;
string                 currentSetupDetails = "";

// Prefix Nama Objek Chart
#define PREFIX_DASH  "TEP_DASH_"
#define PREFIX_LINES "TEP_LINE_"

// Status S/R, Entry & Countdown Global
double                 g_nearestRes        = 0.0;
double                 g_nearestSup        = 0.0;
string                 lastSignalType      = "None";
double                 lastEntryPrice      = 0.0;
string                 lastCountdownStr    = "00:00";

//+------------------------------------------------------------------+
//| Bersihkan Garis Liar / Sisa Lama yang Menumpuk di Chart          |
//+------------------------------------------------------------------+
void CleanStrayChartObjects()
  {
   if(!InpCleanStrayHlines) return;
   int total = ObjectsTotal(0, 0, OBJ_HLINE);
   for(int i = total - 1; i >= 0; i--)
     {
      string name = ObjectName(0, i, 0, OBJ_HLINE);
      if(StringFind(name, PREFIX_LINES) < 0)
        {
         ObjectDelete(0, name);
        }
     }
  }

//+------------------------------------------------------------------+
//| Terapkan Tema Dark Obsidian TradingView Otomatis                 |
//+------------------------------------------------------------------+
void ApplyTradingViewProTheme()
  {
   if(!InpApplyProTheme) return;

   // 1. Tata Letak & Spasi Chart
   ChartSetInteger(0, CHART_SHOW_GRID, false);             // Hilangkan kisi/grid kotak yang bikin pusing
   ChartSetInteger(0, CHART_SHIFT, true);                  // Beri ruang geser candle ke kiri
   ChartSetDouble(0, CHART_SHIFT_SIZE, 14.0);              // 14% ruang nafas di sebelah kanan
   ChartSetInteger(0, CHART_SHOW_ONE_CLICK, false);        // Sembunyikan panel One-Click Trading di kiri atas
   ChartSetInteger(0, CHART_SHOW_PERIOD_SEP, false);       // Hilangkan garis pemisah periode vertikal

   // 2. Skema Warna Dark Obsidian Elegan (TradingView Modern)
   ChartSetInteger(0, CHART_COLOR_BACKGROUND, C'13,17,23');      // Latar belakang Obsidian gelap adem
   ChartSetInteger(0, CHART_COLOR_FOREGROUND, C'165,180,200');   // Angka harga & sumbu waktu abu lembut
   ChartSetInteger(0, CHART_COLOR_GRID, C'24,30,42');           // Grid redup jika sewaktu-waktu dinyalakan

   // 3. Warna Candlestick (Emerald Green & Crimson Ruby)
   ChartSetInteger(0, CHART_COLOR_CHART_UP, C'8,153,129');       // Garis batas Candle Naik
   ChartSetInteger(0, CHART_COLOR_CHART_DOWN, C'242,54,69');     // Garis batas Candle Turun
   ChartSetInteger(0, CHART_COLOR_CANDLE_BULL, C'8,153,129');    // Isi Candle Naik (Emerald)
   ChartSetInteger(0, CHART_COLOR_CANDLE_BEAR, C'242,54,69');    // Isi Candle Turun (Ruby)
   ChartSetInteger(0, CHART_COLOR_CHART_LINE, C'180,195,215');   // Garis chart
   ChartSetInteger(0, CHART_COLOR_BID, C'120,135,155');          // Garis Bid
   ChartSetInteger(0, CHART_COLOR_ASK, C'242,54,69');           // Garis Ask
   ChartSetInteger(0, CHART_COLOR_LAST, C'8,153,129');

   ChartSetInteger(0, CHART_MODE, CHART_CANDLES);                // Format Candlestick Jepang
   ChartRedraw(0);
  }

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
   handle_rsi    = iRSI(_Symbol, _Period, 14, PRICE_CLOSE);
   handle_adx    = iADX(_Symbol, _Period, 14);

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

   // Inisialisasi Handle Sistem 3 Layar (Triple Screen)
   if(InpUseTripleScreen)
     {
      handle_screen1_ema = iMA(_Symbol, InpScreen1_TF, InpScreen1_EMA, 0, MODE_EMA, PRICE_CLOSE);
      handle_screen2_ema = iMA(_Symbol, InpScreen2_TF, InpScreen2_EMA, 0, MODE_EMA, PRICE_CLOSE);
      if(handle_screen1_ema == INVALID_HANDLE || handle_screen2_ema == INVALID_HANDLE)
        {
         Print("[Indicator Warning] Gagal menginisialisasi handle Triple Screen (H1/M15).");
        }
     }
   else
     {
      handle_screen1_ema = INVALID_HANDLE;
      handle_screen2_ema = INVALID_HANDLE;
     }

   if(handle_ema8 == INVALID_HANDLE || handle_ema21 == INVALID_HANDLE ||
      handle_ema125 == INVALID_HANDLE || handle_atr == INVALID_HANDLE)
     {
      Print("[Error] Gagal membuat handle indikator internal MQL5");
      return(INIT_FAILED);
     }

   // Konfigurasi modul struktur pasar
   structureAnalyzer.Configure(50, InpChopBars, InpMaxEmaCrosses, InpWhipsawBars, InpMaxWhipsawCrosses, InpMaxAtrMultiplier);

   // Bersihkan garis-garis lama / stray horizontal lines
   CleanStrayChartObjects();

   // Terapkan tema Dark Obsidian TradingView otomatis
   ApplyTradingViewProTheme();

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
   if(handle_rsi != INVALID_HANDLE)
     {
      IndicatorRelease(handle_rsi);
      handle_rsi = INVALID_HANDLE;
     }
   if(handle_adx != INVALID_HANDLE)
     {
      IndicatorRelease(handle_adx);
      handle_adx = INVALID_HANDLE;
     }

   // Bersihkan objek dashboard dan garis di chart
   ObjectsDeleteAll(0, PREFIX_DASH);
   ObjectsDeleteAll(0, PREFIX_LINES);
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
      outReason = StringFormat("Syncing %s Data...", GetTfShortName(InpScreen1_TF));
      return false;
     }

   if(isBuy)
     {
      if(h1Rates[1].close < h1Ema[1])
        {
         outReason = StringFormat("Layar 1 (%s) Macro Bearish (Close %.2f < EMA%d %.2f)",
                                  GetTfShortName(InpScreen1_TF), h1Rates[1].close, InpScreen1_EMA, h1Ema[1]);
         return false;
        }
     }
   else
     {
      if(h1Rates[1].close > h1Ema[1])
        {
         outReason = StringFormat("Layar 1 (%s) Macro Bullish (Close %.2f > EMA%d %.2f)",
                                  GetTfShortName(InpScreen1_TF), h1Rates[1].close, InpScreen1_EMA, h1Ema[1]);
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
      outReason = StringFormat("Syncing %s Data...", GetTfShortName(InpScreen2_TF));
      return false;
     }

   // 1. Cek Struktur Ayunan M15 (HH-HL vs LH-LL)
   if(InpScreen2_RequireStruct)
     {
      ENUM_MARKET_STRUCTURE m15_struct = structureAnalyzer.AnalyzeStructure(m15Rates, cRates, 1);
      if(isBuy && m15_struct == STRUCTURE_BEARISH_LH_LL)
        {
         outReason = StringFormat("Layar 2 (%s) Struktur Bearish (LH-LL). Dilarang BUY melawan ayunan M15.", GetTfShortName(InpScreen2_TF));
         return false;
        }
      if(!isBuy && m15_struct == STRUCTURE_BULLISH_HH_HL)
        {
         outReason = StringFormat("Layar 2 (%s) Struktur Bullish (HH-HL). Dilarang SELL melawan ayunan M15.", GetTfShortName(InpScreen2_TF));
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
                                     GetTfShortName(InpScreen2_TF), InpScreen2_EMA, m15Rates[1].close, m15Ema[1]);
            return false;
           }
         if(!isBuy && m15Rates[1].close > m15Ema[1])
           {
            outReason = StringFormat("Layar 2 (%s) di atas Level Kunci EMA %d (%.2f > %.2f)",
                                     GetTfShortName(InpScreen2_TF), InpScreen2_EMA, m15Rates[1].close, m15Ema[1]);
            return false;
           }
        }
     }

   return true;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Pullback Berada di Fibonacci Golden Zone untuk BUY    |
//+------------------------------------------------------------------+
bool IsFiboGoldenZoneBuy(const MqlRates &rates[], int totalRates, int shift = 1)
  {
   int start = shift + 1;
   int end = MathMin(shift + 30, totalRates - 1);
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

   double fibo50 = swingHigh - (0.50 * range);
   double fiboDeep = swingHigh - (0.786 * range);

   return (rates[shift].low <= fibo50 && rates[shift].high >= fiboDeep);
  }

//+------------------------------------------------------------------+
//| Cek Apakah Pullback Berada di Fibonacci Golden Zone untuk SELL   |
//+------------------------------------------------------------------+
bool IsFiboGoldenZoneSell(const MqlRates &rates[], int totalRates, int shift = 1)
  {
   int start = shift + 1;
   int end = MathMin(shift + 30, totalRates - 1);
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

   double fibo50 = swingLow + (0.50 * range);
   double fiboDeep = swingLow + (0.786 * range);

   return (rates[shift].high >= fibo50 && rates[shift].low <= fiboDeep);
  }

//+------------------------------------------------------------------+
//| Cek Keberadaan Fair Value Gap (FVG) Aktif yang Termitigasi      |
//+------------------------------------------------------------------+
bool HasActiveFVG(const MqlRates &rates[], int totalRates, bool isBuy, int shift = 1)
  {
   int end = MathMin(shift + 10, totalRates - 2);

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
//| Hitung Skor Konfluensi & Grade Kualitas Setup BUY (Indikator)    |
//+------------------------------------------------------------------+
int CalculateBuyConfluenceScore(const MqlRates &rates[], int totalRates, const double &rsiBuf[],
                                const double &adxBuf[], double currentRsi,
                                const double &e8Series[], const double &e21Series[], const double &e125Series[],
                                double currentAtr, string &outDetails, string &outGrade)
  {
   int score = 0;
   outDetails = "";

   // 1. Fibonacci Golden Zone (50% - 78.6%)
   if(IsFiboGoldenZoneBuy(rates, totalRates, 1))
     {
      score += InpScoreWeightFibo;
      outDetails += "Fibo+";
     }

   // 2. RSI Momentum Sehat (45 - 70)
   if(currentRsi >= 45.0 && currentRsi <= 70.0)
     {
      score += InpScoreWeightRSI;
      outDetails += "RSI+";
     }

   // 3. Fair Value Gap (FVG Mitigation)
   if(HasActiveFVG(rates, totalRates, true, 1))
     {
      score += InpScoreWeightFVG;
      outDetails += "FVG+";
     }

   // 4. ADX Trend Strength (>= 20)
   if(ArraySize(adxBuf) >= 2 && adxBuf[1] >= 20.0)
     {
      score += InpScoreWeightADX;
      outDetails += "ADX+";
     }

   // 5. Market Structure & False Signal Filter (HH-HL)
   if(structureAnalyzer.ValidateBuyFilters(rates, totalRates, e8Series, e21Series, e125Series, currentAtr, InpUseStructureFilter, 1) == FILTER_PASS)
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
//| Hitung Skor Konfluensi & Grade Kualitas Setup SELL (Indikator)   |
//+------------------------------------------------------------------+
int CalculateSellConfluenceScore(const MqlRates &rates[], int totalRates, const double &rsiBuf[],
                                 const double &adxBuf[], double currentRsi,
                                 const double &e8Series[], const double &e21Series[], const double &e125Series[],
                                 double currentAtr, string &outDetails, string &outGrade)
  {
   int score = 0;
   outDetails = "";

   // 1. Fibonacci Golden Zone (50% - 78.6%)
   if(IsFiboGoldenZoneSell(rates, totalRates, 1))
     {
      score += InpScoreWeightFibo;
      outDetails += "Fibo+";
     }

   // 2. RSI Momentum Sehat (30 - 55)
   if(currentRsi >= 30.0 && currentRsi <= 55.0)
     {
      score += InpScoreWeightRSI;
      outDetails += "RSI+";
     }

   // 3. Fair Value Gap (FVG Mitigation)
   if(HasActiveFVG(rates, totalRates, false, 1))
     {
      score += InpScoreWeightFVG;
      outDetails += "FVG+";
     }

   // 4. ADX Trend Strength (>= 20)
   if(ArraySize(adxBuf) >= 2 && adxBuf[1] >= 20.0)
     {
      score += InpScoreWeightADX;
      outDetails += "ADX+";
     }

   // 5. Market Structure & False Signal Filter (LH-LL)
   if(structureAnalyzer.ValidateSellFilters(rates, totalRates, e8Series, e21Series, e125Series, currentAtr, InpUseStructureFilter, 1) == FILTER_PASS)
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

   if(adxVal >= 20.0)
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

   if(adxVal >= 20.0)
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

         // Cek Sinyal Buy Historis (Pullback -> Breakout -> SMC)
         ENUM_CANDLE_PATTERN bPat = patternDetector.DetectBullishPattern(rates, s, e8_s, e21_s, e125_s);
         double hBreakLvl = 0.0, hSmcLvl = 0.0;
         string hSmcInfo = "";
         bool hBullBreak = (bPat == PATTERN_NONE) && DetectBullishBreakout(rates, copiedRates, s, InpBreakoutLookbackBars, InpBreakoutMinBodyRatio, hBreakLvl);
         bool hBullSmc   = (bPat == PATTERN_NONE && !hBullBreak) && DetectSmcBullishSetup(rates, copiedRates, s, hSmcLvl, hSmcInfo);

         bool hHasBuy = (bPat != PATTERN_NONE) || hBullBreak || hBullSmc;
         if(hHasBuy)
           {
            bool hTrendBuy = (hBullBreak || hBullSmc) ?
               (rates[s].close > e125_s && e8_s > e21_s && rates[s].close > e8_s) :
               (rates[s].close > e125_s && e8_s > e21_s && rates[s].low > e125_s);

            bool strongClose = (!InpRequireStrongClose || (rates[s].close > e8_s && rates[s].close > rates[s].open));
            bool emaSlopeOk  = (!InpRequireEmaSlope || (e8_s > ema8Series[s + 1]));
            bool cooldownOk  = (lastBuyBar - s >= InpSignalCooldownBars);

            if(hTrendBuy && strongClose && emaSlopeOk && cooldownOk)
              {
               if(hBullBreak || hBullSmc || structureAnalyzer.ValidateBuyFilters(rates, copiedRates, ema8Series, ema21Series, ema125Series, atr_s, InpUseStructureFilter, s) == FILTER_PASS)
                 {
                  BufferBuySignal[target_idx] = rates[s].low - (atr_s * 0.4);
                  lastBuyBar = s;
                 }
              }
           }

         // Cek Sinyal Sell Historis (Pullback -> Breakout -> SMC)
         ENUM_CANDLE_PATTERN sPat = patternDetector.DetectBearishPattern(rates, s, e8_s, e21_s, e125_s);
         double hBearBreakLvl = 0.0, hSmcBearLvl = 0.0;
         string hSmcBearInfo = "";
         bool hBearBreak = (sPat == PATTERN_NONE) && DetectBearishBreakout(rates, copiedRates, s, InpBreakoutLookbackBars, InpBreakoutMinBodyRatio, hBearBreakLvl);
         bool hBearSmc   = (sPat == PATTERN_NONE && !hBearBreak) && DetectSmcBearishSetup(rates, copiedRates, s, hSmcBearLvl, hSmcBearInfo);

         bool hHasSell = (sPat != PATTERN_NONE) || hBearBreak || hBearSmc;
         if(hHasSell)
           {
            bool hTrendSell = (hBearBreak || hBearSmc) ?
               (rates[s].close < e125_s && e8_s < e21_s && rates[s].close < e8_s) :
               (rates[s].close < e125_s && e8_s < e21_s && rates[s].high < e125_s);

            bool strongClose = (!InpRequireStrongClose || (rates[s].close < e8_s && rates[s].close < rates[s].open));
            bool emaSlopeOk  = (!InpRequireEmaSlope || (e8_s < ema8Series[s + 1]));
            bool cooldownOk  = (lastSellBar - s >= InpSignalCooldownBars);

            if(hTrendSell && strongClose && emaSlopeOk && cooldownOk)
              {
               if(hBearBreak || hBearSmc || structureAnalyzer.ValidateSellFilters(rates, copiedRates, ema8Series, ema21Series, ema125Series, atr_s, InpUseStructureFilter, s) == FILTER_PASS)
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

   // Update Status Real-Time Sistem 3 Layar (Triple Screen)
   if(InpUseTripleScreen)
     {
      // 1. Layar 1: H1 Macro Bias
      if(handle_screen1_ema != INVALID_HANDLE)
        {
         MqlRates s1Rates[];
         double s1Ema[];
         ArraySetAsSeries(s1Rates, true);
         ArraySetAsSeries(s1Ema, true);
         if(CopyRates(_Symbol, InpScreen1_TF, 0, 5, s1Rates) >= 2 && CopyBuffer(handle_screen1_ema, 0, 0, 5, s1Ema) >= 2)
           {
            if(s1Rates[1].close > s1Ema[1])
              {
               currentScreen1Status = StringFormat("BULLISH (Close > EMA%d)", InpScreen1_EMA);
               currentScreen1Color  = clrLime;
              }
            else if(s1Rates[1].close < s1Ema[1])
              {
               currentScreen1Status = StringFormat("BEARISH (Close < EMA%d)", InpScreen1_EMA);
               currentScreen1Color  = clrTomato;
              }
           }
         else
           {
            currentScreen1Status = StringFormat("Syncing %s...", GetTfShortName(InpScreen1_TF));
            currentScreen1Color  = clrGold;
           }
        }

      // 2. Layar 2: M15 Market Structure
      MqlRates s2Rates[];
      ArraySetAsSeries(s2Rates, true);
      int cM15 = CopyRates(_Symbol, InpScreen2_TF, 0, 55, s2Rates);
      if(cM15 >= 30)
        {
         ENUM_MARKET_STRUCTURE m15_struct = structureAnalyzer.AnalyzeStructure(s2Rates, cM15, 1);
         if(m15_struct == STRUCTURE_BULLISH_HH_HL)
           {
            currentScreen2Status = "BULLISH (HH-HL Ayunan Naik)";
            currentScreen2Color  = clrLime;
           }
         else if(m15_struct == STRUCTURE_BEARISH_LH_LL)
           {
            currentScreen2Status = "BEARISH (LH-LL Ayunan Turun)";
            currentScreen2Color  = clrTomato;
           }
         else
           {
            currentScreen2Status = "TRANSITION / SIDEWAYS";
            currentScreen2Color  = clrGold;
           }
        }
      else
        {
         currentScreen2Status = StringFormat("Syncing %s...", GetTfShortName(InpScreen2_TF));
         currentScreen2Color  = clrGold;
        }
     }

   // Deteksi Pola Candlestick Bullish pada bar 1 (Pullback Rejection)
   ENUM_CANDLE_PATTERN bullPattern = patternDetector.DetectBullishPattern(rates, 1, e8_1, e21_1, e125_1);
   ENUM_CANDLE_PATTERN bearPattern = patternDetector.DetectBearishPattern(rates, 1, e8_1, e21_1, e125_1);

   // Deteksi Strategi Tambahan: Momentum Breakout (Penembusan Range Lookback)
   double bullBreakLevel = 0.0;
   double bearBreakLevel = 0.0;
   bool isBullBreakout = DetectBullishBreakout(rates, copiedRates, 1, InpBreakoutLookbackBars, InpBreakoutMinBodyRatio, bullBreakLevel);
   bool isBearBreakout = DetectBearishBreakout(rates, copiedRates, 1, InpBreakoutLookbackBars, InpBreakoutMinBodyRatio, bearBreakLevel);

   // Index bar 1 dalam buffer non-series
   int bar1_idx = rates_total - 2;

   bool strongCloseBuy  = (!InpRequireStrongClose || (rates[1].close > e8_1 && rates[1].close > rates[1].open));
   bool strongCloseSell = (!InpRequireStrongClose || (rates[1].close < e8_1 && rates[1].close < rates[1].open));
   bool slopeBuyOk      = (!InpRequireEmaSlope || (e8_1 > ema8Series[2]));
   bool slopeSellOk     = (!InpRequireEmaSlope || (e8_1 < ema8Series[2]));
   bool cooldownBuyOk   = (lastBuySignalTime == 0 || (rates[1].time - lastBuySignalTime >= PeriodSeconds() * InpSignalCooldownBars));
   bool cooldownSellOk  = (lastSellSignalTime == 0 || (rates[1].time - lastSellSignalTime >= PeriodSeconds() * InpSignalCooldownBars));

   // Evaluasi Volume Candle Konfirmasi Bar 1
   long vol_bar1 = (rates[1].real_volume > 0) ? rates[1].real_volume : rates[1].tick_volume;
   double sumVol = 0;
   int volLookback = MathMin(InpVolumeLookback, copiedRates - 2);
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
   bool isSmcBull = (bullPattern == PATTERN_NONE && !isBullBreakout) && DetectSmcBullishSetup(rates, copiedRates, 1, smcBullLevel, smcBullInfo);
   bool isSmcBear = (bearPattern == PATTERN_NONE && !isBearBreakout) && DetectSmcBearishSetup(rates, copiedRates, 1, smcBearLevel, smcBearInfo);

   bool hasBuySignal  = (bullPattern != PATTERN_NONE) || isBullBreakout || isSmcBull;
   bool hasSellSignal = (bearPattern != PATTERN_NONE) || isBearBreakout || isSmcBear;
   bool isBuyBreakoutTrigger  = (bullPattern == PATTERN_NONE && isBullBreakout);
   bool isSellBreakoutTrigger = (bearPattern == PATTERN_NONE && isBearBreakout);
   bool isBuySmcTrigger       = (bullPattern == PATTERN_NONE && !isBullBreakout && isSmcBull);
   bool isSellSmcTrigger      = (bearPattern == PATTERN_NONE && !isBearBreakout && isSmcBear);

   // VALIDASI SETUP BUY (PULLBACK, BREAKOUT & SMC)
   if(hasBuySignal)
     {
      lastDetectedPattern = (bullPattern != PATTERN_NONE) ? GetPatternName(bullPattern) : 
                            (isBuyBreakoutTrigger ? StringFormat("Breakout (H%d)", InpBreakoutLookbackBars) : smcBullInfo);

      // Syarat 1: Harga > EMA 125 dan EMA 8 > EMA 21
      bool trendValid = (isBuyBreakoutTrigger || isBuySmcTrigger) ? 
         (rates[1].close > e125_1 && e8_1 > e21_1 && rates[1].close > e8_1) :
         (rates[1].close > e125_1 && e8_1 > e21_1 && rates[1].low > e125_1);

      string s1Reason = "", s2Reason = "";
      if(!trendValid)
        {
         lastFilterStatus = "FILTERED: Trend/EMA Misalignment";
        }
      else if(InpUseTripleScreen && !EvaluateScreen1MacroBias(true, s1Reason))
        {
         lastFilterStatus = "FILTERED: " + s1Reason;
        }
      else if(InpUseTripleScreen && !isBuyBreakoutTrigger && !isBuySmcTrigger && !EvaluateScreen2MarketStructure(true, s2Reason))
        {
         lastFilterStatus = "FILTERED: " + s2Reason;
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
      else if(!volumeOk)
        {
         lastFilterStatus = StringFormat("FILTERED: Low Volume (%d < %.0f Avg)", vol_bar1, avgVol * InpVolumeMultiplier);
        }
      else
        {
         // Salin RSI & ADX untuk evaluasi konfluensi
         double rsiBuf[], adxBuf[];
         ArraySetAsSeries(rsiBuf, true);
         ArraySetAsSeries(adxBuf, true);
         CopyBuffer(handle_rsi, 0, 0, 5, rsiBuf);
         CopyBuffer(handle_adx, 0, 0, 5, adxBuf);
         double curRsi = (ArraySize(rsiBuf) > 1) ? rsiBuf[1] : 50.0;
         double curAdx = (ArraySize(adxBuf) > 1) ? adxBuf[1] : 20.0;

         string confDetails = "", confGrade = "A";
         int confScore = 100;

         if(isBuyBreakoutTrigger)
           {
            confScore = CalculateBreakoutConfluenceScore(true, curRsi, curAdx, volRatio, confDetails, confGrade);
           }
         else if(isBuySmcTrigger)
           {
            confScore = CalculateSmcConfluenceScore(true, curRsi, curAdx, volRatio, smcBullInfo, confDetails, confGrade);
           }
         else
           {
            confScore = CalculateBuyConfluenceScore(rates, copiedRates, rsiBuf, adxBuf, curRsi, ema8Series, ema21Series, ema125Series, currentAtr, confDetails, confGrade);
           }

         currentSetupGrade = confGrade;
         currentSetupScore = confScore;
         currentSetupDetails = confDetails;

         if(!isBuyBreakoutTrigger && !isBuySmcTrigger && InpUseConfluenceScoring && confScore < InpMinConfluenceScore)
           {
            lastFilterStatus = StringFormat("FILTERED: Skor Konfluensi Rendah (%d/100, Grade %s < Min %d) [%s]",
                                            confScore, confGrade, InpMinConfluenceScore, confDetails);
           }
         else
           {
            string engineName = isBuyBreakoutTrigger ? "BREAKOUT" : (isBuySmcTrigger ? "SMC" : "PULLBACK");
            lastFilterStatus = StringFormat("VALID PASS (%s) | Grade %s (%d/100) [%s]", 
                                            engineName, confGrade, confScore, confDetails);
            BufferBuySignal[bar1_idx] = rates[1].low - (currentAtr * 0.4);
            lastSignalType = isBuyBreakoutTrigger ? "BREAKOUT BUY" : (isBuySmcTrigger ? "SMC BUY" : "BUY");
            lastEntryPrice = rates[1].close;

            // Kirim notifikasi jika bar baru belum pernah di-alert (hanya saat live market)
            if(rates[1].time != lastAlertBarTime)
              {
               lastAlertBarTime  = rates[1].time;
               lastBuySignalTime = rates[1].time;
               if(prev_calculated > 0)
                 {
                  double refLow = isBuySmcTrigger ? MathMin(smcBullLevel, rates[1].low) : rates[1].low;
                  double buySl = NormalizeDouble(refLow - (currentAtr * 0.3), _Digits);
                  double buyTp = NormalizeDouble(rates[1].close + (rates[1].close - buySl) * 2.0, _Digits);
                  SendSignalNotification(lastSignalType, lastDetectedPattern, rates[1].close, buySl, buyTp, vol_bar1, volRatio, confGrade, confScore, confDetails);
                 }
              }
           }
        }
     }
   // VALIDASI SETUP SELL (PULLBACK, BREAKOUT & SMC)
   else if(hasSellSignal)
     {
      lastDetectedPattern = (bearPattern != PATTERN_NONE) ? GetPatternName(bearPattern) : 
                            (isSellBreakoutTrigger ? StringFormat("Breakout (L%d)", InpBreakoutLookbackBars) : smcBearInfo);

      // Syarat 1: Harga < EMA 125 dan EMA 8 < EMA 21
      bool trendValid = (isSellBreakoutTrigger || isSellSmcTrigger) ?
         (rates[1].close < e125_1 && e8_1 < e21_1 && rates[1].close < e8_1) :
         (rates[1].close < e125_1 && e8_1 < e21_1 && rates[1].high < e125_1);

      string s1Reason = "", s2Reason = "";
      if(!trendValid)
        {
         lastFilterStatus = "FILTERED: Trend/EMA Misalignment";
        }
      else if(InpUseTripleScreen && !EvaluateScreen1MacroBias(false, s1Reason))
        {
         lastFilterStatus = "FILTERED: " + s1Reason;
        }
      else if(InpUseTripleScreen && !isSellBreakoutTrigger && !isSellSmcTrigger && !EvaluateScreen2MarketStructure(false, s2Reason))
        {
         lastFilterStatus = "FILTERED: " + s2Reason;
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
      else if(!volumeOk)
        {
         lastFilterStatus = StringFormat("FILTERED: Low Volume (%d < %.0f Avg)", vol_bar1, avgVol * InpVolumeMultiplier);
        }
      else
        {
         // Salin RSI & ADX untuk evaluasi konfluensi
         double rsiBuf[], adxBuf[];
         ArraySetAsSeries(rsiBuf, true);
         ArraySetAsSeries(adxBuf, true);
         CopyBuffer(handle_rsi, 0, 0, 5, rsiBuf);
         CopyBuffer(handle_adx, 0, 0, 5, adxBuf);
         double curRsi = (ArraySize(rsiBuf) > 1) ? rsiBuf[1] : 50.0;
         double curAdx = (ArraySize(adxBuf) > 1) ? adxBuf[1] : 20.0;

         string confDetails = "", confGrade = "A";
         int confScore = 100;

         if(isSellBreakoutTrigger)
           {
            confScore = CalculateBreakoutConfluenceScore(false, curRsi, curAdx, volRatio, confDetails, confGrade);
           }
         else if(isSellSmcTrigger)
           {
            confScore = CalculateSmcConfluenceScore(false, curRsi, curAdx, volRatio, smcBearInfo, confDetails, confGrade);
           }
         else
           {
            confScore = CalculateSellConfluenceScore(rates, copiedRates, rsiBuf, adxBuf, curRsi, ema8Series, ema21Series, ema125Series, currentAtr, confDetails, confGrade);
           }

         currentSetupGrade = confGrade;
         currentSetupScore = confScore;
         currentSetupDetails = confDetails;

         if(!isSellBreakoutTrigger && !isSellSmcTrigger && InpUseConfluenceScoring && confScore < InpMinConfluenceScore)
           {
            lastFilterStatus = StringFormat("FILTERED: Skor Konfluensi Rendah (%d/100, Grade %s < Min %d) [%s]",
                                            confScore, confGrade, InpMinConfluenceScore, confDetails);
           }
         else
           {
            string engineName = isSellBreakoutTrigger ? "BREAKOUT" : (isSellSmcTrigger ? "SMC" : "PULLBACK");
            lastFilterStatus = StringFormat("VALID PASS (%s) | Grade %s (%d/100) [%s]",
                                            engineName, confGrade, confScore, confDetails);
            BufferSellSignal[bar1_idx] = rates[1].high + (currentAtr * 0.4);
            lastSignalType = isSellBreakoutTrigger ? "BREAKOUT SELL" : (isSellSmcTrigger ? "SMC SELL" : "SELL");
            lastEntryPrice = rates[1].close;

            // Kirim notifikasi jika bar baru belum pernah di-alert (hanya saat live market)
            if(rates[1].time != lastAlertBarTime)
              {
               lastAlertBarTime   = rates[1].time;
               lastSellSignalTime = rates[1].time;
               if(prev_calculated > 0)
                 {
                  double refHigh = isSellSmcTrigger ? MathMax(smcBearLevel, rates[1].high) : rates[1].high;
                  double sellSl = NormalizeDouble(refHigh + (currentAtr * 0.3), _Digits);
                  double sellTp = NormalizeDouble(rates[1].close - (sellSl - rates[1].close) * 2.0, _Digits);
                  SendSignalNotification(lastSignalType, lastDetectedPattern, rates[1].close, sellSl, sellTp, vol_bar1, volRatio, confGrade, confScore, confDetails);
                 }
              }
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

   // 1. Gambar Garis Resistance, Support & Entry Level di chart
   DrawSnrAndEntry(rates, copiedRates, ema8Series[0], ema21Series[0], ema125Series[0]);

   // 2. Gambar Countdown Penutupan Candle
   DrawCandleCountdown(rates);

   // 3. Update HUD Dashboard sesuai mode yang dipilih
   static ENUM_DASHBOARD_MODE prevDashMode = (ENUM_DASHBOARD_MODE)-1;
   if(InpDashboardMode != prevDashMode)
     {
      ObjectsDeleteAll(0, PREFIX_DASH);
      prevDashMode = InpDashboardMode;
     }

   if(InpDashboardMode == DASH_MODE_MINI_PRO)
     {
      DrawMiniDashboard(rates, ema8Series, ema21Series, ema125Series);
     }
   else if(InpDashboardMode == DASH_MODE_FULL)
     {
      DrawDashboard(rates, ema8Series, ema21Series, ema125Series);
     }
   else
     {
      ObjectsDeleteAll(0, PREFIX_DASH);
     }

   return(rates_total);
  }


//+------------------------------------------------------------------+
//| Fungsi Mengirim Notifikasi Lengkap (Pop-up, Push, Sound, Email)  |
//+------------------------------------------------------------------+
void SendSignalNotification(string signalType, string pattern, double price, double sl = 0.0, double tp = 0.0,
                            long vol = 0, double volRatio = 0.0, string grade = "A", int score = 0, string details = "")
  {
   string slTpStr = "";
   if(sl > 0.0 && tp > 0.0)
     {
      slTpStr = StringFormat(" | SL: %s | TP: %s (1:2 R:R)", DoubleToString(sl, _Digits), DoubleToString(tp, _Digits));
     }

   string volStr = "";
   if(vol > 0 && volRatio > 0.0)
     {
      volStr = StringFormat(" | Vol: %s (%.1fx Avg)", IntegerToString(vol), volRatio);
     }

   string confStr = "";
   if(score > 0)
     {
      confStr = StringFormat(" | Grade %s (%d/100: %s)", grade, score, details);
     }

   string msg = StringFormat("🔔 [%s GRADE %s | Skor %d] %s %s @ %s%s%s%s | Pattern: %s",
                             signalType, grade, score, _Symbol, GetTfShortName(_Period),
                             DoubleToString(price, _Digits), slTpStr, volStr, confStr, pattern);

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
//| Hitung Level Resistance & Support Mayor Dinamis                  |
//+------------------------------------------------------------------+
void CalculateDynamicSNR(const MqlRates &rates[], int totalRates, int lookback, double &nearestRes, double &nearestSup)
  {
   nearestRes = 0.0;
   nearestSup = 0.0;
   if(totalRates < 15) return;

   int count = MathMin(lookback, totalRates - 2);
   double curPrice = rates[0].close;

   double minResAbove = DBL_MAX;
   double maxSupBelow = 0.0;
   double absoluteMax = rates[1].high;
   double absoluteMin = rates[1].low;

   for(int i = 1; i <= count; i++)
     {
      if(rates[i].high > absoluteMax) absoluteMax = rates[i].high;
      if(rates[i].low < absoluteMin)  absoluteMin = rates[i].low;

      // Cek apakah swing high fractal (lebih tinggi dari bar sebelum dan sesudah)
      if(i >= 2 && i <= count - 1)
        {
         if(rates[i].high >= rates[i-1].high && rates[i].high >= rates[i+1].high)
           {
            if(rates[i].high > curPrice && rates[i].high < minResAbove)
              {
               minResAbove = rates[i].high;
              }
           }
         if(rates[i].low <= rates[i-1].low && rates[i].low <= rates[i+1].low)
           {
            if(rates[i].low < curPrice && rates[i].low > maxSupBelow)
              {
               maxSupBelow = rates[i].low;
              }
           }
        }
     }

   nearestRes = (minResAbove != DBL_MAX) ? minResAbove : absoluteMax;
   nearestSup = (maxSupBelow > 0.0) ? maxSupBelow : absoluteMin;

   nearestRes = NormalizeDouble(nearestRes, _Digits);
   nearestSup = NormalizeDouble(nearestSup, _Digits);
  }

//+------------------------------------------------------------------+
//| Helper Menggambar Garis Horizontal                               |
//+------------------------------------------------------------------+
void DrawHLine(string name, double price, color clr, ENUM_LINE_STYLE style, int width, string desc)
  {
   string objName = PREFIX_LINES + name;
   if(ObjectFind(0, objName) < 0)
     {
      ObjectCreate(0, objName, OBJ_HLINE, 0, 0, price);
      ObjectSetInteger(0, objName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, objName, OBJPROP_HIDDEN, true);
     }
   ObjectMove(0, objName, 0, 0, price);
   ObjectSetInteger(0, objName, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, objName, OBJPROP_STYLE, style);
   ObjectSetInteger(0, objName, OBJPROP_WIDTH, width);
   ObjectSetString(0, objName, OBJPROP_TOOLTIP, desc);
   ObjectSetInteger(0, objName, OBJPROP_BACK, true);
  }

//+------------------------------------------------------------------+
//| Gambar Garis S/R, Entry Level & Label di Chart                   |
//+------------------------------------------------------------------+
void DrawSnrAndEntry(const MqlRates &rates[], int copiedRates, double e8_0, double e21_0, double e125_0)
  {
   CalculateDynamicSNR(rates, copiedRates, InpSnrLookbackBars, g_nearestRes, g_nearestSup);

   // 1. Garis Resistance & Support
   if(InpShowSnrLines)
     {
      if(g_nearestRes > 0.0)
        {
         string resDesc = StringFormat("RESISTANCE: %.2f", g_nearestRes);
         DrawHLine("RES", g_nearestRes, InpColorResistance, InpSnrLineStyle, InpSnrLineWidth, resDesc);
        }
      if(g_nearestSup > 0.0)
        {
         string supDesc = StringFormat("SUPPORT: %.2f", g_nearestSup);
         DrawHLine("SUP", g_nearestSup, InpColorSupport, InpSnrLineStyle, InpSnrLineWidth, supDesc);
        }
     }
   else
     {
      ObjectDelete(0, PREFIX_LINES + "RES");
      ObjectDelete(0, PREFIX_LINES + "SUP");
     }

   // 2. Garis Entry Level
   if(InpShowEntryLine)
     {
      double entryPrice = lastEntryPrice;
      color entryClr = (lastSignalType == "SELL") ? InpColorEntrySell : InpColorEntryBuy;
      string entryDesc = "";

      if(entryPrice > 0.0 && lastSignalType != "None")
        {
         entryDesc = StringFormat("ENTRY %s: %.2f", lastSignalType, entryPrice);
        }
      else
        {
         // Jika belum ada sinyal terkonfirmasi, tampilkan proyeksi zona Value Zone
         entryPrice = NormalizeDouble((e8_0 + e21_0) / 2.0, _Digits);
         if(rates[0].close > e125_0)
           {
            entryClr = InpColorEntryBuy;
            entryDesc = StringFormat("PROJECTION BUY ENTRY (Value Zone): %.2f", entryPrice);
           }
         else
           {
            entryClr = InpColorEntrySell;
            entryDesc = StringFormat("PROJECTION SELL ENTRY (Value Zone): %.2f", entryPrice);
           }
        }

      if(entryPrice > 0.0)
        {
         DrawHLine("ENTRY", entryPrice, entryClr, InpEntryLineStyle, InpEntryLineWidth, entryDesc);
        }
     }
   else
     {
      ObjectDelete(0, PREFIX_LINES + "ENTRY");
     }
  }

//+------------------------------------------------------------------+
//| Gambar Badge Countdown Waktu Penutupan Candle                    |
//+------------------------------------------------------------------+
void DrawCandleCountdown(const MqlRates &rates[])
  {
   if(!InpShowCandleCountdown)
     {
      ObjectDelete(0, PREFIX_LINES + "COUNTDOWN_BG");
      ObjectDelete(0, PREFIX_LINES + "COUNTDOWN_TXT");
      return;
     }

   datetime barOpenTime = rates[0].time;
   int tfSec = PeriodSeconds(_Period);
   datetime barCloseTime = barOpenTime + tfSec;
   datetime curTime = TimeCurrent();

   int secLeft = (int)(barCloseTime - curTime);
   if(secLeft < 0) secLeft = 0;

   int mm = secLeft / 60;
   int ss = secLeft % 60;

   lastCountdownStr = StringFormat("%02d:%02d", mm, ss);
   string countdownText = StringFormat("⏱ Candle (%s): %s", GetTfShortName(_Period), lastCountdownStr);

   int x = InpCountdownX;
   int y = InpCountdownY;
   ENUM_BASE_CORNER corner = InpCountdownCorner;

   // Warna badge berkedip merah saat mendekati close (misal sisa <= 15 detik)
   color textColor = (secLeft <= 15) ? clrRed : InpColorCountdown;
   color borderColor = (secLeft <= 15) ? clrCrimson : C'52,66,92';

   // Panel Badge
   string bgName = PREFIX_LINES + "COUNTDOWN_BG";
   if(ObjectFind(0, bgName) < 0)
     {
      ObjectCreate(0, bgName, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, bgName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, bgName, OBJPROP_HIDDEN, true);
     }
   ObjectSetInteger(0, bgName, OBJPROP_CORNER, corner);
   ObjectSetInteger(0, bgName, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, bgName, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, bgName, OBJPROP_XSIZE, 155);
   ObjectSetInteger(0, bgName, OBJPROP_YSIZE, 24);
   ObjectSetInteger(0, bgName, OBJPROP_BGCOLOR, C'15,20,30');
   ObjectSetInteger(0, bgName, OBJPROP_BORDER_COLOR, borderColor);
   ObjectSetInteger(0, bgName, OBJPROP_COLOR, borderColor);
   ObjectSetInteger(0, bgName, OBJPROP_BORDER_TYPE, BORDER_FLAT);

   // Teks Badge
   string txtName = PREFIX_LINES + "COUNTDOWN_TXT";
   if(ObjectFind(0, txtName) < 0)
     {
      ObjectCreate(0, txtName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, txtName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, txtName, OBJPROP_HIDDEN, true);
     }
   ObjectSetInteger(0, txtName, OBJPROP_CORNER, corner);
   ObjectSetInteger(0, txtName, OBJPROP_XDISTANCE, x + 10);
   ObjectSetInteger(0, txtName, OBJPROP_YDISTANCE, y + 4);
   ObjectSetString(0, txtName, OBJPROP_TEXT, countdownText);
   ObjectSetInteger(0, txtName, OBJPROP_COLOR, textColor);
   ObjectSetString(0, txtName, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, txtName, OBJPROP_FONTSIZE, InpCountdownFontSize);
  }

//+------------------------------------------------------------------+
//| Menggambar Mini HUD Dashboard Glassmorphic (Ramping & Elegan)    |
//+------------------------------------------------------------------+
void DrawMiniDashboard(const MqlRates &rates[], const double &ema8Series[], const double &ema21Series[], const double &ema125Series[])
  {
   int x = InpDashboardX;
   int y = InpDashboardY;
   int width = 345;
   int height = 78;
   ENUM_BASE_CORNER corner = InpDashboardCorner;
   bool isLower = (corner == CORNER_LEFT_LOWER || corner == CORNER_RIGHT_LOWER);

   int y_bg     = y;
   int y_header = isLower ? (y + height - 22) : y;
   int y_title  = isLower ? (y + height - 17) : (y + 4);
   int y_sub    = isLower ? (y + height - 17) : (y + 4);
   int y_timer  = isLower ? (y + height - 17) : (y + 4);
   int y_row1   = isLower ? (y + 35) : (y + 27);
   int y_row2   = isLower ? (y + 13) : (y + 51);

   // 1. Glass Card Background
   CreatePanel("MINI_BG", x, y_bg, width, height, C'16,22,34', C'48,60,85', corner);
   CreatePanel("MINI_HEADER", x, y_header, width, 22, C'25,34,50', C'58,72,100', corner);

   // 2. Header: Judul + Simbol + Timeframe + Spread + Countdown
   long liveSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   string symTfText = StringFormat("%s (%s) | Sprd: %d", _Symbol, StringSubstr(EnumToString((ENUM_TIMEFRAMES)_Period), 7), liveSpread);
   CreateLabel("MINI_TITLE", x + 10, y_title, "⚡ TEP PRO", clrGold, 8, true, corner);
   string gradeText = (currentSetupScore > 0) ? StringFormat(" | Grade: %s (%d%%)", currentSetupGrade, currentSetupScore) : "";
   color subClr = (currentSetupGrade == "A+") ? clrLime : ((currentSetupGrade == "A") ? clrDeepSkyBlue : ((liveSpread <= 45) ? clrDeepSkyBlue : clrTomato));
   CreateLabel("MINI_SUB", x + 80, y_sub, symTfText + gradeText, subClr, 8, false, corner);
   CreateLabel("MINI_TIMER", x + 250, y_timer, StringFormat("⏱ %s", lastCountdownStr), InpColorCountdown, 8, true, corner);

   // 3. Baris 1: Trend & Triple Screen
   double curPrice = rates[0].close;
   double e125_0   = ema125Series[0];
   color trendColor = (curPrice > e125_0) ? clrLimeGreen : clrTomato;
   string trendVal  = (curPrice > e125_0) ? "Bull (M5)" : "Bear (M5)";

   CreateLabel("MINI_L_TR", x + 10, y_row1, "Trend:", C'160,175,195', 8, false, corner);
   CreateLabel("MINI_V_TR", x + 48, y_row1, trendVal, trendColor, 8, true, corner);

   string screenStatus = "";
   color  screenClr    = clrGold;
   if(InpUseTripleScreen)
     {
      string s1Short = (StringFind(currentScreen1Status, "BULLISH") >= 0) ? "Bull" : ((StringFind(currentScreen1Status, "BEARISH") >= 0) ? "Bear" : "Sync");
      string s2Short = (StringFind(currentScreen2Status, "BULLISH") >= 0) ? "HH-HL" : ((StringFind(currentScreen2Status, "BEARISH") >= 0) ? "LH-LL" : "Range");
      screenStatus = StringFormat("H1:%s | M15:%s", s1Short, s2Short);
      screenClr = (s1Short == "Bull" && s2Short == "HH-HL") ? clrLime : ((s1Short == "Bear" && s2Short == "LH-LL") ? clrTomato : clrGold);
     }
   else
     {
      screenStatus = StringFormat("HTF(%s): %s", GetTfShortName(effectiveHTF), (currentHtfStatus == "BULLISH (Above 50)") ? "Bull" : ((currentHtfStatus == "BEARISH (Below 50)") ? "Bear" : "Flat"));
      screenClr = currentHtfColor;
     }
   CreateLabel("MINI_V_HTF", x + 130, y_row1, screenStatus, screenClr, 8, false, corner);

   // 4. Baris 2: S/R & Entry Target
   string resStr = (g_nearestRes > 0.0) ? StringFormat("%.2f", g_nearestRes) : "-";
   string supStr = (g_nearestSup > 0.0) ? StringFormat("%.2f", g_nearestSup) : "-";
   double entryVal = (lastEntryPrice > 0.0) ? lastEntryPrice : NormalizeDouble((ema8Series[0] + ema21Series[0]) / 2.0, _Digits);
   string entryStr = StringFormat("%.2f", entryVal);

   string snrEntryText = StringFormat("🎯 Res: %s  |  Sup: %s  |  Entry: %s", resStr, supStr, entryStr);
   CreateLabel("MINI_SNR", x + 10, y_row2, snrEntryText, C'205,215,230', 8, false, corner);
  }

//+------------------------------------------------------------------+
//| Menggambar HUD Dashboard Elegan & Rapi pada Chart (Posisi Bawah) |
//+------------------------------------------------------------------+
void DrawDashboard(const MqlRates &rates[], const double &ema8Series[], const double &ema21Series[], const double &ema125Series[])
  {
   int x = InpDashboardX;
   int y = InpDashboardY;
   int width = 430;  // Lebar proporsional agar tidak ada teks yang terpotong
   int height = 315; // Tinggi mencakup baris S/R, Entry & Countdown
   ENUM_BASE_CORNER corner = InpDashboardCorner;

   bool isLower = (corner == CORNER_LEFT_LOWER || corner == CORNER_RIGHT_LOWER);

   int y_bg     = y;
   int y_header = isLower ? (y + height - 28) : y;
   int y_title  = isLower ? (y + height - 21) : (y + 6);
   int y_sub    = isLower ? (y + height - 20) : (y + 7);
   int y_row1   = isLower ? (y + height - 48) : (y + 34);
   int stepY    = isLower ? -21 : 21;
   int y_div    = isLower ? (y + 26) : (y + 281);
   int y_foot   = isLower ? (y + 8)  : (y + 287);

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

   // Baris 8: Resistance Level
   lineY += stepY;
   string resStr = (g_nearestRes > 0.0) ? StringFormat("$%.2f", g_nearestRes) : "None";
   CreateLabel("L_RES", x + 14, lineY, "Resistance:", C'180,185,195', 9, false, corner);
   CreateLabel("V_RES", x_val, lineY, resStr, InpColorResistance, 9, true, corner);

   // Baris 9: Support Level
   lineY += stepY;
   string supStr = (g_nearestSup > 0.0) ? StringFormat("$%.2f", g_nearestSup) : "None";
   CreateLabel("L_SUP", x + 14, lineY, "Support:", C'180,185,195', 9, false, corner);
   CreateLabel("V_SUP", x_val, lineY, supStr, InpColorSupport, 9, true, corner);

   // Baris 10: Entry Level Sinyal / Proyeksi
   lineY += stepY;
   string entryStr = "";
   color  entryClr = clrGold;
   if(lastEntryPrice > 0.0 && lastSignalType != "None")
     {
      entryStr = StringFormat("$%.2f (%s)", lastEntryPrice, lastSignalType);
      entryClr = (lastSignalType == "SELL") ? InpColorEntrySell : InpColorEntryBuy;
     }
   else
     {
      double projPrice = NormalizeDouble((e8_0 + e21_0) / 2.0, _Digits);
      entryStr = StringFormat("$%.2f (Projected)", projPrice);
      entryClr = clrGold;
     }
   CreateLabel("L_ENTRY", x + 14, lineY, "Entry Level:", C'180,185,195', 9, false, corner);
   CreateLabel("V_ENTRY", x_val, lineY, entryStr, entryClr, 9, true, corner);

   // Baris 11: Countdown Penutupan Candle
   lineY += stepY;
   CreateLabel("L_CLOSE", x + 14, lineY, "Candle Close In:", C'180,185,195', 9, false, corner);
   CreateLabel("V_CLOSE", x_val, lineY, lastCountdownStr, InpColorCountdown, 9, true, corner);

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
