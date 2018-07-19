from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import FilesProject, FilesProjectFile


class ProjectCreateForm(forms.Form):
    """
    Form for selecting the type of project to create
    """

    type = forms.ChoiceField(
        label='Project type',
        help_text='Select the type of project you would like to create',
        choices=[
            ('files', 'Uploaded files')
        ]
    )

    helper = FormHelper()
    helper.add_input(
        Submit('submit', 'Create', css_class='button is-primary')
    )


class FilesProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = FilesProject
        fields = ['name']


class FilesProjectFileUpdateForm(forms.ModelForm):
    class Meta:
        model = FilesProjectFile
        fields = ['file']


FilesProjectFileFormSet = forms.inlineformset_factory(
    FilesProject, FilesProjectFile,
    form=FilesProjectFileUpdateForm,
    extra=1
)
