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

from accounts.models import Account, AccountType, READ, UPDATE, DELETE, CREATE, Address
from users.models import User


class KeysTestCase(TestCase):

    def setUp(self):
        self.account_a = Account.objects.create(
            name='account_a',
            type=AccountType.get('bronze')
        )
        self.account_b = Account.objects.create(
            name='account_b',
            type=AccountType.get('gold')
        )

        self.user_1 = User.objects.create(username='user_1')
        self.user_2 = User.objects.create(username='user_2')

    def test_default(self):
        self.account_a.key_add(
            users=[self.user_1],
            scopes=[(READ,)]
        )

        self.assertEqual(self.account_a.keys.count(), 1)
        self.assertEqual(self.account_a.keys.all()[0].scopes.count(), 1)
        self.assertEqual(self.account_b.keys.count(), 0)


class AddressTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='user_1')
        self.user_2 = User.objects.create_user(username='user_2')
        self.user_3 = User.objects.create_user(username='user_3')

        self.account_1 = Account.objects.create(
            name='account_1',
            type=AccountType.get('bronze')
        )
        self.account_1.owners.add(self.user_1)
        self.account_1.key_add(
            users=[self.user_3],
            scopes=[
                (READ, 'aaa'),
                (UPDATE, 'aaa/bbb'),
                (CREATE, None, 'session')
            ]
        )

        self.account_2 = Account.objects.create(
            name='account_2',
            type=AccountType.get('bronze')
        )
        self.account_2.owners.add(self.user_2)

        self.address_1 = Address.objects.create(
            address='aaa',
            account=self.account_1
        )
        self.address_2 = Address.objects.create(
            address='aaa/bbb',
            account=self.account_1,
            public=True
        )
        self.address_3 = Address.objects.create(
            address='bbb',
            account=self.account_2
        )

    def test_find(self):
        self.assertEqual(Address.find('aaa'), self.address_1)
        self.assertEqual(Address.find('aaa/ddd'), self.address_1)
        self.assertEqual(Address.find('aaa/bbb'), self.address_2)
        self.assertEqual(Address.find('foo'), None)

    def test_within(self):
        self.assertTrue(Address.within('a', 'a'))
        self.assertTrue(Address.within('a/aa', 'a'))
        self.assertFalse(Address.within('a', 'a/aa'))

        self.assertTrue(Address.within('foo/bar/noo', 'foo/bar/noo'))
        self.assertTrue(Address.within('foo/bar/noo', 'foo/bar'))
        self.assertTrue(Address.within('foo/bar/noo', 'foo'))
        self.assertFalse(Address.within('foo/bar/noo', 'food'))
        self.assertFalse(Address.within('foo/bar/noo', 'bar/foo'))
        self.assertFalse(Address.within('foo/bar/noo', 'bar'))

    def test_authorize(self):
        auth = Account.authorize

        # Address account owners can do anything
        self.assertTrue(auth(self.user_1, 'aaa'))
        self.assertTrue(auth(self.user_1, 'aaa', UPDATE))
        self.assertTrue(auth(self.user_1, 'aaa', DELETE))
        self.assertTrue(auth(self.user_1, 'aaa', CREATE))
        self.assertTrue(auth(self.user_1, self.account_1, CREATE, 'session'))
        # but others can't
        self.assertFalse(auth(self.user_2, 'aaa'))
        self.assertFalse(auth(self.user_2, 'aaa', UPDATE))
        self.assertFalse(auth(self.user_2, 'aaa', DELETE))
        self.assertFalse(auth(self.user_2, 'aaa', CREATE))
        # unless the address is public - then they can read
        self.assertTrue(auth(self.user_2, 'aaa/bbb'))
        self.assertFalse(auth(self.user_2, 'aaa/bbb', UPDATE))
        self.assertFalse(auth(self.user_2, 'aaa/bbb', DELETE))
        self.assertFalse(auth(self.user_2, 'aaa/bbb', CREATE))
        # or if they have a key
        self.assertTrue(auth(self.user_3, 'aaa/bbb'))
        self.assertTrue(auth(self.user_3, 'aaa/bbb', UPDATE))
        self.assertFalse(auth(self.user_3, 'aaa/bbb', DELETE))
        self.assertFalse(auth(self.user_3, 'aaa/bbb', CREATE))
        self.assertTrue(auth(self.user_3, self.account_1, CREATE, 'session'))
