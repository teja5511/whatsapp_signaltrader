# PROMPT 7 OF 12 — MT5 ADAPTER AND DEMO EXECUTION WORKER
# 5 PROMPTS REMAIN AFTER THIS PHASE

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the repository, preserve all valid Phase 1–6 work, implement Prompt 7 completely, run every applicable validation, fix every project-controlled failure, and stop after Prompt 7.

Do not explain the plan before starting.  
Do not connect WhatsApp.  
Do not install or implement OpenWA.  
Do not enable live-account execution.  
Do not store MT5 passwords.  
Do not add AI or LLM behaviour.  
Do not push to GitHub.  
Do not create a remote.

A clean local Git commit at the end is allowed only after all checks pass.

---

# CURRENT VERIFIED STATE

Phases 1–6 are complete.

Current verified capabilities:

- pnpm monorepo
- Tauri/React desktop scaffold
- Node.js/TypeScript WhatsApp worker scaffold
- Python FastAPI trading service
- SQLite + SQLAlchemy 2.x
- Alembic through `003_entry_planning_and_risk_engine`
- Parser `1.0.0`
- Campaign state machine `1.0.0`
- Duplicate strategy `1.0.0`
- Planner `1.0.0`
- Risk engine `1.0.0`
- Planned-entry persistence
- Default entry count `5`
- Default lot per entry `0.3000`
- Default five-entry exposure `1.5000`
- Maximum campaign volume `2.0000`
- MT5 integration absent
- WhatsApp integration absent
- Live execution absent

Do not rewrite working Phase 1–6 functionality without a documented technical reason.

---

# PHASE OBJECTIVE

Implement a safe, testable, demo-only MetaTrader 5 adapter and single-writer execution worker for Windows.

Implement:

1. MT5 adapter interface
2. Fake adapter
3. Dry-run adapter
4. Real MetaTrader5 Python adapter
5. MT5 initialization and shutdown
6. Demo/live account detection
7. Hedging-mode verification
8. Optional account/server allowlists
9. XAUUSD symbol discovery and broker-symbol resolution
10. Symbol specification retrieval
11. Trade-permission checks
12. Pending-order request building
13. `order_check` before every real send
14. Demo pending-order placement
15. Pending-order modification and deletion
16. Position SL/TP modification
17. Position closing
18. Campaign pending-order cancellation
19. Campaign position closing
20. Demo-only emergency close-all
21. Durable execution jobs
22. Single-writer execution queue
23. Idempotent order submission
24. MT5 request/response persistence
25. Campaign execution-state transitions
26. Basic order/position synchronization
27. Local authenticated MT5 APIs
28. Fake-adapter and dry-run tests
29. Optional manually gated real-demo smoke tests
30. Documentation, migrations, benchmarks, and CI updates

Do not implement:

- WhatsApp connectivity
- OpenWA
- Automatic execution from WhatsApp
- Final dashboard
- Multiple MT5 accounts
- Multiple instruments
- Live trading
- AI or LLM decisions

---

# SOURCE DOCUMENTS

