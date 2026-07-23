# PROMPT 5 OF 12 — CAMPAIGN STATE MACHINE AND DUPLICATE PROTECTION
# 7 PROMPTS REMAIN AFTER THIS PHASE

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the repository, preserve all valid Phase 1–4 work, implement Prompt 5 completely, run all applicable validations, fix all project-controlled failures, and stop after Prompt 5.

Do not explain the plan before starting.  
Do not ask questions unless implementation is blocked by a genuinely unresolved trading rule.  
Do not connect to WhatsApp.  
Do not connect to MT5.  
Do not place, modify, or close trades.  
Do not calculate entry ladders.  
Do not allocate take-profit positions.  
Do not resolve unresolved trading decisions.  
Do not add AI or LLM behaviour.  
Do not push to GitHub.  
Do not create a remote.

A clean local Git commit at the end is allowed only after every required check passes.

---

# CURRENT VERIFIED PROJECT STATE

Phases 1–4 are complete.

Current project root:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Current verified capabilities:

- Requirements and architecture documentation
- pnpm monorepo
- Tauri/React desktop scaffold
- Node.js/TypeScript WhatsApp worker scaffold
- Python FastAPI trading service
- SQLite + SQLAlchemy 2.x
- Alembic revision `001_initial_schema`
- Pydantic contracts
- TypeScript/Zod contracts
- Deterministic parser version `1.0.0`
- Parser API
- Parser persistence
- Exact decimal handling
- Trading disabled
- MT5 integration absent
- WhatsApp integration absent
- LLM integration absent

Current parser supports:

- New XAUUSD signals
- Incomplete signals
- Stop-loss commands
- Close commands
- Cancel commands
- Zone-valid commands
- Re-entry commands
- Delayed TP commands
- Informational messages
- Ambiguous messages
- Unsupported instruments
- Reply metadata preservation

Do not rewrite working Phase 1–4 functionality without a documented technical reason.

---

# PHASE OBJECTIVE

Implement the persistent campaign lifecycle, campaign matching, exact duplicate protection, semantic duplicate protection, explicit re-entry handling, command attachment, idempotent processing, optimistic concurrency, and auditable state transitions.

This phase must implement:

1. Campaign creation from parsed signals
2. Campaign state machine
3. State transition validation
4. State transition persistence
5. Exact duplicate protection
6. Semantic duplicate protection
7. Explicit re-entry exceptions
8. Message-to-campaign matching
9. Reply-to-signal matching
10. Follow-up command attachment
11. Idempotent campaign creation
12. Optimistic concurrency
13. Campaign read APIs
14. Safe confirmation and rejection lifecycle
15. Recovery-safe persistence
16. Comprehensive tests

Do not implement:

- Entry ladder calculation
- TP allocation across positions
- 100-pip calculations
- MT5 connection
- MT5 order placement
- MT5 order modification
- Position closing
- WhatsApp connection
- OpenWA integration
- Final dashboard
- Trading execution
- AI interpretation

Trading must remain disabled.

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
docs/DATA_MODEL.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/OPEN_DECISIONS.md
docs/PARSER_ARCHITECTURE.md
docs/PARSER_RULES.md
docs/PARSER_CLASSIFICATION.md
docs/PARSER_API.md
docs/PARSER_VERSIONING.md
docs/PHASE_4_REPORT.md
```

Do not resolve any decision still listed in:

```text
docs/OPEN_DECISIONS.md
```

---

# CONFIRMED CAMPAIGN RULES

## Campaign creation

A campaign may be created only from a parsed message classified as:

```text
NEW_SIGNAL
```

The signal must:

- Use instrument `XAUUSD`
- Include direction `BUY` or `SELL`
- Include a valid zone
- Include a stop loss
- Pass parser validation
- Not be an exact duplicate
- Not be a blocked semantic duplicate
- Not exceed any currently known structural constraints
- Not trigger trading

A campaign must never be created from:

- Informational messages
- Ambiguous messages
- Unsupported instruments
- Invalid messages
- Standalone follow-up commands
- Duplicate signals unless explicit re-entry is approved by deterministic rules

## Initial campaign state

Use:

```text
WAITING_FOR_TP
```

when:

- TP1 is missing
- TP2 is missing
- Both are missing

Use:

```text
AWAITING_CONFIRMATION
```

when:

- Signal has the required structural fields
- TP1 and TP2 are available
- Execution mode is confirmation

Use:

```text
PARSED
```

only as a transient or recorded transition state if the state machine design requires it.

Do not place a campaign directly into:

```text
PLANNED
PENDING
OPEN
MANAGING
```

during Prompt 5.

## Automatic mode

Automatic mode may affect whether confirmation is required later, but Prompt 5 must not execute trades.

If execution mode is automatic and the campaign is structurally complete:

- State may become `PARSED` or a safe pre-planning state documented by the state machine
- It must not become `PLANNED`
- It must not place orders
- Trading remains disabled
- The campaign must remain blocked from execution until later phases

Prefer a clearly named state already present in the approved state list rather than inventing a new state.

---

# CAMPAIGN STATES

Use the existing stable wire values:

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

Do not rename these values.

---

# STATE MACHINE IMPLEMENTATION

Implement a deterministic state machine.

Suggested structure:

```text
apps/trading-service/src/trading_service/
├── campaigns/
│   ├── __init__.py
│   ├── constants.py
│   ├── state_machine.py
│   ├── transition_rules.py
│   ├── matching.py
│   ├── duplicate_service.py
│   ├── campaign_factory.py
│   ├── command_attachment.py
│   ├── service.py
│   ├── errors.py
│   └── result.py
└── tests/
    └── campaigns/
