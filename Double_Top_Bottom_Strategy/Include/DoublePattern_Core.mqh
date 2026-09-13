//+------------------------------------------------------------------+
//|                                        DoublePattern_Core.mqh    |
//|                 Double Top & Double Bottom Core Engine           |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, XAUUSD Senior Trader"
#property link      ""
#property version   "1.00"

//+------------------------------------------------------------------+
//| Enum Tipe Pola Reversal                                          |
//+------------------------------------------------------------------+
enum ENUM_DOUBLE_PATTERN_TYPE
  {
   PATTERN_NONE,
   PATTERN_DOUBLE_BOTTOM, // Pola "W" - Bullish Reversal
   PATTERN_DOUBLE_TOP     // Pola "M" - Bearish Reversal
  };

//+------------------------------------------------------------------+
//| Enum Status Pola                                                 |
//+------------------------------------------------------------------+
enum ENUM_PATTERN_STATUS
  {
   STATUS_NONE,
   STATUS_FORMING,        // Puncak/Lembah 2 terbentuk, sedang menunggu breakout neckline
   STATUS_CONFIRMED,      // Breakout Neckline terkonfirmasi dengan volume tinggi
   STATUS_COMPLETED,      // Pola telah selesai atau dieksekusi trade
   STATUS_INVALIDATED     // Pola batal / ditembus di luar batas
  };

//+------------------------------------------------------------------+
//| Struct Titik Swing Fractal                                       |
//+------------------------------------------------------------------+
struct SwingPoint
  {
   datetime time;
   double   price;
   bool     isHigh;       // true = High, false = Low
   int      barIndex;
  };

//+------------------------------------------------------------------+
//| Struct Data Pola Double Top / Double Bottom                      |
//+------------------------------------------------------------------+
struct DoublePatternInfo
  {
   ENUM_DOUBLE_PATTERN_TYPE type;
   ENUM_PATTERN_STATUS      status;
   datetime                 t1;            // Waktu Puncak 1 / Lembah 1
   double                   p1;            // Harga Puncak 1 / Lembah 1
   int                      barIndex1;
   datetime                 tNeck;         // Waktu Neckline perantara
   double                   pNeck;         // Level Harga Neckline
   int                      barIndexNeck;
   datetime                 t2;            // Waktu Puncak 2 / Lembah 2
   double                   p2;            // Harga Puncak 2 / Lembah 2
   int                      barIndex2;
   datetime                 tBreak;        // Waktu candle breakout
   double                   pBreak;        // Harga penutupan candle breakout
   double                   volumeRatio;   // Rasio volume lilin breakout terhadap SMA Volume
   double                   patternHeight; // Tinggi pola (Points/Price)
   bool                     hasTriggered;  // Sudah dieksekusi trade
  };

