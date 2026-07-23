# WhatsApp Worker Local REST API Specification

Document Version: 1.0.0 (Phase 8 API)  
Status: Approved & Implemented  

---

## Endpoints

### Unauthenticated Public Endpoints
- `GET /health`
- `GET /ready`
- `GET /version`

### Authenticated Endpoints (Requires `Authorization: Bearer <LOCAL_API_TOKEN>`)
- `GET /status`
- `GET /metrics`
- `GET /configuration`
- `GET /session`
- `GET /session/qr`
- `GET /groups`
- `GET /groups/:group_id/admins`
- `GET /spool`
- `GET /quarantine`
- `GET /events` (SSE Event Stream)
- `POST /start`
- `POST /stop`
- `POST /session/logout`
- `POST /session/reset`
- `POST /configuration/group`
- `POST /configuration/admin`
- `POST /quarantine/:item_id/requeue`
