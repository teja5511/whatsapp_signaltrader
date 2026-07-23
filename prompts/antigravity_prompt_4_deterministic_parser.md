# PROMPT 4 OF 12 — DETERMINISTIC SIGNAL AND COMMAND PARSER
# 8 PROMPTS REMAIN AFTER THIS PHASE

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the current repository, preserve all valid Phase 1–3 work, implement Prompt 4 completely, run all applicable validations, fix all project-controlled failures, and stop after Prompt 4.

Do not explain the plan before starting.  
Do not ask questions unless implementation is blocked by a genuinely unresolved trading rule.  
Do not connect to WhatsApp.  
Do not connect to MT5.  
Do not implement order execution.  
Do not implement campaign transition rules.  
Do not resolve unresolved trading decisions.  
Do not add an LLM or AI parser.  
Do not push to GitHub.  
Do not create a remote.

---

# CURRENT VERIFIED PROJECT STATE

Phases 1–3 are complete.

Current project root:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Current architecture:

```text
apps/
├── desktop/
├── whatsapp-worker/
└── trading-service/

packages/
├── shared-contracts/
├── ui/
└── parser-fixtures/
```

Current persistence foundation:

- SQLite
- SQLAlchemy 2.x
- Alembic revision `001_initial_schema`
- Pydantic contracts
- TypeScript/Zod contracts
- Unit of Work
- Repositories
- Trading disabled
- MT5 integration absent
- WhatsApp integration absent

Do not rewrite or replace working Phase 1–3 foundations without a documented technical reason.

---

# PHASE OBJECTIVE

Implement a deterministic, testable, auditable parser for XAUUSD WhatsApp messages.

The parser must classify and extract structured data from:

1. New trading signals
2. Delayed take-profit updates
3. Stop-loss modification commands
4. Explicit close and exit commands
5. Cancel and skip commands
6. Zone-valid messages
7. Explicit re-entry commands
8. Informational-only messages
9. Ambiguous messages
10. Invalid and unsupported messages

This phase must implement parsing only.

Do not:

- Place orders
- Modify orders
- Close positions
- Calculate entry ladders
- Allocate TP positions
- Transition campaign states
- Generate semantic duplicate keys
- Connect OpenWA
- Connect MetaTrader 5
- Make autonomous trading decisions

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
docs/DOMAIN_CONTRACTS.md
docs/DATABASE_IMPLEMENTATION.md
docs/CONTRACT_VERSIONING.md
docs/PHASE_3_REPORT.md
```

Confirmed rules:

```text
Instrument: XAUUSD only
Direction: BUY or SELL
Entry count: configurable elsewhere, not parsed from these signals
Lot size: configured elsewhere, not parsed from these signals
Maximum total lots: enforced later, not by the parser
TP Open: metadata only in version 1
Trading enabled: false
Automation: paused
Execution mode: confirmation
```

Do not resolve any item in `docs/OPEN_DECISIONS.md`.

---

# PARSER DESIGN RULES

The parser must be:

- Deterministic
- Rule-based
- Stateless at the pure parsing layer
- Case-insensitive
- Whitespace-tolerant
- Unicode-hyphen tolerant
- Decimal-safe
- Auditable
- Versioned
- Reproducible
- Free of hidden network calls
- Free of AI or LLM dependencies

The same input and parser version must always produce the same result.

Use:

```text
parser_version = "1.0.0"
contract_version = "1.0.0"
```

The parser must not infer unsupported facts.

The parser may extract only what is explicitly present in the message or safely determined from deterministic syntax.

---

# REQUIRED PARSER PIPELINE

Implement a clear pipeline:

```text
Raw message
    ↓
Input validation
    ↓
Text normalization
    ↓
Line segmentation
    ↓
Candidate classification
    ↓
Field extraction
    ↓
Deterministic validation
    ↓
Structured parse result
    ↓
Persistence-ready DTO
```

Separate:

1. Text normalization
2. Classification
3. Extraction
4. Validation
5. Result construction

Do not create one large monolithic regex.

---

# PYTHON PACKAGE STRUCTURE

Implement inside the trading service with a structure similar to:

```text
apps/trading-service/src/trading_service/
├── parser/
│   ├── __init__.py
│   ├── constants.py
│   ├── normalization.py
│   ├── line_parser.py
│   ├── classification.py
│   ├── signal_parser.py
│   ├── command_parser.py
│   ├── validation.py
│   ├── result.py
│   ├── service.py
│   └── patterns/
│       ├── instrument.py
│       ├── direction.py
│       ├── zone.py
│       ├── stop_loss.py
│       ├── take_profit.py
│       └── commands.py
└── tests/
    └── parser/
