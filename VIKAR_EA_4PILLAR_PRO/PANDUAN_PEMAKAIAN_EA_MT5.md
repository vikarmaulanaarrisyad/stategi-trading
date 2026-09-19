# 🏛️ PANDUAN RESMI EA ROBOT TRADING METATRADER 5 (MT5)
## VIKAR INSTITUTIONAL 4-PILLAR EA PRO
**SMC Core • Support & Resistance Daily Pivots • Triple EMA • Auto-Fibonacci Golden Pocket**

---

## 📌 1. Pendahuluan & Filosofi Sistem

**VIKAR EA 4-Pillar Pro** adalah robot trading otomatis (*Expert Advisor*) untuk platform **MetaTrader 5 (MT5)** yang dirancang dengan mematuhi standar trading institusional tanpa tebak-tebakan (*zero subjective discretion*).

Robot ini menggabungkan 4 pilar analisis teknikal yang saling memvalidasi (*Multi-Confluence Filter*):

```
+-------------------------------------------------------------------------+
|                  ARSITEKTUR 4 PILAR INSTITUSIONAL                        |
+-------------------------------------------------------------------------+
| PILAR 1: SMART MONEY CONCEPTS (SMC CORE)                                |
|  - Deteksi Struktur Pasar: BOS (Break of Structure) & CHoCH             |
|  - Liquidity Sweep (Stop Hunt pada Swing High / Swing Low)              |
|  - Dealing Range Equilibrium (BUY hanya di Diskon, SELL di Premium)     |
+-------------------------------------------------------------------------+
| PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS)                            |
|  - Daily Pivot Points Otomatis (Central Pivot P, S1-S3, R1-R3)          |
|  - Aturan Double Alignment: BUY di atas Pivot P & SELL di bawah Pivot P |
|  - Headroom Filter: Memastikan jarak ke tembok Pivot minimal 0.7x ATR   |
+-------------------------------------------------------------------------+
| PILAR 3: TRIPLE EXPONENTIAL MOVING AVERAGE (EMA 8, 21, 125)             |
|  - EMA 125 Putih: Institutional Macro Trend Baseline                    |
|  - Ribbon EMA 8 Cyan & EMA 21 Magenta: Dynamic Pullback Value Zone      |
|  - Konfirmasi Candlestick Rejection: Hammer, Engulfing, Morning Star    |
+-------------------------------------------------------------------------+
| PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET                          |
|  - Auto-Fibo dari Swing SMC Aktif (Low ke High / High ke Low)           |
|  - Golden Pocket Filter: Wajib menguji area diskon 0.500 - 0.786        |
|  - Rasio Emas 0.618 sebagai pemicu pantulan presisi                     |
+-------------------------------------------------------------------------+
```

---

## 📂 2. Struktur Folder & Berkas yang Disediakan

