# System Status Aggregation Specification

## Aggregated Status DTO
Endpoint `GET /api/v1/system/status` aggregates real-time health across all system components:

- `service`: Service identifier (`"trading-service"`)
- `version`: System status contract version (`"1.0.0"`)
- `automation_state`: System control state (`PAUSED`, `RUNNING`, `EMERGENCY_STOPPED`)
- `trading_enabled`: Boolean flag indicating if demo trading is unlocked.
- `database`: Database connection status and pending migrations.
- `mt5_adapter`: Status of MT5 IPC connector, broker login, server, environment (`DEMO`).
- `whatsapp_worker`: Connection state of Baileys Node.js WhatsApp worker adapter.
- `outbox_queue`: Pending outbox event count and dispatch metrics.
