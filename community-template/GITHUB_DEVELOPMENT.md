# GitHub-to-tracker development increment

This is an experimental read-only path. It is not yet connected to the n8n workflow, Telegram, an AI model or the coding worker.

## Run on Windows

1. Install Python 3 and download this repository. Open PowerShell in `community-template`.
2. Optional: set `$env:GITHUB_TOKEN` privately for a GitHub token with only the access required for public issue searches. A token is not required for public search, but unauthenticated limits apply. Never paste tokens in messages.
3. Run `python github_sync.py --database bounty-tracker.sqlite --pages 1`. Up to 10 pages can be requested with `--pages`. Each completed page is saved; if a later page fails, earlier pages remain saved.
4. Run `python tracker.py --database bounty-tracker.sqlite list` to inspect candidates. Each discovery stores the source URL, GitHub repository and issue, observation and discovery times, and an explicitly advertised reward quote when recognized. This is not proof of funding.

The tracker and discovery tables are created alongside existing records. Duplicate normalization uses the tracker; do not run multiple simultaneous discovery processes against the same database until concurrent ingestion has been tested.

## Verification

The `github_verify.verify(db, url)` function stores a separate verification observation with source URL and timestamps. It can flag closed issues, explicit ISO-format deadlines and selected suspicious text. It labels an open observation PARTIALLY_VERIFIED; the check reflects the stored observation time, not a real-time guarantee. It never asserts funding, eligibility or claim status from issue text. It is currently a Python interface, not an n8n integration.

## Test report

- Fixture tests cover deduplication, missing fields, pull requests, pagination, rate limit and network error, plus conservative verification of reward, eligibility, closed issues and deadlines.
- Live read-only GitHub search: first run inserted 100 search candidates into a separate test database; a second run updated 100 and inserted none. Results are not verified bounties.
- Live AI, Telegram, n8n orchestration, approval, isolated coding execution and end-to-end lifecycle tests have not been completed.

## Approval review investigation

The recorded rejection stated that executing the imported Algora discovery workflow could send an external Telegram notification or disclose workflow data. The review did not identify a specific node, permission or exact data flow. Do not infer the precise cause or rerun the rejected action by another route. The workflow's connection to Telegram has not been demonstrated. Future integration must separately document the target workflow graph, credential permissions, payload and human approval, and use an authorized test recipient for a live message.
