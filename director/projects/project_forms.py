from django import forms

from lib.forms import ModelFormWithSubmit
from .project_models import Project


class ProjectCreateForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['account', 'name', 'description', 'public']
        widgets = {
            'name': forms.TextInput()
        }


class ProjectGeneralForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['name', 'description', 'public']
        widgets = {
            'name': forms.TextInput()
        }


class ProjectSettingsMetadataForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput()
        }
