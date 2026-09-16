"""
Modul Evaluasi Sinyal Strategi Triple EMA Pullback
Menghubungkan Indikator, Price Action Candlestick, dan Filter Struktur Pasar.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import pandas as pd

from config import TradingConfig
from candle_patterns import (
    CandlePattern,
    detect_bullish_pattern,
    detect_bearish_pattern,
    get_pattern_name
)
from market_structure import (
    MarketStructureAnalyzer,
    FilterResult,
    filter_result_to_string
)
from support_resistance import (
    SupportResistanceAnalyzer,
    SnrSnapshot
)
from smc_analyzer import (
    SmcAnalyzer,
    SmcSnapshot
)

@dataclass
class TradeSignal:
    signal_type: str                  # "BUY" atau "SELL"
    pattern: CandlePattern            # Pola candlestick konfirmasi
    pattern_name: str                 # Nama deskriptif pola
    entry_price: float                # Estimasi harga masuk
    stop_loss: float                  # Harga Stop Loss terhitung
    take_profit: float                # Harga Take Profit terhitung
    sl_distance_points: float         # Jarak SL dalam points
    reason: str                       # Alasan / info setup
    nearest_support: Optional[float] = None     # Level Support terdekat
    nearest_resistance: Optional[float] = None  # Level Resistance terdekat
    snr_bounce_info: str = ""                   # Info konfluensi pantulan S/R (RBS / SBR)
    smc_zone: str = ""                          # Zona valuasi SMC ("DISCOUNT", "PREMIUM", "OTE")
    smc_sweep_info: str = ""                    # Info SSL/BSL sweep jika terdeteksi

class TripleEmaStrategy:
    def __init__(self, config: TradingConfig):
        self.config = config
        self.structure_analyzer = MarketStructureAnalyzer(
            fractal_lookback=config.fractal_lookback,
            chop_bars=config.chop_bars,
            max_ema_crosses=config.max_ema_crosses,
            whipsaw_bars=config.whipsaw_bars,
            max_whipsaw_crosses=config.max_whipsaw_crosses,
            max_atr_multiplier=config.max_atr_multiplier
        )
        self.snr_analyzer = SupportResistanceAnalyzer(
            major_lookback=getattr(config, 'snr_major_lookback', 20),
            minor_lookback=getattr(config, 'snr_minor_lookback', 8)
        )
        self.smc_analyzer = SmcAnalyzer(
            dealing_range_bars=getattr(config, 'smc_dealing_range_bars', 35),
            pivot_lookback=getattr(config, 'smc_pivot_lookback', 5),
            sweep_lookback_bars=getattr(config, 'smc_sweep_lookback_bars', 15)
        )

    def calculate_sl_tp(self, 
                        signal_type: str, 
                        entry_price: float, 
                        df: pd.DataFrame, 
                        point_size: float,
                        shift: int = -1) -> Tuple[float, float, float]:
        """
        Menghitung harga Stop Loss dan Take Profit berdasarkan mode SL.
        Mengembalikan (sl_price, tp_price, sl_distance_points).
        """
        n = len(df)
        if shift < 0:
            shift = n + shift
            
        row = df.iloc[shift]
        atr_val = row['atr']
        
        lookback = max(2, min(shift, getattr(self.config, 'swing_lookback_bars', 6)))
        if signal_type == "BUY":
            if self.config.sl_mode == "SWING_CANDLE":
                # Swing low dari lookback bar terakhir
                recent_lows = [df.iloc[shift - i]['low'] for i in range(lookback)]
                lowest_low = min(recent_lows)
                sl_price = lowest_low - (self.config.sl_buffer_points * point_size)
            elif self.config.sl_mode == "ATR_BASED":
                sl_price = entry_price - (self.config.sl_atr_multiplier * atr_val)
            else:  # FIXED_POINTS
                sl_price = entry_price - (self.config.sl_fixed_points * point_size)
                
            sl_dist_pts = (entry_price - sl_price) / point_size
            if sl_dist_pts < self.config.min_sl_points:
                sl_price = entry_price - (self.config.min_sl_points * point_size)
                sl_dist_pts = self.config.min_sl_points
                
            tp_price = entry_price + ((entry_price - sl_price) * self.config.risk_reward_ratio)
            
        else:  # SELL
            if self.config.sl_mode == "SWING_CANDLE":
                # Swing high dari lookback bar terakhir
                recent_highs = [df.iloc[shift - i]['high'] for i in range(lookback)]
                highest_high = max(recent_highs)
                sl_price = highest_high + (self.config.sl_buffer_points * point_size)
            elif self.config.sl_mode == "ATR_BASED":
                sl_price = entry_price + (self.config.sl_atr_multiplier * atr_val)
            else:  # FIXED_POINTS
                sl_price = entry_price + (self.config.sl_fixed_points * point_size)
                
            sl_dist_pts = (sl_price - entry_price) / point_size
            if sl_dist_pts < self.config.min_sl_points:
                sl_price = entry_price + (self.config.min_sl_points * point_size)
                sl_dist_pts = self.config.min_sl_points
                
            tp_price = entry_price - ((sl_price - entry_price) * self.config.risk_reward_ratio)

        return sl_price, tp_price, sl_dist_pts

    def evaluate_signal(self, 
                        df: pd.DataFrame, 
                        current_ask: Optional[float] = None, 
                        current_bid: Optional[float] = None, 
                        point_size: float = 0.01,
                        htf_bullish: bool = True,
                        htf_bearish: bool = True,
                        shift: int = -1) -> Optional[TradeSignal]:
        """
        Mengevaluasi bar closed (shift) untuk sinyal BUY atau SELL.
        """
        n = len(df)
        if shift < 0:
            shift = n + shift
        if shift < 3 or shift >= n:
            return None

        c0 = df.iloc[shift]
        c_prev = df.iloc[shift - 1]

        if current_ask is None:
            current_ask = float(c0['close'])
        if current_bid is None:
            current_bid = float(c0['close'])

        # Sinyal BUY
        bull_pattern = detect_bullish_pattern(df, shift)
        if bull_pattern != CandlePattern.NONE:
            # 1. Syarat Tren Lengkap Triple EMA: EMA 8 > EMA 21 > EMA 125 & Price di atas EMA 125
            trend_bull = (
                (c0['ema8'] > c0['ema21']) and 
                (c0['ema21'] > c0['ema125']) and 
                (c0['close'] > c0['ema125']) and 
                (c0['low'] > c0['ema125'])
            )
            if not trend_bull:
                return None
                
            # 2. MTF Filter
            if self.config.use_mtf_filter and not htf_bullish:
                return None
                
            # 3. Strong close di atas EMA 8
            if self.config.require_strong_close and not (c0['close'] > c0['ema8'] and c0['close'] > c0['open']):
                return None
                
            # 4. Slope EMA 8 naik
            if self.config.require_ema_slope and not (c0['ema8'] > c_prev['ema8']):
                return None
                
            # 5. ADX Filter
            if self.config.use_adx_filter and (c0['adx'] < self.config.min_adx_level):
                return None
                
            # 6. Filter False Signal & Struktur
            res = self.structure_analyzer.validate_buy_filters(
                df, 
                require_hh_hl=self.config.use_structure_filter, 
                shift=shift
            )
            if res != FilterResult.PASS:
                return None

            # Sinyal BUY Valid: Hitung SL/TP
            entry = current_ask
            sl, tp, dist = self.calculate_sl_tp("BUY", entry, df, point_size, shift)
            
            # Proteksi Max SL: Batalkan jika jarak SL melebihi toleransi maksimal (R:R tidak efisien)
            max_sl = getattr(self.config, 'max_sl_points', 2500)
            if dist > max_sl:
                return None

            # 7. Evaluasi Support & Resistance (SNR)
            snr_snap = self.snr_analyzer.analyze_snr(df, shift)
            if getattr(self.config, 'use_snr_filter', True):
                # Filter Obstacle S/R: Mencegah order jika terhalang Major Resistance sebelum target 1:1 R
                if getattr(self.config, 'snr_obstacle_filter', True):
                    blocked, obs_msg = self.snr_analyzer.is_obstacle_blocking(
                        signal_type="BUY",
                        entry_price=entry,
                        sl_dist_points=dist,
                        point_size=point_size,
                        snapshot=snr_snap,
                        min_clearance_rr=getattr(self.config, 'snr_min_clearance_rr', 1.0)
                    )
                    if blocked:
                        return None
                        
                # Konfluensi Ketat: Wajib pantul di Support / RBS jika diaktifkan
                if getattr(self.config, 'snr_require_bounce_confluence', False) and not snr_snap.has_support_bounce:
                    return None

            # 8. Evaluasi Smart Money Concepts (SMC): Valuasi Discount & Liquidity Sweep
            smc_snap = self.smc_analyzer.analyze_smc(df, shift)
            if getattr(self.config, 'use_smc_filter', True):
                # Valuasi Discount Zone (BUY hanya di area murah < 50%)
                if getattr(self.config, 'use_smc_discount_premium', True) and not smc_snap.is_discount:
                    return None
                # Mode Ketat OTE Golden Pocket (0.618 - 0.786)
                if getattr(self.config, 'use_smc_ote_strict', False) and not smc_snap.is_ote_buy:
                    return None
                # Wajib Liquidity Sweep (SSL Sweep sebelum BUY)
                if getattr(self.config, 'use_smc_liquidity_sweep', True) and not smc_snap.has_ssl_sweep:
                    return None

            p_name = get_pattern_name(bull_pattern)
            reason_str = f"Valid Bullish Setup: {p_name}"
            if snr_snap.has_support_bounce:
                reason_str += f" | {snr_snap.bounce_info}"
            if getattr(self.config, 'use_smc_filter', True):
                reason_str += f" | {smc_snap.summary_info}"

            return TradeSignal(
                signal_type="BUY",
                pattern=bull_pattern,
                pattern_name=p_name,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                sl_distance_points=dist,
                reason=reason_str,
                nearest_support=snr_snap.nearest_support,
                nearest_resistance=snr_snap.nearest_resistance,
                snr_bounce_info=snr_snap.bounce_info,
                smc_zone=smc_snap.zone_label,
                smc_sweep_info=smc_snap.ssl_sweep_info
            )

        # Sinyal SELL
        bear_pattern = detect_bearish_pattern(df, shift)
        if bear_pattern != CandlePattern.NONE:
            # 1. Syarat Tren Lengkap Triple EMA: EMA 8 < EMA 21 < EMA 125 & Price di bawah EMA 125
            trend_bear = (
                (c0['ema8'] < c0['ema21']) and 
                (c0['ema21'] < c0['ema125']) and 
                (c0['close'] < c0['ema125']) and 
                (c0['high'] < c0['ema125'])
            )
            if not trend_bear:
                return None
                
            # 2. MTF Filter
            if self.config.use_mtf_filter and not htf_bearish:
                return None
                
            # 3. Strong close di bawah EMA 8
            if self.config.require_strong_close and not (c0['close'] < c0['ema8'] and c0['close'] < c0['open']):
                return None
                
            # 4. Slope EMA 8 turun
            if self.config.require_ema_slope and not (c0['ema8'] < c_prev['ema8']):
                return None
                
            # 5. ADX Filter
            if self.config.use_adx_filter and (c0['adx'] < self.config.min_adx_level):
                return None
                
            # 6. Filter False Signal & Struktur
            res = self.structure_analyzer.validate_sell_filters(
                df, 
                require_lh_ll=self.config.use_structure_filter, 
                shift=shift
            )
            if res != FilterResult.PASS:
                return None

            # Sinyal SELL Valid: Hitung SL/TP
            entry = current_bid
            sl, tp, dist = self.calculate_sl_tp("SELL", entry, df, point_size, shift)

            # Proteksi Max SL
            max_sl = getattr(self.config, 'max_sl_points', 2500)
            if dist > max_sl:
                return None

            # 7. Evaluasi Support & Resistance (SNR)
            snr_snap = self.snr_analyzer.analyze_snr(df, shift)
            if getattr(self.config, 'use_snr_filter', True):
                # Filter Obstacle S/R: Mencegah order jika terhalang Major Support sebelum target 1:1 R
                if getattr(self.config, 'snr_obstacle_filter', True):
                    blocked, obs_msg = self.snr_analyzer.is_obstacle_blocking(
                        signal_type="SELL",
                        entry_price=entry,
                        sl_dist_points=dist,
                        point_size=point_size,
                        snapshot=snr_snap,
                        min_clearance_rr=getattr(self.config, 'snr_min_clearance_rr', 1.0)
                    )
                    if blocked:
                        return None
                        
                # Konfluensi Ketat: Wajib pantul di Resistance / SBR jika diaktifkan
                if getattr(self.config, 'snr_require_bounce_confluence', False) and not snr_snap.has_resistance_bounce:
                    return None

            # 8. Evaluasi Smart Money Concepts (SMC): Valuasi Premium & Liquidity Sweep
            smc_snap = self.smc_analyzer.analyze_smc(df, shift)
            if getattr(self.config, 'use_smc_filter', True):
                # Valuasi Premium Zone (SELL hanya di area mahal > 50%)
                if getattr(self.config, 'use_smc_discount_premium', True) and not smc_snap.is_premium:
                    return None
                # Mode Ketat OTE Golden Pocket (0.618 - 0.786)
                if getattr(self.config, 'use_smc_ote_strict', False) and not smc_snap.is_ote_sell:
                    return None
                # Wajib Liquidity Sweep (BSL Sweep sebelum SELL)
                if getattr(self.config, 'use_smc_liquidity_sweep', True) and not smc_snap.has_bsl_sweep:
                    return None

            p_name = get_pattern_name(bear_pattern)
            reason_str = f"Valid Bearish Setup: {p_name}"
            if snr_snap.has_resistance_bounce:
                reason_str += f" | {snr_snap.bounce_info}"
            if getattr(self.config, 'use_smc_filter', True):
                reason_str += f" | {smc_snap.summary_info}"

            return TradeSignal(
                signal_type="SELL",
                pattern=bear_pattern,
                pattern_name=p_name,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                sl_distance_points=dist,
                reason=reason_str,
                nearest_support=snr_snap.nearest_support,
                nearest_resistance=snr_snap.nearest_resistance,
                snr_bounce_info=snr_snap.bounce_info,
                smc_zone=smc_snap.zone_label,
                smc_sweep_info=smc_snap.bsl_sweep_info
            )

        return None
