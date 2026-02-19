/**
 * Redis-like Cache Utility
 * Uses localStorage for persistence (can be replaced with Redis backend later)
 * Supports TTL (Time-To-Live) for automatic expiration
 */

const CACHE_PREFIX = 'trendscraper_cache_'
const DEFAULT_TTL = 5 * 60 * 1000 // 5 minutes in milliseconds

/**
 * Generate cache key from table name and optional parameters
 */
const getCacheKey = (table, params = {}) => {
  const paramString = Object.keys(params)
    .sort()
    .map(key => `${key}:${params[key]}`)
    .join('|')
  return `${CACHE_PREFIX}${table}${paramString ? `_${paramString}` : ''}`
}

/**
 * Check if cache entry is expired
 */
const isExpired = (cacheEntry) => {
  if (!cacheEntry || !cacheEntry.expiresAt) return true
  return Date.now() > cacheEntry.expiresAt
}

/**
 * Set data in cache with TTL
 * @param {string} key - Cache key
 * @param {any} data - Data to cache
 * @param {number} ttl - Time to live in milliseconds (default: 5 minutes)
 */
export const setCache = (key, data, ttl = DEFAULT_TTL) => {
  try {
    const cacheEntry = {
      data,
      timestamp: Date.now(),
      expiresAt: Date.now() + ttl,
    }
    localStorage.setItem(key, JSON.stringify(cacheEntry))
    console.log(`✅ Cached data for key: ${key.substring(CACHE_PREFIX.length)} (TTL: ${ttl / 1000}s)`)
  } catch (error) {
    console.warn('Failed to set cache:', error)
    // If localStorage is full, try to clear old entries
    if (error.name === 'QuotaExceededError') {
      clearExpiredCache()
      try {
        localStorage.setItem(key, JSON.stringify(cacheEntry))
      } catch (retryError) {
        console.error('Failed to set cache after cleanup:', retryError)
      }
    }
  }
}

/**
 * Get data from cache
 * @param {string} key - Cache key
 * @returns {any|null} - Cached data or null if not found/expired
 */
export const getCache = (key) => {
  try {
    const cached = localStorage.getItem(key)
    if (!cached) return null

    const cacheEntry = JSON.parse(cached)
    
    if (isExpired(cacheEntry)) {
      // Remove expired entry
      localStorage.removeItem(key)
      console.log(`⏰ Cache expired for key: ${key.substring(CACHE_PREFIX.length)}`)
      return null
    }

    console.log(`💾 Cache hit for key: ${key.substring(CACHE_PREFIX.length)}`)
    return cacheEntry.data
  } catch (error) {
    console.warn('Failed to get cache:', error)
    return null
  }
}

/**
 * Remove specific cache entry
 * @param {string} key - Cache key to remove
 */
export const removeCache = (key) => {
  try {
    localStorage.removeItem(key)
    console.log(`🗑️ Removed cache for key: ${key.substring(CACHE_PREFIX.length)}`)
  } catch (error) {
    console.warn('Failed to remove cache:', error)
  }
}

/**
 * Clear all expired cache entries
 */
export const clearExpiredCache = () => {
  try {
    const keys = Object.keys(localStorage)
    let cleared = 0
    
    keys.forEach(key => {
      if (key.startsWith(CACHE_PREFIX)) {
        const cached = localStorage.getItem(key)
        if (cached) {
          try {
            const cacheEntry = JSON.parse(cached)
            if (isExpired(cacheEntry)) {
              localStorage.removeItem(key)
              cleared++
            }
          } catch (e) {
            // Invalid cache entry, remove it
            localStorage.removeItem(key)
            cleared++
          }
        }
      }
    })
    
    if (cleared > 0) {
      console.log(`🧹 Cleared ${cleared} expired cache entries`)
    }
  } catch (error) {
    console.warn('Failed to clear expired cache:', error)
  }
}

/**
 * Clear all cache entries (for a specific table or all)
 * @param {string} table - Optional table name to clear cache for
 */
export const clearCache = (table = null) => {
  try {
    const keys = Object.keys(localStorage)
    let cleared = 0
    
    keys.forEach(key => {
      if (key.startsWith(CACHE_PREFIX)) {
        if (table === null || key.includes(table)) {
          localStorage.removeItem(key)
          cleared++
        }
      }
    })
    
    console.log(`🗑️ Cleared ${cleared} cache entries${table ? ` for table: ${table}` : ''}`)
  } catch (error) {
    console.warn('Failed to clear cache:', error)
  }
}

/**
 * Get cache statistics
 */
export const getCacheStats = () => {
  try {
    const keys = Object.keys(localStorage)
    const cacheKeys = keys.filter(key => key.startsWith(CACHE_PREFIX))
    const stats = {
      total: cacheKeys.length,
      expired: 0,
      active: 0,
      totalSize: 0,
    }
    
    cacheKeys.forEach(key => {
      const cached = localStorage.getItem(key)
      if (cached) {
        stats.totalSize += cached.length
        try {
          const cacheEntry = JSON.parse(cached)
          if (isExpired(cacheEntry)) {
            stats.expired++
          } else {
            stats.active++
          }
        } catch (e) {
          stats.expired++
        }
      }
    })
    
    return stats
  } catch (error) {
    console.warn('Failed to get cache stats:', error)
    return { total: 0, expired: 0, active: 0, totalSize: 0 }
  }
}

/**
 * Cache Supabase query result
 * @param {string} table - Table name
 * @param {object} params - Query parameters
 * @param {any} data - Data to cache
 * @param {number} ttl - Time to live in milliseconds
 */
export const cacheQuery = (table, params = {}, data, ttl = DEFAULT_TTL) => {
  const key = getCacheKey(table, params)
  setCache(key, data, ttl)
}

/**
 * Get cached Supabase query result
 * @param {string} table - Table name
 * @param {object} params - Query parameters
 * @returns {any|null} - Cached data or null
 */
export const getCachedQuery = (table, params = {}) => {
  const key = getCacheKey(table, params)
  return getCache(key)
}

/**
 * Invalidate cache for a specific table
 * @param {string} table - Table name
 */
export const invalidateTableCache = (table) => {
  clearCache(table)
}

// Clean up expired cache on load
if (typeof window !== 'undefined') {
  clearExpiredCache()
  // Set up periodic cleanup (every 10 minutes)
  setInterval(clearExpiredCache, 10 * 60 * 1000)
}

export default {
  setCache,
  getCache,
  removeCache,
  clearCache,
  clearExpiredCache,
  getCacheStats,
  cacheQuery,
  getCachedQuery,
  invalidateTableCache,
  getCacheKey,
}

