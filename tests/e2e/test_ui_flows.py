"""E2E tests for cx-coach Streamlit UI."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function")
def page_with_app(page: Page, base_url: str) -> Page:
    """Navigate to the app and wait for it to load."""
    page.goto(base_url)
    # Wait for Streamlit to fully load
    page.wait_for_selector("text=cx-coach", timeout=30000)
    return page


class TestPageLoad:
    """Tests for initial page load."""

    def test_title_displayed(self, page_with_app: Page) -> None:
        """Test that the main title is displayed."""
        expect(page_with_app.locator("h1")).to_contain_text("cx-coach")

    def test_subtitle_displayed(self, page_with_app: Page) -> None:
        """Test that the subtitle is displayed."""
        expect(page_with_app.get_by_text("AI 기반 상담 코칭")).to_be_visible()

    def test_tabs_exist(self, page_with_app: Page) -> None:
        """Test that all main tabs are visible."""
        expect(page_with_app.get_by_role("tab", name="파일 업로드")).to_be_visible()
        expect(page_with_app.get_by_role("tab", name="텍스트 입력")).to_be_visible()
        expect(page_with_app.get_by_role("tab", name="분석 이력")).to_be_visible()
        expect(page_with_app.get_by_role("tab", name="FAQ 관리")).to_be_visible()


class TestTextInputTab:
    """Tests for text input functionality."""

    def test_text_input_tab_content(self, page_with_app: Page) -> None:
        """Test text input tab shows expected elements."""
        # Click text input tab
        page_with_app.get_by_role("tab", name="텍스트 입력").click()

        # Check for text area
        expect(page_with_app.get_by_text("대화 직접 입력")).to_be_visible()

        # Check for sample text in textarea
        textarea = page_with_app.locator("textarea").first
        expect(textarea).to_be_visible()

    def test_sample_conversation_present(self, page_with_app: Page) -> None:
        """Test that sample conversation is pre-filled."""
        page_with_app.get_by_role("tab", name="텍스트 입력").click()

        textarea = page_with_app.locator("textarea").first
        content = textarea.input_value()

        assert "상담원:" in content
        assert "고객:" in content

    def test_analyze_button_exists(self, page_with_app: Page) -> None:
        """Test that analyze button is present."""
        page_with_app.get_by_role("tab", name="텍스트 입력").click()

        button = page_with_app.get_by_role("button", name="분석 시작")
        expect(button).to_be_visible()


class TestFileUploadTab:
    """Tests for file upload functionality."""

    def test_file_upload_tab_content(self, page_with_app: Page) -> None:
        """Test file upload tab shows expected elements."""
        # File upload is default tab
        expect(page_with_app.get_by_text("상담 파일 업로드")).to_be_visible()

    def test_supported_formats_shown(self, page_with_app: Page) -> None:
        """Test that supported file formats are displayed."""
        # Check for format text in the description
        expect(page_with_app.get_by_text("TXT", exact=True).first).to_be_visible()


class TestFAQManagementTab:
    """Tests for FAQ management functionality."""

    def test_faq_tab_content(self, page_with_app: Page) -> None:
        """Test FAQ management tab shows expected elements."""
        page_with_app.get_by_role("tab", name="FAQ 관리").click()

        # Should show FAQ upload section
        expect(page_with_app.get_by_text("FAQ 문서 업로드")).to_be_visible()


class TestAnalysisHistoryTab:
    """Tests for analysis history functionality."""

    def test_history_tab_content(self, page_with_app: Page) -> None:
        """Test analysis history tab shows expected elements."""
        page_with_app.get_by_role("tab", name="분석 이력").click()

        # Should show sort options
        expect(page_with_app.get_by_text("정렬 기준")).to_be_visible()

    def test_load_history_button_exists(self, page_with_app: Page) -> None:
        """Test that load history button is present."""
        page_with_app.get_by_role("tab", name="분석 이력").click()

        button = page_with_app.get_by_role("button", name="이력 불러오기")
        expect(button).to_be_visible()
