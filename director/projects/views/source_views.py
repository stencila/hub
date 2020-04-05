import json
import os
import typing

import oauth2client.client
from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.html import escape
from django.views import View
from django.views.generic import CreateView, DetailView

from accounts.db_facade import user_is_account_admin
from lib import data_size
from lib.conversion_types import ConversionFormatId
from lib.google_docs_facade import GoogleDocsFacade
from lib.path_operations import utf8_path_join, utf8_basename, utf8_dirname
from lib.resource_allowance import (
    account_resource_limit,
    QuotaName,
    StorageLimitExceededException,
    get_subscription_upgrade_text,
)
from lib.social_auth_token import user_social_token, user_github_token
from projects.disk_file_facade import DiskFileFacade
from projects.models import DropboxSource, GithubSource
from projects.permission_models import ProjectPermissionType
from projects.source_content_facade import (
    SourceEditContext,
    SourceContentFacade,
    make_source_content_facade,
)
from projects.source_forms import GithubSourceForm, GoogleDocsSourceForm
from projects.source_models import DiskSource, GoogleDocsSource, Source
from projects.source_operations import strip_directory
from projects.views.mixins import (
    ProjectPermissionsMixin,
    ContentFacadeMixin,
    ConverterMixin,
)


def project_files_redirect(
    account_name: str, project_name: str, dir_path: typing.Optional[str]
) -> HttpResponse:
    """Redirect to the correct file browse URL, taking into account if we are in inside a directory."""
    if dir_path:
        return redirect("project_files_path", account_name, project_name, dir_path)

    return redirect("project_files", account_name, project_name)


class SourceCreateView(CreateView, ProjectPermissionsMixin):
    """A base class for view for creating new project sources."""

    project_permission_required = ProjectPermissionType.EDIT

    def get_initial(self):
        path = self.request.GET.get("path") or "."
        return {
            "project": self.get_project(
                self.request.user,
                self.kwargs["account_name"],
                self.kwargs["project_name"],
            ),
            "path": path,
        }

    def get_redirect(self, account_name: str, project_name: str) -> HttpResponse:
        args = [account_name, project_name]

        if self.request.GET.get("directory"):
            args.append(self.request.GET.get("directory"))
            redirect_name = "project_files_path"
        else:
            redirect_name = "project_files"

        return redirect(redirect_name, *args)

    def form_valid(self, form):
        """Override to set the project for the `Source` and redirect back to that project."""
        file_source = form.save(commit=False)
        file_source.project = self.get_project(
            self.request.user, self.kwargs["account_name"], self.kwargs["project_name"]
        )
        file_source.save()

        return self.get_redirect(
            self.kwargs["account_name"], self.kwargs["project_name"]
        )


class DropboxSourceCreateView(SourceCreateView):
    """A view for creating a Dropbox project source."""

    model = DropboxSource
    template_name = "projects/dropboxsource_create.html"


class GithubSourceCreateView(SourceCreateView):
    """A view for creating a Github project source."""

    model = GithubSource
    form_class = GithubSourceForm
    template_name = "projects/githubsource_create.html"

    def get(self, request, *args, **kwargs) -> HttpResponse:
        github_token = user_github_token(request.user)
        if not github_token:
            social_url = reverse("socialaccount_connections")
            messages.error(
                request,
                "Can not link a Github repository as you do not have a Github account connected to "
                "your Stencila Hub account.<br/>Please connect your Github account on the "
                '<a href="{}">Account Connections page</a>.'.format(social_url),
                extra_tags="safe",
            )
            return redirect(
                "project_files", kwargs["account_name"], kwargs["project_name"]
            )

        return super().get(request, *args, **kwargs)


class GoogleDocsSourceCreateView(SourceCreateView):
    """A view for creating a Github project source."""

    model = GoogleDocsSource
    form_class = GoogleDocsSourceForm
    template_name = "projects/googledocssource_create.html"

    def form_valid(self, form: GoogleDocsSourceForm) -> HttpResponse:
        google_app = SocialApp.objects.filter(provider="google").first()

        gdf = GoogleDocsFacade(
            google_app.client_id,
            google_app.secret,
            user_social_token(self.request.user, "google"),
        )

        directory = self.request.GET.get("directory", "")
        document = gdf.get_document(form.cleaned_data["doc_id"])

        source = form.save(commit=False)
        source.project = self.get_project(
            self.request.user, self.kwargs["account_name"], self.kwargs["project_name"]
        )
        source.path = utf8_path_join(directory, document["title"])
        source.save()

        return self.get_redirect(
            self.kwargs["account_name"], self.kwargs["project_name"]
        )


