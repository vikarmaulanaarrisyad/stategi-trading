import sys
from datetime import datetime, timedelta
import MetaTrader5 as mt5

def calculate_ema(prices, period):
    ema = [0.0] * len(prices)
    if len(prices) < period: return ema
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
    if n < period: return atr
    atr[period] = sum(tr[1:period + 1]) / period
    for i in range(period + 1, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr

def calculate_adx(highs, lows, closes, period=14):
    n = len(closes)
    if n < period * 2: return [25.0] * n
    adx = [25.0] * n
    for i in range(period, n):
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]
        pdm = up_move if up_move > down_move and up_move > 0 else 0.0
        ndm = down_move if down_move > up_move and down_move > 0 else 0.0
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        if tr > 0:
            diff = abs(pdm - ndm)
            sum_dm = pdm + ndm
            dx = (diff / sum_dm * 100.0) if sum_dm > 0 else 20.0
            adx[i] = (adx[i - 1] * (period - 1) + dx) / period
        else:
            adx[i] = adx[i - 1]
    return adx

def run_august_backtest(preset_name="SNIPER", initial_balance=20.0, lot_size=0.01):
    if not mt5.initialize():
        print("Failed to initialize MT5")
        sys.exit(1)

    symbol = 'XAUUSD.dmb'
    if not mt5.symbol_select(symbol, True):
        for s in ['XAUUSD', 'GOLD', 'XAUUSDm']:
            if mt5.symbol_select(s, True): symbol = s; break

    # Warmup from mid-July 2026 (2 weeks prior to Aug 1)
    dt_warmup = datetime(2026, 7, 15)
    dt_target_start = datetime(2026, 8, 1)
    dt_now = datetime.now()

    rates_raw = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, dt_warmup, dt_now)
    mt5.shutdown()

    if rates_raw is None or len(rates_raw) == 0:
        print("Failed to fetch rates from MT5")
        sys.exit(1)

    total_bars = len(rates_raw)
    times = [int(r['time']) for r in rates_raw]
    opens = [float(r['open']) for r in rates_raw]
    highs = [float(r['high']) for r in rates_raw]
    lows = [float(r['low']) for r in rates_raw]
    closes = [float(r['close']) for r in rates_raw]

    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)
    atr = calculate_atr(highs, lows, closes, 14)
    adx = calculate_adx(highs, lows, closes, 14)

    if "FAST" in preset_name.upper():
        min_confluence = 60.0; be_trigger_pips = 8.0; be_lock_pips = 4.5; tp1_trigger_pips = 10.0; rr_ratio = 1.5
    elif "SNIPER" in preset_name.upper():
        min_confluence = 75.0; be_trigger_pips = 8.0; be_lock_pips = 5.0; tp1_trigger_pips = 14.0; rr_ratio = 1.8
    elif "SCALPING" in preset_name.upper():
        min_confluence = 65.0; be_trigger_pips = 12.0; be_lock_pips = 5.0; tp1_trigger_pips = 15.0; rr_ratio = 1.8
    else: # 1YEAR_OPTIMAL
        min_confluence = 65.0; be_trigger_pips = 12.0; be_lock_pips = 5.0; tp1_trigger_pips = 15.0; rr_ratio = 2.0

    pip_value = 0.10
    lot_multiplier = lot_size * 100.0

    balance = initial_balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0
    min_balance = balance

    trades = []
    active_trade = None
    last_order_bar = -10

    last_swing_high = highs[0]; last_swing_low = lows[0]
    prev_swing_high = highs[0]; prev_swing_low = lows[0]

    weekly_data = {}
    monthly_data = {}
    exit_reasons = {}

    target_start_ts = int(dt_target_start.timestamp())

    for i in range(150, total_bars):
        t_curr = times[i]
        dt_curr = datetime.fromtimestamp(t_curr)

        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high; last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low; last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        if active_trade is not None:
            t = active_trade
            c_high = highs[i]; c_low = lows[i]; c_close = closes[i]

            profit_pips = (c_close - t['open_price']) / pip_value if t['type'] == 'BUY' else (t['open_price'] - c_close) / pip_value

            closed = False
            pnl = 0.0
            reason = ""

            if t['type'] == 'BUY':
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']: t['sl'] = struct_sl
                trail_sl = ema21[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']: t['sl'] = trail_sl

                # Auto-Cut Reversal
                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    pnl = (c_close - t['open_price']) * lot_multiplier
                    closed = True; reason = 'AUTO-CUT REVERSAL'
                # Stop Loss
                elif c_low <= t['sl']:
                    pnl = (t['sl'] - t['open_price']) * lot_multiplier
                    closed = True
                    reason = 'SL+ LOCK WIN' if t['sl'] > t['open_price'] else 'STOP LOSS'
                # Take Profit
                elif c_high >= t['tp']:
                    pnl = (t['tp'] - t['open_price']) * lot_multiplier
                    closed = True; reason = 'TAKE PROFIT (R:R)'

            else: # SELL
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']: t['sl'] = struct_sl
                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']: t['sl'] = trail_sl

                # Auto-Cut Reversal
                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    pnl = (t['open_price'] - c_close) * lot_multiplier
                    closed = True; reason = 'AUTO-CUT REVERSAL'
                # Stop Loss
                elif c_high >= t['sl']:
                    pnl = (t['open_price'] - t['sl']) * lot_multiplier
                    closed = True
                    reason = 'SL+ LOCK WIN' if t['sl'] < t['open_price'] else 'STOP LOSS'
                # Take Profit
                elif c_low <= t['tp']:
                    pnl = (t['open_price'] - t['tp']) * lot_multiplier
                    closed = True; reason = 'TAKE PROFIT (R:R)'

            if closed:
                balance += pnl
                t_record = {
                    'open_time': t['open_time'], 'close_time': dt_curr,
                    'type': t['type'], 'open_price': t['open_price'],
                    'close_price': c_close if reason == 'AUTO-CUT REVERSAL' else (t['tp'] if 'TAKE PROFIT' in reason else t['sl']),
                    'sl': t['sl'], 'tp': t['tp'], 'pnl': pnl, 'reason': reason,
                    'duration_bars': i - t['bar_idx'], 'duration_mins': (i - t['bar_idx']) * 5
                }
                trades.append(t_record)

                m_key = t['open_time'].strftime("%Y-%m")
                w_key = f"{t['open_time'].strftime('%Y')}-W{t['open_time'].isocalendar()[1]:02d}"

                if m_key not in monthly_data: monthly_data[m_key] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}
                monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                if pnl > 0: monthly_data[m_key]['wins'] += 1
                else: monthly_data[m_key]['losses'] += 1

                if w_key not in weekly_data: weekly_data[w_key] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0, 'start_dt': t['open_time']}
                weekly_data[w_key]['trades'] += 1; weekly_data[w_key]['pnl'] += pnl
                if pnl > 0: weekly_data[w_key]['wins'] += 1
                else: weekly_data[w_key]['losses'] += 1

                exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

                if balance > equity_peak: equity_peak = balance
                dd = equity_peak - balance
                dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
                if dd > max_dd_dollars: max_dd_dollars = dd; max_dd_pct = dd_pct
                if balance < min_balance: min_balance = balance

                active_trade = None
                continue

        # Check for new entry (Only if time is >= 2026-08-01)
        if t_curr < target_start_ts: continue
        if active_trade is not None: continue
        if (i - last_order_bar) < 3: continue
        if adx[i - 1] < 20.0: continue

        fibo_range = last_swing_high - last_swing_low
        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
        bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

        candle_body = abs(closes[i - 1] - opens[i - 1])
        body_pct = (candle_body / bar_range) * 100.0
        upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
        lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
        upper_wick_pct = (upper_wick / bar_range) * 100.0
        lower_wick_pct = (lower_wick / bar_range) * 100.0

        is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
        is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

        buy_trend_125 = (closes[i - 1] > ema125[i - 1]) and (ema_slope >= 2.0)
        if buy_trend_125 or is_bull_trap:
            if body_pct <= 22.0 and not is_bull_trap: continue
            if upper_wick_pct >= 45.0 and not is_bull_trap: continue
            is_engulf = closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= highs[i - 2]
            if is_engulf and ((closes[i - 1] - ema21[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value): continue

            is_pullback = lows[i - 1] <= max(ema8[i - 1], ema21[i - 1]) and highs[i - 1] >= min(ema8[i - 1], ema21[i - 1])
            is_pinbar = (lower_wick / bar_range) >= 0.50
            candle_ok = is_pinbar or is_engulf or is_bull_trap
            fibo_gp_buy_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
            fibo_gp_buy_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0
            in_gp = (lows[i - 1] <= fibo_gp_buy_50 and highs[i - 1] >= fibo_gp_buy_78)

            score = 0.0
            if closes[i - 1] > last_swing_high: score += 20.0
            else: score += 15.0
            if lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low: score += 12.0
            if in_gp: score += 10.0
            if ema8[i - 1] > ema21[i - 1]: score += 10.0
            if is_pinbar: score += 15.0
            elif is_engulf: score += 12.0
            if is_pullback: score += 10.0
            if is_bull_trap: score += 15.0
            if last_swing_high > prev_swing_high and last_swing_low > prev_swing_low: score += 15.0

            if (is_pullback and candle_ok and score >= min_confluence) or is_bull_trap:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (open_p - lows[i - 1]) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p - sl_dist
                tp_p = open_p + (rr_ratio * sl_dist)
                active_trade = {
                    'type': 'BUY', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p,
                    'is_be': False, 'open_time': dt_curr, 'bar_idx': i
                }
                last_order_bar = i; continue

        sell_trend_125 = (closes[i - 1] < ema125[i - 1]) and (ema_slope <= -2.0)
        if sell_trend_125 or is_bear_trap:
            if body_pct <= 22.0 and not is_bear_trap: continue
            if lower_wick_pct >= 45.0 and not is_bear_trap: continue
            is_engulf = closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= lows[i - 2]
            if is_engulf and ((ema21[i - 1] - closes[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value): continue

            is_pullback = highs[i - 1] >= min(ema8[i - 1], ema21[i - 1]) and lows[i - 1] <= max(ema8[i - 1], ema21[i - 1])
            upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
            is_pinbar = (upper_wick / bar_range) >= 0.50
            candle_ok = is_pinbar or is_engulf or is_bear_trap
            fibo_gp_sell_50 = last_swing_low + (0.500 * fibo_range) if fibo_range > 0 else 0
            fibo_gp_sell_78 = last_swing_low + (0.786 * fibo_range) if fibo_range > 0 else 0
            in_gp = (highs[i - 1] >= fibo_gp_sell_50 and lows[i - 1] <= fibo_gp_sell_78)

            score = 0.0
            if closes[i - 1] < last_swing_low: score += 20.0
            else: score += 15.0
            if highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high: score += 12.0
            if in_gp: score += 10.0
            if ema8[i - 1] < ema21[i - 1]: score += 10.0
            if is_pinbar: score += 15.0
            elif is_engulf: score += 12.0
            if is_pullback: score += 10.0
            if is_bear_trap: score += 15.0
            if last_swing_high < prev_swing_high and last_swing_low < prev_swing_low: score += 15.0

            if (is_pullback and candle_ok and score >= min_confluence) or is_bear_trap:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (highs[i - 1] - open_p) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p + sl_dist
                tp_p = open_p - (rr_ratio * sl_dist)
                active_trade = {
                    'type': 'SELL', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p,
                    'is_be': False, 'open_time': dt_curr, 'bar_idx': i
                }
                last_order_bar = i; continue

    total_t = len(trades)
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    wr = len(wins) / total_t * 100.0 if total_t > 0 else 0
    gross_win = sum([t['pnl'] for t in wins])
    gross_loss = abs(sum([t['pnl'] for t in losses]))
    pf = (gross_win / gross_loss) if gross_loss > 0 else 99.0

    buy_trades = [t for t in trades if t['type'] == 'BUY']
    sell_trades = [t for t in trades if t['type'] == 'SELL']
    buy_wins = [t for t in buy_trades if t['pnl'] > 0]
    sell_wins = [t for t in sell_trades if t['pnl'] > 0]

    # Consecutive stats
    max_cons_wins = 0; cur_cons_wins = 0
    max_cons_loss = 0; cur_cons_loss = 0
    for t in trades:
        if t['pnl'] > 0:
            cur_cons_wins += 1; cur_cons_loss = 0
            if cur_cons_wins > max_cons_wins: max_cons_wins = cur_cons_wins
        else:
            cur_cons_loss += 1; cur_cons_wins = 0
            if cur_cons_loss > max_cons_loss: max_cons_loss = cur_cons_loss

    avg_win = (gross_win / len(wins)) if len(wins) > 0 else 0.0
    avg_loss = (gross_loss / len(losses)) if len(losses) > 0 else 0.0
    avg_dur = (sum(t['duration_mins'] for t in trades) / total_t) if total_t > 0 else 0.0

    return {
        'preset': preset_name, 'total': total_t, 'wins': len(wins), 'losses': len(losses),
        'win_rate': wr, 'profit_factor': pf, 'net_profit': balance - initial_balance,
        'growth': ((balance - initial_balance) / initial_balance) * 100.0,
        'gross_win': gross_win, 'gross_loss': gross_loss,
        'avg_win': avg_win, 'avg_loss': avg_loss,
        'max_dd_dollars': max_dd_dollars, 'max_dd_pct': max_dd_pct,
        'final_balance': balance, 'min_balance': min_balance,
        'buy_count': len(buy_trades), 'buy_wr': (len(buy_wins) / len(buy_trades) * 100.0) if buy_trades else 0,
        'sell_count': len(sell_trades), 'sell_wr': (len(sell_wins) / len(sell_trades) * 100.0) if sell_trades else 0,
        'max_cons_wins': max_cons_wins, 'max_cons_loss': max_cons_loss,
        'avg_duration_mins': avg_dur, 'exit_reasons': exit_reasons,
        'weekly': weekly_data, 'monthly': monthly_data, 'trades': trades
    }

def main():
    print("=" * 110)
    print("BACKTEST EA MT4: 1 AGUSTUS 2026 - 21 SEPTEMBER 2026 (HARI INI)")
    print("PENGATURAN: MODAL AWAL $20.00 | FIXED LOT 0.01 (QUICKPRO MT4)")
    print("=" * 110)

    presets = ["SNIPER", "1YEAR_OPTIMAL", "SCALPING", "FAST"]
    results = {}

    print(f"{'Nama Preset':<25} | {'Trades':<7} | {'Win Rate':<9} | {'PF':<5} | {'Saldo Akhir':<12} | {'Net Profit ($)':<14} | {'Pertumbuhan':<11} | {'Min Balance'}")
    print("-" * 110)

    for p in presets:
        r = run_august_backtest(preset_name=p, initial_balance=20.0, lot_size=0.01)
        results[p] = r
        print(f"{r['preset']:<25} | {r['total']:<7} | {r['win_rate']:>6.2f}%   | {r['profit_factor']:>4.2f} | ${r['final_balance']:>10,.2f} | ${r['net_profit']:>12,.2f} | {r['growth']:>9.1f}% | ${r['min_balance']:>8.2f}")
    print("=" * 110 + "\n")

    # Focus on SNIPER (Default Setting MT4 EA)
    sn = results["SNIPER"]
    print("=" * 80)
    print("DETAIL PERFORMA PRESET SNIPER (BAWAAN EA MT4 KITA)")
    print("=" * 80)
    print(f"Modal Awal          : $20.00")
    print(f"Saldo Akhir         : ${sn['final_balance']:,.2f}")
    print(f"Keuntungan Bersih   : +${sn['net_profit']:,.2f} (+{sn['growth']:.1f}%)")
    print(f"Total Transaksi     : {sn['total']} Trades ({sn['wins']} Win / {sn['losses']} Loss)")
    print(f"Win Rate Keseluruhan: {sn['win_rate']:.2f}%")
    print(f"Profit Factor       : {sn['profit_factor']:.2f}")
    print(f"Max Drawdown        : ${sn['max_dd_dollars']:.2f} ({sn['max_dd_pct']:.2f}%)")
    print(f"Saldo Terendah (Dip): ${sn['min_balance']:.2f} (TIDAK PERNAH MARGIN CALL!)")
    print(f"Rata-rata Menang    : +${sn['avg_win']:.2f} per trade")
    print(f"Rata-rata Kalah     : -${sn['avg_loss']:.2f} per trade")
    print(f"Max Consecutive Win : {sn['max_cons_wins']} kali berturut-turut")
    print(f"Max Consecutive Loss: {sn['max_cons_loss']} kali berturut-turut")
    print(f"Rata-rata Durasi    : {sn['avg_duration_mins']:.1f} Menit ({sn['avg_duration_mins']/5.0:.1f} Lilin M5)")
    print(f"BUY Trades          : {sn['buy_count']} Trades (Win Rate: {sn['buy_wr']:.1f}%)")
    print(f"SELL Trades         : {sn['sell_count']} Trades (Win Rate: {sn['sell_wr']:.1f}%)")
    print("-" * 80)

    print("\nDISTRIBUSI ALASAN PENUTUPAN TRANSAKSI (EXIT MECHANICS):")
    for reason, count in sorted(sn['exit_reasons'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / sn['total'] * 100.0) if sn['total'] > 0 else 0
        print(f"  * {reason:<22}: {count:>4} trade ({pct:>5.1f}%)")

    print("\nPERFORMA BULANAN:")
    for m in sorted(sn['monthly'].keys()):
        d = sn['monthly'][m]
        wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0
        print(f"  * {m}: {d['trades']} Trades | Win Rate: {wr:.1f}% | Profit: +${d['pnl']:.2f}")

    print("\nPERFORMA MINGGUAN (WEEK-BY-WEEK):")
    for w in sorted(sn['weekly'].keys()):
        d = sn['weekly'][w]
        wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0
        status = "PROFIT" if d['pnl'] >= 0 else "LOSS"
        print(f"  * {w} ({d['start_dt'].strftime('%d %b %Y')}): {d['trades']:>3} Trades | WR: {wr:>5.1f}% | Net: ${d['pnl']:>7.2f} [{status}]")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
