---
name: langgraph-rag-patterns
description: 이 스킬은 LangGraph 기반 RAG(Retrieval-Augmented Generation) 에이전트 프로젝트의 표준 구조를 생성합니다.
---

# LangGraph RAG Agent 프로젝트 구조 스킬

이 스킬은 LangGraph 기반 RAG(Retrieval-Augmented Generation) 에이전트 프로젝트의 표준 구조를 생성합니다.

## 프로젝트 개요

- **프레임워크**: FastAPI + LangGraph + LangChain
- **데이터베이스**: PostgreSQL + pgvector (벡터 검색)
- **패키지 관리**: uv
- **아키텍처**: Clean Architecture + 의존성 주입

---

## 디렉토리 구조

```
project-name/
├── app/                                    # 메인 애플리케이션
│   ├── __init__.py
│   ├── main.py                            # FastAPI 진입점
│   │
│   ├── core/                              # 핵심 설정
│   │   ├── __init__.py
│   │   └── config.py                      # Pydantic Settings
│   │
│   ├── domain/                            # 도메인 레이어
│   │   ├── __init__.py
│   │   ├── entities/                      # 도메인 엔티티
│   │   │   ├── __init__.py
│   │   │   └── conversation.py            # 대화 엔티티
│   │   └── interfaces/                    # 추상 인터페이스 (Repository 등)
│   │       ├── __init__.py
│   │       └── repositories.py            # Repository 인터페이스
│   │
│   ├── application/                       # Application Layer
│   │   ├── __init__.py
│   │   ├── services/                      # 비즈니스 서비스
│   │   │   ├── __init__.py
│   │   │   └── analysis_service.py        # 분석 서비스
│   │   │
│   │   └── agent/                         # LangGraph 에이전트
│   │       ├── __init__.py
│   │       ├── agent.py                   # 에이전트 진입점
│   │       │
│   │       ├── graph/                     # 그래프 정의
│   │       │   ├── __init__.py
│   │       │   └── graph.py               # StateGraph 구성
│   │       │
│   │       └── nodes/                     # 그래프 노드들
│   │           ├── __init__.py
│   │           ├── rewriting.py           # 쿼리 리라이팅
│   │           ├── retrieval.py           # 벡터 검색
│   │           ├── generation.py          # 응답 생성
│   │           └── verification.py        # 응답 검증
│   │
│   ├── infrastructure/                    # 인프라 레이어
│   │   ├── __init__.py
│   │   │
│   │   ├── llm/                           # LLM 클라이언트
│   │   │   ├── __init__.py                # get_chat_model, get_embeddings 노출
│   │   │   ├── model.py                   # LLM 래퍼
│   │   │   └── embedding.py               # 임베딩 모델
│   │   │
│   │   ├── vector_store/                  # 벡터 스토어
│   │   │   ├── __init__.py
│   │   │   └── pg_vector_store.py         # PGVectorStore 설정
│   │   │
│   │   ├── db/                            # 데이터베이스
│   │   │   ├── __init__.py
│   │   │   ├── database.py                # SQLAlchemy 엔진/세션
│   │   │   └── models/                    # ORM 모델
│   │   │       ├── __init__.py
│   │   │       └── base.py                # Base 클래스
│   │   │
│   │   └── stt/                           # Speech-to-Text
│   │       ├── __init__.py
│   │       └── whisper_client.py          # Whisper API 클라이언트
│   │
│   └── interfaces/                        # 인터페이스 레이어 (Adapters)
│       ├── __init__.py
│       │
│       ├── api/                           # REST API
│       │   ├── __init__.py
│       │   ├── routes.py                  # 메인 라우터
│       │   └── endpoints/                 # 엔드포인트들
│       │       ├── __init__.py
│       │       ├── analysis.py            # 분석 API
│       │       └── faq.py                 # FAQ API
│       │
│       └── ui/                            # Streamlit UI
│           ├── __init__.py
│           ├── main.py                    # UI 진입점
│           └── components/                # UI 컴포넌트
│               └── __init__.py
│
├── alembic/                               # DB 마이그레이션
│   ├── env.py
│   └── versions/
│
├── tests/                                 # 테스트
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/                              # 단위 테스트
│   └── integration/                       # 통합 테스트
│
├── scripts/                               # 유틸리티 스크립트
│
├── pyproject.toml                         # 프로젝트 설정
├── uv.lock                                # 의존성 잠금
├── .env.example                           # 환경변수 템플릿
├── .pre-commit-config.yaml                # Pre-commit 훅
├── Dockerfile
├── docker-compose.yml
└── alembic.ini
```

