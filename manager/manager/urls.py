from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from manager.views import (
    favicon,
    handle403,
    handle404,
    handle500,
    home,
    test403,
    test404,
    test500,
)

urlpatterns = [
    path("favicon.ico", favicon),
    path("stencila/admin/", admin.site.urls, name="admin"),
    path("stencila/test/403/", test403),
    path("stencila/test/404/", test404),
    path("stencila/test/500/", test500),
    path("", home, name="home"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("debug/", include(debug_toolbar.urls))] + urlpatterns


handler403 = handle403
handler404 = handle404
handler500 = handle500
