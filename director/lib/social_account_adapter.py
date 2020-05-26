from allauth.account.models import EmailAddress
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

# Override the default adapter from socialaccount. See
# https://github.com/pennersr/django-allauth/issues/418#issuecomment-107880925


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # When a new social login has a verified email address that
        # matches a verified email address already in the database, link
        # the new social account to the existing user instead of creating
        # a new user.

        if sociallogin.is_existing:
            return

        if not sociallogin.email_addresses:
            return

        for email in sociallogin.email_addresses:
            if not email.verified:
                continue
            try:
                existing_email = EmailAddress.objects.get(
                    email__iexact=email.email, verified=True
                )
                sociallogin.connect(request, existing_email.user)
                break
            except EmailAddress.DoesNotExist:
                continue
