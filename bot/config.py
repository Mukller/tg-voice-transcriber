import os


class Config:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    WHISPER_MODEL = os.environ.get("WHISPER_MODEL", "small")
    WHISPER_DEVICE = os.environ.get("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE = os.environ.get("WHISPER_COMPUTE_TYPE", "int8")
    WHISPER_LANGUAGE = os.environ.get("WHISPER_LANGUAGE") or None  # None = auto-detect
    WHISPER_INITIAL_PROMPT = os.environ.get("WHISPER_INITIAL_PROMPT") or None
    TMP_DIR = os.environ.get("TMP_DIR", "/tmp/tg-voice-transcriber")
    HEARTBEAT_FILE = os.environ.get("HEARTBEAT_FILE", "/tmp/tg-voice-transcriber/.heartbeat")
    HEARTBEAT_INTERVAL_SECONDS = 20
    SHUTDOWN_DRAIN_TIMEOUT_SECONDS = 90

    # Rough real-time factor (processing seconds per audio second) per model,
    # used only to show a "estimated wait" hint to the user — not exact.
    WHISPER_RTF_ESTIMATES = {
        "tiny": 0.15, "base": 0.2, "small": 0.35, "medium": 0.7, "large-v3": 1.3,
    }


config = Config()
