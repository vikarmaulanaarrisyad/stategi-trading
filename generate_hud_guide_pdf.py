import os
import re
import sys
import base64
import shutil
import subprocess
from datetime import datetime

def main():
    print("=" * 95)
    print("MEMULAI GENERASI DOKUMEN PDF: PANDUAN LENGKAP DASHBOARD HUD EA MT4")
    print("=" * 95)

    # Load screenshot image and encode to base64
    src_img = r"C:\Users\vikar\.gemini\antigravity-ide\brain\299352ef-4615-48c5-a529-06d94f4d54c1\.user_uploaded\media_1789992864448.png"
    img_b64 = ""
    if os.path.exists(src_img):
        with open(src_img, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        print(f"[+] Berhasil memuat tangkapan layar HUD user ({len(img_b64):,} karakter base64).")
    else:
        print("[-] File gambar tangkapan layar tidak ditemukan.")

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Panduan Lengkap Dashboard HUD EA VIKAR 4-Pillar Pro MT4</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 10mm 14mm;
    }}
    body {{
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        margin: 0;
        padding: 0;
        font-size: 11px;
        line-height: 1.45;
    }}
    .page-break {{
        page-break-before: always;
    }}
    .header-box {{
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
    }}
    .header-title {{
        font-size: 17px;
        font-weight: 800;
        color: #f8fafc;
        margin: 0 0 2px 0;
    }}
    .header-sub {{
        font-size: 11px;
        color: #38bdf8;
        font-weight: 600;
    }}
    .section-title {{
        font-size: 12.5px;
        font-weight: 700;
        color: #0f172a;
        margin: 12px 0 6px 0;
        padding-left: 8px;
        border-left: 3.5px solid #0284c7;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .img-card {{
        background: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
    }}
    .img-card img {{
        max-height: 220px;
        border-radius: 4px;
        border: 1px solid #475569;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 10px;
        margin-bottom: 8px;
    }}
    th {{
        background: #f1f5f9;
        color: #1e293b;
        font-weight: 700;
        padding: 5px 8px;
        border: 1px solid #e2e8f0;
        text-align: left;
    }}
    td {{
        padding: 4.5px 8px;
        border: 1px solid #e2e8f0;
        color: #334155;
    }}
    .code-term {{
        font-family: 'Consolas', 'Courier New', monospace;
        font-weight: 700;
        color: #0369a1;
        background: #f0f9ff;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 10px;
    }}
    .highlight-box {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
        font-size: 10.5px;
    }}
    .alert-box {{
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        color: #991b1b;
        margin-bottom: 10px;
        font-size: 10.5px;
    }}
    .success-box {{
        background: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 8px 12px;
        border-radius: 0 6px 6px 0;
        color: #14532d;
        margin-bottom: 10px;
        font-size: 10.5px;
    }}
    .footer {{
        margin-top: 12px;
        border-top: 1px solid #e2e8f0;
        padding-top: 6px;
        font-size: 9px;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
    }}
</style>
</head>
<body>

<!-- HALAMAN 1 -->
<div class="header-box">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 class="header-title">BEDAH LENGKAP DASHBOARD HUD MT4</h1>
            <div class="header-sub">Panduan Membaca Panel Informasi Real-Time VIKAR EA 4-Pillar Pro (QuickPro MT4)</div>
        </div>
        <div style="background:#0284c7; color:#ffffff; font-size:10.5px; font-weight:700; padding:4px 10px; border-radius:6px; text-transform:uppercase;">
            Dokumen Edukasi Trader
        </div>
    </div>
</div>

