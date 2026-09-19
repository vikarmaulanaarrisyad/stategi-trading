import os
import subprocess
import base64
import re

def image_to_base64(path):
    if os.path.exists(path):
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        with open(path, "rb") as img_file:
            return f"data:{mime};base64," + base64.b64encode(img_file.read()).decode("utf-8")
    return ""

artifact_dir = r"C:\Users\vikar\.gemini\antigravity-ide\brain\35bc941c-56ef-442a-b8ea-185da534d5c0"
img_buy = image_to_base64(os.path.join(artifact_dir, "setup_buy_continuation_1789611753200.jpg"))
img_sell = image_to_base64(os.path.join(artifact_dir, "setup_sell_continuation_1789611766274.jpg"))
img_buy_choch = image_to_base64(os.path.join(artifact_dir, "setup_buy_choch_1789611784040.jpg"))
img_sell_choch = image_to_base64(os.path.join(artifact_dir, "setup_sell_choch_1789611801504.jpg"))
img_scalp = image_to_base64(os.path.join(artifact_dir, "setup_scalp_confluence_1789611821381.jpg"))
img_fibo_buy = image_to_base64(os.path.join(artifact_dir, "fibo_buy_confluence_1789625869992.jpg"))
img_fibo_sell = image_to_base64(os.path.join(artifact_dir, "fibo_sell_confluence_1789625890125.jpg"))
img_synergy = image_to_base64(os.path.join(artifact_dir, "synergy_ema_pivots_1789626295121.jpg"))
img_chart4 = image_to_base64(os.path.join(artifact_dir, "chart_annotated_smc_case4.png"))
img_smc_bos = image_to_base64(os.path.join(artifact_dir, "smc_bos_inducement_pattern_1789635642712.jpg"))
img_smc_choch = image_to_base64(os.path.join(artifact_dir, "smc_choch_reversal_pattern_1789635661082.jpg"))

