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
