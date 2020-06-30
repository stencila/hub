import pytest

from . import Pull


def test_missing_type():
    pull = Pull()
    with pytest.raises(AssertionError) as excinfo:
        pull.do({}, "path")
    assert "source must have a type" in str(excinfo.value)


def test_unknown_type():
    pull = Pull()
    with pytest.raises(ValueError) as excinfo:
        pull.do({"type": "foo"}, "path")
    assert "Unknown source type: foo" in str(excinfo.value)
