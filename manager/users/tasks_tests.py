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
        data = {
            "id": 1,
            "attributes": {
                "username": "ada",
                "first_name": "",
                "last_name": "",
                "display_name": "",
                "location": None,
                "image": None,
                "website": None,
                "public_email": None,
                "date_joined": mock.ANY,
                "last_login": None,
                "personal_account_id": 3,
                "personal_account_tier": 1,
                "orgs_summary_max_tier": None,
                "orgs_summary_total": 0,
                "orgs_summary_member": 0,
                "orgs_summary_manager": 0,
                "orgs_summary_owner": 0,
                "projects_summary_total": 2,
                "projects_summary_reader": 0,
                "projects_summary_reviewer": 0,
                "projects_summary_editor": 0,
                "projects_summary_author": 0,
                "projects_summary_manager": 0,
                "projects_summary_owner": 2,
            },
        }
        headers = {
            "Authorization": "Bearer userflow_key",
            "UserFlow-Version": "2020-01-03",
        }

        # Called with a user object
        update_services_for_user(self.ada, services=["userflow"])
        httpx_post.assert_called_with(
            "https:/api.getuserflow.com/users", data=data, headers=headers,
        )

        # Called with an `int` instead
        update_services_for_user(self.ada.id, services=["userflow"])
        httpx_post.assert_called_with(
            "https:/api.getuserflow.com/users", data=data, headers=headers,
        )
