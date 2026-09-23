"""
Testing Breakout Stop Order with:
1. Structural SL (tight SL at candle low/high)
2. London/NY Session filtering (trading only 08:00 - 23:00 broker time)
3. Dynamic Breakeven & Trailing
"""
import math
from datetime import datetime
import MetaTrader5 as mt5
from run_detailed_ea_audit_backtest import calculate_ema, calculate_atr, calculate_adx, calculate_choppiness

def run_optimized_test():
    if not mt5.initialize():
        return
    rates_m5 = mt5.copy_rates_from_pos("XAUUSD.dmb", mt5.TIMEFRAME_M5, 0, 15000)
    rates_m15 = mt5.copy_rates_from_pos("XAUUSD.dmb", mt5.TIMEFRAME_M15, 0, 10000)
    mt5.shutdown()

    pip_value = 0.10

    def test_logic(rates, is_m15=False, use_session_filter=True, tight_breakout_sl=True, rr=1.8, be_trigger=10.0, be_lock=3.0):
        times = [int(r['time']) for r in rates]
        opens = [float(r['open']) for r in rates]
        highs = [float(r['high']) for r in rates]
        lows = [float(r['low']) for r in rates]
        closes = [float(r['close']) for r in rates]
        n = len(closes)

        ema8 = calculate_ema(closes, 8)
        ema21 = calculate_ema(closes, 21)
        ema125 = calculate_ema(closes, 125)
        atr = calculate_atr(highs, lows, closes, 14)
        adx = calculate_adx(highs, lows, closes, 14)
        ci = calculate_choppiness(highs, lows, closes, 14)

        balance = 10000.0
        equity_peak = balance
        max_dd = 0.0
        trades = []
        active_trade = None
        pending_order = None
        last_order_bar = -999

        for i in range(130, n):
            dt = datetime.fromtimestamp(times[i])
            hour = dt.hour

            c_open, c_high, c_low, c_close = opens[i], highs[i], lows[i], closes[i]
            prev_o, prev_h, prev_l, prev_c = opens[i - 1], highs[i - 1], lows[i - 1], closes[i - 1]
            current_atr = atr[i] if atr[i] > 0 else 1.5

            # 1. Pending check
            if pending_order is not None:
                p = pending_order
                filled = False
                if p['type'] == 'BUY_STOP' and c_high >= p['price']:
                    filled = True
                    exec_p = max(c_open, p['price'])
                    tp_p = exec_p + (rr * (exec_p - p['sl']))
                    active_trade = {
                        'type': 'BUY', 'open_price': exec_p, 'sl': p['sl'], 'tp': tp_p,
                        'lot': 0.10, 'is_be': False, 'realized_profit': 0.0
                    }
                elif p['type'] == 'SELL_STOP' and c_low <= p['price']:
                    filled = True
                    exec_p = min(c_open, p['price'])
                    tp_p = exec_p - (rr * (p['sl'] - exec_p))
                    active_trade = {
                        'type': 'SELL', 'open_price': exec_p, 'sl': p['sl'], 'tp': tp_p,
                        'lot': 0.10, 'is_be': False, 'realized_profit': 0.0
                    }
                if filled:
                    pending_order = None
                    last_order_bar = i
                elif i >= p['expire_bar']:
                    pending_order = None

            # 2. Active trade management
            if active_trade is not None:
                t = active_trade
                if t['type'] == 'BUY':
                    pips = (c_close - t['open_price']) / pip_value
                    if pips >= be_trigger and not t['is_be']:
                        t['sl'] = t['open_price'] + (be_lock * pip_value)
                        t['is_be'] = True
                    # Trailing via EMA 21
                    if t['is_be']:
                        tr_sl = ema21[i - 1] - (3.0 * pip_value)
                        if tr_sl > t['sl'] and (c_close - tr_sl) >= (10 * pip_value):
                            t['sl'] = tr_sl
                    if c_low <= t['sl']:
                        pnl = (t['sl'] - t['open_price']) * 10.0
                        balance += pnl
                        trades.append({'pnl': pnl, 'win': pnl > 0, 'be': t['is_be']})
                        active_trade = None
                    elif c_high >= t['tp']:
                        pnl = (t['tp'] - t['open_price']) * 10.0
                        balance += pnl
                        trades.append({'pnl': pnl, 'win': True, 'be': False})
                        active_trade = None

                elif t['type'] == 'SELL':
                    pips = (t['open_price'] - c_close) / pip_value
                    if pips >= be_trigger and not t['is_be']:
                        t['sl'] = t['open_price'] - (be_lock * pip_value)
                        t['is_be'] = True
                    if t['is_be']:
                        tr_sl = ema21[i - 1] + (3.0 * pip_value)
                        if tr_sl < t['sl'] and (tr_sl - c_close) >= (10 * pip_value):
                            t['sl'] = tr_sl
                    if c_high >= t['sl']:
                        pnl = (t['open_price'] - t['sl']) * 10.0
                        balance += pnl
                        trades.append({'pnl': pnl, 'win': pnl > 0, 'be': t['is_be']})
                        active_trade = None
                    elif c_low <= t['tp']:
                        pnl = (t['open_price'] - t['tp']) * 10.0
                        balance += pnl
                        trades.append({'pnl': pnl, 'win': True, 'be': False})
                        active_trade = None

                if balance > equity_peak:
                    equity_peak = balance
                dd = (equity_peak - balance) / equity_peak * 100.0
                if dd > max_dd:
                    max_dd = dd

            # 3. Signal detector
            if active_trade is not None or pending_order is not None:
                continue
            if (i - last_order_bar) < 3:
                continue

            # Session filter: Active European & US session (08:00 - 23:00 broker time)
            if use_session_filter and (hour < 8 or hour >= 23):
                continue

            if ci[i - 1] > 60.0:  # Skip choppy market
                continue
            if adx[i - 1] < 22.0:  # Require kinetic momentum
                continue

            lookback = 30
            last_swing_high = max(highs[max(0, i - lookback):i - 1])
            last_swing_low = min(lows[max(0, i - lookback):i - 1])
            fibo_range = last_swing_high - last_swing_low

            ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
            bar_range = prev_h - prev_l if prev_h > prev_l else 0.01

            is_bull_trap = prev_h > last_swing_high and prev_c < last_swing_high and (prev_h - prev_c) >= (0.40 * bar_range)
            is_bear_trap = prev_l < last_swing_low and prev_c > last_swing_low and (prev_c - prev_l) >= (0.40 * bar_range)

            # BUY SETUP
            buy_trend_125 = (prev_c > ema125[i - 1]) and (ema_slope >= 2.0)
            if buy_trend_125 or is_bull_trap:
                is_pullback = prev_l <= max(ema8[i - 1], ema21[i - 1]) and prev_h >= min(ema8[i - 1], ema21[i - 1])
                lower_wick = min(prev_o, prev_c) - prev_l
                is_pinbar = (lower_wick / bar_range) >= 0.50
                is_engulf = prev_c > prev_o and closes[i - 2] < opens[i - 2] and prev_c >= highs[i - 2]
                candle_ok = is_pinbar or is_engulf or is_bull_trap

                score = 0.0
                if prev_c > last_swing_high: score += 20.0
                else: score += 15.0
                if prev_l < last_swing_low and prev_c > last_swing_low: score += 12.0
                if ema8[i - 1] > ema21[i - 1]: score += 10.0
                if is_pinbar: score += 15.0
                elif is_engulf: score += 12.0
                if is_pullback: score += 10.0
                if is_bull_trap: score += 15.0

                if (is_pullback and candle_ok and score >= 65.0) or is_bull_trap:
                    stop_p = prev_h + (2.0 * pip_value)
                    if tight_breakout_sl:
                        # Structural invalidation: low of the trigger candle
                        sl_p = prev_l - (2.0 * pip_value)
                        # Min risk safety
                        if (stop_p - sl_p) < (15.0 * pip_value):
                            sl_p = stop_p - (15.0 * pip_value)
                        elif (stop_p - sl_p) > (35.0 * pip_value):
                            sl_p = stop_p - (35.0 * pip_value)
                    else:
                        sl_p = opens[i] - max(20.0 * pip_value, (opens[i] - prev_l) + (1.2 * current_atr))

                    pending_order = {
                        'type': 'BUY_STOP', 'price': stop_p, 'sl': sl_p,
                        'expire_bar': i + 4
                    }
                    continue

            # SELL SETUP
            sell_trend_125 = (prev_c < ema125[i - 1]) and (ema_slope <= -2.0)
            if sell_trend_125 or is_bear_trap:
                is_pullback = prev_h >= min(ema8[i - 1], ema21[i - 1]) and prev_l <= max(ema8[i - 1], ema21[i - 1])
                upper_wick = prev_h - max(prev_o, prev_c)
                is_pinbar = (upper_wick / bar_range) >= 0.50
                is_engulf = prev_c < prev_o and closes[i - 2] > opens[i - 2] and prev_c <= lows[i - 2]
                candle_ok = is_pinbar or is_engulf or is_bear_trap

                score = 0.0
                if prev_c < last_swing_low: score += 20.0
                else: score += 15.0
                if prev_h > last_swing_high and prev_c < last_swing_high: score += 12.0
                if ema8[i - 1] < ema21[i - 1]: score += 10.0
                if is_pinbar: score += 15.0
                elif is_engulf: score += 12.0
                if is_pullback: score += 10.0
                if is_bear_trap: score += 15.0

                if (is_pullback and candle_ok and score >= 65.0) or is_bear_trap:
                    stop_p = prev_l - (2.0 * pip_value)
                    if tight_breakout_sl:
                        # Structural invalidation: high of the trigger candle
                        sl_p = prev_h + (2.0 * pip_value)
                        if (sl_p - stop_p) < (15.0 * pip_value):
                            sl_p = stop_p + (15.0 * pip_value)
                        elif (sl_p - stop_p) > (35.0 * pip_value):
                            sl_p = stop_p + (35.0 * pip_value)
                    else:
                        sl_p = opens[i] + max(20.0 * pip_value, (prev_h - opens[i]) + (1.2 * current_atr))

                    pending_order = {
                        'type': 'SELL_STOP', 'price': stop_p, 'sl': sl_p,
                        'expire_bar': i + 4
                    }
                    continue

        wins = len([t for t in trades if t['win']])
        losses = len([t for t in trades if not t['win']])
        wr = (wins / len(trades) * 100.0) if trades else 0
        gross_p = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        gross_l = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        pf = (gross_p / gross_l) if gross_l > 0 else 99.0
        net_p = balance - 10000.0
        return len(trades), wr, pf, net_p, max_dd

    print(f"{'Konfigurasi':<50} | {'Trades':<6} | {'Win%':<7} | {'PF':<5} | {'Net Profit':<11} | {'Max DD%':<7}")
    print("-" * 100)

    # Test M5 variations
    for tight_sl in [False, True]:
        for sess in [False, True]:
            for rr in [1.5, 1.8, 2.0]:
                for be_trig in [10.0, 12.0]:
                    name = f"M5 | TightSL:{str(tight_sl):<5} | Sess:{str(sess):<5} | RR:{rr:.1f} | BE:{be_trig:.0f}p"
                    tr, wr, pf, net, dd = test_logic(rates_m5, is_m15=False, use_session_filter=sess, tight_breakout_sl=tight_sl, rr=rr, be_trigger=be_trig)
                    if net > 0:
                        print(f"{name:<50} | {tr:<6} | {wr:>5.1f}% | {pf:>4.2f} | ${net:>9.2f} | {dd:>5.2f}%")

    print("\n--- M15 TIMEFRAME ---")
    for tight_sl in [False, True]:
        for sess in [False, True]:
            for rr in [1.5, 1.8, 2.0]:
                name = f"M15 | TightSL:{str(tight_sl):<5} | Sess:{str(sess):<5} | RR:{rr:.1f}"
                tr, wr, pf, net, dd = test_logic(rates_m15, is_m15=True, use_session_filter=sess, tight_breakout_sl=tight_sl, rr=rr, be_trigger=15.0)
                if net > 0:
                    print(f"{name:<50} | {tr:<6} | {wr:>5.1f}% | {pf:>4.2f} | ${net:>9.2f} | {dd:>5.2f}%")

if __name__ == '__main__':
    run_optimized_test()
