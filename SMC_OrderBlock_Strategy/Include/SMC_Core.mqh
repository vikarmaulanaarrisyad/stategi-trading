//+------------------------------------------------------------------+
//|                                                     SMC_Core.mqh |
//|                     Smart Money Concepts (SMC) Core Engine       |
//|                         Copyright 2026, XAUUSD Senior Trader     |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026, XAUUSD Senior Trader"
#property link      ""
#property version   "1.10"

//+------------------------------------------------------------------+
//| Enum Struktur Pasar SMC                                          |
//+------------------------------------------------------------------+
enum ENUM_SMC_STRUCTURE
  {
   SMC_STRUCT_NEUTRAL,        // Belum ada struktur dominan
   SMC_STRUCT_BULLISH_BOS,    // Break of Structure Naik (Trend Continuation)
   SMC_STRUCT_BEARISH_BOS,    // Break of Structure Turun (Trend Continuation)
   SMC_STRUCT_BULLISH_CHOCH,  // Change of Character Naik (Reversal Bullish)
   SMC_STRUCT_BEARISH_CHOCH   // Change of Character Turun (Reversal Bearish)
  };

//+------------------------------------------------------------------+
//| Struct Order Block (OB)                                          |
//+------------------------------------------------------------------+
struct SMC_OrderBlock
  {
   datetime time;             // Waktu pembentukan candle OB
   double   high;             // Batas atas kotak OB
   double   low;              // Batas bawah kotak OB
   double   open;             // Open price candle OB
   double   close;            // Close price candle OB
   bool     isBullish;        // true = Bullish OB (Demand), false = Bearish OB (Supply)
   bool     hasDeparted;      // true jika harga sudah bergerak menjauhi zona OB
   bool     isMitigated;      // true jika sudah pernah disentuh harga retest setelah departure
   bool     isInvalidated;    // true jika harga menembus batas berlawanan (broken OB)
   datetime mitigatedTime;    // Waktu mitigasi
   int      barIndex;         // Index bar saat terbentuk
   bool     hasTriggered;     // true jika sudah dieksekusi trade pada retest ini
  };

//+------------------------------------------------------------------+
//| Struct Fair Value Gap (FVG / Imbalance)                          |
//+------------------------------------------------------------------+
struct SMC_FairValueGap
  {
   datetime time;             // Waktu Lilin ke-2 (Lilin Gap Imbalance)
   double   top;              // Batas atas gap
   double   bottom;           // Batas bawah gap
   bool     isBullish;        // true = Bullish FVG, false = Bearish FVG
   bool     isMitigated;      // true jika gap sudah terisi
   datetime mitigatedTime;    // Waktu mitigasi
   int      barIndex;
  };

//+------------------------------------------------------------------+
//| Struct Swing High / Swing Low Point                              |
//+------------------------------------------------------------------+
struct SMC_SwingPoint
  {
   datetime time;
   double   price;
   bool     isHigh;           // true = Swing High, false = Swing Low
   int      barIndex;
  };

