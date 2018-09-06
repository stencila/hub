from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from accounts.models import Account, Team
from lib.forms import FormWithSubmit, ModelFormWithSubmit


class AccountSettingsForm(forms.ModelForm):
    helper = FormHelper()
    helper.layout = Layout(
        'name',
        'logo',
        Submit('submit', 'Update', css_class="button is-primary")
    )

    class Meta:
        model = Account
        fields = ('name', 'logo')
        widgets = {
            'name': forms.TextInput
        }


class AccountCreateForm(FormWithSubmit):
        class Meta:
            model = Account
            fields = ['name']
            widgets = {
                'name': forms.TextInput()
            }

        def __init__(self, *args, **kwargs):
    #        request = kwargs.pop('request')
            super().__init__(*args, **kwargs)

        #    accounts = Account.objects.filter(user_roles__user=request.user)
        #    self.fields['account'].queryset = accounts


class TeamForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Team
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput
        }
