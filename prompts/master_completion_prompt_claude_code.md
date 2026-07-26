# MASTER COMPLETION PROMPT — FINISH THE ENTIRE PROJECT

You are Claude Code working inside the existing repository:

```text
C:\Users\Pavan Teja\projects\whatsapp_trading bot
```

You already know the complete project context.

Do not create a new project.
Do not restart from scratch.
Preserve valid Phase 1–10 work.
Inspect the real code instead of trusting completion reports.
Find and fix every project-controlled bug, finish all missing work, harden reliability and security, run the full validation matrix, build the Windows Tauri release, and leave the repository as a complete `1.0.0-demo` release.

Do not explain the plan before starting.
Do not stop after creating files.
Do not claim success unless the implementation, tests, migrations, runtime checks, and release build actually pass.
Do not push to a remote.
Create a final local commit only after all project-controlled checks pass.

---

# NON-NEGOTIABLE PRODUCT RULES

```text
Instrument: XAUUSD only
Platform: MetaTrader 5
Broker target: Exness
Account type: Demo only
Account mode: Hedging only
WhatsApp accounts: 1
Approved groups: 1
Approved admins: 1
Minimum entries: 3
Maximum entries: 8
Default entries: 5
Default lot per entry: 0.3000
Maximum total campaign lots: 2.0000
Default automation: PAUSED
Default execution mode: CONFIRMATION
Trading enabled by default: false
Live execution: impossible
```

Never add a live-trading override.

Never allow:

```text
WhatsApp worker → MT5
Desktop → MT5 directly
Desktop → SQLite directly
Parser → MT5
LLM → trading action
Ambiguous command → automatic execution
Live or non-hedging account → trade mutation
```

All real MT5 trade operations must remain behind:

```text
explicit execution enable
demo-account verification
hedging verification
XAUUSD symbol verification
account/server allowlists when configured
campaign-state validation
planning fingerprint validation
risk validation
single-writer execution queue
idempotency protection
```

---

# EXISTING PHASES TO VERIFY

The repository claims to include:

1. Requirements and architecture
2. Monorepo and service scaffolding
3. Database, migrations, repositories, and shared contracts
4. Deterministic parser
5. Campaign state machine and duplicate protection
6. Entry ladder, TP allocation, and risk engine
7. MT5 adapter and demo execution worker
8. OpenWA WhatsApp worker
9. FastAPI orchestration and real-time events
10. Tauri React dashboard

Verify every claim against the actual repository.

Repair:

- Missing modules
- Fake implementations
- Unimplemented routes
- Broken imports
- Dead code
- Contract drift
- Migration drift
- Incorrect settings
- Broken scripts
- Failing tests
- Security gaps
- UI/API mismatches
- Packaging failures

Create:

```text
docs/FINAL_AUDIT.md
```

Record all problems found and fixes made.

---

# COMPLETE BUG AUDIT

Search the tracked repository for:

```text
TODO
FIXME
HACK
NotImplemented
NotImplementedError
placeholder
mock only
return {}
return []
pass
throw new Error
@ts-ignore
type: ignore
skip
xfail
debugger
console.log
hardcoded
temporary
```

Review all relevant matches.

Fix all project-controlled issues including:

- Decimal-to-float conversions
- Timezone errors
- Enum mismatches
- API schema mismatches
- Duplicate rows or jobs
- Queue races
- Event duplication or sequence gaps
- Transaction boundary errors
- Stale locks
- Retry storms
- Crash-recovery gaps
- Token leakage
- Unsafe Tauri capabilities
- React route/render bugs
- Broken dangerous-action dialogs
- Accessibility failures
- Windows path-with-spaces failures
- Build and installer failures

Do not hide failures by weakening tests, typing, linting, constraints, or safety gates.

---

# UNRESOLVED TRADING RULES

Inspect:

```text
docs/OPEN_DECISIONS.md
```

Do not guess unresolved trading behaviour.

For every unresolved item:

1. Implement a typed policy.
2. Use a safe blocked default.
3. Expose it in backend settings and the desktop UI.
4. Validate it.
5. Persist it in policy snapshots.
6. Add tests.
7. Prevent execution until resolved or explicitly confirmed.

This includes:

- Exact XAUUSD meaning of 100 pips
- Current price inside or beyond the zone
- TP1/TP2 ladder indices
- Secure Profits
- Exit this trade on your comfort
- Hold it
- Skip this for now
- Zone Valid reactivation
- New signal while another campaign is active
- Existing filled positions after a newer signal

