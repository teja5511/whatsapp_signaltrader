# CONSOLIDATED ANTIGRAVITY PROMPT — PHASES 1 TO 3

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the current repository, preserve all valid existing work, repair missing or inconsistent items, implement everything required below, run all validations, fix project-controlled failures, and stop only when Phases 1–3 are fully complete.

Do not explain the plan before starting.  
Do not ask questions unless work is blocked by a genuinely unresolved trading rule.  
Do not create duplicate files or duplicate project roots.  
Do not push to GitHub.  
Do not create a remote.  
Do not connect to WhatsApp.  
Do not connect to MT5.  
Do not implement real trading execution.

---

# PROJECT OBJECTIVE

Build a Windows desktop application that will eventually:

- Read XAUUSD signals from one selected WhatsApp group.
- Use one WhatsApp account.
- Accept instructions only from one approved group administrator.
- Parse new signals and follow-up instructions.
- Create evenly distributed XAUUSD pending orders inside a signal zone.
- Execute and manage trades through MetaTrader 5.
- Use one Exness MT5 account.
- Start with a demo account.
- Require MT5 hedging mode.
- Support adjustable entry count and per-entry lot size.
- Prevent duplicate execution.
- Persist all signals, campaigns, commands, orders, positions and audit events.
- Support fully automatic and confirmation execution modes.
- Recover safely after application or computer restarts.

---

# CONFIRMED TRADING REQUIREMENTS

## Environment

```text
Instrument: XAUUSD only
Operating system: Windows
Broker: Exness
Platform: MetaTrader 5
Initial account: Demo
Account mode: Hedging
MT5 accounts: 1
WhatsApp accounts: 1
WhatsApp groups: 1 selected group
Approved senders: 1 admin
```

## Entry settings

```text
Minimum entries: 3
Maximum entries: 8
Default entries: 5
Lot size means per individual entry
Default development lot per entry: 0.30
Maximum total campaign lots: 2.00
```

Total requested exposure:

```text
entry_count × lot_per_entry
```

Execution must be blocked when:

```text
entry_count × lot_per_entry > 2.00
```

Do not silently reduce lot size.

Entry prices must be evenly distributed across the complete signal zone:

```text
step = (zone_high - zone_low) / (entry_count - 1)
```

Both zone boundaries must be included.

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

## Take-profit allocation

```text
Exactly 1 position → Signal TP1
Exactly 1 position → Signal TP2
All remaining positions → Fixed 100-pip TP
```

Examples:

```text
3 entries:
1 × 100-pip TP
1 × TP1
1 × TP2

5 entries:
3 × 100-pip TP
1 × TP1
1 × TP2

8 entries:
6 × 100-pip TP
1 × TP1
1 × TP2
```

## TP Open

For version 1:

```text
Store TP Open as signal metadata only.
Do not create an unmanaged open runner.
```

## Default application state

```text
Automation: paused
Execution mode: confirmation
Trading enabled: false
```

---

# SIGNAL EXAMPLES

Store these as parser fixtures. Do not implement parsing logic yet.

```text
Gold Sell
4120-4128

sl - 4136

tp - 4112
tp - 4104
tp - Open
```

```text
Gold Sell Limit
3990-3998

Sl - 4008
```

A TP may arrive later:

```text
TP 3960
```

Follow-up messages:

```text
Move SL to 4138 for added safety.
We barely survived the SL.
Exit this trade on your comfort.
Zone Valid.
Skip this for now.
Wait for update.
100 Pips Almost.
Secure Profits.
Market is very shaky move SL to 4074 for safety.
50+ Pips.
It will come to Zone again.
Hard SL 4013.
Same Zone for Re-entry.
Just touched our SL and reversed, if you haven't closed like mine, Hold it.
```

---

# UNRESOLVED TRADING RULES

Do not guess or silently resolve:

1. Exact XAUUSD price distance represented by 100 pips.
2. Behaviour when price is already inside the signal zone.
3. Behaviour when price has passed the full zone.
4. Whether orders are placed before delayed TP1 and TP2 arrive.
5. Which exact ladder indices receive TP1 and TP2.
6. Meaning of `Secure Profits`.
7. Meaning of `Exit this trade on your comfort`.
8. Meaning of `Hold it`.
9. Behaviour when a new signal arrives while an earlier campaign remains open.
10. Whether old filled positions remain active after a new signal.
11. Whether `Skip this for now` pauses or cancels pending orders.
12. Whether `Zone Valid` reactivates a paused campaign.

