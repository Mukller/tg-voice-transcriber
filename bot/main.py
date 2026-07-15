import asyncio
import logging
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.commands import register_commands
from bot.config import config
from bot.handlers import register_handlers
from bot.transcriber import transcriber

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def _heartbeat_loop() -> None:
    """Touch a file periodically so docker-compose's healthcheck can tell
    the event loop is still alive and responsive."""
    heartbeat_path = Path(config.HEARTBEAT_FILE)
    heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        heartbeat_path.touch()
        await asyncio.sleep(config.HEARTBEAT_INTERVAL_SECONDS)


async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    register_commands(dp)
    register_handlers(dp)
    transcriber.start()

    heartbeat_task = asyncio.create_task(_heartbeat_loop())

    logger.info("Bot starting (whisper model=%s)", config.WHISPER_MODEL)
    try:
        # aiogram installs its own SIGINT/SIGTERM handlers here and returns
        # once polling stops gracefully — no need to manage signals ourselves.
        await dp.start_polling(bot)
    finally:
        heartbeat_task.cancel()
        logger.info("Polling stopped, waiting for in-flight transcription to finish...")
        try:
            await asyncio.wait_for(transcriber.wait_idle(), timeout=config.SHUTDOWN_DRAIN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            logger.warning("Timed out waiting for the transcription queue to drain")
        await bot.session.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