Read before implementation:

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
docs/ENTRY_PLANNER.md
docs/RISK_ENGINE.md
docs/PLANNING_POLICIES.md
docs/SYMBOL_SPECIFICATION.md
docs/PHASE_6_REPORT.md
```

Only fully planned campaigns with resolved policies may reach execution.

---

# NON-NEGOTIABLE SAFETY DEFAULTS

```text
MT5_ADAPTER_MODE=fake
MT5_EXECUTION_ENABLED=false
MT5_DEMO_ONLY=true
MT5_LIVE_EXECUTION_ENABLED=false
MT5_AUTOMATIC_EXECUTION_ENABLED=false
MT5_REQUIRE_MANUAL_CONFIRMATION=true
MT5_CLOSE_ALL_ENABLED=false
```

Real order submission is allowed only when every gate passes:

```text
adapter mode = real
execution enabled = true
demo only = true
connected account = demo
margin mode = hedging
login allowlist passes when configured
server allowlist passes when configured
terminal trading allowed
account trading allowed
resolved symbol is XAUUSD-compatible and tradable
campaign state = PLANNED
planned entries complete
planning fingerprint matches
campaign version matches
entry count <= 8
total lots <= 2.0000
explicit execution request received
single-writer worker accepts the job
```

Any failed gate blocks execution.

Live, contest, unknown, netting, exchange, or non-hedging accounts must be blocked.

Do not provide a live-trading override in Prompt 7.

---

# MT5 CONNECTION MODEL

Preferred model:

```text
The user manually opens MetaTrader 5 and logs into the intended Exness demo account.
The application initializes against that existing terminal session.
```

Do not store MT5 passwords.

Do not call `mt5.login()` using stored credentials.

Support optional:

```text
MT5_TERMINAL_PATH=
MT5_INITIALIZE_TIMEOUT_MS=10000
MT5_ALLOWED_LOGINS=
MT5_ALLOWED_SERVERS=
MT5_SYMBOL_OVERRIDE=
```

Mask account numbers in normal logs.

---

# PACKAGE COMPATIBILITY

Before installing `MetaTrader5`:

1. Inspect Python version and architecture.
2. Verify a compatible wheel exists.
3. Prefer compatible 64-bit Python.
4. Pin the package version.
5. Do not alter global Python unnecessarily.
6. If incompatible, create a project-local compatible environment.
7. Record exact versions and limitations.
8. Do not claim real-adapter validation when MT5 is unavailable.

Fake and dry-run adapters must work without MetaTrader 5 installed.

---

# MODULE STRUCTURE

Use a clean structure similar to:

```text
apps/trading-service/src/trading_service/
├── mt5/
│   ├── __init__.py
│   ├── constants.py
│   ├── errors.py
│   ├── contracts.py
│   ├── adapter.py
│   ├── fake_adapter.py
│   ├── dry_run_adapter.py
│   ├── real_adapter.py
│   ├── terminal.py
│   ├── account.py
│   ├── symbols.py
│   ├── request_builder.py
│   ├── filling_policy.py
│   ├── execution_queue.py
│   ├── execution_worker.py
│   ├── execution_service.py
│   ├── order_service.py
│   ├── position_service.py
│   ├── synchronization.py
│   ├── idempotency.py
│   ├── result.py
│   └── health.py
└── tests/
    └── mt5/
```

All direct `MetaTrader5` package calls must remain inside the real adapter boundary.

---

# ADAPTER MODES

Support:

```text
fake
dry_run
real
```

## Fake

- Deterministic in-memory simulation
- Configurable account, symbol, order, position, fill, and failure states
- No external package required

## Dry run

- Builds real normalized requests
- Runs local preflight and validation
- Never calls `order_send`
- Never creates realistic fake broker tickets
- Returns:

```text
dry_run = true
execution_performed = false
```

## Real

- Uses official MetaTrader5 Python package
- Windows-only
- Demo-only
- Explicit local opt-in
- Excluded from normal CI
- Live accounts always blocked

---

# ADAPTER INTERFACE

Define normalized methods similar to:

```text
initialize()
shutdown()
is_initialized()
terminal_info()
account_info()
list_symbols()
select_symbol()
symbol_info()
symbol_tick()
order_check()
order_send()
orders_get()
positions_get()
history_orders_get()
history_deals_get()
last_error()
```

Higher-level methods:

```text
place_pending_order()
modify_pending_order()
delete_pending_order()
modify_position_sltp()
close_position()
cancel_campaign_orders()
close_campaign_positions()
close_all_xauusd()
```

Do not expose raw MT5 namedtuples outside the adapter.

---

# INITIALIZATION AND HEALTH

Initialization sequence:

1. Acquire initialization lock.
2. Initialize MT5 once.
3. Read terminal info.
4. Read account info.
5. Detect demo/live/contest/unknown.
6. Verify hedging mode.
7. Verify terminal trade permission.
8. Verify account trade permission.
9. Verify optional allowlists.
10. Resolve XAUUSD broker symbol.
11. Read symbol specification.
12. Select symbol if required.
13. Mark adapter ready only after every check passes.

Normalized health states:

```text
DISABLED
NOT_INSTALLED
NOT_INITIALIZED
INITIALIZING
CONNECTED
READY
DEGRADED
BLOCKED_LIVE_ACCOUNT
BLOCKED_NON_HEDGING
BLOCKED_ACCOUNT_NOT_ALLOWED
BLOCKED_SERVER_NOT_ALLOWED
BLOCKED_SYMBOL_NOT_FOUND
BLOCKED_SYMBOL_AMBIGUOUS
TRADING_NOT_ALLOWED
ERROR
SHUTTING_DOWN
```

Shutdown must stop the worker, reject new jobs, safely finish or stop current work, call MT5 shutdown once, and persist an audit event.

---

# ACCOUNT DETECTION

Normalize environment:

```text
DEMO
CONTEST
REAL
UNKNOWN
```

Only `DEMO` may execute.

Normalize margin mode:

```text
HEDGING
NETTING
EXCHANGE
UNKNOWN
```

Only `HEDGING` may execute.

Return account metadata safely:

```text
login_masked
server
company
environment_kind
margin_mode
currency
leverage
trade_allowed
trade_expert
balance
equity
margin
margin_free
```

Do not log or persist passwords.

---

# XAUUSD SYMBOL RESOLUTION

Resolve one broker symbol for canonical:

```text
XAUUSD
```

Possible candidates may include:

```text
XAUUSD
XAUUSDm
XAUUSD.a
XAUUSDc
GOLD
```

Resolution order:

1. Exact configured override, if present
2. Exact `XAUUSD`
3. Strict accepted suffix variants beginning with `XAUUSD`
4. `GOLD` only when symbol metadata confirms gold

Block when:

```text
zero matches → XAUUSD_SYMBOL_NOT_FOUND
multiple equal matches → XAUUSD_SYMBOL_AMBIGUOUS
```

Never auto-select an unrelated symbol.

Persist:

```text
canonical_symbol = XAUUSD
broker_symbol = resolved broker name
```

---

# SYMBOL SPECIFICATION

Map MT5 symbol info into the Phase 6 contract:

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
filling_mode
order_mode
expiration_mode
visible
spread
spread_float
source
captured_at
```