//+------------------------------------------------------------------+
//| Class Mesin Inti Pola Double Top & Double Bottom                 |
//+------------------------------------------------------------------+
class CDoublePatternCore
  {
private:
   int                m_swingLookback;        // Lookback fractal (default 3 atau 4)
   int                m_minBarsBetween;       // Minimal jarak lilin antara Puncak 1 dan 2 (default 5)
   int                m_maxBarsBetween;       // Maksimal jarak lilin antara Puncak 1 dan 2 (default 60)
   double             m_tolerancePct;         // Toleransi keselarasan horizontal (%) (default 15.0%)
   double             m_minHeightPoints;      // Minimal tinggi pola dalam points (default 50.0)
   double             m_minVolumeMultiplier;  // Pengali volume minimal konfirmasi breakout (default 1.15x)
   int                m_volumeSmaPeriod;      // Periode SMA Volume (default 20)

   SwingPoint         m_swings[];             // Daftar titik swing
   DoublePatternInfo  m_activeBottom;         // Pola Double Bottom ("W") aktif independen
   DoublePatternInfo  m_activeTop;            // Pola Double Top ("M") aktif independen
   DoublePatternInfo  m_lastConfirmedBottom;  // Pola Bottom terakhir yang terkonfirmasi
   DoublePatternInfo  m_lastConfirmedTop;     // Pola Top terakhir yang terkonfirmasi

public:
                      CDoublePatternCore();
                     ~CDoublePatternCore();

   void               Configure(int swingLookback = 3, int minBars = 5, int maxBars = 60,
                                double tolerancePct = 15.0, double minHeightPoints = 50.0,
                                double minVolMult = 1.15, int volPeriod = 20);

   void               Update(const MqlRates &rates[], int totalBars);

   // Akses Data
   bool               HasActivePattern() const { return (m_activeBottom.type != PATTERN_NONE || m_activeTop.type != PATTERN_NONE); }
   DoublePatternInfo  GetActiveBottom() const { return m_activeBottom; }
   DoublePatternInfo  GetActiveTop() const { return m_activeTop; }
   DoublePatternInfo  GetActivePattern() const;
   DoublePatternInfo  GetLastConfirmedPattern() const;

   // Cek Sinyal Breakout pada Bar 1 (Closed Bar Non-Repainting)
   bool               IsDoubleBottomBreakout(const MqlRates &rates[], DoublePatternInfo &outPattern);
   bool               IsDoubleTopBreakout(const MqlRates &rates[], DoublePatternInfo &outPattern);

   // Tandai pola sudah dieksekusi agar tidak entri ganda
   void               MarkBottomTriggered();
   void               MarkTopTriggered();
   void               MarkPatternTriggered();

private:
   void               ScanSwingPoints(const MqlRates &rates[], int totalBars);
   void               DetectDoubleBottom(const MqlRates &rates[], int totalBars, double avgVolume);
   void               DetectDoubleTop(const MqlRates &rates[], int totalBars, double avgVolume);
   double             CalculateAverageVolume(const MqlRates &rates[], int totalBars, int period);
  };

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CDoublePatternCore::CDoublePatternCore()
  {
   m_swingLookback       = 3;
   m_minBarsBetween      = 5;
   m_maxBarsBetween      = 60;
   m_tolerancePct        = 15.0;
   m_minHeightPoints     = 50.0;
   m_minVolumeMultiplier = 1.15;
   m_volumeSmaPeriod     = 20;

   ArrayResize(m_swings, 0);
   ZeroMemory(m_activeBottom);
   ZeroMemory(m_activeTop);
   ZeroMemory(m_lastConfirmedBottom);
   ZeroMemory(m_lastConfirmedTop);
  }

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CDoublePatternCore::~CDoublePatternCore()
  {
   ArrayFree(m_swings);
  }

//+------------------------------------------------------------------+
//| Konfigurasi Parameter                                            |
//+------------------------------------------------------------------+
void CDoublePatternCore::Configure(int swingLookback = 3, int minBars = 5, int maxBars = 60,
                                   double tolerancePct = 15.0, double minHeightPoints = 50.0,
                                   double minVolMult = 1.15, int volPeriod = 20)
  {
   m_swingLookback       = MathMax(2, swingLookback);
   m_minBarsBetween      = MathMax(3, minBars);
   m_maxBarsBetween      = MathMax(m_minBarsBetween + 5, maxBars);
   m_tolerancePct        = MathMax(5.0, tolerancePct);
   m_minHeightPoints     = MathMax(20.0, minHeightPoints);
   m_minVolumeMultiplier = MathMax(1.0, minVolMult);
   m_volumeSmaPeriod     = MathMax(10, volPeriod);
  }

//+------------------------------------------------------------------+
//| Hitung Rata-Rata Volume SMA                                      |
//+------------------------------------------------------------------+
double CDoublePatternCore::CalculateAverageVolume(const MqlRates &rates[], int totalBars, int period)
  {
   int count = MathMin(totalBars - 2, period);
   if(count <= 0) return 1.0;

   double sum = 0.0;
   for(int i = 2; i <= count + 1; i++)
     {
      sum += (double)rates[i].tick_volume;
     }
   return (sum / (double)count);
  }

