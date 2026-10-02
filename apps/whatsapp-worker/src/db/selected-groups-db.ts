// @ts-ignore
import { DatabaseSync } from "node:sqlite";
import fs from "fs";
import path from "path";
import { resolveWorkerPaths } from "../config/paths";

export interface SelectedGroupRecord {
  id: string;
  jid: string;
  name: string;
  addedAt: string;
  enabled: boolean;
  lastSignalTime: string | null;
  messagesToday: number;
}

export class SelectedGroupsDB {
  private db: DatabaseSync;

  constructor(dbPath: string = "./data/selected_groups.db") {
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    this.db = new DatabaseSync(dbPath);
    this.init();
  }

  private init() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS selected_groups (
        id TEXT PRIMARY KEY,
        jid TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        addedAt TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 1,
        lastSignalTime TEXT,
        messagesToday INTEGER DEFAULT 0
      );
    `);
  }

  getAll(): SelectedGroupRecord[] {
    try {
      const stmt = this.db.prepare("SELECT * FROM selected_groups ORDER BY name ASC");
      const rows = stmt.all() as any[];
      return rows.map((r) => ({
        id: String(r.id),
        jid: String(r.jid),
        name: String(r.name),
        addedAt: String(r.addedAt),
        enabled: Boolean(r.enabled),
        lastSignalTime: r.lastSignalTime ? String(r.lastSignalTime) : null,
        messagesToday: Number(r.messagesToday || 0),
      }));
    } catch {
      return [];
    }
  }

  getEnabledJids(): Set<string> {
    try {
      const stmt = this.db.prepare("SELECT jid FROM selected_groups WHERE enabled = 1");
      const rows = stmt.all() as any[];
      return new Set(rows.map((r) => String(r.jid)));
    } catch {
      return new Set();
    }
  }

  getByJid(jid: string): SelectedGroupRecord | null {
    try {
      const stmt = this.db.prepare("SELECT * FROM selected_groups WHERE jid = ? OR id = ?");
      const r = stmt.get(jid, jid) as any;
      if (!r) return null;
      return {
        id: String(r.id),
        jid: String(r.jid),
        name: String(r.name),
        addedAt: String(r.addedAt),
        enabled: Boolean(r.enabled),
        lastSignalTime: r.lastSignalTime ? String(r.lastSignalTime) : null,
        messagesToday: Number(r.messagesToday || 0),
      };
    } catch {
      return null;
    }
  }

  add(jid: string, name: string): SelectedGroupRecord {
    const cleanJid = jid.trim();
    const cleanName = (name || cleanJid).trim();
    const existing = this.getByJid(cleanJid);
    if (existing) {
      return existing;
    }
    const id = `grp-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    const addedAt = new Date().toISOString();
    const stmt = this.db.prepare(
      "INSERT INTO selected_groups (id, jid, name, addedAt, enabled, messagesToday) VALUES (?, ?, ?, ?, 1, 0)"
    );
    stmt.run(id, cleanJid, cleanName, addedAt);
    return {
      id,
      jid: cleanJid,
      name: cleanName,
      addedAt,
      enabled: true,
      lastSignalTime: null,
      messagesToday: 0,
    };
  }

  remove(jid: string): boolean {
    try {
      const stmt = this.db.prepare("DELETE FROM selected_groups WHERE jid = ? OR id = ?");
      stmt.run(jid, jid);
      return true;
    } catch {
      return false;
    }
  }

  setEnabled(jid: string, enabled: boolean): SelectedGroupRecord | null {
    try {
      const stmt = this.db.prepare(
        "UPDATE selected_groups SET enabled = ? WHERE jid = ? OR id = ?"
      );
      stmt.run(enabled ? 1 : 0, jid, jid);
      return this.getByJid(jid);
    } catch {
      return null;
    }
  }

  recordSignal(jid: string): void {
    try {
      const now = new Date().toISOString();
      const stmt = this.db.prepare(
        "UPDATE selected_groups SET lastSignalTime = ?, messagesToday = messagesToday + 1 WHERE jid = ?"
      );
      stmt.run(now, jid);
    } catch {}
  }
}

function defaultSelectedGroupsPath(): string {
  const paths = resolveWorkerPaths(process.env.WHATSAPP_DATA_DIR);
  return path.join(paths.dataDir, "selected_groups.db");
}

export const selectedGroupsDb = new SelectedGroupsDB(defaultSelectedGroupsPath());
