"""
Rate limiter for authentication attempts using Django's cache framework.
"""

import hashlib
from django.core.cache import cache


class LoginRateLimiter:
    """
    Rate limiter for login attempts based on IP address.
    Implements 5 failed attempts per 5 minutes window.
    """

    MAX_ATTEMPTS = 5
    WINDOW_SECONDS = 300  # 5 minutes

    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.cache_key = self._get_cache_key()

    def _get_cache_key(self):
        """Generate a safe cache key from IP address."""
        ip_hash = hashlib.md5(self.ip_address.encode()).hexdigest()
        return f"login_attempts_{ip_hash}"

    def get_attempts(self):
        """Get current number of attempts."""
        attempts = cache.get(self.cache_key)
        return attempts if attempts is not None else 0

    def is_blocked(self):
        """Check if the IP is currently rate limited."""
        return self.get_attempts() >= self.MAX_ATTEMPTS

    def record_attempt(self):
        """Record a failed login attempt."""
        attempts = self.get_attempts()

        if attempts == 0:
            # First attempt, set with expiry
            cache.set(self.cache_key, 1, self.WINDOW_SECONDS)
        else:
            # Increment existing counter
            cache.set(self.cache_key, attempts + 1, self.WINDOW_SECONDS)

        return attempts + 1

    def get_remaining_time(self):
        """Get remaining time until rate limit resets."""
        ttl = cache.ttl(self.cache_key)
        return ttl if ttl else self.WINDOW_SECONDS

    def clear(self):
        """Clear rate limit for this IP (e.g., after successful login)."""
        cache.delete(self.cache_key)

    def get_error_message(self):
        """Get formatted error message with remaining time."""
        remaining_minutes = (self.get_remaining_time() + 59) // 60
        return f"Too many attempts, try again in {remaining_minutes} minutes"


def get_rate_limiter_for_request(request):
    """Helper function to get rate limiter for a request."""
    ip_address = request.META.get('REMOTE_ADDR', '')
    if not ip_address:
        # Fallback to X-Forwarded-For header
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()

    return LoginRateLimiter(ip_address)
