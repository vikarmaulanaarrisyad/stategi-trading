import sys
import os
import time
from datetime import datetime, timedelta
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

def load_dataset():
    if not mt5.initialize():
        print("MT5 init failed")
        sys.exit(1)
    symbol = 'XAUUSD.dmb'
    if not mt5.symbol_select(symbol, True):
        for s in ['XAUUSD', 'GOLD', 'XAUUSDm']:
            if mt5.symbol_select(s, True): symbol = s; break

    d_cur = datetime(2025, 4, 14)
    d_end = datetime(2026, 9, 21)
    native_m5 = {}
    cur = d_cur
    while cur < d_end:
        nxt = min(cur + timedelta(days=30), d_end)
        r = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, cur, nxt)
        if r is not None and len(r) > 0:
            for b in r:
                t = int(b['time'])
                if t >= int(cur.timestamp()) and t < int(nxt.timestamp()):
                    native_m5[t] = {
                        'time': t, 'open': float(b['open']), 'high': float(b['high']),
                        'low': float(b['low']), 'close': float(b['close']), 'tick_volume': int(b['tick_volume'])
                    }
        cur = nxt

    sorted_native = [native_m5[t] for t in sorted(native_m5.keys())]
    first_native_time = sorted_native[0]['time']

    r_m15 = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, datetime(2025, 1, 1), datetime(2025, 4, 15))
    mt5.shutdown()

    prior_m5 = []
    if r_m15 is not None and len(r_m15) > 0:
        for b in r_m15:
            t0 = int(b['time'])
            if t0 >= first_native_time: continue
            o = float(b['open']); h = float(b['high']); l = float(b['low']); c = float(b['close'])
            v = int(b['tick_volume']) // 3
            if c >= o:
                b1_o = o; b1_l = l + 0.3 * (o - l) if o > l else l; b1_c = o + 0.4 * (c - o); b1_h = max(b1_o, b1_c)
                prior_m5.append({'time': t0, 'open': b1_o, 'high': b1_h, 'low': b1_l, 'close': b1_c, 'tick_volume': v})
                b2_o = b1_c; b2_h = h; b2_l = min(b2_o, b1_l); b2_c = o + 0.8 * (c - o)
                prior_m5.append({'time': t0 + 300, 'open': b2_o, 'high': b2_h, 'low': b2_l, 'close': b2_c, 'tick_volume': v})
                b3_o = b2_c; b3_h = max(b3_o, h); b3_l = min(b3_o, c); b3_c = c
                prior_m5.append({'time': t0 + 600, 'open': b3_o, 'high': b3_h, 'low': b3_l, 'close': b3_c, 'tick_volume': v})
            else:
                b1_o = o; b1_h = o + 0.3 * (h - o) if h > o else h; b1_c = o - 0.4 * (o - c); b1_l = min(b1_o, b1_c)
                prior_m5.append({'time': t0, 'open': b1_o, 'high': b1_h, 'low': b1_l, 'close': b1_c, 'tick_volume': v})
                b2_o = b1_c; b2_l = l; b2_h = max(b2_o, b1_h); b2_c = o - 0.8 * (o - c)
                prior_m5.append({'time': t0 + 300, 'open': b2_o, 'high': b2_h, 'low': b2_l, 'close': b2_c, 'tick_volume': v})
                b3_o = b2_c; b3_l = min(b3_o, l); b3_h = max(b3_o, c); b3_c = c
                prior_m5.append({'time': t0 + 600, 'open': b3_o, 'high': b3_h, 'low': b3_l, 'close': b3_c, 'tick_volume': v})

    return prior_m5 + sorted_native

