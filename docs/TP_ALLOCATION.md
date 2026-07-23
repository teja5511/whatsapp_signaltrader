# TP Allocation Specification

Document Version: 1.0.0 (Phase 6 TP Allocation)  
Status: Approved & Implemented  

---

## 1. Category Distribution Rules

- Exactly **1 entry** assigned to `TP_1`.
- Exactly **1 entry** assigned to `TP_2`.
- All remaining **N - 2 entries** assigned to `TP_100` (fixed 100-pip target).

---

## 2. Allocation Policies

- Production default: `UNRESOLVED` (blocks planning until configured).
- Fixture/Explicit policies: `OUTER_BOUNDARIES_TO_SIGNAL_TPS`, `EXPLICIT_INDICES`, `LOWEST_INDICES_TO_SIGNAL_TPS`, `HIGHEST_INDICES_TO_SIGNAL_TPS`.
