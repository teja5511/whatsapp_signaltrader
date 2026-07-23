# Security & Safety Controls Specification

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Approved & Frozen  

---

## 1. Safety Boundaries & Protective Rules

### 1.1 Source & Admin Authorization Controls
- **Single Approved Group**: System binds strictly to one user-configured WhatsApp Group JID (`target_group_jid`). Messages from any other group or direct message (DM) are discarded immediately.
- **Single Approved Admin**: System inspects `sender_jid` against the designated group administrator phone number. Non-admin messages trigger security warnings and are dropped prior to parsing.

---

### 1.2 Instrument & Account Guardrails
- **XAUUSD Instrument Isolation**: System hard-rejects any trade signal for symbols other than `XAUUSD` (or broker suffix equivalents e.g. `XAUUSDm`).
- **Hedging Account Enforcement**: Upon connection, the MT5 adapter queries `account_info().margin_mode`. If the account uses Netting (`ACCOUNT_MARGIN_MODE_RETAIL_NETTING`), trading execution is locked and blocked.
- **Demo / Live Detection**: The MT5 adapter queries `account_info().trade_mode`. The current mode (`DEMO` vs `REAL`) is prominently displayed on the UI dashboard with warning banners for real accounts.

---

### 1.3 Exposure & Sizing Hard Limits
- **Maximum Campaign Exposure**: Absolute exposure ceiling is **2.00 total lots**.
  - Formula: $\text{Total Lots} = \text{Entry Count} \times \text{Lot Per Entry} \le 2.00$.
  - Guard Behavior: If total lots exceed 2.00, execution is **blocked**. The system raises a hard validation error and will **NEVER** silently reduce or modify lot sizes.
- **Entry Count Bounds**: Entry count parameter is restricted between **3 and 8 entries inclusive**. Values outside this range are rejected by UI inputs and backend schema validators.

---

### 1.4 Execution Integrity & Anti-Duplicate Controls
- **Idempotency Engine**: Every incoming message generates a unique key derived from WhatsApp Message ID and SHA-256 content hash stored in `duplicate_keys`. Duplicate incoming webhooks are discarded.
- **Single MT5 Execution Queue**: All MT5 API calls pass through a single thread-bound asyncio execution queue, eliminating concurrent race conditions and duplicate order execution.
- **Startup Reconciliation Lock**: Upon boot, a global reconciliation lock (`system_reconciling_lock`) blocks new signal execution until MT5 live orders are fully synced with SQLite state.

---

## 2. Emergency Controls & Fail-Safes

### 2.1 Automation Pause Switch
- Dashboard provides a high-priority **"Pause Automation"** toggle switch.
- When toggled ON: Incoming signals are parsed and logged, but state transitions to `PLANNED` or order placement to MT5 are suspended until automation is unpaused.

---

### 2.2 Emergency Close-All Mechanism
- Dashboard provides a prominent, guarded **"EMERGENCY CLOSE ALL"** button.
- Triggering Emergency Close-All:
  1. Instantly cancels all active pending grid orders across all campaigns in MT5.
  2. Issues market close requests for all open positions across all campaigns in MT5.
  3. Transitions all active campaigns to `CLOSED` / `CANCELLED` status with audit trail entry `EMERGENCY_CLOSE_ALL_TRIGGERED`.

---

## 3. Security Infrastructure & Local API Protection

- **Local API Security**: FastAPI backend listens exclusively on `127.0.0.1` (localhost). External network interfaces are not bound.
- **Secret & Token Storage**: User WhatsApp sessions, tokens, and MT5 login credentials are saved locally in the OS Windows Credential Manager / encrypted local directory.
- **Audit Logging**: All security events, authorization failures, system state changes, user interactions, and MT5 API calls are logged to append-only SQLite audit tables (`system_audit_events`).
