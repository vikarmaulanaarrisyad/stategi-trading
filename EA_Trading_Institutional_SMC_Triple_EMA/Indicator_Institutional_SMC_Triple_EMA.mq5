//+------------------------------------------------------------------+
//|                         Indicator_Institutional_SMC_Triple_EMA.mq5|
//|                 Copyright 2026, Institutional SMC & Triple EMA   |
//|                                      https://www.tradingview.com |
//+------------------------------------------------------------------+
#property copyright "Institutional SMC & Triple EMA Master"
#property link      "https://www.tradingview.com"
#property version   "1.00"
#property description "Indikator Visual MT5: Triple EMA (8, 21, 125) + 9 Pola Candlestick + Dashboard HUD & Sinyal"
#property indicator_chart_window
#property indicator_buffers 7
#property indicator_plots   5

//--- Plot 1: Fast EMA 8
#property indicator_label1  "Fast EMA (8)"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrCyan
#property indicator_style1  STYLE_SOLID
#property indicator_width1  1

//--- Plot 2: Medium EMA 21
#property indicator_label2  "Medium EMA (21)"
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrGold
#property indicator_style2  STYLE_SOLID
#property indicator_width2  2

//--- Plot 3: Trend EMA 125
#property indicator_label3  "Trend Baseline EMA (125)"
#property indicator_type3   DRAW_LINE
#property indicator_color3  clrDarkViolet
#property indicator_style3  STYLE_SOLID
#property indicator_width3  3

//--- Plot 4: Sinyal BUY
#property indicator_label4  "Triple EMA BUY"
#property indicator_type4   DRAW_ARROW
#property indicator_color4  clrMediumSpringGreen
#property indicator_width4  2

//--- Plot 5: Sinyal SELL
#property indicator_label5  "Triple EMA SELL"
#property indicator_type5   DRAW_ARROW
#property indicator_color5  clrCrimson
#property indicator_width5  2

//+------------------------------------------------------------------+
//| INPUT PARAMETERS USER                                            |
//+------------------------------------------------------------------+
input group "=== 1. PENGATURAN TRIPLE EMA ==="
input bool   InpShowEMA8           = true;   // Tampilkan Fast EMA 8
input int    InpFastEMAPeriod      = 8;      // Periode Fast EMA
input bool   InpShowEMA21          = true;   // Tampilkan Medium EMA 21
input int    InpMediumEMAPeriod    = 21;     // Periode Medium EMA
input bool   InpShowEMA125         = true;   // Tampilkan Trend Baseline EMA 125
input int    InpTrendEMAPeriod     = 125;    // Periode Trend EMA
input int    InpPullbackLookback   = 3;      // Jendela Memori Pullback (Lilin)

input group "=== 2. TAMPILAN SINYAL DI CHART ==="
input bool   InpShowSignals        = false;  // Tampilkan Panah Sinyal di Chart (Hidden by Default)
input bool   InpShowBuyArrow       = true;   // Tampilkan Panah BUY
input bool   InpShowSellArrow      = true;   // Tampilkan Panah SELL

input group "=== 3. HUD DASHBOARD ON-CHART ==="
input bool   InpShowDashboard      = true;   // Tampilkan Tabel HUD Dashboard
input ENUM_BASE_CORNER InpDashCorner = CORNER_LEFT_UPPER; // Posisi Dashboard
input int    InpDashX              = 20;     // Jarak X (Pixels)
input int    InpDashY              = 30;     // Jarak Y (Pixels)

input group "=== 4. FILTER KEAMANAN (ANTI-FALSE SIGNAL) ==="
input bool   InpFilterChop         = true;   // Filter EMA 8-21 Sideways / Cross Bolak-Balik
input bool   InpFilterWhipsaw125   = true;   // Filter Whipsaw Lilin Bolak-Balik EMA 125
input bool   InpFilterOverextended = true;   // Filter Lilin Terlalu Jauh dari EMA
input double InpMaxAtrExtMult      = 2.2;    // Batas Toleransi Jarak Lilin ke EMA (x ATR)
input bool   InpFilterStructure    = true;   // Filter Struktur Market (HH-HL / LH-LL)

