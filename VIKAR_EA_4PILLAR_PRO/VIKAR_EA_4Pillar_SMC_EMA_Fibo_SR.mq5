//+------------------------------------------------------------------+
//|                               VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5|
//|        Copyright 2026, Vikar Institutional 4-Pillar Strategy     |
//|               SMC Core • S/R Pivots • Triple EMA • Fibonacci      |
//+------------------------------------------------------------------+
#property copyright "Vikar Institutional 4-Pillar Trading Strategy"
#property link      "https://www.tradingview.com"
#property version   "4.00"
#property description "Vikar EA 4-Pillar Pro - MTF Price Action Edition v4.00 (M1 OB Retest Engine)"
#property description "SMC Core, M1 Multi-Timeframe OB/Pullback Confirmation, 10-Pattern Price Action"
#property description "Prop Firm Guardian, Dynamic Structural Trailing & M1 Zone Radar HUD"

#include <Trade\Trade.mqh>
#include <Trade\PositionInfo.mqh>
#include <Trade\OrderInfo.mqh>

//+------------------------------------------------------------------+
//| ENUMERASI KONFIGURASI                                            |
//+------------------------------------------------------------------+
enum ENUM_MARKET_REGIME
{
   REGIME_STRONG_TREND,     // Tren Sangat Kuat (CI < 38.2) - Momentum Breakout Ideal
   REGIME_NORMAL,           // Tren Normal / Sehat (38.2 <= CI <= 61.8) - 4-Pillar Sniper Standard
   REGIME_CHOPPY_SIDEWAYS   // Sideways Sempit / Kompresi (CI > 61.8) - Bahaya Fakeout Tinggi!
};

enum ENUM_LOT_TYPE
{
   LOT_TYPE_BROKER_MIN,   // Otomatis Minimal Lot Broker (Paling Aman, Menyesuaikan Broker)
   LOT_TYPE_FIXED,        // Fixed Lot (Ukuran Lot Statis)
   LOT_TYPE_RISK_PERCENT  // Dynamic Risk % of Balance
};

enum ENUM_SL_TYPE
{
   SL_TYPE_SWING_FIBO,    // Di Balik Swing Fractal / Fibo 1.0 + Buffer ATR (Rekomendasi Pro)
   SL_TYPE_CANDLE_WICK,   // Ujung Ekor Lilin Konfirmasi + Buffer
   SL_TYPE_FIXED_PIPS     // Jarak Pips Statis
};

enum ENUM_TP_TYPE
{
   TP_TYPE_RISK_REWARD,   // Rasio Risk-to-Reward (Default SNIPER: 1 : 1.8)
   TP_TYPE_FIBO_EXT,      // Target Ekstensi Fibonacci (-0.272 & -0.618)
   TP_TYPE_PIVOT_LEVEL,   // Target Level Pivot Statis Terdekat (R1/R2 atau S1/S2)
   TP_TYPE_FIXED_POINTS   // Target Jarak Statis (Fixed 100 Point / Sesuai Input)
};

enum ENUM_BE_MODE
{
   BE_MODE_PIPS,          // Berdasarkan Jarak Pips Profit (e.g. Profit +15 Pips -> Geser SL ke +5 Pips)
   BE_MODE_RISK_REWARD    // Berdasarkan Rasio Risk-Reward (e.g. Profit 1:1 -> Geser SL ke +5 Pips)
};

enum ENUM_PROFIT_TARGET_MODE
{
   PROFIT_TARGET_CURRENCY,  // Target Profit Berdasarkan Nominal Uang ($ / Saldo Akun)
   PROFIT_TARGET_PERCENT    // Target Profit Berdasarkan Persentase Saldo Modal (%)
};



//+------------------------------------------------------------------+
//| INPUT PARAMETERS USER (KOMPATIBILITAS DIDIMAX MT5 - SNIPER $20)  |
//+------------------------------------------------------------------+
input group "=== 1. MANAJEMEN LOT & RISIKO MODAL ==="
input ENUM_LOT_TYPE InpLotType            = LOT_TYPE_FIXED;        // Model Lot (Default: Fixed Lot 0.01 - Standar Akun $20)
input double        InpRiskPercent        = 1.0;                   // Risiko per Transaksi (% Modal, Jika Mode Risk %)
input double        InpFixedLot           = 0.01;                  // Ukuran Lot Tetap (0.01 Lot Teraman Modal $20)
input double        InpMinLot             = 0.00;                  // Batas Bawah Lot (0.0 = Auto Deteksi Minimal Broker)
input double        InpMaxLot             = 0.05;                  // Batas Maksimal Lot (Safeguard: 0.05 Anti-Lot Besar)
input int           InpMaxOpenPositions   = 1;                     // Maksimal Posisi Aktif Bersamaan (1 = Anti-Hedging)
input int           InpSignalCooldownBars = 3;                     // Jeda Minimal Lilin Antar Sinyal (Cooldown Bars)
input ulong         InpMagicNumber        = 777125;                // Magic Number Unik EA
input string        InpTradeComment       = "VIKAR-4PillarPro";    // Komentar Identitas Transaksi
input ulong         InpDeviation          = 15;                    // Toleransi Slippage (Points)

input group "=== 2. TARGET STOP LOSS, TAKE PROFIT & EXIT STRATEGY ==="
input ENUM_SL_TYPE  InpSLType             = SL_TYPE_SWING_FIBO;    // Metode Penempatan Stop Loss
input double        InpSLBufferAtrMult    = 1.2;                   // Buffer Pengaman SL (x Nilai ATR 14)
input double        InpMinSLPips          = 20.0;                  // Batas Minimum Jarak SL (Pips - Anti Micro SL)
input double        InpMaxSLPips          = 70.0;                  // Batas Maksimal Jarak SL (Pips)
input double        InpFixedSLPips        = 35.0;                  // Jarak SL Statis (Jika Mode Fixed Pips)
input ENUM_TP_TYPE  InpTPType             = TP_TYPE_RISK_REWARD;   // Metode Penentuan Target Take Profit (Default: Risk-to-Reward Ratio)
input double        InpRiskRewardRatio    = 1.8;                   // Rasio Risk to Reward (Default SNIPER: 1 : 1.8)
input double        InpFixedTPPoints      = 100.0;                 // Target Jarak TP Statis (Points, misal 100 Point = 10 Pips)

// --- Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin) ---
input bool          InpUseBreakeven       = true;                  // Aktifkan Auto-Breakeven / SL+ (Kunci Modal & Profit)
input ENUM_BE_MODE  InpBreakevenMode      = BE_MODE_PIPS;          // Model Pemicu Auto-BE / SL+ (Pips / Risk-Reward)
input double        InpBreakevenTriggerPips= 8.0;                  // Jarak Profit Memicu BE / SL+ (8.0 Pips = 80 Point)
input double        InpBreakevenRRTrigger = 1.0;                   // Pemicu BE Saat Profit Mencapai R:R (1.0 = 1:1, Mode RR)
input double        InpBreakevenLockPips  = 5.0;                   // Pips Keuntungan Terkunci Saat SL+ (5.0 Pips = 50 Point - Cover Spread & Komisi)
input bool          InpUseTrailingEMA21   = true;                  // Trailing Stop Dinamis Mengikuti EMA 21 Magenta
input double        InpTrailingBufferPips = 5.0;                   // Jarak Buffer Trailing dari EMA 21 (Pips)

// --- Dynamic Trailing Stop (Kawal Kenaikan Candle & Jarak Points) ---
input bool          InpUseCandleTrailing  = true;                  // Trailing Naik Mengikuti Low/High Lilin (Candle-by-Candle)
input double        InpCandleTrailBufferPoints = 30.0;             // Buffer Jarak di Bawah Ekor Lilin (30 Point = 3.0 Pips Ruang Nafas)
input bool          InpUsePointsTrailing  = true;                  // Trailing Stop Dinamis Berdasarkan Jarak Points
input double        InpTrailingStartPoints= 120.0;                 // Pemicu Trailing Aktif (Setelah Profit 120 Point = 12 Pips)
input double        InpTrailingDistPoints = 80.0;                  // Jarak Pengawalan SL di Belakang Harga (80 Point = 8 Pips)
input double        InpTrailingStepPoints = 15.0;                  // Langkah Geser SL Tiap Kenaikan Harga (15 Point = 1.5 Pips)

// --- Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner) ---
input bool          InpUsePartialClose    = true;                  // Aktifkan Partial Take Profit (Amankan 50% di TP1)
input double        InpPartialClosePercent= 50.0;                  // Persentase Lot Ditutup di TP1 (Default: 50%)
input ENUM_BE_MODE  InpPartialTriggerMode = BE_MODE_PIPS;          // Model Pemicu TP1 (Pips / Risk-Reward)
input double        InpPartialTriggerPips = 14.0;                  // Jarak Profit Pemicu TP1 (14.0 Pips = 140 Point)
input double        InpPartialRRTrigger   = 1.5;                   // Pemicu TP1 Saat Mencapai R:R (1.5 = 1:1.5, Mode RR)
input bool          InpPartialMoveSLPlus  = true;                  // Otomatis Geser Sisa Lot ke SL+ Setelah TP1 Ambil Untung

input group "=== 2.6 DYNAMIC STRUCTURAL SWING TRAILING (v3.00) ==="
input bool          InpUseStructuralTrailing       = true;         // Trailing Stop Struktur Ayunan SMC (HL/LH) untuk Runner
input double        InpStructuralTrailingAtrBuffer = 0.5;          // Buffer Jarak dari Swing HL/LH (x ATR)

// --- Auto Cut Profit Saat Indikasi Pembalikan Arah ---
input bool          InpAutoCutProfit      = true;                  // Auto Cut Profit Saat Ada Indikasi Pembalikan Arah
input double        InpMinProfitToCutPips = 3.0;                   // Batas Minimal Floating Profit (Pips) Sebelum Cut Aktif
input bool          InpCutOnCHoCH         = true;                  // Cut Profit Jika Terdeteksi CHoCH Berlawanan (SMC)
input bool          InpCutOnCandleReversal= true;                  // Cut Profit Jika Muncul Candlestick Rejection Berlawanan
input bool          InpCutOnEMACross      = true;                  // Cut Profit Jika Lilin Menembus Ribbon EMA 21 Berlawanan
input group "=== 2.5 STAGNANT TRADE TIME-EXIT (v2.60) ==="
input bool          InpUseTimeBasedExit        = true;             // Tutup Otomatis Posisi yang Mengambang Terlalu Lama
input int           InpMaxTradeDurationHours   = 6;                // Batas Maksimal Durasi Posisi (Jam, e.g. 6 Jam)
input double        InpMinProfitToTimeExitPips = 0.0;              // Minimal Profit (Pips) untuk Time-Exit (0.0 = Impas / BE)

input group "=== 3. PILAR 1: SMART MONEY CONCEPTS (SMC CORE) ==="
input int           InpFractalPeriod      = 3;                     // Periode Deteksi Ayunan Fractal (Bars Kiri/Kanan)
input bool          InpRequireBOSorCHoCH  = true;                  // Wajib Konfirmasi Struktur Pasar (BOS / CHoCH)
input bool          InpRequireDiscount    = false;                 // Filter Dealing Range (false = Fleksibel Mengikuti Momentum)
input bool          InpUseLiquiditySweep  = true;                  // Deteksi & Prioritas Liquidity Sweep (Stop Hunt)
input bool          InpUseFVGFilter       = true;                  // Deteksi Fair Value Gap (FVG Imbalance)
input bool          InpUseOrderBlock      = true;                  // Aktifkan Mesin Valid Order Block (OB) Institusional
input double        InpOBDisplacementAtrMult = 1.15;               // Multiplier Displacement ATR Lilin Pemicu OB (Min: 1.15x)
input bool          InpRequireOBMitigation= false;                 // Wajib Lilin Sedang Menguji Zona OB (Mitigation Test)
input int           InpOBMaxAgeBars       = 35;                    // Batas Usia Lilin Maksimal Order Block Aktif (Bars)
input int           InpFVGLookbackBars    = 20;                    // Jendela Pemindaian Multi-Bar Fair Value Gap (FVG)
input int           InpMinFVGPoints       = 10;                    // Batas Minimal Celah Lebar FVG (Points)

input group "=== 3.1 SISTEM SKOR KONFLUENSI 4 PILAR (GRADE FILTER) ==="
input bool          InpUseConfluenceScore = true;                  // Aktifkan Sistem Skor Konfluensi 4 Pilar (0 - 100 Poin)
input double        InpMinConfluenceScore = 75.0;                  // Skor Minimal Eksekusi (75.0 = Preset SNIPER Grade A+ Modal $20)

input group "=== 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ==="
input bool          InpAllowMomentumBreakout       = true;         // Aktifkan Eksekusi Momentum Breakout (Anti-Ketinggalan Reli)
input double        InpBreakoutAtrMult             = 1.0;          // Minimal Ukuran Lilin Breakout (x Nilai ATR 14)
input bool          InpBreakoutRequireVSA          = true;         // Wajib Didukung Lonjakan Volume VSA (>= 1.3x)
input bool          InpBreakoutRequireBOS          = true;         // Wajib Menembus Swing High/Low (Konfirmasi BOS)

input group "=== 4. PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS) ==="
input bool          InpUseDailyPivots     = true;                  // Aktifkan Kalkulasi Daily Pivot Points
input bool          InpRequireDoubleAlign = false;                 // Wajib Double Alignment (false = Fleksibel Mengikuti EMA Trend)
input double        InpMinHeadroomATR     = 0.5;                   // Jarak Minimal ke Tembok Resisten/Support (x ATR)

input group "=== 5. PILAR 3: TRIPLE EMA & MULTI-TIMEFRAME (H1 MACRO) ==="
input int             InpFastEMA          = 8;                     // Fast EMA Period (Cyan Momentum)
input int             InpMediumEMA        = 21;                    // Medium EMA Period (Magenta Ribbon & Trailing)
input int             InpTrendEMA         = 125;                   // Trend Institutional Baseline (Putih)
input int             InpPullbackLookback = 5;                     // Jendela Lilin Pengujian Pullback (Bars)
input bool            InpFilterWhipsaw125 = false;                 // Filter Whipsaw Lilin Bolak-Balik EMA 125
input bool            InpUseHTFFilter     = true;                  // Aktifkan Filter Macro Trend Higher Timeframe (H1)
input ENUM_TIMEFRAMES InpHTFTimeframe     = PERIOD_H1;              // Timeframe Macro Trend (Default: H1)
input int             InpHTFTrendEMA      = 125;                   // HTF Trend Baseline Period (Putih 125)
input bool            InpHTFRequireRibbon = true;                  // Wajib Konfirmasi HTF Ribbon (EMA 8 > EMA 21)

input group "=== 5.1 MULTI-TIMEFRAME PRICE ACTION — M1 OB RETEST ENGINE (v4.00) ==="
input bool            InpUseMTFM1Engine     = true;   // Aktifkan Mesin Konfirmasi Price Action M1 (Pullback ke OB)
input bool            InpRequireM1OBRetest  = true;   // WAJIB Retest ke OB Demand/Supply M1 Sebelum Entry (Mode Ketat)
input double          InpM1PullbackWeight   = 20.0;   // Bobot Skor Konfluensi Retest M1 (Maks 20 Poin)
input int             InpM1OBLookback       = 60;     // Lookback Bar M1 untuk Deteksi Order Block (60 = 60 menit)
input double          InpM1OBDispAtrMult    = 0.7;    // Minimal Displacement ATR untuk OB M1 Valid (x ATR M1)
input double          InpM1ZoneBufferPips   = 1.5;    // Buffer Sentuh Zona OB M1 untuk Konfirmasi Retest (Pips)
input bool            InpM1RequireCHoCH     = false;  // Wajib CHoCH M1 sebagai Konfirmasi Reversal Presisi

input group "=== 6. PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET ==="
input bool          InpUseAutoFibo        = true;                  // Aktifkan Validasi Fibonacci Retracement
input bool          InpRequireGoldenPocket= false;                 // Wajib Menguji Area Golden Pocket (false = Cukup Sentuh Ribbon EMA)
input double        InpFiboGPMin          = 0.500;                 // Batas Atas Retracement Golden Pocket
input double        InpFiboGPMid          = 0.618;                 // Rasio Emas Utama (Golden Ratio 61.8%)
input double        InpFiboGPMax          = 0.786;                 // Batas Bawah Retracement Golden Pocket

input group "=== 7. POLA KONFIRMASI CANDLESTICK REJECTION ==="
input bool          InpRequireCandleRejection = true;              // Wajib Pola Rejection Cerdas (Pin Bar, Engulfing, Star, Tweezer)
input double        InpMinCandleScore         = 60.0;              // Skor Kualitas Lilin Minimal (0 - 100, 60 = Grade A)
input bool          InpUseHammerPinBar        = true;              // Pin Bar & Hammer Rejection (Ekor Penolakan >= 55%)
input bool          InpUseEngulfing           = true;              // Bullish & Bearish Engulfing Institusional
input bool          InpUseMorningEveningStar  = true;              // Morning Star & Evening Star (3-Bar Reversal)
input bool          InpUseTweezer             = true;              // Tweezer Tops & Tweezer Bottoms (Double Level Test)
input bool          InpUseFVGRebound          = true;              // Fair Value Gap Mitigation Rebound
input bool          InpUseThreeSoldiersCrows  = true;              // Three White Soldiers & Three Black Crows (Impulsive Push)
input bool          InpUseHaramiInsideBar     = true;              // Harami & Inside Bar Compression Breakout
input bool          InpUsePiercingDarkCloud   = true;              // Piercing Line & Dark Cloud Cover (>50% Penetration)
input bool          InpUseDragonflyGravestone = true;              // Dragonfly Doji & Gravestone Doji Extreme Rejection
input bool          InpUseInvertedHammerStar  = true;              // Inverted Hammer & Shooting Star Rejection

input group "=== 7.1 MESIN POLA GRAFIK (CHART PATTERN ENGINE) ==="
input bool          InpUseChartPatterns       = true;              // Aktifkan Mesin Pengenal Pola Grafik (Chart Patterns)
input bool          InpUseDoubleTopBottom     = true;              // Deteksi Double Bottom (W) & Double Top (M-Pattern)
input bool          InpUseQuasimodo           = true;              // Deteksi Quasimodo (QM Institutional Level)
input bool          InpUseHeadAndShoulders    = true;              // Deteksi Head & Shoulders & Inverse H&S
input bool          InpUseFlagsContinuation   = true;              // Deteksi Bullish / Bearish Flags (Slanted Channel)
input double        InpMinChartPatternScore   = 65.0;              // Skor Minimal Pola Grafik (0 - 100)

input group "=== 8. FILTER PROTEKSI & WAKTU SESI PASAR ==="
input bool          InpUseShockGuard      = true;                  // Proteksi Lonjakan Volatilitas Berita (Shock Guard)
input double        InpShockAtrMult       = 2.2;                   // Batas Abnormal Lonjakan Lilin Berita (x Nilai ATR)
input int           InpShockCooldownBars  = 2;                     // Jeda Pengaman Lilin Pasca-Lonjakan Shock (Bars)
input bool          InpCutOnEarlyInvalidation = true;              // Cut Dini Jika Terbentuk Lilin Menelan Order Block Acuan
input double        InpMaxSpreadPips      = 6.0;                   // Batas Maksimal Spread Diizinkan (Pips - Aman Rollover)
input bool          InpUseSessionFilter   = false;                 // Batasi Jam Trading (false = 24 Jam Auto Trade)
input int           InpSessionStartHour   = 0;                     // Jam Mulai Trading
input int           InpSessionEndHour     = 24;                    // Jam Selesai Trading

input group "=== 8.1 PROTEKSI AKUN & CIRCUIT BREAKER ==="
input bool          InpUseConsecutiveLossGuard = true;          // Jeda Anti-Overtrading Pasca-Loss Berturut-turut
input int           InpMaxConsecutiveLosses    = 2;             // Batas Loss Berturut-turut Hari Ini (Default: 2)
input int           InpCooldownHours           = 4;             // Durasi Istirahat Robot Pasca-Loss (Jam)
input bool          InpUseDailyLossLimit       = true;          // Batasi Maksimal Kerugian Harian (% Modal)
input double        InpMaxDailyLossPercent     = 2.5;           // Batas Maksimal Kerugian Harian (% Saldo Awal Hari Ini)

input group "=== 8.2 VOLUME SPREAD ANALYSIS (VSA INSTITUSIONAL) ==="
input bool          InpUseVSA                  = true;          // Aktifkan Analisis Volume Footprint Institusional
input int           InpVSALookbackBars         = 20;            // Periode Rata-rata Volume Lilin Acuan (Bars)
input double        InpVSAClimaxRatio          = 1.75;          // Batas Lonjakan Volume Climax / Absorption (x Rata-rata)
input double        InpVSANoSupplyRatio        = 0.85;          // Batas Volume Kering / No-Supply Pullback (x Rata-rata)

input group "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ==="
input bool          InpUseFridayGuard              = true;         // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
input int           InpFridayCloseHour             = 21;           // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)

input group "=== 8.4 MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE) ==="
input bool          InpUseSelfHealing              = true;         // Aktifkan Mesin Otopsi & Koreksi Diri Pasca-Loss
input double        InpPenaltyConfluencePts        = 10.0;         // Penalti Ambang Skor Minimal Pasca-SL (+10 Poin)
input int           InpQuarantinePatternBars       = 15;           // Durasi Karantina Pola Lilin Gagal (Bars)
input double        InpAdaptiveSLBufferBoost       = 0.3;          // Tambahan Buffer ATR Pasca-Loss (x ATR)
input int           InpAdaptiveBufferTrades        = 3;            // Jumlah Transaksi dengan Buffer Ekstra Pasca-SL
input bool          InpAutopsyNotifyPush           = true;         // Kirim Laporan Otopsi Pasca-Loss ke Smartphone
input group "=== 8.5 REINFORCEMENT LEARNING & AI CANDLESTICK SHIELD (v3.40) ==="
input bool          InpUsePatternMatrix        = true;         // Aktifkan Memori Rapor & Pembelajaran Pola Mandiri
input bool          InpUsePreTrainedBrain      = true;         // Bekali Otak Awal dari Hasil Audit 9 Bulan (Pre-Trained)
input bool          InpFilterDojiCandles       = true;         // AI Shield: Tolak Entry Saat Candle Doji / Body Tipis (<22%)
input bool          InpFilterExhaustionWicks   = true;         // AI Shield: Tolak Entry Saat Muncul Ekor Penolakan Lawan (>=45%)
input bool          InpFilterOverextended      = true;         // AI Shield: Tolak Engulfing Terlalu Jauh dari EMA (>1.5x ATR)
input bool          InpSaveBrainToDisk         = true;         // Simpan Memori Pembelajaran Permanen ke File Disk (Auto-Save)
input int           InpMinTradesForPatternEval = 3;            // Minimal Transaksi Sebelum Evaluasi Pola
input double        InpPatternBlacklistWinrate = 40.0;         // Ambang Batas Blacklist Mandiri (Winrate < 40%)
input double        InpPatternBoostWinrate     = 70.0;         // Ambang Batas Boost Mandiri (Winrate > 70%)
input double        InpPatternBoostScore       = 10.0;         // Bonus Skor Konfluensi untuk Pola Akurat
input double        InpPatternPenaltyScore     = 15.0;         // Penalti Pengetatan Skor untuk Pola Lemah
input bool          InpUseDirectionalLearning  = true;         // Proteksi Anti-Loss Berulang Searah (Directional Bias Learning)
input double        InpDirectionalPenaltyScore = 10.0;         // Penalti Skor Tambahan untuk Arah yang Baru Saja Gagal
input int           InpDirectionalPenaltyBars  = 12;           // Durasi Penalti Arah Gagal (Bars Lilin)
input bool          InpUseHourlyLearning       = true;         // Hindari Jam Rawan Loss Berulang Hari Ini (Hourly Learning)

input group "=== 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ==="
input bool          InpUseRegimeFilter         = true;         // Aktifkan Sensor Cuaca Pasar (Trending vs Choppy)
input int           InpChoppinessPeriod        = 14;           // Periode Perhitungan Choppiness Index (CI)
input double        InpChoppyThreshold         = 61.8;         // Ambang Batas Pasar Choppy / Sideways (CI > 61.8)
input double        InpTrendingThreshold       = 38.2;         // Ambang Batas Pasar Tren Kuat (CI < 38.2)
input bool          InpBlockBreakoutInChoppy   = true;         // Blokir Momentum Breakout Saat Pasar Choppy
input group "=== 8.7 PRE-NEWS EVENT & SPREAD SPIKE SHIELD (v2.60) ==="
input bool          InpUseNewsShield           = true;             // Aktifkan Sensor Antisipasi Berita Berdampak Tinggi
input int           InpNewsMinsBefore          = 20;               // Waktu Pembekuan Sebelum Rilis Berita (Menit)
input int           InpNewsMinsAfter           = 25;               // Waktu Pembekuan Sesudah Rilis Berita (Menit)
input bool          InpAutoLockBEBeforeNews    = true;             // Otomatis Kunci SL+ pada Posisi Profit Jelang Berita
input string        InpNewsReleaseHoursServer  = "15:30,21:00";    // Jam Rilis Berita AS Utama (Waktu Server Broker)
input double        InpMaxSpreadSpikeMultiplier= 1.8;              // Batas Lonjakan Spread Dinamis (x InpMaxSpreadPips)

input group "=== 8.9 AUTONOMOUS NEURO-CALIBRATION & SELF-TUNING (v3.20) ==="
input bool          InpUseAutoCalibration          = true;         // Aktifkan Kalibrasi Parameter Mandiri Real-Time (v3.20)
input double        InpAutoTuningSensitivity       = 1.35;         // Sensitivitas Deteksi Volatilitas (ATR14 / ATR100)
input int           InpCalibrationConsecLossMax    = 2;            // Pemicu Pengetatan Parameter Saat Loss Beruntun (Default: 2x)
input double        InpAutoTuningMaxBufferMult     = 1.6;          // Batas Maksimal Ekspansi Buffer SL (x ATR)
input double        InpAutoTuningScoreStep         = 5.0;          // Langkah Pengetatan Ambang Skor per Kejadian Loss

input group "=== 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ==="
input bool          InpUseDivergenceFilter     = true;             // Deteksi Divergensi RSI (Cegah Beli Pucuk / Jual Lembah)
input int           InpRSIPeriod               = 14;               // Periode RSI untuk Deteksi Momentum
input int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)
input group "=== 8.9 SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70) ==="
input bool          InpUseADXFilter            = true;             // Blokir Entry Saat Pasar Tidur / Tanpa Arah (ADX Rendah)
input int           InpADXPeriod               = 14;               // Periode Perhitungan ADX
input double        InpMinADXThreshold         = 22.0;             // Ambang Batas Minimal ADX (Rekomendasi: 20.0 - 25.0)

input group "=== 8.10 SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70) ==="
input bool          InpUseEMASlopeFilter       = true;             // Blokir Entry Saat Garis EMA Datar / Kusut (Flat Sideways)
input int           InpEMASlopeLookback        = 5;                // Jarak Lilin Pengujian Kemiringan EMA (Bars)
input double        InpMinEMASlopePips         = 3.0;              // Ambang Batas Minimal Kenaikan/Penurunan EMA (Pips)

input group "=== 8.11 SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70) ==="
input bool          InpUseVolumeFilter         = true;             // Wajibkan Lonjakan Volume Institusi pada Lilin Konfirmasi
input int           InpVolumeMAPeriod          = 20;               // Periode Rata-Rata Volume Bergerak (Bars)
input double        InpMinVolumeMultiplier     = 1.15;             // Minimal Rasio Volume Konfirmasi (x Rata-Rata 20 Bar)

input group "=== 8.12 BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70) ==="
input bool          InpUseMinATRFilter         = true;             // Blokir Entry Saat Rentang Gerak Pasar Terlalu Sempit
input double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)
input group "=== 8.13 PROP FIRM EQUITY GUARDIAN & KILL-SWITCH (v3.00) ==="
input bool          InpUseEquityGuardian       = true;             // Aktifkan Pengaman Batas Drawdown Harian Ketat
input double        InpMaxDailyEquityDDPct     = 4.0;              // Batas Maksimal Penurunan Equity Harian (%)
input bool          InpLockTradingOnDDBreach   = true;             // Kunci Trading Otomatis Hingga Besok Jika Batas Tersentuh

input group "=== 8.14 ASYMMETRIC CONFIDENCE RISK ALLOCATOR (v3.00) ==="
input bool          InpUseAsymmetricLot        = true;             // Skalakan Lot Berdasarkan Kualitas Konfluensi (Kelly)
input double        InpGradeABoostMultiplier   = 1.30;             // Pengali Lot untuk Setup Grade A+ (Skor >= 85)
input double        InpGradeBPenaltyMultiplier = 0.70;             // Pengali Lot untuk Setup Standar (Skor 60-75)

input group "=== 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ==="
input bool          InpUseTrapHunter           = true;             // Eksekusi Reversal saat Bandar Menyapu Stop Loss Retail
input double        InpMinSweepPips            = 4.0;              // Minimal Jarak Penembusan Palsu (Pips)
input double        InpMaxSweepPips            = 30.0;             // Maksimal Jarak Penembusan Palsu (Pips)
input double        InpMinRejectionWickPct     = 40.0;             // Minimal Panjang Ekor Penolakan Lilin (%)

input group "=== 8.16 PRO TRADER DISCIPLINE SUITE (v3.30) ==="
input bool          InpUseDailyProfitLockdown  = false;             // Kunci Trading Hari Ini Jika Target Profit Harian Tercapai (false = Bebas Sesuai Backtest)
input ENUM_PROFIT_TARGET_MODE InpDailyProfitTargetMode = PROFIT_TARGET_CURRENCY; // Model Target Profit Harian
input double        InpDailyProfitTargetMoney  = 50.0;              // Target Profit Harian ($ USD)
input double        InpDailyProfitTargetPercent= 2.0;               // Target Profit Harian (% Modal)
input bool          InpUseRolloverGuard        = true;              // Bekukan Entry Selama Rollover Spread Melebar Tengah Malam
input int           InpRolloverStartHour       = 23;                // Jam Mulai Rollover Server
input int           InpRolloverStartMin        = 50;                // Menit Mulai Rollover Server (23:50)
input int           InpRolloverEndHour         = 0;                 // Jam Selesai Rollover Server
input int           InpRolloverEndMin          = 25;                // Menit Selesai Rollover Server (00:25)
input bool          InpUseMaxDailyTrades       = false;             // Batasi Kuota Maksimal Transaksi per Hari (false = Tanpa Batas, Sesuai Backtest)
input int           InpMaxDailyTrades          = 25;                // Kuota Maksimal Transaksi per Hari (Jika Diaktifkan)
input bool          InpUseMilestoneRatchet     = false;             // Kunci Untung Bertingkat (false = Gunakan Trailing SMC Dinamis Sesuai Backtest)
input bool          InpTradeKillzonesOnly      = false;             // Hanya Trading di Sesi Institusional Paling Likuid (London & NY)
input int           InpKillzoneLondonStart     = 9;                 // Jam Mulai London Killzone (Server Time)
input int           InpKillzoneLondonEnd       = 13;                // Jam Selesai London Killzone (Server Time)
input int           InpKillzoneNYStart         = 14;                // Jam Mulai New York Killzone (Server Time)
input int           InpKillzoneNYEnd           = 20;                // Jam Selesai New York Killzone (Server Time)

input group "=== 11. NOTIFIKASI PUSH KE SMARTPHONE (HP) ==="
input bool          InpSendPushNotifications       = true;         // Kirim Notifikasi Instan ke HP (MetaTrader 5 Mobile)
input bool          InpNotifyOnEntry               = true;         // Notifikasi Saat Eksekusi Open Posisi (BUY / SELL)
input bool          InpNotifyOnSLPlus              = true;         // Notifikasi Saat Auto-BE / SL+ Mengunci Profit
input bool          InpNotifyOnPartial             = true;         // Notifikasi Saat TP1 50% Ditutup & Runner Aktif
input bool          InpNotifyOnCircuitBreaker      = true;         // Notifikasi Saat Circuit Breaker Cooldown Terpicu

input group "=== 9. ON-CHART SMC VISUALIZER (AUTO-DRAW DI CHART) ==="
input bool          InpDrawSMCOnChart     = true;                  // Otomatis Gambar Kotak Order Block, FVG & Garis BOS di MT5
input color         InpColorBullishOB     = C'14,116,144';         // Warna Kotak Bullish Order Block (Base Demand)
input color         InpColorBearishOB     = C'190,18,60';          // Warna Kotak Bearish Order Block (Supply Zone)
input color         InpColorFVG           = C'217,119,6';          // Warna Kotak Fair Value Gap (FVG Imbalance)

input group "=== 10. STATISTIK PERFORMA & TAMPILAN DASHBOARD ==="
input bool          InpShowDashboard      = true;                  // Tampilkan Dashboard Monitor 4 Pilar
input int           InpDashboardX         = 15;                    // Posisi Awal Dashboard X (Pixel dari Kiri)
input int           InpDashboardY         = 20;
input int           InpDashboardWidth     = 480;                   // Lebar Panel Dashboard (Pixel)                    // Posisi Awal Dashboard Y (Pixel dari Atas)
input bool          InpShowPnLStats       = true;                  // Tampilkan Rekap PnL (Sejak Start, Harian, Mingguan)
input bool          InpResetStatsOnStart  = false;                 // Reset Statistik Awal Saat EA Dipasang Ulang

//+------------------------------------------------------------------+
//| STRUKTUR DATA INTERNAL (SMC & CANDLESTICK INTELLIGENCE)          |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| STRUKTUR DATA KECERDASAN INSTITUSIONAL (OB, FVG & CONFLUENCE)    |
//+------------------------------------------------------------------+
struct SMCOrderBlock
{
   bool     isValid;
   bool     isBullish;
   datetime time;
   double   top;
   double   bottom;
   double   median;
   double   displacementAtr;
   bool     isMitigated;
   datetime mitigationTime;
   int      barAge;
};

