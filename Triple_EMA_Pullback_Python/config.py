"""
Konfigurasi Parameter Robot Trading Triple EMA Pullback
Sesuai dengan arsitektur Expert Advisor MT5 (MQL5)
"""

from dataclasses import dataclass

@dataclass
class TradingConfig:
    # --- Pengaturan Simbol & Akun ---
    symbol: str = "XAUUSD"                 # Simbol trading (misal: XAUUSD, EURUSD)
    timeframe: str = "M5"                  # Timeframe eksekusi (M1, M5, M15, M30, H1, H4, D1)
    magic_number: int = 8821125            # ID Unik Robot
    order_comment: str = "TripleEMA_PyBot" # Komentar pada order
    
    # --- Indikator Moving Average ---
    ema_fast_period: int = 8              # EMA 8 (Fast Momentum)
    ema_med_period: int = 21              # EMA 21 (Dynamic Support/Resistance / Value Zone)
    ema_slow_period: int = 125            # EMA 125 (Major Baseline Trend)
    
    # --- Indikator ATR & ADX ---
    atr_period: int = 14                  # Periode Average True Range
    adx_period: int = 14                  # Periode Average Directional Index
    use_adx_filter: bool = True           # Filter kekuatan tren
    min_adx_level: float = 20.0           # Batas minimal ADX (di bawah 20 = pasar sideways flat)
    
    # --- Sistem 3 Layar / Triple Screen (H1 -> M15 -> M5) ---
    use_triple_screen: bool = True        # Aktifkan Sistem 3 Layar (H1 Macro Bias -> M15 Structure -> M5 Trigger)
    screen1_timeframe: str = "H1"         # Layar 1: Timeframe Tren Besar Institusi (Macro Bias H1)
    screen1_ema_period: int = 50          # Layar 1: Periode EMA Tren Besar Macro
    screen2_timeframe: str = "M15"        # Layar 2: Timeframe Struktur Pasar & Ayunan M15
    screen2_ema_period: int = 50          # Layar 2: Periode EMA Level Kunci M15
    screen2_require_structure: bool = False# Layar 2: Wajib Konfirmasi Struktur Ayunan (False agar tidak memblokir momentum breakout)
    screen2_require_key_level: bool = True# Layar 2: Wajib Konfirmasi Level Kunci EMA M15

    # --- Sistem Skor Probabilitas & Konfluensi (Confluence Scoring) ---
    use_confluence_scoring: bool = True   # Aktifkan Sistem Skor Konfluensi (Anti Lagging Entry)
    min_confluence_score: int = 40        # Ambang batas minimal skor entri (60=Grade A, 80=Grade A+, 40=Grade B/Breakout)
    use_dynamic_grade_sizing: bool = False# Sizing lot dinamis berbasis Grade (A+=100%, A=75%, B=50%)
    score_weight_fibo: int = 20           # Bobot Skor: Fibonacci Golden Zone (50%-78.6%)
    score_weight_rsi: int = 20            # Bobot Skor: RSI Momentum Sehat (45-70 Buy / 30-55 Sell)
    score_weight_fvg: int = 20            # Bobot Skor: Mitigasi Fair Value Gap (FVG)
    score_weight_adx: int = 20            # Bobot Skor: ADX Trend Strength (>= 20)
    score_weight_structure: int = 20      # Bobot Skor: Struktur Ayunan HH-HL / LH-LL
    
    # --- Filter Multi-Timeframe (HTF) ---
    use_mtf_filter: bool = True           # Filter tren skala besar
    htf_timeframe: str = "H1"             # Timeframe macro (Default: H1)
    htf_ema_period: int = 50              # Periode EMA di HTF
    
    # --- Filter False Signal & Anti-Spam ---
    signal_cooldown_bars: int = 5         # Jeda minimal antar sinyal (candle)
    require_strong_close: bool = True     # Wajib Close menembus & menutup di sisi EMA 8
    require_ema_slope: bool = True        # Wajib Slope EMA 8 searah tren
    use_structure_filter: bool = True     # Validasi struktur HH/HL (Buy) atau LH/LL (Sell)
    fractal_lookback: int = 50            # Lookback fractal swing
    
    use_chop_filter: bool = True          # Filter persilangan EMA 8 & 21 berulang-ulang
    chop_bars: int = 15                   # Lookback bar cek chop
    max_ema_crosses: int = 2              # Maksimal silang EMA 8 & 21 dalam lookback
    
    use_whipsaw_filter: bool = True       # Filter penembusan EMA 125 berulang-ulang
    whipsaw_bars: int = 20                # Lookback bar cek whipsaw EMA 125
    max_whipsaw_crosses: int = 2          # Maksimal penembusan EMA 125
    
    use_overextend_filter: bool = True    # Filter jarak candle terlalu jauh dari EMA
    max_atr_multiplier: float = 2.0       # Toleransi jarak harga ke EMA 8 (x ATR)
    
    # --- Support & Resistance (SNR) Dinamis & Obstacle Filter ---
    use_snr_filter: bool = True           # Aktifkan modul Support & Resistance
    snr_major_lookback: int = 20          # Lookback pivot Major S/R
    snr_minor_lookback: int = 8           # Lookback pivot Minor S/R
    snr_obstacle_filter: bool = True      # Tolak order jika terhalang Major S/R sebelum target 1:1 R
    snr_min_clearance_rr: float = 1.0     # Jarak minimal ruang bebas ke rintangan S/R (x R:R)
    snr_require_bounce_confluence: bool = False # True = Wajib pantulan persis di zona Support/RBS (Ketat)
    
    # --- Smart Money Concepts (SMC) & Liquidity Filter ---
    use_smc_filter: bool = True           # Master switch filter SMC (Discount/Premium & Sweep)
    use_smc_discount_premium: bool = False # False = Izinkan pullback sehat di zona EMA; True = Wajib di Discount (<50%)
    smc_dealing_range_bars: int = 35      # Lookback bar untuk Dealing Range (High/Low)
    use_smc_ote_strict: bool = False      # True = Wajib di Fibonacci OTE (0.618 - 0.786 Golden Pocket)
    use_smc_liquidity_sweep: bool = False  # True = Wajib didahului Liquidity Sweep (SSL untuk Buy, BSL untuk Sell)
    smc_sweep_lookback_bars: int = 15     # Toleransi bar ke belakang sejak sweep terjadi
    smc_pivot_lookback: int = 5           # Lookback fractal swing pivot penanda likuiditas BSL/SSL
    
    # --- Money Management & Lot Size ---
    lot_mode: str = "RISK_PERCENT"         # "FIXED" atau "RISK_PERCENT" (Rekomendasi: RISK_PERCENT)
    fixed_lot: float = 0.10                # Ukuran lot jika lot_mode == "FIXED"
    risk_percent: float = 1.0             # Resiko per transaksi (% dari Equity)
    max_lot_size: float = 5.0             # Batas maksimal lot eksekusi
    max_open_positions: int = 1           # Maksimal posisi terbuka bersamaan (Live/Demo)
    
    # --- Stop Loss & Take Profit ---
    sl_mode: str = "SWING_CANDLE"         # "SWING_CANDLE", "ATR_BASED", atau "FIXED_POINTS"
    swing_lookback_bars: int = 6          # Lookback bar untuk swing high / swing low (default: 6 bar)
    sl_atr_multiplier: float = 1.5        # Multiplier ATR jika sl_mode == "ATR_BASED"
    sl_fixed_points: int = 300            # Points SL jika sl_mode == "FIXED_POINTS"
    sl_buffer_points: int = 50            # Buffer pips di bawah swing low / di atas swing high
    risk_reward_ratio: float = 2.0        # Target Take Profit penuh (misal 1:2.0)
    min_sl_points: int = 300              # Proteksi SL minimal (300 pts = $3.00 di Gold)
    max_sl_points: int = 1500             # Proteksi SL maksimal (1500 pts = $15.00 di Gold, akomodir volatilitas wajar XAUUSD)
    xau_min_sl_atr_mult: float = 1.0      # SL adaptif volatilitas Emas: minimal 1.0x ATR M15

    # --- Filter Fundamental & Shock Volatilitas Berita XAUUSD ---
    use_fundamental_shock_filter: bool = True     # Deteksi lilin lonjakan berita abnormal (News Spike Trap)
    fundamental_shock_atr_multiplier: float = 2.5 # Ambang lilin lonjakan (x ATR)
    fundamental_shock_cooldown_bars: int = 4      # Jeda bar setelah terjadi shock volatilitas berita
    use_news_window_filter: bool = False          # Filter jam rilis data ekonomi krusial AS (NFP, CPI, FOMC)
    news_window_hours: tuple = (13, 14, 19, 20)   # Jam server broker saat data makro AS rilis
    xau_session_filter: str = "LONDON_NY"         # "ALL" atau "LONDON_NY" (eliminasi fakeout Sesi Asia)

    # --- Filter Volume Transaksi Lilin (Smart Money Volume) ---
    use_volume_filter: bool = True                # Wajib Volume Lilin Setup Valid (Diatas Rata-rata)
    volume_lookback: int = 20                     # Lookback Rata-rata Volume (SMA 20)
    volume_multiplier: float = 1.0                # Minimal Volume Setup (x Rata-rata Volume)

    # --- Mode Backtest & Analisis False Signal ---
    backtest_mode: str = "UNCONSTRAINED"          # "UNCONSTRAINED" (evaluasi semua sinyal) atau "SINGLE_POSITION"
    backtest_max_open_positions: int = 0          # 0 = Bebas / Unlimited, >0 = Batasi posisi simultan
    backtest_ignore_cooldown: bool = True         # True = Abaikan jeda candle agar semua sinyal diuji
    false_signal_mfe_threshold: float = 0.5       # Ambang MFE R (loss dengan MFE < 0.5R = False Signal / Fakeout)

    # --- Strategi Tambahan: Momentum Breakout ---
    use_breakout_strategy: bool = True            # Aktifkan Strategi Momentum Breakout
    breakout_lookback_bars: int = 15              # Lookback Bar Konsolidasi / Range Breakout
    breakout_min_body_ratio: float = 0.50         # Minimal Rasio Body Candle Penembus (50%)
    breakout_require_volume: bool = True          # Wajib Konfirmasi Lonjakan Volume
    breakout_vol_multiplier: float = 1.1          # Pengali Volume Minimal (1.1x Rata-rata)

    # --- Strategi Tambahan: Smart Money Concepts (SMC Institutional) ---
    use_smc_strategy: bool = True                 # Aktifkan Strategi SMC Institutional (Engine 3)
    smc_require_discount_premium: bool = True     # Wajib di Zona Discount (Buy) / Premium (Sell)
    smc_require_sweep: bool = False               # Wajib Ada Liquidity Sweep (SSL/BSL Grab)

    # --- Filter Tambahan: Fibonacci Golden Pocket (OTE) ---
    use_fibo_golden_zone: bool = True             # Pullback masuk ke zona Discount/Golden Zone (0.50 - 0.786)
    fibo_lookback_bars: int = 30                  # Lookback swing impulse Fibonacci
    fibo_min_retrace: float = 0.236               # Minimal retracement (23.6% Shallow Pullback di Momentum Kuat)
    fibo_max_retrace: float = 0.786               # Maksimal retracement (78.6% Deep OTE)

    # --- Filter Tambahan: RSI Momentum & Divergence ---
    use_rsi_filter: bool = True                   # Filter momentum sehat RSI
    rsi_period: int = 14                          # Periode RSI
    rsi_buy_min: float = 45.0                     # Minimal RSI untuk Buy (Momentum naik)
    rsi_buy_max: float = 70.0                     # Maksimal RSI untuk Buy (Bukan pucuk overbought)
    rsi_sell_min: float = 30.0                    # Minimal RSI untuk Sell (Bukan lembah oversold)
    rsi_sell_max: float = 55.0                    # Maksimal RSI untuk Sell (Momentum turun)
    use_rsi_divergence: bool = False              # Opsi konfirmasi Hidden/Regular Divergence

    # --- Filter Tambahan: Fair Value Gap (FVG / Imbalance) ---
    use_fvg_filter: bool = False                  # Opsi konfirmasi mitigasi area FVG
    fvg_lookback_bars: int = 10                   # Lookback deteksi FVG
    
    # --- Proteksi Profit: Partial Close, Break-Even & Trailing Stop ---
    use_partial_close: bool = True        # Ambil profit sebagian (Scale-Out) di target tertentu
    partial_close_rr: float = 1.0         # Target Partial TP saat profit mencapai 1:1.0 R:R
    partial_close_percent: float = 50.0   # Persentase lot yang ditutup saat Partial TP (misal 50%)

    use_break_even: bool = True           # Pindahkan SL ke Entry saat mencapai target tertentu
    be_trigger_rr: float = 1.5            # Trigger BEP saat keuntungan mencapai 1:1.5 R:R
    be_lock_profit_points: int = 30       # Points profit yang dikunci di atas/bawah harga open
    
    # --- Trailing Stop Dinamis ---
    use_trailing_stop: bool = False       # Dimatikan agar target 1:2 R:R tercapai penuh
    trailing_start_rr: float = 1.8        # Trailing baru aktif setelah profit >= 1:1.8 R:R
    trailing_by_ema21: bool = False       # Trailing mengikuti garis EMA 21
    trailing_atr_mult: float = 1.5        # Trailing jarak ATR jika trailing_by_ema21 == False
    
    # --- Circuit Breaker: Batasan Kerugian Harian ---
    use_daily_loss_limit: bool = True     # Batasi kerugian harian
    max_daily_losses: int = 2             # Maksimal jumlah trade loss per hari
    max_daily_loss_percent: float = 3.0   # Maksimal akumulasi kerugian harian (% dari Equity)
    
    # --- Filter Jam Trading & Spread ---
    use_time_filter: bool = True          # Batasi jam trading
    time_filter_use_server_time: bool = True # True = jam server broker (rekomendasi), False = jam lokal PC
    start_hour: int = 8                   # Jam mulai (Sesi London)
    end_hour: int = 21                    # Jam akhir (Sesi New York)
    max_spread_points: int = 40           # Toleransi spread maksimal dalam points
    
    # --- Proteksi Gap Akhir Pekan (Friday Auto-Close) ---
    use_friday_close: bool = True         # Tutup semua posisi sebelum akhir pekan
    friday_close_hour: int = 21           # Jam auto-close Jumat
    friday_close_minute: int = 30         # Menit auto-close Jumat
    block_friday_new_trades: bool = True  # Blokir sinyal baru mulai Jumat sore
    friday_stop_trade_hour: int = 18      # Jam mulai blokir entri baru di hari Jumat
    
    # --- Data History & Polling Rate ---
    history_bars_count: int = 350         # Jumlah candle untuk kalkulasi indikator (agar EMA 125 stabil)
    tick_interval_sec: float = 1.0        # Interval pengecekan posisi & harga (detik)
