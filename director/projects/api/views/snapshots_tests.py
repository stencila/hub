from typing import Optional
from unittest import mock

from django.http import HttpRequest
from django.utils import timezone
from rest_framework import status

from general.testing import DatabaseTestCase
from projects.models import Project, Snapshot


class MockProjectSnapshotter:
    def __init__(self, storage_root: str) -> None:
        pass

    def snapshot_project(
        self, request: HttpRequest, project: Project, tag: Optional[str] = None
    ) -> Snapshot:
        return Snapshot.objects.create(
            project=project,
            version_number=1,
            tag=tag or None,
            creator=request.user,
            created=timezone.now(),
            completed=timezone.now(),
        )


class SnapshotAPIViewsTest(DatabaseTestCase):
    """
    Test API views for snapshots.

    Tests for the `ProjectSnapshotter` should be done elsewhere.
    It is mocked in these tests.
    """

    def setUp(self):
        super().setUp()
        self.patcher = mock.patch(
            "projects.api.views.snapshots.ProjectSnapshotter",
            new=MockProjectSnapshotter,
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    # Type specific CRUD methods (no U & D methods though)

    def list_snaps(self, user, project: Project):
        return self.list(user, "snapshots", kwargs={"pk": project.pk})

    def create_snap(self, user, project: Project, tag: Optional[str] = None):
        return self.create(
            user, "snapshots", kwargs={"pk": project.pk}, data={"tag": tag}
        )

    def retrieve_snap(self, user, project: Project, number=None):
        return self.retrieve(
            user, "snapshots", kwargs={"pk": project.pk, "number": number}
        )

    # Testing methods

    def test_create_ok(self):
        response = self.create_snap(self.ada, self.ada_private)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["project"] == self.ada_private.id
        assert response.data["number"] == 1
        assert response.data["tag"] is None
        assert response.data["creator"] == self.ada.id
        assert response.data["created"] is not None
        assert response.data["completed"] is not None

    def test_create_tag_optional(self):
        response = self.create_snap(self.ada, self.ada_public, "the-tag")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["project"] == self.ada_public.id
        assert response.data["tag"] == "the-tag"

    def test_create_must_be_authenticated(self):
        response = self.create_snap(None, self.ada_public)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_must_have_project_edit_permission(self):
        response = self.create_snap(self.ada, self.bob_private)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_and_retrieve_basic(self):
        """Test a user can list and retrieve the snapshots they create for a project."""
        number = self.create_snap(self.ada, self.ada_public).data["number"]

        response = self.list_snaps(self.ada, self.ada_public)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["number"] == number

        response = self.retrieve_snap(self.ada, self.ada_public, number)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["project"] == self.ada_public.id
        assert response.data["number"] == number
        assert response.data["tag"] is None
        assert response.data["creator"] == self.ada.id
        assert response.data["created"] is not None
        assert response.data["completed"] is not None

    def test_list_and_retrieve_unauthenticated(self):
        """Test unauthenticated user can list and retreive for public but not private projects."""
        # Public
        number = self.create_snap(self.ada, self.ada_public).data["number"]
        response = self.list_snaps(None, self.ada_public)
        assert response.status_code == status.HTTP_200_OK
        response = self.retrieve_snap(None, self.ada_public, number)
        assert response.status_code == status.HTTP_200_OK

        # Private
        number = self.create_snap(self.ada, self.ada_private).data["number"]
        response = self.list_snaps(None, self.ada_private)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = self.retrieve_snap(None, self.ada_private, number)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_not_found(self):
        response = self.retrieve_snap(None, self.ada_public, 2743965137659)
        assert response.status_code == status.HTTP_404_NOT_FOUND
