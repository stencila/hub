from unittest import mock

from manager.testing import DatabaseTestCase
from users.tasks import update_services_all_users, update_services_for_user


class UserTasksTests(DatabaseTestCase):
    @mock.patch("httpx.post")
    def test_update_services_all_users(self, httpx_post):
        # Just checks that the query for users does not fail
        update_services_all_users()

    @mock.patch("django.conf.settings.USERFLOW_API_KEY", "userflow_key")
    @mock.patch("httpx.post")
    def test_update_userflow(self, httpx_post):
        json = {
            "id": 1,
            "attributes": {
                "username": "ada",
                "first_name": mock.ANY,
                "last_name": mock.ANY,
                "display_name": mock.ANY,
                "location": mock.ANY,
                "image": mock.ANY,
                "website": mock.ANY,
                "public_email": mock.ANY,
                "date_joined": mock.ANY,
                "last_login": mock.ANY,
                "personal_account_id": mock.ANY,
                "personal_account_tier": mock.ANY,
                "orgs_summary_max_tier": mock.ANY,
                "orgs_summary_total": mock.ANY,
                "orgs_summary_member": mock.ANY,
                "orgs_summary_manager": mock.ANY,
                "orgs_summary_owner": mock.ANY,
                "projects_summary_total": mock.ANY,
                "projects_summary_reader": mock.ANY,
                "projects_summary_reviewer": mock.ANY,
                "projects_summary_editor": mock.ANY,
                "projects_summary_author": mock.ANY,
                "projects_summary_manager": mock.ANY,
                "projects_summary_owner": mock.ANY,
                "name": "ada",
                "email": mock.ANY,
            },
        }
        headers = {
            "Authorization": "Bearer userflow_key",
            "UserFlow-Version": "2020-01-03",
        }

        # Called with a user object
        update_services_for_user(self.ada, services=["userflow"])
        httpx_post.assert_called_with(
            "https://api.getuserflow.com/users", json=json, headers=headers,
        )

        # Called with an `int` instead
        update_services_for_user(self.ada.id, services=["userflow"])
        httpx_post.assert_called_with(
            "https://api.getuserflow.com/users", json=json, headers=headers,
        )
