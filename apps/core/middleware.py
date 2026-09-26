import time
from django.http import JsonResponse
from django.core.cache import cache


class RateLimitMiddleware:
    """
    Middleware to track failed login attempts per IP address.
    Blocks IP after 5 failed attempts within 5 minutes.
    """

    MAX_ATTEMPTS = 5
    TIME_WINDOW = 300  # 5 minutes in seconds
    BLOCK_DURATION = 300  # 5 minutes block

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check rate limiting for login attempts
        if request.path == '/login/' and request.method == 'POST':
            ip_address = self.get_client_ip(request)
            cache_key = f'login_attempts_{ip_address}'
            blocked_key = f'login_blocked_{ip_address}'

            # Check if IP is currently blocked
            if cache.get(blocked_key):
                return JsonResponse(
                    {'error': 'Too many failed attempts. Please try again later.'},
                    status=429
                )

            # Process the request
            response = self.get_response(request)

            # Check if login failed (non-redirect response usually indicates failure)
            if response.status_code == 200 or hasattr(response, 'context_data'):
                # Increment failed attempts counter
                attempts = cache.get(cache_key, 0) + 1
                cache.set(cache_key, attempts, self.TIME_WINDOW)

                if attempts >= self.MAX_ATTEMPTS:
                    cache.set(blocked_key, True, self.BLOCK_DURATION)
                    cache.delete(cache_key)

            return response

        return self.get_response(request)

    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
