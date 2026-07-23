# Parser REST API Specification

Document Version: 1.0.0 (Phase 4 Parser)  
Status: Approved & Implemented  

---

## Endpoints

### 1. `GET /api/v1/parser/version`
Returns parser version metadata:
```json
{
  "parser_version": "1.0.0",
  "contract_version": "1.0.0",
  "deterministic": true,
  "ai_enabled": false,
  "trading_enabled": false
}
```

### 2. `POST /api/v1/parser/preview`
Parses raw message text without database persistence or trade execution.

### 3. `POST /api/v1/parser/messages`
Parses raw message text, stores `whatsapp_messages`, `parsed_messages`, `signals` (if signal), and audit log. Returns HTTP 201 for new messages or HTTP 200 for duplicate submissions.

### 4. `GET /api/v1/parser/messages/{raw_message_id}`
Retrieves stored raw WhatsApp message and associated parsed result JSON.
