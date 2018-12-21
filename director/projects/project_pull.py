import os
import pathlib

from lib.github_facade import GitHubFacade
from projects.project_models import Project
from projects.source_models import FileSource, GithubSource, LinkedSourceAuthentication
from projects.source_operations import normalise_path, path_is_in_directory


class ProjectPullHelper(object):
    project: Project
    authentication: LinkedSourceAuthentication
    checkout_path: str

    def __init__(self, project: Project, authentication: LinkedSourceAuthentication, checkout_path: str) -> None:
        self.project = project
        self.authentication = authentication
        self.checkout_path = checkout_path

    def pull(self) -> None:
        sources = list(self.project.sources.all())
        # FileSources should be processed last so that local content overwrites linked
        # True > False so FileSources will be at the end
        sources.sort(key=lambda s: isinstance(s, FileSource))

        for source in sources:
            if isinstance(source, FileSource):
                self.pull_file_source(source)
            elif isinstance(source, GithubSource):
                self.pull_github_source(source)
            else:
                raise TypeError("Don't know how to pull a source of type {}".format(type(source)))

    def pull_file_source(self, source: FileSource) -> None:
        local_path = normalise_path(os.path.join(self.checkout_path, source.path))
        local_containing_path = os.path.dirname(local_path)

        if os.path.normpath(local_containing_path) != os.path.normpath(self.checkout_path):
            pathlib.Path(local_containing_path).mkdir(parents=True, exist_ok=True)
        self.validate_checkout_subpath(local_path)
        with open(local_path, 'wb') as local_file:
            content = source.pull_binary()
            if content:
                local_file.write(content)

    def pull_github_source(self, source: GithubSource) -> None:
        facade = GitHubFacade(source.repo, self.authentication.github_token)
        self.pull_github_directory(source, facade, source.subpath)

    def pull_github_directory(self, source: GithubSource, github_facade: GitHubFacade, directory: str) -> None:
        trim_length = -len(source.subpath)

        trimmed_directory = directory[:trim_length] if trim_length != 0 else directory

        local_path = os.path.join(self.checkout_path, normalise_path(source.path), trimmed_directory)

        self.validate_checkout_subpath(local_path)

        pathlib.Path(local_path).mkdir(parents=True, exist_ok=True)

        for directory_entry in github_facade.list_directory(directory):
            item_path = os.path.join(directory, directory_entry.name)

            if directory_entry.is_directory:
                self.pull_github_directory(source, github_facade, item_path)
            else:
                self.pull_github_file(github_facade, os.path.join(local_path, directory_entry.name),
                                      os.path.join(directory, directory_entry.name))

    def pull_github_file(self, github_facade: GitHubFacade, local_path: str, remote_path: str) -> None:
        self.validate_checkout_subpath(local_path)
        with open(local_path, 'wb') as local_file:
            local_file.write(github_facade.get_binary_file_content(remote_path))

    def validate_checkout_subpath(self, path: str):
        if not path_is_in_directory(path, self.checkout_path):
            raise ValueError("{} is not a subpath of {}".format(path, self.checkout_path))