<div style="display:grid; grid-template-columns: 240px 1fr; gap:16px; margin-bottom:14px;">
    <div class="img-card">
        <div style="font-size:10.5px; font-weight:700; color:#38bdf8; margin-bottom:8px;">TAMPILAN HUD PADA CHART ANDA</div>
        <img src="data:image/png;base64,{img_b64}" alt="Tangkapan Layar Dashboard HUD MT4" />
        <div style="font-size:9.5px; color:#94a3b8; margin-top:6px;">Aktif pada XAUUSD.i M5 QuickPro</div>
    </div>
    <div>
        <div class="section-title" style="margin-top:0;">Apa itu Dashboard HUD?</div>
        <p style="margin-top:0; color:#475569; font-size:11px; line-height:1.55;">
            <strong>Heads-Up Display (HUD)</strong> adalah panel instrumen cerdas transparan yang digambar langsung di atas chart MetaTrader 4 Anda. Fungsinya memberikan informasi <strong>transparan 100%</strong> mengenai kondisi keuangan akun, kalkulasi 4 pilar teknikal (SMC, EMA, Fibo, Pivot), status proteksi AI, serta alasan mengapa robot sedang membuka atau menahan transaksi.
        </p>
        
        <div class="success-box">
            <strong>Keunggulan Desain HUD:</strong><br/>
            Dilengkapi tombol interaktif <code>[ :: GESER ]</code> di pojok kanan atas banner. Anda dapat menekan dan menggeser (<em>drag &amp; drop</em>) seluruh panel ke posisi mana saja di chart yang Anda sukai tanpa menghalangi candlestick.
        </div>

        <div class="section-title">1. Bagian Banner Header &amp; Identitas Operasional</div>
        <table>
            <thead>
                <tr>
                    <th style="width:38%;">Teks di Layar</th>
                    <th>Penjelasan &amp; Makna Fungsional</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span class="code-term">VIKAR 4-PILLAR PRO</span></td>
                    <td>Nama program EA resmi yang terpasang dan beroperasi di akun MT4 Anda.</td>
                </tr>
                <tr>
                    <td><span class="code-term">XAUUSD.i [5M]</span></td>
                    <td>Instrumen Emas (Gold) di broker QuickPro yang sedang dianalisis pada timeframe <strong>M5 (5 Menit)</strong>.</td>
                </tr>
                <tr>
                    <td><span class="code-term">Lot: 0.01</span></td>
                    <td>Ukuran lot tetap yang digunakan untuk setiap posisi (aman untuk modal $20).</td>
                </tr>
                <tr>
                    <td><span class="code-term">ID: 777104</span></td>
                    <td><strong>Magic Number Unik</strong> EA MT4 untuk membedakan transaksi robot dari transaksi manual.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<div class="section-title">2. Baris Informasi Keuangan &amp; Akun Real-Time</div>
<table>
    <thead>
        <tr>
            <th style="width:30%;">Elemen Layar</th>
            <th style="width:25%;">Nilai Pada Screenshot</th>
            <th>Maksud &amp; Perhitungan Finansial</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><span class="code-term">Start Modal &amp; Aktivasi</span></td>
            <td><strong>$16.41</strong> (Aktivasi: 09:18)</td>
            <td>Saldo awal akun saat EA pertama kali diaktifkan pada chart hari ini pukul 09:18 WIB.</td>
        </tr>
        <tr>
            <td><span class="code-term">Saldo | Equity</span></td>
            <td><strong>$20.00</strong> | <strong>$20.00</strong></td>
            <td><strong>Saldo</strong>: Total dana riil setelah semua order closed. <strong>Equity</strong>: Nilai riil akun saat ini (Saldo + Floating PnL).</td>
        </tr>
        <tr>
            <td><span class="code-term">Floating &amp; Jumlah Posisi</span></td>
            <td><strong>$0.00</strong> (0 Posisi)</td>
            <td>Profit/loss transaksi yang sedang berjalan. Angka <strong>0 Posisi</strong> berarti EA sedang menunggu setup terbaik (maks 1 posisi aktif).</td>
        </tr>
        <tr>
            <td><span class="code-term">Spread Real-Time</span></td>
            <td><strong>3.4 pips</strong> (34 points)</td>
            <td>Selisih harga jual (Bid) &amp; beli (Ask) di broker QuickPro. EA memonitor ini agar tidak entry saat spread melebar.</td>
        </tr>
    </tbody>
</table>

