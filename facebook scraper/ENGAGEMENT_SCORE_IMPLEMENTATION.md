# Engagement Score - Current Implementation

## Overview

This document describes **exactly what is implemented** in the codebase for engagement score calculation. There are **three different implementations** across different scraper files.

---

## Implementation 1: `base.py` (Main/Facebook Scraper)

### Location
- **File**: `base.py`
- **Class**: `FacebookScraper`
- **Method**: `_calculate_engagement_score()`
- **Lines**: 2570-2604

### Implementation Details

```python
def _calculate_engagement_score(self, likes: int, comments: int, shares: int) -> float:
    """
    Calculate engagement score (1-10 scale).
    
    Args:
        likes: Number of likes
        comments: Number of comments
        shares: Number of shares
        
    Returns:
        float: Engagement score (1.0-10.0)
    """
```

### Formula

**Step 1: Weighted Sum**
```python
weighted = (likes * 1) + (comments * 4) + (shares * 8)
```

**Weights:**
- Likes: **1.0x**
- Comments: **4.0x**
- Shares: **8.0x**
- Views: **NOT USED**

**Step 2: Progressive Scaling (Piecewise Linear)**

```python
if weighted == 0:
    return 1.0

if weighted <= 20:
    score = 1.0 + (weighted / 20) * 1.5
    # Range: 1.0 to 2.5

elif weighted <= 100:
    score = 2.5 + ((weighted - 20) / 80) * 1.5
    # Range: 2.5 to 4.0

elif weighted <= 500:
    score = 4.0 + ((weighted - 100) / 400) * 2.0
    # Range: 4.0 to 6.0

elif weighted <= 2000:
    score = 6.0 + ((weighted - 500) / 1500) * 2.0
    # Range: 6.0 to 8.0

elif weighted <= 10000:
    score = 8.0 + ((weighted - 2000) / 8000) * 1.5
    # Range: 8.0 to 9.5

else:
    score = min(10.0, 9.5 + (math.log10(weighted) - 4) * 0.125)
    # Range: 9.5 to 10.0 (logarithmic for very high values)
```

**Step 3: Clamping**
```python
return round(max(1.0, min(10.0, score)), 2)
```

### Usage in Code

**Location 1: Finalizing hashtag data** (Line 2518)
```python
tag_data['engagement_score'] = self._calculate_engagement_score(
    int(tag_data['avg_likes']),      # Average likes per post
    int(tag_data['avg_comments']),   # Average comments per post
    int(tag_data['avg_shares'])      # Average shares per post
)
```

**Location 2: Demo/mock data** (Line 2960)
```python
'engagement_score': self._calculate_engagement_score(l, c, s)
```

### Input Data Source

Uses **average values** from aggregated hashtag data:
- `avg_likes`: Average likes per post for the hashtag
- `avg_comments`: Average comments per post
- `avg_shares`: Average shares per post

**Note**: Views are tracked in `TrendRecord` but **NOT used** in engagement score calculation.

### Edge Cases

- **Zero engagement**: Returns `1.0` (minimum score)
- **Exception handling**: Returns `1.0` on any error
- **Very high values**: Uses logarithmic scaling above 10,000 weighted score

---

## Implementation 2: `perfect_scraper.py`

### Location
- **File**: `perfect_scraper.py`
- **Class**: `PerfectFacebookScraper`
- **Method**: `calculate_engagement_score()`
- **Lines**: 518-550

### Implementation Details

**Nearly identical to `base.py`** with one bug:

### Formula

**Step 1: Weighted Sum**
```python
weighted = (likes * 1.0) + (comments * 4.0) + (shares * 8.0)
```

**Step 2: Progressive Scaling**

**BUG FOUND**: Lines 541-544 have incorrect threshold calculation:

```python
elif weighted <= 500:
    score = 4.0 + ((weighted - 500) / 400) * 2.0  # BUG: should be (weighted - 100)
```

