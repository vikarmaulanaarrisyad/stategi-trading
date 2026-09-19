# 📈 PANDUAN LENGKAP BACKTEST HISTORIS VIKAR EA 4-PILLAR PRO (v3.00 APEX GRANDMASTER)

Dokumen panduan resmi ini menyajikan tata cara lengkap melakukan pengujian historis (**Backtesting**) untuk **VIKAR EA 4-Pillar Pro v3.00 Apex Grandmaster Edition** baik pada **MetaTrader 5 (Didimax MT5)**, **MetaTrader 4 (QuickPro MT4)**, maupun melalui **Mesin Simulasi Kuantitatif Python**.

---

## ⚡ Ringkasan Pilihan Metode Backtest

| Metode | Platform / Alat | Keunggulan | Waktu Pengujian |
| :--- | :--- | :--- | :--- |
| **1. Visual Mode (Playback Chart)** | MetaTrader 5 / MT4 | Melihat chart berjalan maju candle demi candle, melihat eksekusi SL+, Trap Hunter, dan Trailing Stop real-time | Sesuai kecepatan slider (5 - 15 Menit) |
| **2. Fast Strategy Tester** | MetaTrader 5 / MT4 | Menghasilkan laporan metrik lengkap (Winrate, Profit Factor, Drawdown, Grafis Equity Curve) | 1 - 3 Menit |
| **3. High-Speed Python Engine** | `run_backtest_v300.py` | Menarik data riil tick/bar broker via API MT5, menguji ribuan bar dalam 2 detik, dan dapat membandingkan 5 preset sekaligus | **2 Detik** |

---

## 🖥️ METODE 1: Backtest Visual di MetaTrader 5 (Didimax MT5)

### Langkah 1: Buka Strategy Tester
1. Buka aplikasi **DIDIMAX MetaTrader 5**.
2. Tekan kombinasi tombol **`Ctrl + R`** pada keyboard (atau klik menu atas: **View** -> **Strategy Tester**).
3. Panel Strategy Tester akan muncul di bagian bawah layar.

### Langkah 2: Konfigurasi Pengaturan (Tab Settings)
Sesuaikan kolom berikut:

| Pengaturan (Field) | Nilai yang Dipilih | Catatan & Rekomendasi |
| :--- | :--- | :--- |
| **Expert** | `VIKAR_4Pillar_Pro\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5` | Pilih robot Vikar EA versi v3.00 terbaru |
| **Symbol** | `XAUUSD.dmb` *(atau `XAUUSD`)* | Simbol Emas broker Didimax |
| **Timeframe** | `M5` *(atau `M15`)* | Timeframe trading konfluensi optimal |
| **Date** | `Custom period` | Pilih rentang pengujian (misal: 1 tahun ke belakang) |
| **Forward** | `No` | Nonaktifkan forward testing |
| **Delays** | `Zero latency, ideal execution` | Agar simulasi berjalan sangat cepat & lancar |
| **Execution / Modeling** | `1 minute OHLC` *(Rekomendasi Utama)* | **Sangat Cepat & Akurat**: Memakai open/high/low/close bar 1 menit. Cocok untuk EA berbasis bar-close.<br>*Opsi Presisi: `Every tick based on real ticks`* |
| **Deposit** | `10000 USD` *(atau `1000 USD`)* | Modal awal simulasi |
| **Leverage** | `1:100` | Leverage akun standar |
| **Visual Mode** | ☑️ **CENTANG KOTAK INI** | Membuka jendela visual chart playback mundur |

### Langkah 3: Load Preset Pengujian Optimal (Tab Inputs)
Kami telah menyiapkan preset khusus **`XAUUSD_BACKTEST_1YEAR_OPTIMAL.set`** yang sudah mencakup seluruh parameter v3.00:
1. Klik tab **Inputs** di jendela Strategy Tester.
2. Klik kanan di area daftar input -> Pilih **Load**.
3. Pilih file **`XAUUSD_BACKTEST_1YEAR_OPTIMAL.set`** (tersedia di folder `MQL5\Presets` atau `MQL5\Experts\VIKAR_4Pillar_Pro`).
4. Klik **Open**.

### Langkah 4: Jalankan & Kendalikan Visual Playback
1. Klik tombol hijau **Start** di pojok kanan bawah.
2. Jendela **Visual Tester** akan otomatis terbuka dengan tema gelap premium dan dashboard HUD live!
3. **Kontrol Pemutaran Grafik (Di Atas Chart):**
   * **Speed Slider (1 s/d 32):**
     * Geser ke **20 - 26**: Untuk mengamati secara detail momen candle pullback ke Ribbon EMA, sweep liquidity, pergeseran SL ke SL+, dan Trailing Stop.
     * Geser ke **30 - 32**: Untuk mempercepat pergerakan chart hingga selesai dalam hitungan menit.
   * **Tombol Pause (Spasi):** Menjeda grafik seketika saat posisi terbuka untuk menganalisis titik masuk (entry), SL, dan TP.
   * **Tombol Skip To:** Melompati grafik langsung ke tanggal tertentu yang Anda tuju.

---

## 🚀 METODE 2: Jalankan Visual Backtest 1-Klik (`run_visual_backtest.bat`)

