from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication

from manager.api.exceptions import AccountQuotaExceeded, SocialTokenMissing


def basic_auth(get_response):
    """Middleware that applies Basic authentication."""

    def middleware(request):
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
    be made on each request e.g. for the URL of the user's image
    """

    def middleware(request):
        if "user" not in request.session:
            if request.user.is_authenticated:
                request.session["user"] = {
                    "image": request.user.personal_account.image.medium,
                }
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
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Obligitory method."""
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
