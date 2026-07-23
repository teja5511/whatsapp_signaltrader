# Command Classification Specification — WhatsApp Signal & Admin Message Parser

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Approved & Frozen  

---

## 1. Classification & Parsing Taxonomy

Incoming messages from the verified group administrator are classified into four primary categories:

1. **PRIMARY_SIGNAL**: New trade setup establishing symbol, direction, entry zone, SL, and TPs.
2. **EXECUTABLE_COMMAND**: Direct follow-up command with explicit mathematical/actionable targets (e.g. set SL to exact price, close all positions).
3. **AMBIGUOUS_COMMAND**: Command expressing intent but lacking deterministic boundaries (e.g., "Exit on your comfort", "Secure Profits"). Requires manual user confirmation or UI alert.
4. **INFORMATIONAL_MESSAGE**: Commentary, progress updates, or market notes with zero direct execution impact (e.g., "50+ Pips", "We barely survived the SL").

---

## 2. Command Analysis Matrix

Below is the complete classification breakdown for all target admin message variants:

### 1. `Move SL to 4138 for added safety`
- **Normalized Text**: `MOVE SL TO 4138 FOR ADDED SAFETY`
- **Classification**: `EXECUTABLE_COMMAND`
- **Extracted Values**: `action="MODIFY_SL"`, `new_sl=4138.0`
- **Executable or Informational**: Executable
- **Campaign-Matching Method**: Active XAUUSD campaign (latest open/pending campaign)
- **Execution Mode**: Automatic / Confirmation (Per user mode setting)
- **Expected Action**: Modify SL of all active grid orders and open positions to `4138.0`.
- **Safety Notes**: Verifies `4138.0` is valid relative to current market price and position directions before submitting MT5 modification request.

---

### 2. `We barely survived the SL`
- **Normalized Text**: `WE BARELY SURVIVED THE SL`
- **Classification**: `INFORMATIONAL_MESSAGE`
- **Extracted Values**: `None`
- **Executable or Informational**: Informational
- **Campaign-Matching Method**: N/A
- **Execution Mode**: N/A
- **Expected Action**: Log message to database and stream to dashboard ticker. Take no trade execution action.
- **Safety Notes**: Zero trade execution impact.

---

### 3. `Exit this trade on your comfort`
- **Normalized Text**: `EXIT THIS TRADE ON YOUR COMFORT`
- **Classification**: `AMBIGUOUS_COMMAND`
- **Extracted Values**: `action="SUGGEST_EXIT"`
- **Executable or Informational**: Informational / Manual Action Required
- **Campaign-Matching Method**: Active XAUUSD campaign
- **Execution Mode**: Confirmation-only (Prompt UI Alert)
- **Expected Action**: Display a prominent UI notification on the dashboard: *"Admin suggested exiting active trade at user discretion"*. Provide a one-click "Close All Positions" button. Do **NOT** automatically close positions.
- **Safety Notes**: Ambiguous wording must never trigger automatic market orders.

---

