import sys
from datetime import datetime
import numpy as np
import MetaTrader5 as mt5

if not mt5.initialize():
    print("MT5 initialization failed")
    sys.exit()

symbol = 'XAUUSD.dmb'
if not mt5.symbol_select(symbol, True):
    for s in ['XAUUSD', 'GOLD', 'XAUUSDm']:
        if mt5.symbol_select(s, True): symbol = s; break

print(f"Using symbol: {symbol}", flush=True)

# 1. Fetch native M5 bars
from datetime import timedelta
d_cur = datetime(2025, 4, 14)
d_end = datetime(2026, 9, 21)

native_m5 = {}
cur = d_cur
while cur < d_end:
    nxt = min(cur + timedelta(days=30), d_end)
    r = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, cur, nxt)
    if r is not None and len(r) > 0:
        for b in r:
            t = int(b['time'])
            if t >= int(cur.timestamp()) and t < int(nxt.timestamp()):
                native_m5[t] = {
                    'time': t, 'open': float(b['open']), 'high': float(b['high']),
                    'low': float(b['low']), 'close': float(b['close']), 'tick_volume': int(b['tick_volume'])
                }
    cur = nxt

sorted_native = [native_m5[t] for t in sorted(native_m5.keys())]
first_native_time = sorted_native[0]['time']
print(f"Native M5 bars collected: {len(sorted_native)} (from {datetime.fromtimestamp(first_native_time)} to {datetime.fromtimestamp(sorted_native[-1]['time'])})", flush=True)

# 2. Fetch M15 bars prior to first native M5 bar
print("Fetching M15 bars...", flush=True)
r_m15 = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, datetime(2025, 1, 1), datetime(2025, 4, 15))
print(f"M15 bars returned: {len(r_m15) if r_m15 is not None else 0}", flush=True)
mt5.shutdown()

prior_m5 = []
if r_m15 is not None and len(r_m15) > 0:
    print(f"M15 bars prior to native M5: {len(r_m15)} (from {datetime.fromtimestamp(int(r_m15[0]['time']))} to {datetime.fromtimestamp(int(r_m15[-1]['time']))})")
    for b in r_m15:
        t0 = int(b['time'])
        o = float(b['open'])
        h = float(b['high'])
        l = float(b['low'])
        c = float(b['close'])
        v = int(b['tick_volume']) // 3

        # Realistic 3-bar subdivision
        # If bullish (close >= open), first sub-bar tends to dip or move towards low, second towards high, third towards close
        if c >= o:
            # Bar 1 (0m - 5m)
            b1_o = o
            b1_l = l + 0.3 * (o - l) if o > l else l
            b1_c = o + 0.4 * (c - o)
            b1_h = max(b1_o, b1_c)
            prior_m5.append({'time': t0, 'open': b1_o, 'high': b1_h, 'low': b1_l, 'close': b1_c, 'tick_volume': v})

            # Bar 2 (5m - 10m)
            b2_o = b1_c
            b2_h = h
            b2_l = min(b2_o, b1_l)
            b2_c = o + 0.8 * (c - o)
            prior_m5.append({'time': t0 + 300, 'open': b2_o, 'high': b2_h, 'low': b2_l, 'close': b2_c, 'tick_volume': v})

            # Bar 3 (10m - 15m)
            b3_o = b2_c
            b3_h = max(b3_o, h)
            b3_l = min(b3_o, c)
            b3_c = c
            prior_m5.append({'time': t0 + 600, 'open': b3_o, 'high': b3_h, 'low': b3_l, 'close': b3_c, 'tick_volume': v})
        else:
            # Bearish bar
            b1_o = o
            b1_h = o + 0.3 * (h - o) if h > o else h
            b1_c = o - 0.4 * (o - c)
            b1_l = min(b1_o, b1_c)
            prior_m5.append({'time': t0, 'open': b1_o, 'high': b1_h, 'low': b1_l, 'close': b1_c, 'tick_volume': v})

            b2_o = b1_c
            b2_l = l
            b2_h = max(b2_o, b1_h)
            b2_c = o - 0.8 * (o - c)
            prior_m5.append({'time': t0 + 300, 'open': b2_o, 'high': b2_h, 'low': b2_l, 'close': b2_c, 'tick_volume': v})

            b3_o = b2_c
            b3_l = min(b3_o, l)
            b3_h = max(b3_o, c)
            b3_c = c
            prior_m5.append({'time': t0 + 600, 'open': b3_o, 'high': b3_h, 'low': b3_l, 'close': b3_c, 'tick_volume': v})

full_dataset = prior_m5 + sorted_native
print(f"\n=======================================================")
print(f"FULL COMBINED M5 DATASET (JANUARI 2025 - SEPTEMBER 2026)")
print(f"Total M5 Bars: {len(full_dataset):,}")
print(f"First Bar: {datetime.fromtimestamp(full_dataset[0]['time'])}")
print(f"Last Bar:  {datetime.fromtimestamp(full_dataset[-1]['time'])}")
print(f"=======================================================")
