import os
import shutil
import tempfile
from typing import Optional, List
from unittest import mock

from django.http import HttpRequest
from django.utils import timezone
from rest_framework import status

from general.testing import DatabaseTestCase
from projects.models import Project, Snapshot
from lib.converter_facade import (
    ConverterIo,
    ConverterIoType,
    ConverterContext,
)

# Set up
snapshots_dir = tempfile.mkdtemp()
snapshot_1_dir = os.path.join(snapshots_dir, "1")
os.mkdir(snapshot_1_dir)
with open(os.path.join(snapshot_1_dir, "test.txt"), "w") as file:
    file.write("Test content")


class MockSnapshotter:
    """Returns a new snapshot but does not create snapshot dir etc."""

    def __init__(self, storage_root: str) -> None:
        pass

    def snapshot_project(
        self, request: HttpRequest, project: Project, tag: Optional[str] = None
    ) -> Snapshot:
        return Snapshot.objects.create(
            project=project,
            version_number=1,
            tag=tag or None,
            path=snapshot_1_dir,
            creator=request.user,
            created=timezone.now(),
            completed=timezone.now(),
        )


class MockConverter:
    """Just copies the input path to the output path."""

    def __init__(self, converter_binary: List[str]) -> None:
        pass

    def convert(
        self,
        input_data: ConverterIo,
        output_data: ConverterIo,
        context: ConverterContext,
    ) -> None:
        assert input_data.io_type == ConverterIoType.PATH
        assert output_data.io_type == ConverterIoType.PATH
        dir = os.path.dirname(output_data.data)
        if not os.path.exists(dir):
            os.makedirs(dir)
        shutil.copyfile(input_data.data, output_data.data)


class SnapshotAPIViewsTest(DatabaseTestCase):
    """
    Test API views for snapshots.

    Tests for the `ProjectSnapshotter` should be done elsewhere.
    It is mocked in these tests.
    """

    def setUp(self):
        super().setUp()
        self.patch_snapshotter = mock.patch(
            "projects.api.views.snapshots.ProjectSnapshotter", new=MockSnapshotter,
        )
        self.patch_snapshotter.start()

        self.patch_snapshotter = mock.patch(
            "projects.api.views.snapshots.ConverterFacade", new=MockConverter,
        )
        self.patch_snapshotter.start()

    def tearDown(self):
        self.patch_snapshotter.stop()

    # Type specific CRUD methods (no U & D methods though)

    def list_snaps(self, user, project: Project):
        return self.list(user, "snapshots", kwargs={"pk": project.pk})

    def create_snap(self, user, project: Project, tag: Optional[str] = None):
        return self.create(
            user, "snapshots", kwargs={"pk": project.pk}, data={"tag": tag}
        )

    def retrieve_snap(self, user, project: Project, number: int, **kwargs):
        return self.retrieve(
            user, "snapshots", kwargs={"pk": project.pk, "number": number}, **kwargs
        )

    def retrieve_file(self, user, project: Project, number: int, path: str, **kwargs):
        return self.retrieve(
            user,
            "api-snapshots-retrieve-file",
            kwargs={"pk": project.pk, "number": number, "path": path},
            **kwargs,
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

    def test_retrieve_archive(self):
        number = self.create_snap(self.ada, self.ada_public).data["number"]

        response = self.retrieve_snap(
            self.ada, self.ada_public, number, data={"format": "zip"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert os.path.exists(os.path.join(snapshots_dir, "{}.zip".format(number)))

        response = self.retrieve_snap(
            self.ada, self.ada_public, number, data={"format": "tar.xz"}
        )
        assert response.status_code == status.HTTP_200_OK
        assert os.path.exists(os.path.join(snapshots_dir, "{}.tar.xz".format(number)))

        response = self.retrieve_snap(
            self.ada,
            self.ada_public,
            number,
            headers={"HTTP_ACCEPT": "application/x-tar"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert os.path.exists(os.path.join(snapshots_dir, "{}.tar".format(number)))

        response = self.retrieve_snap(
            self.ada,
            self.ada_public,
            number,
            headers={"HTTP_ACCEPT": "application/x-tar+bzip2"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert os.path.exists(os.path.join(snapshots_dir, "{}.tar.bz2".format(number)))

    def test_retrieve_errors(self):
        number = self.create_snap(self.bob, self.bob_private).data["number"]

        response = self.retrieve_snap(
            self.bob, self.bob_private, number, data={"format": "foo"}
        )
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert (
            response.data["message"]
            == "Could not satisfy the requested format 'foo', must be one of ['json', 'tar.bz2', 'tar.gz', 'tar', 'tar.xz', 'zip']"
        )

    def test_retrieve_file_raw(self):
        number = self.create_snap(self.ada, self.ada_public).data["number"]

        response = self.retrieve_file(None, self.ada_public, number, "test.txt")
        assert response.status_code == status.HTTP_200_OK
        assert b"".join(response.streaming_content).decode("ascii") == "Test content"

    def test_retrieve_file_errors(self):
        number = self.create_snap(self.ada, self.ada_private).data["number"]

        response = self.retrieve_file(self.bob, self.ada_private, number, "test.txt")
        assert response.status_code == status.HTTP_403_FORBIDDEN

        response = self.retrieve_file(self.ada, self.ada_private, number, "foo.txt")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = self.retrieve_file(
            self.ada, self.ada_private, number, "test.txt", data={"format": "foo"}
        )
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert (
            response.data["message"]
            == "Could not satisfy the request format parameter or Accept header"
        )

    def test_retrieve_file_converted(self):
        number = self.create_snap(self.ada, self.ada_public).data["number"]
        snapshot_cache = os.path.join(snapshots_dir, "{}.cache".format(number))

        def get(**kwargs):
            response = self.retrieve_file(
                None, self.ada_public, number, "test.txt", **kwargs
            )
            assert response.status_code == status.HTTP_200_OK

        # Using the format query parameter
        get(data={"format": "html"})
        assert os.path.exists(os.path.join(snapshot_cache, "test-txt.html"))

        # Using the accept header
        get(headers={"HTTP_ACCEPT": "application/pdf"})
        assert os.path.exists(os.path.join(snapshot_cache, "test-txt.pdf"))

        # With the account theme set
        self.ada_account.theme = "org-theme"
        self.ada_account.save()
        get(data={"format": "html"})
        assert os.path.exists(os.path.join(snapshot_cache, "test-txt-org-theme.html"))

        # The project theme overrides the account theme
        self.ada_public.theme = "a/local/project/theme"
        self.ada_public.save()
        get(data={"format": "html"})
        assert os.path.exists(
            os.path.join(snapshot_cache, "test-txt-alocalprojecttheme.html")
        )

        # And the theme query parameter trumps them all
        get(data={"format": "html", "theme": "wilmore"})
        assert os.path.exists(os.path.join(snapshot_cache, "test-txt-wilmore.html"))

    def test_retrieve_file_csp(self):
        """Test that headers are set if the account has hosts set."""
        self.bob_account.hosts = "https://*.example.com http://example.com"
        self.bob_account.save()

        number = self.create_snap(self.bob, self.bob_public).data["number"]

        response = self.retrieve_file(None, self.bob_public, number, "test.txt")
        assert (
            response["Content-Security-Policy"]
            == "frame-ancestors https://*.example.com http://example.com;"
        )
        assert response["X-Frame-Options"] == "allow-from https://*.example.com"
