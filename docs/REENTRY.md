# Explicit Re-entry Specification

Document Version: 1.0.0 (Phase 5 Re-entry)  
Status: Approved & Implemented  

---

## Re-entry Lifecycle

- **Trigger**: Parsed `REENTRY` command (`Same Zone for Re-entry`, `Re-enter same zone`).
- **Child Campaign Creation**: Instantiates a new linked child campaign copying signal parameters (`instrument`, `direction`, `zone`, `stop_loss`, `tp1`, `tp2`).
- **Hierarchy Linkage**:
  - `parent_campaign_id`: Source campaign ID.
  - `reentry_sequence`: `parent.reentry_sequence + 1`.
- **Settings Snapshot**: Re-evaluates current `AppSettings` for lot per entry and maximum exposure cap.
