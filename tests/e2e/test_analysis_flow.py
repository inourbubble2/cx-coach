"""E2E tests for analysis functionality."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function")
def page_with_app(page: Page, base_url: str) -> Page:
    """Navigate to the app and wait for it to load."""
    page.goto(base_url)
    page.wait_for_selector("text=cx-coach", timeout=30000)
    return page


class TestTextAnalysis:
    """Tests for text-based conversation analysis."""

    def test_analyze_sample_conversation(self, page_with_app: Page) -> None:
        """Test analyzing the sample conversation returns results."""
        page = page_with_app

        # Go to text input tab
        page.get_by_role("tab", name="텍스트 입력").click()

        # Sample conversation should already be filled
        textarea = page.locator("textarea").first
        content = textarea.input_value()
        assert "상담원:" in content, "Sample conversation should be pre-filled"

        # Click analyze button
        page.get_by_role("button", name="분석 시작").click()

        # Wait for analysis to complete - check for metric label
        page.wait_for_selector("text=Total Score", timeout=60000)

        # Verify analysis result sections appear
        expect(page.get_by_text("Total Score")).to_be_visible()

    def test_analysis_shows_scores(self, page_with_app: Page) -> None:
        """Test that analysis displays all score categories."""
        page = page_with_app

        # Go to text input tab and analyze
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()

        # Wait for results
        page.wait_for_selector("text=종합 점수", timeout=60000)

        # Check score categories are displayed (use first match)
        expect(page.get_by_text("인사/첫인상").first).to_be_visible()
        expect(page.get_by_text("경청/공감").first).to_be_visible()
        expect(page.get_by_text("문제 파악").first).to_be_visible()
        expect(page.get_by_text("해결 제시").first).to_be_visible()
        expect(page.get_by_text("마무리").first).to_be_visible()

    def test_analysis_shows_feedback(self, page_with_app: Page) -> None:
        """Test that analysis displays strengths and improvements."""
        page = page_with_app

        # Go to text input tab and analyze
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()

        # Wait for results
        page.wait_for_selector("text=분석 결과", timeout=60000)

        # Check feedback sections
        expect(page.get_by_text("잘한 점")).to_be_visible()
        expect(page.get_by_text("종합 코멘트")).to_be_visible()
        expect(page.get_by_text("개선 포인트")).to_be_visible()

    def test_analysis_shows_grade(self, page_with_app: Page) -> None:
        """Test that analysis displays a grade (A-F)."""
        page = page_with_app

        # Go to text input tab and analyze
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()

        # Wait for results
        page.wait_for_selector("text=분석 결과", timeout=60000)

        # Check grade is displayed (Grade: A, B, C, D, or F)
        expect(page.get_by_text("Grade:")).to_be_visible()

    def test_json_download_available(self, page_with_app: Page) -> None:
        """Test that JSON download button appears after analysis."""
        page = page_with_app

        # Go to text input tab and analyze
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()

        # Wait for results
        page.wait_for_selector("text=분석 결과", timeout=60000)

        # Check download button exists
        expect(page.get_by_role("button", name="JSON 다운로드")).to_be_visible()

    def test_custom_conversation_analysis(self, page_with_app: Page) -> None:
        """Test analyzing a custom conversation."""
        page = page_with_app

        # Go to text input tab
        page.get_by_role("tab", name="텍스트 입력").click()

        # Clear and enter custom conversation
        textarea = page.locator("textarea").first
        textarea.fill("""상담원: 안녕하세요, 고객센터입니다.
고객: 제품이 고장났어요.
상담원: 불편을 드려 죄송합니다. 어떤 제품인가요?
고객: 세탁기요.
상담원: 네, 세탁기 고장이시군요. 증상을 말씀해주시겠어요?
고객: 전원이 안 켜져요.
상담원: 전원 문제시군요. 먼저 콘센트 연결 상태를 확인해주시겠어요?
고객: 확인했는데 잘 연결되어 있어요.
상담원: 그렇다면 기사님 방문이 필요할 것 같습니다. 내일 오전 방문 가능하신가요?
고객: 네, 가능해요.
상담원: 내일 오전 10시로 예약해드렸습니다. 다른 궁금한 점 있으신가요?
고객: 아니요, 감사합니다.
상담원: 감사합니다. 좋은 하루 되세요.""")

        # Click analyze
        page.get_by_role("button", name="분석 시작").click()

        # Wait for results
        page.wait_for_selector("text=분석 결과", timeout=60000)

        # Verify results appear
        expect(page.get_by_text("종합 점수")).to_be_visible()


class TestEmptyInputValidation:
    """Tests for input validation."""

    def test_empty_text_shows_warning(self, page_with_app: Page) -> None:
        """Test that empty text input shows a warning."""
        page = page_with_app

        # Go to text input tab
        page.get_by_role("tab", name="텍스트 입력").click()

        # Clear the textarea
        textarea = page.locator("textarea").first
        textarea.fill("")

        # Click analyze
        page.get_by_role("button", name="분석 시작").click()

        # Should show warning
        expect(page.get_by_text("대화 내용을 입력해주세요")).to_be_visible()
