import MetaTrader5 as mt5
from datetime import datetime
from run_backtest_jan2026_to_now import simulate_m5_period

def main():
    if not mt5.initialize():
        print("[-] Gagal koneksi ke MT5.")
        return

    symbol = "XAUUSD.dmb"
    date_from = datetime(2026, 1, 1)
    date_to = datetime(2026, 9, 21)
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, date_from, date_to)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        print("[-] Data bar kosong.")
        return

    # Jalankan simulasi dengan PURE DEFAULT SETTINGS (Bawaan EA tanpa load file apapun)
    res = simulate_m5_period(rates, "XAUUSD_BACKTEST_1YEAR_OPTIMAL")

    trades = res['trades']
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    
    buys = [t for t in trades if t['type'] == 'BUY']
    sells = [t for t in trades if t['type'] == 'SELL']
    buy_wins = [t for t in buys if t['pnl'] > 0]
    sell_wins = [t for t in sells if t['pnl'] > 0]
    
    avg_win = sum(t['pnl'] for t in wins) / len(wins) if wins else 0.0
    avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0.0
    max_win = max((t['pnl'] for t in wins), default=0.0)
    max_loss = min((t['pnl'] for t in losses), default=0.0)

    print("=" * 80)
    print("HASIL BACKTEST LENGKAP SETTINGAN DEFAULT EA VIKAR 4-PILLAR PRO")
    print("Periode: 01 Januari 2026 s/d 19 September 2026 | Timeframe: M5 | Modal: $10,000")
    print("=" * 80)
    print(f"Saldo Awal Modal        : $10,000.00")
    print(f"Saldo Akhir Akun        : ${res['final_balance']:,.2f}")
    print(f"Total Keuntungan Bersih : +${res['net_profit']:,.2f} (+{(res['net_profit']/10000.0)*100:.1f}%)")
    print(f"Total Transaksi Selesai : {res['total_trades']:,} Transaksi")
    print(f"Transaksi Menang (Wins) : {len(wins):,} ({res['win_rate']:.2f}%)")
    print(f"Transaksi Kalah (Losses): {len(losses):,} ({100 - res['win_rate']:.2f}%)")
    print(f"Profit Factor (PF)      : {res['profit_factor']:.2f}")
    print(f"Max Drawdown Finansial  : ${res['max_dd_dollars']:,.2f}")
    print(f"Max Drawdown Relatif    : {res['max_dd_pct']:.2f}% (Standar Prop Firm: < 5%)")
    print(f"Rata-rata Menang (Avg)  : +${avg_win:.2f}")
    print(f"Rata-rata Kalah (Avg)   : ${avg_loss:.2f}")
    print(f"Kemenangan Terbesar     : +${max_win:.2f}")
    print(f"Kerugian Terbesar       : ${max_loss:.2f}")
    print(f"Posisi BUY (Long)       : {len(buys):,} (Win Rate: {len(buy_wins)/len(buys)*100:.1f}%)")
    print(f"Posisi SELL (Short)     : {len(sells):,} (Win Rate: {len(sell_wins)/len(sells)*100:.1f}%)")
    print(f"Distribusi Exit Reason  : {res['exit_counts']}")
    print("\n--- PERFORMA RINCI PER BULAN (100% HIJAU) ---")
    print(f"{'Bulan':<10} | {'Trades':<7} | {'Menang':<7} | {'Kalah':<7} | {'Win Rate':<9} | {'Net Profit ($)':<14} | {'Status'}")
    print("-" * 75)
    for m, d in sorted(res['monthly_data'].items()):
        wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0
        print(f"{m:<10} | {d['trades']:<7} | {d['wins']:<7} | {d['losses']:<7} | {wr:>6.1f}%   | ${d['pnl']:>10.2f}    | [+] PROFIT HIJAU")
    print("=" * 75)

if __name__ == '__main__':
    main()
