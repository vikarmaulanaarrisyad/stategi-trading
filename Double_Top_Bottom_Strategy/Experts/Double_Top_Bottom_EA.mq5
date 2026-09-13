//+------------------------------------------------------------------+
//|                                     Double_Top_Bottom_EA.mq5     |
//|                 Double Top & Double Bottom Expert Advisor        |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright   "Copyright 2026, XAUUSD Senior Trader"
#property link        ""
#property version     "1.10"
#property description "EA Auto-Trading Pola Double Top (M) & Double Bottom (W) dengan Konfirmasi Breakout Volume Tinggi, Minimum Risk:Reward Protection, Trend Confluence, dan Risk Management Pro"

// Include pustaka standar MQL5 untuk eksekusi order
#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\AccountInfo.mqh>

// Include modul strategi
#include "..\Include\DoublePattern_Core.mqh"
#include "..\Include\DoublePattern_RiskManager.mqh"

//+------------------------------------------------------------------+
//| Enum Mode Stop Loss                                              |
//+------------------------------------------------------------------+
enum ENUM_SL_MODE
  {
   SL_PATTERN_EXTREMUM, // Level Support / Resistance Pola + Buffer
   SL_FIXED_POINTS      // Fixed Points
  };

//+------------------------------------------------------------------+
//| Enum Mode Take Profit                                            |
//+------------------------------------------------------------------+
enum ENUM_TP_MODE
  {
   TP_PATTERN_HEIGHT,   // Proyeksi Tinggi Pola (dengan jaminan min R:R)
   TP_RISK_REWARD,      // Target Rasio Risk:Reward (1:X)
   TP_FIXED_POINTS      // Fixed Points
  };

//+------------------------------------------------------------------+
//| Enum Mode Money Management                                       |
//+------------------------------------------------------------------+
enum ENUM_LOT_MODE
  {
   LOT_RISK_PERCENT,    // Dinamis Berdasarkan % Risk dari Equity
   LOT_FIXED            // Fixed Lot
  };

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

input group "=== Filter Konfluensi Tren Makro & RSI ==="
input bool                 InpUseEma200Filter      = true;          // Aktifkan Filter Tren Institusional EMA 200
input int                  InpEma200Period         = 200;           // Periode EMA 200
input bool                 InpFilterCounterTrend   = true;          // Saring Transaksi Melawan Tren Kuat (Kecuali RSI Ekstrem)
input bool                 InpUseRsiFilter         = true;          // Filter Momentum RSI
input int                  InpRsiPeriod            = 14;            // Periode RSI
input double               InpRsiExtremeBuy        = 40.0;          // Minimal RSI untuk Buy Reversal Melawan Tren
input double               InpRsiExtremeSell       = 60.0;          // Maksimal RSI untuk Sell Reversal Melawan Tren
input bool                 InpRequireStrongCandle  = true;          // Wajib Candle Breakout Searah (Bullish/Bearish Body)

input group "=== Money Management & Lot Size ==="
input ENUM_LOT_MODE        InpLotMode              = LOT_RISK_PERCENT; // Mode Kalkulasi Lot
input double               InpFixedLot             = 0.01;          // Fixed Lot Size (jika LOT_FIXED)
input double               InpRiskPercent          = 1.0;           // Resiko per Trade (% Equity)
input double               InpMaxLotSize           = 5.0;           // Maksimal Lot Eksekusi
input int                  InpMaxOpenPositions     = 1;             // Maksimal Posisi Terbuka Bersamaan

input group "=== Stop Loss & Take Profit (Minimum R:R Protection) ==="
input ENUM_SL_MODE         InpSLMode               = SL_PATTERN_EXTREMUM; // Mode Stop Loss
input int                  InpSL_BufferPoints      = 50;            // Buffer Tambahan SL di luar Support/Resistance (Points)
input int                  InpMinSLPoints          = 150;           // Batas Minimal SL Points (Proteksi Broker Gold)
input int                  InpMaxSLPoints          = 600;           // Batas Maksimal SL Points
input ENUM_TP_MODE         InpTPMode               = TP_PATTERN_HEIGHT;   // Mode Take Profit
input double               InpMinRiskRewardRatio   = 1.4;           // Minimal Rasio Risk:Reward (Kunci Profit Factor > 1.5)
input double               InpRiskRewardRatio      = 1.5;           // Target Risk:Reward (jika TP_RISK_REWARD)
input int                  InpTP_FixedPoints       = 300;           // Fixed TP Points (jika TP_FIXED_POINTS)

