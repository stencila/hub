from django import forms

from lib.forms import ModelFormWithSubmit
from .source_models import FileSource

FILE_TYPES = [
    ('text/rmarkdown', 'RMarkdown'),
    ('text/ipynb', 'Jupyter Notebook')
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
