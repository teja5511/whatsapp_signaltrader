import { z } from "zod";

// Enums
export enum TradeDirection {
  BUY = "BUY",
  SELL = "SELL"
}

export enum ExecutionMode {
  AUTO = "AUTO",
  CONFIRMATION = "CONFIRMATION"
}

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

export enum OrderType {
  BUY_LIMIT = "BUY_LIMIT",
  SELL_LIMIT = "SELL_LIMIT",
  BUY_STOP = "BUY_STOP",
  SELL_STOP = "SELL_STOP"
}

// Zod Schemas
export const TradeDirectionSchema = z.nativeEnum(TradeDirection);
export const ExecutionModeSchema = z.nativeEnum(ExecutionMode);
export const SignalStatusSchema = z.nativeEnum(SignalStatus);
export const OrderTypeSchema = z.nativeEnum(OrderType);

// App Settings Schema
export const AppSettingsSchema = z.object({
  entryCount: z.number().int().min(3).max(8).default(5),
  lotPerEntry: z.number().positive().default(0.10),
  maxExposureLots: z.number().positive().max(2.00).default(2.00),
  executionMode: ExecutionModeSchema.default(ExecutionMode.CONFIRMATION),
  targetGroupJid: z.string().optional(),
  adminSenderJid: z.string().optional()
}).refine(
  (data) => data.entryCount * data.lotPerEntry <= data.maxExposureLots,
  {
    message: "Total volume (entryCount * lotPerEntry) must not exceed maxExposureLots (2.00 lots max)",
    path: ["lotPerEntry"]
  }
);

export type AppSettings = z.infer<typeof AppSettingsSchema>;

// Raw WhatsApp Message Schema
export const RawMessageSchema = z.object({
  id: z.string(),
  groupId: z.string(),
  senderId: z.string(),
  isAdmin: z.boolean(),
  content: z.string(),
  contentHash: z.string(),
  receivedAt: z.string().datetime()
});

export type RawMessagePayload = z.infer<typeof RawMessageSchema>;

// Parsed Signal Schema
export const ParsedSignalSchema = z.object({
  id: z.string().uuid(),
  rawMessageId: z.string(),
  symbol: z.literal("XAUUSD"),
  direction: TradeDirectionSchema,
  entryMin: z.number().positive(),
  entryMax: z.number().positive(),
  stopLoss: z.number().positive(),
  tp1: z.number().positive().nullable(),
  tp2: z.number().positive().nullable(),
  hasTpOpen: z.boolean().default(false),
  createdAt: z.string().datetime()
});

export type ParsedSignalPayload = z.infer<typeof ParsedSignalSchema>;

// Planned Entry Schema
export const PlannedEntrySchema = z.object({
  id: z.string().uuid(),
  campaignId: z.string().uuid(),
  ladderIndex: z.number().int().min(0).max(7),
  price: z.number().positive(),
  volume: z.number().positive(),
  orderType: OrderTypeSchema,
  stopLoss: z.number().positive(),
  takeProfit: z.number().positive().nullable(),
  tpType: z.enum(["FIXED_100_PIP", "TP1", "TP2"])
});

export type PlannedEntry = z.infer<typeof PlannedEntrySchema>;

// Campaign Summary Schema
export const CampaignSummarySchema = z.object({
  id: z.string().uuid(),
  signalId: z.string().uuid(),
  magicNumber: z.number().int().positive(),
  currentState: SignalStatusSchema,
  executionMode: ExecutionModeSchema,
  entryCount: z.number().int().min(3).max(8),
  lotPerEntry: z.number().positive(),
  totalVolume: z.number().positive().max(2.00),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime()
});

export type CampaignSummary = z.infer<typeof CampaignSummarySchema>;

// Audit Event Schema
export const AuditEventSchema = z.object({
  id: z.number().int().positive(),
  eventType: z.string(),
  payload: z.record(z.unknown()),
  createdAt: z.string().datetime()
});

export type AuditEvent = z.infer<typeof AuditEventSchema>;
