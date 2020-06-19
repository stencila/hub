from django.urls import include, path

from manager.api.routers import OptionalSlashRouter
from projects.api.views.projects import ProjectsAgentsViewSet, ProjectsViewSet
from projects.api.views.sources import ProjectsSourcesViewSet

projects = OptionalSlashRouter()
projects.register("projects", ProjectsViewSet, "api-projects")

projects_agents = OptionalSlashRouter()
projects_agents.register("agents", ProjectsAgentsViewSet, "api-projects-agents")

projects_sources = OptionalSlashRouter()
projects_sources.register("sources", ProjectsSourcesViewSet, "api-projects-sources")

urlpatterns = projects.urls + [
    path("projects/<project>/", include(projects_agents.urls)),
    path("projects/<project>/", include(projects_sources.urls)),
]
