# PROMPT 6 OF 12 — ENTRY LADDER, TP ALLOCATION AND RISK ENGINE
# 6 PROMPTS REMAIN AFTER THIS PHASE

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the repository, preserve all valid Phase 1–5 work, implement Prompt 6 completely, run all applicable validations, fix all project-controlled failures, and stop after Prompt 6.

Do not explain the plan before starting.
Do not ask questions unless implementation is blocked by a genuinely unresolved trading rule.
Do not connect to WhatsApp.
Do not connect to MT5.
Do not place, modify, or close trades.
Do not resolve unresolved trading decisions.
Do not add AI or LLM behaviour.
Do not push to GitHub.
Do not create a remote.

A clean local Git commit at the end is allowed only after every required check passes.

---

# CURRENT VERIFIED PROJECT STATE

Phases 1–5 are complete.

Current verified capabilities:

- Requirements and architecture documentation
- pnpm monorepo
- Tauri/React desktop scaffold
- Node.js/TypeScript WhatsApp worker scaffold
- Python FastAPI trading service
- SQLite + SQLAlchemy 2.x
- Alembic revisions through `002_campaign_lifecycle_and_duplicates`
- Pydantic contracts
- TypeScript/Zod contracts
- Deterministic parser version `1.0.0`
- Campaign state machine version `1.0.0`
- Duplicate strategy version `1.0.0`
- Campaign creation and confirmation workflow
- Exact and semantic duplicate protection
- Explicit re-entry
- Campaign matching
- Trading disabled
- MT5 integration absent
- WhatsApp integration absent
- LLM integration absent

Do not rewrite working Phase 1–5 functionality without a documented technical reason.

---

# IMPORTANT PHASE 5 DATA CORRECTION

The Phase 5 report states:

```text
lot_per_entry = 0.10
requested_total_lots = 0.50 for 5 entries
```

This conflicts with the confirmed requirement:

```text
Default lot per entry = 0.30
5 entries × 0.30 = 1.50 total lots
```

Before implementing Prompt 6:

1. Inspect persisted defaults, tests, fixtures, migrations, seed logic, APIs, and documentation.
2. Correct the default development lot-per-entry value to `0.3000`.
3. Correct the default five-entry requested total to `1.5000`.
4. Do not overwrite genuine user-configured values unless they were seeded incorrectly.
5. Add an idempotent migration or settings repair when required.
6. Add regression tests proving the default remains `0.3000`.
7. Add a correction note to the Phase 5 report.
8. Keep the maximum total campaign volume at `2.0000`.

---

# PHASE OBJECTIVE

Implement the deterministic planning and safety engine that converts an approved campaign into a complete set of planned XAUUSD entries.

Implement:

1. Evenly distributed entry ladders
2. Broker-agnostic symbol specification contracts
3. Tick-size price normalization
4. Per-entry lot validation
5. Total exposure validation
6. TP category allocation
7. Fixed 100-pip TP calculation through an explicit policy
8. Signal TP1 and TP2 assignment
9. SL propagation and structural validation
10. Pending-order intent planning
11. Optional current-price simulation
12. Risk validation
13. Planning preview
14. Planned-entry persistence
15. Idempotent planning and safe replanning
16. Planner and risk-engine versioning
17. Tests, benchmarks, APIs, migrations, and documentation

Do not implement:

- MT5 initialization
- MT5 symbol lookup
- MT5 order placement
- Order modification
- Position closing
- WhatsApp connectivity
- OpenWA
- Broker execution
- Spread or slippage checks
- Final dashboard
- AI or LLM decisions

Trading must remain disabled.

---

# SOURCE-OF-TRUTH DOCUMENTS

Read:

```text
README.md
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
docs/TRADING_RULES.md
docs/CAMPAIGN_STATE_MACHINE.md
docs/DATA_MODEL.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/OPEN_DECISIONS.md
docs/CAMPAIGN_IMPLEMENTATION.md
docs/DUPLICATE_PROTECTION.md
docs/CAMPAIGN_MATCHING.md
docs/CONFIRMATION_WORKFLOW.md
docs/PHASE_5_REPORT.md
```

Do not silently resolve any item in `docs/OPEN_DECISIONS.md`.

---

# CONFIRMED PLANNING RULES

## Entry count

```text
Minimum: 3
Maximum: 8
Default: 5
```

## Per-entry lot

