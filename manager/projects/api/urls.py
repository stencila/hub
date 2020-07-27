from django.urls import include, path
from rest_framework.routers import Route

from manager.api.routers import OptionalSlashRouter
from projects.api.views.files import ProjectsFilesViewSet
from projects.api.views.projects import ProjectsAgentsViewSet, ProjectsViewSet
from projects.api.views.snapshots import ProjectsSnapshotsViewSet
from projects.api.views.sources import ProjectsSourcesViewSet

projects = OptionalSlashRouter()
projects.register("projects", ProjectsViewSet, "api-projects")

projects_agents = OptionalSlashRouter()
projects_agents.register("agents", ProjectsAgentsViewSet, "api-projects-agents")


class ProjectsFilesRouter(OptionalSlashRouter):
    """
    A custom router for handling file paths.

    This is necessary because paths contain slashes etc.
    """

    routes = [
        Route(
            url=r"^{prefix}/(?P<file>.+?)!history$",
            name="{basename}-history",
            detail=True,
            mapping={"get": "history"},
            initkwargs={},
        ),
        Route(
            url=r"^{prefix}/(?P<file>.+?)!convert$",
            name="{basename}-convert",
            detail=True,
            mapping={"post": "convert"},
            initkwargs={},
        ),
        Route(
            url=r"^{prefix}/(?P<file>.+)$",
            name="{basename}-detail",
            detail=True,
            mapping={"get": "retrieve", "delete": "destroy"},
            initkwargs={},
        ),
        Route(
            url=r"^{prefix}/?$",
            name="{basename}-list",
            detail=False,
            mapping={"get": "list"},
            initkwargs={},
        ),
    ]


projects_files = ProjectsFilesRouter()
projects_files.register("files", ProjectsFilesViewSet, "api-projects-files")

projects_snapshots = OptionalSlashRouter()
projects_snapshots.register(
    "snapshots", ProjectsSnapshotsViewSet, "api-projects-snapshots"
)

projects_sources = OptionalSlashRouter()
projects_sources.register("sources", ProjectsSourcesViewSet, "api-projects-sources")

urlpatterns = projects.urls + [
    path("projects/<project>/", include(projects_agents.urls)),
    path("projects/<project>/", include(projects_files.urls)),
    path("projects/<project>/", include(projects_snapshots.urls)),
    path("projects/<project>/", include(projects_sources.urls)),
]
