# Source manifest

This draft was assembled from the accessible private repository:

- Repository: `nithin-builds/bounty-autopilot-worker`
- Branch: `main`
- Source tree commit: `baab2a304082809667023de6d6d3d43ccb2ab45f`
- Included source files:
  - `.github/workflows/verify-bounty.yml`
  - `scripts/collect-evidence.sh`
  - `scripts/validate-evidence.py`
  - `scripts/write-evidence.py`
  - `tests/test_validate_evidence.py`
  - `.gitignore` (hardened for this draft)
- Intentionally excluded:
  - `.github/workflows/worker-heartbeat.yml` because it calls a private service endpoint and depends on private GitHub secrets.
  - The original n8n workflows because they were not available for inspection.
  - Mission Control dashboard code and private service configuration.

The included worker source is a snapshot of the owner's private repository. Review licensing and provenance before redistribution.
