# One-click setup and run (Windows PowerShell 5.1+)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

function Test-PythonCommand {
    param(
        [string]$Exe,
        [string[]]$PrefixArgs = @()
    )
    $pyCode = 'import sys; print(sys.version_info.major, sys.version_info.minor, sep=chr(46))'
    try {
        $v = (& $Exe @PrefixArgs -c $pyCode 2>$null | Select-Object -First 1)
        $v = "$v".Trim()
        if ($v -notmatch '^\d+\.\d+$') {
            return $null
        }
        $parts = $v.Split(".")
        if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 10) {
            return @{ Exe = $Exe; PrefixArgs = $PrefixArgs }
        }
    } catch {
        return $null
    }
    return $null
}

function Find-Python {
    $candidates = @(
        @{ Exe = "python"; PrefixArgs = @() },
        @{ Exe = "py"; PrefixArgs = @("-3") },
        @{ Exe = "py"; PrefixArgs = @() },
        @{ Exe = "python3"; PrefixArgs = @() }
    )
    foreach ($c in $candidates) {
        $ok = Test-PythonCommand -Exe $c.Exe -PrefixArgs $c.PrefixArgs
        if ($ok) {
            return $ok
        }
    }
    return $null
}

$pythonInfo = Find-Python
if (-not $pythonInfo) {
    Write-Host "Python 3.10+ is required. Install from https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "On Windows, enable 'Add python.exe to PATH' during install." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

$pythonExe = $pythonInfo.Exe
$pythonPrefix = $pythonInfo.PrefixArgs
Write-Host "Using: $pythonExe $($pythonPrefix -join ' ')" -ForegroundColor Cyan

if (-not (Test-Path "$ProjectRoot\venv\Scripts\python.exe")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $pythonExe @pythonPrefix -m venv "$ProjectRoot\venv"
}

$venvPython = "$ProjectRoot\venv\Scripts\python.exe"
$venvPip = "$ProjectRoot\venv\Scripts\pip.exe"
$venvUvicorn = "$ProjectRoot\venv\Scripts\uvicorn.exe"

Write-Host "Installing dependencies..." -ForegroundColor Yellow
& $venvPip install -r "$ProjectRoot\requirements.txt" -q

if (-not (Test-Path "$ProjectRoot\.env")) {
    Copy-Item "$ProjectRoot\.env.example" "$ProjectRoot\.env"
    Write-Host "Created .env (SQLite mode - no PostgreSQL needed)." -ForegroundColor Green
}

Write-Host "Preparing database..." -ForegroundColor Yellow
Set-Location "$ProjectRoot\backend"
& $venvPython -m db.init_db

function Stop-ListenerOnPort {
    param([int]$Port)
    try {
        $procIds = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
            Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($procId in $procIds) {
            if ($procId -and $procId -gt 0) {
                Write-Host "Stopping old server on port $Port (PID $procId)..." -ForegroundColor Yellow
                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            }
        }
        if ($procIds) { Start-Sleep -Seconds 1 }
    } catch {
        # ignore if Get-NetTCPConnection unavailable
    }
}

Stop-ListenerOnPort -Port 8000

Write-Host ""
Write-Host "Starting server at http://127.0.0.1:8000/" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

Start-Process "http://127.0.0.1:8000/"

& $venvUvicorn main:app --host 127.0.0.1 --port 8000 --reload
