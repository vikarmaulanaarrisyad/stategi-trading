# Panduan Lengkap Cara Menjalankan Backtest EA Vikar 4-Pillar di MetaTrader 4 (MT4)

Panduan praktis ini dibuat khusus agar Anda dapat menguji performa historis robot trading **VIKAR EA 4-Pillar MT4** dengan konfigurasi **Take Profit 100 Point** dan **Dynamic Trailing Stop** di Strategy Tester MT4.

---

## 1. Persiapan Awal di MetaTrader 4

1. Buka aplikasi **MetaTrader 4 (QuickPro Edition)** di komputer Anda.
2. Pastikan data histori lilin (candlestick) XAUUSD / Gold sudah terunduh:
   - Tekan tombol **F2** di keyboard untuk membuka jendela **History Center**.
   - Cari dan klik ganda simbol **XAUUSD** (atau **GOLD**).
   - Klik timeframe **5 Minutes (M5)** lalu klik tombol **Download**.
   - Tunggu beberapa detik hingga proses unduh selesai, lalu klik **Close**.

---

## 2. Membuka Jendela Strategy Tester

1. Tekan tombol kombinasi **Ctrl + R** di keyboard Anda, atau klik menu **View** > **Strategy Tester**.
2. Jendela pengujian akan muncul di bagian bawah layar MetaTrader 4.

---

## 3. Pengaturan Kolom Strategy Tester

Isi kolom-kolom pada jendela Strategy Tester seperti berikut:

| Kolom | Pengaturan yang Dipilih | Keterangan |
| :--- | :--- | :--- |
| **Expert Advisor** | `VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4` | Pilih robot Vikar MT4 versi terbaru |
| **Symbol** | `XAUUSD` (atau `XAUUSD.i` / `GOLD`) | Simbol instrumen yang ingin diuji |
| **Model** | **Every tick (the most precise method)** | Menghasilkan akurasi trailing stop dan TP 100 point paling presisi |
| **Use date** | **Centang (Aktifkan)** | Tentukan tanggal awal dan akhir (misal 3 bulan atau 1 tahun terakhir) |
| **Visual mode** | *Opsional (Bebas)* | Centang jika ingin melihat grafik berjalan lambat; **Hilangkan centang** jika ingin proses backtest selesai cepat dalam hitungan detik/menit |
| **Period** | **M5 (5 Menit)** | Timeframe rekomendasi untuk scalping 100 point |
| **Spread** | `Current` atau `25` | Ketik spread realistis broker Anda (Gold biasanya 20 - 30 points) |

---

## 4. Memuat Preset Backtest TP 100 Point

Preset resmi yang sudah dioptimalkan telah disediakan dan otomatis tersimpan di folder Presets MT4 Anda:

1. Di sebelah kanan baris Expert Advisor pada Strategy Tester, klik tombol **Expert properties**.
2. Masuk ke tab **Inputs**.
3. Klik tombol **Load** di pojok kanan bawah.
4. Anda akan langsung melihat dua file preset resmi:
   - 📁 **`QUICKPRO_XAUUSD_BACKTEST_TP100_SCALPING.set`** *(Rekomendasi Utama)*:
     - Target TP: **100 Point** (10 Pips).
     - Trailing Points Aktif: Mulai profit $\ge$ 40 point, kawal jarak 30 point.
     - Candle Trailing Aktif: SL otomatis memanjat di bawah ekor Low lilin sebelumnya.
     - Auto-Breakeven: Mengunci modal di +20 point saat profit mencapai 50 point.
     - AI Loss Autopsy & Directional Learning Aktif.
   - 📁 **`QUICKPRO_XAUUSD_BACKTEST_TP100_GRADE_A_SNIPER.set`**:
     - Mode konservatif dengan filter konfluensi skor minimal **75 Poin** (hanya mengeksekusi setup terbaik berprobabilitas tertinggi).
5. Pilih salah satu preset di atas, lalu klik **Open**.
6. Klik **OK** untuk menutup jendela Expert properties.

---

## 5. Memulai dan Melihat Hasil Pengujian

1. Klik tombol **Start** berwarna hijau di pojok kanan bawah Strategy Tester.
2. Proses backtest akan berjalan:
   - Pantau bilah progres hijau hingga terisi penuh 100%.
3. Setelah selesai, buka tab-tab berikut di bagian bawah Strategy Tester:
   - 📈 **Graph**: Grafik kurva pertumbuhan saldo modal (*Equity & Balance Curve*).
   - 📊 **Report**: Laporan statistik lengkap meliputi:
     - *Total Net Profit* (Total Keuntungan Bersih)
     - *Profit Factor* (Rasio Keuntungan vs Kerugian)
     - *Max Drawdown* (Tingkat penurunan modal maksimal)
     - *Win Rate %* (Persentase kemenangan transaksi)
   - 📋 **Results**: Catatan setiap order BUY, SELL, SL+, Trailing Stop, dan TP 100 Point yang dieksekusi secara kronologis.

---

## 6. Tips Mengoptimalkan Hasil Backtest
- **Gunakan Spread Realistis**: Hindari memakai spread 0 atau terlalu kecil. Untuk XAUUSD, gunakan spread 20-30 points sesuai kondisi real broker QuickPro.
- **Kualitas Pemodelan (Modelling Quality)**: Untuk mendapatkan akurasi di atas 90%, unduh riwayat data M1 dan M5 yang bersih dari History Center.
- **Kecepatan Backtest**: Preset ini telah otomatis menonaktifkan gambar visual chart (`InpDrawSMCOnChart=0`) selama backtest untuk melipatgandakan kecepatan komputasi tanpa mengubah logika analisa trading.
