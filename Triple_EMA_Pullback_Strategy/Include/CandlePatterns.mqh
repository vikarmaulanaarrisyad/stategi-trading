//+------------------------------------------------------------------+
//|                                              CandlePatterns.mqh  |
//|                        Triple EMA Pullback Strategy Library      |
//|                                  Copyright 2026, XAUUSD Trader   |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, XAUUSD Senior Trader"
#property link      ""
#property strict

//+------------------------------------------------------------------+
//| Enum Pola Candlestick                                            |
//+------------------------------------------------------------------+
enum ENUM_CANDLE_PATTERN
  {
   PATTERN_NONE = 0,
   // Pola Bullish (1 - 9)
   PATTERN_HAMMER,
   PATTERN_BULLISH_PINBAR,
   PATTERN_BULLISH_ENGULFING,
   PATTERN_MORNING_STAR,
   PATTERN_PIERCING_LINE,
   PATTERN_THREE_WHITE_SOLDIERS,
   PATTERN_BULLISH_DOJI,
   PATTERN_BULLISH_INSIDE_BAR,
   PATTERN_BULLISH_TWO_CANDLE_REJECTION,
   
   // Pola Bearish (10 - 18)
   PATTERN_SHOOTING_STAR,
   PATTERN_BEARISH_PINBAR,
   PATTERN_BEARISH_ENGULFING,
   PATTERN_DARK_CLOUD_COVER,
   PATTERN_EVENING_STAR,
   PATTERN_THREE_BLACK_CROWS,
   PATTERN_BEARISH_DOJI,
   PATTERN_BEARISH_INSIDE_BAR,
   PATTERN_BEARISH_TWO_CANDLE_REJECTION
  };

//+------------------------------------------------------------------+
//| Fungsi Mendapatkan Nama Pola Dalam Teks                          |
//+------------------------------------------------------------------+
string GetPatternName(ENUM_CANDLE_PATTERN pattern)
  {
   switch(pattern)
     {
      case PATTERN_HAMMER:                       return "Hammer (Bullish Rejection)";
      case PATTERN_BULLISH_PINBAR:               return "Bullish Pin Bar";
      case PATTERN_BULLISH_ENGULFING:            return "Bullish Engulfing";
      case PATTERN_MORNING_STAR:                 return "Morning Star (3 Candles)";
      case PATTERN_PIERCING_LINE:                return "Piercing Line";
      case PATTERN_THREE_WHITE_SOLDIERS:         return "Three White Soldiers";
      case PATTERN_BULLISH_DOJI:                 return "Bullish Doji Rejection";
      case PATTERN_BULLISH_INSIDE_BAR:           return "Bullish Inside Bar Breakout";
      case PATTERN_BULLISH_TWO_CANDLE_REJECTION: return "Two Candle Bullish Rejection";
      
      case PATTERN_SHOOTING_STAR:                return "Shooting Star (Bearish Rejection)";
      case PATTERN_BEARISH_PINBAR:               return "Bearish Pin Bar";
      case PATTERN_BEARISH_ENGULFING:            return "Bearish Engulfing";
      case PATTERN_DARK_CLOUD_COVER:             return "Dark Cloud Cover";
      case PATTERN_EVENING_STAR:                 return "Evening Star (3 Candles)";
      case PATTERN_THREE_BLACK_CROWS:            return "Three Black Crows";
      case PATTERN_BEARISH_DOJI:                 return "Bearish Doji Rejection";
      case PATTERN_BEARISH_INSIDE_BAR:           return "Bearish Inside Bar Breakdown";
      case PATTERN_BEARISH_TWO_CANDLE_REJECTION: return "Two Candle Bearish Rejection";
      default:                                   return "No Pattern";
     }
  }

