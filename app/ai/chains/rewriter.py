"""Text rewriting chain using LangChain."""

from enum import Enum

from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.prompts.templates import (
    REWRITE_CLARITY_TEMPLATE,
    REWRITE_POLITE_TEMPLATE,
    REWRITE_SHORTEN_TEMPLATE,
    REWRITE_TRANSLATE_TEMPLATE,
)


class RewriteMode(str, Enum):
    """Supported rewrite modes."""

    CLARITY = "clarity"
    SHORTEN = "shorten"
    POLITE = "polite"
    TRANSLATE = "translate"


def create_rewrite_chain(
    mode: RewriteMode,
    target_language: str = "Korean",
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> LLMChain:
    """
    Factory function to create a text rewriting chain.

    Args:
        mode: The rewriting mode to use
        target_language: Target language for translation mode (default: Korean)
        model: OpenAI model to use
        temperature: Sampling temperature (lower = more deterministic)

    Returns:
        LLMChain configured for the specified rewrite mode

    Raises:
        ValueError: If an unsupported mode is provided
    """
    # Select template and input variables based on mode
    if mode == RewriteMode.CLARITY:
        template = REWRITE_CLARITY_TEMPLATE
        input_variables = ["text"]
    elif mode == RewriteMode.SHORTEN:
        template = REWRITE_SHORTEN_TEMPLATE
        input_variables = ["text"]
    elif mode == RewriteMode.POLITE:
        template = REWRITE_POLITE_TEMPLATE
        input_variables = ["text"]
    elif mode == RewriteMode.TRANSLATE:
        template = REWRITE_TRANSLATE_TEMPLATE
        input_variables = ["text", "target_language"]
    else:
        raise ValueError(f"Unsupported rewrite mode: {mode}")

    prompt = PromptTemplate(
        input_variables=input_variables,
        template=template,
    )

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    return LLMChain(llm=llm, prompt=prompt)
