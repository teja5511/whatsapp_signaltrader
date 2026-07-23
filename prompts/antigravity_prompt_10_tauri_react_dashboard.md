# PROMPT 10 OF 12 — TAURI REACT DASHBOARD
# 2 PROMPTS REMAIN AFTER THIS PHASE

Continue inside:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

Do not create another project directory.

Preserve all valid Phase 1–9 work. Implement Prompt 10 completely, run every applicable validation, fix every project-controlled failure, and stop after Prompt 10.

Do not explain the plan before starting.
Do not weaken backend safety.
Do not enable live trading.
Do not allow direct desktop access to SQLite, MT5, OpenWA session files, or order execution.
Do not store API tokens in localStorage, sessionStorage, URLs, logs, or plain JSON.
Do not auto-approve ambiguous commands.
Do not add AI or LLM behaviour.
Do not push or create a remote.

A clean local commit is allowed only after all required checks pass.

---

# CURRENT STATE

Phases 1–9 are complete.

Verified backend capabilities:

- FastAPI orchestration
- SQLite, SQLAlchemy, Alembic through revision `005_orchestration_and_realtime_events`
- Deterministic parser
- Campaign state machine
- Duplicate protection
- Entry planner and risk engine
- Fake, dry-run, and real demo-only MT5 adapters
- Durable MT5 execution queue
- OpenWA WhatsApp worker
- One approved group and one approved admin
- Durable WhatsApp spool
- Transactional outbox
- Domain events
- WebSocket, SSE, and event replay
- Automation controls
- Confirmation and automatic orchestration
- Trading disabled by default
- Live execution impossible
- LLM integration absent

Do not rewrite working Phase 1–9 features without a documented technical reason.

---

# PHASE OBJECTIVE

Build the complete Tauri 2 React desktop dashboard for operating and monitoring the XAUUSD WhatsApp-to-MT5 system.

Implement:

1. Professional desktop shell
2. Secure local API authentication
3. FastAPI integration
4. WhatsApp worker integration
5. MT5 status integration
6. WebSocket real-time events
7. SSE fallback
8. REST replay after reconnect
9. Overview dashboard
10. WhatsApp setup and monitoring
11. MT5 setup and monitoring
12. Campaign list and detail
13. Confirmation workflow
14. Ambiguous-command review
15. Planned entries
16. Orders, positions, and execution jobs
17. Event viewer
18. Settings
19. Automation controls
20. Demo-trading controls
21. Emergency controls
22. Loading, empty, offline, degraded, blocked, and error states
23. Accessibility
24. Unit, component, E2E, and build validation

Do not implement full reconciliation, production packaging, live trading, multiple accounts/groups/instruments, or AI.

Prompt 11 handles reliability and reconciliation.
Prompt 12 handles packaging and release.

---

# SOURCE DOCUMENTS

Read:

```text
README.md
docs/ARCHITECTURE.md
docs/SECURITY_AND_SAFETY.md
docs/OPEN_DECISIONS.md
docs/ORCHESTRATION.md
docs/AUTOMATION_AND_CONFIRMATION.md
docs/REALTIME_EVENTS.md
docs/SYSTEM_STATUS.md
docs/CONTROL_API.md
docs/ORCHESTRATION_API.md
docs/WHATSAPP_WORKER_API.md
docs/MT5_API.md
docs/PLANNING_API.md
docs/CAMPAIGN_API.md
docs/PHASE_9_REPORT.md
```

Do not resolve anything in `docs/OPEN_DECISIONS.md`.

---

# BOUNDARIES

Allowed:

```text
Tauri Desktop → authenticated local REST/WebSocket/SSE → FastAPI
Tauri Desktop → authenticated local REST → WhatsApp worker
```

Forbidden:

```text
Desktop → SQLite
Desktop → MetaTrader5 package
Desktop → MT5 terminal directly
Desktop → order_send
Desktop → OpenWA objects
Desktop → WhatsApp session files
Desktop → unrestricted shell
```

The backend remains the final authority for validation and execution.

---

# VERSIONS

Use:

```text
desktop_version = "1.0.0"
dashboard_contract_version = "1.0.0"
desktop_event_client_version = "1.0.0"
```

---

# STACK

Use the existing approved stack:

```text
Tauri 2
React
TypeScript
Vite
Tailwind CSS
shadcn/ui-compatible components
TanStack Query
Zustand
React Router
Zod
React Hook Form
Vitest
React Testing Library
Playwright
```

Use Recharts only where useful.

Do not add a large redundant UI framework.

---

# STRUCTURE

Use a clean structure similar to:

```text
apps/desktop/src/
├── routes/
├── layouts/
├── pages/
│   ├── overview/
│   ├── whatsapp/
│   ├── mt5/
│   ├── campaigns/
│   ├── confirmations/
│   ├── positions/
│   ├── events/
│   ├── settings/
│   └── about/
├── features/
├── components/
├── api/
├── realtime/
├── stores/
├── hooks/
├── lib/
└── tests/

apps/desktop/src-tauri/src/
├── main.rs
├── commands.rs
├── secure_store.rs
├── process.rs
└── window.rs
```

Keep server data in TanStack Query.
Use Zustand only for client UI state and non-sensitive preferences.

---

# DESIGN

Build a professional, dark-first operational dashboard.

Requirements:

- Clean
- Dense but readable
- High contrast
- Low visual noise
- No casino styling
- No flashing profit effects
- No fake P/L
- No excessive gradients

Status semantics:

```text
Green = healthy/success
Amber = warning/degraded/confirmation
Red = blocked/error/emergency
Blue = information
Gray = disabled/offline
```

Never rely on color alone.
Use text, icon, and accessible labels.

Theme:

```text
System
Dark
Light
```

Default:

```text
System
```

---

# APP SHELL

Create:

```text
Sidebar
Top status bar
Main route content
Optional bottom event/connection strip
```

Sidebar:

```text
Overview
WhatsApp
MT5
Campaigns
Confirmations
Orders & Positions
Events
Settings
About
```

Top bar indicators:

```text
DEMO/REAL/BLOCKED
Automation state
Execution mode
Trading enabled
WhatsApp status
MT5 status
FastAPI status
Realtime status
```

Always show a persistent red banner for:

```text
REAL account detected
EMERGENCY_STOPPED
system ERROR
live-account block
```

---

# SECURE TOKEN STORAGE

Never store `LOCAL_API_TOKEN` in browser storage.

Implement secure storage with:

```text
Rust keyring crate
or
Tauri Stronghold
```

Preferred architecture:

```text
React
→ Tauri command
→ Rust secure request proxy
→ FastAPI with Authorization header
```

Required commands:

```text
secure_token_set
secure_token_exists
secure_token_clear
secure_api_request
get_app_version
get_platform_info
open_external_url
```

Rules:

- Token masked in UI
- Token never logged
- Token never placed in query strings
- Token never returned in normal API responses
- Test with fake secure storage
- No generic shell command
- No arbitrary file read/write command

---

# CONNECTION SETTINGS

Defaults:

```text
FastAPI URL = http://127.0.0.1:8000
WhatsApp worker URL = http://127.0.0.1:8010
```

Rules:

- Loopback only by default
- Reject unsupported URL schemes
- Warn before non-loopback URLs
- Never send token to an untrusted host
- Require explicit confirmation for non-loopback addresses

---

# STARTUP FLOW

On startup:

1. Load safe preferences.
2. Check secure token availability.
3. Probe FastAPI health.
4. Probe WhatsApp worker health.
5. Fetch system status and versions.
6. Request short-lived event ticket.
7. Connect WebSocket.
8. Fall back to SSE.
9. Fall back to polling.
10. Replay events after the last sequence.
11. Show degraded state instead of crashing.

---

# TYPED API CLIENT

Requirements:

- Zod-validate all responses
- Timeouts
- AbortController
- Retry GET only
- No automatic mutation retries
- Correlation IDs
- Idempotency keys
- Typed error mapping
- Token redaction
- Loopback validation
- No `any`

Error categories:

```text
NETWORK
AUTHENTICATION
AUTHORIZATION
VALIDATION
STATE_CONFLICT
VERSION_CONFLICT
SAFETY_BLOCK
SERVICE_UNAVAILABLE
EVENT_GAP
UNKNOWN
```

Display backend error code and correlation ID.

---

# REALTIME CLIENT

Use:

```text
POST /api/v1/events/ticket
GET /api/v1/events/ws
GET /api/v1/events/sse
GET /api/v1/events/replay
GET /api/v1/events/latest-sequence
```

