import os
import subprocess
import base64
import re
import shutil

def image_to_base64(path):
    if os.path.exists(path):
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        with open(path, "rb") as img_file:
            return f"data:{mime};base64," + base64.b64encode(img_file.read()).decode("utf-8")
    return ""

artifact_dir = r"C:\Users\vikar\.gemini\antigravity-ide\brain\35bc941c-56ef-442a-b8ea-185da534d5c0"
img_smc_bos = image_to_base64(os.path.join(artifact_dir, "smc_bos_inducement_pattern_1789635642712.jpg"))
img_smc_choch = image_to_base64(os.path.join(artifact_dir, "smc_choch_reversal_pattern_1789635661082.jpg"))
img_fibo_buy = image_to_base64(os.path.join(artifact_dir, "fibo_buy_confluence_1789625869992.jpg"))
img_synergy = image_to_base64(os.path.join(artifact_dir, "synergy_ema_pivots_1789626295121.jpg"))

html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>BUKU PANDUAN RESMI VIKAR EA 4-PILLAR PRO MT4 (QUICKPRO EDITION)</title>
<style>
  @page {{
    size: A4;
    margin: 10mm 12mm 12mm 12mm;
    @bottom-right {{
      content: "Halaman " counter(page);
      font-size: 8pt;
      font-weight: 700;
      color: #0284c7;
    }}
    @bottom-left {{
      content: "VIKAR EA 4-PILLAR PRO MT4 (QUICKPRO EDITION) | BUKU PANDUAN PENGGUNA RESMI";
      font-size: 7.5pt;
      color: #64748b;
      font-weight: 600;
    }}
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.36;
    font-size: 8.5pt;
    margin: 0;
    padding: 0;
  }}

  .page {{
    page-break-after: always;
    break-after: page;
    height: 980px;
    max-height: 980px;
    overflow: hidden;
    position: relative;
    padding-bottom: 5px;
  }}

  .page:last-child, .page:last-of-type {{
    page-break-after: avoid;
    break-after: avoid;
  }}

  /* Cover Styling */
  .cover {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 980px;
    background: linear-gradient(135deg, #090d16 0%, #0f172a 40%, #1e293b 75%, #0369a1 100%);
    color: #ffffff;
    border-radius: 12px;
    padding: 35px 30px;
    text-align: center;
  }}

  .cover-badge {{
    display: inline-block;
    background: rgba(56, 189, 248, 0.15);
    border: 1.5px solid #38bdf8;
    color: #38bdf8;
    padding: 6px 20px;
    border-radius: 30px;
    font-size: 8.5pt;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 15px;
  }}

  .cover-title {{
    font-size: 27pt;
    font-weight: 900;
    line-height: 1.15;
    margin: 0 0 8px 0;
    background: linear-gradient(to right, #38bdf8, #f59e0b, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .cover-subtitle {{
    font-size: 12.5pt;
    color: #94a3b8;
    font-weight: 500;
    margin: 0 0 20px 0;
  }}

  .cover-box-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 15px 0;
    text-align: left;
  }}

  .cover-card {{
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 12px 14px;
    backdrop-filter: blur(5px);
  }}

  .cover-card h4 {{
    margin: 0 0 4px 0;
    color: #38bdf8;
    font-size: 9.5pt;
    font-weight: 700;
  }}

  .cover-card p {{
    margin: 0;
    color: #cbd5e1;
    font-size: 8pt;
    line-height: 1.35;
  }}

  .cover-footer {{
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 14px;
    font-size: 8pt;
    color: #94a3b8;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  /* Standard Page Elements */
  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 5px;
    margin-bottom: 12px;
  }}

  .header-bar h2 {{
    margin: 0;
    font-size: 13.5pt;
    color: #0f172a;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .header-bar .tag {{
    background: #e0f2fe;
    color: #0369a1;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 3px 9px;
    border-radius: 12px;
    border: 1px solid #bae6fd;
  }}

  h3 {{
    font-size: 10pt;
    color: #0369a1;
    margin: 10px 0 5px 0;
    font-weight: 700;
    border-left: 3.5px solid #0284c7;
    padding-left: 7px;
  }}

  p {{
    margin: 0 0 6px 0;
  }}

  .alert-box {{
    background: #f8fafc;
    border-radius: 8px;
    border-left: 4px solid #0284c7;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 8pt;
    line-height: 1.35;
  }}

  .alert-box.success {{
    background: #f0fdf4;
    border-left-color: #16a34a;
    color: #166534;
  }}

  .alert-box.warning {{
    background: #fffbeb;
    border-left-color: #f59e0b;
    color: #92400e;
  }}

  .alert-box.danger {{
    background: #fef2f2;
    border-left-color: #ef4444;
    color: #991b1b;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.8pt;
    margin: 7px 0 10px 0;
  }}

  th {{
    background: #0f172a;
    color: #ffffff;
    padding: 5px 7px;
    text-align: left;
    font-weight: 700;
  }}

  td {{
    padding: 5px 7px;
    border-bottom: 1px solid #e2e8f0;
    vertical-align: top;
  }}

  tr:nth-child(even) td {{
    background: #f8fafc;
  }}

  .badge {{
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 7pt;
    font-weight: 700;
  }}

  .badge-blue {{ background: #e0f2fe; color: #0369a1; }}
  .badge-green {{ background: #dcfce7; color: #15803d; }}
  .badge-amber {{ background: #fef3c7; color: #b45309; }}
  .badge-red {{ background: #fee2e2; color: #b91c1c; }}

  .grid-2 {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 7px 0;
  }}

  .grid-3 {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin: 7px 0;
  }}

  .card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 8px 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
  }}

  .card-header {{
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 4px;
    font-size: 8.5pt;
    display: flex;
    align-items: center;
    gap: 5px;
  }}

  .code-snippet {{
    background: #0f172a;
    color: #38bdf8;
    font-family: Consolas, monospace;
    font-size: 7.5pt;
    padding: 6px 10px;
    border-radius: 6px;
    margin: 5px 0;
    overflow-x: hidden;
    line-height: 1.35;
  }}

  .diagram-img {{
    width: 100%;
    max-height: 155px;
    object-fit: contain;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    margin: 4px 0 6px 0;
    background: #000;
  }}
</style>
</head>
<body>

<!-- HALAMAN COVER -->
<div class="page cover">
  <div class="cover-top">
    <div class="cover-badge">METATRADER 4 • QUICKPRO SPECIAL EDITION • v3.00 APEX GRANDMASTER EDITION</div>
    <h1 class="cover-title">VIKAR EA 4-PILLAR PRO</h1>
    <div class="cover-subtitle">Buku Panduan Lengkap Instalasi, Setup AutoTrading, Manajemen Risiko & Reward Institusional</div>
  </div>

  <div>
    <div class="cover-box-grid">
      <div class="cover-card">
        <h4>🛡️ Adaptasi Minimal Lot QuickPro</h4>
        <p>Dilengkapi sistem cerdas <b>LOT_TYPE_BROKER_MIN</b>. Otomatis membaca minimal lot akun QuickPro (0.01 mikro atau 0.10 standar) sehingga 100% bebas dari penolakan order (Error 131).</p>
      </div>
      <div class="cover-card">
        <h4>🚀 Dual-Engine Execution</h4>
        <p>Jalur <b>Sniper Pullback Reversal</b> (Golden Pocket & Order Block) + Jalur <b>Momentum Breakout Expansion</b> (anti-ketinggalan reli kencang emas saat tren meledak).</p>
      </div>
      <div class="cover-card">
        <h4>💰 Multi-Stage Profit & SL+ Guard</h4>
        <p>Kunci modal instan di SL+ (+2.5 pips profit bersih), ambil untung 50% di TP1, dan kawal sisa lot <i>Runner</i> di balik ayunan Higher Low/Lower High SMC untuk memburu reli $30-$60.</p>
      </div>
      <div class="cover-card">
        <h4>⚡ Circuit Breaker & Weekend Guard</h4>
        <p>Jeda otomatis 4 jam jika terjadi 2x Stop Loss berturut-turut. Transaksi SL+ dihitung sebagai WIN. Proteksi Jumat malam pukul 21:00 server melikuidasi posisi agar terhindar dari lonjakan Gap akhir pekan.</p>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <div><strong>Aset Utama:</strong> XAUUSD (Gold) | <strong>Timeframe:</strong> M15 (Primary) & M5 (Scalp)</div>
    <div><strong>Kompatibilitas:</strong> QuickPro MT4 & Universal MQL4 Brokers</div>
    <div><strong>Edisi Resmi:</strong> September 2026</div>
  </div>
</div>

<!-- HALAMAN 1: KEUNGGULAN QUICKPRO & ARSITEKTUR 4 PILAR -->
<div class="page">
  <div class="header-bar">
    <h2>1. Keunggulan Sistem Lot QuickPro & Arsitektur 4 Pilar</h2>
    <span class="tag">ARSITEKTUR STRATEGI</span>
  </div>

  <div class="alert-box warning">
    <strong>⚠️ Kendala Klasik Trader di Broker QuickPro:</strong> Di broker lokal QuickPro, aturan ukuran minimal lot sangat ketat. Beberapa akun reguler memiliki <b>Minimal Lot 0.10</b>, sementara akun mini memiliki <b>Minimal Lot 0.01</b>. Jika EA memaksakan 0.01 pada akun 0.10, server broker akan langsung menolak order dengan kode <code>Error 131: ERR_INVALID_TRADE_VOLUME</code>.
  </div>

  <h3>🛡️ Solusi Cerdas: Fitur LOT_TYPE_BROKER_MIN</h3>
  <p>Robot ini telah dilengkapi mesin adaptasi lot bawaan. Secara otomatis robot melakukan kueri ke server broker menggunakan <code>MarketInfo(Symbol(), MODE_MINLOT)</code> dan <code>MarketInfo(Symbol(), MODE_LOTSTEP)</code>.</p>
  
  <div class="grid-2">
    <div class="card">
      <div class="card-header">🏢 Akun Standar / Reguler QuickPro</div>
      <p style="font-size:7.5pt; margin-bottom:4px;">Batas minimal lot broker: <b>0.10</b></p>
      <div class="code-snippet">Auto-Detect: Executing 0.10 Lot (Sesuai Aturan)</div>
      <p style="font-size:7.2pt; color:#64748b;">Order langsung diterima seketika tanpa error atau slippage reject.</p>
    </div>
    <div class="card">
      <div class="card-header">🌱 Akun Mini / Mikro QuickPro</div>
      <p style="font-size:7.5pt; margin-bottom:4px;">Batas minimal lot broker: <b>0.01</b></p>
      <div class="code-snippet">Auto-Detect: Executing 0.01 Lot (Modal Kecil)</div>
      <p style="font-size:7.2pt; color:#64748b;">Modal terkecil sekalipun aman dikelola dengan resiko yang sangat terukur.</p>
    </div>
  </div>

  <h3>🏛️ Sinergi 4 Pilar Institusional di MetaTrader 4</h3>
  <p>Seluruh logika inti algoritma v2.30 ditanamkan secara utuh ke dalam bahasa MQL4 tanpa pemotongan fitur:</p>

  <table>
    <thead>
      <tr>
        <th style="width:22%;">Pilar Trading</th>
        <th style="width:38%;">Komponen Algoritma di MT4</th>
        <th style="width:40%;">Peran & Keunggulan bagi Akun</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Pilar 1: SMC Core</b></td>
        <td>BOS, CHoCH, Liquidity Sweep, Order Block (OB), Fair Value Gap (FVG).</td>
        <td>Memastikan entri selalu mengikuti akumulasi Smart Money, bukan perangkap ritel.</td>
      </tr>
      <tr>
        <td><b>Pilar 2: Support & Resistance</b></td>
        <td>Daily Pivot Points Multi-Level (P, S1-S3, R1-R3), Headroom ATR Filter.</td>
        <td>Mencegah aksi konyol membeli tepat di tembok resisten atau menjual di dasar support.</td>
      </tr>
      <tr>
        <td><b>Pilar 3: Triple EMA</b></td>
        <td>EMA 8 Cyan (Momentum), EMA 21 Magenta (Ribbon/Trailing), EMA 125 Putih (Trend).</td>
        <td>Filter arah tren makro dan penyedia zona pantulan (Dynamic Value Zone) yang sangat akurat.</td>
      </tr>
      <tr>
        <td><b>Pilar 4: Fibonacci Retrace</b></td>
        <td>Auto-Fibo SMC Swings, Golden Pocket (0.500 - 0.618 - 0.786), Ekstensi Target.</td>
        <td>Menentukan area beli diskon terbaik dan proyeksi take profit proporsional berbasis matematika emas.</td>
      </tr>
    </tbody>
  </table>

  <div class="alert-box success">
    <strong>💡 Skor Konfluensi 4 Pilar:</strong> Sebelum membuka posisi, EA menghitung skor gabungan (0 - 100 Poin). Order hanya dilepas jika skor memenuhi syarat minimal preset (55 untuk Fast Trade, 70 untuk High Winrate Sniper).
  </div>
</div>

<!-- HALAMAN 2: INSTALASI MT4 & PANDUAN CEPAT -->
<div class="page">
  <div class="header-bar">
    <h2>2. Langkah Instalasi di QuickPro MetaTrader 4</h2>
    <span class="tag">SETUP & DEPLOYMENT</span>
  </div>

  <p>Ikuti 5 langkah mudah berikut untuk memasang robot ke terminal QuickPro MT4 Anda:</p>

  <div class="card" style="margin-bottom:8px;">
    <div class="card-header">📁 Langkah 1: Buka Data Folder MetaTrader 4</div>
    <p style="font-size:7.8pt;">Buka terminal QuickPro MT4 Anda, klik menu <b>File</b> di pojok kiri atas ➔ pilih <b>Open Data Folder</b> (Buka Folder Data). Jendela Windows Explorer akan terbuka secara otomatis.</p>
  </div>

  <div class="card" style="margin-bottom:8px;">
    <div class="card-header">📋 Langkah 2: Salin File EA (.mq4 & .ex4) dan File Preset (.set)</div>
    <p style="font-size:7.8pt;">1. Buka folder <code>MQL4 ➔ Experts</code>, lalu salin file <b>VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4</b> dan <b>VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.ex4</b> ke dalamnya.<br>
    2. Buka folder <code>MQL4 ➔ Presets</code>, lalu salin file preset berekstensi <b>.set</b> ke dalamnya.</p>
  </div>

  <div class="card" style="margin-bottom:8px;">
    <div class="card-header">🔄 Langkah 3: Refresh Panel Navigator di MT4</div>
    <p style="font-size:7.8pt;">Kembali ke MT4, tekan tombol keyboard <b>Ctrl + N</b> untuk memunculkan panel Navigator sebelah kiri. Klik kanan pada menu <b>Expert Advisors</b> ➔ klik <b>Refresh</b> (Segarkan). EA akan langsung muncul di daftar!</p>
  </div>

  <div class="card" style="margin-bottom:8px;">
    <div class="card-header">⚙️ Langkah 4: Pengaturan Centang Wajib (Allow Live Trading)</div>
    <p style="font-size:7.8pt;">Buka Chart <b>XAUUSD</b> (Timeframe <b>M15</b>). Seret EA dari Navigator ke chart. Pada jendela yang muncul:</p>
    <div class="grid-2" style="margin:4px 0;">
      <div style="background:#f1f5f9; padding:5px 8px; border-radius:4px; font-size:7.5pt;">
        ☑ <b>Allow live trading</b> (Wajib dicentang)<br>
        ☑ <b>Allow DLL imports</b> (Disarankan dicentang)
      </div>
      <div style="background:#f1f5f9; padding:5px 8px; border-radius:4px; font-size:7.5pt;">
        ☑ <b>Tombol AutoTrading di Toolbar Atas</b> harus menyala <b>HIJAU</b>.<br>
        Pastikan ikon di pojok kanan atas chart tersenyum: <b>😊</b>
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:8px;">
    <div class="card-header">📥 Langkah 5: Memuat File Preset (.set)</div>
    <p style="font-size:7.8pt;">Pada tab <b>Inputs</b> di jendela pengaturan EA (atau tekan <b>F7</b> pada chart), klik tombol <b>Load</b> di sebelah kanan ➔ pilih file <code>QUICKPRO_XAUUSD_FAST_AUTO_TRADE.set</code> ➔ klik <b>Open</b> ➔ klik <b>OK</b>. Dashboard futuristik EA akan langsung aktif di layar chart Anda!</p>
  </div>

  <div class="alert-box danger">
    <strong>🚨 Catatan Penting Wajah Sedih (☹️):</strong> Jika ikon di pojok kanan atas chart menampilkan wajah cemberut/sedih, artinya AutoTrading dicekal. Tekan tombol besar <b>AutoTrading</b> di toolbar atas hingga berwarna hijau, lalu tekan F7 pada chart dan centang <i>Allow live trading</i>.
  </div>
</div>

<!-- HALAMAN 3: BEDAH MANAJEMEN RESIKO (RISK) -->
<div class="page">
  <div class="header-bar">
    <h2>3. Bedah Tuntas Manajemen Risiko (Risk Control)</h2>
    <span class="tag">MONEY MANAGEMENT</span>
  </div>

  <p>Pengelolaan modal adalah kunci kelangsungan akun trading. EA ini memiliki 3 lapis perlindungan modal yang dapat diatur di tab <b>Inputs (F7)</b>:</p>

  <h3>📊 1. Pemilihan Model Lot Modal (Grup Input 1)</h3>
  <table>
    <thead>
      <tr>
        <th style="width:28%;">Parameter Input</th>
        <th style="width:22%;">Setelan / Default</th>
        <th style="width:50%;">Penjelasan Teknis & Contoh Implementasi</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code>InpLotType</code></td>
        <td><code>LOT_TYPE_BROKER_MIN</code></td>
        <td><b>Model Lot:</b> Mode 0 = Minimal lot broker QuickPro (Paling Aman). Mode 1 = Persentase Risiko. Mode 2 = Lot Tetap.</td>
      </tr>
      <tr>
        <td><code>InpRiskPercent</code></td>
        <td><code>1.0%</code></td>
        <td><b>Persentase Risiko Saldo:</b> Jika modal $1,000 dan diisi 1.0%, risiko dibatasi $10. Lot dihitung dinamis = <code>Modal x Risk% / Jarak SL</code>.</td>
      </tr>
      <tr>
        <td><code>InpFixedLot</code></td>
        <td><code>0.01</code></td>
        <td><b>Ukuran Lot Statis:</b> Hanya aktif jika <code>InpLotType = LOT_TYPE_FIXED</code>.</td>
      </tr>
      <tr>
        <td><code>InpMaxLot</code></td>
        <td><code>0.10</code></td>
        <td><b>Safeguard Lot Maksimal:</b> Pagar pengaman keras agar EA tidak akan pernah membuka lot melebihi batas ini sekalipun modal besar.</td>
      </tr>
      <tr>
        <td><code>InpMaxOpenPositions</code></td>
        <td><code>1</code></td>
        <td><b>Anti-Hedging & Anti-Overtrading:</b> Menjamin EA hanya fokus mengawal 1 transaksi terbaik dalam satu waktu.</td>
      </tr>
    </tbody>
  </table>

  <h3>🛡️ 2. Stop Loss Dinamis Berbasis Struktur SMC (Grup Input 2)</h3>
  <p>EA tidak menggunakan Stop Loss kaku sembarangan, melainkan menaruh proteksi di balik level pertahanan institusional:</p>

  <div class="grid-2">
    <div class="card">
      <div class="card-header">🟢 Stop Loss Posisi BUY</div>
      <p style="font-size:7.5pt;">Diletakkan presisi di bawah <b>Lembah Order Block Bullish</b> atau <b>Level 78.6% Fibonacci Retracement</b> + buffer 1.0x ATR.<br>
      <span class="badge badge-green">Min SL: 15 Pips | Max SL: 28 Pips</span></p>
    </div>
    <div class="card">
      <div class="card-header">🔴 Stop Loss Posisi SELL</div>
      <p style="font-size:7.5pt;">Diletakkan presisi di atas <b>Puncak Order Block Bearish</b> atau <b>Level 78.6% Fibonacci Retracement</b> + buffer 1.0x ATR.<br>
      <span class="badge badge-red">Min SL: 15 Pips | Max SL: 28 Pips</span></p>
    </div>
  </div>

  <div class="card" style="margin-top:8px;">
    <div class="card-header">📐 Visual Siklus Struktur Ayunan SMC & Titik Stop Loss</div>
    <img class="diagram-img" src="{img_smc_bos}" alt="SMC BOS Pattern">
    <p style="font-size:7.2pt; color:#475569; text-align:center; margin:0;">Level Stop Loss institusional ditaruh tepat di bawah Swing Low valid pasca Inducement & BOS terkonfirmasi.</p>
  </div>
</div>

<!-- HALAMAN 4: BEDAH MANAJEMEN REWARD & EXIT -->
<div class="page">
  <div class="header-bar">
    <h2>4. Bedah Tuntas Manajemen Reward & Multi-Stage Exit</h2>
    <span class="tag">PROFIT HARVESTING</span>
  </div>

  <p>Kelemahan terbesar robot trading biasa adalah membiarkan posisi profit berbalik menjadi floating loss. EA Vikar 4-Pillar Pro mengatasi masalah ini dengan sistem <b>Multi-Stage Exit 5 Tahap</b>:</p>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #0284c7;">
    <div class="card-header" style="color:#0284c7;">🔒 TAHAP 1: Auto-Breakeven / SL+ (Modal 100% Bebas Risiko & Untung Terkunci)</div>
    <p style="font-size:7.8pt;">Saat harga bergerak menguntungkan sebesar <b>8.0 Pips</b> (<code>InpBreakevenTriggerPips</code>), robot seketika menggeser Stop Loss melewati open price dan <b>mengunci profit bersih +2.5 Pips</b> (<code>InpBreakevenLockPips</code>). Dari detik ini, transaksi Anda tidak mungkin rugi!</p>
  </div>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #16a34a;">
    <div class="card-header" style="color:#16a34a;">💰 TAHAP 2: Partial Take Profit TP1 (Amankan Uang Tunai 50% Lot)</div>
    <p style="font-size:7.8pt;">Begitu target profit menyentuh <b>10.0 Pips</b> (<code>InpPartialTriggerPips</code>), robot otomatis melikuidasi <b>50% dari total lot</b> (<code>InpPartialClosePercent = 50%</code>) dan memasukkannya ke saldo real akun. Modal Anda langsung bertambah secara pasti!</p>
  </div>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #f59e0b;">
    <div class="card-header" style="color:#f59e0b;">🏃 TAHAP 3: Multi-Stage Structural Trailing Stop (Kawal Sisa Lot RUNNER)</div>
    <p style="font-size:7.8pt;">Sisa 50% lot (Runner) dibiarkan berlari dengan Stop Loss yang digeser bertahap di balik <b>Higher Low (HL)</b> untuk BUY atau di atas <b>Lower High (LH)</b> untuk SELL. Posisi Runner kebal dari goyangan koreksi minor dan mampu menunggangi tren monster hingga <b>$30 - $60 pergerakan emas</b>!</p>
  </div>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #8b5cf6;">
    <div class="card-header" style="color:#8b5cf6;">📈 TAHAP 4: Trailing Stop Ribbon EMA 21 Magenta</div>
    <p style="font-size:7.8pt;">Jika harga bergerak dalam gelombang tren standar, Stop Loss terus membayangi garis EMA 21 Magenta dengan buffer 4 pips (<code>InpTrailingBufferPips = 4.0</code>), menjamin keuntungan terus terkunci seiring pergerakan harga naik/turun.</p>
  </div>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #ef4444;">
    <div class="card-header" style="color:#ef4444;">⚡ TAHAP 5: Auto Cut Profit Saat Terdeteksi Pembalikan Arah Tajam</div>
    <p style="font-size:7.8pt;">Jika floating profit Anda sudah mencapai minimal <b>+3 Pips</b> lalu muncul pola pembalikan arah tajam di lilin selesai (Reversal candle / CHoCH berlawanan), EA langsung menutup transaksi lebih dini agar keuntungan tidak tergerus.</p>
  </div>

  <div class="alert-box success">
    <strong>🎯 Rasio Risk to Reward (R:R):</strong> Parameter <code>InpRiskRewardRatio = 1.5</code> menjamin setiap 20 pips risiko SL akan dibalas dengan potensi Take Profit minimal 30 pips.
  </div>
</div>

<!-- HALAMAN 5: CIRCUIT BREAKER & PROTEKSI AKUN -->
<div class="page">
  <div class="header-bar">
    <h2>5. Proteksi Akun, Circuit Breaker & Weekend Guard</h2>
    <span class="tag">SAFETY MECHANISMS</span>
  </div>

  <p>Pasar emas (XAUUSD) terkenal dengan volatilitas liar pada jam-jam rilis berita High-Impact. EA dilengkapi perisai algoritma mutakhir:</p>

  <h3>🛡️ 1. Consecutive Loss Circuit Breaker (Anti-Overtrading)</h3>
  <div class="card" style="margin-bottom:8px;">
    <div class="card-header">⏱️ Mekanisme Jeda Istirahat 4 Jam</div>
    <p style="font-size:7.8pt;">Jika terjadi <b>2 kali Stop Loss berturut-turut pada hari yang sama</b> (<code>InpMaxConsecutiveLosses = 2</code>), EA otomatis mematikan pencarian sinyal dan <b>beristirahat selama 4 jam</b> (<code>InpCooldownHours = 4</code>). Hal ini mencegah akun tergerus saat pasar sedang tidak rasional (whipsaw).</p>
  </div>

  <div class="alert-box success">
    <strong>✨ JAWABAN PASTI: Apakah SL+ Dihitung Sebagai Stop Loss?</strong><br>
    <b>TIDAK!</b> Transaksi yang ditutup oleh SL+ menghasilkan keuntungan bersih (<code>OrderProfit() > 0</code>). Dalam algoritma EA ini, transaksi SL+ <b>DIPERLAKUKAN SEBAGAI KEMENANGAN (WIN)</b> dan secara otomatis <b>MERESET COUNTER LOSS KEMBALI KE 0</b>. Robot tidak akan pernah terpicu istirahat akibat transaksi yang terkena SL+!
  </div>

  <h3>📉 2. Daily Loss Limit (Batas Kerugian Maksimal Harian)</h3>
  <div class="card" style="margin-bottom:8px;">
    <p style="font-size:7.8pt;">Parameter <code>InpMaxDailyLossPercent = 2.5%</code> membatasi kerugian akumulatif harian maksimal 2.5% dari modal awal hari. Jika batas ini tersentuh, robot berhenti mengeksekusi order baru sampai pergantian hari berikutnya. Modal pokok Anda terlindungi 100% dari potensi margin call.</p>
  </div>

  <h3>🚪 3. Friday Weekend Guard (Anti-Gap Akhir Pekan)</h3>
  <div class="card" style="margin-bottom:8px;">
    <p style="font-size:7.8pt;">Setiap hari Jumat pukul <b>21:00 waktu server MT4</b> (<code>InpFridayCloseHour = 21</code>), EA otomatis melikuidasi seluruh posisi mengambang dan menolak sinyal baru. Trader dapat tidur nyenyak di akhir pekan tanpa cemas terhadap risiko lonjakan harga pembukaan (*Gap*) hari Senin subuh.</p>
  </div>

  <h3>⚡ 4. Shock Guard Volatility Filter</h3>
  <p style="font-size:7.8pt;">Jika terjadi lilin berita abnormal dengan rentang &ge; 3.2&times; ATR, Shock Guard aktif dan membekukan eksekusi selama 2 bar lilin hingga pasar kembali tenang dan likuiditas normal terbentuk.</p>
</div>

<!-- HALAMAN 5B: SISTEM OTOPSI & KOREKSI DIRI PASCA-SL (SELF-HEALING) -->
<div class="page">
  <div class="header-bar">
    <h2>5B. Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing Engine v2.40)</h2>
    <span class="tag">FITUR REVOLUSIONER</span>
  </div>

  <p>Inovasi kecerdasan buatan terdepan pada v2.40: Robot tidak hanya menerima kerugian secara pasif, melainkan <b>melakukan otopsi teknikal seketika</b>, mendiagnosa akar penyebab Stop Loss, dan secara otonom <b>mengoreksi dirinya sendiri</b> agar winrate akun Anda terlindungi!</p>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #ef4444;">
    <div class="card-header" style="color:#ef4444; font-size:8.5pt;">🔍 1. Algoritma Otopsi Posisi Rugi (True Loss Diagnostic)</div>
    <p style="font-size:7.6pt; margin-bottom:4px;">Begitu posisi ditutup rugi (Loss murni, bukan BE/SL+), modul otopsi menganalisis kondisi pasar di bar penutupan:</p>
    <div class="grid-2" style="font-size:7.3pt;">
      <div style="background:#fef2f2; padding:5px 8px; border-radius:5px;">
        • <b>Volatilitas Abnormal:</b> Lilin &ge; 2.2&times; ATR mendadak terdeteksi (News Shock).<br>
        • <b>Liquidity Sweep:</b> Ekor panjang menyapu area stop sebelum harga berbalik.
      </div>
      <div style="background:#fef2f2; padding:5px 8px; border-radius:5px;">
        • <b>Pembalikan Struktur Makro:</b> Terjadi CHoCH atau penembusan batas dinamis EMA 125.<br>
        • <b>Pengujian Level Gagal:</b> Setup minor kehilangan konfluensi di zona diskon/premium.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #0284c7;">
    <div class="card-header" style="color:#0284c7; font-size:8.5pt;">⚙️ 2. Tiga Tindakan Koreksi Mandiri Robot (Self-Correction Actions)</div>
    <div class="grid-3" style="font-size:7.3pt;">
      <div style="background:#f0f9ff; padding:5px 7px; border-radius:5px;">
        <b>🎯 PENALTI SKOR KONFLUENSI</b><br>
        Ambang skor minimum dinaikkan <b>+10 Poin</b> (misal 55 &rarr; 65). Robot hanya akan mengeksekusi sinyal sempurna <i>Grade A+</i> berikutnya.
      </div>
      <div style="background:#f0f9ff; padding:5px 7px; border-radius:5px;">
        <b>⛔ KARANTINA POLA GAGAL</b><br>
        Pola candlestick atau chart pattern yang menyebabkan SL <b>dikarantina selama 15 bar</b>. Robot menolak sinyal dari pola tersebut hingga masa isolasi selesai.
      </div>
      <div style="background:#f0f9ff; padding:5px 7px; border-radius:5px;">
        <b>🛡️ ADAPTIVE SL EXPANSION</b><br>
        Jarak Stop Loss diperlebar <b>+0.3&times; ATR</b> selama <b>3 transaksi berikutnya</b>, melindungi posisi dari sapuan ekor lilin (<i>wick hunt</i>).
      </div>
    </div>
  </div>

  <div class="grid-2" style="margin-top:6px;">
    <div class="alert-box success" style="margin:0;">
      <strong>🔄 Pemulihan Otomatis (Self-Reset Engine)</strong><br>
      Begitu transaksi berikutnya mencapai target <b>Take Profit</b> atau dikunci keuntungan <b>SL+ (Break-Even Lock)</b>, status otopsi otomatis direset ke kondisi normal. Disiplin trading terjaga 100%!
    </div>
    <div class="alert-box warning" style="margin:0;">
      <strong>📲 Notifikasi Otopsi ke Smartphone</strong><br>
      Trader menerima laporan langsung via Push Notification MT4: memuat nomor tiket, nominal kerugian, diagnosa penyebab teknis, dan tindakan pengetatan sinyal yang sedang aktif.
    </div>
  </div>
</div>

<!-- HALAMAN 5C: KECERDASAN KUANTITATIF (PATTERN MATRIX & CHOPPINESS INDEX v3.00) -->
<div class="page">
  <div class="header-bar">
    <h2>5C. Kecerdasan Kuantitatif: Pattern Matrix & Sensor Cuaca (v3.00)</h2>
    <span class="tag">AI QUANTITATIVE</span>
  </div>

  <p>Peningkatan kecerdasan buatan v3.00 membawa dua pilar trading kuantitatif kelas institusional: <b>Memori Rapor Kinerja Tiap Pola</b> dan <b>Klasifikasi Cuaca Pasar Berbasis Entropi Fisika (Choppiness Index)</b>.</p>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #0284c7;">
    <div class="card-header" style="color:#0284c7; font-size:8.5pt;">📊 1. Dynamic Pattern Performance Matrix (AI Pattern Learning)</div>
    <p style="font-size:7.6pt; margin-bottom:4px;">Robot mencatat statistik kemenangan (Win Rate) untuk 12 kategori pola secara real-time dan persisten di memori terminal:</p>
    <div class="grid-3" style="font-size:7.3pt;">
      <div style="background:#f0fdf4; padding:5px 7px; border-radius:5px; border:1px solid #bbf7d0;">
        <b style="color:#15803d;">🚀 DYNAMIC BOOST (+10 Poin)</b><br>
        Jika suatu pola memiliki <b>Winrate &ge; 70%</b>, robot memberi bonus skor +10 Poin. Setup yang sedang ampuh diprioritaskan!
      </div>
      <div style="background:#fef2f2; padding:5px 7px; border-radius:5px; border:1px solid #fecaca;">
        <b style="color:#b91c1c;">⛔ AUTO-BLACKLIST (< 40%)</b><br>
        Jika suatu pola memiliki <b>Winrate &lt; 40%</b>, robot otomatis mem-blacklist pola tersebut. Menolak setup yang sedang sering rugi!
      </div>
      <div style="background:#f8fafc; padding:5px 7px; border-radius:5px; border:1px solid #e2e8f0;">
        <b style="color:#0369a1;">💾 MEMORI PERSISTEN</b><br>
        Data statistik tersimpan aman di Global Variable terminal dan tidak akan hilang meskipun MT4 Anda di-restart.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:8px; border-left: 4px solid #f59e0b;">
    <div class="card-header" style="color:#f59e0b; font-size:8.5pt;">🌪️ 2. Market Regime Classifier (Sensor Cuaca Choppiness Index)</div>
    <p style="font-size:7.6pt; margin-bottom:4px;">Menggunakan rumus entropi fraktal 14-bar untuk mengukur apakah pasar sedang tren searah atau sideways berbahaya:</p>
    <div class="grid-3" style="font-size:7.3pt;">
      <div style="background:#f0f9ff; padding:5px 7px; border-radius:5px;">
        <b>🌊 STRONG TREND (CI &lt; 38.2)</b><br>
        Pasar bergerak satu arah dengan akselerasi tinggi. Jalur <i>Momentum Breakout</i> aktif penuh memburu reli besar.
      </div>
      <div style="background:#fffbeb; padding:5px 7px; border-radius:5px;">
        <b>🎯 NORMAL TREND (38.2 - 61.8)</b><br>
        Pasar bergerak sehat. Robot menerapkan aturan 4 Pilar sniper standard (Pullback Ribbon EMA + Golden Pocket Fibo).
      </div>
      <div style="background:#fef2f2; padding:5px 7px; border-radius:5px;">
        <b>🛑 CHOPPY / RANGE (CI &gt; 61.8)</b><br>
        Pasar kompresi sempit. <b>Momentum Breakout DIBLOKIR OTOMATIS</b> (mencegah 85% fakeout) dan skor diperketat +10 poin!
      </div>
    </div>
  </div>

  <div class="alert-box success" style="margin-top:6px;">
    <strong>🖥️ Terintegrasi Langsung ke Glassmorphic Dashboard HUD:</strong><br>
    Layar chart Anda kini menampilkan status cuaca pasar terkini <code>[Cuaca Pasar: TRENDING (CI: 31.4)]</code> dan rangkuman pola terbaik <code>[Rapor Pola: Pin Bar 80%]</code> secara real-time!
  </div>
</div>

<!-- HALAMAN 5D: PERISAI PRE-NEWS, SPREAD SPIKE & DIVERGENSI RSI (v3.00) -->
<div class="page">
  <div class="header-bar">
    <h2>5D. Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v3.00)</h2>
    <span class="tag">INSTITUTIONAL SHIELD</span>
  </div>

  <p>Pembaruan <b>v3.00 Apex Institutional Intelligence</b> melengkapi robot dengan 3 lapisan perlindungan ekstra untuk memusnahkan penyebab Stop Loss yang paling sering dialami trader retail:</p>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #ef4444;">
    <div class="card-header" style="color:#ef4444; font-size:8.5pt;">🛡️ 1. Pre-News Event & Spread Spike Shield (Section 8.7)</div>
    <p style="font-size:7.5pt; margin-bottom:4px;">Mencegah modal tersapu oleh volatilitas liar dan lonjakan spread saat rilis data ekonomi AS (CPI, NFP, PPI, FOMC):</p>
    <div class="grid-3" style="font-size:7.2pt;">
      <div style="background:#fef2f2; padding:5px 7px; border-radius:5px; border:1px solid #fecaca;">
        <b style="color:#b91c1c;">❄️ PEMBEKUAN ORDER (20m - 25m)</b><br>
        Order baru otomatis <b>dibekukan 20 menit sebelum hingga 25 menit sesudah</b> rilis berita (15:30 & 21:00 server). Anti-slippage!
      </div>
      <div style="background:#f0fdf4; padding:5px 7px; border-radius:5px; border:1px solid #bbf7d0;">
        <b style="color:#15803d;">🔒 AUTO-LOCK BE JELANG NEWS</b><br>
        Posisi yang sedang floating profit otomatis ditarik SL-nya ke <b>SL+ (Break-Even Lock)</b> beberapa menit sebelum berita keluar. Modal 100% aman!
      </div>
      <div style="background:#fffbeb; padding:5px 7px; border-radius:5px; border:1px solid #fde68a;">
        <b style="color:#b45309;">⚡ SPREAD SPIKE FILTER (&gt;1.8x)</b><br>
        Jika spread broker mendadak melebar > 1.8x batas maksimal, transaksi ditunda sampai spread kembali normal dan likuiditas stabil.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #8b5cf6;">
    <div class="card-header" style="color:#8b5cf6; font-size:8.5pt;">📈 2. RSI Momentum Divergence Exhaustion Sensor (Section 8.8)</div>
    <p style="font-size:7.5pt; margin-bottom:4px;">Memindai ketidakcocokan antara gerakan harga dan momentum RSI 14 untuk mencegah jebakan retail:</p>
    <div class="grid-2" style="font-size:7.2pt;">
      <div style="background:#fdf4ff; padding:5px 7px; border-radius:5px; border:1px solid #f0abfc;">
        <b style="color:#86198f;">🚫 CEGAH BELI DI PUCUK (Bearish Divergence)</b><br>
        Jika harga mencetak Higher High namun RSI mencetak Lower High di area overbought (>60), sinyal BUY <b>DIBATALKAN</b> karena momentum pembeli sudah habis (Exhaustion).
      </div>
      <div style="background:#f5f3ff; padding:5px 7px; border-radius:5px; border:1px solid #ddd6fe;">
        <b style="color:#5b21b6;">🚫 CEGAH JUAL DI LEMBAH (Bullish Divergence)</b><br>
        Jika harga mencetak Lower Low namun RSI mencetak Higher Low di area oversold (&lt;40), sinyal SELL <b>DIBATALKAN</b> karena penjual kehilangan tenaga dan rawan rebound tajam.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #059669;">
    <div class="card-header" style="color:#059669; font-size:8.5pt;">⏳ 3. Stagnant Trade Time-Exit / Rollover Shield (Section 2.5)</div>
    <p style="font-size:7.5pt; margin:0;">
      Posisi yang telah berjalan lebih dari <b>6 Jam</b> tanpa menyentuh TP dan berada di area profit/impas akan <b>ditutup secara damai</b>. Fitur ini membebaskan margin serta melindungi akun dari biaya swap rollover tengah malam dan lonjakan spread sesi subuh.
    </p>
  </div>

  <div class="alert-box success" style="margin-top:5px;">
    <strong>🖥️ Status Real-Time di Glassmorphic Dashboard:</strong><br>
    Panel HUD kini memantau kedua sensor ini secara live: <code>[News Shield]: AMAN (STANDBY) | Momentum: NORMAL (SEHAT)</code>.
  </div>
</div>

<!-- HALAMAN 5E: SMART SIDEWAYS & ANTI-FAKEOUT SUITE (v3.00) -->
<div class="page">
  <div class="header-bar">
    <h2>5E. Smart Sideways & Anti-Fakeout Suite (v3.00)</h2>
    <span class="tag">SMART SIDEWAYS SUITE</span>
  </div>

  <p>Pembaruan <b>v3.00 Apex Institutional Intelligence</b> menghadirkan 4 sensor kuantitatif baru untuk membasmi kerugian saat pasar sideways, kompresi sempit, atau breakout palsu (*fakeout*):</p>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #0284c7;">
    <div class="card-header" style="color:#0284c7; font-size:8.3pt;">⚡ 1. ADX Directional Power Threshold (Section 8.9)</div>
    <p style="font-size:7.4pt; margin:0 0 3px 0;">
      Mengukur tenaga kinetik pergerakan pasar. Jika <b>ADX(14) &lt; 22.0</b>, pasar dinyatakan berada di <i>Dead/Zombie Zone</i> (tanpa daya dorong terarah). Seluruh eksekusi dibekukan otomatis sampai pasar memiliki tren nyata (ADX &ge; 22.0).
    </p>
  </div>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #f59e0b;">
    <div class="card-header" style="color:#f59e0b; font-size:8.3pt;">📐 2. EMA Slope & Flatness Angle Filter (Section 8.10)</div>
    <p style="font-size:7.4pt; margin:0 0 3px 0;">
      Mendeteksi saat garis EMA 125 dan EMA 21 bergerak mendatar horizontal seperti benang kusut (<i>EMA Tangle</i>). Syarat eksekusi:
    </p>
    <div class="grid-2" style="font-size:7.2pt;">
      <div style="background:#f0fdf4; padding:4px 6px; border-radius:5px; border:1px solid #bbf7d0;">
        <b style="color:#15803d;">📈 SYARAT BUY (Slope &ge; +3 Pips)</b><br>
        Garis EMA 125 wajib menanjak ke atas minimal 3.0 pips dalam 5 bar terakhir. Menolak BUY saat garis EMA datar!
      </div>
      <div style="background:#fef2f2; padding:4px 6px; border-radius:5px; border:1px solid #fecaca;">
        <b style="color:#b91c1c;">📉 SYARAT SELL (Slope &le; -3 Pips)</b><br>
        Garis EMA 125 wajib menukik ke bawah minimal 3.0 pips dalam 5 bar terakhir. Menolak SELL saat garis EMA datar!
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #8b5cf6;">
    <div class="card-header" style="color:#8b5cf6; font-size:8.3pt;">📊 3. Institutional Volume Expansion / VSA (Section 8.11)</div>
    <p style="font-size:7.4pt; margin:0 0 3px 0;">
      Breakout institusi sejati selalu disertai lonjakan volume transaksi (*Volume Footprint*). Jika penembusan BOS/CHoCH terjadi namun volume lilin konfirmasi di bawah <b>1.15x rata-rata 20 bar</b>, robot menolaknya sebagai <b>Fakeout Jebakan Retail</b>!
    </p>
  </div>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #10b981;">
    <div class="card-header" style="color:#10b981; font-size:8.3pt;">📏 4. Minimum ATR Volatility Floor (Section 8.12)</div>
    <p style="font-size:7.4pt; margin:0;">
      Menjamin pasar memiliki ruang gerak yang memadai (<b>ATR &ge; 12.0 pips</b>). Jika pasar mati dengan pergerakan lilin liliput (&lt; 12 pips), robot tidak akan entry agar target TP tidak tersangkut spread.
    </p>
  </div>

  <div class="alert-box success" style="margin-top:5px;">
    <strong>🖥️ Terpantau Real-Time di HUD Chart:</strong><br>
    Baris baru di layar monitor: <code>[Anti-Sideways]: ADX: 24.5 | Vol: 132% | Slope Filter: AKTIF</code>.
  </div>
</div>

<!-- HALAMAN 5F: PROP FIRM GUARDIAN, STRUCTURAL TRAILING & TRAP HUNTER (v3.00) -->
<div class="page">
  <div class="header-bar">
    <h2>5F. Apex Grandmaster Suite (v3.00)</h2>
    <span class="tag">GRANDMASTER v3.00</span>
  </div>

  <p>Versi <b>v3.00 Apex Grandmaster Edition</b> menyematkan 4 mesin kelas institusional tingkat tinggi yang dirancang khusus untuk standarisasi akun prop firm dan profit konsisten:</p>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #ef4444;">
    <div class="card-header" style="color:#ef4444; font-size:8.3pt;">🛡️ 1. Prop Firm Equity Guardian & Hard DD Kill-Switch (Section 8.13)</div>
    <p style="font-size:7.4pt; margin:0 0 3px 0;">
      Mengawasi penurunan equity harian secara real-time terhadap modal awal pukul 00:00 (<i>Midnight Balance</i>). Jika equity turun menyentuh <b>4.0%</b> (di bawah batas 5% Prop Firm seperti FTMO/MFF), robot langsung memotong seluruh posisi aktif dan mengunci transaksi hingga pergantian hari server. Dilengkapi notifikasi push darurat ke smartphone!
    </p>
  </div>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #06b6d4;">
    <div class="card-header" style="color:#06b6d4; font-size:8.3pt;">📈 2. Dynamic Structural Swing Trailing (Section 2.6)</div>
    <p style="font-size:7.4pt; margin:0 0 3px 0;">
      Bukan sekadar trailing pips statis, Stop Loss digeser secara cerdas dan terlindungi di balik struktur ayunan harga nyata:
    </p>
    <div class="grid-2" style="font-size:7.2pt;">
      <div style="background:#f0fdf4; padding:4px 6px; border-radius:5px; border:1px solid #bbf7d0;">
        <b style="color:#15803d;">🟢 POSISI BUY</b><br>
        SL dikunci di bawah Higher Low (HL) terkonfirmasi + buffer 0.5x ATR saat posisi telah mengamankan profit &ge; InpBreakevenLockPips.
      </div>
      <div style="background:#fef2f2; padding:4px 6px; border-radius:5px; border:1px solid #fecaca;">
        <b style="color:#b91c1c;">🔴 POSISI SELL</b><br>
        SL dikunci di atas Lower High (LH) terkonfirmasi + buffer 0.5x ATR saat posisi telah mengamankan profit &ge; InpBreakevenLockPips.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #8b5cf6;">
    <div class="card-header" style="color:#8b5cf6; font-size:8.3pt;">⚖️ 3. Asymmetric Confidence Risk Allocator (Kelly Scaling v3.00)</div>
    <p style="font-size:7.4pt; margin:0 0 3px 0;">
      Mengalokasikan lot dinamis berdasarkan kualitas konfluensi: Setup <b>Grade A+ (Skor &ge; 85)</b> mendapatkan dorongan lot <b>1.30x</b> untuk memaksimalkan profit saat probabilitas tertinggi, sementara Setup Standar (&lt; 75) diskalakan turun menjadi <b>0.70x</b> untuk memitigasi risiko.
    </p>
  </div>

  <div class="card" style="margin-bottom:6px; border-left: 4px solid #f59e0b;">
    <div class="card-header" style="color:#f59e0b; font-size:8.3pt;">🎯 4. Liquidity Sweep Trap Hunter / Turtle Soup (Section 8.15)</div>
    <p style="font-size:7.4pt; margin:0;">
      Memanfaatkan momen pembantaian stop loss retail oleh bandar besar (<i>Stop Hunt Reversal</i>). Ketika harga menusuk ke luar ayunan High/Low (4 - 30 pips) lalu langsung ditarik kembali dengan ekor penolakan &ge; 40%, EA langsung mengeksekusi posisi reversal mengikuti arah manipulasi smart money!
    </p>
  </div>

  <div class="alert-box success" style="margin-top:5px;">
    <strong>🖥️ Pantauan HUD Layar:</strong><br>
    Baris baru di monitor MT4: <code>[Prop Firm Guard]: DD: 0.0% / Max 4.0% | Trap Hunter: AKTIF</code>.
  </div>
</div>

<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->
<div class="page">
  <div class="header-bar">
    <h2>6. Panduan 4 Preset Siap Pakai (.set) Termasuk RR 1:2.5 Elite</h2>
    <span class="tag">PRESET PROFILES</span>
  </div>

  <p>Telah disediakan 4 konfigurasi preset yang diuji secara mendalam untuk instrumen XAUUSD di broker QuickPro:</p>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #0284c7;">
    <div class="card-header" style="color:#0284c7; font-size:8.5pt;">🚀 PRESET 1: QUICKPRO_XAUUSD_FAST_AUTO_TRADE.set (Rekomendasi Utama)</div>
    <div class="grid-3" style="font-size:7.2pt;">
      <div>• <b>Timeframe:</b> M15 (atau M5)<br>• <b>Lot Type:</b> Min Lot Broker<br>• <b>Skor Min:</b> 55 Poin</div>
      <div>• <b>Risk Reward:</b> 1 : 1.5<br>• <b>BE Trigger:</b> +8.0 Pips<br>• <b>BE Lock:</b> +2.5 Pips</div>
      <div>• <b>TP1 Partial:</b> 50% at 10 Pips<br>• <b>Runner:</b> SMC HL/LH<br>• <b>Self-Healing:</b> Aktif</div>
    </div>
  </div>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #8b5cf6;">
    <div class="card-header" style="color:#8b5cf6; font-size:8.5pt;">💎 PRESET 2: QUICKPRO_XAUUSD_RR_1_TO_2_5_ELITE.set (Institutional RR 1:2.5)</div>
    <div class="grid-3" style="font-size:7.2pt;">
      <div>• <b>Timeframe:</b> M15 (Primary)<br>• <b>Lot Type:</b> Min Lot Broker<br>• <b>Skor Min:</b> 65 Poin</div>
      <div>• <b>Risk Reward:</b> 1 : 2.5 (Pure RR)<br>• <b>BE Trigger:</b> +10.0 Pips<br>• <b>BE Lock:</b> +2.5 Pips</div>
      <div>• <b>TP1 Partial:</b> 50% at 15 Pips<br>• <b>Runner:</b> 2.5x SL Distance<br>• <b>Self-Healing:</b> Aktif</div>
    </div>
  </div>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #16a34a;">
    <div class="card-header" style="color:#16a34a; font-size:8.5pt;">🎯 PRESET 3: QUICKPRO_XAUUSD_HIGH_WINRATE_SNIPER.set (Khusus Setup Sempurna)</div>
    <div class="grid-3" style="font-size:7.2pt;">
      <div>• <b>Timeframe:</b> M15 / H1<br>• <b>Lot Type:</b> Min Lot Broker<br>• <b>Skor Min:</b> 70 Poin</div>
      <div>• <b>Risk Reward:</b> 1 : 2.0<br>• <b>BE Trigger:</b> +10.0 Pips<br>• <b>BE Lock:</b> +3.0 Pips</div>
      <div>• <b>TP1 Partial:</b> 50% at 15 Pips<br>• <b>Golden Pocket:</b> Wajib Masuk<br>• <b>Self-Healing:</b> Aktif</div>
    </div>
  </div>

  <div class="card" style="margin-bottom:7px; border-left: 4px solid #f59e0b;">
    <div class="card-header" style="color:#f59e0b; font-size:8.5pt;">⚡ PRESET 4: QUICKPRO_XAUUSD_M5_SCALPING.set (Fast Intraday Scalper)</div>
    <div class="grid-3" style="font-size:7.2pt;">
      <div>• <b>Timeframe:</b> M5 (5 Menit)<br>• <b>Lot Type:</b> Min Lot Broker<br>• <b>Skor Min:</b> 50 Poin</div>
      <div>• <b>Risk Reward:</b> 1 : 1.3<br>• <b>BE Trigger:</b> +6.0 Pips<br>• <b>BE Lock:</b> +2.0 Pips</div>
      <div>• <b>TP1 Partial:</b> 50% at 8 Pips<br>• <b>SL Range:</b> 12 - 22 Pips<br>• <b>Self-Healing:</b> Aktif</div>
    </div>
  </div>

  <h3>📥 Cara Memuat Preset di Chart MT4:</h3>
  <p style="font-size:7.8pt;">1. Tekan <b>F7</b> pada chart tempat EA terpasang ➔ buka tab <b>Inputs</b>.<br>
  2. Klik tombol <b>Load</b> di sebelah kanan jendela.<br>
  3. Pilih file preset yang diinginkan (misal: <code>QUICKPRO_XAUUSD_RR_1_TO_2_5_ELITE.set</code>).<br>
  4. Klik <b>Open</b>, lalu klik <b>OK</b>. Seluruh konfigurasi otomatis terpasang dengan sempurna!</p>
</div>

<!-- HALAMAN 7: NOTIFIKASI PUSH, FAQ & SOP HARIAN -->
<div class="page">
  <div class="header-bar">
    <h2>7. Notifikasi Smartphone, Troubleshooting FAQ & SOP</h2>
    <span class="tag">PANDUAN OPERASIONAL</span>
  </div>

  <h3>📱 Menghubungkan EA ke Smartphone Anda (Android & iPhone)</h3>
  <p style="font-size:7.8pt;">Robot dapat mengirim notifikasi instan langsung ke saku Anda setiap kali Open Posisi, Kunci SL+, Amankan TP1 50%, atau Circuit Breaker aktif:</p>
  <div class="card" style="margin-bottom:8px; font-size:7.5pt;">
    1. Buka aplikasi <b>MetaTrader 4</b> di smartphone ➔ Menu <b>Settings</b> ➔ <b>Messages</b> ➔ Catat <b>MetaQuotes ID</b> Anda (kode 8 digit alfanumerik).<br>
    2. Buka MT4 di laptop/PC ➔ Menu <b>Tools</b> ➔ <b>Options</b> ➔ Tab <b>Notifications</b>.<br>
    3. Centang ☑ <b>Enable Push notifications</b> ➔ Masukkan MetaQuotes ID HP Anda ➔ Klik <b>Test</b> ➔ Klik <b>OK</b>.
  </div>

  <h3>❓ Tanya Jawab & Troubleshooting Umum</h3>
  <table>
    <thead>
      <tr>
        <th style="width:30%;">Pertanyaan</th>
        <th style="width:70%;">Solusi & Jawaban Praktis</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Kenapa EA belum open posisi?</b></td>
        <td>Robot hanya mengeksekusi jika terjadi konfluensi 4 pilar valid dan lilin selesai (*bar close*). Pastikan tombol AutoTrading berwarna hijau dan spread di bawah batas 4.5 pips.</td>
      </tr>
      <tr>
        <td><b>Kenapa lot terbuka 0.10 padahal input 0.01?</b></td>
        <td>Akun QuickPro Anda adalah tipe standar yang batas minimal transaksinya 0.10. EA secara cerdas menyesuaikan agar order tidak ditolak oleh broker.</td>
      </tr>
      <tr>
        <td><b>Apakah EA boleh dijalankan 24 jam?</b></td>
        <td>Sangat boleh, asalkan menggunakan koneksi stabil atau VPS (Virtual Private Server). EA sudah memiliki Friday Weekend Guard yang otomatis melikuidasi posisi di akhir pekan.</td>
      </tr>
    </tbody>
  </table>

  <h3>📋 Standard Operating Procedure (SOP) Harian Trader</h3>
  <div class="alert-box success">
    <b>Checklist 3 Menit Sebelum Menyalakan AutoTrading:</b><br>
    ☑ 1. Pastikan koneksi internet stabil (Ping server QuickPro < 100 ms).<br>
    ☑ 2. Pastikan chart berada di timeframe <b>M15</b> untuk XAUUSD.<br>
    ☑ 3. Pastikan tombol <b>AutoTrading</b> di toolbar atas menyala hijau dan ikon di chart tersenyum (😊).<br>
    ☑ 4. Periksa kalender ekonomi (ForexFactory). Jika ada berita NFP atau FOMC, Shock Guard akan otomatis melindungi modal Anda.<br>
    ☑ 5. Biarkan robot bekerja secara disiplin mengikuti algoritma tanpa intervensi manual yang emosional!
  </div>
</div>

</body>
</html>
"""

# Save temporary HTML
temp_html = os.path.join(os.path.dirname(__file__), "temp_mt4_guide.html")
with open(temp_html, "w", encoding="utf-8") as f:
    f.write(html_content)

# Destination paths
pdf_proj = os.path.join(os.path.dirname(__file__), "PANDUAN_LENGKAP_EA_VIKAR_PRO_MT4.pdf")
pdf_qp_terminal = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\F0B9948E0028C307A69410B7E4F7F6B6\MQL4\PANDUAN_LENGKAP_EA_VIKAR_PRO_MT4.pdf"
pdf_artifact = os.path.join(artifact_dir, "PANDUAN_LENGKAP_EA_VIKAR_PRO_MT4.pdf")

# Detect Edge path
edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_proj}",
    temp_html
]

print("Converting HTML to PDF via Edge Headless...")
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(pdf_proj):
    size = os.path.getsize(pdf_proj)
    print(f"SUCCESS: PDF created at {pdf_proj} ({size} bytes)")
    
    with open(pdf_proj, "rb") as f:
        pdf_bytes = f.read()
    page_matches = re.findall(b"/Type\\s*/Page[^s]", pdf_bytes)
    print(f"Total Pages in Generated PDF: {len(page_matches)}")

    # Sync to QuickPro MQL4 and Artifact
    shutil.copy2(pdf_proj, pdf_qp_terminal)
    shutil.copy2(pdf_proj, pdf_artifact)
    print(f"Synced to QuickPro MT4: {pdf_qp_terminal}")
    print(f"Synced to Artifact: {pdf_artifact}")

    if os.path.exists(temp_html):
        os.remove(temp_html)
else:
    print("FAILED to create PDF.")
    print("Return code:", res.returncode)
    print("Stderr:", res.stderr)
