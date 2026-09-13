# 🌐 Panduan Lengkap: Indikator Institutional SMC & S/R Master (TradingView)
## Support & Resistance Kuat, Auto Fibonacci Golden Zone, BOS/CHoCH, OB & FVG System

Indikator ini ditulis menggunakan **Pine Script v6** (versi resmi terbaru dari TradingView) untuk memberikan visualisasi institusional tingkat lanjut secara real-time pada chart TradingView Anda (cocok untuk **XAUUSD/Gold**, **Forex**, **Crypto**, dan **Saham**).

---

## 💎 1. Fitur Utama Indikator di Chart

1. **Support & Resistance Terkuat & Terbaru Realtime:**
   - **Garis Merah Solid (Major Resistance):** Level resistance tertinggi terkuat berdasarkan swing structural major.
   - **Garis Hijau Solid (Major Support):** Level support terendah terkuat tempat buyer institusi berkumpul.
   - **Garis Putus-Putus (Minor S/R):** Level pantulan terdekat untuk scalping/intraday.
   - **Garis Cyan Putus-putus (RBS - Resistance Became Support):** Resistance yang berhasil ditembus valid otomatis berbalik peran menjadi Support Baru tempat harga bersiap memantul (*bouncing*). Ditandai label `PANTULAN RBS 💎`.
   - **Garis Oranye Putus-putus (SBR - Support Became Resistance):** Support yang berhasil ditembus valid otomatis berbalik peran menjadi Resistance Baru tempat harga bersiap tertolak (*rejection*). Ditandai label `PENOLAKAN SBR 💎`.
   - **Label Harga Realtime:** Menampilkan nominal harga S/R, RBS, dan SBR yang selalu memanjang rapi ke kanan lilin aktif.
2. **Auto Fibonacci Golden Zone (0.50 - 0.618 - 0.65 OTE):**
   - Secara otomatis mendeteksi ayunan harga (*swing high* ke *swing low* aktif).
   - Memetakan kotak arsiran emas (*Golden Pocket*) yang merupakan area **Optimal Trade Entry (OTE)** dengan probabilitas pantulan tertinggi di dunia teknikal.
   - Garis putus-putus rasio emas **61.8%** terpampang jelas sebagai level target entri presisi.
3. **Struktur Pasar (BOS & CHoCH):**
   - **BOS (Break of Structure):** Garis hijau/merah solid saat tren berlanjut menembus swing high/low.
   - **CHoCH (Change of Character):** Garis hijau/merah putus-putus saat terjadi pembalikan tren utama (*major reversal*).
   - Label ayunan harga otomatis: **HH (Higher High)**, **HL (Higher Low)**, **LH (Lower High)**, **LL (Lower Low)**.
4. **Institutional Order Block (OB) - Hanya Ditandai yang Valid A+:**
   - **Filter Validitas A+ Institusional:** Hanya menandai lilin Order Block yang memenuhi syarat baku institusi:
     - **Displacement:** Diikuti lilin ekspansi besar searah tren (ukuran body > 0.85 ATR).
     - **Menciptakan Imbalance / FVG:** Menghasilkan lonjakan harga yang meninggalkan celah likuiditas (FVG) atau **Liquidity Sweep** (menyapu high/low lilin sebelumnya).
     - **Searah Struktur & Hierarki Trend:** Selaras dengan tren EMA atau menembus struktur swing (BOS).
   - **Kotak Cyan/Biru Muda (Bullish OB / Valid Demand):** Area akumulasi beli institusi terverifikasi.
   - **Kotak Pink/Magenta (Bearish OB / Valid Supply):** Area distribusi jual institusi terverifikasi.
   - **Mitigasi Presisi (Mean Threshold 50% & Invalidation):** Kotak tetap aktif dan terlihat saat harga menguji (*retest*) ke dalam zona, dan otomatis dihapus hanya jika ditembus habis atau close melewati batas 50% Mean Threshold.
5. **Fair Value Gap (FVG / Imbalance) - Hanya Ditandai yang Valid:**
   - **Filter Validitas Institusional:** Hanya menandai celah 3-lilin yang benar-benar berkualitas:
     - **Lilin Tengah Impulsif:** Lilin ke-[1] wajib memiliki body dominan (≥ 50% dari total range lilin) dan ukuran range ≥ 0.50 ATR (menghilangkan lilin doji/ragu-ragu).
     - **Lebar Gap Signifikan:** Minimal 20 ticks dan minimal 0.20x ATR (menyaring celah mikro/noise spread).
     - **Searah Tren:** Selaras dengan momentum pasar dan hierarki Triple EMA.
   - **Auto-Clean Mitigated:** Otomatis terhapus rapi saat gap harga telah terisi penuh (*filled*).
