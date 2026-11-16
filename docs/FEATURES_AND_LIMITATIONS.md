# Features and limitations

| Capability | Status in this archive | Evidence / note |
|---|---|---|
| Manual GitHub Actions trigger | Included | `verify-bounty.yml` |
| Public GitHub repository input | Included | URL validation in collector |
| Immutable baseline and patched commit refs | Included | Full 40-character SHA validation |
| Python `unittest` execution | Included | Fixed command |
| Docker-isolated test execution | Included | Read-only mount, no network, non-root UID, dropped capabilities, resource limits |
| Evidence JSON and raw logs | Included | Evidence writer and Actions artifact |
| Evidence validation | Included | Five unit tests in source repository |
| Bounty discovery/source polling | Not included | Original n8n workflow not recovered |
| AI opportunity scoring | Not included | No model calls in this worker |
| Telegram notifications | Not included | No Telegram node or bot config in this worker |
| Mission Control dashboard | Not included | Private dashboard is not packaged |
| Solution generation/building | Not included | Separate system, not in this repo |
| Automatic contact/comments/claims | Prohibited for this edition | Human review only |
| Pushes, pull requests, submissions | Prohibited for this edition | Separate explicit human approval required |

## Important limitations

- Only public GitHub HTTPS repositories are accepted.
- The test command is fixed to `python -m unittest discover`.
- Test suites must not require network access or downloading dependencies while running.
- A passing baseline is rejected because the regression has not been demonstrated.
- A failing patched run is rejected.
- Equal test counts are required.
- A successful collector run does not guarantee correctness outside the tested suite.
- Bounty eligibility, reward availability, acceptance criteria, deadlines, and platform terms must be verified by a person.
