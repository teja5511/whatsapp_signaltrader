import path from "path";

export interface WorkerPaths {
  rootDir: string;
  dataDir: string;
  sessionsDir: string;
  spoolDir: string;
  spoolPendingDir: string;
  spoolDeliveringDir: string;
  spoolDeliveredDir: string;
  quarantineDir: string;
  locksDir: string;
  configDir: string;
  localConfigFile: string;
}

export function resolveWorkerPaths(baseDataDir?: string): WorkerPaths {
  const rootDir = path.resolve(__dirname, "../../");
  const dataDir = baseDataDir ? path.resolve(baseDataDir) : path.join(rootDir, "data");

  return {
    rootDir,
    dataDir,
    sessionsDir: path.join(dataDir, "sessions"),
    spoolDir: path.join(dataDir, "spool"),
    spoolPendingDir: path.join(dataDir, "spool", "pending"),
    spoolDeliveringDir: path.join(dataDir, "spool", "delivering"),
    spoolDeliveredDir: path.join(dataDir, "spool", "delivered"),
    quarantineDir: path.join(dataDir, "quarantine"),
    locksDir: path.join(dataDir, "locks"),
    configDir: path.join(dataDir, "config"),
    localConfigFile: path.join(dataDir, "config", "worker.local.json")
  };
}
