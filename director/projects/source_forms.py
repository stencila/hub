import os
import re
import typing
from pathlib import PurePosixPath
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from lib.forms import ModelFormWithSubmit
from projects.project_models import Project
from .source_models import FileSource, GithubSource, Source


def validate_unique_project_path(project: Project, path: str, existing_source_pk: typing.Optional[int] = None) -> None:
    """
    Check if a `FileSource` with a path already exists for a given `Project`.

    If a path `FileSource` with path does exist raise a `ValidationError`.
    """
    # this check only matters for FileSource objects because linked sources can be mapped to the same path
    existing_sources = FileSource.objects.filter(project=project, path=path)

    if existing_source_pk:
        existing_sources = existing_sources.exclude(pk=existing_source_pk)

    if len(existing_sources):
        raise ValidationError("A source with path {} already exists for this project.".format(path))


class VirtualPathField(forms.CharField):
    """Field for validating paths to FileSource."""

    def clean(self, value):
        cleaned_value = super().clean(value)

        if cleaned_value.startswith('/') or cleaned_value.endswith('/'):
            raise ValidationError('The path must not start or end with a "/".')

        path = PurePosixPath(cleaned_value)
        for part in path.parts:
            if re.match(r'^\.+$', part):
                raise ValidationError('The path must not contain "." or ".." as components.')
        return cleaned_value


class FileSourceForm(ModelFormWithSubmit):
    path = VirtualPathField(required=True)

    current_directory: str = ''

    class Meta:
        model = FileSource
        fields = ('path',)

    def __init__(self, *args, **kwargs):
        if 'current_directory' in kwargs:
            self.current_directory = kwargs.pop('current_directory')

        super(FileSourceForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('path') is not None:
            cleaned_data['path'] = os.path.join(self.current_directory, cleaned_data['path'])

        if self.is_valid():
            validate_unique_project_path(self.initial['project'], cleaned_data['path'])
        return cleaned_data


class RelativeFileSourceForm(FileSourceForm):
    path = VirtualPathField(label='File name', required=True)


class SourceUpdateForm(ModelForm):
    path = VirtualPathField(required=True)

    class Meta:
        model = Source
        fields = ('path',)

    def clean(self):
        cleaned_data = super().clean()
        if 'path' in cleaned_data:  # it might not be, if the form is not valid then cleaned_data will be an empty dict
            validate_unique_project_path(self.instance.project, cleaned_data['path'], self.instance.pk)
        return cleaned_data


class GithubSourceForm(ModelFormWithSubmit):
    class Meta:
        model = GithubSource
        fields = ('path', 'repo', 'subpath')
        widgets = {
            'repo': forms.TextInput(),
            'subpath': forms.TextInput(),
            'path': forms.TextInput()
        }

    @staticmethod
    def raise_repo_validation_error(repo: str) -> None:
        raise ValidationError('"{}" is not a valid Github repository. A repository (in the format "username/path", or '
                              'a URL) is required.'.format(repo))

    def clean_repo(self) -> str:
        """Validate that the repo is either in the format `username/repo`, or extract this from a Github URL."""
        repo = self.cleaned_data['repo']
        if not repo:
            self.raise_repo_validation_error(repo)

        github_url = urlparse(self.cleaned_data['repo'])

        if github_url.scheme.lower() not in ('https', 'http', ''):
            self.raise_repo_validation_error(repo)

        if github_url.netloc.lower() not in ('github.com', ''):
            self.raise_repo_validation_error(repo)

        repo_match = re.match(r"^((github\.com/)|/)?([a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38})/([\w_-]+)/?$",
                              github_url.path, re.I)

        if not repo_match:
            self.raise_repo_validation_error(repo)

        repo_match = typing.cast(typing.Match, repo_match)

        return '{}/{}'.format(repo_match[3], repo_match[4])
