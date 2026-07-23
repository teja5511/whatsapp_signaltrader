import crypto from "crypto";

export function generateWorkerIdempotencyKey(groupId: string, whatsappMessageId: string): string {
  const rawKey = `WHATSAPP:${groupId.trim()}:${whatsappMessageId.trim()}`;
  return crypto.createHash("sha256").update(rawKey).digest("hex");
}
