# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] - 2026-07-04

### Added

- Initial release: aiogram bot transcribing `voice` and `video_note` messages via local faster-whisper
- Configurable Whisper model size via `WHISPER_MODEL` env var
- Single-worker asyncio queue for sequential transcription jobs
- Docker / Docker Compose deployment
