import os

target_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Section 2.5 Inputs
inputs_25 = """
//--- 2.5 PROTEKSI POSISI MACET (STAGNANT TRADE TIME-EXIT v2.60) ---
extern string       sec25                  = "=== 2.5 STAGNANT TRADE TIME-EXIT (v2.60) ===";
extern bool          InpUseTimeBasedExit        = true;             // Tutup Otomatis Posisi yang Mengambang Terlalu Lama
extern int           InpMaxTradeDurationHours   = 6;                // Batas Maksimal Durasi Posisi (Jam, e.g. 6 Jam)
extern double        InpMinProfitToTimeExitPips = 0.0;              // Minimal Profit (Pips) untuk Time-Exit (0.0 = Impas / BE)
"""
if "InpUseTimeBasedExit" not in content:
    content = content.replace(
        'extern bool          InpCutOnEMACross      = true;                  // Cut Profit Jika Lilin Menembus Ribbon EMA 21 Berlawanan',
        'extern bool          InpCutOnEMACross      = true;                  // Cut Profit Jika Lilin Menembus Ribbon EMA 21 Berlawanan\n' + inputs_25.strip()
    )

# 2. Add Section 8.7 and 8.8 Inputs
inputs_87_88 = """
//--- 8.7 PRE-NEWS EVENT & SPREAD SPIKE SHIELD (v2.60) ---
extern string       sec87                  = "=== 8.7 PRE-NEWS EVENT SHIELD (v2.60) ===";
extern bool          InpUseNewsShield           = true;             // Aktifkan Sensor Antisipasi Berita Berdampak Tinggi
extern int           InpNewsMinsBefore          = 20;               // Waktu Pembekuan Sebelum Rilis Berita (Menit)
extern int           InpNewsMinsAfter           = 25;               // Waktu Pembekuan Sesudah Rilis Berita (Menit)
extern bool          InpAutoLockBEBeforeNews    = true;             // Otomatis Kunci SL+ pada Posisi Profit Jelang Berita
extern string        InpNewsReleaseHoursServer  = "15:30,21:00";    // Jam Rilis Berita AS Utama (Waktu Server Broker)
extern double        InpMaxSpreadSpikeMultiplier= 1.8;              // Batas Lonjakan Spread Dinamis (x InpMaxSpreadPips)

//--- 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ---
extern string       sec88                  = "=== 8.8 SENSOR KELELAHAN DIVERGENCE (v2.60) ===";
extern bool          InpUseDivergenceFilter     = true;             // Deteksi Divergensi RSI (Cegah Beli Pucuk / Jual Lembah)
extern int           InpRSIPeriod               = 14;               // Periode RSI untuk Deteksi Momentum
extern int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)
"""
if "InpUseNewsShield" not in content:
    content = content.replace(
        'extern bool          InpBlockBreakoutInChoppy   = true;             // Blokir Momentum Breakout Saat Pasar Choppy',
        'extern bool          InpBlockBreakoutInChoppy   = true;             // Blokir Momentum Breakout Saat Pasar Choppy\n' + inputs_87_88.strip()
    )

# 3. Add Globals for v2.60
globals_v260 = """
string g_newsStatusStr = "AMAN (STANDBY)";
string g_divStatusStr  = "NORMAL (SEHAT)";
"""
if "g_newsStatusStr" not in content:
    content = content.replace('string             g_bestPatternStr    = "BELUM ADA DATA";', 'string             g_bestPatternStr    = "BELUM ADA DATA";\n' + globals_v260.strip())

