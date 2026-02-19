# Enhanced Sentiment Analysis Guide

This guide explains how to use the enhanced sentiment analysis features for ranking trends and brand safety filtering.

## Features

- ✅ **Multiple Backends**: TextBlob (simple, fast) and HuggingFace Transformers (advanced, accurate)
- ✅ **Brand Safety Filtering**: Filter out negative content automatically
- ✅ **Sentiment-Weighted Ranking**: Rank trends based on sentiment
- ✅ **Confidence Scores**: Get confidence levels for sentiment predictions

## Installation

### Basic Setup (TextBlob only - default)

TextBlob is already installed with the basic requirements:

```bash
pip install textblob
python -m textblob.download_corpora
```

### Advanced Setup (HuggingFace Transformers)

For better accuracy, install HuggingFace transformers:

```bash
pip install transformers torch
```

This enables advanced sentiment analysis using pre-trained models like:
- `cardiffnlp/twitter-roberta-base-sentiment-latest` (default)
- `distilbert-base-uncased-finetuned-sst-2-english`
- Or any HuggingFace sentiment model

## Usage

### Basic Sentiment Analysis

The scraper already analyzes sentiment automatically. Each post gets:
- `sentiment`: "positive", "negative", or "neutral"
- `sentiment_score`: Polarity from -1.0 (very negative) to +1.0 (very positive)
- `subjectivity`: How subjective the text is (0.0 to 1.0)

### Using Enhanced Analyzer

```python
from sentiment_analyzer import SentimentAnalyzer, SentimentMethod, get_analyzer

# Auto mode (tries HuggingFace, falls back to TextBlob)
analyzer = get_analyzer(SentimentMethod.AUTO)

# Analyze sentiment
sentiment, polarity, confidence = analyzer.analyze("I love this product!")
# Returns: ("positive", 0.85, 0.92)

# Force TextBlob only (faster)
textblob_analyzer = SentimentAnalyzer(method=SentimentMethod.TEXTBLOB)

# Force HuggingFace only (more accurate)
hf_analyzer = SentimentAnalyzer(method=SentimentMethod.HUGGINGFACE)
```

### Brand Safety Filtering

Filter out negative content automatically:

```python
from sentiment_analyzer import is_brand_safe

# Check if text is brand-safe
text = "This product is amazing!"
if is_brand_safe(text, min_sentiment=0.0):  # 0.0 = neutral or positive
    print("Safe to show")
else:
    print("Filter out negative content")

# In the scraper, filter posts by sentiment
from sentiment_analyzer import get_analyzer, SentimentMethod

analyzer = get_analyzer(SentimentMethod.AUTO)

# Filter items - only show positive trends
positive_items = analyzer.filter_by_sentiment(
    items=all_posts,
    sentiment_filter="positive",  # Only positive
    min_polarity=0.2  # At least slightly positive
)

# Brand-safe filtering (neutral or positive)
brand_safe_items = analyzer.filter_by_sentiment(
    items=all_posts,
    sentiment_filter=None,  # No specific filter
    min_polarity=0.0  # Neutral or better
)
```

### Sentiment-Weighted Ranking

Rank trends based on sentiment (positive trends ranked higher):

```python
from sentiment_analyzer import get_analyzer, SentimentMethod

analyzer = get_analyzer(SentimentMethod.AUTO)

# Rank items by sentiment (positive first)
ranked_items = analyzer.rank_by_sentiment(
    items=trends,
    prefer_positive=True  # Positive trends ranked higher
)

# Rank items by sentiment (negative first - for monitoring)
ranked_items = analyzer.rank_by_sentiment(
    items=trends,
    prefer_positive=False  # Negative trends ranked higher
)
```

## Integration with Scraper

### Enable Enhanced Sentiment in BaseScraper

The `BaseScraper` class supports enhanced sentiment analysis:

```python
from base import FacebookScraper

scraper = FacebookScraper(headless=True)

# Use enhanced sentiment analysis (HuggingFace if available)
sentiment, polarity, confidence = scraper.analyze_sentiment(
    text="Amazing product!",
    use_enhanced=True  # Enable HuggingFace if available
)

# Brand safety check
if scraper.is_brand_safe(text, min_sentiment=0.0):
    print("Brand-safe content")
```

### Filter Posts During Scraping

You can filter posts by sentiment in the scraping process:

```python
# After scraping posts
posts = scraper.scrape_category_hashtags("technology", max_posts=100)

# Filter to only brand-safe posts
from sentiment_analyzer import get_analyzer, SentimentMethod

analyzer = get_analyzer(SentimentMethod.AUTO)
brand_safe_posts = analyzer.filter_by_sentiment(
    items=posts,
    min_polarity=0.0  # Neutral or positive only
)

# Rank by sentiment
ranked_posts = analyzer.rank_by_sentiment(brand_safe_posts, prefer_positive=True)
```

## Sentiment in Trend Ranking

The scraper already uses sentiment in trend ranking calculations:

```python
# In the trending score calculation (already implemented)
# Sentiment contributes 8% to the final score
trending_score = (
    engagement_norm * 0.45 +      # Engagement (45%)
    time_norm * 0.25 +            # Recency (25%)
    velocity_norm * 0.15 +        # Growth velocity (15%)
    consistency_norm * 0.07 +     # Consistency (7%)
    sentiment_norm * 0.08 +       # Sentiment (8%)
)

# Sentiment weight multiplier
if sentiment_score > 0:
    sentiment_weight = 1.0 + (sentiment_score * 0.3)  # Boost positive
elif sentiment_score < 0:
    sentiment_weight = 1.0 + (sentiment_score * 0.2)  # Penalize negative
else:
    sentiment_weight = 1.0

base_score *= sentiment_weight  # Apply sentiment multiplier
```