Priority:

```text
WebSocket
SSE
REST polling
```

Implement:

- Short-lived ticket auth
- No long-lived token in URL
- Last event sequence tracking
- Replay after reconnect
- Event ID deduplication
- Ordered processing
- Gap detection
- Gap replay
- Exponential reconnect with jitter
- Bounded event buffer
- Slow-client handling
- No duplicate toast for replayed events

States:

```text
DISCONNECTED
CONNECTING
CONNECTED_WS
CONNECTED_SSE
POLLING
REPLAYING
DEGRADED
ERROR
```

---

# OVERVIEW PAGE

Sections:

## System readiness

Cards:

```text
FastAPI
Database
WhatsApp
MT5
Execution worker
Realtime events
```

Each card shows:

- State
- Last update
- Reason
- Link to details

## Trading controls

Display:

```text
Automation
Execution mode
Trading enabled
MT5 environment
Margin mode
Resolved symbol
```

Controls:

```text
Pause
Resume
Set Confirmation
Set Automatic
Enable Demo Trading
Disable Trading
Emergency Stop
Reset Emergency Stop
```

## Campaign summary

Show counts for:

```text
Waiting for TP
Awaiting confirmation
Planned
Placing orders
Pending
Partially filled
Open
Failed
```

## Pending actions

Show:

```text
Campaign confirmations
Ambiguous confirmations
Planning blocks
Failed MT5 jobs
WhatsApp quarantine
```

## Recent events

Show latest domain events.

## Safety summary

Always show:

```text
Live execution possible: false
Instrument: XAUUSD
Maximum campaign volume: 2.0000
Maximum entries: 8
```

---

# WHATSAPP PAGE

Sections:

## Connection

```text
Adapter mode
Connection state
Authenticated
Worker enabled
Worker version
OpenWA version
Last reconnect
```

## Session actions

```text
Start
Stop
Show QR when enabled
Logout
Reset
```

Reset phrase:

```text
RESET WHATSAPP SESSION
```

Never expose the raw QR payload.

## Group setup

- List eligible groups
- Select exactly one
- Show name and masked ID
- Do not auto-select by name

## Admin setup

- List group admins
- Select exactly one
- Show name and masked ID
- Show admin/super-admin state
- Do not trust names as identity

## Spool and quarantine

Show:

```text
Pending
Delivering
Delivered
Quarantined
Retry attempts
Oldest pending
Disk usage
```

Actions:

```text
Retry safe item
Requeue quarantine
View sanitized detail
```

---

# MT5 PAGE

Sections:

## Adapter

```text
fake/dry_run/real
health
initialized
execution enabled
demo only
worker running
```

## Account

```text
Environment
Masked login
Server
Company
Currency
Leverage
Margin mode
Trade allowed
Expert allowed
Balance
Equity
Margin
Free margin
```

Show badges:

```text
DEMO
REAL BLOCKED
UNKNOWN BLOCKED
```

## Symbol

```text
Canonical symbol
Broker symbol
Digits
Point
Tick size
Volume min/max/step
Trade mode
Filling mode
```

## Controls

```text
Initialize
Shutdown
Read-only preflight
Synchronize
```

No live override.

## Queue

Show execution batches and jobs.

---

# CAMPAIGNS PAGE

Filters:

```text
State
Date
Direction
Mode
Campaign code
Parent campaign
```

Columns:

```text
Campaign
Direction
Zone
SL
TP1
TP2
Mode
State
Entries
Lot per entry
Total lots
Created
Updated
```

Use pagination or virtualization.

---

# CAMPAIGN DETAIL

Show:

## Header

```text
Code
State
Direction
Instrument
Mode
Created
Parent/re-entry
Version
```

## Signal

```text
Original text
Zone
SL
TP1
TP2
TP Open metadata
Source message
Reply linkage
```

## Timeline

Chronological state transitions.

## Planning

```text
Planner version
Risk version
Fingerprint
Policies
Symbol snapshot
Validation issues
```

## Planned entries

```text
Sequence
Price
Lot
SL
TP
TP category
Order type
Magic
Comment
Status
Order ticket
Position ticket
```

## Commands

Show matching result and status.

## Confirmations

Show approval/rejection history.

## Execution

Show batches, jobs, checks, orders, positions, and sync state.

