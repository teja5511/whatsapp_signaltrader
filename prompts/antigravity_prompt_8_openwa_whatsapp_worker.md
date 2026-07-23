# PROMPT 8 OF 12 — OPENWA WHATSAPP WORKER
# 4 PROMPTS REMAIN AFTER THIS PHASE

Continue working inside the existing project:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Inspect the repository, preserve all valid Phase 1–7 work, implement Prompt 8 completely, run every applicable validation, fix every project-controlled failure, and stop after Prompt 8.

Do not explain the plan before starting.  
Do not ask questions unless work is blocked by a genuinely unresolved requirement.  
Do not connect the worker directly to MT5.  
Do not allow WhatsApp messages to call MT5 APIs.  
Do not enable live-account execution.  
Do not automatically execute campaigns from WhatsApp in this phase.  
Do not add AI or LLM interpretation.  
Do not push to GitHub.  
Do not create a remote.

A clean local Git commit at the end is allowed only after all required checks pass.

---

# CURRENT VERIFIED PROJECT STATE

Phases 1–7 are complete.

Current verified capabilities include:

- Requirements and architecture documentation
- pnpm monorepo
- Tauri/React desktop scaffold
- Node.js/TypeScript WhatsApp worker scaffold
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
- Fake, dry-run, and real MT5 adapters
- Demo-only and hedging-only safety gates
- Durable single-writer MT5 execution queue
- Local API authentication
- Trading disabled by default
- Live execution impossible
- WhatsApp integration absent
- LLM integration absent

Do not rewrite working Phase 1–7 functionality without a documented technical reason.

---

# PHASE OBJECTIVE

Implement a reliable OpenWA-based WhatsApp worker for one WhatsApp account, one approved group, and one approved group administrator.

This phase must implement:

1. OpenWA dependency integration
2. WhatsApp session creation and restoration
3. QR login workflow
4. One-client process lock
5. Connection health and reconnect handling
6. Group discovery
7. Approved group selection
8. Approved admin selection and validation
9. Admin-role verification
10. Group-only filtering
11. Text-message extraction
12. Reply and quoted-message metadata
13. Message normalization envelope
14. Exact-message idempotency
15. Durable file-based delivery spool
16. Ordered delivery to the trading service
17. Retry and quarantine handling
18. Worker-local health and status API
19. Local authentication
20. Sanitized structured logging
21. Session logout and reset
22. Fake OpenWA adapter
23. Fixture-driven tests
24. Optional manually gated real WhatsApp smoke tests
25. Documentation, benchmarks, and CI updates

Do not implement:

- Direct MT5 calls
- Direct database access to the trading-service SQLite database
- Campaign execution from WhatsApp
- Automatic approval
- Automatic order placement
- Final FastAPI orchestration
- Final dashboard
- Multiple WhatsApp accounts
- Multiple approved groups
- Multiple approved admins
- WhatsApp Business Cloud API
- Telegram
- AI interpretation
- LLM classification

Prompt 9 will implement full FastAPI orchestration and real-time event distribution.

---

# SOURCE-OF-TRUTH DOCUMENTS

Read before implementation:

```text
README.md
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
docs/SECURITY_AND_SAFETY.md
docs/COMMAND_CLASSIFICATION.md
docs/PARSER_ARCHITECTURE.md
docs/PARSER_RULES.md
docs/PARSER_API.md
docs/CAMPAIGN_MATCHING.md
docs/DUPLICATE_PROTECTION.md
docs/MT5_ADAPTER.md
docs/MT5_DEMO_SAFETY.md
docs/MT5_API.md
docs/PHASE_7_REPORT.md
docs/OPEN_DECISIONS.md
```

Do not resolve any trading rule in `docs/OPEN_DECISIONS.md`.

---

# NON-NEGOTIABLE BOUNDARY

The WhatsApp worker is an ingestion adapter only.

Allowed flow:

```text
WhatsApp
    ↓
OpenWA Worker
    ↓
Authenticated local HTTP
    ↓
FastAPI parser ingestion
```

Forbidden flow:

```text
WhatsApp → MT5
WhatsApp Worker → MT5 adapter
WhatsApp Worker → execution queue
WhatsApp Worker → order placement
WhatsApp Worker → campaign approval
WhatsApp Worker → direct SQLite business database
```

The worker may submit a sanitized message envelope only.

The trading service remains the only owner of:

- Parsing
- Campaign matching
- Duplicate decisions
- Planning
- Execution authorization
- MT5 operations
- Business persistence

---

# OPENWA PACKAGE

Use the OpenWA library requested for this project.

Before installation:

1. Inspect the current Node.js version.
2. Inspect the current worker package.
3. Verify the currently maintained OpenWA package name and API from the official project repository and package metadata.
4. Pin a compatible version.
5. Record the selected package and version.
6. Do not install an unrelated WhatsApp automation library as a silent replacement.
7. If the current Node.js version is unsupported:
   - Use a project-local compatible Node version through the documented version manager.
   - Do not alter unrelated global installations.
8. Do not falsely report real OpenWA validation if Chromium or WhatsApp login is unavailable.

The likely package namespace may be:

```text
@open-wa/wa-automate
```

Verify before using it.

Create an adapter boundary so tests do not depend on Chromium or a real WhatsApp account.

---

# WORKER VERSIONING

Use:

```text
whatsapp_worker_version = "1.0.0"
whatsapp_ingestion_contract_version = "1.0.0"
openwa_adapter_version = "1.0.0"
```

Expose these through the worker status API.

---

