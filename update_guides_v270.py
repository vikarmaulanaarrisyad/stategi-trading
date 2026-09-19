import os

# -------------------------------------------------------------
# 1. Update MT4 Guide: build_mt4_pdf_guide.py
# -------------------------------------------------------------
mt4_guide_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\build_mt4_pdf_guide.py"
with open(mt4_guide_path, "r", encoding="utf-8") as f:
    mt4_code = f.read()

mt4_code = mt4_code.replace("v2.60 APEX INSTITUTIONAL INTELLIGENCE", "v2.70 APEX INSTITUTIONAL INTELLIGENCE")
mt4_code = mt4_code.replace("v2.60", "v2.70")

page_5e = """
<!-- HALAMAN 5E: SMART SIDEWAYS & ANTI-FAKEOUT SUITE (v2.70) -->
<div class="page">
  <div class="header-bar">
    <h2>5E. Smart Sideways & Anti-Fakeout Suite (v2.70)</h2>
    <span class="tag">SMART SIDEWAYS SUITE</span>
  </div>

  <p>Pembaruan <b>v2.70 Apex Institutional Intelligence</b> menghadirkan 4 sensor kuantitatif baru untuk membasmi kerugian saat pasar sideways, kompresi sempit, atau breakout palsu (*fakeout*):</p>

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
"""

if "HALAMAN 5E:" not in mt4_code:
    mt4_code = mt4_code.replace("<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->", page_5e.strip() + "\n\n<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->")

with open(mt4_guide_path, "w", encoding="utf-8") as f:
    f.write(mt4_code)

print("Updated build_mt4_pdf_guide.py with Page 5E!")

# -------------------------------------------------------------
# 2. Update MT5 Guide: build_beginner_friendly_pdf.py
# -------------------------------------------------------------
mt5_guide_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\build_beginner_friendly_pdf.py"
with open(mt5_guide_path, "r", encoding="utf-8") as f:
    mt5_code = f.read()

mt5_code = mt5_code.replace("v2.60", "v2.70")
mt5_code = mt5_code.replace("Apex Institutional Intelligence & Self-Healing", "Apex Institutional Intelligence v2.70 (Smart Sideways & Anti-Fakeout)")

# Update TOC
old_toc_mt5 = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v2.60)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>"""

new_toc_mt5 = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v2.60)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Smart Sideways & Anti-Fakeout Suite: ADX, Slope & VSA (v2.70)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 14</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>"""

if old_toc_mt5 in mt5_code:
    mt5_code = mt5_code.replace(old_toc_mt5, new_toc_mt5)

bab_8e = """
<!-- ==================== HALAMAN 9E: SMART SIDEWAYS & ANTI-FAKEOUT SUITE ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8E: Smart Sideways & Anti-Fakeout Suite (v2.70)</div>
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
"""

target_marker = "<!-- ==================== HALAMAN 10: PANDUAN INSTALASI MT5 ==================== -->"
if "HALAMAN 9E:" not in mt5_code and target_marker in mt5_code:
    mt5_code = mt5_code.replace(target_marker, bab_8e.strip() + "\n\n" + target_marker)

with open(mt5_guide_path, "w", encoding="utf-8") as f:
    f.write(mt5_code)

print("Updated build_beginner_friendly_pdf.py with Bab 8E!")