## Context actions

```text
Approve only
Approve, plan, and queue demo
Reject
Plan
Replan
MT5 preflight
Queue demo
Cancel pending
Close campaign
Retry blocked orchestration
```

Only show actions valid for the current state.
Backend remains authoritative.

---

# CONFIRMATIONS PAGE

Tabs:

```text
Campaign confirmations
Ambiguous command confirmations
```

Campaign card:

```text
Campaign
Signal
Direction
Zone
SL
TPs
Entries
Lot
Total lots
Mode
Risk summary
Created
```

Actions:

```text
Approve only
Approve, plan, and queue demo
Reject
Open campaign
```

Ambiguous command card:

```text
Original text
Suggested action
Campaign
Match type
Candidate count
Created
Expiry
```

Require explicit action:

```text
Approve close
Approve cancel
Hold/no action
Skip/no action
Reject command
```

No generic ambiguous “Approve”.

---

# ORDERS AND POSITIONS

Tabs:

```text
Pending Orders
Open Positions
History
Execution Jobs
```

Pending order actions:

```text
Modify
Delete
Open campaign
```

Position actions:

```text
Modify SL/TP
Close
Open campaign
```

Use backend values only.
Do not invent P/L.

---

# EVENTS PAGE

Features:

```text
Live/pause
Event type filter
Campaign filter
Aggregate filter
Severity filter
Search
Sequence range
Replay
Export sanitized JSON
```

Columns:

```text
Sequence
Time
Event
Aggregate
Campaign
Actor
Correlation
Causation
Summary
```

Detail drawer:

- Pretty redacted JSON
- Copy event ID
- Copy correlation ID
- Open campaign

Virtualize large lists.

---

# SETTINGS PAGE

## General

```text
Theme
Refresh interval
Event buffer size
Desktop notifications
Sound notifications
```

Sound default:

```text
off
```

## API

```text
FastAPI URL
Worker URL
Token configured
Test connection
Clear token
```

## Trading defaults

```text
Execution mode
Entry count
Lot per entry
Maximum total lots
```

Validate:

```text
3 <= entries <= 8
lot > 0
entries × lot <= 2.0000
```

Never silently adjust.

## Planning policies

Expose backend-supported settings:

```text
100-pip distance
Policy confirmed
TP allocation policy
Explicit TP indices
Unspecified intent policy
Current-price policy
```

Show unresolved warnings.
Do not guess values.

## MT5 safety

Display:

```text
Adapter mode
Demo only
Execution enabled
Manual confirmation
Allowlist status
Close-all status
```

Never expose live enablement.

## WhatsApp

Show approved group, admin, and admin-role requirement.

---

# ABOUT PAGE

Show all application and backend versions, schema revision, build mode, Tauri, Rust, Node, and Python versions.

Safety statement:

```text
Demo-only execution
XAUUSD only
Live-account execution blocked
```

---

# DANGEROUS CONTROL DIALOGS

## Automatic mode

Warn:

```text
Automatic mode still requires demo trading to be enabled and every backend safety gate to pass.
```

## Enable demo trading

Typed phrase:

```text
ENABLE DEMO XAUUSD TRADING
```

Show account, masked login, server, hedging, symbol, and max lots.

## Emergency stop

Typed phrase:

```text
EMERGENCY STOP XAUUSD
```

Explain that it stops new work but does not automatically close positions.

## Reset emergency stop

Typed phrase:

```text
RESET EMERGENCY STOP
```

Explain that reset does not enable trading.

## Emergency close-all

Typed phrase:

```text
CLOSE ALL DEMO XAUUSD
```

Default scope:

```text
APPLICATION_OWNED
```

Use backend preview when available.

---

# NOTIFICATIONS

Use toasts for transient results.

Use persistent banners for:

```text
Backend offline
Worker offline
MT5 blocked
Live account detected
Emergency stop
Realtime disconnected
Unresolved policy
Failed execution job
Quarantine backlog
```

OS notifications require opt-in.

Do not include raw signal text by default.

---

# OFFLINE AND DEGRADED BEHAVIOUR

FastAPI offline:

- Show offline shell
- Disable mutations
- Keep connection settings available

Worker offline:

- Show degraded
- Keep campaigns and MT5 usable

MT5 offline:

- Show blocked
- Keep ingestion and review usable

Realtime offline:

- Fall back to polling

Never crash the app.

---

# ACCESSIBILITY

Meet practical WCAG 2.1 AA requirements:

- Keyboard navigation
- Visible focus
- Labels
- Dialog focus trapping
- Screen-reader status
- Table headers
- Form error associations
- Reduced motion
- Color-independent status
- Readable contrast

Add automated accessibility tests where practical.

---

# TAURI SECURITY

Minimize capabilities.

Requirements:

- No unrestricted filesystem
- No arbitrary shell
- No direct database access
- No direct MT5 access
- No WhatsApp session access
- CSP enabled
- Production DevTools disabled where appropriate
- App-origin navigation locked
- External links opened safely
- Local API allowlist only

Audit `tauri.conf.json` and capabilities.

---

# API COMPATIBILITY

Inspect backend endpoints.

Add only safe read endpoints or typed wrappers when necessary, such as:

```text
GET /api/v1/confirmations
GET /api/v1/mt5/orders
GET /api/v1/mt5/positions
GET /api/v1/mt5/history
GET /api/v1/mt5/execution/batches
```

Do not weaken safety.

Use shared schemas from `packages/shared-contracts`.

---

# REQUIRED TESTS

## Unit/component

Test:

- App shell and routes
- Offline/error boundaries
- Secure token handling
- Status states
- All controls
- Campaign list/detail
- Confirmations
- WhatsApp setup
- MT5 views
- Event replay/gaps/deduplication
- Accessibility
- Fake/live-block labels

## Security

Verify:

- No token in localStorage
- No token in sessionStorage
- No token in URLs
- No token in logs
- Non-loopback warning
- No generic shell command
- No broad filesystem capability

## Playwright E2E

Required scenarios:

1. Configure token and load Overview.
2. Healthy fake system.
3. Pause/resume.
4. Set confirmation/automatic.
5. Receive campaign event.
6. View campaign.
7. Approve only.
8. Approve and queue demo.
9. Review delayed TP.
10. Review ambiguous command.
11. View job progression.
12. View spool recovery.
13. Emergency stop.
14. Reset emergency stop.
15. Event reconnect and replay.
16. Backend offline/recovery.
17. Worker offline.
18. MT5 blocked.
19. No live control.
20. No token in browser storage.

Use fake services only.

---

# BUILD SCRIPTS

Add or update:

```text
desktop:dev
desktop:build
desktop:test
desktop:test:e2e
desktop:lint
desktop:typecheck
desktop:tauri:dev
desktop:tauri:build
desktop:visual
```

---

# MOCK MODE

Support:

```text
VITE_DESKTOP_MOCK_MODE=false
```

When true:

- Deterministic fixtures
- Permanent `MOCK MODE` banner
- No real WhatsApp or MT5
- No real token persistence

Default false.

---

# DOCUMENTATION

Create or update:

```text
docs/DESKTOP_DASHBOARD.md
docs/DESKTOP_SECURITY.md
docs/DESKTOP_API_CLIENT.md
docs/DESKTOP_REALTIME.md
docs/DESKTOP_CONTROLS.md
docs/DESKTOP_CAMPAIGNS.md
docs/DESKTOP_WHATSAPP.md
docs/DESKTOP_MT5.md
docs/DESKTOP_TESTING.md
docs/PHASE_10_REPORT.md
docs/ARCHITECTURE.md
docs/SECURITY_AND_SAFETY.md
docs/ACCEPTANCE_CRITERIA.md
docs/REPOSITORY_STRUCTURE.md
README.md
```

Update README:

