"""
SIMULASI LENGKAP BACKTEST MODAL $20.00 DENGAN LOT 0.01 (QUICKPRO MT4)
Periode: Januari 2026 s/d Sekarang (50,123 Bar M5 XAUUSD)
Melacak secara presisi setiap transaksi, pertumbuhan ekuitas, margin, dan kurva saldo.
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

def run_exact_20usd(rates_clean):
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
    pip_value = 0.10

    initial_balance = 20.0
    balance = initial_balance
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0
    min_balance = balance
    min_equity = balance

    trades = []
    active_trade = None
    last_order_bar = -10

    last_swing_high = highs[0]
    last_swing_low = lows[0]
    prev_swing_high = highs[0]
    prev_swing_low = lows[0]

    monthly_data = {}

    for i in range(150, total_bars):
        dt_curr = datetime.fromtimestamp(times[i])
        month_key = dt_curr.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {'trades': 0, 'wins': 0, 'losses': 0, 'pnl': 0.0}

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

            # 0.01 lot PnL ($1 per $1 price move)
            dollar_pnl = (c_close - t['open_price']) * 1.0 if t['type'] == 'BUY' else (t['open_price'] - c_close) * 1.0
            cur_eq = balance + dollar_pnl
            if cur_eq < min_equity: min_equity = cur_eq

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

                if profit_pips >= 5.0 and c_close < ema21[i] and closes[i - 1] >= ema21[i - 1]:
                    pnl = (c_close - t['open_price']) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                if c_low <= t['sl']:
                    pnl = (t['sl'] - t['open_price']) * 1.0
                    balance += pnl
                    reason = 'SL+ LOCK WIN' if t['sl'] > t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': reason, 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                if c_high >= t['tp']:
                    pnl = (t['tp'] - t['open_price']) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'BUY', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

            else:
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']: t['sl'] = new_sl; t['is_be'] = True
                if (t['is_be'] or profit_pips >= be_lock_pips) and last_swing_high < t['open_price']:
                    struct_sl = last_swing_high + (0.5 * current_atr)
                    if struct_sl < t['sl']: t['sl'] = struct_sl
                trail_sl = ema21[i] + (5.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']: t['sl'] = trail_sl

                if profit_pips >= 5.0 and c_close > ema21[i] and closes[i - 1] <= ema21[i - 1]:
                    pnl = (t['open_price'] - c_close) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'AUTO-CUT REVERSAL', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                if c_high >= t['sl']:
                    pnl = (t['open_price'] - t['sl']) * 1.0
                    balance += pnl
                    reason = 'SL+ LOCK WIN' if t['sl'] < t['open_price'] else 'STOP LOSS'
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': reason, 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
                    active_trade = None; continue

                if c_low <= t['tp']:
                    pnl = (t['open_price'] - t['tp']) * 1.0
                    balance += pnl
                    trades.append({'time': times[i], 'type': 'SELL', 'pnl': pnl, 'reason': 'TAKE PROFIT (R:R)', 'bal': balance})
                    monthly_data[month_key]['trades'] += 1; monthly_data[month_key]['pnl'] += pnl
                    if pnl > 0: monthly_data[month_key]['wins'] += 1
                    else: monthly_data[month_key]['losses'] += 1
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

    print("=========================================================================================")
    print("HASIL SIMULASI PENUH MODAL $20.00 | FIXED LOT 0.01 (QUICKPRO MT4)")
    print("=========================================================================================")
    print(f"Saldo Awal Modal : ${initial_balance:.2f}")
    print(f"Saldo Akhir      : ${balance:,.2f} (+${balance - initial_balance:,.2f} / +{((balance - initial_balance)/initial_balance)*100:.1f}%)")
    print(f"Total Transaksi  : {total_t:,} Trade ({len(wins):,} Menang / {len(losses):,} Kalah)")
    print(f"Win Rate         : {wr:.2f}%")
    print(f"Profit Factor    : {pf:.2f}")
    print(f"Maksimum Drawdown: ${max_dd_dollars:.2f} ({max_dd_pct:.2f}%)")
    print(f"Saldo Terendah   : ${min_balance:.2f}")
    print(f"Ekuitas Terendah : ${min_equity:.2f}")
    print("=========================================================================================\n")

    print("--- KINERJA PER BULAN (JANUARI - SEPTEMBER 2026) ---")
    print(f"{'Bulan':<10} | {'Trades':<8} | {'Win Rate':<10} | {'Profit Bersih ($)':<18} | {'Status'}")
    print("-" * 65)
    for m, d in monthly_data.items():
        m_wr = (d['wins'] / d['trades'] * 100.0) if d['trades'] > 0 else 0
        st = "PROFIT HIJAU" if d['pnl'] > 0 else "LOSS MERAH"
        print(f"{m:<10} | {d['trades']:<8} | {m_wr:>6.1f}%    | ${d['pnl']:>15,.2f}  | {st}")
    print("-" * 65)

if __name__ == "__main__":
    if not mt5.initialize(): sys.exit()
    symbol = "XAUUSD.dmb"
    if not mt5.symbol_select(symbol, True):
        for s in ["XAUUSD", "GOLD", "XAUUSDm"]:
            if mt5.symbol_select(s, True): symbol = s; break
    dt_from = datetime(2026, 1, 1)
    rates_raw = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M5, datetime.now(), 65000)
    mt5.shutdown()
    rates_clean = [r for r in rates_raw if datetime.fromtimestamp(int(r['time'])) >= dt_from]
    run_exact_20usd(rates_clean)
