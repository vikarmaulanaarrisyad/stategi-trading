//+------------------------------------------------------------------+
//|                               EA_Institutional_SMC_Triple_EMA.mq5|
//|                 Copyright 2026, Institutional SMC & Triple EMA   |
//|                                      https://www.tradingview.com |
//+------------------------------------------------------------------+
#property copyright "Institutional SMC & Triple EMA Master"
#property link      "https://www.tradingview.com"
#property version   "1.00"
#property description "EA Otomatis MT5 berbasis Triple EMA (8, 21, 125) + 9 Pola Candlestick + SMC Pullback & Watchdog"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>

//+------------------------------------------------------------------+
//| ENUMERASI KONFIGURASI                                            |
//+------------------------------------------------------------------+
enum ENUM_LOT_TYPE
{
   LOT_TYPE_FIXED,       // Fixed Lot (Ukuran Lot Tetap)
   LOT_TYPE_RISK_PERCENT // Dynamic Risk % of Balance (Risiko % Modal)
};

enum ENUM_SL_TYPE
{
   SL_TYPE_CANDLE_WICK,  // Ujung Ekor Lilin Konfirmasi + Buffer
   SL_TYPE_EMA_21,       // Garis EMA 21 + Buffer
   SL_TYPE_FIXED_PIPS    // Fixed Pips (Jarak Pips Statis)
};

//+------------------------------------------------------------------+
//| INPUT PARAMETERS USER                                            |
//+------------------------------------------------------------------+
input group "=== 1. MANAJEMEN LOT & RISIKO ==="
input ENUM_LOT_TYPE InpLotType            = LOT_TYPE_FIXED;  // Model Manajemen Lot
input double        InpFixedLot           = 0.10;            // Ukuran Lot Tetap (Standar DIDIMAX min 0.10)
input double        InpRiskPercent        = 1.0;             // Risiko per Transaksi (% Saldo)
input double        InpMaxLot             = 20.0;            // Maksimal Lot Transaksi (Safeguard)
input int           InpMaxOpenPositions   = 1;               // Maksimal Posisi Aktif (1 = Anti-Hedging)
input int           InpSignalCooldownBars = 3;               // Jeda Lilin Minimal Antar Order (Cooldown Bars)
input ulong         InpMagicNumber        = 888125;          // Magic Number ID EA
input string        InpTradeComment       = "SMC-TripleEMA"; // Komentar Order
input ulong         InpDeviation          = 10;              // Slippage Maksimal (Points)

input group "=== 2. STOP LOSS & TAKE PROFIT ==="
input ENUM_SL_TYPE  InpSLType             = SL_TYPE_CANDLE_WICK; // Model Penempatan Stop Loss
input double        InpSLBufferPips       = 5.0;             // Buffer Pengaman SL (Pips)
input double        InpMinSLPips          = 18.0;            // Batas Minimum Jarak SL (Pips - Anti Micro SL)
input double        InpRiskRewardRatio    = 1.3;             // Rasio Target TP (RRR 1 : X - Sweet Spot M5)
input double        InpFixedSLPips        = 25.0;            // Jarak SL Statis (Jika Mode Fixed)
input double        InpMaxSpreadPips      = 6.0;             // Batas Maksimal Spread Diizinkan (Pips)
input bool          InpUseBreakeven       = true;            // Aktifkan Auto-Breakeven (BEP Kunci Profit)
input double        InpBreakevenTrigger   = 22.0;            // Pemicu BEP Saat Profit (Pips)
input double        InpBreakevenLock      = 8.0;             // Kunci Profit Saat BEP (Pips)
input bool          InpUseTrailing        = false;           // Aktifkan Trailing Stop Dinamis
input double        InpTrailingDistPips   = 25.0;            // Jarak Trailing Stop (Pips)
input double        InpTrailingStepPips   = 10.0;            // Langkah Trailing Stop (Pips)

input group "=== 3. TRIPLE EMA (EXPONENTIAL) ==="
input int           InpFastEMA            = 8;               // Fast EMA Period (Cyan)
input int           InpMediumEMA          = 21;              // Medium EMA Period (Kuning)
input int           InpTrendEMA           = 125;             // Trend Baseline EMA (Ungu)
input int           InpPullbackLookback   = 3;               // Jendela Memori Lilin Pullback (Bars)

