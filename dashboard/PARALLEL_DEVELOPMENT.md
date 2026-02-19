# Parallel Development Guide

## Overview
You can deploy your dashboard to `trendscraper.in` while continuing to develop locally. Here's how:

## Workflow

### 1. **Deploy Production Version** (One-time setup)
Deploy your current dashboard to your domain so it's live for clients.

### 2. **Continue Local Development**
Keep working on improvements locally using `npm run dev`

### 3. **Deploy Updates**
When you're ready, deploy your improvements to production.

---

## Quick Deployment (Recommended: Vercel)

### Step 1: Build Production Version
```powershell
npm run build
```

### Step 2: Deploy to Vercel
```powershell
# If not already logged in
vercel login

# Deploy to production
vercel --prod
```

### Step 3: Add Your Domain
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings → Domains**
4. Add `trendscraper.in` and `www.trendscraper.in`
5. Follow Vercel's DNS instructions to update your domain records

---

## Parallel Development Workflow

### Daily Development
```powershell
# Work locally on improvements
npm run dev
# Dashboard runs on http://localhost:5176
```

### When Ready to Deploy Updates
```powershell
# 1. Build production version
npm run build

# 2. Deploy to production
vercel --prod

# Your changes are now live on trendscraper.in!
```

---

## Alternative: Automatic Deployments (Git-based)

### Option A: Vercel with GitHub
1. Push your code to GitHub
2. Connect GitHub repo to Vercel
3. Every push to `main` branch auto-deploys
4. Work on `dev` branch locally, merge when ready

### Option B: Cloudflare Pages with GitHub
1. Push to GitHub
2. Connect to Cloudflare Pages
3. Auto-deploys on every push

---

## Best Practices

### ✅ Do This:
- **Local Development**: Always test locally first with `npm run dev`
- **Preview Build**: Test production build locally with `npm run preview` before deploying
- **Version Control**: Use Git to track changes
- **Staging**: Consider a staging environment (e.g., `staging.trendscraper.in`)

### ❌ Avoid:
- Deploying untested code directly to production
- Making changes directly on the production site
- Skipping local testing

---

## Quick Commands Reference

```powershell
# Local Development
npm run dev              # Start dev server (localhost:5176)

# Production Build
npm run build           # Build for production
npm run preview         # Preview production build locally

# Deployment
vercel --prod           # Deploy to production (Vercel)
netlify deploy --prod  # Deploy to production (Netlify)

# Cloudflare Tunnel (for quick sharing)
cloudflared tunnel --url http://localhost:5176
```

---

## Troubleshooting

### Domain Not Working?
- Check DNS records are correctly configured
- Wait 24-48 hours for DNS propagation
- Verify domain is added in hosting platform

### Build Errors?
- Check `npm run build` works locally first
- Review error messages in deployment logs
- Ensure all dependencies are in `package.json`

### Changes Not Showing?
- Clear browser cache (Ctrl+Shift+R)
- Check deployment logs for build errors
- Verify you deployed the latest build

---

## Recommended Setup

1. **Deploy to Vercel** (easiest, best performance)
2. **Connect to GitHub** for automatic deployments
3. **Use branches**: 
   - `main` = production (auto-deploys)
   - `dev` = development branch
4. **Local testing** before every deployment

---

## Next Steps

1. Run `npm run build` to create production build
2. Deploy using `vercel --prod`
3. Add your domain in Vercel dashboard
4. Continue developing locally with `npm run dev`
5. Deploy updates when ready!

