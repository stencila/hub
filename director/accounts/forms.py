from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms

from accounts.models import Account, Team
from lib.data_cleaning import clean_slug, SlugType
from lib.forms import ModelFormWithCreate


class CleanNameMixin:
    def clean_name(self):
        return clean_slug(self.cleaned_data["name"], SlugType.ACCOUNT)


class AccountSettingsForm(CleanNameMixin, forms.ModelForm):
    helper = FormHelper()
    helper.layout = Layout(
        "name", "logo", Submit("submit", "Update", css_class="button is-primary")
    )

    class Meta:
        model = Account
        fields = ("name", "logo")


class AccountCreateForm(CleanNameMixin, ModelFormWithCreate):
    helper = FormHelper()
    helper.layout = Layout("name", "logo",)

    class Meta:
        model = Account
        fields = ("name", "logo")


class TeamForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Team
        fields = ("name", "description")
        widgets = {"name": forms.TextInput}