input group "=== 5. TOGGLE 9 POLA CANDLESTICK ==="
input bool   InpUseHammerShootingStar = true; // 1. Hammer & Shooting Star
input bool   InpUsePinBar             = true; // 2. Pin Bar Bullish & Bearish
input bool   InpUseEngulfing          = true; // 3. Bullish & Bearish Engulfing
input bool   InpUseMorningEveningStar = true; // 4. Morning Star & Evening Star
input bool   InpUsePiercingDarkCloud  = true; // 5. Piercing Line & Dark Cloud Cover
input bool   InpUseThreeSoldiersCrows = true; // 6. Three White Soldiers & Black Crows
input bool   InpUseDojiRejection      = true; // 7. Doji Rejection Bullish & Bearish
input bool   InpUseInsideBar          = true; // 8. Inside Bar Breakout & Breakdown
input bool   InpUseTwoCandleRejection = true; // 9. Two Candle Rejection Bullish & Bearish

//+------------------------------------------------------------------+
//| BUFFER INDIKATOR                                                 |
//+------------------------------------------------------------------+
double BufEMA8[];
double BufEMA21[];
double BufEMA125[];
double BufBuyArrow[];
double BufSellArrow[];
double BufATR[];
double BufTrueRange[];

// Prefiks objek UI dashboard
#define PREFIX_HUD "SMC_TRIPLE_EMA_HUD_"

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU PENGELOLA OBJEK UI DASHBOARD                     |
//+------------------------------------------------------------------+
void CreateLabel(string name, string text, int x, int y, color clr, int fontSize = 9, bool isBold = false)
{
   string objName = PREFIX_HUD + name;
   if (ObjectFind(0, objName) < 0)
   {
      ObjectCreate(0, objName, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, objName, OBJPROP_CORNER, InpDashCorner);
      ObjectSetInteger(0, objName, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, objName, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, objName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, objName, OBJPROP_HIDDEN, true);
   }
   ObjectSetString(0, objName, OBJPROP_TEXT, text);
   ObjectSetInteger(0, objName, OBJPROP_COLOR, clr);
   ObjectSetString(0, objName, OBJPROP_FONT, isBold ? "Segoe UI Bold" : "Segoe UI");
   ObjectSetInteger(0, objName, OBJPROP_FONTSIZE, fontSize);
}

