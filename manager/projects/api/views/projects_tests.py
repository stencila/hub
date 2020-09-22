from rest_framework import status

from manager.testing import DatabaseTestCase


class ProjectsViewsTest(DatabaseTestCase):
    """Test projects CRUD using API."""

    def test_create(self):
        """
        Test creating a project
        """
        response = self.create(
            self.ada, "projects", {"account": self.ada.personal_account.id}
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_list(self):
        """
        Test listing projects with various filters
        """

        # Create projects with different values for the fields
        # that we can filter them on.
        for user, name, public, roles, sources in [
            (self.ada, "apple", True, [], []),
            (self.ada, "banana", False, [(self.bob, "AUTHOR")], []),
            (
                self.bob,
                "cherry",
                False,
                [],
                [
                    {
                        "type": "GoogleDocsSource",
                        "doc_id": "1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA",
                        "path": "report.gdoc",
                    }
                ],
            ),
        ]:
            response = self.create(
                user,
                "api-projects-list",
                {"account": user.personal_account.id, "name": name, "public": public},
            )
            assert response.status_code == status.HTTP_201_CREATED
            project = response.data

            for other_user, role in roles:
                response = self.create(
                    user,
                    "api-projects-agents-list",
                    {"type": "user", "agent": other_user.id, "role": role},
                    kwargs={"project": project["id"]},
                )
                assert response.status_code == status.HTTP_201_CREATED

            for source in sources:
                response = self.create(
                    user,
                    "api-projects-sources-list",
                    source,
                    kwargs={"project": project["id"]},
                )
                assert response.status_code == status.HTTP_201_CREATED

        # Different users will get different numbers of project

        response = self.list(None, "projects")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3 + 1

        response = self.list(self.ada, "projects")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3 + 1 + 2

        # Search in name, title, description

        response = self.list(self.ada, "projects", {"search": "appl"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "apple"

        # Filter by role

        response = self.list(self.bob, "projects", {"role": "member"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2 + 2

        response = self.list(self.bob, "projects", {"role": "author"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        response = self.list(self.bob, "projects", {"role": "editor"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

        # Filter by source

        response = self.list(
            self.bob,
            "projects",
            {"source": "gdoc://1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        response = self.list(
            self.bob, "projects", {"source": "gdoc://1BW6MubIyDirCGW9Wq-doesnotexist"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

        response = self.list(self.bob, "projects", {"source": "gdoc://invalid-id"})
        assert response.status_code == 400
        assert response.data["errors"] == [
            {
                "field": "source",
                "message": 'Unable to parse source address "gdoc://invalid-id"',
            }
        ]

        response = self.list(
            self.ada,
            "projects",
            {"source": "gdoc://1BW6MubIyDirCGW9Wq-tSqCma8pioxBI6VpeLyXn5mZA"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
