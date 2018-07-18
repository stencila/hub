from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
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
    FilesProject
)
from .forms import (
    ProjectCreateForm,
    FilesProjectUpdateForm, FilesProjectFileFormSet
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


class FilesProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = FilesProject
    form_class = FilesProjectUpdateForm
    template_name = 'projects/filesproject_update.html'
    success_url = reverse_lazy('project_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['file_formset'] = FilesProjectFileFormSet(
                self.request.POST,
                self.request.FILES,
                instance=self.object
            )
            context['file_formset'].full_clean()
        else:
            context['file_formset'] = FilesProjectFileFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['file_formset']
        if formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))