Use Decimal-safe conversion.

Before execution compare current specification against the planning snapshot.

Material changes that block execution:

```text
tick_size
volume_min
volume_max
volume_step
trade_mode
```

Return:

```text
SYMBOL_SPECIFICATION_CHANGED
```

Require replan.

---

# FILLING AND TIME POLICIES

Normalize filling modes:

```text
FOK
IOC
RETURN
UNKNOWN
```

Choose only a mode supported by the symbol and operation.

Block unknown or unsupported modes.

Default pending-order time policy:

```text
GTC
```

Support normalized values:

```text
GTC
DAY
SPECIFIED
SPECIFIED_DAY
```

Use only supported modes.

---

# PENDING ORDER REQUESTS

Map planned entries:

```text
BUY_LIMIT → MT5 buy-limit pending order
SELL_LIMIT → MT5 sell-limit pending order
```

Every request must include normalized:

```text
action
symbol
volume
order_type
price
stop_loss
take_profit
magic_number
comment
time_type
expiration when required
filling_type
```

Do not recalculate or silently alter:

- Entry price
- Volume
- SL
- TP
- Magic number
- Comment
- TP category

If the broker specification requires a change, block and require replan.

---

# ORDER CHECK AND SEND

Every real request must run:

```text
order_check
```

before:

```text
order_send
```

Persist normalized check request and result.

Never call `order_send` after a failed check.

Immediately before send, re-check:

- Demo account
- Hedging mode
- Trading permissions
- Campaign state/version
- Planning fingerprint
- Entry ownership
- Existing order/position linkage
- Symbol specification
- Execution enablement

Call `order_send` only once per idempotency key.

Persist:

```text
request
check response
send response
raw retcode
normalized result
ticket when returned
last error
timestamps
```

Never blindly retry an ambiguous send.

Use:

```text
EXECUTION_OUTCOME_UNKNOWN
```

and require synchronization before retry.

---

# EXECUTION IDEMPOTENCY

Create SHA-256 idempotency keys from canonical fields:

```text
campaign_id
planning_fingerprint
planned_entry_id
campaign_version
account login hash
account server
broker symbol
operation type
```

Rules:

- One active place-order operation per planned entry
- Repeated API request returns existing batch/job
- Restart cannot permit duplicate sends
- Ambiguous outcome blocks resend
- Database-backed protection required

---

# DURABLE SINGLE-WRITER QUEUE

Create migration:

```text
004_mt5_demo_execution_worker
```

Add a durable job table such as:

```text
mt5_execution_jobs
```

Fields:

```text
id
batch_id
campaign_id
planned_entry_id
operation_type
idempotency_key
status
priority
attempt_count
max_attempts
payload_json
result_json
last_error_code
last_error_message
available_at
locked_at
locked_by
started_at
completed_at
created_at
updated_at
```

Statuses:

```text
QUEUED
RUNNING
SUCCEEDED
FAILED
BLOCKED
OUTCOME_UNKNOWN
CANCELLED
```

Constraint:

```text
idempotency_key unique
```

Add account, symbol, and synchronization snapshot tables when required.

Only one worker may perform trade operations.

The API queues jobs and never sends trades in the HTTP request thread.

Place-order automatic retry count:

```text
0 after an ambiguous or sent request
```

Read-only status calls may retry safely.

---

# CAMPAIGN EXECUTION

Execute only campaigns in:

```text
PLANNED
```

Preconditions:

```text
planned entries complete
entry count matches campaign
all planned entries status = PLANNED
planning fingerprint matches
campaign version matches
no unresolved policy
no active execution batch
no linked order or position
entry count <= 8
total lots <= 2.0000
canonical instrument = XAUUSD
real adapter READY
demo account
hedging account
```

Queue one batch and one child job per planned entry.

Process entries in ascending `entry_sequence`.

---

# STATE TRANSITIONS

Extend the state machine:

```text
PLANNED → PLACING_ORDERS
PLACING_ORDERS → PENDING
PLACING_ORDERS → PARTIALLY_PLACED
PLACING_ORDERS → PARTIALLY_FILLED
PLACING_ORDERS → OPEN
PLACING_ORDERS → FAILED

PARTIALLY_PLACED → PENDING
PARTIALLY_PLACED → PARTIALLY_FILLED
PARTIALLY_PLACED → OPEN
PARTIALLY_PLACED → CANCELLED
PARTIALLY_PLACED → FAILED

PENDING → PARTIALLY_FILLED
PENDING → OPEN
PENDING → CANCELLED
PENDING → FAILED

PARTIALLY_FILLED → OPEN
PARTIALLY_FILLED → MANAGING
PARTIALLY_FILLED → CLOSING
PARTIALLY_FILLED → CLOSED
PARTIALLY_FILLED → FAILED

OPEN → MANAGING
OPEN → CLOSING
OPEN → CLOSED
OPEN → FAILED

MANAGING → CLOSING
MANAGING → CLOSED
MANAGING → FAILED

CLOSING → CLOSED
CLOSING → FAILED
```

State meaning:

```text
PENDING = all intended unfilled orders accepted
PARTIALLY_PLACED = some accepted, some failed or blocked
PARTIALLY_FILLED = positions exist and pending orders remain
OPEN = positions exist and no intended pending orders remain
```

Use snapshots, not assumptions.

---

# PARTIAL PLACEMENT

Create:

```text
PartialPlacementPolicy
```

Values:

```text
KEEP_ACCEPTED_AND_REPORT
ROLLBACK_UNFILLED_ACCEPTED
BLOCK_REMAINING_AFTER_FIRST_FAILURE
```

Production default:

```text
BLOCK_REMAINING_AFTER_FIRST_FAILURE
```

On first definite failure:

- Stop sending remaining entries
- Preserve accepted orders
- Mark `PARTIALLY_PLACED`
- Require explicit user action for cancellation
- Never blindly rollback after a fill

---

# BASIC SYNCHRONIZATION

After every successful send:

1. Query active orders.
2. Query positions.
3. Match by ticket, magic number, comment, symbol, volume, and price.
4. Persist normalized order/position records.
5. Update planned-entry status.
6. Update campaign state.

Add:

```text
synchronize_campaign(campaign_id)
```

Full startup reconciliation remains for Prompt 11.

---

# ORDER AND POSITION OPERATIONS

Implement demo-only queued operations:

```text
modify_pending_order
delete_pending_order
cancel_campaign_pending_orders
modify_position_sltp
close_position
close_campaign_positions
```

Rules:

- Explicit request
- Local API token required
- Demo and hedging verified again
- Ownership verified by campaign, ticket, magic, comment, and symbol
- No unrelated order or position may be modified
- Persist request and response
- Update local state only after MT5 confirmation
- No blind retry after ambiguous outcome

For position close, use an opposite market deal linked to the position ticket.

Use configurable close deviation:

```text
MT5_CLOSE_DEVIATION_POINTS=20
```

This is not a spread filter.

---

# EMERGENCY CLOSE ALL XAUUSD

Implement demo-only emergency operation.

Default:

```text
MT5_CLOSE_ALL_ENABLED=false
```

Require confirmation phrase:

```text
CLOSE ALL DEMO XAUUSD
```

Scopes:

```text
APPLICATION_OWNED
ALL_XAUUSD_ON_ACCOUNT
```

Default scope:

```text
APPLICATION_OWNED
```

`ALL_XAUUSD_ON_ACCOUNT` requires a stronger second confirmation.

Never touch non-XAUUSD instruments.

Never operate on live accounts.

Return per-ticket results and audit everything.

---

# ERROR CODES

Implement structured errors including:

```text
MT5_PACKAGE_UNAVAILABLE
MT5_INITIALIZE_FAILED
MT5_TERMINAL_UNAVAILABLE
MT5_ACCOUNT_INFO_UNAVAILABLE
MT5_LIVE_ACCOUNT_BLOCKED
MT5_CONTEST_ACCOUNT_BLOCKED
MT5_ACCOUNT_NOT_HEDGING
MT5_ACCOUNT_NOT_ALLOWED
MT5_SERVER_NOT_ALLOWED
MT5_TERMINAL_TRADE_DISABLED
MT5_ACCOUNT_TRADE_DISABLED
XAUUSD_SYMBOL_NOT_FOUND
XAUUSD_SYMBOL_AMBIGUOUS
XAUUSD_SYMBOL_NOT_TRADABLE
SYMBOL_SPECIFICATION_CHANGED
FILLING_MODE_UNSUPPORTED
ORDER_TIME_MODE_UNSUPPORTED
CAMPAIGN_NOT_PLANNED
PLAN_INCOMPLETE
PLANNING_FINGERPRINT_MISMATCH
CAMPAIGN_VERSION_CONFLICT
EXECUTION_DISABLED
EXECUTION_JOB_DUPLICATE
EXECUTION_ALREADY_ACTIVE
EXECUTION_OUTCOME_UNKNOWN
ORDER_CHECK_FAILED
ORDER_SEND_FAILED
ORDER_REJECTED
ORDER_NOT_FOUND
ORDER_OWNERSHIP_MISMATCH
POSITION_NOT_FOUND
POSITION_OWNERSHIP_MISMATCH
PARTIAL_PLACEMENT
CLOSE_CONFIRMATION_INVALID
EMERGENCY_CLOSE_DISABLED
WORKER_NOT_RUNNING
WORKER_SHUTTING_DOWN
```

Preserve raw MT5 retcodes as metadata.

---

# CONFIGURATION

Update `.env.example`:

```text
MT5_ADAPTER_MODE=fake
MT5_EXECUTION_ENABLED=false
MT5_DEMO_ONLY=true
MT5_LIVE_EXECUTION_ENABLED=false
MT5_AUTOMATIC_EXECUTION_ENABLED=false
MT5_REQUIRE_MANUAL_CONFIRMATION=true
MT5_TERMINAL_PATH=
MT5_INITIALIZE_TIMEOUT_MS=10000
MT5_ALLOWED_LOGINS=
MT5_ALLOWED_SERVERS=
MT5_SYMBOL_OVERRIDE=
MT5_CLOSE_DEVIATION_POINTS=20
MT5_CLOSE_ALL_ENABLED=false
MT5_WORKER_POLL_INTERVAL_MS=250
MT5_WORKER_ID=
MT5_PARTIAL_PLACEMENT_POLICY=BLOCK_REMAINING_AFTER_FIRST_FAILURE
```

Settings API must reject:

```text
MT5_LIVE_EXECUTION_ENABLED=true
MT5_DEMO_ONLY=false
```

Never commit a real `.env` or credentials.

---

# LOCAL API AUTHENTICATION

All mutating MT5 endpoints require:

```text
Authorization: Bearer <LOCAL_API_TOKEN>
```

Requirements:

- Token from ignored local environment
- Constant-time comparison
- Missing or wrong token blocks mutation
- Never log token
- Bind service to localhost by default
- Tests for missing, wrong, and correct token

---

# DOMAIN CONTRACTS

Update Python and TypeScript/Zod contracts for:

```text
Mt5AdapterMode
Mt5HealthState
Mt5AccountEnvironment
Mt5MarginMode
Mt5TerminalStatus
Mt5AccountStatus
Mt5SymbolResolution
Mt5SymbolSpecification
Mt5FillingMode
Mt5TimePolicy
Mt5ExecutionOperation
Mt5ExecutionJob
Mt5ExecutionJobStatus
Mt5ExecutionBatch
Mt5OrderCheckRequest
Mt5OrderCheckResult
Mt5OrderSendRequest
Mt5OrderSendResult
Mt5OrderSnapshot
Mt5PositionSnapshot
Mt5SynchronizationResult
Mt5ExecutionPreflight
Mt5ExecutionPreflightResult
Mt5CampaignExecutionRequest
Mt5CampaignExecutionResult
Mt5OrderModificationRequest
Mt5OrderDeletionRequest
Mt5PositionModificationRequest
Mt5PositionCloseRequest
Mt5CampaignCancelRequest
Mt5CampaignCloseRequest
Mt5EmergencyCloseRequest
Mt5EmergencyCloseResult
PartialPlacementPolicy
ExecutionIdempotencyKey
```

Use Decimal strings for financial values.

Versions:

```text
mt5_adapter_version = 1.0.0
execution_worker_version = 1.0.0
```

