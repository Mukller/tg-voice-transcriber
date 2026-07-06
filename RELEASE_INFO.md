# Release Info

## v1.1.0 — 2026-07-07

- `/start` and `/help` commands
- Message splitting for transcripts longer than Telegram's 4096-char limit
- Estimated wait time shown while transcribing, based on audio duration and queue depth
- Basic punctuation post-processing (capitalize sentence starts, add trailing period)
- Retry with backoff when downloading media from Telegram fails
- Log rotation (`json-file`, 10m x 3) in docker-compose

## v1.0.0 — 2026-07-04

Initial release.

- Telegram bot that automatically transcribes voice messages and video notes using local faster-whisper
- Works in private chats and groups
- Configurable Whisper model (`small` by default), no code changes needed to switch to `medium`/`large-v3`
- Deployed via Docker Compose