//+------------------------------------------------------------------+
//| Class Mesin Inti Smart Money Concepts (SMC)                      |
//+------------------------------------------------------------------+
class CSMCCore
  {
private:
   int               m_swingLookback;     // Lookback fractal swing (default 3 atau 5)
   int               m_maxZones;          // Maksimal zona aktif tersimpan (default 12)
   double            m_minFvgPoints;      // Ukuran minimal FVG dalam points
   double            m_minObPoints;       // Ukuran minimal OB dalam points

   SMC_SwingPoint    m_swings[];          // Daftar swing points terbaru
   SMC_OrderBlock    m_orderBlocks[];     // Daftar Order Blocks aktif
   SMC_FairValueGap  m_fvgs[];            // Daftar Fair Value Gaps aktif

   ENUM_SMC_STRUCTURE m_lastStructure;    // Status struktur terakhir
   datetime          m_lastChochTime;     // Waktu CHoCH terakhir
   datetime          m_lastBosTime;       // Waktu BOS terakhir

public:
                     CSMCCore();
                    ~CSMCCore();

   void              Configure(int swingLookback = 3, int maxZones = 12, double minFvgPoints = 30.0, double minObPoints = 20.0);
   void              Update(const MqlRates &rates[], int totalBars);

   // Akses Data
   ENUM_SMC_STRUCTURE GetLastStructure() const { return m_lastStructure; }
   datetime          GetLastBosTime() const { return m_lastBosTime; }
   datetime          GetLastChochTime() const { return m_lastChochTime; }

   int               GetOrderBlocksTotal() const { return ArraySize(m_orderBlocks); }
   bool              GetOrderBlock(int index, SMC_OrderBlock &ob) const;
   int               GetFvgsTotal() const { return ArraySize(m_fvgs); }
   bool              GetFvg(int index, SMC_FairValueGap &fvg) const;
   int               GetSwingsTotal() const { return ArraySize(m_swings); }
   bool              GetSwing(int index, SMC_SwingPoint &sp) const;

   // Deteksi Retest Masuk Zona (Hanya OB yang sudah depart dan belum termitigasi)
   bool              IsRetestingBullishOB(double currentPrice, SMC_OrderBlock &outOB) const;
   bool              IsRetestingBearishOB(double currentPrice, SMC_OrderBlock &outOB) const;
   bool              IsRetestingBullishFVG(double currentPrice, SMC_FairValueGap &outFVG) const;
   bool              IsRetestingBearishFVG(double currentPrice, SMC_FairValueGap &outFVG) const;

   // Tandai OB sudah dieksekusi agar tidak terjadi entri berulang
   void              MarkOrderBlockTriggered(datetime obTime);

   // Cek apakah ada FVG unmitigated yang mendukung OB (Confluence)
   bool              HasFVGConfluence(const SMC_OrderBlock &ob) const;

   // Analisis Premium vs Discount (Fibonacci 50% Equilibrium)
   bool              IsInDiscountZone(double price) const;
   bool              IsInPremiumZone(double price) const;
   double            GetDealingRangeHigh() const;
   double            GetDealingRangeLow() const;

private:
   double            CalculateAverageATR(const MqlRates &rates[], int totalBars, int period = 14);
   void              ScanSwingPoints(const MqlRates &rates[], int totalBars);
   void              ScanStructureBreaks(const MqlRates &rates[], int totalBars);
   void              ScanOrderBlocks(const MqlRates &rates[], int totalBars, double avgAtr);
   void              ScanFairValueGaps(const MqlRates &rates[], int totalBars, double avgAtr);
   void              UpdateMitigations(const MqlRates &rates[], int totalBars);
  };

//+------------------------------------------------------------------+
//| Constructor                                                      |
//+------------------------------------------------------------------+
CSMCCore::CSMCCore()
  {
   m_swingLookback = 3;
   m_maxZones      = 12;
   m_minFvgPoints  = 30.0;
   m_minObPoints   = 20.0;
   m_lastStructure = SMC_STRUCT_NEUTRAL;
   m_lastChochTime = 0;
   m_lastBosTime   = 0;

   ArrayResize(m_swings, 0);
   ArrayResize(m_orderBlocks, 0);
   ArrayResize(m_fvgs, 0);
  }

//+------------------------------------------------------------------+
//| Destructor                                                       |
//+------------------------------------------------------------------+
CSMCCore::~CSMCCore()
  {
   ArrayFree(m_swings);
   ArrayFree(m_orderBlocks);
   ArrayFree(m_fvgs);
  }

//+------------------------------------------------------------------+
//| Konfigurasi Parameter                                            |
//+------------------------------------------------------------------+
void CSMCCore::Configure(int swingLookback = 3, int maxZones = 12, double minFvgPoints = 30.0, double minObPoints = 20.0)
  {
   m_swingLookback = MathMax(2, swingLookback);
   m_maxZones      = MathMax(4, maxZones);
   m_minFvgPoints  = minFvgPoints;
   m_minObPoints   = minObPoints;
  }

