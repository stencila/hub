import typing

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from lib.forms import ModelFormWithSubmit
from projects.project_models import Project
from .source_models import FileSource, GithubSource, Source

# TODO: these should be proper mime types!
FILE_TYPES = [
    # ('text/folder', 'Folder'),
    ('text/dar', 'Dar'),
    ('text/dockerfile', 'Dockerfile'),
    ('text/ipynb', 'Jupyter Notebook'),
    ('text/rmarkdown', 'RMarkdown'),
]


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


class FileSourceForm(ModelFormWithSubmit):
    type = forms.ChoiceField(choices=FILE_TYPES)
    path = forms.RegexField(regex=r'^[^/][A-Za-z\-/\.]+[^/]$', widget=forms.TextInput,
                            error_messages={'invalid': 'The path must not contain spaces, or start or end with a /'})

    class Meta:
        model = FileSource
        fields = ('path',)
        widgets = {
            'type': forms.Select(),
            'path': forms.TextInput()
        }

    def clean(self):
        validate_unique_project_path(self.initial['project'], self.cleaned_data['path'])
        return super().clean()


class SourceUpdateForm(ModelForm):
    path = forms.RegexField(regex=r'^[^/][A-Za-z\-/\.]+[^/]$', widget=forms.TextInput,
                            error_messages={'invalid': 'The path must not contain spaces, or start or end with a /'})

    class Meta:
        model = Source
        fields = ('path',)

    def clean(self):
        validate_unique_project_path(self.instance.project, self.cleaned_data['path'], self.instance.pk)
        return super().clean()


class GithubSourceForm(ModelFormWithSubmit):
    class Meta:
        model = GithubSource
        fields = ('path', 'repo', 'subpath')
        widgets = {
            'repo': forms.TextInput(),
            'subpath': forms.TextInput(),
            'path': forms.TextInput()
        }
