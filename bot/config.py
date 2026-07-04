import os


class Config:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
    WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
    WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE")  # None = auto-detect
    TMP_DIR = os.environ.get("TMP_DIR", "/tmp/tg-voice-transcriber")


config = Config()
