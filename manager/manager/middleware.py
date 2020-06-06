from django.shortcuts import render
from rest_framework.authentication import BasicAuthentication

from manager.api.exceptions import AccountQuotaExceeded


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

    Renders pages for `AccountQuotaExceeded` and other
    exceptions.
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
