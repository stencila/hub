import json
import os
import typing
from os.path import splitext

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView

from lib.converter_facade import ConverterFacade
from lib.google_docs_facade import GoogleDocsFacade
from lib.social_auth_token import user_github_token, user_social_token
from projects.disk_file_facade import DiskFileFacade, ItemType
from projects.permission_models import ProjectPermissionType
from projects.project_views import ProjectPermissionsMixin
from projects.source_edit import SourceEditContext, SourceContentFacade
from projects.source_models import LinkedSourceAuthentication, DiskSource, GoogleDocsSource
from projects.source_operations import strip_directory, get_filesystem_project_path, utf8_path_join, utf8_basename, \
    utf8_dirname
from .models import Project, DropboxSource, GithubSource
from .source_forms import GithubSourceForm, DiskFileSourceForm, GoogleDocsSourceForm


class SourceCreateView(LoginRequiredMixin, ProjectPermissionsMixin, CreateView):
    """A base class for view for creating new project sources."""

    project_permission_required = ProjectPermissionType.EDIT

    def get_initial(self):
        return {
            'project': get_object_or_404(Project, pk=self.kwargs['pk'])
        }

    def get_redirect(self, pk: int) -> HttpResponse:
        if self.request.GET.get('directory'):
            return redirect("project_files_path", pk, self.request.GET['directory'])
        else:
            return redirect("project_files", pk)

    def form_valid(self, form):
        """Override to set the project for the `Source` and redirect back to that project."""
        pk = self.kwargs['pk']
        file_source = form.save(commit=False)
        file_source.project = get_object_or_404(Project, pk=pk)
        file_source.save()

        return self.get_redirect(pk)


class FileSourceCreateView(LoginRequiredMixin, ProjectPermissionsMixin, View):
    """A view for creating a new, emtpy local file in the project."""

    form_class = DiskFileSourceForm
    template_name = 'projects/filesource_create.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        self.get_project(request.user, pk)

        return self.get_response(request, self.form_class())

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        project = self.get_project(request.user, pk)

        form = self.form_class(request.POST)

        if form.is_valid():
            dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

            dff.create_file(utf8_path_join(self.current_directory, form.cleaned_data['path']))

            if self.current_directory:
                return redirect("project_files_path", pk, self.current_directory)
            else:
                return redirect("project_files", pk, )

        return self.get_response(request, form)

    def get_response(self, request: HttpRequest, form: DiskFileSourceForm) -> HttpResponse:
        return render(request,
                      self.template_name,
                      self.get_render_context({
                          'current_directory': self.current_directory,
                          'form': form
                      })
                      )

    @property
    def current_directory(self) -> str:
        return self.request.GET.get('directory', '')


class DropboxSourceCreateView(SourceCreateView):
    """A view for creating a Dropbox project source."""

    model = DropboxSource
    template_name = 'projects/dropboxsource_create.html'


class GithubSourceCreateView(SourceCreateView):
    """A view for creating a Github project source."""

    model = GithubSource
    form_class = GithubSourceForm
    template_name = 'projects/githubsource_create.html'


class GoogleDocsSourceCreateView(SourceCreateView):
    """A view for creating a Github project source."""

    model = GoogleDocsSource
    form_class = GoogleDocsSourceForm
    template_name = 'projects/googledocssource_create.html'

    def form_valid(self, form: GoogleDocsSourceForm) -> HttpResponse:
        google_app = SocialApp.objects.filter(provider='google').first()

        gdf = GoogleDocsFacade(google_app.client_id, google_app.secret, user_social_token(self.request.user, 'google'))

        directory = self.request.GET.get('directory', '')
        document = gdf.get_document(form.cleaned_data['doc_id'])

        pk = self.kwargs['pk']
        source = form.save(commit=False)
        source.project = get_object_or_404(Project, pk=pk)
        source.path = utf8_path_join(directory, document['title'])
        source.save()

        return self.get_redirect(pk)