Document these in:

```text
docs/OPEN_DECISIONS.md
```

---

# REQUIRED ARCHITECTURE

```text
WhatsApp Group
      ↓
Node.js TypeScript WhatsApp Worker
      ↓
Python FastAPI Trading Service
      ↓
Single MT5 Execution Worker
      ↓
MetaTrader 5

Tauri React Desktop
      ↓
REST + WebSocket
      ↓
Python FastAPI Trading Service

Python Trading Service
      ↓
SQLite Database
```

## Technology stack

```text
Desktop:
- Tauri 2
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui-compatible structure
- TanStack Query
- Zustand
- Vitest
- React Testing Library

WhatsApp Worker:
- Node.js
- TypeScript
- Zod
- Pino
- Vitest
- OpenWA later, not now

Trading Service:
- Python
- FastAPI
- Uvicorn
- Pydantic
- SQLAlchemy 2.x
- Alembic
- pytest
- pytest-asyncio
- Ruff
- mypy or Pyright

Storage:
- SQLite

Workspace:
- pnpm workspaces
```

## Architecture rules

- WhatsApp worker must not contain trading logic.
- Desktop must never communicate directly with MT5.
- WhatsApp worker must never communicate directly with MT5.
- Python trading service owns all business logic.
- Python trading service is the only database owner.
- Only one execution worker may eventually send MT5 operations.
- No LLM may directly execute trades.
- All future trading behaviour must be deterministic and auditable.

---

# REQUIRED REPOSITORY STRUCTURE

Ensure this structure exists:

```text
project-root/
├── apps/
│   ├── desktop/
│   ├── whatsapp-worker/
│   └── trading-service/
├── packages/
│   ├── shared-contracts/
│   ├── ui/
│   └── parser-fixtures/
├── scripts/
├── infra/
│   └── docker/
├── docs/
├── .github/
│   └── workflows/
├── README.md
├── DEVELOPMENT.md
├── package.json
├── pnpm-workspace.yaml
├── tsconfig.base.json
├── eslint.config.*
├── prettier.config.*
├── .prettierignore
├── .editorconfig
├── .gitattributes
├── .gitignore
└── .env.example
```

If the repository currently contains:

```text
packages/contracts
```

rename it to:

```text
packages/shared-contracts
```

Update all references and do not leave both directories.

If Git is not initialized:

```powershell
git init
```

Do not commit unless explicitly requested.

---

# PHASE 1 — REQUIREMENTS AND ARCHITECTURE

Ensure all files exist and are fully populated:

```text
README.md
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
docs/TRADING_RULES.md
docs/COMMAND_CLASSIFICATION.md
docs/CAMPAIGN_STATE_MACHINE.md
docs/DATA_MODEL.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/OPEN_DECISIONS.md
docs/IMPLEMENTATION_ROADMAP.md
docs/ASSUMPTIONS.md
```

Requirements must use IDs such as:

```text
FR-001
NFR-001
SAFE-001
```

Document these campaign states:

```text
RECEIVED
PARSED
INVALID
WAITING_FOR_TP
AWAITING_CONFIRMATION
PLANNED
PLACING_ORDERS
PARTIALLY_PLACED
PENDING
PARTIALLY_FILLED
OPEN
MANAGING
CLOSING
CLOSED
CANCELLED
REJECTED
FAILED
```

Do not implement transition logic yet.

The latency requirement must be documented only as an internal processing target:

```text
Under healthy local conditions, target less than 500 ms from receipt of a WhatsApp event by the local worker to creation of a validated execution request, excluding WhatsApp delivery, MT5 terminal processing and broker execution.
```

Do not represent it as guaranteed end-to-end latency.

---

# PHASE 2 — MONOREPO AND DEVELOPMENT SCAFFOLD

## Root workspace

Create or repair root scripts:

```text
bootstrap
dev
dev:desktop
dev:whatsapp
dev:trading
build
build:desktop
build:whatsapp
lint
lint:fix
format
format:check
typecheck
test
test:unit
check
clean
doctor
```

Use:

```text
pnpm workspaces
TypeScript strict mode
ESLint
Prettier
Vitest
```

Do not use wildcard dependency versions.

Generate and retain a lockfile.

## Desktop scaffold

Create a safe desktop shell in:

```text
apps/desktop
```

Display:

