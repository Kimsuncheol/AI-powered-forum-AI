"""Common API dependencies."""

from typing import Annotated

from fastapi import Depends

from app.core.firebase import verify_firebase_token

# Type alias for authenticated user dependency
CurrentUser = Annotated[dict, Depends(verify_firebase_token)]
