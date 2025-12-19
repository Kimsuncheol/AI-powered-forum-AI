"""Question-answering chain using LangChain."""

from langchain_classic.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.ai.prompts.templates import QA_TEMPLATE


def create_qa_chain(
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
) -> LLMChain:
    """
    Factory function to create a Q&A chain.

    Args:
        model: OpenAI model to use
        temperature: Sampling temperature

    Returns:
        LLMChain configured for Q&A
    """
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=QA_TEMPLATE,
    )

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    return LLMChain(llm=llm, prompt=prompt)
