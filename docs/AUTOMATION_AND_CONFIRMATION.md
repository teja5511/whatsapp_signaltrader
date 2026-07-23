# Automation & User Confirmation Policy Framework

## Execution Modes
1. **`CONFIRMATION` Mode (Default Safety Protocol)**:
   - Signals from WhatsApp are parsed into valid campaigns.
   - Campaign enters state `AWAITING_CONFIRMATION`.
   - Requires explicit HTTP POST `/api/v1/campaigns/{campaign_id}/approve` or `/api/v1/orchestration/campaigns/{campaign_id}/approve`.

2. **`AUTOMATIC` Mode**:
   - Enabled only when `trading_enabled = True` and `automation_state = RUNNING`.
   - Requires confirmation phrase `"ENABLE DEMO XAUUSD TRADING"`.
   - Automatically generates limit entry ladder and queues MT5 execution batch.

## Emergency Protocols
- **Emergency Stop Phrase**: `"RESET EMERGENCY STOP"` required to clear `EMERGENCY_STOPPED` state.
- **Trading Control Phrase**: `"ENABLE DEMO XAUUSD TRADING"` required to enable live execution on Exness MT5 Hedging Demo Account.
