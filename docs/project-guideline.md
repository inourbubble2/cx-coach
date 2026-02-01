# Project Guidelines: cx-coach

This document consolidates the Product Requirements Document (PRD) and Architecture Document for the `cx-coach` project. It serves as the single source of truth for understanding the project's goals, requirements, and technical implementation.

## 1. Project Overview

**cx-coach** is an AI-based Consultation Quality Analysis and Coaching System. It allows users to upload consultation logs or voice recordings, which are then analyzed by an LLM to provide multi-dimensional quality assessments, specific coaching feedback, and KPI reports.

## 2. User & Personas

### 2.1 Users
1.  **Consultation Manager (Team Leader)**: Needs to evaluate team performance, save time on manual monitoring, and track long-term growth.
2.  **Consultant (Agent)**: Needs immediate feedback, self-improvement, and objective performance tracking.

### 2.2 User Journey
- **Manager**: Upload team's logs -> Check Analysis Dashboard -> Conduct efficient coaching sessions.
- **Consultant**: Finish consultation -> Upload for self-check -> Receive immediate feedback -> Apply improvements to next call.

## 3. Functional Requirements

### 3.1 P1 - Must Have (MVP)
1.  **Conversation File Upload**:
    *   Support: TXT, CSV, JSON (max 10MB).
    *   Processing: < 2 sec.
2.  **Voice File Upload & STT**:
    *   Support: MP3, WAV, M4A, MP4, WebM (max 30 mins).
    *   Performance: 5-min audio processed in < 30 sec (Whisper API).
3.  **Consultation Quality Analysis**:
    *   **Input Processing**:
        *   TXT, CSV, JSON 등 대화 내역 파일 업로드
        *   LLM이 구조화된 Conversation으로 추출 (AI-based parsing)
        *   Audio 파일 (MP3, WAV, M4A, MP4, WebM)은 OpenAI Whisper를 사용해 STT
        *   STT된 내용을 LLM이 구조화된 Conversation으로 추출
    *   **Analysis Process**:
        *   LLM으로 Conversation의 상담 품질을 검사
        *   AI Analysis of 6 dimensions:
            1. **Clarification (문제 파악)**: 고객 문제 정확히 파악했는가
            2. **Empathy & Tone (공감/톤)**: 공감과 적절한 어조 사용
            3. **Solution Accuracy (해결 정확도)**: 정확한 해결책 제시
            4. **Actionability (구체성/실행 가능성)**: 구체적이고 실행 가능한 안내
            5. **Confirmation & Closure (확인/마무리)**: 이해 확인 및 적절한 마무리
            6. **Compliance & Safety (리스크/정책 준수)**: 정책 준수 및 위험 요소 관리
        *   Scoring: 1-10 scale per dimension, total normalized to 100.
        *   관련 FAQ가 있다면, similarity search하여 더 정확한 가이드라인 안내
        *   **FAQ Accuracy**: FAQ 컨텍스트가 제공된 경우 정확한 정보/오류 정보/누락 정보 분석
    *   **Output**: JSON format with strengths and improvements.
4.  **Coaching Feedback Generation**:
    *   Specific, actionable advice with "Before vs. After" examples.
5.  **Analysis Dashboard**:
    *   Visual charts, score breakdowns, MoM trends.
6.  **UI Requirements for Analysis**:
    *   버튼을 눌러서 바로 예시 입력을 할 수 있음
    *   분석 후 바로 결과를 볼 수 있음

1.  **Direct Text Input**
2.  **Conversation Persistence**:
    *   원본 대화 내용을 `conversations` 테이블에 저장
    *   분석 결과(`analysis_results`)와 대화(`conversations`)를 `conversation_id`로 연결
    *   분석 이력 조회 시 원본 대화 함께 확인 가능
    *   API: `GET /api/conversations/{id}`, `GET /api/history/{request_id}/conversation`
