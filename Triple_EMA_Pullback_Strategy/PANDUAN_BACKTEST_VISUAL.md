# 📈 Panduan Lengkap Backtest Visual 1 Tahun di MetaTrader 5 (MT5)

Dokumen ini memandu Anda melakukan **Backtest Visual 1 Tahun** (chart mundur ke masa lalu lalu berjalan maju candle demi candle secara visual) menggunakan **Triple EMA Pullback EA** pada MetaTrader 5 (Didimax).

---

## 🚀 Langkah 1: Buka Strategy Tester di MT5

1. Buka aplikasi **MetaTrader 5**.
2. Tekan kombinasi tombol **`Ctrl + R`** pada keyboard (atau klik menu atas: **View** -> **Strategy Tester**).
3. Panel Strategy Tester akan muncul di bagian bawah layar MT5 Anda.

---

## ⚙️ Langkah 2: Atur Konfigurasi Pengujian (Tab Settings)

Di tab **Settings**, sesuaikan parameter berikut:

| Parameter | Nilai yang Dipilih | Keterangan |
| :--- | :--- | :--- |
| **Expert** | `Triple_EMA_Pullback_EA.ex5` | Pilih robot EA Triple EMA Pullback |
| **Symbol** | `XAUUSD.dmb` | Simbol Gold broker Didimax (atau simbol aktif Anda) |
| **Timeframe** | `M5` (atau `M15`) | Timeframe eksekusi pullback entry |
| **Period / Date** | `Custom period` | Atur rentang waktu 1 tahun ke belakang |
| **From / To** | `2025.09.01` s/d `2026.09.12` | Tanggal awal s/d tanggal hari ini |
| **Forward** | `No` | Tidak menggunakan forward testing |
| **Delays** | `Zero latency` | Agar proses simulasi berjalan cepat dan lancar |
| **Execution / Modeling** | `1 minute OHLC` *(Rekomendasi)* | **Sangat Cepat**: Menggunakan harga open/high/low/close bar 1 menit. Cocok untuk EA berbasis candle close |
| | *Atau: `Every tick based on real ticks`* | Jika ingin presisi tertinggi per tick spread real (membutuhkan waktu unduh data lebih lama) |
| **Deposit** | `10000 USD` (atau `1000 USD`) | Modal awal simulasi |
| **Leverage** | `1:100` (atau sesuai akun) | Daya ungkit akun |
| **Visual mode** | ☑️ **CENTANG KOTAK INI (Wajib)** | Mengaktifkan grafik visual yang mundur dan berjalan candle demi candle |

> [!TIP]
> **Template Visual Otomatis**: Kami telah mengonfigurasi berkas `tester.tpl` di folder profil MT5 Anda. Saat mode visual dimulai, chart akan otomatis memakai tema gelap premium lengkap dengan 3 garis EMA (8, 21, 125), area ribbon cloud, dan panel HUD!

---

## 📥 Langkah 3: Load Preset Pengujian (Tab Inputs)

Kami telah membuatkan berkas preset khusus: `Triple_EMA_XAUUSD_1Year_Backtest.set` yang sudah siap pakai:
1. Klik tab **Inputs** di Strategy Tester.
2. Klik kanan di area daftar input -> Pilih **Load**.
3. Pilih file **`Triple_EMA_XAUUSD_1Year_Backtest.set`** (tersedia di folder `Profiles/Tester/` atau di folder project ini).
4. Klik **Open**. Seluruh pengaturan (EMA, Sistem 3 Layar H1-M15-M5, Confluence Scoring 60+, Volume Filter SMA20, News Shock ATR, R:R 1:2, Partial Close 50% di 1:1R, dan Auto BEP) otomatis terisi secara optimal.

> [!TIP]
> **Sinkronisasi Otomatis**: Jika Anda memodifikasi kode strategi di VS Code / editor, cukup jalankan `deploy_to_mt5.bat` sekali klik untuk menyalin dan mengompilasi otomatis ke MetaTrader 5 Didimax Anda!

---

## 🎬 Langkah 4: Mulai Simulasi Visual (Playback Chart)

1. Klik tombol hijau **Start** di pojok kanan bawah tab Settings.
2. Jendela baru bernama **Visual Tester** akan otomatis terbuka.
3. Chart XAUUSD akan **otomatis mundur ke tanggal 1 tahun yang lalu** dan mulai berjalan maju candle demi candle secara visual.
4. **Fungsi Kontrol Playback (Di Bagian Atas Jendela Visual)**:
   - **Speed Slider (1 s/d 32)**:
     - Geser ke kiri (Speed 1 - 25) untuk memperlambat dan memperhatikan price action, pola candle, pullback EMA, dan pergeseran Trailing Stop.
     - Geser ke kanan (Speed 30 - 32) untuk mempercepat pergerakan chart hingga selesai 1 tahun dalam beberapa menit.
   - **Tombol Pause (atau tekan tombol Spasi)**: Menjeda grafik seketika saat ada open posisi Buy / Sell untuk menganalisis titik entry, SL, dan TP.
   - **Tombol Skip To**: Melompat langsung ke tanggal tertentu yang diinginkan.

---

## 📊 Langkah 5: Analisis Hasil Winrate, Profit, dan Drawdown

Setelah pengujian selesai (atau jika Anda klik tombol **Stop**):

### 1. Tab "Backtest" / "Report"
Lihat statistik performa komprehensif:
- **Win Rate (%)**: Dilihat pada baris **`Profit Trades (% of total)`** (Persentase transaksi yang profit dari total entri).
- **Loss Rate (%)**: Dilihat pada baris **`Loss Trades (% of total)`**.
- **Total Net Profit**: Total keuntungan bersih dalam USD (Profit kotor dikurangi kerugian kotor).
- **Profit Factor**: Perbandingan total untung dibagi total rugi (Sistem bagus jika Profit Factor > 1.80 - 2.50).
- **Max Equity Drawdown (%)**: Penurunan saldo terbesar selama 1 tahun (mengukur resiko akun).
- **Average Win vs Average Loss**: Mengukur efektivitas rasio Risk:Reward 1:2.0.

### 2. Tab "Graph"
Menampilkan grafik garis pertumbuhan modal (**Equity & Balance Curve**). Kurva yang sehat akan membentuk tren naik miring ke kanan atas yang konsisten.

### 3. Tab "Trades" / "Journal"
Menampilkan riwayat setiap transaksi yang dieksekusi:
- Waktu Open & Close.
- Jenis posisi (Buy / Sell).
- Lot size dan harga eksekusi.
- Catatan pola candle pemicu entri (misal `TripleEMA_XAU_Hammer`, `TripleEMA_XAU_Engulfing`).
- Poin profit / loss yang diraih.