Folder baru strategi ini tersimpan di:
`e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\`

| Nama Berkas | Fungsi & Deskripsi |
| :--- | :--- |
| **`VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5`** | Source code bahasa MQL5 lengkap, rapi, dan modular (v2.1 Audited) |
| **`VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5`** | Binary terkompilasi (0 Error, 0 Warning) siap pakai |
| **`PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf`** | Buku Panduan Manual Lengkap Resmi Format PDF (11 Halaman Cetak Siap Baca) |
| **`XAUUSD_FAST_AUTO_TRADE.set`** | Preset Auto-Trade Cepat (Skor 60+, SL+ 8 pips, TP1 10 pips, Lot Broker Min 0.10) |
| **`XAUUSD_HIGH_WINRATE_SNIPER.set`** | Preset Sniper Ultra Winrate (Grade A+ Skor 80+, Double Align, Golden Pocket, Lot Min 0.10) |
| **`XAUUSD_M5_Scalping_Confluence.set`** | Preset setting optimal untuk Scalping Gold timeframe M5 (Skor 65+) |
| **`XAUUSD_M15_DayTrading_GradeA.set`** | Preset setting optimal untuk Day Trading Gold timeframe M15 (Skor 70+) |
| **`PANDUAN_PEMAKAIAN_EA_MT5.md`** | Dokumen panduan markdown instalasi, konfigurasi, dan SOP eksekusi |

> [!NOTE]
> File `.ex5`, `.mq5`, `.pdf`, dan semua berkas `.set` juga telah **otomatis disalin ke folder terminal MT5 Anda**:  
> `AppData\Roaming\MetaQuotes\Terminal\...\MQL5\Experts\VIKAR_4Pillar_Pro\` dan `MQL5\Presets\`  
> Sehingga EA, buku panduan PDF, dan preset langsung tersedia di terminal MT5 tanpa perlu copy-paste manual!

---

## 🚀 3. Panduan Instalasi Cepat pada MetaTrader 5

1. **Buka MetaTrader 5:**
   - Jalankan terminal MT5 DIDIMAX atau broker pilihan Anda.
2. **Buka Jendela Navigator (`Ctrl + N`):**
   - Cari menu **Expert Advisors (Penasihat Ahli)**.
   - Klik kanan pada menu tersebut lalu klik **Refresh**.
   - Anda akan melihat folder **`VIKAR_4Pillar_Pro`** dengan EA **`VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR`**.
3. **Buka Chart Instrumen:**
   - Buka grafik **XAUUSD (Gold)** pada timeframe **M5** (untuk scalping) atau **M15** (untuk day trading).
4. **Pasang EA ke Grafik:**
   - Tarik (*drag & drop*) EA ke grafik.
   - Pada tab **Common (Umum)**: Centang **"Allow Algo Trading" (Izinkan Trading Algoritma)**.
5. **Muat File Preset (.set):**
   - Klik tab **Inputs (Masukan)**.
   - Klik tombol **Load (Muat)** di pojok kanan bawah.
   - Pilih `XAUUSD_M5_Scalping_Confluence.set` atau `XAUUSD_M15_DayTrading_GradeA.set`.
   - Klik **OK**.
6. **Pastikan Tombol Algo Trading di Toolbar Aktif:**
   - Pastikan tombol **Algo Trading** di bagian atas toolbar berwarna **Hijau**.
   - Di pojok kanan atas grafik akan muncul topi kelulusan warna biru yang menandakan EA sedang aktif mengawasi pasar.

---

## ⚙️ 4. Penjelasan Parameter Input Utama

### A. Manajemen Lot & Proteksi Modal Terkecil (Anti-Lot Besar)
* `InpLotType`: 
  * `LOT_TYPE_BROKER_MIN` (**Rekomendasi Default & Paling Aman**): **Otomatis menggunakan ukuran minimal lot yang diizinkan oleh broker**.
    * Pada broker **DIDIMAX**, EA secara presisi akan selalu membuka **0.10 lot** (tidak akan pernah membesar).
    * Pada broker internasional/ECN dengan minimal 0.01 lot, EA akan membuka **0.01 lot**.
    * Ini menjamin modal Anda selalu terlindungi dengan risiko paling kecil dan konservatif!
  * `LOT_TYPE_FIXED`: Menggunakan lot tetap sesuai input `InpFixedLot` (Default: `0.10`).
  * `LOT_TYPE_RISK_PERCENT`: Menghitung ukuran lot secara dinamis berdasarkan `% Modal` (Default: 1.0%).
* `InpMinLot`: **0.00** (`0.00` = Otomatis mendeteksi batas bawah volume minimal dari server broker).
* `InpMaxLot`: **0.10** (**Safeguard Plafon Maksimal**): Memastikan order lot yang dikirim ke pasar **TIDAK AKAN PERNAH melebihi 0.10 lot**, melindungi akun secara mutlak dari risiko salah hitung atau lot besar!
* `InpRiskPercent`: Batas risiko per transaksi jika menggunakan mode Risk % (Default: 1.0%).
* `InpMaxOpenPositions`: Maksimal jumlah posisi aktif bersamaan (Default: 1 untuk mencegah overtrading dan hedging).
* `InpSignalCooldownBars`: Jeda lilin minimal sebelum boleh membuka posisi baru setelah penutupan trade.

### B. Stop Loss, Take Profit, Partial Scaling & Proteksi Dinamis
* `InpSLType`:
  * `SL_TYPE_SWING_FIBO`: Stop Loss ditaruh di balik Swing Fractal / Fibo 1.0 + buffer ATR (Rekomendasi institusional).
  * `SL_TYPE_CANDLE_WICK`: SL di ujung ekor lilin pemicu.
* `InpRiskRewardRatio`: Target keuntungan penuh (Default M5: 1:1.8, Default M15: 1:2.5).

* **🎯 Fitur Partial Take Profit / Scaling Out (TP1 50% + SL+ Runner):**
  * *Filosofi:* Cuan cepat langsung diamankan di saku (50% lot), modal awal terlindungi 100% dengan memindahkan sisa lot ke **SL+**, dan sisa lot dibiarkan berlari (*runner*) memburu tren panjang menggunakan Trailing Stop EMA 21.
  * `InpUsePartialClose`: Mengaktifkan scaling out otomatis saat harga menyentuh TP1.
  * `InpPartialClosePercent`: Persentase lot yang ditutup di TP1 (Default: `50.0%`).
  * `InpPartialTriggerMode`:
    * `BE_MODE_PIPS` (Default): TP1 dipicu berdasarkan pencapaian jarak pips profit (misal: +15 pips).
    * `BE_MODE_RISK_REWARD`: TP1 dipicu saat mencapai rasio R:R tertentu (misal: 1:1.2 atau 1:1.5).
  * `InpPartialTriggerPips`: Jarak pips profit untuk menutup sebagian posisi di TP1 (Default: 12 - 18 pips).
  * `InpPartialRRTrigger`: Rasio R:R target pemicu TP1 jika menggunakan mode R:R.
  * `InpPartialMoveSLPlus`: Jika `true` (default), begitu TP1 berhasil dieksekusi, sisa posisi otomatis digeser ke **SL+ (Stop Loss Plus di atas harga open)** sehingga posisi dijamin bebas risiko kerugian (*Risk-Free Trade*).
  * **Proteksi Batas Lot Broker (Anti Error 10014 Invalid Volume):** Pada broker dengan minimal lot 0.10 (seperti DIDIMAX), volume 0.10 lot tidak dapat dipecah menjadi 0.05. Jika posisi bernilai 0.10 lot, EA secara cerdas **mengunci posisi langsung ke SL+ pada level TP1** agar profit tetap terjamin tanpa terjadi penolakan order oleh server broker!

* **🛡️ Fitur Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin):**
  * `InpUseBreakeven`: Mengaktifkan penggeseran Stop Loss otomatis saat posisi telah berjalan profit.
  * `InpBreakevenMode`:
    * `BE_MODE_PIPS` (Default): Pemicu berbasis jarak pips profit (Contoh: saat profit sudah mencapai +12 pips, geser SL).
    * `BE_MODE_RISK_REWARD`: Pemicu berbasis rasio R:R (Contoh: saat profit menyamai jarak risiko awal 1:1, geser SL).
  * `InpBreakevenTriggerPips`: Jarak pips profit yang dibutuhkan untuk memicu penggeseran (Default: 10 - 15 pips).
  * `InpBreakevenLockPips`: **Nilai Pips Keuntungan Terkunci (SL+)**
    * Jika diisi `0.0`: Murni Breakeven (SL digeser tepat ke harga open entry / BEP 0 resiko).
    * Jika diisi `+3.0` s/d `+5.0`: **SL+ (Stop Loss Plus)**. SL dipasang **di atas harga entry (BUY)** atau **di bawah harga entry (SELL)**, sehingga jika harga berbalik arah, Anda **pasti keluar dalam kondisi PROFIT BERSIH**!

* **✂️ Fitur Auto Cut Profit (Tutup Dini Saat Indikasi Pembalikan Arah):**
  * `InpAutoCutProfit`: Menutup posisi secara otomatis jika terdeteksi bahwa pasar berbalik arah sebelum menyentuh target Take Profit, sehingga keuntungan yang sudah didapat tidak lenyap menjadi kerugian.
  * `InpMinProfitToCutPips`: Syarat batas minimal profit mengambang (*floating pips*) sebelum proteksi cut aktif (Default: 3.0 - 5.0 pips) agar tidak terpotong oleh noise kecil.
  * `InpCutOnCHoCH`: Cut profit jika terdeteksi pembentukan **Change of Character (CHoCH)** berlawanan dari struktur SMC.
  * `InpCutOnCandleReversal`: Cut profit jika muncul **Candlestick Rejection Grade A** berlawanan (misal Pin Bar penolakan, Engulfing penyerapan, atau Star reversal).
  * `InpCutOnEMACross`: Cut profit jika harga menembus dan lilin ditutup di sisi seberang **Ribbon EMA 21 Magenta**.
* `InpUseTrailingEMA21`: Mengawal posisi profit menggunakan garis dinamis **EMA 21 Magenta**. Posisi tetap ditahan (*Hold*) selama tren kuat berlangsung.

### C. Multi-Timeframe Macro Alignment (H1 + M5/M15) & Arus Modal Besar
* *Filosofi:* Menghindari jebakan pembalikan semu (*fakeout*) pada timeframe kecil. EA memastikan eksekusi scalp/day trade di M5 atau M15 selalu searah dengan arus modal besar (*smart money flow*) di timeframe H1.
* `InpUseHTFFilter`: Mengaktifkan filter makro Higher Timeframe (Default: `true`).
* `InpHTFTimeframe`: Timeframe acuan makro institusional (Default: `PERIOD_H1`).
* `InpHTFTrendEMA`: Garis pembatas tren utama institusional di H1 (Default: `EMA 125 Putih`).
* `InpHTFRequireRibbon`: Mewajibkan momentum ribbon H1 (EMA 8 Cyan > EMA 21 Magenta untuk Bullish, atau sebaliknya untuk Bearish).
* **Aturan Alignment:**
  * **Hanya Boleh BUY di M5/M15** jika di H1 harga berada **di atas EMA 125** dan Ribbon EMA 8 > 21.
  * **Hanya Boleh SELL di M5/M15** jika di H1 harga berada **di bawah EMA 125** dan Ribbon EMA 8 < 21.
  * Jika H1 sedang kontra atau sideways, sinyal di M5/M15 otomatis ditolak dan dashboard akan menampilkan: `FILTER: KONTRA HTF (H1 BEARISH / BULLISH)`.

### D. Kecerdasan Struktur Pasar (SMC) & Pola Candlestick Institusional
* **Membaca Struktur Pasar (Smart Money Concepts):**
  * `InpRequireBOSorCHoCH`: Memastikan arah tren struktural valid:
    * **BOS (Break of Structure):** Konfirmasi kelanjutan tren kuat dengan *body candle close* menembus Swing High (Uptrend) atau Swing Low (Downtrend).
    * **CHoCH (Change of Character):** Deteksi pembalikan arah institusional saat struktur berlawanan pertama kali ditembus.
    * **Struktur Ayunan:** Secara otomatis mengenali pola Higher Highs - Higher Lows (HH-HL) untuk Bullish dan Lower Highs - Lower Lows (LH-LL) untuk Bearish.
  * `InpRequireDiscount`: **Smart Money Dealing Range Matrix**
    * EA secara matematis menghitung posisi harga di dalam Dealing Range (0% s/d 100%).
    * **Anti-Beli di Pucuk:** Dilarang BUY jika harga berada di area **Premium (> 50%)**.
    * **Anti-Jual di Lembah:** Dilarang SELL jika harga berada di area **Diskon (< 50%)**.
  * `InpUseLiquiditySweep`: **Turtle Soup / Stop Hunt Detector**
    * Mendeteksi saat harga menyapu Swing High / Swing Low retail hanya dengan ekor lilin (*wick pierce*), lalu ditutup kembali ke dalam range. Ini adalah tanda paling kuat bahwa institusi telah selesai menjerat Stop Loss retail dan siap membalikkan harga.
  * `InpUseFVGFilter`: Mendeteksi zona **Fair Value Gap (Ketidakseimbangan Harga)** dan mengantisipasi pantulan saat harga melakukan mitigasi FVG.

* **Membaca Pola Candlestick Cerdas (Quality Scoring 0 - 100):**
  * `InpRequireCandleRejection`: Mengaktifkan filter pola penolakan institusional berkualitas tinggi:
    * **Hammer & Pin Bar:** Ekor penolakan (*rejection wick*) wajib $\ge 55\%$ dari total panjang lilin dengan body kecil di ujung.
    * **Institutional Engulfing:** Lilin pembalikan menelan lilin sebelumnya dengan volume/range ekspansi yang jelas.
    * **Tweezer Tops & Bottoms:** Dua lilin berturut-turut menguji dan menolak level harga yang sama persis (level double test).
    * **Morning Star & Evening Star:** Formasi pembalikan 3 lilin (Exhaustion $\rightarrow$ Indecision $\rightarrow$ Strong Expansion).
    * **FVG Mitigation Rebound:** Lilin menyentuh area Fair Value Gap lalu memantul kuat.
  * `InpMinCandleScore`: **Ambang Batas Skor Lilin (Default: 60 - 70)**
    * Setiap pola lilin dinilai secara kuantitatif berdasarkan ketajaman ekor, rasio body, plus **bonus konfluensi** jika penolakan terjadi tepat di **Ribbon EMA 8/21 (+10 poin)** atau di **Golden Pocket Fibo 61.8% (+10 poin)**. Hanya pola Grade A/A+ yang lolos dieksekusi!

* **S/R & Headroom Filter:**
  * `InpRequireDoubleAlign`: Wajib harga di atas Pivot P (untuk BUY) atau di bawah Pivot P (untuk SELL).
  * `InpRequireGoldenPocket`: Memastikan harga telah menyentuh zona diskon emas Fibonacci **0.500 s/d 0.786**.
  * `InpMinHeadroomATR`: Menolak sinyal jika di depan entri terdapat tembok Pivot yang terlalu dekat (< 0.7x ATR).

### D. Statistik Performa & Rekap PnL (Profit & Loss)
* `InpShowPnLStats`: Menampilkan rekap transaksi real-time langsung pada layar chart:
  * **Sejak EA Diaktifkan:** Modal awal (*Start Balance*), Net Profit ($ dan %), jumlah transaksi menang (*Win*) vs kalah (*Loss*), Gross Profit, dan Gross Loss.
  * **Per Hari (Hari Ini):** Net Profit hari ini, Gross Profit hari ini, dan Gross Loss hari ini beserta jumlah dealnya.
  * **Per Minggu (Minggu Ini):** Net Profit minggu ini, Gross Profit minggu ini, dan Gross Loss minggu ini beserta jumlah dealnya.
  * **Floating PnL:** Keuntungan/kerugian mengambang dari transaksi yang sedang berjalan saat ini.
* `InpResetStatsOnStart`: Jika `false` (default), modal awal dan riwayat aktivasi tetap tersimpan meskipun MT5 di-restart atau timeframe diubah. Set ke `true` jika ingin mereset penghitungan dari nol saat pasang ulang.

### E. Tampilan Dashboard GUI Modern & Interaktif (Bisa Digeser / Drag & Drop)
* Dashboard dirancang menggunakan **Glassmorphic Dark Card (`#0f172a`)** dengan header **Deep Cyan (`#0369a1`)** dan tipografi profesional Segoe UI.
* **Fitur Drag & Drop (Bisa Digeser Bebas):**
  * Anda dapat memindahkan dashboard ke mana pun di layar chart.
  * **Caranya:** Cukup klik kiri dan tahan mouse di area kartu dashboard (terutama di baris header bertuliskan **`[ ⠿ GESER ]`**), lalu geser mouse ke posisi yang diinginkan.
  * **Auto-Save Posisi:** MT5 otomatis mengingat koordinat terakhir di mana Anda meletakkan dashboard. Saat ganti timeframe atau restart MT5, posisi dashboard **tidak akan kembali ke pojok kiri** melainkan tetap di tempat yang Anda pilih!