---

# API ENDPOINTS

Add:

```text
GET  /api/v1/mt5/version
GET  /api/v1/mt5/status
GET  /api/v1/mt5/terminal
GET  /api/v1/mt5/account
GET  /api/v1/mt5/symbol
GET  /api/v1/mt5/symbol/specification
POST /api/v1/mt5/initialize
POST /api/v1/mt5/shutdown
POST /api/v1/mt5/synchronize
POST /api/v1/mt5/execution/preflight/{campaign_id}
POST /api/v1/mt5/execution/campaigns/{campaign_id}
GET  /api/v1/mt5/execution/jobs
GET  /api/v1/mt5/execution/jobs/{job_id}
GET  /api/v1/mt5/execution/batches/{batch_id}
POST /api/v1/mt5/execution/jobs/{job_id}/cancel
POST /api/v1/mt5/orders/{order_ticket}/modify
DELETE /api/v1/mt5/orders/{order_ticket}
POST /api/v1/mt5/campaigns/{campaign_id}/cancel-pending
POST /api/v1/mt5/positions/{position_ticket}/modify-sltp
POST /api/v1/mt5/positions/{position_ticket}/close
POST /api/v1/mt5/campaigns/{campaign_id}/close
POST /api/v1/mt5/emergency/close-all-xauusd
```

Campaign execution endpoint must:

- Require expected campaign version
- Require planning fingerprint
- Require explicit confirmation
- Queue work
- Return `202 Accepted`
- Never send in the HTTP request thread

Suggested status codes:

```text
200 read/idempotent result
202 job queued
401 invalid local token
403 safety gate blocked
404 not found
409 state/version/idempotency conflict
422 validation error
503 MT5 or worker unavailable
```

Every response must clearly show:

```text
adapter_mode
demo_only
account_environment
execution_performed
job_id
batch_id
safety_checks
```

---

# FAKE ADAPTER SCENARIOS

Implement deterministic scenarios:

```text
healthy_demo_hedging
live_account
netting_account
trade_disabled
symbol_missing
symbol_ambiguous
symbol_spec_changed
order_check_failure
first_send_failure
middle_send_failure
all_orders_accepted
immediate_first_fill
partial_fill_with_pending
outcome_unknown
order_modify_success
order_delete_success
position_modify_success
position_close_success
emergency_close_partial_failure
disconnected_during_batch
```

---

# REAL DEMO SMOKE TESTS

Real-demo smoke tests must be excluded from normal pytest and CI.

Require:

```text
RUN_MT5_DEMO_SMOKE_TESTS=true
MT5_ADAPTER_MODE=real
MT5_EXECUTION_ENABLED=true
MT5_DEMO_ONLY=true
```

Before any smoke order:

1. Confirm demo account.
2. Confirm hedging mode.
3. Confirm allowlists.
4. Confirm symbol.
5. Use a safe test lot not exceeding project limits.
6. Use a pending price safely away from market.
7. Require explicit user confirmation.
8. Place one test pending order.
9. Verify it exists.
10. Delete it.
11. Verify no position remains.
12. Stop immediately if cleanup fails.

If not explicitly run, report:

```text
NOT RUN — manual demo opt-in required
```

Do not report unrun tests as passed.

---

# REQUIRED TESTS

Use fake adapter and temporary databases.

## Safety

Test:

- Live account blocked
- Contest blocked
- Unknown account blocked
- Netting blocked
- Trading disabled blocked
- Wrong login blocked
- Wrong server blocked
- Symbol missing blocked
- Symbol ambiguity blocked
- Changed specification blocked
- Missing token blocked
- Wrong token blocked

## Execution

Test:

- Planned campaign creates one batch
- One child job per entry
- Entry-sequence processing
- Same request is idempotent
- Stale campaign version rejected
- Planning fingerprint mismatch rejected
- `order_check` failure prevents send
- All accepted → `PENDING`
- Partial accepted → `PARTIALLY_PLACED`
- None accepted → `FAILED`
- Immediate fill creates position snapshot
- Pending plus position → `PARTIALLY_FILLED`
- Positions only → `OPEN`
- Outcome unknown blocks retry
- Restart simulation does not duplicate sends
- Entry count never exceeds 8
- Total lots never exceeds 2.0000
- Only XAUUSD executes

## Orders and positions

Test:

- Modify owned pending order
- Reject unowned order
- Delete owned order
- Idempotent confirmed deletion
- Modify owned position SL/TP
- Reject unowned position
- Close owned position
- Confirm close through synchronization
- Cancel campaign pending orders
- Close campaign positions
- Partial ticket failures reported
- No cross-campaign mutation

