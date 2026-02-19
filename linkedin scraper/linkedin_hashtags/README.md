# LinkedIn Hashtag Scraper (Scrapy Version)

This is a professional LinkedIn hashtag scraper built with Scrapy framework that can extract trending hashtags from LinkedIn feeds.

## Features

- 🔐 **Authentication Support**: Handles both cookie-based and credential-based LinkedIn authentication
- 🕷️ **Scrapy Framework**: Built on the robust Scrapy web scraping framework
- 🤖 **Selenium Integration**: Uses undetected-chromedriver for dynamic content handling
- 📊 **Multiple Export Formats**: Exports data to JSON, CSV, and generates detailed reports
- 🔄 **Fallback Methods**: Multiple hashtag extraction strategies for reliability
- 📝 **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Installation

1. **Install Dependencies**:
```bash
pip install scrapy scrapy-fake-useragent undetected-chromedriver python-dotenv
```

2. **Setup Environment Variables**:
Create a `.env` file in the project root:
```env
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

3. **Chrome Browser**: Ensure you have Chrome browser installed (the scraper will automatically manage ChromeDriver).

## Project Structure

```
linkedin_hashtags/
├── linkedin_hashtags/
│   ├── spiders/
│   │   └── linkedin_hashtags.py    # Main spider
│   ├── items.py                    # Data structure definitions
│   ├── pipelines.py                # Data processing pipelines
│   ├── settings.py                 # Scrapy configuration
│   └── middlewares.py              # Custom middlewares
├── output/                         # Generated output files
├── test_scraper.py                 # Test script
├── scrapy.cfg                      # Scrapy project config
└── README.md                       # This file
```

## Usage

### Method 1: Using Scrapy Command (Recommended)
```bash
cd linkedin_hashtags
scrapy crawl linkedin_hashtags
```

### Method 2: Using Test Script
```bash
cd linkedin_hashtags
python test_scraper.py
```

### Method 3: Custom Parameters
```bash
scrapy crawl linkedin_hashtags -s DOWNLOAD_DELAY=5 -s LOG_LEVEL=DEBUG
```

## Output Files

The scraper generates several output files in the `output/` directory:

- **JSON Export**: `linkedin_hashtags_YYYYMMDD_HHMMSS.json` - Structured data
- **CSV Export**: `linkedin_hashtags_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- **Report**: `hashtags_report_YYYYMMDD_HHMMSS.txt` - Human-readable summary
- **Debug HTML**: `debug_scrapy_feed_TIMESTAMP.html` - Raw LinkedIn feed HTML

## Configuration

Key settings in `settings.py`:

```python
# Scraping behavior
DOWNLOAD_DELAY = 3
CONCURRENT_REQUESTS = 1
AUTOTHROTTLE_ENABLED = True

# Export pipelines
ITEM_PIPELINES = {
    'linkedin_hashtags.pipelines.HashtagValidationPipeline': 200,
    'linkedin_hashtags.pipelines.JsonExportPipeline': 300,
    'linkedin_hashtags.pipelines.CsvExportPipeline': 400,
    'linkedin_hashtags.pipelines.ReportPipeline': 500,
}
```

## Data Fields

Each scraped hashtag contains:

- `name`: Lowercase hashtag name
- `original_case`: Original case hashtag name
- `url`: LinkedIn hashtag URL
- `mentions`: Number of mentions found
- `context`: Sample text context
- `sentiment_score`: Sentiment analysis score
- `sentiment_polarity`: Sentiment classification
- `scraped_at`: Timestamp of scraping
- `post_text`: Sample post text
- `author`: Post author information

## Authentication

The spider supports two authentication methods:

1. **Cookie Authentication** (Preferred):
   - Automatically saves session cookies after successful login
   - Faster subsequent runs without re-authentication

2. **Credential Authentication**:
   - Uses email/password from `.env` file
   - Handles security challenges and CAPTCHAs
   - Automatically saves cookies for future use

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - The spider automatically handles ChromeDriver management
   - If issues persist, try updating Chrome browser

2. **Authentication Failed**:
   - Verify credentials in `.env` file
   - Delete saved cookies: `rm linkedin_cookies.json`
   - Handle security challenges manually when prompted

3. **No Hashtags Found**:
   - LinkedIn may show suggested content instead of posts
   - Try running at different times when more posts are available
   - Check debug HTML files to verify content structure

### Debug Mode
Run with debug logging:
```bash
scrapy crawl linkedin_hashtags -L DEBUG
```

## Ethical Usage

- ⚠️ **Rate Limiting**: Built-in delays and throttling to respect LinkedIn's servers
- 🤝 **Terms of Service**: Ensure compliance with LinkedIn's Terms of Service
- 🔒 **Privacy**: Handle user data responsibly and securely
- 📊 **Data Use**: Use scraped data for legitimate research/analysis purposes only

## Example Output

```
🏷️  LinkedIn Hashtags Report - 2025-09-10 17:45:32
============================================================
📊 Total unique hashtags found: 15
📈 Total mentions across all hashtags: 47

🔥 Top 15 Trending Hashtags:
----------------------------------------
 1. #Bengaluru (5 mentions) 🚀
 2. #Upskilling (3 mentions) ⭐
 3. #ArtificialIntelligence (3 mentions) ⭐
 4. #Health (2 mentions) 📌
 5. #Wellness (2 mentions) 📌
```

## Contributing

Feel free to contribute improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational and research purposes. Please respect LinkedIn's Terms of Service and robots.txt guidelines.
