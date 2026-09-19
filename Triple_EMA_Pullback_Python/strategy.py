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
    session_name: str = ""                      # Sesi pasar ("LONDON", "NEW_YORK", "ASIA", "OVERLAP")
    news_status: str = ""                       # Status fundamental berita ("CLEAN", "SHOCK_AVOIDED")
    confluence_score: int = 100                 # Skor konfluensi 0 - 100
    setup_grade: str = "A"                      # Grade kualitas ("A+", "A", "B", "C")
    confluence_details: str = ""                # Rincian poin konfluensi ("Fibo+RSI+Struct")

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

    def get_session_name(self, bar_time) -> str:
        """Mengidentifikasi sesi pasar berdasarkan jam candle broker."""
        if bar_time is None or not hasattr(bar_time, 'hour'):
            return "UNKNOWN"
        h = bar_time.hour
        # Asumsi jam broker GMT+2 / GMT+3 (standard Forex broker):
        # Asia: 00:00 - 08:00 broker
        # London Open: 08:00 - 14:00 broker
        # London/NY Overlap: 14:00 - 18:00 broker
        # NY Afternoon: 18:00 - 22:00 broker
        if 8 <= h < 14:
            return "LONDON"
        elif 14 <= h < 18:
            return "LONDON_NY_OVERLAP"
        elif 18 <= h < 22:
            return "NEW_YORK"
        else:
            return "ASIAN_SESSION"

    def is_session_allowed(self, bar_time) -> Tuple[bool, str]:
        """Cek apakah sesi saat ini diizinkan untuk eksekusi sinyal."""
        session_mode = getattr(self.config, 'xau_session_filter', 'ALL')
        if session_mode == 'LONDON_NY' and hasattr(bar_time, 'hour'):
            h = bar_time.hour
            # Hanya London & NY (jam 8 sampai 21 broker)
            if h < 8 or h >= 21:
                return False, f"Sesi Asia diabaikan (Hour {h:02d}:00)"
        return True, "Session OK"

    def is_fundamental_shock_active(self, df: pd.DataFrame, shift: int = -1) -> Tuple[bool, str]:
        """
        Deteksi Shock Volatilitas Berita Fundamental.
        Mencegah entri saat/segera setelah candle lonjakan berita besar (> 2.5x ATR).
        """
        if not getattr(self.config, 'use_fundamental_shock_filter', True):
            return False, "Filter News Shock nonaktif"

        n = len(df)
        if shift < 0:
            shift = n + shift
        mult = getattr(self.config, 'fundamental_shock_atr_multiplier', 2.5)
        cooldown = max(1, getattr(self.config, 'fundamental_shock_cooldown_bars', 4))
        start = max(0, shift - cooldown)

        for i in range(shift, start - 1, -1):
            bar = df.iloc[i]
            atr_val = bar.get('atr', 0.0)
            bar_range = bar['high'] - bar['low']
            if atr_val > 0 and bar_range >= (mult * atr_val):
                bars_ago = shift - i
                return True, f"Fundamental Shock Bar ({bar_range:.2f} >= {mult}x ATR, {bars_ago} bar lalu)"

        return False, "Normal Volatility"

    def is_news_window_active(self, bar_time) -> Tuple[bool, str]:
        """Cek apakah candle berada pada jam rilis berita makro AS penting."""
        if not getattr(self.config, 'use_news_window_filter', False):
            return False, "Filter News Window nonaktif"
        if bar_time is not None and hasattr(bar_time, 'hour'):
            windows = getattr(self.config, 'news_window_hours', (13, 14, 19, 20))
            if bar_time.hour in windows:
                return True, f"Jendela Rilis Berita AS (Jam {bar_time.hour:02d}:00)"
        return False, "Clear Window"

    def calculate_confluence_score(self, signal_type: str, df: pd.DataFrame, shift: int = -1) -> Tuple[int, str, str]:
        """
        Menghitung skor konfluensi dan grade kualitas setup (A+, A, B, C).
        Mengembalikan (score, grade, details_string).
        """
        score = 0
        details = []
        n = len(df)
        if shift < 0:
            shift = n + shift
        c0 = df.iloc[shift]

        w_fibo = getattr(self.config, 'score_weight_fibo', 20)
        w_rsi  = getattr(self.config, 'score_weight_rsi', 20)
        w_fvg  = getattr(self.config, 'score_weight_fvg', 20)
        w_adx  = getattr(self.config, 'score_weight_adx', 20)
        w_str  = getattr(self.config, 'score_weight_structure', 20)

        # 1. Fibo Golden Zone (50% - 78.6%)
        from indicators import is_in_fibo_golden_zone_buy, is_in_fibo_golden_zone_sell
        if signal_type == "BUY":
            if is_in_fibo_golden_zone_buy(df, shift):
                score += w_fibo
                details.append("Fibo")
        else:
            if is_in_fibo_golden_zone_sell(df, shift):
                score += w_fibo
                details.append("Fibo")

        # 2. RSI Momentum Sehat (45-70 Buy / 30-55 Sell)
        if 'rsi' in c0:
            rsi_val = c0['rsi']
            if signal_type == "BUY" and (45.0 <= rsi_val <= 70.0):
                score += w_rsi
                details.append("RSI")
            elif signal_type == "SELL" and (30.0 <= rsi_val <= 55.0):
                score += w_rsi
                details.append("RSI")

        # 3. FVG Mitigation
        from indicators import has_active_fvg
        if has_active_fvg(df, is_buy=(signal_type == "BUY"), shift=shift):
            score += w_fvg
            details.append("FVG")

        # 4. ADX Strength
        if 'adx' in c0 and c0['adx'] >= getattr(self.config, 'min_adx_level', 20.0):
            score += w_adx
            details.append("ADX")

        # 5. Structure (HH-HL / LH-LL)
        if signal_type == "BUY":
            res = self.structure_analyzer.validate_buy_filters(df, require_hh_hl=True, shift=shift)
        else:
            res = self.structure_analyzer.validate_sell_filters(df, require_lh_ll=True, shift=shift)
        if res == FilterResult.PASS:
            score += w_str
            details.append("Struct")

        # Tentukan Grade Setup
        if score >= 80:
            grade = "A+"
        elif score >= 60:
            grade = "A"
        elif score >= 40:
            grade = "B"
        else:
            grade = "C"

        return score, grade, "+".join(details)

    def detect_bullish_breakout(self, df: pd.DataFrame, shift: int = -1) -> Tuple[bool, float]:
        """
        Deteksi Bullish Momentum Breakout (Penembusan Range Lookback Donchian).
        Close di atas highest high dari lookback bar sebelumnya, didukung solid candle body.
        """
        if not getattr(self.config, 'use_breakout_strategy', True):
            return False, 0.0
            
        n = len(df)
        if shift < 0:
            shift = n + shift
            
        lookback = getattr(self.config, 'breakout_lookback_bars', 15)
        min_body_ratio = getattr(self.config, 'breakout_min_body_ratio', 0.50)
        
        if shift < lookback + 2:
            return False, 0.0
            
        c0 = df.iloc[shift]
        range0 = c0['high'] - c0['low']
        if range0 <= 0.0 or c0['close'] <= c0['open']:
            return False, 0.0
            
        body0 = c0['close'] - c0['open']
        if (body0 / range0) < min_body_ratio:
            return False, 0.0
            
        # Highest High dari shift - 1 ke shift - lookback
        highest_high = max(df.iloc[shift - i]['high'] for i in range(1, lookback + 1))
        
        # Volume check jika diaktifkan
        if getattr(self.config, 'breakout_require_volume', True) and 'volume' in df.columns:
            vol_lookback = getattr(self.config, 'volume_lookback', 20)
            start_vol = max(0, shift - 1 - vol_lookback)
            avg_vol = df.iloc[start_vol:shift]['volume'].mean()
            vol_mult = getattr(self.config, 'breakout_vol_multiplier', 1.1)
            if avg_vol > 0 and c0['volume'] < (avg_vol * vol_mult):
                return False, highest_high
                
        return (c0['close'] > highest_high), highest_high

    def detect_bearish_breakout(self, df: pd.DataFrame, shift: int = -1) -> Tuple[bool, float]:
        """
        Deteksi Bearish Momentum Breakout (Penembusan Range Lookback Donchian).
        Close di bawah lowest low dari lookback bar sebelumnya, didukung solid candle body.
        """
        if not getattr(self.config, 'use_breakout_strategy', True):
            return False, 0.0
            
        n = len(df)
        if shift < 0:
            shift = n + shift
            
        lookback = getattr(self.config, 'breakout_lookback_bars', 15)
        min_body_ratio = getattr(self.config, 'breakout_min_body_ratio', 0.50)
        
        if shift < lookback + 2:
            return False, 0.0
            
        c0 = df.iloc[shift]
        range0 = c0['high'] - c0['low']
        if range0 <= 0.0 or c0['close'] >= c0['open']:
            return False, 0.0
            
        body0 = c0['open'] - c0['close']
        if (body0 / range0) < min_body_ratio:
            return False, 0.0
            
        # Lowest Low dari shift - 1 ke shift - lookback
        lowest_low = min(df.iloc[shift - i]['low'] for i in range(1, lookback + 1))
        
        # Volume check jika diaktifkan
        if getattr(self.config, 'breakout_require_volume', True) and 'volume' in df.columns:
            vol_lookback = getattr(self.config, 'volume_lookback', 20)
            start_vol = max(0, shift - 1 - vol_lookback)
            avg_vol = df.iloc[start_vol:shift]['volume'].mean()
            vol_mult = getattr(self.config, 'breakout_vol_multiplier', 1.1)
            if avg_vol > 0 and c0['volume'] < (avg_vol * vol_mult):
                return False, lowest_low
                
        return (c0['close'] < lowest_low), lowest_low

    def calculate_breakout_confluence_score(self, signal_type: str, df: pd.DataFrame, shift: int = -1) -> Tuple[int, str, str]:
        """
        Hitung Skor Konfluensi Khusus Setup Momentum Breakout.
        Base 40 + RSI + ADX + Volume.
        """
        score = 40
        details = ["RangeBreak"]
        c0 = df.iloc[shift]
        
        rsi_val = c0.get('rsi', 50.0)
        adx_val = c0.get('adx', 20.0)
        
        if signal_type == "BUY":
            if 45.0 <= rsi_val <= 75.0:
                score += 20
                details.append("RSI")
        else:
            if 25.0 <= rsi_val <= 55.0:
                score += 20
                details.append("RSI")
                
        if adx_val >= 20.0:
            score += 20
            details.append("ADX")
            
        if 'volume' in df.columns:
            vol_lookback = getattr(self.config, 'volume_lookback', 20)
            start_vol = max(0, shift - 1 - vol_lookback)
            avg_vol = df.iloc[start_vol:shift]['volume'].mean()
            vol_mult = getattr(self.config, 'breakout_vol_multiplier', 1.1)
            if avg_vol > 0 and c0['volume'] >= (avg_vol * vol_mult):
                score += 20
                details.append("Vol")
                
        if score >= 80:
            grade = "A+"
        elif score >= 60:
            grade = "A"
        else:
            grade = "B"
            
        return score, grade, "+".join(details)

    def calculate_smc_confluence_score(self, signal_type: str, df: pd.DataFrame, smc_info: str, shift: int = -1) -> Tuple[int, str, str]:
        """
        Hitung Skor Konfluensi Khusus Setup SMC Institutional.
        Base 40 + RSI + ADX + Volume.
        """
        score = 40
        details = [smc_info] if smc_info else ["SMC"]
        c0 = df.iloc[shift]
        
        rsi_val = c0.get('rsi', 50.0)
        adx_val = c0.get('adx', 20.0)
        
        if signal_type == "BUY":
            if 40.0 <= rsi_val <= 70.0:
                score += 20
                details.append("RSI")
        else:
            if 30.0 <= rsi_val <= 60.0:
                score += 20
                details.append("RSI")
                
        if adx_val >= 20.0:
            score += 20
            details.append("ADX")
            
        if 'volume' in df.columns:
            vol_lookback = getattr(self.config, 'volume_lookback', 20)
            start_vol = max(0, shift - 1 - vol_lookback)
            avg_vol = df.iloc[start_vol:shift]['volume'].mean()
            if avg_vol > 0 and c0['volume'] >= avg_vol:
                score += 20
                details.append("Vol")
                
        if score >= 80:
            grade = "A+"
        elif score >= 60:
            grade = "A"
        else:
            grade = "B"
            
        return score, grade, "+".join(details)

    def calculate_sl_tp(self, 
                        signal_type: str, 
                        entry_price: float, 
                        df: pd.DataFrame, 
                        point_size: float,
                        shift: int = -1,
                        is_breakout: bool = False,
                        is_smc: bool = False,
                        smc_level: Optional[float] = None) -> Tuple[float, float, float]:
        """
        Menghitung harga Stop Loss dan Take Profit berdasarkan mode SL.
        Mengembalikan (sl_price, tp_price, sl_distance_points).
        Mengintegrasikan proteksi volatilitas dinamis khusus Emas (XAUUSD).
        """
        n = len(df)
        if shift < 0:
            shift = n + shift
            
        row = df.iloc[shift]
        atr_val = row['atr']
        
        # SL adaptif volatilitas Emas: minimal xau_min_sl_atr_mult x ATR M15
        xau_mult = getattr(self.config, 'xau_min_sl_atr_mult', 1.0)
        atr_min_pts = (atr_val * xau_mult) / point_size if point_size > 0 else 0
        effective_min_sl = max(float(self.config.min_sl_points), atr_min_pts)
        
        # Buffer adaptif: minimal buffer_points atau 0.25x ATR
        effective_buffer = max(self.config.sl_buffer_points * point_size, 0.25 * atr_val)

        lookback = max(2, min(shift, getattr(self.config, 'swing_lookback_bars', 6)))
        if signal_type == "BUY":
            if is_breakout:
                lowest_low = min(df.iloc[shift]['low'], df.iloc[shift - 1]['low'])
                sl_price = lowest_low - effective_buffer
            elif is_smc:
                lowest_low = min(df.iloc[shift]['low'], df.iloc[shift - 1]['low']) if smc_level is None else smc_level
                sl_price = lowest_low - effective_buffer
            elif self.config.sl_mode == "SWING_CANDLE":
                recent_lows = [df.iloc[shift - i]['low'] for i in range(lookback)]
                lowest_low = min(recent_lows)
                sl_price = lowest_low - effective_buffer
            elif self.config.sl_mode == "ATR_BASED":
                sl_price = entry_price - (self.config.sl_atr_multiplier * atr_val)
            else:  # FIXED_POINTS
                sl_price = entry_price - (self.config.sl_fixed_points * point_size)
                
            sl_dist_pts = (entry_price - sl_price) / point_size
            if sl_dist_pts < effective_min_sl:
                sl_price = entry_price - (effective_min_sl * point_size)
                sl_dist_pts = effective_min_sl
                
            tp_price = entry_price + ((entry_price - sl_price) * self.config.risk_reward_ratio)
            
        else:  # SELL
            if is_breakout:
                highest_high = max(df.iloc[shift]['high'], df.iloc[shift - 1]['high'])
                sl_price = highest_high + effective_buffer
            elif is_smc:
                highest_high = max(df.iloc[shift]['high'], df.iloc[shift - 1]['high']) if smc_level is None else smc_level
                sl_price = highest_high + effective_buffer
            elif self.config.sl_mode == "SWING_CANDLE":
                recent_highs = [df.iloc[shift - i]['high'] for i in range(lookback)]
                highest_high = max(recent_highs)
                sl_price = highest_high + effective_buffer
            elif self.config.sl_mode == "ATR_BASED":
                sl_price = entry_price + (self.config.sl_atr_multiplier * atr_val)
            else:  # FIXED_POINTS
                sl_price = entry_price + (self.config.sl_fixed_points * point_size)
                
            sl_dist_pts = (sl_price - entry_price) / point_size
            if sl_dist_pts < effective_min_sl:
                sl_price = entry_price + (effective_min_sl * point_size)
                sl_dist_pts = effective_min_sl
                
            tp_price = entry_price - ((sl_price - entry_price) * self.config.risk_reward_ratio)

        return sl_price, tp_price, sl_dist_pts

    def evaluate_signal(self, 
                        df: pd.DataFrame, 
                        current_ask: Optional[float] = None, 
                        current_bid: Optional[float] = None, 
                        point_size: float = 0.01,
                        htf_bullish: bool = True,
                        htf_bearish: bool = True,
                        m15_df: Optional[pd.DataFrame] = None,
                        h1_df: Optional[pd.DataFrame] = None,
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
        bar_time = c0.get('time', None)

        # 0. Filter Fundamental & Sesi Pasar
        shock_active, shock_msg = self.is_fundamental_shock_active(df, shift)
        if shock_active:
            return None

        news_active, news_msg = self.is_news_window_active(bar_time)
        if news_active:
            return None

        sess_allowed, sess_msg = self.is_session_allowed(bar_time)
        if not sess_allowed:
            return None

        sess_name = self.get_session_name(bar_time)

        if current_ask is None:
            current_ask = float(c0['close'])
        if current_bid is None:
            current_bid = float(c0['close'])

        # Evaluasi Sistem 3 Layar (Triple Screen: H1 Macro Bias & M15 Market Structure)
        use_triple = getattr(self.config, 'use_triple_screen', True)
        m15_buy_ok = True
        m15_sell_ok = True

        if use_triple:
            # 1. Layar 1: H1 Macro Bias
            if h1_df is not None and len(h1_df) >= 2:
                h1_bar = h1_df.iloc[-1]
                h1_ema_col = f"ema{getattr(self.config, 'screen1_ema_period', 50)}"
                if h1_ema_col in h1_bar:
                    if h1_bar['close'] < h1_bar[h1_ema_col]:
                        htf_bullish = False
                    if h1_bar['close'] > h1_bar[h1_ema_col]:
                        htf_bearish = False

            # 2. Layar 2: M15 Market Structure & Level Kunci
            if m15_df is not None and len(m15_df) >= 30:
                from market_structure import MarketStructure
                m15_struct = self.structure_analyzer.analyze_structure(m15_df, shift=-1)
                m15_bar = m15_df.iloc[-1]
                m15_ema_col = f"ema{getattr(self.config, 'screen2_ema_period', 50)}"

                if getattr(self.config, 'screen2_require_structure', True):
                    if m15_struct == MarketStructure.BEARISH_LH_LL:
                        m15_buy_ok = False
                    if m15_struct == MarketStructure.BULLISH_HH_HL:
                        m15_sell_ok = False

                if getattr(self.config, 'screen2_require_key_level', True) and m15_ema_col in m15_bar:
                    if m15_bar['close'] < m15_bar[m15_ema_col]:
                        m15_buy_ok = False
                    if m15_bar['close'] > m15_bar[m15_ema_col]:
                        m15_sell_ok = False

        # Sinyal BUY (Pullback, Breakout, atau SMC Institutional)
        bull_pattern = detect_bullish_pattern(df, shift)
        is_bull_breakout = False
        bull_break_level = 0.0
        if bull_pattern == CandlePattern.NONE and getattr(self.config, 'use_breakout_strategy', True):
            is_bull_breakout, bull_break_level = self.detect_bullish_breakout(df, shift)
            if is_bull_breakout:
                bull_pattern = CandlePattern.MOMENTUM_BREAKOUT_BUY

        # Engine 3: SMC Institutional (Liquidity Sweep & Value Zone)
        is_bull_smc = False
        smc_bull_info = ""
        smc_bull_level = 0.0
        if bull_pattern == CandlePattern.NONE and getattr(self.config, 'use_smc_strategy', True):
            smc_snap = self.smc_analyzer.analyze_smc(df, shift)
            require_discount = getattr(self.config, 'smc_require_discount_premium', True)
            require_sweep = getattr(self.config, 'smc_require_sweep', False)
            
            discount_ok = (not require_discount) or smc_snap.is_discount
            sweep_ok = (not require_sweep) or smc_snap.has_ssl_sweep
            confluence_smc = smc_snap.has_ssl_sweep or smc_snap.price_percent_in_range <= 40.0
            c_bull_candle = (c0['close'] > c0['open'])
            
            if discount_ok and sweep_ok and confluence_smc and c_bull_candle:
                is_bull_smc = True
                bull_pattern = CandlePattern.SMC_INSTITUTIONAL_BUY
                smc_bull_info = smc_snap.summary_info
                smc_bull_level = min(c0['low'], df.iloc[shift - 1]['low'])

        if bull_pattern != CandlePattern.NONE:
            is_buy_breakout = (bull_pattern == CandlePattern.MOMENTUM_BREAKOUT_BUY)
            is_buy_smc = (bull_pattern == CandlePattern.SMC_INSTITUTIONAL_BUY)
            # 1. Syarat Tren:
            if is_buy_breakout or is_buy_smc:
                trend_bull = (
                    (c0['close'] > c0['ema125']) and 
                    (c0['ema8'] > c0['ema21']) and 
                    (c0['close'] > c0['ema8'])
                )
            else:
                trend_bull = (
                    (c0['ema8'] > c0['ema21']) and 
                    (c0['ema21'] > c0['ema125']) and 
                    (c0['close'] > c0['ema125']) and 
                    (c0['low'] > c0['ema125'])
                )
            if not trend_bull:
                return None

            # 2. Filter Sistem 3 Layar (Layar 1 & Layar 2)
            if use_triple and not is_buy_breakout and not is_buy_smc and not m15_buy_ok:
                return None
                
            # 3. MTF Filter
            if self.config.use_mtf_filter and not htf_bullish:
                return None
                
            # 3. Strong close di atas EMA 8
            if self.config.require_strong_close and not (c0['close'] > c0['ema8'] and c0['close'] > c0['open']):
                return None
                
            # 4. Slope EMA 8 naik
            if self.config.require_ema_slope and not (c0['ema8'] > c_prev['ema8']):
                return None
                
            # 5. Evaluasi Sistem Skor Konfluensi & Grade Kualitas
            conf_score = 100
            conf_grade = "A"
            conf_details = ""

            if is_buy_breakout:
                conf_score, conf_grade, conf_details = self.calculate_breakout_confluence_score("BUY", df, shift)
                min_score = getattr(self.config, 'min_confluence_score', 40)
                if conf_score < min_score:
                    return None
            elif is_buy_smc:
                conf_score, conf_grade, conf_details = self.calculate_smc_confluence_score("BUY", df, smc_bull_info, shift)
                min_score = getattr(self.config, 'min_confluence_score', 40)
                if conf_score < min_score:
                    return None
            elif getattr(self.config, 'use_confluence_scoring', True):
                conf_score, conf_grade, conf_details = self.calculate_confluence_score("BUY", df, shift)
                min_score = getattr(self.config, 'min_confluence_score', 60)
                if conf_score < min_score:
                    return None
            else:
                # Mode Tradisional: Semua filter tambahan wajib lolos
                if self.config.use_adx_filter and (c0['adx'] < self.config.min_adx_level):
                    return None
                res = self.structure_analyzer.validate_buy_filters(df, require_hh_hl=self.config.use_structure_filter, shift=shift)
                if res != FilterResult.PASS:
                    return None

            # Sinyal BUY Valid: Hitung SL/TP
            entry = current_ask
            sl, tp, dist = self.calculate_sl_tp("BUY", entry, df, point_size, shift, is_breakout=is_buy_breakout, is_smc=is_buy_smc, smc_level=smc_bull_level)
            
            # Proteksi Max SL: Batalkan jika jarak SL melebihi toleransi maksimal
            max_sl = getattr(self.config, 'max_sl_points', 2500)
            if dist > max_sl:
                return None

            p_name = get_pattern_name(bull_pattern)
            prefix = "Momentum Breakout" if is_buy_breakout else ("SMC Institutional" if is_buy_smc else "Bullish")
            reason_str = f"{prefix} Grade {conf_grade} ({conf_score}/100): {p_name}"
            if conf_details:
                reason_str += f" [{conf_details}]"

            return TradeSignal(
                signal_type="BUY",
                pattern=bull_pattern,
                pattern_name=p_name,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                sl_distance_points=dist,
                reason=reason_str,
                session_name=sess_name,
                news_status="CLEAN",
                confluence_score=conf_score,
                setup_grade=conf_grade,
                confluence_details=conf_details
            )

        # Sinyal SELL (Pullback, Breakout, atau SMC Institutional)
        bear_pattern = detect_bearish_pattern(df, shift)
        is_bear_breakout = False
        bear_break_level = 0.0
        if bear_pattern == CandlePattern.NONE and getattr(self.config, 'use_breakout_strategy', True):
            is_bear_breakout, bear_break_level = self.detect_bearish_breakout(df, shift)
            if is_bear_breakout:
                bear_pattern = CandlePattern.MOMENTUM_BREAKOUT_SELL

        # Engine 3: SMC Institutional (Liquidity Sweep & Value Zone)
        is_bear_smc = False
        smc_bear_info = ""
        smc_bear_level = 0.0
        if bear_pattern == CandlePattern.NONE and getattr(self.config, 'use_smc_strategy', True):
            smc_snap = self.smc_analyzer.analyze_smc(df, shift)
            require_discount = getattr(self.config, 'smc_require_discount_premium', True)
            require_sweep = getattr(self.config, 'smc_require_sweep', False)
            
            premium_ok = (not require_discount) or smc_snap.is_premium
            sweep_ok = (not require_sweep) or smc_snap.has_bsl_sweep
            confluence_smc = smc_snap.has_bsl_sweep or smc_snap.price_percent_in_range >= 60.0
            c_bear_candle = (c0['close'] < c0['open'])
            
            if premium_ok and sweep_ok and confluence_smc and c_bear_candle:
                is_bear_smc = True
                bear_pattern = CandlePattern.SMC_INSTITUTIONAL_SELL
                smc_bear_info = smc_snap.summary_info
                smc_bear_level = max(c0['high'], df.iloc[shift - 1]['high'])

        if bear_pattern != CandlePattern.NONE:
            is_sell_breakout = (bear_pattern == CandlePattern.MOMENTUM_BREAKOUT_SELL)
            is_sell_smc = (bear_pattern == CandlePattern.SMC_INSTITUTIONAL_SELL)
            # 1. Syarat Tren Lengkap Triple EMA:
            if is_sell_breakout or is_sell_smc:
                trend_bear = (
                    (c0['close'] < c0['ema125']) and 
                    (c0['ema8'] < c0['ema21']) and 
                    (c0['close'] < c0['ema8'])
                )
            else:
                trend_bear = (
                    (c0['ema8'] < c0['ema21']) and 
                    (c0['ema21'] < c0['ema125']) and 
                    (c0['close'] < c0['ema125']) and 
                    (c0['high'] < c0['ema125'])
                )
            if not trend_bear:
                return None

            # 2. Filter Sistem 3 Layar (Layar 1 & Layar 2)
            if use_triple and not is_sell_breakout and not is_sell_smc and not m15_sell_ok:
                return None
                
            # 3. MTF Filter
            if self.config.use_mtf_filter and not htf_bearish:
                return None
                
            # 3. Strong close di bawah EMA 8
            if self.config.require_strong_close and not (c0['close'] < c0['ema8'] and c0['close'] < c0['open']):
                return None
                
            # 4. Slope EMA 8 turun
            if self.config.require_ema_slope and not (c0['ema8'] < c_prev['ema8']):
                return None
                
            # 5. Evaluasi Sistem Skor Konfluensi & Grade Kualitas
            conf_score = 100
            conf_grade = "A"
            conf_details = ""

            if is_sell_breakout:
                conf_score, conf_grade, conf_details = self.calculate_breakout_confluence_score("SELL", df, shift)
                min_score = getattr(self.config, 'min_confluence_score', 40)
                if conf_score < min_score:
                    return None
            elif is_sell_smc:
                conf_score, conf_grade, conf_details = self.calculate_smc_confluence_score("SELL", df, smc_bear_info, shift)
                min_score = getattr(self.config, 'min_confluence_score', 40)
                if conf_score < min_score:
                    return None
            elif getattr(self.config, 'use_confluence_scoring', True):
                conf_score, conf_grade, conf_details = self.calculate_confluence_score("SELL", df, shift)
                min_score = getattr(self.config, 'min_confluence_score', 60)
                if conf_score < min_score:
                    return None
            else:
                # Mode Tradisional: Semua filter tambahan wajib lolos
                if self.config.use_adx_filter and (c0['adx'] < self.config.min_adx_level):
                    return None
                res = self.structure_analyzer.validate_sell_filters(df, require_lh_ll=self.config.use_structure_filter, shift=shift)
                if res != FilterResult.PASS:
                    return None

            # Sinyal SELL Valid: Hitung SL/TP
            entry = current_bid
            sl, tp, dist = self.calculate_sl_tp("SELL", entry, df, point_size, shift, is_breakout=is_sell_breakout, is_smc=is_sell_smc, smc_level=smc_bear_level)

            # Proteksi Max SL
            max_sl = getattr(self.config, 'max_sl_points', 2500)
            if dist > max_sl:
                return None

            p_name = get_pattern_name(bear_pattern)
            prefix = "Momentum Breakout" if is_sell_breakout else ("SMC Institutional" if is_sell_smc else "Bearish")
            reason_str = f"{prefix} Grade {conf_grade} ({conf_score}/100): {p_name}"
            if conf_details:
                reason_str += f" [{conf_details}]"

            return TradeSignal(
                signal_type="SELL",
                pattern=bear_pattern,
                pattern_name=p_name,
                entry_price=entry,
                stop_loss=sl,
                take_profit=tp,
                sl_distance_points=dist,
                reason=reason_str,
                session_name=sess_name,
                news_status="CLEAN",
                confluence_score=conf_score,
                setup_grade=conf_grade,
                confluence_details=conf_details
            )

        return None
