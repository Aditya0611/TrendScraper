# Start Dev Server and Cloudflare Tunnel
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TREN ENGINE - Cloudflare Tunnel Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if dev server is already running
$devServerRunning = Test-NetConnection -ComputerName localhost -Port 5176 -InformationLevel Quiet -WarningAction SilentlyContinue

if (-not $devServerRunning) {
    Write-Host "Starting development server..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm run dev" -WindowStyle Minimized
    Write-Host "Waiting for server to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
} else {
    Write-Host "Development server is already running on port 5176" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Cloudflare tunnel..." -ForegroundColor Cyan
Write-Host "Your tunnel URL will appear below:" -ForegroundColor Green
Write-Host ""

# Start the tunnel (this will block and show the URL)
cloudflared tunnel --url http://localhost:5176

