import typing
from shutil import copytree

from django.http import HttpRequest
from django.utils import timezone

from lib.resource_allowance import account_resource_limit, QuotaName
from lib.social_auth_token import user_github_token
from projects.project_models import Project, Snapshot
from projects.project_puller import ProjectSourcePuller
from projects.source_models import LinkedSourceAuthentication
from projects.source_operations import generate_snapshot_directory


class SnapshotInProgressError(RuntimeError):
    pass


class ProjectSnapshotter:
    storage_root: str

    def __init__(self, storage_root: str) -> None:
        self.storage_root = storage_root

    def snapshot_project(
        self, request: HttpRequest, project: Project, tag: typing.Optional[str] = None
    ) -> Snapshot:
        if project.snapshot_in_progress:
            raise SnapshotInProgressError(
                "A snapshot is already in progress for Project {}".format(project.pk)
            )

        project.snapshot_in_progress = True
        project.save()

        authentication = LinkedSourceAuthentication(user_github_token(request.user))
        storage_limit = typing.cast(
            int, account_resource_limit(project.account, QuotaName.STORAGE_LIMIT)
        )
        project_puller = ProjectSourcePuller(
            project, self.storage_root, authentication, request, storage_limit
        )
        try:
            previous_version = (
                Snapshot.objects.filter(project=project)
                .order_by("-version_number")
                .values("version_number")
                .first()
            )

            if previous_version:
                new_version = previous_version["version_number"] + 1
            else:
                new_version = 1

            snapshot = Snapshot.objects.create(
                project=project,
                version_number=new_version,
                tag=tag or None,  # default to None instead of empty string
            )

            project_puller.pull()
            snapshot.path = generate_snapshot_directory(self.storage_root, snapshot)
            copytree(project_puller.project_directory, snapshot.path)
            snapshot.snapshot_time = timezone.now()
            snapshot.save()
        finally:
            project.snapshot_in_progress = False
            project.save()

        return snapshot
