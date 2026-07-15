<div align="center">

[English](README_EN.md) • **Русский**

</div>

# tg-voice-transcriber

Telegram-бот для автоматической транскрибации голосовых сообщений и видео-кружков в текст. Работает полностью локально — распознавание речи выполняется на своём сервере через [faster-whisper](https://github.com/SYSTRAN/faster-whisper), без обращения к платным облачным API.

## Возможности

- Автоматическая транскрибация голосовых сообщений (`voice`) и видеосообщений-кружков (`video_note`)
- Работает как в личных чатах, так и в группах (все голосовые в группе транскрибируются автоматически)
- Локальное распознавание речи — без отправки аудио сторонним сервисам
- Модель Whisper настраивается через переменную окружения (`small` / `medium` / `large-v3`) без изменения кода
- Последовательная очередь задач (один воркер), чтобы не перегружать CPU сервера

## Стек

- Python 3.11, [aiogram 3](https://docs.aiogram.dev/)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2 + Whisper)
- ffmpeg — извлечение аудио из видео-кружков
- Docker / Docker Compose

## Запуск

```bash
cp .env.example .env
# заполнить BOT_TOKEN в .env (получить у @BotFather)
docker compose up -d --build
```

### Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `BOT_TOKEN` | — | Токен бота от @BotFather (обязательно) |
| `WHISPER_MODEL` | `small` | Модель Whisper: `tiny`/`base`/`small`/`medium`/`large-v3` |
| `WHISPER_DEVICE` | `cpu` | `cpu` или `cuda` |
| `WHISPER_COMPUTE_TYPE` | `int8` | Тип вычислений (`int8`, `float16`, `float32`) |
| `WHISPER_LANGUAGE` | (авто) | Код языка (`ru`, `en`, ...); пусто — автоопределение |
| `WHISPER_INITIAL_PROMPT` | (пусто) | Подсказка модели: имена, термины, специфичные слова — поднимает точность на бытовой речи |

## Важно для групп

Чтобы бот видел все сообщения в группе (а не только адресованные ему), нужно отключить Privacy Mode: в [@BotFather](https://t.me/BotFather) → `Bot Settings` → `Group Privacy` → `Turn off`.

## Лицензия

MIT, см. [LICENSE.md](LICENSE.md).
