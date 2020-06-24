from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import select_template

from projects.api.views.sources import ProjectsSourcesViewSet
from projects.models.sources import Source, UploadSource


def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Get a list of project sources."""
    viewset = ProjectsSourcesViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    sources = viewset.get_queryset()
    return render(
        request, "projects/sources.html", dict(project=project, sources=sources)
    )


@login_required
def create(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Create a source.

    Looks for a template with name:

       projects/sources/create_<source-type>.html

    but falls back to using `projects/sources/create.html` with inclusion of:

       projects/sources/_create_<source-type>_fields.html

    falling back to:

       projects/sources/_create_fields.html
    """
    viewset = ProjectsSourcesViewSet.init("create", request, args, kwargs)
    project = viewset.get_project()

    source_type = kwargs.get("type")
    source_class = Source.class_from_type_name(source_type).__name__

    template = select_template(
        [
            "projects/sources/create_{0}.html".format(source_type),
            "projects/sources/create.html",
        ]
    ).template.name
    fields_template = select_template(
        [
            "projects/sources/_create_{0}_fields.html".format(source_type),
            "projects/sources/_create_fields.html",
        ]
    ).template.name

    serializer_class = viewset.get_serializer_class(source_class=source_class)
    serializer = serializer_class()

    return render(
        request,
        template,
        dict(
            project=project,
            serializer=serializer,
            fields_template=fields_template,
            source_class=source_class,
        ),
    )


@login_required
def upload(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Upload files to the project.

    If there is no existing `UploadSource` with the path, then one
    will be created. Otherwise the content of the source will be
    replaced with the uploaded content.
    """
    viewset = ProjectsSourcesViewSet.init("create", request, args, kwargs)
    project = viewset.get_project()

    if request.method == "GET":
        return render(request, "projects/sources/upload.html", dict(project=project))
    elif request.method == "POST":
        files = request.FILES.getlist("files")
        if files:
            for file in files:
                source, created = UploadSource.objects.get_or_create(
                    project=project, path=file.name
                )
                source.file = file
                source.save()
        return redirect("ui-projects-sources", project.account.name, project.name)
    else:
        raise Http404


def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Retrieve a source."""
    viewset = ProjectsSourcesViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    source = viewset.get_object()
    return render(
        request, "projects/sources/retrieve.html", dict(project=project, source=source)
    )


@login_required
def update(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Update a source."""
    viewset = ProjectsSourcesViewSet.init("partial_update", request, args, kwargs)
    instance = viewset.get_object()
    serializer = viewset.get_serializer(instance)
    return render(
        request,
        "projects/sources/update.html",
        dict(source=instance, serializer=serializer),
    )


@login_required
def rename(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Rename (ie change the path of) a source."""
    viewset = ProjectsSourcesViewSet.init("partial_update", request, args, kwargs)
    source = viewset.get_object()
    serializer = viewset.get_serializer(source)
    return render(
        request,
        "projects/sources/rename.html",
        dict(
            serializer=serializer,
            source=source,
            project=source.project,
            account=source.project.account,
        ),
    )


@login_required
def destroy(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Destory a source."""
    viewset = ProjectsSourcesViewSet.init("destroy", request, args, kwargs)
    source = viewset.get_object()
    return render(
        request,
        "projects/sources/destroy.html",
        dict(source=source, project=source.project, account=source.project.account),
    )
