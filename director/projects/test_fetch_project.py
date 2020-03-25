from django.contrib.auth.models import User
from django.test import TestCase

from accounts.models import Account, AccountRole, AccountUserRole
from projects.permission_facade import fetch_project_for_user
from projects.permission_models import ProjectPermissionType
from projects.project_models import Project


class TestFetchProjectForUser(TestCase):
    def setUp(self):
        """
        Create Account, Projects and Users for testing.

        user1 is creator of project1, user2 is the creator of project2. admin created neither but is the admin of the
        account. All users and projects are in this same account.
        """
        self.user1 = User.objects.create(username='user1')
        self.user2 = User.objects.create(username='user2')
        self.admin = User.objects.create(username='admin')
        account = Account.objects.create(name='account')
        account2 = Account.objects.create(name='account2')

        self.project1 = Project.objects.create(account=account, creator=self.user1, name='project1')
        self.project2 = Project.objects.create(account=account, creator=self.user2, name='project2')
        self.project3 = Project.objects.create(account=account2, creator=self.user1, name='project3')

        account_member_role = AccountRole.objects.get(name='Account member')
        account_admin_role = AccountRole.objects.get(name='Account admin')

        AccountUserRole.objects.create(user=self.user1, account=account, role=account_member_role)
        AccountUserRole.objects.create(user=self.user2, account=account, role=account_member_role)
        AccountUserRole.objects.create(user=self.admin, account=account, role=account_admin_role)

    def test_member_project_fetch(self):
        """Test that normal users can only fetch projects that they have specific project access to."""
        fetch_result_1_allowed = fetch_project_for_user(self.user1, account_name='account', project_name='project1')
        self.assertIn(ProjectPermissionType.OWN, fetch_result_1_allowed.agent_permissions)

        fetch_result_1_disallowed = fetch_project_for_user(self.user1, account_name='account', project_name='project2')
        self.assertEqual(fetch_result_1_disallowed.agent_permissions, set())

    def test_admin_project_fetch(self):
        """An admin should have OWN permissions on any project in their account."""
        admin_allowed_1 = fetch_project_for_user(self.admin, account_name='account', project_name='project1')

        self.assertIn(ProjectPermissionType.OWN, admin_allowed_1.agent_permissions)

        admin_allowed_2 = fetch_project_for_user(self.admin, account_name='account', project_name='project2')
        self.assertIn(ProjectPermissionType.OWN, admin_allowed_2.agent_permissions)

        admin_disallowed_1 = fetch_project_for_user(self.admin, account_name='account2', project_name='project3')
        self.assertEqual(admin_disallowed_1.agent_permissions, set())
