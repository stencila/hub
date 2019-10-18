import json
import typing
from os.path import splitext

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import constants as message_constants
from django.http import HttpRequest
from github import GithubException, RateLimitExceededException

from lib.github_facade import GitHubFacade
from lib.google_docs_facade import GoogleDocsFacade
from lib.social_auth_token import user_github_token, user_social_token
from projects.disk_file_facade import DiskFileFacade
from projects.project_models import Project
from projects.source_models import Source, GithubSource, DiskSource, GoogleDocsSource
from projects.source_operations import strip_directory, utf8_path_join, utf8_basename

DEFAULT_TEXT_ENCODING = 'utf8'


class SourceEditContext(typing.NamedTuple):
    path: str
    extension: str
    content: typing.Union[str, bytes]
    source: typing.Union[Source, DiskSource]
    editable: bool
    supports_commit_message: bool


class Message(typing.NamedTuple):
    level: int
    message: str


def rate_limit_decorator(func):
    def wrapper(scf, *args, **kwargs):
        try:
            return func(scf, *args, **kwargs)
        except RateLimitExceededException:
            scf.add_rate_limit_exceeded_error()
            return None

    return wrapper


class SourceContentFacade(object):
    file_path: str
    source: typing.Union[Source, DiskSource]
    messages: typing.List[Message]
    disk_file_facade: DiskFileFacade
    github_facade: typing.Optional[GitHubFacade]
    google_docs_facade: typing.Optional[GoogleDocsFacade]
    encoding: str

    def __init__(self, file_path: str, source: typing.Union[Source, DiskSource],
                 disk_file_facade: DiskFileFacade,
                 github_facade: typing.Optional[GitHubFacade],
                 google_docs_facade: typing.Optional[GoogleDocsFacade], encoding=DEFAULT_TEXT_ENCODING) -> None:
        self.messages = []
        self.file_path = file_path
        self.source = source
        self.disk_file_facade = disk_file_facade
        self.github_facade = github_facade
        self.google_docs_facade = google_docs_facade
        self.encoding = encoding

    def get_content(self) -> typing.Union[str, dict]:
        if isinstance(self.source, GithubSource):
            return self.get_github_source_content()

        if isinstance(self.source, DiskSource):
            return self.get_disk_source_content()

        if isinstance(self.source, GoogleDocsSource):
            return self.get_google_docs_source_content()

        raise TypeError('Don\'t know how to get content for source type \'{}\''.format(type(self.source)))

    def get_binary_content(self) -> bytes:
        if isinstance(self.source, GithubSource):
            return self.get_github_source_binary_content()

        if isinstance(self.source, DiskSource):
            return self.get_disk_source_binary_content()

        if isinstance(self.source, GoogleDocsSource):
            return self.get_google_docs_source_binary_content()

        raise TypeError('Don\'t know how to get binary content for source type \'{}\''.format(type(self.source)))

    def get_edit_context(self) -> typing.Optional[SourceEditContext]:
        supports_commit_message = False

        if isinstance(self.source, GithubSource):
            if not self.github_facade:
                raise TypeError('Can\'t edit, GithubFacade not set.')

            editable = self.github_facade.allows_editing
            supports_commit_message = True
        elif isinstance(self.source, DiskSource):
            editable = True
        else:
            raise TypeError('Don\'t know how to get EditContext for source type \'{}\''.format(type(self.source)))

        _, ext = splitext(self.file_path.lower())
        content = self.get_content()

        if not isinstance(content, (str, bytes)):
            if content is None and self.error_exists:
                return None
            raise TypeError('Can\'t edit a non str or BytesIO')

        return SourceEditContext(self.file_path, ext, content, self.source, editable, supports_commit_message)

    def update_content(self, content: str, commit_message: typing.Optional[str] = None) -> bool:
        if isinstance(self.source, DiskSource):
            return self.update_disk_source_content(content)

        if isinstance(self.source, GithubSource):
            return self.update_github_source_content(content, commit_message)

        raise TypeError('Don\'t know how to update content for source type \'{}\''.format(type(self.source)))

    # Messages decoupled from request
    def add_message(self, level: int, message: str) -> None:
        self.messages.append(Message(level, message))

    def message_iterator(self) -> typing.Iterator[Message]:
        while self.messages:
            yield self.messages.pop(0)

    def add_rate_limit_exceeded_error(self) -> None:
        self.add_message(message_constants.ERROR, 'Could not access Github because the anonymous rate limit has been '
                                                  'reached. Add your Github account on the Account Connections page to '
                                                  'prevent this error in the future.')

    # Github
    @rate_limit_decorator
    def get_github_source_content(self) -> str:
        if not self.github_facade:
            raise TypeError('Can\'t continue, GithubFacade not set.')

        path_in_repo = self.get_github_repository_path()
        return self.github_facade.get_file_content(path_in_repo, self.encoding)

    @rate_limit_decorator
    def get_github_source_binary_content(self) -> bytes:
        if not self.github_facade:
            raise TypeError('Can\'t continue, GithubFacade not set.')

        path_in_repo = self.get_github_repository_path()
        return self.github_facade.get_binary_file_content(path_in_repo)

    def get_github_repository_path(self) -> str:
        source = typing.cast(GithubSource, self.source)
        return utf8_path_join(source.subpath, strip_directory(self.file_path, source.path))

    @rate_limit_decorator
    def update_github_source_content(self, content: str, commit_message: str) -> bool:
        if not self.github_facade:
            raise TypeError('Can\'t continue, GithubFacade not set.')

        if not self.github_facade.allows_editing:
            raise PermissionError('Unable to commit without a Github Token.')

        if not commit_message:
            raise ValueError('Unable to commit without a commit message.')

        path_in_repo = self.get_github_repository_path()

        try:
            self.github_facade.put_file_content(path_in_repo, content, commit_message)
        except GithubException as e:
            if e.status == 403:
                self.add_message(message_constants.ERROR,
                                 'Unable to save file. Please make sure you have installed the {} application for your '
                                 'Github repositories. Please visit {} for more information.'.format(
                                     settings.STENCILA_GITHUB_APPLICATION_NAME,
                                     settings.STENCILA_GITHUB_APPLICATION_URL)
                                 )
            elif e.status == 404:
                # this error usually will occur if the application is not set up with the correct rights on the
                # Stencila side, so the user can't really fix this
                self.add_message(message_constants.ERROR,
                                 'Unable to save file. Please make sure the file exists, and if it does, make sure '
                                 'Github integrations are set up correctly.')
            else:
                raise

            return False
        return True

    # Disk
    def get_disk_source_content(self) -> str:
        return self.disk_file_facade.read_file_content(self.file_path).decode(self.encoding)

    def update_disk_source_content(self, content: str) -> bool:
        self.disk_file_facade.write_file_content(self.file_path, content.encode(self.encoding))
        return True

    def get_disk_source_binary_content(self) -> bytes:
        return self.disk_file_facade.read_file_content(self.file_path)

    # Google Docs
    def get_google_docs_source_content(self) -> dict:
        if not self.google_docs_facade:
            raise TypeError('Can\'t continue, GithubFacade not set.')

        if not isinstance(self.source, GoogleDocsSource):
            raise TypeError('Attempting to get Google Docs content from a non GoogleDocsSource')

        return self.google_docs_facade.get_document(self.source.doc_id)

    def get_google_docs_source_binary_content(self) -> bytes:
        doc = self.get_google_docs_source_content()

        return json.dumps(doc).encode(self.encoding)

    def get_name(self) -> str:
        """Get the name of the source (i.e. basename)."""
        return utf8_basename(self.file_path)

    @property
    def error_exists(self) -> bool:
        try:
            filter(lambda m: m.level == message_constants.ERROR, self.messages)
        except StopIteration:
            return False
        return True

    def add_messages_to_request(self, request: HttpRequest) -> None:
        for message in self.message_iterator():
            messages.add_message(request, message.level, message.message)


def make_source_content_facade(user: User, file_path: str, source: typing.Union[Source, DiskSource],
                               project: Project) -> SourceContentFacade:
    disk_facade = DiskFileFacade(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)

    gh_token = user_github_token(user)

    gh_facade: typing.Optional[GitHubFacade] = None

    if isinstance(source, GithubSource):
        source = typing.cast(GithubSource, source)

        gh_facade = GitHubFacade(source.repo, gh_token)

    gd_facade: typing.Optional[GoogleDocsFacade] = None

    if isinstance(source, GoogleDocsSource):
        source = typing.cast(GoogleDocsSource, source)
        google_app = SocialApp.objects.filter(provider='google').first()

        if google_app is None:
            raise RuntimeError('No Google Docs app set up.')

        gd_facade = GoogleDocsFacade(google_app.client_id, google_app.secret, user_social_token(user, 'google'))

    return SourceContentFacade(file_path, source, disk_facade, gh_facade, gd_facade)
