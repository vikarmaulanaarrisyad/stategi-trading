//+------------------------------------------------------------------+
//|                                  SMC_OrderBlock_Indicator.mq5   |
//|                 Smart Money Concepts (OB, FVG, BOS & CHoCH)      |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.10"
#property description "SMC Visual Indicator: Order Block (OB), Fair Value Gap (FVG), BOS & CHoCH Structure Shift dengan HUD Dashboard"

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

// Include modul SMC
#include "..\Include\SMC_Core.mqh"

//+------------------------------------------------------------------+
//| Parameter Input                                                  |
//+------------------------------------------------------------------+
input group "=== Parameter Deteksi Smart Money Concepts ==="
input int                  InpSwingLookback        = 3;             // Fractal Swing Lookback (Bars)
input int                  InpMaxZones             = 8;             // Maksimal Zona OB & FVG Aktif
input double               InpMinFvgPoints         = 30.0;          // Ukuran Minimal FVG (Points)
input double               InpMinObPoints          = 20.0;          // Ukuran Minimal Order Block (Points)
input bool                 InpShowOrderBlocks      = true;          // Gambar Kotak Order Block (OB) di Chart
input bool                 InpShowFVG              = true;          // Gambar Kotak Fair Value Gap (FVG)
input bool                 InpShowMitigatedZones   = true;          // Tampilkan Zona yang Sudah Termitigasi (Muted)

input group "=== Kustomisasi Warna Zona Visual ==="
input color                InpColorBullishOB       = C'30,70,140';  // Warna Bullish Order Block (Demand)
input color                InpColorBearishOB       = C'140,40,50';  // Warna Bearish Order Block (Supply)
input color                InpColorBullishFVG      = C'20,110,90';  // Warna Bullish FVG
input color                InpColorBearishFVG      = C'130,50,110'; // Warna Bearish FVG

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

// Objek Mesin SMC
CSMCCore smcEngine;

// Status Terakhir untuk Dashboard
datetime lastAlertBarTime    = 0;
string   lastDetectedSignal  = "Waiting for Retest";
color    lastSignalColor     = C'180,185,195';

#define PREFIX_SMC "SMC_DASH_"
#define PREFIX_OB  "SMC_OB_"
#define PREFIX_FVG "SMC_FVG_"
#define PREFIX_STR "SMC_STR_"

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
//| Helper Menggambar Kotak Zona di Chart (OB / FVG)                 |
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

   IndicatorSetString(INDICATOR_SHORTNAME, "SMC Order Block & FVG System");
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits);

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Custom indicator deinitialization function                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   ObjectsDeleteAll(0, PREFIX_SMC);
   ObjectsDeleteAll(0, PREFIX_OB);
   ObjectsDeleteAll(0, PREFIX_FVG);
   ObjectsDeleteAll(0, PREFIX_STR);
  }

