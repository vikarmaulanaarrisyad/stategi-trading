"""
SIMULASI OPTIMASI FILTER POLA CANDLESTICK BERMASALAH
Menguji dampak filter:
1. Filter Doji / Spinning Top (Body < 20% Range)
2. Filter Exhaustion Wick (Upper wick > 45% pada Buy, Lower wick > 45% pada Sell)
3. Filter False Engulfing Overextension (Jarak ke EMA > 1.5 ATR)
"""

import sys
from datetime import datetime
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

def test_filters(rates_clean, filter_doji=False, filter_exhaustion=False, filter_bad_engulf=False):
    total_bars = len(rates_clean)
    times = [int(r['time']) for r in rates_clean]
    opens = [float(r['open']) for r in rates_clean]
    highs = [float(r['high']) for r in rates_clean]
    lows = [float(r['low']) for r in rates_clean]
    closes = [float(r['close']) for r in rates_clean]

    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)
    atr = calculate_atr(highs, lows, closes, 14)
    adx = calculate_adx(highs, lows, closes, 14)

    min_confluence = 65.0
    be_trigger_pips = 12.0
    be_lock_pips = 5.0
    tp1_trigger_pips = 15.0
    rr_ratio = 2.0
    base_lot = 0.10
    pip_value = 0.10

    initial_balance = 10000.0
    balance = initial_balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0

    midnight_balance = balance
    daily_lockout = False

    trades = []
    active_trade = None
    last_order_bar = -10

    daily_high = highs[0]
    daily_low = lows[0]
    daily_close = closes[0]

    last_swing_high = highs[0]
    last_swing_low = lows[0]
    prev_swing_high = highs[0]
    prev_swing_low = lows[0]

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        dt_prev = datetime.fromtimestamp(times[i - 1])

        if dt_curr.day != dt_prev.day:
            daily_high = highs[i]
            daily_low = lows[i]
            midnight_balance = balance
            daily_lockout = False
        else:
            daily_high = max(daily_high, highs[i])
            daily_low = min(daily_low, lows[i])
        daily_close = closes[i]

        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high
                last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low
                last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        if active_trade is not None:
            t = active_trade
            c_high = highs[i]
            c_low = lows[i]
            c_close = closes[i]

            if t['type'] == 'BUY':
                floating_pnl = t['realized_profit'] + ((c_close - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
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
                    if new_sl > t['sl']: t['sl'] = new_sl

                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']: t['sl'] = struct_sl

                trail_sl = ema21[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']:
                    t['sl'] = trail_sl

                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'pnl': pnl, 'type': 'BUY'})
                    active_trade = None
                    continue

                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'pnl': pnl, 'type': 'BUY'})
                    active_trade = None
                    continue

                if c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'pnl': pnl, 'type': 'BUY'})
                    active_trade = None
                    continue

            elif t['type'] == 'SELL':
                floating_pnl = t['realized_profit'] + ((t['open_price'] - c_close) * (t['remaining_lot'] / 0.10) * 10.0)
                profit_pips = (t['open_price'] - c_close) / pip_value

                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
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
                    if new_sl < t['sl']: t['sl'] = new_sl

                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']: t['sl'] = struct_sl

                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']:
                    t['sl'] = trail_sl

                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'pnl': pnl, 'type': 'SELL'})
                    active_trade = None
                    continue

                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'pnl': pnl, 'type': 'SELL'})
                    active_trade = None
                    continue

                if c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'pnl': pnl, 'type': 'SELL'})
                    active_trade = None
                    continue

            if balance > equity_peak: equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars:
                max_dd_dollars = dd
                max_dd_pct = dd_pct

        if active_trade is not None or daily_lockout: continue
        if (i - last_order_bar) < 3: continue
        if adx[i - 1] < 20.0: continue

        fibo_range = last_swing_high - last_swing_low
        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
        bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

        # Candlestick anatomy filter check
        candle_body = abs(closes[i - 1] - opens[i - 1])
        body_pct = (candle_body / bar_range) * 100.0
        upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
        lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
        upper_wick_pct = (upper_wick / bar_range) * 100.0
        lower_wick_pct = (lower_wick / bar_range) * 100.0

        # Filter 1: Doji / Spinning top
        if filter_doji and body_pct <= 22.0:
            continue

        is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
        is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

        # BUY SETUP
        buy_trend_125 = (closes[i - 1] > ema125[i - 1]) and (ema_slope >= 2.0)
        if buy_trend_125 or is_bull_trap:
            # Filter 2: Exhaustion Upper Wick on BUY
            if filter_exhaustion and upper_wick_pct >= 45.0:
                continue

            # Filter 3: Bad Engulfing
            is_engulf = closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= highs[i - 2]
            if filter_bad_engulf and is_engulf:
                dist_to_ema21 = (closes[i - 1] - ema21[i - 1]) / pip_value
                if dist_to_ema21 >= (1.5 * current_atr / pip_value):
                    continue

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

                lot = base_lot
                if score >= 85.0: lot = round(base_lot * 1.30, 2)
                elif score < 75.0: lot = round(base_lot * 0.70, 2)

                active_trade = {
                    'type': 'BUY', 'open_time': times[i], 'open_price': open_p,
                    'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score
                }
                last_order_bar = i
                continue

        # SELL SETUP
        sell_trend_125 = (closes[i - 1] < ema125[i - 1]) and (ema_slope <= -2.0)
        if sell_trend_125 or is_bear_trap:
            # Filter 2: Exhaustion Lower Wick on SELL
            if filter_exhaustion and lower_wick_pct >= 45.0:
                continue

            # Filter 3: Bad Engulfing
            is_engulf = closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= lows[i - 2]
            if filter_bad_engulf and is_engulf:
                dist_to_ema21 = (ema21[i - 1] - closes[i - 1]) / pip_value
                if dist_to_ema21 >= (1.5 * current_atr / pip_value):
                    continue

            is_pullback = highs[i - 1] >= min(ema8[i - 1], ema21[i - 1]) and lows[i - 1] <= max(ema8[i - 1], ema21[i - 1])
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

                lot = base_lot
                if score >= 85.0: lot = round(base_lot * 1.30, 2)
                elif score < 75.0: lot = round(base_lot * 0.70, 2)

                active_trade = {
                    'type': 'SELL', 'open_time': times[i], 'open_price': open_p,
                    'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score
                }
                last_order_bar = i
                continue

    total_t = len(trades)
    wins = len([t for t in trades if t['pnl'] > 0])
    losses = len([t for t in trades if t['pnl'] <= 0])
    gross_win = sum([t['pnl'] for t in trades if t['pnl'] > 0])
    gross_loss = abs(sum([t['pnl'] for t in trades if t['pnl'] <= 0]))
    pf = (gross_win / gross_loss) if gross_loss > 0 else 99.0
    net_pnl = balance - initial_balance
    wr = (wins / total_t * 100.0) if total_t > 0 else 0

    return {
        'total': total_t, 'wins': wins, 'losses': losses, 'win_rate': wr,
        'profit_factor': pf, 'net_profit': net_pnl, 'max_dd_dollars': max_dd_dollars,
        'max_dd_pct': max_dd_pct, 'final_balance': balance
    }

