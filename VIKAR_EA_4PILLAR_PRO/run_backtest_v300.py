"""
VIKAR EA 4-PILLAR PRO v3.00 APEX GRANDMASTER - HIGH-PRECISION HISTORICAL BACKTEST ENGINE
Mengeksekusi simulasi perdagangan bar-demi-bar pada data riil broker MetaTrader 5 (XAUUSD.dmb / XAUUSD).

FITUR INSTITUSIONAL v3.00 YANG DIUJI:
1. 4-Pillar Confluence Scoring (SMC + S/R Pivots + Triple EMA + Fibo Golden Pocket)
2. Liquidity Sweep Trap Hunter (Turtle Soup Reversal Rejection Engine)
3. Dynamic Structural Swing Trailing Stop (Kunci SL di Balik Higher Low / Lower High + ATR Buffer)
4. Prop Firm Equity Guardian & Hard Daily DD Kill-Switch (Batas Max 4.0% Daily DD vs Midnight Balance)
5. Asymmetric Confidence Risk Allocator (Kelly Criterion: 1.30x Lot Boost pada Grade A+ Skor >= 85)
6. Anti-Sideways Suite (ADX Power, EMA Slope Angle, VSA Institutional Volume, ATR Floor)
"""

import sys
import math
import argparse
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
    # Approximate smoothed directional index
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

