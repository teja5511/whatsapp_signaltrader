import test from "node:test";
import assert from "node:assert/strict";
import fs from "fs";
import path from "path";
import os from "os";
import { SessionManager } from "../src/openwa/session";
import { SessionAlreadyInUseError, InvalidResetConfirmationError } from "../src/errors";
import { RESET_CONFIRMATION_PHRASE } from "../src/constants";

test("SessionManager should acquire and release process lock", () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-session-test-"));
  try {
    const mgr1 = new SessionManager("test-session", tmpDataDir, "worker-1");
    mgr1.acquireLock();

    // Second manager with current PID should throw SessionAlreadyInUseError
    const mgr2 = new SessionManager("test-session", tmpDataDir, "worker-2");
    assert.throws(() => mgr2.acquireLock(), SessionAlreadyInUseError);

    mgr1.releaseLock();
  } finally {
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});

test("SessionManager resetSession should enforce exact confirmation phrase", () => {
  const tmpDataDir = fs.mkdtempSync(path.join(os.tmpdir(), "wa-reset-test-"));
  try {
    const mgr = new SessionManager("test-session", tmpDataDir);
    assert.throws(() => mgr.resetSession("wrong phrase", tmpDataDir), InvalidResetConfirmationError);
    assert.doesNotThrow(() => mgr.resetSession(RESET_CONFIRMATION_PHRASE, tmpDataDir));
  } finally {
    fs.rmSync(tmpDataDir, { recursive: true, force: true });
  }
});
