//+------------------------------------------------------------------+
//|                               Double_Top_Bottom_Indicator.mq5    |
//|                 Double Top & Double Bottom Visual System         |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.00"
#property description "Indikator Visual Deteksi Pola Double Top (M) & Double Bottom (W) dengan Garis Neckline, Filter Volume, dan HUD Dashboard"

#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   2

// Plot 1: Buy Signal Arrow
#property indicator_label1  "Double Bottom Buy Signal"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrAqua
#property indicator_style1  STYLE_SOLID
#property indicator_width1  2

// Plot 2: Sell Signal Arrow
#property indicator_label2  "Double Top Sell Signal"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrMagenta
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

// Include modul strategi
#include "..\Include\DoublePattern_Core.mqh"

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== Parameter Deteksi Pola Double Top & Bottom ==="
input int                  InpSwingLookback        = 3;             // Fractal Swing Lookback (Bars)
input int                  InpMinBarsBetween       = 5;             // Minimal Jarak Lilin Antar Puncak/Lembah
input int                  InpMaxBarsBetween       = 60;            // Maksimal Jarak Lilin Antar Puncak/Lembah
input double               InpTolerancePct         = 15.0;          // Toleransi Keselarasan Puncak/Lembah (%)
input double               InpMinHeightPoints      = 50.0;          // Minimal Tinggi Pola (Points)
input double               InpMinVolumeMultiplier  = 1.15;          // Minimal Pengali Volume Breakout (1.15x SMA)
input int                  InpVolumePeriod         = 20;            // Periode SMA Volume

input group "=== Kustomisasi Visual Garis & Pola ==="
input bool                 InpShowPatternLines     = true;          // Gambar Garis Bentuk Pola (M / W)
input bool                 InpShowNeckline         = true;          // Gambar Garis Horizontal Neckline
input color                InpColorDoubleBottom    = clrAqua;       // Warna Pola Double Bottom (W)
input color                InpColorDoubleTop       = clrLightCoral; // Warna Pola Double Top (M)
input color                InpColorNeckline        = clrGold;       // Warna Garis Neckline

input group "=== Tampilan Visual & Dashboard HUD ==="
input bool                 InpShowDashboard        = true;          // Tampilkan HUD Dashboard di Chart
input ENUM_BASE_CORNER     InpDashboardCorner      = CORNER_LEFT_LOWER; // Letak Sudut Dashboard
input int                  InpDashboardX           = 20;            // Posisi X Dashboard (Pixel)
input int                  InpDashboardY           = 25;            // Posisi Y Dashboard (Pixel)

input group "=== Notifikasi & Alert ==="
input bool                 InpPopupAlert           = true;          // Pop-up Alert di Layar MT5
input bool                 InpPushNotification     = true;          // Push Notification ke HP (MT5 Mobile)
input bool                 InpSoundAlert           = true;          // Bunyi Alarm
input string               InpSoundFile            = "alert.wav";   // File Suara

//+------------------------------------------------------------------+
//| Buffer Indikator                                                 |
//+------------------------------------------------------------------+
double BufferBuySignal[];
double BufferSellSignal[];

// Objek Mesin Pola
CDoublePatternCore patternEngine;

// Status Dashboard
datetime lastAlertBarTime   = 0;
string   lastDetectedSignal = "Scanning for M / W Patterns";
color    lastSignalColor    = C'180,185,195';

#define PREFIX_DASH "DBL_DASH_"
#define PREFIX_LINE "DBL_LINE_"
#define PREFIX_NECK "DBL_NECK_"

