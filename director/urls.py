"""director URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
import os
import json

from django.conf import settings
from django.conf.urls import url, include, handler400, handler403, handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.core import urlresolvers

import general.views
import builds.views
import components.views
import sessions_.views
import snippets.views
import users.views


urlpatterns = [

    # Front page
    url(r'^$',                                                       general.views.front),

    # API documentation
    url(r'^api/api.yml',                                             general.views.api_yml),
    url(r'^api/?$',                                                  general.views.api_ui),

    # Snippets
    url(r'^snippets(/(?P<id>.+))?/?$',                               snippets.views.snippets),

    # Sessions
    url(r'^sessions(/(?P<id>\d+))?/?$',                              sessions_.views.sessions),
    url(r'^sessions/new/?$',                                         sessions_.views.new),
    url(r'^sessions/(?P<id>\d+)@connect/?$',                         sessions_.views.connect),
    url(r'^sessions/(?P<id>\d+)@ping/?$',                            sessions_.views.ping),
    url(r'^sessions/(?P<id>\d+)@stop/?$',                            sessions_.views.stop),

    # User management (login, logout etc)
    url(r'^me/?$',                                                   users.views.me_read),
    url(r'^me/signup/?$',                                            users.views.signup),
    url(r'^me/signin/?$',                                            users.views.signin),
    url(r'^me/signin-dialog/?$',                                     users.views.signin_dialog),
    url(r'^me/signout/?$',                                           users.views.signout),
    url(r'^me/settings/?$',                                          users.views.settings),
    url(r'^me/',                                                     include('allauth.urls')),
    # The allauth URLs not overidden above are:
        # password/change/                    account_change_password         change password
        # password/set/                       account_set_password            confirmation that password is changed?
        # inactive/                           account_inactive                notify user that account is inactive?
        # email/                              account_email                   add, change and verify emails
        # confirm-email/                      account_email_verification_sent
        # confirm-email/(?P<key>\w+)/
        # password/reset/                     account_reset_password
        # password/reset/done/                account_reset_password_done
        # password/reset/key/.../             account_reset_password_from_key
        # password/reset/key/done/            account_reset_password_from_key_done
        # social/login/cancelled/             socialaccount_login_cancelled
        # social/login/error/                 socialaccount_login_error
        # social/connections                  socialaccount_connections

    url(r'^users/?$',                                                users.views.users_list),
    url(r'^users/(?P<username>[\w-]+)/?$',                           users.views.users_read),

    url(r'^tokens/?$',                                               users.views.tokens),
    url(r'^tokens/(?P<id>\d+)/?$',                                   users.views.tokens),

    url(r'^events/?$',                                               users.views.events),

    url(r'^builds(/(?P<id>\d+))?/?$',                                builds.views.builds),

    # Administration interface
    url(r'^admin/',                                                  admin.site.urls),

    # Test views
    url(r'^test/400',                                                general.views.test400),
    url(r'^test/403',                                                general.views.test403),
    url(r'^test/404',                                                general.views.test404),
    url(r'^test/500',                                                general.views.test500),

    # Error handling
    url(r'^backend-error/(?P<backend>[\w-]+)/(?P<url>.+)$',          general.views.backend_error),
]

handler400 = general.views.handler400
handler403 = general.views.handler403
handler404 = general.views.handler404
handler500 = general.views.handler500

# In development, serve static files that are handled by `nginx.conf` when in production
if settings.MODE == 'local':

    # Dynamically generated content
    urlpatterns += static(r'/dynamic/', document_root=os.path.join(settings.BASE_DIR, 'dynamic'))

    # Build Javascript and CSS on get.stenci.la when in production
    # can be obtained when in local mode from:
    # ...a local directory
    if settings.GET_LOCAL:
        urlpatterns += static(r'/get/web/', document_root='/srv/stencila/store/get/web')
    # ...a locally running `stencila/web/server.js` which compiles on the fly ;
    # run it with `make web-devserve` in that repo
    elif settings.GET_DEVSERVE:
        urlpatterns += [
            url(r'^get/web/(?P<path>.*)$', lambda request, path: HttpResponseRedirect('//localhost:5000/get/web/'+path))
        ]
    # or, fallback to the production deployment
    else:
        urlpatterns += [
            url(r'^get/web/(?P<path>.*)$', lambda request, path: HttpResponseRedirect('https://s3-us-west-2.amazonaws.com/get.stenci.la/web/'+path))
        ]

    # Django Debug Toolbar for JSON API endpoints
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


urlpatterns += [

    ############### Collections of components #################
    
    # List
    url(r'^(?P<type>(components|stencils|sheets|functions))/?$',  components.views.components),

    # Create
    url(r'^(?P<type>(stencils|sheets|functions))/new/?$',  components.views.new),

    ############### Individual components #################
  
    # Slugified URL
    url(r'^(?P<address>.+)/(?P<slug>.*)-$',                components.views.slugified),

    # Tiny URL e.g.
    #   /gdf3Nd~
    # Gets redirected to the canonical URL for the component
    # The tilde prevents potential (although low probability)
    # clashes between shortened URLs and other URLs
    url(r'^(?P<tiny>\w+)~$',                               components.views.tiny),

    # Component methods
    url(r'^(?P<address>.+)@boot$',                         components.views.boot),
    url(r'^(?P<address>.+)@activate$',                     components.views.activate),
    url(r'^(?P<address>.+)@deactivate$',                   components.views.deactivate),
    url(r'^(?P<address>.+)@session$',                      components.views.session),
    url(r'^(?P<address>.+)@ping$',                         components.views.ping),
    url(r'^(?P<address>.+)@save$',                         components.views.method, {'method': 'save'}),
    url(r'^(?P<address>.+)@commit$',                       components.views.commit),
    url(r'^(?P<address>.+)@commits$',                      components.views.commits),
    url(r'^(?P<address>.+)@sync$',                         components.views.method, {'method': 'sync'}),
    url(r'^(?P<address>.+)@received$',                     components.views.received),

    # Stencil methods
    url(r'^(?P<address>.+)@content$',                      components.views.content),
    url(r'^(?P<address>.+)@render$',                       components.views.method, {'method': 'render'}),

    # Sheet methods
    url(r'^(?P<address>.+)@update$',                       components.views.method, {'method': 'update'}),

    # Component Git repo access: distinguished by `.git` followed by query
    url(r'^(?P<address>.+)\.git.*$',                       components.views.git),

    # Component file access: any other url with a dot in it (resolved in view)
    url(r'^(?P<path>(.+)\.(.+))$',                         components.views.file),

    ############### Addresses #################

    # Any other URL needs to be routed to the a canonical URL, index page, or
    # listing of components at the address
    url(r'^(?P<address>.*)$',                              components.views.route),
]
