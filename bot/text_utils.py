TELEGRAM_MESSAGE_LIMIT = 4096
SENTENCE_END = (".", "!", "?", "…")


def format_segment(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    if not text[0].isupper():
        text = text[0].upper() + text[1:]
    if not text.endswith(SENTENCE_END):
        text += "."
    return text


def format_transcript(segments: list[str]) -> str:
    return " ".join(format_segment(s) for s in segments if s.strip())


def split_message(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    """Split text into chunks that fit Telegram's message length limit,
    breaking on whitespace so words aren't cut mid-way."""
    if len(text) <= limit:
        return [text]

    chunks = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind(" ", 0, limit)
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at].strip())
        remaining = remaining[split_at:].strip()
    if remaining:
        chunks.append(remaining)
    return chunks
