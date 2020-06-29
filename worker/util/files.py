from typing import Dict, Any
import os
import mimetypes

Files = Dict[str, Dict[str, Any]]


def list_files(directory: str) -> Files:
    """
    List, and provide information on, all files in a directory.

    Includes all subdirectories and all files.
    """
    files = {}
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for filename in filenames:
            absolute_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(absolute_path, directory)
            mimetype, encoding = mimetypes.guess_type(relative_path)
            files[relative_path] = {
                "size": os.path.getsize(absolute_path),
                "mimetype": mimetype,
                "encoding": encoding,
                "modified": os.path.getmtime(absolute_path),
            }
    return files