//+------------------------------------------------------------------+
//| Kelas Detektor Candlestick Price Action                          |
//+------------------------------------------------------------------+
class CCandlePatternDetector
  {
private:
   double            m_min_body_ratio;

public:
                     CCandlePatternDetector() : m_min_body_ratio(0.05) {}
                    ~CCandlePatternDetector() {}

   // Deteksi Pola Bullish pada bar shift (biasanya bar 1)
   ENUM_CANDLE_PATTERN DetectBullishPattern(const MqlRates &rates[], int shift, double ema8, double ema21, double ema125);

   // Deteksi Pola Bearish pada bar shift (biasanya bar 1)
   ENUM_CANDLE_PATTERN DetectBearishPattern(const MqlRates &rates[], int shift, double ema8, double ema21, double ema125);

private:
   bool              IsTouchEMA21or8(double low, double high, double ema8, double ema21);
  };

//+------------------------------------------------------------------+
//| Cek apakah candle menyentuh / berada di zona EMA 8 - EMA 21      |
//+------------------------------------------------------------------+
bool CCandlePatternDetector::IsTouchEMA21or8(double low, double high, double ema8, double ema21)
  {
   double upper_zone = MathMax(ema8, ema21);
   double lower_zone = MathMin(ema8, ema21);
   double buffer = (upper_zone - lower_zone) * 0.3; // Toleransi sentuh
   
   return (low <= (upper_zone + buffer) && high >= (lower_zone - buffer));
  }

//+------------------------------------------------------------------+
//| Deteksi 9 Pola Candlestick Bullish                               |
//+------------------------------------------------------------------+
ENUM_CANDLE_PATTERN CCandlePatternDetector::DetectBullishPattern(const MqlRates &rates[], int s, double ema8, double ema21, double ema125)
  {
   // Pastikan index mencukupi (minimal 4 candle ke belakang)
   if(s < 1 || s + 3 >= ArraySize(rates)) return PATTERN_NONE;

   // Definisi candle s (candle konfirmasi yang baru saja close)
   double o0 = rates[s].open;
   double h0 = rates[s].high;
   double l0 = rates[s].low;
   double c0 = rates[s].close;
   double range0 = h0 - l0;
   if(range0 <= 0.0) return PATTERN_NONE;
   
   double body0 = MathAbs(c0 - o0);
   double lower_wick0 = (c0 >= o0) ? (o0 - l0) : (c0 - l0);
   double upper_wick0 = (c0 >= o0) ? (h0 - c0) : (h0 - o0);
   bool isBullish0 = (c0 > o0);

   // Definisi candle s+1 (1 candle sebelumnya)
   double o1 = rates[s+1].open;
   double h1 = rates[s+1].high;
   double l1 = rates[s+1].low;
   double c1 = rates[s+1].close;
   double range1 = h1 - l1;
   double body1 = MathAbs(c1 - o1);
   bool isBearish1 = (c1 < o1);

   // Definisi candle s+2 (2 candle sebelumnya)
   double o2 = rates[s+2].open;
   double h2 = rates[s+2].high;
   double l2 = rates[s+2].low;
   double c2 = rates[s+2].close;

   // Validasi dasar: Low candle harus menyentuh zona pullback EMA 8/21 dan tetap di atas EMA 125
   bool touchedZone = IsTouchEMA21or8(l0, h0, ema8, ema21) || IsTouchEMA21or8(l1, h1, ema8, ema21);
   if(!touchedZone) return PATTERN_NONE;
   if(l0 <= ema125 || l1 <= ema125) return PATTERN_NONE; // Harga wajib di atas EMA 125

   // 1. HAMMER (Ekor bawah panjang >= 2x body, body kecil di atas, upper wick sangat kecil)
   if(lower_wick0 >= (2.0 * body0) && upper_wick0 <= (0.25 * range0) && (c0 - l0) >= (0.65 * range0))
     {
      return PATTERN_HAMMER;
     }

   // 2. BULLISH PIN BAR (Ekor bawah >= 60% total range, penolakan harga bawah jelas)
   if(lower_wick0 >= (0.60 * range0) && upper_wick0 <= (0.20 * range0) && body0 <= (0.35 * range0))
     {
      return PATTERN_BULLISH_PINBAR;
     }

   // 3. BULLISH ENGULFING (Candle hijau menelan candle merah s+1)
   if(isBullish0 && isBearish1 && body1 > 0.0)
     {
      if(c0 >= o1 && o0 <= c1 && body0 > body1)
        {
         return PATTERN_BULLISH_ENGULFING;
        }
     }

   // 4. MORNING STAR (3 candle: s+2 bearish, s+1 small body/indecision di EMA, s bullish kuat)
   if(c2 < o2 && range1 > 0.0)
     {
      bool isSmallBody1 = (body1 <= (h1 - l1) * 0.40);
      bool isStrongBullish0 = isBullish0 && (c0 >= (o2 + c2) / 2.0); // Close di atas 50% candle 2
      if(isSmallBody1 && isStrongBullish0 && l1 <= MathMax(ema8, ema21))
        {
         return PATTERN_MORNING_STAR;
        }
     }

   // 5. PIERCING LINE (Candle merah diikuti candle hijau yang open rendah tapi close > 50% body merah)
   if(isBearish1 && isBullish0 && body1 > 0.0)
     {
      double midPoint1 = (o1 + c1) / 2.0;
      if(o0 <= c1 + (range1 * 0.1) && c0 > midPoint1 && c0 < o1)
        {
         return PATTERN_PIERCING_LINE;
        }
     }

   // 6. THREE WHITE SOLDIERS (3 candle hijau berturut-turut, higher close, higher high)
   if(c0 > o0 && c1 > o1 && c2 > o2)
     {
      if(c0 > c1 && c1 > c2 && h0 > h1 && h1 > h2)
        {
         if(upper_wick0 <= 0.3 * range0 && (h1 - c1) <= 0.3 * range1)
           {
            return PATTERN_THREE_WHITE_SOLDIERS;
           }
        }
     }

   // 7. BULLISH DOJI REJECTION (Body sangat tipis <= 10% range, ekor bawah panjang menunjukkan buyer masuk)
   if(body0 <= (0.12 * range0) && lower_wick0 >= (0.50 * range0) && isBullish0)
     {
      return PATTERN_BULLISH_DOJI;
     }

   // 8. BULLISH INSIDE BAR BREAKOUT (Candle s+1 di dalam range s+2, lalu candle s breakout ke atas)
   if(h1 <= h2 && l1 >= l2) // s+1 adalah inside bar
     {
      if(isBullish0 && c0 > h1) // candle s breakout high inside bar
        {
         return PATTERN_BULLISH_INSIDE_BAR;
        }
     }

   // 9. TWO CANDLE REJECTION (Candle s+1 memiliki ekor bawah panjang di EMA, candle s bullish kuat)
   if(range1 > 0.0)
     {
      double lower_wick1 = (c1 >= o1) ? (o1 - l1) : (c1 - l1);
      if(lower_wick1 >= (0.45 * range1) && isBullish0 && c0 > h1)
        {
         return PATTERN_BULLISH_TWO_CANDLE_REJECTION;
        }
     }

   return PATTERN_NONE;
  }

