//+------------------------------------------------------------------+
//|                                             MarketStructure.mqh  |
//|                        Triple EMA Pullback Strategy Library      |
//|                                  Copyright 2026, XAUUSD Trader   |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, XAUUSD Senior Trader"
#property link      ""
#property strict

//+------------------------------------------------------------------+
//| Enum Status Struktur Market                                      |
//+------------------------------------------------------------------+
enum ENUM_MARKET_STRUCTURE
  {
   STRUCTURE_UNKNOWN = 0,
   STRUCTURE_BULLISH_HH_HL, // Higher Highs & Higher Lows (Trend Naik Valid)
   STRUCTURE_BEARISH_LH_LL, // Lower Highs & Lower Lows (Trend Turun Valid)
   STRUCTURE_SIDEWAYS       // Sideways / Rentang Range Tidak Jelas
  };

//+------------------------------------------------------------------+
//| Enum Status Filter False Signal                                  |
//+------------------------------------------------------------------+
enum ENUM_FILTER_RESULT
  {
   FILTER_PASS = 0,         // Lolos semua filter
   FILTER_FAIL_CHOP_EMA8_21,// Gagal: EMA 8 & 21 sering bolak-balik
   FILTER_FAIL_WHIPSAW_125, // Gagal: Harga bolak-balik menembus EMA 125
   FILTER_FAIL_OVEREXTENDED,// Gagal: Candle terlalu jauh dari EMA (Overextended)
   FILTER_FAIL_STRUCTURE    // Gagal: Struktur market bukan HH-HL / LH-LL
  };

//+------------------------------------------------------------------+
//| Fungsi Konversi Struktur ke Teks                                 |
//+------------------------------------------------------------------+
string GetMarketStructureName(ENUM_MARKET_STRUCTURE structure)
  {
   switch(structure)
     {
      case STRUCTURE_BULLISH_HH_HL: return "Bullish (Higher High & Higher Low)";
      case STRUCTURE_BEARISH_LH_LL: return "Bearish (Lower High & Lower Low)";
      case STRUCTURE_SIDEWAYS:      return "Sideways / Range Bound (Waspada)";
      default:                      return "Unclear / In Transition";
     }
  }

//+------------------------------------------------------------------+
//| Fungsi Konversi Hasil Filter ke Teks Deskriptif                  |
//+------------------------------------------------------------------+
string FilterResultToString(ENUM_FILTER_RESULT res)
  {
   switch(res)
     {
      case FILTER_FAIL_CHOP_EMA8_21: return "Chop Sideways (EMA 8-21 Cross)";
      case FILTER_FAIL_WHIPSAW_125:  return "Whipsaw EMA 125";
      case FILTER_FAIL_OVEREXTENDED: return "Overextended Candle (> 2.0x ATR)";
      case FILTER_FAIL_STRUCTURE:    return "Structure Not HH/HL or LH/LL";
      default:                       return "Valid";
     }
  }