class FileSourceUploadView(LoginRequiredMixin, ProjectPermissionsMixin, DetailView):
    """A view for uploading one or more files into the project."""

    model = Project
    template_name = 'projects/filesource_upload.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get_context_data(self, **kwargs):
        self.get_project(self.request.user, self.kwargs['pk'])
        context_data = super().get_context_data(**kwargs)
        context_data['upload_directory'] = self.request.GET.get('directory', '')
        return context_data

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        project = self.get_project(request.user, pk)

        directory = request.GET.get('directory', '')
        files = request.FILES.getlist('file')

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        if directory:
            dff.create_directory(directory)

        for file in files:
            dff.write_file_content(utf8_path_join(directory, file.name), file.read())

        return HttpResponse()


class SourceOpenView(LoginRequiredMixin, ProjectPermissionsMixin, DetailView):
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

    def process_get(self, request: HttpRequest, content_facade: SourceContentFacade) -> HttpResponse:
        return self.render(request, content_facade.get_edit_context(), {
            'default_commit_message': self.get_default_commit_message(request)
        })

    def get(self, request: HttpRequest, project_pk: int, pk: int, path: str) -> HttpResponse:
        content_facade = self.get_content_facade(request, project_pk, pk, path)
        return self.process_get(request, content_facade)

    @staticmethod
    def get_github_repository_path(source, file_path):
        repo_path = utf8_path_join(source.subpath, strip_directory(file_path, source.path))
        return repo_path

    def post(self, request: HttpRequest, project_pk: int, pk: int, path: str) -> HttpResponse:
        self.pre_post_check(request, project_pk)

        content_facade = self.get_content_facade(request, project_pk, pk, path)
        return self.perform_post(request, project_pk, path, content_facade)

    def pre_post_check(self, request: HttpRequest, project_pk: int) -> None:
        self.perform_project_fetch(request.user, project_pk)
        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

    def perform_post(self, request: HttpRequest, project_pk: int, path: str, content_facade: SourceContentFacade):
        commit_message = request.POST.get('commit_message') or self.get_default_commit_message(request)
        if not content_facade.update_content(request.POST['file_content'], commit_message):
            return self.render(request, content_facade.get_edit_context(), {
                'commit_message': commit_message,
                'default_commit_message': self.get_default_commit_message(request)
            })
        messages.success(request, 'Content of {} updated.'.format(os.path.basename(path)))
        directory = os.path.dirname(path)
        if directory:
            reverse_name = 'project_files_path'
            args = (project_pk, directory,)  # type: ignore
        else:
            reverse_name = 'project_files'
            args = (project_pk,)  # type: ignore
        return redirect(reverse(reverse_name, args=args))

    def get_content_facade(self, request, project_pk, pk, path):
        source = self.get_source(request.user, project_pk, pk)
        authentication = LinkedSourceAuthentication(user_github_token(request.user))
        return SourceContentFacade(source, authentication, request, path)


class DiskFileSourceOpenView(SourceOpenView):
    project_permission_required = ProjectPermissionType.VIEW

    def get_content_facade(self, request: HttpRequest, project_pk: int, pk: int, path: str):
        fs_path = get_filesystem_project_path(settings.STENCILA_PROJECT_STORAGE_DIRECTORY,
                                              self.get_project(request.user, project_pk), path)
        return SourceContentFacade(DiskSource(), None, request, fs_path)

    def get(self, request: HttpRequest, project_pk: int, path: str) -> HttpResponse:  # type: ignore
        content_facade = self.get_content_facade(request, project_pk, -1, path)
        return self.process_get(request, content_facade)

    def post(self, request: HttpRequest, project_pk: int, path: str) -> HttpResponse:  # type: ignore
        self.pre_post_check(request, project_pk)

        content_facade = self.get_content_facade(request, project_pk, -1, path)

        return self.perform_post(request, project_pk, path, content_facade)


class DiskFileSourceUpdateView(LoginRequiredMixin, ProjectPermissionsMixin, View):
    form_class = DiskFileSourceForm
    template_name = 'projects/source_update.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get(self, request: HttpRequest, pk: int, path: str) -> HttpResponse:
        project = self.get_project(request.user, pk)

        form = self.form_class(initial={'path': path})

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        if not dff.item_exists(path):
            raise Http404

        return self.get_response(request, project, form, path)

    def get_response(self, request: HttpRequest, project: Project, form: DiskFileSourceForm, path: str) -> HttpResponse:
        return render(request, self.template_name, {
            'project': project,
            'current_path': path,
            'form': form
        })

    def post(self, request: HttpRequest, pk: int, path: str) -> HttpResponse:
        project = self.get_project(request.user, pk)

        form = self.form_class(request.POST, initial={'path': path})

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        if not dff.item_exists(path):
            raise Http404

        if form.is_valid():
            dff.move_file(path, form.cleaned_data['path'])
            messages.success(request, '"{}" was moved to "{}".'.format(path, form.cleaned_data['path']))

            directory = request.GET.get('from', '')

            if directory:
                return redirect('project_files_path', pk, directory)
            else:
                return redirect('project_files', pk)

        return self.get_response(request, project, form, path)


