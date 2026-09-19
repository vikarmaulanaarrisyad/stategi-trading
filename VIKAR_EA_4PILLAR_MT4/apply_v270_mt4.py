import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update version property and description
content = content.replace('#property version   "2.60"', '#property version   "2.70"')
content = content.replace('v2.60 Apex Edition', 'v2.70 Apex Edition')
content = content.replace(
    '#property description "5. Pre-News Event Shield, Spread Spike & RSI Divergence Sensor (v2.60)"',
    '#property description "5. Pre-News Event Shield, Spread Spike & RSI Divergence Sensor (v2.60)"\n#property description "6. Smart Sideways & Anti-Fakeout Suite (ADX, EMA Slope, VSA, ATR Floor v2.70)"'
)

# 2. Add Section 8.9 - 8.12 Inputs
inputs_v270 = """
//--- 8.9 SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70) ---
extern string       sec89                  = "=== 8.9 SENSOR KEKUATAN TREN: ADX FILTER (v2.70) ===";
extern bool          InpUseADXFilter            = true;             // Blokir Entry Saat Pasar Tidur / Tanpa Arah (ADX Rendah)
extern int           InpADXPeriod               = 14;               // Periode Perhitungan ADX
extern double        InpMinADXThreshold         = 22.0;             // Ambang Batas Minimal ADX (Rekomendasi: 20.0 - 25.0)

//--- 8.10 SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70) ---
extern string       sec810                 = "=== 8.10 SENSOR KEMIRINGAN EMA SLOPE (v2.70) ===";
extern bool          InpUseEMASlopeFilter       = true;             // Blokir Entry Saat Garis EMA Datar / Kusut (Flat Sideways)
extern int           InpEMASlopeLookback        = 5;                // Jarak Lilin Pengujian Kemiringan EMA (Bars)
extern double        InpMinEMASlopePips         = 3.0;              // Ambang Batas Minimal Kenaikan/Penurunan EMA (Pips)

//--- 8.11 SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70) ---
extern string       sec811                 = "=== 8.11 SENSOR VOLUME INSTITUSIONAL: VSA (v2.70) ===";
extern bool          InpUseVolumeFilter         = true;             // Wajibkan Lonjakan Volume Institusi pada Lilin Konfirmasi
extern int           InpVolumeMAPeriod          = 20;               // Periode Rata-Rata Volume Bergerak (Bars)
extern double        InpMinVolumeMultiplier     = 1.15;             // Minimal Rasio Volume Konfirmasi (x Rata-Rata 20 Bar)

//--- 8.12 BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70) ---
extern string       sec812                 = "=== 8.12 BATAS BAWAH VOLATILITAS: ATR FLOOR (v2.70) ===";
extern bool          InpUseMinATRFilter         = true;             // Blokir Entry Saat Rentang Gerak Pasar Terlalu Sempit
extern double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)
"""

if "InpUseADXFilter" not in content:
    content = content.replace(
        'extern int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)',
        'extern int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)\n' + inputs_v270.strip()
    )

# 3. Add Globals for v2.70
globals_v270 = """
string g_sidewaysStatusStr = "NORMAL (TREN SEHAT)";
double g_currentADXVal     = 25.0;
double g_currentVolRatio   = 1.20;
"""
if "g_sidewaysStatusStr" not in content:
    content = content.replace(
        'string g_divStatusStr  = "NORMAL (SEHAT)";',
        'string g_divStatusStr  = "NORMAL (SEHAT)";\n' + globals_v270.strip()
    )

# 4. Add Helper Functions
helpers_v270 = """
//+------------------------------------------------------------------+
//| SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70)                 |
//+------------------------------------------------------------------+
bool CheckADXPower(double &adxVal)
{
   adxVal = iADX(Symbol(), 0, InpADXPeriod, PRICE_CLOSE, MODE_MAIN, 1);
   g_currentADXVal = adxVal;
   if (!InpUseADXFilter) return true;
   return (adxVal >= InpMinADXThreshold);
}

//+------------------------------------------------------------------+
//| SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70)                |
//+------------------------------------------------------------------+
bool CheckEMASlope(bool isBuy, double &slopePips)
{
   slopePips = 0.0;
   if (!InpUseEMASlopeFilter) return true;
   if (Bars < InpEMASlopeLookback + 5) return true;

   double emaNow  = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double emaPast = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1 + InpEMASlopeLookback);

   if (isBuy)
   {
      slopePips = PriceToPips(emaNow - emaPast);
      return (slopePips >= InpMinEMASlopePips);
   }
   else
   {
      slopePips = PriceToPips(emaPast - emaNow);
      return (slopePips >= InpMinEMASlopePips);
   }
}

//+------------------------------------------------------------------+
//| SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION FILTER (v2.70)        |
//+------------------------------------------------------------------+
bool CheckVolumeExpansion(double &volRatio)
{
   volRatio = 1.0;
   if (!InpUseVolumeFilter) return true;
   if (Bars < InpVolumeMAPeriod + 5) return true;

   double sumVol = 0.0;
   for (int i = 2; i <= InpVolumeMAPeriod + 1; i++)
   {
      sumVol += (double)Volume[i];
   }
   double avgVol = sumVol / (double)InpVolumeMAPeriod;
   if (avgVol <= 0) return true;

   double currentVol = (double)Volume[1];
   volRatio = currentVol / avgVol;
   g_currentVolRatio = volRatio;

   return (volRatio >= InpMinVolumeMultiplier);
}

//+------------------------------------------------------------------+
//| SENSOR BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70)       |
//+------------------------------------------------------------------+
bool CheckMinATRFloor(double currentAtrPrice, double &atrPips)
{
   atrPips = PriceToPips(currentAtrPrice);
   if (!InpUseMinATRFilter) return true;
   return (atrPips >= InpMinATRPips);
}
"""

