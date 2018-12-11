import os
import typing
from os.path import dirname

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from projects.permission_models import ProjectPermissionType
from projects.project_views import ProjectPermissionsMixin
from projects.source_edit import SourceEditContext, SourceContentFacade
from projects.source_operations import strip_directory
from .models import Project, Source, FileSource, DropboxSource, GithubSource
from .source_forms import FileSourceForm, GithubSourceForm, SourceUpdateForm


class SourceCreateView(LoginRequiredMixin, ProjectPermissionsMixin, CreateView):
    """A base class for view for creating new project sources."""

    project_permission_required = ProjectPermissionType.EDIT

    def form_valid(self, form):
        """Override to set the project for the `Source` and redirect back to that project."""
        pk = self.kwargs['pk']
        file_source = form.save(commit=False)
        file_source.project = get_object_or_404(Project, pk=pk)
        file_source.save()
        return HttpResponseRedirect(
            reverse("project_files", kwargs={'pk': pk})
        )


class FileSourceCreateView(SourceCreateView):
    """A view for creating a new, emtpy local file in the project."""

    model = FileSource
    form_class = FileSourceForm
    template_name = 'projects/filesource_create.html'


class DropboxSourceCreateView(SourceCreateView):
    """A view for creating a Dropbox project source."""

    model = DropboxSource
    template_name = 'projects/dropboxsource_create.html'


class GithubSourceCreateView(SourceCreateView):
    """A view for creating a Github project source."""

    model = GithubSource
    form_class = GithubSourceForm
    template_name = 'projects/githubsource_create.html'


class FileSourceUploadView(LoginRequiredMixin, ProjectPermissionsMixin, DetailView):
    """A view for uploading one or more files into the project."""

    model = Project
    template_name = 'projects/filesource_upload.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get_context_data(self, **kwargs):
        self.perform_project_fetch(self.request.user, self.kwargs['pk'])
        context_data = super().get_context_data(**kwargs)
        context_data['upload_directory'] = self.request.GET.get('directory', '')
        return context_data

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.perform_project_fetch(request.user, pk)
        self.test_required_project_permission()

        directory = request.GET.get('directory', '')
        while directory.endswith('/'):
            directory = directory[:-1]

        files = request.FILES.getlist('file')
        for file in files:
            if directory:
                file_path = '{}/{}'.format(directory, file.name)
            else:
                file_path = file.name

            source = FileSource.objects.create(
                project=self.project,
                path=file_path,
                file=file
            )
            source.save()

        return HttpResponse()


class FileSourceOpenView(LoginRequiredMixin, ProjectPermissionsMixin, DetailView):
    project_permission_required = ProjectPermissionType.VIEW

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['file_content'] = self.object.pull()
        return data

    def render(self, request: HttpRequest, editing_context: SourceEditContext,
               extra_context: typing.Optional[dict] = None) -> HttpResponse:
        render_context = {
            'file_path': editing_context.path,
            'file_extension': editing_context.extension,
            'file_content': editing_context.content,
            'file_editable': editing_context.editable,
            'source': editing_context.source,
            'supports_commit_message': editing_context.supports_commit_message
        }
        render_context.update(extra_context or {})
        return render(request, 'projects/source_open.html', self.get_render_context(render_context))

    @staticmethod
    def get_default_commit_message(request: HttpRequest):
        return 'Commit from Stencila Hub User {}'.format(request.user)

    def get(self, request: HttpRequest, project_pk: int, pk: int, path: str) -> HttpResponse:
        source = self.get_source(request.user, project_pk, pk)

        content_facade = SourceContentFacade(source, request, path)

        return self.render(request, content_facade.get_edit_context(), {
            'default_commit_message': self.get_default_commit_message(request)
        })

    @staticmethod
    def get_github_repository_path(source, file_path):
        repo_path = os.path.join(source.subpath, strip_directory(file_path, source.path))
        return repo_path

    def post(self, request: HttpRequest, project_pk: int, pk: int, path: str) -> HttpResponse:
        self.perform_project_fetch(request.user, project_pk)

        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

        source = self.get_source(request.user, project_pk, pk)

        content_facade = SourceContentFacade(source, request, path)
        commit_message = request.POST.get('commit_message') or self.get_default_commit_message(request)
        if not content_facade.update_content(request.POST['file_content'], commit_message):
            return self.render(request, content_facade.get_edit_context(), {
                'default_commit_message': commit_message or self.get_default_commit_message(request)
            })

        messages.success(request, 'Content of {} updated.'.format(os.path.basename(path)))

        directory = dirname(path)

        if directory:
            reverse_name = 'project_files_path'
            args = (project_pk, directory,)  # type: ignore
        else:
            reverse_name = 'project_files'
            args = (project_pk,)  # type: ignore

        return redirect(reverse(reverse_name, args=args))


class FileSourceUpdateView(LoginRequiredMixin, ProjectPermissionsMixin, UpdateView):
    model = Source
    form_class = SourceUpdateForm
    template_name = 'projects/source_update.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})

    def get_object(self, *args, **kwargs):
        return self.get_source(self.request.user, self.kwargs['project_pk'], self.kwargs['pk'])


class FileSourceDeleteView(LoginRequiredMixin, ProjectPermissionsMixin, DeleteView):
    model = Source
    template_name = 'confirm_delete.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})
