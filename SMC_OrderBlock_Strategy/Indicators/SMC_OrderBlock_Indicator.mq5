//+------------------------------------------------------------------+
//|                                  SMC_OrderBlock_Indicator.mq5   |
//|    Institutional SMC & S/R Master (Support, Resistance, Fibo,   |
//|                 Order Block, FVG, BOS & CHoCH System)            |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.20"
#property description "Institutional SMC & S/R Master: Garis Support/Resistance Dinamis, Auto Fibo Golden Zone, Order Block, FVG, BOS/CHoCH, & HUD Dashboard"

#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   2

// Plot 1: Buy Signal Arrow
#property indicator_label1  "SMC Buy Signal"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrAqua
#property indicator_style1  STYLE_SOLID
#property indicator_width1  2

// Plot 2: Sell Signal Arrow
#property indicator_label2  "SMC Sell Signal"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrMagenta
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

// Include modul SMC Core
#include "..\Include\SMC_Core.mqh"

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== 1. Garis Support & Resistance (Realtime & Kuat) ==="
input bool                 InpShowSR               = true;          // Tampilkan Garis Support & Resistance
input int                  InpSrLookbackMajor      = 15;            // Lookback Major S/R (Terkuat)
input int                  InpSrLookbackMinor      = 5;             // Lookback Minor S/R (Terdekat)
input color                InpColorMajorRes        = C'242,54,69';  // Warna Major Resistance (Merah Solid)
input color                InpColorMajorSup        = C'8,153,129';  // Warna Major Support (Hijau Solid)
input color                InpColorMinorRes        = C'235,87,87';  // Warna Minor Resistance (Merah Putus-putus)
input color                InpColorMinorSup        = C'39,174,96';  // Warna Minor Support (Hijau Putus-putus)
input bool                 InpShowSRLabels         = true;          // Tampilkan Label Harga S/R di Kanan

input group "=== 2. Auto Fibonacci Golden Zone (0.50 - 0.65 OTE) ==="
input bool                 InpShowFibo             = true;          // Tampilkan Auto Fibo Golden Zone
input color                InpColorGoldenZone      = C'65,50,15';   // Warna Kotak Golden Pocket
input color                InpColorFibo618         = clrGold;       // Warna Garis Rasio Emas 61.8%
input bool                 InpShowFiboLabel        = true;          // Tampilkan Label Fibo 61.8%

input group "=== 3. Garis Struktur Pasar (BOS & CHoCH) ==="
input bool                 InpShowStructureLines   = true;          // Tampilkan Garis BOS & CHoCH
input color                InpColorBullStruct      = clrLime;       // Warna Bullish Structure (BOS/CHoCH)
input color                InpColorBearStruct      = clrTomato;     // Warna Bearish Structure (BOS/CHoCH)

input group "=== 4. Institutional Order Block (OB) & FVG ==="
input int                  InpSwingLookback        = 3;             // Fractal Swing Lookback (Bars)
input int                  InpMaxZones             = 8;             // Maksimal Zona OB & FVG Aktif
input double               InpMinFvgPoints         = 30.0;          // Ukuran Minimal FVG (Points)
input double               InpMinObPoints          = 20.0;          // Ukuran Minimal Order Block (Points)
input bool                 InpShowOrderBlocks      = true;          // Gambar Kotak Order Block (OB) di Chart
input bool                 InpShowFVG              = true;          // Gambar Kotak Fair Value Gap (FVG)
input bool                 InpShowMitigatedZones   = true;          // Tampilkan Zona Termitigasi (Garis Muted)
input color                InpColorBullishOB       = C'30,70,140';  // Warna Bullish OB (Demand)
input color                InpColorBearishOB       = C'140,40,50';  // Warna Bearish OB (Supply)
input color                InpColorBullishFVG      = C'20,110,90';  // Warna Bullish FVG
input color                InpColorBearishFVG      = C'130,50,110'; // Warna Bearish FVG

