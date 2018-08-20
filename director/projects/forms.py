import typing

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.models import User
from django.http import QueryDict

from .models import FilesSource, ResourceLimit, DataSource, Project, generate_project_key


def get_initial_form_data_from_project(project: typing.Optional[Project]) -> dict:
    if not project:
        return {}

    initial = {
        key: getattr(project, key) for key in
        ('token', 'key', 'max_concurrent', 'max_sessions', 'resource_limit', 'public')
    }

    initial['source'] = project.sources.first()

    return initial


def update_project_from_form_data(project: Project, form_data: QueryDict) -> None:
    project.max_concurrent = form_data['max_concurrent']
    project.max_sessions = form_data['max_sessions']
    project.resource_limit = form_data['resource_limit']
    project.public = form_data['public']

    # at this stage assume a 1:1 mapping Project:Source even though the DB support multiple sources
    # update this when allowing for 1:n mapping in the UI
    project.sources.clear()
    if form_data['source']:
        project.sources.add(form_data['source'])

    if form_data['generate_key']:
        project.key = generate_project_key()
    else:
        project.key = form_data['key']


class OldProjectCreateForm(forms.Form):
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


def form_add_submit_button(form: typing.Any) -> None:
    form.helper = FormHelper()
    form.helper.add_input(
        Submit('submit', form.submit_button_label, css_class='button is-primary')
    )


class FormWithSubmit(forms.Form):
    def __init__(self, *args, **kwargs) -> None:
        super(FormWithSubmit, self).__init__(*args, **kwargs)
        form_add_submit_button(self)


class ModelFormWithSubmit(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        super(ModelFormWithSubmit, self).__init__(*args, **kwargs)
        form_add_submit_button(self)


class SaveButtonMixin:
    submit_button_label = "Save"


class CreateButtonMixin:
    submit_button_label = "Create"


class ProjectForm(FormWithSubmit):
    """
    Form for creating a Project
    """

    public = forms.BooleanField(
        required=False,
        help_text="Make this project available to anyone."
    )

    token = forms.CharField(
        required=False,
        disabled=True,
        help_text='Unique token identifying this group. This will be generated when first saved.'
    )

    key = forms.CharField(
        label="Access Key",
        required=False,
        max_length=128,
        help_text="This key needs to be used when creating a Session. Leave blank to not require a key."
    )

    generate_key = forms.BooleanField(
        required=False,
        help_text="Automatically generate an access key."
    )

    max_concurrent = forms.IntegerField(
        required=False,
        min_value=1,
        help_text='The maximum number of sessions to run at one time. Leave blank for unlimited.'
    )

    max_sessions = forms.IntegerField(
        required=False,
        min_value=1,
        help_text='The total maximum number of sessions allowed to create. Leave blank for unlimited.'
    )

    resource_limit = forms.ModelChoiceField(
        required=True,
        queryset=ResourceLimit.objects.none(),  # this needs to be set at runtime
        help_text='The Resource Limit to use to define resources when creating new Sessions in this project.'
    )

    source = forms.ModelChoiceField(
        required=False,
        queryset=DataSource.objects.none(),  # this needs to be set at runtime,
        help_text='The data source for this Project'
    )

    def populate_choice_fields(self, user: User):
        self.fields['resource_limit'].queryset = ResourceLimit.objects.filter(owner=user)
        self.fields['source'].queryset = DataSource.objects.filter(creator=user)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['max_sessions'] is not None and (
                cleaned_data['max_concurrent'] is None
                or cleaned_data['max_concurrent'] > cleaned_data['max_sessions']):
            self.add_error('max_concurrent',
                           "The maximum number of concurrent sessions must be less than the maximum number of total "
                           "sessions.")

        return cleaned_data


class ProjectCreateForm(CreateButtonMixin, ProjectForm):
    pass


class ProjectUpdateForm(SaveButtonMixin, ProjectForm):
    pass


class ResourceLimitForm(ModelFormWithSubmit):
    submit_button_label = None

    class Meta:
        model = ResourceLimit
        fields = ['name', 'description', 'memory', 'cpu', 'network', 'lifetime', 'timeout']

        widgets = {
            'name': forms.TextInput
        }

        labels = {
            'cpu': 'CPU'
        }

        help_texts = {
            'network': 'Gigabytes (GB) of network transfer allocated. Leave blank for unlimited.',
            'lifetime': 'Minutes before the session is terminated (even if active). Leave blank for unlimited.',
            'timeout': 'Minutes of inactivity before the session is terminated. Leave blank for unlimited.'
        }

    def clean(self) -> dict:
        cleaned_data = super().clean()

        if cleaned_data['lifetime'] is not None and (
                cleaned_data['timeout'] is None
                or cleaned_data['timeout'] > cleaned_data['lifetime']):
            self.add_error('timeout', 'The idle timeout must be less that the maximum lifetime of the Session.')
        return cleaned_data


class ResourceLimitUpdateForm(SaveButtonMixin, ResourceLimitForm):
    pass


class ResourceLimitCreateForm(CreateButtonMixin, ResourceLimitForm):
    pass


class FilesSourceForm(ModelFormWithSubmit):
    class Meta:
        model = FilesSource
        fields = ["project"]


class FilesSourceUpdateForm(SaveButtonMixin, FilesSourceForm):
    pass


class FilesSourceCreateForm(CreateButtonMixin, FilesSourceForm):
    pass
