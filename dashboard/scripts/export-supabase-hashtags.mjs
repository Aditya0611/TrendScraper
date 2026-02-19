import { createClient } from '@supabase/supabase-js';

const SUPABASE_URL = process.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.VITE_SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  console.error('Set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY before running this script.');
  process.exit(1);
}

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
const TABLES = ['facebook', 'twitter', 'instagram', 'tiktok'];

const extractHashtags = value => {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap(extractHashtags);
  }
  if (typeof value === 'object') {
    return Object.values(value).flatMap(extractHashtags);
  }
  const matches = String(value).match(/#[\p{L}\p{N}_-]+/gu);
  return matches ? matches.map(tag => tag.replace('#', '').toLowerCase()) : [];
};

(async () => {
  for (const table of TABLES) {
    const { data, error } = await supabase.from(table).select('*');
    if (error) {
      console.error(`\n❌ ${table}: ${error.message}`);
      continue;
    }
    const hashtags = new Set();
    (data || []).forEach(row => {
      Object.values(row || {}).forEach(value => {
        extractHashtags(value).forEach(tag => hashtags.add(tag));
      });
    });

    console.log(`\n${table.toUpperCase()} (${hashtags.size} hashtags)`);
    console.log([...hashtags].map(tag => `#${tag}`).join(', ') || 'No hashtags found');
  }
})();
