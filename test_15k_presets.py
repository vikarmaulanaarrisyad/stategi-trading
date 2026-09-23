"""
Testing the complete optimized settings:
1. Entry Mode: Pending Stop Breakout (2p buffer)
2. Breakeven Trigger: 12 pips, Lock: 4 pips
3. Partial Close: 15 pips (50%) + lock SL+
4. R:R Ratio: 2.0 (TP at 2x SL risk)
5. Spread filter: Max 6 pips
6. Session: European & US active (08:00 - 23:00 broker)
"""

import MetaTrader5 as mt5
from datetime import datetime
from run_backtest_v300 import calculate_ema, calculate_atr, calculate_adx, simulate_strategy

if not mt5.initialize():
    print("[-] MT5 failed")
    exit()

print("[+] Running backtest on 15,000 M5 bars of XAUUSD.dmb...")
rates = mt5.copy_rates_from_pos("XAUUSD.dmb", mt5.TIMEFRAME_M5, 0, 15000)
mt5.shutdown()

res = simulate_strategy(rates, "XAUUSD_BACKTEST_1YEAR_OPTIMAL")
print(f"Standard Optimal Preset (15,000 bars):")
print(f"Total Trades: {res['total_trades']}")
print(f"Win Rate    : {res['win_rate']:.2f}%")
print(f"Profit      : ${res['net_profit']:.2f}")
print(f"P.Factor    : {res['profit_factor']:.2f}")
print(f"Max DD      : {res['max_dd_pct']:.2f}%")

res_sniper = simulate_strategy(rates, "XAUUSD_HIGH_WINRATE_SNIPER")
print(f"\nSniper Preset (15,000 bars):")
print(f"Total Trades: {res_sniper['total_trades']}")
print(f"Win Rate    : {res_sniper['win_rate']:.2f}%")
print(f"Profit      : ${res_sniper['net_profit']:.2f}")
print(f"P.Factor    : {res_sniper['profit_factor']:.2f}")
print(f"Max DD      : {res_sniper['max_dd_pct']:.2f}%")
