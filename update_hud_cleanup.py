import os

def apply_enhanced_hud():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Add DestroyDashboardGUI in OnInit
    anchor_oninit = "int OnInit()\n{\n"
    if anchor_oninit in code and "DestroyDashboardGUI();" not in code[code.find(anchor_oninit):code.find(anchor_oninit)+100]:
        code = code.replace(anchor_oninit, anchor_oninit + "   DestroyDashboardGUI();\n", 1)
        print("[+] Added DestroyDashboardGUI() in OnInit()")

    # 2. Add legacy object cleanup at top of UpdateDashboard()
    legacy_clean = """   // Pembersihan objek legacy dari versi sebelumnya agar tidak ada teks bertumpuk
   static bool s_cleanedLegacy = false;
   if (!s_cleanedLegacy)
   {
      ObjectDelete(0, "VIKAR_HUD_BAL_START");
      ObjectDelete(0, "VIKAR_HUD_BAL_CURR");
      ObjectDelete(0, "VIKAR_HUD_FLOAT");
      ObjectDelete(0, "VIKAR_HUD_SIDEWAYS");
      ObjectDelete(0, "VIKAR_HUD_HEAL");
      ObjectDelete(0, "VIKAR_HUD_PATMAT");
      ObjectDelete(0, "VIKAR_HUD_PRODISCIPLINE");
      s_cleanedLegacy = true;
   }"""
    
    if "Comment(\"\");" in code and "s_cleanedLegacy" not in code:
        code = code.replace("Comment(\"\"); // Bersihkan teks Comment biasa agar chart bersih", 
                            "Comment(\"\"); // Bersihkan teks Comment biasa agar chart bersih\n" + legacy_clean)
        print("[+] Added legacy object cleanup in UpdateDashboard()")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    print("[+] Successfully updated HUD with clean initializers!")

if __name__ == '__main__':
    apply_enhanced_hud()
