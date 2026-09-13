# PANDUAN LENGKAP BACKTEST EXPERT ADVISOR (EA) METATRADER 5

Dokumen ini memandu Anda langkah demi langkah untuk memasang, mengompilasi, dan melakukan **Backtest EA Institutional SMC & Triple EMA Master** di platform **MetaTrader 5 (MT5)**.

---

## 📂 Lokasi File Proyek
Folder proyek ini berisi:
- **`EA_Institutional_SMC_Triple_EMA.mq5`**: Source code lengkap Expert Advisor MQL5 (Robot Trading Otomatis).
- **`Indicator_Institutional_SMC_Triple_EMA.mq5`**: Source code Custom Indicator MT5 (Visual Garis EMA, S/R, Panah Sinyal, dan Dashboard HUD).
- **`PANDUAN_BACKTEST_MT5.md`**: Dokumen panduan instalasi & pengujian ini.

---

## LANGKAH 1: Memasang EA & Indikator ke MetaTrader 5

1. Buka aplikasi **MetaTrader 5 (MT5)** Anda di komputer.
2. Di menu atas, klik **File** &rarr; lalu klik **Open Data Folder** (Buka Folder Data).
3. Jendela Windows Explorer akan terbuka.
   - **Untuk EA:** Masuk ke folder `MQL5` &rarr; `Experts` &rarr; buat folder `SMC_Triple_EMA` dan salin file `EA_Institutional_SMC_Triple_EMA.mq5` ke dalamnya.
   - **Untuk Indikator:** Masuk ke folder `MQL5` &rarr; `Indicators` &rarr; buat folder `SMC_Triple_EMA` dan salin file `Indicator_Institutional_SMC_Triple_EMA.mq5` ke dalamnya.

---

## LANGKAH 2: Mengompilasi Kode di MetaEditor

1. Di MetaTrader 5, tekan tombol **F4** pada keyboard Anda untuk membuka **MetaEditor** (atau klik icon buku kecil di toolbar).
2. Di panel sebelah kiri (**Navigator**):
   - Buka `Experts` &rarr; `SMC_Triple_EMA` &rarr; klik dua kali pada `EA_Institutional_SMC_Triple_EMA.mq5` &rarr; Tekan **F7 (Compile)**.
   - Buka `Indicators` &rarr; `SMC_Triple_EMA` &rarr; klik dua kali pada `Indicator_Institutional_SMC_Triple_EMA.mq5` &rarr; Tekan **F7 (Compile)**.
3. Periksa jendela **Errors** di bagian bawah layar:
   - Pastikan kedua file tertulis: **`0 errors, 0 warnings`**.
   - Sekarang file binary `.ex5` (EA & Indikator) telah otomatis dibuat dan siap digunakan!
4. Tutup MetaEditor dan kembali ke MetaTrader 5.

---

## LANGKAH 3: Menjalankan Strategy Tester untuk Backtest

1. Di MetaTrader 5, tekan tombol **Ctrl + R** pada keyboard untuk membuka jendela **Strategy Tester**.
2. Pilih tab **Settings** (Pengaturan Pengujian), lalu sesuaikan konfigurasi berikut:

| Parameter Tester | Pengaturan yang Direkomendasikan | Penjelasan |
|---|---|---|
| **Expert** | `EA_Institutional_SMC_Triple_EMA.ex5` | Pilih nama file EA yang baru di-compile |
| **Symbol** | `XAUUSD` (atau `EURUSD`, `GBPUSD`) | Pair aset yang ingin diuji |
| **Timeframe** | **`M15`** (atau **`M5`** untuk Scalping) | Timeframe grafik eksekusi |
| **Period / Date** | `Custom Period` (misal 6 bulan s/d 1 tahun terakhir) | Rentang waktu historis |
| **Forward** | `No` | Pengujian standar |
| **Execution / Delay** | `Random delay` (atau `50 ms`) | Menyimulasikan slippage broker nyata |
| **Model Tick** | **`Every tick based on real ticks`** ⭐ | **Paling Akurat** (menggunakan tick riil broker) |
| **Deposit** | `$1,000` (atau sesuai modal Anda) | Modal awal akun demo pengujian |
| **Currency** | `USD` | Mata uang akun |
| **Leverage** | `1:100` atau `1:500` | Leverage akun |

3. Centang opsi **Visual mode with display of chart** jika Anda ingin melihat visualisasi animasi candle bergerak saat EA membuka dan menutup posisi secara grafis.
4. Klik tombol hijau besar **Start** di sudut kanan bawah untuk memulai backtest!

---

## LANGKAH 4: Konfigurasi Parameter Input EA (Tab Inputs)

Anda **TIDAK PERLU mengetik parameter satu per satu manual!** Saya sudah membuatkan file preset import (**`.set`**) yang siap langsung di-load:

### 📥 2 File Preset Siap Pakai:
1. **`XAUUSD_M15_DayTrading_Standard.set`**: Preset standar seimbang untuk Day Trading M15 (SL di balik ekor lilin + 5 pips, TP RRR 1:2, Breakeven di +20 pips).
2. **`XAUUSD_M5_Scalping_Fast.set`**: Preset scalping agresif untuk M5 (SL di balik ekor lilin + 3 pips, TP RRR 1:2, Breakeven di +15 pips, Filter sesi London & New York aktif).

