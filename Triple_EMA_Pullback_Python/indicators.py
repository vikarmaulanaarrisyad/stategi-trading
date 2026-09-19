"""
Modul Perhitungan Indikator Teknis
Mengimplementasikan EMA, ATR, dan ADX secara efisien dengan Pandas & Numpy.
"""

import pandas as pd
import numpy as np

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    """Menghitung Exponential Moving Average (EMA)."""
    return series.ewm(span=period, adjust=False).mean()

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Menghitung Average True Range (ATR).
    df wajib memiliki kolom: 'high', 'low', 'close'.
    """
    high = df['high']
    low = df['low']
    close_prev = df['close'].shift(1)
    
    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    # Gunakan metode Wilder's RMA (sama dengan perhitungan ATR standar di MT5)
    atr = tr.ewm(alpha=1.0 / period, adjust=False).mean()
    return atr

def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Menghitung Average Directional Index (ADX) 14 periode.
    df wajib memiliki kolom: 'high', 'low', 'close'.
    """
    high = df['high']
    low = df['low']
    close_prev = df['close'].shift(1)
    
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    plus_dm_series = pd.Series(plus_dm, index=df.index)
    minus_dm_series = pd.Series(minus_dm, index=df.index)
    
    tr1 = high - low
    tr2 = (high - close_prev).abs()
    tr3 = (low - close_prev).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.ewm(alpha=1.0 / period, adjust=False).mean()
    plus_di = 100 * (plus_dm_series.ewm(alpha=1.0 / period, adjust=False).mean() / atr.replace(0, np.nan))
    minus_di = 100 * (minus_dm_series.ewm(alpha=1.0 / period, adjust=False).mean() / atr.replace(0, np.nan))
    
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan))
    adx = dx.ewm(alpha=1.0 / period, adjust=False).mean().fillna(0.0)
    
    return adx

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Menghitung Relative Strength Index (RSI) dengan metode Wilder RMA."""
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    
    avg_gain = gain.ewm(alpha=1.0 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, adjust=False).mean()
    
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)

def is_in_fibo_golden_zone_buy(df: pd.DataFrame, shift: int = -1, lookback: int = 30, min_retrace: float = 0.50, max_retrace: float = 0.786) -> bool:
    """Mengecek apakah candle pullback menguji zona Fibo Discount / Golden Zone (0.50 - 0.786)."""
    n = len(df)
    idx = n + shift if shift < 0 else shift
    if idx < lookback:
        return True
    
    sub_df = df.iloc[max(0, idx - lookback):idx]
    swing_high = sub_df['high'].max()
    swing_low = sub_df['low'].min()
    diff = swing_high - swing_low
    if diff <= 0:
        return True
    
    fibo_50 = swing_high - (min_retrace * diff)
    fibo_deep = swing_high - (max_retrace * diff)
    
    pullback_low = df.iloc[idx]['low']
    pullback_high = df.iloc[idx]['high']
    return (pullback_low <= fibo_50 and pullback_high >= fibo_deep)

def is_in_fibo_golden_zone_sell(df: pd.DataFrame, shift: int = -1, lookback: int = 30, min_retrace: float = 0.50, max_retrace: float = 0.786) -> bool:
    """Mengecek apakah candle pullback menguji zona Fibo Premium / Golden Zone (0.50 - 0.786)."""
    n = len(df)
    idx = n + shift if shift < 0 else shift
    if idx < lookback:
        return True
    
    sub_df = df.iloc[max(0, idx - lookback):idx]
    swing_high = sub_df['high'].max()
    swing_low = sub_df['low'].min()
    diff = swing_high - swing_low
    if diff <= 0:
        return True
    
    fibo_50 = swing_low + (min_retrace * diff)
    fibo_deep = swing_low + (max_retrace * diff)
    
    pullback_high = df.iloc[idx]['high']
    pullback_low = df.iloc[idx]['low']
    return (pullback_high >= fibo_50 and pullback_low <= fibo_deep)

def has_active_fvg(df: pd.DataFrame, is_buy: bool, shift: int = -1, lookback: int = 10) -> bool:
    """Mendeteksi apakah terdapat Bullish / Bearish FVG dalam lookback bar."""
    n = len(df)
    idx = n + shift if shift < 0 else shift
    if idx < 3:
        return False
    
    for i in range(max(2, idx - lookback), idx):
        if is_buy:
            if df.iloc[i]['low'] > df.iloc[i-2]['high']:
                gap_top = df.iloc[i]['low']
                gap_bottom = df.iloc[i-2]['high']
                current_low = df.iloc[idx]['low']
                if current_low <= gap_top and current_low >= gap_bottom:
                    return True
        else:
            if df.iloc[i]['high'] < df.iloc[i-2]['low']:
                gap_bottom = df.iloc[i]['high']
                gap_top = df.iloc[i-2]['low']
                current_high = df.iloc[idx]['high']
                if current_high >= gap_bottom and current_high <= gap_top:
                    return True
    return False

def compute_all_indicators(df: pd.DataFrame, 
                           ema_fast: int = 8, 
                           ema_med: int = 21, 
                           ema_slow: int = 125, 
                           atr_period: int = 14, 
                           adx_period: int = 14,
                           rsi_period: int = 14) -> pd.DataFrame:
    """Menambahkan seluruh kolom indikator teknis ke DataFrame."""
    df = df.copy()
    df['ema8'] = calculate_ema(df['close'], ema_fast)
    df['ema21'] = calculate_ema(df['close'], ema_med)
    df['ema125'] = calculate_ema(df['close'], ema_slow)
    df['atr'] = calculate_atr(df, atr_period)
    df['adx'] = calculate_adx(df, adx_period)
    df['rsi'] = calculate_rsi(df['close'], rsi_period)
    return df