```text
WhatsApp XAUUSD Trading Bot
Development Scaffold

Demo/Live: Unknown
Automation: Paused
Execution Mode: Confirmation
WhatsApp: Not connected
MT5: Not connected
Trading Service: Checking
```

Create placeholder navigation for:

```text
Overview
WhatsApp
MT5
Active Signals
Positions
Settings
Logs
```

Create disabled safety controls:

```text
Pause Automation
Emergency Close All XAUUSD
Automatic / Confirmation
```

Label them:

```text
Development placeholder — no trading action connected
```

The desktop must start with:

```text
Automation paused
Confirmation mode
Disconnected or unknown connection states
```

Add basic render and component tests.

## WhatsApp worker scaffold

Create:

```text
apps/whatsapp-worker
```

Use:

```text
Node.js
TypeScript
Zod
Pino
Vitest
```

Create:

```text
src/
├── index.ts
├── config/
├── logging/
├── health/
├── contracts/
└── adapters/
```

It must:

- Load validated environment configuration.
- Start without connecting to WhatsApp.
- Emit structured logs.
- Shut down on SIGINT and SIGTERM.
- Report:

```text
WhatsApp integration is not implemented.
```

Do not install or connect OpenWA yet.

## Trading service scaffold

Create:

```text
apps/trading-service
```

Use:

```text
apps/trading-service/
├── pyproject.toml
├── alembic.ini
├── src/
│   └── trading_service/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       ├── logging.py
│       ├── api/
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       ├── adapters/
│       └── contracts/
└── tests/
```

Provide:

```text
GET /health
GET /ready
GET /version
```

Trading must remain disabled.

Do not create order placement, modification or closing endpoints.

## Parser fixtures

Create:

```text
packages/parser-fixtures/
├── README.md
└── fixtures/
    ├── new-signals/
    ├── follow-up-commands/
    ├── informational/
    ├── ambiguous/
    └── invalid/
```

Store all user-provided sample messages with metadata:

```json
{
  "expected_category": "unresolved_until_parser_phase",
  "source": "user-provided"
}
```

Do not create executable parser behaviour.

## Environment

Create a safe `.env.example`:

```text
APP_ENV=development
LOG_LEVEL=INFO

TRADING_SERVICE_HOST=127.0.0.1
TRADING_SERVICE_PORT=8000
TRADING_SERVICE_URL=http://127.0.0.1:8000

WHATSAPP_WORKER_HOST=127.0.0.1
WHATSAPP_WORKER_PORT=8010

LOCAL_API_TOKEN=replace-with-development-token

DATABASE_URL=sqlite:///./data/trading_bot.db

AUTOMATION_DEFAULT_STATE=paused
EXECUTION_MODE_DEFAULT=confirmation
TRADING_ENABLED=false
```

Do not commit a real `.env`.

## PowerShell scripts

Ensure these exist:

```text
scripts/check-environment.ps1
scripts/bootstrap.ps1
scripts/dev.ps1
scripts/test.ps1
scripts/lint.ps1
scripts/build.ps1
scripts/clean.ps1
scripts/validate.ps1
```

Scripts must:

- Work with paths containing spaces.
- Stop on errors.
- Return non-zero exit codes on failure.
- Never modify global PowerShell execution policy.
- Never connect WhatsApp.
- Never start MT5.
- Never enable trading.

---

# PHASE 3 — DATABASE AND SHARED DOMAIN CONTRACTS

## Financial data rules

Never use binary floating point for financial fields.

Python:

```python
decimal.Decimal
```

Database:

```text
Prices: NUMERIC(18, 8)
Volumes: NUMERIC(12, 4)
```

API and TypeScript:

```text
Decimal strings
```

Example:

```json
{
  "zone_low": "3990.00000000",
  "zone_high": "3998.00000000",
  "lot_per_entry": "0.3000",
  "maximum_total_lots": "2.0000"
}
```

Do not use JavaScript numbers for:

- Price
- Lot size
- Volume
- Stop loss
- Take profit
- Monetary values

Use:

```text
UUID4 internal IDs
UTC ISO 8601 timestamps
contract_version = "1.0.0"
```

---

# SQLITE DATABASE CONFIGURATION

Use:

- SQLite
- SQLAlchemy 2.x
- Alembic
- Explicit session lifecycle
- Transaction-safe repositories
- Database health checking
- Schema revision checking

Enable:

```sql
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
```

Database URL must come from environment configuration.

The Python service must be the only database owner.

