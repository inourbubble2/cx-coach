"""Unit tests for Supabase client operations.

Tests use mocked Supabase client to avoid actual database calls.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain import (
    AnalysisHistorySummary,
    AnalysisResult,
    Conversation,
    Improvement,
    Scores,
    Turn,
)
from app.infrastructure.db.analysis_repository import (
    _db_to_domain,
    _domain_to_summary,
    delete_analysis,
    get_analysis,
    list_analyses,
    save_analysis,
)
from app.infrastructure.db.conversation_repository import (
    _db_to_domain as conv_db_to_domain,
)
from app.infrastructure.db.conversation_repository import (
    _domain_to_db as conv_domain_to_db,
)
from app.infrastructure.db.conversation_repository import (
    get_conversation,
    save_conversation,
)
from app.infrastructure.db.models.analysis import AnalysisResult as DBAnalysisResult
from app.infrastructure.db.models.conversation import Conversation as DBConversation


@pytest.fixture
def sample_result() -> AnalysisResult:
    """Create a sample AnalysisResult for testing."""
    return AnalysisResult(
        request_id="test-uuid-1234",
        analyzed_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        scores=Scores(
            clarification=8,
            empathy_tone=7,
            solution_accuracy=9,
            actionability=8,
            confirmation_closure=7,
            compliance_safety=8,
        ),
        total_score=78,
        strengths=["친절한 인사", "명확한 해결책 제시"],
        improvements=[
            Improvement(
                issue="공감 부족",
                original="네, 확인해보겠습니다.",
                suggested="아, 그러셨군요. 불편하셨겠습니다. 확인해보겠습니다.",
                reason="고객의 감정에 공감하면 신뢰가 높아집니다.",
            )
        ],
        overall_feedback="전반적으로 양호한 상담이었습니다.",
        is_resolved=True,
        csat_score=4,
    )


@pytest.fixture
def sample_db_row() -> DBAnalysisResult:
    """Create a sample database row for testing."""
    return DBAnalysisResult(
        request_id="test-uuid-1234",
        analyzed_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        clarification_score=8,
        empathy_tone_score=7,
        solution_accuracy_score=9,
        actionability_score=8,
        confirmation_closure_score=7,
        compliance_safety_score=8,
        total_score=78,
        strengths=["친절한 인사", "명확한 해결책 제시"],
        improvements=[
            {
                "issue": "공감 부족",
                "original": "네, 확인해보겠습니다.",
                "suggested": "아, 그러셨군요. 불편하셨겠습니다. 확인해보겠습니다.",
                "reason": "고객의 감정에 공감하면 신뢰가 높아집니다.",
            }
        ],
        overall_feedback="전반적으로 양호한 상담이었습니다.",
        is_resolved=True,
        csat_score=4,
    )


class TestDbToDomain:
    """Tests for _db_to_domain conversion."""

    def test_converts_db_to_domain(self, sample_db_row: DBAnalysisResult):
        """Should convert database model to AnalysisResult."""
        result = _db_to_domain(sample_db_row)

        assert result.request_id == "test-uuid-1234"
        assert result.scores.clarification == 8
        assert result.scores.empathy_tone == 7
        assert result.scores.solution_accuracy == 9
        assert result.scores.actionability == 8
        assert result.scores.confirmation_closure == 7
        assert result.scores.compliance_safety == 8
        assert result.total_score == 78
        assert len(result.strengths) == 2
        assert len(result.improvements) == 1
        assert result.improvements[0].issue == "공감 부족"
        assert result.is_resolved is True
        assert result.csat_score == 4


class TestDomainToSummary:
    """Tests for _domain_to_summary conversion."""

    def test_converts_to_summary(self):
        """Should convert domain data to AnalysisHistorySummary."""
        summary = _domain_to_summary(
            "test-uuid-1234", datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC), 78
        )

        assert summary.request_id == "test-uuid-1234"
        assert summary.total_score == 78
        assert summary.grade == "C"

    @pytest.mark.parametrize(
        "score,expected_grade",
        [
            (95, "A"),
            (90, "A"),
            (85, "B"),
            (80, "B"),
            (75, "C"),
            (70, "C"),
            (65, "D"),
            (60, "D"),
            (55, "F"),
            (0, "F"),
        ],
    )
    def test_grade_calculation(self, score: int, expected_grade: str):
        """Should calculate correct grade based on score."""
        summary = _domain_to_summary(
            "test-uuid", datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC), score
        )

        assert summary.grade == expected_grade


class TestSaveAnalysis:
    """Tests for save_analysis function."""

    @pytest.mark.asyncio
    async def test_saves_analysis_result(self, sample_result: AnalysisResult):
        """Should save analysis result to database."""
        mock_session = MagicMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            await save_analysis(sample_result)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()


class TestGetAnalysis:
    """Tests for get_analysis function."""

    @pytest.mark.asyncio
    async def test_returns_result_when_found(self, sample_db_row: DBAnalysisResult):
        """Should return AnalysisResult when found."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_db_row
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            result = await get_analysis("test-uuid-1234")

        assert result is not None
        assert result.request_id == "test-uuid-1234"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when analysis not found."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            result = await get_analysis("nonexistent-uuid")

        assert result is None


