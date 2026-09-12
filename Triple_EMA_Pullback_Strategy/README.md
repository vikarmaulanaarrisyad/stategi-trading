# 📈 TRIPLE EMA PULLBACK SYSTEM (XAUUSD / FOREX) — METATRADER 5 (MQL5)

Sistem trading tren dan pullback presisi tinggi untuk **MetaTrader 5 (MT5)** yang dirancang berdasarkan pengalaman lebih dari 10 tahun trading **XAUUSD (Gold)** dan pasar Forex.

---

## 📑 DAFTAR ISI
1. [Filosofi & Komponen Strategi](#1-filosofi--komponen-strategi)
2. [Arsitektur File & Struktur Folder](#2-arsitektur-file--struktur-folder)
3. [Aturan Setup Entry Valid](#3-aturan-setup-entry-valid)
   - [Setup BUY Valid](#-setup-buy-valid)
   - [Setup SELL Valid](#-setup-sell-valid)
4. [Filter False Signals (Waspada Sinyal Palsu)](#4-filter-false-signals-waspada-sinyal-palsu)
5. [Katalog 18 Pola Candlestick Konfirmasi (9 Bullish & 9 Bearish)](#5-katalog-18-pola-candlestick-konfirmasi)
6. [Panduan Instalasi & Kompilasi di MetaTrader 5](#6-panduan-instalasi--kompilasi-di-metatrader-5)
7. [Panduan Parameter Indikator & Expert Advisor](#7-panduan-parameter-indikator--expert-advisor)
8. [Rekomendasi Setup Khusus XAUUSD (Gold)](#8-rekomendasi-setup-khusus-xauusd-gold)

---

## 1. FILOSOFI & KOMPONEN STRATEGI

Strategi ini beroperasi pada prinsip bahwa **"Trend is your friend, but Value is where you enter"**. Kita tidak mengejar harga di puncak atau lembah, melainkan menunggu harga beristirahat (*pullback*) ke area nilai (*Value Zone*).

### 3 Garis Exponential Moving Average (EMA):
1. **EMA 8 (Fast EMA - Warna Biru Muda)**:
   - Mengukur momentum jangka pendek yang agresif.
2. **EMA 21 (Medium EMA - Warna Oranye / Merah)**:
   - Berfungsi sebagai **Dynamic Support** saat uptrend dan **Dynamic Resistance** saat downtrend.
   - Area antara EMA 8 dan EMA 21 disebut **"The Value Zone" (Zona Pullback)**.
3. **EMA 125 (Major Baseline Trend - Warna Hijau)**:
   - Filter tren utama jangka panjang (*Institutional Baseline*).
   - **Harga di atas EMA 125**: Pasar dikuasai Bullish (HANYA FOKUS BUY).
   - **Harga di bawah EMA 125**: Pasar dikuasai Bearish (HANYA FOKUS SELL).

---

## 2. ARSITEKTUR FILE & STRUKTUR FOLDER

```
Triple_EMA_Pullback_Strategy/
│
├── Include/
│   ├── CandlePatterns.mqh               # Library deteksi 18 pola candlestick rejection & confirmation
│   └── MarketStructure.mqh              # Library analisis struktur HH/HL, LH/LL & filter sideways/chop
│
├── Indicators/
│   └── Triple_EMA_Pullback_Indicator.mq5 # Custom Indicator visual: EMA 8, 21, 125, Panah Sinyal,
│                                        # HUD Dashboard on-chart, & Alert (Pop-up/Push/Sound)
│
├── Experts/
│   └── Triple_EMA_Pullback_EA.mq5        # Expert Advisor (Auto Trading Robot) dengan Money Management,
│                                        # Dynamic SL/TP, Auto Break-Even & Trailing Stop
│
└── README.md                            # Dokumentasi lengkap dan buku panduan strategi
```

---

## 3. ATURAN SETUP ENTRY VALID

### 🟢 SETUP BUY VALID:
1. **Trend Utama Bullish**:
   - Harga berada di atas EMA 125 (`Close > EMA 125`).
   - EMA 8 berada di atas EMA 21 (`EMA 8 > EMA 21`).
2. **Struktur Pasar Valid**:
   - Pasar membentuk struktur **Higher High (HH)** dan **Higher Low (HL)**.
3. **Pullback Terjadi**:
   - Harga mengalami koreksi turun menuju area antara EMA 8 dan EMA 21.
   - Low candle menyentuh atau menguji EMA 8 / EMA 21, namun **wajib tetap berada di atas EMA 125**.
4. **Konfirmasi Candlestick Bullish**:
   - Muncul salah satu dari **9 Pola Candlestick Bullish Rejection** (lihat bab 5).
5. **Filter False Signal Lolos**:
   - EMA 8 & 21 tidak sedang saling menyilang bolak-balik (bukan pasar sideways).
   - Jarak candle ke EMA 8 tidak overextended (maksimal 2.0x ATR 14).
6. **Entry & Exit**:
   - **Entry**: Pada open candle berikutnya setelah candle konfirmasi selesai (Bar 1 close).
   - **Stop Loss**: Di bawah Low candle konfirmasi / Swing Low terakhir + buffer 5-10 pips.
   - **Take Profit**: Minimal Risk:Reward 1:1.5 hingga 1:2.0, atau resistance berikutnya.

---

### 🔴 SETUP SELL VALID:
1. **Trend Utama Bearish**:
   - Harga berada di bawah EMA 125 (`Close < EMA 125`).
   - EMA 8 berada di bawah EMA 21 (`EMA 8 < EMA 21`).
2. **Struktur Pasar Valid**:
   - Pasar membentuk struktur **Lower High (LH)** dan **Lower Low (LL)**.
3. **Pullback Terjadi**:
   - Harga mengalami koreksi naik menuju area antara EMA 8 dan EMA 21.
   - High candle menyentuh atau menguji EMA 8 / EMA 21, namun **wajib tetap berada di bawah EMA 125**.
4. **Konfirmasi Candlestick Bearish**:
   - Muncul salah satu dari **9 Pola Candlestick Bearish Rejection** (lihat bab 5).
5. **Filter False Signal Lolos**:
   - Tidak terjadi sideways / whipsaw di sekitar EMA 125.
   - Candle tidak overextended dari EMA 8.
6. **Entry & Exit**:
   - **Entry**: Pada open candle berikutnya setelah candle konfirmasi selesai.
   - **Stop Loss**: Di atas High candle konfirmasi / Swing High terakhir + buffer 5-10 pips.
   - **Take Profit**: Minimal Risk:Reward 1:1.5 hingga 1:2.0, atau support berikutnya.

---

## 4. FILTER FALSE SIGNALS (WASPADA SINYAL PALSU)

Keunggulan utama sistem ini dibanding strategi indikator biasa adalah 4 lapis perlindungan dari jebakan pasar (*market traps*):

1. **Anti-Chop Filter (EMA 8 & 21 Bolak-balik)**:
   - Jika EMA 8 dan EMA 21 saling memotong >= 2 kali dalam 15 candle terakhir, pasar dideteksi sedang **konsolidasi/sideways**.
   - *Tindakan Sistem*: Memblokir seluruh sinyal sampai salah satu pihak (buyer/seller) mendominasi secara jelas.
2. **Anti-Whipsaw Filter (Harga Bolak-balik Menembus EMA 125)**:
   - Jika harga menembus ke atas dan ke bawah EMA 125 berulang kali dalam 20 candle terakhir, tren utama sedang kehilangan arah.
   - *Tindakan Sistem*: Mengabaikan sinyal sampai harga berkonsolidasi tegas di salah satu sisi EMA 125.
3. **Struktur Market Validator (HH/HL vs LH/LL)**:
   - Menghindari entry saat harga bergerak dalam range sempit (*indecision box*). Sinyal Buy hanya dieksekusi jika swing high dan swing low mencetak titik yang lebih tinggi.
4. **Anti-Overextended Filter (Jarak Terlalu Jauh dari EMA)**:
   - Seringkali trader pemula mengejar harga (*FOMO*) saat melihat candle hijau panjang.
   - Jika jarak harga ke EMA 8 > `2.0 * ATR(14)`, risiko koreksi tajam sangat tinggi.
   - *Tindakan Sistem*: Sinyal diberi status **FILTERED: Overextended**, mencegah entri terlambat.

---

## 5. KATALOG 18 POLA CANDLESTICK KONFIRMASI

### 🟢 9 Pola Konfirmasi Bullish:

| No | Nama Pola | Karakteristik Utama di Area EMA 8 - 21 | Keterangan Rejection |
|---|---|---|---|
| 1 | **Hammer** | Ekor bawah panjang (>= 2x body), body kecil di atas, upper wick minimal. | Penolakan harga bawah yang kuat oleh buyer. |
| 2 | **Bullish Pin Bar** | Ekor bawah >= 60% total range, body kecil di 35% teratas candle. | Buyer menolak penurunan saat menyentuh EMA 21. |
| 3 | **Bullish Engulfing** | Candle hijau berbadan besar menelan sempurna body candle merah sebelumnya. | Perubahan momentum seketika dari seller ke buyer. |
| 4 | **Morning Star** | Pola 3 candle: Bearish -> Candle kecil indecision di EMA -> Bullish kuat. | Pola pembalikan arah 3 candle paling handal. |
| 5 | **Piercing Line** | Candle merah diikuti candle hijau yang menutup > 50% dari body merah. | Daya beli bangkit dari support EMA. |
| 6 | **Three White Soldiers** | 3 candle hijau berturut-turut dengan higher close dan lower shadow pendek. | Momentum ekspansi bullish kuat keluar dari zona EMA. |
| 7 | **Bullish Doji Rejection** | Body sangat tipis (<= 10%), ekor bawah panjang menolak support EMA 8/21. | Ketidakpastian seller diserap sepenuhnya oleh buyer. |
| 8 | **Bullish Inside Bar** | Candle kecil berada di dalam range candle induk sebelumnya, lalu breakout ke atas. | Pengurangan tekanan jual diikuti letupan beli. |
| 9 | **Two Candle Rejection** | Candle pertama berekor bawah panjang menabrak EMA, diikuti candle hijau kuat. | Rejection ganda yang sangat solid untuk konfirmasi. |

---

### 🔴 9 Pola Konfirmasi Bearish:

| No | Nama Pola | Karakteristik Utama di Area EMA 8 - 21 | Keterangan Rejection |
|---|---|---|---|
| 1 | **Shooting Star** | Ekor atas panjang (>= 2x body), body kecil di bawah, lower wick minimal. | Penolakan harga atas yang tajam oleh seller. |
| 2 | **Bearish Pin Bar** | Ekor atas >= 60% total range, body kecil di 35% terbawah candle. | Seller menolak kenaikan saat membentur EMA 21. |
| 3 | **Bearish Engulfing** | Candle merah berbadan besar menelan sempurna body candle hijau sebelumnya. | Perubahan momentum seketika dari buyer ke seller. |
| 4 | **Dark Cloud Cover** | Candle hijau diikuti candle merah yang menutup < 50% dari body hijau. | Daya jual menembus pertahanan buyer di resistance EMA. |
| 5 | **Evening Star** | Pola 3 candle: Bullish -> Candle kecil indecision di EMA -> Bearish kuat. | Pola pembalikan arah 3 candle dari uptrend ke downtrend. |
| 6 | **Three Black Crows** | 3 candle merah berturut-turut dengan lower close dan ekor atas pendek. | Momentum ekspansi bearish kuat keluar dari zona EMA. |
| 7 | **Bearish Doji Rejection** | Body tipis (<= 10%), ekor atas panjang menolak resistance EMA 8/21. | Ketidakpastian buyer diserap sepenuhnya oleh seller. |
| 8 | **Bearish Inside Bar** | Candle kecil berada di dalam range candle induk sebelumnya, lalu breakdown ke bawah. | Pengurangan tekanan beli diikuti letupan jual. |
| 9 | **Two Candle Rejection** | Candle pertama berekor atas panjang membentur EMA, diikuti candle merah kuat. | Rejection ganda yang sangat solid untuk entri Sell. |

---

## 6. PANDUAN INSTALASI & KOMPILASI DI METATRADER 5

### Langkah 1: Buka Folder Data MetaTrader 5
1. Buka aplikasi **MetaTrader 5** di PC/Laptop Anda.
2. Klik menu **File** -> **Open Data Folder** (Buka Folder Data).
3. Buka folder **MQL5**.

### Langkah 2: Salin File Proyek
Salin file-file dari folder proyek ini ke direktori MT5 yang sesuai:
1. **Folder Include**:
   Salin `CandlePatterns.mqh` dan `MarketStructure.mqh` ke dalam:
   `MQL5\Include\`
2. **Folder Indicators**:
   Salin `Triple_EMA_Pullback_Indicator.mq5` ke dalam:
   `MQL5\Indicators\`
3. **Folder Experts**:
   Salin `Triple_EMA_Pullback_EA.mq5` ke dalam:
   `MQL5\Experts\`

### Langkah 3: Kompilasi di MetaEditor
1. Di MetaTrader 5, tekan tombol **F4** untuk membuka **MetaEditor**.
2. Di panel Navigator (sebelah kiri), cari file:
   - `Indicators\Triple_EMA_Pullback_Indicator.mq5` -> Buka lalu klik tombol **Compile** (atau tekan **F7**).
   - `Experts\Triple_EMA_Pullback_EA.mq5` -> Buka lalu klik tombol **Compile** (atau tekan **F7**).
3. Pastikan pada tab *Errors* di bagian bawah tertulis:
   `0 errors, 0 warnings`.

### Langkah 4: Pasang ke Chart
1. Kembali ke MT5. Buka chart instrumen (contoh: **XAUUSD** timeframe **M15** atau **H1**).
2. Di panel **Navigator** MT5 (`Ctrl + N`), cari:
   - **Indicators**: Tarik `Triple_EMA_Pullback_Indicator` ke chart.
   - **Experts**: Tarik `Triple_EMA_Pullback_EA` ke chart (pastikan tombol **Algo Trading** di toolbar MT5 sudah aktif dan centang *Allow Algo Trading*).

---

## 7. PANDUAN PARAMETER INDIKATOR & EXPERT ADVISOR

### Parameter Indikator:
- `InpEMA8_Period` (Default: 8) : Periode EMA Cepat.
- `InpEMA21_Period` (Default: 21) : Periode EMA Menengah (Dynamic S/R).
- `InpEMA125_Period` (Default: 125) : Periode EMA Baseline Tren Utama.
- `InpUseStructureFilter` (Default: true) : Validasi struktur HH/HL (Buy) atau LH/LL (Sell).
- `InpUseChopFilter` (Default: true) : Filter sideways persilangan EMA 8 & 21.
- `InpUseWhipsawFilter` (Default: true) : Filter whipsaw penembusan EMA 125.
- `InpUseOverextendFilter` (Default: true) : Filter candle yang melompat terlalu jauh dari EMA.
- `InpShowDashboard` (Default: true) : Menampilkan HUD Panel Elegan di sudut chart.
- `InpPopupAlert` / `InpPushNotification` / `InpSoundAlert` : Opsi notifikasi lengkap ke PC dan aplikasi HP.

### Parameter Expert Advisor (Auto Trader):
- `InpLotMode` : Pilih `LOT_RISK_PERCENT` (Rekomendasi 1% - 2%) atau `LOT_FIXED`.
- `InpSLMode` : Mode penentuan Stop Loss (`SL_SWING_CANDLE`, `SL_ATR_BASED`, atau `SL_FIXED_POINTS`).
- `InpRiskRewardRatio` (Default: 2.0) : Target Take Profit (1:2 R:R).
- `InpUseBreakEven` (Default: true) : Otomatis memindahkan SL ke titik entry (BEP) saat profit mencapai 1:1 R:R.
- `InpUseTrailingStop` (Default: true) : Trailing stop otomatis mengikuti garis EMA 21 untuk mengunci profit tren panjang.
- `InpUseTimeFilter` (Default: true) : Mengunci trading hanya pada jam likuiditas tinggi (08:00 - 21:00 waktu broker).
- `InpMaxSpreadPoints` (Default: 40) : Perlindungan dari pelebaran spread di Gold.

---

## 8. REKOMENDASI SETUP KHUSUS XAUUSD (GOLD)

Emas (*Gold / XAUUSD*) memiliki volatilitas dan karakteristik likuiditas yang unik:

1. **Timeframe Terbaik**:
   - **M15 (Scalping / Day Trading)**: Ideal untuk trader aktif yang mencari 1 - 3 setup berkualitas per hari.
   - **H1 (Swing Trading)**: Sangat presisi, memiliki tingkat keberhasilan tertinggi karena tren EMA 125 di H1 sangat dihormati oleh institusi.
2. **Sesi Trading Paling Menguntungkan**:
   - **Sesi London (14:00 - 18:00 WIB)**: Awal pergerakan tren harian.
   - **Sesi London - New York Overlap (19:30 - 23:00 WIB)**: Likuiditas tertinggi dan volume transaksi terbesar pada XAUUSD.
   - *Hindari*: Sesi penutupan pasar / rollover (04:00 - 06:00 WIB) karena spread melebar secara drastis.
3. **Manajemen Resiko Disiplin**:
   - Resiko maksimal per trade: **1% - 1.5%** dari total modal akun.
   - Jangan pernah menggeser Stop Loss menjauh saat harga berlawanan arah.
   - Gunakan fitur **Auto Break-Even** dan **Trailing EMA 21** untuk membiarkan profit berlari (*let your profits run*) saat Gold sedang trending kuat ratusan pips.

---

*Selamat trading secara profesional dan disiplin bersama sistem Triple EMA Pullback!*
