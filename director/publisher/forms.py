from django import forms

from publisher.models import SessionTemplate


class SessionGroupForm(forms.Form):
    token = forms.CharField(
        required=False,
        disabled=True,
        help_text='Unique token identifying this group. This will be generated when first saved.'
    )

    key = forms.CharField(
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

    template = forms.ModelChoiceField(
        required=True,
        queryset=SessionTemplate.objects.none(),  # this needs to be set at runtime
        help_text='The Session Template to use to defines resources when creating new Sessions in this group.'
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['max_sessions'] is not None and (
                cleaned_data['max_concurrent'] is None
                or cleaned_data['max_concurrent'] > cleaned_data['max_sessions']):
            self.add_error('max_concurrent',
                           "The maximum number of concurrent sessions must be less than the maximum number of total "
                           "sessions.")

        return cleaned_data


class SessionTemplateForm(forms.ModelForm):
    class Meta:
        model = SessionTemplate
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

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['lifetime'] is not None and (
                cleaned_data['timeout'] is None
                or cleaned_data['timeout'] > cleaned_data['lifetime']):
            self.add_error('timeout', 'The idle timeout must be less that the maximum lifetime of the Session.')
        return cleaned_data
