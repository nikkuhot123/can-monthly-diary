$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

do {
    $proc = Get-NetTCPConnection -LocalPort 9931 -ErrorAction SilentlyContinue
    $stopped = $false
    if ($proc -and $proc.OwningProcess -gt 4) {
        Write-Host ("Port 9931 in use by PID " + $proc.OwningProcess + ", stopping...")
        Stop-Process -Id $proc.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $stopped = $true
    } elseif ($proc) {
        Write-Host "Port 9931 in TIME_WAIT, waiting..."
        Start-Sleep -Seconds 3
        $stopped = $true
    }
} while ($stopped)

Write-Host "Starting Audit Diary System on http://127.0.0.1:9931"
.\venv\Scripts\python main.py
