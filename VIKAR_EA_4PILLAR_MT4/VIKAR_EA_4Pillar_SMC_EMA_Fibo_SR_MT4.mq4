//+------------------------------------------------------------------+
//|                          VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4|
//|        Copyright 2026, Vikar Institutional 4-Pillar Strategy     |
//|               SMC Core • S/R Pivots • Triple EMA • Fibonacci      |
//|                    (MetaTrader 4 - QuickPro Edition)             |
//+------------------------------------------------------------------+
#property copyright "Vikar Institutional 4-Pillar Trading Strategy"
#property link      "https://www.tradingview.com"
#property version   "4.10"
#property strict
#property description "Robot Trading MT4 Institusional 4 Pilar Terpadu (v4.10 Dual M15/M5 POI Stalker Edition)"
#property description "1. SMC Core, Order Block, FVG, VSA Footprint & Multi-Confluence Engine"
#property description "2. Self-Healing AI Pattern Matrix, Market Regime Classifier & News Shield"
#property description "3. Dual-Timeframe M15 & M5 POI Stalker, M1 Micro-Sniper Timing, Milestone Ratchet"

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
   TP_TYPE_FIXED_PIPS,    // Target Jarak Statis Pips (Default: 150 Pips)
   TP_TYPE_RISK_REWARD,   // Rasio Risk-to-Reward (1 : 1.5 / 1 : 2 / 1 : 3)
   TP_TYPE_FIBO_EXT,      // Target Ekstensi Fibonacci (-0.272 & -0.618)
   TP_TYPE_PIVOT_LEVEL,   // Target Level Pivot Statis Terdekat (R1/R2 atau S1/S2)
   TP_TYPE_FIXED_POINTS   // Target Jarak Statis (Points)
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

enum ENUM_MARKET_REGIME
{
   REGIME_STRONG_TREND,     // Tren Sangat Kuat (CI < 38.2) - Momentum Breakout Ideal
   REGIME_NORMAL,           // Tren Normal / Sehat (38.2 <= CI <= 61.8) - 4-Pillar Sniper Standard
   REGIME_CHOPPY_SIDEWAYS   // Sideways Sempit / Kompresi (CI > 61.8) - Bahaya Fakeout Tinggi!
};

enum ENUM_HTF_BIAS
{
   HTF_BIAS_NEUTRAL,
   HTF_BIAS_BULLISH,
   HTF_BIAS_BEARISH
};

enum ENUM_TREND_ALIGNMENT
{
   TREND_ALIGN_M5_BASELINE,        // 1. M5 EMA 125 Baseline Saja (Standar)
   TREND_ALIGN_TRIPLE_EMA_STACK,   // 2. Triple EMA Stack (8 > 21 > 125 untuk BUY, 8 < 21 < 125 untuk SELL)
   TREND_ALIGN_DUAL_M15_M5,        // 3. Dual Timeframe M15 + M5 Alignment (Rekomendasi Institusional Pro)
   TREND_ALIGN_MACRO_H1_M5         // 4. Macro H1 + M5 Alignment (Swing Trend)
};

//+------------------------------------------------------------------+
//| INPUT PARAMETERS USER (KOMPATIBILITAS QUICKPRO MT4 - SNIPER $20) |
//+------------------------------------------------------------------+
//--- 1. MANAJEMEN LOT & RISIKO MODAL ---
extern string       sec1                   = "=== 1. MANAJEMEN LOT & RISIKO MODAL ===";
extern ENUM_LOT_TYPE InpLotType            = LOT_TYPE_FIXED;        // Model Lot (Default: Fixed Lot 0.01 - Standar Akun $20 QuickPro)
extern double        InpRiskPercent        = 1.0;                   // Risiko per Transaksi (% Modal, Jika Mode Risk %)
extern double        InpFixedLot           = 0.01;                  // Ukuran Lot Tetap (0.01 Lot - Aman untuk Modal $20)
extern double        InpMinLot             = 0.00;                  // Batas Bawah Lot (0.0 = Auto Deteksi Minimal Broker QuickPro)
extern double        InpMaxLot             = 0.05;                  // Batas Maksimal Lot (Safeguard Anti-Lot Besar)
extern int           InpMaxOpenPositions   = 1;                     // Maksimal Posisi Aktif Bersamaan (1 = Anti-Hedging)
extern int           InpSignalCooldownBars = 3;                     // Jeda Minimal Lilin Antar Sinyal (Bars)
extern int           InpMagicNumber        = 777104;                // Magic Number Unik EA MT4
extern string        InpTradeComment       = "VIKAR-QP-MT4";        // Komentar Identitas Transaksi
extern int           InpDeviation          = 15;                    // Toleransi Slippage (Points)

//--- 2. TARGET STOP LOSS, TAKE PROFIT & EXIT STRATEGY ---
extern string       sec2                   = "=== 2. TARGET STOP LOSS, TAKE PROFIT & EXIT STRATEGY ===";
extern ENUM_SL_TYPE  InpSLType             = SL_TYPE_SWING_FIBO;    // Metode Penempatan Stop Loss
extern double        InpSLBufferAtrMult    = 1.2;                   // Buffer Pengaman SL (x Nilai ATR 14) [v4.20: 1.2x ATR aman]
extern double        InpMinSLPips          = 50.0;                  // Batas Minimum Jarak SL (Pips) [v4.20: Min 50 pips]
extern double        InpMaxSLPips          = 55.0;                  // Batas Maksimal Jarak SL (Pips) [v4.20: Maks 55 pips]
extern double        InpFixedSLPips        = 50.0;                  // Jarak SL Statis (Jika Mode Fixed Pips)
extern ENUM_TP_TYPE  InpTPType             = TP_TYPE_FIXED_PIPS;    // Metode Penentuan Target Take Profit (Default: Fixed 150 Pips)
extern double        InpFixedTPPips        = 150.0;                 // Target Jarak TP Statis (Pips) [Default: 150 Pips]
extern double        InpRiskRewardRatio    = 2.2;                   // Rasio Risk to Reward [v3.71: 1.8→2.2 untuk avg win > avg loss]
extern double        InpFixedTPPoints      = 1500.0;                // Target Jarak TP Statis (Points) [1500 Points = 150 Pips]

// --- Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin) ---
extern bool          InpUseBreakeven       = true;                  // Aktifkan Auto-Breakeven / SL+
extern ENUM_BE_MODE  InpBreakevenMode      = BE_MODE_PIPS;          // Model Pemicu Auto-BE
extern double        InpBreakevenTriggerPips= 6.0;                  // Jarak Profit Memicu BE [v3.71: 8→6 pips, lebih cepat aman]
extern double        InpBreakevenRRTrigger = 1.0;                   // Pemicu BE Saat Profit Mencapai R:R
extern double        InpBreakevenLockPips  = 3.0;                   // Pips Terkunci Saat SL+ [v3.71: 5→3 pips, lebih agresif]
extern bool          InpUseTrailingEMA21   = true;                  // Trailing Stop Dinamis Mengikuti EMA 21
extern double        InpTrailingBufferPips = 4.0;                   // Buffer Trailing dari EMA 21 [v3.71: 5→4]

// --- Dynamic Trailing Stop ---
extern bool          InpUseCandleTrailing  = true;                  // Trailing Naik Mengikuti Low/High Lilin
extern double        InpCandleTrailBufferPoints = 20.0;             // Buffer di Bawah Ekor Lilin [v3.71: 30→20]
extern bool          InpUsePointsTrailing  = true;                  // Trailing Stop Dinamis Berdasarkan Jarak Points
extern double        InpTrailingStartPoints= 80.0;                  // Pemicu Trailing Aktif [v3.71: 120→80 points, lebih cepat]
extern double        InpTrailingDistPoints = 60.0;                  // Jarak SL di Belakang Harga [v3.71: 80→60 points]
extern double        InpTrailingStepPoints = 10.0;                  // Langkah Geser SL [v3.71: 15→10 points]

// --- Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner) ---
extern bool          InpUsePartialClose    = true;                  // Aktifkan Partial Take Profit (Amankan 50% di TP1)
extern double        InpPartialClosePercent= 50.0;                  // Persentase Lot Ditutup di TP1 (Default: 50%)
extern ENUM_BE_MODE  InpPartialTriggerMode = BE_MODE_PIPS;          // Model Pemicu TP1 (Pips / Risk-Reward)
extern double        InpPartialTriggerPips = 14.0;                  // Jarak Profit Pemicu TP1 (14.0 Pips = 140 Point)
extern double        InpPartialRRTrigger   = 1.5;                   // Pemicu TP1 Saat Mencapai R:R
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
//--- 2.5 PROTEKSI POSISI MACET (STAGNANT TRADE TIME-EXIT v2.60) ---
extern string       sec25                  = "=== 2.5 STAGNANT TRADE TIME-EXIT (v2.60) ===";
extern bool          InpUseTimeBasedExit        = true;             // Tutup Otomatis Posisi yang Mengambang Terlalu Lama
extern int           InpMaxTradeDurationHours   = 6;                // Batas Maksimal Durasi Posisi (Jam, e.g. 6 Jam)
extern double        InpMinProfitToTimeExitPips = 0.0;              // Minimal Profit (Pips) untuk Time-Exit (0.0 = Impas / BE)

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
extern double        InpMinConfluenceScore = 75.0;                  // Skor Minimal Eksekusi (75.0 = Preset SNIPER Grade A+ Modal $20)

//--- 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ---
extern string       sec32                  = "=== 3.2 MESIN MOMENTUM BREAKOUT & EXPANSION ===";
extern bool          InpAllowMomentumBreakout = false;              // Aktifkan Eksekusi Momentum Breakout (Default false: Anti Beli di Pucuk)
extern double        InpBreakoutAtrMult       = 1.0;                // Minimal Ukuran Lilin Breakout (x Nilai ATR 14)
extern bool          InpBreakoutRequireVSA    = true;               // Wajib Didukung Lonjakan Volume VSA (>= 1.3x)
extern bool          InpBreakoutRequireBOS    = true;               // Wajib Menembus Swing High/Low (Konfirmasi BOS)

//--- 3.3 MESIN SEKUENSIAL SMC SNIPER (SWEEP -> CHOCH -> FVG RETEST) ---
extern string       sec33                  = "=== 3.3 MESIN SEKUENSIAL SMC SNIPER ===";
extern bool          InpUseSequentialSMCSniper= true;               // Aktifkan Setup Sekuensial: Sweep -> CHoCH -> FVG Retest
extern int           InpMaxBarsSweepToCHoCH   = 10;                 // Batas Maks Lilin dari Sweep ke CHoCH
extern int           InpMaxBarsCHoCHToRetest  = 15;                 // Batas Maks Lilin dari CHoCH ke Retest FVG
extern double        InpSniperMinRR           = 3.0;                // Target Minimum Risk-to-Reward (RR) Sniper (1:3+)
extern double        InpSniperSLBufferPips    = 2.0;                // Buffer SL Di Balik Jarum Sweep (Pips)
extern bool          InpSniperEnterAt50FVG    = true;               // Entry Presisi di 50% FVG (false = Ujung FVG)

//--- 3.4 MESIN PRO TREND PULLBACK SCALPER (v4.20 INSTITUSIONAL) ---
extern string             sec34                       = "=== 3.4 PRO TREND PULLBACK SCALPER (v4.20) ===";
extern bool               InpEnableProPullbackScalper = true;                  // Aktifkan Mesin Pro Pullback Scalper Institusional
extern ENUM_TREND_ALIGNMENT InpTrendAlignment         = TREND_ALIGN_DUAL_M15_M5;// Hierarki Trend Dominan (M15+M5 Rekomendasi Pro)
extern bool               InpStrictTrendOnly          = true;                  // Kunci Arah: Wajib 100% Mengikuti Trend (Anti-Melawan Trend)
extern bool               InpBlockCounterTrendCHoCH   = true;                  // Blokir CHoCH Kontra-Trend (Alihkan ke Mode Siaga Pullback)
extern int                InpMinPullbackConfluences   = 2;                     // Minimal Konfluensi (Ribbon, Fibo GP, FVG, POI, Sweep)
extern bool               InpRequireVSAExhaustion     = true;                  // Wajib Konfirmasi Volume Kering (No-Supply / No-Demand)
extern bool               InpFastScalpTP1AtSwing      = true;                  // TP1 Otomatis di Pucuk Swing Terdekat (Amankan Profit Kilat)


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
extern bool          InpUseHTFFilter       = false;                 // Aktifkan Filter Macro Trend Higher Timeframe (H1)
extern int           InpHTFTimeframe       = PERIOD_H1;             // Timeframe Macro Trend (Default: H1 = 60)
extern int           InpHTFTrendEMA        = 125;                   // HTF Trend Baseline Period (Putih 125)
extern bool          InpHTFRequireRibbon   = true;                  // Wajib Konfirmasi HTF Ribbon (EMA 8 > EMA 21)

//--- 5.1 SMART PULLBACK QUALITY ENGINE (v3.70) ---
extern string       sec51                  = "=== 5.1 SMART PULLBACK QUALITY ENGINE (v3.70) ===";
extern bool          InpUsePullbackScore   = true;   // Aktifkan Penilaian Kualitas Pullback (Presisi Tinggi)
extern double        InpMinPullbackScore   = 60.0;   // Skor Minimal Pullback Valid (0-100, Default 60)
extern bool          InpRequireImpulsePre  = true;   // [SMART v3.80] Wajib Ada Displacement/Impulse Sebelum Pullback (Anti-Chop)
extern double        InpImpulseAtrMult     = 0.8;    // Minimal Kekuatan Impulse Pembentuk Swing (0.8x ATR)
extern bool          InpRequireMultiBarPB  = false;  // Wajib 2+ Bar Sentuh Ribbon (Anti Single-Spike Pullback)
extern bool          InpUsePBVolumeFilter  = true;   // Bonus Skor Jika Volume Pullback < Volume Impulse (No-Demand)

//--- 5.2 MULTI-TIMEFRAME M1 MICRO-SNIPER TIMING (v3.90) ---
extern string       sec52                  = "=== 5.2 MULTI-TIMEFRAME M1 MICRO-SNIPER (v3.90) ===";
extern bool          InpUseMTFM1Engine      = true;   // Aktifkan Mesin Konfirmasi Sub-Struktur M1
extern bool          InpRequireM1StrictGate = false;  // Wajib Konfirmasi M1 (false = Bonus Konfluensi + SL Presisi)
extern int           InpM1LookbackBars      = 60;     // Jendela Pemindaian Bar M1 (60 Bar = 1 Jam)
extern double        InpM1DispAtrMult       = 0.7;    // Minimal Displacement Lilin M1 (x ATR M1)
extern double        InpM1BufferPips        = 1.5;    // Toleransi Jarak Retest Zona M1 (Pips)
extern bool          InpM1UseTightSL        = false;  // Gunakan Stop Loss Presisi di Balik Swing M1 (Default false: Anti Wick-Hunt)
extern double        InpM1MinSLPips         = 10.0;   // Batas Minimum SL Presisi M1 (Pips)

//--- 5.3 TOP-DOWN M15 & M5 POI STALKER ENGINE (v4.10) ---
enum ENUM_POI_SCAN_MODE
{
   POI_SCAN_DUAL_M15_M5,   // Scan Keduanya: M15 & M5 Sekaligus (Multi-Layer POI - Rekomendasi)
   POI_SCAN_M15_ONLY,      // Hanya Timeframe M15
   POI_SCAN_M5_ONLY        // Hanya Timeframe M5
};

extern string             sec53                  = "=== 5.3 TOP-DOWN M15 & M5 POI STALKER (v4.10) ===";
extern bool               InpUsePOIStalker       = true;                 // Aktifkan Pemindaian POI Institusional (OB & Likuiditas)
extern ENUM_POI_SCAN_MODE InpPOIScanMode         = POI_SCAN_DUAL_M15_M5; // Mode Pemindaian POI (Dual M15+M5 / M15 Only / M5 Only)
extern bool               InpRequirePOIZone      = false;                // Wajib Sedang di Zona POI (false = Bonus Konfluensi +25 Poin)
extern int                InpPOILookbackBars     = 100;                  // Jendela Bar yang Dipindai (100 Bar)
extern double             InpPOIDispAtrMult      = 1.2;                  // Minimal Kekuatan Impulse Pembentuk OB (1.2x ATR)
extern bool               InpPOIDetectLiquidity  = true;                 // Deteksi Equal Highs (BSL) / Equal Lows (SSL)
extern double             InpPOIEqTolerancePips  = 2.5;                  // Toleransi Kembar Equal High/Low (Pips)
extern bool               InpDrawPOIVisuals      = true;                 // Gambar Kotak & Garis POI di Chart MT4
extern color              InpColorM15Demand      = C'20,60,40';          // Warna Kotak M15 Demand POI (Dark Emerald)
extern color              InpColorM15Supply      = C'60,20,30';          // Warna Kotak M15 Supply POI (Dark Crimson)
extern color              InpColorM5Demand       = C'15,75,45';          // Warna Kotak M5 Demand POI (Medium Forest)
extern color              InpColorM5Supply       = C'75,20,35';          // Warna Kotak M5 Supply POI (Medium Wine)
extern color              InpColorLiquidity      = clrGold;              // Warna Garis Likuiditas BSL/SSL
extern bool               InpRequireLTFRejection = true;                 // Stalking Mode: Wajib Rejection/Konfirmasi Lilin di LTF

#define InpUseM15POIStalker   InpUsePOIStalker
#define InpRequireM15POIZone  InpRequirePOIZone
#define InpM15LookbackBars    InpPOILookbackBars
#define InpM15OBDispAtrMult   InpPOIDispAtrMult
#define InpM15DetectLiquidity InpPOIDetectLiquidity
#define InpM15EqTolerancePips InpPOIEqTolerancePips
#define InpDrawM15Visuals     InpDrawPOIVisuals
#define InpColorM15Liquidity  InpColorLiquidity


//--- 6. PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET ---
extern string       sec6                   = "=== 6. PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET ===";
extern bool          InpUseAutoFibo        = true;                  // Aktifkan Validasi Fibonacci Retracement
extern bool          InpRequireGoldenPocket= false;                 // Wajib Menguji Area Golden Pocket (false = Cukup Sentuh Ribbon EMA)
extern double        InpFiboGPMin          = 0.500;                 // Batas Atas Retracement Golden Pocket
extern double        InpFiboGPMid          = 0.618;                 // Rasio Emas Utama (Golden Ratio 61.8%)
extern double        InpFiboGPMax          = 0.786;                 // Batas Bawah Retracement Golden Pocket
extern bool          InpAutoCleanBrokenFibo= true;                  // Otomatis Bersihkan Fibo dari Chart Jika Level 100% / Struktur Ditembus
extern bool          InpInvalidateOnClose786 = false;               // Invalidasi Jika Lilin Ditutup Menembus 78.6% (Deep Pocket Jebol)


//--- 7. POLA KONFIRMASI CANDLESTICK REJECTION ---
extern string       sec7                   = "=== 7. POLA KONFIRMASI CANDLESTICK REJECTION ===";
extern bool          InpRequireCandleRejection = false;             // Wajib Pola Rejection Cerdas (Pin Bar, Engulfing, Star, Tweezer)
extern double        InpMinCandleScore         = 55.0;              // Skor Kualitas Lilin Minimal (0 - 100)
extern bool          InpUseHammerPinBar        = true;              // Pin Bar & Hammer Rejection (Ekor >= 60%)
extern bool          InpUseEngulfing           = true;              // Bullish & Bearish Engulfing Institusional
extern bool          InpUseMorningEveningStar  = true;              // Morning Star & Evening Star (3-Bar Reversal)
extern bool          InpUseTweezer             = true;              // Tweezer Tops & Tweezer Bottoms (Double Level Test)
extern bool          InpUseFVGRebound          = true;              // Fair Value Gap Mitigation Rebound
extern bool          InpUseThreeSoldiersCrows  = true;              // Three White Soldiers & Three Black Crows (Impulsive Push)
extern bool          InpUseHaramiInsideBar     = true;              // Harami & Inside Bar Compression Breakout
extern bool          InpUsePiercingDarkCloud   = true;              // Piercing Line & Dark Cloud Cover (>50% Penetration)
extern bool          InpUseDragonflyGravestone = true;              // Dragonfly Doji & Gravestone Doji Extreme Rejection
extern bool          InpUseInvertedHammerStar  = true;              // Inverted Hammer & Shooting Star Rejection
// Pola Baru v3.70
extern bool          InpUseWickSeries          = true;              // [NEW] Wick Rejection Series (2 bar berturut ekor kuat)
extern bool          InpUseMicroPullbackPin    = true;              // [NEW] Micro Pullback Pin Bar (body <20% tepat di EMA8)
extern bool          InpUseOutsideBarPB        = true;              // [NEW] Outside Bar Pullback (menelan ekor lawan di ribbon)


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
extern bool          InpUseShockGuard      = false;                 // Proteksi Lonjakan Volatilitas Berita (Shock Guard)
extern double        InpShockAtrMult       = 3.2;                   // Batas Abnormal Lonjakan Lilin Berita (x Nilai ATR)
extern int           InpShockCooldownBars  = 2;                     // Jeda Pengaman Lilin Pasca-Lonjakan Shock (Bars)
extern bool          InpCutOnEarlyInvalidation = true;              // Cut Dini Jika Terbentuk Lilin Menelan Order Block Acuan
extern double        InpMaxSpreadPips      = 4.5;                   // Batas Maksimal Spread Diizinkan (Pips)
extern bool          InpUseSessionFilter   = false;                 // Batasi Jam Trading (false = 24 Jam Auto Trade)
extern int           InpSessionStartHour   = 0;                     // Jam Mulai Trading
extern int           InpSessionEndHour     = 24;                    // Jam Selesai Trading

//--- 8.1 PROTEKSI AKUN & CIRCUIT BREAKER ---
extern string       sec81                  = "=== 8.1 PROTEKSI AKUN & CIRCUIT BREAKER ===";
extern bool          InpUseConsecutiveLossGuard = false;            // Jeda Anti-Overtrading Pasca-Loss Beruntun
extern int           InpMaxConsecutiveLosses    = 2;                // Batas Loss Berturut-turut Hari Ini (Default: 2)
extern int           InpCooldownHours           = 4;                // Durasi Istirahat Robot Pasca-Loss (Jam)
extern bool          InpUseDailyLossLimit       = false;            // Batasi Maksimal Kerugian Harian (% Modal)
extern double        InpMaxDailyLossPercent     = 2.5;              // Batas Maksimal Kerugian Harian (% Saldo Awal Hari Ini)

//--- 8.2 VOLUME SPREAD ANALYSIS (VSA INSTITUSIONAL) ---
extern string       sec82                  = "=== 8.2 VOLUME SPREAD ANALYSIS (VSA INSTITUSIONAL) ===";
extern bool          InpUseVSA                  = true;             // Aktifkan Analisis Volume Footprint Institusional
extern int           InpVSALookbackBars         = 20;               // Periode Rata-rata Volume Lilin Acuan (Bars)
extern double        InpVSAClimaxRatio          = 1.75;             // Batas Lonjakan Volume Climax / Absorption (x Rata-rata)
extern double        InpVSANoSupplyRatio        = 0.85;             // Batas Volume Kering / No-Supply Pullback (x Rata-rata)

//--- 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ---
extern string       sec83                  = "=== 8.3 PROTEKSI AKHIR PEKAN (FRIDAY WEEKEND GUARD) ===";
extern bool          InpUseFridayGuard          = false;            // Tutup Semua Posisi & Tolak Order Baru Jelang Weekend
extern int           InpFridayCloseHour         = 21;               // Jam Penutupan Posisi Jumat Malam (Server Time, 21:00)

//--- 8.4 MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE) ---
extern string       sec84                  = "=== 8.4 MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING) ===";
extern bool          InpUseSelfHealing          = true;             // Aktifkan Mesin Otopsi & Koreksi Diri Pasca-Loss
extern double        InpPenaltyConfluencePts    = 10.0;             // Penalti Ambang Skor Minimal Pasca-SL (+10 Poin)
extern int           InpQuarantinePatternBars   = 15;               // Durasi Karantina Pola Lilin Gagal (Bars)
extern double        InpAdaptiveSLBufferBoost   = 0.3;              // Tambahan Buffer ATR Pasca-Loss (x ATR)
extern int           InpAdaptiveBufferTrades    = 3;                // Jumlah Transaksi dengan Buffer Ekstra Pasca-SL
extern bool          InpAutopsyNotifyPush       = true;             // Kirim Laporan Otopsi Pasca-Loss ke Smartphone
//--- 8.5 REINFORCEMENT LEARNING & AI CANDLESTICK SHIELD (v3.40) ---
extern string       sec85                      = "=== 8.5 REINFORCEMENT LEARNING & AI CANDLESTICK SHIELD (v3.40) ===";
extern bool         InpUsePatternMatrix        = true;             // Aktifkan Memori Rapor & Pembelajaran Pola Mandiri
extern bool         InpUsePreTrainedBrain      = true;             // Bekali Otak Awal dari Hasil Audit 9 Bulan (Pre-Trained)
extern bool         InpFilterDojiCandles       = true;             // AI Shield: Tolak Entry Saat Candle Doji / Body Tipis (<22%)
extern bool         InpFilterExhaustionWicks   = true;             // AI Shield: Tolak Entry Saat Muncul Ekor Penolakan Lawan (>=45%)
extern bool         InpFilterOverextended      = true;             // AI Shield: Tolak Engulfing Terlalu Jauh dari EMA (>1.5x ATR)
extern bool         InpSaveBrainToDisk         = true;             // Simpan Memori Pembelajaran Permanen ke File Disk (Auto-Save)
extern int          InpMinTradesForPatternEval = 3;                // Minimal Transaksi Sebelum Evaluasi Pola
extern double       InpPatternBlacklistWinrate = 40.0;             // Ambang Batas Blacklist Mandiri (Winrate < 40%)
extern double       InpPatternBoostWinrate     = 70.0;             // Ambang Batas Boost Mandiri (Winrate > 70%)
extern double       InpPatternBoostScore       = 10.0;             // Bonus Skor Konfluensi untuk Pola Akurat
extern double       InpPatternPenaltyScore     = 15.0;             // Penalti Pengetatan Skor untuk Pola Lemah
extern bool         InpUseDirectionalLearning  = true;             // Proteksi Anti-Loss Berulang Searah (Directional Bias Learning)
extern double       InpDirectionalPenaltyScore = 10.0;             // Penalti Skor Tambahan untuk Arah yang Baru Saja Gagal
extern int          InpDirectionalPenaltyBars  = 12;               // Durasi Penalti Arah Gagal (Bars Lilin)
extern bool         InpUseHourlyLearning       = true;             // Hindari Jam Tertentu yang Rawan Loss Berulang

//--- 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ---
extern string       sec86                  = "=== 8.6 MARKET REGIME CLASSIFIER (CHOPPINESS INDEX v2.50) ===";
extern bool          InpUseRegimeFilter         = false;            // Aktifkan Sensor Cuaca Pasar (Trending vs Choppy)
extern int           InpChoppinessPeriod        = 14;               // Periode Perhitungan Choppiness Index (CI)
extern double        InpChoppyThreshold         = 61.8;             // Ambang Batas Pasar Choppy / Sideways (CI > 61.8)
extern double        InpTrendingThreshold       = 38.2;             // Ambang Batas Pasar Tren Kuat (CI < 38.2)
extern bool          InpBlockBreakoutInChoppy   = false;            // Blokir Momentum Breakout Saat Pasar Choppy
//--- 8.7 PRE-NEWS EVENT & SPREAD SPIKE SHIELD (v2.60) ---
extern string       sec87                  = "=== 8.7 PRE-NEWS EVENT SHIELD (v2.60) ===";
extern bool          InpUseNewsShield           = false;            // Aktifkan Sensor Antisipasi Berita Berdampak Tinggi
extern int           InpNewsMinsBefore          = 20;               // Waktu Pembekuan Sebelum Rilis Berita (Menit)
extern int           InpNewsMinsAfter           = 25;               // Waktu Pembekuan Sesudah Rilis Berita (Menit)
extern bool          InpAutoLockBEBeforeNews    = false;            // Otomatis Kunci SL+ pada Posisi Profit Jelang Berita
extern string        InpNewsReleaseHoursServer  = "15:30,21:00";    // Jam Rilis Berita AS Utama (Waktu Server Broker)
extern double        InpMaxSpreadSpikeMultiplier= 1.8;              // Batas Lonjakan Spread Dinamis (x InpMaxSpreadPips)

//--- 8.9 AUTONOMOUS NEURO-CALIBRATION & SELF-TUNING (v3.20) ---
extern string       sec89Calib            = "=== 8.9 AUTONOMOUS NEURO-CALIBRATION (v3.20) ===";
extern bool         InpUseAutoCalibration         = true;         // Aktifkan Kalibrasi Parameter Mandiri Real-Time (v3.20)
extern double       InpAutoTuningSensitivity      = 1.35;         // Sensitivitas Deteksi Volatilitas (ATR14 / ATR100)
extern int          InpCalibrationConsecLossMax   = 2;            // Pemicu Pengetatan Parameter Saat Loss Beruntun (Default: 2x)
extern double       InpAutoTuningMaxBufferMult    = 1.6;          // Batas Maksimal Ekspansi Buffer SL (x ATR)
extern double       InpAutoTuningScoreStep        = 5.0;          // Langkah Pengetatan Ambang Skor per Kejadian Loss

//--- 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ---
extern string       sec88                  = "=== 8.8 SENSOR KELELAHAN DIVERGENCE (v2.60) ===";
extern bool          InpUseDivergenceFilter     = true;             // Deteksi Divergensi RSI (Cegah Beli Pucuk / Jual Lembah)
extern int           InpRSIPeriod               = 14;               // Periode RSI untuk Deteksi Momentum
extern int           InpDivergenceLookbackBars  = 25;               // Jendela Pengujian Ayunan Puncak/Lembah RSI (Bars)
//--- 8.9 SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v3.80 SMART) ---
extern string       sec89                  = "=== 8.9 SENSOR KEKUATAN TREN: ADX FILTER (v3.80) ===";
extern bool          InpUseADXFilter            = true;             // [SMART v3.80] Blokir Entry Saat Pasar Tidur / Tanpa Arah (ADX Rendah)
extern int           InpADXPeriod               = 14;               // Periode Perhitungan ADX
extern double        InpMinADXThreshold         = 20.0;             // Ambang Batas Minimal ADX (20.0 Optimal M5)

//--- 8.10 SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v3.80 SMART) ---
extern string       sec810                 = "=== 8.10 SENSOR KEMIRINGAN EMA SLOPE (v3.80) ===";
extern bool          InpUseEMASlopeFilter       = true;             // [SMART v3.80] Blokir Entry Saat Garis EMA Datar / Kusut (Flat Sideways)
extern int           InpEMASlopeLookback        = 5;                // Jarak Lilin Pengujian Kemiringan EMA (Bars)
extern double        InpMinEMASlopePips         = 2.0;              // Ambang Batas Minimal Kenaikan/Penurunan EMA (2.0 Pips)

//--- 8.11 SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION (v2.70) ---
extern string       sec811                 = "=== 8.11 SENSOR VOLUME INSTITUSIONAL: VSA (v2.70) ===";
extern bool          InpUseVolumeFilter         = true;             // Wajibkan Lonjakan Volume Institusi pada Lilin Konfirmasi
extern int           InpVolumeMAPeriod          = 20;               // Periode Rata-Rata Volume Bergerak (Bars)
extern double        InpMinVolumeMultiplier     = 1.15;             // Minimal Rasio Volume Konfirmasi (x Rata-Rata 20 Bar)

//--- 8.12 BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70) ---
extern string       sec812                 = "=== 8.12 BATAS BAWAH VOLATILITAS: ATR FLOOR (v2.70) ===";
extern bool          InpUseMinATRFilter         = false;            // Blokir Entry Saat Rentang Gerak Pasar Terlalu Sempit
extern double        InpMinATRPips              = 12.0;             // Minimal Jarak ATR 14 dalam Pips (Anti-Pasar Mati)
//--- 8.13 PROP FIRM EQUITY GUARDIAN & KILL-SWITCH (v3.00) ---
extern string       sec813                 = "=== 8.13 PROP FIRM EQUITY GUARDIAN (v3.00) ===";
extern bool          InpUseEquityGuardian       = false;            // Aktifkan Pengaman Batas Drawdown Harian Ketat
extern double        InpMaxDailyEquityDDPct     = 4.0;              // Batas Maksimal Penurunan Equity Harian (%)
extern bool          InpLockTradingOnDDBreach   = false;            // Kunci Trading Otomatis Hingga Besok Jika Batas Tersentuh

//--- 8.14 ASYMMETRIC CONFIDENCE RISK ALLOCATOR (v3.00) ---
extern string       sec814                 = "=== 8.14 ASYMMETRIC RISK ALLOCATOR (v3.00) ===";
extern bool          InpUseAsymmetricLot        = true;             // Skalakan Lot Berdasarkan Kualitas Konfluensi (Kelly)
extern double        InpGradeABoostMultiplier   = 1.30;             // Pengali Lot untuk Setup Grade A+ (Skor >= 85)
extern double        InpGradeBPenaltyMultiplier = 0.70;             // Pengali Lot untuk Setup Standar (Skor 60-75)

//--- 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ---
extern string       sec815                 = "=== 8.15 LIQUIDITY SWEEP TRAP HUNTER (v3.00) ===";
extern bool          InpUseTrapHunter           = true;             // Eksekusi Reversal saat Bandar Menyapu Stop Loss Retail
extern double        InpMinSweepPips            = 4.0;              // Minimal Jarak Penembusan Palsu (Pips)
extern double        InpMaxSweepPips            = 30.0;             // Maksimal Jarak Penembusan Palsu (Pips)
extern double        InpMinRejectionWickPct     = 40.0;             // Minimal Panjang Ekor Penolakan Lilin (%)

//--- 8.16 PRO TRADER DISCIPLINE SUITE (v3.30) ---
extern string       sec816                 = "=== 8.16 PRO TRADER DISCIPLINE SUITE (v3.30) ===";
extern bool          InpUseDailyProfitLockdown  = false;             // Kunci Trading Hari Ini Jika Target Profit Harian Tercapai (false = Bebas Sesuai Backtest)
extern ENUM_PROFIT_TARGET_MODE InpDailyProfitTargetMode = PROFIT_TARGET_CURRENCY; // Model Target Profit Harian
extern double        InpDailyProfitTargetMoney  = 50.0;              // Target Profit Harian ($ USD)
extern double        InpDailyProfitTargetPercent= 2.0;               // Target Profit Harian (% Modal)
extern bool          InpUseRolloverGuard        = false;             // Bekukan Entry Selama Rollover Spread Melebar Tengah Malam
extern int           InpRolloverStartHour       = 23;                // Jam Mulai Rollover Server
extern int           InpRolloverStartMin        = 50;                // Menit Mulai Rollover Server (23:50)
extern int           InpRolloverEndHour         = 0;                 // Jam Selesai Rollover Server
extern int           InpRolloverEndMin          = 25;                // Menit Selesai Rollover Server (00:25)
extern bool          InpUseMaxDailyTrades       = false;             // Batasi Kuota Maksimal Transaksi per Hari (false = Bebas Sesuai Backtest)
extern int           InpMaxDailyTrades          = 25;                // Kuota Maksimal Transaksi per Hari (Jika Diaktifkan)
extern bool          InpUseMilestoneRatchet     = true;              // [SMART v3.80] Kunci Untung Bertingkat (+0.5R di 1R, +1.0R di 1.5R, +1.5R di 2R)
extern bool          InpTradeKillzonesOnly      = false;             // Hanya Trading di Sesi Institusional Paling Likuid (London & NY)
extern int           InpKillzoneLondonStart     = 9;                 // Jam Mulai London Killzone (Server Time)
extern int           InpKillzoneLondonEnd       = 13;                // Jam Selesai London Killzone (Server Time)
extern int           InpKillzoneNYStart         = 14;                // Jam Mulai New York Killzone (Server Time)
extern int           InpKillzoneNYEnd           = 20;                // Jam Selesai New York Killzone (Server Time)

//--- 8.17 ASISTEN TRADE MANUAL (AUTO SL/TP/BE/TRAILING UNTUK ORDER MANUAL) ---
extern string       sec817                  = "=== 8.17 ASISTEN TRADE MANUAL (AUTO SL / TP / TRAILING) ===";
extern bool          InpManageManualTrades  = true;   // Kelola Order Manual di Chart Ini (Magic Number = 0)
extern double        InpManualSLPips        = 50.0;   // Auto Stop Loss untuk Trade Manual (50 Pips Min, 55 Maks)
extern double        InpManualTPPips        = 150.0;  // Auto Take Profit untuk Trade Manual (Default: 150 Pips)
extern bool          InpManualAutoBE        = true;   // Auto SL+ Kunci Profit untuk Trade Manual
extern double        InpManualBETriggerPips = 8.0;    // Pemicu Auto-BE Trade Manual (Pips Profit)
extern double        InpManualBELockPips    = 5.0;    // Pips Keuntungan Terkunci saat SL+ Trade Manual
extern bool          InpManualTrailing      = true;   // Auto Trailing Stop Dinamis untuk Trade Manual (Selalu Aktif)
extern double        InpManualTrailingStart = 12.0;   // Pemicu Trailing Trade Manual Aktif (Pips Profit)
extern double        InpManualTrailingDist  = 8.0;    // Jarak Pengawalan SL di Belakang Harga (Pips)
extern double        InpManualTrailingStep  = 1.5;    // Langkah Geser SL per Kenaikan Harga (Pips)

//--- 9. ON-CHART VISUALIZER (AUTO-DRAW SMC, S&R PIVOTS & FIBONACCI) ---
extern string       sec9                   = "=== 9. ON-CHART VISUALIZER (SMC, S&R PIVOT & FIBO) ===";
extern bool          InpDrawSMCOnChart     = true;                  // Otomatis Gambar Kotak Order Block & FVG di MT4
extern color         InpColorBullishOB     = C'14,116,144';         // Warna Kotak Bullish Order Block (Base Demand)
extern color         InpColorBearishOB     = C'190,18,60';          // Warna Kotak Bearish Order Block (Supply Zone)
extern color         InpColorFVG           = C'217,119,6';          // Warna Kotak Fair Value Gap (FVG Imbalance)
extern bool          InpDrawStructureLines = true;                  // Gambar Garis & Label BOS, CHoCH, SSS, & IDM di MT4
extern color         InpColorBOS           = C'34,197,94';          // Warna Garis BOS (Break of Structure - Hijau)
extern color         InpColorCHoCH         = C'6,182,212';          // Warna Garis CHoCH (Change of Character - Cyan)
extern color         InpColorSSS           = C'236,72,153';         // Warna Garis SSS (Smart Money Sweep - Pink Neon)
extern color         InpColorIDM           = C'250,204,21';         // Warna Garis IDM (Inducement - Kuning Emas)
extern bool          InpDrawPivotsOnChart  = true;                  // Gambar Garis S&R Daily Pivot (P, R1-R3, S1-S3)
extern color         InpColorPivotP        = C'100,116,139';        // Warna Garis Daily Pivot Sentral (P)
extern color         InpColorPivotRes      = C'239,68,68';          // Warna Garis Resisten (R1, R2, R3)
extern color         InpColorPivotSup      = C'16,185,129';         // Warna Garis Support (S1, S2, S3)
extern bool          InpDrawFiboOnChart    = true;                  // Gambar Garis & Zona Fibo Golden Pocket (50%, 61.8%, 78.6%)
extern color         InpColorFiboGP        = C'245,158,11';         // Warna Level Emas Fibo 61.8% (Golden Pocket)
extern bool          InpDrawSwingLines     = true;                  // Gambar Garis Struktur Ayunan (Kandel Lama ke Kandel Baru)
extern double        InpMinSwingATRMult    = 1.2;                   // Filter Jarak Minimal Ayunan (x ATR) Biar Tidak Kebanyakan Garis
extern int           InpMaxSwingLegs       = 4;                     // Maksimal Garis Ayunan Ditampilkan (Maks 3-5 Biar Rapi)
extern color         InpColorSwingUp       = C'34,197,94';          // Warna Garis Ayunan Naik (Bullish Leg - Hijau)
extern color         InpColorSwingDown     = C'239,68,68';          // Warna Garis Ayunan Turun (Bearish Leg - Merah)


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
extern bool          InpNotifyOnClose         = true;               // Notifikasi Saat Auto Cut Profit / Posisi Ditutup
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

