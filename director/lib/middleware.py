from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse


def ie_detect_middleware(get_response):
    """Redirect Internet Explorer to a page letting them know they are not currently supported."""
    def middleware(request: HttpRequest):
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        if user_agent and 'MSIE' in user_agent:
            if 'ie-unsupported' not in request.path:
                # prevent redirect loops
                return redirect(reverse('ie-unsupported'))

        return get_response(request)

    return middleware
