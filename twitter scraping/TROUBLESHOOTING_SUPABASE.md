# Troubleshooting: Data Not Showing in Supabase

## Issue Found

The diagnostic script revealed that your `twitter` table is **missing the `language` column** (and possibly other columns). This is causing insert operations to fail silently.

## Quick Fix

### Step 1: Add Missing Columns

Go to your **Supabase SQL Editor** and run this script:

```sql
-- Add all missing columns
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS language TEXT;
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS retweets INTEGER DEFAULT 0;
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS likes INTEGER DEFAULT 0;
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ;
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ;
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS version_id TEXT;

-- Set defaults for existing records
UPDATE twitter SET retweets = 0 WHERE retweets IS NULL;
UPDATE twitter SET likes = 0 WHERE likes IS NULL;
UPDATE twitter SET language = 'unknown' WHERE language IS NULL;
```

Or use the complete script: `fix_supabase_table.sql`

### Step 2: Verify Table Structure

Your table should have these columns:

- `id` (BIGSERIAL PRIMARY KEY)
- `created_at` (TIMESTAMPTZ)
- `platform` (TEXT)
- `topic_hashtag` (TEXT)
- `engagement_score` (FLOAT)
- `sentiment_polarity` (FLOAT)
- `sentiment_label` (TEXT)
- `language` (TEXT) ← **MISSING**
- `posts` (INTEGER)
- `views` (INTEGER)
- `retweets` (INTEGER) ← **MISSING**
- `likes` (INTEGER) ← **MISSING**
- `metadata` (JSONB)
- `version_id` (TEXT) ← **MISSING**
- `first_seen` (TIMESTAMPTZ) ← **MISSING**
- `last_seen` (TIMESTAMPTZ) ← **MISSING**

### Step 3: Check RLS Policies

1. Go to **Authentication** → **Policies** in Supabase
2. Find the `twitter` table
3. Make sure there are policies allowing:
   - **SELECT** (for reading data)
   - **INSERT** (for adding new records)
   - **UPDATE** (for updating existing records)

If RLS is enabled but no policies exist, you can temporarily disable RLS:

```sql
ALTER TABLE twitter DISABLE ROW LEVEL SECURITY;
```

Or create a policy that allows all operations:

```sql
CREATE POLICY "Allow all operations" ON twitter
FOR ALL
USING (true)
WITH CHECK (true);
```

### Step 4: Test Again

Run the diagnostic script:

```bash
python check_supabase_connection.py
```

You should see:
- ✅ Table exists
- ✅ All required columns present
- ✅ Insert test successful

### Step 5: Run the Scraper

Once the table structure is fixed:

```bash
python t3_scraper.py
```

You should see output like:
```
SUCCESS: X new records inserted, Y existing records updated!
```

## Common Issues

### Issue 1: Missing Columns
**Error**: `Could not find the 'language' column`
**Solution**: Run the migration script above

### Issue 2: RLS Blocking Inserts
**Error**: Insert succeeds but no data appears
**Solution**: Check RLS policies or temporarily disable RLS

### Issue 3: TEST_MODE Enabled
**Symptom**: Scraper runs but says "TEST MODE"
**Solution**: Check your `.env` file has correct `SUPABASE_URL` and `SUPABASE_KEY`

### Issue 4: Wrong Table Name
**Error**: `relation "twitter" does not exist`
**Solution**: Check your table is named `twitter` (lowercase) in Supabase

## Verify Data in Supabase

1. Go to **Table Editor** in Supabase dashboard
2. Select the `twitter` table
3. You should see your scraped trends with:
   - Hashtags
   - Engagement scores
   - Sentiment labels
   - Post counts
   - Retweets and likes

## Still Not Working?

Run the diagnostic script and share the output:

```bash
python check_supabase_connection.py
```

This will help identify the specific issue.

