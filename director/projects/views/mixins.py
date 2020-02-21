import os
import shutil
import tempfile
import typing
import warnings
from os import unlink

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractUser, User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, Http404

from accounts.models import Account
from lib.conversion_types import ConversionFormatId, mimetype_from_path, DOCX_MIMETYPES, UnknownMimeTypeError
from lib.converter_facade import ConverterFacade, ConverterIo, ConverterIoType, ConverterContext
from lib.resource_allowance import account_resource_limit, QuotaName
from lib.social_auth_token import user_github_token
from projects.permission_facade import ProjectFetchResult, fetch_project_for_user
from projects.permission_models import ProjectPermissionType, ProjectRole, get_highest_permission
from projects.project_models import Project, PublishedItem
from projects.project_puller import ProjectSourcePuller
from projects.source_content_facade import SourceContentFacade, make_source_content_facade
from projects.source_models import LinkedSourceAuthentication, GoogleDocsSource, DiskSource, Source
from projects.source_operations import generate_project_archive_directory
from lib.path_operations import utf8_path_join, utf8_dirname, utf8_realpath
from projects.views.shared import DEFAULT_ENVIRON, get_project_publish_directory, get_source


class ProjectPermissionsMixin(object):
    project_fetch_result: typing.Optional[ProjectFetchResult] = None
    project_permission_required: typing.Optional[ProjectPermissionType] = None

    def get(self, request: HttpRequest, account_name: str, project_name: str, *args, **kwargs) -> HttpResponse:
        warnings.warn("ProjectPermissionsMixin GET", DeprecationWarning)
        self.perform_project_fetch(request.user, account_name, project_name)
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).get(request, account_name, project_name, *args,  # type: ignore
                                                        **kwargs)

    def post(self, request: HttpRequest, account_name: str, project_name: str, *args, **kwargs):
        warnings.warn("ProjectPermissionsMixin GET", DeprecationWarning)
        self.perform_project_fetch(request.user, account_name, project_name)
        self.test_required_project_permission()
        return super(ProjectPermissionsMixin, self).post(request, account_name, project_name, *args,  # type: ignore
                                                         **kwargs)

    def delete(self, request: HttpRequest, account_name: str, project_name: str, *args, **kwargs):
        warnings.warn("ProjectPermissionsMixin DELETE", DeprecationWarning)
        self.perform_project_fetch(request.user, account_name, project_name)
        self.test_required_project_permission()

        return super(ProjectPermissionsMixin, self).delete(request, account_name, project_name, *args,  # type: ignore
                                                           **kwargs)

    def perform_project_fetch(self, user: AbstractUser, account_name: typing.Optional[str] = None,
                              project_name: typing.Optional[str] = None, pk: typing.Optional[int] = None) -> None:
        if self.project_fetch_result is None:
            self.project_fetch_result = fetch_project_for_user(user, pk, account_name, project_name)

    def get_render_context(self, context: dict) -> dict:
        context['environ'] = DEFAULT_ENVIRON
        context['project'] = self.project
        context['project_roles'] = self.project_roles
        context['project_permissions'] = self.project_permissions
        context['account'] = self.account
        return context

    def get_context_data(self, **kwargs) -> dict:
        context_data = super().get_context_data(**kwargs)  # type: ignore
        # this should only be used as a mixin to a view that will have the get_context_data function

        return self.get_render_context(context_data)

    def _test_project_fetch_result_set(self) -> None:
        if self.project_fetch_result is None:
            raise ValueError("project_fetch_result not set")

    # mypy is told to ignore the return from these properties as it doesn't understand that
    # _test_project_fetch_result_set does a None check

    @property
    def project(self) -> Project:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.project  # type: ignore

    @property
    def project_permissions(self) -> typing.Set[ProjectPermissionType]:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.agent_permissions  # type: ignore

    @property
    def project_roles(self) -> typing.Set[ProjectRole]:
        self._test_project_fetch_result_set()
        return self.project_fetch_result.agent_roles  # type: ignore

    @property
    def account(self) -> Account:
        self._test_project_fetch_result_set()
        return self.project.account  # type: ignore

    def has_permission(self, permission: ProjectPermissionType) -> bool:
        return self.has_any_permissions((permission,))

    def has_any_permissions(self, permissions: typing.Iterable[ProjectPermissionType]) -> bool:
        for permission in permissions:
            if permission in self.project_permissions:
                return True

        return False

    def test_required_project_permission(self) -> None:
        if self.project_permission_required is not None and not self.has_permission(self.project_permission_required):
            raise PermissionDenied

    def get_project(self, user: AbstractUser, account_name: typing.Optional[str] = None,
                    project_name: typing.Optional[str] = None, pk: typing.Optional[int] = None) -> Project:
        self.perform_project_fetch(user, account_name, project_name, pk)
        self.test_required_project_permission()
        return self.project

    def get_object(self, *args, **kwargs):
        self.perform_project_fetch(self.request.user, self.kwargs['account_name'], self.kwargs['project_name'])
        return self.project_fetch_result.project

    @property
    def highest_permission(self) -> typing.Optional[ProjectPermissionType]:
        return get_highest_permission(self.project_permissions)

    def get_project_puller(self, request: HttpRequest, account_name: str, project_name: str) -> ProjectSourcePuller:
        self.perform_project_fetch(request.user, account_name, project_name)

        self.test_required_project_permission()

        if not settings.STENCILA_PROJECT_STORAGE_DIRECTORY:
            raise RuntimeError('STENCILA_PROJECT_STORAGE_DIRECTORY setting must be set to pull Project files.')

        authentication = LinkedSourceAuthentication(user_github_token(request.user))

        storage_limit = typing.cast(int, account_resource_limit(self.project.account, QuotaName.STORAGE_LIMIT))

        return ProjectSourcePuller(self.project, settings.STENCILA_PROJECT_STORAGE_DIRECTORY, authentication, request,
                                   storage_limit)


