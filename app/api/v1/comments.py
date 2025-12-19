"""Comment-related API endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate
from app.services import comment_service

router = APIRouter()


@router.get("/thread/{thread_id}", response_model=list[CommentResponse])
async def list_comments(thread_id: str, skip: int = 0, limit: int = 50):
    """List all comments for a thread."""
    return await comment_service.get_comments_by_thread(thread_id, skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: str):
    """Get a specific comment by ID."""
    return await comment_service.get_comment(comment_id)


@router.post("", response_model=CommentResponse, status_code=201)
async def create_comment(comment: CommentCreate, current_user: CurrentUser):
    """Create a new comment (requires authentication)."""
    return await comment_service.create_comment(comment, current_user["uid"])


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str, comment: CommentUpdate, current_user: CurrentUser
):
    """Update a comment (requires authentication and ownership)."""
    return await comment_service.update_comment(comment_id, comment, current_user["uid"])


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: str, current_user: CurrentUser):
    """Delete a comment (requires authentication and ownership)."""
    await comment_service.delete_comment(comment_id, current_user["uid"])
