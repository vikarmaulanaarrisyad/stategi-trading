"""
SCAN MINIMUM CAPITAL REQUIREMENT FOR 0.01 LOT ON XAUUSD (JAN - SEP 2026)
Mencari modal awal minimal yang aman untuk fixed lot 0.01 di akun Standar USD vs Akun Cent.
"""

import sys
from datetime import datetime
import MetaTrader5 as mt5
from run_backtest_20usd_micro import *

def test_capital(rates_clean, capital, lot=0.01):
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

    balance = capital
    equity_peak = balance
    max_dd_dollars = 0.0
    max_dd_pct = 0.0
    min_equity = balance
    blown = False
    trades = []
    active_trade = None
    last_order_bar = -10

    last_swing_high = highs[0]
    last_swing_low = lows[0]
    prev_swing_high = highs[0]
    prev_swing_low = lows[0]

    for i in range(150, total_bars):
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

            dollar_pnl = (c_close - t['open_price']) * 1.0 if t['type'] == 'BUY' else (t['open_price'] - c_close) * 1.0
            cur_eq = balance + dollar_pnl
            if cur_eq < min_equity: min_equity = cur_eq

            # Margin Call threshold (misal margin $5.00 pada 1:1000 leverage)
            if cur_eq <= 4.0:
                blown = True
                break

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
                    balance += pnl; trades.append(pnl); active_trade = None; continue
                if c_low <= t['sl']:
                    pnl = (t['sl'] - t['open_price']) * 1.0
                    balance += pnl; trades.append(pnl); active_trade = None; continue
                if c_high >= t['tp']:
                    pnl = (t['tp'] - t['open_price']) * 1.0
                    balance += pnl; trades.append(pnl); active_trade = None; continue

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
                    balance += pnl; trades.append(pnl); active_trade = None; continue
                if c_high >= t['sl']:
                    pnl = (t['open_price'] - t['sl']) * 1.0
                    balance += pnl; trades.append(pnl); active_trade = None; continue
                if c_low <= t['tp']:
                    pnl = (t['open_price'] - t['tp']) * 1.0
                    balance += pnl; trades.append(pnl); active_trade = None; continue

            if balance > equity_peak: equity_peak = balance
            dd = equity_peak - balance
            dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
            if dd > max_dd_dollars: max_dd_dollars = dd; max_dd_pct = dd_pct

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

    wins = [p for p in trades if p > 0]
    wr = len(wins) / len(trades) * 100.0 if trades else 0
    return {
        'capital': capital, 'final_balance': balance, 'net_profit': balance - capital,
        'min_equity': min_equity, 'blown': blown, 'trades': len(trades), 'win_rate': wr,
        'max_dd_dollars': max_dd_dollars
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

    print("=========================================================================================================")
    print("SIMULASI KETAHANAN MODAL DENGAN FIXED LOT 0.01 (XAUUSD M5 JANUARI - SEPTEMBER 2026)")
    print("=========================================================================================================")
    print(f"{'Modal Awal':<15} | {'Status Akun':<18} | {'Lowest Equity':<15} | {'Saldo Akhir':<15} | {'Profit Bersih ($)'}")
    print("-" * 85)

    test_amounts = [20.0, 30.0, 40.0, 50.0, 75.0, 100.0]
    for cap in test_amounts:
        r = test_capital(rates_clean, cap, 0.01)
        st = "[MC / TUMBANG]" if r['blown'] else "[SURVIVE & PROFIT]"
        print(f"${r['capital']:<14.2f} | {st:<18} | ${r['min_equity']:<14.2f} | ${r['final_balance']:<14.2f} | ${r['net_profit']:>10,.2f}")
    print("=========================================================================================================\n")

if __name__ == "__main__":
    main()
