# Planning REST API Specification

Document Version: 1.0.0 (Phase 6 Planning API)  
Status: Approved & Implemented  

---

## Endpoints

1. `GET /api/v1/planning/version` — Returns planner and risk engine versions (`1.0.0`).
2. `GET /api/v1/planning/policies` — Returns active planning policy snapshot.
3. `POST /api/v1/planning/preview` — Stateless planning preview endpoint (no DB persistence).
4. `POST /api/v1/campaigns/{campaign_id}/plan` — Plans entries for approved campaign and persists `planned_entries` rows (201 Created / 200 Idempotent).
5. `GET /api/v1/campaigns/{campaign_id}/plan` — Gets campaign plan summary.
6. `GET /api/v1/campaigns/{campaign_id}/planned-entries` — Returns array of planned entry records.
