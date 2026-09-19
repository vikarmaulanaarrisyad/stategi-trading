import os
import shutil

def upgrade_mt4():
    path = r"e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
    bak_path = path + ".v310.bak"
    shutil.copyfile(path, bak_path)
    print(f"Created backup: {bak_path}")

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    # 1. Update version
    code = code.replace('#property version   "3.10"', '#property version   "3.20"')
    code = code.replace('v3.10 (Adaptive AI Learning)', 'v3.20 (Autonomous Neuro-Calibration & Self-Tuning)')

    # 2. Add extern parameters
    param_code = """//--- 8.9 AUTONOMOUS NEURO-CALIBRATION & SELF-TUNING (v3.20) ---
extern string       sec89                 = "=== 8.9 AUTONOMOUS NEURO-CALIBRATION (v3.20) ===";
extern bool         InpUseAutoCalibration         = true;         // Aktifkan Kalibrasi Parameter Mandiri Real-Time (v3.20)
extern double       InpAutoTuningSensitivity      = 1.35;         // Sensitivitas Deteksi Volatilitas (ATR14 / ATR100)
extern int          InpCalibrationConsecLossMax   = 2;            // Pemicu Pengetatan Parameter Saat Loss Beruntun (Default: 2x)
extern double       InpAutoTuningMaxBufferMult    = 1.6;          // Batas Maksimal Ekspansi Buffer SL (x ATR)
extern double       InpAutoTuningScoreStep        = 5.0;          // Langkah Pengetatan Ambang Skor per Kejadian Loss
"""
    anchor_param = '//--- 8.8 SENSOR KELELAHAN MOMENTUM: RSI DIVERGENCE (v2.60) ---'
    code = code.replace(anchor_param, param_code + "\n" + anchor_param)

    # 3. Add struct after LossAutopsyReport g_autopsy;
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
AutoCalibrationState g_calibration = {false, 1.0, 0.0, 2, 15.0, 1.0, "Normal", 0};
"""
    code = code.replace("LossAutopsyReport g_autopsy;", "LossAutopsyReport g_autopsy;\n" + calib_struct)

    # 4. AutoCalibrateTradingParameters() definition
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

   double atr14Val  = iATR(_Symbol, _Period, 14, 1);
   double atr100Val = iATR(_Symbol, _Period, 100, 1);
   if (atr100Val <= 0.0) atr100Val = atr14Val;

   double volRatio = (atr100Val > 0.0) ? (atr14Val / atr100Val) : 1.0;
   g_calibration.volatilityRatio = volRatio;

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
    code = code.replace("int start()\n{", calib_func + "\nint start()\n{\n   AutoCalibrateTradingParameters();")

    # 5. Connect effective values in MT4
    # Cooldown check
    code = code.replace(
        "if (lastOrderBarTime != 0 && (Time[0] - lastOrderBarTime) < (InpSignalCooldownBars * (Period() * 60)))",
        "int effectiveCooldown = InpUseAutoCalibration ? g_calibration.cooldownBars : InpSignalCooldownBars;\n   if (lastOrderBarTime != 0 && (Time[0] - lastOrderBarTime) < (effectiveCooldown * (Period() * 60)))"
    )

    # Score BUY
    code = code.replace(
        "double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);",
        "double effectiveMinScoreBUY = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);"
    )

    # Score SELL
    code = code.replace(
        "double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);",
        "double effectiveMinScoreSELL = InpMinConfluenceScore + (InpUseAutoCalibration ? g_calibration.scoreElevation : 0.0) + (InpUseSelfHealing && g_autopsy.isActive ? g_autopsy.scorePenalty : 0.0);"
    )

    # SL calculation in BUY
    code = code.replace(
        "slPrice = lastSwingLow.price - (InpSLBufferAtrMult * currentAtr);",
        "double effectiveBufferMultBUY = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);\n            slPrice = lastSwingLow.price - (effectiveBufferMultBUY * currentAtr);"
    )

    # SL calculation in SELL
    code = code.replace(
        "slPrice = lastSwingHigh.price + (InpSLBufferAtrMult * currentAtr);",
        "double effectiveBufferMultSELL = (InpUseAutoCalibration ? g_calibration.slBufferAtrMult : InpSLBufferAtrMult) + ((InpUseSelfHealing && g_autopsy.tradesWithExtraBuffer > 0) ? InpAdaptiveSLBufferBoost : 0.0);\n            slPrice = lastSwingHigh.price + (effectiveBufferMultSELL * currentAtr);"
    )

    # Candle trailing buffer in MT4
    code = code.replace(
        "double candleSL  = NormalizeDouble(candleLow - PointToPrice(InpCandleTrailBufferPoints), Digits);",
        "double effectiveCandleBufBUY = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;\n      double candleSL  = NormalizeDouble(candleLow - PointToPrice(effectiveCandleBufBUY), Digits);"
    )
    code = code.replace(
        "double candleSL   = NormalizeDouble(candleHigh + PointToPrice(InpCandleTrailBufferPoints), Digits);",
        "double effectiveCandleBufSELL = InpUseAutoCalibration ? g_calibration.candleTrailBufferPts : InpCandleTrailBufferPoints;\n      double candleSL   = NormalizeDouble(candleHigh + PointToPrice(effectiveCandleBufSELL), Digits);"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    print("MT4 upgraded to v3.20 cleanly!")

if __name__ == '__main__':
    upgrade_mt4()