The desktop and WhatsApp worker must never access SQLite directly.

---

# DATABASE TABLES

Implement SQLAlchemy models and one Alembic migration for all tables below.

## application_settings

```text
id
key
value_json
value_type
is_sensitive
created_at
updated_at
```

Defaults:

```text
automation_state = paused
execution_mode = confirmation
trading_enabled = false
entry_count = 5
lot_per_entry = 0.3000
maximum_total_lots = 2.0000
minimum_entry_count = 3
maximum_entry_count = 8
instrument_allowlist = ["XAUUSD"]
environment_kind = unknown
```

## approved_groups

```text
id
platform_group_id
display_name
is_active
created_at
updated_at
```

Constraint:

```text
platform_group_id unique
```

## approved_senders

```text
id
platform_sender_id
display_name
role
is_active
created_at
updated_at
```

Role:

```text
ADMIN
```

Constraint:

```text
platform_sender_id unique
```

## raw_whatsapp_messages

```text
id
whatsapp_message_id
group_id
sender_id
message_text
normalized_text
message_timestamp
received_at
quoted_whatsapp_message_id
is_reply
message_type
processing_status
correlation_id
raw_metadata_json
created_at
updated_at
```

Constraint:

```text
UNIQUE(group_id, whatsapp_message_id)
```

Indexes:

```text
whatsapp_message_id
group_id
sender_id
message_timestamp
processing_status
quoted_whatsapp_message_id
```

## parsed_messages

```text
id
raw_message_id
parser_version
category
confidence_kind
is_executable
parsed_payload_json
validation_errors_json
created_at
```

Categories:

```text
NEW_SIGNAL
FOLLOW_UP_COMMAND
INFORMATIONAL
AMBIGUOUS
INVALID
UNSUPPORTED
```

## signals

```text
id
raw_message_id
instrument
direction
order_intent
zone_low
zone_high
stop_loss
tp1
tp2
tp_open_present
signal_timestamp
status
created_at
updated_at
```

Enums:

```text
direction:
BUY
SELL

order_intent:
LIMIT
UNSPECIFIED

status:
DETECTED
VALIDATED
INVALID
SUPERSEDED
```

Constraints:

```text
instrument = XAUUSD
zone_low <= zone_high
```

## campaigns

```text
id
campaign_code
signal_id
parent_campaign_id
reentry_sequence
state
execution_mode
environment_kind
instrument
entry_count
lot_per_entry
maximum_total_lots
requested_total_lots
stop_loss
tp1
tp2
tp_open_present
requires_confirmation
approved_at
rejected_at
closed_at
created_at
updated_at
version
```

Constraints:

```text
campaign_code unique
entry_count between 3 and 8
lot_per_entry > 0
maximum_total_lots <= 2.0000
requested_total_lots <= 2.0000
instrument = XAUUSD
```

Campaign states:

```text
RECEIVED
PARSED
INVALID
WAITING_FOR_TP
AWAITING_CONFIRMATION
PLANNED
PLACING_ORDERS
PARTIALLY_PLACED
PENDING
PARTIALLY_FILLED
OPEN
MANAGING
CLOSING
CLOSED
CANCELLED
REJECTED
FAILED
```

## campaign_state_transitions

```text
id
campaign_id
from_state
to_state
reason_code
reason_text
trigger_type
trigger_reference_id
transitioned_at
correlation_id
created_at
```

Trigger types:

```text
WHATSAPP_MESSAGE
USER_ACTION
SYSTEM
MT5_EVENT
RECOVERY
```

Treat as append-only through repositories.

## campaign_commands

```text
id
campaign_id
raw_message_id
command_type
classification
extracted_value
extracted_value_kind
execution_eligibility
status
requires_confirmation
processed_at
created_at
updated_at
```

Future command values:

```text
MODIFY_STOP_LOSS
CLOSE_CAMPAIGN
CANCEL_SIGNAL
ZONE_VALID
REENTRY
ADD_TAKE_PROFIT
SECURE_PROFITS
HOLD
INFORMATION_ONLY
UNKNOWN
```

## planned_entries

```text
id
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
mt5_order_ticket
mt5_position_ticket
magic_number
order_comment
created_at
updated_at
```

TP categories:

```text
TP_100
TP_1
TP_2
```

Statuses:

```text
PLANNED
VALIDATED
SUBMITTING
ACCEPTED
REJECTED
CANCELLED
FILLED
CLOSED
FAILED
```

