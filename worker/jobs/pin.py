import os
import re
from typing import cast, List, Optional, Tuple

from dxf import DXF

from jobs.base.job import Job

# Dictionary of credentials for authenticating with registries
CONTAINER_REGISTRY_CREDENTIALS = {
    "registry-1.docker.io": os.environ.get(
        "DOCKER_REGISTRY_CREDENTIALS", "username:password"
    ).split(":")
}

# Regext for pasing a container image identifier
# Based on answers at https://stackoverflow.com/questions/39671641/regex-to-parse-docker-tag
# Playground at https://regex101.com/r/hP8bK1/42
CONTAINER_IMAGE_REGEX = re.compile(
    r"^((?=[^:\/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))+(?::[0-9]{1,5})?/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:/(?![._-])[a-z0-9._-]*(?<![._-]))*)(?:(:(?![.-])[a-zA-Z0-9_.-]{1,128})|(@sha256:[a-f0-9]+))?$"  # noqa
)


class Pin(Job):
    """
    A job that pins the version of the container image to use for a project.

    Usually used when creating a project snapshot. Resolves an unpinned container image
    tag e.g. `@stencila/executa-midi:latest` to a fully qualified image identifier including
    it's registry (e.g. `docker.io`), repository (e.g. `stencila/executa-midi`) and
    digest (e.g. `sha256:a18710...`). The `digest` part is the same as returned by
    `docker inspect <alias> --format='{{.RepoDigests}}'` and the "digest" shown on the Docker Hub.
    """

    name = "pin"

    def do(self, container_image: Optional[str] = None, **kwargs) -> str:  # type: ignore
        [host, repo, alias, digest] = self.parse(container_image)
        if digest:
            return digest

        if host is None:
            host = "registry-1.docker.io"
        if repo is None:
            repo = "stencila/executa-midi"
        if alias is None:
            alias = "latest"

        username, password = CONTAINER_REGISTRY_CREDENTIALS[host]

        dxf = DXF(
            host,
            repo,
            lambda dxf, response: dxf.authenticate(
                username, password, response=response
            ),
        )
        # Get the "Docker-Content-Digest" for the alias. This is the SHA256 hash
        # that can be used with `docker run` and is on the Docker Hub for an image tag,
        # not the one returned by ``.get_digest()`.
        digest = dxf._get_dcd(alias)

        return self.deparse(host, repo, cast(str, digest))

    @staticmethod
    def parse(
        container_image: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        Parse a container image identifier into its component parts: host, repo, and alias or id.
        """
        if container_image is None:
            return (None, None, None, None)

        if container_image.startswith("sha256:"):
            return (None, None, None, container_image)

        match = CONTAINER_IMAGE_REGEX.match(container_image)
        if not match:
            raise ValueError("Unable to parse image identifier: {0}", container_image)

        host, repo, alias, digest = match.groups()
        if host is not None and host.endswith("/"):
            host = host[:-1]
        if alias is not None:
            alias = alias[1:]
        if digest is not None:
            digest = digest[1:]
        return (host, repo, alias, digest)

    @staticmethod
    def deparse(host: str, repo: str, id_: str) -> str:
        """
        Generate a container image identifier from its component parts.
        """
        domain = {"registry-1.docker.io": "docker.io"}.get(host, host)
        return "{domain}/{repo}@{id}".format(domain=domain, repo=repo, id=id_)