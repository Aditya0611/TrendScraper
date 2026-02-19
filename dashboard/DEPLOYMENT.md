# Deploying TrendScraper Dashboard

This guide will help you host your dashboard at `https://trendscraper.in`.

## Pre-deployment Checklist

Before deploying, ensure you have your Supabase credentials ready. You will need:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

> [!IMPORTANT]
> These variables are required for the dashboard to fetch real-time data. Without them, the app will run in "Demo Mode" with fallback data.

---

## Option 1: Deploy to Vercel (Recommended)

Vercel is the easiest platform for React/Vite apps.

1.  **Install Vercel CLI**:
    ```powershell
    npm install -g vercel
    ```
2.  **Login**:
    ```powershell
    vercel login
    ```
3.  **Initialize & Deploy**:
    ```powershell
    vercel
    ```
    - Follow the prompts (use default settings).
    - **When asked about Environment Variables**, you can add them later in the dashboard or via CLI:
      ```powershell
      vercel env add VITE_SUPABASE_URL production
      vercel env add VITE_SUPABASE_ANON_KEY production
      ```
4.  **Production Deployment**:
    ```powershell
    vercel --prod
    ```
5.  **Connect Domain**:
    - Go to [Vercel Dashboard](https://vercel.com/dashboard).
    - Select your project → **Settings** → **Domains**.
    - Add `trendscraper.in`.
    - Vercel will provide the **A Record** (e.g., `76.76.21.21`) or **CNAME** (e.g., `cname.vercel-dns.com`) for your DNS settings.

---

## Option 2: Deploy to Netlify

1.  **Install Netlify CLI**:
    ```powershell
    npm install -g netlify-cli
    ```
2.  **Login**:
    ```powershell
    netlify login
    ```
3.  **Build & Deploy**:
    ```powershell
    npm run build
    netlify deploy --prod --dir=dist
    ```
4.  **Set Environment Variables**:
    - Go to [Netlify Dashboard](https://app.netlify.com).
    - **Site settings** → **Environment variables**.
    - Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
    - Re-deploy to apply changes.
5.  **Connect Domain**:
    - **Domain settings** → **Add custom domain**.
    - Add `trendscraper.in`.
    - Update your DNS records as instructed (typically a CNAME if using a subdomain or A record for apex).

---

## DNS Configuration for `trendscraper.in` (GoDaddy)

Since you purchased your domain from GoDaddy, follow these steps to connect it:

1.  **Log in to GoDaddy**: Go to your [My Products](https://dcc.godaddy.com/control/portfolio) page.
2.  **Manage DNS**: Click **DNS** next to your `trendscraper.in` domain.
3.  **Add/Edit Records**:
    - **For Vercel (Recommended)**:
      - Locate the **A** record with name `@`. Click Edit and change value to `76.76.21.21`.
      - Locate the **CNAME** record with name `www`. Click Edit and change value to `cname.vercel-dns.com`.
    - **For Netlify**:
      - Netlify will provide a specific subdomain (e.g., `your-site.netlify.app`).
      - Create a **CNAME** record for `@` (or use an A record if GoDaddy supports Alias) pointing to that value.
      - Update the `www` **CNAME** to point to your Netlify URL.

| Type | Name | Value (for Vercel) | TTL |
| :--- | :--- | :--- | :--- |
| **A** | `@` | `76.76.21.21` | 600 or Default |
| **CNAME** | `www` | `cname.vercel-dns.com` | 600 or Default |

> [!NOTE]
> **TTL (Time to Live)**: Setting this to 600 (10 minutes) helps changes propagate faster during setup.

4.  **Wait for Propagation**: GoDaddy updates usually take 5-30 minutes, but can take longer. You can check status at [DNSChecker.org](https://dnschecker.org/#A/trendscraper.in).

---

## Post-Deployment Verification

Once the site is live at `https://trendscraper.in`:

1.  **Check Data Load**: Ensure the stat cards and tables are showing real data (not demo data).
2.  **Check Console**: Open browser dev tools (F12) and check the **Console** tab. If you see "Supabase environment variables missing", ensure they are correctly set in your hosting provider's dashboard.
3.  **SSL/HTTPS**: Verify that the lock icon appears in the address bar. Most providers (Vercel/Netlify) handle this automatically.

---