```text
Default: 0.3000
Meaning: lot size for each individual entry
```

## Maximum campaign volume

```text
2.0000 lots
```

Formula:

```text
requested_total_lots = entry_count × lot_per_entry
```

Block when:

```text
requested_total_lots > maximum_total_lots
```

Never silently change entry count or lot size.

## Even ladder

```text
step = (zone_high - zone_low) / (entry_count - 1)
```

Include both boundaries.

Example:

```text
Zone: 3990–3998
Entries: 5

3990
3992
3994
3996
3998
```

## TP allocation

```text
Exactly 1 entry → TP_1
Exactly 1 entry → TP_2
All remaining entries → TP_100
```

Examples:

```text
3 entries: 1 TP_100, 1 TP_1, 1 TP_2
5 entries: 3 TP_100, 1 TP_1, 1 TP_2
8 entries: 6 TP_100, 1 TP_1, 1 TP_2
```

`TP Open` remains metadata only. Do not create an open runner.

---

# UNRESOLVED RULES MUST REMAIN EXPLICIT

Do not hide these unresolved decisions:

1. Exact XAUUSD price distance represented by 100 pips.
2. Behaviour when current price is already inside the zone.
3. Behaviour when current price has passed the zone.
4. Which ladder indices receive TP1 and TP2.

Implement explicit policy contracts. Planning must return a structured blocked result when a required policy is missing.

---

# POLICY CONTRACTS

## HundredPipDistancePolicy

Fields:

```text
price_distance
source
is_user_confirmed
```

Production default:

```text
price_distance = null
is_user_confirmed = false
```

Do not assume 100 pips equals `0.10`, `1.00`, or `10.00`.

Tests may inject fixture-only policies, such as:

```text
price_distance = 1.00000000
source = TEST_FIXTURE
is_user_confirmed = false
```

The fixture must never become the production default.

## CurrentPriceZonePolicy

Values:

```text
NO_CURRENT_PRICE_CHECK
BLOCK_IF_INSIDE_ZONE
BLOCK_IF_ZONE_PASSED
SKIP_PASSED_LEVELS
RECALCULATE_REMAINING_LEVELS
CONVERT_PASSED_LEVELS_TO_MARKET
```

Prompt 6 default:

```text
NO_CURRENT_PRICE_CHECK
```

Do not use `CONVERT_PASSED_LEVELS_TO_MARKET`.

## TpIndexAllocationPolicy

Values:

```text
LOWEST_INDICES_TO_SIGNAL_TPS
HIGHEST_INDICES_TO_SIGNAL_TPS
OUTER_BOUNDARIES_TO_SIGNAL_TPS
CENTER_TO_SIGNAL_TPS
EXPLICIT_INDICES
UNRESOLVED
```

Production default:

```text
UNRESOLVED
```

Planning must block until configured.

For `EXPLICIT_INDICES`, require:

```text
tp1_index
tp2_index
```

with distinct valid indices.

## UnspecifiedOrderIntentPolicy

Values:

```text
BLOCK
TREAT_AS_LIMIT
```

Production default:

```text
BLOCK
```

Do not create market orders.

---

# VERSIONING

Use:

```text
planner_version = "1.0.0"
risk_engine_version = "1.0.0"
```

Persist:

```text
planner_version
risk_engine_version
planning_policy_snapshot
symbol_specification_snapshot
planning_fingerprint
```

Create migration revision when needed:

```text
003_entry_planning_and_risk_engine
```

---

# SYMBOL SPECIFICATION CONTRACT

Create a broker-agnostic contract:

```text
symbol
digits
point
tick_size
volume_min
volume_max
volume_step
stops_level_points
freeze_level_points
trade_mode
contract_size
source
captured_at
```

Use decimal strings on the wire.

Example test fixture:

```json
{
  "symbol": "XAUUSD",
  "digits": 2,
  "point": "0.01000000",
  "tick_size": "0.01000000",
  "volume_min": "0.0100",
  "volume_max": "100.0000",
  "volume_step": "0.0100",
  "stops_level_points": 0,
  "freeze_level_points": 0,
  "trade_mode": "FULL",
  "contract_size": "100.0000",
  "source": "TEST_FIXTURE",
  "captured_at": "2026-07-23T10:00:00Z"
}
```

Do not claim these are live Exness values.

---

# MODULE STRUCTURE

Use a clean structure similar to:

