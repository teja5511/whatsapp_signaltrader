# PROMPT 9 OF 12 — FASTAPI ORCHESTRATION AND REAL-TIME EVENTS
# 3 PROMPTS REMAIN AFTER THIS PHASE

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the repository, preserve all valid Phase 1–8 work, implement Prompt 9 completely, run every applicable validation, fix every project-controlled failure, and stop after Prompt 9.

Do not explain the plan before starting.  
Do not ask questions unless work is blocked by a genuinely unresolved requirement.  
Do not bypass existing safety gates.  
Do not enable live-account execution.  
Do not allow the WhatsApp worker to call MT5 directly.  
Do not resolve ambiguous trading commands automatically.  
Do not add AI or LLM interpretation.  
Do not implement the final desktop dashboard in this phase.  
Do not push to GitHub.  
Do not create a remote.

A clean local Git commit at the end is allowed only after every required check passes.

---

# CURRENT VERIFIED PROJECT STATE

Phases 1–8 are complete.

Current verified capabilities include:

- Requirements and architecture documentation
- pnpm monorepo
- Tauri/React desktop scaffold
- Node.js/TypeScript OpenWA WhatsApp worker
- Python FastAPI trading service
- SQLite + SQLAlchemy 2.x
- Alembic revisions through `004_mt5_demo_execution_worker`
- Pydantic contracts
- TypeScript/Zod contracts
- Deterministic parser version `1.0.0`
- Campaign state machine version `1.0.0`
- Duplicate strategy version `1.0.0`
- Planner version `1.0.0`
- Risk engine version `1.0.0`
- MT5 adapter version `1.0.0`
- MT5 execution worker version `1.0.0`
- WhatsApp worker version `1.0.0`
- OpenWA adapter boundary
- Single approved WhatsApp group
- Single approved admin
- Durable WhatsApp spool
- Authenticated worker-to-service delivery
- Durable MT5 single-writer execution queue
- Demo-only MT5 execution safety
- Trading disabled by default
- Live execution impossible
- LLM integration absent

Do not rewrite working Phase 1–8 functionality without a documented technical reason.

---

# PHASE OBJECTIVE

Implement the central FastAPI orchestration layer and durable real-time event system that connects:

```text
WhatsApp ingestion
→ deterministic parsing
→ campaign creation or command attachment
→ confirmation or automatic-mode decision
→ planning
→ demo-only MT5 execution queue
→ state updates
→ real-time events
```

This phase must implement:

1. Central orchestration service
2. Durable orchestration runs
3. Transactional outbox
4. Domain event persistence
5. Real-time WebSocket events
6. Real-time SSE events
7. Event replay by sequence
8. Aggregate system status
9. Automation pause/resume controls
10. Confirmation/automatic execution modes
11. Safe automatic demo pipeline
12. Human confirmation pipeline
13. Delayed TP orchestration
14. Follow-up command orchestration
15. Re-entry orchestration
16. SL modification dispatch
17. Close and cancel dispatch
18. Ambiguous command confirmation workflow
19. Worker status integration
20. MT5 status integration
21. Cross-service correlation IDs
22. Local API authentication and authorization
23. Idempotent event processing
24. Failure isolation and retry policy
25. End-to-end fake-worker/fake-MT5 tests
26. Comprehensive documentation and benchmarks

Do not implement:

- Final Tauri dashboard
- Full startup reconciliation
- Full broker-history reconciliation
- Production packaging
- Installer creation
- Live trading
- Multiple WhatsApp accounts
- Multiple groups
- Multiple MT5 accounts
- Multiple instruments
- AI or LLM trading decisions

Prompt 10 will implement the final desktop dashboard.  
Prompt 11 will implement full reconciliation, emergency reliability, and hardening.  
Prompt 12 will implement packaging and end-to-end release validation.

---

# SOURCE-OF-TRUTH DOCUMENTS

Read before implementation:

```text
README.md
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
docs/TRADING_RULES.md
docs/COMMAND_CLASSIFICATION.md
docs/CAMPAIGN_STATE_MACHINE.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/OPEN_DECISIONS.md
docs/PARSER_ARCHITECTURE.md
docs/CAMPAIGN_IMPLEMENTATION.md
docs/CAMPAIGN_MATCHING.md
docs/DUPLICATE_PROTECTION.md
docs/ENTRY_PLANNER.md
docs/RISK_ENGINE.md
docs/PLANNING_POLICIES.md
docs/MT5_ADAPTER.md
docs/MT5_DEMO_SAFETY.md
docs/MT5_EXECUTION_WORKER.md
docs/WHATSAPP_WORKER.md
docs/WHATSAPP_MESSAGE_ENVELOPE.md
docs/WHATSAPP_SPOOL_AND_RETRY.md
docs/PHASE_8_REPORT.md
```

Do not silently resolve any item in:

```text
docs/OPEN_DECISIONS.md
```

---

# NON-NEGOTIABLE ORCHESTRATION BOUNDARIES

Allowed flow:

```text
WhatsApp Worker
    ↓
FastAPI ingestion endpoint
    ↓
Parser
    ↓
Campaign/command service
    ↓
Orchestration policy
    ↓
Planner
    ↓
MT5 execution queue
```

Forbidden flow:

```text
WhatsApp Worker → MT5
WhatsApp Worker → execution queue
WhatsApp Worker → direct campaign approval
Desktop → MT5
Desktop → SQLite
Parser → MT5
LLM → execution
```

The FastAPI trading service remains the only business orchestrator.

---

# VERSIONING

Use:

```text
orchestrator_version = "1.0.0"
event_contract_version = "1.0.0"
outbox_version = "1.0.0"
system_status_contract_version = "1.0.0"
```

Expose all versions through APIs.

---

# MODULE STRUCTURE

Use a clean structure similar to:

```text
apps/trading-service/src/trading_service/
├── orchestration/
│   ├── __init__.py
│   ├── constants.py
│   ├── errors.py
│   ├── contracts.py
│   ├── policies.py
│   ├── coordinator.py
│   ├── signal_pipeline.py
│   ├── command_pipeline.py
│   ├── confirmation_pipeline.py
│   ├── automatic_pipeline.py
│   ├── delayed_tp.py
│   ├── reentry.py
│   ├── execution_dispatch.py
│   ├── status_aggregation.py
│   ├── idempotency.py
│   ├── retry.py
│   └── service.py
├── events/
│   ├── __init__.py
│   ├── constants.py
│   ├── contracts.py
│   ├── domain_event.py
│   ├── publisher.py
│   ├── outbox.py
│   ├── dispatcher.py
│   ├── subscriptions.py
│   ├── replay.py
│   ├── websocket.py
│   ├── sse.py
│   └── service.py
└── tests/
    ├── orchestration/
    └── events/
```

Keep orchestration, event persistence, event delivery, and API transport separate.

---

# ORCHESTRATION INPUTS

Support orchestration from:

```text
WHATSAPP_MESSAGE
USER_ACTION
SYSTEM_ACTION
MT5_EVENT
RECOVERY
```

Prompt 9 should actively use:

```text
WHATSAPP_MESSAGE
USER_ACTION
SYSTEM_ACTION
MT5_EVENT
```

`RECOVERY` may be reserved for Prompt 11.

Every orchestration input must include:

```text
source_type
source_id
correlation_id
causation_id
received_at
actor_type
actor_id
payload
```

---

# CORRELATION AND CAUSATION

Every message and event must carry:

```text
correlation_id
causation_id
```

Rules:

- A new WhatsApp message starts or continues one correlation chain.
- Parser result uses the same correlation ID.
- Campaign creation uses the same correlation ID.
- Planning uses the same correlation ID.
- Execution batch uses the same correlation ID.
- Child MT5 jobs use the same correlation ID and their own causation IDs.
- Follow-up commands preserve their own message correlation and reference the campaign correlation.
- Events must expose both IDs.
- Do not generate a new unrelated correlation ID at every layer.

Use UUIDs.

---

# AUTOMATION STATES

Use:

```text
PAUSED
RUNNING
EMERGENCY_STOPPED
```

Default:

```text
PAUSED
```

Rules:

## PAUSED

- WhatsApp ingestion continues.
- Parsing continues.
- Campaign creation continues.
- Command attachment continues.
- Planning may occur only through explicit user action.
- No automatic planning.
- No automatic MT5 queueing.
- Explicit authenticated user actions may still approve, plan, or execute demo campaigns when permitted.

## RUNNING

- Automatic-mode campaigns may proceed through safe orchestration.
- Confirmation-mode campaigns remain confirmation-gated.
- Ambiguous commands remain confirmation-gated.
- Demo-only MT5 gates still apply.
- Live accounts remain blocked.

## EMERGENCY_STOPPED

- Ingestion may continue and spool.
- Parsing may continue.
- No new planning.
- No new MT5 jobs.
- Existing queued jobs must be blocked or cancelled when safe.
- Existing running send operation must not be interrupted unsafely.
- Emergency state remains until explicit authenticated reset.
- Reset requires a confirmation phrase.

Required reset phrase:

```text
RESET EMERGENCY STOP
```

---

# EXECUTION MODES

Use:

```text
CONFIRMATION
AUTOMATIC
```

Default:

```text
CONFIRMATION
```

Campaign mode must be snapshotted at creation.

Do not retroactively alter the mode of existing campaigns unless an explicit audited user action updates that campaign before execution.

---

# SIGNAL ORCHESTRATION PIPELINE

For a valid persisted `NEW_SIGNAL` message:

```text
1. Verify source group and sender
2. Parse idempotently
3. Create or retrieve signal
4. Run exact duplicate check
5. Run semantic duplicate check
6. Create or retrieve campaign
7. Emit campaign event
8. Evaluate TP completeness
9. Evaluate automation state
10. Evaluate campaign execution mode
11. Stop at the correct state
```

## Incomplete signal

When TP1 or TP2 is missing:

```text
campaign state = WAITING_FOR_TP
```

Do not plan.

Do not execute.

## Complete signal in confirmation mode

```text
campaign state = AWAITING_CONFIRMATION
```

Do not plan automatically.

Do not execute.

## Complete signal in automatic mode while automation is PAUSED

Keep campaign in a safe pre-execution state.

Preferred:

```text
AWAITING_CONFIRMATION
```

with reason:

```text
AUTOMATION_PAUSED
```

Do not create a new state.

## Complete signal in automatic mode while automation is RUNNING

Proceed only when:

- Trading is explicitly enabled
- MT5 execution is explicitly enabled
- Adapter is demo-only ready
- Planning policies are fully resolved
- Campaign has valid TP1 and TP2
- Campaign passes all safety checks

Pipeline:

```text
campaign
→ PLANNED approval equivalent with SYSTEM trigger
→ plan
→ MT5 preflight
→ queue execution batch
```

Every automatic step must be audited.

No automatic execution is allowed if any planning policy remains unresolved.

---

# TRADING ENABLEMENT

Separate:

```text
automation_state
execution_mode
trading_enabled
mt5_execution_enabled
```

All must align for automatic execution.

Automatic execution requires:

```text
automation_state = RUNNING
campaign.execution_mode = AUTOMATIC
trading_enabled = true
mt5_execution_enabled = true
MT5 account = demo
MT5 margin mode = hedging
all safety checks pass
```

Default remains:

```text
trading_enabled = false
mt5_execution_enabled = false
automation_state = PAUSED
execution_mode = CONFIRMATION
```

Do not provide any path to live trading.

---

# SAFE TRADING ENABLE CONTROL

Add authenticated control to enable demo trading.

Requirements:

- Demo adapter must be ready.
- Live account must be impossible.
- Confirmation phrase required.
- Current account and server displayed.
- Hedging verified.
- XAUUSD symbol resolved.
- Maximum total lots remains 2.0000.
- Local API token required.
- Full audit event.

Required phrase:

```text
ENABLE DEMO XAUUSD TRADING
```

Disabling trading requires no destructive confirmation phrase.

Enabling trading must not automatically set automation to RUNNING.

These are separate controls.

---

# DELAYED TP ORCHESTRATION

