"""
Modul Backtester Strategi Triple EMA Pullback
Mendukung:
1. Mode Unconstrained (Bebas / Multi-Posisi) & Mode Single-Position (Realistis)
2. Filter Multi-Timeframe (HTF) Sejati berbasis Resampling H1
3. Diagnostik & Telemetri False Signal (Klasifikasi Fakeout, MFE/MAE, Breakdown Sesi & Pola)
4. Eksekusi Bar-by-Bar realistis: Partial Take Profit 1:1R, Auto-BEP, Trailing Stop EMA 21
"""

import math
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from config import TradingConfig
from indicators import compute_all_indicators
from strategy import TripleEmaStrategy, TradeSignal

class BacktestTrade:
    def __init__(self, ticket: int, signal_type: str, open_time: Any, 
                 open_price: float, lot: float, sl: float, tp: float, pattern: str,
                 session: str = "UNKNOWN", entry_bar_idx: int = 0):
        self.ticket = ticket
        self.signal_type = signal_type
        self.open_time = open_time
        self.open_price = open_price
        self.initial_lot = lot
        self.lot = lot
        self.initial_sl = sl
        self.current_sl = sl
        self.tp = tp
        self.pattern = pattern
        self.session = session
        self.entry_bar_idx = entry_bar_idx
        
        self.close_time = None
        self.close_price = 0.0
        self.profit = 0.0
        self.is_closed = False
        self.exit_reason = ""
        self.is_partial_closed = False
        self.partial_profit = 0.0
        
        # Telemetri False Signal & Excursion
        self.sl_dist_abs = abs(open_price - sl)
        self.max_mfe_r = 0.0  # Maximum Favorable Excursion (dalam satuan R)
        self.max_mae_r = 0.0  # Maximum Adverse Excursion (dalam satuan R)
        self.is_false_signal = False
        self.status = "OPEN"  # "WIN", "BEP", "FALSE_SIGNAL", "LOSS"
        self.hold_bars = 0
        self.r_multiple = 0.0