class ArchivesDirMixin(object):
    @staticmethod
    def get_archives_directory(project: Project) -> str:
        return generate_project_archive_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

    @staticmethod
    def get_archive_path(archives_directory, name) -> str:
        return utf8_realpath(utf8_path_join(archives_directory, name))


class ContentFacadeMixin(object):
    def get_content_facade(self, request: HttpRequest, account_name: str, project_name: str,
                           path: str) -> SourceContentFacade:
        # type ignores because mypy doesn't trust us to use this only one a class which has these methods
        project = self.get_project(request.user, account_name, project_name)  # type: ignore
        source = get_source(request.user, project, path)
        return make_source_content_facade(request.user, path, source, project)  # type: ignore


class ConverterMixin:
    _converter: typing.Optional[ConverterFacade] = None

    @property
    def converter(self) -> ConverterFacade:
        if self._converter is None:
            self._converter = ConverterFacade(settings.STENCILA_BINARY)

        return self._converter

    def do_conversion(self, source_type: typing.Optional[ConversionFormatId],
                      source_path: str,
                      target_type: ConversionFormatId,
                      target_path: typing.Optional[str] = None, standalone: bool = False) -> str:
        """
        Perform a conversion (with Encoda).

        If `target_path` is not set then a `NamedTemporaryFile` is created and its path returned. The temporary file
        is not cleaned up.
        """
        if not target_path:
            with tempfile.NamedTemporaryFile(delete=False) as temp_output:
                target_path = temp_output.name

        converter_input = ConverterIo(ConverterIoType.PATH, source_path, source_type)
        converter_output = ConverterIo(ConverterIoType.PATH, target_path, target_type)

        context = ConverterContext(standalone=standalone)

        convert_result = self.converter.convert(converter_input, converter_output, context)

        if convert_result.returncode != 0:
            raise RuntimeError('Convert process failed. Stderr is: {}'.format(
                convert_result.stderr.decode('ascii')))

        return target_path

    def convert_to_google_docs(self, request: HttpRequest, project: Project, scf: SourceContentFacade, target_name: str,
                               target_path: str) -> None:
        """
        Convert a document to Google Docs.

        If the document is already in DOCX or HTML format it will just be uploaded, otherwise it is first converted to
        DOCX. The document is uploaded in DOCX/HTML and Google takes care of converting to Google Docs format.
        """
        if scf.source_type not in (ConversionFormatId.html, ConversionFormatId.docx):
            output_content, output_mime_type = self.convert_source_for_google_docs(scf)
        else:
            output_mime_type = mimetype_from_path(scf.file_path) or 'application/octet-stream'
            output_content = scf.get_binary_content()
        gdf = scf.google_docs_facade

        if gdf is None:
            raise TypeError('Google Docs Facade was not set up. Check that app tokens are good.')

        new_doc_id = gdf.create_document(target_name, output_content, output_mime_type)
        existing_source = GoogleDocsSource.objects.filter(project=project, path=target_path).first()
        new_source = gdf.create_source_from_document(project, utf8_dirname(target_path), new_doc_id)
        if existing_source is not None:
            gdf.trash_document(existing_source.doc_id)
            messages.info(request, 'Existing Google Docs file "{}" was moved to the Trash.'.format(target_name))
            existing_source.doc_id = new_source.doc_id
            existing_source.save()
        else:
            new_source.save()

    def convert_source_for_google_docs(self, scf: SourceContentFacade) -> typing.Tuple[bytes, str]:
        # GoogleDocs can only convert from HTML or DOCX so convert to DOCX on our end first
        temp_output_path = None
        input_path = None
        # if the source is not from Disk then the content should be saved to a temp path beforehand
        use_temp_input_path = not isinstance(scf.source, DiskSource)
        try:
            input_path = scf.sync_content(use_temp_input_path)

            temp_output_path = self.do_conversion(scf.source_type, input_path, ConversionFormatId.docx)

            with open(temp_output_path, 'rb') as temp_output:  # reopen after data has been written
                output_content = temp_output.read()  # this is in DOCX after conversion
        finally:
            if use_temp_input_path and input_path and os.path.exists(input_path):
                unlink(input_path)

            if temp_output_path and os.path.exists(temp_output_path):
                unlink(temp_output_path)
        return output_content, DOCX_MIMETYPES[0]

    def source_convert(self, request: HttpRequest, project: Project, scf: SourceContentFacade, target_path: str,
                       target_name: str, target_type: ConversionFormatId, standalone: bool = False) -> None:
        if target_type == ConversionFormatId.gdoc:
            self.convert_to_google_docs(request, project, scf, target_name, target_path)
        else:
            try:
                absolute_input_path = scf.sync_content()
            except FileNotFoundError:
                raise Http404

            absolute_output_path = scf.disk_file_facade.full_file_path(target_path)

            self.do_conversion(scf.source_type, absolute_input_path, target_type, absolute_output_path, standalone)

    def convert_and_publish(self, user: User, project: Project, pi: PublishedItem, pi_created: bool,
                            source: typing.Union[Source, DiskSource], source_path: str,
                            scf: typing.Optional[SourceContentFacade] = None) -> None:
        try:
            if not scf:
                scf = make_source_content_facade(user, source_path, source, project)

            published_path = utf8_path_join(get_project_publish_directory(project), '{}.html'.format(pi.pk))

            if os.path.exists(published_path):
                os.unlink(published_path)

            if os.path.exists(published_path + '.media'):
                shutil.rmtree(published_path + '.media')

            try:
                absolute_input_path = scf.sync_content()
            except FileNotFoundError:
                raise Http404

            self.do_conversion(scf.source_type, absolute_input_path, ConversionFormatId.html, published_path, False)
        except (RuntimeError, Http404, UnknownMimeTypeError):
            # Without this we can end up with items without paths
            if pi_created:
                pi.delete()
            raise

        pi.path = published_path
        if isinstance(source, Source):
            pi.source = source
        else:
            pi.source = None
        pi.save()
