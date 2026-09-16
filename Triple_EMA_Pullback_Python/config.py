"""
Konfigurasi Parameter Robot Trading Triple EMA Pullback
Sesuai dengan arsitektur Expert Advisor MT5 (MQL5)
"""

from dataclasses import dataclass

@dataclass
class TradingConfig:
    # --- Pengaturan Simbol & Akun ---
    symbol: str = "XAUUSD"                 # Simbol trading (misal: XAUUSD, EURUSD)
    timeframe: str = "M15"                 # Timeframe eksekusi (M1, M5, M15, M30, H1, H4, D1)
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
    use_smc_discount_premium: bool = True # BUY hanya di Discount (<50%), SELL hanya di Premium (>50%)
    smc_dealing_range_bars: int = 35      # Lookback bar untuk Dealing Range (High/Low)
    use_smc_ote_strict: bool = False      # True = Wajib di Fibonacci OTE (0.618 - 0.786 Golden Pocket)
    use_smc_liquidity_sweep: bool = True  # Wajib didahului Liquidity Sweep (SSL untuk Buy, BSL untuk Sell)
    smc_sweep_lookback_bars: int = 15     # Toleransi bar ke belakang sejak sweep terjadi
    smc_pivot_lookback: int = 5           # Lookback fractal swing pivot penanda likuiditas BSL/SSL
    
    # --- Money Management & Lot Size ---
    lot_mode: str = "RISK_PERCENT"         # "FIXED" atau "RISK_PERCENT"
    fixed_lot: float = 0.01               # Ukuran lot jika lot_mode == "FIXED"
    risk_percent: float = 1.0             # Resiko per transaksi (% dari Equity)
    max_lot_size: float = 5.0             # Batas maksimal lot eksekusi
    max_open_positions: int = 1           # Maksimal posisi terbuka bersamaan
    
    # --- Stop Loss & Take Profit ---
    sl_mode: str = "SWING_CANDLE"         # "SWING_CANDLE", "ATR_BASED", atau "FIXED_POINTS"
    swing_lookback_bars: int = 6          # Lookback bar untuk swing high / swing low (default: 6 bar)
    sl_atr_multiplier: float = 1.5        # Multiplier ATR jika sl_mode == "ATR_BASED"
    sl_fixed_points: int = 300            # Points SL jika sl_mode == "FIXED_POINTS"
    sl_buffer_points: int = 50            # Buffer pips di bawah swing low / di atas swing high
    risk_reward_ratio: float = 2.0        # Target Take Profit penuh (misal 1:2.0)
    min_sl_points: int = 150              # Proteksi SL minimal (150 pts = $1.50 di Gold)
    max_sl_points: int = 2500             # Proteksi SL maksimal (2500 pts = $25.00 di Gold, batalkan entry jika SL melebihi batas ini)
    
    # --- Proteksi Profit: Partial Close, Break-Even & Trailing Stop ---
    use_partial_close: bool = True        # Ambil profit sebagian (Scale-Out) di target tertentu
    partial_close_rr: float = 1.0         # Target Partial TP saat profit mencapai 1:1.0 R:R
    partial_close_percent: float = 50.0   # Persentase lot yang ditutup saat Partial TP (misal 50%)

    use_break_even: bool = True           # Pindahkan SL ke Entry saat mencapai target tertentu
    be_trigger_rr: float = 1.0            # Trigger BEP saat keuntungan mencapai 1:1.0 R:R (setelah / bersama Partial TP)
    be_lock_profit_points: int = 20       # Points profit yang dikunci di atas/bawah harga open
    
    use_trailing_stop: bool = True        # Aktifkan Trailing Stop
    trailing_start_rr: float = 1.4        # Trailing baru aktif setelah profit >= 1:1.4 R:R
    trailing_by_ema21: bool = True        # Trailing mengikuti garis EMA 21
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