struct M1SniperResult
{
   bool     isValid;
   bool     isBuyReady;
   bool     isSellReady;
   bool     hasDemandOB;
   bool     hasSupplyOB;
   double   demandTop;
   double   demandBottom;
   double   supplyTop;
   double   supplyBottom;
   bool     isCHoCH;
   bool     isRejection;
   double   bestSLPrice;
   double   score;
   string   statusText;
   datetime lastUpdated;
};
M1SniperResult g_m1Sniper;

struct M15POIZone
{
   bool              isValid;
   ENUM_TIMEFRAMES   tf;
   string            tfName;          // "M15" atau "M5"
   bool              isDemand;        // true = Demand (Buy), false = Supply (Sell)
   double            top;
   double            bottom;
   datetime          time;
   double            displacement;
   bool              isMitigated;
};

struct M15LiquidityPool
{
   bool              isValid;
   ENUM_TIMEFRAMES   tf;
   string            tfName;          // "M15" atau "M5"
   bool              isBuySide;       // true = BSL (Equal Highs), false = SSL (Equal Lows)
   double            priceLevel;
   datetime          time1;
   datetime          time2;
   bool              isSwept;
};

struct M15StalkerResult
{
   bool              isValid;
   M15POIZone        demandZone;      // M15 Demand Zone
   M15POIZone        supplyZone;      // M15 Supply Zone
   M15LiquidityPool  bslPool;         // M15 BSL
   M15LiquidityPool  sslPool;         // M15 SSL

   M15POIZone        m5DemandZone;    // M5 Demand Zone
   M15POIZone        m5SupplyZone;    // M5 Supply Zone
   M15LiquidityPool  m5BslPool;       // M5 BSL
   M15LiquidityPool  m5SslPool;       // M5 SSL

   bool              isInDemandPOI;       // Price is inside or reacting to M15/M5 Demand
   bool              isInSupplyPOI;       // Price is inside or reacting to M15/M5 Supply
   bool              hasApproachedDemand; // Stalking mode
   bool              hasApproachedSupply; // Stalking mode
   string            activeDemandTF;      // "M15", "M5", atau "DUAL M15+M5"
   string            activeSupplyTF;      // "M15", "M5", atau "DUAL M15+M5"
   double            demandDistPips;
   double            supplyDistPips;
   double            bestSLBuy;           // Tight SL level below Demand
   double            bestSLSell;          // Tight SL level above Supply
   double            score;               // Confluence score contribution
   string            statusText;
   datetime          lastUpdated;
};
M15StalkerResult g_m15Stalker;

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

   // Visual Structure Elements (BOS, CHoCH, SSS, IDM)
   double              bosPrice;
   datetime            bosTimeStart;
   datetime            bosTimeEnd;
   bool                isBullishBOS;
   datetime            bosBreakTime;     // Waktu candle tertutup yang menembus & membentuk BOS
   double              bosBreakPrice;    // Harga ekstrem (High/Low) candle penembus BOS
   bool                bosIsConfirmed;   // True jika sudah ada candle tertutup yang membentuk BOS

   double              chochPrice;
   datetime            chochTimeStart;
   datetime            chochTimeEnd;
   bool                isBullishCHoCH;
   datetime            chochBreakTime;   // Waktu candle tertutup yang menembus & membentuk CHoCH
   double              chochBreakPrice;  // Harga ekstrem (High/Low) candle penembus CHoCH
   bool                chochIsConfirmed; // True jika sudah ada candle tertutup yang membentuk CHoCH

   double              sweepPriceLevel;
   datetime            sweepTimeStart;
   datetime            sweepTimeEnd;
   bool                isBullishSweep;

   bool                hasIDM;
   double              idmPrice;
   datetime            idmTime;
   bool                isBullishIDM;
};

struct SMCSwing
{
   datetime time;
   double   price;
   bool     isHigh;
   bool     isSwept;
};

struct ValidStructureSwing
{
   datetime time;
   double   price;
   bool     isHigh;
   string   label;
};

#define MAX_VALID_SWINGS 8
ValidStructureSwing g_validSwings[MAX_VALID_SWINGS];
int                 g_validSwingCount = 0;

enum ENUM_SNIPER_STAGE
{
   SNIPER_STAGE_IDLE            = 0, // Standby mencari Liquidity Sweep
   SNIPER_STAGE_SWEEP_DETECTED  = 1, // Sweep Swing High/Low terdeteksi (Jarum ekor)
   SNIPER_STAGE_CHOCH_CONFIRMED = 2, // CHoCH pembalikan terkonfirmasi closed candle
   SNIPER_STAGE_FVG_ARMED       = 3, // Fair Value Gap terbentuk & siap diuji
   SNIPER_STAGE_READY_TO_FIRE   = 4  // Harga sedang retest ke zona FVG (Trigger Aktif)
};

struct SMCSniperTracker
{
   ENUM_SNIPER_STAGE stage;
   bool              isBullish;
   datetime          sweepTime;
   int               sweepBarIndex;
   double            sweepLevel;      // Level swing yang disweep
   double            sweepExtreme;    // Wick ekstrem (High/Low) dari lilin sweep
   datetime          chochTime;
   int               chochBarIndex;
   double            chochLevel;      // Level swing penembus CHoCH
   bool              hasFVG;
   double            fvgTop;
   double            fvgBottom;
   double            fvgMid;
   datetime          fvgTime;
   int               fvgBarIndex;
   double            entryPrice;
   double            recommendedSL;
   double            recommendedTP1;  // Minimal 1:3 RR
   double            recommendedTP2;
   string            statusText;
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
   bool   isBullish;
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
int            g_panelH           = 490;
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
SMCSniperTracker      g_sniperBUY;
SMCSniperTracker      g_sniperSELL;

struct ProPullbackResult
{
   bool   isValid;
   int    confluenceCount;
   string confluencesStr;
   double suggestedSL;
   double suggestedTP;
   double pullbackScore;
   bool   isVSAOk;
};

ProPullbackResult    g_proPullbackBUY;
ProPullbackResult    g_proPullbackSELL;
ENUM_HTF_BIAS        g_dominantTrendBias = HTF_BIAS_NEUTRAL;
string               g_dominantTrendStr  = "NEUTRAL (STANDBY)";

bool                 g_shockGuardActive  = false;
datetime             g_lastShockTime     = 0;
int                  g_shockCooldownLeft = 0;

// Variabel Status Circuit Breaker & VSA Institusional (v2.3)
int                  g_consecutiveLossCount = 0;
datetime             g_lastLossTime         = 0;
datetime             g_cooldownUntilTime    = 0;
double               g_todayClosedProfit    = 0.0;
bool                 g_dailyLossLimitHit    = false;

// Struktur & State Mesin Otopsi & Koreksi Diri Pasca-Loss (v2.40)
struct LossAutopsyReport
{
   bool                 isActive;
   int                  failedTicket;
   datetime             timeLoss;
   ENUM_CANDLE_PATTERN  failedPattern;
   string               failedPatternName;
   string               lossReason;
   double               scorePenalty;
   datetime             quarantineUntilBar;
   int                  tradesWithExtraBuffer;
   int                  failedDirection;        // Arah posisi gagal: +1 BUY, -1 SELL, 0 None
   datetime             directionPenaltyUntil;  // Waktu berakhirnya penalti arah gagal
   int                  toxicHour;              // Jam server rawan loss berulang (-1 jika aman)
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
AutoCalibrationState g_calibration = {false, 1.0, 0.0, 2, 15.0, 1.0, "Normal", 0};

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

#define TOTAL_TRACKED_PATTERNS 13
PatternRecord g_patternMatrix[TOTAL_TRACKED_PATTERNS];

ENUM_MARKET_REGIME g_currentRegime     = REGIME_NORMAL;
double             g_currentChoppiness = 50.0;
string             g_bestPatternStr    = "BELUM ADA DATA";
string g_newsStatusStr = "AMAN (STANDBY)";
string g_divStatusStr  = "NORMAL (SEHAT)";
string g_sidewaysStatusStr = "NORMAL (TREN SEHAT)";
double g_midnightBalance      = 0.0;
bool   g_equityLockActive     = false;
double g_currentDailyDDPct    = 0.0;
int    g_ddBtnY1              = 0;   // Koordinat Y atas tombol Reset DD (untuk deteksi klik)
int    g_ddBtnY2              = 0;   // Koordinat Y bawah tombol Reset DD

// Pro Trader Discipline Suite Globals (v3.30)
bool     g_dailyProfitLocked        = false;
datetime g_lastProfitLockDay        = 0;
int      g_todayTradesCount         = 0;
datetime g_lastTradeCountDay        = 0;
string g_trapHunterStatusStr  = "STANDBY";
double g_currentADXVal     = 25.0;
double g_currentVolRatio   = 1.20;

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

double PointToPrice(double points)
{
   return PipToPrice(points / 10.0);
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
double CalculateRiskLot(double slDistancePrice, double score = 70.0)
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

   // 8.14 Asymmetric Confidence Risk Allocator (Kelly Scaling v3.00)
   if (InpUseAsymmetricLot)
   {
      if (score >= 85.0)
         finalLot *= InpGradeABoostMultiplier;
      else if (score < 75.0)
         finalLot *= InpGradeBPenaltyMultiplier;
   }

   // Batasi Lot sesuai Min / Max User dan Broker QuickPro
   double effectiveMinLot = (InpMinLot > 0.0) ? MathMax(InpMinLot, brokerMinLot) : brokerMinLot;
   double effectiveMaxLot = (InpMaxLot > 0.0) ? MathMin(InpMaxLot, brokerMaxLot) : brokerMaxLot;
   if (effectiveMaxLot < effectiveMinLot) effectiveMaxLot = effectiveMinLot;

   finalLot = MathMax(effectiveMinLot, MathMin(effectiveMaxLot, finalLot));

   // Normalisasi pembulatan lot sesuai step lot broker QuickPro (dengan proteksi IEEE-754 epsilon)
   finalLot = MathFloor((finalLot + 0.0000001) / brokerStepLot) * brokerStepLot;

   int lotDigits = 2;
   if (brokerStepLot == 1.0) lotDigits = 0;
   else if (brokerStepLot == 0.1) lotDigits = 1;
   else if (brokerStepLot == 0.01) lotDigits = 2;
   else if (brokerStepLot == 0.001) lotDigits = 3;

   finalLot = NormalizeDouble(finalLot, lotDigits);
   if (finalLot < effectiveMinLot) finalLot = effectiveMinLot;
   if (finalLot > effectiveMaxLot) finalLot = effectiveMaxLot;

   return finalLot;
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
//| HELPER & FUNGSI PERSISTENSI AUTOPSY MT4 (v3.10 AI LEARNING)     |
//+------------------------------------------------------------------+
void SaveTradeEntrySnapshotMT4(int ticket, int direction, int patternId, double currentScore, double currentAtr)
{
   GlobalVariableSet("VIKAR_PAT_"  + IntegerToString(ticket), (double)patternId);
   GlobalVariableSet("VIKAR_DIR_"  + IntegerToString(ticket), (double)direction);
   GlobalVariableSet("VIKAR_HOUR_" + IntegerToString(ticket), (double)Hour());
   GlobalVariableSet("VIKAR_ATR_"  + IntegerToString(ticket), currentAtr);
   GlobalVariableSet("VIKAR_SCO_"  + IntegerToString(ticket), currentScore);
}

void SaveAutopsyStateMT4()
{
   string pfx = "VIKAR_MT4_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
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

void LoadAutopsyStateMT4()
{
   string pfx = "VIKAR_MT4_AUTOPSY_" + IntegerToString(InpMagicNumber) + "_";
   if (GlobalVariableCheck(pfx + "ACTIVE") && GlobalVariableGet(pfx + "ACTIVE") > 0.5)
   {
      g_autopsy.isActive              = true;
      g_autopsy.failedTicket          = (int)GlobalVariableGet(pfx + "TICKET");
      g_autopsy.failedPattern         = (ENUM_CANDLE_PATTERN)(int)GlobalVariableGet(pfx + "PAT");
      g_autopsy.scorePenalty          = GlobalVariableGet(pfx + "PENALTY");
      g_autopsy.quarantineUntilBar    = (datetime)GlobalVariableGet(pfx + "QUARANTINE");
      g_autopsy.tradesWithExtraBuffer = (int)GlobalVariableGet(pfx + "BUFFER");
      g_autopsy.failedDirection       = (int)GlobalVariableGet(pfx + "DIR");
      g_autopsy.directionPenaltyUntil = (datetime)GlobalVariableGet(pfx + "DIRUNTIL");
      g_autopsy.toxicHour             = (int)GlobalVariableGet(pfx + "TOXICHOUR");
      g_autopsy.lossReason            = "PEMULIHAN STATUS PASCA-RESTART (PERSISTENT)";
      Print("[SELF-HEALING RESTORED MT4] Status otopsi berhasil dipulihkan dari memori persisten.");
   }
   else
   {
      g_autopsy.isActive              = false;
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
      g_autopsy.toxicHour             = -1;
   }
}

//+------------------------------------------------------------------+
//| MESIN OTOPSI & KOREKSI DIRI PASCA-LOSS (SELF-HEALING ENGINE v3.10)|
//+------------------------------------------------------------------+
void PerformLossAutopsy(int ticket, datetime closeTime, double lossAmount)
{
   g_autopsy.isActive     = true;
   g_autopsy.failedTicket = ticket;
   g_autopsy.timeLoss     = closeTime;
   g_autopsy.scorePenalty = InpPenaltyConfluencePts;
   g_autopsy.tradesWithExtraBuffer = InpAdaptiveBufferTrades;

   // 1. Ambil data pola candlestick dari memori Global Variable (TIDAK DIHAPUS DISINI AGAR BISA DIBACA MATRIX)
   string patGvKey = "VIKAR_PAT_" + IntegerToString(ticket);
   ENUM_CANDLE_PATTERN pat = PATTERN_NONE;
   int rawPatId = 0;
   if (GlobalVariableCheck(patGvKey))
   {
      rawPatId = (int)GlobalVariableGet(patGvKey);
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

   datetime currentBarTime = Time[0];
   if (pat != PATTERN_NONE || rawPatId >= 11)
      g_autopsy.quarantineUntilBar = currentBarTime + (InpQuarantinePatternBars * Period() * 60);
   else
      g_autopsy.quarantineUntilBar = 0;

   // Ambil Direction (BUY = +1, SELL = -1)
   int tradeDir = 0;
   string dirGvKey = "VIKAR_DIR_" + IntegerToString(ticket);
   if (GlobalVariableCheck(dirGvKey)) tradeDir = (int)GlobalVariableGet(dirGvKey);

   if (InpUseDirectionalLearning && tradeDir != 0)
   {
      g_autopsy.failedDirection       = tradeDir;
      g_autopsy.directionPenaltyUntil = currentBarTime + (InpDirectionalPenaltyBars * Period() * 60);
   }
   else
   {
      g_autopsy.failedDirection       = 0;
      g_autopsy.directionPenaltyUntil = 0;
   }

   // Ambil Jam Transaksi (0..23) dan Lacak Jam Rawan Loss Berulang
   int tradeHour = -1;
   string hrGvKey = "VIKAR_HOUR_" + IntegerToString(ticket);
   if (GlobalVariableCheck(hrGvKey)) tradeHour = (int)GlobalVariableGet(hrGvKey);

   if (InpUseHourlyLearning && tradeHour >= 0 && tradeHour <= 23)
   {
      string hLossKey = "VIKAR_MT4_HLOSS_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(tradeHour);
      int currentHLoss = GlobalVariableCheck(hLossKey) ? (int)GlobalVariableGet(hLossKey) : 0;
      currentHLoss++;
      GlobalVariableSet(hLossKey, (double)currentHLoss);

      if (currentHLoss >= 2)
      {
         g_autopsy.toxicHour = tradeHour;
         Print("[HOURLY LEARNING MT4] Jam ", tradeHour, ":00 server terdeteksi rawan loss berulang (", currentHLoss, "x loss). Proteksi jam aktif!");
      }
      else
         g_autopsy.toxicHour = -1;
   }
   else
      g_autopsy.toxicHour = -1;

   // 2. Diagnosa Anatomi Mendalam Penyebab Loss (7 Skenario Institusional)
   double currentAtr = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   double lastBarRange = High[1] - Low[1];
   double currentEma125 = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);

   double htfEma125 = iMA(Symbol(), InpHTFTimeframe, InpHTFTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double htfClose  = iClose(Symbol(), InpHTFTimeframe, 1);
   bool isHtfBull   = (htfClose > htfEma125);
   bool isHtfBear   = (htfClose < htfEma125);

   string reason = "PENGUJIAN LEVEL GAGAL (SUPPORT/RESISTEN DITEMBUS)";
   if (lastBarRange >= (2.0 * currentAtr))
      reason = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPREAD SPIKE)";
   else if (g_currentChoppiness > 61.8)
      reason = "JEBAKAN SIDEWAYS NOISE (PASAR CHOPPY KOMPRESI)";
   else if (g_smcAnalysis.hasCHoCH || (Close[1] < currentEma125 && Open[1] > currentEma125) || (Close[1] > currentEma125 && Open[1] < currentEma125))
      reason = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)";
   else if (g_smcAnalysis.hasSweep)
      reason = "LIQUIDITY SWEEP SHAKEOUT (SL TERSAPU EKOR)";
   else if (tradeDir == 1 && isHtfBear)
      reason = "DIRECTIONAL ERROR (BUY MELAWAN TREN MAKRO HTF)";
   else if (tradeDir == -1 && isHtfBull)
      reason = "DIRECTIONAL ERROR (SELL MELAWAN TREN MAKRO HTF)";
   else if (g_autopsy.toxicHour >= 0)
      reason = "JAM RAWAN VOLATILITAS (TOXIC HOUR REVERSAL)";

   g_autopsy.lossReason = reason;
   SaveAutopsyStateMT4();

   Print("==================================================================");
   Print("[SELF-HEALING AUTOPSY MT4] Posisi #", ticket, " Loss: ", DoubleToString(lossAmount, 2));
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
      string notif = "OTOPSI PASCA-SL MT4 #" + IntegerToString(ticket) + " (" + DoubleToString(lossAmount, 2) + ")\n" +
                     "Diagnosa: " + reason + "\n" +
                     "Koreksi: Ambang Skor +" + DoubleToString(g_autopsy.scorePenalty, 0) + " Poin.";
      if (pat != PATTERN_NONE || rawPatId >= 11)
         notif += " Pola " + patName + " dikarantina " + IntegerToString(InpQuarantinePatternBars) + " bar.";
      if (tradeDir != 0 && InpUseDirectionalLearning)
         notif += " Penalti arah " + (tradeDir == 1 ? "BUY" : "SELL") + " aktif.";
      SendPushAlert(notif);
   }
}

//+------------------------------------------------------------------+
//| FUNGSI MATEMATIS: CHOPPINESS INDEX (CI) DENGAN BASE 10 LOGARITHM|
//+------------------------------------------------------------------+
double CalculateChoppinessIndex(int period)
{
   if (Bars < period + 2) return 50.0;

   double sumTR = 0.0;
   double highMax = High[1];
   double lowMin  = Low[1];

   for (int i = 1; i <= period; i++)
   {
      double h = High[i];
      double l = Low[i];
      double prevClose = Close[i + 1];

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
//| INISIALISASI & PEMULIHAN MEMORI PATTERN PERFORMANCE MATRIX       |
//+------------------------------------------------------------------+
void SaveAIBrainToDiskMT4()
{
   if (!InpSaveBrainToDisk) return;
   string fileName = "vikar_ai_brain_" + IntegerToString(InpMagicNumber) + ".csv";
   int handle = FileOpen(fileName, FILE_WRITE|FILE_CSV, ';');
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

bool LoadAIBrainFromDiskMT4()
{
   if (!InpSaveBrainToDisk) return false;
   string fileName = "vikar_ai_brain_" + IntegerToString(InpMagicNumber) + ".csv";
   if (!FileIsExist(fileName)) return false;

   int handle = FileOpen(fileName, FILE_READ|FILE_CSV, ';');
   if (handle == INVALID_HANDLE) return false;

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
   Print("[AI BRAIN DISK MT4] Berhasil memuat ingatan permanen dari disk: ", fileName, " (", loaded, " pola).");
   return (loaded > 0);
}

void InitPatternMatrix()
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

   bool loadedFromDisk = LoadAIBrainFromDiskMT4();

   int blacklistedCount = 0;
   double highestWR = -1.0;
   string bestName = "BELUM ADA DATA";

   for (int i = 0; i < TOTAL_TRACKED_PATTERNS; i++)
   {
      string gvWKey = "VIKAR_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);
      string gvLKey = "VIKAR_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(i);

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

      // Pre-Trained Institutional Knowledge (Pengalaman Audit 50,123 Bar M5 2026)
      if (InpUsePreTrainedBrain && total == 0)
      {
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
   SaveAIBrainToDiskMT4();
   Print("[AI PATTERN MATRIX MT4] Diinisialisasi. Pola Aktif: ", TOTAL_TRACKED_PATTERNS, " | Ter-blacklist: ", blacklistedCount, " | Terbaik: ", g_bestPatternStr);
}

void UpdatePatternRecord(int patternId, bool isWin)
{
   if (patternId < 0 || patternId >= TOTAL_TRACKED_PATTERNS) return;

   string gvWKey = "VIKAR_PMR_W_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);
   string gvLKey = "VIKAR_PMR_L_" + IntegerToString(InpMagicNumber) + "_" + IntegerToString(patternId);

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
         Print("[AI MATRIX WARNING MT4] Pola '", g_patternMatrix[patternId].name, "' di-BLACKLIST mandiri (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% < ", InpPatternBlacklistWinrate, "%).");
      }
      else if (g_patternMatrix[patternId].winRate >= InpPatternBoostWinrate)
      {
         g_patternMatrix[patternId].isBlacklisted = false;
         g_patternMatrix[patternId].scoreModifier = InpPatternBoostScore;
         Print("[AI MATRIX BOOST MT4] Pola '", g_patternMatrix[patternId].name, "' mendapatkan BOOST +", InpPatternBoostScore, " Poin (Winrate: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "% >= ", InpPatternBoostWinrate, "%).");
      }
      else
      {
         if (g_patternMatrix[patternId].isBlacklisted)
         {
            Print("[AI MATRIX REHABILITASI MT4] Pola '", g_patternMatrix[patternId].name, "' dipulihkan dari blacklist (Winrate membaik: ", DoubleToString(g_patternMatrix[patternId].winRate, 1), "%).");
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
   SaveAIBrainToDiskMT4();
}

//+------------------------------------------------------------------+
//| SENSOR PRE-NEWS EVENT SHIELD: PEMERIKSAAN JADWAL RILIS BERITA AS |
//+------------------------------------------------------------------+
bool IsInsideNewsWindow(string &activeNewsStr)
{
   activeNewsStr = "";
   if (!InpUseNewsShield) return false;

   datetime now = TimeCurrent();
   int currentMins = TimeHour(now) * 60 + TimeMinute(now);

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
      item = StringTrimLeft(StringTrimRight(item));
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
//| SENSOR PELEBARAN SPREAD ABNORMAL (SPREAD SPIKE SHIELD)          |
//+------------------------------------------------------------------+
bool IsSpreadSpikeDetected()
{
   if (!InpUseNewsShield) return false;
   double currentSpreadPips = (double)MarketInfo(Symbol(), MODE_SPREAD) * Point / PipToPrice(1.0);
   if (currentSpreadPips > (InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier))
   {
      Print("[SPREAD SPIKE SHIELD MT4] Terdeteksi lonjakan spread ekstrem: ", DoubleToString(currentSpreadPips, 1), " pips > ", DoubleToString(InpMaxSpreadPips * InpMaxSpreadSpikeMultiplier, 1), " pips. Menunda eksekusi.");
      return true;
   }
   return false;
}

//+------------------------------------------------------------------+
//| SENSOR PELEMAHAN MOMENTUM: RSI DIVERGENCE (ANTI-PUCUK / LEMBAH)  |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| SENSOR KEKUATAN TREN KINETIK: ADX FILTER (v2.70)                 |
//+------------------------------------------------------------------+
bool CheckADXPower(double &adxVal)
{
   adxVal = iADX(Symbol(), 0, InpADXPeriod, PRICE_CLOSE, MODE_MAIN, 1);
   g_currentADXVal = adxVal;
   if (!InpUseADXFilter) return true;
   return (adxVal >= InpMinADXThreshold);
}

//+------------------------------------------------------------------+
//| SENSOR KEMIRINGAN SUDUT: EMA SLOPE FILTER (v2.70)                |
//+------------------------------------------------------------------+
bool CheckEMASlope(bool isBuy, double &slopePips)
{
   slopePips = 0.0;
   if (!InpUseEMASlopeFilter) return true;
   if (Bars < InpEMASlopeLookback + 5) return true;

   double emaNow  = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double emaPast = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1 + InpEMASlopeLookback);

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
//| SENSOR VOLUME INSTITUSIONAL: VSA EXPANSION FILTER (v2.70)        |
//+------------------------------------------------------------------+
bool CheckVolumeExpansion(double &volRatio)
{
   volRatio = 1.0;
   if (!InpUseVolumeFilter) return true;
   if (Bars < InpVolumeMAPeriod + 5) return true;

   double sumVol = 0.0;
   for (int i = 2; i <= InpVolumeMAPeriod + 1; i++)
   {
      sumVol += (double)Volume[i];
   }
   double avgVol = sumVol / (double)InpVolumeMAPeriod;
   if (avgVol <= 0) return true;

   double currentVol = (double)Volume[1];
   volRatio = currentVol / avgVol;
   g_currentVolRatio = volRatio;

   return (volRatio >= InpMinVolumeMultiplier);
}

//+------------------------------------------------------------------+
//| SENSOR BATAS BAWAH VOLATILITAS: MINIMUM ATR FLOOR (v2.70)       |
//+------------------------------------------------------------------+
bool CheckMinATRFloor(double currentAtrPrice, double &atrPips)
{
   atrPips = PriceToPips(currentAtrPrice);
   if (!InpUseMinATRFilter) return true;
   return (atrPips >= InpMinATRPips);
}

bool CheckRSIDivergence(bool isBuy)
{
   if (!InpUseDivergenceFilter) return false;
   int lookback = MathMin(InpDivergenceLookbackBars, Bars - 5);
   if (lookback < 10) return false;

   if (isBuy)
   {
      // Deteksi Bearish Divergence (Harga buat Higher High, tapi RSI buat Lower High)
      int peak1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (High[i] > High[peak1]) peak1 = i;
      }

      int peak2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (High[j] > High[peak2]) peak2 = j;
      }

      double priceHigh1 = High[peak1];
      double priceHigh2 = High[peak2];
      double rsi1 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, peak1);
      double rsi2 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, peak2);

      if (priceHigh1 > priceHigh2 + PipToPrice(2.5) && rsi1 < rsi2 - 3.0 && rsi1 > 60.0)
      {
         g_divStatusStr = "BEARISH DIVERGENCE (EXHAUSTION TOP)";
         Print("[DIVERGENCE MT4] Bearish Divergence terdeteksi di pucuk (Peak1 RSI: ", DoubleToString(rsi1, 1), " < Peak2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan BUY.");
         return true;
      }
   }
   else
   {
      // Deteksi Bullish Divergence (Harga buat Lower Low, tapi RSI buat Higher Low)
      int trough1 = 1;
      for (int i = 1; i <= 5; i++)
      {
         if (Low[i] < Low[trough1]) trough1 = i;
      }

      int trough2 = 6;
      for (int j = 6; j <= lookback; j++)
      {
         if (Low[j] < Low[trough2]) trough2 = j;
      }

      double priceLow1 = Low[trough1];
      double priceLow2 = Low[trough2];
      double rsi1 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, trough1);
      double rsi2 = iRSI(Symbol(), 0, InpRSIPeriod, PRICE_CLOSE, trough2);

      if (priceLow1 < priceLow2 - PipToPrice(2.5) && rsi1 > rsi2 + 3.0 && rsi1 < 40.0)
      {
         g_divStatusStr = "BULLISH DIVERGENCE (EXHAUSTION BOTTOM)";
         Print("[DIVERGENCE MT4] Bullish Divergence terdeteksi di dasar (Trough1 RSI: ", DoubleToString(rsi1, 1), " > Trough2 RSI: ", DoubleToString(rsi2, 1), "). Membatalkan SELL.");
         return true;
      }
   }

   g_divStatusStr = "NORMAL (SEHAT)";
   return false;
}

void ResetSelfHealingState(string triggerReason)
{
   if (!g_autopsy.isActive) return;
   g_autopsy.isActive              = false;
   g_autopsy.scorePenalty          = 0.0;
   g_autopsy.tradesWithExtraBuffer = 0;
   g_autopsy.quarantineUntilBar    = 0;
   g_autopsy.failedDirection       = 0;
   g_autopsy.directionPenaltyUntil = 0;
   g_autopsy.lossReason            = "STANDBY / OPTIMAL (NORMAL)";
   SaveAutopsyStateMT4();
   Print("[SELF-HEALING NORMALIZED MT4] Sistem kembali ke mode standar. Pemicu: ", triggerReason);
}

//+------------------------------------------------------------------+
//| PRO TRADER DISCIPLINE HELPERS (v3.30)                            |
//+------------------------------------------------------------------+
bool IsInRolloverWindow()
{
   if (!InpUseRolloverGuard) return false;
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
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

bool IsInKillzoneWindow()
{
   if (!InpTradeKillzonesOnly) return true;
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   if (dt.hour >= InpKillzoneLondonStart && dt.hour < InpKillzoneLondonEnd) return true;
   if (dt.hour >= InpKillzoneNYStart && dt.hour < InpKillzoneNYEnd) return true;
   return false;
}

//+------------------------------------------------------------------+
//| EVALUASI CIRCUIT BREAKER: CONSECUTIVE LOSS COOLDOWN & DAILY LIMIT|
//+------------------------------------------------------------------+
bool CheckCircuitBreakers()
{
   // 0. Prop Firm Equity Guardian (v3.00)
   if (InpUseEquityGuardian)
   {
      static datetime lastDayReset = 0;
      datetime currentDayStart = iTime(Symbol(), PERIOD_D1, 0);
      if (lastDayReset != currentDayStart)
      {
         g_midnightBalance  = AccountBalance();
         g_equityLockActive = false;
         lastDayReset       = currentDayStart;
      }

      if (g_equityLockActive)
      {
         g_lastSignalType = "PROP FIRM GUARDIAN: TRADING DIKUNCI HARI INI (BATAS DD TERSENTUH)";
         return false;
      }

      if (g_midnightBalance > 0.0)
      {
         double currentDDAmount = g_midnightBalance - AccountEquity();
         double currentDDPct    = (currentDDAmount / g_midnightBalance) * 100.0;
         g_currentDailyDDPct    = currentDDPct;

         if (currentDDPct >= InpMaxDailyEquityDDPct)
         {
            Print("[PROP FIRM EQUITY GUARDIAN MT4] EMERGENCY KILL-SWITCH! Penurunan equity harian mencapai ", DoubleToString(currentDDPct, 2), "% >= ", DoubleToString(InpMaxDailyEquityDDPct, 2), "%. Menutup seluruh posisi & mengunci trading!");
            
            int totalOrders = OrdersTotal();
            for (int p = totalOrders - 1; p >= 0; p--)
            {
               if (OrderSelect(p, SELECT_BY_POS, MODE_TRADES))
               {
                  if (OrderSymbol() == Symbol() && OrderMagicNumber() == InpMagicNumber)
                  {
                     bool cls = OrderClose(OrderTicket(), OrderLots(), (OrderType() == OP_BUY ? Bid : Ask), InpDeviation, clrRed);
                     if (!cls) Print("[ERROR] Gagal emergency close order #", OrderTicket());
                  }
               }
            }

            g_equityLockActive = true;
            g_lastSignalType   = "PROP FIRM GUARDIAN: TRADING DIKUNCI (DD " + DoubleToString(currentDDPct, 1) + "% >= " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%)";
            
            if (InpSendPushNotifications)
               SendPushAlert("PROP FIRM EQUITY GUARDIAN MEMICU HARD KILL-SWITCH!\nDrawdown Harian: " + DoubleToString(currentDDPct, 1) + "% mencapai batas maksimal. Akun dikunci hingga besok.");
            
            return false;
         }
      }
   }

   if (!InpUseConsecutiveLossGuard && !InpUseDailyLossLimit && !InpUseEquityGuardian && !InpUseDailyProfitLockdown && !InpUseMaxDailyTrades)
      return true;

   datetime todayStart = iTime(Symbol(), PERIOD_D1, 0);
   int consecutiveLosses = 0;
   datetime lastLossTime = 0;
   double todayClosedPnL = 0.0;
   struct HistoryTradeInfo
   {
      int      ticket;
      datetime closeTime;
      double   profit;
   };

   HistoryTradeInfo todayTrades[];
   int countToday = 0;
   int histTotal = OrdersHistoryTotal();

   for (int i = 0; i < histTotal; i++)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_HISTORY)) continue;
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
      if (OrderCloseTime() < todayStart) continue;

      ArrayResize(todayTrades, countToday + 1);
      todayTrades[countToday].ticket    = OrderTicket();
      todayTrades[countToday].closeTime = OrderCloseTime();
      todayTrades[countToday].profit    = OrderProfit() + OrderSwap() + OrderCommission();
      countToday++;
   }

   // Urutkan transaksi hari ini secara kronologis mutlak (kebal dari klik kolom GUI terminal MT4)
   for (int a = 0; a < countToday - 1; a++)
   {
      for (int b = a + 1; b < countToday; b++)
      {
         if (todayTrades[a].closeTime > todayTrades[b].closeTime)
         {
            HistoryTradeInfo tmp = todayTrades[a];
            todayTrades[a] = todayTrades[b];
            todayTrades[b] = tmp;
         }
      }
   }