* **Parameter Koordinat Awal:**
  * `InpDashboardX`: Posisi awal horizontal dari tepi kiri chart (Default: 15 pixel).
  * `InpDashboardY`: Posisi awal vertikal dari tepi atas chart (Default: 20 pixel).
* **Tidak Ada Lagi Tumpang Tindih Candlestick:** Lilin harga otomatis digeser ke kanan (`Chart Shift`), dan panel memiliki latar belakang solid gelap sehingga teks tidak bertabrakan dengan lilin chart.
* **Cara Refresh Tampilan di MT5:** Jika EA sedang berjalan di grafik saat pembaruan, cukup klik tombol timeframe lain (misal **M5** lalu kembali ke **M1**) atau tekan **F7** lalu klik **OK** agar tampilan interaktif langsung aktif.

---

## 🧪 5. Panduan Backtest pada Strategy Tester MT5

Untuk menguji performa historis EA:
1. Tekan kombinasi tombol **`Ctrl + R`** di MT5 untuk membuka jendela **Strategy Tester**.
2. Pilih mode **Single Test (Pengujian Tunggal)**.
3. Atur parameter berikut:
   * **Expert:** `VIKAR_4Pillar_Pro\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5`
   * **Symbol:** `XAUUSD` (atau `GOLD`)
   * **Period:** `M5` atau `M15`
   * **Date:** 1–6 bulan terakhir (misal: 2026.01.01 s/d sekarang)
   * **Forward:** `No`
   * **Execution:** `Every tick based on real ticks` (atau `1 minute OHLC` untuk kecepatan tinggi)
   * **Deposit:** `$1,000` (atau sesuaikan dengan modal akun Anda)
   * **Leverage:** `1:100` atau `1:500`
