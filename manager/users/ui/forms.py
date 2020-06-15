from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator


class SignupForm(AllauthSignupForm):
    """Form for users to sign up."""

    termsconditions = forms.BooleanField(
        label='I have read and agree to the <a href="https://policies.stenci.la/terms">terms and conditions</a>',
        required=True,
        help_text='Please read and agree to our Terms and Conditions',
    )


class UsernameForm(forms.Form):
    """Form for changing a user's username."""

    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        help_text="Enter a new username.",
    )