When a delayed TP command is attached:

1. Match the campaign.
2. Apply TP1 or TP2 using existing deterministic rules.
3. Emit `TAKE_PROFIT_UPDATED`.
4. If still incomplete:
   - remain `WAITING_FOR_TP`
5. If complete:
   - evaluate campaign mode and automation state
6. Confirmation mode:
   - transition to `AWAITING_CONFIRMATION`
7. Automatic mode + automation paused:
   - transition to `AWAITING_CONFIRMATION` or remain safely blocked with reason
8. Automatic mode + automation running:
   - continue through safe automatic planning and demo execution only if every gate passes

Do not overwrite existing TPs with an unspecified third TP.

---

# USER CONFIRMATION PIPELINE

For confirmation-mode campaigns:

```text
AWAITING_CONFIRMATION
```

User approval must:

1. Require local API authentication.
2. Require expected campaign version.
3. Persist confirmation.
4. Transition to `PLANNED`.
5. Invoke planning using configured policies.
6. Stop with a structured blocked result if policies are unresolved.
7. Run MT5 preflight.
8. Queue demo execution only when explicitly requested by the approval action or a separate execute action.

Support two safe approval contracts:

```text
APPROVE_ONLY
APPROVE_PLAN_AND_QUEUE_DEMO
```

Default:

```text
APPROVE_ONLY
```

Do not queue MT5 automatically from a generic approval without explicit requested action.

---

# AUTOMATIC PIPELINE

The automatic pipeline must be deterministic.

Required gates:

```text
automation_state = RUNNING
campaign mode = AUTOMATIC
trading enabled = true
MT5 execution enabled = true
demo-only account
hedging mode
XAUUSD only
campaign complete
campaign not duplicate
planning policies resolved
risk validation passes
planning fingerprint valid
MT5 preflight passes
no active duplicate execution batch
```

If any gate fails:

- Do not execute.
- Persist an orchestration decision.
- Emit a blocking event.
- Leave the campaign in the safest valid state.

Do not repeatedly retry a structurally blocked campaign.

---

# COMMAND ORCHESTRATION

Process attached follow-up commands through the coordinator.

Supported deterministic commands:

```text
MODIFY_STOP_LOSS
CLOSE_CAMPAIGN
CANCEL_SIGNAL
ZONE_VALID
REENTRY
ADD_TAKE_PROFIT
```

Ambiguous commands:

```text
SECURE_PROFITS
HOLD
EXIT_ON_COMFORT
SKIP_FOR_NOW
```

must never execute automatically.

---

# MODIFY STOP LOSS ORCHESTRATION

For a matched `MODIFY_STOP_LOSS` command:

## Pre-execution campaign

When no MT5 orders or positions exist:

- Update campaign requested/current SL.
- Invalidate existing plan when the SL changed.
- Require replan.
- Emit `CAMPAIGN_PLAN_INVALIDATED`.
- Do not create an MT5 modification job.

## Pending orders or open positions exist

- Verify campaign ownership.
- Verify demo-only MT5 readiness.
- Validate requested SL structurally.
- Queue the correct MT5 modification operations.
- Use the single-writer queue.
- Return command status:

```text
QUEUED
BLOCKED
REQUIRES_CONFIRMATION
FAILED
```

Do not modify unrelated orders or positions.

Automatic execution of an SL command is allowed only when:

- The command is explicit
- Campaign match is unambiguous
- Automation is RUNNING
- Campaign mode is AUTOMATIC
- Demo trading is enabled
- All MT5 gates pass

Otherwise require user confirmation.

---

# CLOSE CAMPAIGN ORCHESTRATION

For explicit `CLOSE_CAMPAIGN`:

## Pre-execution campaign

Transition to:

```text
CANCELLED
```

No MT5 operation.

## Campaign with pending orders only

Queue:

```text
cancel campaign pending orders
```

Then synchronize and transition appropriately.

## Campaign with positions

Queue:

```text
close campaign positions
```

and cancel remaining pending orders.

Do not mark `CLOSED` until synchronization confirms no owned orders or positions remain.

Automatic close is allowed only for explicit unambiguous commands in automatic mode while automation is RUNNING and demo trading is enabled.

Otherwise require confirmation.

---

# CANCEL SIGNAL ORCHESTRATION

For explicit `CANCEL_SIGNAL`:

- Pre-execution campaign → `CANCELLED`
- Pending-order campaign → queue pending-order cancellation
- Open positions must not be closed unless the command explicitly means close
- Do not treat cancel as close when positions exist
- Emit a warning requiring user confirmation when scope is unclear

`Skip this for now` remains ambiguous and must not cancel automatically.

---

# ZONE VALID ORCHESTRATION

For `ZONE_VALID`:

- Attach command
- Emit event
- Preserve campaign state
- Do not reactivate a cancelled campaign
- Do not execute
- Do not resolve the open reactivation decision

---

# REENTRY ORCHESTRATION

For explicit re-entry:

1. Use existing matched parent campaign.
2. Create one idempotent child campaign.
3. Evaluate TP completeness.
4. Snapshot current safe settings.
5. Preserve parent linkage.
6. Apply normal confirmation or automatic-mode flow.
7. Do not bypass semantic duplicate protection except through the existing explicit re-entry exception.
8. Do not create two child campaigns for one command.

---

# AMBIGUOUS COMMAND CONFIRMATION

Create a confirmation record containing:

```text
command_id
campaign_id
suggested_action
original_text
match_type
candidate_count
created_at
expires_at
status
```

Statuses:

```text
PENDING
APPROVED
REJECTED
CANCELLED
EXPIRED
```

Default expiry:

```text
No automatic expiry for campaign confirmation
```

For ambiguous command confirmations, allow a configurable expiry:

```text
AMBIGUOUS_COMMAND_CONFIRMATION_TTL_MINUTES=30
```

Expiry must not execute anything.

A user approval must specify an explicit normalized action.

Examples:

```text
APPROVE_CLOSE
APPROVE_CANCEL
APPROVE_HOLD_NO_ACTION
APPROVE_SKIP_NO_ACTION
REJECT_COMMAND
```

