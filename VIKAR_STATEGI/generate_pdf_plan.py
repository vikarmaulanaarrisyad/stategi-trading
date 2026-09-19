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
img_real1 = image_to_base64(os.path.join(artifact_dir, ".user_uploaded", "media_1789627268394.png"))
img_real2 = image_to_base64(os.path.join(artifact_dir, ".user_uploaded", "media_1789631793548.png"))
img_real3 = image_to_base64(os.path.join(artifact_dir, ".user_uploaded", "media_1789639086722.png"))
img_real4 = image_to_base64(os.path.join(artifact_dir, "chart_annotated_smc_case4.png"))
img_smc_bos = image_to_base64(os.path.join(artifact_dir, "smc_bos_inducement_pattern_1789635642712.jpg"))
img_smc_choch = image_to_base64(os.path.join(artifact_dir, "smc_choch_reversal_pattern_1789635661082.jpg"))

html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>TRADING PLAN INSTITUSIONAL - VIKAR STRATEGY PRO</title>
<style>
  @page {{
    size: A4;
    margin: 14mm 14mm 16mm 14mm;
    @bottom-right {{
      content: "Halaman " counter(page);
      font-size: 8pt;
      color: #64748b;
    }}
    @bottom-left {{
      content: "VIKAR TRIPLE EMA & PIVOTS PRO | INSTITUTIONAL TRADING PLAN & REAL-MARKET STUDY";
      font-size: 8pt;
      color: #64748b;
      font-weight: bold;
    }}
  }}
  
  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.45;
    font-size: 9pt;
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

  /* Header & Titles */
  .cover {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 940px;
    text-align: center;
    background: linear-gradient(145deg, #0f172a 0%, #1e293b 60%, #0369a1 100%);
    color: #ffffff;
    border-radius: 12px;
    padding: 30px 25px;
    box-sizing: border-box;
  }}

  .cover-badge {{
    background-color: rgba(2, 132, 199, 0.3);
    border: 1px solid #38bdf8;
    color: #38bdf8;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 25px;
  }}

  .cover-title {{
    font-size: 26pt;
    font-weight: 800;
    line-height: 1.2;
    margin: 0 0 15px 0;
    background: linear-gradient(to right, #38bdf8, #f43f5e, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}

  .cover-subtitle {{
    font-size: 12.5pt;
    color: #cbd5e1;
    max-width: 650px;
    margin: 0 0 35px 0;
    font-weight: 400;
  }}

  .cover-meta-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
    width: 90%;
    max-width: 600px;
    margin-top: 25px;
    text-align: left;
  }}

  .cover-meta-card {{
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 12px 18px;
    border-radius: 8px;
  }}

  .cover-meta-label {{
    font-size: 7.5pt;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
  }}

  .cover-meta-val {{
    font-size: 10pt;
    color: #ffffff;
    font-weight: 700;
    margin-top: 3px;
  }}

  /* Headings */
  h1 {{
    font-size: 15pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 5px;
    margin-top: 0;
    margin-bottom: 12px;
  }}

  h2 {{
    font-size: 11pt;
    font-weight: 700;
    color: #0369a1;
    margin-top: 12px;
    margin-bottom: 6px;
  }}

  h3 {{
    font-size: 9.5pt;
    font-weight: 700;
    color: #334155;
    margin-top: 8px;
    margin-bottom: 4px;
  }}

  /* Badges */
  .badge {{
    display: inline-block;
    padding: 2px 7px;
    font-size: 7pt;
    font-weight: 700;
    border-radius: 4px;
    text-transform: uppercase;
  }}
  .badge-buy {{ background-color: #dcfce7; color: #166534; border: 1px solid #86efac; }}
  .badge-sell {{ background-color: #ffe4e6; color: #9f1239; border: 1px solid #fca5a5; }}
  .badge-bos {{ background-color: #e0f2fe; color: #075985; border: 1px solid #7dd3fc; }}
  .badge-choch {{ background-color: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }}
  .badge-gold {{ background-color: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }}
  .badge-fibo {{ background-color: #fef08a; color: #854d0e; border: 1px solid #eab308; }}

  /* Tables */
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 12px 0;
    font-size: 8pt;
  }}

  th, td {{
    border: 1px solid #cbd5e1;
    padding: 5px 8px;
    text-align: left;
  }}

  th {{
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
  }}

  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* Boxes & Callouts */
  .box {{
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #0284c7;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 8px 0;
  }}

  .box-warning {{
    background-color: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 4px solid #e11d48;
    color: #881337;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 8px 0;
  }}

  .box-success {{
    background-color: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
    color: #14532d;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 8px 0;
  }}

  .box-fibo {{
    background-color: #fefce8;
    border: 1px solid #fef08a;
    border-left: 4px solid #eab308;
    color: #713f12;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 8px 0;
  }}

  /* Grid layouts */
  .grid-2 {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }}

  .grid-3 {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }}

  .card {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}

  .card-title {{
    font-weight: 700;
    font-size: 9pt;
    color: #0f172a;
    margin-bottom: 3px;
  }}

  /* Image Containers */
  .chart-img-container {{
    text-align: center;
    margin: 6px 0;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    overflow: hidden;
    background-color: #0f172a;
  }}

  .chart-img-container img {{
    width: 100%;
    max-height: 235px;
    object-fit: contain;
    display: block;
  }}

  .chart-caption {{
    background-color: #1e293b;
    color: #94a3b8;
    font-size: 7.2pt;
    padding: 4px 8px;
    text-align: center;
    border-top: 1px solid #334155;
  }}

  ul, ol {{
    margin: 3px 0 6px 16px;
    padding: 0;
  }}

  li {{
    margin-bottom: 2px;
  }}
</style>
</head>
<body>

  <!-- ==================== HALAMAN 1: COVER ==================== -->
  <div class="page">
    <div class="cover">
      <div class="cover-badge">Unified 4-Pillar Institutional Trading System</div>
      <div class="cover-title">VIKAR 4-PILLAR PRO:<br>SMC CORE • S/R • EMA • FIBONACCI</div>
      <div class="cover-subtitle">
        Buku Panduan Standar Operasional Prosedur (SOP) Institusional: Smart Money Concepts (SMC) sebagai Core Pondasi, Support & Resistance Statis, Triple Exponential Moving Average (EMA), dan Akurasi Presisi Fibonacci Retracement Golden Pocket
      </div>

      <div class="cover-meta-grid">
        <div class="cover-meta-card">
          <div class="cover-meta-label">Arsitektur 4 Pilar</div>
          <div class="cover-meta-val">SMC Core + S/R + Triple EMA + Auto Fibo</div>
        </div>
        <div class="cover-meta-card">
          <div class="cover-meta-label">Timeframe Eksekusi</div>
          <div class="cover-meta-val">M5 (Scalping) & M15 (Day Trade)</div>
        </div>
        <div class="cover-meta-card">
          <div class="cover-meta-label">Aset Utama</div>
          <div class="cover-meta-val">Gold (XAUUSD), EURUSD, GBPUSD</div>
        </div>
        <div class="cover-meta-card">
          <div class="cover-meta-label">Target Rasio Resiko</div>
          <div class="cover-meta-val">Min. 1:2 s/d 1:3.5 Risk to Reward (R:R)</div>
        </div>
      </div>

      <div style="margin-top: 50px; font-size: 8pt; color: #64748b; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 15px; width: 80%;">
        Disusun khusus untuk eksekusi Akun Real | Zero-Repaint Bar Close Rule | Real-Market Case Studies Included
      </div>
    </div>
  </div>

  <!-- ==================== HALAMAN 2: FILOSOFI & MINDSET ==================== -->
  <div class="page">
    <h1>1. Filosofi & Mindset Trader Profesional</h1>
    
    <p>
      Mayoritas 90% trader retail mengalami kerugian karena bertindak berdasarkan emosi: takut ketinggalan momen (FOMO), membeli di puncak kenaikan, atau menjual di dasar penurunan. 
      Sistem <strong>VIKAR 4-Pillar Pro</strong> dirancang dengan prinsip institusional: <em>"Beli di Area Diskon saat Tren Naik, dan Jual di Area Premium saat Tren Turun dengan Multi-Konfluensi."</em>
    </p>

    <div class="box-success">
      <strong>Hukum Emas VIKAR Strategy:</strong><br>
      • <strong>SMC Core:</strong> Struktur pasar (BOS/CHoCH) dan sapuan likuiditas menentukan arah uang pintar (<em>Smart Money</em>).<br>
      • <strong>Support & Resistance:</strong> Daily Pivot Points dan 3 Level Kunci menjadi pembatas lantai, atap, dan status <em>Double Alignment</em>.<br>
      • <strong>Triple EMA:</strong> EMA 125 sebagai filter arah besar, dan Ribbon EMA 8–21 sebagai dynamic support/resistance dan trailing stop.<br>
      • <strong>Fibonacci Retracement:</strong> Golden Pocket (0.500–0.786) memastikan harga masuk di diskon terbaik dengan target ekstensi presisi.
    </div>

    <h2>Perbandingan Pola Pikir: Retail vs Profesional</h2>
    <table>
      <thead>
        <tr>
          <th style="width: 20%;">Aspek</th>
          <th style="width: 40%;">Retail Trader Pemula (Rugi)</th>
          <th style="width: 40%;">Trader Profesional VIKAR (Profit Konsisten)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Aksi saat Breakout</strong></td>
          <td>Langsung BUY saat melihat candle hijau panjang (FOMO pucuk).</td>
          <td>Tandai struktur BOS, lalu <strong>sabar menunggu harga terkoreksi (pullback)</strong>.</td>
        </tr>
        <tr>
          <td><strong>Lokasi Masuk (Entry)</strong></td>
          <td>Di sembarang titik di tengah pergerakan pasar.</td>
          <td>Hanya di <strong>Area of Value</strong> (Ribbon EMA 8–21, Golden Pocket, dan Pivot).</td>
        </tr>
        <tr>
          <td><strong>Konfirmasi Sinyal</strong></td>
          <td>Masuk terburu-buru saat candle masih bergerak (rawan repaint).</td>
          <td>Wajib menunggu candle <strong>tertutup resmi (Bar Close)</strong>.</td>
        </tr>
        <tr>
          <td><strong>Penempatan Stop Loss</strong></td>
          <td>Sangat sempit (asal taruh) atau digeser-geser saat floating minus.</td>
          <td>Di balik <strong>Structure Swing Fractal + 1.2x ATR buffer</strong> (tahan spread & noise).</td>
        </tr>
        <tr>
          <td><strong>Manajemen Resiko</strong></td>
          <td>Menggunakan lot besar tanpa hitungan resiko (Overlot).</td>
          <td>Resiko dibatasi <strong>maksimal 1% – 2%</strong> modal per transaksi.</td>
        </tr>
      </tbody>
    </table>

    <h2>3 Pilar Kesuksesan Trading (The Holy Trinity)</h2>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">1. Trading Edge (30%)</div>
        <p style="font-size: 7.5pt; color: #475569; margin: 0;">
          Kombinasi matematis 4 Pilar: SMC Core, S/R Pivot, Triple EMA, dan Auto-Fibonacci.
        </p>
      </div>
      <div class="card">
        <div class="card-title">2. Money Management (40%)</div>
        <p style="font-size: 7.5pt; color: #475569; margin: 0;">
          Rasio Risk to Reward minimal 1:2, proteksi BEP pada 1:1, serta formula lot size terukur.
        </p>
      </div>
      <div class="card">
        <div class="card-title">3. Disiplin Psikologi (30%)</div>
        <p style="font-size: 7.5pt; color: #475569; margin: 0;">
          Ketegasan untuk <em>tidak trading</em> saat pasar sideways atau 30 menit menjelang berita High-Impact.
        </p>
      </div>
    </div>
  </div>

  <!-- ==================== HALAMAN 3: ARSITEKTUR 4 PILAR ==================== -->
  <div class="page">
    <h1>2. Arsitektur 4 Pilar Terpadu: SMC Core, S/R, Triple EMA, & Fibonacci</h1>

    <p>Indikator <code>VIKAR_Triple_EMA_Pivots.pine</code> mengintegrasikan 4 modul canggih yang bekerja serasi tanpa tumpang tindih:</p>

    <div class="card" style="margin-bottom: 8px; border-left: 4px solid #6b21a8;">
      <div class="card-title" style="color: #6b21a8;">Pilar 1 (CORE UTAMA): Smart Money Concepts (SMC) Market Structure</div>
      <ul style="font-size: 7.8pt;">
        <li><strong>BOS (Break of Structure):</strong> Penembusan puncak/lembah sebelumnya searah tren (tanda kelanjutan tren institusional sehat).</li>
        <li><strong>CHoCH (Change of Character):</strong> Penembusan struktur berlawanan arah dengan tren sebelumnya (peringatan awal pembalikan arah tren).</li>
        <li><strong>Liquidity Sweep (Stop Hunt):</strong> Sumbu lilin (*wick*) menusuk menembus ayunan fractal untuk menyapu Stop Loss retail sebelum berbalik arah tajam (*V-shape*).</li>
        <li><strong>Premium vs Discount Pricing:</strong> Membagi dealing range menjadi area Murah (Diskon < 50% untuk BUY) dan area Mahal (Premium > 50% untuk SELL).</li>
      </ul>
    </div>

    <div class="card" style="margin-bottom: 8px; border-left: 4px solid #b45309;">
      <div class="card-title" style="color: #b45309;">Pilar 2: Support & Resistance (Pivot Points & 3 Level Kunci)</div>
      <ul style="font-size: 7.8pt;">
        <li><strong>Daily Pivot Points Statis:</strong> Level P (Central Pivot), Support (S1–S5), dan Resistance (R1–R5) acuan likuiditas bank.</li>
        <li><strong>3 Level Kunci Visual:</strong> Garis abu-abu <em>Tertinggi Resistance</em>, garis solid biru <em>Pivot</em>, dan garis abu-abu <em>Terendah Support</em>.</li>
        <li><strong>Double Alignment Rule:</strong> Jika harga berada di atas EMA 125 DAN di atas Pivot Biru = Status <strong>SUPER BULLISH (Grade A+)</strong>.</li>
        <li><strong>Headroom Filter:</strong> Menjamin ada ruang minimal 0.8x ATR sebelum menyentuh tembok Pivot penghalang berikutnya.</li>
      </ul>
    </div>

    <div class="card" style="margin-bottom: 8px; border-left: 4px solid #0369a1;">
      <div class="card-title" style="color: #0369a1;">Pilar 3: Exponential Moving Average (Triple EMA 8, 21, 125)</div>
      <ul style="font-size: 7.8pt;">
        <li><strong>EMA 125 Putih (Institutional Baseline):</strong> Filter tren utama. Di atas EMA 125 = hanya BUY; di bawah = hanya SELL.</li>
        <li><strong>Ribbon EMA 8 Cyan & EMA 21 Magenta:</strong> Dynamic S/R Value Zone tempat terjadinya pemantulan (*pullback bounce*).</li>
        <li><strong>Trailing Stop EMA 21:</strong> Selama candle belum pernah Bar Close di bawah Ribbon EMA 21, posisi ditahan (*Hold*) untuk menangkap reli panjang.</li>
      </ul>
    </div>

    <div class="card" style="border-left: 4px solid #eab308;">
      <div class="card-title" style="color: #854d0e;">Pilar 4: Fibonacci Retracement & Auto Golden Pocket</div>
      <ul style="font-size: 7.8pt;">
        <li><strong>Golden Pocket Zone (0.500 - 0.618 - 0.786):</strong> Ditarik dari Swing Low ke Swing High struktur SMC aktif untuk menentukan titik presisi pembalikan.</li>
        <li><strong>Target Ekstensi TP Bertingkat:</strong> Level 0.000 (TP1 / Swing High), Fibo Ext -0.272 (TP2), dan Fibo Ext -0.618 (TP3 Ekspansi).</li>
        <li><strong>Fitur Auto-Fibonacci:</strong> Otomatis menghitung dan menampilkan shading Golden Pocket & target ekstensi langsung di chart.</li>
      </ul>
    </div>
  </div>

  <!-- ==================== HALAMAN 4: MASTERCLASS VISUAL SMC ==================== -->
  <div class="page">
    <h1>2.1. Masterclass Visual SMC: Siklus BOS, Inducement (IDM), & CHoCH</h1>

    <div class="grid-2" style="gap: 10px; margin-bottom: 6px;">
      <!-- KOLOM KIRI: BOS & INDUCEMENT -->
      <div>
        <div class="chart-img-container" style="margin: 0 0 4px 0;">
          <img src="{img_smc_bos}" alt="SMC BOS & Inducement Diagram" style="max-height: 185px;">
          <div class="chart-caption">
            Gambar 2.1: Siklus Uptrend SMC — BOS, Penjebakan Inducement (IDM), Sapuan Stop Hunt, dan Rebound di Order Block / Golden Pocket.
          </div>
        </div>
        <div class="card" style="border-left: 3px solid #0284c7; padding: 6px 8px;">
          <div class="card-title" style="color: #0369a1; font-size: 8pt;">A. ANATOMI BOS & INDUCEMENT (IDM)</div>
          <ul style="font-size: 7pt; margin-left: 12px; margin-bottom: 0;">
            <li><strong>Higher High (HH) Sah:</strong> Puncak baru HANYA sah diakui jika harga berhasil turun menyapu level <em>Inducement (IDM)</em> pertama.</li>
            <li><strong>Jebakan Retail di IDM:</strong> Trader pemula buru-buru BUY di garis IDM karena mengira itu support. Institusi sengaja menyapu level ini (*Stop Hunt*).</li>
            <li><strong>Titik Eksekusi Emas:</strong> Institusi memborong order BUY saat harga masuk ke area <strong>Order Block / Fibo Golden Pocket</strong> lalu melesat mencetak <strong>BOS</strong> berikutnya.</li>
          </ul>
        </div>
      </div>

      <!-- KOLOM KANAN: CHOCH & REVERSAL -->
      <div>
        <div class="chart-img-container" style="margin: 0 0 4px 0;">
          <img src="{img_smc_choch}" alt="SMC CHoCH Reversal Diagram" style="max-height: 185px;">
          <div class="chart-caption">
            Gambar 2.2: Siklus Reversal SMC — Sapuan Likuiditas Pucuk (BSL Hunt), Terjadinya CHoCH (Penembusan HL), dan Mitigasi Bearish FVG/OB.
          </div>
        </div>
        <div class="card" style="border-left: 3px solid #f43f5e; padding: 6px 8px;">
          <div class="card-title" style="color: #b91c1c; font-size: 8pt;">B. ANATOMI CHoCH & LIQUIDITY SWEEP</div>
          <ul style="font-size: 7pt; margin-left: 12px; margin-bottom: 0;">
            <li><strong>Liquidity Sweep Pucuk:</strong> Sumbu lilin menusuk ke atas puncak (*BSL Hunt*) untuk menyapu Stop Loss para seller retail sebelum harga berbalik.</li>
            <li><strong>Konfirmasi CHoCH:</strong> Terjadi penurunan agresif (*Displacement*) yang <strong>Bar Close resmi di bawah Higher Low (HL) terakhir</strong>. Tren naik resmi gugur!</li>
            <li><strong>Entri Re-Test:</strong> Tunggu harga terkoreksi naik menguji kembali zona <strong>Bearish Order Block / Fair Value Gap (FVG)</strong> untuk membuka posisi SELL.</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="card" style="border-top: 3px solid #eab308; padding: 5px 10px;">
      <div class="card-title" style="color: #854d0e; font-size: 8.5pt;">C. HUKUM MUTLAK EKSEKUSI SMART MONEY CONCEPTS (SMC)</div>
      <p style="font-size: 7.2pt; color: #1e293b; margin: 2px 0;">
        • <strong>Dilarang Beli di Pucuk BOS:</strong> Trader amatir membeli saat candle hijau besar menembus resisten. Trader profesional menandai BOS, lalu sabar menunggu sapuan Inducement masuk ke zona diskon.<br>
        • <strong>Konfirmasi Body Close vs Wick:</strong> Penembusan dengan ekor sumbu (*wick*) adalah <em>Liquidity Sweep</em>. Penembusan resmi dengan bodi lilin penuh (*body close*) barulah sah diakui sebagai <strong>BOS</strong> atau <strong>CHoCH</strong>!
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN 5: SOP EKSEKUSI 4 PILAR ==================== -->
  <div class="page">
    <h1>3. Standard Operating Procedure (SOP) Eksekusi 4 Pilar Terpadu</h1>

    <p>Sebelum membuka posisi apapun pada MetaTrader atau platform broker Anda, pastikan seluruh 4 pilar telah selaras:</p>

    <div class="grid-2">
      <!-- BUY SOP -->
      <div class="card" style="border-top: 4px solid #10b981;">
        <div class="card-title" style="color: #047857;">SOP EKSEKUSI BUY (Grade A+ Setup)</div>
        <ol style="margin-left: 14px; font-size: 7.8pt;">
          <li><strong>Pilar 1 (SMC Core):</strong> Terkonfirmasi struktur <strong>BULLISH BOS</strong> atau <strong>BULLISH CHoCH</strong>. Lebih utama jika didahului <em>Liquidity Sweep</em> pada Swing Low. Dilarang membeli saat breakout puncak.</li>
          <li><strong>Pilar 2 (S/R Statis):</strong> Posisi harga berada di atas garis <strong>Pivot Biru harian</strong> (*Double Alignment*), dengan Headroom ke resisten R1 minimal 0.8x ATR.</li>
          <li><strong>Pilar 3 (EMA Dynamic):</strong> Bodi candle wajib di atas <strong>EMA 125 Putih</strong> (miring ke atas), dan koreksi turun masuk ke celah <strong>Ribbon EMA 8 & 21</strong>.</li>
          <li><strong>Pilar 4 (Fibonacci GP):</strong> Titik pantulan wajib bersarang di area <strong>Golden Pocket (0.500–0.786)</strong>.</li>
          <li><strong>Pemicu Eksekusi:</strong> Muncul pola Hammer / Bullish Engulfing yang <strong>Bar Close resmi di atas EMA 21</strong>.</li>
        </ol>
      </div>

      <!-- SELL SOP -->
      <div class="card" style="border-top: 4px solid #f43f5e;">
        <div class="card-title" style="color: #b91c1c;">SOP EKSEKUSI SELL (Grade A+ Setup)</div>
        <ol style="margin-left: 14px; font-size: 7.8pt;">
          <li><strong>Pilar 1 (SMC Core):</strong> Terkonfirmasi struktur <strong>BEARISH BOS</strong> atau <strong>BEARISH CHoCH</strong>. Lebih utama jika didahului <em>Liquidity Sweep</em> pada Swing High. Dilarang menjual di dasar lembah.</li>
          <li><strong>Pilar 2 (S/R Statis):</strong> Posisi harga berada di bawah garis <strong>Pivot Biru harian</strong> (*Double Alignment*), dengan Headroom ke support S1 minimal 0.8x ATR.</li>
          <li><strong>Pilar 3 (EMA Dynamic):</strong> Bodi candle wajib di bawah <strong>EMA 125 Putih</strong> (menukik ke bawah), dan koreksi naik menyentuh bawah <strong>Ribbon EMA 8 & 21</strong>.</li>
          <li><strong>Pilar 4 (Fibonacci GP):</strong> Titik penolakan wajib bersarang di area <strong>Golden Pocket (0.500–0.786)</strong>.</li>
          <li><strong>Pemicu Eksekusi:</strong> Muncul pola Shooting Star / Bearish Engulfing yang <strong>Bar Close resmi di bawah EMA 21</strong>.</li>
        </ol>
      </div>
    </div>

    <h2>Ringkasan Titik Eksekusi Order:</h2>
    <table>
      <thead>
        <tr>
          <th>Komponen</th>
          <th>Posisi BUY</th>
          <th>Posisi SELL</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Entry Price</strong></td>
          <td>Harga penutupan (Close) candle rejection konfirmasi.</td>
          <td>Harga penutupan (Close) candle rejection konfirmasi.</td>
        </tr>
        <tr>
          <td><strong>Stop Loss (SL)</strong></td>
          <td>Di balik <strong>Structure Swing Low</strong> / Fibo 1.0 + 1.2x ATR buffer.</td>
          <td>Di balik <strong>Structure Swing High</strong> / Fibo 1.0 + 1.2x ATR buffer.</td>
        </tr>
        <tr>
          <td><strong>Breakeven (BEP)</strong></td>
          <td>Geser SL ke Entry saat floating profit mencapai <strong>1:1 R:R</strong>.</td>
          <td>Geser SL ke Entry saat floating profit mencapai <strong>1:1 R:R</strong>.</td>
        </tr>
        <tr>
          <td><strong>Take Profit (TP)</strong></td>
          <td>Target 1: Swing High (0.0). Target 2: Fibo Ext -0.272. Target 3: -0.618.</td>
          <td>Target 1: Swing Low (0.0). Target 2: Fibo Ext -0.272. Target 3: -0.618.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ==================== HALAMAN 5: KONDISI PASAR ENTRY BUY & SELL ==================== -->
  <div class="page">
    <h1>4. Kondisi Pasar Ideal Entry BUY & SELL</h1>

    <p style="margin-bottom: 8px;">
      Trader institusional tidak pernah memaksakan trading di sembarang waktu. Keuntungan konsisten lahir dari kemampuan menyaring dan hanya mengeksekusi saat <strong>rezim pasar berada pada probabilitas tertinggi (A+ Setup)</strong>:
    </p>

    <div class="grid-2" style="margin-bottom: 8px;">
      <!-- KONDISI PASAR BUY -->
      <div class="card" style="border-top: 3px solid #10b981; padding: 8px 10px;">
        <div class="card-title" style="color: #047857; font-size: 9pt; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <span>KAPAN ENTRY BUY DIIZINKAN?</span>
          <span class="badge badge-buy">Markup Phase</span>
        </div>
        <ul style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Rezim Tren:</strong> Harga di atas <strong>EMA 125 Putih</strong> dan garis EMA miring stabil ke atas (+30° s/d +45°).</li>
          <li><strong>Struktur SMC:</strong> Rangkaian <strong>Higher High (HH) & Higher Low (HL)</strong>, disusul <strong>Bullish BOS</strong> resmi.</li>
          <li><strong>Fase Retracement:</strong> Koreksi harga murah santai menuju <strong>Area Diskon Fibo</strong> (< 50% dealing range).</li>
          <li><strong>Zona Value:</strong> Lilin menyentuh <strong>Ribbon EMA 8–21</strong> atau memantul di lantai <strong>Pivot (P / S1)</strong>.</li>
          <li><strong>Trigger Lilin:</strong> Pola Hammer / Bullish Engulfing yang <strong>Bar Close resmi di atas EMA 21</strong>.</li>
          <li><strong>Headroom Bebas:</strong> Jarak ke resisten Pivot berikutnya minimal <strong>0.8x ATR</strong>.</li>
          <li><strong>Sesi Terbaik:</strong> London (14:00–18:00 WIB) & New York (19:00–23:00 WIB).</li>
        </ul>
      </div>

      <!-- KONDISI PASAR SELL -->
      <div class="card" style="border-top: 3px solid #f43f5e; padding: 8px 10px;">
        <div class="card-title" style="color: #b91c1c; font-size: 9pt; display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <span>KAPAN ENTRY SELL DIIZINKAN?</span>
          <span class="badge badge-sell">Markdown Phase</span>
        </div>
        <ul style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Rezim Tren:</strong> Harga di bawah <strong>EMA 125 Putih</strong> dan garis EMA menukik tajam ke bawah.</li>
          <li><strong>Struktur SMC:</strong> Rangkaian <strong>Lower High (LH) & Lower Low (LL)</strong>, disusul <strong>Bearish BOS</strong> resmi.</li>
          <li><strong>Fase Retracement:</strong> Rebound santai ke <strong>Area Premium Fibo</strong> (> 50% dealing range) untuk menjebak ritel.</li>
          <li><strong>Zona Value:</strong> Lilin membentur bagian bawah <strong>Ribbon EMA 8–21</strong> atau resisten <strong>Pivot (P / R1)</strong>.</li>
          <li><strong>Trigger Lilin:</strong> Pola Shooting Star / Bearish Engulfing yang <strong>Bar Close resmi di bawah EMA 21</strong>.</li>
          <li><strong>Headroom Bebas:</strong> Jarak ke support Pivot berikutnya minimal <strong>0.8x ATR</strong>.</li>
          <li><strong>Sesi Terbaik:</strong> London (14:00–18:00 WIB) & New York (19:00–23:00 WIB).</li>
        </ul>
      </div>
    </div>

    <h2>Matriks Perbandingan: Kondisi Pasar Boleh Entry vs Dilarang Entry</h2>
    <table style="font-size: 7.8pt; margin-bottom: 6px;">
      <thead>
        <tr>
          <th style="width: 22%;">Parameter Pasar</th>
          <th style="width: 39%; color: #047857;">Kondisi Prima (BOLEH ENTRY)</th>
          <th style="width: 39%; color: #b91c1c;">Kondisi Rawan (DILARANG ENTRY)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Arah & Kemiringan EMA 125</strong></td>
          <td>Miring tajam ke atas (BUY) atau ke bawah (SELL).</td>
          <td>Datar horizontal, berbelit kusut dengan EMA 8 & 21.</td>
        </tr>
        <tr>
          <td><strong>Struktur Ayunan SMC</strong></td>
          <td>BOS searah tren telah terkonfirmasi dengan candle tegas.</td>
          <td>Tidak ada BOS, harga bolak-balik menembus swing tanpa arah.</td>
        </tr>
        <tr>
          <td><strong>Lokasi Harga Terhadap EMA</strong></td>
          <td>Menyentuh Ribbon EMA 8–21 (jarak ke EMA 125 ≤ 2.5x ATR).</td>
          <td>Overextended (> 2.5x ATR) atau harga memotong bolak-balik.</td>
        </tr>
        <tr>
          <td><strong>Jarak ke Pivot Terdekat</strong></td>
          <td>Headroom longgar (≥ 0.8x ATR sebelum Pivot berikutnya).</td>
          <td>Sangat sempit (< 0.8x ATR), membentur dinding Pivot keras.</td>
        </tr>
        <tr>
          <td><strong>Waktu & Kalender Berita</strong></td>
          <td>Sesi London / New York, tidak ada berita High-Impact.</td>
          <td>Sesi sepi / rollover (04:00–06:00 WIB) atau ada berita CPI/NFP.</td>
        </tr>
      </tbody>
    </table>

    <div class="box-success" style="padding: 5px 10px; font-size: 7.8pt; margin-top: 2px;">
      <strong>Prinsip Emas Institusional:</strong> Menunggu kondisi pasar yang tepat membutuhkan 90% waktu Anda. Keberhasilan trading ditentukan oleh kesabaran menunggu setup yang memenuhi seluruh checklist di atas.
    </div>
  </div>

  <!-- ==================== HALAMAN 6: FIBONACCI RETRACEMENT MASTERCLASS ==================== -->
  <div class="page">
    <h1>5. Panduan Penarikan Fibonacci Retracement & Multi-Konfluensi</h1>

    <p style="margin-bottom: 6px;">
      Fibonacci Retracement adalah instrumen matematis yang digunakan oleh bank sentral dan institusi global untuk mengukur seberapa jauh harga terkoreksi sebelum melanjutkan tren utamanya. 
      Dalam sistem <strong>VIKAR Pro</strong>, Fibonacci <strong>tidak pernah digunakan sendirian</strong>, melainkan digabungkan dalam sistem <strong>4-Layer Confluence</strong>.
    </p>

    <div class="box-fibo">
      <strong>Konsep Inti Smart Money: Discount vs Premium</strong><br>
      • <strong>Pasar Bullish (BUY):</strong> Jangan membeli di pucuk! Tunggu harga diskon di bawah level 50% (Equilibrium), idealnya di <strong>Golden Pocket (0.50 – 0.618 – 0.786 / OTE)</strong>.<br>
      • <strong>Pasar Bearish (SELL):</strong> Jangan menjual di dasar lembah! Tunggu harga naik sementara ke area premium di atas 50%, idealnya di <strong>Golden Pocket (0.50 – 0.618 – 0.786)</strong>.
    </div>

    <h2>Tabel Konfigurasi Level Fibonacci Pro di TradingView</h2>
    <table style="font-size: 7.8pt; margin-bottom: 6px;">
      <thead>
        <tr>
          <th style="width: 12%;">Level Fibo</th>
          <th style="width: 18%;">Zona Pasar</th>
          <th style="width: 45%;">Makna & Reaksi Institusional</th>
          <th style="width: 25%;">Tindakan Trader VIKAR</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>0.000 (0%)</strong></td>
          <td>Swing Target</td>
          <td>Puncak atau Lembah baru yang baru saja terbentuk (titik penembusan BOS).</td>
          <td>Target Take Profit 1 (TP 1)</td>
        </tr>
        <tr>
          <td><strong>0.236 & 0.382</strong></td>
          <td>Shallow Retrace</td>
          <td>Koreksi dangkal saat tren sangat agresif. Rawan jebakan fakeout bagi ritel.</td>
          <td><strong>ABAIKAN</strong> (Diskon kurang murah)</td>
        </tr>
        <tr>
          <td><strong>0.500 (50%)</strong></td>
          <td>Equilibrium</td>
          <td>Batas adil (*Fair Value*). Harga berada di persimpangan kekuatan pembeli dan penjual.</td>
          <td>Siaga pantauan awal konfluensi</td>
        </tr>
        <tr>
          <td><strong>0.618 (61.8%)</strong></td>
          <td><span class="badge badge-fibo">Golden Ratio</span></td>
          <td>Rasio emas alam semesta. Tempat paling disukai algoritma institusi untuk entry posisi.</td>
          <td><strong>AREA ENTRY PRIMER</strong></td>
        </tr>
        <tr>
          <td><strong>0.786 (78.6%)</strong></td>
          <td><span class="badge badge-gold">OTE Pocket</span></td>
          <td><em>Optimal Trade Entry (OTE)</em>. Diskon terdalam dengan rasio R:R paling tinggi (SL sangat sempit).</td>
          <td><strong>AREA ENTRY MAKSIMAL</strong></td>
        </tr>
        <tr>
          <td><strong>1.000 (100%)</strong></td>
          <td>Invalidation Level</td>
          <td>Titik awal ayunan (*Origin Swing*). Jika level ini tertembus, maka tren resmi batal (*Invalid*).</td>
          <td>Batas Pelindung Stop Loss (SL)</td>
        </tr>
        <tr>
          <td><strong>-0.272 & -0.618</strong></td>
          <td>Extension Targets</td>
          <td>Proyeksi ekspansi harga ke wilayah harga baru setelah BOS berhasil dilanjutkan.</td>
          <td>Target TP 2 & TP 3 (Runner Profit)</td>
        </tr>
      </tbody>
    </table>

    <h2>3 Aturan Baku Penarikan Garis Fibonacci (The Golden Rules)</h2>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">1. Arah Kiri ke Kanan</div>
        <p style="font-size: 7.2pt; color: #334155; margin: 0;">
          Wajib ditarik dari titik masa lalu (sebelah kiri) menuju ke titik masa kini (sebelah kanan). Jangan pernah menarik mundur dari kanan ke kiri.
        </p>
      </div>
      <div class="card">
        <div class="card-title">2. Sumbu (Wick Tip)</div>
        <p style="font-size: 7.2pt; color: #334155; margin: 0;">
          Jangkar Fibo wajib ditaruh pada ujung sumbu terluar (<em>extreme wick</em>), bukan badan candle. Ekor lilin adalah batas likuiditas mutlak transaksi.
        </p>
      </div>
      <div class="card">
        <div class="card-title">3. Wajib Ada BOS</div>
        <p style="font-size: 7.2pt; color: #334155; margin: 0;">
          Dilarang menarik Fibo jika belum tercipta penembusan struktur BOS yang sah. Fibo hanya mengukur gelombang impuls yang sudah selesai.
        </p>
      </div>
    </div>
  </div>

  <!-- ==================== HALAMAN 7: TUTORIAL FIBONACCI BUY SETUP ==================== -->
  <div class="page">
    <h1>5.1. Tutorial Penarikan Fibonacci BUY Setup (Uptrend Confluence)</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_fibo_buy}" alt="Fibonacci BUY Confluence Chart">
      <div class="chart-caption">
        Gambar 5.1: Penarikan Fibonacci BUY dari Swing Low (1.000) ke Swing High (0.000). Harga retrace ke Golden Pocket (0.50–0.786) yang berhimpitan dengan Pivot Point & Ribbon EMA 8/21, memicu balon hijau "Buy".
      </div>
    </div>

    <h2>Langkah Demi Langkah (Step-by-Step Practical Tutorial):</h2>
    <div class="grid-2" style="margin-bottom: 6px;">
      <div class="card" style="border-left: 3px solid #10b981;">
        <div class="card-title" style="color: #047857; font-size: 8.5pt;">LANGKAH 1–3: PENARIKAN JANGKAR</div>
        <ol style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Validasi Tren Naik:</strong> Pastikan harga berada di atas <strong>EMA 125 Putih</strong> dan telah terjadi <strong>Bullish BOS</strong> (puncak lama tertembus).</li>
          <li><strong>Klik 1 (Titik Awal - Level 1.000):</strong> Pilih alat <em>Fib Retracement</em> di TradingView (Alt + F). Klik tepat di ujung ekor terbawah <strong>Swing Low (Lembah asal reli)</strong>.</li>
          <li><strong>Klik 2 (Titik Akhir - Level 0.000):</strong> Tarik garis ke kanan atas dan klik tepat di ujung ekor tertinggi <strong>Swing High (Puncak BOS)</strong>.</li>
        </ol>
      </div>

      <div class="card" style="border-left: 3px solid #0284c7;">
        <div class="card-title" style="color: #0369a1; font-size: 8.5pt;">LANGKAH 4–6: KONFLUENSI & EKSEKUSI</div>
        <ol style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Amati Golden Pocket:</strong> Tandai zona antara level <strong>0.500, 0.618, dan 0.786</strong>.</li>
          <li><strong>Cek Konfluensi 3 Lapis:</strong> Pastikan di zona tersebut terdapat: (a) Ribbon EMA 8–21, dan/atau (b) Garis horizontal Pivot Point (P / S1).</li>
          <li><strong>Trigger Eksekusi:</strong> Tunggu lilin Hammer / Engulfing <strong>Close resmi</strong> disertai balon hijau <strong>Buy</strong>. Buka posisi BUY saat bar close!</li>
        </ol>
      </div>
    </div>

    <h2>Protokol Target Stop Loss & Take Profit Fibonacci BUY:</h2>
    <table style="font-size: 7.5pt; margin-bottom: 4px;">
      <thead>
        <tr>
          <th>Target</th>
          <th>Level Fibonacci</th>
          <th>Lokasi Penempatan Harga</th>
          <th>Tindakan Manajemen Order</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Stop Loss (SL)</strong></td>
          <td>Di bawah 1.000 / 0.786</td>
          <td>Ujung Swing Low (Level 1.000) <strong>dikurangi 1.2x ATR buffer</strong>.</td>
          <td>Wajib dipasang saat klik open order. Jangan pernah digeser mundur!</td>
        </tr>
        <tr>
          <td><strong>Breakeven (BEP)</strong></td>
          <td>Rasio 1:1 R:R</td>
          <td>Saat harga floating profit sama dengan jarak Stop Loss.</td>
          <td>Pindahkan SL ke harga Entry. Trade berubah menjadi <strong>100% Bebas Risiko</strong>.</td>
        </tr>
        <tr>
          <td><strong>Take Profit 1 (TP 1)</strong></td>
          <td>Level 0.000 (0%)</td>
          <td>Puncak Swing High sebelumnya (titik resistance awal).</td>
          <td>Close 50% ukuran lot (Partial Profit), kunci uang riil ke akun.</td>
        </tr>
        <tr>
          <td><strong>Take Profit 2 (TP 2)</strong></td>
          <td>Level -0.272 Extension</td>
          <td>Zona ekstensi harga pertama di wilayah harga tertinggi baru.</td>
          <td>Close 25% sisa lot (Amankan profit lanjutan).</td>
        </tr>
        <tr>
          <td><strong>Take Profit 3 (TP 3)</strong></td>
          <td>Level -0.618 Extension</td>
          <td>Zona ekstensi harga maksimal institusional.</td>
          <td>Close 100% sisa posisi (*Runner Target Full Exit*).</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ==================== HALAMAN 8: TUTORIAL FIBONACCI SELL SETUP ==================== -->
  <div class="page">
    <h1>5.2. Tutorial Penarikan Fibonacci SELL Setup & 5 Kesalahan Fatal</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_fibo_sell}" alt="Fibonacci SELL Confluence Chart">
      <div class="chart-caption">
        Gambar 5.2: Penarikan Fibonacci SELL dari Swing High (1.000) ke Swing Low (0.000). Harga retrace naik ke Golden Pocket (0.50–0.786) yang membentur Resisten Pivot R1 & Ribbon EMA 8/21, memicu balon merah "Sell".
      </div>
    </div>

    <h2>Langkah Demi Langkah (Step-by-Step Practical Tutorial):</h2>
    <div class="grid-2" style="margin-bottom: 6px;">
      <div class="card" style="border-left: 3px solid #f43f5e;">
        <div class="card-title" style="color: #b91c1c; font-size: 8.5pt;">LANGKAH 1–3: PENARIKAN JANGKAR SELL</div>
        <ol style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Validasi Tren Turun:</strong> Harga wajib di bawah <strong>EMA 125 Putih</strong> dan terkonfirmasi <strong>Bearish BOS</strong> (lembah lama ditembus ke bawah).</li>
          <li><strong>Klik 1 (Titik Awal - Level 1.000):</strong> Klik alat Fibonacci di TradingView tepat di ujung ekor teratas <strong>Swing High (Puncak asal penurunan)</strong>.</li>
          <li><strong>Klik 2 (Titik Akhir - Level 0.000):</strong> Tarik garis ke kanan bawah dan klik di ujung ekor terbawah <strong>Swing Low (Lembah dasar BOS)</strong>.</li>
        </ol>
      </div>

      <div class="card" style="border-left: 3px solid #b45309;">
        <div class="card-title" style="color: #b45309; font-size: 8.5pt;">LANGKAH 4–6: PREMIUM ZONA & EKSEKUSI</div>
        <ol style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Tunggu Rebound ke Premium:</strong> Biarkan harga merayap naik sementara masuk ke Golden Pocket (<strong>0.500 s/d 0.786</strong>).</li>
          <li><strong>Konfluensi Resisten:</strong> Golden Pocket wajib bertumpuk dengan: (a) Ribbon EMA 8–21 yang menukik, dan/atau (b) Resisten Pivot (P / R1).</li>
          <li><strong>Trigger Eksekusi:</strong> Begitu candle Shooting Star / Bearish Engulfing <strong>Close resmi</strong> dengan balon merah <strong>Sell</strong>, buka order SELL!</li>
        </ol>
      </div>
    </div>

    <h2>5 Kesalahan Fatal Trader Retail Saat Menarik Fibonacci:</h2>
    <table style="font-size: 7.5pt; margin-bottom: 4px;">
      <thead>
        <tr>
          <th style="width: 25%;">Kesalahan Fatal Retail</th>
          <th style="width: 45%;">Dampak Buruk yang Terjadi</th>
          <th style="width: 30%;">Solusi Benar Trader VIKAR</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Penarikan Terbalik</strong></td>
          <td>Level 0 dan 1 terbalik sehingga level diskon dan target profit berantakan.</td>
          <td>Hafalkan: <strong>Klik 1 selalu Level 1.000 (Asal)</strong>, Klik 2 selalu Level 0.000 (Ujung).</td>
        </tr>
        <tr>
          <td><strong>2. Menarik di Pasar Sideways</strong></td>
          <td>Menarik Fibo saat tidak ada BOS, menghasilkan garis semu tanpa kekuatan pembalikan.</td>
          <td>Wajib tunggu penembusan struktur BOS yang sah sebelum membuka alat Fibo.</td>
        </tr>
        <tr>
          <td><strong>3. FOMO Masuk di 0.236 / 0.382</strong></td>
          <td>Membeli terlalu dini saat harga belum diskon, lalu tersapu turun ke 0.618.</td>
          <td>Sabar! Hanya entry jika harga minimal menyentuh level <strong>0.500 atau 0.618</strong>.</td>
        </tr>
        <tr>
          <td><strong>4. Memotong Ekor Lilin (Wick)</strong></td>
          <td>Menarik jangkar hanya sampai badan candle, mengabaikan jejak likuiditas ekor.</td>
          <td>Jangkar wajib menempel persis pada titik tertinggi/terendah <strong>ujung sumbu</strong>.</td>
        </tr>
        <tr>
          <td><strong>5. Entry Tanpa Konfluensi</strong></td>
          <td>Hanya mengandalkan garis Fibo tanpa konfirmasi Ribbon EMA & Pivot Point.</td>
          <td>Fibo wajib bertumpuk minimal dengan <strong>Ribbon EMA atau Pivot Level</strong>.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ==================== HALAMAN 9: SINERGI TRIPLE EMA & PIVOT POINTS ==================== -->
  <div class="page">
    <h1>6. Sinergi & Mekanisme Interaksi Triple EMA dengan Pivot Points</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_synergy}" alt="Synergy Triple EMA and Pivots Chart">
      <div class="chart-caption">
        Gambar 6.1: Sinergi Double Alignment (Harga di atas EMA 125 & di atas Pivot Biru) berpadu dengan pantulan Ribbon EMA 8/21 tepat di garis Pivot, memicu sinyal BUY bot meluncur menuju Tertinggi Resistance.
      </div>
    </div>

    <div class="grid-2" style="margin-bottom: 6px;">
      <!-- CARD 1: DOUBLE ALIGNMENT -->
      <div class="card" style="border-top: 3px solid #0284c7;">
        <div class="card-title" style="color: #0369a1; font-size: 8.5pt;">A. DOUBLE ALIGNMENT (SINKRONISASI MAKRO)</div>
        <ul style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Super Bullish (Grade A+ BUY):</strong> Harga di atas <strong>EMA 125</strong> (Tren Makro Naik) <em>DAN</em> harga di atas <strong>Central Pivot Biru</strong> (Sentimen Harian Bullish). Sinyal BUY memiliki probabilitas tertinggi!</li>
          <li><strong>Super Bearish (Grade A+ SELL):</strong> Harga di bawah <strong>EMA 125</strong> <em>DAN</em> di bawah <strong>Central Pivot Biru</strong>. Sinyal SELL meluncur agresif.</li>
          <li><strong>Sentiment Clash (Hati-Hati):</strong> Harga di atas EMA 125 tapi di bawah Pivot Biru. <em>Tindakan:</em> Tunggu harga breakout menembus Pivot Biru sebelum entry.</li>
        </ul>
      </div>

      <!-- CARD 2: 3 LEVEL KUNCI -->
      <div class="card" style="border-top: 3px solid #eab308;">
        <div class="card-title" style="color: #854d0e; font-size: 8.5pt;">B. CARA TRADING 3 LEVEL KUNCI RANGE</div>
        <ul style="font-size: 7.5pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Hari Sideways (Pantulan):</strong> Harga mantul di <em>Terendah Support</em> $\rightarrow$ Target ke <em>Pivot Biru</em> / <em>Tertinggi Resistance</em>. Begitu juga penolakan di <em>Tertinggi</em> menuju Pivot.</li>
          <li><strong>Hari Trending (SnR Flip):</strong> Jika <em>Tertinggi Resistance</em> ditembus lilin Marubozu hijau besar: <strong>DILARANG SELL!</strong> Tunggu retest ke garis Tertinggi (menjadi Support baru) berpadu Ribbon EMA untuk BUY lanjut.</li>
          <li><strong>Confluence Crossover:</strong> Ribbon EMA memotong Pivot = Magnet Rebound kuat.</li>
        </ul>
      </div>
    </div>

    <h2>Protokol Dynamic Trailing Stop Berbasis EMA 21 (Let Your Winners Run):</h2>
    <table style="font-size: 7.5pt; margin-bottom: 4px;">
      <thead>
        <tr>
          <th style="width: 25%;">Kondisi Posisi</th>
          <th style="width: 45%;">Aturan Tindakan Berdasarkan EMA 21</th>
          <th style="width: 30%;">Tujuan & Keuntungan</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Posisi BUY Sedang Running</strong></td>
          <td>Selama belum ada candle yang <strong>Bar Close resmi di bawah EMA 21 Magenta</strong>, tahan posisi (*Hold*). Geser SL bertahap di bawah lembah swing yang terbentuk.</td>
          <td>Mencegah keluar terlalu cepat, menangkap tren reli panjang hingga puluhan pips.</td>
        </tr>
        <tr>
          <td><strong>Posisi SELL Sedang Running</strong></td>
          <td>Selama belum ada candle yang <strong>Bar Close resmi di atas EMA 21 Magenta</strong>, biarkan posisi meluncur ke bawah (*Hold*). Geser SL bertahap di atas puncak swing.</td>
          <td>Mengunci profit maksimal saat pasar mengalami tren terjun bebas (*sell-off*).</td>
        </tr>
        <tr>
          <td><strong>Candle Close Menembus EMA 21</strong></td>
          <td>Jika satu candle utuh ditutup menembus balik garis EMA 21, segera <strong>Close All</strong> sisa posisi.</td>
          <td>Mengamankan keuntungan sebelum pasar berbalik arah atau konsolidasi melelahkan.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ==================== HALAMAN 10: 7 ZONA BAHAYA NO-TRADE ==================== -->
  <div class="page">
    <h1>7. 7 Zona Bahaya yang WAJIB DIHINDARI (No-Trade Protocol)</h1>

    <p style="margin-bottom: 6px;">
      Dalam trading profesional, <strong>modal dilindungi oleh apa yang Anda tolak, bukan apa yang Anda ambil</strong>. Lebih dari 80% kehancuran akun retail disebabkan oleh memaksakan transaksi pada 7 kondisi pasar terlarang berikut:
    </p>

    <table style="font-size: 7.5pt; margin-bottom: 6px;">
      <thead>
        <tr>
          <th style="width: 23%;">Zona Bahaya Terlarang</th>
          <th style="width: 45%;">Ciri Visual Pada Grafik Chart</th>
          <th style="width: 32%;">Risiko Fatal Jika Memaksakan Entry</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>1. Pasar Sideways / Datar (Chop)</strong></td>
          <td>Garis EMA 8, 21, dan 125 saling berbelit mendatar seperti benang kusut. Lilin kerdil tanpa arah.</td>
          <td><strong>Terkena Whipsaw:</strong> Sinyal BUY dan SELL bergantian memicu Stop Loss karena harga tanpa arah.</td>
        </tr>
        <tr>
          <td><strong>2. Pasar Overextended (> 2.5x ATR)</strong></td>
          <td>Harga sudah melonjak sangat tinggi atau anjlok drastis meninggalkan baseline EMA 125.</td>
          <td><strong>Mean Reversion Trap:</strong> Terjebak membeli di pucuk tertinggi atau menjual di lembah jurang.</td>
        </tr>
        <tr>
          <td><strong>3. Menjelang Berita High-Impact</strong></td>
          <td>30 menit sebelum dan sesudah rilis data ekonomi krusial (CPI, NFP, Suku Bunga Fed/FOMC, GDP AS).</td>
          <td><strong>Slippage Liar:</strong> Lonjakan harga puluhan pips dalam hitungan detik dapat melompati Stop Loss.</td>
        </tr>
        <tr>
          <td><strong>4. Sesi Rollover Bank (04:00–06:00 WIB)</strong></td>
          <td>Pergantian hari di server broker perbankan. Likuiditas global drop mendekati nol.</td>
          <td><strong>Spread Blowout:</strong> Spread Gold bisa melonjak hingga $2–$5, menyapu Stop Loss akun Anda.</td>
        </tr>
        <tr>
          <td><strong>5. Menabrak Dinding Pivot (Headroom)</strong></td>
          <td>Sinyal BUY muncul persis di bawah Pivot Resisten R1/R2 (< 0.8x ATR), atau SELL di atas Support S1.</td>
          <td><strong>Benturan Likuiditas:</strong> Pergerakan terhenti dan memantul balik karena menabrak order limit institusi.</td>
        </tr>
        <tr>
          <td><strong>6. Sinyal Intra-Bar (Belum Close)</strong></td>
          <td>Membuka posisi terburu-buru saat lilin masih berjalan (timer candle belum 00:00).</td>
          <td><strong>False Repaint Trap:</strong> Lilin Hammer bisa berbalik menjadi candle merah di detik terakhir bar.</td>
        </tr>
        <tr>
          <td><strong>7. Melawan Arus Tren HTF (H1/H4)</strong></td>
          <td>Mengeksekusi BUY di M5/M15 padahal tren timeframe H1 atau H4 sedang terjun bebas.</td>
          <td><strong>Terlindas Arus Besar:</strong> Pullback minor M5 langsung dilibas oleh penjualan institusi H1/H4.</td>
        </tr>
      </tbody>
    </table>

    <div class="box-warning" style="margin: 4px 0; padding: 5px 10px; font-size: 7.5pt;">
      <strong>Protokol Disiplin Tanpa Toleransi:</strong> Jika Anda mendeteksi salah satu dari 7 kondisi di atas, <strong>dilarang keras membuka posisi</strong>, betapapun menariknya bentuk candle saat itu. Simpan peluru Anda hanya untuk setup A+!
    </div>

    <h2 style="margin: 6px 0 4px 0;">Matriks Evaluasi Cepat: "Bolehkah Saya Entry Sekarang?"</h2>
    <div class="grid-3">
      <div class="card" style="text-align: center; border-top: 3px solid #10b981; padding: 6px;">
        <div class="card-title" style="color: #047857; font-size: 8pt;">LAMPU HIJAU (GO)</div>
        <p style="font-size: 7pt; color: #334155; margin: 2px 0;">
          Tren miring, BOS valid, retrace ke Golden Pocket & Ribbon EMA, bar close resmi, jam aktif London/NY.
        </p>
        <span class="badge badge-buy">Eksekusi Penuh</span>
      </div>
      <div class="card" style="text-align: center; border-top: 3px solid #f59e0b; padding: 6px;">
        <div class="card-title" style="color: #b45309; font-size: 8pt;">LAMPU KUNING (WAIT)</div>
        <p style="font-size: 7pt; color: #334155; margin: 2px 0;">
          Sinyal muncul di sesi Asia atau dekat Pivot (< 1.2x ATR). Kurangi ukuran lot menjadi 50% atau tunggu konfirmasi.
        </p>
        <span class="badge badge-gold">Hati-Hati</span>
      </div>
      <div class="card" style="text-align: center; border-top: 3px solid #f43f5e; padding: 6px;">
        <div class="card-title" style="color: #b91c1c; font-size: 8pt;">LAMPU MERAH (STOP)</div>
        <p style="font-size: 7pt; color: #334155; margin: 2px 0;">
          Ada berita High Impact < 30 mnt, EMA kusut datar, overextended > 2.5x ATR, atau jam rollover 04:00–06:00 WIB.
        </p>
        <span class="badge badge-sell">Dilarang Masuk</span>
      </div>
    </div>
  </div>

  <!-- ==================== HALAMAN 11: SETUP 1 & 2 ==================== -->
  <div class="page">
    <h1>8. Katalog Setup Unggulan (Bagian 1: Trend Following)</h1>

    <!-- SETUP 1 -->
    <div class="card" style="margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span class="card-title" style="color: #047857; font-size: 10pt;">Setup 1: BUY Continuation (BOS + Pullback Rejection Hammer)</span>
        <span class="badge badge-buy">Trend Following</span>
      </div>
      <div class="chart-img-container">
        <img src="{img_buy}" alt="Setup 1 BUY Continuation">
        <div class="chart-caption">Visual Chart Setup 1: Struktur BOS terkonfirmasi, disusul retrace ke Ribbon EMA & Pivot P dengan penolakan Hammer.</div>
      </div>
      <p style="font-size: 8pt; margin: 4px 0 0 0;">
        <strong>Karakteristik:</strong> Setup paling aman dengan persentase kemenangan (<em>win rate</em>) tertinggi. Terjadi saat pasar sedang reli kuat. Trader menunggu kembalinya harga ke area diskon sebelum melanjutkan kenaikan.
      </p>
    </div>

    <!-- SETUP 2 -->
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span class="card-title" style="color: #b91c1c; font-size: 10pt;">Setup 2: SELL Continuation (BOS + Shooting Star di Pivot R1)</span>
        <span class="badge badge-sell">Trend Following</span>
      </div>
      <div class="chart-img-container">
        <img src="{img_sell}" alt="Setup 2 SELL Continuation">
        <div class="chart-caption">Visual Chart Setup 2: Struktur BOS breakdown terkonfirmasi, pullback ke Ribbon EMA membentur resisten Pivot R1.</div>
      </div>
      <p style="font-size: 8pt; margin: 4px 0 0 0;">
        <strong>Karakteristik:</strong> Penurunan tajam diikuti kenaikan santai untuk menjebak retail. Begitu candle penolakan ekor atas membentur resisten Pivot R1 dan pita EMA, entri SELL dibuka dengan target S1/S2.
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN 12: SETUP 3 & 4 ==================== -->
  <div class="page">
    <h1>8. Katalog Setup Unggulan (Bagian 2: Reversal)</h1>

    <!-- SETUP 3 -->
    <div class="card" style="margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span class="card-title" style="color: #047857; font-size: 10pt;">Setup 3: BUY Reversal (CHoCH + Support S1 + Bullish Engulfing)</span>
        <span class="badge badge-choch">Bottom Reversal</span>
      </div>
      <div class="chart-img-container">
        <img src="{img_buy_choch}" alt="Setup 3 BUY Reversal">
        <div class="chart-caption">Visual Chart Setup 3: Pembalikan arah dasar lembah dengan konfirmasi CHoCH dan Bullish Engulfing di lantai Support S1.</div>
      </div>
      <p style="font-size: 8pt; margin: 4px 0 0 0;">
        <strong>Karakteristik:</strong> Terjadi setelah penurunan panjang mencapai titik jenuh jual (<em>oversold</em>). Terobosan struktur CHoCH membuktikan pembeli besar masuk, memberikan rasio R:R hingga 1:2.5 ke atas.
      </p>
    </div>

    <!-- SETUP 4 -->
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span class="card-title" style="color: #b91c1c; font-size: 10pt;">Setup 4: SELL Reversal (CHoCH + Resisten R2 + Bearish Engulfing)</span>
        <span class="badge badge-choch">Top Reversal</span>
      </div>
      <div class="chart-img-container">
        <img src="{img_sell_choch}" alt="Setup 4 SELL Reversal">
        <div class="chart-caption">Visual Chart Setup 4: Pembalikan arah di pucuk harga dengan CHoCH dan Bearish Engulfing pada atap resisten Pivot R2.</div>
      </div>
      <p style="font-size: 8pt; margin: 4px 0 0 0;">
        <strong>Karakteristik:</strong> Kegagalan menembus Pivot R2 yang disusul penembusan swing low memicu sinyal pembalikan arah (<em>trend reversal</em>). Sangat menguntungkan untuk swing intraday.
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN 13: SETUP 5 & SESI TRADING ==================== -->
  <div class="page">
    <h1>8. Katalog Setup Unggulan (Bagian 3: Scalping)</h1>

    <!-- SETUP 5 -->
    <div class="card" style="margin-bottom: 12px;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
        <span class="card-title" style="color: #0369a1; font-size: 10pt;">Setup 5: M5 Scalping Double Confluence (Double Pin Bar di Pivot P)</span>
        <span class="badge badge-gold">XAUUSD Scalping</span>
      </div>
      <div class="chart-img-container">
        <img src="{img_scalp}" alt="Setup 5 Scalping Confluence">
        <div class="chart-caption">Visual Chart Setup 5: Scalping cepat di M5 dengan formasi Double Pin Bar rejection di atas garis Daily Pivot dan Ribbon EMA.</div>
      </div>
      <p style="font-size: 8pt; margin: 4px 0 0 0;">
        <strong>Karakteristik:</strong> Setup scalping favorit para trader emas. Dua jarum ekor bawah menguji lantai yang sama membuktikan bahwa level tersebut dijaga ketat oleh pembeli institusional.
      </p>
    </div>

    <h2>Panduan Waktu & Sesi Trading (WIB)</h2>
    <table style="font-size: 7.8pt;">
      <thead>
        <tr>
          <th>Sesi Pasar</th>
          <th>Jam Trading (WIB)</th>
          <th>Karakteristik Pergerakan</th>
          <th>Rekomendasi Tindakan</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>Sesi Asia (Tokyo)</strong></td>
          <td>07:00 – 14:00</td>
          <td>Volatilitas rendah hingga sedang. Pergerakan cenderung tertib di dalam range.</td>
          <td>Cocok untuk scalping M5 di sekitar level Pivot P dan S1/R1.</td>
        </tr>
        <tr>
          <td><strong>Sesi London (Eropa)</strong></td>
          <td>14:00 – 20:00</td>
          <td>Volatilitas tinggi, sering terjadi <em>London Breakout</em> dan penentuan tren harian.</td>
          <td><strong>Sesi Emas:</strong> Fokus pada Setup 1 dan Setup 2 (Trend Following).</td>
        </tr>
        <tr>
          <td><strong>Sesi New York (Overlap)</strong></td>
          <td>19:00 – 23:00</td>
          <td>Volume dan volatilitas puncak. Likuiditas terbesar dunia pada instrumen Gold.</td>
          <td><strong>Sesi Terbaik:</strong> Ambil sinyal rejection murni, waspadai rilis berita jam 19:30/21:00 WIB.</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- ==================== HALAMAN 14: STUDI KASUS PASAR NYATA (BAGIAN 1) ==================== -->
  <div class="page">
    <h1>9. Studi Kasus Pasar Nyata (Bagian 1: Akumulasi Fibo & Entry Buy)</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_real1}" alt="Real Market Case Study XAUUSD M5 Part 1">
      <div class="chart-caption">
        Gambar 9.1: Grafik Real-Market Akun Riil XAU/USD (Gold) M5 (17 September 2026, 13:41 WIB). Sinyal BUY Grade A+ jam 12:30 WIB memantul di Area Fibo 618-786 & Pivot Biru 4.288,57, melesat +210 pips menuju atap resisten 4.315,42.
      </div>
    </div>

    <div class="grid-2" style="margin-bottom: 6px;">
      <!-- CARD 1: BEDAH SINYAL BUY A+ -->
      <div class="card" style="border-left: 3px solid #10b981;">
        <div class="card-title" style="color: #047857; font-size: 8.5pt;">A. BEDAH MONSTER BUY TRADE (JAM 12:30 WIB)</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Konfluensi Emas:</strong> Harga turun tepat ke <strong>AREA FIBO 618 - 786</strong> berhimpitan dengan garis <strong>Pivot Biru 4.288,57</strong>.</li>
          <li><strong>Liquidity Sweep (Stop Hunt):</strong> Ekor lilin menusuk menembus Swing Low LL di <strong>4.285,29</strong> menyapu SL retail, lalu memantul balik kilat (*V-Shape*).</li>
          <li><strong>Trigger Bullish Engulfing:</strong> Lilin hijau menelan lilin merah dan Bar Close resmi di atas EMA 125.</li>
          <li><strong>Eksekusi Akun Riil:</strong> Entry <strong>4.294,66</strong> | SL <strong>4.285,13</strong> | TP(1:2) <strong>4.313,72</strong>. <strong>HIT TP SEMPURNA!</strong> Reli +210 pips hingga atap 4.315.</li>
        </ul>
      </div>

      <!-- CARD 2: FILTER NOISE SIDEWAYS -->
      <div class="card" style="border-left: 3px solid #f43f5e;">
        <div class="card-title" style="color: #b91c1c; font-size: 8.5pt;">B. MENGAPA SINYAL JAM 11:30–12:20 WAJIB DIABAIKAN?</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Fase Konsolidasi Sempit (Chop):</strong> Harga terjepit mendatar di antara garis EMA 125 Putih dan Pivot Biru.</li>
          <li><strong>Tidak Ada BOS Baru:</strong> Ayunan belum mampu menembus struktur puncak atau lembah secara tegas.</li>
          <li><strong>SOP 7 Zona Bahaya:</strong> Sesuai Zona Bahaya 1 di Halaman 10, pasar sideways adalah area terlarang! Menunggu konfirmasi BOS jam 12:30 menyelamatkan modal dari <em>whipsaw</em>.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="border-top: 3px solid #0284c7; padding: 5px 10px;">
      <div class="card-title" style="color: #0369a1; font-size: 8.5pt;">C. KONDISI AWAL JAM 13:41 WIB (HARGA 4.307,40)</div>
      <p style="font-size: 7.2pt; color: #1e293b; margin: 2px 0;">
        Harga sempat tertolak di resisten 4.315,42. SOP melarang BUY di pucuk dan menginstruksikan trader menunggu koreksi sehat ke Ribbon EMA 21 (4.303–4.306) untuk bersiap mengambil entri kelanjutan tren.
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN 15: STUDI KASUS PASAR NYATA (BAGIAN 2) ==================== -->
  <div class="page">
    <h1>9.1. Studi Kasus Lanjutan: Breakout BOS & Reli Monster +430 Pips</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_real2}" alt="Real Market Case Study XAUUSD M5 Part 2 BOS Breakout">
      <div class="chart-caption">
        Gambar 9.2: Grafik Real-Market XAU/USD M5 (17 September 2026, 14:56 WIB). Terlihat Mode Clean Chart aktif tanpa tanda visual, HUD menampilkan 'SUPER BULLISH (Grade A+)', terjadi penembusan 'BULLISH BOS' di 4.315,40 dan harga meledak hingga 4.337+ (+430 pips dari entri 4.294).
      </div>
    </div>

    <div class="grid-2" style="margin-bottom: 6px;">
      <!-- CARD 1: CLEAN CHART & DOUBLE ALIGNMENT -->
      <div class="card" style="border-left: 3px solid #0284c7;">
        <div class="card-title" style="color: #0369a1; font-size: 8.5pt;">A. CLEAN CHART & DOUBLE ALIGNMENT HUD</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Mode Grafik Bersih:</strong> Semua tanda visual BUY/SELL disembunyikan (*clean chart*), membebaskan grafik dari distraksi teks huruf.</li>
          <li><strong>Konfirmasi Double Alignment:</strong> Baris 1 Tabel HUD memvalidasi status <strong>SUPER BULLISH (Grade A+)</strong> warna Cyan (Harga berada jauh di atas EMA 125 Putih di 4.302 dan di atas Pivot Biru di 4.288).</li>
          <li><strong>Transisi Struktur:</strong> Struktur SMC resmi bertransformasi dari <em>CHoCH</em> menjadi <strong>BULLISH BOS</strong>!</li>
        </ul>
      </div>

      <!-- CARD 2: ANATOMI BREAKOUT BOS -->
      <div class="card" style="border-left: 3px solid #10b981;">
        <div class="card-title" style="color: #047857; font-size: 8.5pt;">B. ANATOMI BREAKOUT BOS DI 4.315,40</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Konfirmasi Jebol Resisten:</strong> Lilin jam 14:15 WIB berhasil Bar Close resmi menembus ke atas garis <code>Swing High [HH]: 4315.40</code>.</li>
          <li><strong>Label BOS Muncul:</strong> Indikator mencetak label biru <strong>BOS</strong>, menandakan likuiditas penjual telah habis dilahap oleh pembeli institusional.</li>
          <li><strong>Ekspansi Super Kencang:</strong> Terjadi ledakan lilin-lilin hijau berturut-turut (*Marubozu Expansion*) menembus 4.320, 4.324, hingga mencapai pucuk <strong>4.337,50</strong>!</li>
        </ul>
      </div>
    </div>

    <div class="card" style="border-top: 3px solid #eab308; padding: 5px 10px;">
      <div class="card-title" style="color: #854d0e; font-size: 8.5pt;">C. PELAJARAN EMAS: MENGAPA TRADER VIKAR MAMPU MENGANTONGI +430 PIPS?</div>
      <p style="font-size: 7.2pt; color: #1e293b; margin: 2px 0;">
        • <strong>Kunci Disiplin Trailing Stop EMA 21:</strong> Trader amatir keluar terlalu awal di 4.315 (+210 pips). Namun dengan aturan Bab 6: <em>Selama candle belum pernah Bar Close di bawah Ribbon EMA 21 Magenta</em>, posisi wajib ditahan (*Hold*)!<br>
        • <strong>Hasil Eksekusi Akhir:</strong> Posisi entri awal di 4.294,66 berhasil mendulang keuntungan maksimal hingga pucuk <strong>4.337,50 (+430 pips / +$43 per troy oz)</strong> sebelum harga melakukan retrace sehat ke 4.324,87 dengan target magnet berikutnya di <strong>R1 (4.341,70)</strong>!
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN 17: STUDI KASUS PASAR NYATA (BAGIAN 3) ==================== -->
  <div class="page">
    <h1>9.2. Studi Kasus Live: Validasi Ascending Channel, FVG & Order Block M15</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_real3}" alt="Live Case Study XAUUSD M15 Ascending Channel FVG OB" style="max-height: 200px;">
      <div class="chart-caption">
        Gambar 9.3: Grafik Analisis Live XAU/USD (Gold) M15 (17 September 2026, 16:58 WIB). Bedah struktur Ascending Parallel Channel, Fair Value Gap (4.300–4.304), dan Order Block M15 (4.288–4.294) yang bertumpuk sempurna di atas Daily Pivot Biru 4.288,57.
      </div>
    </div>

    <div class="grid-2" style="margin-bottom: 6px;">
      <!-- CARD 1: ANATOMI STRUKTUR & TRENDLINE LIQUIDITY TRAP -->
      <div class="card" style="border-left: 3px solid #0284c7;">
        <div class="card-title" style="color: #0369a1; font-size: 8.5pt;">A. ANATOMI STRUKTUR & TRENDLINE LIQUIDITY TRAP</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Ascending Parallel Channel:</strong> Pola channel naik ditarik presisi menghubungkan Higher Lows sesi Asia (~4.260–4.288) ke pucuk tertinggi 4.337,50. Saat ini harga sedang menguji garis bawah channel di 4.307.</li>
          <li><strong>Waspada Trendline Liquidity Trap:</strong> Trader retail pemula menganggap garis bawah channel sebagai area BUY instan. Dalam kaidah Smart Money Concepts (SMC), garis miring ini menyimpan tumpukan <em>Sell Stop Liquidity (SSL)</em> yang rentan disapu (*Stop Hunt*).</li>
          <li><strong>Rongga FVG (4.300–4.304):</strong> Terdapat <em>Fair Value Gap</em> (imbalance) akibat lompatan reli jam 13:00–14:00. FVG bertindak sebagai magnet harga untuk penyeimbangan likuiditas (*rebalancing*).</li>
        </ul>
      </div>

      <!-- CARD 2: SUPER CONFLUENCE OB M15 & PIVOT BIRU -->
      <div class="card" style="border-left: 3px solid #10b981;">
        <div class="card-title" style="color: #047857; font-size: 8.5pt;">B. SUPER CONFLUENCE: OB M15 & PIVOT BIRU 4.288,57</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Tumpukan Level Keramat:</strong> Kotak hijau <strong>Order Block M15 (4.288–4.294)</strong> bertumpuk persis di atas <strong>Daily Pivot Biru (4.288,57)</strong> dan area <strong>Fibonacci Golden Pocket (61.8%–78.6%)</strong>!</li>
          <li><strong>Pilar Double Alignment:</strong> Garis Pivot Biru adalah benteng pertahanan terakhir institusi. Di atas 4.288, struktur besar harian tetap berstatus <em>SUPER BULLISH</em>.</li>
          <li><strong>Benteng EMA 125:</strong> Garis putih EMA 125 di 4.302 memberikan bantalan dinamis pertama sebelum harga mencapai lantai Pivot.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="border-top: 3px solid #eab308; padding: 5px 10px;">
      <div class="card-title" style="color: #854d0e; font-size: 8.5pt;">C. RENCANA AKSI EKSEKUSI INSTITUSIONAL (SKENARIO A vs SKENARIO B)</div>
      <p style="font-size: 7.2pt; color: #1e293b; margin: 2px 0;">
        • <strong>Skenario A (Agresif - FVG Bounce 4.300–4.304):</strong> Jika candle M15 menyentuh FVG lalu mencetak rejection Pin Bar / Hammer dan <em>Bar Close di atas EMA 21 Magenta</em>. Entry: <strong>4.304,00–4.306,00</strong> | SL: <strong>4.296,00</strong> (di bawah FVG) | TP1: <strong>4.320,00</strong> | TP2: <strong>4.337,50</strong> (Pucuk High).<br>
        • <strong>Skenario B (Konservatif Grade A+ - Sweep Channel ke OB 4.288–4.294):</strong> Biarkan institusi menjebol garis channel ke bawah untuk memakan SL retail, lalu memantul tajam di zona OB M15 & Pivot Biru 4.288,57. Tunggu konfirmasi Bullish Engulfing Bar Close. Entry: <strong>4.291,00–4.294,50</strong> | SL: <strong>4.283,50</strong> (di balik Swing Low 4.285) | TP1: <strong>4.315,00</strong> | TP2: <strong>4.337,50</strong> | TP3: <strong>4.341,70 (Resisten R1)</strong>.
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN BARU: STUDI KASUS LIVE 9.3 ==================== -->
  <div class="page">
    <h1>9.3. Masterclass Real-Market: Bedah Anatomi V-Reversal, Liquidity Sweep, FVG & Order Block (17 September 2026, 23:39 WIB)</h1>

    <div class="chart-img-container" style="margin: 4px 0 6px 0;">
      <img src="{img_real4}" alt="Live Case Study XAUUSD V-Reversal Liquidity Sweep FVG OB" style="max-height: 202px;">
      <div class="chart-caption">
        Gambar 9.4: Grafik Analisis Real-Market XAU/USD (17 September 2026, 23:39 WIB - Harga: 4.360,14). Pemetaan visual komprehensif: <em>Sell-Side Liquidity (SSL) Sweep</em> di 4.264 (-120 pips ke 4.240), <em>Bullish Order Block Demand Base (4.240–4.260)</em>, <em>Bullish CHoCH (4.300)</em>, <em>Multi-Tier FVG (4.280–4.300 & 4.335–4.355)</em>, serta <em>Bullish BOS ke 4.383</em>.
      </div>
    </div>

    <div class="grid-2" style="margin-bottom: 6px;">
      <!-- CARD 1: SIKLUS TURTLE SOUP & REVERSAL OB -->
      <div class="card" style="border-left: 3px solid #ef4444;">
        <div class="card-title" style="color: #b91c1c; font-size: 8.5pt;">A. ANATOMI STOP HUNT & BASE DEMAND (4.240–4.260)</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>Sell-Side Liquidity (SSL) Sweep:</strong> Pada pagi 17 September, harga dibuang secara vertikal dari 4.370 menembus Swing Low 15 September (4.264) hingga ekor lilin menyentuh 4.240. Ini adalah manipulasi klasik institusi (*Turtle Soup*) untuk melikuidasi Stop Loss buyer retail.</li>
          <li><strong>Pembentukan Bullish Order Block (4.240–4.260):</strong> Kotak hijau di dasar lembah merupakan zona akumulasi volume raksasa institusi (*Smart Money Demand*). Begitu likuiditas terserap, harga berbalik arah secara instan (*V-Shape Reversal*).</li>
          <li><strong>Konfirmasi Bullish CHoCH (4.300):</strong> Kenaikan eksplosif langsung menembus swing high minor 4.300, mengubah karakter tren dari Bearish menjadi Bullish secara resmi.</li>
        </ul>
      </div>

      <!-- CARD 2: DUAL FAIR VALUE GAP & BOS EXPANSION -->
      <div class="card" style="border-left: 3px solid #f59e0b;">
        <div class="card-title" style="color: #b45309; font-size: 8.5pt;">B. MULTI-TIER FVG & BREAKOUT BOS EXPANSION</div>
        <ul style="font-size: 7.2pt; margin-left: 14px; margin-bottom: 0;">
          <li><strong>FVG 1 Imbalance (4.280–4.300):</strong> Lompatan harga meninggalkan ketidakseimbangan order. Koreksi ke 4.288 mengisi kembali (*mitigasi FVG 1*) sebelum memicu ekspansi kedua.</li>
          <li><strong>Bullish BOS (4.370) & New High (4.383):</strong> Gelombang reli kedua menembus puncak resisten 4.370 dengan <em>body candle close</em> yang solid (*Break of Structure*), mencetak puncak tertinggi baru di 4.383.</li>
          <li><strong>FVG 2 & Secondary OB (4.335–4.355):</strong> Reli kedua melahirkan zona ketidakseimbangan baru (kotak cyan). Area ini bertumpuk dengan rasio emas Fibonacci <strong>Golden Pocket (0.500–0.618)</strong> dari ayunan 4.288 ke 4.383.</li>
        </ul>
      </div>
    </div>

    <div class="card" style="border-top: 3px solid #10b981; padding: 5px 10px;">
      <div class="card-title" style="color: #047857; font-size: 8.5pt;">C. ANALISIS POSISI LIVE (4.360,14) & SOP EKSEKUSI RE-ENTRY GRADE A+</div>
      <p style="font-size: 7.2pt; color: #1e293b; margin: 2px 0;">
        • <strong>Status Pasar Saat Ini (4.360,14):</strong> Setelah mencetak rejeksi di pucuk 4.383 (*Bearish Supply Peak*), harga sedang melakukan *healthy pullback* (koreksi sehat) menuju Value Zone FVG 2 / Bullish OB di <strong>4.335–4.355</strong>.<br>
        • <strong>SOP Entry Buy Limit / Rebound:</strong> Pasang area pantauan di <strong>4.340,00–4.352,00</strong> (Area Golden Pocket Fibo 61.8% & FVG 2). Tunggu konfirmasi lilin rejection (Hammer / Bullish Engulfing pada M5/M15).<br>
        • <strong>Target Proteksi & Keuntungan:</strong> Stop Loss di <strong>4.328,00</strong> (di bawah lantai FVG 2) | TP1: <strong>4.368,00</strong> (+160 pips) | TP2: <strong>4.383,00</strong> (Re-test Peak High) | TP3: <strong>4.400,00</strong> (Target Ekstensi Fibo -0.272).
      </p>
    </div>
  </div>

  <!-- ==================== HALAMAN 18: RISK MANAGEMENT ==================== -->
  <div class="page">
    <h1>10. Manajemen Resiko Anti-Kena SL</h1>

    <div class="box-warning">
      <strong>Pelajaran Krusial Kasus Gold (XAUUSD):</strong><br>
      Menaruh Stop Loss sempit (0.3x ATR / 15 pips) di pasar Gold sama saja dengan bunuh diri finansial. Pergerakan wajar 1 candle M15 di Gold berkisar $3–$8 (30–80 pips). SL wajib dipasang di balik <strong>Structure Swing Fractal / Fibo 1.0</strong> dengan buffer minimal <strong>1.2x ATR</strong>!
    </div>

    <h2>Formula Ukuran Lot Sesuai Resiko Modal (1% - 2%)</h2>
    <p style="margin-bottom: 6px;">
      Jangan pernah menggunakan lot tebak-tebakan. Gunakan rumus baku matematika berikut:
    </p>

    <div class="box" style="text-align: center; font-size: 10pt; font-weight: bold; background: #f0fdf4; border-color: #22c55e; padding: 6px 10px;">
      Ukuran Lot = (Total Modal x % Resiko) ÷ (Jarak Stop Loss dalam Pips x Nilai Pip)
    </div>

    <h2>Tabel Panduan Lot Size Berdasarkan Modal (Maksimal Resiko 1.5%)</h2>
    <table style="font-size: 7.8pt;">
      <thead>
        <tr>
          <th>Saldo Modal ($)</th>
          <th>Batas Resiko ($)</th>
          <th>Jarak SL Rata-Rata Gold (Pips)</th>
          <th>Rekomendasi Lot Size</th>
          <th>Target Profit 1:2 R:R ($)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>$200 (Akun Pemula)</td>
          <td>$3.00 (1.5%)</td>
          <td>30 pips ($3.0)</td>
          <td><strong>0.01 Lot</strong></td>
          <td>+$6.00</td>
        </tr>
        <tr>
          <td>$500 (Mikro)</td>
          <td>$7.50 (1.5%)</td>
          <td>35 pips ($3.5)</td>
          <td><strong>0.02 Lot</strong></td>
          <td>+$15.00</td>
        </tr>
        <tr>
          <td>$1,000 (Standar)</td>
          <td>$15.00 (1.5%)</td>
          <td>35 pips ($3.5)</td>
          <td><strong>0.04 Lot</strong></td>
          <td>+$30.00</td>
        </tr>
        <tr>
          <td>$3,000 (Pertumbuhan)</td>
          <td>$45.00 (1.5%)</td>
          <td>40 pips ($4.0)</td>
          <td><strong>0.11 Lot</strong></td>
          <td>+$90.00</td>
        </tr>
        <tr>
          <td>$5,000 (Pro)</td>
          <td>$75.00 (1.5%)</td>
          <td>40 pips ($4.0)</td>
          <td><strong>0.18 Lot</strong></td>
          <td>+$150.00</td>
        </tr>
        <tr>
          <td>$10,000 (Institusi)</td>
          <td>$150.00 (1.5%)</td>
          <td>45 pips ($4.5)</td>
          <td><strong>0.33 Lot</strong></td>
          <td>+$300.00</td>
        </tr>
      </tbody>
    </table>

    <h2>Aturan Breakeven (BEP 1:1) - Mengunci Modal</h2>
    <ul style="font-size: 8pt;">
      <li>Ketika harga sudah bergerak profit sejauh <strong>1:1 Risk-to-Reward</strong> (jarak profit = jarak resiko awal), <strong>SEGERA pindahkan Stop Loss ke titik harga Entry</strong>.</li>
      <li>Dengan cara ini, trade Anda resmi berstatus <strong>100% Risk-Free (Trade Bebas Resiko)</strong>. Apapun yang terjadi berikutnya, akun Anda tidak akan rugi satu sen pun.</li>
      <li>Tutup 50% lot (<em>Partial Close</em>) di level Pivot atau target Fibo 0.000 untuk mengamankan uang riil ke kantong Anda.</li>
    </ul>
  </div>

  <!-- ==================== HALAMAN 17: NO-TRADE CHECKLIST ==================== -->
  <div class="page">
    <h1>11. Disiplin Psikologi & Checklist No-Trade</h1>

    <p style="margin-bottom: 6px;">
      Seorang trader profesional dihormati bukan karena berapa sering ia masuk pasar, melainkan karena kemampuannya <strong>menahan diri untuk tidak trading saat kondisi pasar tidak ideal</strong>.
    </p>

    <div class="box-warning" style="padding: 6px 10px; margin-bottom: 6px;">
      <h3 style="color: #9f1239; margin-top: 0; font-size: 8.5pt;">DILARANG MEMBUKA POSISI JIKA TERJADI KONDISI BERIKUT:</h3>
      <ol style="margin-left: 14px; font-size: 7.5pt;">
        <li><strong>EMA 125 Bergerak Datar / Kusut:</strong> Menandakan pasar sedang sideways/konsolidasi. Sinyal apapun akan menghasilkan <em>whipsaw</em> (kerugian bolak-balik).</li>
        <li><strong>30 Menit Menjelang Berita High-Impact (Red Folder News):</strong> Seperti CPI, Non-Farm Payroll (NFP), FOMC Statement, atau Suku Bunga Fed. Volatilitas liar pada rilis berita dapat melompati Stop Loss (<em>slippage</em>).</li>
        <li><strong>Harga Sudah Terlalu Jauh dari EMA 125 (> 2.5x ATR):</strong> Kondisi <em>overextended</em>. Menjual di dasar lembah atau membeli di pucuk tertinggi adalah perangkap likuiditas.</li>
        <li><strong>Rasio Risk to Reward Kurang dari 1:1.5:</strong> Jika di depan titik entri terdapat tembok Pivot yang terlalu dekat (< 0.8x ATR), batalkan trade tersebut.</li>
      </ol>
    </div>

    <h2>Lembar Checklist Sebelum Klik Buy / Sell (Print & Tempel di Meja)</h2>
    <table style="font-size: 7.5pt; margin-bottom: 8px;">
      <thead>
        <tr>
          <th style="width: 10%; text-align: center;">Centang</th>
          <th style="width: 38%;">Parameter Wajib</th>
          <th style="width: 52%;">Kondisi yang Harus Terpenuhi</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center;">[  ]</td>
          <td><strong>1. Double Alignment</strong></td>
          <td>Harga di atas EMA 125 & di atas Pivot Biru (untuk BUY) atau di bawah keduanya (untuk SELL).</td>
        </tr>
        <tr>
          <td style="text-align: center;">[  ]</td>
          <td><strong>2. Struktur Pasar SMC</strong></td>
          <td>Tercatat BOS atau CHoCH yang searah. Sinyal bukan diambil saat breakout pucuk/dasar.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[  ]</td>
          <td><strong>3. Retracement Fibonacci</strong></td>
          <td>Harga telah masuk ke Golden Pocket (0.500 s/d 0.786) dan bersentuhan dengan Ribbon EMA.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[  ]</td>
          <td><strong>4. Konfirmasi Bar Close</strong></td>
          <td>Candle rejection telah menutup resmi pada timer bar (bukan sinyal berjalan / repaint).</td>
        </tr>
        <tr>
          <td style="text-align: center;">[  ]</td>
          <td><strong>5. Ukuran Resiko Terukur</strong></td>
          <td>Resiko maksimal 1%–1.5% modal. SL dipasang di balik swing structure / Fibo 1.000 + buffer.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[  ]</td>
          <td><strong>6. Jadwal Berita Aman</strong></td>
          <td>Tidak ada rilis berita ekonomi berdampak tinggi (CPI/NFP/FOMC) dalam 30 menit ke depan.</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 20px; text-align: center; border-top: 2px dashed #cbd5e1; padding-top: 15px;">
      <p style="font-size: 10pt; font-weight: bold; color: #0f172a; margin: 0;">
        "Kunci sukses bukanlah keserakahan mengejar pips, melainkan disiplin mematuhi rencana."
      </p>
      <p style="font-size: 8pt; color: #64748b; margin-top: 3px;">
        VIKAR STRATEGY PRO — TRADING PLAN, SINERGI, FIBONACCI & REAL-MARKET SOP RESMI
      </p>
    </div>
  </div>

</body>
</html>
"""

html_path = os.path.join(os.path.dirname(__file__), "trading_plan_temp.html")
pdf_path = os.path.join(os.path.dirname(__file__), "TRADING_PLAN_VIKAR_PRO.pdf")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML generated at: {html_path}")

edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(edge_path):
    edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

cmd = [
    edge_path,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]

print("Converting HTML to PDF via Edge Headless...")
res = subprocess.run(cmd, capture_output=True, text=True)

if os.path.exists(pdf_path):
    print(f"SUCCESS: PDF created at: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path)} bytes")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    page_matches = re.findall(b"/Type\\s*/Page[^s]", pdf_bytes)
    print(f"Total Pages in Generated PDF: {len(page_matches)}")
    if os.path.exists(html_path):
        os.remove(html_path)
else:
    print("FAILED to create PDF.")
    print("Return code:", res.returncode)
    print("Stdout:", res.stdout)
    print("Stderr:", res.stderr)