```text
apps/trading-service/src/trading_service/
├── planning/
│   ├── __init__.py
│   ├── constants.py
│   ├── errors.py
│   ├── decimal_math.py
│   ├── symbol_spec.py
│   ├── ladder.py
│   ├── price_normalization.py
│   ├── volume_normalization.py
│   ├── tp_allocation.py
│   ├── tp_calculation.py
│   ├── risk_engine.py
│   ├── policies.py
│   ├── planner.py
│   ├── persistence.py
│   ├── result.py
│   └── service.py
└── tests/
    └── planning/
```

Keep ladder, normalization, TP allocation, risk, and persistence separate.

---

# DECIMAL RULES

Use `Decimal` only for financial values.

Never use float for:

- Prices
- Steps
- Tick sizes
- Point sizes
- Volumes
- Lot steps
- SL
- TP
- Total exposure
- Price distance

Use explicit rounding, preferably `ROUND_HALF_UP`, and document it.

---

# LADDER CALCULATION

Input:

```text
zone_low
zone_high
entry_count
```

Validate:

```text
zone_low < zone_high
3 <= entry_count <= 8
```

Calculate:

```text
raw_step = (zone_high - zone_low) / (entry_count - 1)
level[i] = zone_low + raw_step × i
```

Guarantee:

```text
first = zone_low
last = zone_high
exactly entry_count levels
```

Use `zone_high` explicitly for the final level to prevent drift.

Return raw levels and raw step before normalization.

---

# PRICE NORMALIZATION

Normalize each level to `tick_size` using explicit Decimal rounding.

Detect and block:

```text
PRICE_NORMALIZATION_COLLISION
PRICE_OUTSIDE_ZONE
PRICE_ORDER_NON_MONOTONIC
```

Do not:

- Reduce entry count
- Expand the zone
- Invent replacement prices

Return raw and normalized levels with collision details.

---

# VOLUME NORMALIZATION

Validate:

```text
lot_per_entry >= volume_min
lot_per_entry <= volume_max
```

Check alignment with `volume_step`.

If mismatched, return:

```text
VOLUME_STEP_MISMATCH
```

Include:

```text
requested_lot
volume_step
suggested_lot
```

Do not auto-apply the suggestion.

---

# EXPOSURE VALIDATION

Calculate:

```text
requested_total_lots = entry_count × lot_per_entry
```

Validate:

```text
requested_total_lots <= campaign.maximum_total_lots
campaign.maximum_total_lots <= 2.0000
entry_count <= 8
```

Required examples:

```text
5 × 0.30 = 1.50 → allowed
6 × 0.30 = 1.80 → allowed
7 × 0.30 = 2.10 → blocked
8 × 0.25 = 2.00 → allowed
```

Return:

```text
entry_count
lot_per_entry
requested_total_lots
maximum_total_lots
maximum_valid_entry_count
```

Use:

```text
maximum_valid_entry_count = min(8, floor(maximum_total_lots / lot_per_entry))
```

---

# TP CATEGORY ALLOCATION

Input:

```text
entry_count
TpIndexAllocationPolicy
```

Output one category for every entry.

Requirements:

```text
Exactly one TP_1
Exactly one TP_2
Exactly entry_count - 2 TP_100
No duplicate assignments
All entries assigned
Deterministic output
Policy snapshot persisted
```

Default `UNRESOLVED` must block planning.

---

# FIXED 100-PIP TP

Input:

```text
direction
entry_price
HundredPipDistancePolicy.price_distance
```

BUY:

```text
tp_100 = entry_price + price_distance
```

SELL:

```text
tp_100 = entry_price - price_distance
```

Normalize to tick size.

Validate direction.

Missing policy must return:

```text
HUNDRED_PIP_POLICY_MISSING
```

Never hardcode the distance.

---

# SIGNAL TP VALIDATION

For BUY:

```text
tp1 > entry_price
tp2 > entry_price
```

For SELL:

```text
tp1 < entry_price
tp2 < entry_price
```

Invalid values return:

```text
SIGNAL_TP_DIRECTION_INVALID
```

Do not reorder TP1 and TP2.

---

# STOP-LOSS VALIDATION

Propagate one campaign SL to every entry.

For BUY:

```text
stop_loss < entry_price
```

For SELL:

```text
stop_loss > entry_price
```

Invalid values return:

```text
STOP_LOSS_DIRECTION_INVALID
```

