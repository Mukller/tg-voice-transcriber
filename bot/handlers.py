import logging
import uuid
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from bot.config import config
from bot.transcriber import extract_audio, transcriber

logger = logging.getLogger(__name__)

router_messages = F.voice | F.video_note


async def handle_media(message: Message, bot: Bot) -> None:
    media = message.voice or message.video_note
    if media is None:
        return

    tmp_dir = Path(config.TMP_DIR)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex
    raw_path = tmp_dir / f"{job_id}.raw"
    wav_path = tmp_dir / f"{job_id}.wav"

    status_msg = await message.reply("🎙 Распознаю...")

    try:
        file = await bot.get_file(media.file_id)
        await bot.download_file(file.file_path, destination=str(raw_path))
        extract_audio(raw_path, wav_path)
        text = await transcriber.transcribe(wav_path)

        if text:
            await status_msg.edit_text(text)
        else:
            await status_msg.edit_text("⚠️ Не удалось распознать речь в сообщении.")
    except Exception:
        logger.exception("Transcription failed")
        await status_msg.edit_text("⚠️ Ошибка при распознавании. Попробуйте ещё раз.")
    finally:
        raw_path.unlink(missing_ok=True)
        wav_path.unlink(missing_ok=True)


def register_handlers(dp: Dispatcher) -> None:
    dp.message.register(handle_media, router_messages)
