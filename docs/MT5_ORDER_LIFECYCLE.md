# MT5 Order Lifecycle Specification

Document Version: 1.0.0 (Phase 7 Order Lifecycle)  
Status: Approved & Implemented  

---

## 1. Pending Order Operations

- **Modification**: `POST /api/v1/mt5/orders/{order_ticket}/modify`
- **Deletion**: `DELETE /api/v1/mt5/orders/{order_ticket}`
- **Campaign Pending Cancellation**: `POST /api/v1/mt5/campaigns/{campaign_id}/cancel-pending`

---

## 2. Validation & Ownership

- Operations verify ownership by ticket, magic number, and symbol.
- Requires local API Bearer token authentication (`Authorization: Bearer <LOCAL_API_TOKEN>`).