Do not infer the action from the ambiguous text.

---

# ORCHESTRATION RUNS

Create durable orchestration-run persistence.

Suggested table:

```text
orchestration_runs
```

Fields:

```text
id
orchestrator_version
source_type
source_id
correlation_id
causation_id
campaign_id
command_id
status
current_step
input_payload_json
output_payload_json
error_code
error_message
started_at
completed_at
created_at
updated_at
```

Statuses:

```text
RECEIVED
RUNNING
WAITING
SUCCEEDED
BLOCKED
FAILED
CANCELLED
```

Constraints:

```text
source_type + source_id + orchestrator_version unique
```

This provides orchestration idempotency.

---

# ORCHESTRATION STEPS

Persist step results.

Suggested table:

```text
orchestration_steps
```

Fields:

```text
id
orchestration_run_id
sequence
step_name
status
input_json
output_json
error_code
error_message
started_at
completed_at
created_at
```

Statuses:

```text
PENDING
RUNNING
SUCCEEDED
SKIPPED
BLOCKED
FAILED
```

Do not store secrets.

---

# DOMAIN EVENTS

Create durable domain events.

Suggested table:

```text
domain_events
```

Fields:

```text
id
sequence
event_id
event_type
event_version
aggregate_type
aggregate_id
campaign_id
correlation_id
causation_id
actor_type
actor_id
payload_json
occurred_at
created_at
```

Constraints:

```text
event_id unique
sequence unique and monotonically increasing
```

Do not use an in-memory-only event bus as the source of truth.

---

# TRANSACTIONAL OUTBOX

Create:

```text
event_outbox
```

Fields:

```text
id
event_id
status
attempt_count
available_at
locked_at
locked_by
published_at
last_error
created_at
updated_at
```

Statuses:

```text
PENDING
PUBLISHING
PUBLISHED
FAILED
```

Requirements:

- Business mutation and outbox insert in one transaction.
- Dispatcher publishes committed events only.
- Retry temporary publication failures.
- Idempotent publication by event ID.
- One local dispatcher writer.
- Events remain replayable even after publication.
- Do not delete domain events after delivery.

Suggested Alembic revision:

```text
005_orchestration_and_realtime_events
```

---

# EVENT TYPES

Implement stable event names including:

```text
SYSTEM_STATUS_CHANGED
AUTOMATION_STATE_CHANGED
EXECUTION_MODE_CHANGED
TRADING_ENABLED
TRADING_DISABLED
EMERGENCY_STOP_ACTIVATED
EMERGENCY_STOP_RESET

WHATSAPP_WORKER_STATUS_CHANGED
WHATSAPP_MESSAGE_RECEIVED
WHATSAPP_MESSAGE_REJECTED
WHATSAPP_MESSAGE_PARSED

SIGNAL_DETECTED
SIGNAL_INCOMPLETE
SIGNAL_COMPLETE
SIGNAL_DUPLICATE_BLOCKED

CAMPAIGN_CREATED
CAMPAIGN_UPDATED
CAMPAIGN_AWAITING_CONFIRMATION
CAMPAIGN_WAITING_FOR_TP
CAMPAIGN_APPROVED
CAMPAIGN_REJECTED
CAMPAIGN_PLANNED
CAMPAIGN_PLAN_BLOCKED
CAMPAIGN_EXECUTION_QUEUED
CAMPAIGN_PLACING_ORDERS
CAMPAIGN_PENDING
CAMPAIGN_PARTIALLY_PLACED
CAMPAIGN_PARTIALLY_FILLED
CAMPAIGN_OPEN
CAMPAIGN_MANAGING
CAMPAIGN_CLOSING
CAMPAIGN_CLOSED
CAMPAIGN_CANCELLED
CAMPAIGN_FAILED

COMMAND_RECEIVED
COMMAND_MATCHED
COMMAND_MATCH_AMBIGUOUS
COMMAND_REQUIRES_CONFIRMATION
COMMAND_APPROVED
COMMAND_REJECTED
COMMAND_DISPATCHED
COMMAND_COMPLETED
COMMAND_FAILED

TAKE_PROFIT_UPDATED
STOP_LOSS_UPDATED
PLAN_INVALIDATED
REENTRY_CREATED

MT5_STATUS_CHANGED
MT5_JOB_QUEUED
MT5_JOB_STARTED
MT5_JOB_SUCCEEDED
MT5_JOB_FAILED
MT5_OUTCOME_UNKNOWN

AUDIT_EVENT_CREATED
```

Do not use arbitrary unversioned event strings.

---

# EVENT CONTRACT

Every event must include:

```json
{
  "event_contract_version": "1.0.0",
  "event_id": "uuid",
  "sequence": 123,
  "event_type": "CAMPAIGN_CREATED",
  "event_version": "1.0",
  "aggregate_type": "CAMPAIGN",
  "aggregate_id": "uuid",
  "campaign_id": "uuid",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "actor_type": "SYSTEM",
  "actor_id": null,
  "occurred_at": "2026-07-23T10:00:00Z",
  "payload": {}
}
```

Financial fields remain decimal strings.

Do not include:

- Passwords
- API tokens
- Session data
- QR payload
- Cookies
- Raw MT5 credentials

---

# EVENT DELIVERY

Support:

```text
WebSocket
Server-Sent Events
REST replay
```

## WebSocket

Endpoint:

```text
GET /api/v1/events/ws
```

Requirements:

- Local bearer authentication
- Client subscription filters
- Heartbeats
- Backpressure handling
- Bounded per-client queue
- Slow-client disconnect
- Event sequence included
- Reconnect using last sequence
- No event mutation by clients

## SSE

Endpoint:

```text
GET /api/v1/events/sse
```

Requirements:

- Local bearer authentication
- `Last-Event-ID` support
- Heartbeats
- Sequence-based replay
- Same event contract as WebSocket

## REST replay

```text
GET /api/v1/events
GET /api/v1/events/{event_id}
GET /api/v1/events/replay?after_sequence=
GET /api/v1/events/latest-sequence
```

Support filters:

```text
event_type
campaign_id
aggregate_type
after_sequence
before_sequence
limit
```

