from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from accounts.models import Account, Team
from lib.data_cleaning import clean_slug, SlugType
from lib.forms import ModelFormWithCreate


class CleanSlugMixin:
    def clean_slug(self):
        return clean_slug(self.cleaned_data['slug'], SlugType.ACCOUNT)


class AccountSettingsForm(CleanSlugMixin, forms.ModelForm):
    helper = FormHelper()
    helper.layout = Layout(
        'name',
        'logo',
        'slug',
        Submit('submit', 'Update', css_class="button is-primary")
    )

    class Meta:
        model = Account
        fields = ('name', 'logo', 'slug')
        widgets = {
            'name': forms.TextInput,
        }

    def clean_slug(self):
        return clean_slug(self.cleaned_data['slug'], SlugType.ACCOUNT)


class AccountCreateForm(ModelFormWithCreate):
    helper = FormHelper()
    helper.layout = Layout(
        'name',
        'logo',
        'slug'
    )

    class Meta:
        model = Account
        fields = ('name', 'logo', 'slug')
        widgets = {
            'name': forms.TextInput,
        }


class TeamForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Team
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput
        }
