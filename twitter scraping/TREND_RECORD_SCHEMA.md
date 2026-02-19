# TrendRecord Data Model

## Overview

The `TrendRecord` dataclass provides a structured, type-safe data model for trending hashtag records. This replaces raw dictionaries and ensures data consistency and integration across the application.

## Schema Definition

```python
@dataclass
class TrendRecord:
    platform: str = "Twitter"
    topic_hashtag: str = ""
    engagement_score: float = 0.0
    sentiment_polarity: float = 0.0
    sentiment_label: str = "Neutral"
    language: str = "unknown"
    posts: int = 0
    views: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    version_id: str = field(default_factory=lambda: SCRAPE_VERSION_ID)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
```

## Database Alignment

The `TrendRecord` structure aligns exactly with the Supabase `twitter` table schema:

| TrendRecord Field | Database Column | Type | Description |
|-------------------|----------------|------|-------------|
| `platform` | `platform` | TEXT | Social media platform (default: "Twitter") |
| `topic_hashtag` | `topic_hashtag` | TEXT | The trending hashtag (e.g., "#Ayodhya") |
| `engagement_score` | `engagement_score` | FLOAT | Score from 1-10 based on engagement metrics |
| `sentiment_polarity` | `sentiment_polarity` | FLOAT | Sentiment polarity (-1.0 to 1.0) |
| `sentiment_label` | `sentiment_label` | TEXT | Sentiment label: "Positive", "Negative", or "Neutral" |
| `language` | `language` | TEXT | ISO 639-1 language code (e.g., "en", "hi") |
| `posts` | `posts` | INTEGER | Number of posts/tweets |
| `views` | `views` | INTEGER | Number of views (default: 0 for Twitter) |
| `metadata` | `metadata` | JSONB | Additional metadata (twitter_link, post_content, raw_count) |
| `version_id` | `version_id` | TEXT | UUID for tracking scrape sessions |
| `first_seen` | `first_seen` | TIMESTAMPTZ | Timestamp when trend was first observed |
| `last_seen` | `last_seen` | TIMESTAMPTZ | Timestamp when trend was last observed (updated on each scrape) |

## Methods

### `to_dict() -> Dict[str, Any]`
Converts the TrendRecord to a dictionary for database insertion. Ensures proper type conversion (float, int, str).

### `from_raw_topic(...) -> TrendRecord`
Class method that creates a TrendRecord from a raw topic dictionary and processed analysis data.

**Parameters:**
- `topic`: Raw topic dictionary from scraping
- `engagement_score`: Calculated engagement score
- `sentiment_label`: Detected sentiment label
- `sentiment_polarity`: Calculated sentiment polarity
- `detected_language`: Detected language code
- `post_content`: Generated post content
- `posts_count`: Parsed post count
- `twitter_link`: Twitter search link
- `first_seen`: Optional datetime for when trend was first seen (preserved on updates)
- `last_seen`: Optional datetime for when trend was last seen (updated on each scrape)

### `from_db_record(db_record: Dict[str, Any]) -> TrendRecord`
Class method that creates a TrendRecord from an existing database record. Parses timestamps and preserves all fields.

### `validate() -> bool`
Validates the TrendRecord data integrity:
- Ensures `topic_hashtag` is not empty
- Validates `sentiment_polarity` is between -1.0 and 1.0
- Validates `engagement_score` is between 0.0 and 10.0
- Validates `sentiment_label` is one of: "Positive", "Negative", "Neutral"

## Usage Example

```python
# Create TrendRecord from raw topic data
trend_record = TrendRecord.from_raw_topic(
    topic={"topic": "#Ayodhya", "count": "38K"},
    engagement_score=6.0,
    sentiment_label="Positive",
    sentiment_polarity=0.569,
    detected_language="en",
    post_content="Exciting launch of Ayodhya!",
    posts_count=38000,
    twitter_link="https://twitter.com/search?q=%23Ayodhya"
)

# Validate before database insertion
if trend_record.validate():
    # Convert to dictionary for Supabase
    record_dict = trend_record.to_dict()
    supabase.table('twitter').insert(record_dict).execute()
```

## Benefits

1. **Type Safety**: Dataclass provides type hints and validation
2. **Data Consistency**: Ensures all records follow the same structure
3. **Integration**: Easy to integrate with APIs, databases, and other systems
4. **Validation**: Built-in validation prevents invalid data
5. **Maintainability**: Single source of truth for data structure
6. **IDE Support**: Better autocomplete and error detection

## Temporal Tracking

The `TrendRecord` now tracks temporal information:
- **first_seen**: Set when a trend is first observed, preserved on subsequent updates
- **last_seen**: Updated every time a trend is observed in a scrape
- **version_id**: Tracks which scrape session the data came from

### Upsert Logic

The system uses upsert (insert or update) logic:
1. **New Trend**: Both `first_seen` and `last_seen` are set to current timestamp
2. **Existing Trend**: `first_seen` is preserved, `last_seen` is updated to current timestamp

This allows tracking:
- How long a trend has been trending (first_seen)
- When it was last seen (last_seen)
- Which scrape session added/updated the record (version_id)

## Database Migration

If your database doesn't have `first_seen` and `last_seen` columns, run the migration script:

```sql
-- See database_migration.sql for the full migration script
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ;
ALTER TABLE twitter ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_twitter_hashtag ON twitter(platform, topic_hashtag);
```

## Migration Notes

All database operations now use `TrendRecord` instead of raw dictionaries:
- `insert_fresh_data_only()` - Uses TrendRecord with upsert logic
- `store_topics_in_supabase()` - Uses TrendRecord with upsert logic
- `get_existing_trend()` - Retrieves existing trends to preserve first_seen
- `upsert_trend_record()` - Handles insert/update with timestamp tracking
- All records are validated before database insertion

