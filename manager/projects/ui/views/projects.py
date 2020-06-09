from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.projects import ProjectsViewSet


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """List projects."""
    viewset = ProjectsViewSet.init("list", request, args, kwargs)
    projects = viewset.get_queryset()
    return render(request, "projects/list.html", dict(projects=projects))


@login_required
def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Create a project."""
    viewset = ProjectsViewSet.init("create", request, args, kwargs)
    serializer = viewset.get_serializer()
    return render(request, "projects/create.html", dict(serializer=serializer))


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve an project."""
    viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    project, role = viewset.get_project_role()
    return render(request, "projects/retrieve.html", dict(project=project, role=role))


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update an project."""
    viewset = ProjectsViewSet.init("update", request, args, kwargs)
    project, role = viewset.get_project_role()
    serializer = viewset.get_serializer(project)
    return render(
        request,
        "projects/update.html",
        dict(project=project, role=role, serializer=serializer),
    )
