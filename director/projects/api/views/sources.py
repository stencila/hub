import json
import os
import shutil
import typing

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import View
from googleapiclient.errors import HttpError
from oauth2client.client import HttpAccessTokenRefreshError
from rest_framework.request import Request
from rest_framework.views import APIView

from lib.conversion_types import UnknownMimeTypeError
from lib.converter_facade import fetch_url
from lib.google_docs_facade import GoogleDocsFacade
from lib.social_auth_token import user_social_token
from projects.disk_file_facade import DiskFileFacade, ItemType
from projects.permission_facade import fetch_project_for_user
from projects.permission_models import ProjectPermissionType
from projects.project_forms import PublishedItemForm
from projects.project_models import PublishedItem
from projects.source_models import GoogleDocsSource, UrlSource, Source, DiskSource
from lib.path_operations import utf8_path_join
from projects.views.mixins import ConverterMixin, ProjectPermissionsMixin


class LinkException(Exception):
    pass


class ItemPublishView(ProjectPermissionsMixin, ConverterMixin, APIView):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: Request, pk: int):  # type: ignore
        """Create or update the `PublishedItem` for this Project."""
        project = self.get_project(request.user, pk=pk)

        data = request.data

        form = PublishedItemForm(data, initial={"project": project})

        if form.is_valid():
            source_id = form.cleaned_data.get("source_id")
            url_path = form.cleaned_data.get("url_path")
            source_path = form.cleaned_data["source_path"]

            if source_id:
                source = get_object_or_404(Source, project=project, pk=source_id)
            else:
                source = DiskSource()

            pi, created = PublishedItem.objects.get_or_create(
                project=project,
                source_path=form.cleaned_data["source_path"],
                defaults={"url_path": url_path},
            )
            if url_path != pi.url_path:
                pi.url_path = url_path
                pi.save()

            try:
                self.convert_and_publish(
                    request.user, project, pi, created, source, source_path
                )
            except (RuntimeError, UnknownMimeTypeError) as e:
                resp_body: typing.Dict[str, typing.Any] = {"success": False}
                if isinstance(e, UnknownMimeTypeError):
                    resp_body["errors"] = [
                        "Unable to determine the type of the file at {}.".format(
                            source_path
                        )
                    ]
                if created:
                    pi.delete()
                return JsonResponse(resp_body)
            except Exception:
                if created:
                    pi.delete()
                raise

            if pi.url_path:
                published_url = reverse(
                    "project_published_content",
                    args=(project.account.name, project.name, pi.url_path),
                )
                published_to = ' to <a href="{}">{}</a>'.format(
                    published_url, pi.url_path
                )
            else:
                published_to = ""

            success_message = "The file <em>{}</em> was published successfully{}.".format(
                escape(source_path), published_to
            )
            messages.success(request, success_message, extra_tags="safe")

            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {"success": False, "errors": form.errors.get_json_data()}
            )


class PublishedItemDeleteView(ProjectPermissionsMixin, APIView):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        pi = get_object_or_404(PublishedItem, pk=pk)
        self.project_fetch_result = fetch_project_for_user(
            request.user, project=pi.project
        )
        pi_url_path = pi.url_path
        self.test_required_project_permission()
        if os.path.exists(pi.path):
            os.unlink(pi.path)

        media_dir = pi.path + ".media"
        if os.path.exists(media_dir):
            shutil.rmtree(media_dir)

        pi.delete()

        if request.is_ajax():
            return JsonResponse(
                {
                    "success": True,
                    "message": "Item at {} was successfully unpublished.".format(
                        pi_url_path
                    ),
                }
            )

        messages.success(
            request,
            "Item at <em>{}</em> was successfully unpublished.".format(
                escape(pi_url_path)
            ),
            extra_tags="safe",
        )

        return HttpResponse(status=204)


