# Prompt 6 of 12 Output Report — Entry Ladder, TP Allocation and Risk Engine

Project: WhatsApp XAUUSD Signal Trading Bot  
Location: `C:\Users\Pavan Teja\projects\whatsapp_trading bot`  
Commit: `ded1bd5`  
Status: Phase 6 Complete & Verified  

---

## Executive Summary

Phase 6 (Entry Ladder, TP Allocation, and Risk Engine) has been fully implemented, validated, and committed to the monorepo.

### Critical Data Correction
- Updated default `lot_per_entry` across settings, schemas, and repositories from `0.10` to **`0.3000`**.
- Default campaign of 5 entries now requests **`1.5000` total lots**. Maximum campaign exposure cap remains **`2.0000` total lots**.

---

## Key Modules Delivered

1. **`apps/trading-service/src/planning/ladder.py`**:
   Calculates evenly distributed price entry ladders for 3 to 8 entries preserving exact zone boundaries (`zone_low` to `zone_high`).

2. **`apps/trading-service/src/planning/price_normalization.py` & `volume_normalization.py`**:
   Tick rounding (`ROUND_HALF_UP` to `0.01`), collision detection, volume step alignment (`0.01`), and total exposure cap enforcement (`2.0000` max lots).

3. **`apps/trading-service/src/planning/tp_allocation.py` & `tp_calculation.py`**:
   Allocates exactly 1 `TP_1`, 1 `TP_2`, and remaining `N-2` `TP_100` targets. Calculates 100-pip prices (`entry ± distance`) with explicit `HundredPipDistancePolicy`.

4. **`apps/trading-service/src/planning/risk_engine.py`**:
   Enforces 24 structured risk issue codes (e.g. `TOTAL_VOLUME_EXCEEDED`, `STOP_LOSS_DIRECTION_INVALID`).

5. **`apps/trading-service/src/planning/planner.py` & `service.py`**:
   Generates deterministic 31-bit magic numbers (`sha256(campaign_id + entry_sequence)`), order comments (`WA-GOLD-0001-E01-TP100`), SHA-256 `planning_fingerprint`, and manages DB persistence with idempotent return.

6. **FastAPI Endpoints**:
   - `GET /api/v1/planning/version`
   - `GET /api/v1/planning/policies`
   - `POST /api/v1/planning/preview`
   - `POST /api/v1/campaigns/{campaign_id}/plan`
   - `GET /api/v1/campaigns/{campaign_id}/plan`
   - `GET /api/v1/campaigns/{campaign_id}/planned-entries`

7. **Alembic Migration**: `003_entry_planning_and_risk_engine.py` creating `planned_entries` table.

---

## Verification & Performance Benchmarks

- **Pytest Suite**: All **57 tests** passed cleanly.
- **Entry Ladder Calculation**: 100,000 runs $\rightarrow$ Median: **0.0017 ms**, p95: **0.0018 ms**.
- **Risk Engine Validation**: 10,000 runs $\rightarrow$ Median: **0.0007 ms**, p95: **0.0008 ms**.
- **Workspace Validation (`scripts/validate.ps1`)**: Passed successfully.

---

## Next Steps

Phase 6 is complete. Proceed to Prompt 7 (MT5 Adapter and Demo Execution Worker).
