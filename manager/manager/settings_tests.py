import re

from django.conf import settings


def test_CORS_ALLOWED_ORIGIN_REGEXES():
    """Test that regexes math orgins for Google add-ons. etc"""
    for origin in (
        # These are origin URLS used by our Google Docs add-on
        "https://n-zoqnmwqnnhslxffeq3hh6ne46wicurqczwe4csa-0lu-script.googleusercontent.com",
        "https://n-zoqnmwqnnhslxffeq3hh6ne46wicurqczwe4csa-11u-script.googleusercontent.com",
    ):
        matched = False
        for regex in settings.CORS_ALLOWED_ORIGIN_REGEXES:
            if re.match(regex, origin):
                matched = True
        assert matched, f"Unmached CORS origin {origin}"