# MODULE STRUCTURE

Use a clean structure similar to:

```text
apps/whatsapp-worker/
├── src/
│   ├── index.ts
│   ├── app.ts
│   ├── constants.ts
│   ├── errors.ts
│   ├── config/
│   │   ├── schema.ts
│   │   ├── loader.ts
│   │   └── paths.ts
│   ├── logging/
│   │   ├── logger.ts
│   │   └── redaction.ts
│   ├── openwa/
│   │   ├── adapter.ts
│   │   ├── real-adapter.ts
│   │   ├── fake-adapter.ts
│   │   ├── client-factory.ts
│   │   ├── session.ts
│   │   ├── qr.ts
│   │   ├── groups.ts
│   │   ├── admins.ts
│   │   ├── messages.ts
│   │   └── reconnect.ts
│   ├── ingestion/
│   │   ├── envelope.ts
│   │   ├── extractor.ts
│   │   ├── filters.ts
│   │   ├── idempotency.ts
│   │   ├── ordered-queue.ts
│   │   ├── spool.ts
│   │   ├── delivery.ts
│   │   ├── retry.ts
│   │   └── quarantine.ts
│   ├── api/
│   │   ├── server.ts
│   │   ├── auth.ts
│   │   ├── health.ts
│   │   ├── session.ts
│   │   ├── configuration.ts
│   │   ├── groups.ts
│   │   ├── messages.ts
│   │   └── events.ts
│   ├── state/
│   │   ├── worker-state.ts
│   │   └── event-bus.ts
│   └── contracts/
│       └── index.ts
├── tests/
├── data/
│   ├── sessions/
│   ├── spool/
│   ├── quarantine/
│   └── locks/
├── package.json
└── README.md
```

Keep OpenWA-specific objects inside the adapter boundary.

Do not expose raw OpenWA message objects to the trading service.

---

# WORKER MODES

Support:

```text
fake
real
```

Default:

```text
WHATSAPP_ADAPTER_MODE=fake
```

## Fake mode

- No Chromium
- No WhatsApp login
- Deterministic group, admin, and message fixtures
- Configurable disconnection and reconnect events
- Configurable duplicate messages
- Configurable reply messages
- Configurable ignored messages
- Used in CI and normal tests

## Real mode

- OpenWA and Chromium
- One WhatsApp account
- Local manual QR authentication
- One approved group
- One approved admin
- Explicit local opt-in
- Never enabled in CI

---

# ENVIRONMENT CONFIGURATION

Update `.env.example` with placeholders:

```text
WHATSAPP_ADAPTER_MODE=fake
WHATSAPP_WORKER_HOST=127.0.0.1
WHATSAPP_WORKER_PORT=8010
WHATSAPP_WORKER_ENABLED=false
WHATSAPP_REAL_CONNECTION_ENABLED=false

WHATSAPP_SESSION_NAME=xauusd-bot
WHATSAPP_SESSION_DIR=./data/sessions
WHATSAPP_SPOOL_DIR=./data/spool
WHATSAPP_QUARANTINE_DIR=./data/quarantine
WHATSAPP_LOCK_DIR=./data/locks

WHATSAPP_APPROVED_GROUP_ID=
WHATSAPP_APPROVED_ADMIN_ID=
WHATSAPP_REQUIRE_ADMIN_ROLE=true

WHATSAPP_DELIVERY_CONCURRENCY=1
WHATSAPP_DELIVERY_TIMEOUT_MS=10000
WHATSAPP_RETRY_INITIAL_MS=1000
WHATSAPP_RETRY_MAX_MS=60000
WHATSAPP_RETRY_MAX_ATTEMPTS=0
WHATSAPP_GROUP_METADATA_TTL_SECONDS=300

TRADING_SERVICE_URL=http://127.0.0.1:8000
LOCAL_API_TOKEN=replace-with-development-token

WHATSAPP_QR_EXPOSE_OVER_LOCAL_API=false
WHATSAPP_QR_TTL_SECONDS=60
WHATSAPP_RAW_TEXT_LOGGING=false
```

Rules:

- Never commit a real `.env`.
- Never commit group IDs or admin IDs by default.
- Never commit WhatsApp session files.
- Never commit Chromium profiles.
- Never commit QR images.
- Never commit cookies.
- Never commit local API tokens.

---

# FILE AND DIRECTORY HYGIENE

Ensure `.gitignore` covers:

```text
apps/whatsapp-worker/data/sessions/
apps/whatsapp-worker/data/spool/
apps/whatsapp-worker/data/quarantine/
apps/whatsapp-worker/data/locks/
**/.openwa/
**/sessionData/
**/chromium-data/
**/userDataDir/
**/qr*.png
**/qr*.txt
```

Do not ignore test fixtures.

Use restrictive local file permissions where supported.

---

# ONE-CLIENT PROCESS LOCK

Only one real OpenWA client may use the configured session.

Implement a lock file containing:

```text
worker_id
process_id
hostname
started_at
session_name
```

Requirements:

- Acquire before OpenWA initialization.
- Use atomic creation.
- Detect active lock owner.
- Refuse a second worker.
- Recover a stale lock only after verifying the process no longer exists.
- Release on graceful shutdown.
- Preserve a warning if abnormal termination leaves a stale lock.
- Fake mode may use isolated temporary locks in tests.

Error:

```text
WHATSAPP_SESSION_ALREADY_IN_USE
```

---

# SESSION MANAGEMENT

Implement:

```text
create session
restore session
validate session
logout session
reset session
```

Rules:

- Session data stays local.
- Session data is never sent to FastAPI.
- Session data is never logged.
- Session data is never included in API responses.
- Logout requires explicit authenticated request.
- Reset requires a stronger confirmation phrase.
- Reset deletes only the configured session directory.
- Do not delete unrelated Chromium profiles.

Required confirmation phrase:

```text
RESET WHATSAPP SESSION
```

---

# QR LOGIN WORKFLOW

Real mode must support manual QR login.

Requirements:

1. Start OpenWA.
2. Capture QR lifecycle events.
3. Display QR in the local terminal when supported.
4. Do not write the QR to disk by default.
5. Keep the latest QR only in memory.
6. Expire the QR after configured TTL.
7. Do not log the raw QR payload.
8. Do not expose QR through local API unless:

```text
WHATSAPP_QR_EXPOSE_OVER_LOCAL_API=true
```

9. QR API must require local authentication.
10. Clear QR after authentication or expiry.

Normalized QR states:

```text
NOT_REQUIRED
WAITING
AVAILABLE
EXPIRED
AUTHENTICATED
FAILED
```

---

# CONNECTION STATES

Use:

```text
DISABLED
STARTING
WAITING_FOR_QR
AUTHENTICATING
CONNECTED
READY
RECONNECTING
DEGRADED
LOGGED_OUT
BLOCKED_CONFIGURATION
ERROR
SHUTTING_DOWN
STOPPED
```

`READY` requires:

```text
OpenWA connected
session authenticated
approved group configured
approved admin configured
approved group found
approved admin found in group
admin role verified when required
trading service reachable or spool available
```

Do not report `READY` merely because Chromium started.

---

# RECONNECT HANDLING

Implement bounded reconnect orchestration.

Requirements:

- Detect disconnect events.
- Stop accepting new delivery work while connection is unavailable.
- Keep already spooled messages.
- Reconnect with exponential backoff and jitter.
- Cap the delay.
- Do not create multiple concurrent clients.
- Revalidate session after reconnect.
- Revalidate group and admin metadata.
- Resume ordered delivery after readiness.
- Emit state-change events.

Do not use infinite tight loops.

---

# GROUP DISCOVERY

After authentication, list groups through the adapter.

Normalize:

```text
group_id
display_name
participant_count
is_read_only
is_community
is_announcement
is_archived
```

Only ordinary supported WhatsApp groups are eligible in version 1.

Block or exclude:

- Direct chats
- Status chats
- Broadcast lists
- Unsupported channels
- Communities when the API cannot guarantee message semantics
- Announcement-only groups when sender/admin semantics cannot be validated

Do not automatically select a group by name.

---

# GROUP SELECTION

Support one approved group.

Selection methods:

```text
environment variable
authenticated local setup API
CLI setup command
```

CLI example:

```text
pnpm --filter whatsapp-worker setup
```

The setup flow must:

1. Require authenticated OpenWA session.
2. List eligible groups.
3. Require explicit selection.
4. Display group name and masked ID.
5. Save the selected group ID only to ignored local configuration.
6. Never commit the ID.
7. Revalidate the group on startup.

Do not support multiple active approved groups.

---

# ADMIN DISCOVERY

For the selected group:

1. Load participant metadata.
2. Identify current admins and super-admins using verified OpenWA fields.
3. Normalize:

```text
sender_id
display_name
is_admin
is_super_admin
is_group_member
```

4. Require explicit admin selection.
5. Store one approved admin ID locally.
6. Revalidate membership and role on startup and periodically.
7. If the approved admin loses admin status:

```text
BLOCKED_CONFIGURATION
```

when `WHATSAPP_REQUIRE_ADMIN_ROLE=true`.

Do not infer admin status from message behaviour.

---

# MESSAGE FILTERING

Process only messages satisfying every rule:

```text
message belongs to approved group
sender matches approved admin
sender is currently an admin when required
message is an incoming group message
message is not sent by the bot account itself
message has a supported text payload
message is not a status update
message is not a reaction-only event
message is not an edit event
message is not a deletion event
message is not a system notification
```

Rejected messages must be ignored safely and counted by reason.

Do not send ignored messages to the trading service.

---

# SUPPORTED MESSAGE TYPES

Version 1 supports:

```text
plain text
text caption attached to supported media when caption extraction is unambiguous
quoted/reply text metadata
```

Do not download media.

Do not process:

```text
images without text caption
videos without text caption
audio
voice notes
documents
stickers
locations
contacts
polls
reactions
payments
calls
deleted messages
edited messages
```

Record unsupported message types as sanitized local metrics only.

---

# MESSAGE ENVELOPE

Create a normalized ingestion contract.

Example:

```json
{
  "contract_version": "1.0.0",
  "worker_version": "1.0.0",
  "source": "WHATSAPP_OPENWA",
  "whatsapp_message_id": "wamid-example",
  "group_id": "group-example",
  "group_name": "Gold Signals",
  "sender_id": "admin-example",
  "sender_name": "Admin",
  "sender_is_admin": true,
  "message_type": "TEXT",
  "text": "Gold Sell\n4120-4128\nSL 4136",
  "message_timestamp": "2026-07-23T10:00:00Z",
  "received_at": "2026-07-23T10:00:01Z",
  "is_reply": false,
  "quoted_whatsapp_message_id": null,
  "quoted_sender_id": null,
  "correlation_id": "uuid",
  "worker_id": "uuid",
  "sanitized_metadata": {}
}
```

Requirements:

- Financial text remains unchanged.
- Do not lowercase or parse trading text in the worker.
- Preserve line breaks.
- Normalize line endings only.
- Preserve quoted-message ID.
- Preserve reply status.
- Convert timestamps to UTC ISO 8601.
- Use stable message IDs from OpenWA.
- Do not expose raw session or chat objects.
- Do not include cookies or authentication data.

---

# TEXT EXTRACTION

Extract text deterministically.

Priority:

```text
1. explicit text body
2. supported caption
3. unsupported
```

Rules:

- Preserve original visible text.
- Normalize CRLF to LF.
- Trim only outer whitespace.
- Do not collapse meaningful line breaks.
- Do not correct spelling.
- Do not parse numbers.
- Do not classify signals.
- Do not add instrument names.
- Do not translate text.

Maximum accepted text length:

```text
10000 characters
```

Oversized messages must be quarantined with:

```text
MESSAGE_TEXT_TOO_LARGE
```

Do not truncate trading text silently.

---

# REPLY METADATA

For reply messages preserve:

```text
is_reply = true
quoted_whatsapp_message_id
quoted_sender_id when safely available
```

Do not require quoted text content.

Do not perform campaign lookup.

The FastAPI service will use the quoted message ID for campaign matching.

If OpenWA cannot provide a quoted ID for a reply:

```text
quoted_whatsapp_message_id = null
reply_metadata_incomplete = true
```

Do not invent an ID.

---

# EXACT MESSAGE IDEMPOTENCY

Create a worker idempotency key:

```text
WHATSAPP:<group_id>:<whatsapp_message_id>
```

Use SHA-256 when stored in filenames or indexes.

Requirements:

- Same OpenWA event processed twice creates one spool item.
- Same message after reconnect creates one delivery.
- Same message after worker restart creates one delivery attempt sequence.
- Trading service remains the final database-backed authority.
- Worker idempotency is an additional safety layer.
- Do not use message text as the exact primary key.

---

# ORDERED DELIVERY

Messages from the approved group must be delivered in timestamp/event order.

Use:

```text
delivery concurrency = 1
```

Requirements:

- One ordered queue per approved group.
- Since only one group exists, one queue is sufficient.
- Preserve arrival order for equal timestamps using a monotonic local sequence.
- Do not deliver message N+1 before N reaches a final local delivery state.
- A permanently quarantined message may allow the queue to continue after audit.
- Do not block forever on one malformed message.

---

# DURABLE FILE-BASED SPOOL

The worker must not access the trading-service SQLite database.

Implement a local file spool.

Suggested structure:

```text
data/spool/
├── pending/
├── delivering/
├── delivered/
└── failed/
```

Use one JSON file per message envelope.

Filename:

```text
<sequence>-<sha256-idempotency-key>.json
```

Requirements:

- Atomic write to temporary file.
- Flush and rename.
- Atomic move between states.
- Validate JSON before delivery.
- Recover `delivering` files after crash.
- Never create duplicate pending files.
- Delivered files may be removed after configurable retention.
- Failed permanent items move to quarantine.
- Session files and spool files remain separate.

Do not use the Python business database.

---

# SPOOL RETENTION

Add settings:

```text
WHATSAPP_DELIVERED_RETENTION_HOURS=24
WHATSAPP_QUARANTINE_RETENTION_DAYS=30
WHATSAPP_SPOOL_MAX_ITEMS=10000
WHATSAPP_SPOOL_MAX_BYTES=104857600
```

When limits are exceeded:

```text
DEGRADED
```

Stop accepting new message envelopes before disk exhaustion.

Do not silently delete pending items.

---

# DELIVERY TO TRADING SERVICE

Use authenticated local HTTP.

Target endpoint:

```text
POST /api/v1/parser/messages
```

Map the worker envelope to the existing parser input contract without losing metadata.

Headers:

```text
Authorization: Bearer <LOCAL_API_TOKEN>
Content-Type: application/json
X-Worker-Id: <worker_id>
X-Correlation-Id: <correlation_id>
X-Idempotency-Key: <worker idempotency key>
```

Requirements:

- Bind service URL to localhost by default.
- Never log the bearer token.
- Use timeout and abort support.
- Validate the response using Zod.
- Treat parser `200` or `201` as delivered.
- Treat an exact duplicate `200` response as delivered.
- Do not call campaign approval or MT5 APIs.
- Do not call execution endpoints.

---

# DELIVERY RESULT CLASSIFICATION

Classify responses:

## Success

```text
200
201
```

Action:

```text
mark delivered
```

## Authentication failure

```text
401
403
```

Action:

```text
block delivery
set worker DEGRADED or BLOCKED_CONFIGURATION
do not retry rapidly
```

## Permanent payload failure

```text
400
404
409 when documented as permanent for this payload
422
```

Action:

```text
move to quarantine
record sanitized response
continue queue
```

Do not quarantine exact-duplicate success responses.

## Temporary failure

```text
408
425
429
500
502
503
504
network error
timeout
```

Action:

```text
retry with exponential backoff and jitter
```

Respect `Retry-After` when present.

---

# RETRY POLICY

Use exponential backoff:

```text
initial = 1000 ms
maximum = 60000 ms
jitter = enabled
```

`WHATSAPP_RETRY_MAX_ATTEMPTS=0` means unlimited temporary retries while the item remains safely spooled.

Requirements:

- Persist attempt count and next attempt time in spool metadata.
- Restart resumes retries.
- No busy loop.
- Permanent failures are not retried.
- Authentication failures pause the delivery queue.
- Manual retry endpoint may requeue quarantined items after correction.