   // Evaluasi urutan transaksi secara kronologis
   for (int k = 0; k < countToday; k++)
   {
      double profit = todayTrades[k].profit;
      todayClosedPnL += profit;

      // Evaluasi Loss vs Win:
      // SL+ menghasilkan net profit > 0, sehingga strictly dihitung sebagai WIN dan me-reset counter!
      if (profit < -0.01) // True Loss (Kerugian riil modal)
      {
         consecutiveLosses++;
         lastLossTime = todayTrades[k].closeTime;
         if (InpUseSelfHealing && g_autopsy.failedTicket != todayTrades[k].ticket)
            PerformLossAutopsy(todayTrades[k].ticket, todayTrades[k].closeTime, profit);
      }
      else if (profit > 0.01) // Win ATAU SL+ (Keuntungan positif) -> Reset Counter ke 0!
      {
         consecutiveLosses = 0; // SL+ MERESET COUNTER! TIDAK PERNAH MEMICU COOLDOWN!
         if (InpUseSelfHealing && g_autopsy.isActive)
            ResetSelfHealingState("TRANSAKSI SELESAI DENGAN PROFIT (WIN / SL+)");
      }

      // Pembaruan Statistik Pattern Performance Matrix MT4 (v3.10)
      string procKey = "VIKAR_PMR_PROC_" + IntegerToString(todayTrades[k].ticket);
      if (!GlobalVariableCheck(procKey))
      {
         string patGvKey = "VIKAR_PAT_" + IntegerToString(todayTrades[k].ticket);
         int patId = GlobalVariableCheck(patGvKey) ? (int)GlobalVariableGet(patGvKey) : 0;
         if (profit > 0.01)
            UpdatePatternRecord(patId, true);
         else if (profit < -0.01)
            UpdatePatternRecord(patId, false);
         GlobalVariableSet(procKey, 1.0);

         // Bersihkan snapshot tiket setelah statistik diperbarui
         if (GlobalVariableCheck(patGvKey)) GlobalVariableDel(patGvKey);
         GlobalVariableDel("VIKAR_DIR_" + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_HOUR_" + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_ATR_" + IntegerToString(todayTrades[k].ticket));
         GlobalVariableDel("VIKAR_SCO_" + IntegerToString(todayTrades[k].ticket));
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

   // 2.1 Daily Profit Target Lockdown ("Done for the Day") (v3.30)
   if (InpUseDailyProfitLockdown)
   {
      double targetProfit = (InpDailyProfitTargetMode == PROFIT_TARGET_CURRENCY) ? 
                            InpDailyProfitTargetMoney : 
                            (AccountBalance() * (InpDailyProfitTargetPercent / 100.0));
      if (todayClosedPnL >= targetProfit)
      {
         g_dailyProfitLocked = true;
         g_lastSignalType = "DONE FOR THE DAY: TARGET PROFIT TERCAPAI (+$" + DoubleToString(todayClosedPnL, 2) + " >= $" + DoubleToString(targetProfit, 2) + ")";
         static datetime lastLockPush = 0;
         if (InpSendPushNotifications && (TimeCurrent() - lastLockPush) > 3600)
         {
            SendPushAlert("TARGET PROFIT HARIAN TERCAPAI! (DONE FOR THE DAY)\nProfit Hari Ini: +$" + DoubleToString(todayClosedPnL, 2) + "\nRobot mengunci trading hari ini demi mengamankan keuntungan!");
            lastLockPush = TimeCurrent();
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
      int totalTradesToday = countToday; // Closed trades today
      int openTotal = OrdersTotal();
      for (int op = 0; op < openTotal; op++)
      {
         if (OrderSelect(op, SELECT_BY_POS, MODE_TRADES))
         {
            if (OrderSymbol() == Symbol() && OrderMagicNumber() == InpMagicNumber && OrderOpenTime() >= todayStart)
               totalTradesToday++;
         }
      }
      g_todayTradesCount = totalTradesToday;
      if (totalTradesToday >= InpMaxDailyTrades)
      {
         g_lastSignalType = "MAX TRADES HARIAN TERCAPAI (" + IntegerToString(totalTradesToday) + "/" + IntegerToString(InpMaxDailyTrades) + "): DISIPLIN KUOTA";
         return false;
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

   SMCSwing tempHighs[2];
   SMCSwing tempLows[2];
   ZeroMemory(tempHighs);
   ZeroMemory(tempLows);
   int countHigh = 0;
   int countLow  = 0;

   // Pindai dari lilin terbaru (i=2) ke belakang untuk mendapatkan swing fractal terkini
   for (int i = 2; i <= limit - k; i++)
   {
      bool isHigh = true;
      bool isLow  = true;

      for (int j = 1; j <= k; j++)
      {
         if (High[i] <= High[i - j] || High[i] <= High[i + j]) isHigh = false;
         if (Low[i] >= Low[i - j]   || Low[i] >= Low[i + j])   isLow  = false;
      }

      if (isHigh && countHigh < 2)
      {
         tempHighs[countHigh].time    = Time[i];
         tempHighs[countHigh].price   = High[i];
         tempHighs[countHigh].isHigh  = true;
         tempHighs[countHigh].isSwept = false;
         countHigh++;
      }

      if (isLow && countLow < 2)
      {
         tempLows[countLow].time    = Time[i];
         tempLows[countLow].price   = Low[i];
         tempLows[countLow].isHigh  = false;
         tempLows[countLow].isSwept = false;
         countLow++;
      }

      if (countHigh >= 2 && countLow >= 2) break;
   }

   if (countHigh >= 1)
   {
      lastSwingHigh = tempHighs[0];
      if (countHigh >= 2) prevSwingHigh = tempHighs[1];
      else
      {
         int hBar2 = iHighest(Symbol(), 0, MODE_HIGH, MathMin(40, Bars - 35), 25);
         if (hBar2 > 0)
         {
            prevSwingHigh.time = Time[hBar2];
            prevSwingHigh.price = High[hBar2];
            prevSwingHigh.isHigh = true;
         }
      }
   }
   else
   {
      int hBar1 = iHighest(Symbol(), 0, MODE_HIGH, MathMin(30, Bars - 5), 1);
      if (hBar1 > 0)
      {
         lastSwingHigh.time = Time[hBar1];
         lastSwingHigh.price = High[hBar1];
         lastSwingHigh.isHigh = true;
      }
      int hBar2 = iHighest(Symbol(), 0, MODE_HIGH, MathMin(40, Bars - 35), 31);
      if (hBar2 > 0)
      {
         prevSwingHigh.time = Time[hBar2];
         prevSwingHigh.price = High[hBar2];
         prevSwingHigh.isHigh = true;
      }
   }

   if (countLow >= 1)
   {
      lastSwingLow = tempLows[0];
      if (countLow >= 2) prevSwingLow = tempLows[1];
      else
      {
         int lBar2 = iLowest(Symbol(), 0, MODE_LOW, MathMin(40, Bars - 35), 25);
         if (lBar2 > 0)
         {
            prevSwingLow.time = Time[lBar2];
            prevSwingLow.price = Low[lBar2];
            prevSwingLow.isHigh = false;
         }
      }
   }
   else
   {
      int lBar1 = iLowest(Symbol(), 0, MODE_LOW, MathMin(30, Bars - 5), 1);
      if (lBar1 > 0)
      {
         lastSwingLow.time = Time[lBar1];
         lastSwingLow.price = Low[lBar1];
         lastSwingLow.isHigh = false;
      }
      int lBar2 = iLowest(Symbol(), 0, MODE_LOW, MathMin(40, Bars - 35), 31);
      if (lBar2 > 0)
      {
         prevSwingLow.time = Time[lBar2];
         prevSwingLow.price = Low[lBar2];
         prevSwingLow.isHigh = false;
      }
   }
}

//+------------------------------------------------------------------+
//| EKSTRAKSI AYUNAN STRUKTUR VALID (KANDEL LAMA KE KANDEL BARU)     |
//| Filter bergantian (High-Low) & Jarak Minimal ATR agar tidak semrawut|
//+------------------------------------------------------------------+
void ExtractValidSwings(int lookback, double currentAtr)
{
   g_validSwingCount = 0;
   if (currentAtr <= 0.0) return;

   int limit = MathMin(lookback, Bars - 5);
   int k = MathMax(2, InpFractalPeriod);
   double minDist = InpMinSwingATRMult * currentAtr;

   // 1. Kumpulkan semua calon fractal dari bar lama ke bar baru (chronological)
   SMCSwing rawSwings[50];
   ZeroMemory(rawSwings);
   int rawCount = 0;

   for (int i = limit; i >= 2; i--)
   {
      bool isH = true;
      bool isL = true;
      for (int j = 1; j <= k; j++)
      {
         if (High[i] <= High[i - j] || High[i] <= High[i + j]) isH = false;
         if (Low[i] >= Low[i - j]   || Low[i] >= Low[i + j])   isL = false;
      }

      if (isH && !isL && rawCount < 50)
      {
         rawSwings[rawCount].time = Time[i];
         rawSwings[rawCount].price = High[i];
         rawSwings[rawCount].isHigh = true;
         rawCount++;
      }
      else if (isL && !isH && rawCount < 50)
      {
         rawSwings[rawCount].time = Time[i];
         rawSwings[rawCount].price = Low[i];
         rawSwings[rawCount].isHigh = false;
         rawCount++;
      }
   }

   if (rawCount < 2) return;

   // 2. Filter Alternating (High -> Low -> High -> Low) & Validitas Jarak Minimal (minDist)
   ValidStructureSwing filtered[30];
   ZeroMemory(filtered);
   int fCount = 0;

   for (int r = 0; r < rawCount; r++)
   {
      if (fCount == 0)
      {
         filtered[0].time = rawSwings[r].time;
         filtered[0].price = rawSwings[r].price;
         filtered[0].isHigh = rawSwings[r].isHigh;
         filtered[0].label = "";
         fCount++;
      }
      else
      {
         bool lastWasHigh = filtered[fCount - 1].isHigh;
         if (rawSwings[r].isHigh == lastWasHigh)
         {
            if (lastWasHigh && rawSwings[r].price > filtered[fCount - 1].price)
            {
               filtered[fCount - 1].time = rawSwings[r].time;
               filtered[fCount - 1].price = rawSwings[r].price;
            }
            else if (!lastWasHigh && rawSwings[r].price < filtered[fCount - 1].price)
            {
               filtered[fCount - 1].time = rawSwings[r].time;
               filtered[fCount - 1].price = rawSwings[r].price;
            }
         }
         else
         {
            double dist = MathAbs(rawSwings[r].price - filtered[fCount - 1].price);
            if (dist >= minDist && fCount < 30)
            {
               filtered[fCount].time = rawSwings[r].time;
               filtered[fCount].price = rawSwings[r].price;
               filtered[fCount].isHigh = rawSwings[r].isHigh;
               filtered[fCount].label = "";
               fCount++;
            }
         }
      }
   }

   if (fCount < 2) return;

   // 3. Beri Label Struktur (HH, HL, LH, LL)
   double prevH = 0.0;
   double prevL = 0.0;
   for (int f = 0; f < fCount; f++)
   {
      if (filtered[f].isHigh)
      {
         if (prevH > 0.0)
            filtered[f].label = (filtered[f].price > prevH) ? "HH" : "LH";
         else
            filtered[f].label = "H";
         prevH = filtered[f].price;
      }
      else
      {
         if (prevL > 0.0)
            filtered[f].label = (filtered[f].price > prevL) ? "HL" : "LL";
         else
            filtered[f].label = "L";
         prevL = filtered[f].price;
      }
   }

   // 4. Ambil N ayunan valid terbaru
   int takeCount = MathMin(fCount, MAX_VALID_SWINGS);
   int startIdx = fCount - takeCount;
   g_validSwingCount = 0;
   for (int kIdx = startIdx; kIdx < fCount; kIdx++)
   {
      g_validSwings[g_validSwingCount] = filtered[kIdx];
      g_validSwingCount++;
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

   s.bosPrice = 0.0;
   s.bosTimeStart = 0;
   s.bosTimeEnd = 0;
   s.isBullishBOS = false;
   s.bosBreakTime = 0;
   s.bosBreakPrice = 0.0;
   s.bosIsConfirmed = false;

   s.chochPrice = 0.0;
   s.chochTimeStart = 0;
   s.chochTimeEnd = 0;
   s.isBullishCHoCH = false;
   s.chochBreakTime = 0;
   s.chochBreakPrice = 0.0;
   s.chochIsConfirmed = false;

   s.sweepPriceLevel = 0.0;
   s.sweepTimeStart = 0;
   s.sweepTimeEnd = 0;
   s.isBullishSweep = false;

   s.hasIDM = false;
   s.idmPrice = 0.0;
   s.idmTime = 0;
   s.isBullishIDM = false;

   if (s.dealingRangeHigh > s.dealingRangeLow)
   {
      double range = s.dealingRangeHigh - s.dealingRangeLow;
      s.discountPercent = ((Close[1] - s.dealingRangeLow) / range) * 100.0;
      s.isDiscount = (s.discountPercent <= 50.0);
      s.isPremium  = (s.discountPercent >= 50.0);
   }

   // -------------------------------------------------------------
   // 1. Deteksi SSS (Smart Money Sweep / Liquidity Sweep)
   // -------------------------------------------------------------
   int scanLimit = MathMin(25, Bars - 5);
   for (int b = 1; b <= scanLimit; b++)
   {
      if (lastSwingHigh.price > 0 && High[b] > lastSwingHigh.price && Close[b] < lastSwingHigh.price && !s.hasSweep)
      {
         s.hasSweep = true;
         s.sweepPrice = High[b];
         s.sweepPriceLevel = lastSwingHigh.price;
         s.sweepTimeStart = lastSwingHigh.time;
         s.sweepTimeEnd = Time[b];
         s.isBullishSweep = false;
         lastSwingHigh.isSwept = true;
         break;
      }
      else if (lastSwingLow.price > 0 && Low[b] < lastSwingLow.price && Close[b] > lastSwingLow.price && !s.hasSweep)
      {
         s.hasSweep = true;
         s.sweepPrice = Low[b];
         s.sweepPriceLevel = lastSwingLow.price;
         s.sweepTimeStart = lastSwingLow.time;
         s.sweepTimeEnd = Time[b];
         s.isBullishSweep = true;
         lastSwingLow.isSwept = true;
         break;
      }
   }

   // -------------------------------------------------------------
   // 2. Deteksi Break of Structure (BOS) & Identifikasi Lilin Tertutup Penembus
   // -------------------------------------------------------------
   // A. Jika terjadi Higher High dibanding swing sebelumnya:
   if (lastSwingHigh.price > prevSwingHigh.price && prevSwingHigh.price > 0)
   {
      s.hasBOS = true;
      s.bosPrice = prevSwingHigh.price;
      s.bosTimeStart = prevSwingHigh.time;
      s.isBullishBOS = true;
      s.structure = SMC_STRUCT_BULLISH;
      s.structureName = "BULLISH BOS (CONTINUATION)";
   }
   // B. Jika terjadi Lower Low dibanding swing sebelumnya:
   else if (lastSwingLow.price < prevSwingLow.price && prevSwingLow.price > 0)
   {
      s.hasBOS = true;
      s.bosPrice = prevSwingLow.price;
      s.bosTimeStart = prevSwingLow.time;
      s.isBullishBOS = false;
      s.structure = SMC_STRUCT_BEARISH;
      s.structureName = "BEARISH BOS (CONTINUATION)";
   }
   // C. Jika candle tertutup sedang menembus swing high/low aktif:
   else if (Close[1] > lastSwingHigh.price && lastSwingHigh.price > 0)
   {
      s.hasBOS = true;
      s.bosPrice = lastSwingHigh.price;
      s.bosTimeStart = lastSwingHigh.time;
      s.isBullishBOS = true;
      s.structure = SMC_STRUCT_BULLISH;
      s.structureName = "BULLISH BOS (BREAKOUT)";
   }
   else if (Close[1] < lastSwingLow.price && lastSwingLow.price > 0)
   {
      s.hasBOS = true;
      s.bosPrice = lastSwingLow.price;
      s.bosTimeStart = lastSwingLow.time;
      s.isBullishBOS = false;
      s.structure = SMC_STRUCT_BEARISH;
      s.structureName = "BEARISH BOS (BREAKOUT)";
   }
   else
   {
      double ema125 = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      if (Close[1] >= ema125 && lastSwingHigh.price > 0)
      {
         s.hasBOS = true;
         s.bosPrice = lastSwingHigh.price;
         s.bosTimeStart = lastSwingHigh.time;
         s.isBullishBOS = true;
         s.structure = SMC_STRUCT_BULLISH;
         s.structureName = "BULLISH BIAS (HH-HL)";
      }
      else if (Close[1] < ema125 && lastSwingLow.price > 0)
      {
         s.hasBOS = true;
         s.bosPrice = lastSwingLow.price;
         s.bosTimeStart = lastSwingLow.time;
         s.isBullishBOS = false;
         s.structure = SMC_STRUCT_BEARISH;
         s.structureName = "BEARISH BIAS (LH-LL)";
      }
   }

   // Cari lilin tertutup (closed candle) yang membentuk BOS:
   if (s.hasBOS && s.bosPrice > 0 && s.bosTimeStart > 0)
   {
      int startBOSBar = iBarShift(Symbol(), 0, s.bosTimeStart);
      int confirmedBOSBar = -1;

      for (int b = startBOSBar - 1; b >= 1; b--)
      {
         if (s.isBullishBOS)
         {
            if (Close[b] > s.bosPrice)
            {
               confirmedBOSBar = b;
               break;
            }
         }
         else
         {
            if (Close[b] < s.bosPrice)
            {
               confirmedBOSBar = b;
               break;
            }
         }
      }

      if (confirmedBOSBar > 0)
      {
         s.bosIsConfirmed = true;
         s.bosBreakTime   = Time[confirmedBOSBar];
         s.bosBreakPrice  = s.isBullishBOS ? High[confirmedBOSBar] : Low[confirmedBOSBar];
         s.bosTimeEnd     = Time[confirmedBOSBar]; // Garis horizontal berakhir tepat di lilin penembus
      }
      else
      {
         s.bosIsConfirmed = false;
         s.bosBreakTime   = 0;
         s.bosBreakPrice  = 0.0;
         s.bosTimeEnd     = Time[0] + (Period() * 60 * 6);
      }
   }

   // -------------------------------------------------------------
   // 3. Deteksi Change of Character (CHoCH) & Identifikasi Lilin Tertutup Pembalik
   // -------------------------------------------------------------
   double ema125Val = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   bool isBullMarket = (Close[1] >= ema125Val) || (lastSwingHigh.price >= prevSwingHigh.price);

   if (isBullMarket && lastSwingLow.price > 0)
   {
      s.hasCHoCH = true;
      s.chochPrice = lastSwingLow.price;
      s.chochTimeStart = lastSwingLow.time;
      s.isBullishCHoCH = false;
   }
   else if (!isBullMarket && lastSwingHigh.price > 0)
   {
      s.hasCHoCH = true;
      s.chochPrice = lastSwingHigh.price;
      s.chochTimeStart = lastSwingHigh.time;
      s.isBullishCHoCH = true;
   }

   // Cari lilin tertutup yang membentuk CHoCH:
   if (s.hasCHoCH && s.chochPrice > 0 && s.chochTimeStart > 0)
   {
      int startCHBar = iBarShift(Symbol(), 0, s.chochTimeStart);
      int confirmedCHBar = -1;

      for (int b = startCHBar - 1; b >= 1; b--)
      {
         if (s.isBullishCHoCH)
         {
            if (Close[b] > s.chochPrice)
            {
               confirmedCHBar = b;
               break;
            }
         }
         else
         {
            if (Close[b] < s.chochPrice)
            {
               confirmedCHBar = b;
               break;
            }
         }
      }

      if (confirmedCHBar > 0)
      {
         s.chochIsConfirmed = true;
         s.chochBreakTime   = Time[confirmedCHBar];
         s.chochBreakPrice  = s.isBullishCHoCH ? High[confirmedCHBar] : Low[confirmedCHBar];
         s.chochTimeEnd     = Time[confirmedCHBar]; // Garis horizontal berakhir tepat di lilin pembalik
         if (s.isBullishCHoCH)
         {
            s.structure = SMC_STRUCT_CHOCH_BUY;
            s.structureName = "BULLISH CHoCH (CONFIRMED REVERSAL)";
         }
         else
         {
            s.structure = SMC_STRUCT_CHOCH_SELL;
            s.structureName = "BEARISH CHoCH (CONFIRMED REVERSAL)";
         }
      }
      else
      {
         s.chochIsConfirmed = false;
         s.chochBreakTime   = 0;
         s.chochBreakPrice  = 0.0;
         s.chochTimeEnd     = Time[0] + (Period() * 60 * 6);
      }
   }

   // -------------------------------------------------------------
   // 4. Deteksi IDM (Inducement Level)
   // -------------------------------------------------------------
   if (lastSwingHigh.price > 0 && lastSwingLow.price > 0)
   {
      int bSH = iBarShift(Symbol(), 0, lastSwingHigh.time);
      int bSL = iBarShift(Symbol(), 0, lastSwingLow.time);

      if (bSL > bSH) // Bullish Wave
      {
         double bestIDMLow = 0.0;
         datetime bestIDMTime = 0;

         for (int m = MathMax(1, bSH); m < bSL; m++)
         {
            if (Low[m] < Low[m - 1] && Low[m] < Low[m + 1] && Low[m] > lastSwingLow.price)
            {
               bestIDMLow = Low[m];
               bestIDMTime = Time[m];
               break;
            }
         }
         if (bestIDMLow <= 0.0 && bSL - bSH >= 2)
         {
            int lowestBar = iLowest(Symbol(), 0, MODE_LOW, bSL - bSH - 1, bSH + 1);
            if (lowestBar > 0 && Low[lowestBar] > lastSwingLow.price)
            {
               bestIDMLow = Low[lowestBar];
               bestIDMTime = Time[lowestBar];
            }
         }

         if (bestIDMLow > 0.0)
         {
            s.hasIDM = true;
            s.idmPrice = bestIDMLow;
            s.idmTime  = bestIDMTime;
            s.isBullishIDM = true;
         }
      }
      else if (bSH > bSL) // Bearish Wave
      {
         double bestIDMHigh = 0.0;
         datetime bestIDMTime = 0;

         for (int m = MathMax(1, bSL); m < bSH; m++)
         {
            if (High[m] > High[m - 1] && High[m] > High[m + 1] && High[m] < lastSwingHigh.price)
            {
               bestIDMHigh = High[m];
               bestIDMTime = Time[m];
               break;
            }
         }
         if (bestIDMHigh <= 0.0 && bSH - bSL >= 2)
         {
            int highestBar = iHighest(Symbol(), 0, MODE_HIGH, bSH - bSL - 1, bSL + 1);
            if (highestBar > 0 && High[highestBar] < lastSwingHigh.price)
            {
               bestIDMHigh = High[highestBar];
               bestIDMTime = Time[highestBar];
            }
         }

         if (bestIDMHigh > 0.0)
         {
            s.hasIDM = true;
            s.idmPrice = bestIDMHigh;
            s.idmTime  = bestIDMTime;
            s.isBullishIDM = false;
         }
      }
   }

   // Fallback IDM: jika belum terdeteksi dari interior wave, ambil minor pullback terdekat
   if (!s.hasIDM && lastSwingHigh.price > 0 && lastSwingLow.price > 0)
   {
      double curEma125 = iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      if (Close[1] >= curEma125)
      {
         int pullBar = iLowest(Symbol(), 0, MODE_LOW, MathMin(15, Bars - 2), 1);
         if (pullBar > 0)
         {
            s.hasIDM = true;
            s.idmPrice = Low[pullBar];
            s.idmTime = Time[pullBar];
            s.isBullishIDM = true;
         }
      }
      else
      {
         int pullBar = iHighest(Symbol(), 0, MODE_HIGH, MathMin(15, Bars - 2), 1);
         if (pullBar > 0)
         {
            s.hasIDM = true;
            s.idmPrice = High[pullBar];
            s.idmTime = Time[pullBar];
            s.isBullishIDM = false;
         }
      }
   }

   return s;
}

//+------------------------------------------------------------------+
//| DETEKSI ORDER BLOCK (OB) DISPLACEMENT ATR & MITIGASI             |
//+------------------------------------------------------------------+
void DetectOrderBlocks(int lookback, double currentAtr)
{
   if (currentAtr <= 0.0) return;
   int limit = MathMin(lookback, InpOBMaxAgeBars);
   double dispThreshold = InpOBDisplacementAtrMult * currentAtr;

   g_bullishOB.isValid = false;
   g_bearishOB.isValid = false;

   // 1. Pemindaian Bullish Order Block (Base Demand Institusional)
   for (int i = 2; i <= limit; i++)
   {
      bool isBearishCandle = (Close[i] < Open[i]);
      
      // Deteksi displacement impulse bullish (1-3 bar penembusan high)
      bool hasDisplacement = false;
      for (int j = 1; j <= MathMin(3, i - 1); j++)
      {
         if ((Close[i - j] - Open[i - j]) >= dispThreshold && Close[i - j] > High[i])
         {
            hasDisplacement = true;
            break;
         }
      }
      if (!hasDisplacement && (Close[i - 1] - Open[i - 1]) >= dispThreshold)
         hasDisplacement = true;

      if (isBearishCandle && hasDisplacement)
      {
         double obTop    = MathMax(Open[i], Close[i]);
         double obBottom = Low[i];

         // Periksa lilin perantara: apakah zona OB pernah di-breakout/dibatalkan (Close < bottom)?
         bool isBroken = false;
         for (int k = i - 1; k >= 1; k--)
         {
            if (Close[k] < obBottom)
            {
               isBroken = true;
               break;
            }
         }
         if (isBroken) continue; // Zona rusak / gagal -> cari OB sebelumnya yang masih utuh

         // Periksa apakah zona OB sudah pernah termitigasi (diuji ulang) sebelum lilin sinyal
         bool isMitigated = false;
         datetime mitTime = 0;
         for (int m = i - 1; m >= 2; m--)
         {
            if (Low[m] <= obTop && High[m] >= obBottom)
            {
               isMitigated = true;
               mitTime = Time[m];
               break;
            }
         }

         g_bullishOB.isValid         = true;
         g_bullishOB.isBullish       = true;
         g_bullishOB.time            = Time[i];
         g_bullishOB.top             = obTop;
         g_bullishOB.bottom          = obBottom;
         g_bullishOB.median          = (obTop + obBottom) / 2.0;
         g_bullishOB.displacementAtr = (Close[i - 1] - Open[i - 1]) / currentAtr;
         g_bullishOB.isMitigated     = isMitigated;
         g_bullishOB.mitigationTime  = mitTime;
         g_bullishOB.barAge          = i;
         break; // Ambil Bullish OB valid terdekat
      }
   }

   // 2. Pemindaian Bearish Order Block (Supply Zone Institusional)
   for (int i = 2; i <= limit; i++)
   {
      bool isBullishCandle = (Close[i] > Open[i]);

      // Deteksi displacement impulse bearish (1-3 bar penembusan low)
      bool hasDisplacement = false;
      for (int j = 1; j <= MathMin(3, i - 1); j++)
      {
         if ((Open[i - j] - Close[i - j]) >= dispThreshold && Close[i - j] < Low[i])
         {
            hasDisplacement = true;
            break;
         }
      }
      if (!hasDisplacement && (Open[i - 1] - Close[i - 1]) >= dispThreshold)
         hasDisplacement = true;

      if (isBullishCandle && hasDisplacement)
      {
         double obTop    = High[i];
         double obBottom = MathMin(Open[i], Close[i]);

         // Periksa lilin perantara: apakah zona OB pernah di-breakout/dibatalkan (Close > top)?
         bool isBroken = false;
         for (int k = i - 1; k >= 1; k--)
         {
            if (Close[k] > obTop)
            {
               isBroken = true;
               break;
            }
         }
         if (isBroken) continue; // Zona rusak / gagal -> cari OB sebelumnya yang masih utuh

         // Periksa apakah zona OB sudah pernah termitigasi sebelum lilin sinyal
         bool isMitigated = false;
         datetime mitTime = 0;
         for (int m = i - 1; m >= 2; m--)
         {
            if (High[m] >= obBottom && Low[m] <= obTop)
            {
               isMitigated = true;
               mitTime = Time[m];
               break;
            }
         }

         g_bearishOB.isValid         = true;
         g_bearishOB.isBullish       = false;
         g_bearishOB.time            = Time[i];
         g_bearishOB.top             = obTop;
         g_bearishOB.bottom          = obBottom;
         g_bearishOB.median          = (obTop + obBottom) / 2.0;
         g_bearishOB.displacementAtr = (Open[i - 1] - Close[i - 1]) / currentAtr;
         g_bearishOB.isMitigated     = isMitigated;
         g_bearishOB.mitigationTime  = mitTime;
         g_bearishOB.barAge          = i;
         break; // Ambil Bearish OB valid terdekat
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
//| MESIN SEKUENSIAL SMC SNIPER: SWEEP -> CHOCH -> FVG RETEST       |
//+------------------------------------------------------------------+
void UpdateSequentialSMCSniper(double currentAtr)
{
   if (!InpUseSequentialSMCSniper) return;
   if (currentAtr <= 0.0) currentAtr = PipToPrice(20.0);

   double slBuffer = PipToPrice(InpSniperSLBufferPips);
   bool isGoldSniper = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
   if (isGoldSniper)
   {
      double goldMinBuf = MathMax(slBuffer, 0.4 * currentAtr);
      if (goldMinBuf < 1.0) goldMinBuf = 1.0; // Minimal $1.00 buffer di balik jarum sweep Gold
      slBuffer = goldMinBuf;
   }
   if (slBuffer <= 0.0) slBuffer = 2.0 * Point * 10.0;

   // =========================================================================
   // 1. STATE MACHINE BULLISH SNIPER (BUY: SWEEP LOW -> CHOCH BULL -> FVG RETEST)
   // =========================================================================

   // --- CHECK INVALIDATION & TIMEOUT UNTUK TAHAP AKTIF ---
   if (g_sniperBUY.stage != SNIPER_STAGE_IDLE)
   {
      // A. Jika harga menembus di bawah titik ekstrem sweep (Wick terendah dijebol = setup batal)
      if (Low[1] < g_sniperBUY.sweepExtreme || Close[1] < g_sniperBUY.sweepExtreme)
      {
         g_sniperBUY.stage = SNIPER_STAGE_IDLE;
         g_sniperBUY.statusText = "IDLE (SWEEP LOW BATAL/DIJEBOL)";
      }
      // B. Cek timeout dari Sweep ke CHoCH
      else if (g_sniperBUY.stage == SNIPER_STAGE_SWEEP_DETECTED)
      {
         int barsSinceSweep = iBarShift(Symbol(), 0, g_sniperBUY.sweepTime);
         if (barsSinceSweep > InpMaxBarsSweepToCHoCH)
         {
            g_sniperBUY.stage = SNIPER_STAGE_IDLE;
            g_sniperBUY.statusText = "IDLE (TIMEOUT MENUNGGU CHOCH)";
         }
      }
      // C. Cek timeout dari CHoCH ke Retest FVG
      else if (g_sniperBUY.stage >= SNIPER_STAGE_CHOCH_CONFIRMED)
      {
         int barsSinceCHoCH = iBarShift(Symbol(), 0, g_sniperBUY.chochTime);
         if (barsSinceCHoCH > InpMaxBarsCHoCHToRetest)
         {
            g_sniperBUY.stage = SNIPER_STAGE_IDLE;
            g_sniperBUY.statusText = "IDLE (TIMEOUT MENUNGGU RETEST FVG)";
         }
      }
   }

   // --- STAGE 0: DETEKSI LIQUIDITY SWEEP DI SWING LOW (SSL) ---
   if (g_sniperBUY.stage == SNIPER_STAGE_IDLE)
   {
      // Pindai 5 lilin terakhir untuk melihat apakah ada sweep swing low yang masih segar
      int scanBars = MathMin(5, Bars - 5);
      for (int b = 1; b <= scanBars; b++)
      {
         // Syarat Sweep: Ekor menembus Swing Low, tapi Candle ditutup di atas Swing Low
         if (lastSwingLow.price > 0 && Low[b] < lastSwingLow.price && Close[b] > lastSwingLow.price)
         {
            g_sniperBUY.stage         = SNIPER_STAGE_SWEEP_DETECTED;
            g_sniperBUY.isBullish     = true;
            g_sniperBUY.sweepTime     = Time[b];
            g_sniperBUY.sweepBarIndex = b;
            g_sniperBUY.sweepLevel    = lastSwingLow.price;
            g_sniperBUY.sweepExtreme  = Low[b];
            g_sniperBUY.hasFVG        = false;
            g_sniperBUY.statusText    = "Stage 1: Sweep Low Terdeteksi @" + DoubleToString(g_sniperBUY.sweepExtreme, Digits);
            break;
         }
      }
   }

   // --- STAGE 1: TUNGGU CHOCH BULLISH DENGAN DISPLACEMENT ---
   if (g_sniperBUY.stage == SNIPER_STAGE_SWEEP_DETECTED)
   {
      int sweepBar = iBarShift(Symbol(), 0, g_sniperBUY.sweepTime);
      double swingResist = (lastSwingHigh.price > 0) ? lastSwingHigh.price : 0.0;
      if (swingResist == 0.0 && prevSwingHigh.price > 0) swingResist = prevSwingHigh.price;

      bool chochFound = false;
      datetime chochT = 0;
      double chochP   = 0.0;

      if (g_smcAnalysis.hasCHoCH && g_smcAnalysis.isBullishCHoCH && g_smcAnalysis.chochBreakTime >= g_sniperBUY.sweepTime)
      {
         chochFound = true;
         chochT     = g_smcAnalysis.chochBreakTime;
         chochP     = g_smcAnalysis.chochPrice;
      }
      else if (swingResist > 0.0)
      {
         for (int b = sweepBar - 1; b >= 1; b--)
         {
            if (Close[b] > swingResist)
            {
               chochFound = true;
               chochT     = Time[b];
               chochP     = swingResist;
               break;
            }
         }
      }

      if (chochFound)
      {
         g_sniperBUY.stage         = SNIPER_STAGE_CHOCH_CONFIRMED;
         g_sniperBUY.chochTime     = chochT;
         g_sniperBUY.chochBarIndex = iBarShift(Symbol(), 0, chochT);
         g_sniperBUY.chochLevel    = chochP;
         g_sniperBUY.statusText    = "Stage 2: Bullish CHoCH Terkonfirmasi";
      }
   }

   // --- STAGE 2: CARI & ARMING BULLISH FAIR VALUE GAP (FVG) ---
   if (g_sniperBUY.stage == SNIPER_STAGE_CHOCH_CONFIRMED)
   {
      int sweepBar = iBarShift(Symbol(), 0, g_sniperBUY.sweepTime);
      bool fvgFound = false;
      double topFVG = 0.0, btmFVG = 0.0;
      datetime timeFVG = 0;
      int idxFVG = 0;

      double minGap = InpMinFVGPoints * Point;

      for (int i = 1; i <= sweepBar; i++)
      {
         if (i + 2 >= Bars) break;
         // Bullish FVG: Low bar i > High bar i+2
         if (Low[i] - High[i + 2] >= minGap)
         {
            fvgFound = true;
            btmFVG   = High[i + 2];
            topFVG   = Low[i];
            timeFVG  = Time[i + 1];
            idxFVG   = i + 1;
            break;
         }
      }

      if (!fvgFound && g_activeFVG.isValid && g_activeFVG.isBullish && g_activeFVG.time >= g_sniperBUY.sweepTime)
      {
         fvgFound = true;
         topFVG   = g_activeFVG.top;
         btmFVG   = g_activeFVG.bottom;
         timeFVG  = g_activeFVG.time;
         idxFVG   = g_activeFVG.barAge;
      }

      if (fvgFound)
      {
         g_sniperBUY.hasFVG        = true;
         g_sniperBUY.fvgTop        = topFVG;
         g_sniperBUY.fvgBottom     = btmFVG;
         g_sniperBUY.fvgMid        = (topFVG + btmFVG) / 2.0;
         g_sniperBUY.fvgTime       = timeFVG;
         g_sniperBUY.fvgBarIndex   = idxFVG;
         g_sniperBUY.stage         = SNIPER_STAGE_FVG_ARMED;
         g_sniperBUY.statusText    = "Stage 3: Bullish FVG Siaga [" + DoubleToString(btmFVG, Digits) + " - " + DoubleToString(topFVG, Digits) + "]";
      }
   }

   // --- STAGE 3: PANTAU RETEST HARGA KE DALAM FVG ---
   if (g_sniperBUY.stage == SNIPER_STAGE_FVG_ARMED)
   {
      double triggerLevel = InpSniperEnterAt50FVG ? g_sniperBUY.fvgMid : g_sniperBUY.fvgTop;
      bool isRetesting = (Low[1] <= triggerLevel && Close[1] >= g_sniperBUY.fvgBottom - (0.2 * currentAtr)) ||
                         (Low[0] <= triggerLevel && Bid >= g_sniperBUY.fvgBottom - (0.2 * currentAtr));

      if (isRetesting)
      {
         g_sniperBUY.stage = SNIPER_STAGE_READY_TO_FIRE;
         g_sniperBUY.entryPrice = Ask;

         // Hitung SL ketat di balik jarum sweep
         g_sniperBUY.recommendedSL = NormalizeDouble(g_sniperBUY.sweepExtreme - slBuffer, Digits);
         double riskDist = Ask - g_sniperBUY.recommendedSL;
         if (riskDist < 10.0 * Point) riskDist = 10.0 * Point;

         // Target TP minimal 1:3 RR
         g_sniperBUY.recommendedTP1 = NormalizeDouble(Ask + (InpSniperMinRR * riskDist), Digits);
         g_sniperBUY.recommendedTP2 = NormalizeDouble(Ask + ((InpSniperMinRR + 1.5) * riskDist), Digits);
         g_sniperBUY.statusText = "Stage 4: FVG Retest SNIPER BUY READY (RR 1:" + DoubleToString(InpSniperMinRR, 1) + ")";
      }
   }


   // =========================================================================
   // 2. STATE MACHINE BEARISH SNIPER (SELL: SWEEP HIGH -> CHOCH BEAR -> FVG RETEST)
   // =========================================================================

   // --- CHECK INVALIDATION & TIMEOUT UNTUK TAHAP AKTIF ---
   if (g_sniperSELL.stage != SNIPER_STAGE_IDLE)
   {
      // A. Jika harga menembus di atas titik ekstrem sweep (Wick tertinggi dijebol = setup batal)
      if (High[1] > g_sniperSELL.sweepExtreme || Close[1] > g_sniperSELL.sweepExtreme)
      {
         g_sniperSELL.stage = SNIPER_STAGE_IDLE;
         g_sniperSELL.statusText = "IDLE (SWEEP HIGH BATAL/DIJEBOL)";
      }
      // B. Cek timeout dari Sweep ke CHoCH
      else if (g_sniperSELL.stage == SNIPER_STAGE_SWEEP_DETECTED)
      {
         int barsSinceSweep = iBarShift(Symbol(), 0, g_sniperSELL.sweepTime);
         if (barsSinceSweep > InpMaxBarsSweepToCHoCH)
         {
            g_sniperSELL.stage = SNIPER_STAGE_IDLE;
            g_sniperSELL.statusText = "IDLE (TIMEOUT MENUNGGU CHOCH)";
         }
      }
      // C. Cek timeout dari CHoCH ke Retest FVG
      else if (g_sniperSELL.stage >= SNIPER_STAGE_CHOCH_CONFIRMED)
      {
         int barsSinceCHoCH = iBarShift(Symbol(), 0, g_sniperSELL.chochTime);
         if (barsSinceCHoCH > InpMaxBarsCHoCHToRetest)
         {
            g_sniperSELL.stage = SNIPER_STAGE_IDLE;
            g_sniperSELL.statusText = "IDLE (TIMEOUT MENUNGGU RETEST FVG)";
         }
      }
   }

   // --- STAGE 0: DETEKSI LIQUIDITY SWEEP DI SWING HIGH (BSL) ---
   if (g_sniperSELL.stage == SNIPER_STAGE_IDLE)
   {
      int scanBars = MathMin(5, Bars - 5);
      for (int b = 1; b <= scanBars; b++)
      {
         // Syarat Sweep: Ekor menembus Swing High, tapi Candle ditutup di bawah Swing High
         if (lastSwingHigh.price > 0 && High[b] > lastSwingHigh.price && Close[b] < lastSwingHigh.price)
         {
            g_sniperSELL.stage         = SNIPER_STAGE_SWEEP_DETECTED;
            g_sniperSELL.isBullish     = false;
            g_sniperSELL.sweepTime     = Time[b];
            g_sniperSELL.sweepBarIndex = b;
            g_sniperSELL.sweepLevel    = lastSwingHigh.price;
            g_sniperSELL.sweepExtreme  = High[b];
            g_sniperSELL.hasFVG        = false;
            g_sniperSELL.statusText    = "Stage 1: Sweep High Terdeteksi @" + DoubleToString(g_sniperSELL.sweepExtreme, Digits);
            break;
         }
      }
   }

   // --- STAGE 1: TUNGGU CHOCH BEARISH DENGAN DISPLACEMENT ---
   if (g_sniperSELL.stage == SNIPER_STAGE_SWEEP_DETECTED)
   {
      int sweepBar = iBarShift(Symbol(), 0, g_sniperSELL.sweepTime);
      double swingSupport = (lastSwingLow.price > 0) ? lastSwingLow.price : 0.0;
      if (swingSupport == 0.0 && prevSwingLow.price > 0) swingSupport = prevSwingLow.price;

      bool chochFound = false;
      datetime chochT = 0;
      double chochP   = 0.0;

      if (g_smcAnalysis.hasCHoCH && !g_smcAnalysis.isBullishCHoCH && g_smcAnalysis.chochBreakTime >= g_sniperSELL.sweepTime)
      {
         chochFound = true;
         chochT     = g_smcAnalysis.chochBreakTime;
         chochP     = g_smcAnalysis.chochPrice;
      }
      else if (swingSupport > 0.0)
      {
         for (int b = sweepBar - 1; b >= 1; b--)
         {
            if (Close[b] < swingSupport)
            {
               chochFound = true;
               chochT     = Time[b];
               chochP     = swingSupport;
               break;
            }
         }
      }

      if (chochFound)
      {
         g_sniperSELL.stage         = SNIPER_STAGE_CHOCH_CONFIRMED;
         g_sniperSELL.chochTime     = chochT;
         g_sniperSELL.chochBarIndex = iBarShift(Symbol(), 0, chochT);
         g_sniperSELL.chochLevel    = chochP;
         g_sniperSELL.statusText    = "Stage 2: Bearish CHoCH Terkonfirmasi";
      }
   }

   // --- STAGE 2: CARI & ARMING BEARISH FAIR VALUE GAP (FVG) ---
   if (g_sniperSELL.stage == SNIPER_STAGE_CHOCH_CONFIRMED)
   {
      int sweepBar = iBarShift(Symbol(), 0, g_sniperSELL.sweepTime);
      bool fvgFound = false;
      double topFVG = 0.0, btmFVG = 0.0;
      datetime timeFVG = 0;
      int idxFVG = 0;

      double minGap = InpMinFVGPoints * Point;

      for (int i = 1; i <= sweepBar; i++)
      {
         if (i + 2 >= Bars) break;
         // Bearish FVG: Low bar i+2 > High bar i
         if (Low[i + 2] - High[i] >= minGap)
         {
            fvgFound = true;
            btmFVG   = High[i];
            topFVG   = Low[i + 2];
            timeFVG  = Time[i + 1];
            idxFVG   = i + 1;
            break;
         }
      }

      if (!fvgFound && g_activeFVG.isValid && !g_activeFVG.isBullish && g_activeFVG.time >= g_sniperSELL.sweepTime)
      {
         fvgFound = true;
         topFVG   = g_activeFVG.top;
         btmFVG   = g_activeFVG.bottom;
         timeFVG  = g_activeFVG.time;
         idxFVG   = g_activeFVG.barAge;
      }

      if (fvgFound)
      {
         g_sniperSELL.hasFVG        = true;
         g_sniperSELL.fvgTop        = topFVG;
         g_sniperSELL.fvgBottom     = btmFVG;
         g_sniperSELL.fvgMid        = (topFVG + btmFVG) / 2.0;
         g_sniperSELL.fvgTime       = timeFVG;
         g_sniperSELL.fvgBarIndex   = idxFVG;
         g_sniperSELL.stage         = SNIPER_STAGE_FVG_ARMED;
         g_sniperSELL.statusText    = "Stage 3: Bearish FVG Siaga [" + DoubleToString(btmFVG, Digits) + " - " + DoubleToString(topFVG, Digits) + "]";
      }
   }

   // --- STAGE 3: PANTAU RETEST HARGA KE DALAM FVG ---
   if (g_sniperSELL.stage == SNIPER_STAGE_FVG_ARMED)
   {
      double triggerLevel = InpSniperEnterAt50FVG ? g_sniperSELL.fvgMid : g_sniperSELL.fvgBottom;
      bool isRetesting = (High[1] >= triggerLevel && Close[1] <= g_sniperSELL.fvgTop + (0.2 * currentAtr)) ||
                         (High[0] >= triggerLevel && Ask <= g_sniperSELL.fvgTop + (0.2 * currentAtr));

      if (isRetesting)
      {
         g_sniperSELL.stage = SNIPER_STAGE_READY_TO_FIRE;
         g_sniperSELL.entryPrice = Bid;

         // Hitung SL ketat di atas jarum sweep
         g_sniperSELL.recommendedSL = NormalizeDouble(g_sniperSELL.sweepExtreme + slBuffer, Digits);
         double riskDist = g_sniperSELL.recommendedSL - Bid;
         if (riskDist < 10.0 * Point) riskDist = 10.0 * Point;

         // Target TP minimal 1:3 RR
         g_sniperSELL.recommendedTP1 = NormalizeDouble(Bid - (InpSniperMinRR * riskDist), Digits);
         g_sniperSELL.recommendedTP2 = NormalizeDouble(Bid - ((InpSniperMinRR + 1.5) * riskDist), Digits);
         g_sniperSELL.statusText = "Stage 4: FVG Retest SNIPER SELL READY (RR 1:" + DoubleToString(InpSniperMinRR, 1) + ")";
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
//+------------------------------------------------------------------+
//| BONUS KONFLUENSI AREA HARGA KUNCI (CONFLUENCE BOOST v3.30)       |
//+------------------------------------------------------------------+
void ApplyCandleConfluenceBoost(CandleAnalysis &c, double ema8, double ema21, double fibo618, double rng)
{
   if (c.pattern != PATTERN_NONE)
   {
      double lowRibbon  = MathMin(ema8, ema21);
      double highRibbon = MathMax(ema8, ema21);

      // Rejection terjadi di Ribbon EMA 8/21 (+10 poin)
      if (c.isBullish && Low[1] <= highRibbon && High[1] >= lowRibbon)
         c.score += 10.0;
      else if (!c.isBullish && High[1] >= lowRibbon && Low[1] <= highRibbon)
         c.score += 10.0;

      // Rejection menguji Golden Pocket 61.8% (+10 poin)
      if (fibo618 > 0.0)
      {
         if (c.isBullish && MathAbs(Low[1] - fibo618) <= (0.35 * rng))
            c.score += 10.0;
         else if (!c.isBullish && MathAbs(High[1] - fibo618) <= (0.35 * rng))
            c.score += 10.0;
      }

      if (c.score > 100.0) c.score = 100.0;
      c.isHighQuality = (c.score >= InpMinCandleScore);
   }
}

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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (Close[1] < Open[1] && Close[2] > Open[2] && Close[1] <= Open[2] && Open[1] >= Close[2])
      {
         c.pattern = PATTERN_ENGULFING;
         c.patternName = "Bearish Engulfing (Absorption)";
         c.isBullish = false;
         c.score = 85.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
   }

   // 3. Pin Bar & Hammer Rejection (80 Poin)
   if (InpUseHammerPinBar)
   {
      // v3.70: threshold diperketat 55%→60% ekor, body 35%→30%
      if (lowerWick >= (0.60 * rng) && body <= (0.30 * rng))
      {
         c.pattern = PATTERN_HAMMER_PINBAR;
         c.patternName = "Bullish Pin Bar / Hammer (Grade A)";
         c.isBullish = true;
         c.score = 80.0 + (lowerWick / rng > 0.70 ? 5.0 : 0.0); // Bonus jika ekor > 70%
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (upperWick >= (0.60 * rng) && body <= (0.30 * rng))
      {
         c.pattern = PATTERN_HAMMER_PINBAR;
         c.patternName = "Bearish Shooting Star / Pin Bar (Grade A)";
         c.isBullish = false;
         c.score = 80.0 + (upperWick / rng > 0.70 ? 5.0 : 0.0);
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
   }

   // 4. Dragonfly Doji & Gravestone Doji (82 Poin)
   if (InpUseDragonflyGravestone)
   {
      // v3.70: Dragonfly body threshold diperketat 10%→8%
      if (lowerWick >= (0.70 * rng) && body <= (0.08 * rng))
      {
         c.pattern = PATTERN_DOJI_REJECTION;
         c.patternName = "Dragonfly Doji (Extreme Rejection A+)";
         c.isBullish = true;
         c.score = 85.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (upperWick >= (0.70 * rng) && body <= (0.08 * rng))
      {
         c.pattern = PATTERN_DOJI_REJECTION;
         c.patternName = "Gravestone Doji (Extreme Rejection A+)";
         c.isBullish = false;
         c.score = 85.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (Close[3] > Open[3] && MathAbs(Close[2] - Open[2]) <= (0.35 * (High[2] - Low[2])) && Close[1] < Open[1] && Close[1] <= ((Open[3] + Close[3]) / 2.0))
      {
         c.pattern = PATTERN_MORNING_EVENING;
         c.patternName = "Evening Star (3-Bar Reversal)";
         c.isBullish = false;
         c.score = 80.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (Close[2] > Open[2] && Close[1] < Open[1] && Open[1] >= High[2] && Close[1] <= ((Open[2] + Close[2]) / 2.0))
      {
         c.pattern = PATTERN_PIERCING_DARKCLOUD;
         c.patternName = "Dark Cloud Cover Pattern";
         c.isBullish = false;
         c.score = 78.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
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
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (MathAbs(High[1] - High[2]) <= pipTol && upperWick >= (0.40 * rng))
      {
         c.pattern = PATTERN_TWEEZER;
         c.patternName = "Tweezer Top Rejection";
         c.isBullish = false;
         c.score = 75.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
   }

   // ============================================================
   // POLA BARU v3.70: SMART PULLBACK CANDLE PATTERNS
   // ============================================================

   // 11. Wick Rejection Series (80 Poin)
   // Dua bar berturut-turut dengan lower/upper wick >= 45% — double test zona
   if (InpUseWickSeries)
   {
      double lw2 = MathMin(Open[2], Close[2]) - Low[2];
      double uw2 = High[2] - MathMax(Open[2], Close[2]);
      double rng2 = High[2] - Low[2];
      if (rng2 > 0)
      {
         // Bullish Wick Series: 2 bar lower wick kuat di area support
         if (lowerWick >= (0.45 * rng) && (lw2 / rng2) >= 0.40)
         {
            c.pattern = PATTERN_HAMMER_PINBAR;
            c.patternName = "Bullish Wick Series (Double-Test Demand)";
            c.isBullish = true;
            c.score = 80.0;
            c.isHighQuality = true;
            ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
         }
         // Bearish Wick Series: 2 bar upper wick kuat di area supply
         else if (upperWick >= (0.45 * rng) && (uw2 / rng2) >= 0.40)
         {
            c.pattern = PATTERN_HAMMER_PINBAR;
            c.patternName = "Bearish Wick Series (Double-Test Supply)";
            c.isBullish = false;
            c.score = 80.0;
            c.isHighQuality = true;
            ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
         }
      }
   }

   // 12. Micro Pullback Pin (82 Poin)
   // Pin Bar body sangat kecil (<20%) — terjadi tepat saat harga touch EMA 8
   if (InpUseMicroPullbackPin)
   {
      double ema8Now = ema8;
      bool touchEma8Bull = (Low[1] <= ema8Now && High[1] >= ema8Now && Close[1] > ema8Now);
      bool touchEma8Bear = (High[1] >= ema8Now && Low[1] <= ema8Now && Close[1] < ema8Now);
      if (touchEma8Bull && lowerWick >= (0.55 * rng) && body <= (0.20 * rng))
      {
         c.pattern = PATTERN_HAMMER_PINBAR;
         c.patternName = "Micro Pin @ EMA8 (Precision Pullback)";
         c.isBullish = true;
         c.score = 82.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
      else if (touchEma8Bear && upperWick >= (0.55 * rng) && body <= (0.20 * rng))
      {
         c.pattern = PATTERN_HAMMER_PINBAR;
         c.patternName = "Micro Shooting Star @ EMA8 (Precision Supply)";
         c.isBullish = false;
         c.score = 82.0;
         c.isHighQuality = true;
         ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
      }
   }

   // 13. Outside Bar Pullback (Presisi XAUUSD Institutional Absorption)
   // Bar sekarang menelan seluruh range bar sebelumnya setelah pullback ke ribbon
   if (InpUseOutsideBarPB)
   {
      double ribbonLow  = MathMin(ema8, ema21);
      double ribbonHigh = MathMax(ema8, ema21);
      bool nearRibbon   = (Low[1] <= ribbonHigh + (rng * 0.2) && High[1] >= ribbonLow - (rng * 0.2));
      if (nearRibbon && High[1] > High[2] && Low[1] < Low[2]) // Menelan range bar sebelumnya
      {
         // Bullish Outside Bar: Menelan range bar 2, ditutup bullish di atas High[2] tanpa ekor atas berlebih
         bool isOBBull = (Close[1] > Open[1] && Close[1] >= High[2] && (High[1] - Close[1]) <= (0.35 * rng));
         // Bearish Outside Bar: Menelan range bar 2, ditutup bearish di bawah Low[2] tanpa ekor bawah berlebih
         bool isOBBear = (Close[1] < Open[1] && Close[1] <= Low[2]  && (Close[1] - Low[1])  <= (0.35 * rng));

         if (isOBBull)
         {
            c.pattern = PATTERN_ENGULFING;
            c.patternName = "Bullish Outside Bar @ Ribbon (Demand Absorption)";
            c.isBullish = true;
            c.score = (Close[1] >= High[1] - (0.20 * rng)) ? 85.0 : 80.0;
            c.isHighQuality = true;
            ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
         }
         else if (isOBBear)
         {
            c.pattern = PATTERN_ENGULFING;
            c.patternName = "Bearish Outside Bar @ Ribbon (Supply Absorption)";
            c.isBullish = false;
            c.score = (Close[1] <= Low[1] + (0.20 * rng)) ? 85.0 : 80.0;
            c.isHighQuality = true;
            ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
         }
      }
   }

   ApplyCandleConfluenceBoost(c, ema8, ema21, fibo618, rng); return c;
}

//+------------------------------------------------------------------+
//| SMART PULLBACK QUALITY ENGINE (v3.70)                            |
//| Menilai kualitas pullback ke ribbon EMA 8/21 (Skor 0-100)       |
//| Hasil >= InpMinPullbackScore (default 60) = pullback valid       |
//+------------------------------------------------------------------+
double CalculatePullbackScore(bool isBuy, double currentAtr)
{
   if (!InpUsePullbackScore) return 100.0; // Bypass jika fitur nonaktif

   double score = 0.0;

   double ema8_1  = iMA(Symbol(), 0, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double ema21_1 = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double ema8_2  = iMA(Symbol(), 0, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 2);
   double ema21_2 = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 2);

   double ribbonLow  = MathMin(ema8_1, ema21_1);
   double ribbonHigh = MathMax(ema8_1, ema21_1);

   // ---------------------------------------------------------------
   // Komponen 1 (+30): Candle rejection terjadi TEPAT di dalam ribbon EMA 8/21
   // Bukan hanya mendekati, tapi memang menyentuh ribbon dari arah yang benar
   // ---------------------------------------------------------------
   bool inRibbonZone = false;
   if (isBuy)
      inRibbonZone = (Low[1] <= ribbonHigh && High[1] >= ribbonLow && Close[1] >= ribbonLow);
   else
      inRibbonZone = (High[1] >= ribbonLow && Low[1] <= ribbonHigh && Close[1] <= ribbonHigh);

   if (inRibbonZone) score += 30.0;

   // ---------------------------------------------------------------
   // Komponen 2 (+20): EMA Zone Depth — price masuk ribbon tapi tidak tembus jauh
   // BUY ideal: Low menyentuh ribbon tapi Close masih di atas ema8
   // SELL ideal: High menyentuh ribbon tapi Close masih di bawah ema8
   // ---------------------------------------------------------------
   if (isBuy && Low[1] <= ribbonHigh && Close[1] > ema8_1)
      score += 20.0;
   else if (!isBuy && High[1] >= ribbonLow && Close[1] < ema8_1)
      score += 20.0;
   else if (inRibbonZone)
      score += 10.0; // Partial bonus

   // ---------------------------------------------------------------
   // Komponen 3 (+20): Ada Displacement/Impulse SEBELUM pullback
   // Scan 10 bar terakhir untuk temukan candle displacement > InpImpulseAtrMult * ATR
   // ---------------------------------------------------------------
   if (InpRequireImpulsePre)
   {
      bool foundImpulse = false;
      double impThresh = InpImpulseAtrMult * currentAtr;
      int scanBars = MathMin(10, Bars - 3);
      for (int k = 2; k <= scanBars; k++)
      {
         double kRange = High[k] - Low[k];
         double kBody  = MathAbs(Close[k] - Open[k]);
         if (kBody >= impThresh)
         {
            // Impulse harus searah trend
            bool impBull = (isBuy  && Close[k] > Open[k] && Close[k] > ema21_1);
            bool impBear = (!isBuy && Close[k] < Open[k] && Close[k] < ema21_1);
            if (impBull || impBear)
            {
               foundImpulse = true;
               break;
            }
         }
      }
      if (foundImpulse) score += 20.0;
   }
   else
      score += 20.0; // Jika filter nonaktif, beri full poin

   // ---------------------------------------------------------------
   // Komponen 4 (+15): Konsolidasi 3+ bar sebelum rejection
   // Harga bergerak lambat (range kecil) selama pullback = legit, bukan spike
   // ---------------------------------------------------------------
   int consolidationBars = 0;
   for (int j = 2; j <= 5; j++)
   {
      double jRange = High[j] - Low[j];
      if (jRange < currentAtr * 0.6) consolidationBars++;
   }
   if (consolidationBars >= 3) score += 15.0;
   else if (consolidationBars >= 2) score += 8.0;

   // ---------------------------------------------------------------
   // Komponen 5 (+15): Volume No-Demand / No-Supply saat pullback
   // Volume bar rejection lebih rendah dari volume impulse sebelumnya
   // ---------------------------------------------------------------
   if (InpUsePBVolumeFilter)
   {
      long volNow = iVolume(Symbol(), 0, 1);
      long volImpulse = 0;
      for (int vi = 2; vi <= 6; vi++)
         if (iVolume(Symbol(), 0, vi) > volImpulse) volImpulse = iVolume(Symbol(), 0, vi);

      if (volImpulse > 0 && volNow < volImpulse * 0.85)
         score += 15.0; // Volume kering = no demand saat pullback (bullish)
      else if (volImpulse > 0 && volNow < volImpulse * 1.0)
         score += 7.0;
   }
   else
      score += 15.0;

   // ---------------------------------------------------------------
   // Komponen 6 (Multi-Bar): Harus ada 2+ bar sentuh ribbon
   // Opsional — jika InpRequireMultiBarPB aktif, score 0 jika hanya 1 bar
   // ---------------------------------------------------------------
   if (InpRequireMultiBarPB)
   {
      int touchCount = 0;
      int lookback = MathMin(InpPullbackLookback, Bars - 3);
      for (int b = 1; b <= lookback; b++)
      {
         double rLow  = MathMin(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b),
                                iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
         double rHigh = MathMax(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b),
                                iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
         if (Low[b] <= rHigh && High[b] >= rLow) touchCount++;
      }
      if (touchCount < 2) return 0.0; // Gagal total jika hanya 1 bar
   }

   return MathMin(100.0, score);
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
//| HIERARKI TREN DOMINAN INSTITUSIONAL: ANTI-MELAWAN TREND (v4.20)  |
//+------------------------------------------------------------------+
ENUM_HTF_BIAS GetDominantTrendBias()
{
   // 1. Data EMA M5 Chart Aktif
   double m5Ema8   = iMA(Symbol(), 0, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double m5Ema21  = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double m5Ema125 = iMA(Symbol(), 0, InpTrendEMA,  0, MODE_EMA, PRICE_CLOSE, 1);
   double m5Close  = Close[1];

   bool m5BullBase = (m5Close > m5Ema125);
   bool m5BearBase = (m5Close < m5Ema125);

   // Mode 1: M5 EMA 125 Baseline Saja
   if (InpTrendAlignment == TREND_ALIGN_M5_BASELINE)
   {
      if (m5BullBase) { g_dominantTrendStr = "BULLISH (M5 > EMA 125)"; return HTF_BIAS_BULLISH; }
      if (m5BearBase) { g_dominantTrendStr = "BEARISH (M5 < EMA 125)"; return HTF_BIAS_BEARISH; }
      g_dominantTrendStr = "NEUTRAL (M5)";
      return HTF_BIAS_NEUTRAL;
   }

   // Mode 2: Triple EMA Stack M5 (8 > 21 > 125)
   if (InpTrendAlignment == TREND_ALIGN_TRIPLE_EMA_STACK)
   {
      if (m5Ema8 > m5Ema21 && m5Ema21 > m5Ema125 && m5Close > m5Ema21)
      {
         g_dominantTrendStr = "STRONG BULLISH (Stack 8>21>125)";
         return HTF_BIAS_BULLISH;
      }
      if (m5Ema8 < m5Ema21 && m5Ema21 < m5Ema125 && m5Close < m5Ema21)
      {
         g_dominantTrendStr = "STRONG BEARISH (Stack 8<21<125)";
         return HTF_BIAS_BEARISH;
      }
      g_dominantTrendStr = "NEUTRAL (EMA Transisi)";
      return HTF_BIAS_NEUTRAL;
   }

   // Mode 3: Dual Timeframe M15 + M5 Alignment (Rekomendasi Pro Institusional)
   if (InpTrendAlignment == TREND_ALIGN_DUAL_M15_M5)
   {
      double m15Ema8   = iMA(Symbol(), PERIOD_M15, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
      double m15Ema21  = iMA(Symbol(), PERIOD_M15, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      double m15Ema125 = iMA(Symbol(), PERIOD_M15, InpTrendEMA,  0, MODE_EMA, PRICE_CLOSE, 1);
      double m15Close  = iClose(Symbol(), PERIOD_M15, 1);

      bool m15Bull = (m15Close > m15Ema125 && m15Ema8 > m15Ema21);
      bool m15Bear = (m15Close < m15Ema125 && m15Ema8 < m15Ema21);

      bool m5Bull  = (m5Close > m5Ema125 && (m5Ema8 > m5Ema21 || m5Close > m5Ema21));
      bool m5Bear  = (m5Close < m5Ema125 && (m5Ema8 < m5Ema21 || m5Close < m5Ema21));

      if (m15Bull && m5Bull)
      {
         g_dominantTrendStr = "STRONG BULLISH (M15+M5 Aligned)";
         return HTF_BIAS_BULLISH;
      }
      if (m15Bear && m5Bear)
      {
         g_dominantTrendStr = "STRONG BEARISH (M15+M5 Aligned)";
         return HTF_BIAS_BEARISH;
      }
      g_dominantTrendStr = "NEUTRAL (M15 vs M5 Pullback Phase)";
      return HTF_BIAS_NEUTRAL;
   }

   // Mode 4: Macro H1 + M5 Alignment
   if (InpTrendAlignment == TREND_ALIGN_MACRO_H1_M5)
   {
      double h1Ema8   = iMA(Symbol(), PERIOD_H1, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
      double h1Ema21  = iMA(Symbol(), PERIOD_H1, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      double h1Ema125 = iMA(Symbol(), PERIOD_H1, InpTrendEMA,  0, MODE_EMA, PRICE_CLOSE, 1);
      double h1Close  = iClose(Symbol(), PERIOD_H1, 1);

      bool h1Bull = (h1Close > h1Ema125 && h1Ema8 > h1Ema21);
      bool h1Bear = (h1Close < h1Ema125 && h1Ema8 < h1Ema21);

      if (h1Bull && m5BullBase)
      {
         g_dominantTrendStr = "STRONG BULLISH (H1+M5 Aligned)";
         return HTF_BIAS_BULLISH;
      }
      if (h1Bear && m5BearBase)
      {
         g_dominantTrendStr = "STRONG BEARISH (H1+M5 Aligned)";
         return HTF_BIAS_BEARISH;
      }
      g_dominantTrendStr = "NEUTRAL (H1 vs M5 Transisi)";
      return HTF_BIAS_NEUTRAL;
   }

   return HTF_BIAS_NEUTRAL;
}

//+------------------------------------------------------------------+
//| MESIN EVALUASI PRO TREND PULLBACK SCALPER (v4.20)                |
//+------------------------------------------------------------------+
ProPullbackResult EvaluateProPullbackSetup(bool isBuy, double currentAtr)
{
   ProPullbackResult res;
   res.isValid = false;
   res.confluenceCount = 0;
   res.confluencesStr = "";
   res.suggestedSL = 0.0;
   res.suggestedTP = 0.0;
   res.pullbackScore = 0.0;
   res.isVSAOk = false;

   if (!InpEnableProPullbackScalper) return res;

   double ema8_1  = iMA(Symbol(), 0, InpFastEMA,   0, MODE_EMA, PRICE_CLOSE, 1);
   double ema21_1 = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
   double ribbonLow  = MathMin(ema8_1, ema21_1);
   double ribbonHigh = MathMax(ema8_1, ema21_1);

   // Confluence 1: Menguji Ribbon EMA 8/21
   bool inRibbon = false;
   if (isBuy)
      inRibbon = (Low[1] <= ribbonHigh && High[1] >= ribbonLow && Close[1] >= ribbonLow);
   else
      inRibbon = (High[1] >= ribbonLow && Low[1] <= ribbonHigh && Close[1] <= ribbonHigh);

   if (inRibbon)
   {
      res.confluenceCount++;
      res.confluencesStr += "Ribbon ";
   }

   // Confluence 2: Golden Pocket Fibo 50% - 78.6%
   if (currentFibo.isValid)
   {
      bool inGP = false;
      if (isBuy)
         inGP = (Low[1] <= currentFibo.level500 && High[1] >= currentFibo.level786);
      else
         inGP = (High[1] >= currentFibo.level500 && Low[1] <= currentFibo.level786);

      if (inGP)
      {
         res.confluenceCount++;
         res.confluencesStr += "FiboGP ";
      }
   }

   // Confluence 3: Fair Value Gap (FVG Imbalance)
   if (g_activeFVG.isValid)
   {
      bool inFVG = false;
      if (isBuy && g_activeFVG.isBullish)
         inFVG = (Low[1] <= g_activeFVG.top && High[1] >= g_activeFVG.bottom);
      else if (!isBuy && !g_activeFVG.isBullish)
         inFVG = (High[1] >= g_activeFVG.bottom && Low[1] <= g_activeFVG.top);

      if (inFVG)
      {
         res.confluenceCount++;
         res.confluencesStr += "FVG ";
      }
   }

   // Confluence 4: Institutional POI (Demand / Supply Zone)
   if (InpUsePOIStalker && g_m15Stalker.isValid)
   {
      if (isBuy && g_m15Stalker.isInDemandPOI)
      {
         res.confluenceCount++;
         res.confluencesStr += "POI-Demand ";
      }
      else if (!isBuy && g_m15Stalker.isInSupplyPOI)
      {
         res.confluenceCount++;
         res.confluencesStr += "POI-Supply ";
      }
   }

   // Confluence 5: Liquidity Sweep (Turtle Soup Inducement)
   if (isBuy && g_smcAnalysis.hasSweep && Low[1] <= lastSwingLow.price && Close[1] > lastSwingLow.price)
   {
      res.confluenceCount++;
      res.confluencesStr += "Sweep-SSL ";
   }
   else if (!isBuy && g_smcAnalysis.hasSweep && High[1] >= lastSwingHigh.price && Close[1] < lastSwingHigh.price)
   {
      res.confluenceCount++;
      res.confluencesStr += "Sweep-BSL ";
   }

   // Evaluasi VSA Volume Exhaustion (No-Supply / No-Demand)
   long volNow = iVolume(Symbol(), 0, 1);
   long volImpulse = 0;
   for (int vi = 2; vi <= 6; vi++)
   {
      long v = iVolume(Symbol(), 0, vi);
      if (v > volImpulse) volImpulse = v;
   }
   res.isVSAOk = (!InpRequireVSAExhaustion || (volImpulse > 0 && volNow <= (long)(volImpulse * 0.90)));
   if (res.isVSAOk && InpRequireVSAExhaustion)
   {
      res.confluenceCount++;
      res.confluencesStr += "VSA-Exhaustion ";
   }

   // Evaluasi Rejection Candle Trigger:
   // Untuk BUY: candle ditutup di atas EMA 8 dan memiliki ekor bawah atau badan bullish
   // Untuk SELL: candle ditutup di bawah EMA 8 dan memiliki ekor atas atau badan bearish
   bool triggerOk = false;
   if (isBuy)
      triggerOk = (Close[1] > ema8_1 && (Close[1] > Open[1] || (High[1] - Low[1] > 0 && (MathMin(Open[1], Close[1]) - Low[1]) / (High[1] - Low[1]) >= 0.30)));
   else
      triggerOk = (Close[1] < ema8_1 && (Close[1] < Open[1] || (High[1] - Low[1] > 0 && (High[1] - MathMax(Open[1], Close[1])) / (High[1] - Low[1]) >= 0.30)));

   if (res.confluenceCount >= InpMinPullbackConfluences && triggerOk && res.isVSAOk)
   {
      res.isValid = true;
      res.pullbackScore = CalculatePullbackScore(isBuy, currentAtr);

      // Hitung Target Scalping Cerdas (TP di Swing Terdekat atau Fixed 150 Pips)
      if (isBuy)
      {
         if (InpTPType == TP_TYPE_FIXED_PIPS)
            res.suggestedTP = Ask + PipToPrice(InpFixedTPPips);
         else if (InpFastScalpTP1AtSwing && lastSwingHigh.price > Ask + (5 * Point))
            res.suggestedTP = lastSwingHigh.price;
         else
            res.suggestedTP = Ask + (InpRiskRewardRatio * (Ask - (Low[1] - (InpSLBufferAtrMult * currentAtr))));

         res.suggestedSL = Low[1] - (InpSLBufferAtrMult * currentAtr);
      }
      else
      {
         if (InpTPType == TP_TYPE_FIXED_PIPS)
            res.suggestedTP = Bid - PipToPrice(InpFixedTPPips);
         else if (InpFastScalpTP1AtSwing && lastSwingLow.price < Bid - (5 * Point) && lastSwingLow.price > 0)
            res.suggestedTP = lastSwingLow.price;
         else
            res.suggestedTP = Bid - (InpRiskRewardRatio * (((High[1] + (InpSLBufferAtrMult * currentAtr)) - Bid)));

         res.suggestedSL = High[1] + (InpSLBufferAtrMult * currentAtr);
      }
   }

   return res;
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
   currentFibo.isBullish = isBullish;
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

      // Cek Invalidasi & Kadaluwarsa Fibo (Auto-Clean saat ditembus)
      if (InpAutoCleanBrokenFibo)
      {
         // 1. Ditembus Rusak: Struktur Swing Low (Level 100%) ditembus/dijebol
         if (Close[1] < currentFibo.level100 || Low[0] < currentFibo.level100)
         {
            currentFibo.isValid = false;
            return;
         }
         // 2. Ditembus Rusak Deep Pocket: Lilin ditutup menembus level 78.6%
         if (InpInvalidateOnClose786 && Close[1] < currentFibo.level786)
         {
            currentFibo.isValid = false;
            return;
         }
         // 3. Kadaluwarsa / Ekspansi Baru: Harga sudah menembus High lama (Level 0%)
         if (Close[1] > currentFibo.level000 + (0.05 * range))
         {
            currentFibo.isValid = false;
            return;
         }
      }
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

      // Cek Invalidasi & Kadaluwarsa Fibo (Auto-Clean saat ditembus)
      if (InpAutoCleanBrokenFibo)
      {
         // 1. Ditembus Rusak: Struktur Swing High (Level 100%) ditembus/dijebol
         if (Close[1] > currentFibo.level100 || High[0] > currentFibo.level100)
         {
            currentFibo.isValid = false;
            return;
         }
         // 2. Ditembus Rusak Deep Pocket: Lilin ditutup menembus level 78.6%
         if (InpInvalidateOnClose786 && Close[1] > currentFibo.level786)
         {
            currentFibo.isValid = false;
            return;
         }
         // 3. Kadaluwarsa / Ekspansi Baru: Harga sudah menembus Low lama (Level 0%)
         if (Close[1] < currentFibo.level000 - (0.05 * range))
         {
            currentFibo.isValid = false;
            return;
         }
      }
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
      if (StringFind(name, "VIKAR_SMC_") == 0 || StringFind(name, "VIKAR_M15_") == 0 || StringFind(name, "VIKAR_M5_") == 0 || StringFind(name, "VIKAR_POI_") == 0 || StringFind(name, "VIKAR_PIVOT_") == 0 || StringFind(name, "VIKAR_FIBO_") == 0 || StringFind(name, "VIKAR_SWING_") == 0)
         ObjectDelete(name);
   }
}

void DrawSMCObjectsOnChart()
{
   datetime tNowExt = Time[0] + (Period() * 60 * 10);
   datetime tLblPos = Time[0] + (Period() * 60 * 2);

   // --- 1. VISUALISASI KOTAK ORDER BLOCK & FVG (ZONE RECTANGLES) ---
   if (InpDrawSMCOnChart)
   {
      datetime tOBEnd = Time[0] + (Period() * 60 * 10);

      // Gambar Bullish OB (Base Demand)
      if (g_bullishOB.isValid)
      {
         string name = "VIKAR_SMC_BULL_OB";
         if (ObjectFind(name) < 0) ObjectCreate(name, OBJ_RECTANGLE, 0, g_bullishOB.time, g_bullishOB.top, tOBEnd, g_bullishOB.bottom);
         else
         {
            ObjectSet(name, OBJPROP_TIME1, g_bullishOB.time);
            ObjectSet(name, OBJPROP_PRICE1, g_bullishOB.top);
            ObjectSet(name, OBJPROP_TIME2, tOBEnd);
            ObjectSet(name, OBJPROP_PRICE2, g_bullishOB.bottom);
         }
         ObjectSet(name, OBJPROP_COLOR, InpColorBullishOB);
         ObjectSet(name, OBJPROP_BACK, true);
      }
      else
      {
         ObjectDelete("VIKAR_SMC_BULL_OB");
      }

      // Gambar Bearish OB (Supply Zone)
      if (g_bearishOB.isValid)
      {
         string name = "VIKAR_SMC_BEAR_OB";
         if (ObjectFind(name) < 0) ObjectCreate(name, OBJ_RECTANGLE, 0, g_bearishOB.time, g_bearishOB.top, tOBEnd, g_bearishOB.bottom);
         else
         {
            ObjectSet(name, OBJPROP_TIME1, g_bearishOB.time);
            ObjectSet(name, OBJPROP_PRICE1, g_bearishOB.top);
            ObjectSet(name, OBJPROP_TIME2, tOBEnd);
            ObjectSet(name, OBJPROP_PRICE2, g_bearishOB.bottom);
         }
         ObjectSet(name, OBJPROP_COLOR, InpColorBearishOB);
         ObjectSet(name, OBJPROP_BACK, true);
      }
      else
      {
         ObjectDelete("VIKAR_SMC_BEAR_OB");
      }

      // Gambar FVG Imbalance
      if (g_activeFVG.isValid && !g_activeFVG.isMitigated)
      {
         string name = "VIKAR_SMC_FVG";
         if (ObjectFind(name) < 0) ObjectCreate(name, OBJ_RECTANGLE, 0, g_activeFVG.time, g_activeFVG.top, tOBEnd, g_activeFVG.bottom);
         else
         {
            ObjectSet(name, OBJPROP_TIME1, g_activeFVG.time);
            ObjectSet(name, OBJPROP_PRICE1, g_activeFVG.top);
            ObjectSet(name, OBJPROP_TIME2, tOBEnd);
            ObjectSet(name, OBJPROP_PRICE2, g_activeFVG.bottom);
         }
         ObjectSet(name, OBJPROP_COLOR, InpColorFVG);
         ObjectSet(name, OBJPROP_BACK, true);
      }
      else
      {
         ObjectDelete("VIKAR_SMC_FVG");
      }

      // Gambar Zona SMC Sniper (Sweep -> CHoCH -> FVG Retest)
      if (InpUseSequentialSMCSniper)
      {
         string sniperBuyZone = "VIKAR_SMC_SNIPER_BUY_ZONE";
         string sniperBuyLbl  = "VIKAR_SMC_SNIPER_BUY_LBL";
         if (g_sniperBUY.stage >= SNIPER_STAGE_FVG_ARMED && g_sniperBUY.hasFVG)
         {
            datetime tBuyEnd = Time[0] + (Period() * 60 * 12);
            if (ObjectFind(sniperBuyZone) < 0)
               ObjectCreate(sniperBuyZone, OBJ_RECTANGLE, 0, g_sniperBUY.fvgTime, g_sniperBUY.fvgTop, tBuyEnd, g_sniperBUY.fvgBottom);
            else
            {
               ObjectSet(sniperBuyZone, OBJPROP_TIME1, g_sniperBUY.fvgTime);
               ObjectSet(sniperBuyZone, OBJPROP_PRICE1, g_sniperBUY.fvgTop);
               ObjectSet(sniperBuyZone, OBJPROP_TIME2, tBuyEnd);
               ObjectSet(sniperBuyZone, OBJPROP_PRICE2, g_sniperBUY.fvgBottom);
            }
            ObjectSet(sniperBuyZone, OBJPROP_COLOR, (g_sniperBUY.stage == SNIPER_STAGE_READY_TO_FIRE) ? clrSpringGreen : clrGold);
            ObjectSet(sniperBuyZone, OBJPROP_BACK, true);

            if (ObjectFind(sniperBuyLbl) < 0)
               ObjectCreate(sniperBuyLbl, OBJ_TEXT, 0, tLblPos, g_sniperBUY.fvgMid);
            else
            {
               ObjectSet(sniperBuyLbl, OBJPROP_TIME1, tLblPos);
               ObjectSet(sniperBuyLbl, OBJPROP_PRICE1, g_sniperBUY.fvgMid);
            }
            string lblText = (g_sniperBUY.stage == SNIPER_STAGE_READY_TO_FIRE) ? "★ SNIPER FVG BUY READY (1:3+ RR)" : "SNIPER FVG BUY ARMED";
            ObjectSetText(sniperBuyLbl, lblText, 8, "Segoe UI Bold", clrSpringGreen);
         }
         else
         {
            ObjectDelete(sniperBuyZone);
            ObjectDelete(sniperBuyLbl);
         }

         string sniperSellZone = "VIKAR_SMC_SNIPER_SELL_ZONE";
         string sniperSellLbl  = "VIKAR_SMC_SNIPER_SELL_LBL";
         if (g_sniperSELL.stage >= SNIPER_STAGE_FVG_ARMED && g_sniperSELL.hasFVG)
         {
            datetime tSellEnd = Time[0] + (Period() * 60 * 12);
            if (ObjectFind(sniperSellZone) < 0)
               ObjectCreate(sniperSellZone, OBJ_RECTANGLE, 0, g_sniperSELL.fvgTime, g_sniperSELL.fvgTop, tSellEnd, g_sniperSELL.fvgBottom);
            else
            {
               ObjectSet(sniperSellZone, OBJPROP_TIME1, g_sniperSELL.fvgTime);
               ObjectSet(sniperSellZone, OBJPROP_PRICE1, g_sniperSELL.fvgTop);
               ObjectSet(sniperSellZone, OBJPROP_TIME2, tSellEnd);
               ObjectSet(sniperSellZone, OBJPROP_PRICE2, g_sniperSELL.fvgBottom);
            }
            ObjectSet(sniperSellZone, OBJPROP_COLOR, (g_sniperSELL.stage == SNIPER_STAGE_READY_TO_FIRE) ? clrTomato : clrGold);
            ObjectSet(sniperSellZone, OBJPROP_BACK, true);

            if (ObjectFind(sniperSellLbl) < 0)
               ObjectCreate(sniperSellLbl, OBJ_TEXT, 0, tLblPos, g_sniperSELL.fvgMid);
            else
            {
               ObjectSet(sniperSellLbl, OBJPROP_TIME1, tLblPos);
               ObjectSet(sniperSellLbl, OBJPROP_PRICE1, g_sniperSELL.fvgMid);
            }
            string lblText = (g_sniperSELL.stage == SNIPER_STAGE_READY_TO_FIRE) ? "★ SNIPER FVG SELL READY (1:3+ RR)" : "SNIPER FVG SELL ARMED";
            ObjectSetText(sniperSellLbl, lblText, 8, "Segoe UI Bold", clrTomato);
         }
         else
         {
            ObjectDelete(sniperSellZone);
            ObjectDelete(sniperSellLbl);
         }
      }
      else
      {
         ObjectDelete("VIKAR_SMC_SNIPER_BUY_ZONE");
         ObjectDelete("VIKAR_SMC_SNIPER_BUY_LBL");
         ObjectDelete("VIKAR_SMC_SNIPER_SELL_ZONE");
         ObjectDelete("VIKAR_SMC_SNIPER_SELL_LBL");
      }
   }
   else
   {
      ObjectDelete("VIKAR_SMC_BULL_OB");
      ObjectDelete("VIKAR_SMC_BEAR_OB");
      ObjectDelete("VIKAR_SMC_FVG");
      ObjectDelete("VIKAR_SMC_SNIPER_BUY_ZONE");
      ObjectDelete("VIKAR_SMC_SNIPER_BUY_LBL");
      ObjectDelete("VIKAR_SMC_SNIPER_SELL_ZONE");
      ObjectDelete("VIKAR_SMC_SNIPER_SELL_LBL");
   }

   // --- 2. VISUALISASI STRUKTUR PASAR: BOS, CHOCH, SSS, IDM ---
   if (InpDrawStructureLines)
   {
      double curAtr = iATR(Symbol(), 0, 14, 1);
      if (curAtr <= 0.0) curAtr = Point * 20;

      // 1. Gambar BOS (Break of Structure) & Lilin Penembus
      string bosLine   = "VIKAR_SMC_BOS_LINE";
      string bosLbl    = "VIKAR_SMC_BOS_LBL";
      string bosMarker = "VIKAR_SMC_BOS_MARKER";
      if (g_smcAnalysis.hasBOS && g_smcAnalysis.bosPrice > 0)
      {
         datetime tBOS1 = g_smcAnalysis.bosTimeStart;
         if (tBOS1 <= 0 || tBOS1 > Time[0]) tBOS1 = Time[MathMin(30, Bars - 2)];
         datetime tBOS2 = g_smcAnalysis.bosTimeEnd;
         if (tBOS2 <= tBOS1) tBOS2 = tBOS1 + (Period() * 60 * 6);

         if (ObjectFind(bosLine) < 0)
            ObjectCreate(bosLine, OBJ_TREND, 0, tBOS1, g_smcAnalysis.bosPrice, tBOS2, g_smcAnalysis.bosPrice);
         else
         {
            ObjectSet(bosLine, OBJPROP_TIME1, tBOS1);
            ObjectSet(bosLine, OBJPROP_PRICE1, g_smcAnalysis.bosPrice);
            ObjectSet(bosLine, OBJPROP_TIME2, tBOS2);
            ObjectSet(bosLine, OBJPROP_PRICE2, g_smcAnalysis.bosPrice);
         }
         ObjectSet(bosLine, OBJPROP_COLOR, InpColorBOS);
         ObjectSet(bosLine, OBJPROP_STYLE, STYLE_DASH);
         ObjectSet(bosLine, OBJPROP_WIDTH, 1);
         ObjectSet(bosLine, OBJPROP_RAY, false);
         ObjectSet(bosLine, OBJPROP_BACK, false);

         datetime tBOSLbl = tLblPos;
         double   pBOSLbl = g_smcAnalysis.bosPrice;

         // Tandai lilin tertutup yang membentuk BOS
         if (g_smcAnalysis.bosIsConfirmed && g_smcAnalysis.bosBreakTime > 0)
         {
            int bBar = iBarShift(Symbol(), 0, g_smcAnalysis.bosBreakTime);
            if (bBar >= 0)
            {
               tBOSLbl = g_smcAnalysis.bosBreakTime;
               pBOSLbl = g_smcAnalysis.isBullishBOS ? (High[bBar] + (curAtr * 0.15)) : (Low[bBar] - (curAtr * 0.15));

               double pMarker = g_smcAnalysis.isBullishBOS ? (Low[bBar] - (curAtr * 0.15)) : (High[bBar] + (curAtr * 0.15));
               int arrowCode  = g_smcAnalysis.isBullishBOS ? 233 : 234; // Panah atas (233) / Panah bawah (234)

               if (ObjectFind(bosMarker) < 0)
                  ObjectCreate(bosMarker, OBJ_ARROW, 0, g_smcAnalysis.bosBreakTime, pMarker);
               else
               {
                  ObjectSet(bosMarker, OBJPROP_TIME1, g_smcAnalysis.bosBreakTime);
                  ObjectSet(bosMarker, OBJPROP_PRICE1, pMarker);
               }
               ObjectSet(bosMarker, OBJPROP_ARROWCODE, arrowCode);
               ObjectSet(bosMarker, OBJPROP_COLOR, InpColorBOS);
               ObjectSet(bosMarker, OBJPROP_WIDTH, 2);
            }
         }
         else
         {
            ObjectDelete(bosMarker);
         }

         // Label "BOS" saja
         if (ObjectFind(bosLbl) < 0)
            ObjectCreate(bosLbl, OBJ_TEXT, 0, tBOSLbl, pBOSLbl);
         else
         {
            ObjectSet(bosLbl, OBJPROP_TIME1, tBOSLbl);
            ObjectSet(bosLbl, OBJPROP_PRICE1, pBOSLbl);
         }
         ObjectSetText(bosLbl, "BOS", 9, "Segoe UI Bold", InpColorBOS);
      }
      else
      {
         ObjectDelete(bosLine);
         ObjectDelete(bosLbl);
         ObjectDelete(bosMarker);
      }

      // 2. Gambar CHoCH (Change of Character) & Lilin Pembalik
      string chochLine   = "VIKAR_SMC_CHOCH_LINE";
      string chochLbl    = "VIKAR_SMC_CHOCH_LBL";
      string chochMarker = "VIKAR_SMC_CHOCH_MARKER";
      if (g_smcAnalysis.hasCHoCH && g_smcAnalysis.chochPrice > 0)
      {
         datetime tCH1 = g_smcAnalysis.chochTimeStart;
         if (tCH1 <= 0 || tCH1 > Time[0]) tCH1 = Time[MathMin(25, Bars - 2)];
         datetime tCH2 = g_smcAnalysis.chochTimeEnd;
         if (tCH2 <= tCH1) tCH2 = tCH1 + (Period() * 60 * 6);

         if (ObjectFind(chochLine) < 0)
            ObjectCreate(chochLine, OBJ_TREND, 0, tCH1, g_smcAnalysis.chochPrice, tCH2, g_smcAnalysis.chochPrice);
         else
         {
            ObjectSet(chochLine, OBJPROP_TIME1, tCH1);
            ObjectSet(chochLine, OBJPROP_PRICE1, g_smcAnalysis.chochPrice);
            ObjectSet(chochLine, OBJPROP_TIME2, tCH2);
            ObjectSet(chochLine, OBJPROP_PRICE2, g_smcAnalysis.chochPrice);
         }
         ObjectSet(chochLine, OBJPROP_COLOR, InpColorCHoCH);
         ObjectSet(chochLine, OBJPROP_STYLE, STYLE_SOLID);
         ObjectSet(chochLine, OBJPROP_WIDTH, 2);
         ObjectSet(chochLine, OBJPROP_RAY, false);
         ObjectSet(chochLine, OBJPROP_BACK, false);

         datetime tCHLbl = tLblPos;
         double   pCHLbl = g_smcAnalysis.chochPrice;

         // Tandai lilin tertutup yang membentuk CHoCH
         if (g_smcAnalysis.chochIsConfirmed && g_smcAnalysis.chochBreakTime > 0)
         {
            int cBar = iBarShift(Symbol(), 0, g_smcAnalysis.chochBreakTime);
            if (cBar >= 0)
            {
               tCHLbl = g_smcAnalysis.chochBreakTime;
               pCHLbl = g_smcAnalysis.isBullishCHoCH ? (High[cBar] + (curAtr * 0.15)) : (Low[cBar] - (curAtr * 0.15));

               double pMarker = g_smcAnalysis.isBullishCHoCH ? (Low[cBar] - (curAtr * 0.15)) : (High[cBar] + (curAtr * 0.15));
               int arrowCode  = g_smcAnalysis.isBullishCHoCH ? 233 : 234;

               if (ObjectFind(chochMarker) < 0)
                  ObjectCreate(chochMarker, OBJ_ARROW, 0, g_smcAnalysis.chochBreakTime, pMarker);
               else
               {
                  ObjectSet(chochMarker, OBJPROP_TIME1, g_smcAnalysis.chochBreakTime);
                  ObjectSet(chochMarker, OBJPROP_PRICE1, pMarker);
               }
               ObjectSet(chochMarker, OBJPROP_ARROWCODE, arrowCode);
               ObjectSet(chochMarker, OBJPROP_COLOR, InpColorCHoCH);
               ObjectSet(chochMarker, OBJPROP_WIDTH, 2);
            }
         }
         else
         {
            ObjectDelete(chochMarker);
         }

         // Label "CHoCH" saja
         if (ObjectFind(chochLbl) < 0)
            ObjectCreate(chochLbl, OBJ_TEXT, 0, tCHLbl, pCHLbl);
         else
         {
            ObjectSet(chochLbl, OBJPROP_TIME1, tCHLbl);
            ObjectSet(chochLbl, OBJPROP_PRICE1, pCHLbl);
         }
         ObjectSetText(chochLbl, "CHoCH", 9, "Segoe UI Bold", InpColorCHoCH);
      }
      else
      {
         ObjectDelete(chochLine);
         ObjectDelete(chochLbl);
         ObjectDelete(chochMarker);
      }

      // 3. Gambar SSS (Smart Money Sweep / Liquidity Sweep)
      string sssLine = "VIKAR_SMC_SSS_LINE";
      string sssLbl  = "VIKAR_SMC_SSS_LBL";
      if (g_smcAnalysis.hasSweep && g_smcAnalysis.sweepPriceLevel > 0)
      {
         datetime tSS1 = g_smcAnalysis.sweepTimeStart;
         if (tSS1 <= 0 || tSS1 > Time[0]) tSS1 = Time[MathMin(20, Bars - 2)];
         datetime tSS2 = tNowExt;
         if (tSS2 <= tSS1) tSS2 = tSS1 + (Period() * 60 * 6);

         if (ObjectFind(sssLine) < 0)
            ObjectCreate(sssLine, OBJ_TREND, 0, tSS1, g_smcAnalysis.sweepPriceLevel, tSS2, g_smcAnalysis.sweepPriceLevel);
         else
         {
            ObjectSet(sssLine, OBJPROP_TIME1, tSS1);
            ObjectSet(sssLine, OBJPROP_PRICE1, g_smcAnalysis.sweepPriceLevel);
            ObjectSet(sssLine, OBJPROP_TIME2, tSS2);
            ObjectSet(sssLine, OBJPROP_PRICE2, g_smcAnalysis.sweepPriceLevel);
         }
         ObjectSet(sssLine, OBJPROP_COLOR, InpColorSSS);
         ObjectSet(sssLine, OBJPROP_STYLE, STYLE_DASHDOT);
         ObjectSet(sssLine, OBJPROP_WIDTH, 1);
         ObjectSet(sssLine, OBJPROP_RAY, false);
         ObjectSet(sssLine, OBJPROP_BACK, false);

         if (ObjectFind(sssLbl) < 0)
            ObjectCreate(sssLbl, OBJ_TEXT, 0, tLblPos, g_smcAnalysis.sweepPriceLevel);
         else
         {
            ObjectSet(sssLbl, OBJPROP_TIME1, tLblPos);
            ObjectSet(sssLbl, OBJPROP_PRICE1, g_smcAnalysis.sweepPriceLevel);
         }
         ObjectSetText(sssLbl, "SSS", 8, "Segoe UI Bold", InpColorSSS);
      }
      else
      {
         ObjectDelete(sssLine);
         ObjectDelete(sssLbl);
      }

      // 4. Gambar IDM (Inducement Level)
      string idmLine = "VIKAR_SMC_IDM_LINE";
      string idmLbl  = "VIKAR_SMC_IDM_LBL";
      if (g_smcAnalysis.hasIDM && g_smcAnalysis.idmPrice > 0)
      {
         datetime tIDM1 = g_smcAnalysis.idmTime;
         if (tIDM1 <= 0 || tIDM1 > Time[0]) tIDM1 = Time[MathMin(15, Bars - 2)];
         datetime tIDM2 = tNowExt;
         if (tIDM2 <= tIDM1) tIDM2 = tIDM1 + (Period() * 60 * 6);

         if (ObjectFind(idmLine) < 0)
            ObjectCreate(idmLine, OBJ_TREND, 0, tIDM1, g_smcAnalysis.idmPrice, tIDM2, g_smcAnalysis.idmPrice);
         else
         {
            ObjectSet(idmLine, OBJPROP_TIME1, tIDM1);
            ObjectSet(idmLine, OBJPROP_PRICE1, g_smcAnalysis.idmPrice);
            ObjectSet(idmLine, OBJPROP_TIME2, tIDM2);
            ObjectSet(idmLine, OBJPROP_PRICE2, g_smcAnalysis.idmPrice);
         }
         ObjectSet(idmLine, OBJPROP_COLOR, InpColorIDM);
         ObjectSet(idmLine, OBJPROP_STYLE, STYLE_DOT);
         ObjectSet(idmLine, OBJPROP_WIDTH, 1);
         ObjectSet(idmLine, OBJPROP_RAY, false);
         ObjectSet(idmLine, OBJPROP_BACK, false);

         if (ObjectFind(idmLbl) < 0)
            ObjectCreate(idmLbl, OBJ_TEXT, 0, tLblPos, g_smcAnalysis.idmPrice);
         else
         {
            ObjectSet(idmLbl, OBJPROP_TIME1, tLblPos);
            ObjectSet(idmLbl, OBJPROP_PRICE1, g_smcAnalysis.idmPrice);
         }
         ObjectSetText(idmLbl, "IDM", 8, "Segoe UI Bold", InpColorIDM);
      }
      else
      {
         ObjectDelete(idmLine);
         ObjectDelete(idmLbl);
      }
   }
   else
   {
      ObjectDelete("VIKAR_SMC_BOS_LINE");
      ObjectDelete("VIKAR_SMC_BOS_LBL");
      ObjectDelete("VIKAR_SMC_BOS_MARKER");
      ObjectDelete("VIKAR_SMC_CHOCH_LINE");
      ObjectDelete("VIKAR_SMC_CHOCH_LBL");
      ObjectDelete("VIKAR_SMC_CHOCH_MARKER");
      ObjectDelete("VIKAR_SMC_SSS_LINE");
      ObjectDelete("VIKAR_SMC_SSS_LBL");
      ObjectDelete("VIKAR_SMC_IDM_LINE");
      ObjectDelete("VIKAR_SMC_IDM_LBL");
   }

   // --- 3. GAMBAR GARIS AYUNAN STRUKTUR (KANDEL LAMA KE KANDEL BARU) ---
   DrawSwingStructureOnChart();
}

//+------------------------------------------------------------------+
//| ON-CHART SWING STRUCTURE ZIGZAG VISUALIZER (VALID LEGS)          |
//+------------------------------------------------------------------+
void CleanSwingStructureObjects()
{
   for (int i = 0; i < 10; i++)
   {
      ObjectDelete("VIKAR_SWING_LEG_" + IntegerToString(i));
      ObjectDelete("VIKAR_SWING_LBL_" + IntegerToString(i));
   }
   ObjectDelete("VIKAR_SWING_LEG_LIVE");
}

void DrawSwingStructureOnChart()
{
   if (!InpDrawSwingLines || g_validSwingCount < 2)
   {
      CleanSwingStructureObjects();
      return;
   }

   int maxLegs = MathMin(InpMaxSwingLegs, g_validSwingCount - 1);
   int startK = g_validSwingCount - 1 - maxLegs;

   CleanSwingStructureObjects();

   int legNum = 0;
   for (int k = startK; k < g_validSwingCount - 1; k++)
   {
      string lineName = "VIKAR_SWING_LEG_" + IntegerToString(legNum);
      string lblName  = "VIKAR_SWING_LBL_" + IntegerToString(legNum);

      datetime t1 = g_validSwings[k].time;
      double   p1 = g_validSwings[k].price;
      datetime t2 = g_validSwings[k + 1].time;
      double   p2 = g_validSwings[k + 1].price;

      bool isGoingUp = (p2 > p1);
      color legClr = isGoingUp ? InpColorSwingUp : InpColorSwingDown;

      // 1. Garis Penghubung Ayunan Struktur Lilin Lama ke Lilin Baru
      if (ObjectFind(lineName) < 0)
         ObjectCreate(lineName, OBJ_TREND, 0, t1, p1, t2, p2);
      else
      {
         ObjectSet(lineName, OBJPROP_TIME1, t1);
         ObjectSet(lineName, OBJPROP_PRICE1, p1);
         ObjectSet(lineName, OBJPROP_TIME2, t2);
         ObjectSet(lineName, OBJPROP_PRICE2, p2);
      }
      ObjectSet(lineName, OBJPROP_COLOR, legClr);
      ObjectSet(lineName, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSet(lineName, OBJPROP_WIDTH, 2);
      ObjectSet(lineName, OBJPROP_RAY, false);
      ObjectSet(lineName, OBJPROP_BACK, false);

      // 2. Label Puncak / Lembah (HH, HL, LH, LL) di Ujung Lilin
      string tag = g_validSwings[k + 1].label;
      if (tag != "")
      {
         if (ObjectFind(lblName) < 0)
            ObjectCreate(lblName, OBJ_TEXT, 0, t2, p2);
         else
         {
            ObjectSet(lblName, OBJPROP_TIME1, t2);
            ObjectSet(lblName, OBJPROP_PRICE1, p2);
         }
         string textDisp = " [" + tag + " " + DoubleToString(p2, Digits) + "]";
         ObjectSetText(lblName, textDisp, 7, "Segoe UI Bold", legClr);
      }

      legNum++;
   }

   // 3. Garis Live Menghubungkan Ayunan Terakhir ke Lilin Berjalan (Candle [0])
   if (g_validSwingCount >= 1)
   {
      string liveLine = "VIKAR_SWING_LEG_LIVE";
      datetime tLast = g_validSwings[g_validSwingCount - 1].time;
      double   pLast = g_validSwings[g_validSwingCount - 1].price;
      datetime tNow  = Time[0];
      double   pNow  = Close[0];

      bool liveUp = (pNow > pLast);
      color liveClr = liveUp ? InpColorSwingUp : InpColorSwingDown;

      if (ObjectFind(liveLine) < 0)
         ObjectCreate(liveLine, OBJ_TREND, 0, tLast, pLast, tNow, pNow);
      else
      {
         ObjectSet(liveLine, OBJPROP_TIME1, tLast);
         ObjectSet(liveLine, OBJPROP_PRICE1, pLast);
         ObjectSet(liveLine, OBJPROP_TIME2, tNow);
         ObjectSet(liveLine, OBJPROP_PRICE2, pNow);
      }
      ObjectSet(liveLine, OBJPROP_COLOR, liveClr);
      ObjectSet(liveLine, OBJPROP_STYLE, STYLE_DOT);
      ObjectSet(liveLine, OBJPROP_WIDTH, 1);
      ObjectSet(liveLine, OBJPROP_RAY, false);
      ObjectSet(liveLine, OBJPROP_BACK, false);
   }
}


//+------------------------------------------------------------------+
//| ON-CHART S&R DAILY PIVOT VISUALIZER (P, R1-R3, S1-S3 MT4)        |
//+------------------------------------------------------------------+
void DrawPivotLevel(string id, string label, double price, color clr, datetime tStart, datetime tEnd)
{
   if (price <= 0.0) return;
   string lineName = "VIKAR_PIVOT_LINE_" + id;
   string lblName  = "VIKAR_PIVOT_LBL_" + id;

   if (ObjectFind(lineName) < 0)
      ObjectCreate(lineName, OBJ_TREND, 0, tStart, price, tEnd, price);
   else
   {
      ObjectSet(lineName, OBJPROP_TIME1, tStart);
      ObjectSet(lineName, OBJPROP_PRICE1, price);
      ObjectSet(lineName, OBJPROP_TIME2, tEnd);
      ObjectSet(lineName, OBJPROP_PRICE2, price);
   }
   ObjectSet(lineName, OBJPROP_COLOR, clr);
   ObjectSet(lineName, OBJPROP_STYLE, (id == "P") ? STYLE_DASH : STYLE_DOT);
   ObjectSet(lineName, OBJPROP_WIDTH, (id == "P") ? 2 : 1);
   ObjectSet(lineName, OBJPROP_RAY, false);
   ObjectSet(lineName, OBJPROP_BACK, true);

   if (ObjectFind(lblName) < 0)
      ObjectCreate(lblName, OBJ_TEXT, 0, tEnd, price);
   else
   {
      ObjectSet(lblName, OBJPROP_TIME1, tEnd);
      ObjectSet(lblName, OBJPROP_PRICE1, price);
   }
   ObjectSetText(lblName, " [" + label + ": " + DoubleToString(price, Digits) + "]", 7, "Segoe UI Bold", clr);
}

void CleanPivotObjects()
{
   string ids[7] = {"R3", "R2", "R1", "P", "S1", "S2", "S3"};
   for (int i = 0; i < 7; i++)
   {
      ObjectDelete("VIKAR_PIVOT_LINE_" + ids[i]);
      ObjectDelete("VIKAR_PIVOT_LBL_" + ids[i]);
   }
}

void DrawDailyPivotsOnChart()
{
   if (!InpDrawPivotsOnChart || !currentPivot.isValid)
   {
      CleanPivotObjects();
      return;
   }

   datetime tStart = iTime(Symbol(), PERIOD_D1, 0);
   if (tStart <= 0) tStart = Time[MathMin(50, Bars - 1)];
   datetime tEnd   = Time[0] + (Period() * 60 * 15);

   DrawPivotLevel("P",  "PIVOT SENTRAL (P)", currentPivot.P,  InpColorPivotP,   tStart, tEnd);
   DrawPivotLevel("R1", "DAILY R1",          currentPivot.R1, InpColorPivotRes, tStart, tEnd);
   DrawPivotLevel("R2", "DAILY R2",          currentPivot.R2, InpColorPivotRes, tStart, tEnd);
   DrawPivotLevel("R3", "DAILY R3",          currentPivot.R3, InpColorPivotRes, tStart, tEnd);
   DrawPivotLevel("S1", "DAILY S1",          currentPivot.S1, InpColorPivotSup, tStart, tEnd);
   DrawPivotLevel("S2", "DAILY S2",          currentPivot.S2, InpColorPivotSup, tStart, tEnd);
   DrawPivotLevel("S3", "DAILY S3",          currentPivot.S3, InpColorPivotSup, tStart, tEnd);
}

//+------------------------------------------------------------------+
//| ON-CHART FIBONACCI GOLDEN POCKET VISUALIZER (50%, 61.8%, 78.6%)  |
//+------------------------------------------------------------------+
void CleanFiboObjects()
{
   ObjectDelete("VIKAR_FIBO_GP_BOX");
   ObjectDelete("VIKAR_FIBO_GP_TITLE");
   ObjectDelete("VIKAR_FIBO_LINE_500");
   ObjectDelete("VIKAR_FIBO_LBL_500");
   ObjectDelete("VIKAR_FIBO_LINE_618");
   ObjectDelete("VIKAR_FIBO_LBL_618");
   ObjectDelete("VIKAR_FIBO_LINE_786");
   ObjectDelete("VIKAR_FIBO_LBL_786");
}

void DrawFiboObjectsOnChart()
{
   if (!InpDrawFiboOnChart || !currentFibo.isValid)
   {
      CleanFiboObjects();
      return;
   }

   datetime tStart = MathMin(lastSwingHigh.time, lastSwingLow.time);
   if (tStart <= 0) tStart = Time[MathMin(30, Bars - 1)];
   datetime tEnd   = Time[0] + (Period() * 60 * 15);

   double topGP = MathMax(currentFibo.level500, currentFibo.level786);
   double botGP = MathMin(currentFibo.level500, currentFibo.level786);
   string gpBox   = "VIKAR_FIBO_GP_BOX";
   string gpTitle = "VIKAR_FIBO_GP_TITLE";

   color boxColor  = currentFibo.isBullish ? C'15,35,25' : C'40,20,25';
   color setupClr  = currentFibo.isBullish ? clrSpringGreen : clrTomato;
   string setupStr = currentFibo.isBullish ? " ★ FIBO BUY SETUP [ZONA DISKON: 50%-78.6%] " : " ★ FIBO SELL SETUP [ZONA PREMIUM: 50%-78.6%] ";

   // 1. Kotak Area Golden Pocket
   if (ObjectFind(gpBox) < 0)
      ObjectCreate(gpBox, OBJ_RECTANGLE, 0, tStart, topGP, tEnd, botGP);
   else
   {
      ObjectSet(gpBox, OBJPROP_TIME1, tStart);
      ObjectSet(gpBox, OBJPROP_PRICE1, topGP);
      ObjectSet(gpBox, OBJPROP_TIME2, tEnd);
      ObjectSet(gpBox, OBJPROP_PRICE2, botGP);
   }
   ObjectSet(gpBox, OBJPROP_COLOR, boxColor);
   ObjectSet(gpBox, OBJPROP_BACK, true);

   // Label Judul Setup di atas Kotak
   double titlePrice = topGP;
   if (ObjectFind(gpTitle) < 0)
      ObjectCreate(gpTitle, OBJ_TEXT, 0, tStart, titlePrice);
   else
   {
      ObjectSet(gpTitle, OBJPROP_TIME1, tStart);
      ObjectSet(gpTitle, OBJPROP_PRICE1, titlePrice);
   }
   ObjectSetText(gpTitle, setupStr, 8, "Segoe UI Bold", setupClr);

   // 2. Garis Level 50.0% Equilibrium (Batas Diskon / Premium)
   string l500   = "VIKAR_FIBO_LINE_500";
   string lbl500 = "VIKAR_FIBO_LBL_500";
   if (ObjectFind(l500) < 0)
      ObjectCreate(l500, OBJ_TREND, 0, tStart, currentFibo.level500, tEnd, currentFibo.level500);
   else
   {
      ObjectSet(l500, OBJPROP_TIME1, tStart);
      ObjectSet(l500, OBJPROP_PRICE1, currentFibo.level500);
      ObjectSet(l500, OBJPROP_TIME2, tEnd);
      ObjectSet(l500, OBJPROP_PRICE2, currentFibo.level500);
   }
   ObjectSet(l500, OBJPROP_COLOR, C'56,189,248'); // Sky Blue Cyan
   ObjectSet(l500, OBJPROP_STYLE, STYLE_DASH);
   ObjectSet(l500, OBJPROP_RAY, false);
   ObjectSet(l500, OBJPROP_BACK, true);

   if (ObjectFind(lbl500) < 0)
      ObjectCreate(lbl500, OBJ_TEXT, 0, tEnd, currentFibo.level500);
   else
   {
      ObjectSet(lbl500, OBJPROP_TIME1, tEnd);
      ObjectSet(lbl500, OBJPROP_PRICE1, currentFibo.level500);
   }
   ObjectSetText(lbl500, " [FIBO 50.0% EQUILIBRIUM: " + DoubleToString(currentFibo.level500, Digits) + "]", 7, "Segoe UI Bold", C'56,189,248');

   // 3. Garis Level 61.8% Golden Ratio (Level Reversal Utama)
   string l618   = "VIKAR_FIBO_LINE_618";
   string lbl618 = "VIKAR_FIBO_LBL_618";
   if (ObjectFind(l618) < 0)
      ObjectCreate(l618, OBJ_TREND, 0, tStart, currentFibo.level618, tEnd, currentFibo.level618);
   else
   {
      ObjectSet(l618, OBJPROP_TIME1, tStart);
      ObjectSet(l618, OBJPROP_PRICE1, currentFibo.level618);
      ObjectSet(l618, OBJPROP_TIME2, tEnd);
      ObjectSet(l618, OBJPROP_PRICE2, currentFibo.level618);
   }
   ObjectSet(l618, OBJPROP_COLOR, InpColorFiboGP);
   ObjectSet(l618, OBJPROP_STYLE, STYLE_SOLID);
   ObjectSet(l618, OBJPROP_RAY, false);
   ObjectSet(l618, OBJPROP_BACK, true);

   if (ObjectFind(lbl618) < 0)
      ObjectCreate(lbl618, OBJ_TEXT, 0, tEnd, currentFibo.level618);
   else
   {
      ObjectSet(lbl618, OBJPROP_TIME1, tEnd);
      ObjectSet(lbl618, OBJPROP_PRICE1, currentFibo.level618);
   }
   ObjectSetText(lbl618, " [FIBO 61.8% GOLDEN RATIO: " + DoubleToString(currentFibo.level618, Digits) + "]", 7, "Segoe UI Bold", InpColorFiboGP);

   // 4. Garis Level 78.6% Deep Pocket
   string l786   = "VIKAR_FIBO_LINE_786";
   string lbl786 = "VIKAR_FIBO_LBL_786";
   if (ObjectFind(l786) < 0)
      ObjectCreate(l786, OBJ_TREND, 0, tStart, currentFibo.level786, tEnd, currentFibo.level786);
   else
   {
      ObjectSet(l786, OBJPROP_TIME1, tStart);
      ObjectSet(l786, OBJPROP_PRICE1, currentFibo.level786);
      ObjectSet(l786, OBJPROP_TIME2, tEnd);
      ObjectSet(l786, OBJPROP_PRICE2, currentFibo.level786);
   }
   ObjectSet(l786, OBJPROP_COLOR, C'148,163,184');
   ObjectSet(l786, OBJPROP_STYLE, STYLE_DOT);
   ObjectSet(l786, OBJPROP_RAY, false);
   ObjectSet(l786, OBJPROP_BACK, true);

   if (ObjectFind(lbl786) < 0)
      ObjectCreate(lbl786, OBJ_TEXT, 0, tEnd, currentFibo.level786);
   else
   {
      ObjectSet(lbl786, OBJPROP_TIME1, tEnd);
      ObjectSet(lbl786, OBJPROP_PRICE1, currentFibo.level786);
   }
   ObjectSetText(lbl786, " [FIBO 78.6% DEEP: " + DoubleToString(currentFibo.level786, Digits) + "]", 7, "Segoe UI", C'148,163,184');
}

//+------------------------------------------------------------------+
//| ON-CHART DUAL M15 & M5 POI VISUALIZER (OB & LIKUIDITAS MT4)     |
//+------------------------------------------------------------------+
void DrawPOIMarkersOnChart()
{
   if (!InpDrawPOIVisuals)
   {
      ObjectDelete("VIKAR_M15_DEMAND_BOX");
      ObjectDelete("VIKAR_M15_DEMAND_LBL");
      ObjectDelete("VIKAR_M15_SUPPLY_BOX");
      ObjectDelete("VIKAR_M15_SUPPLY_LBL");
      ObjectDelete("VIKAR_M15_BSL_LINE");
      ObjectDelete("VIKAR_M15_BSL_LBL");
      ObjectDelete("VIKAR_M15_SSL_LINE");
      ObjectDelete("VIKAR_M15_SSL_LBL");

      ObjectDelete("VIKAR_M5_DEMAND_BOX");
      ObjectDelete("VIKAR_M5_DEMAND_LBL");
      ObjectDelete("VIKAR_M5_SUPPLY_BOX");
      ObjectDelete("VIKAR_M5_SUPPLY_LBL");
      ObjectDelete("VIKAR_M5_BSL_LINE");
      ObjectDelete("VIKAR_M5_BSL_LBL");
      ObjectDelete("VIKAR_M5_SSL_LINE");
      ObjectDelete("VIKAR_M5_SSL_LBL");
      return;
   }

   datetime tEnd = Time[0] + (Period() * 60 * 12);

   // ================= M15 DEMAND BOX & LABEL =================
   if (g_m15Stalker.demandZone.isValid && !g_m15Stalker.demandZone.isMitigated)
   {
      string nameBox = "VIKAR_M15_DEMAND_BOX";
      string nameLbl = "VIKAR_M15_DEMAND_LBL";
      if (ObjectFind(nameBox) < 0)
         ObjectCreate(nameBox, OBJ_RECTANGLE, 0, g_m15Stalker.demandZone.time, g_m15Stalker.demandZone.top, tEnd, g_m15Stalker.demandZone.bottom);
      else
      {
         ObjectSet(nameBox, OBJPROP_TIME1, g_m15Stalker.demandZone.time);
         ObjectSet(nameBox, OBJPROP_PRICE1, g_m15Stalker.demandZone.top);
         ObjectSet(nameBox, OBJPROP_TIME2, tEnd);
         ObjectSet(nameBox, OBJPROP_PRICE2, g_m15Stalker.demandZone.bottom);
      }
      ObjectSet(nameBox, OBJPROP_COLOR, InpColorM15Demand);
      ObjectSet(nameBox, OBJPROP_BACK, true);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.demandZone.top);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.demandZone.top);
      }
      ObjectSetText(nameLbl, " [M15 DEMAND POI: POTENSI BUY]", 8, "Segoe UI Bold", clrSpringGreen);
   }
   else
   {
      ObjectDelete("VIKAR_M15_DEMAND_BOX");
      ObjectDelete("VIKAR_M15_DEMAND_LBL");
   }

   // ================= M15 SUPPLY BOX & LABEL =================
   if (g_m15Stalker.supplyZone.isValid && !g_m15Stalker.supplyZone.isMitigated)
   {
      string nameBox = "VIKAR_M15_SUPPLY_BOX";
      string nameLbl = "VIKAR_M15_SUPPLY_LBL";
      if (ObjectFind(nameBox) < 0)
         ObjectCreate(nameBox, OBJ_RECTANGLE, 0, g_m15Stalker.supplyZone.time, g_m15Stalker.supplyZone.top, tEnd, g_m15Stalker.supplyZone.bottom);
      else
      {
         ObjectSet(nameBox, OBJPROP_TIME1, g_m15Stalker.supplyZone.time);
         ObjectSet(nameBox, OBJPROP_PRICE1, g_m15Stalker.supplyZone.top);
         ObjectSet(nameBox, OBJPROP_TIME2, tEnd);
         ObjectSet(nameBox, OBJPROP_PRICE2, g_m15Stalker.supplyZone.bottom);
      }
      ObjectSet(nameBox, OBJPROP_COLOR, InpColorM15Supply);
      ObjectSet(nameBox, OBJPROP_BACK, true);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.supplyZone.bottom);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.supplyZone.bottom);
      }
      ObjectSetText(nameLbl, " [M15 SUPPLY POI: POTENSI SELL]", 8, "Segoe UI Bold", clrTomato);
   }
   else
   {
      ObjectDelete("VIKAR_M15_SUPPLY_BOX");
      ObjectDelete("VIKAR_M15_SUPPLY_LBL");
   }

   // ================= M15 BSL & SSL LINES =================
   if (g_m15Stalker.bslPool.isValid && !g_m15Stalker.bslPool.isSwept)
   {
      string nameLine = "VIKAR_M15_BSL_LINE";
      string nameLbl  = "VIKAR_M15_BSL_LBL";
      if (ObjectFind(nameLine) < 0)
         ObjectCreate(nameLine, OBJ_TREND, 0, g_m15Stalker.bslPool.time1, g_m15Stalker.bslPool.priceLevel, tEnd, g_m15Stalker.bslPool.priceLevel);
      else
      {
         ObjectSet(nameLine, OBJPROP_TIME1, g_m15Stalker.bslPool.time1);
         ObjectSet(nameLine, OBJPROP_PRICE1, g_m15Stalker.bslPool.priceLevel);
         ObjectSet(nameLine, OBJPROP_TIME2, tEnd);
         ObjectSet(nameLine, OBJPROP_PRICE2, g_m15Stalker.bslPool.priceLevel);
      }
      ObjectSet(nameLine, OBJPROP_COLOR, InpColorLiquidity);
      ObjectSet(nameLine, OBJPROP_STYLE, STYLE_DOT);
      ObjectSet(nameLine, OBJPROP_RAY, false);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.bslPool.priceLevel);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.bslPool.priceLevel);
      }
      ObjectSetText(nameLbl, " [M15 BSL EQUAL HIGHS]", 8, "Segoe UI", InpColorLiquidity);
   }
   else
   {
      ObjectDelete("VIKAR_M15_BSL_LINE");
      ObjectDelete("VIKAR_M15_BSL_LBL");
   }

   if (g_m15Stalker.sslPool.isValid && !g_m15Stalker.sslPool.isSwept)
   {
      string nameLine = "VIKAR_M15_SSL_LINE";
      string nameLbl  = "VIKAR_M15_SSL_LBL";
      if (ObjectFind(nameLine) < 0)
         ObjectCreate(nameLine, OBJ_TREND, 0, g_m15Stalker.sslPool.time1, g_m15Stalker.sslPool.priceLevel, tEnd, g_m15Stalker.sslPool.priceLevel);
      else
      {
         ObjectSet(nameLine, OBJPROP_TIME1, g_m15Stalker.sslPool.time1);
         ObjectSet(nameLine, OBJPROP_PRICE1, g_m15Stalker.sslPool.priceLevel);
         ObjectSet(nameLine, OBJPROP_TIME2, tEnd);
         ObjectSet(nameLine, OBJPROP_PRICE2, g_m15Stalker.sslPool.priceLevel);
      }
      ObjectSet(nameLine, OBJPROP_COLOR, InpColorLiquidity);
      ObjectSet(nameLine, OBJPROP_STYLE, STYLE_DOT);
      ObjectSet(nameLine, OBJPROP_RAY, false);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.sslPool.priceLevel);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.sslPool.priceLevel);
      }
      ObjectSetText(nameLbl, " [M15 SSL EQUAL LOWS]", 8, "Segoe UI", InpColorLiquidity);
   }
   else
   {
      ObjectDelete("VIKAR_M15_SSL_LINE");
      ObjectDelete("VIKAR_M15_SSL_LBL");
   }

   // ================= M5 DEMAND BOX & LABEL =================
   if (g_m15Stalker.m5DemandZone.isValid && !g_m15Stalker.m5DemandZone.isMitigated)
   {
      string nameBox = "VIKAR_M5_DEMAND_BOX";
      string nameLbl = "VIKAR_M5_DEMAND_LBL";
      if (ObjectFind(nameBox) < 0)
         ObjectCreate(nameBox, OBJ_RECTANGLE, 0, g_m15Stalker.m5DemandZone.time, g_m15Stalker.m5DemandZone.top, tEnd, g_m15Stalker.m5DemandZone.bottom);
      else
      {
         ObjectSet(nameBox, OBJPROP_TIME1, g_m15Stalker.m5DemandZone.time);
         ObjectSet(nameBox, OBJPROP_PRICE1, g_m15Stalker.m5DemandZone.top);
         ObjectSet(nameBox, OBJPROP_TIME2, tEnd);
         ObjectSet(nameBox, OBJPROP_PRICE2, g_m15Stalker.m5DemandZone.bottom);
      }
      ObjectSet(nameBox, OBJPROP_COLOR, InpColorM5Demand);
      ObjectSet(nameBox, OBJPROP_BACK, true);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.m5DemandZone.top);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.m5DemandZone.top);
      }
      ObjectSetText(nameLbl, " [M5 DEMAND POI: POTENSI BUY]", 8, "Segoe UI Bold", clrLimeGreen);
   }
   else
   {
      ObjectDelete("VIKAR_M5_DEMAND_BOX");
      ObjectDelete("VIKAR_M5_DEMAND_LBL");
   }

   // ================= M5 SUPPLY BOX & LABEL =================
   if (g_m15Stalker.m5SupplyZone.isValid && !g_m15Stalker.m5SupplyZone.isMitigated)
   {
      string nameBox = "VIKAR_M5_SUPPLY_BOX";
      string nameLbl = "VIKAR_M5_SUPPLY_LBL";
      if (ObjectFind(nameBox) < 0)
         ObjectCreate(nameBox, OBJ_RECTANGLE, 0, g_m15Stalker.m5SupplyZone.time, g_m15Stalker.m5SupplyZone.top, tEnd, g_m15Stalker.m5SupplyZone.bottom);
      else
      {
         ObjectSet(nameBox, OBJPROP_TIME1, g_m15Stalker.m5SupplyZone.time);
         ObjectSet(nameBox, OBJPROP_PRICE1, g_m15Stalker.m5SupplyZone.top);
         ObjectSet(nameBox, OBJPROP_TIME2, tEnd);
         ObjectSet(nameBox, OBJPROP_PRICE2, g_m15Stalker.m5SupplyZone.bottom);
      }
      ObjectSet(nameBox, OBJPROP_COLOR, InpColorM5Supply);
      ObjectSet(nameBox, OBJPROP_BACK, true);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.m5SupplyZone.bottom);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.m5SupplyZone.bottom);
      }
      ObjectSetText(nameLbl, " [M5 SUPPLY POI: POTENSI SELL]", 8, "Segoe UI Bold", clrCoral);
   }
   else
   {
      ObjectDelete("VIKAR_M5_SUPPLY_BOX");
      ObjectDelete("VIKAR_M5_SUPPLY_LBL");
   }

   // ================= M5 BSL & SSL LINES =================
   if (g_m15Stalker.m5BslPool.isValid && !g_m15Stalker.m5BslPool.isSwept)
   {
      string nameLine = "VIKAR_M5_BSL_LINE";
      string nameLbl  = "VIKAR_M5_BSL_LBL";
      if (ObjectFind(nameLine) < 0)
         ObjectCreate(nameLine, OBJ_TREND, 0, g_m15Stalker.m5BslPool.time1, g_m15Stalker.m5BslPool.priceLevel, tEnd, g_m15Stalker.m5BslPool.priceLevel);
      else
      {
         ObjectSet(nameLine, OBJPROP_TIME1, g_m15Stalker.m5BslPool.time1);
         ObjectSet(nameLine, OBJPROP_PRICE1, g_m15Stalker.m5BslPool.priceLevel);
         ObjectSet(nameLine, OBJPROP_TIME2, tEnd);
         ObjectSet(nameLine, OBJPROP_PRICE2, g_m15Stalker.m5BslPool.priceLevel);
      }
      ObjectSet(nameLine, OBJPROP_COLOR, InpColorLiquidity);
      ObjectSet(nameLine, OBJPROP_STYLE, STYLE_DASH);
      ObjectSet(nameLine, OBJPROP_RAY, false);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.m5BslPool.priceLevel);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.m5BslPool.priceLevel);
      }
      ObjectSetText(nameLbl, " [M5 BSL EQUAL HIGHS]", 8, "Segoe UI", InpColorLiquidity);
   }
   else
   {
      ObjectDelete("VIKAR_M5_BSL_LINE");
      ObjectDelete("VIKAR_M5_BSL_LBL");
   }

   if (g_m15Stalker.m5SslPool.isValid && !g_m15Stalker.m5SslPool.isSwept)
   {
      string nameLine = "VIKAR_M5_SSL_LINE";
      string nameLbl  = "VIKAR_M5_SSL_LBL";
      if (ObjectFind(nameLine) < 0)
         ObjectCreate(nameLine, OBJ_TREND, 0, g_m15Stalker.m5SslPool.time1, g_m15Stalker.m5SslPool.priceLevel, tEnd, g_m15Stalker.m5SslPool.priceLevel);
      else
      {
         ObjectSet(nameLine, OBJPROP_TIME1, g_m15Stalker.m5SslPool.time1);
         ObjectSet(nameLine, OBJPROP_PRICE1, g_m15Stalker.m5SslPool.priceLevel);
         ObjectSet(nameLine, OBJPROP_TIME2, tEnd);
         ObjectSet(nameLine, OBJPROP_PRICE2, g_m15Stalker.m5SslPool.priceLevel);
      }
      ObjectSet(nameLine, OBJPROP_COLOR, InpColorLiquidity);
      ObjectSet(nameLine, OBJPROP_STYLE, STYLE_DASH);
      ObjectSet(nameLine, OBJPROP_RAY, false);

      if (ObjectFind(nameLbl) < 0)
         ObjectCreate(nameLbl, OBJ_TEXT, 0, tEnd, g_m15Stalker.m5SslPool.priceLevel);
      else
      {
         ObjectSet(nameLbl, OBJPROP_TIME1, tEnd);
         ObjectSet(nameLbl, OBJPROP_PRICE1, g_m15Stalker.m5SslPool.priceLevel);
      }
      ObjectSetText(nameLbl, " [M5 SSL EQUAL LOWS]", 8, "Segoe UI", InpColorLiquidity);
   }
   else
   {
      ObjectDelete("VIKAR_M5_SSL_LINE");
      ObjectDelete("VIKAR_M5_SSL_LBL");
   }
}

#define DrawM15POIMarkersOnChart DrawPOIMarkersOnChart

//+------------------------------------------------------------------+
//| ASISTEN TRADE MANUAL: AUTO SL / TP / BE / TRAILING (v3.50)      |
//| Mendeteksi order manual (MagicNumber=0) di chart ini dan         |
//| otomatis memasang SL, TP, Auto-Breakeven, dan Trailing Stop.    |
//+------------------------------------------------------------------+
void ManageManualTrades()
{
   if (!InpManageManualTrades) return;

   int stopsLevel  = (int)MarketInfo(Symbol(), MODE_STOPLEVEL);
   int freezeLevel = (int)MarketInfo(Symbol(), MODE_FREEZELEVEL);
   double minStopDist = MathMax(MathMax(stopsLevel * Point, freezeLevel * Point), 10 * Point);

   int total = OrdersTotal();
   for (int i = total - 1; i >= 0; i--)
   {
      if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
      // Hanya proses order manual (MagicNumber == 0) di symbol ini
      if (OrderSymbol() != Symbol() || OrderMagicNumber() != 0) continue;
      if (OrderType() != OP_BUY && OrderType() != OP_SELL)      continue;

      int    ticket  = OrderTicket();
      int    type    = OrderType();
      double open    = OrderOpenPrice();
      double sl      = OrderStopLoss();
      double tp      = OrderTakeProfit();
      double current = (type == OP_BUY) ? Bid : Ask;
      double pipsProfit = (type == OP_BUY) ? PriceToPips(current - open)
                                            : PriceToPips(open - current);

      // -------------------------------------------------------
      // STEP 1: Auto-Attach SL jika belum ada
      // -------------------------------------------------------
      if (sl == 0.0 && InpManualSLPips > 0.0)
      {
         double newSL = 0.0;
         if (type == OP_BUY)
            newSL = NormalizeDouble(open - PipToPrice(InpManualSLPips), Digits);
         else
            newSL = NormalizeDouble(open + PipToPrice(InpManualSLPips), Digits);

         bool slOK = false;
         if (type == OP_BUY  && (current - newSL) >= minStopDist) slOK = true;
         if (type == OP_SELL && (newSL - current) >= minStopDist) slOK = true;

         if (slOK)
         {
            if (OrderModify(ticket, open, newSL, tp, 0, clrOrange))
            {
               sl = newSL;
               Print("[MANUAL ASSIST] Order Manual #", ticket,
                     " | Auto-SL dipasang @ ", DoubleToString(newSL, Digits),
                     " (", DoubleToString(InpManualSLPips, 1), " pips dari Open)");
               if (InpSendPushNotifications)
                  SendNotification("VIKAR MT4 – AUTO SL MANUAL\nOrder #" + IntegerToString(ticket) +
                                   " SL otomatis dipasang @ " + DoubleToString(newSL, Digits));
            }
            else
               Print("[MANUAL ASSIST ERROR] Gagal pasang Auto-SL Order #", ticket,
                     " Error: ", GetLastError());
         }
      }

      // -------------------------------------------------------
      // STEP 2: Auto-Attach TP jika belum ada
      // -------------------------------------------------------
      if (tp == 0.0 && InpManualTPPips > 0.0)
      {
         double newTP = 0.0;
         if (type == OP_BUY)
            newTP = NormalizeDouble(open + PipToPrice(InpManualTPPips), Digits);
         else
            newTP = NormalizeDouble(open - PipToPrice(InpManualTPPips), Digits);

         bool tpOK = false;
         if (type == OP_BUY  && (newTP - current) >= minStopDist) tpOK = true;
         if (type == OP_SELL && (current - newTP) >= minStopDist) tpOK = true;

         if (tpOK)
         {
            if (OrderModify(ticket, open, sl, newTP, 0, clrOrange))
            {
               tp = newTP;
               Print("[MANUAL ASSIST] Order Manual #", ticket,
                     " | Auto-TP dipasang @ ", DoubleToString(newTP, Digits),
                     " (", DoubleToString(InpManualTPPips, 1), " pips dari Open)");
               if (InpSendPushNotifications)
                  SendNotification("VIKAR MT4 – AUTO TP MANUAL\nOrder #" + IntegerToString(ticket) +
                                   " TP otomatis dipasang @ " + DoubleToString(newTP, Digits));
            }
            else
               Print("[MANUAL ASSIST ERROR] Gagal pasang Auto-TP Order #", ticket,
                     " Error: ", GetLastError());
         }
      }

      // -------------------------------------------------------
      // STEP 3: Auto-Breakeven / SL+ untuk Trade Manual
      // -------------------------------------------------------
      if (InpManualAutoBE && InpManualBETriggerPips > 0.0)
      {
         if (pipsProfit >= InpManualBETriggerPips)
         {
            double beSL = 0.0;
            if (type == OP_BUY)
            {
               beSL = NormalizeDouble(open + PipToPrice(InpManualBELockPips), Digits);
               bool needBE = (sl < beSL) && ((current - beSL) >= minStopDist);
               if (needBE)
               {
                  if (OrderModify(ticket, open, beSL, tp, 0, clrGold))
                  {
                     sl = beSL;
                     Print("[MANUAL ASSIST BE] Order Manual BUY #", ticket,
                           " | SL+ dikunci @ ", DoubleToString(beSL, Digits),
                           " (+", DoubleToString(InpManualBELockPips, 1), " pips)");
                     if (InpSendPushNotifications)
                        SendNotification("VIKAR MT4 – AUTO BE MANUAL\nBUY Manual #" +
                                         IntegerToString(ticket) + " SL dikunci ke " +
                                         DoubleToString(beSL, Digits));
                  }
               }
            }
            else // OP_SELL
            {
               beSL = NormalizeDouble(open - PipToPrice(InpManualBELockPips), Digits);
               bool needBE = (sl == 0.0 || sl > beSL) && ((beSL - current) >= minStopDist);
               if (needBE)
               {
                  if (OrderModify(ticket, open, beSL, tp, 0, clrGold))
                  {
                     sl = beSL;
                     Print("[MANUAL ASSIST BE] Order Manual SELL #", ticket,
                           " | SL+ dikunci @ ", DoubleToString(beSL, Digits),
                           " (+", DoubleToString(InpManualBELockPips, 1), " pips)");
                     if (InpSendPushNotifications)
                        SendNotification("VIKAR MT4 – AUTO BE MANUAL\nSELL Manual #" +
                                         IntegerToString(ticket) + " SL dikunci ke " +
                                         DoubleToString(beSL, Digits));
                  }
               }
            }
         }
      }

      // -------------------------------------------------------
      // STEP 4: Auto Trailing Stop Dinamis untuk Trade Manual
      // -------------------------------------------------------
      if (InpManualTrailing && InpManualTrailingStart > 0.0 && InpManualTrailingDist > 0.0)
      {
         if (pipsProfit >= InpManualTrailingStart)
         {
            if (type == OP_BUY)
            {
               double trailSL = NormalizeDouble(current - PipToPrice(InpManualTrailingDist), Digits);
               bool moveUp = (trailSL > open) && // Hanya geser jika sudah di atas open (profit terjamin)
                             (trailSL > sl)    &&
                             ((trailSL - sl) >= PipToPrice(InpManualTrailingStep)) &&
                             ((current - trailSL) >= minStopDist);
               if (moveUp)
               {
                  if (OrderModify(ticket, open, trailSL, tp, 0, clrLime))
                  {
                     sl = trailSL;
                     Print("[MANUAL TRAIL] BUY Manual #", ticket,
                           " | SL dinaikkan mengawal harga @ ", DoubleToString(trailSL, Digits));
                  }
               }
            }
            else // OP_SELL
            {
               double trailSL = NormalizeDouble(current + PipToPrice(InpManualTrailingDist), Digits);
               bool moveDown = (trailSL < open) && // Hanya geser jika sudah di bawah open (profit terjamin)
                               (sl == 0.0 || trailSL < sl) &&
                               ((sl == 0.0 ? PipToPrice(InpManualTrailingStep) :
                                 (sl - trailSL)) >= PipToPrice(InpManualTrailingStep)) &&
                               ((trailSL - current) >= minStopDist);
               if (moveDown)
               {
                  if (OrderModify(ticket, open, trailSL, tp, 0, clrLime))
                  {
                     sl = trailSL;
                     Print("[MANUAL TRAIL] SELL Manual #", ticket,
                           " | SL diturunkan mengawal harga @ ", DoubleToString(trailSL, Digits));
                  }
               }
            }
         }
      }
   } // end for loop
}

//+------------------------------------------------------------------+
//| MANAJEMEN POSISI AKTIF: AUTO-BE, PARTIAL 50%, TRAILING STRUCTURAL|
//+------------------------------------------------------------------+
void ManageActiveTrades()
{
   if (!InpUseBreakeven && !InpUseTrailingEMA21 && !InpUsePartialClose && !InpUseStructuralTrailing && !InpUseCandleTrailing && !InpUsePointsTrailing && !InpUseMilestoneRatchet)
      return;

   // Bersihkan global variable jika tidak ada order aktif
   if (OrdersTotal() == 0)
   {
      int totalGV = GlobalVariablesTotal();
      for (int g = totalGV - 1; g >= 0; g--)
      {
         string gvName = GlobalVariableName(g);
         if (StringFind(gvName, "VIKAR_PARTIAL_") == 0 || StringFind(gvName, "VIKAR_INIT_R_") == 0)
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
// 0. Stagnant Trade Time-Exit & Pre-News BE Protection (v2.60)
      double hoursOpen = (double)(TimeCurrent() - OrderOpenTime()) / 3600.0;
      double pipsProfit = (type == OP_BUY) ? PriceToPips(current - open) : PriceToPips(open - current);

      // Pre-News Auto-Lock BE
      string activeNewsShield = "";
      if (InpUseNewsShield && InpAutoLockBEBeforeNews && IsInsideNewsWindow(activeNewsShield))
      {
         if (pipsProfit >= InpBreakevenLockPips)
         {
            double lockPrice = (type == OP_BUY) ? NormalizeDouble(open + PipToPrice(InpBreakevenLockPips), Digits)
                                                : NormalizeDouble(open - PipToPrice(InpBreakevenLockPips), Digits);
            bool needLock = (type == OP_BUY) ? (sl < lockPrice) : (sl > lockPrice || sl == 0);
            if (needLock)
            {
               Print("[PRE-NEWS LOCK MT4] Order #", ticket, " dikunci ke SL+ jelang ", activeNewsShield);
               bool modRes = OrderModify(ticket, open, lockPrice, tp, 0, clrGold);
               if (!modRes) Print("[ERROR] Gagal lock BE pre-news: ", GetLastError());
            }
         }
      }

      // Stagnant Time-Based Exit
      if (InpUseTimeBasedExit && hoursOpen >= (double)InpMaxTradeDurationHours && pipsProfit >= InpMinProfitToTimeExitPips)
      {
         Print("[TIME-EXIT MT4] Order #", ticket, " ditutup otomatis karena sudah mengambang ", DoubleToString(hoursOpen, 1), " jam (Profit: ", DoubleToString(pipsProfit, 1), " pips).");
         bool clsRes = OrderClose(ticket, posVol, (type == OP_BUY ? Bid : Ask), InpDeviation, clrGold);
         if (!clsRes) Print("[ERROR] Gagal time-exit order: ", GetLastError());
         continue;
      }

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
               double closeVol      = MathFloor(((posVol * (InpPartialClosePercent / 100.0)) + 0.0000001) / brokerStepLot) * brokerStepLot;
               closeVol             = NormalizeDouble(closeVol, 2);
               double remainVol     = NormalizeDouble(posVol - closeVol, 2);

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
                           if (!OrderModify(ticket, open, newSL, tp, 0, clrBlue))
                              Print("[ERROR] OrderModify TP1 BUY SL+ gagal: ", GetLastError());
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
                     if (!OrderModify(ticket, open, newSL, tp, 0, clrBlue))
                        Print("[ERROR] OrderModify TP1 BUY SL+ gagal: ", GetLastError());
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
               double closeVol      = MathFloor(((posVol * (InpPartialClosePercent / 100.0)) + 0.0000001) / brokerStepLot) * brokerStepLot;
               closeVol             = NormalizeDouble(closeVol, 2);
               double remainVol     = NormalizeDouble(posVol - closeVol, 2);

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
                           if (!OrderModify(ticket, open, newSL, tp, 0, clrRed))
                              Print("[ERROR] OrderModify TP1 SELL SL+ gagal: ", GetLastError());
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
                     if (!OrderModify(ticket, open, newSL, tp, 0, clrRed))
                        Print("[ERROR] OrderModify TP1 SELL SL+ gagal: ", GetLastError());
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

      // 2.5 Dynamic Points Trailing Stop (Kawal Kenaikan Harga per Step Points)
      if (InpUsePointsTrailing)
      {
         if (type == OP_BUY)
         {
            double profitPoints = PriceToPips(current - open) * 10.0;
            if (profitPoints >= InpTrailingStartPoints)
            {
               double targetSL = NormalizeDouble(current - PointToPrice(InpTrailingDistPoints), Digits);
               if (targetSL > open && (targetSL - sl) >= PointToPrice(InpTrailingStepPoints) && (current - targetSL) >= minStopDist)
               {
                  if (OrderModify(ticket, open, targetSL, tp, 0, clrGreen))
                  {
                     sl = targetSL;
                     Print("[TRAILING POINTS MT4] Posisi BUY #", ticket, " SL dinaikkan mengawal harga: ", targetSL);
                  }
               }
            }
         }
         else if (type == OP_SELL)
         {
            double profitPoints = PriceToPips(open - current) * 10.0;
            if (profitPoints >= InpTrailingStartPoints)
            {
               double targetSL = NormalizeDouble(current + PointToPrice(InpTrailingDistPoints), Digits);
               if (targetSL < open && (sl == 0 || (sl - targetSL) >= PointToPrice(InpTrailingStepPoints)) && (targetSL - current) >= minStopDist)
               {
                  if (OrderModify(ticket, open, targetSL, tp, 0, clrGreen))
                  {
                     sl = targetSL;
                     Print("[TRAILING POINTS MT4] Posisi SELL #", ticket, " SL diturunkan mengawal harga: ", targetSL);
                  }
               }
            }
         }
      }

      // 2.6 Dynamic Candle-by-Candle Trailing Stop (Kawal Mengikuti Ekor Lilin Terkini)
      if (InpUseCandleTrailing && Bars > 2)
      {
         if (type == OP_BUY)
         {
            double candleLow = Low[1];
            double effectiveCandleBufBUY = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;
      double candleSL  = NormalizeDouble(candleLow - PointToPrice(effectiveCandleBufBUY), Digits);
            if (candleSL > open && candleSL > sl && (candleSL - sl) >= (5 * Point) && (current - candleSL) >= minStopDist)
            {
               if (OrderModify(ticket, open, candleSL, tp, 0, clrGreen))
               {
                  sl = candleSL;
                  Print("[TRAILING CANDLE MT4] Posisi BUY #", ticket, " SL naik di bawah ekor lilin Low[1]: ", candleSL);
               }
            }
         }
         else if (type == OP_SELL)
         {
            double candleHigh = High[1];
            double effectiveCandleBufSELL = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;
      double candleSL   = NormalizeDouble(candleHigh + PointToPrice(effectiveCandleBufSELL), Digits);
            if (candleSL < open && (sl == 0 || candleSL < sl) && (sl - candleSL) >= (5 * Point) && (candleSL - current) >= minStopDist)
            {
               if (OrderModify(ticket, open, candleSL, tp, 0, clrGreen))
               {
                  sl = candleSL;
                  Print("[TRAILING CANDLE MT4] Posisi SELL #", ticket, " SL turun di atas ekor lilin High[1]: ", candleSL);
               }
            }
         }
      }

      // 2.7 Milestone Ratchet Trailing (v3.30 Pro Discipline)
      // Tiered profit locking: Locks +0.5R at 1.0R profit, +1.0R at 1.5R, +1.5R at 2.0R
      if (InpUseMilestoneRatchet)
      {
         string gvRKey = "VIKAR_INIT_R_" + IntegerToString(ticket);
         double rDist = 0.0;
         if (GlobalVariableCheck(gvRKey)) rDist = GlobalVariableGet(gvRKey);
         else
         {
            rDist = (type == OP_BUY) ? (open - sl) : (sl - open);
            if (rDist <= 0.0) rDist = PipToPrice(InpFixedSLPips);
            GlobalVariableSet(gvRKey, rDist);
         }

         if (rDist > 0.0)
         {
            if (type == OP_BUY)
            {
               double pDist = current - open;
               double targetSL = 0.0;
               if (pDist >= 2.0 * rDist)      targetSL = NormalizeDouble(open + (1.5 * rDist), Digits);
               else if (pDist >= 1.5 * rDist) targetSL = NormalizeDouble(open + (1.0 * rDist), Digits);
               else if (pDist >= 1.0 * rDist) targetSL = NormalizeDouble(open + (0.5 * rDist), Digits);

               if (targetSL > sl && (current - targetSL) >= minStopDist)
               {
                  if (OrderModify(ticket, open, targetSL, tp, 0, clrGreen))
                  {
                     sl = targetSL;
                     Print("[MILESTONE RATCHET MT4] BUY #", ticket, " SL dinaikkan mengunci profit ke: ", targetSL);
                  }
               }
            }
            else if (type == OP_SELL)
            {
               double pDist = open - current;
               double targetSL = 0.0;
               if (pDist >= 2.0 * rDist)      targetSL = NormalizeDouble(open - (1.5 * rDist), Digits);
               else if (pDist >= 1.5 * rDist) targetSL = NormalizeDouble(open - (1.0 * rDist), Digits);
               else if (pDist >= 1.0 * rDist) targetSL = NormalizeDouble(open - (0.5 * rDist), Digits);

               if (targetSL > 0.0 && (sl == 0.0 || targetSL < sl) && (targetSL - current) >= minStopDist)
               {
                  if (OrderModify(ticket, open, targetSL, tp, 0, clrGreen))
                  {
                     sl = targetSL;
                     Print("[MILESTONE RATCHET MT4] SELL #", ticket, " SL diturunkan mengunci profit ke: ", targetSL);
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
               if (!OrderModify(ticket, open, trailSL, tp, 0, clrGreen))
                  Print("[ERROR] OrderModify Trailing BUY gagal: ", GetLastError());
            }
         }
         else if (type == OP_SELL)
         {
            double trailSL = NormalizeDouble(ema21Val + PipToPrice(InpTrailingBufferPips), Digits);
            if (trailSL < open && (sl == 0 || (sl - trailSL) >= (10 * Point)) && (trailSL - current) >= minStopDist)
            {
               if (!OrderModify(ticket, open, trailSL, tp, 0, clrGreen))
                  Print("[ERROR] OrderModify Trailing SELL gagal: ", GetLastError());
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

   // 1. Early Invalidation Cut (OB Jebol oleh Displacement Lawan)
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
            if (!OrderClose(ticket, OrderLots(), Bid, InpDeviation, clrGold))
               Print("[ERROR] OrderClose Early Invalidation BUY gagal: ", GetLastError());
         }
         else if (type == OP_SELL && g_bearishOB.isValid && Close[1] > g_bearishOB.top && (Close[1] - Open[1]) >= dispThreshold)
         {
            Print("[EARLY INVALIDATION CUT] Bearish OB jebol oleh Bullish Displacement! Menutup SELL #", ticket);
            if (!OrderClose(ticket, OrderLots(), Ask, InpDeviation, clrGold))
               Print("[ERROR] OrderClose Early Invalidation SELL gagal: ", GetLastError());
         }
      }
   }

   // 2. Auto Cut Profit Saat Floating Profit & Terdeteksi Pembalikan Arah
   if (InpAutoCutProfit)
   {
      double ema21Val = iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, 1);
      int total = OrdersTotal();
      for (int i = total - 1; i >= 0; i--)
      {
         if (!OrderSelect(i, SELECT_BY_POS, MODE_TRADES)) continue;
         if (OrderSymbol() != Symbol() || OrderMagicNumber() != InpMagicNumber) continue;
         if (Time[1] < OrderOpenTime()) continue;

         int ticket = OrderTicket();
         int type   = OrderType();
         double open = OrderOpenPrice();
         double current = (type == OP_BUY) ? Bid : Ask;
         double pipsProfit = (type == OP_BUY) ? PriceToPips(current - open) : PriceToPips(open - current);

         if (pipsProfit < InpMinProfitToCutPips) continue;

         bool shouldCut = false;
         string cutReason = "";

         if (type == OP_BUY)
         {
            // Indikasi Bearish Reversal
            if (InpCutOnCHoCH && g_smcAnalysis.hasCHoCH && g_smcAnalysis.structure == SMC_STRUCT_BEARISH)
            {
               shouldCut = true;
               cutReason = "SMC Bearish CHoCH Reversal";
            }
            else if (InpCutOnCandleReversal && !g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore)
            {
               shouldCut = true;
               cutReason = "Bearish Candlestick Reversal (" + g_candleAnalysis.patternName + ")";
            }
            else if (InpCutOnEMACross && Close[1] < ema21Val && Close[2] >= ema21Val)
            {
               shouldCut = true;
               cutReason = "Close di bawah Ribbon EMA 21";
            }

            if (shouldCut)
            {
               Print("[AUTO CUT PROFIT MT4] Mengamankan profit +", DoubleToString(pipsProfit, 1), " pips pada BUY #", ticket, " karena: ", cutReason);
               if (OrderClose(ticket, OrderLots(), Bid, InpDeviation, clrGold))
               {
                  if (InpNotifyOnClose)
                     SendPushAlert("PROFIT SECURED! BUY #" + IntegerToString(ticket) + " cut profit +" + DoubleToString(pipsProfit, 1) + " pips (" + cutReason + ")");
               }
               else Print("[ERROR] Auto Cut Profit BUY gagal: ", GetLastError());
            }
         }
         else if (type == OP_SELL)
         {
            // Indikasi Bullish Reversal
            if (InpCutOnCHoCH && g_smcAnalysis.hasCHoCH && g_smcAnalysis.structure == SMC_STRUCT_BULLISH)
            {
               shouldCut = true;
               cutReason = "SMC Bullish CHoCH Reversal";
            }
            else if (InpCutOnCandleReversal && g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore)
            {
               shouldCut = true;
               cutReason = "Bullish Candlestick Reversal (" + g_candleAnalysis.patternName + ")";
            }
            else if (InpCutOnEMACross && Close[1] > ema21Val && Close[2] <= ema21Val)
            {
               shouldCut = true;
               cutReason = "Close di atas Ribbon EMA 21";
            }

            if (shouldCut)
            {
               Print("[AUTO CUT PROFIT MT4] Mengamankan profit +", DoubleToString(pipsProfit, 1), " pips pada SELL #", ticket, " karena: ", cutReason);
               if (OrderClose(ticket, OrderLots(), Ask, InpDeviation, clrGold))
               {
                  if (InpNotifyOnClose)
                     SendPushAlert("PROFIT SECURED! SELL #" + IntegerToString(ticket) + " cut profit +" + DoubleToString(pipsProfit, 1) + " pips (" + cutReason + ")");
               }
               else Print("[ERROR] Auto Cut Profit SELL gagal: ", GetLastError());
            }
         }
      }
   }
}

//+------------------------------------------------------------------+
//| M1 MULTI-TIMEFRAME SUB-STRUCTURE & RETEST ENGINE (v3.90)        |
//+------------------------------------------------------------------+
M1SniperResult AnalyzeM1SubStructure(bool isBuy, double m5Atr)
{
   M1SniperResult r;
   r.isValid = false;
   r.isBuyReady = false;
   r.isSellReady = false;
   r.hasDemandOB = false;
   r.hasSupplyOB = false;
   r.demandTop = 0.0;
   r.demandBottom = 0.0;
   r.supplyTop = 0.0;
   r.supplyBottom = 0.0;
   r.isCHoCH = false;
   r.isRejection = false;
   r.bestSLPrice = 0.0;
   r.score = 0.0;
   r.statusText = "M1: OFF";
   r.lastUpdated = TimeCurrent();

   if (!InpUseMTFM1Engine) return r;

   int m1Bars = iBars(Symbol(), PERIOD_M1);
   if (m1Bars < 20)
   {
      r.statusText = "M1: MEMUAT DATA...";
      return r;
   }

   double m1Atr = iATR(Symbol(), PERIOD_M1, 14, 1);
   if (m1Atr <= 0.0) m1Atr = PipToPrice(5.0);

   double dispThresh = InpM1DispAtrMult * m1Atr;
   double bufferPrice = PipToPrice(InpM1BufferPips);

   int scanLimit = MathMin(InpM1LookbackBars, m1Bars - 3);

   double bestDemandTop = 0.0, bestDemandBottom = 0.0;
   double bestSupplyTop = 0.0, bestSupplyBottom = 0.0;

   // 1. Scan Order Block M1
   for (int i = 1; i < scanLimit; i++)
   {
      double cClose = iClose(Symbol(), PERIOD_M1, i);
      double cOpen  = iOpen(Symbol(), PERIOD_M1, i);
      double cHigh  = iHigh(Symbol(), PERIOD_M1, i);
      double cLow   = iLow(Symbol(), PERIOD_M1, i);

      // Bullish Demand OB: Lilin bearish diikuti lonjakan bullish
      if (cClose < cOpen)
      {
         bool hasImpulse = false;
         for (int j = 1; j <= MathMin(3, i - 1); j++)
         {
            double jClose = iClose(Symbol(), PERIOD_M1, i - j);
            double jOpen  = iOpen(Symbol(), PERIOD_M1, i - j);
            if ((jClose - jOpen) >= dispThresh && jClose > cHigh)
            {
               hasImpulse = true;
               break;
            }
         }
         if (hasImpulse)
         {
            if (bestDemandTop == 0.0 || cHigh > bestDemandTop)
            {
               bestDemandTop = cHigh;
               bestDemandBottom = cLow;
            }
         }
      }

      // Bearish Supply OB: Lilin bullish diikuti lonjakan bearish
      if (cClose > cOpen)
      {
         bool hasImpulse = false;
         for (int j = 1; j <= MathMin(3, i - 1); j++)
         {
            double jClose = iClose(Symbol(), PERIOD_M1, i - j);
            double jOpen  = iOpen(Symbol(), PERIOD_M1, i - j);
            if ((jOpen - jClose) >= dispThresh && jClose < cLow)
            {
               hasImpulse = true;
               break;
            }
         }
         if (hasImpulse)
         {
            if (bestSupplyBottom == 0.0 || cLow < bestSupplyBottom)
            {
               bestSupplyTop = cHigh;
               bestSupplyBottom = cLow;
            }
         }
      }
   }

   if (bestDemandTop > 0.0)
   {
      r.hasDemandOB = true;
      r.demandTop = bestDemandTop;
      r.demandBottom = bestDemandBottom;
   }
   if (bestSupplyBottom > 0.0)
   {
      r.hasSupplyOB = true;
      r.supplyTop = bestSupplyTop;
      r.supplyBottom = bestSupplyBottom;
   }

   // 2. Evaluasi Lilin M1 Terkini & Trigger
   double m1Close1 = iClose(Symbol(), PERIOD_M1, 1);
   double m1Open1  = iOpen(Symbol(), PERIOD_M1, 1);
   double m1High1  = iHigh(Symbol(), PERIOD_M1, 1);
   double m1Low1   = iLow(Symbol(), PERIOD_M1, 1);
   double m1Range1 = m1High1 - m1Low1;

   // Deteksi Micro Swing High / Low M1
   double m1RecentHigh = 0.0, m1RecentLow = 0.0;
   for (int k = 2; k <= 7; k++)
   {
      double kH = iHigh(Symbol(), PERIOD_M1, k);
      double kL = iLow(Symbol(), PERIOD_M1, k);
      if (m1RecentHigh == 0.0 || kH > m1RecentHigh) m1RecentHigh = kH;
      if (m1RecentLow == 0.0  || kL < m1RecentLow)  m1RecentLow  = kL;
   }

   if (isBuy)
   {
      bool isRetestingDemand = (r.hasDemandOB && m1Low1 <= (r.demandTop + bufferPrice) && m1High1 >= r.demandBottom);
      bool isCHoCHBull = (m1RecentHigh > 0.0 && m1Close1 > m1RecentHigh && m1Close1 > m1Open1);
      bool isPinbarBull = (m1Range1 > 0 && ((MathMin(m1Open1, m1Close1) - m1Low1) / m1Range1) >= 0.50);
      bool isEngulfBull = (m1Close1 > m1Open1 && iClose(Symbol(), PERIOD_M1, 2) < iOpen(Symbol(), PERIOD_M1, 2) && m1Close1 >= iHigh(Symbol(), PERIOD_M1, 2));

      double m1Ema8_1  = iMA(Symbol(), PERIOD_M1, 8, 0, MODE_EMA, PRICE_CLOSE, 1);
      double m1Ema21_1 = iMA(Symbol(), PERIOD_M1, 21, 0, MODE_EMA, PRICE_CLOSE, 1);
      bool isM1RibbonBull = (m1Close1 > m1Ema8_1 && m1Ema8_1 > m1Ema21_1);

      double score = 0.0;
      if (isRetestingDemand) score += 8.0;
      if (isCHoCHBull)       score += 6.0;
      if (isPinbarBull || isEngulfBull) score += 4.0;
      if (isM1RibbonBull)    score += 2.0;

      r.score = MathMin(20.0, score);
      r.isCHoCH = isCHoCHBull;
      r.isRejection = (isPinbarBull || isEngulfBull);
      r.isBuyReady = (score >= 6.0 || isCHoCHBull || isRetestingDemand);
      r.isValid = true;

      // Stop Loss Presisi M1
      double swingM1Low = m1Low1;
      for (int slK = 1; slK <= 5; slK++)
      {
         double lk = iLow(Symbol(), PERIOD_M1, slK);
         if (lk < swingM1Low) swingM1Low = lk;
      }
      r.bestSLPrice = swingM1Low - (0.5 * m1Atr);

      if (isRetestingDemand && isCHoCHBull)
         r.statusText = "DEMAND RETEST + CHoCH (SNIPER A+)";
      else if (isRetestingDemand)
         r.statusText = "DEMAND RETEST VALID";
      else if (isCHoCHBull)
         r.statusText = "MICRO-CHoCH BREAKOUT";
      else if (r.isBuyReady)
         r.statusText = "BUY REJECTION READY";
      else
         r.statusText = "SCANNING RETEST...";
   }
   else
   {
      bool isRetestingSupply = (r.hasSupplyOB && m1High1 >= (r.supplyBottom - bufferPrice) && m1Low1 <= r.supplyTop);
      bool isCHoCHBear = (m1RecentLow > 0.0 && m1Close1 < m1RecentLow && m1Close1 < m1Open1);
      bool isPinbarBear = (m1Range1 > 0 && ((m1High1 - MathMax(m1Open1, m1Close1)) / m1Range1) >= 0.50);
      bool isEngulfBear = (m1Close1 < m1Open1 && iClose(Symbol(), PERIOD_M1, 2) > iOpen(Symbol(), PERIOD_M1, 2) && m1Close1 <= iLow(Symbol(), PERIOD_M1, 2));

      double m1Ema8_1  = iMA(Symbol(), PERIOD_M1, 8, 0, MODE_EMA, PRICE_CLOSE, 1);
      double m1Ema21_1 = iMA(Symbol(), PERIOD_M1, 21, 0, MODE_EMA, PRICE_CLOSE, 1);
      bool isM1RibbonBear = (m1Close1 < m1Ema8_1 && m1Ema8_1 < m1Ema21_1);

      double score = 0.0;
      if (isRetestingSupply) score += 8.0;
      if (isCHoCHBear)       score += 6.0;
      if (isPinbarBear || isEngulfBear) score += 4.0;
      if (isM1RibbonBear)    score += 2.0;

      r.score = MathMin(20.0, score);
      r.isCHoCH = isCHoCHBear;
      r.isRejection = (isPinbarBear || isEngulfBear);
      r.isSellReady = (score >= 6.0 || isCHoCHBear || isRetestingSupply);
      r.isValid = true;

      // Stop Loss Presisi M1
      double swingM1High = m1High1;
      for (int slK = 1; slK <= 5; slK++)
      {
         double hk = iHigh(Symbol(), PERIOD_M1, slK);
         if (hk > swingM1High) swingM1High = hk;
      }
      r.bestSLPrice = swingM1High + (0.5 * m1Atr);

      if (isRetestingSupply && isCHoCHBear)
         r.statusText = "SUPPLY RETEST + CHoCH (SNIPER A+)";
      else if (isRetestingSupply)
         r.statusText = "SUPPLY RETEST VALID";
      else if (isCHoCHBear)
         r.statusText = "MICRO-CHoCH BREAKDOWN";
      else if (r.isSellReady)
         r.statusText = "SELL REJECTION READY";
      else
         r.statusText = "SCANNING RETEST...";
   }

   return r;
}

//+------------------------------------------------------------------+
//| TOP-DOWN M15 & M5 POI STALKER ENGINE (v4.10)                     |
//| Memindai zona Order Block Institusional (Demand/Supply) &         |
//| Likuiditas (Equal Highs BSL / Equal Lows SSL) di M15 & M5.       |
//| Menandai status Stalking untuk konfirmasi rejection di LTF.     |
//+------------------------------------------------------------------+
void ScanSingleTF_POI(ENUM_TIMEFRAMES tf, string tfName, int lookbackBars, double dispAtrMult, double eqTolPips,
                      M15POIZone &demandZone, M15POIZone &supplyZone,
                      M15LiquidityPool &bslPool, M15LiquidityPool &sslPool)
{
   demandZone.isValid = false;
   supplyZone.isValid = false;
   bslPool.isValid    = false;
   sslPool.isValid    = false;

   double tfAtr = iATR(Symbol(), tf, 14, 1);
   if (tfAtr <= 0.0) tfAtr = PipToPrice(20.0);

   int totalBars = iBars(Symbol(), tf);
   int lookback = MathMin(lookbackBars, totalBars - 10);
   if (lookback < 20) return;

   double dispThreshold = dispAtrMult * tfAtr;
   double eqTolerance   = PipToPrice(eqTolPips);

   // 1. Pindai Demand OB (Base Demand tf)
   for (int i = 2; i < lookback; i++)
   {
      double cOpen  = iOpen(Symbol(), tf, i);
      double cClose = iClose(Symbol(), tf, i);
      double cHigh  = iHigh(Symbol(), tf, i);
      double cLow   = iLow(Symbol(), tf, i);

      // Lilin bearish sebelum lonjakan bullish
      if (cClose < cOpen)
      {
         bool isImpulse = false;
         for (int j = 1; j <= MathMin(3, i - 1); j++)
         {
            double jClose = iClose(Symbol(), tf, i - j);
            double jOpen  = iOpen(Symbol(), tf, i - j);
            if ((jClose - jOpen) >= dispThreshold && jClose > cHigh)
            {
               isImpulse = true;
               break;
            }
         }

         if (isImpulse)
         {
            // OB tetap valid sampai ada lilin yang CLOSE di bawah cLow (invalidation)
            bool broken = false;
            for (int k = i - 1; k >= 1; k--)
            {
               if (iClose(Symbol(), tf, k) < cLow)
               {
                  broken = true;
                  break;
               }
            }
            if (!broken)
            {
               demandZone.isValid = true;
               demandZone.tf = tf;
               demandZone.tfName = tfName;
               demandZone.isDemand = true;
               demandZone.top = cHigh;
               demandZone.bottom = cLow;
               demandZone.time = iTime(Symbol(), tf, i);
               demandZone.displacement = dispThreshold;
               demandZone.isMitigated = false;
               break;
            }
         }
      }
   }

   // 2. Pindai Supply OB (Supply Zone tf)
   for (int i = 2; i < lookback; i++)
   {
      double cOpen  = iOpen(Symbol(), tf, i);
      double cClose = iClose(Symbol(), tf, i);
      double cHigh  = iHigh(Symbol(), tf, i);
      double cLow   = iLow(Symbol(), tf, i);

      // Lilin bullish sebelum lonjakan bearish
      if (cClose > cOpen)
      {
         bool isImpulse = false;
         for (int j = 1; j <= MathMin(3, i - 1); j++)
         {
            double jClose = iClose(Symbol(), tf, i - j);
            double jOpen  = iOpen(Symbol(), tf, i - j);
            if ((jOpen - jClose) >= dispThreshold && jClose < cLow)
            {
               isImpulse = true;
               break;
            }
         }

         if (isImpulse)
         {
            bool broken = false;
            for (int k = i - 1; k >= 1; k--)
            {
               if (iClose(Symbol(), tf, k) > cHigh)
               {
                  broken = true;
                  break;
               }
            }
            if (!broken)
            {
               supplyZone.isValid = true;
               supplyZone.tf = tf;
               supplyZone.tfName = tfName;
               supplyZone.isDemand = false;
               supplyZone.top = cHigh;
               supplyZone.bottom = cLow;
               supplyZone.time = iTime(Symbol(), tf, i);
               supplyZone.displacement = dispThreshold;
               supplyZone.isMitigated = false;
               break;
            }
         }
      }
   }

   // 3. Pindai Kolam Likuiditas (Equal Highs & Equal Lows tf)
   if (InpPOIDetectLiquidity)
   {
      // Pindai Equal Highs (BSL)
      for (int i = 3; i < MathMin(lookback, 60); i++)
      {
         double h1 = iHigh(Symbol(), tf, i);
         if (h1 > iHigh(Symbol(), tf, i + 1) && h1 > iHigh(Symbol(), tf, i - 1))
         {
            for (int j = i + 2; j < MathMin(lookback, 80); j++)
            {
               double h2 = iHigh(Symbol(), tf, j);
               if (h2 > iHigh(Symbol(), tf, j + 1) && h2 > iHigh(Symbol(), tf, j - 1))
               {
                  if (MathAbs(h1 - h2) <= eqTolerance)
                  {
                     double eqPrice = (h1 + h2) * 0.5;
                     bool swept = false;
                     for (int s = i - 1; s >= 1; s--)
                     {
                        if (iHigh(Symbol(), tf, s) > eqPrice + PipToPrice(1.0))
                        {
                           swept = true;
                           break;
                        }
                     }
                     bslPool.isValid = true;
                     bslPool.tf = tf;
                     bslPool.tfName = tfName;
                     bslPool.isBuySide = true;
                     bslPool.priceLevel = eqPrice;
                     bslPool.time1 = iTime(Symbol(), tf, j);
                     bslPool.time2 = iTime(Symbol(), tf, i);
                     bslPool.isSwept = swept;
                     break;
                  }
               }
            }
            if (bslPool.isValid) break;
         }
      }

      // Pindai Equal Lows (SSL)
      for (int i = 3; i < MathMin(lookback, 60); i++)
      {
         double l1 = iLow(Symbol(), tf, i);
         if (l1 < iLow(Symbol(), tf, i + 1) && l1 < iLow(Symbol(), tf, i - 1))
         {
            for (int j = i + 2; j < MathMin(lookback, 80); j++)
            {
               double l2 = iLow(Symbol(), tf, j);
               if (l2 < iLow(Symbol(), tf, j + 1) && l2 < iLow(Symbol(), tf, j - 1))
               {
                  if (MathAbs(l1 - l2) <= eqTolerance)
                  {
                     double eqPrice = (l1 + l2) * 0.5;
                     bool swept = false;
                     for (int s = i - 1; s >= 1; s--)
                     {
                        if (iLow(Symbol(), tf, s) < eqPrice - PipToPrice(1.0))
                        {
                           swept = true;
                           break;
                        }
                     }
                     sslPool.isValid = true;
                     sslPool.tf = tf;
                     sslPool.tfName = tfName;
                     sslPool.isBuySide = false;
                     sslPool.priceLevel = eqPrice;
                     sslPool.time1 = iTime(Symbol(), tf, j);
                     sslPool.time2 = iTime(Symbol(), tf, i);
                     sslPool.isSwept = swept;
                     break;
                  }
               }
            }
            if (sslPool.isValid) break;
         }
      }
   }
}

M15StalkerResult AnalyzeInstitutionalPOI()
{
   M15StalkerResult res;
   res.isValid = false;
   res.isInDemandPOI = false;
   res.isInSupplyPOI = false;
   res.hasApproachedDemand = false;
   res.hasApproachedSupply = false;
   res.activeDemandTF = "";
   res.activeSupplyTF = "";
   res.demandDistPips = 999.0;
   res.supplyDistPips = 999.0;
   res.bestSLBuy = 0.0;
   res.bestSLSell = 0.0;
   res.score = 0.0;
   res.statusText = "POI STALKER: OFF";
   res.lastUpdated = TimeCurrent();

   if (!InpUsePOIStalker) return res;

   // 1. Pindai M15 jika diaktifkan
   if (InpPOIScanMode == POI_SCAN_DUAL_M15_M5 || InpPOIScanMode == POI_SCAN_M15_ONLY)
   {
      ScanSingleTF_POI(PERIOD_M15, "M15", InpPOILookbackBars, InpPOIDispAtrMult, InpPOIEqTolerancePips,
                       res.demandZone, res.supplyZone, res.bslPool, res.sslPool);
   }

   // 2. Pindai M5 jika diaktifkan
   if (InpPOIScanMode == POI_SCAN_DUAL_M15_M5 || InpPOIScanMode == POI_SCAN_M5_ONLY)
   {
      ScanSingleTF_POI(PERIOD_M5, "M5", InpPOILookbackBars, InpPOIDispAtrMult, InpPOIEqTolerancePips,
                       res.m5DemandZone, res.m5SupplyZone, res.m5BslPool, res.m5SslPool);
   }

   // Jika mode M5 Only, salin m5 ke zona utama agar kompatibel
   if (InpPOIScanMode == POI_SCAN_M5_ONLY)
   {
      res.demandZone = res.m5DemandZone;
      res.supplyZone = res.m5SupplyZone;
      res.bslPool    = res.m5BslPool;
      res.sslPool    = res.m5SslPool;
   }

   double curPrice = (Bid + Ask) * 0.5;
   double bufferPrice = PipToPrice(2.5);
   double currentAtr = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0.0) currentAtr = PipToPrice(20.0);

   // 3. Evaluasi Posisi Harga vs Zona DEMAND (M15 & M5)
   bool inM15Demand = (res.demandZone.isValid && curPrice <= (res.demandZone.top + bufferPrice) && curPrice >= (res.demandZone.bottom - bufferPrice));
   bool inM5Demand  = (res.m5DemandZone.isValid && curPrice <= (res.m5DemandZone.top + bufferPrice) && curPrice >= (res.m5DemandZone.bottom - bufferPrice));

   if (inM15Demand && inM5Demand)
   {
      res.isInDemandPOI = true;
      res.activeDemandTF = "DUAL M15+M5";
      res.demandDistPips = 0.0;
      res.score = 35.0;
      res.statusText = "DI ZONA DUAL M15+M5 DEMAND (SUPER CONFLUENCE BUY CETAR)";
      res.bestSLBuy = MathMin(res.demandZone.bottom, res.m5DemandZone.bottom) - (0.5 * currentAtr);
   }
   else if (inM5Demand)
   {
      res.isInDemandPOI = true;
      res.activeDemandTF = "M5";
      res.demandDistPips = 0.0;
      res.score = 25.0;
      res.statusText = "DI ZONA M5 DEMAND (POTENSI BUY CETAR)";
      res.bestSLBuy = res.m5DemandZone.bottom - (0.5 * currentAtr);
   }
   else if (inM15Demand)
   {
      res.isInDemandPOI = true;
      res.activeDemandTF = "M15";
      res.demandDistPips = 0.0;
      res.score = 25.0;
      res.statusText = "DI ZONA M15 DEMAND (POTENSI BUY CETAR)";
      res.bestSLBuy = res.demandZone.bottom - (0.5 * currentAtr);
   }

   // 4. Evaluasi Posisi Harga vs Zona SUPPLY (M15 & M5)
   bool inM15Supply = (res.supplyZone.isValid && curPrice >= (res.supplyZone.bottom - bufferPrice) && curPrice <= (res.supplyZone.top + bufferPrice));
   bool inM5Supply  = (res.m5SupplyZone.isValid && curPrice >= (res.m5SupplyZone.bottom - bufferPrice) && curPrice <= (res.m5SupplyZone.top + bufferPrice));

   if (inM15Supply && inM5Supply)
   {
      res.isInSupplyPOI = true;
      res.activeSupplyTF = "DUAL M15+M5";
      res.supplyDistPips = 0.0;
      res.score = 35.0;
      res.statusText = "DI ZONA DUAL M15+M5 SUPPLY (SUPER CONFLUENCE SELL CETAR)";
      res.bestSLSell = MathMax(res.supplyZone.top, res.m5SupplyZone.top) + (0.5 * currentAtr);
   }
   else if (inM5Supply)
   {
      res.isInSupplyPOI = true;
      res.activeSupplyTF = "M5";
      res.supplyDistPips = 0.0;
      res.score = 25.0;
      res.statusText = "DI ZONA M5 SUPPLY (POTENSI SELL CETAR)";
      res.bestSLSell = res.m5SupplyZone.top + (0.5 * currentAtr);
   }
   else if (inM15Supply)
   {
      res.isInSupplyPOI = true;
      res.activeSupplyTF = "M15";
      res.supplyDistPips = 0.0;
      res.score = 25.0;
      res.statusText = "DI ZONA M15 SUPPLY (POTENSI SELL CETAR)";
      res.bestSLSell = res.supplyZone.top + (0.5 * currentAtr);
   }

   // 5. Jika Belum Masuk Zona, Hitung Jarak Terdekat (Stalking Mode)
   if (!res.isInDemandPOI && !res.isInSupplyPOI)
   {
      double dM15 = res.demandZone.isValid ? ((curPrice > res.demandZone.top) ? (curPrice - res.demandZone.top) : (res.demandZone.bottom - curPrice)) : 99999.0;
      double dM5  = res.m5DemandZone.isValid ? ((curPrice > res.m5DemandZone.top) ? (curPrice - res.m5DemandZone.top) : (res.m5DemandZone.bottom - curPrice)) : 99999.0;
      double minD = MathMin(dM15, dM5);
      res.demandDistPips = PriceToPips(minD);

      double sM15 = res.supplyZone.isValid ? ((curPrice < res.supplyZone.bottom) ? (res.supplyZone.bottom - curPrice) : (curPrice - res.supplyZone.top)) : 99999.0;
      double sM5  = res.m5SupplyZone.isValid ? ((curPrice < res.m5SupplyZone.bottom) ? (res.m5SupplyZone.bottom - curPrice) : (curPrice - res.m5SupplyZone.top)) : 99999.0;
      double minS = MathMin(sM15, sM5);
      res.supplyDistPips = PriceToPips(minS);

      if (res.demandDistPips <= 10.0)
      {
         res.hasApproachedDemand = true;
         string tfStr = (dM5 < dM15) ? "M5" : "M15";
         res.statusText = "MENDEKATI " + tfStr + " DEMAND (" + DoubleToString(res.demandDistPips, 1) + "p) [STALKING]";
      }
      else if (res.supplyDistPips <= 10.0)
      {
         res.hasApproachedSupply = true;
         string tfStr = (sM5 < sM15) ? "M5" : "M15";
         res.statusText = "MENDEKATI " + tfStr + " SUPPLY (" + DoubleToString(res.supplyDistPips, 1) + "p) [STALKING]";
      }
      else
      {
         res.statusText = "POI MONITORING (M15/M5 STANDBY)";
      }
   }

   res.isValid = true;
   return res;
}

#define AnalyzeM15InstitutionalPOI AnalyzeInstitutionalPOI

//+------------------------------------------------------------------+
//| PEMERIKSAAN SINYAL EKSEKUSI (DUAL-ENGINE: SNIPER & MOMENTUM)     |
//+------------------------------------------------------------------+
void CheckTradeSignal()
{
   double currentAtr   = iATR(Symbol(), 0, 14, 1);
   if (currentAtr <= 0) currentAtr = PipToPrice(20.0);

   // 0.3 Batas Bawah Volatilitas: ATR Floor (v2.70)
   double currentAtrPips = 0.0;
   if (InpUseMinATRFilter && !CheckMinATRFloor(currentAtr, currentAtrPips))
   {
      g_lastSignalType = "ATR FLOOR: PASAR MATI / RANGE TERLALU SEMPIT (" + DoubleToString(currentAtrPips, 1) + " pips < " + DoubleToString(InpMinATRPips, 1) + " pips)";
      return;
   }

   // 0.4 Sensor Kekuatan Tren Kinetik: ADX Filter (v2.70)
   double adxPower = 0.0;
   if (InpUseADXFilter && !CheckADXPower(adxPower))
   {
      g_lastSignalType = "ADX FILTER: PASAR TIDUR / TANPA ARAH (ADX: " + DoubleToString(adxPower, 1) + " < " + DoubleToString(InpMinADXThreshold, 1) + ")";
      return;
   }

   // 0.5 Sensor Volume Institusional: VSA Filter (v2.70)
   double volRatio = 1.0;
   if (InpUseVolumeFilter && !CheckVolumeExpansion(volRatio))
   {
      g_lastSignalType = "VSA FILTER: VOLUME KERING / FAKEOUT RETAIL (Vol: " + DoubleToString(volRatio * 100.0, 0) + "% < " + DoubleToString(InpMinVolumeMultiplier * 100.0, 0) + "%)";
      return;
   }

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
   DrawDailyPivotsOnChart();
   UpdateSMCSwings(100);
   ExtractValidSwings(100, currentAtr);
   g_smcAnalysis = AnalyzeMarketStructure();
   DetectOrderBlocks(100, currentAtr);
   TrackFairValueGaps(100);
   UpdateSequentialSMCSniper(currentAtr);
   g_chartPattern = AnalyzeChartPatterns(100, currentAtr);
   g_m15Stalker = AnalyzeM15InstitutionalPOI();
   DrawSMCObjectsOnChart();
   DrawM15POIMarkersOnChart();

   bool currentTrendBias = (Close[1] > currentEma125);
   UpdateAutoFibo(currentTrendBias);
   DrawFiboObjectsOnChart();
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

   // Evaluasi Tren Dominan Institusional (v4.20 Anti-Melawan Trend)
   g_dominantTrendBias = GetDominantTrendBias();
   ENUM_HTF_BIAS htfBias = AnalyzeHTFMacroTrend();
   bool buyHTFOk  = (!InpUseHTFFilter || htfBias == HTF_BIAS_BULLISH);
   bool sellHTFOk = (!InpUseHTFFilter || htfBias == HTF_BIAS_BEARISH);

   // Evaluasi Keselarasan Tren untuk BUY
   bool isTrendBullish = (g_dominantTrendBias == HTF_BIAS_BULLISH);
   bool isTrendBearish = (g_dominantTrendBias == HTF_BIAS_BEARISH);

   //+---------------------------------------------------------------+
   //| EVALUASI SETUP BUY                                            |
   //+---------------------------------------------------------------+
   bool buyTrendEMA125 = (Close[1] > currentEma125);
   if (InpStrictTrendOnly && isTrendBearish)
   {
      // Tren Makro Bearish: Dilarang keras BUY!
      buyTrendEMA125 = false;
   }
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

         // Pullback ke Ribbon EMA 8/21 — Smart Pullback Quality Engine (v3.70)
         double pbScore = CalculatePullbackScore(true, currentAtr);
         bool isPullbackEMA = (pbScore >= InpMinPullbackScore);
         if (!isPullbackEMA)
         {
            // Fallback legacy: cek lama (sentuh ribbon kapan saja dalam lookback)
            int maxLookback = MathMin(InpPullbackLookback, Bars - 5);
            for (int b = 1; b <= maxLookback; b++)
            {
               double lowEma  = MathMin(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
               double highEma = MathMax(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
               if (Low[b] <= highEma && High[b] >= lowEma)
               {
                  isPullbackEMA = !InpUsePullbackScore; // Legacy hanya aktif jika scoring dimatikan
                  break;
               }
            }
            if (!isPullbackEMA)
               g_lastSignalType = "PULLBACK ENGINE: SKOR " + DoubleToString(pbScore, 0) + "/100 < MIN " + DoubleToString(InpMinPullbackScore, 0);
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
         {
            double cRangeBUY  = High[1] - Low[1];
            double upWickBUY  = High[1] - MathMax(Open[1], Close[1]);
            double lowWickBUY = MathMin(Open[1], Close[1]) - Low[1];
            // Lilin hijau sehat atau penolakan bawah kuat (bukan doji/upper wick dominan)
            isRejection = (Close[1] > Open[1] && upWickBUY < 0.45 * cRangeBUY) || (cRangeBUY > 0 && (lowWickBUY / cRangeBUY) >= 0.35);
         }

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

         // 1. Evaluasi Cuaca Pasar (Market Regime Classifier CI v2.50)
         g_currentChoppiness = CalculateChoppinessIndex(InpChoppinessPeriod);
         if (g_currentChoppiness > InpChoppyThreshold)
            g_currentRegime = REGIME_CHOPPY_SIDEWAYS;
         else if (g_currentChoppiness < InpTrendingThreshold)
            g_currentRegime = REGIME_STRONG_TREND;
         else
            g_currentRegime = REGIME_NORMAL;

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(true, currentAtr, g_smcAnalysis, g_bullishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);

         // 1.5 Multi-Timeframe M1 Micro-Sniper Timing (v3.90)
         if (InpUseMTFM1Engine)
         {
            M1SniperResult m1Buy = AnalyzeM1SubStructure(true, currentAtr);
            g_m1Sniper = m1Buy;
            if (m1Buy.isValid && m1Buy.isBuyReady)
            {
               scoreRes.totalScore += m1Buy.score;
            }
            else if (InpRequireM1StrictGate)
            {
               g_lastSignalType = "M1 STRICT GATE: MENUNGGU RETEST / CHoCH M1 (BUY)";
               return;
            }
         }

         // 1.6 Top-Down Institutional POI Confluence & Gate (v4.10)
         if (InpUsePOIStalker && g_m15Stalker.isValid)
         {
            if (g_m15Stalker.isInDemandPOI)
            {
               scoreRes.totalScore += g_m15Stalker.score;
               if (InpRequireLTFRejection && !g_candleAnalysis.isHighQuality && !(InpUseMTFM1Engine && g_m1Sniper.isValid && g_m1Sniper.isRejection))
               {
                  g_lastSignalType = "POI STALKER: MENUNGGU CANDLE REJECTION DI LTF";
                  return;
               }
            }
            else if (InpRequirePOIZone)
            {
               g_lastSignalType = "POI GATE: HARGA DI LUAR DEMAND (Jarak: " + DoubleToString(g_m15Stalker.demandDistPips, 1) + " pips)";
               return;
            }
         }

         g_lastScoreResult = scoreRes;

         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreBUY += 10.0; // Filter ekstra saat pasar sideways sempit

         // Adaptive Directional Penalty: Cegah balas dendam BUY jika baru saja loss BUY
         if (InpUseDirectionalLearning && g_autopsy.failedDirection == 1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
            effectiveMinScoreBUY += InpDirectionalPenaltyScore;

         // Hourly Toxic Learning: Hindari jam rawan loss berulang
         if (InpUseHourlyLearning && g_autopsy.toxicHour == Hour())
            effectiveMinScoreBUY += 10.0;

         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         // 2.5 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
         bool isBullishSweepTrap = false;
         if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
         {
            double candleRange = High[1] - Low[1];
            if (candleRange > 0 && lastSwingLow.price > 0 && Low[1] < lastSwingLow.price && Close[1] > lastSwingLow.price)
            {
               double sweepDistPips = PriceToPips(lastSwingLow.price - Low[1]);
               double lowerWick     = MathMin(Open[1], Close[1]) - Low[1];
               double lowerWickPct  = (lowerWick / candleRange) * 100.0;
               if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && lowerWickPct >= InpMinRejectionWickPct)
               {
                  isBullishSweepTrap = true;
                  g_trapHunterStatusStr = "BULLISH SWEEP TRAP (SSL REVERSAL)";
                  Print("[TRAP HUNTER MT4] Bullish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(lowerWickPct, 0), "%.");
               }
            }
         }

         // 3. Momentum Breakout Detection (Anti-Ketinggalan Momentum)
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways (Fakeout 85%)
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody   = Close[1] - Open[1];
               double candleRange  = High[1] - Low[1];
               double upperWick    = High[1] - MathMax(Open[1], Close[1]);
               double distToEma21  = MathAbs(Close[1] - currentEma21);

               bool isBigBullBody     = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (Close[1] > currentEma8 && currentEma8 > currentEma21);
               bool isBOSBreakout     = (!InpBreakoutRequireBOS || Close[1] > lastSwingHigh.price || g_smcAnalysis.hasBOS);
               bool isVSASupported    = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));
               bool isNotExhausted    = (candleRange > 0 && (upperWick / candleRange) <= 0.35); // Anti Bull Trap ekor atas
               bool isNotOverextended = (distToEma21 <= (1.2 * currentAtr)); // Anti overstretch jauh dari Ribbon

               if (isBigBullBody && isRibbonExpanding && isBOSBreakout && isVSASupported && isNotExhausted && isNotOverextended)
                  isMomentumBreakout = true;
            }
         }

         // 2.6 Sequential SMC Sniper Engine (Sweep -> CHoCH -> FVG Retest)
         bool isSMCSniperBUY = false;
         if (InpUseSequentialSMCSniper && g_sniperBUY.stage == SNIPER_STAGE_READY_TO_FIRE)
         {
            isSMCSniperBUY = true;
         }

         // 2.7 Pro Trend Pullback Scalper Engine (v4.20 Institusional)
         g_proPullbackBUY = EvaluateProPullbackSetup(true, currentAtr);
         bool isProPullbackBUY = (InpEnableProPullbackScalper && g_proPullbackBUY.isValid && (isTrendBullish || !InpStrictTrendOnly));

         // 4. Evaluasi Pattern Performance Matrix (AI Pattern Learning v2.50)
         int activePatIdBUY = isBullishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);
         if (InpUsePatternMatrix)
         {
            if (g_patternMatrix[activePatIdBUY].isBlacklisted)
            {
               g_lastSignalType = "AI MATRIX: POLA " + g_patternMatrix[activePatIdBUY].name + " DI-BLACKLIST (WR: " + DoubleToString(g_patternMatrix[activePatIdBUY].winRate, 1) + "%)";
               return;
            }
         }

         if (InpUseDivergenceFilter && CheckRSIDivergence(true) && !isSMCSniperBUY)
         {
            g_lastSignalType = "DIVERGENCE: BEARISH EXHAUSTION (CEGAH BELI DI PUCUK)";
            return;
         }

         double slopeBuyPips = 0.0;
         if (InpUseEMASlopeFilter && !CheckEMASlope(true, slopeBuyPips) && !isSMCSniperBUY)
         {
            g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeBuyPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
            return;
         }

         // =========================================================================
         // AI BRAIN & CANDLESTICK SHIELD PROTECTION GATE (v3.40)
         // =========================================================================
         // Terapkan Modifikasi Skor dari Hasil Pembelajaran Mandiri (Bonus / Penalti Bersih 1x)
         if (InpUsePatternMatrix)
            scoreRes.totalScore += g_patternMatrix[activePatIdBUY].scoreModifier;

         // 2. AI Candlestick Shield: Filter Doji / Body Tipis (<22% Range)
         double barRangeBUY = High[1] - Low[1];
         if (barRangeBUY > 0)
         {
            double barBodyBUY      = MathAbs(Close[1] - Open[1]);
            double barBodyPctBUY   = (barBodyBUY / barRangeBUY) * 100.0;
            double barUpWickBUY    = High[1] - MathMax(Open[1], Close[1]);
            double barUpWickPctBUY = (barUpWickBUY / barRangeBUY) * 100.0;

            if (InpFilterDojiCandles && barBodyPctBUY <= 22.0 && !isBullishSweepTrap && !isSMCSniperBUY)
            {
               g_lastSignalType = "AI SHIELD: BODY DOJI / RAGU-RAGU (" + DoubleToString(barBodyPctBUY, 0) + "% < 22%)";
               return;
            }

            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Upper Wick >= 40% on BUY)
            if (InpFilterExhaustionWicks && barUpWickPctBUY >= 40.0 && !isSMCSniperBUY)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN SELLER DI ATAS (" + DoubleToString(barUpWickPctBUY, 0) + "% >= 40%)";
               return;
            }

            // 4. AI Candlestick Shield: Filter Overextended Engulfing (> 1.5x ATR dari EMA21)
            if (InpFilterOverextended && (g_candleAnalysis.pattern == PATTERN_ENGULFING || isMomentumBreakout) && !isSMCSniperBUY)
            {
               double distToEma21 = MathAbs(Close[1] - currentEma21);
               if (distToEma21 > (1.5 * currentAtr))
               {
                  g_lastSignalType = "AI SHIELD: OVEREXTENDED DARI EMA21 (" + DoubleToString(PriceToPips(distToEma21), 1) + " > 1.5x ATR)";
                  return;
               }
            }
         }

         bool canExecuteBuy = (smcBullishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreBUY)) ||
                              (isProPullbackBUY && isHeadroomOk) ||
                              (isMomentumBreakout && isHeadroomOk) ||
                              (isBullishSweepTrap && isHeadroomOk) ||
                              (isSMCSniperBUY && isHeadroomOk);

         if (canExecuteBuy)
         {
            double slPrice = 0.0;
            double tpPrice = 0.0;

            // 1. Tentukan Baseline SL berdasarkan mode terpilih (Sertakan Adaptive SL Buffer jika ada)
            if (isSMCSniperBUY && g_sniperBUY.recommendedSL > 0.0 && g_sniperBUY.recommendedSL < Ask)
            {
               slPrice = g_sniperBUY.recommendedSL;
            }
            else if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingLow.price > 0)
            {
               double effectiveBufferMultBUY = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);
               slPrice = lastSwingLow.price - (effectiveBufferMultBUY * currentAtr);
            }
            else if (InpSLType == SL_TYPE_CANDLE_WICK)
            {
               double wickBuf = PipToPrice(5.0) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? (InpAdaptiveSLBufferBoost * currentAtr) : 0.0);
               slPrice = Low[1] - wickBuf;
            }
            else
            {
               double fixBuf = PipToPrice(InpFixedSLPips) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? (InpAdaptiveSLBufferBoost * currentAtr) : 0.0);
               slPrice = Ask - fixBuf;
            }

