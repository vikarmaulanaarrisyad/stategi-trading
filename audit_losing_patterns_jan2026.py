"""
AUDIT POLA CANDLESTICK & KERUGIAN EA (JANUARI 2026 - SEKARANG)
Mengidentifikasi secara presisi pola candlestick mana yang menyebabkan EA terkena Stop Loss (SL)
atau menderita kerugian berulang pada 50,123 Bar M5 XAUUSD.
"""

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

def classify_candle_pattern(o, h, l, c, prev_o, prev_h, prev_l, prev_c, current_atr, is_buy):
    """
    Menganalisis anatomi candlestick saat sinyal terbentuk (bar i-1).
    """
    candle_range = h - l if h > l else 0.01
    body = abs(c - o)
    body_pct = (body / candle_range) * 100.0
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l
    upper_wick_pct = (upper_wick / candle_range) * 100.0
    lower_wick_pct = (lower_wick / candle_range) * 100.0
    atr_ratio = candle_range / current_atr if current_atr > 0 else 1.0

    # 1. Climax Candle / Exhaustion Expansion (Candle Raksasa > 2.2x ATR)
    if atr_ratio >= 2.2:
        if is_buy and c > o:
            return "Climax Bullish Candle (>2.2x ATR - Puncak Reli/FOMO)"
        elif not is_buy and c < o:
            return "Climax Bearish Candle (>2.2x ATR - Dasar Panic Selling)"
        else:
            return "Extreme News Volatility Spike (>2.2x ATR)"

    # 2. Exhaustion Wick / Rejection Pinbar Lawan Arah
    if is_buy and upper_wick_pct >= 45.0:
        return "Exhaustion Upper Wick (Penolakan Seller Kuat / Shooting Star)"
    if not is_buy and lower_wick_pct >= 45.0:
        return "Exhaustion Lower Wick (Penolakan Buyer Kuat / Hammer)"

    # 3. Doji / High Wave / Spinning Top (Body Tipis < 20% Range di Area Keraguan)
    if body_pct <= 22.0:
        return "Doji / Spinning Top (Konsolidasi & Volatilitas Rendah)"

    # 4. Counter-Candle Pressure (Candle lawan arah sebelum sinyal)
    if is_buy and c < o and body_pct >= 55.0:
        return "Bearish Momentum Candle Lawan Sinyal Buy"
    if not is_buy and c > o and body_pct >= 55.0:
        return "Bullish Momentum Candle Lawan Sinyal Sell"

    # 5. Bullish / Bearish Engulfing Valid
    if is_buy and c > o and prev_c < prev_o and c >= prev_h:
        return "Bullish Engulfing Pattern"
    if not is_buy and c < o and prev_c > prev_o and c <= prev_l:
        return "Bearish Engulfing Pattern"

    # 6. Pinbar Reversal Searah (Valid Hammer / Shooting Star)
    if is_buy and lower_wick_pct >= 50.0:
        return "Valid Bullish Hammer / Pinbar"
    if not is_buy and upper_wick_pct >= 50.0:
        return "Valid Bearish Shooting Star / Pinbar"

    # 7. Standard Trend Continuation Body
    if is_buy and c > o:
        return "Standard Healthy Bullish Body"
    if not is_buy and c < o:
        return "Standard Healthy Bearish Body"

    return "Indecision Mixed Candle"