//+------------------------------------------------------------------+
//| Menggambar Garis & Kotak Zona SMC pada Chart                     |
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
//| Menggambar HUD Dashboard Elegan & Rapi                           |
//+------------------------------------------------------------------+
void DrawDashboard(const MqlRates &rates[], double currentAtr)
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
   CreateLabel("TITLE", x + 14, y_title, "SMART MONEY CONCEPTS", clrGold, 9, true, corner);
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

   CreateLabel("L_STRUCT", x + 14, lineY, "SMC Structure:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STRUCT", x_val, lineY, stText, stColor, 9, true, corner);

   // Baris 2: Order Block Bullish Terdekat (Unmitigated)
   lineY += stepY;
   string obBullText = "None Active";
   color  obBullColor = C'140,150,165';
   int obTotal = smcEngine.GetOrderBlocksTotal();
   for(int i = 0; i < obTotal; i++)
     {
      SMC_OrderBlock ob;
      if(smcEngine.GetOrderBlock(i, ob))
        {
         if(ob.isBullish && !ob.isMitigated && !ob.isInvalidated)
           {
            obBullText = StringFormat("Active: %.2f - %.2f", ob.low, ob.high);
            obBullColor = clrAqua;
            break;
           }
        }
     }
   CreateLabel("L_OB_BULL", x + 14, lineY, "Bullish OB Zone:", C'180,185,195', 9, false, corner);
   CreateLabel("V_OB_BULL", x_val, lineY, obBullText, obBullColor, 9, true, corner);

   // Baris 3: Order Block Bearish Terdekat (Unmitigated)
   lineY += stepY;
   string obBearText = "None Active";
   color  obBearColor = C'140,150,165';
   for(int i = 0; i < obTotal; i++)
     {
      SMC_OrderBlock ob;
      if(smcEngine.GetOrderBlock(i, ob))
        {
         if(!ob.isBullish && !ob.isMitigated && !ob.isInvalidated)
           {
            obBearText = StringFormat("Active: %.2f - %.2f", ob.low, ob.high);
            obBearColor = clrSalmon;
            break;
           }
        }
     }
   CreateLabel("L_OB_BEAR", x + 14, lineY, "Bearish OB Zone:", C'180,185,195', 9, false, corner);
   CreateLabel("V_OB_BEAR", x_val, lineY, obBearText, obBearColor, 9, true, corner);

   // Baris 4: FVG Imbalance Terdekat
   lineY += stepY;
   string fvgText = "No Imbalance";
   color  fvgColor = C'140,150,165';
   int fvgTotal = smcEngine.GetFvgsTotal();
   for(int i = 0; i < fvgTotal; i++)
     {
      SMC_FairValueGap fvg;
      if(smcEngine.GetFvg(i, fvg))
        {
         if(!fvg.isMitigated)
           {
            fvgText = StringFormat("%s Gap: %.2f - %.2f", fvg.isBullish ? "Bullish" : "Bearish", fvg.bottom, fvg.top);
            fvgColor = fvg.isBullish ? clrMediumSeaGreen : clrHotPink;
            break;
           }
        }
     }
   CreateLabel("L_FVG", x + 14, lineY, "Nearest FVG:", C'180,185,195', 9, false, corner);
   CreateLabel("V_FVG", x_val, lineY, fvgText, fvgColor, 9, true, corner);

   // Baris 5: Status Harga Terhadap Zona (Bar 0 Live)
   lineY += stepY;
   string retestText = "Price in Free Zone";
   color  retestColor = C'170,180,195';
   SMC_OrderBlock activeOB;
   SMC_FairValueGap activeFVG;

   if(smcEngine.IsRetestingBullishOB(rates[0].close, activeOB))
     {
      retestText = "RETESTING Bullish OB (Buy Area)";
      retestColor = clrAqua;
     }
   else if(smcEngine.IsRetestingBearishOB(rates[0].close, activeOB))
     {
      retestText = "RETESTING Bearish OB (Sell Area)";
      retestColor = clrMagenta;
     }
   else if(smcEngine.IsRetestingBullishFVG(rates[0].close, activeFVG))
     {
      retestText = "FILLING Bullish FVG Imbalance";
      retestColor = clrLime;
     }
   else if(smcEngine.IsRetestingBearishFVG(rates[0].close, activeFVG))
     {
      retestText = "FILLING Bearish FVG Imbalance";
      retestColor = clrOrangeRed;
     }

   CreateLabel("L_PRICE", x + 14, lineY, "Price Status:", C'180,185,195', 9, false, corner);
   CreateLabel("V_PRICE", x_val, lineY, retestText, retestColor, 8, true, corner);

   // Baris 6: Sinyal Terakhir
   lineY += stepY;
   CreateLabel("L_SIGNAL", x + 14, lineY, "Trade Signal:", C'180,185,195', 9, false, corner);
   CreateLabel("V_SIGNAL", x_val, lineY, lastDetectedSignal, lastSignalColor, 9, true, corner);

   // Baris 7: Filter Status
   lineY += stepY;
   CreateLabel("L_STATUS", x + 14, lineY, "System Status:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STATUS", x_val, lineY, "SMC Engine Active", clrLime, 8, true, corner);

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
         lastDetectedSignal = "BUY CONFIRMED (OB Rejection)";
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
         lastDetectedSignal = "SELL CONFIRMED (OB Rejection)";
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

   // Gambar kotak visual zona SMC di chart
   RenderSMCVisuals(rates, copied);

   // Gambar HUD Dashboard
   if(InpShowDashboard)
     {
      DrawDashboard(rates, currentAtr);
     }

   return(rates_total);
  }
