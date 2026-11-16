# AI / model setup

## Current verified package

The included evidence collector has **no AI model dependency** and makes no LLM calls. No model key, model provider, prompt, or AI scoring node is required to run it.

## Full Bounty Autopilot

The AI-assisted discovery/scoring workflows belong to the original n8n project, which was not accessible during this packaging run. Therefore:

- no AI model is configured by this Community Edition archive;
- no AI scoring feature is claimed as included;
- no provider key should be added to this package;
- any historic free-tier model choice must be rechecked against the provider's current terms, quotas, supported models, and regional availability before it is documented as a working free option.

When the n8n export is recovered, store provider credentials in n8n's credential manager. Do not hard-code keys in workflow JSON, `.env` examples, prompts, screenshots, GitHub Actions files, or logs.

AI output must be treated as a research aid, not authoritative proof. Verify the live bounty page, reward, eligibility, acceptance criteria, issue status, and platform rules independently.
