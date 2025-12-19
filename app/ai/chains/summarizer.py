"""Thread summarization chain using LangChain."""

from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.prompts.templates import SUMMARIZER_TEMPLATE


def create_summarizer_chain(
    model: str = "gpt-4o-mini",
    temperature: float = 0.3,
) -> LLMChain:
    """
    Factory function to create a thread summarization chain.

    Args:
        model: OpenAI model to use
        temperature: Sampling temperature (lower = more deterministic)

    Returns:
        LLMChain configured for summarization
    """
    prompt = PromptTemplate(
        input_variables=["thread_content"],
        template=SUMMARIZER_TEMPLATE,
    )

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    return LLMChain(llm=llm, prompt=prompt)
