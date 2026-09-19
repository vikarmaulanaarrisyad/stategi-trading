# -*- coding: utf-8 -*-
"""
Generator untuk membangun VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4 lengkap untuk MetaTrader 4 QuickPro.
"""

mql4_code = r'''//+------------------------------------------------------------------+
//|                          VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4|
//|        Copyright 2026, Vikar Institutional 4-Pillar Strategy     |
//|               SMC Core • S/R Pivots • Triple EMA • Fibonacci      |
//|                    (MetaTrader 4 - QuickPro Edition)             |
//+------------------------------------------------------------------+
#property copyright "Vikar Institutional 4-Pillar Trading Strategy"
#property link      "https://www.tradingview.com"
#property version   "2.30"
#property strict
#property description "Robot Trading MT4 Institusional 4 Pilar Terpadu (v2.3 QuickPro Edition)"
#property description "1. SMC Core & Momentum Breakout Engine (Anti-Ketinggalan Momentum)"
#property description "2. Order Block & Multi-Bar FVG Tracker with VSA Footprint Absorption"
#property description "3. Chart Pattern Engine & Advanced Candlestick Multi-Confluence"
#property description "4. Multi-Stage Structural Trailing Stop & Daily Circuit Breaker Guard"
#property description "5. QuickPro Auto-Detect Min Lot & Smartphone Push Notifications"

//+------------------------------------------------------------------+
//| ENUMERASI KONFIGURASI                                            |
//+------------------------------------------------------------------+
enum ENUM_LOT_TYPE
{
   LOT_TYPE_BROKER_MIN,   // Otomatis Minimal Lot Broker QuickPro (Paling Aman, Menyesuaikan Akun)
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

enum ENUM_HTF_BIAS
{
   HTF_BIAS_NEUTRAL,
   HTF_BIAS_BULLISH,
   HTF_BIAS_BEARISH
};

//+------------------------------------------------------------------+
//| INPUT PARAMETERS USER (KOMPATIBILITAS QUICKPRO MT4)              |
//+------------------------------------------------------------------+
//--- 1. MANAJEMEN LOT & RISIKO MODAL ---
extern string       sec1                   = "=== 1. MANAJEMEN LOT & RISIKO MODAL ===";
extern ENUM_LOT_TYPE InpLotType            = LOT_TYPE_BROKER_MIN;   // Model Lot (Default: Minimal Lot Broker QuickPro - Paling Aman)
extern double        InpRiskPercent        = 1.0;                   // Risiko per Transaksi (% Modal, Jika Mode Risk %)
extern double        InpFixedLot           = 0.01;                  // Ukuran Lot Tetap (Jika Mode Fixed Lot)
extern double        InpMinLot             = 0.00;                  // Batas Bawah Lot (0.0 = Auto Deteksi Minimal Broker QuickPro)
extern double        InpMaxLot             = 0.10;                  // Batas Maksimal Lot (Safeguard Anti-Lot Besar)
extern int           InpMaxOpenPositions   = 1;                     // Maksimal Posisi Aktif Bersamaan (1 = Anti-Hedging)
extern int           InpSignalCooldownBars = 2;                     // Jeda Minimal Lilin Antar Sinyal (Bars)
extern int           InpMagicNumber        = 777104;                // Magic Number Unik EA MT4
extern string        InpTradeComment       = "VIKAR-QP-MT4";        // Komentar Identitas Transaksi
extern int           InpDeviation          = 15;                    // Toleransi Slippage (Points)

//--- 2. TARGET STOP LOSS, TAKE PROFIT & EXIT STRATEGY ---
extern string       sec2                   = "=== 2. TARGET STOP LOSS, TAKE PROFIT & EXIT STRATEGY ===";
extern ENUM_SL_TYPE  InpSLType             = SL_TYPE_SWING_FIBO;    // Metode Penempatan Stop Loss
extern double        InpSLBufferAtrMult    = 1.0;                   // Buffer Pengaman SL (x Nilai ATR 14)
extern double        InpMinSLPips          = 15.0;                  // Batas Minimum Jarak SL (Pips)
extern double        InpMaxSLPips          = 28.0;                  // Batas Maksimal Jarak SL (Pips - Terbukti Optimal di Gold)
extern double        InpFixedSLPips        = 25.0;                  // Jarak SL Statis (Jika Mode Fixed Pips)
extern ENUM_TP_TYPE  InpTPType             = TP_TYPE_RISK_REWARD;   // Metode Penentuan Target Take Profit
extern double        InpRiskRewardRatio    = 1.5;                   // Rasio Risk to Reward (1 : X)

// --- Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin) ---
extern bool          InpUseBreakeven       = true;                  // Aktifkan Auto-Breakeven / SL+ (Kunci Modal & Profit)
extern ENUM_BE_MODE  InpBreakevenMode      = BE_MODE_PIPS;          // Model Pemicu Auto-BE / SL+ (Pips / Risk-Reward)
extern double        InpBreakevenTriggerPips= 8.0;                  // Jarak Profit Memicu BE / SL+ (Pips)
extern double        InpBreakevenRRTrigger = 1.0;                   // Pemicu BE Saat Profit Mencapai R:R (1.0 = 1:1)
extern double        InpBreakevenLockPips  = 2.5;                   // Pips Keuntungan Terkunci Saat SL+ (SL Geser ke Profit)
extern bool          InpUseTrailingEMA21   = true;                  // Trailing Stop Dinamis Mengikuti EMA 21 Magenta
extern double        InpTrailingBufferPips = 4.0;                   // Jarak Buffer Trailing dari EMA 21 (Pips)

// --- Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner) ---
extern bool          InpUsePartialClose    = true;                  // Aktifkan Partial Take Profit (Amankan 50% di TP1)
extern double        InpPartialClosePercent= 50.0;                  // Persentase Lot Ditutup di TP1 (Default: 50%)
extern ENUM_BE_MODE  InpPartialTriggerMode = BE_MODE_PIPS;          // Model Pemicu TP1 (Pips / Risk-Reward)
extern double        InpPartialTriggerPips = 10.0;                  // Jarak Profit Pemicu TP1 (Pips)
extern double        InpPartialRRTrigger   = 1.2;                   // Pemicu TP1 Saat Mencapai R:R
extern bool          InpPartialMoveSLPlus  = true;                  // Otomatis Geser Sisa Lot ke SL+ Setelah TP1 Ambil Untung

// --- Multi-Stage Structural Trailing Stop (SMC Swing High/Low Runner) ---
extern bool          InpUseStructuralTrailing       = true;         // Trailing Stop Struktur Ayunan SMC (HL/LH) untuk Runner
extern double        InpStructuralTrailingAtrBuffer = 0.5;          // Buffer Jarak dari Swing HL/LH (x ATR)

// --- Auto Cut Profit Saat Indikasi Pembalikan Arah ---
extern bool          InpAutoCutProfit      = true;                  // Auto Cut Profit Saat Ada Indikasi Pembalikan Arah
extern double        InpMinProfitToCutPips = 3.0;                   // Batas Minimal Floating Profit (Pips) Sebelum Cut Aktif
extern bool          InpCutOnCHoCH         = true;                  // Cut Profit Jika Terdeteksi CHoCH Berlawanan (SMC)
extern bool          InpCutOnCandleReversal= true;                  // Cut Profit Jika Muncul Candlestick Rejection Berlawanan
extern bool          InpCutOnEMACross      = true;                  // Cut Profit Jika Lilin Menembus Ribbon EMA 21 Berlawanan

//--- 3. PILAR 1: SMART MONEY CONCEPTS (SMC CORE) ---
extern string       sec3                   = "=== 3. PILAR 1: SMART MONEY CONCEPTS (SMC CORE) ===";
extern int           InpFractalPeriod      = 2;                     // Periode Deteksi Ayunan Fractal (Bars Kiri/Kanan)
extern bool          InpRequireBOSorCHoCH  = true;                  // Wajib Konfirmasi Struktur Pasar (BOS / CHoCH)
extern bool          InpRequireDiscount    = false;                 // Filter Dealing Range (false = Fleksibel Mengikuti Momentum)
extern bool          InpUseLiquiditySweep  = true;                  // Deteksi & Prioritas Liquidity Sweep (Stop Hunt)
extern bool          InpUseFVGFilter       = true;                  // Deteksi Fair Value Gap (FVG Imbalance)
extern bool          InpUseOrderBlock      = true;                  // Aktifkan Mesin Valid Order Block (OB) Institusional
extern double        InpOBDisplacementAtrMult = 1.15;               // Multiplier Displacement ATR Lilin Pemicu OB (Min: 1.15x)
extern bool          InpRequireOBMitigation= false;                 // Wajib Lilin Sedang Menguji Zona OB
extern int           InpOBMaxAgeBars       = 35;                    // Batas Usia Lilin Maksimal Order Block Aktif (Bars)
extern int           InpFVGLookbackBars    = 20;                    // Jendela Pemindaian Multi-Bar Fair Value Gap (FVG)
extern int           InpMinFVGPoints       = 10;                    // Batas Minimal Celah Lebar FVG (Points)

//--- 3.1 SISTEM SKOR KONFLUENSI 4 PILAR ---
extern string       sec31                  = "=== 3.1 SISTEM SKOR KONFLUENSI 4 PILAR ===";
extern bool          InpUseConfluenceScore = true;                  // Aktifkan Sistem Skor Konfluensi 4 Pilar (0 - 100 Poin)
extern double        InpMinConfluenceScore = 55.0;                  // Skor Minimal Eksekusi (55 = Fast Scalp, 75 = Sniper)

//--- 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ---
extern string       sec32                  = "=== 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ===";
extern bool          InpAllowMomentumBreakout = true;               // Aktifkan Eksekusi Momentum Breakout (Anti-Ketinggalan Reli)
extern double        InpBreakoutAtrMult       = 1.0;                // Minimal Ukuran Lilin Breakout (x Nilai ATR 14)
extern bool          InpBreakoutRequireVSA    = true;               // Wajib Didukung Lonjakan Volume VSA (>= 1.3x)
extern bool          InpBreakoutRequireBOS    = true;               // Wajib Menembus Swing High/Low (Konfirmasi BOS)

//--- 4. PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS) ---
extern string       sec4                   = "=== 4. PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS) ===";
extern bool          InpUseDailyPivots     = true;                  // Aktifkan Kalkulasi Daily Pivot Points
extern bool          InpRequireDoubleAlign = false;                 // Wajib Double Alignment (false = Fleksibel Mengikuti EMA Trend)
extern double        InpMinHeadroomATR     = 0.5;                   // Jarak Minimal ke Tembok Resisten/Support (x ATR)

//--- 5. PILAR 3: TRIPLE EMA & MULTI-TIMEFRAME (H1 MACRO) ---
extern string       sec5                   = "=== 5. PILAR 3: TRIPLE EMA & MULTI-TIMEFRAME (H1 MACRO) ===";
extern int           InpFastEMA            = 8;                     // Fast EMA Period (Cyan Momentum)
extern int           InpMediumEMA          = 21;                    // Medium EMA Period (Magenta Ribbon & Trailing)
extern int           InpTrendEMA           = 125;                   // Trend Institutional Baseline (Putih)
extern int           InpPullbackLookback   = 8;                     // Jendela Lilin Pengujian Pullback (Bars)
extern bool          InpFilterWhipsaw125   = false;                 // Filter Whipsaw Lilin Bolak-Balik EMA 125
extern bool          InpUseHTFFilter       = true;                  // Aktifkan Filter Macro Trend Higher Timeframe (H1)
extern int           InpHTFTimeframe       = PERIOD_H1;             // Timeframe Macro Trend (Default: H1 = 60)
extern int           InpHTFTrendEMA        = 125;                   // HTF Trend Baseline Period (Putih 125)
extern bool          InpHTFRequireRibbon   = true;                  // Wajib Konfirmasi HTF Ribbon (EMA 8 > EMA 21)

//--- 6. PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET ---
extern string       sec6                   = "=== 6. PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET ===";
extern bool          InpUseAutoFibo        = true;                  // Aktifkan Validasi Fibonacci Retracement
extern bool          InpRequireGoldenPocket= false;                 // Wajib Menguji Area Golden Pocket (false = Cukup Sentuh Ribbon EMA)
extern double        InpFiboGPMin          = 0.500;                 // Batas Atas Retracement Golden Pocket
extern double        InpFiboGPMid          = 0.618;                 // Rasio Emas Utama (Golden Ratio 61.8%)
extern double        InpFiboGPMax          = 0.786;                 // Batas Bawah Retracement Golden Pocket

//--- 7. POLA KONFIRMASI CANDLESTICK REJECTION ---
extern string       sec7                   = "=== 7. POLA KONFIRMASI CANDLESTICK REJECTION ===";
extern bool          InpRequireCandleRejection = true;              // Wajib Pola Rejection Cerdas (Pin Bar, Engulfing, Star, Tweezer)
extern double        InpMinCandleScore         = 55.0;              // Skor Kualitas Lilin Minimal (0 - 100)
extern bool          InpUseHammerPinBar        = true;              // Pin Bar & Hammer Rejection (Ekor Penolakan >= 55%)
extern bool          InpUseEngulfing           = true;              // Bullish & Bearish Engulfing Institusional
extern bool          InpUseMorningEveningStar  = true;              // Morning Star & Evening Star (3-Bar Reversal)
extern bool          InpUseTweezer             = true;              // Tweezer Tops & Tweezer Bottoms (Double Level Test)
extern bool          InpUseFVGRebound          = true;              // Fair Value Gap Mitigation Rebound
extern bool          InpUseThreeSoldiersCrows  = true;              // Three White Soldiers & Three Black Crows (Impulsive Push)
extern bool          InpUseHaramiInsideBar     = true;              // Harami & Inside Bar Compression Breakout
extern bool          InpUsePiercingDarkCloud   = true;              // Piercing Line & Dark Cloud Cover (>50% Penetration)
extern bool          InpUseDragonflyGravestone = true;              // Dragonfly Doji & Gravestone Doji Extreme Rejection
extern bool          InpUseInvertedHammerStar  = true;              // Inverted Hammer & Shooting Star Rejection

//--- 7.1 MESIN POLA GRAFIK (CHART PATTERN ENGINE) ---
extern string       sec71                  = "=== 7.1 MESIN POLA GRAFIK (CHART PATTERN ENGINE) ===";
extern bool          InpUseChartPatterns       = true;              // Aktifkan Mesin Pengenal Pola Grafik (Chart Patterns)
extern bool          InpUseDoubleTopBottom     = true;              // Deteksi Double Bottom (W) & Double Top (M-Pattern)
extern bool          InpUseQuasimodo           = true;              // Deteksi Quasimodo (QM Institutional Level)
extern bool          InpUseHeadAndShoulders    = true;              // Deteksi Head & Shoulders & Inverse H&S
extern bool          InpUseFlagsContinuation   = true;              // Deteksi Bullish / Bearish Flags (Slanted Channel)
extern double        InpMinChartPatternScore   = 65.0;              // Skor Minimal Pola Grafik (0 - 100)

//--- 8. FILTER PROTEKSI & WAKTU SESI PASAR ---
extern string       sec8                   = "=== 8. FILTER PROTEKSI & WAKTU SESI PASAR ===";
extern bool          InpUseShockGuard      = true;                  // Proteksi Lonjakan Volatilitas Berita (Shock Guard)
extern double        InpShockAtrMult       = 3.2;                   // Batas Abnormal Lonjakan Lilin Berita (x Nilai ATR)
extern int           InpShockCooldownBars  = 2;                     // Jeda Pengaman Lilin Pasca-Lonjakan Shock (Bars)
extern bool          InpCutOnEarlyInvalidation = true;              // Cut Dini Jika Terbentuk Lilin Menelan Order Block Acuan
extern double        InpMaxSpreadPips      = 4.5;                   // Batas Maksimal Spread Diizinkan (Pips)
extern bool          InpUseSessionFilter   = false;                 // Batasi Jam Trading (false = 24 Jam Auto Trade)
extern int           InpSessionStartHour   = 0;                     // Jam Mulai Trading
extern int           InpSessionEndHour     = 24;                    // Jam Selesai Trading

//--- 8.1 PROTEKSI AKUN & CIRCUIT BREAKER ---
extern string       sec81                  = "=== 8.1 PROTEKSI AKUN & CIRCUIT BREAKER ===";
extern bool          InpUseConsecutiveLossGuard = true;             // Jeda Anti-Overtrading Pasca-Loss Berturut-turut
extern int           InpMaxConsecutiveLosses    = 2;                // Batas Loss Berturut-turut Hari Ini (Default: 2)
extern int           InpCooldownHours           = 4;                // Durasi Istirahat Robot Pasca-Loss (Jam)
extern bool          InpUseDailyLossLimit       = true;             // Batasi Maksimal Kerugian Harian (% Modal)
extern double        InpMaxDailyLossPercent     = 2.5;              // Batas Maksimal Kerugian Harian (% Saldo Awal Hari Ini)

//--- 8.2 VOLUME SPREAD ANALYSIS (VSA INSTITUSIONAL) ---
extern string       sec82                  = "=== 8.2 VOLUME SPREAD ANALYSIS (VSA INSTITUSIONAL) ===";
extern bool          InpUseVSA                  = true;             // Aktifkan Analisis Volume Footprint Institusional
extern int           InpVSALookbackBars         = 20;               // Periode Rata-rata Volume Lilin Acuan (Bars)
extern double        InpVSAClimaxRatio          = 1.75;             // Batas Lonjakan Volume Climax / Absorption (x Rata-rata)
extern double        InpVSANoSupplyRatio        = 0.85;             // Batas Volume Kering / No-Supply Pullback (x Rata-rata)

//--- 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ---
extern string       sec83                  = "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ===";
extern bool          InpUseFridayGuard          = true;             // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
extern int           InpFridayCloseHour         = 21;               // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)

//--- 9. ON-CHART SMC VISUALIZER (AUTO-DRAW DI CHART) ---
extern string       sec9                   = "=== 9. ON-CHART SMC VISUALIZER (AUTO-DRAW DI CHART) ===";
extern bool          InpDrawSMCOnChart     = true;                  // Otomatis Gambar Kotak Order Block, FVG & Garis BOS di MT4
extern color         InpColorBullishOB     = C'14,116,144';         // Warna Kotak Bullish Order Block (Base Demand)
extern color         InpColorBearishOB     = C'190,18,60';          // Warna Kotak Bearish Order Block (Supply Zone)
extern color         InpColorFVG           = C'217,119,6';          // Warna Kotak Fair Value Gap (FVG Imbalance)

//--- 10. STATISTIK PERFORMA & TAMPILAN DASHBOARD ---
extern string       sec10                  = "=== 10. STATISTIK PERFORMA & TAMPILAN DASHBOARD ===";
extern bool          InpShowDashboard      = true;                  // Tampilkan Dashboard Monitor 4 Pilar
extern int           InpDashboardX         = 15;                    // Posisi Awal Dashboard X (Pixel dari Kiri)
extern int           InpDashboardY         = 20;                    // Posisi Awal Dashboard Y (Pixel dari Atas)
extern bool          InpShowPnLStats       = true;                  // Tampilkan Rekap PnL (Sejak Start, Harian, Mingguan)
extern bool          InpResetStatsOnStart  = false;                 // Reset Statistik Awal Saat EA Dipasang Ulang

//--- 11. NOTIFIKASI PUSH KE SMARTPHONE (HP) ---
extern string       sec11                  = "=== 11. NOTIFIKASI PUSH KE SMARTPHONE (HP) ===";
extern bool          InpSendPushNotifications = true;               // Kirim Notifikasi Instan ke HP (MetaTrader 4 Mobile)
extern bool          InpNotifyOnEntry         = true;               // Notifikasi Saat Eksekusi Open Posisi (BUY / SELL)
extern bool          InpNotifyOnSLPlus        = true;               // Notifikasi Saat Auto-BE / SL+ Mengunci Profit
extern bool          InpNotifyOnPartial       = true;               // Notifikasi Saat TP1 50% Ditutup & Runner Aktif
extern bool          InpNotifyOnCircuitBreaker= true;               // Notifikasi Saat Circuit Breaker Cooldown Terpicu

//+------------------------------------------------------------------+
//| STRUKTUR DATA INTERNAL (SMC & CANDLESTICK INTELLIGENCE)          |
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
   double R1;
   double R2;
   double R3;
   double S1;
   double S2;
   double S3;
   bool   isValid;
};

struct AutoFibo
{
   double high;
   double low;
   double level000;
   double level236;
   double level382;
   double level500;
   double level618;
   double level786;
   double level100;
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
//| VARIABEL GLOBAL & STATE                                          |
//+------------------------------------------------------------------+
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
int            g_panelH           = 475;
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

// Variabel Status Circuit Breaker & VSA Institusional (v2.3)
int                  g_consecutiveLossCount = 0;
datetime             g_lastLossTime         = 0;
datetime             g_cooldownUntilTime    = 0;
double               g_todayClosedProfit    = 0.0;
bool                 g_dailyLossLimitHit    = false;

string         g_lastSignalType = "MENUNGGU SETUP";
string         g_lastBOSStatus  = "NETRAL";
string         g_lastFiboStatus = "DILUAR GP";
string         g_doubleAlignStr = "MENUNGGU DATA";

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: KONVERSI PIPS & POINTS                          |
//+------------------------------------------------------------------+
double PipToPrice(double pips)
{
   double point = MarketInfo(Symbol(), MODE_POINT);
   int digits   = (int)MarketInfo(Symbol(), MODE_DIGITS);
   bool isGold  = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
   double mult  = 1.0;
   if (isGold)
   {
      if (digits == 3) mult = 100.0;
      else if (digits == 2) mult = 10.0;
      else mult = 1.0;
   }
   else
   {
      if (digits == 5 || digits == 3) mult = 10.0;
      else mult = 1.0;
   }
   return pips * point * mult;
}

double PriceToPips(double priceDiff)
{
   double point = MarketInfo(Symbol(), MODE_POINT);
   int digits   = (int)MarketInfo(Symbol(), MODE_DIGITS);
   if (point <= 0.0) return 0.0;
   bool isGold  = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
   double mult  = 1.0;
   if (isGold)
   {
      if (digits == 3) mult = 100.0;
      else if (digits == 2) mult = 10.0;
      else mult = 1.0;
   }
   else
   {
      if (digits == 5 || digits == 3) mult = 10.0;
      else mult = 1.0;
   }
   return MathAbs(priceDiff) / (point * mult);
}

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: NOTIFIKASI PUSH SMARTPHONE (HP)                 |
//+------------------------------------------------------------------+
void SendPushAlert(string msg)
{
   if (!InpSendPushNotifications) return;
   SendNotification("[VIKAR EA MT4 - " + Symbol() + "]\n" + msg);
}

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: HITUNG LOT SIZE KOMPATIBEL BROKER QUICKPRO      |
//+------------------------------------------------------------------+
double CalculateRiskLot(double slDistancePrice)
{
   double brokerMinLot  = MarketInfo(Symbol(), MODE_MINLOT);
   double brokerMaxLot  = MarketInfo(Symbol(), MODE_MAXLOT);
   double brokerStepLot = MarketInfo(Symbol(), MODE_LOTSTEP);

   // Safeguard jika broker mengembalikan 0
   if (brokerMinLot <= 0.0) brokerMinLot = 0.01;
   if (brokerMaxLot <= 0.0) brokerMaxLot = 100.0;
   if (brokerStepLot <= 0.0) brokerStepLot = 0.01;

   double finalLot = brokerMinLot;

   if (InpLotType == LOT_TYPE_BROKER_MIN)
   {
      finalLot = brokerMinLot;
   }
   else if (InpLotType == LOT_TYPE_FIXED)
   {
      finalLot = InpFixedLot;
   }
   else if (InpLotType == LOT_TYPE_RISK_PERCENT)
   {
      double balance = AccountBalance();
      double riskMoney = balance * (InpRiskPercent / 100.0);
      double tickValue = MarketInfo(Symbol(), MODE_TICKVALUE);
      double tickSize  = MarketInfo(Symbol(), MODE_TICKSIZE);

      if (tickSize > 0 && tickValue > 0 && slDistancePrice > 0)
      {
         double ticksAtRisk = slDistancePrice / tickSize;
         double calculatedLot = riskMoney / (ticksAtRisk * tickValue);
         finalLot = calculatedLot;
      }
      else
      {
         finalLot = brokerMinLot;
      }
   }

   // Batasi Lot sesuai Min / Max User dan Broker QuickPro
   double effectiveMinLot = (InpMinLot > 0.0) ? MathMax(InpMinLot, brokerMinLot) : brokerMinLot;
   double effectiveMaxLot = (InpMaxLot > 0.0) ? MathMin(InpMaxLot, brokerMaxLot) : brokerMaxLot;
   if (effectiveMaxLot < effectiveMinLot) effectiveMaxLot = effectiveMinLot;

   finalLot = MathMax(effectiveMinLot, MathMin(effectiveMaxLot, finalLot));

   // Normalisasi pembulatan lot sesuai step lot broker QuickPro
   finalLot = MathFloor(finalLot / brokerStepLot) * brokerStepLot;

   int lotDigits = 2;
   if (brokerStepLot == 1.0) lotDigits = 0;
   else if (brokerStepLot == 0.1) lotDigits = 1;
   else if (brokerStepLot == 0.01) lotDigits = 2;
   else if (brokerStepLot == 0.001) lotDigits = 3;

   return NormalizeDouble(finalLot, lotDigits);
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
   return "$0.00";
}

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: HITUNG FLOATING PNL & JUMLAH POSISI AKTIF       |
//+------------------------------------------------------------------+
double GetOpenFloatingPnL(int &count)
{
   count = 0;
   double totalFloat = 0.0;
   int total = OrdersTotal();
   for (int i = 0; i < total; i++)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if (OrderSymbol() == Symbol() && OrderMagicNumber() == InpMagicNumber)
      {
         count++;
         totalFloat += OrderProfit() + OrderSwap() + OrderCommission();
      }
   }
   return totalFloat;
}

//+------------------------------------------------------------------+
//| FUNGSI PEMBANTU: HITUNG HISTORI STATISTIK PERFORMA TRADING MT4   |
//+------------------------------------------------------------------+
TradeStats CalculateHistoryStats(datetime fromTime)
{
   TradeStats s;
   s.grossProfit = 0.0;
   s.grossLoss   = 0.0;
   s.netProfit   = 0.0;
   s.winTrades   = 0;
   s.lossTrades  = 0;
   s.totalTrades = 0;

   int histTotal = OrdersHistoryTotal();
   for (int i = 0; i < histTotal; i++)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
      if (OrderCloseTime() < fromTime) continue;

      double profit = OrderProfit() + OrderSwap() + OrderCommission();
      s.netProfit += profit;
      s.totalTrades++;

      if (profit > 0.0001)
      {
         s.grossProfit += profit;
         s.winTrades++;
      }
      else if (profit < -0.0001)
      {
         s.grossLoss += MathAbs(profit);
         s.lossTrades++;
      }
   }
   return s;
}

//+------------------------------------------------------------------+
//| DETEKSI LILIN BARU (NON-REPAINT BAR CLOSE RULE)                  |
//+------------------------------------------------------------------+
bool IsNewBar()
{
   datetime currentBarTime = Time[0];
   if (currentBarTime != lastBarTime)
   {
      lastBarTime = currentBarTime;
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|
//+------------------------------------------------------------------+
bool CheckCircuitBreakers()
{
   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit)
      return true;

   datetime todayStart = iTime(Symbol(), PERIOD_D1, 0);
   int consecutiveLosses = 0;
   datetime lastLossTime = 0;
   double todayClosedPnL = 0.0;
   int histTotal = OrdersHistoryTotal();

   for (int i = 0; i < histTotal; i++)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
      if (OrderCloseTime() < todayStart) continue;

      double profit = OrderProfit() + OrderSwap() + OrderCommission();
      todayClosedPnL += profit;

      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil modal)
      {
         consecutiveLosses++;
         lastLossTime = OrderCloseTime();
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER! TIDAK PERNAH MEMICU COOLDOWN!
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
      double currentBal = AccountBalance();
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

   return true;
}

//+------------------------------------------------------------------+
//| UPDATE DAILY PIVOT POINTS (P, R1-R3, S1-S3)                      |
//+------------------------------------------------------------------+
void UpdateDailyPivots()
{
   double dHigh  = iHigh(Symbol(), PERIOD_D1, 1);
   double dLow   = iLow(Symbol(), PERIOD_D1, 1);
   double dClose = iClose(Symbol(), PERIOD_D1, 1);

   if (dHigh <= 0 || dLow <= 0 || dClose <= 0)
   {
      currentPivot.isValid = false;
      return;
   }

   currentPivot.P  = (dHigh + dLow + dClose) / 3.0;
   currentPivot.R1 = (2.0 * currentPivot.P) - dLow;
   currentPivot.S1 = (2.0 * currentPivot.P) - dHigh;
   currentPivot.R2 = currentPivot.P + (dHigh - dLow);
   currentPivot.S2 = currentPivot.P - (dHigh - dLow);
   currentPivot.R3 = dHigh + 2.0 * (currentPivot.P - dLow);
   currentPivot.S3 = dLow - 2.0 * (dHigh - currentPivot.P);
   currentPivot.isValid = true;
}

//+------------------------------------------------------------------+
//| UPDATE AYUNAN STRUKTURAL SMC (SWING HIGH & LOW FRACTAL)          |
//+------------------------------------------------------------------+
void UpdateSMCSwings(int lookback)
{
   int limit = MathMin(lookback, Bars - 5);
   int k = InpFractalPeriod;

   for (int i = 2; i <= limit - k; i++)
   {
      bool isHigh = true;
      bool isLow  = true;

      for (int j = 1; j <= k; j++)
      {
         if (High[i] <= High[i - j] || High[i] <= High[i + j]) isHigh = false;
         if (Low[i] >= Low[i - j]   || Low[i] >= Low[i + j])   isLow  = false;
      }

      if (isHigh && lastSwingHigh.time != Time[i])
      {
         prevSwingHigh = lastSwingHigh;
         lastSwingHigh.time   = Time[i];
         lastSwingHigh.price  = High[i];
         lastSwingHigh.isHigh = true;
         lastSwingHigh.isSwept = false;
      }

      if (isLow && lastSwingLow.time != Time[i])
      {
         prevSwingLow = lastSwingLow;
         lastSwingLow.time   = Time[i];
         lastSwingLow.price  = Low[i];
         lastSwingLow.isHigh = false;
         lastSwingLow.isSwept = false;
      }
   }
}

//+------------------------------------------------------------------+
//| ANALISIS STRUKTUR PASAR SMC (BOS, CHOCH, SWEEP, DISKON/PREMIUM)  |
//+------------------------------------------------------------------+
SMCStructureAnalysis AnalyzeMarketStructure()
{
   SMCStructureAnalysis s;
   s.structure = SMC_STRUCT_NEUTRAL;
   s.structureName = "SIDEWAYS";
   s.hasBOS = false;
   s.hasCHoCH = false;
   s.hasSweep = false;
   s.sweepPrice = 0.0;
   s.dealingRangeLow = lastSwingLow.price;
   s.dealingRangeHigh = lastSwingHigh.price;
   s.discountPercent = 50.0;
   s.isDiscount = false;
   s.isPremium = false;
   s.hasFVG = g_activeFVG.isValid;
   s.fvgTop = g_activeFVG.top;
   s.fvgBottom = g_activeFVG.bottom;

   if (s.dealingRangeHigh > s.dealingRangeLow)
   {
      double range = s.dealingRangeHigh - s.dealingRangeLow;
      s.discountPercent = ((Close[1] - s.dealingRangeLow) / range) * 100.0;
      s.isDiscount = (s.discountPercent <= 50.0);
      s.isPremium  = (s.discountPercent >= 50.0);
   }

   // 1. Deteksi Liquidity Sweep (Stop Hunt)
   if (High[1] > lastSwingHigh.price && Close[1] < lastSwingHigh.price)
   {
      s.hasSweep = true;
      s.sweepPrice = High[1];
      lastSwingHigh.isSwept = true;
   }
   else if (Low[1] < lastSwingLow.price && Close[1] > lastSwingLow.price)
   {
      s.hasSweep = true;
      s.sweepPrice = Low[1];
      lastSwingLow.isSwept = true;
   }

   // 2. Deteksi Break of Structure (BOS) & Change of Character (CHoCH)
   if (Close[1] > lastSwingHigh.price && lastSwingHigh.price > 0)
   {
      if (lastSwingHigh.price < prevSwingHigh.price)
      {
         s.hasCHoCH = true;
         s.structure = SMC_STRUCT_CHOCH_BUY;
         s.structureName = "BULLISH CHoCH (REVERSAL)";
      }
      else
      {
         s.hasBOS = true;
         s.structure = SMC_STRUCT_BULLISH;
         s.structureName = "BULLISH BOS (CONTINUATION)";
      }
   }
   else if (Close[1] < lastSwingLow.price && lastSwingLow.price > 0)
   {
      if (lastSwingLow.price > prevSwingLow.price)
      {
         s.hasCHoCH = true;
         s.structure = SMC_STRUCT_CHOCH_SELL;
         s.structureName = "BEARISH CHoCH (REVERSAL)";
      }
      else
      {
         s.hasBOS = true;
         s.structure = SMC_STRUCT_BEARISH;
         s.structureName = "BEARISH BOS (CONTINUATION)";
      }
   }
   else
   {
      if (lastSwingHigh.price > prevSwingHigh.price && lastSwingLow.price > prevSwingLow.price)
      {
         s.structure = SMC_STRUCT_BULLISH;
         s.structureName = "BULLISH BIAS (HH-HL)";
      }
      else if (lastSwingHigh.price < prevSwingHigh.price && lastSwingLow.price < prevSwingLow.price)
      {
         s.structure = SMC_STRUCT_BEARISH;
         s.structureName = "BEARISH BIAS (LH-LL)";
      }
   }

   return s;
}

//+------------------------------------------------------------------+
//| DETEKSI ORDER BLOCK (OB) DISPLACEMENT ATR & MITIGASI             |
//+------------------------------------------------------------------+
void DetectOrderBlocks(int lookback, double currentAtr)
{
   int limit = MathMin(lookback, InpOBMaxAgeBars);
   double dispThreshold = InpOBDisplacementAtrMult * currentAtr;

   // Pemindaian Bullish Order Block (Base Demand)
   for (int i = 2; i <= limit; i++)
   {
      bool isBearishCandle = (Close[i] < Open[i]);
      bool hasDisplacement = (Close[i - 1] - Open[i - 1]) >= dispThreshold;

      if (isBearishCandle && hasDisplacement)
      {
         g_bullishOB.isValid         = true;
         g_bullishOB.isBullish       = true;
         g_bullishOB.time            = Time[i];
         g_bullishOB.top             = MathMax(Open[i], Close[i]);
         g_bullishOB.bottom          = Low[i];
         g_bullishOB.median          = (g_bullishOB.top + g_bullishOB.bottom) / 2.0;
         g_bullishOB.displacementAtr = (Close[i - 1] - Open[i - 1]) / currentAtr;
         g_bullishOB.isMitigated     = (Low[1] <= g_bullishOB.top);
         g_bullishOB.barAge          = i;
         break;
      }
   }

   // Pemindaian Bearish Order Block (Supply Zone)
   for (int i = 2; i <= limit; i++)
   {
      bool isBullishCandle = (Close[i] > Open[i]);
      bool hasDisplacement = (Open[i - 1] - Close[i - 1]) >= dispThreshold;

      if (isBullishCandle && hasDisplacement)
      {
         g_bearishOB.isValid         = true;
         g_bearishOB.isBullish       = false;
         g_bearishOB.time            = Time[i];
         g_bearishOB.top             = High[i];
         g_bearishOB.bottom          = MathMin(Open[i], Close[i]);
         g_bearishOB.median          = (g_bearishOB.top + g_bearishOB.bottom) / 2.0;
         g_bearishOB.displacementAtr = (Open[i - 1] - Close[i - 1]) / currentAtr;
         g_bearishOB.isMitigated     = (High[1] >= g_bearishOB.bottom);
         g_bearishOB.barAge          = i;
         break;
      }
   }
}

//+------------------------------------------------------------------+
//| TRACKER FAIR VALUE GAP (FVG IMBALANCE)                           |
//+------------------------------------------------------------------+
void TrackFairValueGaps(int lookback)
{
   int limit = MathMin(lookback, InpFVGLookbackBars);
   double minGap = InpMinFVGPoints * Point;
   g_activeFVG.isValid = false;

   for (int i = 1; i <= limit - 2; i++)
   {
      // Bullish FVG: Low bar 1 lebih tinggi dari High bar 3
      if (Low[i] - High[i + 2] >= minGap)
      {
         g_activeFVG.isValid     = true;
         g_activeFVG.isBullish   = true;
         g_activeFVG.time        = Time[i + 1];
         g_activeFVG.top         = Low[i];
         g_activeFVG.bottom      = High[i + 2];
         g_activeFVG.mid         = (g_activeFVG.top + g_activeFVG.bottom) / 2.0;
         g_activeFVG.isMitigated = (Low[1] <= g_activeFVG.top);
         g_activeFVG.barAge      = i;
         break;
      }
      // Bearish FVG: High bar 1 lebih rendah dari Low bar 3
      else if (Low[i + 2] - High[i] >= minGap)
      {
         g_activeFVG.isValid     = true;
         g_activeFVG.isBullish   = false;
         g_activeFVG.time        = Time[i + 1];
         g_activeFVG.top         = Low[i + 2];
         g_activeFVG.bottom      = High[i];
         g_activeFVG.mid         = (g_activeFVG.top + g_activeFVG.bottom) / 2.0;
         g_activeFVG.isMitigated = (High[1] >= g_activeFVG.bottom);
         g_activeFVG.barAge      = i;
         break;
      }
   }
}

//+------------------------------------------------------------------+
//| MESIN POLA GRAFIK: DOUBLE TOP/BOTTOM, QUASIMODO, H&S, FLAGS      |
//+------------------------------------------------------------------+
ChartPatternAnalysis AnalyzeChartPatterns(int lookback, double currentAtr)
{
   ChartPatternAnalysis p;
   p.pattern = CHART_PATTERN_NONE;
   p.patternName = "Scanning Geometri...";
   p.isBullish = true;
   p.score = 0.0;
   p.keyLevel = 0.0;
   p.isValid = false;

   if (!InpUseChartPatterns) return p;

   double tol = 0.35 * currentAtr;

   // 1. Quasimodo Pattern (QM Institutional Setup - Skor 95 Poin)
   if (InpUseQuasimodo)
   {
      // Bullish QM: Left Shoulder Low -> Higher High -> Lower Low (Sweep) -> CHoCH Breakout -> Retrace to Left Shoulder
      if (prevSwingLow.price > 0 && lastSwingLow.price < prevSwingLow.price && lastSwingHigh.price > prevSwingHigh.price)
      {
         double leftShoulderLevel = prevSwingLow.price;
         if (MathAbs(Low[1] - leftShoulderLevel) <= tol || (Low[1] <= leftShoulderLevel && Close[1] >= leftShoulderLevel))
         {
            p.pattern = CHART_PATTERN_QUASIMODO_BUY;
            p.patternName = "★ Bullish Quasimodo (QM Level)";
            p.isBullish = true;
            p.score = 95.0;
            p.keyLevel = leftShoulderLevel;
            p.isValid = true;
            return p;
         }
      }
      // Bearish QM: Left Shoulder High -> Lower Low -> Higher High (Sweep) -> CHoCH Breakout -> Retrace to Left Shoulder
      if (prevSwingHigh.price > 0 && lastSwingHigh.price > prevSwingHigh.price && lastSwingLow.price < prevSwingLow.price)
      {
         double leftShoulderLevel = prevSwingHigh.price;
         if (MathAbs(High[1] - leftShoulderLevel) <= tol || (High[1] >= leftShoulderLevel && Close[1] <= leftShoulderLevel))
         {
            p.pattern = CHART_PATTERN_QUASIMODO_SELL;
            p.patternName = "★ Bearish Quasimodo (QM Level)";
            p.isBullish = false;
            p.score = 95.0;
            p.keyLevel = leftShoulderLevel;
            p.isValid = true;
            return p;
         }
      }
   }

   // 2. Double Bottom (W) & Double Top (M)
   if (InpUseDoubleTopBottom)
   {
      // Double Bottom (W): Dua lembah berdekatan dengan Liquidity Sweep pada kaki kedua
      if (lastSwingLow.price > 0 && prevSwingLow.price > 0 && MathAbs(lastSwingLow.price - prevSwingLow.price) <= tol)
      {
         p.pattern = CHART_PATTERN_DOUBLE_BOTTOM;
         p.patternName = "★ Double Bottom (W-Pattern)";
         p.isBullish = true;
         p.score = 85.0;
         p.keyLevel = lastSwingLow.price;
         p.isValid = true;
         return p;
      }
      // Double Top (M): Dua puncak berdekatan
      if (lastSwingHigh.price > 0 && prevSwingHigh.price > 0 && MathAbs(lastSwingHigh.price - prevSwingHigh.price) <= tol)
      {
         p.pattern = CHART_PATTERN_DOUBLE_TOP;
         p.patternName = "★ Double Top (M-Pattern)";
         p.isBullish = false;
         p.score = 85.0;
         p.keyLevel = lastSwingHigh.price;
         p.isValid = true;
         return p;
      }
   }

   // 3. Head and Shoulders (H&S)
   if (InpUseHeadAndShoulders)
   {
      if (lastSwingHigh.price < prevSwingHigh.price && prevSwingHigh.price > 0)
      {
         p.pattern = CHART_PATTERN_HEAD_SHOULDERS;
         p.patternName = "★ Head & Shoulders (H&S)";
         p.isBullish = false;
         p.score = 90.0;
         p.keyLevel = lastSwingHigh.price;
         p.isValid = true;
         return p;
      }
      if (lastSwingLow.price > prevSwingLow.price && prevSwingLow.price > 0)
      {
         p.pattern = CHART_PATTERN_INVERSE_HS;
         p.patternName = "★ Inverse Head & Shoulders";
         p.isBullish = true;
         p.score = 90.0;
         p.keyLevel = lastSwingLow.price;
         p.isValid = true;
         return p;
      }
   }

   // 4. Continuation Flags
   if (InpUseFlagsContinuation)
   {
      if (Close[1] > Close[4] && High[1] < High[2] && Low[1] > Low[2])
      {
         p.pattern = CHART_PATTERN_BULL_FLAG;
         p.patternName = "★ Bullish Flag Continuation";
         p.isBullish = true;
         p.score = 80.0;
         p.keyLevel = Low[1];
         p.isValid = true;
         return p;
      }
      if (Close[1] < Close[4] && High[1] < High[2] && Low[1] > Low[2])
      {
         p.pattern = CHART_PATTERN_BEAR_FLAG;
         p.patternName = "★ Bearish Flag Continuation";
         p.isBullish = false;
         p.score = 80.0;
         p.keyLevel = High[1];
         p.isValid = true;
         return p;
      }
   }

   return p;
}

//+------------------------------------------------------------------+
//| ANALISIS KECERDASAN CANDLESTICK (10 POLA REJECTION LENGKAP)      |
//+------------------------------------------------------------------+
CandleAnalysis AnalyzeCandlePattern(double ema8, double ema21, double fibo618, double pivotP)
{
   CandleAnalysis c;
   c.pattern = PATTERN_NONE;
   c.patternName = "Candle Biasa";
   c.isBullish = (Close[1] >= Open[1]);
   c.score = 0.0;
   c.wickRatio = 0.0;
   c.bodyRatio = 0.0;
   c.isHighQuality = false;

   double rng = High[1] - Low[1];
   if (rng <= 0.0) return c;

   double body      = MathAbs(Close[1] - Open[1]);
   double upperWick = High[1] - MathMax(Open[1], Close[1]);
   double lowerWick = MathMin(Open[1], Close[1]) - Low[1];

   c.wickRatio = ((c.isBullish ? lowerWick : upperWick) / rng) * 100.0;
   c.bodyRatio = (body / rng) * 100.0;

   // 1. Three White Soldiers & Three Black Crows (85 Poin)
   if (InpUseThreeSoldiersCrows)
   {
      if (Close[1] > Open[1] && Close[2] > Open[2] && Close[3] > Open[3] &&
          Close[1] > Close[2] && Close[2] > Close[3] &&
          Open[1] >= Open[2] && Open[2] >= Open[3])
      {
         c.pattern = PATTERN_THREE_SOLDIERS_CROWS;
         c.patternName = "Three White Soldiers (Expansion)";
         c.isBullish = true;
         c.score = 85.0;
         c.isHighQuality = true;
         return c;
      }
      else if (Close[1] < Open[1] && Close[2] < Open[2] && Close[3] < Open[3] &&
               Close[1] < Close[2] && Close[2] < Close[3] &&
               Open[1] <= Open[2] && Open[2] <= Open[3])
      {
         c.pattern = PATTERN_THREE_SOLDIERS_CROWS;
         c.patternName = "Three Black Crows (Expansion)";
         c.isBullish = false;
         c.score = 85.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 2. Bullish & Bearish Engulfing (85 Poin)
   if (InpUseEngulfing)
   {
      if (Close[1] > Open[1] && Close[2] < Open[2] && Close[1] >= Open[2] && Open[1] <= Close[2])
      {
         c.pattern = PATTERN_ENGULFING;
         c.patternName = "Bullish Engulfing (Absorption)";
         c.isBullish = true;
         c.score = 85.0;
         c.isHighQuality = true;
         return c;
      }
      else if (Close[1] < Open[1] && Close[2] > Open[2] && Close[1] <= Open[2] && Open[1] >= Close[2])
      {
         c.pattern = PATTERN_ENGULFING;
         c.patternName = "Bearish Engulfing (Absorption)";
         c.isBullish = false;
         c.score = 85.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 3. Pin Bar & Hammer Rejection (80 Poin)
   if (InpUseHammerPinBar)
   {
      if (lowerWick >= (0.55 * rng) && body <= (0.35 * rng))
      {
         c.pattern = PATTERN_HAMMER_PINBAR;
         c.patternName = "Bullish Pin Bar / Hammer";
         c.isBullish = true;
         c.score = 80.0;
         c.isHighQuality = true;
         return c;
      }
      else if (upperWick >= (0.55 * rng) && body <= (0.35 * rng))
      {
         c.pattern = PATTERN_HAMMER_PINBAR;
         c.patternName = "Bearish Shooting Star / Pin Bar";
         c.isBullish = false;
         c.score = 80.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 4. Dragonfly Doji & Gravestone Doji (82 Poin)
   if (InpUseDragonflyGravestone)
   {
      if (lowerWick >= (0.70 * rng) && body <= (0.10 * rng))
      {
         c.pattern = PATTERN_DOJI_REJECTION;
         c.patternName = "Dragonfly Doji (Extreme Rejection)";
         c.isBullish = true;
         c.score = 82.0;
         c.isHighQuality = true;
         return c;
      }
      else if (upperWick >= (0.70 * rng) && body <= (0.10 * rng))
      {
         c.pattern = PATTERN_DOJI_REJECTION;
         c.patternName = "Gravestone Doji (Extreme Rejection)";
         c.isBullish = false;
         c.score = 82.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 5. Morning Star & Evening Star (80 Poin)
   if (InpUseMorningEveningStar)
   {
      if (Close[3] < Open[3] && MathAbs(Close[2] - Open[2]) <= (0.35 * (High[2] - Low[2])) && Close[1] > Open[1] && Close[1] >= ((Open[3] + Close[3]) / 2.0))
      {
         c.pattern = PATTERN_MORNING_EVENING;
         c.patternName = "Morning Star (3-Bar Reversal)";
         c.isBullish = true;
         c.score = 80.0;
         c.isHighQuality = true;
         return c;
      }
      else if (Close[3] > Open[3] && MathAbs(Close[2] - Open[2]) <= (0.35 * (High[2] - Low[2])) && Close[1] < Open[1] && Close[1] <= ((Open[3] + Close[3]) / 2.0))
      {
         c.pattern = PATTERN_MORNING_EVENING;
         c.patternName = "Evening Star (3-Bar Reversal)";
         c.isBullish = false;
         c.score = 80.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 6. Harami & Inside Bar Compression (78 Poin)
   if (InpUseHaramiInsideBar)
   {
      if (High[1] <= High[2] && Low[1] >= Low[2])
      {
         c.pattern = PATTERN_HARAMI_INSIDE_BAR;
         c.patternName = (Close[1] >= Open[1]) ? "Bullish Harami Inside Bar" : "Bearish Harami Inside Bar";
         c.isBullish = (Close[1] >= Open[1]);
         c.score = 78.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 7. Piercing Line & Dark Cloud Cover (78 Poin)
   if (InpUsePiercingDarkCloud)
   {
      if (Close[2] < Open[2] && Close[1] > Open[1] && Open[1] <= Low[2] && Close[1] >= ((Open[2] + Close[2]) / 2.0))
      {
         c.pattern = PATTERN_PIERCING_DARKCLOUD;
         c.patternName = "Piercing Line Pattern";
         c.isBullish = true;
         c.score = 78.0;
         c.isHighQuality = true;
         return c;
      }
      else if (Close[2] > Open[2] && Close[1] < Open[1] && Open[1] >= High[2] && Close[1] <= ((Open[2] + Close[2]) / 2.0))
      {
         c.pattern = PATTERN_PIERCING_DARKCLOUD;
         c.patternName = "Dark Cloud Cover Pattern";
         c.isBullish = false;
         c.score = 78.0;
         c.isHighQuality = true;
         return c;
      }
   }

   // 8. Tweezer Double Level Test (75 Poin)
   if (InpUseTweezer)
   {
      double pipTol = PipToPrice(2.0);
      if (MathAbs(Low[1] - Low[2]) <= pipTol && lowerWick >= (0.40 * rng))
      {
         c.pattern = PATTERN_TWEEZER;
         c.patternName = "Tweezer Bottom Rejection";
         c.isBullish = true;
         c.score = 75.0;
         c.isHighQuality = true;
         return c;
      }
      else if (MathAbs(High[1] - High[2]) <= pipTol && upperWick >= (0.40 * rng))
      {
         c.pattern = PATTERN_TWEEZER;
         c.patternName = "Tweezer Top Rejection";
         c.isBullish = false;
         c.score = 75.0;
         c.isHighQuality = true;
         return c;
      }
   }

   return c;
}

//+------------------------------------------------------------------+
//| ANALISIS BIAS MAKRO HIGHER TIMEFRAME (H1 MACRO)                  |
//+------------------------------------------------------------------+
ENUM_HTF_BIAS AnalyzeHTFMacroTrend()
{
   if (!InpUseHTFFilter) return HTF_BIAS_NEUTRAL;

   double htfEma125 = iMA(Symbol(), InpHTFTimeframe, InpHTFTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double htfEma8   = iMA(Symbol(), InpHTFTimeframe, InpFastEMA,     0, MODE_EMA, PRICE_CLOSE, 1);
   double htfEma21  = iMA(Symbol(), InpHTFTimeframe, InpMediumEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double htfClose  = iClose(Symbol(), InpHTFTimeframe, 1);

   bool bull = (htfClose > htfEma125);
   bool bear = (htfClose < htfEma125);

   if (InpHTFRequireRibbon)
   {
      bull = bull && (htfEma8 > htfEma21);
      bear = bear && (htfEma8 < htfEma21);
   }

   if (bull)
   {
      g_htfMacroStr = "BULLISH (H1 di atas 125 & Ribbon)";
      return HTF_BIAS_BULLISH;
   }
   else if (bear)
   {
      g_htfMacroStr = "BEARISH (H1 di bawah 125 & Ribbon)";
      return HTF_BIAS_BEARISH;
   }

   g_htfMacroStr = "NEUTRAL / CONFLICT";
   return HTF_BIAS_NEUTRAL;
}

//+------------------------------------------------------------------+
//| UPDATE FIBONACCI RETRACEMENT SESUAI AYUNAN SMC AKTIF             |
//+------------------------------------------------------------------+
void UpdateAutoFibo(bool isBullish)
{
   if (!InpUseAutoFibo)
   {
      currentFibo.isValid = false;
      return;
   }

   double fHigh = lastSwingHigh.price;
   double fLow  = lastSwingLow.price;

   if (fHigh <= fLow || fLow <= 0)
   {
      currentFibo.isValid = false;
      return;
   }

   double range = fHigh - fLow;
   currentFibo.high = fHigh;
   currentFibo.low  = fLow;
   currentFibo.isValid = true;

   if (isBullish)
   {
      currentFibo.level000 = fHigh;
      currentFibo.level236 = fHigh - (0.236 * range);
      currentFibo.level382 = fHigh - (0.382 * range);
      currentFibo.level500 = fHigh - (InpFiboGPMin * range);
      currentFibo.level618 = fHigh - (InpFiboGPMid * range);
      currentFibo.level786 = fHigh - (InpFiboGPMax * range);
      currentFibo.level100 = fLow;
      currentFibo.ext272   = fHigh + (0.272 * range);
      currentFibo.ext618   = fHigh + (0.618 * range);
   }
   else
   {
      currentFibo.level000 = fLow;
      currentFibo.level236 = fLow + (0.236 * range);
      currentFibo.level382 = fLow + (0.382 * range);
      currentFibo.level500 = fLow + (InpFiboGPMin * range);
      currentFibo.level618 = fLow + (InpFiboGPMid * range);
      currentFibo.level786 = fLow + (InpFiboGPMax * range);
      currentFibo.level100 = fHigh;
      currentFibo.ext272   = fLow - (0.272 * range);
      currentFibo.ext618   = fLow - (0.618 * range);
   }
}

//+------------------------------------------------------------------+
//| PROTEKSI SHOCK GUARD (LONJAKAN VOLATILITAS BERITA)               |
//+------------------------------------------------------------------+
bool CheckShockGuard(double currentAtr)
{
   if (!InpUseShockGuard) return false;

   if (g_shockGuardActive)
   {
      g_shockCooldownLeft--;
      if (g_shockCooldownLeft <= 0)
      {
         g_shockGuardActive = false;
         Print("[SHOCK GUARD EXPIRED] Pasar kembali normal, EA aktif mencari sinyal.");
      }
      else
      {
         return true;
      }
   }

   double lastBarRange = High[1] - Low[1];
   if (currentAtr > 0 && lastBarRange >= (InpShockAtrMult * currentAtr))
   {
      g_shockGuardActive = true;
      g_shockCooldownLeft = InpShockCooldownBars;
      g_lastShockTime = Time[1];
      Print("[SHOCK GUARD TRIGGERED] Terdeteksi lonjakan lilin abnormal: ", DoubleToString(PriceToPips(lastBarRange), 1), " pips (", DoubleToString(lastBarRange / currentAtr, 1), "x ATR). Jeda ", InpShockCooldownBars, " lilin.");
      return true;
   }

   return false;
}

//+------------------------------------------------------------------+
//| FILTER WHIPSAW DI AREA EMA 125                                   |
//+------------------------------------------------------------------+
bool IsWhipsawEMA125()
{
   if (!InpFilterWhipsaw125) return false;

   int crossCount = 0;
   for (int i = 1; i <= 6; i++)
   {
      double emaVal = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, i);
      bool above1 = (Close[i] > emaVal);
      bool above2 = (Close[i + 1] > emaVal);
      if (above1 != above2) crossCount++;
   }

   return (crossCount >= 3);
}

//+------------------------------------------------------------------+
//| SISTEM SKORING KONFLUENSI 4 PILAR TERPADU (0 - 100 POIN)         |
//+------------------------------------------------------------------+
ConfluenceScoreResult CalculateConfluenceScore(bool isBuy, double currentAtr,
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

   double close1 = Close[1];
   double high1  = High[1];
   double low1   = Low[1];

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
            r.obMitigationPts += 12.0;
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

      // 10. Volume Spread Analysis (VSA Footprint Absorption & No-Supply Test)
      if (InpUseVSA)
      {
         long sumVol = 0;
         int countVol = 0;
         int vLookback = MathMin(InpVSALookbackBars, Bars - 5);
         for (int v = 2; v < 2 + vLookback; v++)
         {
            sumVol += Volume[v];
            countVol++;
         }
         double avgVol = (countVol > 0) ? ((double)sumVol / (double)countVol) : (double)Volume[1];
         double volRatio = (avgVol > 0) ? ((double)Volume[1] / avgVol) : 1.0;

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
   }
   else // SELL
   {
      if (smc.structure == SMC_STRUCT_BEARISH || smc.hasBOS)
         r.structurePts += 15.0;
      if (smc.hasCHoCH)
         r.structurePts = 20.0;
      if (smc.isPremium)
         r.structurePts += 5.0;
      r.structurePts = MathMin(20.0, r.structurePts);

      if (ob.isValid && !ob.isBullish)
      {
         r.obMitigationPts += 8.0;
         if (high1 >= ob.bottom && low1 <= ob.top)
            r.obMitigationPts += 12.0;
         else if (MathAbs(high1 - ob.bottom) <= (0.5 * currentAtr))
            r.obMitigationPts += 6.0;
      }

      if (ob.isValid && ob.displacementAtr >= 1.25)
         r.displacementPts += MathMin(15.0, 5.0 + (ob.displacementAtr * 5.0));

      if (fvg.isValid && !fvg.isBullish)
      {
         r.fvgPts += 6.0;
         if (high1 >= fvg.bottom && low1 <= fvg.top)
            r.fvgPts += 9.0;
      }

      if (smc.hasSweep && high1 >= lastSwingHigh.price)
         r.sweepPts = 10.0;

      if (fibo.isValid && high1 >= fibo.level500 && low1 <= fibo.level786)
         r.fiboGPPts = 10.0;
      else if (fibo.isValid && smc.isPremium)
         r.fiboGPPts = 5.0;

      if (close1 < ema125)
      {
         r.emaRibbonPts += 5.0;
         if (ema8 < ema21)
            r.emaRibbonPts += 5.0;
      }

      if (!candle.isBullish && candle.score > 0)
         r.candlePts = MathMin(10.0, candle.score * 0.10);

      if (g_chartPattern.isValid && !g_chartPattern.isBullish && g_chartPattern.score >= InpMinChartPatternScore)
         r.chartPatternPts = MathMin(15.0, g_chartPattern.score * 0.15);

      if (InpUseVSA)
      {
         long sumVol = 0;
         int countVol = 0;
         int vLookback = MathMin(InpVSALookbackBars, Bars - 5);
         for (int v = 2; v < 2 + vLookback; v++)
         {
            sumVol += Volume[v];
            countVol++;
         }
         double avgVol = (countVol > 0) ? ((double)sumVol / (double)countVol) : (double)Volume[1];
         double volRatio = (avgVol > 0) ? ((double)Volume[1] / avgVol) : 1.0;

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
//| ON-CHART SMC VISUALIZER (GAMBAR OB, FVG & BOS DI MT4)            |
//+------------------------------------------------------------------+
void CleanSMCObjects()
{
   int total = ObjectsTotal();
   for (int i = total - 1; i >= 0; i--)
   {
      string name = ObjectName(i);
      if (StringFind(name, "VIKAR_SMC_") == 0)
         ObjectDelete(name);
   }
}

void DrawSMCObjectsOnChart()
{
   if (!InpDrawSMCOnChart) return;

   datetime tStart = Time[MathMin(30, Bars - 1)];
   datetime tEnd   = Time[0] + (Period() * 60 * 10);

   // Gambar Bullish OB (Base Demand)
   if (g_bullishOB.isValid && !g_bullishOB.isMitigated)
   {
      string name = "VIKAR_SMC_BULL_OB";
      if (ObjectFind(name) < 0) ObjectCreate(name, OBJ_RECTANGLE, 0, g_bullishOB.time, g_bullishOB.top, tEnd, g_bullishOB.bottom);
      else
      {
         ObjectSet(name, OBJPROP_TIME1, g_bullishOB.time);
         ObjectSet(name, OBJPROP_PRICE1, g_bullishOB.top);
         ObjectSet(name, OBJPROP_TIME2, tEnd);
         ObjectSet(name, OBJPROP_PRICE2, g_bullishOB.bottom);
      }
      ObjectSet(name, OBJPROP_COLOR, InpColorBullishOB);
      ObjectSet(name, OBJPROP_BACK, true);
   }

   // Gambar Bearish OB (Supply Zone)
   if (g_bearishOB.isValid && !g_bearishOB.isMitigated)
   {
      string name = "VIKAR_SMC_BEAR_OB";
      if (ObjectFind(name) < 0) ObjectCreate(name, OBJ_RECTANGLE, 0, g_bearishOB.time, g_bearishOB.top, tEnd, g_bearishOB.bottom);
      else
      {
         ObjectSet(name, OBJPROP_TIME1, g_bearishOB.time);
         ObjectSet(name, OBJPROP_PRICE1, g_bearishOB.top);
         ObjectSet(name, OBJPROP_TIME2, tEnd);
         ObjectSet(name, OBJPROP_PRICE2, g_bearishOB.bottom);
      }
      ObjectSet(name, OBJPROP_COLOR, InpColorBearishOB);
      ObjectSet(name, OBJPROP_BACK, true);
   }

   // Gambar FVG Imbalance
   if (g_activeFVG.isValid && !g_activeFVG.isMitigated)
   {
      string name = "VIKAR_SMC_FVG";
      if (ObjectFind(name) < 0) ObjectCreate(name, OBJ_RECTANGLE, 0, g_activeFVG.time, g_activeFVG.top, tEnd, g_activeFVG.bottom);
      else
      {
         ObjectSet(name, OBJPROP_TIME1, g_activeFVG.time);
         ObjectSet(name, OBJPROP_PRICE1, g_activeFVG.top);
         ObjectSet(name, OBJPROP_TIME2, tEnd);
         ObjectSet(name, OBJPROP_PRICE2, g_activeFVG.bottom);
      }
      ObjectSet(name, OBJPROP_COLOR, InpColorFVG);
      ObjectSet(name, OBJPROP_BACK, true);
   }
}

//+------------------------------------------------------------------+
//| MANAJEMEN POSISI AKTIF: AUTO-BE, PARTIAL 50%, TRAILING STRUCTURAL|
//+------------------------------------------------------------------+
void ManageActiveTrades()
{
   if (!InpUseBreakeven && !InpUseTrailingEMA21 && !InpUsePartialClose && !InpUseStructuralTrailing)
      return;

   // Bersihkan global variable jika tidak ada order aktif
   if (OrdersTotal() == 0)
   {
      int totalGV = GlobalVariablesTotal();
      for (int g = totalGV - 1; g >= 0; g--)
      {
         string gvName = GlobalVariableName(g);
         if (StringFind(gvName, "VIKAR_PARTIAL_") == 0)
            GlobalVariableDel(gvName);
      }
   }

   double ema21Val = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double currentAtr = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   int stopsLevel  = (int)MarketInfo(Symbol(), MODE_STOPLEVEL);
   int freezeLevel = (int)MarketInfo(Symbol(), MODE_FREEZELEVEL);
   double minStopDist = MathMax(MathMax(stopsLevel * Point, freezeLevel * Point), 10 * Point);

   int total = OrdersTotal();
   for (int i = total - 1; i >= 0; i--)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;

      int    ticket   = OrderTicket();
      double open     = OrderOpenPrice();
      double sl       = OrderStopLoss();
      double tp       = OrderTakeProfit();
      int    type     = OrderType();
      double posVol   = OrderLots();
      double current  = (type == OP_BUY) ? Bid : Ask;

      string gvKey = "VIKAR_PARTIAL_" + IntegerToString(ticket);
      bool isRunnerLot = GlobalVariableCheck(gvKey);

      // 1. Partial Take Profit 50% di TP1
      if (InpUsePartialClose && !isRunnerLot)
      {
         bool triggerTP1 = false;
         if (type == OP_BUY)
         {
            if (InpPartialTriggerMode == BE_MODE_PIPS)
            {
               if (PriceToPips(current - open) >= InpPartialTriggerPips) triggerTP1 = true;
            }
            else
            {
               double riskDist = open - sl;
               if (riskDist > 0 && (current - open) >= (InpPartialRRTrigger * riskDist)) triggerTP1 = true;
            }

            if (triggerTP1)
            {
               double brokerMinLot  = MarketInfo(Symbol(), MODE_MINLOT);
               double brokerStepLot = MarketInfo(Symbol(), MODE_LOTSTEP);
               double closeVol      = MathFloor((posVol * (InpPartialClosePercent / 100.0)) / brokerStepLot) * brokerStepLot;
               double remainVol     = posVol - closeVol;

               if (closeVol >= brokerMinLot && remainVol >= brokerMinLot)
               {
                  if (OrderClose(ticket, closeVol, Bid, InpDeviation, clrBlue))
                  {
                     GlobalVariableSet(gvKey, 1.0);
                     Print("[PARTIAL TP1] Posisi BUY #", ticket, " ditutup 50% (", closeVol, " lot)! Sisa ", remainVol, " lot berjalan sebagai RUNNER!");
                     if (InpNotifyOnPartial) SendPushAlert("TP1 50% CLOSED!\nPosisi BUY #" + IntegerToString(ticket) + " amankan 50% profit. Sisa lot berjalan sebagai Runner!");
                     if (InpPartialMoveSLPlus)
                     {
                        double newSL = NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), Digits);
                        if (newSL > sl && (current - newSL) >= minStopDist)
                        {
                           OrderModify(ticket, open, newSL, tp, 0, clrBlue);
                        }
                     }
                  }
               }
               else
               {
                  GlobalVariableSet(gvKey, 1.0);
                  double newSL = NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), Digits);
                  if (newSL > sl && (current - newSL) >= minStopDist)
                  {
                     OrderModify(ticket, open, newSL, tp, 0, clrBlue);
                  }
               }
            }
         }
         else if (type == OP_SELL)
         {
            if (InpPartialTriggerMode == BE_MODE_PIPS)
            {
               if (PriceToPips(open - current) >= InpPartialTriggerPips) triggerTP1 = true;
            }
            else
            {
               double riskDist = sl - open;
               if (riskDist > 0 && (open - current) >= (InpPartialRRTrigger * riskDist)) triggerTP1 = true;
            }

            if (triggerTP1)
            {
               double brokerMinLot  = MarketInfo(Symbol(), MODE_MINLOT);
               double brokerStepLot = MarketInfo(Symbol(), MODE_LOTSTEP);
               double closeVol      = MathFloor((posVol * (InpPartialClosePercent / 100.0)) / brokerStepLot) * brokerStepLot;
               double remainVol     = posVol - closeVol;

               if (closeVol >= brokerMinLot && remainVol >= brokerMinLot)
               {
                  if (OrderClose(ticket, closeVol, Ask, InpDeviation, clrRed))
                  {
                     GlobalVariableSet(gvKey, 1.0);
                     Print("[PARTIAL TP1] Posisi SELL #", ticket, " ditutup 50% (", closeVol, " lot)! Sisa ", remainVol, " lot berjalan sebagai RUNNER!");
                     if (InpNotifyOnPartial) SendPushAlert("TP1 50% CLOSED!\nPosisi SELL #" + IntegerToString(ticket) + " amankan 50% profit. Sisa lot berjalan sebagai Runner!");
                     if (InpPartialMoveSLPlus)
                     {
                        double newSL = NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), Digits);
                        if ((sl == 0 || newSL < sl) && (newSL - current) >= minStopDist)
                        {
                           OrderModify(ticket, open, newSL, tp, 0, clrRed);
                        }
                     }
                  }
               }
               else
               {
                  GlobalVariableSet(gvKey, 1.0);
                  double newSL = NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), Digits);
                  if ((sl == 0 || newSL < sl) && (newSL - current) >= minStopDist)
                  {
                     OrderModify(ticket, open, newSL, tp, 0, clrRed);
                  }
               }
            }
         }
      }

      // 2. Auto-Breakeven / SL+ (Kunci Modal)
      if (InpUseBreakeven)
      {
         if (type == OP_BUY)
         {
            bool triggerBE = false;
            if (InpBreakevenMode == BE_MODE_PIPS)
            {
               if (PriceToPips(current - open) >= InpBreakevenTriggerPips) triggerBE = true;
            }
            else
            {
               double riskDist = open - sl;
               if (riskDist > 0 && (current - open) >= (InpBreakevenRRTrigger * riskDist)) triggerBE = true;
            }

            if (triggerBE)
            {
               double newSL = NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), Digits);
               if ((sl < open || (newSL - sl) >= (10 * Point)) && (current - newSL) >= minStopDist)
               {
                  if (OrderModify(ticket, open, newSL, tp, 0, clrGreen))
                  {
                     Print("[AUTO-BE / SL+] Posisi BUY #", ticket, " SL digeser ke SL+: ", newSL);
                     if (InpNotifyOnSLPlus) SendPushAlert("AUTO-BE SL+ LOCKED!\nPosisi BUY #" + IntegerToString(ticket) + " SL dikunci ke " + DoubleToString(newSL, Digits) + " (Profit Terkunci)");
                  }
               }
            }
         }
         else if (type == OP_SELL)
         {
            bool triggerBE = false;
            if (InpBreakevenMode == BE_MODE_PIPS)
            {
               if (PriceToPips(open - current) >= InpBreakevenTriggerPips) triggerBE = true;
            }
            else
            {
               double riskDist = sl - open;
               if (riskDist > 0 && (open - current) >= (InpBreakevenRRTrigger * riskDist)) triggerBE = true;
            }

            if (triggerBE)
            {
               double newSL = NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), Digits);
               if ((sl > open || sl == 0 || (sl - newSL) >= (10 * Point)) && (newSL - current) >= minStopDist)
               {
                  if (OrderModify(ticket, open, newSL, tp, 0, clrGreen))
                  {
                     Print("[AUTO-BE / SL+] Posisi SELL #", ticket, " SL digeser ke SL+: ", newSL);
                     if (InpNotifyOnSLPlus) SendPushAlert("AUTO-BE SL+ LOCKED!\nPosisi SELL #" + IntegerToString(ticket) + " SL dikunci ke " + DoubleToString(newSL, Digits) + " (Profit Terkunci)");
                  }
               }
            }
         }
      }

      // 3. Trailing Stop EMA 21 Magenta
      if (InpUseTrailingEMA21)
      {
         if (type == OP_BUY)
         {
            double trailSL = NormalizeDouble(ema21Val - PipToPrice(InpTrailingBufferPips), Digits);
            if (trailSL > open && (trailSL - sl) >= (10 * Point) && (current - trailSL) >= minStopDist)
            {
               OrderModify(ticket, open, trailSL, tp, 0, clrGreen);
            }
         }
         else if (type == OP_SELL)
         {
            double trailSL = NormalizeDouble(ema21Val + PipToPrice(InpTrailingBufferPips), Digits);
            if (trailSL < open && (sl == 0 || (sl - trailSL) >= (10 * Point)) && (trailSL - current) >= minStopDist)
            {
               OrderModify(ticket, open, trailSL, tp, 0, clrGreen);
            }
         }
      }

      // 4. Multi-Stage Structural Trailing Stop untuk RUNNER (Pasca-TP1)
      if (InpUseStructuralTrailing && isRunnerLot)
      {
         if (type == OP_BUY)
         {
            if (lastSwingLow.price > 0 && lastSwingLow.price > open)
            {
               double structSL = NormalizeDouble(lastSwingLow.price - (InpStructuralTrailingAtrBuffer * currentAtr), Digits);
               if (structSL > sl && (structSL - sl) >= (10 * Point) && (current - structSL) >= minStopDist)
               {
                  if (OrderModify(ticket, open, structSL, tp, 0, clrGreen))
                  {
                     Print("[SMC STRUCTURAL RUNNER] Posisi BUY #", ticket, " SL dipindah di bawah Higher Low (HL): ", structSL);
                  }
               }
            }
         }
         else if (type == OP_SELL)
         {
            if (lastSwingHigh.price > 0 && lastSwingHigh.price < open)
            {
               double structSL = NormalizeDouble(lastSwingHigh.price + (InpStructuralTrailingAtrBuffer * currentAtr), Digits);
               if ((sl == 0 || structSL < sl) && (sl - structSL) >= (10 * Point) && (structSL - current) >= minStopDist)
               {
                  if (OrderModify(ticket, open, structSL, tp, 0, clrGreen))
                  {
                     Print("[SMC STRUCTURAL RUNNER] Posisi SELL #", ticket, " SL dipindah di atas Lower High (LH): ", structSL);
                  }
               }
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| AUTO CUT PROFIT SAAT INDIKASI PEMBALIKAN ARAH                    |
//+------------------------------------------------------------------+
void CheckAutoCutProfit(double currentAtr)
{
   if (!InpAutoCutProfit && !InpCutOnEarlyInvalidation) return;

   // Early Invalidation Cut
   if (InpCutOnEarlyInvalidation)
   {
      double dispThreshold = (currentAtr > 0) ? (0.75 * currentAtr) : PipToPrice(15.0);
      int total = OrdersTotal();
      for (int i = total - 1; i >= 0; i--)
      {
         if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
         if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
         if (Time[1] < OrderOpenTime()) continue;

         int ticket = OrderTicket();
         int type   = OrderType();

         if (type == OP_BUY && g_bullishOB.isValid && Close[1] < g_bullishOB.bottom && (Open[1] - Close[1]) >= dispThreshold)
         {
            Print("[EARLY INVALIDATION CUT] Bullish OB jebol oleh Bearish Displacement! Menutup BUY #", ticket);
            OrderClose(ticket, OrderLots(), Bid, InpDeviation, clrGold);
         }
         else if (type == OP_SELL && g_bearishOB.isValid && Close[1] > g_bearishOB.top && (Close[1] - Open[1]) >= dispThreshold)
         {
            Print("[EARLY INVALIDATION CUT] Bearish OB jebol oleh Bullish Displacement! Menutup SELL #", ticket);
            OrderClose(ticket, OrderLots(), Ask, InpDeviation, clrGold);
         }
      }
   }
}

//+------------------------------------------------------------------+
//| PEMERIKSAAN SINYAL EKSEKUSI (DUAL-ENGINE: SNIPER & MOMENTUM)     |
//+------------------------------------------------------------------+
void CheckTradeSignal()
{
   double currentAtr   = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   double currentEma8   = iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double currentEma21  = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double currentEma125 = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);

   // Filter Shock Guard
   if (CheckShockGuard(currentAtr))
   {
      g_lastSignalType = "SHOCK GUARD: JEDA PASCA-LONJAKAN VOLATILITAS";
      return;
   }

   // Update komponen analisa
   UpdateDailyPivots();
   UpdateSMCSwings(100);
   g_smcAnalysis = AnalyzeMarketStructure();
   DetectOrderBlocks(100, currentAtr);
   TrackFairValueGaps(100);
   g_chartPattern = AnalyzeChartPatterns(100, currentAtr);
   DrawSMCObjectsOnChart();

   bool currentTrendBias = (Close[1] > currentEma125);
   UpdateAutoFibo(currentTrendBias);
   g_candleAnalysis = AnalyzeCandlePattern(currentEma8, currentEma21, currentFibo.level618, currentPivot.P);

   CheckAutoCutProfit(currentAtr);

   // Periksa batas maksimal posisi aktif
   int openCount = 0;
   int total = OrdersTotal();
   for (int i = 0; i < total; i++)
   {
      if (OrderSelect(i, SELECT_BY_POS, MODE_TRADES))
      {
         if (OrderSymbol() == Symbol() && OrderMagicNumber() == InpMagicNumber)
            openCount++;
      }
   }
   if (openCount >= InpMaxOpenPositions) return;

   // Cooldown antar order
   if (lastOrderBarTime != 0 && (Time[0] - lastOrderBarTime) < (InpSignalCooldownBars * Period() * 60))
      return;

   // Whipsaw filter
   if (IsWhipsawEMA125())
   {
      g_lastSignalType = "FILTER: WHIPSAW DI EMA 125";
      return;
   }

   // Filter HTF Makro H1
   ENUM_HTF_BIAS htfBias = AnalyzeHTFMacroTrend();
   bool buyHTFOk  = (!InpUseHTFFilter || htfBias == HTF_BIAS_BULLISH);
   bool sellHTFOk = (!InpUseHTFFilter || htfBias == HTF_BIAS_BEARISH);

   //+---------------------------------------------------------------+
   //| EVALUASI SETUP BUY                                            |
   //+---------------------------------------------------------------+
   bool buyTrendEMA125 = (Close[1] > currentEma125);
   bool buyDoubleAlign = true;
   if (InpUseDailyPivots && InpRequireDoubleAlign)
      buyDoubleAlign = (Close[1] > currentPivot.P);

   if (buyTrendEMA125 && buyDoubleAlign)
   {
      if (!buyHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {
         UpdateAutoFibo(true);

         bool smcBullishOk = true;
         if (InpRequireBOSorCHoCH)
         {
            smcBullishOk = (g_smcAnalysis.structure == SMC_STRUCT_BULLISH ||
                            g_smcAnalysis.hasCHoCH ||
                            (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && Low[1] <= lastSwingLow.price));
         }

         if (InpRequireDiscount && !g_smcAnalysis.isDiscount)
            smcBullishOk = false;

         bool isSwept = (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && Low[1] <= lastSwingLow.price);

         // Pullback ke Ribbon EMA 8/21
         bool isPullbackEMA = false;
         int maxLookback = MathMin(InpPullbackLookback, Bars - 5);
         for (int b = 1; b <= maxLookback; b++)
         {
            double lowEma  = MathMin(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
            double highEma = MathMax(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
            if (Low[b] <= highEma && High[b] >= lowEma)
            {
               isPullbackEMA = true;
               break;
            }
         }

         // Golden Pocket
         bool isFiboGPOk = true;
         if (InpUseAutoFibo && InpRequireGoldenPocket && currentFibo.isValid)
            isFiboGPOk = (Low[1] <= currentFibo.level500 && High[1] >= currentFibo.level786);

         // Candlestick Rejection
         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
            isRejection = (Close[1] >= Open[1]);

         // Headroom
         bool isHeadroomOk = true;
         if (InpUseDailyPivots && currentPivot.R1 > Close[1])
         {
            double distToR1 = currentPivot.R1 - Close[1];
            if (distToR1 < (InpMinHeadroomATR * currentAtr)) isHeadroomOk = false;
         }

         // Order Block
         bool isOBMitigatedOk = true;
         if (InpUseOrderBlock && InpRequireOBMitigation)
            isOBMitigatedOk = (g_bullishOB.isValid && Low[1] <= g_bullishOB.top && High[1] >= g_bullishOB.bottom);

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = Close[1] - Open[1];
            bool isBigBullBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (Close[1] > currentEma8 && currentEma8 > currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || Close[1] > lastSwingHigh.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));

            if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
               isMomentumBreakout = true;
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||
                              (isMomentumBreakout && isHeadroomOk);

         if (canExecuteBuy)
         {
            double slPrice = 0.0;
            double tpPrice = 0.0;

            if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingLow.price > 0)
               slPrice = lastSwingLow.price - (InpSLBufferAtrMult * currentAtr);
            else if (InpSLType == SL_TYPE_CANDLE_WICK)
               slPrice = Low[1] - PipToPrice(5.0);
            else
               slPrice = Ask - PipToPrice(InpFixedSLPips);

            double slDist = Ask - slPrice;
            if (PriceToPips(slDist) < InpMinSLPips) slPrice = Ask - PipToPrice(InpMinSLPips);
            if (PriceToPips(slDist) > InpMaxSLPips) slPrice = Ask - PipToPrice(InpMaxSLPips);

            if (InpTPType == TP_TYPE_RISK_REWARD)
               tpPrice = Ask + (InpRiskRewardRatio * (Ask - slPrice));
            else if (InpTPType == TP_TYPE_FIBO_EXT && currentFibo.isValid && currentFibo.ext272 > Ask)
               tpPrice = currentFibo.ext272;
            else if (InpTPType == TP_TYPE_PIVOT_LEVEL && currentPivot.R1 > Ask)
               tpPrice = currentPivot.R1;
            else
               tpPrice = Ask + (InpRiskRewardRatio * (Ask - slPrice));

            // Stops Level validation
            int stopsLevel = (int)MarketInfo(Symbol(), MODE_STOPLEVEL);
            double minStopDist = MathMax(stopsLevel * Point, MarketInfo(Symbol(), MODE_SPREAD) * Point + (5 * Point));
            if ((Ask - slPrice) < minStopDist) slPrice = Ask - minStopDist;
            if ((tpPrice - Ask) < minStopDist) tpPrice = Ask + minStopDist;

            slPrice = NormalizeDouble(slPrice, Digits);
            tpPrice = NormalizeDouble(tpPrice, Digits);

            double lots = CalculateRiskLot(Ask - slPrice);

            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            int ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrBlue);

            if (ticket > 0)
            {
               lastOrderBarTime = Time[0];
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = "BUY EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
               Print("[BUY EXECUTION MT4] Ticket: #", ticket, " | Lot: ", lots, " | Price: ", Ask, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert("BUY " + DoubleToString(lots, 2) + " " + Symbol() + " @ " + DoubleToString(Ask, Digits) +
                                "\nSL: " + DoubleToString(slPrice, Digits) + " | TP: " + DoubleToString(tpPrice, Digits) +
                                "\nPola: " + patStr);
               }
               UpdateDashboard();
               return;
            }
            else
            {
               int err = GetLastError();
               Print("[BUY REJECTED MT4] Error: ", err);
               g_lastSignalType = "ORDER DITOLAK BROKER (Error " + IntegerToString(err) + ")";
            }
         }
      }
   }

   //+---------------------------------------------------------------+
   //| EVALUASI SETUP SELL                                           |
   //+---------------------------------------------------------------+
   bool sellTrendEMA125 = (Close[1] < currentEma125);
   bool sellDoubleAlign = true;
   if (InpUseDailyPivots && InpRequireDoubleAlign)
      sellDoubleAlign = (Close[1] < currentPivot.P);

   if (sellTrendEMA125 && sellDoubleAlign)
   {
      if (!sellHTFOk)
      {
         g_lastSignalType = "FILTER: KONTRA HTF (" + g_htfMacroStr + ")";
      }
      else
      {
         UpdateAutoFibo(false);

         bool smcBearishOk = true;
         if (InpRequireBOSorCHoCH)
         {
            smcBearishOk = (g_smcAnalysis.structure == SMC_STRUCT_BEARISH ||
                            g_smcAnalysis.hasCHoCH ||
                            (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && High[1] >= lastSwingHigh.price));
         }

         if (InpRequireDiscount && !g_smcAnalysis.isPremium)
            smcBearishOk = false;

         bool isSwept = (InpUseLiquiditySweep && g_smcAnalysis.hasSweep && High[1] >= lastSwingHigh.price);

         bool isPullbackEMA = false;
         int maxLookback = MathMin(InpPullbackLookback, Bars - 5);
         for (int b = 1; b <= maxLookback; b++)
         {
            double lowEma  = MathMin(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
            double highEma = MathMax(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
            if (High[b] >= lowEma && Low[b] <= highEma)
            {
               isPullbackEMA = true;
               break;
            }
         }

         bool isFiboGPOk = true;
         if (InpUseAutoFibo && InpRequireGoldenPocket && currentFibo.isValid)
            isFiboGPOk = (High[1] >= currentFibo.level500 && Low[1] <= currentFibo.level786);

         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (!g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
            isRejection = (Close[1] <= Open[1]);

         bool isHeadroomOk = true;
         if (InpUseDailyPivots && currentPivot.S1 < Close[1])
         {
            double distToS1 = Close[1] - currentPivot.S1;
            if (distToS1 < (InpMinHeadroomATR * currentAtr)) isHeadroomOk = false;
         }

         bool isOBMitigatedOk = true;
         if (InpUseOrderBlock && InpRequireOBMitigation)
            isOBMitigatedOk = (g_bearishOB.isValid && High[1] >= g_bearishOB.bottom && Low[1] <= g_bearishOB.top);

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);
         g_lastScoreResult = scoreRes;

         // Momentum Breakout Detection
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            double candleBody = Open[1] - Close[1];
            bool isBigBearBody = (candleBody >= (InpBreakoutAtrMult * currentAtr));
            bool isRibbonExpanding = (Close[1] < currentEma8 && currentEma8 < currentEma21);
            bool isBOSBreakout = (!InpBreakoutRequireBOS || Close[1] < lastSwingLow.price || g_smcAnalysis.hasBOS);
            bool isVSASupported = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));

            if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported)
               isMomentumBreakout = true;
         }

         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && scoreRes.isPassed) ||
                               (isMomentumBreakout && isHeadroomOk);

         if (canExecuteSell)
         {
            double slPrice = 0.0;
            double tpPrice = 0.0;

            if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingHigh.price > 0)
               slPrice = lastSwingHigh.price + (InpSLBufferAtrMult * currentAtr);
            else if (InpSLType == SL_TYPE_CANDLE_WICK)
               slPrice = High[1] + PipToPrice(5.0);
            else
               slPrice = Bid + PipToPrice(InpFixedSLPips);

            double slDist = slPrice - Bid;
            if (PriceToPips(slDist) < InpMinSLPips) slPrice = Bid + PipToPrice(InpMinSLPips);
            if (PriceToPips(slDist) > InpMaxSLPips) slPrice = Bid + PipToPrice(InpMaxSLPips);

            if (InpTPType == TP_TYPE_RISK_REWARD)
               tpPrice = Bid - (InpRiskRewardRatio * (slPrice - Bid));
            else if (InpTPType == TP_TYPE_FIBO_EXT && currentFibo.isValid && currentFibo.ext272 < Bid)
               tpPrice = currentFibo.ext272;
            else if (InpTPType == TP_TYPE_PIVOT_LEVEL && currentPivot.S1 < Bid)
               tpPrice = currentPivot.S1;
            else
               tpPrice = Bid - (InpRiskRewardRatio * (slPrice - Bid));

            int stopsLevel = (int)MarketInfo(Symbol(), MODE_STOPLEVEL);
            double minStopDist = MathMax(stopsLevel * Point, MarketInfo(Symbol(), MODE_SPREAD) * Point + (5 * Point));
            if ((slPrice - Bid) < minStopDist) slPrice = Bid + minStopDist;
            if ((Bid - tpPrice) < minStopDist) tpPrice = Bid - minStopDist;

            slPrice = NormalizeDouble(slPrice, Digits);
            tpPrice = NormalizeDouble(tpPrice, Digits);

            double lots = CalculateRiskLot(slPrice - Bid);

            string tradeCmt = InpTradeComment + (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS")));
            int ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrRed);

            if (ticket > 0)
            {
               lastOrderBarTime = Time[0];
               string patStr = isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName;
               g_lastSignalType = "SELL EXECUTED: " + patStr + " (Skor: " + DoubleToString(scoreRes.totalScore, 0) + ")";
               Print("[SELL EXECUTION MT4] Ticket: #", ticket, " | Lot: ", lots, " | Price: ", Bid, " | SL: ", slPrice, " | TP: ", tpPrice, " | Pattern: ", patStr);
               if (InpNotifyOnEntry)
               {
                  SendPushAlert("SELL " + DoubleToString(lots, 2) + " " + Symbol() + " @ " + DoubleToString(Bid, Digits) +
                                "\nSL: " + DoubleToString(slPrice, Digits) + " | TP: " + DoubleToString(tpPrice, Digits) +
                                "\nPola: " + patStr);
               }
               UpdateDashboard();
               return;
            }
            else
            {
               int err = GetLastError();
               Print("[SELL REJECTED MT4] Error: ", err);
               g_lastSignalType = "ORDER DITOLAK BROKER (Error " + IntegerToString(err) + ")";
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| ON-CHART HUD DASHBOARD DISPLAY (MODERN GLASSMORPHIC GUI)         |
//+------------------------------------------------------------------+
void CreateOrUpdateRect(string name, int x, int y, int w, int h, color bgCol, color borderCol)
{
   if (ObjectFind(name) < 0)
   {
      ObjectCreate(name, OBJ_RECTANGLE_LABEL, 0, 0, 0);
      ObjectSet(name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSet(name, OBJPROP_SELECTABLE, false);
      ObjectSet(name, OBJPROP_BACK, false);
   }
   ObjectSet(name, OBJPROP_XDISTANCE, x);
   ObjectSet(name, OBJPROP_YDISTANCE, y);
   ObjectSet(name, OBJPROP_XSIZE, w);
   ObjectSet(name, OBJPROP_YSIZE, h);
   ObjectSet(name, OBJPROP_BGCOLOR, bgCol);
   ObjectSet(name, OBJPROP_COLOR, borderCol);
}

void CreateOrUpdateText(string name, int x, int y, string text, color clr, int fontSize, string font)
{
   if (ObjectFind(name) < 0)
   {
      ObjectCreate(name, OBJ_LABEL, 0, 0, 0);
      ObjectSet(name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSet(name, OBJPROP_SELECTABLE, false);
   }
   ObjectSet(name, OBJPROP_XDISTANCE, x);
   ObjectSet(name, OBJPROP_YDISTANCE, y);
   ObjectSetText(name, text, fontSize, font, clr);
}

void DestroyDashboardGUI()
{
   int total = ObjectsTotal();
   for (int i = total - 1; i >= 0; i--)
   {
      string name = ObjectName(i);
      if (StringFind(name, "VIKAR_HUD_") == 0)
         ObjectDelete(name);
   }
}

void UpdateDashboard()
{
   if (!InpShowDashboard)
   {
      DestroyDashboardGUI();
      return;
   }

   double balance = AccountBalance();
   double equity  = AccountEquity();
   double spread  = PriceToPips(Ask - Bid);

   int openCount = 0;
   double openFloating = GetOpenFloatingPnL(openCount);

   datetime startOfDay  = iTime(Symbol(), PERIOD_D1, 0);
   if (startOfDay == 0) startOfDay = TimeCurrent() - 86400;

   datetime startOfWeek = iTime(Symbol(), PERIOD_W1, 0);
   if (startOfWeek == 0) startOfWeek = TimeCurrent() - (7 * 86400);

   TradeStats statsTotal = CalculateHistoryStats(g_eaStartTime);
   TradeStats statsDaily = CalculateHistoryStats(startOfDay);
   TradeStats statsWeekly= CalculateHistoryStats(startOfWeek);

   double totalGrowthPct = (g_eaInitialBalance > 0) ? ((balance - g_eaInitialBalance) / g_eaInitialBalance * 100.0) : 0.0;

   int panelX = g_panelX;
   int panelY = g_panelY;
   int panelW = g_panelW;
   int panelH = InpShowPnLStats ? 515 : 435;

   // 1. Container Utama
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, panelH, C'15,23,42', C'51,65,85');

   // 2. Header Banner
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 34, C'3,105,161', C'56,189,248');
   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 12, panelY + 4, "VIKAR 4-PILLAR PRO (MT4 QUICKPRO)", clrWhite, 10, "Segoe UI Bold");
   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 12, panelY + 19, Symbol() + " [" + IntegerToString(Period()) + "M] | " + lotDisplay + " | ID: " + IntegerToString(InpMagicNumber), C'224,242,254', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_HDR_DRAG", panelX + panelW - 74, panelY + 9, "[ :: GESER ]", C'186,230,253', 8, "Segoe UI Bold");

   // 3. Ringkasan Saldo Akun
   CreateOrUpdateText("VIKAR_HUD_BAL_START", panelX + 12, panelY + 42, "Start Modal: $" + DoubleToString(g_eaInitialBalance, 2) + "  (Aktivasi: " + TimeToStr(g_eaStartTime, TIME_MINUTES) + ")", C'148,163,184', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_BAL_CURR", panelX + 12, panelY + 56, "Saldo: $" + DoubleToString(balance, 2) + "  |  Equity: $" + DoubleToString(equity, 2), clrWhite, 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_FLOAT", panelX + 12, panelY + 72, "Floating: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Posisi)  |  Spread: " + DoubleToString(spread, 1) + " pips", floatClr, 8, "Segoe UI Bold");

   int currY = panelY + 92;

   // 4. Inset Card: Rekap Profit & Loss
   if (InpShowPnLStats)
   {
      CreateOrUpdateRect("VIKAR_HUD_PNL_BG", panelX + 8, currY, panelW - 16, 78, C'30,41,59', C'71,85,105');
      CreateOrUpdateText("VIKAR_HUD_PNL_TITLE", panelX + 15, currY + 4, "REKAP PROFIT & LOSS REAL-TIME:", C'251,191,36', 8, "Segoe UI Bold");

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

   // 5. Status 4 Pilar Multi-Confluence
   string scoreStr = "Ready";
   if (g_lastScoreResult.totalScore > 0)
      scoreStr = DoubleToString(g_lastScoreResult.totalScore, 0) + "/100 (" + g_lastScoreResult.grade + ")";
   color scoreClr = (g_lastScoreResult.totalScore >= 80.0) ? C'74,222,128' : ((g_lastScoreResult.totalScore >= 55.0) ? C'251,191,36' : C'203,213,225');
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
   if (g_smcAnalysis.hasSweep) smcStr = smcStr + " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr = smcStr + " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_PILAR1", panelX + 12, currY, "[SMC Struktur]: " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   color htfClr = (StringFind(g_htfMacroStr, "BULLISH") >= 0) ? C'74,222,128' : ((StringFind(g_htfMacroStr, "BEARISH") >= 0) ? C'248,113,113' : C'251,191,36');
   string htfText = InpUseHTFFilter ? g_htfMacroStr : "FILTER OFF";
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", panelX + 12, currY + 14, "[Macro H1]    : " + htfText, htfClr, 7, "Segoe UI Bold");

   string rangeStr = (g_smcAnalysis.isDiscount ? "DISKON (" : "PREMIUM (") + DoubleToString(g_smcAnalysis.discountPercent, 1) + "%)";
   if (currentFibo.isValid) rangeStr = rangeStr + " | GP: " + DoubleToString(currentFibo.level618, 2);
   CreateOrUpdateText("VIKAR_HUD_PILAR2", panelX + 12, currY + 28, "[Dealing Range]: " + rangeStr, (g_smcAnalysis.isDiscount ? C'74,222,128' : C'248,113,113'), 7, "Segoe UI");

   string patStr = g_chartPattern.isValid ? (g_chartPattern.patternName + " [" + DoubleToString(g_chartPattern.score, 0) + "p]") : "Scanning Geometri...";
   color patClr = g_chartPattern.isValid ? (g_chartPattern.isBullish ? C'74,222,128' : C'248,113,113') : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_CHART_PAT", panelX + 12, currY + 42, "[Pola Chart]  : " + patStr, patClr, 7, "Segoe UI Bold");

   string candleStr = g_candleAnalysis.patternName;
   if (g_candleAnalysis.score > 0) candleStr = candleStr + " [Skor: " + DoubleToString(g_candleAnalysis.score, 0) + "/100]";
   color candleClr = g_candleAnalysis.isHighQuality ? C'251,191,36' : C'203,213,225';
   CreateOrUpdateText("VIKAR_HUD_PILAR3", panelX + 12, currY + 56, "[Pola Lilin]  : " + candleStr, candleClr, 7, "Segoe UI");

   double ema125Val = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   string emaTrendStr = (Close[1] > ema125Val) ? "BULLISH (Di Atas 125)" : "BEARISH (Di Bawah 125)";
   CreateOrUpdateText("VIKAR_HUD_PILAR4", panelX + 12, currY + 70, "[Triple EMA]  : " + emaTrendStr + " | Ribbon 8/21", C'232,121,249', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_PILAR5", panelX + 12, currY + 84, "[S/R Pivot]   : P: " + DoubleToString(currentPivot.P, 2) + " [R1: " + DoubleToString(currentPivot.R1, 2) + " | S1: " + DoubleToString(currentPivot.S1, 2) + "]", C'148,163,184', 7, "Segoe UI");

   // Baris VSA Footprint
   string vsaDisplay = InpUseVSA ? (g_lastScoreResult.vsaStatus != "" ? g_lastScoreResult.vsaStatus : "Normal Volume") : "VSA: OFF";
   color vsaClr = (StringFind(vsaDisplay, "CLIMAX") >= 0) ? C'74,222,128' : ((StringFind(vsaDisplay, "NO-SUPPLY") >= 0) ? C'56,189,248' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_VSA", panelX + 12, currY + 98, "[VSA Footprint]: " + vsaDisplay, vsaClr, 7, "Segoe UI Bold");

   // Baris Circuit Guard
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
   currY += 130;

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
}

//+------------------------------------------------------------------+
//| ON INIT                                                          |
//+------------------------------------------------------------------+
int OnInit()
{
   g_panelX = InpDashboardX;
   g_panelY = InpDashboardY;

   g_gvStartTimeKey = "VIKAR_MT4_START_TIME_" + IntegerToString(InpMagicNumber);
   g_gvStartBalKey  = "VIKAR_MT4_START_BAL_"  + IntegerToString(InpMagicNumber);

   if (InpResetStatsOnStart || !GlobalVariableCheck(g_gvStartTimeKey))
   {
      g_eaStartTime      = TimeCurrent();
      g_eaInitialBalance = AccountBalance();
      GlobalVariableSet(g_gvStartTimeKey, (double)g_eaStartTime);
      GlobalVariableSet(g_gvStartBalKey,  g_eaInitialBalance);
   }
   else
   {
      g_eaStartTime      = (datetime)GlobalVariableGet(g_gvStartTimeKey);
      g_eaInitialBalance = GlobalVariableGet(g_gvStartBalKey);
   }

   double qpMinLot = MarketInfo(Symbol(), MODE_MINLOT);
   Print("=== VIKAR EA 4-PILLAR PRO MT4 (QUICKPRO EDITION) INITIALIZED ===");
   Print("Aset: ", Symbol(), " | TF: M", Period(), " | Magic: ", InpMagicNumber, " | QuickPro Min Lot: ", qpMinLot);
   Print("Start Time: ", TimeToStr(g_eaStartTime, TIME_DATE|TIME_MINUTES), " | Start Modal: $", DoubleToString(g_eaInitialBalance, 2));

   UpdateDailyPivots();
   UpdateDashboard();
   return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| ON DEINIT                                                        |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   DestroyDashboardGUI();
   CleanSMCObjects();
   Comment("");
}

//+------------------------------------------------------------------+
//| ON TICK                                                          |
//+------------------------------------------------------------------+
void OnTick()
{
   // 1. Kelola Posisi Aktif
   ManageActiveTrades();

   // 2. Tampilkan Dashboard HUD
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

   // 3. Hanya Cari Sinyal Saat Lilin Baru Selesai
   if (!IsNewBar()) return;

   // 3.1 Periksa Proteksi Circuit Breaker
   if (!CheckCircuitBreakers()) return;

   // 3.2 Proteksi Akhir Pekan (Friday Weekend Guard)
   if (InpUseFridayGuard)
   {
      MqlDateTime dtFriday;
      TimeToStruct(TimeCurrent(), dtFriday);
      if (dtFriday.day_of_week == 5 && dtFriday.hour >= InpFridayCloseHour)
      {
         int total = OrdersTotal();
         for (int fPos = total - 1; fPos >= 0; fPos--)
         {
            if (OrderSelect(fPos, SELECT_BY_POS, MODE_TRADES))
            {
               if (OrderSymbol() == Symbol() && OrderMagicNumber() == InpMagicNumber)
               {
                  if (OrderType() == OP_BUY) OrderClose(OrderTicket(), OrderLots(), Bid, InpDeviation, clrGold);
                  else if (OrderType() == OP_SELL) OrderClose(OrderTicket(), OrderLots(), Ask, InpDeviation, clrGold);
                  Print("[FRIDAY WEEKEND GUARD MT4] Menutup posisi #", OrderTicket(), " jelang akhir pekan demi keamanan modal!");
               }
            }
         }
         g_lastSignalType = "FRIDAY WEEKEND GUARD: PASAR JUMAT MALAM (ANTI-GAP)";
         return;
      }
   }

   // 4. Periksa Filter Spread
   double spreadPips = PriceToPips(Ask - Bid);
   if (spreadPips > InpMaxSpreadPips)
   {
      g_lastSignalType = "SPREAD MELEBIHI BATAS (" + DoubleToString(spreadPips, 1) + " pips)";
      return;
   }

   // 5. Periksa Sesi Waktu Trading
   if (InpUseSessionFilter)
   {
      MqlDateTime dt;
      TimeToStruct(TimeCurrent(), dt);
      if (dt.hour < InpSessionStartHour || dt.hour >= InpSessionEndHour)
      {
         g_lastSignalType = "DILUAR SESI TRADING (" + IntegerToString(dt.hour) + ":00)";
         return;
      }
   }

   // 6. Jalankan Evaluasi Sinyal
   CheckTradeSignal();
}

//+------------------------------------------------------------------+
//| CHART EVENT (INTERAKTIF DRAG & DROP DASHBOARD MT4)               |
//+------------------------------------------------------------------+
void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
{
   if (!InpShowDashboard) return;

   if (id == CHARTEVENT_CLICK)
   {
      int clickX = (int)lparam;
      int clickY = (int)dparam;

      if (clickX >= (g_panelX + g_panelW - 85) && clickX <= (g_panelX + g_panelW) &&
          clickY >= g_panelY && clickY <= (g_panelY + 34))
      {
         // Toggle drag state
         g_isDragging = !g_isDragging;
         if (g_isDragging)
         {
            g_dragOffsetX = clickX - g_panelX;
            g_dragOffsetY = clickY - g_panelY;
            CreateOrUpdateText("VIKAR_HUD_HDR_DRAG", g_panelX + g_panelW - 74, g_panelY + 9, "[ LEPAS ]", C'251,191,36', 8, "Segoe UI Bold");
         }
         else
         {
            CreateOrUpdateText("VIKAR_HUD_HDR_DRAG", g_panelX + g_panelW - 74, g_panelY + 9, "[ :: GESER ]", C'186,230,253', 8, "Segoe UI Bold");
         }
         ChartRedraw();
      }
      else if (g_isDragging)
      {
         g_panelX = MathMax(5, clickX - g_dragOffsetX);
         g_panelY = MathMax(5, clickY - g_dragOffsetY);
         UpdateDashboard();
         ChartRedraw();
      }
   }
}
//+------------------------------------------------------------------+
'''

with open(r'e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4', 'w', encoding='utf-8') as f:
    f.write(mql4_code)

print('VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4 successfully generated!')
print('File size:', len(mql4_code), 'bytes')
