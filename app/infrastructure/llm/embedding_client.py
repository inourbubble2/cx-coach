"""OpenAI embedding client for FAQ vectorization.

Uses text-embedding-3-small model which produces 1536-dimensional vectors.
"""

from loguru import logger
from openai import AsyncOpenAI

from app.core.config import settings

EMBEDDING_DIMENSIONS = 1536
MAX_BATCH_SIZE = 100

_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Get or create the OpenAI client singleton."""
    global _client

    if _client is None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    return _client


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for multiple texts.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (1536 dimensions each)

    Raises:
        RuntimeError: If API key is not configured
        ValueError: If texts list is empty
    """
    if not texts:
        raise ValueError("texts list cannot be empty")

    logger.debug(f"Generating embeddings for {len(texts)} texts")

    client = _get_client()
    embeddings: list[list[float]] = []

    # Process in batches
    for i in range(0, len(texts), MAX_BATCH_SIZE):
        batch = texts[i : i + MAX_BATCH_SIZE]
        logger.debug(f"Processing batch {i // MAX_BATCH_SIZE + 1}: {len(batch)} texts")

        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=batch,
        )

        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)

    logger.info(f"Generated {len(embeddings)} embeddings")
    return embeddings


async def generate_single_embedding(text: str) -> list[float]:
    """Generate embedding for a single text.

    Args:
        text: Text string to embed

    Returns:
        Embedding vector (1536 dimensions)

    Raises:
        RuntimeError: If API key is not configured
        ValueError: If text is empty
    """
    if not text.strip():
        raise ValueError("text cannot be empty")

    logger.debug(f"Generating embedding for text of length {len(text)}")

    client = _get_client()

    response = await client.embeddings.create(
        model=settings.OPENAI_EMBEDDING_MODEL,
        input=text,
    )

    embedding = response.data[0].embedding

    logger.debug(f"Generated embedding with {len(embedding)} dimensions")
    return embedding
