import logging
import os
import shutil
import tempfile
from typing import Optional

import httpx

from config import get_snapshot_dir
from jobs.base.job import Job
from util.files import Files, ensure_dir, list_files

logger = logging.getLogger(__name__)


class Archive(Job):
    """
    A job that archives files from a project's working directory to a snapshot.

    Previously, we copied all files to the snapshot dir. However, because there were
    performance and reliability issues with that, we now only copy `index.html` and
    related files. This is a temporary measure until we place these in a separate bucket.
    """

    name = "archive"

    def do(self, project: int, snapshot: str, path: str, url: str, **kwargs) -> Files:  # type: ignore
        assert isinstance(project, int)
        assert isinstance(snapshot, str)
        assert isinstance(path, str)
        assert isinstance(url, str)

        files = list_files()

        # This section is temporary, in future index.html will be
        # placed in content storage.
        snapshot_dir = get_snapshot_dir(project, snapshot)
        ensure_dir(snapshot_dir)
        if os.path.exists("index.html"):
            shutil.copy("index.html", snapshot_dir)
        if os.path.exists("index.html.media"):
            shutil.copytree("index.html.media", snapshot_dir)

        temp_zip_base_name = tempfile.NamedTemporaryFile().name
        shutil.make_archive(temp_zip_base_name, "zip", ".")
        temp_zip_file_name = temp_zip_base_name + ".zip"

        if url:
            httpx.post(url, files={path: open(temp_zip_file_name, "rb")})
        else:
            # In development simulate POSTing by copying to the snapshot storage
            logger.warning("No URL was supplied, copying to snapshot dir")
            from config import get_snapshots_root

            shutil.copy(temp_zip_file_name, os.path.join(get_snapshots_root(), path))

        return files
