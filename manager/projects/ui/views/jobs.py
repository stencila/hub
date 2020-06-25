from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from jobs.api.views import ProjectsJobsViewSet


@login_required
def list(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """Get a list of project jobs."""
    viewset = ProjectsJobsViewSet.init("list", request, args, kwargs)
    project = viewset.get_project()
    jobs = viewset.get_queryset(project)
    return render(request, "projects/jobs/list.html", dict(jobs=jobs, project=project))


@login_required
def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a job.
    """
    viewset = ProjectsJobsViewSet.init("retrieve", request, args, kwargs)
    project = viewset.get_project()
    job = viewset.get_object(project)

    # If the ?redirect parameter is present
    # then check if the job is already ready and we
    # can redirect to the result directly
    redirect_on_success = request.GET.get("redirect")
    # if redirect_on_success is not None:
    #    if job.has_ended:
    #        # TODO: Redirect to the result of the job
    #        return redirect(job.success_url())

    return render(
        request,
        "projects/jobs/retrieve.html",
        dict(job=job, project=project, redirect_on_success=redirect_on_success),
    )