<div class="section-title">3. Kotak Rekapitulasi Profit &amp; Loss Real-Time</div>
<table>
    <thead>
        <tr>
            <th style="width:25%;">Baris Rekap</th>
            <th style="width:25%;">Nilai Pada Layar</th>
            <th>Artinya</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><span class="code-term">• Sejak Start</span></td>
            <td><strong>$0.00 (+21.9%) | 0W/0L</strong></td>
            <td>Modal akun Anda telah bertumbuh <strong>+21.9%</strong> dari titik awal $16.41 menjadi $20.00. <strong>0W/0L</strong> menandakan belum ada transaksi yang ditutup sejak jam aktivasi 09:18.</td>
        </tr>
        <tr>
            <td><span class="code-term">• Hari Ini</span></td>
            <td><strong>Net $0.00 (+$0.00 / -$0.00)</strong></td>
            <td>Akumulasi keuntungan bersih hari ini, dipecah menjadi perolehan profit dan kerugian.</td>
        </tr>
        <tr>
            <td><span class="code-term">• Minggu Ini</span></td>
            <td><strong>Net $0.00 (Profit / Loss)</strong></td>
            <td>Total laba bersih yang dibukukan selama minggu berjalan (Senin s/d Jumat).</td>
        </tr>
    </tbody>
</table>

<div class="footer">
    <div>Panduan Resmi Dashboard HUD • VIKAR EA 4-Pillar Pro MT4</div>
    <div>Dicetak pada: {datetime.now().strftime('%d %B %Y %H:%M')} • Halaman 1 dari 3</div>
</div>

<div class="page-break"></div>

<!-- HALAMAN 2 -->
<div class="section-title">4. Bedah Pilar Analisis Teknikal &amp; Sinyal Pasar</div>
<p style="color:#64748b; margin-top:2px;">Bagian ini membeberkan cara kerja 4 pilar institusional EA dalam membaca struktur pergerakan harga Emas M5:</p>

<table>
    <thead>
        <tr>
            <th style="width:26%;">Indikator di HUD</th>
            <th style="width:30%;">Kondisi Pada Tangkapan Layar</th>
            <th>Penjelasan Logika Trading &amp; Aksi Robot</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><span class="code-term">[Confluence]</span></td>
            <td><strong style="color:#10b981;">Ready</strong></td>
            <td>Semua indikator siap dan kalkulasi multi-konfluensi aktif bekerja.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Order Block]</span></td>
            <td><strong>FVG: 4362.3 - 4364.8</strong></td>
            <td><strong>Fair Value Gap (FVG)</strong> terdeteksi di range $4.362,3 s/d $4.364,8. Ini adalah zona ketidakseimbangan harga yang menjadi target re-test institusi.</td>
        </tr>
        <tr>
            <td><span class="code-term">[SMC Struktur]</span></td>
            <td><strong style="color:#0284c7;">BULLISH BOS [BOS]</strong></td>
            <td><strong>Break of Structure (BOS)</strong> ke arah atas. Struktur pasar sedang berada dalam fase kelanjutan tren naik (<em>Bullish Continuation</em>).</td>
        </tr>
        <tr>
            <td><span class="code-term">[Macro H1]</span></td>
            <td><strong style="color:#f59e0b;">NEUTRAL / CONFLICT</strong></td>
            <td>Tren Timeframe Besar (H1) sedang tidak selaras atau berkonsolidasi. EA otomatis menyaring sinyal agar tidak gegabah entry melawan arus besar.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Dealing Range]</span></td>
            <td><strong>PREMIUM (153.6%) | GP: 4359.42</strong></td>
            <td>Harga berada di zona <strong>Premium</strong> (sudah relatif tinggi). Level <strong>Golden Pocket (GP)</strong> Fibonacci 61.8% berada di $4.359,42.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Pola Chart]</span></td>
            <td><strong>Scanning Geometri...</strong></td>
            <td>Mesin pola geometri sedang memantau potensi formasi Quasimodo atau Double Bottom.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Pola Lilin]</span></td>
            <td><strong style="color:#10b981;">Bullish Pin Bar [Skor: 90/100]</strong></td>
            <td>Terdeteksi lilin penolakan harga (<em>Rejection</em>) sangat valid dengan skor <strong>90/100 (Grade A+)</strong>. Ekor bawah panjang menandakan pembeli menolak harga turun.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Triple EMA]</span></td>
            <td><strong style="color:#10b981;">BULLISH (Di Atas 125) | Ribbon 8/21</strong></td>
            <td>Harga berada di atas EMA 125 Institusional (tren bullish), dan pita EMA 8 (Cyan) berada di atas EMA 21 (Magenta).</td>
        </tr>
        <tr>
            <td><span class="code-term">[S/R Pivot]</span></td>
            <td><strong>P: 4371.52 [R1: 4408.77 | S1: 4343.51]</strong></td>
            <td>Level batas harian: Titik Pivot Tengah di 4371.52, Resisten 1 di 4408.77, dan Support 1 di 4343.51.</td>
        </tr>
        <tr>
            <td><span class="code-term">[VSA Footprint]</span></td>
            <td><strong>Memantau Volume...</strong></td>
            <td>Volume Spread Analysis mengawasi lonjakan volume transaksi smart money.</td>
        </tr>
    </tbody>