Constraints:

```text
UNIQUE(campaign_id, entry_sequence)
UNIQUE(campaign_id, normalized_price)
```

## mt5_orders

```text
id
campaign_id
planned_entry_id
mt5_ticket
symbol
order_type
volume
requested_price
accepted_price
stop_loss
take_profit
magic_number
comment
status
submitted_at
accepted_at
cancelled_at
raw_request_json
raw_response_json
created_at
updated_at
```

Constraint:

```text
mt5_ticket unique when present
```

## mt5_positions

```text
id
campaign_id
planned_entry_id
source_order_id
mt5_position_ticket
symbol
direction
volume
open_price
current_stop_loss
current_take_profit
opened_at
closed_at
close_price
status
raw_snapshot_json
created_at
updated_at
```

Statuses:

```text
OPEN
PARTIALLY_CLOSED
CLOSED
UNKNOWN
```

Constraint:

```text
mt5_position_ticket unique when present
```

## execution_attempts

```text
id
campaign_id
planned_entry_id
operation_type
attempt_number
request_payload_json
response_payload_json
result_code
result_message
success
started_at
completed_at
correlation_id
created_at
```

Operation types:

```text
PLACE_PENDING_ORDER
MODIFY_ORDER
DELETE_ORDER
MODIFY_POSITION_SLTP
CLOSE_POSITION
CLOSE_CAMPAIGN
EMERGENCY_CLOSE
RECONCILE
```

Persistence only. Do not implement execution.

## duplicate_keys

```text
id
duplicate_type
duplicate_key
raw_message_id
campaign_id
expires_at
created_at
```

Duplicate types:

```text
EXACT_MESSAGE
SEMANTIC_SIGNAL
EXPLICIT_REENTRY
```

Constraint:

```text
UNIQUE(duplicate_type, duplicate_key)
```

## user_confirmations

```text
id
campaign_id
action
decision
decided_by
decision_reason
decided_at
correlation_id
created_at
```

Actions:

```text
EXECUTE_CAMPAIGN
REJECT_CAMPAIGN
AMBIGUOUS_COMMAND
EMERGENCY_CLOSE
CLOSE_CAMPAIGN
```

Decisions:

```text
APPROVED
REJECTED
CANCELLED
```

## audit_events

```text
id
event_type
severity
actor_type
actor_id
campaign_id
raw_message_id
entity_type
entity_id
summary
details_json
correlation_id
occurred_at
created_at
```

Actor types:

```text
SYSTEM
USER
WHATSAPP_ADMIN
MT5
SERVICE
```

Treat as append-only through repositories.

## application_errors

```text
id
service
error_code
error_type
message
sanitized_context_json
stack_trace
correlation_id
campaign_id
raw_message_id
occurred_at
resolved_at
created_at
```

Never store secrets in error context.

---

# RELATIONSHIPS AND DELETE RULES

- Use foreign keys.
- Raw WhatsApp messages must not be deleted when campaigns are removed.
- Signals must retain raw-message traceability.
- Campaigns should not normally be hard deleted.
- State transitions, commands, execution attempts and audit events must be preserved.
- Planned entries belong to one campaign.
- MT5 orders and positions belong to a campaign and planned entry.
- Prefer status updates over destructive deletion.
- Avoid broad cascading deletes that erase history.
- Use restrictive delete behaviour for audit-critical records.

---

# ALEMBIC

Configure inside:

```text
apps/trading-service
```

Required structure:

```text
apps/trading-service/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
```

Create one initial migration containing the complete Phase 3 schema.

Requirements:

- Upgrade from an empty database.
- Downgrade safely to base.
- Foreign keys.
- Unique constraints.
- Indexes.
- String-enum storage.
- Numeric precision.
- UTC timestamp handling.
- Current revision reporting.

Do not create the normal schema outside Alembic.

---

# PYTHON STRUCTURE

Use:

```text
apps/trading-service/src/trading_service/
├── api/
├── application/
│   ├── dto/
│   └── services/
├── domain/
│   ├── enums.py
│   ├── identifiers.py
│   ├── decimal_types.py
│   ├── models/
│   └── repositories/
├── infrastructure/
│   └── database/
│       ├── base.py
│       ├── engine.py
│       ├── session.py
│       ├── models/
│       ├── repositories/
│       ├── unit_of_work.py
│       └── health.py
└── contracts/
    ├── common.py
    ├── messages.py
    ├── signals.py
    ├── campaigns.py
    ├── entries.py
    └── audit.py
```

