from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import projects.ui.urls
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
    test_account_quota_exceeded,
    test_messages,
)

urlpatterns = [
    path(Paths.api.value + "/", include("manager.api.urls")),
    path(Paths.favicon.value, favicon),
    path(Paths.me.value + "/", include("users.ui.urls")),
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
    path("", include(projects.ui.urls.before_account_urls)),
    path("", include("accounts.ui.urls")),
    path("", include(projects.ui.urls.after_account_urls)),
    path("", home, name="home"),
]

handler403 = handle403
handler404 = handle404
handler500 = handle500

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static

    urlpatterns = (
        [path("debug/", include(debug_toolbar.urls))]
        + urlpatterns
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    )