//+------------------------------------------------------------------+
//| Kelas Analisis Struktur Pasar & Filter False Signal              |
//+------------------------------------------------------------------+
class CMarketStructure
  {
private:
   int               m_fractal_lookback;
   int               m_chop_bars;
   int               m_max_ema_crosses;
   int               m_whipsaw_bars;
   int               m_max_ema125_crosses;
   double            m_max_atr_multiplier;

public:
                     CMarketStructure();
                    ~CMarketStructure() {}

   // Set Parameter Filter
   void              Configure(int fractalLookback = 30,
                               int chopBars = 15,
                               int maxEmaCrosses = 2,
                               int whipsawBars = 20,
                               int maxEma125Crosses = 2,
                               double maxAtrMultiplier = 2.0);

   // Analisis Struktur Market (HH-HL vs LH-LL)
   ENUM_MARKET_STRUCTURE AnalyzeStructure(const MqlRates &rates[], int totalRates, int shift = 1);

   // Filter 1: Deteksi Sideways EMA 8 & EMA 21 Sering Bolak-balik
   bool              IsEma8_21Choppy(const double &ema8[], const double &ema21[], int shift = 1);

   // Filter 2: Deteksi Whipsaw EMA 125 (Harga sering menembus bolak-balik)
   bool              IsEma125Whipsawing(const MqlRates &rates[], const double &ema125[], int shift = 1);

   // Filter 3: Deteksi Candle Terlalu Jauh dari EMA (Overextended Risk)
   bool              IsCandleOverextended(double closePrice, double ema8Value, double atrValue);

   // Validasi Filter Lengkap untuk BUY
   ENUM_FILTER_RESULT ValidateBuyFilters(const MqlRates &rates[],
                                         int totalRates,
                                         const double &ema8[],
                                         const double &ema21[],
                                         const double &ema125[],
                                         double currentAtr,
                                         bool requireHHHL = true,
                                         int shift = 1);

   // Validasi Filter Lengkap untuk SELL
   ENUM_FILTER_RESULT ValidateSellFilters(const MqlRates &rates[],
                                          int totalRates,
                                          const double &ema8[],
                                          const double &ema21[],
                                          const double &ema125[],
                                          double currentAtr,
                                          bool requireLHLL = true,
                                          int shift = 1);
  };

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CMarketStructure::CMarketStructure()
  {
   m_fractal_lookback    = 50;
   m_chop_bars           = 15;
   m_max_ema_crosses     = 2;
   m_whipsaw_bars        = 20;
   m_max_ema125_crosses  = 2;
   m_max_atr_multiplier  = 2.0;
  }

//+------------------------------------------------------------------+
//| Konfigurasi Parameter                                            |
//+------------------------------------------------------------------+
void CMarketStructure::Configure(int fractalLookback,
                                 int chopBars,
                                 int maxEmaCrosses,
                                 int whipsawBars,
                                 int maxEma125Crosses,
                                 double maxAtrMultiplier)
  {
   m_fractal_lookback    = MathMax(20, fractalLookback);
   m_chop_bars           = MathMax(5, chopBars);
   m_max_ema_crosses     = MathMax(1, maxEmaCrosses);
   m_whipsaw_bars        = MathMax(10, whipsawBars);
   m_max_ema125_crosses  = MathMax(1, maxEma125Crosses);
   m_max_atr_multiplier  = (maxAtrMultiplier > 0.5) ? maxAtrMultiplier : 2.0;
  }

