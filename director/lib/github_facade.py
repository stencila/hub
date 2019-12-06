import typing
from datetime import datetime

import pytz
from github import Github
from github.Repository import Repository


class GithubDirectoryEntry(typing.NamedTuple):
    name: str
    is_directory: bool
    last_modified: datetime


class GitHubFacade(object):
    _github_connector: typing.Optional[Github] = None
    _repository: typing.Optional[Repository] = None

    def __init__(self, repository_path: str, access_token: typing.Optional[str] = None) -> None:
        self.repository_path = repository_path
        self.access_token = access_token

    @property
    def github_connector(self) -> Github:
        if self._github_connector is None:
            self._github_connector = Github(self.access_token)
        return self._github_connector

    @property
    def repository(self) -> Repository:
        if self._repository is None:
            self._repository = self.github_connector.get_repo(self.repository_path)
        return self._repository

    def list_directory(self, relative_path: str) -> typing.Iterable[GithubDirectoryEntry]:
        while relative_path.endswith('/'):
            relative_path = relative_path[:-1]

        contents = self.repository.get_contents(relative_path)
        for content in contents:
            last_modified = datetime.strptime(content.last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            yield GithubDirectoryEntry(content.name, content.type == 'dir', last_modified.replace(tzinfo=pytz.UTC))

    def get_file_content(self, relative_path: str, encoding) -> str:
        return self.get_binary_file_content(relative_path).decode(encoding)

    def get_binary_file_content(self, relative_path: str) -> bytearray:
        f = self.repository.get_contents(relative_path)
        return f.decoded_content

    def put_file_content(self, relative_path: str, content: str, commit_message: str) -> None:
        f = self.repository.get_contents(relative_path)
        self.repository.update_file(f.path, commit_message, content, f.sha)

    def get_size(self, relative_path: str) -> int:
        return self.repository.get_contents(relative_path).size

    @property
    def allows_editing(self) -> bool:
        """
        Return False if self does not allow editing, or return True if it might allow editing.

        This function is kind of a guess. If `self.access_token` is empty then editing is definitely not allowed. If it
        is set, then editing might be allowed, assuming the token is valid and for the correct user etc.
        """
        return True if self.access_token else False
