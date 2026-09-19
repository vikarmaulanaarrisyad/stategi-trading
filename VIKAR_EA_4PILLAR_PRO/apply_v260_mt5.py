import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Version and Description Header
old_header = """#property version   "2.30"
#property description "Robot Trading MT5 Institusional 4 Pilar Terpadu (v2.3 Apex Momentum & Guard)"
#property description "1. SMC Core & Momentum Breakout Engine (Anti-Ketinggalan Momentum)"
#property description "2. Order Block & Multi-Bar FVG Tracker with VSA Footprint Absorption"
#property description "3. Chart Pattern Engine & Advanced Candlestick Multi-Confluence"
#property description "4. Multi-Stage Structural Trailing Stop & Daily Circuit Breaker Guard"
#property description "5. Friday Weekend Gap Guard & Smartphone Push Notifications\""""

new_header = """#property version   "2.60"
#property description "Robot Trading MT5 Institusional 4 Pilar Terpadu (v2.60 Apex Edition)"
#property description "1. SMC Core & Momentum Breakout Engine (Anti-Ketinggalan Momentum)"
#property description "2. Order Block & Multi-Bar FVG Tracker with VSA Footprint Absorption"
#property description "3. Dynamic Pattern Performance Matrix (Self-Healing AI Rapor Pola v2.50)"
#property description "4. Market Regime Classifier (Choppiness Index Anti-Fakeout v2.50)"
#property description "5. Pre-News Event Shield, Spread Spike & RSI Divergence Sensor (v2.60)\""""

if old_header in content:
    content = content.replace(old_header, new_header)

# 2. Add Section 2.5 Inputs
inputs_25 = """
input group "=== 2.5 STAGNANT TRADE TIME-EXIT (v2.60) ==="
input bool          InpUseTimeBasedExit        = true;             // Tutup Otomatis Posisi yang Mengambang Terlalu Lama
input int           InpMaxTradeDurationHours   = 6;                // Batas Maksimal Durasi Posisi (Jam, e.g. 6 Jam)
input double        InpMinProfitToTimeExitPips = 0.0;              // Minimal Profit (Pips) untuk Time-Exit (0.0 = Impas / BE)
"""
if "InpUseTimeBasedExit" not in content:
    content = content.replace(
        'input bool          InpCutOnEMACross      = true;                  // Cut Profit Jika Lilin Menembus Ribbon EMA 21 Berlawanan',
        'input bool          InpCutOnEMACross      = true;                  // Cut Profit Jika Lilin Menembus Ribbon EMA 21 Berlawanan\n' + inputs_25.strip()
    )

# 3. Add Section 8.7 and 8.8 Inputs
inputs_87_88 = """
input group "=== 8.7 PRE-NEWS EVENT & SPREAD SPIKE SHIELD (v2.60) ==="
input bool          InpUseNewsShield           = true;             // Aktifkan Sensor Antisipasi Berita Berdampak Tinggi
input int           InpNewsMinsBefore          = 20;               // Waktu Pembekuan Sebelum Rilis Berita (Menit)
input int           InpNewsMinsAfter           = 25;               // Waktu Pembekuan Sesudah Rilis Berita (Menit)
input bool          InpAutoLockBEBeforeNews    = true;             // Otomatis Kunci SL+ pada Posisi Profit Jelang Berita
input string        InpNewsReleaseHoursServer  = "15:30,21:00";    // Jam Rilis Berita AS Utama (Waktu Server Broker)
input double        InpMaxSpreadSpikeMultiplier= 1.8;              // Batas Lonjakan Spread Dinamis (x InpMaxSpreadPips)

input group "=== 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ==="
input bool          InpUseDivergenceFilter     = true;             // Deteksi Divergensi RSI (Cegah Beli Pucuk / Jual Lembah)
input int           InpRSIPeriod               = 14;               // Periode RSI untuk Deteksi Momentum
input int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)
"""
if "InpUseNewsShield" not in content:
    content = content.replace(
        'input bool          InpBlockBreakoutInChoppy   = true;         // Blokir Momentum Breakout Saat Pasar Choppy',
        'input bool          InpBlockBreakoutInChoppy   = true;         // Blokir Momentum Breakout Saat Pasar Choppy\n' + inputs_87_88.strip()
    )

# 4. Add Globals and Forward Declarations for v2.60
globals_v260 = """
string g_newsStatusStr = "AMAN (STANDBY)";
string g_divStatusStr  = "NORMAL (SEHAT)";
int    h_rsi_div       = INVALID_HANDLE;

// Forward Declarations (v2.60)
bool IsInsideNewsWindowMQL5(string &activeNewsStr);
bool IsSpreadSpikeDetectedMQL5();
bool CheckRSIDivergenceMQL5(bool isBuy);
"""
if "IsInsideNewsWindowMQL5(string &activeNewsStr);" not in content:
    content = content.replace('string             g_bestPatternStr    = "BELUM ADA DATA";', 'string             g_bestPatternStr    = "BELUM ADA DATA";\n' + globals_v260.strip())

# 5. Add Handle Init in OnInit() and Release in OnDeinit()
if "h_rsi_div = iRSI" not in content:
    content = content.replace(
        'h_atr14  = iATR(_Symbol, _Period, InpATRPeriod);',
        'h_atr14  = iATR(_Symbol, _Period, InpATRPeriod);\n   h_rsi_div = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);'
    )

if "if (h_rsi_div != INVALID_HANDLE)" not in content:
    content = content.replace(
        'if (h_atr14  != INVALID_HANDLE) IndicatorRelease(h_atr14);',
        'if (h_atr14  != INVALID_HANDLE) IndicatorRelease(h_atr14);\n   if (h_rsi_div != INVALID_HANDLE) IndicatorRelease(h_rsi_div);'
    )

