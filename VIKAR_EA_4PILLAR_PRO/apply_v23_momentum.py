# -*- coding: utf-8 -*-
"""
Script untuk menerapkan v2.3 Apex Momentum & Guard ke VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5
"""

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Header Version
old_header = """#property version   "2.20"
#property description "Robot Trading MT5 Institusional 4 Pilar Terpadu (v2.2 Apex Institutional)"
#property description "1. SMC Core: BOS, CHoCH, Liquidity Sweep, Discount/Premium Matrix"
#property description "2. Order Block Engine (Displacement ATR) & Multi-Bar FVG Tracker"
#property description "3. Chart Pattern Engine (W/M, Quasimodo QM, Head & Shoulders, Flags)"
#property description "4. Advanced Candlestick Intelligence & Volume Spread Analysis (VSA Footprint)"
#property description "5. Multi-Stage Structural Trailing Stop & Daily Circuit Breaker Guard\""""

new_header = """#property version   "2.30"
#property description "Robot Trading MT5 Institusional 4 Pilar Terpadu (v2.3 Apex Momentum & Guard)"
#property description "1. SMC Core & Momentum Breakout Engine (Anti-Ketinggalan Momentum)"
#property description "2. Order Block & Multi-Bar FVG Tracker with VSA Footprint Absorption"
#property description "3. Chart Pattern Engine & Advanced Candlestick Multi-Confluence"
#property description "4. Multi-Stage Structural Trailing Stop & Daily Circuit Breaker Guard"
#property description "5. Friday Weekend Gap Guard & Smartphone Push Notifications\""""

assert old_header in content, "Header match failed!"
content = content.replace(old_header, new_header, 1)

# 2. Add Momentum Breakout Inputs under Group 3.1
old_pilar2 = 'input group "=== 4. PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS) ==="'
idx_p2 = content.find(old_pilar2)
assert idx_p2 != -1, "Group 4 find failed!"

momentum_inputs = """input group "=== 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ==="
input bool          InpAllowMomentumBreakout       = true;         // Aktifkan Eksekusi Momentum Breakout (Anti-Ketinggalan Reli)
input double        InpBreakoutAtrMult             = 1.0;          // Minimal Ukuran Lilin Breakout (x Nilai ATR 14)
input bool          InpBreakoutRequireVSA          = true;         // Wajib Didukung Lonjakan Volume VSA (>= 1.3x)
input bool          InpBreakoutRequireBOS          = true;         // Wajib Menembus Swing High/Low (Konfirmasi BOS)

"""

content = content[:idx_p2] + momentum_inputs + content[idx_p2:]

# 3. Add Friday Guard and Push Notification Inputs
idx_vsa_grp = content.find('input group "=== 8.2 VOLUME SPREAD ANALYSIS')
assert idx_vsa_grp != -1, "Group 8.2 find failed!"
idx_smc_draw = content.find('input group "=== 9. ON-CHART SMC VISUALIZER', idx_vsa_grp)
assert idx_smc_draw != -1, "Group 9 find failed!"

friday_push_inputs = """input group "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ==="
input bool          InpUseFridayGuard              = true;         // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
input int           InpFridayCloseHour             = 21;           // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)

input group "=== 11. NOTIFIKASI PUSH KE SMARTPHONE (HP) ==="
input bool          InpSendPushNotifications       = true;         // Kirim Notifikasi Instan ke HP (MetaTrader 5 Mobile)
input bool          InpNotifyOnEntry               = true;         // Notifikasi Saat Eksekusi Open Posisi (BUY / SELL)
input bool          InpNotifyOnSLPlus              = true;         // Notifikasi Saat Auto-BE / SL+ Mengunci Profit
input bool          InpNotifyOnPartial             = true;         // Notifikasi Saat TP1 50% Ditutup & Runner Aktif
input bool          InpNotifyOnCircuitBreaker      = true;         // Notifikasi Saat Circuit Breaker Cooldown Terpicu

"""

content = content[:idx_smc_draw] + friday_push_inputs + content[idx_smc_draw:]

# 4. Add Helper Function SendPushAlert
idx_helpers = content.find("//| FUNGSI PEMBANTU: KONVERSI PIPS & POINTS")
assert idx_helpers != -1, "Helpers find failed!"

push_func = """//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: NOTIFIKASI PUSH SMARTPHONE (HP)                 |
//+------------------------------------------------------------------+
void SendPushAlert(string msg)
{
   if (!InpSendPushNotifications) return;
   SendNotification("[VIKAR EA PRO - " + _Symbol + "]\\n" + msg);
}

"""

content = content[:idx_helpers] + push_func + content[idx_helpers:]

