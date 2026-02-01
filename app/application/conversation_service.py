"""Service for creating and managing Conversation objects from various inputs."""

from loguru import logger

from app.domain import Conversation
from app.infrastructure.llm.conversation_parser import parse_conversation_with_llm
from app.infrastructure.stt import (
    SUPPORTED_AUDIO_FORMATS,
    is_audio_file,
    transcribe_audio,
)


async def create_from_audio(file_content: bytes, filename: str) -> Conversation:
    """Create conversation from audio file."""
    logger.info(f"Creating conversation from audio: {filename}")

    transcript = await transcribe_audio(file_content, filename)
    conversation = await parse_conversation_with_llm(transcript)
    logger.debug(f"Parsed {conversation.turn_count} turns from audio transcript")
    return conversation


async def create_from_file(file_content: bytes | str, filename: str) -> Conversation:
    """Create conversation from generic file."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if is_audio_file(filename):
        return await create_from_audio(file_content, filename)

    if ext in ("json", "csv", "txt", "text", "md"):
        # Rule-based Parsing을 추가할 수도 있으나, MVP에서 제외.
        content = (
            file_content.decode("utf-8")
            if isinstance(file_content, bytes)
            else file_content
        )
        conversation = await parse_conversation_with_llm(content)
        logger.debug(f"Parsed {conversation.turn_count} turns from file")
        return conversation
    else:
        supported = ", ".join(sorted(SUPPORTED_AUDIO_FORMATS))
        raise ValueError(
            f"지원하지 않는 파일 형식입니다: {ext}. "
            f"TXT, CSV, JSON, MD 또는 오디오({supported}) 형식을 사용하세요."
        )
