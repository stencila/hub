from django.urls import include, path, re_path

import projects.ui.views.projects as project_views
import projects.ui.views.sources as sources_views
from manager.paths import RootPaths
from projects.paths import ProjectPaths

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
        include(
            [
                path("", project_views.retrieve, name="ui-projects-retrieve",),
                path(
                    ProjectPaths.sharing.value + "/",
                    project_views.sharing,
                    name="ui-projects-sharing",
                ),
                path(
                    ProjectPaths.settings.value + "/",
                    project_views.update,
                    name="ui-projects-update",
                ),
                path(
                    ProjectPaths.sources.value + "/",
                    include(
                        [
                            path(
                                "new/<str:type>",
                                sources_views.create,
                                name="ui-projects-sources-create",
                            ),
                            path(
                                "delete/<str:source>",
                                sources_views.destroy,
                                name="ui-projects-sources-destroy",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    )
]
