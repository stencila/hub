from django import forms

from lib.forms import ModelFormWithSubmit
from .source_models import FileSource, GithubSource

# TODO: these should be proper mime types!
FILE_TYPES = [
    # ('text/folder', 'Folder'),
    ('text/dar', 'Dar'),
    ('text/dockerfile', 'Dockerfile'),
    ('text/ipynb', 'Jupyter Notebook'),
    ('text/rmarkdown', 'RMarkdown'),
]


class FileSourceForm(ModelFormWithSubmit):
    type = forms.ChoiceField(choices=FILE_TYPES)
    path = forms.RegexField(regex=r'[A-Za-z\-/]+')

    class Meta:
        model = FileSource
        fields = ('path',)
        widgets = {
            'type': forms.Select(),
            'path': forms.TextInput()
        }


class GithubSourceForm(ModelFormWithSubmit):

    class Meta:
        model = GithubSource
        fields = ('path', 'repo', 'subpath')
        widgets = {
            'repo': forms.TextInput(),
            'subpath': forms.TextInput(),
            'path': forms.TextInput()
        }
