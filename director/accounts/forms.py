from crispy_forms.helper import FormHelper
from django import forms

from accounts.models import Team


class TeamForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Team
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput
        }