//+------------------------------------------------------------------+
//| Analisis Pola Swing HH/HL atau LH/LL Menggunakan Fractal Swing    |
//+------------------------------------------------------------------+
ENUM_MARKET_STRUCTURE CMarketStructure::AnalyzeStructure(const MqlRates &rates[], int totalRates, int shift)
  {
   if(totalRates < shift + 15) return STRUCTURE_UNKNOWN;

   double swingHighs[];
   double swingLows[];
   ArrayResize(swingHighs, 0);
   ArrayResize(swingLows, 0);

   int maxSearch = MathMin(shift + m_fractal_lookback, totalRates - 3);

   // 1. Scan Primer: 5-bar Fractal (2 bar kiri, 2 bar kanan)
   for(int i = shift + 2; i < maxSearch; i++)
     {
      // Swing High: High[i] lebih tinggi dari 2 bar sebelum dan 2 bar sesudah
      if(rates[i].high > rates[i-1].high && rates[i].high > rates[i-2].high &&
         rates[i].high > rates[i+1].high && rates[i].high > rates[i+2].high)
        {
         int sz = ArraySize(swingHighs);
         ArrayResize(swingHighs, sz + 1);
         swingHighs[sz] = rates[i].high;
         if(sz + 1 >= 2 && ArraySize(swingLows) >= 2) break;
        }

      // Swing Low: Low[i] lebih rendah dari 2 bar sebelum dan 2 bar sesudah
      if(rates[i].low < rates[i-1].low && rates[i].low < rates[i-2].low &&
         rates[i].low < rates[i+1].low && rates[i].low < rates[i+2].low)
        {
         int sz = ArraySize(swingLows);
         ArrayResize(swingLows, sz + 1);
         swingLows[sz] = rates[i].low;
         if(sz + 1 >= 2 && ArraySize(swingHighs) >= 2) break;
        }
     }

   // 2. Scan Sekunder (Fallback): 3-bar Fractal jika tren cepat/rapat
   if(ArraySize(swingHighs) < 2 || ArraySize(swingLows) < 2)
     {
      ArrayResize(swingHighs, 0);
      ArrayResize(swingLows, 0);
      int maxSearch3 = MathMin(shift + m_fractal_lookback, totalRates - 2);

      for(int i = shift + 1; i < maxSearch3; i++)
        {
         if(rates[i].high > rates[i-1].high && rates[i].high > rates[i+1].high)
           {
            int sz = ArraySize(swingHighs);
            ArrayResize(swingHighs, sz + 1);
            swingHighs[sz] = rates[i].high;
            if(sz + 1 >= 2 && ArraySize(swingLows) >= 2) break;
           }

         if(rates[i].low < rates[i-1].low && rates[i].low < rates[i+1].low)
           {
            int sz = ArraySize(swingLows);
            ArrayResize(swingLows, sz + 1);
            swingLows[sz] = rates[i].low;
            if(sz + 1 >= 2 && ArraySize(swingHighs) >= 2) break;
           }
        }
     }

   // Butuh minimal 2 swing high dan 2 swing low untuk konfirmasi struktur
   if(ArraySize(swingHighs) < 2 || ArraySize(swingLows) < 2)
     {
      return STRUCTURE_UNKNOWN;
     }

   double shRecent = swingHighs[0]; // Swing High terbaru sebelum bar shift
   double shPrev   = swingHighs[1]; // Swing High sebelumnya
   double slRecent = swingLows[0];  // Swing Low terbaru sebelum bar shift
   double slPrev   = swingLows[1];  // Swing Low sebelumnya

   // Kondisi Bullish: Higher High (shRecent > shPrev) dan Higher Low (slRecent > slPrev)
   if(shRecent > shPrev && slRecent > slPrev)
     {
      return STRUCTURE_BULLISH_HH_HL;
     }

   // Kondisi Bearish: Lower High (shRecent < shPrev) dan Lower Low (slRecent < slPrev)
   if(shRecent < shPrev && slRecent < slPrev)
     {
      return STRUCTURE_BEARISH_LH_LL;
     }

   return STRUCTURE_SIDEWAYS;
  }

//+------------------------------------------------------------------+
//| Cek apakah EMA 8 & EMA 21 sering bolak-balik (Chop / Sideways)   |
//+------------------------------------------------------------------+
bool CMarketStructure::IsEma8_21Choppy(const double &ema8[], const double &ema21[], int shift)
  {
   int sz8  = ArraySize(ema8);
   int sz21 = ArraySize(ema21);
   int maxLimit = MathMin(sz8, sz21) - 1;
   if(shift >= maxLimit) return false;

   int endBar = MathMin(shift + m_chop_bars - 1, maxLimit - 1);
   int crosses = 0;

   // Hitung berapa kali EMA 8 dan 21 berganti tanda (cross) dalam lookback
   for(int i = shift; i <= endBar; i++)
     {
      double diff1 = ema8[i] - ema21[i];
      double diff2 = ema8[i+1] - ema21[i+1];
      if((diff1 > 0 && diff2 < 0) || (diff1 < 0 && diff2 > 0))
        {
         crosses++;
        }
     }

   return (crosses >= m_max_ema_crosses);
  }

//+------------------------------------------------------------------+
//| Cek apakah harga bolak-balik menembus EMA 125 (Whipsaw)          |
//+------------------------------------------------------------------+
bool CMarketStructure::IsEma125Whipsawing(const MqlRates &rates[], const double &ema125[], int shift)
  {
   int szRates = ArraySize(rates);
   int sz125   = ArraySize(ema125);
   int maxLimit = MathMin(szRates, sz125) - 1;
   if(shift >= maxLimit) return false;

   int endBar = MathMin(shift + m_whipsaw_bars - 1, maxLimit - 1);
   int crosses = 0;

   // Hitung berapa kali harga Close menyeberangi EMA 125
   for(int i = shift; i <= endBar; i++)
     {
      double diff1 = rates[i].close - ema125[i];
      double diff2 = rates[i+1].close - ema125[i+1];
      if((diff1 > 0 && diff2 < 0) || (diff1 < 0 && diff2 > 0))
        {
         crosses++;
        }
     }

   return (crosses >= m_max_ema125_crosses);
  }

