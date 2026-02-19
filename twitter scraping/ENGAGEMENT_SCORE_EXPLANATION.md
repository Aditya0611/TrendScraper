# Engagement Score Calculation

## Overview

The engagement score (1-10 scale) is now calculated based on **ACTUAL scraped engagement metrics**, not arbitrary keyword matching. This ensures the score reflects real user engagement and can be used for sorting, filtering, and highlighting high-impact trends.

## Scoring Formula

The engagement score is calculated using three factors:

### 1. Primary Factor: Tweet Count (Posts) - 0 to 7 points

**This is the MAIN engagement metric scraped from trends24.in**

Uses logarithmic scaling to handle the wide range of tweet counts:

```
Score = log10(posts + 1) × 1.75
```

**Examples:**
- **1K posts** → ~3.0 points
- **10K posts** → ~4.0 points  
- **100K posts** → ~5.0 points
- **1M posts** → ~6.0 points
- **10M posts** → ~7.0 points

If no tweet count is available, a minimal 0.5 points is added.

### 2. Secondary Factor: Trend Duration (Persistence) - 0 to 2 points

Longer-lasting trends indicate sustained engagement. Based on `first_seen` timestamp:

- **1-6 hours**: +0.5 points (recent trend)
- **6-24 hours**: +1.0 points (sustained engagement)
- **24+ hours**: +2.0 points (long-lasting trend)

This rewards trends that maintain engagement over time.

### 3. Tertiary Factor: Growth Rate (Momentum) - 0 to 1 point

If a trend is reappearing and growing, it shows momentum:

- Calculates growth rate: `(current_posts - previous_posts) / previous_posts`
- If growth rate > 50%: Adds up to 1.0 points
- Formula: `min(1.0, growth_rate × 0.5)`

This identifies trending topics that are gaining traction.

## Final Score Calculation

```
Final Score = Base (1.0) + Tweet Count Score (0-7) + Duration Bonus (0-2) + Growth Bonus (0-1)
Final Score = max(1.0, min(10.0, calculated_score))
```

## Score Ranges

| Score Range | Category | Description |
|-------------|----------|-------------|
| 8.0 - 10.0 | 🔥 Very High | Major trending topics with high engagement |
| 6.0 - 7.9 | ⚡ High | Strong engagement and visibility |
| 4.0 - 5.9 | 📈 Medium | Moderate engagement |
| 2.0 - 3.9 | 📊 Low | Lower engagement |
| 1.0 - 1.9 | 📉 Very Low | Minimal engagement |

## Why This Matters

### ✅ Sorting Trends
High engagement scores indicate topics that are actively engaging users. Sort by `engagement_score DESC` to see the most impactful trends first.

### ✅ Filtering Noise
Low engagement scores help filter out less relevant or spammy trends. Filter with `engagement_score >= 4.0` to focus on meaningful trends.

### ✅ Highlighting High-Impact Items
Use engagement scores to:
- Display top trends prominently
- Send alerts for high-engagement topics
- Prioritize content for analysis
- Identify viral trends early

## Data Sources

All metrics are based on **scraped data** from trends24.in:
- **Tweet Count**: Scraped from the trends page
- **Trend Duration**: Calculated from `first_seen` and `last_seen` timestamps
- **Growth Rate**: Calculated by comparing current and previous `posts` values

## Example Calculation

**Scenario**: A hashtag with 38K tweets that has been trending for 12 hours

1. **Tweet Count**: log10(38000 + 1) × 1.75 = ~5.3 points
2. **Duration**: 12 hours = +1.0 points (sustained)
3. **Growth**: Not applicable (first observation)
4. **Final Score**: 1.0 + 5.3 + 1.0 = **7.3** (High engagement)

## Benefits

1. **Data-Driven**: Based on actual engagement metrics, not assumptions
2. **Transparent**: Clear formula that can be verified
3. **Scalable**: Logarithmic scaling handles wide ranges
4. **Dynamic**: Updates based on trend persistence and growth
5. **Actionable**: Enables sorting, filtering, and prioritization

