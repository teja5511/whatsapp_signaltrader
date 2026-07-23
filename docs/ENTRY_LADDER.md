# Entry Ladder Specification

Document Version: 1.0.0 (Phase 6 Entry Ladder)  
Status: Approved & Implemented  

---

## 1. Distribution Formula

```text
step = (zone_high - zone_low) / (entry_count - 1)
level[i] = zone_low + step * i
```

- Boundaries preserved: `level[0] == zone_low`, `level[N-1] == zone_high`.
- Supported entry counts: 3 to 8 inclusive. Default: 5 entries.

---

## 2. Price Normalization & Collision Detection

- Levels normalized to symbol tick size (`0.01` for XAUUSD) using `ROUND_HALF_UP`.
- `PRICE_NORMALIZATION_COLLISION` emitted if tick rounding creates duplicate price levels.
