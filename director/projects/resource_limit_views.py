import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import ModelForm, forms
from django.http import HttpResponseRedirect, HttpRequest
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView

from projects.forms import ResourceLimitForm, ResourceLimitUpdateForm, ResourceLimitCreateForm
from projects.models import ResourceLimit
from projects.view_base import DetailView, owner_access_check


class ResourceLimitListView(ListView, LoginRequiredMixin):
    model = ResourceLimit
    paginate_by = 100

    def get_queryset(self) -> QuerySet:
        return ResourceLimit.objects.filter(owner=self.request.user)


class ResourceLimitDetailView(DetailView):
    model = ResourceLimit
    create_form_class = ResourceLimitCreateForm
    edit_form_class = ResourceLimitUpdateForm
    template = "projects/resourcelimit_form.html"
    save_redirect_reverse = "resourcelimit_list"
    is_model_form = True
    model_name = 'ResourceLimit'

    def get_initial_instance(self, request: HttpRequest) -> ResourceLimit:
        return ResourceLimit(owner=request.user)

    def update_and_save_instance(self, instance: ResourceLimit, form: ResourceLimitForm):
        form.save()

    def check_instance_ownership(self, instance: ResourceLimit):
        if not owner_access_check(self.request, instance):
            raise PermissionDenied


class ResourceLimitCreateView(CreateView, LoginRequiredMixin):
    form_class = ResourceLimitCreateForm
    template_name = 'projects/resourcelimit_form.html'


class ResourceLimitUpdateView(UpdateView):
    form_class = ResourceLimitUpdateForm
    template_name = 'projects/resourcelimit_form.html'
    model = ResourceLimit
