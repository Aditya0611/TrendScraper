@echo off
echo Starting Cloudflare Tunnel...
echo Make sure your dev server is running on http://localhost:5173
echo.
cloudflared tunnel --url http://localhost:5173


