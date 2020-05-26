import os
import typing
from os import DirEntry

PathType = typing.Union[str, bytes]


def to_utf8(s: PathType) -> bytes:
    """If a `str` is passed in, return its utf8 encoding, ff `bytes`, assume it is already utf8 and just return it."""
    return s.encode("utf8") if isinstance(s, str) else s


def utf8_path_join(*args: PathType) -> str:
    """Encode `str` typed args into `bytes` using utf8 then passes all to `os.path.join`."""
    return os.path.join(*list(map(to_utf8, args))).decode("utf8")


def utf8_normpath(path: PathType) -> str:
    return os.path.normpath(to_utf8(path)).decode("utf8")


def utf8_isdir(path: PathType) -> bool:
    return os.path.isdir(to_utf8(path))


def utf8_basename(path: PathType) -> str:
    return os.path.basename(to_utf8(path)).decode("utf8")


def utf8_dirname(path: PathType) -> str:
    return os.path.dirname(to_utf8(path)).decode("utf8")


def utf8_realpath(path: PathType) -> str:
    return os.path.realpath(to_utf8(path)).decode("utf8")


def utf8_path_exists(path: PathType) -> bool:
    return os.path.exists(to_utf8(path))


def utf8_unlink(path: PathType) -> None:
    os.unlink(to_utf8(path))


def utf8_makedirs(path: PathType, *args, **kwargs) -> None:
    os.makedirs(to_utf8(path), *args, **kwargs)


def utf8_rename(src: PathType, dest: PathType):
    os.rename(to_utf8(src), to_utf8(dest))


def utf8_scandir(path: PathType) -> typing.Iterable[DirEntry]:
    yield from os.scandir(to_utf8(path))


def normalise_path(path: str, append_slash: bool = False) -> str:
    if path == "." or path == "":
        return ""

    append_slash = append_slash or path.endswith("/")

    return utf8_normpath(path) + ("/" if append_slash else "")


def path_is_in_directory(
    path: str, directory: str, allow_matching: bool = False
) -> bool:
    path = normalise_path(path)
    directory = normalise_path(directory, True)

    if path.startswith(directory):
        return True

    if not allow_matching:
        return False

    if not path.endswith("/"):
        path += "/"

    return path == directory


def relative_path_join(directory: str, relative_path: str) -> str:
    """
    Join `relative_path` on to `directory`.

    Then ensure that the generated path is inside the `director`y (i.e. relative_path does not contain path traversal
    components).
    """
    full_path = utf8_realpath(utf8_path_join(directory, relative_path))

    if path_is_in_directory(full_path, directory):
        return full_path

    raise ValueError("Path {} is not in directory {}".format(full_path, directory))
