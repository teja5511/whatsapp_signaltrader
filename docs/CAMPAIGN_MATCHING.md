# Campaign Matching Specification

Document Version: 1.0.0 (Phase 5 Campaign Matching)  
Status: Approved & Implemented  

---

## Matching Strategy Priority

1. **`MATCHED_BY_QUOTE`**: Direct match via `quoted_message_id` when `is_reply = true`.
2. **`MATCHED_BY_SIGNAL_MESSAGE`**: Exact raw signal message match.
3. **`MATCHED_LATEST_COMPATIBLE`**: Matched against latest active campaign in non-terminal states (`WAITING_FOR_TP`, `AWAITING_CONFIRMATION`, `PLANNED`).
4. **`MATCH_AMBIGUOUS`**: Returned when multiple active candidates exist without explicit reply context.