class DiskFileSourceDeleteView(LoginRequiredMixin, ProjectPermissionsMixin, View):
    template_name = 'confirm_delete.html'
    project_permission_required = ProjectPermissionType.EDIT

    def get(self, request: HttpRequest, pk: int, path: str) -> HttpResponse:
        project = self.get_project(request.user, pk)

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        if not dff.item_exists(path):
            messages.warning(request, '{} does not exist in this project.'.format(path))
            return self.get_completion_redirect(pk)

        return render(request, self.template_name, {
            'object': path
        })

    def post(self, request: HttpRequest, pk: int, path: str) -> HttpResponse:
        project = self.get_project(request.user, pk)

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        if not dff.item_exists(path):
            messages.warning(request, '{} does not exist in this project.'.format(path))
            return self.get_completion_redirect(pk)

        dff.remove_item(path)
        messages.success(request, '{} was deleted.'.format(path))

        return self.get_completion_redirect(pk)

    def get_completion_redirect(self, pk: int) -> HttpResponse:
        if self.current_directory:
            return redirect('project_files_path', pk, self.current_directory)

        return redirect('project_files', pk)

    @property
    def current_directory(self) -> str:
        return self.request.GET.get('from', '')


class SourceConvertView(LoginRequiredMixin, ProjectPermissionsMixin, View):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        project = self.get_project(request.user, pk)

        body = json.loads(request.body)

        source_id = body['source_id']
        source_path = body['source_path']
        target_type = body['target_type']
        source_type = None

        if target_type not in ('markdown', 'html', 'googledocs'):
            raise TypeError('Can\'t convert to {}.'.format(target_type))

        google_token = user_social_token(request.user, 'google')

        google_app = SocialApp.objects.filter(provider='google').first()
        gdf = GoogleDocsFacade(google_app.client_id, google_app.secret, google_token)
        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        if not source_id:
            # assume it's a file source and read from disk
            if dff.item_type(source_path) != ItemType.FILE:
                raise OSError('{} is not a file.'.format(source_path))

            content = dff.read_file_content(source_path)
        else:
            source = self.get_source(request.user, pk, source_id)

            if isinstance(source, GoogleDocsSource):
                doc = gdf.get_document(source.doc_id)
                content = json.dumps(doc).encode('utf8')
                source_type = 'googledocs'
            else:
                authentication = LinkedSourceAuthentication(user_github_token(request.user), google_token)
                scf = SourceContentFacade(source, authentication, request, source_path)
                content = scf.get_binary_content()

        source_path_without_ext, source_ext = splitext(source_path)

        source_name = utf8_basename(source_path)

        converter = ConverterFacade(settings.STENCILA_CONVERTER_BINARY)

        if source_type is None:
            source_type = {
                '.md': 'markdown',
                '.html': 'html',
                '.htm': 'html'
            }[source_ext.lower()]

        if source_type == 'markdown' and target_type == 'googledocs':
            content = converter.convert('markdown', 'html', content)

        if target_type == 'googledocs':
            new_doc_id = gdf.create_document_from_html(source_name, content.decode('utf8'))

            gdf.create_source_from_document(project, utf8_dirname(source_path), new_doc_id)
        elif target_type in ('markdown', 'html'):
            new_extension = 'md' if target_type == 'markdown' else 'html'
            new_path = source_path_without_ext + '.' + new_extension
            converted_content = converter.convert(source_type, target_type, content)
            dff.write_file_content(new_path, converted_content)
        else:
            raise NotImplementedError('Can\'t convert to anything except googledocs.')

        messages.success(request, '{} was converted.'.format(utf8_basename(source_path)))

        return JsonResponse({
            'success': True
        })
