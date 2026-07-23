# MT5 Symbol Resolution Specification

Document Version: 1.0.0 (Phase 7 Symbol Resolution)  
Status: Approved & Implemented  

---

## 1. Resolution Priority Strategy

For canonical symbol `XAUUSD`:
1. `MT5_SYMBOL_OVERRIDE` if configured.
2. Exact match `XAUUSD`.
3. Suffix variants starting with `XAUUSD` (e.g. `XAUUSDm`, `XAUUSD.a`, `XAUUSDc`).
4. Alias `GOLD` if confirmed by broker symbol metadata.

---

## 2. Ambiguity & Missing Symbol Rules

- Zero matches $\rightarrow$ raises `XAUUSDSymbolNotFoundError` (`XAUUSD_SYMBOL_NOT_FOUND`).
- Multiple equal matches $\rightarrow$ raises `XAUUSDSymbolAmbiguousError` (`XAUUSD_SYMBOL_AMBIGUOUS`).
