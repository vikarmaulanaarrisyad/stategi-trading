import os

guide_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\build_beginner_friendly_pdf.py"
with open(guide_file, "r", encoding="utf-8") as f:
    content = f.read()

# Update version strings
content = content.replace("v2.40", "v2.50")
content = content.replace("Apex Self-Healing & Momentum", "Apex Quantitative Intelligence & Self-Healing")

# Update table of contents
old_toc = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 10</td><td>Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing Engine v2.40)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 11</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Katalog 4 Preset Resmi (.set) & Cara Memilih Sesuai Modal</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Cara Membaca Layar Monitor (HUD Dashboard) di Chart</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 14</td><td>Tanya Jawab Masalah Umum (Troubleshooting & Solusi Error)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 15</td><td>Lembar Checklist SOP Harian & 5 Rukun Disiplin Trader</td></tr>"""

new_toc = """        <tr><td style="font-weight: bold; color: #0284c7;">Hal 10</td><td>Mesin Otopsi & Koreksi Diri Pasca-SL (Self-Healing Engine)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 11</td><td>Kecerdasan Kuantitatif: Pattern Matrix & Sensor Cuaca (v2.50)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 12</td><td>Panduan Instalasi Bergambar di MetaTrader 5 (Didimax MT5)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 13</td><td>Katalog 4 Preset Resmi (.set) & Cara Memilih Sesuai Modal</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 14</td><td>Cara Membaca Layar Monitor (HUD Dashboard) di Chart</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 15</td><td>Tanya Jawab Masalah Umum (Troubleshooting & Solusi Error)</td></tr>
        <tr><td style="font-weight: bold; color: #0284c7;">Hal 16</td><td>Lembar Checklist SOP Harian & 5 Rukun Disiplin Trader</td></tr>"""

if old_toc in content:
    content = content.replace(old_toc, new_toc)

# Add Bab 8C page
bab_8c = """
<!-- ==================== HALAMAN 9C: KECERDASAN KUANTITATIF (PATTERN MATRIX & SENSOR CUACA) ==================== -->
<div class="page">
  <div class="chapter-header">
    <div class="chapter-title">Bab 8C: Kecerdasan Kuantitatif v2.50 (Pattern Matrix & Sensor Cuaca)</div>
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
"""

target_marker = "<!-- ==================== HALAMAN 10: PANDUAN INSTALASI MT5 ==================== -->"
if "HALAMAN 9C:" not in content and target_marker in content:
    content = content.replace(target_marker, bab_8c.strip() + "\n\n" + target_marker)

with open(guide_file, "w", encoding="utf-8") as f:
    f.write(content)

print("build_beginner_friendly_pdf.py updated with Bab 8C!")
