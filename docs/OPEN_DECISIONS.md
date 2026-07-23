# Open & Unresolved Decisions Log

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Active — Pending User Clarification  

---

## Overview

This document tracks all trading-rule decisions and edge-case behaviors that remain unresolved. To maintain system reliability and safety, unresolved items will **NOT be guessed** or hardcoded without explicit user approval.

---

## Unresolved Decision Items Catalog

### Item 1: Exact Price-Distance Meaning of 100 XAUUSD Pips
- **Description**: In gold trading (XAUUSD), "pip" terminology varies across brokers. 100 pips could mean a price change of **$1.00** (e.g. 4120.00 to 4121.00) or **$10.00** (e.g. 4120.00 to 4130.00).
- **Available Options**:
  - *Option A*: 100 pips = $1.00 price delta (100 points / $0.01 digits).
  - *Option B*: 100 pips = $10.00 price delta (1000 points).
- **Recommended Option**: Option A ($1.00 price delta) as standard 2-decimal gold pip, configurable via setting.
- **Safety Implications**: Incorrect pip definition could set TP 10x too wide or 10x too tight.
- **Implementation Status**: Implementation of fixed 100-pip calculation logic in Phase 6 is blocked until confirmed.
- **Required User Decision**: Specify exact dollar delta for "100 pips".

---

### Item 2: Behavior When Price is Already Inside Signal Zone
- **Description**: When a signal arrives for zone `4120-4128`, but live XAUUSD market price is currently `4124.00` (mid-zone).
- **Available Options**:
  - *Option A*: Place `BUY_LIMIT` for levels below 4124, and `BUY_STOP` for levels above 4124.
  - *Option B*: Execute instant Market Orders for levels below 4124, and `BUY_LIMIT` for levels above.
  - *Option C*: Reject the signal as stale.
- **Recommended Option**: Option A (Limit/Stop split depending on current price).
- **Safety Implications**: Market orders could experience slippage.
- **Implementation Status**: Non-blocking for parser/DB (Phase 3-5), blocked for Grid Calculator (Phase 6).
- **Required User Decision**: Select Option A, B, or C.

---

### Item 3: Behavior When Price Has Passed the Full Zone
- **Description**: Signal arrives for `Sell 4120-4128`, but current market price has already dropped to `4110.00` (far below zone).
- **Available Options**:
  - *Option A*: Place `SELL_LIMIT` orders at `4120-4128` anyway, waiting for retracement.
  - *Option B*: Cancel/Expire the signal as missed.
- **Recommended Option**: Option A (Place limit orders as requested).
- **Safety Implications**: Option B prevents chasing trades.
- **Implementation Status**: Non-blocking for early phases.
- **Required User Decision**: Select Option A or B.

---

### Item 4: Delayed TP1 / TP2 Message Arrival Timing
- **Description**: Admin posts entry zone and SL first, then posts TP1/TP2 in a separate message 30 seconds later.
- **Available Options**:
  - *Option A*: Wait in `WAITING_FOR_TP` state without placing MT5 orders until TP message arrives.
  - *Option B*: Place grid orders immediately with temporary default 100-pip TPs, then update TPs when message arrives.
- **Recommended Option**: Option A (Wait for complete signal parameters before MT5 placement).
- **Safety Implications**: Option A prevents placing trades without complete exit plans.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Select Option A or B.

---

### Item 5: Exact Ladder Index Assignment for TP1 & TP2
- **Description**: For 5 entries (indices 0, 1, 2, 3, 4), which specific indices get TP1 and TP2?
- **Available Options**:
  - *Option A*: Index 0 gets TP1, Index 1 gets TP2, Indices 2,3,4 get 100-pip TP.
  - *Option B*: Deepest entry (Index 4) gets TP1, Index 3 gets TP2, Indices 0,1,2 get 100-pip TP.
- **Recommended Option**: Option A (Lowest index $\rightarrow$ TP1).
- **Safety Implications**: Ensures deterministic position exit mapping.
- **Implementation Status**: Blocked for Phase 6 grid mapping module.
- **Required User Decision**: Confirm index mapping schedule.

---

### Item 6: Interpretation of `Secure Profits`
- **Description**: Admin posts message `Secure Profits`.
- **Available Options**:
  - *Option A*: Automatically move SL to Break Even for all active positions.
  - *Option B*: Automatically close 50% of active position volume.
  - *Option C*: Treat as `AMBIGUOUS_COMMAND` and prompt user UI confirmation card.
- **Recommended Option**: Option C (Confirmation prompt only; never automate ambiguous commands).
- **Safety Implications**: Prevents unintentional position liquidation.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Select Option A, B, or C.

---

### Item 7: Interpretation of `Exit this trade on your comfort`
- **Description**: Admin posts message `Exit this trade on your comfort`.
- **Available Options**:
  - *Option A*: Treat as informational commentary; take no automated MT5 action.
  - *Option B*: Prompt UI confirmation card with one-click "Close All" button.
- **Recommended Option**: Option B (Dashboard user notification with exit button).
- **Safety Implications**: Zero automatic execution risk.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Confirm Option B.

---

### Item 8: Interpretation of `Hold it`
- **Description**: Admin posts `... Hold it`.
- **Available Options**:
  - *Option A*: Informational log entry only.
  - *Option B*: Temporarily freeze automated trailing SL modifications.
- **Recommended Option**: Option A.
- **Safety Implications**: Safe informational logging.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Confirm Option A.

---

### Item 9: Behavior When New Signal Arrives While Previous Campaign Active
- **Description**: Admin posts a new `Gold Buy` signal while a `Gold Sell` campaign is currently active.
- **Available Options**:
  - *Option A*: Cancel/close previous campaign before executing new signal.
  - *Option B*: Allow both campaigns to coexist independently using distinct Magic Numbers (Hedging account mode).
- **Recommended Option**: Option B (Coexist via distinct MT5 Magic Numbers).
- **Safety Implications**: Requires hedging account support (enforced by SAFE-003).
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Select Option A or B.

---

### Item 10: Active Filled Positions After New Signal
- **Description**: When a campaign is replaced or cancelled by a new signal, should already-filled market positions be closed or left open under old SL/TP?
- **Available Options**:
  - *Option A*: Close open market positions immediately.
  - *Option B*: Leave open market positions running under their existing SL/TP, while cancelling only pending grid orders.
- **Recommended Option**: Option B (Protect open fills).
- **Safety Implications**: Option A incurs instant spread/realized PnL loss.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Select Option A or B.

---

### Item 11: Action of `Skip this for now` on Active Pending Orders
- **Description**: Admin posts `Skip this for now` for an active campaign.
- **Available Options**:
  - *Option A*: Cancel all MT5 pending grid orders for the campaign.
  - *Option B*: Pause campaign automation without deleting MT5 orders.
- **Recommended Option**: Option A (Cancel pending grid orders).
- **Safety Implications**: Eliminates unfilled pending order exposure.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Select Option A or B.

---

### Item 12: Action of `Zone Valid` on Paused Campaigns
- **Description**: Admin posts `Zone Valid` after a previous skip or pause.
- **Available Options**:
  - *Option A*: Reactivate paused campaign and re-submit pending grid orders.
  - *Option B*: Display UI notification letting user manually re-enable campaign.
- **Recommended Option**: Option B.
- **Safety Implications**: Requires user confirmation before re-submitting orders.
- **Implementation Status**: Non-blocking.
- **Required User Decision**: Select Option A or B.
