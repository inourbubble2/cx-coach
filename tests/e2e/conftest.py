"""E2E test fixtures for Playwright tests."""

import subprocess
import time
from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def streamlit_server() -> Generator[str, None, None]:
    """Start Streamlit server for E2E tests.

    Yields:
        Base URL of the Streamlit server
    """
    process = subprocess.Popen(
        [
            "uv",
            "run",
            "streamlit",
            "run",
            "app/interfaces/ui/main.py",
            "--server.port",
            "8599",
            "--server.headless",
            "true",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to start
    time.sleep(5)

    yield "http://localhost:8599"

    # Cleanup
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


@pytest.fixture(scope="session")
def base_url(streamlit_server: str) -> str:
    """Get base URL for tests."""
    return streamlit_server