Do not alter the SL.

---

# ORDER TYPE PLANNING

Map:

```text
BUY + LIMIT → BUY_LIMIT
SELL + LIMIT → SELL_LIMIT
BUY + UNSPECIFIED → blocked by default
SELL + UNSPECIFIED → blocked by default
```

Do not infer market orders.

With a test-only `TREAT_AS_LIMIT` policy, map unspecified BUY/SELL to corresponding limit types.

---

# OPTIONAL CURRENT PRICE SIMULATION

Preview may accept:

```text
current_bid
current_ask
```

Do not fetch live prices.

Without current prices:

```text
current_price_validation = NOT_PERFORMED
```

Apply only the selected policy.

Never convert entries to market orders.

---

# RISK ENGINE CODES

Implement at least:

```text
ENTRY_COUNT_BELOW_MINIMUM
ENTRY_COUNT_ABOVE_MAXIMUM
LOT_SIZE_NON_POSITIVE
LOT_SIZE_BELOW_SYMBOL_MINIMUM
LOT_SIZE_ABOVE_SYMBOL_MAXIMUM
VOLUME_STEP_MISMATCH
TOTAL_VOLUME_EXCEEDED
ZONE_INVALID
PRICE_NORMALIZATION_COLLISION
PRICE_OUTSIDE_ZONE
PRICE_ORDER_NON_MONOTONIC
STOP_LOSS_MISSING
STOP_LOSS_DIRECTION_INVALID
TP1_MISSING
TP2_MISSING
SIGNAL_TP_DIRECTION_INVALID
HUNDRED_PIP_POLICY_MISSING
TP_INDEX_POLICY_MISSING
ORDER_INTENT_UNRESOLVED
UNSUPPORTED_INSTRUMENT
SYMBOL_SPEC_INVALID
CURRENT_PRICE_POLICY_BLOCK
CAMPAIGN_STATE_NOT_PLANNABLE
TRADING_ENABLED_UNEXPECTEDLY
```

Severity:

```text
INFO
WARNING
ERROR
```

Planning succeeds only with zero errors.

---

# PLANNABLE STATE

Allow planning only from:

```text
PLANNED
```

Do not plan from:

```text
WAITING_FOR_TP
AWAITING_CONFIRMATION
CANCELLED
REJECTED
FAILED
CLOSED
```

Successful planning must not advance to execution states.

Campaign remains:

```text
PLANNED
```

---

# PLANNING RESULT

Return:

```text
contract_version
planner_version
risk_engine_version
campaign_id
campaign_code
status
entry_count
lot_per_entry
requested_total_lots
raw_step
symbol_specification
policy_snapshot
entries
validation_issues
warnings
execution_performed
trading_enabled
```

Statuses:

```text
READY
BLOCKED
ALREADY_PLANNED
INVALIDATED
```

Always return:

```text
execution_performed = false
trading_enabled = false
```

---

# PLANNED ENTRY PERSISTENCE

On success create exactly `entry_count` rows with:

```text
campaign_id
entry_sequence
planned_price
normalized_price
lot_size
stop_loss
take_profit
tp_category
order_side
pending_order_type
status
magic_number
order_comment
planner_version
risk_engine_version
policy_snapshot_json
symbol_spec_snapshot_json
planning_fingerprint
created_at
updated_at
```

Initial status:

```text
PLANNED
```

No MT5 ticket, position ticket, or execution attempt.

Use sequence numbers:

```text
1 through N
```

---

# ORDER COMMENTS

Generate deterministic comments such as:

```text
WA-GOLD-0001-E01-TP100
WA-GOLD-0001-E04-TP1
WA-GOLD-0001-E05-TP2
```

Respect a configurable maximum length.

Do not include secrets.

---

# MAGIC NUMBERS

Generate stable positive integers using a cryptographic hash of:

```text
campaign_id + entry_sequence
```

Map to a safe positive 31-bit range.

Do not use Python `hash()`.

Persist the result.

Re-entry campaigns must produce distinct values.

---

# IDEMPOTENT PLANNING

Create a SHA-256 planning fingerprint from:

```text
campaign_id
campaign_version
planner_version
risk_engine_version
entry_count
lot_per_entry
zone_low
zone_high
stop_loss
tp1
tp2
symbol specification
policy snapshot
```

Behaviour:

