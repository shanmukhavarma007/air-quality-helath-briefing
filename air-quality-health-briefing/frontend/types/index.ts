export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_verified: boolean;
  created_at: string;
}

export interface HealthProfile {
  id: string;
  user_id: string;
  age_bracket: string;
  conditions: string[];
  activity_level: string;
  briefing_time: string;
  timezone: string;
}

export interface UserLocation {
  id: string;
  user_id: string;
  label: string;
  latitude: number;
  longitude: number;
  address?: string;
  is_primary: boolean;
  alert_threshold: number;
}

export interface AQIData {
  aqi_value: number;
  category: string;
  hex_color: string;
  pm25?: number;
  pm10?: number;
  o3?: number;
  no2?: number;
  co?: number;
  so2?: number;
  station_name: string;
  station_distance?: number;
  last_updated: string;
}

export interface Briefing {
  id: string;
  user_id: string;
  location_id?: string;
  aqi_at_generation?: number;
  outdoor_safety?: string;
  summary: string;
  mask_recommendation?: string;
  symptom_watch: string[];
  best_time_window?: string;
  activity_guidance: string;
  historical_context?: string;
  is_cached_result: boolean;
  generated_at: string;
}

export interface QuotaStatus {
  daily_limit: number;
  remaining: number;
  resets_at: string;
}

export interface HourlyData {
  time: string;
  value: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
