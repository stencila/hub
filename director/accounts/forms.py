from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Submit
from django import forms

from accounts.models import Account, Team
from lib.data_cleaning import clean_slug, SlugType
from lib.forms import ModelFormWithCreate
from assets.thema import themes


class CleanNameMixin:
    def clean_name(self):
        return clean_slug(self.cleaned_data["name"], SlugType.ACCOUNT)


class AccountCreateForm(CleanNameMixin, ModelFormWithCreate):
    helper = FormHelper()
    helper.layout = Layout("name", "logo",)

    class Meta:
        model = Account
        fields = ("name", "logo")


class AccountSettingsForm(CleanNameMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AccountSettingsForm, self).__init__(*args, **kwargs)
        instance = kwargs["instance"]

        self.helper = FormHelper(self)
        self.helper.layout = Layout()

        if not instance.is_personal:
            self.helper.layout.append(
                Div(
                    HTML(
                        '<p class="title is-4">Identity</p>'
                        '<p class="subtitle is-5">Settings for your organisation\'s public profile.</p>'
                    ),
                    "name",
                    "logo",
                    css_class="mb-12",
                )
            )
        else:
            del self.fields["name"]
            del self.fields["logo"]

        self.helper.layout.append(
            Div(
                Div(
                    HTML(
                        '<p class="title is-4">Content</p>'
                        '<p class="subtitle is-5">Settings affecting how content is served for your projects.</p>'
                    ),
                    "theme",
                    "hosts",
                    css_class="",
                ),
                Submit("submit", "Update", css_class="mt-4 button is-primary"),
            )
        )

    class Meta:
        model = Account
        fields = ("name", "logo", "theme", "hosts")
        widgets = {
            "theme": forms.Select(
                choices=[(None, "")] + [(theme, theme) for theme in themes]
            ),
            "hosts": forms.TextInput(),
        }


class TeamForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_tag = False

    class Meta:
        model = Team
        fields = ("name", "description")
        widgets = {"name": forms.TextInput}