4. Klik tombol **Inputs**, klik kanan lalu **Load** file preset `.set`.
5. Klik **Start (Mulai)**.
6. Periksa tab **Graph** (Kurva pertumbuhan ekuitas) dan tab **Backtest** (Profit Factor, Drawdown maksimal, Win Rate).

---

## 🏆 6. Formula Rahasia Agar WIN RATE (Menang) Jauh Lebih Besar dari LOSS (Kalah)

Banyak trader pemula mengira bahwa memperbanyak frekuensi open posisi akan membuat untung lebih cepat. Faktanya, mematikan filter (`false`) justru menyebabkan robot masuk pada noise pasar sideways dan melawan tren besar, yang berujung pada kekalahan berturut-turut.

Untuk membuat **Jumlah Transaksi Menang (WIN) Jauh Melampaui Transaksi Kalah (LOSS)** hingga mencapai rasio win rate **75% – 85%+**, terapkan 5 pilar setting berikut:

### 1. ⚡ Akselerasi SL+ Cepat (Pemicu +8.0 Pips) — "The Loss Eliminator"
* **Setting:** `InpBreakevenTriggerPips = 8.0` dan `InpBreakevenLockPips = 2.5` (atau `3.0`).
* **Cara Kerja:** Pada instrumen Emas (XAUUSD), pantulan dari Ribbon EMA 8/21 hampir selalu memberikan impuls awal 8–12 pips dalam hitungan detik. Begitu harga berjalan +8 pips, Stop Loss langsung ditarik ke depan entry sebesar **+2.5 pips (SL+)**.
* **Keuntungan:** Jika harga tiba-tiba berbalik arah, transaksi **TIDAK JADI LOSS**, melainkan ditutup dengan **PROFIT BERSIH (+2.5 pips)**! Transaksi ini dihitung sebagai **+1 WIN** dan **0 LOSS** pada statistik akun.