input group "=== 4. FILTER ANTI-FALSE SIGNAL (WATCHDOG) ==="
input bool          InpFilterChop         = true;            // Filter EMA 8-21 Sideways / Cross Bolak-Balik
input bool          InpFilterWhipsaw125   = true;            // Filter Lilin Whipsaw Bolak-Balik EMA 125
input bool          InpFilterOverextended = true;            // Filter Lilin Terlalu Jauh dari EMA (Overextended)
input double        InpMaxAtrExtMult      = 2.2;             // Batas Jarak Maksimal Lilin ke EMA (x ATR)
input bool          InpFilterStructure    = true;            // Filter Validitas Struktur Market (HH-HL / LH-LL)

input group "=== 5. TOGGLE 9 POLA CANDLESTICK ==="
input bool          InpUseHammerShootingStar = true;         // 1. Hammer & Shooting Star
input bool          InpUsePinBar             = true;         // 2. Pin Bar Bullish & Bearish
input bool          InpUseEngulfing          = true;         // 3. Bullish & Bearish Engulfing
input bool          InpUseMorningEveningStar = true;         // 4. Morning Star & Evening Star
input bool          InpUsePiercingDarkCloud  = true;         // 5. Piercing Line & Dark Cloud Cover
input bool          InpUseThreeSoldiersCrows = true;         // 6. Three White Soldiers & Black Crows
input bool          InpUseDojiRejection      = true;         // 7. Doji Rejection Bullish & Bearish
input bool          InpUseInsideBar          = true;         // 8. Inside Bar Breakout & Breakdown
input bool          InpUseTwoCandleRejection = true;         // 9. Two Candle Rejection Bullish & Bearish

input group "=== 6. FILTER WAKTU SESI TRADING ==="
input bool          InpUseSessionFilter   = false;           // Batasi Jam Trading (London & NY)
input int           InpSessionStartHour   = 14;              // Jam Mulai Trading (WIB / Broker Hour)
input int           InpSessionEndHour     = 23;              // Jam Akhir Trading (WIB / Broker Hour)

//+------------------------------------------------------------------+
//| VARIABEL GLOBAL & HANDLE INDIKATOR                               |
//+------------------------------------------------------------------+
CTrade         trade;
CPositionInfo  posInfo;

int            h_ema8   = INVALID_HANDLE;
int            h_ema21  = INVALID_HANDLE;
int            h_ema125 = INVALID_HANDLE;
int            h_atr14  = INVALID_HANDLE;

datetime       lastBarTime = 0;
datetime       lastOrderBarTime = 0;

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: KONVERSI PIPS KE HARGA                          |
//+------------------------------------------------------------------+
double PipToPrice(double pips)
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double mult = (digits == 3 || digits == 5 || (StringFind(_Symbol, "XAU") >= 0 && digits == 2)) ? 10.0 : 1.0;
   return pips * point * mult;
}

