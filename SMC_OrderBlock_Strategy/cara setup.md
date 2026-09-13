# 🏛️ Panduan Lengkap: Institutional SMC & S/R Master (MetaTrader 5)
## Support & Resistance Terkuat, Auto Fibonacci Golden Zone, BOS/CHoCH, Order Block & FVG System

Sistem trading institusional ini dirancang khusus untuk menganalisa dan mengeksekusi peluang probabilitas tinggi pada pasar **XAUUSD (Emas)** dan instrumen Forex utama di platform **MetaTrader 5 (MT5)**, baik untuk analisa teknikal manual maupun otomatisasi robot (EA).

---

## 💎 1. Fitur Lengkap Indikator Visual di Chart MT5

Ketika template atau indikator dipasang ke chart MT5 Anda:

1. **Garis Support & Resistance Dinamis (Major & Minor):**
   - **Garis Merah Solid (Major Resistance):** Ditarik langsung dari titik puncak swing pivot terkuat dan memanjang horizontal ke kanan layar (*Ray Right*), lengkap dengan tag harga nominal (contoh: `R Major: 2345.50`).
   - **Garis Hijau Solid (Major Support):** Ditarik dari titik lembah swing pivot terendah terkuat dan memanjang horizontal ke kanan layar (*Ray Right*), lengkap dengan tag harga nominal (contoh: `S Major: 2320.10`).
   - **Garis Putus-Putus (Minor S/R):** Level pantulan intraday terdekat (`R Minor` & `S Minor`) untuk mengantisipasi reaksi harga cepat.
2. **Auto Fibonacci Golden Zone (0.50 - 0.65 OTE):**
   - **Kotak Emas/Kuning Gelap (*Golden Pocket*):** Area pantulan emas (0.50 s/d 0.65 OTE) yang otomatis dipetakan dari ayunan harga terkini (*dealing range*).
   - **Garis Putus-Putus Emas 61.8%:** Level rasio emas paling presisi tempat institusi bank memasang limit order pantulan.
3. **Garis Struktur Pasar (BOS & CHoCH):**
   - Garis hijau/merah yang secara otomatis memetakan titik penembusan struktur (*Break of Structure*) dan pembalikan tren (*Change of Character*).
4. **Institutional Order Block (OB):**
   - **Kotak Biru Transparan (Bullish OB / Demand):** Area akumulasi beli institusi.
   - **Kotak Merah Transparan (Bearish OB / Supply):** Area distribusi jual institusi.
   - Kotak yang sudah tersentuh/termitigasi akan otomatis dirapikan (*muted dotted style*) agar chart tidak semrawut.
5. **Fair Value Gap (FVG / Imbalance):**
   - Kotak area ketidakseimbangan likuiditas 3 lilin yang belum terisi (*unfilled liquidity*).
6. **Panah Konfirmasi Sinyal Non-Repainting:**
   - **Panah Biru Aqua (Naik):** Konfirmasi entri BUY setelah harga retest ke Bullish OB dengan pantulan lilin bullish.
   - **Panah Magenta (Turun):** Konfirmasi entri SELL setelah harga retest ke Bearish OB dengan pantulan lilin bearish.
7. **HUD Dashboard On-Chart (Pojok Kiri Bawah):**
   - Menampilkan Market Structure aktif, jarak pips ke Major Resistance/Support, status zona Fibonacci (*IN GOLDEN POCKET!*, *Premium Zone*, *Discount Zone*), jumlah OB unmitigated, status sinyal, dan sesi pasar aktif.

---

## ⚡ 2. Cara Pasang 1-Klik Menggunakan Template Chart MT5 (.tpl)

Kami telah membuatkan template khusus yang sudah disalin langsung ke direktori MT5 Anda:
📁 Nama Template: **`Institutional_SMC_SR_Master.tpl`** (atau **`SMC_OrderBlock_Pro.tpl`**)

### Langkah Pemasangan Sangat Mudah:
1. Buka aplikasi **MetaTrader 5 (MT5)** di komputer Anda.
2. Buka chart yang ingin Anda analisa, misalnya **`XAUUSD`** pada timeframe **`M15`** atau **`M5`**.
3. **Klik Kanan** di area kosong chart mana saja.
4. Sorot menu **Templates** -> Pilih **`Institutional_SMC_SR_Master`** (atau `SMC_OrderBlock_Pro`).
5. **Selesai!** 
   - Chart seketika berubah menjadi tema gelap institusional elegan (*dark mode*).
   - Lilin hijau & merah cerah, grid tersembunyi, chart shift aktif ke kanan.
   - Seluruh **Garis Major S/R**, **Kotak Fibo Golden Zone & Garis 61.8%**, **Kotak Order Block & FVG**, serta **HUD Dashboard** langsung muncul rapi di layar!

