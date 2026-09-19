# 🏆 PANDUAN LENGKAP PENGGUNAAN EA 4-PILLAR PRO (METATRADER 4 - BROKER QUICKPRO)

> **Versi EA:** v2.30 Institutional Apex Momentum (MT4 Edition)  
> **Target Broker:** QuickPro / Broker MetaTrader 4 Lainnya  
> **Instrumen Utama:** XAUUSD / GOLD  
> **Timeframe Rekomendasi:** M15 (Primary Scalp & Day Trade) atau M5 (Fast Scalp)

---

## 📌 DAFTAR ISI
1. [Keunggulan Sistem Adaptasi Lot QuickPro](#1-keunggulan-sistem-adaptasi-lot-quickpro)
2. [Langkah-Langkah Instalasi di QuickPro MT4](#2-langkah-langkah-instalasi-di-quickpro-mt4)
3. [Pengaturan Wajib AutoTrading di MT4](#3-pengaturan-wajib-autotrading-di-mt4)
4. [Panduan Memuat File Preset (.set)](#4-panduan-memuat-file-preset-set)
5. [Fitur-Fitur Cerdas Unggulan di MT4](#5-fitur-fitur-cerdas-unggulan-di-mt4)
6. [Cara Setting Notifikasi Push ke HP (Android / iPhone)](#6-cara-setting-notifikasi-push-ke-hp-android--iphone)
7. [Tanya Jawab & Troubleshooting Error Umum MT4](#7-tanya-jawab--troubleshooting-error-umum-mt4)

---

## 1. Keunggulan Sistem Adaptasi Lot QuickPro

Salah satu kendala umum saat menjalankan robot EA di broker lokal seperti **QuickPro** adalah variasi aturan spesifikasi kontrak dan ukuran minimal lot:
- Beberapa tipe akun QuickPro memiliki **Minimal Lot 0.10** (Akun Standar/Reguler).
- Beberapa tipe akun memiliki **Minimal Lot 0.01** (Akun Mikro/Mini).

Jika sebuah EA dipaksa membuka 0.01 lot pada akun yang minimal lotnya 0.10, broker akan menolak order dengan kode `Error 131: ERR_INVALID_TRADE_VOLUME` dan robot gagal entry.

### 🛡️ Solusi Cerdas EA Vikar 4-Pillar MT4:
Pada EA ini, sistem lot telah dilengkapi fitur **`LOT_TYPE_BROKER_MIN` (Default)**:
```mql4
extern ENUM_LOT_TYPE InpLotType = LOT_TYPE_BROKER_MIN; // Otomatis menyesuaikan minimal lot broker QuickPro
```
- **Deteksi Otomatis:** EA langsung memanggil `MarketInfo(Symbol(), MODE_MINLOT)` dan `MarketInfo(Symbol(), MODE_LOTSTEP)`.
- **Aman 100%:** Jika akun Anda di QuickPro minimal lotnya `0.10`, EA akan otomatis mengeksekusi `0.10`. Jika minimal lotnya `0.01`, EA otomatis mengeksekusi `0.01`.
- **Tidak Perlu Edit Manual:** Anda tidak perlu khawatir salah ketik atau ditolak broker.

---

## 2. Langkah-Langkah Instalasi di QuickPro MT4

Ikuti langkah mudah berikut untuk memasang EA ke dalam terminal MetaTrader 4 QuickPro:

1. **Buka Terminal QuickPro MT4**.
2. Klik menu **File** di pojok kiri atas, lalu pilih **Open Data Folder** (Buka Folder Data).
3. Di jendela file explorer yang muncul, buka folder:
   ```text
   MQL4 ➔ Experts
   ```
4. Salin (Copy) file EA:
   - [VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4](file:///e:/Python/STRATEGY/VIKAR_EA_4PILLAR_MT4/VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4)
   - Tempel (Paste) ke dalam folder `Experts` tersebut.
5. Salin juga ketiga file preset `.set` ke dalam folder:
   ```text
   MQL4 ➔ Presets
   ```
   (File preset ada di: `e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\*.set`)
6. **Kompilasi EA (Compile):**
   - Kembali ke MT4, tekan tombol keyboard **F4** untuk membuka **MetaEditor MT4**.
   - Di panel Navigator MetaEditor sebelah kiri, buka folder `Experts` dan klik ganda `VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4`.
   - Klik tombol **Compile** (atau tekan **F7**).
   - Pastikan di bagian bawah tertulis: **`0 error(s), 0 warning(s)`**.
   - Tutup MetaEditor.
7. Kembali ke terminal MT4, di panel **Navigator** (sebelah kiri), klik kanan pada tulisan **Expert Advisors** lalu pilih **Refresh**.
8. Sekarang EA **`VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4`** sudah muncul dan siap digunakan!

---

## 3. Pengaturan Wajib AutoTrading di MT4

Agar EA dapat membuka dan mengelola order secara otomatis tanpa dihalangi sistem keamanan MT4:

1. **Aktifkan Tombol AutoTrading:**
   - Pada toolbar atas MT4, pastikan tombol bertuliskan **"AutoTrading"** berlogo hijau (menyala).
2. **Pengaturan Global MT4:**
   - Klik menu **Tools** ➔ **Options** ➔ Tab **Expert Advisors**.
   - Centang opsi:
     - ☑ **Allow automated trading**
     - ☑ **Allow DLL imports** (opsional, disarankan)
     - ☑ **Allow WebRequest for listed URL** (jika ingin webhook/alert)
   - Klik **OK**.
3. **Pasang EA ke Chart:**
   - Buka chart **XAUUSD** (Gold), atur timeframe ke **M15** (atau **M5**).
   - Seret (drag) EA dari panel Navigator ke atas chart.
   - Pada jendela pop-up tab **Common**:
     - Centang ☑ **Allow live trading**
     - Centang ☑ **Allow import of external experts**
     - Pastikan gambar emoji di pojok kanan atas chart tersenyum (😊).

---

## 4. Panduan Memuat File Preset (.set)

Tersedia 4 preset siap pakai yang telah dioptimasi khusus untuk XAUUSD di broker QuickPro:

| Nama File Preset | Karakter Strategi | Timeframe | Target Profit / Gaya |
| :--- | :--- | :--- | :--- |
| **`QUICKPRO_XAUUSD_FAST_AUTO_TRADE.set`** | 🚀 **Rekomendasi Utama** - Dual Engine (Reversal + Momentum Breakout Cepat) | M15 / M5 | Agresif seimbang, anti-ketinggalan tren kencang |
| **`QUICKPRO_XAUUSD_RR_1_TO_2_5_ELITE.set`** | 💎 **Elite RR 1:2.5** - Matematika Probabilitas Tinggi, Cuan 2.5x Risiko | M15 | Sangat menguntungkan, cukup winrate 30% akun tetap bertumbuh |
| **`QUICKPRO_XAUUSD_HIGH_WINRATE_SNIPER.set`** | 🎯 **Sniper Institusional** - Hanya eksekusi jika konfluensi skor $\ge 70$ | M15 / H1 | Winrate tinggi, santai, rasio RR 1:2 |
| **`QUICKPRO_XAUUSD_M5_SCALPING.set`** | ⚡ **Fast Scalper** - Menangkap ayunan pendek intraday | M5 | Target TP cepat, SL ketat, penguncian BE kilat |

### Cara Memuat Preset:
1. Saat jendela pengaturan EA terbuka (atau tekan **F7** pada chart tempat EA terpasang).
2. Pilih tab **Inputs**.
3. Klik tombol **Load** di sebelah kanan.
4. Pilih file preset yang diinginkan (misal: [QUICKPRO_XAUUSD_FAST_AUTO_TRADE.set](file:///e:/Python/STRATEGY/VIKAR_EA_4PILLAR_MT4/QUICKPRO_XAUUSD_FAST_AUTO_TRADE.set)).
5. Klik **Open**, lalu klik **OK**.

---

## 5. Fitur-Fitur Cerdas Unggulan di MT4

EA MT4 ini mengadopsi seluruh logika institusional v2.30 tanpa ada yang disunat:

### 1. Dual-Engine Execution (Anti-Ketinggalan Reli)
- **Engine 1 (Sniper Reversal):** Membeli di diskon/Order Block dengan konfirmasi pola lilin rejection (Pin Bar, Engulfing, Star, dsb.).
- **Engine 2 (Momentum Breakout):** Jika pasar emas mengalami breakout kencang dengan lonjakan Volume Institusional VSA $\ge 1.3\times$, EA langsung mengeksekusi order searah momentum tanpa menunggu pullback.

### 2. Multi-Stage Structural Trailing Stop (SMC Runner)
- Begitu target **TP1 tercapai (50% lot diamankan di saku)**:
  - Sisa lot (50% Runner) dipindahkan Stop Loss-nya ke atas/bawah **Ayunan Struktur SMC (Higher Low / Lower High)**.
  - Menghindari posisi ter-cut dini oleh koreksi minor, sehingga posisi runner mampu mengejar reli monster $\$30 - \$60$ pergerakan emas!

### 3. Circuit Breaker & Consecutive Loss Guard
- Jika terjadi 2 kali Stop Loss berturut-turut pada hari yang sama, robot otomatis beristirahat selama **4 jam**.
- **SL+ (Auto-BE) Dihitung Menang:** Jika order terkena Stop Loss di area profit (SL+), sistem mengenalinya sebagai profit dan mereset hitungan loss menjadi 0.
- **Daily Loss Limit:** Maksimal kerugian harian dipatok 2.5% saldo awal hari.

### 4. Friday Weekend Guard (Anti-Gap Akhir Pekan)
- Setiap hari Jumat pukul 21:00 waktu server MT4, EA otomatis menutup semua posisi mengambang dan menolak order baru untuk melindungi modal dari resiko lonjakan Gap harga pembukaan pasar hari Senin.

### 5. Glassmorphic Interactive Dashboard HUD
- Dilengkapi panel modern semi-transparan dengan tombol interaktif **`[ :: GESER ]`** di pojok kanan atas panel. Anda dapat menggeser posisi dashboard ke mana saja di layar chart cukup dengan sekali klik!

### 6. Adaptive Post-Loss Self-Healing & Diagnostic Engine (v2.40 Apex)
- **Otopsi Kerugian Otomatis (Loss Autopsy):** Begitu sebuah order tertutup terkena Stop Loss murni (rugi), robot langsung menjalankan algoritma diagnosis teknis:
  - *Volatilitas Abnormal (News Shock / Spike):* Range lilin penutupan $\ge 2.2 \times$ ATR.
  - *Pembalikan Struktur Makro (Trend Invalidation):* Terjadi CHoCH atau penembusan batas dinamis EMA 125.
  - *Liquidity Sweep Shakeout:* Ekor lilin menyapu area stop sebelum arah bergerak.
  - *Pengujian Level Gagal:* Setup minor kehilangan momentum di zona diskon/premium.
- **3 Aksi Koreksi Diri Mandiri:**
  1. **Penalti Skor Konfluensi:** Ambang skor minimal dinaikkan **+10 Poin** (misal dari 55 menjadi 65), hanya mengeksekusi setup *Grade A+* berikutnya.
  2. **Karantina Pola Gagal (Pattern Quarantine):** Pola candlestick atau chart pattern pemicu kerugian diisolasi selama **15 bar lilin** berikutnya.
  3. **Adaptive SL Buffer Expansion:** Stop Loss diperlebar **+0.3x ATR** untuk **3 transaksi berikutnya** untuk mencegah sapuan ekor lilin.
- **Auto Self-Reset:** Begitu trade berikutnya menang (Take Profit) atau terkunci keuntungan oleh SL+ (Break-Even Lock), seluruh penalti dan karantina otomatis direset ke status normal.
- **Notifikasi Push Otopsi:** Laporan diagnosa dan tindakan koreksi langsung dikirim ke aplikasi MetaTrader HP Anda.

---

## 6. Cara Setting Notifikasi Push ke HP (Android / iPhone)

Robot ini dapat mengirimkan sinyal instan (Entry, TP1, SL+, Circuit Breaker, dan Close Order) langsung ke smartphone Anda:

1. Buka aplikasi **MetaTrader 4** di smartphone Anda.
2. Masuk ke menu **Settings** ➔ **Messages / Notifikasi**.
3. Di sana Anda akan melihat **MetaQuotes ID** (kode unik 8 digit alfanumerik, misal: `12AB34CD`).
4. Buka terminal MT4 di komputer/laptop Anda.
5. Klik menu **Tools** ➔ **Options** ➔ Tab **Notifications**.
6. Centang ☑ **Enable Push notifications**.
7. Masukkan **MetaQuotes ID** HP Anda pada kolom yang disediakan.
8. Klik tombol **Test** untuk memastikan notifikasi masuk ke HP Anda.
9. Klik **OK**. Kini seluruh aksi robot akan dilaporkan secara real-time ke saku Anda!

---

## 7. Tanya Jawab & Troubleshooting Error Umum MT4

### Q1: Apakah EA ini bisa digunakan di broker selain QuickPro?
> **Jawab:** Ya, bisa! Logika lot adaptif kami bekerja universal di broker mana pun (IC Markets, Exness, Didimax, XM, FXOpen, dll.), karena EA selalu membaca batas minimal dan step lot langsung dari server broker.

### Q2: Di pojok kanan atas chart muncul wajah sedih ☹️, kenapa?
> **Jawab:** Itu tanda bahwa AutoTrading belum diizinkan. Tekan **F7** pada chart, buka tab **Common**, dan centang **"Allow live trading"**. Pastikan juga tombol besar **AutoTrading** di toolbar berwarna hijau.

### Q3: Kenapa lot yang terbuka 0.10 padahal di input tertulis 0.01?
> **Jawab:** Berarti akun QuickPro Anda adalah tipe reguler/standar yang batas minimal transaksinya adalah 0.10 lot. EA secara otomatis menyesuaikannya agar order Anda tidak di-reject broker.

### Q4: Apakah dashboard HUD memperlambat kerja MT4?
> **Jawab:** Tidak. Dashboard HUD dioptimalkan dengan timer 250ms dan event listener yang sangat ringan, menjaga latensi eksekusi tetap instan di bawah 5 milidetik.