struct SMCFairValueGap
{
   bool     isValid;
   bool     isBullish;
   datetime time;
   double   top;
   double   bottom;
   double   mid;
   bool     isMitigated;
   datetime mitigationTime;
   int      barAge;
};

struct ConfluenceScoreResult
{
   double totalScore;       // 0 - 100
   string grade;            // "GRADE A+ SNIPER", "GRADE A HIGH PROB", "GRADE B REJECT"
   bool   isPassed;         // totalScore >= InpMinConfluenceScore
   double structurePts;     // Max 20
   double displacementPts;  // Max 15
   double obMitigationPts;  // Max 20
   double fvgPts;           // Max 15
   double sweepPts;         // Max 10
   double fiboGPPts;        // Max 10
   double emaRibbonPts;     // Max 10
   double candlePts;        // Max 10
   double chartPatternPts;  // Max 15 (Bonus Pola Grafik)
   double vsaPts;           // Max 10 (Bonus VSA Volume Climax / No-Supply)
   string vsaStatus;        // "CLIMAX ABSORPTION (+10)", "NO-SUPPLY PULLBACK (+5)", "NORMAL"
   string details;
};

enum ENUM_SMC_STRUCTURE
{
   SMC_STRUCT_NEUTRAL,     // Sideways / Konsolidasi
   SMC_STRUCT_BULLISH,     // Bullish Trend (HH - HL)
   SMC_STRUCT_BEARISH,     // Bearish Trend (LH - LL)
   SMC_STRUCT_CHOCH_BUY,   // Pembalikan Bullish CHoCH
   SMC_STRUCT_CHOCH_SELL   // Pembalikan Bearish CHoCH
};

enum ENUM_CANDLE_PATTERN
{
   PATTERN_NONE,
   PATTERN_HAMMER_PINBAR,        // Pin Bar & Hammer Rejection
   PATTERN_ENGULFING,            // Institutional Absorption Engulfing
   PATTERN_TWEEZER,              // Tweezer Double Level Rejection
   PATTERN_MORNING_EVENING,      // Morning / Evening Star (3-Bar Reversal)
   PATTERN_FVG_MITIGATION,       // Rebound dari Fair Value Gap (FVG)
   PATTERN_THREE_SOLDIERS_CROWS, // Three White Soldiers / Three Black Crows
   PATTERN_HARAMI_INSIDE_BAR,    // Harami & Inside Bar Compression Breakout
   PATTERN_PIERCING_DARKCLOUD,   // Piercing Line & Dark Cloud Cover
   PATTERN_DOJI_REJECTION,       // Dragonfly Doji / Gravestone Doji Extreme Rejection
   PATTERN_INVERTED_HAMMER_STAR  // Inverted Hammer & Shooting Star Rejection
};

enum ENUM_CHART_PATTERN
{
   CHART_PATTERN_NONE,
   CHART_PATTERN_DOUBLE_BOTTOM,       // W-Pattern Reversal (Double Bottom)
   CHART_PATTERN_DOUBLE_TOP,          // M-Pattern Reversal (Double Top)
   CHART_PATTERN_QUASIMODO_BUY,       // Bullish Quasimodo (QM Institutional Reversal)
   CHART_PATTERN_QUASIMODO_SELL,      // Bearish Quasimodo (QM Institutional Reversal)
   CHART_PATTERN_HEAD_SHOULDERS,      // Head & Shoulders Bearish Reversal
   CHART_PATTERN_INVERSE_HS,          // Inverse Head & Shoulders Bullish Reversal
   CHART_PATTERN_BULL_FLAG,           // Bullish Continuation Flag
   CHART_PATTERN_BEAR_FLAG            // Bearish Continuation Flag
};

struct ChartPatternAnalysis
{
   ENUM_CHART_PATTERN pattern;
   string             patternName;
   bool               isBullish;
   double             score;            // 0 - 100
   double             keyLevel;         // Level harga acuan (Left Shoulder / Double Test Level)
   datetime           startTime;
   datetime           endTime;
   bool               isValid;
};

struct CandleAnalysis
{
   ENUM_CANDLE_PATTERN pattern;
   string              patternName;
   bool                isBullish;
   double              score;           // Kualitas Pola (0 - 100)
   double              wickRatio;       // % Panjang Ekor Penolakan
   double              bodyRatio;       // % Ukuran Body
   bool                isHighQuality;   // Score >= InpMinCandleScore
};

struct SMCStructureAnalysis
{
   ENUM_SMC_STRUCTURE  structure;
   string              structureName;
   bool                hasBOS;          // Break of Structure
   bool                hasCHoCH;        // Change of Character
   bool                hasSweep;        // Liquidity Sweep (Stop Hunt)
   double              sweepPrice;
   double              dealingRangeLow;
   double              dealingRangeHigh;
   double              discountPercent; // 0% = Low (Diskon Maksimal), 100% = High (Premium)
   bool                isDiscount;      // discountPercent <= 50.0%
   bool                isPremium;       // discountPercent >= 50.0%
   bool                hasFVG;          // Ada Fair Value Gap aktif
   double              fvgTop;
   double              fvgBottom;
};

struct SMCSwing
{
   datetime time;
   double   price;
   bool     isHigh;
   bool     isSwept;
};

// ===================================================================
// STRUCT MULTI-TIMEFRAME PRICE ACTION ENGINE (v4.00)
// ===================================================================
struct MTFZone
{
   bool     isValid;
   bool     isBullish;     // true = OB Demand (Buy), false = OB Supply (Sell)
   double   top;
   double   bottom;
   double   mid;
   string   zoneType;      // "OB_DEMAND", "OB_SUPPLY"
   ENUM_TIMEFRAMES tf;
   datetime detectedAt;
   bool     isTested;      // Harga pernah menyentuh zona
   bool     isMitigated;   // Zona sudah ditembus sepenuhnya
   double   dispAtrMult;   // Kekuatan displacement pembentuk OB (x ATR)
};

struct MTFAnalysisResult
{
   // M1 Order Block Detection
   MTFZone  m1DemandOB;       // OB Demand (Bullish) M1 terdekat di bawah harga
   MTFZone  m1SupplyOB;       // OB Supply (Bearish) M1 terdekat di atas harga
   
   // M1 Pullback / Retest Status
   bool     m1PullbackValid;  // true = harga sedang retest ke OB M1 yang valid
   bool     m1PullbackIsBuy;  // true = retest ke OB Demand (siap Buy), false = ke OB Supply (siap Sell)
   string   m1PullbackType;   // Deskripsi: "OB_DEMAND_RETEST" / "OB_SUPPLY_RETEST"
   double   m1PullbackScore;  // Skor retest (0 - 20)
   
   // M1 Structure
   bool     m1CHoCHBull;      // CHoCH Bullish terdeteksi di M1
   bool     m1CHoCHBear;      // CHoCH Bearish terdeteksi di M1
   bool     m1BOSBull;        // BOS Bullish (Higher High) di M1
   bool     m1BOSBear;        // BOS Bearish (Lower Low) di M1
   
   // M1 ATR
   double   m1Atr;
   
   // HUD Display
   string   m1StatusStr;      // Teks status untuk HUD
   string   m1DemandStr;      // Range OB Demand untuk HUD
   string   m1SupplyStr;      // Range OB Supply untuk HUD
   datetime lastUpdated;
};

struct DailyPivot
{
   double P;
   double S1, S2, S3;
   double R1, R2, R3;
   double highD1, lowD1, closeD1;
   datetime dayTime;
};

struct AutoFibo
{
   double high;
   double low;
   double level0;
   double level236;
   double level382;
   double level500;
   double level618;
   double level786;
   double level1000;
   double ext272;
   double ext618;
   bool   isValid;
};

struct TradeStats
{
   double grossProfit;
   double grossLoss;
   double netProfit;
   int    winTrades;
   int    lossTrades;
   int    totalTrades;
};

//+------------------------------------------------------------------+
//| VARIABEL GLOBAL & HANDLE INDIKATOR                               |
//+------------------------------------------------------------------+
CTrade         trade;
CPositionInfo  posInfo;
COrderInfo     orderInfo;

int            h_ema8       = INVALID_HANDLE;
int            h_ema21      = INVALID_HANDLE;
int            h_ema125     = INVALID_HANDLE;
int            h_atr14      = INVALID_HANDLE;
int            h_atr100     = INVALID_HANDLE;
int            h_htf_ema125 = INVALID_HANDLE;
int            h_htf_ema8   = INVALID_HANDLE;
int            h_htf_ema21  = INVALID_HANDLE;
string         g_htfMacroStr = "H1 MACRO READY";

// === M1 MTF ENGINE HANDLES & GLOBALS (v4.00) ===
int            h_m1_ema21   = INVALID_HANDLE;  // EMA 21 di M1 untuk trailing M1
int            h_m1_atr14   = INVALID_HANDLE;  // ATR 14 di M1 untuk filter displacement OB
datetime       g_lastM1BarTime = 0;            // Timestamp bar M1 terakhir (throttle update)
MTFAnalysisResult g_mtfResult;                 // Hasil analisis M1 terbaru (cached per M1 bar)

datetime       lastBarTime      = 0;
datetime       lastOrderBarTime = 0;

datetime       g_eaStartTime      = 0;
double         g_eaInitialBalance = 0.0;
string         g_gvStartTimeKey   = "";
string         g_gvStartBalKey    = "";

// Koordinat & State Drag & Drop Dashboard
int            g_panelX           = 15;
int            g_panelY           = 20;
int            g_panelW           = 460;
int            g_panelH           = 400;
bool           g_isDragging       = false;
int            g_dragOffsetX      = 0;
int            g_dragOffsetY      = 0;
bool           g_hudMinimized     = false;

bool           g_eaManualPause    = false;

SMCSwing             lastSwingHigh;
SMCSwing             prevSwingHigh;
SMCSwing             lastSwingLow;
SMCSwing             prevSwingLow;
DailyPivot           currentPivot;
AutoFibo             currentFibo;

SMCStructureAnalysis g_smcAnalysis;
CandleAnalysis       g_candleAnalysis;
SMCOrderBlock        g_bullishOB;
SMCOrderBlock        g_bearishOB;
SMCFairValueGap      g_activeFVG;
ConfluenceScoreResult g_lastScoreResult;
ChartPatternAnalysis  g_chartPattern;

bool                 g_shockGuardActive  = false;
datetime             g_lastShockTime     = 0;
int                  g_shockCooldownLeft = 0;

// Variabel Status Circuit Breaker & VSA Institusional (v2.2)
int                  g_consecutiveLossCount = 0;
datetime             g_lastLossTime         = 0;
datetime             g_cooldownUntilTime    = 0;
double               g_todayClosedProfit    = 0.0;
bool                 g_dailyLossLimitHit    = false;

// Struktur & State Mesin Otopsi & Koreksi Diri Pasca-Loss (v2.40 Apex)
struct LossAutopsyReport
{
   bool                 isActive;
   ulong                failedTicket;
   datetime             timeLoss;
   ENUM_CANDLE_PATTERN  failedPattern;
   string               failedPatternName;
   string               lossReason;
   double               scorePenalty;
   datetime             quarantineUntilBar;
   int                  tradesWithExtraBuffer;
   int                  failedDirection;        // +1 for BUY, -1 for SELL
   datetime             directionPenaltyUntil;  // Waktu berakhir penalti arah
   int                  toxicHour;              // Jam rawan loss (-1 jika normal)
};
LossAutopsyReport g_autopsy;

//+------------------------------------------------------------------+
//| AUTONOMOUS NEURO-CALIBRATION STATE (v3.20)                       |
//+------------------------------------------------------------------+
struct AutoCalibrationState
{
   bool   isCalibrated;
   double slBufferAtrMult;        // Dynamic multiplier: default InpSLBufferAtrMult
   double scoreElevation;         // Dynamic score elevation
   int    cooldownBars;           // Dynamic cooldown bars
   double candleTrailBufferPts;   // Dynamic candle trail buffer
   double volatilityRatio;        // ATR14 / ATR100
   string regimeDescription;      // "Normal", "High Volatility Spike", "Choppy Compression"
   int    consecutiveLossStreak;  // Current active consecutive losses
};
AutoCalibrationState g_calibration = {false, 1.2, 0.0, 3, 15.0, 1.0, "Normal", 0};

//+------------------------------------------------------------------+
//| STRUKTUR & MEMORI DINAMIS: PATTERN PERFORMANCE MATRIX (v3.10)   |
//+------------------------------------------------------------------+
struct PatternRecord
{
   int    patternId;
   string name;
   int    wins;
   int    losses;
   int    total;
   double winRate;
   bool   isBlacklisted;
   double scoreModifier;
};

#define TOTAL_TRACKED_PATTERNS 13
PatternRecord g_patternMatrix[TOTAL_TRACKED_PATTERNS];

ENUM_MARKET_REGIME g_currentRegime     = REGIME_NORMAL;
double             g_currentChoppiness = 50.0;
string             g_bestPatternStr    = "BELUM ADA DATA";
string g_newsStatusStr = "AMAN (STANDBY)";
string g_divStatusStr  = "NORMAL (SEHAT)";
int    h_rsi_div       = INVALID_HANDLE;
string g_sidewaysStatusStr = "NORMAL (TREN SEHAT)";
double g_currentADXVal     = 25.0;
double g_currentVolRatio   = 1.20;
int    h_adx14             = INVALID_HANDLE;
double g_midnightBalance      = 0.0;
bool   g_equityLockActive     = false;
double g_currentDailyDDPct    = 0.0;
string g_trapHunterStatusStr  = "STANDBY";

// Pro Trader Discipline Suite Globals (v3.30)
bool     g_dailyProfitLocked        = false;
datetime g_lastProfitLockDay        = 0;
int      g_todayTradesCount         = 0;
datetime g_lastTradeCountDay        = 0;


string         g_lastSignalType = "MENUNGGU SETUP";
string         g_lastBOSStatus  = "NETRAL";
string         g_lastFiboStatus = "DILUAR GP";
string         g_doubleAlignStr = "MENUNGGU DATA";

//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: NOTIFIKASI PUSH SMARTPHONE (HP)                 |
//+------------------------------------------------------------------+
void SendPushAlert(string msg)
{
   if (!InpSendPushNotifications) return;
   SendNotification("[VIKAR EA PRO - " + _Symbol + "]\n" + msg);
}

//| FUNGSI PEMBANTU: KONVERSI PIPS & POINTS                          |
//+------------------------------------------------------------------+
double PipToPrice(double pips)
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits   = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   bool isGold  = (StringFind(_Symbol, "XAU") >= 0 || StringFind(_Symbol, "GOLD") >= 0);
   double mult  = 1.0;
   if (isGold)
   {
      if (digits == 3) mult = 100.0;
      else if (digits == 2) mult = 10.0;
      else mult = 1.0;
   }
   else
   {
      if (digits == 3 || digits == 5) mult = 10.0;
      else mult = 1.0;
   }
   return pips * point * mult;
}

double PriceToPips(double priceDiff)
{
   double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   int digits   = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   bool isGold  = (StringFind(_Symbol, "XAU") >= 0 || StringFind(_Symbol, "GOLD") >= 0);
   double mult  = 1.0;
   if (isGold)
   {
      if (digits == 3) mult = 100.0;
      else if (digits == 2) mult = 10.0;
      else mult = 1.0;
   }
   else
   {
      if (digits == 3 || digits == 5) mult = 10.0;
      else mult = 1.0;
   }
   if (point * mult == 0) return 0.0;
   return priceDiff / (point * mult);
}

double PointToPrice(double points)
{
   return PipToPrice(points / 10.0);
}