```

Keep:

- State transition rules
- Campaign creation
- Duplicate protection
- Campaign matching
- Persistence orchestration

in separate modules.

Do not create one monolithic service.

---

# ALLOWED TRANSITIONS FOR PROMPT 5

Implement at least these transitions:

```text
RECEIVED → PARSED
RECEIVED → INVALID
PARSED → WAITING_FOR_TP
PARSED → AWAITING_CONFIRMATION
PARSED → INVALID
WAITING_FOR_TP → WAITING_FOR_TP
WAITING_FOR_TP → AWAITING_CONFIRMATION
WAITING_FOR_TP → CANCELLED
WAITING_FOR_TP → REJECTED
WAITING_FOR_TP → FAILED
AWAITING_CONFIRMATION → AWAITING_CONFIRMATION
AWAITING_CONFIRMATION → REJECTED
AWAITING_CONFIRMATION → CANCELLED
AWAITING_CONFIRMATION → FAILED
AWAITING_CONFIRMATION → PLANNED
PLANNED → CANCELLED
PLANNED → FAILED
```

Important:

- `AWAITING_CONFIRMATION → PLANNED` is allowed only for explicit user approval.
- Prompt 5 may persist the state transition to `PLANNED`.
- Prompt 5 must not calculate entries.
- Prompt 5 must not create planned-entry rows.
- Prompt 5 must not place MT5 orders.
- `PLANNED` only means the campaign is approved for the future planning phase.
- This distinction must be documented and tested.

Support self-transitions only when they represent a meaningful idempotent update, such as:

```text
WAITING_FOR_TP → WAITING_FOR_TP
AWAITING_CONFIRMATION → AWAITING_CONFIRMATION
```

Every self-transition must have a reason code and must not create infinite duplicate transition rows.

---

# FORBIDDEN TRANSITIONS IN PROMPT 5

Reject transitions such as:

```text
RECEIVED → OPEN
PARSED → PENDING
WAITING_FOR_TP → OPEN
AWAITING_CONFIRMATION → OPEN
AWAITING_CONFIRMATION → PLACING_ORDERS
PLANNED → OPEN
CANCELLED → OPEN
REJECTED → PLANNED
CLOSED → OPEN
FAILED → OPEN
```

Later execution states may exist in the enum but must remain unreachable through Prompt 5 application services.

The state machine must reject invalid transitions with a typed error.

---

# TERMINAL STATES

Treat these as terminal for normal Prompt 5 operations:

```text
INVALID
CLOSED
CANCELLED
REJECTED
FAILED
```

Do not allow normal transitions out of terminal states.

Recovery behaviour for later phases may be documented but not implemented unless already approved.

---

# TRANSITION RECORDS

Every successful transition must create an append-only record containing:

```text
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

Prompt 5 must use only:

```text
WHATSAPP_MESSAGE
USER_ACTION
SYSTEM
```

Do not generate fake MT5 events.

Required reason codes should include at least:

```text
SIGNAL_RECEIVED
SIGNAL_PARSED
SIGNAL_INVALID
MISSING_TAKE_PROFIT
SIGNAL_COMPLETE
USER_APPROVED
USER_REJECTED
ADMIN_CANCELLED
ADMIN_CLOSE_REQUESTED
TP_UPDATE_RECEIVED
ZONE_VALID_RECEIVED
AMBIGUOUS_COMMAND_REQUIRES_CONFIRMATION
DUPLICATE_BLOCKED
SEMANTIC_DUPLICATE_BLOCKED
EXPLICIT_REENTRY_CREATED
PERSISTENCE_FAILURE
```

Do not use only free-form reason text.

---

# CAMPAIGN FACTORY

Implement deterministic campaign creation from a persisted parsed signal.

Input:

```text
Raw WhatsApp message
Parsed message
Signal record
Current settings
Correlation ID
```

Output:

```text
Campaign
Initial transition records
Duplicate decision
Campaign creation result
```

