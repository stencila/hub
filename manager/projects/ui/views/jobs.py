from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from jobs.api.views import ProjectsJobsViewSet


@login_required
def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get a list of project jobs.
    """
    viewset = ProjectsJobsViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    jobs = viewset.get_queryset(project)

    return render(request, "projects/jobs/list.html", dict(project=project, jobs=jobs))


@login_required
def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a job.
    """
    viewset = ProjectsJobsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    job = viewset.get_object(project)

    return render(
        request, "projects/jobs/retrieve.html", dict(project=project, job=job)
    )
