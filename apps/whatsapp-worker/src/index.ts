import { WhatsAppWorkerApp } from "./app";

export * from "./constants";
export * from "./errors";
export * from "./config/schema";
export * from "./config/loader";
export * from "./config/paths";
export * from "./contracts";
export * from "./state/worker-state";
export * from "./state/event-bus";
export * from "./openwa/adapter";
export * from "./openwa/fake-adapter";
export * from "./openwa/real-adapter";
export * from "./openwa/client-factory";
export * from "./openwa/session";
export * from "./openwa/filters";
export * from "./openwa/spool";
export * from "./openwa/delivery";
export * from "./openwa/quarantine";
export * from "./app";

if (require.main === module) {
  const app = new WhatsAppWorkerApp();
  app.start().catch((err) => {
    console.error("[WhatsApp Worker Fatal Error]", err);
    process.exit(1);
  });
}
