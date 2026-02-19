import { useState, useEffect, useMemo, useCallback } from 'react'
import { supabase } from './supabaseClient'
import { cacheQuery, getCachedQuery, invalidateTableCache } from './cache'
import './App.css'
import './StatCards.css'
import './Views.css'

const PLATFORM_LOGOS = {
  facebook: 'https://cdn.simpleicons.org/facebook/1877F2',
  fb: 'https://cdn.simpleicons.org/facebook/1877F2',
  meta: 'https://cdn.simpleicons.org/facebook/1877F2',
  twitter: 'https://cdn.simpleicons.org/x/1DA1F2',
  x: 'https://cdn.simpleicons.org/x/1DA1F2',
  instagram: 'https://cdn.simpleicons.org/instagram/E4405F',
  ig: 'https://cdn.simpleicons.org/instagram/E4405F',
  tiktok: 'https://cdn.simpleicons.org/tiktok/000000',
  tt: 'https://cdn.simpleicons.org/tiktok/000000',
  youtube: 'https://cdn.simpleicons.org/youtube/FF0000',
  yt: 'https://cdn.simpleicons.org/youtube/FF0000',
  linkedin: 'https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png',
  li: 'https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png',
  linkedin_exact: 'https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png',
}

const DEFAULT_PLATFORM_LOGO =
  'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="%235865FF"/><path d="M22 24h20a4 4 0 014 4v16a4 4 0 01-4 4H22a4 4 0 01-4-4V28a4 4 0 014-4zm0-10h20a4 4 0 014 4v2H18v-2a4 4 0 014-4z" fill="white" opacity="0.9"/></svg>'

const PLATFORM_OPTIONS = [
  { key: 'facebook', label: 'Facebook', table: 'facebook', logo: PLATFORM_LOGOS.facebook },
  { key: 'twitter', label: 'Twitter', table: 'twitter', logo: PLATFORM_LOGOS.twitter },
  { key: 'instagram', label: 'Instagram', table: 'instagram', logo: PLATFORM_LOGOS.instagram },
  { key: 'tiktok', label: 'TikTok', table: 'tiktok', logo: PLATFORM_LOGOS.tiktok },
  { key: 'linkedin', label: 'LinkedIn', table: 'linkedin', logo: PLATFORM_LOGOS.linkedin },
  { key: 'youtube', label: 'YouTube', table: 'youtube', logo: PLATFORM_LOGOS.youtube },
]

const DEMO_DATA = {
  facebook: [
    {
      Topic: '#DoubleBlinkChallenge',
      Platform: 'Facebook',
      Posts: 1820,
      Views: 245000,
      Engagement_score: 18450,
      Trend_velocity: 6.3,
      Growth_pct: 38,
      status: 'breaking',
      created_at: new Date().toISOString(),
    },
    {
      Topic: 'Snack Reveal Switch',
      Platform: 'Facebook',
      Posts: 940,
      Views: 98000,
      Engagement_score: 7200,
      Trend_velocity: 4.1,
      Growth_pct: 21,
      status: 'surging',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '#FallFreshness',
      Platform: 'Facebook',
      Posts: 560,
      Views: 35000,
      Engagement_score: 2600,
      Trend_velocity: 1.2,
      Growth_pct: -8,
      status: 'fading',
      created_at: new Date().toISOString(),
    },
  ],
  linkedin: [
    {
      Topic: 'B2B AI Adoption 2025',
      Platform: 'LinkedIn',
      Posts: 740,
      Views: 185000,
      Engagement_score: 12600,
      Trend_velocity: 3.8,
      Growth_pct: 18,
      status: 'surging',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '#CareerGrowth',
      Platform: 'LinkedIn',
      Posts: 520,
      Views: 99000,
      Engagement_score: 7200,
      Trend_velocity: 2.1,
      Growth_pct: 9,
      status: 'steady',
      created_at: new Date().toISOString(),
    },
    {
      Topic: 'Product Marketing Playbooks',
      Platform: 'LinkedIn',
      Posts: 410,
      Views: 68000,
      Engagement_score: 5200,
      Trend_velocity: 1.4,
      Growth_pct: -4,
      status: 'fading',
      created_at: new Date().toISOString(),
    },
  ],
  twitter: [
    {
      Topic: '#AIinMedia',
      Platform: 'Twitter',
      Posts: 3100,
      Views: 420000,
      Engagement_score: 30500,
      Trend_velocity: 7.1,
      Growth_pct: 44,
      status: 'breaking',
      created_at: new Date().toISOString(),
    },
    {
      Topic: 'Threads vs X Debate',
      Platform: 'Twitter',
      Posts: 1980,
      Views: 210000,
      Engagement_score: 14600,
      Trend_velocity: 3.9,
      Growth_pct: 17,
      status: 'surging',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '#MotivationMonday',
      Platform: 'Twitter',
      Posts: 870,
      Views: 86000,
      Engagement_score: 5400,
      Trend_velocity: 0.9,
      Growth_pct: -5,
      status: 'fading',
      created_at: new Date().toISOString(),
    },
  ],
  instagram: [
    {
      Topic: '#SustainableDaily',
      Platform: 'Instagram',
      Posts: 2200,
      Views: 310000,
      Engagement_score: 28800,
      Trend_velocity: 5.2,
      Growth_pct: 29,
      status: 'breaking',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '#UrbanExplorer',
      Platform: 'Instagram',
      Posts: 1500,
      Views: 185000,
      Engagement_score: 15500,
      Trend_velocity: 3.3,
      Growth_pct: 14,
      status: 'surging',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '#MindfulMoment',
      Platform: 'Instagram',
      Posts: 630,
      Views: 52000,
      Engagement_score: 3700,
      Trend_velocity: 1.1,
      Growth_pct: -6,
      status: 'fading',
      created_at: new Date().toISOString(),
    },
  ],
  tiktok: [
    {
      Topic: '#warmupfortheholidays',
      Platform: 'TikTok',
      Posts: 2100,
      Views: 1800000,
      Engagement_score: 96000,
      Trend_velocity: 6.7,
      Growth_pct: 41,
      status: 'breaking',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '“Sorry I can’t hear you, I’m busy”',
      Platform: 'TikTok',
      Posts: 1780,
      Views: 1420000,
      Engagement_score: 77500,
      Trend_velocity: 4.6,
      Growth_pct: 23,
      status: 'surging',
      created_at: new Date().toISOString(),
    },
    {
      Topic: '#FallFreshness',
      Platform: 'TikTok',
      Posts: 960,
      Views: 420000,
      Engagement_score: 28400,
      Trend_velocity: 1.4,
      Growth_pct: -9,
      status: 'fading',
      created_at: new Date().toISOString(),
    },
  ],
  youtube: [
    {
      Topic: 'Tech Review 2025',
      Platform: 'YouTube',
      Posts: 450,
      Views: 1200000,
      Engagement_score: 85000,
      Trend_velocity: 8.2,
      Growth_pct: 55,
      status: 'breaking',
      created_at: new Date().toISOString(),
    },
    {
      Topic: 'Unboxing iPhone 16 Pro',
      Platform: 'YouTube',
      Posts: 320,
      Views: 850000,
      Engagement_score: 62000,
      Trend_velocity: 5.4,
      Growth_pct: 28,
      status: 'surging',
      created_at: new Date().toISOString(),
    },
  ],
}

const POWER_TOOL_ITEMS = [
  {
    key: 'sprout',
    name: 'Sprout Social',
    highlight: 'Publishing UX & Reports → Sprout Social (calendar ergonomics; templated exec packs).',
    description: 'Calendar ergonomics, team workflows, exec-ready reporting.',
    url: 'https://sproutsocial.com/',
  },
  {
    key: 'sprinklr',
    name: 'Sprinklr',
    highlight: 'Approval Hierarchies & Fleet Controls → Sprinklr (scale with compliance).',
    description: 'Enterprise governance, RBAC controls, audit trails.',
    url: 'https://www.sprinklr.com/',
  },
  {
    key: 'brandwatch',
    name: 'Brandwatch',
    highlight: 'Entity/Topic Sentiment & Alerts → Brandwatch (granular sentiment; anomaly detection).',
    description: 'Granular sentiment, entity alerts, research-grade listening.',
    url: 'https://www.brandwatch.com/',
  },
  {
    key: 'meltwater',
    name: 'Meltwater',
    description: 'News velocity, media monitoring, breakout story detection.',
    url: 'https://www.meltwater.com/',
  },
]


const getPlatformLogo = (platformName) => {
  if (!platformName) return DEFAULT_PLATFORM_LOGO
  const normalized = platformName.toLowerCase().trim().replace(/\s+/g, '')
  if (PLATFORM_LOGOS[normalized]) return PLATFORM_LOGOS[normalized]
  if (PLATFORM_LOGOS[platformName.toLowerCase().trim()]) return PLATFORM_LOGOS[platformName.toLowerCase().trim()]
  return DEFAULT_PLATFORM_LOGO
}

const TIME_RANGES = [
  { key: '24h', label: 'Last 24h', hours: 24 },
  { key: '7d', label: '7 Days', hours: 24 * 7 },
  { key: '30d', label: '30 Days', hours: 24 * 30 },
  { key: 'all', label: 'All Time', hours: null },
]