html_content = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>PANDUAN OPERASIONAL LENGKAP EA MT5 - VIKAR 4-PILLAR PRO</title>
<style>
  @page {{
    size: A4;
    margin: 12mm 12mm 14mm 12mm;
    @bottom-right {{
      content: "Halaman " counter(page);
      font-size: 8pt;
      color: #64748b;
      font-weight: 600;
    }}
    @bottom-left {{
      content: "VIKAR EA 4-PILLAR PRO (v2.1 MASTER INTELLIGENCE) | PANDUAN MANUAL MT5 RESMI";
      font-size: 7.5pt;
      color: #64748b;
      font-weight: bold;
    }}
  }}
  
  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.4;
    font-size: 8.5pt;
    margin: 0;
    padding: 0;
  }}

  .page {{
    page-break-after: always;
    break-after: page;
    position: relative;
    box-sizing: border-box;
  }}

  .page:last-child, .page:last-of-type {{
    page-break-after: avoid;
    break-after: avoid;
  }}

  /* Cover Page */
  .cover {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 960px;
    text-align: center;
    background: linear-gradient(145deg, #090d16 0%, #0f172a 45%, #1e293b 80%, #0369a1 100%);
    color: #ffffff;
    border-radius: 12px;
    padding: 30px 25px;
    box-sizing: border-box;
  }}

  .cover-badge {{
    background-color: rgba(56, 189, 248, 0.15);
    border: 1.5px solid #38bdf8;
    color: #38bdf8;
    padding: 6px 18px;
    border-radius: 20px;
    font-size: 8.5pt;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 20px;
  }}

  .cover-title {{
    font-size: 26pt;
    font-weight: 900;
    line-height: 1.2;
    margin: 0 0 10px 0;
    background: linear-gradient(to right, #38bdf8, #f43f5e, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .cover-subtitle {{
    font-size: 13pt;
    color: #94a3b8;
    font-weight: 500;
    margin: 0 0 25px 0;
    letter-spacing: 0.5px;
  }}

  .cover-pillars {{
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 15px 0 30px 0;
    width: 100%;
  }}

  .pillar-box {{
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.3);
    border-radius: 8px;
    padding: 10px 12px;
    flex: 1;
    text-align: center;
  }}

  .pillar-box h4 {{
    margin: 0 0 4px 0;
    font-size: 9pt;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}

  .pillar-box p {{
    margin: 0;
    font-size: 7.5pt;
    color: #cbd5e1;
    line-height: 1.3;
  }}

  .cover-meta {{
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 20px;
    width: 90%;
    margin-top: 20px;
    display: flex;
    justify-content: space-around;
    font-size: 8pt;
    color: #cbd5e1;
  }}

  .meta-item strong {{
    display: block;
    color: #38bdf8;
    font-size: 8.5pt;
  }}

  /* Chapter Titles & Headings */
  .chapter-header {{
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 5px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}

  .chapter-title {{
    font-size: 14pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .chapter-badge {{
    background-color: #0284c7;
    color: #ffffff;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 4px;
    text-transform: uppercase;
  }}

  h2 {{
    font-size: 11pt;
    font-weight: 700;
    color: #0369a1;
    margin: 10px 0 6px 0;
    border-left: 3.5px solid #0284c7;
    padding-left: 7px;
  }}

  h3 {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #1e293b;
    margin: 8px 0 4px 0;
  }}

  p {{
    margin: 0 0 7px 0;
    text-align: justify;
  }}

  /* Grid & Columns */
  .grid-2 {{
    display: flex;
    gap: 12px;
    margin-bottom: 10px;
  }}

  .grid-2 > div {{
    flex: 1;
  }}

  .grid-3 {{
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }}

  .grid-3 > div {{
    flex: 1;
  }}

  .grid-4 {{
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
  }}

  .grid-4 > div {{
    flex: 1;
  }}

  /* Cards & Callouts */
  .card {{
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 9px 11px;
    margin-bottom: 8px;
  }}

  .card-highlight {{
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-left: 4px solid #0284c7;
    border-radius: 6px;
    padding: 8px 11px;
    margin-bottom: 8px;
  }}

  .card-success {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
    border-radius: 6px;
    padding: 8px 11px;
    margin-bottom: 8px;
  }}

  .card-warning {{
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #d97706;
    border-radius: 6px;
    padding: 8px 11px;
    margin-bottom: 8px;
  }}

  .card-danger {{
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 4px solid #e11d48;
    border-radius: 6px;
    padding: 8px 11px;
    margin-bottom: 8px;
  }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 9px;
    font-size: 7.8pt;
  }}

  th, td {{
    padding: 4.5px 7px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }}

  th {{
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 7.5pt;
    letter-spacing: 0.5px;
  }}

  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  .badge {{
    display: inline-block;
    padding: 1.5px 6px;
    border-radius: 3px;
    font-size: 7pt;
    font-weight: 700;
    text-transform: uppercase;
  }}

  .badge-blue {{ background-color: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }}
  .badge-green {{ background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }}
  .badge-red {{ background-color: #ffe4e6; color: #be123c; border: 1px solid #fda4af; }}
  .badge-purple {{ background-color: #f3e8ff; color: #7e22ce; border: 1px solid #d8b4fe; }}
  .badge-gold {{ background-color: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }}

  /* Chart & Images */
  .img-container {{
    width: 100%;
    text-align: center;
    margin: 6px 0;
  }}

  .img-container img {{
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
  }}

  .img-caption {{
    font-size: 7.2pt;
    color: #64748b;
    margin-top: 3px;
    font-style: italic;
  }}

  /* Code Blocks */
  code {{
    font-family: 'Consolas', 'Courier New', monospace;
    background-color: #e2e8f0;
    padding: 1.5px 4px;
    border-radius: 3px;
    font-size: 8pt;
    color: #0f172a;
  }}

  .code-block {{
    background-color: #0f172a;
    color: #38bdf8;
    font-family: 'Consolas', monospace;
    font-size: 7.8pt;
    padding: 8px 12px;
    border-radius: 5px;
    line-height: 1.35;
    margin-bottom: 8px;
    overflow-x: hidden;
  }}
</style>
</head>
<body>

<!-- ==================== HALAMAN 1: COVER ==================== -->
<div class="page">
  <div class="cover">
    <div class="cover-badge">METATRADER 5 (MT5) OFFICIAL USER MANUAL</div>
    <h1 class="cover-title">VIKAR INSTITUTIONAL<br>4-PILLAR EA PRO</h1>
    <div class="cover-subtitle">Robot Trading Otomatis Berbasis 4 Pilar Terpadu (v2.1 Master Intelligence)</div>
    
    <div class="cover-pillars">
      <div class="pillar-box">
        <h4>Pilar 1: SMC Core</h4>
        <p>BOS, CHoCH, Liquidity Sweep, Equilibrium 50% Diskon/Premium</p>
      </div>
      <div class="pillar-box">
        <h4>Pilar 2: S/R Pivots</h4>
        <p>Daily Pivots, Double Alignment & Headroom ATR Protection</p>
      </div>
      <div class="pillar-box">
        <h4>Pilar 3: Triple EMA</h4>
        <p>EMA 8 Momentum, EMA 21 Value Ribbon & EMA 125 Macro Baseline</p>
      </div>
      <div class="pillar-box">
        <h4>Pilar 4: Fibonacci</h4>
        <p>Auto-Fibo SMC, Golden Pocket 61.8% & TP Target Projections</p>
      </div>
    </div>

    <div style="width: 90%; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 8px; padding: 15px; text-align: left; margin-bottom: 20px;">
      <h4 style="color: #38bdf8; margin: 0 0 8px 0; font-size: 9.5pt; text-align: center; text-transform: uppercase; letter-spacing: 1px;">Kecerdasan Buatan Terintegrasi (Master Intelligence v2.1)</h4>
      <p style="color: #cbd5e1; font-size: 8pt; margin: 0; line-height: 1.45;">
        Buku panduan resmi ini mendokumentasikan secara rinci arsitektur logika, petunjuk instalasi terminal MT5, SOP manajemen risiko, katalog 4 preset resmi, panduan membaca HUD real-time, mekanisme Auto-Cut Profit pembalikan, hingga prosedur backtest dengan data centang riil. Dirancang khusus untuk trader institusional yang mengutamakan rasio kemenangan tinggi (High Winrate) dan proteksi modal teruji.
      </p>
    </div>

    <div class="cover-meta">
      <div class="meta-item">
        <strong>Platform</strong>
        MetaTrader 5 (Didimax / ECN)
      </div>
      <div class="meta-item">
        <strong>Instrumen Utama</strong>
        XAU/USD (Gold) & Major FX
      </div>
      <div class="meta-item">
        <strong>Timeframe</strong>
        M5 (Scalping) & M15 (Day Trade)
      </div>
      <div class="meta-item">
        <strong>Versi Mesin</strong>
        v2.1 Master Intelligence (Audited)
      </div>
    </div>

    <div style="margin-top: 25px; font-size: 7.5pt; color: #94a3b8;">
      Copyright &copy; 2026 Vikar Institutional Trading Strategy. Hak Cipta Dilindungi Undang-Undang.
    </div>
  </div>
</div>

<!-- ==================== HALAMAN 2: ARSITEKTUR 4 PILAR TERPADU ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 1: Arsitektur 4 Pilar Terpadu</div>
    <div class="chapter-badge">Pondasi Sistem</div>
  </div>

  <p>
    <strong>VIKAR EA 4-Pillar Pro</strong> dirancang dengan filosofi dasar bahwa pasar finansial modern digerakkan oleh institusi perbankan besar (*Smart Money*), bukan tebak-tebakan teknikal ritel. Agar memiliki probabilitas kemenangan yang tinggi, robot ini menggabungkan 4 pilar teknikal saling mengunci (*Quadruple Multi-Confluence Validation*):
  </p>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>🏛️ Pilar 1: Smart Money Concepts (SMC Core)</h3>
      <p>
        Menjadi pondasi utama dalam memetakan niat modal institusional:
      </p>
      <ul style="margin: 0 0 4px 0; padding-left: 16px;">
        <li><strong>BOS (Break of Structure):</strong> Memvalidasi fase ekspansi kelanjutan tren (*Trend Continuation*).</li>
        <li><strong>CHoCH (Change of Character):</strong> Mendeteksi sinyal dini pembalikan tren (*Reversal Alert*).</li>
        <li><strong>Liquidity Sweep (Stop Hunt):</strong> Mendeteksi sapuan likuiditas di pucuk Swing High / Swing Low ritel sebelum harga bergerak kencang ke arah sebenarnya.</li>
        <li><strong>Dealing Range Equilibrium (50% Matrix):</strong> Wajib BUY hanya di Zona Diskon (&lt; 50%), dan SELL hanya di Zona Premium (&gt; 50%). Dilarang keras membeli harga mahal!</li>
      </ul>
    </div>

    <div class="card-highlight">
      <h3>🎯 Pilar 2: S/R Struktural & Daily Pivot Points</h3>
      <p>
        Menyediakan dinding batas harga objektif harian dari data pasar D1:
      </p>
      <ul style="margin: 0 0 4px 0; padding-left: 16px;">
        <li><strong>Central Pivot (P):</strong> Garis ekuilibrium harian institusi (Biru).</li>
        <li><strong>Double Alignment Rule:</strong> Sinergi ganda mutlak. Harga di atas EMA 125 DAN di atas Pivot P = <code>SUPER BULLISH (Grade A+)</code>. Sebaliknya di bawah keduanya = <code>SUPER BEARISH</code>.</li>
        <li><strong>Headroom ATR Filter:</strong> Melarang eksekusi order jika jarak ke dinding Support/Resistance terdekat kurang dari <code>0.5x ATR</code> untuk menghindari "membeli tepat di pucuk atap resisten".</li>
      </ul>
    </div>
  </div>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>📈 Pilar 3: Triple EMA & Macro HTF Alignment</h3>
      <p>
        Navigasi tren dinamis 3 lapisan dan filter timeframe tinggi:
      </p>
      <ul style="margin: 0 0 4px 0; padding-left: 16px;">
        <li><strong>EMA 125 Putih:</strong> Baseline tren institusional jangka menengah. Filter mutlak pembagi wilayah Bullish / Bearish.</li>
        <li><strong>Ribbon EMA 8 Cyan & EMA 21 Magenta:</strong> Zona nilai dinamis (*Dynamic Value Zone*). Harga harus mengalami koreksi sehat (*pullback*) ke pita ini sebelum entri.</li>
        <li><strong>Macro H1 Alignment:</strong> Membaca tren di timeframe H1 secara real-time. Eksekusi M5 hanya diizinkan jika sejalan dengan arus modal besar H1.</li>
      </ul>
    </div>

    <div class="card-highlight">
      <h3>🌀 Pilar 4: Fibonacci Retracement & Golden Pocket</h3>
      <p>
        Matematika rasio emas untuk akurasi titik entri sniper:
      </p>
      <ul style="margin: 0 0 4px 0; padding-left: 16px;">
        <li><strong>Auto-Fibo Dynamic SMC:</strong> Ditarik otomatis dari Swing Low ke Swing High aktif yang dihasilkan algoritma SMC.</li>
        <li><strong>Golden Pocket (0.500 - 0.618 - 0.786):</strong> Area koreksi terkuat di dunia. Pantulan di level 61.8% memberikan bobot skor konfluensi maksimal.</li>
        <li><strong>Target Ekstensi Fibo:</strong> Menghitung target proyeksi Take Profit objektif pada level ekstensi <code>-0.272 (TP1)</code> dan <code>-0.618 (TP2)</code>.</li>
      </ul>
    </div>
  </div>

  <div class="card">
    <h3 style="margin: 0 0 4px 0; color: #0284c7;">Matriks Aturan Baku Eksekusi 4 Pilar:</h3>
    <table>
      <thead>
        <tr>
          <th>Pilar Analisis</th>
          <th>Syarat SETUP BUY (Long)</th>
          <th>Syarat SETUP SELL (Short)</th>
          <th>Fungsi Filter</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. SMC Core</strong></td>
          <td>Bullish Structure / BOS / CHoCH + Zona Diskon (&lt;50%)</td>
          <td>Bearish Structure / BOS / CHoCH + Zona Premium (&gt;50%)</td>
          <td>Memastikan entri searah arus Smart Money</td>
        </tr>
        <tr>
          <td><strong>2. S/R Pivots</strong></td>
          <td>Harga &gt; Pivot P Harian + Headroom ATR Cukup</td>
          <td>Harga &lt; Pivot P Harian + Headroom ATR Cukup</td>
          <td>Mencegah entri tertabrak dinding resisten</td>
        </tr>
        <tr>
          <td><strong>3. Triple EMA</strong></td>
          <td>Harga &gt; EMA 125 + Pullback ke Ribbon EMA 8/21</td>
          <td>Harga &lt; EMA 125 + Pullback ke Ribbon EMA 8/21</td>
          <td>Menyaring momentum dan koreksi sehat</td>
        </tr>
        <tr>
          <td><strong>4. Fibonacci</strong></td>
          <td>Retracement menguji area Golden Pocket (0.50 - 0.786)</td>
          <td>Retracement menguji area Golden Pocket (0.50 - 0.786)</td>
          <td>Akurasi presisi pantulan rasio emas 61.8%</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- ==================== HALAMAN 3: VISUAL MASTERCLASS SMC & OB/FVG ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 2: Visual Anatomi SMC & Order Block Engine</div>
    <div class="chapter-badge">Bedah Algoritma</div>
  </div>

  <h2>1. Siklus Struktur Pasar: BOS, Inducement & CHoCH</h2>
  <p>
    Pasar bergerak dalam siklus ekspansi dan retracement. Algoritma SMC pada EA secara otomatis mendeteksi setiap titik ayunan (*Fractal Swings*) untuk memvalidasi struktur pasar yang valid:
  </p>

  <div class="grid-2">
    <div class="img-container">
      <img src="__IMG_SMC_BOS__" style="max-height: 190px;" alt="BOS & Inducement">
      <div class="img-caption">Gambar 1: Struktur Bullish BOS (Break of Structure) & Inducement Sweep</div>
    </div>
    <div class="img-container">
      <img src="__IMG_SMC_CHOCH__" style="max-height: 190px;" alt="CHoCH Reversal">
      <div class="img-caption">Gambar 2: Transisi Pembalikan Tren Bullish CHoCH (Change of Character)</div>
    </div>
  </div>

  <h2>2. Mesin Order Block (OB) & Multi-Bar Fair Value Gap (FVG)</h2>
  <p>
    Salah satu keunggulan terbesar pada versi <strong>v2.1 Master Intelligence</strong> adalah mesin pelacak Order Block dan FVG otomatis:
  </p>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>📦 Order Block Engine (Displacement ATR $\ge 1.25\times$)</h3>
      <ul style="margin: 0; padding-left: 16px;">
        <li><strong>Bullish Order Block (Base Demand):</strong> Lilin *bearish* terakhir sebelum lonjakan lilin *bullish* impulsif yang memiliki panjang body $\ge 1.25\times\text{ATR}$.</li>
        <li><strong>Bearish Order Block (Supply Zone):</strong> Lilin *bullish* terakhir sebelum kejatuhan harga impulsif.</li>
        <li><strong>Mitigation Tracker:</strong> EA melacak apakah zona OB tersebut masih perawan (*fresh/unmitigated*) atau sudah tersentuh (*mitigated*). Entri pada OB yang belum pernah tersentuh memiliki probabilitas tertinggi!</li>
      </ul>
    </div>

    <div class="card-highlight">
      <h3>⚡ Multi-Bar Fair Value Gap (FVG Imbalance)</h3>
      <ul style="margin: 0; padding-left: 16px;">
        <li><strong>Definisi Celah FVG:</strong> Ketidakseimbangan 3 lilin di mana ekor lilin 1 dan ekor lilin 3 tidak saling tumpang tindih (*imbalance*).</li>
        <li><strong>Pemindaian Multi-Bar (20 Bars):</strong> Memindai hingga 20–35 lilin ke belakang untuk menemukan area FVG aktif.</li>
        <li><strong>Rebound Mitigasi:</strong> Saat harga kembali menguji (*fill*) celah FVG dan memantul, EA memberikan nilai konfluensi tambahan sebesar +15 poin!</li>
      </ul>
    </div>
  </div>

  <div class="card-success">
    <h3 style="margin: 0 0 4px 0; color: #15803d;">🛡️ Fitur Smart Early Invalidation Cut:</h3>
    <p style="margin: 0;">
      Jika posisi BUY sedang terbuka di area Bullish Order Block, namun tiba-tiba pasar dikejutkan oleh lilin *displacement bearish* kuat yang menembus dasar Order Block acuan, EA akan <strong>langsung menutup posisi lebih awal</strong> tanpa menunggu harga menyentuh Stop Loss penuh. Fitur ini berhasil menghemat modal trader hingga 50% - 70% dari risiko kerugian normal!
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 4: CHART PATTERNS & CANDLESTICK ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 3: Mesin Pola Grafik & Candlestick Lanjutan</div>
    <div class="chapter-badge">Kecerdasan v2.1</div>
  </div>

  <h2>1. Mesin Pengenal Pola Grafik (Chart Pattern Recognition Engine)</h2>
  <p>
    Versi v2.1 mengintegrasikan modul pendeteksi pola grafik geometris institusional berbasis ayunan harga multi-bar:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Nama Pola Grafik</th>
        <th style="width: 15%;">Tipe & Arah</th>
        <th style="width: 12%;">Skor Pola</th>
        <th>Logika Deteksi & Karakteristik Institusional</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Quasimodo (QM Setup)</strong></td>
        <td><span class="badge badge-purple">Reversal Elit</span></td>
        <td><strong>95 Poin</strong></td>
        <td>Pola Over-Under: Sapuan likuiditas Higher High disusul Lower Low tajam, lalu harga retrace menguji level Left Shoulder di zona Base Demand.</td>
      </tr>
      <tr>
        <td><strong>Double Bottom (W-Pattern)</strong></td>
        <td><span class="badge badge-green">Bullish Reversal</span></td>
        <td><strong>85 Poin</strong></td>
        <td>Dua lembah sejajar berjarak &le; 0.35x ATR. Kaki kedua menolak level lembah pertama dengan konfluensi Liquidity Sweep.</td>
      </tr>
      <tr>
        <td><strong>Double Top (M-Pattern)</strong></td>
        <td><span class="badge badge-red">Bearish Reversal</span></td>
        <td><strong>85 Poin</strong></td>
        <td>Dua puncak sejajar berjarak &le; 0.35x ATR. Kaki kedua menolak level puncak pertama, sinyal awal kejatuhan harga.</td>
      </tr>
      <tr>
        <td><strong>Head & Shoulders (H&S)</strong></td>
        <td><span class="badge badge-blue">Struktural 3-Ayunan</span></td>
        <td><strong>90 Poin</strong></td>
        <td>Head berada di titik ekstrem tertinggi/terendah, Left Shoulder dan Right Shoulder memantul simetris di level Golden Pocket Fibo.</td>
      </tr>
      <tr>
        <td><strong>Bullish / Bearish Flags</strong></td>
        <td><span class="badge badge-gold">Continuation</span></td>
        <td><strong>80 Poin</strong></td>
        <td>Lilin tiang bendera impulsif (&ge; 1.2x ATR) diikuti saluran koreksi miring 3-5 lilin sebelum ledakan ekspansi kelanjutan tren.</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Kecerdasan Pola Candlestick Rejection Lanjutan</h2>
  <div class="grid-2">
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 5px 0;">A. Three White Soldiers & Three Black Crows (85 Poin)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Tiga lilin ekspansi beruntun dengan body penuh yang ditutup semakin tinggi (BUY) atau semakin rendah (SELL). Mengonfirmasi gelombang modal besar sedang masuk pasar secara agresif.
      </p>
    </div>
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 5px 0;">B. Dragonfly Doji & Gravestone Doji (82 Poin)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Penolakan harga ekstrem di mana ekor lilin mencapai &ge; 70% dari total panjang lilin dan body sangat tipis (&le; 12%). Menandakan sapuan stop loss total dan penolakan harga instan.
      </p>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 5px 0;">C. Bullish & Bearish Harami / Inside Bar (78 Poin)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Lilin kedua terbentuk sepenuhnya di dalam rentang lilin pertama (*Inside Bar Compression*). Menandakan jeda kompresi volatilitas sebelum terjadi lonjakan breakout terarah.
      </p>
    </div>
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 5px 0;">D. Piercing Line & Dark Cloud Cover (78 Poin)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Lilin konfirmasi menembus lebih dari 50% body lilin berlawanan sebelumnya. Menunjukkan penyerapan suplai/demand (*Absorption*) yang sangat dominan oleh institusi.
      </p>
    </div>
  </div>

  <div class="card-highlight">
    <h3 style="margin: 0 0 4px 0;">Pola Rejection Klasik Terverifikasi (Tambahan):</h3>
    <p style="margin: 0; font-size: 8pt;">
      Selain pola lanjutan di atas, EA tetap memindai pola klasik berakurasi tinggi: <strong>Hammer & Pin Bar</strong> (Ekor &ge; 55%), <strong>Institutional Engulfing</strong>, <strong>Tweezer Tops/Bottoms</strong>, dan <strong>Morning/Evening Star</strong> (3-Bar Reversal).
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 5: SISTEM SKOR KONFLUENSI ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 4: Sistem Skor Konfluensi 4 Pilar</div>
    <div class="chapter-badge">Grade Filter</div>
  </div>

  <h2>Bobot Skor Kuantitatif (0 - 100 Poin)</h2>
  <p>
    Untuk mengeliminasi sinyal lemah dan noise pasar, EA menerapkan sistem penilaian matematis (*Quantitative Confluence Score*). Setiap komponen teknikal memiliki bobot poin tertentu:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Komponen Analisis</th>
        <th style="width: 15%;">Maks. Poin</th>
        <th>Kriteria Penilaian Bobot Poin</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. Struktur Pasar SMC</strong></td>
        <td><strong>20 Poin</strong></td>
        <td>BOS Valid (+15 Poin) | CHoCH Reversal Kuat (+20 Poin) | Posisi di Zona Diskon/Premium (+5 Poin).</td>
      </tr>
      <tr>
        <td><strong>2. Order Block Mitigation</strong></td>
        <td><strong>20 Poin</strong></td>
        <td>Ada OB Aktif Valid (+8 Poin) | Harga tepat menguji zona Base Demand / Supply (+12 Poin).</td>
      </tr>
      <tr>
        <td><strong>3. Displacement Momentum</strong></td>
        <td><strong>15 Poin</strong></td>
        <td>Lilin pemicu memiliki body impulsif $\ge 1.25\times\text{ATR}$ (Skor proporsional $5 + \text{Displacement}\times 5$).</td>
      </tr>
      <tr>
        <td><strong>4. Fair Value Gap (FVG)</strong></td>
        <td><strong>15 Poin</strong></td>
        <td>Ada Celah FVG Aktif (+6 Poin) | Lilin sedang memitigasi celah FVG Imbalance (+9 Poin).</td>
      </tr>
      <tr>
        <td><strong>5. Liquidity Sweep</strong></td>
        <td><strong>10 Poin</strong></td>
        <td>Ekor lilin menyapu stop loss di luar Swing High / Swing Low sebelumnya (+10 Poin).</td>
      </tr>
      <tr>
        <td><strong>6. Fibo Golden Pocket</strong></td>
        <td><strong>10 Poin</strong></td>
        <td>Harga berada tepat di area rasio emas 0.500 - 0.786 (+10 Poin) | Berada di zona diskon (+5 Poin).</td>
      </tr>
      <tr>
        <td><strong>7. Triple EMA Ribbon</strong></td>
        <td><strong>10 Poin</strong></td>
        <td>Harga di sisi tren EMA 125 (+5 Poin) | Momentum Ribbon EMA 8 sejalan dengan EMA 21 (+5 Poin).</td>
      </tr>
      <tr>
        <td><strong>8. Candlestick Rejection</strong></td>
        <td><strong>10 Poin</strong></td>
        <td>Pola lilin terkonfirmasi (Skor lilin $\times 0.10$, maksimal +10 Poin).</td>
      </tr>
      <tr>
        <td><strong>9. Bonus Pola Grafik</strong></td>
        <td><strong>15 Poin</strong></td>
        <td>Pola Quasimodo, Double Top/Bottom, H&S, atau Flag terdeteksi (Bonus hingga +15 Poin!).</td>
      </tr>
    </tbody>
  </table>

  <h2>Klasifikasi Kualitas Sinyal (Grade Execution Filter)</h2>
  <div class="grid-3">
    <div class="card-success">
      <h3 style="color: #15803d; margin: 0 0 4px 0;">GRADE A+ SNIPER</h3>
      <div style="font-size: 16pt; font-weight: 800; color: #16a34a; margin-bottom: 5px;">&ge; 80 Poin</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Setup sempurna dengan konfluensi penuh: Struktur SMC + Order Block + FVG + Golden Pocket + Pola Lilin Elit. Winrate tertinggi!
      </p>
    </div>

    <div class="card-highlight">
      <h3 style="color: #0369a1; margin: 0 0 4px 0;">GRADE A HIGH PROB</h3>
      <div style="font-size: 16pt; font-weight: 800; color: #0284c7; margin-bottom: 5px;">65 - 79 Poin</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Setup berkualitas tinggi memenuhi syarat tren utama EMA 125, Double Alignment Pivot, dan konfirmasi rejection lilin.
      </p>
    </div>

    <div class="card-danger">
      <h3 style="color: #be123c; margin: 0 0 4px 0;">GRADE B REJECT</h3>
      <div style="font-size: 16pt; font-weight: 800; color: #e11d48; margin-bottom: 5px;">&lt; 65 Poin</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Setup lemah, minim konfluensi, atau berada di area konsolidasi/whipsaw. <strong>DITOLAK OTOMATIS</strong> oleh sistem!
      </p>
    </div>
  </div>

  <div class="card-warning">
    <h3 style="color: #b45309; margin: 0 0 4px 0;">⚡ Shock Guard Protection (Anti-Spike Berita):</h3>
    <p style="margin: 0; font-size: 8pt;">
      Jika terbentuk lilin abnormal dengan rentang harga $&gt; 2.2\times\text{ATR}$ (akibat rilis data NFP, CPI, atau FOMC), sistem otomatis mengunci status <strong>SHOCK GUARD</strong> dan menghentikan seluruh entri baru selama 2-3 lilin berikutnya sampai kepanikan pasar mereda.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 6: MEKANISME EKSEKUSI PINTAR ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 5: Fitur Pertahanan Profit & Trade Management</div>
    <div class="chapter-badge">Profit Defense</div>
  </div>

  <h2>1. Auto-Breakeven / SL+ (Kunci Modal & Profit Terjamin)</h2>
  <p>
    Begitu transaksi berjalan menguntungkan, EA tidak membiarkan keuntungan berubah menjadi kerugian. Fitur Auto-Breakeven secara otomatis menggeser Stop Loss melampaui harga entri (*SL Plus*):
  </p>
  <div class="grid-2">
    <div class="card-highlight">
      <h3>Model Pemicu Berdasarkan Pips (BE Pips Mode)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Contoh: Saat posisi BUY berjalan profit <code>+8.0 s/d +15.0 Pips</code>, Stop Loss otomatis digeser ke <code>Harga Open + 3.0 s/d 5.0 Pips</code>. Modal 100% aman dan profit kecil telah terkunci di tangan!
      </p>
    </div>
    <div class="card-highlight">
      <h3>Model Pemicu Berdasarkan Rasio Risk-Reward (BE RR Mode)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Contoh: Saat posisi mencapai keuntungan <code>1 : 1 R:R</code> dari jarak risiko SL awal, Stop Loss otomatis digeser ke SL+ untuk mengamankan posisi bebas risiko (*Risk-Free Trade*).
      </p>
    </div>
  </div>

  <h2>2. Partial Take Profit (Scaling Out: Amankan 50% di TP1 + SL+ Runner)</h2>
  <p>
    Strategi trader profesional adalah mengamankan sebagian keuntungan di target awal sambil membiarkan sisa volume memburu tren besar:
  </p>
  <div class="card-success">
    <h3 style="color: #15803d; margin: 0 0 4px 0;">Mekanisme Kerja Partial Close 50%:</h3>
    <ul style="margin: 0; padding-left: 18px; font-size: 8pt;">
      <li>Saat harga mencapai target profit parsial (misal +10 s/d +18 pips), sistem menutup <strong>50% lot</strong> posisi.</li>
      <li>Keuntungan 50% langsung masuk ke saldo riil akun (*Realized Balance*).</li>
      <li>Sisa 50% lot otomatis dipasangi <strong>Stop Loss Plus (SL+)</strong> dan dibiarkan berjalan sebagai <strong>RUNNER</strong> hingga menyentuh Take Profit final (R:R 1:2 atau Fibo -0.272).</li>
      <li><strong>Proteksi Khusus Broker Didimax:</strong> Jika posisi dibuka dengan minimal lot broker (0.10 lot) yang tidak dapat dibagi dua, EA secara cerdas mengaktifkan <code>FULL LOCK SL+</code> sehingga transaksi tetap terlindungi tanpa mengalami penolakan error lot dari broker!</li>
    </ul>
  </div>

  <h2>3. Trailing Stop Dinamis Mengikuti Ribbon EMA 21 Magenta</h2>
  <p>
    Untuk menangkap pergerakan tren panjang tanpa keluar terlalu dini, EA menyediakan Trailing Stop cerdas yang dipatok pada Ribbon EMA 21:
  </p>
  <div class="card">
    <ul style="margin: 0; padding-left: 18px; font-size: 8pt;">
      <li><strong>Posisi BUY:</strong> Stop Loss dinaikkan bertahap tepat di bawah garis EMA 21 (dikurangi buffer 4-5 pips). Selama lilin harga tetap berada di atas EMA 21, posisi terus menghasilkan cuan tanpa batas (*Unlimited Trend Rider*).</li>
      <li><strong>Posisi SELL:</strong> Stop Loss diturunkan bertahap tepat di atas garis EMA 21 (ditambah buffer 4-5 pips).</li>
    </ul>
  </div>

  <h2>4. Auto Cut Profit Saat Indikasi Pembalikan Arah</h2>
  <div class="card-danger">
    <h3 style="color: #be123c; margin: 0 0 4px 0;">Deteksi Pembalikan Dini (Reversal Signal Exit):</h3>
    <p style="margin: 0 0 4px 0; font-size: 8pt;">
      Jika posisi sedang berjalan profit (&ge; batas minimal profit pips), namun tiba-tiba terdeteksi salah satu dari 3 indikasi pembalikan berikut:
    </p>
    <ol style="margin: 0; padding-left: 18px; font-size: 8pt;">
      <li><strong>Terbentuk CHoCH Berlawanan:</strong> Perubahan karakter struktur pasar SMC yang membatalkan tren sebelumnya.</li>
      <li><strong>Candlestick Reversal Rejection:</strong> Muncul pola Pin Bar, Engulfing, atau Doji kuat berlawanan arah order.</li>
      <li><strong>Penembusan Pita EMA 21:</strong> Lilin ditutup menembus Ribbon EMA 21 ke arah berlawanan.</li>
    </ol>
    <p style="margin: 4px 0 0 0; font-size: 8pt; font-weight: bold; color: #be123c;">
      EA akan langsung menutup posisi untuk mengamankan profit yang ada daripada membiarkannya tergerus habis!
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 7: MANAJEMEN RISIKO & LOT ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 6: Manajemen Risiko, Lot & Pengamanan Akun</div>
    <div class="chapter-badge">Safety Rules</div>
  </div>

  <h2>1. Proteksi Menyesuaikan Minimal Lot Broker (Didimax Safeguard)</h2>
  <p>
    Setiap broker memiliki aturan ukuran lot minimal yang berbeda. Khusus pada broker lokal Indonesia seperti <strong>DIDIMAX</strong>, ukuran transaksi minimal untuk instrumen XAU/USD (Gold) adalah <strong>0.10 lot</strong> (bukan 0.01 lot mikro seperti broker luar).
  </p>
  <div class="card-highlight">
    <h3 style="margin: 0 0 4px 0;">Algoritma Normalisasi Lot Anti-Error:</h3>
    <div class="code-block">
// Cuplikan Logika Proteksi Lot pada VIKAR EA 4-Pillar Pro:
double brokerMinLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN); // Otomatis deteksi 0.10 di Didimax
double minLot = (InpMinLot > 0) ? MathMax(brokerMinLot, InpMinLot) : brokerMinLot;
if (maxLot < minLot) maxLot = minLot; // Proteksi anti-kontradiksi
double normalized = MathFloor(rawLot / stepLot) * stepLot;
if (normalized < minLot) normalized = minLot;
if (normalized > maxLot) normalized = maxLot;
    </div>
    <p style="margin: 0; font-size: 8pt;">
      Dengan arsitektur di atas, EA <strong>tidak akan pernah menghasilkan error 10014 (Invalid Volume)</strong> karena ukuran lot selalu mematuhi batas bawah minimal broker secara otomatis.
    </p>
  </div>

  <h2>2. Tiga Pilihan Model Perhitungan Lot</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Model Lot</th>
        <th style="width: 25%;">Parameter Input</th>
        <th>Deskripsi & Rekomendasi Penggunaan</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Minimal Lot Broker (Default)</strong></td>
        <td><code>InpLotType = 0</code></td>
        <td><strong>Paling Aman & Sangat Direkomendasikan!</strong> EA otomatis bertransaksi menggunakan lot terkecil yang diizinkan broker (0.10 lot di Didimax). Menjamin ketahanan modal maksimal.</td>
      </tr>
      <tr>
        <td><strong>Fixed Lot (Ukuran Tetap)</strong></td>
        <td><code>InpLotType = 1</code><br><code>InpFixedLot = 0.10</code></td>
        <td>Ukuran lot statis yang ditentukan sendiri oleh user. Dibatasi oleh pengaman <code>InpMaxLot</code> agar tidak terjadi kesalahan ketik lot besar.</td>
      </tr>
      <tr>
        <td><strong>Dynamic Risk % Balance</strong></td>
        <td><code>InpLotType = 2</code><br><code>InpRiskPercent = 1.0</code></td>
        <td>Lot dihitung otomatis berdasarkan persentase risiko modal per transaksi terhadap jarak Stop Loss. Cocok untuk akun modal besar di atas $10.000.</td>
      </tr>
    </tbody>
  </table>

  <h2>3. Perlindungan Margin Akun & Anti-Hedging</h2>
  <div class="grid-2">
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 4px 0;">Validasi Margin Sebelum Eksekusi</h3>
      <p style="font-size: 8pt; margin: 0;">
        Sebelum mengirim order ke server broker, EA memanggil fungsi <code>OrderCalcMargin()</code>. Jika sisa margin bebas (*Free Margin*) di akun tidak mencukupi, order langsung dibatalkan secara aman dengan peringatan di layar untuk mencegah *Margin Call*.
      </p>
    </div>

    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 4px 0;">Maksimal 1 Posisi Aktif (Anti-Hedging)</h3>
      <p style="font-size: 8pt; margin: 0;">
        Secara default, parameter <code>InpMaxOpenPositions = 1</code> membatasi hanya ada satu transaksi yang berjalan. EA tidak akan membuka posisi baru atau melakukan averaging liar sebelum posisi sebelumnya selesai (*Zero Martingale*).
      </p>
    </div>
  </div>

  <div class="card-warning">
    <h3 style="color: #b45309; margin: 0 0 4px 0;">🛡️ Filter Spread Maksimal (Anti-Slippage Malam Hari):</h3>
    <p style="margin: 0; font-size: 8pt;">
      Pada saat pergantian hari pasar (*Rollover* pk 04:00 - 06:00 WIB), spread broker seringkali melebar hingga puluhan pips. Fitur <code>InpMaxSpreadPips = 4.5 s/d 10.0</code> secara ketat menolak pembukaan order baru jika spread sedang tinggi untuk menghindari kerugian akibat biaya transaksi tersembunyi.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 8: PANDUAN INSTALASI MT5 ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 7: Panduan Instalasi Langkah-demi-Langkah di MT5</div>
    <div class="chapter-badge">Setup Guide</div>
  </div>

  <h2>Langkah 1: Membuka Folder Data MetaTrader 5</h2>
  <p>
    File EA dan Preset telah disalin otomatis oleh sistem ke direktori MT5 Anda. Namun untuk memastikan dan mengetahuinya:
  </p>
  <ol style="margin: 0 0 8px 0; padding-left: 18px;">
    <li>Buka aplikasi <strong>DIDIMAX MetaTrader 5</strong> pada komputer / laptop Windows Anda.</li>
    <li>Klik menu <strong>File</strong> pada pojok kiri atas &rarr; pilih <strong>Open Data Folder</strong>.</li>
    <li>Masuk ke folder <strong>MQL5</strong> &rarr; <strong>Experts</strong> &rarr; periksa keberadaan folder <strong>VIKAR_4Pillar_Pro</strong>.</li>
    <li>Pastikan file <code>VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5</code> dan file <code>.set</code> sudah berada di dalamnya.</li>
  </ol>

  <h2>Langkah 2: Mengaktifkan Algo Trading di Terminal MT5</h2>
  <div class="card-danger">
    <h3 style="color: #be123c; margin: 0 0 4px 0;">⚠️ PENTING: Pengaturan Wajib Terminal!</h3>
    <p style="font-size: 8pt; margin: 0 0 4px 0;">
      Jika tombol Algo Trading belum diaktifkan, robot tidak akan memiliki izin untuk membuka posisi:
    </p>
    <ul style="margin: 0; padding-left: 18px; font-size: 8pt;">
      <li>Klik menu <strong>Tools</strong> &rarr; <strong>Options</strong> (atau tekan shortcut <code>Ctrl + O</code>).</li>
      <li>Pilih tab <strong>Expert Advisors</strong>.</li>
      <li>Centang kotak: <strong>"Allow Algo Trading"</strong>.</li>
      <li>Centang kotak: <strong>"Allow DLL imports"</strong>.</li>
      <li>Pastikan tombol besar <strong>"Algo Trading"</strong> di toolbar atas MT5 berwarna <strong>HIJAU</strong> (bukan merah).</li>
    </ul>
  </div>

  <h2>Langkah 3: Memasang EA ke Grafik XAU/USD (Gold)</h2>
  <ol style="margin: 0 0 8px 0; padding-left: 18px;">
    <li>Buka jendela <strong>Market Watch</strong> (<code>Ctrl + M</code>) &rarr; klik kanan pada <code>XAUUSD</code> atau <code>GOLD</code> &rarr; pilih <strong>Chart Window</strong>.</li>
    <li>Ubah timeframe grafik menjadi <strong>M5</strong> (untuk Scalping Cepat) atau <strong>M15</strong> (untuk Day Trading).</li>
    <li>Buka jendela <strong>Navigator</strong> (<code>Ctrl + N</code>) &rarr; buka folder <strong>Experts</strong> &rarr; <strong>VIKAR_4Pillar_Pro</strong>.</li>
    <li>Klik dan seret (drag & drop) <strong>VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR</strong> ke dalam grafik XAUUSD Anda.</li>
  </ol>

  <h2>Langkah 4: Memuat File Preset Setting (.set)</h2>
  <div class="card-success">
    <h3 style="color: #15803d; margin: 0 0 4px 0;">Cara Memuat Preset Konfigurasi Resmi:</h3>
    <ol style="margin: 0; padding-left: 18px; font-size: 8pt;">
      <li>Pada jendela pop-up EA yang muncul, pilih tab <strong>Inputs</strong>.</li>
      <li>Klik tombol <strong>Load...</strong> di sebelah kanan bawah.</li>
      <li>Pilih salah satu file preset resmi sesuai preferensi Anda (misal: <code>XAUUSD_FAST_AUTO_TRADE.set</code>).</li>
      <li>Klik <strong>Open</strong>, lalu klik <strong>OK</strong>.</li>
      <li>Periksa pojok kanan atas grafik: Jika muncul nama EA dengan ikon topi berwarna biru/hijau, maka EA telah aktif sempurna!</li>
    </ol>
  </div>

  <div class="card">
    <h3 style="margin: 0 0 4px 0; color: #0284c7;">Status Ikon EA di Pojok Kanan Atas Chart:</h3>
    <table>
      <thead>
        <tr>
          <th>Ikon / Indikator</th>
          <th>Status Kerja</th>
          <th>Artinya & Tindakan yang Harus Dilakukan</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong style="color: #16a34a;">Topi Biru / Hijau</strong></td>
          <td><span class="badge badge-green">AKTIF NORMAL</span></td>
          <td>Robot berjalan dengan izin penuh, memantau sinyal setiap penutupan lilin.</td>
        </tr>
        <tr>
          <td><strong style="color: #dc2626;">Topi Abu-Abu / Silang Merah</strong></td>
          <td><span class="badge badge-red">TIDAK AKTIF</span></td>
          <td>Algo Trading mati atau opsi Allow Algo Trading di tab Common belum dicentang.</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<!-- ==================== HALAMAN 9: KATALOG 4 PRESET RESMI ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8: Katalog 4 Preset Resmi (.set)</div>
    <div class="chapter-badge">Presets Library</div>
  </div>

  <p>
    Tersedia <strong>4 file konfigurasi preset teruji</strong> yang telah dioptimalkan secara spesifik sesuai gaya dan profil risiko trader:
  </p>

  <div class="card-highlight">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
      <h3 style="margin: 0; color: #0369a1;">1. XAUUSD_FAST_AUTO_TRADE.set (Preset Auto-Trade Cepat & Aktif)</h3>
      <span class="badge badge-blue">Magic: 777101 | TF: M5</span>
    </div>
    <p style="font-size: 8pt; margin: 0 0 5px 0;">
      Dirancang untuk trader yang menginginkan transaksi lebih aktif dengan eksekusi cepat, penguncian profit dini, dan frekuensi sinyal lebih tinggi.
    </p>
    <div class="grid-3" style="font-size: 7.5pt; margin: 0;">
      <div><strong>Min Confluence:</strong> 60 Poin</div>
      <div><strong>Double Align:</strong> Fleksibel (false)</div>
      <div><strong>Auto BE (SL+):</strong> +8.0 Pips (Kunci +2.5p)</div>
      <div><strong>TP1 (Partial 50%):</strong> +10.0 Pips</div>
      <div><strong>Risk-Reward TP2:</strong> 1 : 1.5</div>
      <div><strong>Cooldown Bars:</strong> 2 Lilin</div>
    </div>
  </div>

  <div class="card-success">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
      <h3 style="margin: 0; color: #15803d;">2. XAUUSD_HIGH_WINRATE_SNIPER.set (Preset Ultra Winrate Grade A+)</h3>
      <span class="badge badge-green">Magic: 777108 | TF: M5</span>
    </div>
    <p style="font-size: 8pt; margin: 0 0 5px 0;">
      <strong>Preset paling disukai untuk ketahanan modal maksimal.</strong> Sangat selektif, hanya mengeksekusi setup Grade A+ yang memiliki konfluensi sempurna 4 pilar.
    </p>
    <div class="grid-3" style="font-size: 7.5pt; margin: 0;">
      <div><strong>Min Confluence:</strong> 80 Poin (Sniper)</div>
      <div><strong>Double Align:</strong> Wajib (EMA125 & Pivot P)</div>
      <div><strong>Golden Pocket:</strong> Wajib Sentuh Fibo 61.8%</div>
      <div><strong>Auto BE (SL+):</strong> +8.0 Pips (Kunci +3.0p)</div>
      <div><strong>TP1 (Partial 50%):</strong> +12.0 Pips</div>
      <div><strong>Risk-Reward TP2:</strong> 1 : 1.6</div>
    </div>
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
      <h3 style="margin: 0; color: #0f172a;">3. XAUUSD_M5_Scalping_Confluence.set (Preset Scalping Seimbang)</h3>
      <span class="badge badge-purple">Magic: 777105 | TF: M5</span>
    </div>
    <p style="font-size: 8pt; margin: 0 0 5px 0;">
      Keseimbangan ideal antara frekuensi trading harian dan rasio kemenangan pada timeframe M5. Memanfaatkan konfirmasi Macro Trend H1.
    </p>
    <div class="grid-3" style="font-size: 7.5pt; margin: 0;">
      <div><strong>Min Confluence:</strong> 65 Poin (Grade A)</div>
      <div><strong>Double Align:</strong> Wajib (true)</div>
      <div><strong>Auto BE (SL+):</strong> +12.0 Pips (Kunci +4.0p)</div>
      <div><strong>TP1 (Partial 50%):</strong> +15.0 Pips</div>
      <div><strong>Risk-Reward TP2:</strong> 1 : 1.8</div>
      <div><strong>Cooldown Bars:</strong> 3 Lilin</div>
    </div>
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
      <h3 style="margin: 0; color: #0f172a;">4. XAUUSD_M15_DayTrading_GradeA.set (Preset Trend Rider M15)</h3>
      <span class="badge badge-gold">Magic: 777115 | TF: M15</span>
    </div>
    <p style="font-size: 8pt; margin: 0 0 5px 0;">
      Dikhususkan untuk gaya Day Trading timeframe M15 yang memburu gelombang tren besar (*Large Swings*) dengan target profit hingga ratusan pips.
    </p>
    <div class="grid-3" style="font-size: 7.5pt; margin: 0;">
      <div><strong>Min Confluence:</strong> 70 Poin</div>
      <div><strong>Risk-Reward:</strong> 1 : 2.5 (Rasio Lebar)</div>
      <div><strong>Auto BE (SL+):</strong> +20.0 Pips (Kunci +6.0p)</div>
      <div><strong>TP1 (Partial 50%):</strong> +25.0 Pips</div>
      <div><strong>Trailing EMA 21:</strong> Aktif Buffer 6.0p</div>
      <div><strong>SL Range:</strong> 22 - 70 Pips</div>
    </div>
  </div>

  <div class="card-warning">
    <h3 style="color: #b45309; margin: 0 0 3px 0;">Tips Memilih Preset:</h3>
    <p style="margin: 0; font-size: 8pt;">
      Untuk akun pemula dengan saldo di bawah $2.000, mulailah dengan <strong>XAUUSD_FAST_AUTO_TRADE.set</strong> atau <strong>XAUUSD_HIGH_WINRATE_SNIPER.set</strong> pada timeframe M5 dengan ukuran lot minimal broker 0.10.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 10: MEMBACA DASHBOARD HUD ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 9: Membaca Layar Monitor Dashboard HUD</div>
    <div class="chapter-badge">Live Monitor</div>
  </div>

  <h2>Struktur Layar Dashboard HUD Real-Time</h2>
  <p>
    Di pojok kiri atas grafik MT5 Anda, EA menampilkan panel monitor interaktif (*Heads-Up Display*) yang diperbarui setiap 250ms tanpa membebani CPU komputer Anda:
  </p>

  <div class="code-block">
+========================================================================+
| VIKAR EA 4-PILLAR PRO  |  v2.1 Master  |  XAUUSD [M5]                 |
+========================================================================+
| Sinyal Terakhir   : BUY EXECUTED: Dragonfly Doji (Skor: 82)            |
| Konfluensi Setup  : GRADE A+ SNIPER (Total Skor: 85.0 / 100)           |
| Double Alignment  : SUPER BULLISH (Harga > EMA 125 & > Pivot P)        |
| Trend EMA 125     : BULLISH TREND (Baseline Putih Terjaga)             |
| Macro Trend (H1)  : BULLISH ALIGNED (Pita H1 EMA 8 > EMA 21)           |
| Struktur SMC      : BULLISH BOS (Expansion Phase)                      |
| Dealing Range     : DISCOUNT ZONE (50% Equilibrium Aman)               |
| Fibo Golden Pocket: DALAM GOLDEN POCKET (Pantulan Area 61.8%)          |
| Daily Pivot Point : CENTRAL PIVOT: 2654.20 | Headroom: 14.5 Pips       |
| Status Proteksi   : SL+: AKTIF | Trailing: EMA 21 | Lot: 0.10          |
| Riwayat Transaksi : Win: 14 | Loss: 2 | Win Rate: 87.5%                |
| Rekap Keuntungan  : Total PnL: +$428.50 | Hari Ini: +$84.20            |
+========================================================================+
  </div>

  <h2>Kamus Indikator Status Dashboard</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Baris Informasi</th>
        <th style="width: 25%;">Variasi Status</th>
        <th>Arti Analisis & Panduan untuk Trader</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Double Alignment</strong></td>
        <td><code>SUPER BULLISH</code><br><code>SUPER BEARISH</code><br><code>CONFLICT</code></td>
        <td>Jika muncul <code>CONFLICT</code>, harga berada di antara EMA 125 dan Pivot P harian. EA otomatis menahan diri (*Wait & See*).</td>
      </tr>
      <tr>
        <td><strong>Macro Trend (H1)</strong></td>
        <td><code>BULLISH ALIGNED</code><br><code>BEARISH ALIGNED</code><br><code>KONTRA HTF</code></td>
        <td>Jika H1 berbeda arah dengan M5, order dibatalkan otomatis demi mematuhi aturan keselarasan arus modal besar.</td>
      </tr>
      <tr>
        <td><strong>Dealing Range</strong></td>
        <td><code>DISCOUNT ZONE</code><br><code>PREMIUM ZONE</code></td>
        <td>BUY hanya dieksekusi di zona diskon (&lt; 50%). Jika harga berada di premium zone, sistem menolak entri beli.</td>
      </tr>
      <tr>
        <td><strong>Konfluensi Setup</strong></td>
        <td><code>GRADE A+ SNIPER</code><br><code>GRADE A HIGH PROB</code></td>
        <td>Menunjukkan kualitas gabungan seluruh pilar (0-100 poin). Skor di atas 80 poin merupakan sinyal elit berakurasi tinggi.</td>
      </tr>
      <tr>
        <td><strong>Win Rate (WR%)</strong></td>
        <td><code>WR: 85.0%</code></td>
        <td>Persentase kemenangan aktual yang dihitung otomatis dari riwayat transaksi tertutup (*Closed Deals*) pada akun Anda.</td>
      </tr>
    </tbody>
  </table>

  <h2>Pesan Live Fallback Khusus</h2>
  <div class="grid-2">
    <div class="card-highlight">
      <h3><code>FILTER: WHIPSAW DI EMA 125</code></h3>
      <p style="font-size: 8pt; margin: 0;">
        Harga sedang bolak-balik menembus EMA 125 (pasar sideways tanpa arah). EA menolak entri hingga tren jelas terbentuk kembali.
      </p>
    </div>
    <div class="card-warning">
      <h3><code>SHOCK GUARD: JEDA VOLATILITAS</code></h3>
      <p style="font-size: 8pt; margin: 0;">
        Terjadi lonjakan candle tajam pasca berita. EA menunggu 2 lilin jeda untuk memastikan pergerakan bukan jebakan *whipsaw*.
      </p>
    </div>
  </div>
</div>

<!-- ==================== HALAMAN 11: PANDUAN BACKTEST MT5 ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 10: Panduan Pengujian Backtest MT5</div>
    <div class="chapter-badge">Strategy Tester</div>
  </div>

  <h2>Langkah Menjalankan Backtest Presisi Tinggi</h2>
  <p>
    Untuk membuktikan keandalan logika EA sebelum terjun ke akun riil, lakukan simulasi backtest pada <strong>Strategy Tester MT5</strong>:
  </p>

  <ol style="margin: 0 0 10px 0; padding-left: 18px;">
    <li>Buka jendela Strategy Tester dengan menekan tombol <code>Ctrl + R</code>.</li>
    <li>Pada tab <strong>Settings</strong>, atur konfigurasi pengujian berikut:
      <ul style="margin: 4px 0; padding-left: 16px;">
        <li><strong>Expert:</strong> Pilih <code>VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5</code>.</li>
        <li><strong>Symbol:</strong> Pilih <code>XAUUSD</code> atau <code>GOLD</code>.</li>
        <li><strong>Period:</strong> Pilih <code>M5</code> (atau <code>M15</code> sesuai preset).</li>
        <li><strong>Date:</strong> Pilih rentang waktu pengujian (misal: 6 bulan s/d 1 tahun terakhir).</li>
        <li><strong>Forward:</strong> Pilih <code>No</code> (atau Custom Period).</li>
        <li><strong>Execution:</strong> Pilih <code>Random delay</code> (simulasi slippage pasar riil).</li>
        <li><strong>Model:</strong> <strong>"Every tick based on real ticks"</strong> (Paling akurat, menggunakan data tick riil broker).</li>
        <li><strong>Deposit:</strong> Atur modal awal (misal: $5.000 atau $10.000).</li>
        <li><strong>Leverage:</strong> Atur <code>1:100</code> (sesuai spesifikasi akun Didimax).</li>
      </ul>
    </li>
    <li>Klik tab <strong>Inputs</strong> &rarr; klik kanan &rarr; pilih <strong>Load</strong> &rarr; muat file <code>XAUUSD_HIGH_WINRATE_SNIPER.set</code> atau <code>XAUUSD_FAST_AUTO_TRADE.set</code>.</li>
    <li>Klik tombol <strong>Start</strong> di pojok kanan bawah untuk memulai proses backtest.</li>
  </ol>

  <h2>Metrik Utama yang Wajib Dievaluasi</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Metrik Kinerja</th>
        <th style="width: 25%;">Target Standar Vikar Pro</th>
        <th>Arti & Tolok Ukur Keberhasilan</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Win Rate (% Profit)</strong></td>
        <td><strong>&ge; 75.0% s/d 85.0%</strong></td>
        <td>Persentase transaksi menang lebih besar daripada transaksi kalah.</td>
      </tr>
      <tr>
        <td><strong>Profit Factor</strong></td>
        <td><strong>&gt; 2.00</strong></td>
        <td>Total keuntungan kotor dibagi total kerugian kotor. Nilai &gt; 2.0 membuktikan efisiensi strategi sangat sehat.</td>
      </tr>
      <tr>
        <td><strong>Max Drawdown (%)</strong></td>
        <td><strong>&lt; 10.0% s/d 15.0%</strong></td>
        <td>Penurunan modal terdalam dari titik puncak. Membuktikan modal terlindungi dari risiko kebangkrutan (*Ruin Risk*).</td>
      </tr>
      <tr>
        <td><strong>Expected Payoff</strong></td>
        <td><strong>Positif Signifikan</strong></td>
        <td>Rata-rata ekspektasi keuntungan bersih per transaksi yang dilakukan.</td>
      </tr>
    </tbody>
  </table>

  <div class="card-highlight">
    <h3 style="margin: 0 0 4px 0;">Grafik Ekuitas Sehat (Smooth Upward Slope):</h3>
    <p style="margin: 0; font-size: 8pt;">
      Ciri khas strategi 4 Pilar adalah kurva pertumbuhan ekuitas (*Equity Curve*) yang menanjak mulus ke kanan atas secara bertahap tanpa ada jurang curam mendadak. Hal ini terjadi berkat kombinasi Auto-Breakeven SL+, Partial Close 50%, dan ketiadaan sistem berbahaya seperti Martingale atau Grid.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 12: TROUBLESHOOTING & FAQ ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 11: Panduan Troubleshooting & FAQ</div>
    <div class="chapter-badge">Tanya Jawab</div>
  </div>

  <h2>Daftar Pertanyaan Umum & Solusi Masalah</h2>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 3px 0;">Q1: Kenapa EA belum membuka posisi sama sekali dalam beberapa jam?</h3>
    <p style="font-size: 8pt; margin: 0;">
      <strong>Jawaban:</strong> Ini adalah perilaku normal dan sangat sehat. VIKAR EA Pro adalah robot sniper yang <strong>hanya bertransaksi saat ada konfluensi Grade A/A+</strong>. Jika pasar sedang sideways, terjadi whipsaw di EMA 125, atau terjadi konflik antara tren EMA dan Daily Pivot P, EA dengan sengaja menahan diri untuk mengamankan modal Anda.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 3px 0;">Q2: Mengapa muncul pesan error 10014 (TRADE_RETCODE_INVALID_VOLUME)?</h3>
    <p style="font-size: 8pt; margin: 0;">
      <strong>Penyebab:</strong> Ukuran lot yang diminta lebih kecil dari batas minimal broker (Didimax mewajibkan minimal 0.10 lot).<br>
      <strong>Solusi:</strong> Pada versi <strong>v2.1 Audited</strong>, sistem telah dilengkapi *Safeguard Auto-Detection* sehingga masalah ini telah terselesaikan 100%. Pastikan parameter <code>InpLotType = LOT_TYPE_BROKER_MIN</code> atau <code>InpFixedLot = 0.10</code>.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 3px 0;">Q3: Apa yang dimaksud dengan error 10017 (TRADE_RETCODE_FROZEN)?</h3>
    <p style="font-size: 8pt; margin: 0;">
      <strong>Penyebab:</strong> Broker mengunci modifikasi SL/TP karena harga pasar sedang terlalu dekat dengan level pesanan (*Freeze Level*).<br>
      <strong>Solusi:</strong> Versi terbaru telah menyertakan proteksi <code>SYMBOL_TRADE_FREEZE_LEVEL</code> otomatis sehingga EA tidak akan mencoba memodifikasi SL saat harga berada di dalam zona beku broker.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 3px 0;">Q4: Apakah EA ini aman dijalankan di VPS (Virtual Private Server)?</h3>
    <p style="font-size: 8pt; margin: 0;">
      <strong>Jawaban:</strong> <strong>Sangat Direkomendasikan!</strong> Menggunakan VPS Windows dengan koneksi stabil menjamin EA dapat memantau pergerakan harga selama 24 jam penuh tanpa terputus masalah listrik padam atau koneksi internet rumah yang tidak stabil.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 3px 0;">Q5: Bolehkah saya melakukan intervensi manual menutup transaksi?</h3>
    <p style="font-size: 8pt; margin: 0;">
      <strong>Jawaban:</strong> Boleh, tetapi <strong>tidak disarankan secara acak</strong>. EA telah memiliki SOP Auto-Breakeven, Partial TP1, Trailing EMA 21, dan Auto-Cut Profit yang berjalan otomatis secara matematis. Biarkan sistem bekerja sesuai rencana trading yang telah teruji.
    </p>
  </div>

  <div class="card-warning">
    <h3 style="color: #b45309; margin: 0 0 3px 0;">Peringatan Risiko Penting (Disclaimer):</h3>
    <p style="margin: 0; font-size: 7.5pt; text-align: justify;">
      Trading instrumen derivatif dan komoditas emas (XAU/USD) mengandung risiko finansial yang tinggi akibat pengaruh pengungkit (*leverage*). Pastikan Anda selalu menggunakan dana yang siap Anda risikokan (*risk capital*), memahami aturan manajemen modal, dan telah melakukan pengujian menyeluruh pada akun demo sebelum mengaktifkannya pada akun riil.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 13: LEMBAR SOP CHECKLIST TRADER ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 12: Lembar Checklist & Disiplin Harian Trader</div>
    <div class="chapter-badge">SOP Harian</div>
  </div>

  <p>
    Cetak atau gunakan lembar checklist harian ini untuk memastikan seluruh prosedur operasional terpenuhi sebelum membiarkan EA bekerja:
  </p>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 6px 0;">📋 Checklist Persiapan Awal Sesi (pk 06:00 - 07:00 WIB):</h3>
    <table>
      <thead>
        <tr>
          <th style="width: 8%; text-align: center;">Status</th>
          <th style="width: 35%;">Item Pemeriksaan</th>
          <th>Standar Operasional Prosedur (SOP) Vikar Pro</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Koneksi Internet & VPS</td>
          <td>Ping ke server broker Didimax di bawah 50ms, status terminal terhubung hijau.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Tombol Algo Trading</td>
          <td>Tombol Algo Trading di toolbar berwarna HIJAU, ikon EA bertopi biru di pojok chart.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Timeframe & Simbol</td>
          <td>Grafik instrumen XAUUSD berada di timeframe M5 (atau M15 sesuai strategi).</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Pilihan Preset (.set)</td>
          <td>Preset <code>XAUUSD_FAST_AUTO_TRADE.set</code> atau <code>SNIPER</code> telah dimuat dengan benar.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Ukuran Lot Broker</td>
          <td>Parameter Lot diatur <code>LOT_TYPE_BROKER_MIN</code> (0.10 lot minimal Didimax).</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 6px 0;">⚡ Checklist Selama Sesi Berjalan (Monitoring Santai):</h3>
    <table>
      <thead>
        <tr>
          <th style="width: 8%; text-align: center;">Status</th>
          <th style="width: 35%;">Kondisi Pasar</th>
          <th>Tindakan Sistem & Sikap Trader</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Rilis Berita High Impact</td>
          <td>Shock Guard aktif otomatis. Jangan panik dan jangan matikan EA di tengah jalan.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Status Double Alignment</td>
          <td>Perhatikan apakah status SUPER BULLISH atau SUPER BEARISH untuk arah tren hari ini.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Posisi Terbuka Berjalan Profit</td>
          <td>Pastikan Auto-Breakeven menggeser SL ke SL+ setelah mencapai target trigger.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <div class="card-highlight">
    <h3 style="margin: 0 0 4px 0; color: #0284c7;">7 Kaidah Emas Psikologi Trader Profesional:</h3>
    <ol style="margin: 0; padding-left: 18px; font-size: 8pt; line-height: 1.4;">
      <li><strong>Percaya pada Statistik:</strong> Jangan menilai performa sistem hanya dari 1 atau 2 transaksi, lihat rata-rata 100 transaksi.</li>
      <li><strong>Kendalikan Keserakahan (*Anti-Greed*):</strong> Jangan pernah menaikkan lot secara sembarangan di luar aturan modal.</li>
      <li><strong>Disiplin Tanpa Emosi:</strong> Robot bekerja tanpa rasa takut atau serakah; tirulah ketenangan algoritma.</li>
      <li><strong>Hargai Waktu No-Trade:</strong> Menunggu tanpa posisi saat pasar konsolidasi adalah bagian dari seni menghasilkan keuntungan.</li>
      <li><strong>Fokus pada Proses, Bukan Uang:</strong> Eksekusi yang benar secara konsisten akan mendatangkan keuntungan finansial dengan sendirinya.</li>
    </ol>
  </div>
</div>

</body>
</html>
"""

temp_html_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\temp_ea_guide.html"
pdf_dest_proj = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf"
pdf_dest_terminal = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_4Pillar_Pro\PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf"
pdf_dest_artifact = os.path.join(artifact_dir, "PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf")

html_content = html_content.replace("__IMG_SMC_BOS__", img_smc_bos).replace("__IMG_SMC_CHOCH__", img_smc_choch)

with open(temp_html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_dest_proj}",
    temp_html_path
]

print("Converting HTML to PDF via Edge Headless...")
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(pdf_dest_proj):
    size = os.path.getsize(pdf_dest_proj)
    print(f"SUCCESS: PDF created at: {pdf_dest_proj} ({size} bytes)")
    
    # Copy to terminal and artifact
    import shutil
    shutil.copy2(pdf_dest_proj, pdf_dest_terminal)
    shutil.copy2(pdf_dest_proj, pdf_dest_artifact)
    print(f"Synced to Didimax MT5: {pdf_dest_terminal}")
    print(f"Synced to Artifact: {pdf_dest_artifact}")

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)
else:
    print("FAILED to create PDF.")
    print("Return code:", res.returncode)
    print("Stdout:", res.stdout)
    print("Stderr:", res.stderr)