if "bool CheckADXPower" not in content:
    content = content.replace(
        "bool CheckRSIDivergence(bool isBuy)",
        helpers_v270.strip() + "\n\nbool CheckRSIDivergence(bool isBuy)"
    )

# 5. Hook into OnTick() for Pre-News & Spread Spike Shield
old_ontick_session = """   // 5. Periksa Sesi Waktu Trading
   if (InpUseSessionFilter)
   {
      MqlDateTime dt;
      TimeToStruct(TimeCurrent(), dt);
      if (dt.hour < InpSessionStartHour || dt.hour >= InpSessionEndHour)
      {
         g_lastSignalType = "DILUAR SESI TRADING (" + IntegerToString(dt.hour) + ":00)";
         return;
      }
   }"""

new_ontick_session = """   // 5. Periksa Sesi Waktu Trading
   if (InpUseSessionFilter)
   {
      MqlDateTime dt;
      TimeToStruct(TimeCurrent(), dt);
      if (dt.hour < InpSessionStartHour || dt.hour >= InpSessionEndHour)
      {
         g_lastSignalType = "DILUAR SESI TRADING (" + IntegerToString(dt.hour) + ":00)";
         return;
      }
   }

   // 5.1 Pre-News Event Shield (v2.60)
   string activeNewsEvent = "";
   if (InpUseNewsShield && IsInsideNewsWindow(activeNewsEvent))
   {
      g_lastSignalType = "PRE-NEWS SHIELD: PEMBEKUAN ORDER JELANG " + activeNewsEvent;
      return;
   }

   // 5.2 Spread Anomaly Spike Shield (v2.60)
   if (InpUseNewsShield && IsSpreadSpikeDetected())
   {
      g_lastSignalType = "SPREAD SPIKE SHIELD: SPREAD MELEBAR ABNORMAL";
      return;
   }"""

if "activeNewsEvent" not in content:
    content = content.replace(old_ontick_session, new_ontick_session)

# 6. Hook into CheckTradeSignal() for ATR Floor, ADX, and Volume
old_atr_check = """   double currentAtr   = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);"""

new_atr_check = """   double currentAtr   = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   // 0.3 Batas Bawah Volatilitas: ATR Floor (v2.70)
   double currentAtrPips = 0.0;
   if (InpUseMinATRFilter && !CheckMinATRFloor(currentAtr, currentAtrPips))
   {
      g_lastSignalType = "ATR FLOOR: PASAR MATI / RANGE TERLALU SEMPIT (" + DoubleToString(currentAtrPips, 1) + " pips < " + DoubleToString(InpMinATRPips, 1) + " pips)";
      return;
   }

   // 0.4 Sensor Kekuatan Tren Kinetik: ADX Filter (v2.70)
   double adxPower = 0.0;
   if (InpUseADXFilter && !CheckADXPower(adxPower))
   {
      g_lastSignalType = "ADX FILTER: PASAR TIDUR / TANPA ARAH (ADX: " + DoubleToString(adxPower, 1) + " < " + DoubleToString(InpMinADXThreshold, 1) + ")";
      return;
   }

   // 0.5 Sensor Volume Institusional: VSA Filter (v2.70)
   double volRatio = 1.0;
   if (InpUseVolumeFilter && !CheckVolumeExpansion(volRatio))
   {
      g_lastSignalType = "VSA FILTER: VOLUME KERING / FAKEOUT RETAIL (Vol: " + DoubleToString(volRatio * 100.0, 0) + "% < " + DoubleToString(InpMinVolumeMultiplier * 100.0, 0) + "%)";
      return;
   }"""

if "currentAtrPips" not in content:
    content = content.replace(old_atr_check, new_atr_check)

# Hook EMA Slope into BUY check
old_buy_hook = """         if (InpUseDivergenceFilter && CheckRSIDivergence(true))
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }"""

new_buy_hook = """         if (InpUseDivergenceFilter && CheckRSIDivergence(true))
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }

         double slopeBuyPips = 0.0;
         if (InpUseEMASlopeFilter && !CheckEMASlope(true, slopeBuyPips))
         {
            g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeBuyPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
            return;
         }"""

if "slopeBuyPips" not in content:
    content = content.replace(old_buy_hook, new_buy_hook)

# Hook EMA Slope into SELL check
old_sell_hook = """         if (InpUseDivergenceFilter && CheckRSIDivergence(false))
         {
            g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
            return;
         }"""

new_sell_hook = """         if (InpUseDivergenceFilter && CheckRSIDivergence(false))
         {
            g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
            return;
         }

         double slopeSellPips = 0.0;
         if (InpUseEMASlopeFilter && !CheckEMASlope(false, slopeSellPips))
         {
            g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeSellPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
            return;
         }"""

if "slopeSellPips" not in content:
    content = content.replace(old_sell_hook, new_sell_hook)

# 7. Update HUD height & row in MT4
content = content.replace(
    'int panelH = InpShowPnLStats ? 590 : 510;',
    'int panelH = InpShowPnLStats ? 610 : 530;'
)

old_hud_block = """   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 164, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");
   currY += 184;"""

new_hud_block = """   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 164, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");

   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope Filter: AKTIF", C'148,163,184', 7, "Segoe UI");
   currY += 198;"""

if "VIKAR_HUD_SIDEWAYS" not in content:
    content = content.replace(old_hud_block, new_hud_block)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("apply_v270_mt4.py executed successfully!")
