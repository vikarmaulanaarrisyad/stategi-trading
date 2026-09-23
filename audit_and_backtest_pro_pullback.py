# audit_and_backtest_pro_pullback.py
import sys
import os
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

def run_simulation(m5_rates, m15_rates, mode="PRO_PULLBACK_V420", start_date=datetime(2026, 8, 1),
                   initial_balance=20.0, lot_size=0.01):
    total_bars = len(m5_rates)
    times = [int(r['time']) for r in m5_rates]
    opens = [float(r['open']) for r in m5_rates]
    highs = [float(r['high']) for r in m5_rates]
    lows = [float(r['low']) for r in m5_rates]
    closes = [float(r['close']) for r in m5_rates]
    volumes = [int(r['tick_volume']) for r in m5_rates]

    # Precalculate M5 indicators
    ema8_m5 = calculate_ema(closes, 8)
    ema21_m5 = calculate_ema(closes, 21)
    ema125_m5 = calculate_ema(closes, 125)
    atr_m5 = calculate_atr(highs, lows, closes, 14)

    # Precalculate M15 indicators and map to M5 timestamps
    m15_times = [int(r['time']) for r in m15_rates]
    m15_closes = [float(r['close']) for r in m15_rates]
    m15_ema8 = calculate_ema(m15_closes, 8)
    m15_ema21 = calculate_ema(m15_closes, 21)
    m15_ema125 = calculate_ema(m15_closes, 125)

    # Build M15 lookup map
    m15_map = {}
    for idx, t in enumerate(m15_times):
        m15_map[t] = idx

    pip_value = 0.10
    lot_multiplier = lot_size * 100.0

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

    target_start_ts = int(start_date.timestamp())

    # Mode parameters
    is_pro_mode = (mode == "PRO_PULLBACK_V420")
    strict_trend = is_pro_mode
    enable_pullback_engine = is_pro_mode
    safe_gold_sl_floor = is_pro_mode

    blocked_counter_trend_count = 0
    pro_pullback_trades_count = 0

    for i in range(150, total_bars):
        t_curr = times[i]
        dt_curr = datetime.fromtimestamp(t_curr)

        # Update swing fractal (2 bars left / right)
        if i >= 4:
            if highs[i - 2] > highs[i - 4] and highs[i - 2] > highs[i - 3] and highs[i - 2] > highs[i - 1] and highs[i - 2] > highs[i]:
                prev_swing_high = last_swing_high; last_swing_high = highs[i - 2]
            if lows[i - 2] < lows[i - 4] and lows[i - 2] < lows[i - 3] and lows[i - 2] < lows[i - 1] and lows[i - 2] < lows[i]:
                prev_swing_low = last_swing_low; last_swing_low = lows[i - 2]

        current_atr = atr_m5[i] if atr_m5[i] > 0 else 1.50

        # Find corresponding M15 bar (bar completed prior to current M5 bar)
        m15_t = (t_curr // 900) * 900
        m15_idx = m15_map.get(m15_t, -1)
        if m15_idx < 0:
            # find latest available
            for dt_step in range(1, 4):
                m15_idx = m15_map.get(m15_t - (dt_step * 900), -1)
                if m15_idx >= 0: break

        m15_bull = False; m15_bear = False
        if m15_idx >= 1:
            m15_bull = (m15_closes[m15_idx - 1] > m15_ema125[m15_idx - 1] and m15_ema8[m15_idx - 1] > m15_ema21[m15_idx - 1])
            m15_bear = (m15_closes[m15_idx - 1] < m15_ema125[m15_idx - 1] and m15_ema8[m15_idx - 1] < m15_ema21[m15_idx - 1])

        m5_bull = (closes[i - 1] > ema125_m5[i - 1] and (ema8_m5[i - 1] > ema21_m5[i - 1] or closes[i - 1] > ema21_m5[i - 1]))
        m5_bear = (closes[i - 1] < ema125_m5[i - 1] and (ema8_m5[i - 1] < ema21_m5[i - 1] or closes[i - 1] < ema21_m5[i - 1]))

        dom_trend = "NEUTRAL"
        if m15_bull and m5_bull: dom_trend = "BULLISH"
        elif m15_bear and m5_bear: dom_trend = "BEARISH"

        # Manage active position
        if active_trade is not None:
            t = active_trade
            c_high = highs[i]; c_low = lows[i]; c_close = closes[i]

            profit_pips = (c_close - t['open_price']) / pip_value if t['type'] == 'BUY' else (t['open_price'] - c_close) / pip_value

            closed = False
            pnl = 0.0
            reason = ""

            be_trigger_pips = 6.0
            be_lock_pips = 3.0

            if t['type'] == 'BUY':
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] + (be_lock_pips * pip_value)
                    if new_sl > t['sl']: t['sl'] = new_sl; t['is_be'] = True
                
                # Trailing with EMA 21
                trail_sl = ema21_m5[i] - (4.0 * pip_value)
                if trail_sl > t['sl'] and trail_sl > t['open_price']: t['sl'] = trail_sl

                # Stop Loss
                if c_low <= t['sl']:
                    pnl = (t['sl'] - t['open_price']) * lot_multiplier
                    closed = True
                    reason = 'SL+ LOCK WIN' if t['sl'] > t['open_price'] else 'STOP LOSS'
                # Take Profit
                elif c_high >= t['tp']:
                    pnl = (t['tp'] - t['open_price']) * lot_multiplier
                    closed = True; reason = 'TAKE PROFIT (SWING TP1)' if t.get('is_pro_pb') else 'TAKE PROFIT'

            else: # SELL
                if profit_pips >= be_trigger_pips and not t['is_be']:
                    new_sl = t['open_price'] - (be_lock_pips * pip_value)
                    if new_sl < t['sl']: t['sl'] = new_sl; t['is_be'] = True

                trail_sl = ema21_m5[i] + (4.0 * pip_value)
                if trail_sl < t['sl'] and trail_sl < t['open_price']: t['sl'] = trail_sl

                # Stop Loss
                if c_high >= t['sl']:
                    pnl = (t['open_price'] - t['sl']) * lot_multiplier
                    closed = True
                    reason = 'SL+ LOCK WIN' if t['sl'] < t['open_price'] else 'STOP LOSS'
                # Take Profit
                elif c_low <= t['tp']:
                    pnl = (t['open_price'] - t['tp']) * lot_multiplier
                    closed = True; reason = 'TAKE PROFIT (SWING TP1)' if t.get('is_pro_pb') else 'TAKE PROFIT'

            if closed:
                balance += pnl
                t_record = {
                    'open_time': t['open_time'], 'close_time': dt_curr,
                    'type': t['type'], 'open_price': t['open_price'],
                    'sl': t['sl'], 'tp': t['tp'], 'pnl': pnl, 'reason': reason,
                    'pattern': t.get('pattern', 'STANDARD'),
                    'duration_bars': i - t['bar_idx'], 'duration_mins': (i - t['bar_idx']) * 5
                }
                trades.append(t_record)

                if balance > equity_peak: equity_peak = balance
                dd = equity_peak - balance
                dd_pct = (dd / equity_peak * 100.0) if equity_peak > 0 else 0
                if dd > max_dd_dollars: max_dd_dollars = dd; max_dd_pct = dd_pct
                if balance < min_balance: min_balance = balance

                active_trade = None
                continue

        # Check for new entry
        if t_curr < target_start_ts: continue
        if active_trade is not None: continue
        if (i - last_order_bar) < 3: continue

        fibo_range = last_swing_high - last_swing_low
        bar_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.01

        candle_body = abs(closes[i - 1] - opens[i - 1])
        body_pct = (candle_body / bar_range) * 100.0
        upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
        lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
        upper_wick_pct = (upper_wick / bar_range) * 100.0
        lower_wick_pct = (lower_wick / bar_range) * 100.0

        ribbon_low = min(ema8_m5[i - 1], ema21_m5[i - 1])
        ribbon_high = max(ema8_m5[i - 1], ema21_m5[i - 1])

        # VSA Volume check
        vol_now = volumes[i - 1]
        vol_impulse = max(volumes[i - 6 : i - 1]) if i >= 6 else vol_now
        is_vsa_exhaustion = (vol_now <= int(vol_impulse * 0.90))

        # Fibo Golden Pocket
        fibo_gp_buy_50 = last_swing_high - (0.500 * fibo_range) if fibo_range > 0 else 0
        fibo_gp_buy_78 = last_swing_high - (0.786 * fibo_range) if fibo_range > 0 else 0
        in_gp_buy = (lows[i - 1] <= fibo_gp_buy_50 and highs[i - 1] >= fibo_gp_buy_78)

        fibo_gp_sell_50 = last_swing_low + (0.500 * fibo_range) if fibo_range > 0 else 0
        fibo_gp_sell_78 = last_swing_low + (0.786 * fibo_range) if fibo_range > 0 else 0
        in_gp_sell = (highs[i - 1] >= fibo_gp_sell_50 and lows[i - 1] <= fibo_gp_sell_78)

        # FVG Detection
        has_bull_fvg = (lows[i - 1] > highs[i - 3]) if i >= 3 else False
        has_bear_fvg = (highs[i - 1] < lows[i - 3]) if i >= 3 else False

        # Trap detection
        is_bull_trap = highs[i - 1] > last_swing_high and closes[i - 1] < last_swing_high and (highs[i - 1] - closes[i - 1]) >= (0.40 * bar_range)
        is_bear_trap = lows[i - 1] < last_swing_low and closes[i - 1] > last_swing_low and (closes[i - 1] - lows[i - 1]) >= (0.40 * bar_range)

        # -------------------------------------------------------------
        # EVALUATE BUY SETUP
        # -------------------------------------------------------------
        buy_allowed = True
        if strict_trend and dom_trend == "BEARISH":
            buy_allowed = False
            blocked_counter_trend_count += 1

        if buy_allowed and closes[i - 1] > ema125_m5[i - 1]:
            # Filter doji and upper exhaustion wick
            if body_pct <= 22.0: pass
            elif upper_wick_pct >= 40.0: pass
            else:
                # Pro Pullback Scalper Confluences
                confluences_buy = 0
                if lows[i - 1] <= ribbon_high and highs[i - 1] >= ribbon_low and closes[i - 1] >= ribbon_low:
                    confluences_buy += 1
                if in_gp_buy:
                    confluences_buy += 1
                if has_bull_fvg:
                    confluences_buy += 1
                if is_bear_trap: # SSL sweep
                    confluences_buy += 1
                if is_vsa_exhaustion:
                    confluences_buy += 1

                rejection_buy = closes[i - 1] > ema8_m5[i - 1] and (closes[i - 1] > opens[i - 1] or lower_wick_pct >= 30.0)

                is_pro_pb_buy = enable_pullback_engine and (confluences_buy >= 2) and rejection_buy
                is_standard_buy = (lows[i - 1] <= ribbon_high and highs[i - 1] >= ribbon_low) and rejection_buy and (not strict_trend or dom_trend == "BULLISH")

                if is_pro_pb_buy or is_standard_buy:
                    open_p = opens[i]
                    if safe_gold_sl_floor:
                        sl_dist = max(5.0, (open_p - lows[i - 1]) + (1.2 * current_atr))
                    else:
                        sl_dist = max(1.5, (open_p - lows[i - 1]) + (1.0 * current_atr))

                    sl_p = open_p - sl_dist

                    if is_pro_pb_buy and last_swing_high > (open_p + 1.0):
                        tp_p = last_swing_high # TP1 at recent swing high!
                    else:
                        tp_p = open_p + (2.2 * sl_dist)

                    active_trade = {
                        'type': 'BUY', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p,
                        'is_be': False, 'open_time': dt_curr, 'bar_idx': i,
                        'pattern': 'PRO-PULLBACK' if is_pro_pb_buy else 'STANDARD-BUY',
                        'is_pro_pb': is_pro_pb_buy
                    }
                    if is_pro_pb_buy: pro_pullback_trades_count += 1
                    last_order_bar = i
                    continue

        # -------------------------------------------------------------
        # EVALUATE SELL SETUP
        # -------------------------------------------------------------
        sell_allowed = True
        if strict_trend and dom_trend == "BULLISH":
            sell_allowed = False
            blocked_counter_trend_count += 1

        if sell_allowed and closes[i - 1] < ema125_m5[i - 1]:
            if body_pct <= 22.0: pass
            elif lower_wick_pct >= 40.0: pass
            else:
                confluences_sell = 0
                if highs[i - 1] >= ribbon_low and lows[i - 1] <= ribbon_high and closes[i - 1] <= ribbon_high:
                    confluences_sell += 1
                if in_gp_sell:
                    confluences_sell += 1
                if has_bear_fvg:
                    confluences_sell += 1
                if is_bull_trap: # BSL sweep
                    confluences_sell += 1
                if is_vsa_exhaustion:
                    confluences_sell += 1

                rejection_sell = closes[i - 1] < ema8_m5[i - 1] and (closes[i - 1] < opens[i - 1] or upper_wick_pct >= 30.0)

                is_pro_pb_sell = enable_pullback_engine and (confluences_sell >= 2) and rejection_sell
                is_standard_sell = (highs[i - 1] >= ribbon_low and lows[i - 1] <= ribbon_high) and rejection_sell and (not strict_trend or dom_trend == "BEARISH")

                if is_pro_pb_sell or is_standard_sell:
                    open_p = opens[i]
                    if safe_gold_sl_floor:
                        sl_dist = max(5.0, (highs[i - 1] - open_p) + (1.2 * current_atr))
                    else:
                        sl_dist = max(1.5, (highs[i - 1] - open_p) + (1.0 * current_atr))

                    sl_p = open_p + sl_dist

                    if is_pro_pb_sell and last_swing_low < (open_p - 1.0) and last_swing_low > 0:
                        tp_p = last_swing_low # TP1 at recent swing low!
                    else:
                        tp_p = open_p - (2.2 * sl_dist)

                    active_trade = {
                        'type': 'SELL', 'open_price': open_p, 'sl': sl_p, 'tp': tp_p,
                        'is_be': False, 'open_time': dt_curr, 'bar_idx': i,
                        'pattern': 'PRO-PULLBACK' if is_pro_pb_sell else 'STANDARD-SELL',
                        'is_pro_pb': is_pro_pb_sell
                    }
                    if is_pro_pb_sell: pro_pullback_trades_count += 1
                    last_order_bar = i
                    continue

    wins = [t for t in trades if t['pnl'] > 0]
    losses = [t for t in trades if t['pnl'] <= 0]
    win_rate = (len(wins) / len(trades) * 100.0) if len(trades) > 0 else 0.0
    gross_profit = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.99
    net_profit = balance - initial_balance
    return {
        'mode': mode,
        'start_date': start_date.strftime("%Y-%m-%d"),
        'initial_balance': initial_balance,
        'final_balance': balance,
        'net_profit': net_profit,
        'return_pct': (net_profit / initial_balance) * 100.0,
        'total_trades': len(trades),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': win_rate,
        'gross_profit': gross_profit,
        'gross_loss': gross_loss,
        'profit_factor': profit_factor,
        'max_dd_dollars': max_dd_dollars,
        'max_dd_pct': max_dd_pct,
        'blocked_counter_trend': blocked_counter_trend_count,
        'pro_pullback_trades': pro_pullback_trades_count,
        'trades': trades
    }

