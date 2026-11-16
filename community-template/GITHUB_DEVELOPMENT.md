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

## Increment 2: local assessment and audit prototype

`assessment.py` adds SQLite tables `assessments`, `approval_decisions` and `notification_outbox` using CREATE TABLE IF NOT EXISTS. Existing opportunity and event tables are preserved. An assessment moves a discovered tracker record to scored once, records an assessment-sourced tracker event, and deduplicates identical assessment and outbox events. Verification observations may still accumulate on repeated assessments.

The score is a **local deterministic preliminary heuristic**, not AI. Its factors explicitly label unknown complexity, repository activity, eligibility, funding, claim status and deadline impact. No score establishes funded or eligible status. Threshold defaults to 60. The outbox contains only URL, score, confidence and generic reasons. Nothing sends or polls this outbox; failed and uncertain deliveries are recorded locally and are not retried automatically.

Approval records include event ID, candidate URL, proposed action, decision, self-declared approver, evidence text and UTC timestamp. These are local audit records only: the approver is not authenticated, and recording approval grants no authority and triggers no action. Do not put secrets or private data in evidence fields. No code execution or external submission is implemented.

From PowerShell in `community-template`, after syncing candidates, run tests:

```powershell
python -m unittest discover -s . -p "test_*.py" -v
```

To assess an existing URL, substitute your own URL:

```powershell
python -c "import tracker,assessment; d=tracker.connect('bounty-tracker.sqlite'); print(assessment.assess(d,'https://github.com/example/repo/issues/1')); d.close()"
```

Test categories: SQLite in-memory fixtures and mocked GitHub errors only. No n8n workflow was imported or executed in this increment; no live AI, Telegram or approval authentication test was performed.

### Previous approval rejection investigation

The recorded decision rejected execution of the imported Algora discovery workflow, citing a potential Telegram notification or workflow-data disclosure. The sanitized isolated copy contains schedule, manual trigger, disabled webhook, GitHub HTTP request, local gate/ingestion HTTP requests, condition and no-op nodes; it has no Telegram node or saved credential references. This establishes the visible copy's node types only. The review did not specify the exact rejected node, permission, destination or payload, so its cause remains unknown. We did not retry the rejected action. Existing n8n workflows and credentials were not modified.

**Blocked:** AI scoring, authenticated approval, n8n integration, Telegram delivery/retry and live end-to-end tests remain unimplemented. Do not expose this prototype to a network or use the local audit records to authorize execution.

## Passphrase-gated local decision prototype

`approval_auth.py` can create a local passphrase verifier using scrypt and records decisions only after the correct passphrase is supplied to that command. It adds the SQLite table `local_approval_credentials` without changing existing records. The passphrase is entered with hidden terminal input, not as a command-line argument.

This is **not an authenticated authorization boundary**: anyone with code or write access to the database can still call the older `assessment.decide` function or alter records. No workflow or external action checks these decisions. There is no account identity verification, rate limiting, recovery mechanism or remote authorization. Do not use it to authorize Telegram, code execution, submissions or financial actions. Do not expose it to a network.

In PowerShell, from `community-template`, run `python approval_auth.py --database bounty-tracker.sqlite setup` to configure it on a database you own. Back up the database and keep the passphrase private. Tests use temporary in-memory databases and do not configure a real passphrase.

Unchanged candidate observations now produce the same assessment/outbox fingerprint even if their observation timestamp changes. Repeated verification observations are still stored.

Live Telegram remains untested: the user authorized a test only after an authenticated approval flow is implemented and a private test chat is identified. Those conditions are not yet met.