## Emergency

Test:

- Disabled by default
- Wrong phrase rejected
- Live account blocked
- Non-XAUUSD untouched
- Application-owned scope works
- Account-wide scope needs stronger confirmation
- Partial failure returns ticket results
- Audit events created

## Persistence

Test:

- Execution batches
- Child jobs
- Unique idempotency keys
- Worker locks
- Execution attempts
- Order-check records
- Order-send records
- Account snapshots
- Symbol snapshots
- Sync events
- Decimal round trips
- Transaction rollback

## Migration

Test:

```text
003 → 004
004 → 003
re-upgrade
base → head
```

## Contracts

Validate all fixtures through Pydantic and Zod.

---

# BENCHMARKS

Add:

```text
100,000 request builds
1,000 five-entry fake execution batches
10,000 idempotency lookups
```

Report median, p95, total duration, and throughput where useful.

No network calls in benchmarks.

---

# LOGGING AND AUDIT

Structured fields:

```text
service
event
adapter_mode
mt5_health_state
account_environment
account_login_masked
account_server
campaign_id
campaign_code
planned_entry_id
job_id
batch_id
operation_type
idempotency_key
mt5_retcode
duration_ms
correlation_id
```

Audit events:

```text
MT5_INITIALIZE_REQUESTED
MT5_INITIALIZED
MT5_INITIALIZE_BLOCKED
MT5_SHUTDOWN
MT5_ACCOUNT_BLOCKED
MT5_SYMBOL_RESOLVED
MT5_SYMBOL_RESOLUTION_FAILED
EXECUTION_PREFLIGHT_PASSED
EXECUTION_PREFLIGHT_BLOCKED
EXECUTION_BATCH_QUEUED
EXECUTION_JOB_STARTED
ORDER_CHECK_PASSED
ORDER_CHECK_FAILED
ORDER_SEND_SUCCEEDED
ORDER_SEND_FAILED
EXECUTION_OUTCOME_UNKNOWN
CAMPAIGN_PARTIALLY_PLACED
CAMPAIGN_PENDING
CAMPAIGN_PARTIALLY_FILLED
CAMPAIGN_OPEN
ORDER_MODIFIED
ORDER_DELETED
POSITION_SLTP_MODIFIED
POSITION_CLOSE_REQUESTED
POSITION_CLOSED
CAMPAIGN_CANCEL_REQUESTED
CAMPAIGN_CLOSE_REQUESTED
EMERGENCY_CLOSE_REQUESTED
EMERGENCY_CLOSE_COMPLETED
```

Never log secrets.

---

# DOCUMENTATION

Create or update:

```text
docs/MT5_ADAPTER.md
docs/MT5_DEMO_SAFETY.md
docs/MT5_SYMBOL_RESOLUTION.md
docs/MT5_EXECUTION_WORKER.md
docs/MT5_ORDER_LIFECYCLE.md
docs/MT5_POSITION_OPERATIONS.md
docs/MT5_API.md
docs/MT5_SMOKE_TESTS.md
docs/PHASE_7_REPORT.md
docs/CAMPAIGN_STATE_MACHINE.md
docs/DATA_MODEL.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/REPOSITORY_STRUCTURE.md
README.md
```

Update README:

```text
Prompt 7 of 12 completed
Next: Prompt 8 — OpenWA WhatsApp Worker
```

---

# ROOT SCRIPTS

Add or update:

```text
mt5:test
mt5:contracts
mt5:benchmark
mt5:migrations
mt5:status
mt5:demo-smoke
```

`mt5:demo-smoke` must require explicit opt-in.

