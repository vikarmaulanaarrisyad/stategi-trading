"""
Modul Analisis Support & Resistance (SNR) Dinamis
Mencakup:
1. Deteksi Major & Minor Support / Resistance berbasis Swing Pivot
2. Deteksi Role Reversal: RBS (Resistance Become Support) & SBR (Support Become Resistance)
3. Filter Obstacle: Memastikan tidak ada tembok S/R yang menghalangi jalan menuju target Take Profit
4. Konfluensi Pantulan S/R: Mengidentifikasi pertemuan zona EMA 8/21 dengan level S/R
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import numpy as np
import pandas as pd

@dataclass
class SnrLevel:
    level_type: str       # "MAJOR_RESISTANCE", "MAJOR_SUPPORT", "MINOR_RESISTANCE", "MINOR_SUPPORT", "RBS", "SBR"
    price: float          # Harga level S/R
    bar_index: int        # Index bar saat level terbentuk
    age_bars: int         # Usia bar sejak terbentuk
    tested_count: int     # Berapa kali harga menguji level ini

@dataclass
class SnrSnapshot:
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    nearest_rbs: Optional[float]
    nearest_sbr: Optional[float]
    has_support_bounce: bool
    has_resistance_bounce: bool
    bounce_info: str
    nearest_major_support: Optional[float] = None
    nearest_major_resistance: Optional[float] = None

class SupportResistanceAnalyzer:
    def __init__(self,
                 major_lookback: int = 20,
                 minor_lookback: int = 8,
                 zone_atr_factor: float = 0.3):
        self.major_lookback = max(10, major_lookback)
        self.minor_lookback = max(4, minor_lookback)
        self.zone_atr_factor = max(0.1, zone_atr_factor)

    def find_pivots(self, highs: np.ndarray, lows: np.ndarray, lookback: int, shift: int) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        """Mencari titik swing high dan swing low dalam rentang bar."""
        p_highs = []
        p_lows = []
        start = max(lookback, shift - 120)
        end = shift - 1

        for i in range(end, start, -1):
            # Cek Swing High
            left_highs = highs[max(0, i - lookback):i]
            right_highs = highs[i + 1:min(len(highs), i + lookback + 1)]
            if len(left_highs) > 0 and len(right_highs) > 0:
                if highs[i] >= np.max(left_highs) and highs[i] >= np.max(right_highs):
                    p_highs.append((i, float(highs[i])))

            # Cek Swing Low
            left_lows = lows[max(0, i - lookback):i]
            right_lows = lows[i + 1:min(len(lows), i + lookback + 1)]
            if len(left_lows) > 0 and len(right_lows) > 0:
                if lows[i] <= np.min(left_lows) and lows[i] <= np.min(right_lows):
                    p_lows.append((i, float(lows[i])))

        return p_highs, p_lows

    def analyze_snr(self, df: pd.DataFrame, shift: int = -1) -> SnrSnapshot:
        """
        Melakukan analisis lengkap S/R pada candle shift.
        Mengembalikan SnrSnapshot berisi level terdekat dan status konfluensi.
        """
        n = len(df)
        if shift < 0:
            shift = n + shift
        if shift < 25 or shift >= n:
            return SnrSnapshot(None, None, None, None, False, False, "Data tidak cukup", None, None)

        c0 = df.iloc[shift]
        current_close = c0['close']
        atr_val = c0.get('atr', (c0['high'] - c0['low']))
        zone_buffer = self.zone_atr_factor * atr_val

        highs = df['high'].values
        lows = df['low'].values
        closes = df['close'].values

        # 1. Cari Major & Minor Pivots
        major_highs, major_lows = self.find_pivots(highs, lows, self.major_lookback, shift)
        minor_highs, minor_lows = self.find_pivots(highs, lows, self.minor_lookback, shift)

        # 2. Ambil Support & Resistance Terdekat (Major dan Gabungan)
        major_res_list = [h[1] for h in major_highs if h[1] > (current_close + zone_buffer * 0.5)]
        major_sup_list = [l[1] for l in major_lows if l[1] < (current_close - zone_buffer * 0.5)]
        nearest_major_res = min(major_res_list) if major_res_list else None
        nearest_major_sup = max(major_sup_list) if major_sup_list else None

        all_res_list = [h[1] for h in (major_highs + minor_highs) if h[1] > (current_close + zone_buffer * 0.5)]
        all_sup_list = [l[1] for l in (major_lows + minor_lows) if l[1] < (current_close - zone_buffer * 0.5)]
        nearest_res = min(all_res_list) if all_res_list else None
        nearest_sup = max(all_sup_list) if all_sup_list else None

        # 3. Deteksi Role Reversal: RBS (Resistance Become Support)
        nearest_rbs = None
        for bar_idx, p_high in (major_highs + minor_highs):
            if p_high < current_close:
                after_closes = closes[bar_idx + 1:shift + 1]
                if len(after_closes) > 0 and np.max(after_closes) > p_high:
                    if nearest_rbs is None or p_high > nearest_rbs:
                        nearest_rbs = p_high

        # 4. Deteksi Role Reversal: SBR (Support Become Resistance)
        nearest_sbr = None
        for bar_idx, p_low in (major_lows + minor_lows):
            if p_low > current_close:
                after_closes = closes[bar_idx + 1:shift + 1]
                if len(after_closes) > 0 and np.min(after_closes) < p_low:
                    if nearest_sbr is None or p_low < nearest_sbr:
                        nearest_sbr = p_low

        # 5. Cek Konfluensi Pantulan (Bounce) pada candle pullback saat ini
        candle_low = c0['low']
        candle_high = c0['high']

        has_sup_bounce = False
        has_res_bounce = False
        bounce_info = "No SNR Bounce"

        # Pantulan Support atau RBS untuk BUY
        key_supports = [s for s in [nearest_sup, nearest_rbs] if s is not None]
        for sup in key_supports:
            if (candle_low <= (sup + zone_buffer)) and (candle_low >= (sup - zone_buffer * 1.5)):
                has_sup_bounce = True
                label = "RBS" if sup == nearest_rbs else "Major Support"
                bounce_info = f"Bounce at {label} ({sup:.2f})"
                break

        # Pantulan Resistance atau SBR untuk SELL
        key_resistances = [r for r in [nearest_res, nearest_sbr] if r is not None]
        for res in key_resistances:
            if (candle_high >= (res - zone_buffer)) and (candle_high <= (res + zone_buffer * 1.5)):
                has_res_bounce = True
                label = "SBR" if res == nearest_sbr else "Major Resistance"
                bounce_info = f"Bounce at {label} ({res:.2f})"
                break

        return SnrSnapshot(
            nearest_support=nearest_sup,
            nearest_resistance=nearest_res,
            nearest_rbs=nearest_rbs,
            nearest_sbr=nearest_sbr,
            has_support_bounce=has_sup_bounce,
            has_resistance_bounce=has_res_bounce,
            bounce_info=bounce_info,
            nearest_major_support=nearest_major_sup,
            nearest_major_resistance=nearest_major_res
        )

    def is_obstacle_blocking(self,
                             signal_type: str,
                             entry_price: float,
                             sl_dist_points: float,
                             point_size: float,
                             snapshot: SnrSnapshot,
                             min_clearance_rr: float = 1.0) -> Tuple[bool, str]:
        """
        Memeriksa apakah ada level S/R Mayor sejati yang menghalangi jalan menuju target keuntungan.
        Menggunakan level Major (bukan swing minor lokal) agar tidak mematikan kelanjutan tren.
        """
        required_clearance_dist = (sl_dist_points * point_size) * min_clearance_rr

        if signal_type == "BUY":
            res = snapshot.nearest_major_resistance
            if res is not None and res > entry_price:
                dist_to_res = res - entry_price
                if dist_to_res < required_clearance_dist:
                    pts_to_res = dist_to_res / point_size
                    return True, f"Terhalang Major Resistance di {res:.2f} (Hanya {pts_to_res:.0f} pts, butuh {required_clearance_dist/point_size:.0f} pts untuk 1:{min_clearance_rr}R)"

        elif signal_type == "SELL":
            sup = snapshot.nearest_major_support
            if sup is not None and sup < entry_price:
                dist_to_sup = entry_price - sup
                if dist_to_sup < required_clearance_dist:
                    pts_to_sup = dist_to_sup / point_size
                    return True, f"Terhalang Major Support di {sup:.2f} (Hanya {pts_to_sup:.0f} pts, butuh {required_clearance_dist/point_size:.0f} pts untuk 1:{min_clearance_rr}R)"

        return False, "Clear (Tidak ada hambatan S/R)"
