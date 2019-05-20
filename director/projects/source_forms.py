import re
import typing
from pathlib import PurePosixPath
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError

from lib.forms import ModelFormWithSubmit, FormWithSubmit
from lib.google_docs_facade import extract_google_document_id_from_url, google_document_id_is_valid
from .source_models import GithubSource, GoogleDocsSource


class PathField(forms.CharField):
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


class DiskFileSourceForm(FormWithSubmit):
    path = PathField(required=True)


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


class GoogleDocsSourceForm(ModelFormWithSubmit):
    class Meta:
        model = GoogleDocsSource
        fields = ('doc_id',)

    def raise_doc_id_validation_error(self, doc_id: str) -> None:
        raise ValidationError(
            '"{}" is not a valid Google Document. A or Google Document ID or URL is required.'.format(doc_id))

    def clean_doc_id(self) -> str:
        """If a Google Docs URL is entered then extract the Document ID."""
        doc_id = self.cleaned_data['doc_id']
        if not doc_id:
            self.raise_doc_id_validation_error(doc_id)

        try:
            doc_id = extract_google_document_id_from_url(doc_id)
        except ValueError:
            pass  # not a URL, could just a be the ID

        if not google_document_id_is_valid(doc_id):
            self.raise_doc_id_validation_error(doc_id)

        return doc_id
