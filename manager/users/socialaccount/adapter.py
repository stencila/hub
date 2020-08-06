import requests
from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


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
