# 🌐 Panduan Lengkap: Indikator Institutional SMC & S/R Master (TradingView)
## Support & Resistance Kuat, Auto Fibonacci Golden Zone, BOS/CHoCH, OB & FVG System

Indikator ini ditulis menggunakan **Pine Script v6** (versi resmi terbaru dari TradingView) untuk memberikan visualisasi institusional tingkat lanjut secara real-time pada chart TradingView Anda (cocok untuk **XAUUSD/Gold**, **Forex**, **Crypto**, dan **Saham**).

---

## 💎 1. Fitur Utama Indikator di Chart

1. **Support & Resistance Terkuat & Terbaru Realtime:**
   - **Garis Merah Solid (Major Resistance):** Level resistance tertinggi terkuat berdasarkan swing structural major.
   - **Garis Hijau Solid (Major Support):** Level support terendah terkuat tempat buyer institusi berkumpul.
   - **Garis Putus-Putus (Minor S/R):** Level pantulan terdekat untuk scalping/intraday.
   - **Label Harga Realtime:** Menampilkan nominal harga S/R yang selalu memanjang rapi ke kanan lilin aktif.
2. **Auto Fibonacci Golden Zone (0.50 - 0.618 - 0.65 OTE):**
   - Secara otomatis mendeteksi ayunan harga (*swing high* ke *swing low* aktif).
   - Memetakan kotak arsiran emas (*Golden Pocket*) yang merupakan area **Optimal Trade Entry (OTE)** dengan probabilitas pantulan tertinggi di dunia teknikal.
   - Garis putus-putus rasio emas **61.8%** terpampang jelas sebagai level target entri presisi.
3. **Struktur Pasar (BOS & CHoCH):**
   - **BOS (Break of Structure):** Garis hijau/merah solid saat tren berlanjut menembus swing high/low.
   - **CHoCH (Change of Character):** Garis hijau/merah putus-putus saat terjadi pembalikan tren utama (*major reversal*).
   - Label ayunan harga otomatis: **HH (Higher High)**, **HL (Higher Low)**, **LH (Lower High)**, **LL (Lower Low)**.
4. **Institutional Order Block (OB):**
   - **Kotak Cyan/Biru Muda (Bullish OB / Demand):** Area akumulasi beli institusi.
   - **Kotak Pink/Magenta (Bearish OB / Supply):** Area distribusi jual institusi.
   - **Auto-Clean Mitigated:** Kotak yang sudah tersentuh harga akan otomatis dibersihkan agar chart tetap bersih dan rapi.
5. **Fair Value Gap (FVG / Imbalance):**
   - Mendeteksi celah kosong 3-lilin (imbalance) tempat likuiditas belum terisi.
   - Otomatis terhapus saat gap harga telah terisi penuh (*filled*).
6. **Sinyal Konfirmasi BUY & SELL di Chart (100% Non-Repainting):**
   - **Label Segitiga Hijau "BUY":** Muncul di bawah candle saat konfirmasi pantulan bullish terbentuk di area support/demand/Fibo.
   - **Label Segitiga Merah "SELL":** Muncul di atas candle saat konfirmasi pantulan bearish terbentuk di area resistance/supply/Fibo.
   - **Waktu Trigger:** Default disetel ke **"Selesai Candle (Closed Bar)"** sehingga sinyal **100% TIDAK REPAINT** (tidak akan hilang atau bergeser setelah lilin tertutup).