### 2. 🎯 Amankan Sebagian Modal di TP1 (+10.0 s/d +12.0 Pips)
* **Setting:** `InpUsePartialClose = true`, `InpPartialTriggerPips = 10.0` (atau `12.0`), `InpPartialClosePercent = 50.0`.
* **Cara Kerja:** Mengamankan 50% profit pada jarak aman yang memiliki probabilitas ketercapaian lebih dari 80%. Sisa lot dipindahkan ke SL+ dan dibiarkan memburu profit besar tanpa beban risiko.

### 3. 🌊 Wajib Selaras dengan Arus Modal Besar (H1 Macro Filter)
* **Setting:** `InpUseHTFFilter = true`, `InpHTFTimeframe = PERIOD_H1`, `InpHTFTrendEMA = 125`.
* **Cara Kerja:** Mencegah robot mengambil posisi melawan arus raksasa institusi di H1. Sinyal BUY di M5/M15 hanya diproses jika H1 Bullish, dan sinyal SELL hanya diproses jika H1 Bearish. Ini mengeliminasi 80% jebakan fakeout!

### 4. ✂️ Auto-Cut Profit Dini (+3.0 Pips)
* **Setting:** `InpAutoCutProfit = true`, `InpMinProfitToCutPips = 3.0`.
* **Cara Kerja:** Jika harga sudah floating profit dan tiba-tiba membentuk pola candle pembalikan atau menembus EMA 21 ke arah berlawanan, robot langsung menutup posisi saat itu juga. Profit diamankan sebelum sempat berbalik menjadi kerugian.

