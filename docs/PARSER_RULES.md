# Parser Tokenization & Extraction Rules

Document Version: 1.0.0 (Phase 4 Parser)  
Status: Approved & Implemented  

---

## 1. Instrument Recognition Rules
- **Supported**: `XAUUSD`, `Gold`, `XAU/USD`, `XAU USD` $\rightarrow$ Normalized to `XAUUSD`.
- **Unsupported**: `BTCUSD`, `EURUSD`, `US30`, `NAS100`, `GBPUSD`, `Silver`, `XAGUSD` $\rightarrow$ Rejected with `UNSUPPORTED_INSTRUMENT` error.

---

## 2. Direction & Intent Rules
- `Buy`, `Gold Buy` $\rightarrow$ Direction = `BUY`, Intent = `UNSPECIFIED`.
- `Buy Limit`, `Gold Buy Limit` $\rightarrow$ Direction = `BUY`, Intent = `LIMIT`.
- `Sell`, `Gold Sell` $\rightarrow$ Direction = `SELL`, Intent = `UNSPECIFIED`.
- `Sell Limit`, `Gold Sell Limit` $\rightarrow$ Direction = `SELL`, Intent = `LIMIT`.
- Conflicting direction keywords (e.g. `BUY` and `SELL` in same message) $\rightarrow$ `INVALID` result (`DIRECTION_CONFLICT`).

---

## 3. Entry Zone Rules
- Formats: `4120-4128`, `4120 - 4128`, `3990 to 3998`, `Zone 3990-3998`, `Entry 3990-3998`.
- If values are reversed (e.g. `4128-4120`), they are auto-sorted into `zoneLow = 4120.0` and `zoneHigh = 4128.0`, emitting a `ZONE_VALUES_REVERSED` warning.

---

## 4. Take Profit Target Rules
- Up to 2 explicit numeric TPs are mapped to `tp1` and `tp2`.
- `TP Open` text sets `tpOpenPresent = True` without creating unmanaged open runners.
- Additional TPs beyond TP2 produce a `TOO_MANY_TAKE_PROFITS` warning and are retained in metadata.
