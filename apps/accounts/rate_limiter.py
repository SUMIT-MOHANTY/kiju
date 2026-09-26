"""
Rate limiter for authentication attempts.
Implements IP-based rate limiting with configurable windows.
"""

import time
from typing import Optional

from django.core.cache import cache
from django.http import HttpRequest


class RateLimiter:
    """
    IP-based rate limiter using Django cache.
    Tracks failed login attempts and blocks after threshold.
    """

    def __init__(
        self,
        key_prefix: str = "login_attempts",
        max_requests: int = 5,
        window_seconds: int = 300,
        block_duration_seconds: Optional[int] = None
    ):
        """
        Initialize rate limiter.

        Args:
            key_prefix: Prefix for cache keys
            max_requests: Maximum allowed requests within the window
            window_seconds: Time window in seconds
            block_duration_seconds: Optional duration to block after
                exceeding limit
        """
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.block_duration_seconds = block_duration_seconds or window_seconds

    def _get_cache_key(self, identifier: str) -> str:
        """Generate cache key for an identifier."""
        return f"{self.key_prefix}:{identifier}"

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for identifier.

        Returns True if under rate limit, False if blocked.
        """
        cache_key = self._get_cache_key(identifier)
        attempts = cache.get(cache_key, [])

        now = time.time()
        cutoff = now - self.window_seconds

        # Remove old attempts outside window
        attempts = [t for t in attempts if t > cutoff]

        # Check if blocked
        if len(attempts) >= self.max_requests:
            return False

        return True

    def record_attempt(self, identifier: str) -> None:
        """Record a failed attempt for identifier."""
        cache_key = self._get_cache_key(identifier)
        attempts = cache.get(cache_key, [])

        now = time.time()
        attempts.append(now)

        # Store with block duration as expiry
        cache.set(
            cache_key,
            attempts,
            timeout=self.block_duration_seconds
        )

    def get_remaining_time(self, identifier: str) -> int:
        """
        Get remaining block time in minutes.

        Returns 0 if not blocked.
        """
        cache_key = self._get_cache_key(identifier)
        attempts = cache.get(cache_key, [])

        if not attempts or len(attempts) < self.max_requests:
            return 0

        now = time.time()
        oldest_attempt = min(attempts)
        remaining = self.window_seconds - (now - oldest_attempt)

        return max(1, int(remaining / 60))

    def clear_attempts(self, identifier: str) -> None:
        """Clear all attempts for identifier (e.g., on successful login)."""
        cache_key = self._get_cache_key(identifier)
        cache.delete(cache_key)


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract client IP from request, handling proxies.

    Checks X-Forwarded-For header first, then REMOTE_ADDR.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
