"""Whisper STT client for audio transcription.

Uses OpenAI's Whisper API to convert audio files to text.
"""

import os
from io import BytesIO

from loguru import logger
from openai import AsyncOpenAI

SUPPORTED_AUDIO_FORMATS = {"mp3", "wav", "m4a", "mp4", "webm", "ogg", "mpeg", "mpga"}
MAX_FILE_SIZE_MB = 25


def is_audio_file(filename: str) -> bool:
    """Check if a file is a supported audio format.

    Args:
        filename: The filename to check

    Returns:
        True if the file extension is a supported audio format
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    return ext in SUPPORTED_AUDIO_FORMATS


async def transcribe_audio(
    file_content: bytes,
    filename: str,
    language: str = "ko",
) -> str:
    """Transcribe audio file to text using OpenAI Whisper API.

    Args:
        file_content: Raw audio file bytes
        filename: Original filename with extension
        language: Language hint for transcription (default: Korean)

    Returns:
        Transcribed text from the audio

    Raises:
        ValueError: If file format is unsupported or file is too large
        RuntimeError: If transcription fails
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"지원하지 않는 오디오 형식입니다: {ext}. "
            f"지원 형식: {', '.join(sorted(SUPPORTED_AUDIO_FORMATS))}"
        )

    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(
            f"파일 크기가 {MAX_FILE_SIZE_MB}MB를 초과합니다: {file_size_mb:.1f}MB"
        )

    logger.info(f"Transcribing audio file: {filename} ({file_size_mb:.1f}MB)")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다")

    client = AsyncOpenAI(api_key=api_key)

    try:
        audio_file = BytesIO(file_content)
        audio_file.name = filename

        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="text",
        )

        transcript = response.strip() if isinstance(response, str) else str(response)

        logger.info(
            f"Transcription completed: {len(transcript)} characters, "
            f"~{len(transcript.split())} words"
        )

        return transcript

    except Exception as e:
        logger.error(f"Whisper transcription failed: {e}")
        raise RuntimeError(f"음성 변환 중 오류가 발생했습니다: {e}") from e
