"""
Modul Analisis Smart Money Concepts (SMC) & Liquidity
Mencakup:
1. Deteksi Dealing Range (Highest High & Lowest Low)
2. Valuasi Zona Discount vs. Premium & Fibonacci OTE (0.618 - 0.786 Golden Pocket)
3. Deteksi Liquidity Sweep (BSL / SSL Stop Run & False Breakout Rejection)
4. Validasi Konfluensi Institusional untuk Sinyal BUY & SELL
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class LiquidityLevel:
    level_type: str       # "BSL" (Buy-Side Liquidity) atau "SSL" (Sell-Side Liquidity)
    price: float          # Titik harga swing
    bar_index: int        # Index bar saat level terbentuk


@dataclass
class SweepEvent:
    sweep_type: str       # "SSL_SWEEP" (Bullish Liquidity Grab) atau "BSL_SWEEP" (Bearish Liquidity Grab)
    swept_level: float    # Harga likuiditas yang disapu
    sweep_bar: int        # Index bar saat sweep terjadi
    age_bars: int         # Berapa bar yang lalu sweep terjadi
    wick_penetration: float # Berapa poin/jarak ekor lilin menembus level


@dataclass
class SmcSnapshot:
    # --- Dealing Range & Valuasi ---
    range_high: float
    range_low: float
    range_eq: float                    # Level Equilibrium (50%)
    price_percent_in_range: float      # Posisi harga dalam range (0% = di range_low, 100% = di range_high)
    is_discount: bool                  # True jika harga < Equilibrium (area murah / valid BUY)
    is_premium: bool                   # True jika harga > Equilibrium (area mahal / valid SELL)
    is_ote_buy: bool                   # True jika harga di Golden Pocket OTE Buy (61.8% - 78.6% retracement)
    is_ote_sell: bool                  # True jika harga di Golden Pocket OTE Sell (61.8% - 78.6% retracement)
    zone_label: str                    # "DISCOUNT (OTE)", "DISCOUNT", "PREMIUM (OTE)", "PREMIUM", atau "EQUILIBRIUM"
    
    # --- Liquidity Sweeps ---
    has_ssl_sweep: bool                # True jika terjadi SSL Sweep terbaru (menyapu Stop Loss seller / buyer fuel)
    ssl_sweep_info: str                # Detail informasi SSL sweep
    has_bsl_sweep: bool                # True jika terjadi BSL Sweep terbaru (menyapu Stop Loss buyer / seller fuel)
    bsl_sweep_info: str                # Detail informasi BSL sweep
    
    # --- Ringkasan & Konfluensi ---
    summary_info: str


class SmcAnalyzer:
    """
    Penganalisa Prinsip Smart Money Concepts (SMC) untuk meningkatkan winrate.
    """
    def __init__(self,
                 dealing_range_bars: int = 35,
                 pivot_lookback: int = 5,
                 sweep_lookback_bars: int = 15):
        self.dealing_range_bars = max(15, dealing_range_bars)
        self.pivot_lookback = max(2, pivot_lookback)
        self.sweep_lookback_bars = max(3, sweep_lookback_bars)

    def find_liquidity_pools(self, highs: np.ndarray, lows: np.ndarray, start_idx: int, end_idx: int) -> Tuple[List[LiquidityLevel], List[LiquidityLevel]]:
        """
        Mencari pool likuiditas swing high (BSL) dan swing low (SSL) berbasis pivot.
        """
        bsl_levels: List[LiquidityLevel] = []
        ssl_levels: List[LiquidityLevel] = []
        k = self.pivot_lookback

        for i in range(start_idx, end_idx):
            if i < k or (i + k) >= len(highs):
                continue

            left_highs = highs[i - k:i]
            right_highs = highs[i + 1:i + k + 1]
            if len(left_highs) > 0 and len(right_highs) > 0:
                if highs[i] >= np.max(left_highs) and highs[i] >= np.max(right_highs):
                    bsl_levels.append(LiquidityLevel("BSL", float(highs[i]), i))

            left_lows = lows[i - k:i]
            right_lows = lows[i + 1:i + k + 1]
            if len(left_lows) > 0 and len(right_lows) > 0:
                if lows[i] <= np.min(left_lows) and lows[i] <= np.min(right_lows):
                    ssl_levels.append(LiquidityLevel("SSL", float(lows[i]), i))

        return bsl_levels, ssl_levels

    def detect_liquidity_sweeps(self,
                                df: pd.DataFrame,
                                shift: int,
                                bsl_pools: List[LiquidityLevel],
                                ssl_pools: List[LiquidityLevel]) -> Tuple[Optional[SweepEvent], Optional[SweepEvent]]:
        """
        Mendeteksi apakah dalam N bar terakhir sebelum/pada shift terjadi sweep likuiditas:
        - SSL Sweep: Low candle menembus di bawah SSL, namun Close tetap di atas SSL (Rejection / False Breakdown).
        - BSL Sweep: High candle menembus di atas BSL, namun Close tetap di bawah BSL (Rejection / False Breakout).
        """
        recent_ssl_sweep: Optional[SweepEvent] = None
        recent_bsl_sweep: Optional[SweepEvent] = None

        search_start = max(0, shift - self.sweep_lookback_bars + 1)
        search_end = shift + 1  # Termasuk candle shift (candle sinyal saat ini)

        # 1. Cek SSL Sweep (Bullish Liquidity Grab)
        for bar_idx in range(search_end - 1, search_start - 1, -1):
            row = df.iloc[bar_idx]
            b_low = float(row['low'])
            b_close = float(row['close'])
            
            for pool in ssl_pools:
                # Level pool harus terbentuk SEBELUM bar sweep
                if pool.bar_index < bar_idx:
                    # Low menembus pool, namun close ditutup kembali di atas level pool
                    if b_low < pool.price and b_close >= pool.price:
                        age = shift - bar_idx
                        penetration = pool.price - b_low
                        # Ambil sweep terdekat
                        if recent_ssl_sweep is None or age < recent_ssl_sweep.age_bars:
                            recent_ssl_sweep = SweepEvent(
                                sweep_type="SSL_SWEEP",
                                swept_level=pool.price,
                                sweep_bar=bar_idx,
                                age_bars=age,
                                wick_penetration=penetration
                            )

        # 2. Cek BSL Sweep (Bearish Liquidity Grab)
        for bar_idx in range(search_end - 1, search_start - 1, -1):
            row = df.iloc[bar_idx]
            b_high = float(row['high'])
            b_close = float(row['close'])

            for pool in bsl_pools:
                # Level pool harus terbentuk SEBELUM bar sweep
                if pool.bar_index < bar_idx:
                    # High melompat di atas pool, namun close ditutup kembali di bawah level pool
                    if b_high > pool.price and b_close <= pool.price:
                        age = shift - bar_idx
                        penetration = b_high - pool.price
                        # Ambil sweep terdekat
                        if recent_bsl_sweep is None or age < recent_bsl_sweep.age_bars:
                            recent_bsl_sweep = SweepEvent(
                                sweep_type="BSL_SWEEP",
                                swept_level=pool.price,
                                sweep_bar=bar_idx,
                                age_bars=age,
                                wick_penetration=penetration
                            )

        return recent_ssl_sweep, recent_bsl_sweep

    def analyze_smc(self, df: pd.DataFrame, shift: int = -1) -> SmcSnapshot:
        """
        Melakukan evaluasi menyeluruh SMC: Dealing Range, Valuasi Discount/Premium, OTE, dan Sweep.
        """
        n = len(df)
        if shift < 0:
            shift = n + shift

        current_close = float(df.iloc[shift]['close'])

        # 1. Tentukan Dealing Range
        range_start = max(0, shift - self.dealing_range_bars)
        sub_highs = df.iloc[range_start:shift + 1]['high'].to_numpy(dtype=float)
        sub_lows = df.iloc[range_start:shift + 1]['low'].to_numpy(dtype=float)

        range_high = float(np.max(sub_highs))
        range_low = float(np.min(sub_lows))
        range_size = range_high - range_low

        if range_size > 1e-6:
            range_eq = range_low + (0.5 * range_size)
            pct_in_range = ((current_close - range_low) / range_size) * 100.0
        else:
            range_eq = current_close
            pct_in_range = 50.0

        # 2. Valuasi Zona & OTE Golden Pocket
        # Discount (< 50% dealing range) & Premium (> 50% dealing range)
        is_discount = current_close < range_eq
        is_premium = current_close > range_eq

        # OTE Golden Pocket (0.618 - 0.786 Fibonacci Retracement)
        # Untuk BUY: Retracement dari High ke Low -> 61.8% s/d 78.6% dari puncak (berarti 21.4% s/d 38.2% dari dasar)
        is_ote_buy = (21.4 <= pct_in_range <= 38.2)
        # Untuk SELL: Retracement dari Low ke High -> 61.8% s/d 78.6% dari dasar
        is_ote_sell = (61.8 <= pct_in_range <= 78.6)

        if is_ote_buy:
            zone_label = "DISCOUNT (OTE Golden Zone)"
        elif is_discount:
            zone_label = "DISCOUNT ZONE"
        elif is_ote_sell:
            zone_label = "PREMIUM (OTE Golden Zone)"
        elif is_premium:
            zone_label = "PREMIUM ZONE"
        else:
            zone_label = "EQUILIBRIUM (50%)"

        # 3. Analisis Liquidity Pools & Sweeps
        all_highs = df['high'].to_numpy(dtype=float)
        all_lows = df['low'].to_numpy(dtype=float)

        pool_scan_start = max(0, shift - (self.sweep_lookback_bars + self.dealing_range_bars))
        bsl_pools, ssl_pools = self.find_liquidity_pools(all_highs, all_lows, pool_scan_start, shift)

        ssl_sweep, bsl_sweep = self.detect_liquidity_sweeps(df, shift, bsl_pools, ssl_pools)

        has_ssl = ssl_sweep is not None
        ssl_info = ""
        if ssl_sweep:
            ssl_info = f"SSL Sweep @ {ssl_sweep.swept_level:.2f} ({ssl_sweep.age_bars}b ago)"

        has_bsl = bsl_sweep is not None
        bsl_info = ""
        if bsl_sweep:
            bsl_info = f"BSL Sweep @ {bsl_sweep.swept_level:.2f} ({bsl_sweep.age_bars}b ago)"

        # 4. Ringkasan
        summary_parts = [f"SMC: {zone_label} ({pct_in_range:.1f}%)"]
        if has_ssl:
            summary_parts.append(ssl_info)
        if has_bsl:
            summary_parts.append(bsl_info)

        summary_str = " | ".join(summary_parts)

        return SmcSnapshot(
            range_high=range_high,
            range_low=range_low,
            range_eq=range_eq,
            price_percent_in_range=pct_in_range,
            is_discount=is_discount,
            is_premium=is_premium,
            is_ote_buy=is_ote_buy,
            is_ote_sell=is_ote_sell,
            zone_label=zone_label,
            has_ssl_sweep=has_ssl,
            ssl_sweep_info=ssl_info,
            has_bsl_sweep=has_bsl,
            bsl_sweep_info=bsl_info,
            summary_info=summary_str
        )
