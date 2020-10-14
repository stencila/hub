import shutil

from util.files import Files, ensure_parent, list_files, move_files, temp_dir

from .helpers import HttpSession


def pull_upload(source: dict, working_dir: str, path: str, **kwargs) -> Files:
    """
    Pull an upload source into a project's working directory.

    An upload source is always a single file, however, if it is
    a file archive e.g. `.zip` it is extracted into the working
    directory.

    In production, `source["url"]` is the URL (usually a storage bucket).
    In development `source["path"]` is the path on the local file system.
    """
    temp = temp_dir()

    # Get the file
    dest_path = ensure_parent(temp, path)
    if "path" in source:
        shutil.copyfile(source["path"], dest_path)
    elif "url" in source:
        HttpSession().pull(source["url"], dest_path)
    else:
        raise ValueError("Upload source must have a `path` or a `url`.")

    # If it is a recognized archive format then unpack in into
    # the temporary directory and then remove it.
    if dest_path.suffix in (".zip", ".tar", ".tar.gz", ".tgz"):
        shutil.unpack_archive(dest_path, temp)
        dest_path.unlink()

    # Enumerate files and move them into the current working directory
    files = list_files(temp)
    move_files(temp)
    return files
