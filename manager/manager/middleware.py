import time

import rest_framework
from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication

from manager.api.exceptions import AccountQuotaExceeded, SocialTokenMissing
from users.models import generate_anonuser_id


def basic_auth(get_response):
    """
    Middleware that applies Basic authentication to non-API views.

    This middleware is usually only added if in development
    and does not get applied to any URLs starting with `/api/` since
    there are separate settings and authentication mechanisms for those.
    """

    def middleware(request):
        if not request.path.startswith("/api/"):
            auth = request.META.get("HTTP_AUTHORIZATION")
            if auth and auth.startswith("Basic "):
                backend = BasicAuthentication()
                user, _ = backend.authenticate(request)
                request.user = user
        return get_response(request)

    return middleware


def session_storage(get_response):
    """
    Middleware that stores commonly accessed data in the session.

    This reduces the number of database queries that need to
    be made on each request (e.g. for the URL of the user's image)
    by caching data in the session. For authenticated users, the
    cache is removed every hour to avoid it being stale
    (e.g. an async task updates the user's image).
    """

    def middleware(request):
        user = request.session.get("user")
        if user is not None:
            is_anon = user.get("anon", True)
            stored_time = user.get("time")
            if not is_anon and (not stored_time or stored_time < (time.time() - 3600)):
                user = None

        if user is None:
            if request.user.is_authenticated:
                user = {
                    "anon": False,
                    "image": request.user.personal_account.image.medium,
                }
            else:
                user = {"anon": True, "id": generate_anonuser_id()}
            user["time"] = time.time()
            request.session["user"] = user

        return get_response(request)

    return middleware


def method_override(get_response):
    """
    Override the request method with the `X-HTTP-Method-Override` header.

    This header is used by `htmx` for PATCH and DELETE requests, since
    most browsers only support issuing GET and POST.
    Based on https://www.django-rest-framework.org/topics/browser-enhancements/#http-header-based-method-overriding
    """
    HEADER = "HTTP_X_HTTP_METHOD_OVERRIDE"

    def middleware(request):
        if request.method == "POST" and HEADER in request.META:
            request.method = request.META[HEADER]
        return get_response(request)

    return middleware


class CustomExceptionsMiddleware:
    """
    Handle custom exceptions.

    Renders pages for custom exceptions e.g. `AccountQuotaExceeded`
    and `rest_framework` exceptions (which are not otherwise handled
    if raised from a `ui-*` view).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Obligatory method."""
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Ummm, process the exception."""
        if isinstance(exception, AccountQuotaExceeded):
            try:
                message = list(exception.detail.values())[0]
            except (TypeError, IndexError):
                message = None
            return render(
                request, "accounts/quota_exceeded.html", dict(message=message)
            )
        elif isinstance(exception, SocialTokenMissing):
            try:
                message = list(exception.detail.values())[0]
            except (TypeError, IndexError):
                message = None
            return render(request, "users/token_missing.html", dict(message=message))
        elif isinstance(exception, rest_framework.exceptions.NotFound):
            return render(request, "404.html", status=404)
        elif isinstance(exception, rest_framework.exceptions.PermissionDenied):
            return render(request, "403.html", status=403)
