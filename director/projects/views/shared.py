import os
import typing

from django.conf import settings
from django.contrib.auth.models import User

from lib.github_facade import GitHubFacade
from lib.social_auth_token import user_github_token
from projects.project_models import Project
from projects.source_models import Source, DiskSource, GithubSource
from projects.source_operations import generate_project_publish_directory, utf8_path_join, strip_directory, utf8_dirname

DEFAULT_ENVIRON = 'stencila/core'


def get_project_publish_directory(project: Project) -> str:
    return generate_project_publish_directory(settings.STENCILA_PROJECT_STORAGE_DIRECTORY, project)


def setup_publish_directory(project: Project) -> None:
    """Create directories and sub-directories to store HTML output for published files."""
    publish_dir = get_project_publish_directory(project)
    if not os.path.exists(publish_dir):
        os.makedirs(publish_dir, True)


def get_source(user: User, project: Project, path: str) -> typing.Union[Source, DiskSource]:
    """
    Locate a `Source` that contains the file at `path`.

    Iterate up through the directory tree of the path until Source(s) mapped to that path are found. Then check if that
    file exists in the source.

    Fall back to DiskSource if no file is found in any linked Sources.
    """
    # the paths won't match if the incoming path has a trailing slash as the paths on the source doesn't (shouldn't)
    path = path.rstrip('/')

    original_path = path

    gh_facade: typing.Optional[GitHubFacade] = None

    while True:
        sources = Source.objects.filter(path=path, project=project)

        if sources:
            if path == original_path:
                # This source should be one without sub files
                return sources[0]
            else:
                # These may be Github, etc, sources mapped into the same directory. Find one that has a file at the path

                for source in sources:
                    if isinstance(source, GithubSource):
                        source = typing.cast(GithubSource, source)

                        if gh_facade is None:
                            gh_token = user_github_token(user)
                            gh_facade = GitHubFacade(source.repo, gh_token)

                        relative_path = utf8_path_join(source.subpath, strip_directory(original_path, source.path))
                        if gh_facade.path_exists(relative_path):
                            return source  # this source has the file so it must be this one?

                        # if not, continue on, keep going up the tree to find the root source
                    else:
                        raise RuntimeError('Don\'t know how to examine the contents of {}'.format(type(source)))

        if path == '.':
            break
        path = utf8_dirname(path)
        if path == '/' or path == '':
            path = '.'

    # Fall Back to DiskSource
    return DiskSource()
