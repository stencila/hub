import pytest

from . import Pull


def test_missing_provider():
    pull = Pull()
    with pytest.raises(AssertionError) as excinfo:
        pull.do({}, "sink")
    assert "Source must have a provider" in str(excinfo.value)


def test_unknown_provider():
    pull = Pull()
    with pytest.raises(ValueError) as excinfo:
        pull.do({"provider": "foo"}, "sink")
    assert "Unknown source provider: foo" in str(excinfo.value)
