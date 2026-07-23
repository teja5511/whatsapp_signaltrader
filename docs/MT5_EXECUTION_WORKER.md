# MT5 Execution Worker Specification

Document Version: 1.0.0 (Phase 7 Worker)  
Status: Approved & Implemented  

---

## 1. Single-Writer Durable Queue

- Jobs persisted in `mt5_execution_jobs` with UNIQUE `idempotency_key`.
- Processed sequentially by a single background worker (`MT5ExecutionWorker`).
- Idempotency key format: `sha256(campaign_id + planning_fingerprint + planned_entry_id + campaign_version + login_hash + server + symbol + op)`.

---

## 2. Order Check & Send Sequence

1. Claim queued job.
2. Verify adapter initialization & demo safety gates.
3. Build `Mt5OrderCheckRequestDTO`.
4. Execute `order_check()`.
5. Persist check record in `mt5_order_checks`.
6. If check fails, fail job and set campaign `PARTIALLY_PLACED`.
7. Execute `order_send()`.
8. Persist attempt record in `mt5_execution_attempts`.
9. Update planned entry and campaign state.