//+------------------------------------------------------------------+
//| FUNGSI DETEKSI LILIN BARU (NEW BAR TRIGGER NON-REPAINTING)       |
//+------------------------------------------------------------------+
bool IsNewBar()
{
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if (currentBarTime != lastBarTime)
   {
      lastBarTime = currentBarTime;
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| FUNGSI NORMALISASI LOT SESUAI ATURAN BROKER (DIDIMAX COMPLIANT)  |
//+------------------------------------------------------------------+
double NormalizeLots(double rawLot)
{
   double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   // Fallback pengaman jika data broker belum terunduh sempurna
   if (minLot <= 0)  minLot = 0.10;
   if (maxLot <= 0)  maxLot = 50.0;
   if (stepLot <= 0) stepLot = 0.10;

   // Terapkan batas safeguard InpMaxLot dari user
   if (InpMaxLot > 0 && InpMaxLot < maxLot)
      maxLot = InpMaxLot;

   // Hitung presisi desimal lot berdasarkan stepLot (Didimax step 0.1 = 1 desimal, 0.01 = 2 desimal)
   int lotDigits = 0;
   if (stepLot <= 0.001) lotDigits = 3;
   else if (stepLot <= 0.01) lotDigits = 2;
   else if (stepLot <= 0.1)  lotDigits = 1;
   else lotDigits = 0;

   // Bulatkan ke kelipatan stepLot terdekat
   double lot = MathFloor((rawLot / stepLot) + 0.000001) * stepLot;

   // Validasi batas minimum & maksimum broker (DIDIMAX min 0.10)
   if (lot < minLot) lot = minLot;
   if (lot > maxLot) lot = maxLot;

   return NormalizeDouble(lot, lotDigits);
}

//+------------------------------------------------------------------+
//| KALKULASI LOT OTOMATIS BERDASARKAN RISIKO % & ATURAN BROKER      |
//+------------------------------------------------------------------+
double CalculateLots(double slDistancePrice)
{
   if (InpLotType == LOT_TYPE_FIXED || slDistancePrice <= 0)
      return NormalizeLots(InpFixedLot);

   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = balance * (InpRiskPercent / 100.0);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

   if (tickSize <= 0 || tickValue <= 0)
      return NormalizeLots(InpFixedLot);

   double ticksAtRisk = slDistancePrice / tickSize;
   double rawLot = riskAmount / (ticksAtRisk * tickValue);

   return NormalizeLots(rawLot);
}

//+------------------------------------------------------------------+
//| CEK FILTER WAKTU SESI                                            |
//+------------------------------------------------------------------+
bool IsInTradeSession()
{
   if (!InpUseSessionFilter) return true;
   MqlDateTime dt;
   TimeCurrent(dt);
   return (dt.hour >= InpSessionStartHour && dt.hour < InpSessionEndHour);
}

//+------------------------------------------------------------------+
//| ONINIT: INISIALISASI INDIKATOR & TRADE                           |
//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpDeviation);
   trade.SetTypeFillingBySymbol(_Symbol);

   double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   PrintFormat("[DIDIMAX BROKER INFO] Simbol: %s | Min Lot: %.2f | Max Lot: %.2f | Step Lot: %.2f",
               _Symbol, minLot, maxLot, stepLot);

   if (InpLotType == LOT_TYPE_FIXED && InpFixedLot < minLot)
   {
      PrintFormat("[DIDIMAX PENYESUAIAN] Input Lot (%.2f) < Min Lot broker (%.2f). EA otomatis menyesuaikan ke %.2f!",
                  InpFixedLot, minLot, minLot);
   }

   h_ema8   = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema21  = iMA(_Symbol, _Period, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema125 = iMA(_Symbol, _Period, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_atr14  = iATR(_Symbol, _Period, 14);

   if (h_ema8 == INVALID_HANDLE || h_ema21 == INVALID_HANDLE || h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE)
   {
      Print("Error: Gagal memuat handle indikator MT5!");
      return INIT_FAILED;
   }

   Print("EA Institutional SMC & Triple EMA berhasil diinisialisasi pada ", _Symbol, " [", EnumToString(_Period), "]");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| ONDEINIT: CLEANUP MEMORY                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if (h_ema8 != INVALID_HANDLE)   IndicatorRelease(h_ema8);
   if (h_ema21 != INVALID_HANDLE)  IndicatorRelease(h_ema21);
   if (h_ema125 != INVALID_HANDLE) IndicatorRelease(h_ema125);
   if (h_atr14 != INVALID_HANDLE)  IndicatorRelease(h_atr14);
}

//+------------------------------------------------------------------+
//| MODUL MANAJEMEN POSISI (BREAKEVEN & TRAILING STOP)               |
//+------------------------------------------------------------------+
void ManageOpenPositions()
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   double beTriggerPrice = PipToPrice(InpBreakevenTrigger);
   double beLockPrice    = PipToPrice(InpBreakevenLock);
   double trailDistPrice = PipToPrice(InpTrailingDistPips);
   double trailStepPrice = PipToPrice(InpTrailingStepPips);

   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (posInfo.SelectByIndex(i))
      {
         if (posInfo.Magic() == InpMagicNumber && posInfo.Symbol() == _Symbol)
         {
            double openPrice = posInfo.PriceOpen();
            double currentSL = posInfo.StopLoss();
            double currentTP = posInfo.TakeProfit();

            // 1. Logika Auto-Breakeven
            if (InpUseBreakeven)
            {
               if (posInfo.PositionType() == POSITION_TYPE_BUY)
               {
                  double currentBid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                  if (currentBid - openPrice >= beTriggerPrice)
                  {
                     double newSL = NormalizeDouble(openPrice + beLockPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
                     if (currentSL < newSL)
                     {
                        trade.PositionModify(posInfo.Ticket(), newSL, currentTP);
                        Print("Auto-Breakeven Aktif [BUY Ticket #", posInfo.Ticket(), "] SL digeser ke: ", newSL);
                     }
                  }
               }
               else if (posInfo.PositionType() == POSITION_TYPE_SELL)
               {
                  double currentAsk = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                  if (openPrice - currentAsk >= beTriggerPrice)
                  {
                     double newSL = NormalizeDouble(openPrice - beLockPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
                     if (currentSL == 0 || currentSL > newSL)
                     {
                        trade.PositionModify(posInfo.Ticket(), newSL, currentTP);
                        Print("Auto-Breakeven Aktif [SELL Ticket #", posInfo.Ticket(), "] SL digeser ke: ", newSL);
                     }
                  }
               }
            }

            // 2. Logika Trailing Stop Dinamis
            if (InpUseTrailing)
            {
               if (posInfo.PositionType() == POSITION_TYPE_BUY)
               {
                  double currentBid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                  if (currentBid - openPrice > trailDistPrice)
                  {
                     double proposedSL = NormalizeDouble(currentBid - trailDistPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
                     if (proposedSL > currentSL + trailStepPrice)
                     {
                        trade.PositionModify(posInfo.Ticket(), proposedSL, currentTP);
                     }
                  }
               }
               else if (posInfo.PositionType() == POSITION_TYPE_SELL)
               {
                  double currentAsk = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                  if (openPrice - currentAsk > trailDistPrice)
                  {
                     double proposedSL = NormalizeDouble(currentAsk + trailDistPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
                     if (currentSL == 0 || proposedSL < currentSL - trailStepPrice)
                     {
                        trade.PositionModify(posInfo.Ticket(), proposedSL, currentTP);
                     }
                  }
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| ON TICK: LOGIKA UTAMA & EKSEKUSI SINYAL                          |
//+------------------------------------------------------------------+
void OnTick()
{
   // Kelola trailing stop / BEP pada posisi yang sudah berjalan
   ManageOpenPositions();

   // Pastikan evaluasi sinyal HANYA terjadi pada pembukaan lilin baru (Closed Bar)
   if (!IsNewBar()) return;
   if (!IsInTradeSession()) return;

   // Filter Batas Spread Maksimal (Perlindungan dari pelebaran spread / news spike)
   if (InpMaxSpreadPips > 0)
   {
      double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      double pipPrice = PipToPrice(1.0);
      if (point > 0 && pipPrice > 0)
      {
         long spreadPoints = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
         double spreadPips = (spreadPoints * point) / pipPrice;
         if (spreadPips > InpMaxSpreadPips) return;
      }
   }

   // Filter Cooldown Lilin Antar Order (Anti-Revenge & Anti-Cluster Overtrading)
   if (InpSignalCooldownBars > 0 && lastOrderBarTime > 0)
   {
      int barsPassed = iBarShift(_Symbol, _Period, lastOrderBarTime);
      if (barsPassed < InpSignalCooldownBars) return;
   }

   // Cek apakah sudah ada posisi aktif dengan Magic Number ini
   bool hasBuyPos = false;
   bool hasSellPos = false;
   int totalPositions = 0;
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (posInfo.SelectByIndex(i))
      {
         if (posInfo.Magic() == InpMagicNumber && posInfo.Symbol() == _Symbol)
         {
            totalPositions++;
            if (posInfo.PositionType() == POSITION_TYPE_BUY)  hasBuyPos = true;
            if (posInfo.PositionType() == POSITION_TYPE_SELL) hasSellPos = true;
         }
      }
   }
   if (totalPositions >= InpMaxOpenPositions) return;

   // Salin data Lilin (Rates) & Indikator
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if (CopyRates(_Symbol, _Period, 0, 35, rates) < 30) return;

   double buf_ema8[], buf_ema21[], buf_ema125[], buf_atr[];
   ArraySetAsSeries(buf_ema8, true);
   ArraySetAsSeries(buf_ema21, true);
   ArraySetAsSeries(buf_ema125, true);
   ArraySetAsSeries(buf_atr, true);

   if (CopyBuffer(h_ema8, 0, 0, 30, buf_ema8) < 25) return;
   if (CopyBuffer(h_ema21, 0, 0, 30, buf_ema21) < 25) return;
   if (CopyBuffer(h_ema125, 0, 0, 30, buf_ema125) < 25) return;
   if (CopyBuffer(h_atr14, 0, 0, 30, buf_atr) < 25) return;

   // Lilin [1] adalah lilin konfirmasi yang baru saja selesai
   double o1 = rates[1].open,  h1 = rates[1].high, l1 = rates[1].low, c1 = rates[1].close;
   double o2 = rates[2].open,  h2 = rates[2].high, l2 = rates[2].low, c2 = rates[2].close;
   double o3 = rates[3].open,  h3 = rates[3].high, l3 = rates[3].low, c3 = rates[3].close;

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

   double atrVal = buf_atr[1];
   double minCandleSize = SymbolInfoDouble(_Symbol, SYMBOL_POINT) * 5.0;

   // -------------------------------------------------------------
   // A. DETEKSI 9 POLA CANDLESTICK BULLISH (Lilin [1])
   // -------------------------------------------------------------
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

   bool hasBullPattern = (bullPattern != "");

   // -------------------------------------------------------------
   // B. DETEKSI 9 POLA CANDLESTICK BEARISH (Lilin [1])
   // -------------------------------------------------------------
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

   bool hasBearPattern = (bearPattern != "");

   // -------------------------------------------------------------
   // C. FILTER KEAMANAN (WATCHDOG ANTI-FALSE SIGNAL)
   // -------------------------------------------------------------
   // 1. Filter Chop: Persilangan EMA 8 & 21 dalam 15 candle
   int emaCrosses = 0;
   for (int k = 1; k <= 15; k++)
   {
      bool crossUp = (buf_ema8[k] > buf_ema21[k] && buf_ema8[k+1] <= buf_ema21[k+1]);
      bool crossDn = (buf_ema8[k] < buf_ema21[k] && buf_ema8[k+1] >= buf_ema21[k+1]);
      if (crossUp || crossDn) emaCrosses++;
   }
   bool isChop = (emaCrosses >= 2) || (MathAbs(buf_ema8[1] - buf_ema21[1]) < (atrVal * 0.12));

   // 2. Filter Whipsaw: Harga melintasi EMA 125 bolak-balik dalam 20 candle
   int ema125Crosses = 0;
   for (int k = 1; k <= 20; k++)
   {
      bool crossUp = (rates[k].close > buf_ema125[k] && rates[k+1].close <= buf_ema125[k+1]);
      bool crossDn = (rates[k].close < buf_ema125[k] && rates[k+1].close >= buf_ema125[k+1]);
      if (crossUp || crossDn) ema125Crosses++;
   }
   bool isWhipsaw = (ema125Crosses >= 2);

   // 3. Filter Overextended (Lilin terlalu jauh dari EMA)
   bool isOverextendedBuy  = (c1 - buf_ema8[1]) > (atrVal * InpMaxAtrExtMult);
   bool isOverextendedSell = (buf_ema8[1] - c1) > (atrVal * InpMaxAtrExtMult);

   // 4. Filter Struktur Pasar (Higher Low / Lower High Swing)
   double lowestL = rates[1].low, prevLowestL = rates[5].low;
   double highestH = rates[1].high, prevHighestH = rates[5].high;
   for (int k = 1; k <= 5; k++)
   {
      if (rates[k].low < lowestL) lowestL = rates[k].low;
      if (rates[k].high > highestH) highestH = rates[k].high;
   }
   for (int k = 6; k <= 12; k++)
   {
      if (rates[k].low < prevLowestL) prevLowestL = rates[k].low;
      if (rates[k].high > prevHighestH) prevHighestH = rates[k].high;
   }
   bool isBullStructure = (lowestL >= prevLowestL);
   bool isBearStructure = (highestH <= prevHighestH);

   // -------------------------------------------------------------
   // D. DETEKSI PULLBACK DENGAN JENDELA MEMORI (1-3 BARS)
   // -------------------------------------------------------------
   bool buyPullbackDetected = false;
   bool sellPullbackDetected = false;

   for (int k = 1; k <= InpPullbackLookback; k++)
   {
      double emaTopK = MathMax(buf_ema8[k], buf_ema21[k]);
      double emaBtmK = MathMin(buf_ema8[k], buf_ema21[k]);

      // Pullback Buy: Low menyentuh area EMA 8/21 dan tetap di atas EMA 125
      if ((rates[k].low <= emaTopK * 1.0015) && (MathMin(rates[k].open, rates[k].close) >= buf_ema125[k]) && (rates[k].low >= buf_ema125[k] * 0.9980))
         buyPullbackDetected = true;

      // Pullback Sell: High menyentuh area EMA 8/21 dan tetap di bawah EMA 125
      if ((rates[k].high >= emaBtmK * 0.9985) && (MathMax(rates[k].open, rates[k].close) <= buf_ema125[k]) && (rates[k].high <= buf_ema125[k] * 1.0020))
         sellPullbackDetected = true;
   }

   // -------------------------------------------------------------
   // E. KONDISI EKSEKUSI SETUP BUY
   // -------------------------------------------------------------
   bool buyTrendValid = (c1 > buf_ema125[1]) && (buf_ema8[1] > buf_ema21[1]);
   bool buySafetyPass = (!InpFilterChop || !isChop) && (!InpFilterWhipsaw125 || !isWhipsaw) && (!InpFilterOverextended || !isOverextendedBuy) && (!InpFilterStructure || isBullStructure);

   if (!hasBuyPos && buyTrendValid && buyPullbackDetected && hasBullPattern && buySafetyPass)
   {
      double askPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double slPrice  = 0.0;

      if (InpSLType == SL_TYPE_CANDLE_WICK)
         slPrice = l1 - PipToPrice(InpSLBufferPips);
      else if (InpSLType == SL_TYPE_EMA_21)
         slPrice = buf_ema21[1] - PipToPrice(InpSLBufferPips);
      else
         slPrice = askPrice - PipToPrice(InpFixedSLPips);

      double slDist = askPrice - slPrice;
      double minSLDist = PipToPrice(InpMinSLPips);
      if (slDist < minSLDist)
      {
         slDist = minSLDist;
         slPrice = askPrice - slDist;
      }

      if (slDist > 0)
      {
         double tpPrice = askPrice + (slDist * InpRiskRewardRatio);
         double lotSize = CalculateLots(slDist);

         slPrice = NormalizeDouble(slPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
         tpPrice = NormalizeDouble(tpPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));

         if (trade.Buy(lotSize, _Symbol, askPrice, slPrice, tpPrice, InpTradeComment + "-" + bullPattern))
         {
            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            Print(">>> BUY ORDER EXECUTION! Pattern: ", bullPattern, " | Lots: ", lotSize, " | SL: ", slPrice, " | TP: ", tpPrice);
         }
      }
   }

   // -------------------------------------------------------------
   // F. KONDISI EKSEKUSI SETUP SELL
   // -------------------------------------------------------------
   bool sellTrendValid = (c1 < buf_ema125[1]) && (buf_ema8[1] < buf_ema21[1]);
   bool sellSafetyPass = (!InpFilterChop || !isChop) && (!InpFilterWhipsaw125 || !isWhipsaw) && (!InpFilterOverextended || !isOverextendedSell) && (!InpFilterStructure || isBearStructure);

   if (!hasSellPos && sellTrendValid && sellPullbackDetected && hasBearPattern && sellSafetyPass)
   {
      double bidPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double slPrice  = 0.0;

      if (InpSLType == SL_TYPE_CANDLE_WICK)
         slPrice = h1 + PipToPrice(InpSLBufferPips);
      else if (InpSLType == SL_TYPE_EMA_21)
         slPrice = buf_ema21[1] + PipToPrice(InpSLBufferPips);
      else
         slPrice = bidPrice + PipToPrice(InpFixedSLPips);

      double slDist = slPrice - bidPrice;
      double minSLDist = PipToPrice(InpMinSLPips);
      if (slDist < minSLDist)
      {
         slDist = minSLDist;
         slPrice = bidPrice + slDist;
      }

      if (slDist > 0)
      {
         double tpPrice = bidPrice - (slDist * InpRiskRewardRatio);
         double lotSize = CalculateLots(slDist);

         slPrice = NormalizeDouble(slPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));
         tpPrice = NormalizeDouble(tpPrice, (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS));

         if (trade.Sell(lotSize, _Symbol, bidPrice, slPrice, tpPrice, InpTradeComment + "-" + bearPattern))
         {
            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            Print(">>> SELL ORDER EXECUTION! Pattern: ", bearPattern, " | Lots: ", lotSize, " | SL: ", slPrice, " | TP: ", tpPrice);
         }
      }
   }
}
//+------------------------------------------------------------------+
