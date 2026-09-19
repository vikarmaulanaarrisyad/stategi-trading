import os
import subprocess

# -------------------------------------------------------------
# 1. Update MT4 Guide: build_mt4_pdf_guide.py
# -------------------------------------------------------------
mt4_guide_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\build_mt4_pdf_guide.py"
with open(mt4_guide_path, "r", encoding="utf-8") as f:
    mt4_code = f.read()

mt4_code = mt4_code.replace("v2.70 APEX INSTITUTIONAL INTELLIGENCE", "v3.00 APEX GRANDMASTER EDITION")
mt4_code = mt4_code.replace("v2.70", "v3.00")
mt4_code = mt4_code.replace("Apex Edition", "Apex Grandmaster Edition")

page_5f = """
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
"""

if "HALAMAN 5F:" not in mt4_code:
    mt4_code = mt4_code.replace("<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->", page_5f.strip() + "\n\n<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->")

with open(mt4_guide_path, "w", encoding="utf-8") as f:
    f.write(mt4_code)

print("Updated build_mt4_pdf_guide.py with Page 5F!")

# -------------------------------------------------------------
# 2. Update MT5 Guide: build_beginner_friendly_pdf.py
# -------------------------------------------------------------
mt5_guide_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\build_beginner_friendly_pdf.py"
with open(mt5_guide_path, "r", encoding="utf-8") as f:
    mt5_code = f.read()

mt5_code = mt5_code.replace("v2.70", "v3.00")
mt5_code = mt5_code.replace("Apex Institutional Intelligence v2.70 (Smart Sideways & Anti-Fakeout)", "Apex Grandmaster Edition v3.00 (Prop Firm & Trap Hunter)")

# Update TOC
old_toc_mt5 = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Smart Sideways & Anti-Fakeout Suite: ADX, Slope & VSA (v2.70)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 14</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>"""

new_toc_mt5 = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Smart Sideways & Anti-Fakeout Suite: ADX, Slope & VSA (v2.70)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 14</td><td>Apex Grandmaster Suite: Prop Firm Guard, Kelly Scaling & Trap Hunter (v3.00)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 15</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>"""

if old_toc_mt5 in mt5_code:
    mt5_code = mt5_code.replace(old_toc_mt5, new_toc_mt5)

bab_9f = """
<!-- ==================== HALAMAN 9F: APEX GRANDMASTER SUITE (v3.00) ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-tag">BAB IX-F • GRANDMASTER SUITE (v3.00)</div>
    <h2>Prop Firm Equity Guardian, Kelly Risk Allocator & Trap Hunter</h2>
    <div class="chapter-desc">4 Fitur Puncak Standar Institusi untuk Ketahanan Akun Prop Firm & Profit Maksimal</div>
  </div>

  <div class="card" style="margin-bottom:12px; border-left:4px solid #ef4444;">
    <div class="card-header" style="color:#ef4444;">🛡️ 1. Prop Firm Equity Guardian & Hard DD Kill-Switch (Section 8.13)</div>
    <p style="font-size:8.3pt; margin:0 0 4px 0;">
      Menjaga akun Anda agar <b>100% aman dari diskualifikasi Prop Firm</b> (FTMO, MFF, TheFundedTrader). Sistem mencatat saldo awal modal setiap pukul 00:00 (Midnight Balance). Jika penurunan equity intraday mencapai <b>4.0%</b> (di bawah batas 5%), seluruh posisi langsung ditutup darurat dan trading dibekukan hingga 00:00 server.
    </p>
  </div>

  <div class="card" style="margin-bottom:12px; border-left:4px solid #06b6d4;">
    <div class="card-header" style="color:#06b6d4;">📈 2. Dynamic Structural Swing Trailing (Section 2.6)</div>
    <p style="font-size:8.3pt; margin:0 0 4px 0;">
      Menggeser Stop Loss secara otomatis di balik benteng Higher Low (BUY) atau Lower High (SELL) terbaru begitu posisi sudah mengunci keuntungan &ge; InpBreakevenLockPips. Memberikan ruang nafas ideal tanpa khawatir tersentuh noise acak pips!
    </p>
  </div>

  <div class="card" style="margin-bottom:12px; border-left:4px solid #8b5cf6;">
    <div class="card-header" style="color:#8b5cf6;">⚖️ 3. Asymmetric Confidence Risk Allocator (Kelly Scaling v3.00)</div>
    <p style="font-size:8.3pt; margin:0 0 4px 0;">
      Peluang emas dengan konfluensi 4 pilar lengkap (Grade A+, Skor &ge; 85) diberikan bobot <b>1.30x lot</b> untuk melipatgandakan return secara terukur. Sebaliknya, setup standar dialokasikan <b>0.70x lot</b>.
    </p>
  </div>

  <div class="card" style="margin-bottom:12px; border-left:4px solid #f59e0b;">
    <div class="card-header" style="color:#f59e0b;">🎯 4. Liquidity Sweep Trap Hunter (Turtle Soup Reversal Engine)</div>
    <p style="font-size:8.3pt; margin:0 0 4px 0;">
      Ketika institusi menyapu stop loss retail di atas puncak ayunan (BSL) atau di bawah lembah ayunan (SSL) sejauh 4-30 pips lalu harga langsung ditarik kembali membentuk ekor panjang (&ge; 40%), EA mengeksekusi pembalikan arah dengan probabilitas keberhasilan sangat tinggi!
    </p>
  </div>

  <div class="alert-box success">
    <strong>📊 Terpantau Real-Time pada HUD Chart:</strong><br>
    Baris monitor: <code>[Prop Firm Guard]: DD: 0.0% / Max 4.0% | Trap Hunter: AKTIF</code>.
  </div>
</div>
"""

if "HALAMAN 9F:" not in mt5_code:
    mt5_code = mt5_code.replace("<!-- ==================== HALAMAN 10: PANDUAN INSTALASI METATRADER 5 ==================== -->", bab_9f.strip() + "\n\n<!-- ==================== HALAMAN 10: PANDUAN INSTALASI METATRADER 5 ==================== -->")

with open(mt5_guide_path, "w", encoding="utf-8") as f:
    f.write(mt5_code)

print("Updated build_beginner_friendly_pdf.py with Chapter 9F!")
