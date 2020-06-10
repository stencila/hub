from django.urls import include, path

from manager.api.routers import OptionalSlashRouter
from projects.api.views.projects import ProjectsViewSet

projects = OptionalSlashRouter()
projects.register("projects", ProjectsViewSet, "api-projects")

urlpatterns = projects.urls