//+------------------------------------------------------------------+
//| Ambil Pola Aktif Paling Relevan untuk Visual HUD                 |
//+------------------------------------------------------------------+
DoublePatternInfo CDoublePatternCore::GetActivePattern() const
  {
   if(m_activeBottom.status == STATUS_CONFIRMED) return m_activeBottom;
   if(m_activeTop.status == STATUS_CONFIRMED)    return m_activeTop;

   if(m_activeBottom.type != PATTERN_NONE && m_activeTop.type != PATTERN_NONE)
     {
      // Ambil yang paling baru lembah/puncak ke-2 nya
      return (m_activeBottom.t2 > m_activeTop.t2) ? m_activeBottom : m_activeTop;
     }

   if(m_activeBottom.type != PATTERN_NONE) return m_activeBottom;
   return m_activeTop;
  }

//+------------------------------------------------------------------+
//| Ambil Pola Terakhir yang Berhasil Breakout                       |
//+------------------------------------------------------------------+
DoublePatternInfo CDoublePatternCore::GetLastConfirmedPattern() const
  {
   if(m_lastConfirmedBottom.tBreak > m_lastConfirmedTop.tBreak)
      return m_lastConfirmedBottom;
   return m_lastConfirmedTop;
  }

//+------------------------------------------------------------------+
//| Update Analisis Lengkap Setiap Bar                               |
//+------------------------------------------------------------------+
void CDoublePatternCore::Update(const MqlRates &rates[], int totalBars)
  {
   if(totalBars < (m_maxBarsBetween + 20)) return;

   ScanSwingPoints(rates, totalBars);

   double avgVolume = CalculateAverageVolume(rates, totalBars, m_volumeSmaPeriod);

   // Pindai pembentukan kedua pola secara mandiri (tidak saling menimpa)
   DetectDoubleBottom(rates, totalBars, avgVolume);
   DetectDoubleTop(rates, totalBars, avgVolume);
  }

//+------------------------------------------------------------------+
//| Pindai Titik Swing Fractal                                       |
//+------------------------------------------------------------------+
void CDoublePatternCore::ScanSwingPoints(const MqlRates &rates[], int totalBars)
  {
   ArrayResize(m_swings, 0);
   int lookbackLimit = MathMin(totalBars - m_swingLookback - 1, 160);

   for(int i = m_swingLookback + 1; i <= lookbackLimit; i++)
     {
      bool isHigh = true;
      bool isLow  = true;

      for(int k = 1; k <= m_swingLookback; k++)
        {
         if(rates[i].high <= rates[i - k].high || rates[i].high <= rates[i + k].high)
            isHigh = false;

         if(rates[i].low >= rates[i - k].low || rates[i].low >= rates[i + k].low)
            isLow = false;
        }

      if(isHigh)
        {
         int sz = ArraySize(m_swings);
         ArrayResize(m_swings, sz + 1);
         m_swings[sz].time     = rates[i].time;
         m_swings[sz].price    = rates[i].high;
         m_swings[sz].isHigh   = true;
         m_swings[sz].barIndex = i;
        }
      else if(isLow)
        {
         int sz = ArraySize(m_swings);
         ArrayResize(m_swings, sz + 1);
         m_swings[sz].time     = rates[i].time;
         m_swings[sz].price    = rates[i].low;
         m_swings[sz].isHigh   = false;
         m_swings[sz].barIndex = i;
        }
     }
  }

