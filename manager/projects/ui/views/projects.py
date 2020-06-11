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
    """Retrieve a project."""
    viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_object()
    return render(
        request, "projects/retrieve.html", dict(project=project, role=project.role)
    )


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update a project."""
    viewset = ProjectsViewSet.init("partial_update", request, args, kwargs)
    project = viewset.get_object()
    serializer = viewset.get_serializer(project)
    return render(
        request,
        "projects/update.html",
        dict(project=project, role=project.role, serializer=serializer),
    )


@login_required
def sharing(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve a project's sharing settings."""
    viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_object()
    return render(
        request, "projects/sharing.html", dict(project=project, role=project.role)
    )