```text
Same fingerprint + complete plan → return existing plan
Different fingerprint + existing plan → require explicit replan
Partial plan → fail and require repair
```

Never append duplicate entries.

---

# SAFE REPLANNING

Allow only when:

```text
campaign state = PLANNED
no MT5 orders
no positions
no execution attempts
```

Replan must:

1. Validate expected campaign version.
2. Preserve an audit snapshot.
3. Supersede or transactionally replace old planned entries.
4. Create the new plan.
5. Increment campaign version.
6. Store old and new fingerprints.
7. Create no execution.

Do not destroy audit history.

---

# TRANSACTIONS

Planning must atomically include:

```text
campaign validation
risk validation
planning fingerprint
planned entries
campaign version update
audit event
```

On failure:

- Roll back entries
- Do not change campaign version
- Return structured errors

Use the existing Unit of Work.

---

# DATABASE MIGRATION

Inspect the schema and create:

```text
003_entry_planning_and_risk_engine
```

when required.

Possible additions:

```text
planned_entries.planner_version
planned_entries.risk_engine_version
planned_entries.policy_snapshot_json
planned_entries.symbol_spec_snapshot_json
planned_entries.planning_fingerprint
planned_entries.superseded_at
campaigns.current_planning_fingerprint
campaigns.planned_at
```

Add indexes for:

```text
planned_entries.campaign_id
planned_entries.planning_fingerprint
planned_entries.status
planned_entries.magic_number
campaigns.current_planning_fingerprint
```

Preserve existing data.

---

# SETTINGS

Add:

```text
default_entry_count = 5
default_lot_per_entry = 0.3000
maximum_total_lots = 2.0000
hundred_pip_price_distance = null
hundred_pip_policy_confirmed = false
tp_index_allocation_policy = UNRESOLVED
tp1_explicit_index = null
tp2_explicit_index = null
unspecified_order_intent_policy = BLOCK
current_price_zone_policy = NO_CURRENT_PRICE_CHECK
```

Validate all values.

Trading remains disabled.

---

# DOMAIN CONTRACTS

Update Python and TypeScript/Zod contracts for:

```text
SymbolSpecification
HundredPipDistancePolicy
CurrentPriceZonePolicy
TpIndexAllocationPolicy
UnspecifiedOrderIntentPolicy
PlanningPolicySnapshot
LadderCalculationRequest
LadderCalculationResult
PriceNormalizationResult
VolumeValidationResult
TpAllocationResult
RiskValidationIssue
CampaignPlanningRequest
CampaignPlanningPreview
CampaignPlan
PlannedEntryDetail
ReplanRequest
ReplanResult
PlanningFingerprint
```

Use decimal strings on the wire.

---

# API

Add:

```text
GET /api/v1/planning/version
GET /api/v1/planning/policies
POST /api/v1/planning/preview
POST /api/v1/campaigns/{campaign_id}/plan
POST /api/v1/campaigns/{campaign_id}/replan
GET /api/v1/campaigns/{campaign_id}/plan
GET /api/v1/campaigns/{campaign_id}/planned-entries
```

Requirements:

- Preview does not persist.
- Plan persists only for `PLANNED` campaigns.
- Same fingerprint is idempotent.
- Different fingerprint requires replan.
- Replan uses optimistic concurrency.
- No order execution.
- No MT5 claims.
- No secrets.

HTTP behaviour:

```text
First plan: 201
Idempotent existing plan: 200
Conflicting existing plan: 409
Stale version: 409
Validation errors: 422
Not found: 404
```

---

# FIXTURES

Create:

```text
packages/parser-fixtures/fixtures/planning/
├── valid/
├── blocked/
├── normalization/
├── tp-allocation/
├── exposure/
├── policies/
├── replan/
└── symbol-specs/
```

Required cases:

1. Five entries across 3990–3998
2. Three entries
3. Eight entries
4. Seven entries × 0.30 blocked
5. Eight entries × 0.25 allowed
6. Tick normalization success
7. Tick collision
8. Invalid lot step
9. Missing 100-pip policy
10. Missing TP index policy
11. Explicit TP indices
12. BUY TP calculation
13. SELL TP calculation
14. BUY SL invalid
15. SELL SL invalid
16. Unspecified order intent blocked
17. Same-fingerprint idempotency
18. Changed-fingerprint replan
19. Wrong campaign state
20. Default lot regression `0.3000`

---

# REQUIRED TESTS

Use temporary SQLite databases.

