target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the dummy declarations if present
content = content.replace("""// Forward Declarations (v2.60)
bool IsInsideNewsWindowMQL5(string &activeNewsStr);
bool IsSpreadSpikeDetectedMQL5();
bool CheckRSIDivergenceMQL5(bool isBuy);\n""", "")

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
    content = content.replace("void OnTick()", helpers_v260.strip() + "\n\nvoid OnTick()")

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("fix_helpers_mt5.py done!")
