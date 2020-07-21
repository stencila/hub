from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from projects.api.views.files import ProjectsFilesViewSet
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
