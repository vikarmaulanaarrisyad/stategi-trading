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

html_content = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>PANDUAN LENGKAP ROBOT TRADING MT5 - VIKAR EA 4-PILLAR PRO</title>
<style>
  @page {
    size: A4;
    margin: 10mm 12mm 12mm 12mm;
    @bottom-right {
      content: "Halaman " counter(page);
      font-size: 8pt;
      font-weight: 700;
      color: #0284c7;
    }
    @bottom-left {
      content: "VIKAR EA 4-PILLAR PRO v3.00 | BUKU PANDUAN TRADING INSTITUSIONAL PEMULA & PRO";
      font-size: 7.5pt;
      color: #64748b;
      font-weight: 600;
    }
  }

  * {
    box-sizing: border-box;
  }

  body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.38;
    font-size: 8.5pt;
    margin: 0;
    padding: 0;
  }

  .page {
    page-break-after: always;
    break-after: page;
    height: 980px;
    max-height: 980px;
    overflow: hidden;
    position: relative;
    padding-bottom: 5px;
  }

  .page:last-child, .page:last-of-type {
    page-break-after: avoid;
    break-after: avoid;
  }

  /* Cover Styling */
  .cover {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 980px;
    background: linear-gradient(135deg, #090d16 0%, #0f172a 40%, #1e293b 75%, #0284c7 100%);
    color: #ffffff;
    border-radius: 12px;
    padding: 35px 30px;
    text-align: center;
  }

  .cover-top {
    text-align: center;
  }

  .cover-badge {
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
    margin-bottom: 18px;
  }

  .cover-title {
    font-size: 28pt;
    font-weight: 900;
    line-height: 1.15;
    margin: 0 0 10px 0;
    background: linear-gradient(to right, #38bdf8, #f43f5e, #ffffff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .cover-subtitle {
    font-size: 13pt;
    color: #94a3b8;
    font-weight: 500;
    margin: 0 0 25px 0;
  }

  .cover-pillars {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 25px;
  }

  .pillar-card {
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 8px;
    padding: 12px 10px;
    flex: 1;
    text-align: center;
  }

  .pillar-card h4 {
    margin: 0 0 4px 0;
    font-size: 9.5pt;
    color: #38bdf8;
    text-transform: uppercase;
  }

  .pillar-card p {
    margin: 0;
    font-size: 7.5pt;
    color: #cbd5e1;
    line-height: 1.3;
  }

  .cover-desc-box {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 8px;
    padding: 14px 18px;
    text-align: left;
    margin-bottom: 20px;
  }

  .cover-desc-box h4 {
    color: #38bdf8;
    margin: 0 0 6px 0;
    font-size: 9.5pt;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .cover-desc-box p {
    color: #cbd5e1;
    font-size: 8pt;
    margin: 0;
    line-height: 1.45;
    text-align: justify;
  }

  .cover-meta {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 12px 20px;
    display: flex;
    justify-content: space-around;
    font-size: 8pt;
    color: #cbd5e1;
    margin-bottom: 10px;
  }

  .meta-item strong {
    display: block;
    color: #38bdf8;
    font-size: 8.5pt;
    margin-bottom: 2px;
  }

  /* Chapter Header Band */
  .chapter-header {
    border-bottom: 2.5px solid #0284c7;
    padding-bottom: 5px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }

  .chapter-title {
    font-size: 13.5pt;
    font-weight: 800;
    color: #0f172a;
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .chapter-badge {
    background: linear-gradient(135deg, #0284c7, #0369a1);
    color: #ffffff;
    font-size: 7.5pt;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
  }

  h2 {
    font-size: 10.5pt;
    font-weight: 700;
    color: #0369a1;
    margin: 8px 0 5px 0;
    border-left: 3.5px solid #0284c7;
    padding-left: 7px;
  }

  h3 {
    font-size: 9pt;
    font-weight: 700;
    color: #1e293b;
    margin: 6px 0 4px 0;
  }

  p {
    margin: 0 0 6px 0;
    text-align: justify;
    line-height: 1.4;
  }

  /* Grids */
  .grid-2 {
    display: flex;
    gap: 10px;
    margin-bottom: 8px;
  }

  .grid-2 > div {
    flex: 1;
  }

  .grid-3 {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
  }

  .grid-3 > div {
    flex: 1;
  }

  .grid-4 {
    display: flex;
    gap: 6px;
    margin-bottom: 8px;
  }

  .grid-4 > div {
    flex: 1;
  }

  /* Cards & Callouts */
  .card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px 10px;
    margin-bottom: 7px;
  }

  .card-highlight {
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-left: 4px solid #0284c7;
    border-radius: 6px;
    padding: 7px 10px;
    margin-bottom: 7px;
  }

  .card-success {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-left: 4px solid #16a34a;
    border-radius: 6px;
    padding: 7px 10px;
    margin-bottom: 7px;
  }

  .card-warning {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-left: 4px solid #d97706;
    border-radius: 6px;
    padding: 7px 10px;
    margin-bottom: 7px;
  }

  .card-danger {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 4px solid #e11d48;
    border-radius: 6px;
    padding: 7px 10px;
    margin-bottom: 7px;
  }

  /* Tips Pemula Box */
  .tips-pemula {
    background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
    border: 1.5px solid #38bdf8;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 6px 0;
  }

  .tips-pemula strong {
    color: #0369a1;
    font-size: 8.5pt;
    display: block;
    margin-bottom: 2px;
  }

  /* Tables */
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 7px;
    font-size: 7.8pt;
  }

  th, td {
    padding: 4px 6px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }

  th {
    background: #0f172a;
    color: #ffffff;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 7.3pt;
    letter-spacing: 0.5px;
  }

  tr:nth-child(even) {
    background-color: #f8fafc;
  }

  /* Badges */
  .badge {
    display: inline-block;
    padding: 1.5px 5px;
    border-radius: 3px;
    font-size: 6.8pt;
    font-weight: 700;
    text-transform: uppercase;
  }

  .badge-blue { background-color: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }
  .badge-green { background-color: #dcfce7; color: #15803d; border: 1px solid #86efac; }
  .badge-red { background-color: #ffe4e6; color: #be123c; border: 1px solid #fda4af; }
  .badge-purple { background-color: #f3e8ff; color: #7e22ce; border: 1px solid #d8b4fe; }
  .badge-gold { background-color: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }

  /* Images */
  .img-container {
    width: 100%;
    text-align: center;
    margin: 5px 0;
  }

  .img-container img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 2px 4px rgba(0,0,0,0.06);
  }

  .img-caption {
    font-size: 7.2pt;
    color: #64748b;
    margin-top: 2px;
    font-style: italic;
  }

  /* Code Blocks */
  code {
    font-family: 'Consolas', monospace;
    background-color: #e2e8f0;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 8pt;
    color: #0f172a;
  }

  .code-block {
    background-color: #0f172a;
    color: #38bdf8;
    font-family: 'Consolas', monospace;
    font-size: 7.5pt;
    padding: 7px 10px;
    border-radius: 5px;
    line-height: 1.35;
    margin-bottom: 7px;
  }

  /* Step Counter */
  .step-number {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    background-color: #0284c7;
    color: #ffffff;
    font-size: 7.5pt;
    font-weight: bold;
    border-radius: 50%;
    margin-right: 5px;
  }
</style>
</head>
<body>

<!-- ==================== HALAMAN 1: COVER ==================== -->
<div class="page">
  <div class="cover">
    <div class="cover-top">
      <div class="cover-badge">BUKU PANDUAN RESMI METATRADER 5 • PEMULA HINGGA MAHIR</div>
      <h1 class="cover-title">VIKAR INSTITUTIONAL<br>4-PILLAR EA PRO</h1>
      <div class="cover-subtitle">Buku Manual Lengkap Pengoperasian Robot Trading Otomatis (v3.00 Apex Institutional Intelligence v3.00 (Smart Sideways & Anti-Fakeout))</div>
      
      <div class="cover-pillars">
        <div class="pillar-card">
          <h4>Pilar 1: SMC Core</h4>
          <p>BOS, CHoCH, Liquidity Sweep & Zona Diskon/Premium 50%</p>
        </div>
        <div class="pillar-card">
          <h4>Pilar 2: S/R Pivots</h4>
          <p>Daily Pivot Points, Double Alignment & Headroom ATR Protection</p>
        </div>
        <div class="pillar-card">
          <h4>Pilar 3: Triple EMA</h4>
          <p>EMA 8 Momentum, EMA 21 Ribbon & EMA 125 Macro Baseline</p>
        </div>
        <div class="pillar-card">
          <h4>Pilar 4: Fibonacci</h4>
          <p>Auto-Fibo SMC, Golden Pocket 61.8% & TP Target Projections</p>
        </div>
      </div>
    </div>

    <div class="cover-desc-box">
      <h4>Selamat Datang di Dunia Trading Otomatis yang Terukur & Disiplin!</h4>
      <p>
        Buku panduan ini disusun secara bertahap dan menggunakan bahasa yang sangat ramah bagi pemula. Anda akan mempelajari bagaimana robot trading <strong>VIKAR EA 4-Pillar Pro</strong> bekerja secara cerdas membaca pasar layaknya bank institusi besar, cara memasangnya di terminal MetaTrader 5 Didimax hanya dalam 5 menit, memilih preset setting terbaik sesuai modal Anda, hingga memahami bagaimana robot ini mengunci keuntungan Anda secara otomatis tanpa perlu begadang memelototi chart grafik 24 jam.
      </p>
    </div>

    <div>
      <div class="cover-meta">
        <div class="meta-item">
          <strong>Platform</strong>
          MetaTrader 5 (MT5 Didimax / ECN)
        </div>
        <div class="meta-item">
          <strong>Instrumen Utama</strong>
          XAU/USD (Gold) & Major FX
        </div>
        <div class="meta-item">
          <strong>Timeframe Rekomendasi</strong>
          M5 (Scalping) & M15 (Day Trade)
        </div>
        <div class="meta-item">
          <strong>Tingkat Kesulitan</strong>
          Sangat Mudah (Ramah Pemula)
        </div>
      </div>
      <div style="font-size: 7.5pt; color: #94a3b8; text-align: center;">
        Copyright &copy; 2026 Vikar Institutional Trading Strategy. Hak Cipta Dilindungi Undang-Undang.
      </div>
    </div>
  </div>
</div>

<!-- ==================== HALAMAN 2: DAFTAR ISI & PENGENALAN PEMULA ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 1: Daftar Isi & Pengenalan Untuk Pemula</div>
    <div class="chapter-badge">From Zero to Hero</div>
  </div>

  <div class="grid-2">
    <div class="card" style="padding: 10px;">
      <h3 style="color: #0284c7; margin: 0 0 6px 0; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 3px;">📖 Daftar Isi Buku Panduan</h3>
      <table style="margin: 0; font-size: 7.5pt;">
        <tr><td style="width: 25px; font-weight: bold; color: #0284c7;">Hal 2</td><td>Daftar Isi & Mengapa Pemula Membutuhkan Robot Trading</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 3</td><td>Mengenal Arsitektur 4 Pilar Rahasia Bank (Bahasa Sederhana)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 4</td><td>Visual Anatomi Pasar SMC (BOS, CHoCH, Diskon vs Premium)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 5</td><td>Order Block (OB) & Fair Value Gap (FVG) Bagi Pemula</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 6</td><td>Mesin Pengenal Pola Grafik & Candlestick Rejection Pintar</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 7</td><td>Sistem Skor Konfluensi (Rapor Nilai 0-100 Poin) & Shock Guard</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 8</td><td>Mekanisme Pertahanan Profit (Auto BE SL+, TP1 50%, Auto Cut)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 9</td><td>Manajemen Risiko Modal & Aturan Lot Didimax (0.10 Lot)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 10</td><td>Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing Engine v3.00)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 11</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Katalog 4 Preset Resmi (.set) & Cara Memilih Sesuai Modal</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Cara Membaca Layar Monitor (HUD Dashboard) di Chart</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 14</td><td>Tanya Jawab Masalah Umum (Troubleshooting & Solusi Error)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 15</td><td>Lembar Checklist SOP Harian & 5 Rukun Disiplin Trader</td></tr>
      </table>
    </div>

    <div>
      <div class="card-highlight">
        <h3 style="color: #0369a1; margin: 0 0 4px 0;">Apa Itu Robot Trading (Expert Advisor)?</h3>
        <p style="font-size: 8pt; margin: 0;">
          <strong>Expert Advisor (EA)</strong> adalah sebuah program asisten otomatis cerdas yang dipasang pada aplikasi MetaTrader 5. Robot ini bertugas menganalisis pergerakan harga emas (XAU/USD), mencari peluang transaksi dengan aturan matematika ketat, membuka posisi secara otomatis, dan mengunci keuntungannya tanpa campur tangan manusia.
        </p>
      </div>

      <div class="card-success">
        <h3 style="color: #15803d; margin: 0 0 4px 0;">Kenapa Pemula Memerlukan EA Vikar Pro?</h3>
        <ul style="margin: 0; padding-left: 16px; font-size: 7.8pt;">
          <li><strong>Anti-Emosi (Zero Greed & Fear):</strong> 90% trader pemula rugi karena rasa serakah atau takut. Robot tidak punya emosi dan 100% disiplin mematuhi SOP.</li>
          <li><strong>Bebas Lelah (24 Jam Non-Stop):</strong> Anda tidak perlu berjam-jam begadang memelototi chart. Biarkan sistem bekerja untuk Anda.</li>
          <li><strong>Proteksi Modal Teruji:</strong> Dilengkapi pengaman otomatis Stop Loss, kunci modal (Auto BE), dan pemotong kerugian dini jika analisa batal.</li>
        </ul>
      </div>
    </div>
  </div>

  <div class="tips-pemula">
    <strong>💡 Perumpamaan Sederhana Untuk Pemula:</strong>
    Trading manual itu seperti mengendarai mobil di tengah badai salju gelap gulita tanpa peta. Menggunakan <strong>VIKAR EA 4-Pillar Pro</strong> itu seperti menaiki pesawat komersial berteknologi *Autopilot* yang dipandu oleh 4 instrumen navigasi canggih, radar cuaca, dan sabuk pengaman otomatis!
  </div>

  <h2>Perbandingan Trading Manual vs Trading dengan Robot Vikar Pro</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Kondisi Trading</th>
        <th style="width: 37%;">Trading Manual (Biasa Dilakukan Pemula)</th>
        <th>Trading Bersama VIKAR EA 4-Pillar Pro</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Kapan Harus Masuk Pasar?</strong></td>
        <td>Menebak-nebak, FOMO ikut-ikutan sinyal grup telegram, sering terlambat beli di pucuk.</td>
        <td>Otomatis hanya masuk jika <strong>4 Pilar Konfluensi LULUS UJIAN</strong> (Skor &ge; 65-80 poin).</td>
      </tr>
      <tr>
        <td><strong>Saat Posisi Sedang Profit?</strong></td>
        <td>Cepat-cepat ditutup karena takut untungnya hilang, atau dibiarkan sampai berbalik jadi rugi.</td>
        <td>Otomatis mengunci modal ke <strong>SL+</strong>, menutup 50% di TP1, dan sisa lot memburu tren panjang.</td>
      </tr>
      <tr>
        <td><strong>Saat Terjadi Berita Besar?</strong></td>
        <td>Panik, order terseret slippage, atau terkena lonjakan candle tajam (MC).</td>
        <td>Fitur <strong>Shock Guard</strong> otomatis menahan posisi dan melindungi akun dari badai berita.</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ==================== HALAMAN 3: ARSITEKTUR 4 PILAR PEMULA ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 2: Mengenal 4 Pilar Rahasia Bank & Institusi</div>
    <div class="chapter-badge">Konsep Dasar</div>
  </div>

  <p>
    Mengapa disebut <strong>Sistem 4 Pilar</strong>? Karena sebuah bangunan kokoh membutuhkan 4 tiang penyangga agar tidak runtuh. Begitu pula transaksi trading emas Anda: robot tidak akan pernah membuka posisi jika salah satu pilar belum memberikan lampu hijau!
  </p>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>🏛️ PILAR 1: SMART MONEY CONCEPTS (SMC)</h3>
      <div style="font-size: 7.8pt; color: #0369a1; font-weight: bold; margin-bottom: 2px;">"Menunggangi Arus Modal Ikan Paus Institusi"</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Pasar finansial dikendalikan oleh bank-bank raksasa (*Smart Money*). Pilar SMC bertugas mendeteksi ke mana arah uang mereka mengalir.
        <br><strong>Aturan Sederhana:</strong> Robot hanya mencari peluang BUY saat pasar sedang dalam tren naik (*Bullish BOS*) dan harga sedang berada di <strong>Zona Diskon (Murah)</strong>.
      </p>
    </div>

    <div class="card-highlight">
      <h3>🎯 PILAR 2: SUPPORT & RESISTANCE (DAILY PIVOTS)</h3>
      <div style="font-size: 7.8pt; color: #0369a1; font-weight: bold; margin-bottom: 2px;">"Mengetahui Batas Lantai & Atap Harian"</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Ibarat sebuah rumah, lantai adalah <em>Support</em> dan atap adalah <em>Resistance</em>. Garis tengahnya adalah <strong>Central Pivot (P)</strong>.
        <br><strong>Aturan Sederhana:</strong> Jangan pernah membeli tepat di bawah atap! Robot memastikan masih ada "ruang bernapas" (*Headroom*) sebelum harga membentur dinding resisten.
      </p>
    </div>
  </div>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>📈 PILAR 3: TRIPLE EMA & MACRO ALIGNMENT</h3>
      <div style="font-size: 7.8pt; color: #0369a1; font-weight: bold; margin-bottom: 2px;">"Jalan Tol Tren & Tempat Istirahat Sehat"</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Menggunakan 3 garis rata-rata bergerak: <strong>EMA 8 Cyan</strong> (Kecepatan), <strong>EMA 21 Magenta</strong> (Pita Nilai), dan <strong>EMA 125 Putih</strong> (Arah Tren Besar).
        <br><strong>Aturan Sederhana:</strong> Jika harga berada di atas EMA 125, jalan tol mengarah ke atas. Kita menunggu harga "istirahat sejenak" (*Pullback*) ke pita EMA 8/21 sebelum ikut melaju kencang.
      </p>
    </div>

    <div class="card-highlight">
      <h3>🌀 PILAR 4: FIBONACCI RETRACEMENT & GOLDEN POCKET</h3>
      <div style="font-size: 7.8pt; color: #0369a1; font-weight: bold; margin-bottom: 2px;">"Matematika Alam Semesta: Rasio Emas 61.8%"</div>
      <p style="font-size: 7.8pt; margin: 0;">
        Fibonacci adalah rumus matematis alami yang digunakan para manajer investasi Wall Street untuk menentukan titik pantulan paling sempurna.
        <br><strong>Aturan Sederhana:</strong> Area antara 50% s/d 78.6% disebut <strong>Golden Pocket</strong>. Saat harga emas memantul di angka sakti <strong>61.8%</strong>, robot siap menembak!
      </p>
    </div>
  </div>

  <h2>Kamus Istilah: Bahasa Teknis vs Bahasa Manusia Sehari-hari</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Istilah Robot Trading</th>
        <th style="width: 30%;">Arti Teknis Pasar</th>
        <th>Bahasa Sederhana (Mudah Dipahami Pemula)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>BOS (Break of Structure)</strong></td>
        <td>Penembusan titik puncak/lembah sebelumnya</td>
        <td>"Tangga harga berhasil naik satu anak tangga lebih tinggi lagi."</td>
      </tr>
      <tr>
        <td><strong>CHoCH (Change of Character)</strong></td>
        <td>Pembalikan arah karakter tren pasar</td>
        <td>"Tanda-tanda mobil harga mulai berputar balik arah."</td>
      </tr>
      <tr>
        <td><strong>Liquidity Sweep (Stop Hunt)</strong></td>
        <td>Sapuan harga mengecoh stop loss trader ritel</td>
        <td>"Bandar menjatuhkan harga sebentar untuk memborong barang murah."</td>
      </tr>
      <tr>
        <td><strong>Discount Zone (&lt; 50%)</strong></td>
        <td>Harga berada di bawah rata-rata dealing range</td>
        <td>"Harga sedang diskon 50% di mall, saat terbaik untuk belanja!"</td>
      </tr>
      <tr>
        <td><strong>Double Alignment</strong></td>
        <td>Sinergi harga &gt; EMA 125 dan &gt; Pivot P</td>
        <td>"Lampu lalu lintas hijau ganda: aman untuk tancap gas maju."</td>
      </tr>
    </tbody>
  </table>

  <div class="tips-pemula">
    <strong>💡 Mengapa 4 Pilar Membuat Winrate Tinggi?</strong>
    Kebanyakan trader pemula hanya memakai 1 indikator saja (misal RSI saja atau Moving Average saja). Saat sinyal itu palsu (*false signal*), mereka langsung rugi. Dengan 4 pilar yang saling memverifikasi, potensi sinyal palsu tersaring hingga 85%!
  </div>
</div>

<!-- ==================== HALAMAN 4: ANATOMI SMC & STRUKTUR ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 3: Visual Anatomi Pasar SMC Bagi Pemula</div>
    <div class="chapter-badge">Visual Masterclass</div>
  </div>

  <h2>1. Memahami Siklus Tangga Pasar: BOS & Inducement</h2>
  <p>
    Lihat gambar di bawah ini. Harga tidak pernah bergerak naik lurus seperti garis lurus, melainkan membentuk pola tangga (naik, istirahat sedikit, lalu naik lagi lebih tinggi):
  </p>

  <div class="grid-2">
    <div class="img-container">
      <img src="__IMG_SMC_BOS__" style="max-height: 185px;" alt="BOS & Inducement">
      <div class="img-caption">Gambar 1: Struktur Bullish BOS (Tangga Naik) & Sapuan Pancingan (Inducement)</div>
    </div>
    <div class="img-container">
      <img src="__IMG_SMC_CHOCH__" style="max-height: 185px;" alt="CHoCH Reversal">
      <div class="img-caption">Gambar 2: Transisi Pembalikan Arah Bullish CHoCH (Awal Perubahan Tren)</div>
    </div>
  </div>

  <h2>2. Anatomi Gerakan Smart Money yang Wajib Diketahui:</h2>
  <div class="grid-3">
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">1. Higher High (Puncak Baru)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Ketika harga berhasil menembus puncak sebelumnya dan ditutup lebih tinggi, itu disebut <strong>BOS (Break of Structure)</strong>. Tanda bahwa pembeli masih sangat berkuasa.
      </p>
    </div>

    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">2. Pancingan (Inducement / IDM)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Bank besar sengaja membuat koreksi kecil untuk memancing trader pemula buru-buru masuk. Begitu ritel masuk, harga dibanting sebentar untuk membersihkan mereka.
      </p>
    </div>

    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">3. Sapuan Stop Hunt (Sweep)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Ekor lilin menyapu stop loss trader ritel di bawah lembah, lalu langsung melesat naik kencang. Robot kita mendeteksi sapuan ini sebagai sinyal emas!
      </p>
    </div>
  </div>

  <h2>3. Hukum Ekuilibrium 50%: Diskon vs Premium</h2>
  <div class="grid-2">
    <div class="card-success">
      <h3 style="color: #15803d; margin: 0 0 3px 0;">🟢 ZONA DISKON (Harga di Bawah 50%):</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Ibarat Anda membeli emas di toko saat sedang ada obral murah. Hanya di area inilah robot diizinkan melakukan <strong>BUY (Beli)</strong>. Jika harga sudah terlanjur melambung tinggi ke atas 50%, robot otomatis membatalkan niat membeli agar tidak terjebak di pucuk!
      </p>
    </div>

    <div class="card-danger">
      <h3 style="color: #be123c; margin: 0 0 3px 0;">🔴 ZONA PREMIUM (Harga di Atas 50%):</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Area di mana harga sudah berada di taraf mahal. Ini adalah tempat terbaik untuk melakukan <strong>SELL (Jual)</strong>. Trader pemula yang tidak tahu aturan ini seringkali membeli di area mahal dan panik saat harga mendadak anjlok.
      </p>
    </div>
  </div>

  <div class="tips-pemula">
    <strong>💡 Mengapa Trader Pemula Sering "Beli Langsung Turun, Jual Langsung Naik"?</strong>
    Karena pemula biasanya membeli saat lilin hijau sedang panjang-panjangnya (mereka membeli di zona Premium/Mahal). Robot VIKAR Pro mengajarkan kesabaran: tunggu harga kembali ke zona diskon dan menyentuh Order Block sebelum masuk pasar!
  </div>
</div>

<!-- ==================== HALAMAN 5: ORDER BLOCK & FVG ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 4: Order Block & Fair Value Gap Bagi Pemula</div>
    <div class="chapter-badge">Jejak Bank</div>
  </div>

  <h2>1. Apa Itu Order Block (OB)?</h2>
  <p>
    Bank-bank besar (seperti JPMorgan atau Citibank) tidak bisa membeli 10.000 lot sekaligus dalam satu detik karena akan membuat harga meledak seketika. Oleh karena itu, mereka memecah pesanan mereka menjadi ribuan tumpukan order. Sisa tumpukan pesanan yang tertinggal di grafik inilah yang dinamakan <strong>Order Block (OB)</strong>.
  </p>

  <div class="grid-2">
    <div class="card-success">
      <h3 style="color: #15803d; margin: 0 0 4px 0;">📦 Bullish Order Block (Base Demand)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Lilin merah (bearish) terakhir tepat sebelum terjadi lonjakan lilin hijau raksasa (*Displacement*).
        <br><strong>Cara Kerja:</strong> Ketika harga turun kembali menguji kotak Order Block ini, robot bersiap menekan tombol BUY karena bank besar akan menyerap sisa pesanan mereka di titik ini.
      </p>
    </div>

    <div class="card-danger">
      <h3 style="color: #be123c; margin: 0 0 4px 0;">📦 Bearish Order Block (Supply Zone)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Lilin hijau (bullish) terakhir tepat sebelum terjadi kejatuhan harga impulsif ke bawah.
        <br><strong>Cara Kerja:</strong> Ketika harga naik kembali menguji kotak ini, robot bersiap menekan tombol SELL karena area ini dipenuhi pesanan jual institusi.
      </p>
    </div>
  </div>

  <h2>2. Apa Itu Fair Value Gap (FVG)?</h2>
  <p>
    Saat bank besar memborong emas dalam jumlah luar biasa, pergerakan lilin begitu cepat sehingga meninggalkan "celah ketidakseimbangan" (*Market Imbalance*). Celah inilah yang disebut <strong>Fair Value Gap (FVG)</strong>.
  </p>

  <div class="card-highlight">
    <h3 style="margin: 0 0 4px 0; color: #0284c7;">⚡ Hukum Magnet Harga:</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      Pasar finansial membenci celah yang kosong. Ibarat lubang di jalan raya yang harus diaspal kembali, harga memiliki sifat alamiah untuk kembali "menjemput dan menutup" (*Mitigation Retest*) celah FVG tersebut sebelum melanjutkan tren aslinya. Robot kita memanfaatkan momen pantulan dari celah ini untuk mencetak keuntungan!
    </p>
  </div>

  <h2>3. Fitur Proteksi Cerdas: Early Invalidation Cut</h2>
  <p>
    Bagaimana jika analisa pasar salah? Pasar finansial tidak ada yang 100% pasti. Namun robot <strong>VIKAR EA 4-Pillar Pro</strong> memiliki sensor pertahanan unik:
  </p>

  <div class="card-danger">
    <h3 style="color: #be123c; margin: 0 0 4px 0;">🛡️ Menutup Posisi Lebih Cepat Sebelum Kena Stop Loss Penuh:</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      Jika kita sedang membuka posisi BUY di Order Block, namun mendadak keluar lilin raksasa berlawanan yang menembus dasar Order Block acuan, robot tidak akan pasrah menunggu harga menyentuh Stop Loss akhir. 
      <br><strong>Sistem akan memotong posisi secara dini (*Early Cut*)</strong>, sehingga kerugian hanya sekitar 30-40% dari risiko normal. Ini adalah rahasia kenapa akun Anda tetap aman dan terhindar dari kebangkrutan (*Anti-Ruin*)!
    </p>
  </div>

  <div class="tips-pemula">
    <strong>💡 Kunci Keberhasilan Trader:</strong>
    Trader amatir fokus pada "Berapa banyak uang yang bisa saya menangkan hari ini?". Trader profesional dan robot cerdas fokus pada "Berapa sedikit risiko yang boleh terjadi jika saya salah?". Saat risiko terjaga, keuntungan akan bertumbuh dengan sendirinya!
  </div>
</div>

<!-- ==================== HALAMAN 6: POLA GRAFIK & CANDLESTICK ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 5: Mesin Pengenal Pola Grafik & Candlestick Pintar</div>
    <div class="chapter-badge">Kecerdasan v2.1</div>
  </div>

  <h2>1. Mesin Pengenal Pola Grafik (Chart Pattern Recognition Engine)</h2>
  <p>
    Pada pembaruan <strong>v2.1 Master Intelligence</strong>, robot telah dibekali kecerdasan buatan untuk membaca geometri chart multi-lilin. Robot secara otomatis menandai pola-pola berikut di layar:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Nama Pola Grafik</th>
        <th style="width: 15%;">Nilai Bonus</th>
        <th>Bentuk Pola & Artinya Bagi Trader Pemula</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Quasimodo (QM Setup)</strong></td>
        <td><span class="badge badge-purple">+15 Poin (Elit)</span></td>
        <td>Bentuk bahu kiri-kepala-bahu kanan unik di mana harga menyapu puncak tertinggi lalu membanting ke bawah. Sinyal pembalikan arah paling akurat di dunia!</td>
      </tr>
      <tr>
        <td><strong>Double Bottom (Huruf W)</strong></td>
        <td><span class="badge badge-green">+12 Poin</span></td>
        <td>Bentuk grafik menyerupai <strong>huruf W</strong>. Dua lembah kembar yang membuktikan harga tidak mampu turun lebih dalam lagi & siap memantul naik.</td>
      </tr>
      <tr>
        <td><strong>Double Top (Huruf M)</strong></td>
        <td><span class="badge badge-red">+12 Poin</span></td>
        <td>Bentuk grafik menyerupai <strong>huruf M</strong>. Dua puncak kembar di atap yang membuktikan harga gagal menembus ke atas & siap terjun bebas.</td>
      </tr>
      <tr>
        <td><strong>Head & Shoulders (H&S)</strong></td>
        <td><span class="badge badge-blue">+14 Poin</span></td>
        <td>Pola Kepala dan Bahu. Pembalikan tren struktural 3 ayunan yang sangat disukai bank institusi.</td>
      </tr>
      <tr>
        <td><strong>Bullish / Bearish Flags</strong></td>
        <td><span class="badge badge-gold">+10 Poin</span></td>
        <td>Bentuk menyerupai bendera berkibar. Setelah lonjakan tiang bendera yang kuat, harga istirahat miring sebentar sebelum meledak melanjutkan arah semula.</td>
      </tr>
    </tbody>
  </table>

  <h2>2. Pengenalan Pola Candlestick Rejection Lanjutan</h2>
  <div class="grid-2">
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">🕯️ Three White Soldiers (Pasukan Putih)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Tiga lilin hijau berturut-turut dengan body tebal yang ditutup semakin tinggi. Menandakan gelombang pembeli sedang menyerbu pasar tanpa ampun.
      </p>
    </div>
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">🕯️ Dragonfly & Gravestone Doji</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Lilin dengan ekor sangat panjang (&ge; 70%) dan badan super tipis. Membuktikan ada perlawanan harga yang sangat dahsyat dari pihak lawan.
      </p>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">🕯️ Bullish & Bearish Harami (Ibu Hamil)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Lilin kedua berukuran lebih kecil dan berada sepenuhnya di dalam perut lilin pertama (*Inside Bar*). Tanda kompresi energi sebelum lonjakan besar.
      </p>
    </div>
    <div class="card">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">🕯️ Piercing Line & Dark Cloud Cover</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Lilin kedua menembus dan menelan lebih dari 50% tubuh lilin sebelumnya. Tanda penyerapan tenaga penjual oleh pembeli (*Absorption*).
      </p>
    </div>
  </div>

  <div class="tips-pemula">
    <strong>💡 Kenapa Pola Candlestick Saja Tidak Cukup?</strong>
    Banyak pemula melihat pola Pin Bar langsung buru-buru BUY di mana saja, padahal lokasinya di tengah jalan. Robot VIKAR Pro hanya menganggap pola lilin valid jika muncul tepat di <strong>Ribbon EMA 8/21</strong> atau di <strong>Golden Pocket Fibonacci 61.8%</strong>!
  </div>
</div>

<!-- ==================== HALAMAN 7: SISTEM SKOR KONFLUENSI ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 6: Sistem Skor Konfluensi (Rapor Nilai 0 - 100)</div>
    <div class="chapter-badge">Grade Filter</div>
  </div>

  <h2>Bagaimana Robot Menilai Kualitas Pasar Sebelum Bertransaksi?</h2>
  <p>
    Bayangkan seorang guru yang mengoreksi lembar ujian muridnya. Robot <strong>VIKAR EA 4-Pillar Pro</strong> menguji kondisi pasar dengan 9 mata pelajaran teknikal. Hanya kondisi pasar yang mendapatkan rapor <strong>nilai di atas 65 poin</strong> yang diizinkan untuk dieksekusi:
  </p>

  <table>
    <thead>
      <tr>
        <th style="width: 30%;">Mata Pelajaran Ujian</th>
        <th style="width: 15%;">Nilai Maksimal</th>
        <th>Kriteria Penilaian yang Harus Terpenuhi</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1. Struktur Tren Pasar SMC</td>
        <td><strong>20 Poin</strong></td>
        <td>BOS Searah (+15 Poin) | CHoCH Reversal Kuat (+20 Poin) | Zona Diskon/Premium (+5 Poin).</td>
      </tr>
      <tr>
        <td>2. Pengujian Order Block</td>
        <td><strong>20 Poin</strong></td>
        <td>Ada zona OB aktif (+8 Poin) | Harga tepat menyentuh area Base Demand (+12 Poin).</td>
      </tr>
      <tr>
        <td>3. Daya Dorong Displacement</td>
        <td><strong>15 Poin</strong></td>
        <td>Lilin pemicu memiliki body impulsif panjang &ge; 1.25x nilai normal ATR pasar.</td>
      </tr>
      <tr>
        <td>4. Fair Value Gap (FVG)</td>
        <td><strong>15 Poin</strong></td>
        <td>Ada celah ketidakseimbangan likuiditas yang sedang diisi dan memantul (+15 Poin).</td>
      </tr>
      <tr>
        <td>5. Sapuan Stop Loss (Sweep)</td>
        <td><strong>10 Poin</strong></td>
        <td>Ekor lilin berhasil menyapu stop loss trader ritel sebelum berbalik (+10 Poin).</td>
      </tr>
      <tr>
        <td>6. Fibonacci Golden Pocket</td>
        <td><strong>10 Poin</strong></td>
        <td>Harga tepat memantul di area rasio emas 0.500 s/d 0.786 (+10 Poin).</td>
      </tr>
      <tr>
        <td>7. Triple EMA Ribbon</td>
        <td><strong>10 Poin</strong></td>
        <td>Harga berada di jalan tol EMA 125 (+5 Poin) | Pita EMA 8 dan 21 mekar searah (+5 Poin).</td>
      </tr>
      <tr>
        <td>8. Pola Candlestick Rejection</td>
        <td><strong>10 Poin</strong></td>
        <td>Terbentuk pola lilin berkualitas tinggi seperti Pin Bar, Engulfing, atau Doji (+10 Poin).</td>
      </tr>
      <tr>
        <td>9. Bonus Pola Grafik</td>
        <td><strong>15 Poin</strong></td>
        <td>Terbentuk pola Quasimodo, Double Bottom (W), atau Flag (Bonus hingga +15 Poin!).</td>
      </tr>
    </tbody>
  </table>

  <h2>3 Tingkatan Rapor Sinyal (Grade Filter)</h2>
  <div class="grid-3">
    <div class="card-success">
      <h3 style="color: #15803d; margin: 0 0 3px 0;">GRADE A+ SNIPER</h3>
      <div style="font-size: 15pt; font-weight: 800; color: #16a34a; margin-bottom: 3px;">Nilai &ge; 80 Poin</div>
      <p style="font-size: 7.5pt; margin: 0;">
        Kondisi pasar bintang lima! Semua pilar sepakat dan pola elit terbentuk. Tingkat kemenangan tertinggi.
      </p>
    </div>

    <div class="card-highlight">
      <h3 style="color: #0369a1; margin: 0 0 3px 0;">GRADE A HIGH PROB</h3>
      <div style="font-size: 15pt; font-weight: 800; color: #0284c7; margin-bottom: 3px;">Nilai 65 - 79 Poin</div>
      <p style="font-size: 7.5pt; margin: 0;">
        Kondisi pasar sangat bagus, memenuhi syarat tren utama EMA 125 dan Daily Pivot P. Dieksekusi normal.
      </p>
    </div>

    <div class="card-danger">
      <h3 style="color: #be123c; margin: 0 0 3px 0;">GRADE B REJECT</h3>
      <div style="font-size: 15pt; font-weight: 800; color: #e11d48; margin-bottom: 3px;">Nilai &lt; 65 Poin</div>
      <p style="font-size: 7.5pt; margin: 0;">
        Pasar jelek, sideways, atau banyak noise. <strong>DITOLAK OTOMATIS</strong> oleh robot demi menjaga uang Anda!
      </p>
    </div>
  </div>

  <div class="card-warning">
    <h3 style="color: #b45309; margin: 0 0 3px 0;">⚡ Payung Pelindung Berita: SHOCK GUARD</h3>
    <p style="margin: 0; font-size: 7.8pt;">
      Saat ada berita ekonomi besar Amerika (seperti data pengangguran NFP atau inflasi CPI), harga emas sering melompat ratusan pips dalam 1 detik. Fitur <strong>Shock Guard</strong> otomatis mendeteksi lonjakan abnormal ini dan <strong>mengunci sistem selama 2-3 lilin</strong> agar akun Anda tidak terkena jebakan badai!
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 8: FITUR PERTAHANAN PROFIT ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 7: Cara Robot Mengamankan Keuntungan Anda</div>
    <div class="chapter-badge">Profit Defense</div>
  </div>

  <h2>Mengapa Banyak Trader Pernah Profit Tapi Berujung Rugi?</h2>
  <p>
    Pernahkah Anda mengalami: posisi Anda sudah untung +$50, Anda biarkan karena ingin untung lebih banyak, namun 1 jam kemudian harga berbalik drastis dan posisi Anda malah rugi -$100?
    <br><strong>VIKAR EA 4-Pillar Pro diciptakan untuk menghentikan mimpi buruk tersebut selamanya</strong> melalui 4 lapis sistem pertahanan keuntungan:
  </p>

  <div class="grid-2">
    <div class="card-success">
      <h3 style="color: #15803d; margin: 0 0 4px 0;">1. Gembok Modal Otomatis (Auto-Breakeven / SL+)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Begitu posisi Anda mencapai keuntungan minimal (misal <strong>+8.0 pips</strong>), robot akan langsung menggeser garis Stop Loss melewati harga awal beli Anda (misal ke <strong>+2.5 pips profit</strong>).
        <br><strong>Hasilnya:</strong> Transaksi Anda kini berstatus <strong>Bebas Risiko (Risk-Free)</strong>! Apapun yang terjadi pada pasar setelah ini, Anda TIDAK AKAN PERNAH RUGI dan minimal membawa pulang keuntungan kecil!
      </p>
    </div>

    <div class="card-highlight">
      <h3 style="color: #0369a1; margin: 0 0 4px 0;">2. Amankan 50% di Awal (Partial Take Profit TP1)</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Trader bijak tidak serakah. Saat harga mencapai target awal TP1 (misal <strong>+10.0 s/d +15.0 pips</strong>):
        <br>• <strong>50% lot ditutup langsung</strong> & uangnya masuk ke saldo riil dompet Anda.
        <br>• Sisa 50% lot dipasangi pengaman SL+ dan dibiarkan berjalan sebagai <strong>RUNNER</strong> untuk mengejar keuntungan besar hingga ratusan pips!
      </p>
    </div>
  </div>

  <div class="grid-2">
    <div class="card">
      <h3 style="color: #0f172a; margin: 0 0 4px 0;">3. Pengawal Setia: Trailing Stop EMA 21</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Jika harga emas sedang mengalami tren reli panjang (misal terbang naik 200 pips):
        <br>Robot tidak akan menutup posisi terlalu cepat. Garis Stop Loss akan dinaikkan pelan-pelan mengikuti pita <strong>EMA 21 Magenta</strong>. Posisi baru ditutup saat ada lilin yang benar-benar menembus garis EMA 21 tersebut. Memaksimalkan cuan hingga titik darah penghabisan!
      </p>
    </div>

    <div class="card-danger">
      <h3 style="color: #be123c; margin: 0 0 4px 0;">4. Sensor Bahaya: Auto-Cut Profit Reversal</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Jika posisi Anda sedang untung (+5 pips), tetapi tiba-tiba di ujung jalan muncul tanda bahaya (seperti lilin pembalikan arah tajam atau struktur CHoCH berlawanan):
        <br><strong>Robot tidak akan menunggu sampai profit Anda habis!</strong> Robot langsung menutup transaksi seketika untuk mengamankan keuntungan yang ada di tangan.
      </p>
    </div>
  </div>

  <h2>Alur Kerja Pengamanan Transaksi Dari Detik ke Detik:</h2>
  <div class="card" style="background: #0f172a; color: #ffffff; padding: 10px;">
    <div style="display: flex; justify-content: space-between; font-size: 7.5pt; text-align: center;">
      <div style="flex: 1; border-right: 1px dashed #334155; padding: 0 5px;">
        <div style="color: #38bdf8; font-weight: bold; margin-bottom: 2px;">FASE 1: ENTRY</div>
        Lulus Skor 4 Pilar &ge; 65<br>Buka BUY dengan SL Aman
      </div>
      <div style="flex: 1; border-right: 1px dashed #334155; padding: 0 5px;">
        <div style="color: #4ade80; font-weight: bold; margin-bottom: 2px;">FASE 2: PROFIT +8p</div>
        Auto BE Aktif!<br>Geser SL ke SL+ (Kunci Modal)
      </div>
      <div style="flex: 1; border-right: 1px dashed #334155; padding: 0 5px;">
        <div style="color: #facc15; font-weight: bold; margin-bottom: 2px;">FASE 3: TP1 +10p</div>
        Tutup 50% Lot Pertama<br>Cuan Masuk Kantong Riil
      </div>
      <div style="flex: 1; padding: 0 5px;">
        <div style="color: #f43f5e; font-weight: bold; margin-bottom: 2px;">FASE 4: RUNNER</div>
        Sisa 50% Mengikuti EMA 21<br>Memburu Profit Ekstensi Fibo
      </div>
    </div>
  </div>

  <div class="tips-pemula">
    <strong>💡 Mengapa Trader Pemula Sangat Nyaman Bersama EA Ini?</strong>
    Karena rasa cemas "Gimana ya kalau habis ini harga turun?" sudah dihapus oleh fitur Auto-Breakeven. Begitu posisi sudah jalan beberapa menit, modal Anda sudah 100% aman terkunci!
  </div>
</div>

<!-- ==================== HALAMAN 9: MANAJEMEN RISIKO & DIDIMAX ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8: Manajemen Risiko & Aturan Lot Didimax</div>
    <div class="chapter-badge">Safety First</div>
  </div>

  <h2>1. Memahami Karakter Broker DIDIMAX (Minimal 0.10 Lot)</h2>
  <p>
    Bagi Anda yang menggunakan broker lokal teregulasi BAPPEBTI seperti <strong>DIDIMAX</strong>, ada satu aturan fundamental yang wajib dipahami: ukuran transaksi minimal untuk instrumen Emas (XAU/USD) adalah <strong>0.10 lot</strong> (bukan 0.01 lot mikro seperti broker luar negeri tak berizin).
  </p>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>Berapa Nilai 0.10 Lot di Emas XAU/USD?</h3>
      <ul style="margin: 0; padding-left: 16px; font-size: 7.8pt;">
        <li>Pergerakan harga sebesar <strong>$1.00</strong> (10 pips) = bernilai <strong>$10.00</strong> profit / risiko.</li>
        <li>Pergerakan harga sebesar <strong>$0.10</strong> (1 pip) = bernilai <strong>$1.00</strong>.</li>
        <li>Jika Stop Loss Anda 25 pips ($2.50 harga emas), maka risikonya adalah <strong>$25.00</strong>.</li>
      </ul>
    </div>

    <div class="card-success">
      <h3 style="color: #15803d;">Proteksi Safeguard Otomatis di Versi v2.1</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Anda tidak perlu pusing menghitung! Versi terbaru robot ini telah dilengkapi <strong>Auto-Broker Lot Detection</strong>. Robot secara otomatis menyesuaikan ukuran lot agar patuh pada syarat minimal Didimax (0.10) dan membatasi agar tidak sengaja memasang lot besar yang membahayakan akun!
      </p>
    </div>
  </div>

  <h2>2. Tabel Rekomendasi Modal Akun vs Pilihan Preset</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 22%;">Saldo Akun ($ USD)</th>
        <th style="width: 15%;">Ukuran Lot</th>
        <th style="width: 30%;">Preset yang Disarankan</th>
        <th>Tingkat Keamanan & Karakteristik</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>$1.000 - $2.000</strong></td>
        <td>0.10 Lot (Min)</td>
        <td><code>XAUUSD_HIGH_WINRATE_SNIPER.set</code></td>
        <td><span class="badge badge-green">Paling Aman (Ultra Konservatif)</span><br>Hanya mengambil setup Grade A+ bintang lima, risiko sangat terkendali.</td>
      </tr>
      <tr>
        <td><strong>$2.500 - $5.000</strong></td>
        <td>0.10 Lot (Min)</td>
        <td><code>XAUUSD_FAST_AUTO_TRADE.set</code></td>
        <td><span class="badge badge-blue">Sangat Sehat (Aktif Cuan)</span><br>Transaksi lebih sering, kunci profit di +8 pips, scaling profit sangat lancar.</td>
      </tr>
      <tr>
        <td><strong>$5.000 - $10.000</strong></td>
        <td>0.10 - 0.20 Lot</td>
        <td><code>XAUUSD_M5_Scalping_Confluence.set</code></td>
        <td><span class="badge badge-purple">Pertumbuhan Cepat (Growth)</span><br>Memanfaatkan sinergi timeframe H1 dan M5 untuk profit konsisten.</td>
      </tr>
      <tr>
        <td><strong>&gt; $10.000</strong></td>
        <td>0.20 - 0.50 Lot</td>
        <td><code>XAUUSD_M15_DayTrading_GradeA.set</code></td>
        <td><span class="badge badge-gold">Institusional (Big Runner)</span><br>Memburu gelombang tren besar hingga target puluhan juta rupiah.</td>
      </tr>
    </tbody>
  </table>

  <h2>3. Aturan Ketat Anti-Kebangkrutan (Zero Martingale & Anti-Hedging)</h2>
  <div class="grid-2">
    <div class="card-danger">
      <h3 style="color: #be123c; margin: 0 0 3px 0;">DILARANG SISTEM MARTINGALE!</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Robot murahan di internet sering menggunakan sistem melipatgandakan lot saat rugi (Martingale: 0.1, lalu 0.2, 0.4, 0.8...). Sistem ini 100% PASTI berujung akun hangus (Margin Call)! <strong>VIKAR EA Pro murni single order disiplin</strong> tanpa melipat lot.
      </p>
    </div>

    <div class="card-success">
      <h3 style="color: #15803d; margin: 0 0 3px 0;">HANYA 1 POSISI DALAM 1 WAKTU</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Parameter <code>InpMaxOpenPositions = 1</code> mengunci agar robot fokus mengawal satu posisi saja sampai selesai tuntas. Tidak ada istilah floating puluhan order yang bikin pusing kepala!
      </p>
    </div>
  </div>

  <div class="tips-pemula">
    <strong>💡 Pesan Penting Tentang Saldo Minimal:</strong>
    Meskipun Didimax memperbolehkan deposit mulai dari $500, untuk ketahanan mental dan kenyamanan Anda dalam menghadapi fluktuasi emas, sangat disarankan memulai dengan saldo <strong>minimal $1.000 s/d $2.000</strong> dengan lot tetap 0.10.
  </div>
</div>

<!-- ==================== HALAMAN 9B: MESIN OTOPSI & KOREKSI DIRI PASCA-SL ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8B: Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing v3.00)</div>
    <div class="chapter-badge">AI Self-Healing</div>
  </div>

  <h2>Bagaimana Robot Memperbaiki Dirinya Sendiri Saat Terkena Stop Loss?</h2>
  <p style="font-size: 8pt; margin-bottom: 8px;">
    Banyak robot konvensional hanya "pasrah" saat terkena Stop Loss dan mengulangi kesalahan yang sama pada trade berikutnya. 
    <strong>VIKAR EA Pro v3.00</strong> dilengkapi mesin otopsi cerdas: robot langsung membongkar alasan teknikal kenapa SL tersentuh, lalu <strong>mengubah perilakunya secara otomatis</strong> untuk melindungi akun Anda!
  </p>

  <div class="card-danger" style="margin-bottom: 8px;">
    <h3 style="color: #be123c; margin: 0 0 3px 0;">🔍 1. Otopsi Seketika (4 Diagnosa Akar Masalah Pasar)</h3>
    <div class="grid-2" style="font-size: 7.5pt;">
      <div>
        • <strong>Volatilitas Abnormal (News Shock):</strong> Lilin lonjakan berita kilat (&ge; 2.2&times; ATR).<br>
        • <strong>Liquidity Sweep (Shakeout):</strong> Ekor lilin sengaja menyapu stop loss sebelum harga berbalik.
      </div>
      <div>
        • <strong>Pembalikan Struktur Makro:</strong> Terjadi CHoCH atau penembusan garis EMA 125.<br>
        • <strong>Pengujian Level Gagal:</strong> Setup minor kehilangan momentum di zona diskon/premium.
      </div>
    </div>
  </div>

  <h3 style="margin: 8px 0 4px 0; font-size: 8.5pt;">⚙️ 2. Tiga Langkah Proteksi & Koreksi Diri Mandiri:</h3>
  <div class="grid-3" style="font-size: 7.5pt;">
    <div class="card" style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 7px;">
      <div style="font-weight: bold; color: #0284c7; margin-bottom: 2px;">🎯 Penalti Skor Konfluensi</div>
      Ambang skor minimum otomatis dinaikkan <strong>+10 Poin</strong> (misal dari 55 menjadi 65). Robot hanya mengeksekusi sinyal sempurna <em>Grade A+</em>.
    </div>
    <div class="card" style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 7px;">
      <div style="font-weight: bold; color: #0284c7; margin-bottom: 2px;">⛔ Karantina Pola Gagal</div>
      Pola candlestick / chart pattern pemicu kerugian <strong>dikarantina selama 15 bar lilin</strong>. Robot memblokir order dari pola tersebut.
    </div>
    <div class="card" style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 7px;">
      <div style="font-weight: bold; color: #0284c7; margin-bottom: 2px;">🛡️ Adaptive SL Buffer</div>
      Jarak Stop Loss diperlebar <strong>+0.3&times; ATR</strong> untuk <strong>3 trade berikutnya</strong>, mencegah posisi tersapu oleh ekor lilin liar.
    </div>
  </div>

  <div class="grid-2" style="margin-top: 8px;">
    <div class="card-success">
      <h4 style="color: #15803d; margin: 0 0 2px 0; font-size: 7.8pt;">🔄 Pemulihan Otomatis (Self-Reset)</h4>
      <p style="font-size: 7.3pt; margin: 0;">
        Begitu trade berikutnya menang (Take Profit) atau terkunci keuntungan (SL+ Break-Even), seluruh penalti dan karantina otomatis direset ke status normal!
      </p>
    </div>
    <div class="card-warning">
      <h4 style="color: #b45309; margin: 0 0 2px 0; font-size: 7.8pt;">📲 Notifikasi Otopsi ke Smartphone</h4>
      <p style="font-size: 7.3pt; margin: 0;">
        Notifikasi dikirim langsung ke aplikasi MT5 HP Anda: memuat tiket order, diagnosa penyebab SL, dan status pengetatan yang sedang diberlakukan.
      </p>
    </div>
  </div>

  <div class="tips-pemula" style="margin-top: 8px;">
    <strong>💡 Keuntungan Utama Untuk Trader:</strong>
    Akun Anda terlindungi dari bahaya <em>revenge trading</em> (balas dendam) dan rangkaian kekalahan beruntun (<em>loss streak</em>). Robot berpikir dingin, mengevaluasi kesalahan, dan kembali dengan setup terkuat!
  </div>
</div>

<!-- ==================== HALAMAN 9C: KECERDASAN KUANTITATIF (PATTERN MATRIX & SENSOR CUACA) ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8C: Kecerdasan Kuantitatif v3.00 (Pattern Matrix & Sensor Cuaca)</div>
    <div class="chapter-badge">AI Quantitative</div>
  </div>

  <h2>Dua Terobosan Sains Trading Kuantitatif di Versi 2.50</h2>
  <p style="font-size: 8pt; margin-bottom: 8px;">
    Menggabungkan kecerdasan adaptif statistik institusional: robot tidak hanya menghafal pola, tetapi <b>menilai efektivitas setiap pola di pasar saat ini</b> dan <b>mengukur kadar kekacauan pasar (Entropi Choppiness)</b> secara matematis!
  </p>

  <div class="card" style="margin-bottom: 8px; border-left: 4px solid #0284c7; padding: 8px;">
    <div style="font-weight: bold; color: #0284c7; font-size: 8.5pt; margin-bottom: 3px;">📊 1. Dynamic Pattern Performance Matrix (AI Pattern Learning)</div>
    <p style="font-size: 7.5pt; margin: 0 0 5px 0;">
      Robot mencatat buku rapor kemenangan (Win Rate) untuk 12 kategori pola candlestick & chart pattern secara real-time dan persisten di memori MT5:
    </p>
    <div class="grid-3" style="font-size: 7.3pt;">
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 6px; border-radius: 6px;">
        <strong style="color: #15803d;">🚀 DYNAMIC BOOST (+10 Poin)</strong><br>
        Jika pola memiliki <b>Win Rate &ge; 70%</b>, robot memberi bonus skor +10 Poin. Setup yang sedang terbukti ampuh diprioritaskan!
      </div>
      <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 6px; border-radius: 6px;">
        <strong style="color: #b91c1c;">⛔ AUTO-BLACKLIST (&lt; 40%)</strong><br>
        Jika pola memiliki <b>Win Rate &lt; 40%</b>, robot otomatis memblokir order dari pola tersebut. Menolak setup yang sering gagal!
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px;">
        <strong style="color: #0369a1;">💾 MEMORI PERSISTEN</strong><br>
        Data statistik tersimpan aman di Global Variable MT5 dan tidak akan terhapus meskipun terminal MT5 ditutup atau laptop restart.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom: 8px; border-left: 4px solid #f59e0b; padding: 8px;">
    <div style="font-weight: bold; color: #f59e0b; font-size: 8.5pt; margin-bottom: 3px;">🌪️ 2. Market Regime Classifier (Sensor Cuaca Choppiness Index)</div>
    <p style="font-size: 7.5pt; margin: 0 0 5px 0;">
      Mengukur entropi fraktal 14-periode untuk membedakan apakah pasar emas sedang tren kencang atau sideways sempit:
    </p>
    <div class="grid-3" style="font-size: 7.3pt;">
      <div style="background: #f0f9ff; border: 1px solid #bae6fd; padding: 6px; border-radius: 6px;">
        <strong style="color: #0284c7;">🌊 STRONG TREND (CI &lt; 38.2)</strong><br>
        Pasar bergerak searah dengan volume besar. Eksekusi <i>Momentum Breakout</i> aktif penuh memburu ekspansi tren raksasa.
      </div>
      <div style="background: #fffbeb; border: 1px solid #fde68a; padding: 6px; border-radius: 6px;">
        <strong style="color: #b45309;">🎯 NORMAL TREND (38.2 - 61.8)</strong><br>
        Pasar bergerak sehat. Robot menerapkan aturan 4 Pilar sniper standard (Pullback Ribbon EMA + Golden Pocket Fibo).
      </div>
      <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 6px; border-radius: 6px;">
        <strong style="color: #b91c1c;">🛑 CHOPPY SIDEWAYS (CI &gt; 61.8)</strong><br>
        Pasar kompresi sempit. <b>Momentum Breakout DIBLOKIR TOTAL</b> (mencegah 85% fakeout) dan ambang skor dinaikkan +10 Poin!
      </div>
    </div>
  </div>

  <div class="card-success" style="padding: 7px;">
    <h4 style="color: #15803d; margin: 0 0 2px 0; font-size: 7.8pt;">🖥️ Terintegrasi Langsung ke Glassmorphic Dashboard HUD MT5:</h4>
    <p style="font-size: 7.3pt; margin: 0;">
      Layar chart Anda kini menampilkan baris indikator cuaca pasar terkini <code>[Cuaca Pasar: TRENDING (CI: 31.4)]</code> serta rekap pola terbaik <code>[Rapor Pola: Pin Bar (80%)]</code> secara real-time!
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 9D: PERISAI PRE-NEWS, SPREAD SPIKE & DIVERGENSI RSI ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8D: Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v3.00)</div>
    <div class="chapter-badge">Institutional Shield</div>
  </div>

  <h2>Tiga Lapisan Perlindungan Tingkat Tinggi di Versi 2.60</h2>
  <p style="font-size: 8pt; margin-bottom: 8px;">
    Mencegah kerugian dari faktor eksternal pasar yang tidak bisa dianalisis dengan teknikal murni: gejolak berita ekonomi AS, manipulasi spread broker, dan jebakan membeli di pucuk / menjual di dasar lembah!
  </p>

  <div class="card" style="margin-bottom: 7px; border-left: 4px solid #ef4444; padding: 7px;">
    <div style="font-weight: bold; color: #ef4444; font-size: 8.5pt; margin-bottom: 3px;">🛡️ 1. Pre-News Event & Spread Spike Shield (Section 8.7)</div>
    <p style="font-size: 7.4pt; margin: 0 0 4px 0;">
      Perlindungan otomatis saat rilis data ekonomi berdampak tinggi AS (CPI, NFP, PPI, FOMC):
    </p>
    <div class="grid-3" style="font-size: 7.2pt;">
      <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 5px; border-radius: 5px;">
        <strong style="color: #b91c1c;">❄️ PEMBEKUAN ORDER</strong><br>
        Order baru <b>dibekukan 20 menit sebelum s/d 25 menit sesudah</b> rilis berita (15:30 & 21:00 server). Anti tersapu lonjakan harga!
      </div>
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 5px; border-radius: 5px;">
        <strong style="color: #15803d;">🔒 AUTO-LOCK BE NEWS</strong><br>
        Posisi yang sedang profit otomatis ditarik SL-nya ke <b>SL+ (Break-Even)</b> sebelum berita keluar. Modal 100% terlindungi tanpa risiko!
      </div>
      <div style="background: #fffbeb; border: 1px solid #fde68a; padding: 5px; border-radius: 5px;">
        <strong style="color: #b45309;">⚡ SPREAD SPIKE (&gt;1.8x)</strong><br>
        Jika spread melebar di atas 1.8x batas normal, eksekusi ditunda sampai pasar tenang dan spread kembali rapat.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom: 7px; border-left: 4px solid #8b5cf6; padding: 7px;">
    <div style="font-weight: bold; color: #8b5cf6; font-size: 8.5pt; margin-bottom: 3px;">📈 2. RSI Momentum Divergence Exhaustion Sensor (Section 8.8)</div>
    <p style="font-size: 7.4pt; margin: 0 0 4px 0;">
      Mendeteksi kelelahan tren melalui divergensi harga vs RSI 14 periode:
    </p>
    <div class="grid-2" style="font-size: 7.2pt;">
      <div style="background: #fdf4ff; border: 1px solid #f0abfc; padding: 5px; border-radius: 5px;">
        <strong style="color: #86198f;">🚫 CEGAH BELI DI PUCUK (Bearish Divergence)</strong><br>
        Jika harga mencetak Higher High namun RSI mencetak Lower High di area overbought (>60), sinyal BUY <b>DIBATALKAN</b> karena dorongan buyer habis.
      </div>
      <div style="background: #f5f3ff; border: 1px solid #ddd6fe; padding: 5px; border-radius: 5px;">
        <strong style="color: #5b21b6;">🚫 CEGAH JUAL DI LEMBAH (Bullish Divergence)</strong><br>
        Jika harga mencetak Lower Low namun RSI mencetak Higher Low di area oversold (&lt;40), sinyal SELL <b>DIBATALKAN</b> demi menghindari pantulan mendadak.
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom: 7px; border-left: 4px solid #059669; padding: 7px;">
    <div style="font-weight: bold; color: #059669; font-size: 8.5pt; margin-bottom: 3px;">⏳ 3. Stagnant Trade Time-Exit / Rollover Shield (Section 2.5)</div>
    <p style="font-size: 7.4pt; margin: 0;">
      Posisi yang telah mengambang lebih dari <b>6 Jam</b> tanpa menyentuh TP dan berada di area profit/impas akan <b>ditutup otomatis</b> demi membebaskan modal serta menghindari swap rollover tengah malam dan pelebaran spread dini hari.
    </p>
  </div>

  <div class="card-success" style="padding: 6px;">
    <h4 style="color: #15803d; margin: 0 0 2px 0; font-size: 7.8pt;">🖥️ Live Monitor di Glassmorphic HUD MT5:</h4>
    <p style="font-size: 7.3pt; margin: 0;">
      Status ditampilkan real-time di chart Anda: <code>[News Shield]: AMAN (STANDBY) | Momentum: NORMAL (SEHAT)</code>.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 9E: SMART SIDEWAYS & ANTI-FAKEOUT SUITE ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8E: Smart Sideways & Anti-Fakeout Suite (v3.00)</div>
    <div class="chapter-badge">Smart Sideways Suite</div>
  </div>

  <h2>Empat Sensor Kuantitatif Anti-Sideways & Anti-Fakeout di Versi 2.70</h2>
  <p style="font-size: 8pt; margin-bottom: 7px;">
    Mencegah robot terjebak dalam pasar mendatar tanpa arah (*choppy compression*), garis EMA yang saling membelit (*EMA tangle*), dan breakout tipuan tanpa volume (*fakeout*):
  </p>

  <div class="card" style="margin-bottom: 6px; border-left: 4px solid #0284c7; padding: 6px;">
    <div style="font-weight: bold; color: #0284c7; font-size: 8.3pt; margin-bottom: 2px;">⚡ 1. ADX Directional Power Threshold (Section 8.9)</div>
    <p style="font-size: 7.4pt; margin: 0;">
      Mengukur tenaga dorong kinetik pasar. Jika <b>ADX(14) &lt; 22.0</b>, pasar berada dalam fase tidur tanpa arah. Seluruh sinyal ditolak sampai ADX &ge; 22.0 yang membuktikan adanya arus tren institusional yang kuat.
    </p>
  </div>

  <div class="card" style="margin-bottom: 6px; border-left: 4px solid #f59e0b; padding: 6px;">
    <div style="font-weight: bold; color: #f59e0b; font-size: 8.3pt; margin-bottom: 2px;">📐 2. EMA Slope & Flatness Angle Filter (Section 8.10)</div>
    <p style="font-size: 7.4pt; margin: 0 0 3px 0;">
      Memvalidasi sudut kemiringan EMA 125 dan EMA 21:
    </p>
    <div class="grid-2" style="font-size: 7.2pt;">
      <div style="background: #f0fdf4; border: 1px solid #bbf7d0; padding: 4px; border-radius: 5px;">
        <strong style="color: #15803d;">📈 SYARAT BUY (Slope &ge; +3 Pips)</strong><br>
        Garis EMA 125 wajib mendaki minimal 3 pips dalam 5 bar terakhir. Menolak BUY saat garis EMA datar!
      </div>
      <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 4px; border-radius: 5px;">
        <strong style="color: #b91c1c;">📉 SYARAT SELL (Slope &le; -3 Pips)</strong><br>
        Garis EMA 125 wajib menukik minimal 3 pips dalam 5 bar terakhir. Menolak SELL saat garis EMA datar!
      </div>
    </div>
  </div>

  <div class="card" style="margin-bottom: 6px; border-left: 4px solid #8b5cf6; padding: 6px;">
    <div style="font-weight: bold; color: #8b5cf6; font-size: 8.3pt; margin-bottom: 2px;">📊 3. Institutional Volume Expansion / VSA (Section 8.11)</div>
    <p style="font-size: 7.4pt; margin: 0;">
      Breakout yang sah wajib didukung lonjakan volume transaksi. Jika lilin konfirmasi memiliki volume di bawah <b>1.15x rata-rata 20 bar</b>, robot menolaknya sebagai sinyal palsu (*Fakeout*).
    </p>
  </div>

  <div class="card" style="margin-bottom: 6px; border-left: 4px solid #10b981; padding: 6px;">
    <div style="font-weight: bold; color: #10b981; font-size: 8.3pt; margin-bottom: 2px;">📏 4. Minimum ATR Volatility Floor (Section 8.12)</div>
    <p style="font-size: 7.4pt; margin: 0;">
      Menjamin pasar emas memiliki range pergerakan yang cukup (<b>ATR &ge; 12.0 pips</b>). Mencegah robot open posisi di pasar mati yang membuat modal tersandera spread.
    </p>
  </div>

  <div class="card-success" style="padding: 5px;">
    <h4 style="color: #15803d; margin: 0 0 2px 0; font-size: 7.8pt;">🖥️ Live Monitor di HUD Chart MT5:</h4>
    <p style="font-size: 7.2pt; margin: 0;">
      Status real-time terpantau di panel: <code>[Anti-Sideways]: ADX: 24.5 | Vol: 132% | Slope Filter: AKTIF</code>.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 10: PANDUAN INSTALASI MT5 ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 9: Panduan Instalasi Langkah-demi-Langkah di MT5</div>
    <div class="chapter-badge">Praktik 5 Menit</div>
  </div>

  <p>
    Memasang robot ini ke dalam MetaTrader 5 sangatlah mudah. Cukup ikuti 5 langkah berikut secara berurutan:
  </p>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 4px 0;"><span class="step-number">1</span> Buka Aplikasi MetaTrader 5 & Periksa Berkas EA</h3>
    <p style="font-size: 8pt; margin: 0;">
      Buka aplikasi <strong>DIDIMAX MT5</strong> di komputer Anda. Berkas EA dan preset sudah disalin secara otomatis oleh sistem kami ke dalam folder MT5 Anda. Untuk memastikannya, tekan tombol <code>Ctrl + N</code> untuk membuka jendela <strong>Navigator</strong> di sebelah kiri. Di bawah bagian <strong>Expert Advisors</strong>, Anda akan melihat folder <strong>VIKAR_4Pillar_Pro</strong>.
    </p>
  </div>

  <div class="card-danger">
    <h3 style="color: #be123c; margin: 0 0 4px 0;"><span class="step-number">2</span> WAJIB: Aktifkan Tombol "Algo Trading" Terminal</h3>
    <p style="font-size: 8pt; margin: 0 0 4px 0;">
      Jika langkah ini dilewati, robot tidak akan bisa bertransaksi!
    </p>
    <ul style="margin: 0; padding-left: 18px; font-size: 7.8pt;">
      <li>Di menu bar paling atas aplikasi MT5, klik <strong>Tools</strong> &rarr; pilih <strong>Options</strong> (atau tekan shortcut <code>Ctrl + O</code>).</li>
      <li>Klik tab <strong>Expert Advisors</strong> &rarr; centang kotak: <strong>"Allow Algo Trading"</strong> dan <strong>"Allow DLL imports"</strong> &rarr; klik <strong>OK</strong>.</li>
      <li>Periksa tombol besar bertuliskan <strong>"Algo Trading"</strong> di toolbar atas: pastikan warnanya <strong>HIJAU</strong> (bukan merah).</li>
    </ul>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 4px 0;"><span class="step-number">3</span> Buka Grafik Emas (XAUUSD) & Atur Timeframe ke M5</h3>
    <p style="font-size: 8pt; margin: 0;">
      Buka jendela Market Watch (<code>Ctrl + M</code>) &rarr; klik kanan pada simbol <code>XAUUSD</code> atau <code>GOLD</code> &rarr; pilih <strong>Chart Window</strong>.
      <br>Di menu bar atas, ubah timeframe grafik menjadi <strong>M5</strong> (lilin 5 menit).
    </p>
  </div>

  <div class="card-success">
    <h3 style="color: #15803d; margin: 0 0 4px 0;"><span class="step-number">4</span> Pasang EA & Muat File Preset (.set)</h3>
    <ol style="margin: 0; padding-left: 18px; font-size: 7.8pt;">
      <li>Di jendela Navigator, klik dan tahan (drag & drop) <code>VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR</code> ke tengah chart XAUUSD Anda.</li>
      <li>Jendela pengaturan EA akan muncul. Masuk ke tab <strong>Inputs</strong>.</li>
      <li>Klik tombol <strong>Load...</strong> di pojok kanan bawah.</li>
      <li>Pilih file preset yang Anda inginkan (misal: <code>XAUUSD_FAST_AUTO_TRADE.set</code>) &rarr; klik <strong>Open</strong>.</li>
      <li>Klik tombol <strong>OK</strong>. Selesai!</li>
    </ol>
  </div>

  <h2>Cara Mengetahui Apakah EA Sudah Berjalan Sempurna?</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Tanda di Layar Chart</th>
        <th style="width: 20%;">Status Kerja</th>
        <th>Penjelasan & Tindakan</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Ikon Topi Berwarna Biru/Hijau</strong><br>(Pojok Kanan Atas Chart)</td>
        <td><span class="badge badge-green">AKTIF SEMPURNA</span></td>
        <td>Robot memiliki izin penuh dan sedang memantau harga secara aktif. Anda tinggal duduk santai!</td>
      </tr>
      <tr>
        <td><strong>Ikon Topi Abu-Abu / Tanda Silang</strong><br>(Pojok Kanan Atas Chart)</td>
        <td><span class="badge badge-red">TIDAK BERJALAN</span></td>
        <td>Tombol Algo Trading belum ditekan, atau centang Allow Algo Trading di tab Common belum aktif.</td>
      </tr>
      <tr>
        <td><strong>Muncul Tabel Panel HUD</strong><br>(Pojok Kiri Atas Chart)</td>
        <td><span class="badge badge-blue">MONITOR AKTIF</span></td>
        <td>Panel informasi 4 pilar menampilkan analisis tren, pivot harian, dan statistik PnL Anda.</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ==================== HALAMAN 11: KATALOG 4 PRESET RESMI ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 10: Katalog 4 Preset Resmi (.set) & Panduan Memilih</div>
    <div class="chapter-badge">Presets Library</div>
  </div>

  <p>
    Anda tidak perlu menyetel puluhan parameter secara manual! Kami telah menyediakan <strong>4 file konfigurasi preset resmi (.set)</strong> yang siap dipakai sesuai tujuan Anda:
  </p>

  <div class="card-highlight">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
      <h3 style="margin: 0; color: #0369a1;">1. XAUUSD_FAST_AUTO_TRADE.set (Pilihan Terpopuler: Cepat & Aktif)</h3>
      <span class="badge badge-blue">TF: M5 | Magic: 777101</span>
    </div>
    <p style="font-size: 7.8pt; margin: 0 0 3px 0;">
      <strong>Untuk trader yang menginginkan transaksi lebih aktif dan tidak sabar menunggu lama.</strong> Menggunakan ambang konfluensi fleksibel (60 poin) dan penguncian modal sangat cepat di +8 pips.
    </p>
    <div class="grid-3" style="font-size: 7.3pt; margin: 0; background: #ffffff; padding: 4px; border-radius: 4px;">
      <div><strong>Target SL+:</strong> +8 pips (Kunci +2.5p)</div>
      <div><strong>TP1 Partial:</strong> +10 pips (50% lot)</div>
      <div><strong>Double Align:</strong> Fleksibel</div>
      <div><strong>Minimal Skor:</strong> 60 Poin</div>
      <div><strong>Target R:R:</strong> 1 : 1.5</div>
      <div><strong>Rekomendasi Saldo:</strong> $1.000 - $3.000</div>
    </div>
  </div>

  <div class="card-success">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
      <h3 style="margin: 0; color: #15803d;">2. XAUUSD_HIGH_WINRATE_SNIPER.set (Ultra Winrate Grade A+)</h3>
      <span class="badge badge-green">TF: M5 | Magic: 777108</span>
    </div>
    <p style="font-size: 7.8pt; margin: 0 0 3px 0;">
      <strong>Preset terbaik untuk pemula yang ingin ketahanan modal maksimal.</strong> Sangat selektif, hanya menembak saat setup benar-benar sempurna bintang lima (Grade A+).
    </p>
    <div class="grid-3" style="font-size: 7.3pt; margin: 0; background: #ffffff; padding: 4px; border-radius: 4px;">
      <div><strong>Minimal Skor:</strong> 80 Poin (Sniper)</div>
      <div><strong>Double Align:</strong> Wajib Terpenuhi</div>
      <div><strong>Fibo Pocket:</strong> Wajib Uji 61.8%</div>
      <div><strong>Target SL+:</strong> +8 pips (Kunci +3.0p)</div>
      <div><strong>TP1 Partial:</strong> +12 pips (50% lot)</div>
      <div><strong>Rekomendasi Saldo:</strong> $1.000 - $5.000</div>
    </div>
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
      <h3 style="margin: 0; color: #1e293b;">3. XAUUSD_M5_Scalping_Confluence.set (Scalping Seimbang)</h3>
      <span class="badge badge-purple">TF: M5 | Magic: 777105</span>
    </div>
    <p style="font-size: 7.8pt; margin: 0 0 3px 0;">
      Keseimbangan ideal antara frekuensi transaksi harian dan rasio kemenangan pada timeframe M5 dengan filter konfirmasi Higher Timeframe H1 aktif.
    </p>
    <div class="grid-3" style="font-size: 7.3pt; margin: 0; background: #ffffff; padding: 4px; border-radius: 4px;">
      <div><strong>Minimal Skor:</strong> 65 Poin (Grade A)</div>
      <div><strong>Target SL+:</strong> +12 pips (Kunci +4.0p)</div>
      <div><strong>TP1 Partial:</strong> +15 pips</div>
      <div><strong>Target R:R:</strong> 1 : 1.8</div>
      <div><strong>Filter HTF H1:</strong> Aktif</div>
      <div><strong>Rekomendasi Saldo:</strong> $2.500 - $5.000</div>
    </div>
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
      <h3 style="margin: 0; color: #1e293b;">4. XAUUSD_M15_DayTrading_GradeA.set (Trend Rider M15)</h3>
      <span class="badge badge-gold">TF: M15 | Magic: 777115</span>
    </div>
    <p style="font-size: 7.8pt; margin: 0 0 3px 0;">
      Khusus gaya Day Trading pada grafik M15 yang memburu pergerakan tren besar dengan target ratusan pips dan jarak Stop Loss lebih leluasa.
    </p>
    <div class="grid-3" style="font-size: 7.3pt; margin: 0; background: #ffffff; padding: 4px; border-radius: 4px;">
      <div><strong>Minimal Skor:</strong> 70 Poin</div>
      <div><strong>Target SL+:</strong> +20 pips (Kunci +6.0p)</div>
      <div><strong>TP1 Partial:</strong> +25 pips</div>
      <div><strong>Target R:R:</strong> 1 : 2.5 (Rasio Lebar)</div>
      <div><strong>Trailing Stop:</strong> EMA 21 Buffer 6p</div>
      <div><strong>Rekomendasi Saldo:</strong> $5.000+</div>
    </div>
  </div>

  <div class="tips-pemula">
    <strong>💡 Rekomendasi Hari Pertama Bagi Pemula:</strong>
    Gunakan <strong>XAUUSD_FAST_AUTO_TRADE.set</strong> di timeframe M5. Anda akan melihat langsung bagaimana robot ini mengunci keuntungan dengan sangat cepat dan gesit!
  </div>
</div>

<!-- ==================== HALAMAN 12: MEMBACA DASHBOARD HUD ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 11: Membaca Layar Monitor (HUD Dashboard) di Chart</div>
    <div class="chapter-badge">Live Monitor</div>
  </div>

  <h2>Memahami Setiap Baris Informasi di Pojok Layar MT5</h2>
  <p>
    Robot dilengkapi papan instrumen cerdas (*Dashboard HUD*) di pojok kiri atas chart yang memberikan transparansi penuh tentang apa yang sedang dipikirkan dan dilakukan oleh algoritma:
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

  <h2>Arti Status-Status yang Sering Muncul di Layar:</h2>
  <table>
    <thead>
      <tr>
        <th style="width: 25%;">Baris Monitor</th>
        <th style="width: 30%;">Teks yang Muncul</th>
        <th>Arti & Kondisi Pasar yang Sedang Terjadi</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Sinyal Terakhir</strong></td>
        <td><code>MENUNGGU SETUP KONFLUENSI</code></td>
        <td>Robot sedang memindai lilin demi lilin, belum ada setup yang lulus syarat kualitas.</td>
      </tr>
      <tr>
        <td><strong>Double Alignment</strong></td>
        <td><code>SUPER BULLISH</code><br><code>SUPER BEARISH</code><br><code>CONFLICT</code></td>
        <td>Jika muncul <code>CONFLICT</code>, harga berada di antara EMA 125 dan Pivot P. Robot sengaja diam karena tren sedang tidak jelas.</td>
      </tr>
      <tr>
        <td><strong>Dealing Range</strong></td>
        <td><code>DISCOUNT ZONE</code> (&lt;50%)<br><code>PREMIUM ZONE</code> (&gt;50%)</td>
        <td>Menunjukkan apakah harga sekarang tergolong murah atau mahal. BUY hanya diizinkan di Discount Zone.</td>
      </tr>
      <tr>
        <td><strong>Konfluensi Setup</strong></td>
        <td><code>GRADE A+ SNIPER</code> (&ge;80)<br><code>GRADE A HIGH PROB</code> (&ge;65)</td>
        <td>Menampilkan rapor skor gabungan. Memastikan transaksi hanya diambil saat kondisi pasar sangat matang.</td>
      </tr>
      <tr>
        <td><strong>Riwayat Transaksi</strong></td>
        <td><code>Win Rate: 85.0%</code></td>
        <td>Akurasi kemenangan nyata akun Anda yang dihitung otomatis dari riwayat transaksi tertutup.</td>
      </tr>
    </tbody>
  </table>

  <h2>Pesan Peringatan Khusus di Baris Sinyal Terakhir:</h2>
  <div class="grid-2">
    <div class="card-warning">
      <h3><code>FILTER: WHIPSAW DI EMA 125</code></h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Harga sedang bolak-balik menembus garis putih EMA 125. Pasar sedang bergerak tanpa arah (sideways). Robot menolak entri sampai arah tren jelas kembali.
      </p>
    </div>
    <div class="card-warning">
      <h3><code>SHOCK GUARD: JEDA VOLATILITAS</code></h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Baru saja terjadi lonjakan candle tajam pasca berita. Robot mengunci entri selama 2 lilin untuk memastikan pergerakan bukan perangkap bandar.
      </p>
    </div>
  </div>
</div>

<!-- ==================== HALAMAN 13: TROUBLESHOOTING & FAQ ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 12: Tanya Jawab Masalah Umum (Troubleshooting)</div>
    <div class="chapter-badge">Solusi Cepat</div>
  </div>

  <h2>Pertanyaan yang Paling Sering Diajukan Pemula (FAQ):</h2>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 2px 0;">Q1: Kenapa robot belum membuka posisi sama sekali selama 3 jam?</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      <strong>Jawaban:</strong> Jangan khawatir, ini adalah tanda bahwa robot bekerja dengan SANGAT BAIK! Robot ini bukan mesin judi yang membuka posisi setiap menit. Robot hanya menembak jika syarat 4 Pilar terpenuhi. Saat pasar sideways atau berisiko, robot dengan sengaja diam untuk melindungi uang Anda dari kerugian yang tidak perlu.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 2px 0;">Q2: Apakah komputer / laptop saya harus menyala terus 24 jam?</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      <strong>Jawaban:</strong> Agar robot dapat memantau pasar tanpa terputus, komputer dan internet harus aktif. 
      <br><strong>Solusi Terbaik:</strong> Sewalah sebuah <strong>VPS (Virtual Private Server) Windows</strong> (sekitar Rp 70.000 - Rp 150.000/bulan). Anda bisa memasang MT5 di VPS tersebut sehingga robot tetap bekerja 24 jam nonstop meskipun laptop pribadi Anda sudah dimatikan.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 2px 0;">Q3: Kenapa muncul pesan error 10014 (TRADE_RETCODE_INVALID_VOLUME)?</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      <strong>Jawaban:</strong> Error ini terjadi jika lot yang diminta lebih kecil dari syarat broker Didimax (0.10 lot). Pada versi <strong>v2.1 Audited</strong>, masalah ini telah <strong>diselesaikan 100%</strong> melalui fitur deteksi otomatis minimal lot broker.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 2px 0;">Q4: Kenapa ikon di pojok chart berwarna abu-abu / bertanda silang?</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      <strong>Solusi:</strong> 
      1. Tekan tombol <strong>"Algo Trading"</strong> di toolbar atas MT5 sampai berwarna hijau.
      <br>2. Klik tombol F7 pada keyboard &rarr; di tab <strong>Common</strong>, pastikan kotak <strong>"Allow Algo Trading"</strong> sudah tercentang.
    </p>
  </div>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 2px 0;">Q5: Bolehkah saya menutup posisi secara manual di HP?</h3>
    <p style="font-size: 7.8pt; margin: 0;">
      <strong>Jawaban:</strong> Boleh, tetapi <strong>sangat tidak disarankan dilakukan secara acak</strong>. Biarkan robot bekerja mengunci SL+, menutup 50% di TP1, atau memotong dini saat ada pembalikan arah sesuai algoritma yang telah teruji.
    </p>
  </div>

  <div class="card-warning">
    <h3 style="color: #b45309; margin: 0 0 2px 0;">Peringatan Penting (Disclaimer Resiko Finansial):</h3>
    <p style="margin: 0; font-size: 7.2pt; text-align: justify;">
      Trading komoditas emas (XAU/USD) memiliki potensi keuntungan yang besar namun juga melibatkan risiko finansial akibat sistem leverage. Selalu gunakan modal dingin yang siap Anda risikokan (*risk capital*), patuhi aturan manajemen lot pada Bab 8, dan biasakan melakukan simulasi di akun demo terlebih dahulu sebelum beralih ke akun riil.
    </p>
  </div>
</div>

<!-- ==================== HALAMAN 14: SOP CHECKLIST & MINDSET ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 13: Lembar SOP Checklist Harian & Mindset Juara</div>
    <div class="chapter-badge">SOP Harian</div>
  </div>

  <p>
    Gunakan atau cetak lembar checklist harian ini untuk memastikan seluruh sistem siap bekerja sebelum Anda memulai aktivitas harian:
  </p>

  <div class="card">
    <h3 style="color: #0369a1; margin: 0 0 4px 0;">📋 Lembar Checklist Persiapan Harian (Pukul 06:30 WIB):</h3>
    <table>
      <thead>
        <tr>
          <th style="width: 8%; text-align: center;">Centang</th>
          <th style="width: 32%;">Langkah Pemeriksaan</th>
          <th>Kondisi Ideal yang Harus Terpenuhi</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Koneksi Internet / VPS</td>
          <td>Status koneksi di pojok kanan bawah MT5 berwarna hijau-biru (sinyal stabil &lt; 50ms).</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Tombol Algo Trading</td>
          <td>Tombol Algo Trading di toolbar berwarna HIJAU, ikon EA bertopi biru di pojok kanan chart.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Simbol & Timeframe</td>
          <td>Grafik instrumen XAUUSD berada di timeframe <strong>M5</strong> (atau M15 sesuai strategi).</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>File Preset (.set)</td>
          <td>Preset <code>XAUUSD_FAST_AUTO_TRADE.set</code> atau <code>SNIPER</code> sudah dimuat di tab Inputs.</td>
        </tr>
        <tr>
          <td style="text-align: center;">[ &nbsp; ]</td>
          <td>Ukuran Lot Didimax</td>
          <td>Parameter Lot diatur <code>LOT_TYPE_BROKER_MIN</code> (otomatis aman di 0.10 lot Didimax).</td>
        </tr>
      </tbody>
    </table>
  </div>

  <h2>5 Rukun Emas Mindset Trader Profesional (Wajib Diresapi Pemula):</h2>
  <div class="grid-2">
    <div class="card-highlight">
      <h3>1. Sabar Menunggu Setup Berkualitas</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Singa tidak berburu setiap detik; singa menunggu mangsa yang tepat sebelum menerkam. Jangan memaksa robot trading jika kondisi pasar memang sedang jelek.
      </p>
    </div>
    <div class="card-highlight">
      <h3>2. Percaya pada Hukum Probabilitas</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Jangan panik jika mengalami 1 kali kerugian. Tidak ada strategi yang menang 100%. Dengan rasio kemenangan 80%, dalam 10 transaksi Anda menang 8 kali dan hanya kalah 2 kali!
      </p>
    </div>
  </div>

  <div class="grid-2">
    <div class="card-highlight">
      <h3>3. Jangan Mengubah Lot Sembarangan</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Keserakahan adalah musuh nomor satu. Tetap gunakan lot 0.10 sampai modal Anda benar-benar bertumbuh berlipat ganda secara konsisten.
      </p>
    </div>
    <div class="card-highlight">
      <h3>4. Nikmati Proses Menabung Profit</h3>
      <p style="font-size: 7.8pt; margin: 0;">
        Keuntungan $10 s/d $30 per hari jika dikumpulkan konsisten selama 20 hari trading sebulan akan menjadi hasil yang sangat luar biasa bagi keluarga Anda.
      </p>
    </div>
  </div>

  <div class="card-success" style="text-align: center; padding: 12px; margin-top: 8px;">
    <h3 style="color: #15803d; margin: 0 0 3px 0; font-size: 10pt;">Selamat Bertransaksi Bersama VIKAR EA 4-Pillar Pro!</h3>
    <p style="margin: 0; font-size: 8pt; color: #166534;">
      Disiplin adalah jembatan antara impian Anda dan kenyataan finansial Anda. Biarkan robot bekerja secara matematis, nikmati hari-hari Anda bersama orang-orang tercinta!
    </p>
  </div>
</div>

</body>
</html>
"""

# Replace image placeholders
html_content = html_content.replace("__IMG_SMC_BOS__", img_smc_bos)
html_content = html_content.replace("__IMG_SMC_CHOCH__", img_smc_choch)

temp_html_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\temp_beginner_guide.html"
pdf_dest_proj = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf"
pdf_dest_terminal = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_4Pillar_Pro\PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf"
pdf_dest_artifact = os.path.join(artifact_dir, "PANDUAN_LENGKAP_EA_VIKAR_PRO.pdf")

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
    
    # Check page count
    with open(pdf_dest_proj, "rb") as f:
        pdf_bytes = f.read()
    page_matches = re.findall(b"/Type\\s*/Page[^s]", pdf_bytes)
    print(f"Total Pages in Generated PDF: {len(page_matches)}")

    # Copy to terminal and artifact
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