Campaign fields must include:

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
created_at
updated_at
version
```

Use current settings for:

```text
entry_count
lot_per_entry
maximum_total_lots
execution_mode
environment_kind
```

Calculate only:

```text
requested_total_lots = entry_count × lot_per_entry
```

Use Decimal.

Do not calculate:

- Entry prices
- 100-pip TP
- TP position allocation

Validate:

```text
3 <= entry_count <= 8
lot_per_entry > 0
requested_total_lots <= 2.0000
instrument = XAUUSD
trading_enabled = false
```

A campaign may still be created while trading is disabled because it is a planning object, but it must never execute.

---

# CAMPAIGN CODE GENERATION

Create deterministic, collision-safe human-readable codes.

Preferred format:

```text
GOLD-YYYYMMDD-NNNN
```

Example:

```text
GOLD-20260723-0001
```

Requirements:

- Unique
- Generated transactionally
- Stable after creation
- Not based only on row count without collision protection
- Safe during concurrent requests
- Re-entry campaigns receive new campaign codes
- Re-entry sequence stored separately

If SQLite concurrency makes sequential codes risky, use:

```text
GOLD-YYYYMMDD-<short unique suffix>
```

Document the chosen strategy.

Do not expose raw database row IDs as campaign codes.

---

# EXACT DUPLICATE PROTECTION

Use the existing exact uniqueness rule:

```text
group_id + whatsapp_message_id
```

Exact duplicate behaviour:

- The same WhatsApp message must never create two raw-message rows.
- The same raw message must never create two signal rows.
- The same signal must never create two campaigns.
- Repeated API submission returns the existing result.
- Restart must not reset duplicate memory.
- Duplicate protection must be database-backed.
- In-memory-only protection is insufficient.

Create an exact duplicate key using stable canonical data.

Example:

```text
EXACT_MESSAGE:<group_id>:<whatsapp_message_id>
```

Store it in the existing duplicate-key table when appropriate.

Do not include secrets.

---

# SEMANTIC DUPLICATE PROTECTION

Implement deterministic semantic signal fingerprinting.

Use normalized fields:

```text
instrument
direction
order_intent
zone_low
zone_high
stop_loss
tp1
tp2
tp_open_present
group_id
sender_id
```

Do not use raw whitespace or capitalization.

Canonicalize decimals before hashing.

Recommended canonical representation:

```json
{
  "instrument": "XAUUSD",
  "direction": "SELL",
  "order_intent": "LIMIT",
  "zone_low": "3990.00000000",
  "zone_high": "3998.00000000",
  "stop_loss": "4008.00000000",
  "tp1": null,
  "tp2": null,
  "tp_open_present": false,
  "group_id": "group-id",
  "sender_id": "admin-id"
}
```

Generate:

```text
SHA-256 canonical JSON hash
```

Store as:

```text
SEMANTIC_SIGNAL:<sha256>
```

Requirements:

- Stable key ordering
- Stable decimal formatting
- UTF-8 encoding
- No locale dependence
- No timestamps inside the semantic body
- No random values
- No Python object string representation
- No JavaScript object-order dependence

---

# SEMANTIC DUPLICATE WINDOW

Use a configurable semantic duplicate time window.

Default:

```text
24 hours
```

Create a setting:

```text
semantic_duplicate_window_hours = 24
```

Validation:

```text
1 <= semantic_duplicate_window_hours <= 168
```

Semantic duplicate decision:

- Same semantic fingerprint
- Same group
- Same sender
- Existing campaign created within the configured window
- No explicit re-entry command

Then:

```text
BLOCK_AS_SEMANTIC_DUPLICATE
```

Do not create a second campaign.

Return the existing campaign reference.

Document that this default may be changed later.

---

# SEMANTIC DUPLICATE DECISIONS

Use a typed result:

```text
NOT_DUPLICATE
EXACT_DUPLICATE
SEMANTIC_DUPLICATE
EXPLICIT_REENTRY_ALLOWED
PARSER_REPROCESS
```

Every duplicate decision must be auditable.

Record:

```text
duplicate_type
duplicate_key
raw_message_id
campaign_id
expires_at
created_at
```

Do not treat an explicit re-entry as an ordinary duplicate.

---

# EXPLICIT RE-ENTRY

The parser already recognizes:

```text
Same Zone for Re-entry
```

as:

```text
FOLLOW_UP_COMMAND
REENTRY
```

Prompt 5 must attach this command to a matched campaign.

When a valid explicit re-entry command is matched:

1. Load the source campaign.
2. Verify source campaign exists.
3. Verify source campaign is not structurally invalid.
4. Create a new campaign.
5. Set:

```text
parent_campaign_id = source campaign ID
reentry_sequence = source campaign reentry_sequence + 1
```

6. Copy only approved signal data:

```text
instrument
direction
order_intent through linked signal metadata
zone
stop_loss
tp1
tp2
tp_open_present
```

7. Use current safe settings for:

```text
entry_count
lot_per_entry
maximum_total_lots
execution_mode
environment_kind
```

8. Generate a new campaign code.
9. Generate a new signal record or a clearly linked re-entry signal snapshot according to the existing schema.
10. Record duplicate type:

```text
EXPLICIT_REENTRY
```

11. Record transition reason:

```text
EXPLICIT_REENTRY_CREATED
```

12. Do not calculate entries.
13. Do not execute trades.

The re-entry command must be processed idempotently.

Submitting the same re-entry command twice must not create two child campaigns.

---

# RE-ENTRY SAFETY

Do not allow re-entry when:

- No source campaign can be matched
- The source message is ambiguous
- The command is from an unapproved sender in future integration
- The command is an exact duplicate already processed
- The source campaign is `INVALID`
- The source campaign lacks a valid zone or stop loss
- Requested total lots exceed 2.00
- Instrument is not XAUUSD

Do not invent missing TP values.

If the source campaign is waiting for TP, the child campaign must also reflect missing TP and begin in:

```text
WAITING_FOR_TP
```

---

# MESSAGE-TO-CAMPAIGN MATCHING

Implement deterministic matching for follow-up commands.

Matching priority:

```text
1. Direct quoted-message match
2. Exact original signal message match
3. Latest compatible active campaign
4. No match
```

## Direct quoted-message match

When:

```text
is_reply = true
quoted_message_id is present
```

Find the raw message with the quoted WhatsApp message ID.

Then find:

```text
raw message
→ parsed signal
→ signal record
→ campaign
```

This must override latest-campaign matching.

## Latest compatible campaign

Use only when there is no quoted message.

Candidate states:

```text
WAITING_FOR_TP
AWAITING_CONFIRMATION
PLANNED
PENDING
PARTIALLY_FILLED
OPEN
MANAGING
```

Prompt 5 will normally only produce the first three, but the matcher must remain compatible with later states.

Exclude:

```text
INVALID
CLOSED
CANCELLED
REJECTED
FAILED
```

Compatibility rules:

- TP update → prefer `WAITING_FOR_TP`
- SL update → latest active campaign
- Close request → latest active campaign
- Cancel signal → latest non-terminal campaign
- Zone valid → latest non-terminal campaign
- Re-entry → latest compatible source campaign

If multiple equally valid campaigns exist and no deterministic winner exists:

```text
MATCH_AMBIGUOUS
```

Do not attach the command automatically.

Require confirmation or explicit reply.

---

# CAMPAIGN MATCH RESULT

Use a typed result:

```text
MATCHED_BY_QUOTE
MATCHED_BY_SIGNAL_MESSAGE
MATCHED_LATEST_COMPATIBLE
MATCH_AMBIGUOUS
NO_MATCH
```

Return:

```text
campaign_id
campaign_code
match_type
candidate_count
reason
```

Persist the match decision in audit metadata.

---

# FOLLOW-UP COMMAND ATTACHMENT

For parsed follow-up commands:

1. Persist the raw message if not already stored.
2. Persist the parsed message.
3. Run campaign matching.
4. If matched:
   - Create a campaign command record.
   - Link the raw message.
   - Link the campaign.
   - Preserve command type.
   - Preserve extracted value.
   - Preserve execution eligibility.
   - Preserve confirmation requirement.
5. If no match:
   - Do not invent a campaign.
   - Persist a no-match audit event.
   - Keep the parsed command retrievable.
6. If ambiguous match:
   - Do not attach automatically.
   - Persist candidate metadata.
   - Require later confirmation.

Do not execute any command.

---

# DELAYED TP UPDATES

When a matched campaign in `WAITING_FOR_TP` receives:

```text
TP 3960
```

Rules:

- Attach the command.
- If `TP1` is missing, fill `TP1`.
- Else if `TP2` is missing, fill `TP2`.
- Else:
  - Do not overwrite existing TP values.
  - Persist a warning or ambiguous update result.

When explicit:

```text
TP1 3960
```

- Fill or update TP1 only.

When explicit:

```text
TP2 3950
```

- Fill or update TP2 only.

Do not update both slots from one single-value command.

When both TP1 and TP2 become available:

```text
WAITING_FOR_TP → AWAITING_CONFIRMATION
```

in confirmation mode.

In automatic mode:

- Do not execute.
- Move only to the safe state defined by the approved transition design.
- Trading remains disabled.

Do not calculate position TP allocation.

---

# STOP-LOSS COMMANDS

For a matched:

```text
MODIFY_STOP_LOSS
```

Prompt 5 must:

- Attach the command.
- Validate that a decimal value exists.
- Store the requested new SL as command data.
- Update campaign requested stop-loss metadata only if the architecture explicitly treats campaign SL as the current requested SL.
- Preserve previous SL in audit details.
- Create no MT5 modification.
- Create no execution attempt.
- Create no position update.

If updating the campaign stop loss, use optimistic concurrency and audit the old and new values.

Do not validate broker stop levels.

Do not validate current market price.

---

# CLOSE AND CANCEL COMMANDS

## Explicit close

For matched:

```text
CLOSE_CAMPAIGN
```

Prompt 5 must not close MT5 positions.

Instead:

- Attach the command.
- Record close request.
- If the campaign has no possible MT5 exposure because execution is not implemented:
  - Transition to `CANCELLED` or `CLOSED` only according to the documented state semantics.
- Prefer:
  - `CANCELLED` for pre-execution campaigns
  - `CLOSING` only in future execution phases
- Do not mark a campaign with possible later external exposure as closed without reconciliation.

Because Prompt 5 has no execution, campaigns created by this app have no positions.

For Prompt 5-created campaigns:

```text
WAITING_FOR_TP → CANCELLED
AWAITING_CONFIRMATION → CANCELLED
PLANNED → CANCELLED
```

Use reason:

```text
ADMIN_CLOSE_REQUESTED
```

## Explicit cancel

For:

```text
CANCEL_SIGNAL
```

Use:

```text
ADMIN_CANCELLED
```

Transition eligible pre-execution campaigns to:

```text
CANCELLED
```

Do not delete records.

## Skip this for now

Still unresolved.

The parser classifies it as ambiguous.

Do not cancel or pause automatically.

---

# ZONE VALID

For matched:

```text
ZONE_VALID
```

Prompt 5 must:

- Attach the command.
- Record an audit event.
- Keep the campaign in its current valid non-terminal state.
- Use an idempotent self-transition only if the state machine and audit model require it.
- Do not reactivate a cancelled campaign.
- Do not place orders.
- Do not resolve the open decision about reactivation.

---

# AMBIGUOUS COMMANDS

For:

```text
Secure Profits
Exit this trade on your comfort
Hold it
Skip this for now
```

Prompt 5 must:

- Persist the parsed message.
- Attempt campaign matching only for context.
- Store candidate campaign reference if unambiguous.
- Create a confirmation request record if appropriate.
- Never transition the campaign automatically.
- Never update SL, TP, or status automatically.
- Never execute.
- Preserve:

```text
requires_confirmation = true
is_executable = false
```

---

# INFORMATIONAL MESSAGES

Informational messages must:

- Persist normally
- Optionally attach contextual campaign metadata only if safely matched
- Never create a campaign command with executable meaning
- Never transition a campaign
- Never update SL or TP
- Never trigger confirmation unless explicitly configured later

---

# USER CONFIRMATION LIFECYCLE

Implement safe confirmation operations for campaigns.

Supported actions:

```text
EXECUTE_CAMPAIGN
REJECT_CAMPAIGN
AMBIGUOUS_COMMAND
CLOSE_CAMPAIGN
```

Prompt 5 must support:

## Approve campaign

Endpoint or service action:

```text
AWAITING_CONFIRMATION → PLANNED
```

Requirements:

- Explicit user action
- Persist user confirmation
- Persist transition
- Use optimistic concurrency
- No entry calculation
- No MT5 execution
- Trading remains disabled

## Reject campaign

```text
AWAITING_CONFIRMATION → REJECTED
```

Requirements:

- Explicit user action
- Persist decision
- Persist reason
- No hard deletion

## Approve ambiguous command

Prompt 5 may persist the approval decision but must not execute the command unless its deterministic action is already defined and safe within Prompt 5.

For unresolved commands:

- Persist approval metadata
- Keep the campaign unchanged
- Mark command as awaiting a later implementation decision if necessary

Do not invent an execution effect.

---

# OPTIMISTIC CONCURRENCY

Use the existing campaign `version` field.

Requirements:

- Increment version on each campaign mutation.
- Update using:

```text
WHERE id = ? AND version = expected_version
```

- If no row is updated:
  - Raise typed concurrency error.
  - Roll back the Unit of Work.
  - Return HTTP 409 where exposed through API.
- Do not silently overwrite concurrent changes.
- Add tests with two sessions or two simulated updates.

Do not rely only on in-memory locks.

---

# TRANSACTION BOUNDARIES

Use the existing Unit of Work.

The following must be atomic:

## New signal campaign creation

```text
raw message
parsed message
signal
exact duplicate key
semantic duplicate key
campaign
initial transitions
audit events
```

## Follow-up command processing

```text
raw message
parsed message
campaign match decision
campaign command
campaign mutation if applicable
transition
audit event
```

## Re-entry creation

```text
re-entry command
source campaign match
duplicate decision
new campaign
parent linkage
transition
duplicate key
audit event
```

On failure:

- Roll back all changes.
- Do not leave partial campaign state.
- Persist application error only through a safe separate failure path if possible.

---

# DATABASE CHANGES

Inspect the existing schema before changing it.

Create a new Alembic revision only when required.

Suggested revision:

```text
002_campaign_lifecycle_and_duplicates
```

Possible schema additions or repairs:

- Unique relation preventing multiple campaigns for one signal unless explicit re-entry design requires otherwise
- Parser-version-aware uniqueness for parsed messages
- Semantic duplicate expiry index
- Campaign command match metadata
- Campaign current SL update tracking
- Campaign close-request metadata
- Confirmation state metadata
- Optimistic locking support
- Campaign-code generation support
- Additional audit indexes

Do not destructively rename existing tables without migration support.

Preserve existing data.

Run upgrade, downgrade, and re-upgrade tests.

---

# DOMAIN CONTRACTS

Update Python and TypeScript/Zod contracts for:

```text
CampaignCreationRequest
CampaignCreationResult
CampaignSummary
CampaignDetail
CampaignTransitionRequest
CampaignTransitionResult
CampaignMatchResult
DuplicateDecision
DuplicateRecord
SemanticSignalFingerprint
CampaignCommandAttachment
CampaignApprovalRequest
CampaignRejectionRequest
ConfirmationResult
ReentryRequest
ReentryResult
ConcurrencyConflict
```

Financial values remain decimal strings on the wire.

Use stable uppercase enum values.

Add:

```text
state_machine_version = "1.0.0"
duplicate_strategy_version = "1.0.0"
```

---

# CAMPAIGN API

Add safe APIs.

## Read APIs

```text
GET /api/v1/campaigns
GET /api/v1/campaigns/{campaign_id}
GET /api/v1/campaigns/{campaign_id}/transitions
GET /api/v1/campaigns/{campaign_id}/commands
GET /api/v1/campaigns/{campaign_id}/duplicate-records
GET /api/v1/campaigns/state-machine
GET /api/v1/campaigns/state-machine/version
GET /api/v1/duplicates/version
```

Support filters:

```text
state
instrument
created_from
created_to
campaign_code
parent_campaign_id
```

## Campaign creation from stored message

Add:

```text
POST /api/v1/campaigns/from-message/{raw_message_id}
```

Requirements:

- Create from persisted parsed signal only.
- Idempotent.
- Exact duplicate safe.
- Semantic duplicate safe.
- Never execute.
- Return existing campaign when exact duplicate.
- Return conflict or typed duplicate result when semantic duplicate.

## Confirmation APIs

```text
POST /api/v1/campaigns/{campaign_id}/approve
POST /api/v1/campaigns/{campaign_id}/reject
```

Approve:

```text
AWAITING_CONFIRMATION → PLANNED
```

Reject:

```text
AWAITING_CONFIRMATION → REJECTED
```

No order placement.

## Command processing

Add:

```text
POST /api/v1/campaigns/process-message/{raw_message_id}
```

Requirements:

- Process a stored parsed follow-up command.
- Match campaign.
- Attach command.
- Apply only Prompt 5-safe mutations.
- Never execute MT5 operations.
- Idempotent.

## Re-entry

Add:

```text
POST /api/v1/campaigns/process-reentry/{raw_message_id}
```

or implement through the generic process-message endpoint.

Requirements:

- Explicit parsed re-entry command only.
- Matched source campaign required.
- Idempotent.
- New child campaign.
- No entry planning.
- No execution.

Do not add order or position endpoints.

---

# API RESPONSE SAFETY

Every campaign mutation response must include:

```text
campaign_id
campaign_code
previous_state
current_state
campaign_version
duplicate_decision
transition_id
trading_enabled
execution_performed
```

For Prompt 5:

```text
trading_enabled = false
execution_performed = false
```

Never claim a trade was executed.

---

# EXACT DUPLICATE API BEHAVIOUR

Repeated identical requests must be idempotent.

Recommended HTTP behaviour:

```text
First successful creation: 201
Exact repeat: 200 with existing resource
Semantic duplicate blocked: 409
Concurrency conflict: 409
Invalid state transition: 409
Invalid input: 422
Not found: 404
```

Document actual behaviour consistently.

---

# TEST FIXTURES

Expand fixtures with campaign scenarios:

```text
packages/parser-fixtures/fixtures/campaigns/
├── complete-signal/
├── incomplete-signal/
├── exact-duplicates/
├── semantic-duplicates/
├── replies/
├── delayed-tp/
├── reentry/
├── cancel/
├── close/
├── zone-valid/
├── ambiguous/
└── concurrency/
```

Include:

1. Complete signal creates one campaign.
2. Same message ID submitted twice creates one campaign.
3. Copied signal with new message ID within 24 hours is blocked.
4. Same copied signal after window expiry is allowed.
5. Explicit re-entry creates one child campaign.
6. Duplicate re-entry command creates one child only.
7. Reply TP attaches to quoted campaign.
8. Non-reply TP attaches to latest compatible `WAITING_FOR_TP` campaign.
9. Ambiguous match attaches to none.
10. Close command cancels pre-execution campaign.
11. `Skip this for now` does not cancel.
12. `Zone Valid` does not create duplicate campaign.
13. Approve moves campaign to `PLANNED`.
14. Reject moves campaign to `REJECTED`.
15. Invalid transition is rejected.
16. Concurrency conflict returns typed error.

---

# REQUIRED TESTS

Use temporary SQLite databases.

## State machine tests

Test every allowed transition.

Test every forbidden transition.

Test terminal-state protection.

Test idempotent self-transition behaviour.

Test transition audit persistence.

Test reason-code enforcement.

## Campaign factory tests

Test:

- Complete signal → `AWAITING_CONFIRMATION`
- Missing TP → `WAITING_FOR_TP`
- XAUUSD only
- Entry count from settings
- Per-entry lot from settings
- Requested total lots exact Decimal
- Requested total lots above 2.00 rejected
- Campaign code uniqueness
- Trading remains disabled

## Exact duplicate tests

Test:

- Same group + same message ID
- Same request after service restart
- Same request through API twice
- One raw message
- One parsed message where parser-version rules apply
- One signal
- One campaign
- One exact duplicate key
- Existing campaign returned

## Semantic duplicate tests

Test:

- Same signal with different capitalization
- Same signal with extra whitespace
- Same signal with Unicode dash
- Same decimals with different formatting
- New message ID
- Same group and sender
- Within 24 hours
- Blocked as semantic duplicate

Test non-duplicates:

- Different direction
- Different zone
- Different SL
- Different TP
- Different group
- Different sender
- Outside duplicate window

## Re-entry tests

Test:

- Explicit re-entry creates child
- Parent campaign linked
- Reentry sequence increments
- New campaign code
- Same safe settings loaded
- Missing TP preserved
- Duplicate re-entry command idempotent
- Invalid source blocked
- No entry rows created
- No MT5 rows created

## Campaign matching tests

Test:

- Quoted reply wins over latest campaign
- TP command prefers `WAITING_FOR_TP`
- Latest compatible campaign selected deterministically
- Terminal campaigns excluded
- Multiple equal candidates produce ambiguity
- No candidate produces no match
- Reply to unknown message produces no match

## Delayed TP tests

Test:

- First unspecified TP fills TP1
- Second unspecified TP fills TP2
- Explicit TP1 updates TP1 only
- Explicit TP2 updates TP2 only
- Third unspecified TP does not overwrite
- Complete TP set moves to `AWAITING_CONFIRMATION`
- No planned entries created

## Command tests

Test:

- SL command attaches and stores requested SL
- Close cancels pre-execution campaign
- Cancel cancels pre-execution campaign
- Zone valid preserves state
- Ambiguous command creates no transition
- Informational message creates no transition
- Command duplicate does not process twice

## Confirmation tests

Test:

- Approve valid state
- Reject valid state
- Approve wrong state rejected
- Reject terminal state rejected
- Confirmation record created
- Transition record created
- No planned entries created
- No execution performed

## Optimistic concurrency tests

Test:

- Version increments
- Stale version fails
- HTTP 409
- Transaction rollback
- No lost update

## API tests

Test all endpoints.

Verify:

- Correct HTTP codes
- Stable response contracts
- Idempotency
- Pagination
- Filtering
- 404 handling
- 409 duplicate handling
- 409 concurrency handling
- 422 validation handling
- `execution_performed = false`

## Cross-language contract tests

Validate all new JSON fixtures with:

- Python Pydantic
- TypeScript Zod

---

# PERFORMANCE AND STRESS TESTS

Add lightweight local tests.

## Duplicate fingerprint benchmark

Generate at least 10,000 semantic fingerprints.

Report:

- Median
- p95
- Total duration

No network calls.

## Campaign matching benchmark

Create a temporary database with at least 1,000 campaigns.

Benchmark:

- Quoted-message match
- Latest-compatible match
- Semantic duplicate lookup

Confirm required indexes are used where practical.

Do not create unrealistic hard failures for slow development hardware.

Document results.

---

# INDEXES

Ensure indexes support:

```text
campaigns.state
campaigns.created_at
campaigns.parent_campaign_id
campaigns.campaign_code
campaigns.signal_id
campaign_state_transitions.campaign_id
campaign_commands.campaign_id
campaign_commands.raw_message_id
duplicate_keys.duplicate_type
duplicate_keys.duplicate_key
duplicate_keys.expires_at
raw messages by group and WhatsApp message ID
signals.raw_message_id
```

Use query plans or SQLite inspection where practical.

---

# LOGGING AND AUDIT

Structured logs must include:

```text
service
event
campaign_id
campaign_code
raw_message_id
correlation_id
previous_state
current_state
duplicate_decision
match_type
duration_ms
```

Do not log:

- API tokens
- WhatsApp secrets
- MT5 credentials
- Cookies
- Passwords

Audit events should include:

```text
CAMPAIGN_CREATED
CAMPAIGN_TRANSITIONED
CAMPAIGN_APPROVED
CAMPAIGN_REJECTED
CAMPAIGN_CANCELLED
COMMAND_ATTACHED
COMMAND_MATCH_FAILED
COMMAND_MATCH_AMBIGUOUS
EXACT_DUPLICATE_DETECTED
SEMANTIC_DUPLICATE_DETECTED
EXPLICIT_REENTRY_CREATED
CONCURRENCY_CONFLICT
```

---

# DOCUMENTATION

Create or update:

```text
docs/CAMPAIGN_IMPLEMENTATION.md
docs/CAMPAIGN_STATE_MACHINE.md
docs/DUPLICATE_PROTECTION.md
docs/CAMPAIGN_MATCHING.md
docs/REENTRY.md
docs/CONFIRMATION_WORKFLOW.md
docs/CAMPAIGN_API.md
docs/PHASE_5_REPORT.md
docs/ACCEPTANCE_CRITERIA.md
docs/DATA_MODEL.md
docs/REPOSITORY_STRUCTURE.md
README.md
```

## CAMPAIGN_IMPLEMENTATION.md

Include:

- Campaign creation
- Initial state selection
- Settings snapshot
- Transaction boundaries
- Optimistic concurrency
- No-execution guarantee

## CAMPAIGN_STATE_MACHINE.md

Include:

- State definitions
- Allowed transition matrix
- Forbidden transitions
- Terminal states
- Reason codes
- Trigger types
- Prompt 5 limitations

## DUPLICATE_PROTECTION.md

Include:

- Exact duplicate key
- Semantic fingerprint
- Canonical JSON rules
- SHA-256 strategy
- 24-hour default window
- Explicit re-entry exception
- Idempotency behaviour

## CAMPAIGN_MATCHING.md

Include:

- Quote-first matching
- Latest-compatible rules
- Command compatibility
- Ambiguous-match behaviour
- No-match behaviour

## REENTRY.md

Include:

- Parent linkage
- Reentry sequence
- Copied data
- Current settings snapshot
- Idempotency
- Safety blocks

## CONFIRMATION_WORKFLOW.md

Include:

- Approve
- Reject
- Ambiguous command confirmation
- No execution in Prompt 5

## CAMPAIGN_API.md

Document all endpoints and response codes.

## PHASE_5_REPORT.md

Include:

- Files created
- Files modified
- Migration revision
- State machine version
- Duplicate strategy version
- Allowed transitions
- Duplicate behaviours
- Matching behaviours
- Fixture count
- Test count
- Benchmark results
- API endpoints
- Known limitations
- Confirmation that no entry planning or execution exists

Update README:

```text
Prompt 5 of 12 completed
Next: Prompt 6 — Entry Ladder, TP Allocation and Risk Engine
```

---

# ROOT SCRIPTS

Add or update:

```text
campaign:test
campaign:contracts
campaign:benchmark
campaign:migrations
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

