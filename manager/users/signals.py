from allauth.account.models import EmailAddress
from allauth.account.signals import user_logged_in, user_logged_out


def clear_user_session_data(sender, request, user, **kwargs):
    """
    Clear the `user` session data (which is there for anon users too).

    In the future, we may link the `AnonUser` to the user. For example,
    for them to not loose objects created while anonymous.
    """
    if "user" in request.session:
        del request.session["user"]


user_logged_in.connect(clear_user_session_data)
user_logged_out.connect(clear_user_session_data)


def set_last_provider(sender, request, response, user, **kwargs):
    """
    Remember the last auth provider in the browser.

    The next time the login page is visited, this provider can be highlighted
    to encourage the user to use the same provider again.
    """
    if "sociallogin" in kwargs:
        response.set_cookie("auth_provider", kwargs["sociallogin"].account.provider)


user_logged_in.connect(set_last_provider)


def add_new_emails(sender, request, response, user, **kwargs):
    """
    Add new emails for a user.

    allauth won't automatically add email addresses from a newly connected
    social account unless it's creating a user. When we automatically link
    a new social account to an existing user by email matching, bring in
    email addresses from the new social account. This can improve email
    matching for users with multiple email addresses if another social
    account is added later. Delayed until after login to avoid triggering
    a call to SocialLogin.save on an existing socialaccount.
    """
    if "sociallogin" not in kwargs:
        return

    if not getattr(kwargs["sociallogin"], "autoconnect", False):
        return

    for e in kwargs["sociallogin"].email_addresses:
        try:
            existing = EmailAddress.objects.get(email__iexact=e.email.lower())
        except EmailAddress.DoesNotExist:
            new = EmailAddress(
                email=e.email, verified=e.verified, primary=False, user=user
            )
            new.save()
            continue

        if existing.user != user:
            # TODO: what if this email is verified but the existing
            # email is unverified? Can this user steal it?
            continue
        elif e.verified and not existing.verified:
            existing.verified = True
            existing.save()


user_logged_in.connect(add_new_emails)
