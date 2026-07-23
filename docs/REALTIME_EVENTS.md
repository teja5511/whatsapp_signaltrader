# Real-Time Domain Event Distribution Architecture

## Streaming Channels
1. **Server-Sent Events (SSE)**: `GET /api/v1/events/sse`
   - Real-time event streaming to web browsers and monitoring UI.
   - Requires short-lived ticket parameter `?ticket=...` generated via `POST /api/v1/events/ticket`.

2. **WebSocket (WS)**: `WS /api/v1/events/ws`
   - Bidirectional real-time event distribution.
   - Authenticated via Bearer token or short-lived connection tickets.

3. **REST Event Replay**: `GET /api/v1/events`
   - Supports sequence replay (`?after_sequence=N`), event filtering by type or campaign ID.

## Security & Payload Redaction
All published event payloads pass through zero-trust redaction (`redact_event_payload`) to strip passwords, Bearer tokens, secrets, session cookies, and QR code raw data before broadcasting.