---

# QUARANTINE

Quarantine reasons include:

```text
MESSAGE_TEXT_TOO_LARGE
UNSUPPORTED_MESSAGE_TYPE
INVALID_ENVELOPE
TRADING_SERVICE_VALIDATION_FAILED
TRADING_SERVICE_AUTH_FAILED
TRADING_SERVICE_PERMANENT_ERROR
APPROVED_GROUP_MISMATCH
APPROVED_ADMIN_MISMATCH
ADMIN_ROLE_INVALID
SPOOL_CORRUPTED
```

Store:

```text
envelope
reason code
sanitized error
attempt count
first seen
last attempted
```

Never store session secrets.

Provide authenticated local APIs to list and requeue safe quarantine items.

---

# WORKER LOCAL API

Bind to:

```text
127.0.0.1
```

Default port:

```text
8010
```

Create:

```text
GET /health
GET /ready
GET /version
GET /status
GET /metrics
GET /configuration
GET /session
GET /session/qr
GET /groups
GET /groups/{group_id}/admins
GET /spool
GET /spool/{item_id}
GET /quarantine
GET /quarantine/{item_id}

POST /start
POST /stop
POST /session/logout
POST /session/reset
POST /configuration/group
POST /configuration/admin
POST /spool/{item_id}/retry
POST /quarantine/{item_id}/requeue
```

Mutating endpoints require:

```text
Authorization: Bearer <LOCAL_API_TOKEN>
```

Read endpoints should also require authentication except `/health` and `/version`.

Do not expose session cookies, raw QR payload, or Chromium paths.

---

# HEALTH RESPONSE

Example:

```json
{
  "service": "whatsapp-worker",
  "status": "ok",
  "worker_version": "1.0.0",
  "adapter_mode": "fake",
  "connection_state": "READY",
  "session_authenticated": true,
  "approved_group_configured": true,
  "approved_admin_configured": true,
  "admin_role_verified": true,
  "trading_service_reachable": true,
  "spool_pending": 0,
  "spool_quarantined": 0,
  "whatsapp_integration_enabled": false
}
```

In fake mode:

```text
whatsapp_integration_enabled = false
```

In real connected mode:

```text
whatsapp_integration_enabled = true
```

Do not claim real connectivity in fake mode.

---

# READINESS

`/ready` returns ready only when:

- Worker enabled
- Adapter started
- Session authenticated in real mode
- Group configured
- Admin configured
- Group validated
- Admin validated
- Role validated when required
- Process lock owned
- Spool writable
- Delivery client configured
- Authentication token configured

Trading-service reachability may produce `DEGRADED` while the durable spool continues accepting within limits.

---

# LOCAL CONFIGURATION STORAGE

Store approved group/admin configuration in an ignored local JSON file or OS-safe local configuration.

Example:

```text
data/config/worker.local.json
```

Do not commit it.

Fields:

```text
approved_group_id
approved_group_display_name
approved_admin_id
approved_admin_display_name
selected_at
last_validated_at
```

Never store passwords or session cookies in this file.

Environment variables may override local configuration explicitly.

Document precedence.

---

# DOUBLE VALIDATION

Before accepting a message:

1. Validate group ID against worker configuration.
2. Validate sender ID.
3. Validate sender admin status from cached metadata.
4. Refresh metadata when cache expires.
5. If role status cannot be confirmed:
   - do not forward
   - set degraded or blocked state
   - record sanitized reason

Do not trust display names for identity.

---

# ADMIN METADATA CACHE

Use TTL:

```text
WHATSAPP_GROUP_METADATA_TTL_SECONDS=300
```

Requirements:

- Cache by group ID.
- Refresh after reconnect.
- Refresh when admin verification fails.
- Do not accept a message while using known-stale invalid metadata.
- Do not hammer WhatsApp metadata APIs.

---

# SELF-MESSAGE FILTER

Determine the authenticated account ID.

Ignore messages where:

```text
sender_id = authenticated account ID
from_me = true
```

Do not create feedback loops.

---

# MESSAGE EDITS AND DELETIONS

The user does not expect edits or deletions.

Version 1 behaviour:

```text
edited message event → ignore and audit locally
deleted message event → ignore and audit locally
```

Do not modify already delivered parser records.

Do not attempt to reverse trades.

Document this limitation.

---

# EVENT BUS

Create an internal typed event bus for future Prompt 9 integration.

Events:

```text
WORKER_STATE_CHANGED
QR_STATE_CHANGED
SESSION_AUTHENTICATED
SESSION_LOGGED_OUT
GROUP_CONFIGURED
ADMIN_CONFIGURED
ADMIN_ROLE_CHANGED
MESSAGE_ACCEPTED
MESSAGE_IGNORED
MESSAGE_SPOOLED
DELIVERY_STARTED
DELIVERY_SUCCEEDED
DELIVERY_RETRY_SCHEDULED
DELIVERY_QUARANTINED
TRADING_SERVICE_STATE_CHANGED
SPOOL_LIMIT_WARNING
```

Do not yet connect this event bus to the desktop.

Provide authenticated local Server-Sent Events or WebSocket only if implemented cleanly.

Preferred Prompt 8 endpoint:

```text
GET /events
```

using SSE with local authentication.

Prompt 9 will bridge worker events through FastAPI.

---

# STRUCTURED LOGGING

Use Pino.

Required fields:

```text
service
worker_version
adapter_mode
event
worker_id
connection_state
message_id
group_id_masked
sender_id_masked
correlation_id
spool_item_id
attempt_count
duration_ms
```

