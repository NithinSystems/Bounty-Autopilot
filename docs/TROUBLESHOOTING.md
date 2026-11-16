# Troubleshooting

## `docker: command not found` or daemon unavailable

Install and start Docker Engine on the runner or local machine. Confirm `docker info` works before running the collector.

## Baseline suite unexpectedly passes

The collector stops because it cannot demonstrate that the reported regression exists at the selected baseline commit. Recheck the issue and baseline SHA. Do not alter the test just to force a failure.

## Patched suite fails

The proposed revision has not passed the required test suite. Review the logs, patch, and environment. Do not treat the artifact as evidence of a successful fix.

## Zero tests detected

The repository may not use Python `unittest`, may have no discoverable tests, or may need dependencies. This collector currently supports only discoverable `unittest` suites that can run without downloading packages.

## Test counts differ

The validator requires the same number of tests in both runs. Check whether the patch added, removed, skipped, or renamed tests. Resolve the difference before relying on the evidence.

## Invalid commit SHA

Provide a full 40-character hexadecimal commit SHA for both baseline and patched revisions. Branch names and shortened SHAs are rejected.

## Repository URL rejected

Use a public GitHub HTTPS URL in the form `https://github.com/OWNER/REPO` (optional `.git`). Private repositories and other Git hosts are not supported by this version.

## No evidence artifact

The workflow uploads the artifact only after the collector has created the evidence directory. Check the failed step logs; a blocked run is not a successful verification.

## n8n or Telegram not working

Those integrations are not included in this archive. Recover the original n8n workflow export and implement/test the integration separately; do not infer that the evidence collector provides them.
