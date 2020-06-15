from django import forms

from accounts.models import Account


class AccountImageForm(forms.ModelForm):
    """Form for updating an account's image."""

    class Meta:
        model = Account
        fields = ["image"]
