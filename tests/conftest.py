"""Pytest configuration and fixtures."""

from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """
    Mock authentication headers for protected endpoints.

    In integration tests, replace with actual Firebase token generation.
    """
    return {"Authorization": "Bearer mock-token"}


@pytest.fixture
def sample_thread() -> dict:
    """Sample thread data for testing."""
    return {
        "title": "Test Thread Title",
        "content": "This is the test thread content.",
    }


@pytest.fixture
def sample_comment() -> dict:
    """Sample comment data for testing."""
    return {
        "thread_id": "test-thread-id",
        "content": "This is a test comment.",
    }
