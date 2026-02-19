# Why Include JSON Files? 📄

## Required JSON Files

### 1. `config/categories.json` - **REQUIRED** ✅

**Why it's needed:**
- `base.py` line 360: **Hard requirement** - exits with error if not found
- `automated_scraper.py` line 28-31: Looks for it in multiple locations
- Contains category definitions and search keywords
- **The scraper will NOT work without it**

**What it contains:**
```json
{
  "technology": {
    "name": "Technology",
    "keywords": ["technology", "tech", "AI", "software", ...]
  },
  "business": {
    "name": "Business",
    "keywords": ["business", "entrepreneur", "startup", ...]
  },
  ...
}
```

**What happens without it:**
- `base.py` will exit with error: `"ERROR: Config file not found"`
- `automated_scraper.py` will fail: `"❌ No categories found"`
- **Scraper cannot run**

### 2. `config/industrial_config.json` - **OPTIONAL** ⚠️

**Why it's included:**
- Used by `industrial_scraper.py` for advanced settings
- Contains rate limiting, proxy, session configurations
- **Optional** - scraper works with defaults if missing
- Included for reference/completeness

**What it contains:**
```json
{
  "scraper": {
    "rate_limit_per_minute": 30,
    "max_concurrent": 1
  },
  "proxy": {
    "enabled": true,
    "health_check_interval": 300
  },
  ...
}
```

**What happens without it:**
- Scraper uses default settings
- Still works, just uses hardcoded defaults
- Less customizable

## Summary

| File | Required? | Why |
|------|-----------|-----|
| `config/categories.json` | ✅ **YES** | Scraper exits if missing - defines what to scrape |
| `config/industrial_config.json` | ⚠️ Optional | Used for advanced settings, defaults work if missing |

## Recommendation

**Keep both files:**
- `categories.json` - **MUST include** (scraper won't work without it)
- `industrial_config.json` - **Should include** (for full functionality)

**Alternative:** If you want to remove `industrial_config.json`, the scraper will still work but with default settings only.