Redact:

```text
Authorization
LOCAL_API_TOKEN
session data
QR payload
cookies
Chromium profile
raw OpenWA authentication data
full account phone number
```

Raw message text logging:

```text
disabled by default
```

When enabled for development:

- Truncate safely for logs only.
- Never alter the delivered envelope.
- Clearly mark as sensitive development logging.

---

# METRICS

Expose local counters:

```text
messages_received_total
messages_accepted_total
messages_ignored_total
messages_ignored_group_total
messages_ignored_sender_total
messages_ignored_admin_role_total
messages_unsupported_total
messages_spooled_total
messages_delivered_total
messages_duplicate_total
messages_retry_total
messages_quarantined_total
openwa_disconnect_total
openwa_reconnect_total
spool_pending
spool_bytes
delivery_latency_ms
```

Do not expose message text in metrics.

---

# SHARED CONTRACTS

Update `packages/shared-contracts` with Zod and TypeScript contracts for:

```text
WhatsAppAdapterMode
WhatsAppConnectionState
WhatsAppQrState
WhatsAppSessionStatus
WhatsAppGroupSummary
WhatsAppAdminSummary
WhatsAppWorkerConfiguration
WhatsAppMessageType
WhatsAppMessageEnvelope
WhatsAppDeliveryStatus
WhatsAppSpoolItem
WhatsAppQuarantineItem
WhatsAppWorkerStatus
WhatsAppWorkerHealth
WhatsAppWorkerEvent
WhatsAppDeliveryResult
```

Add matching Python Pydantic ingestion contracts where needed.

All IDs remain strings.

Timestamps use UTC ISO 8601.

---

# FASTAPI INGESTION COMPATIBILITY

Inspect the existing:

```text
POST /api/v1/parser/messages
```

Ensure it can safely accept the worker envelope or a mapped parser input.

Do not redesign campaign orchestration.

Add only minimal compatibility fields when required:

```text
source
worker_id
sender_is_admin
group_name
sender_name
message_type
received_at
sanitized_metadata
```

The trading service must independently reject:

- Wrong group
- Wrong sender
- Unsupported source
- Missing required IDs

Add approved-group/admin validation at the service boundary if absent.

Do not trust worker validation alone.

Do not trigger MT5 execution.

---

# SERVICE-SIDE SOURCE VALIDATION

Add or confirm:

```text
approved_group_id
approved_admin_id
```

validation before parsing a real worker message.

Rules:

- Fake/test messages may use explicit test bypass only inside tests.
- Production/development real ingestion requires configured IDs.
- Wrong group returns `403`.
- Wrong sender returns `403`.
- Missing worker authentication returns `401`.
- Parser preview remains separate and must not impersonate real WhatsApp ingestion.
- All rejections are audited.

---

# FAKE OPENWA SCENARIOS

Implement deterministic scenarios:

```text
healthy_authenticated
waiting_for_qr
login_success
login_failure
logged_out
disconnect_and_reconnect
group_missing
group_ambiguous_name
admin_missing
admin_not_admin
admin_role_revoked
approved_text_message
wrong_group_message
wrong_sender_message
self_message
reply_message
caption_message
unsupported_media
duplicate_event
out_of_order_events
service_unavailable
service_auth_failure
service_validation_failure
spool_recovery_after_crash
quarantine_requeue
lock_already_held
stale_lock_recovery
```

Tests must assert exact behaviour.

---

# REAL WHATSAPP SMOKE TESTS

Real OpenWA tests must be manually gated.

Required environment:

```text
RUN_WHATSAPP_SMOKE_TESTS=true
WHATSAPP_ADAPTER_MODE=real
WHATSAPP_WORKER_ENABLED=true
WHATSAPP_REAL_CONNECTION_ENABLED=true
```

Smoke tests must:

1. Start one OpenWA client.
2. Authenticate through QR if required.
3. List groups.
4. Verify the selected group.
5. Verify the selected admin.
6. Read one explicitly designated test message.
7. Deliver it to a local test or development parser endpoint.
8. Confirm one parser record.
9. Confirm no campaign execution.
10. Confirm no MT5 execution.
11. Shut down cleanly.
12. Preserve session locally unless logout is explicitly requested.

Do not send messages to the WhatsApp group.

Do not post automated replies.

Do not create trades.

If not run, report:

```text
NOT RUN — manual WhatsApp opt-in required
```

Do not report it as passed.

---

# REQUIRED TESTS

Use fake OpenWA adapter by default.

## Configuration tests

Test:

- Valid fake configuration
- Missing token
- Missing group
- Missing admin
- Invalid port
- Invalid retry values
- Invalid spool limits
- Real mode disabled without explicit opt-in
- Session paths remain inside worker data directory

## Lock tests

Test:

- Acquire
- Release
- Second process blocked
- Stale lock recovered
- Active lock not removed
- Crash recovery metadata

## Session tests

Test:

- New session
- Restored session
- QR required
- Authenticated
- Logged out
- Reset confirmation
- Session secrets never returned

## Group/admin tests

Test:

- Eligible groups listed
- Group selected by ID
- No automatic selection by name
- Admin list
- Admin selected by ID
- Role verified
- Role revoked
- Missing admin blocks readiness
- Display-name collision does not affect identity

## Filter tests

Test:

- Approved group/admin accepted
- Wrong group ignored
- Wrong sender ignored
- Non-admin ignored
- Self message ignored
- Status ignored
- Reaction ignored
- Edit ignored
- Deletion ignored
- Unsupported media ignored
- Supported caption accepted

