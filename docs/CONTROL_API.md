# System Control API Specification

## Endpoints
- `GET /api/v1/control/state`: Retrieve current automation state and trading permissions.
- `POST /api/v1/control/automation/pause`: Pause all automated campaign actions.
- `POST /api/v1/control/automation/resume`: Resume automation (`RUNNING`).
- `POST /api/v1/control/emergency-stop`: Trigger emergency stop (`EMERGENCY_STOPPED`).
- `POST /api/v1/control/emergency-stop/reset`: Reset emergency stop using phrase `"RESET EMERGENCY STOP"`.
- `POST /api/v1/control/trading/enable-demo`: Unlock trading using phrase `"ENABLE DEMO XAUUSD TRADING"`.
- `POST /api/v1/control/trading/disable`: Lock trading.