```

Use the existing project style where it differs, but preserve clear module boundaries.

---

# TYPESCRIPT CONTRACT UPDATES

Update:

```text
packages/shared-contracts
```

Add or extend parser-related Zod contracts for:

```text
ParserInput
TextNormalizationResult
ParsedSignalPayload
ParsedCommandPayload
ParsedInformationalPayload
ParsedAmbiguousPayload
ParserValidationIssue
ParserResult
```

Do not duplicate incompatible contract definitions.

Python and TypeScript wire formats must remain consistent.

---

# INPUT CONTRACT

Create a parser input contract similar to:

```json
{
  "contract_version": "1.0.0",
  "parser_version": "1.0.0",
  "message_id": "wamid-example",
  "group_id": "group-example",
  "sender_id": "admin-example",
  "text": "Gold Sell\n4120-4128\n\nsl - 4136\n\ntp - 4112\ntp - 4104\ntp - Open",
  "message_timestamp": "2026-07-23T10:00:00Z",
  "quoted_message_id": null,
  "is_reply": false
}
```

Requirements:

- `text` must be a string.
- Empty or whitespace-only messages must be classified as invalid.
- Message metadata must pass through unchanged.
- The parser must never modify IDs.
- Timestamps must remain UTC-aware.
- No WhatsApp authentication data may enter the parser contract.

---

# TEXT NORMALIZATION

Implement deterministic normalization.

Normalize:

- Windows line endings
- Unix line endings
- Repeated blank lines
- Repeated internal spaces
- Leading and trailing spaces
- Tabs
- Non-breaking spaces
- Unicode dash variants
- Unicode minus variants
- Curly apostrophes
- Common full-width punctuation where safe
- Case for matching while preserving original text separately

Supported dash normalization should include at least:

```text
-
–
—
−
‐
‑
```

Normalize them to:

```text
-
```

Preserve:

```text
original_text
normalized_text
normalized_lines
```

Do not remove decimal points.

Do not rewrite numeric values.

Do not spell-correct trading values.

Do not translate messages.

---

# SUPPORTED INSTRUMENT TERMS

Recognize these as XAUUSD:

```text
Gold
GOLD
XAUUSD
XAU/USD
XAU USD
```

Normalize to:

```text
XAUUSD
```

Reject unsupported explicit instruments such as:

```text
BTCUSD
EURUSD
US30
NAS100
GBPUSD
Silver
XAGUSD
```

When no instrument is present:

- A standalone command may still be valid.
- A new signal must not be accepted unless XAUUSD or Gold is explicitly identified.
- Do not assume an instrument for a new signal.

---

# SUPPORTED DIRECTION TERMS

Recognize:

```text
Buy
Gold Buy
XAUUSD Buy
Buy Limit
Gold Buy Limit
XAUUSD Buy Limit

