import { z } from "zod";
import { MODE_FAKE, MODE_REAL, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_SESSION_NAME, DEFAULT_TRADING_SERVICE_URL, DEFAULT_LOCAL_API_TOKEN } from "../constants";

export const WorkerConfigSchema = z.object({
  adapterMode: z.enum([MODE_FAKE, MODE_REAL]).default(MODE_FAKE),
  workerHost: z.string().default(DEFAULT_HOST),
  workerPort: z.number().int().default(DEFAULT_PORT),
  workerEnabled: z.boolean().default(true),
  realConnectionEnabled: z.boolean().default(false),
  sessionName: z.string().default(DEFAULT_SESSION_NAME),
  dataDir: z.string().optional(),
  approvedGroupId: z.string().optional(),
  approvedAdminId: z.string().optional(),
  requireAdminRole: z.boolean().default(true),
  deliveryConcurrency: z.number().int().default(1),
  deliveryTimeoutMs: z.number().int().default(10000),
  retryInitialMs: z.number().int().default(1000),
  retryMaxMs: z.number().int().default(60000),
  retryMaxAttempts: z.number().int().default(3),
  groupMetadataTtlSeconds: z.number().int().default(300),
  tradingServiceUrl: z.string().default(DEFAULT_TRADING_SERVICE_URL),
  localApiToken: z.string().default(DEFAULT_LOCAL_API_TOKEN),
  qrExposeOverLocalApi: z.boolean().default(true),
  qrTtlSeconds: z.number().int().default(60),
  rawTextLogging: z.boolean().default(false)
});

export type WorkerConfig = z.infer<typeof WorkerConfigSchema>;
