from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView

from jobs.models import Job, JobMethod, JobStatus
from projects.models import ProjectPermissionType
from projects.views.project_views import ProjectPermissionsMixin, ProjectTab


class JobViewMixin(ProjectPermissionsMixin):
    """
    Mixin for the following view classes.

    Extends `ProjectPermissionsMixin` for authorization
    on a per project level.
    """

    def get_context_data(self, **kwargs) -> dict:
        """Add context for when rendering templates."""
        context_data = super().get_context_data(**kwargs)
        context_data["project_tab"] = ProjectTab.JOBS.value
        context_data["canCancel"] = self.has_permission(ProjectPermissionType.EDIT)
        return context_data

    def post(
        self, request: HttpRequest, account_name: str, project_name: str
    ) -> HttpResponse:
        """Handle a POST request."""
        project = ProjectPermissionsMixin.get_object(self, account_name=account_name)
        self.request_permissions_guard(
            request, pk=project.id, permission=ProjectPermissionType.EDIT
        )

        if request.POST.get("action") == "cancel":
            valid_job = project.jobs.filter(pk=request.POST["job_id"])
            if len(valid_job) == 0:
                raise ValueError(
                    "Cannot delete this job as it's not associated with this project."
                )

            try:
                job = Job.objects.get(pk=request.POST["job_id"])
            except Job.DoesNotExist:
                messages.error(
                    request,
                    "Job with ID {} does not exist.".format(request.POST["job_id"]),
                )
            else:
                job.delete()
                messages.success(
                    request,
                    "Job with ID {} was cancelled.".format(request.POST["job_id"]),
                )

        return redirect("project_job_list", account_name, project_name)


class JobListView(JobViewMixin, ListView):
    """Display job list for a project to the user."""

    template_name = "job_list.html"
    paginate_by = 20
    project_permission_required = ProjectPermissionType.VIEW

    def get_queryset(self):
        """
        Get all jobs for the project.

        `ProjectPermissionsMixin.get_object` checks that the
        request user has the required project permission and
        will raise `PermissionDenied` if not.
        """
        project = ProjectPermissionsMixin.get_object(self)
        object_list = project.jobs.all()

        object_list = self._get_status({}, object_list)
        object_list = self._get_method({}, object_list)
        object_list = self._get_users({}, project, object_list)

        return object_list.order_by("-id")

    def get_context_data(self, **kwargs):
        """Update context to supply filter variables for the template."""
        context = super().get_context_data(**kwargs)
        project = ProjectPermissionsMixin.get_object(self)

        context = self._get_status(context)
        context = self._get_method(context)
        context = self._get_users(context, project)

        return context

    def _get_status(self, context, object_list=None):
        """
        Extract the status from the request.

        If a valid context is passed, then we also return the list of all
        available options. If an object_list is provided, filter the results
        if the request variable is valid.
        """
        status = self.request.GET.get("status", "").upper()

        if object_list is not None:
            return self._get_object_list(
                object_list, status != "" and JobStatus.is_member(status), status=status
            )

        options = list(map(lambda s: (s.name, s.value), JobStatus))

        return {
            **context,
            "status_options": sorted(options, key=lambda x: x[0]),
            "status": status,
        }

    def _get_method(self, context, object_list=None):
        """
        Extract the method from the request.

        If a valid context is passed, then we also return the list of all
        available options. If an object_list is provided, filter the results
        if the request variable is valid.
        """
        method = self.request.GET.get("trigger", "").lower()

        if object_list is not None:
            return self._get_object_list(
                object_list, method != "" and JobMethod.is_member(method), method=method
            )

        options = list(map(lambda s: (s.name, s.value), JobMethod))

        return {
            **context,
            "method_options": sorted(options, key=lambda x: x[0]),
            "method": method,
        }

    def _get_users(self, context, project, object_list=None):
        """
        Extract the user from the request.

        If a valid context is passed, then we also return the list of all
        available options. If an object_list is provided, filter the results
        if the request variable is valid.
        """
        by = self.request.GET.get("by", "").lower()
        options = [
            ("Project members", "members"),
            ("Others (Anonymous users)", "anonymous"),
        ]
        exists = [i for i in options if i[1] == by]
        matches = exists[0][1] if len(exists) == 1 else ""

        if object_list is not None:
            return self._get_object_list(
                object_list,
                matches != "",
                creator__isnull=True if matches == "anonymous" else False,
            )

        return {
            **context,
            "by": by,
            "by_options": options,
        }

    def _get_object_list(self, object_list, condition, **kwargs):
        """Get a filtered object_list if the condition is valid."""
        if object_list is not None:
            return object_list.filter(**kwargs) if condition else object_list
        return None


class JobDetailView(JobViewMixin, DetailView):
    """Display job detail page to the user."""

    template_name = "job_detail.html"
    project_permission_required = ProjectPermissionType.VIEW

    def get_object(self) -> Job:
        """Get an individual job, checking that the user permission to view it."""
        project = ProjectPermissionsMixin.get_object(self)
        return project.jobs.get(id=self.kwargs["job"])
