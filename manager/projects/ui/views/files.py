from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.files import ProjectsFilesViewSet


@login_required
def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get a list of project files.

    The trailing part of the URL becomes the `prefix` query
    parameter, consistent with API ending e.g.

      /<account>/<project>/files/sub?search=foo

    is equivalent to:

      /api/projects/<project>/files?prefix=sub&search=foo
    """
    prefix = kwargs.get("prefix")
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    request.GET = request.GET.copy()
    request.GET["prefix"] = prefix
    request.GET["aggregate"] = True

    viewset = ProjectsFilesViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    files = viewset.get_queryset(project)

    # List of tuples for directory breadcrumbs
    dirs = [("root", "")]
    path = ""
    for name in prefix.split("/"):
        if name:
            path += name + "/"
            dirs.append((name, path))

    return render(
        request,
        "projects/files/list.html",
        dict(prefix=prefix, dirs=dirs, files=files, project=project,),
    )
