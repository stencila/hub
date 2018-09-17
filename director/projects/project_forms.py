import typing

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Submit
from django import forms

from lib.forms import FormWithSubmit, ModelFormWithSubmit
from accounts.models import Account
from .project_models import Project, SessionParameters


class ProjectCreateForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['account', 'name', 'description', 'public']
        widgets = {
            'name': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

        accounts = Account.objects.filter(user_roles__user=request.user).distinct()
        self.fields['account'].queryset = accounts


class ProjectGeneralForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['name', 'description', 'public']
        widgets = {
            'name': forms.TextInput()
        }


class ProjectSharingForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['public', 'token', 'key']
        widgets = {
            'token': forms.TextInput(),
            'key': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML(
                    '<p class="title is-5">Public access</p>'
                    '<p class="subtitle is-6">Make this project readable by everyone!</p>'
                ),
                'public',
                css_class="section"
            ),
            Div(
                HTML(
                    '<p class="title is-5">Collaborator access</p>'
                    '<p class="subtitle is-6">Add collaborators to this project</p>'
                ),
                css_class="section"
            ),
            Submit('submit', 'Update', css_class="button is-primary")
        )


class ProjectSettingsMetadataForm(ModelFormWithSubmit):

    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput()
        }


class ProjectSettingsAccessForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ['token', 'key']
        widgets = {
            'token': forms.TextInput(),
            'key': forms.TextInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML(
                    '<p class="title is-5">API tokens and keys</p>'
                    '<p class="subtitle is-6">Set tokens and keys for API access to this project</p>'
                ),
                'token',
                'key',
                css_class="section"
            ),
            Submit('submit', 'Update', css_class="button is-primary")
        )


class ProjectSettingsSessionsForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = []

    sessions_total = forms.IntegerField(
        required=False,
        min_value=1,
        label='Total',
        help_text='Maximum total number of sessions that can be created for this project. Leave blank for unlimited.'
    )

    sessions_concurrent = forms.IntegerField(
        required=False,
        min_value=1,
        label='Concurrent',
        help_text='Maximum number of sessions allowed to run at one time for this project. Leave blank for unlimited.'
    )

    sessions_queued = forms.IntegerField(
        required=False,
        min_value=1,
        label='Queued',
        help_text='Maximum number of queued requests for a session for this project. Leave blank for unlimited.'
    )

    memory = forms.FloatField(
        min_value=0,
        required=False,
        help_text='Gigabytes (GB) of memory allocated.',
        widget=forms.NumberInput(attrs={'v-model': 'memory'})
    )

    cpu = forms.FloatField(
        label='CPU',
        required=False,
        min_value=1,
        max_value=100,
        help_text='CPU shares (out of 100 per CPU) allocated.',
        widget=forms.NumberInput(attrs={'v-model': 'cpu'})
    )

    network = forms.FloatField(
        min_value=0,
        required=False,
        help_text='Gigabytes (GB) of network transfer allocated. Leave blank for unlimited.',
        widget=forms.NumberInput(attrs={'v-model': 'network'})
    )

    lifetime = forms.IntegerField(
        min_value=0,
        required=False,
        help_text='Minutes before the session is terminated (even if active). Leave blank for unlimited.',
        widget=forms.NumberInput(attrs={'v-model': 'lifetime'})
    )

    timeout = forms.IntegerField(
        min_value=0,
        required=False,
        help_text='Minutes of inactivity before the session is terminated. Leave blank for unlimited.',
        widget=forms.NumberInput(attrs={'v-model': 'timeout'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(
                        '<p class="title is-5">Session numbers</p>'
                        '<p class="subtitle is-6">Control the number of sessions for this project</p>'
                    ),
                    'sessions_concurrent',
                    'sessions_queued',
                    'sessions_total',
                    css_class="column is-half section"
                ),
                Div(
                    HTML(
                        '<p class="title is-5">Session parameters</p>'
                        '<p class="subtitle is-6">Control the parameters for each session</p>'
                    ),
                    'memory',
                    'cpu',
                    'network',
                    'lifetime',
                    'timeout',
                    HTML('<preset-parameters @select-preset="selectPreset"></preset-parameters>'),
                    css_class="column is-half section"
                ),
                css_class="columns"
            ),
            Submit('submit', 'Update', css_class="button is-primary")
        )

    @staticmethod
    def initial(project):
        initial = {}
        initial['sessions_total'] = project.sessions_total
        initial['sessions_concurrent'] = project.sessions_concurrent
        initial['sessions_queued'] = project.sessions_queued
        initial['memory'] = project.session_parameters.memory
        initial['cpu'] = project.session_parameters.cpu
        initial['network'] = project.session_parameters.network
        initial['lifetime'] = project.session_parameters.lifetime
        initial['timeout'] = project.session_parameters.timeout
        return initial

    def clean(self) -> dict:
        cleaned_data = super().clean()

        if cleaned_data['sessions_total'] is not None and \
           cleaned_data['sessions_concurrent'] is not None and \
           cleaned_data['sessions_concurrent'] > cleaned_data['sessions_total']:
            self.add_error('sessions_concurrent',
                           'The maximum number of concurrent Sessions must be less than the maximum total Sessions.')

        if cleaned_data['lifetime'] is not None and (
                cleaned_data['timeout'] is None
                or cleaned_data['timeout'] > cleaned_data['lifetime']):
            self.add_error('timeout', 'The idle timeout must be less that the maximum lifetime of the Session.')

        return cleaned_data

    def save(self, commit=True):
        project = super().save(commit=False)

        project.sessions_total = self.cleaned_data['sessions_total']
        project.sessions_concurrent = self.cleaned_data['sessions_concurrent']
        project.sessions_queued = self.cleaned_data['sessions_queued']
        project.session_parameters.memory = self.cleaned_data['memory']
        project.session_parameters.cpu = self.cleaned_data['cpu']
        project.session_parameters.network = self.cleaned_data['network']
        project.session_parameters.lifetime = self.cleaned_data['lifetime']
        project.session_parameters.timeout = self.cleaned_data['timeout']

        if commit:
            project.session_parameters.save()
            project.save()

        return project
