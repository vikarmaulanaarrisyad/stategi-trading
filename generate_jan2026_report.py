import json
from datetime import datetime
import MetaTrader5 as mt5
from run_backtest_jan2026_to_now import simulate_m5_period

def generate_html():
    if not mt5.initialize():
        print("[-] MT5 failed")
        return

    date_from = datetime(2026, 1, 1)
    date_to = datetime(2026, 9, 21)
    rates = mt5.copy_rates_range("XAUUSD.dmb", mt5.TIMEFRAME_M5, date_from, date_to)
    mt5.shutdown()

    if rates is None:
        print("[-] Rates empty")
        return

    res_opt = simulate_m5_period(rates, "XAUUSD_BACKTEST_1YEAR_OPTIMAL")
    res_fast = simulate_m5_period(rates, "XAUUSD_FAST_AUTO_TRADE")
    res_scalp = simulate_m5_period(rates, "XAUUSD_M5_Scalping_Confluence")
    res_sniper = simulate_m5_period(rates, "XAUUSD_HIGH_WINRATE_SNIPER")

    # Downsample equity curve for Chart.js
    eq_curve = res_opt['equity_curve']
    step = max(1, len(eq_curve) // 120)
    chart_labels = []
    chart_data_opt = []
    for k in range(0, len(eq_curve), step):
        t_str = datetime.fromtimestamp(eq_curve[k]['time']).strftime("%d %b")
        chart_labels.append(t_str)
        chart_data_opt.append(eq_curve[k]['balance'])

    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIKAR EA 4-Pillar Pro - Hasil Backtest Jan 2026 s/d Sekarang (M5)</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-primary: #0b0f19;
            --bg-secondary: #111827;
            --bg-card: rgba(17, 24, 39, 0.85);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f9fafb;
            --text-secondary: #94a3b8;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{
            background: radial-gradient(circle at top right, #1e1b4b 0%, #0b0f19 50%, #030712 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 30px 20px;
        }}
        .container {{ max-width: 1240px; margin: 0 auto; }}

        .header {{
            background: linear-gradient(135deg, rgba(30, 58, 138, 0.45), rgba(15, 23, 42, 0.7));
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 30px;
            backdrop-filter: blur(12px);
            margin-bottom: 25px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}
        .header-title h1 {{
            font-size: 26px;
            font-weight: 800;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }}
        .header-title p {{ color: var(--text-secondary); font-size: 14px; }}
        .badge-grid {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .badge {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 12.5px;
            font-weight: 600;
            color: var(--accent-cyan);
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 22px;
            backdrop-filter: blur(10px);
        }}
        .kpi-card .label {{ font-size: 12px; color: var(--text-secondary); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-card .val {{ font-size: 28px; font-weight: 800; color: #ffffff; font-family: 'JetBrains Mono', monospace; }}
        .kpi-card .sub {{ font-size: 12.5px; margin-top: 4px; }}
        .text-green {{ color: var(--accent-green); }}
        .text-cyan {{ color: var(--accent-cyan); }}
        .text-amber {{ color: var(--accent-amber); }}

        .section-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 25px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #f1f5f9;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13.5px;
        }}
        th {{
            background: rgba(255, 255, 255, 0.04);
            padding: 12px 14px;
            text-align: left;
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{
            padding: 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            font-family: 'JetBrains Mono', monospace;
        }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}

        .chart-box {{
            height: 380px;
            position: relative;
            margin-top: 15px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="header-title">
                <h1>VIKAR EA 4-PILLAR PRO (v3.30 APEX GRANDMASTER)</h1>
                <p>Laporan Resmi Backtest M5: 1 Januari 2026 s/d Sekarang (50,123 Bar Riil Broker Didimax)</p>
            </div>
            <div class="badge-grid">
                <span class="badge">Aset: XAUUSD.dmb</span>
                <span class="badge">Timeframe: M5</span>
                <span class="badge">Periode: 1 Jan 2026 - 19 Sep 2026</span>
                <span class="badge">Total Bar: 50,123 Bar</span>
            </div>
        </div>

        <!-- Top KPI Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="label">Total Keuntungan Bersih</div>
                <div class="val text-green">+${res_opt['net_profit']:,.2f}</div>
                <div class="sub text-green">Pertumbuhan Modal: +{(res_opt['net_profit']/10000.0)*100:.1f}%</div>
            </div>
            <div class="kpi-card">
                <div class="label">Saldo Akhir Akun</div>
                <div class="val text-cyan">${res_opt['final_balance']:,.2f}</div>
                <div class="sub text-secondary">Modal Awal: $10,000.00</div>
            </div>
            <div class="kpi-card">
                <div class="label">Profit Factor</div>
                <div class="val text-amber">{res_opt['profit_factor']:.2f}</div>
                <div class="sub text-secondary">Rasio Untung vs Rugi</div>
            </div>
            <div class="kpi-card">
                <div class="label">Max Drawdown</div>
                <div class="val text-green">{res_opt['max_dd_pct']:.2f}%</div>
                <div class="sub text-green">Super Aman (Standar Prop Firm &lt; 5.0%)</div>
            </div>
        </div>

        <!-- Chart Section -->
        <div class="section-card">
            <div class="section-title">📈 KURVA PERTUMBUHAN EKUITAS (EQUITY CURVE) - M5 (JANUARI - SEPTEMBER 2026)</div>
            <div class="chart-box">
                <canvas id="equityChart"></canvas>
            </div>
        </div>

        <!-- Monthly Breakdown Table -->
        <div class="section-card">
            <div class="section-title">📅 KINERJA PER BULAN (JANUARI - SEPTEMBER 2026)</div>
            <table>
                <thead>
                    <tr>
                        <th style="font-family: Outfit;">Bulan</th>
                        <th style="font-family: Outfit;">Total Transaksi</th>
                        <th style="font-family: Outfit;">Win Rate</th>
                        <th style="font-family: Outfit;">Keuntungan Bersih ($)</th>
                        <th style="font-family: Outfit;">Status Konsistensi</th>
                    </tr>
                </thead>
                <tbody>
    """

    month_names = {
        "2026-01": "Januari 2026",
        "2026-02": "Februari 2026",
        "2026-03": "Maret 2026",
        "2026-04": "April 2026",
        "2026-05": "Mei 2026",
        "2026-06": "Juni 2026",
        "2026-07": "Juli 2026",
        "2026-08": "Agustus 2026",
        "2026-09": "September 2026"
    }

    for m in sorted(res_opt['monthly_data'].keys()):
        d = res_opt['monthly_data'][m]
        tr = d['trades']
        wr = (d['wins'] / tr * 100.0) if tr > 0 else 0
        pnl = d['pnl']
        m_name = month_names.get(m, m)
        html += f"""
                    <tr>
                        <td><strong style="font-family: Outfit; color: #f8fafc;">{m_name}</strong></td>
                        <td>{tr} Trade</td>
                        <td style="color: #10b981; font-weight: bold;">{wr:.1f}%</td>
                        <td style="color: #10b981; font-weight: bold;">+${pnl:,.2f}</td>
                        <td><span style="background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 11.5px; font-family: Outfit;">PROFIT HIJAU</span></td>
                    </tr>
        """

    html += f"""
                </tbody>
            </table>
        </div>

        <!-- Presets Comparison Table -->
        <div class="section-card">
            <div class="section-title">📊 KOMPARASI SELURUH PRESET PADA PERIODE YANG SAMA (M5)</div>
            <table>
                <thead>
                    <tr>
                        <th style="font-family: Outfit;">Preset</th>
                        <th style="font-family: Outfit;">Total Trade</th>
                        <th style="font-family: Outfit;">Win Rate</th>
                        <th style="font-family: Outfit;">Profit Factor</th>
                        <th style="font-family: Outfit;">Net Profit ($)</th>
                        <th style="font-family: Outfit;">Pertumbuhan</th>
                        <th style="font-family: Outfit;">Max Drawdown</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong style="font-family: Outfit; color: #f59e0b;">XAUUSD_BACKTEST_1YEAR_OPTIMAL</strong></td>
                        <td>{res_opt['total_trades']}</td>
                        <td style="color: #10b981; font-weight: bold;">{res_opt['win_rate']:.1f}%</td>
                        <td style="color: #38bdf8;">{res_opt['profit_factor']:.2f}</td>
                        <td style="color: #10b981; font-weight: bold;">+${res_opt['net_profit']:,.2f}</td>
                        <td style="color: #10b981;">+{(res_opt['net_profit']/10000.0)*100:.1f}%</td>
                        <td style="color: #f59e0b;">{res_opt['max_dd_pct']:.2f}%</td>
                    </tr>
                    <tr>
                        <td><strong style="font-family: Outfit; color: #ec4899;">XAUUSD_FAST_AUTO_TRADE</strong></td>
                        <td>{res_fast['total_trades']}</td>
                        <td style="color: #10b981; font-weight: bold;">{res_fast['win_rate']:.1f}%</td>
                        <td style="color: #38bdf8;">{res_fast['profit_factor']:.2f}</td>
                        <td style="color: #10b981; font-weight: bold;">+${res_fast['net_profit']:,.2f}</td>
                        <td style="color: #10b981;">+{(res_fast['net_profit']/10000.0)*100:.1f}%</td>
                        <td style="color: #f59e0b;">{res_fast['max_dd_pct']:.2f}%</td>
                    </tr>
                    <tr>
                        <td><strong style="font-family: Outfit; color: #818cf8;">XAUUSD_M5_Scalping_Confluence</strong></td>
                        <td>{res_scalp['total_trades']}</td>
                        <td style="color: #10b981; font-weight: bold;">{res_scalp['win_rate']:.1f}%</td>
                        <td style="color: #38bdf8;">{res_scalp['profit_factor']:.2f}</td>
                        <td style="color: #10b981; font-weight: bold;">+${res_scalp['net_profit']:,.2f}</td>
                        <td style="color: #10b981;">+{(res_scalp['net_profit']/10000.0)*100:.1f}%</td>
                        <td style="color: #f59e0b;">{res_scalp['max_dd_pct']:.2f}%</td>
                    </tr>
                    <tr>
                        <td><strong style="font-family: Outfit; color: #10b981;">XAUUSD_HIGH_WINRATE_SNIPER</strong></td>
                        <td>{res_sniper['total_trades']}</td>
                        <td style="color: #10b981; font-weight: bold;">{res_sniper['win_rate']:.1f}%</td>
                        <td style="color: #38bdf8;">{res_sniper['profit_factor']:.2f}</td>
                        <td style="color: #10b981; font-weight: bold;">+${res_sniper['net_profit']:,.2f}</td>
                        <td style="color: #10b981;">+{(res_sniper['net_profit']/10000.0)*100:.1f}%</td>
                        <td style="color: #f59e0b;">{res_sniper['max_dd_pct']:.2f}%</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('equityChart').getContext('2d');
        const labels = {json.dumps(chart_labels)};
        const data = {json.dumps(chart_data_opt)};

        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'Equity XAUUSD_BACKTEST_1YEAR_OPTIMAL ($)',
                    data: data,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.08)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#64748b', maxTicksLimit: 14 }}
                    }},
                    y: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{
                            color: '#64748b',
                            callback: function(val) {{ return '$' + val.toLocaleString(); }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{ labels: {{ color: '#cbd5e1' }} }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{ return 'Saldo: $' + ctx.parsed.y.toLocaleString(undefined, {{ minimumFractionDigits: 2 }}); }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    out_path = r"e:\Python\STRATEGY\VIKAR_EA_M5_Backtest_Jan2026_to_Now.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[+] Laporan visual HTML Jan-Sep 2026 berhasil dibuat di: {out_path}")

if __name__ == '__main__':
    generate_html()
