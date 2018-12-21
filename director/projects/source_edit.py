import os
import typing
from io import BytesIO
from os.path import splitext

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from github import GithubException

from lib.github_facade import GitHubFacade
from projects.source_models import Source, GithubSource, FileSource, LinkedSourceAuthentication
from projects.source_operations import strip_directory


class SourceEditContext(typing.NamedTuple):
    path: str
    extension: str
    content: typing.Union[str, BytesIO]
    source: Source
    editable: bool
    supports_commit_message: bool


class SourceContentFacade(object):
    source: Source
    request: HttpRequest
    authentication: LinkedSourceAuthentication
    file_path: str

    def __init__(self, source: Source, authentication: LinkedSourceAuthentication, request: HttpRequest,
                 file_path: str) -> None:
        self.source = source
        self.authentication = authentication
        self.request = request
        self.file_path = file_path

    def get_content(self) -> typing.Union[str, BytesIO]:
        if isinstance(self.source, FileSource):
            return self.get_file_source_content()
        elif isinstance(self.source, GithubSource):
            return self.get_github_source_content()
        else:
            raise TypeError("Don't know how to get content for source type '{}'".format(type(self.source)))

    def get_file_source_content(self) -> BytesIO:
        return self.source.pull()

    def get_github_source_content(self) -> str:
        source = typing.cast(GithubSource, self.source)
        path_in_repo = self.get_github_repository_path()

        gh = GitHubFacade(source.repo, self.authentication.github_token)
        return gh.get_file_content(path_in_repo)

    def get_github_repository_path(self) -> str:
        source = typing.cast(GithubSource, self.source)
        return os.path.join(source.subpath, strip_directory(self.file_path, source.path))

    def get_edit_context(self) -> SourceEditContext:
        if isinstance(self.source, FileSource):
            editable = True
            supports_commit_message = False
        elif isinstance(self.source, GithubSource):
            editable = self.authentication.github_token is not None
            supports_commit_message = True
        else:
            raise TypeError("Don't know how to get EditContext for source type '{}'".format(type(self.source)))

        _, ext = splitext(self.file_path.lower())
        content = self.get_content()
        return SourceEditContext(self.file_path, ext, content, self.source, editable, supports_commit_message)

    def update_content(self, content: str, commit_message: typing.Optional[str]) -> bool:
        if isinstance(self.source, FileSource):
            return self.update_file_source_content(content)
        elif isinstance(self.source, GithubSource):
            return self.update_github_source_content(content, commit_message)
        else:
            raise TypeError("Don't know how to update content for source type '{}'".format(type(self.source)))

    def update_file_source_content(self, content: str) -> bool:
        self.source.push(content)
        return True

    def update_github_source_content(self, content: str, commit_message: typing.Optional[str]) -> bool:
        if self.authentication.github_token is None:
            raise ValueError("Unable to save without a Github token.")  # user should not be able to post to here anyway

        if not commit_message:
            raise ValueError("Can not commit without a commit message.")

        path_in_repo = self.get_github_repository_path()

        source = typing.cast(GithubSource, self.source)
        gh = GitHubFacade(source.repo, self.authentication.github_token)

        try:
            gh.put_file_content(path_in_repo, content, commit_message)
        except GithubException as e:
            if e.status == 403:
                messages.error(self.request,
                               'Unable to save file. Please make sure you have installed the {} application '
                               'for your Github repositories. Please visit {} for more information.'.format(
                                   settings.STENCILA_GITHUB_APPLICATION_NAME, settings.STENCILA_GITHUB_APPLICATION_URL)
                               )
            elif e.status == 404:
                # this error usually will occur if the application is not set up with the correct rights on the
                # Stencila side, so the user can't really fix this
                messages.error(self.request, 'Unable to save file. Please make sure the file exists, and if it does,'
                                             'make sure Github integrations are set up correctly.')
            else:
                raise

            return False
        return True