def main():
    if not mt5.initialize():
        print("Failed to initialize MT5")
        sys.exit(1)

    symbol = 'XAUUSD.dmb'
    if not mt5.symbol_select(symbol, True):
        for s in ['XAUUSD', 'GOLD', 'XAUUSDm']:
            if mt5.symbol_select(s, True): symbol = s; break

    dt_start = datetime(2026, 7, 15)
    dt_now = datetime(2026, 9, 23)

    m5_rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M5, dt_start, dt_now)
    m15_rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M15, dt_start, dt_now)
    mt5.shutdown()

    if m5_rates is None or len(m5_rates) == 0:
        print("Failed to fetch rates")
        sys.exit(1)

    print("=" * 80)
    print("BACKTEST COMPARATIVE AUDIT: FITUR PRO TREND PULLBACK SCALPER (v4.20)")
    print(f"Asset: {symbol} | Data Bars: {len(m5_rates)} M5 bars, {len(m15_rates)} M15 bars")
    print(f"Periode Uji: 1 Agustus 2026 s/d 23 September 2026 | Modal Awal: $20.00 (Micro)")
    print("=" * 80)

    # 1. Baseline Model
    res_base = run_simulation(m5_rates, m15_rates, mode="BASELINE_PRE_V420", start_date=datetime(2026, 8, 1))

    # 2. New Pro Pullback Scalper Model (v4.20)
    res_pro = run_simulation(m5_rates, m15_rates, mode="PRO_PULLBACK_V420", start_date=datetime(2026, 8, 1))

    print("\nHASIL PERBANDINGAN PERFORMA (AGUSTUS - SEPTEMBER 2026):")
    print(f"{'Metrik Performa':<32} | {'BASELINE (Sebelum)':<20} | {'PRO PULLBACK (v4.20)':<20}")
    print("-" * 78)
    print(f"{'Modal Awal':<32} | ${res_base['initial_balance']:<19.2f} | ${res_pro['initial_balance']:<19.2f}")
    print(f"{'Saldo Akhir (Balance)':<32} | ${res_base['final_balance']:<19.2f} | ${res_pro['final_balance']:<19.2f}")
    print(f"{'Net Profit ($)':<32} | ${res_base['net_profit']:<19.2f} | ${res_pro['net_profit']:<19.2f}")
    print(f"{'Return on Capital (%)':<32} | +{res_base['return_pct']:<18.1f}% | +{res_pro['return_pct']:<18.1f}%")
    print(f"{'Total Transaksi':<32} | {res_base['total_trades']:<20} | {res_pro['total_trades']:<20}")
    print(f"{'Win Rate (%)':<32} | {res_base['win_rate']:<19.1f}% | {res_pro['win_rate']:<19.1f}%")
    print(f"{'Profit Factor':<32} | {res_base['profit_factor']:<20.2f} | {res_pro['profit_factor']:<20.2f}")
    print(f"{'Maksimal Drawdown ($)':<32} | ${res_base['max_dd_dollars']:<19.2f} | ${res_pro['max_dd_dollars']:<19.2f}")
    print(f"{'Maksimal Drawdown (%)':<32} | {res_base['max_dd_pct']:<19.1f}% | {res_pro['max_dd_pct']:<19.1f}%")
    print(f"{'Sinyal Kontra-Trend Diblokir':<32} | {'0 (Dibiarkan Loss)':<20} | {res_pro['blocked_counter_trend']:<20}")
    print(f"{'Trade Pro Pullback Terpicu':<32} | {'0 (Fitur Belum Ada)':<20} | {res_pro['pro_pullback_trades']:<20}")
    print("=" * 80)

    # September 2026 specific audit
    res_sep_base = run_simulation(m5_rates, m15_rates, mode="BASELINE_PRE_V420", start_date=datetime(2026, 9, 1))
    res_sep_pro = run_simulation(m5_rates, m15_rates, mode="PRO_PULLBACK_V420", start_date=datetime(2026, 9, 1))

    print("\nHASIL AUDIT KHUSUS BULAN INI (SEPTEMBER 2026 - VOLATILITAS TINGGI):")
    print(f"{'Metrik':<30} | {'BASELINE':<18} | {'PRO PULLBACK v4.20':<18}")
    print("-" * 72)
    print(f"{'Net Profit ($)':<30} | ${res_sep_base['net_profit']:<17.2f} | ${res_sep_pro['net_profit']:<17.2f}")
    print(f"{'Win Rate (%)':<30} | {res_sep_base['win_rate']:<17.1f}% | {res_sep_pro['win_rate']:<17.1f}%")
    print(f"{'Profit Factor':<30} | {res_sep_base['profit_factor']:<18.2f} | {res_sep_pro['profit_factor']:<18.2f}")
    print(f"{'Max Drawdown ($)':<30} | ${res_sep_base['max_dd_dollars']:<17.2f} | ${res_sep_pro['max_dd_dollars']:<17.2f}")
    print("=" * 80)

if __name__ == '__main__':
    main()
