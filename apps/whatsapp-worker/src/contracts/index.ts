import { z } from "zod";
import { WHATSAPP_INGESTION_CONTRACT_VERSION, WHATSAPP_WORKER_VERSION } from "../constants";

export const WhatsAppMessageEnvelopeSchema = z.object({
  contract_version: z.string().default(WHATSAPP_INGESTION_CONTRACT_VERSION),
  worker_version: z.string().default(WHATSAPP_WORKER_VERSION),
  source: z.literal("WHATSAPP_OPENWA"),
  whatsapp_message_id: z.string(),
  group_id: z.string(),
  group_name: z.string(),
  sender_id: z.string(),
  sender_name: z.string(),
  sender_is_admin: z.boolean().default(true),
  message_type: z.enum(["TEXT", "CAPTION"]),
  text: z.string().max(10000),
  message_timestamp: z.string(),
  received_at: z.string(),
  is_reply: z.boolean().default(false),
  quoted_whatsapp_message_id: z.string().nullable().default(null),
  quoted_sender_id: z.string().nullable().default(null),
  correlation_id: z.string(),
  worker_id: z.string(),
  sanitized_metadata: z.record(z.unknown()).default({})
});

export type WhatsAppMessageEnvelope = z.infer<typeof WhatsAppMessageEnvelopeSchema>;

export const GroupSummarySchema = z.object({
  id: z.string().optional(),
  name: z.string().optional(),
  participants: z.number().int().optional(),
  isCommunity: z.boolean().optional(),
  group_id: z.string(),
  display_name: z.string(),
  participant_count: z.number().int(),
  is_read_only: z.boolean().default(false),
  is_community: z.boolean().default(false),
  is_announcement: z.boolean().default(false),
  is_archived: z.boolean().default(false)
});

export type GroupSummary = z.infer<typeof GroupSummarySchema>;

export const GroupAdminSummarySchema = z.object({
  admin_id: z.string(),
  display_name: z.string(),
  is_admin: z.boolean().default(true),
  is_super_admin: z.boolean().default(false),
  is_group_member: z.boolean().default(true)
});

export type GroupAdminSummary = z.infer<typeof GroupAdminSummarySchema>;