input group "=== Proteksi Profit: Break-Even & Trailing ==="
input bool                 InpUseBreakEven         = true;          // Aktifkan Auto Break-Even (BEP)
input double               InpBE_TriggerRR         = 1.0;           // Pindahkan SL ke BEP saat Profit mencapai 1:X R:R
input int                  InpBE_LockProfitPoints  = 20;            // Profit Terkunci di atas Entry (Points)
input bool                 InpUseTrailingStop      = true;          // Aktifkan Trailing Stop
input double               InpTrailingStartRR      = 1.2;           // Trailing Stop Mulai Aktif pada Profit 1:X R:R
input int                  InpTrailingDistancePoints = 120;         // Jarak Trailing Stop (Points)
input int                  InpTrailingStepPoints   = 20;            // Step Pembaruan Trailing (Points)

input group "=== Proteksi Kerugian Harian (Circuit Breaker) ==="
input bool                 InpUseDailyLossLimit    = true;          // Batasi Kerugian Harian (Stop Trading Hari Ini)
input int                  InpMaxDailyLosses       = 2;             // Maksimal Trade Kalah per Hari
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

input group "=== Visual Dashboard HUD di Chart ==="
input bool                 InpShowDashboard        = true;          // Tampilkan HUD Dashboard di Chart
input ENUM_BASE_CORNER     InpDashboardCorner      = CORNER_LEFT_LOWER; // Letak Sudut Dashboard
input int                  InpDashboardX           = 20;            // Posisi X Dashboard (Pixel)
input int                  InpDashboardY           = 25;            // Posisi Y Dashboard (Pixel)

input group "=== Kecepatan Simulasi Visual Mode ==="
input int                  InpVisualDelayMs        = 0;             // Delay Visual Per Tick/Bar (ms, 0=Normal, 50-100ms=Santai)

input group "=== EA System ID ==="
input ulong                InpMagicNumber          = 770022;        // Magic Number Unik EA Double Pattern
input string               InpOrderComment         = "DoublePat_EA"; // Komentar Order

//+------------------------------------------------------------------+
//| Objek Trading & Indikator                                        |
//+------------------------------------------------------------------+
CTrade                    trade;
CPositionInfo             positionInfo;
CAccountInfo              accountInfo;

CDoublePatternCore        patternEngine;
CDoublePatternRiskManager riskManager;

int                       handleEma200      = INVALID_HANDLE;
int                       handleRsi         = INVALID_HANDLE;
datetime                  lastTradeBarTime  = 0;
string                    lastTradeStatus   = "Waiting for Setup";
color                     lastStatusColor   = C'180,185,195';

#define PREFIX_DASH_EA "DBL_EA_DASH_"

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
   string objName = PREFIX_DASH_EA + name;
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
   string objName = PREFIX_DASH_EA + name;
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
//| Hapus Semua Objek Dashboard EA                                   |
//+------------------------------------------------------------------+
void RemoveDashboard()
  {
   ObjectsDeleteAll(0, PREFIX_DASH_EA);
  }

//+------------------------------------------------------------------+
//| Hitung Posisi Terbuka EA                                         |
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
//| Hitung Floating Profit EA                                        |
//+------------------------------------------------------------------+
double GetFloatingProfit()
  {
   double profit = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(positionInfo.SelectByIndex(i))
        {
         if(positionInfo.Symbol() == _Symbol && positionInfo.Magic() == InpMagicNumber)
           {
            profit += positionInfo.Profit() + positionInfo.Swap();
           }
        }
     }
   return profit;
  }