class TripleEmaBacktester:
    def __init__(self, config: TradingConfig, initial_balance: float = 10000.0, point_size: float = 0.01):
        self.config = config
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.point_size = point_size
        self.strategy = TripleEmaStrategy(config)
        self.trades: List[BacktestTrade] = []
        self.trade_records: List[Dict[str, Any]] = []
        self.equity_curve: List[float] = [initial_balance]

    def _prepare_htf_trend_map(self, df: pd.DataFrame) -> Dict[str, Dict[Any, bool]]:
        """
        Menyiapkan peta tren Multi-Timeframe (HTF H1) sejati dari candle M15
        agar backtest tidak menggunakan nilai dummy.
        """
        htf_map = {'bull': {}, 'bear': {}}
        if not self.config.use_mtf_filter or 'time' not in df.columns:
            return htf_map

        try:
            temp_df = df.copy()
            temp_df['dt'] = pd.to_datetime(temp_df['time'])
            # Resample M15 ke H1
            h1_df = temp_df.set_index('dt').resample('1h').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            }).dropna()

            period = getattr(self.config, 'htf_ema_period', 50)
            if len(h1_df) >= period:
                h1_df['htf_ema'] = h1_df['close'].ewm(span=period, adjust=False).mean()
                for idx, row in h1_df.iterrows():
                    htf_map['bull'][idx] = bool(row['close'] > row['htf_ema'])
                    htf_map['bear'][idx] = bool(row['close'] < row['htf_ema'])
        except Exception:
            pass

        return htf_map

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Menjalankan backtest bar-by-bar dengan opsi Unconstrained / Multi-Posisi."""
        mode_str = getattr(self.config, 'backtest_mode', 'UNCONSTRAINED')
        print(f"\n[Backtest Dimulai] Memproses {len(df)} candle data (Mode: {mode_str})...")
        
        df = compute_all_indicators(
            df,
            ema_fast=self.config.ema_fast_period,
            ema_med=self.config.ema_med_period,
            ema_slow=self.config.ema_slow_period,
            atr_period=self.config.atr_period,
            adx_period=self.config.adx_period,
            rsi_period=getattr(self.config, 'rsi_period', 14)
        )

        htf_map = self._prepare_htf_trend_map(df)
        has_htf_data = len(htf_map['bull']) > 0

        open_trades: List[BacktestTrade] = []
        ticket_counter = 1
        last_signal_bar = -999

        start_bar = max(135, self.config.ema_slow_period + 10)
        unconstrained = (mode_str.upper() == "UNCONSTRAINED")
        max_positions = getattr(self.config, 'backtest_max_open_positions', 0)
        ignore_cooldown = getattr(self.config, 'backtest_ignore_cooldown', True) if unconstrained else False
        mfe_thresh = getattr(self.config, 'false_signal_mfe_threshold', 0.5)

        for i in range(start_bar, len(df)):
            curr_bar = df.iloc[i]
            bar_time = curr_bar['time']
            high = curr_bar['high']
            low = curr_bar['low']
            open_p = curr_bar['open']
            close_p = curr_bar['close']
            ema21_val = curr_bar['ema21']
            atr_val = curr_bar['atr']

            # -------------------------------------------------------------
            # 1. Kelola Semua Posisi Terbuka (Trailing, BEP, TP, SL, MFE/MAE)
            # -------------------------------------------------------------
            remaining_open_trades: List[BacktestTrade] = []

            for trade in open_trades:
                init_sl_dist = trade.sl_dist_abs

                if trade.signal_type == "BUY":
                    # Update MFE & MAE
                    if init_sl_dist > 0:
                        cur_mfe = (high - trade.open_price) / init_sl_dist
                        cur_mae = (trade.open_price - low) / init_sl_dist
                        trade.max_mfe_r = max(trade.max_mfe_r, cur_mfe)
                        trade.max_mae_r = max(trade.max_mae_r, cur_mae)

                    hit_sl = low <= trade.current_sl
                    hit_tp = high >= trade.tp

                    if hit_sl and hit_tp:
                        hit_sl = close_p < open_p
                        hit_tp = not hit_sl

                    if hit_sl:
                        trade.close_price = trade.current_sl
                        trade.close_time = bar_time
                        trade.is_closed = True
                        trade.exit_reason = "Stop Loss"
                    elif hit_tp:
                        trade.close_price = trade.tp
                        trade.close_time = bar_time
                        trade.is_closed = True
                        trade.exit_reason = "Take Profit"
                    else:
                        current_profit_dist = high - trade.open_price
                        current_r = current_profit_dist / init_sl_dist if init_sl_dist > 0 else 0
                        
                        # Partial Take Profit Check (1:1.0 R:R)
                        if getattr(self.config, 'use_partial_close', True) and not trade.is_partial_closed and current_r >= getattr(self.config, 'partial_close_rr', 1.0):
                            partial_lot = round(trade.initial_lot * (getattr(self.config, 'partial_close_percent', 50.0) / 100.0), 2)
                            if partial_lot >= 0.01 and (trade.lot - partial_lot) >= 0.01:
                                p_diff = (init_sl_dist * getattr(self.config, 'partial_close_rr', 1.0))
                                trade.partial_profit = p_diff * partial_lot * 100.0
                                trade.lot = round(trade.lot - partial_lot, 2)
                                trade.is_partial_closed = True
                                self.balance += trade.partial_profit
                                # Otomatis geser SL ke BEP
                                bep_sl = trade.open_price + (self.config.be_lock_profit_points * self.point_size)
                                trade.current_sl = max(trade.current_sl, bep_sl)

                        # Auto Break-Even Check
                        if self.config.use_break_even and current_r >= self.config.be_trigger_rr:
                            bep_sl = trade.open_price + (self.config.be_lock_profit_points * self.point_size)
                            if trade.current_sl < bep_sl:
                                trade.current_sl = bep_sl

                        # Trailing Stop Check
                        if self.config.use_trailing_stop and current_r >= self.config.trailing_start_rr:
                            if self.config.trailing_by_ema21:
                                target_trail = ema21_val - (20 * self.point_size)
                            else:
                                target_trail = close_p - (self.config.trailing_atr_mult * atr_val)

                            if target_trail > trade.open_price and target_trail > trade.current_sl:
                                trade.current_sl = target_trail

                elif trade.signal_type == "SELL":
                    # Update MFE & MAE
                    if init_sl_dist > 0:
                        cur_mfe = (trade.open_price - low) / init_sl_dist
                        cur_mae = (high - trade.open_price) / init_sl_dist
                        trade.max_mfe_r = max(trade.max_mfe_r, cur_mfe)
                        trade.max_mae_r = max(trade.max_mae_r, cur_mae)

                    hit_sl = high >= trade.current_sl
                    hit_tp = low <= trade.tp

                    if hit_sl and hit_tp:
                        hit_sl = close_p > open_p
                        hit_tp = not hit_sl

                    if hit_sl:
                        trade.close_price = trade.current_sl
                        trade.close_time = bar_time
                        trade.is_closed = True
                        trade.exit_reason = "Stop Loss"
                    elif hit_tp:
                        trade.close_price = trade.tp
                        trade.close_time = bar_time
                        trade.is_closed = True
                        trade.exit_reason = "Take Profit"
                    else:
                        current_profit_dist = trade.open_price - low
                        current_r = current_profit_dist / init_sl_dist if init_sl_dist > 0 else 0
                        
                        # Partial Take Profit Check (1:1.0 R:R)
                        if getattr(self.config, 'use_partial_close', True) and not trade.is_partial_closed and current_r >= getattr(self.config, 'partial_close_rr', 1.0):
                            partial_lot = round(trade.initial_lot * (getattr(self.config, 'partial_close_percent', 50.0) / 100.0), 2)
                            if partial_lot >= 0.01 and (trade.lot - partial_lot) >= 0.01:
                                p_diff = (init_sl_dist * getattr(self.config, 'partial_close_rr', 1.0))
                                trade.partial_profit = p_diff * partial_lot * 100.0
                                trade.lot = round(trade.lot - partial_lot, 2)
                                trade.is_partial_closed = True
                                self.balance += trade.partial_profit
                                # Otomatis geser SL ke BEP
                                bep_sl = trade.open_price - (self.config.be_lock_profit_points * self.point_size)
                                trade.current_sl = min(trade.current_sl, bep_sl)

                        # Auto Break-Even Check
                        if self.config.use_break_even and current_r >= self.config.be_trigger_rr:
                            bep_sl = trade.open_price - (self.config.be_lock_profit_points * self.point_size)
                            if trade.current_sl > bep_sl:
                                trade.current_sl = bep_sl

                        # Trailing Stop Check
                        if self.config.use_trailing_stop and current_r >= self.config.trailing_start_rr:
                            if self.config.trailing_by_ema21:
                                target_trail = ema21_val + (20 * self.point_size)
                            else:
                                target_trail = close_p + (self.config.trailing_atr_mult * atr_val)

                            if target_trail < trade.open_price and target_trail < trade.current_sl:
                                trade.current_sl = target_trail

                # Evaluasi jika trade selesai pada bar ini
                if trade.is_closed:
                    diff = (trade.close_price - trade.open_price) if trade.signal_type == "BUY" else (trade.open_price - trade.close_price)
                    remaining_profit = diff * trade.lot * 100.0
                    trade.profit = remaining_profit + trade.partial_profit
                    trade.hold_bars = i - trade.entry_bar_idx
                    self.balance += remaining_profit
                    self.equity_curve.append(self.balance)

                    # Klasifikasi Status & False Signal
                    if init_sl_dist > 0:
                        trade.r_multiple = round(diff / init_sl_dist, 2)

                    if trade.profit > 0.01:
                        trade.status = "WIN"
                    elif abs(trade.profit) <= 1.0 or trade.is_partial_closed:
                        trade.status = "BEP"
                    elif trade.max_mfe_r < mfe_thresh:
                        trade.is_false_signal = True
                        trade.status = "FALSE_SIGNAL"
                    else:
                        trade.status = "LOSS"

                    self.trades.append(trade)
                    self.trade_records.append({
                        "ticket": trade.ticket,
                        "time": str(trade.open_time),
                        "close_time": str(trade.close_time),
                        "type": trade.signal_type,
                        "pattern": trade.pattern,
                        "session": trade.session,
                        "entry": round(trade.open_price, 2),
                        "sl": round(trade.initial_sl, 2),
                        "tp": round(trade.tp, 2),
                        "exit": round(trade.close_price, 2),
                        "profit": round(trade.profit, 2),
                        "r_multiple": trade.r_multiple,
                        "max_mfe_r": round(trade.max_mfe_r, 2),
                        "status": trade.status,
                        "exit_reason": trade.exit_reason
                    })
                else:
                    remaining_open_trades.append(trade)

            open_trades = remaining_open_trades

            # -------------------------------------------------------------
            # 2. Evaluasi Sinyal Baru
            # -------------------------------------------------------------
            can_enter = False
            if unconstrained:
                # Mode Tanpa Batasan: Boleh buka posisi kapan saja sinyal valid muncul
                if max_positions > 0:
                    can_enter = len(open_trades) < max_positions
                else:
                    can_enter = True
            else:
                # Mode Tradisional: Hanya jika tidak ada posisi terbuka
                can_enter = (len(open_trades) == 0)

            if not ignore_cooldown:
                if (i - last_signal_bar) < self.config.signal_cooldown_bars:
                    can_enter = False

            if can_enter:
                # Filter jam trading umum
                if hasattr(bar_time, 'hour'):
                    if self.config.use_time_filter and (bar_time.hour < self.config.start_hour or bar_time.hour >= self.config.end_hour):
                        continue

                # Evaluasi tren HTF sejati jika data tersedia
                htf_bull = True
                htf_bear = True
                if has_htf_data:
                    try:
                        dt_floor = pd.to_datetime(bar_time).floor('1h')
                        htf_bull = htf_map['bull'].get(dt_floor, True)
                        htf_bear = htf_map['bear'].get(dt_floor, True)
                    except Exception:
                        pass

                sub_df = df.iloc[:i]
                open_next = curr_bar['open']

                signal: Optional[TradeSignal] = self.strategy.evaluate_signal(
                    df=sub_df,
                    current_ask=open_next,
                    current_bid=open_next,
                    point_size=self.point_size,
                    htf_bullish=htf_bull,
                    htf_bearish=htf_bear,
                    shift=-1
                )

                if signal is not None:
                    sl_dist_points = signal.sl_distance_points
                    risk_money = self.balance * (self.config.risk_percent / 100.0)
                    point_val = self.point_size * 100.0
                    calc_lot = (risk_money / (sl_dist_points * point_val)) if (sl_dist_points * point_val) > 0 else 0.01
                    lot = max(0.01, min(self.config.max_lot_size, round(calc_lot, 2)))

                    new_trade = BacktestTrade(
                        ticket=ticket_counter,
                        signal_type=signal.signal_type,
                        open_time=bar_time,
                        open_price=open_next,
                        lot=lot,
                        sl=signal.stop_loss,
                        tp=signal.take_profit,
                        pattern=signal.pattern_name,
                        session=getattr(signal, 'session_name', 'UNKNOWN'),
                        entry_bar_idx=i
                    )
                    open_trades.append(new_trade)
                    ticket_counter += 1
                    last_signal_bar = i

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Menghasilkan metrik performa & telemetri False Signal komprehensif."""
        total_trades = len(self.trades)
        if total_trades == 0:
            print("[Backtest Hasil] Tidak ada trade yang dieksekusi.")
            return {"total_trades": 0, "net_profit": 0.0, "win_rate_percent": 0.0}

        wins = [t for t in self.trades if t.profit > 0]
        losses = [t for t in self.trades if t.profit <= 0]
        beps = [t for t in self.trades if t.status == "BEP"]
        false_sigs = [t for t in self.trades if t.is_false_signal]
        normal_losses = [t for t in self.trades if t.status == "LOSS"]

        win_count = len(wins)
        loss_count = len(losses)
        false_sig_count = len(false_sigs)
        bep_count = len(beps)

        win_rate = (win_count / total_trades) * 100.0
        false_rate = (false_sig_count / total_trades) * 100.0

        gross_profit = sum(t.profit for t in wins)
        gross_loss = abs(sum(t.profit for t in losses))
        net_profit = gross_profit - gross_loss
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')

        # Maximum Drawdown
        peak = self.initial_balance
        max_dd = 0.0
        max_dd_pct = 0.0
        for eq in self.equity_curve:
            if eq > peak:
                peak = eq
            dd = peak - eq
            dd_pct = (dd / peak) * 100.0 if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
            if dd_pct > max_dd_pct:
                max_dd_pct = dd_pct

        avg_mfe = np.mean([t.max_mfe_r for t in self.trades]) if self.trades else 0.0
        avg_mae = np.mean([t.max_mae_r for t in self.trades]) if self.trades else 0.0

        # Breakdown False Signal by Pattern & Session
        pattern_breakdown: Dict[str, int] = {}
        session_breakdown: Dict[str, int] = {}
        for t in false_sigs:
            pattern_breakdown[t.pattern] = pattern_breakdown.get(t.pattern, 0) + 1
            session_breakdown[t.session] = session_breakdown.get(t.session, 0) + 1

        report = {
            "initial_balance": self.initial_balance,
            "final_balance": round(self.balance, 2),
            "net_profit": round(net_profit, 2),
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "bep_trades": bep_count,
            "false_signals_count": false_sig_count,
            "false_signal_rate_percent": round(false_rate, 2),
            "normal_losses_count": len(normal_losses),
            "win_rate_percent": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "Inf",
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "max_drawdown_amount": round(max_dd, 2),
            "max_drawdown_percent": round(max_dd_pct, 2),
            "avg_mfe_r": round(float(avg_mfe), 2),
            "avg_mae_r": round(float(avg_mae), 2),
            "false_signals_by_pattern": pattern_breakdown,
            "false_signals_by_session": session_breakdown,
            "trades_list": self.trade_records
        }

        mode_desc = "UNCONSTRAINED (Semua Sinyal Diuji)" if getattr(self.config, 'backtest_mode', 'UNCONSTRAINED') == 'UNCONSTRAINED' else "SINGLE POSITION (Realistis)"

        print("\n" + "=" * 65)
        print("   [LAPORAN PERFORMA BACKTEST & AUDIT FALSE SIGNAL XAUUSD]")
        print("=" * 65)
        print(f" Mode Simulasi     : {mode_desc}")
        print(f" Modal Awal        : ${report['initial_balance']:,.2f}")
        print(f" Saldo Akhir       : ${report['final_balance']:,.2f}")
        print(f" Net Profit        : ${report['net_profit']:,.2f} ({((report['net_profit']/report['initial_balance'])*100):.2f}%)")
        print(f" Total Transaksi   : {report['total_trades']}")
        print(f" Menang / Kalah    : {report['winning_trades']} Win / {report['losing_trades']} Loss ({report['bep_trades']} BEP)")
        print(f" Win Rate          : {report['win_rate_percent']}%")
        print(f" Profit Factor     : {report['profit_factor']}")
        print(f" Max Drawdown      : ${report['max_drawdown_amount']:,.2f} ({report['max_drawdown_percent']}%)")
        print("-" * 65)
        print("  TELEMETRI FALSE SIGNAL (FAKEOUT / JEBAKAN):")
        print(f"  • False Signal Count : {report['false_signals_count']} trade (MFE < {getattr(self.config, 'false_signal_mfe_threshold', 0.5)}R)")
        print(f"  • False Signal Rate  : {report['false_signal_rate_percent']}% dari seluruh sinyal")
        print(f"  • Normal Reversals   : {report['normal_losses_count']} trade (Sempat profit >= 0.5R)")
        print(f"  • Rata-rata MFE      : {report['avg_mfe_r']} R (Jangkauan profit maksimal)")
        print(f"  • Rata-rata MAE      : {report['avg_mae_r']} R (Jangkauan drawdown per trade)")
        if pattern_breakdown:
            print(f"  • False Sigs by Pattern: {dict(sorted(pattern_breakdown.items(), key=lambda x: x[1], reverse=True))}")
        if session_breakdown:
            print(f"  • False Sigs by Session: {session_breakdown}")
        print("=" * 65 + "\n")

        return report

