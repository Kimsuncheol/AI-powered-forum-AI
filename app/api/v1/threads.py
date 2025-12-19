"""Thread-related API endpoints."""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.thread import ThreadCreate, ThreadResponse, ThreadUpdate
from app.services import thread_service

router = APIRouter()


@router.get("", response_model=list[ThreadResponse])
async def list_threads(skip: int = 0, limit: int = 20):
    """List all threads with pagination."""
    return await thread_service.get_threads(skip=skip, limit=limit)


@router.get("/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    """Get a specific thread by ID."""
    return await thread_service.get_thread(thread_id)


@router.post("", response_model=ThreadResponse, status_code=201)
async def create_thread(thread: ThreadCreate, current_user: CurrentUser):
    """Create a new thread (requires authentication)."""
    return await thread_service.create_thread(thread, current_user["uid"])


@router.put("/{thread_id}", response_model=ThreadResponse)
async def update_thread(
    thread_id: str, thread: ThreadUpdate, current_user: CurrentUser
):
    """Update a thread (requires authentication and ownership)."""
    return await thread_service.update_thread(thread_id, thread, current_user["uid"])


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(thread_id: str, current_user: CurrentUser):
    """Delete a thread (requires authentication and ownership)."""
    await thread_service.delete_thread(thread_id, current_user["uid"])
