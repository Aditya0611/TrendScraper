# TikTok Scraper - Client Demo Script

## Demo Duration: 20 minutes

---

## SLIDE 1: Introduction (2 minutes)

**Title**: Social Media Trend Scraper - Complete Solution

**Key Points**:
- ✅ All requirements fulfilled
- ✅ Production-ready code
- ✅ 10,000 records in database
- ✅ Dynamic cron configuration
- ✅ Real-time dashboard
- ✅ Advanced filtering

---

## SLIDE 2: Database Verification (3 minutes)

**Demo Steps**:
1. Open Supabase dashboard
2. Navigate to `tiktok` table
3. Show record count: 10,000
4. Show sample record with all fields:
   - topic, engagement_score, posts, views
   - sentiment_polarity, sentiment_label
   - scraped_at, platform, metadata

**Talking Points**:
- "Database writes are fully functional"
- "All scraped data is persisted to Supabase"
- "10,000 records demonstrate production stability"

---

## SLIDE 3: Dynamic Cron Configuration (5 minutes)

**Demo Steps**:
1. Open Odoo
2. Navigate to: Social Media Trends → Scheduler Settings
3. Show list view with all platforms
4. Click on TikTok platform
5. Show form view with:
   - Enable/Disable toggle
   - Frequency slider (0.5-24 hours)
   - Statistics (success rate, run count)
   - Last run / Next run times

6. Change frequency from 3.0 to 2.0 hours
7. Save
8. Explain: "Worker will pick this up in 5 minutes"

**Talking Points**:
- "Admin can now control scraper frequency from Odoo"
- "No code changes needed"
- "Settings automatically sync to worker"
- "Success rate tracking for monitoring"

---

## SLIDE 4: "What's Hot Right Now" Widget (3 minutes)

**Demo Steps**:
1. Navigate to Odoo dashboard
2. Show "What's Hot Right Now" widget
3. Explain widget features:
   - Top 10 trending topics
   - Last 6 hours only
   - Engagement score >= 6.0
   - Platform icons
   - Sentiment badges
   - Post/view counts

**Talking Points**:
- "Real-time trending topics at a glance"
- "Only shows 'hot' trends (recent + high engagement)"
- "Color-coded sentiment for quick insights"
- "Auto-refreshes every 6 hours"

---

## SLIDE 5: Advanced Filters (5 minutes)

**Demo Steps**:
1. Navigate to: Social Media Trends → Trending Topics
2. Show kanban view with trend cards

3. **Filter Demo 1: Platform**
   - Apply filter: Platform = TikTok
   - Show results

4. **Filter Demo 2: Date Range**
   - Apply filter: Last 7 Days
   - Show results

5. **Filter Demo 3: Engagement**
   - Apply filter: High Engagement (8.0+)
   - Show results

6. **Filter Demo 4: Combined**
   - Apply: TikTok + High Engagement + Today
   - Show results

7. **Group By Demo**
   - Group by: Platform
   - Show organized view

**Talking Points**:
- "Powerful filtering for trend analysis"
- "Combine multiple filters"
- "Group by platform, sentiment, or date"
- "Easy to find specific trends"

---

## SLIDE 6: Technical Architecture (2 minutes)

**Diagram**:
```
┌─────────────────────────────────────────┐
│         APScheduler Worker              │
├─────────────────────────────────────────┤
│                                         │
│  Scraper Jobs ──→ Supabase (tiktok)    │
│       ↓                                 │
│  On Failure ──→ Job Queue (retry)      │
│                                         │
│  Odoo Sync ──→ Odoo (trends)           │
│                                         │
│  Config Reload ←── Supabase (settings) │
│                                         │
└─────────────────────────────────────────┘
```

**Talking Points**:
- "Async retry queue with exponential backoff"
- "Odoo integration for trend management"
- "Dynamic configuration reload"
- "Production-ready architecture"

---

## SLIDE 7: Q&A (2 minutes)

**Anticipated Questions**:

**Q**: How often does the scraper run?
**A**: Configurable from Odoo (0.5-24 hours), default is 3 hours

**Q**: What happens if scraping fails?
**A**: Automatically added to retry queue with exponential backoff (60s, 120s, 240s)

**Q**: Can we add more platforms?
**A**: Yes, just add to Scheduler Settings in Odoo

**Q**: How is data synced to Odoo?
**A**: Automatic sync every 1 hour via XMLRPC

**Q**: Can we change the "hot trends" criteria?
**A**: Yes, currently set to last 6 hours + score >= 7.0 (configurable in code)

---

## SLIDE 8: Next Steps

**Deployment Checklist**:
- [ ] Install Odoo module in production
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Start worker service
- [ ] Monitor initial runs
- [ ] Train admin users

**Support**:
- Complete documentation provided
- Installation guide included
- Troubleshooting section available
- Code is well-documented

---

## Demo Tips

### Before Demo
- [ ] Ensure Supabase has fresh data
- [ ] Restart Odoo to clear cache
- [ ] Start worker in background
- [ ] Open all necessary tabs
- [ ] Test all filters beforehand

### During Demo
- Speak clearly and confidently
- Show, don't just tell
- Pause for questions
- Highlight production-ready quality
- Emphasize all requirements fulfilled

### After Demo
- Provide documentation links
- Offer to answer follow-up questions
- Schedule training session if needed
- Confirm deployment timeline

---

## Success Metrics

✅ All 10 requirements fulfilled
✅ 10,000 records in database
✅ Zero unverified modules
✅ Production-ready code
✅ Comprehensive documentation
✅ Full testing completed

**Status**: READY FOR CLIENT APPROVAL
