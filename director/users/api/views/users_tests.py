from rest_framework import status

from general.testing import DatabaseTestCase


class UserAPIViewsTests(DatabaseTestCase):
    """Test that the various user API endpoints work."""

    # Type specific API requests

    def list_users(self, user, data={}):
        return self.list(user, "users", data=data)

    def retrieve_user(self, user, pk: int):
        return self.retrieve(user, "users", kwargs={"pk": pk})

    def retrieve_me(self, user):
        return self.retrieve(user, "api-users-retrieve-me")

    # Testing methods

    def test_list(self):
        anon = self.list_users(None)
        assert anon.status_code == status.HTTP_200_OK
        assert len(anon.data["results"]) > 0

        authed = self.list_users(self.ada)
        assert authed.data == anon.data

        searched = self.list_users(None, data={"q": "cam"})
        users = searched.data["results"]
        assert len(users) == 1
        assert users[0]["username"] == "cam"

    def test_retrieve_user(self):
        response = self.retrieve_user(None, 2)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "bob"

    def test_retrieve_me(self):
        response = self.retrieve_me(None)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert (
            response.data["message"] == "Authentication credentials were not provided."
        )

        response = self.retrieve_me(self.ada)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "ada"
