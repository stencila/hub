from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.snapshots import ProjectsSnapshotsViewSet


@login_required
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


@login_required
def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a snapshot of a project.
    """
    viewset = ProjectsSnapshotsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    snapshot = viewset.get_object(project)

    return render(
        request,
        "projects/snapshots/retrieve.html",
        dict(project=project, snapshot=snapshot),
    )
