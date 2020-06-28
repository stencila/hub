from django.urls import include, path

from manager.api.routers import OptionalSlashRouter
from projects.api.views.files import ProjectsFilesViewSet
from projects.api.views.projects import ProjectsAgentsViewSet, ProjectsViewSet
from projects.api.views.snapshots import ProjectsSnapshotsViewSet
from projects.api.views.sources import ProjectsSourcesViewSet

projects = OptionalSlashRouter()
projects.register("projects", ProjectsViewSet, "api-projects")

projects_agents = OptionalSlashRouter()
projects_agents.register("agents", ProjectsAgentsViewSet, "api-projects-agents")

projects_files = OptionalSlashRouter()
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