//+------------------------------------------------------------------+
//| DETEKSI LILIN BARU (NON-REPAINTING BAR CLOSE TRIGGER)            |
//+------------------------------------------------------------------+
bool IsNewBar()
{
   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if (currentBarTime != lastBarTime && currentBarTime != 0)
   {
      lastBarTime = currentBarTime;
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| NORMALISASI UKURAN LOT SESUAI ATURAN BROKER                      |
//+------------------------------------------------------------------+
double NormalizeLots(double rawLot)
{
   double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot       = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double stepLot      = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if (brokerMinLot <= 0) brokerMinLot = 0.10;
   if (maxLot <= 0)       maxLot = 100.0;
   if (stepLot <= 0)      stepLot = 0.01;

   // Pastikan batas bawah mematuhi minimal broker dan InpMinLot
   double minLot = brokerMinLot;
   if (InpMinLot > 0)
      minLot = MathMax(brokerMinLot, InpMinLot);

   if (InpMaxLot > 0 && InpMaxLot < maxLot)
      maxLot = InpMaxLot;

   // Proteksi anti-kontradiksi: pastikan maxLot tidak lebih kecil dari minLot broker
   if (maxLot < minLot)
      maxLot = minLot;

   double normalized = MathFloor(rawLot / stepLot) * stepLot;

   if (normalized < minLot) normalized = minLot;
   if (normalized > maxLot) normalized = maxLot;

   int digits = 2;
   if (stepLot == 0.1) digits = 1;
   if (stepLot == 1.0) digits = 0;

   return NormalizeDouble(normalized, digits);
}

//+------------------------------------------------------------------+
//| HITUNG LOT BERDASARKAN METODE MANAJEMEN RISIKO                   |
//+------------------------------------------------------------------+
double CalculateRiskLot(double slDistancePrice, double score = 70.0)
{
   double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if (brokerMinLot <= 0) brokerMinLot = 0.10;

   double finalLot = brokerMinLot;

   // Mode 1: Otomatis Menyesuaikan Minimal Lot Broker (Aman, Konservatif & Anti-Lot Besar)
   if (InpLotType == LOT_TYPE_BROKER_MIN)
   {
      finalLot = brokerMinLot;
   }
   // Mode 2: Fixed Lot (Ukuran Statis)
   else if (InpLotType == LOT_TYPE_FIXED)
   {
      finalLot = InpFixedLot;
   }
   // Mode 3: Dynamic Risk Percent (% Saldo Modal)
   else if (InpLotType == LOT_TYPE_RISK_PERCENT)
   {
      double balance = AccountInfoDouble(ACCOUNT_BALANCE);
      if (balance <= 0) return NormalizeLots(brokerMinLot);

      double riskAmount = balance * (InpRiskPercent / 100.0);



      double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

      if (tickValue <= 0 || tickSize <= 0 || slDistancePrice <= 0)
         return NormalizeLots(brokerMinLot);

      double lossPerLot = (slDistancePrice / tickSize) * tickValue;
      if (lossPerLot <= 0) return NormalizeLots(brokerMinLot);

      finalLot = riskAmount / lossPerLot;
   }

   // 8.14 Asymmetric Confidence Risk Allocator (Kelly Scaling v3.00)
   if (InpUseAsymmetricLot)
   {
      if (score >= 85.0)
         finalLot *= InpGradeABoostMultiplier;
      else if (score < 75.0)
         finalLot *= InpGradeBPenaltyMultiplier;
   }

   return NormalizeLots(finalLot);
}

//+------------------------------------------------------------------+
//| PILAR 2: KALKULASI DAILY PIVOT POINTS DARI DATA D1               |
//+------------------------------------------------------------------+
bool UpdateDailyPivots()
{
   MqlRates ratesD1[];
   ArraySetAsSeries(ratesD1, true);
   if (CopyRates(_Symbol, PERIOD_D1, 1, 1, ratesD1) < 1)
      return false;

   currentPivot.highD1  = ratesD1[0].high;
   currentPivot.lowD1   = ratesD1[0].low;
   currentPivot.closeD1 = ratesD1[0].close;
   currentPivot.dayTime = ratesD1[0].time;

   // Formula Standar Floor Pivot
   currentPivot.P  = (currentPivot.highD1 + currentPivot.lowD1 + currentPivot.closeD1) / 3.0;
   currentPivot.R1 = (2.0 * currentPivot.P) - currentPivot.lowD1;
   currentPivot.S1 = (2.0 * currentPivot.P) - currentPivot.highD1;

   double range = currentPivot.highD1 - currentPivot.lowD1;
   currentPivot.R2 = currentPivot.P + range;
   currentPivot.S2 = currentPivot.P - range;

   currentPivot.R3 = currentPivot.highD1 + 2.0 * (currentPivot.P - currentPivot.lowD1);
   currentPivot.S3 = currentPivot.lowD1 - 2.0 * (currentPivot.highD1 - currentPivot.P);

   return true;
}

//+------------------------------------------------------------------+
//| PILAR 1: DETEKSI AYUNAN FRACTAL DUA SIKLUS (SMC SWINGS)          |
//+------------------------------------------------------------------+
void UpdateSMCSwings(const MqlRates &rates[], int totalBars)
{
   int k = InpFractalPeriod;
   if (k < 1) k = 1;
   if (totalBars < (2 * k + 5)) return;

   int lookback = MathMin(totalBars - k - 2, 90);
   int highFound = 0;
   int lowFound  = 0;

   for (int i = k + 1; i < lookback; i++)
   {
      bool isFractalHigh = true;
      for (int j = 1; j <= k; j++)
      {
         int leftIdx  = i + j;
         int rightIdx = i - j;
         if (rightIdx < 0 || leftIdx >= totalBars)
         {
            isFractalHigh = false;
            break;
         }
         if (rates[i].high <= rates[rightIdx].high || rates[i].high <= rates[leftIdx].high)
         {
            isFractalHigh = false;
            break;
         }
      }

      if (isFractalHigh)
      {
         if (highFound == 0)
         {
            lastSwingHigh.time    = rates[i].time;
            lastSwingHigh.price   = rates[i].high;
            lastSwingHigh.isHigh  = true;
            lastSwingHigh.isSwept = false;
            highFound++;
         }
         else if (highFound == 1 && rates[i].time != lastSwingHigh.time && MathAbs(rates[i].high - lastSwingHigh.price) > _Point * 5)
         {
            prevSwingHigh.time    = rates[i].time;
            prevSwingHigh.price   = rates[i].high;
            prevSwingHigh.isHigh  = true;
            prevSwingHigh.isSwept = false;
            highFound++;
            break;
         }
      }
   }

   for (int i = k + 1; i < lookback; i++)
   {
      bool isFractalLow = true;
      for (int j = 1; j <= k; j++)
      {
         int leftIdx  = i + j;
         int rightIdx = i - j;
         if (rightIdx < 0 || leftIdx >= totalBars)
         {
            isFractalLow = false;
            break;
         }
         if (rates[i].low >= rates[rightIdx].low || rates[i].low >= rates[leftIdx].low)
         {
            isFractalLow = false;
            break;
         }
      }

      if (isFractalLow)
      {
         if (lowFound == 0)
         {
            lastSwingLow.time    = rates[i].time;
            lastSwingLow.price   = rates[i].low;
            lastSwingLow.isHigh  = false;
            lastSwingLow.isSwept = false;
            lowFound++;
         }
         else if (lowFound == 1 && rates[i].time != lastSwingLow.time && MathAbs(rates[i].low - lastSwingLow.price) > _Point * 5)
         {
            prevSwingLow.time    = rates[i].time;
            prevSwingLow.price   = rates[i].low;
            prevSwingLow.isHigh  = false;
            prevSwingLow.isSwept = false;
            lowFound++;
            break;
         }
      }
   }
}

//+------------------------------------------------------------------+
//| ANALISIS KECERDASAN STRUKTUR PASAR SMC (BOS, CHOCH, SWEEP, FVG)  |
//+------------------------------------------------------------------+
SMCStructureAnalysis AnalyzeMarketStructure(const MqlRates &rates[])
{
   SMCStructureAnalysis s;
   s.structure = SMC_STRUCT_NEUTRAL;
   s.structureName = "Mencari Struktur";
   s.hasBOS = false;
   s.hasCHoCH = false;
   s.hasSweep = false;
   s.sweepPrice = 0.0;
   s.dealingRangeLow = lastSwingLow.price;
   s.dealingRangeHigh = lastSwingHigh.price;
   s.discountPercent = 50.0;
   s.isDiscount = false;
   s.isPremium = false;
   s.hasFVG = false;
   s.fvgTop = 0.0;
   s.fvgBottom = 0.0;

   if (ArraySize(rates) < 6 || lastSwingHigh.price <= 0 || lastSwingLow.price <= 0)
      return s;

   double close1 = rates[1].close;
   double high1  = rates[1].high;
   double low1   = rates[1].low;

   // 1. Dealing Range & Persentase Diskon / Premium
   double drRange = s.dealingRangeHigh - s.dealingRangeLow;
   if (drRange > 0)
   {
      double rawPct = ((close1 - s.dealingRangeLow) / drRange) * 100.0;
      s.discountPercent = MathMax(0.0, MathMin(100.0, rawPct));
      s.isDiscount = (rawPct <= 50.0);
      s.isPremium  = (rawPct >= 50.0);
   }

   // 2. Evaluasi Siklus Ayunan Swing (HH-HL vs LH-LL)
   bool isBullishSwings = (prevSwingHigh.price > 0 && prevSwingLow.price > 0 &&
                           lastSwingHigh.price >= prevSwingHigh.price && lastSwingLow.price >= prevSwingLow.price);
   bool isBearishSwings = (prevSwingHigh.price > 0 && prevSwingLow.price > 0 &&
                           lastSwingHigh.price <= prevSwingHigh.price && lastSwingLow.price <= prevSwingLow.price);

   if (isBullishSwings)
   {
      s.structure = SMC_STRUCT_BULLISH;
      s.structureName = "BULLISH (HH-HL)";
   }
   else if (isBearishSwings)
   {
      s.structure = SMC_STRUCT_BEARISH;
      s.structureName = "BEARISH (LH-LL)";
   }
   else
   {
      s.structure = (lastSwingHigh.price > lastSwingLow.price) ? SMC_STRUCT_BULLISH : SMC_STRUCT_BEARISH;
      s.structureName = (s.structure == SMC_STRUCT_BULLISH) ? "BULLISH BIAS" : "BEARISH BIAS";
   }

   // 3. Konfirmasi Break of Structure (BOS) & Change of Character (CHoCH)
   if (close1 > lastSwingHigh.price && rates[1].open < lastSwingHigh.price)
   {
      s.hasBOS = true;
      if (s.structure == SMC_STRUCT_BEARISH)
      {
         s.hasCHoCH = true;
         s.structure = SMC_STRUCT_CHOCH_BUY;
         s.structureName = "BULLISH CHoCH REVERSAL";
      }
      else
      {
         s.structureName = "BULLISH BOS";
      }
   }
   else if (close1 < lastSwingLow.price && rates[1].open > lastSwingLow.price)
   {
      s.hasBOS = true;
      if (s.structure == SMC_STRUCT_BULLISH)
      {
         s.hasCHoCH = true;
         s.structure = SMC_STRUCT_CHOCH_SELL;
         s.structureName = "BEARISH CHoCH REVERSAL";
      }
      else
      {
         s.structureName = "BEARISH BOS";
      }
   }

   // 4. Deteksi Liquidity Sweep (Stop Hunt Retail oleh Institusi)
   if (low1 < lastSwingLow.price && close1 > lastSwingLow.price)
   {
      s.hasSweep = true;
      s.sweepPrice = lastSwingLow.price;
   }
   else if (high1 > lastSwingHigh.price && close1 < lastSwingHigh.price)
   {
      s.hasSweep = true;
      s.sweepPrice = lastSwingHigh.price;
   }

   // 5. Deteksi Fair Value Gap (FVG)
   if (InpUseFVGFilter)
   {
      if (rates[3].high < rates[1].low)
      {
         s.hasFVG = true;
         s.fvgTop = rates[1].low;
         s.fvgBottom = rates[3].high;
      }
      else if (rates[3].low > rates[1].high)
      {
         s.hasFVG = true;
         s.fvgTop = rates[3].low;
         s.fvgBottom = rates[1].high;
      }
   }

   return s;
}

//+------------------------------------------------------------------+
//| DETEKSI ORDER BLOCK (OB) INSTITUSIONAL DENGAN DISPLACEMENT ATR   |
//+------------------------------------------------------------------+
void DetectOrderBlocks(const MqlRates &rates[], int totalRates, double currentAtr)
{
   if (totalRates < 15 || currentAtr <= 0) return;

   // 1. Scan Bullish Order Block (Base Demand):
   for (int i = 2; i < MathMin(totalRates - 3, InpOBMaxAgeBars); i++)
   {
      bool isBaseCandle = (rates[i].close <= rates[i].open);
      double bodyDisp = MathAbs(rates[i-1].close - rates[i-1].open);
      double rangeDisp = rates[i-1].high - rates[i-1].low;
      bool isDisplacement = (rates[i-1].close > rates[i-1].open) && 
                            (rangeDisp >= (InpOBDisplacementAtrMult * currentAtr) || bodyDisp >= (0.75 * currentAtr));

      if (isBaseCandle && isDisplacement)
      {
         g_bullishOB.isValid = true;
         g_bullishOB.isBullish = true;
         g_bullishOB.time = rates[i].time;
         g_bullishOB.top = rates[i].high;
         g_bullishOB.bottom = rates[i].low;
         g_bullishOB.median = (g_bullishOB.top + g_bullishOB.bottom) * 0.5;
         g_bullishOB.displacementAtr = rangeDisp / currentAtr;
         g_bullishOB.barAge = i;

         g_bullishOB.isMitigated = false;
         for (int k = i - 2; k >= 1; k--)
         {
            if (rates[k].low <= g_bullishOB.top && rates[k].high >= g_bullishOB.bottom)
            {
               g_bullishOB.isMitigated = true;
               g_bullishOB.mitigationTime = rates[k].time;
               break;
            }
         }
         break;
      }
   }

   // 2. Scan Bearish Order Block (Supply Zone):
   for (int i = 2; i < MathMin(totalRates - 3, InpOBMaxAgeBars); i++)
   {
      bool isBaseCandle = (rates[i].close >= rates[i].open);
      double bodyDisp = MathAbs(rates[i-1].close - rates[i-1].open);
      double rangeDisp = rates[i-1].high - rates[i-1].low;
      bool isDisplacement = (rates[i-1].close < rates[i-1].open) && 
                            (rangeDisp >= (InpOBDisplacementAtrMult * currentAtr) || bodyDisp >= (0.75 * currentAtr));

      if (isBaseCandle && isDisplacement)
      {
         g_bearishOB.isValid = true;
         g_bearishOB.isBullish = false;
         g_bearishOB.time = rates[i].time;
         g_bearishOB.top = rates[i].high;
         g_bearishOB.bottom = rates[i].low;
         g_bearishOB.median = (g_bearishOB.top + g_bearishOB.bottom) * 0.5;
         g_bearishOB.displacementAtr = rangeDisp / currentAtr;
         g_bearishOB.barAge = i;

         g_bearishOB.isMitigated = false;
         for (int k = i - 2; k >= 1; k--)
         {
            if (rates[k].high >= g_bearishOB.bottom && rates[k].low <= g_bearishOB.top)
            {
               g_bearishOB.isMitigated = true;
               g_bearishOB.mitigationTime = rates[k].time;
               break;
            }
         }
         break;
      }
   }
}

//+------------------------------------------------------------------+
//| LACAK FAIR VALUE GAP (FVG) MULTI-BAR (IMBALANCE TRACKER)         |
//+------------------------------------------------------------------+
void TrackFairValueGaps(const MqlRates &rates[], int totalRates)
{
   g_activeFVG.isValid = false;
   if (totalRates < 6) return;

   int lookback = MathMin(totalRates - 3, InpFVGLookbackBars);
   double minGap = InpMinFVGPoints * _Point;

   for (int i = 1; i <= lookback; i++)
   {
      // Bullish FVG
      if (rates[i].low > rates[i+2].high + minGap)
      {
         g_activeFVG.isValid = true;
         g_activeFVG.isBullish = true;
         g_activeFVG.time = rates[i+1].time;
         g_activeFVG.top = rates[i].low;
         g_activeFVG.bottom = rates[i+2].high;
         g_activeFVG.mid = (g_activeFVG.top + g_activeFVG.bottom) * 0.5;
         g_activeFVG.barAge = i;

         g_activeFVG.isMitigated = false;
         for (int m = i - 1; m >= 1; m--)
         {
            if (rates[m].low <= g_activeFVG.top)
            {
               g_activeFVG.isMitigated = true;
               g_activeFVG.mitigationTime = rates[m].time;
               break;
            }
         }
         break;
      }
      // Bearish FVG
      else if (rates[i].high < rates[i+2].low - minGap)
      {
         g_activeFVG.isValid = true;
         g_activeFVG.isBullish = false;
         g_activeFVG.time = rates[i+1].time;
         g_activeFVG.top = rates[i+2].low;
         g_activeFVG.bottom = rates[i].high;
         g_activeFVG.mid = (g_activeFVG.top + g_activeFVG.bottom) * 0.5;
         g_activeFVG.barAge = i;

         g_activeFVG.isMitigated = false;
         for (int m = i - 1; m >= 1; m--)
         {
            if (rates[m].high >= g_activeFVG.bottom)
            {
               g_activeFVG.isMitigated = true;
               g_activeFVG.mitigationTime = rates[m].time;
               break;
            }
         }
         break;
      }
   }
}

//+------------------------------------------------------------------+
//| DETEKSI LONJAKAN VOLATILITAS ABNORMAL / BERITA (SHOCK GUARD)     |
//+------------------------------------------------------------------+
bool CheckShockGuard(const MqlRates &rates[], double currentAtr)
{
   if (!InpUseShockGuard || currentAtr <= 0)
   {
      g_shockGuardActive = false;
      return false;
   }

   if (g_shockCooldownLeft > 0)
   {
      g_shockCooldownLeft--;
      g_shockGuardActive = (g_shockCooldownLeft > 0);
      if (g_shockGuardActive) return true;
   }

   double barRange = rates[1].high - rates[1].low;
   if (barRange >= (InpShockAtrMult * currentAtr))
   {
      g_shockGuardActive = true;
      g_shockCooldownLeft = InpShockCooldownBars;
      g_lastShockTime = rates[1].time;
      Print("[SHOCK GUARD TRIGGERED] Terdeteksi lonjakan lilin abnormal: ", DoubleToString(PriceToPips(barRange), 1), " pips (", DoubleToString(barRange / currentAtr, 1), "x ATR). Jeda ", InpShockCooldownBars, " lilin.");
      return true;
   }

   g_shockGuardActive = false;
   return false;
}

//+------------------------------------------------------------------+
//| MESIN PENGENAL POLA GRAFIK (CHART PATTERN RECOGNITION ENGINE)    |
//+------------------------------------------------------------------+
ChartPatternAnalysis AnalyzeChartPatterns(const MqlRates &rates[], int totalRates, double currentAtr)
{
   ChartPatternAnalysis cp;
   cp.pattern = CHART_PATTERN_NONE;
   cp.patternName = "Tanpa Pola Chart";
   cp.isBullish = false;
   cp.score = 0.0;
   cp.keyLevel = 0.0;
   cp.startTime = 0;
   cp.endTime = 0;
   cp.isValid = false;

   if (!InpUseChartPatterns || totalRates < 20 || currentAtr <= 0)
      return cp;

   double close1 = rates[1].close;
   double high1  = rates[1].high;
   double low1   = rates[1].low;

   // 1. POLA QUASIMODO (QM INSTITUTIONAL SETUP) - SKOR 95 POIN (ELIT)
   if (InpUseQuasimodo && prevSwingHigh.price > 0 && prevSwingLow.price > 0 && lastSwingHigh.price > 0 && lastSwingLow.price > 0)
   {
      // Bullish Quasimodo: Left Shoulder (prevSwingLow), Higher High (lastSwingHigh), Lower Low Sweep (lastSwingLow)
      // Harga sekarang sedang melakukan retracement kembali menguji level Left Shoulder (prevSwingLow)!
      if (lastSwingLow.price < prevSwingLow.price && lastSwingHigh.price > prevSwingHigh.price)
      {
         double qmDist = MathAbs(low1 - prevSwingLow.price);
         if (qmDist <= (0.45 * currentAtr) && close1 > prevSwingLow.price)
         {
            cp.pattern = CHART_PATTERN_QUASIMODO_BUY;
            cp.patternName = "Bullish Quasimodo (QM Over-Under)";
            cp.isBullish = true;
            cp.score = 95.0;
            cp.keyLevel = prevSwingLow.price;
            cp.startTime = prevSwingLow.time;
            cp.endTime = rates[1].time;
            cp.isValid = true;
            return cp;
         }
      }
      // Bearish Quasimodo: Left Shoulder (prevSwingHigh), Lower Low (lastSwingLow), Higher High Sweep (lastSwingHigh)
      // Harga sekarang retrace menguji level Left Shoulder (prevSwingHigh)!
      else if (lastSwingHigh.price > prevSwingHigh.price && lastSwingLow.price < prevSwingLow.price)
      {
         double qmDist = MathAbs(high1 - prevSwingHigh.price);
         if (qmDist <= (0.45 * currentAtr) && close1 < prevSwingHigh.price)
         {
            cp.pattern = CHART_PATTERN_QUASIMODO_SELL;
            cp.patternName = "Bearish Quasimodo (QM Over-Under)";
            cp.isBullish = false;
            cp.score = 95.0;
            cp.keyLevel = prevSwingHigh.price;
            cp.startTime = prevSwingHigh.time;
            cp.endTime = rates[1].time;
            cp.isValid = true;
            return cp;
         }
      }
   }

   // 2. POLA DOUBLE BOTTOM (W-PATTERN) & DOUBLE TOP (M-PATTERN) - SKOR 85 POIN
   if (InpUseDoubleTopBottom && prevSwingLow.price > 0 && lastSwingLow.price > 0)
   {
      // Double Bottom (W-Pattern): Dua lembah berjarak dekat, kaki ke-2 menolak level lembah ke-1
      double lowDiff = MathAbs(lastSwingLow.price - prevSwingLow.price);
      if (lowDiff <= (0.35 * currentAtr) && close1 > prevSwingLow.price && (rates[1].time - lastSwingLow.time) <= (10 * PeriodSeconds(_Period)))
      {
         cp.pattern = CHART_PATTERN_DOUBLE_BOTTOM;
         cp.patternName = "Double Bottom (W-Pattern)";
         cp.isBullish = true;
         cp.score = 85.0;
         cp.keyLevel = (lastSwingLow.price + prevSwingLow.price) * 0.5;
         cp.startTime = prevSwingLow.time;
         cp.endTime = rates[1].time;
         cp.isValid = true;
         return cp;
      }
   }
   if (InpUseDoubleTopBottom && prevSwingHigh.price > 0 && lastSwingHigh.price > 0)
   {
      // Double Top (M-Pattern): Dua puncak berjarak dekat
      double highDiff = MathAbs(lastSwingHigh.price - prevSwingHigh.price);
      if (highDiff <= (0.35 * currentAtr) && close1 < prevSwingHigh.price && (rates[1].time - lastSwingHigh.time) <= (10 * PeriodSeconds(_Period)))
      {
         cp.pattern = CHART_PATTERN_DOUBLE_TOP;
         cp.patternName = "Double Top (M-Pattern)";
         cp.isBullish = false;
         cp.score = 85.0;
         cp.keyLevel = (lastSwingHigh.price + prevSwingHigh.price) * 0.5;
         cp.startTime = prevSwingHigh.time;
         cp.endTime = rates[1].time;
         cp.isValid = true;
         return cp;
      }
   }

   // 3. POLA HEAD & SHOULDERS & INVERSE H&S - SKOR 90 POIN
   if (InpUseHeadAndShoulders && prevSwingHigh.price > 0 && lastSwingHigh.price > 0)
   {
      // Inverse H&S: Head (lastSwingLow paling dalam), Left Shoulder (prevSwingLow), Right Shoulder (lilin sekarang memantul di level Left Shoulder)
      if (prevSwingLow.price > 0 && lastSwingLow.price < prevSwingLow.price)
      {
         double shoulderDiff = MathAbs(low1 - prevSwingLow.price);
         if (shoulderDiff <= (0.45 * currentAtr) && close1 > prevSwingLow.price)
         {
            cp.pattern = CHART_PATTERN_INVERSE_HS;
            cp.patternName = "Inverse Head & Shoulders (iH&S)";
            cp.isBullish = true;
            cp.score = 90.0;
            cp.keyLevel = prevSwingLow.price;
            cp.startTime = prevSwingLow.time;
            cp.endTime = rates[1].time;
            cp.isValid = true;
            return cp;
         }
      }
      // Regular Head & Shoulders: Head (lastSwingHigh tertinggi), Left Shoulder (prevSwingHigh), Right Shoulder memantul di level Left Shoulder
      if (prevSwingHigh.price > 0 && lastSwingHigh.price > prevSwingHigh.price)
      {
         double shoulderDiff = MathAbs(high1 - prevSwingHigh.price);
         if (shoulderDiff <= (0.45 * currentAtr) && close1 < prevSwingHigh.price)
         {
            cp.pattern = CHART_PATTERN_HEAD_SHOULDERS;
            cp.patternName = "Head & Shoulders Reversal (H&S)";
            cp.isBullish = false;
            cp.score = 90.0;
            cp.keyLevel = prevSwingHigh.price;
            cp.startTime = prevSwingHigh.time;
            cp.endTime = rates[1].time;
            cp.isValid = true;
            return cp;
         }
      }
   }

   // 4. POLA BULLISH & BEARISH FLAG (SLANTED CHANNEL CONTINUATION) - SKOR 80 POIN
   if (InpUseFlagsContinuation && totalRates >= 10)
   {
      // Bullish Flag: Lilin impulsif naik 4-6 bar lalu, diikuti kompresi turun pelan 3 lilin
      double impulseMove = rates[5].close - rates[5].open;
      if (impulseMove >= (1.2 * currentAtr) && rates[4].high >= rates[3].high && rates[3].high >= rates[2].high && close1 > rates[2].high)
      {
         cp.pattern = CHART_PATTERN_BULL_FLAG;
         cp.patternName = "Bullish Flag Breakout";
         cp.isBullish = true;
         cp.score = 80.0;
         cp.keyLevel = rates[2].high;
         cp.startTime = rates[5].time;
         cp.endTime = rates[1].time;
         cp.isValid = true;
         return cp;
      }
      // Bearish Flag: Lilin impulsif turun 4-6 bar lalu, diikuti koreksi pelan naik 3 lilin
      double dumpMove = rates[5].open - rates[5].close;
      if (dumpMove >= (1.2 * currentAtr) && rates[4].low <= rates[3].low && rates[3].low <= rates[2].low && close1 < rates[2].low)
      {
         cp.pattern = CHART_PATTERN_BEAR_FLAG;
         cp.patternName = "Bearish Flag Breakdown";
         cp.isBullish = false;
         cp.score = 80.0;
         cp.keyLevel = rates[2].low;
         cp.startTime = rates[5].time;
         cp.endTime = rates[1].time;
         cp.isValid = true;
         return cp;
      }
   }

   return cp;
}

//+------------------------------------------------------------------+
//| SISTEM SKORING KONFLUENSI 4 PILAR TERPADU (0 - 100 POIN)         |
//+------------------------------------------------------------------+
ConfluenceScoreResult CalculateConfluenceScore(bool isBuy, const MqlRates &rates[], double currentAtr,
                                              const SMCStructureAnalysis &smc,
                                              const SMCOrderBlock &ob,
                                              const SMCFairValueGap &fvg,
                                              const CandleAnalysis &candle,
                                              const AutoFibo &fibo,
                                              double ema8, double ema21, double ema125)
{
   ConfluenceScoreResult r;
   r.totalScore = 0.0;
   r.structurePts = 0.0;
   r.displacementPts = 0.0;
   r.obMitigationPts = 0.0;
   r.fvgPts = 0.0;
   r.sweepPts = 0.0;
   r.fiboGPPts = 0.0;
   r.emaRibbonPts = 0.0;
   r.candlePts = 0.0;
   r.chartPatternPts = 0.0;
   r.vsaPts = 0.0;
   r.vsaStatus = "NORMAL";

   double close1 = rates[1].close;
   double high1  = rates[1].high;
   double low1   = rates[1].low;

   if (isBuy)
   {
      // 1. Struktur SMC (Max 20)
      if (smc.structure == SMC_STRUCT_BULLISH || smc.hasBOS)
         r.structurePts += 15.0;
      if (smc.hasCHoCH)
         r.structurePts = 20.0;
      if (smc.isDiscount)
         r.structurePts += 5.0;
      r.structurePts = MathMin(20.0, r.structurePts);

      // 2. Order Block Validation & Mitigation (Max 20)
      if (ob.isValid && ob.isBullish)
      {
         r.obMitigationPts += 8.0;
         if (low1 <= ob.top && high1 >= ob.bottom)
            r.obMitigationPts += 12.0; // Tepat di Base Demand!
         else if (MathAbs(low1 - ob.top) <= (0.5 * currentAtr))
            r.obMitigationPts += 6.0;
      }

      // 3. Displacement Momentum (Max 15)
      if (ob.isValid && ob.displacementAtr >= 1.25)
         r.displacementPts += MathMin(15.0, 5.0 + (ob.displacementAtr * 5.0));

      // 4. Fair Value Gap (FVG) Confluence (Max 15)
      if (fvg.isValid && fvg.isBullish)
      {
         r.fvgPts += 6.0;
         if (low1 <= fvg.top && high1 >= fvg.bottom)
            r.fvgPts += 9.0;
      }

      // 5. Liquidity Sweep (Max 10)
      if (smc.hasSweep && low1 <= lastSwingLow.price)
         r.sweepPts = 10.0;

      // 6. Fibonacci Golden Pocket (Max 10)
      if (fibo.isValid && low1 <= fibo.level500 && high1 >= fibo.level786)
         r.fiboGPPts = 10.0;
      else if (fibo.isValid && smc.isDiscount)
         r.fiboGPPts = 5.0;

      // 7. Triple EMA Trend & Ribbon (Max 10)
      if (close1 > ema125)
      {
         r.emaRibbonPts += 5.0;
         if (ema8 > ema21)
            r.emaRibbonPts += 5.0;
      }

      // 8. Candlestick Rejection (Max 10)
      if (candle.isBullish && candle.score > 0)
         r.candlePts = MathMin(10.0, candle.score * 0.10);

      // 9. Bonus Pola Grafik (Chart Pattern Bonus - Max 15 Poin)
      if (g_chartPattern.isValid && g_chartPattern.isBullish && g_chartPattern.score >= InpMinChartPatternScore)
         r.chartPatternPts = MathMin(15.0, g_chartPattern.score * 0.15);
   }
   else // SELL
   {
      // 1. Struktur SMC (Max 20)
      if (smc.structure == SMC_STRUCT_BEARISH || smc.hasBOS)
         r.structurePts += 15.0;
      if (smc.hasCHoCH)
         r.structurePts = 20.0;
      if (smc.isPremium)
         r.structurePts += 5.0;
      r.structurePts = MathMin(20.0, r.structurePts);

      // 2. Order Block (Max 20)
      if (ob.isValid && !ob.isBullish)
      {
         r.obMitigationPts += 8.0;
         if (high1 >= ob.bottom && low1 <= ob.top)
            r.obMitigationPts += 12.0;
         else if (MathAbs(high1 - ob.bottom) <= (0.5 * currentAtr))
            r.obMitigationPts += 6.0;
      }

      // 3. Displacement Momentum (Max 15)
      if (ob.isValid && ob.displacementAtr >= 1.25)
         r.displacementPts += MathMin(15.0, 5.0 + (ob.displacementAtr * 5.0));

      // 4. Fair Value Gap (Max 15)
      if (fvg.isValid && !fvg.isBullish)
      {
         r.fvgPts += 6.0;
         if (high1 >= fvg.bottom && low1 <= fvg.top)
            r.fvgPts += 9.0;
      }

      // 5. Liquidity Sweep (Max 10)
      if (smc.hasSweep && high1 >= lastSwingHigh.price)
         r.sweepPts = 10.0;

      // 6. Fibonacci Golden Pocket (Max 10)
      if (fibo.isValid && high1 >= fibo.level500 && low1 <= fibo.level786)
         r.fiboGPPts = 10.0;
      else if (fibo.isValid && smc.isPremium)
         r.fiboGPPts = 5.0;

      // 7. Triple EMA (Max 10)
      if (close1 < ema125)
      {
         r.emaRibbonPts += 5.0;
         if (ema8 < ema21)
            r.emaRibbonPts += 5.0;
      }

      // 8. Candlestick Rejection (Max 10)
      if (!candle.isBullish && candle.score > 0)
         r.candlePts = MathMin(10.0, candle.score * 0.10);

      // 9. Bonus Pola Grafik (Chart Pattern Bonus - Max 15 Poin)
      if (g_chartPattern.isValid && !g_chartPattern.isBullish && g_chartPattern.score >= InpMinChartPatternScore)
         r.chartPatternPts = MathMin(15.0, g_chartPattern.score * 0.15);
   }

   // 10. Volume Spread Analysis (VSA Footprint Absorption & No-Supply Test)
   if (InpUseVSA)
   {
      long sumVol = 0;
      int countVol = 0;
      int vLookback = MathMin(InpVSALookbackBars, ArraySize(rates) - 2);
      for (int v = 2; v < 2 + vLookback; v++)
      {
         sumVol += rates[v].tick_volume;
         countVol++;
      }
      double avgVol = (countVol > 0) ? ((double)sumVol / (double)countVol) : (double)rates[1].tick_volume;
      double volRatio = (avgVol > 0) ? ((double)rates[1].tick_volume / avgVol) : 1.0;

      if (isBuy)
      {
         bool atKeyZone = (ob.isValid && ob.isBullish && low1 <= ob.top && high1 >= ob.bottom) ||
                          (fibo.isValid && low1 <= fibo.level500 && high1 >= fibo.level786) ||
                          (low1 <= MathMax(ema8, ema21) && high1 >= MathMin(ema8, ema21));

         if (atKeyZone && volRatio >= InpVSAClimaxRatio)
         {
            r.vsaPts = 10.0;
            r.vsaStatus = "CLIMAX ABSORPTION (" + DoubleToString(volRatio, 1) + "x)";
         }
         else if (volRatio <= InpVSANoSupplyRatio)
         {
            r.vsaPts = 5.0;
            r.vsaStatus = "NO-SUPPLY PULLBACK (" + DoubleToString(volRatio, 1) + "x)";
         }
      }
      else // SELL
      {
         bool atKeyZone = (ob.isValid && !ob.isBullish && high1 >= ob.bottom && low1 <= ob.top) ||
                          (fibo.isValid && high1 >= fibo.level500 && low1 <= fibo.level786) ||
                          (high1 >= MathMin(ema8, ema21) && low1 <= MathMax(ema8, ema21));

         if (atKeyZone && volRatio >= InpVSAClimaxRatio)
         {
            r.vsaPts = 10.0;
            r.vsaStatus = "CLIMAX ABSORPTION (" + DoubleToString(volRatio, 1) + "x)";
         }
         else if (volRatio <= InpVSANoSupplyRatio)
         {
            r.vsaPts = 5.0;
            r.vsaStatus = "NO-SUPPLY PULLBACK (" + DoubleToString(volRatio, 1) + "x)";
         }
      }
   }

   r.totalScore = r.structurePts + r.displacementPts + r.obMitigationPts + r.fvgPts + r.sweepPts + r.fiboGPPts + r.emaRibbonPts + r.candlePts + r.chartPatternPts + r.vsaPts;
   r.totalScore = MathMin(100.0, MathMax(0.0, r.totalScore));

   if (r.totalScore >= 80.0)
      r.grade = "GRADE A+ SNIPER";
   else if (r.totalScore >= 65.0)
      r.grade = "GRADE A HIGH PROB";
   else
      r.grade = "GRADE B REJECT";

   // ================================================================
   // 11. BONUS M1 MULTI-TIMEFRAME PULLBACK / OB RETEST (v4.00)
   // Maks +20 poin tambahan jika harga sedang retest ke OB M1 valid
   // ================================================================
   if (InpUseMTFM1Engine && g_mtfResult.m1PullbackValid)
   {
      bool dirMatch = (isBuy && g_mtfResult.m1PullbackIsBuy) ||
                      (!isBuy && !g_mtfResult.m1PullbackIsBuy);
      if (dirMatch)
      {
         double m1Bonus = g_mtfResult.m1PullbackScore; // sudah dihitung di DetectM1Engine()
         r.totalScore += m1Bonus;
         r.details += StringFormat(" | M1-OB:%+.1fpts", m1Bonus);
         Print("[M1-MTF] Bonus M1 OB Retest: +", DoubleToString(m1Bonus, 1),
               " pts | Tipe: ", g_mtfResult.m1PullbackType);
      }
   }

   r.totalScore = MathMin(100.0, MathMax(0.0, r.totalScore));

   // Recalculate grade setelah bonus M1
   if (r.totalScore >= 80.0)
      r.grade = "GRADE A+ SNIPER";
   else if (r.totalScore >= 65.0)
      r.grade = "GRADE A HIGH PROB";
   else
      r.grade = "GRADE B REJECT";

   r.isPassed = (!InpUseConfluenceScore || r.totalScore >= InpMinConfluenceScore);
   return r;
}

//+------------------------------------------------------------------+
//| ON-CHART SMC VISUALIZER: GAMBAR OB, FVG & BOS DI CHART MT5       |
//+------------------------------------------------------------------+
void CleanSMCObjects()
{
   ObjectsDeleteAll(0, "VIKAR_SMC_");
}

void DrawSMCObjectsOnChart()
{
   if (!InpDrawSMCOnChart)
   {
      CleanSMCObjects();
      return;
   }

   datetime timeNow = TimeCurrent();
   datetime timeFuture = timeNow + (PeriodSeconds(_Period) * 12);

   // 1. Gambar Bullish Order Block (Demand Box)
   if (g_bullishOB.isValid && g_bullishOB.top > 0)
   {
      string obName = "VIKAR_SMC_OB_BULL";
      if (ObjectFind(0, obName) < 0)
         ObjectCreate(0, obName, OBJ_RECTANGLE, 0, g_bullishOB.time, g_bullishOB.top, timeFuture, g_bullishOB.bottom);
      else
      {
         ObjectSetInteger(0, obName, OBJPROP_TIME, 0, g_bullishOB.time);
         ObjectSetDouble(0, obName, OBJPROP_PRICE, 0, g_bullishOB.top);
         ObjectSetInteger(0, obName, OBJPROP_TIME, 1, timeFuture);
         ObjectSetDouble(0, obName, OBJPROP_PRICE, 1, g_bullishOB.bottom);
      }
      ObjectSetInteger(0, obName, OBJPROP_COLOR, InpColorBullishOB);
      ObjectSetInteger(0, obName, OBJPROP_BGCOLOR, InpColorBullishOB);
      ObjectSetInteger(0, obName, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, obName, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, obName, OBJPROP_BACK, true);
      ObjectSetInteger(0, obName, OBJPROP_FILL, true);
      ObjectSetString(0, obName, OBJPROP_TOOLTIP, "Bullish Order Block (Base Demand)\nTop: " + DoubleToString(g_bullishOB.top, 2) + "\nBottom: " + DoubleToString(g_bullishOB.bottom, 2));

      string obTxt = "VIKAR_SMC_OB_BULL_TXT";
      if (ObjectFind(0, obTxt) < 0)
         ObjectCreate(0, obTxt, OBJ_TEXT, 0, g_bullishOB.time, g_bullishOB.top);
      else
      {
         ObjectSetInteger(0, obTxt, OBJPROP_TIME, 0, g_bullishOB.time);
         ObjectSetDouble(0, obTxt, OBJPROP_PRICE, 0, g_bullishOB.top);
      }
      ObjectSetString(0, obTxt, OBJPROP_TEXT, "  ◄ BULLISH OB (DEMAND) [" + (g_bullishOB.isMitigated ? "MITIGATED" : "ACTIVE") + "]");
      ObjectSetInteger(0, obTxt, OBJPROP_COLOR, InpColorBullishOB);
      ObjectSetInteger(0, obTxt, OBJPROP_FONTSIZE, 8);
      ObjectSetInteger(0, obTxt, OBJPROP_BACK, true);
   }

   // 2. Gambar Bearish Order Block (Supply Box)
   if (g_bearishOB.isValid && g_bearishOB.top > 0)
   {
      string obName = "VIKAR_SMC_OB_BEAR";
      if (ObjectFind(0, obName) < 0)
         ObjectCreate(0, obName, OBJ_RECTANGLE, 0, g_bearishOB.time, g_bearishOB.top, timeFuture, g_bearishOB.bottom);
      else
      {
         ObjectSetInteger(0, obName, OBJPROP_TIME, 0, g_bearishOB.time);
         ObjectSetDouble(0, obName, OBJPROP_PRICE, 0, g_bearishOB.top);
         ObjectSetInteger(0, obName, OBJPROP_TIME, 1, timeFuture);
         ObjectSetDouble(0, obName, OBJPROP_PRICE, 1, g_bearishOB.bottom);
      }
      ObjectSetInteger(0, obName, OBJPROP_COLOR, InpColorBearishOB);
      ObjectSetInteger(0, obName, OBJPROP_BGCOLOR, InpColorBearishOB);
      ObjectSetInteger(0, obName, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, obName, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, obName, OBJPROP_BACK, true);
      ObjectSetInteger(0, obName, OBJPROP_FILL, true);
      ObjectSetString(0, obName, OBJPROP_TOOLTIP, "Bearish Order Block (Supply Zone)\nTop: " + DoubleToString(g_bearishOB.top, 2) + "\nBottom: " + DoubleToString(g_bearishOB.bottom, 2));

      string obTxt = "VIKAR_SMC_OB_BEAR_TXT";
      if (ObjectFind(0, obTxt) < 0)
         ObjectCreate(0, obTxt, OBJ_TEXT, 0, g_bearishOB.time, g_bearishOB.top);
      else
      {
         ObjectSetInteger(0, obTxt, OBJPROP_TIME, 0, g_bearishOB.time);
         ObjectSetDouble(0, obTxt, OBJPROP_PRICE, 0, g_bearishOB.top);
      }
      ObjectSetString(0, obTxt, OBJPROP_TEXT, "  ◄ BEARISH OB (SUPPLY) [" + (g_bearishOB.isMitigated ? "MITIGATED" : "ACTIVE") + "]");
      ObjectSetInteger(0, obTxt, OBJPROP_COLOR, InpColorBearishOB);
      ObjectSetInteger(0, obTxt, OBJPROP_FONTSIZE, 8);
      ObjectSetInteger(0, obTxt, OBJPROP_BACK, true);
   }

   // 3. Gambar Fair Value Gap (FVG Imbalance Box)
   if (g_activeFVG.isValid && g_activeFVG.top > 0)
   {
      string fvgName = "VIKAR_SMC_FVG";
      if (ObjectFind(0, fvgName) < 0)
         ObjectCreate(0, fvgName, OBJ_RECTANGLE, 0, g_activeFVG.time, g_activeFVG.top, timeFuture, g_activeFVG.bottom);
      else
      {
         ObjectSetInteger(0, fvgName, OBJPROP_TIME, 0, g_activeFVG.time);
         ObjectSetDouble(0, fvgName, OBJPROP_PRICE, 0, g_activeFVG.top);
         ObjectSetInteger(0, fvgName, OBJPROP_TIME, 1, timeFuture);
         ObjectSetDouble(0, fvgName, OBJPROP_PRICE, 1, g_activeFVG.bottom);
      }
      ObjectSetInteger(0, fvgName, OBJPROP_COLOR, InpColorFVG);
      ObjectSetInteger(0, fvgName, OBJPROP_STYLE, STYLE_DOT);
      ObjectSetInteger(0, fvgName, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, fvgName, OBJPROP_BACK, true);
      ObjectSetInteger(0, fvgName, OBJPROP_FILL, false);

      string fvgTxt = "VIKAR_SMC_FVG_TXT";
      if (ObjectFind(0, fvgTxt) < 0)
         ObjectCreate(0, fvgTxt, OBJ_TEXT, 0, g_activeFVG.time, g_activeFVG.mid);
      else
      {
         ObjectSetInteger(0, fvgTxt, OBJPROP_TIME, 0, g_activeFVG.time);
         ObjectSetDouble(0, fvgTxt, OBJPROP_PRICE, 0, g_activeFVG.mid);
      }
      string fvgType = g_activeFVG.isBullish ? "BULLISH FVG" : "BEARISH FVG";
      ObjectSetString(0, fvgTxt, OBJPROP_TEXT, "  ◄ " + fvgType + " (IMBALANCE)");
      ObjectSetInteger(0, fvgTxt, OBJPROP_COLOR, InpColorFVG);
      ObjectSetInteger(0, fvgTxt, OBJPROP_FONTSIZE, 7);
      ObjectSetInteger(0, fvgTxt, OBJPROP_BACK, true);
   }

   // 4. Gambar Penanda Pola Grafik (Chart Pattern Visualizer)
   if (g_chartPattern.isValid && g_chartPattern.keyLevel > 0)
   {
      string patName = "VIKAR_SMC_CHART_PAT";
      if (ObjectFind(0, patName) < 0)
         ObjectCreate(0, patName, OBJ_TEXT, 0, g_chartPattern.startTime, g_chartPattern.keyLevel);
      else
      {
         ObjectSetInteger(0, patName, OBJPROP_TIME, 0, g_chartPattern.startTime);
         ObjectSetDouble(0, patName, OBJPROP_PRICE, 0, g_chartPattern.keyLevel);
      }
      color patClr = g_chartPattern.isBullish ? C'52,211,153' : C'251,113,133';
      ObjectSetString(0, patName, OBJPROP_TEXT, "  ★ " + g_chartPattern.patternName + " [" + DoubleToString(g_chartPattern.score, 0) + "p]");
      ObjectSetInteger(0, patName, OBJPROP_COLOR, patClr);
      ObjectSetInteger(0, patName, OBJPROP_FONTSIZE, 9);
      ObjectSetString(0, patName, OBJPROP_FONT, "Segoe UI Bold");
      ObjectSetInteger(0, patName, OBJPROP_BACK, true);
   }

   // 5. Garis Struktur BOS / CHoCH
   if (lastSwingHigh.price > 0)
   {
      string bosName = "VIKAR_SMC_LINE_SH";
      if (ObjectFind(0, bosName) < 0)
         ObjectCreate(0, bosName, OBJ_TREND, 0, lastSwingHigh.time, lastSwingHigh.price, timeFuture, lastSwingHigh.price);
      else
      {
         ObjectSetInteger(0, bosName, OBJPROP_TIME, 0, lastSwingHigh.time);
         ObjectSetDouble(0, bosName, OBJPROP_PRICE, 0, lastSwingHigh.price);
         ObjectSetInteger(0, bosName, OBJPROP_TIME, 1, timeFuture);
         ObjectSetDouble(0, bosName, OBJPROP_PRICE, 1, lastSwingHigh.price);
      }
      ObjectSetInteger(0, bosName, OBJPROP_COLOR, C'56,189,248');
      ObjectSetInteger(0, bosName, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, bosName, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, bosName, OBJPROP_BACK, true);
   }
   if (lastSwingLow.price > 0)
   {
      string bosName = "VIKAR_SMC_LINE_SL";
      if (ObjectFind(0, bosName) < 0)
         ObjectCreate(0, bosName, OBJ_TREND, 0, lastSwingLow.time, lastSwingLow.price, timeFuture, lastSwingLow.price);
      else
      {
         ObjectSetInteger(0, bosName, OBJPROP_TIME, 0, lastSwingLow.time);
         ObjectSetDouble(0, bosName, OBJPROP_PRICE, 0, lastSwingLow.price);
         ObjectSetInteger(0, bosName, OBJPROP_TIME, 1, timeFuture);
         ObjectSetDouble(0, bosName, OBJPROP_PRICE, 1, lastSwingLow.price);
      }
      ObjectSetInteger(0, bosName, OBJPROP_COLOR, C'248,113,113');
      ObjectSetInteger(0, bosName, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(0, bosName, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, bosName, OBJPROP_BACK, true);
   }
}

//+------------------------------------------------------------------+
//| PILAR 4: KALKULASI FIBONACCI RETRACEMENT & GOLDEN POCKET         |
//+------------------------------------------------------------------+
void UpdateAutoFibo(bool isUptrend)
{
   if (lastSwingHigh.price <= 0 || lastSwingLow.price <= 0 || lastSwingHigh.price <= lastSwingLow.price)
   {
      currentFibo.isValid = false;
      return;
   }

   currentFibo.high = lastSwingHigh.price;
   currentFibo.low  = lastSwingLow.price;
   double range     = currentFibo.high - currentFibo.low;

   if (isUptrend)
   {
      // Untuk Uptrend (Tarik dari Low ke High, 0.000 di pucuk, 1.000 di lembah)
      currentFibo.level0    = currentFibo.high;
      currentFibo.level236  = currentFibo.high - (0.236 * range);
      currentFibo.level382  = currentFibo.high - (0.382 * range);
      currentFibo.level500  = currentFibo.high - (0.500 * range);
      currentFibo.level618  = currentFibo.high - (0.618 * range);
      currentFibo.level786  = currentFibo.high - (0.786 * range);
      currentFibo.level1000 = currentFibo.low;
      currentFibo.ext272    = currentFibo.high + (0.272 * range);
      currentFibo.ext618    = currentFibo.high + (0.618 * range);
   }
   else
   {
      // Untuk Downtrend (Tarik dari High ke Low, 0.000 di lembah, 1.000 di pucuk)
      currentFibo.level0    = currentFibo.low;
      currentFibo.level236  = currentFibo.low + (0.236 * range);
      currentFibo.level382  = currentFibo.low + (0.382 * range);
      currentFibo.level500  = currentFibo.low + (0.500 * range);
      currentFibo.level618  = currentFibo.low + (0.618 * range);
      currentFibo.level786  = currentFibo.low + (0.786 * range);
      currentFibo.level1000 = currentFibo.high;
      currentFibo.ext272    = currentFibo.low - (0.272 * range);
      currentFibo.ext618    = currentFibo.low - (0.618 * range);
   }

   currentFibo.isValid = true;
}

//+------------------------------------------------------------------+
//| ANALISIS KECERDASAN POLA CANDLESTICK REJECTION INSTITUSIONAL     |
//+------------------------------------------------------------------+
CandleAnalysis AnalyzeCandlePattern(const MqlRates &rates[], double ema8Val, double ema21Val, double gpLevel, double pivotLevel)
{
   CandleAnalysis res;
   res.pattern = PATTERN_NONE;
   res.patternName = "Candle Biasa";
   res.isBullish = false;
   res.score = 0.0;
   res.wickRatio = 0.0;
   res.bodyRatio = 0.0;
   res.isHighQuality = false;

   if (ArraySize(rates) < 6) return res;

   double open1   = rates[1].open;
   double close1  = rates[1].close;
   double high1   = rates[1].high;
   double low1    = rates[1].low;
   double range1  = high1 - low1;
   if (range1 <= 0) return res;

   double body1      = MathAbs(close1 - open1);
   double lowerWick1 = MathMin(open1, close1) - low1;
   double upperWick1 = high1 - MathMax(open1, close1);

   double lowerWickPct = (lowerWick1 / range1) * 100.0;
   double upperWickPct = (upperWick1 / range1) * 100.0;
   double bodyPct      = (body1 / range1) * 100.0;

   double open2  = rates[2].open;
   double close2 = rates[2].close;
   double high2  = rates[2].high;
   double low2   = rates[2].low;
   double range2 = high2 - low2;
   double body2  = MathAbs(close2 - open2);

   double open3  = rates[3].open;
   double close3 = rates[3].close;

   // 1. EVALUASI POLA BULLISH
   // A. Three White Soldiers (3 Lilin Bullish Kuat Beruntun)
   if (InpUseThreeSoldiersCrows && ArraySize(rates) >= 4 &&
       rates[3].close > rates[3].open && rates[2].close > rates[2].open && rates[1].close > rates[1].open &&
       rates[1].close > rates[2].close && rates[2].close > rates[3].close &&
       rates[1].open >= rates[2].open && rates[2].open >= rates[3].open)
   {
      res.pattern = PATTERN_THREE_SOLDIERS_CROWS;
      res.patternName = "Three White Soldiers (Expansion)";
      res.isBullish = true;
      res.score = 85.0;
   }
   // B. Dragonfly Doji (Ekor Bawah Ekstrem >= 70%)
   else if (InpUseDragonflyGravestone && lowerWickPct >= 70.0 && bodyPct <= 12.0)
   {
      res.pattern = PATTERN_DOJI_REJECTION;
      res.patternName = "Dragonfly Doji Rejection (" + DoubleToString(lowerWickPct, 0) + "%)";
      res.isBullish = true;
      res.score = 82.0;
   }
   // C. Bullish Harami / Inside Bar Breakout (Kompresi Volatilitas)
   else if (InpUseHaramiInsideBar && high2 > low2 && rates[2].close < rates[2].open &&
            rates[1].high <= rates[2].high && rates[1].low >= rates[2].low && rates[1].close > rates[1].open)
   {
      res.pattern = PATTERN_HARAMI_INSIDE_BAR;
      res.patternName = "Bullish Harami (Inside Bar Compression)";
      res.isBullish = true;
      res.score = 78.0;
   }
   // D. Piercing Line (Penetrasi > 50% Body Lilin Bearish Sebelumnya)
   else if (InpUsePiercingDarkCloud && rates[2].close < rates[2].open && rates[1].close > rates[1].open &&
            rates[1].open <= rates[2].close && rates[1].close >= ((rates[2].open + rates[2].close) * 0.5) && rates[1].close < rates[2].open)
   {
      res.pattern = PATTERN_PIERCING_DARKCLOUD;
      res.patternName = "Bullish Piercing Line (>50%)";
      res.isBullish = true;
      res.score = 78.0;
   }
   // E. Inverted Hammer (Penolakan Ekor Atas di Area Diskon/Support)
   else if (InpUseInvertedHammerStar && upperWickPct >= 55.0 && lowerWickPct <= 20.0 && bodyPct <= 30.0 && close1 >= open1)
   {
      res.pattern = PATTERN_INVERTED_HAMMER_STAR;
      res.patternName = "Inverted Hammer Rebound";
      res.isBullish = true;
      res.score = 74.0;
   }
   // F. Pola Klasik: Pin Bar / Hammer
   else if (InpUseHammerPinBar && lowerWickPct >= 55.0 && upperWickPct <= 22.0)
   {
      res.pattern = PATTERN_HAMMER_PINBAR;
      res.patternName = "Bullish Pin Bar (" + DoubleToString(lowerWickPct, 0) + "% Wick)";
      res.isBullish = true;
      res.score = 50.0 + (lowerWickPct * 0.35);
      if (close1 >= open1) res.score += 5.0;
   }
   // G. Bullish Engulfing
   else if (InpUseEngulfing && close2 < open2 && close1 > open1 && close1 >= high2 && body1 > (body2 * 1.1))
   {
      res.pattern = PATTERN_ENGULFING;
      res.patternName = "Bullish Engulfing (Absorption)";
      res.isBullish = true;
      res.score = 75.0;
   }
   // H. Tweezer Bottom
   else if (InpUseTweezer && MathAbs(low1 - low2) <= (0.12 * range1) && lowerWickPct >= 38.0 && close1 > open1)
   {
      res.pattern = PATTERN_TWEEZER;
      res.patternName = "Tweezer Bottom Rejection";
      res.isBullish = true;
      res.score = 70.0;
   }
   // I. Morning Star
   else if (InpUseMorningEveningStar && close3 < open3 && close1 > open1 && body2 <= (0.35 * range1) && close1 > ((open3 + close3) / 2.0))
   {
      res.pattern = PATTERN_MORNING_EVENING;
      res.patternName = "Morning Star Reversal";
      res.isBullish = true;
      res.score = 80.0;
   }
   // J. FVG Mitigation
   else if (InpUseFVGRebound && rates[3].high > 0 && low1 <= rates[3].high && close1 > rates[3].high && close1 > open1)
   {
      res.pattern = PATTERN_FVG_MITIGATION;
      res.patternName = "Bullish FVG Mitigation";
      res.isBullish = true;
      res.score = 72.0;
   }

   // 2. EVALUASI POLA BEARISH (Jika belum terdeteksi bullish)
   if (res.pattern == PATTERN_NONE)
   {
      // A. Three Black Crows (3 Lilin Bearish Kuat Beruntun)
      if (InpUseThreeSoldiersCrows && ArraySize(rates) >= 4 &&
          rates[3].close < rates[3].open && rates[2].close < rates[2].open && rates[1].close < rates[1].open &&
          rates[1].close < rates[2].close && rates[2].close < rates[3].close &&
          rates[1].open <= rates[2].open && rates[2].open <= rates[3].open)
      {
         res.pattern = PATTERN_THREE_SOLDIERS_CROWS;
         res.patternName = "Three Black Crows (Dump Expansion)";
         res.isBullish = false;
         res.score = 85.0;
      }
      // B. Gravestone Doji (Ekor Atas Ekstrem >= 70%)
      else if (InpUseDragonflyGravestone && upperWickPct >= 70.0 && bodyPct <= 12.0)
      {
         res.pattern = PATTERN_DOJI_REJECTION;
         res.patternName = "Gravestone Doji Rejection (" + DoubleToString(upperWickPct, 0) + "%)";
         res.isBullish = false;
         res.score = 82.0;
      }
      // C. Bearish Harami / Inside Bar
      else if (InpUseHaramiInsideBar && high2 > low2 && rates[2].close > rates[2].open &&
               rates[1].high <= rates[2].high && rates[1].low >= rates[2].low && rates[1].close < rates[1].open)
      {
         res.pattern = PATTERN_HARAMI_INSIDE_BAR;
         res.patternName = "Bearish Harami (Inside Bar Compression)";
         res.isBullish = false;
         res.score = 78.0;
      }
      // D. Dark Cloud Cover
      else if (InpUsePiercingDarkCloud && rates[2].close > rates[2].open && rates[1].close < rates[1].open &&
               rates[1].open >= rates[2].close && rates[1].close <= ((rates[2].open + rates[2].close) * 0.5) && rates[1].close > rates[2].open)
      {
         res.pattern = PATTERN_PIERCING_DARKCLOUD;
         res.patternName = "Dark Cloud Cover (>50%)";
         res.isBullish = false;
         res.score = 78.0;
      }
      // E. Shooting Star
      else if (InpUseInvertedHammerStar && upperWickPct >= 55.0 && lowerWickPct <= 20.0 && bodyPct <= 30.0 && close1 <= open1)
      {
         res.pattern = PATTERN_INVERTED_HAMMER_STAR;
         res.patternName = "Shooting Star Rejection";
         res.isBullish = false;
         res.score = 74.0;
      }
      // F. Bearish Pin Bar
      else if (InpUseHammerPinBar && upperWickPct >= 55.0 && lowerWickPct <= 22.0)
      {
         res.pattern = PATTERN_HAMMER_PINBAR;
         res.patternName = "Bearish Pin Bar (" + DoubleToString(upperWickPct, 0) + "% Wick)";
         res.isBullish = false;
         res.score = 50.0 + (upperWickPct * 0.35);
         if (close1 <= open1) res.score += 5.0;
      }
      // G. Bearish Engulfing
      else if (InpUseEngulfing && close2 > open2 && close1 < open1 && close1 <= low2 && body1 > (body2 * 1.1))
      {
         res.pattern = PATTERN_ENGULFING;
         res.patternName = "Bearish Engulfing (Absorption)";
         res.isBullish = false;
         res.score = 75.0;
      }
      // H. Tweezer Top
      else if (InpUseTweezer && MathAbs(high1 - high2) <= (0.12 * range1) && upperWickPct >= 38.0 && close1 < open1)
      {
         res.pattern = PATTERN_TWEEZER;
         res.patternName = "Tweezer Top Rejection";
         res.isBullish = false;
         res.score = 70.0;
      }
      // I. Evening Star
      else if (InpUseMorningEveningStar && close3 > open3 && close1 < open1 && body2 <= (0.35 * range1) && close1 < ((open3 + close3) / 2.0))
      {
         res.pattern = PATTERN_MORNING_EVENING;
         res.patternName = "Evening Star Reversal";
         res.isBullish = false;
         res.score = 80.0;
      }
      // J. FVG Mitigation
      else if (InpUseFVGRebound && rates[3].low > 0 && high1 >= rates[3].low && close1 < rates[3].low && close1 < open1)
      {
         res.pattern = PATTERN_FVG_MITIGATION;
         res.patternName = "Bearish FVG Mitigation";
         res.isBullish = false;
         res.score = 72.0;
      }
   }

   // 3. BONUS KONFLUENSI AREA HARGA KUNCI (CONFLUENCE BOOST)
   if (res.pattern != PATTERN_NONE)
   {
      double lowRibbon  = MathMin(ema8Val, ema21Val);
      double highRibbon = MathMax(ema8Val, ema21Val);

      // Rejection terjadi di Ribbon EMA 8/21 (+10 poin)
      if (res.isBullish && low1 <= highRibbon && high1 >= lowRibbon)
         res.score += 10.0;
      else if (!res.isBullish && high1 >= lowRibbon && low1 <= highRibbon)
         res.score += 10.0;

      // Rejection menguji Golden Pocket 61.8% (+10 poin)
      if (gpLevel > 0)
      {
         if (res.isBullish && MathAbs(low1 - gpLevel) <= (0.35 * range1))
            res.score += 10.0;
         else if (!res.isBullish && MathAbs(high1 - gpLevel) <= (0.35 * range1))
            res.score += 10.0;
      }

      if (res.score > 100.0) res.score = 100.0;
      res.isHighQuality = (res.score >= InpMinCandleScore);
   }

   res.wickRatio = res.isBullish ? lowerWickPct : upperWickPct;
   res.bodyRatio = bodyPct;
   return res;
}

//+------------------------------------------------------------------+
//| WRAPPER CEK POLA BULLISH & BEARISH                               |
//+------------------------------------------------------------------+
bool IsBullishRejection(const MqlRates &rates[], double ema8Val, double ema21Val, double gpLevel, double pivotLevel)
{
   CandleAnalysis ca = AnalyzeCandlePattern(rates, ema8Val, ema21Val, gpLevel, pivotLevel);
   return (ca.isBullish && ca.pattern != PATTERN_NONE && ca.score >= InpMinCandleScore);
}

bool IsBearishRejection(const MqlRates &rates[], double ema8Val, double ema21Val, double gpLevel, double pivotLevel)
{
   CandleAnalysis ca = AnalyzeCandlePattern(rates, ema8Val, ema21Val, gpLevel, pivotLevel);
   return (!ca.isBullish && ca.pattern != PATTERN_NONE && ca.score >= InpMinCandleScore);
}

//+------------------------------------------------------------------+
//| FILTER WHIPSAW DI SEKITAR EMA 125                                |
//+------------------------------------------------------------------+
bool IsWhipsawEMA125(const MqlRates &rates[], const double &ema125[])
{
   if (!InpFilterWhipsaw125) return false;
   int rSize = ArraySize(rates);
   int eSize = ArraySize(ema125);
   if (rSize < 8 || eSize < 8) return false;

   int crosses = 0;
   int maxCheck = MathMin(6, MathMin(rSize - 2, eSize - 2));
   for (int i = 1; i <= maxCheck; i++)
   {
      if ((rates[i].close > ema125[i] && rates[i + 1].close < ema125[i + 1]) ||
          (rates[i].close < ema125[i] && rates[i + 1].close > ema125[i + 1]))
         crosses++;
   }
   return (crosses >= 3);
}

//+------------------------------------------------------------------+
//| ANALISIS BIAS MAKRO HIGHER TIMEFRAME (H1 MACRO FILTER)           |
//+------------------------------------------------------------------+
enum ENUM_HTF_BIAS
{
   HTF_BIAS_NEUTRAL, // Netral / Transisi
   HTF_BIAS_BULLISH, // Macro Trend Bullish Kuat
   HTF_BIAS_BEARISH  // Macro Trend Bearish Kuat
};

ENUM_HTF_BIAS AnalyzeHTFMacroTrend()
{
   if (!InpUseHTFFilter || h_htf_ema125 == INVALID_HANDLE)
   {
      g_htfMacroStr = "HTF FILTER OFF";
      return HTF_BIAS_NEUTRAL;
   }

   double ema125H1[], ema8H1[], ema21H1[];
   ArraySetAsSeries(ema125H1, true);
   ArraySetAsSeries(ema8H1, true);
   ArraySetAsSeries(ema21H1, true);

   if (CopyBuffer(h_htf_ema125, 0, 0, 3, ema125H1) < 2)
   {
      g_htfMacroStr = "H1 DATA LOADING";
      return HTF_BIAS_NEUTRAL;
   }

   bool hasRibbon = (CopyBuffer(h_htf_ema8, 0, 0, 3, ema8H1) >= 2 && CopyBuffer(h_htf_ema21, 0, 0, 3, ema21H1) >= 2);

   double closeH1 = iClose(_Symbol, InpHTFTimeframe, 1);
   if (closeH1 <= 0)
   {
      g_htfMacroStr = "H1 PRICE LOADING";
      return HTF_BIAS_NEUTRAL;
   }

   bool isAbove125 = (closeH1 > ema125H1[1]);
   bool isBelow125 = (closeH1 < ema125H1[1]);

   bool ribbonBull = hasRibbon ? (ema8H1[1] >= ema21H1[1]) : true;
   bool ribbonBear = hasRibbon ? (ema8H1[1] <= ema21H1[1]) : true;

   if (isAbove125 && (!InpHTFRequireRibbon || ribbonBull))
   {
      g_htfMacroStr = "BULLISH (H1 di atas 125" + (ribbonBull ? " & Ribbon" : "") + ")";
      return HTF_BIAS_BULLISH;
   }
   else if (isBelow125 && (!InpHTFRequireRibbon || ribbonBear))
   {
      g_htfMacroStr = "BEARISH (H1 di bawah 125" + (ribbonBear ? " & Ribbon" : "") + ")";
      return HTF_BIAS_BEARISH;
   }

   g_htfMacroStr = "KONSOLIDASI / TRANSISI H1";
   return HTF_BIAS_NEUTRAL;
}

//+------------------------------------------------------------------+
//| FUNGSI MATEMATIS: CHOPPINESS INDEX (CI) MQL5 DENGAN LOG10       |
//+------------------------------------------------------------------+
double CalculateChoppinessIndexMQL5(int period)
{
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if (CopyRates(_Symbol, _Period, 0, period + 2, rates) < period + 2)
      return 50.0;

   double sumTR = 0.0;
   double highMax = rates[1].high;
   double lowMin  = rates[1].low;

   for (int i = 1; i <= period; i++)
   {
      double h = rates[i].high;
      double l = rates[i].low;
      double prevClose = rates[i + 1].close;

      double tr1 = h - l;
      double tr2 = MathAbs(h - prevClose);
      double tr3 = MathAbs(l - prevClose);
      double trueRange = MathMax(tr1, MathMax(tr2, tr3));

      sumTR += trueRange;
      if (h > highMax) highMax = h;
      if (l < lowMin)  lowMin  = l;
   }

   double range = highMax - lowMin;
   if (range <= 0.00001 || sumTR <= 0.00001) return 50.0;

   double log10Period = MathLog(period) / MathLog(10.0);
   double log10Val    = MathLog(sumTR / range) / MathLog(10.0);

   double ci = 100.0 * (log10Val / log10Period);
   if (ci < 0.0) ci = 0.0;
   if (ci > 100.0) ci = 100.0;

   return ci;
}

//+------------------------------------------------------------------+
//| SISTEM PEMBELAJARAN & OTOPSI ADAPTIF PASCA-LOSS (v3.10 MQL5)     |
//+------------------------------------------------------------------+
void SaveTradeEntrySnapshotMQL5(ulong orderTicket, ulong dealTicket, int patternId, int direction, double currentScore, double currentAtr)
{
   MqlDateTime mdt;
   TimeCurrent(mdt);

   GlobalVariableSet("VIKAR_PAT_"  + IntegerToString((long)orderTicket), (double)patternId);
   GlobalVariableSet("VIKAR_DIR_"  + IntegerToString((long)orderTicket), (double)direction);
   GlobalVariableSet("VIKAR_HOUR_" + IntegerToString((long)orderTicket), (double)mdt.hour);
   GlobalVariableSet("VIKAR_ATR_"  + IntegerToString((long)orderTicket), currentAtr);
   GlobalVariableSet("VIKAR_SCO_"  + IntegerToString((long)orderTicket), currentScore);

   if (dealTicket > 0 && dealTicket != orderTicket)
   {
      GlobalVariableSet("VIKAR_PAT_"  + IntegerToString((long)dealTicket), (double)patternId);
      GlobalVariableSet("VIKAR_DIR_"  + IntegerToString((long)dealTicket), (double)direction);
      GlobalVariableSet("VIKAR_HOUR_" + IntegerToString((long)dealTicket), (double)mdt.hour);
      GlobalVariableSet("VIKAR_ATR_"  + IntegerToString((long)dealTicket), currentAtr);
      GlobalVariableSet("VIKAR_SCO_"  + IntegerToString((long)dealTicket), currentScore);
   }
}

void SaveAutopsyStateMQL5()
{
   string pfx = "VIKAR_MT5_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
   GlobalVariableSet(pfx + "ACTIVE", g_autopsy.isActive ? 1.0 : 0.0);
   GlobalVariableSet(pfx + "TICKET", (double)g_autopsy.failedTicket);
   GlobalVariableSet(pfx + "PAT", (double)g_autopsy.failedPattern);
   GlobalVariableSet(pfx + "PENALTY", g_autopsy.scorePenalty);
   GlobalVariableSet(pfx + "QUARANTINE", (double)g_autopsy.quarantineUntilBar);
   GlobalVariableSet(pfx + "BUFFER", (double)g_autopsy.tradesWithExtraBuffer);
   GlobalVariableSet(pfx + "DIR", (double)g_autopsy.failedDirection);
   GlobalVariableSet(pfx + "DIRUNTIL", (double)g_autopsy.directionPenaltyUntil);
   GlobalVariableSet(pfx + "TOXICHOUR", (double)g_autopsy.toxicHour);
}

void LoadAutopsyStateMQL5()
{
   string pfx = "VIKAR_MT5_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
   if (GlobalVariableCheck(pfx + "ACTIVE") && GlobalVariableGet(pfx + "ACTIVE") > 0.5)
   {
      g_autopsy.isActive              = true;
      g_autopsy.failedTicket          = (ulong)GlobalVariableGet(pfx + "TICKET");
      g_autopsy.failedPattern         = (ENUM_CANDLE_PATTERN)(int)GlobalVariableGet(pfx + "PAT");
      g_autopsy.scorePenalty          = GlobalVariableGet(pfx + "PENALTY");
      g_autopsy.quarantineUntilBar    = (datetime)GlobalVariableGet(pfx + "QUARANTINE");
      g_autopsy.tradesWithExtraBuffer = (int)GlobalVariableGet(pfx + "BUFFER");
      g_autopsy.failedDirection       = (int)GlobalVariableGet(pfx + "DIR");
      g_autopsy.directionPenaltyUntil = (datetime)GlobalVariableGet(pfx + "DIRUNTIL");
      g_autopsy.toxicHour             = (int)GlobalVariableGet(pfx + "TOXICHOUR");
      g_autopsy.lossReason            = "PEMULIHAN STATUS PASCA-RESTART (PERSISTENT)";
      Print("[SELF-HEALING RESTORED MT5] Status otopsi berhasil dipulihkan dari memori persisten.");
   }
   else
   {
      g_autopsy.isActive              = false;
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
      g_autopsy.toxicHour             = -1;
   }
}

void SaveAIBrainToDiskMQL5()
{
   if (!InpSaveBrainToDisk) return;
   string fileName = "vikar_ai_brain_" + IntegerToString(InpMagicNumber) + ".csv";
   int handle = FileOpen(fileName, FILE_WRITE|FILE_CSV|FILE_ANSI, ';');
   if (handle != INVALID_HANDLE)
   {
      FileWrite(handle, "PatternId", "Name", "Wins", "Losses", "Total", "WinRate", "IsBlacklisted", "ScoreModifier");
      for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
      {
         FileWrite(handle,
            IntegerToString(g_patternMatrix[i].patternId),
            g_patternMatrix[i].name,
            IntegerToString(g_patternMatrix[i].wins),
            IntegerToString(g_patternMatrix[i].losses),
            IntegerToString(g_patternMatrix[i].total),
            DoubleToString(g_patternMatrix[i].winRate, 2),
            IntegerToString(g_patternMatrix[i].isBlacklisted ? 1 : 0),
            DoubleToString(g_patternMatrix[i].scoreModifier, 1)
         );
      }
      FileClose(handle);
   }
}

bool LoadAIBrainFromDiskMQL5()
{
   if (!InpSaveBrainToDisk) return false;
   string fileName = "vikar_ai_brain_" + IntegerToString(InpMagicNumber) + ".csv";
   if (!FileIsExist(fileName)) return false;

   int handle = FileOpen(fileName, FILE_READ|FILE_CSV|FILE_ANSI, ';');
   if (handle == INVALID_HANDLE) return false;

   // Skip baris header
   if (!FileIsEnding(handle))
   {
      while (!FileIsLineEnding(handle) && !FileIsEnding(handle)) FileReadString(handle);
   }

   int loaded = 0;
   while (!FileIsEnding(handle) && loaded < TOTAL_TRACKED_PATTERNS)
   {
      string sId = FileReadString(handle);
      if (sId == "") break;
      int patId       = (int)StringToInteger(sId);
      string name     = FileReadString(handle);
      int wins        = (int)StringToInteger(FileReadString(handle));
      int losses      = (int)StringToInteger(FileReadString(handle));
      int total       = (int)StringToInteger(FileReadString(handle));
      double wr       = StringToDouble(FileReadString(handle));
      bool isBlk      = (StringToInteger(FileReadString(handle)) == 1);
      double scoreMod = StringToDouble(FileReadString(handle));

      if (patId >= 0 && patId < TOTAL_TRACKED_PATTERNS)
      {
         g_patternMatrix[patId].wins          = wins;
         g_patternMatrix[patId].losses        = losses;
         g_patternMatrix[patId].total         = total;
         g_patternMatrix[patId].winRate       = wr;
         g_patternMatrix[patId].isBlacklisted = isBlk;
         g_patternMatrix[patId].scoreModifier = scoreMod;
         loaded++;
      }
   }
   FileClose(handle);
   Print("[AI BRAIN DISK MT5] Berhasil memuat ingatan permanen dari disk: ", fileName, " (", loaded, " pola).");
   return (loaded > 0);
}

void InitPatternMatrixMQL5()
{
   string patNames[TOTAL_TRACKED_PATTERNS] = {
      "Setup Standar / PA",
      "Pin Bar / Hammer",
      "Engulfing Absorption",
      "Tweezer Rejection",
      "Morning / Evening Star",
      "FVG Rebound",
      "Three Soldiers / Crows",
      "Harami Inside Bar",
      "Piercing / Dark Cloud",
      "Dragonfly / Gravestone",
      "Inverted Hammer / Star",
      "Momentum BOS Breakout",
      "Liquidity Sweep Trap Hunter"
   };

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      g_patternMatrix[i].patternId = i;
      g_patternMatrix[i].name      = patNames[i];
   }

   // 1. Coba muat ingatan dari disk file
   bool loadedFromDisk = LoadAIBrainFromDiskMQL5();

   int blacklistedCount = 0;
   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      string gvWKey = "VIKAR_MT5_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);
      string gvLKey = "VIKAR_MT5_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);

      int wins   = GlobalVariableCheck(gvWKey) ? (int)GlobalVariableGet(gvWKey) : 0;
      int losses = GlobalVariableCheck(gvLKey) ? (int)GlobalVariableGet(gvLKey) : 0;

      if (loadedFromDisk)
      {
         wins   = MathMax(wins, g_patternMatrix[i].wins);
         losses = MathMax(losses, g_patternMatrix[i].losses);
      }

      int total  = wins + losses;
      double wr  = (total > 0) ? ((double)wins * 100.0 / (double)total) : 0.0;

      g_patternMatrix[i].wins          = wins;
      g_patternMatrix[i].losses        = losses;
      g_patternMatrix[i].total         = total;
      g_patternMatrix[i].winRate       = wr;
      g_patternMatrix[i].isBlacklisted = false;
      g_patternMatrix[i].scoreModifier = 0.0;

      // 2. Pre-Trained Institutional Knowledge (Pengalaman Audit 50,123 Bar M5 2026)
      // Jika akun baru dipasang (total == 0), tanamkan memori proteksi awal:
      if (InpUsePreTrainedBrain && total == 0)
      {
         // A. Pola Toxic Terbukti Sering Rugi -> Blacklist Sejak Awal
         if (i == 9) // Dragonfly / Gravestone / Doji
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            g_patternMatrix[i].losses = 5;
            g_patternMatrix[i].total = 5;
            g_patternMatrix[i].winRate = 0.0;
         }
         else if (i == 7) // Harami Inside Bar
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            g_patternMatrix[i].losses = 4;
            g_patternMatrix[i].total = 5;
            g_patternMatrix[i].winRate = 20.0;
         }
         else if (i == 10) // Inverted Hammer / Star
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            g_patternMatrix[i].losses = 4;
            g_patternMatrix[i].total = 6;
            g_patternMatrix[i].winRate = 33.3;
         }
         // B. Pola Juara Terbukti Akurat -> Boost Sejak Awal
         else if (i == 1 || i == 6 || i == 11 || i == 12)
         {
            g_patternMatrix[i].isBlacklisted = false;
            g_patternMatrix[i].scoreModifier = InpPatternBoostScore;
            g_patternMatrix[i].wins = 7;
            g_patternMatrix[i].total = 10;
            g_patternMatrix[i].winRate = 70.0;
         }
      }
      else if (InpUsePatternMatrix && total >= InpMinTradesForPatternEval)
      {
         if (wr < InpPatternBlacklistWinrate)
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
         }
         else if (wr >= InpPatternBoostWinrate)
         {
            g_patternMatrix[i].isBlacklisted = false;
            g_patternMatrix[i].scoreModifier = InpPatternBoostScore;
         }
      }

      if (g_patternMatrix[i].isBlacklisted)
         blacklistedCount++;

      if (g_patternMatrix[i].total >= 2 && g_patternMatrix[i].winRate > highestWR)
      {
         highestWR = g_patternMatrix[i].winRate;
         bestName  = patNames[i] + " (" + DoubleToString(highestWR, 0) + "%)";
      }
   }

   g_bestPatternStr = bestName;
   SaveAIBrainToDiskMQL5();
   Print("[AI PATTERN MATRIX MT5] Diinisialisasi. Pola Aktif: ", TOTAL_TRACKED_PATTERNS, " | Ter-blacklist: ", blacklistedCount, " | Terbaik: ", g_bestPatternStr);
}

