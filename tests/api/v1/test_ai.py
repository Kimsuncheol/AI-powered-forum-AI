"""Unit tests for AI endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.api.deps import CurrentUser
from app.core.firebase import verify_firebase_token


@pytest.fixture
def mock_chain():
    """Mock AI chain."""
    chain = AsyncMock()
    chain.ainvoke.return_value = {"text": "Mock AI response"}
    return chain


@pytest.mark.asyncio
@patch("app.api.v1.ai.summarizer.create_summarizer_chain")
async def test_summarize_thread_success(mock_chain, authenticated_client):
    """Test successful thread summarization."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "This is a summary."}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/summarize-thread",
        json={"content": "This is a long thread content that needs summarization."},
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["summary"] == "This is a summary."


@pytest.mark.asyncio
async def test_summarize_thread_content_too_long(authenticated_client):
    """Test that content exceeding max length is rejected."""
    # Create content exceeding 50,000 characters
    long_content = "a" * 50001
    
    response = authenticated_client.post(
        "/api/v1/ai/summarize-thread",
        json={"content": long_content},
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_summarize_thread_content_too_short(authenticated_client):
    """Test that content below minimum length is rejected."""
    response = authenticated_client.post(
        "/api/v1/ai/summarize-thread",
        json={"content": "short"},
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_summarize_thread_unauthorized(client):
    """Test that unauthorized requests are rejected."""
    response = client.post(
        "/api/v1/ai/summarize-thread",
        json={"content": "Some content"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@patch("app.api.v1.ai.summarizer.create_summarizer_chain")
async def test_summarize_thread_chain_error(mock_chain, authenticated_client):
    """Test error handling when LangChain fails."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.side_effect = Exception("OpenAI API error")
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/summarize-thread",
        json={"content": "Some content to summarize"},
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "failed" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("app.api.v1.ai.qa_chain.create_qa_chain")
async def test_qa_success(mock_chain, authenticated_client):
    """Test successful Q&A."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "The answer is 42."}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/qa",
        json={
            "context": "The meaning of life is 42.",
            "question": "What is the meaning of life?",
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["answer"] == "The answer is 42."


@pytest.mark.asyncio
async def test_qa_question_too_long(authenticated_client):
    """Test that overly long questions are rejected."""
    long_question = "a" * 1001
    
    response = authenticated_client.post(
        "/api/v1/ai/qa",
        json={
            "context": "Some context here",
            "question": long_question,
        },
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_qa_context_too_long(authenticated_client):
    """Test that overly long context is rejected."""
    long_context = "a" * 50001
    
    response = authenticated_client.post(
        "/api/v1/ai/qa",
        json={
            "context": long_context,
            "question": "What is this?",
        },
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Rewrite endpoint tests

@pytest.mark.asyncio
@patch("app.api.v1.ai.rewriter.create_rewrite_chain")
async def test_rewrite_clarity_mode(mock_chain, authenticated_client):
    """Test rewriting in clarity mode."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "This is clearer text."}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "This confusing sentence structure has.",
            "mode": "clarity",
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rewritten_text"] == "This is clearer text."
    assert response.json()["mode"] == "clarity"


@pytest.mark.asyncio
@patch("app.api.v1.ai.rewriter.create_rewrite_chain")
async def test_rewrite_shorten_mode(mock_chain, authenticated_client):
    """Test rewriting in shorten mode."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "Short version."}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "This is a very long and verbose text that could be shortened significantly.",
            "mode": "shorten",
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rewritten_text"] == "Short version."
    assert response.json()["mode"] == "shorten"


@pytest.mark.asyncio
@patch("app.api.v1.ai.rewriter.create_rewrite_chain")
async def test_rewrite_polite_mode(mock_chain, authenticated_client):
    """Test rewriting in polite mode."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "Would you kindly fix this?"}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "Fix this now!",
            "mode": "polite",
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rewritten_text"] == "Would you kindly fix this?"
    assert response.json()["mode"] == "polite"


@pytest.mark.asyncio
@patch("app.api.v1.ai.rewriter.create_rewrite_chain")
async def test_rewrite_translate_mode(mock_chain, authenticated_client):
    """Test translation mode with target language."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "こんにちは"}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "Hello",
            "mode": "translate",
            "target_language": "Japanese",
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rewritten_text"] == "こんにちは"
    assert response.json()["mode"] == "translate"


@pytest.mark.asyncio
@patch("app.api.v1.ai.rewriter.create_rewrite_chain")
async def test_rewrite_translate_default_korean(mock_chain, authenticated_client):
    """Test translation with default Korean language."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "안녕하세요"}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "Hello",
            "mode": "translate",
        },
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["rewritten_text"] == "안녕하세요"


@pytest.mark.asyncio
async def test_rewrite_text_too_long(authenticated_client):
    """Test that text exceeding 10K chars is rejected."""
    long_text = "a" * 10001
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": long_text,
            "mode": "clarity",
        },
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_rewrite_unauthorized(client):
    """Test that unauthorized rewrite requests are rejected."""
    response = client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "Some text",
            "mode": "clarity",
        },
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@patch("app.api.v1.ai.rewriter.create_rewrite_chain")
async def test_rewrite_chain_error(mock_chain, authenticated_client):
    """Test error handling when rewrite chain fails."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.side_effect = Exception("API error")
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "Some text",
            "mode": "clarity",
        },
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "failed" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_rewrite_invalid_mode(authenticated_client):
    """Test that invalid mode is rejected."""
    response = authenticated_client.post(
        "/api/v1/ai/rewrite",
        json={
            "text": "Some text",
            "mode": "invalid_mode",
        },
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Moderation endpoint tests

@pytest.mark.asyncio
@patch("app.api.v1.ai.moderator.create_moderation_chain")
async def test_moderate_safe_content(mock_chain, authenticated_client):
    """Test moderation of safe content."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {
        "text": '{"risk_score": 0.1, "reason_tags": [], "explanation": "Content appears appropriate."}'
    }
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/moderate",
        json={"content": "This is a great forum discussion!"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["risk_score"] == 0.1
    assert data["reason_tags"] == []
    assert data["flagged_for_review"] is False


@pytest.mark.asyncio
@patch("app.api.v1.ai.moderator.create_moderation_chain")
async def test_moderate_risky_content(mock_chain, authenticated_client):
    """Test moderation of risky content that should be flagged."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {
        "text": '{"risk_score": 0.75, "reason_tags": ["harassment", "spam"], "explanation": "Contains personal attacks and promotional content."}'
    }
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/moderate",
        json={"content": "Buy my product now! You're an idiot if you don't!"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["risk_score"] == 0.75
    assert "harassment" in data["reason_tags"]
    assert "spam" in data["reason_tags"]
    assert data["flagged_for_review"] is True  # risk >= 0.5


@pytest.mark.asyncio
@patch("app.api.v1.ai.moderator.create_moderation_chain")
async def test_moderate_borderline_content(mock_chain, authenticated_client):
    """Test moderation of borderline content."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {
        "text": '{"risk_score": 0.45, "reason_tags": ["off_topic"], "explanation": "Content is somewhat off-topic but not harmful."}'
    }
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/moderate",
        json={"content": "Anyone want to chat about movies?"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["risk_score"] == 0.45
    assert data["flagged_for_review"] is False  # risk < 0.5


@pytest.mark.asyncio
async def test_moderate_content_too_long(authenticated_client):
    """Test that content exceeding 10K chars is rejected."""
    long_content = "a" * 10001
    
    response = authenticated_client.post(
        "/api/v1/ai/moderate",
        json={"content": long_content},
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_moderate_unauthorized(client):
    """Test that unauthorized moderation requests are rejected."""
    response = client.post(
        "/api/v1/ai/moderate",
        json={"content": "Some content"},
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@patch("app.api.v1.ai.moderator.create_moderation_chain")
async def test_moderate_invalid_json_response(mock_chain, authenticated_client):
    """Test error handling when AI returns invalid JSON."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {"text": "This is not JSON"}
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/moderate",
        json={"content": "Some content"},
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
@patch("app.api.v1.ai.moderator.create_moderation_chain")
async def test_moderate_all_reason_tags(mock_chain, authenticated_client):
    """Test that all possible reason tags can be returned."""
    mock_llm_chain = AsyncMock()
    mock_llm_chain.ainvoke.return_value = {
        "text": '{"risk_score": 0.9, "reason_tags": ["spam", "harassment", "hate_speech", "explicit", "violence", "misinformation", "off_topic"], "explanation": "Severely problematic content."}'
    }
    mock_chain.return_value = mock_llm_chain
    
    response = authenticated_client.post(
        "/api/v1/ai/moderate",
        json={"content": "Really bad content"},
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["reason_tags"]) == 7
    assert data["flagged_for_review"] is True
