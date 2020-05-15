from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView

from jobs.models import Job


class JobsListView(LoginRequiredMixin, ListView):
    """Display jobs dashboard to the user."""

    template_name = "jobs_list.html"
    paginate_by = 20

    def get_queryset(self):
        return Job.objects.filter(users__id=self.request.user.id)


class JobsDetailsView(LoginRequiredMixin, DetailView):
    """Display jobs detail page to the user."""

    model = Job
    template_name = "jobs_details.html"