Sell
Gold Sell
XAUUSD Sell
Sell Limit
Gold Sell Limit
XAUUSD Sell Limit
```

Normalize direction to:

```text
BUY
SELL
```

Normalize order intent to:

```text
LIMIT
UNSPECIFIED
```

Rules:

- Explicit `Buy Limit` or `Sell Limit` → `LIMIT`
- Plain `Gold Buy` or `Gold Sell` → `UNSPECIFIED`
- Do not infer a market order
- Do not convert `UNSPECIFIED` to `LIMIT` during parsing
- Later phases may decide execution behaviour

---

# NUMBER EXTRACTION

Use `Decimal`, never float.

Support numeric forms such as:

```text
3990
3990.0
3990.00
4,120
4120.50
```

For thousands separators:

- Accept a comma only when it is clearly a thousands separator.
- Normalize `4,120` to `4120`.
- Reject ambiguous malformed forms such as `4,12,0`.
- Do not treat comma as a decimal separator in version 1.

Reject:

```text
NaN
Infinity
-Infinity
scientific notation unless explicitly approved
```

Store financial values as decimal strings in wire output.

---

# ZONE EXTRACTION

Support entry zones such as:

```text
4120-4128
4120 - 4128
4120–4128
3990 to 3998
3990 TO 3998
Zone 3990-3998
Entry 3990-3998
Entry Zone: 3990 - 3998
```

Normalize to:

```json
{
  "zone_low": "3990.00000000",
  "zone_high": "3998.00000000"
}
```

Rules:

- If the first value is higher than the second, sort them numerically into low and high.
- Preserve the original order in optional parser metadata for audit.
- Emit a non-fatal warning when values were reversed.
- Require exactly one valid zone for a normal signal.
- Multiple conflicting zones must produce an ambiguous or invalid result.
- A single price is not a zone.
- Do not create a synthetic range.

---

# STOP-LOSS EXTRACTION

Support:

```text
SL 4136
SL - 4136
SL: 4136
Sl - 4008
sl 4136
Stop Loss 4136
Stoploss 4136
Hard SL 4013
Move SL to 4138
Move stop loss to 4074
```

Normalize the numeric value to a decimal string.

Distinguish:

- New signal SL field
- Follow-up SL modification command
- Hard SL wording as metadata

For a new signal:

```json
{
  "stop_loss": "4136.00000000"
}
```

For a command:

```json
{
  "command_type": "MODIFY_STOP_LOSS",
  "value": "4138.00000000",
  "value_kind": "PRICE"
}
```

Do not determine whether the SL is directionally safe in this phase.

Do not execute the modification.

---

# TAKE-PROFIT EXTRACTION

Support:

```text
TP 4112
TP - 4112
TP: 4112
Tp 4112
Take Profit 4112
Takeprofit 4112
TP1 4112
TP 1 4112
TP2 4104
TP 2 4104
TP Open
TP - Open
```

For a full signal:

- Preserve TP order as written.
- Extract at most two numeric signal TPs for version 1.
- First numeric TP → `tp1`
- Second numeric TP → `tp2`
- `TP Open` → `tp_open_present = true`
- Additional numeric TPs beyond two must produce a warning and remain in parser metadata.
- Do not silently discard extra TP text.
- Do not create an unmanaged runner.

Example:

```text
tp - 4112
tp - 4104
tp - Open
```

Output:

```json
{
  "tp1": "4112.00000000",
  "tp2": "4104.00000000",
  "tp_open_present": true
}
```

For a standalone TP update:

```text
TP 3960
```

Classify as:

```text
FOLLOW_UP_COMMAND
```

Command type:

```text
ADD_TAKE_PROFIT
```

Do not decide whether it is TP1 or TP2 when the message does not explicitly say.

Use:

```text
target_tp_slot = UNSPECIFIED
```

When explicit:

```text
TP1 3960
```

Use:

```text
target_tp_slot = TP1
```

When explicit:

```text
TP2 3950
```

Use:

```text
target_tp_slot = TP2
```

Campaign matching is implemented later.

---

# NEW SIGNAL CLASSIFICATION

A message is a `NEW_SIGNAL` candidate when it contains:

- Explicit XAUUSD/Gold instrument
- Explicit BUY or SELL direction
- One valid price zone

Stop loss may be:

- Present
- Missing

Take profits may be:

- Present
- Partially present
- Missing
- Include `TP Open`

New signal result fields:

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
missing_fields
warnings
source_lines
```

Validation severity:

## Valid complete signal

Contains:

- Instrument
- Direction
- Zone
- Stop loss
- At least TP1 and TP2, or the documented accepted Phase 1 form

Do not require `TP Open`.

## Valid incomplete signal

Contains:

- Instrument
- Direction
- Zone
- Stop loss
- Missing one or both numeric TPs

Classification remains:

```text
NEW_SIGNAL
```

Set:

```text
completeness = INCOMPLETE
```

Include:

```text
missing_fields = ["tp1", "tp2"]
```

This supports delayed TP messages.

## Invalid signal

Examples:

- Missing direction
- Missing zone
- Conflicting directions
- Multiple conflicting zones
- Unsupported explicit instrument
- No meaningful signal syntax

Do not treat invalid messages as executable.

---

# FOLLOW-UP COMMAND CLASSIFICATION

Implement deterministic command types.

## MODIFY_STOP_LOSS

Examples:

```text
Move SL to 4138 for added safety.
SL 4138
Hard SL 4013.
Market is very shaky move SL to 4074 for safety.
Move stop loss to 4074.
```

Output:

```text
category = FOLLOW_UP_COMMAND
command_type = MODIFY_STOP_LOSS
classification = EXPLICIT
execution_eligibility = ELIGIBLE_AFTER_CAMPAIGN_MATCH
requires_confirmation = false
```

Extract:

```text
value
value_kind = PRICE
hard_stop = true or false
```

The surrounding commentary must not prevent extraction of an explicit SL command.

## CLOSE_CAMPAIGN

Examples:

```text
Close trade
Close this trade
Close the trade
Close all positions for this signal
Exit trade
Exit this trade
```

Output:

```text
category = FOLLOW_UP_COMMAND
command_type = CLOSE_CAMPAIGN
classification = EXPLICIT
execution_eligibility = ELIGIBLE_AFTER_CAMPAIGN_MATCH
```

Do not classify:

```text
Exit this trade on your comfort
```

as an explicit automatic close.

That message is ambiguous.

## CANCEL_SIGNAL

Examples:

```text
Cancel signal
Delete pending orders
Cancel pending orders
Skip this for now
```

Rules:

- `Cancel signal` → explicit `CANCEL_SIGNAL`
- `Delete pending orders` → explicit `CANCEL_SIGNAL` with scope metadata `PENDING_ONLY`
- `Skip this for now` → ambiguous because final behaviour is unresolved

Do not assign final execution semantics to `Skip this for now`.

## ZONE_VALID

Examples:

```text
Zone Valid
Zone is valid
Same zone valid
```

Output:

```text
category = FOLLOW_UP_COMMAND
command_type = ZONE_VALID
classification = EXPLICIT
execution_eligibility = ELIGIBLE_AFTER_CAMPAIGN_MATCH
```

Do not implement reactivation behaviour.

## REENTRY

Examples:

```text
Same Zone for Re-entry
Same zone reentry
Re-enter same zone
Re entry same zone
```

Output:

```text
category = FOLLOW_UP_COMMAND
command_type = REENTRY
classification = EXPLICIT
execution_eligibility = ELIGIBLE_AFTER_CAMPAIGN_MATCH
```

Do not create a campaign in this phase.

## ADD_TAKE_PROFIT

Examples:

```text
TP 3960
TP1 3960
TP2 3950
Take Profit 3960
```

Output:

```text
category = FOLLOW_UP_COMMAND
command_type = ADD_TAKE_PROFIT
classification = EXPLICIT
execution_eligibility = ELIGIBLE_AFTER_CAMPAIGN_MATCH
```

Extract target slot when explicit.

---

# INFORMATIONAL-ONLY CLASSIFICATION

Classify these as informational unless an explicit executable command is also present:

```text
We barely survived the SL.
Wait for update.
100 Pips Almost.
50+ Pips.
It will come to Zone again.
Just touched our SL and reversed.
Market is very shaky.
```

Output:

```text
category = INFORMATIONAL
is_executable = false
execution_eligibility = NEVER
```

For mixed messages:

```text
Market is very shaky move SL to 4074 for safety.
```

The explicit numeric SL command takes precedence.

Output:

```text
category = FOLLOW_UP_COMMAND
command_type = MODIFY_STOP_LOSS
```

Preserve commentary as metadata.

---

# AMBIGUOUS CLASSIFICATION

Classify these as ambiguous:

```text
Secure Profits.
Exit this trade on your comfort.
Hold it.
Skip this for now.
Just touched our SL and reversed, if you haven't closed like mine, Hold it.
```

Output:

```text
category = AMBIGUOUS
is_executable = false
execution_eligibility = REQUIRES_CONFIRMATION
requires_confirmation = true
```

Possible command hints may be included:

```text
SECURE_PROFITS
CLOSE_CAMPAIGN
HOLD
CANCEL_SIGNAL
```

But no automatic action may be selected.

Do not resolve the meaning of these messages.

---

# CONFLICT RESOLUTION PRIORITY

Use deterministic priority when one message matches multiple patterns.

Recommended priority:

```text
1. Unsupported explicit instrument
2. Full new signal
3. Explicit close/exit command
4. Explicit stop-loss modification
5. Explicit take-profit update
6. Explicit re-entry
7. Explicit zone-valid
8. Explicit cancel command
9. Ambiguous command
10. Informational message
11. Invalid/unsupported
```

Important:

- A complete new signal containing `SL` and `TP` lines must remain a new signal, not multiple commands.
- An explicit numeric command embedded in commentary must be classified as a command.
- Ambiguous wording must never override an explicit numeric command.
- Unsupported instrument must not be converted into XAUUSD.
- Conflicting directions must produce an invalid result.

Document the final precedence table.

---

# RESULT CONTRACT

Return one structured result.

Example new signal:

```json
{
  "contract_version": "1.0.0",
  "parser_version": "1.0.0",
  "category": "NEW_SIGNAL",
  "is_executable": false,
  "requires_confirmation": true,
  "original_text": "Gold Sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104\ntp - Open",
  "normalized_text": "gold sell\n4120-4128\nsl - 4136\ntp - 4112\ntp - 4104\ntp - open",
  "signal": {
    "instrument": "XAUUSD",
    "direction": "SELL",
    "order_intent": "UNSPECIFIED",
    "zone_low": "4120.00000000",
    "zone_high": "4128.00000000",
    "stop_loss": "4136.00000000",
    "tp1": "4112.00000000",
    "tp2": "4104.00000000",
    "tp_open_present": true,
    "completeness": "COMPLETE"
  },
  "command": null,
  "informational": null,
  "ambiguous": null,
  "validation_issues": [],
  "warnings": [],
  "source_metadata": {
    "message_id": "example",
    "group_id": "group",
    "sender_id": "admin",
    "quoted_message_id": null,
    "is_reply": false
  }
}
```

In Prompt 4:

```text
is_executable = false
```

for all results because execution is not implemented.

Use a separate field for future eligibility:

```text
execution_eligibility
```

Possible values:

```text
NEVER
REQUIRES_CONFIRMATION
ELIGIBLE_AFTER_CAMPAIGN_MATCH
ELIGIBLE_AFTER_VALIDATION
```

Do not imply that parsing alone authorizes execution.

---

# VALIDATION ISSUES

Use structured validation issues:

```json
{
  "code": "SIGNAL_DIRECTION_MISSING",
  "severity": "ERROR",
  "field": "direction",
  "message": "A new signal requires an explicit BUY or SELL direction.",
  "source_line": 1
}
```

Severity values:

```text
INFO
WARNING
ERROR
```

Required issue codes should include at least:

```text
EMPTY_MESSAGE
UNSUPPORTED_INSTRUMENT
INSTRUMENT_MISSING
DIRECTION_MISSING
DIRECTION_CONFLICT
ZONE_MISSING
ZONE_INVALID
ZONE_MULTIPLE_CONFLICT
ZONE_VALUES_REVERSED
STOP_LOSS_MISSING
TP1_MISSING
TP2_MISSING
TOO_MANY_TAKE_PROFITS
INVALID_DECIMAL
AMBIGUOUS_COMMAND
UNSUPPORTED_MESSAGE
MULTIPLE_EXPLICIT_COMMANDS
```

Do not use free-form strings only.

---

# MULTIPLE COMMANDS IN ONE MESSAGE

If one follow-up message contains multiple compatible explicit instructions, parse them into an ordered command list only if the existing contracts can support it safely.

Example:

```text
Move SL to 4074 and TP1 3960
```

Preferred result:

```text
category = FOLLOW_UP_COMMAND
commands = [
  MODIFY_STOP_LOSS,
  ADD_TAKE_PROFIT
]
```

If the current contract permits only one command:

- Extend it to support `commands[]`.
- Preserve deterministic order.
- Reject conflicting commands.

Example conflict:

```text
Close trade but hold it
```

Output:

```text
category = AMBIGUOUS
requires_confirmation = true
```

Do not automatically close.

---

# MESSAGE REPLY METADATA

The parser must preserve:

```text
quoted_message_id
is_reply
```

It must not perform campaign lookup.

Add parser hints:

```text
campaign_match_strategy_hint
```

Possible values:

```text
QUOTED_MESSAGE
LATEST_COMPATIBLE
NONE
```

Rules:

- `is_reply = true` and quoted ID present → `QUOTED_MESSAGE`
- Standalone follow-up command without reply → `LATEST_COMPATIBLE`
- New signal or informational message → `NONE`

Actual matching belongs to Prompt 5.

---

# PERSISTENCE INTEGRATION

Integrate parsing with the existing persistence layer without implementing campaign logic.

Implement an application service similar to:

```text
MessageParsingService
```

Responsibilities:

1. Accept a validated parser input.
2. Persist or retrieve the raw WhatsApp message.
3. Run the deterministic parser.
4. Persist the parsed result in `parsed_messages`.
5. Persist a `signals` row only for valid or incomplete `NEW_SIGNAL` results.
6. Persist a `campaign_commands` or existing command-equivalent row only for parsed follow-up commands when the current schema permits safe association.
7. If a campaign ID is required by the existing command table and no campaign is matched yet:
   - Do not invent a campaign.
   - Persist the parsed command payload in `parsed_messages`.
   - Leave campaign command creation for Prompt 5.
8. Record a parser audit event.
9. Return the parser result.

Do not transition campaigns.

Do not generate entry ladders.

Do not execute trades.

Use the existing Unit of Work for atomic persistence.

---

# RAW MESSAGE IDEMPOTENCY

Exact duplicate execution logic belongs to Prompt 5, but parsing persistence must safely handle repeated raw message submissions.

For the existing composite uniqueness rule:

```text
group_id + whatsapp_message_id
```