---

## 핵심 파일 템플릿

### 1. pyproject.toml

```toml
[project]
name = "project-name"
version = "0.1.0"
description = "LangGraph RAG Agent"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    # Web Framework
    "fastapi>=0.115.0",
    "uvicorn>=0.32.0",

    # LangChain & LangGraph
    "langchain>=0.3.0",
    "langgraph>=0.2.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",

    # Vector Store
    "langchain-postgres>=0.0.12",
    "pgvector>=0.3.0",

    # Database
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.30.0",
    "psycopg2-binary>=2.9.0",
    "alembic>=1.14.0",

    # Settings
    "pydantic-settings>=2.6.0",

    # Logging
    "loguru>=0.7.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.7.0",
    "mypy>=1.13.0",
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=4.1.0",
    "pre-commit>=4.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 2. app/core/config.py

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project
    PROJECT_NAME: str = "RAG Agent"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Supabase (Optional)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    # LangSmith (Optional)
    LANGCHAIN_TRACING: bool = False
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str = "rag-agent"


settings = Settings()
```

### 3. app/infrastructure/llm/model.py

```python
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from app.core.config import settings


def get_chat_model() -> BaseChatModel:
    """ChatModel 인스턴스를 반환합니다."""
    return ChatOpenAI(
        model=settings.OPENAI_CHAT_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
```

### 4. app/infrastructure/llm/embedding.py

```python
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings

from app.core.config import settings


def get_embeddings() -> Embeddings:
    """Embedding 모델 인스턴스를 반환합니다."""
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
```

### 5. app/infrastructure/llm/__init__.py

```python
from app.infrastructure.llm.embedding import get_embeddings
from app.infrastructure.llm.model import get_chat_model

__all__ = ["get_chat_model", "get_embeddings"]
```

### 6. app/infrastructure/db/database.py

```python
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# 엔진 싱글톤
_engine = None
_session_factory = None


def get_database_url() -> str:
    """Build async database URL."""
    url = settings.DATABASE_URL
    # Convert postgres:// to postgresql+asyncpg://
    return url.replace("postgres://", "postgresql+asyncpg://").replace(
        "postgresql://", "postgresql+asyncpg://"
    )


def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Get an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session
```

### 7. app/infrastructure/db/models/base.py

```python
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """모든 모델의 기본 클래스"""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )
```

### 8. app/infrastructure/vector_store/pg_vector_store.py

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVectorStore

from app.core.config import settings
from app.infrastructure.db.database import get_engine


def get_embeddings() -> OpenAIEmbeddings:
    """Get OpenAI embeddings instance."""
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )


async def get_vector_store(
    collection_name: str = "faq_embeddings",
) -> PGVectorStore:
    """PGVectorStore 인스턴스를 반환합니다.
    
    Async Factory 패턴을 사용하여 비동기 엔진으로 초기화합니다.
    """
    engine = get_engine()
    embeddings = get_embeddings()

    return await PGVectorStore.create(
        engine=engine,
        embedding_service=embeddings,
        table_name="faq_embeddings",
        collection_name=collection_name,
        # Schema mapping
        id_column="id",
        content_column="content",
        embedding_column="embedding",
        metadata_columns=[
            "document_id",
            "is_active",
            # 필요한 메타데이터 컬럼 추가
        ],
        metadata_json_column="cmetadata",
        use_jsonb=True,
    )
```

### 9. app/application/analysis_agent/nodes/rewriting.py

```python
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.infrastructure.llm import get_chat_model
from app.domain.entities.agent import GraphState

