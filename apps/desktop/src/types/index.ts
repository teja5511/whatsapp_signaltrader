export type AutomationState = "PAUSED" | "RUNNING" | "EMERGENCY_STOPPED";
export type ExecutionMode = "CONFIRMATION" | "AUTOMATIC";
export type RealtimeStatus = "DISCONNECTED" | "CONNECTING" | "CONNECTED_WS" | "CONNECTED_SSE" | "POLLING" | "REPLAYING" | "DEGRADED" | "ERROR";

export interface SystemStatus {
  service: string;
  version: string;
  overall_state: string;
  automation_state: AutomationState;
  execution_mode: ExecutionMode;
  trading_enabled: boolean;
  database: {
    connected: boolean;
    backend: string;
    pending_migrations: boolean;
  };
  mt5_adapter: {
    initialized: boolean;
    adapter_mode: string;
    health_state: string;
    account_environment: string;
    login_masked: string;
    is_live_account: boolean;
    live_blocked: boolean;
  };
  whatsapp_worker: {
    connected: boolean;
    worker_enabled: boolean;
    group_configured: boolean;
    admin_configured: boolean;
  };
  outbox_queue: {
    pending_events: number;
    delivered_events: number;
    failed_events: number;
  };
}

export interface ControlState {
  automation_state: AutomationState;
  default_execution_mode: ExecutionMode;
  trading_enabled: boolean;
  mt5_execution_enabled: boolean;
  orchestrator_enabled: boolean;
  event_dispatcher_enabled: boolean;
}

export interface DomainEvent {
  event_contract_version: string;
  event_id: string;
  sequence: number;
  event_type: string;
  event_version?: string;
  aggregate_type: string;
  aggregate_id: string;
  campaign_id?: string;
  correlation_id: string;
  occurred_at: string;
  payload: Record<string, any>;
}

export interface CampaignConfirmation {
  campaign_id: string;
  campaign_code: string;
  direction: string;
  zone_low: number;
  zone_high: number;
  stop_loss: number;
  version: number;
  created_at: string;
}

export interface AmbiguousCommandConfirmation {
  id: string;
  command_id?: string;
  campaign_id?: string;
  original_text: string;
  suggested_action: string;
  match_type: string;
  candidate_count: number;
  status: string;
  expires_at?: string;
  created_at: string;
}

export interface CampaignSummary {
  id: string;
  campaign_code: string;
  state: string;
  execution_mode: string;
  direction: string;
  zone_low: number;
  zone_high: number;
  stop_loss: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Mt5Order {
  ticket: number;
  symbol: string;
  type: string;
  volume: number;
  price_open: number;
  sl: number;
  tp: number;
  campaign_id?: string;
  state: string;
}

export interface Mt5Position {
  ticket: number;
  symbol: string;
  type: string;
  volume: number;
  price_open: number;
  price_current: number;
  sl: number;
  tp: number;
  profit: number;
  campaign_id?: string;
}

export interface ExecutionJob {
  id: string;
  batch_id: string;
  campaign_id: string;
  planned_entry_id?: string;
  operation_type: string;
  status: string;
  attempt_count?: number;
  created_at: string;
}