            double slDist = Ask - slPrice;

            // 2. Proteksi Zona Institutional POI (Prioritas tertinggi jika berada di zona Demand)
            if (!isSMCSniperBUY && InpUsePOIStalker && g_m15Stalker.isInDemandPOI)
            {
               double poiDemandBottom = (g_m15Stalker.demandZone.isValid && g_m15Stalker.demandZone.bottom > 0.0) ? g_m15Stalker.demandZone.bottom :
                                        ((g_m15Stalker.m5DemandZone.isValid && g_m15Stalker.m5DemandZone.bottom > 0.0) ? g_m15Stalker.m5DemandZone.bottom : 0.0);
               double poiSL = (g_m15Stalker.bestSLBuy > 0.0) ? g_m15Stalker.bestSLBuy : (poiDemandBottom > 0.0 ? poiDemandBottom - (0.5 * currentAtr) : 0.0);
               if (poiSL > 0.0 && poiSL < Ask)
               {
                  slPrice = poiSL;
                  slDist  = Ask - slPrice;
               }
            }
            bool isGoldBUY = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
            double safeMinSLBUY = PipToPrice(InpMinSLPips);
            double atrFloorBUY  = (isGoldBUY ? 1.0 : 0.8) * currentAtr;
            if (safeMinSLBUY < atrFloorBUY) safeMinSLBUY = atrFloorBUY;
            if (isGoldBUY && safeMinSLBUY < 5.0) safeMinSLBUY = 5.0; // Minimal $5.00 lantai pengaman XAUUSD (50 pips)
            if (safeMinSLBUY > PipToPrice(InpMaxSLPips)) safeMinSLBUY = PipToPrice(InpMaxSLPips);

