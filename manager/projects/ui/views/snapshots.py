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
    snapshot_viewset = ProjectsSnapshotsViewSet.init("retrieve", request, args, kwargs)
    project = snapshot_viewset.get_project()
    snapshot = snapshot_viewset.get_object(project=project)
    snapshot_context = snapshot_viewset.get_response_context(instance=snapshot)

    files_viewset = ProjectsFilesViewSet.init("list", request, args, kwargs)
    files = files_viewset.get_queryset(project=project, snapshot=snapshot)
    files_context = files_viewset.get_response_context(queryset=files)

    return render(
        request,
        template,
        dict(**snapshot_context, **files_context, meta=project.get_meta()),
    )
