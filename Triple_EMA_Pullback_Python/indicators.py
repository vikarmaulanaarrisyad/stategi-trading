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

def compute_all_indicators(df: pd.DataFrame, 
                           ema_fast: int = 8, 
                           ema_med: int = 21, 
                           ema_slow: int = 125, 
                           atr_period: int = 14, 
                           adx_period: int = 14) -> pd.DataFrame:
    """Menambahkan seluruh kolom indikator teknis ke DataFrame."""
    df = df.copy()
    df['ema8'] = calculate_ema(df['close'], ema_fast)
    df['ema21'] = calculate_ema(df['close'], ema_med)
    df['ema125'] = calculate_ema(df['close'], ema_slow)
    df['atr'] = calculate_atr(df, atr_period)
    df['adx'] = calculate_adx(df, adx_period)
    return df
