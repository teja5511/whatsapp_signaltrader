import fs from "fs";
import path from "path";
import os from "os";
import { resolveWorkerPaths } from "../config/paths";
import { SessionAlreadyInUseError, InvalidResetConfirmationError } from "../errors";
import { RESET_CONFIRMATION_PHRASE } from "../constants";

export interface LockFileData {
  worker_id: string;
  process_id: number;
  hostname: string;
  started_at: string;
  session_name: string;
}

export class SessionManager {
  private lockFilePath: string;

  constructor(private sessionName: string = "xauusd-bot", baseDataDir?: string, private workerId: string = "worker-1") {
    const paths = resolveWorkerPaths(baseDataDir);
    this.lockFilePath = path.join(paths.locksDir, `${sessionName}.lock`);
  }

  acquireLock(): void {
    const dir = path.dirname(this.lockFilePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    if (fs.existsSync(this.lockFilePath)) {
      try {
        const raw = fs.readFileSync(this.lockFilePath, "utf-8");
        const data: LockFileData = JSON.parse(raw);

        // Check if lock process is still running
        if (data.process_id && this.isProcessAlive(data.process_id)) {
          throw new SessionAlreadyInUseError(`Session lock '${this.sessionName}' is actively owned by process ${data.process_id} on ${data.hostname}.`);
        } else {
          // Stale lock from dead process -> overwrite cleanly
          fs.unlinkSync(this.lockFilePath);
        }
      } catch (err: any) {
        if (err instanceof SessionAlreadyInUseError) throw err;
        // Corrupted lock file -> remove stale lock
        try { fs.unlinkSync(this.lockFilePath); } catch {}
      }
    }

    const lockData: LockFileData = {
      worker_id: this.workerId,
      process_id: process.pid,
      hostname: os.hostname(),
      started_at: new Date().toISOString(),
      session_name: this.sessionName
    };

    fs.writeFileSync(this.lockFilePath, JSON.stringify(lockData, null, 2), { flag: "wx" });
  }

  releaseLock(): void {
    if (fs.existsSync(this.lockFilePath)) {
      try {
        const raw = fs.readFileSync(this.lockFilePath, "utf-8");
        const data: LockFileData = JSON.parse(raw);
        if (data.process_id === process.pid) {
          fs.unlinkSync(this.lockFilePath);
        }
      } catch {
        try { fs.unlinkSync(this.lockFilePath); } catch {}
      }
    }
  }

  resetSession(confirmationPhrase: string, sessionDir: string): void {
    if (confirmationPhrase !== RESET_CONFIRMATION_PHRASE) {
      throw new InvalidResetConfirmationError();
    }
    if (fs.existsSync(sessionDir)) {
      fs.rmSync(sessionDir, { recursive: true, force: true });
    }
  }

  private isProcessAlive(pid: number): boolean {
    try {
      return process.kill(pid, 0);
    } catch {
      return false;
    }
  }
}
