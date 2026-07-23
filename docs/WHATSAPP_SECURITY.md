# WhatsApp Security & Filtering Rules

Document Version: 1.0.0 (Phase 8 Security)  
Status: Approved & Implemented  

---

## 1. Single-Group & Single-Admin Validation

Messages are accepted ONLY if:
1. Message belongs to approved group (`WHATSAPP_APPROVED_GROUP_ID`).
2. Sender matches approved admin (`WHATSAPP_APPROVED_ADMIN_ID`).
3. Sender currently possesses admin role when `WHATSAPP_REQUIRE_ADMIN_ROLE=true`.
4. Message is NOT sent by bot account itself (`fromMe === false`).
5. Message text is $\le 10,000$ characters.

---

## 2. Redaction & Local Authentication

- All mutating endpoints require `Authorization: Bearer <LOCAL_API_TOKEN>`.
- Log output redacts tokens, session credentials, QR payloads, cookies, and account phone numbers.