## Campaign-specific

```powershell
pnpm campaign:test
pnpm campaign:contracts
pnpm campaign:benchmark
pnpm campaign:migrations
```

Use equivalent commands if required by the existing repository style.

## Alembic

Run against a disposable database:

```powershell
alembic upgrade head
alembic current
alembic downgrade -1
alembic upgrade head
```

Also test full migration from base to head.

## FastAPI

Start the service and verify:

```text
GET /health
GET /ready
GET /version
GET /api/v1/campaigns
GET /api/v1/campaigns/{campaign_id}
GET /api/v1/campaigns/{campaign_id}/transitions
GET /api/v1/campaigns/{campaign_id}/commands
GET /api/v1/campaigns/{campaign_id}/duplicate-records
GET /api/v1/campaigns/state-machine
GET /api/v1/campaigns/state-machine/version
GET /api/v1/duplicates/version
POST /api/v1/campaigns/from-message/{raw_message_id}
POST /api/v1/campaigns/{campaign_id}/approve
POST /api/v1/campaigns/{campaign_id}/reject
POST /api/v1/campaigns/process-message/{raw_message_id}
```

Verify re-entry through the selected API design.

Then stop the service cleanly.

## Database safety verification

After all tests verify:

- Campaigns created only from valid signals
- No planned entries created
- No pending orders created
- No positions created
- No MT5 execution attempts created
- Exact duplicate creates no second campaign
- Semantic duplicate creates no second campaign
- Explicit re-entry creates exactly one child campaign
- Transition history is append-only
- Audit history is append-only

