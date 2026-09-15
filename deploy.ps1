# ==============================================================================
# DMC Operations Platform - Windows PowerShell Deployment Script
# ==============================================================================
$ErrorActionPreference = "Stop"

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🚀 DMC OPERATIONS PLATFORM: WINDOWS DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 1. Verify Python
try {
    $pyVer = python --version
    Write-Host "✓ Python runtime found: $pyVer" -ForegroundColor Green
} catch {
    Write-Error "Python 3 is required. Please install Python 3.10+ from python.org."
    exit 1
}

# 2. Check or create .env
if (-not (Test-Path ".env")) {
    Write-Host "ℹ️  No .env file found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# 3. Initialize SQLite database
Write-Host "ℹ️  Initializing SQLite database & contract tariffs..." -ForegroundColor Yellow
python db.py

# 4. Prompt for launch mode
Write-Host ""
Write-Host "Choose launch mode:" -ForegroundColor White
Write-Host "1) Start local server & open Dashboard in browser (Recommended)" -ForegroundColor Gray
Write-Host "2) Start with Docker Compose (DMC Platform + n8n workflows)" -ForegroundColor Gray
Write-Host "3) Run in background process" -ForegroundColor Gray
$choice = Read-Host "Enter option [1-3] (Default: 1)"
if (-not $choice) { $choice = "1" }

switch ($choice) {
    "1" {
        Write-Host "🚀 Starting DMC Operations Platform..." -ForegroundColor Green
        python server.py
    }
    "2" {
        if (Get-Command docker -ErrorAction SilentlyContinue) {
            Write-Host "🚀 Starting Docker Compose containers..." -ForegroundColor Green
            docker compose up -d --build
            Write-Host "✓ Containers launched!" -ForegroundColor Green
            Write-Host "👉 DMC Command Center: http://localhost:8080" -ForegroundColor Cyan
            Write-Host "👉 n8n Workflow Automation: http://localhost:5678" -ForegroundColor Cyan
        } else {
            Write-Warning "Docker is not installed or not in PATH. Starting with Python directly..."
            python server.py
        }
    }
    "3" {
        $job = Start-Process python -ArgumentList "server.py --no-browser" -PassThru
        Write-Host "✓ DMC server started in background (PID: $($job.Id))" -ForegroundColor Green
        Write-Host "👉 Access at: http://localhost:8080" -ForegroundColor Cyan
    }
    default {
        Write-Host "Invalid option. Exiting." -ForegroundColor Red
    }
}