//+------------------------------------------------------------------+
//| Deteksi 9 Pola Candlestick Bearish                               |
//+------------------------------------------------------------------+
ENUM_CANDLE_PATTERN CCandlePatternDetector::DetectBearishPattern(const MqlRates &rates[], int s, double ema8, double ema21, double ema125)
  {
   if(s < 1 || s + 3 >= ArraySize(rates)) return PATTERN_NONE;

   // Definisi candle s (candle konfirmasi)
   double o0 = rates[s].open;
   double h0 = rates[s].high;
   double l0 = rates[s].low;
   double c0 = rates[s].close;
   double range0 = h0 - l0;
   if(range0 <= 0.0) return PATTERN_NONE;

   double body0 = MathAbs(c0 - o0);
   double lower_wick0 = (c0 >= o0) ? (o0 - l0) : (c0 - l0);
   double upper_wick0 = (c0 >= o0) ? (h0 - c0) : (h0 - o0);
   bool isBearish0 = (c0 < o0);

   // Definisi candle s+1
   double o1 = rates[s+1].open;
   double h1 = rates[s+1].high;
   double l1 = rates[s+1].low;
   double c1 = rates[s+1].close;
   double range1 = h1 - l1;
   double body1 = MathAbs(c1 - o1);
   bool isBullish1 = (c1 > o1);

   // Definisi candle s+2
   double o2 = rates[s+2].open;
   double h2 = rates[s+2].high;
   double l2 = rates[s+2].low;
   double c2 = rates[s+2].close;

   // Validasi dasar: High candle harus menyentuh zona pullback EMA 8/21 dan tetap di bawah EMA 125
   bool touchedZone = IsTouchEMA21or8(l0, h0, ema8, ema21) || IsTouchEMA21or8(l1, h1, ema8, ema21);
   if(!touchedZone) return PATTERN_NONE;
   if(h0 >= ema125 || h1 >= ema125) return PATTERN_NONE; // Harga wajib di bawah EMA 125

   // 1. SHOOTING STAR (Ekor atas panjang >= 2x body, body kecil di bawah, lower wick sangat kecil)
   if(upper_wick0 >= (2.0 * body0) && lower_wick0 <= (0.25 * range0) && (h0 - c0) >= (0.65 * range0))
     {
      return PATTERN_SHOOTING_STAR;
     }

   // 2. BEARISH PIN BAR (Ekor atas >= 60% total range, penolakan harga atas jelas di EMA)
   if(upper_wick0 >= (0.60 * range0) && lower_wick0 <= (0.20 * range0) && body0 <= (0.35 * range0))
     {
      return PATTERN_BEARISH_PINBAR;
     }

   // 3. BEARISH ENGULFING (Candle merah menelan candle hijau s+1)
   if(isBearish0 && isBullish1 && body1 > 0.0)
     {
      if(c0 <= o1 && o0 >= c1 && body0 > body1)
        {
         return PATTERN_BEARISH_ENGULFING;
        }
     }

   // 4. DARK CLOUD COVER (Candle hijau diikuti candle merah yang open di atas tapi close < 50% body hijau)
   if(isBullish1 && isBearish0 && body1 > 0.0)
     {
      double midPoint1 = (o1 + c1) / 2.0;
      if(o0 >= c1 - (range1 * 0.1) && c0 < midPoint1 && c0 > o1)
        {
         return PATTERN_DARK_CLOUD_COVER;
        }
     }

   // 5. EVENING STAR (3 candle: s+2 bullish, s+1 small body di EMA resistance, s bearish kuat)
   if(c2 > o2 && range1 > 0.0)
     {
      bool isSmallBody1 = (body1 <= (h1 - l1) * 0.40);
      bool isStrongBearish0 = isBearish0 && (c0 <= (o2 + c2) / 2.0); // Close di bawah 50% candle 2
      if(isSmallBody1 && isStrongBearish0 && h1 >= MathMin(ema8, ema21))
        {
         return PATTERN_EVENING_STAR;
        }
     }

   // 6. THREE BLACK CROWS (3 candle merah berturut-turut, lower close, lower low)
   if(c0 < o0 && c1 < o1 && c2 < o2)
     {
      if(c0 < c1 && c1 < c2 && l0 < l1 && l1 < l2)
        {
         if(lower_wick0 <= 0.3 * range0 && (c1 - l1) <= 0.3 * range1)
           {
            return PATTERN_THREE_BLACK_CROWS;
           }
        }
     }

   // 7. BEARISH DOJI REJECTION (Body sangat tipis <= 10% range, ekor atas panjang penolakan resistance)
   if(body0 <= (0.12 * range0) && upper_wick0 >= (0.50 * range0) && isBearish0)
     {
      return PATTERN_BEARISH_DOJI;
     }

   // 8. BEARISH INSIDE BAR BREAKDOWN (Candle s+1 di dalam range s+2, lalu candle s breakdown ke bawah)
   if(h1 <= h2 && l1 >= l2)
     {
      if(isBearish0 && c0 < l1)
        {
         return PATTERN_BEARISH_INSIDE_BAR;
        }
     }

   // 9. TWO CANDLE REJECTION (Candle s+1 ekor atas panjang di EMA, candle s bearish kuat)
   if(range1 > 0.0)
     {
      double upper_wick1 = (c1 >= o1) ? (h1 - c1) : (h1 - o1);
      if(upper_wick1 >= (0.45 * range1) && isBearish0 && c0 < l1)
        {
         return PATTERN_BEARISH_TWO_CANDLE_REJECTION;
        }
     }

   return PATTERN_NONE;
  }
//+------------------------------------------------------------------+
