"""AI-powered API endpoints."""

from fastapi import APIRouter

from app.ai.chains import qa_chain, summarizer
from app.api.deps import CurrentUser
from app.schemas.ai import (
    QARequest,
    QAResponse,
    SummarizeRequest,
    SummarizeResponse,
)

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_thread(request: SummarizeRequest, current_user: CurrentUser):
    """Summarize thread content using AI (requires authentication)."""
    chain = summarizer.create_summarizer_chain()
    result = await chain.ainvoke({"thread_content": request.content})
    return SummarizeResponse(summary=result["text"])


@router.post("/qa", response_model=QAResponse)
async def question_answer(request: QARequest, current_user: CurrentUser):
    """Answer questions about thread content using AI (requires authentication)."""
    chain = qa_chain.create_qa_chain()
    result = await chain.ainvoke({
        "context": request.context,
        "question": request.question,
    })
    return QAResponse(answer=result["text"])
