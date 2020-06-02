import requests
from allauth.account.models import EmailAddress
from allauth.account.signals import user_logged_in
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


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


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Override the default adapter from socialaccount.

    See https://github.com/pennersr/django-allauth/issues/418#issuecomment-107880925
    """

    def pre_social_login(self, request, sociallogin):
        """
        Attempt to connect a social login to an existing user account.

        When a new social login has a verified email address that
        matches a verified email address already in the database, link
        the new social account to the existing user instead of creating
        a new user.
        """
        if sociallogin.is_existing:
            return

        if not sociallogin.email_addresses:
            return

        self.add_secondary_emails(sociallogin)

        def primary_first(email):
            return 1 - int(email.primary)

        for email in sorted(sociallogin.email_addresses, key=primary_first):
            if not email.verified:
                continue
            try:
                existing_email = EmailAddress.objects.get(
                    email__iexact=email.email, verified=True
                )
                # Mark this sociallogin as automatically connected, so
                # that the login signal knows to look for new email
                # addresses.
                sociallogin.autoconnect = True
                sociallogin.connect(request, existing_email.user)
                break
            except EmailAddress.DoesNotExist:
                continue

    def add_secondary_emails(self, sociallogin):
        """
        Add any secondary emails.

        Allauth's github provider currently only has a primary email, but
        we would like secondary emails too, so add an extra request to the
        gihub api for all user emails. It could be cleaner to override
        GitHubProvider's extract_email_addresses function, but here we can
        restrict the extra request to the first login instead of every
        login.
        """
        if len(sociallogin.email_addresses) != 1:
            return

        if sociallogin.account.provider != "github":
            return

        response = requests.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": "token {}".format(sociallogin.token.token)},
        )

        if response.status_code != 200:
            # No access to user/emails, but assume the primary address
            # is verified, because github requires email verification
            # before allowing authorization of oauth apps.
            # https://help.github.com/en/github/authenticating-to-github/authorizing-oauth-apps
            sociallogin.email_addresses[0].verified = True
            return

        all_emails = response.json()

        if all_emails:
            email_addresses = []

            for email in all_emails:
                email_addresses.append(
                    EmailAddress(
                        email=email.get("email"),
                        verified=email.get("verified"),
                        primary=email.get("primary"),
                    )
                )

            sociallogin.email_addresses = email_addresses
