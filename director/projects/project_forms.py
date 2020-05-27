import typing

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, HTML, Layout, Submit
from django import forms

from projects.source_models import Source
from .project_models import Project, PublishedItem

class ProjectSharingForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["public", "token", "key"]
        widgets = {"token": forms.TextInput(), "key": forms.TextInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML(
                    '<p class="title is-5">Public access</p>'
                    '<p class="subtitle is-6">Make this project readable by everyone!</p>'
                ),
                "public",
            ),
            Submit("submit", "Update", css_class="button is-primary"),
        )


class ProjectSettingsSessionsForm(forms.ModelForm):
    class Meta:
        model = Project
        fields: typing.List[str] = []

    sessions_total = forms.IntegerField(
        required=False,
        min_value=1,
        label="Total",
        help_text="Maximum total number of sessions that can be created for this project. Leave blank for unlimited.",
    )

    sessions_concurrent = forms.IntegerField(
        required=False,
        min_value=1,
        label="Concurrent",
        help_text="Maximum number of sessions allowed to run at one time for this project. Leave blank for unlimited.",
    )

    sessions_queued = forms.IntegerField(
        required=False,
        min_value=1,
        label="Queued",
        help_text="Maximum number of queued requests for a session for this project. Leave blank for unlimited.",
    )

    memory = forms.FloatField(
        min_value=0,
        required=False,
        help_text="Gigabytes (GB) of memory allocated.",
        widget=forms.NumberInput(attrs={"v-model": "memory"}),
    )

    cpu = forms.FloatField(
        label="CPU",
        required=False,
        min_value=1,
        max_value=100,
        help_text="CPU shares (out of 100 per CPU) allocated.",
        widget=forms.NumberInput(attrs={"v-model": "cpu"}),
    )

    network = forms.FloatField(
        min_value=0,
        required=False,
        help_text="Gigabytes (GB) of network transfer allocated. Leave blank for unlimited.",
        widget=forms.NumberInput(attrs={"v-model": "network"}),
    )

    lifetime = forms.IntegerField(
        min_value=0,
        required=False,
        help_text="Minutes before the session is terminated (even if active). Leave blank for unlimited.",
        widget=forms.NumberInput(attrs={"v-model": "lifetime"}),
    )

    timeout = forms.IntegerField(
        min_value=0,
        required=False,
        help_text="Minutes of inactivity before the session is terminated. Leave blank for unlimited.",
        widget=forms.NumberInput(attrs={"v-model": "timeout"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(
                        '<p class="title is-6 is-uppercase-heading">Session numbers</p>'
                        '<p class="subtitle is-6">Control the number of sessions for this project</p>'
                    ),
                    "sessions_concurrent",
                    "sessions_queued",
                    "sessions_total",
                    css_class="column is-half",
                ),
                Div(
                    HTML(
                        '<p class="title is-6 is-uppercase-heading">Session parameters</p>'
                        '<p class="subtitle is-6">Control the parameters for each session</p>'
                        '<preset-parameters @select-preset="selectPreset"></preset-parameters>'
                    ),
                    "memory",
                    "cpu",
                    "network",
                    "lifetime",
                    "timeout",
                    css_class="column is-half",
                ),
                css_class="columns",
            ),
            Submit("submit", "Update", css_class="button is-primary"),
        )

    @staticmethod
    def initial(project: Project) -> dict:
        return {
            "sessions_total": project.sessions_total,
            "sessions_concurrent": project.sessions_concurrent,
            "sessions_queued": project.sessions_queued,
            "memory": project.session_parameters.memory,
            "cpu": project.session_parameters.cpu,
            "network": project.session_parameters.network,
            "lifetime": project.session_parameters.lifetime,
            "timeout": project.session_parameters.timeout,
        }

    def clean(self) -> dict:
        cleaned_data = super().clean()

        if (
            cleaned_data["sessions_total"] is not None
            and cleaned_data["sessions_concurrent"] is not None
            and cleaned_data["sessions_concurrent"] > cleaned_data["sessions_total"]
        ):
            self.add_error(
                "sessions_concurrent",
                "The maximum number of concurrent Sessions must be less than the maximum total Sessions.",
            )

        if cleaned_data["lifetime"] is not None and (
            cleaned_data["timeout"] is None
            or cleaned_data["timeout"] > cleaned_data["lifetime"]
        ):
            self.add_error(
                "timeout",
                "The idle timeout must be less that the maximum lifetime of the Session.",
            )

        return cleaned_data

    def save(self, commit=True):
        project = super().save(commit=False)

        project.sessions_total = self.cleaned_data["sessions_total"]
        project.sessions_concurrent = self.cleaned_data["sessions_concurrent"]
        project.sessions_queued = self.cleaned_data["sessions_queued"]
        project.session_parameters.memory = self.cleaned_data["memory"]
        project.session_parameters.cpu = self.cleaned_data["cpu"]
        project.session_parameters.network = self.cleaned_data["network"]
        project.session_parameters.lifetime = self.cleaned_data["lifetime"]
        project.session_parameters.timeout = self.cleaned_data["timeout"]

        if commit:
            project.session_parameters.save()
            project.save()

        return project


class PublishedItemForm(forms.ModelForm):
    class Meta:
        model = PublishedItem
        fields = ["source_path", "url_path"]

    source_id = forms.IntegerField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        project = cleaned_data.get("project")

        if not project:
            return

        source_id = cleaned_data.get("source_id")

        if source_id:
            try:
                project.sources.get(pk=source_id)
            except Source.DoesNotExist:
                self.add_error(
                    "source_id",
                    "Source with id {} does not exist on this project.".format(
                        self.source_id
                    ),
                )
