"""Comment business logic service."""

from app.core.exceptions import ForbiddenError, NotFoundError
from app.schemas.comment import CommentCreate, CommentResponse, CommentUpdate


async def get_comments_by_thread(
    thread_id: str, skip: int = 0, limit: int = 50
) -> list[CommentResponse]:
    """Get all comments for a thread with pagination."""
    # TODO: Implement database query
    return []


async def get_comment(comment_id: str) -> CommentResponse:
    """Get a comment by ID."""
    # TODO: Implement database query
    raise NotFoundError(f"Comment {comment_id} not found")


async def create_comment(comment: CommentCreate, user_id: str) -> CommentResponse:
    """Create a new comment."""
    # TODO: Implement database insert
    return CommentResponse(
        id="temp-id",
        thread_id=comment.thread_id,
        content=comment.content,
        author_id=user_id,
    )


async def update_comment(
    comment_id: str, comment: CommentUpdate, user_id: str
) -> CommentResponse:
    """Update a comment (owner only)."""
    # TODO: Implement ownership check and update
    raise NotFoundError(f"Comment {comment_id} not found")


async def delete_comment(comment_id: str, user_id: str) -> None:
    """Delete a comment (owner only)."""
    # TODO: Implement ownership check and delete
    raise NotFoundError(f"Comment {comment_id} not found")