## Default regression

Verify:

```text
default lot = 0.3000
default entries = 5
default requested total = 1.5000
```

## Ladder

Test entry counts 3–8, exact boundaries, high precision, and no drift.

## Price normalization

Test tick sizes:

```text
0.01
0.10
0.25
```

Test collisions, bounds, and monotonic order.

## Volume

Test:

```text
0.30 with 0.01 step
0.30 with 0.10 step
0.30 with 0.25 step mismatch
below minimum
above maximum
non-positive lot
```

## Exposure

Test:

```text
5 × 0.30 = 1.50 allowed
6 × 0.30 = 1.80 allowed
7 × 0.30 = 2.10 blocked
8 × 0.25 = 2.00 allowed
```

## TP allocation

For counts 3–8 verify exactly one TP1, one TP2, and all remaining TP100.

Test explicit indices, invalid duplicate indices, and unresolved policy blocking.

## TP calculation

Use fixture-only distance policies.

Test BUY, SELL, tick normalization, missing policy, invalid distance, direction validation, and `TP Open`.

## SL

Test BUY and SELL structural validation.

## Order intent

Test BUY_LIMIT, SELL_LIMIT, default blocking, fixture-only `TREAT_AS_LIMIT`, and absence of market orders.

## Planner

Test:

- Exact entry count
- Lot propagation
- SL propagation
- TP assignment
- Exact total lots
- Stable fingerprint
- Idempotency
- Replan requirement
- Partial plan rejection
- No MT5 records
- No positions
- No execution attempts

## Replan

Test allowed, blocked by MT5 order, blocked by position, blocked by execution attempt, stale version, audit preservation, and new fingerprint.

## API

Test all endpoints, codes, contracts, Decimal strings, idempotency, conflicts, and no execution.

## Migration

Test 002→003, 003→002, re-upgrade, and full base-to-head.

## Cross-language

Validate all planning fixtures through Pydantic and Zod.

---

# BENCHMARKS

Add:

```text
100,000 ladder calculations
10,000 full risk validations
1,000 plan persistence and retrieval operations
```

Report median, p95, and total duration.

No network calls.

---

# LOGGING AND AUDIT

Structured fields:

```text
service
event
campaign_id
campaign_code
planner_version
risk_engine_version
planning_fingerprint
entry_count
lot_per_entry
requested_total_lots
validation_issue_count
duration_ms
correlation_id
```

Audit events:

```text
PLAN_PREVIEWED
PLAN_CREATED
PLAN_RETURNED_IDEMPOTENTLY
PLAN_BLOCKED
PLAN_REPLACED
PLAN_REPLAN_BLOCKED
RISK_VALIDATION_FAILED
DEFAULT_LOT_SETTING_REPAIRED
```

Do not log secrets.

---

# DOCUMENTATION

Create or update:

```text
docs/ENTRY_PLANNER.md
docs/ENTRY_LADDER.md
docs/TP_ALLOCATION.md
docs/RISK_ENGINE.md
docs/PLANNING_POLICIES.md
docs/SYMBOL_SPECIFICATION.md
docs/PLANNING_API.md
docs/PHASE_6_REPORT.md
docs/TRADING_RULES.md
docs/DATA_MODEL.md
docs/ACCEPTANCE_CRITERIA.md
docs/OPEN_DECISIONS.md
docs/REPOSITORY_STRUCTURE.md
docs/PHASE_5_REPORT.md
README.md
```

Update README:

```text
Prompt 6 of 12 completed
Next: Prompt 7 — MT5 Adapter and Demo Execution Worker
```

---

# ROOT SCRIPTS

Add or update:

```text
planning:test
planning:contracts
planning:benchmark
planning:migrations
```

Preserve existing commands.

---

# REQUIRED VALIDATION

