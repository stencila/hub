from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.snapshots import ProjectsSnapshotsViewSet


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    List snapshots for a project.
    """
    viewset = ProjectsSnapshotsViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    snapshots = viewset.get_queryset(project)

    return render(
        request,
        "projects/snapshots/list.html",
        dict(project=project, snapshots=snapshots),
    )


def retrieve(
    request: HttpRequest, *args, template="projects/snapshots/retrieve.html", **kwargs
) -> HttpResponse:
    """
    Retrieve a snapshot of a project.
    """
    viewset = ProjectsSnapshotsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    snapshot = viewset.get_object(project)

    return render(request, template, dict(project=project, snapshot=snapshot),)