---

## 🎯 3. Standard Operating Procedure (SOP) Trading Manual

### Setup BUY (High Probability Confluence):
1. **Bias Struktur:** Dashboard menunjukkan `BULLISH CHoCH` atau `BULLISH BOS`.
2. **Zona Harga:** Harga berada di **Discount Zone** (< 50% dealing range) atau menyentuh **Kotak Emas Fibo Golden Pocket (0.50 - 0.65)**.
3. **Area Entri:** Harga pullback masuk menyentuh **Kotak Biru (Bullish OB)** atau **Major Support Hijau**.
4. **Konfirmasi:** Muncul lilin pantulan bullish (Bar 1 tertutup) dan muncul **Panah Aqua**.
5. **Eksekusi:** BUY pada pembukaan lilin berikutnya.
6. **Stop Loss (SL):** 5-10 pips di bawah batas bawah Order Block / Major Support.
7. **Take Profit (TP):** Target rasio **1:1.5 s/d 1:2.0** atau pada garis **Major Resistance Merah**.

### Setup SELL (High Probability Confluence):
1. **Bias Struktur:** Dashboard menunjukkan `BEARISH CHoCH` atau `BEARISH BOS`.
2. **Zona Harga:** Harga berada di **Premium Zone** (> 50% dealing range) atau menyentuh **Kotak Emas Fibo Golden Pocket**.
3. **Area Entri:** Harga pullback naik menyentuh **Kotak Merah (Bearish OB)** atau **Major Resistance Merah**.
4. **Konfirmasi:** Muncul lilin pantulan bearish (Bar 1 tertutup) dan muncul **Panah Magenta**.
5. **Eksekusi:** SELL pada pembukaan lilin berikutnya.
6. **Stop Loss (SL):** 5-10 pips di atas batas atas Order Block / Major Resistance.
7. **Take Profit (TP):** Target rasio **1:1.5 s/d 1:2.0** atau pada garis **Major Support Hijau**.

---

## 🤖 4. Menjalankan Robot Trading Otomatis (Expert Advisor / EA)

Robot EA terkompilasi **`SMC_OrderBlock_EA.ex5`** dapat Anda gunakan untuk auto trading maupun pengujian Strategy Tester di MT5:

### A. Cara Pasang EA di Live / Demo Chart:
1. Di panel **Navigator (Ctrl + N)** MT5 -> Buka folder **Expert Advisors**.
2. Tarik (*drag & drop*) **`SMC_OrderBlock_EA`** ke chart XAUUSD yang sudah terpasang template di atas.
3. Di tab **Common**: Centang **"Allow Algo Trading"**.
4. Di toolbar atas MT5: Pastikan tombol **Algo Trading** berwarna hijau aktif.

### B. Cara Menjalankan Backtest Visual 1 Tahun:
1. Tekan shortcut **`Ctrl + R`** di MetaTrader 5 untuk membuka panel **Strategy Tester**.
2. Pada tab **Settings**:
   - **Expert:** `SMC_OrderBlock_EA.ex5`
   - **Symbol:** `XAUUSD.dmb` (atau simbol Gold broker Anda).
   - **Timeframe:** `M15` atau `M5`.
   - **Period:** `Custom period` (misal 1 tahun ke belakang).
   - **Modeling:** `1 minute OHLC` (sangat cepat) atau `Every tick based on real ticks`.
   - **Visual mode:** ☑️ **Centang kotak ini** untuk melihat jalannya eksekusi candle demi candle.
3. Pada tab **Inputs**:
   - Klik kanan -> Pilih **Load**.
   - Pilih preset optimal: **`SMC_XAUUSD_Backtest.set`** -> klik **Open**.
4. Klik tombol hijau **Start**.
5. Chart visual akan otomatis berjalan mundur dan mengeksekusi order dengan proteksi Stop Loss & Take Profit otomatis.

---

## 🛡️ 5. Proteksi Resiko Institusional Bawaan Robot EA

- **Daily Loss Circuit Breaker:** Mengunci akun jika batas toleransi loss harian tercapai (default 2 loss/hari), memotong rantai *overtrading* dan menjaga modal.
- **Proteksi Gap Akhir Pekan (Friday Auto-Close):** Menolak entri baru setelah pukul 18:00 dan menutup seluruh posisi pada 21:30 di hari Jumat untuk mengamankan saldo dari lompatan harga akhir pekan.
- **Auto Break-Even (BEP):** Menggeser Stop Loss ke harga entri (+ buffer pips) begitu harga mencapai profit 1.2R.
- **Trailing Stop Adaptif:** Mengunci profit berjalan secara bertahap saat target profit mendekati TP penuh.