class FileSourceUploadView(ProjectPermissionsMixin, View):
    """A view for uploading one or more files into the project."""

    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        directory = request.GET.get("directory", "")
        files = request.FILES.getlist("file")

        dff = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

        storage_limit = typing.cast(
            int, account_resource_limit(project.account, QuotaName.STORAGE_LIMIT)
        )
        actual_storage_used = storage_used = (
            0 if storage_limit == -1 else dff.get_project_directory_size()
        )

        respond_with_json = request.META.get("HTTP_ACCEPT") == "application/json"

        error = None

        try:
            if directory:
                dff.create_directory(directory)

            if storage_limit != -1:
                for file in files:
                    storage_used += file.size
                    if storage_used > storage_limit:
                        plural = "s" if len(files) != 1 else ""
                        raise StorageLimitExceededException(
                            'The file{} could not be saved as it would exceed the storage limit for the account "{}". '
                            "The current limit is {}, you have used {}. Please visit the Account Subscriptions page "
                            "to add or upgrade a subscription".format(
                                plural,
                                project.account,
                                data_size.to_human(storage_limit),
                                data_size.to_human(actual_storage_used),
                            )
                        )

            for file in files:
                dff.write_file_content(
                    utf8_path_join(directory, file.name), file.read()
                )
        except Exception as e:
            if respond_with_json:
                error = str(e)
            else:
                messages.error(request, "Error during upload: {}".format(str(e)))

        response_status = (
            500 if error else (200 if respond_with_json else 204)
        )  # 240 == no content

        if respond_with_json:
            return JsonResponse(
                {"success": error is None, "error": error}, status=response_status
            )
        else:
            return HttpResponse(status=response_status)


class SourceDownloadView(ProjectPermissionsMixin, ContentFacadeMixin, View):
    project_permission_required = ProjectPermissionType.VIEW

    def get(  # type: ignore
        self, request: HttpRequest, account_name: str, project_name: str, path: str,
    ) -> HttpResponse:
        content_facade = self.get_content_facade(
            request, account_name, project_name, path
        )
        return self.process_get(account_name, project_name, path, content_facade)

    def process_get(
        self,
        account_name: str,
        project_name: str,
        path: str,
        content_facade: SourceContentFacade,
    ) -> HttpResponse:
        # TODO: see if this can return a handle for streaming response
        file_content = content_facade.get_binary_content()

        if content_facade.error_exists:
            content_facade.add_messages_to_request(self.request)
            return project_files_redirect(
                account_name, project_name, utf8_dirname(path)
            )

        response = HttpResponse(file_content, content_type="application/octet-stream")

        response["Content-Disposition"] = "attachment; filename={}".format(
            content_facade.get_name()
        )
        return response


