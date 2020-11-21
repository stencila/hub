from django.core.cache import cache
from rest_framework import status

from accounts.models import AccountTier
from dois.models import Doi
from manager.testing import DatabaseTestCase
from projects.models.nodes import Node
from projects.models.projects import Project


class DoisViewsTest(DatabaseTestCase):
    """Test creating and retrieving DOIs."""

    def test_create(self):
        # Allow one DOI to be created for Ada's account
        AccountTier.objects.update(dois_created_month=1)
        cache.delete("account-tier-1")

        node = Node.objects.create(
            json={"type": "Article"},
            project=Project.objects.create(account=self.ada.personal_account),
        )

        response = self.create(self.ada, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == status.HTTP_201_CREATED

        response = self.create(self.ada, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == 402
        assert (
            response.data["errors"][0]["message"]
            == "The number of DOIs created has been exceeded. Please upgrade the plan for the account."
        )

        response = self.create(self.bob, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == 403
        assert (
            response.data["message"]
            == "You need to be the project manager or owner to create a DOI for it."
        )

        node = Node.objects.create(json={"type": "foo"})
        response = self.create(self.ada, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["errors"][0]["message"]
            == "Node type must be one of Article, Review."
        )

        node = Node.objects.create(json={"type": "Article"})
        response = self.create(self.ada, "api-dois-list", data=dict(node=node.id))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            response.data["errors"][0]["message"] == "Node must be linked to a project."
        )

    def test_list(self):
        response = self.list(None, "api-dois-list")
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve(self):
        node = Node.objects.create(json={"type": "Article"})
        Doi.objects.create(node=node)

        response = self.retrieve(None, "api-dois-detail", kwargs={"doi": 1})
        assert response.status_code == status.HTTP_200_OK
