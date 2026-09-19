import os
import shutil

section_v250 = """
;--- 8.5 DYNAMIC PATTERN PERFORMANCE MATRIX (AI LEARNING v2.50) ---
InpUsePatternMatrix=1
InpMinTradesForPatternEval=3
InpPatternBlacklistWinrate=40.0
InpPatternBoostWinrate=70.0
InpPatternBoostScore=10.0
InpPatternPenaltyScore=15.0

;--- 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ---
InpUseRegimeFilter=1
InpChoppinessPeriod=14
InpChoppyThreshold=61.8
InpTrendingThreshold=38.2
InpBlockBreakoutInChoppy=1
"""

section_v260 = """
;--- 2.5 STAGNANT TRADE TIME-EXIT (v2.60) ---
InpUseTimeBasedExit=1
InpMaxTradeDurationHours=6
InpMinProfitToTimeExitPips=0.0

;--- 8.7 PRE-NEWS EVENT & SPREAD SPIKE SHIELD (v2.60) ---
InpUseNewsShield=1
InpNewsMinsBefore=20
InpNewsMinsAfter=25
InpAutoLockBEBeforeNews=1
InpNewsReleaseHoursServer=15:30,21:00
InpMaxSpreadSpikeMultiplier=1.8

;--- 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ---
InpUseDivergenceFilter=1
InpRSIPeriod=14
InpDivergenceLookbackBars=25
"""

section_v270 = """
;--- 8.9 SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70) ---
InpUseADXFilter=1
InpADXPeriod=14
InpMinADXThreshold=22.0

;--- 8.10 SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70) ---
InpUseEMASlopeFilter=1
InpEMASlopeLookback=5
InpMinEMASlopePips=3.0

;--- 8.11 SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70) ---
InpUseVolumeFilter=1
InpVolumeMAPeriod=20
InpMinVolumeMultiplier=1.15

;--- 8.12 BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70) ---
InpUseMinATRFilter=1
InpMinATRPips=12.0
"""

section_v300 = """
;--- 2.6 DYNAMIC STRUCTURAL SWING TRAILING (v3.00) ---
InpUseStructuralTrailing=1
InpStructuralTrailingAtrBuffer=0.5

;--- 8.13 PROP FIRM EQUITY GUARDIAN & KILL-SWITCH (v3.00) ---
InpUseEquityGuardian=1
InpMaxDailyEquityDDPct=4.0
InpLockTradingOnDDBreach=1

;--- 8.14 ASYMMETRIC CONFIDENCE RISK ALLOCATOR (v3.00) ---
InpUseAsymmetricLot=1
InpGradeABoostMultiplier=1.30
InpGradeBPenaltyMultiplier=0.70

;--- 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ---
InpUseTrapHunter=1
InpMinSweepPips=4.0
InpMaxSweepPips=30.0
InpMinRejectionWickPct=40.0
"""

def update_folder_presets(folder_path):
    for fname in os.listdir(folder_path):
        if fname.endswith(".set"):
            fpath = os.path.join(folder_path, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            changed = False
            if "InpUsePatternMatrix" not in content:
                print(f"Adding v2.50 sections to {fname}")
                content = content.strip() + "\n" + section_v250.strip() + "\n"
                changed = True
            if "InpUseNewsShield" not in content:
                print(f"Adding v2.60 sections to {fname}")
                content = content.strip() + "\n" + section_v260.strip() + "\n"
                changed = True
            if "InpUseADXFilter" not in content:
                print(f"Adding v2.70 sections to {fname}")
                content = content.strip() + "\n" + section_v270.strip() + "\n"
                changed = True
            if "InpUseEquityGuardian" not in content:
                print(f"Adding v3.00 Grandmaster sections to {fname}")
                content = content.strip() + "\n" + section_v300.strip() + "\n"
                changed = True
            if changed:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
            else:
                print(f"Already up-to-date: {fname}")

# 1. Update MT4 repo presets
update_folder_presets(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4")
# 2. Update MT5 repo presets
update_folder_presets(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO")

# 3. Copy MT4 presets to QuickPro MT4 Presets
mt4_dest = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\F0B9948E0028C307A69410B7E4F7F6B6\MQL4\Presets"
if os.path.exists(mt4_dest):
    for fname in os.listdir(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4"):
        if fname.endswith(".set"):
            src = os.path.join(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4", fname)
            shutil.copy(src, os.path.join(mt4_dest, fname))
            print(f"Copied {fname} to QuickPro MT4 Presets")

# 4. Copy MT5 presets to Didimax MT5 Presets & Experts
mt5_dest = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Presets"
mt5_experts_dest = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_4Pillar_Pro"
for d in [mt5_dest, mt5_experts_dest]:
    if os.path.exists(d):
        for fname in os.listdir(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO"):
            if fname.endswith(".set"):
                src = os.path.join(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO", fname)
                shutil.copy(src, os.path.join(d, fname))
                print(f"Copied {fname} to {os.path.basename(d)}")

print("All presets updated and synced for v3.00 Apex Grandmaster Edition successfully!")
