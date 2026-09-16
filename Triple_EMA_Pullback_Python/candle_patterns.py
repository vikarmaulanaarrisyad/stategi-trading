"""
Modul Deteksi 18 Pola Candlestick Rejection & Confirmation
Mengonversi logika dari CandlePatterns.mqh ke Python murni.
"""

from enum import Enum
from typing import Tuple, Optional
import pandas as pd

class CandlePattern(Enum):
    NONE = 0
    # Pola Bullish (1 - 9)
    HAMMER = 1
    BULLISH_PINBAR = 2
    BULLISH_ENGULFING = 3
    MORNING_STAR = 4
    PIERCING_LINE = 5
    THREE_WHITE_SOLDIERS = 6
    BULLISH_DOJI = 7
    BULLISH_INSIDE_BAR = 8
    BULLISH_TWO_CANDLE_REJECTION = 9
    
    # Pola Bearish (10 - 18)
    SHOOTING_STAR = 10
    BEARISH_PINBAR = 11
    BEARISH_ENGULFING = 12
    DARK_CLOUD_COVER = 13
    EVENING_STAR = 14
    THREE_BLACK_CROWS = 15
    BEARISH_DOJI = 16
    BEARISH_INSIDE_BAR = 17
    BEARISH_TWO_CANDLE_REJECTION = 18

def get_pattern_name(pattern: CandlePattern) -> str:
    """Mengembalikan deskripsi nama pola candlestick."""
    names = {
        CandlePattern.HAMMER: "Hammer (Bullish Rejection)",
        CandlePattern.BULLISH_PINBAR: "Bullish Pin Bar",
        CandlePattern.BULLISH_ENGULFING: "Bullish Engulfing",
        CandlePattern.MORNING_STAR: "Morning Star (3 Candles)",
        CandlePattern.PIERCING_LINE: "Piercing Line",
        CandlePattern.THREE_WHITE_SOLDIERS: "Three White Soldiers",
        CandlePattern.BULLISH_DOJI: "Bullish Doji Rejection",
        CandlePattern.BULLISH_INSIDE_BAR: "Bullish Inside Bar Breakout",
        CandlePattern.BULLISH_TWO_CANDLE_REJECTION: "Two Candle Bullish Rejection",
        
        CandlePattern.SHOOTING_STAR: "Shooting Star (Bearish Rejection)",
        CandlePattern.BEARISH_PINBAR: "Bearish Pin Bar",
        CandlePattern.BEARISH_ENGULFING: "Bearish Engulfing",
        CandlePattern.DARK_CLOUD_COVER: "Dark Cloud Cover",
        CandlePattern.EVENING_STAR: "Evening Star (3 Candles)",
        CandlePattern.THREE_BLACK_CROWS: "Three Black Crows",
        CandlePattern.BEARISH_DOJI: "Bearish Doji Rejection",
        CandlePattern.BEARISH_INSIDE_BAR: "Bearish Inside Bar Breakdown",
        CandlePattern.BEARISH_TWO_CANDLE_REJECTION: "Two Candle Bearish Rejection",
        CandlePattern.NONE: "No Pattern"
    }
    return names.get(pattern, "No Pattern")

def is_touch_ema_zone(low: float, high: float, ema8: float, ema21: float) -> bool:
    """Cek apakah harga menguji/menyentuh zona nilai antara EMA 8 dan EMA 21."""
    upper_zone = max(ema8, ema21)
    lower_zone = min(ema8, ema21)
    buffer = (upper_zone - lower_zone) * 0.3
    return (low <= (upper_zone + buffer)) and (high >= (lower_zone - buffer))

