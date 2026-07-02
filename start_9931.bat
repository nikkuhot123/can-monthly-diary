@echo off
setlocal
cd /d "%~dp0"

echo Starting Audit Diary System on http://127.0.0.1:9931
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$maxAttempts = 10; $attempt = 0; " ^
    "do { " ^
    "  $proc = Get-NetTCPConnection -LocalPort 9931 -ErrorAction SilentlyContinue | Select-Object -First 1; " ^
    "  $stillBusy = $false; $attempt++; " ^
    "  if ($proc -and $proc.OwningProcess -gt 4) { " ^
    "    Write-Host ('Port 9931 in use by PID ' + $proc.OwningProcess + ', killing...'); " ^
    "    taskkill /F /PID $($proc.OwningProcess) 2>$null; " ^
    "    Start-Sleep -Seconds 2; " ^
    "    $stillBusy = $true; " ^
    "  } elseif ($proc) { " ^
    "    Write-Host 'Port 9931 in TIME_WAIT, waiting...'; " ^
    "    Start-Sleep -Seconds 3; " ^
    "    $stillBusy = $true; " ^
    "  } " ^
    "  if ($attempt -ge $maxAttempts -and $stillBusy) { " ^
    "    Write-Host ('Failed to free port 9931 after ' + $maxAttempts + ' attempts.'); " ^
    "    exit 1; " ^
    "  } " ^
    "} while ($stillBusy)"

venv\Scripts\python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to launch the application.
    echo Check the error above.
    echo.
    pause
)
