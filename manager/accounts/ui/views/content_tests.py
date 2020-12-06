from accounts.ui.views.content import index_html_links


def test_index_html_links():
    assert index_html_links(b'<a href="#internal">') == b'<a href="#internal">'
    assert (
        index_html_links(b'<a href="external">')
        == b'<a href="external" target="_blank" rel="noreferrer noopener">'
    )
    assert (
        index_html_links(b'<a href="/another/path">')
        == b'<a href="/another/path" target="_blank" rel="noreferrer noopener">'
    )
    assert (
        index_html_links(b'<a href="https://example.org/page#foo">')
        == b'<a href="https://example.org/page#foo" target="_blank" rel="noreferrer noopener">'
    )
    assert (
        index_html_links(b'<a href="://example.org/page.html?foo=bar">')
        == b'<a href="://example.org/page.html?foo=bar" target="_blank" rel="noreferrer noopener">'
    )
