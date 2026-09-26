"""
Authentication middleware for session expiry and HTMX-aware auth handling.
"""

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect


class SessionExpiryMiddleware:
    """
    Middleware to handle session timeout.
    Logs out the user if the session has expired based on
    SESSION_COOKIE_AGE setting.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = datetime.fromisoformat(last_activity)
                session_age = getattr(
                    settings,
                    'SESSION_COOKIE_AGE',
                    3600
                )
                if datetime.now() - last_activity_time > timedelta(
                    seconds=session_age
                ):
                    logout(request)
                    return redirect('accounts:login')

            request.session['last_activity'] = datetime.now().isoformat()

        response = self.get_response(request)
        return response


class HTMXAuthMiddleware:
    """
    Middleware to handle HTMX-aware authentication redirects.
    Returns HX-Redirect header for 401 responses on HTMX requests
    instead of regular redirects.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if this is an HTMX request that got redirected to login
        if (request.headers.get('HX-Request') == 'true' and
                response.status_code == 302):
            location = response.get('Location', '')
            if '/login/' in location:
                # Convert to HX-Redirect for HTMX handling
                new_response = HttpResponse(status=401)
                new_response['HX-Redirect'] = location
                return new_response

        return response