## Source security scan

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

No active MT5, WhatsApp, LLM, or trading execution code may exist.

## Git

Run:

```powershell
git status --short
```

If all checks pass, a local commit is allowed:

```powershell
git add .
git commit -m "feat: complete Prompt 5 - Campaign State Machine and Duplicate Protection"
```

Do not push.

---

# FAILURE HANDLING

Do not mark Prompt 5 complete because files were generated.

When a check fails:

1. Read the complete error.
2. Fix the project-controlled root cause.
3. Rerun the targeted check.
4. Do not weaken state validation.
5. Do not allow forbidden transitions.
6. Do not remove duplicate constraints.
7. Do not replace database-backed idempotency with memory-only logic.
8. Do not treat semantic duplicates as explicit re-entry.
9. Do not auto-attach ambiguous commands.
10. Do not create fake campaign matches.
11. Do not bypass optimistic concurrency.
12. Do not create entry rows.
13. Do not create MT5 rows.
14. Do not falsely report a check as passed.
15. Report genuine external blockers honestly.

---

# COMPLETION REQUIREMENTS

Prompt 5 is complete only when:

- Campaign creation from valid signals works.
- Incomplete signals create `WAITING_FOR_TP` campaigns.
- Complete signals create `AWAITING_CONFIRMATION` campaigns.
- State transition validation works.
- Forbidden transitions are rejected.
- Terminal states are protected.
- Transition records are append-only.
- Exact duplicate protection works across restarts.
- Semantic duplicate protection works.
- Semantic fingerprints are deterministic.
- Duplicate time window works.
- Explicit re-entry creates one linked child campaign.
- Duplicate re-entry commands are idempotent.
- Quote-first campaign matching works.
- Latest-compatible matching works.
- Ambiguous matching produces no automatic attachment.
- Delayed TP updates work.
- Confirmation approval moves to `PLANNED`.
- Rejection moves to `REJECTED`.
- Optimistic concurrency works.
- Campaign APIs work.
- Python and TypeScript contracts agree.
- All project-controlled checks pass.
- Trading remains disabled.
- No entry ladder is calculated.
- No planned entries are created.
- No MT5 integration exists.
- No WhatsApp integration exists.
- No LLM integration exists.
- No live credentials exist.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 5 OF 12 COMPLETED