## Envelope tests

Test:

- IDs preserved
- Text preserved
- Line endings normalized
- UTC timestamps
- Reply ID preserved
- Incomplete reply metadata marked
- No session data
- No cookies
- Maximum text length
- Oversized message quarantined

## Spool tests

Test:

- Atomic creation
- Duplicate prevention
- Ordered sequence
- Pending to delivering
- Delivering to delivered
- Crash recovery
- Corrupted item quarantine
- Size limit degradation
- No pending-item deletion
- Retention cleanup

## Delivery tests

Test:

- `200` delivered
- `201` delivered
- Exact duplicate `200` delivered
- `401` pauses queue
- `403` pauses queue
- `422` quarantines
- `429` retries
- `500` retries
- Timeout retries
- `Retry-After`
- Exponential backoff
- Persistent attempt count
- Queue order maintained
- No campaign or MT5 endpoints called

## API tests

Test all worker endpoints.

Verify:

- Local bind
- Authentication
- QR exposure disabled by default
- QR TTL
- Session reset confirmation
- Configuration mutation
- Quarantine requeue
- SSE authentication
- No secrets in responses

## Service-side validation tests

Test:

- Correct group/admin accepted
- Wrong group rejected
- Wrong sender rejected
- Missing token rejected
- Parser preview unaffected
- No MT5 execution
- No automatic campaign approval

## Cross-language contracts

Validate all worker fixtures through:

- TypeScript Zod
- Python Pydantic where applicable

---

# PERFORMANCE TESTS

Add lightweight benchmarks.

## Envelope extraction

```text
100,000 message envelope extractions
```

## Filter pipeline

```text
100,000 group/admin/type filter evaluations
```

## Spool operations

```text
10,000 atomic spool writes and moves
```

using a disposable directory.

## Delivery queue

```text
10,000 fake successful deliveries
```

Report median, p95, and total duration.

No real WhatsApp calls.

---

# CI

Update CI to:

- Run fake OpenWA adapter tests
- Run worker contract tests
- Run spool tests
- Run delivery tests
- Build the worker
- Never start Chromium
- Never connect WhatsApp
- Never require QR login
- Never expose secrets
- Never run real smoke tests

---

# DOCUMENTATION

Create or update:

```text
docs/WHATSAPP_WORKER.md
docs/OPENWA_INTEGRATION.md
docs/WHATSAPP_SESSION.md
docs/WHATSAPP_GROUP_ADMIN_SETUP.md
docs/WHATSAPP_MESSAGE_ENVELOPE.md
docs/WHATSAPP_SPOOL_AND_RETRY.md
docs/WHATSAPP_WORKER_API.md
docs/WHATSAPP_SMOKE_TESTS.md
docs/PHASE_8_REPORT.md
docs/ARCHITECTURE.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/REPOSITORY_STRUCTURE.md
README.md
```

## WHATSAPP_WORKER.md

Include:

- Worker responsibilities
- Boundaries
- Modes
- Startup
- Shutdown
- Health states
- No-MT5 guarantee

## OPENWA_INTEGRATION.md

Include:

- Package and version
- Adapter boundary
- Chromium requirements
- Session lifecycle
- Reconnect behaviour

## WHATSAPP_SESSION.md

Include:

- QR login
- Local session storage
- Logout
- Reset
- Process lock
- Secret handling

## WHATSAPP_GROUP_ADMIN_SETUP.md

Include:

- Group discovery
- Explicit selection
- Admin discovery
- Role verification
- Configuration precedence

## WHATSAPP_MESSAGE_ENVELOPE.md

Include the full contract and field semantics.

## WHATSAPP_SPOOL_AND_RETRY.md

Include:

- File layout
- Atomic writes
- Ordering
- Retry classification
- Quarantine
- Retention
- Recovery

## WHATSAPP_WORKER_API.md

Document all endpoints, authentication, and status codes.

## WHATSAPP_SMOKE_TESTS.md

Document manual real-mode setup and safety.

## PHASE_8_REPORT.md

Include:

- Files created
- Files changed
- OpenWA package and version
- Node.js version
- Worker version
- Contract version
- Adapter modes
- Connection states
- Group/admin validation
- Spool design
- Retry policy
- Fixture count
- Test count
- Benchmark results
- API endpoints
- Real WhatsApp smoke test status
- Known limitations
- Confirmation that MT5 execution is not called by the worker

Update README:

```text
Prompt 8 of 12 completed
Next: Prompt 9 — FastAPI Orchestration and Real-Time Events
```

---

# ROOT SCRIPTS

Add or update:

```text
whatsapp:test
whatsapp:contracts
whatsapp:benchmark
whatsapp:fake
whatsapp:status
whatsapp:setup
whatsapp:smoke
```

`whatsapp:smoke` must require explicit environment opt-in.

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

Run existing service checks because ingestion contracts may change:

```powershell
ruff check .
ruff format --check .
mypy apps/trading-service/src
pytest
```

## WhatsApp-specific

```powershell
pnpm whatsapp:test
pnpm whatsapp:contracts
pnpm whatsapp:benchmark
pnpm whatsapp:fake
```

Run `pnpm whatsapp:status` only when safe.

Do not run `whatsapp:smoke` without every explicit opt-in.

## FastAPI

Start the trading service in safe fake mode.

Start the WhatsApp worker in fake mode.

Verify:

```text
worker /health
worker /ready
worker /version
worker /status
worker /configuration
worker /spool
worker /quarantine
worker /events
trading service POST /api/v1/parser/messages
```

