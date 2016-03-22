#  This file is part of Stencila Hub.
#  
#  Copyright (C) 2015-2016 Stencila Ltd.
#  
#  Stencila Hub is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#  
#  Stencila Hub is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public License
#  along with Stencila Hub.  If not, see <http://www.gnu.org/licenses/>.

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
