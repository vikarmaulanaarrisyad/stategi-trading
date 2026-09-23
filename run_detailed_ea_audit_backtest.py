"""
VIKAR EA 4-PILLAR PRO - COMPREHENSIVE BACKTEST AUDITOR & OPTIMIZER
Menganalisis kinerja EA pada 15,000 bar data riil broker Didimax MT5 (XAUUSD.dmb).
Mendeteksi kelemahan: jam trading yang sering loss, pemicu drawdown terbesar,
rasio TP/SL optimal, serta perbandingan mode eksekusi.
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

def calculate_choppiness(highs, lows, closes, period=14):
    n = len(closes)
    ci = [50.0] * n
    for i in range(period, n):
        sum_tr = 0.0
        for k in range(i - period + 1, i + 1):
            sum_tr += max(highs[k] - lows[k], abs(highs[k] - closes[k - 1]), abs(lows[k] - closes[k - 1]))
        max_h = max(highs[i - period + 1:i + 1])
        min_l = min(lows[i - period + 1:i + 1])
        range_hl = max_h - min_l
        if range_hl > 0 and sum_tr > 0:
            ci_val = 100.0 * (math.log10(sum_tr / range_hl) / math.log10(period))
            ci[i] = max(0.0, min(100.0, ci_val))
        else:
            ci[i] = 50.0
    return ci

def run_simulation(rates_raw, config):
    times = [int(r['time']) for r in rates_raw]
    opens = [float(r['open']) for r in rates_raw]
    highs = [float(r['high']) for r in rates_raw]
    lows = [float(r['low']) for r in rates_raw]
    closes = [float(r['close']) for r in rates_raw]
    n = len(closes)

    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)
    atr = calculate_atr(highs, lows, closes, 14)
    adx = calculate_adx(highs, lows, closes, 14)
    ci = calculate_choppiness(highs, lows, closes, 14)

    min_confluence = config.get('min_confluence', 65.0)
    be_trigger_pips = config.get('be_trigger_pips', 12.0)
    be_lock_pips = config.get('be_lock_pips', 4.0)
    tp1_trigger_pips = config.get('tp1_trigger_pips', 15.0)
    rr_ratio = config.get('rr_ratio', 2.0)
    mode = config.get('mode', 'STOP')  # STOP, MARKET, LIMIT
    stop_buffer_pips = config.get('stop_buffer_pips', 2.0)
    limit_offset_pips = config.get('limit_offset_pips', 5.0)
    expiry_bars = config.get('expiry_bars', 4)
    filter_choppy = config.get('filter_choppy', True)
    filter_asian = config.get('filter_asian', False)
    use_trailing = config.get('use_trailing', True)
    trailing_buffer = config.get('trailing_buffer_pips', 5.0)

    pip_value = 0.10  # 1 pip on XAUUSD (2 digits) = $0.10
    initial_balance = 10000.0
    balance = initial_balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0

    active_trade = None
    pending_order = None
    last_order_bar = -999
    daily_lockout = False
    current_day = -1
    today_pnl = 0.0

    trades = []
    hourly_stats = {h: {'trades': 0, 'wins': 0, 'pnl': 0.0} for h in range(24)}
    day_stats = {d: {'trades': 0, 'wins': 0, 'pnl': 0.0} for d in range(7)}

    for i in range(130, n):
        dt = datetime.fromtimestamp(times[i])
        day_num = dt.weekday()
        hour = dt.hour

        if dt.day != current_day:
            current_day = dt.day
            daily_lockout = False
            today_pnl = 0.0

        c_open, c_high, c_low, c_close = opens[i], highs[i], lows[i], closes[i]
        prev_o, prev_h, prev_l, prev_c = opens[i - 1], highs[i - 1], lows[i - 1], closes[i - 1]
        current_atr = atr[i] if atr[i] > 0 else 1.5

        # 1. PENDING ORDER CHECK
        if pending_order is not None:
            p_type = pending_order['type']
            p_price = pending_order['price']
            p_sl = pending_order['sl']
            p_lot = pending_order['lot']
            filled = False

            if p_type == 'BUY_STOP' and c_high >= p_price:
                filled = True
                exec_p = max(c_open, p_price)
                tp_p = exec_p + (rr_ratio * (exec_p - p_sl))
                active_trade = {
                    'type': 'BUY', 'open_time': times[i], 'open_price': exec_p,
                    'sl': p_sl, 'tp': tp_p, 'initial_lot': p_lot, 'remaining_lot': p_lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': pending_order['score'],
                    'open_hour': hour, 'open_day': day_num
                }
            elif p_type == 'SELL_STOP' and c_low <= p_price:
                filled = True
                exec_p = min(c_open, p_price)
                tp_p = exec_p - (rr_ratio * (p_sl - exec_p))
                active_trade = {
                    'type': 'SELL', 'open_time': times[i], 'open_price': exec_p,
                    'sl': p_sl, 'tp': tp_p, 'initial_lot': p_lot, 'remaining_lot': p_lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': pending_order['score'],
                    'open_hour': hour, 'open_day': day_num
                }
            elif p_type == 'BUY_LIMIT' and c_low <= p_price:
                filled = True
                exec_p = min(c_open, p_price)
                tp_p = exec_p + (rr_ratio * (exec_p - p_sl))
                active_trade = {
                    'type': 'BUY', 'open_time': times[i], 'open_price': exec_p,
                    'sl': p_sl, 'tp': tp_p, 'initial_lot': p_lot, 'remaining_lot': p_lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': pending_order['score'],
                    'open_hour': hour, 'open_day': day_num
                }
            elif p_type == 'SELL_LIMIT' and c_high >= p_price:
                filled = True
                exec_p = max(c_open, p_price)
                tp_p = exec_p - (rr_ratio * (p_sl - exec_p))
                active_trade = {
                    'type': 'SELL', 'open_time': times[i], 'open_price': exec_p,
                    'sl': p_sl, 'tp': tp_p, 'initial_lot': p_lot, 'remaining_lot': p_lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': pending_order['score'],
                    'open_hour': hour, 'open_day': day_num
                }

            if filled:
                pending_order = None
                last_order_bar = i
            elif i >= pending_order['expire_bar']:
                pending_order = None

        # 2. ACTIVE TRADE MANAGEMENT
        if active_trade is not None:
            t = active_trade
            if t['type'] == 'BUY':
                profit_pips = (c_close - t['open_price']) / pip_value
                # Breakeven
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # Partial Close TP1 (50%)
                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    closed_lot = round(t['initial_lot'] * 0.50, 2)
                    pnl_tp1 = (c_close - t['open_price']) * (closed_lot / 0.10) * 10.0
                    t['realized_profit'] += pnl_tp1
                    t['remaining_lot'] -= closed_lot
                    t['is_tp1'] = True
                    be_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if be_sl > t['sl']:
                        t['sl'] = be_sl

                # Trailing Stop via EMA 21
                if use_trailing and t['is_be']:
                    trail_sl = ema21[i - 1] - (trailing_buffer * pip_value)
                    if trail_sl > t['sl'] and (c_close - trail_sl) >= (15 * pip_value):
                        t['sl'] = trail_sl

                # Exit checks
                if c_low <= t['sl']:
                    exit_p = t['sl']
                    pnl = t['realized_profit'] + ((exit_p - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    today_pnl += pnl
                    reason = 'BREAKEVEN (SL+)' if t['is_be'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'hour': t['open_hour'], 'day': t['open_day']})
                    active_trade = None
                elif c_high >= t['tp']:
                    exit_p = t['tp']
                    pnl = t['realized_profit'] + ((exit_p - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    today_pnl += pnl
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'hour': t['open_hour'], 'day': t['open_day']})
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

                if use_trailing and t['is_be']:
                    trail_sl = ema21[i - 1] + (trailing_buffer * pip_value)
                    if trail_sl < t['sl'] and (trail_sl - c_close) >= (15 * pip_value):
                        t['sl'] = trail_sl

                if c_high >= t['sl']:
                    exit_p = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_p) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    today_pnl += pnl
                    reason = 'BREAKEVEN (SL+)' if t['is_be'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'hour': t['open_hour'], 'day': t['open_day']})
                    active_trade = None
                elif c_low <= t['tp']:
                    exit_p = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_p) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    today_pnl += pnl
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'hour': t['open_hour'], 'day': t['open_day']})
                    active_trade = None

            if balance > equity_peak:
                equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars:
                max_dd_dollars = dd
                max_dd_pct = dd_pct

            # Daily DD kill switch (4%)
            if today_pnl < -(initial_balance * 0.04):
                daily_lockout = True

        # 3. SIGNAL GENERATION
        if active_trade is not None or pending_order is not None or daily_lockout:
            continue
        if (i - last_order_bar) < 3:
            continue

        # Asian session filter (hour 0-5 broker time = low liquidity, high spread)
        if filter_asian and (hour >= 23 or hour < 6):
            continue

        # Anti-choppy filter
        if filter_choppy and ci[i - 1] > 61.8:
            continue

        # ADX power filter
        if adx[i - 1] < 20.0:
            continue

        # Swing detection
        lookback = 30
        last_swing_high = max(highs[max(0, i - lookback):i - 1])
        last_swing_low = min(lows[max(0, i - lookback):i - 1])
        fibo_range = last_swing_high - last_swing_low

        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
        bar_range = prev_h - prev_l if prev_h > prev_l else (0.01)

        # Bull Trap detection
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
            fibo_gp_buy_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
            fibo_gp_buy_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0
            in_gp = (prev_l <= fibo_gp_buy_50 and prev_h >= fibo_gp_buy_78)

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

            if (is_pullback and candle_ok and score >= min_confluence) or is_bull_trap:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (open_p - prev_l) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p - sl_dist
                tp_p = open_p + (rr_ratio * sl_dist)
                lot = 0.10

                if mode == 'MARKET':
                    active_trade = {
                        'type': 'BUY', 'open_time': times[i], 'open_price': open_p,
                        'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                        'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score,
                        'open_hour': hour, 'open_day': day_num
                    }
                    last_order_bar = i
                elif mode == 'STOP':
                    stop_p = prev_h + (stop_buffer_pips * pip_value)
                    pending_order = {
                        'type': 'BUY_STOP', 'price': stop_p, 'sl': sl_p,
                        'lot': lot, 'score': score, 'expire_bar': i + expiry_bars
                    }
                elif mode == 'LIMIT':
                    limit_p = open_p - (limit_offset_pips * pip_value)
                    pending_order = {
                        'type': 'BUY_LIMIT', 'price': limit_p, 'sl': sl_p,
                        'lot': lot, 'score': score, 'expire_bar': i + expiry_bars
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

            if (is_pullback and candle_ok and score >= min_confluence) or is_bear_trap:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (prev_h - open_p) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p + sl_dist
                tp_p = open_p - (rr_ratio * sl_dist)
                lot = 0.10

                if mode == 'MARKET':
                    active_trade = {
                        'type': 'SELL', 'open_time': times[i], 'open_price': open_p,
                        'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                        'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score,
                        'open_hour': hour, 'open_day': day_num
                    }
                    last_order_bar = i
                elif mode == 'STOP':
                    stop_p = prev_l - (stop_buffer_pips * pip_value)
                    pending_order = {
                        'type': 'SELL_STOP', 'price': stop_p, 'sl': sl_p,
                        'lot': lot, 'score': score, 'expire_bar': i + expiry_bars
                    }
                elif mode == 'LIMIT':
                    limit_p = open_p + (limit_offset_pips * pip_value)
                    pending_order = {
                        'type': 'SELL_LIMIT', 'price': limit_p, 'sl': sl_p,
                        'lot': lot, 'score': score, 'expire_bar': i + expiry_bars
                    }
                continue

    # Compile statistics
    total_trades = len(trades)
    winning = [t for t in trades if t['pnl'] > 0]
    losing = [t for t in trades if t['pnl'] < 0]
    be = [t for t in trades if t['pnl'] == 0]

    gross_profit = sum(t['pnl'] for t in winning)
    gross_loss = abs(sum(t['pnl'] for t in losing))
    net_profit = balance - initial_balance
    win_rate = (len(winning) / total_trades * 100.0) if total_trades > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)

    # Exits breakdown
    exit_counts = {}
    for t in trades:
        r = t['reason']
        exit_counts[r] = exit_counts.get(r, 0) + 1

    # Hourly breakdown
    for t in trades:
        h = t['hour']
        hourly_stats[h]['trades'] += 1
        if t['pnl'] > 0: hourly_stats[h]['wins'] += 1
        hourly_stats[h]['pnl'] += t['pnl']

    return {
        'total_trades': total_trades,
        'wins': len(winning),
        'losses': len(losing),
        'be': len(be),
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'net_profit': net_profit,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'max_dd_pct': max_dd_pct,
        'exit_counts': exit_counts,
        'hourly_stats': hourly_stats,
        'trades': trades
    }

def main():
    print("=" * 80)
    print("AUDIT & BACKTEST EVALUASI STRATEGI EA VIKAR 4-PILLAR PRO")
    print("=" * 80)

    if not mt5.initialize():
        print("[-] Gagal inisialisasi MT5.")
        return

    symbol = "XAUUSD.dmb"
    print(f"[+] Menarik 15,000 bar M5 & 10,000 bar M15 {symbol}...")
    rates_m5 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 15000)
    rates_m15 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 10000)
    mt5.shutdown()

    if rates_m5 is None:
        print("[-] Data M5 kosong.")
        return

    print(f"[+] Berhasil memuat {len(rates_m5)} bar M5 & {len(rates_m15)} bar M15.")

    experiments = [
        ("1. Standard M5 - Market Instant", rates_m5, {'mode': 'MARKET', 'filter_asian': False, 'min_confluence': 65.0}),
        ("2. Standard M5 - Stop Breakout (2p)", rates_m5, {'mode': 'STOP', 'stop_buffer_pips': 2.0, 'filter_asian': False, 'min_confluence': 65.0}),
        ("3. M5 Stop Breakout + Asian Filter (Skip 23:00-06:00)", rates_m5, {'mode': 'STOP', 'stop_buffer_pips': 2.0, 'filter_asian': True, 'min_confluence': 65.0}),
        ("4. M5 Stop Breakout + Confluence Tinggi (70 Skor)", rates_m5, {'mode': 'STOP', 'stop_buffer_pips': 2.0, 'filter_asian': True, 'min_confluence': 70.0}),
        ("5. Standard M15 - Stop Breakout (2p)", rates_m15, {'mode': 'STOP', 'stop_buffer_pips': 2.0, 'filter_asian': False, 'min_confluence': 65.0}),
        ("6. M15 Stop Breakout + Asian Filter", rates_m15, {'mode': 'STOP', 'stop_buffer_pips': 2.0, 'filter_asian': True, 'min_confluence': 65.0}),
    ]

    print("\n" + "=" * 95)
    print(f"{'Konfigurasi / Eksperimen':<45} | {'Trades':<6} | {'Win%':<7} | {'PF':<5} | {'Net Profit':<11} | {'Max DD%':<7}")
    print("-" * 95)

    results = []
    for name, r_data, cfg in experiments:
        res = run_simulation(r_data, cfg)
        results.append((name, res, cfg))
        print(f"{name:<45} | {res['total_trades']:<6} | {res['win_rate']:>5.1f}% | {res['profit_factor']:>4.2f} | ${res['net_profit']:>9.2f} | {res['max_dd_pct']:>5.2f}%")
    print("=" * 95)

    # Analisis Audit Mendalam pada Skenario Terbaik
    best = max(results, key=lambda x: x[1]['net_profit'])
    print(f"\n[HASIL AUDIT TERBAIK]: {best[0]}")
    b_res = best[1]
    print(f"- Total Trades  : {b_res['total_trades']} ({b_res['wins']} Win / {b_res['losses']} Loss / {b_res['be']} BE)")
    print(f"- Win Rate      : {b_res['win_rate']:.2f}%")
    print(f"- Profit Factor : {b_res['profit_factor']:.2f}")
    print(f"- Net Profit    : ${b_res['net_profit']:.2f}")
    print(f"- Max Drawdown  : {b_res['max_dd_pct']:.2f}%")
    print(f"- Distribusi Exit: {b_res['exit_counts']}")

    # Hourly Win Rate Audit
    print("\n[AUDIT KINERJA PER JAM (00:00 - 23:00 Broker)]: ")
    print(f"{'Jam':<5} | {'Trades':<7} | {'Win%':<7} | {'Net PnL':<10}")
    print("-" * 35)
    for h in range(24):
        h_info = b_res['hourly_stats'][h]
        if h_info['trades'] > 0:
            h_wr = (h_info['wins'] / h_info['trades']) * 100.0
            print(f"{h:02d}:00 | {h_info['trades']:<7} | {h_wr:>5.1f}% | ${h_info['pnl']:>8.2f}")

if __name__ == '__main__':
    main()
