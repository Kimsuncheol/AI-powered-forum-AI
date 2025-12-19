"""Content moderation chain using LangChain."""

import json
import logging

from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.prompts.templates import MODERATION_TEMPLATE

logger = logging.getLogger(__name__)


def create_moderation_chain(
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> LLMChain:
    """
    Factory function to create a content moderation chain.

    Args:
        model: OpenAI model to use
        temperature: Sampling temperature (lower = more deterministic)

    Returns:
        LLMChain configured for content moderation
    """
    prompt = PromptTemplate(
        input_variables=["content"],
        template=MODERATION_TEMPLATE,
    )

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    return LLMChain(llm=llm, prompt=prompt)


def parse_moderation_result(result: str) -> dict:
    """
    Parse the AI moderation result from JSON string.

    Args:
        result: JSON string from the AI model

    Returns:
        Parsed dict with risk_score, reason_tags, and explanation

    Raises:
        ValueError: If result cannot be parsed
    """
    try:
        # Try to extract JSON from the result
        # Sometimes the AI includes extra text before/after the JSON
        start = result.find("{")
        end = result.rfind("}") + 1
        
        if start == -1 or end == 0:
            raise ValueError("No JSON object found in result")
        
        json_str = result[start:end]
        parsed = json.loads(json_str)
        
        # Validate required fields
        if "risk_score" not in parsed:
            raise ValueError("Missing 'risk_score' in result")
        
        if "reason_tags" not in parsed:
            parsed["reason_tags"] = []
        
        if "explanation" not in parsed:
            parsed["explanation"] = ""
        
        # Ensure risk_score is between 0 and 1
        risk_score = float(parsed["risk_score"])
        if not 0.0 <= risk_score <= 1.0:
            logger.warning(f"Risk score {risk_score} out of range, clamping to [0,1]")
            risk_score = max(0.0, min(1.0, risk_score))
        
        parsed["risk_score"] = risk_score
        
        return parsed
        
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse moderation result: {e}")
        raise ValueError(f"Failed to parse moderation result: {str(e)}")
