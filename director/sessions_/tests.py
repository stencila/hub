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

import unittest
import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from sessions.models import Worker, Session
from users.models import User, UserToken


class VirtualBoxWorkerTestCase(TestCase):
    '''
    Test a VirtualBox worker
    '''

    @classmethod
    def setUpClass(cls):
        # Class member so only one instance used in
        # tests below
        cls.worker = Worker(
            platform='vbox'
        )

    # Naming of tests to ensure a particular
    # order

    def test_01_launch(self):
        self.worker.launch()

        self.assertEqual(self.worker.platform_id, "vbox-on-localhost")
        self.assertEqual(self.worker.ip, "192.168.43.43")
        self.assertEqual(self.worker.port, 7654)
        self.assertTrue(self.worker.started > timezone.now()-datetime.timedelta(seconds=1))

    def test_02_update(self):
        self.worker.update()

        self.assertTrue(self.worker.updated > timezone.now()-datetime.timedelta(seconds=1))
        self.assertTrue(self.worker.active)
        self.assertEqual(len(self.worker.infos.all()), 1)

    @unittest.skip("Skipping terminate() while tests in development")
    def test_03_terminate(self):
        self.worker.terminate()

        self.assertTrue(self.worker.stopped > timezone.now()-datetime.timedelta(seconds=1))
        self.assertFalse(self.active)


@unittest.skip("Skipping EC2 Worker test. Comment out this line to run.")
class EC2WorkerTestCase(TestCase):
    '''
    Test a EC2 worker
    '''

    @classmethod
    def setUpClass(cls):
        # Class member so only one instance used in
        # tests below
        cls.worker = Worker(
            platform='ec2'
        )

    # Naming of tests to ensure a particular
    # order

    def test_01_launch(self):
        self.worker.launch()

    def test_02_update(self):
        self.worker.update()

    def test_03_terminate(self):
        self.worker.terminate()


class SessionTestCase(TestCase):
    '''
    Test sessions
    '''

    @classmethod
    def setUpClass(cls):
        # A worker is created here so that it
        # is in the test database and available for
        # launching a session
        cls.worker = Worker.objects.create(
            platform='vbox'
        )
        cls.worker.launch()
        # Some users for testing authorization
        cls.user1 = User.objects.create_user(username='user1', password='secret')
        cls.user2 = User.objects.create_user(username='user2', password='secret')
        # A stencil to launch a session for
        cls.stencil = Component(address='a', type='stencil')
        # Start a session for them
        cls.session = Session_.launch(
            component=cls.stencil,
            user=cls.user1,
        )

    @classmethod
    def tearDownClass(cls):
        cls.session.stop()

    def test_start(self):
        '''
        Has the session started properly?
        '''
        self.assertEqual(self.session.component, self.stencil)
        self.assertEqual(self.session.user, self.user1)

        token = UserToken.get_sessions_token(self.user1)
        self.assertEqual(self.session.token, token.string)

        self.assertEqual(self.session.memory, '1g')
        self.assertEqual(self.session.cpu, 1024)

        self.assertEqual(self.session.worker, self.worker)
        self.assertTrue(self.session.uuid is not None)
        self.assertEqual(self.session.status, 'Starting')
        self.assertTrue(self.session.started > timezone.now()-datetime.timedelta(seconds=1))

    def test_update(self):
        self.session.update()

        self.assertTrue(self.session.active)
        self.assertTrue(self.session.started > timezone.now()-datetime.timedelta(seconds=10))
        self.assertTrue(self.session.port > 10000)
        self.assertEqual(self.session.status[:2], 'Up')
        self.assertTrue(self.session.updated > timezone.now()-datetime.timedelta(seconds=1))

    def test_stats(self):
        self.session.stats()

    def test_authorization(self):
        # By default on the session owner has access
        self.assertTrue(self.session.authorize(self.user1))
        self.assertFalse(self.session.authorize(self.user2))

        # Users can be invited
        self.session.invite(self.user1, self.user2)
        self.assertTrue(self.session.authorize(self.user2))

        # Users can be uninvited
        self.session.uninvite(self.user1, self.user2)
        self.assertFalse(self.session.authorize(self.user2))

        # Another user can't invite themselves
        with self.assertRaises(PermissionDenied):
            self.session.invite(self.user2, self.user2)