def detect_bullish_pattern(df: pd.DataFrame, idx: int = -1, shift: Optional[int] = None) -> CandlePattern:
    """
    Mendeteksi 9 pola candlestick bullish pada index candle yang baru saja closed (idx / shift).
    df wajib berisi bar berurutan (indeks terakhir adalah candle tertutup terbaru).
    """
    if shift is not None:
        idx = shift
    # Butuh minimal 4 candle sebelumnya
    n = len(df)
    if idx < 0:
        idx = n + idx
    if idx < 3 or idx >= n:
        return CandlePattern.NONE

    # Candle 0 (candle konfirmasi yang baru close di bar idx)
    c0_row = df.iloc[idx]
    o0, h0, l0, c0 = c0_row['open'], c0_row['high'], c0_row['low'], c0_row['close']
    ema8_0, ema21_0, ema125_0 = c0_row['ema8'], c0_row['ema21'], c0_row['ema125']
    range0 = h0 - l0
    if range0 <= 0:
        return CandlePattern.NONE
        
    body0 = abs(c0 - o0)
    lower_wick0 = (o0 - l0) if c0 >= o0 else (c0 - l0)
    upper_wick0 = (h0 - c0) if c0 >= o0 else (h0 - o0)
    is_bullish0 = c0 > o0

    # Candle 1 (1 candle sebelumnya)
    c1_row = df.iloc[idx - 1]
    o1, h1, l1, c1 = c1_row['open'], c1_row['high'], c1_row['low'], c1_row['close']
    range1 = h1 - l1
    body1 = abs(c1 - o1)
    is_bearish1 = c1 < o1

    # Candle 2 (2 candle sebelumnya)
    c2_row = df.iloc[idx - 2]
    o2, h2, l2, c2 = c2_row['open'], c2_row['high'], c2_row['low'], c2_row['close']

    # Validasi Dasar: Minimal salah satu dari 3 candle terakhir menguji zona EMA 8/21 dan semua low tetap di atas EMA 125
    touched_zone = (
        is_touch_ema_zone(l0, h0, ema8_0, ema21_0) or
        is_touch_ema_zone(l1, h1, c1_row['ema8'], c1_row['ema21']) or
        is_touch_ema_zone(l2, h2, c2_row['ema8'], c2_row['ema21'])
    )
    if not touched_zone:
        return CandlePattern.NONE
    if l0 <= ema125_0 or l1 <= c1_row['ema125'] or l2 <= c2_row['ema125']:
        return CandlePattern.NONE

    # 1. HAMMER (Ekor bawah panjang >= 2x body, upper wick <= 25% range, close di area 65% atas)
    if (lower_wick0 >= 2.0 * body0) and (upper_wick0 <= 0.25 * range0) and ((c0 - l0) >= 0.65 * range0):
        return CandlePattern.HAMMER

    # 2. BULLISH PIN BAR (Ekor bawah >= 60% total range, body kecil di atas)
    if (lower_wick0 >= 0.60 * range0) and (upper_wick0 <= 0.20 * range0) and (body0 <= 0.35 * range0):
        return CandlePattern.BULLISH_PINBAR

    # 3. BULLISH ENGULFING (Candle hijau menelan candle merah sebelumnya)
    if is_bullish0 and is_bearish1 and body1 > 0:
        if c0 >= o1 and o0 <= c1 and body0 > body1:
            return CandlePattern.BULLISH_ENGULFING

    # 4. MORNING STAR (3 candle: bearish -> small body indecision di EMA -> bullish kuat)
    if (c2 < o2) and (range1 > 0):
        is_small_body1 = body1 <= (range1 * 0.40)
        is_strong_bullish0 = is_bullish0 and (c0 >= (o2 + c2) / 2.0)
        ema_zone_1 = max(c1_row['ema8'], c1_row['ema21'])
        if is_small_body1 and is_strong_bullish0 and (l1 <= ema_zone_1 * 1.002):
            return CandlePattern.MORNING_STAR

    # 5. PIERCING LINE (Candle merah diikuti candle hijau yang open rendah lalu tembus 50% body merah)
    if is_bearish1 and is_bullish0 and body1 > 0:
        mid_point1 = (o1 + c1) / 2.0
        if o0 <= (c1 + (range1 * 0.1)) and c0 > mid_point1 and c0 < o1:
            return CandlePattern.PIERCING_LINE

    # 6. THREE WHITE SOLDIERS (3 candle hijau berturut-turut, higher close, higher high)
    if (c0 > o0) and (c1 > o1) and (c2 > o2):
        if (c0 > c1 > c2) and (h0 > h1 > h2):
            if upper_wick0 <= 0.3 * range0 and (h1 - c1) <= 0.3 * range1:
                return CandlePattern.THREE_WHITE_SOLDIERS

    # 7. BULLISH DOJI REJECTION (Body <= 12% range, ekor bawah panjang >= 50% range, c0 >= o0)
    if (body0 <= 0.12 * range0) and (lower_wick0 >= 0.50 * range0) and (c0 >= o0):
        return CandlePattern.BULLISH_DOJI

    # 8. BULLISH INSIDE BAR BREAKOUT (Candle 1 di dalam candle 2, lalu candle 0 breakout ke atas)
    if (h1 <= h2) and (l1 >= l2):
        if is_bullish0 and c0 > h1:
            return CandlePattern.BULLISH_INSIDE_BAR

    # 9. TWO CANDLE REJECTION (Candle 1 ekor bawah panjang membentur EMA, candle 0 bullish kuat)
    if range1 > 0:
        lower_wick1 = (o1 - l1) if c1 >= o1 else (c1 - l1)
        if lower_wick1 >= (0.45 * range1) and is_bullish0 and c0 > h1:
            return CandlePattern.BULLISH_TWO_CANDLE_REJECTION

    return CandlePattern.NONE

