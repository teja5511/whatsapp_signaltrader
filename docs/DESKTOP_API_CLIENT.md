# Desktop Typed API Client Specification

The `ApiClient` class (`apps/desktop/src/api/apiClient.ts`) wraps all local FastAPI and WhatsApp worker endpoints:
- Error categorization: `NETWORK`, `AUTHENTICATION`, `SAFETY_BLOCK`, `VALIDATION`, `STATE_CONFLICT`, `SERVICE_UNAVAILABLE`.
- Unique request correlation IDs (`X-Correlation-ID`).