Keep ORM models separate from Pydantic contracts.

Never expose ORM models directly from FastAPI.

---

# REPOSITORY INTERFACES

Define and implement:

```text
SettingsRepository
RawMessageRepository
ParsedMessageRepository
SignalRepository
CampaignRepository
CampaignTransitionRepository
CampaignCommandRepository
PlannedEntryRepository
Mt5OrderRepository
Mt5PositionRepository
ExecutionAttemptRepository
DuplicateKeyRepository
ConfirmationRepository
AuditRepository
ApplicationErrorRepository
```

Baseline operations:

```text
get_by_id
add
update
list
exists
```

Entity-specific operations:

```text
RawMessageRepository.get_by_platform_message_id()
CampaignRepository.get_by_campaign_code()
CampaignRepository.list_active()
CampaignTransitionRepository.list_for_campaign()
PlannedEntryRepository.list_for_campaign()
DuplicateKeyRepository.exists_key()
SettingsRepository.get_by_key()
SettingsRepository.set_value()
```

Do not place trading business logic in repositories.

---

# UNIT OF WORK

Implement a SQLAlchemy Unit of Work exposing:

```text
session
commit
rollback
repository access
context-manager support
```

Requirements:

- Roll back on exceptions.
- Avoid uncontrolled nested sessions.
- Do not commit automatically after every row.
- Support future atomic campaign persistence.
- Test successful commit.
- Test rollback after exceptions.

---

# PYTHON PYDANTIC CONTRACTS

Create:

```text
RawWhatsAppMessage
ParsedMessage
GoldSignal
Campaign
CampaignStateTransition
CampaignCommand
PlannedEntry
Mt5OrderRecord
Mt5PositionRecord
ExecutionAttempt
UserConfirmation
AuditEvent
ApplicationError
ApplicationSettings
```

Requirements:

- Decimal fields use `Decimal`.
- JSON serialization emits decimal strings.
- IDs use UUID.
- Timestamps are timezone-aware.
- Enum values use stable uppercase strings.
- Include `contract_version`.
- Reject unknown enums.
- Reject invalid decimal values.
- Do not expose database internals unnecessarily.

---

# TYPESCRIPT/ZOD SHARED CONTRACTS

Use:

```text
packages/shared-contracts
```

Suggested structure:

```text
packages/shared-contracts/
├── src/
│   ├── common/
│   │   ├── decimal.ts
│   │   ├── identifiers.ts
│   │   └── timestamps.ts
│   ├── enums/
│   ├── messages/
│   ├── signals/
│   ├── campaigns/
│   ├── entries/
│   ├── audit/
│   └── index.ts
├── fixtures/
│   ├── valid/
│   └── invalid/
├── tests/
├── package.json
└── tsconfig.json
```

Create Zod schemas and inferred TypeScript types for:

```text
RawWhatsAppMessage
ParsedMessage
GoldSignal
Campaign
CampaignStateTransition
CampaignCommand
PlannedEntry
Mt5OrderRecord
Mt5PositionRecord
ExecutionAttempt
UserConfirmation
AuditEvent
ApplicationError
ApplicationSettings
```

Create validated or branded strings for:

```text
UUID
DecimalString
UtcTimestamp
WhatsAppMessageId
CampaignCode
CorrelationId
```

Never use JavaScript numbers for financial decimal fields.

Export everything from one stable package entry point.

---

# CROSS-LANGUAGE CONTRACT TESTING

Use JSON fixture-based consistency testing.

Create valid and invalid fixtures for:

- Raw WhatsApp message
- Parsed signal
- Campaign
- Planned entry
- State transition
- Audit event

Every valid fixture must pass:

- Python Pydantic validation.
- TypeScript Zod validation.

Every invalid fixture must fail both.

Use:

```text
contract_version = "1.0.0"
```

Add a root or workspace script to run both contract suites.

Do not introduce a complex code-generation system.

---

# ENUMS

Use stable uppercase wire values.

Implement at least:

```text
Direction
OrderIntent
CampaignState
ExecutionMode
EnvironmentKind
AutomationState
MessageCategory
ProcessingStatus
CommandType
CommandClassification
ExecutionEligibility
TpCategory
PlannedEntryStatus
Mt5OrderStatus
Mt5PositionStatus
DuplicateType
ConfirmationDecision
AuditSeverity
ActorType
TriggerType
```