3.  **Analysis History/Storage (Supabase)**:
    *   분석 후 이력을 저장
    *   일간, 주간, 월간으로 통계를 볼 수 있음
    *   특정 range로 조회하여, 과거에 비해 개선점이 있는지도 볼 수 있음
4.  **FAQ RAG Integration**:
    *   **Upload Methods**:
        *   File upload: PDF, TXT files (max 10MB)
        *   URL input: Extracts text from web pages (HTML/plain text)
        *   Direct text input: TEXT 입력
    *   **Document Types**: WEB, FILE, TEXT로 구분
    *   **Table Architecture** (`faq_documents` and `faq_embeddings`):
        *   `faq_documents` stores metadata
        *   `faq_embeddings` stores vector embeddings
        *   Metadata includes: `document_id`, `filename`, `file_type`, `is_active`, `created_at`
    *   **Document Management**:
        *   Toggle active/inactive status per document (`toggle_faq_active()`)
        *   Only active documents are included in similarity search
        *   Delete documents and all associated chunks
    *   **Retrieval Flow**:
        *   `retrieval_node` in LangGraph extracts customer messages and searches relevant FAQs
        *   Uses `similarity_search()` with `only_active=True` filter
        *   Results formatted as `FAQContext` for LLM prompts
    *   **API Endpoints**:
        *   `POST /api/faq/file` - File upload
        *   `POST /api/faq/url` - URL upload
        *   `POST /api/faq/text` - Text input
        *   `GET /api/faq/list` - List documents
        *   `GET /api/faq/{id}` - Get document details (for preview)
        *   `PATCH /api/faq/{id}/status` - Toggle active status
        *   `PATCH /api/faq/{id}` - Update document content and re-embed
        *   `DELETE /api/faq/{id}` - Delete document
    *   **UI Requirements**:
        *   등록된 FAQ 조회 (미리보기) 가능
        *   FAQ의 콘텐츠를 수정하고, 수정된 콘텐츠를 바탕으로 재임베딩할 수 있음

### 3.3 P3 - Nice to Have
1.   **Team Dashboard**
2.   **Real-time Streaming Analysis**

## 4. Technical Architecture

### 4.1 Tech Stack
-   **Backend**: FastAPI (Async API)
-   **LLM Orchestration**: LangChain 1.2.0+ & LangGraph (Workflow state management)
-   **Models**: OpenAI GPT-4o (Analysis), Whisper (STT), text-embedding-3-small
-   **Database**: Supabase (PostgreSQL + pgvector)
-   **Frontend**: Next.js 14 (App Router), Tailwind CSS, Shadcn UI

### 4.2 High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                       Next.js UI                            │
│  (App Router, Dashboard, History, FAQ Pages)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                         │
│  (routes.py, faq_routes.py)                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Analysis   │ │     FAQ      │ │ Conversation │
│   Service    │ │   Service    │ │   Service    │
└──────┬───────┘ └──────┬───────┘ └──────────────┘
       │                │
       ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│  (retrieval_node → analysis_node → END)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌────────────┐ ┌────────────┐ ┌────────────┐
   │  OpenAI    │ │  Supabase  │ │  PgVector  │
   │  GPT-4o    │ │ PostgreSQL │ │  (RAG)     │
   │  Whisper   │ │            │ │            │
   └────────────┘ └────────────┘ └────────────┘
```

### 4.3 Component Design
**Clean Architecture Layers**:
```
app/
├── domain/           # 도메인 모델 (Conversation, AnalysisResult, FAQ)
├── application/      # 비즈니스 로직 (Services, LangGraph Agent)
│   ├── analysis_agent/   # LangGraph 기반 분석 워크플로우
│   ├── analysis_service.py
│   ├── conversation_service.py
│   └── faq_service.py
├── infrastructure/   # 외부 시스템 연동
│   ├── db/          # Supabase/PostgreSQL 레포지토리
│   ├── llm/         # LangChain 체인, 프롬프트
│   ├── stt/         # Whisper API 연동
│   └── vector_store/ # PgVector 연동
├── interfaces/       # 백엔드 인터페이스
│   └── api/         # FastAPI 라우터
└── ui/              # Next.js Frontend App
    ├── app/         # Pages & Routes
    ├── components/  # Reusable UI Components
    └── lib/         # API Client & Utils
