# Output Display Guide 📊

## What You'll See in Terminal

The scraper now displays detailed output during and after scraping:

### During Scraping

For each category, you'll see:

```
================================================================================
CATEGORY 1/8: TECHNOLOGY
================================================================================

Scraping top 10 hashtags for technology...
Search terms: technology, innovation, ai

✓ Category 'technology' completed: 10 hashtags found

Top Hashtags Found:
--------------------------------------------------------------------------------

1. #artificialintelligence
   Engagement Score: 8.45
   Trending Score: 92.3
   Posts: 45
   Total Engagement: 125,430
   Avg Engagement: 2,787.3
   Likes: 98,200 | Comments: 18,450 | Shares: 8,780
   Sentiment: positive (0.65)
   Language: en
   URL: https://www.facebook.com/hashtag/artificialintelligence

2. #innovation
   ...
```

### Final Summary

At the end, you'll see:

```
================================================================================
SCRAPING SESSION COMPLETE
================================================================================
Total Categories: 8
Successful: 6
Failed: 2
Total Duration: 65.6 minutes

================================================================================
SCRAPED RESULTS SUMMARY
================================================================================
Total Hashtags Scraped: 54

📊 TECHNOLOGY (10 hashtags):
--------------------------------------------------------------------------------
  1. #artificialintelligence | Engagement: 8.45 | Posts: 45
  2. #innovation | Engagement: 7.89 | Posts: 38
  3. #tech | Engagement: 7.23 | Posts: 42
  4. #startup | Engagement: 6.98 | Posts: 35
  5. #digital | Engagement: 6.75 | Posts: 29

📊 BUSINESS (8 hashtags):
--------------------------------------------------------------------------------
  ...

================================================================================
FINAL METRICS
================================================================================
  Total Requests: 97
  Successful: 97
  Failed: 0
  Success Rate: 100.00%
  Total Posts Scraped: 21
  Total Hashtags Found: 54
  Avg Response Time: 4.28s
```

## If You Don't See Output

### Issue 1: JSON Logging Interference

The scraper uses JSON logging which might mix with regular output. The actual scraped data will still appear, but might be mixed with JSON log lines.

**Solution:** Look for the sections marked with:
- `Top Hashtags Found:`
- `SCRAPED RESULTS SUMMARY`
- `FINAL METRICS`

### Issue 2: Output is Scrolled Away

If the terminal scrolls too fast, the output might be above the visible area.

**Solution:** 
- Scroll up in terminal to see earlier output
- Or redirect output to a file: `python automated_scraper.py > output.txt`

### Issue 3: No Results Scraped

If you see:
```
⚠ Category 'technology' completed but no results found
```

This means:
- The scraper ran successfully
- But no posts/hashtags were found (likely due to session issues or Facebook blocking)

**Solution:** Check the logs for login/session errors

## Saving Output to File

To save all output to a file:

```bash
# Save to file (overwrites)
python automated_scraper.py > scraper_output.txt 2>&1

# Or append to file
python automated_scraper.py >> scraper_output.txt 2>&1

# View in real-time while saving
python automated_scraper.py 2>&1 | tee scraper_output.txt
```

## Real-time Monitoring

You can watch the output in real-time:

```bash
# Linux/Mac
python automated_scraper.py 2>&1 | grep -E "(Top Hashtags|Category.*completed|hashtags found)"

# Windows PowerShell
python automated_scraper.py 2>&1 | Select-String -Pattern "Top Hashtags|Category.*completed|hashtags found"
```

## Understanding the Output

### Engagement Score (1-10)
- Higher = more engagement
- Calculated from likes, comments, shares

### Trending Score (0-100)
- Higher = more trending
- Based on recent activity and engagement

### Post Count
- Number of posts found for this hashtag

### Total Engagement
- Sum of all likes, comments, shares across posts

### Sentiment Score (-1 to +1)
- Positive: > 0.1
- Negative: < -0.1  
- Neutral: -0.1 to 0.1

## Example Output Format

```
1. #hashtagname
   Engagement Score: 8.45      ← Overall engagement quality
   Trending Score: 92.3        ← How trending right now
   Posts: 45                   ← Number of posts scraped
   Total Engagement: 125,430   ← Total likes+comments+shares
   Avg Engagement: 2,787.3     ← Average per post
   Likes: 98,200 | Comments: 18,450 | Shares: 8,780
   Sentiment: positive (0.65)  ← Overall sentiment
   Language: en                ← Primary language detected
   URL: https://www.facebook.com/hashtag/hashtagname
```

## Tips

1. **Look for the summary** - Most important info is at the end
2. **Check metrics** - Success rate tells you how well scraping went
3. **Category status** - Each category shows ✓ (success) or ⚠ (no results)
4. **JSON logs** - Mix with output but contain detailed debug info

## Next Steps

After seeing the output:
1. Results are also saved to JSON files in `data/` directory
2. Check `logs/scraper.log` for detailed JSON logs
3. Use the hashtag URLs to visit Facebook pages directly

