//+------------------------------------------------------------------+
//|                               VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5|
//|        Copyright 2026, Vikar Institutional 4-Pillar Strategy     |
//|               SMC Core • S/R Pivots • Triple EMA • Fibonacci      |
//+------------------------------------------------------------------+
#property copyright "Vikar Institutional 4-Pillar Trading Strategy"
#property link      "https://www.tradingview.com"
#property version   "3.00"
#property description "Vikar EA 4-Pillar Pro - Apex Grandmaster Edition v3.00"
#property description "SMC Core, Smart Multi-Filter Suite & Self-Healing Matrix"
#property description "Prop Firm Guardian, Dynamic Structural Trailing & Trap Hunter"

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
   TP_TYPE_RISK_REWARD,   // Rasio Risk-to-Reward (1 : 1.5 / 1 : 2 / 1 : 3)
   TP_TYPE_FIBO_EXT,      // Target Ekstensi Fibonacci (-0.272 & -0.618)
   TP_TYPE_PIVOT_LEVEL    // Target Level Pivot Statis Terdekat (R1/R2 atau S1/S2)
};

enum ENUM_BE_MODE
{
   BE_MODE_PIPS,          // Berdasarkan Jarak Pips Profit (e.g. Profit +15 Pips -> Geser SL ke +5 Pips)
   BE_MODE_RISK_REWARD    // Berdasarkan Rasio Risk-Reward (e.g. Profit 1:1 -> Geser SL ke +5 Pips)
};

//+------------------------------------------------------------------+
//| INPUT PARAMETERS USER                                            |
//+------------------------------------------------------------------+
input group "=== 1. MANAJEMEN LOT & RISIKO MODAL ==="
input ENUM_LOT_TYPE InpLotType            = LOT_TYPE_BROKER_MIN;   // Model Lot (Default: Minimal Lot Broker - Aman)
input double        InpRiskPercent        = 1.0;                   // Risiko per Transaksi (% Modal, Jika Mode Risk %)
input double        InpFixedLot           = 0.10;                  // Ukuran Lot Tetap (Jika Mode Fixed Lot)
input double        InpMinLot             = 0.00;                  // Batas Bawah Lot (0.0 = Auto Deteksi Minimal Broker)
input double        InpMaxLot             = 0.10;                  // Batas Maksimal Lot (Safeguard: 0.10 Anti-Lot Besar)
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
input ENUM_TP_TYPE  InpTPType             = TP_TYPE_RISK_REWARD;   // Metode Penentuan Target Take Profit
input double        InpRiskRewardRatio    = 2.0;                   // Rasio Risk to Reward (1 : X)

// --- Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin) ---
input bool          InpUseBreakeven       = true;                  // Aktifkan Auto-Breakeven / SL+ (Kunci Modal & Profit)
input ENUM_BE_MODE  InpBreakevenMode      = BE_MODE_PIPS;          // Model Pemicu Auto-BE / SL+ (Pips / Risk-Reward)
input double        InpBreakevenTriggerPips= 15.0;                 // Jarak Profit Memicu BE / SL+ (Pips, Mode Pips)
input double        InpBreakevenRRTrigger = 1.0;                   // Pemicu BE Saat Profit Mencapai R:R (1.0 = 1:1, Mode RR)
input double        InpBreakevenLockPips  = 5.0;                   // Pips Keuntungan Terkunci Saat SL+ (SL Geser ke Profit)
input bool          InpUseTrailingEMA21   = true;                  // Trailing Stop Dinamis Mengikuti EMA 21 Magenta
input double        InpTrailingBufferPips = 5.0;                   // Jarak Buffer Trailing dari EMA 21 (Pips)

// --- Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner) ---
input bool          InpUsePartialClose    = true;                  // Aktifkan Partial Take Profit (Amankan 50% di TP1)
input double        InpPartialClosePercent= 50.0;                  // Persentase Lot Ditutup di TP1 (Default: 50%)
input ENUM_BE_MODE  InpPartialTriggerMode = BE_MODE_PIPS;          // Model Pemicu TP1 (Pips / Risk-Reward)
input double        InpPartialTriggerPips = 18.0;                 // Jarak Profit Pemicu TP1 (Pips, Mode Pips)
input double        InpPartialRRTrigger   = 1.5;                   // Pemicu TP1 Saat Mencapai R:R (1.5 = 1:1.5, Mode RR)
input bool          InpPartialMoveSLPlus  = true;                  // Otomatis Geser Sisa Lot ke SL+ Setelah TP1 Ambil Untung

