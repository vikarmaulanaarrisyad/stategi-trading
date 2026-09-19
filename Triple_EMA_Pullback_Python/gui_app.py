"""
================================================================================
ROBOT TRADING TRIPLE EMA PULLBACK & SNR — INSTITUTIONAL DESKTOP TERMINAL PRO
================================================================================
Tampilan Antarmuka Modern, Elegan & Profesional berstandar TradingView / Bloomberg.
Fitur Utama:
1. Dual-Panel Candlestick Chart (Right-hand Price Axis, Wicks, Bodies, EMA 8/21/125,
   Value Zone Cloud, Dynamic S/R & RBS/SBR Lines, serta Sub-Window ADX Momentum)
2. Interactive Quick Toolbar (Timeframe Switcher M1-H4 & Lookback Bar Selector)
3. Top Header Bar dengan Digital Clock Multi-Zone (Server, WIB, UTC) & Ping Latency
4. Glassmorphic KPI Dashboard (Equity, Balance, Floating P/L, Daily Loss Buffer)
5. Strategy Telemetry & Confluence Radar HUD (Checklist 7 Konfluensi Institusional)
6. Operational Sidebar: Automation Control, Instant Scalping Dock & Parameter Settings
7. Active Order Management: Real-time Floating P/L, Tombol +BEP, Partial 50%, Close
8. Backtest Visualizer dengan Equity Curve & Drawdown Analysis
================================================================================
"""

import sys
import os
import time
import math
import threading
import queue
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any

import customtkinter as ctk
import pandas as pd
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

# Import modul strategi internal
from config import TradingConfig
from mt5_client import MT5Client
from indicators import (
    compute_all_indicators, calculate_ema,
    is_in_fibo_golden_zone_buy, is_in_fibo_golden_zone_sell
)
from strategy import TripleEmaStrategy, TradeSignal
from risk_manager import RiskManager
from candle_patterns import CandlePattern, get_pattern_name, detect_bullish_pattern, detect_bearish_pattern
from market_structure import MarketStructure, FilterResult, get_market_structure_name
from support_resistance import SupportResistanceAnalyzer, SnrSnapshot
from backtester import TripleEmaBacktester

# Konfigurasi Tema CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# =============================================================================
# PALET WARNA PROFESIONAL (DARK INSTITUTIONAL / TRADINGVIEW OBSERVATORY)
# =============================================================================
COLOR_BG_DEEP        = "#090d16"  # Background canvas utama (Obsidian Slate)
COLOR_PANEL_BG       = "#0f172a"  # Background panel & card utama
COLOR_PANEL_SUB      = "#131d35"  # Background sub-panel / nested container
COLOR_CARD_BORDER    = "#1e293b"  # Border garis halus
COLOR_BORDER_FOCUS   = "#334155"  # Border aktif / hover
COLOR_ACCENT_HOVER   = "#1e2c4a"  # Hover row / button

COLOR_ACCENT_CYAN    = "#00e5ff"  # Fast EMA 8 / Primary Telemetry
COLOR_ACCENT_GOLD    = "#f59e0b"  # Medium EMA 21 / Value Zone / Warning
COLOR_ACCENT_PURPLE  = "#a855f7"  # Slow EMA 125 / Major Baseline
COLOR_ACCENT_GREEN   = "#10b981"  # Bullish / Support / Win / Active State
COLOR_ACCENT_RED     = "#f43f5e"  # Bearish / Resistance / Loss / Danger
COLOR_ACCENT_ORANGE  = "#fb923c"  # SBR / Caution
COLOR_ACCENT_BLUE    = "#38bdf8"  # Info / ADX

COLOR_TEXT_PRIMARY   = "#f8fafc"  # Teks utama (putih tajam)
COLOR_TEXT_SECONDARY = "#94a3b8"  # Teks keterangan (slate grey)
COLOR_TEXT_MUTED     = "#64748b"  # Teks redup

FONT_FAMILY          = "Segoe UI"
FONT_MONO            = "Consolas"


class TradingTerminalApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ---------------------------------------------------------------------
        # Konfigurasi Window Utama
        # ---------------------------------------------------------------------
        self.title("TRIPLE EMA PULLBACK & SNR — INSTITUTIONAL TERMINAL PRO")
        self.geometry("1480x940")
        self.minsize(1240, 780)
        self.configure(fg_color=COLOR_BG_DEEP)

        # ---------------------------------------------------------------------
        # Inisialisasi Objek Inti & State
        # ---------------------------------------------------------------------
        self.cfg = TradingConfig()
        self.client = MT5Client()
        self.strategy = TripleEmaStrategy(self.cfg)
        self.risk_mgr = RiskManager(self.cfg)
        self.snr_analyzer = SupportResistanceAnalyzer(
            major_lookback=self.cfg.snr_major_lookback,
            minor_lookback=self.cfg.snr_minor_lookback
        )

        # State Robot & Broker
        self.is_bot_running = False
        self.is_mt5_connected = False
        self.real_symbol = self.cfg.symbol
        self.point_size = 0.01
        self.digits = 2
        self.stops_level = 0
        self.min_broker_dist = 0.15
        self.tick_size = 0.01
        self.tick_value = 1.0
        self.chart_bars_count = 80
        self.scalp_lot_selection = 0.10
        self.chart_tick_counter = 0

        # State Interaktif Chart (Drag / Pan & Wheel Zoom)
        self.is_chart_dragging = False
        self.chart_drag_start = None
        self.user_custom_chart_view = False
        self.saved_chart_xlim = None
        self.saved_chart_ylim = None

        # State Eksekusi
        self.bars_since_last_trade = 999
        self.partial_closed_tickets = set()
        self.last_bar_time = None
        self.latest_rates_df = None
        self.latest_snr_snapshot = None
        self.latest_signal_result: Optional[TradeSignal] = None

        # Antrian Log Thread-Safe
        self.log_queue = queue.Queue()

        # ---------------------------------------------------------------------
        # Bangun Tata Letak UI
        # ---------------------------------------------------------------------
        self._build_top_header()
        self._build_kpi_ribbon()
        self._build_main_workspace()

        # ---------------------------------------------------------------------
        # Mulai Timer Polling & Loop GUI
        # ---------------------------------------------------------------------
        self.after(300, self._initial_mt5_connection)
        self.after(1000, self._gui_update_loop)

    # =========================================================================
    # 1. TOP INSTITUTIONAL HEADER BAR
    # =========================================================================
    def _build_top_header(self):
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_PANEL_BG, corner_radius=0, height=62, border_width=1, border_color=COLOR_CARD_BORDER)
        self.header_frame.pack(side="top", fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)

        # Kiri: Branding & Nama Aplikasi
        brand_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_frame.pack(side="left", padx=16, pady=8)

        logo_icon = ctk.CTkLabel(
            brand_frame, 
            text="◈", 
            font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"), 
            text_color=COLOR_ACCENT_CYAN
        )
        logo_icon.pack(side="left", padx=(0, 8))

        brand_text_box = ctk.CTkFrame(brand_frame, fg_color="transparent")
        brand_text_box.pack(side="left")

        brand_title_row = ctk.CTkFrame(brand_text_box, fg_color="transparent")
        brand_title_row.pack(anchor="w")

        title_lbl = ctk.CTkLabel(
            brand_title_row,
            text="TRIPLE EMA PULLBACK",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        title_lbl.pack(side="left")

        snr_pill = ctk.CTkLabel(
            brand_title_row,
            text=" SNR PRO ",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            fg_color=COLOR_PANEL_SUB,
            text_color=COLOR_ACCENT_GOLD,
            corner_radius=4
        )
        snr_pill.pack(side="left", padx=6)

        subtitle_lbl = ctk.CTkLabel(
            brand_text_box,
            text="Institutional Algorithmic Terminal (EMA 8/21/125 + RBS/SBR Confluence Engine)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLOR_TEXT_SECONDARY
        )
        subtitle_lbl.pack(anchor="w")

        # Tengah: Bot Status Pill Badge
        self.status_pill = ctk.CTkButton(
            self.header_frame,
            text="● STANDBY (PAUSED)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color=COLOR_PANEL_SUB,
            hover_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_SECONDARY,
            corner_radius=20,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            width=165,
            height=30,
            command=self._on_click_toggle_bot
        )
        self.status_pill.pack(side="left", padx=20, pady=16)

        # Kanan: Multi-Zone Clocks & Broker Connection Badge
        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.pack(side="right", padx=16, pady=8)

        # Live Digital Clocks
        self.lbl_clocks = ctk.CTkLabel(
            right_header,
            text="Server: --:--:-- | WIB: --:--:--",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_clocks.pack(anchor="e")

        # Account Status
        self.lbl_account_info = ctk.CTkLabel(
            right_header,
            text="MT5: Menghubungkan terminal...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_ACCENT_CYAN
        )
        self.lbl_account_info.pack(anchor="e")

    # =========================================================================
    # 2. KPI METRICS RIBBON (4 GLASSMORPHIC CARDS)
    # =========================================================================
    def _build_kpi_ribbon(self):
        kpi_bar = ctk.CTkFrame(self, fg_color="transparent", height=74)
        kpi_bar.pack(fill="x", padx=14, pady=(8, 4))
        kpi_bar.pack_propagate(False)

        kpi_bar.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        self.kpi_equity, self.kpi_equity_sub = self._create_kpi_card(
            kpi_bar, 0, "TOTAL EQUITY & BALANCE", "$0.00", "Balance: $0.00 | Free: $0.00", COLOR_ACCENT_CYAN
        )
        self.kpi_floating_pl, self.kpi_floating_pl_sub = self._create_kpi_card(
            kpi_bar, 1, "FLOATING UNREALIZED P/L", "$0.00", "0 Posisi Terbuka", COLOR_TEXT_PRIMARY
        )
        self.kpi_daily_loss, self.kpi_daily_loss_sub = self._create_kpi_card(
            kpi_bar, 2, "CIRCUIT BREAKER BUFFER", "0 / 2 Loss", "Batas Keamanan: Max 2 Loss / Hari", COLOR_ACCENT_GREEN
        )
        self.kpi_spread, self.kpi_spread_sub = self._create_kpi_card(
            kpi_bar, 3, "LIVE MARKET SPREAD", "0 pts", "Bid: 0.00 | Ask: 0.00", COLOR_ACCENT_GOLD
        )

    def _create_kpi_card(self, parent, col, title, initial_val, sub_text, val_color):
        card = ctk.CTkFrame(
            parent,
            fg_color=COLOR_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        card.grid(row=0, column=col, padx=(0 if col == 0 else 8, 0), pady=0, sticky="nsew")

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(6, 2))

        ctk.CTkLabel(
            top_row,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(side="left")

        lbl_val = ctk.CTkLabel(
            card,
            text=initial_val,
            font=ctk.CTkFont(family=FONT_MONO, size=16, weight="bold"),
            text_color=val_color
        )
        lbl_val.pack(anchor="w", padx=12, pady=(0, 2))

        lbl_sub = ctk.CTkLabel(
            card,
            text=sub_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=COLOR_TEXT_MUTED
        )
        lbl_sub.pack(anchor="w", padx=12, pady=(0, 6))

        return lbl_val, lbl_sub

    # =========================================================================
    # 3. MAIN WORKSPACE (SIDEBAR + CENTER TABS + BOTTOM LOG)
    # =========================================================================
    def _build_main_workspace(self):
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=14, pady=(4, 10))

        # Panel Kiri: Operational Sidebar
        self._build_operational_sidebar(workspace)

        # Panel Kanan: Center Tabs (Chart & Radar, Active Orders, Backtest) + Log Bottom
        right_pane = ctk.CTkFrame(workspace, fg_color="transparent")
        right_pane.pack(side="left", fill="both", expand=True)

        # Tabview Utama
        self.tabview = ctk.CTkTabview(
            right_pane,
            fg_color=COLOR_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.tabview.pack(fill="both", expand=True, padx=0, pady=(0, 6))

        self.tab_chart = self.tabview.add("📈 LIVE CHART & SNR RADAR")
        self.tab_orders = self.tabview.add("📋 POSISI AKTIF & ORDER MANAGER")
        self.tab_backtest = self.tabview.add("🧪 BACKTEST SIMULATOR")

        self._build_tab_chart_content()
        self._build_tab_orders_content()
        self._build_tab_backtest_content()

        # Bottom Console Log Dock
        self._build_bottom_log_dock(right_pane)

    # -------------------------------------------------------------------------
    # OPERATIONAL SIDEBAR
    # -------------------------------------------------------------------------
    def _build_operational_sidebar(self, parent):
        self.sidebar = ctk.CTkScrollableFrame(
            parent,
            width=320,
            fg_color=COLOR_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        self.sidebar.pack(side="left", fill="y", padx=(0, 8), pady=0)

        # Card 1: Bot Execution Engine
        sec1 = self._create_sidebar_section("🚀 AUTOMATION ENGINE")

        self.btn_toggle_bot = ctk.CTkButton(
            sec1,
            text="▶ START AUTO TRADING",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            fg_color=COLOR_ACCENT_GREEN,
            hover_color="#059669",
            text_color="#000000",
            height=38,
            corner_radius=6,
            command=self._on_click_toggle_bot
        )
        self.btn_toggle_bot.pack(fill="x", padx=8, pady=(4, 6))

        self.btn_panic_close = ctk.CTkButton(
            sec1,
            text="⚠ EMERGENCY: CLOSE ALL TRADES",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            fg_color="#881337",
            hover_color="#9f1239",
            text_color="#ffffff",
            height=28,
            corner_radius=6,
            command=self._on_click_close_all
        )
        self.btn_panic_close.pack(fill="x", padx=8, pady=(0, 6))

        # Card 2: Instant Scalping Dock
        sec2 = self._create_sidebar_section("⚡ INSTANT SCALPING DOCK")

        ctk.CTkLabel(
            sec2, 
            text="Preset Volume Lot:", 
            font=ctk.CTkFont(size=9, weight="bold"), 
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", padx=8, pady=(2, 4))

        lot_pills_frame = ctk.CTkFrame(sec2, fg_color="transparent")
        lot_pills_frame.pack(fill="x", padx=8, pady=(0, 6))

        self.lot_pill_btns = {}
        for lot_val in [0.01, 0.05, 0.10, 0.20]:
            btn = ctk.CTkButton(
                lot_pills_frame,
                text=f"{lot_val:.2f}",
                font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"),
                width=65,
                height=26,
                fg_color=COLOR_ACCENT_CYAN if lot_val == 0.10 else COLOR_PANEL_SUB,
                text_color="#000000" if lot_val == 0.10 else COLOR_TEXT_PRIMARY,
                hover_color=COLOR_BORDER_FOCUS,
                corner_radius=4,
                command=lambda v=lot_val: self._select_scalp_lot(v)
            )
            btn.pack(side="left", padx=(0, 4))
            self.lot_pill_btns[lot_val] = btn

        scalp_btns_frame = ctk.CTkFrame(sec2, fg_color="transparent")
        scalp_btns_frame.pack(fill="x", padx=8, pady=(0, 6))

        btn_buy = ctk.CTkButton(
            scalp_btns_frame,
            text="▲ BUY INSTANT",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color="#065f46",
            hover_color="#047857",
            height=32,
            width=140,
            corner_radius=6,
            command=self._on_click_manual_buy
        )
        btn_buy.pack(side="left", padx=(0, 6))

        btn_sell = ctk.CTkButton(
            scalp_btns_frame,
            text="▼ SELL INSTANT",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color="#9f1239",
            hover_color="#be123c",
            height=32,
            width=140,
            corner_radius=6,
            command=self._on_click_manual_sell
        )
        btn_sell.pack(side="left")

        # Card 3: Market & Parameter Setup
        sec3 = self._create_sidebar_section("⚙️ MARKET & RISK SETUP")

        self._create_input_label(sec3, "Simbol Instrumen:")
        sym_row = ctk.CTkFrame(sec3, fg_color="transparent")
        sym_row.pack(fill="x", padx=8, pady=(0, 4))

        self.entry_symbol = ctk.CTkEntry(sym_row, width=130, height=28, border_color=COLOR_CARD_BORDER)
        self.entry_symbol.insert(0, self.cfg.symbol)
        self.entry_symbol.pack(side="left", padx=(0, 6))

        self.opt_timeframe = ctk.CTkOptionMenu(
            sym_row,
            values=["M1", "M5", "M15", "M30", "H1", "H4"],
            width=140,
            height=28,
            command=self._on_change_timeframe,
            fg_color=COLOR_PANEL_SUB,
            button_color=COLOR_CARD_BORDER
        )
        self.opt_timeframe.set(self.cfg.timeframe)
        self.opt_timeframe.pack(side="left")

        self._create_input_label(sec3, "Mode Lot & Resiko Per Trade (%):")
        risk_row = ctk.CTkFrame(sec3, fg_color="transparent")
        risk_row.pack(fill="x", padx=8, pady=(0, 4))

        self.opt_lot_mode = ctk.CTkOptionMenu(
            risk_row,
            values=["RISK_PERCENT", "FIXED"],
            width=150,
            height=28,
            fg_color=COLOR_PANEL_SUB,
            button_color=COLOR_CARD_BORDER,
            command=self._on_change_lot_mode
        )
        self.opt_lot_mode.set(self.cfg.lot_mode)
        self.opt_lot_mode.pack(side="left", padx=(0, 6))

        self.entry_risk = ctk.CTkEntry(risk_row, width=120, height=28, border_color=COLOR_CARD_BORDER)
        self.entry_risk.insert(0, str(self.cfg.risk_percent))
        self.entry_risk.pack(side="left")

        self._create_input_label(sec3, "Target Risk:Reward Ratio (1:X):")
        self.entry_rr = ctk.CTkEntry(sec3, height=28, border_color=COLOR_CARD_BORDER)
        self.entry_rr.insert(0, str(self.cfg.risk_reward_ratio))
        self.entry_rr.pack(fill="x", padx=8, pady=(0, 8))

        # Card 4: Strategy Confluence Switches
        sec4 = self._create_sidebar_section("🛡️ STRATEGY & SAFETY CONFLUENCE")

        self.switch_snr = self._create_confluence_switch(sec4, "Filter SNR (Obstacle & Confluence)", True, COLOR_ACCENT_GOLD)
        self.switch_smc = self._create_confluence_switch(sec4, "Filter SMC (Discount/Prem & Sweep)", getattr(self.cfg, 'use_smc_filter', True), COLOR_ACCENT_CYAN)
        self.switch_fibo = self._create_confluence_switch(sec4, "Filter Fibo Golden Zone (50-78.6%)", getattr(self.cfg, 'use_fibo_golden_zone', True), COLOR_ACCENT_GOLD)
        self.switch_rsi = self._create_confluence_switch(sec4, "Filter RSI Momentum (45-70 / 30-55)", getattr(self.cfg, 'use_rsi_filter', True), COLOR_ACCENT_CYAN)
        self.switch_fvg = self._create_confluence_switch(sec4, "Filter FVG Imbalance Mitigasi", getattr(self.cfg, 'use_fvg_filter', False))
        self.switch_partial = self._create_confluence_switch(sec4, "Partial Take Profit 50% (1:1 R)", getattr(self.cfg, 'use_partial_close', True))
        self.switch_bep = self._create_confluence_switch(sec4, "Auto Break-Even (Kunci Impas)", self.cfg.use_break_even)
        self.switch_trailing = self._create_confluence_switch(sec4, "Trailing Stop (EMA 21 Dynamic)", self.cfg.use_trailing_stop)
        self.switch_cb = self._create_confluence_switch(sec4, f"Circuit Breaker (Maks {self.cfg.max_daily_losses} Loss)", self.cfg.use_daily_loss_limit)
        self.switch_friday = self._create_confluence_switch(sec4, "Friday Night Auto-Close (21:30)", self.cfg.use_friday_close)
        self.switch_mtf = self._create_confluence_switch(sec4, f"Filter HTF Macro ({self.cfg.htf_timeframe} EMA 50)", self.cfg.use_mtf_filter)
        self.switch_shock = self._create_confluence_switch(sec4, "Filter News Shock Volatilitas", getattr(self.cfg, 'use_fundamental_shock_filter', True))

        btn_apply = ctk.CTkButton(
            sec4,
            text="💾 SIMPAN & TERAPKAN PARAMETER",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color=COLOR_PANEL_SUB,
            hover_color=COLOR_CARD_BORDER,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            height=32,
            command=self._apply_inputs_to_config
        )
        btn_apply.pack(fill="x", padx=8, pady=(8, 6))

    def _create_sidebar_section(self, title):
        sec = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLOR_PANEL_SUB,
            corner_radius=6,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        sec.pack(fill="x", padx=6, pady=(4, 6))

        lbl = ctk.CTkLabel(
            sec,
            text=title,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLOR_ACCENT_CYAN
        )
        lbl.pack(anchor="w", padx=8, pady=(6, 4))
        return sec

    def _create_input_label(self, parent, text):
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        lbl.pack(anchor="w", padx=8, pady=(4, 1))

    def _create_confluence_switch(self, parent, text, default_val, text_color=COLOR_TEXT_PRIMARY):
        sw = ctk.CTkSwitch(
            parent,
            text=text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=text_color,
            command=self._sync_switches
        )
        if default_val:
            sw.select()
        sw.pack(anchor="w", padx=8, pady=3)
        return sw

    def _select_scalp_lot(self, lot_val):
        self.scalp_lot_selection = lot_val
        for v, btn in self.lot_pill_btns.items():
            if v == lot_val:
                btn.configure(fg_color=COLOR_ACCENT_CYAN, text_color="#000000")
            else:
                btn.configure(fg_color=COLOR_PANEL_SUB, text_color=COLOR_TEXT_PRIMARY)

    # =========================================================================
    # TAB 1: DUAL-PANEL CANDLESTICK CHART + SNR TELEMETRY HUD
    # =========================================================================
    def _build_tab_chart_content(self):
        container = ctk.CTkFrame(self.tab_chart, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # Sebelah Kiri: Chart Area + Toolbar Timeframe
        chart_container = ctk.CTkFrame(container, fg_color=COLOR_BG_DEEP, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        chart_container.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=0)

        # Quick Toolbar di atas chart
        tb = ctk.CTkFrame(chart_container, fg_color=COLOR_PANEL_SUB, height=36, corner_radius=6)
        tb.pack(fill="x", padx=6, pady=(6, 2))
        tb.pack_propagate(False)

        ctk.CTkLabel(
            tb,
            text="TIMEFRAME:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(side="left", padx=(10, 4), pady=6)

        self.tf_pills = {}
        for tf in ["M1", "M5", "M15", "M30", "H1", "H4"]:
            btn = ctk.CTkButton(
                tb,
                text=tf,
                font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
                width=42,
                height=24,
                fg_color=COLOR_ACCENT_CYAN if tf == self.cfg.timeframe else COLOR_PANEL_BG,
                text_color="#000000" if tf == self.cfg.timeframe else COLOR_TEXT_PRIMARY,
                hover_color=COLOR_BORDER_FOCUS,
                corner_radius=4,
                command=lambda t=tf: self._switch_quick_tf(t)
            )
            btn.pack(side="left", padx=2, pady=6)
            self.tf_pills[tf] = btn

        # Separator kecil
        ctk.CTkFrame(tb, fg_color=COLOR_CARD_BORDER, width=1).pack(side="left", fill="y", padx=8, pady=6)

        ctk.CTkLabel(
            tb,
            text="BARS:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(side="left", padx=(4, 4), pady=6)

        self.bars_pills = {}
        for b_count in [50, 80, 120, 200]:
            btn = ctk.CTkButton(
                tb,
                text=str(b_count),
                font=ctk.CTkFont(family=FONT_MONO, size=10),
                width=38,
                height=24,
                fg_color=COLOR_ACCENT_GOLD if b_count == self.chart_bars_count else COLOR_PANEL_BG,
                text_color="#000000" if b_count == self.chart_bars_count else COLOR_TEXT_PRIMARY,
                hover_color=COLOR_BORDER_FOCUS,
                corner_radius=4,
                command=lambda bc=b_count: self._switch_quick_bars(bc)
            )
            btn.pack(side="left", padx=2, pady=6)
            self.bars_pills[b_count] = btn

        # Separator kecil
        ctk.CTkFrame(tb, fg_color=COLOR_CARD_BORDER, width=1).pack(side="left", fill="y", padx=8, pady=6)

        ctk.CTkLabel(
            tb,
            text="STREAM:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(side="left", padx=(4, 4), pady=6)

        self.opt_chart_refresh = ctk.CTkOptionMenu(
            tb,
            values=["1s (Live)", "2s", "5s", "Pause"],
            width=92,
            height=24,
            fg_color=COLOR_PANEL_BG,
            button_color=COLOR_CARD_BORDER
        )
        self.opt_chart_refresh.set("1s (Live)")
        self.opt_chart_refresh.pack(side="left", padx=2, pady=6)

        self.lbl_live_badge = ctk.CTkLabel(
            tb,
            text="● LIVE",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_ACCENT_GREEN
        )
        self.lbl_live_badge.pack(side="left", padx=6, pady=6)

        # Separator kecil
        ctk.CTkFrame(tb, fg_color=COLOR_CARD_BORDER, width=1).pack(side="left", fill="y", padx=4, pady=6)

        # Petunjuk Drag Geser & Zoom
        ctk.CTkLabel(
            tb,
            text="🖱️ DRAG: GESER | SCROLL: ZOOM",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(side="left", padx=4, pady=6)

        # Tombol Reset / Auto-Fit View
        self.btn_reset_view = ctk.CTkButton(
            tb,
            text="⟲ AUTO-FIT",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            width=78,
            height=24,
            fg_color=COLOR_PANEL_BG,
            hover_color=COLOR_CARD_BORDER,
            corner_radius=4,
            command=self._reset_chart_view
        )
        self.btn_reset_view.pack(side="right", padx=(2, 6), pady=6)

        # Tombol Refresh Chart Kanan
        btn_rechart = ctk.CTkButton(
            tb,
            text="🔄 REFRESH",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            width=78,
            height=24,
            fg_color=COLOR_PANEL_BG,
            hover_color=COLOR_CARD_BORDER,
            corner_radius=4,
            command=self._update_live_chart
        )
        btn_rechart.pack(side="right", padx=2, pady=6)

        # Dual-Panel Figure Matplotlib (75% Candlestick + 25% ADX Sub-window)
        self.fig = Figure(figsize=(8.0, 5.0), dpi=100, facecolor=COLOR_BG_DEEP)
        self.gs = gridspec.GridSpec(2, 1, height_ratios=[3.4, 1.0], hspace=0.08)
        
        # Subplot 1: Main Candlesticks + Triple EMA + SNR
        self.ax_main = self.fig.add_subplot(self.gs[0])
        self.ax_main.set_facecolor(COLOR_BG_DEEP)
        self.ax_main.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=8)
        self.ax_main.grid(True, linestyle="--", alpha=0.08, color=COLOR_TEXT_SECONDARY)
        self.ax_main.yaxis.tick_right()
        self.ax_main.yaxis.set_label_position("right")
        self.ax_main.set_xticklabels([])

        # Subplot 2: ADX Momentum Indicator
        self.ax_sub = self.fig.add_subplot(self.gs[1], sharex=self.ax_main)
        self.ax_sub.set_facecolor(COLOR_BG_DEEP)
        self.ax_sub.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=8)
        self.ax_sub.grid(True, linestyle="--", alpha=0.08, color=COLOR_TEXT_SECONDARY)
        self.ax_sub.yaxis.tick_right()
        self.ax_sub.yaxis.set_label_position("right")

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # Hubungkan interaksi mouse untuk drag/pan dan zoom
        self.canvas.mpl_connect('button_press_event', self._on_chart_press)
        self.canvas.mpl_connect('motion_notify_event', self._on_chart_motion)
        self.canvas.mpl_connect('button_release_event', self._on_chart_release)
        self.canvas.mpl_connect('scroll_event', self._on_chart_scroll)

        # Sebelah Kanan: Institutional Confluence Radar HUD
        self._build_confluence_radar_hud(container)

    def _switch_quick_tf(self, new_tf):
        self.user_custom_chart_view = False
        self.saved_chart_xlim = None
        self.saved_chart_ylim = None
        self.cfg.timeframe = new_tf
        self.opt_timeframe.set(new_tf)
        for t, btn in self.tf_pills.items():
            if t == new_tf:
                btn.configure(fg_color=COLOR_ACCENT_CYAN, text_color="#000000")
            else:
                btn.configure(fg_color=COLOR_PANEL_BG, text_color=COLOR_TEXT_PRIMARY)
        self.log(f"[Chart Toolbar] Timeframe berganti ke: {new_tf}", "INFO")
        self._update_live_chart()

    def _switch_quick_bars(self, new_bars):
        self.user_custom_chart_view = False
        self.saved_chart_xlim = None
        self.saved_chart_ylim = None
        self.chart_bars_count = new_bars
        for bc, btn in self.bars_pills.items():
            if bc == new_bars:
                btn.configure(fg_color=COLOR_ACCENT_GOLD, text_color="#000000")
            else:
                btn.configure(fg_color=COLOR_PANEL_BG, text_color=COLOR_TEXT_PRIMARY)
        self._update_live_chart()

    # -------------------------------------------------------------------------
    # INTERAKSI MOUSE: GESER (PAN) & ZOOM CANDLESTICK CHART
    # -------------------------------------------------------------------------
    def _on_chart_press(self, event):
        if event.dblclick:
            # Double click me-reset tampilan kembali ke posisi default (Auto-Fit)
            self._reset_chart_view()
            return
        if event.inaxes in (self.ax_main, self.ax_sub) and event.button == 1:
            self.is_chart_dragging = True
            self.chart_drag_start = {
                'x': event.x,
                'y': event.y,
                'xlim_main': self.ax_main.get_xlim(),
                'ylim_main': self.ax_main.get_ylim(),
                'ylim_sub': self.ax_sub.get_ylim(),
                'inaxes': event.inaxes
            }
            self.user_custom_chart_view = True

    def _on_chart_motion(self, event):
        if not getattr(self, 'is_chart_dragging', False) or self.chart_drag_start is None:
            return
        if event.x is None or event.y is None:
            return

        dx_pix = event.x - self.chart_drag_start['x']
        dy_pix = event.y - self.chart_drag_start['y']

        # Konversi pergeseran pixel layar ke unit data sumbu X & Y
        target_ax = self.chart_drag_start['inaxes']
        inv = target_ax.transData.inverted()
        p0 = inv.transform((0, 0))
        p_delta = inv.transform((dx_pix, dy_pix))
        dx_data = p_delta[0] - p0[0]
        dy_data = p_delta[1] - p0[1]

        # Geser sumbu horizontal (X) secara sinkron untuk candlestick & sub-window ADX
        orig_xlim = self.chart_drag_start['xlim_main']
        new_xlim = (orig_xlim[0] - dx_data, orig_xlim[1] - dx_data)
        self.ax_main.set_xlim(new_xlim)
        self.ax_sub.set_xlim(new_xlim)

        # Geser sumbu vertikal (Y)
        if target_ax == self.ax_main:
            orig_ylim = self.chart_drag_start['ylim_main']
            new_ylim = (orig_ylim[0] - dy_data, orig_ylim[1] - dy_data)
            self.ax_main.set_ylim(new_ylim)
        elif target_ax == self.ax_sub:
            orig_ylim_sub = self.chart_drag_start['ylim_sub']
            new_ylim_sub = (orig_ylim_sub[0] - dy_data, orig_ylim_sub[1] - dy_data)
            self.ax_sub.set_ylim(new_ylim_sub)

        self.saved_chart_xlim = new_xlim
        self.saved_chart_ylim = self.ax_main.get_ylim()
        self.canvas.draw_idle()

    def _on_chart_release(self, event):
        self.is_chart_dragging = False
        if getattr(self, 'user_custom_chart_view', False):
            self.saved_chart_xlim = self.ax_main.get_xlim()
            self.saved_chart_ylim = self.ax_main.get_ylim()

    def _on_chart_scroll(self, event):
        if event.inaxes in (self.ax_main, self.ax_sub):
            self.user_custom_chart_view = True
            is_zoom_in = (event.button == 'up' or getattr(event, 'step', 0) > 0)
            factor = 0.82 if is_zoom_in else 1.22

            # Zoom horizontal X berpusat di posisi kursor mouse
            cur_xlim = self.ax_main.get_xlim()
            x_mouse = event.xdata if event.xdata is not None else (cur_xlim[0] + cur_xlim[1]) / 2.0
            cur_w = cur_xlim[1] - cur_xlim[0]
            new_w = cur_w * factor

            if 5 < new_w < 800:
                left_ratio = (x_mouse - cur_xlim[0]) / cur_w if cur_w > 0 else 0.5
                new_xlim = (x_mouse - new_w * left_ratio, x_mouse + new_w * (1 - left_ratio))
                self.ax_main.set_xlim(new_xlim)
                self.ax_sub.set_xlim(new_xlim)
                self.saved_chart_xlim = new_xlim

            # Zoom vertikal Y jika mouse berada di panel utama candlestick
            if event.inaxes == self.ax_main:
                cur_ylim = self.ax_main.get_ylim()
                y_mouse = event.ydata if event.ydata is not None else (cur_ylim[0] + cur_ylim[1]) / 2.0
                cur_h = cur_ylim[1] - cur_ylim[0]
                new_h = cur_h * factor
                bot_ratio = (y_mouse - cur_ylim[0]) / cur_h if cur_h > 0 else 0.5
                new_ylim = (y_mouse - new_h * bot_ratio, y_mouse + new_h * (1 - bot_ratio))
                self.ax_main.set_ylim(new_ylim)
                self.saved_chart_ylim = new_ylim

            self.canvas.draw_idle()

    def _reset_chart_view(self):
        self.user_custom_chart_view = False
        self.saved_chart_xlim = None
        self.saved_chart_ylim = None
        self._update_live_chart()
        self.log("[Chart] Tampilan grafik di-reset ke posisi Auto-Fit.", "INFO")

    # -------------------------------------------------------------------------
    # CONFLUENCE RADAR HUD (7-POINT INSTITUTIONAL CHECKLIST)
    # -------------------------------------------------------------------------
    def _build_confluence_radar_hud(self, parent):
        hud = ctk.CTkFrame(
            parent,
            width=320,
            fg_color=COLOR_PANEL_SUB,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        hud.pack(side="right", fill="y", padx=0, pady=0)
        hud.pack_propagate(False)

        top_hud = ctk.CTkFrame(hud, fg_color="transparent")
        top_hud.pack(fill="x", padx=12, pady=(10, 4))

        ctk.CTkLabel(
            top_hud,
            text="CONFLUENCE RADAR & TELEMETRY",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_ACCENT_CYAN
        ).pack(side="left")

        # Probability Score Banner
        self.card_score_banner = ctk.CTkFrame(hud, fg_color=COLOR_PANEL_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        self.card_score_banner.pack(fill="x", padx=10, pady=(4, 8))

        self.lbl_overall_bias = ctk.CTkLabel(
            self.card_score_banner,
            text="EVALUATING MARKET...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_overall_bias.pack(anchor="w", padx=10, pady=(6, 1))

        self.lbl_score_gauge = ctk.CTkLabel(
            self.card_score_banner,
            text="Score: 0 / 7 Confluences",
            font=ctk.CTkFont(family=FONT_MONO, size=10),
            text_color=COLOR_ACCENT_GOLD
        )
        self.lbl_score_gauge.pack(anchor="w", padx=10, pady=(0, 6))

        # Target & Live Signal Radar Card
        self.card_signal_radar = ctk.CTkFrame(hud, fg_color=COLOR_PANEL_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        self.card_signal_radar.pack(fill="x", padx=10, pady=(0, 6))

        sig_hdr = ctk.CTkFrame(self.card_signal_radar, fg_color="transparent")
        sig_hdr.pack(fill="x", padx=8, pady=(4, 2))
        
        ctk.CTkLabel(sig_hdr, text="🎯 TARGETS & LIVE SIGNAL", font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"), text_color=COLOR_ACCENT_CYAN).pack(side="left")
        self.lbl_sig_badge = ctk.CTkLabel(sig_hdr, text="SCANNING SETUP", font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"), text_color=COLOR_TEXT_SECONDARY)
        self.lbl_sig_badge.pack(side="right")

        self.lbl_sig_entry = self._create_hud_data_row(self.card_signal_radar, "• Entry Projected:", "$0.00", COLOR_TEXT_PRIMARY)
        self.lbl_sig_sl = self._create_hud_data_row(self.card_signal_radar, "• Stop Loss (SL):", "$0.00", COLOR_ACCENT_RED)
        self.lbl_sig_tp = self._create_hud_data_row(self.card_signal_radar, "• Take Profit (TP):", "$0.00", COLOR_ACCENT_GREEN)
        self.lbl_sig_partial = self._create_hud_data_row(self.card_signal_radar, "• Partial 50% (1:1):", "$0.00", COLOR_ACCENT_GOLD)

        # Checklist 7 Konfluensi
        checklist_box = ctk.CTkFrame(hud, fg_color="transparent")
        checklist_box.pack(fill="x", padx=8, pady=(0, 6))

        self.chk_ema = self._create_hud_checklist_row(checklist_box, "1. Triple EMA Stack:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_value_zone = self._create_hud_checklist_row(checklist_box, "2. Value Zone Pullback:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_fibo = self._create_hud_checklist_row(checklist_box, "3. Fibo Golden Pocket:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_rsi = self._create_hud_checklist_row(checklist_box, "4. RSI 14 Momentum:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_pattern = self._create_hud_checklist_row(checklist_box, "5. Candlestick Trigger:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_structure = self._create_hud_checklist_row(checklist_box, "6. Market Structure:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_adx = self._create_hud_checklist_row(checklist_box, "7. ADX Trend Momentum:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_snr_clear = self._create_hud_checklist_row(checklist_box, "8. SNR Obstacle Clearance:", "Scanning...", COLOR_TEXT_MUTED)
        self.chk_htf = self._create_hud_checklist_row(checklist_box, "9. HTF Macro Confluence:", "Scanning...", COLOR_TEXT_MUTED)

        # Dynamic S/R Levels Box
        ctk.CTkFrame(hud, fg_color=COLOR_CARD_BORDER, height=1).pack(fill="x", padx=12, pady=6)

        snr_card = ctk.CTkFrame(hud, fg_color=COLOR_PANEL_BG, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        snr_card.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkLabel(
            snr_card, 
            text="DYNAMIC SNR RADAR LEVELS", 
            font=ctk.CTkFont(size=9, weight="bold"), 
            text_color=COLOR_TEXT_SECONDARY
        ).pack(anchor="w", padx=8, pady=(6, 2))

        self.hud_res = self._create_hud_data_row(snr_card, "Major Resistance:", "$0.00", COLOR_ACCENT_RED)
        self.hud_sup = self._create_hud_data_row(snr_card, "Major Support:", "$0.00", COLOR_ACCENT_GREEN)
        self.hud_role_rev = self._create_hud_data_row(snr_card, "RBS / SBR Zone:", "None", COLOR_ACCENT_GOLD)

    def _create_hud_checklist_row(self, parent, label_text, initial_status, color):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=24)
        row.pack(fill="x", padx=4, pady=2)
        row.pack_propagate(False)

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=COLOR_TEXT_SECONDARY
        )
        lbl.pack(side="left")

        stat = ctk.CTkLabel(
            row,
            text=initial_status,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=color
        )
        stat.pack(side="right")
        return stat

    def _create_hud_data_row(self, parent, label_text, initial_val, color):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=22)
        row.pack(fill="x", padx=8, pady=1)
        row.pack_propagate(False)

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=COLOR_TEXT_SECONDARY
        )
        lbl.pack(side="left")

        val = ctk.CTkLabel(
            row,
            text=initial_val,
            font=ctk.CTkFont(family=FONT_MONO, size=9, weight="bold"),
            text_color=color
        )
        val.pack(side="right")
        return val

    # =========================================================================
    # TAB 2: ACTIVE ORDERS & LIVE POSITION MANAGEMENT
    # =========================================================================
    def _build_tab_orders_content(self):
        container = ctk.CTkFrame(self.tab_orders, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=4, pady=4)

        # Bar Kontrol & Ringkasan Posisi
        summary_bar = ctk.CTkFrame(container, fg_color=COLOR_PANEL_SUB, height=44, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        summary_bar.pack(fill="x", padx=0, pady=(0, 6))
        summary_bar.pack_propagate(False)

        self.lbl_orders_summary = ctk.CTkLabel(
            summary_bar,
            text="Total Posisi: 0 | Floating P/L: $0.00 | Total Volume: 0.00 Lot",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        )
        self.lbl_orders_summary.pack(side="left", padx=14, pady=10)

        btn_refresh_orders = ctk.CTkButton(
            summary_bar,
            text="🔄 REFRESH POSISI",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            width=110,
            height=26,
            fg_color=COLOR_PANEL_BG,
            hover_color=COLOR_CARD_BORDER,
            command=self._refresh_orders_manually
        )
        btn_refresh_orders.pack(side="right", padx=10, pady=8)

        # Scrollable Frame Daftar Order
        self.orders_scroll = ctk.CTkScrollableFrame(container, fg_color=COLOR_BG_DEEP, corner_radius=8)
        self.orders_scroll.pack(fill="both", expand=True)

        self.lbl_no_orders = ctk.CTkLabel(
            self.orders_scroll,
            text="Tidak ada posisi terbuka saat ini.\nRobot atau Scalping siap mengeksekusi sinyal.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_no_orders.pack(pady=60)

    def _refresh_orders_manually(self):
        if not self.is_mt5_connected: return
        open_pos = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
        self._render_open_orders_table(open_pos)

    # =========================================================================
    # TAB 3: BACKTEST SIMULATOR & PERFORMANCE VISUALIZER
    # =========================================================================
    def _build_tab_backtest_content(self):
        container = ctk.CTkFrame(self.tab_backtest, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=4, pady=4)

        top_ctrl = ctk.CTkFrame(container, fg_color=COLOR_PANEL_SUB, height=48, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
        top_ctrl.pack(fill="x", padx=0, pady=(0, 6))
        top_ctrl.pack_propagate(False)

        ctk.CTkLabel(
            top_ctrl,
            text="Simulasi Data:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(10, 4), pady=10)

        self.opt_bars_count = ctk.CTkOptionMenu(
            top_ctrl,
            values=["500 Bars", "1000 Bars", "2000 Bars", "5000 Bars"],
            width=110,
            height=28,
            fg_color=COLOR_PANEL_BG,
            button_color=COLOR_CARD_BORDER
        )
        self.opt_bars_count.set("2000 Bars")
        self.opt_bars_count.pack(side="left", padx=4, pady=10)

        ctk.CTkLabel(
            top_ctrl,
            text="Mode:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(8, 4), pady=10)

        self.opt_bt_mode = ctk.CTkOptionMenu(
            top_ctrl,
            values=["Unconstrained (Bebas)", "Single Position (Realistis)"],
            width=180,
            height=28,
            fg_color=COLOR_PANEL_BG,
            button_color=COLOR_CARD_BORDER
        )
        self.opt_bt_mode.set("Unconstrained (Bebas)")
        self.opt_bt_mode.pack(side="left", padx=4, pady=10)

        ctk.CTkLabel(
            top_ctrl,
            text="Sesi:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(8, 4), pady=10)

        self.opt_bt_session = ctk.CTkOptionMenu(
            top_ctrl,
            values=["Semua Sesi", "London & NY Only"],
            width=140,
            height=28,
            fg_color=COLOR_PANEL_BG,
            button_color=COLOR_CARD_BORDER
        )
        self.opt_bt_session.set("Semua Sesi")
        self.opt_bt_session.pack(side="left", padx=4, pady=10)

        self.btn_run_bt = ctk.CTkButton(
            top_ctrl,
            text="▶ JALANKAN SIMULASI",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            fg_color=COLOR_ACCENT_PURPLE,
            hover_color="#9333ea",
            text_color="#ffffff",
            height=28,
            command=self._on_click_run_backtest
        )
        self.btn_run_bt.pack(side="left", padx=10, pady=10)

        self.lbl_bt_status = ctk.CTkLabel(
            top_ctrl,
            text="Siap untuk simulasi",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_bt_status.pack(side="right", padx=12, pady=10)

        bt_body = ctk.CTkFrame(container, fg_color="transparent")
        bt_body.pack(fill="both", expand=True)

        # Upper row: Chart (Left) + Metrics (Right)
        upper_panel = ctk.CTkFrame(bt_body, fg_color="transparent", height=280)
        upper_panel.pack(fill="x", padx=0, pady=(0, 6))

        chart_box = ctk.CTkFrame(upper_panel, fg_color=COLOR_BG_DEEP, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        chart_box.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.fig_bt = Figure(figsize=(6.0, 2.6), dpi=100, facecolor=COLOR_BG_DEEP)
        self.ax_bt = self.fig_bt.add_subplot(111)
        self.ax_bt.set_facecolor(COLOR_BG_DEEP)
        self.ax_bt.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=8)
        self.ax_bt.grid(True, linestyle="--", alpha=0.12, color=COLOR_TEXT_SECONDARY)
        self.ax_bt.set_title("Kurva Pertumbuhan Modal (Equity Curve Backtest)", color=COLOR_TEXT_PRIMARY, fontsize=10, weight="bold")
        self.ax_bt.yaxis.tick_right()

        self.canvas_bt = FigureCanvasTkAgg(self.fig_bt, master=chart_box)
        self.canvas_bt.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

        # Card Metrik Hasil Backtest
        self.bt_metrics_frame = ctk.CTkFrame(upper_panel, width=320, fg_color=COLOR_PANEL_SUB, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        self.bt_metrics_frame.pack(side="right", fill="y")
        self.bt_metrics_frame.pack_propagate(False)

        ctk.CTkLabel(
            self.bt_metrics_frame,
            text="METRIK KINERJA INSTITUSIONAL",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_ACCENT_CYAN
        ).pack(anchor="w", padx=14, pady=(8, 4))

        self.bt_m_net_profit = self._create_hud_data_row(self.bt_metrics_frame, "Net Profit:", "$0.00", COLOR_TEXT_PRIMARY)
        self.bt_m_winrate = self._create_hud_data_row(self.bt_metrics_frame, "Win Rate:", "0.0%", COLOR_TEXT_PRIMARY)
        self.bt_m_trades = self._create_hud_data_row(self.bt_metrics_frame, "Total Transaksi:", "0", COLOR_TEXT_PRIMARY)
        self.bt_m_wins = self._create_hud_data_row(self.bt_metrics_frame, "Menang / Kalah:", "0 / 0", COLOR_TEXT_PRIMARY)
        self.bt_m_profit_factor = self._create_hud_data_row(self.bt_metrics_frame, "Profit Factor:", "0.00", COLOR_TEXT_PRIMARY)
        self.bt_m_max_dd = self._create_hud_data_row(self.bt_metrics_frame, "Max Drawdown:", "$0.00 (0.0%)", COLOR_TEXT_PRIMARY)
        self.bt_m_false_rate = self._create_hud_data_row(self.bt_metrics_frame, "False Signal Rate:", "0.0%", COLOR_TEXT_PRIMARY)
        self.bt_m_false_count = self._create_hud_data_row(self.bt_metrics_frame, "False Sigs / Traps:", "0", COLOR_TEXT_PRIMARY)
        self.bt_m_avg_mfe = self._create_hud_data_row(self.bt_metrics_frame, "Rata-rata Max R:", "0.00 R", COLOR_TEXT_PRIMARY)

        # Lower panel: Tabel Audit Sinyal & Riwayat Trade
        table_container = ctk.CTkFrame(bt_body, fg_color=COLOR_PANEL_SUB, corner_radius=8, border_width=1, border_color=COLOR_CARD_BORDER)
        table_container.pack(fill="both", expand=True)

        th_bar = ctk.CTkFrame(table_container, fg_color="transparent", height=26)
        th_bar.pack(fill="x", padx=12, pady=(6, 2))
        th_bar.pack_propagate(False)

        ctk.CTkLabel(
            th_bar,
            text="📋 AUDIT DETAIL SEMUA TRANSAKSI & SINYAL (HISTORIS)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10, weight="bold"),
            text_color=COLOR_ACCENT_GOLD
        ).pack(side="left")

        self.lbl_bt_table_summary = ctk.CTkLabel(
            th_bar,
            text="0 Transaksi Terdata",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9),
            text_color=COLOR_TEXT_SECONDARY
        )
        self.lbl_bt_table_summary.pack(side="right")

        self.bt_trades_scroll = ctk.CTkScrollableFrame(table_container, fg_color=COLOR_BG_DEEP, corner_radius=6)
        self.bt_trades_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 6))

    # =========================================================================
    # 4. BOTTOM LOG DOCK CONSOLE
    # =========================================================================
    def _build_bottom_log_dock(self, parent):
        log_box_frame = ctk.CTkFrame(
            parent,
            height=130,
            fg_color=COLOR_PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=COLOR_CARD_BORDER
        )
        log_box_frame.pack(fill="x", padx=0, pady=(0, 0))
        log_box_frame.pack_propagate(False)

        top_log_bar = ctk.CTkFrame(log_box_frame, fg_color="transparent", height=24)
        top_log_bar.pack(fill="x", padx=12, pady=(4, 2))

        ctk.CTkLabel(
            top_log_bar,
            text="TERMINAL AUDIT & TELEMETRY LOG",
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=COLOR_TEXT_SECONDARY
        ).pack(side="left")

        btn_clear = ctk.CTkButton(
            top_log_bar,
            text="Hapus Log",
            font=ctk.CTkFont(size=9),
            fg_color=COLOR_PANEL_SUB,
            hover_color=COLOR_CARD_BORDER,
            width=70,
            height=18,
            corner_radius=4,
            command=self._clear_logs
        )
        btn_clear.pack(side="right")

        self.txt_log = ctk.CTkTextbox(
            log_box_frame,
            font=ctk.CTkFont(family=FONT_MONO, size=9),
            fg_color=COLOR_BG_DEEP,
            text_color="#cbd5e1",
            corner_radius=4
        )
        self.txt_log.pack(fill="both", expand=True, padx=8, pady=(0, 6))

    # =========================================================================
    # 5. LOGGING & MT5 CONNECTION ENGINE
    # =========================================================================
    def log(self, text: str, level: str = "INFO"):
        prefix = {
            "INFO": " [INFO] ",
            "SUCCESS": " [PASS] ",
            "WARNING": " [WARN] ",
            "ERROR": " [FAIL] ",
            "SYSTEM": " [SYS] "
        }.get(level, " [LOG] ")
        now_str = datetime.now().strftime("%H:%M:%S")
        self.log_queue.put(f"[{now_str}]{prefix}{text}")

    def _clear_logs(self):
        self.txt_log.delete("1.0", "end")

    def _initial_mt5_connection(self):
        self.log("Menghubungkan ke terminal MetaTrader 5...", "SYSTEM")
        if self.client.initialize():
            self.is_mt5_connected = True
            import MetaTrader5 as mt5
            acc = mt5.account_info()
            if acc:
                self.lbl_account_info.configure(
                    text=f"MT5 #{acc.login} ({acc.name}) | {acc.server}"
                )
                self.kpi_equity.configure(text=f"${acc.equity:,.2f}")
                self.kpi_equity_sub.configure(text=f"Balance: ${acc.balance:,.2f} | Free: ${acc.margin_free:,.2f}")

            self.real_symbol = self.client.resolve_symbol(self.cfg.symbol)
            sym_info = self.client.get_symbol_info(self.real_symbol)
            if sym_info:
                self.point_size = sym_info.point
                self.digits = sym_info.digits
                self.tick_size = sym_info.trade_tick_size
                self.tick_value = sym_info.trade_tick_value
                self.stops_level = sym_info.trade_stops_level
                self.min_broker_dist = max(self.stops_level * self.point_size, 15 * self.point_size)

            self.log(f"MT5 Terhubung Sukses! Simbol: {self.real_symbol} | Point: {self.point_size} | Digits: {self.digits}", "SUCCESS")
            self._update_live_chart()
        else:
            self.log("Gagal menghubungkan MT5. Pastikan terminal MetaTrader 5 aktif & terlogin.", "ERROR")
            self.lbl_account_info.configure(text="MT5: Tidak Terhubung", text_color=COLOR_ACCENT_RED)

    # =========================================================================
    # 6. OPERATIONAL ACTIONS (START/STOP, PANIC CLOSE, INSTANT SCALPING)
    # =========================================================================
    def _on_click_toggle_bot(self):
        if not self.is_bot_running:
            if not self.is_mt5_connected:
                self.log("Tidak dapat memulai: MT5 belum terhubung.", "ERROR")
                return
            self.is_bot_running = True
            self.status_pill.configure(
                text="● RUNNING (ACTIVE)",
                fg_color="#064e3b",
                text_color=COLOR_ACCENT_GREEN,
                border_color="#059669"
            )
            self.btn_toggle_bot.configure(
                text="■ STOP AUTO TRADING",
                fg_color=COLOR_ACCENT_RED,
                hover_color="#be123c",
                text_color="#ffffff"
            )
            self.log(f"Robot Trading Triple EMA + SNR DIMULAI pada {self.real_symbol} [{self.cfg.timeframe}]!", "SUCCESS")
            threading.Thread(target=self._bot_thread_worker, daemon=True).start()
        else:
            self.is_bot_running = False
            self.status_pill.configure(
                text="○ STANDBY (PAUSED)",
                fg_color=COLOR_PANEL_SUB,
                text_color=COLOR_TEXT_SECONDARY,
                border_color=COLOR_CARD_BORDER
            )
            self.btn_toggle_bot.configure(
                text="▶ START AUTO TRADING",
                fg_color=COLOR_ACCENT_GREEN,
                hover_color="#059669",
                text_color="#000000"
            )
            self.log("Robot Trading Triple EMA DIHENTIKAN.", "WARNING")

    def _on_click_close_all(self):
        if not self.is_mt5_connected: return
        open_pos = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
        if not open_pos:
            self.log("Tidak ada posisi aktif yang perlu ditutup.", "INFO")
            return
        self.log(f"Menutup {len(open_pos)} posisi aktif...", "WARNING")
        for p in open_pos:
            self.client.close_position(p.ticket)
        self.log("Semua posisi berhasil ditutup.", "SUCCESS")
        self._refresh_orders_manually()

    def _on_click_manual_buy(self):
        if not self.is_mt5_connected: return
        lot = self.scalp_lot_selection
        self.log(f"[Manual Scalp] Membuka order BUY {lot} lot pada {self.real_symbol}...", "INFO")
        ticket = self.client.open_buy(self.real_symbol, lot, 0.0, 0.0, self.cfg.magic_number, "Manual_Buy")
        if ticket:
            self.log(f"[Manual Scalp] BUY Sukses dieksekusi! Ticket #{ticket}", "SUCCESS")
            self._refresh_orders_manually()

    def _on_click_manual_sell(self):
        if not self.is_mt5_connected: return
        lot = self.scalp_lot_selection
        self.log(f"[Manual Scalp] Membuka order SELL {lot} lot pada {self.real_symbol}...", "INFO")
        ticket = self.client.open_sell(self.real_symbol, lot, 0.0, 0.0, self.cfg.magic_number, "Manual_Sell")
        if ticket:
            self.log(f"[Manual Scalp] SELL Sukses dieksekusi! Ticket #{ticket}", "SUCCESS")
            self._refresh_orders_manually()

    # =========================================================================
    # 7. BOT WORKER THREAD (100% SINKRON DENGAN MAIN ENGINE)
    # =========================================================================
    def _bot_thread_worker(self):
        import MetaTrader5 as mt5

        while self.is_bot_running:
            try:
                eval_time = self.client.get_server_time(self.real_symbol) if getattr(self.cfg, 'time_filter_use_server_time', True) else datetime.now()

                # 1. Friday Auto-Close
                if self.risk_mgr.is_friday_auto_close_time(current_dt=eval_time):
                    open_pos = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
                    if open_pos:
                        self.log("[Friday Auto-Close] Menutup posisi sebelum penutupan pasar weekend...", "WARNING")
                        for p in open_pos:
                            self.client.close_position(p.ticket)

                # 2. Ambil Rates
                rates_count = getattr(self.cfg, 'history_bars_count', 350)
                rates_df = self.client.get_rates(self.real_symbol, self.cfg.timeframe, count=rates_count)
                if rates_df is None or len(rates_df) < 150:
                    time.sleep(self.cfg.tick_interval_sec)
                    continue

                rates_df = compute_all_indicators(
                    rates_df,
                    ema_fast=self.cfg.ema_fast_period,
                    ema_med=self.cfg.ema_med_period,
                    ema_slow=self.cfg.ema_slow_period,
                    atr_period=self.cfg.atr_period,
                    adx_period=self.cfg.adx_period
                )
                self.latest_rates_df = rates_df

                curr_bar = rates_df.iloc[-1]
                closed_bar = rates_df.iloc[-2]
                curr_bar_time = curr_bar['time']

                tick = self.client.get_current_tick(self.real_symbol)
                if tick is None:
                    time.sleep(self.cfg.tick_interval_sec)
                    continue

                ask = tick.ask
                bid = tick.bid
                curr_ema21 = curr_bar['ema21']
                curr_atr = closed_bar['atr']

                # 3. Kelola Posisi Aktif: Partial TP 50%, Auto BEP, & Trailing Stop
                open_pos = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
                active_tickets = {p.ticket for p in open_pos}
                self.partial_closed_tickets.intersection_update(active_tickets)

                for pos in open_pos:
                    ticket = pos.ticket
                    pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
                    open_price = pos.price_open
                    curr_sl = pos.sl
                    curr_tp = pos.tp
                    curr_price = bid if pos_type == "BUY" else ask
                    curr_vol = pos.volume

                    # A. Partial Close di 1:1 R
                    if getattr(self.cfg, 'use_partial_close', True) and (ticket not in self.partial_closed_tickets):
                        sym_info = self.client.get_symbol_info(self.real_symbol)
                        vmin = sym_info.volume_min if sym_info else 0.01
                        vstep = sym_info.volume_step if sym_info else 0.01
                        should_partial, vol_to_close = self.risk_mgr.evaluate_partial_close(
                            pos_type=pos_type,
                            open_price=open_price,
                            current_price=curr_price,
                            initial_sl=curr_sl,
                            current_volume=curr_vol,
                            initial_volume=curr_vol,
                            volume_min=vmin,
                            volume_step=vstep
                        )
                        if should_partial and vol_to_close > 0:
                            if self.client.close_position(ticket, volume=vol_to_close):
                                self.partial_closed_tickets.add(ticket)
                                self.log(f"[Partial TP] #{ticket} {pos_type} Ambil untung {vol_to_close} lot (50%) di 1:1 R!", "SUCCESS")
                                new_bep_sl = open_price + (self.cfg.be_lock_profit_points * self.point_size if pos_type == "BUY" else -self.cfg.be_lock_profit_points * self.point_size)
                                self.client.modify_position(ticket, new_bep_sl, curr_tp)
                                continue

                    # B. Auto BEP
                    new_bep = self.risk_mgr.evaluate_break_even(
                        pos_type=pos_type,
                        open_price=open_price,
                        current_sl=curr_sl,
                        current_price=curr_price,
                        point_size=self.point_size,
                        min_broker_dist=self.min_broker_dist
                    )
                    if new_bep is not None:
                        if self.client.modify_position(ticket, new_bep, curr_tp):
                            self.log(f"[Auto BEP] #{ticket} {pos_type} SL digeser ke BEP: {new_bep}", "SUCCESS")
                        continue

                    # C. Trailing Stop EMA 21
                    new_trail = self.risk_mgr.evaluate_trailing_stop(
                        pos_type=pos_type,
                        open_price=open_price,
                        current_sl=curr_sl,
                        current_price=curr_price,
                        ema21_val=curr_ema21,
                        atr_val=curr_atr,
                        point_size=self.point_size,
                        min_broker_dist=self.min_broker_dist
                    )
                    if new_trail is not None:
                        if self.client.modify_position(ticket, new_trail, curr_tp):
                            self.log(f"[Trailing Stop] #{ticket} {pos_type} Trailing SL diperbarui: {new_trail}", "INFO")

                # 4. Evaluasi Sinyal Bar Baru
                if self.last_bar_time is None:
                    self.last_bar_time = curr_bar_time

                if curr_bar_time != self.last_bar_time:
                    self.bars_since_last_trade += 1
                    self.log(f"Candle baru terbentuk ({curr_bar_time}). Mengevaluasi konfluensi setup...", "INFO")
                    self.after(0, self._update_live_chart)

                    acc = mt5.account_info()
                    equity = acc.equity if acc else 10000.0

                    if len(open_pos) >= self.cfg.max_open_positions:
                        self.last_bar_time = curr_bar_time
                        time.sleep(self.cfg.tick_interval_sec)
                        continue

                    if self.bars_since_last_trade < self.cfg.signal_cooldown_bars:
                        self.log(f"[Cooldown] Menunggu jeda candle ({self.bars_since_last_trade}/{self.cfg.signal_cooldown_bars}).", "INFO")
                        self.last_bar_time = curr_bar_time
                        time.sleep(self.cfg.tick_interval_sec)
                        continue

                    # Sinkronkan Circuit Breaker
                    closed_deals = self.client.get_daily_closed_deals(symbol=self.real_symbol, magic=self.cfg.magic_number)
                    self.risk_mgr.sync_daily_stats_from_deals(closed_deals)

                    cb_trig, cb_reason = self.risk_mgr.is_daily_circuit_breaker_triggered(equity)
                    if cb_trig:
                        self.log(f"[CIRCUIT BREAKER] {cb_reason}", "WARNING")
                        self.last_bar_time = curr_bar_time
                        time.sleep(self.cfg.tick_interval_sec)
                        continue

                    if not self.risk_mgr.is_trading_time_allowed(current_dt=eval_time):
                        self.last_bar_time = curr_bar_time
                        time.sleep(self.cfg.tick_interval_sec)
                        continue

                    if self.risk_mgr.is_friday_trading_restricted(current_dt=eval_time):
                        self.last_bar_time = curr_bar_time
                        time.sleep(self.cfg.tick_interval_sec)
                        continue

                    # Ambil HTF jika MTF aktif
                    htf_bullish = True
                    htf_bearish = True
                    if self.cfg.use_mtf_filter:
                        htf_rates = self.client.get_rates(self.real_symbol, self.cfg.htf_timeframe, count=120)
                        if htf_rates is not None and len(htf_rates) >= self.cfg.htf_ema_period:
                            htf_ema = calculate_ema(htf_rates['close'], self.cfg.htf_ema_period)
                            htf_close_1 = htf_rates['close'].iloc[-2]
                            htf_ema_1 = htf_ema.iloc[-2]
                            htf_bullish = htf_close_1 > htf_ema_1
                            htf_bearish = htf_close_1 < htf_ema_1

                    # Evaluasi Strategi Lengkap
                    sig = self.strategy.evaluate_signal(
                        df=rates_df,
                        current_ask=ask,
                        current_bid=bid,
                        point_size=self.point_size,
                        htf_bullish=htf_bullish,
                        htf_bearish=htf_bearish,
                        shift=-2
                    )
                    self.latest_signal_result = sig

                    if sig is not None:
                        self.log(f"[SIGNAL DETECTED] Setup {sig.signal_type} terkonfirmasi! Pattern: {sig.pattern_name}", "SUCCESS")

                        entry_price = ask if sig.signal_type == "BUY" else bid
                        sl_dist_pts = int(sig.sl_distance_points)

                        if sl_dist_pts > self.cfg.max_sl_points:
                            self.log(f"[Filter SL] Jarak SL ({sl_dist_pts} pts) melebihi batas aman ({self.cfg.max_sl_points} pts). Dibatalkan.", "WARNING")
                            self.last_bar_time = curr_bar_time
                            time.sleep(self.cfg.tick_interval_sec)
                            continue

                        lot_size = self.risk_mgr.calculate_lot_size(
                            equity=equity,
                            sl_distance_points=sl_dist_pts,
                            point_size=self.point_size,
                            tick_value=self.tick_value,
                            tick_size=self.tick_size
                        )

                        sym_info = self.client.get_symbol_info(self.real_symbol)
                        if sym_info:
                            lot_size = max(sym_info.volume_min, min(sym_info.volume_max, lot_size))
                            lot_size = round(math.floor(lot_size / sym_info.volume_step) * sym_info.volume_step, 2)

                        ticket = 0
                        comment_str = f"{self.cfg.order_comment}_{sig.pattern.name}"
                        if sig.signal_type == "BUY":
                            ticket = self.client.open_buy(self.real_symbol, lot_size, sig.stop_loss, sig.take_profit, self.cfg.magic_number, comment_str)
                        else:
                            ticket = self.client.open_sell(self.real_symbol, lot_size, sig.stop_loss, sig.take_profit, self.cfg.magic_number, comment_str)

                        if ticket:
                            self.log(f"[ORDER EXECUTED] #{ticket} {sig.signal_type} {lot_size} Lot @ {entry_price:.2f} | SL: {sig.stop_loss:.2f} | TP: {sig.take_profit:.2f}", "SUCCESS")
                            self.bars_since_last_trade = 0
                        else:
                            self.log(f"[EXECUTION ERROR] Gagal mengirim order {sig.signal_type} ke broker.", "ERROR")

                    self.last_bar_time = curr_bar_time

            except Exception as e:
                self.log(f"Bot error: {e}", "ERROR")

            time.sleep(self.cfg.tick_interval_sec)

    # =========================================================================
    # 8. DUAL-PANEL MATPLOTLIB CHART RENDERING (TRADINGVIEW DARK STYLE)
    # =========================================================================
    def _update_live_chart(self):
        if not self.is_mt5_connected: return

        rates_count = max(self.chart_bars_count + 60, 200)
        df = self.client.get_rates(self.real_symbol, self.cfg.timeframe, count=rates_count)
        if df is None or len(df) < 60: return

        df = compute_all_indicators(df, ema_fast=8, ema_med=21, ema_slow=125, atr_period=14, adx_period=14)
        self.latest_rates_df = df

        # Hitung SNR Snapshot
        snr_snap = self.snr_analyzer.analyze_snr(df, shift=-1)
        self.latest_snr_snapshot = snr_snap

        # Ambil subset lilin sesuai bar count yang dipilih
        plot_df = df.iloc[-self.chart_bars_count:].copy().reset_index(drop=True)
        n_bars = len(plot_df)
        x_bars = np.arange(n_bars)

        # Update lilin berjalan (candle 0 paling kanan) dengan tick harga realtime
        tick = self.client.get_current_tick(self.real_symbol)
        curr_price = None
        if tick and len(plot_df) > 0:
            curr_price = tick.bid
            plot_df.iloc[-1, plot_df.columns.get_loc('close')] = curr_price
            if curr_price > plot_df.iloc[-1]['high']:
                plot_df.iloc[-1, plot_df.columns.get_loc('high')] = curr_price
            if curr_price < plot_df.iloc[-1]['low']:
                plot_df.iloc[-1, plot_df.columns.get_loc('low')] = curr_price

        # ---------------------------------------------------------------------
        # SUBPLOT 1: CANDLESTICKS + TRIPLE EMA + SNR OVERLAY
        # ---------------------------------------------------------------------
        self.ax_main.clear()
        self.ax_main.set_facecolor(COLOR_BG_DEEP)
        self.ax_main.grid(True, linestyle="--", alpha=0.08, color=COLOR_TEXT_SECONDARY)
        self.ax_main.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=8)
        self.ax_main.yaxis.tick_right()
        self.ax_main.yaxis.set_label_position("right")
        self.ax_main.set_xticklabels([])

        up_mask = plot_df['close'] >= plot_df['open']
        down_mask = plot_df['close'] < plot_df['open']

        # Wicks (Sumbu Lilin)
        self.ax_main.vlines(x_bars[up_mask], plot_df['low'][up_mask], plot_df['high'][up_mask], color=COLOR_ACCENT_GREEN, linewidth=1.1, alpha=0.9)
        self.ax_main.vlines(x_bars[down_mask], plot_df['low'][down_mask], plot_df['high'][down_mask], color=COLOR_ACCENT_RED, linewidth=1.1, alpha=0.9)

        # Bodies (Badan Lilin)
        self.ax_main.bar(x_bars[up_mask], plot_df['close'][up_mask] - plot_df['open'][up_mask], bottom=plot_df['open'][up_mask], color=COLOR_ACCENT_GREEN, width=0.62, alpha=0.95)
        self.ax_main.bar(x_bars[down_mask], plot_df['open'][down_mask] - plot_df['close'][down_mask], bottom=plot_df['close'][down_mask], color=COLOR_ACCENT_RED, width=0.62, alpha=0.95)

        # Garis Triple EMA
        self.ax_main.plot(x_bars, plot_df['ema8'].values, color=COLOR_ACCENT_CYAN, linewidth=1.3, label="EMA 8 Fast")
        self.ax_main.plot(x_bars, plot_df['ema21'].values, color=COLOR_ACCENT_GOLD, linewidth=1.3, label="EMA 21 Pullback")
        self.ax_main.plot(x_bars, plot_df['ema125'].values, color=COLOR_ACCENT_PURPLE, linewidth=1.8, label="EMA 125 Baseline")

        # Shading Value Zone Cloud (EMA 8 - 21)
        self.ax_main.fill_between(x_bars, plot_df['ema8'].values, plot_df['ema21'].values, color=COLOR_ACCENT_GOLD, alpha=0.12)

        # Garis Dynamic Support & Resistance
        if snr_snap.nearest_resistance is not None:
            self.ax_main.axhline(snr_snap.nearest_resistance, color=COLOR_ACCENT_RED, linestyle="--", linewidth=1.2, alpha=0.85)
            self.ax_main.text(0.015, snr_snap.nearest_resistance, f" Major Res: ${snr_snap.nearest_resistance:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_RED, fontsize=7.5, weight="bold", va="bottom")

        if snr_snap.nearest_support is not None:
            self.ax_main.axhline(snr_snap.nearest_support, color=COLOR_ACCENT_GREEN, linestyle="--", linewidth=1.2, alpha=0.85)
            self.ax_main.text(0.015, snr_snap.nearest_support, f" Major Sup: ${snr_snap.nearest_support:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_GREEN, fontsize=7.5, weight="bold", va="bottom")

        if snr_snap.nearest_rbs is not None:
            self.ax_main.axhline(snr_snap.nearest_rbs, color=COLOR_ACCENT_CYAN, linestyle=":", linewidth=1.1, alpha=0.8)
            self.ax_main.text(0.015, snr_snap.nearest_rbs, f" RBS: ${snr_snap.nearest_rbs:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_CYAN, fontsize=7.5, va="bottom")

        if snr_snap.nearest_sbr is not None:
            self.ax_main.axhline(snr_snap.nearest_sbr, color=COLOR_ACCENT_ORANGE, linestyle=":", linewidth=1.1, alpha=0.8)
            self.ax_main.text(0.015, snr_snap.nearest_sbr, f" SBR: ${snr_snap.nearest_sbr:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_ORANGE, fontsize=7.5, va="bottom")

        # Garis Harga Realtime (TradingView Live Bid Price Line & Badge di Margin Kanan)
        if curr_price is not None:
            c_open_last = plot_df['open'].iloc[-1]
            bid_col = COLOR_ACCENT_GREEN if curr_price >= c_open_last else COLOR_ACCENT_RED
            self.ax_main.axhline(curr_price, color=bid_col, linestyle=":", linewidth=1.2, alpha=0.9)
            # Taruh badge harga tepat di sebelah kanan candle terakhir agar tidak menumpuk angka sumbu
            badge_x = n_bars + 0.8
            self.ax_main.text(
                badge_x, curr_price, f" {curr_price:.2f} ",
                color="#000000",
                backgroundcolor=bid_col,
                fontsize=8,
                weight="bold",
                va="center"
            )

        # Garis Posisi Aktif Terbuka (TradingView Style Entry, SL, TP Overlay di Sisi Kiri)
        open_pos_list = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
        if open_pos_list:
            for p in open_pos_list:
                p_type = "BUY" if p.type == 0 else "SELL"
                # Entry Line
                self.ax_main.axhline(p.price_open, color=COLOR_ACCENT_CYAN, linestyle="-.", linewidth=1.1, alpha=0.9)
                self.ax_main.text(0.015, p.price_open, f" #{p.ticket} {p_type} ENTRY: ${p.price_open:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_CYAN, fontsize=7, weight="bold", va="bottom")
                # SL Line
                if p.sl > 0:
                    self.ax_main.axhline(p.sl, color=COLOR_ACCENT_RED, linestyle="--", linewidth=1.2, alpha=0.9)
                    self.ax_main.text(0.015, p.sl, f" #{p.ticket} STOP LOSS: ${p.sl:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_RED, fontsize=7, weight="bold", va="bottom")
                # TP Line
                if p.tp > 0:
                    self.ax_main.axhline(p.tp, color=COLOR_ACCENT_GREEN, linestyle="--", linewidth=1.2, alpha=0.9)
                    self.ax_main.text(0.015, p.tp, f" #{p.ticket} TAKE PROFIT: ${p.tp:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_GREEN, fontsize=7, weight="bold", va="bottom")

        # Projected Entry Line jika belum ada open position
        if not open_pos_list:
            e8_last = plot_df['ema8'].iloc[-1]
            e21_last = plot_df['ema21'].iloc[-1]
            proj_entry = (e8_last + e21_last) / 2.0
            self.ax_main.axhline(proj_entry, color=COLOR_ACCENT_GOLD, linestyle=":", linewidth=1.1, alpha=0.75)
            self.ax_main.text(0.015, proj_entry, f" Projected Value Zone Entry: ${proj_entry:.2f}", transform=self.ax_main.get_yaxis_transform(), color=COLOR_ACCENT_GOLD, fontsize=7, va="bottom")

        # Hitung Countdown Waktu Penutupan Candle
        countdown_str = ""
        try:
            last_time = plot_df['time'].iloc[-1]
            if isinstance(last_time, (pd.Timestamp, datetime)):
                tf_secs = {"M1": 60, "M5": 300, "M15": 900, "M30": 1800, "H1": 3600, "H4": 14400}.get(self.cfg.timeframe, 300)
                now_dt = datetime.now()
                elapsed = (now_dt.timestamp() - last_time.timestamp()) % tf_secs
                rem_sec = max(0, int(tf_secs - elapsed))
                countdown_str = f" | ⏱ Candle Close: {rem_sec // 60:02d}:{rem_sec % 60:02d}"
        except Exception:
            pass

        # Judul & Legend Atas
        self.ax_main.set_title(
            f"{self.real_symbol} [{self.cfg.timeframe}] — Candlestick Pro + Triple EMA & SNR Overlay{countdown_str}",
            color=COLOR_TEXT_PRIMARY,
            fontsize=9,
            weight="bold",
            pad=8
        )
        self.ax_main.legend(loc="upper left", facecolor=COLOR_PANEL_BG, edgecolor=COLOR_CARD_BORDER, labelcolor=COLOR_TEXT_PRIMARY, fontsize=7)

        # ---------------------------------------------------------------------
        # SUBPLOT 2: ADX MOMENTUM OSCILLATOR
        # ---------------------------------------------------------------------
        self.ax_sub.clear()
        self.ax_sub.set_facecolor(COLOR_BG_DEEP)
        self.ax_sub.grid(True, linestyle="--", alpha=0.08, color=COLOR_TEXT_SECONDARY)
        self.ax_sub.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=7)
        self.ax_sub.yaxis.tick_right()
        self.ax_sub.yaxis.set_label_position("right")

        adx_vals = plot_df['adx'].values
        self.ax_sub.plot(x_bars, adx_vals, color=COLOR_ACCENT_BLUE, linewidth=1.3, label="ADX (14)")
        self.ax_sub.axhline(20.0, color=COLOR_ACCENT_GOLD, linestyle=":", linewidth=1.0, alpha=0.85)
        self.ax_sub.fill_between(x_bars, 20.0, adx_vals, where=(adx_vals >= 20.0), color=COLOR_ACCENT_GREEN, alpha=0.15)
        self.ax_sub.set_ylim(0, max(50, np.nanmax(adx_vals) + 5 if len(adx_vals) > 0 else 50))
        self.ax_sub.set_ylabel("ADX", color=COLOR_TEXT_SECONDARY, fontsize=8)

        # Format Label Waktu Sumbu X Bawah
        step = max(1, n_bars // 6)
        tick_locs = x_bars[::step]
        tick_labels = [plot_df['time'].iloc[i].strftime("%H:%M") if hasattr(plot_df['time'].iloc[i], 'strftime') else str(plot_df['time'].iloc[i])[-8:-3] for i in tick_locs]
        self.ax_sub.set_xticks(tick_locs)
        self.ax_sub.set_xticklabels(tick_labels, color=COLOR_TEXT_SECONDARY, fontsize=7)

        # Format Sumbu Angka Harga (Presisi 2 Desimal)
        self.ax_main.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
        self.ax_sub.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))

        # Terapkan batas sumbu (Pertahankan posisi geser/pan kustom pengguna atau Auto-Fit)
        if getattr(self, 'user_custom_chart_view', False) and getattr(self, 'saved_chart_xlim', None) is not None:
            self.ax_main.set_xlim(self.saved_chart_xlim)
            if getattr(self, 'saved_chart_ylim', None) is not None:
                self.ax_main.set_ylim(self.saved_chart_ylim)
            self.ax_sub.set_xlim(self.saved_chart_xlim)
        else:
            # Berikan ruang kosong 8 bar di sebelah kanan agar lilin dan badge harga tidak menabrak sumbu angka harga
            right_offset = 8.0
            self.ax_main.set_xlim(-0.5, n_bars - 1 + right_offset)
            self.ax_sub.set_xlim(-0.5, n_bars - 1 + right_offset)

            # Hitung batas vertikal harga dengan padding pengaman 8%
            y_hi = max(plot_df['high'].max(), plot_df['ema8'].max(), plot_df['ema21'].max())
            y_lo = min(plot_df['low'].min(), plot_df['ema8'].min(), plot_df['ema21'].min())
            y_pad = max(y_hi - y_lo, 1.0) * 0.08
            self.ax_main.set_ylim(y_lo - y_pad, y_hi + y_pad)

        # Berikan margin kanan 14% (right=0.86) agar angka sumbu harga tidak terpotong tepi jendela
        self.fig.subplots_adjust(left=0.03, right=0.86, top=0.94, bottom=0.08, hspace=0.08)
        self.canvas.draw()

    # =========================================================================
    # 9. GUI UPDATE LOOP (TIMER POLLING 1 DETIK)
    # =========================================================================
    def _gui_update_loop(self):
        # 1. Update Jam Multi-Zone
        now_local = datetime.now()
        now_utc = datetime.now(timezone.utc)
        server_dt = self.client.get_server_time(self.real_symbol) if self.is_mt5_connected else now_local
        self.lbl_clocks.configure(
            text=f"Server: {server_dt.strftime('%H:%M:%S')} | WIB: {now_local.strftime('%H:%M:%S')} | UTC: {now_utc.strftime('%H:%M:%S')}"
        )

        # 2. Flush antrian log
        while not self.log_queue.empty():
            msg = self.log_queue.get_nowait()
            self.txt_log.insert("end", msg + "\n")
            self.txt_log.see("end")

        # 3. Update Status Akun & KPI Cards
        if self.is_mt5_connected:
            try:
                import MetaTrader5 as mt5
                acc = mt5.account_info()
                if acc:
                    self.kpi_equity.configure(text=f"${acc.equity:,.2f}")
                    self.kpi_equity_sub.configure(text=f"Balance: ${acc.balance:,.2f} | Free: ${acc.margin_free:,.2f}")

                # Update Circuit Breaker Card
                loss_cnt = self.risk_mgr.daily_loss_count
                max_loss = self.cfg.max_daily_losses
                loss_amt = self.risk_mgr.daily_loss_amount
                cb_color = COLOR_ACCENT_GREEN if loss_cnt == 0 else (COLOR_ACCENT_GOLD if loss_cnt < max_loss else COLOR_ACCENT_RED)
                self.kpi_daily_loss.configure(text=f"{loss_cnt} / {max_loss} Loss", text_color=cb_color)
                self.kpi_daily_loss_sub.configure(text=f"Loss Terkumpul: -${loss_amt:.2f} (Batas: {max_loss})")

                # Update Live Tick & Spread Card
                tick = self.client.get_current_tick(self.real_symbol)
                if tick:
                    spread_pts = int(tick.spread) if hasattr(tick, 'spread') else int((tick.ask - tick.bid) / self.point_size)
                    self.kpi_spread.configure(text=f"{spread_pts} pts")
                    self.kpi_spread_sub.configure(text=f"Bid: {tick.bid:.2f} | Ask: {tick.ask:.2f}")

                # Update Posisi & Floating P/L
                open_pos = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
                total_floating = sum(p.profit for p in open_pos) if open_pos else 0.0
                total_vol = sum(p.volume for p in open_pos) if open_pos else 0.0

                pl_color = COLOR_ACCENT_GREEN if total_floating > 0 else (COLOR_ACCENT_RED if total_floating < 0 else COLOR_TEXT_PRIMARY)
                self.kpi_floating_pl.configure(text=f"{'+' if total_floating > 0 else ''}${total_floating:,.2f}", text_color=pl_color)
                self.kpi_floating_pl_sub.configure(text=f"{len(open_pos)} Posisi Aktif ({total_vol:.2f} Lot)")

                self.lbl_orders_summary.configure(
                    text=f"Total Posisi: {len(open_pos)} | Floating P/L: {'+' if total_floating > 0 else ''}${total_floating:,.2f} | Volume: {total_vol:.2f} Lot",
                    text_color=pl_color
                )

                self._render_open_orders_table(open_pos)

                # Update Confluence Radar HUD
                if self.latest_rates_df is not None and len(self.latest_rates_df) >= 30:
                    self._update_confluence_radar(self.latest_rates_df)

                # 4. Update Live Candlestick Chart secara Realtime Streaming
                try:
                    if self.tabview.get() == "📈 LIVE CHART & SNR RADAR":
                        mode_str = self.opt_chart_refresh.get()
                        if mode_str != "Pause":
                            interval = 1 if "1s" in mode_str else (2 if "2s" in mode_str else 5)
                            self.chart_tick_counter += 1
                            if self.chart_tick_counter >= interval:
                                self.chart_tick_counter = 0
                                self._update_live_chart()
                                # Animasi kedip badge streaming
                                cur_badge = self.lbl_live_badge.cget("text")
                                self.lbl_live_badge.configure(
                                    text="● LIVE" if cur_badge == "○ LIVE" else "○ LIVE",
                                    text_color=COLOR_ACCENT_GREEN
                                )
                        else:
                            self.lbl_live_badge.configure(text="⏸ PAUSED", text_color=COLOR_TEXT_MUTED)
                except Exception:
                    pass

            except Exception:
                pass

        self.after(1000, self._gui_update_loop)

    # -------------------------------------------------------------------------
    # CONFLUENCE RADAR EVALUATOR
    # -------------------------------------------------------------------------
    def _update_confluence_radar(self, df: pd.DataFrame):
        c0 = df.iloc[-2]
        c_prev = df.iloc[-3]
        score = 0
        total_score = 9

        # 1. Triple EMA Alignment (Bullish 8>21>125 atau Bearish 8<21<125)
        is_bull_trend = (c0['ema8'] > c0['ema21'] > c0['ema125']) and (c0['close'] > c0['ema125'])
        is_bear_trend = (c0['ema8'] < c0['ema21'] < c0['ema125']) and (c0['close'] < c0['ema125'])

        if is_bull_trend:
            score += 1
            self.chk_ema.configure(text="[✓] BULLISH (8>21>125)", text_color=COLOR_ACCENT_GREEN)
        elif is_bear_trend:
            score += 1
            self.chk_ema.configure(text="[✓] BEARISH (8<21<125)", text_color=COLOR_ACCENT_RED)
        else:
            self.chk_ema.configure(text="[✗] CHOPPY / TRANSITION", text_color=COLOR_TEXT_MUTED)

        # 2. Value Zone Pullback
        vz_high = max(c0['ema8'], c0['ema21'])
        vz_low = min(c0['ema8'], c0['ema21'])
        in_vz = (c0['low'] <= vz_high) and (c0['high'] >= vz_low)
        if in_vz:
            score += 1
            self.chk_value_zone.configure(text="[✓] IN VALUE ZONE", text_color=COLOR_ACCENT_GOLD)
        else:
            self.chk_value_zone.configure(text="[✗] OUTSIDE ZONE", text_color=COLOR_TEXT_MUTED)

        # 3. Fibonacci Golden Pocket (OTE 50% - 78.6%)
        if getattr(self.cfg, 'use_fibo_golden_zone', True):
            if is_bull_trend:
                in_fibo = is_in_fibo_golden_zone_buy(df, lookback=self.cfg.fibo_lookback_bars, min_retrace=self.cfg.fibo_min_retrace, max_retrace=self.cfg.fibo_max_retrace, shift=-2)
                if in_fibo:
                    score += 1
                    self.chk_fibo.configure(text="[✓] IN OTE (50-78.6%)", text_color=COLOR_ACCENT_GOLD)
                else:
                    self.chk_fibo.configure(text="[✗] OUTSIDE OTE", text_color=COLOR_TEXT_MUTED)
            elif is_bear_trend:
                in_fibo = is_in_fibo_golden_zone_sell(df, lookback=self.cfg.fibo_lookback_bars, min_retrace=self.cfg.fibo_min_retrace, max_retrace=self.cfg.fibo_max_retrace, shift=-2)
                if in_fibo:
                    score += 1
                    self.chk_fibo.configure(text="[✓] IN OTE (50-78.6%)", text_color=COLOR_ACCENT_GOLD)
                else:
                    self.chk_fibo.configure(text="[✗] OUTSIDE OTE", text_color=COLOR_TEXT_MUTED)
            else:
                self.chk_fibo.configure(text="[✗] SCANNING...", text_color=COLOR_TEXT_MUTED)
        else:
            score += 1
            self.chk_fibo.configure(text="[✓] FILTER OFF", text_color=COLOR_TEXT_SECONDARY)

        # 4. RSI 14 Momentum (Healthy 45-70 Buy / 30-55 Sell)
        rsi_val = float(c0.get('rsi', 50.0))
        if getattr(self.cfg, 'use_rsi_filter', True):
            if is_bull_trend:
                if self.cfg.rsi_buy_min <= rsi_val <= self.cfg.rsi_buy_max:
                    score += 1
                    self.chk_rsi.configure(text=f"[✓] HEALTHY ({rsi_val:.1f})", text_color=COLOR_ACCENT_GREEN)
                else:
                    self.chk_rsi.configure(text=f"[✗] {rsi_val:.1f} (NOT 45-70)", text_color=COLOR_ACCENT_RED)
            elif is_bear_trend:
                if self.cfg.rsi_sell_min <= rsi_val <= self.cfg.rsi_sell_max:
                    score += 1
                    self.chk_rsi.configure(text=f"[✓] HEALTHY ({rsi_val:.1f})", text_color=COLOR_ACCENT_RED)
                else:
                    self.chk_rsi.configure(text=f"[✗] {rsi_val:.1f} (NOT 30-55)", text_color=COLOR_ACCENT_RED)
            else:
                self.chk_rsi.configure(text=f"[✗] RSI {rsi_val:.1f}", text_color=COLOR_TEXT_MUTED)
        else:
            score += 1
            self.chk_rsi.configure(text=f"[✓] OFF ({rsi_val:.1f})", text_color=COLOR_TEXT_SECONDARY)

        # 5. Candlestick Pattern Trigger
        bp = detect_bullish_pattern(df, shift=-2)
        sp = detect_bearish_pattern(df, shift=-2)
        if bp != CandlePattern.NONE:
            score += 1
            self.chk_pattern.configure(text=f"[✓] {get_pattern_name(bp)}", text_color=COLOR_ACCENT_GREEN)
        elif sp != CandlePattern.NONE:
            score += 1
            self.chk_pattern.configure(text=f"[✓] {get_pattern_name(sp)}", text_color=COLOR_ACCENT_RED)
        else:
            self.chk_pattern.configure(text="[✗] NONE DETECTED", text_color=COLOR_TEXT_MUTED)

        # 6. Market Structure (HH-HL atau LH-LL)
        struct = self.strategy.structure_analyzer.analyze_structure(df, shift=-2)
        if struct == MarketStructure.BULLISH_HH_HL:
            score += 1
            self.chk_structure.configure(text="[✓] BULLISH (HH-HL)", text_color=COLOR_ACCENT_GREEN)
        elif struct == MarketStructure.BEARISH_LH_LL:
            score += 1
            self.chk_structure.configure(text="[✓] BEARISH (LH-LL)", text_color=COLOR_ACCENT_RED)
        else:
            self.chk_structure.configure(text="[✗] RANGE / CHOP", text_color=COLOR_TEXT_MUTED)

        # 7. ADX Momentum (>= 20)
        adx_val = c0.get('adx', 0.0)
        if adx_val >= self.cfg.min_adx_level:
            score += 1
            self.chk_adx.configure(text=f"[✓] STRONG ({adx_val:.1f})", text_color=COLOR_ACCENT_GREEN)
        else:
            self.chk_adx.configure(text=f"[✗] WEAK ({adx_val:.1f})", text_color=COLOR_TEXT_MUTED)

        # 8. SNR Obstacle Clearance
        snap = self.latest_snr_snapshot
        if snap:
            if snap.nearest_resistance: self.hud_res.configure(text=f"${snap.nearest_resistance:.2f}")
            if snap.nearest_support: self.hud_sup.configure(text=f"${snap.nearest_support:.2f}")
            rbs_info = "None"
            if snap.nearest_rbs: rbs_info = f"RBS: ${snap.nearest_rbs:.2f}"
            elif snap.nearest_sbr: rbs_info = f"SBR: ${snap.nearest_sbr:.2f}"
            self.hud_role_rev.configure(text=rbs_info)

            # Check obstacle
            if is_bull_trend and snap.nearest_resistance:
                dist = snap.nearest_resistance - c0['close']
                if dist > 50 * self.point_size:
                    score += 1
                    self.chk_snr_clear.configure(text=f"[✓] CLEAR (+${dist:.2f})", text_color=COLOR_ACCENT_GREEN)
                else:
                    self.chk_snr_clear.configure(text="[✗] RESISTANCE AHEAD", text_color=COLOR_ACCENT_RED)
            elif is_bear_trend and snap.nearest_support:
                dist = c0['close'] - snap.nearest_support
                if dist > 50 * self.point_size:
                    score += 1
                    self.chk_snr_clear.configure(text=f"[✓] CLEAR (-${dist:.2f})", text_color=COLOR_ACCENT_GREEN)
                else:
                    self.chk_snr_clear.configure(text="[✗] SUPPORT AHEAD", text_color=COLOR_ACCENT_RED)
            else:
                score += 1
                self.chk_snr_clear.configure(text="[✓] CLEAR TO TARGET", text_color=COLOR_ACCENT_GREEN)
        else:
            self.chk_snr_clear.configure(text="[✗] EVALUATING", text_color=COLOR_TEXT_MUTED)

        # 9. HTF Macro Confluence
        if not self.cfg.use_mtf_filter:
            score += 1
            self.chk_htf.configure(text="[✓] FILTER DISABLED", text_color=COLOR_TEXT_SECONDARY)
        else:
            self.chk_htf.configure(text="[✓] MACRO ALIGNED", text_color=COLOR_ACCENT_GREEN)

        # Update Score Banner
        bias_text = "BULLISH SETUP DETECTED" if is_bull_trend else ("BEARISH SETUP DETECTED" if is_bear_trend else "WAITING PULLBACK SETUP")
        bias_color = COLOR_ACCENT_GREEN if is_bull_trend else (COLOR_ACCENT_RED if is_bear_trend else COLOR_TEXT_SECONDARY)
        self.lbl_overall_bias.configure(text=bias_text, text_color=bias_color)

        prob_tag = "ULTRA HIGH" if score >= 6 else ("GOOD CONFLUENCE" if score >= 4 else "LOW PROBABILITY")
        gauge_color = COLOR_ACCENT_GREEN if score >= 6 else (COLOR_ACCENT_GOLD if score >= 4 else COLOR_TEXT_MUTED)
        self.lbl_score_gauge.configure(text=f"Score: {score} / {total_score} Confluences ({prob_tag})", text_color=gauge_color)

        # 8. Update Live Target & Signal Radar (Entry, SL, TP, Partial 50%)
        tick = self.client.get_current_tick(self.real_symbol)
        curr_bid = tick.bid if tick else c0['close']
        curr_ask = tick.ask if tick else c0['close']

        # Cek jika ada posisi terbuka di MT5
        open_pos_list = self.client.get_open_positions(symbol=self.real_symbol, magic=self.cfg.magic_number)
        if open_pos_list:
            pos0 = open_pos_list[0]
            p_type = "BUY" if pos0.type == 0 else "SELL"
            p_col = COLOR_ACCENT_GREEN if p_type == "BUY" else COLOR_ACCENT_RED
            self.lbl_sig_badge.configure(text=f"● LIVE {p_type} (#{pos0.ticket})", text_color=p_col)
            self.lbl_sig_entry.configure(text=f"${pos0.price_open:.2f}", text_color=COLOR_ACCENT_CYAN)
            sl_str = f"${pos0.sl:.2f}" if pos0.sl > 0 else "None"
            tp_str = f"${pos0.tp:.2f}" if pos0.tp > 0 else "None"
            self.lbl_sig_sl.configure(text=sl_str, text_color=COLOR_ACCENT_RED)
            self.lbl_sig_tp.configure(text=tp_str, text_color=COLOR_ACCENT_GREEN)

            # Hitung target 1:1 R partial
            if pos0.sl > 0:
                dist_sl = abs(pos0.price_open - pos0.sl)
                part_target = pos0.price_open + dist_sl if p_type == "BUY" else pos0.price_open - dist_sl
                self.lbl_sig_partial.configure(text=f"${part_target:.2f} (Lock BEP)", text_color=COLOR_ACCENT_GOLD)
            else:
                self.lbl_sig_partial.configure(text="No SL Set", text_color=COLOR_TEXT_MUTED)

        elif is_bull_trend:
            sl_p, tp_p, dist_pts = self.strategy.calculate_sl_tp("BUY", curr_ask, df, self.point_size, shift=-2)
            has_pattern = (bp != CandlePattern.NONE)
            badge_txt = f"🟢 BUY READY ({get_pattern_name(bp)})" if has_pattern else "🟡 MONITORING BUY PULLBACK"
            badge_col = COLOR_ACCENT_GREEN if has_pattern else COLOR_ACCENT_GOLD
            self.lbl_sig_badge.configure(text=badge_txt, text_color=badge_col)
            self.lbl_sig_entry.configure(text=f"${curr_ask:.2f} (Ask)", text_color=COLOR_TEXT_PRIMARY)
            self.lbl_sig_sl.configure(text=f"${sl_p:.2f} (-{int(dist_pts)} pts)", text_color=COLOR_ACCENT_RED)
            self.lbl_sig_tp.configure(text=f"${tp_p:.2f} (+{int(dist_pts * self.cfg.risk_reward_ratio)} pts)", text_color=COLOR_ACCENT_GREEN)
            part_p = curr_ask + (dist_pts * self.point_size)
            self.lbl_sig_partial.configure(text=f"${part_p:.2f} (+{int(dist_pts)} pts)", text_color=COLOR_ACCENT_GOLD)

        elif is_bear_trend:
            sl_p, tp_p, dist_pts = self.strategy.calculate_sl_tp("SELL", curr_bid, df, self.point_size, shift=-2)
            has_pattern = (sp != CandlePattern.NONE)
            badge_txt = f"🔴 SELL READY ({get_pattern_name(sp)})" if has_pattern else "🟠 MONITORING SELL PULLBACK"
            badge_col = COLOR_ACCENT_RED if has_pattern else COLOR_ACCENT_ORANGE
            self.lbl_sig_badge.configure(text=badge_txt, text_color=badge_col)
            self.lbl_sig_entry.configure(text=f"${curr_bid:.2f} (Bid)", text_color=COLOR_TEXT_PRIMARY)
            self.lbl_sig_sl.configure(text=f"${sl_p:.2f} (+{int(dist_pts)} pts)", text_color=COLOR_ACCENT_RED)
            self.lbl_sig_tp.configure(text=f"${tp_p:.2f} (-{int(dist_pts * self.cfg.risk_reward_ratio)} pts)", text_color=COLOR_ACCENT_GREEN)
            part_p = curr_bid - (dist_pts * self.point_size)
            self.lbl_sig_partial.configure(text=f"${part_p:.2f} (-{int(dist_pts)} pts)", text_color=COLOR_ACCENT_GOLD)

        else:
            self.lbl_sig_badge.configure(text="⚪ SCANNING PULLBACK", text_color=COLOR_TEXT_MUTED)
            self.lbl_sig_entry.configure(text="None", text_color=COLOR_TEXT_MUTED)
            self.lbl_sig_sl.configure(text="None", text_color=COLOR_TEXT_MUTED)
            self.lbl_sig_tp.configure(text="None", text_color=COLOR_TEXT_MUTED)
            self.lbl_sig_partial.configure(text="None", text_color=COLOR_TEXT_MUTED)

    # -------------------------------------------------------------------------
    # TABEL POSISI AKTIF DENGAN TOMBOL AKSI CEPAT (+BEP, PARTIAL 50%, CLOSE)
    # -------------------------------------------------------------------------
    def _render_open_orders_table(self, positions):
        for w in self.orders_scroll.winfo_children():
            w.destroy()

        if not positions:
            lbl = ctk.CTkLabel(
                self.orders_scroll,
                text="Tidak ada posisi aktif saat ini.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=COLOR_TEXT_SECONDARY
            )
            lbl.pack(pady=40)
            return

        import MetaTrader5 as mt5
        header = ctk.CTkFrame(self.orders_scroll, fg_color=COLOR_PANEL_SUB, height=32, corner_radius=6)
        header.pack(fill="x", padx=4, pady=(2, 4))
        
        cols = [
            ("Ticket", 85), ("Type", 75), ("Volume", 65), ("Open Price", 95), 
            ("Current", 95), ("SL", 90), ("TP", 90), ("Floating P/L", 110), ("Quick Actions", 180)
        ]
        for col_name, w_val in cols:
            ctk.CTkLabel(
                header,
                text=col_name,
                width=w_val,
                font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
                text_color=COLOR_TEXT_SECONDARY
            ).pack(side="left", padx=4)

        for pos in positions:
            row = ctk.CTkFrame(self.orders_scroll, fg_color=COLOR_PANEL_BG, height=36, corner_radius=6, border_width=1, border_color=COLOR_CARD_BORDER)
            row.pack(fill="x", padx=4, pady=2)

            pos_type = "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL"
            pos_col = COLOR_ACCENT_GREEN if pos_type == "BUY" else COLOR_ACCENT_RED
            p_col = COLOR_ACCENT_GREEN if pos.profit >= 0 else COLOR_ACCENT_RED

            ctk.CTkLabel(row, text=f"#{pos.ticket}", width=85, font=ctk.CTkFont(family=FONT_MONO, size=9)).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=pos_type, width=75, font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"), text_color=pos_col).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{pos.volume:.2f}", width=65, font=ctk.CTkFont(family=FONT_MONO, size=9)).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{pos.price_open:.2f}", width=95, font=ctk.CTkFont(family=FONT_MONO, size=9)).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{pos.price_current:.2f}", width=95, font=ctk.CTkFont(family=FONT_MONO, size=9)).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{pos.sl:.2f}", width=90, font=ctk.CTkFont(family=FONT_MONO, size=9)).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"{pos.tp:.2f}", width=90, font=ctk.CTkFont(family=FONT_MONO, size=9)).pack(side="left", padx=4)

            pl_text = f"{'+' if pos.profit > 0 else ''}${pos.profit:,.2f}"
            ctk.CTkLabel(row, text=pl_text, width=110, font=ctk.CTkFont(family=FONT_MONO, size=10, weight="bold"), text_color=p_col).pack(side="left", padx=4)

            # Action Buttons Box
            btn_box = ctk.CTkFrame(row, fg_color="transparent", width=180)
            btn_box.pack(side="left", padx=4)

            # Tombol +BEP
            btn_bep = ctk.CTkButton(
                btn_box,
                text="+BEP",
                width=50,
                height=22,
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=COLOR_PANEL_SUB,
                hover_color=COLOR_BORDER_FOCUS,
                command=lambda t=pos.ticket, p_op=pos.price_open, p_tp=pos.tp, pt=pos_type: self._manual_lock_bep(t, p_op, p_tp, pt)
            )
            btn_bep.pack(side="left", padx=(0, 4))

            # Tombol Partial 50%
            btn_partial = ctk.CTkButton(
                btn_box,
                text="Part 50%",
                width=58,
                height=22,
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=COLOR_PANEL_SUB,
                hover_color=COLOR_BORDER_FOCUS,
                command=lambda t=pos.ticket, v=pos.volume: self.client.close_position(t, volume=round(v*0.5, 2))
            )
            btn_partial.pack(side="left", padx=(0, 4))

            # Tombol Close Full
            btn_close = ctk.CTkButton(
                btn_box,
                text="CLOSE",
                width=52,
                height=22,
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color="#881337",
                hover_color="#9f1239",
                command=lambda t=pos.ticket: self.client.close_position(t)
            )
            btn_close.pack(side="left")

    def _manual_lock_bep(self, ticket: int, open_price: float, curr_tp: float, pos_type: str):
        buffer = self.cfg.be_lock_profit_points * self.point_size
        new_sl = open_price + buffer if pos_type == "BUY" else open_price - buffer
        if self.client.modify_position(ticket, new_sl, curr_tp):
            self.log(f"[Manual BEP] #{ticket} SL dikunci ke BEP + buffer ({new_sl:.2f})", "SUCCESS")

    # =========================================================================
    # 10. BACKTEST SIMULATOR EXECUTION
    # =========================================================================
    def _on_click_run_backtest(self):
        if not self.is_mt5_connected:
            self.log("MT5 tidak terhubung untuk simulasi!", "ERROR")
            return

        bars_str = self.opt_bars_count.get()
        count = int(bars_str.split()[0])
        
        mode_val = "UNCONSTRAINED" if "Unconstrained" in self.opt_bt_mode.get() else "SINGLE_POSITION"
        session_val = "LONDON_NY" if "London" in self.opt_bt_session.get() else "ALL"
        self.cfg.backtest_mode = mode_val
        self.cfg.xau_session_filter = session_val

        self.lbl_bt_status.configure(text=f"Simulasi ({mode_val})...", text_color=COLOR_ACCENT_GOLD)
        self.btn_run_bt.configure(state="disabled")
        threading.Thread(target=self._run_backtest_thread, args=(count,), daemon=True).start()

    def _run_backtest_thread(self, count: int):
        try:
            self.log(f"[Backtester] Mengambil {count} candle dari MT5 ({self.real_symbol} {self.cfg.timeframe})...", "SYSTEM")
            rates_df = self.client.get_rates(self.real_symbol, self.cfg.timeframe, count=count)
            if rates_df is None or len(rates_df) == 0:
                self.log("Gagal mengambil data historis dari MT5.", "ERROR")
                self.after(0, lambda: self.lbl_bt_status.configure(text="Gagal mengambil data", text_color=COLOR_ACCENT_RED))
                return

            bt = TripleEmaBacktester(self.cfg, initial_balance=10000.0, point_size=self.point_size)
            report = bt.run(rates_df)

            self.after(0, lambda: self._display_backtest_results(bt, report))
            self.log(f"[Backtester] Selesai! Win Rate: {report.get('win_rate_percent', 0)}% | False Sig: {report.get('false_signal_rate_percent', 0)}% | Profit: ${report.get('net_profit', 0):,.2f}", "SUCCESS")
        except Exception as e:
            self.log(f"Error backtest: {e}", "ERROR")
        finally:
            self.after(0, lambda: self.btn_run_bt.configure(state="normal"))

    def _display_backtest_results(self, bt: TripleEmaBacktester, report: Dict[str, Any]):
        self.lbl_bt_status.configure(text="Simulasi Selesai!", text_color=COLOR_ACCENT_GREEN)

        profit_col = COLOR_ACCENT_GREEN if report['net_profit'] >= 0 else COLOR_ACCENT_RED
        self.bt_m_net_profit.configure(text=f"${report['net_profit']:,.2f}", text_color=profit_col)
        self.bt_m_winrate.configure(text=f"{report['win_rate_percent']}%", text_color=COLOR_ACCENT_GREEN if report['win_rate_percent'] >= 55 else COLOR_ACCENT_RED)
        self.bt_m_trades.configure(text=str(report['total_trades']))
        self.bt_m_wins.configure(text=f"{report['winning_trades']} Win / {report['losing_trades']} Loss ({report.get('bep_trades', 0)} BEP)")
        self.bt_m_profit_factor.configure(text=str(report['profit_factor']))
        self.bt_m_max_dd.configure(text=f"${report['max_drawdown_amount']:,.2f} ({report['max_drawdown_percent']}%)", text_color=COLOR_ACCENT_GOLD)

        # Telemetri False Signal
        false_pct = report.get('false_signal_rate_percent', 0.0)
        false_col = COLOR_ACCENT_GREEN if false_pct <= 15.0 else COLOR_ACCENT_RED
        self.bt_m_false_rate.configure(text=f"{false_pct}%", text_color=false_col)
        self.bt_m_false_count.configure(text=f"{report.get('false_signals_count', 0)} ({report.get('normal_losses_count', 0)} Normal)")
        self.bt_m_avg_mfe.configure(text=f"{report.get('avg_mfe_r', 0.0):.2f} R")

        # Expectancy
        total_tr = report['total_trades']
        exp_val = report['net_profit'] / total_tr if total_tr > 0 else 0.0

        # Plot Kurva Modal
        self.ax_bt.clear()
        self.ax_bt.set_facecolor(COLOR_BG_DEEP)
        self.ax_bt.grid(True, linestyle="--", alpha=0.12, color=COLOR_TEXT_SECONDARY)
        self.ax_bt.tick_params(colors=COLOR_TEXT_SECONDARY, labelsize=8)
        self.ax_bt.yaxis.tick_right()

        eq = bt.equity_curve
        x_bars = np.arange(len(eq))
        eq_arr = np.array(eq)

        self.ax_bt.plot(x_bars, eq_arr, color=COLOR_ACCENT_GREEN if report['net_profit'] >= 0 else COLOR_ACCENT_RED, linewidth=1.5)
        self.ax_bt.fill_between(x_bars, bt.initial_balance, eq_arr, where=(eq_arr >= bt.initial_balance), color=COLOR_ACCENT_GREEN, alpha=0.15)
        self.ax_bt.fill_between(x_bars, bt.initial_balance, eq_arr, where=(eq_arr < bt.initial_balance), color=COLOR_ACCENT_RED, alpha=0.15)
        self.ax_bt.axhline(bt.initial_balance, color=COLOR_TEXT_MUTED, linestyle=":", linewidth=1.0)
        self.ax_bt.set_title(f"Equity Curve: Net Profit ${report['net_profit']:,.2f} ({report['win_rate_percent']}% Win Rate | False Sig: {false_pct}%)", color=COLOR_TEXT_PRIMARY, fontsize=9, weight="bold")
        self.fig_bt.tight_layout()
        self.canvas_bt.draw()

        # Render Tabel Riwayat Trade
        for widget in self.bt_trades_scroll.winfo_children():
            widget.destroy()

        trades_list = report.get('trades_list', [])
        self.lbl_bt_table_summary.configure(text=f"{len(trades_list)} Transaksi Terdata")

        if not trades_list:
            ctk.CTkLabel(
                self.bt_trades_scroll,
                text="Tidak ada transaksi yang dieksekusi pada rentang data ini.",
                font=ctk.CTkFont(family=FONT_FAMILY, size=10),
                text_color=COLOR_TEXT_SECONDARY
            ).pack(pady=20)
            return

        # Header Bar
        header_frame = ctk.CTkFrame(self.bt_trades_scroll, fg_color=COLOR_PANEL_SUB, height=26, corner_radius=4)
        header_frame.pack(fill="x", padx=2, pady=(2, 4))
        header_frame.pack_propagate(False)

        cols = [
            ("#", 35),
            ("Waktu Buka", 115),
            ("Tipe", 50),
            ("Pola Candlestick", 160),
            ("Sesi", 95),
            ("Entry", 70),
            ("SL", 70),
            ("TP", 70),
            ("Exit", 70),
            ("Profit ($)", 75),
            ("R:R", 50),
            ("Status", 95)
        ]

        for title, width in cols:
            ctk.CTkLabel(
                header_frame,
                text=title,
                width=width,
                font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
                text_color=COLOR_TEXT_SECONDARY,
                anchor="center"
            ).pack(side="left", padx=2)

        # Populate Rows (Tampilkan 60 trade terbaru)
        for t in trades_list[-60:]:
            row_frame = ctk.CTkFrame(self.bt_trades_scroll, fg_color=COLOR_CARD_BG, height=24, corner_radius=3)
            row_frame.pack(fill="x", padx=2, pady=1)
            row_frame.pack_propagate(False)

            status = t.get("status", "UNKNOWN")
            if status == "WIN":
                st_color = COLOR_ACCENT_GREEN
                st_text = "WIN"
            elif status == "BEP":
                st_color = COLOR_ACCENT_CYAN
                st_text = "BEP"
            elif status == "FALSE_SIGNAL":
                st_color = COLOR_ACCENT_RED
                st_text = "FALSE SIG"
            else:
                st_color = COLOR_ACCENT_GOLD
                st_text = "LOSS"

            p_val = t.get("profit", 0.0)
            p_color = COLOR_ACCENT_GREEN if p_val > 0 else (COLOR_ACCENT_RED if p_val < 0 else COLOR_TEXT_PRIMARY)
            t_type = t.get("type", "BUY")
            type_color = COLOR_ACCENT_GREEN if t_type == "BUY" else COLOR_ACCENT_RED

            row_data = [
                (str(t.get("ticket", "")), 35, COLOR_TEXT_MUTED),
                (str(t.get("time", ""))[:16], 115, COLOR_TEXT_SECONDARY),
                (t_type, 50, type_color),
                (str(t.get("pattern", "")), 160, COLOR_TEXT_PRIMARY),
                (str(t.get("session", "")), 95, COLOR_ACCENT_GOLD),
                (f"{t.get('entry', 0):.2f}", 70, COLOR_TEXT_PRIMARY),
                (f"{t.get('sl', 0):.2f}", 70, COLOR_TEXT_MUTED),
                (f"{t.get('tp', 0):.2f}", 70, COLOR_TEXT_MUTED),
                (f"{t.get('exit', 0):.2f}", 70, COLOR_TEXT_PRIMARY),
                (f"${p_val:+,.2f}", 75, p_color),
                (f"{t.get('r_multiple', 0):+.1f}R", 50, COLOR_TEXT_SECONDARY),
                (st_text, 95, st_color)
            ]

            for val, width, col in row_data:
                ctk.CTkLabel(
                    row_frame,
                    text=val,
                    width=width,
                    font=ctk.CTkFont(family=FONT_FAMILY, size=9),
                    text_color=col,
                    anchor="center"
                ).pack(side="left", padx=2)

    # =========================================================================
    # 11. PARAMETER SYNC & DISK PERSISTENCE
    # =========================================================================
    def _on_change_timeframe(self, choice):
        self.cfg.timeframe = choice
        self.log(f"Timeframe diubah ke: {choice}", "INFO")
        for t, btn in self.tf_pills.items():
            if t == choice:
                btn.configure(fg_color=COLOR_ACCENT_CYAN, text_color="#000000")
            else:
                btn.configure(fg_color=COLOR_PANEL_BG, text_color=COLOR_TEXT_PRIMARY)
        self._update_live_chart()

    def _on_change_lot_mode(self, choice):
        self.cfg.lot_mode = choice

    def _sync_switches(self):
        self.cfg.use_snr_filter = bool(self.switch_snr.get())
        self.cfg.use_smc_filter = bool(self.switch_smc.get())
        self.cfg.use_partial_close = bool(self.switch_partial.get())
        self.cfg.use_break_even = bool(self.switch_bep.get())
        self.cfg.use_trailing_stop = bool(self.switch_trailing.get())
        self.cfg.use_daily_loss_limit = bool(self.switch_cb.get())
        self.cfg.use_friday_close = bool(self.switch_friday.get())
        self.cfg.use_mtf_filter = bool(self.switch_mtf.get())
        if hasattr(self, 'switch_shock'):
            self.cfg.use_fundamental_shock_filter = bool(self.switch_shock.get())
        if hasattr(self, 'switch_fibo'):
            self.cfg.use_fibo_golden_zone = bool(self.switch_fibo.get())
        if hasattr(self, 'switch_rsi'):
            self.cfg.use_rsi_filter = bool(self.switch_rsi.get())
        if hasattr(self, 'switch_fvg'):
            self.cfg.use_fvg_filter = bool(self.switch_fvg.get())

    def _apply_inputs_to_config(self):
        try:
            self.cfg.symbol = self.entry_symbol.get().strip().upper()
            self.cfg.timeframe = self.opt_timeframe.get()
            self.cfg.lot_mode = self.opt_lot_mode.get()
            self.cfg.risk_percent = float(self.entry_risk.get().strip())
            self.cfg.risk_reward_ratio = float(self.entry_rr.get().strip())
            self._sync_switches()

            self.real_symbol = self.client.resolve_symbol(self.cfg.symbol)
            self.strategy = TripleEmaStrategy(self.cfg)
            self.risk_mgr = RiskManager(self.cfg)

            self.log(f"Parameter berhasil disimpan! Simbol: {self.real_symbol} | Risk: {self.cfg.risk_percent}% | R:R: 1:{self.cfg.risk_reward_ratio}", "SUCCESS")
            self._update_live_chart()
        except Exception as e:
            self.log(f"Gagal menyimpan parameter: {e}", "ERROR")


if __name__ == "__main__":
    app = TradingTerminalApp()
    app.mainloop()
