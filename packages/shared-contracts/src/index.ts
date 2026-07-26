import { z } from "zod";

// Shared Enums and Constants
export enum TradeDirection {
  BUY = "BUY",
  SELL = "SELL"
}

export const TradeDirectionSchema = z.nativeEnum(TradeDirection);

export enum SignalStatus {
  RECEIVED = "RECEIVED",
  PARSED = "PARSED",
  INVALID = "INVALID",
  WAITING_FOR_TP = "WAITING_FOR_TP",
  AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION",
  PLANNED = "PLANNED",
  PLACING_ORDERS = "PLACING_ORDERS",
  PARTIALLY_PLACED = "PARTIALLY_PLACED",
  PENDING = "PENDING",
  PARTIALLY_FILLED = "PARTIALLY_FILLED",
  OPEN = "OPEN",
  MANAGING = "MANAGING",
  CLOSING = "CLOSING",
  CLOSED = "CLOSED",
  CANCELLED = "CANCELLED",
  REJECTED = "REJECTED",
  FAILED = "FAILED"
}

export const SignalStatusSchema = z.nativeEnum(SignalStatus);

export enum ExecutionMode {
  AUTO = "AUTO",
  CONFIRMATION = "CONFIRMATION"
}

export const ExecutionModeSchema = z.nativeEnum(ExecutionMode);

export enum OrderType {
  BUY_LIMIT = "BUY_LIMIT",
  SELL_LIMIT = "SELL_LIMIT"
}

export const OrderTypeSchema = z.nativeEnum(OrderType);

// Domain Schemas
export const SignalSchema = z.object({
  id: z.string().uuid(),
  instrument: z.string().default("XAUUSD"),
  direction: TradeDirectionSchema,
  entryRangeLow: z.number().positive(),
  entryRangeHigh: z.number().positive(),
  stopLoss: z.number().positive().optional(),
  takeProfits: z.array(z.number().positive()),
  rawMessage: z.string(),
  createdAt: z.date()
});

export type Signal = z.infer<typeof SignalSchema>;

export const CampaignSchema = z.object({
  id: z.string().uuid(),
  campaignCode: z.string(),
  signalId: z.string().uuid(),
  parentCampaignId: z.string().uuid().optional(),
  reentrySequence: z.number().int().default(0),
  magicNumber: z.number().int(),
  currentState: SignalStatusSchema,
  executionMode: ExecutionModeSchema,
  entryCount: z.number().int().default(5),
  lotPerEntry: z.number().positive().default(0.30),
  totalVolume: z.number().positive().default(1.50),
  maximumTotalLots: z.number().positive().default(2.00),
  requestedTotalLots: z.number().positive().default(1.50),
  currentStopLoss: z.number().positive().optional(),
  tp1: z.number().positive().optional(),
  tp2: z.number().positive().optional(),
  hasTpOpen: z.boolean().default(false),
  version: z.number().int().default(1),
  tradingEnabled: z.boolean().default(false),
  executionPerformed: z.boolean().default(false),
  createdAt: z.date(),
  updatedAt: z.date()
});

export type Campaign = z.infer<typeof CampaignSchema>;

export const WhatsAppMessageEnvelopeSchema = z.object({
  messageId: z.string().min(1),
  groupId: z.string().min(1),
  senderId: z.string().min(1),
  rawContent: z.string().min(1).max(10000),
  receivedAt: z.string(),
  idempotencyKey: z.string().min(1),
  workerId: z.string().default("openwa-worker-01"),
  adapterMode: z.enum(["fake", "real"]).default("fake")
});

export type WhatsAppMessageEnvelope = z.infer<typeof WhatsAppMessageEnvelopeSchema>;

// Symbol Specification Schema
export const SymbolSpecificationSchema = z.object({
  canonical_symbol: z.string().default("XAUUSD"),
  broker_symbol: z.string().default("XAUUSD"),
  digits: z.number().int().default(2),
  point: z.string().default("0.0100"),
  tick_size: z.string().default("0.0100"),
  volume_min: z.string().default("0.0100"),
  volume_max: z.string().default("100.0000"),
  volume_step: z.string().default("0.0100"),
  stops_level_points: z.number().int().default(0),
  freeze_level_points: z.number().int().default(0),
  trade_mode: z.string().default("FULL"),
  contract_size: z.string().default("100.0000"),
  source: z.string().default("TEST_FIXTURE"),
  captured_at: z.string()
});

export type SymbolSpecification = z.infer<typeof SymbolSpecificationSchema>;

export const PlannedEntryDetailSchema = z.object({
  entry_sequence: z.number().int(),
  ladder_index: z.number().int(),
  planned_price: z.string(),
  normalized_price: z.string(),
  lot_size: z.string(),
  stop_loss: z.string(),
  take_profit: z.string().nullable(),
  tp_category: z.enum(["TP_100", "TP_1", "TP_2"]),
  order_type: OrderTypeSchema,
  magic_number: z.number().int(),
  order_comment: z.string(),
  status: z.literal("PLANNED")
});

