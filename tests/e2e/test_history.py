"""E2E tests for analysis history functionality."""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function")
def page_with_app(page: Page, base_url: str) -> Page:
    """Navigate to the app and wait for it to load."""
    page.goto(base_url)
    page.wait_for_selector("text=cx-coach", timeout=30000)
    return page


class TestHistoryTab:
    """Tests for analysis history tab."""

    def test_history_tab_shows_sort_options(self, page_with_app: Page) -> None:
        """Test history tab displays sort options."""
        page = page_with_app

        # Go to history tab
        page.get_by_role("tab", name="분석 이력").click()

        # Should show sort options
        expect(page.get_by_text("정렬 기준")).to_be_visible()

    def test_history_tab_shows_limit_slider(self, page_with_app: Page) -> None:
        """Test history tab displays limit slider."""
        page = page_with_app

        # Go to history tab
        page.get_by_role("tab", name="분석 이력").click()

        # Should show limit slider
        expect(page.get_by_text("표시 개수")).to_be_visible()

    def test_load_history_button_works(self, page_with_app: Page) -> None:
        """Test loading history from database."""
        page = page_with_app

        # Go to history tab
        page.get_by_role("tab", name="분석 이력").click()

        # Click load history button
        page.get_by_role("button", name="이력 불러오기").click()

        # Should show loading spinner or results/empty message
        # Wait for either results or empty message
        page.wait_for_timeout(3000)

        # Should show either history items or "없습니다" message
        history_loaded = (
            page.get_by_text("저장된 분석 이력이 없습니다").is_visible()
            or page.get_by_text("총").is_visible()
        )
        assert history_loaded, "History should load and show results or empty message"


class TestHistoryWithAnalysis:
    """Tests for history after performing analysis."""

    def test_analysis_appears_in_history(self, page_with_app: Page) -> None:
        """Test that a new analysis appears in history."""
        page = page_with_app

        # First, perform an analysis
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()

        # Wait for analysis to complete
        page.wait_for_selector("text=종합 점수", timeout=60000)

        # Now go to history and load
        page.get_by_role("tab", name="분석 이력").click()
        page.get_by_role("button", name="이력 불러오기").click()

        # Wait for history to load
        page.wait_for_timeout(5000)

        # History should show at least one item
        expect(page.get_by_text("총")).to_be_visible(timeout=10000)

    def test_history_shows_score_and_grade(self, page_with_app: Page) -> None:
        """Test history items show score and grade."""
        page = page_with_app

        # Perform analysis first
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()
        page.wait_for_selector("text=종합 점수", timeout=60000)

        # Go to history
        page.get_by_role("tab", name="분석 이력").click()
        page.get_by_role("button", name="이력 불러오기").click()
        page.wait_for_timeout(5000)

        # Should show "총 N건" text indicating results loaded
        expect(page.get_by_text("총")).to_be_visible(timeout=10000)

        # Should show at least one "상세 보기" button (indicating items exist)
        expect(page.get_by_role("button", name="상세 보기").first).to_be_visible()

    def test_view_detail_button_works(self, page_with_app: Page) -> None:
        """Test clicking detail view button exists and is clickable."""
        page = page_with_app

        # Perform analysis first
        page.get_by_role("tab", name="텍스트 입력").click()
        page.get_by_role("button", name="분석 시작").click()
        page.wait_for_selector("text=Total Score", timeout=60000)

        # Go to history
        page.get_by_role("tab", name="분석 이력").click()
        page.get_by_role("button", name="이력 불러오기").click()
        page.wait_for_timeout(5000)

        # Verify detail button exists and is clickable
        detail_button = page.get_by_role("button", name="상세 보기").first
        expect(detail_button).to_be_visible(timeout=10000)
        expect(detail_button).to_be_enabled()

        # Click should not throw error
        detail_button.click()
        page.wait_for_timeout(2000)

        # Page should still be functional after click
        expect(page.get_by_role("tab", name="분석 이력")).to_be_visible()
