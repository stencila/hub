from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from jobs.api.views import ProjectsJobsViewSet
from projects.models.projects import Project


@login_required
def retrieve(request: HttpRequest, *args, **kwargs) -> HttpResponse:
    """
    Retrieve a job.
    """
    # Resolve the account + project names into a project id
    project = Project.objects.get(
        account__name=kwargs.get("account"), name=kwargs.get("project")
    )

    # Get the job (with permissions checking)
    viewset = ProjectsJobsViewSet.init(
        "retrieve", request, args, dict(project=str(project.id), job=kwargs.get("job"))
    )
    job = viewset.get_object()

    # If the ?redirect parameter is present
    # then check if the job is already ready and we
    # can redirect to the result directly
    redirect_on_success = request.GET.get("redirect")
    if redirect_on_success is not None:
        if job.has_ended:
            # TODO: Redirect to the result of the job
            return redirect(job.success_url())

    return render(
        request,
        "projects/jobs/retrieve.html",
        dict(job=job, redirect_on_success=redirect_on_success),
    )
