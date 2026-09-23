import sys
import os
import MetaTrader5 as mt5
sys.path.insert(0, os.path.dirname(__file__))
from test_compare_entry import run_backtest_mode

def main():
    if not mt5.initialize():
        print("Failed MT5 init")
        return
    rates = mt5.copy_rates_from_pos('XAUUSD.dmb', mt5.TIMEFRAME_M5, 0, 15000)
    mt5.shutdown()

    modes = [
        ('1. Market Direct (All)', {'type': 'MARKET'}),
        ('2. Limit Pullback 5p', {'type': 'LIMIT', 'method': 'FIXED_PIPS', 'offset_pips': 5.0, 'expiry_bars': 4}),
        ('3. Limit Mid-Candle (50%)', {'type': 'LIMIT', 'method': 'MID_CANDLE', 'expiry_bars': 4}),
        ('4. Stop Breakout 2p', {'type': 'STOP', 'buffer_pips': 2.0, 'expiry_bars': 4}),
        ('5. Stop Breakout 4p', {'type': 'STOP', 'buffer_pips': 4.0, 'expiry_bars': 4}),
    ]

    print("=" * 95)
    print("HASIL PENGUJIAN LENGKAP ENTRY MODES PADA XAUUSD M5 (15.000 BARS):")
    print("=" * 95)
    for name, cfg in modes:
        res = run_backtest_mode(name, rates, cfg)
        wr = res['win_rate']
        pf = res['profit_factor']
        pnl = res['net_profit']
        dd = res['max_dd_pct']
        filled = res['filled']
        sig = res['signals']
        fill_pct = res['fill_rate']
        print(f"{name:<30} | Filled: {filled:>3}/{sig:>3} ({fill_pct:>5.1f}%) | WR: {wr:>5.2f}% | PF: {pf:>4.2f} | Net: ${pnl:>8.2f} | DD: {dd:>5.2f}%")
    print("=" * 95)

if __name__ == '__main__':
    main()