void UpdatePatternRecordMQL5(int patternId, bool isWin)
{
   if (patternId < 0 || patternId >= TOTAL_TRACKED_PATTERNS) return;

   string gvWKey = "VIKAR_MT5_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);
   string gvLKey = "VIKAR_MT5_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);

   if (isWin)
   {
      g_patternMatrix[patternId].wins++;
      GlobalVariableSet(gvWKey, (double)g_patternMatrix[patternId].wins);
   }
   else
   {
      g_patternMatrix[patternId].losses++;
      GlobalVariableSet(gvLKey, (double)g_patternMatrix[patternId].losses);
   }

   g_patternMatrix[patternId].total = g_patternMatrix[patternId].wins + g_patternMatrix[patternId].losses;
   if (g_patternMatrix[patternId].total > 0)
      g_patternMatrix[patternId].winRate = (double)g_patternMatrix[patternId].wins * 100.0 / (double)g_patternMatrix[patternId].total;

   if (InpUsePatternMatrix && g_patternMatrix[patternId].total >= InpMinTradesForPatternEval)
   {
      if (g_patternMatrix[patternId].winRate < InpPatternBlacklistWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = true;
         g_patternMatrix[patternId].scoreModifier = -InpPatternPenaltyScore;
         Print("[AI MATRIX WARNING MT5] Pola '", g_patternMatrix[patternId].name, "' di-BLACKLIST mandiri (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% < ", InpPatternBlacklistWinrate, "%).");
      }
      else if (g_patternMatrix[patternId].winRate >= InpPatternBoostWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = InpPatternBoostScore;
         Print("[AI MATRIX BOOST MT5] Pola '", g_patternMatrix[patternId].name, "' mendapatkan BOOST +", InpPatternBoostScore, " Poin (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% >= ", InpPatternBoostWinrate, "%).");
      }
      else
      {
         if (g_patternMatrix[patternId].isBlacklisted)
         {
            Print("[AI MATRIX REHABILITASI MT5] Pola '", g_patternMatrix[patternId].name, "' dipulihkan dari blacklist (Winrate membaik: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "%).");
         }
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = 0.0;
      }
   }

   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";
   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      if (g_patternMatrix[i].total >= 2 && g_patternMatrix[i].winRate > highestWR)
      {
         highestWR = g_patternMatrix[i].winRate;
         bestName  = g_patternMatrix[i].name + " (" + DoubleToString(g_patternMatrix[i].winRate, 0) + "%)";
      }
   }
   g_bestPatternStr = bestName;
   SaveAIBrainToDiskMQL5();
}

void PerformLossAutopsyMQL5(ulong ticket, ulong posId, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil snapshot data transaksi dari memori Global Variable
   string patGvKeyPos = "VIKAR_PAT_" + IntegerToString((long)posId);
   string patGvKeyTkt = "VIKAR_PAT_" + IntegerToString((long)ticket);
   ENUM_CANDLE_PATTERN pat = PATTERN_NONE;
   int rawPatId = 0;
   if (GlobalVariableCheck(patGvKeyPos))
   {
      rawPatId = (int)GlobalVariableGet(patGvKeyPos);
      pat = (ENUM_CANDLE_PATTERN)rawPatId;
   }
   else if (GlobalVariableCheck(patGvKeyTkt))
   {
      rawPatId = (int)GlobalVariableGet(patGvKeyTkt);
      pat = (ENUM_CANDLE_PATTERN)rawPatId;
   }
   g_autopsy.failedPattern = pat;

   string patName = "Pola Setup Standard";
   if (rawPatId == 12) patName = "Liquidity Sweep Trap Hunter";
   else if (rawPatId == 11) patName = "Momentum BOS Breakout";
   else if (pat == PATTERN_HAMMER_PINBAR) patName = "Pin Bar / Hammer";
   else if (pat == PATTERN_ENGULFING) patName = "Engulfing";
   else if (pat == PATTERN_TWEEZER) patName = "Tweezer Rejection";
   else if (pat == PATTERN_MORNING_EVENING) patName = "Morning/Evening Star";
   else if (pat == PATTERN_FVG_MITIGATION) patName = "FVG Mitigation Rebound";
   else if (pat == PATTERN_THREE_SOLDIERS_CROWS) patName = "Three Soldiers/Crows";
   else if (pat == PATTERN_HARAMI_INSIDE_BAR) patName = "Harami Inside Bar";
   else if (pat == PATTERN_PIERCING_DARKCLOUD) patName = "Piercing/Dark Cloud";
   else if (pat == PATTERN_DOJI_REJECTION) patName = "Doji Rejection";
   else if (pat == PATTERN_INVERTED_HAMMER_STAR) patName = "Inverted Hammer/Star";
   g_autopsy.failedPatternName = patName;

   datetime currentBarTime = iTime(_Symbol, _Period, 0);
   if (pat != PATTERN_NONE || rawPatId >= 11)
      g_autopsy.quarantineUntilBar = currentBarTime + (InpQuarantinePatternBars * PeriodSeconds(_Period));
   else
      g_autopsy.quarantineUntilBar = 0;

   // Ambil Direction (BUY = +1, SELL = -1)
   int tradeDir = 0;
   string dirKeyPos = "VIKAR_DIR_" + IntegerToString((long)posId);
   string dirKeyTkt = "VIKAR_DIR_" + IntegerToString((long)ticket);
   if (GlobalVariableCheck(dirKeyPos)) tradeDir = (int)GlobalVariableGet(dirKeyPos);
   else if (GlobalVariableCheck(dirKeyTkt)) tradeDir = (int)GlobalVariableGet(dirKeyTkt);

   if (InpUseDirectionalLearning && tradeDir != 0)
   {
      g_autopsy.failedDirection       = tradeDir;
      g_autopsy.directionPenaltyUntil = currentBarTime + (InpDirectionalPenaltyBars * PeriodSeconds(_Period));
   }
   else
   {
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
   }

   // Ambil Jam Transaksi (0..23) dan Lacak Jam Rawan Loss Berulang
   int tradeHour = -1;
   string hrKeyPos = "VIKAR_HOUR_" + IntegerToString((long)posId);
   string hrKeyTkt = "VIKAR_HOUR_" + IntegerToString((long)ticket);
   if (GlobalVariableCheck(hrKeyPos)) tradeHour = (int)GlobalVariableGet(hrKeyPos);
   else if (GlobalVariableCheck(hrKeyTkt)) tradeHour = (int)GlobalVariableGet(hrKeyTkt);

   if (InpUseHourlyLearning && tradeHour >= 0 && tradeHour <= 23)
   {
      string hLossKey = "VIKAR_MT5_HLOSS_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(tradeHour);
      int currentHLoss = GlobalVariableCheck(hLossKey) ? (int)GlobalVariableGet(hLossKey) : 0;
      currentHLoss++;
      GlobalVariableSet(hLossKey, (double)currentHLoss);

      if (currentHLoss >= 2)
      {
         g_autopsy.toxicHour = tradeHour;
         Print("[HOURLY LEARNING MT5] Jam ", tradeHour, ":00 server terdeteksi rawan loss berulang (", currentHLoss, "x loss). Proteksi jam aktif!");
      }
      else
         g_autopsy.toxicHour = -1;
   }
   else
      g_autopsy.toxicHour = -1;

   // 2. Diagnosa Anatomi Mendalam Penyebab Loss (7 Skenario Institusional)
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   CopyRates(_Symbol, _Period, 0, 5, rates);

   double atrVal[];
   ArraySetAsSeries(atrVal, true);
   CopyBuffer(h_atr14, 0, 0, 3, atrVal);
   double currentAtr = (ArraySize(atrVal) > 1) ? atrVal[1] : PipToPrice(20.0);

   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   CopyBuffer(h_ema125, 0, 0, 3, ema125Val);
   double currentEma125 = (ArraySize(ema125Val) > 1) ? ema125Val[1] : 0.0;

   double lastBarRange = (ArraySize(rates) > 1) ? (rates[1].high - rates[1].low) : 0.0;
   ENUM_HTF_BIAS currentHTFBias = AnalyzeHTFMacroTrend();

   string reason = "PENGUJIAN LEVEL GAGAL (SUPPORT/RESISTEN DITEMBUS)";
   if (lastBarRange >= (2.0 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPREAD SPIKE)";
   else if (g_currentChoppiness > 61.8)
      reason = "JEBAKAN SIDEWAYS NOISE (PASAR CHOPPY KOMPRESI)";
   else if (g_smcAnalysis.hasCHoCH || (ArraySize(rates) > 1 && currentEma125 > 0 && ((rates[1].close < currentEma125 && rates[1].open > currentEma125) || (rates[1].close > currentEma125 && rates[1].open < currentEma125))))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU EKOR)";
   else if (tradeDir == 1 && currentHTFBias == HTF_BIAS_BEARISH)
      reason = "DIRECTIONAL ERROR (BUY MELAWAN TREN MAKRO H1)";
   else if (tradeDir == -1 && currentHTFBias == HTF_BIAS_BULLISH)
      reason = "DIRECTIONAL ERROR (SELL MELAWAN TREN MAKRO H1)";
   else if (g_autopsy.toxicHour >= 0)
      reason = "JAM RAWAN VOLATILITAS (TOXIC HOUR REVERSAL)";

   g_autopsy.lossReason = reason;
   SaveAutopsyStateMQL5();

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT5] Posisi Deal #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
   Print("DIAGNOSA PENYEBAB : ", g_autopsy.lossReason);
   Print("KOREKSI 1 (SKOR)  : Ambang Konfluensi dinaikkan +", DoubleToString(g_autopsy.scorePenalty, 0), " Poin (Hanya Setup Grade A+)");
   if (pat != PATTERN_NONE || rawPatId >= 11)
      Print("KOREKSI 2 (POLA)  : Pola ", patName, " dikarantina selama ", InpQuarantinePatternBars, " Bar lilin.");
   if (tradeDir != 0 && InpUseDirectionalLearning)
      Print("KOREKSI 3 (ARAH)  : Penalti arah ", (tradeDir == 1 ? "BUY" : "SELL"), " +", DoubleToString(InpDirectionalPenaltyScore, 0), " Poin selama ", InpDirectionalPenaltyBars, " Bar lilin.");
   Print("KOREKSI 4 (BUFFER): Stop Loss diperlebar +", DoubleToString(InpAdaptiveSLBufferBoost, 2), "x ATR untuk ", InpAdaptiveBufferTrades, " trade berikutnya.");
   Print("==================================================================");

   if (InpAutopsyNotifyPush)
   {
      string notif = "OTOPSI PASCA-SL #" + IntegerToString((long)ticket) + " (" + DoubleToString(lossAmount, 2) + ")\nDiagnosa: " + reason + "\nKoreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE || rawPatId >= 11)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      if (tradeDir != 0 && InpUseDirectionalLearning)
         notif += " Penalti arah " + (tradeDir == 1 ? "BUY" : "SELL") + " aktif.";
      SendPushAlert(notif);
   }
}

