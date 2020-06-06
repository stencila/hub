from rest_framework.authentication import BasicAuthentication


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