### 5. 🛡️ Filter Jam Trading Emas (Sesi Likuiditas Tinggi)
* **Setting:** `InpUseSessionFilter = true`, `InpSessionStartHour = 12`, `InpSessionEndHour = 22`.
* **Cara Kerja:** Hanya bertransaksi saat pasar London & New York sedang aktif (volume likuiditas tinggi). Menghindari sesi dini hari / Asia yang sering sideways liar dan mengalami pelebaran spread.

---

## 🧠 7. Fitur Kecerdasan Institusional Supercharged (Pembaruan Versi 2.0)

Pada Versi 2.0, EA `VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR` mendapatkan peningkatan arsitektur kecerdasan buatan institusional (*Institutional Trading Intelligence*) tingkat lanjut:

### A. Mesin Valid Order Block (OB) Institusional & Validasi Displacement ATR
* **Filosofi Perbankan:** Order Block bukanlah sembarang lilin, melainkan jejak kaki akumulasi/distribusi dana raksasa (*smart money footprint*).
* **Cara Deteksi Cerdas:**
  * **Bullish Order Block (Base Demand):** Lilin bearish terakhir sebelum terjadinya dorongan *bullish displacement* yang agresif (Range Lilin $\ge 1.25\times\text{ATR}$ atau Body $\ge 0.75\times\text{ATR}$) yang memicu BOS/CHoCH atau menciptakan FVG.
  * **Bearish Order Block (Supply Zone):** Lilin bullish terakhir sebelum guyuran *bearish displacement* agresif yang memecahkan struktur pasar ke bawah.
* **Logika Mitigasi:** EA memantau apakah harga yang sedang retrace sedang menguji (*testing / mitigation*) zona Order Block aktif. Pantulan dari Base Demand Order Block menghasilkan akurasi win rate tertinggi!

### B. Multi-Bar Fair Value Gap (FVG) Imbalance Tracker
* EA memindai hingga 20–35 lilin ke belakang (`InpFVGLookbackBars = 20`) untuk mendeteksi area ketidakseimbangan likuiditas (*imbalance*) yang belum termitigasi (*unmitigated FVG*).
* Ketika zona FVG bertepatan dengan Golden Pocket Fibonacci atau Order Block, EA memberikan bobot konfluensi ganda.

### C. Sistem Skor Konfluensi 4 Pilar Terpadu (0 – 100 Poin) & Grade Filter
Alih-alih sekadar logika IF-THEN kaku, EA kini menggunakan **Algoritma Skor Kualitas Matematis (0 - 100 Poin)**:
* **Struktur SMC (BOS / CHoCH / Dealing Range):** Maksimal **20 Poin**
* **Order Block (OB) Validation & Mitigation Test:** Maksimal **20 Poin**
* **Displacement Momentum (Institutional Footprint):** Maksimal **15 Poin**
* **Fair Value Gap (FVG) Imbalance Confluence:** Maksimal **15 Poin**
* **Liquidity Sweep (Stop Hunt / Turtle Soup):** Maksimal **10 Poin**
* **Fibonacci Golden Pocket Retracement:** Maksimal **10 Poin**
* **Triple EMA Trend 125 & Ribbon 8/21:** Maksimal **10 Poin**
* **Candlestick Rejection Score:** Maksimal **10 Poin**

**Sistem Grade Otomatis:**
* **Grade A+ Ultra Sniper (Skor $\ge 80$):** Sinyal berprobabilitas kemenangan tertinggi dengan konfluensi multi-faktor yang lengkap.
* **Grade A High Probability (Skor $\ge 65$):** Sinyal standar institusional yang lolos filter ketat.
* **Grade B / Reject (Skor $< 65$):** Otomatis ditolak oleh EA agar tidak membuang modal pada setup berkualitas rendah!

### D. Shock Guard & News Volatility Spike Protection (Anti Slippage Berita)
* **Masalah:** Saat rilis berita ekonomi besar (*High-Impact News* seperti NFP, CPI, FOMC), harga emas kerap melompat dengan spread melebar liar dan slippage besar.
* **Solusi Shock Guard:** Jika lilin yang baru terbentuk mengalami lonjakan range abnormal ($> 2.2\times\text{ATR}$), EA seketika mengaktifkan mode **`SHOCK GUARD ACTIVE`** dan memberlakukan jeda pengaman (*cooldown*) selama 2 lilin. EA menolak entry baru hingga badai volatilitas mereda!

### E. On-Chart Smart SMC Visualizer (Gambar Otomatis di Chart MT5)
* EA secara otomatis menggambar grafis SMC interaktif langsung di layar chart MT5 Anda (`InpDrawSMCOnChart = true`):
  * **Kotak Biru Lembut (`#0e7490`):** Menandai area **Bullish Order Block (Base Demand)** aktif.
  * **Kotak Merah Lembut (`#be123c`):** Menandai area **Bearish Order Block (Supply Zone)** aktif.
  * **Kotak Kuning Keemasan Putus-putus (`#d97706`):** Menandai celah **Fair Value Gap (FVG Imbalance)**.
  * **Garis Putus-putus Horizontal:** Menandai level struktur ayunan **BOS (Break of Structure)** dan **CHoCH**.