//+------------------------------------------------------------------+
//| Format Singkat Timeframe                                         |
//+------------------------------------------------------------------+
string GetTfShortName(ENUM_TIMEFRAMES tf)
  {
   switch(tf)
     {
      case PERIOD_M1:  return "M1";
      case PERIOD_M5:  return "M5";
      case PERIOD_M15: return "M15";
      case PERIOD_M30: return "M30";
      case PERIOD_H1:  return "H1";
      case PERIOD_H4:  return "H4";
      case PERIOD_D1:  return "D1";
      case PERIOD_W1:  return "W1";
      case PERIOD_MN1: return "MN";
      default:         return EnumToString(tf);
     }
  }

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
//| Helper Menggambar Garis Segmen Pola                              |
//+------------------------------------------------------------------+
void DrawTrendLine(string name, datetime t1, double p1, datetime t2, double p2, color clr, int width = 2, ENUM_LINE_STYLE style = STYLE_SOLID)
  {
   if(ObjectFind(0, name) < 0)
     {
      ObjectCreate(0, name, OBJ_TREND, 0, t1, p1, t2, p2);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
     }
   else
     {
      ObjectMove(0, name, 0, t1, p1);
      ObjectMove(0, name, 1, t2, p2);
     }
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_WIDTH, width);
   ObjectSetInteger(0, name, OBJPROP_STYLE, style);
   ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, false);
   ObjectSetInteger(0, name, OBJPROP_BACK, false);
  }

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
  {
   SetIndexBuffer(0, BufferBuySignal, INDICATOR_DATA);
   SetIndexBuffer(1, BufferSellSignal, INDICATOR_DATA);

   PlotIndexSetInteger(0, PLOT_ARROW, 233); // Panah Naik (Buy)
   PlotIndexSetInteger(1, PLOT_ARROW, 234); // Panah Turun (Sell)

   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, 0.0);

   patternEngine.Configure(InpSwingLookback, InpMinBarsBetween, InpMaxBarsBetween,
                           InpTolerancePct, InpMinHeightPoints, InpMinVolumeMultiplier, InpVolumePeriod);

   IndicatorSetString(INDICATOR_SHORTNAME, "Double Top & Bottom Pattern System");
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   ObjectsDeleteAll(0, PREFIX_DASH);
   ObjectsDeleteAll(0, PREFIX_LINE);
   ObjectsDeleteAll(0, PREFIX_NECK);
  }

//+------------------------------------------------------------------+
//| Render Garis Pola & Neckline di Chart                            |
//+------------------------------------------------------------------+
void RenderPatternVisuals(const MqlRates &rates[], int totalBars)
  {
   if(!patternEngine.HasActivePattern()) return;

   DoublePatternInfo pat = patternEngine.GetActivePattern();

   color patColor = (pat.type == PATTERN_DOUBLE_BOTTOM) ? InpColorDoubleBottom : InpColorDoubleTop;

   if(InpShowPatternLines)
     {
      // 1. Garis Puncak/Lembah 1 ke Neckline
      DrawTrendLine(PREFIX_LINE + "LEG1", pat.t1, pat.p1, pat.tNeck, pat.pNeck, patColor, 2, STYLE_SOLID);

      // 2. Garis Neckline ke Puncak/Lembah 2
      DrawTrendLine(PREFIX_LINE + "LEG2", pat.tNeck, pat.pNeck, pat.t2, pat.p2, patColor, 2, STYLE_SOLID);

      // 3. Garis Puncak/Lembah 2 ke Breakout / Bar Berjalan
      datetime targetTime = (pat.tBreak > 0) ? pat.tBreak : rates[0].time;
      double targetPrice  = (pat.pBreak > 0) ? pat.pBreak : rates[0].close;
      DrawTrendLine(PREFIX_LINE + "LEG3", pat.t2, pat.p2, targetTime, targetPrice, patColor, 2, STYLE_DOT);
     }

   if(InpShowNeckline && pat.pNeck > 0.0)
     {
      datetime rightTime = rates[0].time + PeriodSeconds() * 10;
      DrawTrendLine(PREFIX_NECK + "HORIZ", pat.tNeck, pat.pNeck, rightTime, pat.pNeck, InpColorNeckline, 2, STYLE_DASH);
     }
  }

