import os
import shutil

# -------------------------------------------------------------
# 1. Fix MT5 OnInit and OnDeinit handle management
# -------------------------------------------------------------
mt5_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
with open(mt5_file, "r", encoding="utf-8") as f:
    mt5_content = f.read()

# Fix OnInit:
old_init_handles = """   h_ema8   = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema21  = iMA(_Symbol, _Period, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema125 = iMA(_Symbol, _Period, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_atr14  = iATR(_Symbol, _Period, 14);

   if (h_ema8 == INVALID_HANDLE || h_ema21 == INVALID_HANDLE ||
       h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE)
   {
      Print("[ERROR] Gagal menginisialisasi handle indikator MQL5!");
      return INIT_FAILED;
   }"""

new_init_handles = """   h_ema8    = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema21   = iMA(_Symbol, _Period, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema125  = iMA(_Symbol, _Period, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_atr14   = iATR(_Symbol, _Period, 14);
   h_rsi_div = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
   h_adx14   = iADX(_Symbol, _Period, InpADXPeriod);

   if (h_ema8 == INVALID_HANDLE || h_ema21 == INVALID_HANDLE ||
       h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE ||
       h_rsi_div == INVALID_HANDLE || h_adx14 == INVALID_HANDLE)
   {
      Print("[ERROR] Gagal menginisialisasi handle indikator MQL5!");
      return INIT_FAILED;
   }"""

if old_init_handles in mt5_content:
    mt5_content = mt5_content.replace(old_init_handles, new_init_handles)
    print("Fixed OnInit indicator handles in MT5!")

# Fix OnDeinit:
old_deinit = """   if (h_ema8 != INVALID_HANDLE)       IndicatorRelease(h_ema8);
   if (h_ema21 != INVALID_HANDLE)      IndicatorRelease(h_ema21);
   if (h_ema125 != INVALID_HANDLE)     IndicatorRelease(h_ema125);
   if (h_atr14 != INVALID_HANDLE)      IndicatorRelease(h_atr14);
   if (h_htf_ema125 != INVALID_HANDLE) IndicatorRelease(h_htf_ema125);
   if (h_htf_ema8 != INVALID_HANDLE)   IndicatorRelease(h_htf_ema8);
   if (h_htf_ema21 != INVALID_HANDLE)  IndicatorRelease(h_htf_ema21);"""

new_deinit = """   if (h_ema8 != INVALID_HANDLE)       IndicatorRelease(h_ema8);
   if (h_ema21 != INVALID_HANDLE)      IndicatorRelease(h_ema21);
   if (h_ema125 != INVALID_HANDLE)     IndicatorRelease(h_ema125);
   if (h_atr14 != INVALID_HANDLE)      IndicatorRelease(h_atr14);
   if (h_htf_ema125 != INVALID_HANDLE) IndicatorRelease(h_htf_ema125);
   if (h_htf_ema8 != INVALID_HANDLE)   IndicatorRelease(h_htf_ema8);
   if (h_htf_ema21 != INVALID_HANDLE)  IndicatorRelease(h_htf_ema21);
   if (h_rsi_div != INVALID_HANDLE)    IndicatorRelease(h_rsi_div);
   if (h_adx14 != INVALID_HANDLE)      IndicatorRelease(h_adx14);"""

if old_deinit in mt5_content:
    mt5_content = mt5_content.replace(old_deinit, new_deinit)
    print("Fixed OnDeinit indicator releases in MT5!")

with open(mt5_file, "w", encoding="utf-8") as f:
    f.write(mt5_content)

# -------------------------------------------------------------
# 2. Fix preset keys in MT4
# -------------------------------------------------------------
mt4_folder = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4"
mt4_dest = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\F0B9948E0028C307A69410B7E4F7F6B6\MQL4\Presets"

for fname in os.listdir(mt4_folder):
    if fname.endswith(".set"):
        fpath = os.path.join(mt4_folder, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            c = f.read()
        
        c = c.replace("InpDrawSMCObjects=", "InpDrawSMCOnChart=")
        c = c.replace("InpEnablePushAlerts=", "InpSendPushNotifications=")
        c = c.replace("InpNotifyOnOrderOpen=", "InpNotifyOnEntry=")
        c = c.replace("InpNotifyOnOrderClose=", "InpNotifyOnSLPlus=")
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(c)
        
        if os.path.exists(mt4_dest):
            shutil.copy(fpath, os.path.join(mt4_dest, fname))
        print(f"Updated and synced preset: {fname}")

print("Fixes applied successfully!")
