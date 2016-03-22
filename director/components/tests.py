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

from django.test import TestCase, Client

from accounts.models import Account, AccountType
from users.models import User, AnonymousUser
from components.models import Address, Component, READ, UPDATE, DELETE


class UrlsTestCase(TestCase):

    def test_url(self):
        self.assertEqual(Component(
            address='a/b/c',
            title=None
        ).url, '/a/b/c/')

        self.assertEqual(Component(
            address='a/b/c',
            title='The title'
        ).url, '/a/b/c/the-title-')

    def test_slug(self):
        self.assertEqual(Component().slug, '')
        self.assertEqual(Component(title='hello world').slug, 'hello-world')
        self.assertEqual(Component(
            title='A sentence with a full stop.').slug, 'a-sentence-with-a-full-stop')
        self.assertEqual(Component(
            title='Lots of punctuation: `~!@#$%^&*()_+{}[]:;"<>,./?').slug,
            'lots-of-punctuation-_'
        )

    def test_tiny(self):
        id = 1000
        alphanum = 'QI'
        self.assertEqual(Component.tiny_convert(id), alphanum)
        self.assertEqual(Component.tiny_convert(alphanum), id)

        com = Component(id=id)
        self.assertEqual(com.tiny_url, 'https://stenci.la/%s~' % alphanum)


class AuthorizeTestCase(TestCase):

    def setUp(self):
        self.user_1 = User.objects.create_user(username='user_1')
        self.user_2 = User.objects.create_user(username='user_2')

        self.account_a = Account.objects.create(
            name='account_a',
            type=AccountType.get('bronze')
        )
        self.account_a.address_add('a')

        self.account_b = Account.objects.create(
            name='account_b',
            type=AccountType.get('bronze')
        )
        self.account_b.address_add('b')

    def test_default(self):
        c = Component.objects.create(
            address='b',
        )

        self.assertFalse(c.authorize(AnonymousUser(), READ))
        self.assertFalse(c.authorize(self.user_1, READ))
        self.assertFalse(c.authorize(self.user_1, UPDATE))
        self.assertFalse(c.authorize(self.user_1, DELETE))

    def test_key_read(self):
        key = self.account_a.keys.create(address='a', action=READ)
        key.users = [self.user_1]
        c = Component.objects.create(
            address='a',
        )

        self.assertTrue(c.authorize(self.user_1, READ))
        self.assertFalse(c.authorize(self.user_2, READ))
        self.assertFalse(c.authorize(AnonymousUser(), READ))
        self.assertFalse(c.authorize(self.user_1, UPDATE))
        self.assertFalse(c.authorize(self.user_1, DELETE))

    def test_key_read_public(self):
        self.account_a.addresses.update(public=True)
        c = Component.objects.create(
            address='a',
        )

        self.assertTrue(c.authorize(self.user_1, READ))
        self.assertTrue(c.authorize(self.user_2, READ))
        self.assertTrue(c.authorize(AnonymousUser(), READ))
        self.assertFalse(c.authorize(self.user_1, UPDATE))
        self.assertFalse(c.authorize(self.user_2, UPDATE))

    def test_key_read_address(self):
        key = self.account_a.keys.create(address='a/b/c', action=READ)
        key.users = [self.user_1]
        c = Component.objects.create(
            address='a/b/c'
        )

        self.assertTrue(c.authorize(self.user_1, READ))
        self.assertFalse(c.authorize(self.user_2, READ))
        self.assertFalse(c.authorize(AnonymousUser(), READ))
        self.assertFalse(c.authorize(self.user_1, UPDATE))
        self.assertFalse(c.authorize(self.user_1, DELETE))

    def test_key_update(self):
        key = self.account_a.keys.create(address='a/b/c', action=UPDATE)
        key.users = [self.user_1]
        c = Component.objects.create(
            address='a/b/c'
        )

        self.assertTrue(c.authorize(self.user_1, READ))
        self.assertTrue(c.authorize(self.user_1, UPDATE))
        self.assertFalse(c.authorize(self.user_1, DELETE))
        self.assertFalse(c.authorize(self.user_2, READ))
        self.assertFalse(c.authorize(self.user_2, UPDATE))
        self.assertFalse(c.authorize(AnonymousUser(), READ))

    def test_key_only_correct_types(self):
        key = self.account_a.keys.create(address='a', action=READ, type='unknown')
        key.users = [self.user_1]
        key = self.account_a.keys.create(address='a/b/c', action=UPDATE, type='different')
        key.users = [self.user_1]
        c = Component.objects.create(
            address='a/b/c'
        )

        self.assertTrue(c.authorize(self.user_1, READ))
        self.assertFalse(c.authorize(self.user_1, UPDATE))

        self.assertFalse(c.authorize(self.user_2, READ))
        self.assertFalse(c.authorize(self.user_2, UPDATE))

        self.assertFalse(c.authorize(AnonymousUser(), READ))


class ViewsTestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user_1 = User.objects.create_user(
            username='user_1', password='secret')
        self.user_2 = User.objects.create_user(
            username='user_2', password='secret')

        self.account = Account.objects.create(
            name='account_a',
            type=AccountType.get('bronze')
        )
        self.account.address_add('a', public=True)
        self.account.address_add('b')
        key = self.account.keys.create(address='b', action=READ)
        key.users = [self.user_1]

        self.com_a = Component.objects.create(
            address='a'
        )
        self.com_b = Component.objects.create(
            address='b'
        )

    def test_setup(self):
        self.assertTrue(self.com_a.authorize(self.user_1, READ))
        self.assertTrue(self.com_a.authorize(self.user_2, READ))
        self.assertFalse(self.com_a.authorize(self.user_1, UPDATE))
        self.assertFalse(self.com_a.authorize(self.user_2, UPDATE))

        self.assertTrue(self.com_b.authorize(self.user_1, READ))
        self.assertFalse(self.com_b.authorize(self.user_2, READ))

    def test_notfound(self):
        r = self.client.get('/foo.git/bar')
        self.assertEqual(r.status_code, 404)

        r = self.client.get('/foo/file.txt')
        self.assertEqual(r.status_code, 404)

        r = self.client.get('/foo/sub/dir/file.txt')
        self.assertEqual(r.status_code, 404)

    def test_read_public(self):
        r = self.client.get('/a.git?x=y')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r['X-Accel-Redirect'], '/internal-component-git/a/.git?x=y')

        r = self.client.get('/a.git/foo')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r['X-Accel-Redirect'], '/internal-component-git/a/.git/foo')

        r = self.client.get('/a/image.png')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r['X-Accel-Redirect'], '/internal-component-raw/a/image.png')

    def test_read_private(self):
        r = self.client.get('/b.git?x=y')
        self.assertEqual(r.status_code, 403)

        r = self.client.get('/b/file.txt')
        self.assertEqual(r.status_code, 403)

        loggedin = self.client.login(username='user_1', password='secret')
        self.assertTrue(loggedin)
        r = self.client.get('/b/file.txt')
        self.assertEqual(r.status_code, 200)

        loggedin = self.client.login(username='user_2', password='secret')
        self.assertTrue(loggedin)
        r = self.client.get('/b/file.txt')
        self.assertEqual(r.status_code, 403)

    def test_tiny_url(self):
        r = self.client.get(self.com_a.tiny_url)
        self.assertRedirects(
            r, self.com_a.url, status_code=301, fetch_redirect_response=False)
