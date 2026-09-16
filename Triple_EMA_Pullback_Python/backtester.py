"""
Modul Backtester Strategi Triple EMA Pullback
Menjalankan simulasi historis bar-by-bar dengan eksekusi realistis,
Auto Break-Even, Trailing Stop, dan laporan statistik performa lengkap.
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
                 open_price: float, lot: float, sl: float, tp: float, pattern: str):
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
        
        self.close_time = None
        self.close_price = 0.0
        self.profit = 0.0
        self.is_closed = False
        self.exit_reason = ""
        self.is_partial_closed = False
        self.partial_profit = 0.0

class TripleEmaBacktester:
    def __init__(self, config: TradingConfig, initial_balance: float = 10000.0, point_size: float = 0.01):
        self.config = config
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.point_size = point_size
        self.strategy = TripleEmaStrategy(config)
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[float] = [initial_balance]

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Menjalankan backtest bar-by-bar."""
        print(f"\n[Backtest Dimulai] Memproses {len(df)} candle data...")
        df = compute_all_indicators(
            df,
            ema_fast=self.config.ema_fast_period,
            ema_med=self.config.ema_med_period,
            ema_slow=self.config.ema_slow_period,
            atr_period=self.config.atr_period,
            adx_period=self.config.adx_period
        )

        active_trade: Optional[BacktestTrade] = None
        ticket_counter = 1
        last_signal_bar = -999

        # Mulai simulasi setelah periode pemanasan indikator (misal bar 135)
        start_bar = max(135, self.config.ema_slow_period + 10)

        for i in range(start_bar, len(df)):
            curr_bar = df.iloc[i]
            prev_bar = df.iloc[i - 1]
            
            # 1. Kelola trade aktif pada candle saat ini
            if active_trade is not None and not active_trade.is_closed:
                high = curr_bar['high']
                low = curr_bar['low']
                open_p = curr_bar['open']
                close_p = curr_bar['close']
                ema21_val = curr_bar['ema21']
                atr_val = curr_bar['atr']

                # Hitung rasio R saat ini
                init_sl_dist = abs(active_trade.open_price - active_trade.initial_sl)
                
                if active_trade.signal_type == "BUY":
                    # Cek Hit SL atau TP
                    hit_sl = low <= active_trade.current_sl
                    hit_tp = high >= active_trade.tp

                    if hit_sl and hit_tp:
                        # Asumsi wajar: jika bar bearish terkena SL dulu, jika bullish terkena TP dulu
                        hit_sl = close_p < open_p
                        hit_tp = not hit_sl

                    if hit_sl:
                        active_trade.close_price = active_trade.current_sl
                        active_trade.close_time = curr_bar['time']
                        active_trade.is_closed = True
                        active_trade.exit_reason = "Stop Loss"
                    elif hit_tp:
                        active_trade.close_price = active_trade.tp
                        active_trade.close_time = curr_bar['time']
                        active_trade.is_closed = True
                        active_trade.exit_reason = "Take Profit"
                    else:
                        current_profit_dist = high - active_trade.open_price
                        current_r = current_profit_dist / init_sl_dist if init_sl_dist > 0 else 0
                        
                        # Partial Take Profit Check (1:1.0 R:R)
                        if getattr(self.config, 'use_partial_close', True) and not active_trade.is_partial_closed and current_r >= getattr(self.config, 'partial_close_rr', 1.0):
                            partial_lot = round(active_trade.initial_lot * (getattr(self.config, 'partial_close_percent', 50.0) / 100.0), 2)
                            if partial_lot >= 0.01 and (active_trade.lot - partial_lot) >= 0.01:
                                p_diff = (init_sl_dist * getattr(self.config, 'partial_close_rr', 1.0))
                                active_trade.partial_profit = p_diff * partial_lot * 100.0
                                active_trade.lot = round(active_trade.lot - partial_lot, 2)
                                active_trade.is_partial_closed = True
                                self.balance += active_trade.partial_profit
                                # Otomatis geser SL ke BEP
                                bep_sl = active_trade.open_price + (self.config.be_lock_profit_points * self.point_size)
                                active_trade.current_sl = max(active_trade.current_sl, bep_sl)

                        # Auto Break-Even Check
                        if self.config.use_break_even and current_r >= self.config.be_trigger_rr:
                            bep_sl = active_trade.open_price + (self.config.be_lock_profit_points * self.point_size)
                            if active_trade.current_sl < bep_sl:
                                active_trade.current_sl = bep_sl

                        # Trailing Stop Check
                        if self.config.use_trailing_stop and current_r >= self.config.trailing_start_rr:
                            if self.config.trailing_by_ema21:
                                target_trail = ema21_val - (20 * self.point_size)
                            else:
                                target_trail = close_p - (self.config.trailing_atr_mult * atr_val)

                            if target_trail > active_trade.open_price and target_trail > active_trade.current_sl:
                                active_trade.current_sl = target_trail

                elif active_trade.signal_type == "SELL":
                    hit_sl = high >= active_trade.current_sl
                    hit_tp = low <= active_trade.tp

                    if hit_sl and hit_tp:
                        hit_sl = close_p > open_p
                        hit_tp = not hit_sl

                    if hit_sl:
                        active_trade.close_price = active_trade.current_sl
                        active_trade.close_time = curr_bar['time']
                        active_trade.is_closed = True
                        active_trade.exit_reason = "Stop Loss"
                    elif hit_tp:
                        active_trade.close_price = active_trade.tp
                        active_trade.close_time = curr_bar['time']
                        active_trade.is_closed = True
                        active_trade.exit_reason = "Take Profit"
                    else:
                        current_profit_dist = active_trade.open_price - low
                        current_r = current_profit_dist / init_sl_dist if init_sl_dist > 0 else 0
                        
                        # Partial Take Profit Check (1:1.0 R:R)
                        if getattr(self.config, 'use_partial_close', True) and not active_trade.is_partial_closed and current_r >= getattr(self.config, 'partial_close_rr', 1.0):
                            partial_lot = round(active_trade.initial_lot * (getattr(self.config, 'partial_close_percent', 50.0) / 100.0), 2)
                            if partial_lot >= 0.01 and (active_trade.lot - partial_lot) >= 0.01:
                                p_diff = (init_sl_dist * getattr(self.config, 'partial_close_rr', 1.0))
                                active_trade.partial_profit = p_diff * partial_lot * 100.0
                                active_trade.lot = round(active_trade.lot - partial_lot, 2)
                                active_trade.is_partial_closed = True
                                self.balance += active_trade.partial_profit
                                # Otomatis geser SL ke BEP
                                bep_sl = active_trade.open_price - (self.config.be_lock_profit_points * self.point_size)
                                active_trade.current_sl = min(active_trade.current_sl, bep_sl)

                        # Auto Break-Even Check
                        if self.config.use_break_even and current_r >= self.config.be_trigger_rr:
                            bep_sl = active_trade.open_price - (self.config.be_lock_profit_points * self.point_size)
                            if active_trade.current_sl > bep_sl:
                                active_trade.current_sl = bep_sl

                        # Trailing Stop Check
                        if self.config.use_trailing_stop and current_r >= self.config.trailing_start_rr:
                            if self.config.trailing_by_ema21:
                                target_trail = ema21_val + (20 * self.point_size)
                            else:
                                target_trail = close_p + (self.config.trailing_atr_mult * atr_val)

                            if target_trail < active_trade.open_price and target_trail < active_trade.current_sl:
                                active_trade.current_sl = target_trail

                # Hitung profit jika posisi ditutup
                if active_trade.is_closed:
                    diff = (active_trade.close_price - active_trade.open_price) if active_trade.signal_type == "BUY" else (active_trade.open_price - active_trade.close_price)
                    # Kalkulasi profit dalam USD untuk Gold (1 lot = 100 oz)
                    remaining_profit = diff * active_trade.lot * 100.0
                    active_trade.profit = remaining_profit + active_trade.partial_profit
                    self.balance += remaining_profit
                    self.trades.append(active_trade)
                    self.equity_curve.append(self.balance)
                    active_trade = None

            # 2. Cek Sinyal Baru jika tidak ada trade aktif
            if active_trade is None and (i - last_signal_bar >= self.config.signal_cooldown_bars):
                # Filter jam trading
                bar_time = curr_bar['time']
                if hasattr(bar_time, 'hour'):
                    if self.config.use_time_filter and (bar_time.hour < self.config.start_hour or bar_time.hour >= self.config.end_hour):
                        continue

                # Evaluasi sinyal pada candle tertutup (i - 1)
                sub_df = df.iloc[:i]
                open_next = curr_bar['open']
                
                signal: Optional[TradeSignal] = self.strategy.evaluate_signal(
                    df=sub_df,
                    current_ask=open_next,
                    current_bid=open_next,
                    point_size=self.point_size,
                    htf_bullish=True,
                    htf_bearish=True,
                    shift=-1
                )

                if signal is not None:
                    # Hitung Lot Size
                    sl_dist_points = signal.sl_distance_points
                    risk_money = self.balance * (self.config.risk_percent / 100.0)
                    point_val = self.point_size * 100.0 # Standard contract
                    calc_lot = (risk_money / (sl_dist_points * point_val)) if (sl_dist_points * point_val) > 0 else 0.01
                    lot = max(0.01, min(self.config.max_lot_size, round(calc_lot, 2)))

                    active_trade = BacktestTrade(
                        ticket=ticket_counter,
                        signal_type=signal.signal_type,
                        open_time=curr_bar['time'],
                        open_price=open_next,
                        lot=lot,
                        sl=signal.stop_loss,
                        tp=signal.take_profit,
                        pattern=signal.pattern_name
                    )
                    ticket_counter += 1
                    last_signal_bar = i

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Menghasilkan metrik statistik performa backtesting."""
        total_trades = len(self.trades)
        if total_trades == 0:
            print("[Backtest Hasil] Tidak ada trade yang dieksekusi.")
            return {"total_trades": 0}

        wins = [t for t in self.trades if t.profit > 0]
        losses = [t for t in self.trades if t.profit <= 0]

        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades) * 100.0

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

        report = {
            "initial_balance": self.initial_balance,
            "final_balance": round(self.balance, 2),
            "net_profit": round(net_profit, 2),
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "win_rate_percent": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "Inf",
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "max_drawdown_amount": round(max_dd, 2),
            "max_drawdown_percent": round(max_dd_pct, 2)
        }

        print("\n" + "=" * 55)
        print("  [LAPORAN PERFORMA BACKTEST TRIPLE EMA]")
        print("=" * 55)
        print(f" Modal Awal        : ${report['initial_balance']:,.2f}")
        print(f" Saldo Akhir       : ${report['final_balance']:,.2f}")
        print(f" Net Profit        : ${report['net_profit']:,.2f} ({((report['net_profit']/report['initial_balance'])*100):.2f}%)")
        print(f" Total Transaksi   : {report['total_trades']}")
        print(f" Menang / Kalah    : {report['winning_trades']} Win / {report['losing_trades']} Loss")
        print(f" Win Rate          : {report['win_rate_percent']}%")
        print(f" Profit Factor     : {report['profit_factor']}")
        print(f" Max Drawdown      : ${report['max_drawdown_amount']:,.2f} ({report['max_drawdown_percent']}%)")
        print("=" * 55 + "\n")

        return report

if __name__ == "__main__":
    # Test runner jika dipanggil langsung
    from mt5_client import MT5Client
    
    cfg = TradingConfig(symbol="XAUUSD", timeframe="M15")
    client = MT5Client()
    
    if client.initialize():
        print("[Backtester] Mengambil data historis dari MT5...")
        rates_df = client.get_rates("XAUUSD", "M15", count=2000)
        client.shutdown()
        
        if rates_df is not None:
            bt = TripleEmaBacktester(cfg, initial_balance=10000.0, point_size=0.01)
            bt.run(rates_df)
    else:
        print("[Backtester] MT5 terminal tidak aktif. Menggunakan data simulasi acak untuk validasi kode...")
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