</table>

<div class="section-title">5. Sistem Proteksi AI &amp; Penjaga Risiko Akun (Safety Shields)</div>
<p style="color:#64748b; margin-top:2px;">Bagian ini menjamin modal akun Anda terlindungi dari bahaya emosi, market sideways, dan drawdown besar:</p>

<table>
    <thead>
        <tr>
            <th style="width:26%;">Sistem Proteksi</th>
            <th style="width:28%;">Status di Screenshot</th>
            <th>Fungsi Perlindungan Terhadap Modal $20</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><span class="code-term">[Circuit Guard]</span></td>
            <td><strong style="color:#10b981;">Normal (0/2 Loss)</strong></td>
            <td><strong>Anti-Balas Dendam</strong>: Jika akun mengalami 2 loss beruntun dalam 1 sesi, EA otomatis rehat beberapa jam untuk mencegah kerugian beruntun. Saat ini 0/2 (aman).</td>
        </tr>
        <tr>
            <td><span class="code-term">[AI Brain / Heal]</span></td>
            <td><strong style="color:#10b981;">STANDBY (NORMAL)</strong></td>
            <td>Modul audit mandiri yang memeriksa integritas order, slippage broker, dan auto-reconnect.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Cuaca Pasar]</span></td>
            <td><strong>NORMAL (CI: 50.0)</strong></td>
            <td><strong>Choppiness Index (CI)</strong>: Mengukur kekacauan pasar. CI 50 menandakan kondisi pasar wajar (bukan badai sideways ekstrem).</td>
        </tr>
        <tr>
            <td><span class="code-term">[Rapor Pola]</span></td>
            <td><strong>Pin Bar / Hammer (100%)</strong></td>
            <td>Memori statistik internal EA mencatat pola Pin Bar memiliki akurasi kemenangan 100% pada sesi perdagangan terkini.</td>
        </tr>
        <tr>
            <td><span class="code-term">[News Shield]</span></td>
            <td><strong style="color:#ef4444;">WASPADA: JELANG 15:30 SERVER</strong></td>
            <td>Filter Berita Otomatis mendeteksi jadwal rilis berita ekonomi berdampak tinggi (High Impact News) pada pukul 15:30 waktu server.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Anti-Sideways]</span></td>
            <td><strong>ADX: 45.9 | Vol: 162% | Slope: AKTIF</strong></td>
            <td>ADX di angka <strong>45.9</strong> (sangat kuat di atas syarat 20.0) dan volume 162% memastikan robot hanya trading saat ada tren yang bertenaga.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Prop Firm Guard]</span></td>
            <td><strong>DD: 0.0% / Max 4.0% | AKTIF</strong></td>
            <td>Batas pengaman Drawdown harian maksimal 4.0% (standar ketat Prop Firm internasional) agar akun tidak pernah mengalami kerugian fatal.</td>
        </tr>
        <tr>
            <td><span class="code-term">[Pro Discipline]</span></td>
            <td><strong>Trades: 0 | AKTIF</strong></td>
            <td>Membatasi jumlah transaksi harian agar akun tidak overtrading.</td>
        </tr>
    </tbody>
</table>

