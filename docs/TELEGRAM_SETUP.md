# Telegram setup — optional future integration

## Current status

Telegram is **not connected** in the evidence collector included here. This document is a preparation guide only; it does not enable alerts by itself.

## Create a bot when the n8n workflow is restored

1. Open Telegram and start a chat with the official `@BotFather` account.
2. Use `/newbot` and follow its prompts.
3. Store the bot token in n8n Credentials (or another secret manager), not in a workflow field or committed file.
4. Add the bot to the intended private chat or group and send a test message.
5. Resolve the destination chat ID using Telegram's supported bot API flow. Keep the ID private.
6. Configure an alert-only n8n node after the discovery/review stage.
7. Send only the minimum useful data: bounty title, public source link, advertised reward with a verification label, and the review status.

## Safety

- Do not expose the bot token in screenshots, logs, exported workflow JSON, or GitHub.
- Do not send automatic claims, comments, applications, pull requests, or submissions through Telegram.
- Do not send private bounty information or personal data to a group.
- Test with a private chat first.

Until the original n8n workflow is recovered and the Telegram node is connected and tested, do not advertise Telegram notifications as a feature of this release.
