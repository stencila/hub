from django.views.generic import ListView, DetailView

from jobs.models import Job
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


class JobDetailView(JobViewMixin, DetailView):
    """Display job detail page to the user."""

    template_name = "job_detail.html"
    project_permission_required = ProjectPermissionType.VIEW

    def get_object(self) -> Job:
        """Get an individual job, checking that the user permission to view it."""
        project = ProjectPermissionsMixin.get_object(self)
        return project.jobs.get(id=self.kwargs["job"])
