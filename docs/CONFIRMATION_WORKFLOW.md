# User Confirmation Workflow Specification

Document Version: 1.0.0 (Phase 5 Confirmation)  
Status: Approved & Implemented  

---

## Confirmation Operations

- **`POST /api/v1/campaigns/{campaign_id}/approve`**:
  - Transitions `AWAITING_CONFIRMATION` $\rightarrow$ `PLANNED`.
  - Increments optimistic concurrency `version`.
  - Logging `USER_APPROVED` state transition.
  - Zero entry ladder generation or MT5 trade execution.
- **`POST /api/v1/campaigns/{campaign_id}/reject`**:
  - Transitions `AWAITING_CONFIRMATION` $\rightarrow$ `REJECTED`.
  - Logging `USER_REJECTED` state transition.