Default limit:

```text
100
```

Maximum:

```text
1000
```

---

# BACKPRESSURE

Each real-time client must have a bounded queue.

Default:

```text
REALTIME_CLIENT_QUEUE_SIZE=500
```

If a client falls behind:

1. Emit a final overflow notice when possible.
2. Disconnect the client.
3. Client must replay from the last sequence.
4. Do not block domain-event persistence.
5. Do not block orchestration.

---

# EVENT REPLAY

Replay must be ordered by:

```text
sequence ascending
```

Requirements:

- No duplicates within one replay response.
- Stable pagination.
- Client can resume after disconnect.
- Old events remain available according to retention.
- Retention must not be implemented as destructive deletion in Prompt 9 unless safely archived.

---

# SYSTEM STATUS AGGREGATION

Create a central status response.

Sources:

```text
FastAPI service
Database
WhatsApp worker
Parser
Campaign service
Planner
MT5 adapter
MT5 execution worker
Event outbox dispatcher
Automation state
Execution mode
Trading enabled state
```

Normalized overall states:

```text
HEALTHY
DEGRADED
BLOCKED
ERROR
STARTING
STOPPED
```

Create:

```text
GET /api/v1/system/status
GET /api/v1/system/health
GET /api/v1/system/readiness
GET /api/v1/system/versions
```

Status must include:

```text
automation_state
default_execution_mode
trading_enabled
mt5_execution_enabled
mt5_account_environment
mt5_margin_mode
whatsapp_worker_state
whatsapp_spool_pending
active_campaign_count
awaiting_confirmation_count
waiting_for_tp_count
queued_mt5_jobs
outbox_pending
latest_event_sequence
```

Do not expose secrets.

---

# WHATSAPP WORKER STATUS INTEGRATION

FastAPI may poll or receive status from the worker.

Use authenticated local HTTP.

Required behaviour:

- Timeouts
- Cached last-known status
- Staleness timestamp
- Worker unavailable → system degraded, not crashed
- Do not block parser ingestion already received
- Do not allow worker to control trading settings

Add:

```text
WHATSAPP_WORKER_URL=http://127.0.0.1:8010
WHATSAPP_WORKER_STATUS_TIMEOUT_MS=2000
WHATSAPP_WORKER_STATUS_TTL_SECONDS=5
```

---

# MT5 STATUS INTEGRATION

Use the existing MT5 adapter/status service.

Status aggregation must distinguish:

```text
fake
dry_run
real
disabled
blocked
ready
```

A fake adapter must never be displayed as a real broker connection.

---

# CONTROL API

Add authenticated endpoints:

```text
GET /api/v1/control/state

POST /api/v1/control/automation/pause
POST /api/v1/control/automation/resume
POST /api/v1/control/emergency-stop
POST /api/v1/control/emergency-stop/reset

POST /api/v1/control/execution-mode
POST /api/v1/control/trading/enable-demo
POST /api/v1/control/trading/disable
```

## Pause

- Idempotent
- Stops new automatic planning and execution
- Does not delete campaigns
- Does not close positions
- Emits event

## Resume

- Requires authenticated request
- Does not enable trading
- Does not automatically execute previously blocked campaigns unless explicitly requested by policy
- Emits event

## Emergency stop

Required phrase:

```text
EMERGENCY STOP XAUUSD
```

Actions:

- Set automation state `EMERGENCY_STOPPED`
- Disable trading
- Block new MT5 jobs
- Cancel queued not-started jobs when safe
- Do not blindly interrupt current send
- Emit high-severity event
- Do not automatically close positions in Prompt 9

## Reset emergency stop

Required phrase:

```text
RESET EMERGENCY STOP
```

Does not re-enable trading.

## Set execution mode

Values:

```text
CONFIRMATION
AUTOMATIC
```

Updates default for new campaigns only.

## Enable demo trading

Required phrase:

```text
ENABLE DEMO XAUUSD TRADING
```

Must pass MT5 demo/hedging/readiness gates.

## Disable trading

Immediate and idempotent.

---

# CAMPAIGN ORCHESTRATION API

Add or extend:

```text
POST /api/v1/orchestration/messages/{raw_message_id}
POST /api/v1/orchestration/campaigns/{campaign_id}/approve
POST /api/v1/orchestration/campaigns/{campaign_id}/reject
POST /api/v1/orchestration/campaigns/{campaign_id}/plan
POST /api/v1/orchestration/campaigns/{campaign_id}/queue-demo
POST /api/v1/orchestration/commands/{command_id}/approve
POST /api/v1/orchestration/commands/{command_id}/reject
POST /api/v1/orchestration/campaigns/{campaign_id}/retry-blocked
GET /api/v1/orchestration/runs
GET /api/v1/orchestration/runs/{run_id}
GET /api/v1/orchestration/runs/{run_id}/steps
```

All mutating endpoints require authentication.

---

# MESSAGE INGESTION ORCHESTRATION

The existing worker sends to:

```text
POST /api/v1/parser/messages
```

Preserve compatibility.

After successful persistence, trigger orchestration through one of these safe designs:

```text
A. parser endpoint invokes orchestration after commit
B. parser endpoint writes an outbox event consumed by the orchestrator
```

Preferred:

```text
transactional outbox event
```

Do not perform the entire pipeline inside the worker HTTP request.

The parser response may include:

```text
orchestration_run_id
orchestration_status
```

but should return promptly.

---

# IDEMPOTENCY

Use durable idempotency for:

```text
message orchestration
campaign approval
campaign rejection
planning request
execution queue request
command approval
command rejection
control actions
event publication
```

Create keys from stable canonical inputs.

Repeated requests must return existing results.

Do not duplicate:

- Campaigns
- Plans
- MT5 batches
- Command actions
- Events
- Confirmations

---

# RETRY POLICY

Retries are allowed only for temporary orchestration infrastructure failures.

Examples:

```text
outbox dispatcher temporary failure
worker status timeout
MT5 status timeout
temporary database lock
```

Do not automatically retry:

```text
order_send ambiguous outcome
invalid campaign state
unresolved planning policy
live-account block
ambiguous command
risk validation failure
```

Use exponential backoff with persisted attempt counts where required.

---

# FAILURE ISOLATION

A failure in one component must not crash the entire service.

Examples:

- WhatsApp worker unavailable → degraded status
- MT5 unavailable → block execution, keep ingestion
- Event client slow → disconnect client
- Outbox publication failure → retry
- One orchestration run fails → persist failure and continue other runs
- Invalid message → audit and stop that run

---

# DATABASE MIGRATION

Inspect the existing schema.

Create:

```text
005_orchestration_and_realtime_events
```

when required.

Add:

```text
orchestration_runs
orchestration_steps
domain_events
event_outbox
```

Add fields or indexes needed for:

```text
correlation_id
causation_id
event sequence
outbox status
orchestration idempotency
confirmation actions
automation state history
```

Indexes:

```text
orchestration_runs.source_type + source_id
orchestration_runs.correlation_id
orchestration_runs.campaign_id
orchestration_runs.status
orchestration_steps.orchestration_run_id + sequence
domain_events.sequence
domain_events.event_type
domain_events.campaign_id
domain_events.correlation_id
event_outbox.status + available_at
```

Preserve all existing data.

---

# SETTINGS

Add safe settings:

```text
automation_state = PAUSED
default_execution_mode = CONFIRMATION
trading_enabled = false
orchestrator_enabled = true
event_dispatcher_enabled = true
realtime_client_queue_size = 500
ambiguous_command_confirmation_ttl_minutes = 30
whatsapp_worker_url = http://127.0.0.1:8010
whatsapp_worker_status_timeout_ms = 2000
whatsapp_worker_status_ttl_seconds = 5
```

Reject unsafe values.

Do not allow:

```text
live execution
non-XAUUSD instrument
automation RUNNING with emergency state active
trading enabled without demo MT5 readiness
```

---

# SHARED CONTRACTS

Update Python Pydantic and TypeScript/Zod contracts for:

```text
AutomationState
ExecutionMode
TradingControlState
OrchestrationSourceType
OrchestrationRunStatus
OrchestrationStepStatus
OrchestrationRun
OrchestrationStep
OrchestrationDecision
DomainEvent
DomainEventType
OutboxStatus
EventReplayRequest
EventReplayResponse
RealtimeSubscription
RealtimeOverflowNotice
SystemComponentStatus
SystemStatus
SystemHealth
SystemReadiness
ControlActionRequest
ControlActionResult
CampaignApprovalAction
CommandApprovalAction
AutomaticPipelineResult
ConfirmationPipelineResult
```

All financial values remain decimal strings.

Unknown enum values must fail.

---

# REAL-TIME AUTHENTICATION

WebSocket and SSE must require the local API token.

Support token through:

```text
Authorization header
```

For browser/WebSocket limitations, allow a short-lived local connection ticket.

Add:

```text
POST /api/v1/events/ticket
```

Requirements:

- Bearer token required
- Ticket expires within 60 seconds
- Single-use
- Stored hashed
- Bound to localhost
- Cannot mutate data
- Never log raw ticket

Do not expose the long-lived token in query strings.

---

# EVENT CLIENT FILTERS

Support subscriptions by:

```text
event_types
campaign_ids
aggregate_types
minimum_severity
```

Default:

```text
all non-sensitive events
```

Do not allow clients to request secret payloads.

---

# EVENT PAYLOAD REDACTION

Before publication:

- Remove authorization tokens
- Remove WhatsApp session data
- Remove QR payload
- Remove MT5 passwords
- Mask account login
- Remove local filesystem secrets
- Keep campaign, order, position, and status data needed by the UI

Add tests for redaction.

---

# AUDIT EVENTS

Audit all control and orchestration decisions.

Required audit events include:

```text
ORCHESTRATION_RUN_CREATED
ORCHESTRATION_RUN_SUCCEEDED
ORCHESTRATION_RUN_BLOCKED
ORCHESTRATION_RUN_FAILED
AUTOMATION_PAUSED
AUTOMATION_RESUMED
EMERGENCY_STOP_ACTIVATED
EMERGENCY_STOP_RESET
EXECUTION_MODE_CHANGED
DEMO_TRADING_ENABLED
TRADING_DISABLED
CAMPAIGN_AUTOMATIC_FLOW_STARTED
CAMPAIGN_CONFIRMATION_FLOW_STARTED
CAMPAIGN_APPROVAL_RECEIVED
CAMPAIGN_REJECTION_RECEIVED
COMMAND_CONFIRMATION_CREATED
COMMAND_CONFIRMATION_APPROVED
COMMAND_CONFIRMATION_REJECTED
OUTBOX_EVENT_CREATED
OUTBOX_EVENT_PUBLISHED
OUTBOX_EVENT_FAILED
REALTIME_CLIENT_CONNECTED
REALTIME_CLIENT_DISCONNECTED
REALTIME_CLIENT_OVERFLOW
```

---

# END-TO-END FAKE PIPELINE TESTS

Use:

```text
Fake OpenWA adapter
Fake MT5 adapter
Temporary SQLite database
Real parser
Real campaign service
Real planner
Real orchestration service
Real outbox
Real event dispatcher
```

Required scenarios:

## Confirmation-mode complete signal

```text
WhatsApp message
→ parser
→ campaign AWAITING_CONFIRMATION
→ event emitted
→ user approves APPROVE_ONLY
→ campaign PLANNED
→ no MT5 job
```

## Confirmation-mode approve and queue

```text
message
→ campaign AWAITING_CONFIRMATION
→ user approves APPROVE_PLAN_AND_QUEUE_DEMO
→ plan
→ preflight
→ MT5 batch queued
→ fake worker processes
→ campaign PENDING or OPEN
```

## Incomplete signal

```text
message
→ WAITING_FOR_TP
→ delayed TP1
→ still WAITING_FOR_TP
→ delayed TP2
→ AWAITING_CONFIRMATION
```

## Automatic mode paused

```text
automatic campaign
automation PAUSED
→ no plan
→ no execution
→ blocking event
```