This should be:
```python
elif weighted <= 500:
    score = 4.0 + ((weighted - 100) / 400) * 2.0
```

**Similarly for 2000 threshold:**
```python
elif weighted <= 2000:
    score = 6.0 + ((weighted - 500) / 1500) * 2.0  # This is correct
```

### Differences from `base.py`

- Uses `1.0`, `4.0`, `8.0` (floats) vs `1`, `4`, `8` (integers) - functionally same
- Same progressive scaling thresholds
- Same logarithmic scaling for very high values

### Usage

**Calculated per-post** (Line 694):
```python
engagement_score = self.calculate_engagement_score(likes, comments, shares)
```

**Then averaged** (Line 763):
```python
engagement_scores = tag_data['engagement_scores']
tag_data['engagement_score'] = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 1.0
```

**Difference**: This calculates score per post and averages, while `base.py` calculates score from averaged metrics.

---

## Implementation 3: `free_api_scraper.py` (Simplified)

### Location
- **File**: `free_api_scraper.py`
- **Class**: `FreeAPIFacebookScraper`
- **Lines**: 541-552

### Implementation Details

**Much simpler approach** - uses only average total engagement:

```python
# Calculate engagement score (1-10)
avg_eng = tag_data['avg_engagement']  # Total engagement / post_count

if avg_eng > 10000:
    engagement_score = 10.0
elif avg_eng > 5000:
    engagement_score = 8.0
elif avg_eng > 1000:
    engagement_score = 6.0
elif avg_eng > 100:
    engagement_score = 4.0
else:
    engagement_score = 2.0
```

### Characteristics

- **No weighting**: Doesn't distinguish likes vs comments vs shares
- **Simple thresholds**: 5-tier system based on average total engagement
- **No normalization**: Direct mapping to fixed scores
- **Less granular**: Only 5 possible scores (2.0, 4.0, 6.0, 8.0, 10.0)

### Limitations

- Doesn't account for engagement type quality
- Less precise scoring
- No smooth scaling

---

## Summary Comparison

| Feature | `base.py` | `perfect_scraper.py` | `free_api_scraper.py` |
|---------|-----------|----------------------|----------------------|
| **Input Metrics** | Likes, Comments, Shares | Likes, Comments, Shares | Total Engagement Only |
| **Weights Used** | ✅ Yes (1x, 4x, 8x) | ✅ Yes (1x, 4x, 8x) | ❌ No |
| **Scaling Method** | Progressive + Logarithmic | Progressive + Logarithmic | Simple Thresholds |
| **Score Range** | 1.0 - 10.0 | 1.0 - 10.0 | 2.0 - 10.0 (5 values) |
| **Granularity** | High (2 decimals) | High (2 decimals) | Low (5 fixed values) |
| **Calculation Level** | Average metrics | Per-post then average | Average metrics |
| **Views Included** | ❌ No | ❌ No | ❌ No |
| **Edge Case Handling** | ✅ Yes | ✅ Yes | ⚠️ Basic |

---

## Key Findings

### What IS Implemented

1. ✅ **Weighted engagement calculation** using:
   - Likes: 1x weight
   - Comments: 4x weight
   - Shares: 8x weight

2. ✅ **Progressive scaling** with piecewise linear functions:
   - 6 different ranges (0-20, 20-100, 100-500, 500-2000, 2000-10000, >10000)
   - Logarithmic scaling for very high values (>10000)

3. ✅ **Normalization to 1-10 scale**

4. ✅ **Edge case handling** (zero engagement, exceptions)

### What is NOT Implemented

1. ❌ **Views are NOT included** in engagement score calculation
   - Views are tracked in `TrendRecord` dataclass
   - But never passed to `_calculate_engagement_score()`
   - Never weighted or included in formula

2. ❌ **Platform-specific weights** - Same weights used for all platforms

3. ❌ **Adaptive weights** - Weights are hardcoded, not configurable

4. ❌ **Time decay** - Recent vs old engagement treated equally

5. ❌ **Rate-based calculation** - No engagement rate (engagement/impressions)