//+------------------------------------------------------------------+
//| Render HUD Dashboard EA                                          |
//+------------------------------------------------------------------+
void UpdateDashboard()
  {
   if(!InpShowDashboard) return;

   int width  = 430;
   int height = 232;
   int x      = InpDashboardX;
   int y      = InpDashboardY;
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
   CreateLabel("TITLE", x + 14, y_title, "DOUBLE TOP & BOTTOM EA PRO", clrGold, 9, true, corner);
   string symTfText = StringFormat("[%s | %s | Spr: %d]", _Symbol, GetTfShortName(_Period), liveSpread);
   CreateLabel("SUBTITLE", x + 250, y_sub, symTfText, (liveSpread <= InpMaxSpreadPoints) ? clrDeepSkyBlue : clrTomato, 8, false, corner);

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

   // Baris 3: Rasio Volume Lilin Breakout
   lineY += stepY;
   string volText = "Standard Volume";
   color  volColor = C'170,180,195';
   if(pat.volumeRatio > 0.0)
     {
      volText = StringFormat("%.2fx SMA (%s)", pat.volumeRatio, (pat.volumeRatio >= InpMinVolumeMultiplier ? "High Vol Confirmed" : "Low Vol"));
      volColor = (pat.volumeRatio >= InpMinVolumeMultiplier) ? clrLime : clrTomato;
     }
   CreateLabel("L_VOL", x + 14, lineY, "Breakout Volume:", C'180,185,195', 9, false, corner);
   CreateLabel("V_VOL", x_val, lineY, volText, volColor, 8, true, corner);

   // Baris 4: Posisi Aktif & Floating Profit
   lineY += stepY;
   int openCount = CountOpenPositions();
   double floatPnl = GetFloatingProfit();
   string posText = StringFormat("%d Posisi | Float: $%.2f", openCount, floatPnl);
   color  posColor = (openCount == 0) ? C'140,150,165' : (floatPnl >= 0 ? clrLime : clrTomato);
   CreateLabel("L_POS", x + 14, lineY, "Open Position:", C'180,185,195', 9, false, corner);
   CreateLabel("V_POS", x_val, lineY, posText, posColor, 9, true, corner);

   // Baris 5: Status Eksekusi Terakhir
   lineY += stepY;
   CreateLabel("L_STAT", x + 14, lineY, "Trade Action:", C'180,185,195', 9, false, corner);
   CreateLabel("V_STAT", x_val, lineY, lastTradeStatus, lastStatusColor, 9, true, corner);

   // Baris 6: Proteksi Kerugian Harian (Circuit Breaker)
   lineY += stepY;
   bool cbActive = riskManager.IsDailyLossLimitReached(InpMagicNumber, _Symbol, accountInfo.Equity(),
                                                       InpUseDailyLossLimit, InpMaxDailyLosses, InpMaxDailyLossPercent);
   string cbText = cbActive ? "CIRCUIT BREAKER ACTIVE (Stopped)" : "Normal / Active";
   color  cbColor = cbActive ? clrTomato : clrLime;
   CreateLabel("L_CB", x + 14, lineY, "Circuit Breaker:", C'180,185,195', 9, false, corner);
   CreateLabel("V_CB", x_val, lineY, cbText, cbColor, 8, true, corner);

   // Baris 7: Akun & Equity
   lineY += stepY;
   string eqText = StringFormat("$%.2f (Bal: $%.2f)", accountInfo.Equity(), accountInfo.Balance());
   CreateLabel("L_EQ", x + 14, lineY, "Equity / Balance:", C'180,185,195', 9, false, corner);
   CreateLabel("V_EQ", x_val, lineY, eqText, clrWhite, 8, false, corner);

   // Garis Pembatas & Footer
   CreatePanel("DIVIDER", x + 12, y_div, width - 24, 1, C'42,54,75', C'42,54,75', corner);

   MqlDateTime dt;
   TimeCurrent(dt);
   string sessionName = "Asian Session";
   if(dt.hour >= 8 && dt.hour < 13) sessionName = "London Session (Active)";
   else if(dt.hour >= 13 && dt.hour < 17) sessionName = "London-NY Overlap (Peak)";
   else if(dt.hour >= 17 && dt.hour < 22) sessionName = "New York Session (Active)";
   else sessionName = "Asian / Rollover (Quiet)";

   string footerText = StringFormat("● Sesi: %s | Mode: Auto-Execution", sessionName);
   CreateLabel("FOOTER", x + 14, y_foot, footerText, C'145,160,185', 8, false, corner);
  }