//+------------------------------------------------------------------+
//| Deteksi Pola Double Bottom ("W")                                 |
//+------------------------------------------------------------------+
void CDoublePatternCore::DetectDoubleBottom(const MqlRates &rates[], int totalBars, double avgVolume)
  {
   int swingCount = ArraySize(m_swings);
   if(swingCount < 3) return;

   // Cari dua lembah swing low berturut-turut terdekat
   for(int i = 0; i < swingCount - 2; i++)
     {
      if(!m_swings[i].isHigh) // Lembah 2 (lebih baru)
        {
         for(int j = i + 1; j < swingCount; j++)
           {
            if(!m_swings[j].isHigh) // Lembah 1 (lebih lama)
              {
               int barDist = m_swings[j].barIndex - m_swings[i].barIndex;
               if(barDist < m_minBarsBetween || barDist > m_maxBarsBetween) continue;

               // Cari titik tertinggi di antara dua lembah sebagai Neckline
               double neckPrice = 0.0;
               datetime neckTime = 0;
               int neckIndex = -1;

               for(int k = m_swings[i].barIndex + 1; k < m_swings[j].barIndex; k++)
                 {
                  if(rates[k].high > neckPrice)
                    {
                     neckPrice = rates[k].high;
                     neckTime  = rates[k].time;
                     neckIndex = k;
                    }
                 }

               if(neckIndex < 0 || neckPrice <= 0.0) continue;

               double low1 = m_swings[j].price;
               double low2 = m_swings[i].price;
               double height = neckPrice - MathMin(low1, low2);

               if(height < (m_minHeightPoints * _Point)) continue;

               // Cek keselarasan horizontal kedua lembah (tolerance)
               double priceDiff = MathAbs(low1 - low2);
               if(priceDiff > (height * (m_tolerancePct / 100.0))) continue;

               // Pola valid ditemukan!
               bool previouslyTriggered = (m_activeBottom.type == PATTERN_DOUBLE_BOTTOM && 
                                           m_activeBottom.t1 == m_swings[j].time && 
                                           m_activeBottom.hasTriggered);

               m_activeBottom.type          = PATTERN_DOUBLE_BOTTOM;
               m_activeBottom.t1            = m_swings[j].time;
               m_activeBottom.p1            = low1;
               m_activeBottom.barIndex1     = m_swings[j].barIndex;
               m_activeBottom.tNeck         = neckTime;
               m_activeBottom.pNeck         = neckPrice;
               m_activeBottom.barIndexNeck  = neckIndex;
               m_activeBottom.t2            = m_swings[i].time;
               m_activeBottom.p2            = low2;
               m_activeBottom.barIndex2     = m_swings[i].barIndex;
               m_activeBottom.patternHeight = height;
               m_activeBottom.hasTriggered  = previouslyTriggered;
               m_activeBottom.status        = STATUS_FORMING;

               // Cek apakah terjadi Breakout Neckline pada Bar 1
               if(rates[1].close > neckPrice && rates[2].close <= neckPrice)
                 {
                  double volRatio = (avgVolume > 0.0) ? ((double)rates[1].tick_volume / avgVolume) : 1.0;
                  m_activeBottom.volumeRatio = volRatio;

                  if(volRatio >= m_minVolumeMultiplier)
                    {
                     m_activeBottom.status = STATUS_CONFIRMED;
                     m_activeBottom.tBreak = rates[1].time;
                     m_activeBottom.pBreak = rates[1].close;
                     m_lastConfirmedBottom = m_activeBottom;
                    }
                 }
               return; // Ditemukan pola terdekat
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Deteksi Pola Double Top ("M")                                    |
//+------------------------------------------------------------------+
void CDoublePatternCore::DetectDoubleTop(const MqlRates &rates[], int totalBars, double avgVolume)
  {
   int swingCount = ArraySize(m_swings);
   if(swingCount < 3) return;

   for(int i = 0; i < swingCount - 2; i++)
     {
      if(m_swings[i].isHigh) // Puncak 2 (lebih baru)
        {
         for(int j = i + 1; j < swingCount; j++)
           {
            if(m_swings[j].isHigh) // Puncak 1 (lebih lama)
              {
               int barDist = m_swings[j].barIndex - m_swings[i].barIndex;
               if(barDist < m_minBarsBetween || barDist > m_maxBarsBetween) continue;

               // Cari titik terendah di antara dua puncak sebagai Neckline
               double neckPrice = 999999.0;
               datetime neckTime = 0;
               int neckIndex = -1;

               for(int k = m_swings[i].barIndex + 1; k < m_swings[j].barIndex; k++)
                 {
                  if(rates[k].low < neckPrice)
                    {
                     neckPrice = rates[k].low;
                     neckTime  = rates[k].time;
                     neckIndex = k;
                    }
                 }

               if(neckIndex < 0 || neckPrice >= 999999.0) continue;

               double high1 = m_swings[j].price;
               double high2 = m_swings[i].price;
               double height = MathMax(high1, high2) - neckPrice;

               if(height < (m_minHeightPoints * _Point)) continue;

               double priceDiff = MathAbs(high1 - high2);
               if(priceDiff > (height * (m_tolerancePct / 100.0))) continue;

               bool previouslyTriggered = (m_activeTop.type == PATTERN_DOUBLE_TOP && 
                                           m_activeTop.t1 == m_swings[j].time && 
                                           m_activeTop.hasTriggered);

               m_activeTop.type          = PATTERN_DOUBLE_TOP;
               m_activeTop.t1            = m_swings[j].time;
               m_activeTop.p1            = high1;
               m_activeTop.barIndex1     = m_swings[j].barIndex;
               m_activeTop.tNeck         = neckTime;
               m_activeTop.pNeck         = neckPrice;
               m_activeTop.barIndexNeck  = neckIndex;
               m_activeTop.t2            = m_swings[i].time;
               m_activeTop.p2            = high2;
               m_activeTop.barIndex2     = m_swings[i].barIndex;
               m_activeTop.patternHeight = height;
               m_activeTop.hasTriggered  = previouslyTriggered;
               m_activeTop.status        = STATUS_FORMING;

               // Cek apakah terjadi Breakdown Neckline pada Bar 1
               if(rates[1].close < neckPrice && rates[2].close >= neckPrice)
                 {
                  double volRatio = (avgVolume > 0.0) ? ((double)rates[1].tick_volume / avgVolume) : 1.0;
                  m_activeTop.volumeRatio = volRatio;

                  if(volRatio >= m_minVolumeMultiplier)
                    {
                     m_activeTop.status = STATUS_CONFIRMED;
                     m_activeTop.tBreak = rates[1].time;
                     m_activeTop.pBreak = rates[1].close;
                     m_lastConfirmedTop = m_activeTop;
                    }
                 }
               return; // Ditemukan pola terdekat
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Cek Apakah Terjadi Breakout Double Bottom pada Bar 1             |
//+------------------------------------------------------------------+
bool CDoublePatternCore::IsDoubleBottomBreakout(const MqlRates &rates[], DoublePatternInfo &outPattern)
  {
   if(m_activeBottom.type == PATTERN_DOUBLE_BOTTOM && 
      !m_activeBottom.hasTriggered && 
      m_activeBottom.status == STATUS_CONFIRMED)
     {
      outPattern = m_activeBottom;
      return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Terjadi Breakdown Double Top pada Bar 1               |
//+------------------------------------------------------------------+
bool CDoublePatternCore::IsDoubleTopBreakout(const MqlRates &rates[], DoublePatternInfo &outPattern)
  {
   if(m_activeTop.type == PATTERN_DOUBLE_TOP && 
      !m_activeTop.hasTriggered && 
      m_activeTop.status == STATUS_CONFIRMED)
     {
      outPattern = m_activeTop;
      return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Tandai Pola Double Bottom Sudah Dieksekusi                       |
//+------------------------------------------------------------------+
void CDoublePatternCore::MarkBottomTriggered()
  {
   m_activeBottom.hasTriggered = true;
   m_activeBottom.status       = STATUS_COMPLETED;
  }

//+------------------------------------------------------------------+
//| Tandai Pola Double Top Sudah Dieksekusi                          |
//+------------------------------------------------------------------+
void CDoublePatternCore::MarkTopTriggered()
  {
   m_activeTop.hasTriggered = true;
   m_activeTop.status       = STATUS_COMPLETED;
  }

//+------------------------------------------------------------------+
//| Tandai Pola Sudah Diberikan Sinyal / Dieksekusi Trade            |
//+------------------------------------------------------------------+
void CDoublePatternCore::MarkPatternTriggered()
  {
   if(m_activeBottom.status == STATUS_CONFIRMED) MarkBottomTriggered();
   if(m_activeTop.status == STATUS_CONFIRMED)    MarkTopTriggered();
  }
