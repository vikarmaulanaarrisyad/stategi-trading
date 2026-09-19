$targetDir = "C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_4Pillar_Pro"
Copy-Item "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5" "$targetDir\" -Force

$editor = "C:\Program Files\DIDIMAX MetaTrader 5\MetaEditor64.exe"
$args = @("/compile:$targetDir\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5", "/log:$targetDir\compile.log")

Start-Process -FilePath $editor -ArgumentList $args -Wait

Start-Sleep -Milliseconds 500
Get-Content "$targetDir\compile.log" -Tail 20
Copy-Item "$targetDir\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5" "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\" -Force
Copy-Item "$targetDir\compile.log" "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\" -Force
Get-Item "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5" | Format-List FullName, LastWriteTime, Length
