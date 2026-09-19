"""
===================================================================================
VIKAR EA 4-PILLAR PRO (v3.10 APEX) - METATRADER 4 HISTORICAL BACKTEST STUDIO
Desktop GUI Application for Strategy Testing on Real MetaTrader 4 Data (.hst & .csv)
Includes:
- 4-Pillar Confluence Engine (SMC + S/R + Triple EMA + Fibo)
- Fixed 100 Point Take Profit
- Dynamic Candle-by-Candle Trailing Stop & Points Trailing
- Adaptive AI Loss Autopsy (7 Scenarios) & Directional Learning (v3.10)
- Interactive Equity Curve, Trade Journal, Pattern Matrix & HTML/CSV Export
===================================================================================
"""

import os
import sys
import math
import struct
import glob
import time
import threading
from datetime import datetime

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

# Set Modern Dark Aesthetics
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ===================================================================================
# 1. METATRADER 4 DATA PARSER (.HST & .CSV)
# ===================================================================================
class MT4DataReader:
    @staticmethod
    def get_mt4_roaming_dirs():
        roaming = os.path.expanduser(r"~\AppData\Roaming\MetaQuotes\Terminal")
        if not os.path.exists(roaming):
            return []
        terminals = []
        for item in os.listdir(roaming):
            t_path = os.path.join(roaming, item)
            hist_path = os.path.join(t_path, "history")
            if os.path.isdir(hist_path):
                terminals.append(t_path)
        return terminals

    @staticmethod
    def find_all_hst_files():
        found = []
        terminals = MT4DataReader.get_mt4_roaming_dirs()
        for t in terminals:
            hist_dir = os.path.join(t, "history")
            for root, _, files in os.walk(hist_dir):
                for f in files:
                    if f.lower().endswith(".hst") and not f.startswith("symbols"):
                        full_path = os.path.join(root, f)
                        server_name = os.path.basename(root)
                        found.append({
                            "server": server_name,
                            "filename": f,
                            "path": full_path,
                            "size": os.path.getsize(full_path)
                        })
        return found

    @staticmethod
    def read_hst(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} tidak ditemukan!")
        
        with open(file_path, "rb") as f:
            header = f.read(148)
            if len(header) < 148:
                raise ValueError("Format header .hst tidak valid atau file rusak!")
            
            version = struct.unpack("<I", header[:4])[0]
            symbol = header[68:80].decode("ascii", errors="ignore").strip("\x00")
            period = struct.unpack("<I", header[80:84])[0]
            digits = struct.unpack("<I", header[84:88])[0]
            
            bars = []
            file_size = os.path.getsize(file_path)
            
            if version == 401:
                # Modern MT4 (Build 509+) format: 60 bytes per bar
                record_size = 60
                fmt = "<qddddqIq"
                num_bars = (file_size - 148) // record_size
                for _ in range(num_bars):
                    data = f.read(record_size)
                    if len(data) < record_size:
                        break
                    t, o, h, l, c, vol, spread, rvol = struct.unpack(fmt, data)
                    bars.append({
                        "time": t,
                        "datetime": datetime.fromtimestamp(t),
                        "open": o,
                        "high": h,
                        "low": l,
                        "close": c,
                        "volume": vol,
                        "spread": spread
                    })
            elif version == 400:
                # Legacy MT4 format: 44 bytes per bar
                record_size = 44
                fmt = "<IdddddI"
                num_bars = (file_size - 148) // record_size
                for _ in range(num_bars):
                    data = f.read(record_size)
                    if len(data) < record_size:
                        break
                    t, o, l, h, c, vol, unused = struct.unpack(fmt, data)
                    bars.append({
                        "time": t,
                        "datetime": datetime.fromtimestamp(t),
                        "open": o,
                        "high": h,
                        "low": l,
                        "close": c,
                        "volume": int(vol),
                        "spread": 0
                    })
            else:
                raise ValueError(f"Versi .hst tidak didukung: {version}")

        # Urutkan bar secara kronologis jika diperlukan
        bars.sort(key=lambda x: x["time"])
        return {
            "symbol": symbol if symbol else os.path.splitext(os.path.basename(file_path))[0],
            "period": period,
            "digits": digits if digits > 0 else 2,
            "bars": bars
        }

    @staticmethod
    def read_csv(file_path):
        # Format ekspor standar MT4 History Center:
        # Date,Time,Open,High,Low,Close,Volume
        df = pd.read_csv(file_path)
        bars = []
        # Normalisasi nama kolom
        cols = {c.strip().lower(): c for c in df.columns}
        
        has_datetime = "datetime" in cols or "date" in cols
        for _, row in df.iterrows():
            if "datetime" in cols:
                dt = pd.to_datetime(row[cols["datetime"]])
            elif "date" in cols and "time" in cols:
                dt = pd.to_datetime(str(row[cols["date"]]) + " " + str(row[cols["time"]]))
            else:
                dt = datetime.now()
            
            t = int(dt.timestamp())
            o = float(row[cols.get("open", df.columns[1])])
            h = float(row[cols.get("high", df.columns[2])])
            l = float(row[cols.get("low", df.columns[3])])
            c = float(row[cols.get("close", df.columns[4])])
            vol = int(row[cols.get("volume", df.columns[5])]) if len(df.columns) > 5 else 100
            bars.append({
                "time": t,
                "datetime": dt,
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": vol,
                "spread": 0
            })
        bars.sort(key=lambda x: x["time"])
        return {
            "symbol": os.path.splitext(os.path.basename(file_path))[0],
            "period": 5,
            "digits": 2,
            "bars": bars
        }


# ===================================================================================
# 2. STRATEGY CALCULATION HELPERS (EMA, ATR, CHOPPINESS, RSI)
# ===================================================================================
def calculate_ema(prices, period):
    n = len(prices)
    ema = [0.0] * n
    if n < period:
        return ema
    mult = 2.0 / (period + 1.0)
    sma = sum(prices[:period]) / period
    ema[period - 1] = sma
    for i in range(period, n):
        ema[i] = (prices[i] - ema[i - 1]) * mult + ema[i - 1]
    return ema