CI must run fake and dry-run tests only.

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
pnpm mt5:test
pnpm mt5:contracts
pnpm mt5:benchmark
pnpm mt5:migrations
```

Run Alembic:

```powershell
alembic upgrade head
alembic current
alembic downgrade -1
alembic upgrade head
```

Test full base-to-head migration.

Start FastAPI in fake mode and verify all MT5 endpoints.

Test dry-run mode.

Run real read-only initialization only when MT5 is available and the account is confirmed demo.

Do not run real-demo smoke tests without every explicit opt-in.

Verify:

- No duplicate jobs
- No duplicate sends
- Fake mode has no real broker tickets
- Total volume never exceeds 2.0000
- Entry count never exceeds 8
- Only XAUUSD operates
- Live execution remains impossible
- No WhatsApp or LLM integration exists
- No credentials are tracked

Search active source for:

```text
password=
MT5_LIVE_EXECUTION_ENABLED=true
MT5_DEMO_ONLY=false
wa.create
open-wa
OpenAI
Anthropic
Gemini
langchain
```

`order_send` is allowed only inside the real adapter and its direct tests/documentation.

Run:

```powershell
git status --short
```

If all checks pass:

```powershell
git add .
git commit -m "feat: complete Prompt 7 - MT5 Adapter and Demo Execution Worker"
```

Do not push.

---

# FAILURE HANDLING

Do not mark Prompt 7 complete because files were generated.

When a check fails:

1. Read the complete error.
2. Fix the project-controlled root cause.
3. Rerun the targeted check.
4. Do not weaken demo-only gates.
5. Do not add a live override.
6. Do not store passwords.
7. Do not auto-select ambiguous symbols.
8. Do not skip `order_check`.
9. Do not blindly retry `order_send`.
10. Do not process trade operations concurrently.
11. Do not bypass version or planning-fingerprint checks.
12. Do not claim smoke tests passed when not run.
13. Do not falsify dry-run tickets.
14. Report external blockers honestly.

---

# COMPLETION REQUIREMENTS

Prompt 7 is complete only when:

- Fake, dry-run, and real adapters exist
- Real adapter is demo-only
- Live accounts are blocked
- Hedging mode is required
- Account/server allowlists work
- XAUUSD symbol resolution works
- Symbol ambiguity blocks execution
- Symbol-specification compatibility is checked
- Filling/time policies are safe
- Every send is preceded by `order_check`
- Durable single-writer queue works
- Idempotency survives restart simulation
- Ambiguous outcomes block retries
- Campaign transitions work
- Partial placement is represented correctly
- Order and position persistence works
- Modify/delete/close operations work in fake tests
- Emergency close is disabled by default
- Mutating APIs require local authentication
- Migration and contracts pass
- All project-controlled checks pass
- WhatsApp integration remains absent
- Live execution remains impossible
- LLM integration remains absent
- No credentials are committed

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 7 OF 12 COMPLETED

Project root:
- ...

Versions:
- MT5 adapter version:
- Execution worker version:
- Planner version:
- State machine version:
- Parser version:
- Contract version:
- MetaTrader5 package version:
- Python version and architecture:

Adapter modes:
- Fake:
- Dry run:
- Real:
- Default mode:

Safety gates:
- Execution default:
- Demo only:
- Live execution:
- Automatic execution:
- Manual confirmation:
- Hedging required:
- Login allowlist:
- Server allowlist:
- Local API authentication:

MT5 initialization:
- Terminal detection:
- Account detection:
- Demo/live detection:
- Margin mode detection:
- Trade permission:
- Shutdown:
- Real terminal test status:

Symbol:
- Canonical symbol:
- Resolution strategy:
- Resolved broker symbol:
- Ambiguity handling:
- Specification compatibility:
- Filling mode:
- Time policy:

Execution worker:
- Queue type:
- Single writer:
- Durable jobs:
- Idempotency:
- Retry policy:
- Partial placement policy:
- Outcome-unknown handling:

Order lifecycle:
- Order check:
- Order send:
- Pending-order modification:
- Pending-order deletion:
- Campaign pending cancellation:
- Synchronization:

Position lifecycle:
- SL/TP modification:
- Position closing:
- Campaign closing:
- Emergency close:
- Emergency default state:

Campaign states:
- PLANNED to PLACING_ORDERS:
- All accepted:
- Partial placement:
- Partial fill:
- Open:
- Failure:

API:
- MT5 status:
- Initialize/shutdown:
- Preflight:
- Campaign execution:
- Job status:
- Order operations:
- Position operations:
- Emergency operation:

Persistence:
- Migration revision:
- Execution jobs:
- Account snapshots:
- Symbol snapshots:
- Order records:
- Position records:
- Execution attempts:
- Sync events:

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
- MT5 contract tests:
- Request-builder benchmark:
- Fake-worker benchmark:
- Idempotency benchmark:
- FastAPI MT5 endpoints:
- Database safety verification:
- Security scan:
- CI:

Real demo smoke test:
- Status:
- Account environment:
- Hedging verified:
- Test order placed:
- Test order removed:
- Positions remaining:
- Reason if not run:

Safety verification:
- Trading enabled by default: false
- Live execution possible: false
- Demo-only enforcement: true
- WhatsApp integration: absent
- LLM integration: absent
- Credentials committed: false
- Concurrent trade sends: false
- Blind order retries: false
- Order check skipped: false

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 8 OF 12 — OPENWA WHATSAPP WORKER
```

Stop after Prompt 7.
