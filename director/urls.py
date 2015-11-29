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

from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect

import general.views
import components.views
import users.views

urlpatterns = [

    # Front page
    url(r'^$',                                                       general.views.front),

    # API endpoints
    url(r'^api/v1/',                                                 include('api_v1')),
    # API documentation
    url(r'^api/api.yml',                                             general.views.api_yml),
    url(r'^api/?$',                                                  general.views.api_ui),

    # User management (login, logout etc)
    url(r'^me/signup/?$',                                            users.views.signup),
    url(r'^me/signin/?$',                                            users.views.signin),
    url(r'^me/signout/?$',                                           users.views.signout),
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

    # Administration interface
    url(r'^admin/',                                                  admin.site.urls),

    # Test views
    url(r'^test/400',                                                general.views.test400),
    url(r'^test/403',                                                general.views.test403),
    url(r'^test/404',                                                general.views.test404),
    url(r'^test/500',                                                general.views.test500),
]

# In development, serve static files that are handled by `nginx.conf` when in production
if settings.MODE == 'local':
    # Dynamically generated content
    urlpatterns += static(r'/dynamic/', document_root=os.path.join(settings.BASE_DIR, 'dynamic'))
    # Javascript (and potentially other resources) on get.stenci.la when in production
    # cal be obtained from a local build via a symlink
    if settings.GET_LOCAL:
        urlpatterns += static(r'/get/', document_root='/srv/stencila/store/get')
    else:
        urlpatterns += [
            url(r'^get/(?P<path>.*)$', lambda request, path: HttpResponseRedirect('https://s3-us-west-2.amazonaws.com/get.stenci.la/'+path))
        ]

urlpatterns += [

    # Create a new component
    url(r'^new/(?P<type>\w+)$',                                 components.views.new),

    # Slugified URL
    url(r'^(?P<address>[\w/]+)/(?P<slug>.*)-$',                 components.views.slugified),

    # Tiny URL e.g.
    #   /gdf3Nd~
    # Gets redirected to the canonical URL for the component
    # The tilde prevents potential (although low probability)
    # clashes between shortened URLs and other URLs
    url(r'^(?P<tiny>\w+)~$',                                    components.views.tiny),

    # Component methods
    url(r'^(?P<address>[\w/]+)@activate$',                     components.views.activate),
    url(r'^(?P<address>[\w/]+)@deactivate$',                   components.views.deactivate),
    url(r'^(?P<address>[\w/]+)@save$',                         components.views.method, {'method': 'save'}),
    url(r'^(?P<address>[\w/]+)@commit$',                       components.views.method, {'method': 'commit'}),
    url(r'^(?P<address>[\w/]+)@commits$',                      components.views.commits),
    url(r'^(?P<address>[\w/]+)@sync$',                         components.views.method, {'method': 'sync'}),
    url(r'^(?P<address>[\w/]+)@received$',                     components.views.received),

    # Stencil methods
    url(r'^(?P<address>[\w/]+)@content$',                      components.views.content),
    url(r'^(?P<address>[\w/]+)@render$',                       components.views.method, {'method': 'render'}),

    # Component Git repo access: distinguished by `.git` followed by query
    url(r'^(?P<address>[\w/]+)\.git.*$',                        components.views.git),

    # Component raw file access: any other url with a dot in it (resolved in view)
    url(r'^(?P<path>(.+)\.(.+))$',                              components.views.raw),

    # Any other URL needs to be routed to the a canonical URL, index page, or
    # listing of components at the address
    url(r'^(?P<address>.*)$',                                   components.views.route),
]