---

# FINISH PHASE 11 — RECONCILIATION, RECOVERY, AND RELIABILITY

Use:

```text
reconciliation_version = "1.0.0"
recovery_version = "1.0.0"
reliability_version = "1.0.0"
```

## Startup recovery

On service startup:

1. Verify database revision and integrity.
2. Verify SQLite foreign keys, WAL, and busy timeout.
3. Restore persisted control state.
4. Keep automation paused unless explicitly persisted otherwise.
5. Never automatically enable trading.
6. Recover abandoned orchestration runs.
7. Recover outbox rows stuck in publishing.
8. Recover execution jobs stuck in running.
9. Mark uncertain broker sends `OUTCOME_UNKNOWN`.
10. Never automatically resend an uncertain operation.
11. Recover WhatsApp spool files left in delivering state.
12. Verify event sequence integrity.
13. Start workers only after safety checks pass.

## MT5 reconciliation

Implement:

```text
startup reconciliation
manual reconciliation
periodic reconciliation
campaign reconciliation
order reconciliation
position reconciliation
history reconciliation
unknown-outcome reconciliation
```

Match using:

```text
ticket
magic number
comment namespace
broker symbol
campaign mapping
planned-entry mapping
volume
price
time window
```

Classifications:

```text
MATCHED
LOCAL_ONLY
BROKER_ONLY
MISMATCHED
MISSING_ORDER
MISSING_POSITION
UNEXPECTED_ORDER
UNEXPECTED_POSITION
DUPLICATE_BROKER_ORDER
OUTCOME_UNKNOWN
```

Do not adopt unrelated broker trades.

Do not delete broker orders automatically because local state differs.

Require explicit review for uncertain cases.

## Reconciliation persistence

Create migration if needed:

```text
006_reconciliation_and_reliability
```

Add appropriate tables such as:

```text
reconciliation_runs
reconciliation_items
recovery_actions
system_locks
health_incidents
```

Persist snapshots, differences, resolution, actor, correlation ID, and timestamps.

## Durable worker recovery

Implement leases and heartbeats.

Rules:

- Dead `RUNNING` job → `OUTCOME_UNKNOWN`
- `QUEUED` remains queued
- `SUCCEEDED` immutable
- `BLOCKED` remains blocked
- Failed trade sends require explicit retry
- No duplicate order submission after restart

## Transactional outbox recovery

- Recover stale publishing locks
- Publish committed events only
- Preserve event sequence
- Retry temporary failures
- Keep publication idempotent
- Never delete domain events needed for replay

## WhatsApp recovery

- Restore delivering files to pending after crash
- Detect duplicate spool files
- Quarantine corrupt items
- Preserve order
- Recover stale session locks safely
- Prevent duplicate delivery after reconnect

## Database reliability

Implement:

```text
scripts/backup-database.ps1
scripts/verify-database.ps1
scripts/restore-database.ps1
```

Requirements:

- Safe backup
- Integrity verification
- Migration revision reporting
- Restore confirmation phrase
- Backup before overwrite
- Disk-full handling
- Database-size metrics
- Migration lock

## Health incidents

Persist incidents:

```text
DATABASE_DEGRADED
WHATSAPP_DISCONNECTED
MT5_DISCONNECTED
LIVE_ACCOUNT_BLOCKED
NON_HEDGING_ACCOUNT_BLOCKED
OUTBOX_BACKLOG
EXECUTION_QUEUE_STALLED
RECONCILIATION_MISMATCH
DISK_SPACE_LOW
SPOOL_LIMIT_REACHED
EVENT_SEQUENCE_ERROR
```

Statuses:

```text
OPEN
ACKNOWLEDGED
RESOLVED
```

## Emergency stop hardening

Phrase:

```text
EMERGENCY STOP XAUUSD
```

Must:

- Persist synchronously
- Disable trading
- Block new automatic planning and execution
- Cancel safe queued jobs
- Let an active broker call reach a safe boundary
- Mark uncertain results for reconciliation
- Survive restart
- Emit a high-severity event

Reset phrase:

```text
RESET EMERGENCY STOP
```

Reset must never re-enable trading.

## Emergency close hardening

Use:

```text
preview → confirm → queue → execute → reconcile → report
```

Scopes:

```text
APPLICATION_OWNED
ALL_XAUUSD_ON_DEMO_ACCOUNT
```

Default:

```text
APPLICATION_OWNED
```

Phrase:

```text
CLOSE ALL DEMO XAUUSD
```

Before execution show:

- Demo account
- Hedging status
- Broker symbol
- Every affected order and position
- Total volume
- Scope

After execution reconcile every ticket.
Do not claim success until broker state confirms it.
Keep emergency stop active.

## Graceful shutdown

Coordinate:

1. Stop accepting mutations.
2. Persist shutdown state.
3. Stop orchestration intake.
4. Stop outbox dispatcher.
5. Stop reconciliation.
6. Stop MT5 worker at a safe boundary.
7. Stop WhatsApp delivery loop.
8. Release locks.
9. Flush logs.
10. Close database sessions.
11. Shut down MT5 once.
12. Exit cleanly.

## Process scripts

Create:

```text
scripts/start-all.ps1
scripts/stop-all.ps1
scripts/status-all.ps1
```

Support paths containing spaces.

---

# FINISH PHASE 12 — RELEASE VALIDATION AND PACKAGING

Use:

```text
release_version = "1.0.0-demo"
```

## Contract audit

Validate matching Python Pydantic and TypeScript Zod contracts for:

- Messages
- Parser
- Campaigns
- Commands
- Planning
- MT5
- WhatsApp
- Orchestration
- Events
- Reconciliation
- Desktop

Every valid fixture must pass both.
Every invalid fixture must fail both.

## Migration audit

Test:

```text
base → head
head → previous
previous → head
fresh database
existing Phase 3 data
existing campaigns
existing plans
existing MT5 jobs
existing events
existing reconciliation data
```

Preserve data.

## Full fake end-to-end scenarios

Use real application logic with:

```text
Fake OpenWA
Real parser
Real campaign service
Real duplicate protection
Real planner
Fake MT5
Real execution worker
Real orchestration
Real events
Real desktop
Temporary SQLite
```

Test at least:

1. Complete BUY signal
2. Complete SELL signal
3. Incomplete signal with delayed TPs
4. Exact duplicate
5. Semantic duplicate
6. Re-entry
7. SL update before execution
8. SL update with pending orders
9. SL update with positions
10. Close before execution
11. Cancel pending orders
12. Close active campaign
13. Ambiguous commands
14. Automatic mode paused
15. Automatic mode trading disabled
16. Automatic demo execution
17. Live-account block
18. Netting-account block
19. Symbol ambiguity
20. Symbol specification change
21. Order-check failure
22. Partial placement
23. Immediate fill
24. Unknown outcome
25. Worker restart
26. FastAPI restart
27. MT5 worker restart
28. Outbox restart
29. Desktop reconnect and event replay
30. Emergency stop during queued work
31. Emergency close
32. Reconciliation mismatches
33. Database backup and restore verification

Validate database state, event order, campaign state, idempotency, and absence of duplicate trade sends.

## Real smoke-test scripts

Create manually gated commands:

```text
whatsapp:smoke
mt5:demo-smoke
combined:demo-smoke
```

Never run in CI.

Required environment flags:

```text
RUN_WHATSAPP_SMOKE_TESTS=true
RUN_MT5_DEMO_SMOKE_TESTS=true
RUN_COMBINED_DEMO_SMOKE_TEST=true
```

If not run, report:

```text
NOT RUN — manual credentials and explicit opt-in required
```

Never report unrun smoke tests as passed.

## MT5 demo smoke

When explicitly enabled:

- Confirm demo
- Confirm hedging
- Confirm allowlist
- Resolve XAUUSD
- Use safe minimum lot
- Place one distant pending order
- Confirm ticket
- Delete it
- Confirm no pending order remains
- Confirm no position remains

## WhatsApp smoke

When explicitly enabled:

- Authenticate
- Verify selected group
- Verify selected admin
- Receive one designated test message
- Deliver it once
- Verify parser persistence
- Verify no automatic MT5 execution unless separately enabled

## Security audit

Run:

```text
pnpm audit
pip-audit
cargo audit
```

Fix project-controlled critical and high issues.

Scan for:

- Credentials
- `.env`
- Tokens
- Passwords
- Session files
- Cookies
- QR payloads
- Hardcoded account IDs
- Hardcoded group/admin IDs
- Live enable flags
- Insecure browser storage
- Unrestricted shell
- Unrestricted filesystem
- SQL injection
- Command injection
- Path traversal
- Unsafe deserialization
- Secret event payloads
- Cross-campaign MT5 mutation

## Logging

Implement structured rotating logs:

- Separate service logs
- Size-based rotation
- Retention
- Correlation IDs
- Secret redaction
- Sanitized desktop log viewer

## Support bundle

Generate a safe support bundle with:

- Versions
- Sanitized settings
- Health
- Migration revision
- Recent sanitized logs
- Recent event metadata
- Reconciliation summary
- Test summary

Exclude:

- Tokens
- Passwords
- Session data
- QR
- Cookies
- Full account login
- Personal chats

## Performance and soak

Run:

- Parser benchmark
- Duplicate fingerprint benchmark
- Planning benchmark
- Fake execution benchmark
- Spool benchmark
- Event benchmark
- Replay benchmark
- Desktop event-render benchmark
- Restart loop test
- Database growth test
- One-hour synthetic soak test

The soak test must prove:

- No duplicate sends
- Stable memory
- Stable queues
- Recoverable temporary failures
- Stable database
- Stable event ordering

## Windows packaging

Build a real Tauri Windows release.

Requirements:

- Production frontend build
- Rust release build
- Working executable
- Windows installer or supported Tauri bundle
- Correct app-data paths
- Correct database and spool locations
- No development-server dependency
- No mock mode
- No DevTools in release
- No embedded credentials
- Safe first-run flow

Create or document:

```text
release/
dist/
```

Do not treat a Vite build as a Tauri release build.

## First run

Implement:

1. Demo-only safety statement
2. XAUUSD-only statement
3. Secure API-token setup
4. Backend health check
5. Worker health check
6. MT5 health check
7. WhatsApp group/admin setup
8. Unresolved-policy review
9. Automation remains paused
10. Trading remains disabled

---

# FINISH AND VERIFY THE DESKTOP

Verify and fix Phase 10 completely.

Must work:

- Overview
- WhatsApp setup/status
- MT5 account/symbol/status
- Campaign list/detail
- Confirmation actions
- Ambiguous-command actions
- Planned entries
- Orders and positions
- Execution jobs
- Events with WS/SSE/replay
- Settings
- About
- Offline/degraded states
- Typed dangerous-action dialogs
- Secure token storage
- Tauri CSP and capabilities
- Accessibility
- Playwright E2E
- Real Tauri release build

No direct SQLite or MT5 access.

Generate an API endpoint inventory and verify every frontend call against the backend.

---

# OBSERVABILITY ENDPOINTS

Add authenticated safe endpoints:

```text
GET /api/v1/diagnostics
GET /api/v1/reconciliation/status
GET /api/v1/reconciliation/runs
GET /api/v1/incidents
GET /api/v1/support-bundle/preview
POST /api/v1/support-bundle
```

Expose safe metrics:

- Uptime
- Queue sizes
- Spool sizes
- Event backlog
- Database size
- Reconciliation status
- Last MT5 sync
- Last WhatsApp delivery
- Worker heartbeat
- Disk-space status

---

# DOCUMENTATION

Create or update:

```text
README.md
docs/FINAL_AUDIT.md
docs/RECONCILIATION.md
docs/RECOVERY.md
docs/RELIABILITY.md
docs/EMERGENCY_OPERATIONS.md
docs/DATABASE_BACKUP_RESTORE.md
docs/OPERATIONS.md
docs/FIRST_RUN.md
docs/DEMO_SETUP.md
docs/REAL_WHATSAPP_SETUP.md
docs/REAL_MT5_DEMO_SETUP.md
docs/TESTING.md
docs/SECURITY_AUDIT.md
docs/PERFORMANCE.md
docs/PACKAGING.md
docs/TROUBLESHOOTING.md
docs/KNOWN_LIMITATIONS.md
docs/RELEASE_NOTES_1.0.0-demo.md
docs/FINAL_COMPLETION_REPORT.md
```

README status:

```text
Project status: Complete demo release
Release: 1.0.0-demo
Live trading: Not supported
Instrument: XAUUSD only
Default state: Paused and trading disabled
```

Update Mermaid architecture, message flow, execution flow, event flow, recovery flow, and reconciliation flow.

---

# REQUIRED COMMANDS

Run all applicable commands.

## Root

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

## Desktop

```powershell
pnpm desktop:lint
pnpm desktop:typecheck
pnpm desktop:test
pnpm desktop:test:e2e
pnpm desktop:build
pnpm desktop:tauri:build
```

## WhatsApp

```powershell
pnpm whatsapp:test
pnpm whatsapp:contracts
pnpm whatsapp:benchmark
pnpm whatsapp:fake
```

## Campaign/planning/MT5/orchestration/events