input group "=== 5. HUD Dashboard On-Chart ==="
input bool                 InpShowDashboard        = true;          // Tampilkan HUD Dashboard di Chart
input ENUM_BASE_CORNER     InpDashboardCorner      = CORNER_LEFT_LOWER; // Letak Sudut Dashboard
input int                  InpDashboardX           = 20;            // Posisi X Dashboard (Pixel)
input int                  InpDashboardY           = 25;            // Posisi Y Dashboard (Pixel)

input group "=== 6. Sistem Notifikasi & Alert ==="
input bool                 InpPopupAlert           = true;          // Pop-up Alert di Layar MT5
input bool                 InpPushNotification     = true;          // Push Notification ke HP (MT5 Mobile)
input bool                 InpSoundAlert           = true;          // Bunyi Alarm
input string               InpSoundFile            = "alert.wav";   // File Suara

//+------------------------------------------------------------------+
//| Buffer Indikator                                                 |
//+------------------------------------------------------------------+
double BufferBuySignal[];
double BufferSellSignal[];

// Objek Mesin SMC Core
CSMCCore smcEngine;

// Status Global & Prefiks Objek
datetime lastAlertBarTime    = 0;
string   lastDetectedSignal  = "Scanning Setup...";
color    lastSignalColor     = C'180,185,195';

double   g_majorRes          = 0.0;
double   g_majorSup          = 0.0;
double   g_minorRes          = 0.0;
double   g_minorSup          = 0.0;

#define PREFIX_SMC  "SMC_DASH_"
#define PREFIX_SR   "SMC_SR_"
#define PREFIX_FIB  "SMC_FIB_"
#define PREFIX_STR  "SMC_STR_"
#define PREFIX_OB   "SMC_OB_"
#define PREFIX_FVG  "SMC_FVG_"

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
//| Helper Menggambar Garis Horizontal Memanjang (Ray Right)         |
//+------------------------------------------------------------------+
void DrawRayLine(string name, datetime t1, double p1, datetime t2, double p2, color clr, int width, ENUM_LINE_STYLE style)
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
   ObjectSetInteger(0, name, OBJPROP_RAY_RIGHT, true);
   ObjectSetInteger(0, name, OBJPROP_BACK, true);
  }

//+------------------------------------------------------------------+
//| Helper Menggambar Tag Label Harga di Kanan Layar                 |
//+------------------------------------------------------------------+
void DrawPriceTag(string name, datetime t, double price, string text, color clr, int fontSize = 8)
  {
   if(ObjectFind(0, name) < 0)
     {
      ObjectCreate(0, name, OBJ_TEXT, 0, t, price);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
     }
   else
     {
      ObjectMove(0, name, 0, t, price);
     }
   ObjectSetString(0, name, OBJPROP_TEXT, text);
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetString(0, name, OBJPROP_FONT, "Segoe UI Bold");
   ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
   ObjectSetInteger(0, name, OBJPROP_ANCHOR, ANCHOR_LEFT);
   ObjectSetInteger(0, name, OBJPROP_BACK, false);
  }

//+------------------------------------------------------------------+
//| Helper Menggambar Objek Teks Dashboard                           |
//+------------------------------------------------------------------+
void CreateLabel(string name, int x, int y, string text, color clr, int fontSize = 9, bool isBold = false, ENUM_BASE_CORNER corner = CORNER_LEFT_LOWER)
  {
   string objName = PREFIX_SMC + name;
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
   string objName = PREFIX_SMC + name;
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
//| Helper Menggambar Kotak Zona di Chart (OB / FVG / Fibo)          |
//+------------------------------------------------------------------+
void DrawZoneBox(string name, datetime t1, double p1, datetime t2, double p2, color clr, bool isFilled = true, ENUM_LINE_STYLE style = STYLE_SOLID)
  {
   if(ObjectFind(0, name) < 0)
     {
      ObjectCreate(0, name, OBJ_RECTANGLE, 0, t1, p1, t2, p2);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_HIDDEN, true);
     }
   else
     {
      ObjectMove(0, name, 0, t1, p1);
      ObjectMove(0, name, 1, t2, p2);
     }
   ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_BGCOLOR, clr);
   ObjectSetInteger(0, name, OBJPROP_FILL, isFilled);
   ObjectSetInteger(0, name, OBJPROP_STYLE, style);
   ObjectSetInteger(0, name, OBJPROP_BACK, true);
  }

