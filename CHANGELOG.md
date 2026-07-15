# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Transcripts now prefixed with 💬
- Deployed model switched to `medium` (CPU-only server, no GPU) for better accuracy
- Loudness normalization before transcription (ffmpeg `loudnorm`) so quiet voice messages recognize as well as loud ones — applied only to the copy fed to Whisper, not sent anywhere
- `WHISPER_INITIAL_PROMPT` env var to hint Whisper with names/terms it commonly mishears
- Edge-silence trimming (ffmpeg `silenceremove`) before transcription, on top of the VAD filter that already handles internal pauses
- Docker healthcheck via a heartbeat file the event loop touches every 20s
- Graceful shutdown: SIGTERM/SIGINT now stop accepting new messages and wait (up to 90s) for the in-flight transcription to finish instead of killing it mid-job

## [1.1.0] - 2026-07-07

### Added

- `/start` and `/help` commands
- Message splitting for transcripts longer than Telegram's 4096-char limit
- Self-calibrating ETA: the bot learns its actual real-time-factor from completed jobs (EMA) and uses that instead of a fixed guess, adapting automatically to server load
- Basic punctuation post-processing (capitalize sentence starts, add trailing period)
- Retry with backoff when downloading media from Telegram fails
- Log rotation (`json-file`, 10m x 3) in docker-compose

## [1.0.0] - 2026-07-04

### Added

- Initial release: aiogram bot transcribing `voice` and `video_note` messages via local faster-whisper
- Configurable Whisper model size via `WHISPER_MODEL` env var
- Single-worker asyncio queue for sequential transcription jobs
- Docker / Docker Compose deployment