6. ❌ **Percentile-based scoring** - No relative ranking

### Views Tracking

Views ARE tracked in the data model:

```python
@dataclass
class TrendRecord:
    views: int = 0  # Views are stored
    ...
```

But views are:
- ✅ **Stored** in the data structure
- ✅ **Extracted** from posts (if available)
- ❌ **NOT used** in engagement score calculation
- ❌ **NOT weighted** or included in formula

---

## Example Calculations

### Example 1: Using `base.py` implementation

**Input:**
- Avg Likes: 500
- Avg Comments: 20
- Avg Shares: 5

**Calculation:**
```
Step 1: Weighted Sum
weighted = (500 × 1) + (20 × 4) + (5 × 8)
         = 500 + 80 + 40
         = 620

Step 2: Progressive Scaling
Since 620 is in range 500-2000:
score = 6.0 + ((620 - 500) / 1500) × 2.0
      = 6.0 + (120 / 1500) × 2.0
      = 6.0 + 0.08 × 2.0
      = 6.0 + 0.16
      = 6.16

Result: engagement_score = 6.16/10
```

### Example 2: Using `free_api_scraper.py` implementation

**Input:**
- Avg Engagement: 1500 (total engagement / post_count)

**Calculation:**
```
Since 1500 > 1000 and <= 5000:
engagement_score = 6.0

Result: engagement_score = 6.0/10
```

### Example 3: Zero Engagement

**Input:**
- Likes: 0
- Comments: 0
- Shares: 0

**Calculation:**
```
weighted = 0
score = 1.0 (minimum)

Result: engagement_score = 1.0/10
```

---

## Code Locations

### Engagement Score Calculation

| File | Method | Lines | Input |
|------|--------|-------|-------|
| `base.py` | `_calculate_engagement_score()` | 2570-2604 | likes, comments, shares |
| `perfect_scraper.py` | `calculate_engagement_score()` | 518-550 | likes, comments, shares |
| `free_api_scraper.py` | Inline calculation | 541-552 | avg_engagement |

### Where It's Called

| File | Location | Context |
|------|----------|---------|
| `base.py` | Line 2518 | Finalizing hashtag data (uses averages) |
| `base.py` | Line 2960 | Demo/mock data generation |
| `perfect_scraper.py` | Line 694 | Per-post calculation |
| `perfect_scraper.py` | Line 763 | Averaging post scores |
| `free_api_scraper.py` | Line 541 | Direct threshold mapping |

### Data Extraction

| File | Method | Lines | Extracts |
|------|--------|-------|----------|
| `base.py` | `_extract_engagement()` | 1947-2020 | likes, comments, shares, views (but views not used) |

---

## Recommendations

### If You Want to Add Views

To include views in the engagement score calculation, you would need to:

1. **Modify the method signature:**
   ```python
   def _calculate_engagement_score(self, likes: int, comments: int, shares: int, views: int = 0) -> float:
   ```

2. **Add views to weighted sum:**
   ```python
   weighted = (likes * 1) + (comments * 4) + (shares * 8) + (views * 0.1)
   ```

3. **Update all call sites** to pass views parameter

4. **Update `perfect_scraper.py`** similarly

### If You Want Platform-Specific Weights

Create a configuration dictionary:
```python
PLATFORM_WEIGHTS = {
    'Facebook': {'likes': 1.0, 'comments': 4.0, 'shares': 8.0, 'views': 0.1},
    'Instagram': {'likes': 1.0, 'comments': 5.0, 'shares': 7.0, 'views': 0.2},
    # etc.
}
```

---

## Conclusion

The current implementation:
- ✅ Uses weighted calculation (likes, comments, shares)
- ✅ Uses progressive scaling for normalization
- ✅ Handles edge cases
- ❌ Does NOT include views in calculation
- ❌ Does NOT use platform-specific weights
- ❌ Does NOT support configuration

Views are tracked in the data model but not used in the engagement score formula.