//+------------------------------------------------------------------+
//| Hitung Rata-Rata ATR Sederhana                                   |
//+------------------------------------------------------------------+
double CSMCCore::CalculateAverageATR(const MqlRates &rates[], int totalBars, int period = 14)
  {
   int count = MathMin(totalBars - 1, period);
   if(count <= 0) return (1.0 * _Point);

   double sumRange = 0.0;
   for(int i = 1; i <= count; i++)
     {
      sumRange += (rates[i].high - rates[i].low);
     }
   double avg = sumRange / (double)count;
   return (avg > 0.0 ? avg : 1.0 * _Point);
  }

//+------------------------------------------------------------------+
//| Update Analisis SMC Lengkap Setiap Bar                           |
//+------------------------------------------------------------------+
void CSMCCore::Update(const MqlRates &rates[], int totalBars)
  {
   if(totalBars < (m_swingLookback * 2 + 15)) return;

   double avgAtr = CalculateAverageATR(rates, totalBars, 14);

   ScanSwingPoints(rates, totalBars);
   ScanStructureBreaks(rates, totalBars);
   ScanOrderBlocks(rates, totalBars, avgAtr);
   ScanFairValueGaps(rates, totalBars, avgAtr);
   UpdateMitigations(rates, totalBars);
  }

//+------------------------------------------------------------------+
//| Pindai Swing High dan Swing Low Fractals                         |
//+------------------------------------------------------------------+
void CSMCCore::ScanSwingPoints(const MqlRates &rates[], int totalBars)
  {
   ArrayResize(m_swings, 0);
   int lookbackLimit = MathMin(totalBars - m_swingLookback - 1, 150);

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
//| Deteksi Penembusan Struktur: BOS & CHoCH (Rekonstruksi Historis) |
//+------------------------------------------------------------------+
void CSMCCore::ScanStructureBreaks(const MqlRates &rates[], int totalBars)
  {
   int swingCount = ArraySize(m_swings);
   if(swingCount < 4) return;

   // 1. Cari Swing High dan Swing Low terdekat dari bar 1
   double nearestSwingHigh = 0.0;
   double nearestSwingLow  = 0.0;
   datetime swingHighTime  = 0;
   datetime swingLowTime   = 0;

   for(int i = 0; i < swingCount; i++)
     {
      if(m_swings[i].isHigh && nearestSwingHigh == 0.0 && m_swings[i].barIndex >= 2)
        {
         nearestSwingHigh = m_swings[i].price;
         swingHighTime    = m_swings[i].time;
        }
      if(!m_swings[i].isHigh && nearestSwingLow == 0.0 && m_swings[i].barIndex >= 2)
        {
         nearestSwingLow = m_swings[i].price;
         swingLowTime    = m_swings[i].time;
        }

      if(nearestSwingHigh > 0.0 && nearestSwingLow > 0.0) break;
     }

   // 2. Tentukan status struktur terkini berdasarkan posisi harga terhadap swing terdekat
   if(nearestSwingHigh > 0.0 && rates[1].close > nearestSwingHigh)
     {
      if(m_lastStructure == SMC_STRUCT_BEARISH_BOS || m_lastStructure == SMC_STRUCT_BEARISH_CHOCH)
        {
         m_lastStructure = SMC_STRUCT_BULLISH_CHOCH;
         m_lastChochTime = rates[1].time;
        }
      else
        {
         m_lastStructure = SMC_STRUCT_BULLISH_BOS;
         m_lastBosTime   = rates[1].time;
        }
     }
   else if(nearestSwingLow > 0.0 && rates[1].close < nearestSwingLow)
     {
      if(m_lastStructure == SMC_STRUCT_BULLISH_BOS || m_lastStructure == SMC_STRUCT_BULLISH_CHOCH)
        {
         m_lastStructure = SMC_STRUCT_BEARISH_CHOCH;
         m_lastChochTime = rates[1].time;
        }
      else
        {
         m_lastStructure = SMC_STRUCT_BEARISH_BOS;
         m_lastBosTime   = rates[1].time;
        }
     }
   else if(m_lastStructure == SMC_STRUCT_NEUTRAL)
     {
      // Rekonstruksi jika baru startup: periksa perbandingan swing points
      double h1 = 0, h2 = 0, l1 = 0, l2 = 0;
      for(int i = 0; i < swingCount; i++)
        {
         if(m_swings[i].isHigh)
           {
            if(h1 == 0) h1 = m_swings[i].price;
            else if(h2 == 0) h2 = m_swings[i].price;
           }
         else
           {
            if(l1 == 0) l1 = m_swings[i].price;
            else if(l2 == 0) l2 = m_swings[i].price;
           }
        }

      if(h1 > h2 && l1 > l2) m_lastStructure = SMC_STRUCT_BULLISH_BOS;
      else if(h1 < h2 && l1 < l2) m_lastStructure = SMC_STRUCT_BEARISH_BOS;
     }
  }

//+------------------------------------------------------------------+
//| Pindai Pembentukan Order Block (OB) Berbasis Displacement & ATR  |
//+------------------------------------------------------------------+
void CSMCCore::ScanOrderBlocks(const MqlRates &rates[], int totalBars, double avgAtr)
  {
   int oldSize = ArraySize(m_orderBlocks);

   SMC_OrderBlock temp[];
   ArrayResize(temp, 0);

   int limit = MathMin(totalBars - 4, 80);

   for(int i = 2; i < limit; i++)
     {
      double obRange = rates[i].high - rates[i].low;
      if(obRange < (m_minObPoints * _Point)) continue;

      // 1. BULLISH ORDER BLOCK: Candle bearish sebelum lonjakan displacement naik kuat
      bool isBearish = (rates[i].close < rates[i].open);
      double dispBodyBull = rates[i - 1].close - rates[i - 1].open;
      bool strongBullishDisp = (rates[i - 1].close > rates[i].high && 
                                dispBodyBull > (obRange * 0.7) && 
                                dispBodyBull >= (avgAtr * 0.6));

      if(isBearish && strongBullishDisp)
        {
         int sz = ArraySize(temp);
         if(sz < m_maxZones)
           {
            ArrayResize(temp, sz + 1);
            temp[sz].time          = rates[i].time;
            temp[sz].high          = rates[i].high;
            temp[sz].low           = rates[i].low;
            temp[sz].open          = rates[i].open;
            temp[sz].close         = rates[i].close;
            temp[sz].isBullish     = true;
            temp[sz].hasDeparted   = false;
            temp[sz].isMitigated   = false;
            temp[sz].isInvalidated = false;
            temp[sz].mitigatedTime = 0;
            temp[sz].barIndex      = i;
            temp[sz].hasTriggered  = false;

            for(int o = 0; o < oldSize; o++)
              {
               if(m_orderBlocks[o].time == rates[i].time)
                 {
                  temp[sz].hasTriggered = m_orderBlocks[o].hasTriggered;
                  break;
                 }
              }
           }
        }

      // 2. BEARISH ORDER BLOCK: Candle bullish sebelum lonjakan displacement turun kuat
      bool isBullish = (rates[i].close > rates[i].open);
      double dispBodyBear = rates[i - 1].open - rates[i - 1].close;
      bool strongBearishDisp = (rates[i - 1].close < rates[i].low && 
                                dispBodyBear > (obRange * 0.7) && 
                                dispBodyBear >= (avgAtr * 0.6));

      if(isBullish && strongBearishDisp)
        {
         int sz = ArraySize(temp);
         if(sz < m_maxZones)
           {
            ArrayResize(temp, sz + 1);
            temp[sz].time          = rates[i].time;
            temp[sz].high          = rates[i].high;
            temp[sz].low           = rates[i].low;
            temp[sz].open          = rates[i].open;
            temp[sz].close         = rates[i].close;
            temp[sz].isBullish     = false;
            temp[sz].hasDeparted   = false;
            temp[sz].isMitigated   = false;
            temp[sz].isInvalidated = false;
            temp[sz].mitigatedTime = 0;
            temp[sz].barIndex      = i;
            temp[sz].hasTriggered  = false;

            for(int o = 0; o < oldSize; o++)
              {
               if(m_orderBlocks[o].time == rates[i].time)
                 {
                  temp[sz].hasTriggered = m_orderBlocks[o].hasTriggered;
                  break;
                 }
              }
           }
        }
     }

   int newCount = ArraySize(temp);
   ArrayResize(m_orderBlocks, newCount);
   for(int j = 0; j < newCount; j++)
     {
      m_orderBlocks[j] = temp[j];
     }
  }

//+------------------------------------------------------------------+
//| Pindai Pembentukan Fair Value Gap (FVG / Imbalance)              |
//+------------------------------------------------------------------+
void CSMCCore::ScanFairValueGaps(const MqlRates &rates[], int totalBars, double avgAtr)
  {
   ArrayResize(m_fvgs, 0);
   int limit = MathMin(totalBars - 4, 80);

   for(int i = 2; i < limit; i++)
     {
      // Pola 3 candle: [i+1], [i], [i-1]
      // 1. BULLISH FVG
      double bullGap = rates[i - 1].low - rates[i + 1].high;
      if(bullGap >= (m_minFvgPoints * _Point) && rates[i].close > rates[i].open)
        {
         int sz = ArraySize(m_fvgs);
         if(sz < m_maxZones)
           {
            ArrayResize(m_fvgs, sz + 1);
            m_fvgs[sz].time          = rates[i].time;
            m_fvgs[sz].top           = rates[i - 1].low;
            m_fvgs[sz].bottom        = rates[i + 1].high;
            m_fvgs[sz].isBullish     = true;
            m_fvgs[sz].isMitigated   = false;
            m_fvgs[sz].mitigatedTime = 0;
            m_fvgs[sz].barIndex      = i;
           }
        }

      // 2. BEARISH FVG
      double bearGap = rates[i + 1].low - rates[i - 1].high;
      if(bearGap >= (m_minFvgPoints * _Point) && rates[i].close < rates[i].open)
        {
         int sz = ArraySize(m_fvgs);
         if(sz < m_maxZones)
           {
            ArrayResize(m_fvgs, sz + 1);
            m_fvgs[sz].time          = rates[i].time;
            m_fvgs[sz].top           = rates[i + 1].low;
            m_fvgs[sz].bottom        = rates[i - 1].high;
            m_fvgs[sz].isBullish     = false;
            m_fvgs[sz].isMitigated   = false;
            m_fvgs[sz].mitigatedTime = 0;
            m_fvgs[sz].barIndex      = i;
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Perbarui Status Departure, Retest & Mitigasi Zona (SMC Akurat)   |
//+------------------------------------------------------------------+
void CSMCCore::UpdateMitigations(const MqlRates &rates[], int totalBars)
  {
   // 1. EVALUASI ORDER BLOCKS
   int obCount = ArraySize(m_orderBlocks);
   for(int i = 0; i < obCount; i++)
     {
      int obBar = m_orderBlocks[i].barIndex;

      // Cek apakah harga sudah pernah meninggalkan zona (Departure)
      bool departed = false;
      int departureBar = -1;

      for(int k = obBar - 1; k >= 1; k--)
        {
         if(m_orderBlocks[i].isBullish)
           {
            if(rates[k].close > m_orderBlocks[i].high)
              {
               departed = true;
               departureBar = k;
               break;
              }
           }
         else
           {
            if(rates[k].close < m_orderBlocks[i].low)
              {
               departed = true;
               departureBar = k;
               break;
              }
           }
        }

      m_orderBlocks[i].hasDeparted = departed;
      if(!departed) continue; // Belum meninggalkan zona, belum siap di-retest

      // Setelah departure terjadi, cek apakah ada candle historis yang telah me-retest / mitigasi zona
      for(int k = departureBar - 1; k >= 1; k--)
        {
         if(m_orderBlocks[i].isBullish)
           {
            // Jika candle close menembus batas bawah OB -> Invalidation (Broken OB)
            if(rates[k].close < m_orderBlocks[i].low)
              {
               m_orderBlocks[i].isInvalidated = true;
               m_orderBlocks[i].isMitigated   = true;
               m_orderBlocks[i].mitigatedTime = rates[k].time;
               break;
              }
            // Jika harga masuk ke zona (low <= high) dan terjadi di bar k >= 2 (sebelum closed bar 1)
            if(rates[k].low <= m_orderBlocks[i].high)
              {
               if(k >= 2)
                 {
                  m_orderBlocks[i].isMitigated   = true;
                  m_orderBlocks[i].mitigatedTime = rates[k].time;
                  break;
                 }
              }
           }
         else
           {
            if(rates[k].close > m_orderBlocks[i].high)
              {
               m_orderBlocks[i].isInvalidated = true;
               m_orderBlocks[i].isMitigated   = true;
               m_orderBlocks[i].mitigatedTime = rates[k].time;
               break;
              }
            if(rates[k].high >= m_orderBlocks[i].low)
              {
               if(k >= 2)
                 {
                  m_orderBlocks[i].isMitigated   = true;
                  m_orderBlocks[i].mitigatedTime = rates[k].time;
                  break;
                 }
              }
           }
        }
     }

   // 2. EVALUASI FAIR VALUE GAPS (FVG)
   int fvgCount = ArraySize(m_fvgs);
   for(int i = 0; i < fvgCount; i++)
     {
      int startIdx = m_fvgs[i].barIndex - 2;

      for(int k = startIdx; k >= 1; k--)
        {
         if(m_fvgs[i].isBullish)
           {
            if(rates[k].low <= m_fvgs[i].bottom)
              {
               m_fvgs[i].isMitigated   = true;
               m_fvgs[i].mitigatedTime = rates[k].time;
               break;
              }
           }
         else
           {
            if(rates[k].high >= m_fvgs[i].top)
              {
               m_fvgs[i].isMitigated   = true;
               m_fvgs[i].mitigatedTime = rates[k].time;
               break;
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Getter Objek Tunggal                                             |
//+------------------------------------------------------------------+
bool CSMCCore::GetOrderBlock(int index, SMC_OrderBlock &ob) const
  {
   if(index < 0 || index >= ArraySize(m_orderBlocks)) return false;
   ob = m_orderBlocks[index];
   return true;
  }

bool CSMCCore::GetFvg(int index, SMC_FairValueGap &fvg) const
  {
   if(index < 0 || index >= ArraySize(m_fvgs)) return false;
   fvg = m_fvgs[index];
   return true;
  }

bool CSMCCore::GetSwing(int index, SMC_SwingPoint &sp) const
  {
   if(index < 0 || index >= ArraySize(m_swings)) return false;
   sp = m_swings[index];
   return true;
  }

//+------------------------------------------------------------------+
//| Cek Retest Bullish OB (Hanya OB Valid yang Belum Termitigasi)    |
//+------------------------------------------------------------------+
bool CSMCCore::IsRetestingBullishOB(double currentPrice, SMC_OrderBlock &outOB) const
  {
   int obCount = ArraySize(m_orderBlocks);
   for(int i = 0; i < obCount; i++)
     {
      if(m_orderBlocks[i].isBullish && 
         m_orderBlocks[i].hasDeparted && 
         !m_orderBlocks[i].isMitigated && 
         !m_orderBlocks[i].isInvalidated &&
         !m_orderBlocks[i].hasTriggered)
        {
         if(currentPrice <= (m_orderBlocks[i].high + 15 * _Point) && 
            currentPrice >= (m_orderBlocks[i].low - 15 * _Point))
           {
            outOB = m_orderBlocks[i];
            return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Retest Bearish OB (Hanya OB Valid yang Belum Termitigasi)    |
//+------------------------------------------------------------------+
bool CSMCCore::IsRetestingBearishOB(double currentPrice, SMC_OrderBlock &outOB) const
  {
   int obCount = ArraySize(m_orderBlocks);
   for(int i = 0; i < obCount; i++)
     {
      if(!m_orderBlocks[i].isBullish && 
         m_orderBlocks[i].hasDeparted && 
         !m_orderBlocks[i].isMitigated && 
         !m_orderBlocks[i].isInvalidated &&
         !m_orderBlocks[i].hasTriggered)
        {
         if(currentPrice >= (m_orderBlocks[i].low - 15 * _Point) && 
            currentPrice <= (m_orderBlocks[i].high + 15 * _Point))
           {
            outOB = m_orderBlocks[i];
            return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Retest Bullish FVG                                           |
//+------------------------------------------------------------------+
bool CSMCCore::IsRetestingBullishFVG(double currentPrice, SMC_FairValueGap &outFVG) const
  {
   int fvgCount = ArraySize(m_fvgs);
   for(int i = 0; i < fvgCount; i++)
     {
      if(m_fvgs[i].isBullish && !m_fvgs[i].isMitigated)
        {
         if(currentPrice <= m_fvgs[i].top && currentPrice >= m_fvgs[i].bottom)
           {
            outFVG = m_fvgs[i];
            return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Cek Retest Bearish FVG                                           |
//+------------------------------------------------------------------+
bool CSMCCore::IsRetestingBearishFVG(double currentPrice, SMC_FairValueGap &outFVG) const
  {
   int fvgCount = ArraySize(m_fvgs);
   for(int i = 0; i < fvgCount; i++)
     {
      if(!m_fvgs[i].isBullish && !m_fvgs[i].isMitigated)
        {
         if(currentPrice >= m_fvgs[i].bottom && currentPrice <= m_fvgs[i].top)
           {
            outFVG = m_fvgs[i];
            return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Tandai Bahwa Order Block Sudah Dieksekusi Trade                  |
//+------------------------------------------------------------------+
void CSMCCore::MarkOrderBlockTriggered(datetime obTime)
  {
   int obCount = ArraySize(m_orderBlocks);
   for(int i = 0; i < obCount; i++)
     {
      if(m_orderBlocks[i].time == obTime)
        {
         m_orderBlocks[i].hasTriggered = true;
         m_orderBlocks[i].isMitigated   = true;
         m_orderBlocks[i].mitigatedTime = TimeCurrent();
         break;
        }
     }
  }

//+------------------------------------------------------------------+
//| Cek Apakah Ada FVG yang Terbentuk di Sekitar Order Block         |
//+------------------------------------------------------------------+
bool CSMCCore::HasFVGConfluence(const SMC_OrderBlock &ob) const
  {
   int fvgCount = ArraySize(m_fvgs);
   for(int i = 0; i < fvgCount; i++)
     {
      if(m_fvgs[i].isBullish == ob.isBullish)
        {
         if(MathAbs((int)(m_fvgs[i].time - ob.time)) <= PeriodSeconds() * 3)
           {
            return true;
           }
        }
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Ambil Batas Atas Range Transaksi (Dealing Range High)            |
//+------------------------------------------------------------------+
double CSMCCore::GetDealingRangeHigh() const
  {
   int swingCount = ArraySize(m_swings);
   for(int i = 0; i < swingCount; i++)
     {
      if(m_swings[i].isHigh) return m_swings[i].price;
     }
   return 0.0;
  }

//+------------------------------------------------------------------+
//| Ambil Batas Bawah Range Transaksi (Dealing Range Low)            |
//+------------------------------------------------------------------+
double CSMCCore::GetDealingRangeLow() const
  {
   int swingCount = ArraySize(m_swings);
   for(int i = 0; i < swingCount; i++)
     {
      if(!m_swings[i].isHigh) return m_swings[i].price;
     }
   return 0.0;
  }

//+------------------------------------------------------------------+
//| Cek Apakah Harga Berada di Zona Diskon (< 50% Equilibrium)       |
//+------------------------------------------------------------------+
bool CSMCCore::IsInDiscountZone(double price) const
  {
   double hi = GetDealingRangeHigh();
   double lo = GetDealingRangeLow();
   if(hi <= 0.0 || lo <= 0.0 || hi <= lo) return true;

   double eq = lo + (hi - lo) * 0.5;
   return (price <= eq);
  }

//+------------------------------------------------------------------+
//| Cek Apakah Harga Berada di Zona Premium (> 50% Equilibrium)      |
//+------------------------------------------------------------------+
bool CSMCCore::IsInPremiumZone(double price) const
  {
   double hi = GetDealingRangeHigh();
   double lo = GetDealingRangeLow();
   if(hi <= 0.0 || lo <= 0.0 || hi <= lo) return true;

   double eq = lo + (hi - lo) * 0.5;
   return (price >= eq);
  }
