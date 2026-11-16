# Production gap analysis and implementation plan

Status: development in progress. This document is not a completion claim.

## Existing components

- Experimental GitHub radar and Algora-via-GitHub search; not a multi-platform production service.
- Inactive n8n starter: GitHub search, OpenAI-compatible model request and Telegram node; import tested, live provider and Telegram delivery unverified.
- Local SQLite tracker; user-entered statuses and local event history, not connected to n8n.
- GitHub evidence worker for a narrow Python unittest baseline/patch comparison; not an autonomous coding pipeline.
- Manual AI assistant instructions; no completed MCP server or dashboard.

## Ordered work and dependencies

1. Establish a persistent shared data model, migrations, canonical identity, provenance, durable jobs, event history and safe credential boundaries. Keep old tracker data readable.
2. Build an official-source GitHub adapter and fixture-backed contract tests; only add other platforms after verifying their current API, terms, authentication and fields. De-duplicate cross-posts only where evidence supports identity. Record unavailable fields as unknown.
3. Implement evidence-based verification for open status, deadlines, rewards and eligibility. Never infer funded or paid status without authoritative evidence; preserve the evidence and time.
4. Add bounded provider adapters with explicit budgets and validated structured outputs. Avoid unsupported claims of winning probability or guaranteed hourly earnings.
5. Add recoverable n8n orchestration and credential setup, with idempotent event processing and alerts only to the installer's chosen chat.
6. Create isolated execution jobs: clone only user-authorized public repositories, plan and test in a constrained environment, capture actual results, and retain the approval gate before publication or submission.
7. Integrate evidence, review, user-approved submission preparation, and platform-supported status/payment observation. Label user assertions separately from platform evidence.
8. Add an MCP server with authenticated access and explicit tool permissions. Test with a real compatible client. Add dashboard and installation guides after the underlying API is stable.
9. Run unit, integration and clean-install tests; run real provider and Telegram checks only with authorized credentials and an identified test recipient. Publish a versioned release only after gaps and licenses are resolved.

## Known blockers and constraints

- Platform API endpoints, access terms and funding evidence vary; no blanket adapter is claimed.
- Provider credentials and a test Telegram recipient are required for live verification. Mocks do not establish live operation.
- User-approved human action is required for public submission, legal terms, spending, and signing transactions.
- n8n has separate licensing terms; older repository source rights have not been established. The community-template folder has its own MIT license.
- A previous automatic approval review rejected an imported workflow execution citing possible Telegram message or data disclosure. Do not bypass that rejection.

## Current verification

The tracker migration and history tests use local SQLite fixtures. They do not prove n8n, platform, AI, Telegram, MCP, or cloud integration.

## GitHub-only increment

- Implemented read-only GitHub search to tracker import with source observations and advertised reward excerpts in `community-template/github_sync.py`. Two live read-only runs in a separate test database returned 100 inserts then 100 updates. This verifies search and deduplication for that snapshot only.
- Added conservative, fixture-tested stored-observation checks in `github_verify.py`. Funding, eligibility and claim status remain unknown; this does not refresh an issue live.
- The n8n workflow has not been connected to the tracker. AI scoring, Telegram, least-privilege approval, isolated coding, evidence integration and lifecycle end-to-end testing remain outstanding.
- The prior automatic-review rejection does not identify an exact node, permission or payload. The recorded details and safe constraints are in `community-template/GITHUB_DEVELOPMENT.md`.

## Increment 2 local prototype

Added local deterministic assessment, limited tracker event synchronization, a minimal unsent notification outbox, and self-declared local decision records. SQLite fixture tests cover duplicate assessments, missing reward, expired and suspicious candidates, failed notifications and rejected decisions. This is not AI scoring, an authenticated approval system, an n8n integration or live Telegram delivery. Earlier automatic-review rejection remains unresolved at the precise node/payload level; do not bypass it. See `community-template/GITHUB_DEVELOPMENT.md`.

## Local approval prototype update

Added passphrase-gated local decision-recording prototype and fixture tests. This is not a complete authenticated authorization flow: direct database/code access can bypass it, and no external action verifies decisions. Telegram remains disabled and untested; the user's conditional approval requires a completed authenticated flow and an identified private test chat.
