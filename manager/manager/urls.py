from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import accounts.ui.views as account_views
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

# fmt: off

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
                path("test/403/", test403),
                path("test/404/", test404),
                path("test/500/", test500),
            ]
        ),
    ),

    # Account URLs
    # List personal accounts at `/users`
    path("users/", account_views.list_users, name="ui-accounts-users"),
    # List organizational accounts at `/orgs`
    path("orgs/", account_views.list_orgs, name="ui-accounts-orgs"),
    # Create a new organizational account at `/orgs/new` (login required)
    path("orgs/new/", account_views.create, name="ui-accounts-create"),
    # Change the account settings at `/<str:name>/settings` or `/<int:id>/settings`  (login required)
    path("<str:id>/settings/", account_views.update, name="ui-accounts-update"),
    # Get the account profile at `/<str:name>` or `/<int:id>`
    path("<str:id>/", account_views.retrieve, name="ui-accounts-retrieve"),

    # Home page
    path("", home, name="home"),
]

# fmt: on

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
