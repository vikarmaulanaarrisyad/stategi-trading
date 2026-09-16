"""
Modul Analisis Struktur Pasar & Filter False Signal
Mengonversi logika MarketStructure.mqh ke Python murni.
Mencakup:
1. Validasi Struktur Pasar (Higher High & Higher Low vs Lower High & Lower Low)
2. Anti-Chop Filter (EMA 8 & 21 sering bersilangan)
3. Anti-Whipsaw Filter (Harga menembus EMA 125 berulang kali)
4. Anti-Overextended Filter (Harga melompat terlalu jauh dari EMA 8)
"""

from enum import Enum
import pandas as pd
import numpy as np

class MarketStructure(Enum):
    UNKNOWN = 0
    BULLISH_HH_HL = 1  # Higher Highs & Higher Lows (Uptrend Valid)
    BEARISH_LH_LL = 2  # Lower Highs & Lower Lows (Downtrend Valid)
    SIDEWAYS = 3       # Sideways / Rentang range tidak beraturan

class FilterResult(Enum):
    PASS = 0
    FAIL_CHOP_EMA8_21 = 1   # EMA 8 & 21 bolak-balik silang (Chop/Sideways)
    FAIL_WHIPSAW_125 = 2    # Harga bolak-balik menembus EMA 125
    FAIL_OVEREXTENDED = 3   # Candle terlalu jauh dari EMA 8 (> 2.0x ATR)
    FAIL_STRUCTURE = 4      # Struktur market bukan HH-HL (Buy) atau LH-LL (Sell)

def get_market_structure_name(structure: MarketStructure) -> str:
    names = {
        MarketStructure.BULLISH_HH_HL: "Bullish (Higher High & Higher Low)",
        MarketStructure.BEARISH_LH_LL: "Bearish (Lower High & Lower Low)",
        MarketStructure.SIDEWAYS: "Sideways / Range-bound",
        MarketStructure.UNKNOWN: "Unclear / In Transition"
    }
    return names.get(structure, "Unknown")

def filter_result_to_string(res: FilterResult) -> str:
    names = {
        FilterResult.PASS: "Valid (Semua Filter Lolos)",
        FilterResult.FAIL_CHOP_EMA8_21: "Filter Gagal: Chop Sideways (EMA 8-21 Cross)",
        FilterResult.FAIL_WHIPSAW_125: "Filter Gagal: Whipsaw EMA 125",
        FilterResult.FAIL_OVEREXTENDED: "Filter Gagal: Overextended Candle (> 2.0x ATR)",
        FilterResult.FAIL_STRUCTURE: "Filter Gagal: Struktur bukan HH/HL atau LH/LL"
    }
    return names.get(res, "Unknown")

