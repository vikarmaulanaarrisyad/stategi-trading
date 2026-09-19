"""
====================================================================
ROBOT TRADING TRIPLE EMA PULLBACK (XAUUSD / FOREX) - PYTHON BOT
====================================================================
Program Utama (Live / Demo Trading Loop)
Mengintegrasikan MetaTrader 5, Indikator Teknis, Deteksi 18 Candlestick,
Filter Struktur Pasar, Auto Break-Even, dan Trailing Stop EMA 21.
====================================================================
"""

import sys
import time
from datetime import datetime
from typing import Optional

from config import TradingConfig
from mt5_client import MT5Client
from indicators import compute_all_indicators, calculate_ema
from strategy import TripleEmaStrategy, TradeSignal
from risk_manager import RiskManager
from candle_patterns import get_pattern_name

def print_banner(cfg: TradingConfig, broker_symbol: str, account_info):
    print("=" * 65)
    print("   ROBOT TRADING TRIPLE EMA PULLBACK (8, 21, 125) - PYTHON")
    print("=" * 65)
    print(f" Simbol Trading   : {broker_symbol} (TF: {cfg.timeframe})")
    print(f" Akun Login       : #{account_info.login} ({account_info.name})")
    print(f" Server Broker    : {account_info.server}")
    print(f" Saldo / Equity   : ${account_info.balance:,.2f} / ${account_info.equity:,.2f}")
    print(f" Mode Lot         : {cfg.lot_mode} (Risk: {cfg.risk_percent}%)")
    print(f" Target R:R       : 1:{cfg.risk_reward_ratio} (Partial Close: {'1:' + str(cfg.partial_close_rr) + 'R' if cfg.use_partial_close else 'Nonaktif'})")
    print(f" Filter SNR       : {'Aktif (Obstacle Mayor & Confluence)' if getattr(cfg, 'use_snr_filter', True) else 'Nonaktif'}")
    print(f" Filter SMC       : {'Aktif (Value Zone)' if getattr(cfg, 'use_smc_filter', True) else 'Nonaktif'}")
    print(f" Filter Fibo OTE  : {'Aktif (Golden Zone 50.0% - 78.6%)' if getattr(cfg, 'use_fibo_golden_zone', True) else 'Nonaktif'}")
    print(f" Filter RSI 14    : {'Aktif (45-70 Buy / 30-55 Sell)' if getattr(cfg, 'use_rsi_filter', True) else 'Nonaktif'}")
    print(f" Filter FVG       : {'Aktif (Imbalance Mitigation)' if getattr(cfg, 'use_fvg_filter', False) else 'Nonaktif'}")
    print(f" Filter News Shock: {'Aktif (Anti-Spike Berita > ' + str(getattr(cfg, 'fundamental_shock_atr_multiplier', 2.5)) + 'x ATR)' if getattr(cfg, 'use_fundamental_shock_filter', True) else 'Nonaktif'}")
    print(f" Filter Sesi Emas : {getattr(cfg, 'xau_session_filter', 'ALL')}")
    print(f" Auto Break-Even  : {'Aktif (1:' + str(cfg.be_trigger_rr) + 'R)' if cfg.use_break_even else 'Nonaktif'}")
    print(f" Trailing Stop    : {'Aktif (EMA 21)' if cfg.use_trailing_stop else 'Nonaktif'}")
    print(f" Circuit Breaker  : {'Maks ' + str(cfg.max_daily_losses) + ' loss / hari' if cfg.use_daily_loss_limit else 'Nonaktif'}")
    print(f" Friday Auto-Close: {'Aktif (' + str(cfg.friday_close_hour) + ':' + str(cfg.friday_close_minute) + ')' if cfg.use_friday_close else 'Nonaktif'}")
    print("=" * 65)
    print(" [STATUS] Robot berjalan... Tekan Ctrl+C di terminal untuk berhenti.\n")