## Automatic mode running but trading disabled

```text
→ no execution
→ TRADING_DISABLED block
```

## Automatic demo success

```text
automation RUNNING
campaign AUTOMATIC
trading enabled
fake demo MT5 ready
resolved planning policies
→ plan
→ queue
→ fake execution
```

## Automatic live-account block

```text
→ no execution
→ live-account blocked event
```

## Explicit SL command

Test pre-execution plan invalidation and active-trade MT5 modification queueing.

## Explicit close

Test pre-execution cancellation and active-trade close queueing.

## Cancel

Test pending-order cancellation without closing open positions unless explicitly requested.

## Re-entry

Test one child campaign and normal mode flow.

## Ambiguous command

Test confirmation creation and zero execution.

## Duplicate message

Test one campaign, one orchestration run, no duplicate plan, no duplicate MT5 batch.

## Service failure

Test outbox retry and run failure isolation.

---

# EVENT TESTS

Test:

- Monotonic sequence
- Unique event ID
- Business transaction plus outbox atomicity
- Outbox retry
- Idempotent publication
- WebSocket authentication
- SSE authentication
- Ticket single-use
- Replay after sequence
- Filters
- Slow-client overflow
- Heartbeat
- Reconnect
- Payload redaction
- Event ordering
- No secret leakage

---

# CONTROL TESTS

Test:

- Pause idempotency
- Resume idempotency
- Resume does not enable trading
- Emergency stop phrase
- Emergency reset phrase
- Emergency reset does not enable trading
- Automatic mode selection
- Confirmation mode selection
- Demo enable phrase
- Demo readiness required
- Live account blocked
- Trading disable
- Control events
- Audit persistence

---

# API TESTS

Test all new endpoints.

Verify:

```text
401 missing token
401 wrong token
403 safety block
404 missing resource
409 version/state conflict
422 validation
202 queued orchestration/execution
200 idempotent result
```

No endpoint may claim live execution.

---

# MIGRATION TESTS

Test:

```text
004 → 005
005 → 004
004 → 005 again
base → head
```

Preserve all existing messages, campaigns, plans, MT5 jobs, and worker-related data.

---

# CROSS-LANGUAGE CONTRACT TESTS

Validate orchestration and event fixtures through:

- Python Pydantic
- TypeScript Zod

Financial values remain decimal strings.

---

# PERFORMANCE TESTS

Add lightweight benchmarks.

## Event persistence

```text
100,000 domain event insert-contract constructions
```

## Event replay

Use a disposable database with:

```text
100,000 events
```

Benchmark replay after sequence with limit 100.

## Orchestration decision

```text
10,000 signal-flow decisions
```

## WebSocket fanout

Fake:

```text
1,000 clients
10,000 events
```

Use a safe synthetic benchmark without requiring real sockets when necessary.

Report median, p95, throughput, and total duration.

Do not create unrealistic hard failures.

---

# CI

Update CI to:

- Run orchestration tests
- Run event/outbox tests
- Run fake end-to-end pipeline
- Run WebSocket/SSE tests
- Run contract tests
- Never connect real WhatsApp
- Never connect real MT5
- Never enable trading
- Never run real smoke tests
- Never store secrets

---

# DOCUMENTATION

Create or update:

```text
docs/ORCHESTRATION.md
docs/AUTOMATION_AND_CONFIRMATION.md
docs/REALTIME_EVENTS.md
docs/TRANSACTIONAL_OUTBOX.md
docs/SYSTEM_STATUS.md
docs/CONTROL_API.md
docs/ORCHESTRATION_API.md
docs/END_TO_END_FLOW.md
docs/PHASE_9_REPORT.md
docs/ARCHITECTURE.md
docs/CAMPAIGN_STATE_MACHINE.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/REPOSITORY_STRUCTURE.md
README.md
```

## ORCHESTRATION.md

Include:

- Coordinator responsibilities
- Signal pipeline
- Command pipeline
- Correlation and causation
- Idempotency
- Failure isolation

## AUTOMATION_AND_CONFIRMATION.md

Include:

- PAUSED
- RUNNING
- EMERGENCY_STOPPED
- CONFIRMATION
- AUTOMATIC
- Demo trading enablement
- Safety gates

## REALTIME_EVENTS.md

Include:

- Event contract
- WebSocket
- SSE
- Replay
- Filters
- Backpressure
- Redaction

## TRANSACTIONAL_OUTBOX.md

Include:

- Atomic write
- Dispatcher
- Retry
- Idempotency
- Sequence ordering

## SYSTEM_STATUS.md

Include component aggregation and state meanings.

## CONTROL_API.md

Document all controls, phrases, and safety behaviour.

## ORCHESTRATION_API.md

Document orchestration endpoints and response codes.

## END_TO_END_FLOW.md

Document complete fake-mode flows from WhatsApp to MT5.

## PHASE_9_REPORT.md

Include:

- Files created
- Files changed
- Migration revision
- Orchestrator version
- Event contract version
- Outbox version
- Domain event count
- API endpoints
- Test count
- Benchmark results
- Fake end-to-end scenarios
- Known limitations
- Confirmation that live trading remains impossible
- Confirmation that the final dashboard is not implemented yet

Update README:

```text
Prompt 9 of 12 completed
Next: Prompt 10 — Tauri React Dashboard
```

---

# ROOT SCRIPTS

Add or update:

```text
orchestration:test
orchestration:contracts
orchestration:benchmark
orchestration:migrations
events:test
events:benchmark
e2e:fake
```

Preserve existing root commands.

---

# REQUIRED VALIDATION

Run all applicable checks.

## Existing validation

```powershell
powershell -ExecutionPolicy Bypass -File ./scripts/validate.ps1
```

Do not modify global execution policy.

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

## Orchestration and events

```powershell
pnpm orchestration:test
pnpm orchestration:contracts
pnpm orchestration:benchmark
pnpm orchestration:migrations
pnpm events:test
pnpm events:benchmark
pnpm e2e:fake
```

Use equivalent repository commands where required.

## Alembic

Run:

```powershell
alembic upgrade head
alembic current
alembic downgrade -1
alembic upgrade head
```

