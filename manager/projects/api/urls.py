from django.urls import include, path

from manager.api.routers import OptionalSlashRouter
from projects.api.views.projects import ProjectsAgentsViewSet, ProjectsViewSet

projects = OptionalSlashRouter()
projects.register("projects", ProjectsViewSet, "api-projects")

projects_agents = OptionalSlashRouter()
projects_agents.register("agents", ProjectsAgentsViewSet, "api-projects-agents")

urlpatterns = projects.urls + [
    path("projects/<project>/", include(projects_agents.urls))
]
