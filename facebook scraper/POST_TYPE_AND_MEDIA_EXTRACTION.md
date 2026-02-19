# Post Type and Media Format Extraction

## Overview

The scraper now extracts post type and media format information from Facebook posts, enabling better content analysis and filtering.

## Features Added

### 1. Post Type Detection

The scraper automatically detects post types:
- **`text`**: Text-only posts
- **`image`**: Posts with single image
- **`album`**: Posts with multiple images (photo albums)
- **`video`**: Posts with video content
- **`link`**: Posts with external links
- **`mixed`**: Posts with both images and videos
- **`unknown`**: If detection fails (fallback)

### 2. Media Format Extraction

For each post, the scraper extracts:

#### Images
- Image URLs from `img` elements
- Background images from CSS
- Filters out profile pictures and icons
- Limits to 10 images per post

#### Videos
- Video URLs from `video` elements
- Video IDs from data attributes
- Facebook video links
- Limits to 5 videos per post

#### Links
- External links (non-Facebook)
- Link previews
- Limits to 5 links per post

### 3. Media Statistics

Aggregated statistics per hashtag:
- **Total images**: Count of all images across posts
- **Total videos**: Count of all videos across posts
- **Total links**: Count of all links across posts
- **Posts with images**: Number of posts containing images
- **Posts with videos**: Number of posts containing videos
- **Posts with links**: Number of posts containing links

### 4. Post Type Distribution

Tracks the distribution of post types per hashtag:
```python
'post_types': {
    'text': 15,
    'image': 8,
    'video': 3,
    'album': 2,
    'link': 1
}
```

## Data Structure

### Individual Post

Each post now includes:

```python
{
    'text': 'Post text content',
    'likes': 100,
    'comments': 10,
    'shares': 5,
    'engagement': 115,
    'sentiment': 'positive',
    'sentiment_score': 0.65,
    'subjectivity': 0.42,
    'is_estimated': False,
    
    # NEW FIELDS:
    'post_type': 'image',  # text, image, video, link, album, mixed, unknown
    'images': ['https://...', ...],  # List of image URLs
    'videos': ['https://...', ...],  # List of video URLs/IDs
    'links': ['https://...', ...],   # List of link URLs
    'has_images': True,              # Boolean flag
    'has_videos': False,             # Boolean flag
    'has_link': False,              # Boolean flag
    'media_count': 1                  # Total media items
}
```

### Hashtag Aggregation

Each hashtag now includes:

```python
{
    'hashtag': '#technology',
    'post_count': 25,
    'total_engagement': 5000,
    # ... other metrics ...
    
    # NEW FIELDS:
    'post_types': {
        'text': 10,
        'image': 8,
        'video': 5,
        'album': 2
    },
    'media_stats': {
        'total_images': 45,
        'total_videos': 8,
        'total_links': 12,
        'posts_with_images': 10,
        'posts_with_videos': 5,
        'posts_with_links': 8
    },
    'media_samples': {
        'images': ['url1', 'url2', 'url3'],  # Sample image URLs
        'videos': ['url1', 'url2'],          # Sample video URLs
        'links': ['url1', 'url2']            # Sample link URLs
    }
}
```

## Implementation Details

### Detection Methods

1. **DOM Element Inspection**: Checks for `<img>`, `<video>`, `<a>` elements
2. **CSS Background Images**: Extracts images from `background-image` styles
3. **Data Attributes**: Reads video IDs from `data-video-id` attributes
4. **HTML Pattern Matching**: Regex patterns for media URLs in HTML
5. **Link Analysis**: Filters external links from internal Facebook links

### Selectors Used

**Images:**
- `img[src*="scontent"]`
- `img[src*="fbcdn"]`
- `div[style*="background-image"]`
- `a[href*="/photo"] img`

**Videos:**
- `video[src]`
- `div[data-video-id]`
- `a[href*="/video"]`
- `div[aria-label*="video"]`

**Links:**
- `a[href*="http"]`
- `a[data-href]`
- `a[target="_blank"]`

### Filtering

- **Profile Pictures**: Filtered out (contains "profile" in URL)
- **Icons**: Filtered out (contains "icon" in URL)
- **Internal Links**: Only external links are extracted (non-Facebook URLs)
- **Duplicate URLs**: Deduplicated using sets

## Usage Examples

### Filter by Post Type

```python
# Get only image posts
image_posts = [p for p in posts if p.get('post_type') == 'image']

# Get video posts
video_posts = [p for p in posts if p.get('post_type') == 'video']

# Get posts with media
media_posts = [p for p in posts if p.get('media_count', 0) > 0]
```

### Access Media URLs

```python
for post in posts:
    post_type = post.get('post_type', 'text')
    
    if post.get('has_images'):
        images = post.get('images', [])
        print(f"Post has {len(images)} images")
        for img_url in images:
            print(f"  Image: {img_url}")
    
    if post.get('has_videos'):
        videos = post.get('videos', [])
        print(f"Post has {len(videos)} videos")
        for video_url in videos:
            print(f"  Video: {video_url}")
    
    if post.get('has_link'):
        links = post.get('links', [])
        print(f"Post has {len(links)} links")
```

### Hashtag Statistics

```python
# Get post type distribution for a hashtag
hashtag = results[0]
post_types = hashtag.get('post_types', {})
print(f"Post types: {post_types}")

# Get media statistics
media_stats = hashtag.get('media_stats', {})
print(f"Total images: {media_stats.get('total_images', 0)}")
print(f"Total videos: {media_stats.get('total_videos', 0)}")
print(f"Posts with images: {media_stats.get('posts_with_images', 0)}")

# Access sample media
samples = hashtag.get('media_samples', {})
print(f"Sample images: {samples.get('images', [])}")
```

## Storage

### JSON Files

Post type and media information is stored in the output JSON files:
- Individual post data includes `post_type` and media arrays
- Hashtag aggregations include `post_types`, `media_stats`, and `media_samples`

### Supabase Database

Media information is stored in the `raw_metadata` field of TrendRecord:
```json
{
  "metadata": {
    "post_types": {"image": 10, "video": 5, ...},
    "media_stats": {...},
    "media_samples": {...}
  }
}
```

## Benefits

1. **Content Analysis**: Understand what types of content perform best
2. **Media Tracking**: Track which hashtags have more visual content
3. **Filtering**: Filter posts by type (e.g., only video posts)
4. **Rich Media**: Access actual image/video URLs for further processing
5. **Trend Insights**: See if certain post types are trending more

## Example Output

```json
{
  "hashtag": "#technology",
  "post_count": 20,
  "post_types": {
    "text": 5,
    "image": 8,
    "video": 4,
    "album": 2,
    "link": 1
  },
  "media_stats": {
    "total_images": 25,
    "total_videos": 4,
    "total_links": 3,
    "posts_with_images": 10,
    "posts_with_videos": 4,
    "posts_with_links": 2
  },
  "media_samples": {
    "images": ["https://scontent.xx.fbcdn.net/...", ...],
    "videos": ["https://www.facebook.com/video/123", ...],
    "links": ["https://example.com/article", ...]
  }
}
```

## Notes

- Media extraction may take slightly longer due to additional DOM inspection
- Some media URLs may be lazy-loaded and not immediately available
- Facebook's dynamic structure means some media may be missed in edge cases
- Video URLs may be video IDs or links depending on Facebook's HTML structure

