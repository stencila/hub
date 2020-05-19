from django.views.generic import ListView, DetailView

from jobs.models import Job, JobStatus, JobMethod
from projects.models import ProjectPermissionType
from projects.views.project_views import ProjectTab, ProjectPermissionsMixin


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
        return context_data


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
        return project.jobs.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = ProjectPermissionsMixin.get_object(self)
        object_list = project.jobs.all()

        status = self.request.GET.get("status")
        status_options = list(map(lambda s: (s.name, s.value), JobStatus))

        method = self.request.GET.get("trigger")
        method_options = list(map(lambda s: (s.name, s.value), JobMethod))

        if status and JobStatus.is_member(status.upper()):
            status = status.upper()
            object_list = object_list.filter(status=status)

        if method and JobMethod.is_member(method.lower()):
            method = method.lower()
            object_list = object_list.filter(method=method)

        context["object_list"] = object_list
        context["status_options"] = sorted(status_options, key=lambda x: x[0])
        context["status"] = status

        context["method_options"] = sorted(method_options, key=lambda x: x[0])
        context["method"] = method

        context["by"] = self.request.GET.get("by")
        context["by_options"] = [
            ("Project members", "members"),
            ("Others (Anonymous users)", "anonymous"),
        ]

        return context


class JobDetailView(JobViewMixin, DetailView):
    """Display job detail page to the user."""

    template_name = "job_detail.html"
    project_permission_required = ProjectPermissionType.VIEW

    def get_object(self) -> Job:
        """Get an individual job, checking that the user permission to view it."""
        project = ProjectPermissionsMixin.get_object(self)
        return project.jobs.get(id=self.kwargs["job"])
