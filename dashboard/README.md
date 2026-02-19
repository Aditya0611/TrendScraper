# Supabase Dashboard

A modern, responsive dashboard to display data from your Supabase tables.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure Supabase:**
   - Copy `.env.example` to `.env`
   - Get your Supabase URL and anon key from your [Supabase project settings](https://supabase.com/dashboard/project/rnrnbbxnmtajjxscawrc/settings/api)
   - Update the `.env` file with your credentials:
     ```
     VITE_SUPABASE_URL=https://rnrnbbxnmtajjxscawrc.supabase.co
     VITE_SUPABASE_ANON_KEY=your_actual_anon_key_here
     ```

3. **Update the table name:**
   - Open `src/App.jsx`
   - Find the line with `const defaultTable = 'your_table_name'`
   - Replace `'your_table_name'` with your actual table name

4. **Run the development server:**
   ```bash
   npm run dev
   ```

5. **Open your browser:**
   - Navigate to the URL shown in the terminal (usually `http://localhost:5173`)

## Features

- 🔄 Real-time data fetching from Supabase
- 💾 **Redis-like caching** - Automatic caching of Supabase queries with TTL (5 minutes default)
- 📊 Beautiful, responsive table display
- 🔍 Easy table switching via input field
- 🎨 Modern gradient UI design
- 📱 Mobile-friendly responsive layout

## Caching System

The dashboard includes a Redis-like caching system that:

- **Automatically caches** Supabase query results
- **TTL (Time-To-Live)**: Cache expires after 5 minutes (configurable)
- **Automatic cleanup**: Expired cache entries are automatically removed
- **Storage**: Uses browser localStorage (can be replaced with Redis backend)

### Cache Features

- ✅ Reduces database queries
- ✅ Faster page loads
- ✅ Automatic expiration
- ✅ Memory efficient (cleans up expired entries)

### Cache Management

The cache is managed automatically, but you can also:

```javascript
import { clearCache, invalidateTableCache, getCacheStats } from './cache'

// Clear all cache
clearCache()

// Clear cache for specific table
invalidateTableCache('facebook')

// Get cache statistics
const stats = getCacheStats()
console.log(stats) // { total: 5, expired: 1, active: 4, totalSize: 12345 }
```

### Upgrading to Redis

To use a real Redis backend instead of localStorage:

1. Create a backend API endpoint that handles Redis operations
2. Update `src/cache.js` to make HTTP requests to your backend
3. The cache interface remains the same, so no changes needed in `App.jsx`

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

