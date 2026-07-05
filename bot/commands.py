from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.config import config

START_TEXT = (
    "🎙 Я транскрибирую голосовые сообщения и видео-кружки в текст.\n\n"
    "Просто пришли мне голосовое или кружок — отвечу текстом.\n"
    "В группах я тоже слышу голосовые (если добавлен в группу).\n\n"
    "/help — подробнее"
)

HELP_TEXT = (
    "Как пользоваться:\n"
    "1. Пришли voice-сообщение или видео-кружок — в личке или в группе.\n"
    "2. Я распознаю речь локально (модель Whisper: {model}) и пришлю текст в ответ.\n\n"
    "Для длинных сообщений (>10 мин) распознавание может занять минуту и больше — "
    "сообщения обрабатываются по одному, в порядке очереди."
).format(model=config.WHISPER_MODEL)


async def cmd_start(message: Message) -> None:
    await message.answer(START_TEXT)


async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


def register_commands(dp: Dispatcher) -> None:
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, Command("help"))
