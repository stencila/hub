from django.urls import include, path, re_path

from manager.paths import RootPaths
from projects.paths import ProjectPaths
from projects.ui.views import files, jobs, projects, reviews, snapshots, sources

# URLs that must go before `accounts.ui.urls`
before_account_urls = [
    path(RootPaths.projects.value + "/", projects.list, name="ui-projects-list"),
    path(
        RootPaths.projects.value + "/new/", projects.create, name="ui-projects-create",
    ),
    path("open/", projects.open, name="ui-projects-open",),
    # Redirect /projects/<project_id>/<rest> to <account_name>/<project_name>
    re_path(
        RootPaths.projects.value + r"/(?P<project>\d+)/(?P<rest>.*)",
        projects.redirect,
        name="ui-projects-redirect",
    ),
    # Redirect /<account_name>/<project_id>/<rest> to <account_name>/<project_name>
    re_path(
        r"^(?P<account>[^/]+)/(?P<project>\d+)/(?P<rest>.*)",
        projects.redirect,
        name="ui-projects-redirect",
    ),
]

# URLs that must go after `accounts.ui.urls`
after_account_urls = [
    path(
        "<slug:account>/<slug:project>/",
        include(
            [
                path("", projects.retrieve, name="ui-projects-retrieve",),
                path(
                    ProjectPaths.claim.value + "/",
                    projects.claim,
                    name="ui-projects-claim",
                ),
                path(
                    ProjectPaths.sharing.value + "/",
                    projects.sharing,
                    name="ui-projects-sharing",
                ),
                path(
                    ProjectPaths.settings.value + "/",
                    projects.update,
                    name="ui-projects-update",
                ),
                path(
                    ProjectPaths.files.value + "/",
                    include(
                        [
                            re_path(
                                r"(?P<file>.+?)!upload",
                                files.upload,
                                name="ui-projects-files-upload",
                            ),
                            re_path(
                                r"(?P<file>.+?)!convert",
                                files.convert,
                                name="ui-projects-files-convert",
                            ),
                            re_path(
                                r"(?P<file>.+?)!delete",
                                files.destroy,
                                name="ui-projects-files-destroy",
                            ),
                            re_path(
                                r"(?P<file>.+?)!details",
                                files.retrieve,
                                name="ui-projects-files-retrieve",
                            ),
                            re_path(
                                r"(?P<file>.+?)!highlight",
                                files.highlight,
                                name="ui-projects-files-highlight",
                            ),
                            re_path(
                                r"(?P<prefix>.*)?",
                                files.list,
                                name="ui-projects-files-list",
                            ),
                        ]
                    ),
                ),
                path(
                    ProjectPaths.sources.value + "/",
                    include(
                        [
                            path("", sources.list, name="ui-projects-sources-list",),
                            path(
                                "new/<str:type>",
                                sources.create,
                                name="ui-projects-sources-create",
                            ),
                            path(
                                "upload",
                                sources.upload,
                                name="ui-projects-sources-upload",
                            ),
                            re_path(
                                r"(?P<source>.+?)!rename",
                                sources.rename,
                                name="ui-projects-sources-rename",
                            ),
                            re_path(
                                r"(?P<source>.+?)!delete",
                                sources.destroy,
                                name="ui-projects-sources-destroy",
                            ),
                            re_path(
                                r"(?P<source>.+)",
                                sources.retrieve,
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
                                "", snapshots.list, name="ui-projects-snapshots-list",
                            ),
                            path(
                                "<int:snapshot>",
                                snapshots.retrieve,
                                name="ui-projects-snapshots-retrieve",
                            ),
                        ]
                    ),
                ),
                path(
                    ProjectPaths.reviews.value + "/",
                    include(
                        [
                            path("", reviews.list, name="ui-projects-reviews-list"),
                            path(
                                "<int:review>",
                                reviews.retrieve,
                                name="ui-projects-reviews-retrieve",
                            ),
                            path(
                                "new",
                                reviews.create,
                                name="ui-projects-reviews-create",
                            ),
                        ]
                    ),
                ),
                path(
                    ProjectPaths.jobs.value + "/",
                    include(
                        [
                            path("", jobs.list, name="ui-projects-jobs-list"),
                            path(
                                "<str:job>",
                                jobs.retrieve,
                                name="ui-projects-jobs-retrieve",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    )
]
