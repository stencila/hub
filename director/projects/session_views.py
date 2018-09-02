import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import ModelForm, forms
from django.http import HttpResponseRedirect, HttpRequest
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from projects.forms import SessionParametersForm, SessionParametersUpdateForm, SessionParametersCreateForm
from projects.models import SessionParameters
#from projects.view_base import DetailView, owner_access_check


class SessionParametersListView(ListView, LoginRequiredMixin):
    model = SessionParameters
    paginate_by = 100

    def get_queryset(self) -> QuerySet:
        return SessionParameters.objects.filter(owner=self.request.user)


class SessionParametersDetailView(DetailView):
    model = SessionParameters
    create_form_class = SessionParametersCreateForm
    edit_form_class = SessionParametersUpdateForm
    template = "projects/sessionparameters_form.html"
    save_redirect_reverse = "sessionparameters_list"
    is_model_form = True
    model_name = 'SessionParameters'

    def get_initial_instance(self, request: HttpRequest) -> SessionParameters:
        return SessionParameters(owner=request.user)

    def update_and_save_instance(self, instance: SessionParameters, form: SessionParametersForm):
        form.save()

    def check_instance_ownership(self, instance: SessionParameters):
        if not owner_access_check(self.request, instance):
            raise PermissionDenied


class SessionParametersCreateView(CreateView, LoginRequiredMixin):
    form_class = SessionParametersCreateForm
    template_name = 'projects/sessionparameters_form.html'


class SessionParametersUpdateView(UpdateView):
    form_class = SessionParametersUpdateForm
    template_name = 'projects/sessionparameters_form.html'
    model = SessionParameters
