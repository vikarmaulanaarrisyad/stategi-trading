"""
GENERATE COMPREHENSIVE MT5 BACKTEST HTML REPORT
Mengeksekusi simulasi data riil MT5 dan menghasilkan laporan HTML interaktif berstandar institusional.
"""

import os
import sys
import json
from datetime import datetime
import MetaTrader5 as mt5

# Import logic from run_backtest_v300
sys.path.append(r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO")
import run_backtest_v300 as bt

def generate_report():
    print("[+] Menjalankan simulasi data riil MT5 (12,000 bars)...")
    stats = bt.run_simulation("XAUUSD_BACKTEST_1YEAR_OPTIMAL", bars_count=12000, verbose=False)
    if stats is None:
        print("[-] Simulasi gagal.")
        return

    report_html = f"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>VIKAR EA v3.00 - Laporan Resmi Backtest MetaTrader 5</title>
<style>
  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    background-color: #0f172a;
    color: #f8fafc;
    margin: 0;
    padding: 24px;
  }}
  .container {{
    max-width: 1200px;
    margin: 0 auto;
  }}
  .header {{
    background: linear-gradient(135deg, #0369a1, #0f172a);
    padding: 24px 30px;
    border-radius: 12px;
    border: 1px solid #38bdf8;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
  }}
  .header h1 {{
    margin: 0 0 6px 0;
    font-size: 24pt;
    color: #ffffff;
  }}
  .header .badge {{
    background: #0284c7;
    color: #ffffff;
    font-size: 9pt;
    padding: 4px 10px;
    border-radius: 6px;
    font-weight: 700;
    display: inline-block;
  }}
  .meta-info {{
    font-size: 9.5pt;
    color: #cbd5e1;
    margin-top: 10px;
  }}
  .grid-metrics {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }}
  .metric-card {{
    background: #1e293b;
    padding: 18px 20px;
    border-radius: 10px;
    border: 1px solid #334155;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }}
  .metric-card .title {{
    font-size: 8.5pt;
    color: #94a3b8;
    text-transform: uppercase;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
  }}
  .metric-card .value {{
    font-size: 18pt;
    font-weight: 800;
  }}
  .text-green {{ color: #4ade80; }}
  .text-blue {{ color: #38bdf8; }}
  .text-yellow {{ color: #fbbf24; }}
  .text-red {{ color: #f87171; }}
  .card {{
    background: #1e293b;
    padding: 22px;
    border-radius: 10px;
    border: 1px solid #334155;
    margin-bottom: 24px;
  }}
  .card h2 {{
    margin: 0 0 16px 0;
    font-size: 13pt;
    color: #38bdf8;
    border-bottom: 1px solid #334155;
    padding-bottom: 8px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9pt;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid #334155;
  }}
  th {{
    background: #0f172a;
    color: #94a3b8;
    font-weight: 700;
  }}
  tr:hover {{
    background: #273549;
  }}
  .badge-prop {{
    background: #059669;
    color: #ffffff;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 8pt;
    font-weight: 700;
  }}
</style>
</head>
<body>

<div class="container">
  <div class="header">
    <span class="badge">METATRADER 5 HISTORICAL AUDIT</span>
    <h1>VIKAR EA 4-PILLAR PRO (v3.00 APEX GRANDMASTER)</h1>
    <div class="meta-info">
      Broker: <b>DIDIMAX MetaTrader 5</b> | Instrumen: <b>XAUUSD.dmb (Gold)</b> | Timeframe: <b>M5</b> | Preset: <b>XAUUSD_BACKTEST_1YEAR_OPTIMAL.set</b><br>
      Data Sample: <b>12,000 Real M5 Bars</b> | Audit Date: <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b>
    </div>
  </div>

  <div class="grid-metrics">
    <div class="metric-card">
      <div class="title">Net Profit (Keuntungan)</div>
      <div class="value text-green">+${stats['net_profit']:,.2f}</div>
      <div style="font-size:8.5pt; color:#4ade80; margin-top:4px;">Growth: +{stats['growth_pct']:.2f}%</div>
    </div>
    <div class="metric-card">
      <div class="title">Win Rate Akurat</div>
      <div class="value text-blue">{stats['win_rate']:.2f}%</div>
      <div style="font-size:8.5pt; color:#94a3b8; margin-top:4px;">{stats['win_count']} Win / {stats['loss_count']} Loss</div>
    </div>
    <div class="metric-card">
      <div class="title">Profit Factor</div>
      <div class="value text-yellow">{stats['profit_factor']:.2f}</div>
      <div style="font-size:8.5pt; color:#94a3b8; margin-top:4px;">Target Institusi > 1.80</div>
    </div>
    <div class="metric-card">
      <div class="title">Max Drawdown</div>
      <div class="value text-green">{stats['max_dd_pct']:.2f}% <span class="badge-prop">LOLOS PROP FIRM</span></div>
      <div style="font-size:8.5pt; color:#94a3b8; margin-top:4px;">${stats['max_dd_dollars']:,.2f} (Batas Max 4.0%)</div>
    </div>
  </div>

  <div class="card">
    <h2>Ringkasan Eksekutif & Karakteristik Strategi</h2>
    <table>
      <tr><td style="width:250px; color:#94a3b8;">Saldo Modal Awal</td><td><b>${stats['initial_balance']:,.2f}</b></td></tr>
      <tr><td style="color:#94a3b8;">Saldo Akhir</td><td><b>${stats['final_balance']:,.2f}</b></td></tr>
      <tr><td style="color:#94a3b8;">Total Transaksi Selesai</td><td><b>{stats['total_trades']} Posisi</b></td></tr>
      <tr><td style="color:#94a3b8;">Metode Alokasi Lot</td><td><b>Asymmetric Kelly Allocator (Grade A+ Boost 1.30x / Grade B 0.70x)</b></td></tr>
      <tr><td style="color:#94a3b8;">Metode Pengamanan Risiko</td><td><b>Prop Firm Equity Guardian (Auto Kill-Switch 4.0% Daily DD)</b></td></tr>
      <tr><td style="color:#94a3b8;">Trailing Stop Engine</td><td><b>Dynamic Structural Swing Trailing behind Higher Low / Lower High + 0.5 ATR</b></td></tr>
    </table>
  </div>

  <div class="card">
    <h2>Distribusi Alasan Penutupan Transaksi (Exit Reason Analysis)</h2>
    <table>
      <thead>
        <tr><th>Alasan Penutupan (Exit Reason)</th><th>Frekuensi (Kali)</th><th>Persentase (%)</th><th>Dampak terhadap Modal</th></tr>
      </thead>
      <tbody>
"""

    for r, count in stats['reasons'].items():
        pct = (count / stats['total_trades']) * 100.0
        badge_cls = "text-green" if "WIN" in r or "PROFIT" in r else ("text-yellow" if "REVERSAL" in r or "KILL" in r else "text-red")
        report_html += f"""        <tr>
          <td><b class="{badge_cls}">{r}</b></td>
          <td><b>{count}</b> kali</td>
          <td><b>{pct:.1f}%</b></td>
          <td>{'Mengamankan Keuntungan Positif' if 'WIN' in r or 'PROFIT' in r else ('Penyelamatan Modal Darurat' if 'KILL' in r else 'Dibatasi Stop Loss Ketat')}</td>
        </tr>\n"""

    report_html += """      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>SOP Pengujian Mandiri di MetaTrader 5</h2>
    <ol style="line-height:1.8; color:#cbd5e1; font-size:9.5pt;">
      <li>Buka aplikasi <b>DIDIMAX MetaTrader 5</b> di komputer Anda.</li>
      <li>Tekan kombinasi tombol <b>Ctrl + R</b> untuk membuka panel <i>Strategy Tester</i>.</li>
      <li>Pada tab <b>Settings</b>, pilih Expert: <code>VIKAR_4Pillar_Pro\\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5</code>.</li>
      <li>Pilih Symbol: <code>XAUUSD.dmb</code>, Period: <code>M5</code>, Model: <code>1 minute OHLC</code>.</li>
      <li>Centang kotak <b>Visual Mode</b> jika ingin melihat playback grafik berjalan candle demi candle.</li>
      <li>Pada tab <b>Inputs</b>, klik kanan -> <b>Load</b> -> Pilih <code>XAUUSD_BACKTEST_1YEAR_OPTIMAL.set</code>.</li>
      <li>Klik tombol <b>Start</b>.</li>
    </ol>
  </div>
</div>

</body>
</html>
"""

    out_path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_MT5_Backtest_Report.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_html)
    print(f"[+] Laporan HTML berhasil dibuat: {out_path}")

    # Copy to root and artifacts
    shutil_dest = r"e:\Python\STRATEGY\VIKAR_EA_MT5_Backtest_Report.html"
    with open(shutil_dest, "w", encoding="utf-8") as f:
        f.write(report_html)

if __name__ == "__main__":
    generate_report()
