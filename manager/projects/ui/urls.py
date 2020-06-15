from django.urls import path, re_path

import projects.ui.views.projects as project_views
from manager.paths import RootPaths

# URLs that must go before `accounts.ui.urls`
before_account_urls = [
    path(RootPaths.projects.value + "/", project_views.list, name="ui-projects-list"),
    path(
        RootPaths.projects.value + "/new/",
        project_views.create,
        name="ui-projects-create",
    ),
    re_path(
        r"^(?P<account>[^/]+)/(?P<project>\d+)(?P<rest>.*)",
        project_views.redirect,
        name="ui-projects-redirect",
    ),
]

# URLs that must go after `accounts.ui.urls`
after_account_urls = [
    path(
        "<slug:account>/<slug:project>/",
        project_views.retrieve,
        name="ui-projects-retrieve",
    ),
    path(
        "<slug:account>/<slug:project>/sharing/",
        project_views.sharing,
        name="ui-projects-sharing",
    ),
    path(
        "<slug:account>/<slug:project>/settings/",
        project_views.update,
        name="ui-projects-update",
    ),
]
