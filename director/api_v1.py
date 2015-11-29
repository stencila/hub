import json

from django.conf.urls import url
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.core import urlresolvers

import users.views
import components.views


urlpatterns = [
    url(r'^me/?$',                                    users.views.me_read),

    url(r'^tokens/?$',                                users.views.tokens),
    url(r'^tokens/(?P<id>\d+)/?$',                    users.views.tokens),

    url(r'^users/?$',                                 users.views.users_list),
    url(r'^users/(?P<username>[\w-]+)/?$',            users.views.users_read),

    # Catch-all to prevent continued search for a URL match under the `api/` root
    url(r'.*', lambda request: HttpResponseNotFound()),
]

if settings.MODE == 'local':

    # Get a Django Debug Toolbar for API endpoints
    # Useful for checking performance of views, in particular
    # the number of database hits
    #
    # From https://gist.github.com/marteinn/5693665

    def html_decorator(func):
        """
        This decorator wraps the JSON API output in HTML.
        (From http://stackoverflow.com/a/14647943)
        """

        def _decorated(*args, **kwargs):
            response = func(*args, **kwargs)

            # Attempt to pretty print JSON
            try:
                content = json.loads(response.content)
                content = json.dumps(content, indent=4, separators=(',', ': '))
            except:
                content = response.content

            wrapped = ("<html><body><pre>",
                       content,
                       "</pre></body></html>")

            return HttpResponse(wrapped)

        return _decorated

    @html_decorator
    def debug(request):
        """
        Debug endpoint that uses the html_decorator,
        """
        path = request.META.get("PATH_INFO")
        api_url = path.replace("/debug", "")

        view = urlresolvers.resolve(api_url)

        accept = request.META.get("HTTP_ACCEPT")
        accept += ",application/json"
        request.META["HTTP_ACCEPT"] = accept

        res = view.func(request, **view.kwargs)
        return HttpResponse(res._container)

    urlpatterns += [
        url(r'^.+/debug', debug),
    ]
