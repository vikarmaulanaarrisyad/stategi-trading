"""
Wrapper Klien MetaTrader 5 (MT5) untuk Python
Mengelola koneksi, pengambilan data rates, eksekusi order BUY/SELL,
modifikasi Stop Loss/Take Profit, dan penutupan posisi.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    mt5 = None
    MT5_AVAILABLE = False

TIMEFRAME_MAP = {
    "M1":  1,     # mt5.TIMEFRAME_M1
    "M5":  5,     # mt5.TIMEFRAME_M5
    "M15": 15,    # mt5.TIMEFRAME_M15
    "M30": 30,    # mt5.TIMEFRAME_M30
    "H1":  16385, # mt5.TIMEFRAME_H1
    "H4":  16388, # mt5.TIMEFRAME_H4
    "D1":  16408, # mt5.TIMEFRAME_D1
    "W1":  32769  # mt5.TIMEFRAME_W1
}

class MT5Client:
    def __init__(self):
        if not MT5_AVAILABLE:
            print("[PERINGATAN] Modul 'MetaTrader5' belum terinstall atau tidak tersedia pada platform ini.")

    def initialize(self, path: Optional[str] = None, login: Optional[int] = None, 
                   password: Optional[str] = None, server: Optional[str] = None) -> bool:
        """Inisialisasi koneksi ke terminal MetaTrader 5."""
        if not MT5_AVAILABLE:
            return False

        kwargs = {}
        if path:
            kwargs['path'] = path
        if login:
            kwargs['login'] = login
        if password:
            kwargs['password'] = password
        if server:
            kwargs['server'] = server

        if not mt5.initialize(**kwargs):
            err = mt5.last_error()
            print(f"[MT5 Error] Gagal inisialisasi MT5: {err}")
            return False

        account = mt5.account_info()
        if account is None:
            print("[MT5 Error] Gagal mendapatkan informasi akun.")
            return False

        print(f"[MT5 Terkoneksi] Akun: #{account.login} | Nama: {account.name} | Server: {account.server} | Saldo: ${account.balance:.2f} | Equity: ${account.equity:.2f}")
        return True

    def shutdown(self):
        """Menutup koneksi terminal MT5."""
        if MT5_AVAILABLE:
            mt5.shutdown()
            print("[MT5] Koneksi diputus dengan aman.")

    def get_timeframe_code(self, tf_str: str) -> int:
        """Mendapatkan kode timeframe MT5 dari string (misal: 'M15')."""
        if MT5_AVAILABLE:
            mapping = {
                "M1": mt5.TIMEFRAME_M1,
                "M5": mt5.TIMEFRAME_M5,
                "M15": mt5.TIMEFRAME_M15,
                "M30": mt5.TIMEFRAME_M30,
                "H1": mt5.TIMEFRAME_H1,
                "H4": mt5.TIMEFRAME_H4,
                "D1": mt5.TIMEFRAME_D1,
                "W1": mt5.TIMEFRAME_W1,
            }
            return mapping.get(tf_str.upper(), mt5.TIMEFRAME_M15)
        return TIMEFRAME_MAP.get(tf_str.upper(), 15)

    def resolve_symbol(self, symbol: str) -> str:
        """Mencari nama simbol yang cocok jika broker menggunakan akhiran seperti .dmb, .m, dsb."""
        if not MT5_AVAILABLE:
            return symbol
            
        sym_info = mt5.symbol_info(symbol)
        if sym_info is not None:
            return symbol

        # Jika tidak ditemukan langsung, cari simbol serupa
        all_symbols = mt5.symbols_get()
        if all_symbols:
            clean_sym = symbol.upper().replace(".DMB", "").replace(".M", "").replace(".RAW", "")
            for s in all_symbols:
                s_name = s.name.upper()
                if clean_sym in s_name or (clean_sym == "XAUUSD" and "GOLD" in s_name):
                    print(f"[MT5 Info] Menggunakan simbol broker: '{s.name}' (sesuai '{symbol}')")
                    return s.name

        return symbol

    def ensure_symbol_selected(self, symbol: str) -> Optional[str]:
        """Memastikan simbol aktif di Market Watch dan mengembalikan nama simbol broker."""
        if not MT5_AVAILABLE:
            return None
        real_sym = self.resolve_symbol(symbol)
        sym_info = mt5.symbol_info(real_sym)
        if sym_info is None:
            print(f"[MT5 Error] Simbol {symbol} / {real_sym} tidak ditemukan di broker!")
            return None
        if not sym_info.visible:
            if not mt5.symbol_select(real_sym, True):
                print(f"[MT5 Error] Gagal menampilkan simbol {real_sym} di Market Watch.")
                return None
        return real_sym

    def get_symbol_info(self, symbol: str):
        """Mengambil data spesifikasi simbol dari broker."""
        if not MT5_AVAILABLE:
            return None
        real_sym = self.ensure_symbol_selected(symbol)
        if not real_sym:
            return None
        return mt5.symbol_info(real_sym)

    def get_rates(self, symbol: str, timeframe_str: str, count: int = 150) -> Optional[pd.DataFrame]:
        """
        Mengambil data candlestick historis dari MT5.
        Mengembalikan DataFrame dengan kolom: ['time', 'open', 'high', 'low', 'close', 'tick_volume']
        """
        if not MT5_AVAILABLE:
            return None

        real_sym = self.ensure_symbol_selected(symbol)
        if not real_sym:
            return None

        tf_code = self.get_timeframe_code(timeframe_str)
        rates = mt5.copy_rates_from_pos(real_sym, tf_code, 0, count)
        
        if rates is None or len(rates) == 0:
            print(f"[MT5 Error] Gagal mengambil data rates {real_sym} {timeframe_str}: {mt5.last_error()}")
            return None

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        return df

    def get_current_tick(self, symbol: str):
        """Mengambil tick harga saat ini (ask, bid, spread)."""
        if not MT5_AVAILABLE:
            return None
        real_sym = self.ensure_symbol_selected(symbol)
        if not real_sym:
            return None
        return mt5.symbol_info_tick(real_sym)

    def get_filling_type(self, symbol_info) -> int:
        """Mendeteksi tipe filling mode yang didukung broker (FOK, IOC, Return)."""
        if not MT5_AVAILABLE or symbol_info is None:
            return 0
            
        filling_mode = symbol_info.filling_mode
        if filling_mode & mt5.ORDER_FILLING_FOK:
            return mt5.ORDER_FILLING_FOK
        elif filling_mode & mt5.ORDER_FILLING_IOC:
            return mt5.ORDER_FILLING_IOC
        return mt5.ORDER_FILLING_RETURN

    def open_buy(self, symbol: str, lot: float, sl: float, tp: float, 
                 magic: int, comment: str) -> Optional[int]:
        """Eksekusi order BUY instan (Market Order)."""
        if not MT5_AVAILABLE:
            return None

        real_sym = self.ensure_symbol_selected(symbol)
        if not real_sym:
            return None

        tick = mt5.symbol_info_tick(real_sym)
        sym_info = mt5.symbol_info(real_sym)
        if tick is None or sym_info is None:
            print("[Order Error] Tidak dapat membaca harga tick.")
            return None

        ask = tick.ask
        digits = sym_info.digits
        price = round(ask, digits)
        sl_norm = round(sl, digits) if sl > 0 else 0.0
        tp_norm = round(tp, digits) if tp > 0 else 0.0

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": real_sym,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": sl_norm,
            "tp": tp_norm,
            "deviation": 20,
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self.get_filling_type(sym_info),
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            ret_desc = result.comment if result else mt5.last_error()
            ret_code = result.retcode if result else -1
            print(f"[ORDER BUY GAGAL] RetCode: {ret_code} | Info: {ret_desc}")
            return None

        print(f"[ORDER BUY SUKSES] Ticket: #{result.order} | Simbol: {real_sym} | Lot: {lot} | Harga: {price} | SL: {sl_norm} | TP: {tp_norm}")
        return result.order

    def open_sell(self, symbol: str, lot: float, sl: float, tp: float, 
                  magic: int, comment: str) -> Optional[int]:
        """Eksekusi order SELL instan (Market Order)."""
        if not MT5_AVAILABLE:
            return None

        real_sym = self.ensure_symbol_selected(symbol)
        if not real_sym:
            return None

        tick = mt5.symbol_info_tick(real_sym)
        sym_info = mt5.symbol_info(real_sym)
        if tick is None or sym_info is None:
            print("[Order Error] Tidak dapat membaca harga tick.")
            return None

        bid = tick.bid
        digits = sym_info.digits
        price = round(bid, digits)
        sl_norm = round(sl, digits) if sl > 0 else 0.0
        tp_norm = round(tp, digits) if tp > 0 else 0.0

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": real_sym,
            "volume": float(lot),
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": sl_norm,
            "tp": tp_norm,
            "deviation": 20,
            "magic": int(magic),
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self.get_filling_type(sym_info),
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            ret_desc = result.comment if result else mt5.last_error()
            ret_code = result.retcode if result else -1
            print(f"[ORDER SELL GAGAL] RetCode: {ret_code} | Info: {ret_desc}")
            return None

        print(f"[ORDER SELL SUKSES] Ticket: #{result.order} | Lot: {lot} | Harga: {price} | SL: {sl_norm} | TP: {tp_norm}")
        return result.order

    def modify_position(self, ticket: int, new_sl: float, current_tp: float) -> bool:
        """Mengubah Stop Loss posisi aktif (untuk BEP atau Trailing Stop)."""
        if not MT5_AVAILABLE:
            return False

        pos = mt5.positions_get(ticket=ticket)
        if pos is None or len(pos) == 0:
            return False

        pos_item = pos[0]
        sym_info = mt5.symbol_info(pos_item.symbol)
        digits = sym_info.digits if sym_info else 2

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "symbol": pos_item.symbol,
            "sl": round(new_sl, digits),
            "tp": round(current_tp, digits),
        }

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            return False
        return True

    def close_position(self, ticket: int, volume: Optional[float] = None) -> bool:
        """Menutup posisi market aktif (penuh atau sebagian/partial close)."""
        if not MT5_AVAILABLE:
            return False

        pos = mt5.positions_get(ticket=ticket)
        if pos is None or len(pos) == 0:
            return False

        pos_item = pos[0]
        symbol = pos_item.symbol
        current_lot = pos_item.volume
        
        # Tentukan volume yang akan ditutup (penuh atau partial)
        if volume is not None and volume > 0 and volume < current_lot:
            lot = round(volume, 2)
        else:
            lot = current_lot

        order_type = mt5.ORDER_TYPE_SELL if pos_item.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return False
            
        price = tick.bid if pos_item.type == mt5.ORDER_TYPE_BUY else tick.ask
        sym_info = mt5.symbol_info(symbol)

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": symbol,
            "volume": float(lot),
            "type": order_type,
            "price": price,
            "deviation": 20,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": self.get_filling_type(sym_info),
        }

        result = mt5.order_send(request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            return True
        else:
            err = result.comment if result else mt5.last_error()
            print(f"[Close/Partial Gagal] Ticket #{ticket} | Info: {err}")
            return False

    def get_server_time(self, symbol: str) -> datetime:
        """Mengambil waktu server broker terkini dari tick harga."""
        if MT5_AVAILABLE:
            tick = mt5.symbol_info_tick(symbol)
            if tick and tick.time > 0:
                return datetime.fromtimestamp(tick.time)
        return datetime.now()

    def get_open_positions(self, symbol: Optional[str] = None, magic: Optional[int] = None):
        """Mengambil list posisi yang sedang terbuka."""
        if not MT5_AVAILABLE:
            return []

        if symbol:
            positions = mt5.positions_get(symbol=symbol)
        else:
            positions = mt5.positions_get()

        if positions is None:
            return []

        if magic is not None:
            return [p for p in positions if p.magic == magic]
        return list(positions)

    def get_daily_closed_deals(self, symbol: str, magic: int) -> List[Any]:
        """Mengambil riwayat transaksi tertutup hari ini."""
        if not MT5_AVAILABLE:
            return []

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Ambil rentang aman dari awal hari ini hingga 24 jam ke depan untuk mengantisipasi selisih timezone broker
        deals = mt5.history_deals_get(today_start - timedelta(hours=4), datetime.now() + timedelta(hours=4))
        if deals is None:
            return []

        filtered = []
        for d in deals:
            if d.symbol == symbol and d.magic == magic and d.entry == mt5.DEAL_ENTRY_OUT:
                filtered.append(d)
        return filtered