def calculate_atr(highs, lows, closes, period=14):
    n = len(closes)
    tr = [0.0] * n
    for i in range(1, n):
        tr[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
    atr = [0.0] * n
    if n < period + 1:
        return atr
    atr[period] = sum(tr[1:period + 1]) / period
    for i in range(period + 1, n):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr

def calculate_choppiness_index(highs, lows, closes, period=14):
    n = len(closes)
    ci = [50.0] * n
    if n < period + 2:
        return ci
    log10_period = math.log10(period)
    for i in range(period, n):
        sum_tr = 0.0
        max_h = highs[i - period + 1]
        min_l = lows[i - period + 1]
        for j in range(i - period + 1, i + 1):
            tr = max(highs[j] - lows[j], abs(highs[j] - closes[j - 1]), abs(lows[j] - closes[j - 1]))
            sum_tr += tr
            if highs[j] > max_h: max_h = highs[j]
            if lows[j] < min_l: min_l = lows[j]
        rng = max_h - min_l
        if rng > 0.00001 and sum_tr > 0.00001:
            val = 100.0 * (math.log10(sum_tr / rng) / log10_period)
            ci[i] = max(0.0, min(100.0, val))
        else:
            ci[i] = 50.0
    return ci

def calculate_rsi(closes, period=14):
    n = len(closes)
    rsi = [50.0] * n
    if n < period + 1:
        return rsi
    gains, losses = [], []
    for i in range(1, period + 1):
        diff = closes[i] - closes[i - 1]
        gains.append(diff if diff > 0 else 0.0)
        losses.append(-diff if diff < 0 else 0.0)
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rs = avg_gain / avg_loss if avg_loss > 0 else 100.0
    rsi[period] = 100.0 - (100.0 / (1.0 + rs))
    for i in range(period + 1, n):
        diff = closes[i] - closes[i - 1]
        gain = diff if diff > 0 else 0.0
        loss = -diff if diff < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rs = avg_gain / avg_loss if avg_loss > 0 else 100.0
        rsi[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsi


# ===================================================================================
# 3. HIGH-PRECISION VIKAR 4-PILLAR INSTITUTIONAL BACKTEST ENGINE
# ===================================================================================
class VikarBacktestEngine:
    TOTAL_PATTERNS = 13
    PATTERN_NAMES = [
        "Setup Standar / PA",
        "Pin Bar / Hammer",
        "Engulfing Absorption",
        "Tweezer Rejection",
        "Morning / Evening Star",
        "FVG Rebound",
        "Three Soldiers / Crows",
        "Harami Inside Bar",
        "Piercing / Dark Cloud",
        "Dragonfly / Gravestone",
        "Inverted Hammer / Star",
        "Momentum BOS Breakout",
        "Liquidity Sweep Trap Hunter"
    ]

    def __init__(self, bars, params):
        self.bars = bars
        self.params = params
        self.n = len(bars)
        
        self.digits = params.get("digits", 2)
        self.is_gold = "XAU" in params.get("symbol", "").upper() or "GOLD" in params.get("symbol", "").upper()
        
        # Point and Pip Multipliers
        self.point = 10 ** (-self.digits)
        if self.is_gold:
            self.pip_mult = 100.0 if self.digits == 3 else 10.0
        else:
            self.pip_mult = 10.0 if self.digits in [3, 5] else 1.0
        
        self.point_to_price = self.point
        self.pip_to_price = self.point * self.pip_mult

    def points_to_price(self, pts):
        return pts * self.point

    def pips_to_price(self, pips):
        return pips * self.pip_to_price

    def price_to_pips(self, diff):
        return abs(diff) / self.pip_to_price if self.pip_to_price > 0 else 0.0

    def price_to_points(self, diff):
        return abs(diff) / self.point if self.point > 0 else 0.0

    def run(self, progress_callback=None):
        if self.n < 150:
            return {"error": "Jumlah bar lilin tidak mencukupi (minimal 150 bar)."}

        # Ekstrak array OHLCV
        times = [b["time"] for b in self.bars]
        dts = [b["datetime"] for b in self.bars]
        opens = [b["open"] for b in self.bars]
        highs = [b["high"] for b in self.bars]
        lows = [b["low"] for b in self.bars]
        closes = [b["close"] for b in self.bars]
        volumes = [b["volume"] for b in self.bars]

        # 1. Pra-kalkulasi Indikator
        ema8 = calculate_ema(closes, self.params.get("fast_ema", 8))
        ema21 = calculate_ema(closes, self.params.get("medium_ema", 21))
        ema125 = calculate_ema(closes, self.params.get("trend_ema", 125))
        atr14 = calculate_atr(highs, lows, closes, 14)
        atr100 = calculate_atr(highs, lows, closes, 100)
        chop14 = calculate_choppiness_index(highs, lows, closes, 14)
        rsi14 = calculate_rsi(closes, 14)

        # 2. State & Memori Simulasi
        balance = self.params.get("initial_balance", 10000.0)
        equity = balance
        initial_balance = balance

        equity_curve = [{"datetime": dts[0], "balance": balance, "equity": equity, "drawdown": 0.0}]
        trades = []
        open_trade = None
        last_order_bar = -100

        # AI Pattern Performance Matrix State
        pattern_matrix = [{"id": i, "name": self.PATTERN_NAMES[i], "wins": 0, "losses": 0, "total": 0, "winrate": 0.0, "modifier": 0.0, "blacklisted": False} for i in range(self.TOTAL_PATTERNS)]

        # AI Self-Healing Autopsy State
        autopsy = {
            "active": False,
            "penalty_score": 0.0,
            "quarantine_until_bar": 0,
            "failed_pattern": 0,
            "failed_dir": 0,
            "dir_penalty_until_bar": 0,
            "toxic_hour": -1,
            "extra_buffer_trades": 0,
            "last_reason": "NORMAL"
        }
        hourly_losses = [0] * 24
        autopsy_logs = []

        # AI Autonomous Neuro-Calibration & Self-Tuning State (v3.20)
        consecutive_loss_count = 0
        calib_state = {
            "regime": "Normal Confluence",
            "vol_ratio": 1.0,
            "score_elevation": 0.0,
            "sl_mult": 1.0,
            "cooldown": self.params.get("cooldown_bars", 2),
            "candle_buf": self.params.get("candle_trail_buf_points", 15.0)
        }
        calib_logs = []

        spread_price = self.points_to_price(self.params.get("spread_points", 25.0))
        fixed_tp_points = self.params.get("fixed_tp_points", 100.0)
        use_fixed_tp = self.params.get("tp_mode", "FIXED_100") == "FIXED_100"

        # 3. Bar-by-Bar Simulation Loop
        start_idx = 130
        for i in range(start_idx, self.n):
            if progress_callback and i % 250 == 0:
                progress_callback(i / self.n)

            current_time = times[i]
            current_dt = dts[i]
            cur_open = opens[i]
            cur_high = highs[i]
            cur_low = lows[i]
            cur_close = closes[i]
            cur_hour = current_dt.hour

            # UPDATE AUTO-CALIBRATION & REGIME TRACKING (v3.20)
            if self.params.get("use_auto_calibration", True):
                cur_atr14 = atr14[i] if atr14[i] > 0 else self.pips_to_price(20.0)
                cur_atr100 = atr100[i] if (i < len(atr100) and atr100[i] > 0) else cur_atr14
                vol_ratio = (cur_atr14 / cur_atr100) if cur_atr100 > 0 else 1.0

                sens = self.params.get("auto_tuning_sensitivity", 1.25)
                score_step = self.params.get("auto_tuning_score_step", 5.0)
                base_cooldown = self.params.get("cooldown_bars", 2)
                base_candle_buf = self.params.get("candle_trail_buf_points", 15.0)

                old_regime = calib_state["regime"]
                if vol_ratio >= sens:
                    calib_regime = "High Volatility Spike"
                    calib_sl_mult = 1.35
                    calib_candle_buf = base_candle_buf * 1.4
                    calib_score_elev = 10.0
                    calib_cooldown = base_cooldown + 1
                elif vol_ratio <= 0.70 or chop14[i] > 61.8:
                    calib_regime = "Choppy Compression"
                    calib_sl_mult = 0.90
                    calib_candle_buf = base_candle_buf
                    calib_score_elev = 5.0
                    calib_cooldown = base_cooldown + 2
                else:
                    calib_regime = "Normal Confluence"
                    calib_sl_mult = 1.0
                    calib_candle_buf = base_candle_buf
                    calib_score_elev = 0.0
                    calib_cooldown = base_cooldown

                # Anti-tilt pasca loss beruntun
                if consecutive_loss_count >= self.params.get("calibration_consec_loss_max", 2):
                    calib_score_elev += (consecutive_loss_count * score_step)
                    calib_cooldown = min(8, base_cooldown * consecutive_loss_count)
                    calib_sl_mult = min(2.5, calib_sl_mult + 0.25)
                    calib_regime += f" (Anti-Tilt L{consecutive_loss_count})"

                if calib_regime != old_regime and (not calib_logs or calib_logs[-1]["regime"] != calib_regime):
                    calib_logs.append({
                        "time": current_dt,
                        "regime": calib_regime,
                        "vol_ratio": round(vol_ratio, 2),
                        "score_elev": f"+{calib_score_elev:.0f} pts",
                        "cooldown": f"{calib_cooldown} bar",
                        "sl_mult": f"{calib_sl_mult:.2f}x"
                    })

                calib_state["regime"] = calib_regime
                calib_state["vol_ratio"] = vol_ratio
                calib_state["score_elevation"] = calib_score_elev
                calib_state["sl_mult"] = calib_sl_mult
                calib_state["cooldown"] = calib_cooldown
                calib_state["candle_buf"] = calib_candle_buf
            else:
                calib_state["regime"] = "Manual Static"
                calib_state["vol_ratio"] = 1.0
                calib_state["score_elevation"] = 0.0
                calib_state["sl_mult"] = 1.0
                calib_state["cooldown"] = self.params.get("cooldown_bars", 2)
                calib_state["candle_buf"] = self.params.get("candle_trail_buf_points", 15.0)

            # A. KELOLA POSISI AKTIF (Trailing Stop, Auto-BE, TP 100 Point & SL)
            if open_trade is not None:
                tr = open_trade
                is_buy = tr["type"] == "BUY"
                trade_pnl = 0.0
                closed = False
                exit_price = 0.0
                exit_reason = ""

                # Cek Stop Loss
                if is_buy and cur_low <= tr["sl"]:
                    closed = True
                    exit_price = tr["sl"]
                    exit_reason = "STOP LOSS"
                elif not is_buy and cur_high >= tr["sl"]:
                    closed = True
                    exit_price = tr["sl"]
                    exit_reason = "STOP LOSS"

                # Cek Take Profit (100 Point)
                if not closed:
                    if is_buy and cur_high >= tr["tp"]:
                        closed = True
                        exit_price = tr["tp"]
                        exit_reason = "TAKE PROFIT (100 PT)"
                    elif not is_buy and cur_low <= tr["tp"]:
                        closed = True
                        exit_price = tr["tp"]
                        exit_reason = "TAKE PROFIT (100 PT)"

                # B. AUTO-BREAKEVEN (SL+)
                if not closed and self.params.get("use_breakeven", True):
                    be_trigger = self.pips_to_price(self.params.get("be_trigger_pips", 5.0))
                    be_lock = self.pips_to_price(self.params.get("be_lock_pips", 2.0))
                    if is_buy:
                        profit_dist = cur_high - tr["open_price"]
                        if profit_dist >= be_trigger and tr["sl"] < (tr["open_price"] + be_lock):
                            tr["sl"] = tr["open_price"] + be_lock
                            tr["is_be_locked"] = True
                    else:
                        profit_dist = tr["open_price"] - cur_low
                        if profit_dist >= be_trigger and tr["sl"] > (tr["open_price"] - be_lock):
                            tr["sl"] = tr["open_price"] - be_lock
                            tr["is_be_locked"] = True

                # C. DYNAMIC POINTS TRAILING STOP
                if not closed and self.params.get("use_points_trailing", True):
                    trail_start = self.points_to_price(self.params.get("trail_start_points", 40.0))
                    trail_dist = self.points_to_price(self.params.get("trail_dist_points", 30.0))
                    trail_step = self.points_to_price(self.params.get("trail_step_points", 10.0))
                    if is_buy:
                        profit_dist = cur_close - tr["open_price"]
                        if profit_dist >= trail_start:
                            target_sl = cur_close - trail_dist
                            if target_sl > tr["sl"] + trail_step and target_sl > tr["open_price"]:
                                tr["sl"] = target_sl
                    else:
                        profit_dist = tr["open_price"] - cur_close
                        if profit_dist >= trail_start:
                            target_sl = cur_close + trail_dist
                            if target_sl < tr["sl"] - trail_step and target_sl < tr["open_price"]:
                                tr["sl"] = target_sl

                # D. DYNAMIC CANDLE-BY-CANDLE TRAILING STOP
                if not closed and self.params.get("use_candle_trailing", True):
                    effective_candle_buf_pts = calib_state["candle_buf"] if self.params.get("use_auto_calibration", True) else self.params.get("candle_trail_buf_points", 15.0)
                    candle_buf = self.points_to_price(effective_candle_buf_pts)
                    if is_buy:
                        prev_low = lows[i - 1]
                        candle_sl = prev_low - candle_buf
                        if candle_sl > tr["open_price"] and candle_sl > tr["sl"]:
                            tr["sl"] = candle_sl
                    else:
                        prev_high = highs[i - 1]
                        candle_sl = prev_high + candle_buf
                        if candle_sl < tr["open_price"] and candle_sl < tr["sl"]:
                            tr["sl"] = candle_sl

                # EKSEKUSI PENUTUPAN ORDER
                if closed:
                    pips_gain = (exit_price - tr["open_price"]) / self.pip_to_price if is_buy else (tr["open_price"] - exit_price) / self.pip_to_price
                    # PnL dalam mata uang account: Lot * 100 * (harga_exit - harga_open) untuk Gold
                    contract_size = 100.0 if self.is_gold else 100000.0
                    dollar_pnl = (exit_price - tr["open_price"]) * tr["lot"] * contract_size if is_buy else (tr["open_price"] - exit_price) * tr["lot"] * contract_size
                    
                    balance += dollar_pnl
                    equity = balance
                    is_win = dollar_pnl > 0.01
                    is_true_loss = dollar_pnl < -0.01

                    if is_win:
                        consecutive_loss_count = 0
                    elif is_true_loss:
                        consecutive_loss_count += 1

                    tr["close_time"] = current_dt
                    tr["close_price"] = exit_price
                    tr["exit_reason"] = exit_reason
                    tr["pnl_pips"] = round(pips_gain, 1)
                    tr["pnl_dollar"] = round(dollar_pnl, 2)
                    tr["balance_after"] = round(balance, 2)
                    trades.append(tr)
                    open_trade = None

                    # PEMBARUAN RAPOR POLA AI (Pattern Matrix)
                    pat_id = tr["pattern_id"]
                    if 0 <= pat_id < self.TOTAL_PATTERNS:
                        if is_win:
                            pattern_matrix[pat_id]["wins"] += 1
                        elif is_true_loss:
                            pattern_matrix[pat_id]["losses"] += 1
                        pattern_matrix[pat_id]["total"] = pattern_matrix[pat_id]["wins"] + pattern_matrix[pat_id]["losses"]
                        tot = pattern_matrix[pat_id]["total"]
                        wr = (pattern_matrix[pat_id]["wins"] / tot * 100.0) if tot > 0 else 0.0
                        pattern_matrix[pat_id]["winrate"] = round(wr, 1)

                        # Blacklist & Boost Rules
                        if self.params.get("use_pattern_matrix", True) and tot >= 3:
                            if wr < 40.0:
                                pattern_matrix[pat_id]["blacklisted"] = True
                                pattern_matrix[pat_id]["modifier"] = -15.0
                            elif wr >= 70.0:
                                pattern_matrix[pat_id]["blacklisted"] = False
                                pattern_matrix[pat_id]["modifier"] = 10.0
                            else:
                                pattern_matrix[pat_id]["blacklisted"] = False
                                pattern_matrix[pat_id]["modifier"] = 0.0

                    # PEMBELAJARAN KEGAGALAN (OTOPSI PASCA-SL & KOREKSI DIRI v3.10)
                    if is_true_loss and self.params.get("use_self_healing", True):
                        autopsy["active"] = True
                        autopsy["failed_pattern"] = pat_id
                        autopsy["failed_dir"] = 1 if is_buy else -1
                        autopsy["penalty_score"] = self.params.get("autopsy_penalty_score", 10.0)
                        autopsy["quarantine_until_bar"] = i + self.params.get("quarantine_bars", 15)
                        autopsy["dir_penalty_until_bar"] = i + self.params.get("directional_penalty_bars", 12)
                        autopsy["extra_buffer_trades"] = 3

                        # Deteksi Jam Rawan Loss (Toxic Hour)
                        if self.params.get("use_hourly_learning", True):
                            hourly_losses[cur_hour] += 1
                            if hourly_losses[cur_hour] >= 2:
                                autopsy["toxic_hour"] = cur_hour

                        # Diagnosa 7 Skenario
                        cur_atr = atr14[i] if atr14[i] > 0 else self.pips_to_price(20.0)
                        bar_range = highs[i - 1] - lows[i - 1]
                        diag = "PENGUJIAN LEVEL GAGAL (LOW CONFLUENCE)"
                        if bar_range >= 2.0 * cur_atr:
                            diag = "VOLATILITAS ABNORMAL (NEWS SHOCK / SPIKE)"
                        elif chop14[i] > 61.8:
                            diag = "JEBAKAN SIDEWAYS NOISE (PASAR CHOPPY KOMPRESI)"
                        elif (closes[i - 1] < ema125[i - 1] and opens[i - 1] > ema125[i - 1]) or (closes[i - 1] > ema125[i - 1] and opens[i - 1] < ema125[i - 1]):
                            diag = "PEMBALIKAN STRUKTUR MAKRO (TREND INVALIDATION)"
                        elif (is_buy and cur_hour == autopsy["toxic_hour"]) or (not is_buy and cur_hour == autopsy["toxic_hour"]):
                            diag = "JAM RAWAN VOLATILITAS (TOXIC HOUR REVERSAL)"
                        elif is_buy and closes[i] < ema125[i]:
                            diag = "DIRECTIONAL ERROR (BUY MELAWAN TREN MAKRO H1)"
                        elif not is_buy and closes[i] > ema125[i]:
                            diag = "DIRECTIONAL ERROR (SELL MELAWAN TREN MAKRO H1)"

                        autopsy["last_reason"] = diag
                        autopsy_logs.append({
                            "time": current_dt,
                            "ticket": tr["ticket"],
                            "type": tr["type"],
                            "pattern": self.PATTERN_NAMES[pat_id],
                            "reason": diag,
                            "penalty": f"+{autopsy['penalty_score']} pts",
                            "dir_guard": "Blok BUY" if is_buy else "Blok SELL"
                        })
                    elif is_win:
                        autopsy["active"] = False
                        autopsy["failed_dir"] = 0
                        autopsy["penalty_score"] = 0.0

            # B. SCANNING SETUP SINYAL BARU (JIKA TIDAK ADA POSISI TERBUKA)
            effective_cooldown = calib_state["cooldown"] if self.params.get("use_auto_calibration", True) else self.params.get("cooldown_bars", 2)
            if open_trade is None and (i - last_order_bar >= effective_cooldown):
                # Filter Regim Choppy
                if self.params.get("use_regime_filter", True) and chop14[i] > 61.8:
                    continue

                cur_atr = atr14[i] if atr14[i] > 0 else self.pips_to_price(20.0)
                
                # Deteksi 13 Pola Lilin Institusional (SMC + Candlestick Suite)
                prev_body = abs(closes[i - 1] - opens[i - 1])
                prev_range = highs[i - 1] - lows[i - 1] if highs[i - 1] > lows[i - 1] else 0.0001
                lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
                upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])

                is_trend_bull = (closes[i - 1] > ema125[i - 1]) and (ema8[i - 1] > ema21[i - 1])
                is_trend_bear = (closes[i - 1] < ema125[i - 1]) and (ema8[i - 1] < ema21[i - 1])

                bull_pat = None
                bear_pat = None

                # 12. Sweep Trap Hunter (Turtle Soup Reversal)
                if (lower_wick / prev_range >= 0.40) and (lows[i - 1] < min(lows[i - 15:i - 1])) and (closes[i - 1] > min(lows[i - 15:i - 1])):
                    bull_pat = 12
                elif (upper_wick / prev_range >= 0.40) and (highs[i - 1] > max(highs[i - 15:i - 1])) and (closes[i - 1] < max(highs[i - 15:i - 1])):
                    bear_pat = 12

                # 11. Momentum BOS Breakout Expansion
                elif (closes[i - 1] - opens[i - 1] >= 1.5 * cur_atr) and (closes[i - 1] > ema8[i - 1] > ema21[i - 1]):
                    bull_pat = 11
                elif (opens[i - 1] - closes[i - 1] >= 1.5 * cur_atr) and (closes[i - 1] < ema8[i - 1] < ema21[i - 1]):
                    bear_pat = 11

                # 6. Three White Soldiers / Three Black Crows
                elif (closes[i - 1] > opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 3] > opens[i - 3] and closes[i - 1] > closes[i - 2] > closes[i - 3]):
                    bull_pat = 6
                elif (closes[i - 1] < opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 3] < opens[i - 3] and closes[i - 1] < closes[i - 2] < closes[i - 3]):
                    bear_pat = 6

                # 4. Morning Star / Evening Star (3-Bar Reversal)
                elif (closes[i - 3] < opens[i - 3] and abs(closes[i - 2] - opens[i - 2]) <= 0.35 * (highs[i - 2] - lows[i - 2]) and closes[i - 1] > opens[i - 1] and closes[i - 1] >= ((opens[i - 3] + closes[i - 3]) / 2.0)):
                    bull_pat = 4
                elif (closes[i - 3] > opens[i - 3] and abs(closes[i - 2] - opens[i - 2]) <= 0.35 * (highs[i - 2] - lows[i - 2]) and closes[i - 1] < opens[i - 1] and closes[i - 1] <= ((opens[i - 3] + closes[i - 3]) / 2.0)):
                    bear_pat = 4

                # 5. Fair Value Gap (FVG) Rebound
                elif (lows[i - 2] > highs[i - 4] and lows[i - 1] <= lows[i - 2] and closes[i - 1] > opens[i - 1]):
                    bull_pat = 5
                elif (highs[i - 2] < lows[i - 4] and highs[i - 1] >= highs[i - 2] and closes[i - 1] < opens[i - 1]):
                    bear_pat = 5

                # 2. Engulfing Absorption
                elif (closes[i - 1] > opens[i - 1] and closes[i - 2] < opens[i - 2] and closes[i - 1] >= opens[i - 2] and opens[i - 1] <= closes[i - 2]):
                    bull_pat = 2
                elif (closes[i - 1] < opens[i - 1] and closes[i - 2] > opens[i - 2] and closes[i - 1] <= opens[i - 2] and opens[i - 1] >= closes[i - 2]):
                    bear_pat = 2

                # 9. Dragonfly Doji / Gravestone Doji Extreme Rejection
                elif (lower_wick >= 0.65 * prev_range and prev_body <= 0.15 * prev_range):
                    bull_pat = 9
                elif (upper_wick >= 0.65 * prev_range and prev_body <= 0.15 * prev_range):
                    bear_pat = 9

                # 1. Pin Bar / Hammer Rejection
                elif (lower_wick >= 0.50 * prev_range and prev_body <= 0.35 * prev_range and closes[i - 1] >= opens[i - 1]):
                    bull_pat = 1
                elif (upper_wick >= 0.50 * prev_range and prev_body <= 0.35 * prev_range and closes[i - 1] <= opens[i - 1]):
                    bear_pat = 1

                # 8. Piercing Line / Dark Cloud Cover
                elif (closes[i - 2] < opens[i - 2] and closes[i - 1] > opens[i - 1] and opens[i - 1] <= lows[i - 2] and closes[i - 1] >= ((opens[i - 2] + closes[i - 2]) / 2.0)):
                    bull_pat = 8
                elif (closes[i - 2] > opens[i - 2] and closes[i - 1] < opens[i - 1] and opens[i - 1] >= highs[i - 2] and closes[i - 1] <= ((opens[i - 2] + closes[i - 2]) / 2.0)):
                    bear_pat = 8

                # 3. Tweezer Rejection
                elif (abs(lows[i - 1] - lows[i - 2]) <= 0.25 * cur_atr and lower_wick >= 0.35 * prev_range):
                    bull_pat = 3
                elif (abs(highs[i - 1] - highs[i - 2]) <= 0.25 * cur_atr and upper_wick >= 0.35 * prev_range):
                    bear_pat = 3

                # 7. Harami Inside Bar
                elif (highs[i - 1] <= highs[i - 2] and lows[i - 1] >= lows[i - 2] and closes[i - 1] >= opens[i - 1]):
                    bull_pat = 7
                elif (highs[i - 1] <= highs[i - 2] and lows[i - 1] >= lows[i - 2] and closes[i - 1] < opens[i - 1]):
                    bear_pat = 7

                # 10. Inverted Hammer / Shooting Star
                elif (upper_wick >= 0.45 * prev_range and prev_body <= 0.35 * prev_range and lower_wick <= 0.20 * prev_range and closes[i - 1] >= opens[i - 1]):
                    bull_pat = 10
                elif (lower_wick >= 0.45 * prev_range and prev_body <= 0.35 * prev_range and upper_wick <= 0.20 * prev_range and closes[i - 1] <= opens[i - 1]):
                    bear_pat = 10

                # 0. Setup Standar / Price Action Pullback
                elif is_trend_bull and abs(closes[i - 1] - ema21[i - 1]) <= 0.8 * cur_atr:
                    bull_pat = 0
                elif is_trend_bear and abs(closes[i - 1] - ema21[i - 1]) <= 0.8 * cur_atr:
                    bear_pat = 0

                # Evaluasi Sinyal BUY
                if bull_pat is not None and (is_trend_bull or bull_pat in [12, 11, 4, 6]):
                    pat_id = bull_pat

                    # Karantina Pola & Penalti Arah
                    if autopsy["active"] and i < autopsy["quarantine_until_bar"] and pat_id == autopsy["failed_pattern"]:
                        continue
                    if autopsy["failed_dir"] == 1 and i < autopsy["dir_penalty_until_bar"]:
                        continue
                    if pattern_matrix[pat_id]["blacklisted"]:
                        continue

                    # Perhitungan Skor Konfluensi
                    score = 50.0
                    if is_trend_bull: score += 15.0
                    if pat_id in [12, 11, 6, 4]: score += 20.0
                    elif pat_id in [1, 2, 9, 8]: score += 15.0
                    elif pat_id in [3, 5, 7, 10]: score += 10.0
                    if chop14[i] < 38.2: score += 10.0
                    score += pattern_matrix[pat_id]["modifier"]

                    req_score = self.params.get("min_confluence_score", 65.0)
                    if self.params.get("use_auto_calibration", True): req_score += calib_state["score_elevation"]
                    if autopsy["active"]: req_score += autopsy["penalty_score"]
                    if cur_hour == autopsy["toxic_hour"]: req_score += 10.0

                    if score >= req_score:
                        entry_price = cur_open + spread_price
                        effective_sl_mult = calib_state["sl_mult"] if self.params.get("use_auto_calibration", True) else 1.0
                        sl_price = cur_open - (self.pips_to_price(self.params.get("fixed_sl_pips", 20.0)) * effective_sl_mult)
                        if pat_id == 12:
                            sl_price = lows[i - 1] - (self.points_to_price(10.0) * effective_sl_mult)

                        if autopsy["extra_buffer_trades"] > 0:
                            sl_price -= 0.3 * cur_atr * effective_sl_mult
                            autopsy["extra_buffer_trades"] -= 1

                        if use_fixed_tp:
                            tp_price = entry_price + self.points_to_price(fixed_tp_points)
                        else:
                            tp_price = entry_price + (self.params.get("risk_reward", 1.5) * (entry_price - sl_price))

                        lot = self.params.get("fixed_lot", 0.01)
                        open_trade = {
                            "ticket": len(trades) + 1,
                            "type": "BUY",
                            "open_time": current_dt,
                            "open_price": entry_price,
                            "sl": sl_price,
                            "tp": tp_price,
                            "lot": lot,
                            "pattern_id": pat_id,
                            "pattern_name": self.PATTERN_NAMES[pat_id],
                            "score": score,
                            "regime": calib_state["regime"],
                            "is_be_locked": False
                        }
                        last_order_bar = i

                # Evaluasi Sinyal SELL
                elif bear_pat is not None and (is_trend_bear or bear_pat in [12, 11, 4, 6]):
                    pat_id = bear_pat

                    if autopsy["active"] and i < autopsy["quarantine_until_bar"] and pat_id == autopsy["failed_pattern"]:
                        continue
                    if autopsy["failed_dir"] == -1 and i < autopsy["dir_penalty_until_bar"]:
                        continue
                    if pattern_matrix[pat_id]["blacklisted"]:
                        continue

                    score = 50.0
                    if is_trend_bear: score += 15.0
                    if pat_id in [12, 11, 6, 4]: score += 20.0
                    elif pat_id in [1, 2, 9, 8]: score += 15.0
                    elif pat_id in [3, 5, 7, 10]: score += 10.0
                    if chop14[i] < 38.2: score += 10.0
                    score += pattern_matrix[pat_id]["modifier"]

                    req_score = self.params.get("min_confluence_score", 65.0)
                    if self.params.get("use_auto_calibration", True): req_score += calib_state["score_elevation"]
                    if autopsy["active"]: req_score += autopsy["penalty_score"]
                    if cur_hour == autopsy["toxic_hour"]: req_score += 10.0

                    if score >= req_score:
                        entry_price = cur_open
                        effective_sl_mult = calib_state["sl_mult"] if self.params.get("use_auto_calibration", True) else 1.0
                        sl_price = cur_open + (self.pips_to_price(self.params.get("fixed_sl_pips", 20.0)) * effective_sl_mult)
                        if pat_id == 12:
                            sl_price = highs[i - 1] + (self.points_to_price(10.0) * effective_sl_mult)

                        if autopsy["extra_buffer_trades"] > 0:
                            sl_price += 0.3 * cur_atr * effective_sl_mult
                            autopsy["extra_buffer_trades"] -= 1

                        if use_fixed_tp:
                            tp_price = entry_price - self.points_to_price(fixed_tp_points)
                        else:
                            tp_price = entry_price - (self.params.get("risk_reward", 1.5) * (sl_price - entry_price))

                        lot = self.params.get("fixed_lot", 0.01)
                        open_trade = {
                            "ticket": len(trades) + 1,
                            "type": "SELL",
                            "open_time": current_dt,
                            "open_price": entry_price,
                            "sl": sl_price,
                            "tp": tp_price,
                            "lot": lot,
                            "pattern_id": pat_id,
                            "pattern_name": self.PATTERN_NAMES[pat_id],
                            "score": score,
                            "regime": calib_state["regime"],
                            "is_be_locked": False
                        }
                        last_order_bar = i

            # Rekam kurva ekuitas secara periodik
            if i % 15 == 0 or open_trade is not None:
                peak_bal = max([p["balance"] for p in equity_curve]) if equity_curve else balance
                dd_pct = (peak_bal - balance) / peak_bal * 100.0 if peak_bal > 0 else 0.0
                equity_curve.append({
                    "datetime": current_dt,
                    "balance": round(balance, 2),
                    "equity": round(balance, 2),
                    "drawdown": round(dd_pct, 2)
                })

        # Tutup posisi tersisa jika masih ada di bar terakhir
        if open_trade is not None:
            tr = open_trade
            is_buy = tr["type"] == "BUY"
            exit_price = closes[-1]
            pips_gain = (exit_price - tr["open_price"]) / self.pip_to_price if is_buy else (tr["open_price"] - exit_price) / self.pip_to_price
            contract_size = 100.0 if self.is_gold else 100000.0
            dollar_pnl = (exit_price - tr["open_price"]) * tr["lot"] * contract_size if is_buy else (tr["open_price"] - exit_price) * tr["lot"] * contract_size
            balance += dollar_pnl
            tr["close_time"] = dts[-1]
            tr["close_price"] = exit_price
            tr["exit_reason"] = "END OF DATA"
            tr["pnl_pips"] = round(pips_gain, 1)
            tr["pnl_dollar"] = round(dollar_pnl, 2)
            tr["balance_after"] = round(balance, 2)
            trades.append(tr)

        # 4. Kalkulasi Statistik Komprehensif
        total_trades = len(trades)
        wins = [t for t in trades if t["pnl_dollar"] > 0]
        losses = [t for t in trades if t["pnl_dollar"] < 0]
        breakevens = [t for t in trades if abs(t["pnl_dollar"]) <= 0.01]

        gross_profit = sum([t["pnl_dollar"] for t in wins])
        gross_loss = abs(sum([t["pnl_dollar"] for t in losses]))
        net_profit = gross_profit - gross_loss
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 99.9
        win_rate = (len(wins) / total_trades * 100.0) if total_trades > 0 else 0.0

        # Maximum Drawdown
        peak = initial_balance
        max_dd_dollar = 0.0
        max_dd_pct = 0.0
        running_bal = initial_balance
        for t in trades:
            running_bal += t["pnl_dollar"]
            if running_bal > peak:
                peak = running_bal
            dd_d = peak - running_bal
            dd_p = (dd_d / peak * 100.0) if peak > 0 else 0.0
            if dd_d > max_dd_dollar: max_dd_dollar = dd_d
            if dd_p > max_dd_pct: max_dd_pct = dd_p

        return {
            "symbol": self.params.get("symbol", "XAUUSD"),
            "period": self.params.get("period", 5),
            "total_bars": self.n,
            "start_date": dts[0].strftime("%Y-%m-%d %H:%M"),
            "end_date": dts[-1].strftime("%Y-%m-%d %H:%M"),
            "initial_balance": initial_balance,
            "final_balance": round(balance, 2),
            "net_profit": round(net_profit, 2),
            "net_profit_pct": round((net_profit / initial_balance) * 100.0, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_loss": round(gross_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "total_trades": total_trades,
            "wins_count": len(wins),
            "losses_count": len(losses),
            "be_count": len(breakevens),
            "win_rate": round(win_rate, 1),
            "max_drawdown_dollar": round(max_dd_dollar, 2),
            "max_drawdown_pct": round(max_dd_pct, 2),
            "trades": trades,
            "equity_curve": equity_curve,
            "pattern_matrix": pattern_matrix,
            "autopsy_logs": autopsy_logs,
            "calib_logs": calib_logs
        }


# ===================================================================================
# 4. MODERN CUSTOMTKINTER DESKTOP GUI APPLICATION
# ===================================================================================
class VikarBacktestStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vikar EA 4-Pillar Pro - MT4 Backtest Studio (v3.20 Neuro-Calibration)")
        self.geometry("1400x860")
        self.minsize(1150, 750)

        self.loaded_data = None
        self.backtest_results = None
        self.available_hst = []

        self._build_ui()
        self._scan_mt4_terminals()

    def _build_ui(self):
        # Grid layout (Sidebar kiri 340px, Konten kanan sisa)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # SIDEBAR KIRI: Pengaturan & Data Source
        # ----------------------------------------------------
        self.sidebar = ctk.CTkScrollableFrame(self, width=330, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Header Title
        title_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=10, pady=(15, 10))
        ctk.CTkLabel(title_frame, text="⚡ VIKAR EA 4-PILLAR", font=ctk.CTkFont(size=18, weight="bold"), text_color="#38bdf8").pack(anchor="w")
        ctk.CTkLabel(title_frame, text="MT4 Historical Backtest Studio • v3.20", font=ctk.CTkFont(size=11), text_color="#94a3b8").pack(anchor="w")

        # Group 1: Sumber Data MT4
        sec1 = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        sec1.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(sec1, text="📁 SUMBER DATA METATRADER 4", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=10, pady=(8, 4))

        self.hst_combo = ctk.CTkComboBox(sec1, values=["Scanning MT4..."], command=self._on_hst_selected)
        self.hst_combo.pack(fill="x", padx=10, pady=5)

        btn_box = ctk.CTkFrame(sec1, fg_color="transparent")
        btn_box.pack(fill="x", padx=10, pady=(0, 8))
        ctk.CTkButton(btn_box, text="🔄 Scan Ulang", width=95, height=28, command=self._scan_mt4_terminals).pack(side="left", padx=(0, 4))
        ctk.CTkButton(btn_box, text="📂 Buka .HST/.CSV", width=120, height=28, fg_color="#334155", hover_color="#475569", command=self._browse_custom_file).pack(side="left")

        self.lbl_data_info = ctk.CTkLabel(sec1, text="Data belum dimuat.", font=ctk.CTkFont(size=10), text_color="#cbd5e1", justify="left")
        self.lbl_data_info.pack(anchor="w", padx=10, pady=(0, 8))

        # Group 2: Parameter Take Profit & Stop Loss
        sec2 = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        sec2.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(sec2, text="🎯 TARGET TP & STOP LOSS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=10, pady=(8, 4))

        ctk.CTkLabel(sec2, text="Metode Target TP:", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10)
        self.combo_tp_mode = ctk.CTkComboBox(sec2, values=["Risk-to-Reward Ratio", "Fixed 100 Points (Scalping)"])
        self.combo_tp_mode.set("Risk-to-Reward Ratio")
        self.combo_tp_mode.pack(fill="x", padx=10, pady=(2, 6))

        row_rr = ctk.CTkFrame(sec2, fg_color="transparent")
        row_rr.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(row_rr, text="Rasio R:R (1 : X):", font=ctk.CTkFont(size=11)).pack(side="left")
        self.ent_rr = ctk.CTkEntry(row_rr, width=80, height=26)
        self.ent_rr.insert(0, "1.5")
        self.ent_rr.pack(side="right")

        row_tp = ctk.CTkFrame(sec2, fg_color="transparent")
        row_tp.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(row_tp, text="Target TP (Point):", font=ctk.CTkFont(size=11)).pack(side="left")
        self.ent_tp_points = ctk.CTkEntry(row_tp, width=80, height=26)
        self.ent_tp_points.insert(0, "100.0")
        self.ent_tp_points.pack(side="right")

        row_sl = ctk.CTkFrame(sec2, fg_color="transparent")
        row_sl.pack(fill="x", padx=10, pady=3)
        ctk.CTkLabel(row_sl, text="Stop Loss (Pips):", font=ctk.CTkFont(size=11)).pack(side="left")
        self.ent_sl_pips = ctk.CTkEntry(row_sl, width=80, height=26)
        self.ent_sl_pips.insert(0, "20.0")
        self.ent_sl_pips.pack(side="right")

        # Group 3: Trailing Stop & Auto-BE Suite
        sec3 = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        sec3.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(sec3, text="🛡️ TRAILING STOP & AUTO-BE", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=10, pady=(8, 4))

        self.chk_candle_trail = ctk.CTkCheckBox(sec3, text="Candle-by-Candle Trailing (Low/High)")
        self.chk_candle_trail.select()
        self.chk_candle_trail.pack(anchor="w", padx=10, pady=3)

        self.chk_points_trail = ctk.CTkCheckBox(sec3, text="Dynamic Points Trailing (Start 40, Dist 30)")
        self.chk_points_trail.select()
        self.chk_points_trail.pack(anchor="w", padx=10, pady=3)

        self.chk_be = ctk.CTkCheckBox(sec3, text="Auto-BE / SL+ (Kunci 20 pt di 50 pt)")
        self.chk_be.select()
        self.chk_be.pack(anchor="w", padx=10, pady=(3, 8))

        # Group 4: AI Self-Healing & Neuro-Calibration (v3.20)
        sec4 = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        sec4.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(sec4, text="🧠 AI CALIBRATION & AUTOPSY (v3.20)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=10, pady=(8, 4))

        self.chk_auto_calib = ctk.CTkCheckBox(sec4, text="Auto-Calibration & Self-Tuning (v3.20)")
        self.chk_auto_calib.select()
        self.chk_auto_calib.pack(anchor="w", padx=10, pady=3)

        self.chk_autopsy = ctk.CTkCheckBox(sec4, text="Otopsi 7 Skenario Pasca-SL & Karantina")
        self.chk_autopsy.select()
        self.chk_autopsy.pack(anchor="w", padx=10, pady=3)

        self.chk_dir_learning = ctk.CTkCheckBox(sec4, text="Directional Bias Guard (+15 pt Penalti)")
        self.chk_dir_learning.select()
        self.chk_dir_learning.pack(anchor="w", padx=10, pady=3)

        self.chk_hourly_learning = ctk.CTkCheckBox(sec4, text="Hourly Toxic Learning (Jam Rawan Loss)")
        self.chk_hourly_learning.select()
        self.chk_hourly_learning.pack(anchor="w", padx=10, pady=3)

        self.chk_pat_matrix = ctk.CTkCheckBox(sec4, text="Rapor Matriks 13 Pola (Boost & Blacklist)")
        self.chk_pat_matrix.select()
        self.chk_pat_matrix.pack(anchor="w", padx=10, pady=(3, 8))

        # Group 5: Modal & Akun
        sec5 = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=8)
        sec5.pack(fill="x", padx=10, pady=8)
        ctk.CTkLabel(sec5, text="💰 MODAL & EKSEKUSI", font=ctk.CTkFont(size=12, weight="bold"), text_color="#f8fafc").pack(anchor="w", padx=10, pady=(8, 4))

        row_bal = ctk.CTkFrame(sec5, fg_color="transparent")
        row_bal.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(row_bal, text="Modal Awal ($):", font=ctk.CTkFont(size=11)).pack(side="left")
        self.ent_balance = ctk.CTkEntry(row_bal, width=80, height=26)
        self.ent_balance.insert(0, "10000")
        self.ent_balance.pack(side="right")

        row_lot = ctk.CTkFrame(sec5, fg_color="transparent")
        row_lot.pack(fill="x", padx=10, pady=2)
        ctk.CTkLabel(row_lot, text="Ukuran Lot:", font=ctk.CTkFont(size=11)).pack(side="left")
        self.ent_lot = ctk.CTkEntry(row_lot, width=80, height=26)
        self.ent_lot.insert(0, "0.01")
        self.ent_lot.pack(side="right")

        row_spd = ctk.CTkFrame(sec5, fg_color="transparent")
        row_spd.pack(fill="x", padx=10, pady=(2, 8))
        ctk.CTkLabel(row_spd, text="Spread (Point):", font=ctk.CTkFont(size=11)).pack(side="left")
        self.ent_spread = ctk.CTkEntry(row_spd, width=80, height=26)
        self.ent_spread.insert(0, "25.0")
        self.ent_spread.pack(side="right")

        # Action Button
        self.btn_run = ctk.CTkButton(self.sidebar, text="▶ JALANKAN BACKTEST MT4", font=ctk.CTkFont(size=14, weight="bold"), height=42, fg_color="#0284c7", hover_color="#0369a1", command=self._start_backtest_thread)
        self.btn_run.pack(fill="x", padx=10, pady=(12, 6))

        self.progress_bar = ctk.CTkProgressBar(self.sidebar)
        self.progress_bar.set(0.0)
        self.progress_bar.pack(fill="x", padx=10, pady=4)

        self.lbl_status = ctk.CTkLabel(self.sidebar, text="Siap menjalankan pengujian.", font=ctk.CTkFont(size=11), text_color="#94a3b8")
        self.lbl_status.pack(padx=10, pady=(0, 15))

        # ----------------------------------------------------
        # KONTEN KANAN: Hasil, Metrik KPI & Grafik Interaktif
        # ----------------------------------------------------
        self.main_content = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_rowconfigure(1, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # Top Metric Cards Frame
        self.cards_frame = ctk.CTkFrame(self.main_content, fg_color="#1e293b", corner_radius=10)
        self.cards_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=15)
        for c in range(6):
            self.cards_frame.grid_columnconfigure(c, weight=1)

        self.card_labels = {}
        metrics = [
            ("NET PROFIT", "$0.00 (+0.0%)", "#38bdf8"),
            ("WIN RATE", "0.0%", "#4ade80"),
            ("PROFIT FACTOR", "0.00", "#fbbf24"),
            ("MAX DRAWDOWN", "0.0% ($0.00)", "#f87171"),
            ("TOTAL TRADES", "0 (0 W / 0 L)", "#e2e8f0"),
            ("AVG TRADE", "$0.00", "#c084fc")
        ]
        for idx, (title, val, clr) in enumerate(metrics):
            box = ctk.CTkFrame(self.cards_frame, fg_color="#0f172a", corner_radius=8)
            box.grid(row=0, column=idx, padx=6, pady=8, sticky="nsew")
            ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=10, weight="bold"), text_color="#94a3b8").pack(pady=(6, 0))
            lbl = ctk.CTkLabel(box, text=val, font=ctk.CTkFont(size=14, weight="bold"), text_color=clr)
            lbl.pack(pady=(0, 6))
            self.card_labels[title] = lbl

        # Tabview
        self.tabview = ctk.CTkTabview(self.main_content)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.tab_chart = self.tabview.add("📈 Grafik Pertumbuhan Modal")
        self.tab_trades = self.tabview.add("📋 Daftar Transaksi")
        self.tab_matrix = self.tabview.add("🧠 Rapor Pola AI (13 Pola)")
        self.tab_autopsy = self.tabview.add("🩺 Log Otopsi Pasca-SL")
        self.tab_calib = self.tabview.add("⚡ Auto-Kalibrasi (v3.20)")

        self._setup_chart_tab()
        self._setup_trades_tab()
        self._setup_matrix_tab()
        self._setup_autopsy_tab()
        self._setup_calib_tab()

    def _setup_chart_tab(self):
        self.fig = Figure(figsize=(9, 4.8), dpi=100, facecolor="#0f172a")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#0f172a")
        self.ax.tick_params(colors="#94a3b8", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#334155")
        self.ax.set_title("KURVA SALDO & EKUITAS AKUN (BACKTEST MT4)", color="#f8fafc", fontsize=12, fontweight="bold", pad=12)
        self.ax.grid(True, linestyle="--", alpha=0.2, color="#64748b")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.tab_chart)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def _setup_trades_tab(self):
        btn_frame = ctk.CTkFrame(self.tab_trades, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="📥 Ekspor ke CSV", width=140, height=28, fg_color="#334155", hover_color="#475569", command=self._export_trades_csv).pack(side="left")
        ctk.CTkButton(btn_frame, text="📄 Ekspor Laporan HTML", width=160, height=28, fg_color="#0369a1", hover_color="#0284c7", command=self._export_html_report).pack(side="left", padx=8)

        tree_frame = ctk.CTkFrame(self.tab_trades, fg_color="#1e293b", corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ("#", "Tipe", "Waktu Buka", "Waktu Tutup", "Harga Open", "Harga Exit", "SL", "TP", "Profit ($)", "Pips", "Alasan Exit", "Pola Lilin")
        self.tree_trades = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        for c in cols:
            self.tree_trades.heading(c, text=c)
            w = 85
            if c in ["Waktu Buka", "Waktu Tutup"]: w = 130
            elif c == "Alasan Exit": w = 150
            elif c == "Pola Lilin": w = 160
            self.tree_trades.column(c, width=w, anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_trades.yview)
        self.tree_trades.configure(yscrollcommand=scroll_y.set)
        self.tree_trades.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _setup_matrix_tab(self):
        tree_frame = ctk.CTkFrame(self.tab_matrix, fg_color="#1e293b", corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Nama Pola Teruji", "Total", "Win", "Loss", "Winrate (%)", "Score Modifier", "Status AI Matrix")
        self.tree_matrix = ttk.Treeview(tree_frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree_matrix.heading(c, text=c)
            w = 120
            if c == "Nama Pola Teruji": w = 240
            self.tree_matrix.column(c, width=w, anchor="center")

        self.tree_matrix.pack(fill="both", expand=True)

    def _setup_autopsy_tab(self):
        tree_frame = ctk.CTkFrame(self.tab_autopsy, fg_color="#1e293b", corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("Waktu", "Tiket", "Arah", "Pola Lilin Gagal", "Diagnosa Akar Masalah (7 Skenario)", "Penalti Skor", "Proteksi Arah")
        self.tree_autopsy = ttk.Treeview(tree_frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree_autopsy.heading(c, text=c)
            w = 110
            if c == "Diagnosa Akar Masalah (7 Skenario)": w = 320
            elif c == "Pola Lilin Gagal": w = 180
            self.tree_autopsy.column(c, width=w, anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_autopsy.yview)
        self.tree_autopsy.configure(yscrollcommand=scroll_y.set)
        self.tree_autopsy.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _setup_calib_tab(self):
        tree_frame = ctk.CTkFrame(self.tab_calib, fg_color="#1e293b", corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("Waktu", "Regim Pasar Adaptif", "Rasio Volatilitas (ATR14/100)", "Elevasi Skor", "Sinyal Cooldown", "SL Buffer Multiplier")
        self.tree_calib = ttk.Treeview(tree_frame, columns=cols, show="headings", height=14)
        for c in cols:
            self.tree_calib.heading(c, text=c)
            w = 130
            if c == "Regim Pasar Adaptif": w = 240
            elif c == "Rasio Volatilitas (ATR14/100)": w = 180
            self.tree_calib.column(c, width=w, anchor="center")

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_calib.yview)
        self.tree_calib.configure(yscrollcommand=scroll_y.set)
        self.tree_calib.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

    def _scan_mt4_terminals(self):
        hst_list = MT4DataReader.find_all_hst_files()
        self.available_hst = hst_list
        if not hst_list:
            self.hst_combo.configure(values=["Tidak ada file .hst ditemukan"])
            self.hst_combo.set("Tidak ada file .hst ditemukan")
            return

        display_values = []
        for h in hst_list:
            size_mb = h["size"] / (1024 * 1024)
            display_values.append(f"[{h['server']}] {h['filename']} ({size_mb:.2f} MB)")

        self.hst_combo.configure(values=display_values)
        
        # Cari default XAUUSD.i5.hst atau M5 pertama
        default_idx = 0
        for i, val in enumerate(display_values):
            if "XAUUSD.i5.hst" in val or "5.hst" in val:
                default_idx = i
                break
        self.hst_combo.set(display_values[default_idx])
        self._load_selected_hst(hst_list[default_idx]["path"])

    def _on_hst_selected(self, choice):
        for h in self.available_hst:
            if h["filename"] in choice and h["server"] in choice:
                self._load_selected_hst(h["path"])
                break

    def _browse_custom_file(self):
        path = filedialog.askopenfilename(filetypes=[("MT4 History Files", "*.hst *.csv"), ("All Files", "*.*")])
        if path:
            self._load_selected_hst(path)

    def _load_selected_hst(self, path):
        try:
            if path.lower().endswith(".csv"):
                data = MT4DataReader.read_csv(path)
            else:
                data = MT4DataReader.read_hst(path)
            self.loaded_data = data
            n_bars = len(data["bars"])
            if n_bars > 0:
                t_start = data["bars"][0]["datetime"].strftime("%Y-%m-%d")
                t_end = data["bars"][-1]["datetime"].strftime("%Y-%m-%d")
                info_text = f"Simbol: {data['symbol']} | TF: M{data['period']}\nTotal: {n_bars:,} bar lilin\nRentang: {t_start} s/d {t_end}"
            else:
                info_text = "File kosong / tidak ada bar."
            self.lbl_data_info.configure(text=info_text)
            self.lbl_status.configure(text=f"Data {data['symbol']} berhasil dimuat.")
        except Exception as e:
            messagebox.showerror("Error Baca Data", f"Gagal membaca data MT4: {str(e)}")

    def _start_backtest_thread(self):
        if not self.loaded_data or len(self.loaded_data["bars"]) < 150:
            messagebox.showwarning("Peringatan", "Silakan pilih data historis MT4 yang valid terlebih dahulu!")
            return

        self.btn_run.configure(state="disabled", text="⏳ Menguji...")
        self.progress_bar.set(0.0)
        self.lbl_status.configure(text="Menjalankan simulasi backtest...")

        # Jalankan di thread latar belakang agar GUI tetap responsif
        threading.Thread(target=self._run_backtest_worker, daemon=True).start()

    def _run_backtest_worker(self):
        try:
            params = {
                "symbol": self.loaded_data["symbol"],
                "period": self.loaded_data["period"],
                "digits": self.loaded_data["digits"],
                "initial_balance": float(self.ent_balance.get()),
                "fixed_lot": float(self.ent_lot.get()),
                "spread_points": float(self.ent_spread.get()),
                "tp_mode": "FIXED_100" if "100" in self.combo_tp_mode.get() else "RR",
                "risk_reward": float(self.ent_rr.get()),
                "fixed_tp_points": float(self.ent_tp_points.get()),
                "fixed_sl_pips": float(self.ent_sl_pips.get()),
                "use_breakeven": bool(self.chk_be.get()),
                "be_trigger_pips": 5.0,
                "be_lock_pips": 2.0,
                "use_points_trailing": bool(self.chk_points_trail.get()),
                "trail_start_points": 40.0,
                "trail_dist_points": 30.0,
                "trail_step_points": 10.0,
                "use_candle_trailing": bool(self.chk_candle_trail.get()),
                "candle_trail_buf_points": 15.0,
                "use_auto_calibration": bool(self.chk_auto_calib.get()),
                "auto_tuning_sensitivity": 1.25,
                "auto_tuning_score_step": 5.0,
                "calibration_consec_loss_max": 2,
                "use_self_healing": bool(self.chk_autopsy.get()),
                "use_directional_learning": bool(self.chk_dir_learning.get()),
                "use_hourly_learning": bool(self.chk_hourly_learning.get()),
                "use_pattern_matrix": bool(self.chk_pat_matrix.get()),
                "fast_ema": 8,
                "medium_ema": 21,
                "trend_ema": 125,
                "min_confluence_score": 65.0,
                "cooldown_bars": 2
            }

            def update_progress(pct):
                self.progress_bar.set(pct)

            engine = VikarBacktestEngine(self.loaded_data["bars"], params)
            results = engine.run(progress_callback=update_progress)
            self.backtest_results = results

            # Perbarui tampilan UI di main thread
            self.after(0, self._render_results, results)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Simulasi", f"Terjadi kesalahan saat simulasi: {str(e)}"))
        finally:
            self.after(0, lambda: self.btn_run.configure(state="normal", text="▶ JALANKAN BACKTEST MT4"))

    def _render_results(self, res):
        self.progress_bar.set(1.0)
        self.lbl_status.configure(text=f"Selesai! {res['total_trades']} transaksi dieksekusi.")

        # 1. Update Kartu Metrik KPI
        p_sign = "+" if res["net_profit"] >= 0 else ""
        p_color = "#38bdf8" if res["net_profit"] >= 0 else "#f87171"
        self.card_labels["NET PROFIT"].configure(text=f"{p_sign}${res['net_profit']:,.2f} ({p_sign}{res['net_profit_pct']}%)", text_color=p_color)
        self.card_labels["WIN RATE"].configure(text=f"{res['win_rate']}%")
        self.card_labels["PROFIT FACTOR"].configure(text=f"{res['profit_factor']:.2f}")
        self.card_labels["MAX DRAWDOWN"].configure(text=f"{res['max_drawdown_pct']:.1f}% (${res['max_drawdown_dollar']:,.2f})")
        self.card_labels["TOTAL TRADES"].configure(text=f"{res['total_trades']} ({res['wins_count']}W / {res['losses_count']}L)")
        avg_payoff = (res["net_profit"] / res["total_trades"]) if res["total_trades"] > 0 else 0.0
        self.card_labels["AVG TRADE"].configure(text=f"{'+' if avg_payoff>=0 else ''}${avg_payoff:.2f}")

        # 2. Render Grafik Pertumbuhan Modal
        self.ax.clear()
        self.ax.set_facecolor("#0f172a")
        self.ax.grid(True, linestyle="--", alpha=0.2, color="#64748b")
        self.ax.tick_params(colors="#94a3b8", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#334155")

        eq_dates = [e["datetime"] for e in res["equity_curve"]]
        eq_bals = [e["balance"] for e in res["equity_curve"]]

        self.ax.plot(eq_dates, eq_bals, color="#38bdf8", linewidth=2.0, label="Saldo Akun ($)")
        self.ax.fill_between(eq_dates, res["initial_balance"], eq_bals, where=np.array(eq_bals) >= res["initial_balance"], alpha=0.15, color="#38bdf8")
        self.ax.fill_between(eq_dates, res["initial_balance"], eq_bals, where=np.array(eq_bals) < res["initial_balance"], alpha=0.20, color="#f87171")
        self.ax.axhline(res["initial_balance"], color="#64748b", linestyle=":", linewidth=1.2)

        self.ax.set_title(f"KURVA PERTUMBUHAN MODAL ({res['symbol']} M{res['period']}) - TP 100 POINT & TRAILING STOP", color="#f8fafc", fontsize=11, fontweight="bold", pad=10)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        self.fig.autofmt_xdate()
        self.canvas.draw()

        # 3. Update Daftar Transaksi Table
        for row in self.tree_trades.get_children():
            self.tree_trades.delete(row)
        for t in res["trades"]:
            p_str = f"{'+' if t['pnl_dollar']>=0 else ''}${t['pnl_dollar']:.2f}"
            self.tree_trades.insert("", "end", values=(
                t["ticket"],
                t["type"],
                t["open_time"].strftime("%Y-%m-%d %H:%M"),
                t["close_time"].strftime("%Y-%m-%d %H:%M"),
                f"{t['open_price']:.2f}",
                f"{t['close_price']:.2f}",
                f"{t['sl']:.2f}",
                f"{t['tp']:.2f}",
                p_str,
                f"{t['pnl_pips']:.1f}",
                t["exit_reason"],
                t["pattern_name"]
            ))

        # 4. Update Pattern Matrix Table
        for row in self.tree_matrix.get_children():
            self.tree_matrix.delete(row)
        for p in res["pattern_matrix"]:
            status = "BLACKLISTED" if p["blacklisted"] else ("BOOST (+10)" if p["modifier"] > 0 else "NORMAL")
            mod_str = f"{'+' if p['modifier']>0 else ''}{p['modifier']:.0f}"
            self.tree_matrix.insert("", "end", values=(
                p["id"],
                p["name"],
                p["total"],
                p["wins"],
                p["losses"],
                f"{p['winrate']:.1f}%",
                mod_str,
                status
            ))

        # 5. Update Autopsy Logs Table
        for row in self.tree_autopsy.get_children():
            self.tree_autopsy.delete(row)
        for a in res["autopsy_logs"]:
            self.tree_autopsy.insert("", "end", values=(
                a["time"].strftime("%Y-%m-%d %H:%M"),
                a["ticket"],
                a["type"],
                a["pattern"],
                a["reason"],
                a["penalty"],
                a["dir_guard"]
            ))

        # 6. Update Auto-Calibration Logs Table
        for row in self.tree_calib.get_children():
            self.tree_calib.delete(row)
        for c in res.get("calib_logs", []):
            self.tree_calib.insert("", "end", values=(
                c["time"].strftime("%Y-%m-%d %H:%M"),
                c["regime"],
                c["vol_ratio"],
                c["score_elev"],
                c["cooldown"],
                c["sl_mult"]
            ))

    def _export_trades_csv(self):
        if not self.backtest_results or not self.backtest_results["trades"]:
            messagebox.showwarning("Peringatan", "Tidak ada hasil transaksi untuk diekspor.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if path:
            df = pd.DataFrame(self.backtest_results["trades"])
            df.to_csv(path, index=False)
            messagebox.showinfo("Sukses", f"Daftar transaksi berhasil disimpan ke:\n{path}")

    def _export_html_report(self):
        if not self.backtest_results:
            messagebox.showwarning("Peringatan", "Tidak ada hasil backtest untuk diekspor.")
            return
        res = self.backtest_results
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML Files", "*.html")])
        if path:
            p_cls = "win" if res['net_profit'] >= 0 else "loss"
            p_sgn = "+" if res['net_profit'] >= 0 else ""
            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Laporan Backtest VIKAR EA 4-Pillar Pro MT4</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0f172a; color: #f8fafc; padding: 25px; }}
        .header {{ background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border-left: 6px solid #38bdf8; }}
        h1 {{ margin: 0; color: #38bdf8; font-size: 24px; }}
        .grid {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px; }}
        .card {{ background: #1e293b; padding: 15px; border-radius: 8px; text-align: center; }}
        .card-val {{ font-size: 18px; font-weight: bold; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; margin-top: 15px; font-size: 12px; }}
        th, td {{ padding: 10px; text-align: center; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; }}
        .win {{ color: #4ade80; font-weight: bold; }}
        .loss {{ color: #f87171; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>VIKAR EA 4-PILLAR PRO MT4 - LAPORAN RESMI PENGUJIAN HISTORIS</h1>
        <p>Instrumen: <b>{res['symbol']}</b> | Timeframe: <b>M{res['period']}</b> | Target TP: <b>100 Point</b> | Trailing: <b>Candle & Points Aktif</b></p>
        <p>Rentang Data: {res['start_date']} s/d {res['end_date']} ({res['total_bars']:,} Bars Lilin)</p>
    </div>
    <div class="grid">
        <div class="card"><div>NET PROFIT</div><div class="card-val {p_cls}">{p_sgn}${res['net_profit']:,.2f} ({p_sgn}{res['net_profit_pct']}%)</div></div>
        <div class="card"><div>WIN RATE</div><div class="card-val" style="color:#4ade80;">{res['win_rate']}%</div></div>
        <div class="card"><div>PROFIT FACTOR</div><div class="card-val" style="color:#fbbf24;">{res['profit_factor']:.2f}</div></div>
        <div class="card"><div>MAX DRAWDOWN</div><div class="card-val" style="color:#f87171;">{res['max_drawdown_pct']}% (${res['max_drawdown_dollar']:,.2f})</div></div>
        <div class="card"><div>TOTAL TRADES</div><div class="card-val">{res['total_trades']} ({res['wins_count']}W / {res['losses_count']}L)</div></div>
        <div class="card"><div>MODAL AKHIR</div><div class="card-val">${res['final_balance']:,.2f}</div></div>
    </div>
    <h2>Daftar Riwayat Transaksi Eksekusi</h2>
    <table>
        <tr><th>#</th><th>Tipe</th><th>Waktu Buka</th><th>Waktu Tutup</th><th>Open</th><th>Exit</th><th>Profit ($)</th><th>Pips</th><th>Alasan Exit</th><th>Pola Lilin</th></tr>
        {"".join([f"<tr><td>{t['ticket']}</td><td>{t['type']}</td><td>{t['open_time']}</td><td>{t['close_time']}</td><td>{t['open_price']}</td><td>{t['close_price']}</td><td class='{'win' if t['pnl_dollar']>0 else 'loss'}'>${t['pnl_dollar']:.2f}</td><td>{t['pnl_pips']}</td><td>{t['exit_reason']}</td><td>{t['pattern_name']}</td></tr>" for t in res['trades']])}
    </table>
</body>
</html>"""
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            messagebox.showinfo("Sukses", f"Laporan HTML berhasil disimpan ke:\n{path}")


if __name__ == "__main__":
    app = VikarBacktestStudio()
    app.mainloop()
