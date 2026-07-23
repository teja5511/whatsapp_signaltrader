# Central FastAPI Background Worker Orchestration & Lifecycle

## Overview
The Orchestration Coordinator (`OrchestrationCoordinator`) is the central orchestrator responsible for managing end-to-end execution across the WhatsApp-to-MT5 XAUUSD trading bot pipeline.

```
WhatsApp Ingestion --> Message Parsing --> Campaign Lifecycle --> Confirmation Gating --> Preflight Checks --> MT5 Batch Queue --> Worker Execution
```

## System Control States
1. **`PAUSED`**: All automated state transitions and trade placements are blocked. Incoming signals transition to `AWAITING_CONFIRMATION`.
2. **`RUNNING`**: Automated campaign planning and MT5 execution operate according to execution policy (`AUTOMATIC` vs `CONFIRMATION`).
3. **`EMERGENCY_STOPPED`**: Complete system lockdown. All pending orders and open positions can be closed via emergency protocol. Resets require explicit control phrase `"RESET EMERGENCY STOP"`.

## High-Availability & Idempotency
- **Idempotency Keying**: Deterministic SHA-256 digest (`orchestrator_version:source_type:source_id`).
- **Transactional Outbox**: All state transitions generate immutable `DomainEventModel` and `OutboxEntryModel` within single Unit of Work DB transactions.