```text
Prompt 10 of 12 completed
Next: Prompt 11 — Reconciliation, Emergency Controls and Reliability
```

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
pnpm desktop:lint
pnpm desktop:typecheck
pnpm desktop:test
pnpm desktop:test:e2e
pnpm desktop:build
pnpm desktop:tauri:build
ruff check .
ruff format --check .
mypy apps/trading-service/src
pytest
pnpm whatsapp:test
pnpm whatsapp:contracts
```

Run integrated fake mode:

```text
FastAPI
Fake MT5 adapter
Fake MT5 worker
Fake WhatsApp worker
Desktop
```

Verify all pages and controls.

Stop cleanly.

Security scan:

```text
localStorage.setItem
sessionStorage.setItem
LOCAL_API_TOKEN=
Authorization:
order_send
MetaTrader5
sqlite
sessionData
password
OpenAI
Anthropic
Gemini
langchain
Command::new
shell.open
```

Review every allowed match.

Run:

```powershell
git status --short
```

If all checks pass:

```powershell
git add .
git commit -m "feat: complete Prompt 10 - Tauri React Dashboard"
```

Do not push.

---

# FAILURE HANDLING

Do not mark Prompt 10 complete because files exist.

When a check fails:

1. Read the full error.
2. Fix the root cause.
3. Rerun the targeted check.
4. Do not bypass backend safety.
5. Do not persist tokens insecurely.
6. Do not add direct MT5 or SQLite access.
7. Do not hide degraded states.
8. Do not use untyped API data.
9. Do not auto-approve ambiguous commands.
10. Do not display fake mode as real.
11. Do not claim Tauri build passed unless it did.
12. Report genuine external blockers.

---

# COMPLETION REQUIREMENTS

Prompt 10 is complete only when:

- Desktop dashboard is implemented.
- Secure token storage works.
- No insecure token persistence exists.
- Typed API client works.
- Overview works.
- WhatsApp page works.
- MT5 page works.
- Campaign list/detail work.
- Confirmations work.
- Ambiguous review works.
- Orders/positions work.
- Events page works.
- Settings and About work.
- WebSocket, SSE fallback, and replay work.
- Automation and demo controls work.
- Emergency controls work.
- Offline/degraded states work.
- Accessibility tests pass.
- E2E fake-mode tests pass.
- Tauri build succeeds.
- Backend compatibility tests pass.
- No direct database or MT5 access exists.
- Live execution remains impossible.
- LLM integration remains absent.
- No credentials are committed.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROMPT 10 OF 12 COMPLETED

Project root:
- ...

Versions:
- Desktop version:
- Dashboard contract version:
- Event client version:
- Tauri version:
- React version:
- TypeScript version:
- Backend orchestrator version:
- Event contract version:

Desktop architecture:
- Routes:
- State management:
- Server cache:
- API client:
- Realtime:
- Secure storage:
- Tauri capabilities:
- CSP:

Pages:
- Overview:
- WhatsApp:
- MT5:
- Campaigns:
- Campaign detail:
- Confirmations:
- Orders and positions:
- Events:
- Settings:
- About:

Controls:
- Pause:
- Resume:
- Confirmation mode:
- Automatic mode:
- Enable demo trading:
- Disable trading:
- Emergency stop:
- Emergency reset:
- Emergency close-all:
- Typed phrases:

Realtime:
- WebSocket:
- SSE fallback:
- REST fallback:
- Replay:
- Gap recovery:
- Deduplication:
- Backpressure:
- Last sequence:

Security:
- Token storage:
- Token in localStorage:
- Token in sessionStorage:
- Token in URLs:
- Token in logs:
- Loopback default:
- Direct SQLite access:
- Direct MT5 access:
- Generic shell:
- Broad filesystem:

UI states:
- Healthy:
- Degraded:
- Offline:
- Emergency stopped:
- Live blocked:
- Fake adapter:
- Loading:
- Empty:
- Error:

Testing:
- Unit:
- Components:
- Accessibility:
- Playwright:
- Visual:
- Backend compatibility:
- Worker compatibility:

Validation:
- Existing validation:
- pnpm format:
- pnpm lint:
- pnpm typecheck:
- pnpm test:
- pnpm build:
- Desktop lint:
- Desktop typecheck:
- Desktop tests:
- Desktop E2E:
- Desktop build:
- Tauri build:
- Ruff:
- Python typecheck:
- Pytest:
- WhatsApp tests:
- Integrated fake mode:
- Security scan:

Safety verification:
- Trading enabled by default: false
- Live execution possible: false
- Demo indicators present: true
- Ambiguous auto-approval: false
- Desktop calls MT5 directly: false
- Desktop accesses SQLite directly: false
- Token persisted insecurely: false
- LLM integration: absent
- Credentials committed: false

Warnings or external blockers:
- ...

Git status:
- ...

Ready for:
PROMPT 11 OF 12 — RECONCILIATION, EMERGENCY CONTROLS AND RELIABILITY
```

Stop after Prompt 10.