//+------------------------------------------------------------------+
//| Cek apakah candle sudah overextended (terlalu jauh dari EMA 8)   |
//+------------------------------------------------------------------+
bool CMarketStructure::IsCandleOverextended(double closePrice, double ema8Value, double atrValue)
  {
   if(atrValue <= 0.0) return false;
   double distance = MathAbs(closePrice - ema8Value);
   return (distance > (m_max_atr_multiplier * atrValue));
  }

//+------------------------------------------------------------------+
//| Validasi Seluruh Filter untuk Sinyal BUY                         |
//+------------------------------------------------------------------+
ENUM_FILTER_RESULT CMarketStructure::ValidateBuyFilters(const MqlRates &rates[],
                                                        int totalRates,
                                                        const double &ema8[],
                                                        const double &ema21[],
                                                        const double &ema125[],
                                                        double currentAtr,
                                                        bool requireHHHL,
                                                        int shift)
  {
   // 1. Cek Chop EMA 8 dan 21
   if(IsEma8_21Choppy(ema8, ema21, shift))
     {
      return FILTER_FAIL_CHOP_EMA8_21;
     }

   // 2. Cek Whipsaw EMA 125
   if(IsEma125Whipsawing(rates, ema125, shift))
     {
      return FILTER_FAIL_WHIPSAW_125;
     }

   // 3. Cek Overextended dari EMA 8
   if(IsCandleOverextended(rates[shift].close, ema8[shift], currentAtr))
     {
      return FILTER_FAIL_OVEREXTENDED;
     }

   // 4. Cek Struktur Pasar (Wajib HH-HL untuk Bullish) jika diaktifkan
   if(requireHHHL)
     {
      ENUM_MARKET_STRUCTURE st = AnalyzeStructure(rates, totalRates, shift);
      if(st != STRUCTURE_BULLISH_HH_HL)
        {
         return FILTER_FAIL_STRUCTURE;
        }
     }

   return FILTER_PASS;
  }

//+------------------------------------------------------------------+
//| Validasi Seluruh Filter untuk Sinyal SELL                        |
//+------------------------------------------------------------------+
ENUM_FILTER_RESULT CMarketStructure::ValidateSellFilters(const MqlRates &rates[],
                                                         int totalRates,
                                                         const double &ema8[],
                                                         const double &ema21[],
                                                         const double &ema125[],
                                                         double currentAtr,
                                                         bool requireLHLL,
                                                         int shift)
  {
   // 1. Cek Chop EMA 8 dan 21
   if(IsEma8_21Choppy(ema8, ema21, shift))
     {
      return FILTER_FAIL_CHOP_EMA8_21;
     }

   // 2. Cek Whipsaw EMA 125
   if(IsEma125Whipsawing(rates, ema125, shift))
     {
      return FILTER_FAIL_WHIPSAW_125;
     }

   // 3. Cek Overextended dari EMA 8
   if(IsCandleOverextended(rates[shift].close, ema8[shift], currentAtr))
     {
      return FILTER_FAIL_OVEREXTENDED;
     }

   // 4. Cek Struktur Pasar (Wajib LH-LL untuk Bearish) jika diaktifkan
   if(requireLHLL)
     {
      ENUM_MARKET_STRUCTURE st = AnalyzeStructure(rates, totalRates, shift);
      if(st != STRUCTURE_BEARISH_LH_LL)
        {
         return FILTER_FAIL_STRUCTURE;
        }
     }

   return FILTER_PASS;
  }
//+------------------------------------------------------------------+
