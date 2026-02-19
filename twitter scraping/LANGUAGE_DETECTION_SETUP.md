# Dynamic Language Detection Setup

## Overview

The scraper now uses **dynamic multi-tool language detection** with automatic fallback. This provides better accuracy and reliability compared to using a single detection method.

## Supported Tools

1. **langdetect** (Primary)
   - Fast and lightweight
   - Good for most cases
   - Already installed and working

2. **fasttext** (Fallback)
   - Excellent for short text
   - Requires model download
   - Better accuracy for hashtags

3. **langid** (Fallback)
   - Good for multilingual content
   - Handles code-mixing well
   - Useful for Indian languages

## Installation

### Basic Setup (langdetect only)
```bash
pip install langdetect
```
This is already included and works out of the box.

### Full Setup (All tools)
```bash
pip install langdetect fasttext langid
```

### FastText Model Download

For FastText to work, you need to download the language identification model:

```bash
# Download the pre-trained model (176MB)
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

# Or using curl
curl -O https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

# Place it in the same directory as t3_scraper.py
```

**Note**: The system will gracefully fallback to other methods if the FastText model is not available.

## How It Works

### Auto Mode (Default)
```python
detect_language("#Ayodhya")  # Tries all available methods
```

**Strategy:**
1. Tries langdetect first (fastest)
2. Falls back to fasttext if langdetect fails
3. Falls back to langid if both fail
4. Uses consensus if multiple methods agree

### Consensus Mode
When multiple tools are available, the system can use consensus:
- If 2+ methods agree on the same language → Use that language
- If methods disagree → Use the first successful result (priority: langdetect > fasttext > langid)

### Specific Method
```python
detect_language("#Ayodhya", method="langdetect")  # Use only langdetect
detect_language("#Ayodhya", method="fasttext")     # Use only fasttext
detect_language("#Ayodhya", method="langid")      # Use only langid
```

## Detection Accuracy

| Method | Speed | Short Text | Multilingual | Accuracy |
|--------|-------|------------|--------------|----------|
| langdetect | ⚡ Fast | ⭐⭐ Good | ⭐⭐ Good | ⭐⭐⭐ Very Good |
| fasttext | 🐢 Slower | ⭐⭐⭐ Excellent | ⭐⭐ Good | ⭐⭐⭐ Excellent |
| langid | ⚡ Fast | ⭐⭐ Good | ⭐⭐⭐ Excellent | ⭐⭐⭐ Very Good |

## Example Output

```
DEBUG: Language detection for '#Ayodhya' -> en (method: langdetect)
DEBUG: Language detection for '#Ayodhya' -> en (consensus: 2/3 methods agree)
```

## Benefits

1. **Better Accuracy**: Multiple tools provide cross-validation
2. **Reliability**: Automatic fallback if one method fails
3. **Flexibility**: Can use specific method or auto-detect
4. **Graceful Degradation**: Works even if some tools aren't installed

## Troubleshooting

### "fasttext not available"
- Install: `pip install fasttext`
- Download model: `lid.176.bin` (see above)
- System will fallback to langdetect/langid

### "langid not available"
- Install: `pip install langid`
- System will fallback to langdetect/fasttext

### All methods return "unknown"
- Text might be too short (< 2 characters)
- Text might contain only numbers/symbols
- Try providing more context (post content)

## Performance

- **langdetect**: ~1ms per detection
- **fasttext**: ~10-50ms per detection (with model loaded)
- **langid**: ~2-5ms per detection
- **Consensus mode**: Sum of all methods used

For best performance, use langdetect alone. For best accuracy, use all three with consensus.

