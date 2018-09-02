import datetime
import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, UpdateView, ListView

from .source_forms import FilesSourceUpdateForm, FilesSourceCreateForm
from .source_models import FilesSource, FilesSourceFile, Source, AvailableSourceType

T = typing.TypeVar('T')


class FilesSourceReadView(LoginRequiredMixin, DetailView):
    model = FilesSource
    template_name = 'projects/filesproject_update.html'

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
    @staticmethod
    def post(request: HttpRequest, pk: int) -> HttpResponse:
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
    @staticmethod
    def delete(request: HttpRequest, pk: int, file: int) -> HttpResponse:
        files_source = get_object_or_404(FilesSource, pk=pk)

        if not owner_access_check(request, files_source, 'creator'):
            raise PermissionDenied
        file = get_object_or_404(FilesSourceFile, source=files_source, pk=file)
        file.delete()
        return JsonResponse(files_source.serialize())


class SourceListView(ListView, LoginRequiredMixin):
    model = Source

    def get_queryset(self):
        if self.request.user.is_staff:
            return Source.objects.all()
        else:
            return Source.objects.filter(creator=self.request.user)


class SourceDetailRouteView(View):
    """Renders a page that lets the user choose what kind of Source to Source to create"""

    @staticmethod
    def get(request: HttpRequest) -> HttpResponse:
        return render(request, "projects/source_route.html",
                      {
                          "source_types": map(lambda x: x, AvailableSourceType)
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


class SourceDetailView(DetailView):
    current_project_type: str = None

    parameter_lookup = {
        "files": DetailViewParameters(
            FilesSource,
            FilesSourceCreateForm,
            FilesSourceUpdateForm,
            True,
            "projects/sources/filessource_detail.html",
            "source_list",
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
            return reverse("source_detail", args=(self.current_project_type, instance.pk,))

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
