# Security & Safety Audit Report

**Release Version**: `1.0.0-demo`  
**Security Level**: High-Assurance Safety Hardened  

---

## Safety Architecture & Strict Enforcement

1. **Instrument Enforcement**: XAUUSD (Gold) ONLY. Any non-gold trade signals are blocked at parser classification.
2. **Account Mode Enforcement**: MetaTrader 5 Demo Hedging Accounts ONLY.
   - Non-demo / Live accounts (`REAL`) are strictly rejected by the MT5 adapter during initialization and preflight checks.
   - Netting margin accounts are blocked.
3. **Volume & Ladder Limits**:
   - Minimum ladder entries: 3
   - Maximum ladder entries: 8
   - Default lot per entry: `0.3000`
   - Maximum total campaign lots: `2.0000` (capped deterministically).
4. **Execution Mode**: `CONFIRMATION` by default. Automation is `PAUSED` by default.
5. **No Direct Storage Access**: The React frontend running in Tauri never accesses SQLite or MetaTrader 5 directly. All interactions pass through authenticated FastAPI backend endpoints.
6. **Token Security**: REST API tokens are stored using Tauri's native OS secure store key-value proxy (`apps/desktop/src-tauri/src/secure_store.rs`), preventing plaintext leakage in browser storage (`localStorage`).

---

## Dependency & Credentials Audit

- **No Tracked Credentials**: Git history scanned; no secrets, tokens, `.env` files, or session cookies are tracked.
- **Payload Redaction**: Transactional Outbox redacts sensitive credentials and raw chat tokens before persisting domain event payloads.
