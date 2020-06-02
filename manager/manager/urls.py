from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from manager.paths import Paths
from manager.ui.views import (
    favicon,
    handle403,
    handle404,
    handle500,
    home,
    render_template,
    test403,
    test404,
    test500,
    test_messages,
)

urlpatterns = [
    path(Paths.api.value, include("manager.api.urls")),
    path(Paths.favicon.value, favicon),
    path(Paths.me.value + "/", include("users.ui.urls")),
    path(
        "stencila/",
        include(
            [
                path("admin/", admin.site.urls, name="admin"),
                path("test/messages/", test_messages),
                path("test/403/", test403),
                path("test/404/", test404),
                path("test/500/", test500),
            ]
        ),
    ),
    path("", home, name="home"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("debug/", include(debug_toolbar.urls)),
        path("render/<str:template>", render_template),
    ] + urlpatterns


handler403 = handle403
handler404 = handle404
handler500 = handle500
