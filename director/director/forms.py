from django import forms
import allauth.account.forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Project
from .storer.hub import HubStorer
hubstorer = HubStorer()

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

class CreateProjectForm(forms.ModelForm):
    name = forms.SlugField(max_length=255)
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(CreateProjectForm, self).__init__(*args, **kwargs)

    def is_valid(self, *args, **kwargs):
        valid = super(CreateProjectForm, self).is_valid()

        self.project_address = hubstorer.address(self.user, self.cleaned_data['name'])

        if Project.objects.filter(address=self.project_address).count() == 0:
            return True

        self._errors['name'] = ['You already have a project with this name']
        return False

    class Meta:
        model = Project
        fields = []
