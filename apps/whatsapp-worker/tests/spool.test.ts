import test from "node:test";
import assert from "node:assert/strict";
import fs from "fs";
import path from "path";
import os from "os";
import { FileSpool } from "../src/openwa/spool";
import { WhatsAppMessageEnvelope } from "../src/contracts";

test("FileSpool should atomically save envelope and transition states", () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-spool-test-"));
  try {
    const spool = new FileSpool(tmpDataDir);
    const env: WhatsAppMessageEnvelope = {
      contract_version: "1.0.0",
      worker_version: "1.0.0",
      source: "WHATSAPP_OPENWA",
      whatsapp_message_id: "wamid-test-spool",
      group_id: "group-xauusd-vip",
      group_name: "XAUUSD VIP",
      sender_id: "admin-master-1",
      sender_name: "Admin",
      sender_is_admin: true,
      message_type: "TEXT",
      text: "Gold Sell\n3990-3998\nsl - 4008",
      message_timestamp: new Date().toISOString(),
      received_at: new Date().toISOString(),
      is_reply: false,
      quoted_whatsapp_message_id: null,
      quoted_sender_id: null,
      correlation_id: "corr-1",
      worker_id: "worker-1",
      sanitized_metadata: {}
    };

    // Save
    const item = spool.saveEnvelope(env);
    assert.equal(item.status, "pending");
    assert.equal(spool.getSpoolCounts().pending, 1);

    // Claim next pending
    const claimed = spool.getNextPendingItem();
    assert.notEqual(claimed, null);
    assert.equal(claimed!.id, item.id);
    assert.equal(spool.getSpoolCounts().delivering, 1);

    // Mark delivered
    spool.markDelivered(item.id);
    assert.equal(spool.getSpoolCounts().delivered, 1);
    assert.equal(spool.getSpoolCounts().delivering, 0);
  } finally {
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});