SYSTEM_PROMPT = """당신은 사용자 쿼리를 벡터 검색에 최적화된 형태로 변환하는 전문가입니다.

규칙:
1. 대화체 필러 제거 (예: "안녕", "궁금해요")
2. 핵심 키워드와 엔티티 추출
3. 간결하고 명확하게 변환
4. 이미 명확한 쿼리는 그대로 반환

예시:
- "저 장학금 신청하고 싶은데 어떻게 해요?" → "장학금 신청 방법"
- "수강신청 기간이 언제부터야?" → "수강신청 기간"
"""


async def rewriting_node(state: GraphState) -> dict[str, Any]:
    """사용자 쿼리를 검색 최적화 형태로 변환합니다."""
    chat_model = get_chat_model()

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["user_query"]),
    ]

    response = await chat_model.ainvoke(messages)
    return {"rewritten_query": response.content}
```

### 10. app/application/analysis_agent/nodes/retrieval.py

```python
from typing import Any

from app.infrastructure.vector_store.pg_vector_store import get_vector_store
from app.domain.entities.agent import Reference, GraphState


async def retrieval_node(state: GraphState, k: int = 5) -> dict[str, Any]:
    """벡터 스토어에서 관련 문서를 검색합니다."""
    query = state.get("rewritten_query") or state["user_query"]
    vector_store = await get_vector_store()

    docs_with_scores = await vector_store.asimilarity_search_with_relevance_scores(
        query, k=k
    )

    references = [
        Reference(
            document_id=doc.metadata.get("document_id", 0),
            chunk_index=doc.metadata.get("chunk_index", 0),
            title=doc.metadata.get("title", ""),
            content=doc.page_content,
            url=doc.metadata.get("url"),
            score=score,
        )
        for (doc, score) in docs_with_scores
    ]

    return {"references": references}
```

### 11. app/application/analysis_agent/graph/graph.py

```python
from langgraph.graph import StateGraph, START, END

from app.domain.entities.agent import GraphState
from app.application.analysis_agent.nodes.rewriting import rewriting_node
from app.application.analysis_agent.nodes.retrieval import retrieval_node


def create_graph():
    """RAG 에이전트 그래프를 생성합니다."""
    workflow = StateGraph(GraphState)

    # 노드 추가
    workflow.add_node("rewriting", rewriting_node)
    workflow.add_node("retrieval", retrieval_node)
    # workflow.add_node("generation", generation_node)

    # 엣지 추가
    workflow.add_edge(START, "rewriting")
    workflow.add_edge("rewriting", "retrieval")
    # workflow.add_edge("retrieval", "generation")
    workflow.add_edge("retrieval", END)

    return workflow.compile()


graph = create_graph()
```

### 12. app/main.py

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.interfaces.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting {settings.PROJECT_NAME}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

### 13. .env.example

```env
# Project
DEBUG=false

# Database (PostgreSQL + pgvector)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Supabase (Optional)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# LangSmith (Optional)
LANGCHAIN_TRACING=false
LANGCHAIN_API_KEY=lsv2-...
LANGCHAIN_PROJECT=rag-agent
```

### 14. docker-compose.yml

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/dbname
    depends_on:
      - db
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

volumes:
  pgdata:
```

### 15. Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 16. .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]
        pass_filenames: false

      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]
        pass_filenames: false
```

---

## Clean Architecture 패턴

### 1. 레이어 구조

```mermaid
graph TD
    subgraph "Interfaces Layer (Adapters)"
        API[FastAPI Routes]
        UI[Streamlit UI]
    end

    subgraph "Application Layer"
        Services[Services]
        Agent[LangGraph Agent]
        Graph[StateGraph]
        Nodes[Nodes]
    end

    subgraph "Domain Layer"
        Entities[Entities]
        Interfaces[Repository Interfaces]
    end

    subgraph "Infrastructure Layer"
        LLM[LLM Clients]
        DB[Database]
        Vector[Vector Store]
        STT[STT Client]
    end

    subgraph "Core Layer"
        Config[Settings & Config]
    end

    API --> Services
    UI --> Services
    Services --> Agent
    Agent --> Graph
    Graph --> Nodes
    Nodes --> LLM
    Nodes --> Vector
    Services --> Interfaces
    Interfaces -.-> DB

    API -.-> Config
    Services -.-> Config
    LLM -.-> Config
