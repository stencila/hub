from scripts.anonymize_test_emails import anonymize_email


def test_anonymize_email():
    """Test that an email address has the @ replaced and domain set to example.com"""
    assert anonymize_email("user@host.com") == "user.host.com@example.com"
