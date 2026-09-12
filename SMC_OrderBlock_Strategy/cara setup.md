# 🏛️ Panduan Lengkap: Smart Money Concepts (SMC) Strategy
## Order Block (OB), Fair Value Gap (FVG), BOS & CHoCH System untuk MetaTrader 5

Sistem trading ini dirancang khusus untuk menangkap jejak transaksi institusi besar (*Smart Money*) pada pasar **XAUUSD (Emas)** dan instrumen Forex utama.

---

## 📚 1. Konsep Dasar Smart Money Concepts (SMC)

Berbeda dengan indikator ritel biasa, SMC berfokus pada **likuiditas institusional**:

### A. Order Block (OB)
- **Bullish Order Block (Demand Zone):** Lilin *bearish* terakhir sebelum terjadi pergerakan impulsif naik tajam yang menembus struktur (*BOS*). Menjadi area pantulan Buy saat harga kembali melakukan koreksi (*retest*).
- **Bearish Order Block (Supply Zone):** Lilin *bullish* terakhir sebelum terjadi dorongan turun tajam yang menembus struktur. Menjadi area pantulan Sell saat harga retest.
- **Unmitigated Zone:** Kotak zona OB di chart yang belum pernah disentuh kembali oleh harga. Ini adalah area dengan probabilitas pantulan tertinggi (*Fresh Area*).

### B. Fair Value Gap (FVG / Imbalance)
- Terjadi ketika ada pergerakan 3 lilin cepat di mana sumbu Lilin 1 dan sumbu Lilin 3 tidak saling bersentuhan (meninggalkan celah kosong).
- Harga memiliki kecenderungan 80%+ untuk kembali mengisi (*fill*) area FVG ini sebelum melanjutkan arah tren aslinya.

### C. Break of Structure (BOS) vs Change of Character (CHoCH)
- **BOS (Break of Structure):** Penembusan swing high/low searah tren yang sedang berjalan (tanda kelanjutan tren / *trend continuation*).
- **CHoCH (Change of Character):** Penembusan swing struktural berlawanan arah yang menandakan **pembalikan arah tren utama** (*trend reversal*).

---

## 🎨 2. Tampilan Indikator di Chart MT5

Saat indikator `SMC_OrderBlock_Indicator.ex5` dipasang ke chart:
1. **Kotak Biru Transparan:** Zona Bullish Order Block (Area Buy).
2. **Kotak Merah Transparan:** Zona Bearish Order Block (Area Sell).
3. **Kotak Garis Hijau / Magenta:** Fair Value Gap (FVG / Imbalance).
4. **Panah Aqua (Naik):** Sinyal konfirmasi Buy setelah retest ke Bullish OB.
5. **Panah Magenta (Turun):** Sinyal konfirmasi Sell setelah retest ke Bearish OB.
6. **HUD Dashboard On-Chart (Pojok Kiri Bawah):**
   - **SMC Structure:** Status struktur saat ini (`BULLISH CHoCH`, `BEARISH BOS`, dll).
   - **Bullish & Bearish OB Zone:** Rentang harga zona Order Block aktif terdekat.
   - **Nearest FVG:** Status gap ketidakseimbangan terdekat.
   - **Price Status:** Status posisi harga saat ini (apakah sedang retest OB atau filling FVG).
   - **Trade Signal:** Sinyal konfirmasi masuk pasar.
   - **Sesi Pasar:** Sesi aktif saat ini (London / New York).

---

## 🎯 3. Standard Operating Procedure (SOP) Trading Manual

Jika Anda menggunakan indikator tanpa robot EA:

### Setup BUY
1. Dashboard menunjukkan **Bullish CHoCH** atau **Bullish BOS**.
2. Harga turun (*pullback*) masuk ke dalam **Kotak Biru (Bullish OB)**.
3. Muncul candle pantulan bullish yang tertutup (Bar 1) dan muncul **Panah Aqua**.
4. **Eksekusi:** BUY di harga penutupan lilin tersebut.
5. **Stop Loss:** 5 pips di bawah batas bawah kotak Order Block.
6. **Take Profit:** Rasio Risk:Reward **1 : 2.0** atau pada Swing High terdekat.

### Setup SELL
1. Dashboard menunjukkan **Bearish CHoCH** atau **Bearish BOS**.
2. Harga naik (*pullback*) menyentuh **Kotak Merah (Bearish OB)**.
3. Muncul candle pantulan bearish yang tertutup (Bar 1) dan muncul **Panah Magenta**.
4. **Eksekusi:** SELL di harga penutupan lilin tersebut.
5. **Stop Loss:** 5 pips di atas batas atas kotak Order Block.
6. **Take Profit:** Rasio Risk:Reward **1 : 2.0** atau pada Swing Low terdekat.

---

## 🎬 4. Cara Backtest Visual 1 Tahun Menggunakan Robot EA

1. Tekan **`Ctrl + R`** di MetaTrader 5 untuk membuka Strategy Tester.
2. Pada tab **Settings**:
   - **Expert:** Pilih `SMC_OrderBlock_EA.ex5`.
   - **Symbol:** `XAUUSD.dmb` (atau simbol Gold broker Anda).
   - **Timeframe:** `M5` (atau `M15`).
   - **Period:** `Custom period` (misal 1 tahun ke belakang).
   - **Modeling:** `1 minute OHLC` (cepat & efisien) atau `Every tick based on real ticks`.
   - **Visual mode:** ☑️ **Centang kotak ini** untuk melihat chart berjalan maju mundur secara visual.
3. Pada tab **Inputs**:
   - Klik kanan -> Pilih **Load**.
   - Pilih file preset: **`SMC_XAUUSD_Backtest.set`** -> klik **Open**.
4. Klik tombol hijau **Start**.
5. Chart akan mundur ke masa lalu dan mulai memetakan Order Block serta mengeksekusi order secara otomatis.

---

## 🛡️ 5. Proteksi Resiko Bawaan Robot EA (Risk Management Pro)

EA ini telah dilengkapi dengan proteksi institusional teruji:
- **Daily Loss Circuit Breaker:** Maksimal 2 loss per hari. Jika tercapai, EA otomatis berhenti trading sampai besok untuk memotong rantai kerugian beruntun.
- **Proteksi Gap Akhir Pekan (Friday Auto-Close):** Menutup otomatis semua posisi terbuka pada hari Jumat pukul 21:30 broker time agar saldo terhindar dari lonjakan gap hari Senin.
- **Auto Break-Even (BEP):** Mengunci modal ke BEP + 20 points begitu keuntungan mencapai 1.2R.
- **Delayed Trailing Stop:** Trailing stop baru aktif setelah posisi mencapai keuntungan minimal 1.4R, memberi ruang napas bagi harga untuk melaju ke Take Profit penuh 1:2.0.