def run_bot():
    cfg = TradingConfig()
    client = MT5Client()

    if not client.initialize():
        print("[FATAL ERROR] Gagal menghubungkan ke MetaTrader 5. Pastikan MT5 sudah terbuka.")
        return

    acc = client.get_account_info() if hasattr(client, 'get_account_info') else None
    # Ambil info akun langsung
    import MetaTrader5 as mt5
    acc = mt5.account_info()
    if acc is None:
        print("[FATAL ERROR] Tidak dapat membaca akun MT5.")
        client.shutdown()
        return

    # Selesaikan nama simbol broker (misal: XAUUSD -> XAUUSD.dmb)
    real_symbol = client.resolve_symbol(cfg.symbol)
    sym_info = client.get_symbol_info(real_symbol)
    if sym_info is None:
        print(f"[FATAL ERROR] Simbol {real_symbol} tidak valid di broker.")
        client.shutdown()
        return

    point_size = sym_info.point
    stops_level = sym_info.trade_stops_level
    min_broker_dist = max(stops_level * point_size, 15 * point_size)
    tick_size = sym_info.trade_tick_size
    tick_value = sym_info.trade_tick_value

    strategy = TripleEmaStrategy(cfg)
    risk_mgr = RiskManager(cfg)

    print_banner(cfg, real_symbol, acc)

    last_bar_time = None
    bars_since_last_trade = 999
    partial_closed_tickets = set()

    try:
        while True:
            # Dapatkan waktu server broker (atau lokal) terkini
            eval_time = client.get_server_time(real_symbol) if getattr(cfg, 'time_filter_use_server_time', True) else datetime.now()

            # 1. Proteksi Akhir Pekan: Jumat Malam Auto-Close
            if risk_mgr.is_friday_auto_close_time(current_dt=eval_time):
                open_positions = client.get_open_positions(symbol=real_symbol, magic=cfg.magic_number)
                if open_positions:
                    print(f"[{eval_time.strftime('%H:%M:%S')}] [Friday Auto-Close] Menutup {len(open_positions)} posisi sebelum weekend...")
                    for pos in open_positions:
                        client.close_position(pos.ticket)

            # 2. Ambil data rates terbaru untuk indikator (350 bar agar EMA 125 stabil)
            rates_count = getattr(cfg, 'history_bars_count', 350)
            rates_df = client.get_rates(real_symbol, cfg.timeframe, count=rates_count)
            if rates_df is None or len(rates_df) < 150:
                time.sleep(cfg.tick_interval_sec)
                continue

            # Hitung seluruh indikator
            rates_df = compute_all_indicators(
                rates_df,
                ema_fast=cfg.ema_fast_period,
                ema_med=cfg.ema_med_period,
                ema_slow=cfg.ema_slow_period,
                atr_period=cfg.atr_period,
                adx_period=cfg.adx_period
            )

            # Bar terakhir adalah candle yang sedang berjalan (rates_df.iloc[-1])
            # Bar -2 adalah candle yang baru saja tertutup sempurna (confirmed bar)
            curr_bar = rates_df.iloc[-1]
            closed_bar = rates_df.iloc[-2]
            current_bar_time = curr_bar['time']

            current_tick = client.get_current_tick(real_symbol)
            if current_tick is None:
                time.sleep(cfg.tick_interval_sec)
                continue

            ask = current_tick.ask
            bid = current_tick.bid
            spread_points = int(current_tick.spread) if hasattr(current_tick, 'spread') else int((ask - bid) / point_size)
            current_ema21 = curr_bar['ema21']
            current_atr = closed_bar['atr']

            # 3. Kelola Posisi Aktif (Partial Close, Break-Even & Trailing Stop) setiap tick
            open_positions = client.get_open_positions(symbol=real_symbol, magic=cfg.magic_number)
            active_tickets = {p.ticket for p in open_positions}
            # Bersihkan cache partial close tiket yang sudah ditutup
            partial_closed_tickets.intersection_update(active_tickets)

            for pos in open_positions:
                ticket = pos.ticket
                pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                open_price = pos.price_open
                current_sl = pos.sl
                current_tp = pos.tp
                curr_price = bid if pos_type == "BUY" else ask
                curr_vol = pos.volume

                # A. Cek Partial Take Profit (Scale-Out di 1:1.0 R:R)
                if getattr(cfg, 'use_partial_close', True) and (ticket not in partial_closed_tickets):
                    should_partial, vol_to_close = risk_mgr.evaluate_partial_close(
                        pos_type=pos_type,
                        open_price=open_price,
                        current_price=curr_price,
                        initial_sl=current_sl,
                        current_volume=curr_vol,
                        initial_volume=curr_vol,
                        volume_min=sym_info.volume_min,
                        volume_step=sym_info.volume_step
                    )
                    if should_partial and vol_to_close > 0:
                        if client.close_position(ticket, volume=vol_to_close):
                            partial_closed_tickets.add(ticket)
                            print(f"[{eval_time.strftime('%H:%M:%S')}] [Partial TP] #{ticket} {pos_type} Sukses tutup partial {vol_to_close} lot di 1:1 R:R!")
                            # Setelah partial close, otomatis pasang BEP
                            new_bep_sl = open_price + (cfg.be_lock_profit_points * point_size if pos_type == "BUY" else -cfg.be_lock_profit_points * point_size)
                            client.modify_position(ticket, new_bep_sl, current_tp)
                            continue

                # B. Cek Auto Break-Even
                new_bep_sl = risk_mgr.evaluate_break_even(
                    pos_type=pos_type,
                    open_price=open_price,
                    current_sl=current_sl,
                    current_price=curr_price,
                    point_size=point_size,
                    min_broker_dist=min_broker_dist
                )
                if new_bep_sl is not None:
                    if client.modify_position(ticket, new_bep_sl, current_tp):
                        print(f"[{eval_time.strftime('%H:%M:%S')}] [Auto BEP] #{ticket} {pos_type} SL digeser ke BEP: {new_bep_sl}")
                    continue

                # C. Cek Trailing Stop
                new_trail_sl = risk_mgr.evaluate_trailing_stop(
                    pos_type=pos_type,
                    open_price=open_price,
                    current_sl=current_sl,
                    current_price=curr_price,
                    ema21_val=current_ema21,
                    atr_val=current_atr,
                    point_size=point_size,
                    min_broker_dist=min_broker_dist
                )
                if new_trail_sl is not None:
                    if client.modify_position(ticket, new_trail_sl, current_tp):
                        print(f"[{eval_time.strftime('%H:%M:%S')}] [Trailing Stop] #{ticket} {pos_type} Trailing SL diperbarui: {new_trail_sl}")

            # 4. Deteksi Pembentukan Candle Baru (Evaluasi Sinyal Entry)
            if last_bar_time is None:
                last_bar_time = current_bar_time

            if current_bar_time != last_bar_time:
                bars_since_last_trade += 1
                now_str = eval_time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{now_str}] Candle baru terbentuk ({current_bar_time}). Evaluasi candle #{len(rates_df)-2}...")

                # Cek batas maksimal posisi terbuka
                if len(open_positions) >= cfg.max_open_positions:
                    last_bar_time = current_bar_time
                    time.sleep(cfg.tick_interval_sec)
                    continue

                # Cek jeda Cooldown antar sinyal
                if bars_since_last_trade < cfg.signal_cooldown_bars:
                    print(f"[{now_str}] [COOLDOWN] Menunggu jeda ({bars_since_last_trade}/{cfg.signal_cooldown_bars} candle sejak trade terakhir).")
                    last_bar_time = current_bar_time
                    time.sleep(cfg.tick_interval_sec)
                    continue

                # Sinkronkan data Circuit Breaker riwayat deal MT5 hari ini
                closed_deals = client.get_daily_closed_deals(symbol=real_symbol, magic=cfg.magic_number)
                risk_mgr.sync_daily_stats_from_deals(closed_deals)

                # Evaluasi Circuit Breaker kerugian harian
                acc_info = mt5.account_info()
                current_equity = acc_info.equity if acc_info else 10000.0
                cb_triggered, cb_reason = risk_mgr.is_daily_circuit_breaker_triggered(current_equity)
                if cb_triggered:
                    print(f"[{now_str}] [CIRCUIT BREAKER] {cb_reason}")
                    last_bar_time = current_bar_time
                    time.sleep(cfg.tick_interval_sec)
                    continue

                # Cek Filter Jam Trading (berdasarkan waktu server broker)
                if not risk_mgr.is_trading_time_allowed(current_dt=eval_time):
                    last_bar_time = current_bar_time
                    time.sleep(cfg.tick_interval_sec)
                    continue

                # Cek Restriksi Hari Jumat
                if risk_mgr.is_friday_trading_restricted(current_dt=eval_time):
                    last_bar_time = current_bar_time
                    time.sleep(cfg.tick_interval_sec)
                    continue

                # Cek Spread Maksimal
                if spread_points > cfg.max_spread_points:
                    print(f"[{now_str}] [FILTER SPREAD] Spread ({spread_points} pts) melebihi batas maksimal ({cfg.max_spread_points} pts).")
                    last_bar_time = current_bar_time
                    time.sleep(cfg.tick_interval_sec)
                    continue

                # Evaluasi Multi-Timeframe (HTF) jika aktif
                htf_bullish = True
                htf_bearish = True
                if cfg.use_mtf_filter:
                    htf_df = client.get_rates(real_symbol, cfg.htf_timeframe, count=120)
                    if htf_df is not None and len(htf_df) >= cfg.htf_ema_period:
                        htf_ema = calculate_ema(htf_df['close'], cfg.htf_ema_period)
                        htf_close_1 = htf_df['close'].iloc[-2]
                        htf_ema_1 = htf_ema.iloc[-2]
                        htf_bullish = htf_close_1 > htf_ema_1
                        htf_bearish = htf_close_1 < htf_ema_1

                # Evaluasi Sinyal Strategi pada bar yang baru saja closed (shift = -2)
                signal: Optional[TradeSignal] = strategy.evaluate_signal(
                    df=rates_df,
                    current_ask=ask,
                    current_bid=bid,
                    point_size=point_size,
                    htf_bullish=htf_bullish,
                    htf_bearish=htf_bearish,
                    shift=-2
                )

                if signal is not None:
                    print(f"[{now_str}] [SINYAL {signal.signal_type}] {signal.reason}")
                    if signal.nearest_support or signal.nearest_resistance:
                        sup_s = f"{signal.nearest_support:.2f}" if signal.nearest_support else "None"
                        res_s = f"{signal.nearest_resistance:.2f}" if signal.nearest_resistance else "None"
                        print(f"[{now_str}] [SNR Info] Support: {sup_s} | Resistance: {res_s}")

                    # Hitung Lot Size Dinamis
                    lot = risk_mgr.calculate_lot_size(
                        equity=current_equity,
                        sl_distance_points=signal.sl_distance_points,
                        point_size=point_size,
                        tick_size=tick_size,
                        tick_value=tick_value,
                        min_lot=sym_info.volume_min,
                        max_lot=sym_info.volume_max,
                        lot_step=sym_info.volume_step
                    )

                    comment = f"{cfg.order_comment}_{signal.pattern.name}"

                    if signal.signal_type == "BUY":
                        ticket = client.open_buy(
                            symbol=real_symbol,
                            lot=lot,
                            sl=signal.stop_loss,
                            tp=signal.take_profit,
                            magic=cfg.magic_number,
                            comment=comment
                        )
                        if ticket:
                            bars_since_last_trade = 0
                    elif signal.signal_type == "SELL":
                        ticket = client.open_sell(
                            symbol=real_symbol,
                            lot=lot,
                            sl=signal.stop_loss,
                            tp=signal.take_profit,
                            magic=cfg.magic_number,
                            comment=comment
                        )
                        if ticket:
                            bars_since_last_trade = 0

                last_bar_time = current_bar_time

            # Tidur sejenak sebelum tick berikutnya
            time.sleep(cfg.tick_interval_sec)

    except KeyboardInterrupt:
        print("\n[ROBOT STOP] Pengguna menghentikan robot via KeyboardInterrupt (Ctrl+C).")
    finally:
        client.shutdown()
        print("[Selesai] Robot trading dimatikan dengan aman.")

if __name__ == "__main__":
    run_bot()