input group "=== 2.6 DYNAMIC STRUCTURAL SWING TRAILING (v3.00) ==="
input bool          InpUseStructuralTrailing       = true;         // Trailing Stop Struktur Ayunan SMC (HL/LH) untuk Runner
input double        InpStructuralTrailingAtrBuffer = 0.5;          // Buffer Jarak dari Swing HL/LH (x ATR)

// --- Auto Cut Profit Saat Indikasi Pembalikan Arah ---
input bool          InpAutoCutProfit      = true;                  // Auto Cut Profit Saat Ada Indikasi Pembalikan Arah
input double        InpMinProfitToCutPips = 5.0;                   // Batas Minimal Floating Profit (Pips) Sebelum Cut Aktif
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
input bool          InpRequireDiscount    = true;                  // Filter Dealing Range (BUY di Diskon, SELL di Premium)
input bool          InpUseLiquiditySweep  = true;                  // Deteksi & Prioritas Liquidity Sweep (Stop Hunt)
input bool          InpUseFVGFilter       = true;                  // Deteksi Fair Value Gap (FVG Imbalance)
input bool          InpUseOrderBlock      = true;                  // Aktifkan Mesin Valid Order Block (OB) Institusional
input double        InpOBDisplacementAtrMult = 1.25;               // Multiplier Displacement ATR Lilin Pemicu OB (Min: 1.25x)
input bool          InpRequireOBMitigation= false;                 // Wajib Lilin Sedang Menguji Zona OB (Mitigation Test)
input int           InpOBMaxAgeBars       = 35;                    // Batas Usia Lilin Maksimal Order Block Aktif (Bars)
input int           InpFVGLookbackBars    = 20;                    // Jendela Pemindaian Multi-Bar Fair Value Gap (FVG)
input int           InpMinFVGPoints       = 15;                    // Batas Minimal Celah Lebar FVG (Points)

input group "=== 3.1 SISTEM SKOR KONFLUENSI 4 PILAR (GRADE FILTER) ==="
input bool          InpUseConfluenceScore = true;                  // Aktifkan Sistem Skor Konfluensi 4 Pilar (0 - 100 Poin)
input double        InpMinConfluenceScore = 65.0;                  // Skor Minimal Eksekusi (65 = Grade A, 80 = Grade A+ Sniper)

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
input double        InpMaxSpreadPips      = 10.0;                  // Batas Maksimal Spread Diizinkan (Pips - Aman Malam Hari)
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
input group "=== 8.5 DYNAMIC PATTERN PERFORMANCE MATRIX (AI LEARNING v2.50) ==="
input bool          InpUsePatternMatrix        = true;         // Aktifkan Memori Rapor & Bobot Kinerja Pola
input int           InpMinTradesForPatternEval = 3;            // Minimal Transaksi Sebelum Evaluasi Pola
input double        InpPatternBlacklistWinrate = 40.0;         // Ambang Batas Blacklist Pola (Winrate < 40%)
input double        InpPatternBoostWinrate     = 70.0;         // Ambang Batas Boost Pola (Winrate > 70%)
input double        InpPatternBoostScore       = 10.0;         // Bonus Skor Konfluensi untuk Pola Akurat
input double        InpPatternPenaltyScore     = 15.0;         // Penalti Pengetatan Skor untuk Pola Lemah

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
input int           InpDashboardY         = 20;                    // Posisi Awal Dashboard Y (Pixel dari Atas)
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

int            h_ema8       = INVALID_HANDLE;
int            h_ema21      = INVALID_HANDLE;
int            h_ema125     = INVALID_HANDLE;
int            h_atr14      = INVALID_HANDLE;
int            h_htf_ema125 = INVALID_HANDLE;
int            h_htf_ema8   = INVALID_HANDLE;
int            h_htf_ema21  = INVALID_HANDLE;
string         g_htfMacroStr = "H1 MACRO READY";

datetime       lastBarTime      = 0;
datetime       lastOrderBarTime = 0;

datetime       g_eaStartTime      = 0;
double         g_eaInitialBalance = 0.0;
string         g_gvStartTimeKey   = "";
string         g_gvStartBalKey    = "";

// Koordinat & State Drag & Drop Dashboard
int            g_panelX           = 15;
int            g_panelY           = 20;
int            g_panelW           = 355;
int            g_panelH           = 400;
bool           g_isDragging       = false;
int            g_dragOffsetX      = 0;
int            g_dragOffsetY      = 0;

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
};
LossAutopsyReport g_autopsy;
//+------------------------------------------------------------------+
//| STRUKTUR & MEMORI DINAMIS: PATTERN PERFORMANCE MATRIX (v2.50)   |
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

