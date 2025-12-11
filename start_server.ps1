#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the Medical Report Simplifier API Server
.DESCRIPTION
    Starts the FastAPI server and optionally opens the frontend in a browser
.EXAMPLE
    .\start_server.ps1
    .\start_server.ps1 -OpenBrowser
#>

param(
    [switch]$OpenBrowser = $false,
    [int]$Port = 8000
)

# Colors for output
$Header = @{ForegroundColor = "Cyan"; NoNewLine = $false }
$Success = @{ForegroundColor = "Green"; NoNewLine = $false }
$Error = @{ForegroundColor = "Red"; NoNewLine = $false }
$Warning = @{ForegroundColor = "Yellow"; NoNewLine = $false }
$Info = @{ForegroundColor = "White"; NoNewLine = $false }

Write-Host ""
Write-Host "========================================" @Header
Write-Host "  🏥 Medical Report Simplifier - Startup" @Header
Write-Host "========================================" @Header
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." @Info
$PythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonExe) {
    Write-Host "❌ Python not found in PATH" @Error
    Write-Host "Please install Python or add it to PATH" @Error
    Read-Host "Press Enter to exit"
    exit 1
}

$PythonVersion = python --version 2>&1
Write-Host "✅ $PythonVersion" @Success

# Check FastAPI
Write-Host "`nChecking FastAPI installation..." @Info
$FastAPICheck = python -c "import fastapi" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  FastAPI not installed, installing requirements..." @Warning
    Write-Host ""
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install requirements" @Error
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host "✅ FastAPI is installed" @Success

# Check Tesseract (optional)
Write-Host "`nChecking Tesseract OCR (optional)..." @Info
$TesseractCheck = tesseract --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tesseract OCR is available (image processing enabled)" @Success
} else {
    Write-Host "⚠️  Tesseract not found (image uploads will fail)" @Warning
    Write-Host "   → Text input will still work perfectly" @Info
    Write-Host "   → Install from: https://github.com/UB-Mannheim/tesseract/wiki" @Info
}

# Ready to start
Write-Host ""
Write-Host "========================================" @Header
Write-Host "Starting server..." @Header
Write-Host "========================================" @Header
Write-Host ""
Write-Host "🌐 API Endpoint:    http://localhost:$Port" @Success
Write-Host "📖 Swagger Docs:    http://localhost:$Port/docs" @Success
Write-Host "🖥️  Frontend:        file:///C:/MERN_project/PLUm/medical_report_api/frontend.html" @Success
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" @Warning
Write-Host ""

# Optional: Open browser
if ($OpenBrowser) {
    Write-Host "Opening frontend in browser..." @Info
    Start-Process "file:///C:/MERN_project/PLUm/medical_report_api/frontend.html"
    
    Write-Host "Opening Swagger docs in browser..." @Info
    Start-Process "http://localhost:$Port/docs"
}

# Start server
Write-Host "========================================`n" @Header
Write-Host "Current directory: $(Get-Location)" @Info
Push-Location (Split-Path -Parent $PSCommandPath)
Write-Host "Changed to: $(Get-Location)" @Info
Write-Host ""

python -m uvicorn app.main:app --reload --port $Port

Pop-Location
Write-Host "`n❌ Server stopped" @Error
Read-Host "Press Enter to exit"
