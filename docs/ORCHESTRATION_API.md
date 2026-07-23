# Orchestration API Specification

## Endpoints
- `GET /api/v1/orchestration/runs`: Query orchestration runs by status or source ID.
- `GET /api/v1/orchestration/runs/{run_id}`: Retrieve full orchestration run details and step trace.
- `POST /api/v1/orchestration/campaigns/{campaign_id}/approve`: Approve an awaiting campaign and execute planning & MT5 queue submission.
