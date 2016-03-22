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

from django.test import TestCase
from django.core.exceptions import PermissionDenied

from users.models import User, UserToken


class UserTokenTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='secret')
        self.user2 = User.objects.create_user(username='user2', password='secret')

    def test_token(self):
        '''
        Do token issuing, encoding/decoding work as expected?
        '''
        token = UserToken.objects.create(
            version='01',
            user=self.user1
        )
        self.assertEqual(token.version, token.string[:2])
        self.assertTrue(len(token.string) > 0)

        string, version, expires, user = UserToken.decode(token.string)
        self.assertEqual(version, token.version)
        self.assertEqual(user, token.user.id)

        user = UserToken.authenticate(token.string)
        self.assertEqual(user, token.user)
        self.assertEqual(user, self.user1)

        with self.assertRaises(PermissionDenied):
            UserToken.authenticate('01-some-bogus-token')

    def test_sessions_token(self):
        token1 = UserToken.get_sessions_token(self.user1)
        token2 = UserToken.get_sessions_token(self.user1)

        self.assertEqual(token1, token2)
        self.assertEqual(token1.user, self.user1)
        self.assertEqual(token1.name, "Sessions token")
        self.assertEqual(token1.notes, 'Token used by Stencila when launching sessions on your behalf')