//+------------------------------------------------------------------+
//| Algoritma Deteksi Pivot High & Low                               |
//+------------------------------------------------------------------+
bool FindPivotHigh(const MqlRates &rates[], int total, int lookback, int startBar, double &outPrice, datetime &outTime)
  {
   for(int i = startBar + lookback; i < total - lookback; i++)
     {
      bool isHigh = true;
      for(int j = 1; j <= lookback; j++)
        {
         if(rates[i].high < rates[i - j].high || rates[i].high < rates[i + j].high)
           {
            isHigh = false;
            break;
           }
        }
      if(isHigh)
        {
         outPrice = rates[i].high;
         outTime  = rates[i].time;
         return true;
        }
     }
   return false;
  }

bool FindPivotLow(const MqlRates &rates[], int total, int lookback, int startBar, double &outPrice, datetime &outTime)
  {
   for(int i = startBar + lookback; i < total - lookback; i++)
     {
      bool isLow = true;
      for(int j = 1; j <= lookback; j++)
        {
         if(rates[i].low > rates[i - j].low || rates[i].low > rates[i + j].low)
           {
            isLow = false;
            break;
           }
        }
      if(isLow)
        {
         outPrice = rates[i].low;
         outTime  = rates[i].time;
         return true;
        }
     }
   return false;
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

   smcEngine.Configure(InpSwingLookback, InpMaxZones, InpMinFvgPoints, InpMinObPoints);

   IndicatorSetString(INDICATOR_SHORTNAME, "Institutional SMC & S/R Master");
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   ObjectsDeleteAll(0, PREFIX_SMC);
   ObjectsDeleteAll(0, PREFIX_SR);
   ObjectsDeleteAll(0, PREFIX_FIB);
   ObjectsDeleteAll(0, PREFIX_OB);
   ObjectsDeleteAll(0, PREFIX_FVG);
   ObjectsDeleteAll(0, PREFIX_STR);
  }

