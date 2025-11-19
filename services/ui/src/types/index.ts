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

export interface QuotaValidationResult {
  allowed: boolean
  remaining: number
  limit: number
  period: string
  reset_at: string
  current_usage: number
  message?: string
}

