from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset
from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator

from lib.forms import FormWithSubmit


class UsernameForm(FormWithSubmit):
    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        help_text='Enter your new username. It must not be in use by anyone else.')


class UserSignupForm(SignupForm):
    termsconditions = forms.BooleanField(
        label="I have read and agree to the Terms and Conditions",
        required=True,
        help_text='Please read and agree to Stencila Hub <a href="http://hub.stenci.la/about/terms-and-conditions/">'
                  'Terms and Conditions</a>'
    )

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'email',
                'username',
                'password',
                'termsconditions'
            )
        )