### 4. `Zone Valid`
- **Normalized Text**: `ZONE VALID`
- **Classification**: `AMBIGUOUS_COMMAND` / `UNRESOLVED`
- **Extracted Values**: `action="CONFIRM_ZONE"`
- **Executable or Informational**: Informational (Pending Unresolved Decision #12)
- **Campaign-Matching Method**: Active or Paused XAUUSD campaign
- **Execution Mode**: Confirmation-only
- **Expected Action**: Log and notify user. Unresolved decision #12 governs whether this reactivates a paused campaign.
- **Safety Notes**: Held until rule resolution.

---

### 5. `Skip this for now`
- **Normalized Text**: `SKIP THIS FOR NOW`
- **Classification**: `AMBIGUOUS_COMMAND` / `UNRESOLVED`
- **Extracted Values**: `action="SKIP_CAMPAIGN"`
- **Executable or Informational**: Actionable / Confirmation-only
- **Campaign-Matching Method**: Active pending campaign or signal awaiting confirmation
- **Execution Mode**: Confirmation-only
- **Expected Action**: If campaign is awaiting confirmation, mark as `REJECTED`. Unresolved decision #11 governs whether it cancels active MT5 pending orders.
- **Safety Notes**: Must not delete filled positions without explicit user confirmation.

---

### 6. `Wait for update`
- **Normalized Text**: `WAIT FOR UPDATE`
- **Classification**: `INFORMATIONAL_MESSAGE`
- **Extracted Values**: `action="HOLD_EXECUTION"`
- **Executable or Informational**: Informational
- **Campaign-Matching Method**: Latest signal
- **Execution Mode**: N/A
- **Expected Action**: Log to audit trail and display banner on dashboard UI.
- **Safety Notes**: Prevents automatic placement of pending signals if in approval queue.

---

### 7. `100 Pips Almost`
- **Normalized Text**: `100 PIPS ALMOST`
- **Classification**: `INFORMATIONAL_MESSAGE`
- **Extracted Values**: `milestone="100_PIPS"`
- **Executable or Informational**: Informational
- **Campaign-Matching Method**: Active campaign
- **Execution Mode**: N/A
- **Expected Action**: Record progress milestone in campaign audit log.
- **Safety Notes**: Informational comment only.

---

### 8. `Secure Profits`
- **Normalized Text**: `SECURE PROFITS`
- **Classification**: `AMBIGUOUS_COMMAND` / `UNRESOLVED`
- **Extracted Values**: `action="SECURE_PROFITS"`
- **Executable or Informational**: Actionable / Manual Review
- **Campaign-Matching Method**: Active open campaign
- **Execution Mode**: Confirmation-only (UI Alert)
- **Expected Action**: Raise dashboard alert: *"Admin recommended securing profits (Move SL to BE / Close Partials)"*. Prompt user with choices.
- **Safety Notes**: Unresolved decision #6 governs specific automated defaults.

---

### 9. `Market is very shaky move SL to 4074 for safety`
- **Normalized Text**: `MARKET IS VERY SHAKY MOVE SL TO 4074 FOR SAFETY`
- **Classification**: `EXECUTABLE_COMMAND`
- **Extracted Values**: `action="MODIFY_SL"`, `new_sl=4074.0`
- **Executable or Informational**: Executable
- **Campaign-Matching Method**: Active campaign
- **Execution Mode**: Automatic / Confirmation
- **Expected Action**: Parse target price `4074.0` and update SL for all orders/positions in the campaign via MT5 API.
- **Safety Notes**: Regex extracts explicit numeric target `4074.0` cleanly while ignoring commentary text.

---

### 10. `50+ Pips`
- **Normalized Text**: `50+ PIPS`
- **Classification**: `INFORMATIONAL_MESSAGE`
- **Extracted Values**: `milestone="50_PIPS"`
- **Executable or Informational**: Informational
- **Campaign-Matching Method**: Active campaign
- **Execution Mode**: N/A
- **Expected Action**: Log progress milestone to audit database.
- **Safety Notes**: No trade execution action.

---

### 11. `It will come to Zone again`
- **Normalized Text**: `IT WILL COME TO ZONE AGAIN`
- **Classification**: `INFORMATIONAL_MESSAGE`
- **Extracted Values**: `commentary="REENTRY_EXPECTED"`
- **Executable or Informational**: Informational
- **Campaign-Matching Method**: Active/Pending campaign
- **Execution Mode**: N/A
- **Expected Action**: Log to database and dashboard ticker.
- **Safety Notes**: No automatic order creation.

---

### 12. `Hard SL 4013`
- **Normalized Text**: `HARD SL 4013`
- **Classification**: `EXECUTABLE_COMMAND`
- **Extracted Values**: `action="MODIFY_SL"`, `new_sl=4013.0`
- **Executable or Informational**: Executable
- **Campaign-Matching Method**: Active campaign
- **Execution Mode**: Automatic / Confirmation
- **Expected Action**: Update SL to `4013.0` for all pending grid orders and active positions.
- **Safety Notes**: Validates SL distance before issuing MT5 order modifications.

---

### 13. `Same Zone for Re-entry`
- **Normalized Text**: `SAME ZONE FOR RE-ENTRY`
- **Classification**: `AMBIGUOUS_COMMAND` / `UNRESOLVED`
- **Extracted Values**: `action="REENTRY_ZONE"`
- **Executable or Informational**: Actionable / Manual Review
- **Campaign-Matching Method**: Previous campaign zone
- **Execution Mode**: Confirmation-only
- **Expected Action**: Prompt user in dashboard with option to clone entry grid for previous zone.
- **Safety Notes**: Does not auto-submit orders without user approval.

---

### 14. `Just touched our SL and reversed, if you haven't closed like mine, Hold it`
- **Normalized Text**: `JUST TOUCHED OUR SL AND REVERSED IF YOU HAVENT CLOSED LIKE MINE HOLD IT`
- **Classification**: `INFORMATIONAL_MESSAGE` / `UNRESOLVED`
- **Extracted Values**: `commentary="HOLD_POSITION"`
- **Executable or Informational**: Informational (Pending Unresolved Decision #8)
- **Campaign-Matching Method**: Active campaign
- **Execution Mode**: N/A
- **Expected Action**: Log to database and display informational notification.
- **Safety Notes**: Zero trade modification action.
