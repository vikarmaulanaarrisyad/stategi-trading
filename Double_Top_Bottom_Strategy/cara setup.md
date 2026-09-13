# 📈 Panduan Lengkap: Strategi Double Bottom ("W") & Double Top ("M")
## Reversal Chart Pattern System dengan Konfirmasi Breakout Volume Tinggi untuk MetaTrader 5

Sistem trading ini dirancang khusus untuk mendeteksi pola pembalikan arah harga (*major reversal pattern*) paling klasik dan handal di dunia teknikal: **Double Bottom (Pola "W")** dan **Double Top (Pola "M")** pada instrumen **XAUUSD (Emas)** serta pasangan Forex utama.

---

## 📚 1. Konsep Dasar Strategi Double Bottom & Double Top

Pola Double Top dan Double Bottom terbentuk dari pergulatan kekuatan antara *Buyers* dan *Sellers* pada level psikologis pasar:

### A. Double Bottom (Pola "W" - Bullish Reversal)
- **Kondisi Awal:** Terbentuk setelah tren turun (*downtrend*) yang signifikan.
- **Karakteristik:** Memiliki **dua dasar lembah yang sejajar** pada level *Support* kuat. Lembah kedua gagal menembus level terendah lembah pertama, menandakan tekanan jual (*selling pressure*) telah habis.
- **Neckline:** Level titik tertinggi (*peak*) perantara di antara kedua lembah.
- **Konfirmasi Breakout & Volume:** Validasi terjadi saat lilin harga berhasil ditutup di atas garis *Neckline* dengan **konfirmasi volume tinggi** (minimal 1.15x lipat dari rata-rata volume 20 lilin terakhir). Ini membuktikan bahwa institusi besar masuk mendorong harga naik.
- **Penempatan Stop Loss:** Di bawah level support (terendah dari kedua lembah) ditambah buffer pips.
- **Target Take Profit:** Proyeksi tinggi pola (*Pattern Height Projection*, dihitung dari jarak support ke neckline lalu diproyeksikan ke atas dari titik breakout) atau menggunakan rasio Risk:Reward 1:1.5 - 1:2.0.

### B. Double Top (Pola "M" - Bearish Reversal)
- **Kondisi Awal:** Terbentuk setelah tren naik (*uptrend*) yang kuat.
- **Karakteristik:** Memiliki **dua puncak sejajar** pada level *Resistance* kuat. Puncak kedua gagal mencetak *Higher High* baru, mencerminkan hilangnya momentum pembeli.
- **Neckline:** Level titik terendah (*trough*) perantara di antara kedua puncak.
- **Konfirmasi Breakdown & Volume:** Validasi terjadi saat lilin harga ditutup di bawah garis *Neckline* dengan **volume tinggi**.
- **Penempatan Stop Loss:** Di atas level resistance (tertinggi dari kedua puncak) ditambah buffer pips.
- **Target Take Profit:** Proyeksi tinggi pola ke arah bawah dari garis neckline atau target rasio Risk:Reward.

---

## 🎨 2. Tampilan Indikator di Chart MT5 (`Double_Top_Bottom_Indicator.ex5`)

Saat indikator dipasang ke chart:
1. **Garis Pola (Bentuk M / W):**
   - Garis **Aqua** tebal secara otomatis menghubungkan kedua lembah dan neckline pada pola Double Bottom ("W").
   - Garis **Light Coral / Merah** tebal menghubungkan kedua puncak dan neckline pada pola Double Top ("M").
2. **Garis Horizontal Neckline:** Garis berwarna **Gold (Emas)** putus-putus membentang dari titik neckline sebagai batas acuan konfirmasi breakout.
3. **Sinyal Panah Non-Repainting:**
   - **Panah Aqua (Bawah Lilin):** Sinyal Buy terkonfirmasi (Breakout Neckline + High Volume pada Bar 1 tertutup).
   - **Panah Magenta (Atas Lilin):** Sinyal Sell terkonfirmasi (Breakdown Neckline + High Volume pada Bar 1 tertutup).
4. **HUD Dashboard On-Chart (Pojok Kiri Bawah - Lebar 430px):**
   - **Pattern Status:** Menampilkan status pola real-time (`Forming W`, `Breakout W!`, `Forming M`, `Breakout M!`).
   - **Neckline Level:** Menampilkan angka harga garis neckline yang menjadi garis batas konfirmasi.
   - **Pattern Extremum:** Menampilkan level harga Support ganda atau Resistance ganda.
   - **Pattern Height:** Tinggi pola dalam points yang menjadi target objektif proyeksi Take Profit.
   - **Breakout Volume:** Rasio volume lilin konfirmasi terhadap SMA Volume 20 (misal `1.35x SMA (High Volume Confirmed)` berwarna hijau).
   - **Trade Signal:** Status sinyal trading terkini.
   - **Sesi Pasar:** Sesi perdagangan aktif (London / New York).

---

## 🎯 3. Standard Operating Procedure (SOP) Trading Manual (Tanpa EA)

Bagi trader yang ingin mengeksekusi sinyal secara manual dengan bantuan indikator:

### Setup BUY (Double Bottom "W")
1. Perhatikan chart setelah fase *downtrend*, tunggu indikator menggambar pola **"W"** warna Aqua.
2. Tunggu harga menembus ke atas garis **Neckline Gold**.
3. Pastikan lilin breakout tersebut telah **tertutup sempurna** (Bar 1 close di atas Neckline).
4. Cek baris **Breakout Volume** di Dashboard HUD berwarna **Hijau** (menunjukkan volume di atas 1.15x rata-rata).
5. Muncul **Panah Aqua** di bawah candle.
6. **Eksekusi Entry:** BUY pada pembukaan candle berikutnya (Open Bar 0).
7. **Stop Loss (SL):** Pasang di bawah level Support terendah pola "W" (diberi jarak buffer 5-10 pips).
8. **Take Profit (TP):** Pasang di level proyeksi tinggi pola (lihat nilai *Pattern Height* di dashboard) atau gunakan R:R minimal 1:1.5.

### Setup SELL (Double Top "M")
1. Perhatikan chart setelah fase *uptrend*, tunggu indikator menggambar pola **"M"** warna Coral.
2. Tunggu harga menembus ke bawah garis **Neckline Gold**.
3. Pastikan lilin breakdown telah **tertutup sempurna** (Bar 1 close di bawah Neckline).
4. Cek baris **Breakout Volume** di Dashboard HUD berwarna **Hijau**.
5. Muncul **Panah Magenta** di atas candle.
6. **Eksekusi Entry:** SELL pada pembukaan candle berikutnya (Open Bar 0).
7. **Stop Loss (SL):** Pasang di atas level Resistance tertinggi pola "M" (diberi jarak buffer 5-10 pips).
8. **Take Profit (TP):** Pasang di level proyeksi tinggi pola ke arah bawah atau gunakan R:R minimal 1:1.5.

---

## 🎬 4. Cara Backtest Visual Menggunakan Robot EA (`Double_Top_Bottom_EA.ex5`)

1. Buka MetaTrader 5 dan tekan tombol shortcut **`Ctrl + R`** untuk membuka jendela **Strategy Tester**.
2. Pada tab **Settings**:
   - **Expert:** Pilih `Double_Top_Bottom_EA.ex5`.
   - **Symbol:** `XAUUSD.dmb` (atau `XAUUSD` / `GOLD` sesuai broker Anda).
   - **Timeframe:** `M15` atau `H1` (Timeframe terbaik untuk keandalan pola chart).
   - **Period:** `Custom period` (misalnya 1 tahun terakhir, misal `2025.01.01 - 2026.01.01`).
   - **Modeling:** Pilih `1 minute OHLC` (sangat cepat & akurat untuk bar-opening EA) atau `Every tick based on real ticks`.
   - **Visual mode with display of charts:** ☑️ **Wajib dicentang** agar chart berjalan secara visual.
3. Pada tab **Inputs**:
   - Klik kanan di sembarang tempat pada tabel input -> Pilih **Load**.
   - Pilih file preset: **`Double_Top_Bottom_Backtest.set`** -> klik **Open**.
4. Klik tombol hijau **Start** di pojok kanan bawah.
5. MetaTrader 5 akan membuka chart visual pengujian dan menjalankan robot secara otomatis:
   - Pola Double Top & Bottom akan terdeteksi.
   - Begitu terjadi breakout neckline dengan volume tinggi, EA langsung membuka posisi.
   - Garis SL, TP, Auto BEP, dan Trailing Stop akan dikelola otomatis oleh EA.

---

## 🛡️ 5. Fitur Proteksi Resiko Institusional (Risk Management Pro)

Robot EA ini dirancang dengan pengamanan modal ketat untuk menjaga akun trading Anda tetap sehat:
- **Dynamic Lot Sizing:** Menghitung lot secara presisi berdasarkan persentase resiko ekuitas (default: 1.0% per trade).
- **Daily Loss Circuit Breaker:** Maksimal 2 trade rugi per hari atau 3% drawdown harian. Jika batas tercapai, EA otomatis berhenti melakukan trading hingga hari berganti untuk mencegah *revenge trading*.
- **Proteksi Gap Akhir Pekan (Friday Auto-Close):** Menutup otomatis seluruh posisi terbuka pada hari Jumat pukul 21:30 broker time dan memblokir order baru sejak pukul 18:00 untuk menghindari resiko *gap* pasar di hari Senin.
- **Auto Break-Even (BEP):** Saat harga telah bergerak menghasilkan keuntungan sebesar 1.0x resiko (1:1 R:R), Stop Loss otomatis dimajukan ke titik impas + 20 points (bebas resiko).
- **Trailing Stop Adaptif:** Mengunci sisa keuntungan secara bertahap seiring laju pergerakan tren harga.
- **Anti-Error 10016 Broker Protection:** Seluruh jarak SL dan TP selalu divalidasi terhadap `SYMBOL_TRADE_STOPS_LEVEL` dan *Spread* live broker sebelum order dikirim ke server broker.