export type PlannedEntryDetail = z.infer<typeof PlannedEntryDetailSchema>;

// App Settings Schema
export const AppSettingsSchema = z.object({
  entryCount: z.number().int().min(3).max(8).default(5),
  lotPerEntry: z.number().positive().default(0.30),
  maxExposureLots: z.number().positive().max(2.00).default(2.00),
  executionMode: ExecutionModeSchema.default(ExecutionMode.CONFIRMATION),
  targetGroupJid: z.string().optional(),
  adminSenderJid: z.string().optional()
});

export type AppSettings = z.infer<typeof AppSettingsSchema>;

// MT5 Adapter & Worker Schemas
export const Mt5AdapterModeSchema = z.enum(["fake", "dry_run", "real"]);
export type Mt5AdapterMode = z.infer<typeof Mt5AdapterModeSchema>;

export const Mt5HealthStateSchema = z.enum([
  "DISABLED", "NOT_INSTALLED", "NOT_INITIALIZED", "INITIALIZING",
  "CONNECTED", "READY", "DEGRADED", "BLOCKED_LIVE_ACCOUNT",
  "BLOCKED_NON_HEDGING", "BLOCKED_ACCOUNT_NOT_ALLOWED",
  "BLOCKED_SERVER_NOT_ALLOWED", "BLOCKED_SYMBOL_NOT_FOUND",
  "BLOCKED_SYMBOL_AMBIGUOUS", "TRADING_NOT_ALLOWED", "ERROR", "SHUTTING_DOWN"
]);
export type Mt5HealthState = z.infer<typeof Mt5HealthStateSchema>;

export const Mt5StatusSchema = z.object({
  adapter_mode: Mt5AdapterModeSchema.default("fake"),
  health_state: Mt5HealthStateSchema.default("NOT_INITIALIZED"),
  execution_enabled: z.boolean().default(false),
  demo_only: z.literal(true).default(true),
  live_execution_enabled: z.literal(false).default(false),
  trading_enabled: z.boolean().default(false),
  account_connected: z.boolean().default(false),
  account_environment: z.enum(["DEMO", "CONTEST", "REAL", "UNKNOWN"]).default("DEMO"),
  margin_mode: z.enum(["HEDGING", "NETTING", "EXCHANGE", "UNKNOWN"]).default("HEDGING"),
  resolved_symbol: z.string().nullable().default("XAUUSD")
});
export type Mt5Status = z.infer<typeof Mt5StatusSchema>;

export const Mt5ExecutionPreflightResultSchema = z.object({
  campaign_id: z.string(),
  is_ready: z.boolean(),
  checks_passed: z.array(z.string()),
  blocking_reasons: z.array(z.string())
});
export type Mt5ExecutionPreflightResult = z.infer<typeof Mt5ExecutionPreflightResultSchema>;

export const Mt5CampaignExecutionRequestSchema = z.object({
  expected_version: z.number().int(),
  planning_fingerprint: z.string(),
  explicit_user_confirm: z.literal(true).default(true)
});
export type Mt5CampaignExecutionRequest = z.infer<typeof Mt5CampaignExecutionRequestSchema>;

export const Mt5CampaignExecutionResultSchema = z.object({
  campaign_id: z.string(),
  batch_id: z.string(),
  status: z.string(),
  queued_jobs_count: z.number().int()
});
export type Mt5CampaignExecutionResult = z.infer<typeof Mt5CampaignExecutionResultSchema>;

// Phase 9 Orchestration, Control & Event Schemas
export const AutomationStateSchema = z.enum(["PAUSED", "RUNNING", "EMERGENCY_STOPPED"]);
export type AutomationState = z.infer<typeof AutomationStateSchema>;

export const SystemStatusSchema = z.object({
  system_status_contract_version: z.string().default("1.0.0"),
  overall_state: z.enum(["HEALTHY", "DEGRADED", "BLOCKED", "ERROR", "STARTING", "STOPPED"]).default("HEALTHY"),
  automation_state: AutomationStateSchema.default("PAUSED"),
  default_execution_mode: ExecutionModeSchema.default(ExecutionMode.CONFIRMATION),
  trading_enabled: z.boolean().default(false),
  mt5_execution_enabled: z.boolean().default(false),
  mt5_account_environment: z.string().default("DEMO"),
  mt5_margin_mode: z.string().default("HEDGING"),
  whatsapp_worker_state: z.string().default("READY"),
  whatsapp_spool_pending: z.number().int().default(0),
  active_campaign_count: z.number().int().default(0),
  awaiting_confirmation_count: z.number().int().default(0),
  waiting_for_tp_count: z.number().int().default(0),
  queued_mt5_jobs: z.number().int().default(0),
  outbox_pending: z.number().int().default(0),
  latest_event_sequence: z.number().int().default(0),
  updated_at: z.string()
});
export type SystemStatus = z.infer<typeof SystemStatusSchema>;

