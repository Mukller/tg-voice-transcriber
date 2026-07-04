import asyncio
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

from bot.config import config

logger = logging.getLogger(__name__)


@dataclass
class TranscriptionJob:
    audio_path: Path
    future: asyncio.Future


class Transcriber:
    """Serializes all transcription work onto a single background worker
    so concurrent Whisper runs don't fight each other for CPU."""

    def __init__(self) -> None:
        self._model: WhisperModel | None = None
        self._queue: asyncio.Queue[TranscriptionJob] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None

    def _load_model(self) -> WhisperModel:
        if self._model is None:
            logger.info("Loading Whisper model=%s device=%s compute_type=%s",
                        config.WHISPER_MODEL, config.WHISPER_DEVICE, config.WHISPER_COMPUTE_TYPE)
            self._model = WhisperModel(
                config.WHISPER_MODEL,
                device=config.WHISPER_DEVICE,
                compute_type=config.WHISPER_COMPUTE_TYPE,
            )
        return self._model

    def start(self) -> None:
        self._worker_task = asyncio.create_task(self._worker_loop())

    async def _worker_loop(self) -> None:
        loop = asyncio.get_running_loop()
        while True:
            job = await self._queue.get()
            try:
                text = await loop.run_in_executor(None, self._transcribe_sync, job.audio_path)
                if not job.future.done():
                    job.future.set_result(text)
            except Exception as exc:  # noqa: BLE001
                if not job.future.done():
                    job.future.set_exception(exc)
            finally:
                self._queue.task_done()

    def _transcribe_sync(self, audio_path: Path) -> str:
        model = self._load_model()
        segments, _info = model.transcribe(
            str(audio_path),
            language=config.WHISPER_LANGUAGE,
            vad_filter=True,
        )
        return " ".join(segment.text.strip() for segment in segments).strip()

    async def transcribe(self, audio_path: Path) -> str:
        future: asyncio.Future = asyncio.get_running_loop().create_future()
        await self._queue.put(TranscriptionJob(audio_path=audio_path, future=future))
        return await future

    @property
    def pending_jobs(self) -> int:
        return self._queue.qsize()


def extract_audio(input_path: Path, output_path: Path) -> None:
    """Extract/convert media to 16kHz mono WAV via ffmpeg (needed for video notes)."""
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(input_path),
            "-ar", "16000", "-ac", "1",
            "-f", "wav", str(output_path),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode(errors='ignore')}")


transcriber = Transcriber()