Project root:
- ...

Versions:
- State machine version:
- Duplicate strategy version:
- Parser version:
- Contract version:

Campaign creation:
- Complete signal initial state:
- Incomplete signal initial state:
- Campaign code strategy:
- Settings snapshot:
- Requested total lots:
- Trading enabled:

State machine:
- Allowed transitions implemented:
- Forbidden transitions enforced:
- Terminal states:
- Transition persistence:
- Optimistic concurrency:

Duplicate protection:
- Exact duplicate key:
- Semantic fingerprint:
- Hash algorithm:
- Duplicate window:
- Exact duplicate behaviour:
- Semantic duplicate behaviour:
- Explicit re-entry exception:

Campaign matching:
- Quote-first matching:
- Latest-compatible matching:
- Ambiguous-match handling:
- No-match handling:

Re-entry:
- Parent linkage:
- Reentry sequence:
- Idempotency:
- Child campaigns created in tests:
- Entry rows created:
- MT5 records created:

Commands:
- Delayed TP:
- Stop-loss requests:
- Close requests:
- Cancel requests:
- Zone valid:
- Ambiguous commands:
- Informational messages:

Confirmation:
- Approve:
- Reject:
- Planned entries created:
- Execution performed:

API:
- Campaign list/detail:
- Transition history:
- Command history:
- Duplicate history:
- Campaign creation:
- Approve:
- Reject:
- Process message:
- Re-entry:

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
- Campaign contract tests:
- Duplicate fingerprint benchmark:
- Campaign matching benchmark:
- FastAPI campaign endpoints:
- Database safety verification:
- Security source scan:

Safety verification:
- Trading enabled: false
- Entry ladder logic: absent
- Planned entries created by campaign approval: false
- MT5 integration: absent
- WhatsApp integration: absent
- LLM integration: absent
- Live credentials: absent
- Ambiguous commands executable: false

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 6 OF 12 — ENTRY LADDER, TP ALLOCATION AND RISK ENGINE
```

Stop after Prompt 5.