export const ControlStateSchema = z.object({
  automation_state: AutomationStateSchema.default("PAUSED"),
  default_execution_mode: ExecutionModeSchema.default(ExecutionMode.CONFIRMATION),
  trading_enabled: z.boolean().default(false),
  mt5_execution_enabled: z.boolean().default(false),
  orchestrator_enabled: z.boolean().default(true),
  event_dispatcher_enabled: z.boolean().default(true)
});
export type ControlState = z.infer<typeof ControlStateSchema>;

export const OrchestrationRunSchema = z.object({
  id: z.string(),
  orchestrator_version: z.string().default("1.0.0"),
  source_type: z.string(),
  source_id: z.string(),
  correlation_id: z.string(),
  causation_id: z.string().nullable().optional(),
  campaign_id: z.string().nullable().optional(),
  command_id: z.string().nullable().optional(),
  status: z.string(),
  current_step: z.string(),
  input_payload: z.record(z.any()),
  output_payload: z.record(z.any()).nullable().optional(),
  error_code: z.string().nullable().optional(),
  error_message: z.string().nullable().optional(),
  started_at: z.string(),
  completed_at: z.string().nullable().optional()
});
export type OrchestrationRun = z.infer<typeof OrchestrationRunSchema>;

export const DomainEventSchema = z.object({
  event_contract_version: z.string().default("1.0.0"),
  event_id: z.string(),
  sequence: z.number().int(),
  event_type: z.string(),
  event_version: z.string().default("1.0"),
  aggregate_type: z.string(),
  aggregate_id: z.string(),
  campaign_id: z.string().nullable().optional(),
  correlation_id: z.string(),
  causation_id: z.string().nullable().optional(),
  actor_type: z.string().default("SYSTEM"),
  actor_id: z.string().nullable().optional(),
  occurred_at: z.string(),
  payload: z.record(z.any())
});
export type DomainEvent = z.infer<typeof DomainEventSchema>;

// Phase 11 Reconciliation, Health Incidents & Recovery Schemas
export const ReconciliationItemSchema = z.object({
  id: z.string(),
  reconciliation_run_id: z.string(),
  entity_type: z.string(),
  classification: z.string(),
  ticket: z.number().int().nullable().optional(),
  magic_number: z.number().int().nullable().optional(),
  campaign_id: z.string().nullable().optional(),
  planned_entry_id: z.string().nullable().optional(),
  job_id: z.string().nullable().optional(),
  local_snapshot: z.record(z.any()).nullable().optional(),
  broker_snapshot: z.record(z.any()).nullable().optional(),
  differences: z.array(z.record(z.any())),
  requires_review: z.boolean(),
  resolution_status: z.string(),
  resolution_action: z.string().nullable().optional(),
  resolved_by: z.string().nullable().optional(),
  resolved_at: z.string().nullable().optional(),
  created_at: z.string()
});
export type ReconciliationItem = z.infer<typeof ReconciliationItemSchema>;

export const ReconciliationRunSchema = z.object({
  id: z.string(),
  reconciliation_version: z.string().default("1.0.0"),
  trigger_type: z.string().default("MANUAL"),
  scope: z.string().default("ALL"),
  campaign_id: z.string().nullable().optional(),
  correlation_id: z.string(),
  actor: z.string().default("SYSTEM"),
  status: z.string(),
  broker_symbol: z.string().nullable().optional(),
  local_order_count: z.number().int().default(0),
  local_position_count: z.number().int().default(0),
  broker_order_count: z.number().int().default(0),
  broker_position_count: z.number().int().default(0),
  matched_count: z.number().int().default(0),
  mismatch_count: z.number().int().default(0),
  requires_review_count: z.number().int().default(0),
  snapshot_summary: z.record(z.any()),
  error_message: z.string().nullable().optional(),
  started_at: z.string(),
  completed_at: z.string().nullable().optional(),
  items: z.array(ReconciliationItemSchema).default([])
});
export type ReconciliationRun = z.infer<typeof ReconciliationRunSchema>;

export const HealthIncidentSchema = z.object({
  id: z.string(),
  incident_kind: z.string(),
  severity: z.string().default("WARNING"),
  status: z.string().default("OPEN"),
  title: z.string(),
  detail: z.record(z.any()),
  occurrence_count: z.number().int().default(1),
  first_seen_at: z.string(),
  last_seen_at: z.string(),
  acknowledged_at: z.string().nullable().optional(),
  acknowledged_by: z.string().nullable().optional(),
  resolved_at: z.string().nullable().optional()
});
export type HealthIncident = z.infer<typeof HealthIncidentSchema>;

export const StartupRecoveryResultSchema = z.object({
  database_integrity: z.string().default("OK"),
  foreign_keys: z.string().default("ENABLED"),
  wal_mode: z.string().default("WAL"),
  control_state: z.record(z.any()),
  recovered_orchestration_runs_count: z.number().int().default(0),
  recovered_outbox_rows_count: z.number().int().default(0),
  recovered_execution_jobs_count: z.number().int().default(0),
  recovered_spool_files_count: z.number().int().default(0),
  recovery_actions: z.array(z.record(z.any())).default([]),
  recovery_completed_at: z.string()
});
export type StartupRecoveryResult = z.infer<typeof StartupRecoveryResultSchema>;
