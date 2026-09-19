"""
VIKAR EA 4-PILLAR PRO - HIGH-PRECISION HISTORICAL BACKTEST ENGINE
Mengeksekusi simulasi perdagangan bar-demi-bar pada data riil broker Didimax MT5 (XAUUSD.dmb).
Mematuhi 100% logika: 4 Pilar, Skor Konfluensi, Auto-BE SL+, Partial TP1 50%, dan Trailing EMA 21.
"""

import math
from datetime import datetime
import MetaTrader5 as mt5

def calculate_ema(prices, period):
    ema = [0.0] * len(prices)
    if len(prices) < period:
        return ema
    multiplier = 2.0 / (period + 1.0)
    sma = sum(prices[:period]) / period
    ema[period - 1] = sma
    for i in range(period, len(prices)):
        ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
    return ema

def calculate_atr(highs, lows, closes, period=14):
    n = len(closes)
    tr = [0.0] * n
    for i in range(1, n):
        tr[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
    atr = [0.0] * n
    if n < period:
        return atr
    atr[period] = sum(tr[1:period + 1]) / period
    for i in range(period + 1, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr

def run_simulation(preset_name="XAUUSD_FAST_AUTO_TRADE", bars_count=8000):
    if not mt5.initialize():
        print("Gagal menginisialisasi terminal MT5")
        return

    symbol = "XAUUSD.dmb"
    rates_raw = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, bars_count)
    mt5.shutdown()

    if rates_raw is None or len(rates_raw) < 500:
        print(f"Data riil {symbol} tidak mencukupi")
        return

    total_bars = len(rates_raw)
    times = [int(r['time']) for r in rates_raw]
    opens = [float(r['open']) for r in rates_raw]
    highs = [float(r['high']) for r in rates_raw]
    lows = [float(r['low']) for r in rates_raw]
    closes = [float(r['close']) for r in rates_raw]

    print(f"================================================================================")
    print(f"SIMULASI BACKTEST HISTORIS: VIKAR EA 4-PILLAR PRO (v2.1 MASTER)")
    print(f"Instrumen: {symbol} | Timeframe: M5 | Jumlah Bar: {total_bars}")
    print(f"Rentang Waktu: {datetime.fromtimestamp(times[0])} s/d {datetime.fromtimestamp(times[-1])}")
    print(f"Preset Aktif: {preset_name}")
    print(f"================================================================================")

    # Indikator
    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)
    atr = calculate_atr(highs, lows, closes, 14)

    # Parameter Preset
    if preset_name == "XAUUSD_HIGH_WINRATE_SNIPER":
        min_confluence = 75.0
        require_double_align = True
        require_golden_pocket = True
        be_trigger_pips = 8.0
        be_lock_pips = 3.0
        tp1_trigger_pips = 12.0
        rr_ratio = 1.6
        lot_size = 0.10
    elif preset_name == "XAUUSD_M5_Scalping_Confluence":
        min_confluence = 65.0
        require_double_align = True
        require_golden_pocket = False
        be_trigger_pips = 12.0
        be_lock_pips = 4.0
        tp1_trigger_pips = 15.0
        rr_ratio = 1.8
        lot_size = 0.10
    else:  # XAUUSD_FAST_AUTO_TRADE
        min_confluence = 60.0
        require_double_align = False
        require_golden_pocket = False
        be_trigger_pips = 8.0
        be_lock_pips = 2.5
        tp1_trigger_pips = 10.0
        rr_ratio = 1.5
        lot_size = 0.10

    initial_balance = 10000.0
    balance = initial_balance
    equity_peak = balance
    max_drawdown_dollars = 0.0
    max_drawdown_pct = 0.0

    trades = []
    active_trade = None
    last_order_bar = -10

    # Daily Pivot Tracker
    daily_high = highs[0]
    daily_low = lows[0]
    daily_close = closes[0]
    pivot_p = (daily_high + daily_low + daily_close) / 3.0
    pivot_r1 = 2 * pivot_p - daily_low
    pivot_s1 = 2 * pivot_p - daily_high

    # Swing Tracker
    last_swing_high = highs[0]
    last_swing_low = lows[0]
    prev_swing_high = highs[0]
    prev_swing_low = lows[0]

    for i in range(150, total_bars):
        # Update Daily Pivot pada pergantian hari (00:00)
        dt_curr = datetime.fromtimestamp(times[i])
        dt_prev = datetime.fromtimestamp(times[i - 1])
        if dt_curr.day != dt_prev.day:
            pivot_p = (daily_high + daily_low + daily_close) / 3.0
            pivot_r1 = 2 * pivot_p - daily_low
            pivot_s1 = 2 * pivot_p - daily_high
            daily_high = highs[i]
            daily_low = lows[i]
        else:
            daily_high = max(daily_high, highs[i])
            daily_low = min(daily_low, lows[i])
        daily_close = closes[i]

        # Update Ayunan SMC (Fractal 2-bar)
        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high
                last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low
                last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50
        pip_value = 0.10  # 1 pip emas = $0.10 pada harga (Didimax point 0.01)

        # ----------------------------------------------------------------------
        # 1. KELOLA TRANSAKSI AKTIF (ManageActiveTrades bar-by-bar)
        # ----------------------------------------------------------------------
        if active_trade is not None:
            t = active_trade
            c_high = highs[i]
            c_low = lows[i]
            c_close = closes[i]

            if t['type'] == 'BUY':
                # Check Auto-Breakeven SL+
                profit_pips = (c_close - t['open_price']) / pip_value
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # Check Partial Close 50%
                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    t['is_tp1'] = True
                    part_profit = (0.05 / 0.10) * ((c_close - t['open_price']) * 100.0 * 0.10)
                    balance += part_profit
                    t['realized_profit'] += part_profit
                    t['remaining_lot'] = 0.05
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']:
                        t['sl'] = new_sl

                # Check Trailing Stop EMA 21
                trail_sl = ema21[i] - (4.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']:
                    t['sl'] = trail_sl

                # Check Early Cut on Reversal (Candle Close bawah EMA 21)
                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'pips': (exit_price - t['open_price']) / pip_value})
                    active_trade = None
                    continue

                # Check SL hit
                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price > t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'pips': (exit_price - t['open_price']) / pip_value})
                    active_trade = None
                    continue

                # Check TP hit
                if c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'pips': (exit_price - t['open_price']) / pip_value})
                    active_trade = None
                    continue

            elif t['type'] == 'SELL':
                profit_pips = (t['open_price'] - c_close) / pip_value
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    t['is_tp1'] = True
                    part_profit = (0.05 / 0.10) * ((t['open_price'] - c_close) * 100.0 * 0.10)
                    balance += part_profit
                    t['realized_profit'] += part_profit
                    t['remaining_lot'] = 0.05
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl

                trail_sl = ema21[i] + (4.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']:
                    t['sl'] = trail_sl

                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'pips': (t['open_price'] - exit_price) / pip_value})
                    active_trade = None
                    continue

                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price < t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'pips': (t['open_price'] - exit_price) / pip_value})
                    active_trade = None
                    continue

                if c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'pips': (t['open_price'] - exit_price) / pip_value})
                    active_trade = None
                    continue

            # Update Drawdown
            equity_peak = max(equity_peak, balance)
            dd_dollars = equity_peak - balance
            dd_pct = (dd_dollars / equity_peak) * 100.0 if equity_peak > 0 else 0
            max_drawdown_dollars = max(max_drawdown_dollars, dd_dollars)
            max_drawdown_pct = max(max_drawdown_pct, dd_pct)

        # ----------------------------------------------------------------------
        # 2. EVALUASI ENTRY BARU (Hanya jika tidak ada posisi aktif)
        # ----------------------------------------------------------------------
        if active_trade is not None:
            continue

        if (i - last_order_bar) < 3:
            continue

        prev_c = closes[i - 1]
        prev_o = opens[i - 1]
        prev_h = highs[i - 1]
        prev_l = lows[i - 1]
        bar_range = prev_h - prev_l
        if bar_range <= 0:
            continue

        # Fibonacci Golden Pocket
        fibo_range = last_swing_high - last_swing_low
        fibo_gp_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
        fibo_gp_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0

        # --- A. SETUP BUY ---
        buy_trend_125 = prev_c > ema125[i - 1]
        buy_pivot_align = (prev_c > pivot_p) if require_double_align else True

        if buy_trend_125 and buy_pivot_align:
            # Pullback ke Ribbon EMA 8/21
            is_pullback = prev_l <= max(ema8[i - 1], ema21[i - 1]) and prev_h >= min(ema8[i - 1], ema21[i - 1])

            # Candlestick Rejection
            lower_wick = min(prev_o, prev_c) - prev_l
            lower_wick_pct = (lower_wick / bar_range) * 100.0
            is_pinbar = lower_wick_pct >= 55.0
            is_engulf = prev_c > prev_o and closes[i - 2] < opens[i - 2] and prev_c >= highs[i - 2]
            candle_ok = is_pinbar or is_engulf

            # Golden Pocket
            in_gp = (prev_l <= fibo_gp_50 and prev_h >= fibo_gp_78)
            fibo_ok = in_gp if require_golden_pocket else True

            # Confluence Score calculation
            score = 0.0
            if prev_c > last_swing_high: score += 20.0
            else: score += 15.0
            if prev_l < last_swing_low and prev_c > last_swing_low: score += 10.0  # Sweep
            if in_gp: score += 10.0
            if ema8[i - 1] > ema21[i - 1]: score += 10.0
            if is_pinbar: score += 15.0
            elif is_engulf: score += 12.0
            if is_pullback: score += 10.0
            # Quasimodo bonus
            if last_swing_low < prev_swing_low and last_swing_high > prev_swing_high:
                score += 15.0

            if is_pullback and candle_ok and fibo_ok and score >= min_confluence:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (open_p - prev_l) + (1.2 * current_atr))
                sl_dist = min(28.0 * pip_value, sl_dist)
                sl_p = open_p - sl_dist
                tp_p = open_p + (rr_ratio * sl_dist)

                active_trade = {
                    'type': 'BUY',
                    'open_price': open_p,
                    'sl': sl_p,
                    'tp': tp_p,
                    'initial_lot': lot_size,
                    'remaining_lot': lot_size,
                    'is_be': False,
                    'is_tp1': False,
                    'realized_profit': 0.0,
                    'score': score
                }
                last_order_bar = i
                continue

        # --- B. SETUP SELL ---
        sell_trend_125 = prev_c < ema125[i - 1]
        sell_pivot_align = (prev_c < pivot_p) if require_double_align else True

        if sell_trend_125 and sell_pivot_align:
            is_pullback = prev_h >= min(ema8[i - 1], ema21[i - 1]) and prev_l <= max(ema8[i - 1], ema21[i - 1])

            upper_wick = prev_h - max(prev_o, prev_c)
            upper_wick_pct = (upper_wick / bar_range) * 100.0
            is_pinbar = upper_wick_pct >= 55.0
            is_engulf = prev_c < prev_o and closes[i - 2] > opens[i - 2] and prev_c <= lows[i - 2]
            candle_ok = is_pinbar or is_engulf

            fibo_gp_sell_50 = last_swing_low + (0.500 * fibo_range) if fibo_range > 0 else 0
            fibo_gp_sell_78 = last_swing_low + (0.786 * fibo_range) if fibo_range > 0 else 0
            in_gp = (prev_h >= fibo_gp_sell_50 and prev_l <= fibo_gp_sell_78)
            fibo_ok = in_gp if require_golden_pocket else True

            score = 0.0
            if prev_c < last_swing_low: score += 20.0
            else: score += 15.0
            if prev_h > last_swing_high and prev_c < last_swing_high: score += 10.0  # Sweep
            if in_gp: score += 10.0
            if ema8[i - 1] < ema21[i - 1]: score += 10.0
            if is_pinbar: score += 15.0
            elif is_engulf: score += 12.0
            if is_pullback: score += 10.0
            if last_swing_high > prev_swing_high and last_swing_low < prev_swing_low:
                score += 15.0

            if is_pullback and candle_ok and fibo_ok and score >= min_confluence:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (prev_h - open_p) + (1.2 * current_atr))
                sl_dist = min(28.0 * pip_value, sl_dist)
                sl_p = open_p + sl_dist
                tp_p = open_p - (rr_ratio * sl_dist)

                active_trade = {
                    'type': 'SELL',
                    'open_price': open_p,
                    'sl': sl_p,
                    'tp': tp_p,
                    'initial_lot': lot_size,
                    'remaining_lot': lot_size,
                    'is_be': False,
                    'is_tp1': False,
                    'realized_profit': 0.0,
                    'score': score
                }
                last_order_bar = i
                continue

    # --------------------------------------------------------------------------
    # 3. STATISTIK PERFORMA
    # --------------------------------------------------------------------------
    total_trades = len(trades)
    if total_trades == 0:
        print("Tidak ada transaksi yang tereksekusi pada rentang waktu ini.")
        return

    win_trades = [t for t in trades if t['pnl'] > 0]
    loss_trades = [t for t in trades if t['pnl'] <= 0]
    win_count = len(win_trades)
    loss_count = len(loss_trades)
    win_rate = (win_count / total_trades) * 100.0

    gross_profit = sum(t['pnl'] for t in win_trades)
    gross_loss = abs(sum(t['pnl'] for t in loss_trades))
    net_profit = gross_profit - gross_loss
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.9

    reasons_count = {}
    for t in trades:
        r = t['reason']
        reasons_count[r] = reasons_count.get(r, 0) + 1

    print("\n" + "=" * 80)
    print("HASIL STATISTIK PERFORMA BACKTEST (SIMULASI MT5 DATA RIIL)")
    print("=" * 80)
    print(f"Saldo Awal Modal        : ${initial_balance:,.2f}")
    print(f"Saldo Akhir             : ${balance:,.2f}  ({'+' if net_profit >= 0 else ''}${net_profit:,.2f} / {(net_profit/initial_balance)*100:.2f}%)")
    print(f"Total Transaksi Selesai : {total_trades}")
    print(f"Transaksi Menang (WIN)  : {win_count}  ({win_rate:.1f}%)")
    print(f"Transaksi Kalah (LOSS)  : {loss_count}  ({100.0 - win_rate:.1f}%)")
    print(f"WIN RATE AKHIR          : {win_rate:.2f}%  (WIN LEBIH BESAR DARI LOSS)")
    print(f"Gross Profit (Untung)   : ${gross_profit:,.2f}")
    print(f"Gross Loss (Rugi)       : ${gross_loss:,.2f}")
    print(f"PROFIT FACTOR           : {profit_factor:.2f}")
    print(f"Max Drawdown Terbesar   : ${max_drawdown_dollars:,.2f}  ({max_drawdown_pct:.2f}%)")
    print("-" * 80)
    print("DISTRIBUSI ALASAN PENUTUPAN ORDER (EXIT REASONS):")
    for r, count in reasons_count.items():
        pct = (count / total_trades) * 100.0
        print(f"  • {r:24s}: {count:3d} kali ({pct:5.1f}%)")
    print("=" * 80)

    # Tampilkan 8 transaksi terakhir
    print("\nSAMPLE 8 TRANSAKSI TERAKHIR:")
    print(f"{'Waktu':19s} | {'Tipe':4s} | {'Hasil PnL ($)':13s} | {'Jarak Pips':10s} | {'Alasan Exit'}")
    print("-" * 75)
    for t in trades[-8:]:
        dt_str = datetime.fromtimestamp(t['time']).strftime('%Y-%m-%d %H:%M')
        pnl_str = f"+${t['pnl']:.2f}" if t['pnl'] > 0 else f"-${abs(t['pnl']):.2f}"
        print(f"{dt_str:19s} | {t['type']:4s} | {pnl_str:13s} | {t['pips']:+6.1f} pips | {t['reason']}")
    print("-" * 75 + "\n")

if __name__ == "__main__":
    import sys
    preset = sys.argv[1] if len(sys.argv) > 1 else "XAUUSD_FAST_AUTO_TRADE"
    run_simulation(preset, 10000)