Store enum values as strings in SQLite.

Unknown enum values must be rejected by Python and TypeScript.

---

# SETTINGS SERVICE

Implement safe settings persistence.

Requirements:

- Return defaults when values are not persisted.
- Seed defaults idempotently.
- Persist safe updates.
- Validate every setting.
- Never allow trading to be enabled in Phases 1–3.

Validation:

```text
entry_count >= 3
entry_count <= 8
lot_per_entry > 0
maximum_total_lots <= 2.0000
minimum_entry_count = 3
maximum_entry_count = 8
trading_enabled = false
instrument_allowlist = ["XAUUSD"]
```

Reject:

```text
entry_count = 9
maximum_total_lots = 3.00
instrument_allowlist = ["BTCUSD"]
trading_enabled = true
```

---

# SAFE API ENDPOINTS

Extend FastAPI with:

```text
GET /api/v1/database/status
GET /api/v1/database/version
GET /api/v1/settings
GET /api/v1/contracts/version
```

Optionally add:

```text
PUT /api/v1/settings
```

only if:

- Safety rules are enforced.
- Trading cannot be enabled.
- Unsupported instruments cannot be added.
- Credentials cannot be stored.
- Tests cover safe and rejected updates.

Do not add:

```text
POST /signals
POST /campaigns/execute
POST /orders
POST /positions/close
```

Update:

```text
GET /health
GET /ready
```

Health must include:

```json
{
  "service": "trading-service",
  "status": "ok",
  "version": "development",
  "trading_enabled": false,
  "mt5_connected": false,
  "database_connected": true,
  "database_schema_current": true
}
```

`/ready` must be not-ready when:

- Database cannot be opened.
- Foreign keys are disabled.
- Migration revision is behind.
- Required settings are invalid.

MT5 is not required for readiness in Phase 3.

---

# SAFE DEVELOPMENT SEEDING

Seed only:

```text
automation_state = paused
execution_mode = confirmation
trading_enabled = false
entry_count = 5
lot_per_entry = 0.3000
maximum_total_lots = 2.0000
minimum_entry_count = 3
maximum_entry_count = 8
instrument_allowlist = ["XAUUSD"]
environment_kind = unknown
```

Do not seed:

- Real WhatsApp group IDs.
- Real admin IDs.
- MT5 account numbers.
- Passwords.
- API tokens.
- Live credentials.

---

# TESTING

Use temporary SQLite databases.

Never use the developer runtime database in automated tests.

## Migration tests

Test:

- Upgrade empty database to head.
- Detect current revision.
- Downgrade to base.
- Upgrade again.

## Constraint tests

Test:

- Duplicate WhatsApp message ID in the same group is rejected.
- Same message ID in another group follows the composite uniqueness rule.
- Campaign code uniqueness.
- Planned-entry sequence uniqueness per campaign.
- Planned-entry normalized-price uniqueness per campaign.
- Duplicate-key uniqueness.
- Entry count below 3 rejected.
- Entry count above 8 rejected.
- Requested total lots above 2.00 rejected.
- Unsupported instrument rejected where enforced.
- Invalid foreign keys rejected.

## Decimal tests

Test exact round trips for:

```text
0.01
0.10
0.30
2.00
3990
3998
4120.12345678
```

Verify exact values survive:

```text
JSON
→ Pydantic
→ SQLAlchemy
→ SQLite
→ Pydantic
→ JSON
```

## Repository tests

Test:

- Add and retrieve raw message.
- Find raw message by WhatsApp message ID.
- Add signal.
- Add campaign.
- List active campaigns.
- Add planned entries.
- Add campaign state transition.
- Append audit event.
- Unit-of-work commit.
- Unit-of-work rollback.

## Settings tests

Test:

- Default settings.
- Safe update.
- Trading enable rejected.
- Invalid entry count rejected.
- Maximum lots violation rejected.
- Unsupported instrument rejected.

## Contract tests

Run the same fixtures through:

- Python Pydantic.
- TypeScript Zod.

Valid fixtures must pass both.  
Invalid fixtures must fail both.

---

# DOCUMENTATION

Ensure or create:

```text
docs/ENVIRONMENT_SETUP.md
docs/DEVELOPMENT.md
docs/REPOSITORY_STRUCTURE.md
docs/LOCAL_PORTS.md
docs/LOGGING.md
docs/DATABASE_IMPLEMENTATION.md
docs/DOMAIN_CONTRACTS.md
docs/DATABASE_MIGRATIONS.md
docs/CONTRACT_VERSIONING.md
docs/PHASE_2_REPORT.md
docs/PHASE_3_REPORT.md
```