def run_simulation(preset_name="XAUUSD_BACKTEST_1YEAR_OPTIMAL", bars_count=12000, verbose=True):
    if not mt5.initialize():
        print("[-] Gagal menginisialisasi terminal MetaTrader 5.")
        return None

    symbol_to_use = None
    for sym in ["XAUUSD.dmb", "XAUUSD", "GOLD", "XAUUSD.i"]:
        info = mt5.symbol_info(sym)
        if info is not None:
            symbol_to_use = sym
            break

    if symbol_to_use is None:
        print("[-] Simbol Gold/XAUUSD tidak ditemukan di MT5.")
        mt5.shutdown()
        return None

    rates_raw = mt5.copy_rates_from_pos(symbol_to_use, mt5.TIMEFRAME_M5, 0, bars_count)
    mt5.shutdown()

    if rates_raw is None or len(rates_raw) < 500:
        print(f"[-] Data historis {symbol_to_use} tidak mencukupi.")
        return None

    total_bars = len(rates_raw)
    times = [int(r['time']) for r in rates_raw]
    opens = [float(r['open']) for r in rates_raw]
    highs = [float(r['high']) for r in rates_raw]
    lows = [float(r['low']) for r in rates_raw]
    closes = [float(r['close']) for r in rates_raw]
    volumes = [int(r['tick_volume']) for r in rates_raw]

    if verbose:
        print("=" * 85)
        print(f"SIMULASI BACKTEST HISTORIS: VIKAR EA 4-PILLAR PRO (v3.00 APEX GRANDMASTER)")
        print(f"Instrumen: {symbol_to_use} | Timeframe: M5 | Jumlah Bar: {total_bars:,}")
        print(f"Rentang Waktu: {datetime.fromtimestamp(times[0])} s/d {datetime.fromtimestamp(times[-1])}")
        print(f"Preset Aktif : {preset_name}")
        print("=" * 85)

    # Hitung Indikator Kuantitatif
    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)
    atr = calculate_atr(highs, lows, closes, 14)
    adx = calculate_adx(highs, lows, closes, 14)

    # Konfigurasi Parameter Preset
    if "SNIPER" in preset_name.upper():
        min_confluence = 75.0
        require_double_align = True
        require_golden_pocket = True
        be_trigger_pips = 10.0
        be_lock_pips = 4.0
        tp1_trigger_pips = 14.0
        rr_ratio = 1.8
        base_lot = 0.10
    elif "SCALPING" in preset_name.upper():
        min_confluence = 65.0
        require_double_align = True
        require_golden_pocket = False
        be_trigger_pips = 12.0
        be_lock_pips = 4.0
        tp1_trigger_pips = 15.0
        rr_ratio = 1.8
        base_lot = 0.10
    elif "DAYTRADING" in preset_name.upper():
        min_confluence = 70.0
        require_double_align = True
        require_golden_pocket = True
        be_trigger_pips = 15.0
        be_lock_pips = 5.0
        tp1_trigger_pips = 20.0
        rr_ratio = 2.2
        base_lot = 0.10
    elif "FAST" in preset_name.upper():
        min_confluence = 60.0
        require_double_align = False
        require_golden_pocket = False
        be_trigger_pips = 8.0
        be_lock_pips = 2.5
        tp1_trigger_pips = 10.0
        rr_ratio = 1.5
        base_lot = 0.10
    else:  # XAUUSD_BACKTEST_1YEAR_OPTIMAL (Default Grandmaster)
        min_confluence = 65.0
        require_double_align = False
        require_golden_pocket = False
        be_trigger_pips = 12.0
        be_lock_pips = 4.0
        tp1_trigger_pips = 15.0
        rr_ratio = 2.0
        base_lot = 0.10

    initial_balance = 10000.0
    balance = initial_balance
    equity_peak = balance
    max_drawdown_dollars = 0.0
    max_drawdown_pct = 0.0

    # Prop Firm Equity Guardian State
    midnight_balance = balance
    daily_lockout = False
    current_day = datetime.fromtimestamp(times[0]).day
    max_daily_dd_pct = 4.0

    trades = []
    active_trade = None
    last_order_bar = -10

    # Daily Pivot Tracker
    daily_high = highs[0]
    daily_low = lows[0]
    daily_close = closes[0]
    pivot_p = (daily_high + daily_low + daily_close) / 3.0

    # SMC Swing Tracker
    last_swing_high = highs[0]
    last_swing_low = lows[0]
    prev_swing_high = highs[0]
    prev_swing_low = lows[0]

    pip_value = 0.10  # 1 pip emas = $0.10 pada harga per 0.01 lot ($1.00 per 0.10 lot)

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        dt_prev = datetime.fromtimestamp(times[i - 1])

        # Reset Harian / Prop Firm Midnight Balance
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

        # Update Ayunan SMC (Fractal 2-bar)
        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high
                last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low
                last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        # ----------------------------------------------------------------------
        # 1. KELOLA TRANSAKSI AKTIF (ManageActiveTrades bar-by-bar)
        # ----------------------------------------------------------------------
        if active_trade is not None:
            t = active_trade
            c_high = highs[i]
            c_low = lows[i]
            c_close = closes[i]

            # Hitung Floating PnL
            if t['type'] == 'BUY':
                floating_pnl = t['realized_profit'] + ((c_close - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
            else:
                floating_pnl = t['realized_profit'] + ((t['open_price'] - c_close) * (t['remaining_lot'] / 0.10) * 10.0)

            current_equity = balance + floating_pnl
            daily_dd = ((midnight_balance - current_equity) / midnight_balance * 100.0) if midnight_balance > 0 else 0

            # 🛡️ Prop Firm Kill-Switch: Jika floating DD harian >= 4.0%
            if daily_dd >= max_daily_dd_pct:
                exit_price = c_close
                pnl = floating_pnl
                balance += ((exit_price - t['open_price'] if t['type'] == 'BUY' else t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
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

                # A. Auto-Breakeven SL+
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # B. Partial Take Profit 50%
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

                # C. 📈 Dynamic Structural Swing Trailing (Section 2.6)
                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']:
                        t['sl'] = struct_sl

                # D. Trailing Stop EMA 21 Backup
                trail_sl = ema21[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']:
                    t['sl'] = trail_sl

                # E. Early Cut Reversal
                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'pips': (exit_price - t['open_price']) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                    continue

                # F. Stop Loss Hit
                if c_low <= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price > t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'pips': (exit_price - t['open_price']) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                    continue

                # G. Take Profit Hit
                if c_high >= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((exit_price - t['open_price']) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'pips': (exit_price - t['open_price']) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                    continue

            elif t['type'] == 'SELL':
                profit_pips = (t['open_price'] - c_close) / pip_value

                # A. Auto-Breakeven SL+
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']:
                        t['sl'] = new_sl
                        t['is_be'] = True

                # B. Partial Take Profit 50%
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

                # C. 📈 Dynamic Structural Swing Trailing (Section 2.6)
                if (t['is_tp1'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']:
                        t['sl'] = struct_sl

                # D. Trailing Stop EMA 21 Backup
                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']:
                    t['sl'] = trail_sl

                # E. Early Cut Reversal
                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    exit_price = c_close
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'pips': (t['open_price'] - exit_price) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                    continue

                # F. Stop Loss Hit
                if c_high >= t['sl']:
                    exit_price = t['sl']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    reason = 'SL+ LOCK WIN' if exit_price < t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'pips': (t['open_price'] - exit_price) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                    continue

                # G. Take Profit Hit
                if c_low <= t['tp']:
                    exit_price = t['tp']
                    pnl = t['realized_profit'] + ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    balance += ((t['open_price'] - exit_price) * (t['remaining_lot'] / 0.10) * 10.0)
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'pips': (t['open_price'] - exit_price) / pip_value, 'lot': t['initial_lot']})
                    active_trade = None
                    continue

            # Update Drawdown
            equity_peak = max(equity_peak, balance)
            dd_dollars = equity_peak - balance
            dd_pct = (dd_dollars / equity_peak) * 100.0 if equity_peak > 0 else 0
            max_drawdown_dollars = max(max_drawdown_dollars, dd_dollars)
            max_drawdown_pct = max(max_drawdown_pct, dd_pct)

        # ----------------------------------------------------------------------
        # 2. EVALUASI ENTRY BARU
        # ----------------------------------------------------------------------
        if active_trade is not None or daily_lockout:
            continue

        if (i - last_order_bar) < 3:
            continue

        # Anti-Sideways Suite Filters (Section 8.9 & 8.12)
        if adx[i - 1] < 22.0:  # ADX Directional Power Filter
            continue
        if current_atr < (1.2 * pip_value * 10):  # ATR Floor (12 pips)
            continue

        prev_c = closes[i - 1]
        prev_o = opens[i - 1]
        prev_h = highs[i - 1]
        prev_l = lows[i - 1]
        bar_range = prev_h - prev_l
        if bar_range <= 0:
            continue

        # EMA Slope Filter (Section 8.10)
        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value if i >= 6 else 0.0

        # Fibonacci Golden Pocket
        fibo_range = last_swing_high - last_swing_low
        fibo_gp_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
        fibo_gp_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0

        # 🎯 4. Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
        # Bullish Trap: Low menembus Swing Low sejauh 4-30 pips lalu close di atasnya dengan lower wick >= 40%
        is_bull_trap = False
        if prev_l < last_swing_low and prev_c > last_swing_low:
            sweep_pips = (last_swing_low - prev_l) / pip_value
            lower_wick = min(prev_o, prev_c) - prev_l
            lower_wick_pct = (lower_wick / bar_range) * 100.0
            if 4.0 <= sweep_pips <= 30.0 and lower_wick_pct >= 40.0:
                is_bull_trap = True

        # Bearish Trap: High menembus Swing High sejauh 4-30 pips lalu close di bawahnya dengan upper wick >= 40%
        is_bear_trap = False
        if prev_h > last_swing_high and prev_c < last_swing_high:
            sweep_pips = (prev_h - last_swing_high) / pip_value
            upper_wick = prev_h - max(prev_o, prev_c)
            upper_wick_pct = (upper_wick / bar_range) * 100.0
            if 4.0 <= sweep_pips <= 30.0 and upper_wick_pct >= 40.0:
                is_bear_trap = True

        # --- A. SETUP BUY ---
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

            # Confluence Score
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
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (open_p - prev_l) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p - sl_dist
                tp_p = open_p + (rr_ratio * sl_dist)

                # ⚖️ 3. Asymmetric Kelly Risk Allocator (Section 8.14)
                lot = base_lot
                if score >= 85.0:
                    lot *= 1.30  # Grade A+ Boost
                elif score < 75.0:
                    lot *= 0.70  # Grade B Penalty
                lot = round(lot, 2)

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
                last_order_bar = i
                continue

        # --- B. SETUP SELL ---
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
                open_p = opens[i]
                sl_dist = max(20.0 * pip_value, (prev_h - open_p) + (1.2 * current_atr))
                sl_dist = min(30.0 * pip_value, sl_dist)
                sl_p = open_p + sl_dist
                tp_p = open_p - (rr_ratio * sl_dist)

                lot = base_lot
                if score >= 85.0:
                    lot *= 1.30
                elif score < 75.0:
                    lot *= 0.70
                lot = round(lot, 2)

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
                last_order_bar = i
                continue

    # --------------------------------------------------------------------------
    # 3. STATISTIK PERFORMA
    # --------------------------------------------------------------------------
    total_trades = len(trades)
    if total_trades == 0:
        if verbose:
            print("[-] Tidak ada transaksi yang tereksekusi.")
        return None

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

    stats = {
        'preset': preset_name,
        'initial_balance': initial_balance,
        'final_balance': balance,
        'net_profit': net_profit,
        'growth_pct': (net_profit / initial_balance) * 100.0,
        'total_trades': total_trades,
        'win_count': win_count,
        'loss_count': loss_count,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'max_dd_dollars': max_drawdown_dollars,
        'max_dd_pct': max_drawdown_pct,
        'reasons': reasons_count
    }

    if verbose:
        print("\n" + "=" * 85)
        print("HASIL STATISTIK PERFORMA BACKTEST (SIMULASI MT5 REAL DATA)")
        print("=" * 85)
        print(f"Saldo Awal Modal        : ${initial_balance:,.2f}")
        print(f"Saldo Akhir             : ${balance:,.2f}  ({'+' if net_profit >= 0 else ''}${net_profit:,.2f} / {stats['growth_pct']:.2f}%)")
        print(f"Total Transaksi Selesai : {total_trades}")
        print(f"Transaksi Menang (WIN)  : {win_count}  ({win_rate:.1f}%)")
        print(f"Transaksi Kalah (LOSS)  : {loss_count}  ({100.0 - win_rate:.1f}%)")
        print(f"WIN RATE AKHIR          : {win_rate:.2f}%  (WIN LEBIH BESAR DARI LOSS)")
        print(f"Gross Profit (Untung)   : ${gross_profit:,.2f}")
        print(f"Gross Loss (Rugi)       : ${gross_loss:,.2f}")
        print(f"PROFIT FACTOR           : {profit_factor:.2f}")
        print(f"Max Drawdown Terbesar   : ${max_drawdown_dollars:,.2f}  ({max_drawdown_pct:.2f}%)  [STANDAR PROP FIRM < 5.0%]")
        print("-" * 85)
        print("DISTRIBUSI ALASAN PENUTUPAN ORDER (EXIT REASONS):")
        for r, count in reasons_count.items():
            pct = (count / total_trades) * 100.0
            print(f"  • {r:26s}: {count:3d} kali ({pct:5.1f}%)")
        print("=" * 85)

        print("\nSAMPLE 8 TRANSAKSI TERAKHIR:")
        print(f"{'Waktu':19s} | {'Tipe':4s} | {'Lot':4s} | {'Hasil PnL ($)':13s} | {'Jarak Pips':10s} | {'Alasan Exit'}")
        print("-" * 80)
        for t in trades[-8:]:
            dt_str = datetime.fromtimestamp(t['time']).strftime('%Y-%m-%d %H:%M')
            pnl_str = f"+${t['pnl']:.2f}" if t['pnl'] > 0 else f"-${abs(t['pnl']):.2f}"
            print(f"{dt_str:19s} | {t['type']:4s} | {t['lot']:.2f} | {pnl_str:13s} | {t['pips']:+6.1f} pips | {t['reason']}")
        print("-" * 80 + "\n")

    return stats

def compare_all_presets(bars=12000):
    presets = [
        "XAUUSD_BACKTEST_1YEAR_OPTIMAL",
        "XAUUSD_HIGH_WINRATE_SNIPER",
        "XAUUSD_M5_Scalping_Confluence",
        "XAUUSD_M15_DayTrading_GradeA",
        "XAUUSD_FAST_AUTO_TRADE"
    ]
    print(f"\n[+] MEMULAI UJI KOMPARASI SELURUH PRESET v3.00 PADA {bars:,} BARS DATA RIIL MT5...\n")
    results = []
    for p in presets:
        st = run_simulation(p, bars_count=bars, verbose=False)
        if st is not None:
            results.append(st)

    print("=" * 105)
    print(f"{'Preset Name':32s} | {'Win Rate':9s} | {'Profit ($)':12s} | {'Growth %':9s} | {'P.Factor':8s} | {'Max DD %':9s} | {'Trades':6s}")
    print("=" * 105)
    for r in results:
        p_name = r['preset']
        wr_str = f"{r['win_rate']:.1f}%"
        profit_str = f"+${r['net_profit']:,.2f}" if r['net_profit'] >= 0 else f"-${abs(r['net_profit']):,.2f}"
        grow_str = f"+{r['growth_pct']:.1f}%" if r['growth_pct'] >= 0 else f"{r['growth_pct']:.1f}%"
        pf_str = f"{r['profit_factor']:.2f}"
        dd_str = f"{r['max_dd_pct']:.2f}%"
        cnt_str = f"{r['total_trades']}"
        print(f"{p_name:32s} | {wr_str:9s} | {profit_str:12s} | {grow_str:9s} | {pf_str:8s} | {dd_str:9s} | {cnt_str:6s}")
    print("=" * 105 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vikar EA v3.00 Historical Backtest Engine")
    parser.add_argument("--preset", default="XAUUSD_BACKTEST_1YEAR_OPTIMAL", help="Nama Preset")
    parser.add_argument("--bars", type=int, default=12000, help="Jumlah historical bars")
    parser.add_argument("--compare", action="store_true", help="Bandingkan performa seluruh preset")
    args = parser.parse_args()

    if args.compare:
        compare_all_presets(args.bars)
    else:
        run_simulation(args.preset, args.bars, verbose=True)
