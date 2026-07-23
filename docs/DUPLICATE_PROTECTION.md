# Duplicate Protection & Fingerprinting Specification

Document Version: 1.0.0 (Phase 5 Duplicate Protection)  
Status: Approved & Implemented  

---

## 1. Exact Message Duplicate Key
- **Format**: `EXACT_MESSAGE:<group_id>:<whatsapp_message_id>`
- **Scope**: Rejections identical raw WhatsApp message submissions across restarts.

---

## 2. Semantic Signal Fingerprint
- **Format**: `SEMANTIC_SIGNAL:<sha256_hash>`
- **Canonical JSON Object**:
  ```json
  {
    "direction": "SELL",
    "group_id": "group-id",
    "instrument": "XAUUSD",
    "order_intent": "LIMIT",
    "sender_id": "admin-id",
    "stop_loss": "4008.00000000",
    "tp1": "4112.00000000",
    "tp2": "4104.00000000",
    "tp_open_present": false,
    "zone_high": "3998.00000000",
    "zone_low": "3990.00000000"
  }
  ```
- **Window**: Default `24 hours` (`semantic_duplicate_window_hours = 24`).
- **Exception**: Explicit re-entry commands bypass duplicate window blocks and create linked child campaigns.