            // 3. Jika di luar POI, terapkan Stop Loss Presisi M1 jika valid, lebih ketat & tetap di atas batas aman
            else if (!isSMCSniperBUY && InpUseMTFM1Engine && InpM1UseTightSL && g_m1Sniper.isValid && g_m1Sniper.bestSLPrice > 0.0 && g_m1Sniper.bestSLPrice < Ask)
            {
               double m1SLDist = Ask - g_m1Sniper.bestSLPrice;
               if (PriceToPips(m1SLDist) >= InpM1MinSLPips && m1SLDist >= safeMinSLBUY && m1SLDist < slDist)
               {
                  slPrice = g_m1Sniper.bestSLPrice;
                  slDist  = Ask - slPrice;
               }
            }

            // 4. Batasi Jarak SL sesuai Batas Minimal Aman & Maksimal
            if (slDist < safeMinSLBUY)
            {
               slPrice = Ask - safeMinSLBUY;
               slDist  = safeMinSLBUY;
            }
            if (PriceToPips(slDist) > InpMaxSLPips)
            {
               slPrice = Ask - PipToPrice(InpMaxSLPips);
               slDist  = Ask - slPrice;
            }

            // 5. Stops Level Validation Broker sebelum TP & Lot dihitung
            int stopsLevel = (int)MarketInfo(Symbol(), MODE_STOPLEVEL);
            double minStopDist = MathMax(stopsLevel * Point, MarketInfo(Symbol(), MODE_SPREAD) * Point + (5 * Point));
            if ((Ask - slPrice) < minStopDist)
            {
               slPrice = Ask - minStopDist;
               slDist  = Ask - slPrice;
            }

