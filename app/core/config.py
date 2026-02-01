"""Application settings using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project
    PROJECT_NAME: str = "cx-coach"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4.1-nano"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Supabase
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    # LangSmith (Optional)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str = "cx-coach"

    # FAQ Settings
    FAQ_CHUNK_SIZE: int = 500
    FAQ_CHUNK_OVERLAP: int = 50
    FAQ_COLLECTION_NAME: str = "faq_embeddings"
    FAQ_MAX_URL_CONTENT_SIZE: int = 10 * 1024 * 1024  # 10MB


settings = Settings()
