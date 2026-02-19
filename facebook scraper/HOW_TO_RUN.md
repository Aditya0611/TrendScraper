# How to Run the Facebook Scraper

## 🚀 Quick Start Guide

### Option 1: Run Locally (Windows)

1. **Activate Virtual Environment** (if using one):
   ```bash
   venv\Scripts\activate
   ```

2. **Install Dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers**:
   ```bash
   playwright install firefox
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root with:
   ```env
   FACEBOOK_EMAIL=your_email@example.com
   FACEBOOK_PASSWORD=your_password
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_key
   ```

5. **Run the Scraper**:
   ```bash
   python automated_scraper.py
   ```

### Option 2: Run via GitHub Actions (Automatic)

The scraper will run automatically:

- **Every 3 hours** (scheduled)
- **Manually** - Go to Actions tab → Click "Run workflow"

**No setup needed** - GitHub Actions handles everything automatically!

---

## 📋 What the Scraper Does

The `automated_scraper.py` script will:

1. ✅ Load all 8 categories from `config/categories.json`:
   - technology
   - business
   - health
   - food
   - travel
   - fashion
   - entertainment
   - sports

2. ✅ Scrape top 10 hashtags for each category

3. ✅ Save results to `data/facebook_top10_*.json` files

4. ✅ Upload data to Supabase (if configured)

5. ✅ Generate logs in `logs/scraper.log`

---

## ⚙️ Configuration Options

You can customize the scraper using environment variables:

```env
# Required
FACEBOOK_EMAIL=your_email@example.com
FACEBOOK_PASSWORD=your_password
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# Optional
MAX_POSTS=100              # Max posts per category (default: 100)
USE_PROXIES=false          # Enable proxy rotation (default: false)
RATE_LIMIT=30              # Requests per minute (default: 30)
HEADLESS=true              # Run browser in headless mode (default: true)
```

---

## 📁 Output Files

After running, you'll find:

- **JSON files**: `data/facebook_top10_*.json` (one per category)
- **Logs**: `logs/scraper.log`
- **Supabase**: Data automatically uploaded to database

---

## 🔍 Monitor GitHub Actions

1. Go to: https://github.com/Aditya0611/facebook/actions
2. Click on the latest workflow run
3. View logs for each step
4. Download artifacts (scraped data) after completion

---

## ❓ Troubleshooting

### Browser Not Found
```bash
# Install Firefox browser for Playwright
playwright install firefox
```

### Login Failed
- Check your credentials in `.env` file
- Disable 2FA temporarily if enabled
- Run with `HEADLESS=false` to see what's happening

### Config File Not Found
- Ensure `config/categories.json` exists
- The script now tries multiple paths automatically

### No Results
- Check `logs/scraper.log` for errors
- Verify categories exist in `config/categories.json`
- Increase `MAX_POSTS` value

---

## 🎯 Quick Commands

```bash
# Run scraper locally
python automated_scraper.py

# Install dependencies
pip install -r requirements.txt

# Install browsers
playwright install firefox chromium

# Check logs
cat logs/scraper.log  # Linux/Mac
type logs\scraper.log  # Windows
```

---

**Ready to scrape! 🎉**