#define TOTAL_TRACKED_PATTERNS 12
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
//| ON INIT                                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(InpDeviation);
   trade.SetTypeFillingBySymbol(_Symbol);

   h_ema8    = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema21   = iMA(_Symbol, _Period, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_ema125  = iMA(_Symbol, _Period, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE);
   h_atr14   = iATR(_Symbol, _Period, 14);
   h_rsi_div = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);
   h_adx14   = iADX(_Symbol, _Period, InpADXPeriod);

   if (h_ema8 == INVALID_HANDLE || h_ema21 == INVALID_HANDLE ||
       h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE ||
       h_rsi_div == INVALID_HANDLE || h_adx14 == INVALID_HANDLE)
   {
      Print("[ERROR] Gagal menginisialisasi handle indikator MQL5!");
      return INIT_FAILED;
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

   Print("=== VIKAR EA 4-PILLAR PRO INITIALIZED SUCCESSFULLY ===");
   Print("Aset: ", _Symbol, " | Timeframe: ", EnumToString(_Period), " | Magic: ", InpMagicNumber);
   Print("Start Time: ", TimeToString(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Balance: $", g_eaInitialBalance);

   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| ON DEINIT                                                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if (h_ema8 != INVALID_HANDLE)       IndicatorRelease(h_ema8);
   if (h_ema21 != INVALID_HANDLE)      IndicatorRelease(h_ema21);
   if (h_ema125 != INVALID_HANDLE)     IndicatorRelease(h_ema125);
   if (h_atr14 != INVALID_HANDLE)      IndicatorRelease(h_atr14);
   if (h_htf_ema125 != INVALID_HANDLE) IndicatorRelease(h_htf_ema125);
   if (h_htf_ema8 != INVALID_HANDLE)   IndicatorRelease(h_htf_ema8);
   if (h_htf_ema21 != INVALID_HANDLE)  IndicatorRelease(h_htf_ema21);
   if (h_rsi_div != INVALID_HANDLE)    IndicatorRelease(h_rsi_div);
   if (h_adx14 != INVALID_HANDLE)      IndicatorRelease(h_adx14);

   ChartSetInteger(0, CHART_EVENT_MOUSE_MOVE, false);
   DestroyDashboardGUI();
   CleanSMCObjects();
   Comment("");
}

//+------------------------------------------------------------------+
//| MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE v2.40)|
//+------------------------------------------------------------------+
void PerformLossAutopsyMQL5(ulong ticket, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil data pola candlestick dari memori Global Variable
   string patGvKey = "VIKAR_PAT_" + IntegerToString((long)ticket);
   ENUM_CANDLE_PATTERN pat = PATTERN_NONE;
   if (GlobalVariableCheck(patGvKey))
   {
      pat = (ENUM_CANDLE_PATTERN)(int)GlobalVariableGet(patGvKey);
      GlobalVariableDel(patGvKey);
   }
   g_autopsy.failedPattern = pat;

   string patName = "Pola Setup Standard";
   if (pat == PATTERN_HAMMER_PINBAR) patName = "Pin Bar / Hammer";
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
   if (pat != PATTERN_NONE)
      g_autopsy.quarantineUntilBar = currentBarTime + (InpQuarantinePatternBars * PeriodSeconds(_Period));
   else
      g_autopsy.quarantineUntilBar = 0;

   // 2. Diagnosa Anatomi Penyebab Loss
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

   string reason = "PENGUJIAN LEVEL GAGAL (LOW CONFLUENCE)";
   if (lastBarRange >= (2.2 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPIKE)";
   else if (g_smcAnalysis.hasCHoCH || (ArraySize(rates) > 1 && currentEma125 > 0 && ((rates[1].close < currentEma125 && rates[1].open > currentEma125) || (rates[1].close > currentEma125 && rates[1].open < currentEma125))))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU WICK)";

   g_autopsy.lossReason = reason;

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT5] Posisi Deal #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
   Print("DIAGNOSA PENYEBAB : ", g_autopsy.lossReason);
   Print("KOREKSI 1 (SKOR)  : Ambang Konfluensi dinaikkan +", DoubleToString(g_autopsy.scorePenalty, 0), " Poin (Hanya Setup Grade A+)");
   if (pat != PATTERN_NONE)
      Print("KOREKSI 2 (POLA)  : Pola ", patName, " dikarantina selama ", InpQuarantinePatternBars, " Bar lilin.");
   Print("KOREKSI 3 (BUFFER): Stop Loss diperlebar +", DoubleToString(InpAdaptiveSLBufferBoost, 2), "x ATR untuk ", InpAdaptiveBufferTrades, " trade berikutnya.");
   Print("==================================================================");

   if (InpAutopsyNotifyPush)
   {
      string notif = "OTOPSI PASCA-SL #" + IntegerToString((long)ticket) + " (" + DoubleToString(lossAmount, 2) + ")\n" +
                     "Diagnosa: " + reason + "\n" +
                     "Koreksi Diri: Ambang Skor dinaikkan +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      SendPushAlert(notif);
   }
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
//| INISIALISASI & PEMULIHAN MEMORI PATTERN PERFORMANCE MATRIX MQL5  |
//+------------------------------------------------------------------+
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
      "Momentum BOS Breakout"
   };

   int blacklistedCount = 0;
   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      g_patternMatrix[i].patternId = i;
      g_patternMatrix[i].name      = patNames[i];

      string gvWKey = "VIKAR_MT5_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);
      string gvLKey = "VIKAR_MT5_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);

      int wins   = GlobalVariableCheck(gvWKey) ? (int)GlobalVariableGet(gvWKey) : 0;
      int losses = GlobalVariableCheck(gvLKey) ? (int)GlobalVariableGet(gvLKey) : 0;
      int total  = wins + losses;
      double wr  = (total > 0) ? ((double)wins * 100.0 / (double)total) : 0.0;

      g_patternMatrix[i].wins          = wins;
      g_patternMatrix[i].losses        = losses;
      g_patternMatrix[i].total         = total;
      g_patternMatrix[i].winRate       = wr;
      g_patternMatrix[i].isBlacklisted = false;
      g_patternMatrix[i].scoreModifier = 0.0;

      if (InpUsePatternMatrix && total >= InpMinTradesForPatternEval)
      {
         if (wr < InpPatternBlacklistWinrate)
         {
            g_patternMatrix[i].isBlacklisted = true;
            g_patternMatrix[i].scoreModifier = -InpPatternPenaltyScore;
            blacklistedCount++;
         }
         else if (wr >= InpPatternBoostWinrate)
         {
            g_patternMatrix[i].isBlacklisted = false;
            g_patternMatrix[i].scoreModifier = InpPatternBoostScore;
         }
      }

      if (total >= 2 && wr > highestWR)
      {
         highestWR = wr;
         bestName  = patNames[i] + " (" + DoubleToString(wr, 0) + "%)";
      }
   }

   g_bestPatternStr = bestName;
   Print("[AI PATTERN MATRIX MT5] Diinisialisasi. Pola Aktif: ", TOTAL_TRACKED_PATTERNS, " | Ter-blacklist: ", blacklistedCount, " | Terbaik: ", g_bestPatternStr);
}

