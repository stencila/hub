import pytest

from .pin import Pin

# These tests use a `pytest-recording` "casette" to record resposes from
# Docker registry to API requests. That casette has had any sensitive data redacted from it.
# To re-record casettes do
#  ./venv/bin/pytest --record-mode=rewrite jobs/pin_test.py


def test_parse():
    """Test parsing of container image identifiers."""
    job = Pin()

    for image, parts in [
        ("name", (None, "name", None, None)),
        ("org/name", (None, "org/name", None, None)),
        ("registry.io/org/name", ("registry.io", "org/name", None, None)),
        ("registry.io:5432/org/name", ("registry.io:5432", "org/name", None, None)),
        ("123.123.123.123/org/name", ("123.123.123.123", "org/name", None, None)),
        ("123.123.123.123:80/org/name", ("123.123.123.123:80", "org/name", None, None)),
        ("name:20.04", (None, "name", "20.04", None)),
        ("org/name:20201005.1", (None, "org/name", "20201005.1", None)),
        (
            "registry.io/org/name:20201005.1",
            ("registry.io", "org/name", "20201005.1", None),
        ),
        (
            "ubuntu@sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2",
            (
                None,
                "ubuntu",
                None,
                "sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2",
            ),
        ),
        (
            "registry.io/org/name@sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2",
            (
                "registry.io",
                "org/name",
                None,
                "sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2",
            ),
        ),
        (
            "sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2",
            (
                None,
                None,
                None,
                "sha256:45b23dee08af5e43a7fea6c4cf9c25ccf269ee113168c19722f87876677c5cb2",
            ),
        ),
    ]:
        assert job.parse(image) == parts


@pytest.mark.vcr
def test_run():
    job = Pin()

    executa_midi_latest = "docker.io/stencila/executa-midi@sha256:0718ba0aa79b648a9abfa8ac324aa6e7a1d86084587a60ff1ab4ec75173848f3"  # noqa
    assert job.do() == executa_midi_latest
    assert job.do("stencila/executa-midi") == executa_midi_latest

    assert (
        job.do("stencila/executa-midi:20201004.1")
        == "docker.io/stencila/executa-midi@sha256:ba8dfd7bbd91cc704baa9fa1b9e6100d70a4a0b153ea97d37ca0eef0fc5dea57"
    )