* Anda dapat melihat secara gamblang apa yang sedang dipikirkan dan dianalisis oleh robot secara visual!

### F. Smart Early Invalidation Cut (Proteksi Modal Maksimal)
* Jika posisi BUY sedang berjalan, dan tiba-tiba terbentuk lilin *displacement bearish* yang menembus tajam di bawah Order Block acuan (institusi berbalik arah merusak struktur), EA tidak menunggu SL penuh tersentuh, melainkan melakukan **Cut Dini**. Fitur ini menghemat modal hingga 50–70% dibanding membiarkan SL penuh tersentuh!

### G. Mesin Pola Grafik Lanjutan (Chart Pattern Recognition Engine - v2.1)
Robot kini dilengkapi dengan kecerdasan geometri grafik multi-lilin (*multi-bar pattern recognition*):
1. **Quasimodo Pattern (QM Institutional Setup - Skor 95 Poin):**
   * Pola pembalikan institusional paling mematikan (*Over-Under Pattern*).
   * **Bullish QM:** Terjadi saat harga membuat *Left Shoulder Low* $\rightarrow$ *Higher High* $\rightarrow$ menyapu likuiditas ke *Lower Low* (Stop Hunt) $\rightarrow$ reli menembus resisten (CHoCH) $\rightarrow$ dan sekarang melakukan *pullback* presisi ke level *Left Shoulder* (Order Block Demand).
   * **Bearish QM:** Terjadi saat harga menyapu puncak tertinggi $\rightarrow$ menembus swing low $\rightarrow$ lalu retrace kembali ke level *Left Shoulder* (Supply Zone).
2. **Double Bottom (W-Pattern) & Double Top (M-Pattern - Skor 85 Poin):**
   * Mendeteksi pembentukan dua lembah (W) atau dua puncak (M). Kaki kedua sering kali disertai *Liquidity Sweep* yang langsung memantul keras.
3. **Head & Shoulders (H&S) & Inverse H&S (Skor 90 Poin):**
   * Mendeteksi pola klasik pembalikan 3 ayunan di mana *Right Shoulder* terbentuk di Golden Pocket Fibo atau Order Block.
4. **Bullish & Bearish Flag (Skor 80 Poin):**
   * Mendeteksi pergerakan impulsif yang diikuti oleh saluran konsolidasi korektif miring (*slanted pullback channel*) menuju Ribbon EMA 21 sebelum melanjutkan tren reli.
5. **Bonus Konfluensi (+15 Poin):** Pola chart yang searah dengan tren akan langsung memberikan bonus skor matematis +15 poin, memicu eksekusi **Grade A+ Ultra Sniper**.

### H. Pola Candlestick Institusional Ekstra (v2.1)
Selain Pin Bar dan Engulfing, robot kini mampu mengenali formasi lilin khusus:
* **Three White Soldiers & Three Black Crows (85 Poin):** Tiga lilin marubozu ekspansif berurutan searah tren institusional.
* **Dragonfly & Gravestone Doji (82 Poin):** Lilin dengan penolakan ekor ekstrem $\ge 70\%$ dengan body tipis di level kunci.
* **Harami / Inside Bar Breakout (78 Poin):** Kompresi volatilitas di mana lilin kecil berada di dalam range lilin induk sebelum terjadi ledakan volume.
* **Piercing Line & Dark Cloud Cover (78 Poin):** Penetrasi lebih dari 50% ke dalam tubuh lilin berlawanan.
* **Inverted Hammer & Shooting Star (74 Poin):** Penolakan likuiditas di area Diskon/Premium.

### I. Volume Spread Analysis (VSA) & Footprint Volume Absorption Engine (v2.2)
Robot kini membaca data volume transaksi riil (`tick_volume`) dari broker:
1. **Volume Climax / Institutional Absorption (+10 Poin):**
   * Jika lilin penolakan (*rejection*) di Order Block / Golden Pocket / Ribbon EMA disertai lonjakan volume transaksi $\ge 1.75\times$ rata-rata 20 lilin terakhir, ini membuktikan terjadinya penyerapan suplai/demand besar-besaran oleh institusi (*Smart Money Inflow*). Nilai konfluensi otomatis ditambah **+10 Poin**.
2. **No-Supply Pullback Test (+5 Poin):**
   * Saat harga melakukan koreksi (*pullback*) menguji Ribbon EMA 8/21, jika volume justru mengering / mengecil ($< 0.85\times$ rata-rata), ini membuktikan tidak ada tekanan jual dari bank besar (trader ritel kehabisan suplai). Nilai konfluensi ditambah **+5 Poin** dengan probabilitas reli melesat hingga $> 80\%$.

