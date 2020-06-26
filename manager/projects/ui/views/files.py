from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.files import ProjectsFilesViewSet


@login_required
def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Get a list of project files."""
    viewset = ProjectsFilesViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    files = viewset.get_queryset(project)
    return render(
        request, "projects/files/list.html", dict(files=files, project=project)
    )
