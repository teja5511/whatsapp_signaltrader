import test from "node:test";
import assert from "node:assert/strict";
import fs from "fs";
import path from "path";
import os from "os";
import { loadWorkerConfig, saveLocalConfig } from "../src/config/loader";
import { MODE_FAKE } from "../src/constants";

test("loadWorkerConfig should load defaults cleanly", () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-config-test-"));
  try {
    const config = loadWorkerConfig({
      WHATSAPP_DATA_DIR: tmpDataDir,
      WHATSAPP_ADAPTER_MODE: "fake"
    });
    assert.equal(config.adapterMode, MODE_FAKE);
    assert.equal(config.workerPort, 8010);
    assert.equal(config.requireAdminRole, true);
  } finally {
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});

test("loadWorkerConfig environment variables should override localConfigFile", () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-config-test-2-"));
  try {
    saveLocalConfig({
      approved_group_id: "local-group-123",
      approved_admin_id: "local-admin-456"
    }, tmpDataDir);

    const config = loadWorkerConfig({
      WHATSAPP_DATA_DIR: tmpDataDir,
      WHATSAPP_APPROVED_GROUP_ID: "env-group-999"
    });

    assert.equal(config.approvedGroupId, "env-group-999");
    assert.equal(config.approvedAdminId, "local-admin-456");
  } finally {
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});
