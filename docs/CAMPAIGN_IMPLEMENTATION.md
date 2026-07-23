# Campaign Implementation Specification

Document Version: 1.0.0 (Phase 5 Campaign Lifecycle)  
Status: Approved & Implemented  

---

## 1. Campaign Factory & Lifecycle Overview

Campaigns act as persistent orchestration wrappers managing trade signals, user approvals, follow-up command attachments, and state transitions prior to entry ladder planning.

```mermaid
graph TD
    Signal[Parsed Signal] --> Factory[Campaign Factory]
    Settings[AppSettings Snapshot] --> Factory
    Factory --> InitState{TP Targets Complete?}
    InitState -- No --> WaitingTP[WAITING_FOR_TP]
    InitState -- Yes --> AwaitingConf[AWAITING_CONFIRMATION]
    WaitingTP -- Delayed TP Received --> AwaitingConf
    AwaitingConf -- User Approve --> Planned[PLANNED]
    AwaitingConf -- User Reject --> Rejected[REJECTED]
    WaitingTP -- Cancel / Close --> Cancelled[CANCELLED]
```

---

## 2. Key Attributes & Concurrency

- **Collision-Safe Campaign Code**: `GOLD-YYYYMMDD-<uuid4_short>` generated transactionally.
- **Magic Number**: Unique random integer identifier assigned per campaign.
- **Optimistic Concurrency**: Atomic version checks (`WHERE id = ? AND version = expected_version`) incrementing `version` on each state mutation to prevent lost updates.
- **No-Execution Guarantee**: Prompt 5 creates planning objects only (`trading_enabled = false`, `execution_performed = false`).
