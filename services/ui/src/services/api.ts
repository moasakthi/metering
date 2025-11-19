import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Get API key from localStorage or env
const getApiKey = () => {
  return localStorage.getItem('api_key') || import.meta.env.VITE_API_KEY || ''
}

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1/meter`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include API key
apiClient.interceptors.request.use((config) => {
  const apiKey = getApiKey()
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey
  }
  return config
})

export interface Event {
  id: string
  tenant_id: string
  resource: string
  feature: string
  quantity: number
  timestamp: string
  metadata?: Record<string, any>
  created_at: string
}

export interface EventFilters {
  tenant_id?: string
  resource?: string
  feature?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

export interface Aggregate {
  tenant_id: string
  resource: string
  feature: string
  window_start: string
  window_end: string
  window_type: string
  total_quantity: number
  event_count: number
}

export interface AggregateFilters {
  window_type: 'hourly' | 'daily' | 'monthly'
  start_date: string
  end_date: string
  tenant_id?: string
  resource?: string
  feature?: string
  group_by?: string
}

export interface QuotaValidationRequest {
  tenant_id: string
  resource: string
  feature: string
  quantity?: number
  period: 'hourly' | 'daily' | 'monthly' | 'yearly'
}

export interface QuotaValidationResult {
  allowed: boolean
  remaining: number
  limit: number
  period: string
  reset_at: string
  current_usage: number
  message?: string
}

export const meteringApi = {
  getEvents: (params: EventFilters) =>
    apiClient.get<{ items: Event[]; page: number; page_size: number; total: number; total_pages: number }>('/events', { params }),

  getAggregates: (params: AggregateFilters) =>
    apiClient.get<{ aggregates: Aggregate[]; summary: any }>('/aggregates', { params }),

  validateQuota: (data: QuotaValidationRequest) =>
    apiClient.post<QuotaValidationResult>('/validate', data),
}

