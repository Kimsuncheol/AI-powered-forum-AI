"""AI-powered API endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.chains import moderator, qa_chain, rewriter, summarizer
from app.api.deps import (
    CurrentUser,
    check_ai_rate_limit,
    get_rate_limit_service,
)
from app.services.rate_limiter import RateLimitService
from app.schemas.ai import (
    ModerationRequest,
    ModerationResponse,
    QARequest,
    QAResponse,
    RewriteRequest,
    RewriteResponse,
    SummarizeRequest,
    SummarizeResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/summarize-thread",
    response_model=SummarizeResponse,
    dependencies=[Depends(check_ai_rate_limit)],
)
async def summarize_thread(
    request: SummarizeRequest,
    current_user: CurrentUser,
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
):
    """
    Summarize thread content using AI.
    
    This endpoint uses LangChain with OpenAI to generate a concise summary of
    the provided thread content. Requires authentication.
    
    Args:
        request: Contains the thread content to summarize
        current_user: Authenticated user information from Firebase
        
    Returns:
        SummarizeResponse with the generated summary
        
    Raises:
        HTTPException: If summarization fails or content is invalid
    """
    try:
        # Validate content length
        if len(request.content) > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content too long. Maximum 50,000 characters allowed.",
            )
        
        # Log the summarization request
        logger.info(
            f"Summarization request from user {current_user['uid']}, "
            f"content length: {len(request.content)} chars"
        )
        
        # Create and invoke the summarization chain
        chain = summarizer.create_summarizer_chain()
        result = await chain.ainvoke({"thread_content": request.content})
        
        # Extract summary from result
        summary = result.get("text", "")
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate summary",
            )
        
        logger.info(f"Successfully generated summary for user {current_user['uid']}")
        
        logger.info(f"Successfully generated summary for user {current_user['uid']}")
        rate_limit_service.increment_usage(current_user["uid"])
        
        return SummarizeResponse(summary=summary)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Summarization failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summarization failed: {str(e)}",
        )


@router.post(
    "/qa",
    response_model=QAResponse,
    dependencies=[Depends(check_ai_rate_limit)],
)
async def question_answer(
    request: QARequest,
    current_user: CurrentUser,
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
):
    """
    Answer questions about thread content using AI.
    
    This endpoint uses LangChain with OpenAI to answer questions based on
    the provided context. Requires authentication.
    
    Args:
        request: Contains the context and question
        current_user: Authenticated user information from Firebase
        
    Returns:
        QAResponse with the generated answer
        
    Raises:
        HTTPException: If Q&A fails or input is invalid
    """
    try:
        # Validate input lengths
        if len(request.context) > 50000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Context too long. Maximum 50,000 characters allowed.",
            )
        
        if len(request.question) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question too long. Maximum 1,000 characters allowed.",
            )
        
        # Log the Q&A request
        logger.info(
            f"Q&A request from user {current_user['uid']}, "
            f"context length: {len(request.context)} chars"
        )
        
        # Create and invoke the Q&A chain
        chain = qa_chain.create_qa_chain()
        result = await chain.ainvoke({
            "context": request.context,
            "question": request.question,
        })
        
        # Extract answer from result
        answer = result.get("text", "")
        if not answer:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate answer",
            )
        
        logger.info(f"Successfully generated answer for user {current_user['uid']}")
        
        logger.info(f"Successfully generated answer for user {current_user['uid']}")
        rate_limit_service.increment_usage(current_user["uid"])
        
        return QAResponse(answer=answer)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Q&A failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Q&A failed: {str(e)}",
        )


@router.post(
    "/rewrite",
    response_model=RewriteResponse,
    dependencies=[Depends(check_ai_rate_limit)],
)
async def rewrite_text(
    request: RewriteRequest,
    current_user: CurrentUser,
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
):
    """
    Rewrite text using AI with different modes.
    
    Supports multiple rewriting modes:
    - clarity: Improve text clarity and readability
    - shorten: Make text more concise
    - polite: Make text more polite and professional
    - translate: Translate to target language (default: Korean)
    
    Args:
        request: Contains text, mode, and optional target language
        current_user: Authenticated user information from Firebase
        
    Returns:
        RewriteResponse with the rewritten text and mode
        
    Raises:
        HTTPException: If rewriting fails or input is invalid
    """
    try:
        # Validate text length
        if len(request.text) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text too long. Maximum 10,000 characters allowed.",
            )
        
        # Log the rewrite request
        logger.info(
            f"Rewrite request from user {current_user['uid']}, "
            f"mode: {request.mode}, text length: {len(request.text)} chars"
        )
        
        # Create the rewrite chain for the specified mode
        chain = rewriter.create_rewrite_chain(
            mode=request.mode,
            target_language=request.target_language or "Korean",
        )
        
        # Prepare input based on mode
        chain_input = {"text": request.text}
        if request.mode == rewriter.RewriteMode.TRANSLATE:
            chain_input["target_language"] = request.target_language or "Korean"
        
        # Invoke the chain
        result = await chain.ainvoke(chain_input)
        
        # Extract rewritten text from result
        rewritten_text = result.get("text", "")
        if not rewritten_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to rewrite text",
            )
        
        logger.info(
            f"Successfully rewrote text for user {current_user['uid']} "
            f"using mode {request.mode}"
        )
        rate_limit_service.increment_usage(current_user["uid"])
        
        return RewriteResponse(
            rewritten_text=rewritten_text,
            mode=request.mode,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Handle invalid mode
        logger.error(f"Invalid rewrite mode: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Text rewrite failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text rewrite failed: {str(e)}",
        )


@router.post(
    "/moderate",
    response_model=ModerationResponse,
    dependencies=[Depends(check_ai_rate_limit)],
)
async def moderate_content(
    request: ModerationRequest,
    current_user: CurrentUser,
    rate_limit_service: RateLimitService = Depends(get_rate_limit_service),
):
    """
    Moderate content using AI to assess risk and provide guidance.
    
    This endpoint provides ASSISTIVE moderation - it returns a risk assessment
    and reason tags but does NOT automatically block content. The response
    is designed to help human moderators make informed decisions.
    
    Risk Score Interpretation:
    - 0.0-0.3: Low risk, likely appropriate
    - 0.3-0.5: Medium risk, may warrant attention
    - 0.5-1.0: High risk, flagged for human review
    
    Reason Tags:
    - spam, harassment, hate_speech, explicit, violence, misinformation, off_topic
    
    Args:
        request: Contains content to moderate
        current_user: Authenticated user information from Firebase
        
    Returns:
        ModerationResponse with risk_score, reason_tags, explanation, and flagged_for_review
        
    Raises:
        HTTPException: If moderation fails or input is invalid
    """
    try:
        # Validate content length
        if len(request.content) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content too long. Maximum 10,000 characters allowed.",
            )
        
        # Log the moderation request
        logger.info(
            f"Moderation request from user {current_user['uid']}, "
            f"content length: {len(request.content)} chars"
        )
        
        # Create and invoke the moderation chain
        chain = moderator.create_moderation_chain()
        result = await chain.ainvoke({"content": request.content})
        
        # Extract and parse the moderation result
        raw_result = result.get("text", "")
        if not raw_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate moderation result",
            )
        
        # Parse the JSON response
        try:
            parsed_result = moderator.parse_moderation_result(raw_result)
        except ValueError as e:
            logger.error(f"Failed to parse moderation result: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse moderation result",
            )
        
        # Determine if content should be flagged for review (risk >= 0.5)
        flagged_for_review = parsed_result["risk_score"] >= 0.5
        
        logger.info(
            f"Moderation complete for user {current_user['uid']}: "
            f"risk_score={parsed_result['risk_score']:.2f}, "
            f"flagged={flagged_for_review}"
        )
        rate_limit_service.increment_usage(current_user["uid"])
        
        return ModerationResponse(
            risk_score=parsed_result["risk_score"],
            reason_tags=parsed_result["reason_tags"],
            explanation=parsed_result["explanation"],
            flagged_for_review=flagged_for_review,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Content moderation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content moderation failed: {str(e)}",
        )