if __name__ == "__main__":
    from mt5_client import MT5Client
    
    cfg = TradingConfig(symbol="XAUUSD", timeframe="M5")
    cfg.backtest_mode = "UNCONSTRAINED"
    client = MT5Client()
    
    if client.initialize():
        print("[Backtester] Mengambil data historis dari MT5...")
        rates_df = client.get_rates("XAUUSD", "M5", count=3000)
        client.shutdown()
        
        if rates_df is not None:
            bt = TripleEmaBacktester(cfg, initial_balance=10000.0, point_size=0.01)
            bt.run(rates_df)
    else:
        print("[Backtester] MT5 terminal tidak aktif. Menggunakan data simulasi acak untuk validasi...")
        np.random.seed(42)
        n = 500
        dates = pd.date_range("2026-01-01", periods=n, freq="15min")
        price = 2000.0 + np.cumsum(np.random.randn(n) * 2.0)
        sim_df = pd.DataFrame({
            'time': dates,
            'open': price + np.random.randn(n) * 0.5,
            'high': price + np.abs(np.random.randn(n) * 1.5),
            'low': price - np.abs(np.random.randn(n) * 1.5),
            'close': price + np.random.randn(n) * 0.5,
            'tick_volume': 100
        })
        bt = TripleEmaBacktester(cfg, initial_balance=10000.0, point_size=0.01)
        bt.run(sim_df)