6. **Sinyal Konfirmasi BUY & SELL di Chart (100% Non-Repainting):**
   - **Label Segitiga Hijau "BUY":** Muncul di bawah candle saat konfirmasi pantulan bullish terbentuk di area support/demand/Fibo.
   - **Label Segitiga Merah "SELL":** Muncul di atas candle saat konfirmasi pantulan bearish terbentuk di area resistance/supply/Fibo.
   - **Waktu Trigger:** Default disetel ke **"Selesai Candle (Closed Bar)"** sehingga sinyal **100% TIDAK REPAINT** (tidak akan hilang atau bergeser setelah lilin tertutup).
7. **HUD Dashboard On-Chart (Tabel Realtime 10 Baris):**
   - Status Triple EMA & Koreksi Pullback (`BULLISH (8 > 21 > 125)`, `PULLBACK BUY (Peluang! 💎)`, dll).
   - Status Struktur Pasar (`BULLISH BOS`, `BULLISH CHoCH`, dll).
   - Jarak pips ke Major Resistance terdekat.
   - Jarak pips ke Major Support terdekat.
   - Status posisi harga terhadap zona Fibo (`IN GOLDEN POCKET!`, `Discount Zone`, atau `Premium Zone`).
   - Jumlah zona Order Block & FVG aktif yang belum termitigasi.
   - Indikator Keamanan Pasar (*Market Safety Watchdog*).
   - **Realtime Signal (Lilin Aktif Detik Ini):** Menampilkan status formasi pola candle yang sedang bergerak saat ini (misal: `🟢 BUY (Lilin Aktif ⏳: Bullish Engulfing)` atau `🟡 PULLBACK BUY (Menunggu Pola ⏳)`) sehingga trader tidak bingung!
   - **Confirmed Entry:** Menampilkan rekap sinyal entri resmi terakhir yang telah selesai terkonfirmasi.
8. **Live Candle Preview Badge di Chart:**
   - Pada lilin yang sedang bergerak (*live candle*), jika setup sedang terbentuk, muncul label interaktif `⏳ LIVE BUY: [Pola] (Menunggu Close Bar)` sehingga trader dapat bersiap mengeksekusi order dengan percaya diri.

---

## 🚀 2. Cara Memasang Skrip ke TradingView (Langkah demi Langkah)

