import re

file_path = r"e:\Python\STRATEGY\run_backtest_jan2026_to_now.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update BUY setup in simulate_m5_period
old_buy_check = """            if (is_pullback and candle_ok and score >= min_confluence) or is_bull_trap:
                open_p = opens[i]"""

new_buy_check = """            # v3.40 AI Candlestick Shield (Anti-Doji, Anti-Exhaustion, Anti-Overextended)
            candle_body = abs(closes[i - 1] - opens[i - 1])
            body_pct = (candle_body / bar_range) * 100.0
            upper_wick = highs[i - 1] - max(opens[i - 1], closes[i - 1])
            upper_wick_pct = (upper_wick / bar_range) * 100.0

            if body_pct <= 22.0 and not is_bull_trap:
                continue
            if upper_wick_pct >= 45.0 and not is_bull_trap:
                continue
            if is_engulf and ((closes[i - 1] - ema21[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value):
                continue

            if (is_pullback and candle_ok and score >= min_confluence) or is_bull_trap:
                open_p = opens[i]"""

if old_buy_check in content:
    content = content.replace(old_buy_check, new_buy_check)
    print("[+] BUY AI Shield successfully injected into simulation.")
else:
    print("[-] BUY check not found.")

# 2. Update SELL setup in simulate_m5_period
old_sell_check = """            if (is_pullback and candle_ok and score >= min_confluence) or is_bear_trap:
                open_p = opens[i]"""

new_sell_check = """            # v3.40 AI Candlestick Shield (Anti-Doji, Anti-Exhaustion, Anti-Overextended)
            candle_body = abs(closes[i - 1] - opens[i - 1])
            body_pct = (candle_body / bar_range) * 100.0
            lower_wick = min(opens[i - 1], closes[i - 1]) - lows[i - 1]
            lower_wick_pct = (lower_wick / bar_range) * 100.0

            if body_pct <= 22.0 and not is_bear_trap:
                continue
            if lower_wick_pct >= 45.0 and not is_bear_trap:
                continue
            if is_engulf and ((ema21[i - 1] - closes[i - 1]) / pip_value) >= (1.5 * current_atr / pip_value):
                continue

            if (is_pullback and candle_ok and score >= min_confluence) or is_bear_trap:
                open_p = opens[i]"""

if old_sell_check in content:
    content = content.replace(old_sell_check, new_sell_check)
    print("[+] SELL AI Shield successfully injected into simulation.")
else:
    print("[-] SELL check not found.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("[+] run_backtest_jan2026_to_now.py updated with v3.40 AI Candlestick Shield!")