Update:

```text
README.md
docs/DATA_MODEL.md
docs/IMPLEMENTATION_ROADMAP.md
```

`CONTRACT_VERSIONING.md` must define:

```text
contract_version = "1.0.0"
```

`PHASE_3_REPORT.md` must include:

- Files created.
- Phase 2 repairs.
- Migration revision.
- Tables created.
- Commands executed.
- Tests run.
- Test results.
- Warnings.
- Confirmation that no trading, WhatsApp or MT5 functionality exists.

Update README to show:

```text
Prompts 1–3 of 12 completed
Next: Prompt 4 — Deterministic Signal and Command Parser
```

---

# REQUIRED VALIDATION

Run all applicable commands.

## Root workspace

```powershell
pnpm install
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

## Python

```powershell
ruff check .
ruff format --check .
mypy apps/trading-service/src
pytest
```

## Alembic

Run against a disposable development database:

```powershell
alembic upgrade head
alembic current
alembic downgrade base
alembic upgrade head
```

## FastAPI

Start the trading service and verify:

```text
GET /health
GET /ready
GET /version
GET /api/v1/database/status
GET /api/v1/database/version
GET /api/v1/settings
GET /api/v1/contracts/version
```

Then stop it cleanly.

## Security source scan

Search active source code for:

```text
order_send
mt5.initialize
MetaTrader5
wa.create
createOrder
place_trade
execute_trade
live account password
```

Documentation matches are allowed.

There must be no active WhatsApp or MT5 integration code.

## Git

Run:

```powershell
git status --short
```

Do not push.  
Do not create a remote.

---

# FAILURE HANDLING

Do not mark the work complete because files were generated.

When a check fails:

1. Read the complete error.
2. Fix the project-controlled root cause.
3. Rerun the targeted check.
4. Do not disable strict typing.
5. Do not remove tests.
6. Do not replace Decimal values with floats.
7. Do not suppress database constraints.
8. Do not falsely report a test as passed.
9. Report external blockers honestly.

---

# COMPLETION REQUIREMENTS

Phases 1–3 are complete only when:

- All required Phase 1 documentation exists and is internally consistent.
- The monorepo structure exists.
- Root workspace scripts work.
- The React desktop shell builds.
- The WhatsApp worker scaffold builds and starts without connecting to WhatsApp.
- The FastAPI service starts.
- SQLite foreign keys are enabled.
- WAL mode is enabled.
- Busy timeout is configured.
- Alembic upgrade succeeds.
- Alembic downgrade succeeds.
- Alembic re-upgrade succeeds.
- All required tables exist.
- Database constraints and indexes exist.
- Repositories work.
- Unit of Work works.
- Default settings are seeded safely.
- Decimal values round-trip exactly.
- Python contracts validate.
- TypeScript/Zod contracts validate.
- Shared fixtures pass in both languages.
- Health and readiness expose database status.
- Trading remains disabled.
- MT5 integration remains absent.
- WhatsApp integration remains absent.
- No live credentials exist.
- All project-controlled checks pass.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PHASES 1 TO 3 OF 12 COMPLETED

Project root:
- ...

Phase 1:
- Requirements and architecture:
- Documentation verification:
- Open decisions preserved:

Phase 2:
- Monorepo applications:
- Shared packages:
- Development scripts:
- Environment setup:
- Repairs performed:

Phase 3 database:
- Engine:
- Schema revision:
- Tables:
- SQLite foreign keys:
- SQLite WAL:
- Busy timeout:

Domain contracts:
- Contract version:
- Python contracts:
- TypeScript/Zod contracts:
- Decimal wire format:
- Shared fixture compatibility:

Repositories implemented:
- ...

Settings defaults:
- Automation:
- Execution mode:
- Trading enabled:
- Entry count:
- Lot per entry:
- Maximum total lots:
- Instrument allowlist:

Validation:
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
- FastAPI endpoints:
- Cross-language contract tests:
- Security source scan:

Safety verification:
- Trading enabled: false
- MT5 integration: absent
- WhatsApp integration: absent
- Live credentials: absent
- Floating-point financial fields: absent

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 4 OF 12 — DETERMINISTIC SIGNAL AND COMMAND PARSER
```

Stop after completing Phases 1–3.
