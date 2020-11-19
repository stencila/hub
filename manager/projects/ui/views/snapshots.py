from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.files import ProjectsFilesViewSet
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
        dict(project=project, snapshots=snapshots, meta=project.get_meta()),
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

    viewset = ProjectsFilesViewSet.init("list", request, args, kwargs)
    files = viewset.get_queryset(project=project, snapshot=snapshot)
    context = viewset.get_response_context(queryset=files)

    return render(
        request, template, dict(snapshot=snapshot, meta=project.get_meta(), **context),
    )
