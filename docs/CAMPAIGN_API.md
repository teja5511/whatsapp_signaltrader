# Campaign REST API Specification

Document Version: 1.0.0 (Phase 5 Campaign API)  
Status: Approved & Implemented  

---

## Endpoints

1. `GET /api/v1/campaigns` — Lists active/all campaigns with status filters.
2. `GET /api/v1/campaigns/{campaign_id}` — Gets detailed campaign representation.
3. `GET /api/v1/campaigns/{campaign_id}/transitions` — Retrieves complete append-only state transition history.
4. `GET /api/v1/campaigns/{campaign_id}/commands` — Retrieves attached follow-up commands.
5. `GET /api/v1/campaigns/{campaign_id}/duplicate-records` — Retrieves duplicate key records.
6. `GET /api/v1/campaigns/state-machine` — Gets allowed transition rules matrix.
7. `GET /api/v1/campaigns/state-machine/version` — Gets state machine version (`1.0.0`).
8. `GET /api/v1/duplicates/version` — Gets duplicate strategy version (`1.0.0`).
9. `POST /api/v1/campaigns/from-message/{raw_message_id}` — Creates campaign from parsed signal (201 Created / 200 Duplicate).
10. `POST /api/v1/campaigns/{campaign_id}/approve` — Approves campaign (`AWAITING_CONFIRMATION` $\rightarrow$ `PLANNED`).
11. `POST /api/v1/campaigns/{campaign_id}/reject` — Rejects campaign (`AWAITING_CONFIRMATION` $\rightarrow$ `REJECTED`).
12. `POST /api/v1/campaigns/process-message/{raw_message_id}` — Processes follow-up command / re-entry message against active campaigns.
