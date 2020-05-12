"""Configuration for pytest."""

from testfixtures import TempDirectory
import pytest


@pytest.fixture()
def tempdir():
    """Add TempDirectory as a pytest fixtire."""
    with TempDirectory() as dir:
        yield dir