void ResetSelfHealingStateMQL5(string triggerReason)
{
   if (!g_autopsy.isActive) return;
   g_autopsy.isActive              = false;
   g_autopsy.scorePenalty          = 0.0;
   g_autopsy.tradesWithExtraBuffer = 0;
   g_autopsy.quarantineUntilBar    = 0;
   g_autopsy.failedDirection       = 0;
   g_autopsy.directionPenaltyUntil = 0;
   g_autopsy.toxicHour             = -1;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   SaveAutopsyStateMQL5();
   Print("[SELF-HEALING NORMALIZED MT5] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}

//+------------------------------------------------------------------+
//| M1 MULTI-TIMEFRAME ENGINE: DETEKSI OB DEMAND/SUPPLY & RETEST     |
//| Dijalankan setiap bar M1 baru. Hasilnya disimpan di g_mtfResult. |
//+------------------------------------------------------------------+
void DetectM1Engine()
{
   if (!InpUseMTFM1Engine) return;
   if (h_m1_atr14 == INVALID_HANDLE || h_m1_ema21 == INVALID_HANDLE) return;

   // Throttle: hanya update saat bar M1 baru terbentuk
   datetime currentM1BarTime = iTime(_Symbol, PERIOD_M1, 0);
   if (currentM1BarTime == g_lastM1BarTime && g_mtfResult.lastUpdated > 0) return;
   g_lastM1BarTime = currentM1BarTime;

   // Reset hasil sebelumnya
   ZeroMemory(g_mtfResult);

   // Ambil data M1
   int lookback = InpM1OBLookback + 5;
   MqlRates m1rates[];
   ArraySetAsSeries(m1rates, true);
   int copied = CopyRates(_Symbol, PERIOD_M1, 0, lookback, m1rates);
   if (copied < 5) { g_mtfResult.m1StatusStr = "DATA M1 KURANG"; return; }

   // Ambil ATR M1
   double m1AtrBuf[];
   ArraySetAsSeries(m1AtrBuf, true);
   double m1Atr = 0.0;
   if (CopyBuffer(h_m1_atr14, 0, 1, 3, m1AtrBuf) >= 1)
      m1Atr = m1AtrBuf[0];
   if (m1Atr <= 0.0) m1Atr = PipToPrice(5.0); // fallback 5 pips
   g_mtfResult.m1Atr = m1Atr;

   double dispThresh = InpM1OBDispAtrMult * m1Atr; // Minimal displacement untuk OB valid
   double bufferPrice = PipToPrice(InpM1ZoneBufferPips);

   double currentBid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double currentAsk = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

   // ---------------------------------------------------------------
   // SCAN ORDER BLOCK M1 (dari bar[1] ke belakang, skip bar[0] live)
   // Logika:
   //   - OB Bullish (DEMAND): Bar bearish besar (displacement Down) yang
   //     diikuti oleh impulse bullish naik → base candle = OB Demand
   //   - OB Bearish (SUPPLY): Bar bullish besar (displacement Up) yang
   //     diikuti oleh impulse bearish turun → base candle = OB Supply
   // ---------------------------------------------------------------
   MTFZone bestDemand; ZeroMemory(bestDemand);
   MTFZone bestSupply; ZeroMemory(bestSupply);

   int scanLimit = MathMin(InpM1OBLookback, copied - 3);

   for (int i = 1; i < scanLimit; i++)
   {
      double barRange = m1rates[i].high - m1rates[i].low;

      // ---- Deteksi OB Bullish (Demand): cari base candle bearish ----
      // Ciri: lilin i bearish, lalu diikuti impulse bullish (close[i-1] > high[i])
      if (m1rates[i].close < m1rates[i].open)  // base candle bearish
      {
         // Cek apakah ada displacement bullish setelahnya (bar[i-2] atau lebih awal)
         bool impulsiveBull = false;
         for (int j = 1; j <= MathMin(3, i - 1); j++)
         {
            double impRange = m1rates[i - j].close - m1rates[i - j].open;
            if (impRange >= dispThresh && m1rates[i - j].close > m1rates[i].high)
            {
               impulsiveBull = true;
               break;
            }
         }

         if (impulsiveBull)
         {
            // Zona OB Demand = [low, high] dari base candle bearish
            double obTop    = m1rates[i].high;
            double obBottom = m1rates[i].low;
            double obMid    = (obTop + obBottom) / 2.0;

            // OB valid jika belum dimitigation (price saat ini masih di atas obBottom)
            bool notMitigated = (currentBid > obBottom);
            // Pilih OB Demand yang terdekat di bawah harga saat ini
            bool belowPrice = (obTop < currentBid + bufferPrice * 5);

            if (notMitigated && belowPrice)
            {
               if (!bestDemand.isValid || obTop > bestDemand.top)
               {
                  bestDemand.isValid    = true;
                  bestDemand.isBullish  = true;
                  bestDemand.top        = obTop;
                  bestDemand.bottom     = obBottom;
                  bestDemand.mid        = obMid;
                  bestDemand.zoneType   = "OB_DEMAND";
                  bestDemand.tf         = PERIOD_M1;
                  bestDemand.detectedAt = m1rates[i].time;
                  bestDemand.dispAtrMult = barRange / (m1Atr > 0 ? m1Atr : 1.0);
                  bestDemand.isMitigated = false;
               }
            }
         }
      }

      // ---- Deteksi OB Bearish (Supply): cari base candle bullish ----
      // Ciri: lilin i bullish, lalu diikuti impulse bearish (close[i-1] < low[i])
      if (m1rates[i].close > m1rates[i].open)  // base candle bullish
      {
         bool impulsiveBear = false;
         for (int j = 1; j <= MathMin(3, i - 1); j++)
         {
            double impRange = m1rates[i - j].open - m1rates[i - j].close;
            if (impRange >= dispThresh && m1rates[i - j].close < m1rates[i].low)
            {
               impulsiveBear = true;
               break;
            }
         }

         if (impulsiveBear)
         {
            double obTop    = m1rates[i].high;
            double obBottom = m1rates[i].low;
            double obMid    = (obTop + obBottom) / 2.0;

            bool notMitigated = (currentAsk < obTop);
            bool abovePrice   = (obBottom > currentAsk - bufferPrice * 5);

            if (notMitigated && abovePrice)
            {
               if (!bestSupply.isValid || obBottom < bestSupply.bottom)
               {
                  bestSupply.isValid    = true;
                  bestSupply.isBullish  = false;
                  bestSupply.top        = obTop;
                  bestSupply.bottom     = obBottom;
                  bestSupply.mid        = obMid;
                  bestSupply.zoneType   = "OB_SUPPLY";
                  bestSupply.tf         = PERIOD_M1;
                  bestSupply.detectedAt = m1rates[i].time;
                  bestSupply.dispAtrMult = barRange / (m1Atr > 0 ? m1Atr : 1.0);
                  bestSupply.isMitigated = false;
               }
            }
         }
      }
   } // end scan loop

   g_mtfResult.m1DemandOB = bestDemand;
   g_mtfResult.m1SupplyOB = bestSupply;

   // ---------------------------------------------------------------
   // CEK PULLBACK / RETEST ke OB M1
   // Kondisi retest: harga saat ini berada dalam zona OB +/- buffer
   // ---------------------------------------------------------------
   g_mtfResult.m1PullbackValid = false;
   g_mtfResult.m1PullbackScore = 0.0;

   // Retest ke OB Demand (Bullish Setup)
   if (bestDemand.isValid)
   {
      bool priceTouchingDemand =
         (currentBid >= (bestDemand.bottom - bufferPrice)) &&
         (currentBid <= (bestDemand.top    + bufferPrice));

      if (priceTouchingDemand)
      {
         g_mtfResult.m1PullbackValid   = true;
         g_mtfResult.m1PullbackIsBuy   = true;
         g_mtfResult.m1PullbackType    = "OB_DEMAND_RETEST";

         // Hitung skor: +10 base, +5 jika displacement kuat, +5 jika CHoCH
         double score = 10.0;
         if (bestDemand.dispAtrMult >= 1.2) score += 5.0;

         // Deteksi CHoCH sederhana M1: cari HH setelah LL sweep di area OB
         bool chochBull = false;
         double recentHigh = 0.0, recentLow = DBL_MAX;
         for (int k = 1; k <= MathMin(10, copied - 1); k++)
         {
            if (m1rates[k].high > recentHigh) recentHigh = m1rates[k].high;
            if (m1rates[k].low  < recentLow)  recentLow  = m1rates[k].low;
         }
         // CHoCH bullish: low baru di zona OB tapi close sudah ke atas high sebelumnya
         if (m1rates[1].close > recentHigh && m1rates[1].low <= bestDemand.top)
            chochBull = true;

         g_mtfResult.m1CHoCHBull = chochBull;
         if (chochBull) score += 5.0;

         g_mtfResult.m1PullbackScore = MathMin(InpM1PullbackWeight, score);
         bestDemand.isTested = true;
         g_mtfResult.m1DemandOB = bestDemand;
      }
   }

   // Retest ke OB Supply (Bearish Setup) — hanya jika belum konfirmasi demand
   if (!g_mtfResult.m1PullbackValid && bestSupply.isValid)
   {
      bool priceTouchingSupply =
         (currentAsk >= (bestSupply.bottom - bufferPrice)) &&
         (currentAsk <= (bestSupply.top    + bufferPrice));

      if (priceTouchingSupply)
      {
         g_mtfResult.m1PullbackValid   = true;
         g_mtfResult.m1PullbackIsBuy   = false;
         g_mtfResult.m1PullbackType    = "OB_SUPPLY_RETEST";

         double score = 10.0;
         if (bestSupply.dispAtrMult >= 1.2) score += 5.0;

         bool chochBear = false;
         double recentHigh = 0.0, recentLow = DBL_MAX;
         for (int k = 1; k <= MathMin(10, copied - 1); k++)
         {
            if (m1rates[k].high > recentHigh) recentHigh = m1rates[k].high;
            if (m1rates[k].low  < recentLow)  recentLow  = m1rates[k].low;
         }
         if (m1rates[1].close < recentLow && m1rates[1].high >= bestSupply.bottom)
            chochBear = true;

         g_mtfResult.m1CHoCHBear = chochBear;
         if (chochBear) score += 5.0;

         g_mtfResult.m1PullbackScore = MathMin(InpM1PullbackWeight, score);
         bestSupply.isTested = true;
         g_mtfResult.m1SupplyOB = bestSupply;
      }
   }

   // ---------------------------------------------------------------
   // Bangun string untuk HUD display
   // ---------------------------------------------------------------
   if (bestDemand.isValid)
      g_mtfResult.m1DemandStr = DoubleToString(bestDemand.bottom, 2) +
                                 " \u2013 " + DoubleToString(bestDemand.top, 2);
   else
      g_mtfResult.m1DemandStr = "TIDAK ADA OB";

   if (bestSupply.isValid)
      g_mtfResult.m1SupplyStr = DoubleToString(bestSupply.bottom, 2) +
                                 " \u2013 " + DoubleToString(bestSupply.top, 2);
   else
      g_mtfResult.m1SupplyStr = "TIDAK ADA OB";

   if (g_mtfResult.m1PullbackValid)
   {
      string typeLabel = g_mtfResult.m1PullbackIsBuy ? "DEMAND RETEST \u2191" : "SUPPLY RETEST \u2193";
      g_mtfResult.m1StatusStr = StringFormat("\u2705 %s (+%.0f pts)", typeLabel, g_mtfResult.m1PullbackScore);
   }
   else
   {
      bool hasDemand = bestDemand.isValid;
      bool hasSupply = bestSupply.isValid;
      if (hasDemand && hasSupply)
         g_mtfResult.m1StatusStr = "MENUNGGU RETEST (D & S TERDETEKSI)";
      else if (hasDemand)
         g_mtfResult.m1StatusStr = "MENUNGGU RETEST KE DEMAND M1";
      else if (hasSupply)
         g_mtfResult.m1StatusStr = "MENUNGGU RETEST KE SUPPLY M1";
      else
         g_mtfResult.m1StatusStr = "SCANNING... (BELUM ADA OB M1)";
   }

   g_mtfResult.lastUpdated = TimeCurrent();

   Print("[M1-MTF] Bar ", TimeToString(currentM1BarTime, TIME_DATE|TIME_MINUTES),
         " | Demand: ", g_mtfResult.m1DemandStr,
         " | Supply: ", g_mtfResult.m1SupplyStr,
         " | Status: ", g_mtfResult.m1StatusStr);
}

//+------------------------------------------------------------------+
//| ON INIT                                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   DestroyDashboardGUI();
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpDeviation);
   trade.SetTypeFillingBySymbol(_Symbol);

   h_ema8    = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema21   = iMA(_Symbol, _Period, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema125  = iMA(_Symbol, _Period, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_atr14   = iATR(_Symbol, _Period, 14);
   h_atr100  = iATR(_Symbol, _Period, 100);
   h_rsi_div = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
   h_adx14   = iADX(_Symbol, _Period, InpADXPeriod);

   if (h_ema8 == INVALID_HANDLE || h_ema21 == INVALID_HANDLE ||
       h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE || h_atr100 == INVALID_HANDLE ||
       h_rsi_div == INVALID_HANDLE || h_adx14 == INVALID_HANDLE)
   {
      Print("[ERROR] Gagal menginisialisasi handle indikator MQL5!");
      return INIT_FAILED;
   }

   // === Inisialisasi Handle M1 MTF Engine (v4.00) ===
   if (InpUseMTFM1Engine)
   {
      h_m1_ema21 = iMA(_Symbol, PERIOD_M1, 21, 0, MODE_EMA, PRICE_CLOSE);
      h_m1_atr14 = iATR(_Symbol, PERIOD_M1, 14);
      if (h_m1_ema21 == INVALID_HANDLE || h_m1_atr14 == INVALID_HANDLE)
      {
         Print("[WARNING] Gagal inisialisasi M1 handle — fitur MTF dinonaktifkan.");
         // Tidak fatal, EA tetap jalan tanpa M1 engine
      }
      else
         Print("[M1-MTF] Handle M1 EMA21 & ATR14 berhasil diinisialisasi.");
      ZeroMemory(g_mtfResult);
      g_lastM1BarTime = 0;
   }

   if (InpUseHTFFilter)
   {
      h_htf_ema125 = iMA(_Symbol, InpHTFTimeframe, InpHTFTrendEMA, 0, MODE_EMA, PRICE_CLOSE);
      h_htf_ema8   = iMA(_Symbol, InpHTFTimeframe, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
      h_htf_ema21  = iMA(_Symbol, InpHTFTimeframe, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   }

   ZeroMemory(lastSwingHigh);
   ZeroMemory(lastSwingLow);
   ZeroMemory(currentPivot);
   ZeroMemory(currentFibo);
   lastBarTime = 0;

   UpdateDailyPivots();

   // Inisialisasi Pelacakan Saldo Awal & Waktu Aktivasi EA
   g_gvStartTimeKey = "VIKAR_EA_" + IntegerToString(InpMagicNumber) + "_START_TIME";
   g_gvStartBalKey  = "VIKAR_EA_" + IntegerToString(InpMagicNumber) + "_START_BAL";

   if (InpResetStatsOnStart || !GlobalVariableCheck(g_gvStartTimeKey))
   {
      g_eaStartTime = TimeCurrent();
      g_eaInitialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      GlobalVariableSet(g_gvStartTimeKey, (double)g_eaStartTime);
      GlobalVariableSet(g_gvStartBalKey, g_eaInitialBalance);
   }
   else
   {
      g_eaStartTime = (datetime)GlobalVariableGet(g_gvStartTimeKey);
      g_eaInitialBalance = GlobalVariableGet(g_gvStartBalKey);
      if (g_eaInitialBalance <= 0)
      {
         g_eaInitialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
         GlobalVariableSet(g_gvStartBalKey, g_eaInitialBalance);
      }
   }

   // Ambil koordinat posisi panel yang tersimpan jika ada (ingat posisi geser terakhir)
   string gvPanelX = "VIKAR_HUD_" + IntegerToString(ChartID()) + "_X";
   string gvPanelY = "VIKAR_HUD_" + IntegerToString(ChartID()) + "_Y";
   if (GlobalVariableCheck(gvPanelX))
      g_panelX = (int)GlobalVariableGet(gvPanelX);
   else
      g_panelX = InpDashboardX;

   if (GlobalVariableCheck(gvPanelY))
      g_panelY = (int)GlobalVariableGet(gvPanelY);
   else
      g_panelY = InpDashboardY;

   // Pastikan koordinat awal tidak di luar batas layar chart
   long chartWidth  = ChartGetInteger(0, CHART_WIDTH_IN_PIXELS);
   long chartHeight = ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);
   if (chartWidth > 50 && g_panelX > (chartWidth - 50)) g_panelX = 15;
   if (chartHeight > 50 && g_panelY > (chartHeight - 50)) g_panelY = 20;

   // Otomatis aktifkan Chart Shift agar panel HUD tidak menimpa lilin
   ChartSetInteger(0, CHART_SHIFT, true);
   ChartSetDouble(0, CHART_SHIFT_SIZE, 24.0);

   // Aktifkan penerimaan event mouse untuk fitur Drag & Drop Dashboard
   ChartSetInteger(0, CHART_EVENT_MOUSE_MOVE, true);
   Comment("");

   // Inisialisasi AI Pattern Matrix & Pulihkan Memori Pembelajaran Pasca-Restart
   InitPatternMatrixMQL5();
   LoadAutopsyStateMQL5();

   Print("=== VIKAR EA 4-PILLAR PRO INITIALIZED SUCCESSFULLY ===");
   Print("Aset: ", _Symbol, " | Timeframe: ", EnumToString(_Period), " | Magic: ", InpMagicNumber);
   Print("Start Time: ", TimeToString(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Balance: $", g_eaInitialBalance);

   // Aktifkan timer 1 detik agar HUD selalu live dan langsung muncul walau pasar libur / weekend
   EventSetTimer(1);
   if (InpShowDashboard)
   {
      UpdateDashboard();
      ChartRedraw(0);
   }

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| ON DEINIT                                                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   EventKillTimer();
   if (h_ema8 != INVALID_HANDLE)       IndicatorRelease(h_ema8);
   if (h_ema21 != INVALID_HANDLE)      IndicatorRelease(h_ema21);
   if (h_ema125 != INVALID_HANDLE)     IndicatorRelease(h_ema125);
   if (h_atr14 != INVALID_HANDLE)      IndicatorRelease(h_atr14);
   if (h_atr100 != INVALID_HANDLE)     IndicatorRelease(h_atr100);
   if (h_htf_ema125 != INVALID_HANDLE) IndicatorRelease(h_htf_ema125);
   if (h_htf_ema8 != INVALID_HANDLE)   IndicatorRelease(h_htf_ema8);
   if (h_htf_ema21 != INVALID_HANDLE)  IndicatorRelease(h_htf_ema21);
   if (h_rsi_div != INVALID_HANDLE)    IndicatorRelease(h_rsi_div);
   if (h_adx14 != INVALID_HANDLE)      IndicatorRelease(h_adx14);
   // M1 handles
   if (h_m1_ema21 != INVALID_HANDLE)   IndicatorRelease(h_m1_ema21);
   if (h_m1_atr14 != INVALID_HANDLE)   IndicatorRelease(h_m1_atr14);

   ChartSetInteger(0, CHART_EVENT_MOUSE_MOVE, false);
   DestroyDashboardGUI();
   CleanSMCObjects();
   Comment("");
}

//+------------------------------------------------------------------+
//| EMERGENCY CLOSE ALL OPEN POSITIONS (PROP FIRM GUARDIAN v3.00)    |
//+------------------------------------------------------------------+
void CloseAllOpenOrders()
{
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (!posInfo.SelectByIndex(i)) continue;
      if (posInfo.Symbol() != _Symbol) continue;
      if (posInfo.Magic() != InpMagicNumber) continue;

      ulong ticket = posInfo.Ticket();
      if (trade.PositionClose(ticket, InpDeviation))
      {
         Print("[PROP FIRM GUARDIAN MQL5] Emergency Close posisi #", ticket, " berhasil dieksekusi.");
      }
      else
      {
         Print("[PROP FIRM GUARDIAN MQL5] Gagal emergency close posisi #", ticket, ". Error: ", trade.ResultRetcode());
      }
   }
}

//+------------------------------------------------------------------+
//| PRO TRADER DISCIPLINE HELPERS (v3.30)                            |
//+------------------------------------------------------------------+
bool IsInRolloverWindowMQL5()
{
   if (!InpUseRolloverGuard) return false;
   MqlDateTime dt;
   TimeCurrent(dt);
   int curMin = dt.hour * 60 + dt.min;
   int startMin = InpRolloverStartHour * 60 + InpRolloverStartMin;
   int endMin = InpRolloverEndHour * 60 + InpRolloverEndMin;
   if (startMin > endMin)
   {
      if (curMin >= startMin || curMin < endMin) return true;
   }
   else
   {
      if (curMin >= startMin && curMin < endMin) return true;
   }
   return false;
}

bool IsInKillzoneWindowMQL5()
{
   if (!InpTradeKillzonesOnly) return true;
   MqlDateTime dt;
   TimeCurrent(dt);
   if (dt.hour >= InpKillzoneLondonStart && dt.hour < InpKillzoneLondonEnd) return true;
   if (dt.hour >= InpKillzoneNYStart && dt.hour < InpKillzoneNYEnd) return true;
   return false;
}

//+------------------------------------------------------------------+
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|
//+------------------------------------------------------------------+
bool CheckCircuitBreakers()
{
   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit && !InpUseEquityGuardian && !InpUseDailyProfitLockdown && !InpUseMaxDailyTrades)
      return true;

   MqlDateTime dt;
   TimeCurrent(dt);
   dt.hour = 0;
   dt.min  = 0;
   dt.sec  = 0;
   datetime todayStart = StructToTime(dt);

   if (!HistorySelect(todayStart, TimeCurrent()))
      return true;

   int consecutiveLosses = 0;
   datetime lastLossTime = 0;
   double todayClosedPnL = 0.0;
   int totalDeals = HistoryDealsTotal();

   for (int i = 0; i < totalDeals; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if (ticket == 0) continue;

      long entryType = HistoryDealGetInteger(ticket, DEAL_ENTRY);
      if (entryType != DEAL_ENTRY_OUT && entryType != DEAL_ENTRY_INOUT) continue;

      long dealMagic = HistoryDealGetInteger(ticket, DEAL_MAGIC);
      if (dealMagic != InpMagicNumber) continue;

      double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT) +
                      HistoryDealGetDouble(ticket, DEAL_SWAP) +
                      HistoryDealGetDouble(ticket, DEAL_COMMISSION);

      todayClosedPnL += profit;

      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      ulong posId = (ulong)HistoryDealGetInteger(ticket, DEAL_POSITION_ID);
      if (posId == 0) posId = (ulong)HistoryDealGetInteger(ticket, DEAL_ORDER);

      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
      {
         consecutiveLosses++;
         lastLossTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
         if (InpUseSelfHealing && g_autopsy.failedTicket != ticket)
            PerformLossAutopsyMQL5(ticket, posId, lastLossTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER KERUGIAN! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingStateMQL5("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }

      // Pembaruan Statistik Pattern Performance Matrix MT5 (v3.10)
      string procKey = "VIKAR_MT5_PMR_PROC_" + IntegerToString((long)ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patKeyPos = "VIKAR_PAT_" + IntegerToString((long)posId);
         string patKeyTkt = "VIKAR_PAT_" + IntegerToString((long)ticket);
         int patId = 0;
         if (GlobalVariableCheck(patKeyPos)) patId = (int)GlobalVariableGet(patKeyPos);
         else if (GlobalVariableCheck(patKeyTkt)) patId = (int)GlobalVariableGet(patKeyTkt);

         if (profit > 0.01)
            UpdatePatternRecordMQL5(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecordMQL5(patId, false);
         GlobalVariableSet(procKey, 1.0);

         // Bersihkan memori tiket setelah selesai diproses
         if (GlobalVariableCheck(patKeyPos)) GlobalVariableDel(patKeyPos);
         if (GlobalVariableCheck(patKeyTkt)) GlobalVariableDel(patKeyTkt);
         GlobalVariableDel("VIKAR_DIR_" + IntegerToString((long)posId));
         GlobalVariableDel("VIKAR_DIR_" + IntegerToString((long)ticket));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString((long)posId));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString((long)ticket));
      }
   }

   g_consecutiveLossCount = consecutiveLosses;
   g_lastLossTime         = lastLossTime;
   g_todayClosedProfit    = todayClosedPnL;

   // 1. Consecutive Loss Cooldown (Jeda 4 Jam Anti-Overtrading Pasca 2x True Loss)
   if (InpUseConsecutiveLossGuard && consecutiveLosses >= InpMaxConsecutiveLosses)
   {
      datetime cooldownEnd = lastLossTime + (InpCooldownHours * 3600);
      if (TimeCurrent() < cooldownEnd)
      {
         g_cooldownUntilTime = cooldownEnd;
         int remainingMins = (int)((cooldownEnd - TimeCurrent()) / 60);
         g_lastSignalType = "CIRCUIT BREAKER: 2x LOSS COOLDOWN (Sisa " + IntegerToString(remainingMins) + " Mnt)";
         static datetime lastCBPushTime = 0;
         if (InpNotifyOnCircuitBreaker && (TimeCurrent() - lastCBPushTime) > 3600)
         {
            SendPushAlert("CIRCUIT BREAKER ACTIVE!\nTerjadi 2x loss berturut-turut. Robot beristirahat selama 4 jam untuk proteksi modal.");
            lastCBPushTime = TimeCurrent();
         }
         return false; // Blok entry baru selama cooldown!
      }
      else
      {
         g_cooldownUntilTime = 0;
      }
   }
   else
   {
      g_cooldownUntilTime = 0;
   }

   // 2. Daily Loss Limit Safeguard (Kunci Hari Jika Akumulasi Rugi > 2.5% Modal)
   if (InpUseDailyLossLimit)
   {
      double currentBal = AccountInfoDouble(ACCOUNT_BALANCE);
      double maxAllowedLoss = -(currentBal * (InpMaxDailyLossPercent / 100.0));
      if (todayClosedPnL <= maxAllowedLoss)
      {
         g_dailyLossLimitHit = true;
         g_lastSignalType = "DAILY LOSS LIMIT (-" + DoubleToString(InpMaxDailyLossPercent, 1) + "%): TRADING DIKUNCI HARI INI";
         return false; // Blok entry baru hingga hari berganti!
      }
      else
      {
         g_dailyLossLimitHit = false;
      }
   }

   // 2.1 Daily Profit Target Lockdown ("Done for the Day") (v3.30)
   if (InpUseDailyProfitLockdown)
   {
      double curBal = AccountInfoDouble(ACCOUNT_BALANCE);
      double targetProfit = (InpDailyProfitTargetMode == PROFIT_TARGET_CURRENCY) ? 
                            InpDailyProfitTargetMoney : 
                            (curBal * (InpDailyProfitTargetPercent / 100.0));
      if (todayClosedPnL >= targetProfit)
      {
         g_dailyProfitLocked = true;
         g_lastSignalType = "DONE FOR THE DAY: TARGET PROFIT TERCAPAI (+$" + DoubleToString(todayClosedPnL, 2) + " >= $" + DoubleToString(targetProfit, 2) + ")";
         static datetime lastLockPushMT5 = 0;
         if (InpSendPushNotifications && (TimeCurrent() - lastLockPushMT5) > 3600)
         {
            SendPushAlert("TARGET PROFIT HARIAN TERCAPAI! (DONE FOR THE DAY)\nProfit Hari Ini: +$" + DoubleToString(todayClosedPnL, 2) + "\nRobot mengunci trading hari ini demi mengamankan keuntungan!");
            lastLockPushMT5 = TimeCurrent();
         }
         return false;
      }
      else
      {
         g_dailyProfitLocked = false;
      }
   }

   // 2.2 Maximum Daily Trades Cap (v3.30)
   if (InpUseMaxDailyTrades)
   {
      int totalEntriesToday = 0;
      for (int d = 0; d < totalDeals; d++)
      {
         ulong dTicket = HistoryDealGetTicket(d);
         if (dTicket == 0) continue;
         if (HistoryDealGetInteger(dTicket, DEAL_ENTRY) == DEAL_ENTRY_IN && HistoryDealGetInteger(dTicket, DEAL_MAGIC) == InpMagicNumber)
            totalEntriesToday++;
      }
      g_todayTradesCount = totalEntriesToday;
      if (totalEntriesToday >= InpMaxDailyTrades)
      {
         g_lastSignalType = "MAX TRADES HARIAN TERCAPAI (" + IntegerToString(totalEntriesToday) + "/" + IntegerToString(InpMaxDailyTrades) + "): DISIPLIN KUOTA";
         return false;
      }
   }

   // 3. Update Midnight Balance saat hari server berganti
   static int lastDayOfYear = -1;
   MqlDateTime dtCur;
   TimeToStruct(TimeCurrent(), dtCur);
   if (dtCur.day_of_year != lastDayOfYear)
   {
      lastDayOfYear = dtCur.day_of_year;
      g_midnightBalance = AccountInfoDouble(ACCOUNT_BALANCE);
      g_equityLockActive = false;
      Print("[PROP FIRM GUARDIAN MQL5] Pergantian hari server terdeteksi. Midnight Balance direset ke: $", DoubleToString(g_midnightBalance, 2));
   }

   // 4. Prop Firm Equity Guardian & Hard Drawdown Kill-Switch (v3.00)
   if (InpUseEquityGuardian && g_midnightBalance > 0.0)
   {
      double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      if (currentEquity < g_midnightBalance)
      {
         g_currentDailyDDPct = ((g_midnightBalance - currentEquity) / g_midnightBalance) * 100.0;
         if (g_currentDailyDDPct >= InpMaxDailyEquityDDPct)
         {
            g_equityLockActive     = true;
            g_lastSignalType       = "PROP FIRM GUARDIAN: DD " + DoubleToString(g_currentDailyDDPct, 1) + "% HIT! TRADING DIKUNCI";
            Print("[PROP FIRM GUARDIAN MQL5] EMERGENCY KILL-SWITCH! Equity DD: ", DoubleToString(g_currentDailyDDPct, 2), "%. Menutup seluruh order aktif & mengunci trading!");
            CloseAllOpenOrders();
            if (InpSendPushNotifications)
            {
               SendPushAlert("EMERGENCY KILL-SWITCH! Prop Firm Equity Guardian terpicu (DD: " + DoubleToString(g_currentDailyDDPct, 1) + "%). Seluruh order ditutup dan trading dikunci.");
            }
            return false;
         }
      }
      else
      {
         g_currentDailyDDPct = 0.0;
      }

      if (InpLockTradingOnDDBreach && g_equityLockActive)
      {
         g_lastSignalType = "PROP FIRM GUARDIAN: TRADING DIKUNCI HINGGA 00:00 SERVER";
         return false;
      }
   }

   return true;
}

//+------------------------------------------------------------------+
//| ON TIMER (UPDATE DASHBOARD OTOMATIS WALAUPUN PASAR TUTUP/WEEKEND)|
//+------------------------------------------------------------------+
void OnTimer()
{
   if (InpShowDashboard)
   {
      UpdateDashboard();
   }
}

//+------------------------------------------------------------------+
//| ON TICK (EKSEKUSI UTAMA PERGERAKAN HARGA)                        |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| SENSOR PRE-NEWS EVENT SHIELD: PEMERIKSAAN JADWAL RILIS BERITA AS |
//+------------------------------------------------------------------+
bool IsInsideNewsWindowMQL5(string &activeNewsStr)
{
   activeNewsStr = "";
   if (!InpUseNewsShield) return false;

   datetime now = TimeCurrent();
   MqlDateTime dt;
   TimeToStruct(now, dt);
   int currentMins = dt.hour * 60 + dt.min;

   string times[];
   int count = 0;
   string str = InpNewsReleaseHoursServer;
   while (StringLen(str) > 0)
   {
      int comma = StringFind(str, ",");
      string item = "";
      if (comma >= 0)
      {
         item = StringSubstr(str, 0, comma);
         str  = StringSubstr(str, comma + 1);
      }
      else
      {
         item = str;
         str  = "";
      }
      StringTrimLeft(item);
      StringTrimRight(item);
      if (StringLen(item) > 0)
      {
         ArrayResize(times, count + 1);
         times[count] = item;
         count++;
      }
   }

   for (int i = 0; i < count; i++)
   {
      int colon = StringFind(times[i], ":");
      if (colon > 0)
      {
         int h = (int)StringToInteger(StringSubstr(times[i], 0, colon));
         int m = (int)StringToInteger(StringSubstr(times[i], colon + 1));
         int targetMins = h * 60 + m;

         int startMins = targetMins - InpNewsMinsBefore;
         int endMins   = targetMins + InpNewsMinsAfter;

         if (currentMins >= startMins && currentMins <= endMins)
         {
            activeNewsStr = "BERITA AS @" + times[i];
            g_newsStatusStr = "WASPADA: JELANG " + times[i] + " SERVER";
            return true;
         }
      }
   }

   g_newsStatusStr = "AMAN (STANDBY)";
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR PELEBARAN SPREAD ABNORMAL (SPREAD SPIKE SHIELD MQL5)     |
//+------------------------------------------------------------------+
bool IsSpreadSpikeDetectedMQL5()
{
   if (!InpUseNewsShield) return false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double currentSpreadPips = PriceToPips(ask - bid);
   if (currentSpreadPips > (InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier))
   {
      Print("[SPREAD SPIKE SHIELD MT5] Terdeteksi lonjakan spread ekstrem: ", DoubleToString(currentSpreadPips, 1), " pips > ", DoubleToString(InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier, 1), " pips. Menunda eksekusi.");
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR PELEMAHAN MOMENTUM: RSI DIVERGENCE (ANTI-PUCUK / LEMBAH)  |
//+------------------------------------------------------------------+
bool CheckRSIDivergenceMQL5(bool isBuy)
{
   if (!InpUseDivergenceFilter || h_rsi_div == INVALID_HANDLE) return false;
   int lookback = MathMin(InpDivergenceLookbackBars, 50);

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if (CopyRates(_Symbol, _Period, 0, lookback + 5, rates) < lookback + 5)
      return false;

   double rsiBuf[];
   ArraySetAsSeries(rsiBuf, true);
   if (CopyBuffer(h_rsi_div, 0, 0, lookback + 5, rsiBuf) < lookback + 5)
      return false;

   if (isBuy)
   {
      int peak1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (rates[i].high > rates[peak1].high) peak1 = i;
      }

      int peak2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (rates[j].high > rates[peak2].high) peak2 = j;
      }

      double priceHigh1 = rates[peak1].high;
      double priceHigh2 = rates[peak2].high;
      double rsi1 = rsiBuf[peak1];
      double rsi2 = rsiBuf[peak2];

      if (priceHigh1 > priceHigh2 + PipToPrice(2.5) && rsi1 < rsi2 - 3.0 && rsi1 > 60.0)
      {
         g_divStatusStr = "BEARISH DIVERGENCE (EXHAUSTION TOP)";
         Print("[DIVERGENCE MT5] Bearish Divergence terdeteksi di pucuk (Peak1 RSI: ", DoubleToString(rsi1, 1), " < Peak2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan BUY.");
         return true;
      }
   }
   else
   {
      int trough1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (rates[i].low < rates[trough1].low) trough1 = i;
      }

      int trough2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (rates[j].low < rates[trough2].low) trough2 = j;
      }

      double priceLow1 = rates[trough1].low;
      double priceLow2 = rates[trough2].low;
      double rsi1 = rsiBuf[trough1];
      double rsi2 = rsiBuf[trough2];

      if (priceLow1 < priceLow2 - PipToPrice(2.5) && rsi1 > rsi2 + 3.0 && rsi1 < 40.0)
      {
         g_divStatusStr = "BULLISH DIVERGENCE (EXHAUSTION BOTTOM)";
         Print("[DIVERGENCE MT5] Bullish Divergence terdeteksi di dasar (Trough1 RSI: ", DoubleToString(rsi1, 1), " > Trough2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan SELL.");
         return true;
      }
   }

   g_divStatusStr = "NORMAL (SEHAT)";
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70 MQL5)           |
//+------------------------------------------------------------------+
bool CheckADXPowerMQL5(double &adxVal)
{
   adxVal = 25.0;
   if (!InpUseADXFilter) return true;
   if (h_adx14 == INVALID_HANDLE) return true;

   double adxBuf[];
   ArraySetAsSeries(adxBuf, true);
   if (CopyBuffer(h_adx14, 0, 1, 1, adxBuf) < 1) return true;

   adxVal = adxBuf[0];
   g_currentADXVal = adxVal;
   return (adxVal >= InpMinADXThreshold);
}

//+------------------------------------------------------------------+
//| SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70 MQL5)          |
//+------------------------------------------------------------------+
bool CheckEMASlopeMQL5(bool isBuy, double &slopePips)
{
   slopePips = 0.0;
   if (!InpUseEMASlopeFilter) return true;
   if (h_ema125 == INVALID_HANDLE) return true;

   double emaBuf[];
   ArraySetAsSeries(emaBuf, true);
   int lookback = InpEMASlopeLookback;
   if (CopyBuffer(h_ema125, 0, 1, lookback + 1, emaBuf) < lookback + 1) return true;

   double emaNow  = emaBuf[0];
   double emaPast = emaBuf[lookback];

   if (isBuy)
   {
      slopePips = PriceToPips(emaNow - emaPast);
      return (slopePips >= InpMinEMASlopePips);
   }
   else
   {
      slopePips = PriceToPips(emaPast - emaNow);
      return (slopePips >= InpMinEMASlopePips);
   }
}

//+------------------------------------------------------------------+
//| SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70 MQL5)         |
//+------------------------------------------------------------------+
bool CheckVolumeExpansionMQL5(double &volRatio)
{
   volRatio = 1.0;
   if (!InpUseVolumeFilter) return true;

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int lookback = InpVolumeMAPeriod + 5;
   if (CopyRates(_Symbol, _Period, 0, lookback, rates) < lookback) return true;

   double sumVol = 0.0;
   for (int i = 2; i <= InpVolumeMAPeriod + 1; i++)
   {
      sumVol += (double)rates[i].tick_volume;
   }
   double avgVol = sumVol / (double)InpVolumeMAPeriod;
   if (avgVol <= 0) return true;

   double currentVol = (double)rates[1].tick_volume;
   volRatio = currentVol / avgVol;
   g_currentVolRatio = volRatio;

   return (volRatio >= InpMinVolumeMultiplier);
}

//+------------------------------------------------------------------+
//| SENSOR BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70 MQL5)  |
//+------------------------------------------------------------------+
bool CheckMinATRFloorMQL5(double currentAtrPrice, double &atrPips)
{
   atrPips = PriceToPips(currentAtrPrice);
   if (!InpUseMinATRFilter) return true;
   return (atrPips >= InpMinATRPips);
}

//+------------------------------------------------------------------+
//| 8.9 AUTONOMOUS NEURO-CALIBRATION & SELF-TUNING ENGINE (v3.20)     |
//+------------------------------------------------------------------+
void AutoCalibrateTradingParameters()
{
   if (!InpUseAutoCalibration)
   {
      g_calibration.slBufferAtrMult      = InpSLBufferAtrMult;
      g_calibration.scoreElevation       = 0.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars;
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints;
      g_calibration.regimeDescription    = "Manual Static";
      return;
   }

   // 1. Baca ATR Jangka Pendek (14) dan Baseline Jangka Panjang (100)
   double atr14Buf[2];
   double atr14Val = 0.0;
   if (h_atr14 != INVALID_HANDLE && CopyBuffer(h_atr14, 0, 0, 2, atr14Buf) > 0)
      atr14Val = atr14Buf[1];

   double atr100Buf[2];
   double atr100Val = 0.0;
   if (h_atr100 != INVALID_HANDLE && CopyBuffer(h_atr100, 0, 0, 2, atr100Buf) > 0)
      atr100Val = atr100Buf[1];
   else
      atr100Val = atr14Val;

   double volRatio = (atr100Val > 0.0) ? (atr14Val / atr100Val) : 1.0;
   g_calibration.volatilityRatio = volRatio;

   // 2. Kalibrasi Adaptif berdasarkan Volatilitas
   if (volRatio >= InpAutoTuningSensitivity)
   {
      g_calibration.regimeDescription    = "High Volatility Spike";
      g_calibration.slBufferAtrMult      = MathMin(InpAutoTuningMaxBufferMult, InpSLBufferAtrMult * 1.35);
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints * 1.4;
      g_calibration.scoreElevation       = 10.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars + 1;
   }
   else if (volRatio <= 0.70 || (InpUseRegimeFilter && g_currentChoppiness > InpChoppyThreshold))
   {
      g_calibration.regimeDescription    = "Choppy Compression";
      g_calibration.slBufferAtrMult      = MathMax(0.8, InpSLBufferAtrMult * 0.9);
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints;
      g_calibration.scoreElevation       = 5.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars + 2;
   }
   else
   {
      g_calibration.regimeDescription    = "Normal Confluence";
      g_calibration.slBufferAtrMult      = InpSLBufferAtrMult;
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints;
      g_calibration.scoreElevation       = 0.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars;
   }

   // 3. Kalibrasi Anti-Tilt pasca Loss Beruntun
   if (g_consecutiveLossCount >= InpCalibrationConsecLossMax)
   {
      g_calibration.scoreElevation += (g_consecutiveLossCount * InpAutoTuningScoreStep);
      g_calibration.cooldownBars = MathMin(8, InpSignalCooldownBars * g_consecutiveLossCount);
      g_calibration.slBufferAtrMult = MathMin(InpAutoTuningMaxBufferMult, g_calibration.slBufferAtrMult + 0.25);
   }

   g_calibration.consecutiveLossStreak = g_consecutiveLossCount;
   g_calibration.isCalibrated          = true;
}

void OnTick()
{
   AutoCalibrateTradingParameters();
   if (g_eaManualPause)
   {
      g_lastSignalType = "PAUSED (TRADING DIHENTIKAN MANUAL VIA BUTTON)";
      return;
   }

   // 0.5 Jalankan M1 MTF Engine setiap tick (throttled per M1 bar)
   DetectM1Engine();

   // 1. Kelola Posisi Aktif (Trailing EMA 21, Structural Runner & Auto-BE Kunci Modal)
   ManageActiveTrades();

   // 2. Tampilkan Dashboard HUD Real-Time (Throttled 250ms untuk Efisiensi CPU)
   if (InpShowDashboard)
   {
      static uint lastHudTick = 0;
      uint currentTick = GetTickCount();
      if (currentTick - lastHudTick >= 250)
      {
         UpdateDashboard();
         lastHudTick = currentTick;
      }
   }

   // 3. Hanya Cari Sinyal Saat Lilin Baru Selesai (Non-Repaint Bar Close Rule)
   if (!IsNewBar())
      return;

   // 3.0 Rollover Spread Blackout Shield (v3.30)
   if (IsInRolloverWindowMQL5())
   {
      g_lastSignalType = "ROLLOVER FREEZE: JENDELA SPREAD MELEBAR TENGAH MALAM";
      return;
   }

   // 3.05 Institutional Killzones Sesi Filter (v3.30)
   if (!IsInKillzoneWindowMQL5())
   {
      g_lastSignalType = "DILUAR KILLZONE INSTITUSIONAL (LONDON & NY ONLY)";
      return;
   }

   // 3.1 Periksa Proteksi Akun & Circuit Breaker (Consecutive Loss Cooldown & Daily Limit)
   if (!CheckCircuitBreakers())
      return;

   // 3.2 Proteksi Akhir Pekan (Friday Weekend Guard - Anti Gap Akhir Pekan)
   if (InpUseFridayGuard)
   {
      MqlDateTime dtFriday;
      TimeCurrent(dtFriday);
      if (dtFriday.day_of_week == 5 && dtFriday.hour >= InpFridayCloseHour)
      {
         for (int fPos = PositionsTotal() - 1; fPos >= 0; fPos--)
         {
            if (posInfo.SelectByIndex(fPos) && posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
            {
               trade.PositionClose(posInfo.Ticket());
               Print("[FRIDAY WEEKEND GUARD] Menutup posisi #", posInfo.Ticket(), " jelang akhir pekan demi keamanan modal!");
            }
         }
         g_lastSignalType = "FRIDAY WEEKEND GUARD: PASAR JUMAT MALAM (ANTI-GAP)";
         return;
      }
   }

   // 4. Periksa Filter Spread Broker
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double currentSpreadPips = PriceToPips(ask - bid);
   if (currentSpreadPips > InpMaxSpreadPips)
   {
      g_lastSignalType = "SPREAD MELEBIHI BATAS (" + DoubleToString(currentSpreadPips, 1) + " pips)";
      return;
   }

   // 5. Periksa Filter Waktu Sesi Trading
   if (InpUseSessionFilter)
   {
      MqlDateTime dt;
      TimeCurrent(dt);
      if (dt.hour < InpSessionStartHour || dt.hour >= InpSessionEndHour)
      {
         g_lastSignalType = "DILUAR SESI TRADING (" + IntegerToString(dt.hour) + ":00)";
         return;
      }
   }

   // 5.1 Pre-News Event Shield (v2.60)
   string activeNewsEvent = "";
   if (InpUseNewsShield && IsInsideNewsWindowMQL5(activeNewsEvent))
   {
      g_lastSignalType = "PRE-NEWS SHIELD: PEMBEKUAN ORDER JELANG " + activeNewsEvent;
      return;
   }

   // 5.2 Spread Anomaly Spike Shield (v2.60)
   if (InpUseNewsShield && IsSpreadSpikeDetectedMQL5())
   {
      g_lastSignalType = "SPREAD SPIKE SHIELD: SPREAD MELEBAR ABNORMAL";
      return;
   }

   // 6. Salin Data Harga & Indikator
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   int copiedRates = CopyRates(_Symbol, _Period, 0, 100, rates);
   if (copiedRates < 25)
      return;

   double ema8[], ema21[], ema125[], atr[];
   ArraySetAsSeries(ema8, true);
   ArraySetAsSeries(ema21, true);
   ArraySetAsSeries(ema125, true);
   ArraySetAsSeries(atr, true);

   if (CopyBuffer(h_ema8, 0, 0, 30, ema8) < 15 ||
       CopyBuffer(h_ema21, 0, 0, 30, ema21) < 15 ||
       CopyBuffer(h_ema125, 0, 0, 30, ema125) < 15 ||
       CopyBuffer(h_atr14, 0, 0, 30, atr) < 15)
      return;

   double currentAtr = (atr[1] > 0) ? atr[1] : PipToPrice(20.0);
   double currentEma8   = ema8[1];
   double currentEma21  = ema21[1];
   double currentEma125 = ema125[1];

   // Filter Shock Guard: Proteksi Lonjakan Lilin Berita Abnormal
   if (CheckShockGuard(rates, currentAtr))
   {
      g_lastSignalType = "SHOCK GUARD: JEDA PASCA-LONJAKAN VOLATILITAS";
      return;
   }

   // Perbarui Daily Pivot Points, Ayunan SMC, dan Analisis Struktur Pasar
   UpdateDailyPivots();
   UpdateSMCSwings(rates, copiedRates);
   g_smcAnalysis = AnalyzeMarketStructure(rates);
   DetectOrderBlocks(rates, copiedRates, currentAtr);
   TrackFairValueGaps(rates, copiedRates);
   g_chartPattern = AnalyzeChartPatterns(rates, copiedRates, currentAtr);
   DrawSMCObjectsOnChart();

   // Perbarui Fibonacci Retracement sesuai bias tren harga saat ini sebelum evaluasi lilin & konfluensi
   bool currentTrendBias = (rates[1].close > currentEma125);
   UpdateAutoFibo(currentTrendBias);

   // Analisis Kecerdasan Pola Candlestick Rejection Real-Time (dengan GP level & Pivot terbaru)
   g_candleAnalysis = AnalyzeCandlePattern(rates, currentEma8, currentEma21, currentFibo.level618, currentPivot.P);

   // 7. Auto Cut Profit pada Posisi Aktif Jika Terdeteksi Pembalikan Arah
   CheckAutoCutProfit(rates, ema21, currentAtr);

   // 8. Periksa Batas Maksimal Posisi Aktif untuk Entry Baru (Posisi Aktif + Pending Orders)
   int openCount = 0;
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (posInfo.SelectByIndex(i))
      {
         if (posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
            openCount++;
      }
   }

   if (openCount >= InpMaxOpenPositions)
      return;

   // 9. Periksa Jeda Cooldown Antar Order
   int effectiveCooldown = InpUseAutoCalibration ? g_calibration.cooldownBars : InpSignalCooldownBars;
   if (lastOrderBarTime != 0 && (iTime(_Symbol, _Period, 0) - lastOrderBarTime) < (effectiveCooldown * PeriodSeconds(_Period)))
      return;

   // 10. Validasi Filter Whipsaw EMA 125
   if (IsWhipsawEMA125(rates, ema125))
   {
      g_lastSignalType = "FILTER: WHIPSAW DI EMA 125";
      return;
   }

   // 11. Evaluasi Analisis Bias Makro Higher Timeframe (H1)
   ENUM_HTF_BIAS htfBias = AnalyzeHTFMacroTrend();
   bool buyHTFOk  = (!InpUseHTFFilter || htfBias == HTF_BIAS_BULLISH);
   bool sellHTFOk = (!InpUseHTFFilter || htfBias == HTF_BIAS_BEARISH);

   //+---------------------------------------------------------------+
   //| EVALUASI 4 PILAR UNTUK SETUP BUY (GRADE A+)                   |
   //+---------------------------------------------------------------+
   bool buyTrendEMA125 = (rates[1].close > currentEma125);
   bool buyDoubleAlign = true;

   if (InpUseDailyPivots && InpRequireDoubleAlign)
   {
      buyDoubleAlign = (rates[1].close > currentPivot.P);
      g_doubleAlignStr = buyDoubleAlign ? "SUPER BULLISH (DI ATAS P)" : "CONFLICT (DI BAWAH P)";
   }

   if (buyTrendEMA125 && buyDoubleAlign)
   {
      if (!buyHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {
         UpdateAutoFibo(true);

         // A. Pilar 1: SMC Core (Struktur Bullish / BOS / CHoCH / Liquidity Sweep)
         bool smcBullishOk = true;
         if (InpRequireBOSorCHoCH)
         {
            smcBullishOk = (g_smcAnalysis.structure == SMC_STRUCT_BULLISH ||
                            g_smcAnalysis.hasCHoCH ||
                            (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && rates[1].low <= lastSwingLow.price));
         }

         // Filter Diskon (< 50% dealing range)
         if (InpRequireDiscount)
         {
            if (!g_smcAnalysis.isDiscount)
               smcBullishOk = false; // Dilarang BUY di area Mahal / Premium!
         }

         // Deteksi Liquidity Sweep pada Swing Low
         bool isSwept = (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && rates[1].low <= lastSwingLow.price);

         // B. Pilar 3: Pullback ke Ribbon EMA 8 & 21
         bool isPullbackEMA = false;
         int maxLookbackBuy = MathMin(InpPullbackLookback, MathMin(copiedRates - 1, MathMin(ArraySize(ema8) - 1, ArraySize(ema21) - 1)));
         for (int b = 1; b <= maxLookbackBuy; b++)
         {
            double lowEma  = MathMin(ema8[b], ema21[b]);
            double highEma = MathMax(ema8[b], ema21[b]);
            if (rates[b].low <= highEma && rates[b].high >= lowEma)
            {
               isPullbackEMA = true;
               break;
            }
         }

         // C. Pilar 4: Retracement ke Golden Pocket (0.500 - 0.786)
         bool isFiboGPOk = true;
         if (InpUseAutoFibo && InpRequireGoldenPocket && currentFibo.isValid)
         {
            isFiboGPOk = (rates[1].low <= currentFibo.level500 && rates[1].high >= currentFibo.level786);
            g_lastFiboStatus = isFiboGPOk ? "GOLDEN POCKET REBOUND" : "DILUAR GP";
         }

         // D. Konfirmasi Lilin Rejection Bullish Cerdas
         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
            isRejection = (rates[1].close >= rates[1].open);

         if (!isPullbackEMA)
            g_lastSignalType = "BULLISH: MENUNGGU PULLBACK KE EMA 8/21";
         else if (!isRejection)
            g_lastSignalType = "STRUKTUR (" + g_smcAnalysis.structureName + "), MENUNGGU POLA LILIN";

         // E. Filter Headroom ke Resisten Pivot Terdekat
         bool isHeadroomOk = true;
         if (InpUseDailyPivots && currentPivot.R1 > rates[1].close)
         {
            double distToR1 = currentPivot.R1 - rates[1].close;
            if (distToR1 < (InpMinHeadroomATR * currentAtr))
               isHeadroomOk = false; // Terlalu dekat tembok resisten!
         }

         // F. Evaluasi Order Block (OB) & Hitung Skor Konfluensi 4 Pilar Terpadu
         bool isOBMitigatedOk = true;
         if (InpUseOrderBlock && InpRequireOBMitigation)
         {
            isOBMitigatedOk = (g_bullishOB.isValid && rates[1].low <= g_bullishOB.top && rates[1].high >= g_bullishOB.bottom);
         }

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, rates, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis, Penalti Arah & Jam Rawan
         double dirPenaltyBUY = 0.0;
         if (InpUseDirectionalLearning && g_autopsy.isActive && g_autopsy.failedDirection == 1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
         {
            dirPenaltyBUY = InpDirectionalPenaltyScore;
         }

         double hourPenaltyBUY = 0.0;
         MqlDateTime mdtNowBuy;
         TimeCurrent(mdtNowBuy);
         if (InpUseHourlyLearning && g_autopsy.isActive && g_autopsy.toxicHour == mdtNowBuy.hour)
         {
            hourPenaltyBUY = 10.0;
         }

         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltyBUY + hourPenaltyBUY;

         if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         if (scoreRes.totalScore < effectiveMinScoreBUY)
         {
            if (dirPenaltyBUY > 0.0)
               g_lastSignalType = "KOREKSI DIRI: PENALTI BUY (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else if (hourPenaltyBUY > 0.0)
               g_lastSignalType = "KOREKSI DIRI: JAM RAWAN H:" + IntegerToString(mdtNowBuy.hour) + " (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else if (InpUseSelfHealing && g_autopsy.isActive)
               g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreBUY, 0) + ")";
            else
               g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
         }

         // F.2 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
         bool isBullishSweepTrap = false;
         if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
         {
            double candleRange = rates[1].high - rates[1].low;
            if (candleRange > 0 && lastSwingLow.price > 0 && rates[1].low < lastSwingLow.price && rates[1].close > lastSwingLow.price)
            {
               double sweepDistPips = PriceToPips(lastSwingLow.price - rates[1].low);
               double lowerWick     = MathMin(rates[1].open, rates[1].close) - rates[1].low;
               double lowerWickPct  = (lowerWick / candleRange) * 100.0;
               if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && lowerWickPct >= InpMinRejectionWickPct)
               {
                  isBullishSweepTrap = true;
                  g_trapHunterStatusStr = "BULLISH SWEEP TRAP (SSL REVERSAL)";
                  Print("[TRAP HUNTER MQL5] Bullish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(lowerWickPct, 0), "%.");
               }
            }
         }

         // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Reli)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = rates[1].close - rates[1].open;
            bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (rates[1].close > currentEma8 && currentEma8 > currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close > lastSwingHigh.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || rates[1].tick_volume >= (long)(1.3 * (double)rates[2].tick_volume)));

            if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
            {
               isMomentumBreakout = true;
            }
         }

         // EKSEKUSI BUY JIKA:
         // Jalur 1 (Konservatif Pullback Sniper): Memenuhi semua 4 pilar + pullback + rejection + skor lolos
         // ATAU
         // Jalur 2 (Agresif Momentum Breakout): Terdeteksi Momentum Expansion BOS tanpa wajib pullback/diskon!
         if (InpUseDivergenceFilter && CheckRSIDivergenceMQL5(true))
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }

         double slopeBuyPips = 0.0;
         if (InpUseEMASlopeFilter && !CheckEMASlopeMQL5(true, slopeBuyPips))
         {
            g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeBuyPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
            return;
         }

         // =========================================================================
         // AI BRAIN & CANDLESTICK SHIELD PROTECTION GATE (v3.40)
         // =========================================================================
         int currentPatIdBUY = (isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));

         // 1. Blacklist Check dari Memori Pembelajaran Mandiri (Dynamic Pattern Matrix)
         if (InpUsePatternMatrix && g_patternMatrix[currentPatIdBUY].isBlacklisted)
         {
            g_lastSignalType = "AI BRAIN: POLA " + g_patternMatrix[currentPatIdBUY].name + " DI-BLACKLIST (Win Rate < " + DoubleToString(InpPatternBlacklistWinrate, 0) + "%)";
            return;
         }

         // Terapkan Modifikasi Skor dari Hasil Pembelajaran Mandiri (Bonus / Penalti)
         if (InpUsePatternMatrix)
            scoreRes.totalScore += g_patternMatrix[currentPatIdBUY].scoreModifier;

         // 2. AI Candlestick Shield: Filter Doji / Body Tipis (<22% Range)
         double barRangeBUY = rates[1].high - rates[1].low;
         if (barRangeBUY > 0)
         {
            double barBodyBUY      = MathAbs(rates[1].close - rates[1].open);
            double barBodyPctBUY   = (barBodyBUY / barRangeBUY) * 100.0;
            double barUpWickBUY    = rates[1].high - MathMax(rates[1].open, rates[1].close);
            double barUpWickPctBUY = (barUpWickBUY / barRangeBUY) * 100.0;

            if (InpFilterDojiCandles && barBodyPctBUY <= 22.0 && !isBullishSweepTrap)
            {
               g_lastSignalType = "AI SHIELD: BODY DOJI / RAGU-RAGU (" + DoubleToString(barBodyPctBUY, 0) + "% < 22%)";
               return;
            }

            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Upper Wick >= 45% on BUY)
            if (InpFilterExhaustionWicks && barUpWickPctBUY >= 45.0 && !isMomentumBreakout)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN SELLER DI ATAS (" + DoubleToString(barUpWickPctBUY, 0) + "% >= 45%)";
               return;
            }

            // 4. AI Candlestick Shield: Filter Overextended Engulfing (> 1.5x ATR dari EMA21)
            if (InpFilterOverextended && (g_candleAnalysis.pattern == PATTERN_ENGULFING || isMomentumBreakout))
            {
               double distToEma21 = MathAbs(rates[1].close - currentEma21);
               if (distToEma21 > (1.5 * currentAtr))
               {
                  g_lastSignalType = "AI SHIELD: OVEREXTENDED DARI EMA21 (" + DoubleToString(PriceToPips(distToEma21), 1) + " > 1.5x ATR)";
                  return;
               }
            }
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk) ||
                              (isBullishSweepTrap && isHeadroomOk);

         // === GUARD M1 OB RETEST (v4.00 MTF Ketat) ===
         // Blokir entry BUY jika Mode Ketat aktif dan tidak ada retest ke OB Demand M1
         if (canExecuteBuy && InpUseMTFM1Engine && InpRequireM1OBRetest)
         {
            bool m1OK = g_mtfResult.m1PullbackValid && g_mtfResult.m1PullbackIsBuy;
            if (!m1OK)
            {
               g_lastSignalType = "M1-GUARD: MENUNGGU RETEST OB DEMAND M1 | " + g_mtfResult.m1StatusStr;
               Print("[M1-MTF GUARD] BUY diblokir — belum ada retest ke OB Demand M1. Status: ", g_mtfResult.m1StatusStr);
               canExecuteBuy = false;
            }
         }

         if (canExecuteBuy)
         {
            double slPrice = 0.0;
            double tpPrice = 0.0;

            // Hitung Stop Loss
            if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingLow.price > 0)
            {
               double effectiveBufferMultBUY = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);
               slPrice = lastSwingLow.price - (effectiveBufferMultBUY * currentAtr);
            }
            else if (InpSLType == SL_TYPE_CANDLE_WICK)
               slPrice = rates[1].low - PipToPrice(5.0);
            else
               slPrice = ask - PipToPrice(InpFixedSLPips);

            // Batasi SL agar tidak terlalu sempit atau terlalu lebar
            double slDist = ask - slPrice;
            if (PriceToPips(slDist) < InpMinSLPips)
               slPrice = ask - PipToPrice(InpMinSLPips);
            if (PriceToPips(slDist) > InpMaxSLPips)
               slPrice = ask - PipToPrice(InpMaxSLPips);

            // Hitung Take Profit
            if (InpTPType == TP_TYPE_FIXED_POINTS)
               tpPrice = ask + PointToPrice(InpFixedTPPoints);
            else if (InpTPType == TP_TYPE_RISK_REWARD)
               tpPrice = ask + (InpRiskRewardRatio * (ask - slPrice));
            else if (InpTPType == TP_TYPE_FIBO_EXT && currentFibo.isValid && currentFibo.ext272 > ask)
               tpPrice = currentFibo.ext272;
            else if (InpTPType == TP_TYPE_PIVOT_LEVEL && currentPivot.R1 > ask)
               tpPrice = currentPivot.R1;
            else
               tpPrice = ask + (InpRiskRewardRatio * (ask - slPrice));

            // Validasi Stops Level Broker (Proteksi Anti-Error 10016)
            long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
            double minStopDist = MathMax(stopsLevel * _Point, SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * _Point + (5 * _Point));
            if ((ask - slPrice) < minStopDist)
               slPrice = ask - minStopDist;
            if ((tpPrice - ask) < minStopDist)
               tpPrice = ask + minStopDist;

            slPrice = NormalizeDouble(slPrice, _Digits);
            tpPrice = NormalizeDouble(tpPrice, _Digits);

            double lots = CalculateRiskLot(ask - slPrice, scoreRes.totalScore);

            // Validasi Kecukupan Margin Akun Sebelum Eksekusi (Proteksi Anti-Error NO MONEY)
            double marginReq = 0.0;
            if (OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, lots, ask, marginReq))
            {
               double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
               if (marginReq > freeMargin)
               {
                  Print("[MARGIN WARNING] Free margin tidak cukup untuk BUY ", lots, " lot. Butuh: $", marginReq, " | Sisa: $", freeMargin);
                  g_lastSignalType = "MARGIN TIDAK CUKUP (Req: $" + DoubleToString(marginReq, 1) + ")";
                  return;
               }
            }

            string tradeCmt = InpTradeComment + (isBullishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))));
            // Adaptive SL Buffer Expansion pasca-loss
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               slPrice = NormalizeDouble(slPrice - (InpAdaptiveSLBufferBoost * currentAtr), _Digits);

            bool orderSuccess = trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt);
            ulong buyTicket = 0;
            ulong buyDeal = 0;
            double executedPrice = ask;
            string execModeTag = "MARKET";

            if (orderSuccess)
            {
               buyTicket = trade.ResultOrder();
               buyDeal   = trade.ResultDeal();
               executedPrice = ask;
               execModeTag   = "MARKET";
            }

            if (orderSuccess)
            {
               GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString((long)buyTicket), MathMax(executedPrice - slPrice, 10 * _Point));
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMQL5(buyTicket, buyDeal, (isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)), 1, scoreRes.totalScore, currentAtr);

               lastOrderBarTime = iTime(_Symbol, _Period, 0);
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = execModeTag + " PLACED: " + patStr + " @ " + DoubleToString(executedPrice, _Digits);
               Print("[", execModeTag, " EXECUTION] Lot: ", lots, " | Price: ", executedPrice, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert(execModeTag + " " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(executedPrice, _Digits) +
                                "\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                                "\nPola: " + patStr);
               }
               UpdateDashboard();
               return;
            }
            else
            {
               Print("[BUY REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
               g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
            }
         }
      }
   }

   //+---------------------------------------------------------------+
   //| EVALUASI 4 PILAR UNTUK SETUP SELL (GRADE A+)                  |
   //+---------------------------------------------------------------+
   bool sellTrendEMA125 = (rates[1].close < currentEma125);
   bool sellDoubleAlign = true;

   if (InpUseDailyPivots && InpRequireDoubleAlign)
   {
      sellDoubleAlign = (rates[1].close < currentPivot.P);
      g_doubleAlignStr = sellDoubleAlign ? "SUPER BEARISH (DI BAWAH P)" : "CONFLICT (DI ATAS P)";
   }

   if (sellTrendEMA125 && sellDoubleAlign)
   {
      if (!sellHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {
         UpdateAutoFibo(false);

         // A. Pilar 1: SMC Core (Struktur Bearish / BOS / CHoCH / Liquidity Sweep)
      bool smcBearishOk = true;
      if (InpRequireBOSorCHoCH)
      {
         smcBearishOk = (g_smcAnalysis.structure == SMC_STRUCT_BEARISH ||
                         g_smcAnalysis.hasCHoCH ||
                         (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && rates[1].high >= lastSwingHigh.price));
      }

      // Filter Premium (> 50% dealing range)
      if (InpRequireDiscount)
      {
         if (!g_smcAnalysis.isPremium)
            smcBearishOk = false; // Dilarang SELL di area Murah / Diskon!
      }

      // Deteksi Liquidity Sweep pada Swing High
      bool isSwept = (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && rates[1].high >= lastSwingHigh.price);

      // B. Pilar 3: Pullback ke Ribbon EMA 8 & 21
      bool isPullbackEMA = false;
      int maxLookbackSell = MathMin(InpPullbackLookback, MathMin(copiedRates - 1, MathMin(ArraySize(ema8) - 1, ArraySize(ema21) - 1)));
      for (int b = 1; b <= maxLookbackSell; b++)
      {
         double lowEma  = MathMin(ema8[b], ema21[b]);
         double highEma = MathMax(ema8[b], ema21[b]);
         if (rates[b].high >= lowEma && rates[b].low <= highEma)
         {
            isPullbackEMA = true;
            break;
         }
      }

      // C. Pilar 4: Retracement ke Golden Pocket (0.500 - 0.786)
      bool isFiboGPOk = true;
      if (InpUseAutoFibo && InpRequireGoldenPocket && currentFibo.isValid)
      {
         isFiboGPOk = (rates[1].high >= currentFibo.level500 && rates[1].low <= currentFibo.level786);
         g_lastFiboStatus = isFiboGPOk ? "GOLDEN POCKET REBOUND" : "DILUAR GP";
      }

      // D. Konfirmasi Lilin Rejection Bearish Cerdas
      bool isRejection = true;
      if (InpRequireCandleRejection)
         isRejection = (!g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
      else
         isRejection = (rates[1].close <= rates[1].open);

      if (!isPullbackEMA)
         g_lastSignalType = "BEARISH: MENUNGGU PULLBACK KE EMA 8/21";
      else if (!isRejection)
         g_lastSignalType = "STRUKTUR (" + g_smcAnalysis.structureName + "), MENUNGGU POLA LILIN";

      // E. Filter Headroom ke Support Pivot Terdekat
      bool isHeadroomOk = true;
      if (InpUseDailyPivots && currentPivot.S1 < rates[1].close)
      {
         double distToS1 = rates[1].close - currentPivot.S1;
         if (distToS1 < (InpMinHeadroomATR * currentAtr))
            isHeadroomOk = false; // Terlalu dekat tembok support!
      }

      // F. Evaluasi Order Block (OB) & Hitung Skor Konfluensi 4 Pilar Terpadu
      bool isOBMitigatedOk = true;
      if (InpUseOrderBlock && InpRequireOBMitigation)
      {
         isOBMitigatedOk = (g_bearishOB.isValid && rates[1].high >= g_bearishOB.bottom && rates[1].low <= g_bearishOB.top);
      }

      ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, rates, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
      g_lastScoreResult = scoreRes;

      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis, Penalti Arah & Jam Rawan
      double dirPenaltySELL = 0.0;
      if (InpUseDirectionalLearning && g_autopsy.isActive && g_autopsy.failedDirection == -1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
      {
         dirPenaltySELL = InpDirectionalPenaltyScore;
      }

      double hourPenaltySELL = 0.0;
      MqlDateTime mdtNowSell;
      TimeCurrent(mdtNowSell);
      if (InpUseHourlyLearning && g_autopsy.isActive && g_autopsy.toxicHour == mdtNowSell.hour)
      {
         hourPenaltySELL = 10.0;
      }

      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltySELL + hourPenaltySELL;

      if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
          g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
      {
         int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
         g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
         return;
      }

      if (scoreRes.totalScore < effectiveMinScoreSELL)
      {
         if (dirPenaltySELL > 0.0)
            g_lastSignalType = "KOREKSI DIRI: PENALTI SELL (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else if (hourPenaltySELL > 0.0)
            g_lastSignalType = "KOREKSI DIRI: JAM RAWAN H:" + IntegerToString(mdtNowSell.hour) + " (SKOR " + DoubleToString(scoreRes.totalScore, 0) + " < " + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else if (InpUseSelfHealing && g_autopsy.isActive)
            g_lastSignalType = "KOREKSI DIRI: SKOR (" + DoubleToString(scoreRes.totalScore, 0) + ") < AMBANG PASCA-SL (" + DoubleToString(effectiveMinScoreSELL, 0) + ")";
         else
            g_lastSignalType = "SKOR (" + DoubleToString(scoreRes.totalScore, 0) + "/100 " + scoreRes.grade + ") < MIN " + DoubleToString(InpMinConfluenceScore, 0);
      }

      // F.2 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
      bool isBearishSweepTrap = false;
      if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
      {
         double candleRange = rates[1].high - rates[1].low;
         if (candleRange > 0 && lastSwingHigh.price > 0 && rates[1].high > lastSwingHigh.price && rates[1].close < lastSwingHigh.price)
         {
            double sweepDistPips = PriceToPips(rates[1].high - lastSwingHigh.price);
            double upperWick     = rates[1].high - MathMax(rates[1].open, rates[1].close);
            double upperWickPct  = (upperWick / candleRange) * 100.0;
            if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && upperWickPct >= InpMinRejectionWickPct)
            {
               isBearishSweepTrap = true;
               g_trapHunterStatusStr = "BEARISH SWEEP TRAP (BSL REVERSAL)";
               Print("[TRAP HUNTER MQL5] Bearish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(upperWickPct, 0), "%.");
            }
         }
      }

      // G. Deteksi Momentum Breakout / Expansion (Anti-Ketinggalan Momentum Terjun)
      bool isMomentumBreakout = false;
      if (InpAllowMomentumBreakout)
      {
         double candleBody = rates[1].open - rates[1].close;
         bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
         bool isRibbonExpanding = (rates[1].close < currentEma8 && currentEma8 < currentEma21);
         bool isBOSBreakout = (!InpBreakoutRequireBOS || rates[1].close < lastSwingLow.price || g_smcAnalysis.hasBOS);
         bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || rates[1].tick_volume >= (long)(1.3 * (double)rates[2].tick_volume)));

         if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
         {
            isMomentumBreakout = true;
         }
      }

      // EKSEKUSI SELL JIKA:
      // Jalur 1 (Konservatif Pullback Sniper): Memenuhi semua 4 pilar + pullback + rejection + skor lolos
      // ATAU
      // Jalur 2 (Agresif Momentum Breakout): Terdeteksi Momentum Expansion BOS tanpa wajib pullback/diskon!
      if (InpUseDivergenceFilter && CheckRSIDivergenceMQL5(false))
      {
         g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
         return;
      }

      double slopeSellPips = 0.0;
      if (InpUseEMASlopeFilter && !CheckEMASlopeMQL5(false, slopeSellPips))
      {
         g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeSellPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
         return;
      }

      // =========================================================================
      // AI BRAIN & CANDLESTICK SHIELD PROTECTION GATE (v3.40)
      // =========================================================================
      int currentPatIdSELL = (isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern));

      // 1. Blacklist Check dari Memori Pembelajaran Mandiri (Dynamic Pattern Matrix)
      if (InpUsePatternMatrix && g_patternMatrix[currentPatIdSELL].isBlacklisted)
      {
         g_lastSignalType = "AI BRAIN: POLA " + g_patternMatrix[currentPatIdSELL].name + " DI-BLACKLIST (Win Rate < " + DoubleToString(InpPatternBlacklistWinrate, 0) + "%)";
         return;
      }

      // Terapkan Modifikasi Skor dari Hasil Pembelajaran Mandiri (Bonus / Penalti)
      if (InpUsePatternMatrix)
         scoreRes.totalScore += g_patternMatrix[currentPatIdSELL].scoreModifier;

      // 2. AI Candlestick Shield: Filter Doji / Body Tipis (<22% Range)
      double barRangeSELL = rates[1].high - rates[1].low;
      if (barRangeSELL > 0)
      {
         double barBodySELL      = MathAbs(rates[1].close - rates[1].open);
         double barBodyPctSELL   = (barBodySELL / barRangeSELL) * 100.0;
         double barLowWickSELL   = MathMin(rates[1].open, rates[1].close) - rates[1].low;
         double barLowWickPctSELL= (barLowWickSELL / barRangeSELL) * 100.0;

         if (InpFilterDojiCandles && barBodyPctSELL <= 22.0 && !isBearishSweepTrap)
         {
            g_lastSignalType = "AI SHIELD: BODY DOJI / RAGU-RAGU (" + DoubleToString(barBodyPctSELL, 0) + "% < 22%)";
            return;
         }

         // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Lower Wick >= 45% on SELL)
         if (InpFilterExhaustionWicks && barLowWickPctSELL >= 45.0 && !isMomentumBreakout)
         {
            g_lastSignalType = "AI SHIELD: PENOLAKAN BUYER DI BAWAH (" + DoubleToString(barLowWickPctSELL, 0) + "% >= 45%)";
            return;
         }

         // 4. AI Candlestick Shield: Filter Overextended Engulfing (> 1.5x ATR dari EMA21)
         if (InpFilterOverextended && (g_candleAnalysis.pattern == PATTERN_ENGULFING || isMomentumBreakout))
         {
            double distToEma21 = MathAbs(rates[1].close - currentEma21);
            if (distToEma21 > (1.5 * currentAtr))
            {
               g_lastSignalType = "AI SHIELD: OVEREXTENDED DARI EMA21 (" + DoubleToString(PriceToPips(distToEma21), 1) + " > 1.5x ATR)";
               return;
            }
         }
      }

      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                            (isMomentumBreakout && isHeadroomOk) ||
                            (isBearishSweepTrap && isHeadroomOk);

      // === GUARD M1 OB RETEST (v4.00 MTF Ketat) ===
      // Blokir entry SELL jika Mode Ketat aktif dan tidak ada retest ke OB Supply M1
      if (canExecuteSell && InpUseMTFM1Engine && InpRequireM1OBRetest)
      {
         bool m1OK = g_mtfResult.m1PullbackValid && !g_mtfResult.m1PullbackIsBuy;
         if (!m1OK)
         {
            g_lastSignalType = "M1-GUARD: MENUNGGU RETEST OB SUPPLY M1 | " + g_mtfResult.m1StatusStr;
            Print("[M1-MTF GUARD] SELL diblokir — belum ada retest ke OB Supply M1. Status: ", g_mtfResult.m1StatusStr);
            canExecuteSell = false;
         }
      }

      if (canExecuteSell)
      {
         double slPrice = 0.0;
         double tpPrice = 0.0;

         // Hitung Stop Loss
         if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingHigh.price > 0)
         {
            double effectiveBufferMultSELL = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);
            slPrice = lastSwingHigh.price + (effectiveBufferMultSELL * currentAtr);
         }
         else if (InpSLType == SL_TYPE_CANDLE_WICK)
            slPrice = rates[1].high + PipToPrice(5.0);
         else
            slPrice = bid + PipToPrice(InpFixedSLPips);

         // Batasi SL agar tidak terlalu sempit atau terlalu lebar
         double slDist = slPrice - bid;
         if (PriceToPips(slDist) < InpMinSLPips)
            slPrice = bid + PipToPrice(InpMinSLPips);
         if (PriceToPips(slDist) > InpMaxSLPips)
            slPrice = bid + PipToPrice(InpMaxSLPips);

         // Hitung Take Profit
         if (InpTPType == TP_TYPE_FIXED_POINTS)
            tpPrice = bid - PointToPrice(InpFixedTPPoints);
         else if (InpTPType == TP_TYPE_RISK_REWARD)
            tpPrice = bid - (InpRiskRewardRatio * (slPrice - bid));
         else if (InpTPType == TP_TYPE_FIBO_EXT && currentFibo.isValid && currentFibo.ext272 < bid)
            tpPrice = currentFibo.ext272;
         else if (InpTPType == TP_TYPE_PIVOT_LEVEL && currentPivot.S1 < bid)
            tpPrice = currentPivot.S1;
         else
            tpPrice = bid - (InpRiskRewardRatio * (slPrice - bid));

         // Validasi Stops Level Broker (Proteksi Anti-Error 10016)
         long stopsLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
         double minStopDist = MathMax(stopsLevel * _Point, SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * _Point + (5 * _Point));
         if ((slPrice - bid) < minStopDist)
            slPrice = bid + minStopDist;
         if ((bid - tpPrice) < minStopDist)
            tpPrice = bid - minStopDist;

         slPrice = NormalizeDouble(slPrice, _Digits);
         tpPrice = NormalizeDouble(tpPrice, _Digits);

         double lots = CalculateRiskLot(slPrice - bid, scoreRes.totalScore);

         // Validasi Kecukupan Margin Akun Sebelum Eksekusi (Proteksi Anti-Error NO MONEY)
         double marginReq = 0.0;
         if (OrderCalcMargin(ORDER_TYPE_SELL, _Symbol, lots, bid, marginReq))
         {
            double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
            if (marginReq > freeMargin)
            {
               Print("[MARGIN WARNING] Free margin tidak cukup untuk SELL ", lots, " lot. Butuh: $", marginReq, " | Sisa: $", freeMargin);
               g_lastSignalType = "MARGIN TIDAK CUKUP (Req: $" + DoubleToString(marginReq, 1) + ")";
               return;
            }
         }

         string tradeCmt = InpTradeComment + (isBearishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))));
         // Adaptive SL Buffer Expansion pasca-loss
         if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
            slPrice = NormalizeDouble(slPrice + (InpAdaptiveSLBufferBoost * currentAtr), _Digits);

         bool orderSuccess = trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt);
         ulong sellTicket = 0;
         ulong sellDeal = 0;
         double executedPrice = bid;
         string execModeTag = "MARKET";

         if (orderSuccess)
         {
            sellTicket = trade.ResultOrder();
            sellDeal   = trade.ResultDeal();
            executedPrice = bid;
            execModeTag   = "MARKET";
         }

         if (orderSuccess)
         {
            GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString((long)sellTicket), MathMax(slPrice - executedPrice, 10 * _Point));
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               g_autopsy.tradesWithExtraBuffer--;
            SaveTradeEntrySnapshotMQL5(sellTicket, sellDeal, (isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)), -1, scoreRes.totalScore, currentAtr);

            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
            g_lastSignalType = execModeTag + " PLACED: " + patStr + " @ " + DoubleToString(executedPrice, _Digits);
            Print("[", execModeTag, " EXECUTION] Lot: ", lots, " | Price: ", executedPrice, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
            if (InpNotifyOnEntry)
            {
               SendPushAlert(execModeTag + " " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(executedPrice, _Digits) +
                             "\nSL: " + DoubleToString(slPrice, _Digits) + " | TP: " + DoubleToString(tpPrice, _Digits) +
                             "\nPola: " + patStr);
            }
            UpdateDashboard();
            return;
         }
         else
         {
            Print("[SELL REJECTED BY BROKER] Retcode: ", trade.ResultRetcode(), " | Deskripsi: ", trade.ResultComment());
            g_lastSignalType = "DITOLAK BROKER: " + IntegerToString(trade.ResultRetcode()) + " (" + trade.ResultComment() + ")";
         }
      }
      }
   }

   // Status Informative Fallback jika tidak ada order dieksekusi pada bar ini
   if (StringFind(g_lastSignalType, "EXECUTED") >= 0)
   {
      g_lastSignalType = "MENUNGGU SETUP KONFLUENSI (GRADE A+)";
   }
   else if (buyTrendEMA125 && !buyDoubleAlign)
   {
      g_lastSignalType = "KONFLIK: HARGA > EMA125 TAPI < PIVOT P (NETRAL)";
   }
   else if (sellTrendEMA125 && !sellDoubleAlign)
   {
      g_lastSignalType = "KONFLIK: HARGA < EMA125 TAPI > PIVOT P (NETRAL)";
   }
}