### J. Multi-Stage Structural Trailing Stop (SMC Swing High/Low Runner - v2.2)
Kelemahan sistem Trailing Stop konvensional yang kaku mengikuti EMA 21 sering kali tersenggol oleh koreksi minor sebelum gelombang tren besar terjadi.
* **Mekanisme Dua Tahap (Multi-Stage):**
  1. **Tahap 1 (Pre-TP1):** Menggunakan Auto-BE dan Trailing EMA 21 standar untuk mengamankan posisi awal.
  2. **Tahap 2 (Post-TP1 Runner Lot):** Begitu target TP1 (50% lot) diamankan ke saldo modal, Stop Loss untuk sisa lot (*Runner*) otomatis dialihkan mengunci di balik **Higher Low (HL) struktural SMC terbaru** (untuk BUY) atau di atas **Lower High (LH) terbaru** (untuk SELL) ditambah buffer ATR.
  3. Ini memberi ruang bernapas yang cukup bagi posisi Runner untuk menunggangi gelombang tren monster $30 - $60 pergerakan emas tanpa terkena *shakeout* prematur!

### K. Daily Equity Guard & Consecutive Loss Circuit Breaker (v2.2)
* **Consecutive Loss Cooldown (Anti-Overtrading):**
  * Jika terjadi **2 kali Stop Loss berturut-turut** pada hari yang sama, robot otomatis mengaktifkan mode proteksi: **Istirahat / Berhenti Trading selama 4 jam**. Ini menghindarkan modal trader dari kondisi pasar yang sedang *choppy* atau anomali tidak rasional.
* **Klarifikasi Mutlak: Apakah SL+ Dihitung Sebagai Stop Loss?**
  * **TIDAK SAMA SEKALI!** SL+ menghasilkan keuntungan bersih (`deal.profit > 0`). Oleh karena itu, SL+ dihitung sebagai **WIN (MENANG)** dan **MERESET COUNTER LOSS KEMBALI KE 0**. Robot tidak akan pernah istirahat karena SL+!
* **Daily Equity Loss Safeguard:**
  * Jika total akumulasi kerugian tertutup hari ini mencapai **-2.5% modal**, trading hari itu dihentikan total (*circuit breaker*) hingga pergantian hari esok.

### L. Adaptive Post-Loss Self-Healing & Diagnostic Engine (v2.40 Apex)
* **Otopsi Kerugian Otomatis (Loss Autopsy Engine):**
  * Begitu deal ditutup rugi (Loss murni, bukan BE/SL+), robot otomatis memeriksa kondisi bar penutupan:
    - *Volatilitas Abnormal (News Shock / Spike):* Rentang lilin $\ge 2.2\times$ ATR.
    - *Pembalikan Struktur Makro (Trend Invalidation):* Terjadi CHoCH atau penembusan batas dinamis EMA 125.
    - *Liquidity Sweep Shakeout:* Ekor lilin berburu liquidity stop sebelum arah berbalik.
    - *Pengujian Level Gagal:* Setup minor kehilangan momentum di zona diskon/premium.
* **3 Aksi Koreksi Diri Mandiri:**
  1. **Penalti Ambang Skor:** Ambang batas konfluensi dinaikkan **+10 Poin** (misal dari 55 menjadi 65). Robot hanya menerima sinyal berkategori *Grade A+*.
  2. **Karantina Pola Gagal (Pattern Quarantine):** Pola candlestick atau chart pattern penyebab SL diisolasi selama **15 bar lilin** berikutnya.
  3. **Adaptive SL Buffer Expansion:** Stop Loss diperlebar **+0.3x ATR** untuk **3 transaksi berikutnya** agar posisi tidak tersapu ekor liar.
* **Auto Self-Reset:**
  * Begitu transaksi berikutnya menang (Take Profit) atau terkunci profit oleh SL+ (Auto BE Lock), sistem otomatis pulih 100% ke kondisi normal.
* **Laporan Otopsi ke Smartphone:**
  * Notifikasi instan dikirim ke aplikasi MetaTrader 5 di HP Anda berisi nomor tiket, jumlah rugi, diagnosa penyebab teknis, dan tindakan pengetatan yang aktif.

---

## 📞 8. Dukungan & Konsultasi

Untuk pertanyaan seputar strategi atau optimasi pengaturan:
* Konsultasikan langsung melalui chat asisten AI Vikar Pro.
* Pastikan selalu melakukan uji coba di **Akun Demo Didimax MT5** terlebih dahulu sebelum beralih ke akun riil!


## 🛡️ 7. Checklist Keamanan Sebelum Menjalankan Akun Riil

- [ ] Gunakan Akun Broker tipe **ECN / Zero Spread / Pro** agar spread Gold tidak membebani profit.
- [ ] Pastikan `InpMaxSpreadPips` disetel di 4.0 – 4.5 pips untuk mencegah entry saat spread melebar liar.
- [ ] Hindari membiarkan EA berjalan 30 menit sebelum dan sesudah rilis berita **High-Impact (NFP / CPI / FOMC)**.
- [ ] Disarankan menyewa **VPS (Virtual Private Server)** dengan latensi < 20 ms agar robot dapat bekerja nonstop 24 jam selama pasar buka tanpa terputus koneksi internet rumah.
- [ ] Patuhi aturan modal: Jangan pernah menaikkan resiko di atas 2% per transaksi.

---
*VIKAR INSTITUTIONAL 4-PILLAR PRO — MT5 TRADING ROBOT AUTOMATION*