def run_candle_audit():
    print("================================================================================")
    print("AUDIT MENDALAM: POLA CANDLESTICK PENYEBAB LOSS EA XAUUSD M5 (JAN - SEP 2026)")
    print("================================================================================")
    
    if not mt5.initialize():
        print("[!] Gagal inisialisasi MT5.")
        return

    symbol = "XAUUSD.dmb"
    if not mt5.symbol_select(symbol, True):
        for s in ["XAUUSD", "GOLD", "XAUUSDm"]:
            if mt5.symbol_select(s, True):
                symbol = s
                break

    dt_from = datetime(2026, 1, 1)
    rates_raw = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, datetime.now(), 65000)
    mt5.shutdown()

    if rates_raw is None or len(rates_raw) == 0:
        print("[!] Data tidak ditemukan!")
        return

    rates_clean = [r for r in rates_raw if datetime.fromtimestamp(int(r['time'])) >= dt_from]
    total_bars = len(rates_clean)
    print(f"[+] Berhasil memuat {total_bars:,} Bar M5 dari {datetime.fromtimestamp(rates_clean[0]['time'])} s/d {datetime.fromtimestamp(rates_clean[-1]['time'])}.\n")

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

    # Setting Default Juara EA MT4 & MT5
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

    # Pattern Tracker Data
    pattern_stats = {}

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

        # SMC Fractals (2-bar)
        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high
                last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low
                last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        # Manage active trade
        if active_trade is not None:
            t = active_trade
            c_high = highs[i]
            c_low = lows[i]
            c_close = closes[i]

            if t['type'] == 'BUY':
                floating_pnl = t['realized_profit'] + ((c_close - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                profit_pips = (c_close - t['open_price']) / pip_value

                # Auto-BE
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # Partial TP1
                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    t['is_tp1'] = True
                    part_lot = t['remaining_lot'] * 0.5
                    part_profit = (part_lot / 0.10) * ((c_close - t['open_price']) * 10.0)
                    balance += part_profit
                    t['realized_profit'] += part_profit
                    t['remaining_lot'] -= part_lot
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']: t['sl'] = new_sl

                # Dynamic Trailing
                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']: t['sl'] = struct_sl

                trail_sl = ema21[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']:
                    t['sl'] = trail_sl

                # Exit checks
                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    t['exit_price'] = exit_price
                    t['pnl'] = pnl
                    t['exit_reason'] = 'AUTO-CUT REVERSAL'
                    t['exit_time'] = times[i]
                    trades.append(t)
                    active_trade = None
                    continue

                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price > t['open_price'] else 'FULL STOP LOSS'
                    t['exit_price'] = exit_price
                    t['pnl'] = pnl
                    t['exit_reason'] = reason
                    t['exit_time'] = times[i]
                    trades.append(t)
                    active_trade = None
                    continue

                if c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    t['exit_price'] = exit_price
                    t['pnl'] = pnl
                    t['exit_reason'] = 'TAKE PROFIT (R:R)'
                    t['exit_time'] = times[i]
                    trades.append(t)
                    active_trade = None
                    continue

            elif t['type'] == 'SELL':
                floating_pnl = t['realized_profit'] + ((t['open_price'] - c_close) * (t['remaining_lot'] / 0.10) * 10.0)
                profit_pips = (t['open_price'] - c_close) / pip_value

                # Auto-BE
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # Partial TP1
                if profit_pips >= tp1_trigger_pips and not t['is_tp1']:
                    t['is_tp1'] = True
                    part_lot = t['remaining_lot'] * 0.5
                    part_profit = (part_lot / 0.10) * ((t['open_price'] - c_close) * 10.0)
                    balance += part_profit
                    t['realized_profit'] += part_profit
                    t['remaining_lot'] -= part_lot
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']: t['sl'] = new_sl

                # Dynamic Trailing
                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']: t['sl'] = struct_sl

                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']:
                    t['sl'] = trail_sl

                # Exit checks
                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    t['exit_price'] = exit_price
                    t['pnl'] = pnl
                    t['exit_reason'] = 'AUTO-CUT REVERSAL'
                    t['exit_time'] = times[i]
                    trades.append(t)
                    active_trade = None
                    continue

                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price < t['open_price'] else 'FULL STOP LOSS'
                    t['exit_price'] = exit_price
                    t['pnl'] = pnl
                    t['exit_reason'] = reason
                    t['exit_time'] = times[i]
                    trades.append(t)
                    active_trade = None
                    continue

                if c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    t['exit_price'] = exit_price
                    t['pnl'] = pnl
                    t['exit_reason'] = 'TAKE PROFIT (R:R)'
                    t['exit_time'] = times[i]
                    trades.append(t)
                    active_trade = None
                    continue

            # Drawdown
            if balance > equity_peak: equity_peak = balance
            dd = equity_peak - balance
            if dd > max_dd_dollars: max_dd_dollars = dd

        # Signal Generation
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

            if (is_pullback and candle_ok and score >= min_confluence) or is_bull_trap:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (open_p - lows[i - 1]) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p - sl_dist
                tp_p = open_p + (rr_ratio * sl_dist)

                lot = base_lot
                if score >= 85.0: lot = round(base_lot * 1.30, 2)
                elif score < 75.0: lot = round(base_lot * 0.70, 2)

                pat_name = classify_candle_pattern(
                    opens[i - 1], highs[i - 1], lows[i - 1], closes[i - 1],
                    opens[i - 2], highs[i - 2], lows[i - 2], closes[i - 2],
                    current_atr, is_buy=True
                )

                hour_entry = dt_curr.hour
                session = "Asian (00-07)" if hour_entry < 8 else ("London (08-14)" if hour_entry < 15 else ("NY Overlap (15-20)" if hour_entry < 21 else "NY Close (21-23)"))

                active_trade = {
                    'type': 'BUY', 'open_time': times[i], 'open_price': open_p,
                    'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score,
                    'pattern': pat_name, 'session': session, 'entry_bar': i,
                    'adx': adx[i - 1], 'atr': current_atr
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

            if (is_pullback and candle_ok and score >= min_confluence) or is_bear_trap:
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (highs[i - 1] - open_p) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p + sl_dist
                tp_p = open_p - (rr_ratio * sl_dist)

                lot = base_lot
                if score >= 85.0: lot = round(base_lot * 1.30, 2)
                elif score < 75.0: lot = round(base_lot * 0.70, 2)

                pat_name = classify_candle_pattern(
                    opens[i - 1], highs[i - 1], lows[i - 1], closes[i - 1],
                    opens[i - 2], highs[i - 2], lows[i - 2], closes[i - 2],
                    current_atr, is_buy=False
                )

                hour_entry = dt_curr.hour
                session = "Asian (00-07)" if hour_entry < 8 else ("London (08-14)" if hour_entry < 15 else ("NY Overlap (15-20)" if hour_entry < 21 else "NY Close (21-23)"))

                active_trade = {
                    'type': 'SELL', 'open_time': times[i], 'open_price': open_p,
                    'sl': sl_p, 'tp': tp_p, 'initial_lot': lot, 'remaining_lot': lot,
                    'is_be': False, 'is_tp1': False, 'realized_profit': 0.0, 'score': score,
                    'pattern': pat_name, 'session': session, 'entry_bar': i,
                    'adx': adx[i - 1], 'atr': current_atr
                }
                last_order_bar = i
                continue

    # ANALISIS STATISTIK POLA CANDLESTICK
    total_trades = len(trades)
    winning_trades = [t for t in trades if t['pnl'] > 0]
    losing_trades = [t for t in trades if t['pnl'] <= 0]
    full_sl_trades = [t for t in trades if t['exit_reason'] == 'FULL STOP LOSS']

    print(f"TOTAL TRADES DIEKSEKUSI : {total_trades:,}")
    print(f"TOTAL TRADES MENANG (WIN): {len(winning_trades):,} ({len(winning_trades)/total_trades*100:.2f}%)")
    print(f"TOTAL TRADES KALAH (LOSS): {len(losing_trades):,} ({len(losing_trades)/total_trades*100:.2f}%)")
    print(f"TOTAL TERKENA FULL SL   : {len(full_sl_trades):,} ({len(full_sl_trades)/total_trades*100:.2f}%)\n")

    # Group by Pattern
    for t in trades:
        pat = t['pattern']
        if pat not in pattern_stats:
            pattern_stats[pat] = {
                'total': 0, 'wins': 0, 'losses': 0, 'full_sl': 0,
                'total_loss_pnl': 0.0, 'total_win_pnl': 0.0, 'net_pnl': 0.0
            }
        pattern_stats[pat]['total'] += 1
        pnl = t['pnl']
        pattern_stats[pat]['net_pnl'] += pnl
        if pnl > 0:
            pattern_stats[pat]['wins'] += 1
            pattern_stats[pat]['total_win_pnl'] += pnl
        else:
            pattern_stats[pat]['losses'] += 1
            pattern_stats[pat]['total_loss_pnl'] += pnl
            if t['exit_reason'] == 'FULL STOP LOSS':
                pattern_stats[pat]['full_sl'] += 1

    # Urutkan berdasarkan Jumlah Kerugian Terbesar ($ Loss)
    sorted_by_loss = sorted(pattern_stats.items(), key=lambda x: x[1]['total_loss_pnl'])

    print("========================================================================================================================")
    print("PERINGKAT POLA CANDLESTICK DENGAN KERUGIAN TERBESAR & PALING SERING KENA FULL SL")
    print("========================================================================================================================")
    print(f"{'No':<3} | {'Nama Pola Candlestick':<52} | {'Trades':<7} | {'Loss':<6} | {'Full SL':<7} | {'Win Rate':<9} | {'Total Rugi ($)':<15} | {'Net PnL ($)':<12}")
    print("-" * 120)

    for idx, (pat, s) in enumerate(sorted_by_loss, 1):
        win_rate = (s['wins'] / s['total'] * 100.0) if s['total'] > 0 else 0
        print(f"{idx:<3} | {pat:<52} | {s['total']:<7} | {s['losses']:<6} | {s['full_sl']:<7} | {win_rate:>6.1f}%   | ${s['total_loss_pnl']:>12,.2f} | ${s['net_pnl']:>10,.2f}")

    print("========================================================================================================================\n")

    # Analisis Sesi Waktu Pemicu Loss
    session_stats = {}
    for t in losing_trades:
        sess = t['session']
        if sess not in session_stats:
            session_stats[sess] = {'count': 0, 'full_sl': 0, 'total_loss': 0.0}
        session_stats[sess]['count'] += 1
        session_stats[sess]['total_loss'] += t['pnl']
        if t['exit_reason'] == 'FULL STOP LOSS':
            session_stats[sess]['full_sl'] += 1

    print("========================================================================================================================")
    print("DISTRIBUSI KERUGIAN BERDASARKAN SESI WAKTU (JAM TRADING)")
    print("========================================================================================================================")
    print(f"{'Sesi Trading':<25} | {'Jumlah Loss':<12} | {'Full SL':<10} | {'Total Rugi ($)':<15} | {'Porsi dari Total Loss'}")
    print("-" * 85)
    total_loss_all = sum(t['pnl'] for t in losing_trades)
    for sess, st in session_stats.items():
        pct = (st['total_loss'] / total_loss_all * 100.0) if total_loss_all < 0 else 0
        print(f"{sess:<25} | {st['count']:<12} | {st['full_sl']:<10} | ${st['total_loss']:>12,.2f} | {pct:>5.1f}%")
    print("========================================================================================================================\n")

if __name__ == "__main__":
    run_candle_audit()
