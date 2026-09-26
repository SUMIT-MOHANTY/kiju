from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.contrib import messages


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware to handle rate limiting for login attempts.
    Blocks IP after 5 failed attempts per 5 minutes.
    """
    max_attempts = 5
    lockout_duration = 300  # 5 minutes in seconds

    def process_request(self, request):
        if request.path == '/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)

            if attempts >= self.max_attempts:
                messages.error(
                    request,
                    'Too many failed attempts. Please try again later.'
                )
                return None

        return None

    def process_response(self, request, response):
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
