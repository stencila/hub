from django.urls import include, path, re_path

from accounts.paths import AccountPaths
from accounts.ui.views import accounts as account_views
from accounts.ui.views import teams as team_views
from accounts.ui.views import users as user_views
from manager.paths import RootPaths

urlpatterns = [
    path(
        RootPaths.users.value + "/",
        account_views.list_users,
        name="ui-accounts-list-users",
    ),
    path(
        RootPaths.orgs.value + "/",
        account_views.list_orgs,
        name="ui-accounts-list-orgs",
    ),
    path(
        RootPaths.orgs.value + "/new/", account_views.create, name="ui-accounts-create"
    ),
    re_path(
        r"^(?P<account>[^/]+)/teams/(?P<team>\d+)(?P<rest>.*)",
        team_views.redirect,
        name="ui-accounts-teams-redirect",
    ),
    re_path(
        r"^(?P<account>\d+)(?P<rest>.*)",
        account_views.redirect,
        name="ui-accounts-redirect",
    ),
    path(
        "<slug:account>/",
        include(
            [
                path("", account_views.retrieve, name="ui-accounts-retrieve"),
                path(
                    AccountPaths.settings.value + "/",
                    include(
                        [
                            path("", account_views.update, name="ui-accounts-update",),
                            path(
                                "image",
                                account_views.update_image,
                                name="ui-accounts-update-image",
                            ),
                        ]
                    ),
                ),
                path(
                    AccountPaths.plan.value + "/",
                    account_views.plan,
                    name="ui-accounts-plan",
                ),
                path(
                    AccountPaths.users.value + "/",
                    user_views.update,
                    name="ui-accounts-users",
                ),
                path(
                    AccountPaths.teams.value + "/",
                    include(
                        [
                            path("", team_views.list, name="ui-accounts-teams-list"),
                            path(
                                "new/",
                                team_views.create,
                                name="ui-accounts-teams-create",
                            ),
                            path(
                                "<slug:team>/",
                                team_views.retrieve,
                                name="ui-accounts-teams-retrieve",
                            ),
                            path(
                                "<slug:team>/settings/",
                                team_views.update,
                                name="ui-accounts-teams-update",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
]