# 5. Add Friday Guard to OnTick
old_ontick_newbar = """   // 3.1 Periksa Proteksi Akun & Circuit Breaker (Consecutive Loss Cooldown & Daily Limit)
   if (!CheckCircuitBreakers())
      return;"""

new_ontick_newbar = """   // 3.1 Periksa Proteksi Akun & Circuit Breaker (Consecutive Loss Cooldown & Daily Limit)
   if (!CheckCircuitBreakers())
      return;

   // 3.2 Proteksi Akhir Pekan (Friday Weekend Guard - Anti Gap Akhir Pekan)
   if (InpUseFridayGuard)
   {
      MqlDateTime dtFriday;
      TimeCurrent(dtFriday);
      if (dtFriday.day_of_week == 5 && dtFriday.hour >= InpFridayCloseHour)
      {
         for (int fPos = PositionsTotal() - 1; fPos >= 0; fPos--)
         {
            if (posInfo.SelectByIndex(fPos) && posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
            {
               trade.PositionClose(posInfo.Ticket());
               Print("[FRIDAY WEEKEND GUARD] Menutup posisi #", posInfo.Ticket(), " jelang akhir pekan demi keamanan modal!");
            }
         }
         g_lastSignalType = "FRIDAY WEEKEND GUARD: PASAR JUMAT MALAM (ANTI-GAP)";
         return;
      }
   }"""

assert old_ontick_newbar in content, "OnTick newbar match failed!"
content = content.replace(old_ontick_newbar, new_ontick_newbar, 1)

# 6. Push Alert on Circuit Breaker Trigger
old_cb_trigger = """         g_cooldownUntilTime = cooldownEnd;
         int remainingMins = (int)((cooldownEnd - TimeCurrent()) / 60);
         g_lastSignalType = "CIRCUIT BREAKER: 2x LOSS COOLDOWN (Sisa " + IntegerToString(remainingMins) + " Mnt)";
         return false; // Blok entry baru selama cooldown!"""

new_cb_trigger = """         g_cooldownUntilTime = cooldownEnd;
         int remainingMins = (int)((cooldownEnd - TimeCurrent()) / 60);
         g_lastSignalType = "CIRCUIT BREAKER: 2x LOSS COOLDOWN (Sisa " + IntegerToString(remainingMins) + " Mnt)";
         static datetime lastCBPushTime = 0;
         if (InpNotifyOnCircuitBreaker && (TimeCurrent() - lastCBPushTime) > 3600)
         {
            SendPushAlert("CIRCUIT BREAKER ACTIVE!\\nTerjadi 2x loss berturut-turut. Robot beristirahat selama 4 jam untuk proteksi modal.");
            lastCBPushTime = TimeCurrent();
         }
         return false; // Blok entry baru selama cooldown!"""

assert old_cb_trigger in content, "CB trigger match failed!"
content = content.replace(old_cb_trigger, new_cb_trigger, 1)

# 7. Add Momentum Breakout Evaluation to BUY
old_buy_exec_block = """         // EKSEKUSI BUY JIKA SEMUA PILAR & SKOR KONFLUENSI MEMENUHI SYARAT
         if (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed)
         {"""

new_buy_exec_block = """         // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = rates[1].close - rates[1].open;
            bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (rates[1].close > currentEma8 && currentEma8 > currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close > lastSwingHigh.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || rates[1].tick_volume >= (long)(1.3 * (double)rates[2].tick_volume)));

            if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
            {
               isMomentumBreakout = true;
            }
         }

         // EKSEKUSI BUY JIKA:
         // Jalur 1 (Konservatif Pullback Sniper): Memenuhi semua 4 pilar + pullback + rejection + skor lolos
         // ATAU
         // Jalur 2 (Agresif Momentum Breakout): Terdeteksi Momentum Expansion BOS tanpa wajib pullback/diskon!
         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||
                              (isMomentumBreakout && isHeadroomOk);

         if (canExecuteBuy)
         {"""

assert old_buy_exec_block in content, "BUY exec block match failed!"
content = content.replace(old_buy_exec_block, new_buy_exec_block, 1)

# 8. Add Momentum comment, Push Alert & Broker retcode to BUY
old_buy_send = """            string tradeCmt = InpTradeComment + (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"));
            if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
            {
               lastOrderBarTime = iTime(_Symbol, _Period, 0);
               g_lastSignalType = "BUY EXECUTED: " + g_candleAnalysis.patternName + " (Skor: " + DoubleToString(g_candleAnalysis.score, 0) + ")";
               Print("[BUY EXECUTION] Lot: ", lots, " | Price: ", ask, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", g_candleAnalysis.patternName, " | Structure: ", g_smcAnalysis.structureName);
               UpdateDashboard();
               return;
            }"""

