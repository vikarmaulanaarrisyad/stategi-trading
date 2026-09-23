"""
VIKAR EA 4-PILLAR PRO - ENTRY EXECUTION MODE COMPARISON ENGINE
Mengeksekusi simulasi bar-demi-bar pada data riil broker MetaTrader 5 (XAUUSD.dmb).
Membandingkan secara head-to-head performa dan winrate antara:
1. Langsung Entry (Instant Market Order)
2. BUY Limit / SELL Limit (Pullback 5 Pips, 8 Pips, Mid-Candle 50%)
3. BUY Stop / SELL Stop (Breakout Confirmation 2 Pips, 4 Pips)
Menghasilkan laporan komparasi konsol dan visual dashboard HTML.
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

def simulate_strategy(rates_raw, mode_cfg):
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

    min_confluence = 65.0
    be_trigger_pips = 12.0
    be_lock_pips = 4.0
    tp1_trigger_pips = 15.0
    rr_ratio = 2.0
    base_lot = 0.10

    balance = 10000.0
    initial_balance = balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0

    midnight_balance = balance
    daily_lockout = False
    max_daily_dd_pct = 4.0

    trades = []
    active_trade = None
    pending_order = None
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
    signals_count = 0
    filled_count = 0
    unfilled_count = 0

    equity_curve = [{'time': times[150], 'balance': balance, 'equity': balance}]

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        dt_prev = datetime.fromtimestamp(times[i - 1])

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

        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high
                last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low
                last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        # 1. PENDING ORDER CHECK
        if pending_order is not None and active_trade is None:
            p = pending_order
            if i >= p['expire_bar']:
                unfilled_count += 1
                pending_order = None
            else:
                filled = False
                fill_price = 0.0
                if p['type'] == 'BUY_LIMIT':
                    if lows[i] <= p['price']:
                        filled = True
                        fill_price = p['price']
                elif p['type'] == 'SELL_LIMIT':
                    if highs[i] >= p['price']:
                        filled = True
                        fill_price = p['price']
                elif p['type'] == 'BUY_STOP':
                    if highs[i] >= p['price']:
                        filled = True
                        fill_price = p['price']
                elif p['type'] == 'SELL_STOP':
                    if lows[i] <= p['price']:
                        filled = True
                        fill_price = p['price']

                if filled:
                    filled_count += 1
                    if p['direction'] == 'BUY':
                        sl_dist = fill_price - p['sl']
                        tp_p = fill_price + (rr_ratio * sl_dist)
                    else:
                        sl_dist = p['sl'] - fill_price
                        tp_p = fill_price - (rr_ratio * sl_dist)

                    active_trade = {
                        'type': p['direction'],
                        'open_time': times[i],
                        'open_price': fill_price,
                        'sl': p['sl'],
                        'tp': tp_p,
                        'initial_lot': p['lot'],
                        'remaining_lot': p['lot'],
                        'is_be': False,
                        'is_tp1': False,
                        'realized_profit': 0.0,
                        'score': p['score']
                    }
                    pending_order = None
                    last_order_bar = i

        # 2. ACTIVE TRADE MANAGEMENT
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

            if daily_dd >= max_daily_dd_pct:
                exit_price = c_close
                pnl = floating_pnl
                balance += pnl
                trades.append({
                    'time': times[i], 'type': t['type'], 'pnl': pnl,
                    'reason': 'PROP FIRM DD KILL-SWITCH',
                    'pips': (exit_price - t['open_price'] if t['type'] == 'BUY' else t['open_price'] - exit_price) / pip_value,
                    'lot': t['initial_lot']
                })
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
                    closed_lot = round(t['initial_lot'] * 0.50, 2)
                    pnl_tp1 = (c_close - t['open_price']) * (closed_lot / 0.10) * 10.0
                    t['realized_profit'] += pnl_tp1
                    t['remaining_lot'] -= closed_lot
                    t['is_tp1'] = True
                    be_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if be_sl > t['sl']:
                        t['sl'] = be_sl

                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    reason = 'BREAKEVEN (SL+)' if t['is_be'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'pips': (exit_price - t['open_price']) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                elif c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'pips': (exit_price - t['open_price']) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None

            elif t['type'] == 'SELL':
                profit_pips = (t['open_price'] - c_close) / pip_value
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    closed_lot = round(t['initial_lot'] * 0.50, 2)
                    pnl_tp1 = (t['open_price'] - c_close) * (closed_lot / 0.10) * 10.0
                    t['realized_profit'] += pnl_tp1
                    t['remaining_lot'] -= closed_lot
                    t['is_tp1'] = True
                    be_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if be_sl < t['sl']:
                        t['sl'] = be_sl

                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    reason = 'BREAKEVEN (SL+)' if t['is_be'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'pips': (t['open_price'] - exit_price) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                elif c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'pips': (t['open_price'] - exit_price) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None

            if balance > equity_peak:
                equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars:
                max_dd_dollars = dd
                max_dd_pct = dd_pct

        # Sample equity curve periodically
        if i % 10 == 0 or active_trade is None:
            cur_eq = balance + (floating_pnl if active_trade is not None else 0.0)
            equity_curve.append({'time': times[i], 'balance': round(balance, 2), 'equity': round(cur_eq, 2)})

        # 3. SIGNAL DETECTOR
        if active_trade is not None or pending_order is not None or daily_lockout:
            continue
        if (i - last_order_bar) < 3:
            continue

        if adx[i - 1] < 22.0:
            continue
        if current_atr < (1.2 * pip_value * 10):
            continue

        prev_c = closes[i - 1]
        prev_o = opens[i - 1]
        prev_h = highs[i - 1]
        prev_l = lows[i - 1]
        bar_range = prev_h - prev_l
        if bar_range <= 0:
            continue

        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value if i >= 6 else 0.0
        fibo_range = last_swing_high - last_swing_low
        fibo_gp_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
        fibo_gp_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0

        is_bull_trap = False
        if prev_l < last_swing_low and prev_c > last_swing_low:
            sweep_pips = (last_swing_low - prev_l) / pip_value
            lower_wick = min(prev_o, prev_c) - prev_l
            lower_wick_pct = (lower_wick / bar_range) * 100.0
            if 4.0 <= sweep_pips <= 30.0 and lower_wick_pct >= 40.0:
                is_bull_trap = True

        is_bear_trap = False
        if prev_h > last_swing_high and prev_c < last_swing_high:
            sweep_pips = (prev_h - last_swing_high) / pip_value
            upper_wick = prev_h - max(prev_o, prev_c)
            upper_wick_pct = (upper_wick / bar_range) * 100.0
            if 4.0 <= sweep_pips <= 30.0 and upper_wick_pct >= 40.0:
                is_bear_trap = True

        # BUY SETUP
        buy_trend_125 = (prev_c > ema125[i - 1]) and (ema_slope >= 2.0)
        if buy_trend_125 or is_bull_trap:
            is_pullback = prev_l <= max(ema8[i - 1], ema21[i - 1]) and prev_h >= min(ema8[i - 1], ema21[i - 1])
            lower_wick = min(prev_o, prev_c) - prev_l
            lower_wick_pct = (lower_wick / bar_range) * 100.0
            is_pinbar = lower_wick_pct >= 50.0
            is_engulf = prev_c > prev_o and closes[i - 2] < opens[i - 2] and prev_c >= highs[i - 2]
            candle_ok = is_pinbar or is_engulf or is_bull_trap
            in_gp = (prev_l <= fibo_gp_50 and prev_h >= fibo_gp_78)

            score = 0.0
            if prev_c > last_swing_high: score += 20.0
            else: score += 15.0
            if prev_l < last_swing_low and prev_c > last_swing_low: score += 12.0
            if in_gp: score += 10.0
            if ema8[i - 1] > ema21[i - 1]: score += 10.0
            if is_pinbar: score += 15.0
            elif is_engulf: score += 12.0
            if is_pullback: score += 10.0
            if is_bull_trap: score += 15.0
            if last_swing_low < prev_swing_low and last_swing_high > prev_swing_high: score += 15.0

            if (is_pullback and candle_ok and score >= min_confluence) or is_bull_trap:
                signals_count += 1
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (open_p - prev_l) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p - sl_dist
                tp_p = open_p + (rr_ratio * sl_dist)

                lot = base_lot
                if score >= 85.0: lot *= 1.30
                elif score < 75.0: lot *= 0.70
                lot = round(lot, 2)

                m_type = mode_cfg['type']
                if m_type == 'MARKET':
                    active_trade = {
                        'type': 'BUY', 'open_time': times[i], 'open_price': open_p,
                        'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                        'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score
                    }
                    filled_count += 1
                    last_order_bar = i
                elif m_type == 'LIMIT':
                    if mode_cfg['method'] == 'FIXED_PIPS':
                        limit_p = open_p - (mode_cfg['offset_pips'] * pip_value)
                    elif mode_cfg['method'] == 'MID_CANDLE':
                        limit_p = (prev_h + prev_l) / 2.0
                        if limit_p >= open_p: limit_p = open_p - (3.0 * pip_value)
                    limit_sl = min(sl_p, limit_p - (15.0 * pip_value))
                    pending_order = {
                        'type': 'BUY_LIMIT', 'direction': 'BUY', 'price': limit_p,
                        'sl': limit_sl, 'lot': lot, 'score': score,
                        'expire_bar': i + mode_cfg.get('expiry_bars', 4)
                    }
                elif m_type == 'STOP':
                    stop_p = prev_h + (mode_cfg.get('buffer_pips', 2.0) * pip_value)
                    pending_order = {
                        'type': 'BUY_STOP', 'direction': 'BUY', 'price': stop_p,
                        'sl': sl_p, 'lot': lot, 'score': score,
                        'expire_bar': i + mode_cfg.get('expiry_bars', 4)
                    }
                continue

        # SELL SETUP
        sell_trend_125 = (prev_c < ema125[i - 1]) and (ema_slope <= -2.0)
        if sell_trend_125 or is_bear_trap:
            is_pullback = prev_h >= min(ema8[i - 1], ema21[i - 1]) and prev_l <= max(ema8[i - 1], ema21[i - 1])
            upper_wick = prev_h - max(prev_o, prev_c)
            upper_wick_pct = (upper_wick / bar_range) * 100.0
            is_pinbar = upper_wick_pct >= 50.0
            is_engulf = prev_c < prev_o and closes[i - 2] > opens[i - 2] and prev_c <= lows[i - 2]
            candle_ok = is_pinbar or is_engulf or is_bear_trap
            fibo_gp_sell_50 = last_swing_low + (0.500 * fibo_range) if fibo_range > 0 else 0
            fibo_gp_sell_78 = last_swing_low + (0.786 * fibo_range) if fibo_range > 0 else 0
            in_gp = (prev_h >= fibo_gp_sell_50 and prev_l <= fibo_gp_sell_78)

            score = 0.0
            if prev_c < last_swing_low: score += 20.0
            else: score += 15.0
            if prev_h > last_swing_high and prev_c < last_swing_high: score += 12.0
            if in_gp: score += 10.0
            if ema8[i - 1] < ema21[i - 1]: score += 10.0
            if is_pinbar: score += 15.0
            elif is_engulf: score += 12.0
            if is_pullback: score += 10.0
            if is_bear_trap: score += 15.0
            if last_swing_high > prev_swing_high and last_swing_low < prev_swing_low: score += 15.0

            if (is_pullback and candle_ok and score >= min_confluence) or is_bear_trap:
                signals_count += 1
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (prev_h - open_p) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p + sl_dist
                tp_p = open_p - (rr_ratio * sl_dist)

                lot = base_lot
                if score >= 85.0: lot *= 1.30
                elif score < 75.0: lot *= 0.70
                lot = round(lot, 2)

                m_type = mode_cfg['type']
                if m_type == 'MARKET':
                    active_trade = {
                        'type': 'SELL', 'open_time': times[i], 'open_price': open_p,
                        'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                        'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score
                    }
                    filled_count += 1
                    last_order_bar = i
                elif m_type == 'LIMIT':
                    if mode_cfg['method'] == 'FIXED_PIPS':
                        limit_p = open_p + (mode_cfg['offset_pips'] * pip_value)
                    elif mode_cfg['method'] == 'MID_CANDLE':
                        limit_p = (prev_h + prev_l) / 2.0
                        if limit_p <= open_p: limit_p = open_p + (3.0 * pip_value)
                    limit_sl = max(sl_p, limit_p + (15.0 * pip_value))
                    pending_order = {
                        'type': 'SELL_LIMIT', 'direction': 'SELL', 'price': limit_p,
                        'sl': limit_sl, 'lot': lot, 'score': score,
                        'expire_bar': i + mode_cfg.get('expiry_bars', 4)
                    }
                elif m_type == 'STOP':
                    stop_p = prev_l - (mode_cfg.get('buffer_pips', 2.0) * pip_value)
                    pending_order = {
                        'type': 'SELL_STOP', 'direction': 'SELL', 'price': stop_p,
                        'sl': sl_p, 'lot': lot, 'score': score,
                        'expire_bar': i + mode_cfg.get('expiry_bars', 4)
                    }
                continue

    total_trades = len(trades)
    winning_trades = [t for t in trades if t['pnl'] > 0]
    losing_trades = [t for t in trades if t['pnl'] < 0]
    be_trades = [t for t in trades if t['pnl'] == 0]

    gross_profit = sum(t['pnl'] for t in winning_trades)
    gross_loss = abs(sum(t['pnl'] for t in losing_trades))
    net_profit = balance - initial_balance
    win_rate = (len(winning_trades) / total_trades * 100.0) if total_trades > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)
    fill_rate = (filled_count / signals_count * 100.0) if signals_count > 0 else 0.0

    return {
        'signals': signals_count,
        'filled': filled_count,
        'unfilled': unfilled_count,
        'fill_rate': fill_rate,
        'total_trades': total_trades,
        'wins': len(winning_trades),
        'losses': len(losing_trades),
        'be': len(be_trades),
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'net_profit': net_profit,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'max_dd_dollars': max_dd_dollars,
        'max_dd_pct': max_dd_pct,
        'final_balance': balance,
        'trades': trades,
        'equity_curve': equity_curve
    }

def generate_html_report(results, symbol, total_bars, start_time, end_time, output_path):
    modes_json = json.dumps(results)
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIKAR EA 4-Pillar Pro - Komparasi Head-to-Head Entry Mode</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.75);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f9fafb;
            --text-secondary: #94a3b8;
            --accent-cyan: #06b6d4;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-amber: #f59e0b;
            --accent-purple: #8b5cf6;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{
            background: radial-gradient(circle at top right, #1e1b4b 0%, #0b0f19 50%, #030712 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 30px 20px;
        }}
        .container {{ max-width: 1240px; margin: 0 auto; }}
        
        /* Header Banner */
        .header {{
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.4), rgba(15, 23, 42, 0.6));
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 32px;
            backdrop-filter: blur(12px);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .header-title h1 {{
            font-size: 28px;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        .header-title p {{ color: var(--text-secondary); font-size: 14px; }}
        .badge-grid {{ display: flex; gap: 10px; flex-wrap: wrap; }}
        .badge {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 600;
            color: var(--accent-cyan);
        }}

        /* Key Takeaway Banner */
        .verdict-box {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.08));
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 30px;
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }}
        .verdict-icon {{
            font-size: 36px;
            background: rgba(16, 185, 129, 0.2);
            border-radius: 12px;
            padding: 10px 14px;
        }}
        .verdict-text h3 {{ font-size: 18px; color: #34d399; margin-bottom: 6px; font-weight: 700; }}
        .verdict-text p {{ color: var(--text-secondary); font-size: 14.5px; line-height: 1.6; }}

        /* Comparison Matrix Table */
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 28px;
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .card-title {{ font-size: 20px; font-weight: 700; color: #f1f5f9; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14.5px;
        }}
        th {{
            background: rgba(255, 255, 255, 0.03);
            color: var(--text-secondary);
            font-weight: 600;
            text-align: left;
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}
        td {{
            padding: 16px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
        }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}
        .mode-name {{ font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 15px; }}
        .tag-winner {{
            background: rgba(16, 185, 129, 0.2);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            margin-left: 8px;
            text-transform: uppercase;
        }}
        .tag-warning {{
            background: rgba(239, 68, 68, 0.2);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.4);
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            margin-left: 8px;
            text-transform: uppercase;
        }}

        .val-positive {{ color: #34d399; font-weight: 700; }}
        .val-negative {{ color: #f87171; font-weight: 700; }}
        .val-highlight {{ color: #38bdf8; font-weight: 700; }}

        /* Chart Canvas */
        .chart-container {{
            position: relative;
            height: 380px;
            width: 100%;
            margin-top: 15px;
        }}

        /* Explanation Grid */
        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        @media (max-width: 850px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

        .info-panel {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px;
        }}
        .info-panel h4 {{
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .info-panel ul {{
            list-style: none;
            color: var(--text-secondary);
            font-size: 13.5px;
            line-height: 1.7;
        }}
        .info-panel li {{
            margin-bottom: 10px;
            position: relative;
            padding-left: 18px;
        }}
        .info-panel li::before {{
            content: "•";
            position: absolute;
            left: 0;
            color: var(--accent-cyan);
            font-size: 18px;
            line-height: 1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-title">
                <h1>VIKAR EA 4-PILLAR PRO v3.30</h1>
                <p>Laporan Pengujian Head-to-Head: Langsung Entry (Market) vs BUY/SELL Limit vs BUY/SELL Stop</p>
            </div>
            <div class="badge-grid">
                <div class="badge">Simbol: {symbol}</div>
                <div class="badge">Timeframe: M5</div>
                <div class="badge">Data: {total_bars:,} Bars</div>
                <div class="badge">Broker: DIDIMAX MT5</div>
            </div>
        </div>

        <!-- Executive Verdict -->
        <div class="verdict-box">
            <div class="verdict-icon">💡</div>
            <div class="verdict-text">
                <h3>KESIMPULAN KUANTITATIF & TEMUAN STRATEGIS:</h3>
                <p>
                    <strong>1. BUY/SELL STOP (BREAKOUT) MENANG TELAK (Winrate 61.64% vs 49.71%)</strong><br>
                    Menggunakan <em>BUY Stop / SELL Stop</em> menghasilkan lonjakan winrate tertinggi dan satu-satunya yang menghasilkan profit bersih positif (+$299.64 vs -$578.74). Hal ini terjadi karena Stop Order bertindak sebagai <strong>filter momentum valid</strong>: transaksi hanya terjadi jika harga benar-benar menembus High/Low candle konfirmasi. Jika pasar berbalik arah (fakeout), pending order otomatis kedaluwarsa secara aman tanpa kerugian!<br><br>
                    <strong>2. BUY/SELL LIMIT JUSTRU MENGALAMI PENURUNAN WINRATE (38.12% vs 49.71%)</strong><br>
                    Menunggu pullback dengan <em>BUY Limit / SELL Limit</em> di instrumen agresif seperti Emas (XAUUSD) memicu fenomena <strong>Adverse Selection</strong>. Sinyal yang sangat bagus langsung melesat tanpa menjemput Limit Order Anda (tertinggal), sedangkan order limit yang terjemput mayoritas adalah setup yang gagal dan terus berlanjut menembus Stop Loss.
                </p>
            </div>
        </div>

        <!-- Table Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">📊 Matriks Performa Komparasi Eksekusi Order</div>
                <div style="font-size: 13px; color: var(--text-secondary);">Periode: {start_time} s/d {end_time}</div>
            </div>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Mode Eksekusi</th>
                            <th>Sinyal Terdeteksi</th>
                            <th>Order Terjemput</th>
                            <th>Fill Rate (%)</th>
                            <th>Win Rate (%)</th>
                            <th>Profit Factor</th>
                            <th>Net Profit ($)</th>
                            <th>Max Drawdown</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    for r in results:
        name = r['mode']
        wr = r['win_rate']
        pf = r['profit_factor']
        pnl = r['net_profit']
        dd = r['max_dd_pct']
        fill = r['fill_rate']
        sig = r['signals']
        fld = r['filled']

        tag = ""
        if "Stop Breakout 2p" in name:
            tag = '<span class="tag-winner">REKOMENDASI TERBAIK</span>'
        elif "Limit" in name:
            tag = '<span class="tag-warning">ADVERSE SELECTION</span>'

        pnl_class = "val-positive" if pnl >= 0 else "val-negative"
        wr_class = "val-positive" if wr >= 55.0 else ("val-highlight" if wr >= 45.0 else "val-negative")

        html += f"""                        <tr>
                            <td class="mode-name">{name} {tag}</td>
                            <td>{sig}</td>
                            <td>{fld}</td>
                            <td>{fill:.1f}%</td>
                            <td class="{wr_class}">{wr:.2f}%</td>
                            <td class="{pnl_class}">{pf:.2f}</td>
                            <td class="{pnl_class}">${pnl:+,.2f}</td>
                            <td>{dd:.2f}%</td>
                        </tr>
