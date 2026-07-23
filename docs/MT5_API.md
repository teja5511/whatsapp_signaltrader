# MT5 REST API Specification

Document Version: 1.0.0 (Phase 7 API)  
Status: Approved & Implemented  

---

## Endpoints Summary

### Read-Only Endpoints
- `GET /api/v1/mt5/version`
- `GET /api/v1/mt5/status`
- `GET /api/v1/mt5/terminal`
- `GET /api/v1/mt5/account`
- `GET /api/v1/mt5/symbol`
- `GET /api/v1/mt5/symbol/specification`
- `POST /api/v1/mt5/execution/preflight/{campaign_id}`
- `GET /api/v1/mt5/execution/jobs`
- `GET /api/v1/mt5/execution/jobs/{job_id}`
- `GET /api/v1/mt5/execution/batches/{batch_id}`

### Mutating Endpoints (Requires `Authorization: Bearer <LOCAL_API_TOKEN>`)
- `POST /api/v1/mt5/initialize`
- `POST /api/v1/mt5/shutdown`
- `POST /api/v1/mt5/synchronize`
- `POST /api/v1/mt5/execution/campaigns/{campaign_id}` (Returns `202 Accepted`)
- `POST /api/v1/mt5/execution/jobs/{job_id}/cancel`
- `POST /api/v1/mt5/orders/{order_ticket}/modify`
- `DELETE /api/v1/mt5/orders/{order_ticket}`
- `POST /api/v1/mt5/campaigns/{campaign_id}/cancel-pending`
- `POST /api/v1/mt5/positions/{position_ticket}/modify-sltp`
- `POST /api/v1/mt5/positions/{position_ticket}/close`
- `POST /api/v1/mt5/campaigns/{campaign_id}/close`
- `POST /api/v1/mt5/emergency/close-all-xauusd`
