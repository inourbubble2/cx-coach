# CLAUDE.md - cx-coach

## Project Context
AI 기반 상담 코칭 및 품질 분석 시스템. 상담 대화/녹음을 분석하여 개선점을 도출하고 코칭 피드백을 생성합니다.

## Tech Stack
- **Runtime**: Python 3.12+
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **LLM**: LangChain 1.2.0+ / LangGraph (gpt-4o)
- **Evaluation**: RAGAs (LLM-as-a-judge)
- **STT**: OpenAI Whisper API
- **Embeddings**: text-embedding-3-small
- **Vector DB**: Supabase (pgvector)
- **Database**: Supabase (PostgreSQL)
- **Lint/Format**: Ruff
# Development
uv run uvicorn app.main:app --reload        # API 서버
uv run streamlit run app/ui/main.py         # Frontend

# Quality
uv run ruff check .                         # Lint
uv run ruff format .                        # Format
uv run pytest -x -v                         # Test (fail fast)
uv run pytest tests/unit/ -v                # Unit tests only
uv run pytest --cov=app --cov-report=term   # Coverage
```

## Architecture (Clean Architecture)
```
app/
├── domain/           # Entities, value objects, interfaces
├── application/      # Use cases, services, DTOs
├── infrastructure/   # DB, LLM clients, external APIs
│   ├── db/          # Supabase client
│   ├── llm/         # LangChain chains
│   └── stt/         # Whisper integration
└── interfaces/       # FastAPI routes, Streamlit UI
    ├── api/
    └── ui/
```

## Code Standards

### MUST (CI enforced)
- `async/await` for ALL I/O operations
- Pydantic v2 models for data validation
- Type hints on all function signatures
- Tests before merge (`pytest -x`)

### SHOULD
- LangChain LCEL syntax for chains
- RAGAs metrics for evaluation
- Dependency injection via FastAPI
- Loguru for logging (not print)

### NEVER
- Sync I/O in async context
- Raw SQL strings
- Hardcoded API keys
- `print()` statements

## Key Files
- `app/domain/models.py` - Core entities (Conversation, Turn, AnalysisResult)
- `app/application/analysis_service.py` - Main analysis orchestration
- `app/infrastructure/llm/analysis_chain.py` - LangChain analysis logic
- `app/infrastructure/db/supabase_client.py` - Database operations

## Testing Strategy
```bash
# 단일 테스트 선호 (전체 suite 대신)
pytest tests/unit/test_analysis.py::test_score_calculation -v

# 새 기능 = 새 테스트 필수
# tests/unit/ - 빠른 단위 테스트
# tests/integration/ - DB/API 연동 테스트
```

## Git Workflow
- Branch: `main`
- Commit: conventional commits (`feat:`, `fix:`, `test:`)
- PR 전: `ruff check . && ruff format . && pytest -x`

## Environment Variables
```
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...
LOG_LEVEL=DEBUG
```

## Gotchas
- LangChain: 1.2.0+ 필수 (LCEL 문법 변경)
- Streamlit: `app/ui/` 디렉토리에서만 실행

## 작업 원칙
1. 새로운 기능 구현 시, `docs/` 폴더를 탐색해서 관련 문서 확인
2. 기존 코드 패턴이 궁금하면 `app/` 내 유사 기능 코드 참고
