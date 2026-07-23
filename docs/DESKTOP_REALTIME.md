# Desktop Real-Time Event Client Architecture

## Connection Hierarchy
1. **WebSocket**: Primary connection via `ws://127.0.0.1:8000/api/v1/events/ws?ticket=...`.
2. **SSE Fallback**: Connects to `http://127.0.0.1:8000/api/v1/events/sse?ticket=...` if WebSocket is unavailable.
3. **REST Polling Fallback**: Polls `GET /api/v1/events?after_sequence=N` every 3 seconds if SSE fails.

## Gap Recovery & Replay
Sequence tracking (`lastSequence`) automatically replays missing domain events after reconnecting.
Deduplication Set limits buffer to 500 recent `event_id` keys.
