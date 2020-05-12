from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class JobsListView(LoginRequiredMixin, TemplateView):
    """Display jobs dashboard to the user."""

    template_name = "jobs_list.html"
