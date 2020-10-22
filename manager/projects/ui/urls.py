from django.urls import include, path, re_path

from manager.paths import RootPaths
from projects.paths import ProjectPaths
from projects.ui.views import files as files_views
from projects.ui.views import jobs as jobs_views
from projects.ui.views import projects as project_views
from projects.ui.views import snapshots as snapshots_views
from projects.ui.views import sources as sources_views

# URLs that must go before `accounts.ui.urls`
before_account_urls = [
    path(RootPaths.projects.value + "/", project_views.list, name="ui-projects-list"),
    path(
        RootPaths.projects.value + "/new/",
        project_views.create,
        name="ui-projects-create",
    ),
    path("open/", project_views.open, name="ui-projects-open",),
    # Redirect /projects/<project_id>/<rest> to <account_name>/<project_name>
    re_path(
        RootPaths.projects.value + r"/(?P<project>\d+)/(?P<rest>.*)",
        project_views.redirect,
        name="ui-projects-redirect",
    ),
    # Redirect /<account_name>/<project_id>/<rest> to <account_name>/<project_name>
    re_path(
        r"^(?P<account>[^/]+)/(?P<project>\d+)/(?P<rest>.*)",
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
                    ProjectPaths.claim.value + "/",
                    project_views.claim,
                    name="ui-projects-claim",
                ),
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
                    ProjectPaths.files.value + "/",
                    include(
                        [
                            re_path(
                                r"(?P<file>.+?)!upload",
                                files_views.upload,
                                name="ui-projects-files-upload",
                            ),
                            re_path(
                                r"(?P<file>.+?)!convert",
                                files_views.convert,
                                name="ui-projects-files-convert",
                            ),
                            re_path(
                                r"(?P<file>.+?)!delete",
                                files_views.destroy,
                                name="ui-projects-files-destroy",
                            ),
                            re_path(
                                r"(?P<file>.+?)!details",
                                files_views.retrieve,
                                name="ui-projects-files-retrieve",
                            ),
                            re_path(
                                r"(?P<file>.+?)!highlight",
                                files_views.highlight,
                                name="ui-projects-files-highlight",
                            ),
                            re_path(
                                r"(?P<prefix>.*)?",
                                files_views.list,
                                name="ui-projects-files-list",
                            ),
                        ]
                    ),
                ),
                path(
                    ProjectPaths.sources.value + "/",
                    include(
                        [
                            path(
                                "", sources_views.list, name="ui-projects-sources-list",
                            ),
                            path(
                                "new/<str:type>",
                                sources_views.create,
                                name="ui-projects-sources-create",
                            ),
                            path(
                                "upload",
                                sources_views.upload,
                                name="ui-projects-sources-upload",
                            ),
                            re_path(
                                r"(?P<source>.+?)!rename",
                                sources_views.rename,
                                name="ui-projects-sources-rename",
                            ),
                            re_path(
                                r"(?P<source>.+?)!delete",
                                sources_views.destroy,
                                name="ui-projects-sources-destroy",
                            ),
                            re_path(
                                r"(?P<source>.+)",
                                sources_views.retrieve,
                                name="ui-projects-sources-retrieve",
                            ),
                        ]
                    ),
                ),
                path(
                    ProjectPaths.snapshots.value + "/",
                    include(
                        [
                            path(
                                "",
                                snapshots_views.list,
                                name="ui-projects-snapshots-list",
                            ),
                            path(
                                "<int:snapshot>",
                                snapshots_views.retrieve,
                                name="ui-projects-snapshots-retrieve",
                            ),
                        ]
                    ),
                ),
                path(
                    ProjectPaths.jobs.value + "/",
                    include(
                        [
                            path("", jobs_views.list, name="ui-projects-jobs-list"),
                            path(
                                "<str:job>",
                                jobs_views.retrieve,
                                name="ui-projects-jobs-retrieve",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    )
]
