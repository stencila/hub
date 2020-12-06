from stencila.schema.types import Article, Paragraph

from .serialize import serialize


def test_serialize():
    assert serialize(True) is True
    assert serialize(1) == 1
    assert serialize("foo") == "foo"

    assert serialize([]) == []
    assert serialize([True, 1, "foo", [2, 3]]) == [True, 1, "foo", [2, 3]]

    assert serialize({}) == {}
    assert serialize(dict(a=True, b=1, c="foo", d=dict(e=2))) == dict(
        a=True, b=1, c="foo", d=dict(e=2)
    )

    assert serialize(Article(content=[Paragraph(content=["Hello world!"])])) == dict(
        type="Article", content=[dict(type="Paragraph", content=["Hello world!"])]
    )
