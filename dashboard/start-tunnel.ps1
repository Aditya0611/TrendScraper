Write-Host "Starting Cloudflare Tunnel..." -ForegroundColor Green
Write-Host "Make sure your dev server is running on http://localhost:5173" -ForegroundColor Yellow
Write-Host ""
cloudflared tunnel --url http://localhost:5173


