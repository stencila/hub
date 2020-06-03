from rest_framework.authentication import BasicAuthentication


def basic_auth(get_response):
    """Middleware that applies Basic authentication."""

    def middleware(request):
        auth = request.META.get("HTTP_AUTHORIZATION")
        if auth and auth.startswith("Basic "):
            backend = BasicAuthentication()
            user, _ = backend.authenticate(request)
            request.user = user
        response = get_response(request)
        return response

    return middleware