class MarketStructureAnalyzer:
    def __init__(self,
                 fractal_lookback: int = 50,
                 chop_bars: int = 15,
                 max_ema_crosses: int = 2,
                 whipsaw_bars: int = 20,
                 max_whipsaw_crosses: int = 2,
                 max_atr_multiplier: float = 2.0):
        self.fractal_lookback = max(20, fractal_lookback)
        self.chop_bars = max(5, chop_bars)
        self.max_ema_crosses = max(1, max_ema_crosses)
        self.whipsaw_bars = max(10, whipsaw_bars)
        self.max_whipsaw_crosses = max(1, max_whipsaw_crosses)
        self.max_atr_multiplier = max_atr_multiplier if max_atr_multiplier > 0.5 else 2.0

    def analyze_structure(self, df: pd.DataFrame, shift: int = -1) -> MarketStructure:
        """
        Analisis swing fractal HH/HL atau LH/LL.
        shift = -1 berarti candle closed terakhir (idx len-1).
        """
        n = len(df)
        if shift < 0:
            shift = n + shift
        if shift < 15:
            return MarketStructure.UNKNOWN

        highs = df['high'].values
        lows = df['low'].values

        swing_highs = []
        swing_lows = []

        start_idx = shift - 2
        min_search = max(2, shift - self.fractal_lookback)

        # 1. Scan Primer: 5-bar Fractal (2 bar kiri, 2 bar kanan)
        for i in range(start_idx, min_search, -1):
            # Swing High
            if (highs[i] > highs[i - 1] and highs[i] > highs[i - 2] and
                highs[i] > highs[i + 1] and highs[i] > highs[i + 2]):
                swing_highs.append(highs[i])
                if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                    break
            # Swing Low
            if (lows[i] < lows[i - 1] and lows[i] < lows[i - 2] and
                lows[i] < lows[i + 1] and lows[i] < lows[i + 2]):
                swing_lows.append(lows[i])
                if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                    break

        # 2. Jika belum cukup, perluas lookback 5-bar fractal hingga 100 bar
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            extended_min = max(2, shift - min(100, self.fractal_lookback * 2))
            for i in range(min_search, extended_min, -1):
                if len(swing_highs) < 2:
                    if (highs[i] > highs[i - 1] and highs[i] > highs[i - 2] and
                        highs[i] > highs[i + 1] and highs[i] > highs[i + 2]):
                        swing_highs.append(highs[i])
                if len(swing_lows) < 2:
                    if (lows[i] < lows[i - 1] and lows[i] < lows[i - 2] and
                        lows[i] < lows[i + 1] and lows[i] < lows[i + 2]):
                        swing_lows.append(lows[i])
                if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                    break

        # 3. Scan Sekunder (Fallback): 3-bar Fractal jika pergerakan rapat
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            swing_highs.clear()
            swing_lows.clear()
            start_idx3 = shift - 1
            min_search3 = max(1, shift - min(100, self.fractal_lookback * 2))
            for i in range(start_idx3, min_search3, -1):
                if highs[i] > highs[i - 1] and highs[i] > highs[i + 1]:
                    swing_highs.append(highs[i])
                    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                        break
                if lows[i] < lows[i - 1] and lows[i] < lows[i + 1]:
                    swing_lows.append(lows[i])
                    if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                        break

        if len(swing_highs) < 2 or len(swing_lows) < 2:
            # Jika hanya ada 1 swing point tapi tren EMA jelas searah
            if len(swing_lows) >= 1 and len(swing_highs) >= 1:
                if 'ema21' in df.columns and 'ema125' in df.columns:
                    c0 = df.iloc[shift]
                    if c0['ema8'] > c0['ema21'] > c0['ema125'] and c0['low'] > swing_lows[0]:
                        return MarketStructure.BULLISH_HH_HL
                    elif c0['ema8'] < c0['ema21'] < c0['ema125'] and c0['high'] < swing_highs[0]:
                        return MarketStructure.BEARISH_LH_LL
            return MarketStructure.UNKNOWN

        sh_recent = swing_highs[0]
        sh_prev = swing_highs[1]
        sl_recent = swing_lows[0]
        sl_prev = swing_lows[1]

        # Kondisi Bullish: Higher High (atau break recent high) & Higher Low
        if (sh_recent >= sh_prev * 0.9995) and sl_recent > sl_prev:
            return MarketStructure.BULLISH_HH_HL

        # Kondisi Bearish: Lower High & Lower Low (atau break recent low)
        if (sh_recent < sh_prev) and (sl_recent <= sl_prev * 1.0005):
            return MarketStructure.BEARISH_LH_LL

        return MarketStructure.SIDEWAYS

    def is_ema8_21_choppy(self, df: pd.DataFrame, shift: int = -1) -> bool:
        """Cek apakah EMA 8 dan EMA 21 sering bolak-balik bersilangan."""
        n = len(df)
        if shift < 0:
            shift = n + shift
        start_idx = max(0, shift - self.chop_bars)
        
        diff = df['ema8'].iloc[start_idx:shift + 1] - df['ema21'].iloc[start_idx:shift + 1]
        signs = np.sign(diff.values)
        sign_changes = np.sum(signs[:-1] != signs[1:])
        
        return bool(sign_changes >= self.max_ema_crosses)

    def is_ema125_whipsawing(self, df: pd.DataFrame, shift: int = -1) -> bool:
        """Cek apakah harga close bolak-balik melintasi EMA 125."""
        n = len(df)
        if shift < 0:
            shift = n + shift
        start_idx = max(0, shift - self.whipsaw_bars)
        
        diff = df['close'].iloc[start_idx:shift + 1] - df['ema125'].iloc[start_idx:shift + 1]
        signs = np.sign(diff.values)
        sign_changes = np.sum(signs[:-1] != signs[1:])
        
        return bool(sign_changes >= self.max_whipsaw_crosses)

    def is_candle_overextended(self, close_price: float, ema8_val: float, atr_val: float) -> bool:
        """Cek apakah candle terlalu jauh melompat dari EMA 8."""
        if atr_val <= 0:
            return False
        distance = abs(close_price - ema8_val)
        return bool(distance > (self.max_atr_multiplier * atr_val))

    def validate_buy_filters(self, df: pd.DataFrame, require_hh_hl: bool = True, shift: int = -1) -> FilterResult:
        """Validasi filter false signal untuk BUY."""
        n = len(df)
        if shift < 0:
            shift = n + shift

        row = df.iloc[shift]
        # 1. Chop filter
        if self.is_ema8_21_choppy(df, shift):
            return FilterResult.FAIL_CHOP_EMA8_21

        # 2. Whipsaw filter
        if self.is_ema125_whipsawing(df, shift):
            return FilterResult.FAIL_WHIPSAW_125

        # 3. Overextended filter
        if self.is_candle_overextended(row['close'], row['ema8'], row['atr']):
            return FilterResult.FAIL_OVEREXTENDED

        # 4. Market Structure filter
        if require_hh_hl:
            struct = self.analyze_structure(df, shift)
            if struct != MarketStructure.BULLISH_HH_HL:
                return FilterResult.FAIL_STRUCTURE

        return FilterResult.PASS

    def validate_sell_filters(self, df: pd.DataFrame, require_lh_ll: bool = True, shift: int = -1) -> FilterResult:
        """Validasi filter false signal untuk SELL."""
        n = len(df)
        if shift < 0:
            shift = n + shift

        row = df.iloc[shift]
        # 1. Chop filter
        if self.is_ema8_21_choppy(df, shift):
            return FilterResult.FAIL_CHOP_EMA8_21

        # 2. Whipsaw filter
        if self.is_ema125_whipsawing(df, shift):
            return FilterResult.FAIL_WHIPSAW_125

        # 3. Overextended filter
        if self.is_candle_overextended(row['close'], row['ema8'], row['atr']):
            return FilterResult.FAIL_OVEREXTENDED

        # 4. Market Structure filter
        if require_lh_ll:
            struct = self.analyze_structure(df, shift)
            if struct != MarketStructure.BEARISH_LH_LL:
                return FilterResult.FAIL_STRUCTURE

        return FilterResult.PASS
