# Public release checklist

Do not publish this draft until every required item is resolved.

- [ ] Recover the original local n8n project and export the real discovery workflows.
- [ ] Confirm which workflows are active and which integrations are genuinely implemented.
- [ ] Remove all automatic-contact/comment behavior from the public edition.
- [ ] Confirm there is no auto-claim, auto-build, auto-push, auto-PR, or auto-submit path.
- [ ] Sanitize exported JSON: remove credential objects, credential IDs, private URLs, tokens, IDs, and user data.
- [ ] Test import into a clean n8n instance without touching the owner's existing instance.
- [ ] Test each enabled workflow with sample data and document exact source/API limits.
- [ ] Verify any AI provider's current free quota, paid fallback, and data handling terms.
- [ ] Wire Telegram only if desired; test alert-only behavior with a private test chat.
- [ ] Review source-platform terms, rate limits, eligibility checks, and permitted API/RSS access.
- [ ] Review all scripts, GitHub Actions, Docker image provenance, and third-party action pins.
- [ ] Run secret scanning and inspect all generated artifacts.
- [ ] Decide and add an explicit license. The private source repository had no license file in the inspected tree; do not assume an open-source license.
- [ ] Review README claims, screenshots, carousel, and DM copy for accuracy.
- [ ] Have the owner approve the final public repository and release.
