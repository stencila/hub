import pytest

from . import Extract


def test_missing_source_type():
    extract = Extract()
    with pytest.raises(AssertionError) as excinfo:
        extract.do({})
    assert "source must have a type" in str(excinfo.value)


def test_unknown_source_type():
    extract = Extract()
    with pytest.raises(ValueError) as excinfo:
        extract.do({"type": "foo"})
    assert "Unknown source type: foo" in str(excinfo.value)


def test_bad_arg_types():
    extract = Extract()

    with pytest.raises(AssertionError) as excinfo:
        extract.do(None)
    assert "source must be a dictionary" in str(excinfo.value)

    with pytest.raises(AssertionError) as excinfo:
        extract.do({"type": "whateva"}, None)
    assert "filters must be a dictionary" in str(excinfo.value)

    with pytest.raises(AssertionError) as excinfo:
        extract.do({"type": "whateva"}, {}, None)
    assert "secrets must be a dictionary" in str(excinfo.value)
