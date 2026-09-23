$metaEditor = "C:\Program Files\DIDIMAX MetaTrader 5\MetaEditor64.exe"
$mq5File = "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.mq5"
$logFile = "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\compile.log"
$ex5File = "e:\Python\STRATEGY\VIKAR_EA_4PILLAR_PRO\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5"

if (Test-Path $logFile) { Remove-Item $logFile -Force }

Write-Host "[+] Compiling $mq5File ..."
Start-Process -FilePath $metaEditor -ArgumentList "/compile:`"$mq5File`" /log:`"$logFile`"" -Wait

Start-Sleep -Seconds 2

if (Test-Path $logFile) {
    $logContent = Get-Content $logFile -Encoding Unicode -ErrorAction SilentlyContinue
    if (-not $logContent) {
        $logContent = Get-Content $logFile -ErrorAction SilentlyContinue
    }
    Write-Host "`n--- COMPILATION LOG ---"
    $logContent | Select-Object -Last 10 | ForEach-Object { Write-Host $_ }
    Write-Host "-----------------------`n"
}

if (Test-Path $ex5File) {
    $item = Get-Item $ex5File
    Write-Host "[OK] Binary EX5 built successfully! Size: $($item.Length) bytes, Modified: $($item.LastWriteTime)"

    $dest1 = "C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5"
    $dest2 = "C:\Users\vikar\AppData\Roaming\MetaQuotes\Terminal\7F6536B8EF31BF48E728E401B7692A0A\MQL5\Experts\VIKAR_4Pillar_Pro\VIKAR_EA_4Pillar_SMC_EMA_Fibo_SR.ex5"

    Copy-Item $ex5File $dest1 -Force
    Write-Host "[+] Deployed to: $dest1"
    Copy-Item $ex5File $dest2 -Force
    Write-Host "[+] Deployed to: $dest2"
} else {
    Write-Host "[-] Compilation failed: EX5 file not found."
}