class TestListAnalyses:
    """Tests for list_analyses function."""

    @pytest.mark.asyncio
    async def test_lists_analyses_sorted_by_date(self):
        """Should list analyses sorted by date."""
        mock_session = MagicMock()
        mock_row = MagicMock()
        mock_row.request_id = "test-uuid-1234"
        mock_row.analyzed_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        mock_row.total_score = 78
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            results = await list_analyses(limit=50, sort_by="date")

        assert len(results) == 1
        assert isinstance(results[0], AnalysisHistorySummary)
        assert results[0].request_id == "test-uuid-1234"

    @pytest.mark.asyncio
    async def test_lists_analyses_sorted_by_score(self):
        """Should list analyses sorted by score."""
        mock_session = MagicMock()
        mock_row = MagicMock()
        mock_row.request_id = "test-uuid-1234"
        mock_row.analyzed_at = datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)
        mock_row.total_score = 78
        mock_result = MagicMock()
        mock_result.all.return_value = [mock_row]
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            results = await list_analyses(limit=50, sort_by="score")

        assert len(results) == 1
        assert results[0].total_score == 78

    @pytest.mark.asyncio
    async def test_respects_limit_parameter(self):
        """Should respect the limit parameter."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            results = await list_analyses(limit=25, sort_by="date")

        assert len(results) == 0


class TestDeleteAnalysis:
    """Tests for delete_analysis function."""

    @pytest.mark.asyncio
    async def test_returns_true_when_deleted(self):
        """Should return True when analysis is deleted."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            result = await delete_analysis("test-uuid-1234")

        assert result is True
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self):
        """Should return False when analysis not found."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.analysis_repository.get_session",
            mock_get_session,
        ):
            result = await delete_analysis("nonexistent-uuid")

        assert result is False


# ===== Conversation Repository Tests =====


@pytest.fixture
def sample_conversation() -> Conversation:
    """Create a sample Conversation for testing."""
    return Conversation(
        turns=[
            Turn(speaker="agent", message="안녕하세요, 무엇을 도와드릴까요?"),
            Turn(speaker="customer", message="배송 상태를 확인하고 싶습니다."),
            Turn(speaker="agent", message="주문번호를 알려주시겠어요?"),
        ],
        metadata={"source": "test"},
    )


@pytest.fixture
def sample_conversation_db_row() -> DBConversation:
    """Create a sample database row for testing."""
    test_id = uuid.uuid4()
    return DBConversation(
        id=test_id,
        created_at=datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC),
        turn_count=3,
        turns=[
            {"speaker": "agent", "message": "안녕하세요, 무엇을 도와드릴까요?"},
            {"speaker": "customer", "message": "배송 상태를 확인하고 싶습니다."},
            {"speaker": "agent", "message": "주문번호를 알려주시겠어요?"},
        ],
        metadata_={"source": "test"},
    )


class TestConversationDbToDomain:
    """Tests for conversation _db_to_domain conversion."""

    def test_converts_db_to_domain(self, sample_conversation_db_row: DBConversation):
        """Should convert database model to Conversation."""
        result = conv_db_to_domain(sample_conversation_db_row)

        assert result.id == sample_conversation_db_row.id
        assert result.created_at == sample_conversation_db_row.created_at
        assert len(result.turns) == 3
        assert result.turns[0].speaker == "agent"
        assert result.turns[0].message == "안녕하세요, 무엇을 도와드릴까요?"
        assert result.metadata == {"source": "test"}


class TestConversationDomainToDb:
    """Tests for conversation _domain_to_db conversion."""

    def test_converts_domain_to_db(self, sample_conversation: Conversation):
        """Should convert Conversation to database model."""
        result = conv_domain_to_db(sample_conversation)

        assert result.id is not None
        assert result.created_at is not None
        assert result.turn_count == 3
        assert len(result.turns) == 3
        assert result.turns[0]["speaker"] == "agent"
        assert result.metadata_ == {"source": "test"}

    def test_preserves_existing_id(self):
        """Should preserve existing id if provided."""
        existing_id = uuid.uuid4()
        conv = Conversation(
            id=existing_id,
            turns=[Turn(speaker="agent", message="Hello")],
        )
        result = conv_domain_to_db(conv)

        assert result.id == existing_id


class TestSaveConversation:
    """Tests for save_conversation function."""

    @pytest.mark.asyncio
    async def test_saves_conversation(self, sample_conversation: Conversation):
        """Should save conversation to database."""
        mock_session = MagicMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.conversation_repository.get_session",
            mock_get_session,
        ):
            result = await save_conversation(sample_conversation)

        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        assert result.id is not None


class TestGetConversation:
    """Tests for get_conversation function."""

    @pytest.mark.asyncio
    async def test_returns_conversation_when_found(
        self, sample_conversation_db_row: DBConversation
    ):
        """Should return Conversation when found."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_conversation_db_row
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.conversation_repository.get_session",
            mock_get_session,
        ):
            result = await get_conversation(sample_conversation_db_row.id)

        assert result is not None
        assert result.id == sample_conversation_db_row.id

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Should return None when conversation not found."""
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        async def mock_get_session():
            yield mock_session

        with patch(
            "app.infrastructure.db.conversation_repository.get_session",
            mock_get_session,
        ):
            result = await get_conversation(uuid.uuid4())

        assert result is None


class TestAnalysisConversationIdIntegration:
    """Tests for conversation_id field in AnalysisResult."""

    def test_db_to_domain_includes_conversation_id(
        self, sample_db_row: DBAnalysisResult
    ):
        """Should include conversation_id in domain model."""
        conv_id = uuid.uuid4()
        sample_db_row.conversation_id = conv_id

        result = _db_to_domain(sample_db_row)

        assert result.conversation_id == conv_id

    def test_db_to_domain_handles_null_conversation_id(
        self, sample_db_row: DBAnalysisResult
    ):
        """Should handle null conversation_id."""
        sample_db_row.conversation_id = None

        result = _db_to_domain(sample_db_row)

        assert result.conversation_id is None
