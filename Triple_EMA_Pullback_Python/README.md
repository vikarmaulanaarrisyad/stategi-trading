# 🤖 TRIPLE EMA PULLBACK TRADING BOT (PYTHON VERSION)

Robot trading otomatis berbasis **Python 3** dan terintegrasi langsung dengan **MetaTrader 5 (MT5)**. Robot ini mengonversi sistem **EA Triple EMA Pullback (8, 21, 125)** ke dalam arsitektur Python yang modular, cepat, dan mudah dikustomisasi.

---

## 📁 Struktur Folder & Modul

```
Triple_EMA_Pullback_Python/
│
├── config.py             # Konfigurasi parameter strategi, risiko, jam, & simbol
├── indicators.py         # Perhitungan matematis EMA, ATR, dan ADX (Pandas & NumPy)
├── candle_patterns.py    # Engine deteksi 18 pola candlestick rejection (9 Bullish & 9 Bearish)
├── market_structure.py   # Analisis struktur HH/HL, LH/LL, Anti-Chop, Anti-Whipsaw & Overextend
├── strategy.py           # Evaluasi sinyal BUY/SELL & kalkulasi dinamis SL/TP
├── risk_manager.py       # Manajemen risiko: Dynamic Lot, Circuit Breaker, Auto BEP & Trailing Stop
├── mt5_client.py         # Wrapper API MetaTrader5 (Koneksi, eksekusi order, modifikasi, close)
├── backtester.py         # Simulator backtesting bar-by-bar pada data riil broker
├── main.py               # Main loop bot trading live/demo (Auto Trade)
├── requirements.txt      # Daftar dependensi Python
└── README.md             # Buku panduan lengkap
```

---

## ⚡ Cara Menjalankan Robot Trading

### 1. Prasyarat
Pastikan dependensi sudah terinstall:
```bash
pip install -r requirements.txt
```
*(Paket yang dibutuhkan: `metatrader5`, `pandas`, `numpy`)*

### 2. Jalankan Terminal MT5
Buka aplikasi **MetaTrader 5** di komputer/VPS Anda dan pastikan sudah login ke akun demo atau real Anda (misal: PT Didimax Berjangka). Pastikan fitur **Algo Trading** aktif jika diperlukan.

### 3. Jalankan Backtester (Simulasi Historis)
Untuk menguji performa strategi pada data historis broker Anda:
```bash
python backtester.py
```
Robot akan otomatis:
1. Terkoneksi ke terminal MT5 Anda.
2. Mendeteksi simbol yang sesuai (misal: `XAUUSD` otomatis diarahkan ke `XAUUSD.dmb` pada broker Didimax).
3. Mengambil 2,000 candle terakhir pada timeframe M15.
4. Menjalankan simulasi lengkap dengan Auto BEP, Trailing Stop, dan menampilkan laporan Win Rate, Profit Factor, serta Max Drawdown.

## 🖥️ Menjalankan Desktop GUI Terminal (Direkomendasikan)

Tersedia aplikasi **Desktop GUI Modern & Profesional** berbasis **CustomTkinter** dan **Matplotlib** dengan tema dark institutional:

### Cara 1: Menggunakan File Batch (1-Klik)
Cukup klik ganda (*double click*) file:
`e:\Python\STRATEGY\Triple_EMA_Pullback_Python\RUN_DESKTOP_APP.bat`

### Cara 2: Lewat Terminal / Command Prompt
```bash
python gui_app.py
```

### Fitur-Fitur Utama Desktop GUI Terminal:
1. **Header Real-Time & Info Akun**:
   - Status badge robot (`● BOT ACTIVE` / `● BOT PAUSED` / `● STANDBY`).
   - Informasi akun MT5: Nomor Login, Nama Akun, Server Broker, Saldo (*Balance*), dan *Equity*.