## Use Cases

### 1. Brand Safety Filtering

Show only positive or neutral content:

```python
# Filter for brand-safe content
safe_trends = analyzer.filter_by_sentiment(
    items=trends,
    min_polarity=0.0  # Neutral or positive
)
```

### 2. Positive Trends Only

Show only positive trending hashtags:

```python
# Filter for positive trends only
positive_trends = analyzer.filter_by_sentiment(
    items=trends,
    sentiment_filter="positive",
    min_polarity=0.2  # At least moderately positive
)
```

### 3. Sentiment-Weighted Ranking

Rank trends with positive sentiment higher:

```python
# Rank trends (positive first)
ranked_trends = analyzer.rank_by_sentiment(
    items=trends,
    prefer_positive=True
)
```

### 4. Monitor Negative Trends

Track negative sentiment for crisis monitoring:

```python
# Get negative trends for monitoring
negative_trends = analyzer.filter_by_sentiment(
    items=trends,
    sentiment_filter="negative"
)

# Rank by severity (most negative first)
ranked_negative = analyzer.rank_by_sentiment(
    items=negative_trends,
    prefer_positive=False  # Most negative first
)
```

## Configuration

### Choose Analysis Method

You can configure which sentiment analyzer to use:

```python
from sentiment_analyzer import SentimentAnalyzer, SentimentMethod

# TextBlob only (fast, simple)
analyzer = SentimentAnalyzer(method=SentimentMethod.TEXTBLOB)

# HuggingFace only (accurate, slower)
analyzer = SentimentAnalyzer(method=SentimentMethod.HUGGINGFACE)

# Auto (try HuggingFace, fallback to TextBlob)
analyzer = SentimentAnalyzer(method=SentimentMethod.AUTO)
```

### Custom HuggingFace Model

Use a different pre-trained model:

```python
from sentiment_analyzer import SentimentAnalyzer, SentimentMethod

# Use a different model
analyzer = SentimentAnalyzer(
    method=SentimentMethod.HUGGINGFACE,
    model_name='distilbert-base-uncased-finetuned-sst-2-english'
)
```

## Performance Comparison

| Method | Speed | Accuracy | Resource Usage |
|--------|-------|----------|----------------|
| TextBlob | ⚡ Fast | ✅ Good | 💚 Low |
| HuggingFace | 🐌 Slower | ✅✅ Excellent | 🔴 Higher |

**Recommendation**: Use TextBlob for real-time scraping (default), HuggingFace for batch analysis when accuracy is critical.

## Examples

### Example 1: Basic Usage

```python
from sentiment_analyzer import analyze_sentiment

sentiment, polarity, confidence = analyze_sentiment("This is amazing!")
print(f"Sentiment: {sentiment}, Score: {polarity:.2f}, Confidence: {confidence:.2f}")
# Output: Sentiment: positive, Score: 0.85, Confidence: 0.92
```

### Example 2: Brand Safety Check

```python
from sentiment_analyzer import is_brand_safe

posts = [
    "Great product! Highly recommend.",
    "This product is terrible.",
    "It's okay, nothing special."
]

safe_posts = [p for p in posts if is_brand_safe(p, min_sentiment=0.0)]
print(f"Brand-safe posts: {len(safe_posts)}/{len(posts)}")
# Output: Brand-safe posts: 2/3 (excludes negative)
```

### Example 3: Rank Trends by Sentiment

```python
from sentiment_analyzer import get_analyzer, SentimentMethod

analyzer = get_analyzer(SentimentMethod.AUTO)

trends = [
    {"hashtag": "#amazing", "posts": 100, "text": "This is amazing!"},
    {"hashtag": "#terrible", "posts": 50, "text": "This is terrible."},
    {"hashtag": "#okay", "posts": 75, "text": "It's okay."}
]

# Rank by sentiment (positive first)
ranked = analyzer.rank_by_sentiment(trends, prefer_positive=True)
for trend in ranked:
    print(f"{trend['hashtag']}: {trend['sentiment']} ({trend.get('sentiment_score', 0):.2f})")
```

## Troubleshooting

### HuggingFace Model Download Failed

If HuggingFace model download fails, it will automatically fall back to TextBlob:

```
WARNING: HuggingFace model loading failed. Falling back to TextBlob.
```

### Memory Issues with HuggingFace

If you encounter memory issues:
- Use a smaller model: `'distilbert-base-uncased-finetuned-sst-2-english'`
- Use CPU mode (already default in the code)
- Stick with TextBlob for real-time analysis

### TextBlob Not Available

If TextBlob is not available, install it:

```bash
pip install textblob
python -m textblob.download_corpora
```

## Summary

- ✅ **TextBlob**: Fast, simple sentiment analysis (default)
- ✅ **HuggingFace**: Advanced, accurate sentiment analysis (optional)
- ✅ **Brand Safety**: Filter negative content automatically
- ✅ **Sentiment Ranking**: Rank trends based on sentiment
- ✅ **Automatic Fallback**: Falls back to TextBlob if HuggingFace unavailable

The enhanced sentiment analysis enables features like:
- Brand safety filtering
- Positive trend discovery
- Crisis monitoring (negative sentiment tracking)
- Sentiment-weighted trend ranking

