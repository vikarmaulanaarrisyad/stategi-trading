"""
Modul Manajemen Resiko & Proteksi Trade (Risk Manager)
Mencakup:
1. Kalkulasi Lot Dinamis berbasis persentase Equity
2. Circuit Breaker Batas Kerugian Harian
3. Auto Break-Even (BEP)
4. Trailing Stop Dinamis berbasis EMA 21 atau ATR
5. Filter Jam Trading & Proteksi Gap Akhir Pekan (Friday Auto-Close)
"""

import math
from datetime import datetime, time
from typing import Dict, Any, Optional, Tuple
from config import TradingConfig

class RiskManager:
    def __init__(self, config: TradingConfig):
        self.config = config
        self.last_calculated_day: int = -1
        self.daily_loss_count: int = 0
        self.daily_loss_amount: float = 0.0

    def calculate_lot_size(self,
                           equity: float = None,
                           sl_distance_points: float = 0.0,
                           point_size: float = 0.01,
                           tick_size: float = 0.01,
                           tick_value: float = 1.0,
                           min_lot: float = 0.01,
                           max_lot: float = 5.0,
                           lot_step: float = 0.01,
                           balance: float = None) -> float:
        """Menghitung lot size profesional berdasarkan resiko modal."""
        if equity is None and balance is not None:
            equity = balance
        elif equity is None:
            equity = 10000.0

        if self.config.lot_mode == "FIXED":
            return round(self.config.fixed_lot, 2)

        if sl_distance_points <= 0:
            return min_lot

        risk_money = equity * (self.config.risk_percent / 100.0)
        
        # Nilai uang per point per 1 lot
        point_val = (tick_value / tick_size) * point_size if tick_size > 0 else 1.0
        
        if point_val <= 0:
            return min_lot

        calculated_lot = risk_money / (sl_distance_points * point_val)
        
        # Batasi dengan parameter broker & konfigurasi EA
        effective_max = min(max_lot, self.config.max_lot_size)
        
        # Bulatkan ke kelipatan lot step
        if lot_step > 0:
            calculated_lot = math.floor(calculated_lot / lot_step) * lot_step
            
        calculated_lot = max(min_lot, min(effective_max, calculated_lot))
        
        # Menentukan desimal lot
        digits = 2
        if lot_step <= 0.001:
            digits = 3
        elif lot_step >= 0.1:
            digits = 1
            
        return round(calculated_lot, digits)

    def is_daily_circuit_breaker_triggered(self, equity: float) -> Tuple[bool, str]:
        """Cek apakah batas kerugian harian telah tercapai."""
        if not self.config.use_daily_loss_limit:
            return False, "Circuit breaker nonaktif"

        now = datetime.now()
        if now.day != self.last_calculated_day:
            self.daily_loss_count = 0
            self.daily_loss_amount = 0.0
            self.last_calculated_day = now.day

        if self.daily_loss_count >= self.config.max_daily_losses:
            msg = f"Batas kalah harian ({self.daily_loss_count}/{self.config.max_daily_losses} trade) tercapai. Trading dijeda hingga besok."
            return True, msg

        max_allowed_loss = equity * (self.config.max_daily_loss_percent / 100.0)
        if self.daily_loss_amount >= max_allowed_loss and max_allowed_loss > 0:
            msg = f"Batas nominal loss harian (${self.daily_loss_amount:.2f} / ${max_allowed_loss:.2f}) tercapai. Trading dijeda hingga besok."
            return True, msg

        return False, "Normal"

    def record_closed_trade(self, profit: float):
        """Mencatat hasil trade untuk evaluasi circuit breaker harian."""
        now = datetime.now()
        if now.day != self.last_calculated_day:
            self.daily_loss_count = 0
            self.daily_loss_amount = 0.0
            self.last_calculated_day = now.day

        if profit < -0.01:
            self.daily_loss_count += 1
            self.daily_loss_amount += abs(profit)

    def sync_daily_stats_from_deals(self, deals: list):
        """Sinkronisasi statistik loss harian dari deal tertutup MT5 secara real-time."""
        now = datetime.now()
        if now.day != self.last_calculated_day:
            self.daily_loss_count = 0
            self.daily_loss_amount = 0.0
            self.last_calculated_day = now.day

        loss_cnt = 0
        loss_amt = 0.0
        for d in deals:
            p = getattr(d, 'profit', 0.0)
            if p < -0.01:
                loss_cnt += 1
                loss_amt += abs(p)
        
        self.daily_loss_count = max(self.daily_loss_count, loss_cnt)
        self.daily_loss_amount = max(self.daily_loss_amount, loss_amt)

    def evaluate_partial_close(self,
                               pos_type: str,
                               open_price: float,
                               current_price: float,
                               initial_sl: float,
                               current_volume: float,
                               initial_volume: float,
                               volume_min: float = 0.01,
                               volume_step: float = 0.01) -> Tuple[bool, float]:
        """
        Mengevaluasi apakah posisi berhak melakukan Partial Take Profit (Scale Out).
        Mengembalikan (should_close_partial, volume_to_close).
        """
        if not getattr(self.config, 'use_partial_close', False):
            return False, 0.0

        # Jika volume saat ini sudah lebih kecil dari 95% initial volume, berarti sudah pernah partial close
        if current_volume < (initial_volume * 0.95):
            return False, 0.0

        initial_sl_dist = abs(open_price - initial_sl)
        if initial_sl_dist <= 0:
            return False, 0.0

        profit_dist = (current_price - open_price) if pos_type == "BUY" else (open_price - current_price)
        current_r = profit_dist / initial_sl_dist

        target_rr = getattr(self.config, 'partial_close_rr', 1.0)
        if current_r >= target_rr:
            pct = getattr(self.config, 'partial_close_percent', 50.0) / 100.0
            vol_to_close = initial_volume * pct
            if volume_step > 0:
                vol_to_close = math.floor(vol_to_close / volume_step) * volume_step
            vol_to_close = round(vol_to_close, 2)

            remaining_vol = round(current_volume - vol_to_close, 2)
            if vol_to_close >= volume_min and remaining_vol >= volume_min:
                return True, vol_to_close

        return False, 0.0

    def is_trading_time_allowed(self, current_dt: Optional[datetime] = None) -> bool:
        """Cek apakah jam saat ini diizinkan untuk trading."""
        if not self.config.use_time_filter:
            return True
            
        dt = current_dt or datetime.now()
        if dt.hour < self.config.start_hour or dt.hour >= self.config.end_hour:
            return False
        return True

    def is_friday_trading_restricted(self, current_dt: Optional[datetime] = None) -> bool:
        """Cek apakah masuk waktu larangan order baru di hari Jumat."""
        if not self.config.use_friday_close:
            return False
            
        dt = current_dt or datetime.now()
        if dt.weekday() == 4:  # 4 = Hari Jumat
            # Jika sudah jam auto-close
            if (dt.hour > self.config.friday_close_hour or 
               (dt.hour == self.config.friday_close_hour and dt.minute >= self.config.friday_close_minute)):
                return True
                
            # Jika memblokir entri baru sejak sore
            if self.config.block_friday_new_trades and dt.hour >= self.config.friday_stop_trade_hour:
                return True
                
        return False

    def is_friday_auto_close_time(self, current_dt: Optional[datetime] = None) -> bool:
        """Cek apakah waktu tutup semua posisi Jumat malam tiba."""
        if not self.config.use_friday_close:
            return False
            
        dt = current_dt or datetime.now()
        if dt.weekday() == 4:  # 4 = Hari Jumat
            if (dt.hour > self.config.friday_close_hour or 
               (dt.hour == self.config.friday_close_hour and dt.minute >= self.config.friday_close_minute)):
                return True
        return False

    def evaluate_break_even(self,
                            pos_type: str,
                            open_price: float,
                            current_sl: float,
                            current_price: float,
                            point_size: float,
                            min_broker_dist: float) -> Optional[float]:
        """
        Mengevaluasi apakah SL harus digeser ke Break-Even (BEP).
        Mengembalikan new_sl jika perlu dimodifikasi, atau None jika tidak.
        """
        if not self.config.use_break_even:
            return None

        initial_sl_dist = abs(open_price - current_sl)
        if initial_sl_dist <= 0:
            initial_sl_dist = 200 * point_size

        profit_dist = (current_price - open_price) if pos_type == "BUY" else (open_price - current_price)
        current_r = profit_dist / initial_sl_dist if initial_sl_dist > 0 else 0.0

        if current_r >= self.config.be_trigger_rr:
            if pos_type == "BUY" and current_sl < open_price:
                new_sl = open_price + (self.config.be_lock_profit_points * point_size)
                if (current_price - new_sl) >= min_broker_dist:
                    return new_sl
            elif pos_type == "SELL" and (current_sl > open_price or current_sl == 0.0):
                new_sl = open_price - (self.config.be_lock_profit_points * point_size)
                if (new_sl - current_price) >= min_broker_dist:
                    return new_sl

        return None

    def evaluate_trailing_stop(self,
                               pos_type: str,
                               open_price: float,
                               current_sl: float,
                               current_price: float,
                               ema21_val: float,
                               atr_val: float,
                               point_size: float,
                               min_broker_dist: float) -> Optional[float]:
        """
        Mengevaluasi Trailing Stop mengikuti garis EMA 21 atau ATR.
        Mengembalikan new_sl jika perlu dimodifikasi, atau None jika tidak.
        """
        if not self.config.use_trailing_stop:
            return None

        initial_sl_dist = abs(open_price - current_sl)
        if initial_sl_dist <= 0:
            initial_sl_dist = 200 * point_size

        profit_dist = (current_price - open_price) if pos_type == "BUY" else (open_price - current_price)
        current_r = profit_dist / initial_sl_dist if initial_sl_dist > 0 else 0.0

        if current_r < self.config.trailing_start_rr:
            return None

        if pos_type == "BUY":
            target_sl = (ema21_val - 20 * point_size) if self.config.trailing_by_ema21 else (current_price - self.config.trailing_atr_mult * atr_val)
            # Validasi: SL harus mengunci profit (di atas open_price) dan lebih tinggi dari SL saat ini
            if (target_sl > open_price and 
                target_sl > current_sl + (15 * point_size) and 
                (current_price - target_sl) >= min_broker_dist):
                return target_sl
        else:  # SELL
            target_sl = (ema21_val + 20 * point_size) if self.config.trailing_by_ema21 else (current_price + self.config.trailing_atr_mult * atr_val)
            if (target_sl < open_price and 
                (current_sl == 0.0 or target_sl < current_sl - (15 * point_size)) and 
                (target_sl - current_price) >= min_broker_dist):
                return target_sl

        return None