            slPrice = NormalizeDouble(slPrice, Digits);

            // 6. Hitung Target Take Profit Cerdas (TP 150 Pips Default)
            if (InpTPType == TP_TYPE_FIXED_PIPS)
            {
               tpPrice = Ask + PipToPrice(InpFixedTPPips);
            }
            else if (isSMCSniperBUY && g_sniperBUY.recommendedTP1 > Ask)
            {
               tpPrice = g_sniperBUY.recommendedTP1;
            }
            else if (InpTPType == TP_TYPE_FIXED_POINTS)
            {
               tpPrice = Ask + PointToPrice(InpFixedTPPoints);
            }
            else if (InpTPType == TP_TYPE_FIBO_EXT)
            {
               if (currentFibo.isValid && currentFibo.ext272 > Ask && (currentFibo.ext272 - Ask) >= slDist)
                  tpPrice = currentFibo.ext272;
               else if (currentFibo.isValid && currentFibo.ext618 > Ask && (currentFibo.ext618 - Ask) >= slDist)
                  tpPrice = currentFibo.ext618;
               else
                  tpPrice = Ask + (InpRiskRewardRatio * slDist);
            }
            else if (InpTPType == TP_TYPE_PIVOT_LEVEL)
            {
               if (currentPivot.R1 > Ask && (currentPivot.R1 - Ask) >= slDist)
                  tpPrice = currentPivot.R1;
               else if (currentPivot.R2 > Ask && (currentPivot.R2 - Ask) >= slDist)
                  tpPrice = currentPivot.R2;
               else
                  tpPrice = Ask + (InpRiskRewardRatio * slDist);
            }
            else // TP_TYPE_RISK_REWARD default
            {
               tpPrice = Ask + (InpRiskRewardRatio * slDist);
            }

