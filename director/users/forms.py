from allauth.account.forms import SignupForm
from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator

from lib.forms import FormWithSubmit


class BetaTokenForm(FormWithSubmit):
    token = forms.CharField(widget=forms.PasswordInput())


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