def detect_bearish_pattern(df: pd.DataFrame, idx: int = -1, shift: Optional[int] = None) -> CandlePattern:
    """
    Mendeteksi 9 pola candlestick bearish pada index candle yang baru saja closed (idx / shift).
    df wajib berisi bar berurutan.
    """
    if shift is not None:
        idx = shift
    n = len(df)
    if idx < 0:
        idx = n + idx
    if idx < 3 or idx >= n:
        return CandlePattern.NONE

    # Candle 0
    c0_row = df.iloc[idx]
    o0, h0, l0, c0 = c0_row['open'], c0_row['high'], c0_row['low'], c0_row['close']
    ema8_0, ema21_0, ema125_0 = c0_row['ema8'], c0_row['ema21'], c0_row['ema125']
    range0 = h0 - l0
    if range0 <= 0:
        return CandlePattern.NONE

    body0 = abs(c0 - o0)
    lower_wick0 = (o0 - l0) if c0 >= o0 else (c0 - l0)
    upper_wick0 = (h0 - c0) if c0 >= o0 else (h0 - o0)
    is_bearish0 = c0 < o0

    # Candle 1
    c1_row = df.iloc[idx - 1]
    o1, h1, l1, c1 = c1_row['open'], c1_row['high'], c1_row['low'], c1_row['close']
    range1 = h1 - l1
    body1 = abs(c1 - o1)
    is_bullish1 = c1 > o1

    # Candle 2
    c2_row = df.iloc[idx - 2]
    o2, h2, l2, c2 = c2_row['open'], c2_row['high'], c2_row['low'], c2_row['close']

    # Validasi Dasar: Minimal salah satu dari 3 candle terakhir menguji zona EMA 8/21 dan semua high tetap di bawah EMA 125
    touched_zone = (
        is_touch_ema_zone(l0, h0, ema8_0, ema21_0) or
        is_touch_ema_zone(l1, h1, c1_row['ema8'], c1_row['ema21']) or
        is_touch_ema_zone(l2, h2, c2_row['ema8'], c2_row['ema21'])
    )
    if not touched_zone:
        return CandlePattern.NONE
    if h0 >= ema125_0 or h1 >= c1_row['ema125'] or h2 >= c2_row['ema125']:
        return CandlePattern.NONE

    # 1. SHOOTING STAR (Ekor atas panjang >= 2x body, body kecil di bawah)
    if (upper_wick0 >= 2.0 * body0) and (lower_wick0 <= 0.25 * range0) and ((h0 - c0) >= 0.65 * range0):
        return CandlePattern.SHOOTING_STAR

    # 2. BEARISH PIN BAR (Ekor atas >= 60% total range, body kecil di bawah)
    if (upper_wick0 >= 0.60 * range0) and (lower_wick0 <= 0.20 * range0) and (body0 <= 0.35 * range0):
        return CandlePattern.BEARISH_PINBAR

    # 3. BEARISH ENGULFING (Candle merah menelan candle hijau sebelumnya)
    if is_bearish0 and is_bullish1 and body1 > 0:
        if c0 <= o1 and o0 >= c1 and body0 > body1:
            return CandlePattern.BEARISH_ENGULFING

    # 4. DARK CLOUD COVER (Candle hijau diikuti candle merah open tinggi lalu tembus 50% body hijau)
    if is_bullish1 and is_bearish0 and body1 > 0:
        mid_point1 = (o1 + c1) / 2.0
        if o0 >= (c1 - (range1 * 0.1)) and c0 < mid_point1 and c0 > o1:
            return CandlePattern.DARK_CLOUD_COVER

    # 5. EVENING STAR (3 candle: bullish -> small body indecision di EMA -> bearish kuat)
    if (c2 > o2) and (range1 > 0):
        is_small_body1 = body1 <= (range1 * 0.40)
        is_strong_bearish0 = is_bearish0 and (c0 <= (o2 + c2) / 2.0)
        ema_zone_1 = min(c1_row['ema8'], c1_row['ema21'])
        if is_small_body1 and is_strong_bearish0 and (h1 >= ema_zone_1 * 0.998):
            return CandlePattern.EVENING_STAR

    # 6. THREE BLACK CROWS (3 candle merah berturut-turut, lower close, lower low)
    if (c0 < o0) and (c1 < o1) and (c2 < o2):
        if (c0 < c1 < c2) and (l0 < l1 < l2):
            if lower_wick0 <= 0.3 * range0 and (c1 - l1) <= 0.3 * range1:
                return CandlePattern.THREE_BLACK_CROWS

    # 7. BEARISH DOJI REJECTION (Body <= 12% range, ekor atas panjang >= 50% range, c0 <= o0)
    if (body0 <= 0.12 * range0) and (upper_wick0 >= 0.50 * range0) and (c0 <= o0):
        return CandlePattern.BEARISH_DOJI

    # 8. BEARISH INSIDE BAR BREAKDOWN (Candle 1 di dalam candle 2, lalu candle 0 breakdown ke bawah)
    if (h1 <= h2) and (l1 >= l2):
        if is_bearish0 and c0 < l1:
            return CandlePattern.BEARISH_INSIDE_BAR

    # 9. TWO CANDLE REJECTION (Candle 1 ekor atas panjang menabrak EMA, candle 0 bearish kuat)
    if range1 > 0:
        upper_wick1 = (h1 - c1) if c1 >= o1 else (h1 - o1)
        if upper_wick1 >= (0.45 * range1) and is_bearish0 and c0 < l1:
            return CandlePattern.BEARISH_TWO_CANDLE_REJECTION

    return CandlePattern.NONE