//+------------------------------------------------------------------+
//| PEMBARUAN REKOR SETIAP KALI DEAL TERTUTUP MQL5                   |
//+------------------------------------------------------------------+
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
         Print("[AI MATRIX WARNING MT5] Pola '", g_patternMatrix[patternId].name, "' di-BLACKLIST sementara (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% < ", InpPatternBlacklistWinrate, "%).");
      }
      else if (g_patternMatrix[patternId].winRate >= InpPatternBoostWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = InpPatternBoostScore;
         Print("[AI MATRIX BOOST MT5] Pola '", g_patternMatrix[patternId].name, "' mendapatkan BOOST +", InpPatternBoostScore, " Poin (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% >= ", InpPatternBoostWinrate, "%).");
      }
      else
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = 0.0;
      }
   }

   // Cari pola dengan performa terbaik
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
}

void ResetSelfHealingStateMQL5(string triggerReason)
{
   if (!g_autopsy.isActive) return;
   g_autopsy.isActive              = false;
   g_autopsy.scorePenalty          = 0.0;
   g_autopsy.tradesWithExtraBuffer = 0;
   g_autopsy.quarantineUntilBar    = 0;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   Print("[SELF-HEALING NORMALIZED MT5] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
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
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|
//+------------------------------------------------------------------+
bool CheckCircuitBreakers()
{
   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit && !InpUseEquityGuardian)
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
      if (profit < -0.01) // True Loss (Kerugian riil pada modal)
      {
         consecutiveLosses++;
         lastLossTime = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
         if (InpUseSelfHealing && g_autopsy.failedTicket != ticket)
            PerformLossAutopsyMQL5(ticket, lastLossTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER KERUGIAN! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingStateMQL5("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }

      // Pembaruan Statistik Pattern Performance Matrix MT5 (v2.50)
      string procKey = "VIKAR_MT5_PMR_PROC_" + IntegerToString((long)ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patGvKey = "VIKAR_PAT_" + IntegerToString((long)ticket);
         int patId = GlobalVariableCheck(patGvKey) ? (int)GlobalVariableGet(patGvKey) : 0;
         if (profit > 0.01)
            UpdatePatternRecordMQL5(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecordMQL5(patId, false);
         GlobalVariableSet(procKey, 1.0);
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

void OnTick()
{
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

   // 8. Periksa Batas Maksimal Posisi Aktif untuk Entry Baru
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
   if (lastOrderBarTime != 0 && (iTime(_Symbol, _Period, 0) - lastOrderBarTime) < (InpSignalCooldownBars * PeriodSeconds(_Period)))
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

         // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         if (scoreRes.totalScore < effectiveMinScoreBUY)
         {
            if (InpUseSelfHealing && g_autopsy.isActive)
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

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isMomentumBreakout && isHeadroomOk) ||
                              (isBullishSweepTrap && isHeadroomOk);

         if (canExecuteBuy)
         {
            double slPrice = 0.0;
            double tpPrice = 0.0;

            // Hitung Stop Loss
            if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingLow.price > 0)
               slPrice = lastSwingLow.price - (InpSLBufferAtrMult * currentAtr);
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
            if (InpTPType == TP_TYPE_RISK_REWARD)
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

            if (trade.Buy(lots, _Symbol, ask, slPrice, tpPrice, tradeCmt))
            {
               ulong buyTicket = trade.ResultOrder();
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)buyTicket), (double)(isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)));

               lastOrderBarTime = iTime(_Symbol, _Period, 0);
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = "BUY EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
               Print("[BUY EXECUTION] Lot: ", lots, " | Price: ", ask, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert("BUY " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(ask, _Digits) +
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

      // Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
      double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
      if (InpUseSelfHealing && g_autopsy.isActive && rates[0].time < g_autopsy.quarantineUntilBar &&
          g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
      {
         int remainBars = (int)((g_autopsy.quarantineUntilBar - rates[0].time) / PeriodSeconds(_Period));
         g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
         return;
      }

      if (scoreRes.totalScore < effectiveMinScoreSELL)
      {
         if (InpUseSelfHealing && g_autopsy.isActive)
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

      bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                            (isMomentumBreakout && isHeadroomOk) ||
                            (isBearishSweepTrap && isHeadroomOk);

      if (canExecuteSell)
      {
         double slPrice = 0.0;
         double tpPrice = 0.0;

         // Hitung Stop Loss
         if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingHigh.price > 0)
            slPrice = lastSwingHigh.price + (InpSLBufferAtrMult * currentAtr);
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
         if (InpTPType == TP_TYPE_RISK_REWARD)
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

         if (trade.Sell(lots, _Symbol, bid, slPrice, tpPrice, tradeCmt))
         {
            ulong sellTicket = trade.ResultOrder();
            if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
               g_autopsy.tradesWithExtraBuffer--;
            GlobalVariableSet("VIKAR_PAT_" + IntegerToString((long)sellTicket), (double)(isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern)));

            lastOrderBarTime = iTime(_Symbol, _Period, 0);
            string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
            g_lastSignalType = "SELL EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
            Print("[SELL EXECUTION] Lot: ", lots, " | Price: ", bid, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr, " | Structure: ", g_smcAnalysis.structureName);
            if (InpNotifyOnEntry)
            {
               SendPushAlert("SELL " + DoubleToString(lots, 2) + " " + _Symbol + " @ " + DoubleToString(bid, _Digits) +
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
   if (!InpUseBreakeven && !InpUseTrailingEMA21 && !InpUsePartialClose && !InpUseTimeBasedExit && !InpAutoLockBEBeforeNews)
      return;

   // Bersihkan global variable tracking partial close jika tidak ada posisi aktif
   if (PositionsTotal() == 0)
   {
      int totalGV = GlobalVariablesTotal();
      for (int g = totalGV - 1; g >= 0; g--)
      {
         string gvName = GlobalVariableName(g);
         if (StringFind(gvName, "VIKAR_PARTIAL_") == 0)
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
void UpdateDashboard()
{
   if (!InpShowDashboard)
   {
      DestroyDashboardGUI();
      return;
   }

   Comment(""); // Bersihkan teks Comment biasa agar tidak bertumpuk di atas lilin

   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
   double spread  = PriceToPips(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));

   int openCount = 0;
   double openFloating = GetOpenFloatingPnL(openCount);

   // Hitung Statistik Sejak Start, Harian, dan Mingguan
   datetime startOfDay  = iTime(_Symbol, PERIOD_D1, 0);
   if (startOfDay == 0) startOfDay = TimeCurrent() - 86400;

   datetime startOfWeek = iTime(_Symbol, PERIOD_W1, 0);
   if (startOfWeek == 0) startOfWeek = TimeCurrent() - (7 * 86400);

   TradeStats statsTotal = CalculateHistoryStats(g_eaStartTime);
   TradeStats statsDaily = CalculateHistoryStats(startOfDay);
   TradeStats statsWeekly= CalculateHistoryStats(startOfWeek);

   double totalGrowthPct = (g_eaInitialBalance > 0) ? ((balance - g_eaInitialBalance) / g_eaInitialBalance * 100.0) : 0.0;

   int panelX = g_panelX;
   int panelY = g_panelY;
   int panelW = g_panelW;
   int panelH = InpShowPnLStats ? 630 : 550;
   g_panelH = panelH;

   // 1. Container Utama (Dark Slate Card)
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, panelH, C'15,23,42', C'51,65,85');

   // 2. Header Banner (Cyan Gradient Accent)
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 34, C'3,105,161', C'56,189,248');
   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 12, panelY + 4, "VIKAR 4-PILLAR PRO", clrWhite, 10, "Segoe UI Bold");
   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 12, panelY + 19, _Symbol + " [" + EnumToString(_Period) + "] | " + lotDisplay + " | ID: " + IntegerToString(InpMagicNumber), C'224,242,254', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_HDR_DRAG", panelX + panelW - 74, panelY + 9, "[ ⠿ GESER ]", C'186,230,253', 8, "Segoe UI Bold");

   // 3. Ringkasan Saldo Akun
   CreateOrUpdateText("VIKAR_HUD_BAL_START", panelX + 12, panelY + 42, "Start Modal: $" + DoubleToString(g_eaInitialBalance, 2) + "  (Aktivasi: " + TimeToString(g_eaStartTime, TIME_MINUTES) + ")", C'148,163,184', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_BAL_CURR", panelX + 12, panelY + 56, "Saldo: $" + DoubleToString(balance, 2) + "  |  Equity: $" + DoubleToString(equity, 2), clrWhite, 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_FLOAT", panelX + 12, panelY + 72, "Floating: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Posisi)  |  Spread: " + DoubleToString(spread, 1) + " pips", floatClr, 8, "Segoe UI Bold");

   int currY = panelY + 92;

   // 4. Inset Card: Rekap Profit & Loss (Harian, Mingguan, Total)
   if (InpShowPnLStats)
   {
      CreateOrUpdateRect("VIKAR_HUD_PNL_BG", panelX + 8, currY, panelW - 16, 78, C'30,41,59', C'71,85,105');
      CreateOrUpdateText("VIKAR_HUD_PNL_TITLE", panelX + 15, currY + 4, "📊 REKAP PROFIT & LOSS REAL-TIME:", C'251,191,36', 8, "Segoe UI Bold");

      color pnlTotalClr = (statsTotal.netProfit > 0) ? C'74,222,128' : (statsTotal.netProfit < 0 ? C'248,113,113' : clrWhite);
      double totalWinratePct = (statsTotal.totalTrades > 0) ? ((double)statsTotal.winTrades / statsTotal.totalTrades * 100.0) : 0.0;
      string winrateStr = (statsTotal.totalTrades > 0) ? (" | WR: " + DoubleToString(totalWinratePct, 1) + "%") : "";
      CreateOrUpdateText("VIKAR_HUD_PNL_TOTAL", panelX + 15, currY + 20, "• Sejak Start : " + FormatPnL(statsTotal.netProfit) + " (" + (totalGrowthPct >= 0 ? "+" : "") + DoubleToString(totalGrowthPct, 1) + "%) | " + IntegerToString(statsTotal.winTrades) + "W/" + IntegerToString(statsTotal.lossTrades) + "L" + winrateStr, pnlTotalClr, 8, "Segoe UI Bold");

      double dailyWinratePct = (statsDaily.totalTrades > 0) ? ((double)statsDaily.winTrades / statsDaily.totalTrades * 100.0) : 0.0;
      string dailyWRStr = (statsDaily.totalTrades > 0) ? (" (" + IntegerToString(statsDaily.winTrades) + "W/" + IntegerToString(statsDaily.lossTrades) + "L - " + DoubleToString(dailyWinratePct, 0) + "%)") : "";
      CreateOrUpdateText("VIKAR_HUD_PNL_DAY", panelX + 15, currY + 38, "• Hari Ini    : Net " + FormatPnL(statsDaily.netProfit) + dailyWRStr + " (+$" + DoubleToString(statsDaily.grossProfit, 2) + " / -$" + DoubleToString(statsDaily.grossLoss, 2) + ")", C'226,232,240', 7, "Segoe UI");
      CreateOrUpdateText("VIKAR_HUD_PNL_WEEK", panelX + 15, currY + 54, "• Minggu Ini  : Net " + FormatPnL(statsWeekly.netProfit) + " (Profit: +$" + DoubleToString(statsWeekly.grossProfit, 2) + " | Loss: -$" + DoubleToString(statsWeekly.grossLoss, 2) + ")", C'226,232,240', 7, "Segoe UI");
      currY += 86;
   }

   // 5. Status 4 Pilar Multi-Confluence Cerdas & Skor Institusional
   string scoreStr = "Ready";
   if (g_lastScoreResult.totalScore > 0)
      scoreStr = DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")";
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 65.0) ? C'251,191,36' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_SCORE", panelX + 12, currY, "[Confluence]  : " + scoreStr, scoreClr, 7, "Segoe UI Bold");
   currY += 14;

   string obStr = "OB: Scanning";
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
      obStr = "Bull OB: " + DoubleToString(g_bullishOB.bottom, 1) + "-" + DoubleToString(g_bullishOB.top, 1) + " (Disp: " + DoubleToString(g_bullishOB.displacementAtr, 1) + "x)";
   else if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
      obStr = "Bear OB: " + DoubleToString(g_bearishOB.bottom, 1) + "-" + DoubleToString(g_bearishOB.top, 1) + " (Disp: " + DoubleToString(g_bearishOB.displacementAtr, 1) + "x)";
   else if (g_activeFVG.isValid)
      obStr = "FVG: " + DoubleToString(g_activeFVG.bottom, 1) + "-" + DoubleToString(g_activeFVG.top, 1);
   CreateOrUpdateText("VIKAR_HUD_OB_FVG", panelX + 12, currY, "[Order Block] : " + obStr, C'244,114,182', 7, "Segoe UI");
   currY += 14;

   string smcStr = g_smcAnalysis.structureName;
   if (g_smcAnalysis.hasSweep) smcStr += " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr += " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_PILAR1", panelX + 12, currY, "[SMC Struktur]: " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   string htfText = InpUseHTFFilter ? g_htfMacroStr : "FILTER OFF";
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", panelX + 12, currY + 14, "[Macro " + EnumToString(InpHTFTimeframe) + "]  : " + htfText, htfClr, 7, "Segoe UI Bold");

   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   if (currentFibo.isValid) rangeStr += " | GP: " + DoubleToString(currentFibo.level618, 2);
   CreateOrUpdateText("VIKAR_HUD_PILAR2", panelX + 12, currY + 28, "[Dealing Range]: " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   string patStr = g_chartPattern.isValid ? (g_chartPattern.patternName + " [" + DoubleToString(g_chartPattern.score, 0) + "p]") : "Scanning Geometri...";
   color patClr = g_chartPattern.isValid ? (g_chartPattern.isBullish ? C'74,222,128' : C'248,113,113') : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_CHART_PAT", panelX + 12, currY + 42, "[Pola Chart]  : " + patStr, patClr, 7, "Segoe UI Bold");

   string candleStr = g_candleAnalysis.patternName;
   if (g_candleAnalysis.score > 0) candleStr += " [Skor: " + DoubleToString(g_candleAnalysis.score, 0) + "/100]";
   color candleClr = g_candleAnalysis.isHighQuality ? C'251,191,36' : C'203,213,225';
   CreateOrUpdateText("VIKAR_HUD_PILAR3", panelX + 12, currY + 56, "[Pola Lilin]  : " + candleStr, candleClr, 7, "Segoe UI");

   double ema125Val[];
   ArraySetAsSeries(ema125Val, true);
   string emaTrendStr = "EMA Baseline Ready";
   if (CopyBuffer(h_ema125, 0, 0, 2, ema125Val) >= 2)
   {
      double closePrice = iClose(_Symbol, _Period, 1);
      emaTrendStr = (closePrice > ema125Val[1]) ? "BULLISH (Di Atas 125)" : "BEARISH (Di Bawah 125)";
   }
   CreateOrUpdateText("VIKAR_HUD_PILAR4", panelX + 12, currY + 70, "[Triple EMA]  : " + emaTrendStr + " | Ribbon 8/21", C'232,121,249', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_PILAR5", panelX + 12, currY + 84, "[S/R Pivot]   : P: " + DoubleToString(currentPivot.P, 2) + " [R1: " + DoubleToString(currentPivot.R1, 2) + " | S1: " + DoubleToString(currentPivot.S1, 2) + "]", C'148,163,184', 7, "Segoe UI");

   // Baris VSA Footprint
   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Volume") : "VSA: OFF";
   color vsaClr = (StringFind(vsaDisplay, "CLIMAX") >= 0) ? C'74,222,128' : ((StringFind(vsaDisplay, "NO-SUPPLY") >= 0) ? C'56,189,248' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_VSA", panelX + 12, currY + 98, "[VSA Footprint]: " + vsaDisplay, vsaClr, 7, "Segoe UI Bold");

   // Baris Circuit Guard & Consecutive Loss Counter
   string cbDisplay = "Normal (0/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss)";
   color cbClr = C'74,222,128';
   if (g_cooldownUntilTime > TimeCurrent())
   {
      int remMins = (int)((g_cooldownUntilTime - TimeCurrent()) / 60);
      cbDisplay = "COOLDOWN (" + IntegerToString(remMins) + " Mnt Sisa)";
      cbClr = C'248,113,113';
   }
   else if (g_dailyLossLimitHit)
   {
      cbDisplay = "DAILY LOCK REACHED";
      cbClr = C'248,113,113';
   }
   else if (g_consecutiveLossCount > 0)
   {
      cbDisplay = IntegerToString(g_consecutiveLossCount) + "/" + IntegerToString(InpMaxConsecutiveLosses) + " Loss Berturut-turut";
      cbClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_CB", panelX + 12, currY + 112, "[Circuit Guard]: " + cbDisplay, cbClr, 7, "Segoe UI Bold");

   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Pts | " + g_autopsy.lossReason + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[Self-Healing]: " + healDisplay, healClr, 7, "Segoe UI Bold");

   // Baris Cuaca Pasar (Market Regime Choppiness)
   string regimeStr = "NORMAL (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
   color regimeClr  = C'74,222,128';
   if (g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
   {
      regimeStr = "CHOPPY / FAKEOUT RISK (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
      regimeClr = C'248,113,113';
   }
   else if (g_currentRegime == REGIME_STRONG_TREND)
   {
      regimeStr = "STRONG TREND (CI: " + DoubleToString(g_currentChoppiness, 1) + ")";
      regimeClr = C'56,189,248';
   }
   CreateOrUpdateText("VIKAR_HUD_REGIME", panelX + 12, currY + 138, "[Cuaca Pasar]: " + regimeStr, regimeClr, 7, "Segoe UI Bold");

   // Baris Rapor Pola Teruji (AI Pattern Matrix)
   string pmStr = InpUsePatternMatrix ? ("Terbaik: " + g_bestPatternStr) : "NONAKTIF";
   CreateOrUpdateText("VIKAR_HUD_PATMAT", panelX + 12, currY + 151, "[Rapor Pola]: " + pmStr, C'203,213,225', 7, "Segoe UI");

   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 164, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");

   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 177, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope: AKTIF", C'148,163,184', 7, "Segoe UI");

   // Baris Prop Firm Guardian & Trap Hunter (v3.00)
   string pfStr = InpUseEquityGuardian ? ("DD: " + DoubleToString(g_currentDailyDDPct, 1) + "% / Max " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%") : "OFF";
   color pfClr = (g_currentDailyDDPct >= InpMaxDailyEquityDDPct * 0.75) ? C'248,113,113' : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_PROPFIRM", panelX + 12, currY + 190, "[Prop Firm Guard]: " + pfStr + " | Trap Hunter: AKTIF", pfClr, 7, "Segoe UI Bold");
   currY += 212;

   // 6. Inset Live Execution Status
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", panelX + 8, currY, panelW - 16, 52, C'15,23,42', C'2,132,199');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", panelX + 15, currY + 4, "STATUS KECERDASAN PASAR:", C'56,189,248', 7, "Segoe UI Bold");
   string statusDisplay = g_lastSignalType;
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING SETUP";
   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 15, currY + 19, statusDisplay, clrWhite, 7, "Segoe UI Bold");
   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = InpUseTrailingEMA21 ? "Trail: ON" : "Trail: OFF";
   string partialStr = InpUsePartialClose ? ("Partial: " + DoubleToString(InpPartialClosePercent, 0) + "%") : "Partial: OFF";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 15, currY + 34, beStr + " | " + cutStr + " | " + trailStr + " | Lot: " + DoubleToString(currentLotSize, 2), C'148,163,184', 7, "Segoe UI");

   ChartRedraw(0);
}

//+------------------------------------------------------------------+
//| CHART EVENT (DRAG & DROP DASHBOARD PANEL SECARA INTERAKTIF)      |
//+------------------------------------------------------------------+
void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
{
   if (!InpShowDashboard) return;

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