Implement one of these deterministic behaviours:

```text
A. Return the previously stored parse result
B. Return a duplicate-status response containing the existing parse result
```

Do not create a second raw-message row.

Do not create a second parsed-message row unless parser reprocessing is explicitly versioned.

If parser version changes later, reprocessing may create a new parsed result linked to the same raw message if the schema supports it.

Document the selected behaviour.

---

# SAFE PARSER API

Add development-safe endpoints:

```text
POST /api/v1/parser/preview
POST /api/v1/parser/messages
GET /api/v1/parser/messages/{raw_message_id}
GET /api/v1/parser/version
```

## POST /api/v1/parser/preview

Requirements:

- Parse without persistence.
- Never create signals or campaigns.
- Never trigger trading.
- Return structured parser result.
- Useful for fixtures and dashboard preview.

## POST /api/v1/parser/messages

Requirements:

- Persist the raw message and parse result.
- Preserve idempotency.
- Persist a signal record only when applicable.
- Never create MT5 orders.
- Never transition a campaign.
- Return HTTP 200 or 201 based on documented idempotent behaviour.

## GET /api/v1/parser/messages/{raw_message_id}

Requirements:

- Return stored raw and parsed result.
- Return 404 when absent.
- Never expose secrets.

## GET /api/v1/parser/version

Return:

```json
{
  "parser_version": "1.0.0",
  "contract_version": "1.0.0",
  "deterministic": true,
  "ai_enabled": false,
  "trading_enabled": false
}
```

Do not add execution endpoints.

---

# PARSER FIXTURES

Expand:

```text
packages/parser-fixtures
```

Use structured JSON fixtures.

Required categories:

```text
fixtures/
├── new-signals/
├── delayed-tp/
├── stop-loss-commands/
├── close-commands/
├── cancel-commands/
├── zone-valid/
├── reentry/
├── informational/
├── ambiguous/
├── unsupported/
└── invalid/
```

Each fixture should contain:

```json
{
  "name": "gold-sell-full-signal",
  "source": "user-provided",
  "input": {
    "text": "Gold Sell\n4120-4128\n\nsl - 4136\n\ntp - 4112\ntp - 4104\ntp - Open"
  },
  "expected": {
    "category": "NEW_SIGNAL",
    "instrument": "XAUUSD",
    "direction": "SELL"
  }
}
```

Include all original user messages.

Add additional variants for:

- Uppercase
- Lowercase
- Extra spaces
- Tabs
- Unicode dashes
- Blank lines
- `XAU/USD`
- `Gold Buy`
- `Gold Sell Limit`
- Reversed zone order
- Thousands separators
- Missing SL
- Missing TP1
- Missing TP2
- Unsupported instrument
- Conflicting buy and sell
- Multiple zones
- Mixed commentary and explicit SL
- Explicit close
- Ambiguous close
- Reply metadata
- Empty message

---

# REQUIRED TESTS

Use parameterized tests.

## Normalization tests

Test:

- CRLF and LF normalization
- Multiple blank lines
- Tabs
- Non-breaking spaces
- Unicode dash normalization
- Curly apostrophes
- Case-insensitive matching
- Original text preservation

## Signal parser tests

Test at least:

```text
Gold Sell
4120-4128
SL - 4136
TP - 4112
TP - 4104
TP - Open
```

Expected:

```text
NEW_SIGNAL
XAUUSD
SELL
UNSPECIFIED
zone_low = 4120
zone_high = 4128
SL = 4136
TP1 = 4112
TP2 = 4104
TP Open = true
```

Test:

```text
Gold Sell Limit
3990-3998
SL - 4008
```

Expected:

```text
NEW_SIGNAL
XAUUSD
SELL
LIMIT
INCOMPLETE
tp1 missing
tp2 missing
```

Test BUY variants.

Test reversed zones.

Test unsupported instruments.

Test missing instrument.

Test direction conflicts.

Test multiple conflicting zones.

## Command parser tests

Test:

```text
Move SL to 4138 for added safety.
```

Expected:

```text
FOLLOW_UP_COMMAND
MODIFY_STOP_LOSS
4138
```

Test:

```text
Market is very shaky move SL to 4074 for safety.
```

Expected:

```text
FOLLOW_UP_COMMAND
MODIFY_STOP_LOSS
4074
```

Test:

```text
Hard SL 4013.
```

Expected:

```text
FOLLOW_UP_COMMAND
MODIFY_STOP_LOSS
hard_stop = true
```

Test:

```text
TP 3960
```

Expected:

```text
FOLLOW_UP_COMMAND
ADD_TAKE_PROFIT
target slot unspecified
```

Test:

```text
Same Zone for Re-entry
```

Expected:

```text
FOLLOW_UP_COMMAND
REENTRY
```

Test:

```text
Zone Valid
```

Expected:

```text
FOLLOW_UP_COMMAND
ZONE_VALID
```

Test explicit close messages.

## Informational tests

Test:

```text
We barely survived the SL.
Wait for update.
100 Pips Almost.
50+ Pips.
It will come to Zone again.
```

Expected:

```text
INFORMATIONAL
is_executable = false
```

## Ambiguous tests

Test:

```text
Secure Profits.
Exit this trade on your comfort.
Hold it.
Skip this for now.
Just touched our SL and reversed, if you haven't closed like mine, Hold it.
```

Expected:

```text
AMBIGUOUS
requires_confirmation = true
is_executable = false
```

## Persistence tests

Test:

- Raw message persisted once.
- Parsed message persisted.
- Valid complete signal creates signal record.
- Valid incomplete signal creates signal record with nullable TP fields.
- Informational message does not create signal.
- Ambiguous message does not create signal.
- Duplicate raw message does not create duplicate rows.
- Parser audit event created.
- Unit of Work rolls back when persistence fails.

## API tests

Test:

```text
POST /api/v1/parser/preview
POST /api/v1/parser/messages
GET /api/v1/parser/messages/{id}
GET /api/v1/parser/version
```

Verify:

- Trading remains disabled.
- No campaign created.
- No planned entries created.
- No MT5 order created.
- No position created.
- Duplicate POST is idempotent.
- Invalid payload returns structured validation errors.

## Cross-language contract tests

Every parser fixture must validate through:

- Python Pydantic contracts
- TypeScript Zod contracts

Ensure financial values remain decimal strings.

---

# PERFORMANCE TEST

Add a lightweight local benchmark for pure parsing.

Requirements:

- Parse at least 1,000 fixture messages.
- Report median and p95 parser time.
- No network calls.
- No database writes in the pure parser benchmark.
- Do not impose an unrealistic hard failure threshold on slow development hardware.
- Document the result.
- Target sub-millisecond or low-millisecond pure parsing where practical.
- Preserve the existing internal processing objective without claiming external WhatsApp or broker latency.

---

# LOGGING AND AUDIT

Structured parser logs should include:

```text
service
parser_version
event
category
message_id
group_id
sender_id
correlation_id
duration_ms
validation_issue_count
```

Do not log:

- API tokens
- WhatsApp session secrets
- Cookies
- MT5 credentials
- Authentication payloads

The parser may log normalized message text in development only if the project’s logging policy permits it.

In production-style configuration, raw message logging should be redactable.

---

# DOCUMENTATION

Create or update:

```text
docs/PARSER_ARCHITECTURE.md
docs/PARSER_RULES.md
docs/PARSER_CLASSIFICATION.md
docs/PARSER_FIXTURES.md
docs/PARSER_API.md
docs/PARSER_VERSIONING.md
docs/PHASE_4_REPORT.md
docs/COMMAND_CLASSIFICATION.md
docs/ACCEPTANCE_CRITERIA.md
docs/REPOSITORY_STRUCTURE.md
README.md
```

## PARSER_ARCHITECTURE.md

Include:

- Pipeline
- Module boundaries
- Deterministic guarantees
- Input/output contracts
- Persistence integration
- Failure handling
- No-AI guarantee

## PARSER_RULES.md

Include:

- Normalization rules
- Instrument recognition
- Direction recognition
- Zone extraction
- SL extraction
- TP extraction
- Missing-field rules
- Decimal handling
- Conflict handling

## PARSER_CLASSIFICATION.md

Include complete precedence and classification tables.

## PARSER_FIXTURES.md

Document all fixture categories and how to add regression cases.

## PARSER_API.md

Document safe parser endpoints.

## PARSER_VERSIONING.md

Define:

```text
parser_version = "1.0.0"
```

Document:

- Patch version for non-behavioural fixes
- Minor version for backward-compatible recognition additions
- Major version for breaking classification or wire-format changes

## PHASE_4_REPORT.md

Include:

- Files created
- Files changed
- Parser version
- Supported signal forms
- Supported commands
- Ambiguous classifications
- Fixture count
- Test count
- Test results
- Benchmark result
- API endpoints
- Known limitations
- Confirmation that no trading, WhatsApp or MT5 integration exists

Update README:

```text
Prompt 4 of 12 completed
Next: Prompt 5 — Campaign State Machine and Duplicate Protection
```

