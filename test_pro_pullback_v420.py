# test_pro_pullback_v420.py
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

def run_simulation(rates_m5, rates_m15, mode="PRO_HYBRID",
                   initial_balance=20.0, lot_size=0.01):
    total_bars = len(rates_m5)
    times = [int(r['time']) for r in rates_m5]
    opens = [float(r['open']) for r in rates_m5]
    highs = [float(r['high']) for r in rates_m5]
    lows = [float(r['low']) for r in rates_m5]
    closes = [float(r['close']) for r in rates_m5]
    volumes = [int(r['tick_volume']) for r in rates_m5]

    ema8_m5 = calculate_ema(closes, 8)
    ema21_m5 = calculate_ema(closes, 21)
    ema125_m5 = calculate_ema(closes, 125)
    atr_m5 = calculate_atr(highs, lows, closes, 14)
    adx_m5 = calculate_adx(highs, lows, closes, 14)

    # M15 lookup map
    m15_times = [int(r['time']) for r in rates_m15]
    m15_closes = [float(r['close']) for r in rates_m15]
    m15_ema8 = calculate_ema(m15_closes, 8)
    m15_ema21 = calculate_ema(m15_closes, 21)
    m15_ema125 = calculate_ema(m15_closes, 125)

    m15_map = {}
    for idx, t in enumerate(m15_times):
        m15_map[t] = idx

    pip_value = 0.10
    be_trigger_pips = 12.0
    be_lock_pips = 5.0
    rr_ratio = 2.0

    balance = initial_balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0

    trades = []
    active_trade = None
    last_order_bar = -10

    last_swing_high = highs[0]; last_swing_low = lows[0]
    prev_swing_high = highs[0]; prev_swing_low = lows[0]

    monthly_data = {}
    blocked_counter_trend = 0
    pro_pullback_executed = 0
    trap_trades_executed = 0

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        month_key = dt_curr.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}

        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high; last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low; last_swing_low = lows[i - 2]

        current_atr = atr_m5[i] if atr_m5[i] > 0 else 1.50

        # M15 Trend mapping
        m15_t = (times[i] // 900) * 900
        m15_idx = m15_map.get(m15_t, -1)
        if m15_idx < 0:
            for dt_step in range(1, 4):
                m15_idx = m15_map.get(m15_t - (dt_step * 900), -1)
                if m15_idx >= 0: break

        m15_bull = False; m15_bear = False
        if m15_idx >= 1:
            m15_bull = (m15_closes[m15_idx - 1] > m15_ema125[m15_idx - 1] and m15_ema8[m15_idx - 1] > m15_ema21[m15_idx - 1])
            m15_bear = (m15_closes[m15_idx - 1] < m15_ema125[m15_idx - 1] and m15_ema8[m15_idx - 1] < m15_ema21[m15_idx - 1])

        m5_bull = (closes[i - 1] > ema125_m5[i - 1])
        m5_bear = (closes[i - 1] < ema125_m5[i - 1])

        dom_trend = "NEUTRAL"
        if m15_bull and m5_bull: dom_trend = "BULLISH"
        elif m15_bear and m5_bear: dom_trend = "BEARISH"

        # Manage active trade
        if active_trade is not None:
            t = active_trade
            c_high = highs[i]; c_low = lows[i]; c_close = closes[i]

            dollar_pnl = (c_close - t['open_price']) * 1.0 if t['type'] == 'BUY' else (t['open_price'] - c_close) * 1.0
            profit_pips = (c_close - t['open_price']) / pip_value if t['type'] == 'BUY' else (t['open_price'] - c_close) / pip_value

            if t['type'] == 'BUY':
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']: t['sl'] = struct_sl
                trail_sl = ema21_m5[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']: t['sl'] = trail_sl

                # Auto-Cut Reversal
                if profit_pips >= 5.0 and c_close < ema21_m5[i] and closes[i - 1] >= ema21_m5[i - 1]:
                    pnl = (c_close - t['open_price']) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                # SL Hit
                if c_low <= t['sl']:
                    pnl = (t['sl'] - t['open_price']) * 1.0
                    balance += pnl
                    reason = 'SL+ LOCK WIN' if t['sl'] > t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                # TP Hit
                if c_high >= t['tp']:
                    pnl = (t['tp'] - t['open_price']) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

            else: # SELL
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']: t['sl'] = struct_sl
                trail_sl = ema21_m5[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']: t['sl'] = trail_sl

                # Auto-Cut Reversal
                if profit_pips >= 5.0 and c_close > ema21_m5[i] and closes[i - 1] <= ema21_m5[i - 1]:
                    pnl = (t['open_price'] - c_close) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                # SL Hit
                if c_high >= t['sl']:
                    pnl = (t['open_price'] - t['sl']) * 1.0
                    balance += pnl
                    reason = 'SL+ LOCK WIN' if t['sl'] < t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                # TP Hit
                if c_low <= t['tp']:
                    pnl = (t['open_price'] - t['tp']) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

            if balance > equity_peak: equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars: max_dd_dollars = dd; max_dd_pct = dd_pct

        if active_trade is not None: continue
        if (i - last_order_bar) < 3: continue
        if adx_m5[i - 1] < 20.0: continue

        fibo_range = last_swing_high - last_swing_low
        ema_slope = (ema125_m5[i - 1] - ema125_m5[i - 6]) / pip_value
        bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

        candle_body = abs(closes[i - 1] - opens[i - 1])
        body_pct = (candle_body / bar_range) * 100.0
        upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
        lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
        upper_wick_pct = (upper_wick / bar_range) * 100.0
        lower_wick_pct = (lower_wick / bar_range) * 100.0

        is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
        is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

        vol_now = volumes[i - 1]
        vol_imp = max(volumes[i - 6 : i - 1]) if i >= 6 else vol_now
        is_vsa_dry = (vol_now <= int(vol_imp * 0.90))

        # -------------------------------------------------------------
        # EVALUASI BUY SETUP
        # -------------------------------------------------------------
        buy_allowed = True
        if mode == "STRICT_TREND" and dom_trend == "BEARISH":
            buy_allowed = False
            blocked_counter_trend += 1
        elif mode == "PRO_HYBRID":
            # Strict trend for standard continuation, but allow Bear Trap (SSL Sweep Reversal)
            if dom_trend == "BEARISH" and not is_bear_trap:
                buy_allowed = False
                blocked_counter_trend += 1

        buy_trend_125 = (closes[i - 1] > ema125_m5[i - 1]) and (ema_slope >= 2.0)
        if buy_allowed and (buy_trend_125 or is_bear_trap):
            if body_pct <= 22.0 and not is_bear_trap: pass
            elif upper_wick_pct >= 40.0 and not is_bear_trap: pass
            else:
                is_engulf = closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= highs[i - 2]
                if is_engulf and ((closes[i - 1] - ema21_m5[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value): pass
                else:
                    is_pullback = lows[i - 1] <= max(ema8_m5[i - 1], ema21_m5[i - 1]) and highs[i - 1] >= min(ema8_m5[i - 1], ema21_m5[i - 1])
                    is_pinbar = (lower_wick / bar_range) >= 0.50
                    candle_ok = is_pinbar or is_engulf or is_bear_trap
                    fibo_gp_buy_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
                    fibo_gp_buy_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0
                    in_gp = (lows[i - 1] <= fibo_gp_buy_50 and highs[i - 1] >= fibo_gp_buy_78)

                    score = 0.0
                    if closes[i - 1] > last_swing_high: score += 20.0
                    else: score += 15.0
                    if lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low: score += 12.0
                    if in_gp: score += 10.0
                    if ema8_m5[i - 1] > ema21_m5[i - 1]: score += 10.0
                    if is_pinbar: score += 15.0
                    elif is_engulf: score += 12.0
                    if is_pullback: score += 10.0
                    if is_bear_trap: score += 15.0
                    if is_vsa_dry: score += 10.0
                    if dom_trend == "BULLISH": score += 15.0
                    if last_swing_high > prev_swing_high and last_swing_low > prev_swing_low: score += 15.0

                    is_pro_pb = (mode == "PRO_HYBRID") and is_pullback and in_gp and is_vsa_dry and candle_ok and (dom_trend == "BULLISH")

                    if (is_pullback and candle_ok and score >= 65.0) or is_bear_trap or is_pro_pb:
                        open_p = opens[i]
                        sl_dist = max(20.0 * pip_value, (open_p - lows[i - 1]) + (1.2 * current_atr))
                        sl_dist = min(35.0 * pip_value, sl_dist)
                        sl_p = open_p - sl_dist
                        tp_p = open_p + (rr_ratio * sl_dist)
                        active_trade = {'type': 'BUY', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p, 'is_be': False}
                        if is_pro_pb: pro_pullback_executed += 1
                        if is_bear_trap: trap_trades_executed += 1
                        last_order_bar = i; continue

        # -------------------------------------------------------------
        # EVALUASI SELL SETUP
        # -------------------------------------------------------------
        sell_allowed = True
        if mode == "STRICT_TREND" and dom_trend == "BULLISH":
            sell_allowed = False
            blocked_counter_trend += 1
        elif mode == "PRO_HYBRID":
            # Strict trend for standard continuation, but allow Bull Trap (BSL Sweep Reversal)
            if dom_trend == "BULLISH" and not is_bull_trap:
                sell_allowed = False
                blocked_counter_trend += 1

        sell_trend_125 = (closes[i - 1] < ema125_m5[i - 1]) and (ema_slope <= -2.0)
        if sell_allowed and (sell_trend_125 or is_bull_trap):
            if body_pct <= 22.0 and not is_bull_trap: pass
            elif lower_wick_pct >= 40.0 and not is_bull_trap: pass
            else:
                is_engulf = closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= lows[i - 2]
                if is_engulf and ((ema21_m5[i - 1] - closes[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value): pass
                else:
                    is_pullback = highs[i - 1] >= min(ema8_m5[i - 1], ema21_m5[i - 1]) and lows[i - 1] <= max(ema8_m5[i - 1], ema21_m5[i - 1])
                    upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
                    is_pinbar = (upper_wick / bar_range) >= 0.50
                    candle_ok = is_pinbar or is_engulf or is_bull_trap
                    fibo_gp_sell_50 = last_swing_low + (0.500 * fibo_range) if fibo_range > 0 else 0
                    fibo_gp_sell_78 = last_swing_low + (0.786 * fibo_range) if fibo_range > 0 else 0
                    in_gp = (highs[i - 1] >= fibo_gp_sell_50 and lows[i - 1] <= fibo_gp_sell_78)

                    score = 0.0
                    if closes[i - 1] < last_swing_low: score += 20.0
                    else: score += 15.0
                    if highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high: score += 12.0
                    if in_gp: score += 10.0
                    if ema8_m5[i - 1] < ema21_m5[i - 1]: score += 10.0
                    if is_pinbar: score += 15.0
                    elif is_engulf: score += 12.0
                    if is_pullback: score += 10.0
                    if is_bull_trap: score += 15.0
                    if is_vsa_dry: score += 10.0
                    if dom_trend == "BEARISH": score += 15.0
                    if last_swing_high < prev_swing_high and last_swing_low < prev_swing_low: score += 15.0

                    is_pro_pb = (mode == "PRO_HYBRID") and is_pullback and in_gp and is_vsa_dry and candle_ok and (dom_trend == "BEARISH")

                    if (is_pullback and candle_ok and score >= 65.0) or is_bull_trap or is_pro_pb:
                        open_p = opens[i]
                        sl_dist = max(20.0 * pip_value, (highs[i - 1] - open_p) + (1.2 * current_atr))
                        sl_dist = min(35.0 * pip_value, sl_dist)
                        sl_p = open_p + sl_dist
                        tp_p = open_p - (rr_ratio * sl_dist)
                        active_trade = {'type': 'SELL', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p, 'is_be': False}
                        if is_pro_pb: pro_pullback_executed += 1
                        if is_bull_trap: trap_trades_executed += 1
                        last_order_bar = i; continue

    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    win_rate = (len(wins) / len(trades) * 100.0) if len(trades) > 0 else 0.0
    gross_profit = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.99
    net_profit = balance - initial_balance

    return {
        'initial_balance': initial_balance,
        'final_balance': balance,
        'net_profit': net_profit,
        'return_pct': (net_profit / initial_balance) * 100.0,
        'total_trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'max_dd_dollars': max_dd_dollars,
        'max_dd_pct': max_dd_pct,
        'blocked_counter_trend': blocked_counter_trend,
        'pro_pullback_executed': pro_pullback_executed,
        'trap_trades_executed': trap_trades_executed,
        'monthly_data': monthly_data
    }

def main():
    if not mt5.initialize():
        print("Failed to initialize MT5")
        sys.exit(1)

    symbol = 'XAUUSD.dmb'
    if not mt5.symbol_select(symbol, True):
        for s in ['XAUUSD', 'GOLD', 'XAUUSDm']:
            if mt5.symbol_select(s, True): symbol = s; break

    dt_start = datetime(2026, 1, 1)
    dt_now = datetime(2026, 9, 23)

    rates_m5 = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, dt_start, dt_now)
    rates_m15 = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, dt_start, dt_now)
    mt5.shutdown()

    print("=" * 95)
    print("AUDIT & BACKTEST KOMPARATIF 3 MODEL EKSEKUSI (JANUARI - SEPTEMBER 2026):")
    print(f"Asset: {symbol} | Total Bar M5: {len(rates_m5):,} | Modal: $20.00 | Lot: 0.01 Fixed")
    print("=" * 95)

    res_base = run_simulation(rates_m5, rates_m15, mode="BASELINE")
    res_hybrid = run_simulation(rates_m5, rates_m15, mode="PRO_HYBRID")

    print(f"{'Metrik Kinerja':<32} | {'BASELINE (Standar)':<26} | {'PRO PULLBACK (v4.20)':<26}")
    print("-" * 92)
    print(f"{'Modal Awal':<32} | ${res_base['initial_balance']:<25.2f} | ${res_hybrid['initial_balance']:<25.2f}")
    print(f"{'Saldo Akhir (Final Balance)':<32} | ${res_base['final_balance']:<25.2f} | ${res_hybrid['final_balance']:<25.2f}")
    print(f"{'Net Profit Bersih ($)':<32} | ${res_base['net_profit']:<25.2f} | ${res_hybrid['net_profit']:<25.2f}")
    print(f"{'Return on Capital (%)':<32} | +{res_base['return_pct']:<24.1f}% | +{res_hybrid['return_pct']:<24.1f}%")
    print(f"{'Total Transaksi':<32} | {res_base['total_trades']:<26} | {res_hybrid['total_trades']:<26}")
    print(f"{'Win Rate (%)':<32} | {res_base['win_rate']:<25.2f}% | {res_hybrid['win_rate']:<25.2f}%")
    print(f"{'Profit Factor':<32} | {res_base['profit_factor']:<26.2f} | {res_hybrid['profit_factor']:<26.2f}")
    print(f"{'Maksimal Drawdown ($)':<32} | ${res_base['max_dd_dollars']:<25.2f} | ${res_hybrid['max_dd_dollars']:<25.2f}")
    print(f"{'Maksimal Drawdown (%)':<32} | {res_base['max_dd_pct']:<25.2f}% | {res_hybrid['max_dd_pct']:<25.2f}%")
    print(f"{'Sinyal Kontra-Trend Diblokir':<32} | {'0 (Dibiarkan)':<26} | {res_hybrid['blocked_counter_trend']:<26}")
    print(f"{'Trade Pro Pullback Sukses':<32} | {'0':<26} | {res_hybrid['pro_pullback_executed']:<26}")
    print("=" * 95)

    print("\nTABEL KINERJA BULANAN PRO PULLBACK SCALPER v4.20 (JANUARI - SEPTEMBER 2026):")
    print("Bulan      | Trades   | Win Rate   | Profit Bersih ($)  | Status")
    print("-" * 75)
    for m in sorted(res_hybrid['monthly_data'].keys()):
        d = res_hybrid['monthly_data'][m]
        wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0.0
        status = "PROFIT HIJAU" if d['pnl'] > 0 else "LOSS"
        print(f"{m:<10} | {d['trades']:<8} | {wr:>6.1f}%    | $ {d['pnl']:>14.2f}  | {status}")
    print("=" * 75)

if __name__ == '__main__':
    main()
