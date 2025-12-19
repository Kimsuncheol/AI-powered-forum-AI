"""Tests for thread service."""

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.thread import ThreadCreate
from app.services import thread_service


@pytest.mark.asyncio
async def test_get_threads_returns_list():
    """Test that get_threads returns a list."""
    result = await thread_service.get_threads()
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_get_thread_not_found():
    """Test that get_thread raises NotFoundError for non-existent thread."""
    with pytest.raises(NotFoundError):
        await thread_service.get_thread("non-existent-id")


@pytest.mark.asyncio
async def test_create_thread():
    """Test thread creation returns proper structure."""
    thread_data = ThreadCreate(title="Test Title", content="Test content")
    result = await thread_service.create_thread(thread_data, "user-123")

    assert result.title == "Test Title"
    assert result.content == "Test content"
    assert result.author_id == "user-123"
