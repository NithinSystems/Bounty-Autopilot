# Bounty Autopilot — manual starter

**Preview:** A small n8n workflow with manual and daily triggers. It imports inactive. Searches GitHub issues with the bounty label, sends up to three public issue excerpts to your selected OpenAI-compatible API, and sends its reviews to your Telegram bot. This is not the full original Bounty Autopilot. It has not been verified with live provider or Telegram credentials.

## What you need

- An n8n instance, either self-hosted or n8n Cloud.
- An API key for an OpenAI-compatible chat completions endpoint and a model available on your account. Calls may cost money.
- Your own Telegram bot token and your private chat ID.
- Internet access. Your selected AI provider receives the public listing text.

## Install n8n

**Hosted:** Create an n8n Cloud account, set up your workspace and sign in. This option can be paid.

**Self-hosted:** Follow the official [Docker setup](https://docs.n8n.io/hosting/installation/docker/) and [security guidance](https://docs.n8n.io/hosting/securing/overview/). For internet-facing servers, configure HTTPS, authentication, backups, updates and a stable encryption key before using real credentials. The repository's localhost-only experimental setup is not a public cloud deployment. Check hosting costs and n8n licensing terms.

## Create your Telegram bot

1. In Telegram open [BotFather](https://t.me/BotFather), run /newbot and follow the prompts. Keep the token secret.
2. Open your new bot and press Start. The bot cannot start a private chat with you.
3. In n8n create a Telegram credential with that token.
4. To obtain your private chat ID, create a temporary Telegram Trigger using the same credential, run its test, send your bot a message and read `message.chat.id` from its output. Stop the test afterwards. Never paste your bot token in a public URL or into an AI chat.

## Import and configure

1. Download `bounty-starter.json` from this folder. In n8n, create a workflow and use **Import from File**. Keep it inactive while setting it up.
2. Open **AI review**. Set its URL to your provider's HTTPS chat-completions endpoint and replace `REPLACE_WITH_YOUR_MODEL` in the JSON body with a model your provider supports.
3. Create an n8n **Header Auth** credential. For a provider using bearer authentication, set header name `Authorization` and value `Bearer YOUR_API_KEY`. Select the credential in the AI node. Do not place the key in the workflow JSON or share exported credentials.
4. In the Telegram node select your Telegram credential and replace `REPLACE_WITH_YOUR_CHAT_ID` with your private numeric chat ID.
5. Use **Execute workflow** once. This sends up to three excerpts to your AI provider and up to three messages to your Telegram chat. Check API pricing and quotas first. A model error stops the run; review the node error and provider settings. After a successful test, activate the workflow only if you want it to run every 24 hours. Set the n8n workflow timezone and confirm the schedule.

The default URL is OpenAI's API. An API account/key and API billing or credits are separate from any ChatGPT subscription. Compatible gateways may be used with their own endpoint, key and model. Claude's native Messages API has a different schema: this template does **not** directly support it. Use a compatible gateway that explicitly supports Claude, or adapt the node before use. Local/open-source models need an accessible compatible API; `localhost` on n8n Cloud refers to n8n Cloud, not your computer.

## Limitations and safety

- GitHub results are candidates, not verified paid bounties. Algora, Polar and Superteam are not integrated into this starter.
- Results are untrusted text: verify payout, funding, rules, deadlines and eligibility yourself. AI scores are subjective.
- This starter has no deduplication, long-term queue, attachments or evidence validator integration. Activating it enables a 24-hour schedule, which can send duplicate messages and incur recurring charges. Keep it inactive until your manual test succeeds and you have checked your budget.
- It does not claim, comment, submit, push code, or run security scans. Keep all external submissions under human control.
- Workflow executions may contain issue text and AI output; manage retention and access in n8n.
- If any credential is exposed, revoke and replace it.

## Optional: track opportunities locally

Install Python 3 and open a terminal in the `community-template` folder:

```bash
python tracker.py add https://github.com/example/repo/issues/1 "Example task"
python tracker.py list
python tracker.py update https://github.com/example/repo/issues/1 reviewing --note "Checking eligibility"
```

Available states: discovered, reviewing, building, ready_for_review, submitted, accepted, rejected and paid. This is a **manual, local** tracker: it is not connected to the n8n workflow or platform accounts. Re-adding the exact same URL is ignored. Statuses and payment notes are user-reported, not independently verified; don't store secrets in notes. The database `bounty-tracker.sqlite` stays on your machine and must be backed up by you.

## Setup prompt for your coding assistant

> Help me set up the Bounty Autopilot manual starter from this repository. First ask whether I use n8n Cloud or self-hosted n8n and which OpenAI-compatible provider I selected. Inspect the current official n8n and provider docs, then guide me one step at a time. Do not ask me to paste secrets into chat. Explain that executing the workflow calls the AI API and sends Telegram messages, and ask me to run the first test myself. Do not expose a local n8n instance to the internet without HTTPS and authentication.

## License

The files in this folder are MIT licensed. Other parts of this repository have separate unresolved licensing status. n8n and other services have their own licenses and terms.
