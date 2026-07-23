# MT5 Position Operations Specification

Document Version: 1.0.0 (Phase 7 Position Operations)  
Status: Approved & Implemented  

---

## 1. Position Operations

- **SL/TP Modification**: `POST /api/v1/mt5/positions/{position_ticket}/modify-sltp`
- **Position Close**: `POST /api/v1/mt5/positions/{position_ticket}/close`
- **Campaign Positions Close**: `POST /api/v1/mt5/campaigns/{campaign_id}/close`
- **Emergency Close-All XAUUSD**: `POST /api/v1/mt5/emergency/close-all-xauusd`

---

## 2. Emergency Close-All Rules

- Disabled by default (`MT5_CLOSE_ALL_ENABLED=false`).
- Requires exact confirmation phrase `CLOSE ALL DEMO XAUUSD`.
- Operates on DEMO accounts only.
- Scopes: `APPLICATION_OWNED` (default) or `ALL_XAUUSD_ON_ACCOUNT`.
- Never touches non-XAUUSD instruments.
