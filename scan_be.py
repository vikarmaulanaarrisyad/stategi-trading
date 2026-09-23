import MetaTrader5 as mt5
from datetime import datetime
from run_backtest_jan2026_to_now import simulate_m5_period

def main():
    if not mt5.initialize():
        print("MT5 init failed")
        return

    rates = mt5.copy_rates_range("XAUUSD.dmb", mt5.TIMEFRAME_M5, datetime(2026, 1, 1), datetime(2026, 9, 21))
    mt5.shutdown()
    if rates is None:
        print("Rates none")
        return

    print("=" * 110)
    print(f"{'Preset':<15} | {'BE Trig':<8} | {'BE Lock':<8} | {'Trades':<6} | {'Win%':<6} | {'PF':<5} | {'Net Profit':<12} | {'Max DD%':<7} | {'TP Count':<8} | {'SL+ Count'}")
    print("-" * 110)

    for be in [10.0, 12.0, 14.0, 15.0, 16.0, 18.0, 20.0]:
        for lock in [3.0, 4.0, 5.0]:
            r = simulate_m5_period(rates, "XAUUSD_BACKTEST_1YEAR_OPTIMAL", {"be_trigger_pips": be, "be_lock_pips": lock})
            tp_c = r['exit_counts'].get('TAKE PROFIT (R:R)', 0)
            slp_c = r['exit_counts'].get('SL+ LOCK WIN', 0)
            print(f"{'OPTIMAL':<15} | {be:>6.1f} p | {lock:>6.1f} p | {r['total_trades']:<6} | {r['win_rate']:>5.1f}% | {r['profit_factor']:>4.2f} | ${r['net_profit']:>10.2f} | {r['max_dd_pct']:>6.2f}% | {tp_c:>8} | {slp_c:>8}")
    print("=" * 110)

    print("\n" + "=" * 110)
    print("SCAN FAST_AUTO_TRADE:")
    print(f"{'Preset':<15} | {'BE Trig':<8} | {'BE Lock':<8} | {'Trades':<6} | {'Win%':<6} | {'PF':<5} | {'Net Profit':<12} | {'Max DD%':<7} | {'TP Count':<8} | {'SL+ Count'}")
    print("-" * 110)
    for be in [8.0, 10.0, 12.0, 14.0, 15.0, 16.0]:
        for lock in [2.5, 3.5, 4.5]:
            r = simulate_m5_period(rates, "XAUUSD_FAST_AUTO_TRADE", {"be_trigger_pips": be, "be_lock_pips": lock})
            tp_c = r['exit_counts'].get('TAKE PROFIT (R:R)', 0)
            slp_c = r['exit_counts'].get('SL+ LOCK WIN', 0)
            print(f"{'FAST_AUTO':<15} | {be:>6.1f} p | {lock:>6.1f} p | {r['total_trades']:<6} | {r['win_rate']:>5.1f}% | {r['profit_factor']:>4.2f} | ${r['net_profit']:>10.2f} | {r['max_dd_pct']:>6.2f}% | {tp_c:>8} | {slp_c:>8}")
    print("=" * 110)

    print("\n" + "=" * 110)
    print("SCAN HIGH_WINRATE_SNIPER:")
    print(f"{'Preset':<15} | {'BE Trig':<8} | {'BE Lock':<8} | {'Trades':<6} | {'Win%':<6} | {'PF':<5} | {'Net Profit':<12} | {'Max DD%':<7} | {'TP Count':<8} | {'SL+ Count'}")
    print("-" * 110)
    for be in [8.0, 10.0, 12.0, 14.0]:
        for lock in [3.0, 4.0, 5.0]:
            r = simulate_m5_period(rates, "XAUUSD_HIGH_WINRATE_SNIPER", {"be_trigger_pips": be, "be_lock_pips": lock})
            tp_c = r['exit_counts'].get('TAKE PROFIT (R:R)', 0)
            slp_c = r['exit_counts'].get('SL+ LOCK WIN', 0)
            print(f"{'SNIPER':<15} | {be:>6.1f} p | {lock:>6.1f} p | {r['total_trades']:<6} | {r['win_rate']:>5.1f}% | {r['profit_factor']:>4.2f} | ${r['net_profit']:>10.2f} | {r['max_dd_pct']:>6.2f}% | {tp_c:>8} | {slp_c:>8}")
    print("=" * 110)

if __name__ == '__main__':
    main()