Run:

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/validate.ps1
pnpm install
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
ruff check .
ruff format --check .
mypy apps/trading-service/src
pytest
pnpm planning:test
pnpm planning:contracts
pnpm planning:benchmark
pnpm planning:migrations
```

Use equivalent repository commands where necessary.

Run Alembic:

```powershell
alembic upgrade head
alembic current
alembic downgrade -1
alembic upgrade head
```

Test full base-to-head migration.

Start FastAPI and verify all planning endpoints, then stop cleanly.

Verify:

- Planned entries only
- No pending orders
- No MT5 orders
- No positions
- No execution attempts
- Campaign remains `PLANNED`
- Trading remains disabled

Search active source code for:

```text
order_send
mt5.initialize
MetaTrader5
wa.create
open-wa
createOrder
place_trade
execute_trade
close_position
modify_position
live account password
OpenAI
Anthropic
Gemini
langchain
```

Documentation matches are allowed.

Run:

```powershell
git status --short
```

If all checks pass, a local commit is allowed:

```powershell
git add .
git commit -m "feat: complete Prompt 6 - Entry Ladder TP Allocation and Risk Engine"
```

Do not push.

---

# FAILURE HANDLING

Do not mark Prompt 6 complete because files were generated.

When a check fails:

1. Read the full error.
2. Fix the root cause.
3. Rerun the targeted check.
4. Do not weaken Decimal precision.
5. Do not silently normalize lot size.
6. Do not silently reduce entries.
7. Do not silently select TP indices.
8. Do not hardcode 100-pip distance.
9. Do not infer market orders.
10. Do not bypass exposure limits.
11. Do not create MT5 records.
12. Do not create execution attempts.
13. Do not falsely report success.
14. Report genuine external blockers.

---

# COMPLETION REQUIREMENTS

Prompt 6 is complete only when:

- Default lot is `0.3000`.
- Five-entry default exposure is `1.5000`.
- Ladders work for 3–8 entries.
- Boundaries are preserved.
- Tick normalization works.
- Collisions block planning.
- Lot-step mismatch blocks planning.
- Exposure validation works.
- Seven entries at 0.30 are blocked.
- Eight entries at 0.25 are allowed.
- TP allocation is exact.
- TP index policy remains explicit.
- 100-pip distance remains explicit.
- Missing policy blocks planning.
- Fixture-only fixed TP calculations work.
- SL and TP direction validation work.
- Unspecified intent blocks by default.
- Planned entries persist.
- Planning is idempotent.
- Replanning is safe and audited.
- APIs and contracts work.
- All project checks pass.
- Trading remains disabled.
- MT5, WhatsApp, and LLM integrations remain absent.
- No live credentials exist.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 6 OF 12 COMPLETED

Project root:
- ...

Versions:
- Planner version:
- Risk engine version:
- State machine version:
- Parser version:
- Contract version:

Phase 5 correction:
- Previous incorrect default lot:
- Corrected default lot:
- Default entry count:
- Correct default requested total:
- Migration or seed repair:
- Regression test:

Ladder:
- Formula:
- Supported entry counts:
- Boundary preservation:
- Tick normalization:
- Collision handling:
- Sequence numbering:

Volume and exposure:
- Per-entry lot:
- Volume step validation:
- Maximum total lots:
- 5 × 0.30:
- 6 × 0.30:
- 7 × 0.30:
- 8 × 0.25:
- Automatic lot reduction:

TP allocation:
- TP1 count:
- TP2 count:
- TP100 count:
- TP index policy:
- TP Open handling:
- 100-pip policy:
- Production default distance:

Risk engine:
- Supported validation codes:
- SL direction validation:
- TP direction validation:
- Order intent validation:
- Current price validation:

Planning:
- Campaign state required:
- Idempotent planning:
- Planning fingerprint:
- Replanning:
- Planned entries persisted:
- Pending orders created:
- MT5 orders created:
- Positions created:
- Execution attempts created:
- Execution performed:

API:
- Planning version:
- Planning policies:
- Preview:
- Plan campaign:
- Replan campaign:
- Get campaign plan:
- Get planned entries:

Validation:
- Existing validation script:
- pnpm format:
- pnpm lint:
- pnpm typecheck:
- pnpm test:
- pnpm build:
- Ruff:
- Python typecheck:
- Pytest:
- Alembic upgrade:
- Alembic downgrade:
- Alembic re-upgrade:
- Planning contract tests:
- Ladder benchmark:
- Risk benchmark:
- Persistence benchmark:
- FastAPI planning endpoints:
- Database safety verification:
- Security source scan:

Safety verification:
- Trading enabled: false
- MT5 integration: absent
- WhatsApp integration: absent
- LLM integration: absent
- Live credentials: absent
- 100-pip distance hardcoded: false
- TP indices silently selected: false
- Lot size silently reduced: false

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 7 OF 12 — MT5 ADAPTER AND DEMO EXECUTION WORKER
```

Stop after Prompt 6.
