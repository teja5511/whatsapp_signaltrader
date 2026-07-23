import test from "node:test";
import assert from "node:assert/strict";
import http from "http";
import fs from "fs";
import path from "path";
import os from "os";
import { loadWorkerConfig } from "../src/config/loader";
import { FakeOpenWAAdapter } from "../src/openwa/fake-adapter";
import { FileSpool } from "../src/openwa/spool";
import { QuarantineManager } from "../src/openwa/quarantine";
import { SessionManager } from "../src/openwa/session";
import { createWorkerApiServer } from "../src/api/server";
import { WHATSAPP_WORKER_VERSION } from "../src/constants";

test("API server should respond to /health and /version unauthenticated", async () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-api-test-"));
  const config = loadWorkerConfig({ WHATSAPP_DATA_DIR: tmpDataDir, WHATSAPP_WORKER_PORT: "8999" });
  const adapter = new FakeOpenWAAdapter();
  const spool = new FileSpool(tmpDataDir);
  const quarantine = new QuarantineManager(tmpDataDir);
  const session = new SessionManager("test", tmpDataDir);
  const server = createWorkerApiServer(config, adapter, spool, quarantine, session);

  await new Promise<void>((resolve) => server.listen(8999, "127.0.0.1", () => resolve()));

  try {
    const resHealth = await fetch("http://127.0.0.1:8999/health");
    assert.equal(resHealth.status, 200);
    const healthJson = (await resHealth.json()) as any;
    assert.equal(healthJson.service, "whatsapp-worker");
    assert.equal(healthJson.worker_version, WHATSAPP_WORKER_VERSION);

    const resVer = await fetch("http://127.0.0.1:8999/version");
    assert.equal(resVer.status, 200);
    const verJson = (await resVer.json()) as any;
    assert.equal(verJson.adapter_mode, "fake");
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});

test("API server mutating endpoints should enforce Bearer token authentication", async () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-api-test-2-"));
  const config = loadWorkerConfig({
    WHATSAPP_DATA_DIR: tmpDataDir,
    WHATSAPP_WORKER_PORT: "8998",
    LOCAL_API_TOKEN: "secret-token-123"
  });
  const adapter = new FakeOpenWAAdapter();
  const spool = new FileSpool(tmpDataDir);
  const quarantine = new QuarantineManager(tmpDataDir);
  const session = new SessionManager("test", tmpDataDir);
  const server = createWorkerApiServer(config, adapter, spool, quarantine, session);

  await new Promise<void>((resolve) => server.listen(8998, "127.0.0.1", () => resolve()));

  try {
    // Missing auth -> 401
    const resNoAuth = await fetch("http://127.0.0.1:8998/status");
    assert.equal(resNoAuth.status, 401);

    // Valid auth -> 200
    const resAuth = await fetch("http://127.0.0.1:8998/status", {
      headers: { Authorization: "Bearer secret-token-123" }
    });
    assert.equal(resAuth.status, 200);
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});