2. **Panel Kontrol Parameter Dinamis (Kiri)**:
   - **START / STOP AUTO TRADING**: Tombol aktivasi dan jeda robot.
   - **TUTUP SEMUA POSISI**: Tombol darurat (*emergency panic button*) untuk menutup seluruh order terbuka sekaligus.
   - Pemilihan Simbol (`XAUUSD`) & Timeframe (`M1`, `M5`, `M15`, `M30`, `H1`, `H4`).
   - Mode Lot (`RISK_PERCENT` vs `FIXED`) & input resiko akun.
   - Target Risk:Reward, Auto Break-Even toggle, Trailing Stop EMA 21 toggle, Daily Circuit Breaker toggle, dan Friday Auto-Close toggle.
3. **KPI Metrics Cards (Atas)**:
   - Menampilkan kartu metrik: *Total Equity*, *Saldo Akun*, *Profit Hari Ini*, dan *Jumlah Posisi Terbuka*.
4. **Tab 1: Live Chart & Strategy Telemetry**:
   - **Live Matplotlib Chart**: Menampilkan pergerakan harga real-time, kurva EMA 8 (Cyan), EMA 21 (Oranye), EMA 125 (Hijau), serta shading area *The Value Zone*.
   - **Strategy Telemetry Badges**: Memantau arah tren (di atas/bawah EMA 125), kekuatan tren ADX (14), struktur pasar (HH/HL vs LH/LL), dan pola candlestick yang sedang terdeteksi.
5. **Tab 2: Backtest Simulator Interaktif**:
   - Uji performa historis (500 - 5000 candle) dengan 1 klik tombol.
   - Merender kurva pertumbuhan modal (*Equity Curve Chart*) dan tabel statistik performa (*Win Rate*, *Profit Factor*, *Max Drawdown*, *Net Profit*).
6. **Tab 3: Posisi Terbuka (Active Orders Table)**:
   - Daftar tabel order terbuka lengkap dengan Ticket, Tipe (BUY/SELL), Lot, Harga Open, SL, TP, Floating Profit (\$), dan tombol *Close* per posisi.
7. **Live Execution Log Console (Bawah)**:
   - Terminal log berwarna secara real-time yang mencatat setiap peristiwa trading, trigger BEP, trailing update, dan status evaluasi candle.

---

## ⚡ Cara Menjalankan Versi CLI / Headless (Console Mode)

## ⚙️ Penjelasan Parameter di `config.py`

Anda dapat menyesuaikan seluruh perilaku robot di file [config.py](config.py):

| Parameter | Default | Keterangan |
|---|---|---|
| `symbol` | `"XAUUSD"` | Simbol trading (otomatis mencari akhiran broker seperti `.dmb`). |
| `timeframe` | `"M15"` | Timeframe eksekusi sinyal (`M1`, `M5`, `M15`, `M30`, `H1`, `H4`). |
| `magic_number` | `8821125` | ID unik robot agar tidak mengganggu order manual Anda. |
| `ema_fast_period` | `8` | EMA Cepat pengukur momentum jangka pendek. |
| `ema_med_period` | `21` | EMA Menengah (Dynamic Support / Resistance / The Value Zone). |
| `ema_slow_period` | `125` | EMA Lambat penentu tren makro institusional. |
| `lot_mode` | `"RISK_PERCENT"` | `"RISK_PERCENT"` (% dari Equity) atau `"FIXED"`. |
| `risk_percent` | `1.0` | Resiko per trade (1.0% dari Equity akun). |
| `risk_reward_ratio` | `2.0` | Target Take Profit (1:2.0 Risk:Reward). |
| `use_break_even` | `True` | Otomatis geser SL ke titik impas (BEP) saat profit mencapai 1:1.2 R:R. |
| `use_trailing_stop` | `True` | Trailing stop dinamis mengikuti garis EMA 21 saat profit >= 1:1.4 R:R. |
| `use_daily_loss_limit` | `True` | Circuit Breaker: Stop trading jika kalah 2x berturut-turut dalam 1 hari. |
| `use_time_filter` | `True` | Hanya trading pada jam likuiditas tinggi (08:00 - 21:00). |
| `use_friday_close` | `True` | Menutup otomatis semua posisi Jumat malam (21:30) untuk menghindari weekend gap. |