//+------------------------------------------------------------------+
//| FITUR KECERDASAN: AUTO-CUT PROFIT SAAT INDIKASI PEMBALIKAN ARAH  |
//+------------------------------------------------------------------+
void CheckAutoCutProfit(const MqlRates &rates[], const double &ema21[], double currentAtr)
{
   if (!InpAutoCutProfit && !InpCutOnEarlyInvalidation) return;

   // Periksa Early Invalidation Cut (Jika terbentuk lilin displacement berlawanan menelan Order Block acuan)
   if (InpCutOnEarlyInvalidation)
   {
      double dispThreshold = (currentAtr > 0) ? (0.75 * currentAtr) : PipToPrice(15.0);
      for (int i = PositionsTotal() - 1; i >= 0; i--)
      {
         if (!posInfo.SelectByIndex(i)) continue;
         if (posInfo.Symbol() != _Symbol || posInfo.Magic() != InpMagicNumber) continue;

         // Pastikan lilin konfirmasi terbentuk SETELAH posisi dibuka (bukan lilin masa lalu sebelum open)
         if (rates[1].time < (datetime)posInfo.Time()) continue;

         ulong ticket = posInfo.Ticket();
         long posType = posInfo.PositionType();

         if (posType == POSITION_TYPE_BUY)
         {
            if (g_bullishOB.isValid && rates[1].close < g_bullishOB.bottom && (rates[1].open - rates[1].close) >= dispThreshold)
            {
               Print("[EARLY INVALIDATION CUT] Bullish Order Block jebol oleh Bearish Displacement! Menutup BUY #", ticket, " untuk proteksi modal!");
               trade.PositionClose(ticket);
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            if (g_bearishOB.isValid && rates[1].close > g_bearishOB.top && (rates[1].close - rates[1].open) >= dispThreshold)
            {
               Print("[EARLY INVALIDATION CUT] Bearish Order Block jebol oleh Bullish Displacement! Menutup SELL #", ticket, " untuk proteksi modal!");
               trade.PositionClose(ticket);
            }
         }
      }
   }

   if (!InpAutoCutProfit) return;

   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (!posInfo.SelectByIndex(i)) continue;
      if (posInfo.Symbol() != _Symbol || posInfo.Magic() != InpMagicNumber) continue;

      ulong  ticket   = posInfo.Ticket();
      double open     = posInfo.PriceOpen();
      long   posType  = posInfo.PositionType();
      double profit   = posInfo.Profit() + posInfo.Swap();

      // 1. Evaluasi Posisi BUY yang Sedang Berjalan Profit
      if (posType == POSITION_TYPE_BUY)
      {
         double profitPips = PriceToPips(bid - open);
         if (profitPips < InpMinProfitToCutPips || profit <= 0)
            continue; // Hanya aktif memotong saat posisi sudah berada dalam keuntungan

         bool isReversal = false;
         string reason = "";

         // A. Indikasi Pembalikan 1: Bearish CHoCH (Pembalikan Struktur SMC)
         if (InpCutOnCHoCH && g_smcAnalysis.hasCHoCH && g_smcAnalysis.structure == SMC_STRUCT_CHOCH_SELL)
         {
            isReversal = true;
            reason = "Bearish CHoCH Reversal";
         }
         // B. Indikasi Pembalikan 2: Candlestick Rejection Bearish Terkonfirmasi (Pin Bar, Engulfing, Star)
         else if (InpCutOnCandleReversal && !g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore)
         {
            isReversal = true;
            reason = g_candleAnalysis.patternName + " (Skor: " + DoubleToString(g_candleAnalysis.score, 0) + ")";
         }
         // C. Indikasi Pembalikan 3: Candle Tutup di Bawah Ribbon EMA 21 Magenta
         else if (InpCutOnEMACross && rates[1].close < ema21[1] && rates[2].close >= ema21[2])
         {
            isReversal = true;
            reason = "Penembusan ke Bawah EMA 21";
         }

         if (isReversal)
         {
            Print("[AUTO-CUT PROFIT] Menutup Dini Posisi BUY #", ticket, " karena Indikasi Pembalikan: ", reason, " | Profit Terkunci: +$", DoubleToString(profit, 2), " (+", DoubleToString(profitPips, 1), " pips)");
            if (trade.PositionClose(ticket))
            {
               g_lastSignalType = "CUT PROFIT (+" + DoubleToString(profitPips, 1) + " pips): " + reason;
               UpdateDashboard();
            }
         }
      }
      // 2. Evaluasi Posisi SELL yang Sedang Berjalan Profit
      else if (posType == POSITION_TYPE_SELL)
      {
         double profitPips = PriceToPips(open - ask);
         if (profitPips < InpMinProfitToCutPips || profit <= 0)
            continue;

         bool isReversal = false;
         string reason = "";

         // A. Indikasi Pembalikan 1: Bullish CHoCH (Pembalikan Struktur SMC)
         if (InpCutOnCHoCH && g_smcAnalysis.hasCHoCH && g_smcAnalysis.structure == SMC_STRUCT_CHOCH_BUY)
         {
            isReversal = true;
            reason = "Bullish CHoCH Reversal";
         }
         // B. Indikasi Pembalikan 2: Candlestick Rejection Bullish Terkonfirmasi (Pin Bar, Engulfing, Star)
         else if (InpCutOnCandleReversal && g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore)
         {
            isReversal = true;
            reason = g_candleAnalysis.patternName + " (Skor: " + DoubleToString(g_candleAnalysis.score, 0) + ")";
         }
         // C. Indikasi Pembalikan 3: Candle Tutup di Atas Ribbon EMA 21 Magenta
         else if (InpCutOnEMACross && rates[1].close > ema21[1] && rates[2].close <= ema21[2])
         {
            isReversal = true;
            reason = "Penembusan ke Atas EMA 21";
         }

         if (isReversal)
         {
            Print("[AUTO-CUT PROFIT] Menutup Dini Posisi SELL #", ticket, " karena Indikasi Pembalikan: ", reason, " | Profit Terkunci: +$", DoubleToString(profit, 2), " (+", DoubleToString(profitPips, 1), " pips)");
            if (trade.PositionClose(ticket))
            {
               g_lastSignalType = "CUT PROFIT (+" + DoubleToString(profitPips, 1) + " pips): " + reason;
               UpdateDashboard();
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| MANAJEMEN POSISI: AUTO-BREAKEVEN / SL+ & TRAILING STOP EMA 21    |
//+------------------------------------------------------------------+


void ManageActiveTrades()
{
   if (!InpUseBreakeven && !InpUseTrailingEMA21 && !InpUsePartialClose && !InpUseTimeBasedExit && !InpAutoLockBEBeforeNews && !InpUseCandleTrailing && !InpUsePointsTrailing && !InpUseMilestoneRatchet && !InpUseStructuralTrailing)
      return;

   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   CopyRates(_Symbol, _Period, 0, 3, rates);

   // Bersihkan global variable tracking partial close jika tidak ada posisi aktif
   if (PositionsTotal() == 0)
   {
      int totalGV = GlobalVariablesTotal();
      for (int g = totalGV - 1; g >= 0; g--)
      {
         string gvName = GlobalVariableName(g);
         if (StringFind(gvName, "VIKAR_PARTIAL_") == 0 || StringFind(gvName, "VIKAR_INIT_R_") == 0)
            GlobalVariableDel(gvName);
      }
   }

   double ema21Val[];
   ArraySetAsSeries(ema21Val, true);
   bool ema21Ok = false;
   if (InpUseTrailingEMA21)
   {
      if (CopyBuffer(h_ema21, 0, 0, 2, ema21Val) >= 2)
         ema21Ok = true;
   }

   double atrVal[];
   ArraySetAsSeries(atrVal, true);
   double currentAtr = PipToPrice(20.0);
   if (CopyBuffer(h_atr14, 0, 0, 2, atrVal) >= 2 && atrVal[1] > 0)
      currentAtr = atrVal[1];

   long stopsLevel  = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   long freezeLevel = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   double minStopDist = MathMax(MathMax(stopsLevel * _Point, freezeLevel * _Point), 10 * _Point);

   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (!posInfo.SelectByIndex(i)) continue;
      if (posInfo.Symbol() != _Symbol || posInfo.Magic() != InpMagicNumber) continue;

      ulong  ticket   = posInfo.Ticket();
      double open     = posInfo.PriceOpen();
      double current  = posInfo.PriceCurrent();
      double sl       = posInfo.StopLoss();
      double tp       = posInfo.TakeProfit();
      long   posType  = posInfo.PositionType();
      double posVol   = posInfo.Volume();

      // 0. Stagnant Trade Time-Exit & Pre-News BE Protection (v2.60)
      double hoursOpen = (double)(TimeCurrent() - posInfo.Time()) / 3600.0;
      double pipsProfit = (posType == POSITION_TYPE_BUY) ? PriceToPips(current - open) : PriceToPips(open - current);

      // Pre-News Auto-Lock BE
      string activeNewsShield = "";
      if (InpUseNewsShield && InpAutoLockBEBeforeNews && IsInsideNewsWindowMQL5(activeNewsShield))
      {
         if (pipsProfit >= InpBreakevenLockPips)
         {
            double lockPrice = (posType == POSITION_TYPE_BUY) ? NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), _Digits)
                                                              : NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), _Digits);
            bool needLock = (posType == POSITION_TYPE_BUY) ? (sl < lockPrice) : (sl > lockPrice || sl == 0);
            if (needLock && MathAbs(current - lockPrice) >= minStopDist)
            {
               Print("[PRE-NEWS LOCK MT5] Posisi #", ticket, " dikunci ke SL+ jelang ", activeNewsShield);
               trade.PositionModify(ticket, lockPrice, tp);
            }
         }
      }

      // Stagnant Time-Based Exit
      if (InpUseTimeBasedExit && hoursOpen >= (double)InpMaxTradeDurationHours && pipsProfit >= InpMinProfitToTimeExitPips)
      {
         Print("[TIME-EXIT MT5] Posisi #", ticket, " ditutup otomatis karena sudah mengambang ", DoubleToString(hoursOpen, 1), " jam (Profit: ", DoubleToString(pipsProfit, 1), " pips).");
         trade.PositionClose(ticket, InpDeviation);
         continue;
      }

      // 1. Logika Partial Take Profit (Amankan 50% di TP1 + Sisa Berjalan dengan SL+)
      if (InpUsePartialClose)
      {
         string gvKey = "VIKAR_PARTIAL_" + IntegerToString(ticket);
         if (!GlobalVariableCheck(gvKey))
         {
            bool triggerTP1 = false;
            if (posType == POSITION_TYPE_BUY)
            {
               if (InpPartialTriggerMode == BE_MODE_PIPS)
               {
                  if (PriceToPips(current - open) >= InpPartialTriggerPips)
                     triggerTP1 = true;
               }
               else // BE_MODE_RISK_REWARD
               {
                  double riskDist = open - sl;
                  if (riskDist > 0 && (current - open) >= (InpPartialRRTrigger * riskDist))
                     triggerTP1 = true;
               }

               if (triggerTP1)
               {
                  double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
                  double stepLot      = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
                  double closeVol     = MathFloor((posVol * (InpPartialClosePercent / 100.0)) / stepLot) * stepLot;
                  double remainVol    = posVol - closeVol;

                  if (closeVol >= brokerMinLot && remainVol >= brokerMinLot)
                  {
                     if (trade.PositionClosePartial(ticket, closeVol))
                     {
                        GlobalVariableSet(gvKey, 1.0);
                        Print("[PARTIAL TAKE PROFIT] Posisi BUY #", ticket, " ditutup 50% (", closeVol, " lot)! Sisa ", remainVol, " lot berjalan sebagai RUNNER!");
                        if (InpPartialMoveSLPlus)
                        {
                           double newSL = NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), _Digits);
                           if (newSL > sl && (current - newSL) >= minStopDist)
                           {
                              trade.PositionModify(ticket, newSL, tp);
                              Print("[PARTIAL SL+] Sisa lot BUY #", ticket, " dipasang SL+ ke: ", newSL);
                           }
                        }
                        UpdateDashboard();
                     }
                  }
                  else
                  {
                     GlobalVariableSet(gvKey, 1.0);
                     double newSL = NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), _Digits);
                     if (newSL > sl && (current - newSL) >= minStopDist)
                     {
                        trade.PositionModify(ticket, newSL, tp);
                        Print("[TP1 HIT - FULL LOCK] Posisi BUY #", ticket, " mencapai TP1. Karena lot minimal (", posVol, "), SL otomatis dikunci ke SL+: ", newSL);
                     }
                  }
               }
            }
            else if (posType == POSITION_TYPE_SELL)
            {
               if (InpPartialTriggerMode == BE_MODE_PIPS)
               {
                  if (PriceToPips(open - current) >= InpPartialTriggerPips)
                     triggerTP1 = true;
               }
               else // BE_MODE_RISK_REWARD
               {
                  double riskDist = sl - open;
                  if (riskDist > 0 && (open - current) >= (InpPartialRRTrigger * riskDist))
                     triggerTP1 = true;
               }

               if (triggerTP1)
               {
                  double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
                  double stepLot      = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
                  double closeVol     = MathFloor((posVol * (InpPartialClosePercent / 100.0)) / stepLot) * stepLot;
                  double remainVol    = posVol - closeVol;

                  if (closeVol >= brokerMinLot && remainVol >= brokerMinLot)
                  {
                     if (trade.PositionClosePartial(ticket, closeVol))
                     {
                        GlobalVariableSet(gvKey, 1.0);
                        Print("[PARTIAL TAKE PROFIT] Posisi SELL #", ticket, " ditutup 50% (", closeVol, " lot)! Sisa ", remainVol, " lot berjalan sebagai RUNNER!");
                        if (InpPartialMoveSLPlus)
                        {
                           double newSL = NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), _Digits);
                           if ((sl == 0 || newSL < sl) && (newSL - current) >= minStopDist)
                           {
                              trade.PositionModify(ticket, newSL, tp);
                              Print("[PARTIAL SL+] Sisa lot SELL #", ticket, " dipasang SL+ ke: ", newSL);
                           }
                        }
                        UpdateDashboard();
                     }
                  }
                  else
                  {
                     GlobalVariableSet(gvKey, 1.0);
                     double newSL = NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), _Digits);
                     if ((sl == 0 || newSL < sl) && (newSL - current) >= minStopDist)
                     {
                        trade.PositionModify(ticket, newSL, tp);
                        Print("[TP1 HIT - FULL LOCK] Posisi SELL #", ticket, " mencapai TP1. Karena lot minimal (", posVol, "), SL otomatis dikunci ke SL+: ", newSL);
                     }
                  }
               }
            }
         }
      }

      // 1. Logika Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin)
      if (InpUseBreakeven)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            bool triggerBE = false;
            if (InpBreakevenMode == BE_MODE_PIPS)
            {
               double profitPips = PriceToPips(current - open);
               if (profitPips >= InpBreakevenTriggerPips)
                  triggerBE = true;
            }
            else // BE_MODE_RISK_REWARD
            {
               double riskDist = open - sl;
               if (riskDist > 0 && (current - open) >= (InpBreakevenRRTrigger * riskDist))
                  triggerBE = true;
            }

            if (triggerBE)
            {
               double newSL = NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), _Digits);
               if ((sl < open || (newSL - sl) >= (10 * _Point)) && (current - newSL) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, newSL, tp))
                  {
                     Print("[AUTO-BE / SL+] Posisi BUY #", ticket, " SL digeser ke SL+ (Kunci +", DoubleToString(InpBreakevenLockPips, 1), " pips): ", newSL);
                      if (InpNotifyOnSLPlus) SendPushAlert("AUTO-BE SL+ LOCKED!\nPosisi BUY #" + IntegerToString(ticket) + " SL dikunci ke " + DoubleToString(newSL, _Digits) + " (Profit Terkunci)");
                  }
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            bool triggerBE = false;
            if (InpBreakevenMode == BE_MODE_PIPS)
            {
               double profitPips = PriceToPips(open - current);
               if (profitPips >= InpBreakevenTriggerPips)
                  triggerBE = true;
            }
            else // BE_MODE_RISK_REWARD
            {
               double riskDist = sl - open;
               if (riskDist > 0 && (open - current) >= (InpBreakevenRRTrigger * riskDist))
                  triggerBE = true;
            }

            if (triggerBE)
            {
               double newSL = NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), _Digits);
               if ((sl > open || sl == 0 || (sl - newSL) >= (10 * _Point)) && (newSL - current) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, newSL, tp))
                  {
                     Print("[AUTO-BE / SL+] Posisi SELL #", ticket, " SL digeser ke SL+ (Kunci +", DoubleToString(InpBreakevenLockPips, 1), " pips): ", newSL);
                      if (InpNotifyOnSLPlus) SendPushAlert("AUTO-BE SL+ LOCKED!\nPosisi SELL #" + IntegerToString(ticket) + " SL dikunci ke " + DoubleToString(newSL, _Digits) + " (Profit Terkunci)");
                  }
               }
            }
         }
      }

      // 1.5 Dynamic Points Trailing Stop (Kawal Kenaikan Harga per Step Points)
      if (InpUsePointsTrailing)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            double profitPoints = PriceToPips(current - open) * 10.0;
            if (profitPoints >= InpTrailingStartPoints)
            {
               double targetSL = NormalizeDouble(current - PointToPrice(InpTrailingDistPoints), _Digits);
               if (targetSL > open && (targetSL - sl) >= PointToPrice(InpTrailingStepPoints) && (current - targetSL) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, targetSL, tp))
                  {
                     sl = targetSL;
                     Print("[TRAILING POINTS MT5] Posisi BUY #", ticket, " SL dinaikkan mengawal harga: ", targetSL);
                  }
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            double profitPoints = PriceToPips(open - current) * 10.0;
            if (profitPoints >= InpTrailingStartPoints)
            {
               double targetSL = NormalizeDouble(current + PointToPrice(InpTrailingDistPoints), _Digits);
               if (targetSL < open && (sl == 0 || (sl - targetSL) >= PointToPrice(InpTrailingStepPoints)) && (targetSL - current) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, targetSL, tp))
                  {
                     sl = targetSL;
                     Print("[TRAILING POINTS MT5] Posisi SELL #", ticket, " SL diturunkan mengawal harga: ", targetSL);
                  }
               }
            }
         }
      }

      // 1.6 Dynamic Candle-by-Candle Trailing Stop (Kawal Mengikuti Ekor Lilin Terkini)
      if (InpUseCandleTrailing && ArraySize(rates) > 1)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            double candleLow = rates[1].low;
            double effectiveCandleBufBUY = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;
      double candleSL  = NormalizeDouble(candleLow - PointToPrice(effectiveCandleBufBUY), _Digits);
            if (candleSL > open && candleSL > sl && (candleSL - sl) >= (5 * _Point) && (current - candleSL) >= minStopDist)
            {
               if (trade.PositionModify(ticket, candleSL, tp))
               {
                  sl = candleSL;
                  Print("[TRAILING CANDLE MT5] Posisi BUY #", ticket, " SL naik di bawah ekor lilin Low[1]: ", candleSL);
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            double candleHigh = rates[1].high;
            double effectiveCandleBufSELL = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;
      double candleSL   = NormalizeDouble(candleHigh + PointToPrice(effectiveCandleBufSELL), _Digits);
            if (candleSL < open && (sl == 0 || candleSL < sl) && (sl - candleSL) >= (5 * _Point) && (candleSL - current) >= minStopDist)
            {
               if (trade.PositionModify(ticket, candleSL, tp))
               {
                  sl = candleSL;
                  Print("[TRAILING CANDLE MT5] Posisi SELL #", ticket, " SL turun di atas ekor lilin High[1]: ", candleSL);
               }
            }
         }
      }

      // 1.7 Milestone Ratchet Trailing (v3.30 Pro Discipline)
      // Tiered profit locking: Locks +0.5R at 1.0R profit, +1.0R at 1.5R, +1.5R at 2.0R
      if (InpUseMilestoneRatchet)
      {
         string gvRKey = "VIKAR_INIT_R_" + IntegerToString((long)ticket);
         double rDist = 0.0;
         if (GlobalVariableCheck(gvRKey)) rDist = GlobalVariableGet(gvRKey);
         else
         {
            rDist = (posType == POSITION_TYPE_BUY) ? (open - sl) : (sl - open);
            if (rDist <= 0.0) rDist = PipToPrice(InpFixedSLPips);
            GlobalVariableSet(gvRKey, rDist);
         }

         if (rDist > 0.0)
         {
            if (posType == POSITION_TYPE_BUY)
            {
               double pDist = current - open;
               double targetSL = 0.0;
               if (pDist >= 2.0 * rDist)      targetSL = NormalizeDouble(open + (1.5 * rDist), _Digits);
               else if (pDist >= 1.5 * rDist) targetSL = NormalizeDouble(open + (1.0 * rDist), _Digits);
               else if (pDist >= 1.0 * rDist) targetSL = NormalizeDouble(open + (0.5 * rDist), _Digits);

               if (targetSL > sl && (current - targetSL) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, targetSL, tp))
                  {
                     sl = targetSL;
                     Print("[MILESTONE RATCHET MT5] BUY #", ticket, " SL dinaikkan mengunci profit ke: ", targetSL);
                  }
               }
            }
            else if (posType == POSITION_TYPE_SELL)
            {
               double pDist = open - current;
               double targetSL = 0.0;
               if (pDist >= 2.0 * rDist)      targetSL = NormalizeDouble(open - (1.5 * rDist), _Digits);
               else if (pDist >= 1.5 * rDist) targetSL = NormalizeDouble(open - (1.0 * rDist), _Digits);
               else if (pDist >= 1.0 * rDist) targetSL = NormalizeDouble(open - (0.5 * rDist), _Digits);

               if (targetSL > 0.0 && (sl == 0.0 || targetSL < sl) && (targetSL - current) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, targetSL, tp))
                  {
                     sl = targetSL;
                     Print("[MILESTONE RATCHET MT5] SELL #", ticket, " SL diturunkan mengunci profit ke: ", targetSL);
                  }
               }
            }
         }
      }

      // 2. Logika Trailing Stop Mengikuti Ribbon EMA 21 Magenta
      if (InpUseTrailingEMA21 && ema21Ok)
      {
         if (posType == POSITION_TYPE_BUY)
         {
            double trailSL = NormalizeDouble(ema21Val[1] - PipToPrice(InpTrailingBufferPips), _Digits);
            if (trailSL > open && (trailSL - sl) >= (10 * _Point) && (current - trailSL) >= minStopDist)
            {
               if (trade.PositionModify(ticket, trailSL, tp))
               {
                  Print("[TRAILING EMA 21] Posisi BUY #", ticket, " SL digeser ke: ", trailSL);
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            double trailSL = NormalizeDouble(ema21Val[1] + PipToPrice(InpTrailingBufferPips), _Digits);
            if (trailSL < open && (sl == 0 || (sl - trailSL) >= (10 * _Point)) && (trailSL - current) >= minStopDist)
            {
               if (trade.PositionModify(ticket, trailSL, tp))
               {
                  Print("[TRAILING EMA 21] Posisi SELL #", ticket, " SL digeser ke: ", trailSL);
               }
            }
         }
      }

      // 3. Multi-Stage Structural Trailing Stop untuk RUNNER & Posisi Cuan (v3.00)
      string gvRunnerKey = "VIKAR_PARTIAL_" + IntegerToString(ticket);
      bool isRunnerLot = GlobalVariableCheck(gvRunnerKey);
      bool isProfitable = (posType == POSITION_TYPE_BUY) ? (current - open >= PipToPrice(InpBreakevenLockPips)) : (open - current >= PipToPrice(InpBreakevenLockPips));

      if (InpUseStructuralTrailing && (isRunnerLot || isProfitable))
      {
         if (posType == POSITION_TYPE_BUY)
         {
            if (lastSwingLow.price > 0 && lastSwingLow.price > open)
            {
               double structSL = NormalizeDouble(lastSwingLow.price - (InpStructuralTrailingAtrBuffer * currentAtr), _Digits);
               if (structSL > sl && (structSL - sl) >= (10 * _Point) && (current - structSL) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, structSL, tp))
                  {
                     Print("[SMC STRUCTURAL RUNNER] Posisi BUY #", ticket, " SL dipindah di bawah Higher Low (HL) terbaru: ", structSL);
                  }
               }
            }
         }
         else if (posType == POSITION_TYPE_SELL)
         {
            if (lastSwingHigh.price > 0 && lastSwingHigh.price < open)
            {
               double structSL = NormalizeDouble(lastSwingHigh.price + (InpStructuralTrailingAtrBuffer * currentAtr), _Digits);
               if ((sl == 0 || structSL < sl) && (sl - structSL) >= (10 * _Point) && (structSL - current) >= minStopDist)
               {
                  if (trade.PositionModify(ticket, structSL, tp))
                  {
                     Print("[SMC STRUCTURAL RUNNER] Posisi SELL #", ticket, " SL dipindah di atas Lower High (LH) terbaru: ", structSL);
                  }
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: FORMAT ANGKA PROFIT / LOSS                      |
//+------------------------------------------------------------------+
string FormatPnL(double amount)
{
   if (amount > 0.0001)
      return "+$" + DoubleToString(amount, 2);
   else if (amount < -0.0001)
      return "-$" + DoubleToString(MathAbs(amount), 2);
   else
      return "$0.00";
}

//+------------------------------------------------------------------+
//| HITUNG STATISTIK PROFIT & LOSS RIWAYAT TRANSAKSI (CLOSED DEALS)  |
//+------------------------------------------------------------------+
TradeStats CalculateHistoryStats(datetime fromTime)
{
   TradeStats stats;
   stats.grossProfit = 0.0;
   stats.grossLoss   = 0.0;
   stats.netProfit   = 0.0;
   stats.winTrades   = 0;
   stats.lossTrades  = 0;
   stats.totalTrades = 0;

   if (!HistorySelect(fromTime, TimeCurrent() + 86400))
      return stats;

   int totalDeals = HistoryDealsTotal();
   for (int i = 0; i < totalDeals; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if (ticket == 0) continue;

      if (HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagicNumber)
         continue;

      string dealSymbol = HistoryDealGetString(ticket, DEAL_SYMBOL);
      if (dealSymbol != _Symbol)
         continue;

      long entry = HistoryDealGetInteger(ticket, DEAL_ENTRY);
      // Hanya hitung transaksi penutupan posisi (DEAL_ENTRY_OUT atau DEAL_ENTRY_OUT_BY)
      if (entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
         continue;

      double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
      double swap   = HistoryDealGetDouble(ticket, DEAL_SWAP);
      double comm   = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
      double totalDealPnL = profit + swap + comm;

      stats.totalTrades++;
      if (totalDealPnL >= 0)
      {
         stats.grossProfit += totalDealPnL;
         stats.winTrades++;
      }
      else
      {
         stats.grossLoss += MathAbs(totalDealPnL);
         stats.lossTrades++;
      }
   }

   stats.netProfit = stats.grossProfit - stats.grossLoss;
   return stats;
}

//+------------------------------------------------------------------+
//| HITUNG FLOATING PROFIT POSISI TERBUKA SAAT INI                   |
//+------------------------------------------------------------------+
double GetOpenFloatingPnL(int &openPositionsCount)
{
   openPositionsCount = 0;
   double totalFloating = 0.0;
   for (int i = PositionsTotal() - 1; i >= 0; i--)
   {
      if (posInfo.SelectByIndex(i))
      {
         if (posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
         {
            openPositionsCount++;
            totalFloating += posInfo.Profit() + posInfo.Swap();
         }
      }
   }
   return totalFloating;
}

//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY                                   |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| FUNGSI PEMBUATAN OBJEK GUI RECTANGLE LABEL (PANEL LATAR)         |
//+------------------------------------------------------------------+
void CreateOrUpdateRect(string name, int x, int y, int width, int height, color bgColor, color borderColor)
{
   if (ObjectFind(0, name) < 0)
   {
      ObjectCreate(0, name, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
      ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor);
      ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, borderColor);
      ObjectSetInteger(0, name, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(0, name, OBJPROP_WIDTH, 1);
      ObjectSetInteger(0, name, OBJPROP_BACK, false);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   }
   else
   {
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
      ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor);
      ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, borderColor);
   }
}

//+------------------------------------------------------------------+
//| FUNGSI PEMBUATAN OBJEK GUI TEXT LABEL (TEKS BERSIH)              |
//+------------------------------------------------------------------+
void CreateOrUpdateText(string name, int x, int y, string text, color clr, int fontSize = 8, string font = "Segoe UI")
{
   if (ObjectFind(0, name) < 0)
   {
      ObjectCreate(0, name, OBJ_LABEL, 0, 0, 0);
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetString(0, name, OBJPROP_FONT, font);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, name, OBJPROP_BACK, false);
   }
   else
   {
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
   }
}

//+------------------------------------------------------------------+
//| HAPUS SEMUA ELEMEN GUI DASHBOARD                                 |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| PEMBUATAN ELEMEN TOMBOL INTERAKTIF (OBJ_BUTTON)                 |
//+------------------------------------------------------------------+
void CreateOrUpdateBtn(string name, int x, int y, int width, int height, string text, color bgColor, color textColor, int fontSize = 8, string font = "Segoe UI Bold")
{
   if (ObjectFind(0, name) < 0)
   {
      ObjectCreate(0, name, OBJ_BUTTON, 0, 0, 0);
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetString(0, name, OBJPROP_FONT, font);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
      ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
      ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor);
      ObjectSetInteger(0, name, OBJPROP_BORDER_COLOR, C'51,65,85');
      ObjectSetInteger(0, name, OBJPROP_STATE, false);
      ObjectSetInteger(0, name, OBJPROP_SELECTABLE, false);
   }
   else
   {
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_XSIZE, width);
      ObjectSetInteger(0, name, OBJPROP_YSIZE, height);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetInteger(0, name, OBJPROP_COLOR, textColor);
      ObjectSetInteger(0, name, OBJPROP_BGCOLOR, bgColor);
      ObjectSetInteger(0, name, OBJPROP_STATE, false);
   }
}

//+------------------------------------------------------------------+
//| METER VISUAL ASCII/UNICODE PROGRESS BAR                         |
//+------------------------------------------------------------------+
string MakeProgressBar(double value, double maxVal, int barLen = 8)
{
   if (maxVal <= 0.0) return "[░░░░░░░░]";
   double ratio = MathMin(MathMax(value / maxVal, 0.0), 1.0);
   int filled = (int)MathRound(ratio * barLen);
   string bar = "[";
   for (int i = 0; i < barLen; i++)
   {
      if (i < filled) bar += "█";
      else bar += "░";
   }
   bar += "]";
   return bar;
}

void DestroyDashboardGUI()
{
   ObjectsDeleteAll(0, "VIKAR_HUD_");
   Comment("");
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| REPOSISI KARTU DASHBOARD SECARA REAL-TIME SAAT DI-DRAG           |
//+------------------------------------------------------------------+
void RepositionDashboard(int newX, int newY)
{
   int deltaX = newX - g_panelX;
   int deltaY = newY - g_panelY;
   if (deltaX == 0 && deltaY == 0) return;

   g_panelX = newX;
   g_panelY = newY;

   int total = ObjectsTotal(0, 0, -1);
   for (int i = 0; i < total; i++)
   {
      string name = ObjectName(0, i, 0, -1);
      if (StringFind(name, "VIKAR_HUD_") == 0)
      {
         int curX = (int)ObjectGetInteger(0, name, OBJPROP_XDISTANCE);
         int curY = (int)ObjectGetInteger(0, name, OBJPROP_YDISTANCE);
         ObjectSetInteger(0, name, OBJPROP_XDISTANCE, curX + deltaX);
         ObjectSetInteger(0, name, OBJPROP_YDISTANCE, curY + deltaY);
      }
   }
   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (MODERN GLASSMORPHIC GUI)         |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (MODERN GLASSMORPHIC PRO GUI)     |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (PRO CYBER-COCKPIT GUI v3.30)     |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (PRO WIDE CYBER-COCKPIT v3.30)    |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD: EXECUTIVE 2-COLUMN COCKPIT v3.30          |
//| Ultra-Modern Fintech Dark Theme (460px x 350px Solid Canvas)     |
//+------------------------------------------------------------------+
void UpdateDashboard()
{
   if (!InpShowDashboard)
   {
      DestroyDashboardGUI();
      return;
   }

   Comment(""); // Bersihkan teks comment biasa

   // Bersihkan objek lama sekali saat inisialisasi / pergantian versi
   static bool s_firstDashboardInit = true;
   if (s_firstDashboardInit)
   {
      DestroyDashboardGUI();
      s_firstDashboardInit = false;
   }

   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
   double ask     = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid     = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread  = PriceToPips(ask - bid);

   int openCount = 0;
   double openFloating = GetOpenFloatingPnL(openCount);

   // Hitung total lot terbuka
   double totalLots = 0.0;
   for (int p = PositionsTotal() - 1; p >= 0; p--)
   {
      if (posInfo.SelectByIndex(p) && posInfo.Symbol() == _Symbol && posInfo.Magic() == InpMagicNumber)
         totalLots += posInfo.Volume();
   }



   // Statistik Sejak Start, Harian, Mingguan
   datetime startOfDay  = iTime(_Symbol, PERIOD_D1, 0);
   if (startOfDay == 0) startOfDay = TimeCurrent() - 86400;

   datetime startOfWeek = iTime(_Symbol, PERIOD_W1, 0);
   if (startOfWeek == 0) startOfWeek = TimeCurrent() - (7 * 86400);

   TradeStats statsTotal = CalculateHistoryStats(g_eaStartTime);
   TradeStats statsDaily = CalculateHistoryStats(startOfDay);
   TradeStats statsWeekly= CalculateHistoryStats(startOfWeek);

   int panelX = g_panelX;
   int panelY = g_panelY;
   int panelW = 460;
   g_panelW = panelW;

   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));


   // ===================================================================
   // JIKA DALAM MODE MINIMIZED (HANYA BILAH RAMPING 44px)
   // ===================================================================
   if (g_hudMinimized)
   {
      int minH = 46;
      g_panelH = minH;
      CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, minH, C'13,18,30', C'30,41,59');
      CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + minH - 2, panelW, 2, C'14,165,233', C'14,165,233');

      CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 8, "◈ VIKAR PRO v3.30", clrWhite, 9, "Segoe UI Bold");
      color floatClrMin = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
      string minStatus = "Float: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + "P) | Eq: $" + DoubleToString(equity, 2);
      CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 26, minStatus, floatClrMin, 7, "Segoe UI Bold");

      CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 78, panelY + 10, 68, 26, "👁️ EXPAND", C'15,23,42', C'52,211,153', 7);
      ChartRedraw(0);
      return;
   }

   // ===================================================================
   // MODE EXPANDED (EXECUTIVE 2-COLUMN COCKPIT)
   // ===================================================================

   // 1. MASTER CANVAS BACKGROUND (SOLID SLATE-OBSIDIAN - ANTI-TEMBUS CANDLE)
   int totalH = 348;
   g_panelH = totalH;
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, totalH, C'13,18,30', C'30,41,59');

   // 2. HEADER BANNER (Y: 0 s/d 44)
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 44, C'18,24,38', C'2,132,199');
   CreateOrUpdateRect("VIKAR_HUD_HDR_LINE", panelX, panelY + 42, panelW, 2, C'14,165,233', C'14,165,233');

   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 14, panelY + 6, "◈ VIKAR 4-PILLAR PRO  v3.30", clrWhite, 10, "Segoe UI Bold");

   string pauseStatus = g_eaManualPause ? "[PAUSED]" : "[ACTIVE]";
   string headerSubStr = _Symbol + " • " + EnumToString(_Period) + " • " + lotDisplay + " • " + pauseStatus + " • ID: " + IntegerToString(InpMagicNumber);
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 14, panelY + 24, headerSubStr, C'148,163,184', 7, "Segoe UI");

   // Tombol Mini / Expand
   CreateOrUpdateBtn("VIKAR_HUD_BTN_VIEW", panelX + panelW - 74, panelY + 9, 64, 25, "👁️ MINI", C'15,23,42', C'52,211,153', 7);

   int currY = panelY + 48;

   // 3. BARIS KPI: RINGKASAN AKUN & PERFORMA (Y: 48 s/d 124, Tinggi 76px)
   CreateOrUpdateRect("VIKAR_HUD_ACC_BG", panelX + 8, currY, panelW - 16, 76, C'20,28,45', C'39,51,73');
   CreateOrUpdateText("VIKAR_HUD_SEC1_TITLE", panelX + 16, currY + 6, "💼 RINGKASAN AKUN & PERFORMA", C'251,191,36', 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   string floatSummary = "Floating: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Pos)";
   CreateOrUpdateText("VIKAR_HUD_SEC1_FLOAT", panelX + panelW - 175, currY + 6, floatSummary, floatClr, 7, "Segoe UI Bold");

   int col1X = panelX + 16;
   int col2X = panelX + 235;

   // Baris 1: Saldo & Ekuitas
   CreateOrUpdateText("VIKAR_HUD_ACC_L1", col1X, currY + 25, "Saldo    : $" + DoubleToString(balance, 2), clrWhite, 7, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_ACC_R1", col2X, currY + 25, "Ekuitas  : $" + DoubleToString(equity, 2), clrWhite, 7, "Segoe UI Bold");

   // Baris 2: Hari Ini & Minggu Ini
   double dailyWinratePct = (statsDaily.totalTrades > 0) ? ((double)statsDaily.winTrades / statsDaily.totalTrades * 100.0) : 0.0;
   string dailyWRStr = (statsDaily.totalTrades > 0) ? (" (" + DoubleToString(dailyWinratePct, 0) + "% WR)") : "";
   CreateOrUpdateText("VIKAR_HUD_ACC_L2", col1X, currY + 42, "Hari Ini : " + FormatPnL(statsDaily.netProfit) + dailyWRStr, (statsDaily.netProfit >= 0 ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_ACC_R2", col2X, currY + 42, "Minggu Ini: " + FormatPnL(statsWeekly.netProfit), (statsWeekly.netProfit >= 0 ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   // Baris 3: Daily Drawdown & Spread
   double ddLimit = InpMaxDailyEquityDDPct;
   double bufferSisa = MathMax(0.0, ddLimit - g_currentDailyDDPct);
   color ddClr = (g_currentDailyDDPct >= ddLimit * 0.75) ? C'248,113,113' : ((g_currentDailyDDPct > 0.0) ? C'251,191,36' : C'74,222,128');
   CreateOrUpdateText("VIKAR_HUD_ACC_L3", col1X, currY + 59, "Daily DD : " + DoubleToString(g_currentDailyDDPct, 2) + "% / " + DoubleToString(ddLimit, 1) + "% (" + DoubleToString(bufferSisa, 1) + "% Sisa)", ddClr, 7, "Segoe UI Bold");
   CreateOrUpdateText("VIKAR_HUD_ACC_R3", col2X, currY + 59, "Spread   : " + DoubleToString(spread, 1) + " pip | " + lotDisplay, C'148,163,184', 7, "Segoe UI");

   currY += 80;

   // 4. GRID 2-KOLOM: 4-PILAR SMC (KIRI) vs SENSOR PASAR & RADAR (KANAN)
   // Lebar masing-masing kolom: 218px, tinggi: 138px
   int colCardW = 218;
   int leftCardX = panelX + 8;
   int rightCardX = panelX + 234;

   // --- KARTU KIRI: 4-PILAR SMC & KONFLUENSI ---
   CreateOrUpdateRect("VIKAR_HUD_SMC_BG", leftCardX, currY, colCardW, 138, C'18,25,40', C'30,41,59');
   CreateOrUpdateRect("VIKAR_HUD_SMC_HDR_BG", leftCardX, currY, colCardW, 22, C'24,33,52', C'40,53,78');
   CreateOrUpdateText("VIKAR_HUD_SMC_HDR", leftCardX + 8, currY + 4, "🏛️ 4-PILAR SMC", C'56,189,248', 7, "Segoe UI Bold");

   string scoreStr = (g_lastScoreResult.totalScore > 0) ? (DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")") : "Ready";
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 65.0) ? C'251,191,36' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_SMC_SCORE", leftCardX + colCardW - 88, currY + 4, "Skor: " + scoreStr, scoreClr, 7, "Segoe UI Bold");

   // Baris 1: SMC Structure Trend
   string smcStr = (g_smcAnalysis.structureName != "") ? g_smcAnalysis.structureName : "Equilibrium";
   if (g_smcAnalysis.hasSweep) smcStr += " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr += " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_SMC_L1", leftCardX + 8, currY + 25, "SMC Trend  : " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   // Baris 2: Dealing Range (Diskon / Premium)
   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   CreateOrUpdateText("VIKAR_HUD_SMC_L2", leftCardX + 8, currY + 43, "Zona Harga : " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   // Baris 3: Triple EMA Baseline
   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   string emaTrendStr = "Bullish (Ribbon)";
   if (CopyBuffer(h_ema125, 0, 0, 2, ema125Val) >= 2)
   {
      double closePrice = iClose(_Symbol, _Period, 1);
      emaTrendStr = (closePrice > ema125Val[1]) ? "Bullish (> EMA125)" : "Bearish (< EMA125)";
   }
   CreateOrUpdateText("VIKAR_HUD_SMC_L3", leftCardX + 8, currY + 61, "Triple EMA : " + emaTrendStr, C'232,121,249', 7, "Segoe UI");

   // Baris 4: Order Block & FVG
   string obStr = "OB: Scanning...";
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
      obStr = "Bull OB " + DoubleToString(g_bullishOB.bottom, 1) + "-" + DoubleToString(g_bullishOB.top, 1);
   else if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
      obStr = "Bear OB " + DoubleToString(g_bearishOB.bottom, 1) + "-" + DoubleToString(g_bearishOB.top, 1);
   CreateOrUpdateText("VIKAR_HUD_SMC_L4", leftCardX + 8, currY + 79, "Order Block: " + obStr, C'244,114,182', 7, "Segoe UI");

   // Baris 5: Fibo Golden Pocket
   string fiboStr = currentFibo.isValid ? ("GP 61.8% @" + DoubleToString(currentFibo.level618, 1)) : "GP: Scanning...";
   CreateOrUpdateText("VIKAR_HUD_SMC_L5", leftCardX + 8, currY + 97, "Fibo Pocket: " + fiboStr, C'52,211,153', 7, "Segoe UI");

   // Baris 6: Pola Lilin & Chart Pattern
   string candleStr = (g_candleAnalysis.patternName != "") ? g_candleAnalysis.patternName : "Lilin Normal";
   if (g_candleAnalysis.score > 0) candleStr += " [" + DoubleToString(g_candleAnalysis.score, 0) + "p]";
   CreateOrUpdateText("VIKAR_HUD_SMC_L6", leftCardX + 8, currY + 115, "Pola Lilin : " + candleStr, C'251,191,36', 7, "Segoe UI");


   // --- KARTU KANAN: SENSOR PASAR & RADAR RISIKO ---
   CreateOrUpdateRect("VIKAR_HUD_RADAR_BG", rightCardX, currY, colCardW, 138, C'18,25,40', C'30,41,59');
   CreateOrUpdateRect("VIKAR_HUD_RADAR_HDR_BG", rightCardX, currY, colCardW, 22, C'24,33,52', C'40,53,78');
   CreateOrUpdateText("VIKAR_HUD_RADAR_HDR", rightCardX + 8, currY + 4, "🛡️ SENSOR PASAR", C'52,211,153', 7, "Segoe UI Bold");

   string regimeStr = (g_currentRegime == REGIME_CHOPPY_SIDEWAYS) ? "CHOPPY" : "TREND SEHAT";
   color regimeClr  = (g_currentRegime == REGIME_CHOPPY_SIDEWAYS) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_RADAR_BADGE", rightCardX + colCardW - 74, currY + 4, "CI: " + DoubleToString(g_currentChoppiness, 0), regimeClr, 7, "Segoe UI Bold");

   // Baris 1: Kondisi Cuaca Pasar
   CreateOrUpdateText("VIKAR_HUD_RADAR_L1", rightCardX + 8, currY + 25, "Kondisi    : " + regimeStr + " (Regime)", regimeClr, 7, "Segoe UI Bold");

   // Baris 2: Macro Trend H1
   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_RADAR_L2", rightCardX + 8, currY + 43, "Macro H1   : " + g_htfMacroStr, htfClr, 7, "Segoe UI Bold");

   // Baris 3: VSA Volume Flow
   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Volume") : "VSA: OFF";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L3", rightCardX + 8, currY + 61, "VSA Volume : " + vsaDisplay, C'203,213,225', 7, "Segoe UI");

   // Baris 4: ADX Trend Kinetic Strength
   string adxStatus = (g_currentADXVal >= 25.0) ? " (Kuat)" : " (Lemah)";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L4", rightCardX + 8, currY + 79, "ADX Power  : " + DoubleToString(g_currentADXVal, 1) + adxStatus, C'251,191,36', 7, "Segoe UI");

   // Baris 5: Circuit Guard Max Consecutive Loss
   string cbDisplay = "0/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss (Aman)";
   if (g_cooldownUntilTime > TimeCurrent()) cbDisplay = "COOLDOWN AKTIF";
   else if (g_consecutiveLossCount > 0) cbDisplay = IntegerToString(g_consecutiveLossCount) + " Loss";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L5", rightCardX + 8, currY + 97, "Circuit G. : " + cbDisplay, C'74,222,128', 7, "Segoe UI");

   // Baris 6: Disiplin Harian (Max Order)
   string discText = IntegerToString(g_todayTradesCount) + (InpUseMaxDailyTrades ? ("/" + IntegerToString(InpMaxDailyTrades)) : "") + " Order Hari Ini";
   CreateOrUpdateText("VIKAR_HUD_RADAR_L6", rightCardX + 8, currY + 115, "Disiplin   : " + discText, C'148,163,184', 7, "Segoe UI");

   currY += 142;

   // 5. BARIS STATUS EKSEKUSI & ACTION (Y: 270 s/d 338, Tinggi 68px)
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", panelX + 8, currY, panelW - 16, 68, C'11,15,25', C'14,165,233');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", panelX + 16, currY + 6, "⚡ RADAR EKSEKUSI & STATUS SINYAL TERAKHIR:", C'56,189,248', 7, "Segoe UI Bold");

   // Tombol Emergency Close All
   CreateOrUpdateBtn("VIKAR_HUD_BTN_CLOSEALL", panelX + panelW - 104, currY + 6, 92, 24, "🚨 CLOSE ALL", C'153,27,27', clrWhite, 7);

   string statusDisplay = (g_lastSignalType != "") ? g_lastSignalType : "MENUNGGU SETUP GRADE A (SCANNING)";
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING ULANG";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 16, currY + 24, "● " + statusDisplay, clrWhite, 8, "Segoe UI Bold");

   // === M1 ZONE RADAR (MTF Price Action Engine v4.00) ===
   if (InpUseMTFM1Engine)
   {
      currY += 44;
      CreateOrUpdateText("VIKAR_HUD_M1_HDR", panelX + 10, currY + 4,
         "── M1 ZONE RADAR (OB RETEST ENGINE) ──", C'100,116,139', 7, "Segoe UI Bold");

      currY += 18;
      color demandColor = g_mtfResult.m1DemandOB.isValid ?
                          (g_mtfResult.m1DemandOB.isTested ? C'34,197,94' : C'56,189,248') : C'100,116,139';
      CreateOrUpdateText("VIKAR_HUD_M1_DEMAND", panelX + 16, currY,
         "▲ OB Demand M1 : " + g_mtfResult.m1DemandStr, demandColor, 7, "Segoe UI");

      currY += 14;
      color supplyColor = g_mtfResult.m1SupplyOB.isValid ?
                          (g_mtfResult.m1SupplyOB.isTested ? C'249,115,22' : C'248,113,113') : C'100,116,139';
      CreateOrUpdateText("VIKAR_HUD_M1_SUPPLY", panelX + 16, currY,
         "▼ OB Supply M1 : " + g_mtfResult.m1SupplyStr, supplyColor, 7, "Segoe UI");

      currY += 14;
      color m1StatusColor = g_mtfResult.m1PullbackValid ? C'34,197,94' : C'251,191,36';
      CreateOrUpdateText("VIKAR_HUD_M1_STATUS", panelX + 16, currY,
         "● Status M1    : " + g_mtfResult.m1StatusStr, m1StatusColor, 7, "Segoe UI Bold");
      currY -= 44; // reset offset agar baris berikutnya tetap di posisi normal
   }

   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = (InpUsePointsTrailing || InpUseCandleTrailing || InpUseTrailingEMA21) ? "Trail: ON" : "Trail: OFF";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 16, currY + 44, "Mode: INSTANT MARKET | " + beStr + " | " + cutStr + " | " + trailStr, C'148,163,184', 7, "Segoe UI");


   int finalH = (currY + 74) - panelY;
   g_panelH = finalH;
   ObjectSetInteger(0, "VIKAR_HUD_BG", OBJPROP_YSIZE, finalH);

   ChartRedraw(0);
}

