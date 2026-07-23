# Transactional Outbox Pattern Specification

## Operational Architecture
To prevent dual-write anomalies between SQLite database mutations and event broadcasting, all events are published using the Transactional Outbox Pattern:

1. **`OutboxPublisher.publish_domain_event`**: Writes both `DomainEventModel` and `EventOutboxModel` within the active `UnitOfWork` database transaction.
2. **`OutboxDispatcher`**: Asynchronously polls or receives notifications for unpublished outbox entries (`status = 'PENDING'`), dispatches them to connected SSE / WebSocket clients, and marks them as `DELIVERED` with `delivered_at` timestamps.

## Guarantee
- **At-Least-Once Delivery**: Events persist atomically with domain state changes.
- **Monotonic Sequencing**: Monotonic sequence keys (`sequence: int, autoincrement=True`) provide reliable reordering and gap detection for UI streaming clients.
