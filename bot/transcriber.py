import asyncio
import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from faster_whisper import WhisperModel

from bot.config import config

logger = logging.getLogger(__name__)

EMA_ALPHA = 0.3  # weight of the newest observation; higher = adapts faster to load changes


@dataclass
class TranscriptionJob:
    audio_path: Path
    future: asyncio.Future


class Transcriber:
    """Serializes all transcription work onto a single background worker
    so concurrent Whisper runs don't fight each other for CPU.

    Also self-calibrates its processing-time estimate: after each job it
    compares actual wall-clock time against audio duration and updates a
    running real-time-factor (RTF) average, so the ETA shown to users
    reflects this server's actual speed (and current load) instead of a
    fixed guess.
    """

    def __init__(self) -> None:
        self._model: WhisperModel | None = None
        self._queue: asyncio.Queue[TranscriptionJob] = asyncio.Queue()
        self._worker_task: asyncio.Task | None = None
        self._rtf_ema: float | None = None
        self._avg_job_seconds: float | None = None

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
                segments, elapsed, duration = await loop.run_in_executor(
                    None, self._transcribe_sync, job.audio_path
                )
                self._record_observation(elapsed, duration)
                if not job.future.done():
                    job.future.set_result(segments)
            except Exception as exc:  # noqa: BLE001
                if not job.future.done():
                    job.future.set_exception(exc)
            finally:
                self._queue.task_done()

    def _transcribe_sync(self, audio_path: Path) -> tuple[list[str], float, float]:
        model = self._load_model()
        start = time.monotonic()
        segments, info = model.transcribe(
            str(audio_path),
            language=config.WHISPER_LANGUAGE,
            vad_filter=True,
        )
        texts = [segment.text.strip() for segment in segments if segment.text.strip()]
        elapsed = time.monotonic() - start
        return texts, elapsed, info.duration

    def _record_observation(self, elapsed: float, duration: float) -> None:
        if duration <= 0:
            return
        observed_rtf = elapsed / duration
        self._rtf_ema = (
            observed_rtf if self._rtf_ema is None
            else EMA_ALPHA * observed_rtf + (1 - EMA_ALPHA) * self._rtf_ema
        )
        self._avg_job_seconds = (
            elapsed if self._avg_job_seconds is None
            else EMA_ALPHA * elapsed + (1 - EMA_ALPHA) * self._avg_job_seconds
        )
        logger.info("Observed RTF=%.2f (elapsed=%.1fs, audio=%.1fs), EMA now %.2f",
                    observed_rtf, elapsed, duration, self._rtf_ema)

    async def transcribe(self, audio_path: Path) -> list[str]:
        future: asyncio.Future = asyncio.get_running_loop().create_future()
        await self._queue.put(TranscriptionJob(audio_path=audio_path, future=future))
        return await future

    def estimate_seconds(self, duration: float) -> int:
        """Estimate processing time for `duration` seconds of audio, using the
        learned RTF if we have enough observations, otherwise a static default
        for the configured model. Adds expected wait time for jobs already queued."""
        rtf = self._rtf_ema if self._rtf_ema is not None else config.WHISPER_RTF_ESTIMATES.get(
            config.WHISPER_MODEL, 0.5
        )
        own_estimate = duration * rtf
        queued_wait = self.pending_jobs * (self._avg_job_seconds or own_estimate)
        return max(1, round(own_estimate + queued_wait))

    @property
    def pending_jobs(self) -> int:
        return self._queue.qsize()


def extract_audio(input_path: Path, output_path: Path) -> None:
    """Extract/convert media to 16kHz mono WAV via ffmpeg (needed for video notes),
    normalizing loudness so quiet voice messages transcribe as well as loud ones.
    This only affects the copy fed to Whisper — nothing is sent back to the user."""
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(input_path),
            "-ar", "16000", "-ac", "1",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-f", "wav", str(output_path),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr.decode(errors='ignore')}")


transcriber = Transcriber()
