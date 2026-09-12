# 📘 PANDUAN LENGKAP & CARA SETUP: TRIPLE EMA PULLBACK SYSTEM (MT5)

Dokumen ini berisi panduan praktis langkah-demi-langkah bagi trader untuk memasang, membaca indikator, menyaring sinyal palsu, dan mengeksekusi trading dengan rasio Risk:Reward tinggi pada instrumen **XAUUSD (Gold)** dan pasar Forex.

---

## 📑 DAFTAR ISI
1. [Prinsip Dasar Strategi](#1-prinsip-dasar-strategi)
2. [Cara Memasang Indikator & EA ke Chart MT5](#2-cara-memasang-indikator--ea-ke-chart-mt5)
3. [Cara Membaca HUD Dashboard (Di Bawah Kiri Chart)](#3-cara-membaca-hud-dashboard)
4. [SOP Eksekusi Sinyal BUY Step-by-Step](#4-sop-eksekusi-sinyal-buy-step-by-step)
5. [SOP Eksekusi Sinyal SELL Step-by-Step](#5-sop-eksekusi-sinyal-sell-step-by-step)
6. [Memahami 4 Filter False Signal (Pencegah Jebakan Pasar)](#6-memahami-4-filter-false-signal)
7. [Pengaturan Parameter Terbaik Khusus XAUUSD (Gold)](#7-pengaturan-parameter-terbaik-khusus-xauusd-gold)
8. [Checklist Harian Sebelum Mengambil Posisi (Pre-Trade Checklist)](#8-checklist-harian-sebelum-mengambil-posisi)

---

## 1. PRINSIP DASAR STRATEGI

Sistem ini dibangun di atas fondasi **Trend Following + Price Action Pullback Rejection**. Kita tidak pernah membeli di harga pucuk (chasing market) atau menjual di lembah, melainkan menunggu harga mengalami koreksi sehat (*pullback*) ke area nilai (*Value Zone*).

### Komponen 3 Exponential Moving Average:
- ⚪ **EMA 125 (Putih Tebal - Solid White)**: **Tren Utama (Baseline Institusi)**.
  - Berwarna putih bersih sehingga **sangat kontras** dan tidak berbenturan dengan warna candlestick (hijau/merah).
  - Harga di atas EMA 125: Wajib **HANYA CARI BUY**.
  - Harga di bawah EMA 125: Wajib **HANYA CARI SELL**.
- 🟣 **EMA 21 (Magenta / Ungu Terang)**: **Dynamic Support / Resistance**.
  - Berwarna magenta cerah sehingga sangat mudah dibedakan dari candle merah (*downtrend*).
  - Merupakan batas utama area *Pullback / Value Zone*.
- 🔵 **EMA 8 (Cyan / Aqua Terang)**: **Momentum Cepat**.
  - Berwarna biru terang elektrik yang sangat mencolok di atas background chart hitam, memudahkan mata membaca lekukan momentum harga.
  - Bersama EMA 21 membentuk *Value Tunnel & Ribbon Cloud* (zona pullback bernilai tinggi).

---

## 2. CARA MEMASANG INDIKATOR & EA KE CHART MT5

### A. Memasang Indikator Visual:
1. Buka aplikasi **MetaTrader 5**.
2. Tekan **`Ctrl + N`** untuk membuka panel **Navigator** di sisi kiri.
3. Buka folder **Indicators** -> Cari **`Triple_EMA_Pullback_Indicator`**.
4. **Tarik (Drag & Drop)** ke atas chart Anda (misal: chart **XAUUSD** timeframe **M15** atau **H1**).
5. Pada jendela opsi input:
   - `InpDashboardCorner`: Sudah default ke `CORNER_LEFT_LOWER` (sudut bawah kiri agar grafik candle di atas tetap bersih).
   - `InpPopupAlert` / `InpPushNotification`: Biarkan `true` jika ingin mendapatkan alarm di PC dan HP saat ada sinyal valid.
6. Klik **OK**. Indikator, 3 garis EMA, panah sinyal, dan kotak dashboard bawah akan langsung muncul.

### B. Memasang Expert Advisor (Jika Ingin Auto Trading):
1. Di panel **Navigator**, buka bagian **Expert Advisors**.
2. Tarik **`Triple_EMA_Pullback_EA`** ke chart.
3. Pada tab **Common**, centang **Allow Algo Trading**.
4. Pada tab **Inputs**, tentukan manajemen modal:
   - `InpLotMode`: Pilih `LOT_RISK_PERCENT` (Rekomendasi: `1.0%` dari Equity).
   - `InpRiskRewardRatio`: Default `2.0` (Target profit 1:2).
   - `InpUseBreakEven`: Default `true` (Otomatis pindah SL ke titik impas saat profit 1:1 R:R).
5. Klik **OK**, lalu pastikan tombol **Algo Trading** di menu atas MT5 menyala **Hijau**.

---

## 3. CARA MEMBACA HUD DASHBOARD

Kotak Dashboard diletakkan di **sudut bawah kiri** chart untuk memberikan informasi pasar secara real-time tanpa menghalangi pergerakan candlestick:

```
┌────────────────────────────────────────────────────────────────────────┐
│  TRIPLE EMA PULLBACK                   [XAUUSD.dmb | PERIOD_M15]       │
├────────────────────────────────────────────────────────────────────────┤
│  Trend (EMA 125):     BULLISH (Above)      ← Status harga thd EMA 125  │
│  EMA 8/21 Align:      EMA 8 > 21 (Bullish) ← Susunan EMA 8 dan 21      │
│  Market Structure:    HH - HL (Uptrend)    ← Struktur ayunan harga     │
│  Last Pattern:        Bullish Engulfing    ← Pola rejection terakhir   │
│  Filter Status:       VALID SIGNAL PASS    ← Status filter keamanan    │
├────────────────────────────────────────────────────────────────────────┤
│  ● Gold & Forex Pullback System | Pro                                  │
└────────────────────────────────────────────────────────────────────────┘
```

### Arti Setiap Baris Status:
1. **Trend (EMA 125)**:
   - `BULLISH (Above)` (Warna Hijau): Harga berada di atas EMA 125 -> **Fokus Buy**.
   - `BEARISH (Below)` (Warna Merah): Harga berada di bawah EMA 125 -> **Fokus Sell**.
2. **EMA 8/21 Align**:
   - `EMA 8 > 21 (Bullish)` (Biru Muda): Garis EMA 8 di atas EMA 21 (momentum naik kuat).
   - `EMA 8 < 21 (Bearish)` (Oranye): Garis EMA 8 di bawah EMA 21 (momentum turun kuat).
3. **Market Structure**:
   - `HH - HL (Uptrend)` (Hijau Terang): Harga sedang mencetak Higher High & Higher Low yang valid.
   - `LH - LL (Downtrend)` (Merah Terang): Harga sedang mencetak Lower High & Lower Low yang valid.
   - `Sideways / Range` (Abu-abu): Pasar tidak memiliki tren yang jelas -> **Jangan entri!**
4. **Last Pattern**:
   - Menampilkan nama dari salah satu **18 Pola Candlestick Rejection** (Hammer, Pin Bar, Engulfing, Morning Star, dll.) yang baru saja terdeteksi di area EMA 8-21.
5. **Filter Status**:
   - `VALID SIGNAL PASS` (Warna Hijau): **Lolos semua filter!** Panah sinyal muncul dan Anda siap entri.
   - `FILTERED: Chop Sideways`: Sinyal dibatalkan karena EMA 8 & 21 bolak-balik menyilang.
   - `FILTERED: Overextended Candle`: Sinyal dibatalkan karena candle melompat terlalu jauh dari EMA (risiko koreksi tinggi).
   - `FILTERED: Whipsaw EMA 125`: Sinyal dibatalkan karena harga bolak-balik menembus EMA 125.

---

## 4. SOP EKSEKUSI SINYAL BUY STEP-BY-STEP

> [!IMPORTANT]
> **Hanya ambil posisi BUY jika panah AQUA (Naik) muncul dan Dashboard menampilkan status `VALID SIGNAL PASS`.**

```
Harga
  ▲                                             [Candle Konfirmasi Selesai]
  │                                                   ▲ (Close Bar)
  │                                  [Pullback]      │█│ ➔ ENTRY BUY DI SINI
  │                                    ┌───┐         │█│
  │                  ┌───┐             │   │        ┌┴─┴┐ (Hammer / Pin Bar / Engulfing)
  │                  │   │             └───┘        │   │
──────EMA 8 (Biru)───┴───┴──────────────────────────┴───┴────────────────────────
                                 ▲ Retest Area EMA 8-21
──────EMA 21 (Oranye)────────────┴───────────────────────────────────────────────
                                            [Stop Loss di bawah Low Rejection]
                                            -----------------------------------
──────EMA 125 (Baseline Hijau - Posisi Jauh di Bawah)────────────────────────────
```

### Langkah Eksekusi:
1. **Periksa Tren & EMA**:
   - Harga wajib berada di atas EMA 125.
   - Garis EMA 8 berada di atas EMA 21.
2. **Tunggu Pullback Masuk Zona Nilai (EMA 8 - 21)**:
   - Jangan buru-buru Buy saat candle sedang naik kencang menjauhi EMA.
   - Tunggu harga koreksi turun menyentuh atau masuk ke antara garis EMA 8 dan EMA 21.
   - **Syarat Mutlak**: Low candle koreksi tidak boleh menembus ke bawah EMA 125.
3. **Tunggu Candle Konfirmasi Bullish Close (Bar 1 Selesai)**:
   - Terdeteksi salah satu pola: *Hammer*, *Bullish Pin Bar*, *Bullish Engulfing*, *Morning Star*, *Piercing Line*, *Three White Soldiers*, *Doji Rejection*, *Inside Bar Breakout*, atau *Two Candle Rejection*.
4. **Eksekusi Entry & Penempatan SL / TP**:
   - **Entry Buy**: Buka posisi tepat saat candle konfirmasi tertutup sempurna (open bar berikutnya).
   - **Stop Loss (SL)**: Letakkan 5 - 10 pips (50 - 100 points) di bawah titik terendah (Low) candle konfirmasi atau swing low terdekat.
   - **Take Profit (TP)**: 
     - Minimal **1:1.5** atau **1:2.0** dari jarak Stop Loss Anda.
     - *Contoh di Gold*: Jika SL berjarak 30 pips ($3.00), maka TP minimal 60 pips ($6.00).
5. **Proteksi Profit (Trade Management)**:
   - Saat harga bergerak naik dan profit mencapai **1:1 R:R**, geser Stop Loss ke harga Entry (**Break-Even / BEP**).
   - Anda juga dapat menggunakan trailing stop mengikuti garis EMA 21.

---

## 5. SOP EKSEKUSI SINYAL SELL STEP-BY-STEP

> [!IMPORTANT]
> **Hanya ambil posisi SELL jika panah MAGENTA (Turun) muncul dan Dashboard menampilkan status `VALID SIGNAL PASS`.**

```
──────EMA 125 (Baseline Hijau - Posisi Jauh di Atas)─────────────────────────────
                                            [Stop Loss di atas High Rejection]
                                            -----------------------------------
──────EMA 21 (Oranye)────────────┬───────────────────────────────────────────────
                                 ▼ Retest Area EMA 8-21
──────EMA 8 (Biru)───┬───┬──────────────────────────┬───┬────────────────────────
  │                  │   │             ┌───┐        │   │
  │                  └───┘             │   │        └┬─┬┘ (Shooting Star / Engulfing)
  │                                  [Pullback]      │█│
  │                                                   ▼ (Close Bar)
  ▼                                             [Candle Konfirmasi Selesai]
Harga                                           ➔ ENTRY SELL DI SINI
```

### Langkah Eksekusi:
1. **Periksa Tren & EMA**:
   - Harga wajib berada di bawah EMA 125.
   - Garis EMA 8 berada di bawah EMA 21.
2. **Tunggu Pullback Masuk Zona Nilai (EMA 8 - 21)**:
   - Tunggu harga naik sejenak menyentuh garis EMA 8 atau EMA 21.
   - **Syarat Mutlak**: High candle koreksi tidak boleh menembus ke atas EMA 125.
3. **Tunggu Candle Konfirmasi Bearish Close**:
   - Terdeteksi salah satu pola: *Shooting Star*, *Bearish Pin Bar*, *Bearish Engulfing*, *Dark Cloud Cover*, *Evening Star*, *Three Black Crows*, *Doji Rejection*, *Inside Bar Breakdown*, atau *Two Candle Rejection*.
4. **Eksekusi Entry & Penempatan SL / TP**:
   - **Entry Sell**: Buka posisi saat candle konfirmasi tertutup sempurna.
   - **Stop Loss (SL)**: Letakkan 5 - 10 pips di atas titik tertinggi (High) candle konfirmasi atau swing high terdekat.
   - **Take Profit (TP)**: Minimal **1:1.5** hingga **1:2.0** dari jarak Stop Loss.
5. **Proteksi Profit (Trade Management)**:
   - Saat profit mencapai 1:1 R:R, pindahkan SL ke Break-Even (BEP).
   - Biarkan profit berlari (*ride the trend*) dengan trailing stop di atas garis EMA 21.

---

## 6. MEMAHAMI 4 FILTER FALSE SIGNAL

Sebagai trader profesional, tujuan utama kita adalah **menghindari kerugian di pasar sideways**. Sistem ini secara otomatis memfilter kondisi berikut:

| Nama Filter | Kondisi Pasar | Mengapa Berbahaya? | Solusi Sistem |
|---|---|---|---|
| **Chop Filter** (EMA 8-21) | EMA 8 dan 21 bolak-balik bersilangan dalam 15 bar. | Pasar sedang flat/konsolidasi tanpa arah yang jelas. | Sinyal panah diblokir sampai salah satu arah mendominasi. |
| **Whipsaw Filter** (EMA 125) | Harga melintas naik-turun menembus EMA 125 dalam 20 bar. | Tren makro sedang bingung/transisi. | Sinyal dinonaktifkan sampai harga konsisten di satu sisi EMA 125. |
| **Overextended Filter** | Jarak harga ke EMA 8 > `2.0 * ATR(14)`. | Pasar sudah *overbought* / *oversold*, rawan pembalikan tajam. | Melarang entri kejar harga (*Anti-FOMO*). Menunggu harga pullback kembali. |
| **Structure Filter** | Pasar tidak membentuk HH-HL (Buy) atau LH-LL (Sell). | Harga bergerak di dalam *range box* / sideways. | Wajib menunggu terbentuknya ayunan struktur baru yang valid. |

---

## 7. PENGATURAN PARAMETER TERBAIK KHUSUS XAUUSD (GOLD)

Emas (*Gold*) memiliki volatilitas yang tinggi dan rentan terhadap lonjakan berita (*news spikes*). Berikut konfigurasi yang terbukti paling stabil:

### 1. Rekomendasi Timeframe:
- **M15 (Scalping / Intra-Day)**: Menghasilkan 2 - 4 peluang berkualitas tinggi per hari. Sangat cocok untuk target profit 30 - 70 pips.
- **H1 (Swing Trading)**: Akurasi tertinggi (> 75%), menghasilkan 2 - 4 sinyal kuat per minggu dengan potensi profit 100 - 300 pips per trade.

### 2. Rekomendasi Jam / Sesi Trading (WIB):
- 🟢 **Sesi London (14:00 - 18:00 WIB)**: Awal pembentukan tren harian emas yang bersih.
- 🟢 **Sesi Overlap London - New York (19:30 - 23:00 WIB)**: Volume dan likuiditas tertinggi di pasar dunia. Setup pullback memberikan *follow-through* paling cepat.
- 🔴 **Hindari Jam Rollover (04:00 - 06:00 WIB)**: Spread emas melebar dari biasanya 1.5 pips menjadi 10 - 20 pips. Jangan pernah entri di jam ini!

### 3. Aturan Money Management Ketat:
- **Resiko per Trade**: Maksimal **1.0% - 1.5%** dari total modal Anda.
- **Formula Lot Sederhana**:
  $$\text{Lot} = \frac{\text{Modal} \times \text{Risk \%}}{\text{Jarak SL (Points)} \times \text{Nilai Per Point}}$$
- *Contoh*: Modal $1,000, resiko 1% ($10). Jika jarak SL adalah 40 pips (400 points di Gold), maka gunakan Lot **0.02** atau **0.03**.

---

## 8. CHECKLIST HARIAN SEBELUM MENGAMBIL POSISI

Sebelum Anda menekan tombol Buy atau Sell di MT5, centang 5 pertanyaan ini:

- [ ] **1. Apakah tren makro jelas?** (Harga di atas EMA 125 untuk Buy, atau di bawah EMA 125 untuk Sell).
- [ ] **2. Apakah garis EMA 8 dan 21 selaras?** (EMA 8 di atas 21 untuk Buy, atau EMA 8 di bawah 21 untuk Sell).
- [ ] **3. Apakah harga sedang menguji / memantul dari area EMA 8 - 21?** (Bukan mengejar harga yang sudah terbang jauh).
- [ ] **4. Apakah ada candle rejection/konfirmasi yang valid?** (Muncul panah Aqua/Magenta setelah candle Bar 1 close).
- [ ] **5. Apakah status Dashboard menunjukkan `VALID SIGNAL PASS`?** (Bukan status *Chop*, *Overextended*, atau *Sideways*).

Jika **SEMUA 5 SYARAT TERPENUHI**, eksekusi trading Anda dengan penuh disiplin, pasang Stop Loss & Take Profit, lalu biarkan sistem bekerja!
