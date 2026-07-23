# Acceptance Criteria Specification

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Approved & Frozen  

---

## 1. Grid & Entry Spacing Test Scenarios

### AC-GRD-001: 5 Evenly Spaced Entries across Range 3990 to 3998
- **Given**: System setting `entry_count = 5`.
- **When**: Admin posts signal `Gold Sell 3990-3998 sl - 4010 tp - 3970 tp - 3960`.
- **Then**:
  - System calculates step size $\Delta P = \frac{3998 - 3990}{5 - 1} = 2.0$.
  - System generates 5 planned entry prices: `3990.0`, `3992.0`, `3994.0`, `3996.0`, `3998.0`.
  - Both lower boundary `3990.0` and upper boundary `3998.0` are included.

---

### AC-GRD-002: Entry Count Boundaries (3 through 8)
- **Given**: System settings configured for entry counts $N \in \{3, 4, 5, 6, 7, 8\}$.
- **When**: Signal for range `4000-4014` is processed.
- **Then**:
  - For $N=3$: Step size $7.0$ $\rightarrow$ prices `4000.0`, `4007.0`, `4014.0`.
  - For $N=8$: Step size $2.0$ $\rightarrow$ prices `4000.0`, `4002.0`, `4004.0`, `4006.0`, `4008.0`, `4010.0`, `4012.0`, `4014.0`.
  - Setting $N < 3$ or $N > 8$ raises a UI setting validation error.

---

## 2. Lot Sizing & Exposure Validation Scenarios

### AC-GRD-003: Per-Entry Lot Sizing Calculation
- **Given**: `entry_count = 5` and user config `lot_per_entry = 0.30`.
- **When**: Signal is parsed and campaign is planned.
- **Then**:
  - System creates 5 distinct pending orders, each with `volume = 0.30`.
  - Total campaign volume calculated is $5 \times 0.30 = 1.50$ lots.

---

### AC-SAFE-001: Two-Lot Exposure Cap Blocking
- **Given**: `entry_count = 5` and user config `lot_per_entry = 0.50` (Total $= 2.50$ lots).
- **When**: Admin signal arrives.
- **Then**:
  - Exposure check detects $2.50 > 2.00$ lots.
  - Campaign transitions to `INVALID` state.
  - UI displays error: *"Execution Blocked: Total volume 2.50 lots exceeds 2.00 lot maximum limit"*.
  - Lot size is **NOT** silently reduced; zero orders are sent to MT5.

---

## 3. Take Profit Allocation Scenarios

### AC-GRD-004: 5-Position TP Allocation
- **Given**: 5 entry campaign created for signal with `TP1 = 4112`, `TP2 = 4104`.
- **When**: Planned entries are generated.
- **Then**:
  - Exactly 1 entry is assigned `take_profit = 4112.0` (TP1).
  - Exactly 1 entry is assigned `take_profit = 4104.0` (TP2).
  - Exactly 3 entries are assigned `take_profit` corresponding to fixed 100-pip target.

---

### AC-GRD-005: Delayed TP Message Handling
- **Given**: Admin posts signal with entry range and SL but no TPs.
- **When**: Initial signal is parsed.
- **Then**:
  - Campaign enters `WAITING_FOR_TP` state.
  - No orders are placed in MT5 yet.
- **When**: Admin sends follow-up message `tp - 4112 tp - 4104`.
- **Then**:
  - Campaign links TP payload, completes allocation, and advances to `PLANNED`.

---

## 4. Signal Ingestion & Authorization Scenarios

### AC-WA-002: Direct WhatsApp Replies & Sender Auth
- **Given**: Group chat containing Admin and non-admin members.
- **When**: Non-admin replies to an admin signal with trade commentary.
- **Then**:
  - System rejects non-admin sender JID.
  - Message logged to `whatsapp_messages` with `is_admin = False`.
  - No parser or order placement logic executes.

---

### AC-SAFE-005: Duplicate Message Protection
- **Given**: WhatsApp Web re-transmits an identical signal message ID or hash.
- **When**: Webhook receives duplicate payload.
- **Then**:
  - `duplicate_keys` table lookup detects existing key.
  - Payload is discarded with log: *"Duplicate message ignored"*.

---

## 5. Follow-up Command Scenarios

### AC-CMD-001: SL Modification Command
- **Given**: Active campaign with 3 pending orders and 2 open positions in MT5.
- **When**: Admin posts `Move SL to 4138 for added safety`.
- **Then**:
  - Parser extracts `new_sl = 4138.0`.
  - MT5 execution worker modifies SL for all 5 active tickets to `4138.0`.
  - Database records updated to reflect new SL.

---

### AC-CMD-002: Re-entry Command Handling
- **Given**: Active/previous campaign completed or closed.
- **When**: Admin posts `Same Zone for Re-entry`.
- **Then**:
  - Command categorized as `AMBIGUOUS_COMMAND`.
  - Dashboard presents confirmation card: *"Re-entry requested for Zone 4120-4128. Create campaign?"*.
  - Orders placed only when user clicks "Approve".

---

## 6. System & Safety Control Scenarios

### AC-EXEC-001 / AC-EXEC-002: Automatic vs Confirmation Modes
- **Given**: System set to `CONFIRMATION` mode.
- **When**: Admin signal arrives.
- **Then**:
  - Campaign enters `AWAITING_CONFIRMATION` state.
  - Dashboard prompts user with Approve/Reject modal.
  - No orders sent to MT5 until user clicks Approve.

---

### AC-SAFE-007: Emergency Close-All Execution
- **Given**: 4 active campaigns with pending orders and open positions in MT5.
- **When**: User clicks "EMERGENCY CLOSE ALL" on dashboard.
- **Then**:
  - MT5 adapter cancels all pending orders and closes all market positions immediately.
  - All campaigns transition to `CLOSED` / `CANCELLED`.

---

### AC-REC-001: Restart Reconciliation
- **Given**: System was shut down with 3 active MT5 pending orders.
- **When**: Application restarts.
- **Then**:
  - Startup reconciliation queries MT5 terminal by Magic Number.
  - System matches MT5 tickets with database `pending_orders`.
  - Campaign state restored to `PENDING` without placing duplicate orders.

---

### AC-SAFE-004: Demo / Live Indicator
- **Given**: MT5 connected to an Exness Demo or Real account.
- **When**: System connects to MT5.
- **Then**:
  - UI header displays visual tag (`DEMO ACCOUNT` in Green or `LIVE ACCOUNT` in Flashing Red).