<div class="footer">
    <div>Panduan Resmi Dashboard HUD • VIKAR EA 4-Pillar Pro MT4</div>
    <div>Dicetak pada: {datetime.now().strftime('%d %B %Y %H:%M')} • Halaman 2 dari 3</div>
</div>

<div class="page-break"></div>

<!-- HALAMAN 3 -->
<div class="section-title">6. Penjelasan Khusus: Mengapa Muncul Kotak Peringatan Bawah?</div>

<div class="alert-box">
    <div style="font-size:12.5px; font-weight:800; margin-bottom:4px;">
        STATUS KECERDASAN PASAR:<br/>
        PRE-NEWS SHIELD: PEMBEKUAN ORDER JELANG BERITA AS @15:30
    </div>
    <div style="font-size:11px; line-height:1.55;">
        <strong>Pertanyaan Sering Muncul:</strong> <em>"Kenapa robot tidak membuka order padahal ada sinyal bagus?"</em><br/>
        <strong>Jawaban &amp; Logika Robot:</strong> Pesan ini adalah <strong>bukti kecerdasan sistem proteksi</strong> EA Anda. Robot mendeteksi bahwa pada pukul <strong>15:30 waktu server</strong> akan dirilis data ekonomi penting Amerika Serikat (seperti CPI / Non-Farm Payroll / PPI).<br/>
        Menjelang berita besar, broker biasanya melebarkan spread secara ekstrem dan pasar rentan mengalami <em>slippage</em> atau lonjakan harga liar bolak-balik dalam hitungan detik. Untuk <strong>melindungi modal $20 Anda dari risiko tersapu pergerakan liar</strong>, EA secara sengaja <strong>membekukan eksekusi order baru (Freeze Mode)</strong>.<br/>
        Begitu dampak rilis berita mereda dan spread kembali normal, EA akan otomatis mencairkan pembekuan (<em>Unfreeze</em>) dan melanjutkan perdagangan normal.
    </div>
</div>

<div class="section-title">Arti Baris Konfigurasi Aktif di Bagian Paling Bawah</div>
<div style="background:#0f172a; color:#ffffff; padding:10px 14px; border-radius:6px; font-family:'Consolas', monospace; font-size:11px; margin-bottom:14px;">
    SL+ (+5p)  |  Cut: ON  |  Trail: ON  |  Lot: 0.01
</div>

<table>
    <thead>
        <tr>
            <th style="width:25%;">Kode Pengaturan</th>
            <th style="width:25%;">Status Saat Ini</th>
            <th>Artinya Bagi Akun Anda</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><span class="code-term">SL+ (+5p)</span></td>
            <td><strong style="color:#10b981;">Aktif (+5 Pips)</strong></td>
            <td>Saat posisi floating profit mencapai +8 pips, Stop Loss otomatis digeser ke +5 pips untuk mengunci keuntungan bebas risiko.</td>
        </tr>
        <tr>
            <td><span class="code-term">Cut: ON</span></td>
            <td><strong style="color:#10b981;">Aktif (Auto-Cut)</strong></td>
            <td>Fitur pemotong posisi darurat: Jika candle mendadak menembus Ribbon EMA secara berlawanan, order langsung ditutup untuk mengamankan profit sisa.</td>
        </tr>
        <tr>
            <td><span class="code-term">Trail: ON</span></td>
            <td><strong style="color:#10b981;">Aktif (Trailing Stop)</strong></td>
            <td>SL dinamis mengawal harga lilin demi lilin untuk membiarkan keuntungan berlari (<em>let your profit run</em>).</td>
        </tr>
        <tr>
            <td><span class="code-term">Lot: 0.01</span></td>
            <td><strong style="color:#0284c7;">0.01 Lot</strong></td>
            <td>Ukuran lot teraman untuk modal $20 di broker QuickPro.</td>
        </tr>
    </tbody>
</table>

