$meta = "C:\Program Files (x86)\QuickPro MT4 Terminal\metaeditor.exe"
$src = "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4"
$log = "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\compile_mt4.log"
Start-Process -FilePath $meta -ArgumentList "/compile:`"$src`" /log:`"$log`"" -Wait
Start-Sleep -Seconds 2
Get-Content $log
$targetDir = "C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\F0B9948E0028C307A69410B7E4F7F6B6\MQL4\Experts"
Copy-Item "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.mq4" $targetDir -Force
Copy-Item "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_MT4\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.ex4" $targetDir -Force
Get-Item "$targetDir\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR_MT4.ex4" | Format-List FullName, LastWriteTime, Length