new_buy_send = """            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
            {
               lastOrderBarTime = iTime(_Symbol, _Period, 0);
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = "BUY EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
               Print("[BUY EXECUTION] Lot: ", lots, " | Price: ", ask, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert("BUY " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(ask, _Digits) +
                                "\\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                                "\\nPola: " + patStr);
               }
               UpdateDashboard();
               return;
            }
            else
            {
               Print("[BUY REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
               g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
            }"""

assert old_buy_send in content, "BUY send match failed!"
content = content.replace(old_buy_send, new_buy_send, 1)

# 9. Add Momentum Breakout Evaluation to SELL
old_sell_exec_block = """      // EKSEKUSI SELL JIKA SEMUA PILAR & SKOR KONFLUENSI MEMENUHI SYARAT
      if (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed)
      {"""

new_sell_exec_block = """      // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Terjun)
      bool isMomentumBreakout = false;
      if (InpAllowMomentumBreakout)
      {
         double candleBody = rates[1].open - rates[1].close;
         bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
         bool isRibbonExpanding = (rates[1].close < currentEma8 && currentEma8 < currentEma21);
         bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close < lastSwingLow.price || g_smcAnalysis.hasBOS);
         bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || rates[1].tick_volume >= (long)(1.3 * (double)rates[2].tick_volume)));

         if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
         {
            isMomentumBreakout = true;
         }
      }

      // EKSEKUSI SELL JIKA:
      // Jalur 1 (Konservatif Pullback Sniper): Memenuhi semua 4 pilar + pullback + rejection + skor lolos
      // ATAU
      // Jalur 2 (Agresif Momentum Breakout): Terdeteksi Momentum Expansion BOS tanpa wajib pullback/diskon!
      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||
                            (isMomentumBreakout && isHeadroomOk);

      if (canExecuteSell)
      {"""

assert old_sell_exec_block in content, "SELL exec block match failed!"
content = content.replace(old_sell_exec_block, new_sell_exec_block, 1)

# 10. Add Momentum comment, Push Alert & Broker retcode to SELL
old_sell_send = """         string tradeCmt = InpTradeComment + (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"));
         if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
         {
            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            g_lastSignalType = "SELL EXECUTED: " + g_candleAnalysis.patternName + " (Skor: " + DoubleToString(g_candleAnalysis.score, 0) + ")";
            Print("[SELL EXECUTION] Lot: ", lots, " | Price: ", bid, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", g_candleAnalysis.patternName, " | Structure: ", g_smcAnalysis.structureName);
            UpdateDashboard();
            return;
         }"""

new_sell_send = """         string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
         if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
         {
            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
            g_lastSignalType = "SELL EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
            Print("[SELL EXECUTION] Lot: ", lots, " | Price: ", bid, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
            if (InpNotifyOnEntry)
            {
               SendPushAlert("SELL " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(bid, _Digits) +
                             "\\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                             "\\nPola: " + patStr);
            }
            UpdateDashboard();
            return;
         }
         else
         {
            Print("[SELL REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
            g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
         }"""

assert old_sell_send in content, "SELL send match failed!"
content = content.replace(old_sell_send, new_sell_send, 1)

# 11. Push Alert on Auto-BE SL+
target_be_buy = 'Print("[AUTO-BE / SL+] Posisi BUY #", ticket, " SL digeser ke SL+ (Kunci +", DoubleToString(InpBreakevenLockPips, 1), " pips): ", newSL);'
repl_be_buy = target_be_buy + '\n                      if (InpNotifyOnSLPlus) SendPushAlert("AUTO-BE SL+ LOCKED!\\nPosisi BUY #" + IntegerToString(ticket) + " SL dikunci ke " + DoubleToString(newSL, _Digits) + " (Profit Terkunci)");'

assert target_be_buy in content, "target_be_buy find failed!"
content = content.replace(target_be_buy, repl_be_buy, 1)

target_be_sell = 'Print("[AUTO-BE / SL+] Posisi SELL #", ticket, " SL digeser ke SL+ (Kunci +", DoubleToString(InpBreakevenLockPips, 1), " pips): ", newSL);'
repl_be_sell = target_be_sell + '\n                      if (InpNotifyOnSLPlus) SendPushAlert("AUTO-BE SL+ LOCKED!\\nPosisi SELL #" + IntegerToString(ticket) + " SL dikunci ke " + DoubleToString(newSL, _Digits) + " (Profit Terkunci)");'

assert target_be_sell in content, "target_be_sell find failed!"
content = content.replace(target_be_sell, repl_be_sell, 1)

with open('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5', 'w', encoding='utf-8') as f:
    f.write(content)

print("v2.3 Apex Momentum & Guard modifications successfully applied to VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5!")