7. **HUD Dashboard On-Chart (Tabel Realtime):**
   - Status Struktur Pasar (`BULLISH BOS`, `BULLISH CHoCH`, dll).
   - Jarak pips ke Major Resistance terdekat.
   - Jarak pips ke Major Support terdekat.
   - Status posisi harga saat ini terhadap zona Fibo (`IN GOLDEN POCKET!`, `Discount Zone`, atau `Premium Zone`).
   - Jumlah zona Order Block & FVG aktif yang belum termitigasi.
   - **Trade Signal:** Menampilkan status sinyal terkini: **BUY** (hijau), **SELL** (merah), atau **Menunggu** (abu-abu).

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
| **1. Support & Resistance** | `Filter Level S/R` | Pilih **"Hanya S/R Terdekat"**, **"Hanya S/R Terkuat"**, atau **"Tampilkan Keduanya"**. |
| **2. Auto Fibonacci** | `Model Jangkauan` & `Lookback` | Mengatur jangkauan garis Golden Zone dan panjang ayunan swing Fibo. |
| **3. Struktur Pasar** | `Tampilkan BOS & CHoCH` | Menampilkan penembusan struktur dan label swing (HH, HL, LH, LL). |
| **4. Order Block (OB)** | `Pilihan Tampilan OB` | **Default:** **"1 Terdekat (1 Demand + 1 Supply Terdekat)"** agar chart super bersih, atau pilih **"1 Terbaru"** / **"Semua Zona"**. |
| | `Tampilkan Keterangan Teks OB` | Menampilkan label teks nama zona di dalam kotak OB dengan huruf kecil (Default: **Aktif**). |
| **5. Fair Value Gap (FVG)**| `Pilihan Tampilan FVG` | **Default:** **"1 Terdekat (1 Bull + 1 Bear Terdekat)"** atau **"1 Terbaru"** atau **"Nonaktifkan"**. |
| | `Tampilkan Keterangan Teks FVG` | Menampilkan label teks nama zona di dalam kotak FVG dengan huruf kecil (Default: **Aktif**). |
| **6. HUD Dashboard** | `Posisi Dashboard` | Pindahkan tabel ke **Top Left**, **Bottom Left**, atau sembunyikan jika layar sempit. |

| **7. Sinyal Konfirmasi** | `Tampilkan Sinyal di Chart` | Master switch sinyal panah/label di chart (Default: **Hidden / Tersembunyi**). |
| | `Tampilkan Sinyal BUY` | Mengaktifkan / menyembunyikan sinyal BUY di chart (Default: **Hidden / Tersembunyi**). |
| | `Tampilkan Sinyal SELL` | Mengaktifkan / menyembunyikan sinyal SELL di chart (Default: **Hidden / Tersembunyi**). |
| | `Waktu Muncul Sinyal` | **Default:** **"Selesai Candle (Closed Bar - Non Repainting)"** (Sinyal terkunci saat lilin tutup). Pilihan kedua: **"Realtime Saat Candle Berjalan"** (langsung saat harga menyentuh zona). |
| | `Sensitivitas Konfirmasi` | Pilih **"Medium (Standar)"**, **"Tinggi (Lebih Banyak Sinyal)"**, atau **"Ketat (Hanya Setup Valid)"**. |



---

## 🔔 4. Cara Membuat Notifikasi Alert Otomatis

Skrip ini telah dilengkapi fungsi `alertcondition()` bawaan TradingView:
1. Tekan tombol shortcut **`Alt + A`** di TradingView (atau klik ikon jam alarm **Create Alert**).
2. Pada kolom **Condition**, pilih: **`Institutional SMC & S/R Master`**.
3. Pilih jenis sinyal yang ingin Anda pantau:
   - **Institutional BUY Signal:** Memberitahu saat sinyal BUY terkonfirmasi pada lilin yang selesai ditutup.
   - **Institutional SELL Signal:** Memberitahu saat sinyal SELL terkonfirmasi pada lilin yang selesai ditutup.
   - **Bullish / Bearish BOS & CHoCH:** Memberitahu saat terjadi penembusan struktur atau perubahan tren.
   - **Touch Major Support / Resistance:** Memberitahu saat harga menyentuh S/R terkuat.
   - **Enter Golden Zone:** Memberitahu saat harga memasuki area pantulan emas Fibonacci (0.50 - 0.65).
4. Pada opsi **Expiration & Frequency**, pilih **"Once Per Bar Close"** (Satu kali per penutupan lilin) agar alert tidak berulang-ulang.
5. Pilih opsi notifikasi: **Notify on App (Notifikasi HP)**, **Show pop-up**, atau **Send email**.
6. Klik **Create**. Anda akan langsung menerima notifikasi setiap kali sinyal institusional valid terbentuk!

