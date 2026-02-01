from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGEngine, PGVectorStore
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.infrastructure.db.database import get_database_url


def get_embeddings() -> OpenAIEmbeddings:
    """Get OpenAI embeddings instance."""
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )


async def get_vector_store() -> PGVectorStore:
    """Create a new PGVectorStore instance.

    Creates fresh engine and instance each time to avoid event loop
    conflicts in environments like Streamlit.

    Returns:
        PGVectorStore instance configured for the collection
    """
    # Create fresh engine for current event loop
    engine = create_async_engine(get_database_url(), pool_pre_ping=True)
    pg_engine = PGEngine.from_engine(engine=engine)
    embeddings = get_embeddings()

    vector_store = await PGVectorStore.create(
        engine=pg_engine,
        table_name="faq_embeddings",
        embedding_service=embeddings,
        id_column="id",
        content_column="content",
        embedding_column="embedding",
        metadata_columns=[
            "document_id",
            "is_active",
        ],
    )

    return vector_store


async def similarity_search(
    query: str,
    k: int = 5,
    only_active: bool = True,
) -> list[tuple[Document, float]]:
    """Perform similarity search on the vector store.

    Args:
        query: The search query text
        k: Number of results to return
        only_active: If True, only search active documents

    Returns:
        List of (Document, score) tuples sorted by relevance
    """
    vector_store = await get_vector_store()

    logger.debug(f"Performing similarity search for: {query[:50]}...")

    filter_dict = {"is_active": True} if only_active else None

    results = await vector_store.asimilarity_search_with_relevance_scores(
        query=query,
        k=k,
        filter=filter_dict,
    )

    logger.info(f"Found {len(results)} similar documents")
    return results


async def add_documents(
    documents: list[Document],
) -> list[str]:
    """Add documents to the vector store.

    Args:
        documents: List of LangChain Document objects to add

    Returns:
        List of document IDs
    """
    vector_store = await get_vector_store()

    logger.debug(f"Adding {len(documents)} documents to vector store")

    ids = await vector_store.aadd_documents(documents)

    logger.info(f"Added {len(ids)} documents")
    return ids


async def delete_documents(
    ids: list[str],
) -> None:
    """Delete documents from the vector store.

    Args:
        ids: List of document IDs to delete
    """
    vector_store = await get_vector_store()

    logger.debug(f"Deleting {len(ids)} documents from vector store")

    await vector_store.adelete(ids=ids)

    logger.info(f"Deleted {len(ids)} documents")
