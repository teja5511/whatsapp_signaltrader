# Campaign State Machine Specification

Document Version: 1.0.0 (Phase 5 State Machine)  
Status: Approved & Implemented  

---

## 1. Allowed Transition Matrix

| From State | Allowed Target States |
| :--- | :--- |
| `RECEIVED` | `PARSED`, `INVALID` |
| `PARSED` | `WAITING_FOR_TP`, `AWAITING_CONFIRMATION`, `INVALID` |
| `WAITING_FOR_TP` | `WAITING_FOR_TP`, `AWAITING_CONFIRMATION`, `CANCELLED`, `REJECTED`, `FAILED` |
| `AWAITING_CONFIRMATION` | `AWAITING_CONFIRMATION`, `PLANNED`, `CANCELLED`, `REJECTED`, `FAILED` |
| `PLANNED` | `CANCELLED`, `FAILED` |

---

## 2. Terminal States & Guards

- **Terminal States**: `INVALID`, `CLOSED`, `CANCELLED`, `REJECTED`, `FAILED`.
- **Forbidden Transitions**: Direct transitions out of terminal states or to execution states (`OPEN`, `PENDING`, `PLACING_ORDERS`) are rejected with `InvalidStateTransitionError`.
- **Transition Logging**: Every transition persists an append-only `CampaignStateTransitionModel` record storing `from_state`, `to_state`, `reason_code`, `trigger_type`, and `correlation_id`.
