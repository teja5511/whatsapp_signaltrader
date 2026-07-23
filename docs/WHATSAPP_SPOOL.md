# WhatsApp Durable Spool & Delivery Specification

Document Version: 1.0.0 (Phase 8 Spool)  
Status: Approved & Implemented  

---

## 1. Directory Structure

```text
data/spool/
├── pending/
├── delivering/
├── delivered/
└── quarantine/
```

- Each envelope is written atomically (`.tmp` $\rightarrow$ `.json`).
- Filename format: `<sequence>-<sha256-idempotency-key>.json`.
- State transitions: `pending` $\rightarrow$ `delivering` $\rightarrow$ `delivered` or `quarantined`.

---

## 2. Delivery Client

- Targets `POST /api/v1/parser/messages` on `TRADING_SERVICE_URL`.
- Sends Bearer token header `Authorization: Bearer <LOCAL_API_TOKEN>`.
- HTTP 200/201 marked delivered. HTTP 401/403/422 moved to quarantine.
