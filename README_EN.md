<div align="center">

**English** • [Русский](README.md)

</div>

# tg-voice-transcriber

A Telegram bot that automatically transcribes voice messages and video notes (circle videos) into text. Speech recognition runs entirely locally via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — no paid cloud API involved.

## Features

- Automatic transcription of `voice` messages and `video_note` circle videos
- Works in both private chats and groups (all voice messages in a group are transcribed automatically)
- Fully local speech recognition — no audio is sent to third-party services
- Whisper model is configurable via environment variable (`small` / `medium` / `large-v3`) without code changes
- Sequential job queue (single worker) to avoid overloading the server's CPU

## Stack

- Python 3.11, [aiogram 3](https://docs.aiogram.dev/)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2 + Whisper)
- ffmpeg — audio extraction from video notes
- Docker / Docker Compose

## Running

```bash
cp .env.example .env
# fill in BOT_TOKEN in .env (get one from @BotFather)
docker compose up -d --build
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | — | Bot token from @BotFather (required) |
| `WHISPER_MODEL` | `small` | Whisper model: `tiny`/`base`/`small`/`medium`/`large-v3` |
| `WHISPER_DEVICE` | `cpu` | `cpu` or `cuda` |
| `WHISPER_COMPUTE_TYPE` | `int8` | Compute type (`int8`, `float16`, `float32`) |
| `WHISPER_LANGUAGE` | (auto) | Language code (`ru`, `en`, ...); empty = auto-detect |

## Note on groups

For the bot to see all messages in a group (not just ones addressed to it), disable Privacy Mode: in [@BotFather](https://t.me/BotFather) → `Bot Settings` → `Group Privacy` → `Turn off`.

## License

MIT, see [LICENSE.md](LICENSE.md).
