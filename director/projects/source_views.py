from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView


from .models import Project, Source, FileSource, DropboxSource, GithubSource
from .source_forms import FileSourceForm, GithubSourceForm


class SourceCreateView(LoginRequiredMixin, CreateView):
    """A base class for view for creating new project sources"""

    def get_context_data(self, *args, **kwargs):
        """Override to add project to the template context"""
        data = super().get_context_data(*args, **kwargs)
        data['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return data

    def form_valid(self, form):
        """Override to set the project for the `Source` and redirect back to that project"""
        pk = self.kwargs['pk']
        filesource = form.save(commit=False)
        filesource.project = get_object_or_404(Project, pk=pk)
        filesource.save()
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


class FileSourceUploadView(LoginRequiredMixin, DetailView):
    """A view for uploading one or more files into the project"""

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


class SourceOpenView(LoginRequiredMixin, DetailView):
    model = Source
    template_name = 'projects/source_open.html'

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data['file_content'] = self.object.pull()
        return data


class SourceUpdateView(LoginRequiredMixin, UpdateView):
    model = Source
    fields = ['path']
    template_name = 'projects/source_update.html'

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})


class SourceDeleteView(LoginRequiredMixin, DeleteView):
    model = Source
    template_name = 'confirm_delete.html'

    def get_success_url(self) -> str:
        return reverse("project_files", kwargs={'pk': self.kwargs['project_pk']})
