# Parser Classification & Precedence Table

Document Version: 1.0.0 (Phase 4 Parser)  
Status: Approved & Implemented  

---

## Precedence Evaluation Hierarchy

When a message is evaluated by `classification.py`, pattern matching follows this strict order of priority:

1. **Unsupported Instrument Guard**: Rejects explicit non-XAUUSD instruments (`BTCUSD`, `EURUSD`, etc.) $\rightarrow$ `UNSUPPORTED`.
2. **Full or Incomplete NEW_SIGNAL**: Matched if message has explicit direction (`BUY`/`SELL`) and valid entry zone `[low, high]`.
3. **Explicit FOLLOW_UP_COMMAND**: Matched for `MODIFY_STOP_LOSS`, `CLOSE_CAMPAIGN`, `CANCEL_SIGNAL`, `ZONE_VALID`, `REENTRY`, `ADD_TAKE_PROFIT`.
4. **AMBIGUOUS Command**: Matched for phrases like `Secure Profits`, `Exit on your comfort`, `Hold it`, `Skip this for now` $\rightarrow$ `requiresConfirmation = true`, `isExecutable = false`.
5. **INFORMATIONAL Message**: Matched for commentary like `We barely survived the SL`, `50+ Pips`, `100 Pips Almost`, `Wait for update` $\rightarrow$ `isExecutable = false`, `executionEligibility = NEVER`.
6. **INVALID Fallback**: Triggered when no valid signal, command, or commentary structure is recognized.