class SourceOpenView(
    LoginRequiredMixin, ProjectPermissionsMixin, ContentFacadeMixin, DetailView
):
    project_permission_required = ProjectPermissionType.VIEW

    def get_context_data(self, *args, **kwargs):
        data = super().get_context_data(*args, **kwargs)
        data["file_content"] = self.object.pull()
        return data

    def render(
        self,
        request: HttpRequest,
        editing_context: SourceEditContext,
        extra_context: typing.Optional[dict] = None,
    ) -> HttpResponse:
        render_context = {
            "project": self.project,
            "has_edit_permission": self.has_permission(ProjectPermissionType.EDIT),
            "file_name": utf8_basename(editing_context.path),
            "file_directory": utf8_dirname(editing_context.path),
            "file_path": editing_context.path,
            "file_extension": editing_context.extension,
            "file_content": editing_context.content,
            "file_editable": editing_context.editable,
            "source": editing_context.source,
            "supports_commit_message": editing_context.supports_commit_message,
        }
        render_context.update(extra_context or {})
        return render(
            request,
            "projects/source_open.html",
            self.get_render_context(render_context),
        )

    @staticmethod
    def get_default_commit_message(request: HttpRequest):
        return "Commit from Stencila Hub User {}".format(request.user)

    def process_get(
        self,
        request: HttpRequest,
        account_name: str,
        project_name: str,
        path: str,
        content_facade: SourceContentFacade,
    ) -> HttpResponse:
        edit_context = content_facade.get_edit_context()

        if edit_context is None:
            content_facade.add_messages_to_request(request)
            return project_files_redirect(
                account_name, project_name, utf8_dirname(path)
            )

        return self.render(
            request,
            edit_context,
            {"default_commit_message": self.get_default_commit_message(request)},
        )

    def get(  # type: ignore
        self, request: HttpRequest, account_name: str, project_name: str, path: str,
    ) -> HttpResponse:
        content_facade = self.get_content_facade(
            request, account_name, project_name, path
        )
        return self.process_get(
            request, account_name, project_name, path, content_facade
        )

    @staticmethod
    def get_github_repository_path(source, file_path):
        repo_path = utf8_path_join(
            source.subpath, strip_directory(file_path, source.path)
        )
        return repo_path

    def post(  # type: ignore
        self, request: HttpRequest, account_name: str, project_name: str, path: str,
    ) -> HttpResponse:
        self.pre_post_check(request, account_name, project_name)

        content_facade = self.get_content_facade(
            request, account_name, project_name, path
        )
        return self.perform_post(
            request, account_name, project_name, path, content_facade
        )

    def pre_post_check(
        self, request: HttpRequest, account_name: str, project_name: str
    ) -> None:
        self.perform_project_fetch(request.user, account_name, project_name)
        if not self.has_permission(ProjectPermissionType.EDIT):
            raise PermissionDenied

    def perform_post(
        self,
        request: HttpRequest,
        account_name: str,
        project_name: str,
        path: str,
        content_facade: SourceContentFacade,
    ) -> HttpResponse:
        commit_message = request.POST.get(
            "commit_message"
        ) or self.get_default_commit_message(request)

        storage_limit = account_resource_limit(
            self.project.account, QuotaName.STORAGE_LIMIT
        )

        update_success = None
        content_override = None

        if storage_limit != -1 and isinstance(content_facade.source, DiskSource):
            old_size = content_facade.get_size()
            new_size = len(request.POST["file_content"])
            if new_size > old_size:
                storage_used = (
                    content_facade.disk_file_facade.get_project_directory_size()
                )
                is_account_admin = user_is_account_admin(
                    self.request.user, self.project.account
                )
                subscription_upgrade_text = get_subscription_upgrade_text(
                    is_account_admin, self.project.account
                )

                if (new_size - old_size) + storage_used > storage_limit:
                    message = (
                        "The file content could not be saved as it would exceed the storage limit for the "
                        "account <em>{}</em>. {}".format(
                            escape(self.project.account), subscription_upgrade_text
                        )
                    )
                    messages.error(request, message, extra_tags="safe")
                    update_success = False
                    content_override = request.POST["file_content"]

        if update_success is None:
            update_success = content_facade.update_content(
                request.POST["file_content"], commit_message
            )

        error_exists = content_facade.error_exists

        content_facade.add_messages_to_request(request)

        dirname = utf8_dirname(path)

        if error_exists or not update_success:
            edit_context = content_facade.get_edit_context(content_override)

            if edit_context is None or content_facade.error_exists:
                return project_files_redirect(account_name, project_name, dirname)

            return self.render(
                request,
                edit_context,
                {
                    "commit_message": commit_message,
                    "default_commit_message": self.get_default_commit_message(request),
                },
            )

        messages.success(
            request, "Content of {} updated.".format(os.path.basename(path))
        )

        return project_files_redirect(account_name, project_name, dirname)


class SourceConvertView(
    LoginRequiredMixin, ProjectPermissionsMixin, ConverterMixin, View
):
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, account_name: str, project_name: str) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, account_name, project_name)

        body = json.loads(request.body)

        source_id = body["source_id"]
        source_path = body["source_path"]
        target_id = body["target_type"]
        target_name = body["target_name"]

        if "/" in target_name:
            raise ValueError("Target name can not contain /")

        if source_id:
            source = get_object_or_404(Source, project=project, pk=source_id)
        else:
            source = DiskSource()

        scf = make_source_content_facade(request.user, source_path, source, project)

        target_path = utf8_path_join(utf8_dirname(source_path), target_name)
        target_type = ConversionFormatId.from_id(target_id)

        try:
            self.source_convert(
                request, project, scf, target_path, target_name, target_type
            )
        except oauth2client.client.Error:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Could not authenticate with your Google account."
                    "Please try logging into Stencila Hub with "
                    "your Google account to refresh the token.",
                }
            )
        except RuntimeError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Conversion of your document failed. Please check the Project Activity page for more "
                    "information.",
                }
            )

        for message in scf.message_iterator():
            messages.add_message(request, message.level, message.message)

        messages.success(
            request, "{} was converted.".format(utf8_basename(source_path))
        )

        return JsonResponse({"success": True})
