# Cloudflare Tunnel Script
Write-Host "Starting Cloudflare tunnel..." -ForegroundColor Cyan
Write-Host "Make sure your dev server is running on http://localhost:5176" -ForegroundColor Yellow
Write-Host ""
Write-Host "The tunnel URL will appear below. Press Ctrl+C to stop the tunnel." -ForegroundColor Green
Write-Host ""

# Start the tunnel
cloudflared tunnel --url http://localhost:5176

