"""E2E tests for FAQ management functionality."""

import os
import tempfile

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="function")
def page_with_app(page: Page, base_url: str) -> Page:
    """Navigate to the app and wait for it to load."""
    page.goto(base_url)
    page.wait_for_selector("text=cx-coach", timeout=30000)
    return page


@pytest.fixture
def sample_faq_file() -> str:
    """Create a temporary FAQ file for testing."""
    content = """자주 묻는 질문 (FAQ)

Q: 배송은 얼마나 걸리나요?
A: 일반 배송은 2-3일, 빠른 배송은 익일 도착합니다.

Q: 반품은 어떻게 하나요?
A: 수령 후 7일 이내에 고객센터로 연락주시면 됩니다.

Q: 결제 수단은 어떤 것이 있나요?
A: 신용카드, 계좌이체, 카카오페이, 네이버페이를 지원합니다.

Q: 포인트는 어떻게 적립되나요?
A: 구매 금액의 1%가 자동 적립됩니다.
"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as f:
        f.write(content)
        return f.name


class TestFAQUpload:
    """Tests for FAQ document upload."""

    def test_faq_tab_shows_upload_section(self, page_with_app: Page) -> None:
        """Test FAQ tab displays upload options."""
        page = page_with_app

        # Go to FAQ management tab
        page.get_by_role("tab", name="FAQ 관리").click()

        # Should show file upload option
        expect(page.get_by_text("FAQ 파일 선택")).to_be_visible()

    def test_faq_tab_shows_url_input(self, page_with_app: Page) -> None:
        """Test FAQ tab displays URL input option."""
        page = page_with_app

        # Go to FAQ management tab
        page.get_by_role("tab", name="FAQ 관리").click()

        # Click on URL input tab
        page.get_by_role("tab", name="URL 입력").click()

        # Should show URL input section
        expect(page.get_by_text("URL에서 가져오기")).to_be_visible()

    def test_upload_faq_file(self, page_with_app: Page, sample_faq_file: str) -> None:
        """Test uploading a FAQ file."""
        page = page_with_app

        # Go to FAQ management tab
        page.get_by_role("tab", name="FAQ 관리").click()

        # Find file input and upload
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(sample_faq_file)

        # Wait for upload to process
        page.wait_for_timeout(2000)

        # Click upload button if visible
        upload_button = page.get_by_role("button", name="업로드")
        if upload_button.is_visible():
            upload_button.click()
            # Wait for success message
            page.wait_for_selector("text=성공", timeout=30000)

        # Cleanup
        os.unlink(sample_faq_file)

    def test_faq_list_section_exists(self, page_with_app: Page) -> None:
        """Test FAQ list section is visible."""
        page = page_with_app

        # Go to FAQ management tab
        page.get_by_role("tab", name="FAQ 관리").click()

        # Should show registered FAQ documents section
        expect(page.get_by_text("등록된 FAQ 문서")).to_be_visible()


class TestFAQDocumentList:
    """Tests for FAQ document list display."""

    def test_show_inactive_checkbox_exists(self, page_with_app: Page) -> None:
        """Test that inactive document filter exists."""
        page = page_with_app

        # Go to FAQ management tab
        page.get_by_role("tab", name="FAQ 관리").click()

        # Should have checkbox for showing inactive documents
        expect(page.get_by_text("비활성 문서 포함")).to_be_visible()

    def test_refresh_list_button_exists(self, page_with_app: Page) -> None:
        """Test refresh button exists for FAQ list."""
        page = page_with_app

        # Go to FAQ management tab
        page.get_by_role("tab", name="FAQ 관리").click()

        # Should have refresh button
        expect(page.get_by_role("button", name="새로고침")).to_be_visible()