### Langkah 1: Buka TradingView & Pine Editor
1. Buka situs [TradingView.com](https://www.tradingview.com) di browser atau buka aplikasi **TradingView Desktop**.
2. Buka chart instrumen yang ingin Anda analisa (contoh: **`XAUUSD`**).
3. Di bagian paling bawah layar chart, klik tab bertuliskan **"Pine Editor"**.

---

### Langkah 2: Salin & Tempel Kode Skrip
1. Buka file skrip yang sudah kami buat di komputer Anda:  
   📁 **`e:\Python\STRATEGY\tradingview\Institutional_SMC_SR_Master.pine`**
2. Salin seluruh isi kodenya:
   - Tekan **`Ctrl + A`** (Pilih Semua).
   - Tekan **`Ctrl + C`** (Salin).
3. Kembali ke jendela **Pine Editor** di TradingView:
   - Hapus teks bawaan yang ada di editor tersebut.
   - Tekan **`Ctrl + V`** (Tempel).

---

### Langkah 3: Simpan dan Tambahkan ke Chart
1. Klik tombol **"Save"** (Ikon Disket) di pojok kanan atas Pine Editor.
   - Beri nama skrip, misalnya: **`Institutional SMC & S/R Master`** -> klik **Save**.
2. Klik tombol **"Add to chart"** (Tambahkan ke Chart).
3. Selesai! Indikator akan langsung aktif di chart dengan garis S/R, kotak Fibo Golden Zone, zona OB/FVG, sinyal BUY/SELL, dan tabel HUD Dashboard.

---

## ⚙️ 3. Kustomisasi & Pengaturan (Menu Settings ⚙️)

Anda bisa mengklik dua kali pada garis indikator atau klik ikon **Gear (Settings)** di samping nama indikator pada chart untuk mengatur tampilan sesuai selera:

| Grup Pengaturan | Pilihan Fitur | Fungsi |
|---|---|---|
| **0B. Multi-Timeframe Scalping** | `Wajib Searah Tren H1/H4` | **Default: Aktif**. Mengunci sinyal di M5 agar HANYA muncul jika searah tren utama H1 (atau H4). |
| | `Timeframe Tren Utama` | Pilihan Timeframe HTF (Default: **H1 / 60 Menit** atau bisa diubah ke **240 / H4**). |
| **1. Support & Resistance** | `Filter Level S/R` | Pilih **"Hanya S/R Terdekat"**, **"Hanya S/R Terkuat"**, atau **"Tampilkan Keduanya"**. |
| **2. Auto Fibonacci** | `Model Jangkauan` & `Lookback` | Mengatur jangkauan garis Golden Zone dan panjang ayunan swing Fibo. |
| **3. Struktur Pasar** | `Tampilkan BOS & CHoCH` | Menampilkan penembusan struktur dan label swing (HH, HL, LH, LL). |
| **4. Order Block (OB)** | `Hanya Tandai OB Valid A+` | **Default: Aktif**. Hanya menandai OB berkualitas institusi (Wajib FVG / Liquidity Sweep + Displacement + Trend Alignment). |
| | `Pilihan Tampilan OB` | **Default:** **"1 Terdekat (1 Demand + 1 Supply Terdekat)"** agar chart super bersih, atau pilih **"1 Terbaru"** / **"Semua Zona"**. |
| | `Tampilkan Keterangan Teks OB` | Menampilkan label teks nama zona di dalam kotak OB dengan huruf kecil (Default: **Aktif**). |
| **5. Fair Value Gap (FVG)**| `Hanya Tandai FVG Valid` | **Default: Aktif**. Hanya menandai FVG dengan lilin tengah impulsif dominan & gap signifikan (menghapus celah doji/noise). |
| | `Minimal Lebar Gap FVG` | Batas minimal rasio gap terhadap ATR (Default: **0.20x ATR**). |
| | `Pilihan Tampilan FVG` | **Default:** **"1 Terdekat (1 Bull + 1 Bear Terdekat)"** atau **"1 Terbaru"** atau **"Nonaktifkan"**. |
| | `Tampilkan Keterangan Teks FVG` | Menampilkan label teks nama zona di dalam kotak FVG dengan huruf kecil (Default: **Aktif**). |
| **6. HUD Dashboard** | `Posisi Dashboard` | Pindahkan tabel ke **Top Left**, **Bottom Left**, atau sembunyikan jika layar sempit. |

| **7. Sinyal Konfirmasi** | `Tampilkan Sinyal di Chart` | Master switch sinyal panah/label di chart (Default: **Hidden / Tersembunyi**). |
| | `Tampilkan Sinyal BUY` | Mengaktifkan / menyembunyikan sinyal BUY di chart (Default: **Hidden / Tersembunyi**). |
| | `Tampilkan Sinyal SELL` | Mengaktifkan / menyembunyikan sinyal SELL di chart (Default: **Hidden / Tersembunyi**). |
| | `Waktu Muncul Sinyal` | **Default:** **"Selesai Candle (Closed Bar - Non Repainting)"** (Sinyal terkunci saat lilin tutup). Pilihan kedua: **"Realtime Saat Candle Berjalan"** (langsung saat harga menyentuh zona). |
| **8. Filter Keamanan** | `Filter EMA Sideways` | Menyaring sinyal saat EMA 8 & 21 flat / bolak-balik tanpa tren jelas. |
| | `Filter Whipsaw 125` | Mencegah jebakan sinyal saat harga bolak-balik menembus EMA 125. |
| | `Filter Overextended` | Mencegah entry saat lilin sudah melesat terlalu jauh dari EMA (> 2.2x ATR). |
| **9. Breakout & Fakeout (5 Pilar)** | `Tampilkan Label Valid Breakout` | Label `VALID BREAKOUT 🚀` saat body candle solid menembus S/R dengan volume meningkat. |
| | `Tampilkan Label Fakeout` | Label `FAKEOUT ⚡` saat terjadi wick sweep / penolakan palsu di S/R. |
| | `Filter Volume Breakout` | Wajib volume meningkat (di atas MA 20 atau candle sebelumnya) saat breakout terjadi. |
| | `Wajib Hierarki Ketat` | Wajib susunan EMA 8 > 21 > 125 untuk BUY dan EMA 8 < 21 < 125 untuk SELL. |

---

## 🏛️ 4. Penerapan 5 Aturan Emas Institusional di Skrip

1. **BREAKOUT VALID BUY:**
   - Body candle bullish **close jelas di atas Resistance**.
   - Volume meningkat di atas rata-rata 20 periode.
   - Retrace / koreksi ke area EMA 8 / EMA 21 atau retest ke Resistance yang ditembus.
   - Muncul salah satu dari 9 lilin konfirmasi pantulan bullish.
   - Searah tren utama: `EMA 8 > EMA 21 > EMA 125` dan `Close > EMA 125`.

2. **FALSE BREAKOUT (FAKEOUT WICK SWEEP):**
   - Hanya sumbu lilin (*wick*) yang menembus level S/R, sedangkan body candle **close kembali di dalam level**.
   - Volume melemah / volume kering (*weak volume*).
   - Ditandai langsung dengan label merah maroon `FAKEOUT ⚡ (Wick Rejection)` di chart.

3. **BREAKOUT VALID SELL:**
   - Body candle bearish kuat **close jelas di bawah Support**.
   - Volume transaksi meningkat saat penembusan.
   - Harga berada di bawah EMA 125 dengan `EMA 8 < EMA 21 < EMA 125`.
   - Retrace ke EMA 8/21 atau Support yang ditembus lalu dikonfirmasi pola lilin bearish.

4. **CANDLE BREAK (PENEMBUSAN LEVEL SOLID):**
   - Mengeliminasi penembusan palsu: penembusan hanya diakui sah jika **body candle benar-benar close melewati level S/R / Swing High / Swing Low**.
   - Ekor panjang yang menembus tanpa body close diklasifikasikan sebagai *liquidity grab / fakeout*.

5. **CANDLE KOREKSI (PULLBACK ADALAH PELUANG, BUKAN REVERSAL):**
   - Pada tren Bullish (`Close > EMA 125`, `EMA 8 > EMA 21`), lilin merah yang turun mendekati EMA 8/21 terbaca sebagai **Koreksi Sehat (Pullback)**.
   - HUD Dashboard langsung menampilkan status: `PULLBACK BUY (Peluang! 💎)`.
   - Indikator tidak panik menutup posisi, melainkan mempersiapkan konfirmasi sinyal BUY setelah koreksi tuntas.

---

## 🔔 5. Cara Membuat Notifikasi Alert Otomatis

Skrip ini telah dilengkapi fungsi `alertcondition()` bawaan TradingView:
1. Tekan tombol shortcut **`Alt + A`** di TradingView (atau klik ikon jam alarm **Create Alert**).
2. Pada kolom **Condition**, pilih: **`Institutional SMC & S/R Master`**.
3. Pilih jenis sinyal yang ingin Anda pantau:
   - **Valid Breakout Resistance (BUY):** Alert saat terjadi penembusan valid body candle pada Resistance disertai volume.
   - **Valid Breakout Support (SELL):** Alert saat terjadi penembusan valid body candle pada Support disertai volume.
   - **False Breakout Resistance / Support (Fakeout):** Alert dini saat terjadi jebakan wick sweep.
   - **Triple EMA BUY Signal:** Memberitahu saat sinyal BUY terkonfirmasi pada lilin yang selesai ditutup.
   - **Triple EMA SELL Signal:** Memberitahu saat sinyal SELL terkonfirmasi pada lilin yang selesai ditutup.
   - **Bullish / Bearish BOS & CHoCH:** Memberitahu saat terjadi penembusan struktur atau perubahan tren.
   - **Touch Major Support / Resistance:** Memberitahu saat harga menyentuh S/R terkuat.
   - **Enter Golden Zone:** Memberitahu saat harga memasuki area pantulan emas Fibonacci (0.50 - 0.65).
4. Pada opsi **Expiration & Frequency**, pilih **"Once Per Bar Close"** (Satu kali per penutupan lilin) agar alert tidak berulang-ulang.
5. Pilih opsi notifikasi: **Notify on App (Notifikasi HP)**, **Show pop-up**, atau **Send email**.
6. Klik **Create**. Anda akan langsung menerima notifikasi setiap kali sinyal institusional valid terbentuk!

---

## ⏱️ 6. Protokol Scalping Multi-Timeframe 3 EMA Expert (H1 ➔ M15/M30 ➔ M5)

Strategi ini dirancang dengan pendekatan **Top-Down Multi-Timeframe** yang baku dan teruji untuk scalper profesional:

### 1. Struktur Timeframe Scalping:
- **H1 (Higher Timeframe - Penentu Arah & Bias):**
  - **Tujuan:** Menemukan tren utama dan menentukan arah bias trading hari ini (**HANYA BUY** atau **HANYA SELL**).
  - **Aturan Tren:**
    - Bias **BULLISH:** Jika harga `Close H1 > EMA 125 H1` dan `EMA 8 H1 > EMA 21 H1`. (Trader hanya diizinkan mencari peluang BUY).
    - Bias **BEARISH:** Jika harga `Close H1 < EMA 125 H1` dan `EMA 8 H1 < EMA 21 H1`. (Trader hanya diizinkan mencari peluang SELL).
    - Bias **SIDEWAYS:** Jika EMA saling berhimpit atau lilin bolak-balik EMA 125. (DILARANG trading!).
  - **Otomatisasi di Indikator:** Indikator TradingView secara otomatis menarik data H1 ini melalui fitur **MTF Scalping Bias** dan menampilkannya di baris pertama HUD Dashboard: `HTF Bias [60]: BULLISH 🟢` / `BEARISH 🔴` / `SIDEWAYS ⚪`.

- **M30 / M15 (Intermediate Timeframe - Area Setup & Pullback):**
  - **Tujuan:** Menemukan area diskon/koreksi harga yang ideal (*Value Pocket*).
  - **Area Pantulan:**
    1. Retracement ke pita dinamis **EMA 8 / EMA 21**.
    2. Retest level **RBS (Resistance Became Support)** atau **SBR (Support Became Resistance)**.
    3. Retest zona **Valid Order Block (Demand/Supply)** atau **Valid FVG (Imbalance)**.
    4. Masuk ke **Golden Pocket Fibonacci 0.618 - 0.65 OTE**.
  - **Otomatisasi di Indikator:** HUD Dashboard menampilkan live status `PULLBACK BUY (Peluang! 💎)` atau `PULLBACK SELL (Peluang! 💎)` saat harga memasuki zona ini.

- **M5 (Execution Timeframe - Konfirmasi Lilin & Entry Presisi):**
  - **Tujuan:** Pemicu eksekusi order instan dengan Stop Loss ketat dan akurasi tinggi.
  - **Konfirmasi:** Muncul salah satu dari **9 Pola Candlestick Konfirmasi Institusional** (Engulfing, Pin Bar/Hammer, Morning/Evening Star, Three Soldiers/Crows, Piercing, Tweezer, dll).
  - **Otomatisasi di Indikator:** Sinyal segitiga hijau `BUY ENTRY 🟢` atau merah `SELL ENTRY 🔴` akan muncul di chart M5 **HANYA JIKA** seluruh aturan di H1 dan M15 telah terpenuhi! Trader dapat langsung membuka posisi begitu sinyal muncul!

---

### 📌 4 Catatan Penting Wajib Disiplin:
1. **Selalu Searah Tren H1 / H4:**
   - Jangan pernah mengambil posisi Buy jika H1 Bearish, dan sebaliknya. Indikator TradingView & Robot EA MT5 secara default **MENGUNCI sinyal M5** agar hanya mengikuti arah tren H1.
2. **Jangan Entry Saat Market Sideways:**
   - Jika pasar sedang *ranging* / *chop* (EMA saling silang berdekatan), indikator otomatis mendeteksi bahaya dan memblokir kemunculan sinyal dengan status `⚪ EMA SIDEWAYS (Tidak Ada Entry ⛔)`.
3. **Wajib Tunggu Pullback yang Jelas:**
   - Jangan pernah mengejar harga (*chasing the market*) saat lilin sudah melesat jauh (*overextended*). Tunggu harga mampir ke pita EMA 8/21 atau level S/R.
4. **Wajib Ada Candle Konfirmasi Sebelum Entry:**
   - Jangan menebak-nebak pucuk atau lembah. Sinyal hanya sah jika lilin konfirmasi telah selesai terbentuk dan ditutup (*closed bar*).



