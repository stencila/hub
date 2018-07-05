from django import forms
import allauth.account.forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Project

class UserSignupForm(allauth.account.forms.SignupForm):

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Sign me up!', css_class='button is-primary'), )


class UserSigninForm(allauth.account.forms.LoginForm):

    def __init__(self, *args, **kwargs):
        super(UserSigninForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Sign me in!', css_class='button is-primary'))

class ProjectUploadForm(forms.ModelForm):
    upload = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = Project
        fields = []

class ProjectRenameForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name',)

class BetaTokenForm(forms.Form):
    token = forms.CharField()
