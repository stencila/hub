from django.urls import path

import projects.ui.views.projects as project_views
from manager.paths import Paths

# URLs that must go before `accounts.ui.urls`
before_account_urls = [
    path(Paths.projects.value + "/", project_views.list, name="ui-projects-list"),
    path(
        Paths.projects.value + "/new/", project_views.create, name="ui-projects-create"
    ),
]

# URls that mist go after `accounts.ui.urls`
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