```

각 레이어의 역할:

- **Interfaces Layer** (`app/interfaces/`): 외부와의 통신을 담당. REST API, UI 등.
- **Application Layer** (`app/application/`): 비즈니스 로직 조율. 서비스, LangGraph 에이전트.
- **Domain Layer** (`app/domain/`): 핵심 비즈니스 엔티티와 인터페이스. 외부 의존성 없음.
- **Infrastructure Layer** (`app/infrastructure/`): 외부 시스템 연동. DB, LLM, Vector Store 등.
- **Core Layer** (`app/core/`): 프로젝트 전역 설정.

### 2. 의존성 규칙

```
Interfaces → Application → Domain ← Infrastructure
                              ↑
                             Core
```

- 상위 레이어는 하위 레이어에 의존 가능
- 하위 레이어는 상위 레이어에 의존 불가
- Domain은 어떤 레이어에도 의존하지 않음
- Infrastructure는 Domain의 인터페이스를 구현

### 3. 의존성 주입 패턴

```python
# Factory 패턴 - 인스턴스 생성 함수
def get_chat_model() -> BaseChatModel:
    return ChatOpenAI(...)

# Async Context Manager - DB 세션
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

# FastAPI Depends 사용
@router.post("/analyze")
async def analyze(
    request: AnalysisRequest,
    session: AsyncSession = Depends(get_session),
):
    ...
```

### 4. LangGraph 노드 플로우

```mermaid
graph TD
    User((User Query)) --> Rewriting

    subgraph "RAG Agent Flow"
        Rewriting[Rewriting Node] -->|Rewritten Query| Retrieval[Retrieval Node]
        Retrieval -->|Context Documents| Generation[Generation Node]
        Generation -->|Draft Response| Verification[Verification Node]
    end

    Verification -->|Verified| End((End))
    Verification -->|Re-generate| Generation
```

- **Rewriting**: 사용자 쿼리를 검색에 최적화된 형태로 변환
- **Retrieval**: Vector Store에서 관련 문서 검색
- **Generation**: 검색된 문서를 바탕으로 답변 생성
- **Verification**: 생성된 답변 검증 및 환각 방지

---

## 프로젝트 초기화 명령어

```bash
# 1. 프로젝트 생성
mkdir project-name && cd project-name
uv init

# 2. 의존성 설치
uv add fastapi uvicorn langchain langgraph langchain-openai \
       langchain-postgres pgvector sqlalchemy asyncpg alembic pydantic-settings loguru

# 3. 개발 의존성
uv add --dev ruff mypy pytest pytest-asyncio pytest-cov pre-commit

# 4. Alembic 초기화
uv run alembic init alembic

# 5. Pre-commit 설정
uv run pre-commit install

# 6. 디렉토리 구조 생성 (Clean Architecture)
mkdir -p app/{core,domain/{entities,interfaces},application/{services,agent/{graph,nodes}},infrastructure/{llm,vector_store,db/models,stt},interfaces/{api/endpoints,ui/components}}

# 7. 환경 변수 설정
cp .env.example .env

# 8. 실행
uv run uvicorn app.main:app --reload
```

---

## 확장 가이드

### 새 노드 추가

1. `app/application/analysis_agent/nodes/` 에 노드 파일 생성
2. `GraphState`에 필요한 필드 추가
3. `graph.py`에서 노드 등록 및 엣지 연결

### 새 인프라 추가

1. `app/infrastructure/` 에 새 디렉토리 생성
2. Factory 함수 또는 Context Manager 패턴 적용
3. `__init__.py`에서 export

### 새 API 엔드포인트 추가

1. `app/interfaces/api/endpoints/` 에 라우터 파일 생성
2. `app/interfaces/api/routes.py`에서 라우터 등록

### 새 서비스 추가

1. `app/application/services/` 에 서비스 파일 생성
2. Domain 인터페이스를 통해 Infrastructure와 통신
