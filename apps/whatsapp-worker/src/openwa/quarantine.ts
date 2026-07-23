import fs from "fs";
import path from "path";
import { SpoolItem } from "./spool";
import { resolveWorkerPaths } from "../config/paths";

export class QuarantineManager {
  constructor(private baseDataDir?: string) {}

  listQuarantinedItems(): SpoolItem[] {
    const paths = resolveWorkerPaths(this.baseDataDir);
    if (!fs.existsSync(paths.quarantineDir)) return [];

    const files = fs.readdirSync(paths.quarantineDir).filter(f => f.endsWith(".json"));
    const items: SpoolItem[] = [];

    for (const f of files) {
      try {
        const raw = fs.readFileSync(path.join(paths.quarantineDir, f), "utf-8");
        items.push(JSON.parse(raw));
      } catch {}
    }
    return items;
  }

  requeueQuarantinedItem(itemId: string): boolean {
    const paths = resolveWorkerPaths(this.baseDataDir);
    const quarantineFile = path.join(paths.quarantineDir, `${itemId}.json`);
    const pendingFile = path.join(paths.spoolPendingDir, `${itemId}.json`);

    if (!fs.existsSync(quarantineFile)) return false;

    try {
      const raw = fs.readFileSync(quarantineFile, "utf-8");
      const item: SpoolItem = JSON.parse(raw);
      item.status = "pending";
      item.attempt_count = 0;
      item.updated_at = new Date().toISOString();

      fs.writeFileSync(pendingFile, JSON.stringify(item, null, 2), "utf-8");
      fs.unlinkSync(quarantineFile);
      return true;
    } catch {
      return false;
    }
  }
}
