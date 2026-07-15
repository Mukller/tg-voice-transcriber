import asyncio
import contextlib
import logging
import signal
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

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    heartbeat_task = asyncio.create_task(_heartbeat_loop())
    polling_task = asyncio.create_task(dp.start_polling(bot))

    logger.info("Bot starting (whisper model=%s)", config.WHISPER_MODEL)
    await stop_event.wait()

    logger.info("Shutdown signal received, stopping polling and waiting for in-flight transcription...")
    heartbeat_task.cancel()
    await dp.stop_polling()
    polling_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await polling_task

    try:
        await asyncio.wait_for(transcriber.wait_idle(), timeout=config.SHUTDOWN_DRAIN_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        logger.warning("Timed out waiting for the transcription queue to drain")

    await bot.session.close()
    logger.info("Shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
