from django import forms


class BetaTokenForm(forms.Form):
    token = forms.CharField(widget=forms.PasswordInput())