---

# ROOT SCRIPTS

Add or update scripts:

```text
parser:test
parser:fixtures
parser:contracts
parser:benchmark
```

Ensure the existing root commands still work:

```text
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

Add appropriate Python commands to project scripts where useful.

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

Use the project environment:

```powershell
ruff check .
ruff format --check .
mypy apps/trading-service/src
pytest
```

## Parser-specific

Run:

```powershell
pnpm parser:test
pnpm parser:contracts
pnpm parser:benchmark
```

Use equivalent commands if script names need to match the existing project style.

## FastAPI

Start the trading service and verify:

```text
GET /health
GET /ready
GET /version
GET /api/v1/parser/version
POST /api/v1/parser/preview
POST /api/v1/parser/messages
GET /api/v1/parser/messages/{raw_message_id}
```

Then stop the service cleanly.

## Database safety

After API parser tests, verify:

- Raw messages exist where expected.
- Parsed messages exist where expected.
- Signal rows exist only for signal results.
- Campaign count is unchanged.
- Planned-entry count is unchanged.
- Pending-order count is unchanged.
- Position count is unchanged.

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
live account password
OpenAI
Anthropic
Gemini
langchain
```

Documentation matches are allowed.

No active MT5, WhatsApp, LLM or trading execution code may exist.

## Git

Run:

```powershell
git status --short
```

Do not push or create a remote.

Do not commit unless explicitly requested.

---

# FAILURE HANDLING

Do not mark Prompt 4 complete because files were generated.

When a check fails:

1. Read the complete error.
2. Fix the project-controlled root cause.
3. Rerun the targeted check.
4. Do not weaken strict typing.
5. Do not remove failing fixtures.
6. Do not change expected classifications merely to make tests pass.
7. Do not convert Decimal values to floats.
8. Do not classify ambiguous messages as executable.
9. Do not hide unsupported instruments.
10. Do not falsely report a check as passed.
11. Report genuine external blockers honestly.

---

# COMPLETION REQUIREMENTS

Prompt 4 is complete only when:

- Deterministic normalization works.
- Full XAUUSD signals parse correctly.
- Incomplete signals parse correctly.
- Delayed TP updates parse correctly.
- Explicit SL modifications parse correctly.
- Explicit close commands parse correctly.
- Re-entry messages parse correctly.
- Zone-valid messages parse correctly.
- Informational messages remain non-executable.
- Ambiguous messages remain non-executable and confirmation-required.
- Unsupported instruments are rejected.
- Decimal values remain exact.
- Reply metadata is preserved.
- Parser results persist safely.
- Duplicate raw submissions are idempotent.
- Parser preview API works.
- Parser persistence API works.
- Python and TypeScript contracts agree.
- All fixtures pass.
- All project-controlled validation passes.
- Trading remains disabled.
- Campaign transition logic remains absent.
- Entry ladder logic remains absent.
- MT5 integration remains absent.
- WhatsApp integration remains absent.
- LLM integration remains absent.
- No live credentials exist.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 4 OF 12 COMPLETED

Project root:
- ...

Parser:
- Parser version:
- Contract version:
- Deterministic:
- AI/LLM enabled:
- Supported instrument:
- Supported directions:
- Supported signal formats:
- Supported explicit commands:
- Informational classifications:
- Ambiguous classifications:

Normalization:
- Unicode dashes:
- Whitespace:
- Line endings:
- Decimal handling:
- Original text preservation:

Persistence:
- Raw message persistence:
- Parsed message persistence:
- Signal persistence:
- Duplicate submission behaviour:
- Audit event persistence:
- Campaign transitions created:
- Planned entries created:
- MT5 records created:

API:
- GET /api/v1/parser/version:
- POST /api/v1/parser/preview:
- POST /api/v1/parser/messages:
- GET /api/v1/parser/messages/{id}:

Fixtures:
- Total fixtures:
- New signal fixtures:
- Command fixtures:
- Informational fixtures:
- Ambiguous fixtures:
- Invalid/unsupported fixtures:

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
- Parser contract tests:
- Parser benchmark:
- FastAPI parser endpoints:
- Database safety verification:
- Security source scan:

Safety verification:
- Trading enabled: false
- Campaign execution: absent
- Entry ladder logic: absent
- MT5 integration: absent
- WhatsApp integration: absent
- LLM integration: absent
- Live credentials: absent
- Ambiguous messages executable: false

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 5 OF 12 — CAMPAIGN STATE MACHINE AND DUPLICATE PROTECTION
```

Stop after Prompt 4.