# 4. Add Helper Functions: IsInsideNewsWindow, IsSpreadSpikeDetected, CheckRSIDivergence
helpers_v260 = """
//+------------------------------------------------------------------+
//| SENSOR PRE-NEWS EVENT SHIELD: PEMERIKSAAN JADWAL RILIS BERITA AS |
//+------------------------------------------------------------------+
bool IsInsideNewsWindow(string &activeNewsStr)
{
   activeNewsStr = "";
   if (!InpUseNewsShield) return false;

   datetime now = TimeCurrent();
   int currentMins = TimeHour(now) * 60 + TimeMinute(now);

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
      item = StringTrimLeft(StringTrimRight(item));
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
//| SENSOR PELEBARAN SPREAD ABNORMAL (SPREAD SPIKE SHIELD)          |
//+------------------------------------------------------------------+
bool IsSpreadSpikeDetected()
{
   if (!InpUseNewsShield) return false;
   double currentSpreadPips = (double)MarketInfo(Symbol(), MODE_SPREAD) * Point / PipToPrice(1.0);
   if (currentSpreadPips > (InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier))
   {
      Print("[SPREAD SPIKE SHIELD MT4] Terdeteksi lonjakan spread ekstrem: ", DoubleToString(currentSpreadPips, 1), " pips > ", DoubleToString(InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier, 1), " pips. Menunda eksekusi.");
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR PELEMAHAN MOMENTUM: RSI DIVERGENCE (ANTI-PUCUK / LEMBAH)  |
//+------------------------------------------------------------------+
bool CheckRSIDivergence(bool isBuy)
{
   if (!InpUseDivergenceFilter) return false;
   int lookback = MathMin(InpDivergenceLookbackBars, Bars - 5);
   if (lookback < 10) return false;

   if (isBuy)
   {
      // Deteksi Bearish Divergence (Harga buat Higher High, tapi RSI buat Lower High)
      int peak1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (High[i] > High[peak1]) peak1 = i;
      }

      int peak2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (High[j] > High[peak2]) peak2 = j;
      }

      double priceHigh1 = High[peak1];
      double priceHigh2 = High[peak2];
      double rsi1 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, peak1);
      double rsi2 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, peak2);

      if (priceHigh1 > priceHigh2 + PipToPrice(2.5) && rsi1 < rsi2 - 3.0 && rsi1 > 60.0)
      {
         g_divStatusStr = "BEARISH DIVERGENCE (EXHAUSTION TOP)";
         Print("[DIVERGENCE MT4] Bearish Divergence terdeteksi di pucuk (Peak1 RSI: ", DoubleToString(rsi1, 1), " < Peak2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan BUY.");
         return true;
      }
   }
   else
   {
      // Deteksi Bullish Divergence (Harga buat Lower Low, tapi RSI buat Higher Low)
      int trough1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (Low[i] < Low[trough1]) trough1 = i;
      }

      int trough2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (Low[j] < Low[trough2]) trough2 = j;
      }

      double priceLow1 = Low[trough1];
      double priceLow2 = Low[trough2];
      double rsi1 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, trough1);
      double rsi2 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, trough2);

      if (priceLow1 < priceLow2 - PipToPrice(2.5) && rsi1 > rsi2 + 3.0 && rsi1 < 40.0)
      {
         g_divStatusStr = "BULLISH DIVERGENCE (EXHAUSTION BOTTOM)";
         Print("[DIVERGENCE MT4] Bullish Divergence terdeteksi di dasar (Trough1 RSI: ", DoubleToString(rsi1, 1), " > Trough2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan SELL.");
         return true;
      }
   }

   g_divStatusStr = "NORMAL (SEHAT)";
   return false;
}
"""
if "IsInsideNewsWindow" not in content:
    content = content.replace("void ResetSelfHealingState(string triggerReason)", helpers_v260.strip() + "\n\nvoid ResetSelfHealingState(string triggerReason)")

# 5. Add Stagnant Time-Exit and Pre-News BE Lock in ManageActiveTrades()
time_exit_code = """
      // 0. Stagnant Trade Time-Exit & Pre-News BE Protection (v2.60)
      double hoursOpen = (double)(TimeCurrent() - OrderOpenTime()) / 3600.0;
      double pipsProfit = (type == OP_BUY) ? PriceToPips(current - open) : PriceToPips(open - current);

      // Pre-News Auto-Lock BE
      string activeNewsShield = "";
      if (InpUseNewsShield && InpAutoLockBEBeforeNews && IsInsideNewsWindow(activeNewsShield))
      {
         if (pipsProfit >= InpBreakevenLockPips)
         {
            double lockPrice = (type == OP_BUY) ? NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), Digits)
                                                : NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), Digits);
            bool needLock = (type == OP_BUY) ? (sl < lockPrice) : (sl > lockPrice || sl == 0);
            if (needLock)
            {
               Print("[PRE-NEWS LOCK MT4] Order #", ticket, " dikunci ke SL+ jelang ", activeNewsShield);
               OrderModify(ticket, open, lockPrice, tp, 0, clrGold);
            }
         }
      }

      // Stagnant Time-Based Exit
      if (InpUseTimeBasedExit && hoursOpen >= (double)InpMaxTradeDurationHours && pipsProfit >= InpMinProfitToTimeExitPips)
      {
         Print("[TIME-EXIT MT4] Order #", ticket, " ditutup otomatis karena sudah mengambang ", DoubleToString(hoursOpen, 1), " jam (Profit: ", DoubleToString(pipsProfit, 1), " pips).");
         OrderClose(ticket, posVol, (type == OP_BUY ? Bid : Ask), InpDeviation, clrGold);
         continue;
      }
"""
if "Stagnant Trade Time-Exit" not in content:
    content = content.replace(
        'bool isRunnerLot = GlobalVariableCheck(gvKey);',
        'bool isRunnerLot = GlobalVariableCheck(gvKey);\n' + time_exit_code.strip()
    )

