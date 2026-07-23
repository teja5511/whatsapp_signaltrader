import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import React from "react";
import { secureTokenSet, secureTokenExists, secureTokenClear } from "../api/tauriClient";
import { globalEventClient } from "../realtime/eventClient";
import { Badge } from "../components/ui/Badge";
import { getStatusBadgeVariant } from "../lib/utils";

describe("Tauri Desktop Security & Shell Unit Tests", () => {
  beforeEach(async () => {
    await secureTokenClear();
    localStorage.clear();
    sessionStorage.clear();
  });

  it("verifies secure token is stored in Rust proxy memory and NEVER in browser storage", async () => {
    await secureTokenSet("secret-local-bearer-token-123");
    const exists = await secureTokenExists();
    expect(exists).toBe(true);

    // Verify localStorage & sessionStorage contain zero tokens
    expect(localStorage.getItem("LOCAL_API_TOKEN")).toBeNull();
    expect(sessionStorage.getItem("LOCAL_API_TOKEN")).toBeNull();
    expect(localStorage.getItem("token")).toBeNull();
  });

  it("verifies status badge color semantics", () => {
    expect(getStatusBadgeVariant("RUNNING")).toBe("green");
    expect(getStatusBadgeVariant("PAUSED")).toBe("amber");
    expect(getStatusBadgeVariant("EMERGENCY_STOPPED")).toBe("red");
    expect(getStatusBadgeVariant("CONFIRMATION")).toBe("blue");
    expect(getStatusBadgeVariant("UNKNOWN_STATE")).toBe("gray");
  });

  it("renders status badge component correctly", () => {
    render(<Badge status="RUNNING" />);
    expect(screen.getByText("RUNNING")).toBeInTheDocument();
  });

  it("verifies realtime event client deduplication buffer", () => {
    let receivedCount = 0;
    const unsubscribe = globalEventClient.subscribe(() => {
      receivedCount++;
    });

    // Simulate same event sequence duplicate
    const fakeEvent = {
      event_contract_version: "1.0.0",
      event_id: "evt-dup-1",
      sequence: 1,
      event_type: "CAMPAIGN_CREATED",
      aggregate_type: "CAMPAIGN",
      aggregate_id: "camp-1",
      correlation_id: "corr-1",
      occurred_at: new Date().toISOString(),
      payload: {},
    };

    (globalEventClient as any).handleIncomingEvent(fakeEvent);
    (globalEventClient as any).handleIncomingEvent(fakeEvent); // Duplicate

    expect(receivedCount).toBe(1);
    unsubscribe();
  });
});
