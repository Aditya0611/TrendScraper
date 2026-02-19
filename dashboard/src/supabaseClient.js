import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

let supabase = null

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase environment variables missing. Running in demo mode with fallback data.')
} else {
  supabase = createClient(supabaseUrl, supabaseAnonKey)
}

export { supabase }