//+------------------------------------------------------------------+
//| 1. Render Garis Support & Resistance (Major & Minor Realtime)    |
//+------------------------------------------------------------------+
void RenderSRLines(const MqlRates &rates[], int totalBars)
  {
   if(!InpShowSR) return;

   datetime rightTime = rates[0].time + PeriodSeconds() * 12;

   // 1. Major Resistance & Support (Terkuat)
   double   majResP = 0.0, majSupP = 0.0;
   datetime majResT = 0,   majSupT = 0;

   if(FindPivotHigh(rates, totalBars, InpSrLookbackMajor, 1, majResP, majResT))
     {
      g_majorRes = majResP;
      DrawRayLine(PREFIX_SR + "MAJOR_RES", majResT, majResP, rightTime, majResP, InpColorMajorRes, 2, STYLE_SOLID);
      if(InpShowSRLabels)
         DrawPriceTag(PREFIX_SR + "LBL_MAJ_RES", rightTime, majResP, StringFormat(" R Major: %.2f", majResP), InpColorMajorRes, 8);
     }

   if(FindPivotLow(rates, totalBars, InpSrLookbackMajor, 1, majSupP, majSupT))
     {
      g_majorSup = majSupP;
      DrawRayLine(PREFIX_SR + "MAJOR_SUP", majSupT, majSupP, rightTime, majSupP, InpColorMajorSup, 2, STYLE_SOLID);
      if(InpShowSRLabels)
         DrawPriceTag(PREFIX_SR + "LBL_MAJ_SUP", rightTime, majSupP, StringFormat(" S Major: %.2f", majSupP), InpColorMajorSup, 8);
     }

   // 2. Minor Resistance & Support (Terdekat)
   double   minResP = 0.0, minSupP = 0.0;
   datetime minResT = 0,   minSupT = 0;

   if(FindPivotHigh(rates, totalBars, InpSrLookbackMinor, 1, minResP, minResT))
     {
      if(MathAbs(minResP - g_majorRes) > (_Point * 10))
        {
         g_minorRes = minResP;
         DrawRayLine(PREFIX_SR + "MINOR_RES", minResT, minResP, rightTime, minResP, InpColorMinorRes, 1, STYLE_DASH);
         if(InpShowSRLabels)
            DrawPriceTag(PREFIX_SR + "LBL_MIN_RES", rightTime, minResP, StringFormat(" R Minor: %.2f", minResP), InpColorMinorRes, 8);
        }
     }

   if(FindPivotLow(rates, totalBars, InpSrLookbackMinor, 1, minSupP, minSupT))
     {
      if(MathAbs(minSupP - g_majorSup) > (_Point * 10))
        {
         g_minorSup = minSupP;
         DrawRayLine(PREFIX_SR + "MINOR_SUP", minSupT, minSupP, rightTime, minSupP, InpColorMinorSup, 1, STYLE_DASH);
         if(InpShowSRLabels)
            DrawPriceTag(PREFIX_SR + "LBL_MIN_SUP", rightTime, minSupP, StringFormat(" S Minor: %.2f", minSupP), InpColorMinorSup, 8);
        }
     }
  }

//+------------------------------------------------------------------+
//| 2. Render Auto Fibonacci Golden Zone (0.50 - 0.65 OTE)           |
//+------------------------------------------------------------------+
void RenderFibonacciGoldenZone(const MqlRates &rates[], int totalBars)
  {
   if(!InpShowFibo) return;

   double highRange = smcEngine.GetDealingRangeHigh();
   double lowRange  = smcEngine.GetDealingRangeLow();
   double diffRange = highRange - lowRange;

   if(diffRange <= 0.0) return;

   datetime rightTime = rates[0].time + PeriodSeconds() * 12;

   bool isBullSwing = (rates[0].close >= (lowRange + diffRange * 0.50));
   double p50  = isBullSwing ? (highRange - diffRange * 0.50) : (lowRange + diffRange * 0.50);
   double p618 = isBullSwing ? (highRange - diffRange * 0.618) : (lowRange + diffRange * 0.618);
   double p65  = isBullSwing ? (highRange - diffRange * 0.65) : (lowRange + diffRange * 0.65);

   double topGold = MathMax(p50, p65);
   double btmGold = MathMin(p50, p65);

   datetime startFiboTime = rates[MathMin(totalBars - 1, 50)].time;
   for(int i = 0; i < MathMin(totalBars, 60); i++)
     {
      if(MathAbs(rates[i].high - highRange) < (_Point * 3) || MathAbs(rates[i].low - lowRange) < (_Point * 3))
        {
         startFiboTime = rates[i].time;
         break;
        }
     }

   // 1. Kotak Golden Pocket
   DrawZoneBox(PREFIX_FIB + "ZONE", startFiboTime, topGold, rightTime, btmGold, InpColorGoldenZone, true, STYLE_SOLID);

   // 2. Garis Rasio Emas 61.8%
   DrawRayLine(PREFIX_FIB + "618", startFiboTime, p618, rightTime, p618, InpColorFibo618, 2, STYLE_DASH);

   // 3. Tag Label 61.8%
   if(InpShowFiboLabel)
      DrawPriceTag(PREFIX_FIB + "LBL", rightTime, p618, StringFormat(" Golden 61.8%%: %.2f", p618), InpColorFibo618, 8);
  }

