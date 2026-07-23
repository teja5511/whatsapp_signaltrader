# Requirements Specification — WhatsApp to MT5 XAUUSD Trading System

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Approved & Frozen  

---

## 1. Functional Requirements (FR)

| ID | Title | Description | Acceptance Traceability |
|---|---|---|---|
| **FR-001** | WhatsApp Ingestion | The system shall continuously monitor one specific user-selected WhatsApp group using a single authenticated WhatsApp account via OpenWA worker. | AC-WA-001 |
| **FR-002** | Sender Verification | The system shall reject all incoming messages unless sent by the verified designated group Administrator phone number/JID. | AC-WA-002 |
| **FR-003** | Signal Parser Engine | The system shall parse incoming XAUUSD/Gold signal text into structured data (Symbol, Direction, Entry Range/Price, Stop Loss, TP1, TP2, TP Open). | AC-PRS-001 |
| **FR-004** | Follow-up Command Parser | The system shall parse follow-up admin instructions (e.g. Move SL, Close Partial, Cancel Pending, Zone Valid, Skip for now, etc.). | AC-PRS-002 |
| **FR-005** | Entry Ladder Calculation | The system shall calculate an evenly spaced entry ladder containing between 3 and 8 pending order levels across the specified entry range (inclusive of both boundaries). Default count is 5. | AC-GRD-001, AC-GRD-002 |
| **FR-006** | Per-Entry Lot Allocation | The lot size configured in the system shall apply to each individual entry order in the ladder (e.g., 5 entries at 0.30 lots = 1.50 total lots). | AC-GRD-003 |
| **FR-007** | Take Profit Allocation Engine | For a campaign of $N$ positions, the system shall assign exactly 1 position to Signal TP1, exactly 1 position to Signal TP2, and all remaining $N-2$ positions to the fixed 100-pip TP target. | AC-GRD-004 |
| **FR-008** | TP Open Metadata Retention | The system shall store `TP Open` as signal metadata in the database without creating unmanaged open runners lacking a hard TP in v1. | AC-GRD-005 |
| **FR-009** | Execution Mode - Automatic | In Automatic Mode, parsed and validated campaigns shall automatically create pending orders in MetaTrader 5 without manual intervention. | AC-EXEC-001 |
| **FR-010** | Execution Mode - Confirmation | In Confirmation Mode, parsed campaigns shall enter `AWAITING_CONFIRMATION` status and present an interactive prompt on the Tauri dashboard requiring user approval/rejection. | AC-EXEC-002 |
| **FR-011** | Unlimited Confirmation Expiry | A campaign awaiting confirmation shall remain valid indefinitely until approved, rejected, explicitly cancelled/exited by admin, or superseded by a finalized replacement rule. | AC-EXEC-003 |
| **FR-012** | MetaTrader 5 Adapter | The system shall execute pending orders, SL/TP modifications, and position closures on MetaTrader 5 using the official Python MT5 API connected to an Exness account. | AC-MT5-001 |
| **FR-013** | Desktop Dashboard | The system shall provide a local Tauri (React) GUI displaying real-time WhatsApp feed, campaign state machine progress, active MT5 grid orders, positions PnL, and emergency controls. | AC-UI-001 |
| **FR-014** | REST & WebSocket API | The Python backend service (FastAPI) shall provide local REST endpoints for UI actions and WebSocket channels for streaming real-time events. | AC-API-001 |

---

## 2. Non-Functional Requirements (NFR)

| ID | Title | Description | Acceptance Traceability |
|---|---|---|---|
| **NFR-001** | Platform & OS Target | The application backend and worker components shall run natively on Windows Desktop 10/11 x64. | AC-SYS-001 |
| **NFR-002** | Signal Latency | Signal processing from WhatsApp ingestion to MT5 order placement request shall complete in under 500 milliseconds. | AC-PERF-001 |
| **NFR-003** | Local Data Persistence | All messages, signals, campaigns, orders, positions, state transitions, and audit events shall be persisted locally in SQLite with WAL mode. | AC-DB-001 |
| **NFR-004** | Startup Reconciliation | Upon application restart, the system shall query MT5 active orders/positions, match against local database records, and reconcile state before resuming processing. | AC-REC-001 |
| **NFR-005** | Local Data Privacy | No signal data or credentials shall be transmitted to external servers or cloud services except direct local communication with WhatsApp and MT5 terminal. | AC-SEC-001 |

---

## 3. Safety & Security Requirements (SAFE)

| ID | Title | Description | Acceptance Traceability |
|---|---|---|---|
| **SAFE-001** | Maximum Exposure Limit | The system shall strictly block execution if `entry_count * lot_per_entry > 2.00` total lots, displaying an explicit validation error without silently reducing lot sizes. | AC-SAFE-001 |
| **SAFE-002** | Symbol Boundary Guard | The system shall restrict all trading execution exclusively to `XAUUSD` (and broker-suffixed equivalents such as `XAUUSDm`), rejecting any other trading pair. | AC-SAFE-002 |
| **SAFE-003** | Hedging Account Enforcer | The system shall verify upon connection that the MT5 account supports Hedging. Execution shall be blocked if Netting is detected. | AC-SAFE-003 |
| **SAFE-004** | Demo Account Guard | The system shall detect and visually display whether the MT5 account is Demo or Live, requiring explicit acknowledgement when running. | AC-SAFE-004 |
| **SAFE-005** | Idempotency & Duplicate Guard | The system shall maintain unique constraint checks on WhatsApp Message IDs and raw content hash to prevent duplicate order placement from re-sent messages. | AC-SAFE-005 |
| **SAFE-006** | Single Execution Queue | All MT5 trading requests shall pass through a single serialized execution queue to eliminate thread race conditions and duplicate order placement. | AC-SAFE-006 |
| **SAFE-007** | Emergency Close-All | The system shall provide a manual UI Emergency Close-All button that cancels all pending grid orders and closes all open campaign positions immediately. | AC-SAFE-007 |