            if ((tpPrice - Ask) < minStopDist) tpPrice = Ask + minStopDist;
            tpPrice = NormalizeDouble(tpPrice, Digits);

            // 7. Hitung Lot dengan Jarak SL Final yang Presisi
            double lots = CalculateRiskLot(Ask - slPrice, scoreRes.totalScore);

            if (isProPullbackBUY && g_proPullbackBUY.suggestedTP > Ask && InpTPType != TP_TYPE_FIXED_PIPS)
               tpPrice = g_proPullbackBUY.suggestedTP;

            string tradeCmt = InpTradeComment + (isProPullbackBUY ? "-PRO-PB" : (isSMCSniperBUY ? "-SNIPER-BUY" : (isBullishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))))));

            int ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrBlue);

            if (ticket <= 0)
            {
               int err = GetLastError();
               if (err == 130) // ERR_INVALID_STOPS (ECN Market Execution Broker Requirement)
               {
                  Print("[ECN RETRY BUY] Broker ECN menolak SL/TP awal. Membuka posisi tanpa SL/TP lalu modifikasi...");
                  ticket = OrderSend(Symbol(), OP_BUY, lots, Ask, InpDeviation, 0, 0, tradeCmt, InpMagicNumber, 0, clrBlue);
                  if (ticket > 0)
                  {
                     Sleep(100);
                     double opPrice = Ask;
                     if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES))
                        opPrice = OrderOpenPrice();
                     if (OrderModify(ticket, opPrice, slPrice, tpPrice, 0, clrBlue))
                        Print("[ECN BUY SUCCESS] SL dan TP berhasil dipasang pada tiket #", ticket);
                     else
                        Print("[ECN BUY WARN] OrderModify SL/TP gagal: ", GetLastError());
                  }
                  else err = GetLastError();
               }
               if (ticket <= 0)
               {
                  Print("[BUY REJECTED MT4] Error: ", err);
                  g_lastSignalType = "ORDER DITOLAK BROKER (Error " + IntegerToString(err) + ")";
               }
            }

            if (ticket > 0)
            {
               if (isSMCSniperBUY)
               {
                  g_sniperBUY.stage = SNIPER_STAGE_IDLE;
                  g_sniperBUY.statusText = "IDLE (EXECUTED TICKET #" + IntegerToString(ticket) + ")";
               }
               GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString(ticket), MathMax(Ask - slPrice, 10 * Point));
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMT4(ticket, 1, activePatIdBUY, scoreRes.totalScore, currentAtr);
               lastOrderBarTime = Time[0];
               string patStr = isProPullbackBUY ? ("Pro Pullback Scalper (" + g_proPullbackBUY.confluencesStr + ")") : (isSMCSniperBUY ? "Sequential SMC Sniper (Sweep->CHoCH->FVG)" : (isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName));
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
         }
         else
         {
            if (scoreRes.totalScore < effectiveMinScoreBUY)
               g_lastSignalType = "SKOR KURANG: " + DoubleToString(scoreRes.totalScore, 0) + " / MIN " + DoubleToString(effectiveMinScoreBUY, 0) + " (BUY)";
            else if (!isHeadroomOk)
               g_lastSignalType = "HEADROOM SEMPIT KE R1 (BUY)";
            else if (!isPullbackEMA)
               g_lastSignalType = "MENUNGGU PULLBACK KE RIBBON EMA (BUY)";
            else if (!isRejection)
               g_lastSignalType = "MENUNGGU CANDLE REJECTION (BUY)";
            else if (!isOBMitigatedOk)
               g_lastSignalType = "MENUNGGU MITIGASI ORDER BLOCK (BUY)";
            else if (!isFiboGPOk)
               g_lastSignalType = "DILUAR GOLDEN POCKET FIBO (BUY)";
            else if (!smcBullishOk)
               g_lastSignalType = "STRUKTUR SMC TIDAK MEMENUHI (BUY)";
         }
      }
   }

   //+---------------------------------------------------------------+
   //| EVALUASI SETUP SELL                                           |
   //+---------------------------------------------------------------+
   bool sellTrendEMA125 = (Close[1] < currentEma125);
   if (InpStrictTrendOnly && isTrendBullish)
   {
      // Tren Makro Bullish: Dilarang keras SELL!
      sellTrendEMA125 = false;
   }
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

         // Pullback ke Ribbon EMA 8/21 — Smart Pullback Quality Engine (v3.70)
         double pbScore = CalculatePullbackScore(false, currentAtr);
         bool isPullbackEMA = (pbScore >= InpMinPullbackScore);
         if (!isPullbackEMA)
         {
            int maxLookback = MathMin(InpPullbackLookback, Bars - 5);
            for (int b = 1; b <= maxLookback; b++)
            {
               double lowEma  = MathMin(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
               double highEma = MathMax(iMA(Symbol(), 0, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE, b), iMA(Symbol(), 0, InpMediumEMA, 0, MODE_EMA, PRICE_CLOSE, b));
               if (High[b] >= lowEma && Low[b] <= highEma)
               {
                  isPullbackEMA = !InpUsePullbackScore;
                  break;
               }
            }
            if (!isPullbackEMA)
               g_lastSignalType = "PULLBACK ENGINE: SKOR " + DoubleToString(pbScore, 0) + "/100 < MIN " + DoubleToString(InpMinPullbackScore, 0);
         }

         bool isFiboGPOk = true;
         if (InpUseAutoFibo && InpRequireGoldenPocket && currentFibo.isValid)
            isFiboGPOk = (High[1] >= currentFibo.level500 && Low[1] <= currentFibo.level786);

         bool isRejection = true;
         if (InpRequireCandleRejection)
            isRejection = (!g_candleAnalysis.isBullish && g_candleAnalysis.pattern != PATTERN_NONE && g_candleAnalysis.score >= InpMinCandleScore);
         else
         {
            double cRangeSELL  = High[1] - Low[1];
            double upWickSELL   = High[1] - MathMax(Open[1], Close[1]);
            double lowWickSELL  = MathMin(Open[1], Close[1]) - Low[1];
            // Lilin merah sehat atau penolakan atas kuat (bukan doji/lower wick dominan)
            isRejection = (Close[1] < Open[1] && lowWickSELL < 0.45 * cRangeSELL) || (cRangeSELL > 0 && (upWickSELL / cRangeSELL) >= 0.35);
         }

         bool isHeadroomOk = true;
         if (InpUseDailyPivots && currentPivot.S1 < Close[1])
         {
            double distToS1 = Close[1] - currentPivot.S1;
            if (distToS1 < (InpMinHeadroomATR * currentAtr)) isHeadroomOk = false;
         }

         bool isOBMitigatedOk = true;
         if (InpUseOrderBlock && InpRequireOBMitigation)
            isOBMitigatedOk = (g_bearishOB.isValid && High[1] >= g_bearishOB.bottom && Low[1] <= g_bearishOB.top);

         // 1. Evaluasi Cuaca Pasar (Market Regime Classifier CI v2.50)
         g_currentChoppiness = CalculateChoppinessIndex(InpChoppinessPeriod);
         if (g_currentChoppiness > InpChoppyThreshold)
            g_currentRegime = REGIME_CHOPPY_SIDEWAYS;
         else if (g_currentChoppiness < InpTrendingThreshold)
            g_currentRegime = REGIME_STRONG_TREND;
         else
            g_currentRegime = REGIME_NORMAL;

         ConfluenceScoreResult scoreRes = CalculateConfluenceScore(false, currentAtr, g_smcAnalysis, g_bearishOB, g_activeFVG, g_candleAnalysis, currentFibo, currentEma8, currentEma21, currentEma125);

         // 1.5 Multi-Timeframe M1 Micro-Sniper Timing (v3.90 SELL)
         if (InpUseMTFM1Engine)
         {
            M1SniperResult m1Sell = AnalyzeM1SubStructure(false, currentAtr);
            g_m1Sniper = m1Sell;
            if (m1Sell.isValid && m1Sell.isSellReady)
            {
               scoreRes.totalScore += m1Sell.score;
            }
            else if (InpRequireM1StrictGate)
            {
               g_lastSignalType = "M1 STRICT GATE: MENUNGGU RETEST / CHoCH M1 (SELL)";
               return;
            }
         }

         // 1.6 Top-Down Institutional POI Confluence & Gate (v4.10)
         if (InpUsePOIStalker && g_m15Stalker.isValid)
         {
            if (g_m15Stalker.isInSupplyPOI)
            {
               scoreRes.totalScore += g_m15Stalker.score;
               if (InpRequireLTFRejection && !g_candleAnalysis.isHighQuality && !(InpUseMTFM1Engine && g_m1Sniper.isValid && g_m1Sniper.isRejection))
               {
                  g_lastSignalType = "POI STALKER: MENUNGGU CANDLE REJECTION DI LTF";
                  return;
               }
            }
            else if (InpRequirePOIZone)
            {
               g_lastSignalType = "POI GATE: HARGA DI LUAR SUPPLY (Jarak: " + DoubleToString(g_m15Stalker.supplyDistPips, 1) + " pips)";
               return;
            }
         }

         g_lastScoreResult = scoreRes;

         // 2. Evaluasi Koreksi Diri Pasca-SL: Ambang Skor Dinamis & Karantina Pola Gagal
         double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);
         if (InpUseRegimeFilter && g_currentRegime == REGIME_CHOPPY_SIDEWAYS)
            effectiveMinScoreSELL += 10.0; // Filter ekstra saat pasar sideways sempit

         // Adaptive Directional Penalty: Cegah balas dendam SELL jika baru saja loss SELL
         if (InpUseDirectionalLearning && g_autopsy.failedDirection == -1 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
            effectiveMinScoreSELL += InpDirectionalPenaltyScore;

         // Hourly Toxic Learning: Hindari jam rawan loss berulang
         if (InpUseHourlyLearning && g_autopsy.toxicHour == Hour())
            effectiveMinScoreSELL += 10.0;

         if (InpUseSelfHealing && g_autopsy.isActive && Time[0] < g_autopsy.quarantineUntilBar &&
             g_candleAnalysis.pattern == g_autopsy.failedPattern && g_autopsy.failedPattern != PATTERN_NONE)
         {
            int remainBars = (int)((g_autopsy.quarantineUntilBar - Time[0]) / (Period() * 60));
            g_lastSignalType = "KOREKSI DIRI: POLA " + g_candleAnalysis.patternName + " DIKARANTINA (Sisa " + IntegerToString(remainBars) + " bar)";
            return;
         }

         // 2.5 Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine v3.00)
         bool isBearishSweepTrap = false;
         if (InpUseTrapHunter && g_smcAnalysis.hasSweep)
         {
            double candleRange = High[1] - Low[1];
            if (candleRange > 0 && lastSwingHigh.price > 0 && High[1] > lastSwingHigh.price && Close[1] < lastSwingHigh.price)
            {
               double sweepDistPips = PriceToPips(High[1] - lastSwingHigh.price);
               double upperWick     = High[1] - MathMax(Open[1], Close[1]);
               double upperWickPct  = (upperWick / candleRange) * 100.0;
               if (sweepDistPips >= InpMinSweepPips && sweepDistPips <= InpMaxSweepPips && upperWickPct >= InpMinRejectionWickPct)
               {
                  isBearishSweepTrap = true;
                  g_trapHunterStatusStr = "BEARISH SWEEP TRAP (BSL REVERSAL)";
                  Print("[TRAP HUNTER MT4] Bearish Liquidity Sweep terdeteksi! Sweep: ", DoubleToString(sweepDistPips, 1), " pips, Ekor: ", DoubleToString(upperWickPct, 0), "%.");
               }
            }
         }

         // 3. Momentum Breakout Detection
         bool isMomentumBreakout = false;
         if (InpAllowMomentumBreakout)
         {
            // Proteksi Cuaca: Jangan breakout saat pasar Choppy Sideways
            if (!InpUseRegimeFilter || !InpBlockBreakoutInChoppy || g_currentRegime != REGIME_CHOPPY_SIDEWAYS)
            {
               double candleBody   = Open[1] - Close[1];
               double candleRange  = High[1] - Low[1];
               double lowerWick    = MathMin(Open[1], Close[1]) - Low[1];
               double distToEma21  = MathAbs(Close[1] - currentEma21);

               bool isBigBearBody     = (candleBody >= (InpBreakoutAtrMult * currentAtr));
               bool isRibbonExpanding = (Close[1] < currentEma8 && currentEma8 < currentEma21);
               bool isBOSBreakout     = (!InpBreakoutRequireBOS || Close[1] < lastSwingLow.price || g_smcAnalysis.hasBOS);
               bool isVSASupported    = (!InpBreakoutRequireVSA || (scoreRes.vsaPts >= 5.0 || Volume[1] >= (long)(1.3 * (double)Volume[2])));
               bool isNotExhausted    = (candleRange > 0 && (lowerWick / candleRange) <= 0.35); // Anti Bear Trap ekor bawah
               bool isNotOverextended = (distToEma21 <= (1.2 * currentAtr)); // Anti overstretch jauh dari Ribbon

               if (isBigBearBody && isRibbonExpanding && isBOSBreakout && isVSASupported && isNotExhausted && isNotOverextended)
                  isMomentumBreakout = true;
            }
         }

         // 2.6 Sequential SMC Sniper Engine (Sweep -> CHoCH -> FVG Retest)
         bool isSMCSniperSELL = false;
         if (InpUseSequentialSMCSniper && g_sniperSELL.stage == SNIPER_STAGE_READY_TO_FIRE)
         {
            isSMCSniperSELL = true;
         }

         // 2.7 Pro Trend Pullback Scalper Engine (v4.20 Institusional)
         g_proPullbackSELL = EvaluateProPullbackSetup(false, currentAtr);
         bool isProPullbackSELL = (InpEnableProPullbackScalper && g_proPullbackSELL.isValid && (isTrendBearish || !InpStrictTrendOnly));

         // 4. Evaluasi Pattern Performance Matrix (AI Pattern Learning v2.50)
         int activePatIdSELL = isBearishSweepTrap ? 12 : (isMomentumBreakout ? 11 : (int)g_candleAnalysis.pattern);
         if (InpUsePatternMatrix)
         {
            if (g_patternMatrix[activePatIdSELL].isBlacklisted)
            {
               g_lastSignalType = "AI MATRIX: POLA " + g_patternMatrix[activePatIdSELL].name + " DI-BLACKLIST (WR: " + DoubleToString(g_patternMatrix[activePatIdSELL].winRate, 1) + "%)";
               return;
            }
         }

         if (InpUseDivergenceFilter && CheckRSIDivergence(false) && !isSMCSniperSELL)
         {
            g_lastSignalType = "DIVERGENCE: BULLISH EXHAUSTION (CEGAH JUAL DI LEMBAH)";
            return;
         }

         double slopeSellPips = 0.0;
         if (InpUseEMASlopeFilter && !CheckEMASlope(false, slopeSellPips) && !isSMCSniperSELL)
         {
            g_lastSignalType = "EMA SLOPE: EMA DATAR / KUSUT (Slope: " + DoubleToString(slopeSellPips, 1) + " pips < " + DoubleToString(InpMinEMASlopePips, 1) + " pips)";
            return;
         }

         // =========================================================================
         // AI BRAIN & CANDLESTICK SHIELD PROTECTION GATE (v3.40)
         // =========================================================================
         // Terapkan Modifikasi Skor dari Hasil Pembelajaran Mandiri (Bonus / Penalti Bersih 1x)
         if (InpUsePatternMatrix)
            scoreRes.totalScore += g_patternMatrix[activePatIdSELL].scoreModifier;

         // 2. AI Candlestick Shield: Filter Doji / Body Tipis (<22% Range)
         double barRangeSELL = High[1] - Low[1];
         if (barRangeSELL > 0)
         {
            double barBodySELL      = MathAbs(Close[1] - Open[1]);
            double barBodyPctSELL   = (barBodySELL / barRangeSELL) * 100.0;
            double barLowWickSELL   = MathMin(Open[1], Close[1]) - Low[1];
            double barLowWickPctSELL= (barLowWickSELL / barRangeSELL) * 100.0;

            if (InpFilterDojiCandles && barBodyPctSELL <= 22.0 && !isBearishSweepTrap && !isSMCSniperSELL)
            {
               g_lastSignalType = "AI SHIELD: BODY DOJI / RAGU-RAGU (" + DoubleToString(barBodyPctSELL, 0) + "% < 22%)";
               return;
            }

            // 3. AI Candlestick Shield: Filter Ekor Penolakan Lawan Arah (Lower Wick >= 40% on SELL)
            if (InpFilterExhaustionWicks && barLowWickPctSELL >= 40.0 && !isSMCSniperSELL)
            {
               g_lastSignalType = "AI SHIELD: PENOLAKAN BUYER DI BAWAH (" + DoubleToString(barLowWickPctSELL, 0) + "% >= 40%)";
               return;
            }

            // 4. AI Candlestick Shield: Filter Overextended Engulfing (> 1.5x ATR dari EMA21)
            if (InpFilterOverextended && (g_candleAnalysis.pattern == PATTERN_ENGULFING || isMomentumBreakout) && !isSMCSniperSELL)
            {
               double distToEma21 = MathAbs(Close[1] - currentEma21);
               if (distToEma21 > (1.5 * currentAtr))
               {
                  g_lastSignalType = "AI SHIELD: OVEREXTENDED DARI EMA21 (" + DoubleToString(PriceToPips(distToEma21), 1) + " > 1.5x ATR)";
                  return;
               }
            }
         }

         bool canExecuteSell = (smcBearishOk && isPullbackEMA && isFiboGPOk && isRejection && isHeadroomOk && isOBMitigatedOk && (scoreRes.totalScore >= effectiveMinScoreSELL)) ||
                               (isProPullbackSELL && isHeadroomOk) ||
                               (isMomentumBreakout && isHeadroomOk) ||
                               (isBearishSweepTrap && isHeadroomOk) ||
                               (isSMCSniperSELL && isHeadroomOk);

         if (canExecuteSell)
         {
            double slPrice = 0.0;
            double tpPrice = 0.0;

            // 1. Tentukan Baseline SL berdasarkan mode terpilih (Sertakan Adaptive SL Buffer jika ada)
            if (isSMCSniperSELL && g_sniperSELL.recommendedSL > 0.0 && g_sniperSELL.recommendedSL > Bid)
            {
               slPrice = g_sniperSELL.recommendedSL;
            }
            else if (InpSLType == SL_TYPE_SWING_FIBO && lastSwingHigh.price > 0)
            {
               double effectiveBufferMultSELL = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);
               slPrice = lastSwingHigh.price + (effectiveBufferMultSELL * currentAtr);
            }
            else if (InpSLType == SL_TYPE_CANDLE_WICK)
            {
               double wickBuf = PipToPrice(5.0) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? (InpAdaptiveSLBufferBoost * currentAtr) : 0.0);
               slPrice = High[1] + wickBuf;
            }
            else
            {
               double fixBuf = PipToPrice(InpFixedSLPips) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? (InpAdaptiveSLBufferBoost * currentAtr) : 0.0);
               slPrice = Bid + fixBuf;
            }

            double slDist = slPrice - Bid;

            // 2. Proteksi Zona Institutional POI (Prioritas tertinggi jika berada di zona Supply)
            if (!isSMCSniperSELL && InpUsePOIStalker && g_m15Stalker.isInSupplyPOI)
            {
               double poiSupplyTop = (g_m15Stalker.supplyZone.isValid && g_m15Stalker.supplyZone.top > 0.0) ? g_m15Stalker.supplyZone.top :
                                     ((g_m15Stalker.m5SupplyZone.isValid && g_m15Stalker.m5SupplyZone.top > 0.0) ? g_m15Stalker.m5SupplyZone.top : 0.0);
               double poiSL = (g_m15Stalker.bestSLSell > 0.0) ? g_m15Stalker.bestSLSell : (poiSupplyTop > 0.0 ? poiSupplyTop + (0.5 * currentAtr) : 0.0);
               if (poiSL > 0.0 && poiSL > Bid)
               {
                  double poiSLDist = poiSL - Bid;
                  if (PriceToPips(poiSLDist) >= InpMinSLPips && poiSLDist < slDist)
                  {
                     slPrice = poiSL;
                     slDist  = slPrice - Bid;
                  }
               }
            }
            bool isGoldSELL = (StringFind(Symbol(), "XAU") >= 0 || StringFind(Symbol(), "GOLD") >= 0);
            double safeMinSLSELL = PipToPrice(InpMinSLPips);
            double atrFloorSELL  = (isGoldSELL ? 1.0 : 0.8) * currentAtr;
            if (safeMinSLSELL < atrFloorSELL) safeMinSLSELL = atrFloorSELL;
            if (isGoldSELL && safeMinSLSELL < 5.0) safeMinSLSELL = 5.0; // Minimal $5.00 lantai pengaman XAUUSD (50 pips)
            if (safeMinSLSELL > PipToPrice(InpMaxSLPips)) safeMinSLSELL = PipToPrice(InpMaxSLPips);

            // 3. Jika di luar POI, terapkan Stop Loss Presisi M1 jika valid, lebih ketat & tetap di atas batas aman
            else if (!isSMCSniperSELL && InpUseMTFM1Engine && InpM1UseTightSL && g_m1Sniper.isValid && g_m1Sniper.bestSLPrice > 0.0 && g_m1Sniper.bestSLPrice > Bid)
            {
               double m1SLDist = g_m1Sniper.bestSLPrice - Bid;
               if (PriceToPips(m1SLDist) >= InpM1MinSLPips && m1SLDist >= safeMinSLSELL && m1SLDist < slDist)
               {
                  slPrice = g_m1Sniper.bestSLPrice;
                  slDist  = slPrice - Bid;
               }
            }

            // 4. Batasi Jarak SL sesuai Batas Minimal Aman & Maksimal
            if (slDist < safeMinSLSELL)
            {
               slPrice = Bid + safeMinSLSELL;
               slDist  = safeMinSLSELL;
            }
            if (PriceToPips(slDist) > InpMaxSLPips)
            {
               slPrice = Bid + PipToPrice(InpMaxSLPips);
               slDist  = slPrice - Bid;
            }

            // 5. Stops Level Validation Broker sebelum TP & Lot dihitung
            int stopsLevel = (int)MarketInfo(Symbol(), MODE_STOPLEVEL);
            double minStopDist = MathMax(stopsLevel * Point, MarketInfo(Symbol(), MODE_SPREAD) * Point + (5 * Point));
            if ((slPrice - Bid) < minStopDist)
            {
               slPrice = Bid + minStopDist;
               slDist  = slPrice - Bid;
            }

            slPrice = NormalizeDouble(slPrice, Digits);

            // 6. Hitung Target Take Profit Cerdas (Smart R:R Floor minimal 1.0x / 1:3+ untuk Sniper)
            if (InpTPType == TP_TYPE_FIXED_PIPS)
            {
               tpPrice = Bid - PipToPrice(InpFixedTPPips);
            }
            else if (isSMCSniperSELL && g_sniperSELL.recommendedTP1 < Bid)
            {
               tpPrice = g_sniperSELL.recommendedTP1;
            }
            else if (InpTPType == TP_TYPE_FIXED_POINTS)
            {
               tpPrice = Bid - PointToPrice(InpFixedTPPoints);
            }
            else if (InpTPType == TP_TYPE_FIBO_EXT)
            {
               if (currentFibo.isValid && currentFibo.ext272 < Bid && (Bid - currentFibo.ext272) >= slDist)
                  tpPrice = currentFibo.ext272;
               else if (currentFibo.isValid && currentFibo.ext618 < Bid && (Bid - currentFibo.ext618) >= slDist)
                  tpPrice = currentFibo.ext618;
               else
                  tpPrice = Bid - (InpRiskRewardRatio * slDist);
            }
            else if (InpTPType == TP_TYPE_PIVOT_LEVEL)
            {
               if (currentPivot.S1 < Bid && (Bid - currentPivot.S1) >= slDist)
                  tpPrice = currentPivot.S1;
               else if (currentPivot.S2 < Bid && (Bid - currentPivot.S2) >= slDist)
                  tpPrice = currentPivot.S2;
               else
                  tpPrice = Bid - (InpRiskRewardRatio * slDist);
            }
            else // TP_TYPE_RISK_REWARD default
            {
               tpPrice = Bid - (InpRiskRewardRatio * slDist);
            }

            if ((Bid - tpPrice) < minStopDist) tpPrice = Bid - minStopDist;
            tpPrice = NormalizeDouble(tpPrice, Digits);

            // 7. Hitung Lot dengan Jarak SL Final yang Presisi
            double lots = CalculateRiskLot(slPrice - Bid, scoreRes.totalScore);

            if (isProPullbackSELL && g_proPullbackSELL.suggestedTP < Bid && g_proPullbackSELL.suggestedTP > 0 && InpTPType != TP_TYPE_FIXED_PIPS)
               tpPrice = g_proPullbackSELL.suggestedTP;

            string tradeCmt = InpTradeComment + (isProPullbackSELL ? "-PRO-PB" : (isSMCSniperSELL ? "-SNIPER-SELL" : (isBearishSweepTrap ? "-TRAP" : (isMomentumBreakout ? "-MOMENTUM" : (isSwept ? "-SWEEP" : (g_smcAnalysis.hasCHoCH ? "-CHOCH" : "-BOS"))))));

            int ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, slPrice, tpPrice, tradeCmt, InpMagicNumber, 0, clrRed);

            if (ticket <= 0)
            {
               int err = GetLastError();
               if (err == 130) // ERR_INVALID_STOPS (ECN Market Execution Broker Requirement)
               {
                  Print("[ECN RETRY SELL] Broker ECN menolak SL/TP awal. Membuka posisi tanpa SL/TP lalu modifikasi...");
                  ticket = OrderSend(Symbol(), OP_SELL, lots, Bid, InpDeviation, 0, 0, tradeCmt, InpMagicNumber, 0, clrRed);
                  if (ticket > 0)
                  {
                     Sleep(100);
                     double opPrice = Bid;
                     if (OrderSelect(ticket, SELECT_BY_TICKET, MODE_TRADES))
                        opPrice = OrderOpenPrice();
                     if (OrderModify(ticket, opPrice, slPrice, tpPrice, 0, clrRed))
                        Print("[ECN SELL SUCCESS] SL dan TP berhasil dipasang pada tiket #", ticket);
                     else
                        Print("[ECN SELL WARN] OrderModify SL/TP gagal: ", GetLastError());
                  }
                  else err = GetLastError();
               }
               if (ticket <= 0)
               {
                  Print("[SELL REJECTED MT4] Error: ", err);
                  g_lastSignalType = "ORDER DITOLAK BROKER (Error " + IntegerToString(err) + ")";
               }
            }

            if (ticket > 0)
            {
               if (isSMCSniperSELL)
               {
                  g_sniperSELL.stage = SNIPER_STAGE_IDLE;
                  g_sniperSELL.statusText = "IDLE (EXECUTED TICKET #" + IntegerToString(ticket) + ")";
               }
               GlobalVariableSet("VIKAR_INIT_R_" + IntegerToString(ticket), MathMax(slPrice - Bid, 10 * Point));
               if (InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0)
                  g_autopsy.tradesWithExtraBuffer--;
               SaveTradeEntrySnapshotMT4(ticket, -1, activePatIdSELL, scoreRes.totalScore, currentAtr);
               lastOrderBarTime = Time[0];
               string patStr = isProPullbackSELL ? ("Pro Pullback Scalper (" + g_proPullbackSELL.confluencesStr + ")") : (isSMCSniperSELL ? "Sequential SMC Sniper (Sweep->CHoCH->FVG)" : (isMomentumBreakout ? "Momentum Breakout Expansion" : g_candleAnalysis.patternName));
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
         }
         else
         {
            if (scoreRes.totalScore < effectiveMinScoreSELL)
               g_lastSignalType = "SKOR KURANG: " + DoubleToString(scoreRes.totalScore, 0) + " / MIN " + DoubleToString(effectiveMinScoreSELL, 0) + " (SELL)";
            else if (!isHeadroomOk)
               g_lastSignalType = "HEADROOM SEMPIT KE S1 (SELL)";
            else if (!isPullbackEMA)
               g_lastSignalType = "MENUNGGU PULLBACK KE RIBBON EMA (SELL)";
            else if (!isRejection)
               g_lastSignalType = "MENUNGGU CANDLE REJECTION (SELL)";
            else if (!isOBMitigatedOk)
               g_lastSignalType = "MENUNGGU MITIGASI ORDER BLOCK (SELL)";
            else if (!isFiboGPOk)
               g_lastSignalType = "DILUAR GOLDEN POCKET FIBO (SELL)";
            else if (!smcBearishOk)
               g_lastSignalType = "STRUKTUR SMC TIDAK MEMENUHI (SELL)";
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

   double totalGrowthPct = (g_eaInitialBalance > 0.0001) ? ((balance - g_eaInitialBalance) / g_eaInitialBalance * 100.0) : 0.0;

   int panelX = g_panelX;
   int panelY = g_panelY;
   int panelW = g_panelW;
   int panelH = InpShowPnLStats ? 704 : 624;

   // 1. Container Utama
   CreateOrUpdateRect("VIKAR_HUD_BG", panelX, panelY, panelW, panelH, C'15,23,42', C'51,65,85');

   // 2. Header Banner (Tinggi 38 px untuk ruang nafas judul & subjudul)
   CreateOrUpdateRect("VIKAR_HUD_HDR_BG", panelX, panelY, panelW, 38, C'3,105,161', C'56,189,248');
   CreateOrUpdateText("VIKAR_HUD_HDR_TITLE", panelX + 12, panelY + 3, "VIKAR 4-PILLAR PRO v4.20 (SMC SNIPER)", clrWhite, 10, "Segoe UI Bold");
   double currentLotSize = CalculateRiskLot(PipToPrice(25.0));
   string lotDisplay = (InpLotType == LOT_TYPE_BROKER_MIN) ? ("Min Lot: " + DoubleToString(currentLotSize, 2)) : ("Lot: " + DoubleToString(currentLotSize, 2));
   CreateOrUpdateText("VIKAR_HUD_HDR_SUB", panelX + 12, panelY + 21, Symbol() + " [" + IntegerToString(Period()) + "M] | " + lotDisplay + " | ID: " + IntegerToString(InpMagicNumber), C'224,242,254', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_HDR_DRAG", panelX + panelW - 74, panelY + 11, "[ :: GESER ]", C'186,230,253', 8, "Segoe UI Bold");

   // 3. Ringkasan Saldo Akun
   CreateOrUpdateText("VIKAR_HUD_BAL_START", panelX + 12, panelY + 45, "Start Modal: $" + DoubleToString(g_eaInitialBalance, 2) + "  (Aktivasi: " + TimeToStr(g_eaStartTime, TIME_MINUTES) + ")", C'148,163,184', 7, "Segoe UI");
   CreateOrUpdateText("VIKAR_HUD_BAL_CURR", panelX + 12, panelY + 59, "Saldo: $" + DoubleToString(balance, 2) + "  |  Equity: $" + DoubleToString(equity, 2), clrWhite, 8, "Segoe UI Bold");

   color floatClr = (openFloating > 0) ? C'74,222,128' : (openFloating < 0 ? C'248,113,113' : C'203,213,225');
   CreateOrUpdateText("VIKAR_HUD_FLOAT", panelX + 12, panelY + 75, "Floating: " + FormatPnL(openFloating) + " (" + IntegerToString(openCount) + " Posisi)  |  Spread: " + DoubleToString(spread, 1) + " pips", floatClr, 8, "Segoe UI Bold");

   int currY = panelY + 95;

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
   if (g_bullishOB.isValid)
      obStr = "Bull OB: " + DoubleToString(g_bullishOB.bottom, 1) + "-" + DoubleToString(g_bullishOB.top, 1) + (g_bullishOB.isMitigated ? " [TESTED]" : " [FRESH]");
   else if (g_bearishOB.isValid)
      obStr = "Bear OB: " + DoubleToString(g_bearishOB.bottom, 1) + "-" + DoubleToString(g_bearishOB.top, 1) + (g_bearishOB.isMitigated ? " [TESTED]" : " [FRESH]");
   else if (g_activeFVG.isValid)
      obStr = "FVG: " + DoubleToString(g_activeFVG.bottom, 1) + "-" + DoubleToString(g_activeFVG.top, 1);
   CreateOrUpdateText("VIKAR_HUD_OB_FVG", panelX + 12, currY, "[Order Block] : " + obStr, C'244,114,182', 7, "Segoe UI");
   currY += 14;

   string smcStr = g_smcAnalysis.structureName;
   if (g_smcAnalysis.hasSweep) smcStr = smcStr + " [SWEEP]";
   else if (g_smcAnalysis.hasBOS) smcStr = smcStr + " [BOS]";
   CreateOrUpdateText("VIKAR_HUD_PILAR1", panelX + 12, currY, "[SMC Struktur]: " + smcStr, C'56,189,248', 7, "Segoe UI Bold");

   color trendClr = (g_dominantTrendBias == HTF_BIAS_BULLISH) ? C'74,222,128' : ((g_dominantTrendBias == HTF_BIAS_BEARISH) ? C'248,113,113' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_PILAR_HTF", panelX + 12, currY + 14, "[Trend Dominan]: " + g_dominantTrendStr, trendClr, 7, "Segoe UI Bold");

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

   string healDisplay = "STANDBY (NORMAL)";
   color healClr = C'52,211,153';
   if (InpUseSelfHealing && g_autopsy.isActive)
   {
      string extraGuard = "";
      if (InpUseDirectionalLearning && g_autopsy.failedDirection != 0 && TimeCurrent() < g_autopsy.directionPenaltyUntil)
         extraGuard += (g_autopsy.failedDirection == 1 ? " | Blok BUY" : " | Blok SELL");
      if (InpUseHourlyLearning && g_autopsy.toxicHour >= 0)
         extraGuard += (" | Toxic H:" + IntegerToString(g_autopsy.toxicHour));
      healDisplay = "AKTIF (+" + DoubleToString(g_autopsy.scorePenalty, 0) + " Skor" + extraGuard + ")";
      healClr = C'251,191,36';
   }
   CreateOrUpdateText("VIKAR_HUD_HEAL", panelX + 12, currY + 125, "[AI Brain / Heal]: " + healDisplay, healClr, 7, "Segoe UI Bold");

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

   // Baris POI Radar (v4.10 M15/M5)
   string poiDisplay = InpUsePOIStalker ? (g_m15Stalker.statusText != "" ? g_m15Stalker.statusText : "POI: MONITORING") : "POI STALKER: OFF";
   color poiClr = (StringFind(poiDisplay, "CETAR") >= 0 || StringFind(poiDisplay, "DI ZONA") >= 0) ? C'74,222,128' : ((StringFind(poiDisplay, "MENDEKATI") >= 0) ? C'56,189,248' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_M15_RADAR", panelX + 12, currY + 151, "[POI Radar (M15/M5)]: " + poiDisplay, poiClr, 7, "Segoe UI Bold");

   // Baris M1 Sub-Radar (v3.90)
   string m1RadarDisplay = InpUseMTFM1Engine ? (g_m1Sniper.statusText != "" ? g_m1Sniper.statusText : "M1: STANDBY") : "M1 ENGINE: OFF";
   color m1RadarClr = (StringFind(m1RadarDisplay, "SNIPER") >= 0 || StringFind(m1RadarDisplay, "CHoCH") >= 0) ? C'74,222,128' : ((StringFind(m1RadarDisplay, "RETEST") >= 0) ? C'56,189,248' : C'251,191,36');
   CreateOrUpdateText("VIKAR_HUD_M1_RADAR", panelX + 12, currY + 164, "[M1 Sub-Radar]: " + m1RadarDisplay, m1RadarClr, 7, "Segoe UI Bold");

   // Baris Rapor Pola Teruji (AI Pattern Matrix)
   string pmStr = InpUsePatternMatrix ? ("Terbaik: " + g_bestPatternStr) : "NONAKTIF";
   CreateOrUpdateText("VIKAR_HUD_PATMAT", panelX + 12, currY + 177, "[Rapor Pola]: " + pmStr, C'203,213,225', 7, "Segoe UI");

   // Baris Pre-News & Divergence Status (v2.60)
   color newsClr = (StringFind(g_newsStatusStr, "WASPADA") >= 0) ? C'248,113,113' : C'74,222,128';
   CreateOrUpdateText("VIKAR_HUD_NEWS", panelX + 12, currY + 190, "[News Shield]: " + g_newsStatusStr + " | Momentum: " + g_divStatusStr, newsClr, 7, "Segoe UI Bold");

   // Baris Anti-Sideways & VSA Status (v2.70)
   string adxStr = InpUseADXFilter ? ("ADX: " + DoubleToString(g_currentADXVal, 1)) : "ADX: OFF";
   string volStr = InpUseVolumeFilter ? ("Vol: " + DoubleToString(g_currentVolRatio * 100.0, 0) + "%") : "Vol: OFF";
   CreateOrUpdateText("VIKAR_HUD_SIDEWAYS", panelX + 12, currY + 203, "[Anti-Sideways]: " + adxStr + " | " + volStr + " | Slope: AKTIF", C'148,163,184', 7, "Segoe UI");

   // Baris Prop Firm Guardian & Trap Hunter (v3.00)
   string pfStr = InpUseEquityGuardian ? ("DD: " + DoubleToString(g_currentDailyDDPct, 1) + "% / Max " + DoubleToString(InpMaxDailyEquityDDPct, 1) + "%") : "OFF";
   color pfClr = (g_currentDailyDDPct >= InpMaxDailyEquityDDPct * 0.75) ? C'248,113,113' : C'148,163,184';
   CreateOrUpdateText("VIKAR_HUD_PROPFIRM", panelX + 12, currY + 216, "[Prop Firm Guard]: " + pfStr + " | Trap Hunter: AKTIF", pfClr, 7, "Segoe UI Bold");

   string discStatus = "AKTIF";
   color discClr = C'74,222,128';
   if (g_dailyProfitLocked) { discStatus = "DONE FOR THE DAY (LOCKED)"; discClr = C'251,191,36'; }
   else if (IsInRolloverWindow()) { discStatus = "ROLLOVER FREEZE"; discClr = C'248,113,113'; }
   else if (InpUseMaxDailyTrades && g_todayTradesCount >= InpMaxDailyTrades) { discStatus = "MAX TRADES REACHED"; discClr = C'248,113,113'; }
   string discStr = "Trades: " + IntegerToString(g_todayTradesCount) + (InpUseMaxDailyTrades ? ("/" + IntegerToString(InpMaxDailyTrades)) : "") + " | " + discStatus;
   CreateOrUpdateText("VIKAR_HUD_PRODISCIPLINE", panelX + 12, currY + 229, "[Pro Discipline] : " + discStr, discClr, 7, "Segoe UI Bold");

   // Baris SMC Sniper (Sweep -> CHoCH -> FVG Retest)
   string sniperDisplay = "OFF";
   color sniperClr = C'148,163,184';
   if (InpUseSequentialSMCSniper)
   {
      if (g_sniperBUY.stage == SNIPER_STAGE_READY_TO_FIRE)
      {
         sniperDisplay = "BUY READY (FVG Retest 1:" + DoubleToString(InpSniperMinRR, 1) + "+ RR)";
         sniperClr = C'74,222,128';
      }
      else if (g_sniperSELL.stage == SNIPER_STAGE_READY_TO_FIRE)
      {
         sniperDisplay = "SELL READY (FVG Retest 1:" + DoubleToString(InpSniperMinRR, 1) + "+ RR)";
         sniperClr = C'248,113,113';
      }
      else if (g_sniperBUY.stage == SNIPER_STAGE_FVG_ARMED)
      {
         sniperDisplay = "BUY ARMED (Menunggu Retest FVG)";
         sniperClr = C'251,191,36';
      }
      else if (g_sniperSELL.stage == SNIPER_STAGE_FVG_ARMED)
      {
         sniperDisplay = "SELL ARMED (Menunggu Retest FVG)";
         sniperClr = C'251,191,36';
      }
      else if (g_sniperBUY.stage == SNIPER_STAGE_CHOCH_CONFIRMED)
      {
         sniperDisplay = "BUY CHoCH Terkonfirmasi (Cari FVG)";
         sniperClr = C'56,189,248';
      }
      else if (g_sniperSELL.stage == SNIPER_STAGE_CHOCH_CONFIRMED)
      {
         sniperDisplay = "SELL CHoCH Terkonfirmasi (Cari FVG)";
         sniperClr = C'56,189,248';
      }
      else if (g_sniperBUY.stage == SNIPER_STAGE_SWEEP_DETECTED)
      {
         sniperDisplay = "BUY Sweep SSL (Menunggu CHoCH)";
         sniperClr = C'244,114,182';
      }
      else if (g_sniperSELL.stage == SNIPER_STAGE_SWEEP_DETECTED)
      {
         sniperDisplay = "SELL Sweep BSL (Menunggu CHoCH)";
         sniperClr = C'244,114,182';
      }
      else
      {
         sniperDisplay = "STANDBY (Memindai Sweep)";
         sniperClr = C'148,163,184';
      }
   }
   CreateOrUpdateText("VIKAR_HUD_SMC_SNIPER", panelX + 12, currY + 242, "[SMC Sniper]   : " + sniperDisplay, sniperClr, 7, "Segoe UI Bold");
   currY += 266;

   // 6. Inset Live Execution Status
   CreateOrUpdateRect("VIKAR_HUD_STATUS_BG", panelX + 8, currY, panelW - 16, 52, C'15,23,42', C'2,132,199');
   CreateOrUpdateText("VIKAR_HUD_STATUS_LBL", panelX + 15, currY + 4, "STATUS KECERDASAN PASAR:", C'56,189,248', 7, "Segoe UI Bold");

   string statusDisplay = g_lastSignalType;
   if (openCount == 0 && StringFind(g_lastSignalType, "EXECUTED") >= 0)
      statusDisplay = "ORDER SELESAI (SUDAH HIT TP / SL+) | SCANNING SETUP";

   CreateOrUpdateText("VIKAR_HUD_STATUS_VAL", panelX + 15, currY + 19, statusDisplay, clrWhite, 7, "Segoe UI Bold");
   string beStr = InpUseBreakeven ? ("SL+ (+" + DoubleToString(InpBreakevenLockPips, 0) + "p)") : "BE: OFF";
   string cutStr = InpAutoCutProfit ? "Cut: ON" : "Cut: OFF";
   string trailStr = (InpUsePointsTrailing || InpUseCandleTrailing || InpUseTrailingEMA21) ? "Trail: ON" : "Trail: OFF";
   string partialStr = InpUsePartialClose ? ("Partial: " + DoubleToString(InpPartialClosePercent, 0) + "%") : "Partial: OFF";
   CreateOrUpdateText("VIKAR_HUD_STATUS_CFG", panelX + 15, currY + 34, beStr + " | " + cutStr + " | " + trailStr + " | Lot: " + DoubleToString(currentLotSize, 2), C'148,163,184', 7, "Segoe UI");

   // === TOMBOL RESET DD LOCK (v3.60) ===
   bool anyLockActive = g_equityLockActive || g_dailyLossLimitHit || g_cooldownUntilTime > TimeCurrent();
   currY += 56;
   color ddBtnBg  = anyLockActive ? C'153,27,27' : C'20,83,45';
   color ddBtnTxt = clrWhite;
   string ddBtnLabel = anyLockActive ? "[TERKUNCI] DD LOCK AKTIF - KLIK RESET" : "[BEBAS] NORMAL (KLIK = RESET DD LOCK)";
   CreateOrUpdateRect("VIKAR_HUD_BTN_RESETDD_BG", panelX + 8, currY, panelW - 16, 22, ddBtnBg, ddBtnBg);
   CreateOrUpdateText("VIKAR_HUD_BTN_RESETDD",    panelX + 14, currY + 4, ddBtnLabel, ddBtnTxt, 7, "Segoe UI Bold");
   // Simpan koordinat tombol untuk deteksi klik
   g_ddBtnY1 = currY;
   g_ddBtnY2 = currY + 22;
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
   InitPatternMatrix();
   LoadAutopsyStateMT4();

   lastBarTime = Time[0]; // Safeguard: tunggu lilin penuh pertama pasca pasang EA

   ZeroMemory(g_sniperBUY);
   ZeroMemory(g_sniperSELL);
   g_sniperBUY.stage = SNIPER_STAGE_IDLE;
   g_sniperBUY.statusText = "IDLE (SCANNING SWEEP)";
   g_sniperSELL.stage = SNIPER_STAGE_IDLE;
   g_sniperSELL.statusText = "IDLE (SCANNING SWEEP)";

   CleanSMCObjects();
   double initAtr = iATR(Symbol(), 0, 14, 1);

   UpdateDailyPivots();
   DrawDailyPivotsOnChart();
   UpdateSMCSwings(100);
   ExtractValidSwings(100, initAtr);
   DetectOrderBlocks(100, initAtr);
   TrackFairValueGaps(100);
   UpdateSequentialSMCSniper(initAtr);
   g_smcAnalysis = AnalyzeMarketStructure();
   UpdateAutoFibo(Close[1] > iMA(Symbol(), 0, InpTrendEMA, 0, MODE_EMA, PRICE_CLOSE, 1));
   DrawFiboObjectsOnChart();
   g_m15Stalker = AnalyzeM15InstitutionalPOI();
   DrawM15POIMarkersOnChart();
   DrawSMCObjectsOnChart();
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
//+------------------------------------------------------------------+
//| REAL-TIME AUTO-CALIBRATION ENGINE (v3.20)                        |
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
   double atr14Val = iATR(Symbol(), 0, 14, 1);
   if (atr14Val <= 0.0) atr14Val = PipToPrice(20.0);

   double atr100Val = iATR(Symbol(), 0, 100, 1);
   if (atr100Val <= 0.0) atr100Val = atr14Val;

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
      g_calibration.cooldownBars = (int)MathMin(8, InpSignalCooldownBars * g_consecutiveLossCount);
      g_calibration.slBufferAtrMult = MathMin(InpAutoTuningMaxBufferMult, g_calibration.slBufferAtrMult + 0.25);
   }

   g_calibration.consecutiveLossStreak = g_consecutiveLossCount;
   g_calibration.isCalibrated          = true;
}

void OnTick()
{
   AutoCalibrateTradingParameters();

   // 1. Kelola Posisi Aktif EA
   ManageActiveTrades();

   // 1.1 Asisten Trade Manual (Auto SL/TP/BE/Trailing untuk Order Magic 0)
   ManageManualTrades();

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

   // 3.0 Rollover Spread Blackout Shield (v3.30)
   if (IsInRolloverWindow())
   {
      g_lastSignalType = "ROLLOVER FREEZE: JENDELA SPREAD MELEBAR TENGAH MALAM";
      return;
   }

   // 3.05 Institutional Killzones Sesi Filter (v3.30)
   if (!IsInKillzoneWindow())
   {
      g_lastSignalType = "DILUAR KILLZONE INSTITUSIONAL (LONDON & NY ONLY)";
      return;
   }

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
                  if (OrderType() == OP_BUY)
                  {
                     if (!OrderClose(OrderTicket(), OrderLots(), Bid, InpDeviation, clrGold))
                        Print("[ERROR] Friday Guard Close BUY gagal: ", GetLastError());
                  }
                  else if (OrderType() == OP_SELL)
                  {
                     if (!OrderClose(OrderTicket(), OrderLots(), Ask, InpDeviation, clrGold))
                        Print("[ERROR] Friday Guard Close SELL gagal: ", GetLastError());
                  }
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

   // 5.1 Pre-News Event Shield (v2.60)
   string activeNewsEvent = "";
   if (InpUseNewsShield && IsInsideNewsWindow(activeNewsEvent))
   {
      g_lastSignalType = "PRE-NEWS SHIELD: PEMBEKUAN ORDER JELANG " + activeNewsEvent;
      return;
   }

   // 5.2 Spread Anomaly Spike Shield (v2.60)
   if (InpUseNewsShield && IsSpreadSpikeDetected())
   {
      g_lastSignalType = "SPREAD SPIKE SHIELD: SPREAD MELEBAR ABNORMAL";
      return;
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

      // Deteksi area drag header
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
      // === TOMBOL RESET DD LOCK ===
      else if (clickX >= g_panelX + 8 && clickX <= g_panelX + g_panelW - 8 &&
               clickY >= g_ddBtnY1    && clickY <= g_ddBtnY2)
      {
         // Reset semua status lock DD
         g_equityLockActive     = false;
         g_dailyLossLimitHit    = false;
         g_cooldownUntilTime    = 0;
         g_consecutiveLossCount = 0;
         g_todayClosedProfit    = 0.0;
         g_lastSignalType = "[RESET] DD LOCK DIRESET MANUAL - TRADING AKTIF KEMBALI";
         Print("[DD RESET] Semua lock DD & Circuit Breaker direset manual oleh trader.");
         Alert("[VIKAR EA MT4] DD Lock direset! Trading aktif kembali.");
         UpdateDashboard();
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
