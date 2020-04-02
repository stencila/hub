"""
SHOULD NOT BE RUN ON PRODUCTION ENVIRONMENT
Replace users' emails with an anonymized version so they don't receive emails from the staging environment.
"""
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User


CONFIRMATION_PHRASE = (
    "testenvironmentonly"  # extra step to prevent this being run inadvertently
)


def anonymize_email(email):
    return email.replace("@", ".") + "@example.com"


def run(*args):
    if len(args) != 1 or args[0] != CONFIRMATION_PHRASE:
        raise ValueError(
            "This script must be run with the correct confirmation phrase."
        )

    for email_address in EmailAddress.objects.all():
        email_address.email = anonymize_email(email_address.email)
        email_address.save()

    for user in User.objects.all():
        user.email = anonymize_email(user.email)
        user.save()
