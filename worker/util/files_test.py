from .files import assert_within, is_within


def test_is_within():
    assert is_within(".", "child")
    assert is_within(".", "child/grandchild")
    assert is_within(".", "child/grandchild/..")
    assert is_within("child", "child/grandchild")

    assert not is_within(".", "..")
    assert not is_within(".", "../..")
    assert not is_within(".", "child/../../..")
    assert not is_within("child", "child/../../deep/../..")


def test_assert_within():
    assert_within(".", "child")
