from django.contrib.auth.models import User
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        '''
        This hook intercepts a SocialLogin instance before the login is done to
        check that the user does not already have a third party account
        connected to their Stencila user account with the same email.
        See http://stackoverflow.com/a/19443127.
        It does not do connection automatically since that can be insecure
        see http://stackoverflow.com/a/13896207
        '''
        duplicate = False
        for email in sociallogin.email_addresses:
            try:
                User.objects.get(email=email)
            except User.DoesNotExist:
                pass
            else:
                duplicate = True
                break
        if duplicate:
            raise Exception('A user with this email has already been registered. Are you trying to login with a different third party account?')
