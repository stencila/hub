from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    View,
    DetailView,
    ListView
)
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)

from .models import (
    Project
)
from .forms import (
    ProjectCreateForm,
    FilesProjectUpdateForm
)


class ProjectListView(LoginRequiredMixin, ListView):
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


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/project_update.html'
    fields = ['address']


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_delete.html'
    success_url = reverse_lazy('project_list')


class ProjectArchiveView(LoginRequiredMixin, View):

    def get(self, request, pk):
        project = get_object_or_404(Project, id=pk)

        archive = project.pull()
        body = archive.getvalue()

        response = HttpResponse(body, content_type='application/x-zip-compressed')
        response['Content-Disposition'] = 'attachment; filename={}.zip'.format('project.name')
        return response


class FilesProjectUpdateView(LoginRequiredMixin, FormView):
    form_class = FilesProjectUpdateForm
    template_name = 'projects/files_project_update.html'

    def get_success_url(self):
        return reverse('files_project_update', args=[self.object.id])

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            project = Project.objects.create()
            #files = request.FILES.getlist('files_field')
            #for file in files:
            #    project.files.add(file)
            project.save()
            # For consistency with CreateView...
            self.object = project
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
