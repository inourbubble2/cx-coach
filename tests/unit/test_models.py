"""Unit tests for domain models."""

from datetime import UTC, datetime

import pytest

from app.domain import (
    AnalysisResult,
    Conversation,
    Improvement,
    Scores,
    Turn,
)


class TestTurn:
    """Tests for Turn model."""

    def test_turn_agent(self):
        turn = Turn(speaker="agent", message="안녕하세요")
        assert turn.speaker == "agent"
        assert turn.message == "안녕하세요"
        assert turn.timestamp is None

    def test_turn_customer(self):
        turn = Turn(speaker="customer", message="도움이 필요해요")
        assert turn.speaker == "customer"
        assert turn.message == "도움이 필요해요"

    def test_turn_with_timestamp(self):
        ts = datetime.now(UTC)
        turn = Turn(speaker="agent", message="네", timestamp=ts)
        assert turn.timestamp == ts

    def test_turn_invalid_speaker(self):
        with pytest.raises(ValueError):
            Turn(speaker="invalid", message="test")


class TestConversation:
    """Tests for Conversation model."""

    def test_conversation_basic(self):
        turns = [
            Turn(speaker="agent", message="안녕하세요"),
            Turn(speaker="customer", message="네"),
        ]
        conv = Conversation(turns=turns)
        assert conv.turn_count == 2

    def test_conversation_agent_turns(self):
        turns = [
            Turn(speaker="agent", message="안녕하세요"),
            Turn(speaker="customer", message="네"),
            Turn(speaker="agent", message="무엇을 도와드릴까요?"),
        ]
        conv = Conversation(turns=turns)
        assert len(conv.agent_turns) == 2
        assert all(t.speaker == "agent" for t in conv.agent_turns)

    def test_conversation_customer_turns(self):
        turns = [
            Turn(speaker="agent", message="안녕하세요"),
            Turn(speaker="customer", message="네"),
            Turn(speaker="customer", message="결제 문의요"),
        ]
        conv = Conversation(turns=turns)
        assert len(conv.customer_turns) == 2
        assert all(t.speaker == "customer" for t in conv.customer_turns)

    def test_conversation_with_metadata(self):
        turns = [Turn(speaker="agent", message="안녕하세요")]
        conv = Conversation(turns=turns, metadata={"source": "phone"})
        assert conv.metadata["source"] == "phone"


class TestScores:
    """Tests for Scores model with 6 dimensions."""

    def test_scores_valid(self):
        scores = Scores(
            clarification=8,
            empathy_tone=7,
            solution_accuracy=9,
            actionability=8,
            confirmation_closure=7,
            compliance_safety=8,
        )
        assert scores.clarification == 8
        assert scores.empathy_tone == 7
        assert scores.solution_accuracy == 9
        assert scores.actionability == 8
        assert scores.confirmation_closure == 7
        assert scores.compliance_safety == 8

    def test_scores_min_boundary(self):
        scores = Scores(
            clarification=1,
            empathy_tone=1,
            solution_accuracy=1,
            actionability=1,
            confirmation_closure=1,
            compliance_safety=1,
        )
        assert scores.clarification == 1

    def test_scores_max_boundary(self):
        scores = Scores(
            clarification=10,
            empathy_tone=10,
            solution_accuracy=10,
            actionability=10,
            confirmation_closure=10,
            compliance_safety=10,
        )
        assert scores.clarification == 10

    def test_scores_below_min(self):
        with pytest.raises(ValueError):
            Scores(
                clarification=0,
                empathy_tone=5,
                solution_accuracy=5,
                actionability=5,
                confirmation_closure=5,
                compliance_safety=5,
            )

    def test_scores_above_max(self):
        with pytest.raises(ValueError):
            Scores(
                clarification=11,
                empathy_tone=5,
                solution_accuracy=5,
                actionability=5,
                confirmation_closure=5,
                compliance_safety=5,
            )


class TestImprovement:
    """Tests for Improvement model."""

    def test_improvement(self):
        imp = Improvement(
            issue="공감 표현 부족",
            original="결제 오류가 발생했군요.",
            suggested="결제 오류로 불편을 드려 죄송합니다.",
            reason="사과와 공감을 먼저 표현하면 고객 만족도 향상",
        )
        assert imp.issue == "공감 표현 부족"
        assert "죄송합니다" in imp.suggested


class TestAnalysisResult:
    """Tests for AnalysisResult model."""

    @pytest.fixture
    def sample_result(self):
        return AnalysisResult(
            request_id="test-123",
            analyzed_at=datetime.now(UTC),
            scores=Scores(
                clarification=8,
                empathy_tone=7,
                solution_accuracy=9,
                actionability=8,
                confirmation_closure=7,
                compliance_safety=8,
            ),
            total_score=78,  # (8+7+9+8+7+8) / 60 * 100 ≈ 78
            strengths=["문제 파악력 우수", "친절한 응대"],
            improvements=[
                Improvement(
                    issue="공감 표현 부족",
                    original="확인해보겠습니다.",
                    suggested="불편을 드려 죄송합니다. 바로 확인해드리겠습니다.",
                    reason="공감 표현으로 고객 신뢰 향상",
                )
            ],
            overall_feedback="전반적으로 양호한 상담입니다.",
        )

    def test_analysis_result_basic(self, sample_result):
        assert sample_result.request_id == "test-123"
        assert sample_result.total_score == 78

    def test_analysis_result_grade_c(self, sample_result):
        assert sample_result.grade == "C"

    def test_analysis_result_grade_a(self):
        result = AnalysisResult(
            request_id="test",
            analyzed_at=datetime.now(UTC),
            scores=Scores(
                clarification=10,
                empathy_tone=10,
                solution_accuracy=10,
                actionability=10,
                confirmation_closure=10,
                compliance_safety=10,
            ),
            total_score=100,
            strengths=[],
            improvements=[],
            overall_feedback="",
        )
        assert result.grade == "A"

    def test_analysis_result_grade_b(self):
        result = AnalysisResult(
            request_id="test",
            analyzed_at=datetime.now(UTC),
            scores=Scores(
                clarification=8,
                empathy_tone=8,
                solution_accuracy=8,
                actionability=8,
                confirmation_closure=8,
                compliance_safety=8,
            ),
            total_score=80,
            strengths=[],
            improvements=[],
            overall_feedback="",
        )
        assert result.grade == "B"

    def test_analysis_result_grade_d(self):
        result = AnalysisResult(
            request_id="test",
            analyzed_at=datetime.now(UTC),
            scores=Scores(
                clarification=5,
                empathy_tone=5,
                solution_accuracy=5,
                actionability=5,
                confirmation_closure=5,
                compliance_safety=5,
            ),
            total_score=50,
            strengths=[],
            improvements=[],
            overall_feedback="",
        )
        assert result.grade == "F"

    def test_analysis_result_grade_f(self):
        result = AnalysisResult(
            request_id="test",
            analyzed_at=datetime.now(UTC),
            scores=Scores(
                clarification=3,
                empathy_tone=3,
                solution_accuracy=3,
                actionability=3,
                confirmation_closure=3,
                compliance_safety=3,
            ),
            total_score=30,
            strengths=[],
            improvements=[],
            overall_feedback="",
        )
        assert result.grade == "F"
