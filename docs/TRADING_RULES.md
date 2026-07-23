# Trading Rules & Execution Logic Specification

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Approved & Frozen  

---

## 1. Confirmed Trading Rules

### 1.1 Entry Ladder Spacing Formula
- **Entry Count ($N$)**: User-adjustable setting with bounds $3 \le N \le 8$. Initial default dashboard value is **5**.
- **Zone Boundaries**: The ladder includes both lower ($P_{min}$) and upper ($P_{max}$) entry boundaries inclusive.
- **Ladder Formula**: For a given entry count $N$, step size $\Delta P$ is calculated as:
  $$\Delta P = \frac{P_{max} - P_{min}}{N - 1}$$
- **Entry Price Points ($P_i$)**:
  $$P_i = P_{min} + i \cdot \Delta P \quad \text{for } i = 0, 1, \dots, N-1$$

#### Example (5 Entries across Range 4120 – 4128):
- $\Delta P = \frac{4128 - 4120}{5 - 1} = \frac{8}{4} = 2.0$
- Entry 0: `4120.0`
- Entry 1: `4122.0`
- Entry 2: `4124.0`
- Entry 3: `4126.0`
- Entry 4: `4128.0`

---

### 1.2 Lot Sizing & Exposure Rules
- **Per-Entry Lot Sizing**: The user-configured lot size applies to **each individual entry** in the ladder.
  - *Example*: 5 entries $\times$ 0.30 lots per entry = **1.50 total lots**.
- **Maximum Exposure Cap**: Total campaign volume must not exceed **2.00 lots**:
  $$\text{Total Volume} = N \times \text{Lot\_Per\_Entry} \le 2.00$$
- **Validation Failure Guard**: If $N \times \text{Lot\_Per\_Entry} > 2.00$, the system shall **block execution** and raise an explicit UI/system validation error. It shall **NEVER** silently reduce or auto-adjust the lot size.

---

### 1.3 Take Profit (TP) Allocation Rules
For a campaign of $N$ positions, positions are deterministically mapped to TP targets as follows:
- **Signal TP1 Target**: Assigned to exactly **1 position**.
- **Signal TP2 Target**: Assigned to exactly **1 position**.
- **Fixed 100-Pip Target**: Assigned to all remaining **$N - 2$ positions**.

#### TP Mapping Schedule Matrix:

| Total Entries ($N$) | Fixed 100-Pip TP Positions | Signal TP1 Positions | Signal TP2 Positions |
|---:|---:|---:|---:|
| 3 | 1 | 1 | 1 |
| 4 | 2 | 1 | 1 |
| **5 (Default)** | **3** | **1** | **1** |
| 6 | 4 | 1 | 1 |
| 7 | 5 | 1 | 1 |
| 8 | 6 | 1 | 1 |

---

### 1.4 Missing TP & `TP Open` Handling
- **Missing TP1 or TP2**: If a signal text contains only one explicit TP (e.g. `TP 4112`), that TP is treated as TP1, and TP2 defaults to the fixed 100-pip target.
- **`TP Open` Text Handling**: For version 1, `TP Open` text is stored strictly as signal metadata in the database. The system does **NOT** create unmanaged open positions without hard TPs or unmanaged runners. All positions utilize the deterministic 100-pip, TP1, and TP2 allocation.

---

### 1.5 Stop Loss (SL) Modifications
- When an admin sends a follow-up SL modification command (e.g., `Move SL to 4138` or `Set SL to Break Even`), the system iterates over all active pending grid orders and filled open positions belonging to the active campaign and issues MT5 `TRADE_ACTION_SLTP` requests to update the SL parameter.

---

## 2. Summary of Unresolved Trading Rules

The following rules remain open and **must not be guessed** during execution:

1. **Exact price-distance meaning of 100 XAUUSD pips**: Whether 100 pips equals $1.00$ price delta (100 points) or $10.00$ price delta.
2. **Current Price inside Signal Zone**: Behaviour when live price is already inside the entry range upon signal arrival.
3. **Current Price past Signal Zone**: Behaviour when price has already breached the full entry zone.
4. **Order Placement Timing on Delayed TPs**: Whether grid orders are placed immediately if TP1/TP2 are sent in follow-up messages.
5. **Exact Ladder Index Mapping for TP1 & TP2**: Which exact index (e.g. index 0 vs index N-1) receives TP1 vs TP2 vs 100-pip TP.
6. **Interpretation of Informational Admin Messages**: Explicit handling of ambiguous phrases (`Secure Profits`, `Exit on your comfort`, `Hold it`).
7. **Multiple Active Campaigns**: System behaviour when a new signal arrives while an earlier campaign has open positions.
8. **Campaign Interplay on Re-entry / Skip**: Detailed action for `Skip this for now` and `Zone Valid` reactivations.

---
*Note: All unresolved rules will be held in `docs/OPEN_DECISIONS.md` until formal user resolution.*
