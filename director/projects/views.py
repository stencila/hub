import datetime
import typing

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, QuerySet
from django.http import JsonResponse, HttpResponse, HttpRequest, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    View,
    ListView,
    RedirectView,
    DetailView as DjangoDetailView
)
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)

from projects.view_base import DetailView, T, owner_access_check
from .models import (
    Project,
    FilesSource, FilesSourceFile,
    ResourceLimit, DataSource, AvailableDataSourceType)
from .forms import (
    ProjectCreateForm,
    FilesSourceUpdateForm,
    ProjectForm, get_initial_form_data_from_project, update_project_from_form_data, ProjectUpdateForm,
    FilesSourceCreateForm)


class OldProjectListView(ListView):
    model = Project
    paginate_by = 100

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Project.objects.filter(
                Q(creator=self.request.user) | Q(public=True)
            )
        else:
            return Project.objects.filter(public=True)


class ProjectListView(View):
    def get_project_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return Project.objects.filter(
                Q(creator=self.request.user) | Q(public=True)
            )
        else:
            return Project.objects.filter(public=True)

    def get_resource_limits_queryset(self) -> QuerySet:
        if self.request.user.is_authenticated:
            return ResourceLimit.objects.filter(owner=self.request.user)

        return ResourceLimit.objects.none()

    def get(self, request) -> HttpResponse:
        projects = self.get_project_queryset()
        resource_limits = self.get_resource_limits_queryset()

        return render(request, "projects/project_list.html", {
            "projects": projects,
            "resource_limits": resource_limits
        })


class ProjectDetailView(DetailView):
    model = Project
    create_form_class = ProjectCreateForm
    edit_form_class = ProjectUpdateForm
    template = "projects/project_create.html"
    model_name = "Project"
    save_redirect_reverse = "project_list"

    def get_initial_instance(self, request: HttpRequest) -> Project:
        return Project(creator=self.request.user)

    def get_form_initial(self, request: HttpRequest, instance: typing.Optional[Project] = None) -> dict:
        return get_initial_form_data_from_project(instance)

    def form_post_create(self, request: HttpRequest, form: ProjectForm) -> None:
        form.populate_choice_fields(request.user)

    def update_and_save_instance(self, instance: Project, form: forms.Form):
        update_project_from_form_data(instance, form.cleaned_data)
        instance.save()

    def check_instance_ownership(self, instance: Project):
        if not (instance.public or owner_access_check(self.request, instance, 'creator')):
            raise PermissionDenied


class ProjectCreateView(LoginRequiredMixin, FormView):
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def get_success_url(self):
        return reverse('project_update', args=[self.project.id])

    def form_valid(self, form):
        self.project = Project.create(
            project_type=form.cleaned_data['type'],
            creator=self.request.user
        )
        return super().form_valid(form)


class ProjectReadView(LoginRequiredMixin, DjangoDetailView):
    model = Project
    fields = ['address']
    template_name = 'projects/project_read.html'


class ProjectUpdateView(LoginRequiredMixin, RedirectView):
    """
    Generic view for updating a project which redirects to
    the type-specific update view.
    """

    def get_redirect_url(self, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        return reverse('%s_update' % project.type, args=[kwargs['pk']])


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_delete.html'
    success_url = reverse_lazy('project_list')


class ProjectArchiveView(LoginRequiredMixin, View):

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        archive = project.pull()
        body = archive.getvalue()

        response = HttpResponse(body, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format('project.name')
        return response


class FilesSourceReadView(LoginRequiredMixin, DetailView):
    model = FilesSource
    template_name = 'projects/fileproject_read.html'

    def get(self, request, pk):
        project = get_object_or_404(FilesSource, pk=pk)
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return JsonResponse(project.serialize())
        else:
            return render(request, self.template_name, project)


class FilesSourceUpdateView(LoginRequiredMixin, UpdateView):
    model = FilesSource
    form_class = FilesSourceUpdateForm
    template_name = 'projects/filesproject_update.html'
    success_url = reverse_lazy('project_list')


class FilesSourceUploadView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        files_source = get_object_or_404(FilesSource, pk=pk)

        if not owner_access_check(request, files_source, 'creator'):
            raise PermissionDenied

        files = request.FILES.getlist('file')
        for file in files:
            instance = FilesSourceFile.objects.create(
                source=files_source,
                name=file,
                file=file,
                modified=datetime.datetime.now(tz=timezone.utc)
            )
            instance.save()
        return JsonResponse(files_source.serialize())


class FilesProjectRemoveView(LoginRequiredMixin, View):
    def delete(self, request: HttpRequest, pk: int, file: int) -> HttpResponse:
        files_source = get_object_or_404(FilesSource, pk=pk)

        if not owner_access_check(request, files_source, 'creator'):
            raise PermissionDenied
        file = get_object_or_404(FilesSourceFile, source=files_source, pk=file)
        file.delete()
        return JsonResponse(files_source.serialize())


class DataSourceListView(ListView):
    model = DataSource


class DataSourceDetailRouteView(View):
    """Renders a page that lets the user choose what kind of Source to DataSource to create"""

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "projects/datasource_route.html",
                      {
                          "source_types": map(lambda x: x, AvailableDataSourceType)
                          # django doesn't know how to iterate enums in templates so convert it to map here
                      })


class DetailViewParameters(typing.NamedTuple):
    model: typing.Type
    create_form_class: typing.Type[forms.Form]
    edit_form_class: typing.Type[forms.Form]
    is_model_form: bool
    template: str
    save_redirect_reverse: str
    model_name: str


class DataSourceDetailView(DetailView):
    current_project_type: str = None

    parameter_lookup = {
        "files": DetailViewParameters(
            FilesSource,
            FilesSourceCreateForm,
            FilesSourceUpdateForm,
            True,
            "projects/sources/filessource_detail.html",
            "datasource_list",
            "Files Source"
        )
    }

    def assign_type_specific_variables(self, project_type: str):
        """
        This same detail view can be used dynamically with different Project Types, this method assigns the parameters
        from the parameter_lookup onto `self`.
        """
        if project_type not in self.parameter_lookup:
            raise Http404

        self.current_project_type = project_type

        parameters = self.parameter_lookup[project_type]

        self.model = parameters.model
        self.create_form_class = parameters.create_form_class
        self.edit_form_class = parameters.edit_form_class
        self.is_model_form = parameters.is_model_form
        self.template = parameters.template
        self.save_redirect_reverse = parameters.save_redirect_reverse
        self.model_name = parameters.model_name

    def form_post_create(self, request: HttpRequest, form: forms.Form):
        form.fields['project'].queryset = Project.objects.filter(creator=request.user)

    def get_post_save_redirect_url(self, instance: T, was_create: bool) -> str:
        if was_create:
            return reverse("datasource_detail", args=(self.current_project_type, instance.pk,))

        return super().get_post_save_redirect_url(instance, was_create)

    def get_initial_instance(self, request: HttpRequest) -> T:
        return self.model(creator=request.user)

    def update_and_save_instance(self, instance: T, form: forms.Form):
        form.save()

    def get(self, request: HttpRequest, project_type: str, pk: typing.Optional[int] = None) -> HttpResponse:
        self.assign_type_specific_variables(project_type)

        return super().get(request, pk)

    def post(self, request: HttpRequest, project_type: str, pk: typing.Optional[int] = None) -> HttpResponse:
        self.assign_type_specific_variables(project_type)

        return super().post(request, pk)
