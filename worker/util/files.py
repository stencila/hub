import hashlib
import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

import filetype

FileInfo = Dict[str, Any]
Files = Dict[str, FileInfo]

# Add mapping between mimetypes and extensions
# See https://docs.python.org/3/library/mimetypes.html#mimetypes.add_type
# "When the extension is already known, the new type will replace the old
# one. When the type is already known the extension will be added to the
# list of known extensions."
for mimetype, ext in [
    ("application/vnd.google-apps.document", ".gdoc"),
    ("application/x-ipynb+json", ".ipynb"),
    ("application/ld+json", ".jsonld"),
    ("text/markdown", ".md"),
    ("text/r+markdown", ".rmd"),
    ("text/x-yaml", ".yaml"),
    ("text/x-yaml", ".yml"),
]:
    mimetypes.add_type(mimetype, ext)


def list_files(directory: str = ".") -> Files:
    """
    List, and provide information on, all files in a directory.

    Includes all subdirectories and all files.
    """
    files = {}
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            absolute_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(absolute_path, directory)
            files[relative_path] = file_info(absolute_path)
    return files


def file_info(path: str, mimetype: Optional[str] = None) -> FileInfo:
    """
    Get info on a file.
    """
    if mimetype:
        encoding = None
    else:
        mimetype, encoding = mimetypes.guess_type(path, strict=False)
        if not mimetype:
            kind = filetype.guess(path)
            if kind:
                mimetype = kind.mime

    return {
        "size": os.path.getsize(path),
        "mimetype": mimetype,
        "encoding": encoding,
        "modified": os.path.getmtime(path),
        "fingerprint": file_fingerprint(path),
    }


def file_fingerprint(path: str) -> str:
    """
    Generate a SHA256 fingerprint of the contents of a file.
    """
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(path, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):  # type: ignore
            h.update(mv[:n])
    return h.hexdigest()


def ensure_parent(*args) -> Path:
    """
    Ensure that the parent directory of a file exists.
    """
    path = Path(*args)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def temp_dir():
    """
    Create a temporary directory.
    """
    return tempfile.mkdtemp()


def remove_dir(path: str) -> None:
    """
    Remove a directory.
    """
    shutil.rmtree(path, ignore_errors=True)


def move_files(source: str, dest: str = ".", cleanup: bool = True) -> None:
    """
    Move from `source` to `dest` directories (with overwrite).
    """
    for subpath in os.listdir(source):
        source_path = os.path.join(source, subpath)
        dest_path = os.path.join(dest, subpath)
        if Path(dest_path).exists():
            shutil.rmtree(dest_path, ignore_errors=True)
        shutil.move(source_path, dest_path)

    if cleanup:
        remove_dir(source)
