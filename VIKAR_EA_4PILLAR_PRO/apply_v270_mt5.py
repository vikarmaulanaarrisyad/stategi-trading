import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
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
input group "=== 8.9 SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70) ==="
input bool          InpUseADXFilter            = true;             // Blokir Entry Saat Pasar Tidur / Tanpa Arah (ADX Rendah)
input int           InpADXPeriod               = 14;               // Periode Perhitungan ADX
input double        InpMinADXThreshold         = 22.0;             // Ambang Batas Minimal ADX (Rekomendasi: 20.0 - 25.0)

input group "=== 8.10 SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70) ==="
input bool          InpUseEMASlopeFilter       = true;             // Blokir Entry Saat Garis EMA Datar / Kusut (Flat Sideways)
input int           InpEMASlopeLookback        = 5;                // Jarak Lilin Pengujian Kemiringan EMA (Bars)
input double        InpMinEMASlopePips         = 3.0;              // Ambang Batas Minimal Kenaikan/Penurunan EMA (Pips)

input group "=== 8.11 SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70) ==="
input bool          InpUseVolumeFilter         = true;             // Wajibkan Lonjakan Volume Institusi pada Lilin Konfirmasi
input int           InpVolumeMAPeriod          = 20;               // Periode Rata-Rata Volume Bergerak (Bars)
input double        InpMinVolumeMultiplier     = 1.15;             // Minimal Rasio Volume Konfirmasi (x Rata-Rata 20 Bar)

input group "=== 8.12 BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70) ==="
input bool          InpUseMinATRFilter         = true;             // Blokir Entry Saat Rentang Gerak Pasar Terlalu Sempit
input double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)
"""

if "InpUseADXFilter" not in content:
    content = content.replace(
        'input int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)',
        'input int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)\n' + inputs_v270.strip()
    )

# 3. Add Globals for v2.70
globals_v270 = """
string g_sidewaysStatusStr = "NORMAL (TREN SEHAT)";
double g_currentADXVal     = 25.0;
double g_currentVolRatio   = 1.20;
int    h_adx14             = INVALID_HANDLE;
"""
if "g_sidewaysStatusStr" not in content:
    content = content.replace(
        'int    h_rsi_div       = INVALID_HANDLE;',
        'int    h_rsi_div       = INVALID_HANDLE;\n' + globals_v270.strip()
    )

# 4. Handle Init in OnInit() and Release in OnDeinit()
if "h_adx14 = iADX" not in content:
    content = content.replace(
        'h_rsi_div = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);',
        'h_rsi_div = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);\n   h_adx14   = iADX(_Symbol, _Period, InpADXPeriod);'
    )

if "if (h_adx14 != INVALID_HANDLE)" not in content:
    content = content.replace(
        'if (h_rsi_div != INVALID_HANDLE) IndicatorRelease(h_rsi_div);',
        'if (h_rsi_div != INVALID_HANDLE) IndicatorRelease(h_rsi_div);\n   if (h_adx14   != INVALID_HANDLE) IndicatorRelease(h_adx14);'
    )

# 5. Add Helper Functions (placed right before void OnTick())
helpers_v270 = """
//+------------------------------------------------------------------+
//| SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70 MQL5)           |
//+------------------------------------------------------------------+
bool CheckADXPowerMQL5(double &adxVal)
{
   adxVal = 25.0;
   if (!InpUseADXFilter) return true;
   if (h_adx14 == INVALID_HANDLE) return true;

   double adxBuf[];
   ArraySetAsSeries(adxBuf, true);
   if (CopyBuffer(h_adx14, 0, 1, 1, adxBuf) < 1) return true;

   adxVal = adxBuf[0];
   g_currentADXVal = adxVal;
   return (adxVal >= InpMinADXThreshold);
}

