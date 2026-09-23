import os
import re

preset_configs = {
    "XAUUSD_BACKTEST_1YEAR_OPTIMAL": {
        "InpBreakevenTriggerPips": "12.0",
        "InpBreakevenLockPips": "5.0",
        "InpTrailingStartPoints": "120.0",
        "InpTrailingDistPoints": "80.0",
        "InpTrailingStepPoints": "15.0",
        "InpCandleTrailBufferPoints": "30.0"
    },
    "XAUUSD_FAST_AUTO_TRADE": {
        "InpBreakevenTriggerPips": "8.0",
        "InpBreakevenLockPips": "4.5",
        "InpTrailingStartPoints": "100.0",
        "InpTrailingDistPoints": "70.0",
        "InpTrailingStepPoints": "15.0",
        "InpCandleTrailBufferPoints": "25.0"
    },
    "XAUUSD_HIGH_WINRATE_SNIPER": {
        "InpBreakevenTriggerPips": "8.0",
        "InpBreakevenLockPips": "5.0",
        "InpTrailingStartPoints": "120.0",
        "InpTrailingDistPoints": "80.0",
        "InpTrailingStepPoints": "15.0",
        "InpCandleTrailBufferPoints": "30.0"
    },
    "XAUUSD_M5_Scalping_Confluence": {
        "InpBreakevenTriggerPips": "12.0",
        "InpBreakevenLockPips": "5.0",
        "InpTrailingStartPoints": "120.0",
        "InpTrailingDistPoints": "80.0",
        "InpTrailingStepPoints": "15.0",
        "InpCandleTrailBufferPoints": "30.0"
    },
    "XAUUSD_M15_DayTrading_GradeA": {
        "InpBreakevenTriggerPips": "20.0",
        "InpBreakevenLockPips": "6.0",
        "InpTrailingStartPoints": "180.0",
        "InpTrailingDistPoints": "120.0",
        "InpTrailingStepPoints": "20.0",
        "InpCandleTrailBufferPoints": "40.0"
    }
}

target_dirs = [
    r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO",
    r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Presets",
    r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Profiles\Tester",
    r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_4Pillar_Pro"
]

updated_count = 0

for d in target_dirs:
    if not os.path.exists(d):
        continue
    for f in os.listdir(d):
        if not f.endswith(".set"):
            continue
        base_name = f.replace(".set", "")
        # Match config
        matched_cfg = None
        for k in preset_configs:
            if k in base_name:
                matched_cfg = preset_configs[k]
                break
        if not matched_cfg:
            continue

        fpath = os.path.join(d, f)
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()

            for param, val in matched_cfg.items():
                pattern = rf"^{param}=.*$"
                replacement = f"{param}={val}"
                if re.search(pattern, content, flags=re.MULTILINE):
                    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                else:
                    # Append if not exists
                    content += f"\n{replacement}"

            with open(fpath, "w", encoding="utf-8") as fh:
                fh.write(content)
            updated_count += 1
            print(f"[OK] Updated preset: {fpath}")
        except Exception as e:
            print(f"[ERR] Failed on {fpath}: {e}")

print(f"\nTotal preset files updated: {updated_count}")
