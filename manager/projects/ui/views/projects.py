from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect as redir
from django.shortcuts import render

from projects.api.serializers import ProjectDestroySerializer
from projects.api.views.projects import ProjectsViewSet


def redirect(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Redirect from a project `id` URL to a project `name` URL.

    For instances where we need to redirect to the project using `id`
    (e.g. because its name may have changed in a form).
    This uses `get_object` to ensure the same access control applies
    to the redirect.
    """
    viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_object()
    return redir(
        "/{0}/{1}{2}".format(project.account.name, project.name, kwargs["rest"])
    )


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """List projects."""
    viewset = ProjectsViewSet.init("list", request, args, kwargs)
    queryset = viewset.get_queryset()
    return render(request, "projects/list.html", dict(projects=queryset))


@login_required
def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Create a project."""
    viewset = ProjectsViewSet.init("create", request, args, kwargs)
    serializer = viewset.get_serializer()
    return render(request, "projects/create.html", dict(serializer=serializer))


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a project.

    Currently redirect to the project sources, but in the future
    could be an overview page, with a preview of the main document etc.
    """
    viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_object()
    return redir("ui-projects-sources-list", project.account.name, project.name)


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update a project."""
    viewset = ProjectsViewSet.init("partial_update", request, args, kwargs)
    instance = viewset.get_object()
    serializer = viewset.get_serializer(instance)
    destroy_serializer = ProjectDestroySerializer()
    return render(
        request,
        "projects/update.html",
        dict(
            project=instance,
            serializer=serializer,
            destroy_serializer=destroy_serializer,
        ),
    )


@login_required
def sharing(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve a project's sharing settings."""
    viewset = ProjectsViewSet.init("retrieve", request, args, kwargs)
    instance = viewset.get_object()
    return render(request, "projects/sharing.html", dict(project=instance))