```

### 4.4 Data Flow
1.  **Input**: File upload (TXT, CSV, JSON) or direct text input.
2.  **Parse (AI-based)**: LLM extracts conversation turns using Structured Output.
3.  **Analyze**: GPT-4o processes the conversation.
4.  **Generate**: Compute scores, format feedback.
5.  **Output**: Display on UI or download.

### 4.5 AI-based Conversation Parsing

규칙 기반 파싱은 MVP에서 제외하고, LLM Structured Output을 사용하여 다양한 형식의 대화 스크립트를 유연하게 처리합니다.

**Output Schema**:
```python
class Message(BaseModel):
    role: Literal["agent", "customer"]
    content: str

class Conversation(BaseModel):
    messages: list[Message]
```

**Implementation**:
- LangChain `with_structured_output()` 사용
- Model: GPT-4o-mini (비용 효율)
- Fallback: 파싱 실패 시 에러 반환 (MVP에서는 규칙 기반 파서 미구현)

## 5. Prompt Engineering

The system uses a structured system prompt to define the persona (15-year QA expert) and strict evaluation criteria (1-10 scale). The output is enforced as JSON by StructuredOutput in LangChain.

**Key Prompt Elements**:
-   **Persona**: Expert Post-call Analyst.
-   **Criteria**: Detailed definition of what constitutes a score of 1 vs 10 for each dimension.
-   **Output Format**: Strict JSON schema.

## 6. Non-Functional Requirements
-   **Performance**: Text analysis < 15s, Audio < 6x realtime speed.
-   **Security**: HTTPS, API keys in `.env`.

### 7. KPI Definitions & Collection Strategy

1.  **Resolution Rate (해결률)**
    *   **Definition**: 상담이 성공적으로 해결되었는지 여부.
    *   **Collection (PoC A안 - 추천)**: 분석 결과 화면에 '해결됨/미해결' 토글 제공. 상담사가 결과 확인 후 직접 체크 (`analysis_history.resolved = true/false`).
    *   **Collection (B안)**: 종료 인사말 감지 ("감사합니다", "해결되었습니다") 기반 자동 추정.

2.  **CSAT (고객 만족도)**
    *   **Definition**: 고객이 느끼는 만족도 (1-5점).
    *   **Collection**: 분석 결과 화면에 CSAT 입력(1~5) 옵션 제공 (`analysis_history.csat`). CRM 데이터 연동 전까지 수동 입력값 또는 모델 추정값을 사용.

3.  **Average Coaching Score (평균 코칭 점수)**
    *   **Definition**: 상담 품질 6대 항목(문제 파악, 공감/톤, 해결 정확도, 실행 가능성, 확인/마무리, 정책 준수)의 평균 점수.
    *   **Collection**: AI 자동 계산 (100점 만점 및 항목별 10점 만점). 기간별 평균 추이 추적.

4.  **FAQ Coverage (근거 자료 활용률)**
    *   **Definition**: AI가 분석 시 적절한 FAQ 문서를 얼마나 잘 찾아냈는지.
    *   **Collection**: 검색된 문서의 Similarity Score가 임계값(Threshold) 이상인 비율.
    *   **Extension**: "FAQ 도움됨" 체크박스를 통해 RAG 품질에 대한 인간 피드백(RLHF) 수집 가능.

5.  **Analysis Latency (응답 속도)**
    *   **Definition**: 요청 시작부터 분석 완료까지 걸린 시간.
    *   **Collection**: `finished_at - started_at`. P50/P95 지표로 모니터링하여 사용자 경험 관리.

## 8. Development Guidelines
-   Use **LangGraph** for managing the analysis workflow state.
-   **Supabase** is used for vector store (future RAG features) and storage.
-   Follow **FastAPI** best practices (dependency injection, Pydantic models).
