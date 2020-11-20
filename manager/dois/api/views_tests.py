from rest_framework import status

from dois.models import Doi
from manager.testing import DatabaseTestCase
from projects.models.nodes import Node


class DoisViewsTest(DatabaseTestCase):
    """Test creating and retrieving DOIs."""

    def test_create_ok(self):
        node = Node.objects.create(json={"type": "Article"})
        response = self.create(self.ada, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_fail(self):
        node = Node.objects.create(json={"type": "foo"})
        response = self.create(self.ada, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["errors"][0]["message"]
            == "Node type must be one of Article, Review"
        )

    def test_list(self):
        response = self.list(None, "api-dois-list")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve(self):
        node = Node.objects.create(json={"type": "Article"})
        Doi.objects.create(node=node)

        response = self.retrieve(None, "api-dois-detail", kwargs={"doi": 1})
        assert response.status_code == status.HTTP_200_OK