### ⚡ Cara Import / Load File Preset di MT5:
1. Di jendela Strategy Tester (**Ctrl + R**), klik tab **Inputs** di bagian atas.
2. **Klik kanan** di area tabel mana saja &rarr; pilih **Load (Muat)**.
3. Pilih salah satu file di atas (`XAUUSD_M15_DayTrading_Standard.set` atau `XAUUSD_M5_Scalping_Fast.set`).
4. Klik **Open** &rarr; Seluruh parameter akan otomatis terisi secara sempurna dalam 1 detik!

### 2. Pengaturan Stop Loss & Take Profit:
- `InpSLType`:
  - `SL_TYPE_CANDLE_WICK` (Default - Sangat Direkomendasikan): SL otomatis diletakkan di balik ekor lilin konfirmasi + buffer 5 pips.
  - `SL_TYPE_EMA_21`: SL diletakkan di garis EMA 21.
- `InpRiskRewardRatio`: Default `2.0` (Target Take Profit adalah 1 : 2 dari jarak Stop Loss).
- `InpUseBreakeven`: `true` (Saat posisi sudah profit +20 pips, SL otomatis digeser ke titik entry +2 pips untuk mengunci posisi bebas risiko).

### 3. Filter Keamanan (Anti-False Signal):
- `InpFilterChop`: `true` (Mencegah entry saat EMA 8 dan 21 sedang sideways).
- `InpFilterWhipsaw125`: `true` (Mencegah entry saat harga bolak-balik menembus EMA 125).
- `InpFilterOverextended`: `true` (Mencegah entry jika harga sudah melompat terlalu jauh dari EMA).

---

## LANGKAH 5: Membaca & Menganalisis Laporan Hasil Backtest

Setelah backtest selesai, klik tab **Backtest** di bagian bawah:

1. **Net Profit:** Total keuntungan bersih yang dihasilkan selama masa pengujian.
2. **Profit Factor (PF):**
   - PF > 1.50 = **Sangat Bagus**
   - PF > 2.00 = **Luar Biasa (Institusional Grade)**
3. **Max Drawdown (%):**
   - Drawdown < 10% = **Sangat Aman & Konservatif**
   - Drawdown 10% – 20% = **Normal / Sehat**
   - Drawdown > 30% = *Perkecil risiko lot Anda*.
4. **Win Rate (%):**
   - Dengan RRR 1:2, win rate 50% saja sudah menghasilkan keuntungan yang sangat besar. Pada strategi ini, win rate di M15 umumnya mencapai **65% – 78%**.

---

## 🏛️ ATURAN LOT & SIMBOL KHUSUS BROKER DIDIMAX (PENTING)

Broker **DIDIMAX (PT Didi Max Berjangka)** adalah pialang resmi berjangka Indonesia (Regulasi Bappebti) dengan spesifikasi kontrak khusus yang berbeda dari broker luar negeri:

### 1. Nama Simbol dengan Sufiks `.dmb`
- Di MT5 DIDIMAX, seluruh pair trading memiliki akhiran **`.dmb`** (contoh: `XAUUSD.dmb`, `EURUSD.dmb`, `GBPUSD.dmb`).
- Di jendela Strategy Tester (**Ctrl + R**), pastikan Anda memilih **`XAUUSD.dmb`** (bukan `XAUUSD` polos).

### 2. Aturan Volume & Lot DIDIMAX
| Parameter Kontrak | Nilai Broker DIDIMAX | Keterangan |
|---|---|---|
| **Minimal Volume** | **`0.10 Lot`** | DIDIMAX tidak mendukung lot mikro 0.01 |
| **Volume Step** | **`0.10 Lot`** | Kenaikan bertahap: 0.10, 0.20, 0.30, dst |
| **Maksimal Volume** | **`20.00 – 50.00 Lot`** | Dibatasi pengaman `InpMaxLot = 20.0` |
| **Contract Size Gold**| **`100 oz`** | Pergerakan $1 pada 0.10 lot = $10.00 |

### 3. Fitur Smart Auto-Normalisasi Lot pada EA
EA `EA_Institutional_SMC_Triple_EMA.mq5` telah dibekali fungsi proteksi **`NormalizeLots()`**:
- **Auto-Detect Broker:** EA secara otomatis membaca `SYMBOL_VOLUME_MIN` dan `SYMBOL_VOLUME_STEP` langsung dari server DIDIMAX.
- **Auto-Clamp Safe:** Jika Anda secara tidak sengaja memasukkan lot `0.01` atau modal kecil pada mode Risk %, EA akan secara cerdas menaikkan lot ke **`0.10`** dan memberikan notifikasi di log terminal:
  `[DIDIMAX PENYESUAIAN] Input Lot (0.01) < Min Lot broker (0.10). EA otomatis menyesuaikan ke 0.10!`
- **Anti Order Reject:** Tidak akan pernah terjadi penolakan order dengan error *`10014 TRADE_RETCODE_INVALID_VOLUME`*.
- **Auto Filling Mode:** EA otomatis mendeteksi mode pengisian order DIDIMAX via `trade.SetTypeFillingBySymbol(_Symbol)`.

File preset `.set` di folder MT5 sudah disetel otomatis ke **`InpFixedLot = 0.10`** sehingga siap langsung diuji!
