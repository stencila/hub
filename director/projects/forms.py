import typing

from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms import ChoiceField, FloatField, IntegerField
from django.http import QueryDict, HttpRequest

from .models import FilesSource, SessionParameters, Source, Project, generate_project_key


def get_initial_form_data_from_project(project: typing.Optional[Project]) -> dict:
    if not project:
        return {}

    initial = {
        key: getattr(project, key) for key in
        ('token', 'key', 'max_concurrent', 'max_sessions', 'session_parameters', 'public')
    }

    initial['source'] = project.sources.first()

    return initial


def update_project_from_form_data(request: HttpRequest, project: Project, general_data: dict, session_data: dict,
                                  parameters_data: dict, access_data: dict) -> None:
    project.public = general_data['public']

    # at this stage assume a 1:1 mapping Project:Source even though the DB support multiple sources
    # update this when allowing for 1:n mapping in the UI
    project.sources.clear()
    if general_data['source']:
        project.sources.add(general_data['source'])

    project.max_concurrent = session_data['max_concurrent']
    project.max_sessions = session_data['max_sessions']

    if access_data['generate_key']:
        project.key = generate_project_key()
    else:
        project.key = access_data['key']

    project.save()

    session_parameters = project.session_parameters or SessionParameters(owner=request.user)
    session_parameters.memory = parameters_data['memory']
    session_parameters.cpu = parameters_data['cpu']
    session_parameters.network = parameters_data['network']
    session_parameters.lifetime = parameters_data['lifetime']
    session_parameters.timeout = parameters_data['timeout']

    session_parameters.save()

    if project.session_parameters != session_parameters:
        project.session_parameters = session_parameters
        project.save()


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
        help_text="This key needs to be used when creating a Session. Leave blank to not require a key.",
        widget=forms.TextInput(attrs={"v-model": "key"})
    )

    generate_key = forms.BooleanField(
        required=False,
        help_text="Automatically generate an access key when saved.",
        widget=forms.CheckboxInput(attrs={"v-model": "generateKey", "@change": "generateKeyChange()"})
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

    session_parameters = forms.ModelChoiceField(
        required=True,
        queryset=SessionParameters.objects.none(),  # this needs to be set at runtime
        help_text='The Session Parameters to use to define resources when creating new Sessions in this project.'
    )

    source = forms.ModelChoiceField(
        required=False,
        queryset=Source.objects.none(),  # this needs to be set at runtime,
        help_text='The data for this Project'
    )

    def populate_choice_fields(self, user: User):
        self.fields['session_parameters'].queryset = SessionParameters.objects.filter(owner=user)

        source_query = Q(creator=user)

        if 'source' in self.initial:
            source_query = source_query | Q(pk=self.initial['source'].id)

        self.fields['source'].queryset = Source.objects.filter(source_query)

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


class SessionParametersForm(ModelFormWithSubmit):
    submit_button_label = None

    class Meta:
        model = SessionParameters
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


class SessionParametersUpdateForm(SaveButtonMixin, SessionParametersForm):
    pass


class SessionParametersCreateForm(CreateButtonMixin, SessionParametersForm):
    pass


class FilesSourceForm(ModelFormWithSubmit):
    class Meta:
        model = FilesSource
        fields = ["project"]


class FilesSourceUpdateForm(SaveButtonMixin, FilesSourceForm):
    pass


class FilesSourceCreateForm(CreateButtonMixin, FilesSourceForm):
    pass


class ProjectGeneralForm(forms.Form):
    helper = FormHelper()

    public = forms.BooleanField(
        required=False,
        help_text="Make this project available to anyone."
    )

    source = forms.ModelChoiceField(
        required=False,
        queryset=Source.objects.none(),  # this needs to be set at runtime,
        help_text="The data for this Project"
    )

    @staticmethod
    def initial_data_from_project(project: typing.Optional[Project]) -> dict:
        return {} if project is None else {
            "public": project.public,
            "source": project.sources.first()
        }

    def populate_source_choices(self, request: HttpRequest) -> None:
        self.fields['source'].queryset = Source.objects.filter(creator=request.user)


class ProjectSessionsForm(forms.Form):
    helper = FormHelper()

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

    @staticmethod
    def initial_data_from_project(project: typing.Optional[Project]) -> dict:
        return {} if project is None else {
            "max_concurrent": project.max_concurrent,
            "max_sessions": project.max_sessions
        }


class ProjectSessionParametersForm(forms.Form):
    helper = FormHelper()

    memory = FloatField(
        # default=1,
        min_value=0,
        required=True,
        help_text='Gigabytes (GB) of memory allocated.',
        widget=forms.NumberInput(attrs={"v-model": "spMemory"})
    )

    cpu = FloatField(
        label="CPU",
        required=True,
        min_value=1,
        max_value=100,
        # default=1,
        help_text='CPU shares (out of 100 per CPU) allocated.',
        widget=forms.NumberInput(attrs={"v-model": "spCpu"})
    )

    network = FloatField(
        min_value=0,
        required=False,
        help_text='Gigabytes (GB) of network transfer allocated. Leave blank for unlimited.',
        widget=forms.NumberInput(attrs={"v-model": "spNetwork"})
    )

    lifetime = IntegerField(
        min_value=0,
        required=False,
        help_text='Minutes before the session is terminated (even if active). Leave blank for unlimited.',
        widget=forms.NumberInput(attrs={"v-model": "spLifetime"})
    )

    timeout = IntegerField(
        # default=60,
        min_value=0,
        required=True,
        help_text='Minutes of inactivity before the session is terminated. Leave blank for unlimited.',
        widget=forms.NumberInput(attrs={"v-model": "spTimeout"})
    )

    def clean(self) -> dict:
        cleaned_data = super().clean()

        if cleaned_data['lifetime'] is not None and (
                cleaned_data['timeout'] is None
                or cleaned_data['timeout'] > cleaned_data['lifetime']):
            self.add_error('timeout', 'The idle timeout must be less that the maximum lifetime of the Session.')
        return cleaned_data

    @staticmethod
    def initial_data_from_project(project: Project) -> dict:
        return {} if (project is None or project.session_parameters is None) else {
            "memory": project.session_parameters.memory,
            "cpu": project.session_parameters.cpu,
            "network": project.session_parameters.network,
            "lifetime": project.session_parameters.lifetime,
            "timeout": project.session_parameters.timeout
        }


class ProjectAccessForm(forms.Form):
    helper = FormHelper()

    token = forms.CharField(
        required=False,
        disabled=True,
        help_text='Unique token identifying this group. This will be generated when first saved.'
    )

    key = forms.CharField(
        label="Access Key",
        required=False,
        max_length=128,
        help_text="This key needs to be used when creating a Session. Leave blank to not require a key.",
        widget=forms.TextInput(attrs={"v-model": "key", ":disabled": "generateKey"})
    )

    generate_key = forms.BooleanField(
        required=False,
        help_text="Automatically generate an access key on save.",
        widget=forms.CheckboxInput(attrs={"v-model": "generateKey", "@change": "generateKeyChange()"})
    )

    @staticmethod
    def initial_data_from_project(project: Project) -> dict:
        return {} if project is None else {
            "token": project.token,
            "key": project.key
        }
