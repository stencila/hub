import datetime
import typing

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpRequest, HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, TemplateView


from .models import Project, Source, FileSource
from .source_forms import FileSourceForm


class FileSourceCreateView(LoginRequiredMixin, CreateView):
    model = FileSource
    form_class = FileSourceForm
    template_name = 'projects/filesource_create.html'

    def get_context_data(self, *args, **kwargs):
        """
        Override to add project to the template context
        """
        data = super().get_context_data(*args, **kwargs)
        data['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return data

    def form_valid(self, form):
        """
        Override to set the project for the `FileSource` and redirect
        back to that project
        """
        pk = self.kwargs['pk']
        filesource = form.save(commit=False)
        filesource.project = get_object_or_404(Project, pk=pk)
        filesource.save()
        return HttpResponseRedirect(
            reverse("project_files", kwargs={'pk': pk})
        )


class FileSourceUploadView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/filesource_upload.html'

    @staticmethod
    def post(request: HttpRequest, pk: int) -> HttpResponse:
        project = get_object_or_404(Project, pk=pk)

        files = request.FILES.getlist('file')
        for file in files:
            source = FileSource.objects.create(
                project=project,
                path=file,
                file=file
            )
            source.save()

        return HttpResponse()


class SourceUpdateView(LoginRequiredMixin, CreateView):
    pass


class SourceDeleteView(LoginRequiredMixin, DeleteView):
    model = Source
    template_name = 'confirm_delete.html'

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})