//+------------------------------------------------------------------+
//| 3. Render Garis Struktur Pasar (BOS & CHoCH)                     |
//+------------------------------------------------------------------+
void RenderStructureVisuals(const MqlRates &rates[], int totalBars)
  {
   if(!InpShowStructureLines) return;

   datetime rightTime = rates[0].time + PeriodSeconds() * 10;
   ENUM_SMC_STRUCTURE st = smcEngine.GetLastStructure();

   if(st == SMC_STRUCT_BULLISH_BOS || st == SMC_STRUCT_BULLISH_CHOCH)
     {
      datetime stTime = (st == SMC_STRUCT_BULLISH_BOS) ? smcEngine.GetLastBosTime() : smcEngine.GetLastChochTime();
      if(stTime > 0 && g_majorRes > 0)
        {
         string lbl = (st == SMC_STRUCT_BULLISH_BOS) ? "BOS [Bullish]" : "CHoCH [Bullish Reversal]";
         DrawRayLine(PREFIX_STR + "ACTIVE", stTime, g_majorRes, rightTime, g_majorRes, InpColorBullStruct, 2, (st == SMC_STRUCT_BULLISH_BOS) ? STYLE_SOLID : STYLE_DASH);
         DrawPriceTag(PREFIX_STR + "TAG", rightTime, g_majorRes, " " + lbl, InpColorBullStruct, 8);
        }
     }
   else if(st == SMC_STRUCT_BEARISH_BOS || st == SMC_STRUCT_BEARISH_CHOCH)
     {
      datetime stTime = (st == SMC_STRUCT_BEARISH_BOS) ? smcEngine.GetLastBosTime() : smcEngine.GetLastChochTime();
      if(stTime > 0 && g_majorSup > 0)
        {
         string lbl = (st == SMC_STRUCT_BEARISH_BOS) ? "BOS [Bearish]" : "CHoCH [Bearish Reversal]";
         DrawRayLine(PREFIX_STR + "ACTIVE", stTime, g_majorSup, rightTime, g_majorSup, InpColorBearStruct, 2, (st == SMC_STRUCT_BEARISH_BOS) ? STYLE_SOLID : STYLE_DASH);
         DrawPriceTag(PREFIX_STR + "TAG", rightTime, g_majorSup, " " + lbl, InpColorBearStruct, 8);
        }
     }
  }

