import mimetypes
from os.path import dirname

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from projects.permission_models import ProjectPermissionType
from projects.project_views import ProjectPermissionsMixin
from .models import Project, Source, FileSource, DropboxSource, GithubSource
from .source_forms import FileSourceForm, GithubSourceForm, SourceUpdateForm


class SourceCreateView(LoginRequiredMixin, ProjectPermissionsMixin, CreateView):
    """A base class for view for creating new project sources."""
    project_permission_required = ProjectPermissionType.EDIT

    def form_valid(self, form):
        """Override to set the project for the `Source` and redirect back to that project"""
        pk = self.kwargs['pk']
        file_source = form.save(commit=False)
        file_source.project = get_object_or_404(Project, pk=pk)
        file_source.save()
        return HttpResponseRedirect(
            reverse("project_files", kwargs={'pk': pk})
        )


class FileSourceCreateView(SourceCreateView):
    """A view for creating a new, emtpy local file in the project"""

    model = FileSource
    form_class = FileSourceForm
    template_name = 'projects/filesource_create.html'


class DropboxSourceCreateView(SourceCreateView):
    """A view for creating a Dropbox project source"""

    model = DropboxSource
    template_name = 'projects/dropboxsource_create.html'


class GithubSourceCreateView(SourceCreateView):
    """A view for creating a Github project source"""

    model = GithubSource
    form_class = GithubSourceForm
    template_name = 'projects/githubsource_create.html'


class FileSourceUploadView(LoginRequiredMixin, ProjectPermissionsMixin, DetailView):
    """A view for uploading one or more files into the project"""

    model = Project
    template_name = 'projects/filesource_upload.html'
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        files = request.FILES.getlist('file')
        for file in files:
            source = FileSource.objects.create(
                project=self.project,
                path=file,
                file=file
            )
            source.save()

        return HttpResponse()


class SourceOpenView(LoginRequiredMixin, ProjectPermissionsMixin, DetailView):
    model = Source
    template_name = 'projects/source_open.html'
    project_permission_required = ProjectPermissionType.VIEW

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['file_content'] = self.object.pull()
        return data

    def get(self, request: HttpRequest, project_pk: int, pk: int) -> HttpResponse:
        source = self.get_source(request.user, project_pk, pk)
        mimetype, encoding = mimetypes.guess_type(source.path, False)

        if mimetype:
            file_language = mimetype.split('/')[1]
        else:
            file_language = ''

        return render(request, 'projects/source_open.html', self.get_render_context({
            'file_path': source.path,
            'file_language': file_language,
            'file_content': source.pull()
        }))

    def post(self, request: HttpRequest, project_pk: int, pk: int) -> HttpResponse:
        source = self.get_source(request.user, project_pk, pk)
        source.push(request.POST['file_content'])
        messages.success(request, 'Content updated.')

        directory = dirname(source.path)

        if directory:
            reverse_name = 'project_files_path'
            args = (project_pk, directory,)
        else:
            reverse_name = 'project_files'
            args = (project_pk,)

        return redirect(reverse(reverse_name, args=args))


class SourceUpdateView(LoginRequiredMixin, ProjectPermissionsMixin, UpdateView):
    model = Source
    form_class = SourceUpdateForm
    template_name = 'projects/source_update.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})

    def get_object(self, *args, **kwargs):
        return self.get_source(self.request.user, self.kwargs['project_pk'], self.kwargs['pk'])


class SourceDeleteView(LoginRequiredMixin, ProjectPermissionsMixin, DeleteView):
    model = Source
    template_name = 'confirm_delete.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})
