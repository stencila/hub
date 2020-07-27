from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from projects.api.views.files import ProjectsFilesViewSet
from projects.api.views.sources import ProjectsSourcesViewSet
from projects.models.sources import UploadSource
from projects.ui.views.messages import all_messages


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get a list of project files.

    The trailing part of the URL becomes the `prefix` query
    parameter, consistent with API ending e.g.

      /<account>/<project>/files/sub?search=foo

    is equivalent to:

      /api/projects/<project>/files?prefix=sub&search=foo
    """
    request.GET = request.GET.copy()
    request.GET["prefix"] = kwargs.get("prefix")

    viewset = ProjectsFilesViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    files = viewset.get_queryset(project)
    context = viewset.get_response_context(queryset=files)

    all_messages(request, project)

    return render(request, "projects/files/list.html", context)


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get details about a file including it's history.

    Checks that the user has list files and then gets
    all the `File` records matching its path.
    """
    viewset = ProjectsFilesViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    file = viewset.get_object(project)
    upstreams = file.get_upstreams()
    downstreams = file.get_downstreams()
    history = viewset.get_history(project)
    context = viewset.get_response_context(
        account=project.account,
        file=file,
        upstreams=upstreams,
        downstreams=downstreams,
        history=history,
    )

    return render(request, "projects/files/retrieve.html", context)


@login_required
def upload(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Upload a file to the project.

    This view differs from the `sources.upload` view in that it
    allows for uploading a single file, with a pretermined file name.
    """
    viewset = ProjectsSourcesViewSet.init("create", request, args, kwargs)
    project = viewset.get_project()
    path = kwargs.get("file")

    if request.method == "GET":
        return render(
            request, "projects/files/upload.html", dict(project=project, path=path)
        )
    elif request.method == "POST":
        file = request.FILES.get("file")
        if file:
            source, created = UploadSource.objects.get_or_create(
                project=project, path=path
            )
            source.file = file
            source.save()

            job = source.pull(request.user)
            job.dispatch()

        return redirect(
            "ui-projects-files-retrieve", project.account.name, project.name, path
        )
    else:
        raise Http404


@login_required
def convert(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Convert a file to another format.
    """
    viewset = ProjectsFilesViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    file = viewset.get_object(project)

    format = request.GET.get("format")
    if format:
        path = Path(file.path).stem + "." + format
    else:
        path = None
    next = request.GET.get("next")

    context = viewset.get_response_context(
        file=file, path=path, format=format, next=next
    )

    return render(request, "projects/files/convert.html", context)


@login_required
def destroy(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Destroy a file.
    """
    viewset = ProjectsFilesViewSet.init("destroy", request, args, kwargs)
    project = viewset.get_project()
    file = viewset.get_object(project)
    context = viewset.get_response_context(file=file)

    return render(request, "projects/files/destroy.html", context)
