import hashlib
import mimetypes
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

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
        mimetype, encoding = file_mimetype(path)

    return {
        "size": os.path.getsize(path),
        "mimetype": mimetype,
        "encoding": encoding,
        "modified": os.path.getmtime(path),
        "fingerprint": file_fingerprint(path),
    }


def file_ext(path: str) -> Optional[str]:
    """
    Get the extension of a file.
    """
    return Path(path).suffix


def file_mimetype(path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Get the mimetype of a file.
    """
    mimetype, encoding = mimetypes.guess_type(path, strict=False)
    if not mimetype and os.path.exists(path):
        kind = filetype.guess(path)
        if kind:
            mimetype = kind.mime
    return mimetype, encoding


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


def bytes_fingerprint(data: bytes) -> str:
    """
    Generate a SHA256 fingerprint of bytes.

    A alternative to `file_fingerprint` when we already have
    the bytes of the file loaded into memory.
    """
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    for n in data:
        h.update(mv[:n])
    return h.hexdigest()


def is_within(parent, child) -> bool:
    """
    Check that a path is within another.
    """
    return Path(parent).resolve() in Path(child).resolve().parents


def assert_within(parent, child):
    """
    Assert that a path is within another.
    """
    assert is_within(parent, child), f"Path {child} is not within {parent}"


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


def remove_if_dir(path: str) -> None:
    """
    Remove a path if it is a directory.
    """
    if os.path.exists(path) and os.path.isdir(path):
        remove_dir(path)


def move_files(source: str, dest: str = ".", cleanup: bool = True) -> None:
    """
    Move files from `source` to `dest` directories.

    With overwrite of existing files, directory merging and (optional) cleanup
    of the source.
    """
    for path, dirs, files in os.walk(source):
        print(path, dirs, files)
        rel_path = os.path.relpath(path, source)
        dest_dir = os.path.join(dest, rel_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        for file in files:
            source_file = os.path.join(path, file)
            dest_file = os.path.join(dest_dir, file)
            if os.path.isfile(dest_file):
                shutil.copy2(source_file, dest_file)
            else:
                os.rename(source_file, dest_file)

    if cleanup:
        remove_dir(source)
