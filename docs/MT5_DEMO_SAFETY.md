# MT5 Demo Safety & Non-Negotiable Gates

Document Version: 1.0.0 (Phase 7 Safety)  
Status: Approved & Implemented  

---

## 1. Mandatory Safety Configuration

```text
MT5_ADAPTER_MODE=fake
MT5_EXECUTION_ENABLED=false
MT5_DEMO_ONLY=true
MT5_LIVE_EXECUTION_ENABLED=false
MT5_AUTOMATIC_EXECUTION_ENABLED=false
MT5_REQUIRE_MANUAL_CONFIRMATION=true
MT5_CLOSE_ALL_ENABLED=false
```

---

## 2. Blocked Conditions

Execution is immediately blocked and an exception raised under any of the following conditions:
1. `MT5_LIVE_EXECUTION_ENABLED=true` or `MT5_DEMO_ONLY=false` requested.
2. Account environment is `REAL`, `CONTEST`, or `UNKNOWN`.
3. Account margin mode is `NETTING`, `EXCHANGE`, or `UNKNOWN`.
4. `order_check` fails prior to `order_send`.
5. Login or Server is not in configured allowlists (`MT5_ALLOWED_LOGINS`, `MT5_ALLOWED_SERVERS`).
6. Maximum volume exceeds `2.0000` lots.
7. Entry count exceeds 8.
