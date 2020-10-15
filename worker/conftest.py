"""Configuration for pytest."""

import pytest
from testfixtures import TempDirectory


@pytest.fixture()
def tempdir():
    """Add TempDirectory as a pytest fixtire."""
    with TempDirectory() as dir:
        yield dir