def run_simulation(dataset, preset_name="SNIPER", initial_balance=20.0, lot_size=0.01):
    total_bars = len(dataset)
    times = [int(r['time']) for r in dataset]
    opens = [float(r['open']) for r in dataset]
    highs = [float(r['high']) for r in dataset]
    lows = [float(r['low']) for r in dataset]
    closes = [float(r['close']) for r in dataset]

    ema8 = calculate_ema(closes, 8)
    ema21 = calculate_ema(closes, 21)
    ema125 = calculate_ema(closes, 125)
    atr = calculate_atr(highs, lows, closes, 14)
    adx = calculate_adx(highs, lows, closes, 14)

    if "FAST" in preset_name.upper():
        min_confluence = 60.0; be_trigger_pips = 8.0; be_lock_pips = 4.5; tp1_trigger_pips = 10.0; rr_ratio = 1.5
    elif "SNIPER" in preset_name.upper():
        min_confluence = 75.0; be_trigger_pips = 8.0; be_lock_pips = 5.0; tp1_trigger_pips = 14.0; rr_ratio = 1.8
    elif "SCALPING" in preset_name.upper():
        min_confluence = 65.0; be_trigger_pips = 12.0; be_lock_pips = 5.0; tp1_trigger_pips = 15.0; rr_ratio = 1.8
    else: # 1YEAR_OPTIMAL
        min_confluence = 65.0; be_trigger_pips = 12.0; be_lock_pips = 5.0; tp1_trigger_pips = 15.0; rr_ratio = 2.0

    pip_value = 0.10 # $0.10 price move = 1 pip
    lot_multiplier = lot_size * 100.0 # 0.01 lot * 100 oz = 1.0 $/point

    balance = initial_balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0
    min_balance = balance

    trades = []
    active_trade = None
    last_order_bar = -10

    last_swing_high = highs[0]; last_swing_low = lows[0]
    prev_swing_high = highs[0]; prev_swing_low = lows[0]

    monthly_data = {}

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        m_key = dt_curr.strftime("%Y-%m")
        if m_key not in monthly_data:
            monthly_data[m_key] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}

        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high; last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low; last_swing_low = lows[i - 2]

        current_atr = atr[i] if atr[i] > 0 else 1.50

        if active_trade is not None:
            t = active_trade
            c_high = highs[i]; c_low = lows[i]; c_close = closes[i]

            profit_pips = (c_close - t['open_price']) / pip_value if t['type'] == 'BUY' else (t['open_price'] - c_close) / pip_value

            if t['type'] == 'BUY':
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_low > t['open_price']:
                    struct_sl = last_swing_low - (0.5 * current_atr)
                    if struct_sl > t['sl']: t['sl'] = struct_sl
                trail_sl = ema21[i] - (5.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']: t['sl'] = trail_sl

                # Auto Cut Reversal
                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    pnl = (c_close - t['open_price']) * lot_multiplier
                    balance += pnl
                    trades.append({'pnl': pnl, 'type': 'BUY', 'reason': 'AUTO-CUT REVERSAL', 'time': dt_curr})
                    monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[m_key]['wins'] += 1
                    else: monthly_data[m_key]['losses'] += 1
                    active_trade = None; continue

                # Stop Loss
                if c_low <= t['sl']:
                    pnl = (t['sl'] - t['open_price']) * lot_multiplier
                    balance += pnl
                    reason = 'SL+ LOCK WIN' if t['sl'] > t['open_price'] else 'STOP LOSS'
                    trades.append({'pnl': pnl, 'type': 'BUY', 'reason': reason, 'time': dt_curr})
                    monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[m_key]['wins'] += 1
                    else: monthly_data[m_key]['losses'] += 1
                    active_trade = None; continue

                # Take Profit
                if c_high >= t['tp']:
                    pnl = (t['tp'] - t['open_price']) * lot_multiplier
                    balance += pnl
                    trades.append({'pnl': pnl, 'type': 'BUY', 'reason': 'TAKE PROFIT (R:R)', 'time': dt_curr})
                    monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[m_key]['wins'] += 1
                    else: monthly_data[m_key]['losses'] += 1
                    active_trade = None; continue

            else: # SELL
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']: t['sl'] = struct_sl
                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']: t['sl'] = trail_sl

                # Auto Cut Reversal
                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    pnl = (t['open_price'] - c_close) * lot_multiplier
                    balance += pnl
                    trades.append({'pnl': pnl, 'type': 'SELL', 'reason': 'AUTO-CUT REVERSAL', 'time': dt_curr})
                    monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[m_key]['wins'] += 1
                    else: monthly_data[m_key]['losses'] += 1
                    active_trade = None; continue

                # Stop Loss
                if c_high >= t['sl']:
                    pnl = (t['open_price'] - t['sl']) * lot_multiplier
                    balance += pnl
                    reason = 'SL+ LOCK WIN' if t['sl'] < t['open_price'] else 'STOP LOSS'
                    trades.append({'pnl': pnl, 'type': 'SELL', 'reason': reason, 'time': dt_curr})
                    monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[m_key]['wins'] += 1
                    else: monthly_data[m_key]['losses'] += 1
                    active_trade = None; continue

                # Take Profit
                if c_low <= t['tp']:
                    pnl = (t['open_price'] - t['tp']) * lot_multiplier
                    balance += pnl
                    trades.append({'pnl': pnl, 'type': 'SELL', 'reason': 'TAKE PROFIT (R:R)', 'time': dt_curr})
                    monthly_data[m_key]['trades'] += 1; monthly_data[m_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[m_key]['wins'] += 1
                    else: monthly_data[m_key]['losses'] += 1
                    active_trade = None; continue

            if balance > equity_peak: equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars: max_dd_dollars = dd; max_dd_pct = dd_pct
            if balance < min_balance: min_balance = balance

        if active_trade is not None: continue
        if (i - last_order_bar) < 3: continue
        if adx[i - 1] < 20.0: continue

        fibo_range = last_swing_high - last_swing_low
        ema_slope = (ema125[i - 1] - ema125[i - 6]) / pip_value
        bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

        candle_body = abs(closes[i - 1] - opens[i - 1])
        body_pct = (candle_body / bar_range) * 100.0
        upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
        lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
        upper_wick_pct = (upper_wick / bar_range) * 100.0
        lower_wick_pct = (lower_wick / bar_range) * 100.0

        is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
        is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

        buy_trend_125 = (closes[i - 1] > ema125[i - 1]) and (ema_slope >= 2.0)
        if buy_trend_125 or is_bull_trap:
            if body_pct <= 22.0 and not is_bull_trap: continue
            if upper_wick_pct >= 45.0 and not is_bull_trap: continue
            is_engulf = closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= highs[i - 2]
            if is_engulf and ((closes[i - 1] - ema21[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value): continue

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
                active_trade = {'type': 'BUY', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p, 'is_be': False}
                last_order_bar = i; continue

        sell_trend_125 = (closes[i - 1] < ema125[i - 1]) and (ema_slope <= -2.0)
        if sell_trend_125 or is_bear_trap:
            if body_pct <= 22.0 and not is_bear_trap: continue
            if lower_wick_pct >= 45.0 and not is_bear_trap: continue
            is_engulf = closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= lows[i - 2]
            if is_engulf and ((ema21[i - 1] - closes[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value): continue

            is_pullback = highs[i - 1] >= min(ema8[i - 1], ema21[i - 1]) and lows[i - 1] <= max(ema8[i - 1], ema21[i - 1])
            upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
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
                active_trade = {'type': 'SELL', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p, 'is_be': False}
                last_order_bar = i; continue

    total_t = len(trades)
    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    wr = len(wins) / total_t * 100.0 if total_t > 0 else 0
    gross_win = sum([t['pnl'] for t in wins])
    gross_loss = abs(sum([t['pnl'] for t in losses]))
    pf = (gross_win / gross_loss) if gross_loss > 0 else 99.0

    return {
        'preset': preset_name, 'total': total_t, 'wins': len(wins), 'losses': len(losses),
        'win_rate': wr, 'profit_factor': pf, 'net_profit': balance - initial_balance,
        'growth': ((balance - initial_balance) / initial_balance) * 100.0,
        'max_dd_dollars': max_dd_dollars, 'max_dd_pct': max_dd_pct,
        'final_balance': balance, 'min_balance': min_balance,
        'monthly': monthly_data, 'trades': trades
    }

def main():
    print("Loading continuous 2025-2026 dataset...", flush=True)
    dataset = load_dataset()
    print(f"Dataset loaded: {len(dataset):,} M5 bars from {datetime.fromtimestamp(dataset[0]['time'])} to {datetime.fromtimestamp(dataset[-1]['time'])}\n", flush=True)

    presets = ["SNIPER", "1YEAR_OPTIMAL", "SCALPING", "FAST"]

    print("=" * 130)
    print(f"HASIL BACKTEST LENGKAP: 1 JANUARI 2025 - 19 SEPTEMBER 2026 (21 BULAN / {len(dataset):,} BARS M5)")
    print(f"PENGATURAN: MODAL AWAL $20.00 | FIXED LOT 0.01 (QUICKPRO MT4)")
    print("=" * 130)
    print(f"{'Nama Preset':<25} | {'Trades':<7} | {'Win Rate':<9} | {'PF':<5} | {'Saldo Akhir':<14} | {'Net Profit ($)':<16} | {'Pertumbuhan':<12} | {'Min Balance'}")
    print("-" * 130)

    results = {}
    for p in presets:
        r = run_simulation(dataset, preset_name=p, initial_balance=20.0, lot_size=0.01)
        results[p] = r
        print(f"{r['preset']:<25} | {r['total']:<7} | {r['win_rate']:>6.2f}%   | {r['profit_factor']:>4.2f} | ${r['final_balance']:>12,.2f} | ${r['net_profit']:>14,.2f} | {r['growth']:>10.1f}% | ${r['min_balance']:>8.2f}")
    print("=" * 130 + "\n")

    # Detailed breakdown for SNIPER
    sn = results["SNIPER"]
    print("=" * 80)
    print("RINCIAN PERFORMA BULANAN PRESET SNIPER (MODAL $20 -> $" + f"{sn['final_balance']:,.2f})")
    print("=" * 80)
    print(f"{'Bulan':<10} | {'Trades':<8} | {'Win Rate':<10} | {'Profit ($)':<14} | {'Status'}")
    print("-" * 80)

    year_2025_pnl = 0.0
    year_2026_pnl = 0.0
    year_2025_trades = 0
    year_2026_trades = 0

    for m in sorted(sn['monthly'].keys()):
        d = sn['monthly'][m]
        wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0
        pnl = d['pnl']
        status = "PROFIT HIJAU" if pnl > 0 else "LOSS MERAH"
        print(f"{m:<10} | {d['trades']:<8} | {wr:>7.1f}%   | ${pnl:>12,.2f} | {status}")
        if m.startswith("2025"):
            year_2025_pnl += pnl; year_2025_trades += d['trades']
        else:
            year_2026_pnl += pnl; year_2026_trades += d['trades']

    print("-" * 80)
    print(f"REKAPITULASI TAHUNAN:")
    print(f"  * TAHUN 2025 (12 Bulan): {year_2025_trades} Trades | Net Profit: ${year_2025_pnl:,.2f}")
    print(f"  * TAHUN 2026 (9 Bulan) : {year_2026_trades} Trades | Net Profit: ${year_2026_pnl:,.2f}")
    print(f"  * TOTAL 21 BULAN       : {sn['total']} Trades | Total Net Profit: ${sn['net_profit']:,.2f}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