//+------------------------------------------------------------------+
//| Menggambar HUD Dashboard Elegan & Rapi                           |
//+------------------------------------------------------------------+
void DrawDashboard(const MqlRates &rates[])
  {
   int x = InpDashboardX;
   int y = InpDashboardY;
   int width = 430;
   int height = 232;
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

   // Background Panel Elegan
   CreatePanel("BG", x, y_bg, width, height, C'20,26,38', C'52,66,92', corner);
   CreatePanel("HEADER", x, y_header, width, 28, C'30,38,54', C'65,82,112', corner);

   // Header
   long liveSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   CreateLabel("TITLE", x + 14, y_title, "DOUBLE TOP & BOTTOM PATTERNS", clrGold, 9, true, corner);
   string symTfText = StringFormat("[%s | %s | Spr: %d]", _Symbol, GetTfShortName(_Period), liveSpread);
   CreateLabel("SUBTITLE", x + 245, y_sub, symTfText, (liveSpread <= 45) ? clrDeepSkyBlue : clrTomato, 8, false, corner);

   int lineY = y_row1;
   int x_val = x + 150;

   DoublePatternInfo pat = patternEngine.GetActivePattern();

   // Baris 1: Status Pola Terkini
   string patText = "Scanning for M / W Patterns";
   color  patColor = C'180,185,195';

   if(pat.type == PATTERN_DOUBLE_BOTTOM)
     {
      if(pat.status == STATUS_CONFIRMED) { patText = "DOUBLE BOTTOM (Breakout W!)"; patColor = clrAqua; }
      else { patText = "Double Bottom (Forming W)"; patColor = clrDeepSkyBlue; }
     }
   else if(pat.type == PATTERN_DOUBLE_TOP)
     {
      if(pat.status == STATUS_CONFIRMED) { patText = "DOUBLE TOP (Breakout M!)"; patColor = clrMagenta; }
      else { patText = "Double Top (Forming M)"; patColor = clrLightCoral; }
     }

   CreateLabel("L_PAT", x + 14, lineY, "Pattern Status:", C'180,185,195', 9, false, corner);
   CreateLabel("V_PAT", x_val, lineY, patText, patColor, 9, true, corner);

   // Baris 2: Level Neckline
   lineY += stepY;
   string neckText = (pat.pNeck > 0.0) ? StringFormat("%.2f", pat.pNeck) : "Waiting for Neckline";
   color  neckColor = (pat.pNeck > 0.0) ? clrGold : C'140,150,165';
   CreateLabel("L_NECK", x + 14, lineY, "Neckline Level:", C'180,185,195', 9, false, corner);
   CreateLabel("V_NECK", x_val, lineY, neckText, neckColor, 9, true, corner);

   // Baris 3: Level Puncak / Lembah (Extremum)
   lineY += stepY;
   string extText = "None";
   color  extColor = C'140,150,165';
   if(pat.type == PATTERN_DOUBLE_BOTTOM && pat.p1 > 0.0)
     {
      extText = StringFormat("Support: %.2f & %.2f", pat.p1, pat.p2);
      extColor = clrAqua;
     }
   else if(pat.type == PATTERN_DOUBLE_TOP && pat.p1 > 0.0)
     {
      extText = StringFormat("Resistance: %.2f & %.2f", pat.p1, pat.p2);
      extColor = clrSalmon;
     }
   CreateLabel("L_EXT", x + 14, lineY, "Pattern Extremum:", C'180,185,195', 9, false, corner);
   CreateLabel("V_EXT", x_val, lineY, extText, extColor, 9, false, corner);

   // Baris 4: Tinggi Pola (Target Height Projection)
   lineY += stepY;
   double pts = (pat.patternHeight > 0.0) ? (pat.patternHeight / _Point) : 0.0;
   string hText = (pts > 0.0) ? StringFormat("%.1f Points (Target TP)", pts) : "0.0";
   CreateLabel("L_HEIGHT", x + 14, lineY, "Pattern Height:", C'180,185,195', 9, false, corner);
   CreateLabel("V_HEIGHT", x_val, lineY, hText, (pts >= InpMinHeightPoints) ? clrLime : C'140,150,165', 9, false, corner);

   // Baris 5: Rasio Volume Breakout
   lineY += stepY;
   string volText = "Standard Volume";
   color  volColor = C'170,180,195';
   if(pat.volumeRatio > 0.0)
     {
      volText = StringFormat("%.2fx SMA (High Volume Confirmed)", pat.volumeRatio);
      volColor = (pat.volumeRatio >= InpMinVolumeMultiplier) ? clrLime : clrTomato;
     }
   CreateLabel("L_VOL", x + 14, lineY, "Breakout Volume:", C'180,185,195', 9, false, corner);
   CreateLabel("V_VOL", x_val, lineY, volText, volColor, 8, true, corner);

   // Baris 6: Sinyal Terakhir
   lineY += stepY;
   CreateLabel("L_SIGNAL", x + 14, lineY, "Trade Signal:", C'180,185,195', 9, false, corner);
   CreateLabel("V_SIGNAL", x_val, lineY, lastDetectedSignal, lastSignalColor, 9, true, corner);

   // Baris 7: Status Sistem
   lineY += stepY;
   CreateLabel("L_STATUS", x + 14, lineY, "System Status:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STATUS", x_val, lineY, "Pattern Engine Active", clrLime, 8, true, corner);

   // Garis Pembatas & Footer
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
   if(rates_total < (InpMaxBarsBetween + 30)) return 0;

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, MathMin(rates_total, 300), rates);
   if(copied < 40) return 0;

   patternEngine.Update(rates, copied);

   if(prev_calculated > 0)
     {
      BufferBuySignal[rates_total - 1]  = 0.0;
      BufferSellSignal[rates_total - 1] = 0.0;
     }

   double currentAtr = (rates[1].high - rates[1].low);
   if(currentAtr <= 0) currentAtr = 1.0 * _Point;

   int bar1_idx = rates_total - 2;

   DoublePatternInfo confirmedPat;

   // 1. Cek Breakout Double Bottom (BUY)
   if(patternEngine.IsDoubleBottomBreakout(rates, confirmedPat))
     {
      BufferBuySignal[bar1_idx] = rates[1].low - (currentAtr * 0.5);
      lastDetectedSignal = "BUY CONFIRMED (W Neckline Break)";
      lastSignalColor    = clrAqua;

      if(rates[1].time != lastAlertBarTime && prev_calculated > 0)
        {
         lastAlertBarTime = rates[1].time;
         if(InpPopupAlert) Alert(StringFormat("[DOUBLE BOTTOM BUY] %s %s: Breakout Neckline di %.2f (Vol: %.2fx)",
                                              _Symbol, GetTfShortName(_Period), rates[1].close, confirmedPat.volumeRatio));
         if(InpPushNotification) SendNotification(StringFormat("DOUBLE BOTTOM BUY: %s %s @ %.2f", _Symbol, GetTfShortName(_Period), rates[1].close));
         if(InpSoundAlert && InpSoundFile != "") PlaySound(InpSoundFile);
        }
     }
   // 2. Cek Breakdown Double Top (SELL)
   else if(patternEngine.IsDoubleTopBreakout(rates, confirmedPat))
     {
      BufferSellSignal[bar1_idx] = rates[1].high + (currentAtr * 0.5);
      lastDetectedSignal = "SELL CONFIRMED (M Neckline Break)";
      lastSignalColor    = clrMagenta;

      if(rates[1].time != lastAlertBarTime && prev_calculated > 0)
        {
         lastAlertBarTime = rates[1].time;
         if(InpPopupAlert) Alert(StringFormat("[DOUBLE TOP SELL] %s %s: Breakdown Neckline di %.2f (Vol: %.2fx)",
                                              _Symbol, GetTfShortName(_Period), rates[1].close, confirmedPat.volumeRatio));
         if(InpPushNotification) SendNotification(StringFormat("DOUBLE TOP SELL: %s %s @ %.2f", _Symbol, GetTfShortName(_Period), rates[1].close));
         if(InpSoundAlert && InpSoundFile != "") PlaySound(InpSoundFile);
        }
     }

   // Gambar pola garis dan garis horizontal Neckline di chart
   RenderPatternVisuals(rates, copied);

   // Gambar HUD Dashboard
   if(InpShowDashboard)
     {
      DrawDashboard(rates);
     }

   return(rates_total);
  }
