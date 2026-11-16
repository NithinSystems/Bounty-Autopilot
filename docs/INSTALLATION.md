# Installation — evidence collector

This guide applies only to the included GitHub evidence collector. It does not install the missing n8n discovery system.

## 1. Prerequisites

- A GitHub account and a repository where you have permission to configure Actions.
- Git.
- Python 3.10 or newer for local validator tests.
- Bash.
- Docker Engine available to the machine or runner that executes the collector.

On Windows, use WSL2 with Docker Engine integration or another supported Bash + Docker environment. Review Docker Desktop's current licensing terms if you use Docker Desktop for business purposes.

## 2. Prepare a repository

After the package has passed owner review:

1. Create a separate repository for the Community Edition. Suggested name: `bounty-autopilot-community`.
2. Copy the contents of this archive into that repository.
3. Keep the original private worker repository unchanged.
4. Ensure GitHub Actions are enabled for the new repository.
5. Do not add API keys, bot tokens, private IDs, or `.env` files.

The included workflow is `.github/workflows/verify-bounty.yml`. It has a `workflow_dispatch` trigger and requires no GitHub token input from the user. Its repository permission is read-only.

## 3. Run local tests

From the repository root:

```bash
python -m unittest discover -s tests -v
bash -n scripts/collect-evidence.sh
```

The tests validate the evidence document rules. The shell syntax check does not execute a bounty verification.

## 4. Run the GitHub Actions workflow

1. Open the repository's **Actions** tab.
2. Select **Verify bounty patch**.
3. Choose **Run workflow**.
4. Supply these values:

   - `repository_url`: public HTTPS GitHub URL, for example `https://github.com/OWNER/REPO`
   - `baseline_ref`: full 40-character commit SHA where the regression is present
   - `patched_ref`: full 40-character commit SHA containing the proposed fix
   - `bounty_id`: 1–64 letters, numbers, underscores, or hyphens

5. Start the run.
6. If verification succeeds, download the `evidence-<bounty_id>` artifact from the run summary.

## 5. What success means

The collector expects:

- the baseline test suite to fail,
- the patched test suite to pass,
- both suites to run at least one test,
- the test counts to match,
- evidence hashes and immutable commit references to validate.

A successful run is evidence for human review only. It is **not** proof of bounty eligibility, maintainer acceptance, reward availability, or permission to submit.

## 6. n8n status

There is no n8n JSON export in this archive. Do not import a placeholder. The original n8n instance and its export must be recovered separately before the full product can be installed by followers.
