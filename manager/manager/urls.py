from django.conf import settings
from django.contrib import admin
from django.urls import include, path

import accounts.ui.views.accounts as account_views
import accounts.ui.views.teams as team_views
import accounts.ui.views.users as user_views
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
                path("test/account-quota-exceeded/", test_account_quota_exceeded),
                path("test/403/", test403),
                path("test/404/", test404),
                path("test/500/", test500),
            ]
        ),
    ),

    # Account URLs
    #
    # List personal accounts
    path("users/", account_views.list_users, name="ui-accounts-list-users"),
    # List organizational accounts
    path("orgs/", account_views.list_orgs, name="ui-accounts-list-orgs"),
    # Create a new organizational account (login required)
    path("orgs/new/", account_views.create, name="ui-accounts-create"),
    # Get an account profile
    path("<slug:account>/", account_views.retrieve, name="ui-accounts-retrieve"),
    # Change account setting (login required)
    path("<slug:account>/settings/", account_views.update, name="ui-accounts-update"),
    # Change account users (login required)
    path("<slug:account>/users/", user_views.update, name="ui-accounts-users"),
    # List account teams (login required)
    path("<slug:account>/teams/", team_views.list, name="ui-accounts-teams-list"),
    # Create account team (login required)
    path("<slug:account>/teams/new/", team_views.create, name="ui-accounts-teams-create"),
    # Change account team (login required)
    path("<slug:account>/teams/<slug:team>/", team_views.retrieve, name="ui-accounts-teams-retrieve"),
    # Change account team (login required)
    path("<slug:account>/teams/<slug:team>/settings/", team_views.update, name="ui-accounts-teams-update"),

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
