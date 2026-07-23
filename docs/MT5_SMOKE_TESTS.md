# Real MT5 Demo Smoke Tests Specification

Document Version: 1.0.0 (Phase 7 Smoke Tests)  
Status: Explicit Opt-In Required  

---

## Environment Opt-In Requirements

To run real MT5 demo smoke tests against a live terminal:
```text
RUN_MT5_DEMO_SMOKE_TESTS=true
MT5_ADAPTER_MODE=real
MT5_EXECUTION_ENABLED=true
MT5_DEMO_ONLY=true
```

## Status

**NOT RUN — manual demo opt-in required.**  
Normal automated pytest and CI runs use `FakeMT5Adapter` and `DryRunMT5Adapter` exclusively.