//+------------------------------------------------------------------+
//| SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70 MQL5)          |
//+------------------------------------------------------------------+
bool CheckEMASlopeMQL5(bool isBuy, double &slopePips)
{
   slopePips = 0.0;
   if (!InpUseEMASlopeFilter) return true;
   if (h_ema125 == INVALID_HANDLE) return true;

   double emaBuf[];
   ArraySetAsSeries(emaBuf, true);
   int lookback = InpEMASlopeLookback;
   if (CopyBuffer(h_ema125, 0, 1, lookback + 1, emaBuf) < lookback + 1) return true;

   double emaNow  = emaBuf[0];
   double emaPast = emaBuf[lookback];

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
//| SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70 MQL5)         |
//+------------------------------------------------------------------+
bool CheckVolumeExpansionMQL5(double &volRatio)
{
   volRatio = 1.0;
   if (!InpUseVolumeFilter) return true;

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int lookback = InpVolumeMAPeriod + 5;
   if (CopyRates(_Symbol, _Period, 0, lookback, rates) < lookback) return true;

   double sumVol = 0.0;
   for (int i = 2; i <= InpVolumeMAPeriod + 1; i++)
   {
      sumVol += (double)rates[i].tick_volume;
   }
   double avgVol = sumVol / (double)InpVolumeMAPeriod;
   if (avgVol <= 0) return true;

   double currentVol = (double)rates[1].tick_volume;
   volRatio = currentVol / avgVol;
   g_currentVolRatio = volRatio;

   return (volRatio >= InpMinVolumeMultiplier);
}

//+------------------------------------------------------------------+
//| SENSOR BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70 MQL5)  |
//+------------------------------------------------------------------+
bool CheckMinATRFloorMQL5(double currentAtrPrice, double &atrPips)
{
   atrPips = PriceToPips(currentAtrPrice);
   if (!InpUseMinATRFilter) return true;
   return (atrPips >= InpMinATRPips);
}
"""

if "bool CheckADXPowerMQL5" not in content:
    content = content.replace(
        "void OnTick()",
        helpers_v270.strip() + "\n\nvoid OnTick()"
    )

# 6. Hook into OnTick() for ATR Floor, ADX, and Volume
old_ontick_rates = """   double currentAtr = PipToPrice(20.0);
   if (atr[1] > 0) currentAtr = atr[1];"""

new_ontick_rates = """   double currentAtr = PipToPrice(20.0);
   if (atr[1] > 0) currentAtr = atr[1];

   // 5.3 Batas Bawah Volatilitas: ATR Floor (v2.70)
   double currentAtrPips = 0.0;
   if (InpUseMinATRFilter && !CheckMinATRFloorMQL5(currentAtr, currentAtrPips))
   {
      g_lastSignalType = "ATR FLOOR: PASAR MATI / RANGE TERLALU SEMPIT (" + DoubleToString(currentAtrPips, 1) + " pips < " + DoubleToString(InpMinATRPips, 1) + " pips)";
      return;
   }

   // 5.4 Sensor Kekuatan Tren Kinetik: ADX Filter (v2.70)
   double adxPower = 0.0;
   if (InpUseADXFilter && !CheckADXPowerMQL5(adxPower))
   {
      g_lastSignalType = "ADX FILTER: PASAR TIDUR / TANPA ARAH (ADX: " + DoubleToString(adxPower, 1) + " < " + DoubleToString(InpMinADXThreshold, 1) + ")";
      return;
   }

   // 5.5 Sensor Volume Institusional: VSA Filter (v2.70)
   double volRatio = 1.0;
   if (InpUseVolumeFilter && !CheckVolumeExpansionMQL5(volRatio))
   {
      g_lastSignalType = "VSA FILTER: VOLUME KERING / FAKEOUT RETAIL (Vol: " + DoubleToString(volRatio * 100.0, 0) + "% < " + DoubleToString(InpMinVolumeMultiplier * 100.0, 0) + "%)";
      return;
   }"""

if "currentAtrPips" not in content:
    content = content.replace(old_ontick_rates, new_ontick_rates)

# Hook EMA Slope into BUY check in MT5
old_buy_hook_5 = """         if (InpUseDivergenceFilter && CheckRSIDivergenceMQL5(true))
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }"""

new_buy_hook_5 = """         if (InpUseDivergenceFilter && CheckRSIDivergenceMQL5(true))
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }

         double slopeBuyPips = 0.0;
         if (InpUseEMASlopeFilter && !CheckEMASlopeMQL5(true, slopeBuyPips))
         {
            g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeBuyPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
            return;
         }"""

if "slopeBuyPips" not in content:
    content = content.replace(old_buy_hook_5, new_buy_hook_5)

# Hook EMA Slope into SELL check in MT5
old_sell_hook_5 = """      if (InpUseDivergenceFilter && CheckRSIDivergenceMQL5(false))
      {
         g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
         return;
      }"""

new_sell_hook_5 = """      if (InpUseDivergenceFilter && CheckRSIDivergenceMQL5(false))
      {
         g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
         return;
      }

      double slopeSellPips = 0.0;
      if (InpUseEMASlopeFilter && !CheckEMASlopeMQL5(false, slopeSellPips))
      {
         g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeSellPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
         return;
      }"""

if "slopeSellPips" not in content:
    content = content.replace(old_sell_hook_5, new_sell_hook_5)

# 7. Update Dashboard HUD height & row in MT5
content = content.replace(
    'int panelH = InpShowPnLStats ? 590 : 510;',
    'int panelH = InpShowPnLStats ? 610 : 530;'
)

old_hud_block_5 = """   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 164, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");
   currY += 184;"""

new_hud_block_5 = """   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 164, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");

   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope Filter: AKTIF", C'148,163,184', 7, "Segoe UI");
   currY += 198;"""

if "VIKAR_HUD_SIDEWAYS" not in content:
    content = content.replace(old_hud_block_5, new_hud_block_5)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("apply_v270_mt5.py executed successfully!")