void CreateBackgroundBox(int width, int height)
{
   string objName = PREFIX_HUD + "BG";
   if (ObjectFind(0, objName) < 0)
   {
      ObjectCreate(0, objName, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, objName, OBJPROP_CORNER, InpDashCorner);
      ObjectSetInteger(0, objName, OBJPROP_XDISTANCE, InpDashX);
      ObjectSetInteger(0, objName, OBJPROP_YDISTANCE, InpDashY);
      ObjectSetInteger(0, objName, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, objName, OBJPROP_YSIZE, height);
      ObjectSetInteger(0, objName, OBJPROP_BGCOLOR, C'20,24,35');
      ObjectSetInteger(0, objName, OBJPROP_BORDER_COLOR, C'51,65,85');
      ObjectSetInteger(0, objName, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(0, objName, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, objName, OBJPROP_HIDDEN, true);
   }
}

//+------------------------------------------------------------------+
//| ONINIT: INISIALISASI BUFFER & INDIKATOR                          |
//+------------------------------------------------------------------+
int OnInit()
{
   // Pengikatan buffer indikator
   SetIndexBuffer(0, BufEMA8, INDICATOR_DATA);
   SetIndexBuffer(1, BufEMA21, INDICATOR_DATA);
   SetIndexBuffer(2, BufEMA125, INDICATOR_DATA);
   SetIndexBuffer(3, BufBuyArrow, INDICATOR_DATA);
   SetIndexBuffer(4, BufSellArrow, INDICATOR_DATA);
   SetIndexBuffer(5, BufATR, INDICATOR_CALCULATIONS);
   SetIndexBuffer(6, BufTrueRange, INDICATOR_CALCULATIONS);

   // Nilai kosong untuk panah
   PlotIndexSetDouble(3, PLOT_EMPTY_VALUE, 0.0);
   PlotIndexSetDouble(4, PLOT_EMPTY_VALUE, 0.0);

   // Tipe karakter simbol panah (Wingdings)
   PlotIndexSetInteger(3, PLOT_ARROW, 233); // Panah ke atas
   PlotIndexSetInteger(4, PLOT_ARROW, 234); // Panah ke bawah

   // Visibilitas garis
   if (!InpShowEMA8)   PlotIndexSetInteger(0, PLOT_DRAW_TYPE, DRAW_NONE);
   if (!InpShowEMA21)  PlotIndexSetInteger(1, PLOT_DRAW_TYPE, DRAW_NONE);
   if (!InpShowEMA125) PlotIndexSetInteger(2, PLOT_DRAW_TYPE, DRAW_NONE);
   if (!InpShowSignals || !InpShowBuyArrow)  PlotIndexSetInteger(3, PLOT_DRAW_TYPE, DRAW_NONE);
   if (!InpShowSignals || !InpShowSellArrow) PlotIndexSetInteger(4, PLOT_DRAW_TYPE, DRAW_NONE);

   IndicatorSetString(INDICATOR_SHORTNAME, "SMC & Triple EMA Master");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| ONDEINIT: CLEANUP UI DASHBOARD                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ObjectsDeleteAll(0, PREFIX_HUD);
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| ONCALCULATE: KALKULASI UTAMA INDIKATOR                           |
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
   if (rates_total < InpTrendEMAPeriod + 30) return 0;

   // 1. Tentukan titik awal perhitungan
   int start = (prev_calculated > 0) ? prev_calculated - 1 : 0;

   // 2. Kalkulasi True Range & ATR 14
   for (int i = start; i < rates_total; i++)
   {
      if (i == 0)
         BufTrueRange[i] = high[i] - low[i];
      else
      {
         double tr1 = high[i] - low[i];
         double tr2 = MathAbs(high[i] - close[i - 1]);
         double tr3 = MathAbs(low[i] - close[i - 1]);
         BufTrueRange[i] = MathMax(tr1, MathMax(tr2, tr3));
      }

      if (i < 14)
         BufATR[i] = BufTrueRange[i];
      else
      {
         double sumTR = 0;
         for (int k = i - 13; k <= i; k++) sumTR += BufTrueRange[k];
         BufATR[i] = sumTR / 14.0;
      }
   }

   // 3. Kalkulasi Self-Contained EMA (8, 21, 125)
   double alpha8   = 2.0 / (InpFastEMAPeriod + 1.0);
   double alpha21  = 2.0 / (InpMediumEMAPeriod + 1.0);
   double alpha125 = 2.0 / (InpTrendEMAPeriod + 1.0);

   for (int i = start; i < rates_total; i++)
   {
      if (i == 0)
      {
         BufEMA8[i]   = close[i];
         BufEMA21[i]  = close[i];
         BufEMA125[i] = close[i];
      }
      else
      {
         BufEMA8[i]   = (close[i] * alpha8)   + (BufEMA8[i - 1]   * (1.0 - alpha8));
         BufEMA21[i]  = (close[i] * alpha21)  + (BufEMA21[i - 1]  * (1.0 - alpha21));
         BufEMA125[i] = (close[i] * alpha125) + (BufEMA125[i - 1] * (1.0 - alpha125));
      }

      BufBuyArrow[i]  = 0.0;
      BufSellArrow[i] = 0.0;
   }

   // 4. Kalkulasi Sinyal S/R & Pola Candlestick (Dimulai setelah data stabil)
   int evalStart = MathMax(start, InpTrendEMAPeriod + 15);
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double minCandleSize = point * 5.0;

   // Variabel tracking status untuk Dashboard
   string lastTradeSignal = "Menunggu";
   color  lastSignalColor = C'148,163,184';
   string lastTrendStatus = "Neutral";
   color  lastTrendColor  = clrWhite;
   string lastSafetyText  = "Clear (No Warnings)";
   color  lastSafetyColor = clrMediumSpringGreen;
   double liveMajorRes    = 0.0;
   double liveMajorSup    = 0.0;

   for (int i = evalStart; i < rates_total - 1; i++) // Hanya lilin selesai (closed bar)
   {
      double o1 = open[i],  h1 = high[i],  l1 = low[i],  c1 = close[i];
      double o2 = open[i-1], h2 = high[i-1], l2 = low[i-1], c2 = close[i-1];
      double o3 = open[i-2], h3 = high[i-2], l3 = low[i-2], c3 = close[i-2];

      double range1 = h1 - l1;
      double body1  = MathAbs(c1 - o1);
      double lowerWick1 = MathMin(o1, c1) - l1;
      double upperWick1 = h1 - MathMax(o1, c1);
      bool   isGreen1   = (c1 > o1);
      bool   isRed1     = (c1 < o1);

      double range2 = h2 - l2;
      double body2  = MathAbs(c2 - o2);
      bool   isGreen2 = (c2 > o2);
      bool   isRed2   = (c2 < o2);

      double range3 = h3 - l3;
      double body3  = MathAbs(c3 - o3);
      bool   isGreen3 = (c3 > o3);
      bool   isRed3   = (c3 < o3);

      double atrVal = BufATR[i];

      // A. 9 Pola Bullish
      bool isBullHammer = (range1 >= minCandleSize) && (lowerWick1 >= 1.8 * body1) && (upperWick1 <= body1 * 0.8) && (c1 >= l1 + range1 * 0.55);
      bool isBullPin    = (range1 >= minCandleSize) && (lowerWick1 >= 0.60 * range1) && (MathMin(o1, c1) >= l1 + range1 * 0.50);
      bool isBullEngulf = (range1 >= minCandleSize) && isGreen1 && isRed2 && (c1 >= o2) && (o1 <= c2) && (body1 >= body2 * 0.95);
      bool isMorningStar = (range3 >= minCandleSize) && isRed3 && (body2 <= body3 * 0.55) && isGreen1 && (c1 >= (o3 + c3) / 2.0);
      bool isPiercing   = (range1 >= minCandleSize) && isRed2 && isGreen1 && (o1 <= c2 * 1.0005) && (c1 > (o2 + c2) / 2.0) && (c1 < o2);
      bool isThreeWhite = isGreen1 && isGreen2 && isGreen3 && (c1 > c2) && (c2 > c3) && (body1 > range1 * 0.35) && (body2 > range2 * 0.35);
      bool isBullDoji   = (range1 >= minCandleSize) && (body1 <= range1 * 0.18) && (lowerWick1 >= range1 * 0.50);
      bool isBullInside = (h2 <= h3) && (l2 >= l3) && isGreen1 && (c1 > h2);
      bool isBullTwoCandle = ((lowerWick1 >= range1 * 0.45) || (MathMin(o2, c2) - l2 >= range2 * 0.45)) && isGreen1 && (c1 > c2);

      string bullPattern = "";
      if (InpUseEngulfing && isBullEngulf)              bullPattern = "Bullish Engulfing";
      else if (InpUseMorningEveningStar && isMorningStar) bullPattern = "Morning Star";
      else if (InpUseThreeSoldiersCrows && isThreeWhite) bullPattern = "Three White Soldiers";
      else if (InpUsePiercingDarkCloud && isPiercing)    bullPattern = "Piercing Line";
      else if (InpUseHammerShootingStar && isBullHammer)  bullPattern = "Hammer";
      else if (InpUsePinBar && isBullPin)                bullPattern = "Pin Bar Bullish";
      else if (InpUseDojiRejection && isBullDoji)        bullPattern = "Doji Rejection";
      else if (InpUseInsideBar && isBullInside)          bullPattern = "Bullish Inside Bar";
      else if (InpUseTwoCandleRejection && isBullTwoCandle) bullPattern = "Two Candle Rejection";

      bool hasBull = (bullPattern != "");

      // B. 9 Pola Bearish
      bool isBearShooting = (range1 >= minCandleSize) && (upperWick1 >= 1.8 * body1) && (lowerWick1 <= body1 * 0.8) && (c1 <= h1 - range1 * 0.55);
      bool isBearPin      = (range1 >= minCandleSize) && (upperWick1 >= 0.60 * range1) && (MathMax(o1, c1) <= l1 + range1 * 0.50);
      bool isBearEngulf   = (range1 >= minCandleSize) && isRed1 && isGreen2 && (c1 <= o2) && (o1 >= c2) && (body1 >= body2 * 0.95);
      bool isEveningStar  = (range3 >= minCandleSize) && isGreen3 && (body2 <= body3 * 0.55) && isRed1 && (c1 <= (o3 + c3) / 2.0);
      bool isDarkCloud    = (range1 >= minCandleSize) && isGreen2 && isRed1 && (o1 >= c2 * 0.9995) && (c1 < (o2 + c2) / 2.0) && (c1 > o2);
      bool isThreeCrows   = isRed1 && isRed2 && isRed3 && (c1 < c2) && (c2 < c3) && (body1 > range1 * 0.35) && (body2 > range2 * 0.35);
      bool isBearDoji     = (range1 >= minCandleSize) && (body1 <= range1 * 0.18) && (upperWick1 >= range1 * 0.50);
      bool isBearInside   = (h2 <= h3) && (l2 >= l3) && isRed1 && (c1 < l2);
      bool isBearTwoCandle = ((upperWick1 >= range1 * 0.45) || (h2 - MathMax(o2, c2) >= range2 * 0.45)) && isRed1 && (c1 < c2);

      string bearPattern = "";
      if (InpUseEngulfing && isBearEngulf)              bearPattern = "Bearish Engulfing";
      else if (InpUseMorningEveningStar && isEveningStar) bearPattern = "Evening Star";
      else if (InpUseThreeSoldiersCrows && isThreeCrows) bearPattern = "Three Black Crows";
      else if (InpUsePiercingDarkCloud && isDarkCloud)   bearPattern = "Dark Cloud Cover";
      else if (InpUseHammerShootingStar && isBearShooting) bearPattern = "Shooting Star";
      else if (InpUsePinBar && isBearPin)                bearPattern = "Pin Bar Bearish";
      else if (InpUseDojiRejection && isBearDoji)        bearPattern = "Doji Rejection";
      else if (InpUseInsideBar && isBearInside)          bearPattern = "Bearish Inside Bar";
      else if (InpUseTwoCandleRejection && isBearTwoCandle) bearPattern = "Two Candle Rejection";

      bool hasBear = (bearPattern != "");

      // C. Filter Keamanan (Chop, Whipsaw, Overextended, Structure)
      int emaCrosses = 0;
      for (int k = i - 14; k <= i; k++)
      {
         if ((BufEMA8[k] > BufEMA21[k] && BufEMA8[k-1] <= BufEMA21[k-1]) || (BufEMA8[k] < BufEMA21[k] && BufEMA8[k-1] >= BufEMA21[k-1]))
            emaCrosses++;
      }
      bool isChop = (emaCrosses >= 2) || (MathAbs(BufEMA8[i] - BufEMA21[i]) < (atrVal * 0.12));

      int ema125Crosses = 0;
      for (int k = i - 19; k <= i; k++)
      {
         if ((close[k] > BufEMA125[k] && close[k-1] <= BufEMA125[k-1]) || (close[k] < BufEMA125[k] && close[k-1] >= BufEMA125[k-1]))
            ema125Crosses++;
      }
      bool isWhipsaw = (ema125Crosses >= 2);

      bool isOverBuy  = (c1 - BufEMA8[i]) > (atrVal * InpMaxAtrExtMult);
      bool isOverSell = (BufEMA8[i] - c1) > (atrVal * InpMaxAtrExtMult);

      double lowestL = l1, prevLowestL = low[i-5];
      double highestH = h1, prevHighestH = high[i-5];
      for (int k = i - 4; k <= i; k++)
      {
         if (low[k] < lowestL) lowestL = low[k];
         if (high[k] > highestH) highestH = high[k];
      }
      for (int k = i - 11; k <= i - 5; k++)
      {
         if (low[k] < prevLowestL) prevLowestL = low[k];
         if (high[k] > prevHighestH) prevHighestH = high[k];
      }
      bool isBullStruct = (lowestL >= prevLowestL);
      bool isBearStruct = (highestH <= prevHighestH);

      // D. Deteksi Pullback Jendela Memori (Lookback)
      bool buyPullback = false;
      bool sellPullback = false;
      for (int k = i; k > i - InpPullbackLookback; k--)
      {
         double topK = MathMax(BufEMA8[k], BufEMA21[k]);
         double btmK = MathMin(BufEMA8[k], BufEMA21[k]);
         if ((low[k] <= topK * 1.0015) && (MathMin(open[k], close[k]) >= BufEMA125[k]) && (low[k] >= BufEMA125[k] * 0.9980))
            buyPullback = true;
         if ((high[k] >= btmK * 0.9985) && (MathMax(open[k], close[k]) <= BufEMA125[k]) && (high[k] <= BufEMA125[k] * 1.0020))
            sellPullback = true;
      }

      // E. Sinyal Eksekusi
      bool buyValid = (c1 > BufEMA125[i]) && (BufEMA8[i] > BufEMA21[i]) && buyPullback && hasBull;
      bool buySafe  = (!InpFilterChop || !isChop) && (!InpFilterWhipsaw125 || !isWhipsaw) && (!InpFilterOverextended || !isOverBuy) && (!InpFilterStructure || isBullStruct);

      bool sellValid = (c1 < BufEMA125[i]) && (BufEMA8[i] < BufEMA21[i]) && sellPullback && hasBear;
      bool sellSafe  = (!InpFilterChop || !isChop) && (!InpFilterWhipsaw125 || !isWhipsaw) && (!InpFilterOverextended || !isOverSell) && (!InpFilterStructure || isBearStruct);

      if (buyValid && buySafe)
      {
         BufBuyArrow[i] = l1 - (atrVal * 0.4);
         lastTradeSignal = "BUY: " + bullPattern;
         lastSignalColor = clrMediumSpringGreen;
      }

      if (sellValid && sellSafe)
      {
         BufSellArrow[i] = h1 + (atrVal * 0.4);
         lastTradeSignal = "SELL: " + bearPattern;
         lastSignalColor = clrCrimson;
      }

      // Lacak status realtime lilin terkini
      if (i == rates_total - 2)
      {
         if (isChop)
         {
            lastSafetyText = "Warning: EMA Sideways";
            lastSafetyColor = clrOrange;
         }
         else if (isWhipsaw)
         {
            lastSafetyText = "Warning: Whipsaw EMA 125";
            lastSafetyColor = clrOrange;
         }
         else if (isOverBuy || isOverSell)
         {
            lastSafetyText = "Warning: Overextended";
            lastSafetyColor = clrOrange;
         }
         else
         {
            lastSafetyText = "Clear (No Warnings)";
            lastSafetyColor = clrMediumSpringGreen;
         }

         if (c1 > BufEMA125[i] && BufEMA8[i] > BufEMA21[i])
         {
            lastTrendStatus = "BULLISH (8 > 21 > 125)";
            lastTrendColor  = clrMediumSpringGreen;
         }
         else if (c1 < BufEMA125[i] && BufEMA8[i] < BufEMA21[i])
         {
            lastTrendStatus = "BEARISH (8 < 21 < 125)";
            lastTrendColor  = clrCrimson;
         }
         else
         {
            lastTrendStatus = "TRANSITION / SIDEWAYS";
            lastTrendColor  = clrGold;
         }

         // Kalkulasi level Major S/R sederhana
         liveMajorRes = high[i];
         liveMajorSup = low[i];
         for (int m = i - 15; m <= i; m++)
         {
            if (high[m] > liveMajorRes) liveMajorRes = high[m];
            if (low[m] < liveMajorSup)  liveMajorSup = low[m];
         }
      }
   }

   // 5. Render HUD Dashboard di Chart
   if (InpShowDashboard)
   {
      CreateBackgroundBox(260, 160);
      int startX = InpDashX + 12;
      int startY = InpDashY + 10;
      int rowH   = 18;

      CreateLabel("TITLE", "SMC & TRIPLE EMA MASTER", startX, startY, clrGold, 10, true);
      CreateLabel("SUB", _Symbol + " [" + EnumToString(_Period) + "]", startX + 160, startY, clrLightSkyBlue, 9, false);

      startY += 20;
      CreateLabel("L_TREND", "Triple EMA Trend:", startX, startY, clrWhite);
      CreateLabel("V_TREND", lastTrendStatus, startX + 115, startY, lastTrendColor, 9, true);

      startY += rowH;
      CreateLabel("L_RES", "Major Resistance:", startX, startY, clrWhite);
      CreateLabel("V_RES", DoubleToString(liveMajorRes, _Digits), startX + 115, startY, clrSalmon);

      startY += rowH;
      CreateLabel("L_SUP", "Major Support:", startX, startY, clrWhite);
      CreateLabel("V_SUP", DoubleToString(liveMajorSup, _Digits), startX + 115, startY, clrMediumSpringGreen);

      startY += rowH;
      CreateLabel("L_SAFE", "Market Safety:", startX, startY, clrWhite);
      CreateLabel("V_SAFE", lastSafetyText, startX + 115, startY, lastSafetyColor, 9, true);

      startY += rowH;
      CreateLabel("L_SIG", "Trade Signal:", startX, startY, clrWhite);
      CreateLabel("V_SIG", lastTradeSignal, startX + 115, startY, lastSignalColor, 9, true);
   }

   return rates_total;
}
//+------------------------------------------------------------------+