```powershell
pnpm campaign:test
pnpm campaign:contracts
pnpm campaign:benchmark
pnpm campaign:migrations

pnpm planning:test
pnpm planning:contracts
pnpm planning:benchmark
pnpm planning:migrations

pnpm mt5:test
pnpm mt5:contracts
pnpm mt5:benchmark
pnpm mt5:migrations

pnpm orchestration:test
pnpm orchestration:contracts
pnpm orchestration:benchmark
pnpm orchestration:migrations

pnpm events:test
pnpm events:benchmark
pnpm e2e:fake
```

## Add and run final scripts

```powershell
pnpm reconciliation:test
pnpm recovery:test
pnpm reliability:test
pnpm security:audit
pnpm soak:test
pnpm release:validate
pnpm release:build
```

## Alembic

```powershell
alembic upgrade head
alembic current
alembic downgrade -1
alembic upgrade head
```

Also test full base-to-head and fixture upgrades.

## Rust

Inside `apps/desktop/src-tauri`:

```powershell
cargo fmt --check
cargo clippy --all-targets --all-features -- -D warnings
cargo test
cargo build --release
```

## Security tools

```text
pnpm audit
pip-audit
cargo audit
```

## Git

```powershell
git status --short
```

---

# RELEASE ACCEPTANCE CRITERIA

The project is complete only when:

- All project-controlled tests pass.
- All required migrations work.
- Fake end-to-end tests pass.
- Startup recovery works.
- Reconciliation works.
- Queue, outbox, and spool recovery work.
- Emergency stop survives restart.
- Emergency close is reconciled.
- No duplicate broker send can occur.
- Live accounts remain blocked.
- Netting accounts remain blocked.
- XAUUSD-only enforcement works.
- Total volume never exceeds 2.0000.
- Entry count never exceeds 8.
- Default lot remains 0.3000.
- Ambiguous commands never execute automatically.
- Unresolved policies block safely.
- Desktop does not access SQLite or MT5 directly.
- Tokens remain secure.
- No credentials are tracked.
- Tauri release build succeeds.
- Windows release artefacts exist.
- Documentation matches reality.
- Real smoke tests are honestly marked run or not run.
- Git working tree is clean after the final commit.

---

# FINAL COMMIT

Only after all project-controlled validation passes:

```powershell
git add .
git commit -m "release: complete XAUUSD WhatsApp MT5 demo trading platform v1.0.0-demo"
```

Do not push.

---

# FINAL RESPONSE FORMAT

Respond only with:

```text
PROJECT COMPLETION SUCCESSFUL

Project:
- WhatsApp XAUUSD MT5 Trading Platform

Release:
- Version:
- Project root:
- Final commit:

Audit:
- Bugs found:
- Bugs fixed:
- Stubs removed:
- TODOs remaining:
- Known limitations:

Core:
- FastAPI:
- WhatsApp worker:
- Parser:
- Campaign service:
- Planner:
- MT5 adapter:
- MT5 worker:
- Orchestrator:
- Events:
- Reconciliation:
- Desktop:

Safety:
- Default automation:
- Default execution mode:
- Trading default:
- Live execution:
- Demo enforcement:
- Hedging enforcement:
- Instrument:
- Maximum entries:
- Default lot:
- Maximum total lots:
- Ambiguous automatic execution:
- Unresolved policy behaviour:

Reliability:
- Startup recovery:
- Queue recovery:
- Outbox recovery:
- Spool recovery:
- Reconciliation:
- Backup/restore:
- Graceful shutdown:
- Emergency stop:
- Emergency close:

Desktop release:
- Tauri build:
- Windows executable:
- Installer:
- First-run setup:
- Secure token storage:

Testing:
- Python tests:
- TypeScript tests:
- Rust tests:
- Playwright scenarios:
- Fake E2E scenarios:
- Contract tests:
- Migration tests:
- Recovery tests:
- Reconciliation tests:
- Security audit:
- Soak test:

Real smoke tests:
- WhatsApp:
- MT5 demo:
- Combined:
- Reason if not run:

Release artefacts:
- Executable:
- Installer:
- Documentation:
- Example configuration:
- Support bundle:
- Test reports:

Validation:
- Formatting:
- Lint:
- Type checking:
- Frontend build:
- Tauri build:
- Dependency audits:
- Security scan:
- Git status:

Warnings:
- ...

READY FOR MANUAL DEMO SETUP
```

Do not stop until the repository is genuinely complete.
