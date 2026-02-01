# cx-coach

AI 기반 상담 코칭 및 품질 분석 시스템

## 기능

- 상담 대화/녹음/영상 분석
- 5개 영역 품질 평가 (인사, 경청, 문제파악, 해결제시, 마무리)
- FAQ RAG 기반으로 상담 내용에 대한 정확성을 검증함
- 구체적 근거와 함께 개선점 제시
- 우선순위별 코칭 피드백

## 요구사항

- Python 3.12+
- OpenAI API Key
- Supabase (PostgreSQL + pgvector)
- Next.js

## 설치

```bash
# uv 설치 (없는 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
uv sync
```

## 환경변수 설정

`.env` 파일을 생성하고 다음 변수를 설정하세요:

```env
# Required
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# Supabase (Optional - for cloud DB)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Optional
LOG_LEVEL=INFO
```

## 로컬 실행

```bash
# API 서버
uv run uvicorn app.main:app --reload

# Frontend (Next.js)
cd ui
npm run dev
```

## 테스트

```bash
# 전체 테스트
uv run pytest -x -v

# 단위 테스트만
uv run pytest tests/unit/ -v

# 커버리지
uv run pytest --cov=app --cov-report=term
```

## 코드 품질

```bash
# 린트
uv run ruff check .

# 포맷
uv run ruff format .
```

---

### Docker (Preferred)

```bash
# 로컬 개발 환경 (Frontend + API + DB)
docker compose up -d
```

서비스 URL:
- UI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Local DB: postgres://user:password@localhost:5432/cx-coach-db

### Local Development (Manual)

**1. API Server**
```bash
# 의존성 설치 및 실행
uv sync
uv run uvicorn app.main:app --reload
```

**2. Frontend (Next.js)**
```bash
cd ui
npm install
npm run dev
# 접속: http://localhost:3000
```
