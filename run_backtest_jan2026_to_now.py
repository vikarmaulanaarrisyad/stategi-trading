"""
VIKAR EA 4-PILLAR PRO - BACKTEST HISTORIS LENGKAP: JANUARI 2026 S/D SEKARANG
Timeframe: M5 | Simbol: XAUUSD.dmb (Broker Didimax)
Menghitung simulasi bar-by-bar pada 50,000+ bar data riil dengan:
1. Rincian Metrik Lengkap (Win Rate, Profit Factor, Net Profit, Max DD)
2. Breakdown Kinerja Bulanan (Januari - September 2026)
3. Komparasi Antar-Preset
4. Ekspor Laporan HTML Visual
"""

import os
import sys
import math
import json
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

def calculate_adx(highs, lows, closes, period=14):
    n = len(closes)
    if n < period * 2:
        return [25.0] * n
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

def simulate_m5_period(rates_raw, preset_name="XAUUSD_BACKTEST_1YEAR_OPTIMAL", custom_params=None):
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

    # Konfigurasi Preset
    if "SNIPER" in preset_name.upper():
        min_confluence = 75.0
        require_double_align = True
        require_golden_pocket = True
        be_trigger_pips = 8.0
        be_lock_pips = 5.0
        tp1_trigger_pips = 14.0
        rr_ratio = 1.8
        base_lot = 0.10
    elif "SCALPING" in preset_name.upper():
        min_confluence = 65.0
        require_double_align = True
        require_golden_pocket = False
        be_trigger_pips = 12.0
        be_lock_pips = 5.0
        tp1_trigger_pips = 15.0
        rr_ratio = 1.8
        base_lot = 0.10
    elif "FAST" in preset_name.upper():
        min_confluence = 60.0
        require_double_align = False
        require_golden_pocket = False
        be_trigger_pips = 8.0
        be_lock_pips = 4.5
        tp1_trigger_pips = 10.0
        rr_ratio = 1.5
        base_lot = 0.10
    else:  # XAUUSD_BACKTEST_1YEAR_OPTIMAL
        min_confluence = 65.0
        require_double_align = False
        require_golden_pocket = False
        be_trigger_pips = 12.0
        be_lock_pips = 5.0
        tp1_trigger_pips = 15.0
        rr_ratio = 2.0
        base_lot = 0.10

    if custom_params:
        if 'be_trigger_pips' in custom_params: be_trigger_pips = custom_params['be_trigger_pips']
        if 'be_lock_pips' in custom_params: be_lock_pips = custom_params['be_lock_pips']
        if 'tp1_trigger_pips' in custom_params: tp1_trigger_pips = custom_params['tp1_trigger_pips']
        if 'rr_ratio' in custom_params: rr_ratio = custom_params['rr_ratio']
        if 'min_confluence' in custom_params: min_confluence = custom_params['min_confluence']

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
    daily_close = closes[0]
    pivot_p = (daily_high + daily_low + daily_close) / 3.0

    last_swing_high = highs[0]
    last_swing_low = lows[0]
    prev_swing_high = highs[0]
    prev_swing_low = lows[0]

    pip_value = 0.10
    monthly_data = {}
    equity_curve = []

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        dt_prev = datetime.fromtimestamp(times[i - 1])

        month_key = dt_curr.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}

        # Midnight balance reset
        if dt_curr.day != dt_prev.day:
            pivot_p = (daily_high + daily_low + daily_close) / 3.0
            daily_high = highs[i]
            daily_low = lows[i]
            midnight_balance = balance
            daily_lockout = False
        else:
            daily_high = max(daily_high, highs[i])
            daily_low = min(daily_low, lows[i])
        daily_close = closes[i]

        # SMC Fractals (2-bar)
        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high
                last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low
                last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        # 1. Manage active trade
        if active_trade is not None:
            t = active_trade
            c_high = highs[i]
            c_low = lows[i]
            c_close = closes[i]

            if t['type'] == 'BUY':
                floating_pnl = t['realized_profit'] + ((c_close - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
            else:
                floating_pnl = t['realized_profit'] + ((t['open_price'] - c_close) * (t['remaining_lot'] / 0.10) * 10.0)

            current_equity = balance + floating_pnl
            daily_dd = ((midnight_balance - current_equity) / midnight_balance * 100.0) if midnight_balance > 0 else 0

            # Prop firm kill-switch
            if daily_dd >= max_daily_dd_pct:
                exit_price = c_close
                pnl = floating_pnl
                balance += ((exit_price - t['open_price'] if t['type'] == 'BUY' else t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                trades.append({
                    'time': times[i], 'type': t['type'], 'pnl': pnl,
                    'reason': 'PROP FIRM DD KILL-SWITCH', 'month': month_key
                })
                monthly_data[month_key]['trades'] += 1
                if pnl > 0: monthly_data[month_key]['wins'] += 1
                else: monthly_data[month_key]['losses'] += 1
                monthly_data[month_key]['pnl'] += pnl
                active_trade = None
                daily_lockout = True
                continue

            if t['type'] == 'BUY':
                profit_pips = (c_close - t['open_price']) / pip_value

                # Auto-BE SL+
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # Partial TP1 50%
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

                # Dynamic Structural Swing Trailing
                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']:
                        t['sl'] = struct_sl

                # Trailing Stop EMA 21 Backup
                trail_sl = ema21[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']:
                    t['sl'] = trail_sl

                # Early Cut Reversal
                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'month': month_key})
                    monthly_data[month_key]['trades'] += 1
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    monthly_data[month_key]['pnl'] += pnl
                    active_trade = None
                    continue

                # Stop Loss Hit
                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price > t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'month': month_key})
                    monthly_data[month_key]['trades'] += 1
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    monthly_data[month_key]['pnl'] += pnl
                    active_trade = None
                    continue

                # Take Profit Hit
                if c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'month': month_key})
                    monthly_data[month_key]['trades'] += 1
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    monthly_data[month_key]['pnl'] += pnl
                    active_trade = None
                    continue

            elif t['type'] == 'SELL':
                profit_pips = (t['open_price'] - c_close) / pip_value

                # Auto-BE SL+
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # Partial TP1 50%
                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    t['is_tp1'] = True
                    part_lot = t['remaining_lot'] * 0.5
                    part_profit = (part_lot / 0.10) * ((t['open_price'] - c_close) * 10.0)
                    balance += part_profit
                    t['realized_profit'] += part_profit
                    t['remaining_lot'] -= part_lot
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl

                # Dynamic Structural Swing Trailing
                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']:
                        t['sl'] = struct_sl

                # Trailing Stop EMA 21 Backup
                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']:
                    t['sl'] = trail_sl

                # Early Cut Reversal
                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'month': month_key})
                    monthly_data[month_key]['trades'] += 1
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    monthly_data[month_key]['pnl'] += pnl
                    active_trade = None
                    continue

                # Stop Loss Hit
                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price < t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'month': month_key})
                    monthly_data[month_key]['trades'] += 1
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    monthly_data[month_key]['pnl'] += pnl
                    active_trade = None
                    continue

                # Take Profit Hit
                if c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'month': month_key})
                    monthly_data[month_key]['trades'] += 1
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    monthly_data[month_key]['pnl'] += pnl
                    active_trade = None
                    continue

            # Drawdown calculation
            if balance > equity_peak:
                equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars:
                max_dd_dollars = dd
                max_dd_pct = dd_pct

        # Sample equity curve
        if i % 25 == 0 or active_trade is None:
            cur_eq = balance + (floating_pnl if active_trade is not None else 0.0)
            equity_curve.append({'time': times[i], 'balance': round(balance, 2), 'equity': round(cur_eq, 2)})

        # 2. Signal Generation (Instant Market)
        if active_trade is not None or daily_lockout:
            continue
        if (i - last_order_bar) < 3:
            continue

        # Anti-choppy & ADX momentum
        if adx[i - 1] < 20.0:
            continue

        fibo_range = last_swing_high - last_swing_low
        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
        bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

        # Trap Hunter
        is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
        is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

        # BUY SETUP
        buy_trend_125 = (closes[i - 1] > ema125[i - 1]) and (ema_slope >= 2.0)
        if buy_trend_125 or is_bull_trap:
            is_pullback = lows[i - 1] <= max(ema8[i - 1], ema21[i - 1]) and highs[i - 1] >= min(ema8[i - 1], ema21[i - 1])
            lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
            is_pinbar = (lower_wick / bar_range) >= 0.50
            is_engulf = closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= highs[i - 2]
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

            if require_double_align and not (buy_trend_125 and ema8[i - 1] > ema21[i - 1]):
                continue
            if require_golden_pocket and not in_gp:
                continue

            # v3.40 AI Candlestick Shield (Anti-Doji, Anti-Exhaustion, Anti-Overextended)
            candle_body = abs(closes[i - 1] - opens[i - 1])
            body_pct = (candle_body / bar_range) * 100.0
            upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
            upper_wick_pct = (upper_wick / bar_range) * 100.0

            if body_pct <= 22.0 and not is_bull_trap:
                continue
            if upper_wick_pct >= 45.0 and not is_bull_trap:
                continue
            if is_engulf and ((closes[i - 1] - ema21[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value):
                continue

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
            is_pullback = highs[i - 1] >= min(ema8[i - 1], ema21[i - 1]) and lows[i - 1] <= max(ema8[i - 1], ema21[i - 1])
            upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
            is_pinbar = (upper_wick / bar_range) >= 0.50
            is_engulf = closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= lows[i - 2]
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

            if require_double_align and not (sell_trend_125 and ema8[i - 1] < ema21[i - 1]):
                continue
            if require_golden_pocket and not in_gp:
                continue

            # v3.40 AI Candlestick Shield (Anti-Doji, Anti-Exhaustion, Anti-Overextended)
            candle_body = abs(closes[i - 1] - opens[i - 1])
            body_pct = (candle_body / bar_range) * 100.0
            lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
            lower_wick_pct = (lower_wick / bar_range) * 100.0

            if body_pct <= 22.0 and not is_bear_trap:
                continue
            if lower_wick_pct >= 45.0 and not is_bear_trap:
                continue
            if is_engulf and ((ema21[i - 1] - closes[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value):
                continue

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

    # Summary
    total_trades = len(trades)
    winning = [t for t in trades if t['pnl'] > 0]
    losing = [t for t in trades if t['pnl'] < 0]
    gross_p = sum(t['pnl'] for t in winning)
    gross_l = abs(sum(t['pnl'] for t in losing))
    net_p = balance - initial_balance
    wr = (len(winning) / total_trades * 100.0) if total_trades > 0 else 0.0
    pf = (gross_p / gross_l) if gross_l > 0 else 99.0

    exit_counts = {}
    for t in trades:
        r = t['reason']
        exit_counts[r] = exit_counts.get(r, 0) + 1

    return {
        'preset': preset_name,
        'trades': trades,
        'total_trades': total_trades,
        'wins': len(winning),
        'losses': len(losing),
        'win_rate': wr,
        'profit_factor': pf,
        'net_profit': net_p,
        'gross_profit': gross_p,
        'gross_loss': gross_l,
        'final_balance': balance,
        'max_dd_dollars': max_dd_dollars,
        'max_dd_pct': max_dd_pct,
        'exit_counts': exit_counts,
        'monthly_data': monthly_data,
        'equity_curve': equity_curve,
        'first_time': times[0],
        'last_time': times[-1]
    }

def main():
    print("=" * 90)
    print("BACKTEST MENYELURUH EA VIKAR 4-PILLAR PRO: JANUARI 2026 S/D SEKARANG (TIMEFRAME M5)")
    print("=" * 90)

    if not mt5.initialize():
        print("[-] Gagal inisialisasi MT5.")
        return

    s = "XAUUSD.dmb"
    date_from = datetime(2026, 1, 1)
    date_to = datetime(2026, 9, 21)
    print(f"[+] Menarik data riil broker Didimax {s} dari {date_from.strftime('%Y-%m-%d')} s/d Sekarang...")
    rates = mt5.copy_rates_range(s, mt5.TIMEFRAME_M5, date_from, date_to)
    mt5.shutdown()

    if rates is None or len(rates) == 0:
        print("[-] Data rates kosong.")
        return

    t0 = datetime.fromtimestamp(int(rates[0]['time']))
    t1 = datetime.fromtimestamp(int(rates[-1]['time']))
    print(f"[+] Berhasil memuat {len(rates):,} Bar M5. Dari: {t0} s/d {t1}")

    presets = [
        "XAUUSD_BACKTEST_1YEAR_OPTIMAL",
        "XAUUSD_HIGH_WINRATE_SNIPER",
        "XAUUSD_M5_Scalping_Confluence",
        "XAUUSD_FAST_AUTO_TRADE"
    ]

    all_res = []
    print("\n" + "=" * 95)
    print(f"{'Nama Preset':<32} | {'Trades':<6} | {'Win%':<7} | {'PF':<5} | {'Net Profit':<11} | {'Max DD%':<7}")
    print("-" * 95)

    for p in presets:
        r = simulate_m5_period(rates, p)
        all_res.append(r)
        print(f"{p:<32} | {r['total_trades']:<6} | {r['win_rate']:>5.1f}% | {r['profit_factor']:>4.2f} | ${r['net_profit']:>9.2f} | {r['max_dd_pct']:>5.2f}%")
    print("=" * 95)

    # Detailed breakdown on the best preset
    best = max(all_res, key=lambda x: x['net_profit'])
    print(f"\n[HASIL LENGKAP PRESET UNGGULAN: {best['preset']}]")
    print(f"Saldo Awal Modal : $10,000.00")
    print(f"Saldo Akhir      : ${best['final_balance']:,.2f} (+${best['net_profit']:,.2f} / +{(best['net_profit']/10000.0)*100:.1f}%)")
    print(f"Total Transaksi  : {best['total_trades']} ({best['wins']} Menang / {best['losses']} Kalah)")
    print(f"Win Rate Akhir   : {best['win_rate']:.2f}%")
    print(f"Profit Factor    : {best['profit_factor']:.2f}")
    print(f"Max Drawdown     : ${best['max_dd_dollars']:,.2f} ({best['max_dd_pct']:.2f}%)")
    print(f"Distribusi Exit  : {best['exit_counts']}")

    print("\n--- PERFORMA PER BULAN (JANUARI - SEPTEMBER 2026) ---")
    print(f"{'Bulan':<10} | {'Trades':<7} | {'Win Rate':<9} | {'Net Profit ($)':<14} | {'Status'}")
    print("-" * 55)
    for m, d in sorted(best['monthly_data'].items()):
        m_wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0
        status = "PROFIT HIJAU" if d['pnl'] > 0 else "MERAH"
        print(f"{m:<10} | {d['trades']:<7} | {m_wr:>6.1f}%   | ${d['pnl']:>10.2f}    | {status}")
    print("=" * 55)

if __name__ == '__main__':
    main()
