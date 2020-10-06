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

    executa_midi_latest = (
        "sha256:055b14cb9563cb25b87973d81adb23a836769a07062425643e790ab8e2dff5fe"
    )
    assert job.do() == executa_midi_latest
    assert job.do("stencila/executa-midi") == executa_midi_latest
    assert job.do(executa_midi_latest) == executa_midi_latest

    assert (
        job.do("stencila/executa-midi:20201004.1")
        == "sha256:aa713b9e09f9f4cd7b573bbecc92019f4cc13a25f347c22f01cd57e2cef1b177"
    )
