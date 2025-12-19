"""Tests for AI chains.

Note: These tests require OPENAI_API_KEY to be set.
Use pytest markers to skip in CI if needed.
"""

import pytest

# Skip all tests in this module if OpenAI is not configured
pytestmark = pytest.mark.skipif(
    True,  # Change to check for OPENAI_API_KEY
    reason="OpenAI API key not configured",
)


def test_summarizer_chain_creation():
    """Test that summarizer chain can be created."""
    from app.ai.chains.summarizer import create_summarizer_chain

    chain = create_summarizer_chain()
    assert chain is not None


def test_qa_chain_creation():
    """Test that QA chain can be created."""
    from app.ai.chains.qa_chain import create_qa_chain

    chain = create_qa_chain()
    assert chain is not None


def test_prompt_templates_defined():
    """Test that prompt templates are defined."""
    from app.ai.prompts.templates import QA_TEMPLATE, SUMMARIZER_TEMPLATE

    assert "{thread_content}" in SUMMARIZER_TEMPLATE
    assert "{context}" in QA_TEMPLATE
    assert "{question}" in QA_TEMPLATE