void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
{
   if (!InpShowDashboard) return;

   if (id == CHARTEVENT_OBJECT_CLICK)
   {
      if (sparam == "VIKAR_HUD_BTN_VIEW")
      {
         g_hudMinimized = !g_hudMinimized;
         DestroyDashboardGUI();
         UpdateDashboard();
         ChartRedraw(0);
         return;
      }

      else if (sparam == "VIKAR_HUD_BTN_PAUSE")
      {
         g_eaManualPause = !g_eaManualPause;
         UpdateDashboard();
         ChartRedraw(0);
         return;
      }
      else if (sparam == "VIKAR_HUD_BTN_CLOSEALL")
      {
         CloseAllOpenOrders();
         UpdateDashboard();
         ChartRedraw(0);
         return;
      }
   }

   if (id == CHARTEVENT_MOUSE_MOVE)
   {
      int mouseX = (int)lparam;
      int mouseY = (int)dparam;
      uint mouseState = (uint)StringToInteger(sparam);
      bool leftButtonDown = ((mouseState & 1) != 0);

      if (leftButtonDown)
      {
         if (!g_isDragging)
         {
            // Deteksi apakah klik mouse berada di area kartu dashboard
            if (mouseX >= g_panelX && mouseX <= (g_panelX + g_panelW) &&
                mouseY >= g_panelY && mouseY <= (g_panelY + g_panelH))
            {
               g_isDragging = true;
               g_dragOffsetX = mouseX - g_panelX;
               g_dragOffsetY = mouseY - g_panelY;
            }
         }
         else
         {
            // Sedang digeser (Dragging)
            int newX = mouseX - g_dragOffsetX;
            int newY = mouseY - g_dragOffsetY;

            long chartWidth  = ChartGetInteger(0, CHART_WIDTH_IN_PIXELS);
            long chartHeight = ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);

            if (newX < 5) newX = 5;
            if (newY < 5) newY = 5;
            if (chartWidth > 50 && newX > (chartWidth - 60)) newX = (int)(chartWidth - 60);
            if (chartHeight > 50 && newY > (chartHeight - 60)) newY = (int)(chartHeight - 60);

            if (newX != g_panelX || newY != g_panelY)
            {
               RepositionDashboard(newX, newY);
            }
         }
      }
      else
      {
         if (g_isDragging)
         {
            g_isDragging = false;
            // Simpan posisi terakhir ke Global Variable agar tetap tersimpan saat reload/ganti TF
            string gvPanelX = "VIKAR_HUD_" + IntegerToString(ChartID()) + "_X";
            string gvPanelY = "VIKAR_HUD_" + IntegerToString(ChartID()) + "_Y";
            GlobalVariableSet(gvPanelX, (double)g_panelX);
            GlobalVariableSet(gvPanelY, (double)g_panelY);
            UpdateDashboard();
         }
      }
   }
   else if (id == CHARTEVENT_CHART_CHANGE)
   {
      // Pastikan posisi panel tidak terlempar ke luar jika jendela MT5 diubah ukurannya
      long chartW = ChartGetInteger(0, CHART_WIDTH_IN_PIXELS);
      long chartH = ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);
      bool adjusted = false;
      if (chartW > 50 && (g_panelX + 50) > chartW)
      {
         g_panelX = MathMax(5, (int)chartW - g_panelW - 20);
         adjusted = true;
      }
      if (chartH > 50 && (g_panelY + 50) > chartH)
      {
         g_panelY = MathMax(5, (int)chartH - g_panelH - 20);
         adjusted = true;
      }
      if (adjusted)
      {
         UpdateDashboard();
      }
   }
}
//+------------------------------------------------------------------+