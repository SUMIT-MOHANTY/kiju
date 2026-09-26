"""
Authentication middleware for Django with HTMX support.
"""

import time
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class SessionExpiryMiddleware(MiddlewareMixin):
    """
    Middleware to handle session expiry with HTMX-aware redirects.
    """

    def process_request(self, request):
        if not hasattr(request, 'user'):
            return None

        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            current_time = time.time()

            if last_activity:
                session_timeout = getattr(settings, 'SESSION_COOKIE_AGE', 3600)
                if current_time - last_activity > session_timeout:
                    logout(request)
                    request.session_expired = True
                    return None

            request.session['last_activity'] = current_time

        return None

    def process_response(self, request, response):
        if getattr(request, 'session_expired', False):
            if request.headers.get('HX-Request'):
                response = HttpResponseRedirect('/login/')
                response['HX-Redirect'] = '/login/'
                return response

        return response


class HTMXAuthMiddleware(MiddlewareMixin):
    """
    Middleware to handle authentication for HTMX requests.
    Returns HX-Redirect header for 401 responses on HTMX requests.
    """

    def process_response(self, request, response):
        if response.status_code == 401 or response.status_code == 403:
            if request.headers.get('HX-Request'):
                login_url = '/login/'
                if hasattr(request, 'path'):
                    login_url = f'/login/?next={request.path}'
                response['HX-Redirect'] = login_url

        return response
