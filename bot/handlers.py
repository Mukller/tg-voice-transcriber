import asyncio
import logging
import uuid
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from bot.config import config
from bot.text_utils import format_transcript, split_message
from bot.transcriber import extract_audio, transcriber

logger = logging.getLogger(__name__)

router_messages = F.voice | F.video_note

DOWNLOAD_RETRIES = 3
DOWNLOAD_RETRY_DELAY_SECONDS = 2


def _estimate_seconds(duration: int) -> int:
    factor = config.WHISPER_RTF_ESTIMATES.get(config.WHISPER_MODEL, 0.5)
    queued_ahead = transcriber.pending_jobs
    return max(1, round(duration * factor)) + queued_ahead * 5


async def _download_with_retry(bot: Bot, file_id: str, destination: Path) -> None:
    last_error: Exception | None = None
    for attempt in range(1, DOWNLOAD_RETRIES + 1):
        try:
            file = await bot.get_file(file_id)
            await bot.download_file(file.file_path, destination=str(destination))
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("Download attempt %s/%s failed: %s", attempt, DOWNLOAD_RETRIES, exc)
            if attempt < DOWNLOAD_RETRIES:
                await asyncio.sleep(DOWNLOAD_RETRY_DELAY_SECONDS * attempt)
    raise last_error  # type: ignore[misc]


async def handle_media(message: Message, bot: Bot) -> None:
    media = message.voice or message.video_note
    if media is None:
        return

    tmp_dir = Path(config.TMP_DIR)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex
    raw_path = tmp_dir / f"{job_id}.raw"
    wav_path = tmp_dir / f"{job_id}.wav"

    eta = _estimate_seconds(media.duration)
    status_msg = await message.reply(f"🎙 Распознаю... (ориентировочно ~{eta} сек)")

    try:
        await _download_with_retry(bot, media.file_id, raw_path)
        extract_audio(raw_path, wav_path)
        segments = await transcriber.transcribe(wav_path)
        text = format_transcript(segments)

        if not text:
            await status_msg.edit_text("⚠️ Не удалось распознать речь в сообщении.")
            return

        chunks = split_message(text)
        await status_msg.edit_text(chunks[0])
        for chunk in chunks[1:]:
            await message.answer(chunk)
    except Exception:
        logger.exception("Transcription failed")
        await status_msg.edit_text("⚠️ Ошибка при распознавании. Попробуйте ещё раз.")
    finally:
        raw_path.unlink(missing_ok=True)
        wav_path.unlink(missing_ok=True)


def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(handle_media, router_messages)
