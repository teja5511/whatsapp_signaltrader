import fs from "fs";
import path from "path";
import { WorkerConfig, WorkerConfigSchema } from "./schema";
import { resolveWorkerPaths } from "./paths";
import { MODE_FAKE } from "../constants";

export interface LocalPersistedConfig {
  approved_group_id?: string;
  approved_group_display_name?: string;
  approved_admin_id?: string;
  approved_admin_display_name?: string;
  selected_at?: string;
  last_validated_at?: string;
}

export function loadWorkerConfig(overrideEnv: Record<string, string | undefined> = process.env): WorkerConfig {
  const env = overrideEnv;
  const paths = resolveWorkerPaths(env.WHATSAPP_DATA_DIR);

  // Ensure data directories exist
  [
    paths.dataDir, paths.sessionsDir, paths.spoolDir, paths.spoolPendingDir,
    paths.spoolDeliveringDir, paths.spoolDeliveredDir, paths.quarantineDir,
    paths.locksDir, paths.configDir
  ].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });

  // Read local persisted config if present
  let localConfig: LocalPersistedConfig = {};
  if (fs.existsSync(paths.localConfigFile)) {
    try {
      const raw = fs.readFileSync(paths.localConfigFile, "utf-8");
      localConfig = JSON.parse(raw);
    } catch {
      localConfig = {};
    }
  }

  // Environment variables take precedence over localConfigFile
  const rawObj = {
    adapterMode: env.WHATSAPP_ADAPTER_MODE || MODE_FAKE,
    workerHost: env.WHATSAPP_WORKER_HOST || "127.0.0.1",
    workerPort: env.WHATSAPP_WORKER_PORT ? parseInt(env.WHATSAPP_WORKER_PORT, 10) : 8010,
    workerEnabled: env.WHATSAPP_WORKER_ENABLED ? env.WHATSAPP_WORKER_ENABLED.toLowerCase() === "true" : true,
    realConnectionEnabled: env.WHATSAPP_REAL_CONNECTION_ENABLED ? env.WHATSAPP_REAL_CONNECTION_ENABLED.toLowerCase() === "true" : false,
    sessionName: env.WHATSAPP_SESSION_NAME || "xauusd-bot",
    dataDir: env.WHATSAPP_DATA_DIR || paths.dataDir,
    approvedGroupId: env.WHATSAPP_APPROVED_GROUP_ID || localConfig.approved_group_id,
    approvedAdminId: env.WHATSAPP_APPROVED_ADMIN_ID || localConfig.approved_admin_id,
    requireAdminRole: env.WHATSAPP_REQUIRE_ADMIN_ROLE ? env.WHATSAPP_REQUIRE_ADMIN_ROLE.toLowerCase() === "true" : true,
    deliveryConcurrency: env.WHATSAPP_DELIVERY_CONCURRENCY ? parseInt(env.WHATSAPP_DELIVERY_CONCURRENCY, 10) : 1,
    deliveryTimeoutMs: env.WHATSAPP_DELIVERY_TIMEOUT_MS ? parseInt(env.WHATSAPP_DELIVERY_TIMEOUT_MS, 10) : 10000,
    retryInitialMs: env.WHATSAPP_RETRY_INITIAL_MS ? parseInt(env.WHATSAPP_RETRY_INITIAL_MS, 10) : 1000,
    retryMaxMs: env.WHATSAPP_RETRY_MAX_MS ? parseInt(env.WHATSAPP_RETRY_MAX_MS, 10) : 60000,
    retryMaxAttempts: env.WHATSAPP_RETRY_MAX_ATTEMPTS ? parseInt(env.WHATSAPP_RETRY_MAX_ATTEMPTS, 10) : 3,
    groupMetadataTtlSeconds: env.WHATSAPP_GROUP_METADATA_TTL_SECONDS ? parseInt(env.WHATSAPP_GROUP_METADATA_TTL_SECONDS, 10) : 300,
    tradingServiceUrl: env.TRADING_SERVICE_URL || "http://127.0.0.1:8000",
    localApiToken: env.LOCAL_API_TOKEN || "dev-local-secret-token",
    qrExposeOverLocalApi: env.WHATSAPP_QR_EXPOSE_OVER_LOCAL_API ? env.WHATSAPP_QR_EXPOSE_OVER_LOCAL_API.toLowerCase() === "true" : false,
    qrTtlSeconds: env.WHATSAPP_QR_TTL_SECONDS ? parseInt(env.WHATSAPP_QR_TTL_SECONDS, 10) : 60,
    rawTextLogging: env.WHATSAPP_RAW_TEXT_LOGGING ? env.WHATSAPP_RAW_TEXT_LOGGING.toLowerCase() === "true" : false
  };

  return WorkerConfigSchema.parse(rawObj);
}

export function saveLocalConfig(localConfig: LocalPersistedConfig, baseDataDir?: string): void {
  const paths = resolveWorkerPaths(baseDataDir);
  if (!fs.existsSync(paths.configDir)) {
    fs.mkdirSync(paths.configDir, { recursive: true });
  }
  fs.writeFileSync(paths.localConfigFile, JSON.stringify(localConfig, null, 2), "utf-8");
}
