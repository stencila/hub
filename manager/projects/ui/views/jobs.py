from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from jobs.api.views import ProjectsJobsViewSet
from jobs.models import JobMethod, JobStatus


@login_required
def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Get a list of project jobs.
    """
    viewset = ProjectsJobsViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    jobs = viewset.get_queryset(project)

    paginator = Paginator(jobs, 25)
    page_number = request.GET.get("page")
    page_jobs = paginator.get_page(page_number)

    return render(
        request,
        "projects/jobs/list.html",
        dict(
            project=project,
            paginator=paginator,
            jobs=page_jobs,
            status=request.GET.get("status"),
            method=request.GET.get("method"),
            creator=request.GET.get("creator"),
            status_options=[(value, value) for value in JobStatus.categories().keys()],
            method_options=[
                (label.title(), value.lower())
                for (label, value) in JobMethod.as_choices()
            ],
            creator_options=[("Me", "me"), ("Others", "other"), ("Anonymous", "anon")],
            meta=project.get_meta(),
        ),
    )


@login_required
def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a job.
    """
    viewset = ProjectsJobsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    job = viewset.get_object(project)

    return render(
        request,
        "projects/jobs/retrieve.html",
        dict(project=project, job=job, meta=project.get_meta()),
    )
