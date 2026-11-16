# Test report

Generated: 2026-11-16

## Local checks

- Python unit tests: PASS
- Shell syntax (`bash -n`): PASS
- YAML validation: parsed successfully with PyYAML
- Secret-pattern scan: PASS — no matches

### Unit test output

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 718, in _warm_feature_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/spreadsheet_warmup.py", line 509, in _warm_drawing_and_image_flows
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/generated/interface/models.py", line 32861, in bring_to_front
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/remote.py", line 764, in __call__
  File "/tmp/tmp.QlpUkOUI9D/artifact_tool_v2-2.8.66/artifact_tool/rpc/client.py", line 175, in call
artifact_tool.rpc.client.RemoteError: Element ordering requires an owning element collection.
test_approval_forgery_blocked (test_validate_evidence.EvidenceTests.test_approval_forgery_blocked) ... ok
test_empty_suite_blocked (test_validate_evidence.EvidenceTests.test_empty_suite_blocked) ... ok
test_failed_patch_blocked (test_validate_evidence.EvidenceTests.test_failed_patch_blocked) ... ok
test_passing_baseline_blocked (test_validate_evidence.EvidenceTests.test_passing_baseline_blocked) ... ok
test_valid (test_validate_evidence.EvidenceTests.test_valid) ... ok

----------------------------------------------------------------------
Ran 5 tests in 19.786s

OK
```

### Shell syntax output

```text
(no output)
```

## Existing GitHub CI observation

The private worker repository's latest inspected readiness run completed successfully on 2026-11-15. The job steps `Run collector safety tests` and `Send readiness heartbeat` both reported success. This is an observation of the existing private repository, not a test of the missing n8n workflow.

## Environment availability

- Docker executable available in this packaging environment: no
- n8n CLI available in this packaging environment: no

The Python runner emitted a spreadsheet-runtime warmup warning before unittest discovery; the actual test process returned exit code 0 and all five tests passed.

## Not tested

- End-to-end Docker execution against a real bounty repository.
- A clean n8n import, because the original n8n workflow JSON was not available.
- AI scoring, source polling, Telegram delivery, or Mission Control integration; none is included in this archive.
- Public release, because no repository was published.

## Release blockers

1. Recover the original n8n workflows and export them.
2. Sanitize and test the n8n export in a clean isolated instance.
3. Confirm all automatic-contact paths are absent.
4. Select a license before public redistribution.
5. Complete the release checklist.


## Additional review — 16 November 2026

- Re-ran 5 validator unit tests and Bash syntax check: passed.
- Changed the collector to refuse existing `work/` or `evidence/` directories rather than delete them; verified refusal with a pre-existing directory.
- Real n8n workflows were located on the owner machine but depend on private local backend services. They are not included or portable yet.
- Docker end-to-end and clean n8n cloud import have not been verified in this review.