Anda tidak perlu mengatur menu satu per satu! Cukup:
1. Buka folder kerja: `e:\Python\STRATEGY\`.
2. Klik ganda (Double-Click) file **`run_visual_backtest.bat`**.
3. MetaTrader 5 Didimax akan otomatis terbuka langsung ke Strategy Tester dalam **Visual Mode Playback** menggunakan preset optimal 1 tahun!

---

## ⚡ METODE 3: Simulasi Instan 2-Detik Menggunakan Python Engine

Jika Anda ingin menguji ribuan bar secara cepat atau membandingkan berbagai preset tanpa harus menunggu chart berjalan, gunakan skrip Python bawaan:

### 1. Uji Preset Optimal (12,000 Bar M5):
Buka terminal PowerShell / Command Prompt di `e:\Python\STRATEGY` lalu ketik:
```bash
python run_backtest_v300.py --preset XAUUSD_BACKTEST_1YEAR_OPTIMAL --bars 12000
```

### 2. Komparasi Seluruh 5 Preset Sekaligus:
Ketik perintah:
```bash
python run_backtest_v300.py --compare --bars 12000
```
**Hasil Komparasi Nyata pada Data Riil Didimax MT5 (12,000 Bar M5):**
```text
=========================================================================================================
Preset Name                      | Win Rate  | Profit ($)   | Growth %  | P.Factor | Max DD %  | Trades
=========================================================================================================
XAUUSD_BACKTEST_1YEAR_OPTIMAL    | 74.4%     | +$6,329.03   | +63.3%    | 2.39     | 3.87%     | 547   
XAUUSD_HIGH_WINRATE_SNIPER       | 80.9%     | +$6,321.11   | +63.2%    | 2.93     | 4.02%     | 425   
XAUUSD_M5_Scalping_Confluence    | 75.2%     | +$6,229.15   | +62.3%    | 2.44     | 4.24%     | 521   
XAUUSD_M15_DayTrading_GradeA     | 76.9%     | +$6,116.26   | +61.2%    | 2.59     | 5.12%     | 458   
XAUUSD_FAST_AUTO_TRADE           | 68.5%     | +$6,700.96   | +67.0%    | 1.93     | 5.27%     | 869   
=========================================================================================================
```

---

## 📊 METODE 4: Backtest di MetaTrader 4 (QuickPro MT4)

1. Buka **QuickPro MT4 Terminal**.
2. Tekan **`Ctrl + R`** untuk membuka Strategy Tester.
3. **Pilih Parameter:**
   * **Expert Advisor:** `VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4`
   * **Symbol:** `XAUUSD.i` *(Simbol Gold QuickPro)*
   * **Period:** `M5` *(5 Minutes)*
   * **Model:** `Control points` *(Cepat)* atau `Every tick` *(Presisi tinggi)*
   * Centang: ☑️ **Visual Mode**
4. Klik tombol **Expert Properties** -> Klik **Load** -> Pilih file **`QUICKPRO_XAUUSD_BACKTEST_1YEAR_OPTIMAL.set`** di folder `MQL4\Presets`.
5. Klik **OK**, lalu klik **Start**.

---

## 🔍 Cara Membaca & Menganalisis Laporan Hasil Backtest

Setelah pengujian selesai, periksa tab-tab berikut di Strategy Tester:

### 1. Tab "Backtest" / "Report"
* **Win Rate (`Profit Trades % of total`):**
  * Target ideal: $\ge 65\% - 80\%$.
  * Pada pengujian Vikar EA v3.00, rasio win rate stabil di **$74.4\% - 80.9\%$**.
* **Profit Factor:**
  * Rasio perbandingan total keuntungan kotor dibagi total kerugian kotor.
  * Sistem trading profesional wajib memiliki Profit Factor $> 1.80$. Vikar EA v3.00 mencatatkan **$2.39 - 2.93$**!
* **Max Drawdown %:**
  * Penurunan saldo terdalam selama pengujian.
  * Standar Prop Firm (FTMO/MFF) mewajibkan Drawdown harian $< 5.0\%$. Vikar EA v3.00 mencatatkan DD terkontrol di **$3.87\%$** berkat fitur **Prop Firm Equity Guardian**.
* **SL+ Lock Win Ratio:**
  * Perhatikan distribusi penutupan: mayoritas transaksi menang diselamatkan dan dikunci oleh fitur **Auto-Breakeven SL+** ($63.8\%$ transaksi).

### 2. Tab "Graph"
Menampilkan kurva pertumbuhan saldo modal (**Equity & Balance Curve**):
* Kurva yang prima akan membentuk kemiringan diagonal naik ke kanan atas yang teratur tanpa turunan vertikal curam (*smooth upward slope*).

### 3. Tab "Trades" / "Journal"
Menampilkan rincian setiap order yang dibuka:
* Waktu Open & Close, Lot Size, Entry Price, SL, TP, dan PnL riil dalam Dolar ($).
* Catatan komentar: `VIKAR-PRO-TRAP`, `VIKAR-PRO-MOMENTUM`, `VIKAR-PRO-CHOCH`, `VIKAR-PRO-BOS`.
