"""Tests for AI rate limiting."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status

from app.services.rate_limiter import RateLimitService

# Mock user for testing
TEST_USER_UID = "test_user_123"


@pytest.fixture
def mock_rate_limit_settings():
    """Mock settings with a low rate limit for testing."""
    with patch("app.services.rate_limiter.settings") as mock_settings:
        mock_settings.AI_DAILY_RATE_LIMIT = 5
        yield mock_settings


@pytest.fixture
def rate_limit_service(mock_rate_limit_settings):
    """Create a rate limit service instance with mocked settings."""
    service = RateLimitService()
    # Reset usage for clean state
    service._usage = {}
    return service


def test_rate_limit_service_basic(rate_limit_service):
    """Test basic service functionality."""
    user_id = "user1"
    
    # Initial check should pass
    assert rate_limit_service.check_limit(user_id) is True
    assert rate_limit_service.get_remaining_requests(user_id) == 5
    
    # Increment usage
    rate_limit_service.increment_usage(user_id)
    assert rate_limit_service.get_remaining_requests(user_id) == 4
    
    # Increment to limit
    for _ in range(4):
        rate_limit_service.increment_usage(user_id)
        
    # Limit reached
    assert rate_limit_service.get_remaining_requests(user_id) == 0
    assert rate_limit_service.check_limit(user_id) is False


def test_rate_limit_service_reset(rate_limit_service):
    """Test that limits reset on a new day."""
    user_id = "user1"
    
    # Use up the limit for "today"
    for _ in range(5):
        rate_limit_service.increment_usage(user_id)
    
    assert rate_limit_service.check_limit(user_id) is False
    
    # Mock _get_today_str to return tomorrow's date
    with patch.object(rate_limit_service, "_get_today_str", return_value="2099-01-01"):
        # Should be allowed now (limit reset)
        assert rate_limit_service.check_limit(user_id) is True
        assert rate_limit_service.get_remaining_requests(user_id) == 5
        
        # Incrementing starts fresh count
        rate_limit_service.increment_usage(user_id)
        assert rate_limit_service.get_remaining_requests(user_id) == 4


@pytest.mark.asyncio
async def test_rate_limit_endpoint_enforcement(authenticated_client):
    """Test rate limiting enforcement on API endpoints."""
    from app.main import app
    
    # Override the rate limit service dependency with one that has a limit of 2
    mock_service = RateLimitService()
    mock_service._limit = 2
    
    # Override dependency
    from app.api.deps import get_rate_limit_service
    app.dependency_overrides[get_rate_limit_service] = lambda: mock_service
    
    # Mock the summarizer chain to avoid real LLM calls
    with patch("app.api.v1.ai.summarizer.create_summarizer_chain") as mock_chain:
        mock_llm_chain = MagicMock()
        mock_llm_chain.ainvoke.side_effect = [{"text": "Summary 1"}, {"text": "Summary 2"}]
        # Need async mock for ainvoke result
        async def async_return(val):
            return val
        mock_chain.return_value.ainvoke.side_effect = [async_return({"text": "Summary 1"}), async_return({"text": "Summary 2"})]
                 
        # 1. First request - OK
        response = authenticated_client.post(
            "/api/v1/ai/summarize-thread",
            json={"content": "This is a test thread content that is long enough."},
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 2. Second request - OK
        response = authenticated_client.post(
            "/api/v1/ai/summarize-thread",
            json={"content": "This is a test thread content that is long enough."},
        )
        assert response.status_code == status.HTTP_200_OK
        
        # 3. Third request - Blocked (Limit exceeded)
        response = authenticated_client.post(
            "/api/v1/ai/summarize-thread",
            json={"content": "This is a test thread content that is long enough."},
        )
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "limit exceeded" in response.json()["detail"]
    
    # Clean up overrides
    app.dependency_overrides = {}
