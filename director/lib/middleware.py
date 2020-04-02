from django.http import HttpRequest
from django.shortcuts import redirect

from lib.browser_detection import user_agent_is_internet_explorer


def ie_detect_middleware(get_response):
    """Redirect Internet Explorer to a page letting them know they are not currently supported."""

    def middleware(request: HttpRequest):
        if user_agent_is_internet_explorer(request.META.get("HTTP_USER_AGENT")):
            if "ie-unsupported" not in request.path:
                # prevent redirect loops
                return redirect("ie-unsupported")

        return get_response(request)

    return middleware
