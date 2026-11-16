# Instagram carousel — honest preview of the Community Edition

## Slide 1 — Hook
I built a bounty evidence checker.
I'm preparing a free NithinSystems Community Edition.

## Slide 2 — The problem
A bounty idea is not enough.
You need reproducible evidence that a reported issue exists and that a proposed fix actually changes the result.

## Slide 3 — What the verified module does
- Checks a baseline commit
- Checks a proposed patched commit
- Runs Python `unittest`
- Compares the results
- Produces evidence logs and hashes

## Slide 4 — Isolation matters
The test suite runs in a restricted Docker container:
read-only source, no network, non-root user, and resource limits.

## Slide 5 — You stay in control
No automatic claims.
No maintainer comments.
No pushes or pull requests.
No bounty submissions.

## Slide 6 — Current supported scope
Public GitHub repositories with Python `unittest` suites that run without downloading dependencies during tests.

## Slide 7 — Transparent about what's next
The full n8n discovery export, AI scoring, and Telegram alerts are not in this preview package yet. I'm not pretending they are working in this release.

## Slide 8 — CTA
Want the free Community Edition when the complete, tested package is ready?

Comment **AUTOPILOT** and follow **@nithinsystems**.

Built by NithinSystems.
