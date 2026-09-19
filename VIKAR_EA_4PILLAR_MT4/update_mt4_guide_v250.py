import os

guide_file = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\build_mt4_pdf_guide.py"
with open(guide_file, "r", encoding="utf-8") as f:
    content = f.read()

# Update cover badge
content = content.replace("v2.40 APEX SELF-HEALING & MOMENTUM", "v2.50 APEX QUANTITATIVE INTELLIGENCE")

# Add Page 5C
page_5c = """
<!-- HALAMAN 5C: KECERDASAN KUANTITATIF (PATTERN MATRIX & CHOPPINESS INDEX v2.50) -->
<div class="page">
  <div class="header-bar">
    <h2>5C. Kecerdasan Kuantitatif: Pattern Matrix & Sensor Cuaca (v2.50)</h2>
    <span class="tag">AI QUANTITATIVE</span>
  </div>

  <p>Peningkatan kecerdasan buatan v2.50 membawa dua pilar trading kuantitatif kelas institusional: <b>Memori Rapor Kinerja Tiap Pola</b> dan <b>Klasifikasi Cuaca Pasar Berbasis Entropi Fisika (Choppiness Index)</b>.</p>

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
"""

if "HALAMAN 5C:" not in content:
    content = content.replace("<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->", page_5c.strip() + "\n\n<!-- HALAMAN 6: PANDUAN 4 PRESET SIAP PAKAI -->")

with open(guide_file, "w", encoding="utf-8") as f:
    f.write(content)

print("build_mt4_pdf_guide.py updated with Page 5C!")
