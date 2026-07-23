import fs from "fs";
import path from "path";
import { WhatsAppMessageEnvelope } from "../contracts";
import { generateWorkerIdempotencyKey } from "./idempotency";
import { resolveWorkerPaths, WorkerPaths } from "../config/paths";

export interface SpoolItem {
  id: string;
  sequence: number;
  idempotency_key: string;
  envelope: WhatsAppMessageEnvelope;
  attempt_count: number;
  status: "pending" | "delivering" | "delivered" | "quarantined";
  last_error?: string;
  created_at: string;
  updated_at: string;
}

export class FileSpool {
  private paths: WorkerPaths;
  private sequenceCounter: number = 0;

  constructor(baseDataDir?: string) {
    this.paths = resolveWorkerPaths(baseDataDir);
    this.ensureDirectories();
  }

  private ensureDirectories(): void {
    [
      this.paths.spoolPendingDir,
      this.paths.spoolDeliveringDir,
      this.paths.spoolDeliveredDir,
      this.paths.quarantineDir
    ].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  saveEnvelope(envelope: WhatsAppMessageEnvelope): SpoolItem {
    this.sequenceCounter += 1;
    const seqStr = String(this.sequenceCounter).padStart(8, "0");
    const key = generateWorkerIdempotencyKey(envelope.group_id, envelope.whatsapp_message_id);
    const itemId = `${seqStr}-${key}`;
    const now = new Date().toISOString();

    const spoolItem: SpoolItem = {
      id: itemId,
      sequence: this.sequenceCounter,
      idempotency_key: key,
      envelope,
      attempt_count: 0,
      status: "pending",
      created_at: now,
      updated_at: now
    };

    const targetFile = path.join(this.paths.spoolPendingDir, `${itemId}.json`);
    const tempFile = path.join(this.paths.spoolPendingDir, `${itemId}.tmp`);

    // Atomic write
    fs.writeFileSync(tempFile, JSON.stringify(spoolItem, null, 2), "utf-8");
    fs.renameSync(tempFile, targetFile);

    return spoolItem;
  }

  getNextPendingItem(): SpoolItem | null {
    const files = fs.readdirSync(this.paths.spoolPendingDir).filter(f => f.endsWith(".json")).sort();
    if (files.length === 0) return null;

    const fileName = files[0];
    const pendingFile = path.join(this.paths.spoolPendingDir, fileName);
    const deliveringFile = path.join(this.paths.spoolDeliveringDir, fileName);

    try {
      const raw = fs.readFileSync(pendingFile, "utf-8");
      const item: SpoolItem = JSON.parse(raw);
      item.status = "delivering";
      item.updated_at = new Date().toISOString();

      fs.writeFileSync(deliveringFile, JSON.stringify(item, null, 2), "utf-8");
      fs.unlinkSync(pendingFile);
      return item;
    } catch {
      return null;
    }
  }

  markDelivered(itemId: string): void {
    const deliveringFile = path.join(this.paths.spoolDeliveringDir, `${itemId}.json`);
    const deliveredFile = path.join(this.paths.spoolDeliveredDir, `${itemId}.json`);

    if (fs.existsSync(deliveringFile)) {
      try {
        const raw = fs.readFileSync(deliveringFile, "utf-8");
        const item: SpoolItem = JSON.parse(raw);
        item.status = "delivered";
        item.updated_at = new Date().toISOString();
        fs.writeFileSync(deliveredFile, JSON.stringify(item, null, 2), "utf-8");
        fs.unlinkSync(deliveringFile);
      } catch {}
    }
  }

  quarantineItem(itemId: string, reasonCode: string, errorMsg: string): void {
    const deliveringFile = path.join(this.paths.spoolDeliveringDir, `${itemId}.json`);
    const pendingFile = path.join(this.paths.spoolPendingDir, `${itemId}.json`);
    const quarantineFile = path.join(this.paths.quarantineDir, `${itemId}.json`);

    let itemRaw: string | null = null;
    if (fs.existsSync(deliveringFile)) {
      itemRaw = fs.readFileSync(deliveringFile, "utf-8");
      fs.unlinkSync(deliveringFile);
    } else if (fs.existsSync(pendingFile)) {
      itemRaw = fs.readFileSync(pendingFile, "utf-8");
      fs.unlinkSync(pendingFile);
    }

    if (itemRaw) {
      try {
        const item: SpoolItem = JSON.parse(itemRaw);
        item.status = "quarantined";
        item.last_error = `[${reasonCode}] ${errorMsg}`;
        item.updated_at = new Date().toISOString();
        fs.writeFileSync(quarantineFile, JSON.stringify(item, null, 2), "utf-8");
      } catch {}
    }
  }

  getSpoolCounts(): { pending: number; delivering: number; delivered: number; quarantined: number } {
    return {
      pending: fs.existsSync(this.paths.spoolPendingDir) ? fs.readdirSync(this.paths.spoolPendingDir).filter(f => f.endsWith(".json")).length : 0,
      delivering: fs.existsSync(this.paths.spoolDeliveringDir) ? fs.readdirSync(this.paths.spoolDeliveringDir).filter(f => f.endsWith(".json")).length : 0,
      delivered: fs.existsSync(this.paths.spoolDeliveredDir) ? fs.readdirSync(this.paths.spoolDeliveredDir).filter(f => f.endsWith(".json")).length : 0,
      quarantined: fs.existsSync(this.paths.quarantineDir) ? fs.readdirSync(this.paths.quarantineDir).filter(f => f.endsWith(".json")).length : 0
    };
  }
}