# 6. Add Helper Functions right before OnInit()
helpers_v260 = """
//+------------------------------------------------------------------+
//| SENSOR PRE-NEWS EVENT SHIELD: PEMERIKSAAN JADWAL RILIS BERITA AS |
//+------------------------------------------------------------------+
bool IsInsideNewsWindowMQL5(string &activeNewsStr)
{
   activeNewsStr = "";
   if (!InpUseNewsShield) return false;

   datetime now = TimeCurrent();
   MqlDateTime dt;
   TimeToStruct(now, dt);
   int currentMins = dt.hour * 60 + dt.min;

   string times[];
   int count = 0;
   string str = InpNewsReleaseHoursServer;
   while (StringLen(str) > 0)
   {
      int comma = StringFind(str, ",");
      string item = "";
      if (comma >= 0)
      {
         item = StringSubstr(str, 0, comma);
         str  = StringSubstr(str, comma + 1);
      }
      else
      {
         item = str;
         str  = "";
      }
      StringTrimLeft(item);
      StringTrimRight(item);
      if (StringLen(item) > 0)
      {
         ArrayResize(times, count + 1);
         times[count] = item;
         count++;
      }
   }

   for (int i = 0; i < count; i++)
   {
      int colon = StringFind(times[i], ":");
      if (colon > 0)
      {
         int h = (int)StringToInteger(StringSubstr(times[i], 0, colon));
         int m = (int)StringToInteger(StringSubstr(times[i], colon + 1));
         int targetMins = h * 60 + m;

         int startMins = targetMins - InpNewsMinsBefore;
         int endMins   = targetMins + InpNewsMinsAfter;

         if (currentMins >= startMins && currentMins <= endMins)
         {
            activeNewsStr = "BERITA AS @" + times[i];
            g_newsStatusStr = "WASPADA: JELANG " + times[i] + " SERVER";
            return true;
         }
      }
   }

   g_newsStatusStr = "AMAN (STANDBY)";
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR PELEBARAN SPREAD ABNORMAL (SPREAD SPIKE SHIELD MQL5)     |
//+------------------------------------------------------------------+
bool IsSpreadSpikeDetectedMQL5()
{
   if (!InpUseNewsShield) return false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double currentSpreadPips = PriceToPips(ask - bid);
   if (currentSpreadPips > (InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier))
   {
      Print("[SPREAD SPIKE SHIELD MT5] Terdeteksi lonjakan spread ekstrem: ", DoubleToString(currentSpreadPips, 1), " pips > ", DoubleToString(InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier, 1), " pips. Menunda eksekusi.");
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR PELEMAHAN MOMENTUM: RSI DIVERGENCE (ANTI-PUCUK / LEMBAH)  |
//+------------------------------------------------------------------+
bool CheckRSIDivergenceMQL5(bool isBuy)
{
   if (!InpUseDivergenceFilter || h_rsi_div == INVALID_HANDLE) return false;
   int lookback = MathMin(InpDivergenceLookbackBars, 50);

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if (CopyRates(_Symbol, _Period, 0, lookback + 5, rates) < lookback + 5)
      return false;

   double rsiBuf[];
   ArraySetAsSeries(rsiBuf, true);
   if (CopyBuffer(h_rsi_div, 0, 0, lookback + 5, rsiBuf) < lookback + 5)
      return false;

   if (isBuy)
   {
      // Deteksi Bearish Divergence (Harga buat Higher High, tapi RSI buat Lower High)
      int peak1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (rates[i].high > rates[peak1].high) peak1 = i;
      }

      int peak2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (rates[j].high > rates[peak2].high) peak2 = j;
      }

      double priceHigh1 = rates[peak1].high;
      double priceHigh2 = rates[peak2].high;
      double rsi1 = rsiBuf[peak1];
      double rsi2 = rsiBuf[peak2];

      if (priceHigh1 > priceHigh2 + PipToPrice(2.5) && rsi1 < rsi2 - 3.0 && rsi1 > 60.0)
      {
         g_divStatusStr = "BEARISH DIVERGENCE (EXHAUSTION TOP)";
         Print("[DIVERGENCE MT5] Bearish Divergence terdeteksi di pucuk (Peak1 RSI: ", DoubleToString(rsi1, 1), " < Peak2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan BUY.");
         return true;
      }
   }
   else
   {
      // Deteksi Bullish Divergence (Harga buat Lower Low, tapi RSI buat Higher Low)
      int trough1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (rates[i].low < rates[trough1].low) trough1 = i;
      }

      int trough2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (rates[j].low < rates[trough2].low) trough2 = j;
      }

      double priceLow1 = rates[trough1].low;
      double priceLow2 = rates[trough2].low;
      double rsi1 = rsiBuf[trough1];
      double rsi2 = rsiBuf[trough2];

      if (priceLow1 < priceLow2 - PipToPrice(2.5) && rsi1 > rsi2 + 3.0 && rsi1 < 40.0)
      {
         g_divStatusStr = "BULLISH DIVERGENCE (EXHAUSTION BOTTOM)";
         Print("[DIVERGENCE MT5] Bullish Divergence terdeteksi di dasar (Trough1 RSI: ", DoubleToString(rsi1, 1), " > Trough2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan SELL.");
         return true;
      }
   }

   g_divStatusStr = "NORMAL (SEHAT)";
   return false;
}
"""

if "bool IsInsideNewsWindowMQL5" not in content:
    content = content.replace(
        "int OnInit()",
        helpers_v260.strip() + "\n\nint OnInit()"
    )

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("apply_v260_mt5.py step 2 updated!")
