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

export enum ParserCategory {
  NEW_SIGNAL = "NEW_SIGNAL",
  FOLLOW_UP_COMMAND = "FOLLOW_UP_COMMAND",
  INFORMATIONAL = "INFORMATIONAL",
  AMBIGUOUS = "AMBIGUOUS",
  INVALID = "INVALID",
  UNSUPPORTED = "UNSUPPORTED"
}

export enum ExecutionEligibility {
  NEVER = "NEVER",
  REQUIRES_CONFIRMATION = "REQUIRES_CONFIRMATION",
  ELIGIBLE_AFTER_CAMPAIGN_MATCH = "ELIGIBLE_AFTER_CAMPAIGN_MATCH",
  ELIGIBLE_AFTER_VALIDATION = "ELIGIBLE_AFTER_VALIDATION"
}

// Zod Schemas
export const TradeDirectionSchema = z.nativeEnum(TradeDirection);
export const ExecutionModeSchema = z.nativeEnum(ExecutionMode);
export const SignalStatusSchema = z.nativeEnum(SignalStatus);
export const OrderTypeSchema = z.nativeEnum(OrderType);
export const ParserCategorySchema = z.nativeEnum(ParserCategory);
export const ExecutionEligibilitySchema = z.nativeEnum(ExecutionEligibility);

// Parser Input Schema
export const ParserInputSchema = z.object({
  contractVersion: z.string().default("1.0.0"),
  parserVersion: z.string().default("1.0.0"),
  messageId: z.string(),
  groupId: z.string(),
  senderId: z.string(),
  text: z.string(),
  messageTimestamp: z.string().datetime(),
  quotedMessageId: z.string().nullable().default(null),
  isReply: z.boolean().default(false)
});

export type ParserInput = z.infer<typeof ParserInputSchema>;

// Parser Validation Issue Schema
export const ParserValidationIssueSchema = z.object({
  code: z.string(),
  severity: z.enum(["INFO", "WARNING", "ERROR"]),
  field: z.string().nullable().default(null),
  message: z.string(),
  sourceLine: z.number().int().nullable().default(null)
});

export type ParserValidationIssue = z.infer<typeof ParserValidationIssueSchema>;

// Parsed Signal Payload
export const ParsedSignalPayloadSchema = z.object({
  instrument: z.literal("XAUUSD"),
  direction: TradeDirectionSchema,
  orderIntent: z.enum(["LIMIT", "UNSPECIFIED"]),
  zoneLow: z.string(),
  zoneHigh: z.string(),
  stopLoss: z.string().nullable().default(null),
  tp1: z.string().nullable().default(null),
  tp2: z.string().nullable().default(null),
  tpOpenPresent: z.boolean().default(false),
  completeness: z.enum(["COMPLETE", "INCOMPLETE"])
});

export type ParsedSignalPayload = z.infer<typeof ParsedSignalPayloadSchema>;

// Parsed Command Payload
export const ParsedCommandPayloadSchema = z.object({
  commandType: z.enum([
    "MODIFY_STOP_LOSS", "CLOSE_CAMPAIGN", "CANCEL_SIGNAL",
    "ZONE_VALID", "REENTRY", "ADD_TAKE_PROFIT"
  ]),
  classification: z.enum(["EXPLICIT", "AMBIGUOUS"]),
  value: z.string().nullable().default(null),
  valueKind: z.enum(["PRICE", "PIPS", "SLOT", "NONE"]).default("NONE"),
  hardStop: z.boolean().default(false),
  targetTpSlot: z.enum(["TP1", "TP2", "UNSPECIFIED"]).nullable().default(null)
});

export type ParsedCommandPayload = z.infer<typeof ParsedCommandPayloadSchema>;

// Complete Parser Result Schema
export const ParserResultSchema = z.object({
  contractVersion: z.string().default("1.0.0"),
  parserVersion: z.string().default("1.0.0"),
  category: ParserCategorySchema,
  isExecutable: z.boolean().default(false),
  requiresConfirmation: z.boolean().default(true),
  executionEligibility: ExecutionEligibilitySchema,
  originalText: z.string(),
  normalizedText: z.string(),
  signal: ParsedSignalPayloadSchema.nullable().default(null),
  command: ParsedCommandPayloadSchema.nullable().default(null),
  commands: z.array(ParsedCommandPayloadSchema).default([]),
  informational: z.record(z.unknown()).nullable().default(null),
  ambiguous: z.record(z.unknown()).nullable().default(null),
  validationIssues: z.array(ParserValidationIssueSchema).default([]),
  warnings: z.array(z.string()).default([]),
  campaignMatchStrategyHint: z.enum(["QUOTED_MESSAGE", "LATEST_COMPATIBLE", "NONE"]).default("NONE"),
  sourceMetadata: z.object({
    messageId: z.string(),
    groupId: z.string(),
    senderId: z.string(),
    quotedMessageId: z.string().nullable().default(null),
    isReply: z.boolean().default(false)
  })
});

export type ParserResult = z.infer<typeof ParserResultSchema>;

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