# 6. Hook Pre-News, Spread Spike, and Divergence into CheckTradeSignal()
old_signal_head = """   // 0. Filter Waktu Sesi Pasar
   if (InpUseSessionFilter && !IsInsideTradingSession())
   {
      g_lastSignalType = "DILUAR JAM SESI AKTIF (" + IntegerToString(InpSessionStartHour) + ":00 - " + IntegerToString(InpSessionEndHour) + ":00)";
      return;
   }"""

new_signal_head = """   // 0. Filter Waktu Sesi Pasar
   if (InpUseSessionFilter && !IsInsideTradingSession())
   {
      g_lastSignalType = "DILUAR JAM SESI AKTIF (" + IntegerToString(InpSessionStartHour) + ":00 - " + IntegerToString(InpSessionEndHour) + ":00)";
      return;
   }

   // 0.1 Pre-News Event Shield (v2.60)
   string activeNewsEvent = "";
   if (InpUseNewsShield && IsInsideNewsWindow(activeNewsEvent))
   {
      g_lastSignalType = "PRE-NEWS SHIELD: PEMBEKUAN ORDER JELANG " + activeNewsEvent;
      return;
   }

   // 0.2 Spread Anomaly Spike Shield (v2.60)
   if (InpUseNewsShield && IsSpreadSpikeDetected())
   {
      g_lastSignalType = "SPREAD SPIKE SHIELD: SPREAD MELEBAR ABNORMAL";
      return;
   }"""

if "activeNewsEvent" not in content:
    content = content.replace(old_signal_head, new_signal_head)

# Hook Divergence into BUY check
old_buy_precheck = "bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||"
new_buy_precheck = """if (InpUseDivergenceFilter && CheckRSIDivergence(true))
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||"""

if "CheckRSIDivergence(true)" not in content:
    content = content.replace(old_buy_precheck, new_buy_precheck)

# Hook Divergence into SELL check
old_sell_precheck = "bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||"
new_sell_precheck = """if (InpUseDivergenceFilter && CheckRSIDivergence(false))
         {
            g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
            return;
         }

         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||"""

if "CheckRSIDivergence(false)" not in content:
    content = content.replace(old_sell_precheck, new_sell_precheck)

# 7. Update Dashboard HUD height and add News Shield and Momentum rows
content = content.replace(
    'int panelH = InpShowPnLStats ? 555 : 475;',
    'int panelH = InpShowPnLStats ? 590 : 510;'
)

old_hud_rows = """   // Baris Rapor Pola Teruji (AI Pattern Matrix)
   string pmStr = InpUsePatternMatrix ? ("Terbaik: " + g_bestPatternStr) : "NONAKTIF";
   CreateOrUpdateText("VIKAR_HUD_PATMAT", panelX + 12, currY + 151, "[Rapor Pola]: " + pmStr, C'203,213,225', 7, "Segoe UI");
   currY += 170;"""

new_hud_rows = """   // Baris Rapor Pola Teruji (AI Pattern Matrix)
   string pmStr = InpUsePatternMatrix ? ("Terbaik: " + g_bestPatternStr) : "NONAKTIF";
   CreateOrUpdateText("VIKAR_HUD_PATMAT", panelX + 12, currY + 151, "[Rapor Pola]: " + pmStr, C'203,213,225', 7, "Segoe UI");

   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 164, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");
   currY += 184;"""

if "VIKAR_HUD_NEWS" not in content:
    content = content.replace(old_hud_rows, new_hud_rows)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("apply_v260_mt4.py finished successfully!")
