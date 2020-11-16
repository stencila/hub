from allauth.account.models import EmailAddress
from allauth.account.signals import user_logged_in, user_logged_out
from allauth.socialaccount.signals import social_account_added, social_account_updated


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
        response.set_cookie(
            "auth_provider",
            kwargs["sociallogin"].account.provider,
            max_age=315360000,  # Ten years in seconds.
            secure=True,
            httponly=True,
        )


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
    sociallogin = kwargs.get("sociallogin")
    if not sociallogin:
        return

    if not getattr(sociallogin, "autoconnect", False):
        return

    for email in sociallogin.email_addresses:
        try:
            existing = EmailAddress.objects.get(email__iexact=email.email.lower())
        except EmailAddress.DoesNotExist:
            EmailAddress.objects.create(
                email=email.email, verified=email.verified, primary=False, user=user
            )
            continue

        if existing.user != user:
            # TODO: what if this email is verified but the existing
            # email is unverified? Can this user steal it?
            continue
        elif email.verified and not existing.verified:
            existing.verified = True
            existing.save()


user_logged_in.connect(add_new_emails)


def update_data_from_provider(sender, request, sociallogin, **kwargs):
    """
    Set the user's personal account image (if necessary) from the social account.
    """
    import accounts.tasks
    import projects.tasks

    user = sociallogin.user
    provider = sociallogin.account.provider

    accounts.tasks.set_image_from_socialaccount(
        account_id=user.personal_account.id, provider=provider,
    )

    if provider == "github":
        projects.tasks.update_github_repos_for_user(user_id=user.id)


social_account_added.connect(update_data_from_provider)
social_account_updated.connect(update_data_from_provider)
