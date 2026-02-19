# Dynamic Language Detection Guide

## Overview

The scraper now automatically detects the language of each post using NLP-based language detection, replacing the hardcoded "en" (English) value. This enables better content analysis for international clients.

## Features

- ✅ **Automatic Language Detection**: Uses `langdetect` library (Google's language detection)
- ✅ **Confidence Scoring**: Returns confidence levels for language predictions
- ✅ **Multi-Language Support**: Detects 50+ languages (ISO 639-1 codes)
- ✅ **Language Distribution**: Tracks language distribution per hashtag
- ✅ **Primary Language**: Determines most common language per hashtag

## Installation

```bash
pip install langdetect
```

The library is already added to `requirements.txt` and will be installed automatically.

## How It Works

### Individual Post Language Detection

Each post is analyzed and assigned:
- **Language Code**: ISO 639-1 code (e.g., 'en', 'es', 'fr', 'de', 'hi', 'zh-cn')
- **Confidence**: Detection confidence (0.0 to 1.0)

### Hashtag Language Aggregation

For each hashtag, the scraper tracks:
- **Language Distribution**: Count of posts per language
- **Primary Language**: Most common language across posts
- **Average Confidence**: Average confidence across all posts

## Data Structure

### Individual Post

Each post now includes:

```python
{
    'text': 'Post text content',
    'language': 'es',              # Detected language code
    'language_confidence': 0.92,   # Detection confidence (0.0-1.0)
    # ... other fields
}
```

### Hashtag Aggregation

Each hashtag now includes:

```python
{
    'hashtag': '#technology',
    'post_count': 25,
    # ... other metrics ...
    
    # Language information:
    'language_distribution': {
        'en': 15,
        'es': 6,
        'fr': 3,
        'hi': 1
    },
    'primary_language': 'en',        # Most common language
    'avg_language_confidence': 0.85  # Average confidence
}
```

### TrendRecord

The TrendRecord now uses the detected primary language:

```python
{
    'platform': 'Facebook',
    'topic_hashtag': '#technology',
    'language': 'en',  # Primary language (detected, not hardcoded)
    # ... other fields
}
```

## Supported Languages

The `langdetect` library supports 50+ languages including:

- **European**: en, es, fr, de, it, pt, nl, ru, pl, cs, sv, da, no, fi
- **Asian**: zh-cn, zh-tw, ja, ko, hi, th, vi, id, ms
- **Middle Eastern**: ar, he, fa, tr
- **Other**: af, sq, be, bg, ca, hr, et, tl, gl, ka, el, gu, ht, iw, is, ga, kn, lv, lt, mk, mt, ne, ro, sr, sk, sl, sw, uk, ur, cy, yi

Full list: https://github.com/Mimino666/langdetect#supported-languages

## Usage Examples

### Access Language Information

```python
# Get post language
for post in posts:
    language = post.get('language', 'en')
    confidence = post.get('language_confidence', 0.0)
    print(f"Post language: {language} (confidence: {confidence:.2f})")
```

### Filter by Language

```python
# Filter posts by language
english_posts = [p for p in posts if p.get('language') == 'en']
spanish_posts = [p for p in posts if p.get('language') == 'es']
multilingual_posts = [p for p in posts if p.get('language') != 'en']
```

### Hashtag Language Distribution

```python
# Get language distribution for a hashtag
hashtag = results[0]
distribution = hashtag.get('language_distribution', {})
print(f"Language distribution: {distribution}")
# Output: {'en': 15, 'es': 6, 'fr': 3}

primary_lang = hashtag.get('primary_language', 'en')
print(f"Primary language: {primary_lang}")
# Output: Primary language: en

avg_confidence = hashtag.get('avg_language_confidence', 0.0)
print(f"Average confidence: {avg_confidence:.2f}")
```

### Multi-Language Analysis

```python
# Analyze multilingual hashtags
for hashtag in results:
    distribution = hashtag.get('language_distribution', {})
    primary = hashtag.get('primary_language', 'en')
    
    # Check if hashtag is multilingual (has posts in multiple languages)
    is_multilingual = len(distribution) > 1
    
    if is_multilingual:
        print(f"{hashtag['hashtag']}: Multilingual ({len(distribution)} languages)")
        for lang, count in distribution.items():
            percentage = (count / hashtag['post_count']) * 100
            print(f"  {lang}: {count} posts ({percentage:.1f}%)")
```

## Implementation Details

### Detection Method

The scraper uses `langdetect.detect()` which:
1. Analyzes character patterns, word frequencies, and n-grams
2. Compares against trained language models
3. Returns the most likely language with confidence score

### Confidence Threshold

- **Minimum Confidence**: 0.3 (configurable)
- **Fallback**: If confidence < 0.3, defaults to 'en'
- **Short Text**: Text < 10 characters defaults to 'en' with 0.0 confidence

### Performance

- **Fast**: ~1-5ms per post
- **Lightweight**: No GPU required
- **Offline**: Works without internet connection

### Error Handling

- **Fallback**: Defaults to 'en' if detection fails
- **Short Text**: Very short text (<10 chars) defaults to 'en'
- **Missing Library**: Falls back to 'en' if langdetect not installed

## Configuration

### Adjust Confidence Threshold

```python
# In base.py, detect_language method
language, confidence = scraper.detect_language(text, min_confidence=0.5)
# Higher threshold = more conservative (fewer detections)
```

### Disable Language Detection

If you want to disable language detection and use default 'en':

```python
# Comment out the language detection in post extraction
# Or modify detect_language to always return 'en'
```

## Use Cases

### 1. International Content Analysis

```python
# Analyze content by language
language_stats = {}
for post in posts:
    lang = post.get('language', 'en')
    language_stats[lang] = language_stats.get(lang, 0) + 1

print("Content by language:")
for lang, count in sorted(language_stats.items(), key=lambda x: x[1], reverse=True):
    print(f"  {lang}: {count} posts")
```

### 2. Multilingual Hashtag Discovery

```python
# Find hashtags popular across multiple languages
multilingual_hashtags = []
for hashtag in results:
    distribution = hashtag.get('language_distribution', {})
    if len(distribution) > 2:  # More than 2 languages
        multilingual_hashtags.append(hashtag)
        print(f"{hashtag['hashtag']}: {len(distribution)} languages")
```

### 3. Language-Specific Trend Filtering

```python
# Filter trends by primary language
english_trends = [h for h in results if h.get('primary_language') == 'en']
spanish_trends = [h for h in results if h.get('primary_language') == 'es']

# Get trends with high confidence
high_confidence_trends = [
    h for h in results 
    if h.get('avg_language_confidence', 0) > 0.8
]
```

### 4. Localization Insights

```python
# Understand content distribution for localization
for category in categories:
    category_results = scrape_category(category)
    
    languages = {}
    for result in category_results:
        primary = result.get('primary_language', 'en')
        languages[primary] = languages.get(primary, 0) + 1
    
    print(f"{category}: Top languages")
    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]:
        print(f"  {lang}: {count} hashtags")
```

## Accuracy Considerations

- **Long Text**: More accurate for longer posts (>50 characters)
- **Short Text**: Less accurate for very short posts (<20 characters)
- **Mixed Languages**: May detect primary language if text is mixed
- **Code/URLs**: URLs and code snippets may affect accuracy

## Example Output

### Post with Language Detection

```json
{
  "text": "¡Esta tecnología es increíble!",
  "language": "es",
  "language_confidence": 0.95,
  "likes": 100,
  "sentiment": "positive",
  "post_type": "text"
}
```

### Hashtag with Language Distribution

```json
{
  "hashtag": "#technology",
  "post_count": 20,
  "language_distribution": {
    "en": 12,
    "es": 5,
    "fr": 2,
    "de": 1
  },
  "primary_language": "en",
  "avg_language_confidence": 0.87,
  "post_types": {
    "text": 10,
    "image": 7,
    "video": 3
  }
}
```

## Troubleshooting

### Language Detection Returns 'en' for Non-English Text

1. **Check text length**: Very short text (<10 chars) defaults to 'en'
2. **Check confidence**: Low confidence may default to 'en' (threshold: 0.3)
3. **Mixed content**: Text with URLs/code may affect detection

### Low Confidence Scores

- Normal for short text
- Normal for mixed-language content
- Consider adjusting `min_confidence` threshold

### Installation Issues

If `langdetect` is not available:
- Install: `pip install langdetect`
- The scraper will fallback to 'en' automatically

## Benefits

1. **International Support**: Understand content in multiple languages
2. **Localization Insights**: Identify which languages are trending
3. **Content Filtering**: Filter posts by language
4. **Market Analysis**: Analyze trends by language/region
5. **Accurate Metadata**: Replace hardcoded 'en' with detected language

## Migration Notes

- **Backward Compatible**: If langdetect not installed, defaults to 'en'
- **No Breaking Changes**: Existing code will continue to work
- **Enhanced Data**: New language fields added to post and hashtag data

