import MetaTrader5 as mt5
from datetime import datetime
from run_backtest_jan2026_to_now import calculate_ema, calculate_atr, calculate_adx

def test_be_variations():
    if not mt5.initialize():
        print("MT5 init failed")
        return

    rates_raw = mt5.copy_rates_range("XAUUSD.dmb", mt5.TIMEFRAME_M5, datetime(2026, 1, 1), datetime(2026, 9, 21))
    mt5.shutdown()
    if rates_raw is None:
        print("Rates none")
        return

    print(f"Loaded {len(rates_raw):,} M5 bars.")

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

    pip_value = 0.10

    test_configs = [
        {"name": "BE 10p / Lock 3p", "be_trig": 10.0, "be_lock": 3.0, "tp1": 15.0},
        {"name": "BE 12p / Lock 4p (Current)", "be_trig": 12.0, "be_lock": 4.0, "tp1": 15.0},
        {"name": "BE 14p / Lock 4p", "be_trig": 14.0, "be_lock": 4.0, "tp1": 16.0},
        {"name": "BE 16p / Lock 5p", "be_trig": 16.0, "be_lock": 5.0, "tp1": 18.0},
        {"name": "BE 18p / Lock 5p", "be_trig": 18.0, "be_lock": 5.0, "tp1": 20.0},
        {"name": "BE 20p / Lock 5p", "be_trig": 20.0, "be_lock": 5.0, "tp1": 22.0},
    ]

    print("\n" + "=" * 95)
    print(f"{'Config Name':<28} | {'Trades':<6} | {'Win%':<7} | {'PF':<5} | {'Net Profit':<11} | {'Max DD%':<7} | {'Exit Dist'}")
    print("-" * 95)

    for cfg in test_configs:
        be_trigger_pips = cfg['be_trig']
        be_lock_pips = cfg['be_lock']
        tp1_trigger_pips = cfg['tp1']
        rr_ratio = 2.0
        min_confluence = 65.0
        require_double_align = False
        require_golden_pocket = False
        base_lot = 0.10

        initial_balance = 10000.0
        balance = initial_balance
        equity_peak = balance
        max_dd_dollars = 0.0
        max_dd_pct = 0.0

        midnight_balance = balance
        daily_lockout = False
        current_day = datetime.fromtimestamp(times[0]).day
        max_daily_dd_pct = 4.0

        trades = []
        active_trade = None
        last_order_bar = -10

        daily_high = highs[0]
        daily_low = lows[0]

        last_swing_high = highs[0]
        last_swing_low = lows[0]
        prev_swing_high = highs[0]
        prev_swing_low = lows[0]

        swing_period = 10

        exit_counts = {'STOP LOSS': 0, 'SL+ LOCK WIN': 0, 'TAKE PROFIT (R:R)': 0, 'AUTO-CUT REVERSAL': 0}

        for i in range(130, len(rates_raw)):
            day_num = datetime.fromtimestamp(times[i]).day
            if day_num != current_day:
                current_day = day_num
                midnight_balance = balance
                daily_lockout = False
                daily_high = highs[i]
                daily_low = lows[i]

            daily_high = max(daily_high, highs[i])
            daily_low = min(daily_low, lows[i])

            if i >= swing_period * 2:
                is_pivot_high = all(highs[i - swing_period] >= highs[i - swing_period - k] for k in range(1, swing_period + 1)) and \
                                all(highs[i - swing_period] >= highs[i - swing_period + k] for k in range(1, swing_period + 1))
                if is_pivot_high:
                    prev_swing_high = last_swing_high
                    last_swing_high = highs[i - swing_period]

                is_pivot_low = all(lows[i - swing_period] <= lows[i - swing_period - k] for k in range(1, swing_period + 1)) and \
                               all(lows[i - swing_period] <= lows[i - swing_period + k] for k in range(1, swing_period + 1))
                if is_pivot_low:
                    prev_swing_low = last_swing_low
                    last_swing_low = lows[i - swing_period]

            c_open = opens[i]
            c_high = highs[i]
            c_low = lows[i]
            c_close = closes[i]
            current_atr = atr[i - 1]

            if active_trade is not None:
                t = active_trade
                if t['type'] == 'BUY':
                    floating_pnl = t['realized_profit'] + ((c_close - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                else:
                    floating_pnl = t['realized_profit'] + ((t['open_price'] - c_close) * (t['remaining_lot'] / 0.10) * 10.0)

                daily_dd = ((midnight_balance - (balance + floating_pnl)) / midnight_balance * 100.0) if midnight_balance > 0 else 0
                if daily_dd >= max_daily_dd_pct:
                    exit_price = c_close
                    pnl = floating_pnl
                    balance += ((exit_price - t['open_price'] if t['type'] == 'BUY' else t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': t['type'], 'pnl': pnl, 'reason': 'PROP FIRM DD KILL-SWITCH'})
                    active_trade = None
                    daily_lockout = True
                    continue

                if t['type'] == 'BUY':
                    profit_pips = (c_close - t['open_price']) / pip_value
                    if profit_pips >= be_trigger_pips and not t['is_be']:
                        new_sl = t['open_price'] + (be_lock_pips * pip_value)
                        if new_sl > t['sl']:
                            t['sl'] = new_sl
                            t['is_be'] = True

                    if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                        t['is_tp1'] = True
                        part_lot = t['remaining_lot'] * 0.5
                        part_profit = (part_lot / 0.10) * ((c_close - t['open_price']) * 10.0)
                        balance += part_profit
                        t['realized_profit'] += part_profit
                        t['remaining_lot'] -= part_lot
                        new_sl = t['open_price'] + (be_lock_pips * pip_value)
                        if new_sl > t['sl']:
                            t['sl'] = new_sl

                    if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                        struct_sl = last_swing_low - (0.5 * current_atr)
                        if struct_sl > t['sl']:
                            t['sl'] = struct_sl

                    trail_sl = ema21[i] - (5.0 * pip_value)
                    if trail_sl > t['sl'] and trail_sl > t['open_price']:
                        t['sl'] = trail_sl

                    if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                        exit_price = c_close
                        pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                        balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                        trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL'})
                        exit_counts['AUTO-CUT REVERSAL'] += 1
                        active_trade = None
                        continue

                    if c_low <= t['sl']:
                        exit_price = t['sl']
                        pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                        balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                        reason = 'SL+ LOCK WIN' if exit_price > t['open_price'] else 'STOP LOSS'
                        trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason})
                        exit_counts[reason] += 1
                        active_trade = None
                        continue

                    if c_high >= t['tp']:
                        exit_price = t['tp']
                        pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                        balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                        trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)'})
                        exit_counts['TAKE PROFIT (R:R)'] += 1
                        active_trade = None
                        continue

                elif t['type'] == 'SELL':
                    profit_pips = (t['open_price'] - c_close) / pip_value
                    if profit_pips >= be_trigger_pips and not t['is_be']:
                        new_sl = t['open_price'] - (be_lock_pips * pip_value)
                        if t['sl'] == 0 or new_sl < t['sl']:
                            t['sl'] = new_sl
                            t['is_be'] = True

                    if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                        t['is_tp1'] = True
                        part_lot = t['remaining_lot'] * 0.5
                        part_profit = (part_lot / 0.10) * ((t['open_price'] - c_close) * 10.0)
                        balance += part_profit
                        t['realized_profit'] += part_profit
                        t['remaining_lot'] -= part_lot
                        new_sl = t['open_price'] - (be_lock_pips * pip_value)
                        if t['sl'] == 0 or new_sl < t['sl']:
                            t['sl'] = new_sl

                    if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                        struct_sl = last_swing_high + (0.5 * current_atr)
                        if t['sl'] == 0 or struct_sl < t['sl']:
                            t['sl'] = struct_sl

                    trail_sl = ema21[i] + (5.0 * pip_value)
                    if (t['sl'] == 0 or trail_sl < t['sl']) and trail_sl < t['open_price']:
                        t['sl'] = trail_sl

                    if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                        exit_price = c_close
                        pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                        balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                        trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL'})
                        exit_counts['AUTO-CUT REVERSAL'] += 1
                        active_trade = None
                        continue

                    if c_high >= t['sl']:
                        exit_price = t['sl']
                        pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                        balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                        reason = 'SL+ LOCK WIN' if exit_price < t['open_price'] else 'STOP LOSS'
                        trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason})
                        exit_counts[reason] += 1
                        active_trade = None
                        continue

                    if c_low <= t['tp']:
                        exit_price = t['tp']
                        pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                        balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                        trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)'})
                        exit_counts['TAKE PROFIT (R:R)'] += 1
                        active_trade = None
                        continue

                if balance > equity_peak:
                    equity_peak = balance
                dd = equity_peak - balance
                dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
                if dd > max_dd_dollars:
                    max_dd_dollars = dd
                    max_dd_pct = dd_pct

            # Signal generation
            if active_trade is not None or daily_lockout:
                continue
            if (i - last_order_bar) < 3:
                continue
            if adx[i - 1] < 20.0:
                continue

            fibo_range = last_swing_high - last_swing_low
            ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
            bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

            is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
            is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

            buy_trend_125 = (closes[i - 1] > ema125[i - 1]) and (ema_slope >= 2.0)
            if buy_trend_125 or is_bull_trap:
                is_pullback = lows[i - 1] <= max(ema8[i - 1], ema21[i - 1]) and highs[i - 1] >= min(ema8[i - 1], ema21[i - 1])
                lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
                is_pinbar = (lower_wick / bar_range) >= 0.50
                is_engulf = closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= highs[i - 2]
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

                if score >= min_confluence:
                    entry_price = c_open
                    raw_sl = last_swing_low - (1.2 * current_atr)
                    min_sl = entry_price - (20.0 * pip_value)
                    max_sl = entry_price - (70.0 * pip_value)
                    sl_price = min(raw_sl, min_sl)
                    sl_price = max(sl_price, max_sl)
                    risk_dist = entry_price - sl_price
                    tp_price = entry_price + (risk_dist * rr_ratio)
                    active_trade = {
                        'type': 'BUY', 'open_price': entry_price, 'sl': sl_price, 'tp': tp_price,
                        'lot': base_lot, 'remaining_lot': base_lot, 'is_be': False, 'is_tp1': False,
                        'realized_profit': 0.0, 'open_time': times[i]
                    }
                    last_order_bar = i
                    continue

            sell_trend_125 = (closes[i - 1] < ema125[i - 1]) and (ema_slope <= -2.0)
            if sell_trend_125 or is_bear_trap:
                is_pullback = highs[i - 1] >= min(ema8[i - 1], ema21[i - 1]) and lows[i - 1] <= max(ema8[i - 1], ema21[i - 1])
                upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
                is_pinbar = (upper_wick / bar_range) >= 0.50
                is_engulf = closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= lows[i - 2]
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

                if score >= min_confluence:
                    entry_price = c_open
                    raw_sl = last_swing_high + (1.2 * current_atr)
                    min_sl = entry_price + (20.0 * pip_value)
                    max_sl = entry_price + (70.0 * pip_value)
                    sl_price = max(raw_sl, min_sl)
                    sl_price = min(sl_price, max_sl)
                    risk_dist = sl_price - entry_price
                    tp_price = entry_price - (risk_dist * rr_ratio)
                    active_trade = {
                        'type': 'SELL', 'open_price': entry_price, 'sl': sl_price, 'tp': tp_price,
                        'lot': base_lot, 'remaining_lot': base_lot, 'is_be': False, 'is_tp1': False,
                        'realized_profit': 0.0, 'open_time': times[i]
                    }
                    last_order_bar = i
                    continue

        wins = sum(1 for t in trades if t['pnl'] > 0)
        losses = sum(1 for t in trades if t['pnl'] <= 0)
        wr = (wins / len(trades) * 100.0) if trades else 0.0
        gp = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gl = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        pf = (gp / gl) if gl > 0 else 99.0
        net_p = balance - initial_balance

        dist_str = f"TP:{exit_counts['TAKE PROFIT (R:R)']} | SL+:{exit_counts['SL+ LOCK WIN']} | SL:{exit_counts['STOP LOSS']}"
        print(f"{cfg['name']:<28} | {len(trades):<6} | {wr:>5.1f}% | {pf:>4.2f} | ${net_p:>9.2f} | {max_dd_pct:>5.2f}% | {dist_str}")

    print("=" * 95)

if __name__ == '__main__':
    test_be_variations()