<div class="section-title">7. Panduan Ringkas Kode Warna Bagi Trader</div>
<div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom:16px;">
    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:6px; padding:8px 10px;">
        <div style="color:#16a34a; font-weight:800; font-size:11px;">HIJAU</div>
        <div style="font-size:10px; color:#334155; margin-top:2px;">Kondisi ideal, tren bullish kuat, profit aman, konfluensi selaras.</div>
    </div>
    <div style="background:#eff6ff; border:1px solid #93c5fd; border-radius:6px; padding:8px 10px;">
        <div style="color:#2563eb; font-weight:800; font-size:11px;">CYAN / BIRU</div>
        <div style="font-size:10px; color:#334155; margin-top:2px;">Informasi struktur BOS, order block FVG, level Fibonacci aktif.</div>
    </div>
    <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:6px; padding:8px 10px;">
        <div style="color:#d97706; font-weight:800; font-size:11px;">KUNING / ORANYE</div>
        <div style="font-size:10px; color:#334155; margin-top:2px;">Status waspada, pasar netral / konflik timeframe, menunggu konfirmasi.</div>
    </div>
    <div style="background:#fef2f2; border:1px solid #fca5a5; border-radius:6px; padding:8px 10px;">
        <div style="color:#dc2626; font-weight:800; font-size:11px;">MERAH</div>
        <div style="font-size:10px; color:#334155; margin-top:2px;">Peringatan proteksi, pra-berita high impact, atau tren bearish.</div>
    </div>
</div>

<div class="highlight-box">
    <strong>Kesimpulan Trader:</strong> Dashboard HUD adalah kokpit pesawat trading Anda. Anda tidak perlu menebak-nebak apa yang sedang terjadi di chart. Cukup lirik HUD untuk mengetahui kesehatan akun, kualitas sinyal lilin, dan status pengaman otomatis yang sedang bekerja menjaga modal Anda.
</div>

<div class="footer">
    <div>Panduan Resmi Dashboard HUD • VIKAR EA 4-Pillar Pro MT4</div>
    <div>Dicetak pada: {datetime.now().strftime('%d %B %Y %H:%M')} • Halaman 3 dari 3</div>
</div>

</body>
</html>
"""

    temp_html_path = r"e:\Python\STRATEGY\temp_hud_guide.html"
    pdf_dest_proj = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\PANDUAN_LENGKAP_DASHBOARD_HUD_MT4.pdf"
    pdf_dest_root = r"e:\Python\STRATEGY\PANDUAN_LENGKAP_DASHBOARD_HUD_MT4.pdf"
    pdf_dest_terminal = r"C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\F0B9948E0028C307A69410B7E4F7F6B6\MQL4\PANDUAN_LENGKAP_DASHBOARD_HUD_MT4.pdf"
    artifact_dir = r"C:\Users\vikar\.gemini\antigravity-ide\brain\299352ef-4615-48c5-a529-06d94f4d54c1"
    pdf_dest_artifact = os.path.join(artifact_dir, "PANDUAN_LENGKAP_DASHBOARD_HUD_MT4.pdf")

    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_path):
        edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

    print(f"[+] Mengonversi HTML ke PDF profesional via Edge Headless...")
    cmd = [
        edge_path,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_dest_proj}",
        temp_html_path
    ]

    subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(pdf_dest_proj):
        size = os.path.getsize(pdf_dest_proj)
        print(f"[OK] File PDF HUD Guide berhasil dibuat di: {pdf_dest_proj} ({size:,} bytes)")
        
        with open(pdf_dest_proj, "rb") as f:
            pdf_bytes = f.read()
        page_matches = re.findall(b"/Type\\s*/Page[^s]", pdf_bytes)
        print(f"[+] Total Halaman PDF: {len(page_matches)} Halaman.")

        shutil.copy2(pdf_dest_proj, pdf_dest_root)
        shutil.copy2(pdf_dest_proj, pdf_dest_terminal)
        shutil.copy2(pdf_dest_proj, pdf_dest_artifact)
        print(f"[+] Disalin ke Direktori Utama: {pdf_dest_root}")
        print(f"[+] Disinkronkan ke QuickPro MT4 Terminal: {pdf_dest_terminal}")
        print(f"[+] Disimpan ke Artifact System: {pdf_dest_artifact}")
    else:
        print("[-] Gagal membuat PDF HUD Guide.")

    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)

if __name__ == '__main__':
    main()