class SourceLinkView(ProjectPermissionsMixin, APIView):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: Request, pk: int) -> HttpResponse:  # type: ignore
        self.get_project(request.user, pk=pk)

        data = request.data

        source_type = data["source_type"]

        error = None
        errors: typing.Dict[str, str] = {}

        directory = data["directory"]

        if source_type == "gdoc":
            try:
                self.link_google_doc(request.user, data, directory)
            except LinkException as e:
                error = str(e)
        elif source_type == "url":
            self.link_url(data, directory, errors)
        else:
            error = "Unknown source type {}".format(source_type)

        resp: typing.Dict[str, typing.Any] = {"success": not error and not errors}

        if errors:
            resp["errors"] = errors
        else:
            resp["error"] = error

        return JsonResponse(resp)

    def link_google_doc(self, user: User, request_body: dict, directory: str) -> None:
        token = user_social_token(user, "google")

        if token is None:
            raise LinkException(
                "Can't link as no Google account is connected to Stencila Hub."
            )

        doc_id = request_body["document_id"]

        if not doc_id:
            raise LinkException("A document ID or URL was not provided.")

        doc_id = GoogleDocsSource.parse_address(doc_id, naked=True, strict=True).doc_id

        google_app = SocialApp.objects.filter(provider="google").first()

        gdf = GoogleDocsFacade(google_app.client_id, google_app.secret, token)

        try:
            document = gdf.get_document(doc_id)
        except HttpAccessTokenRefreshError:
            raise LinkException(
                "Could not refresh your Google authentication token. Please contact support for more information."
            )
        except HttpError:
            raise LinkException(
                "Could not retrieve the document, please check the ID/URL."
            )

        title = document["title"]

        source = GoogleDocsSource(
            doc_id=doc_id,
            project=self.project,
            path=utf8_path_join(directory, title.replace("/", "-")),
        )

        source.save()
        messages.success(
            self.request,
            "Google Doc <em>{}</em> was linked.".format(escape(title)),
            extra_tags="safe",
        )

    def link_url(self, request_body: dict, directory: str, errors: dict) -> None:
        url = request_body["url"]

        try:
            URLValidator()(url)
        except ValidationError:
            errors["url"] = '"{}" is not a valid URL.'.format(url)

        filename = request_body["filename"]

        if filename == "":
            errors["filename"] = "The filename must be set."
        elif "/" in filename or ":" in filename or "\\" in filename or ";" in filename:
            errors[
                "filename"
            ] = "The filename must not contain the characters /, :, \\ or ;."

        if errors:
            return

        fetch_url(url, user_agent=settings.STENCILA_CLIENT_USER_AGENT)
        path = utf8_path_join(directory, filename.replace("/", "-"))
        source = UrlSource(url=url, project=self.project, path=path)
        source.save()
        messages.success(
            self.request,
            "URL <em>{}</em> was linked.".format(escape(url)),
            extra_tags="safe",
        )


# Views below are not DRF views, they should be


class DiskItemCreateView(ProjectPermissionsMixin, View):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk=pk)

        dff = DiskFileFacade(settings.STORAGE_DIR, project)

        body = json.loads(request.body)

        item_type = ItemType(body["type"])
        path = body["path"]

        error = None

        if dff.item_exists(path):
            error = 'Item exists at "{}".'.format(path)
        elif item_type == ItemType.FILE:
            dff.create_file(path)
        elif item_type == ItemType.FOLDER:
            dff.create_directory(path)
        else:
            raise TypeError("Don't know how to create a {}".format(item_type))

        return JsonResponse({"success": not error, "error": error})


class DiskItemMoveView(ProjectPermissionsMixin, View):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk=pk)

        dff = DiskFileFacade(settings.STORAGE_DIR, project)

        body = json.loads(request.body)

        source = body["source"]
        destination = body["destination"]

        error = None

        if not dff.item_exists(source):
            error = 'Source item does not exist at "{}".'.format(source)
        elif dff.item_exists(destination):
            error = 'Destination already exists at "{}".'.format(destination)
        else:
            dff.move_file(source, destination)

        return JsonResponse({"success": not error, "error": error})


class DiskItemRemoveView(ProjectPermissionsMixin, View):
    swagger_schema = None
    project_permission_required = ProjectPermissionType.EDIT

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:  # type: ignore
        project = self.get_project(request.user, pk=pk)

        dff = DiskFileFacade(settings.STORAGE_DIR, project)

        body = json.loads(request.body)

        path = body["path"]

        error = None

        if not dff.item_exists(path):
            error = 'Item does not exist at "{}".'.format(path)
        else:
            dff.remove_item(path)

        return JsonResponse({"success": not error, "error": error})
