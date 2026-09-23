import os
import shutil

def fix_hud_timer():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Add EventSetTimer and immediate draw in OnInit()
    old_init_end = """   Print("=== VIKAR EA 4-PILLAR PRO INITIALIZED SUCCESSFULLY ===");
   Print("Aset: ", _Symbol, " | Timeframe: ", EnumToString(_Period), " | Magic: ", InpMagicNumber);
   Print("Start Time: ", TimeToString(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Balance: $", g_eaInitialBalance);

   return INIT_SUCCEEDED;"""

    new_init_end = """   Print("=== VIKAR EA 4-PILLAR PRO INITIALIZED SUCCESSFULLY ===");
   Print("Aset: ", _Symbol, " | Timeframe: ", EnumToString(_Period), " | Magic: ", InpMagicNumber);
   Print("Start Time: ", TimeToString(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Balance: $", g_eaInitialBalance);

   // Aktifkan timer 1 detik agar HUD selalu live dan langsung muncul walau pasar libur / weekend
   EventSetTimer(1);
   if (InpShowDashboard)
   {
      UpdateDashboard();
      ChartRedraw(0);
   }

   return INIT_SUCCEEDED;"""

    if old_init_end in code:
        code = code.replace(old_init_end, new_init_end)
        print("[+] Added EventSetTimer(1) & immediate UpdateDashboard in OnInit()")
    else:
        print("[-] old_init_end not found!")

    # 2. Add EventKillTimer in OnDeinit()
    old_deinit = """void OnDeinit(const int reason)
{"""
    new_deinit = """void OnDeinit(const int reason)
{
   EventKillTimer();"""
    if old_deinit in code and "EventKillTimer();" not in code:
        code = code.replace(old_deinit, new_deinit, 1)
        print("[+] Added EventKillTimer in OnDeinit()")

    # 3. Add void OnTimer() right before OnTick()
    old_ontick_header = "//+------------------------------------------------------------------+\n//| ON TICK"
    ontimer_func = """//+------------------------------------------------------------------+
//| ON TIMER (UPDATE DASHBOARD OTOMATIS WALAUPUN PASAR TUTUP/WEEKEND)|
//+------------------------------------------------------------------+
void OnTimer()
{
   if (InpShowDashboard)
   {
      UpdateDashboard();
   }
}

//+------------------------------------------------------------------+
//| ON TICK"""
    if old_ontick_header in code and "void OnTimer()" not in code:
        code = code.replace(old_ontick_header, ontimer_func, 1)
        print("[+] Added void OnTimer() before OnTick()")
    else:
        print("[-] old_ontick_header not found or OnTimer already exists")

    # 4. Add ChartRedraw(0); at end of UpdateDashboard()
    old_hud_end = """   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", cardX + 10, currY + 39, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + " | Lot: " + DoubleToString(currentLotSize, 2), C'148,163,184', 7, "Segoe UI");
}"""

    new_hud_end = """   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", cardX + 10, currY + 39, "Mode: " + entryModeTag + " | " + beStr + " | " + cutStr + " | " + trailStr + " | Lot: " + DoubleToString(currentLotSize, 2), C'148,163,184', 7, "Segoe UI");

   // Paksa MT5 merender visual grafik secara instan (Sangat penting saat akhir pekan / pasar tutup)
   ChartRedraw(0);
}"""

    if old_hud_end in code:
        code = code.replace(old_hud_end, new_hud_end)
        print("[+] Added ChartRedraw(0) at end of UpdateDashboard()")
    else:
        print("[-] old_hud_end not found!")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] All live timer & immediate rendering fixes applied!")

if __name__ == '__main__':
    fix_hud_timer()
