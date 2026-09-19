import os
import shutil

def upgrade_mt5():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Version update
    code = code.replace('#property version   "3.10"', '#property version   "3.20"')
    code = code.replace('v3.10 (Adaptive AI Learning)', 'v3.20 (Autonomous Neuro-Calibration & Self-Tuning)')

    # 2. Input parameters
    input_decl = """input group "=== 8.9 AUTONOMOUS NEURO-CALIBRATION & SELF-TUNING (v3.20) ==="
input bool          InpUseAutoCalibration          = true;         // Aktifkan Kalibrasi Parameter Mandiri Real-Time (v3.20)
input double        InpAutoTuningSensitivity       = 1.35;         // Sensitivitas Deteksi Volatilitas (ATR14 / ATR100)
input int           InpCalibrationConsecLossMax    = 2;            // Pemicu Pengetatan Parameter Saat Loss Beruntun (Default: 2x)
input double        InpAutoTuningMaxBufferMult     = 1.6;          // Batas Maksimal Ekspansi Buffer SL (x ATR)
input double        InpAutoTuningScoreStep         = 5.0;          // Langkah Pengetatan Ambang Skor per Kejadian Loss
"""
    anchor_input = 'input group "=== 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ==="'
    code = code.replace(anchor_input, input_decl + "\n" + anchor_input)

    # 3. Handle declaration: h_atr100
    code = code.replace("int            h_atr14      = INVALID_HANDLE;", "int            h_atr14      = INVALID_HANDLE;\nint            h_atr100     = INVALID_HANDLE;")

    # 4. Calibration Struct & State right after LossAutopsyReport g_autopsy;
    calib_struct = """
//+------------------------------------------------------------------+
//| AUTONOMOUS NEURO-CALIBRATION STATE (v3.20)                       |
//+------------------------------------------------------------------+
struct AutoCalibrationState
{
   bool   isCalibrated;
   double slBufferAtrMult;        // Dynamic multiplier: default InpSLBufferAtrMult
   double scoreElevation;         // Dynamic score elevation
   int    cooldownBars;           // Dynamic cooldown bars
   double candleTrailBufferPts;   // Dynamic candle trail buffer
   double volatilityRatio;        // ATR14 / ATR100
   string regimeDescription;      // "Normal", "High Volatility Spike", "Choppy Compression"
   int    consecutiveLossStreak;  // Current active consecutive losses
};
AutoCalibrationState g_calibration = {false, 1.2, 0.0, 3, 15.0, 1.0, "Normal", 0};
"""
    anchor_struct = "LossAutopsyReport g_autopsy;"
    code = code.replace(anchor_struct, anchor_struct + "\n" + calib_struct)

    # 5. Handle creation in OnInit()
    init_handles_old = "h_atr14   = iATR(_Symbol, _Period, 14);"
    init_handles_new = "h_atr14   = iATR(_Symbol, _Period, 14);\n   h_atr100  = iATR(_Symbol, _Period, 100);"
    code = code.replace(init_handles_old, init_handles_new)

    check_handles_old = "h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE ||"
    check_handles_new = "h_ema125 == INVALID_HANDLE || h_atr14 == INVALID_HANDLE || h_atr100 == INVALID_HANDLE ||"
    code = code.replace(check_handles_old, check_handles_new)

    # 6. Handle release in OnDeinit()
    deinit_old = "if (h_atr14 != INVALID_HANDLE)      IndicatorRelease(h_atr14);"
    deinit_new = "if (h_atr14 != INVALID_HANDLE)      IndicatorRelease(h_atr14);\n   if (h_atr100 != INVALID_HANDLE)     IndicatorRelease(h_atr100);"
    code = code.replace(deinit_old, deinit_new)

    # 7. Function AutoCalibrateTradingParameters() right before void OnTick()
    calib_func = """//+------------------------------------------------------------------+
//| 8.9 AUTONOMOUS NEURO-CALIBRATION & SELF-TUNING ENGINE (v3.20)     |
//+------------------------------------------------------------------+
void AutoCalibrateTradingParameters()
{
   if (!InpUseAutoCalibration)
   {
      g_calibration.slBufferAtrMult      = InpSLBufferAtrMult;
      g_calibration.scoreElevation       = 0.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars;
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints;
      g_calibration.regimeDescription    = "Manual Static";
      return;
   }

   // 1. Baca ATR Jangka Pendek (14) dan Baseline Jangka Panjang (100)
   double atr14Buf[2];
   double atr14Val = 0.0;
   if (h_atr14 != INVALID_HANDLE && CopyBuffer(h_atr14, 0, 0, 2, atr14Buf) > 0)
      atr14Val = atr14Buf[1];

   double atr100Buf[2];
   double atr100Val = 0.0;
   if (h_atr100 != INVALID_HANDLE && CopyBuffer(h_atr100, 0, 0, 2, atr100Buf) > 0)
      atr100Val = atr100Buf[1];
   else
      atr100Val = atr14Val;

   double volRatio = (atr100Val > 0.0) ? (atr14Val / atr100Val) : 1.0;
   g_calibration.volatilityRatio = volRatio;

   // 2. Kalibrasi Adaptif berdasarkan Volatilitas
   if (volRatio >= InpAutoTuningSensitivity)
   {
      g_calibration.regimeDescription    = "High Volatility Spike";
      g_calibration.slBufferAtrMult      = MathMin(InpAutoTuningMaxBufferMult, InpSLBufferAtrMult * 1.35);
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints * 1.4;
      g_calibration.scoreElevation       = 10.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars + 1;
   }
   else if (volRatio <= 0.70 || (InpUseRegimeFilter && g_currentChoppiness > InpChoppyThreshold))
   {
      g_calibration.regimeDescription    = "Choppy Compression";
      g_calibration.slBufferAtrMult      = MathMax(0.8, InpSLBufferAtrMult * 0.9);
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints;
      g_calibration.scoreElevation       = 5.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars + 2;
   }
   else
   {
      g_calibration.regimeDescription    = "Normal Confluence";
      g_calibration.slBufferAtrMult      = InpSLBufferAtrMult;
      g_calibration.candleTrailBufferPts = InpCandleTrailBufferPoints;
      g_calibration.scoreElevation       = 0.0;
      g_calibration.cooldownBars         = InpSignalCooldownBars;
   }

   // 3. Kalibrasi Anti-Tilt pasca Loss Beruntun
   if (g_consecutiveLossCount >= InpCalibrationConsecLossMax)
   {
      g_calibration.scoreElevation += (g_consecutiveLossCount * InpAutoTuningScoreStep);
      g_calibration.cooldownBars = MathMin(8, InpSignalCooldownBars * g_consecutiveLossCount);
      g_calibration.slBufferAtrMult = MathMin(InpAutoTuningMaxBufferMult, g_calibration.slBufferAtrMult + 0.25);
   }

   g_calibration.consecutiveLossStreak = g_consecutiveLossCount;
   g_calibration.isCalibrated          = true;
}
"""
    code = code.replace("void OnTick()\n{", calib_func + "\nvoid OnTick()\n{\n   AutoCalibrateTradingParameters();")

    # 8. Connect effective values
    # Cooldown in signal checking
    code = code.replace(
        "if (lastOrderBarTime != 0 && (iTime(_Symbol, _Period, 0) - lastOrderBarTime) < (InpSignalCooldownBars * PeriodSeconds(_Period)))",
        "int effectiveCooldown = InpUseAutoCalibration ? g_calibration.cooldownBars : InpSignalCooldownBars;\n   if (lastOrderBarTime != 0 && (iTime(_Symbol, _Period, 0) - lastOrderBarTime) < (effectiveCooldown * PeriodSeconds(_Period)))"
    )

    # Effective score BUY
    code = code.replace(
        "double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltyBUY + hourPenaltyBUY;",
        "double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltyBUY + hourPenaltyBUY;"
    )

    # Effective score SELL
    code = code.replace(
        "double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltySELL + hourPenaltySELL;",
        "double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0) + dirPenaltySELL + hourPenaltySELL;"
    )

    # SL buffer in BUY
    code = code.replace(
        "slPrice = lastSwingLow.price - (InpSLBufferAtrMult * currentAtr);",
        "double effectiveBufferMultBUY = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);\n            slPrice = lastSwingLow.price - (effectiveBufferMultBUY * currentAtr);"
    )

    # SL buffer in SELL
    code = code.replace(
        "slPrice = lastSwingHigh.price + (InpSLBufferAtrMult * currentAtr);",
        "double effectiveBufferMultSELL = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);\n            slPrice = lastSwingHigh.price + (effectiveBufferMultSELL * currentAtr);"
    )

    # Candle trailing buffer
    code = code.replace(
        "double candleSL  = NormalizeDouble(candleLow - PointToPrice(InpCandleTrailBufferPoints), _Digits);",
        "double effectiveCandleBufBUY = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;\n      double candleSL  = NormalizeDouble(candleLow - PointToPrice(effectiveCandleBufBUY), _Digits);"
    )
    code = code.replace(
        "double candleSL   = NormalizeDouble(candleHigh + PointToPrice(InpCandleTrailBufferPoints), _Digits);",
        "double effectiveCandleBufSELL = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;\n      double candleSL   = NormalizeDouble(candleHigh + PointToPrice(effectiveCandleBufSELL), _Digits);"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("MT5 upgraded to v3.20 cleanly!")

if __name__ == '__main__':
    upgrade_mt5()