//+------------------------------------------------------------------+
//| 4. Render Kotak Zona Order Block & Fair Value Gap                |
//+------------------------------------------------------------------+
void RenderSMCVisuals(const MqlRates &rates[], int totalBars)
  {
   datetime rightTime = rates[0].time + PeriodSeconds() * 12;

   // 1. Gambar Kotak Order Block
   if(InpShowOrderBlocks)
     {
      int obTotal = smcEngine.GetOrderBlocksTotal();
      for(int i = 0; i < obTotal; i++)
        {
         SMC_OrderBlock ob;
         if(smcEngine.GetOrderBlock(i, ob))
           {
            string name = StringFormat("%s_%d_%d", PREFIX_OB, i, (int)ob.time);

            if(!ob.isMitigated && !ob.isInvalidated)
              {
               color c = ob.isBullish ? InpColorBullishOB : InpColorBearishOB;
               DrawZoneBox(name, ob.time, ob.high, rightTime, ob.low, c, true, STYLE_SOLID);
              }
            else if(ob.isMitigated && ob.mitigatedTime > 0 && InpShowMitigatedZones)
              {
               color cMuted = ob.isBullish ? C'25,50,70' : C'70,35,40';
               DrawZoneBox(name, ob.time, ob.high, ob.mitigatedTime, ob.low, cMuted, false, STYLE_DOT);
              }
            else
              {
               ObjectDelete(0, name);
              }
           }
        }
     }

   // 2. Gambar Kotak Fair Value Gap (FVG)
   if(InpShowFVG)
     {
      int fvgTotal = smcEngine.GetFvgsTotal();
      for(int i = 0; i < fvgTotal; i++)
        {
         SMC_FairValueGap fvg;
         if(smcEngine.GetFvg(i, fvg))
           {
            string name = StringFormat("%s_%d_%d", PREFIX_FVG, i, (int)fvg.time);

            if(!fvg.isMitigated)
              {
               color c = fvg.isBullish ? InpColorBullishFVG : InpColorBearishFVG;
               DrawZoneBox(name, fvg.time, fvg.top, rightTime, fvg.bottom, c, false, STYLE_SOLID);
              }
            else if(fvg.isMitigated && fvg.mitigatedTime > 0 && InpShowMitigatedZones)
              {
               color cMuted = fvg.isBullish ? C'20,60,50' : C'60,30,55';
               DrawZoneBox(name, fvg.time, fvg.top, fvg.mitigatedTime, fvg.bottom, cMuted, false, STYLE_DOT);
              }
            else
              {
               ObjectDelete(0, name);
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| 5. Menggambar HUD Dashboard Elegan & Rapi di Chart               |
//+------------------------------------------------------------------+
void DrawDashboard(const MqlRates &rates[], double currentAtr)
  {
   int x = InpDashboardX;
   int y = InpDashboardY;
   int width = 430;
   int height = 250;
   ENUM_BASE_CORNER corner = InpDashboardCorner;

   bool isLower = (corner == CORNER_LEFT_LOWER || corner == CORNER_RIGHT_LOWER);

   int y_bg     = y;
   int y_header = isLower ? (y + height - 28) : y;
   int y_title  = isLower ? (y + height - 21) : (y + 6);
   int y_sub    = isLower ? (y + height - 20) : (y + 7);
   int y_row1   = isLower ? (y + height - 48) : (y + 34);
   int stepY    = isLower ? -20 : 20;
   int y_div    = isLower ? (y + 26) : (y + 214);
   int y_foot   = isLower ? (y + 8)  : (y + 220);

   // Background Panel Elegan
   CreatePanel("BG", x, y_bg, width, height, C'20,26,38', C'52,66,92', corner);
   CreatePanel("HEADER", x, y_header, width, 28, C'30,38,54', C'65,82,112', corner);

   // Header
   long liveSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   CreateLabel("TITLE", x + 14, y_title, "INSTITUTIONAL SMC & S/R", clrGold, 9, true, corner);
   string symTfText = StringFormat("[%s | %s | Spr: %d]", _Symbol, GetTfShortName(_Period), liveSpread);
   CreateLabel("SUBTITLE", x + 215, y_sub, symTfText, (liveSpread <= 45) ? clrDeepSkyBlue : clrTomato, 8, false, corner);

   int lineY = y_row1;
   int x_val = x + 150;

   // Baris 1: Struktur Pasar Terakhir (BOS / CHoCH)
   ENUM_SMC_STRUCTURE st = smcEngine.GetLastStructure();
   string stText = "Neutral (Consolidating)";
   color  stColor = C'180,185,195';
   if(st == SMC_STRUCT_BULLISH_CHOCH) { stText = "BULLISH CHoCH (Reversal UP)"; stColor = clrLime; }
   else if(st == SMC_STRUCT_BEARISH_CHOCH) { stText = "BEARISH CHoCH (Reversal DOWN)"; stColor = clrTomato; }
   else if(st == SMC_STRUCT_BULLISH_BOS)   { stText = "BULLISH BOS (Trend UP)"; stColor = clrAqua; }
   else if(st == SMC_STRUCT_BEARISH_BOS)   { stText = "BEARISH BOS (Trend DOWN)"; stColor = clrSalmon; }

   CreateLabel("L_STRUCT", x + 14, lineY, "Market Structure:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STRUCT", x_val, lineY, stText, stColor, 9, true, corner);

   // Baris 2: Major Resistance Terkuat
   lineY += stepY;
   string resStr = (g_majorRes > 0) ? StringFormat("%.2f (+%d pips)", g_majorRes, (int)((g_majorRes - rates[0].close) / _Point / 10)) : "Scanning...";
   CreateLabel("L_MAJ_RES", x + 14, lineY, "Major Resistance:", C'180,185,195', 9, false, corner);
   CreateLabel("V_MAJ_RES", x_val, lineY, resStr, C'242,54,69', 9, true, corner);

   // Baris 3: Major Support Terkuat
   lineY += stepY;
   string supStr = (g_majorSup > 0) ? StringFormat("%.2f (-%d pips)", g_majorSup, (int)((rates[0].close - g_majorSup) / _Point / 10)) : "Scanning...";
   CreateLabel("L_MAJ_SUP", x + 14, lineY, "Major Support:", C'180,185,195', 9, false, corner);
   CreateLabel("V_MAJ_SUP", x_val, lineY, supStr, C'8,153,129', 9, true, corner);

   // Baris 4: Status Fibo Golden Zone
   lineY += stepY;
   double highRange = smcEngine.GetDealingRangeHigh();
   double lowRange  = smcEngine.GetDealingRangeLow();
   double diffRange = highRange - lowRange;
   string fiboText = "Equilibrium";
   color  fiboClr  = clrGold;

   if(diffRange > 0)
     {
      double midRange = lowRange + diffRange * 0.50;
      double p618 = highRange - diffRange * 0.618;
      if(MathAbs(rates[0].close - p618) <= (_Point * 25))
        {
         fiboText = "IN GOLDEN POCKET (0.618 OTE)!";
         fiboClr  = clrGold;
        }
      else if(rates[0].close > midRange)
        {
         fiboText = "Premium Zone (Look for Sell)";
         fiboClr  = C'242,54,69';
        }
      else
        {
         fiboText = "Discount Zone (Look for Buy)";
         fiboClr  = C'8,153,129';
        }
     }
   CreateLabel("L_FIBO", x + 14, lineY, "Fibonacci Zone:", C'180,185,195', 9, false, corner);
   CreateLabel("V_FIBO", x_val, lineY, fiboText, fiboClr, 9, true, corner);

   // Baris 5: Order Block Aktif
   lineY += stepY;
   int unmitOB = 0;
   int obTotal = smcEngine.GetOrderBlocksTotal();
   for(int i = 0; i < obTotal; i++)
     {
      SMC_OrderBlock ob;
      if(smcEngine.GetOrderBlock(i, ob) && !ob.isMitigated && !ob.isInvalidated) unmitOB++;
     }
   CreateLabel("L_OB", x + 14, lineY, "Active Order Blocks:", C'180,185,195', 9, false, corner);
   CreateLabel("V_OB", x_val, lineY, StringFormat("%d Zones Unmitigated", unmitOB), clrDeepSkyBlue, 9, true, corner);

   // Baris 6: Sinyal Konfirmasi Retest
   lineY += stepY;
   CreateLabel("L_SIGNAL", x + 14, lineY, "Trade Signal:", C'180,185,195', 9, false, corner);
   CreateLabel("V_SIGNAL", x_val, lineY, lastDetectedSignal, lastSignalColor, 9, true, corner);

   // Baris 7: Status Sistem
   lineY += stepY;
   CreateLabel("L_STATUS", x + 14, lineY, "System Status:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STATUS", x_val, lineY, "SMC & S/R Engine Running", clrLime, 8, true, corner);

   // Garis Pembatas & Footer
   CreatePanel("DIVIDER", x + 12, y_div, width - 24, 1, C'42,54,75', C'42,54,75', corner);

   MqlDateTime dt;
   TimeCurrent(dt);
   string sessionName = "Asian Session";
   if(dt.hour >= 8 && dt.hour < 13) sessionName = "London Session (Active)";
   else if(dt.hour >= 13 && dt.hour < 17) sessionName = "London-NY Overlap (Peak)";
   else if(dt.hour >= 17 && dt.hour < 22) sessionName = "New York Session (Active)";
   else sessionName = "Asian / Rollover (Quiet)";

   string footerText = StringFormat("● Sesi Pasar: %s", sessionName);
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
   if(rates_total < 40) return 0;

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, MathMin(rates_total, 300), rates);
   if(copied < 35) return 0;

   // Update mesin SMC
   smcEngine.Update(rates, copied);

   // Bersihkan buffer bar berjalan
   if(prev_calculated > 0)
     {
      BufferBuySignal[rates_total - 1]  = 0.0;
      BufferSellSignal[rates_total - 1] = 0.0;
     }

   // Hitung ATR sederhana untuk offset panah
   double currentAtr = (rates[1].high - rates[1].low);
   if(currentAtr <= 0) currentAtr = 1.0 * _Point;

   // Deteksi sinyal konfirmasi retest pada Bar 1 (Closed bar non-repainting)
   SMC_OrderBlock obTarget;
   int bar1_idx = rates_total - 2;

   // 1. Sinyal BUY: Retest ke Bullish OB + Rejection Bullish Candle
   if(smcEngine.IsRetestingBullishOB(rates[1].low, obTarget))
     {
      if(rates[1].close > rates[1].open)
        {
         BufferBuySignal[bar1_idx] = rates[1].low - (currentAtr * 0.5);
         lastDetectedSignal = "BUY CONFIRMED (OB Retest)";
         lastSignalColor    = clrAqua;

         if(rates[1].time != lastAlertBarTime && prev_calculated > 0)
           {
            lastAlertBarTime = rates[1].time;
            if(InpPopupAlert) Alert(StringFormat("[SMC BUY] %s %s: Retest Bullish Order Block di %.2f", _Symbol, GetTfShortName(_Period), rates[1].close));
            if(InpPushNotification) SendNotification(StringFormat("SMC BUY ALERT: %s %s @ %.2f", _Symbol, GetTfShortName(_Period), rates[1].close));
            if(InpSoundAlert && InpSoundFile != "") PlaySound(InpSoundFile);
           }
        }
     }
   // 2. Sinyal SELL: Retest ke Bearish OB + Rejection Bearish Candle
   else if(smcEngine.IsRetestingBearishOB(rates[1].high, obTarget))
     {
      if(rates[1].close < rates[1].open)
        {
         BufferSellSignal[bar1_idx] = rates[1].high + (currentAtr * 0.5);
         lastDetectedSignal = "SELL CONFIRMED (OB Retest)";
         lastSignalColor    = clrMagenta;

         if(rates[1].time != lastAlertBarTime && prev_calculated > 0)
           {
            lastAlertBarTime = rates[1].time;
            if(InpPopupAlert) Alert(StringFormat("[SMC SELL] %s %s: Retest Bearish Order Block di %.2f", _Symbol, GetTfShortName(_Period), rates[1].close));
            if(InpPushNotification) SendNotification(StringFormat("SMC SELL ALERT: %s %s @ %.2f", _Symbol, GetTfShortName(_Period), rates[1].close));
            if(InpSoundAlert && InpSoundFile != "") PlaySound(InpSoundFile);
           }
        }
     }

   // 1. Gambar Garis Support & Resistance (Major & Minor)
   RenderSRLines(rates, copied);

   // 2. Gambar Auto Fibonacci Golden Zone (0.50 - 0.65 OTE)
   RenderFibonacciGoldenZone(rates, copied);

   // 3. Gambar Garis Struktur Pasar (BOS & CHoCH)
   RenderStructureVisuals(rates, copied);

   // 4. Gambar Kotak Zona Order Block & FVG
   RenderSMCVisuals(rates, copied);

   // 5. Gambar HUD Dashboard
   if(InpShowDashboard)
     {
      DrawDashboard(rates, currentAtr);
     }

   return(rates_total);
  }
