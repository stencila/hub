import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    View,
    DetailView,
    ListView,
    RedirectView
)
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)

from .models import (
    Project,
    FilesProject, FilesProjectFile
)
from .forms import (
    ProjectCreateForm,
    FilesProjectUpdateForm
)


class ProjectListView(ListView):
    model = Project
    paginate_by = 100


class ProjectCreateView(LoginRequiredMixin, FormView):
    form_class = ProjectCreateForm
    template_name = 'projects/project_create.html'

    def get_success_url(self):
        return reverse('project_update', args=[self.project.id])

    def form_valid(self, form):
        self.project = Project.create(
            type=form.cleaned_data['type'],
            creator=self.request.user
        )
        return super().form_valid(form)


class ProjectReadView(LoginRequiredMixin, DetailView):
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


class FilesProjectReadView(LoginRequiredMixin, DetailView):
    model = FilesProject
    template_name = 'projects/fileproject_read.html'

    def get(self, request, pk):
        project = get_object_or_404(FilesProject, pk=pk)
        if request.META.get('HTTP_ACCEPT') == 'application/json':
            return JsonResponse(project.serialize())
        else:
            return render(request, self.template_name, project)


class FilesProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = FilesProject
    form_class = FilesProjectUpdateForm
    template_name = 'projects/filesproject_update.html'
    success_url = reverse_lazy('project_list')


class FilesProjectUploadView(LoginRequiredMixin, View):

    def post(self, request, pk):
        project = get_object_or_404(FilesProject, pk=pk)
        files = request.FILES.getlist('file')
        for file in files:
            instance = FilesProjectFile.objects.create(
                project=project,
                name=file,
                file=file,
                modified=datetime.datetime.now(tz=timezone.utc)
            )
            instance.save()
        return JsonResponse(project.serialize())


class FilesProjectRemoveView(LoginRequiredMixin, View):

    def delete(self, request, pk, file):
        project = get_object_or_404(FilesProject, pk=pk)
        file = get_object_or_404(FilesProjectFile, project=project, pk=file)
        file.delete()
        return JsonResponse(project.serialize())
