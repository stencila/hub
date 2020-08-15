from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import projects.ui.urls
from manager.paths import RootPaths
from manager.ui.views import (
    favicon,
    handle403,
    handle404,
    handle500,
    home,
    pricing,
    render_template,
    robots,
    test403,
    test404,
    test500,
    test_account_quota_exceeded,
    test_messages,
)

urlpatterns = [
    path(RootPaths.favicon.value, favicon),
    path(RootPaths.robots.value, robots),
    path(RootPaths.api.value + "/", include("manager.api.urls")),
    path(RootPaths.me.value + "/", include("users.ui.urls")),
    path(RootPaths.pricing.value + "/", pricing, name="ui-pricing"),
    path(
        "stencila/",
        include(
            [
                path("admin/", admin.site.urls, name="admin"),
                path("render/", render_template),
                path("test/messages/", test_messages),
                path("test/account-quota-exceeded/", test_account_quota_exceeded),
                path("test/403/", test403),
                path("test/404/", test404),
                path("test/500/", test500),
            ]
        ),
    ),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("debug/", include(debug_toolbar.urls))]

if settings.CONFIGURATION.endswith("Dev"):
    from manager.storage import serve_local

    for pattern in serve_local():
        urlpatterns = urlpatterns + pattern

# Account and project URL which match other arbitrary URL
# (e.g. /possible-org/potential-project) should come last
# so that they do not 404 for other views.
urlpatterns += [
    path("", include(projects.ui.urls.before_account_urls)),
    path("", include("accounts.ui.urls")),
    path("", include(projects.ui.urls.after_account_urls)),
    path("", home, name="home"),
]

handler403 = handle403
handler404 = handle404
handler500 = handle500
