from unittest import mock

from manager.testing import DatabaseTestCase
from users.tasks import update_services_for_user


class UserTasksTests(DatabaseTestCase):
    @mock.patch("django.conf.settings.USERFLOW_KEY", "userflow_key")
    @mock.patch("httpx.post")
    def test_update_userflow(self, httpx_post):
        update_services_for_user(self.ada, services=["userflow"])
        httpx_post.assert_called_with(
            "https:/api.getuserflow.com/users",
            data={
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
            },
            headers={
                "Authorization": "Bearer userflow_key",
                "UserFlow-Version": "2020-01-03",
            },
        )