Test full base-to-head.

## Service integration

Start:

```text
FastAPI trading service
WhatsApp worker in fake mode
MT5 adapter in fake mode
MT5 execution worker
Event outbox dispatcher
```

Verify:

- Complete signal confirmation flow
- Complete signal automatic blocked flow
- Complete signal automatic demo flow
- Incomplete signal and delayed TP
- Explicit SL command
- Explicit close command
- Cancel command
- Re-entry
- Ambiguous command
- Duplicate message
- Worker unavailable degradation
- MT5 unavailable block
- WebSocket event stream
- SSE event stream
- Replay after disconnect

Stop everything cleanly.

## Security scan

Search active source code for:

```text
MT5_LIVE_EXECUTION_ENABLED=true
MT5_DEMO_ONLY=false
order_send
wa.create
open-wa
Authorization:
LOCAL_API_TOKEN=
password
sessionData
qr
OpenAI
Anthropic
Gemini
langchain
```

Allowed:

- Existing real OpenWA adapter
- Existing real MT5 adapter
- Authentication handling without hardcoded secrets

Forbidden:

- Hardcoded credentials
- Live enablement
- Worker-to-MT5 calls
- LLM usage
- QR/session leakage

## Git

Run:

```powershell
git status --short
```

If all checks pass, a local commit is allowed:

```powershell
git add .
git commit -m "feat: complete Prompt 9 - FastAPI Orchestration and Real-Time Events"
```

Do not push.

---

# FAILURE HANDLING

Do not mark Prompt 9 complete because files were generated.

When a check fails:

1. Read the complete error.
2. Fix the project-controlled root cause.
3. Rerun the targeted check.
4. Do not bypass automation-state checks.
5. Do not bypass confirmation mode.
6. Do not bypass demo-only MT5 checks.
7. Do not auto-execute ambiguous commands.
8. Do not publish events before transaction commit.
9. Do not use in-memory-only event persistence.
10. Do not lose event sequence ordering.
11. Do not block business transactions on slow clients.
12. Do not duplicate orchestration runs.
13. Do not duplicate MT5 batches.
14. Do not expose secrets in event payloads.
15. Do not claim live execution.
16. Do not falsely report a check as passed.
17. Report genuine external blockers honestly.

---

# COMPLETION REQUIREMENTS

Prompt 9 is complete only when:

- Central orchestration service works.
- Message orchestration is idempotent.
- Confirmation pipeline works.
- Automatic pipeline works in fake demo mode.
- Automatic pipeline is blocked while paused.
- Automatic pipeline is blocked while trading is disabled.
- Live account remains blocked.
- Delayed TP orchestration works.
- SL command orchestration works.
- Close and cancel orchestration work.
- Re-entry orchestration works.
- Ambiguous commands require explicit action.
- Automation controls work.
- Emergency stop works.
- Trading enable/disable controls work.
- Orchestration runs persist.
- Orchestration steps persist.
- Domain events persist.
- Transactional outbox works.
- WebSocket works.
- SSE works.
- Event replay works.
- Backpressure works.
- System status aggregation works.
- Worker status integration works.
- MT5 status integration works.
- Correlation and causation IDs propagate.
- Event payloads are redacted.
- Python and TypeScript contracts agree.
- Migration works.
- Fake end-to-end flows pass.
- All project-controlled checks pass.
- Final dashboard remains unimplemented.
- Live execution remains impossible.
- LLM integration remains absent.
- No credentials are committed.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 9 OF 12 COMPLETED

Project root:
- ...

Versions:
- Orchestrator version:
- Event contract version:
- Outbox version:
- System status contract version:
- Parser version:
- Planner version:
- MT5 adapter version:
- WhatsApp worker version:
- Contract version:

Orchestration:
- Signal pipeline:
- Command pipeline:
- Confirmation pipeline:
- Automatic pipeline:
- Delayed TP:
- Re-entry:
- Idempotency:
- Correlation IDs:
- Causation IDs:
- Failure isolation:

Controls:
- Default automation state:
- Default execution mode:
- Trading default:
- Pause:
- Resume:
- Emergency stop:
- Emergency reset:
- Demo trading enable:
- Trading disable:
- Live execution:

Automatic mode:
- Paused behaviour:
- Trading-disabled behaviour:
- Demo-ready behaviour:
- Live-account behaviour:
- Unresolved-policy behaviour:
- Ambiguous-command behaviour:

Events:
- Persistence:
- Event sequence:
- Transactional outbox:
- WebSocket:
- SSE:
- Replay:
- Filters:
- Backpressure:
- Payload redaction:
- Latest event sequence:

System status:
- FastAPI:
- Database:
- WhatsApp worker:
- Parser:
- Campaign service:
- Planner:
- MT5 adapter:
- MT5 worker:
- Outbox:
- Overall state:

API:
- System status:
- Control:
- Orchestration:
- Events:
- WebSocket:
- SSE:
- Event ticket:
- Replay:

Persistence:
- Migration revision:
- Orchestration runs:
- Orchestration steps:
- Domain events:
- Event outbox:
- Confirmation records:
- Audit events:

End-to-end fake scenarios:
- Confirmation-only signal:
- Approve and queue demo:
- Incomplete signal:
- Delayed TP:
- Automatic paused:
- Automatic trading disabled:
- Automatic demo success:
- Live account blocked:
- SL command:
- Close command:
- Cancel command:
- Re-entry:
- Ambiguous command:
- Duplicate message:

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
- Orchestration contract tests:
- Event tests:
- Fake end-to-end:
- Event persistence benchmark:
- Event replay benchmark:
- Orchestration benchmark:
- WebSocket fanout benchmark:
- Service integration:
- Security scan:
- CI:

Safety verification:
- Default automation paused: true
- Default confirmation mode: true
- Trading enabled by default: false
- Live execution possible: false
- WhatsApp worker calls MT5: false
- Ambiguous commands automatic: false
- Events contain secrets: false
- LLM integration: absent
- Credentials committed: false

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 10 OF 12 — TAURI REACT DASHBOARD
```

Stop after Prompt 9.
