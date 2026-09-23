import sys
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

def run_backtest_mode(mode_name, rates_raw, entry_cfg):
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
    require_double_align = False
    require_golden_pocket = False
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

        # --- A. CHECK PENDING ORDER FILL OR EXPIRY ---
        if pending_order is not None and active_trade is None:
            p = pending_order
            # Check expiry
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
                    # Recalculate SL distance from fill price
                    if p['direction'] == 'BUY':
                        sl_dist = fill_price - p['sl']
                        tp_p = fill_price + (rr_ratio * sl_dist)
                    else:
                        sl_dist = p['sl'] - fill_price
                        tp_p = fill_price - (rr_ratio * sl_dist)

                    active_trade = {
                        'type': p['direction'],
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

        # --- B. MANAGE ACTIVE TRADE ---
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
                    'type': t['type'], 'pnl': pnl, 'reason': 'DD KILL-SWITCH',
                    'pips': (exit_price - t['open_price'] if t['type'] == 'BUY' else t['open_price'] - exit_price) / pip_value
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

                # Stop Loss Check
                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    reason = 'BREAKEVEN (SL+)' if t['is_be'] else 'STOP LOSS'
                    trades.append({'type': 'BUY', 'pnl': pnl, 'reason': reason, 'pips': (exit_price - t['open_price']) / pip_value})
                    active_trade = None
                elif c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    trades.append({'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'pips': (exit_price - t['open_price']) / pip_value})
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

                # Stop Loss Check
                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    reason = 'BREAKEVEN (SL+)' if t['is_be'] else 'STOP LOSS'
                    trades.append({'type': 'SELL', 'pnl': pnl, 'reason': reason, 'pips': (t['open_price'] - exit_price) / pip_value})
                    active_trade = None
                elif c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += pnl
                    trades.append({'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'pips': (t['open_price'] - exit_price) / pip_value})
                    active_trade = None

            if balance > equity_peak:
                equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars:
                max_dd_dollars = dd
                max_dd_pct = dd_pct

        # --- C. SIGNAL SCANNING ---
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
        buy_pivot_align = (prev_c > pivot_p) if require_double_align else True

        if (buy_trend_125 and buy_pivot_align) or is_bull_trap:
            is_pullback = prev_l <= max(ema8[i - 1], ema21[i - 1]) and prev_h >= min(ema8[i - 1], ema21[i - 1])
            lower_wick = min(prev_o, prev_c) - prev_l
            lower_wick_pct = (lower_wick / bar_range) * 100.0
            is_pinbar = lower_wick_pct >= 50.0
            is_engulf = prev_c > prev_o and closes[i - 2] < opens[i - 2] and prev_c >= highs[i - 2]
            candle_ok = is_pinbar or is_engulf or is_bull_trap
            in_gp = (prev_l <= fibo_gp_50 and prev_h >= fibo_gp_78)
            fibo_ok = in_gp if require_golden_pocket else True

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

            if (is_pullback and candle_ok and fibo_ok and score >= min_confluence) or is_bull_trap:
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

                mode_type = entry_cfg['type']
                if mode_type == 'MARKET':
                    active_trade = {
                        'type': 'BUY',
                        'open_price': open_p,
                        'sl': sl_p,
                        'tp': tp_p,
                        'initial_lot': lot,
                        'remaining_lot': lot,
                        'is_be': False,
                        'is_tp1': False,
                        'realized_profit': 0.0,
                        'score': score
                    }
                    filled_count += 1
                    last_order_bar = i
                elif mode_type == 'LIMIT':
                    # Calculate Limit Price below Open
                    if entry_cfg['method'] == 'FIXED_PIPS':
                        limit_p = open_p - (entry_cfg['offset_pips'] * pip_value)
                    elif entry_cfg['method'] == 'MID_CANDLE':
                        limit_p = (prev_h + prev_l) / 2.0
                        if limit_p >= open_p:
                            limit_p = open_p - (3.0 * pip_value)
                    limit_sl = min(sl_p, limit_p - (15.0 * pip_value))
                    pending_order = {
                        'type': 'BUY_LIMIT',
                        'direction': 'BUY',
                        'price': limit_p,
                        'sl': limit_sl,
                        'lot': lot,
                        'score': score,
                        'expire_bar': i + entry_cfg.get('expiry_bars', 4)
                    }
                elif mode_type == 'STOP':
                    stop_p = prev_h + (entry_cfg.get('buffer_pips', 2.0) * pip_value)
                    pending_order = {
                        'type': 'BUY_STOP',
                        'direction': 'BUY',
                        'price': stop_p,
                        'sl': sl_p,
                        'lot': lot,
                        'score': score,
                        'expire_bar': i + entry_cfg.get('expiry_bars', 4)
                    }
                continue

        # SELL SETUP
        sell_trend_125 = (prev_c < ema125[i - 1]) and (ema_slope <= -2.0)
        sell_pivot_align = (prev_c < pivot_p) if require_double_align else True

        if (sell_trend_125 and sell_pivot_align) or is_bear_trap:
            is_pullback = prev_h >= min(ema8[i - 1], ema21[i - 1]) and prev_l <= max(ema8[i - 1], ema21[i - 1])
            upper_wick = prev_h - max(prev_o, prev_c)
            upper_wick_pct = (upper_wick / bar_range) * 100.0
            is_pinbar = upper_wick_pct >= 50.0
            is_engulf = prev_c < prev_o and closes[i - 2] > opens[i - 2] and prev_c <= lows[i - 2]
            candle_ok = is_pinbar or is_engulf or is_bear_trap

            fibo_gp_sell_50 = last_swing_low + (0.500 * fibo_range) if fibo_range > 0 else 0
            fibo_gp_sell_78 = last_swing_low + (0.786 * fibo_range) if fibo_range > 0 else 0
            in_gp = (prev_h >= fibo_gp_sell_50 and prev_l <= fibo_gp_sell_78)
            fibo_ok = in_gp if require_golden_pocket else True

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

            if (is_pullback and candle_ok and fibo_ok and score >= min_confluence) or is_bear_trap:
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

                mode_type = entry_cfg['type']
                if mode_type == 'MARKET':
                    active_trade = {
                        'type': 'SELL',
                        'open_price': open_p,
                        'sl': sl_p,
                        'tp': tp_p,
                        'initial_lot': lot,
                        'remaining_lot': lot,
                        'is_be': False,
                        'is_tp1': False,
                        'realized_profit': 0.0,
                        'score': score
                    }
                    filled_count += 1
                    last_order_bar = i
                elif mode_type == 'LIMIT':
                    # Calculate Limit Price above Open
                    if entry_cfg['method'] == 'FIXED_PIPS':
                        limit_p = open_p + (entry_cfg['offset_pips'] * pip_value)
                    elif entry_cfg['method'] == 'MID_CANDLE':
                        limit_p = (prev_h + prev_l) / 2.0
                        if limit_p <= open_p:
                            limit_p = open_p + (3.0 * pip_value)
                    limit_sl = max(sl_p, limit_p + (15.0 * pip_value))
                    pending_order = {
                        'type': 'SELL_LIMIT',
                        'direction': 'SELL',
                        'price': limit_p,
                        'sl': limit_sl,
                        'lot': lot,
                        'score': score,
                        'expire_bar': i + entry_cfg.get('expiry_bars', 4)
                    }
                elif mode_type == 'STOP':
                    stop_p = prev_l - (entry_cfg.get('buffer_pips', 2.0) * pip_value)
                    pending_order = {
                        'type': 'SELL_STOP',
                        'direction': 'SELL',
                        'price': stop_p,
                        'sl': sl_p,
                        'lot': lot,
                        'score': score,
                        'expire_bar': i + entry_cfg.get('expiry_bars', 4)
                    }
                continue

    # Summary Statistics
    total_trades = len(trades)
    winning_trades = [t for t in trades if t['pnl'] > 0]
    losing_trades = [t for t in trades if t['pnl'] < 0]
    be_trades = [t for t in trades if t['pnl'] == 0]

    gross_profit = sum(t['pnl'] for t in winning_trades)
    gross_loss = abs(sum(t['pnl'] for t in losing_trades))
    net_profit = balance - initial_balance
    win_rate = (len(winning_trades) / total_trades * 100.0) if total_trades > 0 else 0.0
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.0
    fill_rate = (filled_count / signals_count * 100.0) if signals_count > 0 else 0.0

    return {
        'mode': mode_name,
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
        'max_dd_dollars': max_dd_dollars,
        'max_dd_pct': max_dd_pct,
        'final_balance': balance
    }

def main():
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
        print("[-] Data bar tidak cukup.")
        return

    print("=" * 90)
    print(f"KOMPARASI HEAD-TO-HEAD ENTRY MODE: VIKAR EA 4-PILLAR PRO")
    print(f"Instrumen: {symbol} | Timeframe: M5 | Total Bar: {len(rates):,}")
    print(f"Periode Data: {datetime.fromtimestamp(int(rates[0]['time']))} s/d {datetime.fromtimestamp(int(rates[-1]['time']))}")
    print("=" * 90)

    modes = [
        ("1. Langsung Entry (Instant Market)", {'type': 'MARKET'}),
        ("2. Buy/Sell Limit Pullback 5 Pips", {'type': 'LIMIT', 'method': 'FIXED_PIPS', 'offset_pips': 5.0, 'expiry_bars': 4}),
        ("3. Buy/Sell Limit Pullback 8 Pips", {'type': 'LIMIT', 'method': 'FIXED_PIPS', 'offset_pips': 8.0, 'expiry_bars': 4}),
        ("4. Buy/Sell Limit Mid-Candle (50%)", {'type': 'LIMIT', 'method': 'MID_CANDLE', 'expiry_bars': 4}),
        ("5. Buy/Sell Stop Breakout 2 Pips", {'type': 'STOP', 'buffer_pips': 2.0, 'expiry_bars': 4}),
    ]

    results = []
    for name, cfg in modes:
        res = run_backtest_mode(name, rates, cfg)
        results.append(res)

    print(f"{'Mode Eksekusi':<35} | {'Sinyal':<6} | {'Filled':<6} | {'Fill%':<6} | {'Trades':<6} | {'Win Rate':<8} | {'PF':<5} | {'Net Profit':<11} | {'Max DD':<7}")
    print("-" * 105)
    for r in results:
        print(f"{r['mode']:<35} | {r['signals']:<6} | {r['filled']:<6} | {r['fill_rate']:>5.1f}% | {r['total_trades']:<6} | {r['win_rate']:>6.2f}% | {r['profit_factor']:>4.2f} | ${r['net_profit']:>9.2f} | {r['max_dd_pct']:>5.2f}%")
    print("=" * 105)

if __name__ == '__main__':
    main()
