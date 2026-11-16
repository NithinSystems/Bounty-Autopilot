# Safety and privacy

## Human control

This Community Edition is an evidence collector, not an autonomous bounty applicant.

It must never automatically:

- claim or reserve a bounty;
- contact a maintainer or post a comment;
- create or push a branch;
- open, update, or submit a pull request;
- submit a solution or mark a bounty complete.

A human must verify the bounty and independently decide whether to proceed. A test pass is not submission approval.

## Execution isolation

The collector:

- accepts only public GitHub HTTPS repository URLs;
- requires immutable full commit SHAs;
- runs the test suite inside a pinned Python Docker image;
- uses no network inside the test container;
- mounts source read-only;
- uses a non-root UID, drops Linux capabilities, disables privilege escalation, and applies process, memory, CPU, and temporary-filesystem limits;
- rejects empty suites, passing baselines, failing patched runs, and evidence that claims submission readiness.

The workflow runner itself needs network access to clone the target repository and pull the pinned container image if it is not already present.

## Secrets and personal data

- No user credentials or API keys are required by the included manual verification workflow.
- Never commit `.env`, access tokens, private keys, cookies, wallet details, personal email addresses, or Telegram bot tokens.
- Do not paste secrets into bounty descriptions, test output, or issue logs.
- Review raw test logs before sharing them; they may contain paths, environment details, or test data.
- The internal heartbeat workflow from the private source repository is intentionally excluded because it targets a private service endpoint and depends on private repository secrets.

## Platform and bounty rules

Use only sources and APIs permitted by their operators. Respect rate limits, program scope, eligibility, deadlines, and disclosure rules. Do not perform unauthorized security testing. Advertised rewards and issue status can change; verify them at the source before spending time.

## Artifact retention

The included GitHub Actions workflow retains the evidence artifact for 30 days. Download and review it promptly; do not assume it is a permanent record.