def main():
    if not mt5.initialize(): return
    symbol = "XAUUSD.dmb"
    if not mt5.symbol_select(symbol, True):
        for s in ["XAUUSD", "GOLD", "XAUUSDm"]:
            if mt5.symbol_select(s, True): symbol = s; break
    dt_from = datetime(2026, 1, 1)
    rates_raw = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, datetime.now(), 65000)
    mt5.shutdown()
    rates_clean = [r for r in rates_raw if datetime.fromtimestamp(int(r['time'])) >= dt_from]

    res_default = test_filters(rates_clean, False, False, False)
    res_no_doji = test_filters(rates_clean, filter_doji=True, filter_exhaustion=False, filter_bad_engulf=False)
    res_no_exhaustion = test_filters(rates_clean, filter_doji=False, filter_exhaustion=True, filter_bad_engulf=False)
    res_all_filters = test_filters(rates_clean, filter_doji=True, filter_exhaustion=True, filter_bad_engulf=True)

    print("=========================================================================================================")
    print("HASIL SIMULASI KOMPARASI FILTER POLA CANDLESTICK BERMASALAH (JAN - SEP 2026)")
    print("=========================================================================================================")
    print(f"{'Skenario Filter':<32} | {'Trades':<7} | {'Win Rate':<9} | {'PF':<5} | {'Net Profit ($)':<14} | {'Pertumbuhan':<11} | {'Max DD ($)':<10} | {'Max DD (%)'}")
    print("-" * 115)

    cases = [
        ("1. Baseline (Tanpa Filter Candle)", res_default),
        ("2. + Filter Doji / Spinning Top", res_no_doji),
        ("3. + Filter Exhaustion Wick Lawan", res_no_exhaustion),
        ("4. + Filter Triple Candle Shield", res_all_filters)
    ]

    for label, r in cases:
        growth = (r['net_profit'] / 10000.0) * 100.0
        print(f"{label:<32} | {r['total']:<7} | {r['win_rate']:>6.2f}%   | {r['profit_factor']:>4.2f} | ${r['net_profit']:>12,.2f} | {growth:>9.1f}% | ${r['max_dd_dollars']:>8,.2f} | {r['max_dd_pct']:>6.2f}%")
    print("=========================================================================================================\n")

if __name__ == "__main__":
    main()
