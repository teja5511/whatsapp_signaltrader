# Planning Policies Specification

Document Version: 1.0.0 (Phase 6 Planning Policies)  
Status: Approved & Implemented  

---

## Explicit Policy Contracts

1. **HundredPipDistancePolicy**: `price_distance` (`None` in production default; e.g. `1.00000000` in fixture).
2. **CurrentPriceZonePolicy**: `NO_CURRENT_PRICE_CHECK` (default), `BLOCK_IF_INSIDE_ZONE`, `BLOCK_IF_ZONE_PASSED`.
3. **TpIndexAllocationPolicy**: `UNRESOLVED` (production default), `OUTER_BOUNDARIES_TO_SIGNAL_TPS`, `EXPLICIT_INDICES`.
4. **UnspecifiedOrderIntentPolicy**: `BLOCK` (production default), `TREAT_AS_LIMIT`.