function App() {
  const [data, setData] = useState([])
  const [filteredData, setFilteredData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [hashtags, setHashtags] = useState([])
  const [hashtagsWithUrls, setHashtagsWithUrls] = useState({})
  const [showHashtagsPanel, setShowHashtagsPanel] = useState(true) // Always show by default
  const [viewMode, setViewMode] = useState('cards') // 'cards', 'table', or 'calendar'
  const [selectedPlatform, setSelectedPlatform] = useState(null)
  const [selectedTimeRange, setSelectedTimeRange] = useState(TIME_RANGES[1]) // default 7d
  const [showExecPackPanel, setShowExecPackPanel] = useState(false)
  const [execPackCopied, setExecPackCopied] = useState(false)
  const [showBrandwatchPanel, setShowBrandwatchPanel] = useState(false)
  const [alerts, setAlerts] = useState([])
  const [showMeltwaterPanel, setShowMeltwaterPanel] = useState(false)
  const [breakoutAlerts, setBreakoutAlerts] = useState([])


  // Brandwatch: Sentiment Analysis
  const sentimentAnalysis = useMemo(() => {
    if (!filteredData.length) return null

    const sentimentCounts = { positive: 0, negative: 0, neutral: 0 }
    const sentimentByPlatform = {}
    const sentimentByTopic = {}
    const entities = new Map()

    // Helper function to infer sentiment from metrics
    const inferSentiment = (row) => {
      // First, try to get explicit sentiment column (check multiple variations)
      const explicitSentiment = row.Sentiment_label || row.sentiment_label || row.Sentiment || row.sentiment ||
        row.sentiment_label || row.SentimentLabel || row.sentimentLabel
      if (explicitSentiment) {
        const sentimentStr = String(explicitSentiment).toLowerCase().trim()
        if (sentimentStr.includes('positive') || sentimentStr === 'pos' || sentimentStr === '+') return 'positive'
        if (sentimentStr.includes('negative') || sentimentStr === 'neg' || sentimentStr === '-') return 'negative'
        if (sentimentStr.includes('neutral') || sentimentStr === 'neu' || sentimentStr === '0') return 'neutral'
      }

      // Fallback: Infer sentiment from metrics (check multiple column name variations)
      const growthPct = Number(row.Growth_pct || row.growth_pct || row.GrowthPercent || row.growthPercent ||
        row.Growth || row.growth || 0)
      const velocity = Number(row.Trend_velocity || row.trend_velocity || row.Velocity || row.velocity ||
        row.trendVelocity || row.TrendVelocity || 0)
      const engagement = Number(row.Engagement_score || row.engagement_score || row.Engagement || row.engagement ||
        row.engagementScore || row.EngagementScore || 0)
      const status = String(row.Status || row.status || '').toLowerCase().trim()

      // Use status if available (check multiple variations)
      if (status.includes('breaking') || status.includes('surging') || status === 'hot' || status === 'trending') {
        return 'positive'
      }
      if (status.includes('fading') || status.includes('declining') || status === 'cold' || status === 'dying') {
        return 'negative'
      }

      // Infer from growth percentage (more nuanced thresholds)
      if (growthPct > 25) return 'positive'
      if (growthPct > 15) return 'positive' // Still positive but less strong
      if (growthPct < -15) return 'negative'
      if (growthPct < -5) return 'negative' // Still negative but less strong

      // Infer from velocity (adjusted thresholds)
      if (velocity > 6) return 'positive'
      if (velocity > 4) return 'positive' // Still positive
      if (velocity < 0.5) return 'negative'
      if (velocity < 1.5) return 'negative' // Still negative

      // Infer from engagement rate (relative to posts)
      const posts = Number(row.Posts || row.posts || row.Post || row.post || 0)
      if (posts > 0) {
        const engagementRate = engagement / posts
        if (engagementRate > 60) return 'positive'
        if (engagementRate > 30) return 'positive' // Still positive
        if (engagementRate < 3) return 'negative'
        if (engagementRate < 8) return 'negative' // Still negative
      }

      // Infer from views (if available)
      const views = Number(row.Views || row.views || row.View || row.view || 0)
      if (posts > 0 && views > 0) {
        const viewsPerPost = views / posts
        if (viewsPerPost > 500) return 'positive'
        if (viewsPerPost < 50) return 'negative'
      }

      return 'neutral'
    }

    filteredData.forEach(row => {
      const normalizedSentiment = inferSentiment(row)

      sentimentCounts[normalizedSentiment] = (sentimentCounts[normalizedSentiment] || 0) + 1

      // Normalize platform name (handle case variations and common aliases)
      const platformRaw = (row.Platform || row.platform || 'Unknown').toString().trim()
      let platform = platformRaw

      // Handle common platform name variations
      const platformLower = platformRaw.toLowerCase()
      if (platformLower === 'fb' || platformLower === 'facebook' || platformLower === 'meta') {
        platform = 'Facebook'
      } else if (platformLower === 'twitter' || platformLower === 'x' || platformLower === 'twtr') {
        platform = 'Twitter'
      } else if (platformLower === 'ig' || platformLower === 'instagram' || platformLower === 'insta') {
        platform = 'Instagram'
      } else if (platformLower === 'tt' || platformLower === 'tiktok' || platformLower === 'tik tok') {
        platform = 'TikTok'
      } else {
        // Capitalize first letter, lowercase rest
        platform = platformRaw.charAt(0).toUpperCase() + platformRaw.slice(1).toLowerCase()
      }

      if (!sentimentByPlatform[platform]) {
        sentimentByPlatform[platform] = { positive: 0, negative: 0, neutral: 0 }
      }
      sentimentByPlatform[platform][normalizedSentiment]++

      const topic = (row.Topic || row.topic || '').toString()
      if (topic) {
        if (!sentimentByTopic[topic]) {
          sentimentByTopic[topic] = { positive: 0, negative: 0, neutral: 0, total: 0 }
        }
        sentimentByTopic[topic][normalizedSentiment]++
        sentimentByTopic[topic].total++

        // Extract entities (hashtags, mentions, key terms)
        const hashtags = topic.match(/#[\w]+/g) || []
        hashtags.forEach(tag => {
          const entity = tag.substring(1).toLowerCase()
          if (!entities.has(entity)) {
            entities.set(entity, { count: 0, sentiment: { positive: 0, negative: 0, neutral: 0 } })
          }
          const entityData = entities.get(entity)
          entityData.count++
          entityData.sentiment[normalizedSentiment]++
        })
      }
    })

    const total = sentimentCounts.positive + sentimentCounts.negative + sentimentCounts.neutral
    const sentimentScore = total > 0
      ? ((sentimentCounts.positive - sentimentCounts.negative) / total) * 100
      : 0

    return {
      overall: sentimentCounts,
      score: sentimentScore,
      byPlatform: sentimentByPlatform,
      byTopic: Object.entries(sentimentByTopic)
        .map(([topic, data]) => ({
          topic,
          ...data,
          sentimentScore: data.total > 0
            ? ((data.positive - data.negative) / data.total) * 100
            : 0
        }))
        .sort((a, b) => b.total - a.total)
        .slice(0, 10),
      entities: Array.from(entities.entries())
        .map(([entity, data]) => ({
          entity,
          count: data.count,
          sentiment: data.sentiment,
          sentimentScore: data.count > 0
            ? ((data.sentiment.positive - data.sentiment.negative) / data.count) * 100
            : 0
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 20)
    }
  }, [filteredData])

  // Brandwatch: Anomaly Detection
  const anomalyDetection = useMemo(() => {
    if (!filteredData.length) return []

    // Work with smaller datasets too (minimum 2 for basic detection)
    const minDataPoints = Math.max(2, Math.min(3, filteredData.length))
    if (filteredData.length < minDataPoints) return []

    const anomalies = []
    const metrics = filteredData.map(row => ({
      topic: row.Topic || row.topic || row.name || '',
      platform: (row.Platform || row.platform || 'Unknown').toString(),
      posts: Number(row.Posts || row.posts || row.Post || row.post || 0),
      views: Number(row.Views || row.views || row.View || row.view || 0),
      engagement: Number(row.Engagement_score || row.engagement_score || row.Engagement || row.engagement || 0),
      velocity: Number(row.Trend_velocity || row.trend_velocity || row.Velocity || row.velocity || 0),
      growthPct: Number(row.Growth_pct || row.growth_pct || row.GrowthPercent || row.growthPercent || 0),
      timestamp: row.created_at || row.createdAt || row.timestamp || new Date().toISOString()
    }))

    // Calculate means and standard deviations
    const posts = metrics.map(m => m.posts).filter(v => v > 0)
    const views = metrics.map(m => m.views).filter(v => v > 0)
    const velocities = metrics.map(m => m.velocity).filter(v => v > 0)
    const growths = metrics.map(m => m.growthPct).filter(v => v !== 0)
    const engagements = metrics.map(m => m.engagement).filter(v => v > 0)

    const calculateStats = (values) => {
      if (values.length === 0) return { mean: 0, stdDev: 0, min: 0, max: 0 }
      if (values.length === 1) {
        return { mean: values[0], stdDev: values[0] * 0.1, min: values[0], max: values[0] }
      }
      const mean = values.reduce((a, b) => a + b, 0) / values.length
      const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length
      const stdDev = Math.sqrt(variance) || mean * 0.2 // Fallback to 20% of mean if stdDev is 0
      const min = Math.min(...values)
      const max = Math.max(...values)
      return { mean, stdDev, min, max }
    }

    const postsStats = calculateStats(posts)
    const viewsStats = calculateStats(views)
    const velocityStats = calculateStats(velocities)
    const growthStats = calculateStats(growths)
    const engagementStats = calculateStats(engagements)

    // Detect anomalies (values > 1.5 standard deviations from mean for smaller datasets)
    const threshold = filteredData.length < 5 ? 1.5 : 2 // Lower threshold for smaller datasets

    metrics.forEach((metric, index) => {

      if (metric.posts > 0 && postsStats.stdDev > 0) {
        const zScore = Math.abs((metric.posts - postsStats.mean) / postsStats.stdDev)
        if (zScore > threshold) {
          anomalies.push({
            id: `anomaly-${index}-posts`,
            type: 'spike',
            metric: 'posts',
            value: metric.posts,
            expected: postsStats.mean,
            deviation: zScore,
            topic: metric.topic,
            platform: metric.platform,
            severity: zScore > 3 ? 'critical' : 'high',
            timestamp: metric.timestamp
          })
        }
      }

      if (metric.views > 0 && viewsStats.stdDev > 0) {
        const zScore = Math.abs((metric.views - viewsStats.mean) / viewsStats.stdDev)
        if (zScore > threshold) {
          anomalies.push({
            id: `anomaly-${index}-views`,
            type: 'spike',
            metric: 'views',
            value: metric.views,
            expected: viewsStats.mean,
            deviation: zScore,
            topic: metric.topic,
            platform: metric.platform,
            severity: zScore > 3 ? 'critical' : 'high',
            timestamp: metric.timestamp
          })
        }
      }

      if (metric.velocity > 0 && velocityStats.stdDev > 0) {
        const zScore = Math.abs((metric.velocity - velocityStats.mean) / velocityStats.stdDev)
        if (zScore > threshold) {
          anomalies.push({
            id: `anomaly-${index}-velocity`,
            type: 'velocity_spike',
            metric: 'velocity',
            value: metric.velocity,
            expected: velocityStats.mean,
            deviation: zScore,
            topic: metric.topic,
            platform: metric.platform,
            severity: zScore > 3 ? 'critical' : 'high',
            timestamp: metric.timestamp
          })
        }
      }

      if (metric.growthPct !== 0 && growthStats.stdDev > 0) {
        const zScore = Math.abs((metric.growthPct - growthStats.mean) / growthStats.stdDev)
        if (zScore > threshold) {
          anomalies.push({
            id: `anomaly-${index}-growth`,
            type: metric.growthPct > 0 ? 'growth_spike' : 'decline',
            metric: 'growth',
            value: metric.growthPct,
            expected: growthStats.mean,
            deviation: zScore,
            topic: metric.topic,
            platform: metric.platform,
            severity: zScore > 3 ? 'critical' : 'high',
            timestamp: metric.timestamp
          })
        }
      }

      // Also detect engagement anomalies
      if (metric.engagement > 0 && engagementStats.stdDev > 0) {
        const zScore = Math.abs((metric.engagement - engagementStats.mean) / engagementStats.stdDev)
        if (zScore > threshold) {
          anomalies.push({
            id: `anomaly-${index}-engagement`,
            type: 'engagement_spike',
            metric: 'engagement',
            value: metric.engagement,
            expected: engagementStats.mean,
            deviation: zScore,
            topic: metric.topic,
            platform: metric.platform,
            severity: zScore > 3 ? 'critical' : 'high',
            timestamp: metric.timestamp
          })
        }
      }
    })

    return anomalies.sort((a, b) => b.deviation - a.deviation)
  }, [filteredData])

  // Meltwater: News Velocity Intelligence & Story Breakout Detection
  const newsVelocityAnalysis = useMemo(() => {
    // Always return a structure, even if no data
    if (!filteredData || filteredData.length === 0) {
      return {
        totalStories: 0,
        breakoutCount: 0,
        storyLifecycle: { emerging: 0, breaking: 0, peak: 0, declining: 0 },
        velocityByPlatform: {},
        topStories: [],
        breakoutStories: [],
        avgVelocityScore: 0
      }
    }

    const velocityByPlatform = {}
    const breakoutStories = []

    // Process each row as a story (since each row represents a topic/platform combination)
    const storyMetrics = filteredData
      .map((row, index) => {
        if (!row) return null

        // Extract topic - be very lenient, accept any non-empty value
        const topic = (row.Topic || row.topic || row.name || row.title || row.text || row.content || row.hashtag || `Story ${index + 1}`).toString().trim()
        // Only filter out if topic is truly empty or just whitespace
        if (!topic || topic.length === 0) return null

        // Normalize platform name (handle case variations and common aliases)
        let platformRaw = (row.Platform || row.platform || 'Unknown').toString().trim()
        const platformLower = platformRaw.toLowerCase()
        let platform = platformRaw
        if (platformLower === 'fb' || platformLower === 'facebook' || platformLower === 'meta') {
          platform = 'Facebook'
        } else if (platformLower === 'twitter' || platformLower === 'x' || platformLower === 'twtr') {
          platform = 'Twitter'
        } else if (platformLower === 'ig' || platformLower === 'instagram' || platformLower === 'insta') {
          platform = 'Instagram'
        } else if (platformLower === 'tt' || platformLower === 'tiktok' || platformLower === 'tik tok') {
          platform = 'TikTok'
        } else if (platformRaw && platformRaw !== 'Unknown') {
          platform = platformRaw.charAt(0).toUpperCase() + platformRaw.slice(1).toLowerCase()
        } else {
          platform = 'Unknown'
        }

        // Extract numeric values with robust parsing - check many column name variations
        // Try all possible column name variations
        const posts = Math.max(0, Number(
          row.Posts || row.posts || row.Post || row.post ||
          row.Posts_count || row.posts_count || row.post_count ||
          row.num_posts || row.numPosts || row.NumPosts ||
          0
        ) || 0)

        const views = Math.max(0, Number(
          row.Views || row.views || row.View || row.view ||
          row.Views_count || row.views_count || row.view_count ||
          row.num_views || row.numViews || row.NumViews ||
          row.impressions || row.Impressions ||
          0
        ) || 0)

        const engagement = Math.max(0, Number(
          row.Engagement_score || row.engagement_score || row.Engagement || row.engagement ||
          row.EngagementScore || row.engagementScore || row.engagement_score ||
          row.engagement_rate || row.engagementRate || row.EngagementRate ||
          row.total_engagement || row.totalEngagement || row.TotalEngagement ||
          0
        ) || 0)

        const velocity = Number(
          row.Trend_velocity || row.trend_velocity || row.Velocity || row.velocity ||
          row.trendVelocity || row.TrendVelocity || row.trend_velocity ||
          row.velocity_score || row.velocityScore || row.VelocityScore ||
          row.momentum || row.Momentum ||
          0
        ) || 0

        const growthPct = Number(
          row.Growth_pct || row.growth_pct || row.GrowthPercent || row.growthPercent ||
          row.Growth || row.growth || row.growth_rate || row.growthRate ||
          row.GrowthRate || row.percent_change || row.percentChange ||
          row.change_pct || row.changePct || row.ChangePct ||
          0
        ) || 0

        const status = (
          row.Status || row.status || row.state || row.State ||
          row.trend_status || row.trendStatus || row.TrendStatus ||
          ''
        ).toString().toLowerCase().trim()

        const timestamp = (
          row.created_at || row.createdAt || row.timestamp || row.Timestamp ||
          row.date || row.Date || row.created || row.Created ||
          new Date().toISOString()
        )

        // If all values are still 0, try to find numeric columns by scanning all fields
        if (posts === 0 && views === 0 && engagement === 0 && velocity === 0 && growthPct === 0 && index < 3) {
          console.log('News Velocity - All values are 0, scanning row for numeric fields:', {
            index,
            topic,
            platform,
            allColumns: Object.keys(row),
            sampleValues: Object.entries(row).slice(0, 10).map(([key, val]) => ({
              key,
              value: val,
              type: typeof val,
              isNumeric: !isNaN(Number(val)) && val !== null && val !== ''
            }))
          })

          // Try to find numeric values in any column that might be our metrics
          Object.entries(row).forEach(([key, val]) => {
            const numVal = Number(val)
            if (!isNaN(numVal) && numVal > 0 && val !== null && val !== '') {
              const keyLower = key.toLowerCase()
              // Try to match column names to our metrics
              if ((keyLower.includes('post') || keyLower.includes('count')) && posts === 0) {
                console.log(`Found potential Posts value in column "${key}":`, numVal)
              }
              if ((keyLower.includes('view') || keyLower.includes('impression')) && views === 0) {
                console.log(`Found potential Views value in column "${key}":`, numVal)
              }
              if (keyLower.includes('engagement') && engagement === 0) {
                console.log(`Found potential Engagement value in column "${key}":`, numVal)
              }
              if ((keyLower.includes('velocity') || keyLower.includes('momentum') || keyLower.includes('trend')) && velocity === 0) {
                console.log(`Found potential Velocity value in column "${key}":`, numVal)
              }
              if ((keyLower.includes('growth') || keyLower.includes('change') || keyLower.includes('percent')) && growthPct === 0) {
                console.log(`Found potential Growth value in column "${key}":`, numVal)
              }
            }
          })
        }

        // Calculate velocity score (composite metric) - ensure no NaN
        const velocityScore = Math.max(0, (
          (isNaN(velocity) ? 0 : Math.abs(velocity) * 0.4) +
          (isNaN(growthPct) ? 0 : Math.abs(growthPct) * 0.3) +
          (isNaN(engagement) ? 0 : Math.min(engagement / 1000, 100) * 0.2) +
          (isNaN(views) ? 0 : Math.min(views / 10000, 100) * 0.1)
        ))

        // Determine story lifecycle stage (improved logic)
        let lifecycle = 'neutral'
        if (status.includes('breaking') || (velocity >= 6 && growthPct >= 30)) {
          lifecycle = 'breaking'
        } else if (velocity >= 4 && growthPct >= 15) {
          lifecycle = 'peak'
        } else if (velocity <= 1 && growthPct < 0) {
          lifecycle = 'declining'
        } else if (velocity > 0 || growthPct > 0) {
          lifecycle = 'emerging'
        } else {
          lifecycle = 'declining'
        }

        // Detect breakout based on high velocity/growth thresholds
        const isBreakout = (velocity >= 6 && growthPct >= 25) ||
          (velocity >= 5 && growthPct >= 30) ||
          (velocity >= 7) ||
          (growthPct >= 40) ||
          (posts >= 1000 && views >= 100000) ||
          (lifecycle === 'breaking')

        const story = {
          key: `${topic}::${platform}::${index}`,
          topic,
          platform,
          avgPosts: posts,
          avgViews: views,
          avgEngagement: engagement,
          avgVelocity: velocity,
          avgGrowth: growthPct,
          maxVelocity: velocity,
          maxGrowth: growthPct,
          maxPosts: posts,
          maxViews: views,
          velocityTrend: 0,
          growthTrend: 0,
          velocityScore,
          lifecycle,
          dataPoints: 1,
          firstSeen: timestamp,
          lastSeen: timestamp
        }

        if (isBreakout) {
          breakoutStories.push({
            id: `breakout-${index}-${topic}-${platform}`,
            topic,
            platform,
            velocityScore,
            maxVelocity: velocity,
            maxGrowth: growthPct,
            maxPosts: posts,
            maxViews: views,
            lifecycle,
            velocityTrend: 0,
            growthTrend: 0,
            timestamp,
            severity: velocity >= 8 || growthPct >= 50 ? 'critical' : 'high'
          })
        }

        return story
      })
      .filter(story => {
        // Keep all stories that have a topic, even if metrics are 0
        return story !== null && story.topic && story.topic.length > 0
      })

    // If no valid stories, log and return empty structure
    if (storyMetrics.length === 0) {
      console.warn('News Velocity: No valid stories found after processing', {
        filteredDataLength: filteredData.length,
        sampleRow: filteredData[0]
      })
      return {
        totalStories: 0,
        breakoutCount: 0,
        storyLifecycle: { emerging: 0, breaking: 0, peak: 0, declining: 0 },
        velocityByPlatform: {},
        topStories: [],
        breakoutStories: [],
        avgVelocityScore: 0
      }
    }

    // Log summary of processed stories
    console.log('News Velocity: Processed stories', {
      totalStories: storyMetrics.length,
      storiesWithVelocity: storyMetrics.filter(s => s.avgVelocity > 0).length,
      storiesWithGrowth: storyMetrics.filter(s => s.avgGrowth !== 0).length,
      storiesWithPosts: storyMetrics.filter(s => s.avgPosts > 0).length,
      storiesWithViews: storyMetrics.filter(s => s.avgViews > 0).length,
      sampleStory: storyMetrics[0]
    })

    // Recalculate lifecycle counts from valid stories
    const storyLifecycle = { emerging: 0, breaking: 0, peak: 0, declining: 0, neutral: 0 }
    storyMetrics.forEach(story => {
      if (story.lifecycle in storyLifecycle) {
        storyLifecycle[story.lifecycle]++
      }
    })

    // Calculate platform-level velocity
    storyMetrics.forEach(story => {
      const platformName = story.platform

      if (!velocityByPlatform[platformName]) {
        velocityByPlatform[platformName] = {
          totalStories: 0,
          totalVelocity: 0,
          totalGrowth: 0,
          breakoutCount: 0,
          avgVelocityScore: 0,
          velocityScores: []
        }
      }
      const platform = velocityByPlatform[platformName]
      platform.totalStories++
      platform.totalVelocity += (isNaN(story.avgVelocity) ? 0 : Math.abs(story.avgVelocity))
      platform.totalGrowth += (isNaN(story.avgGrowth) ? 0 : story.avgGrowth)
      platform.velocityScores.push(isNaN(story.velocityScore) ? 0 : story.velocityScore)
      if (story.lifecycle === 'breaking') platform.breakoutCount++
    })

    // Calculate platform averages
    Object.keys(velocityByPlatform).forEach(platform => {
      const data = velocityByPlatform[platform]
      if (data.totalStories > 0) {
        data.avgVelocity = data.totalVelocity / data.totalStories
        data.avgGrowth = data.totalGrowth / data.totalStories
        const totalScore = data.velocityScores.reduce((sum, s) => sum + (isNaN(s) ? 0 : s), 0)
        data.avgVelocityScore = totalScore / data.totalStories
      }
    })

    // Sort stories by velocity score (only include stories with valid scores)
    const topStories = storyMetrics
      .filter(s => s && !isNaN(s.velocityScore) && s.velocityScore >= 0)
      .sort((a, b) => (b.velocityScore || 0) - (a.velocityScore || 0))
      .slice(0, 15)

    // Sort breakout stories by severity and velocity
    const sortedBreakouts = breakoutStories
      .filter(b => b && !isNaN(b.velocityScore))
      .sort((a, b) => {
        if (a.severity !== b.severity) {
          return a.severity === 'critical' ? -1 : 1
        }
        return (b.velocityScore || 0) - (a.velocityScore || 0)
      })
      .slice(0, 10)

    // Calculate overall average velocity score
    const validScores = storyMetrics
      .map(s => s.velocityScore)
      .filter(score => !isNaN(score) && score >= 0)
    const avgVelocityScore = validScores.length > 0
      ? validScores.reduce((sum, score) => sum + score, 0) / validScores.length
      : 0

    return {
      totalStories: storyMetrics.length,
      breakoutCount: sortedBreakouts.length,
      storyLifecycle,
      velocityByPlatform,
      topStories,
      breakoutStories: sortedBreakouts,
      avgVelocityScore: Math.max(0, avgVelocityScore)
    }
  }, [filteredData])

  // Update breakout alerts when new breakouts are detected
  useEffect(() => {
    if (newsVelocityAnalysis && newsVelocityAnalysis.breakoutStories.length > 0) {
      setBreakoutAlerts(prev => {
        const existingIds = new Set(prev.map(a => a.id))
        const newAlerts = newsVelocityAnalysis.breakoutStories
          .filter(story => !existingIds.has(story.id))
          .map(story => ({
            ...story,
            read: false,
            createdAt: new Date().toISOString()
          }))

        return newAlerts.length > 0 ? [...newAlerts, ...prev].slice(0, 50) : prev
      })
    }
  }, [newsVelocityAnalysis])

  // Update alerts when anomalies are detected
  useEffect(() => {
    if (anomalyDetection.length > 0) {
      setAlerts(prev => {
        const existingIds = new Set(prev.map(a => a.id))
        const newAlerts = anomalyDetection
          .filter(anomaly => !existingIds.has(anomaly.id))
          .map(anomaly => ({
            ...anomaly,
            read: false,
            createdAt: new Date().toISOString()
          }))

        return newAlerts.length > 0 ? [...newAlerts, ...prev].slice(0, 100) : prev
      })
    }
  }, [anomalyDetection])

  const heroHighlights = useMemo(() => {
    if (!filteredData.length) return []

    const score = entry => {
      const posts = Number(entry.Posts || entry.posts || 0)
      const views = Number(entry.Views || entry.views || 0)
      const engagement = Number(entry.Engagement_score || entry.engagement_score || 0)
      const velocity = Number(entry.Trend_velocity || entry.trend_velocity || entry.Velocity || entry.velocity || 0)
      const growthPct = Number(entry.Growth_pct || entry.growth_pct || entry.GrowthPercent || 0)
      return engagement * 4 + posts * 2 + views + velocity * 5 + growthPct * 3
    }

    const normalized = filteredData.map(item => {
      // Try multiple fields for topic
      const topic = (
        item.Topic ||
        item.topic ||
        item.name ||
        item.title ||
        item.text ||
        item.content ||
        item.hashtag ||
        ''
      ).toString().trim()

      const platform = (item.Platform || item.platform || selectedPlatform?.label || '').toString()
      const status = (item.Status || item.status || item.status_label || '').toString().toLowerCase()
      const velocity = Number(item.Trend_velocity || item.trend_velocity || item.Velocity || item.velocity || 0)
      const growthPct = Number(item.Growth_pct || item.growth_pct || item.GrowthPercent || item.growth || 0)
      const engagement = Number(item.Engagement_score || item.engagement_score || item.engagement || 0)
      const posts = Number(item.Posts || item.posts || item.post_count || 0)

      // Extract hashtag from topic if it contains one
      let displayTopic = topic
      if (!displayTopic || displayTopic === 'Untitled Trend') {
        // Try to extract from other fields
        const hashtagMatch = JSON.stringify(item).match(/#[\w]+/i)
        if (hashtagMatch) {
          displayTopic = hashtagMatch[0]
        } else {
          displayTopic = 'Trending Topic'
        }
      }

      return {
        raw: item,
        topic: displayTopic,
        platform: platform || selectedPlatform?.label || 'Cross-platform',
        status,
        velocity,
        growthPct,
        engagement,
        posts,
        score: score(item),
      }
    })

    normalized.sort((a, b) => b.score - a.score)

    const categories = [
      { key: 'breaking', label: 'Breaking', badgeClass: 'badge-breaking' },
      { key: 'surging', label: 'Surging', badgeClass: 'badge-surging' },
      { key: 'fading', label: 'Fading', badgeClass: 'badge-fading' },
    ]

    return categories
      .map(category => {
        const match =
          normalized.find(item => item.status === category.key) ||
          (category.key === 'fading' ? normalized[normalized.length - 1] : normalized[0])

        if (!match) return null

        let metric = ''
        if (match.engagement > 0) {
          metric = `${match.engagement.toLocaleString()} engagement`
        } else if (match.velocity > 0) {
          metric = `${match.velocity.toFixed(1)} velocity`
        } else if (match.growthPct !== 0) {
          metric = `${match.growthPct > 0 ? '+' : ''}${match.growthPct.toFixed(1)}% growth`
        } else if (match.posts > 0) {
          metric = `${match.posts.toLocaleString()} posts`
        } else {
          metric = 'No metrics'
        }

        return {
          id: `${category.key}-${match.topic}`,
          topic: match.topic,
          metric,
          badge: category.label,
          badgeClass: category.badgeClass,
          footer: match.platform ? `Platform: ${match.platform}` : 'Cross-platform',
        }
      })
      .filter(Boolean)
  }, [filteredData, selectedPlatform])

  const calendarData = useMemo(() => {
    if (!filteredData.length) return []

    const slotsPerDay = ['09:00', '12:30', '17:00']
    const now = new Date()
    const start = new Date(now)
    const day = start.getDay()
    const diff = (day === 0 ? -6 : 1) - day
    start.setDate(start.getDate() + diff)
    start.setHours(0, 0, 0, 0)

    const normalized = filteredData.map((row, idx) => {
      const topic = (row.Topic || row.topic || 'Untitled Trend').toString()
      const platform = (row.Platform || row.platform || (selectedPlatform?.label ?? 'Cross-platform')).toString()
      const status = (row.Status || row.status || 'neutral').toString().toLowerCase()
      const velocity = Number(row.Trend_velocity || row.trend_velocity || row.velocity || 0)
      const growthPct = Number(row.Growth_pct || row.growth_pct || row.GrowthPercent || 0)
      const engagement = Number(row.Engagement_score || row.engagement_score || 0)
      const views = Number(row.Views || row.views || 0)
      const createdFallback = row.created_at || row.createdAt || row.timestamp || null
      const createdDate = createdFallback ? new Date(createdFallback) : new Date(start.getTime() + idx * 60 * 60 * 1000)

      return {
        topic,
        platform,
        status: ['breaking', 'surging', 'fading'].includes(status) ? status : 'neutral',
        velocity,
        growthPct,
        engagement,
        views,
        createdDate: Number.isNaN(createdDate.getTime()) ? new Date(start.getTime() + idx * 60 * 60 * 1000) : createdDate,
      }
    })

    const suggestions = [...normalized].sort((a, b) => (b.velocity || 0) - (a.velocity || 0))
    let pointer = 0

    return Array.from({ length: 7 }).map((_, index) => {
      const date = new Date(start)
      date.setDate(start.getDate() + index)
      const dayName = date.toLocaleDateString(undefined, { weekday: 'short' })
      const dateLabel = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })

      const slots = slotsPerDay.map((time) => {
        const suggestion = suggestions[pointer] || null
        pointer += 1

        if (!suggestion) {
          return {
            time,
            topic: 'Open slot – drag in a campaign',
            platform: selectedPlatform?.label || 'Any Platform',
            status: 'neutral',
            velocity: 0,
            growthPct: 0,
            engagement: 0,
            views: 0,
          }
        }

        return {
          time,
          topic: suggestion.topic,
          platform: suggestion.platform,
          status: suggestion.status || 'neutral',
          velocity: suggestion.velocity,
          growthPct: suggestion.growthPct,
          engagement: suggestion.engagement,
          views: suggestion.views,
        }
      })

      return {
        id: `${date.toISOString().split('T')[0]}-${index}`,
        dayName,
        dateLabel,
        slots,
      }
    })
  }, [filteredData, selectedPlatform])

  const execPackData = useMemo(() => {
    if (!filteredData.length) return null

    const totals = filteredData.reduce(
      (acc, row) => {
        const posts = Number(row.Posts || row.posts || 0)
        const views = Number(row.Views || row.views || 0)
        const engagement = Number(row.Engagement_score || row.engagement_score || 0)
        const velocity = Number(row.Trend_velocity || row.trend_velocity || row.velocity || 0)
        const status = (row.Status || row.status || '').toString().toLowerCase()
        const platform = (row.Platform || row.platform || 'Cross-platform').toString()

        acc.posts += Number.isFinite(posts) ? posts : 0
        acc.views += Number.isFinite(views) ? views : 0
        acc.engagement += Number.isFinite(engagement) ? engagement : 0
        acc.velocity.push(Number.isFinite(velocity) ? velocity : 0)
        acc.statusCounts[status] = (acc.statusCounts[status] || 0) + 1
        acc.platforms[platform] = (acc.platforms[platform] || 0) + 1
        return acc
      },
      {
        posts: 0,
        views: 0,
        engagement: 0,
        velocity: [],
        statusCounts: {},
        platforms: {},
      },
    )

    const avgVelocity =
      totals.velocity.length > 0
        ? totals.velocity.reduce((sum, value) => sum + value, 0) / totals.velocity.length
        : 0

    const topTopics = filteredData.slice(0, 5).map(row => ({
      topic: row.Topic || row.topic || 'Untitled Trend',
      platform: row.Platform || row.platform || 'Cross-platform',
      velocity: Number(row.Trend_velocity || row.trend_velocity || row.velocity || 0),
      growthPct: Number(row.Growth_pct || row.growth_pct || row.GrowthPercent || 0),
      status: (row.Status || row.status || 'neutral').toString().toLowerCase(),
    }))

    const watchouts = filteredData
      .filter(row => {
        const status = (row.Status || row.status || '').toString().toLowerCase()
        return status === 'fading' || status === 'declining'
      })
      .slice(0, 3)
      .map(row => ({
        topic: row.Topic || row.topic || 'Untitled Trend',
        platform: row.Platform || row.platform || 'Cross-platform',
        growthPct: Number(row.Growth_pct || row.growth_pct || row.GrowthPercent || 0),
      }))

    const hashtagRollup = Object.entries(hashtagsWithUrls).flatMap(([platform, list]) =>
      list.slice(0, 3).map(tag => ({
        platform,
        hashtag: tag.hashtag,
        url: tag.url,
      })),
    )

    return {
      generatedAt: new Date(),
      totalRecords: filteredData.length,
      posts: totals.posts,
      views: totals.views,
      engagement: totals.engagement,
      avgVelocity,
      statusCounts: totals.statusCounts,
      platforms: totals.platforms,
      topTopics,
      watchouts,
      hashtagRollup,
      highlights: heroHighlights,
      timeRange: selectedTimeRange.label,
      platformLabel: selectedPlatform?.label || 'All Platforms',
    }
  }, [filteredData, heroHighlights, hashtagsWithUrls, selectedPlatform, selectedTimeRange])

  const execPackMarkdown = useMemo(() => {
    if (!execPackData) return ''

    const lines = []
    lines.push(`# Executive Report – ${execPackData.platformLabel}`)
    lines.push(`**Time Range:** ${execPackData.timeRange}`)
    lines.push(`**Generated:** ${execPackData.generatedAt.toLocaleString()}`)
    lines.push('')
    lines.push('## Platform Snapshot')
    lines.push(
      `- Records: ${execPackData.totalRecords.toLocaleString()} | Posts: ${execPackData.posts.toLocaleString()} | Engagement: ${execPackData.engagement.toLocaleString()} | Views: ${execPackData.views.toLocaleString()}`,
    )
    lines.push(`- Avg Velocity: ${execPackData.avgVelocity.toFixed(1)}`)
    lines.push(
      `- Status Mix: ${Object.entries(execPackData.statusCounts)
        .map(([status, count]) => `${status || 'unknown'} (${count})`)
        .join(', ') || 'n/a'}`,
    )
    lines.push(
      `- Platform Mix: ${Object.entries(execPackData.platforms)
        .map(([platform, count]) => `${platform} (${count})`)
        .join(', ')}`,
    )
    lines.push('')
    lines.push('## Top Plays')
    execPackData.topTopics.forEach(item => {
      lines.push(
        `- ${item.topic} (${item.platform}) – Velocity ${item.velocity.toFixed(1)}, Growth ${item.growthPct.toFixed(
          1,
        )}%, Status: ${item.status}`,
      )
    })
    lines.push('')
    if (execPackData.watchouts.length) {
      lines.push('## Watchouts')
      execPackData.watchouts.forEach(item => {
        lines.push(`- ${item.topic} (${item.platform}) – Growth ${item.growthPct.toFixed(1)}%`)
      })
      lines.push('')
    }
    if (execPackData.hashtagRollup.length) {
      lines.push('## Hot Hashtags')
      execPackData.hashtagRollup.forEach(item => {
        lines.push(`- #${item.hashtag} (${item.platform})${item.url ? ` → ${item.url}` : ''}`)
      })
      lines.push('')
    }
    if (execPackData.highlights.length) {
      lines.push('## Highlights')
      execPackData.highlights.forEach(card => {
        lines.push(`- ${card.badge}: ${card.topic} (${card.metric})`)
      })
    }

    lines.push('')
    lines.push('_Generated via Trend Engine_')

    return lines.join('\n')
  }, [execPackData])

  const downloadExecPack = useCallback(() => {
    if (!execPackData) return
    const blob = new Blob([execPackMarkdown], { type: 'text/markdown' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    const label = selectedPlatform?.label ? selectedPlatform.label.replace(/\s+/g, '_').toLowerCase() : 'all-platforms'
    a.href = url
    a.download = `executive-report-${label}-${new Date().toISOString().split('T')[0]}.md`
    a.click()
    window.URL.revokeObjectURL(url)
  }, [execPackData, execPackMarkdown, selectedPlatform])

  const copyExecPack = useCallback(async () => {
    if (!execPackMarkdown) return
    try {
      await navigator.clipboard.writeText(execPackMarkdown)
      setExecPackCopied(true)
      setTimeout(() => setExecPackCopied(false), 2000)
    } catch (copyErr) {
      console.warn('Clipboard unavailable, falling back to download.', copyErr)
      downloadExecPack()
    }
  }, [downloadExecPack, execPackMarkdown])

  const lastUpdated = useMemo(() => {
    if (!data.length) return null
    const timestamps = data
      .map(row => {
        const createdValue =
          row.updated_at ||
          row.created_at ||
          row.createdAt ||
          row.Created_at ||
          row.CreatedAt ||
          row.timestamp ||
          row.Timestamp ||
          row.date ||
          row.Date
        if (!createdValue) return null
        const parsed = new Date(createdValue)
        return Number.isNaN(parsed.getTime()) ? null : parsed
      })
      .filter(Boolean)
    if (!timestamps.length) return null
    return new Date(Math.max(...timestamps.map(date => date.getTime())))
  }, [data])

  const filterData = useCallback((dataSet, term, timeRange) => {
    if (!Array.isArray(dataSet)) return []

    const normalizedTerm = term.trim().toLowerCase()
    const hasCutoff = Boolean(timeRange?.hours)
    const cutoff = hasCutoff ? Date.now() - timeRange.hours * 60 * 60 * 1000 : null

    return dataSet.filter(row => {
      if (hasCutoff && cutoff) {
        const createdValue =
          row.created_at ||
          row.createdAt ||
          row.Created_at ||
          row.CreatedAt ||
          row.updated_at ||
          row.timestamp ||
          row.Timestamp ||
          row.date ||
          row.Date

        if (createdValue) {
          const createdDate = new Date(createdValue)
          if (!Number.isNaN(createdDate.getTime()) && createdDate.getTime() < cutoff) {
            return false
          }
        }
      }

      if (!normalizedTerm) return true

      return Object.values(row).some(value => {
        if (value === null || value === undefined) return false
        if (typeof value === 'object') {
          try {
            return JSON.stringify(value).toLowerCase().includes(normalizedTerm)
          } catch (err) {
            return false
          }
        }
        return String(value).toLowerCase().includes(normalizedTerm)
      })
    })
  }, [])

  // Define extractHashtags BEFORE the useEffect that uses it
  const extractHashtags = useCallback((dataArray) => {
    if (!dataArray || !Array.isArray(dataArray) || dataArray.length === 0) {
      console.log('extractHashtags: No data provided or empty array')
      setHashtags([])
      setHashtagsWithUrls({})
      return
    }

    console.log('extractHashtags: Processing', dataArray.length, 'rows')
    console.log('extractHashtags: Sample row:', dataArray[0])

    const allHashtags = new Set()
    const hashtagsWithUrlsMap = new Map()

    const normalizePlatform = (platform) => {
      if (!platform) return 'Unknown'
      const lower = platform.toLowerCase().trim()
      if (lower === 'fb' || lower === 'facebook') return 'Facebook'
      if (lower === 'twitter' || lower === 'x') return 'Twitter'
      if (lower === 'ig' || lower === 'instagram') return 'Instagram'
      if (lower === 'yt' || lower === 'youtube') return 'YouTube'
      if (lower === 'linkedin' || lower === 'li') return 'LinkedIn'
      if (lower === 'tiktok' || lower === 'tt') return 'TikTok'
      return platform.charAt(0).toUpperCase() + platform.slice(1).toLowerCase()
    }

    const addHashtag = (tag, platform, url) => {
      const cleanTag = tag.replace('#', '').trim().toLowerCase()
      if (!cleanTag) return
      allHashtags.add(cleanTag)
      const key = `${platform}-${cleanTag}`
      if (!hashtagsWithUrlsMap.has(key)) {
        hashtagsWithUrlsMap.set(key, {
          hashtag: cleanTag,
          platform: platform,
          url: url,
          count: 1
        })
      } else {
        const existing = hashtagsWithUrlsMap.get(key)
        if (!existing.url && url) {
          existing.url = url
        }
        existing.count += 1
      }
    }

    dataArray.forEach(row => {
      const rawPlatform = row.Platform || row.platform || 'Unknown'
      const platform = normalizePlatform(rawPlatform)
      let url = null

      if (row.Metadata) {
        try {
          const metadata = typeof row.Metadata === 'string' ? JSON.parse(row.Metadata) : row.Metadata
          url = metadata.source_url || metadata.url || metadata.link || null
        } catch (e) {
          const urlMatch = row.Metadata.match(/https?:\/\/[^\s"']+/)
          if (urlMatch) url = urlMatch[0]
        }
      }

      if (row.source_url) url = row.source_url
      if (row.url) url = row.url
      if (row.link) url = row.link

      const topic = row.Topic || row.topic || row.name || row.title || row.text || row.content || ''
      const hashtagMatches = topic.match(/#[\w]+/g)

      if (hashtagMatches && hashtagMatches.length > 0) {
        hashtagMatches.forEach(tag => {
          addHashtag(tag, platform, url)
        })
      }

      if (topic && !hashtagMatches && topic.trim().startsWith('#')) {
        addHashtag(topic.trim(), platform, url)
      }

      Object.entries(row).forEach(([columnName, value]) => {
        if (Array.isArray(value)) {
          value.forEach(item => {
            if (typeof item === 'string' && item.trim()) {
              addHashtag(item, platform, url)
            }
          })
        } else if (typeof value === 'string' && value.trim().startsWith('[') && value.trim().endsWith(']')) {
          try {
            const parsed = JSON.parse(value)
            if (Array.isArray(parsed)) {
              parsed.forEach(item => {
                if (typeof item === 'string' && item.trim()) {
                  addHashtag(item, platform, url)
                }
              })
            }
          } catch (e) {
            const hashtagMatches = value.match(/#[\w]+/g)
            if (hashtagMatches) {
              hashtagMatches.forEach(tag => {
                addHashtag(tag, platform, url)
              })
            }
          }
        } else if (typeof value === 'string' && value.trim() && value !== topic) {
          const hashtagMatches = value.match(/#[\w]+/g)
          if (hashtagMatches) {
            hashtagMatches.forEach(tag => {
              addHashtag(tag, platform, url)
            })
          }

          const columnLower = columnName.toLowerCase()
          const isHashtagColumn = columnLower === 'c' ||
            columnLower === 'hashtags' ||
            columnLower === 'keywords' ||
            columnLower === 'tags' ||
            columnLower.includes('hashtag') ||
            columnLower.includes('keyword') ||
            columnLower.includes('tag')

          if (isHashtagColumn && value.trim() && !value.includes(' ') && value.trim().length > 0) {
            addHashtag(value, platform, url)
          }
        }
      })
    })

    setHashtags(Array.from(allHashtags).sort())

    const hashtagsArray = Array.from(hashtagsWithUrlsMap.values())
    const groupedByPlatform = hashtagsArray.reduce((acc, item) => {
      if (!acc[item.platform]) {
        acc[item.platform] = []
      }
      acc[item.platform].push(item)
      return acc
    }, {})

    Object.keys(groupedByPlatform).forEach(platform => {
      groupedByPlatform[platform].sort((a, b) => {
        if (b.count !== a.count) {
          return b.count - a.count
        }
        return a.hashtag.localeCompare(b.hashtag)
      })
    })

    setHashtagsWithUrls(groupedByPlatform)
  }, [])

  // Extract hashtags whenever filteredData changes
  useEffect(() => {
    if (filteredData && filteredData.length > 0) {
      extractHashtags(filteredData)
    } else if (filteredData && filteredData.length === 0) {
      setHashtags([])
      setHashtagsWithUrls({})
    }
  }, [filteredData, extractHashtags])

  useEffect(() => {
    // Don't fetch on initial load - let user enter table name first
    setLoading(false)
  }, [])

  useEffect(() => {
    if (data.length === 0) {
      setFilteredData([])
      return
    }
    const updated = filterData(data, searchTerm, selectedTimeRange)
    setFilteredData(updated)
  }, [data, searchTerm, selectedTimeRange, filterData])

  const fetchData = async (platformOption, forceRefresh = false) => {
    try {
      setLoading(true)
      setError(null)
      setSelectedPlatform(platformOption)

      // Clear cache if force refresh is requested
      if (forceRefresh && platformOption?.table) {
        invalidateTableCache(platformOption.table)
        console.log('🔄 Cache cleared, forcing fresh data fetch')
      }

      // Supabase/PostgreSQL table names are case-sensitive and typically lowercase
      // Try the provided name first, then try lowercase, and also try with underscores
      const baseTable = platformOption?.table || platformOption?.key || ''
      const tableNamesToTry = [
        baseTable,
        baseTable.toLowerCase(),
        baseTable.replace(/\s+/g, '_').toLowerCase(),
        baseTable.replace(/\s+/g, '_'),
      ].filter(Boolean).filter((v, i, a) => a.indexOf(v) === i) // Remove duplicates

      if (tableNamesToTry.length === 0) {
        throw new Error('No Supabase table has been configured for this platform yet.')
      }

      let fetched = false
      let lastError = null

      if (supabase) {
        for (const candidateTable of tableNamesToTry) {
          let tableData = null
          let fetchError = null

          // Check cache first
          const cacheParams = { order: 'created_at_desc' }
          const cachedData = getCachedQuery(candidateTable, cacheParams)

          if (cachedData) {
            console.log(`💾 Using cached data for table: ${candidateTable} (${cachedData.length} records)`)
            tableData = cachedData
            fetched = true
          } else {
            try {
              // First try with ordering by created_at
              const response = await supabase
                .from(candidateTable)
                .select('*')
                .order('created_at', { ascending: false })
              tableData = response.data
              fetchError = response.error

              // If ordering fails, try without ordering
              if (fetchError && (fetchError.message?.includes('created_at') || fetchError.message?.includes('column'))) {
                const retryParams = { order: 'none' }
                const retryCached = getCachedQuery(candidateTable, retryParams)

                if (retryCached) {
                  console.log(`💾 Using cached data (no order) for table: ${candidateTable}`)
                  tableData = retryCached
                  fetchError = null
                } else {
                  const retry = await supabase.from(candidateTable).select('*')
                  tableData = retry.data
                  fetchError = retry.error

                  // Cache the result if successful
                  if (!fetchError && tableData && Array.isArray(tableData) && tableData.length > 0) {
                    cacheQuery(candidateTable, retryParams, tableData)
                  }
                }
              } else if (!fetchError && tableData && Array.isArray(tableData) && tableData.length > 0) {
                // Cache successful query with ordering
                cacheQuery(candidateTable, cacheParams, tableData)
              }
            } catch (supabaseErr) {
              fetchError = supabaseErr
            }
          }

          if (!fetchError && tableData && Array.isArray(tableData) && tableData.length > 0) {
            console.log(`✅ Successfully fetched ${tableData.length} records from Supabase table: ${candidateTable}`)
            // Set data first, then filtered data will update via useEffect
            setData(tableData)
            // Also set filtered data immediately for faster UI update
            const filtered = filterData(tableData, searchTerm, selectedTimeRange)
            setFilteredData(filtered)
            // Extract hashtags from full dataset
            extractHashtags(tableData)
            fetched = true
            setError(null) // Clear any previous errors
            break
          }

          if (fetchError) {
            lastError = fetchError
            // If table doesn't exist, try next table name
            if (
              fetchError.message?.includes('Could not find the table') ||
              fetchError.message?.includes('relation') ||
              fetchError.message?.includes('does not exist') ||
              fetchError.message?.includes('permission denied')
            ) {
              console.log(`Table "${candidateTable}" not found or no access, trying next...`)
              continue
            }
            // For other errors, log but continue trying other table names
            console.warn(`Error fetching from table "${candidateTable}":`, fetchError.message)
          }
        }
      } else {
        console.warn('Supabase client unavailable; using demo data fallback.')
      }

      if (!fetched) {
        // Only use demo data if Supabase is completely unavailable or all tables don't exist
        if (!supabase) {
          console.warn('Supabase client unavailable; using demo data fallback.')
          const fallbackData = DEMO_DATA[platformOption.key] || []
          if (fallbackData.length > 0) {
            console.log(`📦 Using demo data for ${platformOption.label}: ${fallbackData.length} records`)
            setData(fallbackData)
            const filtered = filterData(fallbackData, searchTerm, selectedTimeRange)
            setFilteredData(filtered)
            extractHashtags(fallbackData)
            setError('⚠️ Supabase not configured. Showing demo data.')
          } else {
            throw new Error(
              `No Supabase connection and no demo data available for ${platformOption?.label || 'this selection'}.`
            )
          }
        } else {
          // Supabase is available but no data found - show error instead of demo data
          const debugTable = tableNamesToTry[0]
          try {
            const { data: debugData, error: debugError } = await supabase
              .from(debugTable)
              .select('*')
              .limit(5)
            console.warn('Supabase debug - No data found', {
              table: debugTable,
              rowCount: debugData?.length || 0,
              error: debugError?.message,
              sample: debugData,
            })

            if (debugData && debugData.length > 0) {
              // Data exists but wasn't fetched properly - try again with simpler query
              const { data: retryData, error: retryError } = await supabase
                .from(debugTable)
                .select('*')
              if (!retryError && retryData && retryData.length > 0) {
                console.log(`✅ Retry successful: fetched ${retryData.length} records from ${debugTable}`)
                setData(retryData)
                const filtered = filterData(retryData, searchTerm, selectedTimeRange)
                setFilteredData(filtered)
                extractHashtags(retryData)
                setError(null)
                return // Success!
              }
            }
          } catch (debugErr) {
            console.warn('Supabase debug error', debugErr)
          }

          // Only use demo data as absolute last resort if Supabase exists but has no data
          const fallbackData = DEMO_DATA[platformOption.key] || []
          if (fallbackData.length > 0) {
            const errorMsg = lastError?.message || `No data found in tables: ${tableNamesToTry.join(', ')}`
            console.warn(`⚠️ No Supabase data found for ${platformOption.label}. Showing demo data.`, errorMsg)
            setData(fallbackData)
            const filtered = filterData(fallbackData, searchTerm, selectedTimeRange)
            setFilteredData(filtered)
            extractHashtags(fallbackData)
            setError(`⚠️ No data in Supabase tables (tried: ${tableNamesToTry.join(', ')}). Showing demo data. Please add data to your Supabase table.`)
          } else {
            throw new Error(
              `No data found in Supabase tables (tried: ${tableNamesToTry.join(', ')}) and no demo data available for ${platformOption?.label || 'this selection'}.`
            )
          }
        }
      }
    } catch (err) {
      console.error('Error fetching data:', err)
      // Only use demo data if Supabase connection failed completely
      if (!supabase) {
        const fallbackData = DEMO_DATA[platformOption?.key || ''] || []
        if (fallbackData.length) {
          console.warn(`Supabase not configured. Using demo data for ${platformOption?.label || platformOption?.key}.`)
          setData(fallbackData)
          const filtered = filterData(fallbackData, searchTerm, selectedTimeRange)
          setFilteredData(filtered)
          extractHashtags(fallbackData)
          setError('⚠️ Supabase not configured. Showing demo data.')
        } else {
          setError(`Supabase not configured and no demo data available: ${err.message}`)
        }
      } else {
        // Supabase is configured but query failed - show error, don't use demo data
        setError(`Failed to fetch from Supabase: ${err.message}. Please check your Supabase configuration and table data.`)
      }
    } finally {
      setLoading(false)
    }
  }

  const handlePlatformSelect = (platformOption) => {
    // Reset view and clear search when switching platforms
    setViewMode('cards')
    setSearchTerm('')
    setError(null)
    // Fetch data for the selected platform
    fetchData(platformOption)
  }

  const handleTimeRangeChange = (range) => {
    setSelectedTimeRange(range)
    setExecPackCopied(false)
  }

  const handleSearch = (e) => {
    const term = e.target.value
    setSearchTerm(term)
  }

  const handleSort = (key) => {
    let direction = 'asc'
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc'
    }

    setSortConfig({ key, direction })

    const sorted = [...filteredData].sort((a, b) => {
      const aVal = a[key]
      const bVal = b[key]

      if (aVal === null || aVal === undefined) return 1
      if (bVal === null || bVal === undefined) return -1

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return direction === 'asc' ? aVal - bVal : bVal - aVal
      }

      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()

      if (direction === 'asc') {
        return aStr.localeCompare(bStr)
      } else {
        return bStr.localeCompare(aStr)
      }
    })

    setFilteredData(sorted)
  }

  const exportToCSV = () => {
    if (filteredData.length === 0) return

    const headers = Object.keys(filteredData[0])
    const csvContent = [
      headers.join(','),
      ...filteredData.map(row =>
        headers.map(header => {
          const value = row[header]
          if (value === null || value === undefined) return ''
          if (typeof value === 'object') return JSON.stringify(value).replace(/"/g, '""')
          return String(value).replace(/"/g, '""')
        }).map(v => `"${v}"`)
      ).map(row => row.join(','))
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const downloadLabel = selectedPlatform?.label
      ? selectedPlatform.label.replace(/\s+/g, '_').toLowerCase()
      : 'data'
    a.download = `${downloadLabel}_${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  const formatCellValue = (value, key) => {
    if (value === null || value === undefined) {
      return <span className="null-value">—</span>
    }

    // Handle arrays (like hashtags)
    if (Array.isArray(value)) {
      if (value.length === 0) {
        return <span className="empty-array">[empty]</span>
      }
      // Check if it's an array of strings (like hashtags)
      if (value.every(item => typeof item === 'string')) {
        return (
          <div className="tags-container">
            {value.map((tag, idx) => (
              <span key={idx} className="tag">
                {tag.startsWith('#') ? tag : `#${tag}`}
              </span>
            ))}
          </div>
        )
      }
      // Array of objects or mixed types
      return (
        <div className="tags-container">
          {value.map((item, idx) => (
            <span key={idx} className="tag">
              {typeof item === 'object' ? JSON.stringify(item) : String(item)}
            </span>
          ))}
        </div>
      )
    }

    // Handle objects (like Metadata)
    if (typeof value === 'object') {
      // Check if it's a date string that can be parsed
      if (value instanceof Date || (typeof value === 'string' && !isNaN(Date.parse(value)) && value.includes('T'))) {
        return new Date(value).toLocaleString()
      }
      return <pre className="json-value">{JSON.stringify(value, null, 2)}</pre>
    }

    // Handle strings that might be JSON
    if (typeof value === 'string' && value.trim().startsWith('[') && value.trim().endsWith(']')) {
      try {
        const parsed = JSON.parse(value)
        if (Array.isArray(parsed)) {
          return formatCellValue(parsed, key)
        }
      } catch (e) {
        // Not valid JSON, continue as string
      }
    }

    // Check if string contains hashtags (like "#ole" in Topic column)
    if (typeof value === 'string') {
      const hashtagMatches = value.match(/#[\w]+/g)
      if (hashtagMatches && hashtagMatches.length > 0) {
        // If the entire value is just hashtags, display them as tags
        const cleanValue = value.trim()
        const allHashtags = hashtagMatches.map(tag => tag.substring(1))

        // If the string is mostly hashtags, display as tags
        if (hashtagMatches.join(' ').length >= cleanValue.length * 0.7) {
          return (
            <div className="tags-container">
              {allHashtags.map((tag, idx) => (
                <span key={idx} className="tag">
                  #{tag}
                </span>
              ))}
            </div>
          )
        } else {
          // Mixed content - show text with hashtags highlighted
          const parts = cleanValue.split(/(#[\w]+)/g)
          return (
            <div>
              {parts.map((part, idx) => {
                if (part.startsWith('#')) {
                  return (
                    <span key={idx} className="tag-inline">
                      {part}
                    </span>
                  )
                }
                return <span key={idx}>{part}</span>
              })}
            </div>
          )
        }
      }

      // Check if it's a JSON string (like Metadata)
      if (value.trim().startsWith('{') && value.trim().endsWith('}')) {
        try {
          const parsed = JSON.parse(value)
          return <pre className="json-value">{JSON.stringify(parsed, null, 2)}</pre>
        } catch (e) {
          // Not valid JSON, continue as string
        }
      }
    }

    // Regular string/number
    return String(value)
  }

  if (loading && data.length === 0) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="dashboard-container">
        <header className="dashboard-header">
          <div className="header-content">
            <div className="header-left">
              <h1>Trend Engine</h1>
              <p className="header-subtitle">Unified intelligence on what’s trending across every social platform.</p>
              <div className="header-metadata">
                <span className="metadata-chip">
                  {selectedPlatform ? (
                    <>
                      <span
                        className="metadata-chip-logo"
                        aria-hidden="true"
                        style={{
                          backgroundImage: `url(${selectedPlatform.logo || getPlatformLogo(selectedPlatform.label)})`,
                        }}
                      />
                      <span className="metadata-chip-text">{selectedPlatform.label}</span>
                    </>
                  ) : (
                    <span className="metadata-chip-text">Select a platform</span>
                  )}
                </span>
                <span className="metadata-chip">
                  <span className="metadata-chip-text">Last updated: Just now</span>
                </span>
              </div>
            </div>
            {heroHighlights.length > 0 && (
              <div className="hero-highlight">
                {heroHighlights.map(card => (
                  <div key={card.id} className="hero-card">
                    <h3>
                      <span className={card.badgeClass}>{card.badge}</span>
                    </h3>
                    <strong>{card.topic}</strong>
                    <span>{card.metric}</span>
                    <footer>{card.footer}</footer>
                  </div>
                ))}
              </div>
            )}
            <div className="header-right">
              <div className="platform-selector">
                {PLATFORM_OPTIONS.map(option => {
                  const isActive = selectedPlatform?.key === option.key
                  const isLinkedIn = option.key === 'linkedin'
                  const logoUrl = option.logo || getPlatformLogo(option.label)
                  return (
                    <button
                      key={option.key}
                      className={`platform-btn ${isActive ? 'active' : ''}`}
                      onClick={() => handlePlatformSelect(option)}
                      disabled={loading && isActive}
                    >
                      <img
                        src={logoUrl}
                        alt={option.label}
                        className="platform-btn-logo-img"
                        aria-hidden="true"
                        onError={(e) => {
                          // Fallback to default logo if image fails to load
                          e.target.src = DEFAULT_PLATFORM_LOGO;
                        }}
                      />
                      <span>{option.label}</span>
                    </button>
                  )
                })}
              </div>
            </div>
          </div>

          {data.length > 0 && (
            <>
              <div className="stats-header">
                <div className="stat-card stat-card-blue">
                  <div className="stat-icon-wrapper stat-icon-blue">
                    <svg className="records-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2.5" fill="none" />
                      <line x1="7" y1="8" x2="17" y2="8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      <line x1="7" y1="12" x2="17" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      <line x1="7" y1="16" x2="17" y2="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      <circle cx="7" cy="8" r="1.5" fill="currentColor" />
                      <circle cx="7" cy="12" r="1.5" fill="currentColor" />
                      <circle cx="7" cy="16" r="1.5" fill="currentColor" />
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="stat-value">{filteredData.length}</div>
                    <div className="stat-label">Visible Records</div>
                  </div>
                </div>
                <div className="stat-card stat-card-orange">
                  <div className="stat-icon-wrapper stat-icon-orange">
                    <svg className="hashtag-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M10 3L8 21M16 3L14 21M3 8L21 8M3 16L21 16" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="stat-value">{hashtags.length}</div>
                    <div className="stat-label">Trending Hashtags</div>
                  </div>
                </div>
                <div className="stat-card stat-card-purple">
                  <div className="stat-icon-wrapper stat-icon-purple">
                    {selectedPlatform ? (
                      <img
                        src={selectedPlatform.logo || getPlatformLogo(selectedPlatform.label)}
                        alt={selectedPlatform.label}
                        className="platform-logo-icon"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="stat-icon-square"></div>
                    )}
                  </div>
                  <div className="stat-info">
                    <div className="stat-value">
                      {selectedPlatform ? selectedPlatform.label : `${Object.keys(hashtagsWithUrls).length || PLATFORM_OPTIONS.length} Platforms`}
                    </div>
                    <div className="stat-label">Source</div>
                  </div>
                </div>
                <div className="stat-card stat-card-indigo">
                  <div className="stat-icon-wrapper stat-icon-indigo">
                    <svg className="clock-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2.5" fill="none" />
                      <circle cx="12" cy="12" r="1.5" fill="currentColor" />
                      <line x1="12" y1="12" x2="12" y2="7" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                      <line x1="12" y1="12" x2="16" y2="12" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="stat-value">{selectedTimeRange.label}</div>
                    <div className="stat-label">Time Range</div>
                  </div>
                </div>
                <div
                  className={`stat-card view-card view-card-pink ${viewMode === 'cards' ? 'active' : ''}`}
                  onClick={() => setViewMode('cards')}
                >
                  <div className="stat-icon-wrapper stat-icon-white">
                    <svg className="view-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="3" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.9" />
                      <rect x="14" y="3" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.9" />
                      <rect x="3" y="14" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.9" />
                      <rect x="14" y="14" width="7" height="7" rx="1.5" fill="currentColor" opacity="0.9" />
                      <rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.3" />
                      <rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.3" />
                      <rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.3" />
                      <rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" fill="none" opacity="0.3" />
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="view-btn">Cards</div>
                  </div>
                </div>
              </div>

              <div className="view-modes-row">
                <div
                  className={`stat-card view-card view-card-green ${viewMode === 'table' ? 'active' : ''}`}
                  onClick={() => setViewMode('table')}
                >
                  <div className="stat-icon-wrapper stat-icon-green">
                    <svg className="view-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="3" width="18" height="18" rx="1.5" fill="currentColor" opacity="0.8" />
                      <rect x="3" y="3" width="18" height="18" rx="1.5" stroke="currentColor" strokeWidth="2" fill="none" />
                      <line x1="3" y1="9" x2="21" y2="9" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                      <line x1="9" y1="3" x2="9" y2="21" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                      <line x1="15" y1="3" x2="15" y2="21" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                      <rect x="4" y="4" width="4" height="4" rx="0.5" fill="white" opacity="0.9" />
                      <rect x="10" y="4" width="4" height="4" rx="0.5" fill="white" opacity="0.9" />
                      <rect x="16" y="4" width="4" height="4" rx="0.5" fill="white" opacity="0.9" />
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="view-btn">Table</div>
                  </div>
                </div>
                <div
                  className={`stat-card view-card view-card-cyan ${viewMode === 'calendar' ? 'active' : ''}`}
                  onClick={() => setViewMode('calendar')}
                >
                  <div className="stat-icon-wrapper stat-icon-cyan">
                    <svg className="view-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="5" width="18" height="16" rx="2" fill="currentColor" opacity="0.8" />
                      <rect x="3" y="5" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="2" fill="none" />
                      <rect x="3" y="5" width="18" height="5" rx="2" fill="currentColor" opacity="0.9" />
                      <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                      <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                      <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                      <circle cx="7" cy="14" r="1.5" fill="white" opacity="1" />
                      <circle cx="12" cy="14" r="1.5" fill="white" opacity="1" />
                      <circle cx="17" cy="14" r="1.5" fill="white" opacity="1" />
                      <circle cx="7" cy="18" r="1.5" fill="white" opacity="1" />
                      <circle cx="12" cy="18" r="1.5" fill="white" opacity="1" />
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="view-btn">Calendar</div>
                  </div>
                </div>
              </div>
            </>
          )}
        </header>

        {error && (
          <div className="error-message">
            <p><strong>Error:</strong> {error}</p>
            <p className="error-hint">
              Make sure the Supabase table contains data and that your `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` variables are configured.
            </p>
          </div>
        )}

        {!error && data.length === 0 && !loading && selectedPlatform && (
          <div className="empty-state">
            <p>No records found for {selectedPlatform.label}. Refresh your Supabase data and try again.</p>
          </div>
        )}


        {!error && data.length > 0 && (
          <>
            {/* Controls Bar */}
            <div className="controls-bar">
              <div className="search-container">
                <input
                  type="text"
                  placeholder="Search across all columns..."
                  value={searchTerm}
                  onChange={handleSearch}
                  className="search-input"
                />
                {searchTerm && (
                  <button
                    onClick={() => { setSearchTerm('') }}
                    className="clear-search-btn"
                    title="Clear search"
                  >
                    ✕
                  </button>
                )}
              </div>

              <div className="controls-actions">
                <button onClick={exportToCSV} className="export-btn" title="Export to CSV">
                  {'\u{1F4E5}'} Export CSV
                </button>
                <button
                  onClick={() => {
                    setShowExecPackPanel(prev => !prev)
                    setExecPackCopied(false)
                  }}
                  className="exec-pack-btn"
                  title="Generate executive report: A formatted summary of key metrics, top trends, and insights ready to share with leadership"
                  disabled={!execPackData}
                >
                  {'\u{1F4C4}'} Executive Report
                </button>
                <button
                  onClick={() => setShowHashtagsPanel(!showHashtagsPanel)}
                  className="hashtags-toggle-btn"
                  title="Toggle hashtags panel"
                >
                  {showHashtagsPanel ? '\u{1F53D}' : '\u{1F53C}'} Hashtags ({hashtags.length})
                </button>
                <button
                  onClick={() => setShowBrandwatchPanel(prev => !prev)}
                  className="brandwatch-btn"
                  title="Sentiment Analysis & Anomaly Detection"
                >
                  {'\u{1F50D}'} Sentiment & Alerts {alerts.filter(a => !a.read).length > 0 && `(${alerts.filter(a => !a.read).length})`}
                </button>
                <button
                  onClick={() => setShowMeltwaterPanel(prev => !prev)}
                  className="meltwater-btn"
                  title="News Velocity & Story Breakout Detection"
                >
                  {'\u{1F4F0}'} News Velocity {breakoutAlerts.filter(a => !a.read).length > 0 && `(${breakoutAlerts.filter(a => !a.read).length})`}
                </button>
              </div>
            </div>

            {showExecPackPanel && execPackData && (
              <div className="exec-pack-panel">
                <div className="exec-pack-header">
                  <div>
                    <h2>Executive Report</h2>
                    <p>
                      Ready-to-drop snapshot for leadership. Auto-tailored to{' '}
                      <strong>{execPackData.platformLabel}</strong> · Range {execPackData.timeRange}.
                    </p>
                  </div>
                  <div className="exec-pack-actions">
                    <button onClick={copyExecPack} className="exec-pack-action-btn">
                      {execPackCopied ? '✅ Copied!' : '📋 Copy Markdown'}
                    </button>
                    <button onClick={downloadExecPack} className="exec-pack-action-btn">
                      ⬇️ Download .md
                    </button>
                  </div>
                </div>
                <div className="exec-pack-grid">
                  <div className="exec-pack-card exec-pack-card--metrics">
                    <h3>Pulse Metrics</h3>
                    <ul>
                      <li><strong>Records:</strong> {execPackData.totalRecords.toLocaleString()}</li>
                      <li><strong>Posts:</strong> {execPackData.posts.toLocaleString()}</li>
                      <li><strong>Engagement:</strong> {execPackData.engagement.toLocaleString()}</li>
                      <li><strong>Views:</strong> {execPackData.views.toLocaleString()}</li>
                      <li><strong>Avg Velocity:</strong> {execPackData.avgVelocity.toFixed(1)}</li>
                    </ul>
                    <div className="exec-pack-chips">
                      {Object.entries(execPackData.statusCounts).map(([status, count]) => (
                        <span key={status} className={`exec-pack-chip exec-pack-chip--${status || 'neutral'}`}>
                          {status || 'neutral'} · {count}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="exec-pack-card">
                    <h3>Top Plays</h3>
                    <ul>
                      {execPackData.topTopics.map(item => (
                        <li key={`${item.topic}-${item.platform}`}>
                          <strong>{item.topic}</strong> · {item.platform} ·{' '}
                          <span>Velocity {item.velocity.toFixed(1)} · Growth {item.growthPct.toFixed(1)}%</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div className="exec-pack-card">
                    <h3>Platform Mix</h3>
                    <ul>
                      {Object.entries(execPackData.platforms).map(([platform, count]) => (
                        <li key={platform}>
                          <strong>{platform}</strong> · {count} records
                        </li>
                      ))}
                    </ul>
                    {execPackData.watchouts.length > 0 && (
                      <div className="exec-pack-watchouts">
                        <h4>Watchouts</h4>
                        <ul>
                          {execPackData.watchouts.map(item => (
                            <li key={`${item.topic}-${item.platform}`}>
                              {item.topic} ({item.platform}) – Growth {item.growthPct.toFixed(1)}%
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <div className="exec-pack-card exec-pack-card--markdown">
                    <h3>Pack Preview</h3>
                    <pre>{execPackMarkdown}</pre>
                  </div>
                </div>
              </div>
            )}

            {/* Brandwatch Sentiment & Alerts Panel */}
            {showBrandwatchPanel && (
              <div className="brandwatch-panel">
                <div className="brandwatch-header">
                  <div>
                    <h2>🔍 Sentiment & Anomaly Detection</h2>
                    <p>
                      Granular sentiment analysis and anomaly detection for{' '}
                      <strong>{selectedPlatform?.label || 'all platforms'}</strong>.
                    </p>
                  </div>
                  <span className="brandwatch-tag">Research-Grade Listening</span>
                </div>

                <div className="brandwatch-grid">
                  {/* Overall Sentiment */}
                  {sentimentAnalysis ? (
                    <>
                      <div className="brandwatch-card brandwatch-card--sentiment">
                        <h3>Overall Sentiment</h3>
                        <div className="sentiment-score">
                          <div className="sentiment-score-value" style={{
                            color: sentimentAnalysis.score > 0 ? '#059669' : sentimentAnalysis.score < 0 ? '#dc2626' : '#64748b'
                          }}>
                            {sentimentAnalysis.score > 0 ? '+' : ''}{sentimentAnalysis.score.toFixed(1)}
                          </div>
                          <div className="sentiment-score-label">Sentiment Score</div>
                        </div>
                        <div className="sentiment-breakdown">
                          <div className="sentiment-bar">
                            <div
                              className="sentiment-segment sentiment-positive"
                              style={{ width: `${(sentimentAnalysis.overall.positive / (sentimentAnalysis.overall.positive + sentimentAnalysis.overall.negative + sentimentAnalysis.overall.neutral)) * 100}%` }}
                            >
                              <span>Positive: {sentimentAnalysis.overall.positive}</span>
                            </div>
                            <div
                              className="sentiment-segment sentiment-neutral"
                              style={{ width: `${(sentimentAnalysis.overall.neutral / (sentimentAnalysis.overall.positive + sentimentAnalysis.overall.negative + sentimentAnalysis.overall.neutral)) * 100}%` }}
                            >
                              <span>Neutral: {sentimentAnalysis.overall.neutral}</span>
                            </div>
                            <div
                              className="sentiment-segment sentiment-negative"
                              style={{ width: `${(sentimentAnalysis.overall.negative / (sentimentAnalysis.overall.positive + sentimentAnalysis.overall.negative + sentimentAnalysis.overall.neutral)) * 100}%` }}
                            >
                              <span>Negative: {sentimentAnalysis.overall.negative}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Sentiment by Platform */}
                      <div className="brandwatch-card">
                        <h3>Sentiment by Platform</h3>
                        <div className="platform-sentiment-list">
                          {Object.entries(sentimentAnalysis.byPlatform).map(([platform, data]) => {
                            const total = data.positive + data.negative + data.neutral
                            const score = total > 0 ? ((data.positive - data.negative) / total) * 100 : 0
                            return (
                              <div key={platform} className="platform-sentiment-item">
                                <div className="platform-sentiment-header">
                                  <span className="platform-sentiment-name">{platform}</span>
                                  <span className="platform-sentiment-score" style={{
                                    color: score > 0 ? '#059669' : score < 0 ? '#dc2626' : '#64748b'
                                  }}>
                                    {score > 0 ? '+' : ''}{score.toFixed(1)}
                                  </span>
                                </div>
                                <div className="platform-sentiment-bars">
                                  <div className="sentiment-mini-bar">
                                    <div className="sentiment-mini-segment sentiment-positive" style={{ width: `${(data.positive / total) * 100}%` }}></div>
                                    <div className="sentiment-mini-segment sentiment-neutral" style={{ width: `${(data.neutral / total) * 100}%` }}></div>
                                    <div className="sentiment-mini-segment sentiment-negative" style={{ width: `${(data.negative / total) * 100}%` }}></div>
                                  </div>
                                </div>
                                <div className="platform-sentiment-counts">
                                  <span className="sentiment-count-positive">👍 {data.positive}</span>
                                  <span className="sentiment-count-neutral">😐 {data.neutral}</span>
                                  <span className="sentiment-count-negative">👎 {data.negative}</span>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>

                      {/* Top Topics by Sentiment */}
                      {sentimentAnalysis.byTopic.length > 0 && (
                        <div className="brandwatch-card">
                          <h3>Top Topics Sentiment</h3>
                          <div className="topics-sentiment-list">
                            {sentimentAnalysis.byTopic.slice(0, 8).map((item, idx) => (
                              <div key={idx} className="topic-sentiment-item">
                                <div className="topic-sentiment-header">
                                  <span className="topic-sentiment-name">{item.topic}</span>
                                  <span className="topic-sentiment-score" style={{
                                    color: item.sentimentScore > 0 ? '#059669' : item.sentimentScore < 0 ? '#dc2626' : '#64748b'
                                  }}>
                                    {item.sentimentScore > 0 ? '+' : ''}{item.sentimentScore.toFixed(1)}
                                  </span>
                                </div>
                                <div className="topic-sentiment-stats">
                                  <span className="sentiment-stat-positive">+{item.positive}</span>
                                  <span className="sentiment-stat-neutral">~{item.neutral}</span>
                                  <span className="sentiment-stat-negative">-{item.negative}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Entity Sentiment */}
                      {sentimentAnalysis.entities.length > 0 && (
                        <div className="brandwatch-card">
                          <h3>Entity Sentiment Analysis</h3>
                          <div className="entities-list">
                            {sentimentAnalysis.entities.slice(0, 12).map((entity, idx) => (
                              <div key={idx} className="entity-item">
                                <div className="entity-header">
                                  <span className="entity-name">#{entity.entity}</span>
                                  <span className="entity-count">{entity.count} mentions</span>
                                </div>
                                <div className="entity-sentiment">
                                  <span className="entity-sentiment-score" style={{
                                    color: entity.sentimentScore > 0 ? '#059669' : entity.sentimentScore < 0 ? '#dc2626' : '#64748b'
                                  }}>
                                    {entity.sentimentScore > 0 ? '+' : ''}{entity.sentimentScore.toFixed(1)}%
                                  </span>
                                  <div className="entity-sentiment-breakdown">
                                    <span className="entity-positive">+{entity.sentiment.positive}</span>
                                    <span className="entity-neutral">~{entity.sentiment.neutral}</span>
                                    <span className="entity-negative">-{entity.sentiment.negative}</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="brandwatch-card">
                      <h3>Sentiment Analysis</h3>
                      <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                        <p>Analyzing sentiment from your data metrics...</p>
                        <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>
                          Sentiment is inferred from growth rates, velocity, engagement, and status indicators.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Anomaly Detection Alerts */}
                  {anomalyDetection.length > 0 ? (
                    <div className="brandwatch-card brandwatch-card--alerts">
                      <div className="alerts-header">
                        <h3>Anomaly Detection Alerts</h3>
                        <div className="alerts-badge">
                          {anomalyDetection.length} {anomalyDetection.length === 1 ? 'Anomaly' : 'Anomalies'}
                        </div>
                      </div>
                      <div className="alerts-list">
                        {anomalyDetection.slice(0, 10).map(anomaly => (
                          <div key={anomaly.id} className={`alert-item alert-${anomaly.severity}`}>
                            <div className="alert-icon">
                              {anomaly.severity === 'critical' ? '🚨' : '⚠️'}
                            </div>
                            <div className="alert-content">
                              <div className="alert-header">
                                <span className="alert-type">{anomaly.type.replace('_', ' ').toUpperCase()}</span>
                                <span className="alert-severity">{anomaly.severity}</span>
                              </div>
                              <div className="alert-details">
                                <strong>{anomaly.topic || 'Unknown Topic'}</strong> on {anomaly.platform}
                              </div>
                              <div className="alert-metrics">
                                <span>{anomaly.metric}: {anomaly.value.toLocaleString()}</span>
                                <span>Expected: ~{anomaly.expected.toFixed(0)}</span>
                                <span className="alert-deviation">{anomaly.deviation.toFixed(1)}σ deviation</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="brandwatch-card">
                      <h3>Anomaly Detection</h3>
                      <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                        <p>No anomalies detected in current data.</p>
                        <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>
                          {filteredData.length < 3
                            ? 'Need at least 3 data points for anomaly detection.'
                            : 'All metrics are within normal ranges.'}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Active Alerts */}
                  {alerts.length > 0 && (
                    <div className="brandwatch-card brandwatch-card--active-alerts">
                      <div className="alerts-header">
                        <h3>Active Alerts</h3>
                        <button
                          onClick={() => setAlerts(prev => prev.map(a => ({ ...a, read: true })))}
                          className="mark-all-read-btn"
                        >
                          Mark All Read
                        </button>
                      </div>
                      <div className="active-alerts-list">
                        {alerts.slice(0, 15).map(alert => (
                          <div key={alert.id} className={`active-alert-item ${alert.read ? 'read' : 'unread'}`}>
                            <div className="active-alert-icon">
                              {alert.severity === 'critical' ? '🚨' : '⚠️'}
                            </div>
                            <div className="active-alert-content">
                              <div className="active-alert-header">
                                <span className="active-alert-type">{alert.type.replace('_', ' ')}</span>
                                <span className="active-alert-time">
                                  {new Date(alert.createdAt || alert.timestamp).toLocaleString()}
                                </span>
                              </div>
                              <div className="active-alert-details">
                                {alert.topic} · {alert.platform} · {alert.metric}: {alert.value.toLocaleString()}
                              </div>
                            </div>
                            <button
                              onClick={() => setAlerts(prev => prev.map(a => a.id === alert.id ? { ...a, read: true } : a))}
                              className="mark-read-btn"
                            >
                              {alert.read ? '✓' : 'Mark Read'}
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Meltwater News Velocity & Story Breakout Panel */}
            {showMeltwaterPanel && (
              <div className="meltwater-panel">
                <div className="meltwater-header">
                  <div>
                    <h2>📰 News Velocity Intelligence</h2>
                    <p>
                      Story breakout detection and velocity tracking for{' '}
                      <strong>{selectedPlatform?.label || 'all platforms'}</strong>.
                    </p>
                  </div>
                  <span className="meltwater-tag">Media Intelligence</span>
                </div>

                <div className="meltwater-grid">
                  {/* Overall Velocity Metrics */}
                  {newsVelocityAnalysis ? (
                    <>
                      <div className="meltwater-card meltwater-card--velocity">
                        <h3>Velocity Overview</h3>
                        <div className="velocity-stats">
                          <div className="velocity-stat">
                            <div className="velocity-stat-value">{newsVelocityAnalysis.totalStories || 0}</div>
                            <div className="velocity-stat-label">Total Stories</div>
                          </div>
                          <div className="velocity-stat">
                            <div className="velocity-stat-value" style={{ color: '#dc2626' }}>
                              {newsVelocityAnalysis.breakoutCount || 0}
                            </div>
                            <div className="velocity-stat-label">Breakouts</div>
                          </div>
                          <div className="velocity-stat">
                            <div className="velocity-stat-value" style={{ color: '#2563eb' }}>
                              {(newsVelocityAnalysis.avgVelocityScore || 0).toFixed(1)}
                            </div>
                            <div className="velocity-stat-label">Avg Velocity Score</div>
                          </div>
                        </div>
                        <div className="story-lifecycle">
                          <h4>Story Lifecycle</h4>
                          <div className="lifecycle-bars">
                            <div className="lifecycle-bar">
                              {newsVelocityAnalysis && newsVelocityAnalysis.totalStories > 0 ? (
                                <>
                                  {newsVelocityAnalysis.storyLifecycle.breaking > 0 && (
                                    <div className="lifecycle-segment lifecycle-breaking" style={{ width: `${Math.max((newsVelocityAnalysis.storyLifecycle.breaking / newsVelocityAnalysis.totalStories) * 100, 5)}%` }}>
                                      <span>Breaking: {newsVelocityAnalysis.storyLifecycle.breaking}</span>
                                    </div>
                                  )}
                                  {newsVelocityAnalysis.storyLifecycle.peak > 0 && (
                                    <div className="lifecycle-segment lifecycle-peak" style={{ width: `${Math.max((newsVelocityAnalysis.storyLifecycle.peak / newsVelocityAnalysis.totalStories) * 100, 5)}%` }}>
                                      <span>Peak: {newsVelocityAnalysis.storyLifecycle.peak}</span>
                                    </div>
                                  )}
                                  {newsVelocityAnalysis.storyLifecycle.emerging > 0 && (
                                    <div className="lifecycle-segment lifecycle-emerging" style={{ width: `${Math.max((newsVelocityAnalysis.storyLifecycle.emerging / newsVelocityAnalysis.totalStories) * 100, 5)}%` }}>
                                      <span>Emerging: {newsVelocityAnalysis.storyLifecycle.emerging}</span>
                                    </div>
                                  )}
                                  {newsVelocityAnalysis.storyLifecycle.declining > 0 && (
                                    <div className="lifecycle-segment lifecycle-declining" style={{ width: `${Math.max((newsVelocityAnalysis.storyLifecycle.declining / newsVelocityAnalysis.totalStories) * 100, 5)}%` }}>
                                      <span>Declining: {newsVelocityAnalysis.storyLifecycle.declining}</span>
                                    </div>
                                  )}
                                  {newsVelocityAnalysis.storyLifecycle.breaking === 0 &&
                                    newsVelocityAnalysis.storyLifecycle.peak === 0 &&
                                    newsVelocityAnalysis.storyLifecycle.emerging === 0 &&
                                    newsVelocityAnalysis.storyLifecycle.declining === 0 && (
                                      <div style={{ padding: '12px', textAlign: 'center', color: '#64748b', width: '100%' }}>No lifecycle data</div>
                                    )}
                                </>
                              ) : (
                                <div style={{ padding: '12px', textAlign: 'center', color: '#64748b', width: '100%' }}>No stories to analyze</div>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Velocity by Platform */}
                      <div className="meltwater-card">
                        <h3>Velocity by Platform</h3>
                        {newsVelocityAnalysis.velocityByPlatform && Object.keys(newsVelocityAnalysis.velocityByPlatform).length > 0 ? (
                          <div className="platform-velocity-list">
                            {Object.entries(newsVelocityAnalysis.velocityByPlatform).map(([platform, data]) => (
                              <div key={platform} className="platform-velocity-item">
                                <div className="platform-velocity-header">
                                  <span className="platform-velocity-name">{platform}</span>
                                  <span className="platform-velocity-score">{data.avgVelocityScore.toFixed(1)}</span>
                                </div>
                                <div className="platform-velocity-metrics">
                                  <span>Avg Velocity: {data.avgVelocity.toFixed(1)}</span>
                                  <span>Avg Growth: {data.avgGrowth.toFixed(1)}%</span>
                                  <span className="breakout-badge">{data.breakoutCount} breakouts</span>
                                </div>
                                <div className="platform-velocity-bar">
                                  <div
                                    className="velocity-bar-fill"
                                    style={{ width: `${Math.min((data.avgVelocityScore / 10) * 100, 100)}%` }}
                                  ></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                            <p>No platform data available.</p>
                          </div>
                        )}
                      </div>

                      {/* Top Stories by Velocity */}
                      {newsVelocityAnalysis.topStories && newsVelocityAnalysis.topStories.length > 0 ? (
                        <div className="meltwater-card">
                          <h3>Top Stories by Velocity</h3>
                          <div className="top-stories-list">
                            {newsVelocityAnalysis.topStories.slice(0, 10).map((story, idx) => (
                              <div key={story.key} className="story-item">
                                <div className="story-header">
                                  <span className="story-rank">#{idx + 1}</span>
                                  <span className="story-topic">{story.topic}</span>
                                  <span className={`story-lifecycle-badge lifecycle-${story.lifecycle}`}>
                                    {story.lifecycle}
                                  </span>
                                </div>
                                <div className="story-metrics">
                                  <div className="story-metric">
                                    <span className="metric-label">Velocity:</span>
                                    <span className="metric-value">{story.avgVelocity.toFixed(1)}</span>
                                  </div>
                                  <div className="story-metric">
                                    <span className="metric-label">Growth:</span>
                                    <span className="metric-value">{story.avgGrowth.toFixed(1)}%</span>
                                  </div>
                                  <div className="story-metric">
                                    <span className="metric-label">Score:</span>
                                    <span className="metric-value">{story.velocityScore.toFixed(1)}</span>
                                  </div>
                                  <div className="story-metric">
                                    <span className="metric-label">Platform:</span>
                                    <span className="metric-value">{story.platform}</span>
                                  </div>
                                </div>
                                <div className="story-trends">
                                  <span className={`trend-indicator ${story.velocityTrend > 0 ? 'trend-up' : story.velocityTrend < 0 ? 'trend-down' : 'trend-neutral'}`}>
                                    {story.velocityTrend > 0 ? '↑' : story.velocityTrend < 0 ? '↓' : '→'} Velocity
                                  </span>
                                  <span className={`trend-indicator ${story.growthTrend > 0 ? 'trend-up' : story.growthTrend < 0 ? 'trend-down' : 'trend-neutral'}`}>
                                    {story.growthTrend > 0 ? '↑' : story.growthTrend < 0 ? '↓' : '→'} Growth
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="meltwater-card">
                          <h3>Top Stories by Velocity</h3>
                          <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                            <p>No stories available for ranking.</p>
                          </div>
                        </div>
                      )}

                      {/* Story Breakouts */}
                      {newsVelocityAnalysis.breakoutStories && newsVelocityAnalysis.breakoutStories.length > 0 ? (
                        <div className="meltwater-card meltwater-card--breakouts">
                          <div className="breakouts-header">
                            <h3>Story Breakouts</h3>
                            <div className="breakouts-badge">
                              {newsVelocityAnalysis.breakoutStories.length} {newsVelocityAnalysis.breakoutStories.length === 1 ? 'Breakout' : 'Breakouts'}
                            </div>
                          </div>
                          <div className="breakouts-list">
                            {newsVelocityAnalysis.breakoutStories.map(breakout => (
                              <div key={breakout.id} className={`breakout-item breakout-${breakout.severity}`}>
                                <div className="breakout-icon">
                                  {breakout.severity === 'critical' ? '🚨' : '📈'}
                                </div>
                                <div className="breakout-content">
                                  <div className="breakout-header">
                                    <span className="breakout-topic">{breakout.topic}</span>
                                    <span className="breakout-severity">{breakout.severity}</span>
                                  </div>
                                  <div className="breakout-details">
                                    <span>{breakout.platform}</span>
                                    <span>·</span>
                                    <span>Velocity: {breakout.maxVelocity.toFixed(1)}</span>
                                    <span>·</span>
                                    <span>Growth: {breakout.maxGrowth.toFixed(1)}%</span>
                                  </div>
                                  <div className="breakout-metrics">
                                    <span>Max Posts: {breakout.maxPosts.toLocaleString()}</span>
                                    <span>Max Views: {breakout.maxViews.toLocaleString()}</span>
                                    <span className="breakout-score">Score: {breakout.velocityScore.toFixed(1)}</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="meltwater-card">
                          <h3>Story Breakouts</h3>
                          <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                            <p>No story breakouts detected.</p>
                            <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>
                              Breakouts are detected when stories show sudden spikes in velocity, growth, posts, or views.
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Active Breakout Alerts */}
                      {breakoutAlerts.length > 0 && (
                        <div className="meltwater-card meltwater-card--alerts">
                          <div className="breakout-alerts-header">
                            <h3>Active Breakout Alerts</h3>
                            <button
                              onClick={() => setBreakoutAlerts(prev => prev.map(a => ({ ...a, read: true })))}
                              className="mark-all-read-btn"
                            >
                              Mark All Read
                            </button>
                          </div>
                          <div className="breakout-alerts-list">
                            {breakoutAlerts.slice(0, 15).map(alert => (
                              <div key={alert.id} className={`breakout-alert-item ${alert.read ? 'read' : 'unread'}`}>
                                <div className="breakout-alert-icon">
                                  {alert.severity === 'critical' ? '🚨' : '📈'}
                                </div>
                                <div className="breakout-alert-content">
                                  <div className="breakout-alert-header">
                                    <span className="breakout-alert-topic">{alert.topic}</span>
                                    <span className="breakout-alert-time">
                                      {new Date(alert.timestamp || Date.now()).toLocaleString()}
                                    </span>
                                  </div>
                                  <div className="breakout-alert-message">
                                    {alert.message || 'Breakout detected'}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Velocity by Platform */}
                      <div className="meltwater-card">
                        <h3>Velocity by Platform</h3>
                        {newsVelocityAnalysis.velocityByPlatform && Object.keys(newsVelocityAnalysis.velocityByPlatform).length > 0 ? (
                          <div className="platform-velocity-list">
                            {Object.entries(newsVelocityAnalysis.velocityByPlatform).map(([platform, data]) => (
                              <div key={platform} className="platform-velocity-item">
                                <div className="platform-velocity-header">
                                  <span className="platform-velocity-name">{platform}</span>
                                  <span className="platform-velocity-score">{data.avgVelocityScore.toFixed(1)}</span>
                                </div>
                                <div className="platform-velocity-metrics">
                                  <span>Avg Velocity: {data.avgVelocity.toFixed(1)}</span>
                                  <span>Avg Growth: {data.avgGrowth.toFixed(1)}%</span>
                                  <span className="breakout-badge">{data.breakoutCount} breakouts</span>
                                </div>
                                <div className="platform-velocity-bar">
                                  <div
                                    className="velocity-bar-fill"
                                    style={{ width: `${Math.min((data.avgVelocityScore / 10) * 100, 100)}%` }}
                                  ></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                            <p>No platform data available.</p>
                          </div>
                        )}
                      </div>

                      {/* Top Stories by Velocity */}
                      {newsVelocityAnalysis.topStories && newsVelocityAnalysis.topStories.length > 0 ? (
                        <div className="meltwater-card">
                          <h3>Top Stories by Velocity</h3>
                          <div className="top-stories-list">
                            {newsVelocityAnalysis.topStories.slice(0, 10).map((story, idx) => (
                              <div key={story.key} className="story-item">
                                <div className="story-header">
                                  <span className="story-rank">#{idx + 1}</span>
                                  <span className="story-topic">{story.topic}</span>
                                  <span className={`story-lifecycle-badge lifecycle-${story.lifecycle}`}>
                                    {story.lifecycle}
                                  </span>
                                </div>
                                <div className="story-metrics">
                                  <div className="story-metric">
                                    <span className="metric-label">Velocity:</span>
                                    <span className="metric-value">{story.avgVelocity.toFixed(1)}</span>
                                  </div>
                                  <div className="story-metric">
                                    <span className="metric-label">Growth:</span>
                                    <span className="metric-value">{story.avgGrowth.toFixed(1)}%</span>
                                  </div>
                                  <div className="story-metric">
                                    <span className="metric-label">Score:</span>
                                    <span className="metric-value">{story.velocityScore.toFixed(1)}</span>
                                  </div>
                                  <div className="story-metric">
                                    <span className="metric-label">Platform:</span>
                                    <span className="metric-value">{story.platform}</span>
                                  </div>
                                </div>
                                <div className="story-trends">
                                  <span className={`trend-indicator ${story.velocityTrend > 0 ? 'trend-up' : story.velocityTrend < 0 ? 'trend-down' : 'trend-neutral'}`}>
                                    {story.velocityTrend > 0 ? '↑' : story.velocityTrend < 0 ? '↓' : '→'} Velocity
                                  </span>
                                  <span className={`trend-indicator ${story.growthTrend > 0 ? 'trend-up' : story.growthTrend < 0 ? 'trend-down' : 'trend-neutral'}`}>
                                    {story.growthTrend > 0 ? '↑' : story.growthTrend < 0 ? '↓' : '→'} Growth
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="meltwater-card">
                          <h3>Top Stories by Velocity</h3>
                          <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                            <p>No stories available for ranking.</p>
                          </div>
                        </div>
                      )}

                      {/* Story Breakouts */}
                      {newsVelocityAnalysis.breakoutStories && newsVelocityAnalysis.breakoutStories.length > 0 ? (
                        <div className="meltwater-card meltwater-card--breakouts">
                          <div className="breakouts-header">
                            <h3>Story Breakouts</h3>
                            <div className="breakouts-badge">
                              {newsVelocityAnalysis.breakoutStories.length} {newsVelocityAnalysis.breakoutStories.length === 1 ? 'Breakout' : 'Breakouts'}
                            </div>
                          </div>
                          <div className="breakouts-list">
                            {newsVelocityAnalysis.breakoutStories.map(breakout => (
                              <div key={breakout.id} className={`breakout-item breakout-${breakout.severity}`}>
                                <div className="breakout-icon">
                                  {breakout.severity === 'critical' ? '🚨' : '📈'}
                                </div>
                                <div className="breakout-content">
                                  <div className="breakout-header">
                                    <span className="breakout-topic">{breakout.topic}</span>
                                    <span className="breakout-severity">{breakout.severity}</span>
                                  </div>
                                  <div className="breakout-details">
                                    <span>{breakout.platform}</span>
                                    <span>·</span>
                                    <span>Velocity: {breakout.maxVelocity.toFixed(1)}</span>
                                    <span>·</span>
                                    <span>Growth: {breakout.maxGrowth.toFixed(1)}%</span>
                                  </div>
                                  <div className="breakout-metrics">
                                    <span>Max Posts: {breakout.maxPosts.toLocaleString()}</span>
                                    <span>Max Views: {breakout.maxViews.toLocaleString()}</span>
                                    <span className="breakout-score">Score: {breakout.velocityScore.toFixed(1)}</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      ) : (
                        <div className="meltwater-card">
                          <h3>Story Breakouts</h3>
                          <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                            <p>No story breakouts detected.</p>
                            <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>
                              Breakouts are detected when stories show sudden spikes in velocity, growth, posts, or views.
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Active Breakout Alerts */}
                      {breakoutAlerts.length > 0 && (
                        <div className="meltwater-card meltwater-card--alerts">
                          <div className="breakout-alerts-header">
                            <h3>Active Breakout Alerts</h3>
                            <button
                              onClick={() => setBreakoutAlerts(prev => prev.map(a => ({ ...a, read: true })))}
                              className="mark-all-read-btn"
                            >
                              Mark All Read
                            </button>
                          </div>
                          <div className="breakout-alerts-list">
                            {breakoutAlerts.slice(0, 15).map(alert => (
                              <div key={alert.id} className={`breakout-alert-item ${alert.read ? 'read' : 'unread'}`}>
                                <div className="breakout-alert-icon">
                                  {alert.severity === 'critical' ? '🚨' : '📈'}
                                </div>
                                <div className="breakout-alert-content">
                                  <div className="breakout-alert-header">
                                    <span className="breakout-alert-topic">{alert.topic}</span>
                                    <span className="breakout-alert-time">
                                      {new Date(alert.createdAt || alert.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                  <div className="breakout-alert-details">
                                    {alert.platform} · Velocity: {alert.maxVelocity.toFixed(1)} · Growth: {alert.maxGrowth.toFixed(1)}%
                                  </div>
                                </div>
                                <button
                                  onClick={() => setBreakoutAlerts(prev => prev.map(a => a.id === alert.id ? { ...a, read: true } : a))}
                                  className="mark-read-btn"
                                >
                                  {alert.read ? '✓' : 'Mark Read'}
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="meltwater-card">
                      <h3>News Velocity Analysis</h3>
                      <div style={{ padding: '20px', textAlign: 'center', color: '#64748b' }}>
                        <p>Analyzing story velocity and breakout patterns...</p>
                        <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>
                          Tracking story lifecycle, velocity trends, and detecting breakouts.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Trending Hashtags Section - Show if there are hashtags */}
            {(hashtags.length > 0 || Object.keys(hashtagsWithUrls).length > 0) && (
              <div className="trending-section" style={{ display: showHashtagsPanel ? 'block' : 'none' }}>
                <div className="section-header">
                  <h2>🔥 Trending Hashtags by Platform</h2>
                  <button
                    onClick={() => setShowHashtagsPanel(!showHashtagsPanel)}
                    className="toggle-btn"
                  >
                    {showHashtagsPanel ? '🔽 Hide' : '🔼 Show'}
                  </button>
                </div>

                {Object.keys(hashtagsWithUrls).length > 0 ? (
                  <>
                    {Object.entries(hashtagsWithUrls).map(([platform, hashtagList]) => {
                      const platformLogo = getPlatformLogo(platform)
                      return (
                        <div key={platform} className="platform-trending-section">
                          <div className="platform-header">
                            <img
                              src={platformLogo}
                              alt=""
                              className="platform-logo"
                              aria-hidden="true"
                              onError={(e) => {
                                e.target.style.display = 'none'
                              }}
                            />
                            <h3>{platform}</h3>
                            <span className="trending-badge">{hashtagList.length} trending</span>
                          </div>
                          <div className="trending-grid">
                            {hashtagList.length > 0 ? (
                              hashtagList.map((item, idx) => {
                                return (
                                  <div key={idx} className="trending-card">
                                    <div className="trending-rank">#{idx + 1}</div>
                                    <div className="trending-content">
                                      <span
                                        className="trending-hashtag"
                                        onClick={() => setSearchTerm(item.hashtag)}
                                        style={{ display: 'inline-block', minWidth: '120px', wordBreak: 'break-word' }}
                                        title={`Click to search for #${item.hashtag}`}
                                      >
                                        #{item.hashtag}
                                      </span>
                                      {item.url && (
                                        <a
                                          href={item.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="trending-link"
                                          title={item.url}
                                        >
                                          🔗
                                        </a>
                                      )}
                                    </div>
                                    <div className="trending-fire">🔥</div>
                                  </div>
                                )
                              })
                            ) : (
                              <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                No hashtags found for {platform}
                              </div>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </>
                ) : (
                  <div className="hashtags-grid">
                    {hashtags.length > 0 ? (
                      hashtags.map((tag, idx) => (
                        <div key={idx} className="trending-card">
                          <div className="trending-rank">#{idx + 1}</div>
                          <span
                            className="trending-hashtag"
                            onClick={() => {
                              setSearchTerm(tag)
                            }}
                            style={{ display: 'inline-block', minWidth: '120px', wordBreak: 'break-word' }}
                            title={`Click to search for #${tag}`}
                          >
                            #{tag}
                          </span>
                          <div className="trending-fire">🔥</div>
                        </div>
                      ))
                    ) : (
                      <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                        No hashtags found in the data
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Content Display - Cards or Table */}
            {viewMode === 'cards' && data.length > 0 && (
              <div className="cards-view">
                <div className="cards-grid">
                  {filteredData.slice(0, 24).map((row, index) => {
                    const topic = row.Topic || row.topic || ''
                    const engagement = row.Engagement_score || row.engagement_score || 0
                    const posts = row.Posts || row.posts || 0
                    const views = row.Views || row.views || 0
                    const sentiment = row.Sentiment_label || row.sentiment_label || 'Neutral'
                    const platform = row.Platform || row.platform || 'Unknown'

                    // Get hashtags from the trending section for this platform (to match what's shown in trending)
                    const normalizedPlatform = platform.toLowerCase().trim()
                    let platformHashtags = []

                    // Find matching platform in hashtagsWithUrls
                    for (const [platformKey, hashtagList] of Object.entries(hashtagsWithUrls)) {
                      const normalizedKey = platformKey.toLowerCase().trim()
                      if (normalizedKey === normalizedPlatform ||
                        (normalizedPlatform.includes('twitter') && normalizedKey.includes('twitter')) ||
                        (normalizedPlatform.includes('x') && normalizedKey.includes('twitter'))) {
                        platformHashtags = hashtagList.map(item => item.hashtag)
                        break
                      }
                    }

                    // Extract hashtags from topic to check if topic already contains hashtags
                    const extractHashtagsFromText = (text) => {
                      if (!text) return []
                      const matches = String(text).match(/#[\w]+/g)
                      return matches ? matches.map(tag => tag.substring(1)) : []
                    }
                    const topicHashtags = extractHashtagsFromText(topic)
                    const topicHashtagSet = new Set(topicHashtags.map(tag => tag.toLowerCase()))

                    // If no trending hashtags found for this platform, extract from row data as fallback
                    if (platformHashtags.length === 0) {
                      const supplementalTags = new Map()

                      // Also check column 'C' and other hashtag columns
                      Object.entries(row).forEach(([columnName, value]) => {
                        const columnLower = columnName.toLowerCase()
                        const isHashtagColumn = columnLower === 'c' ||
                          columnLower === 'hashtags' ||
                          columnLower === 'keywords' ||
                          columnLower === 'tags' ||
                          columnLower.includes('hashtag') ||
                          columnLower.includes('keyword') ||
                          columnLower.includes('tag')

                        if (isHashtagColumn) {
                          if (Array.isArray(value)) {
                            value.forEach(item => {
                              if (typeof item === 'string' && item.trim()) {
                                const cleanTagRaw = item.replace('#', '').trim()
                                const normalized = cleanTagRaw.toLowerCase()
                                if (normalized && !topicHashtagSet.has(normalized) && !supplementalTags.has(normalized)) {
                                  supplementalTags.set(normalized, cleanTagRaw)
                                }
                              }
                            })
                          } else if (typeof value === 'string' && value.trim()) {
                            const cleanTagRaw = value.replace('#', '').trim()
                            const normalized = cleanTagRaw.toLowerCase()
                            if (normalized && !topicHashtagSet.has(normalized) && !supplementalTags.has(normalized)) {
                              supplementalTags.set(normalized, cleanTagRaw)
                            }
                          }
                        }
                      })
                      platformHashtags = [...topicHashtags, ...Array.from(supplementalTags.values())]
                    }

                    // Only show hashtags in the "Hashtags:" section if the topic doesn't already contain hashtags
                    // This prevents duplication - if topic is "#ole #acl", we don't need a separate "Hashtags:" section
                    const hasHashtagsInTopic = topicHashtags.length > 0

                    // Only show the "Hashtags:" section if topic doesn't have hashtags
                    // If topic has hashtags, they're already visible in the card-topic, so no need to duplicate
                    const cardHashtags = !hasHashtagsInTopic && platformHashtags.length > 0
                      ? [platformHashtags[index % platformHashtags.length]].filter(Boolean)
                      : []

                    const platformLogo = getPlatformLogo(platform)

                    return (
                      <div key={index} className="content-card">
                        <div className="card-header">
                          <div className="card-rank">#{index + 1}</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <img
                              src={platformLogo}
                              alt=""
                              className="platform-logo platform-logo--compact"
                              aria-hidden="true"
                            />
                            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{platform}</span>
                            <div className="card-trending">🔥 Trending</div>
                          </div>
                        </div>
                        <div className="card-content">
                          <div className="card-topic">
                            {formatCellValue(topic, 'topic')}
                          </div>
                          {cardHashtags.length > 0 && (
                            <div style={{ marginTop: '15px', marginBottom: '15px' }}>
                              <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#666', marginBottom: '8px' }}>
                                Hashtags:
                              </div>
                              <div className="tags-container">
                                {cardHashtags.map((tag, idx) => (
                                  <span
                                    key={idx}
                                    className="tag"
                                    onClick={() => {
                                      setSearchTerm(tag)
                                    }}
                                    style={{ cursor: 'pointer' }}
                                  >
                                    #{tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          <div className="card-metrics">
                            {engagement > 0 && (
                              <div className="metric">
                                <span className="metric-icon">📈</span>
                                <span className="metric-value">{engagement}</span>
                                <span className="metric-label">Engagement</span>
                              </div>
                            )}
                            {posts > 0 && (
                              <div className="metric">
                                <span className="metric-icon">📝</span>
                                <span className="metric-value">{posts.toLocaleString()}</span>
                                <span className="metric-label">Posts</span>
                              </div>
                            )}
                            {views > 0 && (
                              <div className="metric">
                                <span className="metric-icon">👁️</span>
                                <span className="metric-value">{views.toLocaleString()}</span>
                                <span className="metric-label">Views</span>
                              </div>
                            )}
                          </div>
                          <div className="card-sentiment">
                            <span className={`sentiment-badge ${sentiment.toLowerCase()}`}>
                              {sentiment}
                            </span>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {viewMode === 'table' && (
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      {(() => {
                        // Get all columns and filter out id and platform
                        const allColumns = Object.keys(data[0] || {})
                        const visibleColumns = allColumns.filter(key => {
                          const lowerKey = key.toLowerCase()
                          return lowerKey !== 'id' && lowerKey !== 'platform'
                        })

                        // Reorder to put Topic first if it exists
                        const topicColumn = visibleColumns.find(k => k.toLowerCase() === 'topic')
                        const otherColumns = visibleColumns.filter(k => k.toLowerCase() !== 'topic')
                        const orderedColumns = topicColumn ? [topicColumn, ...otherColumns] : visibleColumns

                        return orderedColumns.map((key) => (
                          <th
                            key={key}
                            onClick={() => handleSort(key)}
                            className="sortable-header"
                            title="Click to sort"
                          >
                            {key}
                            {sortConfig.key === key && (
                              <span className="sort-indicator">
                                {sortConfig.direction === 'asc' ? ' ↑' : ' ↓'}
                              </span>
                            )}
                          </th>
                        ))
                      })()}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.map((row, index) => {
                      // Get filtered keys in the same order as headers
                      const allColumns = Object.keys(data[0] || {})
                      const visibleColumns = allColumns.filter(key => {
                        const lowerKey = key.toLowerCase()
                        return lowerKey !== 'id' && lowerKey !== 'platform'
                      })

                      // Reorder to put Topic first if it exists (same as header)
                      const topicColumn = visibleColumns.find(k => k.toLowerCase() === 'topic')
                      const otherColumns = visibleColumns.filter(k => k.toLowerCase() !== 'topic')
                      const orderedColumns = topicColumn ? [topicColumn, ...otherColumns] : visibleColumns

                      return (
                        <tr key={index}>
                          {orderedColumns.map((key, cellIndex) => (
                            <td key={`${index}-${key}-${cellIndex}`}>
                              {formatCellValue(row[key], key)}
                            </td>
                          ))}
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}

            {viewMode === 'calendar' && calendarData.length > 0 && (
              <div className="calendar-view">
                <div className="calendar-header">
                  <div>
                    <h2>Sprout Social Publishing Calendar</h2>
                    <p>
                      Ergonomic weekboard auto-filled with velocity-weighted slots for{' '}
                      <strong>{selectedPlatform?.label || 'all platforms'}</strong>.
                    </p>
                  </div>
                  <span className="calendar-tag">Publishing UX</span>
                </div>
                <div className="calendar-grid">
                  {calendarData.map(day => (
                    <div key={day.id} className="calendar-day">
                      <div className="calendar-day-header">
                        <span className="calendar-day-name">{day.dayName}</span>
                        <span className="calendar-day-date">{day.dateLabel}</span>
                      </div>
                      <div className="calendar-slot-list">
                        {day.slots.map((slot, idx) => (
                          <div
                            key={`${day.id}-${idx}-${slot.time}`}
                            className={`calendar-slot calendar-slot--${slot.status || 'neutral'}`}
                          >
                            <div className="calendar-slot-time">{slot.time}</div>
                            <div className="calendar-slot-topic">{slot.topic}</div>
                            <div className="calendar-slot-meta">
                              <span className="calendar-slot-platform">{slot.platform}</span>
                              {(slot.velocity || slot.growthPct) ? (
                                <span className="calendar-slot-stats">
                                  ⚡ {Number(slot.velocity || 0).toFixed(1)} · 📈 {Number(slot.growthPct || 0).toFixed(1)}%
                                </span>
                              ) : (
                                <span className="calendar-slot-status">Ready for assignment</span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
                <p className="calendar-footnote">
                  Quick-glance slots with velocity signals and ready status cues for campaign planning.
                </p>
              </div>
            )}
          </>
        )}

        {!error && data.length > 0 && (
          <div className="stats">
            <p>
              Showing <strong>{filteredData.length}</strong> of <strong>{data.length}</strong> records
              {searchTerm && <span className="search-info"> (filtered by "{searchTerm}")</span>}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

