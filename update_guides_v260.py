import os
import subprocess

# -------------------------------------------------------------
# 1. Update MT4 Guide: build_mt4_pdf_guide.py
# -------------------------------------------------------------
mt4_guide_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\build_mt4_pdf_guide.py"
with open(mt4_guide_path, "r", encoding="utf-8") as f:
    mt4_code = f.read()

mt4_code = mt4_code.replace("v2.50 APEX QUANTITATIVE INTELLIGENCE", "v2.60 APEX INSTITUTIONAL INTELLIGENCE")
mt4_code = mt4_code.replace("v2.50", "v2.60")

page_5d = """
<!-- HALAMAN 5D: PERISAI PRE-NEWS, SPREAD SPIKE & DIVERGENSI RSI (v2.60) -->
<div class="page">
  <div class="header-bar">
    <h2>5D. Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v2.60)</h2>
    <span class="tag">INSTITUTIONAL SHIELD</span>
  </div>

  <p>Pembaruan <b>v2.60 Apex Institutional Intelligence</b> melengkapi robot dengan 3 lapisan perlindungan ekstra untuk memusnahkan penyebab Stop Loss yang paling sering dialami trader retail:</p>

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
"""

if "HALAMAN 5D:" not in mt4_code:
    mt4_code = mt4_code.replace("<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->", page_5d.strip() + "\n\n<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->")

with open(mt4_guide_path, "w", encoding="utf-8") as f:
    f.write(mt4_code)

print("Updated build_mt4_pdf_guide.py!")

# -------------------------------------------------------------
# 2. Update MT5 Guide: build_beginner_friendly_pdf.py
# -------------------------------------------------------------
mt5_guide_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\build_beginner_friendly_pdf.py"
with open(mt5_guide_path, "r", encoding="utf-8") as f:
    mt5_code = f.read()

mt5_code = mt5_code.replace("v2.50", "v2.60")
mt5_code = mt5_code.replace("Apex Quantitative Intelligence & Self-Healing", "Apex Institutional Intelligence & Self-Healing")

# Update TOC
old_toc_5 = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 10</td><td>Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing Engine)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 11</td><td>Kecerdasan Kuantitatif: Pattern Matrix & Sensor Cuaca (v2.50)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>"""

new_toc_5 = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 10</td><td>Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing Engine)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 11</td><td>Kecerdasan Kuantitatif: Pattern Matrix & Sensor Cuaca (v2.50)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v2.60)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>"""

if old_toc_5 in mt5_code:
    mt5_code = mt5_code.replace(old_toc_5, new_toc_5)

bab_8d = """
<!-- ==================== HALAMAN 9D: PERISAI PRE-NEWS, SPREAD SPIKE & DIVERGENSI RSI ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8D: Perisai Berita AS, Spread Spike & Sensor RSI Divergence (v2.60)</div>
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
"""

target_marker = "<!-- ==================== HALAMAN 10: PANDUAN INSTALASI MT5 ==================== -->"
if "HALAMAN 9D:" not in mt5_code and target_marker in mt5_code:
    mt5_code = mt5_code.replace(target_marker, bab_8d.strip() + "\n\n" + target_marker)

with open(mt5_guide_path, "w", encoding="utf-8") as f:
    f.write(mt5_code)

print("Updated build_beginner_friendly_pdf.py!")