Inject fake messages and verify:

- Approved message delivered once
- Reply metadata preserved
- Wrong group ignored
- Wrong sender ignored
- Non-admin ignored
- Duplicate ignored
- Service outage spooled
- Service recovery delivers
- No campaign execution
- No MT5 job created

Stop both services cleanly.

## Security scan

Search active source code for:

```text
order_send
mt5.initialize
MetaTrader5
wa.create
open-wa
LOCAL_API_TOKEN=
Authorization:
sessionData
cookies
password
OpenAI
Anthropic
Gemini
langchain
```

Allowed:

- OpenWA calls inside the real adapter
- MT5 code in the existing MT5 adapter
- Authorization handling without hardcoded tokens

Forbidden:

- WhatsApp worker importing MT5 modules
- Hardcoded credentials
- Session data committed
- QR payload logging
- LLM usage

## Git

Run:

```powershell
git status --short
```

If all checks pass, a local commit is allowed:

```powershell
git add .
git commit -m "feat: complete Prompt 8 - OpenWA WhatsApp Worker"
```

Do not push.

---

# FAILURE HANDLING

Do not mark Prompt 8 complete because files were generated.

When a check fails:

1. Read the complete error.
2. Fix the project-controlled root cause.
3. Rerun the targeted check.
4. Do not bypass approved group validation.
5. Do not bypass approved admin validation.
6. Do not trust display names as IDs.
7. Do not accept non-admin messages when admin-role verification is required.
8. Do not connect the worker to MT5.
9. Do not remove durable spool behaviour.
10. Do not process messages out of order.
11. Do not log QR or session data.
12. Do not commit local configuration.
13. Do not claim real smoke tests passed when not run.
14. Do not falsely report a check as passed.
15. Report genuine external blockers honestly.

---

# COMPLETION REQUIREMENTS

Prompt 8 is complete only when:

- OpenWA is integrated behind an adapter.
- Fake adapter works.
- Real adapter is implemented behind explicit opt-in.
- One-client process lock works.
- Session restoration works.
- QR flow works.
- QR is not logged or persisted by default.
- Group discovery works.
- One approved group is enforced.
- Admin discovery works.
- One approved admin is enforced.
- Admin role is verified.
- Wrong group messages are ignored.
- Wrong sender messages are ignored.
- Self messages are ignored.
- Supported text and captions are extracted.
- Reply IDs are preserved.
- Exact worker idempotency works.
- Durable file spool works.
- Ordered delivery works.
- Retry and quarantine work.
- Trading-service delivery is authenticated.
- Service-side group/admin validation works.
- Worker local API works.
- Session secrets remain local.
- Python and TypeScript contracts agree.
- All project-controlled checks pass.
- Worker never calls MT5.
- WhatsApp does not automatically approve or execute campaigns.
- Live execution remains impossible.
- LLM integration remains absent.
- No credentials are committed.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 8 OF 12 COMPLETED

Project root:
- ...

Versions:
- WhatsApp worker version:
- Ingestion contract version:
- OpenWA adapter version:
- OpenWA package:
- OpenWA package version:
- Node.js version:
- Parser version:
- Contract version:

Adapter modes:
- Fake:
- Real:
- Default mode:

Session:
- Session directory:
- Session restore:
- QR login:
- QR persisted:
- QR logged:
- Logout:
- Reset:
- Process lock:

Connection:
- States:
- Reconnect:
- Backoff:
- Single client:
- Real connection test status:

Group and admin:
- Approved groups supported:
- Approved admins supported:
- Group selection:
- Admin selection:
- Admin role verification:
- Metadata cache:
- Wrong group handling:
- Wrong sender handling:
- Non-admin handling:

Messages:
- Supported types:
- Unsupported types:
- Text preservation:
- Reply metadata:
- Self-message filtering:
- Edit handling:
- Delete handling:
- Maximum text size:

Spool:
- Storage type:
- Ordered delivery:
- Atomic writes:
- Duplicate prevention:
- Crash recovery:
- Retry policy:
- Quarantine:
- Retention:
- Limits:

Delivery:
- Trading service endpoint:
- Authentication:
- Idempotency header:
- Success handling:
- Temporary failure handling:
- Permanent failure handling:
- Campaign execution called:
- MT5 endpoint called:

Worker API:
- Health:
- Readiness:
- Status:
- Session:
- QR:
- Groups:
- Admins:
- Configuration:
- Spool:
- Quarantine:
- Events:

Service-side validation:
- Approved group:
- Approved admin:
- Missing token:
- Wrong group:
- Wrong sender:
- Parser ingestion:
- Automatic approval:
- MT5 execution:

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
- WhatsApp contract tests:
- Envelope benchmark:
- Filter benchmark:
- Spool benchmark:
- Delivery benchmark:
- Worker API tests:
- FastAPI ingestion tests:
- End-to-end fake ingestion:
- Security scan:
- CI:

Real WhatsApp smoke test:
- Status:
- QR authentication:
- Group verified:
- Admin verified:
- Test message received:
- Parser record created:
- Campaign execution performed:
- MT5 execution performed:
- Reason if not run:

Safety verification:
- Worker imports MT5: false
- Worker calls execution API: false
- Approved group count: 1
- Approved admin count: 1
- Admin role required: true
- Session data committed: false
- QR payload logged: false
- Credentials committed: false
- Live execution possible: false
- LLM integration: absent

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 9 OF 12 — FASTAPI ORCHESTRATION AND REAL-TIME EVENTS
```

Stop after Prompt 8.
