from django.urls import path, re_path

import accounts.ui.views.accounts as account_views
import accounts.ui.views.teams as team_views
import accounts.ui.views.users as user_views
from manager.paths import Paths

urlpatterns = [
    path(
        Paths.users.value + "/", account_views.list_users, name="ui-accounts-list-users"
    ),
    path(Paths.orgs.value + "/", account_views.list_orgs, name="ui-accounts-list-orgs"),
    path(Paths.orgs.value + "/new/", account_views.create, name="ui-accounts-create"),
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
    path("<slug:account>/", account_views.retrieve, name="ui-accounts-retrieve"),
    path("<slug:account>/settings/", account_views.update, name="ui-accounts-update"),
    path("<slug:account>/users/", user_views.update, name="ui-accounts-users"),
    path("<slug:account>/teams/", team_views.list, name="ui-accounts-teams-list"),
    path(
        "<slug:account>/teams/new/", team_views.create, name="ui-accounts-teams-create"
    ),
    path(
        "<slug:account>/teams/<slug:team>/",
        team_views.retrieve,
        name="ui-accounts-teams-retrieve",
    ),
    path(
        "<slug:account>/teams/<slug:team>/settings/",
        team_views.update,
        name="ui-accounts-teams-update",
    ),
]
