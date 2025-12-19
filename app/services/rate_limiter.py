"""Rate limiting service for AI endpoints."""

import logging
from datetime import datetime, timezone
from typing import Dict, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitService:
    """
    Service to track and limit AI usage per user.
    
    NOTE: This is an in-memory implementation for the MVP.
    In a production environment with multiple workers/instances,
    this should be backed by Redis or a similar shared store.
    """
    
    def __init__(self):
        # Maps user_uid to (date_string, count)
        # Example: "user123": ("2023-10-27", 10)
        self._usage: Dict[str, Tuple[str, int]] = {}
        self._limit = settings.AI_DAILY_RATE_LIMIT

    def _get_today_str(self) -> str:
        """Get current date as YYYY-MM-DD string (UTC)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def check_limit(self, user_id: str) -> bool:
        """
        Check if the user has reached their daily limit.
        
        Args:
            user_id: The unique identifier of the user.
            
        Returns:
            True if the user is allowed to make a request, False otherwise.
        """
        today = self._get_today_str()
        
        if user_id not in self._usage:
            # User hasn't made any requests yet (or not today if cleanup happened)
            return True
        
        last_date, count = self._usage[user_id]
        
        # If the stored date is different from today, their count resets
        if last_date != today:
            return True
            
        # Check against the limit
        return count < self._limit

    def increment_usage(self, user_id: str) -> None:
        """
        Increment the usage count for a user.
        
        Should be called after a successful (or attempted) AI request.
        """
        today = self._get_today_str()
        
        if user_id not in self._usage:
            self._usage[user_id] = (today, 1)
        else:
            last_date, count = self._usage[user_id]
            
            if last_date != today:
                # New day, reset count
                self._usage[user_id] = (today, 1)
            else:
                # Same day, increment
                self._usage[user_id] = (today, count + 1)
                
        # Optional: Clean up old entries periodically to prevent memory leak
        # For MVP/small scale, this might not be strictly necessary, 
        # but good practice would be to have a cleanup job.

    def get_remaining_requests(self, user_id: str) -> int:
        """Get the number of remaining requests for the user today."""
        today = self._get_today_str()
        
        if user_id not in self._usage:
            return self._limit
            
        last_date, count = self._usage[user_id]
        
        if last_date != today:
            return self._limit
            
        return max(0, self._limit - count)