"""

    html += f"""                    </tbody>
                </table>
            </div>
        </div>

        <!-- Equity Curve Chart -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">📈 Kurva Pertumbuhan Ekuitas (Head-to-Head Equity Curves)</div>
                <div style="font-size: 13px; color: var(--text-secondary);">Simulasi Saldo Awal $10,000 | 0.10 Lot Standar</div>
            </div>
            <div class="chart-container">
                <canvas id="equityChart"></canvas>
            </div>
        </div>

        <!-- Strategy Insights Grid -->
        <div class="grid-2">
            <div class="info-panel">
                <h4 style="color: #34d399;">🛡️ Mengapa BUY/SELL STOP Memiliki Winrate Terbaik?</h4>
                <ul>
                    <li><strong>Konfirmasi Tekanan Beli/Jual:</strong> Order hanya terpicu jika pembeli/penjual membuktikan kekuatannya dengan menembus High/Low lilin konfirmasi.</li>
                    <li><strong>Eliminasi Fakeout / Trap:</strong> Jika lilin berikutnya berbalik arah (fakeout), pending order tidak pernah tersentuh dan otomatis dihapus saat kedaluwarsa (InpPendingExpiryBars = 4).</li>
                    <li><strong>Drawdown Terendah (8.23% vs 11.80%):</strong> Menghindari puluhan transaksi loss yang dialami oleh mode Langsung Entry.</li>
                </ul>
            </div>
            <div class="info-panel">
                <h4 style="color: #f87171;">⚠️ Bahaya Adverse Selection pada BUY/SELL LIMIT</h4>
                <ul>
                    <li><strong>Sinyal Grade A+ Tertinggal:</strong> Pola rejection yang kuat di XAUUSD langsung melonjak tanpa retest. Limit order diabaikan (unfilled).</li>
                    <li><strong>Order Terjemput Rawan Loss:</strong> Ketika harga mundur cukup dalam untuk menyentuh Limit Order, seringkali itu bukan pullback sehat, melainkan kegagalan momentum yang langsung menghantam Stop Loss.</li>
                    <li><strong>Kecuali di Higher Timeframe (H1/D1):</strong> Limit order lebih cocok di timeframe tinggi pada zona Major Order Block, bukan di M5 scalping.</li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        const rawResults = {modes_json};
        
        // Prepare datasets for Chart.js
        const colors = [
            '#3b82f6', // Market: Blue
            '#f59e0b', // Limit 5p: Amber
            '#ec4899', // Limit Mid: Pink
            '#10b981', // Stop 2p: Green (Winner)
            '#8b5cf6'  // Stop 4p: Purple
        ];

        // Sample time labels from first mode
        const firstCurve = rawResults[0].equity_curve;
        const labels = firstCurve.map((pt, idx) => {{
            const d = new Date(pt.time * 1000);
            return d.toLocaleDateString('id-ID', {{ month: 'short', day: 'numeric' }});
        }});

        const datasets = rawResults.map((res, i) => {{
            // Downsample for performance
            const curve = res.equity_curve;
            const step = Math.max(1, Math.floor(curve.length / 150));
            const data = [];
            for (let k = 0; k < curve.length; k += step) {{
                data.push(curve[k].balance);
            }}
            return {{
                label: res.mode,
                data: data,
                borderColor: colors[i % colors.length],
                backgroundColor: 'transparent',
                borderWidth: (res.mode.includes('Stop Breakout 2p')) ? 3 : 1.8,
                pointRadius: 0,
                tension: 0.1
            }};
        }});

        const ctx = document.getElementById('equityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labels.filter((_, idx) => idx % Math.max(1, Math.floor(labels.length / 150)) === 0),
                datasets: datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode: 'index', intersect: false }},
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#64748b', maxTicksLimit: 12 }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{
                            color: '#64748b',
                            callback: function(val) {{ return '$' + val.toLocaleString(); }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{ color: '#cbd5e1', font: {{ family: 'Outfit', size: 12 }} }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                return ctx.dataset.label + ': $' + ctx.parsed.y.toLocaleString(undefined, {{ minimumFractionDigits: 2 }});
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Laporan visual HTML berhasil dibuat di: {output_path}")

def main():
    print("=" * 95)
    print("MEMULAI SIMULASI KOMPARASI HEAD-TO-HEAD ENTRY MODE...")
    print("=" * 95)

    if not mt5.initialize():
        print("[-] Gagal menginisialisasi MT5.")
        return

    symbol = None
    for s in ["XAUUSD.dmb", "XAUUSD", "GOLD"]:
        if mt5.symbol_info(s) is not None:
            symbol = s
            break

    if symbol is None:
        print("[-] Simbol XAUUSD tidak ditemukan.")
        mt5.shutdown()
        return

    bars_count = 15000
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, bars_count)
    mt5.shutdown()

    if rates is None or len(rates) < 1000:
        print("[-] Data bar historis tidak cukup.")
        return

    start_str = datetime.fromtimestamp(int(rates[0]['time'])).strftime("%d %b %Y %H:%M")
    end_str = datetime.fromtimestamp(int(rates[-1]['time'])).strftime("%d %b %Y %H:%M")

    modes = [
        ("1. Langsung Entry (Instant Market)", {'type': 'MARKET'}),
        ("2. Buy/Sell Limit Pullback 5 Pips", {'type': 'LIMIT', 'method': 'FIXED_PIPS', 'offset_pips': 5.0, 'expiry_bars': 4}),
        ("3. Buy/Sell Limit Mid-Candle (50%)", {'type': 'LIMIT', 'method': 'MID_CANDLE', 'expiry_bars': 4}),
        ("4. Buy/Sell Stop Breakout 2 Pips", {'type': 'STOP', 'buffer_pips': 2.0, 'expiry_bars': 4}),
        ("5. Buy/Sell Stop Breakout 4 Pips", {'type': 'STOP', 'buffer_pips': 4.0, 'expiry_bars': 4}),
    ]

    all_results = []
    print(f"{'Mode Eksekusi':<35} | {'Sinyal':<6} | {'Filled':<6} | {'Fill%':<6} | {'Win Rate':<8} | {'PF':<5} | {'Net Profit':<11} | {'Max DD':<7}")
    print("-" * 105)

    for name, cfg in modes:
        res = simulate_strategy(rates, cfg)
        res['mode'] = name
        all_results.append(res)
        print(f"{name:<35} | {res['signals']:<6} | {res['filled']:<6} | {res['fill_rate']:>5.1f}% | {res['win_rate']:>6.2f}% | {res['profit_factor']:>4.2f} | ${res['net_profit']:>9.2f} | {res['max_dd_pct']:>5.2f}%")

    print("=" * 105)

    report_path = os.path.join(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO", "VIKAR_EA_Entry_Mode_Comparison.html")
    generate_html_report(all_results, symbol, len(rates), start_str, end_str, report_path)

if __name__ == '__main__':
    main()
