import os
from PIL import Image, ImageDraw, ImageFont

def create_annotated_chart():
    img_path = r'e:\Python\STRATEGY\VIKAR_STATEGI\chart_raw_latest.png'
    out_path = r'e:\Python\STRATEGY\VIKAR_STATEGI\chart_annotated_smc_case4.png'
    
    base = Image.open(img_path).convert('RGBA')
    w, h = base.size
    
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Fonts
    font_title   = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 11)
    font_sub     = ImageFont.truetype(r'C:\Windows\Fonts\segoeui.ttf', 8)
    font_bold    = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 9)
    font_bold_sm = ImageFont.truetype(r'C:\Windows\Fonts\segoeuib.ttf', 8)
    font_mono    = ImageFont.truetype(r'C:\Windows\Fonts\consola.ttf', 8)
    
    def p_to_y(price):
        return int(round(127.0 + (4380.0 - price) * 1.5143))

    def draw_badge(d, text, x, y, bg_col, text_col, font, pad_x=5, pad_y=3):
        bbox = font.getbbox(text)
        bw = bbox[2] - bbox[0] + pad_x * 2
        bh = bbox[3] - bbox[1] + pad_y * 2
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=3, fill=bg_col, outline=(51, 65, 85, 230), width=1)
        d.text((x + pad_x, y + pad_y - bbox[1]), text, fill=text_col, font=font)
        return bw, bh

    # 1. HEADER BANNER (Top Left)
    draw.rounded_rectangle([10, 10, 485, 52], radius=5, fill=(15, 23, 42, 245), outline=(56, 189, 248, 240), width=1)
    draw.text((18, 14), "VIKAR 4-PILLAR SMC MASTERCLASS: BEDAH ANATOMI XAU/USD", fill=(56, 189, 248, 255), font=font_title)
    draw.text((18, 30), "Analisis Real-Market: Liquidity Sweep, Bullish CHoCH, Multi-Tier FVG & Demand Order Block", fill=(226, 232, 240, 255), font=font_sub)

    # 2. LIQUIDITY SWEEP (SSL POOL & STOP HUNT)
    y_ssl = p_to_y(4264)  # ~303
    y_dump = p_to_y(4240) # ~339
    
    # Red dashed line across the Sep 15 low
    for x_dash in range(60, 470, 8):
        draw.line([(x_dash, y_ssl), (min(x_dash + 5, 470), y_ssl)], fill=(239, 68, 68, 220), width=1)
    draw_badge(draw, "SELL-SIDE LIQUIDITY (SSL POOL) ~4.264", 75, y_ssl - 16, (30, 41, 59, 230), (248, 113, 113, 255), font_bold_sm)

    # Downward arrow showing stop hunt plunge
    draw.line([(453, y_ssl), (453, y_dump)], fill=(239, 68, 68, 255), width=2)
    draw.polygon([(449, y_dump - 6), (457, y_dump - 6), (453, y_dump)], fill=(239, 68, 68, 255))
    draw_badge(draw, "STOP HUNT / SWEEP (Wick -120 Pips ke 4.240)", 360, y_dump + 6, (15, 23, 42, 245), (251, 113, 133, 255), font_bold)

    # 3. PRIMARY BULLISH ORDER BLOCK (Demand Base: 4.240 - 4.260)
    y_ob_top = p_to_y(4260) # ~309
    y_ob_bot = p_to_y(4240) # ~339
    draw.rectangle([442, y_ob_top, 560, y_ob_bot], fill=(16, 185, 129, 40), outline=(5, 150, 105, 230), width=1)
    draw_badge(draw, "DEMAND BASE / BULLISH OB (4.240 - 4.260)", 445, y_ob_top - 16, (15, 23, 42, 235), (52, 211, 153, 255), font_bold_sm)

    # 4. BULLISH CHoCH (Break above 4.300)
    y_choch = p_to_y(4300) # ~248
    for x_dash in range(470, 565, 8):
        draw.line([(x_dash, y_choch), (min(x_dash + 5, 565), y_choch)], fill=(56, 189, 248, 220), width=1)
    draw_badge(draw, "BULLISH CHoCH (PEMBALIKAN STRUKTUR 4.300)", 478, y_choch - 15, (15, 23, 42, 235), (56, 189, 248, 255), font_bold_sm)

    # 5. FAIR VALUE GAP 1 (FVG 4.280 - 4.300)
    y_fvg1_top = p_to_y(4300)
    y_fvg1_bot = p_to_y(4280)
    draw.rectangle([485, y_fvg1_top, 535, y_fvg1_bot], fill=(245, 158, 11, 40), outline=(217, 119, 6, 210), width=1)
    draw_badge(draw, "FVG 1 IMBALANCE", 484, y_fvg1_top + 10, (15, 23, 42, 230), (251, 191, 36, 255), font_mono)

    # 6. BULLISH BOS (Break of Structure above 4.370 to 4.383)
    y_bos = p_to_y(4370) # ~142
    draw.line([(425, y_bos), (635, y_bos)], fill=(34, 197, 94, 220), width=1)
    draw_badge(draw, "BULLISH BOS (HIGHER HIGH EXPANSION 4.383)", 465, y_bos - 16, (15, 23, 42, 235), (74, 222, 128, 255), font_bold_sm)

    # 7. BEARISH REJECTION SUPPLY PEAK (4.380 - 4.385)
    y_peak_top = p_to_y(4385)
    y_peak_bot = p_to_y(4378)
    draw.rectangle([618, y_peak_top, 665, y_peak_bot], fill=(244, 63, 94, 50), outline=(225, 29, 72, 230), width=1)
    draw_badge(draw, "BEARISH REJECTION OB", 570, y_peak_top - 15, (15, 23, 42, 235), (251, 113, 133, 255), font_bold_sm)

    # 8. SECONDARY BULLISH OB & FVG 2 (4.335 - 4.355)
    y_fvg2_top = p_to_y(4355)
    y_fvg2_bot = p_to_y(4335)
    draw.rectangle([580, y_fvg2_top, 665, y_fvg2_bot], fill=(6, 182, 212, 40), outline=(8, 145, 178, 220), width=1)
    draw_badge(draw, "BULLISH OB & FVG 2 (VALUE ZONE 4.335 - 4.355)", 555, y_fvg2_bot + 4, (15, 23, 42, 235), (103, 232, 249, 255), font_bold_sm)

    # 9. CURRENT PRICE CALLOUT (4.360,14) - Adjusted position to avoid any collision
    y_curr = p_to_y(4360.14)
    x_curr = 668
    # Target reticle on current candle
    draw.ellipse([x_curr - 4, y_curr - 4, x_curr + 4, y_curr + 4], outline=(239, 68, 68, 255), width=2)
    
    # Arrow to callout box positioned to the right
    x_box = 690
    y_box = 145
    draw.line([(x_curr + 5, y_curr), (x_box, y_box + 20)], fill=(56, 189, 248, 255), width=1)
    draw.rounded_rectangle([x_box, y_box, x_box + 225, y_box + 58], radius=5, fill=(15, 23, 42, 248), outline=(56, 189, 248, 255), width=1)
    draw.text((x_box + 8, y_box + 6), "HARGA SAAT INI: 4.360,14", fill=(251, 191, 36, 255), font=font_bold)
    draw.text((x_box + 8, y_box + 22), "• Pullback Menguji FVG 2 & OB Diskon", fill=(226, 232, 240, 255), font=font_sub)
    draw.text((x_box + 8, y_box + 37), "• SETUP BUY REBOUND GRADE A+", fill=(52, 211, 153, 255), font=font_bold)

    # 10. LEGEND CARD (Bottom Left - Solid background to cleanly obscure background indicator noise)
    draw.rounded_rectangle([10, 422, 450, 465], radius=4, fill=(15, 23, 42, 255), outline=(51, 65, 85, 240), width=1)
    draw.text((18, 431), "LEGENDA SMC:", fill=(148, 163, 184, 255), font=font_bold_sm)
    
    draw.rectangle([95, 433, 103, 441], fill=(16, 185, 129, 255))
    draw.text((107, 432), "Order Block (OB)", fill=(226, 232, 240, 255), font=font_sub)

    draw.rectangle([185, 433, 193, 441], fill=(245, 158, 11, 255))
    draw.text((197, 432), "Fair Value Gap (FVG)", fill=(226, 232, 240, 255), font=font_sub)

    draw.rectangle([295, 433, 303, 441], fill=(239, 68, 68, 255))
    draw.text((307, 432), "Liquidity Sweep", fill=(226, 232, 240, 255), font=font_sub)

    draw.rectangle([385, 433, 393, 441], fill=(56, 189, 248, 255))
    draw.text((397, 432), "CHoCH / BOS", fill=(226, 232, 240, 255), font=font_sub)

    # Combine base image with overlay
    final_img = Image.alpha_composite(base, overlay).convert('RGB')
    final_img.save(out_path, quality=95)
    
    # Also copy to artifact directory
    dst_art = r'C:\Users\vikar\.gemini\antigravity-ide\brain\35bc941c-56ef-442a-b8ea-185da534d5c0\chart_annotated_smc_case4.png'
    final_img.save(dst_art, quality=95)
    print(f'Successfully updated annotated chart at: {out_path} and {dst_art}')

if __name__ == '__main__':
    create_annotated_chart()
