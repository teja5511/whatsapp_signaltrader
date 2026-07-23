# System Assumptions & Baseline Registry

Document Version: 1.0.0 (Phase 1 Freeze)  
Status: Approved & Frozen  

---

## 1. Confirmed Facts (User-Approved Specifications)

The following items are explicitly confirmed and must be strictly enforced:

1. **Target Instrument**: Solely `XAUUSD` (and broker-suffixed equivalents e.g., `XAUUSDm`).
2. **Account Requirement**: Exness MetaTrader 5 **Hedging** account.
3. **Execution Platform**: Windows 10/11 x64 Desktop Application.
4. **Source Filtering**: Single dedicated WhatsApp account listening to one specific WhatsApp group, accepting commands strictly from the verified administrator.
5. **Entry Ladder Bounds**: Adjustable entry count between **3 and 8 entries** inclusive (initial dashboard default: **5**).
6. **Lot Sizing Rule**: Lot size value applies to **each individual entry** (e.g. 5 entries $\times$ 0.30 lot = 1.50 total lots).
7. **Maximum Exposure Ceiling**: Absolute maximum exposure capped at **2.00 total lots**. If $N \times \text{Lot} > 2.00$, execution is blocked with an explicit error.
8. **Take Profit Allocation Strategy**:
   - Exactly 1 position for Signal TP1.
   - Exactly 1 position for Signal TP2.
   - All remaining $N-2$ positions for the fixed 100-pip target.
9. **`TP Open` Text Handling**: Stored as signal metadata in v1; does **NOT** create unmanaged open positions without hard TPs.
10. **Confirmation Mode Expiry**: A campaign awaiting approval remains valid until user approves/rejects, admin cancels/exits, or a new signal supersedes it.

---

## 2. Technical Assumptions

The following technical dependencies are assumed based on platform specifications:

1. **Local Desktop Execution**: Python 3.11+, Node.js 18+, and MetaTrader 5 terminal client are installed on the target Windows host machine.
2. **MT5 API Availability**: Official `MetaTrader5` Python library connects via IPC to an active MT5 terminal running on the same host machine.
3. **WhatsApp Web Connectivity**: OpenWA worker uses Puppeteer to maintain an active WhatsApp Web session stored in local browser profiles.
4. **Database Mode**: SQLite WAL mode provides sufficient write concurrency for single-user local desktop operation.

---

## 3. Temporary Defaults (Subject to Configuration)

The following system defaults are active prior to user modification:

1. **Initial Dashboard Default Entry Count**: `5` entries.
2. **Initial Dashboard Default Lot per Entry**: `0.10` lots (Total $5 \times 0.10 = 0.50$ lots).
3. **Execution Mode**: `CONFIRMATION` mode enabled by default on initial application boot.
4. **Default Magic Number Offset**: `888000` base magic number for tracking campaign orders.

---

## 4. Unresolved Trading Rules (Pending Clarification)

> [!CAUTION]
> The following trading rules remain unresolved and are tracked in `docs/OPEN_DECISIONS.md`. They are **NOT** user-approved requirements and will not be guessed:

1. Exact price-distance meaning of 100 XAUUSD pips ($1.00$ vs $10.00$ price delta).
2. Behavior when market price is already inside entry zone upon signal arrival.
3. Behavior when market price has already passed full zone upon signal arrival.
4. Order placement timing when TP1/TP2 are sent in follow-up messages.
5. Exact ladder index assignment (lowest vs highest price level) for TP1 and TP2.
6. Execution defaults for ambiguous phrases (`Secure Profits`, `Exit on your comfort`, `Hold it`).
7. Multi-campaign interplay when a new signal arrives during an active trade.
8. Retaining vs closing filled positions upon campaign cancellation or re-entry.
9. Action of `Skip this for now` on active pending orders.
10. Action of `Zone Valid` on paused campaigns.
