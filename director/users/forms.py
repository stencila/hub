from django import forms

from lib.forms import FormWithSubmit


class BetaTokenForm(FormWithSubmit):
    token = forms.CharField(widget=forms.PasswordInput())