//+------------------------------------------------------------------+
//| Cek Filter Jam Trading                                           |
//+------------------------------------------------------------------+
bool IsTradingTimeAllowed()
  {
   if(!InpUseTimeFilter) return true;

   MqlDateTime dt;
   TimeCurrent(dt);

   if(InpStartHour <= InpEndHour)
     {
      return (dt.hour >= InpStartHour && dt.hour < InpEndHour);
     }
   else
     {
      // Jam melintasi tengah malam
      return (dt.hour >= InpStartHour || dt.hour < InpEndHour);
     }
  }

//+------------------------------------------------------------------+
//| Kelola Posisi Terbuka: Auto Break-Even (BEP) & Trailing Stop     |
//+------------------------------------------------------------------+
void ManageOpenPositions()
  {
   long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   long currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   double minDist = MathMax((double)InpMinSLPoints, (double)(stopsLevel + currentSpread + 10)) * _Point;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(!positionInfo.SelectByIndex(i)) continue;
      if(positionInfo.Symbol() != _Symbol || positionInfo.Magic() != InpMagicNumber) continue;

      ulong ticket = positionInfo.Ticket();
      ENUM_POSITION_TYPE posType = positionInfo.PositionType();
      double openPrice    = positionInfo.PriceOpen();
      double currentSL    = positionInfo.StopLoss();
      double currentTP    = positionInfo.TakeProfit();
      double currentPrice = positionInfo.PriceCurrent();

      double initialSLDistance = MathAbs(openPrice - currentSL);
      if(initialSLDistance <= 0.0)
        {
         initialSLDistance = InpMinSLPoints * _Point;
        }

      double profitPoints = (posType == POSITION_TYPE_BUY) ? (currentPrice - openPrice) : (openPrice - currentPrice);
      double currentR     = (initialSLDistance > 0.0) ? (profitPoints / initialSLDistance) : 0.0;

      // 1. AUTO BREAK-EVEN (BEP)
      if(InpUseBreakEven && currentR >= InpBE_TriggerRR)
        {
         if(posType == POSITION_TYPE_BUY && (currentSL < openPrice || currentSL == 0.0))
           {
            double newSL = NormalizeDouble(openPrice + (InpBE_LockProfitPoints * _Point), _Digits);
            if((currentPrice - newSL) >= minDist)
              {
               if(trade.PositionModify(ticket, newSL, currentTP))
                 {
                  Print(StringFormat("[DoublePattern Auto BEP] Buy Order #%I64u SL dipindahkan ke Break-Even: %.2f", ticket, newSL));
                 }
               continue;
              }
           }
         else if(posType == POSITION_TYPE_SELL && (currentSL > openPrice || currentSL == 0.0))
           {
            double newSL = NormalizeDouble(openPrice - (InpBE_LockProfitPoints * _Point), _Digits);
            if((newSL - currentPrice) >= minDist)
              {
               if(trade.PositionModify(ticket, newSL, currentTP))
                 {
                  Print(StringFormat("[DoublePattern Auto BEP] Sell Order #%I64u SL dipindahkan ke Break-Even: %.2f", ticket, newSL));
                 }
               continue;
              }
           }
        }

      // 2. TRAILING STOP
      if(InpUseTrailingStop && currentR >= InpTrailingStartRR)
        {
         if(posType == POSITION_TYPE_BUY)
           {
            double trailDist = MathMax((double)InpTrailingDistancePoints * _Point, initialSLDistance * 0.6);
            double targetTrailSL = currentPrice - trailDist;

            if(targetTrailSL > openPrice && targetTrailSL > currentSL + (InpTrailingStepPoints * _Point) && (currentPrice - targetTrailSL) >= minDist)
              {
               if(trade.PositionModify(ticket, NormalizeDouble(targetTrailSL, _Digits), currentTP))
                 {
                  Print(StringFormat("[DoublePattern Trailing Stop] Buy Order #%I64u trailing SL diperbarui: %.2f", ticket, targetTrailSL));
                 }
              }
           }
         else if(posType == POSITION_TYPE_SELL)
           {
            double trailDist = MathMax((double)InpTrailingDistancePoints * _Point, initialSLDistance * 0.6);
            double targetTrailSL = currentPrice + trailDist;

            if(targetTrailSL < openPrice && (currentSL == 0.0 || targetTrailSL < currentSL - (InpTrailingStepPoints * _Point)) && (targetTrailSL - currentPrice) >= minDist)
              {
               if(trade.PositionModify(ticket, NormalizeDouble(targetTrailSL, _Digits), currentTP))
                 {
                  Print(StringFormat("[DoublePattern Trailing Stop] Sell Order #%I64u trailing SL diperbarui: %.2f", ticket, targetTrailSL));
                 }
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetDeviationInPoints(20);

   patternEngine.Configure(InpSwingLookback, InpMinBarsBetween, InpMaxBarsBetween,
                           InpTolerancePct, InpMinHeightPoints, InpMinVolumeMultiplier, InpVolumePeriod);

   if(InpUseEma200Filter)
     {
      handleEma200 = iMA(_Symbol, _Period, InpEma200Period, 0, MODE_EMA, PRICE_CLOSE);
      if(handleEma200 == INVALID_HANDLE)
        {
         Print("[DoublePattern EA Error] Gagal membuat handle EMA 200!");
         return(INIT_FAILED);
        }
     }

   if(InpUseRsiFilter)
     {
      handleRsi = iRSI(_Symbol, _Period, InpRsiPeriod, PRICE_CLOSE);
      if(handleRsi == INVALID_HANDLE)
        {
         Print("[DoublePattern EA Error] Gagal membuat handle RSI!");
         return(INIT_FAILED);
        }
     }

   UpdateDashboard();
   Print("[DoublePattern EA] Inisialisasi Berhasil v1.10. Dual engine W & M aktif dengan Minimum R:R protection.");
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(handleEma200 != INVALID_HANDLE) IndicatorRelease(handleEma200);
   if(handleRsi != INVALID_HANDLE) IndicatorRelease(handleRsi);
   RemoveDashboard();
   Print("[DoublePattern EA] Deinitialisasi Selesai. Reason: ", reason);
  }

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(_Symbol, _Period, 0, MathMin(InpMaxBarsBetween + 60, 300), rates);
   if(copied < 40) return;

   // Delay visual mode untuk kenyamanan pengamatan
   if(MQLInfoInteger(MQL_VISUAL_MODE) && InpVisualDelayMs > 0)
     {
      Sleep(InpVisualDelayMs);
     }

   // Update HUD Dashboard
   UpdateDashboard();

   // Kelola posisi aktif (Auto BEP & Trailing Stop) setiap tick
   ManageOpenPositions();

   // Proteksi Gap Akhir Pekan: Tutup posisi otomatis Jumat malam
   riskManager.CheckFridayAutoClose(trade, positionInfo, InpMagicNumber, _Symbol,
                                    InpUseFridayClose, InpFridayCloseHour, InpFridayCloseMinute);

   // Update mesin pola (independen W dan M)
   patternEngine.Update(rates, copied);

   // Cek apakah ada candle baru (Eksekusi hanya sekali saat candle baru buka)
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

   // Cek filter jam trading
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

   // Cek batasan spread broker
   long currentSpread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(currentSpread > InpMaxSpreadPoints)
     {
      return;
     }

   // Baca EMA 200
   double ema200Val = 0.0;
   if(InpUseEma200Filter && handleEma200 != INVALID_HANDLE)
     {
      double emaBuf[];
      ArraySetAsSeries(emaBuf, true);
      if(CopyBuffer(handleEma200, 0, 1, 1, emaBuf) > 0)
        {
         ema200Val = emaBuf[0];
        }
     }

   // Filter RSI jika diaktifkan
   double rsiVal = 50.0;
   if(InpUseRsiFilter && handleRsi != INVALID_HANDLE)
     {
      double rsiBuf[];
      ArraySetAsSeries(rsiBuf, true);
      if(CopyBuffer(handleRsi, 0, 1, 1, rsiBuf) > 0)
        {
         rsiVal = rsiBuf[0];
        }
     }

   long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   double minAllowedDist = MathMax((double)InpMinSLPoints, (double)(stopsLevel + currentSpread + 10)) * _Point;

   DoublePatternInfo pat;

   // =======================================================
   // EKSEKUSI SINYAL BUY (Double Bottom "W" Neckline Breakout)
   // =======================================================
   if(patternEngine.IsDoubleBottomBreakout(rates, pat))
     {
      bool strongCandleOk = (!InpRequireStrongCandle || (rates[1].close > rates[1].open));
      
      // Filter Tren: jika harga di bawah EMA 200 (counter-trend buy), wajib RSI oversold atau counter-trend filter off
      bool trendOk = true;
      if(InpUseEma200Filter && ema200Val > 0.0)
        {
         if(rates[1].close < ema200Val) // Counter-trend buy
           {
            if(InpFilterCounterTrend && rsiVal > InpRsiExtremeBuy)
              {
               trendOk = false;
               Print(StringFormat("[Double Bottom Filtered] Harga di bawah EMA 200 & RSI belum oversold (%.1f > %.1f).", rsiVal, InpRsiExtremeBuy));
              }
           }
        }

      if(!strongCandleOk)
        {
         Print("[Double Bottom Filtered] Candle breakout bukan candle bullish solid.");
        }
      else if(!trendOk)
        {
         Print("[Double Bottom Filtered] Trend filter memblokir transaksi Buy berisiko.");
        }
      else
        {
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

         // SL ditempatkan di bawah level support (terendah dari Lembah 1 dan Lembah 2)
         double supportLevel = MathMin(pat.p1, pat.p2);
         double slPrice = (InpSLMode == SL_PATTERN_EXTREMUM) ? (supportLevel - (InpSL_BufferPoints * _Point)) :
                                                               (ask - (InpMinSLPoints * _Point));

         // Enforce perlindungan broker: untuk BUY, SL dibandingkan dengan harga BID
         if((bid - slPrice) < minAllowedDist)
           {
            slPrice = bid - minAllowedDist;
           }

         double slDistPoints = (ask - slPrice) / _Point;
         if(slDistPoints > InpMaxSLPoints)
           {
            slPrice = ask - (InpMaxSLPoints * _Point);
            slDistPoints = InpMaxSLPoints;
           }

         // Hitung Target Take Profit dengan perlindungan MINIMUM RISK:REWARD (>= InpMinRiskRewardRatio)
         double tpPrice = 0.0;
         double minTargetPoints = slDistPoints * InpMinRiskRewardRatio;

         if(InpTPMode == TP_PATTERN_HEIGHT)
           {
            double heightPoints = pat.patternHeight / _Point;
            double effectivePoints = MathMax(heightPoints, minTargetPoints);
            tpPrice = ask + (effectivePoints * _Point);
           }
         else if(InpTPMode == TP_RISK_REWARD)
           {
            double effectiveRR = MathMax(InpRiskRewardRatio, InpMinRiskRewardRatio);
            tpPrice = ask + ((ask - slPrice) * effectiveRR);
           }
         else
           {
            double effectivePoints = MathMax((double)InpTP_FixedPoints, minTargetPoints);
            tpPrice = ask + (effectivePoints * _Point);
           }

         // Enforce jarak minimum TP
         if((tpPrice - ask) < minAllowedDist)
           {
            tpPrice = ask + minAllowedDist;
           }

         double lot = riskManager.CalculateLotSize(accountInfo.Equity(), InpRiskPercent, slDistPoints,
                                                  _Symbol, InpFixedLot, (InpLotMode == LOT_FIXED), InpMaxLotSize);

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         if(trade.Buy(lot, _Symbol, ask, slPrice, tpPrice, InpOrderComment))
           {
            lastTradeBarTime = currentBarTime;
            patternEngine.MarkBottomTriggered();
            lastTradeStatus = StringFormat("BUY Executed @ %.2f (R:R %.1f)", ask, (tpPrice - ask) / (ask - slPrice));
            lastStatusColor = clrAqua;
            Print(StringFormat("[DOUBLE BOTTOM BUY SUCCESS] Lot: %.2f | Ask: %.2f | SL: %.2f | TP: %.2f | R:R: %.2f | Vol Ratio: %.2fx",
                               lot, ask, slPrice, tpPrice, (tpPrice - ask) / (ask - slPrice), pat.volumeRatio));
           }
         else
           {
            Print(StringFormat("[DOUBLE BOTTOM BUY GAGAL] Retcode: %d - %s", trade.ResultRetcode(), trade.ResultRetcodeDescription()));
           }
        }
     }

   // =======================================================
   // EKSEKUSI SINYAL SELL (Double Top "M" Neckline Breakdown)
   // =======================================================
   if(patternEngine.IsDoubleTopBreakout(rates, pat))
     {
      bool strongCandleOk = (!InpRequireStrongCandle || (rates[1].close < rates[1].open));

      // Filter Tren: jika harga di atas EMA 200 (bullish mega trend seperti Gold 2025/2026),
      // wajib ada konfirmasi RSI Overbought (>= 60-65) agar tidak sell sembarangan melawan tren!
      bool trendOk = true;
      if(InpUseEma200Filter && ema200Val > 0.0)
        {
         if(rates[1].close > ema200Val) // Counter-trend sell melawan super bull run
           {
            if(InpFilterCounterTrend && rsiVal < InpRsiExtremeSell)
              {
               trendOk = false;
               Print(StringFormat("[Double Top Filtered] Harga di atas EMA 200 & RSI belum overbought (%.1f < %.1f). Menolak Sell melawan tren.", rsiVal, InpRsiExtremeSell));
              }
           }
        }

      if(!strongCandleOk)
        {
         Print("[Double Top Filtered] Candle breakdown bukan candle bearish solid.");
        }
      else if(!trendOk)
        {
         Print("[Double Top Filtered] Trend filter memblokir transaksi Sell berisiko melawan tren naik.");
        }
      else
        {
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

         // SL ditempatkan di atas level resistance (tertinggi dari Puncak 1 dan Puncak 2)
         double resistanceLevel = MathMax(pat.p1, pat.p2);
         double slPrice = (InpSLMode == SL_PATTERN_EXTREMUM) ? (resistanceLevel + (InpSL_BufferPoints * _Point)) :
                                                               (bid + (InpMinSLPoints * _Point));

         // Enforce perlindungan broker: untuk SELL, SL dibandingkan dengan harga ASK
         if((slPrice - ask) < minAllowedDist)
           {
            slPrice = ask + minAllowedDist;
           }

         double slDistPoints = (slPrice - bid) / _Point;
         if(slDistPoints > InpMaxSLPoints)
           {
            slPrice = bid + (InpMaxSLPoints * _Point);
            slDistPoints = InpMaxSLPoints;
           }

         // Hitung Target Take Profit dengan perlindungan MINIMUM RISK:REWARD (>= InpMinRiskRewardRatio)
         double tpPrice = 0.0;
         double minTargetPoints = slDistPoints * InpMinRiskRewardRatio;

         if(InpTPMode == TP_PATTERN_HEIGHT)
           {
            double heightPoints = pat.patternHeight / _Point;
            double effectivePoints = MathMax(heightPoints, minTargetPoints);
            tpPrice = bid - (effectivePoints * _Point);
           }
         else if(InpTPMode == TP_RISK_REWARD)
           {
            double effectiveRR = MathMax(InpRiskRewardRatio, InpMinRiskRewardRatio);
            tpPrice = bid - ((slPrice - bid) * effectiveRR);
           }
         else
           {
            double effectivePoints = MathMax((double)InpTP_FixedPoints, minTargetPoints);
            tpPrice = bid - (effectivePoints * _Point);
           }

         // Enforce jarak minimum TP
         if((bid - tpPrice) < minAllowedDist)
           {
            tpPrice = bid - minAllowedDist;
           }

         double lot = riskManager.CalculateLotSize(accountInfo.Equity(), InpRiskPercent, slDistPoints,
                                                  _Symbol, InpFixedLot, (InpLotMode == LOT_FIXED), InpMaxLotSize);

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         if(trade.Sell(lot, _Symbol, bid, slPrice, tpPrice, InpOrderComment))
           {
            lastTradeBarTime = currentBarTime;
            patternEngine.MarkTopTriggered();
            lastTradeStatus = StringFormat("SELL Executed @ %.2f (R:R %.1f)", bid, (bid - tpPrice) / (slPrice - bid));
            lastStatusColor = clrMagenta;
            Print(StringFormat("[DOUBLE TOP SELL SUCCESS] Lot: %.2f | Bid: %.2f | SL: %.2f | TP: %.2f | R:R: %.2f | Vol Ratio: %.2fx",
                               lot, bid, slPrice, tpPrice, (bid - tpPrice) / (slPrice - bid), pat.volumeRatio));
           }
         else
           {
            Print(StringFormat("[DOUBLE TOP SELL GAGAL] Retcode: %d - %s", trade.ResultRetcode(), trade.ResultRetcodeDescription()));
           }
        }
     }
  }
//+------------------------------------------------------------------+
