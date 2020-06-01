from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms
from django.contrib.auth.validators import UnicodeUsernameValidator


class SignupForm(AllauthSignupForm):
    """Form for users to sign up."""

    termsconditions = forms.BooleanField(
        label="I have read and agree to the Terms and Conditions",
        required=True,
        help_text='Please read and agree to our <a href="https://policies.stenci.la/terms">Terms and Conditions</a>',
    )


class UsernameForm(forms.Form):
    """Form for changing a user's username."""

    username = forms.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
        help_text="Enter a new username.",
    )
